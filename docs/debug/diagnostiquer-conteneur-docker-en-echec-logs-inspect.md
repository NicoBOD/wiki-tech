---
title: Diagnostiquer un conteneur Docker en échec avec logs et inspect
date: 2026-06-29
author: Nicolas BODAINE
tags:
  - docker
  - debug
  - conteneur
  - linux
difficulty: intermédiaire
os: Linux
status: publié
---

# Diagnostiquer un conteneur Docker en échec avec logs et inspect

!!! abstract "Résumé"
    Apprenez à diagnostiquer un conteneur Docker qui refuse de démarrer, s'arrête de manière inattendue (crash loop) ou fonctionne anormalement, en utilisant les commandes natives `docker logs` et `docker inspect`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux |
| Dernière mise à jour | 2026-06-29 |

## Contexte

Il arrive fréquemment qu'un conteneur Docker s'arrête immédiatement après son lancement ou redémarre en boucle sans raison apparente (état `Restarting` ou `Exited (1)`). Le diagnostic de ces défaillances nécessite d'examiner en détail les sorties standard de l'application embarquée et la configuration interne du conteneur générée par le démon Docker.

L'objectif de ce tutoriel est de maîtriser les deux outils essentiels du débogage Docker : `docker logs` pour comprendre ce que l'application a fait, et `docker inspect` pour comprendre comment le conteneur a été configuré et pourquoi il s'est arrêté.

## Prérequis

- Un système Linux avec Docker installé.
- Des droits suffisants pour utiliser la commande `docker` (souvent via le groupe `docker` ou `sudo`).
- Un ou plusieurs conteneurs en cours d'exécution ou récemment arrêtés.

## Procédure

### Étape 1 : Identifier le conteneur défaillant

La première étape consiste à lister tous les conteneurs, y compris ceux qui sont arrêtés, afin de repérer celui qui pose problème.

```bash
# Lister tous les conteneurs (actifs et inactifs)
docker ps -a
```

Repérez le nom ou l'ID (ex: `a1b2c3d4e5f6`) de votre conteneur. Notez son statut, par exemple `Exited (137)` ou `Exited (1)`, qui donne un premier indice :

- `Exited (0)` : Arrêt normal (l'application a terminé sa tâche proprement).
- `Exited (1)` : Erreur applicative (souvent une configuration manquante ou un crash du code).
- `Exited (137)` : Conteneur tué par le système (OOM - Out of Memory, ou arrêt forcé).

### Étape 2 : Analyser les journaux avec `docker logs`

Les logs correspondent aux sorties standard (`stdout` et `stderr`) du processus principal (PID 1) du conteneur. C'est ici que l'on trouve les erreurs d'exécution (base de données inaccessible, erreur de syntaxe, etc.).

```bash
# Afficher tous les logs du conteneur
docker logs <nom_ou_id_du_conteneur>
```

Pour faciliter la lecture, surtout si le conteneur a généré beaucoup de logs, vous pouvez filtrer la sortie :

```bash
# N'afficher que les 50 dernières lignes
docker logs --tail 50 <nom_ou_id_du_conteneur>

# Suivre les logs en temps réel (utile si le conteneur tourne encore ou redémarre en boucle)
docker logs -f <nom_ou_id_du_conteneur>

# Ajouter les horodatages pour voir exactement quand le crash a eu lieu
docker logs -t <nom_ou_id_du_conteneur>
```

!!! tip "Conseil"
    Si la commande ne retourne rien, cela signifie souvent que l'application écrit ses logs dans un fichier spécifique à l'intérieur du conteneur (ex: `/var/log/nginx/error.log`) au lieu de la sortie standard.

### Étape 3 : Examiner l'état interne avec `docker inspect`

Si les logs ne suffisent pas, `docker inspect` permet de voir toute la configuration JSON du conteneur. Cela inclut l'état exact de l'arrêt, les variables d'environnement, les volumes montés et la configuration réseau.

```bash
# Inspecter le conteneur complet
docker inspect <nom_ou_id_du_conteneur>
```

Le retour étant très verbeux, utilisez l'outil `jq` ou le formatage Go-template natif de Docker pour cibler des informations précises.

**Vérifier le code de sortie exact et la raison de l'arrêt (OOMKilled) :**
```bash
docker inspect -f '{{.State.Status}} (ExitCode: {{.State.ExitCode}})' <nom_ou_id_du_conteneur>
docker inspect -f 'OOMKilled: {{.State.OOMKilled}}' <nom_ou_id_du_conteneur>
```
Si `OOMKilled` est `true`, le conteneur a consommé plus de mémoire vive que ce qui lui était alloué et a été arrêté par le noyau Linux.

**Vérifier les variables d'environnement :**
```bash
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' <nom_ou_id_du_conteneur>
```
Une variable mal orthographiée ou manquante est l'une des causes les plus fréquentes d'échec au démarrage.

**Vérifier les chemins des volumes montés (Bind Mounts) :**
```bash
docker inspect -f '{{range .Mounts}}Source: {{.Source}} -> Dest: {{.Destination}}{{println}}{{end}}' <nom_ou_id_du_conteneur>
```
Assurez-vous que les dossiers hôtes ciblés existent et que le conteneur dispose des permissions nécessaires pour y lire/écrire.

### Étape 4 : Ouvrir un shell temporaire pour l'investigation

Parfois, un conteneur plante immédiatement, rendant impossible l'utilisation de `docker exec`. Pour l'analyser, vous pouvez forcer le lancement d'une nouvelle instance en écrasant sa commande par défaut (`entrypoint`) par un shell interactif :

```bash
# Démarrer une nouvelle instance interactive avec bash (ou sh)
docker run --rm -it --entrypoint /bin/sh <nom_de_l_image>
```

Une fois à l'intérieur, vous pouvez vérifier manuellement si le fichier de configuration est présent, si les droits sont corrects, ou tenter de lancer l'application manuellement pour observer son comportement.

## Aide-mémoire

| Commande | Action |
|----------|--------|
| `docker ps -a` | Lister tous les conteneurs (actifs et arrêtés) |
| `docker logs -f <id>` | Suivre les logs d'un conteneur en direct |
| `docker inspect <id>` | Afficher la configuration complète au format JSON |
| `docker inspect -f '{{.State.ExitCode}}' <id>` | Extraire spécifiquement le code de retour |
| `docker run -it --entrypoint sh <image>` | Lancer une image en remplaçant la commande par un shell |

## Ressources

- [Documentation officielle Docker - Troubleshooting](https://docs.docker.com/config/containers/logging/) — Informations sur les drivers de logging.
- [Documentation officielle - docker logs](https://docs.docker.com/reference/cli/docker/container/logs/)
- [Documentation officielle - docker inspect](https://docs.docker.com/reference/cli/docker/inspect/)
