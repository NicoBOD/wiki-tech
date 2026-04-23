---
title: virt-sysprep — préparer une image Linux au clonage
date: 2026-04-23
author: Nicolas BODAINE
tags:
  - virt-sysprep
  - libguestfs
  - virtualisation
  - linux
  - template
difficulty: intermédiaire
os: Linux / libguestfs / KVM
status: publié
---

# virt-sysprep — préparer une image Linux au clonage

!!! abstract "Résumé"
    `virt-sysprep` prépare une image de machine virtuelle Linux pour le clonage en supprimant les éléments propres à une instance : clés SSH, `machine-id`, caches, journaux, fichiers temporaires et autres traces locales.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux / libguestfs / KVM |
| Dernière mise à jour | 2026-04-23 |

## Contexte

Copier directement une image disque Linux (par exemple un fichier `.qcow2`) est risqué : le clone récupère exactement la même identité que la machine d'origine.

Cela peut provoquer :

- des conflits réseau ;
- des avertissements SSH ;
- des identifiants système dupliqués ;
- la fuite d'historiques de commandes ou de données temporaires.

**`virt-sysprep`** sert précisément à éviter cela. L'outil nettoie une VM existante pour la transformer en modèle prêt à être cloné.

L'intérêt majeur est qu'il fait partie de **`libguestfs`** : l'image disque est modifiée directement depuis l'hôte, sans démarrer la machine virtuelle.

## Prérequis

- Le paquet **`virt-sysprep`** (suite `libguestfs`) est installé sur l'hôte.
- La VM à préparer est **complètement arrêtée**.
- Un snapshot ou une sauvegarde de l'image existe avant intervention.
- Vous connaissez soit le nom de la VM dans libvirt, soit le chemin exact de l'image disque.

!!! danger "Règle d'or"
    N'exécutez jamais `virt-sysprep` sur une image disque attachée à une VM en cours d'exécution.
    Le système de fichiers invité pourrait être corrompu de manière irréversible.

## Procédure

### Étape 1 : arrêter la machine modèle

Avant toute opération, vérifier que la VM cible est bien hors tension.

```bash
virsh shutdown nom_de_ta_vm_modele
virsh domstate nom_de_ta_vm_modele
```

Le statut attendu doit être `shut off`.

### Étape 2 : lancer `virt-sysprep`

Deux approches courantes existent :

#### Cibler une VM connue de libvirt

```bash
virt-sysprep -d nom_de_ta_vm_modele
```

#### Cibler directement une image disque

```bash
virt-sysprep -a /chemin/vers/image.qcow2
```

Une fois la commande terminée, l'image est "scellée" et prête à être clonée.

### Étape 3 : comprendre ce qui est nettoyé

Par défaut, `virt-sysprep` exécute plusieurs opérations de nettoyage sur le système invité.

Les plus importantes sont :

- suppression des **clés hôtes SSH** dans `/etc/ssh/ssh_host_*` ;
- nettoyage des **baux DHCP persistants** et des références réseau spécifiques à l'instance ;
- réinitialisation du **`machine-id`** ;
- vidage des **journaux** dans `/var/log/` ;
- suppression des **historiques utilisateur** comme `.bash_history` ;
- nettoyage des **caches de gestionnaires de paquets** ;
- suppression des fichiers temporaires dans `/tmp/` et `/var/tmp/` ;
- suppression de l'ancienne **graine aléatoire**.

Le prochain démarrage du clone régénère alors ses propres éléments d'identité.

### Étape 4 : cloner l'image préparée

Le cycle d'usage typique est le suivant :

1. Créer une VM modèle avec les paquets de base.
2. Éteindre la VM.
3. Exécuter `virt-sysprep`.
4. Cloner l'image disque autant de fois que nécessaire.
5. Démarrer chaque clone comme une machine fraîche et unique.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `virt-sysprep -d nom_vm` | Nettoie une VM connue de libvirt |
| `virt-sysprep -a image.qcow2` | Nettoie directement une image disque |
| `virt-sysprep --list-operations` | Liste les opérations disponibles |
| `virt-sysprep --operations ...` | Limite l'exécution à un ensemble précis d'opérations |

## Vérification

Après le premier démarrage d'un clone, vérifier que l'identité système a bien été régénérée.

```bash
cat /etc/machine-id
ls /etc/ssh/ssh_host_*
```

!!! success "Résultat attendu"
    Le fichier `/etc/machine-id` n'est plus vide et les clés hôtes SSH présentes sur le clone ont été recréées localement au premier démarrage.

## Ressources

- [Documentation officielle libguestfs](https://libguestfs.org/) — Présentation de la suite d'outils
- [Manpage de virt-sysprep](https://libguestfs.org/virt-sysprep.1.html) — Référence complète des options et opérations
