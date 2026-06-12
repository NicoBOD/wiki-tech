---
title: Auditer la sécurité de son serveur Linux avec Lynis
date: 2026-06-12
author: Nicolas BODAINE
tags:
  - securite
  - audit
  - linux
  - lynis
difficulty: intermédiaire
os: Linux (Ubuntu/Debian)
status: publié
---

# Auditer la sécurité de son serveur Linux avec Lynis

!!! abstract "Résumé"
    Lynis est un outil open-source reconnu pour réaliser des audits de sécurité approfondis sur les systèmes UNIX/Linux. Il analyse le système, recherche les failles potentielles, vérifie les configurations logicielles et fournit un rapport détaillé avec un score de "durcissement" (Hardening index) ainsi que des recommandations concrètes pour améliorer la sécurité de la machine.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux (Ubuntu/Debian) |
| Dernière mise à jour | 2026-06-12 |

## Contexte

Lorsque l'on déploie un nouveau serveur ou que l'on reprend l'administration d'une machine existante, il est difficile de savoir si les bonnes pratiques de sécurité ont été respectées. Des services mal configurés, des ports ouverts inutilement ou des mots de passe faibles peuvent compromettre le système. Lynis automatise cette vérification et agit comme un assistant de sécurité qui parcourt des centaines de points de contrôle (CIS benchmarks, standards de l'industrie, etc.) pour vous indiquer exactement quoi corriger.

## Prérequis

- Un serveur sous Linux (Ubuntu, Debian, CentOS, etc.)
- Un accès terminal avec les privilèges `sudo` ou `root`
- Une connexion Internet pour l'installation

## Procédure

### Étape 1 : Installation de Lynis

Bien que Lynis soit présent dans les dépôts par défaut de nombreuses distributions, il est souvent préférable d'utiliser la version la plus récente depuis les dépôts officiels de l'éditeur CISofy, ou simplement de le télécharger directement. Pour des raisons de simplicité pédagogique, nous utiliserons ici le gestionnaire de paquets de la distribution (la version sera fonctionnelle bien que potentiellement pas la toute dernière).

=== "Ubuntu / Debian"

    ```bash
    sudo apt update
    sudo apt install -y lynis
    ```

=== "RHEL / AlmaLinux / Rocky"

    ```bash
    sudo dnf install -y epel-release
    sudo dnf install -y lynis
    ```

Vérifiez que l'installation s'est bien déroulée en affichant la version :
```bash
lynis show version
```

### Étape 2 : Lancement du premier audit

Pour que Lynis puisse effectuer des tests approfondis, notamment sur des fichiers de configuration système sensibles, il est indispensable de le lancer avec des privilèges élevés.

```bash
sudo lynis audit system
```

L'outil va analyser le système section par section (Boot and services, Kernel, Memory and Processes, Users, Groups and Authentication, File systems, etc.).
Pendant l'analyse, l'écran va défiler. Attendez simplement que l'audit soit terminé.

### Étape 3 : Analyse des résultats

À la fin de l'audit, Lynis affiche un résumé complet avec plusieurs sections très importantes :

1. **Warnings (Avertissements) :** Ce sont les points critiques qu'il faut corriger rapidement (ex: un paquet vulnérable, un mot de passe root manquant).
2. **Suggestions (Recommandations) :** Ce sont des bonnes pratiques pour "durcir" (harden) votre système (ex: configurer des règles de pare-feu plus strictes, restreindre les permissions d'un répertoire).
3. **Hardening Index :** C'est un score sur 100 indiquant le niveau de sécurité global de votre système. Il est rare d'avoir 100/100, l'objectif est d'améliorer ce score progressivement.

Les logs et rapports de l'audit sont sauvegardés dans :
- Fichier de log détaillé : `/var/log/lynis.log`
- Fichier de rapport (pour parsing) : `/var/log/lynis-report.dat`

### Étape 4 : Comprendre et corriger une alerte

Lynis associe un identifiant (Test ID) à chaque suggestion ou avertissement, par exemple `SSH-7408` ou `FILE-6310`.

Pour obtenir plus d'informations sur un problème spécifique et savoir comment le résoudre, utilisez la commande suivante en remplaçant `TEST-ID` par l'identifiant concerné :

```bash
lynis show details TEST-ID
```

Par exemple, si Lynis suggère de modifier un paramètre SSH (Test ID: `SSH-7408`) :
```bash
lynis show details SSH-7408
```

La sortie affichera la description détaillée du problème, la solution recommandée et parfois un lien direct vers la documentation CISofy correspondante. Il ne vous reste plus qu'à appliquer la correction recommandée (par exemple, éditer `/etc/ssh/sshd_config` et redémarrer le service SSH), puis à relancer l'audit pour vérifier que le problème a disparu.

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `sudo lynis audit system` | Lance un audit de sécurité complet du système local |
| `lynis show version` | Affiche la version de Lynis installée |
| `lynis show details ID` | Affiche les informations détaillées et la solution pour une alerte (Test ID) |
| `lynis show commands` | Liste toutes les commandes Lynis disponibles |

## Ressources

- [Site officiel de Lynis (CISofy)](https://cisofy.com/lynis/) — Présentation et documentation de l'outil
- [Guide de l'ANSSI (Recommandations de sécurité Linux)](https://cyber.gouv.fr/publications/recommandations-de-securite-relatives-un-systeme-gnulinux) — Pour comprendre en profondeur les bonnes pratiques recommandées par Lynis
