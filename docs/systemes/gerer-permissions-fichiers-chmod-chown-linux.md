---
title: "Comprendre et gérer les permissions sous Linux (chmod, chown)"
date: 2026-06-05
author: Nicolas BODAINE
tags:
  - linux
  - permissions
  - systeme
  - bash
difficulty: débutant
os: Linux (Toutes distributions)
status: publié
---

# Comprendre et gérer les permissions sous Linux (chmod, chown)

!!! abstract "Résumé"
    Ce tutoriel explique comment lire, comprendre et modifier les permissions des fichiers et répertoires sous Linux. Nous aborderons les concepts de propriétaire, groupe et les commandes fondamentales `chmod` et `chown`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Toutes distributions Linux |
| Dernière mise à jour | 2026-06-05 |

## Contexte

Sous Linux, la sécurité et la gestion des accès reposent sur un système de droits attribués aux fichiers et aux répertoires. Chaque fichier appartient à un **propriétaire** et à un **groupe**. Pour chaque fichier, trois types de permissions sont définis :
- **Lecture (r - read)**
- **Écriture (w - write)**
- **Exécution (x - execute)**

Ces permissions sont attribuées à trois catégories d'utilisateurs :
- Le propriétaire (User - u)
- Le groupe propriétaire (Group - g)
- Les autres utilisateurs (Others - o)

Comprendre ces mécanismes est indispensable pour tout administrateur système, afin de protéger les données sensibles et garantir le bon fonctionnement des services.

## Prérequis

- Un accès à un terminal Linux (machine virtuelle ou poste physique).
- Un utilisateur standard, et un accès à `sudo` pour changer les propriétaires si nécessaire.

## Procédure

### Étape 1 : Lire les permissions avec `ls -l`

Pour visualiser les permissions, utilisez la commande `ls -l`.

```bash
ls -l mon_fichier.txt
```

!!! note "Analyse du résultat"
    Le résultat ressemble souvent à ceci :  
    `-rw-r--r-- 1 alice admin 1024 jun 5 10:00 mon_fichier.txt`

Décortiquons le bloc de permissions `-rw-r--r--` :

1. Le premier caractère indique le type (`-` pour fichier, `d` pour répertoire, `l` pour lien symbolique).
2. Les trois suivants (`rw-`) sont les droits du **propriétaire** (User) : Lecture et Écriture.
3. Les trois suivants (`r--`) sont les droits du **groupe** (Group) : Lecture seule.
4. Les trois derniers (`r--`) sont les droits des **autres** (Others) : Lecture seule.

Dans cet exemple, `alice` est le propriétaire et `admin` est le groupe.

### Étape 2 : Modifier les permissions avec `chmod` (Mode Symbolique)

La commande `chmod` (change mode) permet de modifier les permissions. Le mode symbolique utilise des lettres pour ajouter (`+`), retirer (`-`) ou définir exactement (`=`) des droits.

Ajouter le droit d'exécution au propriétaire :
```bash
chmod u+x script.sh
```

Retirer le droit d'écriture aux autres :
```bash
chmod o-w fichier.conf
```

Ajouter le droit de lecture à tout le monde (User, Group, Others) :
```bash
chmod a+r document.pdf
```

### Étape 3 : Modifier les permissions avec `chmod` (Mode Octal)

Le mode octal utilise des nombres pour définir les droits. C'est souvent plus rapide.
Chaque droit a une valeur :
- **4** = Lecture (r)
- **2** = Écriture (w)
- **1** = Exécution (x)
- **0** = Aucun droit (-)

On additionne ces valeurs pour chaque catégorie (Propriétaire, Groupe, Autres).

- `rwx` = 4 + 2 + 1 = 7
- `rw-` = 4 + 2 + 0 = 6
- `r--` = 4 + 0 + 0 = 4

Donner tous les droits au propriétaire, et la lecture seule au groupe et aux autres (`rwxr--r--`) :
```bash
chmod 744 script.sh
```

Donner tous les droits à tout le monde (`rwxrwxrwx` - Attention, très dangereux en sécurité !) :
```bash
chmod 777 fichier_partage.txt
```

### Étape 4 : Changer le propriétaire et le groupe avec `chown`

La commande `chown` (change owner) permet de changer à qui appartient un fichier. **L'utilisation de `sudo` est souvent requise** pour attribuer un fichier à un autre utilisateur.

Changer le propriétaire d'un fichier :
```bash
sudo chown bob document.txt
```

Changer le propriétaire et le groupe en même temps (séparés par `:` ou `.`) :
```bash
sudo chown bob:devops projet/
```

Appliquer le changement de manière récursive à un dossier et tout son contenu (`-R`) :
```bash
sudo chown -R alice:admin /var/www/mondossier/
```

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `ls -l` | Affiche les permissions détaillées. |
| `chmod u+x fichier` | Ajoute l'exécution au propriétaire. |
| `chmod 644 fichier` | Propriétaire : lire/écrire. Groupe/Autres : lire. (Standard pour les fichiers). |
| `chmod 755 dossier` | Propriétaire : tous droits. Groupe/Autres : lire/exécuter. (Standard pour les dossiers). |
| `chown user:group fichier` | Change le propriétaire et le groupe d'un fichier. |

## Vérification

Pour vérifier que vos modifications ont bien été appliquées :

```bash
ls -l
```

!!! success "Résultat attendu"
    Observez le bloc de permissions au début de la ligne, ainsi que les colonnes du propriétaire et du groupe pour confirmer que les droits sont ceux souhaités.

## Ressources

- [Ubuntu - Gestion des droits d'accès](https://doc.ubuntu-fr.org/droits) — Documentation de la communauté Ubuntu francophone.
- Pages de manuel Linux (`man chmod`, `man chown`).