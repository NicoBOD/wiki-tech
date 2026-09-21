---
title: "Créer des lanceurs GNOME personnalisés avec actions rapides et rechargement à chaud"
date: 2026-09-21
author: Nicolas BODAINE
tags:
  - linux
  - ubuntu
  - gnome
  - xdg
  - desktop
  - docker
  - bash
difficulty: intermédiaire
os: Ubuntu 24.04 / GNOME Desktop
status: publié
---

# Créer des lanceurs GNOME personnalisés avec actions rapides et rechargement à chaud

!!! abstract "Résumé"
    Apprenez à intégrer vos scripts, outils en ligne de commande (CLI), démons d'arrière-plan ou conteneurs Docker directement dans le menu d'applications et le dock de GNOME sous Ubuntu. Ce guide détaille la norme FreeDesktop (fichiers `.desktop`), l'ajout d'actions rapides au clic droit, la gestion stricte de la localisation française (pour éviter le repli forcé en anglais), le rechargement à chaud de GNOME Shell sans déconnexion, ainsi qu'un cas pratique complet avec Docker et Lazydocker.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 LTS (GNOME Desktop / X11 ou Wayland) |
| Dernière mise à jour | 2026-09-21 |

## Contexte

Sous Linux, de nombreux utilitaires essentiels fonctionnent exclusivement en ligne de commande ou en tant que services d'arrière-plan (Docker, Rclone, USBGuard, Tailscale, smartmontools, etc.). Par habitude ou par manque de visibilité, on a tendance à oublier leur présence, ou à trouver fastidieux d'ouvrir un terminal pour taper des commandes récurrentes de diagnostic ou de synchronisation.

Créer une entrée personnalisée dans le menu GNOME permet de :

1. **Rendre visibles les services système** dans la grille d'applications et le champ de recherche de GNOME Shell.
2. **Fournir une interface assistée** (en terminal interactif ou TUI) qui affiche immédiatement l'état du service et les choix possibles.
3. **Exploiter les actions rapides au clic droit** sur l'icône dans le dock (ex. *Statistiques*, *Nettoyage*, *Synchroniser maintenant*).

Cependant, plusieurs pièges techniques surviennent fréquemment : textes qui s'affichent obstinément en anglais, bordures de fenêtres désalignées à cause de caractères UTF-8, outils graphiques/TUI qui refusent de démarrer depuis un conteneur, ou obligation supposée de fermer sa session pour appliquer les changements. Ce tutoriel détaille la méthode robuste pas-à-pas pour éviter chaque écueil.

## Prérequis

- Un environnement de bureau GNOME sous Linux (testé sous Ubuntu 24.04 LTS).
- Un terminal et un éditeur de texte.
- Le paquet d'outils de validation FreeDesktop :

```bash
sudo apt update && sudo apt install desktop-file-utils
```

---

## Procédure

### Étape 1 : Créer le script assistant interactif (`~/.local/bin/`)

Pour les outils sans interface graphique native, la bonne pratique consiste à concevoir un script wrapper en Bash qui s'exécute dans un terminal (`Terminal=true`).

Ce script remplit deux rôles :
1. **Mode interactif** : Afficher un en-tête soigné, un résumé de santé en un coup d'œil, et un menu d'options chiffrées avec mise en pause avant fermeture.
2. **Mode direct (paramètres en ligne de commande)** : Permettre aux actions rapides de bureau (clic droit) d'exécuter directement une tâche spécifique.

Créez le répertoire utilisateur standard s'il n'existe pas :

```bash
mkdir -p ~/.local/bin
```

Créez ensuite votre script, par exemple `~/.local/bin/docker-gestion` :

```bash title="~/.local/bin/docker-gestion" linenums="1"
#!/usr/bin/env bash
set -uo pipefail

# Couleurs ANSI
R=$'\e[0m'; RED=$'\e[31m'; GRN=$'\e[32m'; YEL=$'\e[33m'; CYA=$'\e[36m'; B=$'\e[1m'; DIM=$'\e[2m'

pause_et_quitter() {
    printf '\n%sAppuyez sur Entrée pour quitter...%s ' "$DIM" "$R"
    read -r _ || true
    exit "${1:-0}"
}

# En-tête avec calcul dynamique de largeur pour éviter tout décalage en UTF-8
entete() {
    clear 2>/dev/null || true
    local titre="Docker — Gestion des Conteneurs & Images"
    local largeur=70
    local len_titre=${#titre}
    local padding=$((largeur - 2 - len_titre))
    local espaces=""
    (( padding > 0 )) && printf -v espaces "%*s" "$padding" ""
    local ligne_horiz=""
    printf -v ligne_horiz "%*s" "$largeur" ""
    ligne_horiz="${ligne_horiz// /═}"

    printf '%s╔%s╗%s\n' "$CYA" "$ligne_horiz" "$R"
    printf '%s║%s  %s%s%s%s%s║%s\n' "$CYA" "$R" "$B" "$titre" "$R" "$espaces" "$CYA" "$R"
    printf '%s╚%s╝%s\n' "$CYA" "$ligne_horiz" "$R"
}

afficher_statut() {
    printf '\n%s── ÉTAT DU DÉMON DOCKER ───────────────────────────────────────────%s\n' "$CYA" "$R"
    if systemctl is-active --quiet docker.service || systemctl is-active --quiet docker.socket; then
        local version
        version=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "actif")
        printf '  %s●%s Démon Docker : %sActif%s (version %s)\n' "$GRN" "$R" "$GRN" "$R" "$version"
    else
        printf '  %s○%s Démon Docker : %sInactif%s\n' "$RED" "$R" "$RED" "$R"
        return
    fi

    printf '\n%s── OCCUPATION DES RESSOURCES DISQUE ────────────────────────────────%s\n' "$CYA" "$R"
    docker system df 2>/dev/null | sed 's/^/  /' || true

    printf '\n%s── CONTENEURS EN COURS D'\''EXÉCUTION ────────────────────────────────%s\n' "$CYA" "$R"
    local nb_actifs
    nb_actifs=$(docker ps -q 2>/dev/null | wc -l)
    if (( nb_actifs > 0 )); then
        docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | sed 's/^/  /'
    else
        printf '  %sAucun conteneur actif pour le moment.%s\n' "$DIM" "$R"
    fi
}

action_stats() {
    printf '\n%s>>> Statistiques CPU/RAM en direct (Ctrl+C pour quitter) :%s\n\n' "$B" "$R"
    docker stats || true
}

action_lazydocker() {
    if [[ -x "$HOME/.local/bin/lazydocker" ]]; then
        "$HOME/.local/bin/lazydocker"
    elif command -v lazydocker >/dev/null 2>&1; then
        lazydocker
    else
        printf '\n%sTéléchargement de Lazydocker...%s\n' "$YEL" "$R"
        curl -Lo /tmp/lazydocker.tar.gz "https://github.com/jesseduffield/lazydocker/releases/download/v0.25.2/lazydocker_0.25.2_Linux_x86_64.tar.gz" 2>/dev/null
        tar -xzf /tmp/lazydocker.tar.gz -C "$HOME/.local/bin" lazydocker 2>/dev/null
        rm -f /tmp/lazydocker.tar.gz
        chmod +x "$HOME/.local/bin/lazydocker"
        "$HOME/.local/bin/lazydocker"
    fi
}

action_prune() {
    printf '\n%s>>> Nettoyage des caches et conteneurs arrêtés :%s\n\n' "$B" "$R"
    docker system prune -f
    printf '\n%s✓ Nettoyage terminé.%s\n' "$GRN" "$R"
}

# Détection des arguments en ligne de commande (appelés par les Desktop Actions)
case "${1:-}" in
    --stats)
        entete
        action_stats
        pause_et_quitter 0
        ;;
    --lazydocker)
        action_lazydocker
        exit 0
        ;;
    --prune)
        entete
        action_prune
        pause_et_quitter 0
        ;;
    --status)
        entete
        afficher_statut
        pause_et_quitter 0
        ;;
esac

# Boucle interactive principale
while true; do
    entete
    afficher_statut

    printf '\n%s── ACTIONS DISPONIBLES ─────────────────────────────────────────────%s\n' "$CYA" "$R"
    printf '  %s1)%s Lancer le gestionnaire TUI Lazydocker\n' "$B" "$R"
    printf '  %s2)%s Statistiques en direct CPU / RAM (docker stats)\n' "$B" "$R"
    printf '  %s3)%s Nettoyer les conteneurs et caches inutilisés (docker system prune)\n' "$B" "$R"
    printf '  %s4)%s Rafraîchir l'\''affichage\n' "$B" "$R"
    printf '  %sq)%s Quitter\n' "$B" "$R"

    printf '\n%sVotre choix [1-4, q] :%s ' "$B" "$R"
    read -r choix || exit 0

    case "$choix" in
        1) action_lazydocker ;;
        2) action_stats; printf '\n%sAppuyez sur Entrée pour revenir...%s ' "$DIM" "$R"; read -r _ || true ;;
        3) action_prune; printf '\n%sAppuyez sur Entrée pour revenir...%s ' "$DIM" "$R"; read -r _ || true ;;
        4) continue ;;
        q|Q) exit 0 ;;
        *) printf '\n%sOption invalide.%s\n' "$RED" "$R"; sleep 1 ;;
    esac
done
```

Rendez le script exécutable :

```bash
chmod +x ~/.local/bin/docker-gestion
```

---

### Étape 2 : Créer ou installer une icône vectorielle SVG (`~/.local/share/icons/`)

GNOME utilise le thème d'icônes XDG situé dans `~/.local/share/icons/hicolor/`. Les icônes vectorielles SVG assurent une netteté parfaite, quelle que soit la résolution de votre écran ou le zoom du dock.

1. Créez l'arborescence des icônes vectorielles :

```bash
mkdir -p ~/.local/share/icons/hicolor/scalable/apps
```

2. Déposez votre fichier SVG nommé d'après l'application (ex: `docker.svg`) :

```xml title="~/.local/share/icons/hicolor/scalable/apps/docker.svg"
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
  <defs>
    <linearGradient id="docBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1d63ed"/>
      <stop offset="100%" stop-color="#0b43b3"/>
    </linearGradient>
  </defs>
  <rect width="128" height="128" rx="28" fill="url(#docBg)"/>
  <!-- Conteneurs -->
  <rect x="52" y="36" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <rect x="40" y="46" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <rect x="52" y="46" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <rect x="64" y="46" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <rect x="28" y="56" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <rect x="40" y="56" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <rect x="52" y="56" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <rect x="64" y="56" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <rect x="76" y="56" width="10" height="8" rx="1.5" fill="#ffffff" opacity="0.95"/>
  <!-- Silhouette baleine -->
  <path d="M18 66 C22 66 26 68 28 68 C34 68 38 68 86 68 C98 68 108 76 110 86 C110 87 106 91 96 93 C80 96 46 96 28 86 C21 82 18 74 18 66 Z" fill="#ffffff"/>
  <circle cx="98" cy="80" r="2.5" fill="#0b43b3"/>
  <path d="M18 66 C15 62 10 56 6 56 C7 62 10 68 14 72 Z" fill="#ffffff"/>
</svg>
```

3. Mettez à jour le cache d'icônes utilisateur :

```bash
gtk-update-icon-cache -f ~/.local/share/icons/hicolor/ 2>/dev/null || true
```

---

### Étape 3 : Créer le fichier de bureau FreeDesktop (`.desktop`)

Les fichiers `.desktop` personnels doivent être enregistrés dans `~/.local/share/applications/`.

Créez le fichier `~/.local/share/applications/docker-gestion.desktop` :

```ini title="~/.local/share/applications/docker-gestion.desktop" linenums="1"
[Desktop Entry]
Type=Application
Version=1.0
Name=Docker — Gestion des Conteneurs
Name[fr]=Docker — Gestion des Conteneurs
Name[fr_FR]=Docker — Gestion des Conteneurs
GenericName=Gestionnaire Docker
GenericName[fr]=Gestionnaire Docker
GenericName[fr_FR]=Gestionnaire Docker
Comment=Tableau de bord, statistiques en direct, Lazydocker et nettoyage Docker
Comment[fr]=Tableau de bord, statistiques en direct, Lazydocker et nettoyage Docker
Comment[fr_FR]=Tableau de bord, statistiques en direct, Lazydocker et nettoyage Docker
Exec=/home/user/.local/bin/docker-gestion
Icon=docker
Terminal=true
Categories=Development;
Keywords=docker;conteneur;container;image;lazydocker;volume;compose;stats;
StartupNotify=false
Actions=Lazydocker;Stats;Prune;

[Desktop Action Lazydocker]
Name=Lancer Lazydocker (TUI)
Name[fr]=Lancer Lazydocker (TUI)
Name[fr_FR]=Lancer Lazydocker (TUI)
Exec=/home/user/.local/bin/docker-gestion --lazydocker

[Desktop Action Stats]
Name=Statistiques CPU/RAM (docker stats)
Name[fr]=Statistiques CPU/RAM (docker stats)
Name[fr_FR]=Statistiques CPU/RAM (docker stats)
Exec=/home/user/.local/bin/docker-gestion --stats

[Desktop Action Prune]
Name=Nettoyer les caches et conteneurs arrêtés
Name[fr]=Nettoyer les caches et conteneurs arrêtés
Name[fr_FR]=Nettoyer les caches et conteneurs arrêtés
Exec=/home/user/.local/bin/docker-gestion --prune
```

---

### Étape 4 : Valider et enregistrer l'entrée de bureau

1. **Valider la syntaxe XDG** avec l'utilitaire `desktop-file-validate` :

```bash
desktop-file-validate ~/.local/share/applications/docker-gestion.desktop
```

Si la commande ne renvoie aucun message, le fichier respecte scrupuleusement le standard.

2. **Mettre à jour la base de données des applications** :

```bash
update-desktop-database ~/.local/share/applications/
```

---

## Les pièges courants et comment les éviter

### Piège 1 : L'affichage obstiné en anglais (`LANGUAGE=fr_FR:en`)

!!! failure "Le problème"
    Vous avez rédigé votre fichier `.desktop` avec un `Name=...` en français et un `Name[en]=...` en anglais. Pourtant, sur un Ubuntu configuré en français, GNOME Shell affiche systématiquement le texte anglais !

!!! note "Explication technique"
    Sous Ubuntu, les sessions françaises exportent généralement la variable d'environnement `LANGUAGE=fr_FR:en`. 
    La bibliothèque `GLib` (utilisée par GNOME Shell pour parser les entrées de bureau) résout les langues dans cet ordre précis :
    
    1. Correspondance exacte : `Name[fr_FR]`
    2. Correspondance générique de langue : `Name[fr]`
    3. Langue suivante dans la variable `LANGUAGE` : **`Name[en]`**
    4. En tout dernier recours : la valeur par défaut sans crochet `Name=`

    Si votre fichier ne contient pas de balise explicite `[fr]` ou `[fr_FR]`, GLib saute la valeur par défaut et prend la clé `[en]` car `en` fait partie de votre chaîne de repli linguistique !

!!! success "La solution"
    1. Définissez la clé par défaut directement en français : `Name=Mon Titre`
    2. Ajoutez explicitement les deux variantes : `Name[fr]=Mon Titre` et `Name[fr_FR]=Mon Titre`
    3. **Supprimez totalement les clés `[en]`** de vos fichiers de bureau personnalisés.

---

### Piège 2 : Recharger GNOME Shell sans fermer la session (X11 vs Wayland)

Après avoir modifié un fichier `.desktop`, GNOME Shell conserve en mémoire vive les anciennes chaînes dans son cache d'objets `Shell.AppSystem`.

!!! question "Faut-il fermer sa session ?"
    **Non !** Si vous utilisez une session **X11** (`echo $XDG_SESSION_TYPE`), GNOME dispose d'un mécanisme de rechargement à chaud conçu précisément pour cela :

1. Pressez la combinaison de touches ++alt+f2++.
2. Tapez simplement la lettre `r` (pour *restart*).
3. Appuyez sur ++enter++.

```bash
# Vérifier votre type de session
echo $XDG_SESSION_TYPE
```

| Type de session | Méthode de rechargement sans perte de travail |
| :--- | :--- |
| **X11** | ++alt+f2++, taper `r`, puis ++enter++. Le gestionnaire de fenêtres se réexécute en 500 ms, toutes vos fenêtres et documents restent ouverts. |
| **Wayland** | Le protocole Wayland ne permet pas de redémarrer le compositeur sans tuer les clients XWayland/Wayland. La réactualisation s'opère soit en attendant que le moniteur d'évènements `GAppInfoMonitor` détecte la modification de date (via `touch ~/.local/share/applications/`), soit en verrouillant/déverrouillant l'écran (++super+l++). |

---

### Piège 3 : Décalage des bordures de cadre en UTF-8 dans le terminal

!!! failure "Le problème"
    Lorsqu'on dessine un cadre en caractères Unicode (`╔══╗`, `║  ║`), la bordure droite `║` est décalée d'un ou deux caractères si le titre contient des caractères accentués (`é`, `è`), des tirets cadratins (`—`) ou des perluètes (`&`).

!!! note "Explication technique"
    En UTF-8, un caractère comme le tiret cadratin `—` (U+2014) mesure **3 octets** en mémoire, mais n'occupe qu'**1 seule colonne visuelle** dans un terminal à chasse fixe (monospace).
    Si un script compte les octets ou si le nombre d'espaces de remplissage est codé en dur dans un éditeur de texte, l'affichage console est faussé.

!!! success "La solution"
    En Bash moderne, l'expansion `${#variable}` renvoie le nombre réel de **caractères Unicode** (et non pas le nombre d'octets). En calculant dynamiquement le padding d'espaces :

```bash
local titre="Docker — Gestion des Conteneurs & Images"
local largeur=70
local len_titre=${#titre}
local padding=$((largeur - 2 - len_titre))
local espaces=""
(( padding > 0 )) && printf -v espaces "%*s" "$padding" ""
```

Le cadre s'ajuste alors au pixel près quelle que soit la longueur ou la teneur linguistique du titre.

---

### Piège 4 : Les outils TUI en conteneur Docker et l'erreur `/dev/tty`

!!! failure "Le problème"
    Lancer une interface en mode texte avancée (comme Lazydocker) via un conteneur éphémère `docker run -it lazyteam/lazydocker` depuis un lanceur `.desktop` échoue silencieusement ou retourne l'erreur :
    
    `*fs.PathError open /dev/tty: no such device or address`

!!! note "Explication technique"
    Les applications TUI conçues avec des bibliothèques comme `tview` ou `bubbletea` en Go requièrent un descripteur de fichier TTY direct pour capturer les flux clavier et souris. À l'intérieur d'un conteneur headless ou isolé, `/dev/tty` n'est pas routé correctement sans monter le pseudo-terminal hôte.

!!! success "La solution"
    Téléchargez directement le binaire compilé natif pour Linux dans `~/.local/bin/` :
    
    ```bash
    curl -Lo /tmp/lazydocker.tar.gz "https://github.com/jesseduffield/lazydocker/releases/download/v0.25.2/lazydocker_0.25.2_Linux_x86_64.tar.gz"
    tar -xzf /tmp/lazydocker.tar.gz -C ~/.local/bin/ lazydocker
    chmod +x ~/.local/bin/lazydocker
    ```
    
    Le binaire s'exécute nativement en quelques millisecondes et communique avec le démon local via le socket standard `/var/run/docker.sock`.

---

## Aide-mémoire

| Composant | Emplacement standard utilisateur |
| :--- | :--- |
| **Scripts exécutables** | `~/.local/bin/<nom-du-script>` |
| **Fichiers de bureau (.desktop)** | `~/.local/share/applications/<nom>.desktop` |
| **Icônes vectorielles (SVG)** | `~/.local/share/icons/hicolor/scalable/apps/<nom>.svg` |
| **Validation du lanceur** | `desktop-file-validate ~/.local/share/applications/<nom>.desktop` |
| **Reconstruction du cache menu** | `update-desktop-database ~/.local/share/applications/` |
| **Test de lancement en CLI** | `gtk-launch <nom>.desktop` |
| **Rechargement GNOME à chaud (X11)** | ++alt+f2++, taper `r`, puis ++enter++ |

---

## Glossaire

FreeDesktop / XDG (Cross-Desktop Group)
:   Ensemble de spécifications et standards ouverts garantissant l'interopérabilité entre les différents environnements de bureau Linux (GNOME, KDE Plasma, XFCE). Définit l'arborescence des dossiers (`XDG_DATA_HOME`, `~/.local/share/applications/`) et la structure des fichiers `.desktop`.

Desktop Entry (`.desktop`)
:   Fichier de configuration au format INI décrivant une application : son nom, sa commande d'exécution, son icône, ses catégories de tri et ses actions contextuelles de menu.

TUI (Terminal User Interface)
:   Interface utilisateur en mode texte s'exécutant dans une console (comme `htop`, `lazydocker`, `ncdu`), offrant une navigation interactive à la souris et au clavier via des bibliothèques telles que ncurses.

Desktop Actions
:   Fonctionnalité de la norme FreeDesktop permettant de déclarer des actions secondaires associées à une application, accessibles via le menu contextuel (clic droit sur l'icône dans le dock GNOME ou le gestionnaire de tâches).

TTY (Teletypewriter)
:   Périphérique sous Linux représentant un terminal d'entrée/sortie texte physique ou émulé (pseudo-terminal `pty`), indispensable pour faire tourner des programmes interactifs.

---

## Vérification

1. **Vérifier la bonne résolution linguistique avec Python et GLib** :

```bash
python3 -c "
import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio

app = Gio.DesktopAppInfo.new('docker-gestion.desktop')
if app:
    print('Nom :', app.get_display_name())
    print('Description :', app.get_description())
else:
    print('Fichier introuvable')
"
```

!!! success "Résultat attendu"
    ```text
    Nom : Docker — Gestion des Conteneurs
    Description : Tableau de bord, statistiques en direct, Lazydocker et nettoyage Docker
    ```

2. **Tester le lancement effectif dans l'environnement graphique** :

```bash
gtk-launch docker-gestion.desktop
```

Une fenêtre de terminal s'ouvre avec l'interface interactive de Docker, ses couleurs, son statut de démon et son menu d'options.

---

## Ressources

- [Spécification officielle FreeDesktop Desktop Entry](https://specifications.freedesktop.org/desktop-entry/latest/) — Standards officiels pour la structure des fichiers `.desktop`.
- [Documentation GNOME Developer — Desktop Files](https://developer.gnome.org/documentation/guidelines/maintainer/integrating.html) — Recommandations d'intégration logicielle dans l'écosystème GNOME.
- [Dépôt officiel Lazydocker](https://github.com/jesseduffield/lazydocker) — Gestionnaire TUI libre pour conteneurs et services Docker.
