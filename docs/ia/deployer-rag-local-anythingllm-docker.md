---
title: Déployer une solution RAG locale avec AnythingLLM et Docker
date: 2026-06-11
author: Nicolas BODAINE
tags:
  - ia
  - llm
  - docker
  - rag
  - anythingllm
difficulty: intermédiaire
os: Linux
status: publié
---

# Déployer une solution RAG locale avec AnythingLLM et Docker

!!! abstract "Résumé"
    Ce tutoriel vous guide pas-à-pas pour déployer AnythingLLM via Docker. Cette application open-source permet de créer votre propre système de Retrieval-Augmented Generation (RAG) en local, en s'interfaçant facilement avec Ollama. Vous pourrez ainsi discuter avec vos documents (PDF, Word, TXT) de manière totalement privée.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux (Debian/Ubuntu) |
| Dernière mise à jour | 2026-06-11 |

## Contexte

Le RAG (*Retrieval-Augmented Generation*) permet à un modèle d'IA de lire des documents externes avant de répondre à une question. Bien qu'il existe de nombreuses solutions cloud, conserver ses données en local garantit la confidentialité de ses informations. **AnythingLLM** est une interface web tout-en-un qui gère à la fois le stockage de documents, l'intégration à un modèle de langage (LLM) et la base de données vectorielle (pour la recherche).

## Prérequis

- Un serveur ou une machine Linux avec **Docker** installé.
- [Ollama installé et configuré](./installer-utiliser-ollama-llm-local.md) sur la même machine (ou accessible en réseau).
- Au moins 4 Go de RAM disponibles.

## Procédure

### Étape 1 : Préparation du dossier de stockage

AnythingLLM a besoin d'un répertoire permanent pour stocker ses données (bases de données, configuration, documents uploadés). Nous allons le créer dans votre répertoire personnel.

```bash
# Définir le chemin de stockage
export STORAGE_LOCATION=$HOME/anythingllm

# Créer le dossier
mkdir -p $STORAGE_LOCATION

# Créer un fichier d'environnement vide
touch "$STORAGE_LOCATION/.env"
```

### Étape 2 : Lancement du conteneur Docker

Lancez l'application AnythingLLM. Le conteneur exposera son interface web sur le port `3001`.

```bash
docker run -d \
  -p 3001:3001 \
  --name anythingllm \
  --restart unless-stopped \
  --cap-add SYS_ADMIN \
  -v ${STORAGE_LOCATION}:/app/server/storage \
  -v ${STORAGE_LOCATION}/.env:/app/server/.env \
  -e STORAGE_DIR="/app/server/storage" \
  mintplexlabs/anythingllm
```

!!! note "Note sur `--cap-add SYS_ADMIN`"
    Ce privilège est parfois requis par AnythingLLM pour exécuter Chromium en interne afin de *scraper* des pages web que vous lui donnez en référence.

### Étape 3 : Accès à l'interface et configuration

Une fois le conteneur démarré, l'interface est accessible depuis votre navigateur :
`http://<IP_DE_VOTRE_MACHINE>:3001`

Lors de la première connexion, un assistant de configuration s'affiche :

1. **LLM Provider** : Choisissez **Ollama**.
   - Entrez l'URL de l'API d'Ollama (par défaut : `http://host.docker.internal:11434` ou `http://<IP_DE_LA_MACHINE>:11434`).
   - Sélectionnez un modèle pré-téléchargé (par ex. `llama3` ou `mistral`).
2. **Vector Database** : Laissez la valeur par défaut (**LanceDB**), elle est intégrée à AnythingLLM et très performante pour un usage local.
3. **Embedding Model** : Choisissez le modèle d'embedding par défaut (AnythingLLM embarque son propre modèle léger, ce qui est parfait pour commencer).

### Étape 4 : Créer un "Workspace" et discuter avec vos documents

1. Créez un nouveau **Workspace** (Espace de travail) et donnez-lui un nom (ex: *Ressources RH* ou *Doc Technique*).
2. Cliquez sur l'icône de document (Upload) dans la barre latérale.
3. Glissez-déposez un fichier PDF ou un document Word.
4. Cliquez sur **Move to Workspace** puis sur **Save and Embed**.
   - *L'IA va découper votre document et le transformer en vecteurs.*
5. Retournez sur le chat du Workspace. Vous pouvez désormais poser des questions dont la réponse se trouve dans le document : AnythingLLM citera même ses sources !

## Vérification

Pour vérifier que le conteneur tourne correctement, listez vos conteneurs actifs :

```bash
docker ps | grep anythingllm
```

!!! success "Résultat attendu"
    Vous devriez voir `mintplexlabs/anythingllm` avec un statut `Up` depuis plusieurs minutes, et le port `0.0.0.0:3001->3001/tcp` ouvert.

## Ressources

- [Dépôt GitHub officiel d'AnythingLLM](https://github.com/Mintplex-Labs/anything-llm) — Code source et documentation complète.
- [Image Docker sur Docker Hub](https://hub.docker.com/r/mintplexlabs/anythingllm) — Versions et mises à jour de l'image.