---
title: Mettre en place un Reverse Proxy (Proxy Inverse) avec Nginx
date: 2026-06-03
author: Nicolas BODAINE
tags:
  - nginx
  - web
  - proxy
  - ubuntu
  - reseaux
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# Mettre en place un Reverse Proxy (Proxy Inverse) avec Nginx

!!! abstract "Résumé"
    Ce tutoriel explique comment installer et configurer un proxy inverse (reverse proxy) basique avec Nginx sur Ubuntu Server. Vous apprendrez à rediriger le trafic web arrivant sur votre serveur vers une application interne écoutant sur un autre port (ex: une application Node.js ou un conteneur Docker).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 LTS |
| Dernière mise à jour | 2026-06-03 |

## Contexte

Lorsque vous hébergez plusieurs applications sur un même serveur (par exemple des conteneurs Docker ou des applications Node.js, Python), elles écoutent souvent sur des ports différents (ex: `8080`, `3000`, `5000`). 
Pour qu'un utilisateur puisse y accéder simplement avec un nom de domaine (comme `app.mon-domaine.com`) sans avoir à préciser le port dans l'URL, on utilise un **Proxy Inverse**. 

**Nginx** va écouter les requêtes sur les ports standards (80 pour HTTP, 443 pour HTTPS) et rediriger (faire office de "proxy") le trafic vers le bon service en arrière-plan en fonction du nom de domaine demandé.

## Prérequis

- Un serveur Ubuntu 24.04 à jour avec accès à Internet.
- Un utilisateur avec les droits `sudo` ou l'accès `root`.
- Au moins un nom de domaine ou sous-domaine pointant vers l'IP de votre serveur (utile pour les tests réels, sinon nous modifierons le fichier `/etc/hosts` de votre machine client pour simuler un domaine).
- Une application qui écoute sur un port local (nous créerons un faux service sur le port `8080` avec Python pour le TP).

## Procédure

### Étape 1 : Mettre en place un faux service en arrière-plan (pour le TP)

Si vous avez déjà un conteneur ou une application (ex: qui tourne sur le port `8080`), passez à l'étape suivante. Sinon, nous allons créer un petit service HTTP de test.

1. Créez un dossier et une page de test :

```bash
mkdir -p ~/test-app
echo "<h1>Bonjour depuis l'application interne sur le port 8080 !</h1>" > ~/test-app/index.html
cd ~/test-app
```

2. Lancez un serveur web basique en Python sur le port `8080`, en tâche de fond :

```bash
python3 -m http.server 8080 &
```

Vous pouvez vérifier que l'application tourne localement depuis votre serveur :

```bash
curl http://localhost:8080
```

### Étape 2 : Installer Nginx

Installez le paquet Nginx depuis les dépôts officiels Ubuntu :

```bash
sudo apt update
sudo apt install -y nginx
```

Vérifiez que le service Nginx est bien démarré :

```bash
sudo systemctl status nginx
```

Par défaut, Nginx sert maintenant une page d'accueil sur le port 80. Si vous tapez l'adresse IP du serveur dans un navigateur distant, vous verrez la page de bienvenue "Welcome to nginx!".

### Étape 3 : Créer la configuration du Reverse Proxy

Dans Nginx, la configuration des différents sites web (Virtual Hosts ou Server Blocks) se fait dans le répertoire `/etc/nginx/sites-available/`.

1. Créez un nouveau fichier de configuration pour votre application :

```bash
sudo nano /etc/nginx/sites-available/mon-app
```

2. Collez la configuration suivante (adaptez `server_name` avec votre nom de domaine, ou l'IP si vous n'avez pas de domaine) :

```nginx
server {
    listen 80;
    server_name mon-app.local; # Remplacez par votre domaine, ex: app.mondomaine.fr

    location / {
        # L'adresse locale et le port de votre application
        proxy_pass http://127.0.0.1:8080;
        
        # Transmission des en-têtes d'origine (très important pour les logs et le bon fonctionnement des apps)
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. Sauvegardez et quittez (`Ctrl+O`, `Entrée`, `Ctrl+X`).

### Étape 4 : Activer le site et tester la configuration

1. Pour activer ce site, créez un lien symbolique vers le dossier `sites-enabled/` :

```bash
sudo ln -s /etc/nginx/sites-available/mon-app /etc/nginx/sites-enabled/
```

2. Testez la syntaxe de votre configuration Nginx pour éviter de casser le serveur :

```bash
sudo nginx -t
```

!!! success "Résultat attendu"
    ```text
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    ```

3. Si le test est réussi, rechargez Nginx pour appliquer les changements en douceur :

```bash
sudo systemctl reload nginx
```

## Vérification

1. Si vous avez utilisé un vrai nom de domaine, accédez à `http://votre-domaine.fr` dans un navigateur.
2. Si vous avez utilisé `mon-app.local` (comme dans le TP), vous devez dire à votre propre ordinateur client (celui depuis lequel vous travaillez) comment trouver ce domaine. 
   - Sous **Windows**, modifiez le fichier `C:\Windows\System32\drivers\etc\hosts` (en tant qu'administrateur avec le Bloc-notes).
   - Sous **Linux / macOS**, modifiez `/etc/hosts` en root.
   - Ajoutez la ligne : `<VOTRE_IP_SERVEUR> mon-app.local`

En naviguant sur `http://mon-app.local`, vous ne devriez plus voir la page d'accueil Nginx par défaut, mais bien :
`Bonjour depuis l'application interne sur le port 8080 !`

## Aide-mémoire

| Commande | Action |
|----------|--------|
| `sudo nginx -t` | Tester la configuration Nginx (à faire systématiquement avant un reload). |
| `sudo systemctl reload nginx` | Appliquer une nouvelle configuration sans couper les connexions en cours. |
| `tail -f /var/log/nginx/error.log` | Lire les logs d'erreurs en direct (très utile pour le débogage d'une mauvaise configuration). |

## Ressources

- [Documentation officielle Nginx : NGINX Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) — Le guide de référence éditeur (en anglais).
- [Ubuntu Server Guide : Web Servers - Nginx](https://ubuntu.com/server/docs/how-to/web-services/install-nginx/) — Manuel Ubuntu sur Nginx.
