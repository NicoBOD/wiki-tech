---
title: Analyser le trafic réseau avec Wireshark
date: 2026-06-12
author: Nicolas BODAINE
tags:
  - wireshark
  - reseau
  - sniffing
  - tcpdump
difficulty: intermédiaire
os: Ubuntu 24.04 / Windows
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Analyser le trafic réseau avec Wireshark : Capturer et filtrer les paquets

!!! abstract "Résumé"
    Wireshark est l'outil de référence mondial pour analyser les trames réseaux. Ce tutoriel couvre les bases de la capture et l'utilisation de filtres pour isoler le trafic pertinent.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Multi-plateformes (Ubuntu, Windows) |
| Dernière mise à jour | 2026-06-12 |

## Contexte

Lorsque vous rencontrez des problèmes de communication entre deux machines, les commandes de base (ping, traceroute) ne suffisent parfois pas. Pour comprendre exactement pourquoi une connexion échoue ou pour auditer ce qui transite en clair, il faut "sniffer" le trafic (capturer les paquets). Wireshark est l'outil incontournable avec interface graphique pour cette tâche, offrant de puissants filtres d'affichage.

## Prérequis

- Une machine de test connectée au réseau (Ubuntu ou Windows).
- Les privilèges administrateur (`root` ou administrateur) pour autoriser la capture sur les interfaces.

## Procédure

### Étape 1 : Installation de Wireshark

=== "Ubuntu (Debian-based)"

    L'installation sous Linux nécessite une attention particulière pour ne pas devoir lancer l'interface graphique en `root` (ce qui est une mauvaise pratique de sécurité).
    ```bash
    sudo apt update
    sudo apt install wireshark -y
    ```
    Lors de l'installation, un écran vous demandera si les non-superutilisateurs doivent pouvoir capturer des paquets. Répondez **Oui**.
    Ajoutez ensuite votre utilisateur au groupe `wireshark` :
    ```bash
    sudo usermod -aG wireshark $USER
    ```
    *Note : Vous devrez vous déconnecter puis vous reconnecter pour que ce changement prenne effet.*

=== "Windows"

    Téléchargez l'installateur depuis le site officiel :
    1. Rendez-vous sur [wireshark.org](https://www.wireshark.org/download.html).
    2. Téléchargez et lancez le *Windows Installer*.
    3. Cochez bien l'installation de **Npcap** lorsqu'elle est proposée (c'est le pilote de capture pour Windows).

### Étape 2 : Lancer la première capture

1. Ouvrez Wireshark.
2. Sur l'écran d'accueil, la liste des interfaces réseau s'affiche avec un mini-graphique d'activité.
3. Repérez l'interface active (par exemple `eth0` ou `Wi-Fi`) et double-cliquez dessus.
4. La capture démarre immédiatement : des lignes colorées commencent à défiler. Chaque ligne représente un paquet réseau.
5. Pour arrêter la capture, cliquez sur le bouton carré rouge (Stop) en haut à gauche.

### Étape 3 : Filtres de capture vs Filtres d'affichage

Il existe deux moments pour filtrer :

- **Filtre de capture (Capture filter)** : Avant de démarrer. Limite la taille de la capture. Utilise la syntaxe BPF (Berkeley Packet Filter).
- **Filtre d'affichage (Display filter)** : Pendant ou après. N'efface pas les données, les masque juste de l'écran. C'est la méthode recommandée pour débuter.

### Étape 4 : Utiliser les filtres d'affichage (Display Filters)

La barre verte en haut est la barre de filtre. Entrez votre filtre et appuyez sur ++enter++.

**Filtres fréquents et utiles :**

- **Filtrer par IP :**
    - `ip.addr == 192.168.1.50` (Trafic depuis ou vers cette IP)
    - `ip.src == 192.168.1.50` (Seulement le trafic émis par cette IP)
- **Filtrer par port / protocole :**
    - `tcp.port == 80` (Trafic web non chiffré)
    - `udp.port == 53` (Requêtes DNS)
- **Filtrer par protocole :**
    - Tapez simplement `http`, `dns`, `icmp`, ou `ssh`.
- **Combiner des filtres :**
    - `ip.addr == 192.168.1.50 and tcp.port == 443` (Trafic HTTPS impliquant cette IP)
    - `http or dns` (Uniquement le HTTP ou le DNS)

!!! tip "Astuce : le clic droit est votre ami"
    Si vous repérez un paquet intéressant, vous pouvez faire un clic droit sur une de ses valeurs (ex: son adresse IP de destination) puis choisir **"Apply as Filter" -> "Selected"**. Wireshark écrira la syntaxe pour vous !

### Étape 5 : Analyser le contenu (Suivre le flux)

L'une des fonctions les plus puissantes de Wireshark est la reconstruction de session.

1. Filtrez pour trouver un échange (par exemple une page web en HTTP non chiffré).
2. Faites un clic droit sur un des paquets de cet échange.
3. Sélectionnez **Follow -> TCP Stream** (ou HTTP Stream).
4. Une nouvelle fenêtre s'ouvre, vous montrant les données brutes échangées, reconstituées de façon lisible. Les données envoyées par le client sont généralement en rouge, celles du serveur en bleu.

## Aide-mémoire

| Syntaxe (Filtre d'affichage) | Description |
|-------------------|-------------|
| `ip.addr == X.X.X.X` | Affiche tout ce qui touche à l'IP `X.X.X.X` |
| `tcp.flags.syn == 1` | Affiche les tentatives d'ouverture de connexion TCP (utile pour voir les scans) |
| `http.request.method == "GET"`| Affiche uniquement les requêtes HTTP GET |
| `eth.addr == MAC` | Filtre au niveau 2 par adresse MAC |

## Ressources

- [Documentation officielle Wireshark](https://www.wireshark.org/docs/wsug_html_chunked/) — Guide utilisateur très complet (en anglais).
- [Wiki Wireshark (DisplayFilters)](https://wiki.wireshark.org/DisplayFilters) — Cheatsheet officiel des filtres d'affichage.
