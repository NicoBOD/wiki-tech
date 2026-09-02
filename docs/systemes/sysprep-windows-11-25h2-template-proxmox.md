---
title: Sysprep d'une VM Windows 11 25H2 et création d'un template sur Proxmox VE
date: 2026-09-02
author: Nicolas BODAINE
tags:
  - windows-11
  - sysprep
  - proxmox
  - template
  - virtualisation
  - bitlocker
  - appx
difficulty: avancé
os: Windows 11 25H2 / Proxmox VE 8
status: publié
---

# Sysprep d'une VM Windows 11 25H2 et création d'un template sur Proxmox VE

!!! abstract "Résumé"
    Généraliser une VM Windows 11 25H2 avec `sysprep`, puis la convertir en template Proxmox réutilisable. L'article couvre la préparation de l'image, le fichier de réponse `unattend.xml`, les trois pièges spécifiques aux builds 24H2/25H2 (BitLocker, paquets Appx, exécution sous SYSTEM) et la conversion côté hyperviseur.

| Propriété            | Valeur                              |
| --------------------- | ----------------------------------- |
| Difficulté           | Avancé                              |
| OS / Environnement   | Windows 11 25H2 / Proxmox VE 8 (KVM) |
| Dernière mise à jour | 2026-09-02                          |

## Contexte

Déployer plusieurs VM Windows 11 identiques à partir d'un clone brut ne fonctionne pas : chaque installation de Windows possède un **SID machine** unique, un nom d'ordinateur, un identifiant de client Windows Update et un état d'activation qui lui sont propres. Dupliquer ces éléments provoque des conflits en domaine Active Directory, des rapports Windows Update erronés et des comportements imprévisibles côté licence.

`sysprep` (System Preparation Tool) résout ce problème en **généralisant** l'image : il efface l'identité machine, réinitialise le catalogue de pilotes et replace le système en mode OOBE. Le prochain démarrage régénère une identité neuve. C'est l'équivalent Windows de [`virt-sysprep`](virt-sysprep-preparer-image-linux-clonage.md) sous Linux, à une différence près : `virt-sysprep` travaille hors ligne sur le fichier disque depuis l'hôte, alors que `sysprep` s'exécute **à l'intérieur** du système invité.

!!! info "Ce que fait exactement `/generalize`"
    - Réinitialise le **SID machine** (Security Identifier), l'identifiant unique dont dérivent tous les SID de comptes locaux.
    - Supprime le `SusClientId`, identifiant du client auprès de Windows Update / WSUS.
    - Efface le nom d'ordinateur et les journaux d'événements.
    - Réinitialise l'horloge d'activation (opération dite de **réarmement**, limitée à 3 par installation).
    - Purge le catalogue de pilotes détectés, sauf instruction contraire.

Les builds Windows 11 **24H2 et 25H2** ont durci la phase de validation de `sysprep`. Trois écueils nouveaux ou aggravés font échouer la procédure, ou pire, produisent une image qui semble correcte mais est inutilisable. Ils sont détaillés dans la section [Problèmes rencontrés](#problemes-rencontres).

## Prérequis

- Un hôte **Proxmox VE 8** avec une VM Windows 11 configurée selon les bonnes pratiques : machine `q35`, BIOS **OVMF (UEFI)**, disque EFI, **TPM 2.0** (v2.0), contrôleur `VirtIO SCSI single`, carte réseau `VirtIO`.
- L'ISO **virtio-win** monté dans la VM (pilotes paravirtualisés + agent invité).
- La VM **non jointe à un domaine**.
- Une session ouverte avec le **compte Administrateur local intégré** (RID 500), activé au préalable :

    ```powershell
    net user Administrateur /active:yes
    ```

- Un espace de stockage suffisant sur l'hôte pour un snapshot de la VM.

!!! tip "Pourquoi le compte Administrateur intégré ?"
    C'est le compte utilisé par le **mode audit**, l'état de personnalisation officiellement supporté par Microsoft. Il n'est associé à aucun profil OOBE et son profil est détruit par `sysprep`. Personnaliser une image depuis un compte utilisateur classique laisse un profil résiduel, première cause d'échec de validation Appx.

## Procédure

### Étape 1 : finaliser l'image de référence

Appliquer toutes les mises à jour Windows, redémarrer, puis laisser le système se stabiliser (aucune tâche de servicing en cours). Installer ensuite les composants Proxmox depuis l'ISO virtio-win, monté ici en `E:` :

=== "Invité Windows (PowerShell)"

    ```powershell
    # Pilotes paravirtualisés (ballon mémoire, série, vidéo)
    msiexec /i E:\virtio-win-gt-x64.msi /quiet /norestart

    # Agent invité QEMU
    msiexec /i E:\guest-agent\qemu-ga-x86_64.msi /quiet /norestart

    Restart-Computer
    ```

=== "Hôte Proxmox (shell)"

    ```bash
    # Activer l'agent côté hyperviseur
    qm set <vmid> --agent enabled=1,fstrim_cloned_disks=1
    ```

!!! info "VirtIO et agent invité, en deux mots"
    **VirtIO** est une interface de *paravirtualisation* : au lieu d'émuler un vrai contrôleur SCSI ou une vraie carte Intel, l'hyperviseur expose un périphérique virtuel simplifié dont l'invité connaît le protocole. On supprime ainsi la couche d'émulation matérielle, ce qui divise la latence disque et réseau par un facteur important.

    Le **QEMU Guest Agent** est un démon installé dans l'invité qui communique avec l'hôte via un canal `virtio-serial`. Il permet à Proxmox de remonter l'adresse IP de la VM, de déclencher un arrêt propre, et surtout de faire un *freeze/thaw* du système de fichiers avant un snapshot, garantissant sa cohérence.

Supprimer `C:\Windows.old` s'il existe, via le Nettoyage de disque (`cleanmgr`) → « Installations précédentes de Windows ». Depuis 24H2, sa présence bloque la validation.

### Étape 2 : désactiver BitLocker

C'est l'étape la plus souvent oubliée, car **Windows 11 chiffre le disque tout seul**. La fonctionnalité *Device Encryption* s'active automatiquement dès que la machine dispose d'un TPM et que l'utilisateur se connecte avec un compte administrateur — ce qui est exactement le cas d'une VM Proxmox avec TPM 2.0 émulé.

```powershell
Get-BitLockerVolume -MountPoint C: |
  Select-Object VolumeStatus, ProtectionStatus, EncryptionPercentage
```

!!! danger "Ne vous fiez pas à `ProtectionStatus`"
    Un volume peut afficher `ProtectionStatus: Off` tout en étant **chiffré** avec la protection simplement suspendue. `sysprep` refusera quand même de démarrer. Le champ qui compte est **`VolumeStatus`**, qui doit valoir `FullyDecrypted`.

Déchiffrer, puis attendre la fin de l'opération :

```powershell
manage-bde -off C:

while ((Get-BitLockerVolume -MountPoint C:).VolumeStatus -ne 'FullyDecrypted') {
    Get-BitLockerVolume -MountPoint C: |
      Select-Object VolumeStatus, EncryptionPercentage
    Start-Sleep 15
}
```

Empêcher les futurs clones de se rechiffrer seuls au premier démarrage :

```powershell
New-Item 'HKLM:\SYSTEM\CurrentControlSet\Control\BitLocker' -Force | Out-Null
Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\BitLocker' `
  -Name PreventDeviceEncryption -Value 1 -Type DWord
```

!!! warning "TPM cloné"
    Proxmox copie le volume `tpmstate` du template vers chaque clone. Tous les clones démarrent donc avec un **contenu TPM identique**. Laisser BitLocker s'activer automatiquement dessus produirait des clés scellées sur une racine de confiance partagée, ce qui n'a aucun sens en termes de sécurité. Si vous voulez BitLocker sur les VM déployées, activez-le après clonage, VM par VM.

### Étape 3 : exécuter le script de pré-vol

Le script ci-dessous vérifie tous les points bloquants connus et applique les corrections sûres. À lancer d'abord sans paramètre (audit), puis avec `-Fix -Clean`.

??? example "Prepare-Sysprep.ps1 (cliquer pour déplier)"

    ```powershell
    #Requires -RunAsAdministrator
    [CmdletBinding()]
    param([switch]$Fix, [switch]$Clean, [switch]$RemoveMismatched)

    $ErrorActionPreference = 'Continue'
    $script:Blockers = @()
    function Section { param($t) Write-Host "`n=== $t ===" -ForegroundColor Cyan }
    function Ok      { param($t) Write-Host "  [OK]    $t" -ForegroundColor Green }
    function Warn    { param($t) Write-Host "  [WARN]  $t" -ForegroundColor Yellow }
    function Block   { param($t) Write-Host "  [BLOC]  $t" -ForegroundColor Red; $script:Blockers += $t }
    function Act     { param($t) Write-Host "  [FIX]   $t" -ForegroundColor Magenta }

    # --- 0. Contexte d'exécution -------------------------------------------
    Section '0. Contexte'
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    if ($sid -eq 'S-1-5-18') { throw 'Session SYSTEM : sysprep casserait Explorer sur 24H2/25H2.' }
    if ($sid -like '*-500') { Ok 'Compte Administrateur intégré (RID 500).' }
    else { Warn "Compte non-RID500 ($sid)." }
    $cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
    Ok "Windows $($cv.DisplayVersion) - build $($cv.CurrentBuild).$($cv.UBR)"

    # --- 1. Vérifications bloquantes ---------------------------------------
    Section '1. Vérifications bloquantes'
    if ((Get-CimInstance Win32_ComputerSystem).PartOfDomain) {
        Block 'Machine jointe à un domaine.'
    } else { Ok 'Machine en workgroup.' }

    try {
        $vols = Get-BitLockerVolume -ErrorAction Stop | Where-Object { $_.VolumeStatus -ne 'FullyDecrypted' }
        if ($vols) {
            foreach ($v in $vols) {
                Block ("BitLocker : $($v.MountPoint) en état '$($v.VolumeStatus)' " +
                       "($($v.EncryptionPercentage) %). Exécutez : manage-bde -off $($v.MountPoint)")
            }
        } else { Ok 'Tous les volumes sont FullyDecrypted.' }
    } catch { Warn 'Module BitLocker indisponible - vérifiez avec manage-bde -status.' }

    if (Test-Path 'C:\Windows.old') { Block 'C:\Windows.old présent.' } else { Ok 'Pas de Windows.old.' }

    $pendingKeys = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending',
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'
    ) | Where-Object { Test-Path $_ }
    $pfro = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager' `
             -Name PendingFileRenameOperations -ErrorAction SilentlyContinue).PendingFileRenameOperations
    if ($pendingKeys -or $pfro) { Block 'Redémarrage en attente.' } else { Ok 'Aucun redémarrage en attente.' }

    $profiles = Get-CimInstance Win32_UserProfile |
        Where-Object { -not $_.Special -and $_.LocalPath -notmatch '\\Administrator$|\\Administrateur$' }
    if ($profiles) {
        Warn ('Profils supplémentaires : ' + ($profiles.LocalPath -join ', '))
        if ($Fix) { foreach ($p in $profiles) { Act "Suppression $($p.LocalPath)"; $p | Remove-CimInstance } }
    } else { Ok 'Aucun profil parasite.' }

    $rearm = (Get-CimInstance SoftwareLicensingService).RemainingWindowsRearmCount
    if ($rearm -le 1) { Warn "Réarmements restants : $rearm - utilisez <SkipRearm>1</SkipRearm>." }
    else { Ok "Réarmements restants : $rearm" }

    # --- 2. Service AppXSvc -------------------------------------------------
    Section '2. AppXSvc'
    $appxStart = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\AppXSvc').Start
    if ($appxStart -eq 4) {
        Warn 'AppXSvc désactivé (4).'
        if ($Fix) { Act 'AppXSvc -> Manuel (3)'
            Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\AppXSvc' -Name Start -Value 3 }
    } else { Ok "AppXSvc Start = $appxStart." }

    # --- 3. Stratégies à figer ----------------------------------------------
    Section '3. Stratégies'
    if ($Fix) {
        $store = 'HKLM:\SOFTWARE\Policies\Microsoft\WindowsStore'
        New-Item $store -Force | Out-Null
        Set-ItemProperty $store -Name AutoDownload -Value 2 -Type DWord
        Act 'Store : mises à jour automatiques désactivées.'

        $cdm = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\CloudContent'
        New-Item $cdm -Force | Out-Null
        Set-ItemProperty $cdm -Name DisableWindowsConsumerFeatures -Value 1 -Type DWord
        Set-ItemProperty $cdm -Name DisableCloudOptimizedContent   -Value 1 -Type DWord
        Act 'Content Delivery Manager désactivé.'

        $bde = 'HKLM:\SYSTEM\CurrentControlSet\Control\BitLocker'
        New-Item $bde -Force | Out-Null
        Set-ItemProperty $bde -Name PreventDeviceEncryption -Value 1 -Type DWord
        Act 'Chiffrement automatique bloqué sur les futurs clones.'
    } else { Warn 'Mode audit. Relancez avec -Fix.' }
    Warn 'Déconnectez la carte réseau avant de lancer sysprep.exe.'

    # --- 4. Cohérence Appx (analyse non destructive) ------------------------
    Section '4. Cohérence Appx'
    $prov      = Get-AppxProvisionedPackage -Online
    $provNames = $prov.DisplayName
    $provFull  = $prov.PackageName

    $candidates = Get-AppxPackage -AllUsers | Where-Object {
        -not $_.IsFramework -and -not $_.IsResourcePackage -and
        $_.SignatureKind -ne 'System' -and $_.NonRemovable -ne $true
    }
    $notProvisioned = $candidates | Where-Object { $provNames -notcontains $_.Name }
    $versionDrift   = $candidates | Where-Object {
        $provNames -contains $_.Name -and $provFull -notcontains $_.PackageFullName }

    if (-not $notProvisioned -and -not $versionDrift) { Ok 'Aucune incohérence Appx.' }
    else {
        if ($notProvisioned) {
            Warn "$($notProvisioned.Count) paquet(s) non provisionné(s) :"
            $notProvisioned | Select-Object Name, PackageFullName | Format-Table -AutoSize | Out-String | Write-Host
        }
        if ($versionDrift) {
            Warn "$($versionDrift.Count) paquet(s) en dérive de version :"
            $versionDrift | Select-Object Name, PackageFullName | Format-Table -AutoSize | Out-String | Write-Host
        }
        if ($RemoveMismatched) {
            foreach ($p in @($notProvisioned) + @($versionDrift)) {
                Act "Remove-AppxPackage -AllUsers $($p.PackageFullName)"
                Get-AppxPackage -AllUsers -Name $p.Name | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
            }
        } else { Warn 'Aucune suppression. Ajoutez -RemoveMismatched si sysprep échoue en 0x80073CF2.' }
    }

    # --- 5. Nettoyage -------------------------------------------------------
    if ($Clean) {
        Section '5. Nettoyage'
        Act 'Hibernation désactivée';   powercfg.exe /h off | Out-Null
        Act 'Magasin de composants';    Dism.exe /Online /Cleanup-Image /StartComponentCleanup /Quiet | Out-Null
        Act 'Fichiers temporaires'
        Remove-Item "$env:TEMP\*", 'C:\Windows\Temp\*' -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item 'C:\Windows\SoftwareDistribution\Download\*' -Recurse -Force -ErrorAction SilentlyContinue
        Act 'Journaux d''événements';   wevtutil.exe el | ForEach-Object { wevtutil.exe cl "$_" 2>$null }
        Act 'TRIM du volume C:';        Optimize-Volume -DriveLetter C -ReTrim -ErrorAction SilentlyContinue
    }

    # --- 6. Verdict ---------------------------------------------------------
    Section 'Verdict'
    if ($script:Blockers.Count -gt 0) {
        Write-Host '  Sysprep VA ÉCHOUER :' -ForegroundColor Red
        $script:Blockers | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    } else { Write-Host '  Aucun point bloquant détecté.' -ForegroundColor Green }
    Write-Host '  Journaux : C:\Windows\System32\Sysprep\Panther\setuperr.log'
    ```

!!! warning "Le piège du filtre Appx trop large"
    Une première version de ce script comparait les paquets sur leur `PackageFullName`, qui **contient le numéro de version**. Toute application intégrée mise à jour par le Store (Bloc-notes, Terminal, Photos) apparaissait alors comme « non provisionnée » et se faisait supprimer. La comparaison doit porter sur le **nom de famille** du paquet (`Name`), et les frameworks (`IsFramework`) ainsi que les paquets de ressources (`IsResourcePackage`) doivent être exclus : ils ne sont **jamais** provisionnés, c'est normal.

### Étape 4 : préparer le fichier `unattend.xml`

Un **fichier de réponse** est un XML qui pilote automatiquement les écrans d'installation et de configuration de Windows. Il est découpé en *passes* (phases) exécutées à des moments différents du cycle de vie :

| Passe | Moment d'exécution | Usage ici |
| ----- | ------------------ | --------- |
| `generalize` | pendant `sysprep /generalize` | réarmement, conservation des pilotes |
| `specialize` | au premier démarrage du clone, avant OOBE | nom de machine, fuseau, RDP |
| `oobeSystem` | juste avant l'écran de bienvenue | langue, comptes locaux, saut de l'OOBE |

Placer le fichier dans `C:\Windows\System32\Sysprep\unattend.xml`.

??? example "unattend.xml (cliquer pour déplier)"

    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <unattend xmlns="urn:schemas-microsoft-com:unattend">

      <settings pass="generalize">
        <component name="Microsoft-Windows-Security-SPP" processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
                   xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
          <SkipRearm>1</SkipRearm>
        </component>

        <component name="Microsoft-Windows-PnpSysprep" processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
                   xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
          <PersistAllDeviceInstalls>true</PersistAllDeviceInstalls>
          <DoNotCleanUpNonPresentDevices>true</DoNotCleanUpNonPresentDevices>
        </component>
      </settings>

      <settings pass="specialize">
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
                   xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
          <ComputerName>*</ComputerName>
          <TimeZone>Romance Standard Time</TimeZone>
        </component>

        <component name="Microsoft-Windows-Deployment" processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
                   xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
          <RunSynchronous>
            <RunSynchronousCommand wcm:action="add">
              <Order>1</Order>
              <Description>Bypass network requirement</Description>
              <Path>reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE" /v BypassNRO /t REG_DWORD /d 1 /f</Path>
            </RunSynchronousCommand>
            <RunSynchronousCommand wcm:action="add">
              <Order>2</Order>
              <Description>Enable RDP</Description>
              <Path>reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f</Path>
            </RunSynchronousCommand>
            <RunSynchronousCommand wcm:action="add">
              <Order>3</Order>
              <Description>Enable RDP firewall rule</Description>
              <Path>netsh advfirewall firewall set rule group="Remote Desktop" new enable=Yes</Path>
            </RunSynchronousCommand>
          </RunSynchronous>
        </component>
      </settings>

      <settings pass="oobeSystem">
        <component name="Microsoft-Windows-International-Core" processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
                   xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
          <InputLocale>040c:0000040c</InputLocale>
          <SystemLocale>fr-FR</SystemLocale>
          <UILanguage>fr-FR</UILanguage>
          <UserLocale>fr-FR</UserLocale>
        </component>

        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64"
                   publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"
                   xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
          <OOBE>
            <HideEULAPage>true</HideEULAPage>
            <HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>
            <HideOnlineAccountScreens>true</HideOnlineAccountScreens>
            <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
            <HideLocalAccountScreen>true</HideLocalAccountScreen>
            <ProtectYourPC>3</ProtectYourPC>
          </OOBE>

          <UserAccounts>
            <AdministratorPassword>
              <Value>ChangeMe!2026</Value>
              <PlainText>true</PlainText>
            </AdministratorPassword>
            <LocalAccounts>
              <LocalAccount wcm:action="add">
                <Name>opsadmin</Name>
                <DisplayName>opsadmin</DisplayName>
                <Group>Administrators</Group>
                <Password>
                  <Value>ChangeMe!2026</Value>
                  <PlainText>true</PlainText>
                </Password>
              </LocalAccount>
            </LocalAccounts>
          </UserAccounts>

          <FirstLogonCommands>
            <SynchronousCommand wcm:action="add">
              <Order>1</Order>
              <Description>Re-register shell XAML packages</Description>
              <CommandLine>powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Add-AppxPackage -Register -Path 'C:\Windows\SystemApps\MicrosoftWindows.Client.CBS_cw5n1h2txyewy\appxmanifest.xml' -DisableDevelopmentMode -ErrorAction SilentlyContinue; Add-AppxPackage -Register -Path 'C:\Windows\SystemApps\Microsoft.UI.Xaml.CBS_8wekyb3d8bbwe\appxmanifest.xml' -DisableDevelopmentMode -ErrorAction SilentlyContinue"</CommandLine>
              <RequiresUserInput>false</RequiresUserInput>
            </SynchronousCommand>
            <SynchronousCommand wcm:action="add">
              <Order>2</Order>
              <Description>Restore Store auto-update</Description>
              <CommandLine>reg delete "HKLM\SOFTWARE\Policies\Microsoft\WindowsStore" /v AutoDownload /f</CommandLine>
              <RequiresUserInput>false</RequiresUserInput>
            </SynchronousCommand>
          </FirstLogonCommands>
        </component>
      </settings>
    </unattend>
    ```

!!! info "Trois options qui méritent une explication"
    **`SkipRearm`** — chaque `/generalize` consomme un des 3 réarmements de licence disponibles. En itérant sur un master, on épuise vite le compteur. Cette option préserve l'horloge d'activation ; on la retire pour le sysprep final si l'on veut un compteur propre.

    **`PersistAllDeviceInstalls`** — par défaut `sysprep` purge les pilotes détectés pour permettre la redétection sur du matériel différent. Ici, tous les clones tourneront sur exactement le même matériel virtuel Proxmox : conserver les pilotes VirtIO accélère nettement le premier démarrage. À repasser à `false` si les VM déployées peuvent avoir des configurations matérielles différentes.

    **`BypassNRO`** — Windows 11 impose une connexion réseau et un compte Microsoft pendant l'OOBE. La création d'un compte local dans la passe `oobeSystem` suffit généralement à contourner cet écran ; cette clé de registre sert de filet de sécurité selon les builds.

!!! danger "Mots de passe en clair"
    Le fichier de réponse contient des mots de passe lisibles. `sysprep` les masque dans la copie déposée en `C:\Windows\Panther\unattend.xml`, mais l'original reste en clair sur l'image. Changez-les au premier démarrage, ou pilotez-les via **Cloudbase-Init** (l'équivalent Windows de cloud-init).

### Étape 5 : snapshot et coupure réseau

Le snapshot est **indispensable** : le compteur de réarmement est limité, et vous voudrez faire évoluer ce master dans six mois.

=== "Hôte Proxmox (shell)"

    ```bash
    qm snapshot <vmid> pre-sysprep --description "Master avant généralisation"
    ```

Déconnecter ensuite la carte réseau de la VM (Matériel → Périphérique réseau → décocher « Connecter »). Sans cela, le Microsoft Store peut mettre à jour une application en tâche de fond entre la vérification et le lancement de `sysprep`, ce qui invalide l'analyse Appx.

### Étape 6 : lancer sysprep

Depuis la session interactive Administrateur, dans une console élevée :

=== "Invité Windows (PowerShell)"

    ```powershell
    C:\Windows\System32\Sysprep\sysprep.exe `
      /generalize /oobe /shutdown /mode:vm `
      /unattend:C:\Windows\System32\Sysprep\unattend.xml
    ```

| Commutateur | Rôle |
| ----------- | ---- |
| `/generalize` | efface l'identité machine (SID, nom, journaux) |
| `/oobe` | le prochain démarrage lance l'assistant de bienvenue |
| `/shutdown` | éteint la VM à la fin, sans redémarrer |
| `/mode:vm` | saute la redétection des pilotes de démarrage critiques ; valable uniquement si les clones restent sur le même hyperviseur |
| `/unattend:` | applique le fichier de réponse |

!!! danger "Ne rallumez pas la VM source"
    Une fois éteinte, la VM est dans l'état « prête au premier démarrage ». La rallumer déclencherait l'OOBE et consommerait la généralisation. Passez directement à la conversion en template.

### Étape 7 : convertir en template Proxmox

=== "Hôte Proxmox (shell)"

    ```bash
    # Retirer les ISO montés (sinon les clones les hériteront)
    qm set <vmid> --ide0 none --ide2 none

    # Vérifier la configuration finale
    qm set <vmid> --agent enabled=1,fstrim_cloned_disks=1
    qm set <vmid> --scsihw virtio-scsi-single
    qm set <vmid> --boot order=scsi0

    # Conversion
    qm template <vmid>
    ```

Puis pour déployer :

```bash
qm clone <vmid_template> <nouveau_vmid> --name win11-poste01 --full
```

!!! tip "Clone complet ou clone lié ?"
    Un **clone lié** (*linked clone*) ne copie pas le disque : il crée une couche différentielle qui pointe vers celui du template. C'est instantané et économe en espace, mais le template devient indestructible et toute évolution du master est impossible. Un **clone complet** (`--full`) duplique réellement le disque. Pour Windows, préférez systématiquement le clone complet.

    L'option `fstrim_cloned_disks=1` demande à Proxmox de déclencher un **TRIM** après clonage. Le TRIM signale au stockage sous-jacent quels blocs sont libres, ce qui permet au *thin provisioning* de ne consommer que l'espace réellement utilisé.

## Problèmes rencontrés

### Erreur 0x80310039 — BitLocker actif

!!! failure "setuperr.log"
    ```
    Error SYSPRP BitLocker-Sysprep: BitLocker is on for the OS volume.
    Turn BitLocker off to run Sysprep. (0x80310039)
    Error SYSPRP ActionPlatform::LaunchModule: Failure occurred while executing
    'ValidateBitLockerState' from C:\Windows\System32\BdeSysprep.dll
    ```

La boîte de dialogue affiche seulement « Sysprep n'a pas pu valider votre installation de Windows ». La cause exacte n'est visible que dans le journal.

**Solution** : voir [Étape 2](#etape-2-desactiver-bitlocker). Déchiffrer avec `manage-bde -off C:` et attendre `FullyDecrypted`.

!!! info "Pourquoi la validation s'arrête là"
    `sysprep` exécute une chaîne de validateurs décrite dans `C:\Windows\System32\Sysprep\ActionFiles\Generalize.xml`. Elle s'interrompt **au premier échec**. Tant que BitLocker bloque, les validateurs suivants (dont celui des paquets Appx) ne sont jamais exécutés : l'absence d'erreur Appx dans le journal ne signifie donc pas que l'image est saine de ce côté.

### Erreur 0x80073CF2 — paquets Appx incohérents

!!! failure "setuperr.log"
    ```
    Error SYSPRP Package <nom_du_paquet> was installed for a user,
    but not provisioned for all users.
    Error SYSPRP Failed to remove apps for the current user: 0x80073cf2.
    ```

**Concept** : une application **Appx/MSIX** (le format de paquet moderne de Windows) peut exister à deux niveaux. *Installée* pour un utilisateur donné, elle vit dans son profil. *Provisionnée*, elle est enregistrée dans l'image et sera déployée automatiquement pour tout nouvel utilisateur. `sysprep` exige la cohérence entre les deux : un paquet présent chez un utilisateur mais absent du provisionnement ne fonctionnerait pas dans l'image généralisée.

**Solution** :

1. Identifier le paquet exact dans le journal (son nom y figure en clair).
2. Le supprimer pour tous les utilisateurs :

    ```powershell
    Get-AppxPackage -AllUsers <NomDuPaquet> | Remove-AppxPackage -AllUsers
    ```

3. Coupable habituel : `Microsoft.DesktopAppInstaller` (winget), silencieusement mis à jour par le Store.

!!! warning "Paquets système non supprimables"
    Si le journal désigne `Microsoft.SecHealthUI`, `MicrosoftWindows.Client.CBS` ou `Microsoft.UI.Xaml.CBS`, n'essayez pas de les retirer : ce sont des composants système protégés. Réparez plutôt l'image :

    ```powershell
    DISM /Online /Cleanup-Image /RestoreHealth
    sfc /scannow
    ```

### Écran noir au premier démarrage du clone

Symptôme : le clone démarre, l'OOBE se déroule, mais après la connexion l'écran reste noir — `explorer.exe` plante en boucle.

**Cause** : `sysprep.exe` a été exécuté sous le compte **Local System** (via PsExec `-s`, une tâche planifiée, ou un orchestrateur de déploiement). Ce contexte n'est pas supporté : il saute l'enregistrement de certains paquets XAML dont dépendent l'explorateur et l'application Paramètres. Le problème est spécifique à Windows 11 24H2/25H2 et Windows Server 2025, les versions antérieures ne reposant pas sur ces paquets.

**Prévention** : toujours lancer `sysprep` depuis une **session interactive**. Le script de pré-vol refuse de s'exécuter si le SID courant est `S-1-5-18`.

**Contournement** sur un clone déjà cassé — ouvrir un Gestionnaire des tâches (`Ctrl+Maj+Échap`) → Fichier → Exécuter → `powershell` :

```powershell
Add-AppxPackage -Register -DisableDevelopmentMode `
  -Path 'C:\Windows\SystemApps\MicrosoftWindows.Client.CBS_cw5n1h2txyewy\appxmanifest.xml'
Add-AppxPackage -Register -DisableDevelopmentMode `
  -Path 'C:\Windows\SystemApps\Microsoft.UI.Xaml.CBS_8wekyb3d8bbwe\appxmanifest.xml'
Stop-Process -Name explorer -Force
```

Microsoft recommande toutefois de **reconstruire l'image** plutôt que de réparer les clones un par un.

## Aide-mémoire

| Commande / Action | Description |
| ----------------- | ----------- |
| `Get-BitLockerVolume \| Select VolumeStatus` | État réel du chiffrement (`FullyDecrypted` attendu) |
| `manage-bde -off C:` | Lance le déchiffrement du volume système |
| `Get-AppxProvisionedPackage -Online` | Liste les paquets provisionnés dans l'image |
| `Get-AppxPackage -AllUsers` | Liste les paquets installés, tous profils confondus |
| `sysprep /generalize /oobe /shutdown /mode:vm` | Généralise puis éteint la VM |
| `sysprep /audit /reboot` | Redémarre en mode audit pour personnaliser l'image |
| `Get-Content …\Sysprep\Panther\setuperr.log -Tail 40` | Lit la cause réelle d'un échec |
| `qm snapshot <vmid> pre-sysprep` | Snapshot du master avant généralisation |
| `qm template <vmid>` | Convertit la VM éteinte en template |
| `qm clone <src> <dst> --full` | Déploie un clone complet depuis le template |

## Checklist

- [ ] Mises à jour Windows appliquées, aucun redémarrage en attente
- [ ] Pilotes VirtIO et QEMU Guest Agent installés
- [ ] `C:\Windows.old` supprimé
- [ ] Machine hors domaine
- [ ] BitLocker : `VolumeStatus = FullyDecrypted`
- [ ] `PreventDeviceEncryption = 1` positionné
- [ ] Aucun profil utilisateur autre que Administrateur
- [ ] `AppXSvc` en démarrage Manuel ou Automatique
- [ ] Mises à jour du Store gelées
- [ ] Script de pré-vol sans point bloquant
- [ ] Snapshot `pre-sysprep` réalisé
- [ ] Carte réseau déconnectée
- [ ] `unattend.xml` en place et relu
- [ ] `sysprep` lancé depuis une session interactive (jamais SYSTEM)
- [ ] VM source non rallumée après extinction
- [ ] ISO démontés, puis `qm template`

## Glossaire

Sysprep
: *System Preparation Tool*. Utilitaire intégré à Windows qui dépersonnalise une installation pour la rendre clonable.

Généralisation
: Phase de `sysprep` qui efface les identifiants propres à une instance. Sans elle, tous les clones partagent la même identité.

SID machine
: *Security Identifier*. Identifiant unique de l'installation, racine de tous les SID de comptes locaux. Deux machines partageant un SID posent problème en domaine.

OOBE
: *Out-Of-Box Experience*. L'assistant de première configuration affiché au démarrage d'un Windows neuf.

Mode audit
: État de personnalisation dans lequel Windows démarre directement sur le bureau avec le compte Administrateur intégré, sans passer par l'OOBE. On y accède par `Ctrl+Maj+F3` pendant l'OOBE ou via `sysprep /audit /reboot`.

Fichier de réponse (unattend.xml)
: XML qui automatise les choix d'installation et de configuration. Structuré en *passes* exécutées à différentes phases du démarrage.

Appx / MSIX
: Format de paquet applicatif moderne de Windows, successeur de MSI pour les applications du Store et de nombreux composants système.

Provisionnement
: Enregistrement d'un paquet Appx au niveau de l'image, pour qu'il soit déployé automatiquement à chaque nouvel utilisateur, par opposition à une installation dans un seul profil.

Réarmement (rearm)
: Remise à zéro de la période d'activation de Windows. Limitée à 3 occurrences par installation.

VirtIO
: Interface de paravirtualisation. L'invité dialogue avec un périphérique virtuel simplifié plutôt qu'avec du matériel émulé, ce qui réduit fortement la latence disque et réseau.

QEMU Guest Agent
: Démon installé dans l'invité qui permet à l'hyperviseur de remonter l'IP, de déclencher un arrêt propre et de figer les systèmes de fichiers avant snapshot.

OVMF
: *Open Virtual Machine Firmware*. Implémentation libre d'UEFI utilisée par Proxmox, requise pour Windows 11 (Secure Boot, TPM).

TPM 2.0
: *Trusted Platform Module*. Puce cryptographique — émulée sous Proxmox via `swtpm` — qui stocke des clés scellées. Prérequis officiel de Windows 11 et socle de BitLocker.

Device Encryption
: Chiffrement automatique du disque activé sans intervention par Windows 11 dès qu'un TPM est présent. Cause fréquente d'échec de `sysprep`.

Thin provisioning
: Allocation de stockage à la demande : le disque virtuel ne consomme sur l'hôte que l'espace réellement écrit. Le TRIM permet de restituer les blocs libérés.

Cloudbase-Init
: Portage Windows de cloud-init. Injecte au premier démarrage le nom d'hôte, les mots de passe, les clés et les scripts depuis une source de métadonnées.

## Vérification

Après déploiement d'un clone, contrôler que l'identité a bien été régénérée :

=== "Invité Windows (PowerShell)"

    ```powershell
    # SID machine : doit différer de celui du master
    (New-Object System.Security.Principal.NTAccount($env:COMPUTERNAME + '\Administrateur')).
      Translate([System.Security.Principal.SecurityIdentifier]).Value

    # Nom d'ordinateur généré aléatoirement
    $env:COMPUTERNAME

    # État de la généralisation
    Get-ItemProperty 'HKLM:\SYSTEM\Setup\Status\SysprepStatus' | Select-Object GeneralizationState

    # Aucune erreur résiduelle
    Get-Content C:\Windows\Panther\setuperr.log -Tail 20
    ```

=== "Hôte Proxmox (shell)"

    ```bash
    # L'agent invité répond : preuve que le clone a démarré proprement
    qm agent <vmid> ping
    qm guest cmd <vmid> get-host-name
    ```

!!! success "Résultat attendu"
    `GeneralizationState` vaut **7** (généralisation terminée), le nom d'ordinateur diffère du master, le SID machine est unique, et `qm agent ping` répond sans erreur. Le bureau se charge normalement, sans écran noir.

## Ressources

- [Sysprep (System Preparation) Overview](https://learn.microsoft.com/windows-hardware/manufacture/desktop/sysprep-process-overview) — Documentation Microsoft de référence
- [Fix black screen after running Sysprep as system](https://learn.microsoft.com/troubleshoot/windows-client/setup-upgrade-and-drivers/sysprep-as-system-windows-11) — Article officiel sur le problème 24H2/25H2
- [Windows 11 guest best practices](https://pve.proxmox.com/wiki/Windows_11_guest_best_practices) — Wiki Proxmox VE
- [Windows VirtIO Drivers](https://pve.proxmox.com/wiki/Windows_VirtIO_Drivers) — Téléchargement et installation des pilotes
- [Unattended Windows Setup Reference](https://learn.microsoft.com/windows-hardware/customize/desktop/unattend/) — Référence complète des composants `unattend.xml`
- [virt-sysprep — préparer une image Linux au clonage](virt-sysprep-preparer-image-linux-clonage.md) — L'équivalent côté Linux
