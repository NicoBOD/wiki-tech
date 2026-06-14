---
title: Intégrer l'assistant IA Continue.dev à VS Code avec un modèle Ollama local
date: 2026-06-14
author: Nicolas BODAINE
tags:
  - ia
  - developpement
  - ollama
  - vscode
  - continue
difficulty: intermédiaire
os: Linux | Windows | macOS
status: publié
---

# Intégrer l'assistant IA Continue.dev à VS Code avec un modèle Ollama local

!!! abstract "Résumé"
    Dans ce tutoriel, nous allons voir comment intégrer l'extension **Continue.dev** à Visual Studio Code (VS Code) et la configurer pour utiliser un modèle linguistique local via **Ollama**. Cela permet de bénéficier d'un assistant de programmation IA (comme GitHub Copilot) entièrement gratuit, privé et fonctionnant localement sur votre machine, sans envoyer votre code dans le cloud.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Tous systèmes (Linux, Windows, macOS) |
| Dernière mise à jour | 2026-06-14 |

## Contexte

Les assistants IA pour le code, comme GitHub Copilot, sont très utiles pour augmenter la productivité des développeurs. Cependant, ils nécessitent un abonnement payant et envoient votre code sur des serveurs externes. Pour les projets nécessitant une confidentialité totale (ou simplement pour ne pas payer d'abonnement), utiliser une alternative open-source et locale est la solution idéale.

**Continue.dev** est une extension pour les éditeurs de code (VS Code et JetBrains) qui permet de connecter divers fournisseurs d'IA. En le couplant avec **Ollama**, vous pouvez exécuter un modèle LLM (Large Language Model) comme `starcoder2` ou `qwen2.5-coder` directement sur votre ordinateur.

## Prérequis

- Avoir **Visual Studio Code** installé.
- Avoir **Ollama** installé et en cours d'exécution (consultez le tutoriel [Installer et utiliser Ollama pour faire tourner un LLM en local](installer-utiliser-ollama-llm-local.md)).
- Disposer d'une machine avec un CPU relativement performant et idéalement un GPU pour des temps de réponse rapides (8 Go de RAM recommandés, 16 Go conseillés).

## Procédure

### Étape 1 : Télécharger un modèle adapté au code avec Ollama

Avant de configurer l'extension, nous devons télécharger un modèle optimisé pour la programmation. Ollama propose plusieurs modèles ; `starcoder2` et `qwen2.5-coder` sont d'excellents choix, de même que `deepseek-coder`.

Ouvrez un terminal et exécutez la commande suivante pour télécharger et lancer le modèle `starcoder2` (la version 3b est légère) :

```bash
ollama run starcoder2:3b
```

!!! tip "Choix du modèle"
    Si vous avez plus de RAM (16 Go ou +), vous pouvez essayer des modèles plus lourds comme `qwen2.5-coder:7b` : `ollama run qwen2.5-coder:7b`. Pour l'autocomplétion (code autocomplete), un modèle petit et rapide est préférable (ex. `starcoder2:3b`). Pour le chat, un modèle plus large est mieux (ex. `llama3` ou `qwen2.5-coder:7b`).

Une fois le modèle téléchargé, vous pouvez quitter le prompt interactif (`/bye`), mais assurez-vous que le service Ollama tourne toujours en arrière-plan.

### Étape 2 : Installer l'extension Continue.dev dans VS Code

1. Ouvrez Visual Studio Code.
2. Allez dans l'onglet **Extensions** (ou ++ctrl+shift+x++).
3. Recherchez **Continue - Codestral, Claude 3.5 Sonnet, GPT-4o...** (l'éditeur est *Continue*).
4. Cliquez sur **Installer**.

Une fois installée, une nouvelle icône (le logo Continue) apparaîtra dans la barre latérale gauche.

### Étape 3 : Configurer Continue pour utiliser Ollama

L'avantage de Continue est sa configuration par un fichier JSON simple.

1. Cliquez sur l'icône **Continue** dans la barre latérale.
2. En bas de la fenêtre Continue, vous trouverez une icône en forme d'engrenage (:material-cog:). Cliquez dessus pour ouvrir le fichier de configuration `config.json`.
3. Modifiez le bloc `"models"` pour utiliser votre modèle local via Ollama pour le chat.
4. Modifiez la section `"tabAutocompleteModel"` pour utiliser le modèle local pour l'autocomplétion (FIM - Fill-In-the-Middle).

Voici un exemple de configuration :

```json title="config.json" linenums="1" hl_lines="4-11 25-32"
{
  "models": [
    {
      "title": "Ollama - Qwen2.5 Coder (Chat)",
      "provider": "ollama",
      "model": "qwen2.5-coder:7b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Ollama - Llama 3 (Chat)",
      "provider": "ollama",
      "model": "llama3",
      "apiBase": "http://localhost:11434"
    }
  ],
  "customCommands": [
    {
      "name": "test",
      "prompt": "Écris des tests unitaires complets pour ce code.",
      "description": "Générer des tests unitaires"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Ollama - Starcoder2 (Autocomplete)",
    "provider": "ollama",
    "model": "starcoder2:3b",
    "apiBase": "http://localhost:11434"
  },
  "allowAnonymousTelemetry": false
}
```

!!! note "Adaptation"
    Assurez-vous que le nom dans `"model"` correspond exactement au nom du modèle que vous avez téléchargé avec Ollama (par exemple, `starcoder2:3b` ou `qwen2.5-coder:7b`).

Sauvegardez le fichier `config.json`. Continue appliquera les modifications instantanément.

### Étape 4 : Utiliser l'assistant

Vous avez maintenant deux fonctionnalités principales à votre disposition :

1. **Le Chat** :
    - Sélectionnez du code dans votre éditeur, appuyez sur ++ctrl+l++ (ou ++cmd+l++ sur Mac) pour l'envoyer dans le chat Continue.
    - Demandez "Explique ce code" ou "Refactorise cette fonction". Le modèle répondra directement dans la barre latérale.
2. **L'Autocomplétion (Tab Autocomplete)** :
    - Pendant que vous tapez du code, Continue interrogera Ollama en arrière-plan.
    - Des suggestions de code en gris clair apparaîtront.
    - Appuyez sur ++tab++ pour accepter une suggestion.

## Vérification

Pour vérifier que tout fonctionne :

1. Ouvrez un fichier Python (ex: `test.py`).
2. Commencez à taper une fonction : `def calculer_moyenne(liste):`
3. Attendez quelques secondes (le temps de réponse dépend de votre CPU/GPU).
4. Une suggestion devrait s'afficher.

```python
# Exemple de ce que l'IA pourrait suggérer
def calculer_moyenne(liste):
    # (Suggestion IA ci-dessous)
    if not liste:
        return 0
    return sum(liste) / len(liste)
```

!!! success "Résultat attendu"
    Si vous obtenez des suggestions de code avec la touche Tab et que le panneau latéral de chat répond à vos questions, votre assistant IA local est fonctionnel ! Si ce n'est pas le cas, vérifiez qu'Ollama est bien lancé (`systemctl status ollama` ou application ouverte) et que le modèle spécifié dans le `config.json` a bien été préalablement téléchargé (`ollama list`).

## Ressources

- [Documentation officielle de Continue.dev](https://docs.continue.dev/) — Guide complet de configuration
- [Site officiel d'Ollama](https://ollama.com/) — Catalogue des modèles disponibles
- [Modèles recommandés pour le code sur Ollama](https://ollama.com/library?category=tools) — Parcourez les LLMs spécialisés dans le développement
