---
title: Installer une interface graphique légère (LXQt ou XFCE) sur Debian 13
date: 2026-08-27
author: Nicolas BODAINE
tags:
  - debian
  - bureau
  - lxqt
  - xfce
  - lightdm
  - xorg
difficulty: débutant
os: Debian 13 (Trixie)
status: publié
---

# Installer une interface graphique légère (LXQt ou XFCE) sur Debian 13

!!! abstract "Résumé"
    Une Debian 13 (Trixie) installée en mode serveur n'embarque aucun environnement graphique. Cette note explique comment en ajouter un **sans réinstaller la machine** : serveur d'affichage Xorg, gestionnaire de connexion LightDM, puis un bureau léger — LXQt (le plus sobre en RAM) ou XFCE (le meilleur compromis légèreté / ergonomie).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Debian 13 (Trixie) |
| Dernière mise à jour | 2026-08-27 |

## Contexte

Lors d'une installation Debian 13 sans sélection de tâche « Environnement de bureau », tout se passe en ligne de commande. C'est le comportement idéal pour un serveur, mais cela devient bloquant dès qu'un outil n'existe qu'en version graphique : navigateur web, console de gestion, IDE, logiciel métier, ou simplement pour transformer la machine en poste de travail utilisable localement.

Inutile de repartir de zéro : il suffit d'ajouter les trois briques manquantes.

1. **Le serveur d'affichage** (Xorg) — il pilote la carte graphique, l'écran, le clavier et la souris, et dessine les fenêtres.
2. **Le gestionnaire de connexion** (*display manager*, ici LightDM) — il affiche l'écran de login graphique et démarre la session de l'utilisateur.
3. **L'environnement de bureau** — les panneaux, le menu, le gestionnaire de fichiers, le terminal, etc.

Sur une machine aux ressources limitées (VM de lab, vieux PC, VPS), GNOME et KDE Plasma sont à éviter : ils sont confortables mais consomment beaucoup de RAM et de CPU. Deux bureaux légers se démarquent :

| Environnement | Empreinte mémoire au repos | Pour quel usage ? |
|---------------|----------------------------|-------------------|
| **LXQt** | La plus faible (de l'ordre de 300 Mo) | Machines très modestes, VM avec peu de RAM, besoin ponctuel d'une interface |
| **XFCE** | Faible, un peu supérieure à LXQt | Poste de travail au quotidien : plus complet, plus ergonomique et très stable |

!!! tip "Lequel choisir ?"
    En cas de doute, partez sur **XFCE** : la différence de consommation est marginale sur une machine disposant de 2 Go de RAM ou plus, et l'expérience utilisateur est nettement plus aboutie. Réservez **LXQt** aux configurations réellement contraintes.

## Prérequis

- Une **Debian 13 (Trixie)** installée sans environnement de bureau.
- Un accès `root` ou un compte disposant des droits `sudo`.
- Un **compte utilisateur non-root** pour ouvrir la session graphique : LightDM refuse par défaut la connexion en `root`.
- Un accès à la **console locale** de la machine (écran et clavier physiques, console Proxmox / vSphere / virt-manager…) : la session graphique s'affiche sur l'écran de la machine, pas dans le terminal SSH.
- Un accès réseau aux dépôts Debian et environ 1 Go d'espace disque libre.

!!! warning "Un redémarrage est nécessaire"
    La dernière étape redémarre la machine. Sur un serveur en production, planifiez l'opération et prévenez les utilisateurs des services hébergés.

## Procédure

### Étape 1 : Mettre à jour le système

C'est le prérequis indispensable avant d'installer de nouveaux paquets : rafraîchir le catalogue des dépôts et appliquer les mises à jour en attente évite les conflits de dépendances et garantit de récupérer les dernières versions des paquets graphiques.

Connectez-vous en `root` ou utilisez `sudo` :

```bash
sudo apt update && sudo apt upgrade -y
```

!!! note "Pas de `sudo` sur une Debian minimale ?"
    `sudo` n'est pas toujours installé sur une Debian minimale. Dans ce cas, passez d'abord en administrateur avec `su -`, puis exécutez les commandes de cette note **sans** le préfixe `sudo`.

### Étape 2 : Installer le serveur d'affichage et le gestionnaire de connexion

On installe le serveur Xorg minimal ainsi que LightDM :

```bash
sudo apt install --no-install-recommends xserver-xorg xinit lightdm -y
```

L'option `--no-install-recommends` évite d'installer les paquets recommandés (mais non indispensables) et garde le système au plus léger. C'est elle qui fait toute la différence entre une installation graphique sobre et plusieurs centaines de Mo de dépendances superflues.

!!! info "Le rôle de chaque paquet"
    - `xserver-xorg` : le serveur d'affichage X11 et les pilotes vidéo / entrée associés.
    - `xinit` : les utilitaires de démarrage d'une session X (dont `startx`), pratiques pour tester l'affichage sans passer par le gestionnaire de connexion.
    - `lightdm` : le gestionnaire de connexion, volontairement plus léger que GDM (GNOME) ou SDDM (KDE Plasma).

### Étape 3 : Installer l'environnement de bureau choisi

Choisissez **une seule** des deux options selon vos besoins.

=== "Option A — LXQt (le plus minimaliste)"

    ```bash
    sudo apt install --no-install-recommends lxqt-core lxqt-session pcmanfm-qt qterminal -y
    ```

    Cette combinaison installe le socle LXQt (`lxqt-core`), la gestion de session (`lxqt-session`), le gestionnaire de fichiers `pcmanfm-qt` et le terminal `qterminal`. C'est le strict nécessaire pour un bureau fonctionnel.

=== "Option B — XFCE (le compromis idéal)"

    ```bash
    sudo apt install --no-install-recommends xfce4 xfce4-terminal thunar -y
    ```

    Le métapaquet `xfce4` apporte le bureau, le panneau et le gestionnaire de fenêtres, complétés ici par le terminal `xfce4-terminal` et le gestionnaire de fichiers `thunar`.

!!! tip "Compléter l'installation à la carte"
    Avec `--no-install-recommends`, certains utilitaires de confort ne sont pas installés (applet réseau, gestionnaire d'archives, visionneuse d'images ou de PDF, polices supplémentaires). Ajoutez-les ensuite à la demande, un par un, plutôt que de tout tirer d'un coup — par exemple `sudo apt install network-manager-gnome` pour disposer de l'icône de gestion du Wi-Fi et des connexions réseau dans le panneau.

### Étape 4 : Activer le démarrage graphique et redémarrer

Il reste à indiquer à systemd de démarrer sur la cible graphique, à activer LightDM au boot, puis à redémarrer :

```bash
sudo systemctl set-default graphical.target
sudo systemctl enable lightdm
sudo reboot
```

- `set-default graphical.target` remplace la cible de démarrage par défaut (`multi-user.target`, le mode console) par la cible graphique.
- `enable lightdm` fait démarrer automatiquement le gestionnaire de connexion à chaque boot.

Au redémarrage, l'écran de connexion LightDM s'affiche directement : saisissez les identifiants de votre compte utilisateur pour ouvrir la session graphique.

## Vérification

Depuis un terminal (console locale ou SSH), contrôlez que la configuration est bien en place :

```bash
systemctl get-default
systemctl status lightdm
```

!!! success "Résultat attendu"
    ```text
    graphical.target

    ● lightdm.service - Light Display Manager
         Loaded: loaded (/usr/lib/systemd/system/lightdm.service; enabled; preset: enabled)
         Active: active (running) since ...
    ```

Les deux marqueurs à retrouver sont `enabled` (LightDM démarre bien au boot) et `active (running)` (l'écran de connexion tourne actuellement).

Une fois la session ouverte, mesurez la consommation réelle du bureau :

```bash
free -h
```

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `systemctl get-default` | Afficher la cible de démarrage actuelle (`graphical.target` ou `multi-user.target`). |
| `sudo systemctl set-default multi-user.target` | Revenir à un démarrage en mode console, sans interface graphique. |
| `sudo systemctl stop lightdm` | Fermer la session graphique sans redémarrer la machine. |
| `sudo systemctl restart lightdm` | Relancer l'écran de connexion, par exemple après un changement de configuration. |
| `sudo dpkg-reconfigure lightdm` | Choisir le gestionnaire de connexion par défaut lorsque plusieurs sont installés. |
| `free -h` | Contrôler la mémoire réellement consommée par le bureau. |

## Ressources

- [Debian Wiki — Xorg](https://wiki.debian.org/Xorg) — Fonctionnement et configuration du serveur d'affichage sous Debian.
- [Debian Wiki — LightDM](https://wiki.debian.org/LightDM) — Options de configuration du gestionnaire de connexion.
- [Debian Wiki — LXQt](https://wiki.debian.org/LXQt) — Paquets et particularités de LXQt sous Debian.
- [Debian Wiki — Xfce](https://wiki.debian.org/Xfce) — Paquets et particularités de XFCE sous Debian.
- [Notes de publication de Debian 13 (Trixie)](https://www.debian.org/releases/trixie/releasenotes) — Changements et points de vigilance de la version.
- [Manuel de `systemctl`](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) — Référence des cibles systemd et de la commande `set-default`.
