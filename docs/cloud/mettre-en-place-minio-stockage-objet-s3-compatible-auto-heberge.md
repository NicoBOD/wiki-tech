---
title: "Déployer un stockage objet S3-compatible avec MinIO en auto-hébergé"
date: 2026-07-08
author: Nicolas BODAINE
tags:
  - minio
  - stockage-objet
  - s3
  - auto-hébergement
  - cloud
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Déployer un stockage objet S3-compatible avec MinIO en auto-hébergé

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour déployer **MinIO**, un serveur de **stockage objet compatible API S3** entièrement open-source, sur une machine Ubuntu Server 24.04 via Docker. Vous apprendrez à le lancer, à créer un *bucket*, à gérer des accès dédiés (utilisateurs/politiques) et à dialoguer avec lui aussi bien depuis la console web que via l'AWS CLI. Idéal en lab pour remplacer Amazon S3 sans dépendre d'un cloud public, ou pour tester ses propres applications cloud-native localement.

|| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu Server 24.04 |
| Dernière mise à jour | 2026-07-08 |

## Contexte

Quand on développe ou qu'on administre des applications modernes (sauvegardes, hébergement de fichiers, pipelines de données, modèles d'IA…), on a souvent besoin d'un **stockage objet** : chaque fichier devient un *objet* adressable par une URL, accessible via HTTP, sans dépendre d'un système de fichiers classique. C'est exactement ce que propose **Amazon S3**, mais il impose un compte cloud facturé.

**MinIO** est une implémentation open-source de ce même modèle, **100 % compatible avec l'API S3**. On peut donc pointer n'importe quelle application « S3-ready » (Spring, Nextcloud, WordPress via plugin S3, scripts AWS CLI…) vers MinIO sans rien changer à son code. Ce TP montre comment l'installer en quelques minutes sur une VM de lab.

## Prérequis

- Une machine **Ubuntu Server 24.04** (VM de lab ou petit serveur physique) avec un accès `sudo`.
- **Docker Engine** installé et fonctionnel (`docker --version` doit répondre). Si ce n'est pas le cas, voir l'article [Installer Docker Engine sur Ubuntu 24.04](../logiciels/installer-docker-engine-ubuntu-2404.md).
- Les ports **9000** (API S3 / données) et **9001** (console web d'administration) libres et autorisés par le pare-feu.
- Un accès réseau depuis votre poste vers l'IP de la machine (pour ouvrir la console web).
- Facultatif : l'**AWS CLI v2** installée sur un poste pour tester la compatibilité S3 en ligne de commande.

## Procédure

### Étape 1 : Préparer le dossier de données persistantes

MinIO stocke les objets sur disque. On crée un dossier dédié monté dans le conteneur afin que les données survivent à un redémarrage :

```bash
sudo mkdir -p /srv/minio/data
sudo chown -R 1000:1000 /srv/minio/data
```

!!! note "Pourquoi `/srv/minio/data` ?"
    Par convention, `/srv` accueille les données servies par les services du serveur. Le propriétaire `1000:1000` correspond à l'utilisateur interne utilisé par l'image officielle MinIO, ce qui évite les erreurs de permissions au démarrage.

### Étape 2 : Lancer MinIO avec Docker

On lance le conteneur en arrière-plan, en exposant les deux ports et en définissant les identifiants racine (l'équivalent du *root account* S3) :

```bash
sudo docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -v /srv/minio/data:/data \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=ChangeMeStrongPassword123 \
  --restart unless-stopped \
  minio/minio server /data --console-address ":9001"
```

!!! warning "Choisissez un mot de passe robuste"
    `MINIO_ROOT_PASSWORD` doit faire **au moins 8 caractères**. Un mot de passe faible est refusé au démarrage. Remplacez `ChangeMeStrongPassword123` par une vraie phrase secrète, et conservez-la : c'est le seul compte admin par défaut.

Vérifiez que le conteneur est bien démarré :

```bash
sudo docker ps --filter name=minio
sudo docker logs minio --tail 20
```

Vous devriez voir une ligne du type :

```
Status:         1 Online, 0 Offline.
API: http://172.17.0.2:9000  http://127.0.0.1:9000
Console: http://172.17.0.2:9001 http://127.0.0.1:9001
```

### Étape 3 : Ouvrir la console web et se connecter

1. Depuis votre navigateur, ouvrez `http://<IP_DE_LA_MACHINE>:9001`.
2. Connectez-vous avec :
   - **Identifiant** : `admin`
   - **Mot de passe** : celui défini dans `MINIO_ROOT_PASSWORD`.

!!! tip "Accès depuis un lab isolé"
    Si votre VM n'a pas d'IP joignable depuis votre poste, ajoutez dans votre fichier local `/etc/hosts` une ligne `192.168.x.x minio.lan` et utilisez `http://minio.lan:9001`.

### Étape 4 : Créer un bucket et uploader un objet

1. Dans la console, cliquez sur **Create Bucket** (ou l'icône + en bas à droite).
2. Nommez-le `tp-minio` (les noms de bucket S3 doivent être en minuscules, sans espaces).
3. Laissez les options par défaut et validez.
4. Ouvrez le bucket, cliquez sur **Upload** → **Upload File**, et déposez un fichier de test (ex. `photo.png`).

Le fichier est maintenant stocké en tant qu'objet adressable via l'API S3.

### Étape 5 : Créer un utilisateur dédié et une politique d'accès

Pour la sécurité, on évite d'utiliser le compte `admin` dans les applications. On crée un utilisateur service avec une politique limitée à un bucket :

1. Console → **Identity** → **Users** → **Create User**.
2. `Access Key` : `app-tp`, `Secret Key` : générez-en un robuste (ou laissez MinIO le proposer), notez-le.
3. Console → **Identity** → **Policies** → **Create Policy**, collez ceci (accès lecture/écriture au seul bucket `tp-minio`) :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::tp-minio", "arn:aws:s3:::tp-minio/*"]
    }
  ]
}
```

4. Nommez la politique `tp-minio-rw`, enregistrez, puis assignez-la à l'utilisateur `app-tp`.

### Étape 6 : Tester la compatibilité S3 avec l'AWS CLI

Sur un poste où AWS CLI v2 est installé, configurez un profil pointant vers MinIO :

```bash
aws configure set aws_access_key_id "app-tp"
aws configure set aws_secret_access_key "<SECRET_DE_APP-TP>"
aws configure set default.region "us-east-1"
aws configure set default.output "json"
```

Puis interrogez MinIO comme s'il s'agissait de S3 (en forçant le endpoint local) :

```bash
aws s3 --endpoint-url http://<IP_DE_LA_MACHINE>:9000 ls s3://tp-minio
aws s3 --endpoint-url http://<IP_DE_LA_MACHINE>:9000 cp ./document.txt s3://tp-minio/document.txt
```

!!! success "Preuve de compatibilité"
    Si la commande `ls` liste le contenu de votre bucket et que `cp` upload sans erreur, c'est que n'importe quelle application compatible S3 fonctionnera avec MinIO sans modification de code.

## Vérification

Comment vérifier que tout fonctionne :

```bash
# Le conteneur doit être à l'état Up
sudo docker ps --filter name=minio --format "{{.Names}} {{.Status}}"

# L'API S3 répond (HTTP 200 attendu)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9000/minio/health/live

# L'objet uploadé est bien présent via l'AWS CLI
aws s3 --endpoint-url http://<IP_DE_LA_MACHINE>:9000 ls s3://tp-minio
```

!!! success "Résultat attendu"
    - `docker ps` affiche `minio Up (healthy)` (ou `Up X seconds`).
    - Le `curl` renvoie `200`.
    - La commande `ls` liste `document.txt` (et tout autre objet déposé).

## Glossaire

MinIO
: Serveur de stockage objet open-source compatible avec l'API Amazon S3.

Bucket
: Conteneur logique de niveau supérieur dans le stockage objet (équivalent à un « dossier racine » S3), dont le nom est globalement unique au sein d'une instance.

Objet
: Unité de stockage : un fichier + ses métadonnées, adressable par une clé (= chemin) au sein d'un bucket.

Access Key / Secret Key
: Identifiants (login/mot de passe) d'un compte S3 permettant d'authentifier les appels à l'API.

Politique (Policy)
: Document JSON décrivant les permissions accordées (quelles actions sur quelles ressources).

## Checklist

- [x] Dossier de données `/srv/minio/data` créé et monté.
- [x] Conteneur MinIO lancé avec ports 9000/9001 exposés.
- [x] Mot de passe racine robuste défini.
- [x] Console web accessible sur `:9001` et connexion admin OK.
- [x] Bucket `tp-minio` créé.
- [x] Utilisateur service `app-tp` + politique restreinte créés.
- [x] Test de lecture/écriture validé via AWS CLI.

## Ressources

- [Documentation officielle MinIO (Linux)](https://min.io/docs/minio/linux/index.html) — Guide de référence d'installation, déploiement distribué et sécurisation.
- [MinIO sur Docker Hub](https://hub.docker.com/r/minio/minio) — Image officielle et tags disponibles.
- [AWS S3 API Reference](https://docs.aws.amazon.com/AmazonS3/latest/API/API_Operations.html) — Spécification de l'API S3 que MinIO implémente.
- [Installer Docker Engine sur Ubuntu 24.04](../logiciels/installer-docker-engine-ubuntu-2404.md) — Prérequis si Docker n'est pas encore présent sur votre serveur.
