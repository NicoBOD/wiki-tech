---
title: Déployer Dify en local avec Docker pour orchestrer des applications IA
date: 2026-06-27
author: Nicolas BODAINE
tags:
  - dify
  - ia
  - docker
  - llm
  - rag
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Déployer Dify en local avec Docker pour orchestrer des applications IA

!!! abstract "Résumé"
    Dify est une plateforme open-source (LLMOps) facilitant la création et l'orchestration d'applications basées sur les LLMs. Ce tutoriel explique comment déployer la pile complète Dify sur votre propre machine ou serveur en utilisant Docker Compose.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 (ou toute distribution Linux avec Docker) |
| Dernière mise à jour | 2026-06-27 |

## Contexte

Vous souhaitez créer des chatbots avancés, des systèmes de questions-réponses sur vos propres documents (RAG - *Retrieval-Augmented Generation*), ou des agents IA autonomes, mais le développement "from scratch" en Python (avec LangChain ou LlamaIndex) est chronophage. 

**Dify** se présente comme une interface visuelle et un moteur de workflow permettant de construire rapidement ces applications. Il s'interface parfaitement avec des API externes (OpenAI, Anthropic) ou des modèles locaux (via Ollama) et inclut tout le nécessaire : gestion des prompts, base de données vectorielle, et suivi des logs.

## Prérequis

- Une machine Linux avec **Docker** et **Docker Compose** installés (consultez la documentation officielle de Docker si nécessaire).
- Au moins **4 Go de RAM** (8 Go recommandés) et 2 vCPU.
- Les ports **80** (HTTP) et **443** (HTTPS) disponibles.
- L'utilitaire `git` installé (`sudo apt install git`).

## Procédure

### Étape 1 : Cloner le dépôt officiel de Dify

L'installation officielle de Dify passe par leur dépôt GitHub qui contient l'ensemble des configurations Docker.

```bash
# Se placer dans le répertoire de son choix, ex: /opt/
cd /opt

# Cloner le dépôt
sudo git clone https://github.com/langgenius/dify.git

# Se rendre dans le sous-dossier docker
cd dify/docker
```

### Étape 2 : Préparer la configuration

Dify utilise un fichier `.env` pour stocker toutes ses variables de configuration (clés secrètes, ports, mots de passe des bases de données). Un fichier d'exemple est fourni.

```bash
# Copier le fichier d'exemple pour créer la configuration active
sudo cp .env.example .env

# Optionnel : Modifier les ports ou configurations spécifiques si besoin
# sudo nano .env
```
*Note : Par défaut, Dify écoutera sur le port 80. Si ce port est déjà pris (par un autre serveur web par exemple), modifiez les variables `NGINX_PORT` et `NGINX_HTTPS_PORT` dans le fichier `.env`.*

### Étape 3 : Déployer l'infrastructure avec Docker Compose

L'architecture de Dify est composée de plusieurs micro-services (base de données PostgreSQL, cache Redis, base vectorielle Weaviate ou Qdrant, worker Celery, API backend, interface web frontend, et Nginx comme reverse proxy).

```bash
# Lancer le déploiement en arrière-plan (mode détaché)
sudo docker compose up -d
```

Cette étape peut prendre quelques minutes, le temps que Docker télécharge toutes les images (plusieurs gigaoctets) et démarre les conteneurs.

### Étape 4 : Initialiser et accéder à Dify

Une fois tous les conteneurs démarrés, ouvrez votre navigateur web et accédez à l'adresse IP de votre serveur :

```text
http://<ADRESSE_IP_DU_SERVEUR>
```
*(Si vous êtes en local, utilisez simplement `http://localhost` ou `http://127.0.0.1`)*

1. Lors de la première visite, Dify vous demandera de configurer le compte **Administrateur**.
2. Renseignez un email, un nom d'utilisateur et un mot de passe robuste.
3. Vous arrivez ensuite sur le tableau de bord principal (Workspace).

### Étape 5 : Connecter un fournisseur de modèle (Ex: Ollama)

Dify seul est une coquille vide : il lui faut un "cerveau" (un LLM). 
Si vous avez un serveur **Ollama** tournant en local sur la même machine (port 11434) :

1. Dans Dify, cliquez sur votre profil en haut à droite > **Settings** (Paramètres).
2. Allez dans l'onglet **Model Providers** (Fournisseurs de modèles).
3. Défilez jusqu'à **Ollama** et cliquez sur **Add Model**.
4. Renseignez le nom du modèle (ex: `llama3` ou `mistral`).
5. Pour le champ "Base URL", si Ollama est sur la même machine hôte, utilisez l'IP locale de la passerelle Docker, souvent `http://172.17.0.1:11434` (ou l'IP LAN de votre machine). `localhost` ne fonctionnera pas car il ciblerait l'intérieur du conteneur Dify.
6. Cliquez sur **Save**. Vous pouvez désormais utiliser ce modèle pour vos applications Dify !

## Vérification

Pour s'assurer que tous les services Dify tournent correctement en tâche de fond :

```bash
cd /opt/dify/docker
sudo docker compose ps
```

!!! success "Résultat attendu"
    Vous devriez voir une liste d'environ 9 conteneurs (nginx, weaviate, db, redis, web, api, worker, sandbox, ssrf_proxy) avec la mention `Up` ou `running` dans la colonne `STATUS`.

## Ressources

- [Documentation officielle de Dify](https://docs.dify.ai/) — Guide complet et concepts avancés.
- [Dépôt GitHub de Dify](https://github.com/langgenius/dify) — Code source et issues tracker.
- [Connecter Ollama à Dify](https://marketplace.dify.ai/plugin/langgenius/ollama) — Guide spécifique pour les LLM locaux.
