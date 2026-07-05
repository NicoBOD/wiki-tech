---
title: Déverrouiller automatiquement LUKS au démarrage avec le TPM2 et Clevis (Ubuntu 24.04)
date: 2026-07-05
author: Nicolas BODAINE
tags:
  - linux
  - securite
  - luks
  - chiffrement
  - tpm2
  - clevis
  - secure-boot
  - initramfs
difficulty: avancé
os: Ubuntu 24.04
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL : entrée ajoutée dans docs/cybersecurite/index.md   -->
<!-- et dans la nav de mkdocs.yml.                                 -->
<!-- ============================================================ -->

# Déverrouiller automatiquement LUKS au démarrage avec le TPM2 et Clevis (Ubuntu 24.04)

!!! abstract "Résumé"
    Sur un portable chiffré avec LUKS2, saisir la phrase de passe à chaque démarrage devient vite pénible. Cette note explique comment déléguer le déverrouillage de la partition racine à la puce **TPM2**, de façon **automatique et sûre**, sur une installation **Ubuntu 24.04 existante** (sans réinstallation). On y explique aussi **pourquoi la méthode `systemd-cryptenroll` seule ne fonctionne pas** sur Ubuntu, et pourquoi **Clevis** est la bonne solution. L'ensemble est conçu pour rester **réversible** et **sans risque de machine non bootable**.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Avancé |
| OS / Environnement | Ubuntu 24.04.4 LTS (UEFI + Secure Boot + TPM 2.0) |
| Matériel de référence | Lenovo ThinkPad T470s |
| Dernière mise à jour | 2026-07-05 |

!!! danger "Opération sensible sur le disque de démarrage"
    On manipule ici l'en-tête LUKS et l'initramfs du disque système. Une erreur peut rendre la machine non bootable. **Suivez l'ordre des étapes**, faites la **sauvegarde de l'en-tête LUKS** (étape 0) et **gardez toujours au moins une méthode de secours** (mot de passe d'origine + recovery key). La méthode décrite retombe automatiquement sur la saisie du mot de passe si le TPM échoue : c'est le filet de sécurité principal.

## Contexte

### Le besoin

Le disque de mon ThinkPad est chiffré avec **LUKS2 + LVM**. À chaque démarrage, je dois saisir manuellement la phrase de passe LUKS. Objectif : **ne plus avoir à taper le mot de passe au boot**, en laissant le **TPM2** libérer la clé automatiquement — tout en conservant des méthodes de secours.

Le lecteur d'empreintes ne peut **pas** déverrouiller LUKS au boot (il n'intervient qu'après le démarrage, au niveau de PAM). La seule vraie solution de déverrouillage du disque au démarrage est donc le **TPM2**.

### L'environnement matériel (référence)

| Élément | Valeur constatée |
|--------|------------------|
| Modèle | Lenovo ThinkPad T470s (`20HGS01P05`) |
| BIOS/UEFI | LENOVO `N1WET76W (1.55)` |
| Démarrage | UEFI (`/sys/firmware/efi` présent) |
| Secure Boot | **Activé** (`mokutil --sb-state` → *SecureBoot enabled*) |
| TPM | **TPM 2.0** présent (`tpm_tis MSFT0101:00`, `/dev/tpm0` + `/dev/tpmrm0`) |
| IOMMU | Actif (`DMAR-IR`, `iommu: Default domain type: Translated`) |
| Chiffrement | LUKS2 + LVM |

Organisation du disque `nvme0n1` :

| Partition | Rôle |
|-----------|------|
| `nvme0n1p1` | `/boot/efi` (EFI) |
| `nvme0n1p2` | `/boot` (non chiffré) |
| `nvme0n1p3` | conteneur `crypto_LUKS` (LUKS2) |
| `dm_crypt-0` | conteneur LUKS ouvert → `LVM2_member` |
| `ubuntu--vg-ubuntu--lv` | `/` (ext4) |

!!! note "UUID LUKS de référence"
    Dans cette note, l'UUID de la partition LUKS est `3e75e9a9-8816-4ae4-a2b8-56cb94555125`. **Remplacez-le partout par le vôtre**, obtenu avec `sudo cryptsetup luksDump /dev/nvme0n1p3`.

## Prérequis

- Ubuntu 24.04 sur **UEFI**, avec **Secure Boot activé** et une **puce TPM 2.0** détectée.
- Une racine chiffrée en **LUKS2** (indispensable : les tokens TPM2 n'existent pas en LUKS1).
- Un accès `sudo`.
- **Connaître sa phrase de passe LUKS** (elle reste le filet de sécurité).
- Une **clé USB** pour stocker la sauvegarde de l'en-tête LUKS hors du disque chiffré.
- Idéalement, une **clé USB Live Ubuntu 24.04** prête en cas de dépannage.

Vérifications matérielles rapides :

```bash
[ -d /sys/firmware/efi ] && echo "UEFI: oui" || echo "UEFI: non"
mokutil --sb-state                       # -> SecureBoot enabled
ls /dev/tpm*                             # -> /dev/tpm0 et /dev/tpmrm0
sudo dmesg | grep -i -e tpm -e iommu     # -> "2.0 TPM", DMAR/iommu
sudo cryptsetup luksDump /dev/nvme0n1p3 | head -5   # -> LUKS Version: 2
```

## Comprendre le piège : pourquoi `systemd-cryptenroll` seul échoue sur Ubuntu

C'est **le point clé** de toute cette procédure, et l'erreur classique.

La documentation générale (et beaucoup de tutoriels orientés Arch/Fedora) recommande :

```bash
# Enrôlement TPM2 "à la systemd" — fonctionne pour l'enrôlement,
# mais NE déverrouille PAS la racine au boot sur Ubuntu 24.04 !
sudo systemd-cryptenroll /dev/nvme0n1p3 --tpm2-device=auto
```

puis d'ajouter dans `/etc/crypttab` :

```text
dm_crypt-0 UUID=... none luks,tpm2-device=auto
```

**Problème :** au `update-initramfs`, Ubuntu affiche :

!!! failure "Avertissement révélateur"
    ```
    cryptsetup: WARNING: dm_crypt-0: ignoring unknown option 'tpm2-device'
    ```

### Cause racine

L'option `tpm2-device=` de `/etc/crypttab` **n'est comprise que par `systemd-cryptsetup`**. Or, sur **Ubuntu 24.04**, l'initramfs par défaut (`initramfs-tools` + `cryptsetup-initramfs`) **n'utilise pas systemd** pour déverrouiller la racine : il utilise le déverrouillage historique en scripts shell (`/scripts/local-top/cryptroot`), qui ne connaît **pas** cette option.

Conséquence : le token `systemd-tpm2` est bien inscrit dans l'en-tête LUKS, mais **rien ne le consulte au boot**. Le keyslot correspondant est donc **mort au démarrage**.

!!! warning "À retenir"
    Sur un Ubuntu 24.04 standard, la chaîne `systemd-cryptenroll --tpm2-device` + `crypttab` + `update-initramfs` **ne peut pas** déverrouiller automatiquement la **racine**. Ce n'est pas une erreur de manipulation, c'est une limite structurelle de l'initramfs Ubuntu.

### Alternatives et pourquoi Clevis

| Solution | Verdict |
|----------|---------|
| **Clevis + TPM2** | ✅ **Recommandée.** Native Ubuntu, s'intègre à `initramfs-tools`, **fallback mot de passe automatique**, réversible. |
| Passer l'initramfs Ubuntu en mode systemd | 🟡 Non supporté proprement par `cryptsetup-initramfs` — fragile, bénéfice nul. |
| Remplacer `initramfs-tools` par `dracut` | 🟠 Fonctionne (tokens systemd-tpm2 gérés) mais **remplace tout le système d'initramfs** : impacts sur Plymouth, hooks Ubuntu, et sur chaque mise à jour noyau. Trop risqué pour ce besoin. |

On retient donc **Clevis**, qui lie un keyslot LUKS au TPM2 et se branche dans l'initramfs Ubuntu via un *hook* dédié, avec repli automatique sur le mot de passe.

## Procédure

!!! tip "Principe directeur"
    On **ajoute** un keyslot dédié au TPM (via Clevis) sans jamais toucher aux keyslots existants (mot de passe + recovery). Chaque étape est vérifiable, et l'ancien mode de déverrouillage reste disponible jusqu'au bout.

### Étape 0 : Filet de sécurité (obligatoire)

Sauvegarde de l'en-tête LUKS (le parachute ultime), puis copie **sur une clé USB externe** :

```bash
sudo cryptsetup luksHeaderBackup /dev/nvme0n1p3 \
  --header-backup-file ~/luks-header-nvme0n1p3-$(date +%F).img
```

!!! danger "Protégez cette sauvegarde"
    L'en-tête contient les keyslots. Stockez-le **hors du disque chiffré** (clé USB), et ne le laissez pas traîner : quiconque possède ce fichier **et** une phrase de passe peut déchiffrer le disque.

Assurez-vous aussi d'avoir noté votre **recovery key** et de connaître votre **mot de passe LUKS**.

### Étape 1 : Vérifier / ajouter les filets logiciels (optionnel mais conseillé)

Une *recovery key* (phrase de passe de secours facile à archiver) :

```bash
sudo systemd-cryptenroll /dev/nvme0n1p3 --recovery-key
```

!!! note
    On peut garder un token `systemd-tpm2` enrôlé au préalable : il est **inoffensif** mais **inutile au boot** (voir plus haut). Il pourra être retiré en fin de procédure (étape 8).

### Étape 2 : Nettoyer `/etc/crypttab`

Retirez toute option `tpm2-device=auto` (ignorée et source de warning). L'objectif est de revenir à une ligne propre — Clevis n'a besoin d'**aucune** option dans `crypttab`, son *hook* détecte le binding automatiquement.

```bash
sudo cp -a /etc/crypttab /etc/crypttab.bak-$(date +%F)
sudo sed -i 's/,tpm2-device=auto//' /etc/crypttab
cat /etc/crypttab
```

Résultat attendu :

```text
dm_crypt-0 UUID=3e75e9a9-8816-4ae4-a2b8-56cb94555125 none luks
```

### Étape 3 : Installer Clevis

```bash
sudo apt update
sudo apt install clevis clevis-luks clevis-initramfs clevis-tpm2 tpm2-tools
```

Vérifier la présence du support TPM2 :

```bash
# Test rapide : le TPM2 chiffre-t-il / déchiffre-t-il ?
echo "test-tpm" | sudo clevis encrypt tpm2 '{"pcr_bank":"sha256","pcr_ids":"7"}' \
  | sudo clevis decrypt && echo "[TPM2 OK]"
```

### Étape 4 : Lier LUKS au TPM2 avec Clevis (le cœur de la procédure)

```bash
sudo clevis luks bind -d /dev/nvme0n1p3 tpm2 '{"pcr_bank":"sha256","pcr_ids":"7"}'
```

- Au prompt `Enter existing LUKS password:`, saisissez votre **mot de passe LUKS** (ou votre **recovery key** — les deux fonctionnent).
- Clevis **ajoute un nouveau keyslot** (par ex. le n°3) et crée un **token `clevis`** qui pointe dessus. Les keyslots existants ne sont pas modifiés.
- Succès = la commande rend la main **sans afficher d'erreur**.

!!! warning "La saisie du mot de passe doit être interactive"
    Cette commande **exige une phrase de passe LUKS existante** : il n'existe aucun contournement, car la clé maîtresse est verrouillée dans le *keyring* du noyau (type `logon`, non relisible — c'est voulu). Lancez donc la commande dans un **vrai terminal** où vous pouvez taper le mot de passe au prompt masqué.

!!! question "Pourquoi PCR 7 ?"
    Un PCR (*Platform Configuration Register*) est un registre du TPM qui mesure un aspect de l'état de démarrage. Le **PCR 7 mesure l'état Secure Boot**. Le lier au TPM protège contre le démarrage d'un OS non signé/modifié qui tenterait l'auto-déverrouillage, **tout en restant stable** lors des mises à jour de noyau (contrairement aux PCR 0/2/4 qui changent au moindre update firmware/bootloader). Alternative plus pratique mais moins sûre : `'{}'` (aucun PCR) — le TPM libère la clé quel que soit l'état de boot.

### Étape 5 : Régénérer l'initramfs

```bash
sudo update-initramfs -u -k all
```

!!! success "Résultat attendu"
    **Aucun** avertissement `ignoring unknown option 'tpm2-device'` (grâce au nettoyage de l'étape 2).

## Vérification

### 1. Le binding Clevis existe

```bash
sudo clevis luks list -d /dev/nvme0n1p3
```

!!! success "Attendu"
    ```
    3: tpm2 '{"hash":"sha256","key":"ecc","pcr_bank":"sha256","pcr_ids":"7"}'
    ```

### 2. Les keyslots et tokens sont cohérents

```bash
sudo cryptsetup luksDump /dev/nvme0n1p3 | grep -E '^[[:space:]]+[0-9]+: (luks2|systemd|clevis|pbkdf2)'
```

On doit retrouver le keyslot mot de passe (slot 0), la recovery (slot 1), éventuellement l'ancien `systemd-tpm2` (slot 2), et le **nouveau keyslot Clevis** (slot 3) associé à un **token `clevis`**.

### 3. Le *hook* Clevis est bien embarqué dans l'initramfs

```bash
sudo lsinitramfs /boot/initrd.img-$(uname -r) | grep -iE 'clevis'
```

!!! success "Attendu (extrait)"
    ```
    scripts/local-top/clevis
    scripts/local-bottom/clevis
    usr/bin/clevis-luks-unlock
    usr/bin/clevis-decrypt-tpm2
    ```

### 4. Test décisif : le TPM libère-t-il réellement la clé ?

On ne peut pas tester en ré-ouvrant `dm_crypt-0` (le disque racine est déjà monté → « périphérique déjà utilisé »). On rejoue donc **exactement l'opération du boot** : demander au TPM de déchiffrer le JWE stocké dans le token Clevis, selon la politique PCR 7.

```bash
# Remplacez --token-id 2 par l'ID du token clevis vu à l'étape "luksDump"
sudo cryptsetup token export --token-id 2 /dev/nvme0n1p3 \
  | python3 -c 'import sys,json; d=json.load(sys.stdin)["jwe"]; sys.stdout.write(".".join([d["protected"],d.get("encrypted_key",""),d["iv"],d["ciphertext"],d["tag"]]))' \
  | sudo clevis decrypt >/dev/null && echo ">>> SUCCÈS : le TPM libère la clé, l'auto-déverrouillage fonctionnera."
```

!!! success "Résultat attendu"
    Le message de succès s'affiche : le TPM a bien libéré la clé sous la politique PCR 7. Le déverrouillage automatique fonctionnera au prochain démarrage.

!!! note "Détails techniques du test"
    Le token Clevis stocke le JWE en forme JSON (champs `protected`, `encrypted_key`, `iv`, `ciphertext`, `tag`). `clevis decrypt` attend la **forme compacte** (segments joints par des points, **sans saut de ligne final** — d'où l'usage de `sys.stdout.write`). L'accès à `/dev/tpmrm0` nécessite **root**, donc le `clevis decrypt` final doit être lancé avec `sudo`.

### 5. Le vrai test : redémarrer

```bash
sudo reboot
```

- **Cas normal** : le disque se déverrouille **tout seul**, sans mot de passe. 🎯
- **Si le TPM refuse** : l'initramfs **redemande la phrase de passe** — aucune casse. C'est le filet de sécurité intégré.

## Précautions prises (récapitulatif)

- [x] **Sauvegarde de l'en-tête LUKS** avant toute modification (étape 0), stockée hors du disque.
- [x] **Sauvegarde de `/etc/crypttab`** avant édition.
- [x] **Keyslots existants intacts** : slot 0 (mot de passe) et slot 1 (recovery) jamais touchés — on n'a fait qu'**ajouter** le keyslot Clevis.
- [x] **Fallback automatique** sur le mot de passe si le TPM échoue (comportement natif de `clevis-initramfs`).
- [x] **Test à froid** du déverrouillage TPM (déchiffrement du JWE) **avant** de dépendre du reboot.
- [x] **Aucune suppression** de keyslot ou token tant que la nouvelle méthode n'est pas validée par un redémarrage réussi.

## Problèmes futurs possibles et comment les surmonter

### Le disque redemande le mot de passe après une mise à jour

C'est le scénario le plus courant et **il est normal**. Le PCR 7 change si l'**état Secure Boot** évolue : mise à jour du firmware/UEFI, mise à jour des clés Secure Boot ou de la `dbx` (souvent via `fwupd`), activation/désactivation de Secure Boot.

**Solution :** déverrouillez au boot avec votre **mot de passe** (ou recovery key), puis **re-liez** le TPM à la nouvelle valeur de PCR 7 :

```bash
# Réenrôle le binding sur l'état de boot courant
sudo clevis luks regen -d /dev/nvme0n1p3 -s <slot_clevis>
sudo update-initramfs -u -k all
```

!!! tip
    `clevis luks regen` régénère le binding existant en conservant le même slot. À défaut, on peut faire `clevis luks unbind` puis un nouveau `clevis luks bind` (voir plus bas).

### Après une mise à jour de noyau

Rien de spécial : `update-initramfs` est relancé automatiquement par le paquet noyau, et le *hook* Clevis est ré-embarqué. Comme on est lié au **PCR 7** (et pas aux PCR liés au noyau/bootloader), le déverrouillage reste valide.

### Je veux revenir en arrière (désactiver l'auto-déverrouillage)

Totalement réversible, sans impact sur le mot de passe :

```bash
# Lister pour retrouver le slot Clevis
sudo clevis luks list -d /dev/nvme0n1p3
# Retirer le binding (remplacez 3 par le bon slot)
sudo clevis luks unbind -d /dev/nvme0n1p3 -s 3
sudo update-initramfs -u -k all
```

### Le TPM a été réinitialisé / la carte mère a changé

Les secrets scellés dans le TPM sont **liés à cette puce**. Un *TPM clear* (dans l'UEFI) ou un changement de carte mère invalide le binding. Le disque redemandera alors le mot de passe : déverrouillez avec la phrase de passe, puis refaites un `clevis luks bind`.

## Plan de secours si le boot échoue

!!! danger "Ordre des recours, du plus simple au plus lourd"

1. **Au prompt de mot de passe** (TPM en échec) → tapez votre **mot de passe LUKS** ou votre **recovery key**. Vous bootez normalement, puis vous re-liez le TPM.

2. **Initramfs cassé / boucle** → démarrez sur la **clé USB Live Ubuntu**, puis *chroot* :

    ```bash
    sudo cryptsetup open /dev/nvme0n1p3 dm_crypt-0        # mot de passe LUKS
    sudo vgchange -ay
    sudo mount /dev/mapper/ubuntu--vg-ubuntu--lv /mnt
    sudo mount /dev/nvme0n1p2 /mnt/boot
    sudo mount /dev/nvme0n1p1 /mnt/boot/efi
    for d in dev proc sys run; do sudo mount --bind /$d /mnt/$d; done
    sudo chroot /mnt
    # --- dans le chroot : revenir à l'état d'avant ---
    sed -i 's/,tpm2-device=auto//' /etc/crypttab
    clevis luks unbind -d /dev/nvme0n1p3 -s 3   # slot Clevis
    update-initramfs -u -k all
    exit
    ```

    Puis `reboot` : vous retrouvez le déverrouillage classique par mot de passe.

3. **En-tête LUKS corrompu (catastrophe)** → restaurez la sauvegarde de l'étape 0 :

    ```bash
    sudo cryptsetup luksHeaderRestore /dev/nvme0n1p3 \
      --header-backup-file /chemin/vers/luks-header-....img
    ```

## Étape 8 (optionnelle) : nettoyage après validation

**Uniquement après au moins un redémarrage réussi avec Clevis**, on peut retirer le token `systemd-tpm2` redondant (inutilisé sur Ubuntu). On **conserve** évidemment le mot de passe (slot 0) et la recovery (slot 1).

```bash
# Vérifier d'abord de quel slot/token il s'agit
sudo cryptsetup luksDump /dev/nvme0n1p3
# Retirer le token + keyslot systemd-tpm2
sudo systemd-cryptenroll /dev/nvme0n1p3 --wipe-slot=tpm2
```

!!! danger "Ne jamais supprimer le keyslot du mot de passe"
    Le keyslot 0 (mot de passe d'origine) est le parachute maître : **il ne doit jamais être supprimé**.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `cryptsetup luksHeaderBackup <dev> --header-backup-file <f>` | Sauvegarder l'en-tête LUKS (parachute) |
| `cryptsetup luksHeaderRestore <dev> --header-backup-file <f>` | Restaurer l'en-tête LUKS |
| `cryptsetup luksDump <dev>` | Afficher keyslots et tokens |
| `clevis luks bind -d <dev> tpm2 '{"pcr_bank":"sha256","pcr_ids":"7"}'` | Lier un keyslot au TPM2 (PCR 7) |
| `clevis luks list -d <dev>` | Lister les bindings Clevis |
| `clevis luks unbind -d <dev> -s <slot>` | Retirer un binding Clevis |
| `clevis luks regen -d <dev> -s <slot>` | Régénérer un binding (après changement de PCR) |
| `update-initramfs -u -k all` | Régénérer l'initramfs (embarque le hook Clevis) |
| `lsinitramfs /boot/initrd.img-$(uname -r) \| grep clevis` | Vérifier la présence du hook dans l'initramfs |
| `systemd-cryptenroll <dev> --wipe-slot=tpm2` | Retirer l'enrôlement systemd-tpm2 (nettoyage) |

## Glossaire

LUKS2
:   *Linux Unified Key Setup*, format standard de chiffrement de disque sous Linux (au-dessus de *dm-crypt*). La version 2 introduit les *tokens*, métadonnées qui associent un mécanisme de déverrouillage à un keyslot.

TPM2
:   *Trusted Platform Module* 2.0 : puce sécurisée qui peut **sceller** un secret et ne le **libérer** que si l'état de démarrage (mesuré dans les PCR) correspond à celui enregistré.

PCR
:   *Platform Configuration Register* : registre du TPM mesurant un aspect du démarrage. Le **PCR 7** mesure l'état Secure Boot.

Clevis
:   Cadre de déverrouillage automatique qui « lie » (*bind*) un keyslot LUKS à une politique (ici le TPM2). Sur Ubuntu, `clevis-initramfs` ajoute un *hook* qui tente le déverrouillage au boot, avec repli sur le mot de passe.

initramfs
:   Système de fichiers minimal chargé avant la racine, chargé de déverrouiller et monter `/`. Sur Ubuntu, il repose sur `initramfs-tools` (scripts shell), **pas** sur systemd — d'où l'incompatibilité avec l'option `tpm2-device` de `crypttab`.

JWE
:   *JSON Web Encryption* : format dans lequel Clevis stocke le secret scellé au TPM, à l'intérieur du token LUKS.

## Ressources

- [Clevis — dépôt officiel](https://github.com/latchset/clevis) — *bind* LUKS, pins tpm2/tang/sss.
- [Manuel cryptsetup / LUKS2](https://gitlab.com/cryptsetup/cryptsetup/-/wikis/home) — référence des commandes et des tokens.
- [systemd-cryptenroll — documentation](https://www.freedesktop.org/software/systemd/man/systemd-cryptenroll.html) — pour comprendre les tokens TPM2 (et leurs limites hors initramfs systemd).
- [Recommandations ANSSI sur le chiffrement](https://cyber.gouv.fr/) — bonnes pratiques de cryptographie.
- Article connexe du wiki : [Sécuriser un volume de données avec le chiffrement LUKS sous Linux](securiser-volume-donnees-chiffrement-luks-linux.md)
