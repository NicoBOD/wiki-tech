---
title: Automatiser la création d'images systèmes (Templates) avec Packer
date: 2026-06-25
author: Nicolas BODAINE
tags:
  - packer
  - automatisation
  - iac
  - proxmox
  - templates
difficulty: intermédiaire
os: Linux
status: publié
---

# Automatiser la création d'images systèmes (Templates) avec Packer

!!! abstract "Résumé"
    Packer est un outil open source développé par HashiCorp qui permet de créer des images machines identiques (templates) pour de multiples plateformes à partir d'une seule configuration source. Ce tutoriel montre comment installer Packer et l'utiliser pour automatiser la création d'un template de machine virtuelle (par exemple, pour Proxmox VE), simplifiant ainsi vos déploiements futurs.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux (Debian/Ubuntu) |
| Dernière mise à jour | 2026-06-25 |

## Contexte

La création manuelle d'images systèmes (installer l'OS, faire les mises à jour, installer les prérequis de base, nettoyer l'image) est une tâche chronophage et source d'erreurs. Pour des étudiants ou des professionnels (TSSR, Administrateur Système), l'automatisation de cette tâche est indispensable. Packer permet de définir l'infrastructure sous forme de code (Infrastructure as Code - IaC) et de générer des templates fiables et reproductibles pour VMware, Proxmox, AWS, ou même Docker.

## Prérequis

- Un poste de travail sous Linux (Debian ou Ubuntu).
- Un accès à un hyperviseur (dans cet exemple, Proxmox VE) avec des identifiants API (Token) valides.
- Une connaissance de base du terminal Linux.

## Procédure

### Étape 1 : Installation de Packer

Packer est distribué sous forme de binaire. Nous allons utiliser le dépôt officiel de HashiCorp pour l'installer sur Debian/Ubuntu.

```bash
# Ajout de la clé GPG officielle de HashiCorp
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

# Ajout du dépôt HashiCorp
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

# Mise à jour des paquets et installation
sudo apt update
sudo apt install packer
```

Vérifiez l'installation :
```bash
packer --version
```

### Étape 2 : Préparation du projet Packer

Créez un dossier dédié pour votre projet Packer et déplacez-vous dedans :

```bash
mkdir ~/packer-proxmox-template
cd ~/packer-proxmox-template
```

Packer utilise le langage HCL (HashiCorp Configuration Language), similaire à Terraform. Créez un fichier de configuration principal nommé `ubuntu-server.pkr.hcl`.

### Étape 3 : Écriture du fichier de configuration Packer

Voici un exemple de configuration pour créer un template Ubuntu Server 24.04 sur Proxmox VE. 

!!! note "Variables d'environnement"
    Pour des raisons de sécurité, nous n'incluons pas les mots de passe dans le fichier. Ils seront passés via des variables d'environnement.

Créez le fichier `ubuntu-server.pkr.hcl` et ajoutez le code suivant :

```hcl title="ubuntu-server.pkr.hcl"
packer {
  required_plugins {
    proxmox = {
      version = ">= 1.1.8"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

variable "proxmox_api_url" {
  type    = string
}

variable "proxmox_api_token_id" {
  type    = string
}

variable "proxmox_api_token_secret" {
  type      = string
  sensitive = true
}

source "proxmox-iso" "ubuntu" {
  proxmox_url              = var.proxmox_api_url
  username                 = var.proxmox_api_token_id
  token                    = var.proxmox_api_token_secret
  insecure_skip_tls_verify = true
  
  node                 = "pve-node-01"
  vm_id                = 9000
  vm_name              = "ubuntu-24.04-template"
  template_description = "Template Ubuntu 24.04 généré par Packer"

  # Paramètres de l'OS
  iso_file = "local:iso/ubuntu-24.04-live-server-amd64.iso"
  unmount_iso = true

  # Paramètres matériels
  cores    = 2
  memory   = 2048
  scsi_controller = "virtio-scsi-pci"
  
  disks {
    disk_size         = "20G"
    format            = "raw"
    storage_pool      = "local-lvm"
    type              = "scsi"
  }

  network_adapters {
    model  = "virtio"
    bridge = "vmbr0"
  }

  # Détection automatique de l'installation (Cloud-init / Autoinstall)
  boot_command = [
    "<esc><wait>",
    "e<wait>",
    "<down><down><down><end>",
    " autoinstall ds=nocloud-net\\;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ ",
    "<f10>"
  ]
  boot_wait = "5s"
  http_directory = "http"
  
  ssh_username = "ubuntu"
  ssh_password = "password123"
  ssh_timeout  = "20m"
}

build {
  sources = ["source.proxmox-iso.ubuntu"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
      "sudo apt-get clean",
      # Nettoyage de l'ID machine pour le clonage
      "sudo truncate -s 0 /etc/machine-id",
      "sudo rm /var/lib/dbus/machine-id",
      "sudo ln -s /etc/machine-id /var/lib/dbus/machine-id"
    ]
  }
}
```

### Étape 4 : Fichier Cloud-Init (Autoinstall)

L'installation automatisée d'Ubuntu repose sur un fichier de configuration Cloud-Init (`user-data`). Packer va le servir temporairement via un mini-serveur HTTP intégré.

Créez un dossier `http` et un fichier `user-data` à l'intérieur :

```bash
mkdir http
```

Créez le fichier `http/user-data` :

```yaml title="http/user-data"
#cloud-config
autoinstall:
  version: 1
  identity:
    hostname: ubuntu-template
    password: "$6$exyv1/u5aY1eKk6r$Kk.z8m3gYn1sU.Tz4L0s2g.oV/2X2K3F4V/5M5E6P7Y8D9J0R1U2N3X4G5K6B7W8D9J0R1U2N3X4G5K6B/"
    realname: Ubuntu User
    username: ubuntu
  ssh:
    install-server: true
    allow-pw: true
  packages:
    - qemu-guest-agent
    - cloud-init
```

!!! note "Mot de passe"
    Le hash correspond au mot de passe `password123`. Il est utilisé pour la connexion SSH initiale de Packer.

Créez également un fichier vide `http/meta-data` :

```bash
touch http/meta-data
```

### Étape 5 : Initialisation et Validation

Avant de lancer la construction, initialisez le projet pour télécharger le plugin Proxmox :

```bash
packer init ubuntu-server.pkr.hcl
```

Validez ensuite la syntaxe de votre fichier :

```bash
packer validate ubuntu-server.pkr.hcl
```

### Étape 6 : Lancement de la construction

Exportez vos identifiants Proxmox en tant que variables d'environnement (les noms de variables Packer préfixés par `PKR_VAR_`) :

```bash
export PKR_VAR_proxmox_api_url="https://votre-proxmox:8006/api2/json"
export PKR_VAR_proxmox_api_token_id="packer@pve!mon_token"
export PKR_VAR_proxmox_api_token_secret="votre-secret-token"
```

Lancez la création du template :

```bash
packer build ubuntu-server.pkr.hcl
```

Packer va se connecter à Proxmox, créer une VM, la démarrer sur l'ISO, taper automatiquement la commande de démarrage (boot_command) pour lancer l'autoinstallation, attendre que le port SSH s'ouvre, exécuter le script de nettoyage (provisioner shell), et enfin convertir la VM en template.

## Vérification

Une fois le processus terminé avec le message `Build 'proxmox-iso.ubuntu' finished.`, connectez-vous à l'interface web de votre Proxmox.

!!! success "Résultat attendu"
    Vous devriez voir un nouveau Template (avec l'ID 9000 et le nom `ubuntu-24.04-template`) dans votre nœud Proxmox. Vous pouvez désormais cloner ce template pour déployer rapidement de nouvelles machines virtuelles identiques, prêtes à l'emploi avec Terraform par exemple !

## Ressources

- [Documentation officielle de Packer](https://developer.hashicorp.com/packer/docs) — Référence complète pour comprendre et configurer Packer.
- [Plugin Packer pour Proxmox](https://developer.hashicorp.com/packer/integrations/hashicorp/proxmox) — Options et paramètres pour le constructeur Proxmox ISO.
- [Autoinstallation Ubuntu (Subiquity)](https://ubuntu.com/server/docs/install/autoinstall) — Documentation pour personnaliser le fichier `user-data`.