---
title: Les bases de n8n
date: 2026-04-08
author: Nicolas BODAINE
tags:
  - n8n
  - automatisation
  - workflow
  - docker
difficulty: débutant
status: publié
---

# Les bases de n8n

!!! abstract "Résumé"
    Guide d'introduction à n8n, la plateforme d'automatisation open source. Cet article couvre l'installation, les concepts fondamentaux, la création d'un premier workflow et les bonnes pratiques pour bien démarrer.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| Dernière mise à jour | 2026-04-08 |

## Contexte

**n8n** (prononcé "n-eight-n") est une plateforme d'automatisation de workflows open source et auto-hébergeable. Elle permet de connecter des applications entre elles et d'automatiser des tâches répétitives sans (ou avec peu de) code.

Contrairement à des solutions comme Zapier ou Make, n8n peut être hébergé sur sa propre infrastructure, ce qui garantit un contrôle total sur les données.

### Cas d'usage courants

- Synchroniser des données entre applications (CRM, mails, bases de données)
- Envoyer des notifications automatiques (Slack, Discord, e-mail)
- Traiter des webhooks et des API
- Automatiser des tâches IT (monitoring, rapports, backups)
- Intégrer des modèles d'IA dans des pipelines de traitement

## Prérequis

- **Docker** et **Docker Compose** installés sur la machine
- Connaissances de base en ligne de commande
- Un navigateur web récent

## Procédure

### Étape 1 : Installer n8n avec Docker Compose

Créer un fichier `docker-compose.yml` :

```yaml
services:
  n8n:
    image: n8nio/n8n
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - GENERIC_TIMEZONE=Europe/Paris
      - TZ=Europe/Paris

volumes:
  n8n_data:
```

Lancer le conteneur :

```bash
docker compose up -d
```

### Étape 2 : Accéder à l'interface

Ouvrir un navigateur et se rendre sur :

```
http://localhost:5678
```

Lors du premier accès, n8n demande de créer un compte administrateur (e-mail + mot de passe). Ce compte est local à l'instance.

### Étape 3 : Comprendre les concepts fondamentaux

Avant de créer un workflow, voici les notions clés :

#### Workflow

Un **workflow** est un enchaînement de nœuds (nodes) qui s'exécutent dans un ordre défini. C'est l'équivalent d'un script visuel.

#### Node (nœud)

Un **node** est une brique élémentaire qui effectue une action précise :

| Type de node | Rôle | Exemples |
|-------------|------|----------|
| **Trigger** | Déclenche le workflow | Webhook, Cron, événement |
| **Action** | Exécute une opération | Envoyer un e-mail, requête HTTP, insérer en BDD |
| **Fonction** | Transforme les données | Code JavaScript/Python, IF, Switch, Merge |

#### Connexions

Les nodes sont reliés par des **connexions** qui transportent les données de l'un à l'autre. Les données circulent sous forme d'**items** (objets JSON).

#### Exécution

Un workflow peut être déclenché :

- **Manuellement** — via le bouton "Execute Workflow"
- **Automatiquement** — via un trigger (webhook, cron, événement externe)

### Étape 4 : Créer son premier workflow

Objectif : créer un workflow qui récupère une citation aléatoire depuis une API et l'affiche.

**4.1 — Ajouter un trigger manuel**

1. Cliquer sur **+** au centre du canvas
2. Chercher **"Manual Trigger"** et l'ajouter
3. Ce node permet de lancer le workflow à la main

**4.2 — Ajouter un node HTTP Request**

1. Cliquer sur **+** à droite du trigger
2. Chercher **"HTTP Request"**
3. Configurer :
    - **Method** : `GET`
    - **URL** : `https://dummyjson.com/quotes/random`
4. Cliquer sur **Execute Node** pour tester

!!! success "Résultat attendu"
    Le node retourne un objet JSON contenant une citation, par exemple :
    ```json
    {
      "id": 42,
      "quote": "The only way to do great work is to love what you do.",
      "author": "Steve Jobs"
    }
    ```

**4.3 — Activer le workflow**

1. Cliquer sur le toggle **"Inactive / Active"** en haut à droite
2. Le workflow est maintenant prêt à être déclenché

!!! tip "Astuce"
    Utiliser le bouton **"Execute Workflow"** pour tester sans activer le workflow. Cela permet de vérifier chaque node étape par étape.

### Étape 5 : Comprendre le flux de données

Chaque node reçoit des données en entrée et produit des données en sortie. Pour inspecter les données :

1. **Cliquer sur un node** après exécution
2. L'onglet **"Output"** affiche les données produites
3. L'onglet **"Input"** affiche les données reçues du node précédent

Les données circulent sous forme de **tableau d'items**. Chaque item est un objet JSON. Si un node reçoit 5 items, il exécute son action 5 fois (une fois par item).

### Étape 6 : Utiliser les expressions

Les **expressions** permettent d'accéder dynamiquement aux données des nodes précédents. Elles s'écrivent entre doubles accolades :

```
{{ $json.quote }}
```

Expressions utiles :

| Expression | Description |
|-----------|-------------|
| `{{ $json.propriété }}` | Accède à une propriété de l'item courant |
| `{{ $('Nom du node').item.json.propriété }}` | Accède aux données d'un node spécifique |
| `{{ $now.toISO() }}` | Date et heure actuelles en ISO |
| `{{ $itemIndex }}` | Index de l'item en cours de traitement |
| `{{ $input.all() }}` | Tous les items en entrée |

!!! warning "Attention"
    Les expressions sont sensibles à la casse. `$json.Quote` et `$json.quote` sont différents.

## Aide-mémoire

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| ++tab++ | Ouvrir le menu d'ajout de node |
| ++ctrl+s++ | Sauvegarder le workflow |
| ++ctrl+enter++ | Exécuter le workflow |
| ++ctrl+z++ | Annuler |
| ++ctrl+shift+z++ | Rétablir |
| ++ctrl+a++ | Sélectionner tous les nodes |
| ++del++ | Supprimer le(s) node(s) sélectionné(s) |
| ++ctrl+d++ | Désactiver / réactiver un node |

### Nodes les plus utilisés

| Node | Usage |
|------|-------|
| **HTTP Request** | Appeler une API externe |
| **Webhook** | Recevoir des requêtes HTTP entrantes |
| **Schedule Trigger** | Déclencher à intervalles réguliers (cron) |
| **IF** | Condition : aiguiller le flux selon une règle |
| **Switch** | Condition multiple : aiguiller vers N branches |
| **Set** | Créer ou modifier des champs dans les données |
| **Code** | Exécuter du JavaScript ou Python personnalisé |
| **Merge** | Combiner les données de plusieurs branches |
| **Split Out** | Éclater un tableau en items individuels |
| **Aggregate** | Regrouper plusieurs items en un seul |

## Vérification

Pour vérifier que l'installation fonctionne correctement :

```bash
docker ps --filter name=n8n --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

!!! success "Résultat attendu"
    ```
    NAMES   STATUS          PORTS
    n8n     Up X minutes    0.0.0.0:5678->5678/tcp
    ```

Puis ouvrir `http://localhost:5678` — l'interface de n8n doit s'afficher.

## Ressources

- [Documentation officielle n8n](https://docs.n8n.io) — Référence complète
- [n8n Community](https://community.n8n.io) — Forum d'entraide
- [Bibliothèque de templates](https://n8n.io/workflows) — Workflows prêts à l'emploi
- [GitHub n8n](https://github.com/n8n-io/n8n) — Code source du projet
