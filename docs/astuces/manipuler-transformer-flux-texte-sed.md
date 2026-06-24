---
title: Manipuler et transformer des flux de texte avec sed
date: 2026-06-24
author: Nicolas BODAINE
tags:
  - linux
  - bash
  - scripting
  - cli
difficulty: intermédiaire
os: Linux
status: publié
---

# Manipuler et transformer des flux de texte avec sed

!!! abstract "Résumé"
    `sed` (Stream Editor) est un utilitaire incontournable sous Linux. Il permet de filtrer, transformer et manipuler des flux de texte (fichiers ou sorties de commandes) à la volée. Maîtriser `sed` vous fera gagner un temps précieux dans l'écriture de vos scripts et la manipulation de données.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | GNU/Linux (Toutes distributions), macOS |
| Dernière mise à jour | 2026-06-24 |

## Contexte

Quand on administre des systèmes ou qu'on écrit des scripts Bash, il est très fréquent d'avoir besoin de remplacer une valeur de configuration dans un fichier, de supprimer certaines lignes d'un log ou d'extraire une information précise sans ouvrir le fichier manuellement avec `nano` ou `vim`.

C'est là que `sed` brille : il lit le texte ligne par ligne, applique des instructions (remplacement, suppression, insertion) en utilisant souvent des expressions régulières (Regex), puis affiche le résultat (ou le sauvegarde dans le fichier source).

## Prérequis

- Un terminal sous Linux ou macOS.
- Des notions de base sur la ligne de commande (pipes `|`, redirections `>`).
- (Optionnel) Quelques notions d'expressions régulières (Regex).

## Aide-mémoire rapide

| Commande | Description |
|----------|-------------|
| `sed 's/A/B/'` | Remplace la première occurrence de A par B sur chaque ligne. |
| `sed 's/A/B/g'` | Remplace **toutes** les occurrences de A par B (`g` = global). |
| `sed -i 's/A/B/g' fichier.txt` | Applique la modification **directement dans le fichier** (`-i`). |
| `sed '3d' fichier.txt` | Supprime la ligne 3. |
| `sed '/motif/d'` | Supprime toutes les lignes contenant "motif". |
| `sed -n '/motif/p'` | Affiche uniquement les lignes contenant "motif" (équivalent basique de `grep`). |

## Procédure pas-à-pas (Lab)

Pour vous entraîner, nous allons d'abord créer un fichier texte de test.

### Étape 1 : Créer l'environnement de test

Ouvrez votre terminal et générez un fichier de configuration factice :

```bash
cat <<EOF > server.conf
# Fichier de configuration du serveur
PORT=8080
BIND_IP=127.0.0.1
ENABLE_LOGS=false
TIMEOUT=30
DEBUG_MODE=false
EOF
```

### Étape 2 : Le remplacement simple (Substitution)

L'opération la plus courante avec `sed` est la commande `s` (substitution). Sa structure est : `s/motif_recherché/motif_de_remplacement/options`.

Testons un changement du port sans modifier le fichier (la sortie s'affiche juste à l'écran) :

```bash
sed 's/8080/443/' server.conf
```

!!! note "Le séparateur `/`"
    Le caractère `/` est traditionnel, mais s'il est présent dans votre texte (ex: un chemin `/var/log`), vous pouvez utiliser un autre délimiteur, comme `|` ou `#` : `sed 's|/var/log|/opt/log|'`.

### Étape 3 : Remplacement global avec `g`

Changeons tous les "false" par "true". Si plusieurs "false" étaient sur la même ligne, un `sed` classique ne changerait que le premier. L'option `g` (global) corrige ça :

```bash
sed 's/false/true/g' server.conf
```

### Étape 4 : Cibler une ligne spécifique

Si l'on veut modifier uniquement la ligne contenant "TIMEOUT", on peut ajouter une adresse avant la commande de substitution :

```bash
sed '/TIMEOUT/s/30/60/' server.conf
```

### Étape 5 : Supprimer des lignes avec `d`

La commande `d` supprime les lignes qui correspondent au motif. Utile pour nettoyer un fichier de ses commentaires :

```bash
# Supprime les lignes commençant (^) par un #
sed '/^#/d' server.conf
```

### Étape 6 : Appliquer les modifications au fichier (In-place)

Jusqu'à présent, nos commandes ont juste affiché le résultat dans le terminal. Pour **écraser** le fichier d'origine, on utilise l'option `-i` (in-place).

```bash
# Activation des logs et du mode debug
sed -i 's/false/true/g' server.conf
```

!!! danger "Attention à l'option `-i`"
    Faites toujours un test sans `-i` au préalable, ou créez un backup à la volée avec `sed -i.bak 's/A/B/' fichier.txt`. Cela générera un fichier `fichier.txt.bak` avec l'ancien contenu.

## Vérification

Vérifions notre fichier final après modification :

```bash
cat server.conf
```

!!! success "Résultat attendu"
    ```text
    # Fichier de configuration du serveur
    PORT=8080
    BIND_IP=127.0.0.1
    ENABLE_LOGS=true
    TIMEOUT=30
    DEBUG_MODE=true
    ```

## Ressources

- [Manuel GNU sed (en anglais)](https://www.gnu.org/software/sed/manual/sed.html) — La documentation officielle très complète.
- [Page man de sed (`man sed`)](https://man7.org/linux/man-pages/man1/sed.1.html) — Référence locale sur votre système.
