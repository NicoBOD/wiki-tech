---
title: Chiffrer et signer des fichiers avec GPG sous Linux
date: 2026-06-29
author: Nicolas BODAINE
tags:
  - gpg
  - chiffrement
  - signature
  - linux
  - sécurité
difficulty: intermédiaire
os: Linux (Debian, Ubuntu, etc.)
status: publié
---

# Chiffrer et signer des fichiers avec GPG sous Linux

!!! abstract "Résumé"
    GnuPG (GPG) est l'outil standard sous Linux pour le chiffrement et la signature de données. Ce tutoriel vous guidera dans la création de votre paire de clés, le chiffrement (symétrique et asymétrique) de fichiers, ainsi que leur signature numérique pour en garantir l'intégrité et l'authenticité.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux (Debian, Ubuntu, etc.) |
| Dernière mise à jour | 2026-06-29 |

## Contexte

La protection des données au repos et en transit est un pilier de la cybersécurité. GPG (Gnu Privacy Guard), implémentation open source de la norme OpenPGP, permet à la fois de garantir la **confidentialité** (seul le destinataire peut lire le fichier) et l'**authenticité** (on est sûr de l'identité de l'expéditeur) via des mécanismes de cryptographie asymétrique. Maîtriser GPG est indispensable pour tout administrateur système ou professionnel de l'IT.

## Prérequis

- Une machine sous Linux (Debian, Ubuntu, etc.).
- Le paquet `gnupg` installé (généralement présent par défaut).
- Un accès terminal.

## Procédure

### Étape 1 : Vérifier l'installation de GPG

Assurez-vous que GPG est bien présent sur votre système :

```bash
gpg --version
```

S'il n'est pas installé (rare), vous pouvez l'ajouter via votre gestionnaire de paquets :

```bash
# Sur Debian/Ubuntu
sudo apt update && sudo apt install gnupg
```

### Étape 2 : Chiffrement symétrique (méthode simple)

Le chiffrement symétrique utilise **un seul et même mot de passe** pour chiffrer et déchiffrer. C'est pratique pour protéger rapidement un fichier sans avoir besoin de générer de clés.

**1. Chiffrer un fichier :**

```bash
# Créez un fichier de test
echo "Mes secrets industriels" > secret.txt

# Chiffrez le fichier (l'option -c signifie "symmetric")
gpg -c secret.txt
```

GPG vous demandera de saisir et de confirmer un mot de passe. Le résultat est un nouveau fichier nommé `secret.txt.gpg`. Vous pouvez maintenant supprimer l'original de façon sécurisée (avec `shred` par exemple).

**2. Déchiffrer un fichier :**

```bash
# Déchiffrer le fichier et l'afficher (ou le sauvegarder)
gpg -d secret.txt.gpg > secret_dechiffre.txt
```

### Étape 3 : Générer une paire de clés (asymétrique)

Pour échanger des données de façon sécurisée sans avoir à transmettre un mot de passe, on utilise la cryptographie asymétrique (une clé publique à partager, une clé privée à garder secrète).

**1. Lancer l'assistant de création :**

```bash
gpg --full-generate-key
```

**2. Répondre aux questions de l'assistant :**
- **Type de clé** : Choisissez `(1) RSA et RSA` (par défaut).
- **Taille de la clé** : Tapez `4096` pour une sécurité maximale.
- **Validité** : Par exemple, `1y` (valable 1 an) ou `0` (n'expire jamais, déconseillé en prod).
- **Identité** : Renseignez vos Nom, Prénom, et adresse e-mail.
- **Mot de passe (passphrase)** : GPG vous demandera un mot de passe robuste pour protéger votre clé privée. **Ne l'oubliez pas !**

**3. Vérifier les clés générées :**

```bash
# Lister les clés publiques
gpg --list-keys

# Lister les clés privées (secrètes)
gpg --list-secret-keys
```

### Étape 4 : Exporter et importer une clé publique

Pour que quelqu'un puisse vous envoyer un fichier chiffré, il lui faut votre clé publique.

**1. Exporter votre clé publique :**

```bash
# Remplacez l'email par celui utilisé lors de la génération
gpg --armor --export votre.email@domaine.com > ma_cle_publique.asc
```
Le fichier `.asc` peut être partagé en toute sécurité.

**2. Importer la clé d'un tiers :**

```bash
gpg --import cle_du_collegue.asc
```

### Étape 5 : Chiffrer et déchiffrer en asymétrique

Maintenant que vous avez la clé publique d'un destinataire (ou la vôtre), vous pouvez chiffrer un fichier de façon asymétrique.

**1. Chiffrer pour un destinataire :**

```bash
# L'option -e (encrypt) et -r (recipient)
gpg -e -r email.destinataire@domaine.com document.pdf
```
Cela produit un fichier `document.pdf.gpg`. Seul le détenteur de la clé privée associée pourra le lire.

**2. Déchiffrer :**

```bash
gpg -d document.pdf.gpg > document_clair.pdf
```

### Étape 6 : Signer numériquement un fichier

La signature garantit que le fichier n'a pas été altéré et confirme qu'il provient bien de vous. Elle utilise **votre clé privée**.

**1. Signer en clair (Cleartext signature) :**
Utile pour les documents texte, le contenu reste lisible, mais une signature est ajoutée à la fin.

```bash
gpg --clearsign contrat.txt
```
Cela génère `contrat.txt.asc`.

**2. Créer une signature détachée :**
Utile pour les binaires ou archives (ISO, tar.gz). La signature est placée dans un fichier séparé.

```bash
gpg --detach-sign archive.tar.gz
```
Cela produit `archive.tar.gz.sig`.

## Vérification

Pour vérifier qu'une signature est valide (vous devez posséder la clé publique de l'expéditeur) :

```bash
# Vérifier une signature détachée
gpg --verify archive.tar.gz.sig archive.tar.gz

# Vérifier un fichier signé en clair
gpg --verify contrat.txt.asc
```

!!! success "Résultat attendu"
    Si la signature est valide, la sortie de la commande inclura `Good signature from "Votre Nom <votre.email@domaine.com>"`. 
    *(Note : Si vous voyez un avertissement "WARNING: This key is not certified with a trusted signature!", c'est normal tant que vous n'avez pas explicitement validé la confiance envers cette clé avec la commande `gpg --edit-key`).*

## Aide-mémoire

| Commande | Description |
|-------------------|-------------|
| `gpg -c fichier` | Chiffrer symétriquement (mot de passe) |
| `gpg --list-keys` | Lister les clés publiques connues |
| `gpg -e -r <email> fichier` | Chiffrer avec la clé publique du destinataire |
| `gpg -d fichier.gpg` | Déchiffrer un fichier |
| `gpg --detach-sign fichier` | Créer une signature détachée (.sig) |
| `gpg --verify fichier.sig` | Vérifier l'authenticité d'une signature |

## Ressources

- [Documentation officielle GnuPG](https://gnupg.org/documentation/index.html) — Référence complète
- [Recommandations de l'ANSSI sur la cryptographie](https://messervices.cyber.gouv.fr/documents-guides/anssi-guide-mecanismes-crypto-3.00.pdf) — Bonnes pratiques en matière de sécurité et de taille de clé.

*[GPG]: GNU Privacy Guard
*[RSA]: Rivest–Shamir–Adleman (algorithme asymétrique)
*[ANSSI]: Agence Nationale de la Sécurité des Systèmes d'Information
