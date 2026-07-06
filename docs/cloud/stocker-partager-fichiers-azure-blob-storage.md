---
title: Stocker et partager des fichiers dans Azure Blob Storage
date: 2026-07-06
author: Nicolas BODAINE
tags:
  - azure
  - cloud
  - stockage
  - blob
difficulty: débutant
os: Linux / Azure CLI
status: publié
---

# Stocker et partager des fichiers dans Azure Blob Storage

!!! abstract "Résumé"
    Azure Blob Storage est le service de stockage d'objets (object storage) de Microsoft Azure, conçu pour conserver de gros volumes de données non structurées (images, vidéos, sauvegardes, journaux, documents). Ce tutoriel explique pas à pas comment créer un compte de stockage, y déposer des fichiers (« blobs »), les télécharger, puis générer un lien de partage temporaire et sécurisé (jeton SAS). Toutes les manipulations sont réalisées en ligne de commande avec **Azure CLI**, entièrement reproductibles dans un environnement de travaux pratiques.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux (Ubuntu) / Azure CLI |
| Dernière mise à jour | 2026-07-06 |

## Contexte

Le besoin de stocker et de partager des fichiers est constant en informatique : sauvegardes automatisées, livrables d'un projet, logs archivés, images servies sur un site web, etc. Sur un serveur local, on mettrait un simple disque ou un dossier NFS. Dans le cloud, on parle de **stockage objet** (object storage) : chaque fichier devient un « blob » (Binary Large Object), identifié par une URL, accessible via HTTP, et non rattaché à un système de fichiers classique.

Azure Blob Storage présente plusieurs avantages majeurs :

- **Évolutivité** : on ne provisionne pas de taille de disque, on paie ce que l'on consomme.
- **Durabilité** : Azure réplique automatiquement les données.
- **Accessibilité** : chaque blob est exposé par une URL HTTP(S).
- **Partage temporaire** : un jeton SAS (Shared Access Signature) permet de donner un accès limité dans le temps, sans partager la clé du compte.

Ce lab reproduit une situation courante : un administrateur ou un développeur doit archiver des fichiers puis en partager un collègue via un lien temporaire.

!!! info "Vocabulaire : Blob Storage"
    Un *blob* est l'unité de fichier dans Azure Blob Storage. Le dossier qui les regroupe s'appelle un *conteneur* (container). Le *compte de stockage* (storage account) est la ressource racine qui contient les conteneurs et expose les clés d'accès.

## Prérequis

- Un compte Microsoft Azure avec une souscription active (crédit gratuit suffisant *[Visualisez les conditions du compte gratuit Azure]*¹).
- L'outil en ligne de commande **Azure CLI** (`az`) installé sur un terminal Linux.
- Environ **100 Mo** de fichiers à uploader pour le test.

¹ Azure propose un crédit gratuit pour démarrer (avec une limite mensuelle gratuite). Vérifiez l'éligibilité de votre abonnement avant de démarrer.

## Procédure

### Étape 1 : Installer Azure CLI et se connecter

Si Azure CLI n'est pas encore installé :

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Vérifiez l'installation :

```bash
az version --output table
```

Authentifiez-vous sur votre compte Azure :

```bash
az login
```

!!! note "Connexion au navigateur"
    Cette commande ouvre votre navigateur par défaut pour rechercher votre identité Microsoft. Revenez dans le terminal une fois authentifié : la liste des abonnements s'affiche.

Vérifiez enfin l'abonnement actif (si vous en avez plusieurs) :

```bash
az account show --output table
```

### Étape 2 : Créer un groupe de ressources

Comme toute ressource Azure, le compte de stockage doit être rangé dans un **groupe de ressources** (conteneur logique de facturation et de cycle de vie).

```bash
az group create \
  --name rg-tuto-blob \
  --location francecentral
```

> **Choix de la région :** `francecentral` correspond au datacenter Azure de Paris. Pour des TP destinés à un public francophone européen, c'est souvent la meilleure option (RUP/GDPR, faible latence Europe).

### Étape 3 : Créer le compte de stockage

Le compte de stockage doit avoir un **nom globalement unique** (3 à 24 caractères, lettres minuscules et chiffres uniquement) car il apparaîtra dans l'URL des blobs (`https://<compte>.blob.core.windows.net`).

Pour ne pas se soucier du nom, on génère un suffixe aléatoire concaténé à un préfixe stable :

```bash
STORAGE_NAME="labblobstorage$RANDOM"

az storage account create \
  --name "$STORAGE_NAME" \
  --resource-group rg-tuto-blob \
  --location francecentral \
  --sku Standard_LRS \
  --kind StorageV2
```

Expliquons les paramètres :

- `--sku Standard_LRS` : niveau de performance *Standard* avec réplication *Locally Redundant Storage* (3 copies dans un même datacenter). Suffisant et économique pour un lab.
- `--kind StorageV2` : type de compte moderne, supporte tous les types de blobs (block, append, page).

!!! tip "Reprendre le nom du compte"
    Pensez à garder la valeur de `$STORAGE_NAME` dans votre session. On en aura besoin pour toutes les étapes suivantes. Si vous avez fermé le terminal, retrouvez-la avec :

    ```bash
    az storage account list \
      --resource-group rg-tuto-blob \
      --query "[].name" \
      --output tsv
    ```

### Étape 4 : Créer un conteneur

Un **conteneur** est l'équivalent d'un dossier racine dans le compte de stockage. Les blobs y sont rangés. Créons-en un nommé `documents`, à accès privé (seul le propriétaire du compte peut lire les blobs — l'accès public sera délégué via un jeton SAS plus loin).

```bash
az storage container create \
  --name documents \
  --account-name "$STORAGE_NAME" \
  --auth-mode login
```

!!! note "Mode d'authentification"
    Le paramètre `--auth-mode login` indique à Azure CLI d'utiliser votre identité connectée (Entra ID) plutôt que la clé de compte (`--account-key`). C'est la méthode recommandée en production (RBAC). Pour un lab basique, on peut aussi récupérer la clé primaire avec `az storage account keys list`.

Listons les conteneurs pour confirmer :

```bash
az storage container list \
  --account-name "$STORAGE_NAME" \
  --auth-mode login \
  --output table
```

### Étape 5 : Uploader un fichier (créer un blob)

Téléchargeons un fichier de test, puis uploaderons-le dans le conteneur `documents`. Procurez-vous n'importe quel fichier ; pour ce lab, on génère un simple fichier texte :

```bash
# Créer un fichier de test local
cat > notes.md <<'EOF'
# Notes de travaux pratiques
- TP Azure Blob Storage
- Date : 2026-07-06
EOF
```

Uploadons ce fichier en tant que blob dans le conteneur :

```bash
az storage blob upload \
  --account-name "$STORAGE_NAME" \
  --container-name documents \
  --name notes.md \
  --file notes.md \
  --auth-mode login \
  --overwrite
```

Vérifions l'inventaire du conteneur :

```bash
az storage blob list \
  --account-name "$STORAGE_NAME" \
  --container-name documents \
  --auth-mode login \
  --output table
```

!!! success "Résultat attendu"
    Le tableau liste votre blob `notes.md` avec sa taille et son type de blob (`BlockBlob`).

### Étape 6 : Télécharger un blob

La commande symétrique permet de récupérer un blob vers votre machine locale :

```bash
az storage blob download \
  --account-name "$STORAGE_NAME" \
  --container-name documents \
  --name notes.md \
  --file notes-recupere.md \
  --auth-mode login
```

Vérifiez le contenu :

```bash
cat notes-recupere.md
```

### Étape 7 : Partager un blob via un jeton SAS

Plutôt que de faire l'erreur de basculer le conteneur en accès public, on génère un **jeton SAS** (Shared Access Signature) : une URL temporaire et signée qui autorise la lecture du fichier pendant une durée limitée, sans partager de clé.

```bash
az storage blob generate-sas \
  --account-name "$STORAGE_NAME" \
  --container-name documents \
  --name notes.md \
  --permissions r \
  --expiry "2026-07-06T23:59:00Z" \
  --auth-mode login \
  --as-user \
  --output tsv
```

Explications :

- `--permissions r` : permission de lecture (Read).
- `--expiry` : date d'expiration au format ISO 8601 UTC (adaptez à la date du jour).
- `--as-user` : le jeton est signé avec votre identité Entra ID, plus précis que la clé de compte.

La commande renvoie le jeton seul (sans le `?` initial). Capturons-le dans une variable, puis construisons l'URL complète du blob :

```bash
SAS_TOKEN=$(
  az storage blob generate-sas \
    --account-name "$STORAGE_NAME" \
    --container-name documents \
    --name notes.md \
    --permissions r \
    --expiry "2026-07-06T23:59:00Z" \
    --auth-mode login \
    --as-user \
    --output tsv
)

SHARE_URL="https://$STORAGE_NAME.blob.core.windows.net/documents/notes.md?$SAS_TOKEN"

echo "$SHARE_URL"
```

!!! tip "Tester l'URL"
    La variable `$SHARE_URL` contient le lien temporaire. Vous pouvez le coller dans un navigateur, ou tester avec `curl` :

    ```bash
    curl -s "$SHARE_URL"
    ```

    Le contenu du fichier `notes.md` s'affiche. Une fois la date d'expiration passée, la même URL renverra une erreur 403 Forbidden.

## Vérification

Vérifions que le blob est en place et que la lecture via le jeton SAS fonctionne :

```bash
# Inventaire final du conteneur
az storage blob list \
  --account-name "$STORAGE_NAME" \
  --container-name documents \
  --auth-mode login \
  --output table

# Test de l'URL de partage
curl -sI "$SHARE_URL" | head -1
```

!!! success "Résultat attendu"
    - La commande `blob list` affiche la liste des blobs dans le conteneur `documents`.
    - `curl -sI` renvoie une ligne `HTTP/1.1 200 OK` (le jeton est valide jusqu'à l'expiration).

## Nettoyage (Important)

Azure Blob Storage est facturé à l'espace consommé et aux opérations. Supprimez le groupe de ressources pour éteindre toutes les ressources d'un coup (compte de stockage, conteneurs, blobs) :

```bash
az group delete \
  --name rg-tuto-blob \
  --yes \
  --no-wait
```

Une fois le groupe de ressources supprimé, toutes les URLs de blobs (et les jetons SAS associés) renvoient une erreur 404 : les données ont été effacées.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `az storage account create` | Crée un compte de stockage (entité racine) |
| `az storage container create` | Crée un conteneur (= dossier racine des blobs) |
| `az storage blob upload` | Dépose un fichier local dans un conteneur |
| `az storage blob download` | Télécharge un blob vers votre machine |
| `az storage blob list` | Liste les blobs d'un conteneur |
| `az storage blob generate-sas` | Génère un jeton de partage temporaire |
| `az storage blob url` | Construit l'URL d'un blob |
| `az group delete --name <rg> --yes` | Supprime le groupe de ressources et tout son contenu |

## Glossaire

Blob
:   *Binary Large Object*. Unité de fichier stockée dans Azure Blob Storage.

Conteneur
:   Regroupement de blobs à la racine d'un compte de stockage (équivalent d'un dossier racine).

Compte de stockage
:   Ressource Azure racine qui fournit l'espace de noms unique `https://<compte>.blob.core.windows.net`.

Jeton SAS (Shared Access Signature)
:   URL signée donnant un accès délégué et temporaire à un blob, sans partager la clé du compte.

SKU LRS
:   *Locally Redundant Storage*. Réplication locale (3 copies dans un seul datacenter Azure).

## Ressources

- [Microsoft Learn — Introduction au stockage Blob Azure](https://learn.microsoft.com/fr-fr/azure/storage/blobs/storage-blobs-introduction) — Présentation officielle du service.
- [Microsoft Learn — Tutoriel : charger et télécharger des blobs avec le portail Azure](https://learn.microsoft.com/fr-fr/azure/storage/blobs/storage-quickstart-blobs-portal) — Variante via l'interface web.
- [Documentation officielle Azure CLI — az storage blob](https://learn.microsoft.com/fr-fr/cli/azure/storage/blob) — Référence complète des commandes.
- [Microsoft Learn — Accorder un accès limité avec une signature d'accès partagé (SAS)](https://learn.microsoft.com/fr-fr/azure/storage/common/storage-sas-overview) — Principe des jetons SAS.
