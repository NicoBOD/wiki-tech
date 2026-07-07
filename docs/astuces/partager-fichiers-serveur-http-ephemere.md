---
title: Partager des fichiers rapidement en local avec un serveur HTTP éphémère
date: 2026-06-29
author: Nicolas BODAINE
tags:
  - réseau
  - transfert
  - python
  - php
  - astuce
difficulty: débutant
os: Linux | Windows | macOS
status: publié
---

# Partager des fichiers rapidement en local avec un serveur HTTP éphémère

!!! abstract "Résumé"
    Comment transformer n'importe quel dossier de votre machine en serveur de fichiers web instantané pour transférer des données rapidement sur votre réseau local.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Multiplateforme |
| Dernière mise à jour | 2026-06-29 |

## Contexte

Vous avez besoin d'envoyer un fichier volumineux d'un PC vers une machine virtuelle, de transférer un document vers un smartphone, ou de mettre à disposition un répertoire temporaire pour un collègue sur le même réseau local. 

Installer et configurer un serveur web complet (Apache, Nginx), un partage réseau (Samba/SMB) ou un serveur FTP serait disproportionné et chronophage pour un besoin ponctuel. Heureusement, la plupart des langages de programmation déjà installés sur votre machine (notamment sur Linux et macOS) intègrent des serveurs HTTP ultra-légers que l'on peut lancer en une seule commande.

## Procédure : Les différentes méthodes

Placez-vous toujours d'abord dans le répertoire que vous souhaitez partager (tous les sous-dossiers et fichiers de ce répertoire seront accessibles publiquement sur le réseau).

```bash
cd /chemin/vers/dossier/a/partager
```

### Méthode 1 : Avec Python (La plus universelle)

Python est installé par défaut sur presque toutes les distributions Linux et sur macOS. C'est la méthode la plus couramment utilisée.

=== "Python 3"

    ```bash
    python3 -m http.server 8000
    ```

    *Par défaut, le serveur écoute sur le port 8000. Vous pouvez changer ce numéro en le remplaçant à la fin de la commande.*

=== "Python 2 (Anciens systèmes)"

    ```bash
    python -m SimpleHTTPServer 8000
    ```

### Méthode 2 : Avec PHP

Si vous êtes développeur web, PHP est probablement installé sur votre machine. Son serveur de développement natif fait parfaitement l'affaire.

```bash
php -S 0.0.0.0:8000
```

!!! note "Écoute globale"
    Le `0.0.0.0` indique à PHP d'écouter sur toutes les interfaces réseau (pas seulement `localhost`), ce qui est nécessaire pour y accéder depuis une autre machine.

### Méthode 3 : Avec Node.js

Si vous utilisez Node.js, vous pouvez utiliser l'exécutable `npx` pour télécharger et lancer un serveur web à la volée.

=== "http-server"

    ```bash
    npx http-server -p 8000
    ```

=== "serve"

    ```bash
    npx serve -l 8000
    ```

### Méthode 4 : Avec Ruby

Moins connu, le langage Ruby propose également un serveur basique en une commande.

```bash
ruby -run -e httpd . -p 8000
```

## Vérification et utilisation

Une fois le serveur lancé, il affiche une sortie indiquant qu'il est en cours d'exécution. Laissez ce terminal ouvert.

1. **Trouvez l'adresse IP** de la machine qui héberge le serveur (utilisez `ip a` sous Linux/macOS ou `ipconfig` sous Windows).
2. Depuis la machine cible (celle qui doit télécharger le fichier), ouvrez un navigateur web.
3. Tapez l'URL `http://<IP_DU_SERVEUR>:8000` (ex: `http://192.168.1.50:8000`).

Vous verrez apparaître la liste des fichiers contenus dans votre dossier. Cliquez simplement sur un fichier pour le télécharger.

!!! success "Résultat attendu"
    Dans le terminal de la machine serveur, vous verrez les requêtes de téléchargement défiler sous forme de logs (GET /mon-fichier.zip 200).

Pour arrêter le serveur une fois le transfert terminé, retournez dans le terminal et appuyez sur ++ctrl+c++.

!!! warning "Sécurité"
    Ces serveurs n'ont **aucune authentification** ni chiffrement (pas de HTTPS). Tout appareil connecté à votre réseau local peut naviguer dans le dossier partagé et télécharger vos fichiers. **Ne les utilisez jamais sur un réseau Wi-Fi public** (café, aéroport) et pensez bien à les couper dès que vous avez terminé.

## Ressources

- [Documentation officielle Python (module http.server)](https://docs.python.org/3/library/http.server.html)
- [Documentation officielle PHP (Built-in web server)](https://www.php.net/manual/fr/features.commandline.webserver.php)
