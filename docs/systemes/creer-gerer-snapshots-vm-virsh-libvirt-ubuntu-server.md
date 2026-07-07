---
title: Créer et gérer des snapshots de VM avec virsh (libvirt) sur Ubuntu Server
date: 2026-07-05
author: Nicolas BODAINE
tags:
  - virsh
  - libvirt
  - kvm
  - virtualisation
  - snapshot
  - linux
  - ubuntu
difficulty: intermédiaire
os: Ubuntu Server 24.04
status: publié
---

# Créer et gérer des snapshots de VM avec virsh (libvirt) sur Ubuntu Server

!!! abstract "Résumé"
    Un *snapshot* (instantané) de machine virtuelle capture l'état du disque, de la mémoire et des périphériques à un instant T. C'est l'équivalent d'un « point de sauvegarde » : on peut altérer la VM — installer un paquet risqué, modifier la configuration réseau, tester une mise à jour — puis **revenir en arrière** en une commande si le résultat ne convient pas. Ce tutoriel montre comment créer, lister, restaurer et supprimer des snapshots avec `virsh` sur un hyperviseur **libvirt/KVM** Ubuntu Server.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu Server 24.04 (libvirt/KVM) |
| Dernière mise à jour | 2026-07-05 |

## Contexte

En lab ou en production, on manipule souvent des VM comme du matériel jetable : on teste une mise à jour de noyau, une nouvelle configuration réseau, l'installation d'un service. Ces opérations peuvent casser la VM. Le snapshot permet de :

- **geler** l'état courant avant une opération risquée ;
- **revenir** instantanément à cet état si l'opération échoue ;
- **garder** plusieurs points de restauration successifs pour comparer des scénarios.

`libvirt` est la couche d'abstraction de référence pour gérer des hyperviseurs sous Linux. Elle expose le CLI `virsh`, omniprésent sur Ubuntu Server, RHEL, Rocky et Debian. Les snapshots gérés par `virsh` sont des snapshots **internes** au format qcow2 ou **externes** (basés sur un *backing file*), mais pour ce tutoriel nous utiliserons les snapshots internes, les plus simples à mettre en œuvre en lab.

!!! info "Snapshots internes vs externes"
    - **Interne** : tout est stocké dans le même fichier `.qcow2`. Simple, idéal pour les labs, mais moins performant sur disques très actifs.
    - **Externe** : libvirt crée un nouveau fichier `.qcow2` qui pointe vers l'ancien comme *backing file*. Recommandé en production, mais hors du périmètre de ce tutoriel.

## Prérequis

- Un hôte **Ubuntu Server 24.04** avec les droits `sudo`.
- Le paquet **`libvirt-daemon-system`** installé et le service `libvirtd` actif.
- Une VM KVM existante, avec un disque au format **qcow2** (les snapshots internes ne fonctionnent pas avec `raw`).
- Votre utilisateur dans le groupe `libvirt` (ou exécution via `sudo`).

!!! tip "Lab reproductible"
    Toutes les commandes ci-dessous sont exécutables sur un hyperviseur libvirt KVM standard. Si vous n'avez pas encore de VM, la préparation d'une est décrite à l'étape 1.

## Procédure

### Étape 1 : Vérifier l'installation de libvirt et lister les VM

Vérifiez que le service libvirt tourne et que vous voyez vos VM :

```bash
sudo systemctl is-active libvirtd
virsh list --all
```

**Exemple de sortie :**

```
 Id   Name         State
----------------------------
 -    lab-ubuntu    shut off
 -    srv-test      shut off
```

!!! warning "Format de disque obligatoire"
    Les snapshots internes nécessitent un disque **qcow2**. Vérifiez avec :
    ```bash
    virsh domblklist lab-ubuntu --details
    ```
    La colonne *Type* doit afficher `file` et le *Format* doit être `qcow2`. Un disque `raw` ne supportera pas les snapshots internes.

### Étape 2 : Comprendre les deux familles de commandes

`virsh` propose deux groupes de commandes pour les snapshots :

| Famille | Commande | Usage |
|---------|----------|-------|
| Disque seul | `virsh snapshot-create-as` avec `--disk-only` | Capture uniquement l'état du disque. La VM continue de tourner (snapshot à chaud). |
| Disque + mémoire + état | `virsh snapshot-create` (par défaut) | Capture aussi la RAM et l'état du CPU. La VM doit être éteinte (ou `--live` pour un instantané à chaud). |

Pour ce tutoriel, nous traitons le cas le plus courant en lab : **VM éteinte, snapshot disque + mémoire**.

### Étape 3 : Créer un premier snapshot

Éteignez proprement la VM, puis créez le snapshot :

```bash
virsh shutdown lab-ubuntu
# attendez l'arrêt complet
virsh domstate lab-ubuntu   # doit renvoyer : shut off

virsh snapshot-create-as lab-ubuntu \
  --name avant-maj \
  --description "État propre avant mise à jour noyau"
```

**Exemple de sortie :**

```
Domain snapshot avant-maj created
```

!!! note "Nom du snapshot"
    Le `--name` doit être court, sans espaces (utilisez `-` ou `_`). Il sert d'identifiant pour toutes les opérations ultérieures.

### Étape 4 : Lister et inspecter les snapshots

Listez tous les snapshots associés à la VM :

```bash
virsh snapshot-list lab-ubuntu
```

**Exemple de sortie :**

```
 Name          Creation Time               State
----------------------------------------------------
 avant-maj     2026-07-05 18:42:11 +0200   shutoff
```

Pour obtenir des détails (description, hiérarchie) :

```bash
virsh snapshot-info lab-ubuntu avant-maj
```

**Exemple de sortie :**

```
Name:           avant-maj
Domain:         lab-ubuntu
Current:        yes
State:          shutoff
Parent:         -
Children:       0
Descendants:    0
Metadata:       yes
```

### Étape 5 : Effectuer l'opération risquée

Démarrez la VM et appliquez votre changement — ici, une mise à jour du noyau :

```bash
virsh start lab-ubuntu
virsh console lab-ubuntu   # ou connexion SSH
```

Une fois connecté dans la VM :

```bash
sudo apt update && sudo apt -y upgrade
sudo reboot
```

Si la VM ne redémarre pas correctement (kernel cassé, grub cassé) — c'est exactement le scénario que le snapshot doit couvrir.

### Étape 6 : Restaurer la VM depuis le snapshot

Sur l'hôte libvirt, éteignez la VM si elle tourne encore, puis restaurez :

```bash
virsh destroy lab-ubuntu      # arrêt forcé car la VM peut être plantée
virsh snapshot-revert lab-ubuntu avant-maj
```

La VM revient à l'état exact du snapshot (`shutoff`, disque et mémoire restaurés). Démarrez-la :

```bash
virsh start lab-ubuntu
```

!!! success "Résultat attendu"
    La VM démarre comme si la mise à jour n'avait jamais eu lieu : même noyau, même uptime à zéro, même contenu de disque.

### Étape 7 : Créer un snapshot à chaud (disque seul)

Si la VM doit rester allumée pendant l'opération, utilisez un snapshot **disque seul** :

```bash
virsh snapshot-create-as lab-ubuntu \
  --name patch-securite \
  --description "Avant application correctif" \
  --disk-only
```

La VM continue de tourner. Pour revenir en arrière :

```bash
virsh snapshot-revert lab-ubuntu patch-securite
```

!!! warning "Restauration d'un snapshot disque seul"
    Un snapshot `--disk-only` ne restaure **pas** la RAM. Si la VM tourne encore au moment du revert, libvirt l'éteint brutalement avant de restaurer le disque. Utilisez-le pour des opérations sur fichiers (config, paquets), pas sur des bases de données en mémoire.

### Étape 8 : Supprimer un snapshot

Une fois l'opération terminée et validée, nettoyez :

```bash
virsh snapshot-delete lab-ubuntu avant-maj
virsh snapshot-delete lab-ubuntu patch-securite
```

**Exemple de sortie :**

```
Domain snapshot avant-maj deleted
```

!!! tip "Bonnes pratiques de nettoyage"
    - Gardez au maximum 2 à 3 snapshots simultanés sur une VM de lab : les chaînes longues ralentissent les I/O.
    - Supprimez les snapshots **dès que l'opération est validée**, pas après.
    - Un snapshot supprimé ne peut pas être récupéré : confirmez la stabilité de la VM avant.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `virsh list --all` | Liste toutes les VM (allumées et éteintes). |
| `virsh domblklist <vm> --details` | Affiche le type et le format des disques d'une VM. |
| `virsh snapshot-create-as <vm> --name <n> --description "…"` | Crée un snapshot (disque + mémoire) sur une VM éteinte. |
| `virsh snapshot-create-as <vm> --name <n> --disk-only` | Crée un snapshot disque seul, VM à chaud. |
| `virsh snapshot-list <vm>` | Liste les snapshots d'une VM. |
| `virsh snapshot-info <vm> <nom>` | Affiche les détails d'un snapshot. |
| `virsh snapshot-revert <vm> <nom>` | Restaure la VM à l'état du snapshot. |
| `virsh snapshot-delete <vm> <nom>` | Supprime un snapshot. |
| `virsh snapshot-current <vm>` | Affiche le snapshot courant (le plus récent revert). |

## Glossaire

Snapshot
:   Instantané de l'état d'une VM (disque, et optionnellement RAM/CPU) permettant un retour en arrière.

qcow2
:   Format d'image disque de QEMU supportant nativement les snapshots internes, le *thin provisioning* et le *backing file*. Contraction de *QEMU Copy-On-Write version 2*.

Backing file
:   Image disque de référence sur laquelle s'appuie une image qcow2 « fille ». Mécanisme utilisé par les snapshots externes.

libvirt
:   API et daemon de gestion d'hyperviseurs (KVM, QEMU, Xen, LXC) sous Linux. Fournit le CLI `virsh`.

## Vérification

Pour confirmer qu'un snapshot est bien enregistré et restaurable :

```bash
virsh snapshot-list lab-ubuntu
virsh snapshot-info lab-ubuntu avant-maj
```

Puis appliquez le cycle complet : créer → endommager (par exemple `sudo rm -rf /etc` dans la VM) → `snapshot-revert` → vérifier que `/etc` est de nouveau présent.

```bash
virsh snapshot-revert lab-ubuntu avant-maj
virsh start lab-ubuntu
virsh console lab-ubuntu
ls /etc   # doit afficher tous les fichiers comme avant la suppression
```

!!! success "Résultat attendu"
    Le répertoire `/etc` contient à nouveau tous ses fichiers : la restauration s'est bien déroulée.

## Ressources

- [Documentation officielle libvirt — format XML des snapshots](https://libvirt.org/formatsnapshot.html) — Référence des éléments XML utilisés par les snapshots.
- [Documentation Red Hat — Managing virtual machine snapshots with virsh](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/html/configuring_and_managing_virtualization/managing-virtual-machine-snapshots-with-virsh) — Guide de référence complet, applicable à Ubuntu avec libvirt.
- [Documentation Ubuntu Server — KVM/libvirt virtualisation](https://ubuntu.com/server/docs/how-to/virtualisation/) — Installation et gestion de libvirt sous Ubuntu.
- [Documentation officielle QEMU — qcow2 et snapshots](https://www.qemu.org/docs/master/system/images.html#vm-snapshots) — Format d'image et gestion des snapshots matériels.
