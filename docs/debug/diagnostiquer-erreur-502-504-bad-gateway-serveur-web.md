---
title: Diagnostiquer une erreur 502/504 Bad Gateway sur un serveur web
date: 2026-06-23
author: Nicolas BODAINE
tags:
  - web
  - nginx
  - reseau
  - apache
  - debug
difficulty: débutant
os: Linux
status: publié
---

# Diagnostiquer une erreur 502/504 Bad Gateway sur un serveur web

!!! abstract "Résumé"
    Comprendre et résoudre les erreurs HTTP 502 (Bad Gateway) et 504 (Gateway Timeout), très fréquentes lors de l'utilisation de proxys inverses comme Nginx ou HAProxy.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux, Nginx, Apache, Proxy |
| Dernière mise à jour | 2026-06-23 |

## Contexte

Lorsque vous hébergez des applications web, vous utilisez souvent un serveur "frontal" (reverse proxy) comme Nginx ou HAProxy qui redirige le trafic vers une application en arrière-plan (Node.js, PHP-FPM, Gunicorn, Tomcat, etc.). 

Si le lien entre le frontal et l'application casse, vous obtenez généralement l'une de ces deux erreurs :
- **502 Bad Gateway** : Le proxy a pu contacter l'application, mais il a reçu une réponse invalide ou inattendue, ou bien la connexion a été refusée (service éteint).
- **504 Gateway Timeout** : Le proxy a contacté l'application, mais n'a pas reçu de réponse dans le temps imparti (l'application est bloquée ou surchargée).

## Problème

L'utilisateur se connecte au site web et voit s'afficher une page d'erreur blanche de son navigateur ou une page générée par Nginx mentionnant "502 Bad Gateway" ou "504 Gateway Timeout".

!!! failure "Message d'erreur Nginx"
    ```text
    502 Bad Gateway
    nginx/1.18.0 (Ubuntu)
    ```

## Procédure de Diagnostic

### Étape 1 : Vérifier le statut du service backend

Dans 90% des cas d'une erreur 502, le service backend (PHP-FPM, Node, Python, etc.) est tout simplement arrêté, a crashé, ou est en redémarrage en boucle.

Vérifiez le statut du service sous-jacent. Par exemple pour `php8.1-fpm` :

```bash
sudo systemctl status php8.1-fpm
```

Si le service est en erreur, relancez-le :

```bash
sudo systemctl restart php8.1-fpm
```

### Étape 2 : Analyser les journaux du proxy (Nginx/Apache)

Si le service semble actif, le serveur proxy détient la réponse exacte dans ses logs d'erreur. Pour Nginx, les logs sont généralement dans `/var/log/nginx/error.log`.

```bash
sudo tail -n 20 /var/log/nginx/error.log
```

!!! success "Exemple de log révélateur (Connexion refusée)"
    ```text
    connect() failed (111: Connection refused) while connecting to upstream
    ```
    *Signification : Nginx tente de contacter l'application sur un port, mais personne ne l'écoute. Le backend est éteint ou écoute sur un autre port.*

### Étape 3 : Vérifier les ports en écoute

Le proxy est configuré pour joindre le backend sur une certaine adresse (ex: `127.0.0.1:8080` ou un socket UNIX `/var/run/php.sock`). 

Vérifiez si l'application écoute bien là où le proxy la cherche :

```bash
sudo ss -tulpn | grep 8080
```
*(Si rien ne s'affiche, c'est que l'application ne s'est pas lancée correctement sur ce port).*

### Étape 4 : Diagnostiquer les lenteurs (Erreur 504)

Si le problème est une **504 Gateway Timeout**, le backend est vivant mais trop lent. Cela peut être causé par :
- Une base de données surchargée (requête très longue).
- Un appel à une API externe distante qui ne répond pas.
- Une boucle infinie dans le code de l'application.

Regardez cette fois-ci les logs de votre application ou de la base de données. Vous pouvez également augmenter temporairement le timeout côté Nginx dans votre configuration si c'est un traitement normal long :

```nginx
# Dans le bloc location
proxy_read_timeout 300;
proxy_connect_timeout 300;
proxy_send_timeout 300;
```

N'oubliez pas de recharger Nginx après modification :
```bash
sudo systemctl reload nginx
```

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `systemctl status <service>` | Vérifier si l'application backend tourne |
| `tail -f /var/log/nginx/error.log` | Suivre en direct les erreurs du reverse proxy |
| `ss -tulpn` | Lister les ports d'écoute locaux et les applications associées |
| `journalctl -u <service> -e` | Voir les derniers logs d'erreur du service backend |

## Vérification

Pour vérifier qu'une erreur 502/504 est résolue :
1. Lancez une requête vers votre serveur en utilisant `curl` :
```bash
curl -I https://votresite.com
```

!!! success "Résultat attendu"
    Vous devez voir un code de statut HTTP `200 OK` (ou `301/302` pour une redirection) et non plus `502` ou `504`.
    ```text
    HTTP/2 200 
    server: nginx
    content-type: text/html; charset=UTF-8
    ```

## Ressources

- [Documentation Nginx - Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) — Guide officiel sur le reverse proxy Nginx.
- [MDN Web Docs - 502 Bad Gateway](https://developer.mozilla.org/fr/docs/Web/HTTP/Status/502) — Explication de la spécification HTTP.
- [MDN Web Docs - 504 Gateway Timeout](https://developer.mozilla.org/fr/docs/Web/HTTP/Status/504) — Explication de la spécification HTTP.
