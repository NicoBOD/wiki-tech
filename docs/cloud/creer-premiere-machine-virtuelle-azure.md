---
title: Créer et configurer sa première machine virtuelle sur Microsoft Azure
date: 2026-06-28
author: Nicolas BODAINE
tags:
  - azure
  - cloud
  - vm
  - cli
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# Créer et configurer sa première machine virtuelle sur Microsoft Azure

!!! abstract "Résumé"
    Ce tutoriel explique comment déployer rapidement une première machine virtuelle (VM) sous Linux (Ubuntu) sur le cloud Microsoft Azure en utilisant l'outil en ligne de commande **Azure CLI**. Cette approche est idéale pour automatiser des déploiements ou simplement apprendre les concepts de base d'Azure (Groupes de ressources, VM, Réseaux).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 (Serveur et Client) |
| Dernière mise à jour | 2026-06-28 |

## Contexte

Microsoft Azure propose une interface web (le portail Azure) très complète, mais le déploiement via ligne de commande avec **Azure CLI** (`az`) s'avère souvent plus rapide, plus clair et surtout automatisable sous forme de scripts. 

L'objectif de ce lab est de déployer une machine virtuelle Linux basique, d'ouvrir un port réseau (comme le port 80 pour le web), et de s'y connecter de manière sécurisée en SSH.

## Prérequis

- Un compte Microsoft Azure actif (un abonnement gratuit ou étudiant suffit).
- Disposer d'un terminal Linux (ou WSL sous Windows, ou macOS).
- L'outil **Azure CLI** (`az`) installé sur votre machine locale.

## Procédure

### Étape 1 : Installer et se connecter à Azure CLI

Si Azure CLI n'est pas encore installé sur votre poste de travail (Ubuntu/Debian), vous pouvez l'installer facilement :

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Ensuite, authentifiez-vous pour relier votre terminal à votre compte Azure :

```bash
az login
```

!!! note "Authentification"
    Cette commande va ouvrir une fenêtre de votre navigateur par défaut pour vous permettre de saisir vos identifiants Microsoft. Une fois connecté, vous pouvez retourner à votre terminal, qui affichera la liste de vos abonnements Azure.

### Étape 2 : Créer un groupe de ressources

Dans Azure, toutes les ressources (VM, adresses IP, disques, cartes réseau) doivent obligatoirement être contenues dans un **Groupe de ressources** (Resource Group). C'est un conteneur logique.

Créons un groupe nommé `MonPremierLab-RG` situé dans le datacenter de Paris (`francecentral`) :

```bash
az group create \
  --name MonPremierLab-RG \
  --location francecentral
```

### Étape 3 : Déployer la machine virtuelle

Nous allons maintenant ordonner à Azure de provisionner une VM. Nous choisirons ici l'image officielle d'Ubuntu 24.04 LTS et un gabarit de machine économique (`Standard_B1s`). Azure va également générer automatiquement les clés SSH nécessaires à la connexion si vous ne les possédez pas.

```bash
az vm create \
  --resource-group MonPremierLab-RG \
  --name MaVM-Ubuntu \
  --image Ubuntu2404 \
  --size Standard_B1s \
  --admin-username azureuser \
  --generate-ssh-keys
```

!!! tip "Clés SSH générées"
    Le paramètre `--generate-ssh-keys` crée une paire de clés SSH sur votre machine locale (habituellement dans `~/.ssh/id_rsa` et `~/.ssh/id_rsa.pub`) si elle n'existe pas déjà, et installe automatiquement la clé publique sur la VM Azure.

La création prend environ une à deux minutes. À la fin du processus, la commande affichera un bloc JSON contenant l'adresse IP publique de votre nouvelle machine (champ `publicIpAddress`). Notez bien cette adresse.

### Étape 4 : Ouvrir les ports réseau

Par défaut, Azure crée un "Groupe de sécurité réseau" (NSG) qui bloque tous les flux entrants depuis Internet, à l'exception du port SSH (TCP/22).
Si vous souhaitez héberger un service web sur cette VM, il faut explicitement ouvrir le port HTTP (TCP/80) :

```bash
az vm open-port \
  --resource-group MonPremierLab-RG \
  --name MaVM-Ubuntu \
  --port 80 \
  --priority 1001
```

### Étape 5 : Se connecter à la VM

Vous pouvez désormais prendre le contrôle de votre VM à distance en utilisant SSH et l'adresse IP publique obtenue lors de l'étape 3.

```bash
ssh azureuser@<ADRESSE_IP_PUBLIQUE>
```

Lors de la première connexion, acceptez l'empreinte cryptographique du serveur en tapant `yes`. 
Vous êtes maintenant connecté sur votre machine virtuelle hébergée dans le cloud Microsoft ! Vous pouvez y installer vos paquets classiques (ex: `sudo apt update && sudo apt install nginx`).

## Nettoyage (Rappel important)

Les ressources allumées dans le cloud sont facturées à l'usage. Une fois votre test terminé, il est **indispensable** de supprimer les ressources pour ne pas consommer votre crédit. 

La suppression du groupe de ressources détruira d'un seul coup la VM, l'adresse IP, le disque dur et toutes les configurations associées :

```bash
az group delete --name MonPremierLab-RG --yes --no-wait
```

## Vérification

Pour valider l'état de la suppression (qui s'effectue en arrière-plan grâce au paramètre `--no-wait`), vous pouvez lister vos groupes de ressources actuels :

```bash
az group list -o table
```

Si la commande ne retourne plus `MonPremierLab-RG`, c'est que votre environnement de test a été complètement nettoyé.

## Ressources

- [Documentation officielle Azure CLI](https://learn.microsoft.com/fr-fr/cli/azure/) — Référence de la commande az
- [Créer une machine virtuelle Linux dans Azure](https://learn.microsoft.com/fr-fr/azure/virtual-machines/linux/quick-create-cli) — Guide rapide par Microsoft
