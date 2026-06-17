---
title: Créer des environnements de test locaux reproductibles avec Vagrant et VirtualBox
date: 2026-06-17
author: Nicolas BODAINE
tags:
  - vagrant
  - virtualbox
  - vm
  - iac
  - automatisation
difficulty: intermédiaire
os: Windows / macOS / Linux
status: publié
---

# Créer des environnements de test locaux reproductibles avec Vagrant et VirtualBox

!!! abstract "Résumé"
    Apprenez à automatiser la création et la configuration de machines virtuelles de test à l'aide de Vagrant et VirtualBox. Idéal pour monter rapidement des environnements de développement ou de TP (laboratoires).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Multiplateforme |
| Dernière mise à jour | 2026-06-17 |

## Contexte

Dans le cadre de l'apprentissage (TSSR, AIS) ou pour tester des architectures, il est fréquent d'avoir besoin de déployer plusieurs machines virtuelles (VMs). Créer ces VMs manuellement via l'interface graphique de VirtualBox est fastidieux, chronophage et sujet aux erreurs. Vagrant résout ce problème en permettant de définir l'infrastructure comme du code (Infrastructure as Code) via un simple fichier `Vagrantfile`.

## Prérequis

- **VirtualBox** installé sur votre machine hôte.
- **Vagrant** installé sur votre machine hôte (disponible sur Windows, macOS et Linux).
- Un terminal (PowerShell sous Windows, Bash/Zsh sous Linux/macOS).

## Procédure

### Étape 1 : Initialiser un projet Vagrant

Créez un dossier dédié à votre projet et initialisez la configuration Vagrant pour utiliser une image (box) Ubuntu 24.04 (Noble Numbat).

=== "Windows / Linux / macOS"

    ```bash
    mkdir mon-lab-vagrant
    cd mon-lab-vagrant
    vagrant init ubuntu/noble64
    ```

Cette commande génère un fichier `Vagrantfile` dans le répertoire courant. C'est ce fichier qui contient la recette de votre environnement.

### Étape 2 : Configurer le Vagrantfile

Ouvrez le fichier `Vagrantfile` avec votre éditeur de texte préféré (par exemple VS Code ou nano). Nous allons le modifier pour attribuer une adresse IP fixe à notre VM et lui allouer des ressources spécifiques (RAM, CPU).

Remplacez le contenu par :

```ruby title="Vagrantfile"
Vagrant.configure("2") do |config|
  # Définition du système d'exploitation (box)
  config.vm.box = "ubuntu/noble64"

  # Configuration réseau : attribution d'une IP privée statique
  config.vm.network "private_network", ip: "192.168.56.10"

  # Personnalisation des ressources VirtualBox
  config.vm.provider "virtualbox" do |vb|
    vb.name = "lab-ubuntu-srv"
    vb.memory = "1024" # 1 Go de RAM
    vb.cpus = 2        # 2 cœurs CPU
  end

  # Script de provisionning exécuté au premier démarrage
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y nginx
    echo "<h1>Serveur de test fonctionnel !</h1>" > /var/www/html/index.html
  SHELL
end
```

!!! tip "Provisionning"
    La section `config.vm.provision` permet d'exécuter des commandes automatiquement au premier démarrage de la VM. Ici, nous installons le serveur web Nginx.

### Étape 3 : Démarrer et provisionner la machine

Lancez la création et le démarrage de la VM. La première fois, Vagrant téléchargera l'image d'Ubuntu (cela peut prendre quelques minutes selon votre connexion).

```bash
vagrant up
```

Vagrant va créer la VM dans VirtualBox, configurer le réseau, partager automatiquement le dossier courant avec `/vagrant` dans la VM, et exécuter le script d'installation de Nginx.

### Étape 4 : Interagir avec la machine

Pour vous connecter à la machine virtuelle en SSH, rien de plus simple, Vagrant gère les clés pour vous :

```bash
vagrant ssh
```

Une fois connecté, vous pouvez vérifier que la machine tourne bien sous Ubuntu et explorer le système. Tapez `exit` pour revenir à votre machine hôte.

### Étape 5 : Gérer le cycle de vie de la VM

Voici les commandes essentielles pour contrôler votre VM au quotidien :

```bash
# Arrêter la VM proprement
vagrant halt

# Suspendre la VM (sauvegarder l'état)
vagrant suspend

# Redémarrer la VM (et appliquer un nouveau Vagrantfile si modifié)
vagrant reload

# Détruire la VM (supprime le disque et les ressources)
vagrant destroy
```

## Vérification

Une fois la VM démarrée avec `vagrant up`, ouvrez votre navigateur web et accédez à l'adresse IP définie :

**[http://192.168.56.10](http://192.168.56.10)**

!!! success "Résultat attendu"
    Vous devriez voir s'afficher une page blanche avec le texte "Serveur de test fonctionnel !", ce qui confirme que la VM est démarrée, que le réseau fonctionne et que le provisionning (Nginx) a bien été exécuté.

## Aide-mémoire

| Commande Vagrant | Description |
|------------------|-------------|
| `vagrant init <box>` | Initialise un nouveau projet avec l'image spécifiée |
| `vagrant up` | Démarre (et provisionne si première fois) la machine |
| `vagrant ssh` | Ouvre une session SSH sur la machine |
| `vagrant halt` | Éteint la machine |
| `vagrant destroy` | Supprime définitivement la machine |
| `vagrant status` | Affiche l'état actuel des VMs du projet |

## Ressources

- [Documentation officielle Vagrant](https://developer.hashicorp.com/vagrant/docs) — HashiCorp
- [Catalogue public des Vagrant Boxes](https://app.vagrantup.com/boxes/search) — HashiCorp
