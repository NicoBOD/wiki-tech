---
title: Configurer sudo en toute sécurité avec visudo
date: 2026-06-25
author: Nicolas BODAINE
tags:
  - sudo
  - visudo
  - securite
  - privileges
difficulty: intermédiaire
os: Debian / Ubuntu / Linux
status: publié
---

# Configurer `sudo` en toute sécurité et limiter les privilèges avec `visudo`

!!! abstract "Résumé"
    Sous Linux, la commande `sudo` permet d'exécuter des commandes avec les droits du superutilisateur (`root`). Toutefois, accorder l'accès total à un utilisateur peut représenter une faille de sécurité majeure. Ce tutoriel vous apprend à limiter finement les privilèges des utilisateurs grâce au fichier `/etc/sudoers` et l'outil indispensable `visudo`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux (Debian, Ubuntu, CentOS, etc.) |
| Dernière mise à jour | 2026-06-25 |

## Contexte

Dans une infrastructure en production ou dans les TP, il est rare de donner le mot de passe `root` à tout le monde. La bonne pratique est d'utiliser `sudo`. Mais comment faire si un développeur a uniquement besoin de relancer le service Apache, et d'absolument rien d'autre ? 
C'est ici qu'intervient la configuration fine du fichier `/etc/sudoers` via la commande **`visudo`**.

!!! danger "Attention"
    N'éditez **jamais** le fichier `/etc/sudoers` avec `nano` ou `vim` directement. Utilisez **toujours** la commande `visudo`. Cet outil vérifie la syntaxe avant d'enregistrer. Une erreur de syntaxe dans ce fichier peut bloquer définitivement tout accès administrateur à votre machine !

## Prérequis

- Un accès root ou un compte possédant déjà tous les droits `sudo`.
- Une machine Linux (machine virtuelle, VPS ou locale).

## Procédure

### Étape 1 : Comprendre la syntaxe de base

Exécutez la commande `visudo` (en tant que root ou via `sudo visudo`). Vous verrez des lignes ressemblant à celle-ci :

```text
root    ALL=(ALL:ALL) ALL
```

Décortiquons cette syntaxe :
1. **`root`** : L'utilisateur concerné.
2. **`ALL=`** : Sur quels hôtes cette règle s'applique (généralement `ALL`).
3. **`(ALL:ALL)`** : En tant que quel utilisateur/groupe la commande peut être lancée.
4. **`ALL`** : Quelles commandes peuvent être exécutées.

### Étape 2 : Créer un alias de commandes (Cmnd_Alias)

Pour rendre le fichier lisible, on peut regrouper plusieurs commandes sous un même nom. Ajoutez ceci dans le fichier :

```text
Cmnd_Alias WEB_RESTART = /bin/systemctl restart apache2, /bin/systemctl reload apache2, /bin/systemctl status apache2
```

### Étape 3 : Accorder des droits limités à un utilisateur

Supposons que nous voulons autoriser l'utilisateur `dev1` à utiliser les commandes définies dans `WEB_RESTART` **sans qu'on lui demande son mot de passe** (pratique pour l'automatisation ou les déploiements).

Ajoutez cette ligne à la fin du fichier :

```text
dev1    ALL=(ALL:ALL) NOPASSWD: WEB_RESTART
```

Si vous voulez qu'il puisse exécuter une commande spécifique tout en devant taper **son** mot de passe, utilisez cette syntaxe :

```text
dev1    ALL=(ALL:ALL) /usr/bin/apt update, /usr/bin/apt upgrade
```

## Vérification

Pour vérifier quels sont vos propres privilèges `sudo`, connectez-vous avec l'utilisateur testé (ex: `su - dev1`) et lancez :

```bash
sudo -l
```

!!! success "Résultat attendu"
    Le système affichera les commandes autorisées pour cet utilisateur :
    ```text
    Matching Defaults entries for dev1 on serveur-web:
        env_reset, mail_badpass, secure_path=...

    User dev1 may run the following commands on serveur-web:
        (ALL : ALL) NOPASSWD: /bin/systemctl restart apache2, /bin/systemctl reload apache2, /bin/systemctl status apache2
        (ALL : ALL) /usr/bin/apt update, /usr/bin/apt upgrade
    ```

Essayez ensuite de lancer une commande interdite (ex: `sudo fdisk -l`), le système vous refusera l'accès.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `visudo` | Édite `/etc/sudoers` de façon sécurisée |
| `sudo -l` | Liste les privilèges sudo de l'utilisateur actuel |
| `sudo -u bob commande` | Exécute une commande en tant que l'utilisateur `bob` |
| `NOPASSWD:` | Mot-clé pour autoriser `sudo` sans taper de mot de passe |

## Ressources

- [Guide d'hygiène informatique de l'ANSSI](https://www.ssi.gouv.fr/) — Recommandations sur le moindre privilège.
- Man pages : `man sudoers` et `man visudo`.
