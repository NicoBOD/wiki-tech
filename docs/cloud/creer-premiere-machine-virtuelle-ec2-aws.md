---
title: Créer et configurer sa première machine virtuelle EC2 sur AWS
date: 2026-06-22
author: Nicolas BODAINE
tags:
  - aws
  - ec2
  - cloud
  - vm
  - ubuntu
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# Créer et configurer sa première machine virtuelle EC2 sur AWS

!!! abstract "Résumé"
    Ce tutoriel explique étape par étape comment lancer et configurer une première machine virtuelle (instance EC2) sur le cloud Amazon Web Services (AWS). Il couvre la création de l'instance, la configuration du pare-feu (Security Group) et la connexion SSH. Idéal pour les étudiants et professionnels IT débutant sur le cloud public.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | AWS / Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-22 |

## Contexte

Dans le cloud AWS, le service fournissant des machines virtuelles s'appelle **Amazon EC2** (*Elastic Compute Cloud*). Le lancement d'une instance EC2 est souvent la première étape pour déployer une application, héberger un serveur web ou réaliser des tests dans le cloud. Ce guide vise à démystifier ce processus via la console d'administration AWS (interface web).

## Prérequis

- Un compte **AWS** actif (le *Free Tier* ou "Niveau gratuit" suffit pour ce tutoriel).
- Un terminal avec un client SSH installé (disponible nativement sous Linux, macOS et Windows 10/11).
- (Optionnel) Une clé SSH locale générée avec `ssh-keygen`. Nous utiliserons ici AWS pour générer la paire de clés.

## Procédure

### Étape 1 : Accéder au tableau de bord EC2

1. Connectez-vous à la [Console de gestion AWS](https://console.aws.amazon.com/).
2. Dans la barre de recherche supérieure, tapez `EC2` et cliquez sur le service **EC2**.
3. Assurez-vous d'être dans la bonne **Région** (en haut à droite, par exemple `Paris - eu-west-3`).
4. Dans le panneau latéral gauche ou sur le tableau de bord, cliquez sur **Instances**, puis sur le bouton orange **Lancer des instances** (Launch instances).

### Étape 2 : Configurer les paramètres de base de l'instance

1. **Nom et balises** : Donnez un nom à votre serveur (ex: `Web-Server-Test`).
2. **Images d'application et de système d'exploitation (AMI)** :
   Sélectionnez **Ubuntu**, et choisissez la version `Ubuntu Server 24.04 LTS (HVM), SSD Volume Type`. Assurez-vous que la mention *Admissible à l'offre gratuite* (Free tier eligible) soit présente.
3. **Type d'instance** :
   Laissez par défaut `t2.micro` (ou `t3.micro` selon la région). Ces types incluent 1 vCPU et 1 Go de RAM, et sont éligibles à l'offre gratuite.

### Étape 3 : Créer ou sélectionner une paire de clés SSH

Pour vous connecter en toute sécurité à l'instance, AWS utilise des clés SSH au lieu de mots de passe.

1. Dans la section **Paire de clés (connexion)**, cliquez sur **Créer une nouvelle paire de clés**.
2. Nommez-la (ex: `cle-aws-perso`).
3. Choisissez le type **RSA** et le format de fichier privé **.pem**.
4. Cliquez sur **Créer une paire de clés**.
5. **Important :** Le fichier `.pem` va se télécharger automatiquement sur votre ordinateur. Rangez-le dans un dossier sécurisé (ex: `~/.ssh/`).

### Étape 4 : Configurer le réseau et la sécurité (Security Group)

Dans la section **Paramètres réseau**, cliquez sur **Modifier** pour afficher tous les détails.

1. **Réseau (VPC)** et **Sous-réseau** : Laissez les valeurs par défaut.
2. **Attribuer automatiquement une adresse IP publique** : Laissez sur *Activer*.
3. **Pare-feu (groupes de sécurité)** :
   Sélectionnez *Créer un groupe de sécurité*. Nommez-le (ex: `sg-web-ssh`).
4. Ajoutez les règles suivantes pour autoriser le trafic entrant :
   - **Type** : `SSH` | **Port** : `22` | **Source** : `N'importe où` (0.0.0.0/0) ou idéalement `Mon adresse IP` (pour plus de sécurité).
   - Cliquez sur **Ajouter une règle de groupe de sécurité** :
   - **Type** : `HTTP` | **Port** : `80` | **Source** : `N'importe où` (0.0.0.0/0).

### Étape 5 : Lancer l'instance

1. Dans le panneau de droite (Résumé), vérifiez vos paramètres.
2. Laissez le stockage par défaut (souvent 8 Go de volume EBS General Purpose).
3. Cliquez sur le bouton orange **Lancer l'instance**.
4. Cliquez sur l'ID de l'instance (ex: `i-0abcd1234efgh5678`) pour retourner au tableau de bord. Attendez que l'état de l'instance passe de *En attente* (Pending) à **En cours d'exécution** (Running).

## Connexion et Vérification

Maintenant que la machine tourne, connectons-nous en SSH.

1. Sélectionnez votre instance dans la liste et trouvez l'**Adresse IPv4 publique** dans l'onglet *Détails* en bas.
2. Ouvrez votre terminal.
3. Restreignez les droits du fichier de clé téléchargé (obligatoire sous Linux/macOS) :
   ```bash
   chmod 400 ~/.ssh/cle-aws-perso.pem
   ```
4. Connectez-vous avec l'utilisateur par défaut d'Ubuntu (`ubuntu`) :
   ```bash
   ssh -i ~/.ssh/cle-aws-perso.pem ubuntu@VOTRE_ADRESSE_IP_PUBLIQUE
   ```

!!! success "Résultat attendu"
    Vous devriez voir l'invite de commande d'Ubuntu confirmant votre connexion :
    `ubuntu@ip-172-31-xx-xx:~$`

## Ressources

- [Documentation officielle Amazon EC2](https://docs.aws.amazon.com/ec2/) — Guide complet d'AWS.
- [Tarification de l'offre gratuite AWS](https://aws.amazon.com/fr/free/) — Détails sur les limites du Free Tier.
