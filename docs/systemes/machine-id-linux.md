---
title: "Comprendre et gérer le `machine-id` sous Linux"
date: 2026-04-23
author: Nicolas BODAINE
tags:
  - linux
  - systemd
  - machine-id
  - dhcp
  - virtualisation
difficulty: intermédiaire
os: Linux
status: publié
---

# Comprendre et gérer le `machine-id` sous Linux

!!! abstract "Résumé"
    Le fichier `/etc/machine-id` est l'identifiant unique d'une installation Linux.
    Cette note explique son rôle, les risques liés au clonage de VM et la bonne méthode pour le réinitialiser avant de créer un template.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux avec `systemd` |
| Dernière mise à jour | 2026-04-23 |

## Contexte

Le fichier `/etc/machine-id` contient une chaîne de **32 caractères hexadécimaux** générée aléatoirement lors de l'installation ou du premier démarrage du système.

Exemple :

```text
d5a415053f3e49de8e176461a5e783ab
```

Contrairement à une adresse MAC, cet identifiant représente **l'instance du système d'exploitation** et non le matériel.
Il doit rester stable pendant toute la durée de vie de cette instance.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `cat /etc/machine-id` | Afficher l'identifiant actuel |
| `truncate -s 0 /etc/machine-id` | Vider le fichier avant de transformer une VM en template |
| `systemd-machine-id-setup` | Générer un `machine-id` si le système doit être initialisé manuellement |
| `virt-sysprep` | Nettoyer une image de VM éteinte avant clonage |

## À quoi sert le `machine-id` ?

De nombreux composants Linux modernes s'appuient sur cet identifiant :

- **DHCP** : des outils comme `NetworkManager` ou `systemd-networkd` l'utilisent pour dériver le **DUID** (*DHCP Unique Identifier*) envoyé au serveur DHCP.
- **Journalisation** : `systemd-journald` s'en sert pour distinguer les journaux provenant de différentes machines.
- **D-Bus et configuration persistante** : il participe à l'identité locale du système pour plusieurs services et environnements de bureau.

## Problème

Le piège classique apparaît lors du **clonage de machines virtuelles**.
Si la machine source et ses clones conservent le même `/etc/machine-id`, ils partagent la même identité système.

Cela peut provoquer :

- des **conflits d'adresses IP** si le serveur DHCP reçoit le même DUID depuis plusieurs VM ;
- des **logs mélangés** sur une plateforme de journalisation centralisée ;
- des comportements incohérents dans les services qui s'appuient sur l'identité de la machine.

!!! warning "Ne pas déployer un clone tel quel"
    Avant de finaliser un template ou une image de VM, videz toujours le `machine-id` pour forcer la génération d'un nouvel identifiant au premier démarrage du clone.

## Solution

### Méthode 1 : utiliser `virt-sysprep` (recommandé)

`virt-sysprep` prépare une image de machine virtuelle **éteinte** avant clonage.
En plus du `machine-id`, il peut également nettoyer les clés SSH, certaines traces réseau et d'autres artefacts propres à la machine source.

Exemple sur une image disque :

```bash
virt-sysprep -a /chemin/vers/image.qcow2
```

!!! tip "Pourquoi cette méthode est préférable"
    Elle limite les oublis et automatise plusieurs nettoyages nécessaires avant de créer un template réutilisable.

### Méthode 2 : vider manuellement le fichier

Si vous préparez le template à la main, **ne supprimez pas** `/etc/machine-id`.
Laissez le fichier en place, mais videz son contenu juste avant d'éteindre la VM :

```bash
sudo truncate -s 0 /etc/machine-id
```

Selon la distribution, vérifiez aussi l'état de `/var/lib/dbus/machine-id` s'il existe encore comme fichier distinct ou comme lien symbolique.

### Que se passe-t-il au prochain démarrage ?

Au premier démarrage du clone, `systemd` détecte que `/etc/machine-id` existe mais est vide.
Il génère alors immédiatement un nouvel identifiant unique via `systemd-machine-id-setup`, ce qui donne au clone sa propre identité.

## Vérification

Après le premier démarrage du clone, validez que le `machine-id` a bien été régénéré :

```bash
cat /etc/machine-id
grep -E '^[0-9a-f]{32}$' /etc/machine-id && echo "machine-id valide"
```

!!! success "Résultat attendu"
    Le fichier contient une nouvelle valeur sur 32 caractères hexadécimaux, différente de celle de la machine source.

## Glossaire

`machine-id`
:   Identifiant unique de l'instance Linux stocké dans `/etc/machine-id`.

`DUID`
:   *DHCP Unique Identifier* utilisé par certains clients DHCP pour s'identifier auprès du serveur.

`Template`
:   Image ou VM de référence utilisée pour créer plusieurs clones.

## Ressources

- [man machine-id](https://www.freedesktop.org/software/systemd/man/latest/machine-id.html) — Documentation officielle sur le format et l'usage du `machine-id`
- [man systemd-machine-id-setup](https://www.freedesktop.org/software/systemd/man/latest/systemd-machine-id-setup.html) — Génération et initialisation du `machine-id`
- [virt-sysprep](https://libguestfs.org/virt-sysprep.1.html) — Outil de préparation d'images de machines virtuelles
