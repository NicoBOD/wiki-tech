---
title: Déployer une base de données relationnelle managée (RDS PostgreSQL) sur AWS
date: 2026-06-13
author: Nicolas BODAINE
tags:
  - AWS
  - Cloud
  - PostgreSQL
  - Base de données
  - RDS
difficulty: intermédiaire
os: AWS
status: publié
---

# Déployer une base de données relationnelle managée (RDS PostgreSQL) sur AWS

!!! abstract "Résumé"
    Ce tutoriel explique comment créer et configurer une base de données relationnelle managée avec Amazon Relational Database Service (RDS) en utilisant le moteur PostgreSQL. Nous verrons comment configurer le réseau, les accès de sécurité, et comment s'y connecter depuis votre machine locale.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| Environnement | Console AWS |
| Dernière mise à jour | 2026-06-13 |

## Contexte

La gestion d'une base de données relationnelle en production peut être complexe (sauvegardes, mises à jour, haute disponibilité). AWS RDS (Relational Database Service) simplifie ce processus en offrant un service managé. Vous n'avez pas besoin de gérer le système d'exploitation ou l'installation du moteur de base de données. 

Dans ce guide, nous allons déployer une instance PostgreSQL au sein du niveau gratuit (Free Tier) d'AWS, afin de minimiser ou d'annuler les coûts d'apprentissage.

## Prérequis

- Un compte AWS actif.
- Un VPC (Virtual Private Cloud) configuré (vous pouvez utiliser le VPC par défaut).
- Un client PostgreSQL installé sur votre machine locale (comme `psql`, pgAdmin, ou DBeaver).

## Procédure

### Étape 1 : Accéder à Amazon RDS

1. Connectez-vous à la [Console de gestion AWS](https://console.aws.amazon.com/).
2. Dans la barre de recherche en haut, tapez **RDS** et cliquez sur le service.
3. Vérifiez la région AWS dans le coin supérieur droit (par exemple, *eu-west-3* pour Paris) et assurez-vous de créer la ressource dans la région de votre choix.

### Étape 2 : Créer la base de données

1. Sur le tableau de bord RDS, cliquez sur le bouton orange **Créer une base de données** (Create database).
2. Choisissez la méthode de création **Standard create**.
3. Dans la section *Options du moteur* (Engine options), sélectionnez **PostgreSQL**.
4. Laissez la version par défaut (souvent la dernière version stable prise en charge).
5. Dans la section *Modèles* (Templates), sélectionnez **Offre gratuite** (Free tier) pour éviter les frais lors de ce TP.

### Étape 3 : Paramètres de configuration (Settings)

Remplissez les informations d'identification de la base de données :

- **Identifiant de l'instance de base de données** (DB instance identifier) : `mon-tuto-postgres`
- **Nom d'utilisateur principal** (Master username) : `postgres` (par défaut)
- **Mot de passe principal** (Master password) : Choisissez un mot de passe fort (ex. `MonSuperMotDePasse!`) et confirmez-le.
  
!!! warning "Mémorisez votre mot de passe"
    AWS ne vous permettra pas de récupérer le mot de passe s'il est perdu (vous devrez le réinitialiser).

### Étape 4 : Configuration de l'instance et du stockage

- **Classe d'instance DB** : Laissée par défaut (`db.t3.micro` ou `db.t4g.micro` selon ce qui est couvert par le Free Tier).
- **Stockage** : 
  - Type : General Purpose SSD (gp2 ou gp3).
  - Taille allouée : 20 Go (le minimum pour le Free Tier).
  - Désactivez *Enable storage autoscaling* (Activer l'allocation automatique du stockage) pour éviter des frais imprévus si la base grossit sans surveillance.

### Étape 5 : Connectivité (Réseau et Sécurité)

La configuration réseau est cruciale pour pouvoir accéder à votre base :

1. **Virtual Private Cloud (VPC)** : Utilisez le *Default VPC*.
2. **Accès public** (Public access) : Sélectionnez **Oui** (Yes).
   > *Note : En production, on place généralement la base en accès privé (Non) et on s'y connecte via une machine relais (bastion) ou un tunnel VPN. Pour ce TP d'apprentissage, l'accès public facilite les tests.*
3. **Groupe de sécurité VPC** (VPC security group) : Sélectionnez *Create new* (Créer nouveau) et nommez-le `rds-public-sg`.
4. **Zone de disponibilité** : Aucune préférence.
5. **Port de la base de données** : Laissez la valeur par défaut de PostgreSQL : `5432`.

### Étape 6 : Lancer la création

1. Faites défiler jusqu'en bas, vous pouvez vérifier l'estimation mensuelle (qui devrait être de 0,00 $ si vous êtes éligible au Free Tier).
2. Cliquez sur **Créer une base de données** (Create database).

!!! tip "Patience"
    La création prend généralement entre 5 et 10 minutes. Vous verrez le statut *Creating* (Création en cours), puis *Backing up* (Sauvegarde en cours), et enfin *Available* (Disponible).

## Autoriser votre adresse IP (Security Group)

Même avec l'option "Accès public" activée, AWS bloque le trafic entrant par défaut via le pare-feu (Security Group).

1. Une fois l'instance *Available*, cliquez sur son nom (`mon-tuto-postgres`).
2. Dans l'onglet **Connectivité et sécurité**, repérez le point de terminaison (Endpoint). C'est l'URL de votre base. Copiez-la.
3. Dans la même section, sous *Groupes de sécurité VPC*, cliquez sur le groupe `rds-public-sg`.
4. Dans la fenêtre EC2 qui s'ouvre, sélectionnez l'onglet **Règles entrantes** (Inbound rules) en bas, puis cliquez sur **Modifier les règles entrantes**.
5. Ajoutez une règle :
   - Type : `PostgreSQL`
   - Protocole : `TCP`
   - Plage de ports : `5432`
   - Source : Sélectionnez **Mon IP** (My IP). Cela limitera l'accès à votre adresse IP actuelle.
6. Cliquez sur **Enregistrer les règles**.

## Vérification

Il est temps de se connecter à la base de données depuis votre machine locale.

=== "Terminal Linux / macOS (psql)"

    Assurez-vous d'avoir le client installé (`sudo apt install postgresql-client` sur Ubuntu) et exécutez :

    ```bash
    psql -h <VOTRE_ENDPOINT_RDS> -U postgres -d postgres -p 5432
    ```
    *Il vous sera demandé de saisir votre mot de passe. L'endpoint ressemble à `mon-tuto-postgres.xxxxx.eu-west-3.rds.amazonaws.com`.*

=== "Logiciel Graphique (ex: DBeaver)"

    1. Créez une nouvelle connexion **PostgreSQL**.
    2. **Host** : `<VOTRE_ENDPOINT_RDS>`
    3. **Port** : `5432`
    4. **Database** : `postgres`
    5. **Username** : `postgres`
    6. **Password** : Votre mot de passe.
    7. Cliquez sur *Test Connection*.

!!! success "Résultat attendu"
    Vous devriez obtenir un accès à l'invite de commande SQL `postgres=>` ou un test de connexion réussi sur votre interface graphique. Vous êtes prêt à exécuter vos requêtes !

## Nettoyage (Éviter les frais)

Si vous ne comptez plus utiliser cette base de données, n'oubliez pas de la supprimer :

1. Dans la console RDS, sélectionnez votre base de données.
2. Cliquez sur **Actions** > **Supprimer**.
3. Décochez la création de l'instantané final (Create final snapshot) pour gagner du temps et de l'espace.
4. Confirmez la suppression en tapant `delete me`.

## Ressources

- [Documentation officielle Amazon RDS pour PostgreSQL](https://docs.aws.amazon.com/fr_fr/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html) — Guide d'utilisation détaillé d'AWS.
- [Télécharger DBeaver](https://dbeaver.io/download/) — Outil universel de gestion de bases de données.
