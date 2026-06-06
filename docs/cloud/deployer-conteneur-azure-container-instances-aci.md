---
title: Déployer un conteneur via Azure Container Instances (ACI)
date: 2026-06-06
author: Nicolas BODAINE
tags:
  - azure
  - cloud
  - conteneurs
  - aci
difficulty: intermédiaire
os: Linux / Azure CLI
status: publié
---

# Déployer un conteneur via Azure Container Instances (ACI)

!!! abstract "Résumé"
    Azure Container Instances (ACI) permet d'exécuter des conteneurs Docker dans le cloud Azure de manière serverless, sans avoir à gérer l'infrastructure sous-jacente (comme les VM ou Kubernetes). Ce tutoriel explique comment déployer rapidement une image de conteneur publique via la ligne de commande Azure (`az cli`).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| Environnement | Azure CLI / Bash |
| Dernière mise à jour | 2026-06-06 |

## Contexte

Dans le cadre de projets d'apprentissage, de maquettes (PoC) ou de tâches planifiées, il est souvent inutile de provisionner un cluster Kubernetes complet (AKS) ou une VM dédiée. ACI répond à ce besoin en offrant un environnement d'exécution léger, rapide à démarrer et facturé à la seconde.

Nous allons ici déployer un simple serveur web Nginx depuis le registre public de Docker Hub.

## Prérequis

- Un compte Microsoft Azure avec une souscription active.
- L'outil en ligne de commande Azure CLI (`az`) installé sur votre machine.
- Une session bash ou un terminal Linux.

## Procédure

### Étape 1 : Connexion à Azure

Connectez-vous à votre compte Azure depuis votre terminal :

```bash
az login
```

Vérifiez que vous êtes sur la bonne souscription (si vous en avez plusieurs) :

```bash
az account show --output table
```

### Étape 2 : Création d'un groupe de ressources

Toute ressource Azure doit appartenir à un groupe de ressources (Resource Group). Nous allons en créer un spécifiquement pour ce conteneur.

```bash
az group create \
  --name rg-tuto-aci \
  --location westeurope
```

> **Note :** La région `westeurope` correspond généralement aux datacenters situés aux Pays-Bas, un bon choix pour l'Europe francophone.

### Étape 3 : Déploiement du conteneur

Nous utilisons la commande `az container create` pour provisionner l'instance ACI. Nous lui attribuerons un nom DNS (FQDN) afin qu'il soit accessible publiquement sur Internet.

```bash
az container create \
  --resource-group rg-tuto-aci \
  --name mon-conteneur-nginx \
  --image nginx:latest \
  --dns-name-label nginx-demo-$RANDOM \
  --ports 80
```

*Explications :*

- `--image nginx:latest` : Indique que l'image doit être récupérée sur Docker Hub public.
- `--dns-name-label` : Définit le sous-domaine de l'URL publique (doit être unique, d'où l'utilisation de `$RANDOM`).
- `--ports 80` : Ouvre le port 80 pour le trafic web.

### Étape 4 : Récupération du statut et de l'URL

Une fois la commande terminée (cela peut prendre environ 1 minute), vérifiez que le conteneur est bien en cours d'exécution et récupérez son FQDN (Fully Qualified Domain Name).

```bash
az container show \
  --resource-group rg-tuto-aci \
  --name mon-conteneur-nginx \
  --query "{FQDN:ipAddress.fqdn,ProvisioningState:provisioningState}" \
  --output table
```

## Vérification

1. Copiez le FQDN retourné par la commande précédente.
2. Ouvrez votre navigateur web et collez le FQDN dans la barre d'adresse (ex: `http://nginx-demo-12345.westeurope.azurecontainer.io`).
3. Vous devriez voir la page d'accueil par défaut "Welcome to nginx!".

!!! success "Résultat attendu"
    La page web s'affiche correctement. Cela confirme que le conteneur a été téléchargé, démarré, et que le trafic réseau est routé correctement par Azure.

### Nettoyage (Important)

ACI est facturé à la seconde. N'oubliez pas de supprimer vos ressources pour éviter des coûts inutiles.

```bash
az group delete \
  --name rg-tuto-aci \
  --yes \
  --no-wait
```

## Aide-mémoire

| Commande | Action |
|----------|--------|
| `az container logs -g <rg> -n <nom>` | Affiche les journaux standards (logs) du conteneur |
| `az container exec -g <rg> -n <nom> --exec-command "/bin/sh"` | Ouvre un shell interactif dans le conteneur |
| `az container stop -g <rg> -n <nom>` | Arrête l'exécution du conteneur (stoppe la facturation CPU/RAM) |

## Ressources

- [Microsoft Learn : Qu’est-ce qu’Azure Container Instances ?](https://learn.microsoft.com/fr-fr/azure/container-instances/container-instances-overview)
- [Microsoft Learn : Démarrage rapide avec Azure CLI](https://learn.microsoft.com/fr-fr/azure/container-instances/container-instances-quickstart)
