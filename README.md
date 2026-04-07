# Wiki Tech

Wiki technique personnel de NicoBOD — notes, découvertes, débugs et astuces.

Thèmes : systèmes, réseaux, cloud, cybersécurité, IA, automatisation, logiciels.

**Consulter le wiki :** [wiki.bodaine.fr](https://wiki.bodaine.fr)

## Ajouter du contenu

1. Cloner le repo : `git clone git@github.com:NicoBOD/wiki-tech.git`
2. Copier le template : `cp docs/_template.md docs/<catégorie>/ma-note.md`
3. Éditer la note : garder les blocs pertinents, supprimer les autres
4. Commit et push sur `main` — le site se met à jour automatiquement

## Utiliser le template

Le fichier `docs/_template.md` est un modèle polyvalent pour toutes les notes. Il contient :

- **Métadonnées** (frontmatter YAML) : titre, date, auteur, tags, difficulté, OS, statut
- **En-tête** : résumé et tableau récapitulatif
- **7 blocs modulaires** adaptés à chaque type de note :

| Bloc | Usage |
|------|-------|
| Contexte | Situation de départ, besoin, problème |
| Prérequis | Liste des prérequis |
| Procédure | Étapes pas-à-pas avec variantes OS |
| Problème / Solution | Erreur + message + résolution |
| Aide-mémoire | Tableau de commandes / actions |
| Vérification | Commande de vérification + résultat attendu |
| Ressources | Liens utiles |

Chaque bloc est précédé d'un commentaire HTML (`<!-- BLOC: ... -->`) qui indique quand l'utiliser. Ces commentaires ne s'affichent pas dans le rendu final.
