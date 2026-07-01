---
title: Planifier des tâches récurrentes simplement sous Linux avec cron (crontab)
date: 2026-07-01
author: Nicolas BODAINE
tags:
  - linux
  - cron
  - crontab
  - automatisation
  - scripting
difficulty: débutant
os: Linux
status: publié
---

# Planifier des tâches récurrentes simplement sous Linux avec cron (crontab)

!!! abstract "Résumé"
    Sous Linux, l'outil incontournable pour exécuter des scripts ou des commandes à intervalles réguliers (toutes les heures, tous les jours, etc.) est **cron**. Ce tutoriel vous explique comment utiliser son interface `crontab` pour automatiser vos tâches courantes comme les sauvegardes, le nettoyage de fichiers ou les mises à jour.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu / Debian / CentOS / etc. (Toute distribution Linux) |
| Dernière mise à jour | 2026-07-01 |

## Contexte

La gestion d'un serveur ou d'une machine sous Linux nécessite souvent d'exécuter des actions répétitives :
- Effectuer une sauvegarde de base de données toutes les nuits à 2h00.
- Vider un dossier temporaire chaque week-end.
- Exécuter un script de surveillance toutes les 5 minutes.

Le démon `cron` (fonctionnant en arrière-plan) et la commande `crontab` (qui permet d'éditer la table de planification) sont préinstallés sur la quasi-totalité des systèmes Linux et constituent la solution standard pour ces besoins. Bien que les [*timers systemd*](planifier-script-timer-systemd-linux.md) soient aujourd'hui recommandés pour des tâches complexes, `cron` reste imbattable pour sa simplicité.

## Prérequis

- Un accès à un terminal sous Linux.
- Les droits d'exécution sur les scripts que vous souhaitez planifier.

## Comprendre la syntaxe de crontab

Chaque ligne d'une crontab est composée de 6 champs séparés par des espaces. Les 5 premiers définissent **quand** la tâche doit s'exécuter, le dernier définit **quelle commande** exécuter.

```text
* * * * * commande à exécuter
- - - - -
| | | | |
| | | | +----- Jour de la semaine (0 - 7) (Dimanche = 0 ou 7)
| | | +------- Mois (1 - 12)
| | +--------- Jour du mois (1 - 31)
| +----------- Heure (0 - 23)
+------------- Minute (0 - 59)
```

**Caractères spéciaux :**
- `*` (astérisque) : "chaque" (ex: chaque minute, chaque heure).
- `,` (virgule) : liste de valeurs (ex: `15,45` pour les minutes 15 et 45).
- `-` (tiret) : plage de valeurs (ex: `1-5` du lundi au vendredi).
- `/` (slash) : intervalle (ex: `*/10` toutes les 10 minutes).

## Procédure

### Étape 1 : Éditer sa crontab

Pour afficher, modifier ou créer les tâches planifiées de votre utilisateur courant, tapez :

```bash
crontab -e
```

Lors de la toute première exécution, le système peut vous demander de choisir un éditeur de texte (nano, vim, etc.). Tapez le numéro correspondant à `nano` (généralement `1`) pour plus de simplicité.

!!! warning "L'environnement cron"
    Les tâches planifiées par `cron` s'exécutent dans un environnement très limité (les variables comme `$PATH` sont minimalistes). **Utilisez toujours les chemins absolus** (ex: `/usr/bin/python3` ou `/home/utilisateur/script.sh`) dans votre crontab pour éviter que le système ne trouve pas vos commandes.

### Étape 2 : Ajouter des tâches planifiées

Dans l'éditeur, descendez tout en bas du fichier et ajoutez vos tâches. Voici quelques exemples concrets :

**1. Exécuter un script de sauvegarde tous les jours à 2h30 du matin :**
```text
30 2 * * * /home/nicolas/scripts/backup.sh
```

**2. Vider le cache toutes les heures (à la minute 0) :**
```text
0 * * * * /usr/bin/rm -rf /var/tmp/mon-cache/*
```

**3. Lancer un script toutes les 15 minutes, du lundi au vendredi :**
```text
*/15 * * * 1-5 /home/nicolas/scripts/check-status.sh
```

**4. Redémarrer un service tous les dimanches soirs à 23h59 :**
*(Attention, nécessite `sudo crontab -e` pour avoir les droits root)*
```text
59 23 * * 0 systemctl restart mon-service
```

Sauvegardez (avec `nano` : ++ctrl+o++ puis ++enter++, puis quittez avec ++ctrl+x++). Le système vous confirmera avec un message comme `crontab: installing new crontab`.

### Étape 3 : Gérer la sortie des commandes (Logs)

Par défaut, si une commande produit du texte (sortie standard ou erreur), `cron` essaie de l'envoyer par email à l'utilisateur, ce qui nécessite un serveur de mail local (souvent non configuré). Pour éviter que les messages soient perdus, redirigez la sortie vers un fichier :

```text
30 2 * * * /home/nicolas/scripts/backup.sh >> /var/log/backup.log 2>&1
```

*(L'instruction `>>` ajoute la sortie au fichier, et `2>&1` redirige les erreurs (canal 2) vers la même destination que la sortie standard (canal 1).)*

Si vous souhaitez totalement ignorer les retours d'une commande (déconseillé pour le debug), redirigez-les vers le néant :
```text
*/5 * * * * /home/nicolas/scripts/silencieux.sh > /dev/null 2>&1
```

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `crontab -e` | Éditer la crontab de l'utilisateur courant. |
| `crontab -l` | Lister le contenu de la crontab sans la modifier. |
| `crontab -r` | Supprimer complètement la crontab (attention !). |
| `sudo crontab -e` | Éditer la crontab de l'utilisateur root. |

**Raccourcis utiles :**
Certaines versions de cron supportent des chaînes pré-définies (à la place des 5 étoiles) :
- `@reboot` : S'exécute une seule fois au démarrage de la machine.
- `@hourly` : Toutes les heures (`0 * * * *`).
- `@daily` : Tous les jours à minuit (`0 0 * * *`).
- `@weekly` : Toutes les semaines (dimanche minuit).
- `@monthly` : Tous les mois (le 1er à minuit).

## Vérification

Pour vérifier que votre crontab a bien été prise en compte, utilisez la commande suivante :

```bash
crontab -l
```

!!! success "Résultat attendu"
    Vos lignes de configuration s'affichent à l'écran.
    Pour vérifier si les tâches se lancent bien à l'heure prévue, vous pouvez consulter les logs de votre système (souvent sous `/var/log/syslog` sur Debian/Ubuntu ou via la commande `journalctl -u cron`).

## Ressources

- [Crontab Guru](https://crontab.guru/) — Un excellent site web interactif pour vérifier, créer et comprendre vos expressions cron.
- `man cron` et `man crontab` dans votre terminal.
