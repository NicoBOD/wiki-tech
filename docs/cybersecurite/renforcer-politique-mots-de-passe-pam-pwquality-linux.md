---
title: Renforcer la politique de mots de passe sous Linux avec pam_pwquality
date: 2026-06-27
author: Nicolas BODAINE
tags:
  - sécurité
  - linux
  - pam
  - mots-de-passe
difficulty: intermédiaire
os: Ubuntu 24.04 / Debian 12
status: publié
---

# Renforcer la politique de mots de passe sous Linux avec pam_pwquality

!!! abstract "Résumé"
    Dans ce tutoriel, vous apprendrez à utiliser le module `pam_pwquality` pour imposer des règles de complexité, de longueur et de qualité sur les mots de passe des utilisateurs sous Linux.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 / Debian 12 |
| Dernière mise à jour | 2026-06-27 |

## Contexte

Par défaut, les systèmes Linux modernes n'imposent pas toujours des règles très strictes sur les mots de passe locaux. Or, dans un environnement d'entreprise, scolaire ou pour vos serveurs personnels exposés, il est critique de s'assurer que les utilisateurs ne définissent pas de mots de passe faibles (ex: `azerty`, `123456`, ou leur nom d'utilisateur).

Le module PAM (Pluggable Authentication Modules) `pam_pwquality` permet d'imposer des critères robustes : longueur minimale, présence de différents types de caractères (majuscules, chiffres, caractères spéciaux) et vérification par rapport à un dictionnaire (pour rejeter les mots courants).

## Prérequis

- Un système Linux basé sur Debian ou Ubuntu (testé sur Ubuntu 24.04 et Debian 12).
- Un accès avec les privilèges `root` ou via `sudo`.

## Procédure

### Étape 1 : Installation du paquet

Sur la plupart des distributions basées sur Debian, le module n'est pas forcément installé par défaut ou nécessite un paquet spécifique pour être configuré finement.

```bash
sudo apt update
sudo apt install libpam-pwquality
```

### Étape 2 : Configuration des règles

La configuration se fait dans le fichier `/etc/security/pwquality.conf`. Ce fichier contient de nombreux paramètres commentés par défaut.

Éditez le fichier :

```bash
sudo nano /etc/security/pwquality.conf
```

Voici quelques paramètres recommandés pour durcir la politique de mots de passe :

```ini title="/etc/security/pwquality.conf"
# Longueur minimale du mot de passe
minlen = 14

# Nombre minimum de classes de caractères différentes (majuscules, minuscules, chiffres, symboles)
# 4 = oblige à utiliser les 4 classes
minclass = 4

# Empêche l'utilisation de mots de passe qui sont juste des mots du dictionnaire inversés
dictcheck = 1

# Le nouveau mot de passe doit différer de l'ancien d'au moins X caractères
difok = 5

# Nombre maximum de caractères consécutifs d'une même classe (ex: abc, 123)
maxsequence = 3

# Refuse un mot de passe qui contient le nom de l'utilisateur (sous forme directe ou inversée)
usercheck = 1
```

### Étape 3 : Application à la configuration PAM

En général, sur les systèmes Debian/Ubuntu récents, l'installation du paquet met automatiquement à jour les fichiers de configuration PAM via `pam-auth-update`. Le module `pwquality` remplace alors l'ancien module `pam_cracklib` s'il était présent.

Toutefois, pour forcer l'application de ces règles **même pour l'utilisateur root**, vous pouvez modifier le fichier PAM des mots de passe communs :

```bash
sudo nano /etc/pam.d/common-password
```

Repérez la ligne contenant `pam_pwquality.so` et ajoutez l'option `enforce_for_root` si vous souhaitez que ces contraintes s'appliquent aussi quand l'administrateur change les mots de passe (par défaut, root peut outrepasser les règles).

```text hl_lines="1"
password        requisite                       pam_pwquality.so retry=3 enforce_for_root
```

- `retry=3` : L'utilisateur aura 3 tentatives pour saisir un mot de passe valide.

## Vérification

Pour vérifier que la politique est bien en place, créez un utilisateur de test et essayez de lui attribuer un mot de passe faible :

```bash
sudo adduser testuser
sudo passwd testuser
```

Essayez de saisir `motdepasse` ou `12345`. Le système devrait refuser avec un message d'erreur :

!!! success "Résultat attendu"
    ```text
    Nouveau mot de passe : 
    Mauvais mot de passe : Le mot de passe est trop court
    Nouveau mot de passe : 
    Mauvais mot de passe : Le mot de passe ne contient pas assez de types de caractères différents
    ```

Une fois le test terminé, vous pouvez supprimer l'utilisateur :

```bash
sudo deluser --remove-home testuser
```

## Ressources

- [Manuel Ubuntu : pam_pwquality](https://manpages.ubuntu.com/manpages/jammy/en/man8/pam_pwquality.8.html) — Documentation officielle des paramètres.
- [ANSSI : Recommandations relatives à l'authentification multifacteur et aux mots de passe](https://messervices.cyber.gouv.fr/documents-guides/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf) — Pour justifier le choix d'une longueur minimale (ex: 14 ou 15 caractères).
