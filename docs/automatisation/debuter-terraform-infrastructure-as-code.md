---
title: Déployer son infrastructure avec Terraform (premiers pas)
date: 2026-06-15
author: Nicolas BODAINE
tags:
  - terraform
  - iac
  - docker
  - devops
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# Déployer son infrastructure avec Terraform : premiers pas

!!! abstract "Résumé"
    Introduction à Terraform, un outil open-source d'**Infrastructure as Code (IaC)**. Ce tutoriel explique les concepts de base et vous guide dans la création, la modification et la destruction d'une infrastructure locale simple (un conteneur Docker) de manière automatisée.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 / Linux |
| Dernière mise à jour | 2026-06-15 |

## Contexte

Dans les environnements modernes, l'infrastructure (serveurs, réseaux, bases de données) n'est plus configurée manuellement (clics dans une interface web ou commandes manuelles). Elle est décrite sous forme de code. C'est ce qu'on appelle l'**Infrastructure as Code (IaC)**.

**Terraform**, développé par HashiCorp, est l'outil leader du marché pour cette tâche. Il utilise un langage déclaratif (HCL - *HashiCorp Configuration Language*) pour décrire le résultat final souhaité, et s'occupe de faire les appels d'API nécessaires pour atteindre cet état.

Pour comprendre Terraform sans avoir besoin de créer un compte cloud (AWS, Azure, GCP) ou de carte bancaire, nous allons utiliser le **provider Docker**. Nous allons demander à Terraform de déployer un serveur web Nginx localement.

## Prérequis

- Une machine Linux (Ubuntu/Debian préféré).
- L'accès à un terminal avec les droits `sudo`.
- **Docker** installé et actif sur la machine. (Voir [Installer Docker Engine sur Ubuntu 24.04](../logiciels/installer-docker-engine-ubuntu-2404.md)).

## Concepts clés

- **Provider** : C'est le plugin qui permet à Terraform d'interagir avec une API distante (AWS, Docker, Proxmox, VMware...).
- **Resource** : C'est un élément d'infrastructure que l'on souhaite créer (une VM, un réseau, un conteneur).
- **State (`terraform.tfstate`)** : C'est le fichier (souvent distant) dans lequel Terraform mémorise l'état actuel de votre infrastructure pour pouvoir la comparer à votre code.

## Procédure

### Étape 1 : Installer Terraform

Sur Ubuntu, Terraform s'installe depuis le dépôt officiel de HashiCorp.

```bash
# Ajouter la clé GPG officielle
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

# Ajouter le dépôt
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

# Installer
sudo apt update && sudo apt install terraform
```

Vérifiez l'installation :
```bash
terraform -v
```

### Étape 2 : Préparer le projet

Créez un dossier pour votre projet Terraform et rendez-vous dedans :

```bash
mkdir ~/mon-premier-terraform
cd ~/mon-premier-terraform
```

Créez un fichier nommé `main.tf` avec votre éditeur favori (ex: `nano main.tf`) et ajoutez le code suivant :

```hcl title="main.tf"
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }
}

provider "docker" {
  # Pour Linux, on utilise le socket Docker local
  host = "unix:///var/run/docker.sock"
}

# Télécharger l'image Nginx
resource "docker_image" "nginx" {
  name         = "nginx:latest"
  keep_locally = false
}

# Lancer un conteneur à partir de cette image
resource "docker_container" "nginx" {
  image = docker_image.nginx.image_id
  name  = "mon_serveur_web_terraform"
  
  ports {
    internal = 80
    external = 8080
  }
}
```

### Étape 3 : Initialiser Terraform (`init`)

La première commande à lancer dans tout projet Terraform est `init`. Elle télécharge les plugins (providers) nécessaires définis dans votre fichier de configuration.

```bash
terraform init
```

!!! success "Résultat"
    Vous devriez voir `Terraform has been successfully initialized!`. Un dossier `.terraform` a été créé pour stocker le plugin Docker.

### Étape 4 : Planifier les changements (`plan`)

Avant d'appliquer quoi que ce soit, on demande à Terraform ce qu'il a l'intention de faire.

```bash
terraform plan
```

Dans la sortie console, Terraform vous indique avec un `+` vert ce qu'il va créer (ici, l'image Docker et le conteneur). Il affichera un résumé comme : `Plan: 2 to add, 0 to change, 0 to destroy.`

### Étape 5 : Appliquer la configuration (`apply`)

Une fois le plan validé, lancez la création de l'infrastructure :

```bash
terraform apply
```

Terraform réaffiche le plan et vous demande de confirmer. Tapez `yes` et validez.
Terraform va alors :
1. Télécharger l'image Nginx.
2. Démarrer le conteneur Nginx avec la redirection du port 8080 vers le port 80.

### Étape 6 : Détruire l'infrastructure (`destroy`)

L'avantage de l'IaC, c'est le nettoyage complet sans oublier de ressources. Pour tout supprimer :

```bash
terraform destroy
```

Confirmez avec `yes`. Terraform arrêtera et supprimera le conteneur ainsi que l'image.

## Vérification

Entre l'étape 5 (apply) et l'étape 6 (destroy), vous pouvez vérifier que votre infrastructure est bien en place.

1. **Vérifier via Docker** :
   ```bash
   docker ps
   ```
   Vous devriez voir un conteneur nommé `mon_serveur_web_terraform` en cours d'exécution.

2. **Vérifier le serveur web** :
   Ouvrez un navigateur sur `http://localhost:8080` ou faites un `curl` :
   ```bash
   curl http://localhost:8080
   ```
   !!! success "Résultat attendu"
       Le code HTML de la page d'accueil par défaut de Nginx s'affiche ("Welcome to nginx!").

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `terraform init` | Initialise le projet et télécharge les providers |
| `terraform plan` | Affiche les modifications qui vont être apportées |
| `terraform apply` | Applique les changements (création, modification, suppression) |
| `terraform destroy` | Détruit toute l'infrastructure gérée par le projet |
| `terraform fmt` | Formate proprement le code HCL du dossier courant |

## Ressources

- [Documentation officielle Terraform](https://developer.hashicorp.com/terraform/docs) — HashiCorp
- [Provider Docker pour Terraform](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs) — Terraform Registry
