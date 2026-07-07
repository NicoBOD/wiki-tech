---
title: Créer et déployer sa première fonction Serverless avec AWS Lambda
date: 2026-06-30
author: Nicolas BODAINE
tags:
  - aws
  - serverless
  - lambda
  - cloud
  - python
difficulty: débutant
os: Cloud (AWS)
status: publié
---

# Créer et déployer sa première fonction Serverless avec AWS Lambda

!!! abstract "Résumé"
    Découvrez comment créer, configurer et tester votre première fonction AWS Lambda en utilisant Python. Le Serverless permet d'exécuter du code sans avoir à provisionner ni gérer de serveurs.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Cloud (AWS) |
| Dernière mise à jour | 2026-06-30 |

## Contexte

Dans une architecture Serverless, vous ne payez que pour le temps de calcul réellement consommé, sans vous soucier de l'infrastructure sous-jacente. AWS Lambda est le service historique de "Function as a Service" (FaaS) d'Amazon. Dans ce tutoriel, nous allons créer une fonction Python très simple qui prend en paramètre un nom et retourne un message d'accueil.

## Prérequis

- Un compte [AWS](https://aws.amazon.com/fr/) actif.
- Avoir les droits suffisants pour créer une fonction Lambda et un rôle IAM.
- Quelques notions de base en Python.

## Procédure

### Étape 1 : Créer la fonction Lambda

1. Connectez-vous à la [Console de gestion AWS](https://console.aws.amazon.com/).
2. Dans la barre de recherche des services, tapez **Lambda** et sélectionnez le service.
3. Cliquez sur le bouton **Créer une fonction** (Create function).
4. Laissez l'option **Créer à partir de zéro** (Author from scratch) cochée.
5. Dans **Nom de la fonction** (Function name), entrez `MaPremiereFonction`.
6. Dans **Exécution** (Runtime), sélectionnez `Python 3.12` ou la dernière version Python disponible.
7. Sous **Autorisations** (Permissions), laissez AWS créer un nouveau rôle avec les autorisations Lambda de base.
8. Cliquez sur le bouton **Créer une fonction** (Create function) en bas de la page.

### Étape 2 : Écrire le code de la fonction

Une fois la fonction créée, vous arrivez sur sa page de configuration. 
Descendez jusqu'à la section **Source du code** (Code source) où l'éditeur en ligne est affiché.

Par défaut, vous trouverez un fichier `lambda_function.py` contenant un petit squelette. Remplacez son contenu par le code suivant :

```python title="lambda_function.py" linenums="1"
import json

def lambda_handler(event, context):
    # Récupération du nom dans l'événement (avec une valeur par défaut)
    nom = event.get('nom', 'Visiteur')
    
    # Création du message d'accueil
    message = f"Bonjour {nom}, bienvenue dans votre première fonction AWS Lambda !"
    
    # Construction de la réponse retournée
    return {
        'statusCode': 200,
        'body': json.dumps({'message': message})
    }
```

Cliquez ensuite sur le bouton **Deploy** (Déployer) pour enregistrer et appliquer ces changements.

### Étape 3 : Tester la fonction

Pour vérifier que la fonction se comporte comme prévu, nous allons simuler un appel.

1. Cliquez sur l'onglet **Test** puis sur le bouton **Créer un nouvel événement** (Create new test event).
2. Nommez l'événement `TestAvecNom`.
3. Dans la zone de texte JSON, insérez le contenu suivant :

```json
{
  "nom": "Nicolas"
}
```

4. Cliquez sur **Enregistrer** (Save).
5. Cliquez sur le bouton bleu **Test** en haut de la page.

## Vérification

Un encart **Résultats d'exécution** (Execution results) s'affiche. Cliquez sur *Détails* pour l'étendre.

!!! success "Résultat attendu"
    Vous devriez voir un résultat semblable à ceci :
    
    ```json
    {
      "statusCode": 200,
      "body": "{\"message\": \"Bonjour Nicolas, bienvenue dans votre premi\\u00e8re fonction AWS Lambda !\"}"
    }
    ```
    
    Vous y verrez également un résumé détaillant la durée d'exécution (souvent en millisecondes), les ressources allouées et consommées.

## Pour aller plus loin

Pour que votre fonction soit accessible depuis un navigateur, vous pouvez par la suite créer une URL de fonction Lambda (Lambda Function URL) ou configurer une API Gateway devant celle-ci. Cela permettra d'exécuter la fonction via une requête HTTP standard.

## Ressources

- [Documentation officielle d'AWS Lambda](https://docs.aws.amazon.com/fr_fr/lambda/latest/dg/welcome.html) — Guide du développeur AWS.
- [Ateliers AWS Skill Builder](https://skillbuilder.aws/) — Pour approfondir ses connaissances sur les architectures Serverless.
