---
title: Sauvegardes automatisées avec script Bash robuste
date: 2026-06-13
author: Nicolas BODAINE
tags:
  - bash
  - sauvegarde
  - script
  - linux
difficulty: intermédiaire
os: Linux
status: publié
---

# Sauvegardes automatisées : créer un script Bash robuste avec gestion des erreurs

!!! abstract "Résumé"
    L'automatisation des sauvegardes est essentielle en administration système. Un script Bash pour sauvegarder des données ne se limite pas à copier des fichiers : il doit gérer les erreurs, logger ses actions et s'assurer que l'espace disque est suffisant. Dans ce tutoriel, nous allons créer un script complet et fiable.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux |
| Dernière mise à jour | 2026-06-13 |

## Contexte

La plupart des scripts de sauvegarde débutants se résument à une simple commande `tar` ou `rsync` planifiée dans le cron. Mais que se passe-t-il si le dossier source n'existe pas ? Si le disque de destination est plein ? Si la commande échoue en plein milieu ? Un script **robuste** doit anticiper ces problèmes, s'arrêter en cas d'erreur critique, et enregistrer ce qui s'est passé dans un fichier de journalisation (log).

## Prérequis

- Une machine Linux avec accès à un terminal.
- Des connaissances de base sur la ligne de commande (navigation, création de fichiers).
- L'utilitaire `tar` installé (présent par défaut sur la quasi-totalité des distributions).

## Procédure

### Étape 1 : Structure de base et bonnes pratiques

Pour qu'un script Bash soit robuste, il faut utiliser des options spécifiques au début du fichier.

Créez un fichier `backup.sh` :

```bash
nano backup.sh
```

Ajoutez l'en-tête suivant :

```bash title="backup.sh" linenums="1"
#!/bin/bash

# Options de robustesse
set -e # Arrête le script si une commande échoue
set -u # Arrête le script si une variable non définie est utilisée
set -o pipefail # Considère un pipeline en erreur si une des commandes échoue

# Variables de configuration
SOURCE_DIR="/var/www/html" # Dossier à sauvegarder
BACKUP_DIR="/mnt/sauvegardes" # Dossier de destination
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.tar.gz"
LOG_FILE="/var/log/backup_script.log"
```

### Étape 2 : Fonction de journalisation (Logging)

Au lieu d'utiliser de simples `echo`, nous allons créer une fonction pour horodater chaque message et l'écrire à la fois dans la console et dans le fichier de log.

Ajoutez ceci à votre script :

```bash title="backup.sh" linenums="15"
# Fonction pour logger les messages
log_message() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] ${message}" | tee -a "${LOG_FILE}"
}
```

### Étape 3 : Vérifications préalables

Avant de commencer la sauvegarde, le script doit s'assurer que l'environnement est prêt.

```bash title="backup.sh" linenums="22"
log_message "=== Début de la sauvegarde ==="

# 1. Vérifier si le dossier source existe
if [ ! -d "${SOURCE_DIR}" ]; then
    log_message "ERREUR : Le dossier source ${SOURCE_DIR} n'existe pas."
    exit 1
fi

# 2. Vérifier (et créer) le dossier de destination
if [ ! -d "${BACKUP_DIR}" ]; then
    log_message "INFO : Création du dossier de destination ${BACKUP_DIR}..."
    mkdir -p "${BACKUP_DIR}"
fi

# 3. Vérifier l'espace disque (ex: s'assurer qu'il reste au moins 1 Go)
ESPACE_LIBRE=$(df -m "${BACKUP_DIR}" | awk 'NR==2 {print $4}')
if [ "${ESPACE_LIBRE}" -lt 1024 ]; then
    log_message "ERREUR : Espace disque insuffisant sur ${BACKUP_DIR} (Moins de 1 Go disponible)."
    exit 1
fi
```

### Étape 4 : Exécution de la sauvegarde avec gestion d'erreurs

Nous allons utiliser `tar` pour compresser les données. Grâce à `set -e`, si `tar` échoue, le script s'arrêtera, mais nous pouvons capturer la réussite ou l'échec pour logger correctement l'événement en désactivant temporairement cette option ou en utilisant une structure conditionnelle classique.

```bash title="backup.sh" linenums="42"
log_message "INFO : Démarrage de l'archive vers ${BACKUP_FILE}..."

# Désactiver l'arrêt immédiat pour gérer l'erreur de tar nous-mêmes
set +e

tar -czf "${BACKUP_FILE}" -C "${SOURCE_DIR}" . 2>> "${LOG_FILE}"
TAR_STATUS=$?

# Réactiver l'arrêt immédiat
set -e

if [ $TAR_STATUS -eq 0 ]; then
    log_message "SUCCÈS : Sauvegarde terminée avec succès."
    
    # Afficher la taille de la sauvegarde
    TAILLE=$(du -h "${BACKUP_FILE}" | awk '{print $1}')
    log_message "INFO : Taille de la sauvegarde : ${TAILLE}"
else
    log_message "ERREUR : La commande tar a échoué avec le code ${TAR_STATUS}."
    # Supprimer le fichier partiellement créé
    [ -f "${BACKUP_FILE}" ] && rm "${BACKUP_FILE}"
    exit 1
fi

log_message "=== Fin de la sauvegarde ==="
```

### Étape 5 : Test du script

1. Rendez le script exécutable :
   ```bash
   chmod +x backup.sh
   ```

2. Créez des dossiers de test pour éviter d'utiliser `/var/www/html` en root, ou exécutez-le avec `sudo` :
   ```bash
   sudo ./backup.sh
   ```

## Vérification

Pour vérifier que tout s'est bien passé, consultez le fichier de log :

```bash
cat /var/log/backup_script.log
```

!!! success "Résultat attendu"
    Vous devriez voir une sortie similaire :
    ```text
    [2026-06-13 12:00:01] === Début de la sauvegarde ===
    [2026-06-13 12:00:01] INFO : Démarrage de l'archive vers /mnt/sauvegardes/backup_2026-06-13_12-00-01.tar.gz...
    [2026-06-13 12:00:03] SUCCÈS : Sauvegarde terminée avec succès.
    [2026-06-13 12:00:03] INFO : Taille de la sauvegarde : 45M
    [2026-06-13 12:00:03] === Fin de la sauvegarde ===
    ```

## Ressources

- [Manuel GNU Bash (set builtin)](https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html) — Documentation officielle des options `set`
- [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/) — Guide très complet pour la création de scripts Bash complexes.
