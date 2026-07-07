---
title: Créer une équipe d'agents IA autonomes avec CrewAI et Ollama
date: 2026-06-28
author: Nicolas BODAINE
tags:
  - ia
  - llm
  - agents
  - python
  - ollama
  - crewai
difficulty: intermédiaire
os: Linux / Windows / macOS
status: publié
---

# Créer une équipe d'agents IA autonomes avec CrewAI et Ollama

!!! abstract "Résumé"
    Apprenez à orchestrer une équipe d'agents IA autonomes sur votre propre machine, en combinant le framework Python **CrewAI** et les modèles locaux gérés par **Ollama**. Idéal pour automatiser des tâches complexes nécessitant recherche et synthèse, sans dépendre de services cloud payants.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Multi-plateforme (Linux recommandé) |
| Dernière mise à jour | 2026-06-28 |

## Contexte

Dans le domaine de l'intelligence artificielle, on passe progressivement d'un modèle de simple "chatbot" (une conversation avec un seul modèle) à des systèmes "multi-agents". Ces systèmes permettent à plusieurs IA spécialisées de collaborer : un agent cherche des informations, un autre les analyse, et un troisième rédige le rapport final.

**CrewAI** est un framework populaire pour orchestrer ces équipes virtuelles (ou "crews"). Couplé à **Ollama**, il vous permet d'exécuter l'ensemble de l'équipe **localement**, de manière gratuite et privée.

## Prérequis

- [x] **Ollama** installé sur votre machine (voir [le tutoriel dédié](installer-utiliser-ollama-llm-local.md)).
- [x] **Python 3.10** ou supérieur installé.
- [x] Un environnement virtuel Python configuré.

## Procédure

### Étape 1 : Préparation du modèle local avec Ollama

CrewAI va envoyer des requêtes au modèle local. Pour des tâches de raisonnement ("agentiques"), il est conseillé d'utiliser un modèle performant comme `llama3` ou `mistral`.

1. Ouvrez un terminal.
2. Téléchargez et démarrez le modèle avec Ollama :

```bash
ollama run mistral
```

*Note : Une fois le prompt `>>>` affiché, vous pouvez quitter avec `Ctrl+D`. Le modèle restera disponible en arrière-plan via l'API locale d'Ollama.*

### Étape 2 : Installation des bibliothèques Python

Dans votre environnement de développement, installez le framework CrewAI et les outils nécessaires pour communiquer avec Ollama.

```bash
# Créer et activer un environnement virtuel (optionnel mais recommandé)
python3 -m venv env_agents
source env_agents/bin/activate  # Sur Linux/macOS
# .\env_agents\Scripts\activate # Sur Windows

# Installer CrewAI et LangChain Community (pour l'intégration Ollama)
pip install crewai langchain-community
```

### Étape 3 : Création du script de l'équipe (Crew)

Nous allons créer un scénario simple : 
- Un **Chercheur** (Researcher) chargé de trouver des informations sur un sujet technique.
- Un **Rédacteur** (Writer) chargé de synthétiser ces informations en un court paragraphe.

Créez un fichier `equipe_ia.py` et copiez le code suivant :

```python title="equipe_ia.py" linenums="1"
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama

# 1. Connexion au modèle local via Ollama
llm_local = Ollama(model="mistral")

# 2. Définition des Agents
chercheur = Agent(
    role='Chercheur Technologique Senior',
    goal='Découvrir les dernières avancées en matière de conteneurisation',
    backstory="""Tu es un chercheur expert en infrastructure IT. 
    Tu adores lire de la documentation et vulgariser les concepts complexes.""",
    verbose=True,
    allow_delegation=False,
    llm=llm_local
)

redacteur = Agent(
    role='Rédacteur Technique',
    goal='Rédiger un résumé clair et engageant sur les conteneurs',
    backstory="""Tu es un rédacteur reconnu pour ta capacité à expliquer 
    la technologie de manière simple. Tu travailles en étroite collaboration 
    avec le chercheur.""",
    verbose=True,
    allow_delegation=False,
    llm=llm_local
)

# 3. Définition des Tâches (Tasks)
tache_recherche = Task(
    description="""Identifie les 3 principaux avantages de l'utilisation 
    de Podman par rapport à Docker en 2026. Fournis des points précis.""",
    expected_output="Une liste à puces des 3 avantages de Podman.",
    agent=chercheur
)

tache_redaction = Task(
    description="""À partir de la liste fournie par le chercheur, rédige 
    un petit paragraphe d'introduction (3-4 phrases) pour un blog IT.""",
    expected_output="Un court paragraphe rédigé en français.",
    agent=redacteur
)

# 4. Création de l'équipe (Crew)
equipe = Crew(
    agents=[chercheur, redacteur],
    tasks=[tache_recherche, tache_redaction],
    process=Process.sequential # Les tâches s'exécutent l'une après l'autre
)

# 5. Lancement de la mission
print("Démarrage de l'équipe d'agents IA...")
resultat_final = equipe.kickoff()

print("\n\n=== RÉSULTAT FINAL ===")
print(resultat_final)
```

### Étape 4 : Exécution et observation

Lancez le script depuis votre terminal :

```bash
python equipe_ia.py
```

Vous verrez dans la console le "raisonnement" de vos agents (grâce à `verbose=True`). Le Chercheur va d'abord traiter sa tâche en sollicitant le modèle Ollama, puis il passera ses conclusions au Rédacteur qui formulera la réponse finale.

## Problème fréquent

!!! failure "Erreur de connexion (Connection refused)"
    Si vous obtenez une erreur de type `Connection refused` ou `Failed to connect to localhost:11434`, cela signifie que le service Ollama ne tourne pas en arrière-plan. Assurez-vous d'avoir bien démarré Ollama ou lancé un `ollama run <modele>` avant d'exécuter votre script Python.

## Glossaire

Agent
:   Dans CrewAI, une entité autonome avec un rôle, un objectif et une histoire (backstory) spécifique, capable d'interagir avec un LLM.

Task (Tâche)
:   Une mission précise assignée à un agent, avec une description claire de ce qui est attendu comme résultat (`expected_output`).

Crew (Équipe)
:   L'ensemble des agents et des tâches orchestrés pour atteindre un but commun, selon un processus défini (séquentiel, hiérarchique, etc.).

## Ressources

- [Documentation officielle CrewAI](https://docs.crewai.com/) — Concepts de base et orchestration avancée.
- [Site officiel Ollama](https://ollama.com/) — Téléchargement et gestion des modèles locaux.
