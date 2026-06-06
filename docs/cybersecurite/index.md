---
icon: material/security
description: Protection des serveurs, pare-feu, certificats SSL et bonnes pratiques de durcissement.
---

# Cybersécurité

Protection des serveurs, pare-feu, certificats SSL et bonnes pratiques de durcissement.

## Durcissement SSH & Accès

- [Configurer l’accès SSH par clé et désactiver l’authentification par mot de passe sur Ubuntu Server](ssh-cle-publique-desactiver-mot-de-passe.md) — Se prémunir contre les attaques par force brute sur le port 22.
- [Installer et configurer Fail2ban pour protéger SSH sur Ubuntu Server 24.04](fail2ban-proteger-ssh-ubuntu-server.md) — Bannir automatiquement les adresses IP tentant de forcer l'accès.

## Pare-feu (Firewall)

- [UFW sur Ubuntu Server — ouvrir seulement SSH, HTTP et HTTPS](ufw-ubuntu-server-premieres-regles.md) — Filtrer les connexions entrantes avec le pare-feu simplifié Uncomplicated Firewall.

## Certificats SSL & Chiffrement

- [Sécuriser un serveur web Nginx avec Let's Encrypt et Certbot sur Ubuntu Server](certbot-nginx-https-lets-encrypt-ubuntu.md) — Obtenir et renouveler automatiquement un certificat TLS/SSL gratuit.
