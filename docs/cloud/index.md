---
icon: material/cloud
description: Notes sur Azure, AWS, GCP, Infrastructure as Code (Terraform, Bicep) et conteneurs.
---

# Cloud

Notes sur Azure, AWS, GCP, Infrastructure as Code (Terraform, Bicep) et conteneurs.

## Google Cloud Platform (GCP)

- [Déployer une application Docker sans serveur avec Google Cloud Run](deployer-application-docker-google-cloud-run.md) — Déploiement d'un conteneur avec gcloud, Artifact Registry et scale-to-zero.
- [Déployer PedagogIA sur Google Cloud Run + MongoDB Atlas](deploy-pedagogia-gcp.md) — Déploiement serverless, gestion stateless et intégration Cloud Storage.

## Amazon Web Services (AWS)

- [Sécuriser son compte AWS : les bases d'IAM (Identity and Access Management)](securiser-compte-aws-bases-iam.md) — Protéger le compte racine avec MFA et créer des accès administrateurs délégués.
- [Créer et configurer sa première machine virtuelle EC2 sur AWS](creer-premiere-machine-virtuelle-ec2-aws.md) — Lancer et configurer une instance Ubuntu EC2, règles de sécurité, et accès SSH sur AWS.
- [Créer une alerte de facturation sur AWS (AWS Budgets) pour sécuriser ses travaux pratiques](creer-alerte-facturation-aws-budgets.md) — Configurer un budget pour recevoir une notification par email avant que les coûts n'explosent.
- [Configurer et utiliser AWS CLI pour interagir avec les services Amazon Web Services](installer-configurer-aws-cli.md) — Configurer les accès, profils et informations d'identification pour interagir avec AWS en ligne de commande.
- [Créer un réseau privé virtuel (VPC) isolé et sécurisé sur AWS](creer-vpc-isole-securise-aws.md) — Concevoir une architecture réseau de zéro (VPC, Subnets, IGW) avec AWS CLI.
- [Déployer une base de données relationnelle managée (RDS PostgreSQL) sur AWS](deployer-base-de-donnees-rds-postgresql-aws.md) — Créer et configurer une instance PostgreSQL managée sur le Free Tier avec accès réseau sécurisé.
- [Déployer un site web statique avec Amazon S3](deployer-site-web-statique-amazon-s3.md) — Hébergement serverless, configuration de bucket policy et accès public.

## Cloud-Init & Provisioning

- [Personnaliser une VM Ubuntu au premier démarrage avec cloud-init et NoCloud](personnaliser-vm-ubuntu-cloud-init-nocloud.md) — Utiliser la méthode NoCloud pour amorcer une VM sans serveur de métadonnées.

## Microsoft Azure

- [Déployer un conteneur via Azure Container Instances (ACI)](deployer-conteneur-azure-container-instances-aci.md) — Déployer rapidement une image Docker serverless avec la ligne de commande Azure.
