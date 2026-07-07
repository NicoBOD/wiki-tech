---
title: Installer et utiliser Stable Diffusion en local (Automatic1111)
date: 2026-06-24
author: Nicolas BODAINE
tags:
  - ia
  - stable diffusion
  - automatic1111
  - image
  - gpu
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Installer et utiliser Stable Diffusion en local (Automatic1111)

!!! abstract "Résumé"
    Ce tutoriel explique comment installer et utiliser **Stable Diffusion WebUI (Automatic1111)** sur une machine Linux. C'est l'interface la plus populaire pour générer des images par Intelligence Artificielle en local, sans dépendre d'un service cloud.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 / Debian 12 |
| Dernière mise à jour | 2026-06-24 |

## Contexte

La génération d'images par IA a connu un bond majeur avec la publication des modèles **Stable Diffusion** en open-source. Plutôt que de payer des abonnements à des services comme Midjourney ou DALL-E, vous pouvez faire tourner votre propre générateur d'images directement sur votre matériel.

Le projet **Stable Diffusion WebUI** (souvent appelé **Automatic1111**, du nom de son créateur) offre une interface web complète pour utiliser ces modèles, paramétrer la génération (prompt, negative prompt, steps, CFG scale) et gérer ses extensions.

## Prérequis

- **Système** : Une distribution Linux basée sur Debian (Ubuntu 24.04 utilisé ici).
- **Python** : Version 3.10 ou 3.11 installée.
- **Stockage** : Au moins 15 à 20 Go d'espace disque disponible (les modèles pèsent plusieurs gigaoctets).
- **Matériel (GPU)** : Une carte graphique NVIDIA (série RTX 20xx, 30xx, 40xx) avec au moins 6 Go de VRAM est *fortement recommandée*. Des pilotes NVIDIA fonctionnels sont requis. 
*(Note : Il est possible de générer des images uniquement avec le CPU, mais cela sera extrêmement lent).*

## Procédure

### Étape 1 : Installer les dépendances système

Avant de télécharger le logiciel, nous devons nous assurer que Git, Python, son module d'environnement virtuel (`venv`), et certaines bibliothèques système liées à l'affichage sont présents.

```bash
sudo apt update
sudo apt install wget git python3 python3-venv libgl1 libglib2.0-0
```

### Étape 2 : Cloner le dépôt GitHub

Placez-vous dans le répertoire de votre choix (par exemple votre dossier utilisateur) et clonez le dépôt officiel d'Automatic1111 :

```bash
cd ~
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui
```

### Étape 3 : Lancer l'installation et le serveur

L'avantage d'Automatic1111 est que tout le processus d'installation Python est géré par un script bash appelé `webui.sh`. Ce script va :
1. Créer un environnement virtuel Python local (`venv`).
2. Télécharger toutes les dépendances lourdes (PyTorch, torchvision, etc.).
3. Télécharger le modèle de base par défaut (Stable Diffusion v1.5, environ 4 Go) s'il n'y a aucun modèle présent.

```bash
# Lancement de l'interface
./webui.sh
```

!!! warning "Temps de téléchargement"
    Le premier lancement prendra du temps (parfois 15 à 30 minutes selon votre connexion), car il doit télécharger de lourds composants. Laissez-le tourner jusqu'à l'apparition du message indiquant l'URL locale.

Une fois l'installation terminée, vous verrez un message similaire à :
`Running on local URL:  http://127.0.0.1:7860`

Vous pouvez alors ouvrir votre navigateur et accéder à `http://127.0.0.1:7860`.

### Étape 4 : Options de démarrage utiles (webui-user.sh)

Pour éviter de taper des arguments de ligne de commande à chaque fois, Automatic1111 utilise le fichier `webui-user.sh` pour enregistrer vos paramètres. 

Éditez ce fichier avec votre éditeur favori :
```bash
nano webui-user.sh
```

Modifiez la variable `COMMANDLINE_ARGS` en fonction de votre configuration matérielle :

**Cas 1 : Accéder à l'interface depuis un autre poste du réseau**
```bash
export COMMANDLINE_ARGS="--listen"
```
*Le serveur écoutera sur `0.0.0.0`, l'interface sera accessible via `http://IP_DE_LA_MACHINE:7860`.*

**Cas 2 : Vous n'avez pas de carte graphique (Génération sur CPU)**
```bash
export COMMANDLINE_ARGS="--use-cpu all --precision full --no-half --skip-torch-cuda-test"
```

**Cas 3 : Vous avez peu de mémoire vidéo (Moins de 6 Go de VRAM)**
```bash
export COMMANDLINE_ARGS="--medvram"
```

## Vérification

1. Une fois le serveur lancé (via `./webui.sh`), ouvrez l'URL affichée.
2. Dans le champ **Prompt**, tapez une description en anglais, par exemple : `a cute orange cat sitting on a laptop, high quality, digital art`.
3. Cliquez sur le bouton orange **Generate**.
4. Patientez pendant que la barre de progression avance. L'image devrait apparaître sur la droite !

!!! tip "Où sont stockées les images ?"
    Toutes les images générées sont automatiquement sauvegardées sur votre disque dans le sous-dossier `outputs/` de votre répertoire `stable-diffusion-webui`.

## Ajouter d'autres modèles

Le modèle v1.5 de base est très bien, mais des modèles spécialisés (photoréalisme, anime, architecture...) existent. 
Pour en ajouter :
1. Téléchargez des modèles (au format `.safetensors`) depuis des sites comme [Civitai](https://civitai.com/) ou [Hugging Face](https://huggingface.co/).
2. Placez les fichiers dans le dossier `models/Stable-diffusion/`.
3. Sur l'interface web, cliquez sur l'icône de rafraîchissement bleue à côté de la liste déroulante *Stable Diffusion checkpoint* en haut à gauche.

## Ressources

- [Dépôt GitHub officiel AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) — Sources et documentation
- [Civitai](https://civitai.com/) — Référentiel communautaire de modèles et d'outils
- [Hugging Face](https://huggingface.co/models?pipeline_tag=text-to-image) — Dépôt de modèles open source
