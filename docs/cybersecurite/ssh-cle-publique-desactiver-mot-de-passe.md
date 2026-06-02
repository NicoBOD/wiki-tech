---
title: Configurer l’accès SSH par clé et désactiver l’authentification par mot de passe sur Ubuntu Server
date: 2026-06-02
author: Nicolas BODAINE
tags:
  - ssh
  - sécurité
  - cybersecurité
  - ubuntu
  - linux
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# Configurer l’accès SSH par clé et désactiver l’authentification par mot de passe sur Ubuntu Server

!!! abstract "Résumé"
    Ce tutoriel explique comment renforcer la sécurité d'un serveur Ubuntu en configurant l'authentification SSH par clé cryptographique, puis en désactivant complètement l'accès par mot de passe. C'est une mesure de durcissement (hardening) fondamentale pour protéger votre serveur contre les attaques par force brute.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 LTS |
| Dernière mise à jour | 2026-06-02 |

## Contexte

Par défaut, l'accès SSH à un serveur Ubuntu (ou à toute distribution Linux) est souvent sécurisé uniquement par un mot de passe. Bien qu'un mot de passe fort soit une première ligne de défense, il reste vulnérable aux attaques par force brute et aux fuites de données. 

L'authentification par clé SSH repose sur une paire de clés cryptographiques (une privée et une publique). Elle est non seulement beaucoup plus sécurisée, mais aussi plus pratique à l'usage, car elle vous évite de taper votre mot de passe à chaque connexion.

Cette procédure est la suite logique des mesures de sécurité de base comme la [configuration d'UFW](ufw-ubuntu-server-premieres-regles.md) et l'[installation de Fail2ban](fail2ban-proteger-ssh-ubuntu-server.md).

## Prérequis

- Un serveur Ubuntu accessible en SSH (avec un utilisateur disposant des droits `sudo`).
- Un poste client (Linux, macOS, ou Windows avec PowerShell/Git Bash) depuis lequel vous vous connecterez.

## Procédure

### Étape 1 : Générer une paire de clés SSH sur le poste client

La première étape consiste à créer la paire de clés sur la machine depuis laquelle vous allez vous connecter (votre poste de travail, **pas le serveur**).

Sur votre poste client, ouvrez un terminal et tapez la commande suivante. Nous utiliserons l'algorithme Ed25519, qui est actuellement la norme recommandée pour sa sécurité et ses performances.

```bash
ssh-keygen -t ed25519 -C "votre_email@exemple.com"
```

!!! note "Explication des paramètres"
    - `-t ed25519` : Spécifie le type de clé à créer.
    - `-C` : Permet d'ajouter un commentaire (généralement une adresse email ou le nom du poste) pour identifier facilement la clé.

Le système vous posera quelques questions :

1. **Emplacement de sauvegarde :** Appuyez sur ++enter++ pour accepter l'emplacement par défaut (`~/.ssh/id_ed25519`).
2. **Passphrase (phrase secrète) :** Il est fortement recommandé d'entrer une phrase secrète pour protéger votre clé privée en cas de vol de votre ordinateur. Si vous préférez ne pas en mettre (déconseillé pour des environnements critiques), appuyez simplement sur ++enter++.

### Étape 2 : Copier la clé publique sur le serveur

Maintenant que vos clés sont générées, vous devez envoyer la clé **publique** (`id_ed25519.pub`) sur votre serveur Ubuntu. La clé privée (`id_ed25519`) ne doit **jamais** quitter votre poste.

Utilisez la commande `ssh-copy-id`, qui automatise l'ajout de la clé publique dans le fichier `~/.ssh/authorized_keys` de votre utilisateur sur le serveur.

```bash
ssh-copy-id utilisateur@adresse_ip_du_serveur
```

Le système vous demandera le mot de passe de votre utilisateur sur le serveur pour effectuer cette copie initiale.

!!! tip "Alternative pour les utilisateurs Windows sans `ssh-copy-id`"
    Si vous êtes sous Windows et que la commande `ssh-copy-id` n'est pas disponible, vous pouvez utiliser cette commande PowerShell pour faire la même chose :
    ```powershell
    type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh utilisateur@adresse_ip_du_serveur "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
    ```

### Étape 3 : Tester la connexion par clé

Avant de désactiver l'authentification par mot de passe, il est crucial de s'assurer que l'authentification par clé fonctionne correctement, sinon vous risquez de vous bloquer en dehors du serveur !

Essayez de vous connecter au serveur :

```bash
ssh utilisateur@adresse_ip_du_serveur
```

Si vous aviez configuré une passphrase à l'étape 1, elle vous sera demandée. Autrement, vous devriez être connecté instantanément sans qu'on vous demande le mot de passe de l'utilisateur distant.

### Étape 4 : Désactiver l'authentification par mot de passe

Une fois que vous avez confirmé que la connexion par clé fonctionne, vous pouvez fermer la porte aux attaques par force brute en refusant les mots de passe.

Sur votre serveur Ubuntu (via votre connexion SSH ouverte à l'étape précédente), éditez le fichier de configuration du service SSH :

```bash
sudo nano /etc/ssh/sshd_config
```

Recherchez la ligne concernant `PasswordAuthentication`. Elle est souvent commentée (précédée d'un `#`) ou définie sur `yes`. 

Modifiez-la pour qu'elle ressemble exactement à ceci (assurez-vous d'enlever le `#` s'il est présent) :

```text title="/etc/ssh/sshd_config"
PasswordAuthentication no
```

Profitez-en pour vérifier que l'authentification par clé publique est bien activée (c'est le cas par défaut) :

```text title="/etc/ssh/sshd_config"
PubkeyAuthentication yes
```

Enregistrez et quittez l'éditeur (++ctrl+o++, ++enter++, ++ctrl+x++).

### Étape 5 : Redémarrer le service SSH

Pour appliquer les modifications, redémarrez le service SSH sur le serveur :

```bash
sudo systemctl restart ssh
```

!!! danger "Attention"
    **Ne fermez pas votre session SSH actuelle tout de suite !** 
    Ouvrez un nouveau terminal sur votre poste client et essayez de vous connecter. Si cela fonctionne, vous pouvez fermer toutes vos fenêtres en toute sécurité.

## Vérification

Pour vérifier que l'authentification par mot de passe est bien désactivée, essayez de vous connecter au serveur depuis une machine (ou en forçant l'authentification par mot de passe) qui n'a pas la clé SSH configurée.

Vous pouvez forcer SSH à ignorer vos clés locales avec cette commande :

```bash
ssh -o PubkeyAuthentication=no utilisateur@adresse_ip_du_serveur
```

!!! success "Résultat attendu"
    Le serveur doit refuser la connexion immédiatement, sans même vous demander de mot de passe, avec un message du type :
    `utilisateur@adresse_ip_du_serveur: Permission denied (publickey).`

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `ssh-keygen -t ed25519` | Génère une nouvelle paire de clés SSH (Ed25519) |
| `ssh-copy-id user@ip` | Copie la clé publique sur le serveur distant |
| `sudo nano /etc/ssh/sshd_config` | Édite le fichier de configuration du serveur SSH |
| `sudo systemctl restart ssh` | Applique les modifications de la configuration SSH |

## Ressources

- [Documentation Ubuntu Server - OpenSSH](https://ubuntu.com/server/docs/service-openssh)
- [Manuel sshd_config - OpenBSD](https://man.openbsd.org/sshd_config)
