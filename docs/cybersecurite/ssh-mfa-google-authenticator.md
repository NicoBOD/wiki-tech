---
title: Sécuriser SSH avec l'authentification double facteur (MFA) via Google Authenticator
date: 2026-06-10
author: Nicolas BODAINE
tags:
  - ssh
  - securite
  - mfa
  - 2fa
  - linux
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Sécuriser SSH avec l'authentification double facteur (MFA) via Google Authenticator

!!! abstract "Résumé"
    Ce tutoriel explique comment renforcer la sécurité d'un serveur Linux en ajoutant une authentification à deux facteurs (2FA/MFA) pour les connexions SSH, à l'aide du module PAM Google Authenticator.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 / Debian |
| Dernière mise à jour | 2026-06-10 |

## Contexte

Par défaut, l'accès SSH à un serveur repose sur un mot de passe ou une clé publique. Bien que l'authentification par clé SSH soit recommandée, l'ajout d'un deuxième facteur (MFA) offre une couche de protection supplémentaire essentielle en cas de compromission de votre clé ou de votre mot de passe. Le module Pluggable Authentication Module (PAM) de Google permet d'intégrer des codes à usage unique basés sur le temps (TOTP) générés par une application sur votre smartphone.

!!! warning "Attention"
    Il est vivement recommandé de garder une session SSH active durant toute l'opération pour éviter de vous bloquer en dehors de votre serveur en cas d'erreur de configuration.

## Prérequis

- Un serveur sous Ubuntu/Debian avec un accès SSH fonctionnel.
- Les droits administrateur (utilisateur avec `sudo`).
- Un smartphone avec une application TOTP installée (Google Authenticator, Aegis, Authy, FreeOTP, etc.).

## Procédure

### Étape 1 : Installation du module PAM

Installez le paquet de la bibliothèque PAM Google Authenticator via le gestionnaire de paquets de votre distribution :

```bash
sudo apt update
sudo apt install libpam-google-authenticator -y
```

### Étape 2 : Configuration du TOTP pour l'utilisateur

En tant que l'utilisateur qui va se connecter en SSH (ne pas utiliser `sudo` ici pour configurer l'utilisateur courant), exécutez la commande d'initialisation :

```bash
google-authenticator
```

L'outil va vous poser une série de questions. Voici les recommandations :

1. **Voulez-vous que les jetons d'authentification soient basés sur le temps ?** : Répondez `y` (yes).
2. Un grand code QR s'affiche dans votre terminal. Scannez-le avec votre application TOTP sur votre smartphone.
3. **Mettez en sécurité vos codes de secours (scratch codes)** : Copiez-les et gardez-les dans un gestionnaire de mots de passe. Ils vous sauveront si vous perdez votre téléphone.
4. **Voulez-vous mettre à jour le fichier `~/.google_authenticator` ?** : Répondez `y`.
5. **Interdire l'usage multiple du même jeton ?** : Répondez `y` (réduit le risque d'attaque par rejeu).
6. **Compenser le désynchronisme temporel (time skew) ?** : Répondez `n` (sauf si vous rencontrez souvent des problèmes d'horloge).
7. **Limiter à 3 essais de connexion toutes les 30 secondes ?** : Répondez `y` (protection contre le brute-force).

### Étape 3 : Configuration du système PAM pour SSH

Il faut maintenant indiquer au système PAM d'exiger le code TOTP pour le service SSH. Éditez le fichier `/etc/pam.d/sshd` :

```bash
sudo nano /etc/pam.d/sshd
```

Ajoutez la ligne suivante à la fin du fichier :

```text
auth required pam_google_authenticator.so
```

*(Si vous souhaitez que le MFA soit demandé uniquement à ceux qui l'ont configuré et ignorer les autres, utilisez plutôt `auth required pam_google_authenticator.so nullok`)*

Sauvegardez (++ctrl+o++, ++enter++) et fermez (++ctrl+x++).

### Étape 4 : Configuration du serveur SSH (sshd)

Ensuite, configurez le démon SSH pour accepter ce type d'authentification interactive. Éditez `/etc/ssh/sshd_config` :

```bash
sudo nano /etc/ssh/sshd_config
```

Trouvez l'option `KbdInteractiveAuthentication` (ou `ChallengeResponseAuthentication` sur les anciennes versions) et passez-la à `yes` :

```text
KbdInteractiveAuthentication yes
```

*(Assurez-vous qu'elle n'est pas commentée, enlevez le `#` si présent)*

Sauvegardez et fermez le fichier.

### Étape 5 : Redémarrage du service SSH

Appliquez les modifications en redémarrant le service `ssh` :

```bash
sudo systemctl restart ssh
```

## Vérification

1. **Ne fermez pas** votre session SSH actuelle !
2. Ouvrez un **nouveau terminal** et tentez de vous connecter à votre serveur :

```bash
ssh utilisateur@ip_du_serveur
```

!!! success "Résultat attendu"
    Après avoir saisi votre mot de passe (ou été authentifié par clé), le système doit vous demander le code :
    ```text
    Verification code:
    ```
    Saisissez le code à 6 chiffres généré par votre application sur votre smartphone.

## Ressources

- [Documentation officielle Ubuntu sur OpenSSH](https://ubuntu.com/server/docs/service-openssh) — Guide général SSH Ubuntu.
- [Page GitHub de google-authenticator-libpam](https://github.com/google/google-authenticator-libpam) — Documentation et code source du module PAM.
