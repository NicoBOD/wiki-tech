---
icon: material/security
description: Protection des serveurs, pare-feu, certificats SSL et bonnes pratiques de durcissement.
---

# Cybersécurité

Protection des serveurs, pare-feu, certificats SSL et bonnes pratiques de durcissement.

## Durcissement SSH & Accès

- [Sécuriser SSH avec l'authentification double facteur (MFA) via Google Authenticator](ssh-mfa-google-authenticator.md) — Ajouter une surcouche de sécurité (TOTP) aux connexions distantes.
- [Configurer l’accès SSH par clé et désactiver l’authentification par mot de passe sur Ubuntu Server](ssh-cle-publique-desactiver-mot-de-passe.md) — Se prémunir contre les attaques par force brute sur le port 22.
- [Installer et configurer Fail2ban pour protéger SSH sur Ubuntu Server 24.04](fail2ban-proteger-ssh-ubuntu-server.md) — Bannir automatiquement les adresses IP tentant de forcer l'accès.
- [Protéger un serveur Linux avec CrowdSec : l'alternative collaborative à Fail2ban](crowdsec-alternative-fail2ban-linux.md) — Détecter et bloquer les attaques via un système de renseignement communautaire sur les menaces (CTI).

## Pare-feu (Firewall)

- [UFW sur Ubuntu Server — ouvrir seulement SSH, HTTP et HTTPS](ufw-ubuntu-server-premieres-regles.md) — Filtrer les connexions entrantes avec le pare-feu simplifié Uncomplicated Firewall.

## Certificats SSL & Chiffrement

- [Sécuriser un serveur web Nginx avec Let's Encrypt et Certbot sur Ubuntu Server](certbot-nginx-https-lets-encrypt-ubuntu.md) — Obtenir et renouveler automatiquement un certificat TLS/SSL gratuit.
- [Sécuriser un volume de données avec le chiffrement LUKS sous Linux](securiser-volume-donnees-chiffrement-luks-linux.md) — Protéger les données au repos en chiffrant un disque ou une partition.
- [Déverrouiller automatiquement LUKS au démarrage avec le TPM2 et Clevis (Ubuntu 24.04)](dechiffrer-automatiquement-luks-tpm2-clevis-secure-boot-ubuntu.md) — Ne plus saisir sa phrase de passe au boot en déléguant le déverrouillage au TPM, de façon sûre et réversible.
- [Chiffrer et signer des fichiers avec GPG sous Linux](chiffrer-signer-fichiers-gpg-linux.md) — Garantir la confidentialité et l'authenticité de vos fichiers locaux et échangés.
- [Chiffrer un poste Windows 11 Pro avec BitLocker : disque système, BitLocker To Go, manage-bde et déblocage helpdesk](chiffrer-poste-windows-11-bitlocker-manage-bde-deblocage-helpdesk.md) — Chiffrer `C:` et une clé USB, piloter BitLocker en ligne de commande et débloquer un poste coincé sur l'écran de récupération.

## Audit & Conformité

- [Auditer la sécurité de son serveur Linux avec Lynis](lynis-audit-securite-linux.md) — Réaliser un scan de vulnérabilités et évaluer le durcissement du système avec un outil open-source.
- [Cartographier et analyser les ports d'un réseau avec Nmap](cartographier-analyser-ports-reseau-nmap.md) — Découvrir les hôtes actifs et les services ouverts avec le scanner de référence.
- [Analyser son réseau Wi-Fi en mode moniteur et tester l'injection avec Aircrack-ng](analyser-wifi-mode-moniteur-injection-aircrack-ng.md) — Scanner, capturer un handshake WPA/WPA3 et tester la robustesse d'un mot de passe Wi-Fi.

## Durcissement Système
- [Configurer `sudo` en toute sécurité avec `visudo`](configurer-sudo-visudo.md) — Limiter les privilèges des utilisateurs.
- [Renforcer la politique de mots de passe sous Linux avec pam_pwquality](renforcer-politique-mots-de-passe-pam-pwquality-linux.md) — Imposer des règles de complexité, de longueur et de qualité sur les mots de passe.
- [Activer le lecteur d'empreintes digitales (login + sudo) sur ThinkPad sous Ubuntu 24.04](activer-lecteur-empreintes-digitales-login-sudo-thinkpad-ubuntu.md) — Faire fonctionner un capteur Validity 138a:0097 (python-validity/open-fprintd) pour déverrouiller la session et authentifier sudo.

- [Renforcer la sécurité d'un service avec AppArmor sous Ubuntu](renforcer-securite-service-apparmor-ubuntu.md) — Créer un périmètre de sécurité strict (sandbox) pour limiter les capacités des applications.
