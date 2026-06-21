---
title: "Déployer Tabby en local : l'alternative open source à GitHub Copilot"
date: 2026-06-21
author: Nicolas BODAINE
tags:
  - IA
  - Assistant de code
  - Docker
  - Auto-hébergement
difficulty: intermédiaire
os: Linux
status: publié
---

# Déployer Tabby en local : l'alternative open source à GitHub Copilot

!!! abstract "Résumé"
    Apprenez à déployer **Tabby**, un assistant de code intelligent auto-hébergé, pour bénéficier d'une complétion de code type GitHub Copilot sans envoyer vos données sur le cloud. Idéal pour garantir la confidentialité de vos projets de développement.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux (Ubuntu / Debian) avec Docker |
| Dernière mise à jour | 2026-06-21 |

## Contexte

GitHub Copilot a révolutionné la complétion de code par l'IA, mais il pose des défis en matière de confidentialité des données, d'enfermement propriétaire et de coût d'abonnement. 

**Tabby** est une alternative open source conçue pour être auto-hébergée. Il propose une API compatible avec les plugins d'éditeurs (VS Code, JetBrains, Neovim) et télécharge automatiquement les modèles d'IA nécessaires (comme *StarCoder* ou *CodeLlama*) pour vous assister localement, que ce soit sur CPU ou GPU.

## Prérequis

- Un système Linux avec **Docker** installé.
- Au minimum 8 Go de RAM (16 Go recommandés).
- (Optionnel mais très recommandé) Un GPU NVIDIA avec les drivers propriétaires et le *NVIDIA Container Toolkit* configurés pour de meilleures performances de complétion en temps réel.

## Procédure

### Étape 1 : Créer le répertoire de données

Tabby a besoin d'un espace local pour télécharger et stocker les modèles d'IA afin d'éviter de les retélécharger à chaque démarrage de conteneur.

```bash
# Création du dossier caché dans le répertoire utilisateur
mkdir -p ~/.tabby
```

### Étape 2 : Lancer Tabby via Docker

Nous allons utiliser Docker pour déployer Tabby. Par défaut, Tabby utilise le modèle `StarCoder-1B`, qui offre un excellent compromis entre légèreté et pertinence.

=== "Déploiement classique (CPU)"

    Si vous n'avez pas de carte graphique dédiée, utilisez cette commande. Les temps de réponse seront un peu plus longs mais suffisants pour tester :

    ```bash
    docker run -it \
      -p 8080:8080 \
      -v ~/.tabby:/data \
      tabbyml/tabby serve \
      --model StarCoder-1B \
      --device cpu
    ```

=== "Déploiement accéléré (GPU NVIDIA)"

    Si vous disposez d'un GPU compatible, utilisez le flag `--gpus all` et précisez `--device cuda` pour bénéficier d'une latence extrêmement faible :

    ```bash
    docker run -it \
      --gpus all \
      -p 8080:8080 \
      -v ~/.tabby:/data \
      tabbyml/tabby serve \
      --model StarCoder-1B \
      --device cuda
    ```

!!! note "Téléchargement initial"
    Au premier lancement, le conteneur va télécharger les poids du modèle (environ 1.5 Go pour StarCoder-1B). Soyez patient, le service démarrera juste après.

### Étape 3 : Vérifier l'interface d'administration

Une fois le modèle chargé, Tabby expose une interface web sur le port `8080`. 

1. Ouvrez votre navigateur et accédez à l'URL suivante : `http://localhost:8080` (ou l'IP de votre serveur).
2. Vous tomberez sur le panneau de contrôle de Tabby, confirmant que l'API est en ligne et prête à accepter des requêtes.

### Étape 4 : Configurer votre éditeur (Exemple VS Code)

Pour exploiter Tabby, il faut relier votre IDE au serveur local.

1. Dans Visual Studio Code, ouvrez l'onglet **Extensions** (++ctrl+shift+x++).
2. Recherchez l'extension officielle **Tabby** (`TabbyML.vscode-tabby`) et installez-la.
3. Une fois installée, une icône Tabby apparaît dans la barre d'état en bas à droite.
4. Cliquez dessus, ouvrez les paramètres de l'extension et modifiez l'**Endpoint** pour indiquer l'URL de votre serveur local :
   `http://localhost:8080`
5. Vérifiez que la connexion est établie (l'icône devient active/verte).

## Vérification

Pour tester l'efficacité de la complétion :

1. Créez un nouveau fichier `app.py` (ou `app.js`).
2. Écrivez un commentaire ou le début d'une fonction, par exemple :

```python
# Fonction pour calculer la suite de Fibonacci
def fibonacci(n):
```

3. Attendez quelques secondes. L'IA devrait vous proposer la suite du code en gris (`ghost text`).
4. Appuyez sur ++tab++ pour accepter la suggestion.

!!! success "Résultat attendu"
    La proposition de code s'affiche instantanément sans nécessiter aucune connexion internet sortante, validant ainsi votre environnement d'assistance au code local !

## Ressources

- [Dépôt GitHub de Tabby](https://github.com/TabbyML/tabby) — Code source et documentation officielle de l'outil.
- [Modèles disponibles](https://tabby.tabbyml.com/docs/models/) — Liste des modèles IA supportés (StarCoder, CodeLlama, Deepseek, etc.) et recommandations matérielles.