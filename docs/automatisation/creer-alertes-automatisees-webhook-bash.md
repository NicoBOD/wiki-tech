---
title: Créer des alertes automatisées via Webhook (Slack/Discord) en Bash
date: 2026-06-28
author: Nicolas BODAINE
tags:
  - bash
  - automatisation
  - webhook
  - slack
  - discord
  - notifications
difficulty: intermédiaire
os: Linux
status: publié
---

# Créer des alertes automatisées via Webhook en Bash

!!! abstract "Résumé"
    Apprenez à intégrer des notifications sur Slack ou Discord directement depuis vos scripts Bash d'administration ou de sauvegarde en utilisant des Webhooks et la commande `curl`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux |
| Dernière mise à jour | 2026-06-28 |

## Contexte

Lorsque vous automatisez des tâches d'administration sur vos serveurs (comme des sauvegardes planifiées, des mises à jour automatiques ou de la supervision), celles-ci s'exécutent de manière silencieuse en arrière-plan. Si une sauvegarde échoue, vous ne le saurez pas immédiatement.

L'utilisation de **Webhooks** permet à vos scripts Bash d'envoyer instantanément un message sur les canaux de communication de votre équipe (Slack, Discord, Microsoft Teams, etc.) via une simple requête HTTP, souvent avec la commande `curl`.

## Prérequis

- Un serveur ou poste de travail sous Linux.
- L'utilitaire `curl` installé (`sudo apt install curl`).
- Les permissions nécessaires pour créer un Webhook sur un canal Slack ou Discord.

## Procédure

### Étape 1 : Obtenir l'URL du Webhook

Avant de commencer à scripter, vous devez générer une URL de Webhook sur la plateforme de votre choix.

=== "Discord"

    1. Allez dans les paramètres d'un de vos salons textuels (roue crantée).
    2. Cliquez sur **Intégrations** > **Webhooks**.
    3. Cliquez sur **Nouveau Webhook**.
    4. Donnez un nom au Webhook (ex: `Alerte Serveur`) et cliquez sur **Copier l'URL du Webhook**.

=== "Slack"

    1. Allez sur la page de création d'applications Slack (api.slack.com/apps).
    2. Créez une application pour votre Workspace.
    3. Allez dans **Incoming Webhooks** et activez la fonctionnalité.
    4. Cliquez sur **Add New Webhook to Workspace**, choisissez un canal et copiez l'URL générée.

L'URL ressemblera à quelque chose comme `https://discord.com/api/webhooks/1234/abcd...` ou `https://hooks.slack.com/services/T00/B00/XXX...`.

### Étape 2 : Envoyer un message simple avec `curl`

Pour interagir avec le Webhook, nous envoyons une requête HTTP de type `POST` contenant un corps de message au format JSON.

Voici la commande basique pour envoyer un simple "Hello World" :

=== "Discord"

    ```bash
    WEBHOOK_URL="VOTRE_URL_ICI"
    curl -H "Content-Type: application/json" \
         -X POST \
         -d '{"content": "⚠️ Alerte : Tâche de sauvegarde terminée avec succès !"}' \
         "$WEBHOOK_URL"
    ```

=== "Slack"

    ```bash
    WEBHOOK_URL="VOTRE_URL_ICI"
    curl -H "Content-Type: application/json" \
         -X POST \
         -d '{"text": "⚠️ Alerte : Tâche de sauvegarde terminée avec succès !"}' \
         "$WEBHOOK_URL"
    ```

!!! tip "Attention aux variables"
    Si vous utilisez des variables dans votre JSON (`-d`), pensez à utiliser des doubles guillemets autour de l'ensemble de la chaîne JSON, et à échapper les guillemets internes, ou utilisez la technique du "Heredoc" pour plus de lisibilité.

### Étape 3 : Créer une fonction Bash réutilisable

Plutôt que de retaper la commande `curl` à chaque fois, il est plus élégant d'écrire une fonction que vous pouvez appeler partout dans votre script.

```bash title="script-sauvegarde.sh" linenums="1"
#!/bin/bash

# Configuration
WEBHOOK_URL="https://discord.com/api/webhooks/xxxx/yyyy"

# Fonction d'envoi d'alerte Discord
send_alert() {
    local message="$1"
    
    # Envoi de la requête en masquant la sortie standard (-s)
    curl -s -H "Content-Type: application/json" \
         -X POST \
         -d "{\"content\": \"$message\"}" \
         "$WEBHOOK_URL" > /dev/null
}

# Début du script
echo "Démarrage de la sauvegarde..."
# ... vos commandes de sauvegarde ici ...

if [ $? -eq 0 ]; then
    send_alert "✅ Succès : La sauvegarde quotidienne s'est bien déroulée."
else
    send_alert "❌ Erreur : La sauvegarde quotidienne a échoué sur le serveur $(hostname)."
fi
```

!!! note "Explication"
    La variable spéciale `$?` contient le code de retour de la dernière commande exécutée (0 indique un succès, toute autre valeur indique une erreur).

### Étape 4 : Formatage avancé (Embeds Discord)

Les Webhooks permettent un formatage bien plus riche que du simple texte. Discord supporte par exemple les "Embeds" qui permettent d'ajouter des couleurs, des titres et des champs de données structurés.

```bash title="alert-embed.sh"
#!/bin/bash

WEBHOOK_URL="https://discord.com/api/webhooks/xxxx/yyyy"
SERVER_NAME=$(hostname)
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')

# Construction du payload JSON avec un bloc 'embeds'
# Note : la couleur 16711680 correspond au rouge vif (pour une alerte)
JSON_PAYLOAD=$(cat <<EOF
{
  "embeds": [{
    "title": "🚨 Alerte Espace Disque",
    "description": "Le serveur **$SERVER_NAME** manque d'espace !",
    "color": 16711680,
    "fields": [
      {
        "name": "Utilisation actuelle de /",
        "value": "$DISK_USAGE",
        "inline": true
      }
    ]
  }]
}
EOF
)

# Envoi de la requête
curl -s -H "Content-Type: application/json" \
     -X POST \
     -d "$JSON_PAYLOAD" \
     "$WEBHOOK_URL"
```

## Vérification

Pour vérifier que tout fonctionne, rendez-vous dans le salon (canal) Slack ou Discord concerné.
Si la requête réussit, le message devrait apparaître immédiatement.
En cas d'échec, vous pouvez retirer l'option `-s` de `curl` pour voir l'erreur HTTP retournée par l'API de Slack ou Discord (par exemple une erreur `401 Unauthorized` si l'URL est incorrecte).

## Ressources

- [Documentation des Webhooks Slack](https://api.slack.com/messaging/webhooks) — Guide officiel de l'API Slack.
- [Documentation des Webhooks Discord](https://discord.com/developers/docs/resources/webhook) — Référence de l'API Discord.
- [Manuel de la commande curl](https://curl.se/docs/manpage.html) — Les différentes options disponibles.