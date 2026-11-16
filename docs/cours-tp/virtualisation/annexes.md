---
title: "Parcours virtualisation — annexes : installation de Workstation, dépannage, aide-mémoire, glossaire"
date: 2026-11-16
author: Nicolas BODAINE
tags:
  - virtualisation
  - vmware
  - depannage
  - travaux-pratiques
difficulty: débutant
os: VMware Workstation Pro 26H1, Debian 13
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Annexes : installation, dépannage, aide-mémoire, glossaire

!!! abstract "Résumé"
    Cette page rassemble ce qui sert pendant tout le parcours : l'**installation de VMware Workstation Pro**, les **pannes les plus courantes** et leur solution, les **raccourcis** de Workstation, un **aide-mémoire** des commandes Debian utilisées dans les TP et un **glossaire** du vocabulaire de la virtualisation.

| Propriété | Valeur |
|-----------|--------|
| Usage | À consulter à tout moment du parcours |
| Version décrite | VMware Workstation Pro 26H1, Debian 13.7 |
| Place dans le parcours | Annexes du parcours [Virtualisation](index.md) |
| Dernière mise à jour | 2026-11-16 |

---

## 1. Installation et dépannage

### 1.1 Télécharger et installer VMware Workstation Pro

Depuis le **11 novembre 2024**, Workstation Pro est **gratuit pour tous les usages** (personnel, éducatif et commercial), et depuis la version 26H1 il ne demande plus de clé de licence. Le téléchargement exige en revanche un **compte gratuit** sur le portail de support de **Broadcom**, l'entreprise qui a racheté VMware.

1. 🖥️ Ouvrir le [portail de support Broadcom](https://support.broadcom.com/) et cliquer sur **Register** (*s'inscrire*). Renseigner une adresse e-mail, valider le code reçu par e-mail, puis compléter le profil demandé.
2. Une fois connecté, ouvrir la page des [téléchargements gratuits de Workstation Pro](https://support.broadcom.com/group/ecx/productdownloads?subfamily=VMware%20Workstation%20Pro&freeDownloads=true), choisir la version la plus récente pour **Windows** (26H1 ou une mise à jour comme 26H1u1), accepter les conditions et télécharger le fichier `.exe`.
3. Lancer l'installateur, accepter le contrat de licence et garder les options proposées par défaut. Un redémarrage du PC peut être demandé.
4. Lancer **VMware Workstation Pro** et vérifier la version dans **Help > About VMware Workstation**.

Si le bouton de téléchargement reste inactif, ou si un message parle de vérification du compte, compléter **toutes** les rubriques du profil Broadcom (adresse comprise), puis réessayer.

!!! info "Le portail change souvent d'apparence"
    Broadcom fait évoluer régulièrement son portail : les intitulés peuvent différer légèrement, mais le principe reste le même (compte gratuit, puis rubrique des téléchargements gratuits). En cas de doute, la fiche [KB 368667 de Broadcom](https://knowledge.broadcom.com/external/article/368667/download-and-license-vmware-desktop-hyper.html) décrit la procédure à jour.

### 1.2 « Intel VT-x is disabled » ou impossible de démarrer une VM 64 bits

La virtualisation matérielle est désactivée dans le BIOS/UEFI du PC. Voir la [partie 2, section 4.1](02-hyperviseur-et-machine-virtuelle.md#41-la-virtualisation-materielle-est-elle-activee) : activer **Intel Virtualization Technology** (ou **VT-x**, ou **SVM Mode** sur AMD), enregistrer, puis **éteindre complètement** le PC avant de le rallumer.

### 1.3 Désactiver l'hyperviseur de Windows pour la virtualisation imbriquée

Quand l'hyperviseur de Windows est actif (sécurité basée sur la virtualisation, Hyper-V, WSL 2…), Workstation fonctionne en **mode Host VBS** : les VM sont plus lentes et la **virtualisation imbriquée** (installer un hyperviseur comme Proxmox VE **dans** une VM, au jour 3) est **impossible**. Le message d'erreur est alors du type *« Virtualized Intel VT-x/EPT is not supported on this platform »*.

!!! warning "Une baisse de sécurité à assumer"
    Ces réglages désactivent une **protection** de Windows et empêchent **WSL 2**, **Docker Desktop** et le **Bac à sable** de fonctionner. Ne les modifier que sur un PC **personnel**, ou avec l'accord de l'administrateur du PC, et seulement quand la virtualisation imbriquée est nécessaire (jour 3). **Noter l'état de départ** de chaque réglage pour pouvoir le rétablir.

D'après Broadcom, il faut désactiver **tout ce qui lance l'hyperviseur de Windows** :

1. 🖥️ **Sécurité Windows > Sécurité des appareils > Isolation du noyau** : désactiver **Intégrité de la mémoire**.
2. 🖥️ Ouvrir **Activer ou désactiver des fonctionnalités Windows** (touche ++win+r++, `optionalfeatures`) et décocher, s'ils sont présents : **Hyper-V**, **Plateforme de machine virtuelle**, **Plateforme de l'hyperviseur Windows**, **Bac à sable Windows** (*Windows Sandbox*).
3. 🖥️ Dans une invite de commandes **en tant qu'administrateur**, empêcher le lancement de l'hyperviseur au démarrage :

    ```bat
    bcdedit /set hypervisorlaunchtype off
    ```

4. Redémarrer le PC, puis vérifier dans `msinfo32` que la **Sécurité basée sur la virtualisation** n'est plus « En cours d'exécution ».

!!! tip "Tout remettre après la formation"
    `bcdedit /set hypervisorlaunchtype auto` (invite de commandes en administrateur), recocher les fonctionnalités, réactiver l'**Intégrité de la mémoire**, puis redémarrer.

### 1.4 La souris ou le clavier restent « coincés » dans la VM

Appuyer sur ++ctrl+alt++ : Workstation rend la souris et le clavier à Windows. Pour les redonner à la VM, cliquer dans sa console ou appuyer sur ++ctrl+g++.

### 1.5 Le clavier de la VM est en QWERTY

L'installateur a été lancé avec un autre clavier, ou le choix n'a pas été enregistré. 🐧 Devenir `root`, reconfigurer le clavier, puis l'appliquer à la console :

```bash
su -
dpkg-reconfigure keyboard-configuration
setupcon
```

Garder le modèle de clavier proposé, choisir la disposition **Français**, puis valider les questions suivantes avec les réponses par défaut.

### 1.6 Pas d'Internet dans une VM branchée en NAT (VMnet8)

Vérifier dans l'ordre :

1. 🐧 `ip -4 a` : la carte réseau (souvent nommée `ens33`) a-t-elle une adresse en `192.168.x.128` ou au-dessus ? Si elle n'a **aucune** adresse, le DHCP n'a pas répondu.
2. 🖥️ **VM > Settings > Network Adapter** : les cases **Connected** et **Connect at power on** sont cochées, et le mode est **NAT: Used to share the host's IP address**.
3. 🖥️ Dans les **Services** de Windows (++win+r++, `services.msc`), les services **VMware NAT Service** et **VMware DHCP Service** sont **En cours d'exécution**. Les redémarrer si besoin.
4. 🐧 Redemander une adresse en désactivant puis réactivant la carte (remplacer `ens33` par le nom affiché par `ip a`) :

    ```bash
    su -
    ifdown ens33 && ifup ens33
    ```

5. 🐧 Tester dans l'ordre la passerelle, Internet, puis la résolution de noms : `ping -c 3 192.168.x.2`, `ping -c 3 1.1.1.1`, `ping -c 3 deb.debian.org`.

### 1.7 Toutes les VM se mettent en pause d'un coup

Le disque du PC qui contient les VM est **plein** : les disques dynamiques ne peuvent plus grandir, et Workstation suspend les VM qui veulent écrire en affichant un message qui demande de libérer de la place. Libérer de l'espace (supprimer des fichiers, des instantanés devenus inutiles ou des VM de TP terminées), puis cliquer sur **Retry** (*réessayer*). C'est le **risque de la surallocation du stockage** vu en [partie 4](04-partager-les-ressources.md#41-disque-dynamique-ou-prealloue).

### 1.8 Les VM sont très lentes

- Le PC manque de mémoire : n'allumer que les VM de la partie en cours et fermer les applications inutiles.
- L'hyperviseur de Windows est actif (mode Host VBS) : voir la [section 1.3](#13-desactiver-lhyperviseur-de-windows-pour-la-virtualisation-imbriquee).
- Les VM sont sur un disque dur mécanique, une clé USB ou un dossier synchronisé avec OneDrive : les déplacer sur un SSD local.
- Une VM a de vieux instantanés : les supprimer avec le **Snapshot Manager**, sauf ceux qui servent de base à des clones liés (`02-outils-installes`, `modele-v1`).

### 1.9 Pas d'Internet sur une VM du réseau isolé VMnet2

Les VM `web1`, `stockage` et `web4` n'ont ni DHCP ni accès direct à Internet : tout passe par `routeur`. Tester couche par couche :

1. 🐧 Sur la VM : `ip -br a` (adresse fixe en `10.10.10.x/24`) et `ip route` (ligne `default via 10.10.10.1`).
2. 🐧 Sur la VM : `ping -c 3 10.10.10.1`. Si le routeur ne répond pas : vérifier qu'il est **allumé**, que la carte de la VM est sur **VMnet2** et **Connected**, et que la seconde carte du routeur a bien `10.10.10.1`.
3. 🐧 Sur `routeur` : `cat /proc/sys/net/ipv4/ip_forward` doit afficher `1`, et `sudo nft list ruleset` doit montrer `masquerade` avec le **nom exact** de la carte VMnet8 (comparer avec `ip -br link`).
4. 🐧 Sur la VM : `ping -c 3 1.1.1.1`, puis `ping -c 3 deb.debian.org`. Si seul le second échoue, corriger `/etc/resolv.conf` (`nameserver 192.168.x.2`).

Le [défi du jour 2](08-defi-jour-2.md#2-diagnostic-trois-pannes) détaille ces pannes.

## 2. Raccourcis clavier de Workstation

| Raccourci | Effet |
|---|---|
| ++ctrl+alt++ | Rendre la souris et le clavier à Windows |
| ++ctrl+g++ | Donner la souris et le clavier à la VM |
| ++ctrl+alt+enter++ | Passer la VM en plein écran, ou en sortir |
| ++ctrl+alt+insert++ | Envoyer ++ctrl+alt+del++ à la VM (le vrai ++ctrl+alt+del++ va à Windows) |

## 3. Aide-mémoire des commandes Debian du parcours

| Commande | Ce qu'elle fait |
|---|---|
| `su -` | Devenir administrateur (`root`), avec son mot de passe |
| `sudo <commande>` | Exécuter une seule commande en administrateur, avec son propre mot de passe |
| `sudo apt update` | Mettre à jour la liste des paquets disponibles |
| `sudo apt install -y <paquet>` | Installer un logiciel |
| `sudo apt full-upgrade -y` | Mettre à jour tout le système |
| `ip -4 a` | Afficher les adresses IPv4 des cartes réseau |
| `ping -c 4 <adresse>` | Tester la connexion vers une machine (4 essais) |
| `hostnamectl` | Afficher ou changer le nom de la machine |
| `systemd-detect-virt` | Indiquer si l'on est dans une VM, et sur quel hyperviseur |
| `lscpu` | Décrire le processeur (vu par le système) |
| `nproc` | Afficher le nombre de processeurs disponibles |
| `free -h` | Afficher la mémoire et l'espace d'échange |
| `vmstat 1 20` | Afficher l'activité mémoire et processeur chaque seconde, 20 fois |
| `df -h /` | Afficher la place occupée et libre sur le disque système |
| `lsblk` | Lister les disques et leurs partitions |
| `lspci` | Lister le matériel branché sur le bus PCI (cartes réseau, contrôleurs…) |
| `sudo dmidecode -s system-manufacturer` | Afficher le fabricant de la machine (vu par le BIOS) |
| `stress-ng --cpu 0 -t 20s` | Charger tous les processeurs pendant 20 secondes |
| `stress-ng --vm 1 --vm-bytes 1500M --vm-keep -t 60s` | Occuper 1,5 Go de mémoire pendant 60 secondes |
| `ip route` | Afficher les routes, dont la passerelle par défaut |
| `sudo ifup <carte>` | Activer une carte réseau décrite dans `/etc/network/interfaces` |
| `sudo sysctl --system` | Appliquer les réglages du noyau de `/etc/sysctl.d/` |
| `sudo nft -c -f /etc/nftables.conf` | Vérifier la syntaxe des règles nftables sans les appliquer |
| `sudo nft list ruleset` | Afficher les règles nftables chargées |
| `sudo systemctl enable --now <service>` | Activer un service au démarrage et le démarrer tout de suite |
| `sudo exportfs -ra` puis `sudo exportfs -v` | Recharger puis afficher les partages NFS |
| `findmnt <dossier>` | Afficher ce qui est monté sur un dossier |
| `sudo mount -a` | Monter tout ce qui est décrit dans `/etc/fstab` (pour le tester) |
| `sudo targetcli ls` | Afficher la configuration de la cible iSCSI |
| `sudo iscsiadm -m discovery -t sendtargets -p <IP>` | Découvrir les cibles iSCSI d'un serveur |
| `sudo iscsiadm -m node --login` | Se connecter aux cibles découvertes |
| `wget -qO- http://<adresse>` | Afficher une page web en ligne de commande |
| `sudo poweroff` | Éteindre proprement la machine |
| `sudo reboot` | Redémarrer la machine |

## 4. Glossaire

Ballon (*ballooning*)
:   Technique de récupération de mémoire : un pilote installé dans la VM réclame de la mémoire au système invité, que l'hyperviseur rend à l'hôte ou donne à une autre VM.

Bare metal
:   « Métal nu » : se dit d'un hyperviseur de **type 1**, installé directement sur le matériel, sans système d'exploitation en dessous.

CHAP
:   *Challenge-Handshake Authentication Protocol* : authentification par identifiant et mot de passe, utilisée notamment pour protéger l'accès aux cibles iSCSI.

Cible et initiateur (iSCSI)
:   En iSCSI, la **cible** est le serveur qui partage des disques (LUN) ; l'**initiateur** est le client qui s'y connecte.

Clone complet
:   Copie intégrale et indépendante d'une VM.

Clone lié
:   Copie d'une VM qui partage le disque figé de l'original et n'enregistre que ses différences. Rapide et économe, mais dépendante de l'original.

Commutateur virtuel (*vSwitch*)
:   Switch logiciel de l'hyperviseur sur lequel sont branchées les cartes réseau des VM ; dans Workstation, les réseaux VMnet0 à VMnet19.

Consolidation
:   Regroupement de plusieurs serveurs physiques peu utilisés sous forme de VM sur un nombre réduit d'hôtes.

DAS
:   *Direct Attached Storage* : disques directement attachés à un seul serveur.

Disque différentiel
:   Fichier de disque qui ne contient que les blocs modifiés depuis un instantané ou depuis la création d'un clone lié.

Disque dynamique (*thin*)
:   Disque virtuel qui n'occupe sur l'hôte que la place réellement écrite, et grandit au fil des écritures.

Disque préalloué (*thick*)
:   Disque virtuel qui occupe dès sa création toute sa taille sur l'hôte.

DNAT (redirection de port)
:   Traduction de l'adresse de **destination** : un pare-feu ou un routeur renvoie ce qui arrive sur l'un de ses ports vers une machine interne.

Haute disponibilité (HA)
:   Fonction d'un cluster qui redémarre automatiquement les VM d'un hôte en panne sur les autres hôtes.

Hôte
:   Machine physique qui exécute l'hyperviseur et héberge les VM.

Hyperviseur
:   Logiciel qui crée les machines virtuelles et partage entre elles les ressources de l'hôte. Aussi appelé VMM.

Instantané (*snapshot*)
:   État enregistré d'une VM (disques, paramètres et éventuellement mémoire), auquel on peut revenir. Ce n'est pas une sauvegarde.

Invité
:   Système d'exploitation installé dans une VM.

IQN
:   *iSCSI Qualified Name* : nom unique d'une cible ou d'un initiateur iSCSI, de la forme `iqn.AAAA-MM.domaine-inversé:nom`.

iSCSI
:   Protocole qui transporte des commandes de disque SCSI sur un réseau IP (port TCP 3260) : un client (initiateur) utilise un disque distant (LUN) d'une cible comme un disque local.

LUN
:   *Logical Unit Number* : disque logique présenté par une baie de stockage ou une cible iSCSI.

Machine virtuelle (VM)
:   Ordinateur simulé par un hyperviseur, avec un matériel virtuel, et isolé des autres VM.

Masquerade
:   Forme de NAT source où le routeur remplace l'adresse des machines internes par sa propre adresse de sortie.

Migration à chaud (vMotion)
:   Déplacement d'une VM allumée d'un hôte à un autre, sans coupure perceptible.

Mode Host VBS
:   Mode de fonctionnement de Workstation quand l'hyperviseur de Windows est actif : Workstation passe par lui, les VM sont plus lentes et la virtualisation imbriquée est impossible.

Mode modèle (*Template mode*)
:   Réglage de Workstation qui empêche de supprimer une VM modèle et ses instantanés, sur lesquels reposent des clones liés.

Modèle (*template*)
:   VM « maître », installée et configurée, qui sert à créer rapidement de nouvelles VM identiques.

NAS
:   *Network Attached Storage* : stockage qui partage des **fichiers** sur le réseau (NFS, SMB).

NAT
:   Traduction d'adresses : les VM ont leur propre réseau privé et sortent sur Internet derrière l'adresse de l'hôte.

NFS
:   *Network File System* : protocole de partage de fichiers du monde Unix et Linux (port TCP 2049).

open-vm-tools
:   Version libre des VMware Tools, fournie par les distributions Linux : pilotes et services qui améliorent l'intégration d'une VM Linux dans un hyperviseur VMware.

P2V
:   *Physical to Virtual* : conversion d'un serveur physique en machine virtuelle, sans réinstallation.

Paravirtualisation
:   Technique où le système invité sait qu'il est virtualisé et dialogue directement avec l'hyperviseur, par des pilotes dédiés, au lieu d'utiliser du matériel imité.

Pont (*Bridged*)
:   Mode réseau qui branche la VM directement sur le réseau physique du PC (VMnet0 dans Workstation).

Provisionnement fin (*thin provisioning*)
:   Fait de n'occuper sur le stockage que l'espace réellement écrit, quelle que soit la taille annoncée du disque ou du volume.

Répartition de charge (DRS)
:   Fonction d'un cluster qui déplace automatiquement des VM (par migration à chaud) pour équilibrer la charge entre les hôtes.

Réseau privé hôte (*Host-only*)
:   Mode réseau où les VM ne communiquent qu'avec le PC hôte et entre elles, sans accès à Internet (VMnet1 dans Workstation).

Routage IP (*IP forwarding*)
:   Fonction qui permet à une machine de faire passer des paquets d'une carte réseau à une autre, c'est-à-dire de servir de routeur.

SAN
:   *Storage Area Network* : réseau de stockage qui partage des **blocs** (des disques, les LUN), en Fibre Channel ou en iSCSI.

SMB
:   *Server Message Block* : protocole de partage de fichiers et d'imprimantes de Windows (port TCP 445).

Surallocation (*overcommitment*)
:   Fait d'attribuer aux VM, au total, plus de ressources (mémoire, processeurs, disque) que l'hôte n'en possède réellement.

Tolérance aux pannes (FT)
:   Fonction qui fait tourner une copie miroir d'une VM sur un autre hôte, prête à prendre le relais sans aucune coupure.

vCPU
:   Processeur virtuel attribué à une VM ; pour l'hôte, c'est un fil d'exécution à faire tourner sur un processeur logique.

Virtualisation imbriquée (*nested virtualization*)
:   Faire tourner un hyperviseur à l'intérieur d'une VM.

VMDK
:   Format des fichiers de disques virtuels de VMware.

VMnet
:   Nom des commutateurs virtuels de VMware Workstation (VMnet0 à VMnet19).

VMware Tools
:   Suite de pilotes et de services de VMware à installer dans les VM : pilotes paravirtualisés, synchronisation de l'heure, copier-coller, arrêt propre depuis l'hyperviseur.

VMX
:   Fichier texte de configuration d'une VM VMware (processeurs, mémoire, disques, cartes réseau).

VT-x / AMD-V
:   Extensions de virtualisation des processeurs Intel et AMD, indispensables pour les VM 64 bits sur Workstation. Elles s'activent dans le BIOS/UEFI.

---

## Ressources

- [Documentation de VMware Workstation Pro 26H1](https://techdocs.broadcom.com/us/en/vmware-cis/desktop-hypervisors/workstation-pro/26H1/using-vmware-workstation-pro.html) — le guide officiel (en anglais).
- [Broadcom — Workstation sur un hôte où Hyper-V est actif](https://techdocs.broadcom.com/us/en/vmware-cis/desktop-hypervisors/workstation-pro/26H1/using-vmware-workstation-pro/running-workstation-on-a-hyper-v-enabled-host.html) — le mode Host VBS (en anglais).
- [Broadcom — KB 389469](https://knowledge.broadcom.com/external/article/389469) — désactiver l'hyperviseur de Windows pour retrouver VT-x virtualisé (en anglais).
- [Guide d'installation de Debian 13](https://www.debian.org/releases/trixie/amd64/) — le manuel officiel, en français.
- Retour à l'[accueil du parcours](index.md).

*[VM]: Virtual Machine — machine virtuelle
*[VMM]: Virtual Machine Monitor — moniteur de machines virtuelles
*[NAT]: Network Address Translation — traduction d'adresses
*[DHCP]: Dynamic Host Configuration Protocol — attribution automatique d'adresses IP
*[WSL]: Windows Subsystem for Linux — sous-système Windows pour Linux
*[VBS]: Virtualization-Based Security — sécurité basée sur la virtualisation
*[SSD]: Solid State Drive — disque à mémoire flash
*[BIOS]: Basic Input/Output System — micrologiciel de démarrage
*[UEFI]: Unified Extensible Firmware Interface — successeur du BIOS
*[IP]: Internet Protocol — adresse d'une machine sur le réseau
*[DNS]: Domain Name System — résolution des noms
*[vCPU]: processeur virtuel
*[LUN]: Logical Unit Number — disque logique présenté par une baie
*[NAS]: Network Attached Storage — partage de fichiers
*[SAN]: Storage Area Network — partage de blocs
*[NFS]: Network File System
*[SMB]: Server Message Block
*[iSCSI]: Internet Small Computer System Interface — disques SCSI sur IP
*[SCSI]: Small Computer System Interface
*[TCP]: Transmission Control Protocol
*[HA]: High Availability — haute disponibilité
*[DNAT]: Destination NAT — redirection de port
*[FT]: Fault Tolerance — tolérance aux pannes
*[DRS]: Distributed Resource Scheduler
*[P2V]: Physical to Virtual
*[CHAP]: Challenge-Handshake Authentication Protocol
*[IQN]: iSCSI Qualified Name
*[DAS]: Direct Attached Storage
