---
title: Déployer un site web statique avec Amazon S3
date: 2026-06-09
author: Nicolas BODAINE
tags:
  - aws
  - cloud
  - s3
  - web
difficulty: débutant
os: AWS
status: publié
---

# Déployer un site web statique avec Amazon S3

!!! abstract "Résumé"
    Amazon S3 (Simple Storage Service) est l'un des services fondamentaux d'AWS. Bien qu'il soit conçu pour le stockage d'objets, il offre une fonctionnalité native permettant d'héberger des sites web statiques (HTML, CSS, JS, images) à très faible coût. Ce tutoriel vous montre comment créer un bucket S3, le configurer pour l'hébergement web, et rendre son contenu public.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | AWS CLI / Console AWS |
| Dernière mise à jour | 2026-06-09 |

## Contexte

Héberger un site statique sur un vrai serveur (EC2, VPS) demande de configurer un serveur web (Nginx, Apache), de gérer les mises à jour de l'OS et de payer pour un serveur allumé en permanence. Avec Amazon S3, vous ne payez que pour l'espace de stockage et la bande passante consommée (souvent quelques centimes par mois), sans aucune gestion de serveur sous-jacente (Serverless).

## Prérequis

- Un compte **AWS** actif.
- L'outil en ligne de commande **AWS CLI** installé et configuré (`aws configure`) sur votre machine de test.
- Quelques fichiers web basiques (un fichier `index.html` et éventuellement `error.html`).

## Procédure

Nous utiliserons l'AWS CLI pour que la démarche soit automatisable et reproductible, bien que tout puisse être fait via l'interface web (AWS Management Console).

### Étape 1 : Créer un bucket S3

Les noms des buckets S3 doivent être **uniques au niveau mondial**. Nous allons créer un bucket nommé `mon-site-statique-12345` (remplacez `12345` par un suffixe aléatoire) dans la région `eu-west-3` (Paris).

```bash
aws s3api create-bucket \
    --bucket mon-site-statique-12345 \
    --region eu-west-3 \
    --create-bucket-configuration LocationConstraint=eu-west-3
```

!!! note "Note sur les régions"
    Si vous utilisez la région `us-east-1` (N. Virginie), le paramètre `--create-bucket-configuration` n'est pas nécessaire.

### Étape 2 : Activer l'hébergement web statique

On indique à S3 que ce bucket doit agir comme un serveur web, et on définit les fichiers de point d'entrée.

```bash
aws s3 website s3://mon-site-statique-12345 \
    --index-document index.html \
    --error-document error.html
```

### Étape 3 : Désactiver le blocage de l'accès public

Par défaut pour des raisons de sécurité, AWS bloque fermement tout accès public aux nouveaux buckets. Pour un site web, nous devons lever cette restriction.

```bash
aws s3api put-public-access-block \
    --bucket mon-site-statique-12345 \
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

### Étape 4 : Appliquer une stratégie de bucket (Bucket Policy)

Maintenant que S3 l'autorise, nous devons explicitement dire au bucket d'autoriser la lecture publique de tous ses objets (`s3:GetObject`).

Créez un fichier local nommé `policy.json` avec ce contenu :

```json title="policy.json"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::mon-site-statique-12345/*"
        }
    ]
}
```

Appliquez cette politique au bucket :

```bash
aws s3api put-bucket-policy \
    --bucket mon-site-statique-12345 \
    --policy file://policy.json
```

### Étape 5 : Uploader les fichiers du site

Créez un fichier `index.html` basique pour le test :

```html title="index.html"
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Mon Site S3</title>
</head>
<body>
    <h1>Bienvenue sur mon site hébergé sur Amazon S3 !</h1>
    <p>Ce site est statique et n'utilise aucun serveur dédié.</p>
</body>
</html>
```

Poussez ce fichier vers votre bucket :

```bash
aws s3 cp index.html s3://mon-site-statique-12345/
```

!!! tip "Synchronisation"
    Si vous avez un dossier complet contenant votre site (CSS, JS, images), vous pouvez utiliser `aws s3 sync mon-dossier/ s3://mon-site-statique-12345/`.

## Vérification

Votre site est maintenant en ligne ! L'URL générée par AWS suit cette structure :
`http://<nom-du-bucket>.s3-website.<region>.amazonaws.com`

Pour notre exemple :
`http://mon-site-statique-12345.s3-website.eu-west-3.amazonaws.com`

Vous pouvez vérifier le bon fonctionnement avec `curl` :

```bash
curl -I http://mon-site-statique-12345.s3-website.eu-west-3.amazonaws.com
```

!!! success "Résultat attendu"
    Vous devriez obtenir un code HTTP `200 OK`. Si vous ouvrez cette URL dans un navigateur, votre page HTML s'affichera.

## Aller plus loin

Bien que cette méthode soit simple, l'URL fournie par AWS est en `http://`. Pour avoir du `https://` et utiliser votre propre nom de domaine, il est fortement recommandé de placer le réseau de diffusion de contenu **Amazon CloudFront** devant votre bucket S3.

## Ressources

- [Documentation officielle AWS - Hébergement d'un site web statique sur Amazon S3](https://docs.aws.amazon.com/fr_fr/AmazonS3/latest/userguide/WebsiteHosting.html)
- [Référence CLI AWS S3](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3/index.html)