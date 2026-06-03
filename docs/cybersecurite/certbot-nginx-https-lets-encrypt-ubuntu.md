---
title: Sécuriser un serveur web Nginx avec Let's Encrypt et Certbot sur Ubuntu Server
date: 2026-06-03
author: Nicolas BODAINE
tags:
  - securite
  - nginx
  - tls
  - https
  - ubuntu
  - certbot
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Sécuriser un serveur web Nginx avec Let's Encrypt et Certbot sur Ubuntu Server

!!! abstract "Résumé"
    Ce tutoriel explique comment générer et configurer un certificat SSL/TLS gratuit via **Let's Encrypt** avec l'outil **Certbot** pour sécuriser un serveur web **Nginx** sur Ubuntu Server. Vous apprendrez à configurer la redirection automatique vers HTTPS et à vérifier le renouvellement automatique.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 (compatible 22.04 / 20.04) |
| Dernière mise à jour | 2026-06-03 |

## Contexte

Par défaut, un serveur web communique en texte clair sur le port 80 (HTTP). Cela signifie que toutes les données échangées (mots de passe, informations personnelles) peuvent être interceptées. Le passage au HTTPS (port 443) permet de chiffrer ces échanges grâce à un certificat SSL/TLS. L'autorité de certification **Let's Encrypt** fournit ces certificats gratuitement, et **Certbot** permet d'automatiser entièrement leur obtention, leur installation et leur renouvellement sur un serveur Nginx.

## Prérequis

- Un serveur Ubuntu avec **Nginx** installé et configuré.
- Un nom de domaine valide (ex: `site.exemple.com`) qui pointe vers l'adresse IP publique de votre serveur via un enregistrement DNS de type `A`.
- Un accès réseau permettant le trafic HTTP (port 80) et HTTPS (port 443). (Si vous utilisez UFW, vérifiez que ces ports sont ouverts).
- Les privilèges `root` ou l'accès à `sudo`.

## Procédure

### Étape 1 : Installer Certbot et son plugin pour Nginx

Certbot est le client recommandé par Let's Encrypt. Il est disponible directement dans les dépôts officiels d'Ubuntu.

```bash
# Mettre à jour la liste des paquets
sudo apt update

# Installer Certbot et le plugin Nginx
sudo apt install certbot python3-certbot-nginx -y
```

### Étape 2 : Vérifier la configuration de Nginx

Pour que Certbot puisse configurer automatiquement le SSL pour Nginx, il doit être capable de trouver le bon bloc `server` dans la configuration de Nginx. 

Ouvrez la configuration de votre site :

```bash
sudo nano /etc/nginx/sites-available/votresite
```

Assurez-vous que la directive `server_name` correspond bien à votre nom de domaine :

```nginx
server {
    listen 80;
    server_name site.exemple.com www.site.exemple.com;
    
    # ... le reste de votre configuration
}
```

Vérifiez que la configuration ne contient pas d'erreurs de syntaxe, puis rechargez Nginx si vous avez fait des modifications :

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Étape 3 : Configurer le pare-feu (UFW)

Si le pare-feu **UFW** est activé, il faut autoriser le trafic HTTPS (port 443).

```bash
# Afficher l'état actuel de UFW
sudo ufw status
```

S'il n'y a pas de règle pour `Nginx Full` (qui ouvre les ports 80 et 443) :

```bash
# Autoriser HTTP et HTTPS
sudo ufw allow 'Nginx Full'

# (Optionnel) Supprimer la règle HTTP simple si vous l'aviez ajoutée
sudo ufw delete allow 'Nginx HTTP'
```

### Étape 4 : Obtenir le certificat SSL

Lancez Certbot en utilisant le plugin Nginx. Certbot s'occupera d'obtenir le certificat et de modifier la configuration de Nginx pour l'utiliser.

```bash
sudo certbot --nginx -d site.exemple.com -d www.site.exemple.com
```

Certbot va vous poser quelques questions :
1. **Adresse e-mail** : Entrez une adresse e-mail valide pour recevoir les alertes de renouvellement et les avis de sécurité.
2. **Conditions d'utilisation** : Acceptez les conditions (`A`).
3. **Partage d'e-mail** : Choisissez si vous souhaitez partager votre e-mail avec l'EFF (`Y` ou `N`).

Certbot communiquera ensuite avec Let's Encrypt. Si tout se passe bien, vos certificats seront téléchargés, installés, et Nginx sera automatiquement rechargé. 

!!! success "Succès"
    Certbot modifiera la configuration de votre site Nginx pour ajouter les directives SSL et rediriger automatiquement le trafic HTTP vers HTTPS.

## Vérification

### 1. Tester l'accès en HTTPS

Ouvrez votre navigateur web et rendez-vous sur `http://site.exemple.com`. Vous devriez être automatiquement redirigé vers `https://site.exemple.com` et voir un cadenas fermé dans la barre d'adresse, indiquant que la connexion est sécurisée.

### 2. Tester le renouvellement automatique

Les certificats Let's Encrypt sont valides pendant 90 jours. Certbot installe automatiquement un timer `systemd` pour renouveler les certificats avant leur expiration. Vous pouvez tester le processus de renouvellement de manière simulée (`--dry-run`) :

```bash
sudo certbot renew --dry-run
```

Si aucune erreur ne s'affiche, cela signifie que le renouvellement automatique est opérationnel.

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `sudo certbot --nginx -d domaine.fr` | Génère un certificat SSL et configure Nginx. |
| `sudo certbot certificates` | Liste tous les certificats gérés par Certbot sur ce serveur. |
| `sudo certbot renew --dry-run` | Simule le processus de renouvellement de tous les certificats. |
| `sudo certbot delete` | Supprime un certificat spécifique du serveur. |

## Ressources

- [Let's Encrypt - Site Officiel](https://letsencrypt.org/fr/)
- [Documentation Certbot pour Nginx](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
- [Documentation Nginx sur le SSL/TLS](https://nginx.org/en/docs/http/configuring_https_servers.html)
