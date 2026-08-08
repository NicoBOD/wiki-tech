---
icon: material/cloud
description: Notes sur Azure, AWS, GCP, Infrastructure as Code (Terraform, Bicep) et conteneurs.
---

# Cloud

Notes sur Azure, AWS, GCP, Infrastructure as Code (Terraform, Bicep) et conteneurs.

## Google Cloud Platform (GCP)

- [Déployer une application Docker sans serveur avec Google Cloud Run](deployer-application-docker-google-cloud-run.md) — Déploiement d'un conteneur avec gcloud, Artifact Registry et scale-to-zero.
- [Déployer PedagogIA sur Google Cloud Run + MongoDB Atlas](deploy-pedagogia-gcp.md) — Déploiement serverless, gestion stateless et intégration Cloud Storage.

## Stockage & synchronisation de fichiers

- [Synchroniser Google Drive sur deux postes Ubuntu avec rclone bisync et chiffrement Crypt](synchroniser-google-drive-rclone-bisync-crypt-deux-postes-ubuntu.md) — Synchronisation bidirectionnelle chiffrée côté client, Client ID OAuth dédié, automatisation systemd et pièges à éviter.

## Amazon Web Services (AWS)

- [Créer et déployer sa première fonction Serverless avec AWS Lambda](creer-deployer-premiere-fonction-serverless-aws-lambda.md) — Création, configuration et exécution de code Python sans serveur.
- [Sécuriser son compte AWS : les bases d'IAM (Identity and Access Management)](securiser-compte-aws-bases-iam.md) — Protéger le compte racine avec MFA et créer des accès administrateurs délégués.
- [Créer et configurer sa première machine virtuelle EC2 sur AWS](creer-premiere-machine-virtuelle-ec2-aws.md) — Lancer et configurer une instance Ubuntu EC2, règles de sécurité, et accès SSH sur AWS.
- [Déployer un site web statique avec Amazon S3](deployer-site-web-statique-amazon-s3.md) — Hébergement serverless, configuration de bucket policy et accès public.
- [Déployer un stockage objet S3-compatible avec MinIO en auto-hébergé](mettre-en-place-minio-stockage-objet-s3-compatible-auto-heberge.md) — Stockage d'objets S3-compatible (ex. MinIO) en local ou sur VM, compatible API S3 pour les applications cloud-native.

## Cloud-Init & Provisioning

- [Personnaliser une VM Ubuntu au premier démarrage avec cloud-init et NoCloud](personnaliser-vm-ubuntu-cloud-init-nocloud.md) — Utiliser la méthode NoCloud pour amorcer une VM sans serveur de métadonnées.

## Microsoft Azure

- [Créer et configurer sa première machine virtuelle sur Microsoft Azure](creer-premiere-machine-virtuelle-azure.md) — Lancer une instance Ubuntu, ouvrir des ports et s'y connecter via Azure CLI.
- [Déployer un conteneur via Azure Container Instances (ACI)](deployer-conteneur-azure-container-instances-aci.md) — Déployer rapidement une image Docker serverless avec la ligne de commande Azure.
- [Stocker et partager des fichiers dans Azure Blob Storage](stocker-partager-fichiers-azure-blob-storage.md) — Créer un compte de stockage, uploader et télécharger des blobs, puis générer un lien de partage temporaire avec un jeton SAS.
- [Mettre en place une surveillance centralisée avec Prometheus et Grafana pour infrastructure cloud hybride](mettre-en-place-surveillance-centralisee-prometheus-grafana-cloud-hybride.md) — Tutoriel complet pour installer et configurer une stack de monitoring open-source (Prometheus, Node Exporter, Grafana) avec intégration cloud (AWS, Azure, GCP).
