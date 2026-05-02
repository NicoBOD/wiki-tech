---
title: Titre de la note
date: 2026-05-02
author: Nicolas BODAINE
tags:
  - tag1
  - tag2
difficulty: débutant | intermédiaire | avancé
os: Ubuntu 24.04 | Windows Server 2025 | ...
status: brouillon | publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Titre de la note

!!! abstract "Résumé"
    Brève description de ce que cette note couvre et pourquoi.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-05-02 |

<!-- ============================================================ -->
<!-- BLOCS MODULAIRES                                              -->
<!-- Gardez les blocs pertinents, supprimez les autres.            -->
<!-- Les commentaires HTML ne s'affichent pas dans le rendu final. -->
<!-- ============================================================ -->

<!-- BLOC: Contexte — Utilisez pour les tutos et fiches debug -->
## Contexte

Décrivez la situation de départ, le besoin ou le problème rencontré.

<!-- BLOC: Prérequis — Utilisez pour les tutos et procédures -->
## Prérequis

- Prérequis 1
- Prérequis 2

<!-- BLOC: Procédure — Utilisez pour les tutos pas-à-pas -->
## Procédure

### Étape 1 : Description

=== "Linux"

    ```bash
    commande linux
    ```

=== "Windows"

    ```powershell
    commande windows
    ```

### Étape 2 : Description

=== "Linux"

    ```bash
    commande linux
    ```

=== "Windows"

    ```powershell
    commande windows
    ```

<!-- BLOC: Problème / Solution — Utilisez pour les fiches debug -->
## Problème

Description de l'erreur ou du symptôme observé.

!!! failure "Message d'erreur"
    Collez ici le message d'erreur exact.

## Solution

Étapes de résolution.

<!-- BLOC: Aide-mémoire — Utilisez pour les fiches de référence -->
## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `commande` | Ce qu'elle fait |

<!-- BLOC: Checklist — Utilisez pour les listes de vérification -->
## Checklist

- [x] Étape terminée
- [ ] Étape à faire
- [ ] Étape à faire

<!-- BLOC: Glossaire — Utilisez pour définir des termes techniques -->
## Glossaire

Terme 1
:   Définition du terme 1.

Terme 2
:   Définition du terme 2.

<!-- BLOC: Vérification — Utilisez après une procédure ou une solution -->
## Vérification

Comment vérifier que tout fonctionne :

```bash
commande de vérification
```

!!! success "Résultat attendu"
    Ce que vous devez observer si tout est OK.

<!-- BLOC: Ressources — Utilisez pour référencer docs et sources -->
## Ressources

- [Lien 1](url) — Description
- [Lien 2](url) — Description

<!-- ============================================================ -->
<!-- RÉFÉRENCE SYNTAXE                                             -->
<!-- Aide-mémoire des syntaxes Markdown disponibles sur ce wiki.   -->
<!-- Supprimez cette section dans vos notes — elle est juste là    -->
<!-- pour vous rappeler ce qui est disponible.                     -->
<!-- ============================================================ -->

<!-- RÉFÉRENCE: Syntaxes Markdown disponibles

=== Mise en forme ===
**gras**                            Texte en gras
*italique*                          Texte en italique
==texte surligné==                  Texte surligné (mark)
^^texte^^                           Exposant (caret)
~texte~                             Indice (tilde)
~~texte barré~~                     Texte barré (tilde)
`code inline`                       Code en ligne
++ctrl+s++                          Touches clavier (keys)

=== Suivi de modifications (critic) ===
{++texte ajouté++}                  Ajout
{--texte supprimé--}                Suppression
{~~ancien~>nouveau~~}               Remplacement
{==texte commenté==}{>>raison<<}    Commentaire

=== Symboles automatiques (smartsymbols) ===
(c) (r) (tm)                        © ® ™
+/- -- >  <--  <-- >                 ± → ← ↔
1/4 1/2 3/4                          ¼ ½ ¾
!=                                   ≠

=== Listes de tâches ===
- [x] Tâche terminée
- [ ] Tâche à faire

=== Listes de définitions ===
Terme
:   Définition du terme.

=== Notes de bas de page ===
Texte avec une note[^1].
[^1]: Contenu de la note de bas de page.

=== Abréviations (tooltip au survol) ===
*[API]: Application Programming Interface
*[DNS]: Domain Name System

=== Onglets ===
=== "Onglet 1"
    Contenu de l'onglet 1.
=== "Onglet 2"
    Contenu de l'onglet 2.

=== Admonitions (boîtes d'alerte) ===
!!! note "Titre"         Note / information
!!! tip "Titre"          Astuce
!!! warning "Titre"      Avertissement
!!! danger "Titre"       Danger
!!! success "Titre"      Succès
!!! failure "Titre"      Échec
!!! abstract "Titre"     Résumé
!!! question "Titre"     Question
!!! example "Titre"        Exemple
!!! quote "Titre"        Citation

??? note "Titre"         Admonition dépliable (fermée par défaut)
???+ note "Titre"        Admonition dépliable (ouverte par défaut)

=== Blocs de code ===
```python title="script.py" linenums="1" hl_lines="2 3"
def hello():
    print("Hello")      # ligne surlignée
    return True          # ligne surlignée
```

=== Icônes Material ===
:material-server:       Serveur
:material-lan:          Réseau
:material-cloud:        Cloud
:material-shield-lock:  Sécurité
:material-robot:        IA
:material-cog:          Automatisation
:material-bug:          Bug
:material-lightbulb:    Astuce

-->