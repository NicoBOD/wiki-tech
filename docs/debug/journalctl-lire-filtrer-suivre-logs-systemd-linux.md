---
title: "Lire, filtrer et suivre les logs avec journalctl"
date: 2026-06-02
author: Nicolas BODAINE
tags:
  - linux
  - systemd
  - logs
  - debug
difficulty: débutant
os: Ubuntu 24.04 / Debian 12
status: publié
---

# Lire, filtrer et suivre les logs avec journalctl pour diagnostiquer un service Linux

!!! abstract "Résumé"
    Sur les distributions Linux modernes utilisant `systemd`, les journaux système et applicatifs sont centralisés par `journald`. Cet outil enregistre les logs sous forme binaire. Pour les consulter efficacement, on utilise la commande `journalctl`. Ce tutoriel vous montrera comment lire, filtrer et suivre ces journaux pour diagnostiquer rapidement vos services.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux (Ubuntu, Debian, RHEL, etc.) |
| Dernière mise à jour | 2026-06-02 |

## Contexte

Lorsque vous installez ou administrez un serveur Linux, il arrive fréquemment qu'un service refuse de démarrer (par exemple Nginx, Apache, SSH, ou un script maison). Le réflexe classique de chercher dans `/var/log/syslog` ou `/var/log/messages` a laissé place à un outil plus puissant et unifié : `journalctl`. 

Savoir manipuler `journalctl` est une compétence fondamentale pour tout administrateur système ou développeur qui dépanne des environnements Linux.

## Prérequis

- Une machine sous Linux utilisant `systemd` (Ubuntu, Debian, CentOS, Rocky Linux, etc.).
- Les droits d'administration (via `sudo` ou `root`) pour consulter l'intégralité des logs du système. Les simples utilisateurs ne peuvent voir que leurs propres logs.

## Procédure

### Étape 1 : Lecture de base

Pour afficher tous les journaux du système depuis le début :

```bash
sudo journalctl
```

*Note : La sortie est paginée par défaut (comme avec la commande `less`). Utilisez les flèches pour naviguer et `q` pour quitter.*

Si vous voulez inverser l'ordre et afficher les logs les plus récents en premier :

```bash
sudo journalctl -r
```

### Étape 2 : Filtrer par unité systemd (service)

C'est l'utilisation la plus courante en débogage. Si le service `nginx` plante, vous ne voulez voir que ses logs :

```bash
sudo journalctl -u nginx.service
```

Vous pouvez omettre le `.service` si le nom est explicite :

```bash
sudo journalctl -u ssh
```

### Étape 3 : Suivre les logs en temps réel (tail)

Pour voir les nouveaux logs apparaître en direct (très utile lors du lancement d'un service ou pour surveiller du trafic) :

```bash
sudo journalctl -f
```

Vous pouvez combiner cette option avec le filtre de service :

```bash
sudo journalctl -u apache2 -f
```

### Étape 4 : Filtrer par date et heure

Si vous savez qu'un incident s'est produit à une heure précise, vous pouvez restreindre l'affichage pour éviter d'être noyé dans les informations :

```bash
# Les logs depuis ce matin
sudo journalctl --since "today"

# Les logs d'hier
sudo journalctl --since "yesterday"

# Entre deux dates ou heures précises
sudo journalctl --since "2026-06-02 08:00:00" --until "2026-06-02 09:30:00"

# Les logs depuis 1 heure
sudo journalctl --since "1 hour ago"
```

### Étape 5 : Filtrer par niveau de priorité

`journald` classe les messages selon la même échelle de priorité que Syslog (de 0 à 7). Pour ne voir que les erreurs (`err` = 3) ou pire (critique, alerte, urgence) :

```bash
sudo journalctl -p 3 -xb
```

> **Astuce :** L'option `-xb` demande d'ajouter des explications textuelles détaillées si disponibles (`-x`) et de limiter l'affichage au démarrage actuel de la machine (`-b`).

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `journalctl -u nom_service` | Afficher les logs d'un service spécifique |
| `journalctl -f` | Suivre les logs en direct (équivalent à `tail -f`) |
| `journalctl -n 50` | Afficher les 50 dernières lignes |
| `journalctl -b` | Afficher les logs depuis le dernier redémarrage (boot) |
| `journalctl --since "1 hour ago"` | Afficher les logs de la dernière heure |
| `journalctl -p err` | Afficher uniquement les messages d'erreur ou plus graves |
| `journalctl --disk-usage` | Vérifier l'espace disque occupé par les journaux |
| `journalctl --vacuum-time=7d` | Nettoyer les logs plus vieux que 7 jours |

## Ressources

- [Documentation officielle systemd.journal-fields](https://www.freedesktop.org/software/systemd/man/systemd.journal-fields.html) — Structure des journaux systemd.
- Manpages de votre système : `man journalctl`.
