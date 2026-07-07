---
title: Créer un réseau privé virtuel (VPC) isolé et sécurisé sur AWS
date: 2026-06-10
author: Nicolas BODAINE
tags:
  - aws
  - vpc
  - reseau
  - cloud
difficulty: intermédiaire
os: AWS
status: publié
---

# Créer un réseau privé virtuel (VPC) isolé et sécurisé sur AWS

!!! abstract "Résumé"
    Dans AWS, un Virtual Private Cloud (VPC) vous permet de lancer des ressources dans un réseau virtuel isolé que vous définissez. Ce tutoriel montre comment créer un VPC de zéro avec des sous-réseaux publics et privés, une passerelle Internet et des tables de routage appropriées en utilisant l'AWS CLI, une étape fondamentale pour l'infrastructure cloud.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | AWS CLI |
| Dernière mise à jour | 2026-06-10 |

## Contexte

Par défaut, AWS fournit un VPC par défaut dans chaque région. Bien que pratique pour des tests rapides, il ne respecte pas les bonnes pratiques de sécurité et de conception pour un environnement de production. Il est essentiel de savoir créer son propre VPC avec une ségrégation réseau (sous-réseaux publics pour les ressources exposées comme les Load Balancers, et sous-réseaux privés pour les bases de données et backends).

## Prérequis

- Un compte **AWS** actif.
- L'outil **AWS CLI** installé et configuré (`aws configure`) avec des droits d'administrateur.
- Le processeur JSON `jq` installé sur votre machine pour faciliter l'extraction d'identifiants.

## Procédure

### Étape 1 : Créer le VPC

Nous allons créer un VPC avec le bloc CIDR `10.0.0.0/16`.

```bash
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=MonVPC_Securise}]' \
  --query 'Vpc.VpcId' --output text)

echo "VPC créé : $VPC_ID"
```

### Étape 2 : Créer les sous-réseaux (Subnets)

Nous créons un sous-réseau public (pour les ressources accessibles depuis Internet) et un sous-réseau privé (pour les ressources isolées).

**Sous-réseau public (10.0.1.0/24) :**
```bash
SUBNET_PUBLIC_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Subnet_Public}]' \
  --query 'Subnet.SubnetId' --output text)

echo "Subnet Public : $SUBNET_PUBLIC_ID"
```

**Sous-réseau privé (10.0.2.0/24) :**
```bash
SUBNET_PRIVATE_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Subnet_Prive}]' \
  --query 'Subnet.SubnetId' --output text)

echo "Subnet Privé : $SUBNET_PRIVATE_ID"
```

### Étape 3 : Créer et attacher une passerelle Internet (Internet Gateway)

Pour que le sous-réseau public puisse communiquer avec Internet, nous devons créer une Internet Gateway (IGW) et l'attacher au VPC.

```bash
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=MonIGW}]' \
  --query 'InternetGateway.InternetGatewayId' --output text)

aws ec2 attach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID

echo "Passerelle Internet attachée : $IGW_ID"
```

### Étape 4 : Configurer la table de routage publique

AWS crée une table de routage par défaut (principale) avec le VPC. Nous allons créer une nouvelle table de routage spécifique pour le réseau public, y ajouter une route vers Internet, puis l'associer au sous-réseau public.

```bash
RTB_PUBLIC_ID=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Table_Routage_Publique}]' \
  --query 'RouteTable.RouteTableId' --output text)

# Ajouter la route vers Internet via la passerelle
aws ec2 create-route \
  --route-table-id $RTB_PUBLIC_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

# Associer la table de routage au sous-réseau public
aws ec2 associate-route-table \
  --route-table-id $RTB_PUBLIC_ID \
  --subnet-id $SUBNET_PUBLIC_ID

echo "Routage public configuré."
```

*(Optionnel)* : Pour un environnement de production complet, on ajouterait une **Passerelle NAT (NAT Gateway)** dans le sous-réseau public pour permettre aux instances du sous-réseau privé de télécharger des mises à jour, sans être exposées sur Internet.

## Vérification

Pour vérifier la création de votre VPC et de ses composants, vous pouvez utiliser la commande suivante qui liste les VPC :

```bash
aws ec2 describe-vpcs --vpc-ids $VPC_ID
```

!!! success "Résultat attendu"
    La commande doit retourner les détails du VPC nouvellement créé, avec l'état `available` et le CIDR `10.0.0.0/16`. Les ressources déployées dans le sous-réseau privé (`10.0.2.0/24`) seront dorénavant inaccessibles depuis Internet.

## Nettoyage (Clean-up)

Si vous faisiez seulement un test, n'oubliez pas de supprimer vos ressources pour éviter tout frais éventuel futur (bien que les VPC eux-mêmes soient gratuits, certaines ressources comme les NAT Gateways sont facturées).

```bash
aws ec2 delete-subnet --subnet-id $SUBNET_PRIVATE_ID
aws ec2 delete-subnet --subnet-id $SUBNET_PUBLIC_ID
aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID
aws ec2 delete-route-table --route-table-id $RTB_PUBLIC_ID
aws ec2 delete-vpc --vpc-id $VPC_ID
```

## Ressources

- [Documentation officielle AWS - Fonctionnement des VPC](https://docs.aws.amazon.com/fr_fr/vpc/latest/userguide/how-it-works.html) — Présentation des concepts fondamentaux.
- [AWS Skill Builder - AWS Cloud Practitioner](https://skillbuilder.aws/exam-prep/cloud-practioner) — Formation gratuite incluant les bases du réseau AWS.
