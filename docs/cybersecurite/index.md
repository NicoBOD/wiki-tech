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

## Pare-feu (Firewall)

- [UFW sur Ubuntu Server — ouvrir seulement SSH, HTTP et HTTPS](ufw-ubuntu-server-premieres-regles.md) — Filtrer les connexions entrantes avec le pare-feu simplifié Uncomplicated Firewall.

## Certificats SSL & Chiffrement

- [Sécuriser un serveur web Nginx avec Let's Encrypt et Certbot sur Ubuntu Server](certbot-nginx-https-lets-encrypt-ubuntu.md) — Obtenir et renouveler automatiquement un certificat TLS/SSL gratuit.
- [Sécuriser un volume de données avec le chiffrement LUKS sous Linux](securiser-volume-donnees-chiffrement-luks-linux.md) — Protéger les données au repos en chiffrant un disque ou une partition.

## Audit & Conformité

- [Auditer la sécurité de son serveur Linux avec Lynis](lynis-audit-securite-linux.md) — Réaliser un scan de vulnérabilités et évaluer le durcissement du système avec un outil open-source.
- [Cartographier et analyser les ports d'un réseau avec Nmap](cartographier-analyser-ports-reseau-nmap.md) — Découvrir les hôtes actifs et les services ouverts avec le scanner de référence.
