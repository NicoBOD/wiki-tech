---
title: Déployer PedagogIA sur Google Cloud Run + MongoDB Atlas
date: 2026-05-02
author: Nicolas BODAINE
tags:
  - gcp
  - cloud-run
  - docker
  - mongodb
  - ia
difficulty: intermédiaire
os: Web
status: publié
---

# Déployer PedagogIA sur Google Cloud Run + MongoDB Atlas

!!! abstract "Résumé"
    Ce tutoriel explique comment déployer l'application open-source **PedagogIA** dans un environnement serverless gratuit et robuste à l'aide de Google Cloud Run. Il couvre la configuration de l'infrastructure stateless, l'intégration de MongoDB Atlas (Free Tier) et la sauvegarde des fichiers générés sur Google Cloud Storage.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| Composants | Google Cloud Run, Cloud Storage, Cloud Build, MongoDB Atlas |
| Dernière mise à jour | 2026-05-02 |

## Contexte

[PedagogIA](https://github.com/TutoTech/PedagogIA) est une application web auto-hébergeable de génération de contenus pédagogiques assistée par IA (Python/JS). Bien qu'elle tourne nativement sur Coolify (Docker avec état), le déploiement sur Google Cloud Run nécessite quelques adaptations en raison de la nature *stateless* (sans état) de l'environnement serverless. 

Les bases de données locales (MongoDB/SQLite) et l'enregistrement de fichiers sur le disque du conteneur ne survivent pas aux redémarrages sur Cloud Run. La solution consiste à déporter la base de données sur **MongoDB Atlas** et le stockage de fichiers (.pptx, images) sur **Google Cloud Storage (GCS)**.

## Prérequis

- Un compte [Google Cloud Platform (GCP)](https://console.cloud.google.com/) avec la facturation activée (nous resterons dans le Free Tier).
- Un compte [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register).
- Le code source de l'application sur un dépôt GitHub.
- API à activer sur GCP : *Cloud Run API*, *Cloud Build API*, *Artifact Registry API*.

## Procédure

### Étape 1 : Créer la base de données sur MongoDB Atlas

Cloud Run nécessitant une base de données externe, nous allons utiliser le tier gratuit de MongoDB.

1. Créez un nouveau cluster gratuit (**M0 Free Tier**) sur MongoDB Atlas.
2. Choisissez **Google Cloud (GCP)** comme fournisseur et sélectionnez votre région (ex: `europe-west1`).
3. Dans l'onglet **Network Access** (à gauche), ajoutez une IP Whitelist pour autoriser l'accès depuis Cloud Run (IP dynamiques) :
   - Adresse : `0.0.0.0/0`
4. Dans **Database Access**, créez un utilisateur et générez un mot de passe fort.
5. Cliquez sur **Connect** > **Drivers** et récupérez la chaîne de connexion (Connection String). Elle ressemblera à ceci :
   `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

### Étape 2 : Préparer le stockage persistant (Cloud Storage)

Les livrables générés par PedagogIA (fichiers PowerPoint, images) seraient perdus à chaque redémarrage de l'instance si sauvegardés localement.

1. Allez dans GCP > **Cloud Storage** > **Buckets**.
2. Créez un nouveau bucket (ex: `pedagogia-fichiers-generes`).
   !!! tip "Rester dans le Free Tier"
       Pour que les 5 Go soient 100% gratuits, vous devez absolument choisir le type d'emplacement **Région** et l'une de ces trois régions US : `us-central1`, `us-east1`, ou `us-west1`.
3. Décochez la protection contre l'accès public pour permettre au frontend d'afficher les URL.
4. Une fois créé, allez dans **Autorisations** > **Accorder l'accès** :
   - Nouveaux comptes : `allUsers`
   - Rôle : `Cloud Storage` > `Lecteur des objets de l'espace de stockage`

### Étape 3 : Adapter le code source (Cloud Build & GCS)

L'application doit être préparée pour le déploiement GCP. Créez une branche dédiée (ex: `google-cloud-run-deploy`).

1. **Port dynamique** : Dans votre `Dockerfile`, modifiez la commande de lancement `uvicorn` pour qu'elle utilise la variable dynamique `$PORT` imposée par Cloud Run.
2. **Intégration GCS** : Le backend Python doit intégrer le SDK `google-cloud-storage`. Au lieu d'écrire sur le disque, l'application doit détecter si la variable `GCS_BUCKET_NAME` existe et uploader le fichier vers Cloud Storage en utilisant l'authentification native de Cloud Run.

### Étape 4 : Déployer sur Google Cloud Run

1. Allez dans GCP > **Cloud Run** > **Créer un service**.
2. Choisissez **Déployer en continu à partir d'un dépôt**. Reliez votre compte GitHub et sélectionnez votre dépôt et la branche `google-cloud-run-deploy`.
3. Dans **Authentification**, cochez *Autoriser les appels non authentifiés* (pour que le site soit public).
4. Dépliez la section **Variables et secrets**. Ajoutez les variables d'environnement nécessaires au projet :
   - `MONGO_URL` : Votre chaîne de connexion Atlas (remplacez username/password, sans les chevrons `<>`).
   - `DB_NAME` : Le nom de la base de données.
   - `GCS_BUCKET_NAME` : Le nom de votre bucket (ex: `pedagogia-fichiers-generes`).
   - *Toutes les autres clés secrètes de l'application (JWT_SECRET, LLM APIs, etc.).*
5. Cliquez sur **Créer/Déployer**.

### Étape 5 : Domaine personnalisé gratuit (Optionnel)

Cloud Run permet d'attacher votre propre domaine (ex: `pedagogia.bodaine.fr`) avec génération de certificat SSL gratuite.

1. Dans Cloud Run, menu de gauche > **Mappages de domaines**.
2. Ajoutez un mappage pour votre service et validez votre domaine via Google Search Console.
3. Chez votre hébergeur DNS (OVH, Gandi...), créez une entrée :
   - Type : `CNAME`
   - Cible : `ghs.googlehosted.com.`
4. N'oubliez pas de mettre à jour la variable `FRONTEND_URL` de votre Cloud Run avec votre nouvelle URL HTTPS.

## Vérification

Comment vérifier que l'infrastructure fonctionne correctement :

1. Ouvrez l'URL publique de votre service Cloud Run.
2. Connectez-vous, générez un contenu pédagogique et un livrable final (.pptx).
3. Cliquez sur le bouton de téléchargement. L'URL cible doit pointer vers `storage.googleapis.com/MON_BUCKET/...`.

!!! success "Résultat attendu"
    L'application charge rapidement, le livrable est généré via l'IA, sauvegardé en ligne et le téléchargement démarre immédiatement.

## Problème courant

!!! failure "Default STARTUP TCP probe failed 1 time consecutively... Connection failed with status CANCELLED."
    Ce message générique s'affiche souvent au premier déploiement dans les logs Cloud Run.

**Solution**
Cela signifie que l'application a "planté" en silence avant de pouvoir ouvrir le port 8080.
1. Allez dans *Explorateur de journaux* (Logs Explorer).
2. **Supprimez le filtre `severity="ERROR"`** de la barre de recherche. Python logue souvent ses crashs sous forme de texte classique (`INFO` ou `DEFAULT`).
3. Cherchez la ligne `Traceback`. Si le processus reste bloqué indéfiniment, vérifiez la configuration IP `0.0.0.0/0` sur le firewall MongoDB Atlas.

## Ressources

- [Documentation Google Cloud Run](https://cloud.google.com/run/docs)
- [MongoDB Atlas - Network Access](https://www.mongodb.com/docs/atlas/security-add-ip-address/)
- [Dépôt TutoTech/PedagogIA](https://github.com/TutoTech/PedagogIA)