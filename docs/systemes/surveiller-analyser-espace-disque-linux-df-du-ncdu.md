---
title: Surveiller et analyser l'espace disque sous Linux avec df, du et ncdu
date: 2026-06-05
author: Nicolas BODAINE
tags:
  - linux
  - stockage
  - systeme
  - ligne-de-commande
difficulty: débutant
os: Linux
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Surveiller et analyser l'espace disque sous Linux avec df, du et ncdu

!!! abstract "Résumé"
    Sur un serveur Linux, l'espace disque peut rapidement saturer à cause de logs, d'images Docker ou de fichiers de cache volumineux. Ce tutoriel explique comment vérifier l'espace disponible global et comment isoler visuellement les dossiers gourmands en stockage à l'aide des outils `df`, `du` et l'excellent utilitaire interactif `ncdu`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux (Ubuntu, Debian, etc.) |
| Dernière mise à jour | 2026-06-05 |

## Contexte

Un serveur qui n'a plus d'espace disque disponible peut s'arrêter brutalement ou corrompre ses bases de données. En tant qu'administrateur système ou étudiant en informatique, il est indispensable de savoir :

1. Constater qu'un disque est plein ou presque.
2. Identifier quels dossiers ou fichiers occupent toute la place.
3. Supprimer les éléments en toute connaissance de cause.

Nous aborderons ici trois outils fondamentaux pour y parvenir.

## Prérequis

- Une machine ou machine virtuelle sous Linux (Ubuntu, Debian...).
- Un accès à un terminal avec les privilèges `sudo` pour analyser l'intégralité du système.

---

## 1. Surveiller l'espace global avec `df`

La commande `df` (Disk Free) permet d'afficher l'espace disque disponible sur tous les systèmes de fichiers montés.

L'utilisation de l'option `-h` (human-readable) est recommandée pour afficher les tailles en Ko, Mo, Go plutôt qu'en blocs bruts.

```bash
df -h
```

!!! example "Exemple de sortie `df -h`"
    ```text
    Sys. de fichiers Taille Utilisé Dispo Uti% Monté sur
    tmpfs              393M    1,7M  391M   1% /run
    /dev/sda2           20G     15G  3,5G  82% /
    tmpfs              2,0G       0  2,0G   0% /dev/shm
    ```

Dans cet exemple, la partition `/dev/sda2` montée sur `/` (la racine) est occupée à 82%. S'il est proche de 100%, il faut agir.

**Astuce pour filtrer :** Si vous ne voulez voir que les vrais disques (et masquer les systèmes virtuels comme `tmpfs`), utilisez :

```bash
df -h -x tmpfs -x devtmpfs
```

---

## 2. Analyser l'espace d'un dossier avec `du`

Quand vous savez qu'un disque est plein, il faut savoir *pourquoi*. La commande `du` (Disk Usage) calcule l'espace utilisé par les fichiers et dossiers.

L'option `-s` affiche un résumé (summary) et `-h` rend la lecture facile.

### Analyser le dossier courant

```bash
du -sh .
```

### Lister les dossiers les plus lourds dans un répertoire

Pour voir les sous-dossiers occupant le plus de place dans `/var`, vous pouvez combiner `du` avec `sort` :

```bash
sudo du -sh /var/* | sort -rh | head -10
```

- `sudo` : permet d'analyser les dossiers protégés (ex: logs).
- `-s` : taille globale de chaque élément dans `/var/*`.
- `-h` : taille lisible (Go, Mo...).
- `sort -rh` : tri inversé (reverse) et compréhensif des tailles lisibles (human).
- `head -10` : affiche le top 10.

---

## 3. Navigation interactive avec `ncdu`

Bien que `df` et `du` soient installés partout, `ncdu` (NCurses Disk Usage) est souvent l'outil préféré des administrateurs car il offre une interface interactive pour naviguer et supprimer les gros fichiers facilement.

### Installation

`ncdu` n'est généralement pas installé par défaut.

```bash
sudo apt update
sudo apt install ncdu -y
```

### Utilisation

Lancez l'outil sur le dossier racine `/` (ou n'importe quel autre répertoire, comme `/var/log` par exemple) :

```bash
sudo ncdu /
```

Le programme va d'abord scanner le disque (cela peut prendre quelques secondes), puis vous présenter une interface navigable :

- Utilisez les **Flèches Haut/Bas** pour vous déplacer.
- Appuyez sur **Entrée** pour entrer dans un dossier.
- Appuyez sur **Flèche Gauche** pour remonter au dossier parent.
- Appuyez sur **d** pour supprimer le fichier/dossier sélectionné (une confirmation vous sera demandée).
- Appuyez sur **q** pour quitter.

!!! danger "Attention aux suppressions"
    Ne supprimez jamais un fichier que vous ne connaissez pas dans `/bin`, `/lib`, `/usr`, ou `/boot`, cela pourrait casser votre système. Ciblez plutôt les fichiers personnels, le cache (`/var/cache`), les anciens logs (`/var/log`) ou les images conteneurs redondantes.

---

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `df -h` | Affiche l'espace libre global des disques |
| `du -sh /chemin/` | Calcule la taille totale d'un dossier spécifique |
| `ncdu /chemin/` | Lance un analyseur interactif de l'espace disque |

## Ressources

- [Manuel de df (Ubuntu)](https://manpages.ubuntu.com/manpages/noble/fr/man1/df.1.html)
- [Site officiel de ncdu](https://dev.yorhel.nl/ncdu)
