---
title: Extraire et formater des données JSON avec la commande jq
date: 2026-06-11
author: Nicolas BODAINE
tags:
  - linux
  - json
  - cli
  - shell
difficulty: intermédiaire
os: Linux
status: publié
---

# Extraire et formater des données JSON avec la commande jq

!!! abstract "Résumé"
    La commande `jq` est le "couteau suisse" en ligne de commande pour analyser, filtrer, formater et modifier des flux de données JSON. Que ce soit pour lire la réponse d'une API ou extraire des infos d'un fichier de configuration, `jq` permet de gagner un temps précieux et d'éviter les `grep` et `awk` complexes sur du JSON.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux |
| Dernière mise à jour | 2026-06-11 |

## Contexte

De nos jours, le format JSON est omniprésent : réponses d'API REST, logs structurés, fichiers de configuration de nombreuses applications et outils d'infrastructure (Docker, Terraform, AWS CLI, etc.).
Le traiter avec des outils Unix classiques comme `grep`, `sed` ou `awk` est souvent hasardeux car le format JSON peut être écrit sur une seule ligne ou formaté de manière variable (indentation, retours à la ligne). `jq` est un parseur de JSON robuste conçu spécifiquement pour la ligne de commande.

## Prérequis

- Avoir accès à un terminal Linux.
- L'outil `curl` pour faire une requête HTTP (pour l'exemple).

## Installation

`jq` est disponible dans les dépôts officiels de presque toutes les distributions.

```bash title="Debian / Ubuntu"
sudo apt update
sudo apt install jq
```

```bash title="RHEL / CentOS / AlmaLinux"
sudo dnf install epel-release
sudo dnf install jq
```

## Procédure : utilisation de base

Pour illustrer les capacités de `jq`, nous allons interroger une API publique qui renvoie des informations sur des utilisateurs aléatoires (JSONPlaceholder) et sauvegarder la réponse dans un fichier.

```bash
curl -s https://jsonplaceholder.typicode.com/users > users.json
```

Voici à quoi ressemble le contenu brut (très compacté, potentiellement sur une seule ligne) :

```json
[{"id":1,"name":"Leanne Graham","username":"Bret","email":"Sincere@april.biz","address":{"street":"Kulas Light","suite":"Apt. 556","city":"Gwenborough","zipcode":"92998-3874","geo":{"lat":"-37.3159","lng":"81.1496"}},"phone":"1-770-736-8031 x56442","website":"hildegard.org","company":{"name":"Romaguera-Crona","catchPhrase":"Multi-layered client-server neural-net","bs":"harness real-time e-markets"}}, ... ]
```

### 1. Formater (Pretty-print) le JSON

C'est l'utilisation la plus courante. Passer simplement le JSON brut à `jq .` le réindente avec des couleurs pour le rendre lisible pour un humain.

```bash
cat users.json | jq .
```
*(Vous pouvez aussi utiliser `jq . users.json` directement sans faire de pipe).*

### 2. Extraire un champ spécifique d'un objet

Si votre JSON est un tableau (ce qui est le cas ici), vous pouvez cibler le premier élément avec `.[0]`, puis accéder à sa propriété `name`.

```bash
jq '.[0].name' users.json
```

!!! success "Résultat attendu"
    ```json
    "Leanne Graham"
    ```

Pour récupérer la valeur sans les guillemets (pour l'utiliser dans un script Bash par exemple), utilisez l'option `-r` (raw) :

```bash
jq -r '.[0].name' users.json
```

### 3. Extraire une valeur de tous les éléments du tableau

Pour itérer sur tous les éléments du tableau et extraire leur adresse email :

```bash
jq -r '.[].email' users.json
```

### 4. Filtrer les résultats (Condition)

Imaginons que nous voulions uniquement récupérer le nom de l'utilisateur dont l'ID est 3. Nous utilisons la fonction `select()`.

```bash
jq -r '.[] | select(.id == 3) | .name' users.json
```

Ici, `jq` crée un pipeline interne avec `|` (similaire au pipe du shell). Il itère sur le tableau `.[]`, filtre avec `select(.id == 3)`, et pour l'élément correspondant, il extrait `.name`.

### 5. Créer un nouvel objet JSON simplifié

Très utile pour nettoyer un gros JSON en gardant uniquement ce qui vous intéresse. On peut mapper la réponse vers un nouveau format.

```bash
jq '.[] | { nom: .name, courriel: .email, ville: .address.city }' users.json
```

!!! success "Résultat partiel"
    ```json
    {
      "nom": "Leanne Graham",
      "courriel": "Sincere@april.biz",
      "ville": "Gwenborough"
    }
    {
      "nom": "Ervin Howell",
      "courriel": "Shanna@melissa.tv",
      "ville": "Wisokyburgh"
    }
    ```

## Aide-mémoire

| Commande `jq` | Description |
|---------------|-------------|
| `jq .` | Affiche le JSON formaté et coloré. |
| `jq -r '.champ'` | Extrait la valeur de "champ" en texte brut (sans guillemets). |
| `jq '.[]'` | Déstructure le tableau pour agir sur chaque élément. |
| `jq 'keys'` | Retourne les clés de l'objet ou les index du tableau. |
| `jq 'length'` | Donne la longueur du tableau ou le nombre de clés d'un objet. |

## Ressources

- [Manuel officiel de jq (en anglais)](https://jqlang.github.io/jq/manual/) — Documentation complète et exhaustive.
- [jqplay.org](https://jqplay.org/) — Bac à sable interactif pour tester vos filtres `jq` en direct depuis votre navigateur.
