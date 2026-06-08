---
title: Débuter avec Postman pour tester des API REST
date: 2026-06-08
author: Nicolas BODAINE
tags:
  - postman
  - api
  - developpement
difficulty: débutant
os: Indépendant
status: publié
---

# Débuter avec Postman pour tester des API REST

!!! abstract "Résumé"
    Postman est l'un des outils les plus populaires pour tester des API (Interfaces de Programmation d'Application). Ce guide vous montrera comment l'installer, créer vos premières requêtes HTTP (GET et POST), et comprendre les réponses reçues. Idéal pour ceux qui découvrent le fonctionnement des API REST.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Windows / macOS / Linux |
| Dernière mise à jour | 2026-06-08 |

## Contexte

Lorsque vous développez une application ou que vous utilisez un service externe (comme la météo, un système de paiement, etc.), il est fréquent de devoir interagir avec une **API REST**. Au lieu d'écrire du code complexe ou d'utiliser la ligne de commande avec `curl` pour vérifier que l'API fonctionne, vous pouvez utiliser une interface graphique intuitive. C'est là que **Postman** entre en jeu : c'est un client HTTP qui permet de forger des requêtes, de les envoyer au serveur et d'inspecter les réponses confortablement.

## Prérequis

- Un ordinateur connecté à Internet (Windows, macOS ou Linux).
- Aucune connaissance avancée en programmation n'est requise, mais savoir ce qu'est une URL et le format JSON est un plus.

## Procédure

### Étape 1 : Installation de Postman

Postman existe sous forme d'application de bureau autonome et en version Web. La version de bureau est recommandée pour éviter les limitations liées au navigateur (comme les problèmes CORS).

1. Allez sur le site officiel : [https://www.postman.com/downloads/](https://www.postman.com/downloads/).
2. Téléchargez l'installateur correspondant à votre système d'exploitation.
3. Installez l'application en suivant l'assistant classique.
4. Au premier lancement, vous pouvez **créer un compte gratuit** (recommandé pour sauvegarder votre travail dans le cloud) ou ignorer cette étape en cliquant sur "Skip and go to the app" (en bas de l'écran).

### Étape 2 : Créer sa première requête (GET)

Nous allons tester l'API publique **JSONPlaceholder**, très pratique pour simuler des appels.

1. Dans Postman, cliquez sur le bouton **"+"** ou sur **"New" > "HTTP Request"** pour ouvrir un nouvel onglet de requête.
2. À côté de la barre d'adresse, assurez-vous que la méthode **GET** est sélectionnée (c'est le cas par défaut).
3. Entrez l'URL suivante dans la barre de recherche : `https://jsonplaceholder.typicode.com/users`
4. Cliquez sur le bouton bleu **Send**.

Dans la partie inférieure de l'écran (la section "Response"), vous verrez :
- Le **Statut** (`200 OK`, indiquant que la requête a réussi).
- Le **Temps** de réponse (ex: `120 ms`).
- Le **Corps** (*Body*) de la réponse, qui affiche une liste d'utilisateurs au format JSON.

### Étape 3 : Envoyer des données avec une requête (POST)

La méthode GET sert à récupérer des données. Pour en envoyer ou en créer, on utilise souvent la méthode **POST**.

1. Ouvrez un nouvel onglet en cliquant sur le bouton **"+"**.
2. Changez la méthode de "GET" à **POST** via le menu déroulant.
3. Entrez l'URL : `https://jsonplaceholder.typicode.com/posts`
4. Juste sous l'URL, cliquez sur l'onglet **Body**.
5. Sélectionnez le bouton radio **raw** (brut).
6. À droite, un menu déroulant apparaît avec le mot "Text". Cliquez dessus et choisissez **JSON**.
7. Dans la grande zone de texte, copiez le code JSON suivant :

```json
{
  "title": "Mon premier test Postman",
  "body": "Ceci est le contenu de mon article test envoyé via l'API.",
  "userId": 1
}
```

8. Cliquez sur **Send**.

Dans la réponse, vous devriez obtenir un statut **201 Created** (qui confirme la création) et le serveur vous renverra l'objet que vous venez d'envoyer, accompagné d'un "id" unique généré par l'API (ex: `"id": 101`).

## Aide-mémoire : Les principales méthodes HTTP

| Méthode HTTP | Description | Équivalent CRUD |
|--------------|-------------|-----------------|
| `GET` | Récupérer des informations (ex: liste d'articles). | Read |
| `POST` | Créer une nouvelle ressource (ex: ajouter un utilisateur). | Create |
| `PUT` | Remplacer entièrement une ressource existante. | Update |
| `PATCH` | Modifier partiellement une ressource (ex: changer juste un mot de passe). | Update |
| `DELETE` | Supprimer une ressource. | Delete |

## Glossaire

API (Application Programming Interface)
:   Ensemble de règles permettant à des logiciels de communiquer entre eux.

JSON (JavaScript Object Notation)
:   Format de données textuel très utilisé dans les API pour structurer l'information de manière lisible par l'homme et la machine.

Code de statut HTTP
:   Code numérique renvoyé par le serveur pour indiquer le résultat de la requête (ex: 200 pour succès, 404 pour non trouvé, 500 pour erreur serveur).

## Ressources

- [Postman Learning Center](https://learning.postman.com/docs/getting-started/introduction/) — Documentation officielle complète.
- [JSONPlaceholder](https://jsonplaceholder.typicode.com/) — Fausse API en ligne gratuite pour les tests et le prototypage.
