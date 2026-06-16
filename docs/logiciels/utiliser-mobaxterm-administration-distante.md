---
title: Découvrir et utiliser MobaXterm pour l'administration distante
date: 2026-06-16
author: Nicolas BODAINE
tags:
  - ssh
  - sftp
  - windows
  - administration
difficulty: débutant
os: Windows
status: publié
---

# Découvrir et utiliser MobaXterm pour l'administration distante

!!! abstract "Résumé"
    MobaXterm est un terminal amélioré pour Windows doté d'un serveur X11, d'un client SSH à onglets, et de nombreux outils réseaux indispensables. Ce tutoriel montre comment l'installer et le configurer pour se connecter et administrer des serveurs distants efficacement.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Windows |
| Dernière mise à jour | 2026-06-16 |

## Contexte

Lorsque l'on administre des serveurs Linux depuis un poste de travail sous Windows, on a souvent besoin de cumuler plusieurs outils : un client SSH (comme PuTTY), un client SFTP (comme WinSCP) ou encore un serveur X pour l'affichage graphique déporté (comme Xming). 

MobaXterm rassemble tous ces outils au sein d'une seule application portable et légère, ce qui en fait le couteau suisse idéal des administrateurs systèmes et réseaux sur Windows.

## Prérequis

- Un poste de travail sous **Windows**.
- Un serveur Linux distant (ou une machine virtuelle) accessible via SSH, dont vous connaissez l'adresse IP et les identifiants de connexion.

## Procédure

### Étape 1 : Téléchargement et installation

1. Rendez-vous sur le site officiel de MobaXterm : [https://mobaxterm.mobatek.net/](https://mobaxterm.mobatek.net/)
2. Allez dans la section **Download**.
3. Choisissez l'édition **Home Edition** (gratuite).
4. Téléchargez la version **Portable edition** (un simple fichier `.zip` sans installation) ou **Installer edition** (si vous préférez l'installer sur votre système).
5. Si vous avez choisi l'édition portable, extrayez l'archive et lancez l'exécutable `MobaXterm_Personal_X.X.exe`.

### Étape 2 : Créer une session SSH

La création de sessions sauvegardées permet de se reconnecter rapidement à ses serveurs sans retaper l'adresse et le port à chaque fois.

1. Dans la fenêtre principale de MobaXterm, cliquez sur le gros bouton **Session** en haut à gauche.
2. Une nouvelle fenêtre s'ouvre, cliquez sur le bouton **SSH**.
3. Remplissez les champs de l'onglet **Basic SSH settings** :
    - **Remote host** : l'adresse IP ou le nom de domaine de votre serveur.
    - **Specify username** : cochez la case et saisissez le nom d'utilisateur (ex: `root` ou `ubuntu`).
    - **Port** : laissez `22` (port par défaut) ou précisez le vôtre si vous l'avez modifié.
4. Cliquez sur **OK**.
5. MobaXterm ouvre alors la session et vous demande votre mot de passe (sauf si vous utilisez des clés SSH, voir onglet *Advanced SSH settings*). Une fois le mot de passe entré, MobaXterm vous proposera de le sauvegarder (pratique pour un poste sécurisé, à éviter sur un poste partagé).

### Étape 3 : Naviguer avec le panneau SFTP (Fichiers)

L'une des grandes forces de MobaXterm est d'intégrer automatiquement un navigateur de fichiers graphique !

1. Lorsque vous êtes connecté en SSH (dans l'onglet principal), observez la barre latérale gauche.
2. Le panneau **Sftp** est automatiquement synchronisé avec le répertoire courant de votre terminal.
3. Si vous tapez `cd /etc` dans le terminal, le panneau s'actualise pour afficher `/etc`.
4. Vous pouvez facilement transférer des fichiers :
    - **Glisser-déposer (Drag & Drop)** : prenez un fichier sur Windows et déposez-le dans le panneau SFTP pour l'envoyer sur le serveur.
    - Cliquez droit sur un fichier pour l'éditer, le supprimer ou en télécharger une copie sur votre poste.

!!! tip "Édition de fichiers à la volée"
    MobaXterm intègre un éditeur de texte léger (MobaTextEditor). Un double-clic sur un fichier de configuration distant dans le panneau SFTP permet de l'éditer directement sous Windows. À l'enregistrement, il est renvoyé automatiquement au serveur.

### Étape 4 : Utiliser des fonctionnalités avancées

- **Multi-exécution (Multi-execution)** : Cliquez sur le bouton "MultiExec" en haut. Ce que vous tapez dans un terminal sera répliqué dans tous les autres terminaux ouverts. Parfait pour mettre à jour plusieurs serveurs simultanément (ex: `apt update && apt upgrade`).
- **Terminal fractionné (Split view)** : Cliquez sur l'icône de disposition en haut à droite (Split) pour afficher deux ou quatre terminaux côte à côte sur un seul écran.
- **Macros** : L'onglet "Macros" dans le panneau latéral vous permet d'enregistrer une suite de commandes et de les rejouer en un seul clic.

## Vérification

Pour valider le bon fonctionnement global, assurez-vous de :

1. Pouvoir ouvrir la session SSH depuis l'arbre de sessions à gauche par un simple double-clic.
2. Télécharger un fichier texte depuis le serveur vers votre bureau Windows en utilisant le volet SFTP.

!!! success "Résultat attendu"
    La session s'ouvre rapidement, l'arbre de fichiers affiche le répertoire courant de l'utilisateur, et les transferts de fichiers s'opèrent de façon transparente.

## Ressources

- [Site officiel MobaXterm](https://mobaxterm.mobatek.net/) — Site de l'éditeur officiel, avec documentation (en anglais).
- [Documentation officielle PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/docs.html) — PuTTY étant le moteur SSH sous-jacent, ses concepts s'appliquent ici.
