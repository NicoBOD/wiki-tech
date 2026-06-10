---
title: Créer un script Python interagissant avec un LLM local via Ollama
date: 2026-06-09
author: Nicolas BODAINE
tags:
  - ollama
  - python
  - ia
  - llm
  - api
difficulty: intermédiaire
os: Linux | Windows | macOS
status: publié
---

# Créer un script Python interagissant avec un LLM local via Ollama

!!! abstract "Résumé"
    Apprenez à utiliser la bibliothèque Python officielle d'Ollama pour intégrer facilement des modèles d'intelligence artificielle locaux (comme Llama 3, Mistral, etc.) directement dans vos propres scripts ou applications.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Multiplateforme |
| Dernière mise à jour | 2026-06-09 |

## Contexte

Maintenant que vous avez [installé et configuré Ollama en local](installer-utiliser-ollama-llm-local.md), vous pouvez interagir avec l'IA via le terminal. Cependant, pour exploiter véritablement la puissance des LLM (Large Language Models), il est très utile de pouvoir les interroger par la programmation. 

L'équipe d'Ollama propose une bibliothèque Python officielle qui enveloppe leur API, rendant la génération de texte, le chat, et le streaming de réponses incroyablement simples à implémenter dans vos propres projets logiciels, scripts d'automatisation ou bots de discussion.

## Prérequis

- [Ollama installé](installer-utiliser-ollama-llm-local.md) et en cours d'exécution sur votre machine (ou accessible sur le réseau).
- Un modèle de langage déjà téléchargé dans Ollama (par exemple `llama3` ou `mistral` : `ollama run mistral`).
- Python 3.8 ou supérieur installé sur votre système.

## Procédure

### Étape 1 : Installer le paquet Python Ollama

Nous allons utiliser `pip` pour installer la bibliothèque officielle. Il est recommandé de le faire dans un environnement virtuel.

```bash title="Terminal"
# Création et activation d'un environnement virtuel (optionnel mais recommandé)
python3 -m venv venv
source venv/bin/activate

# Installation du paquet
pip install ollama
```

### Étape 2 : Génération de texte basique (One-shot)

Commençons par un script simple qui envoie une requête (prompt) et attend la réponse complète avant de l'afficher. 

Créez un fichier nommé `generer_texte.py` :

```python title="generer_texte.py" linenums="1"
import ollama

# Définissez le modèle que vous souhaitez utiliser
MODELE = 'mistral' # Assurez-vous d'avoir fait un 'ollama run mistral' avant

print(f"Interrogation du modèle {MODELE} en cours...\n")

reponse = ollama.generate(model=MODELE, prompt='Explique-moi le fonctionnement du protocole DNS en trois phrases.')

# Affichage du résultat
print("Réponse de l'IA :")
print(reponse['response'])
```

Pour l'exécuter : `python generer_texte.py`

### Étape 3 : Conversation avec historique (Chat)

Pour construire un chatbot, le modèle doit se souvenir du contexte de la conversation. La méthode `chat` est conçue pour cela en gérant des listes de messages.

Créez un fichier `chatbot_simple.py` :

```python title="chatbot_simple.py" linenums="1"
import ollama

MODELE = 'mistral'

# On initialise l'historique avec un message système (optionnel)
historique = [
  {'role': 'system', 'content': 'Tu es un assistant informatique expert en réseaux. Tu réponds de manière concise.'}
]

print("Chatbot démarré. Tapez 'quit' pour quitter.")

while True:
    utilisateur_input = input("\nVous : ")
    
    if utilisateur_input.lower() in ['quit', 'exit']:
        break
        
    # Ajouter le message de l'utilisateur à l'historique
    historique.append({'role': 'user', 'content': utilisateur_input})
    
    # Appeler l'API
    reponse = ollama.chat(model=MODELE, messages=historique)
    
    message_ia = reponse['message']['content']
    print(f"\nAssistant : {message_ia}")
    
    # Ajouter la réponse à l'historique pour le prochain tour
    historique.append({'role': 'assistant', 'content': message_ia})
```

### Étape 4 : Utiliser le streaming pour une meilleure expérience

Plutôt que d'attendre la génération complète de la réponse (ce qui peut prendre plusieurs secondes), vous pouvez afficher les mots au fur et à mesure qu'ils sont générés par le modèle, comme le fait ChatGPT.

Créez un fichier `chat_streaming.py` :

```python title="chat_streaming.py" linenums="1" hl_lines="6"
import ollama

# Le paramètre stream=True est la clé ici
stream = ollama.chat(
    model='mistral',
    messages=[{'role': 'user', 'content': 'Écris un petit poème sur Linux.'}],
    stream=True,
)

print("IA : ", end='', flush=True)

# On itère sur les morceaux de réponse (chunks) au fur et à mesure
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)

print() # Retour à la ligne à la fin
```

## Vérification

Pour vérifier que tout fonctionne bien, exécutez votre script de streaming :

```bash
python3 chat_streaming.py
```

!!! success "Résultat attendu"
    Vous devriez voir la réponse s'écrire mot par mot dans votre terminal, avec une utilisation de votre CPU ou GPU en local.

## Ressources

- [Dépôt GitHub de la librairie Python Ollama](https://github.com/ollama/ollama-python) — Documentation officielle et exemples avancés.
- [Documentation de l'API REST Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md) — Pour comprendre comment fonctionne le moteur en coulisse.