---
title: Déployer un proxy IA unifié avec LiteLLM pour centraliser ses modèles
date: 2026-07-01
author: Nicolas BODAINE
tags:
  - IA
  - LiteLLM
  - Docker
  - Proxy
  - LLM
difficulty: intermédiaire
os: Linux (Docker)
status: publié
---

# Déployer un proxy IA unifié avec LiteLLM pour centraliser ses modèles

!!! abstract "Résumé"
    Apprenez à utiliser LiteLLM comme un proxy API universel pour unifier vos fournisseurs d'IA (OpenAI, Anthropic, Ollama, Mistral, etc.) sous une seule API compatible OpenAI.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux / Docker |
| Dernière mise à jour | 2026-07-01 |

## Contexte

Lorsque vous développez des applications basées sur l'intelligence artificielle, vous êtes souvent amené à utiliser plusieurs modèles provenant de différents fournisseurs (OpenAI, Anthropic, Google Gemini, ou même des modèles locaux via Ollama). 

Chaque fournisseur a souvent son propre format d'API et sa propre gestion de clés. **LiteLLM** permet de résoudre ce problème en s'interposant comme un "proxy". Il traduit toutes les requêtes en un format standard (celui d'OpenAI) et gère le routage, le suivi des coûts (cost tracking) et le contrôle d'accès vers vos différents modèles.

## Prérequis

- Un serveur Linux (Ubuntu, Debian...) avec un accès terminal.
- **Docker** et **Docker Compose** installés.
- Des clés d'API (ou un service local comme Ollama) pour tester la configuration.

## Procédure

### Étape 1 : Préparation de l'environnement

Créez un répertoire dédié pour votre proxy LiteLLM et placez-vous à l'intérieur.

```bash
mkdir -p ~/litellm-proxy
cd ~/litellm-proxy
```

### Étape 2 : Création de la configuration LiteLLM

LiteLLM fonctionne à l'aide d'un fichier YAML pour définir les modèles disponibles et leurs paramètres. Créez un fichier `config.yaml` :

```yaml title="config.yaml"
model_list:
  # Exemple avec OpenAI
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: os.environ/OPENAI_API_KEY

  # Exemple avec Anthropic Claude
  - model_name: claude-3-haiku
    litellm_params:
      model: anthropic/claude-3-haiku-20240307
      api_key: os.environ/ANTHROPIC_API_KEY

  # Exemple avec un modèle local Ollama
  - model_name: llama3-local
    litellm_params:
      model: ollama/llama3
      api_base: http://host.docker.internal:11434

general_settings:
  master_key: sk-mas-secret-key-123 # La clé unique que vos applications utiliseront
```

*(Note : Remplacez la valeur de `master_key` par une clé secrète sécurisée, par exemple générée via `openssl rand -hex 16`.)*

### Étape 3 : Fichier d'environnement (Variables)

Afin de ne pas exposer vos clés réelles dans le fichier `config.yaml`, nous utilisons le paramètre `os.environ`. Créez un fichier `.env` pour stocker vos véritables clés d'API :

```bash
nano .env
```

Ajoutez-y vos informations :

```env title=".env"
OPENAI_API_KEY=sk-proj-votre-cle-openai
ANTHROPIC_API_KEY=sk-ant-votre-cle-anthropic
```

### Étape 4 : Fichier Docker Compose

Créez le fichier `docker-compose.yml` pour déployer le proxy :

```yaml title="docker-compose.yml"
services:
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: litellm-proxy
    ports:
      - "4000:4000"
    volumes:
      - ./config.yaml:/app/config.yaml
    env_file:
      - .env
    command: [ "--config", "/app/config.yaml", "--port", "4000" ]
    restart: always
```

### Étape 5 : Lancement du proxy

Démarrez LiteLLM avec Docker Compose en mode détaché :

```bash
docker compose up -d
```

Vous pouvez vérifier les logs pour vous assurer que tout est bien lancé et que la configuration a été lue :

```bash
docker compose logs -f
```

## Vérification

Pour valider que votre proxy fonctionne, testez-le avec une simple requête `curl`. Vous allez interroger votre serveur (sur le port 4000) comme s'il s'agissait de l'API OpenAI, mais LiteLLM va router la requête vers le bon fournisseur.

Ici, nous interrogeons le modèle `gpt-3.5-turbo` via le proxy (remplacez `sk-mas-secret-key-123` par votre `master_key` configurée à l'étape 2) :

```bash
curl --location 'http://localhost:4000/v1/chat/completions' \
--header 'Authorization: Bearer VOTRE_CLE' \
--header 'Content-Type: application/json' \
--data '{
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Quelle est la capitale de la France ?"}
    ]
}'
```

!!! success "Résultat attendu"
    Vous devriez recevoir une réponse JSON structurée au format OpenAI contenant la réponse du modèle choisi (ex: *"La capitale de la France est Paris."*), quel que soit le fournisseur réel du modèle (Ollama, Anthropic, etc., en changeant juste le champ `model` dans la requête curl).

## Ressources

- [Documentation officielle LiteLLM](https://docs.litellm.ai/) — Documentation complète pour la gestion avancée des modèles, le tracking des dépenses et l'équilibrage de charge.
- [GitHub LiteLLM](https://github.com/BerriAI/litellm) — Dépôt du projet open-source.
