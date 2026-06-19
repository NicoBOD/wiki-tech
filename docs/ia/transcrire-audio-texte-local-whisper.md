---
title: Transcrire de l'audio en texte localement avec OpenAI Whisper
date: 2026-06-19
author: Nicolas BODAINE
tags:
  - ia
  - python
  - audio
  - open-source
  - whisper
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Transcrire de l'audio en texte localement avec OpenAI Whisper

!!! abstract "Résumé"
    Apprenez à installer et utiliser le modèle open source Whisper d'OpenAI pour transcrire ou traduire des fichiers audio en texte, directement sur votre propre machine. Contrairement aux API cloud, cette méthode garantit la confidentialité de vos données et fonctionne hors ligne.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-19 |

## Contexte

OpenAI propose **Whisper**, un modèle de reconnaissance vocale très performant et robuste. L'avantage majeur est qu'il est disponible en **open source** : vous pouvez le faire tourner localement sur votre ordinateur sans envoyer vos fichiers audio sur des serveurs distants. C'est particulièrement utile pour traiter des enregistrements confidentiels (réunions, entretiens) ou pour automatiser du sous-titrage sans payer de frais d'API.

## Prérequis

- Une machine sous Linux (Ubuntu 24.04 recommandé).
- **Python 3.9 à 3.11** (Whisper est compatible avec ces versions).
- L'outil de traitement audio **FFmpeg** installé sur le système.
- *(Optionnel mais recommandé)* Une carte graphique (GPU) NVIDIA avec les pilotes CUDA pour des performances optimales.

## Procédure

### Étape 1 : Installer FFmpeg

Whisper s'appuie sur `ffmpeg` pour lire et convertir quasiment n'importe quel format audio ou vidéo (mp3, wav, mp4, etc.).

```bash
sudo apt update
sudo apt install ffmpeg -y
```

Pour vérifier que l'installation a bien fonctionné :

```bash
ffmpeg -version
```

### Étape 2 : Préparer l'environnement Python

Il est fortement recommandé de créer un environnement virtuel pour isoler les dépendances de ce projet.

```bash
# Installation du paquet pour gérer les environnements virtuels (si non présent)
sudo apt install python3-venv -y

# Création du dossier du projet
mkdir ~/whisper-local && cd ~/whisper-local

# Création et activation de l'environnement virtuel
python3 -m venv whisper-env
source whisper-env/bin/activate
```

!!! tip "Activation de l'environnement"
    L'environnement virtuel doit être activé (`source whisper-env/bin/activate`) à chaque fois que vous souhaitez utiliser Whisper dans un nouveau terminal.

### Étape 3 : Installer Whisper et PyTorch

Si vous avez une carte graphique NVIDIA, installez d'abord PyTorch avec le support CUDA pour profiter de l'accélération GPU :

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Si vous utilisez uniquement le processeur (CPU), une installation classique suffit :

```bash
pip install torch torchvision torchaudio
```

Ensuite, installez le paquet officiel d'OpenAI Whisper directement depuis le dépôt GitHub :

```bash
pip install -U openai-whisper
```

### Étape 4 : Utiliser Whisper en ligne de commande

Whisper vient avec un outil en ligne de commande très simple. Placez un fichier audio de test (par exemple `interview.mp3`) dans votre dossier `~/whisper-local`.

Pour transcrire l'audio avec le modèle par défaut (qui est assez léger) :

```bash
whisper interview.mp3 --model small
```

#### Choisir le bon modèle

Whisper propose plusieurs tailles de modèles : `tiny`, `base`, `small`, `medium`, `large`.
- Les petits modèles (`tiny`, `base`) sont très rapides mais peuvent faire des erreurs sur des accents ou du bruit de fond.
- Les grands modèles (`large`, `large-v3`) sont très précis, gèrent de nombreuses langues mais exigent plus de mémoire RAM/VRAM et de puissance de calcul.

```bash
# Exemple avec le modèle large (idéal pour la précision en français)
whisper interview.mp3 --model large --language French
```

#### Traduire de l'audio vers l'anglais

Whisper sait nativement transcrire et traduire n'importe quelle langue prise en charge vers l'anglais. Utilisez l'argument `--task translate` :

```bash
whisper interview_francaise.mp3 --model medium --task translate
```

### Étape 5 : Utiliser Whisper dans un script Python

Pour automatiser vos traitements, vous pouvez importer Whisper directement dans vos scripts Python. Créez un fichier `transcrire.py` :

```python title="transcrire.py" linenums="1"
import whisper

# 1. Charger le modèle (ex: "base", "small", "medium", "large")
print("Chargement du modèle...")
model = whisper.load_model("small")

# 2. Lancer la transcription
print("Transcription en cours...")
result = model.transcribe("interview.mp3")

# 3. Afficher et sauvegarder le résultat
texte_transcrit = result["text"]
print("\nRésultat :")
print(texte_transcrit)

with open("transcription.txt", "w", encoding="utf-8") as f:
    f.write(texte_transcrit)
    
print("\nLe texte a été sauvegardé dans transcription.txt.")
```

Exécutez-le avec :

```bash
python transcrire.py
```

## Vérification

Pour valider le bon fonctionnement de l'outil, lancez une simple commande d'aide pour confirmer que la CLI de Whisper est accessible dans votre environnement virtuel :

```bash
whisper --help
```

!!! success "Résultat attendu"
    Une liste complète d'options et d'arguments doit s'afficher, prouvant que Whisper et toutes ses dépendances ont été correctement installés.

## Ressources

- [Dépôt GitHub officiel d'OpenAI Whisper](https://github.com/openai/whisper) — Documentation complète et code source.
- [Documentation PyTorch](https://pytorch.org/get-started/locally/) — Guide pour l'installation selon votre architecture matérielle (CUDA, ROCm, CPU).