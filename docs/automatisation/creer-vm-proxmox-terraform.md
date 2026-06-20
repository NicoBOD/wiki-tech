---
title: Automatiser la création de machines virtuelles Proxmox avec Terraform
date: 2026-06-20
author: Nicolas BODAINE
tags:
  - proxmox
  - terraform
  - iac
  - automatisation
difficulty: intermédiaire
os: Linux / Proxmox VE
status: publié
---

# Automatiser la création de machines virtuelles Proxmox avec Terraform

!!! abstract "Résumé"
    Découvrez comment utiliser Terraform et le provider Telmate pour automatiser le déploiement et la configuration de machines virtuelles sur un hyperviseur Proxmox VE, dans une démarche d'Infrastructure as Code (IaC).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux / Proxmox VE |
| Dernière mise à jour | 2026-06-20 |

## Contexte

Dans un environnement de laboratoire ou de production basé sur Proxmox VE, la création manuelle de machines virtuelles (VM) depuis l'interface web devient rapidement fastidieuse et source d'erreurs. 

En utilisant **Terraform**, vous pouvez décrire vos machines virtuelles sous forme de code (Infrastructure as Code) et les déployer automatiquement. Cela garantit la reproductibilité, facilite la gestion des versions (avec Git), et permet de détruire ou recréer vos environnements de test en quelques secondes.

## Prérequis

- Un serveur **Proxmox VE** fonctionnel (version 7.x ou 8.x).
- **Terraform** installé sur votre machine locale (voir le [tutoriel sur les bases de Terraform](debuter-terraform-infrastructure-as-code.md)).
- Un accès **root** ou un utilisateur avec des privilèges suffisants sur Proxmox pour gérer les VM et générer un token d'API.
- Un **template (modèle) de VM** ou une image ISO prête à l'emploi sur Proxmox (ici nous utiliserons la méthode de clonage de template cloud-init pour plus d'efficacité).

## Procédure

### Étape 1 : Créer un utilisateur et un Token API dans Proxmox

Plutôt que d'utiliser le mot de passe `root`, il est recommandé de créer un utilisateur dédié et un token d'API pour Terraform.

Connectez-vous à l'interface web de Proxmox ou via SSH, et configurez les accès (exemple via interface web) :
1. Allez dans **Datacenter > Permissions > Users** et créez un utilisateur `terraform@pve`.
2. Allez dans **Datacenter > Permissions > API Tokens** et créez un token pour l'utilisateur `terraform@pve`. Nommez-le `tf-token`. **Notez le Secret (UUID)**, il ne sera affiché qu'une seule fois.
3. Allez dans **Datacenter > Permissions**, ajoutez une permission sur le path `/` avec le rôle `Administrator` (ou un rôle sur mesure) pour l'utilisateur ou le token `terraform@pve!tf-token`.

### Étape 2 : Configurer le provider Terraform pour Proxmox

Sur votre machine locale, créez un répertoire pour votre projet et initialisez le fichier principal.

```bash
mkdir proxmox-terraform
cd proxmox-terraform
touch main.tf credentials.auto.tfvars variables.tf
```

Dans le fichier `main.tf`, déclarez le provider (ici nous utilisons le provider populaire `Telmate/proxmox`) :

```hcl title="main.tf"
terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "3.0.1-rc1"
    }
  }
}

provider "proxmox" {
  pm_api_url          = "https://<IP_DE_VOTRE_PROXMOX>:8006/api2/json"
  pm_api_token_id     = var.proxmox_api_token_id
  pm_api_token_secret = var.proxmox_api_token_secret
  
  # Ignorer la vérification du certificat SSL (si auto-signé)
  pm_tls_insecure     = true
}
```

### Étape 3 : Configurer les variables et secrets

Ne stockez jamais vos secrets directement dans le code. Déclarez-les dans `variables.tf` et donnez-leur une valeur dans `credentials.auto.tfvars`.

```hcl title="variables.tf"
variable "proxmox_api_token_id" {
  type        = string
  description = "Token ID pour l'API Proxmox"
}

variable "proxmox_api_token_secret" {
  type        = string
  description = "Token Secret pour l'API Proxmox"
  sensitive   = true
}
```

```hcl title="credentials.auto.tfvars"
proxmox_api_token_id     = "terraform@pve!tf-token"
proxmox_api_token_secret = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" # Remplacez par votre vrai UUID
```

!!! warning "Sécurité"
    N'oubliez pas d'ajouter `*.auto.tfvars` dans votre fichier `.gitignore` pour ne pas pousser vos identifiants sur un dépôt public !

### Étape 4 : Déclarer la ressource Machine Virtuelle

Ajoutez le bloc suivant dans `main.tf` pour définir une VM qui sera clonée à partir d'un template (assurez-vous d'avoir un template existant, par exemple `ubuntu-cloud-init`).

```hcl title="main.tf"
resource "proxmox_vm_qemu" "test_server" {
  name        = "ubuntu-tf-vm"
  desc        = "VM déployée avec Terraform"
  target_node = "pve" # Remplacez par le nom de votre nœud Proxmox
  
  # Clonage à partir d'un template existant
  clone       = "ubuntu-cloud-init" # Nom exact du template dans Proxmox
  full_clone  = true

  # Configuration matérielle
  cores   = 2
  sockets = 1
  memory  = 2048
  agent   = 1 # Nécessite qemu-guest-agent installé sur le template

  # Configuration Réseau
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }

  # Disque système
  disk {
    size    = "20G"
    type    = "scsi"
    storage = "local-lvm"
  }
  scsihw = "virtio-scsi-pci"

  # Configuration Cloud-init
  os_type = "cloud-init"
  ipconfig0 = "ip=192.168.1.150/24,gw=192.168.1.1" # Mettez IP statique ou 'dhcp'
  nameserver = "1.1.1.1"
  ciuser     = "admin-tf"
  cipassword = "password-super-secure"
  sshkeys = <<EOF
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... votre_clé_publique...
EOF
}
```

### Étape 5 : Initialiser et déployer l'infrastructure

Dans votre terminal, lancez l'initialisation pour télécharger le provider :

```bash
terraform init
```

Vérifiez le plan d'exécution :

```bash
terraform plan
```

Si le plan est correct, appliquez la configuration :

```bash
terraform apply
```
Tapez `yes` pour confirmer. Terraform va communiquer avec l'API de Proxmox, cloner le template, ajuster les configurations et démarrer la VM.

## Vérification

Pour vérifier que tout s'est bien passé :
1. Allez sur l'interface web de Proxmox : vous devriez voir la VM `ubuntu-tf-vm` démarrée sur le nœud défini.
2. Ouvrez la console ou connectez-vous en SSH directement depuis votre terminal :

```bash
ssh admin-tf@192.168.1.150
```

!!! success "Résultat attendu"
    Vous devez être connecté en SSH sur votre nouvelle machine virtuelle avec les ressources allouées par Terraform.

## Ressources

- [Provider Telmate Proxmox sur le Terraform Registry](https://registry.terraform.io/providers/Telmate/proxmox/latest/docs) — Documentation officielle du provider.
- [Proxmox VE API Documentation](https://pve.proxmox.com/pve-docs/api-viewer/) — Pour comprendre comment Terraform interagit en arrière-plan.
