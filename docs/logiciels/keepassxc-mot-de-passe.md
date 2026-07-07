---
title: "Gérer ses mots de passe hors-ligne en toute sécurité avec KeePassXC"
date: 2026-06-24
author: Nicolas BODAINE
tags:
  - securite
  - mot-de-passe
  - keepassxc
  - logiciels
difficulty: débutant
os: Windows | macOS | Linux
status: publié
---

# Gérer ses mots de passe hors-ligne en toute sécurité avec KeePassXC

!!! abstract "Résumé"
    KeePassXC est un gestionnaire de mots de passe libre, open-source et multiplateforme qui stocke vos identifiants localement. Ce tutoriel montre comment l'installer, créer un coffre-fort chiffré, organiser vos mots de passe et mettre en place des sauvegardes fiables.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Windows / macOS / Linux |
| Dernière mise à jour | 2026-06-24 |

## Contexte

La gestion des mots de passe est un pilier de la cybersécurité, tant sur le plan personnel que professionnel. Face à la multiplication des comptes en ligne, il est humainement impossible de mémoriser des mots de passe forts et uniques pour chaque service. C'est là qu'interviennent les gestionnaires de mots de passe.

Dans ce tutoriel, nous allons découvrir **KeePassXC**, un gestionnaire de mots de passe libre, open-source et multiplateforme. Contrairement aux solutions cloud (comme Bitwarden, LastPass, etc.), KeePassXC stocke votre coffre-fort localement (hors-ligne), ce qui vous donne un contrôle total sur vos données, conformément aux bonnes pratiques recommandées par des autorités comme l'ANSSI.

## Prérequis

- Un ordinateur fonctionnant sous Linux, Windows ou macOS.
- Les droits d'administration pour l'installation du logiciel.

## Procédure

### Étape 1 : Installation de KeePassXC

=== "Linux (Ubuntu/Debian)"

    Ouvrez votre terminal et exécutez la commande suivante :
    ```bash
    sudo apt update
    sudo apt install -y keepassxc
    ```

=== "Windows / macOS"

    Téléchargez l'installateur adapté à votre système depuis le site officiel :
    [https://keepassxc.org/download/](https://keepassxc.org/download/)
    
    Une fois installé, lancez l'application.

### Étape 2 : Création de votre premier coffre-fort

Un coffre-fort KeePassXC est un fichier (portant généralement l'extension `.kdbx`) qui contient toutes vos données chiffrées.

1. Cliquez sur **Créer une nouvelle base de données**.
2. Renseignez un **Nom de la base de données** (ex: `MonCoffreFort_ZamanIA`) et une description optionnelle. Cliquez sur *Continuer*.
3. **Paramètres de chiffrement** : Les paramètres par défaut (Temps de déchiffrement ciblé à 1 seconde) offrent un bon compromis entre sécurité et confort d'utilisation. Laissez-les tels quels et cliquez sur *Continuer*.
4. **Authentification de la base de données** : C'est l'étape la plus critique. 
    - Entrez un **Mot de passe principal (Master Password)**. 
    - *Règle d'or :* Ce mot de passe doit être long, complexe, mais surtout **mémorisable par vous seul**. Utilisez par exemple une *phrase de passe* (ex: `LeChatNoirDortSurLeCanapéRouge!123`).
    - Saisissez-le à nouveau pour confirmer.
5. Cliquez sur **Terminé**, puis choisissez un emplacement sûr sur votre ordinateur pour enregistrer le fichier `.kdbx`.

### Étape 3 : Ajout d'une entrée et génération de mot de passe

Maintenant que votre coffre-fort est ouvert, ajoutons vos premiers identifiants.

1. Cliquez sur l'icône **+** (ou allez dans *Entrées > Ajouter une nouvelle entrée*).
2. Renseignez les champs :
    - **Titre :** Le nom du service (ex: `GitHub Nicolas`).
    - **Nom d'utilisateur :** L'adresse email ou le pseudo associé.
    - **URL :** L'adresse web du service (utile pour l'intégration navigateur).
3. **Le Mot de passe :**
    - Plutôt que de choisir un mot de passe vous-même, cliquez sur l'icône représentant un dé noir à côté du champ mot de passe.
    - Cela ouvre le **Générateur de mots de passe**.
    - Réglez la longueur (ex: 20 caractères) et cochez les types de caractères (majuscules, minuscules, chiffres, caractères spéciaux).
    - Cliquez sur l'icône **Appliquer** (la coche verte) pour injecter ce nouveau mot de passe fort dans votre entrée.
4. Cliquez sur **OK** pour sauvegarder l'entrée.

### Étape 4 : Organisation : Utilisation des Groupes

Pour garder un coffre-fort lisible, surtout lorsque vous avez des centaines d'entrées, il est recommandé d'utiliser des Groupes (Dossiers).

1. Dans le panneau de gauche, faites un clic droit sur `Racine` et choisissez **Nouveau groupe**.
2. Nommez le groupe (ex: `Réseaux Sociaux`, `Banques`, `Serveurs Perso`) et attribuez-lui une icône personnalisée pour le repérer visuellement.
3. Vous pouvez glisser-déposer les entrées existantes dans les groupes correspondants.

### Étape 5 : Bonnes pratiques de sauvegarde

Puisque KeePassXC est une solution **hors-ligne**, votre coffre-fort est un simple fichier `.kdbx` stocké sur votre disque dur. **Si vous perdez ce fichier (casse du disque, vol), vous perdez tous vos mots de passe !**

#### Stratégie de sauvegarde (La règle du 3-2-1)
1. **Faites des copies régulières** de votre fichier `.kdbx`.
2. Conservez-le sur au moins **deux supports différents** (ex: votre disque dur et une clé USB).
3. Gardez une copie **hors site** (ex: sur un serveur distant, un NAS personnel, ou même un Cloud grand public comme Google Drive ou Nextcloud). 
    - *Note de sécurité :* Puisque le fichier `.kdbx` est fortement chiffré par votre Master Password, le stocker sur un Cloud public ne présente pas de risque majeur, à condition que votre mot de passe principal soit robuste.

## Checklist

- [x] Installer KeePassXC
- [ ] Créer une base de données `.kdbx`
- [ ] Définir un mot de passe principal fort
- [ ] Ajouter une première entrée et générer un mot de passe fort
- [ ] Organiser les entrées dans des groupes
- [ ] Mettre en place une routine de sauvegarde régulière

## Vérification

Pour valider le bon fonctionnement de KeePassXC :

1. Fermez l'application ou verrouillez la base de données.
2. Ouvrez à nouveau le fichier `.kdbx` en saisissant votre mot de passe principal.
3. Double-cliquez sur l'entrée créée pour copier les identifiants et tester la connexion sur le site cible.

!!! success "Résultat attendu"
    La base de données s'ouvre correctement avec le mot de passe maître, et les identifiants copiés permettent une authentification réussie.

## Ressources

- [Site officiel KeePassXC](https://keepassxc.org/) — Téléchargement et actualités.
- [Documentation officielle de KeePassXC](https://keepassxc.org/docs/) — Manuel d'utilisation détaillé.
- [Recommandations de l'ANSSI sur les mots de passe](https://messervices.cyber.gouv.fr/documents-guides/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf) — Guide des bonnes pratiques pour la sécurité des identifiants.
