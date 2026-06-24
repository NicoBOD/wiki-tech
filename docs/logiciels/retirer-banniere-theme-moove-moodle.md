---
title: Retirer le bandeau publicitaire du thème Moove de Moodle
date: 2026-06-24
author: Nicolas BODAINE
tags:
  - Moodle
  - Moove
  - CSS
  - PHP
difficulty: intermédiaire
os: Linux
status: publié
---

# Retirer le bandeau publicitaire du thème Moove de Moodle

!!! abstract "Résumé"
    Le thème Moove pour Moodle affiche par défaut un bandeau promotionnel "Conecti.me Partners" sur la page de notifications d'administration. Ce guide explique comment le masquer proprement via l'interface graphique (CSS personnalisé) ou le supprimer définitivement au niveau du code PHP.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Tout environnement (Moodle 4.x / 5.x) |
| Dernière mise à jour | 2026-06-24 |

---

## Contexte

Le thème **Moove** (`theme_moove`) est l'un des thèmes les plus populaires pour Moodle en raison de son design moderne et épuré. Cependant, l'éditeur du thème (Conecti.me) intègre par défaut un bandeau de publicité ("Conecti.me Partners" promouvant ReadSpeaker et d'autres partenaires) tout en haut de la page **Administration du site > Notifications**.

Bien que cette publicité aide à financer le projet, elle peut nuire à l'esthétique professionnelle d'une plateforme d'apprentissage d'entreprise ou d'établissement scolaire.

---

## Méthode 1 : Masquage par l'interface graphique (CSS personnalisé)

Cette méthode est la plus simple et la plus sûre. Elle ne nécessite pas d'accès aux fichiers du serveur et résiste aux mises à jour du thème. Elle consiste à injecter une règle CSS pour masquer l'élément publicitaire.

### Procédure

1. Connectez-vous à Moodle en tant qu'**administrateur**.
2. Naviguez vers **Administration du site** > **Apparence** > **Thèmes** > **Moove**.
3. Cliquez sur l'onglet **Paramètres avancés** (Advanced settings).
4. Localisez le champ de saisie nommé **CSS brut** (`rawscss`).
5. Copiez et collez le code suivant à la fin du champ :

```css
/* Masquer le bandeau de publicité Conecti.me Partners */
.conectime-partners-banner {
    display: none !important;
}
```

6. Cliquez sur le bouton **Enregistrer les modifications** en bas de page.
7. Allez dans **Administration du site** > **Développement** > **Vider les caches** pour appliquer immédiatement le changement.

!!! success "Résultat"
    Le bandeau disparaît visuellement pour tous les administrateurs naviguant sur les pages de configuration.

---

## Méthode 2 : Suppression définitive dans le code source (PHP)

Si vous gérez Moodle en conteneur Docker (stateless) ou si vous préférez éviter que le serveur web ne charge et ne rende inutilement ces éléments dans le DOM, vous pouvez supprimer le bandeau directement du code PHP du thème.

### Prérequis

* Un accès en écriture aux fichiers du serveur Moodle (ou dans votre répertoire de build Docker).
* Le fichier concerné se trouve à l'emplacement : `theme/moove/classes/output/core/admin_renderer.php`.

### Procédure

#### Étape 1 : Retrait de l'appel dans le Renderer d'administration

Ouvrez le fichier `theme/moove/classes/output/core/admin_renderer.php` avec votre éditeur. Recherchez la méthode `admin_notifications_page(...)` et supprimez ou commentez la ligne suivante (autour de la ligne 97) :

```diff
         $output .= $this->header();
         $output .= $this->output->heading(get_string('notifications', 'admin'));
         $output .= $this->conectime_services_and_support_content();
-        $output .= $this->conectime_partners_content();
         $output .= $this->maturity_info($maturity);
```

#### Étape 2 : Suppression de la méthode privée du Renderer

Faites défiler le fichier jusqu'à la fin et supprimez la déclaration de la méthode `conectime_partners_content()` (ainsi que son bloc de commentaire de documentation) :

```diff
-    /**
-     * Display services and support content.
-     *
-     * @return string the campaign content raw html.
-     */
-    private function conectime_partners_content(): string {
-        return $this->render_from_template('theme_moove/moove/conectime_partners_banner', []);
-    }
 }
```

#### Étape 3 (Optionnel) : Nettoyage des fichiers du thème

Pour une propreté optimale du dépôt et de l'image, vous pouvez supprimer les ressources associées au bandeau qui ne sont plus appelées :

* Supprimez le template mustache : `theme/moove/templates/moove/conectime_partners_banner.mustache`
* Supprimez le logo SVG partenaire : `theme/moove/pix/partner-readspeaker.svg`

---

## Vérification

Pour vérifier que la suppression ou le masquage a réussi :

1. Accédez à la page d'administration : `https://<votre-moodle>/admin/index.php`.
2. Inspectez la page (touche ++f12++ sur votre navigateur).
3. Recherchez l'élément avec la classe `.conectime-partners-banner`.
   * **Avec la Méthode 1** : L'élément est présent mais possède la propriété CSS `display: none`.
   * **Avec la Méthode 2** : L'élément n'apparaît plus du tout dans le code source de la page (le DOM).

---

## Ressources

* [Dépôt GitHub officiel du thème Moove](https://github.com/willianmano/moodle-theme_moove) — Pour suivre l'évolution du code source.
* [Documentation Moodle - Personnalisation CSS](https://docs.moodle.org/fr/Param%C3%A8tres_des_th%C3%A8mes) — Informations générales sur l'ajout de styles personnalisés.
