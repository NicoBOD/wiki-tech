---
title: Installer et configurer Windows Terminal pour unifier ses environnements CLI (PowerShell, WSL, SSH)
date: 2026-06-19
author: Nicolas BODAINE
tags:
  - windows
  - wsl
  - powershell
  - ssh
  - cli
difficulty: débutant
os: Windows 10 / Windows 11
status: publié
---

# Installer et configurer Windows Terminal

!!! abstract "Résumé"
    Windows Terminal est un terminal moderne, rapide, efficace et puissant pour les utilisateurs des outils de ligne de commande sur Windows. Il rassemble dans une même fenêtre via des onglets vos différents environnements : PowerShell, l'Invite de commandes (cmd), le Sous-système Windows pour Linux (WSL), et même vos connexions SSH vers d'autres serveurs.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Windows 10 / Windows 11 |
| Dernière mise à jour | 2026-06-19 |

## Contexte

De nombreux administrateurs systèmes et développeurs sous Windows jonglent quotidiennement entre plusieurs fenêtres : une pour PowerShell, une pour WSL (Linux) et souvent un autre outil (comme PuTTY ou MobaXterm) pour le SSH. Windows Terminal permet de tout regrouper dans une interface unique, personnalisable et performante.

## Prérequis

- Un poste sous Windows 10 (version 1903 ou ultérieure) ou Windows 11.
- Une connexion Internet pour le téléchargement.
- Avoir activé ou installé WSL (optionnel, mais recommandé pour en tirer pleinement parti).

## Procédure

### Étape 1 : Installation de Windows Terminal

La méthode la plus simple est de passer par le Microsoft Store, ce qui garantit des mises à jour automatiques.

1. Ouvrez le **Microsoft Store** sur votre machine Windows.
2. Recherchez **Windows Terminal**.
3. Cliquez sur **Installer** ou **Obtenir**.

Si vous préférez la ligne de commande (via winget ou choco) :

=== "Winget (Recommandé)"

    ```powershell
    winget install --id Microsoft.WindowsTerminal -e
    ```

=== "Chocolatey"

    ```powershell
    choco install microsoft-windows-terminal
    ```

### Étape 2 : Configuration de base (Profils par défaut)

Une fois installé, lancez Windows Terminal.

1. Par défaut, il s'ouvre sur PowerShell.
2. Pour ouvrir un nouvel onglet, cliquez sur le bouton `+` ou utilisez le raccourci ++ctrl+shift+t++.
3. En cliquant sur la flèche `v` à côté du `+`, vous verrez les profils pré-configurés (PowerShell, Invite de commandes, Azure Cloud Shell, et vos distributions WSL installées comme Ubuntu).
4. Cliquez sur **Paramètres** (ou faites ++ctrl+,++).

Dans l'onglet **Démarrage**, vous pouvez définir :
- Le profil par défaut (celui qui s'ouvre avec le bouton `+`).
- Le comportement au démarrage (ouvrir un nouvel onglet, restaurer la session précédente).

### Étape 3 : Ajouter un profil SSH (Accès rapide à un serveur)

L'un des grands atouts est de pouvoir créer un profil pour se connecter directement à un serveur distant en SSH, sans avoir à taper la commande à chaque fois.

1. Allez dans les **Paramètres** de Windows Terminal (via la flèche `v`).
2. En bas à gauche, cliquez sur **Ajouter un nouveau profil**.
3. Choisissez **Nouveau profil vide**.
4. Configurez-le ainsi :
   - **Nom** : `Serveur Web (Ubuntu)` (par exemple).
   - **Ligne de commande** : `ssh utilisateur@adresse_ip_du_serveur`
   - **Icône** : Vous pouvez choisir une icône intégrée, ou laisser vide (une icône Tux s'affichera souvent pour les serveurs Linux).
5. Cliquez sur **Enregistrer**.

Désormais, un simple clic dans le menu déroulant ouvrira un onglet et lancera directement la connexion SSH vers ce serveur.

### Étape 4 : Personnalisation de l'apparence

Windows Terminal est hautement personnalisable. Dans les paramètres d'un profil (onglet **Apparence**), vous pouvez modifier :
- Le thème (sombre, clair).
- La police de caractères (très utile pour des polices avec ligatures comme *Caskaydia Cove Nerd Font*).
- L'opacité de l'arrière-plan (effet acrylique/translucide).

## Vérification

Pour vérifier que tout fonctionne, tentez de lancer plusieurs onglets en parallèle :

- ++ctrl+shift+1++ (Lance le 1er profil, par défaut PowerShell).
- ++ctrl+shift+2++ (Lance le 2ème profil).
- Ouvrez votre nouveau profil SSH depuis le menu déroulant.

!!! success "Résultat attendu"
    Vous devez avoir une seule fenêtre Windows Terminal contenant un onglet PowerShell, un onglet WSL et un onglet SSH, vous permettant de naviguer facilement de l'un à l'autre.

## Ressources

- [Documentation officielle Windows Terminal](https://learn.microsoft.com/fr-fr/windows/terminal/) — Microsoft Learn
- [Installer WSL](https://learn.microsoft.com/fr-fr/windows/wsl/install) — Microsoft Learn