---
title: Connecter Open WebUI à Ollama (Votre propre ChatGPT local)
date: 2026-06-07
author: Nicolas BODAINE
tags:
  - ia
  - llm
  - ollama
  - open-webui
  - docker
  - ubuntu
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Connecter Open WebUI à Ollama : votre propre ChatGPT local

!!! abstract "Résumé"
    Ce tutoriel explique comment déployer **Open WebUI** avec Docker pour offrir une interface web conviviale (similaire à ChatGPT) à vos modèles de langage locaux exécutés par **Ollama**. Fini la ligne de commande, place à une vraie interface graphique multi-utilisateurs !

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-07 |

## Contexte

Dans un [précédent tutoriel](installer-utiliser-ollama-llm-local.md), nous avons vu comment installer Ollama pour faire tourner des LLM (comme Llama 3 ou Mistral) en local sur votre machine. Bien que fonctionnelle, l'utilisation exclusive en ligne de commande limite l'adoption par des utilisateurs moins techniques et ne permet pas de conserver facilement l'historique des conversations.

**Open WebUI** (anciennement Ollama WebUI) comble ce vide. C'est une interface web open source très riche en fonctionnalités, qui s'intègre parfaitement avec Ollama et offre une expérience utilisateur très proche de ChatGPT.

## Prérequis

- Une machine Linux (ex: Ubuntu Server 24.04).
- **Ollama** installé et fonctionnel (voir le [tutoriel dédié](installer-utiliser-ollama-llm-local.md)).
- **Docker** installé sur la machine (voir le [tutoriel Docker](../logiciels/installer-docker-engine-ubuntu-2404.md)).

## Procédure

### Étape 1 : Lancer Open WebUI avec Docker

Open WebUI est distribué principalement sous forme d'image Docker, ce qui rend son déploiement très simple.

Si Open WebUI et Ollama sont installés sur le **même serveur**, vous devez permettre au conteneur Docker d'Open WebUI de communiquer avec Ollama qui tourne sur l'hôte.

Exécutez la commande suivante pour télécharger et démarrer le conteneur :

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

**Explications des paramètres :**

- `-d` : Fait tourner le conteneur en arrière-plan (mode détaché).
- `-p 3000:8080` : Expose l'interface web sur le port `3000` de votre machine (le port interne du conteneur est le 8080).
- `--add-host=host.docker.internal:host-gateway` : Permet au conteneur d'accéder au réseau de l'hôte (indispensable pour contacter Ollama sur `localhost:11434`).
- `-v open-webui:/app/backend/data` : Crée un volume persistant pour sauvegarder vos conversations, vos paramètres et vos comptes utilisateurs.
- `--name open-webui` : Nomme le conteneur pour le retrouver facilement.
- `--restart always` : Assure que l'interface redémarre automatiquement au boot du serveur ou en cas de crash.

### Étape 2 : Accéder à l'interface et créer le compte administrateur

Une fois le conteneur démarré, ouvrez votre navigateur web et accédez à l'adresse suivante :

```text
http://<IP_DE_VOTRE_SERVEUR>:3000
```
*(Si vous êtes en local, utilisez `http://localhost:3000` ou `http://127.0.0.1:3000`)*

Lors de votre première connexion :
1. Cliquez sur **"Sign Up"** (S'inscrire).
2. Remplissez le formulaire (Nom, Email, Mot de passe). 
3. **Le premier compte créé devient automatiquement l'Administrateur** de l'instance Open WebUI.

!!! note "Sécurité"
    Par défaut, les inscriptions sont ouvertes. Une fois votre compte admin créé, il est recommandé d'aller dans les paramètres (Settings > Admin Settings > General) pour désactiver les nouvelles inscriptions ("Enable New Sign Ups") si votre serveur est accessible publiquement.

### Étape 3 : Interagir avec vos modèles

Une fois connecté, l'interface ressemblera fortement à ce que vous connaissez peut-être déjà.

1. En haut de l'écran, vous verrez un menu déroulant permettant de **sélectionner un modèle**.
2. Open WebUI détecte automatiquement les modèles que vous avez déjà téléchargés via Ollama (ex: `llama3`, `mistral`, `phi3`).
3. Si la liste est vide, vous pouvez aller dans les paramètres **Admin Settings > Models** pour télécharger de nouveaux modèles directement depuis l'interface web en entrant leur nom (ex: `llama3:8b`).
4. Sélectionnez un modèle et commencez à discuter !

## Vérification

Pour vérifier que votre conteneur Docker tourne correctement et n'affiche pas d'erreurs, vous pouvez consulter ses logs :

```bash
docker logs -f open-webui
```

!!! success "Résultat attendu"
    Vous devriez voir des messages indiquant le démarrage du serveur Uvicorn / FastAPI et aucune erreur de connexion fatale. Vous pouvez stopper la lecture des logs avec ++ctrl+c++.

## Ressources

- [Dépôt GitHub d'Open WebUI](https://github.com/open-webui/open-webui) — Code source et documentation officielle.
- [Docker Hub - Open WebUI](https://hub.docker.com/r/ghcr.io/open-webui/open-webui) — Image Docker officielle.
- [Bibliothèque de modèles Ollama](https://ollama.com/library) — Liste des modèles téléchargeables.
