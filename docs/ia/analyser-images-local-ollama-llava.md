---
title: Analyser des images en local avec Ollama et le modèle vision LLaVA
date: 2026-06-16
author: Nicolas BODAINE
tags:
  - ia
  - ollama
  - llava
  - vision
  - local
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Analyser des images en local avec Ollama et le modèle LLaVA

!!! abstract "Résumé"
    Découvrez comment utiliser l'IA pour analyser, décrire ou interroger le contenu de vos images de manière totalement locale et privée, sans rien envoyer dans le cloud, grâce à Ollama et au modèle multimodal LLaVA.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 (ou tout système compatible Ollama) |
| Dernière mise à jour | 2026-06-16 |

## Contexte

Ollama s'est imposé comme l'outil incontournable pour faire tourner des LLM (Large Language Models) en local. Ce que l'on sait moins, c'est qu'il prend également en charge les **modèles multimodaux**, c'est-à-dire capables de comprendre plusieurs types de données, comme du texte ET des images.

Le modèle **LLaVA** (Large Language-and-Vision Assistant) est l'un des modèles open-source les plus performants dans ce domaine. Il vous permet de faire de l'analyse visuelle, de la reconnaissance de texte (OCR), ou simplement de demander une description détaillée d'une image, le tout sans compromettre la confidentialité de vos données.

## Prérequis

- [Ollama installé et fonctionnel](installer-utiliser-ollama-llm-local.md) sur votre machine.
- Au moins 8 Go de RAM (le modèle `llava` par défaut pèse environ 4.5 Go).
- Une image de test (par exemple, une photo de paysage ou une capture d'écran) stockée sur votre machine.

## Procédure

### Étape 1 : Télécharger le modèle LLaVA

La première étape consiste à récupérer le modèle depuis la bibliothèque de modèles d'Ollama.

```bash
ollama pull llava
```

Ollama va télécharger les poids du modèle. Si vous avez une configuration très modeste ou très puissante, sachez qu'il existe d'autres déclinaisons comme `llava:13b` (plus lourd) ou `llava:34b`.

### Étape 2 : Analyser une image en ligne de commande

Une fois le modèle téléchargé, vous pouvez lui poser une question en incluant simplement le chemin absolu ou relatif de votre image dans le prompt. Ollama détectera automatiquement le fichier, le transformera au format attendu et l'enverra au modèle.

Exemple :

```bash
ollama run llava "Décris-moi cette image en français : /home/user/Images/vacances.jpg"
```

!!! tip "Astuce pour les chemins de fichiers"
    Assurez-vous que le chemin vers votre image ne contienne pas d'espaces, ou entourez-le correctement de guillemets pour éviter que le terminal ne le coupe.

### Étape 3 : Mode interactif

Vous pouvez aussi entrer dans l'interface de discussion d'Ollama, puis charger l'image.

```bash
ollama run llava
```

Une fois le prompt `>>>` affiché, vous pouvez simplement ajouter votre image à vos questions :

```text
>>> Peux-tu me lister les objets présents sur l'image ./bureau.png ?
```

### Étape 4 : Utiliser l'API REST d'Ollama avec une image

Si vous souhaitez automatiser ce processus dans un script (en Python, Bash, etc.), l'API d'Ollama accepte les images. L'image doit cependant être envoyée encodée en **Base64**.

Voici un exemple avec la commande `curl` :

```bash
# On encode d'abord l'image en base64 sans sauts de ligne (-w 0 sur Linux)
IMAGE_BASE64=$(base64 -w 0 /chemin/vers/image.jpg)

# On envoie la requête à l'API locale
curl http://localhost:11434/api/generate -d '{
  "model": "llava",
  "prompt": "Que vois-tu sur cette image ? Réponds de façon concise.",
  "images": ["'"$IMAGE_BASE64"'"],
  "stream": false
}'
```

Le retour sera un flux JSON contenant la réponse de l'IA (champ `response`).

## Vérification

Pour valider le bon fonctionnement de l'installation, téléchargez une image arbitraire et testez :

```bash
wget -O /tmp/test-image.jpg https://raw.githubusercontent.com/ollama/ollama/main/docs/images/ollama-logo.png
ollama run llava "What is the text on this image? /tmp/test-image.jpg"
```

!!! success "Résultat attendu"
    L'IA devrait identifier qu'il s'agit du logo d'Ollama ou mentionner la présence de l'alpaga emblématique.

## Ressources

- [Documentation officielle Ollama](https://github.com/ollama/ollama) — Dépôt GitHub d'Ollama.
- [Modèle LLaVA sur Ollama](https://ollama.com/library/llava) — Page de la bibliothèque avec les différentes déclinaisons de LLaVA.
- [Projet de recherche LLaVA](https://llava-vl.github.io/) — Le site du projet de recherche original derrière le modèle.
