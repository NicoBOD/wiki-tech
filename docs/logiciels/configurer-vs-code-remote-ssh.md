---
title: Configurer VS Code avec Remote-SSH pour administrer un serveur Linux
date: 2026-06-12
author: Nicolas BODAINE
tags:
  - vscode
  - ssh
  - administration
  - linux
difficulty: débutant
os: Windows / macOS / Linux (Client) & Linux (Serveur)
status: publié
---

# Configurer VS Code avec Remote-SSH pour administrer un serveur Linux

!!! abstract "Résumé"
    Apprenez à configurer et utiliser l'extension Remote-SSH de Visual Studio Code pour administrer, développer et modifier des fichiers directement sur un serveur Linux distant, tout en profitant du confort d'une interface graphique moderne sur votre poste de travail.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Windows / macOS / Linux (Client) & Linux (Serveur) |
| Dernière mise à jour | 2026-06-12 |

## Contexte

La gestion de serveurs Linux passe traditionnellement par un terminal en ligne de commande (via SSH) et l'utilisation d'éditeurs texte tels que Nano ou Vim. S'ils sont indispensables à maîtriser, l'édition prolongée de fichiers de configuration, de scripts d'automatisation ou de code directement sur le serveur peut être fastidieuse pour un administrateur ou un développeur débutant.

Visual Studio Code, couplé à l'extension **Remote - SSH** développée par Microsoft, permet de se connecter à un serveur Linux distant tout en ayant accès à une interface graphique complète : explorateur de fichiers, édition multi-onglets, coloration syntaxique, terminal intégré, etc. Vous travaillez en local, mais toutes les commandes et modifications sont exécutées sur le serveur.

## Prérequis

- Un poste de travail avec **Visual Studio Code** installé.
- Un **client SSH** installé sur votre poste de travail (inclus par défaut dans Windows 10/11, macOS et Linux).
- Un serveur distant ou une machine virtuelle (VM) sous Linux (ex: Ubuntu Server ou Debian) avec le service **OpenSSH Server** actif.
- Les identifiants (utilisateur et mot de passe, ou clé SSH) pour se connecter au serveur Linux.

## Procédure

### Étape 1 : Installer l'extension Remote - SSH

Sur votre poste de travail où VS Code est installé :

1. Ouvrez Visual Studio Code.
2. Cliquez sur l'icône **Extensions** dans la barre latérale gauche (ou utilisez le raccourci clavier ++ctrl+shift+x++).
3. Dans la barre de recherche, tapez `Remote - SSH`.
4. Sélectionnez l'extension développée par **Microsoft** et cliquez sur **Installer**.

### Étape 2 : Configurer la connexion SSH

L'extension permet d'enregistrer des hôtes afin de ne pas retaper les paramètres de connexion à chaque fois.

1. Cliquez sur la nouvelle icône **Remote Explorer** (Explorateur distant) apparue dans la barre latérale gauche (généralement symbolisée par un écran d'ordinateur).
2. Dans le panneau *Remotes (Tunnels/SSH)*, cliquez sur le symbole **+** (New Remote).
3. Une barre de saisie apparaît en haut. Entrez la commande SSH complète, par exemple :
   ```bash
   ssh utilisateur@adresse_ip_du_serveur
   ```
4. Appuyez sur ++enter++. VS Code vous demande alors quel fichier de configuration mettre à jour. Choisissez le premier de la liste (souvent `~/.ssh/config` sous Linux/macOS ou `C:\Users\VotreNom\.ssh\config` sous Windows).
5. Une notification apparaît en bas à droite : cliquez sur **Connect**.

### Étape 3 : Se connecter au serveur distant

Lors de la toute première connexion à un serveur, VS Code a besoin d'installer un petit composant serveur.

1. Si VS Code vous demande le type de plateforme du serveur distant, sélectionnez **Linux**.
2. Il vous demandera ensuite si vous faites confiance à l'empreinte de l'hôte (fingerprint). Cliquez sur **Continue**.
3. Saisissez le mot de passe de votre utilisateur distant (si vous n'utilisez pas l'authentification par clé SSH).
4. Patientez quelques instants pendant que VS Code télécharge et installe le "VS Code Server" sur la machine distante.
5. Une fois connecté, un badge vert en bas à gauche de la fenêtre VS Code affichera `SSH: adresse_ip_du_serveur`.

### Étape 4 : Utiliser l'explorateur et le terminal intégré

Maintenant que vous êtes connecté :

1. Allez dans l'onglet **Explorateur** (la première icône dans la barre latérale gauche).
2. Cliquez sur **Ouvrir le dossier** (Open Folder). Vous naviguez maintenant dans le système de fichiers du serveur Linux. Par défaut, il propose votre dossier personnel (`/home/utilisateur`). Validez en cliquant sur **OK**.
3. Vous pouvez désormais créer, éditer et supprimer des fichiers directement sur le serveur via l'interface graphique.
4. Ouvrez un terminal intégré en cliquant sur **Affichage** > **Terminal** (ou via ++ctrl+j++ ou l'utilisation du raccourci clavier associé). Ce terminal n'est pas celui de votre machine physique, mais bien une invite de commande SSH directement connectée à votre serveur.

## Vérification

Pour confirmer que vous êtes bien sur le serveur distant et non sur votre poste local :

1. Ouvrez le terminal intégré de VS Code.
2. Tapez la commande suivante pour afficher les informations de l'OS :

```bash
cat /etc/os-release
```

!!! success "Résultat attendu"
    Vous devez voir s'afficher les informations de votre système Linux (par exemple `PRETTY_NAME="Ubuntu 24.04 LTS"`), et non celles de votre propre ordinateur de travail. Les modifications apportées aux fichiers depuis l'explorateur sont appliquées instantanément sur le serveur distant.

## Ressources

- [Documentation officielle Microsoft : Remote Development using SSH](https://code.visualstudio.com/docs/remote/ssh) — Guide complet sur l'utilisation avancée du plugin Remote-SSH (en anglais).
