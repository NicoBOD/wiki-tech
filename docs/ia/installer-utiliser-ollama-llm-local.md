---
title: Installer et utiliser Ollama pour exécuter des LLM en local
date: 2026-06-06
author: Nicolas BODAINE
tags:
  - ia
  - llm
  - ollama
  - local
  - ubuntu
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Installer et utiliser Ollama pour exécuter des LLM en local

!!! abstract "Résumé"
    Ce tutoriel vous guide pas-à-pas dans l'installation d'Ollama sur un serveur Ubuntu, et vous montre comment télécharger et interroger des modèles de langage (LLM) directement en local, sans dépendre d'API cloud (et donc sans frais ni fuite de données).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-06 |

## Contexte

De nombreuses solutions d'intelligence artificielle reposent sur des API externes (comme OpenAI ou Anthropic), ce qui soulève parfois des problèmes de confidentialité ou de coût pour des projets de test ou des données sensibles.
**Ollama** est un outil en ligne de commande open source permettant de faire tourner très simplement des modèles de langage puissants (comme Llama 3, Mistral, ou Phi-3) directement sur votre propre machine.

C'est un excellent moyen de se familiariser avec les LLM (Large Language Models) dans un environnement de laboratoire sécurisé.

## Prérequis

- Un serveur ou une machine virtuelle sous **Ubuntu 24.04**.
- Un accès terminal avec les privilèges `sudo`.
- **Au moins 8 Go de RAM** recommandés (16 Go pour des modèles plus larges).
- *(Optionnel mais recommandé)* Une connexion internet rapide pour télécharger les modèles (plusieurs Go chacun).

## Procédure

### Étape 1 : Installer Ollama

L'installation d'Ollama est simplifiée grâce à un script d'installation officiel qui configure automatiquement le service en arrière-plan.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

!!! note "Service systemd"
    Une fois le script terminé, Ollama s'exécute automatiquement en tant que service système (`systemd`). Vous pouvez vérifier son état avec `systemctl status ollama`.

### Étape 2 : Vérifier l'installation

Assurez-vous que la commande Ollama est bien disponible et que le service répond.

```bash
ollama --version
```

!!! success "Résultat attendu"
    ```text
    ollama version is 0.1.x
    ```

### Étape 3 : Télécharger et exécuter un modèle (Llama 3 ou Mistral)

Pour interagir avec un LLM, il faut d'abord en télécharger un. Ollama utilise la commande `run` qui télécharge le modèle s'il n'est pas déjà présent en local, puis ouvre un prompt interactif.

Par exemple, pour exécuter **Llama 3** (le modèle de Meta, très performant pour sa taille) :

```bash
ollama run llama3
```

*(Si vous préférez un modèle français open-weight, vous pouvez utiliser `ollama run mistral`)*.

Lors du premier lancement, le téléchargement peut prendre quelques minutes selon votre connexion.

### Étape 4 : Interagir avec le LLM

Une fois le modèle chargé, vous arrivez dans un prompt interactif. Vous pouvez y taper vos questions directement :

```text
>>> Explique-moi ce qu'est un LLM en une phrase simple.
Un LLM (Grand Modèle de Langage) est un programme d'intelligence artificielle entraîné sur de vastes quantités de texte pour comprendre et générer du langage humain de manière naturelle.

>>> /bye
```

Utilisez `/bye` ou `Ctrl+D` pour quitter le prompt interactif.

### Étape 5 : Gérer ses modèles locaux

Ollama stocke les modèles sur votre disque. Vous pouvez lister ceux qui sont disponibles localement, ou les supprimer pour libérer de l'espace.

**Lister les modèles installés :**
```bash
ollama list
```

**Supprimer un modèle :**
```bash
ollama rm llama3
```

## Intégration via l'API locale

Ollama expose également une API REST locale sur le port `11434`, ce qui est parfait pour l'intégrer dans vos propres scripts Python ou applications.

### Exemple de requête avec `curl`

Vous pouvez interroger votre modèle local avec une simple requête HTTP :

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Pourquoi le ciel est bleu ?",
  "stream": false
}'
```

Le retour sera un objet JSON contenant la réponse du modèle générée sur votre propre serveur.

## Checklist

- [x] Installer Ollama via le script officiel.
- [x] Vérifier que le service systemd est actif.
- [x] Lancer un modèle (`llama3` ou `mistral`) en mode interactif.
- [x] Tester l'API locale avec `curl`.

## Glossaire

LLM (Large Language Model)
:   Modèle d'intelligence artificielle capable de comprendre, traduire et générer du texte de manière cohérente.

Ollama
:   Outil permettant d'exécuter, de gérer et de servir des LLM localement sans configuration complexe.

## Ressources

- [Site officiel d'Ollama](https://ollama.com/) — Modèles disponibles et documentation de base.
- [Dépôt GitHub d'Ollama](https://github.com/ollama/ollama) — Pour les paramètres avancés et le troubleshooting.
