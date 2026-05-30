---
title: Planifier un script avec un timer systemd sous Linux
date: 2026-05-30
author: Nicolas BODAINE
tags:
  - linux
  - systemd
  - timer
  - automatisation
  - script
  - planification
difficulty: débutant
os: Ubuntu 24.04 / Debian 13
status: publié
---

# Planifier un script avec un timer systemd sous Linux

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour créer un **script Bash** simple, l'exécuter avec une **unité de service systemd**, puis le lancer automatiquement avec un **timer systemd** sur **Ubuntu 24.04** ou **Debian 13**.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 / Debian 13 |
| Dernière mise à jour | 2026-05-30 |

## Contexte

Dans un lab, on a souvent besoin d'exécuter une tâche automatiquement :

- écrire un horodatage dans un fichier ;
- lancer un script de sauvegarde ;
- nettoyer un dossier temporaire ;
- déclencher un contrôle régulier.

Sur les systèmes Linux modernes basés sur **systemd**, on peut planifier ce type de tâche avec un **timer**.
Un timer systemd ne lance pas directement une commande : il **active une unité de service**.

Dans ce TP, nous allons volontairement utiliser un exemple très simple et sans risque :

- créer un script qui écrit la date et l'heure dans un fichier de log ;
- créer un service `systemd` de type `oneshot` ;
- créer un timer qui lance ce service automatiquement ;
- vérifier le résultat avec `systemctl` et `journalctl`.

## Prérequis

- Une VM ou un poste de test sous **Ubuntu 24.04** ou **Debian 13**
- Un compte avec les droits `sudo`
- Un système utilisant **systemd**
- Un éditeur de texte comme `nano`

!!! note "Pourquoi cet exemple est intéressant"
    Une fois ce premier TP compris, vous pourrez réutiliser exactement la même logique pour un script de sauvegarde, de rotation de logs, de supervision légère ou de maintenance.

## Procédure

### Étape 1 : créer le script à exécuter

Nous allons créer un petit script qui ajoute une ligne dans `/var/log/horodatage-lab.log`.

Créez le fichier suivant :

```bash
sudo nano /usr/local/bin/horodatage-lab.sh
```

Collez le contenu ci-dessous :

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "$(/usr/bin/date '+%Y-%m-%d %H:%M:%S') - exécution du timer systemd" >> /var/log/horodatage-lab.log
```

Rendez ensuite le script exécutable :

```bash
sudo chmod 755 /usr/local/bin/horodatage-lab.sh
```

### Étape 2 : tester le script manuellement

Avant de planifier quoi que ce soit, vérifiez que le script fonctionne tout seul.

```bash
sudo /usr/local/bin/horodatage-lab.sh
sudo tail -n 5 /var/log/horodatage-lab.log
```

Exemple de résultat attendu :

```text
2026-05-30 18:10:00 - exécution du timer systemd
```

!!! success "Résultat attendu"
    Une nouvelle ligne horodatée doit apparaître dans `/var/log/horodatage-lab.log`.

### Étape 3 : créer l'unité de service systemd

Un **timer** active en général un **service**.
Nous allons donc créer d'abord le service `horodatage-lab.service`.

Créez le fichier suivant :

```bash
sudo nano /etc/systemd/system/horodatage-lab.service
```

Collez ce contenu :

```ini
[Unit]
Description=Script de test pour timer systemd

[Service]
Type=oneshot
ExecStart=/usr/local/bin/horodatage-lab.sh
```

### Explication rapide

- `Description` : description lisible du service ;
- `Type=oneshot` : adapté à une tâche courte qui s'exécute puis se termine ;
- `ExecStart` : commande réellement lancée par le service.

!!! tip "Pourquoi `oneshot` ?"
    Ce type convient très bien aux scripts de maintenance ou d'automatisation qui font une action puis quittent immédiatement.

### Étape 4 : recharger systemd et tester le service

Quand vous ajoutez une nouvelle unité, il faut demander à `systemd` de relire sa configuration.

```bash
sudo systemctl daemon-reload
sudo systemctl start horodatage-lab.service
sudo systemctl status horodatage-lab.service --no-pager
```

Pour vérifier le résultat côté fichier de log :

```bash
sudo tail -n 5 /var/log/horodatage-lab.log
```

Pour vérifier le journal du service :

```bash
sudo journalctl -u horodatage-lab.service -n 20 --no-pager
```

!!! success "Résultat attendu"
    Le service doit s'exécuter sans erreur et ajouter une nouvelle ligne dans le fichier de log.

### Étape 5 : créer le timer systemd

Nous allons maintenant créer le timer associé.

Objectif du TP :

- lancer une première exécution peu après le démarrage de la machine ;
- relancer ensuite le service toutes les 5 minutes.

Créez le fichier suivant :

```bash
sudo nano /etc/systemd/system/horodatage-lab.timer
```

Collez le contenu ci-dessous :

```ini
[Unit]
Description=Exécuter horodatage-lab.service toutes les 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=horodatage-lab.service

[Install]
WantedBy=timers.target
```

### Comprendre les paramètres du timer

- `OnBootSec=2min` : première exécution 2 minutes après le démarrage ;
- `OnUnitActiveSec=5min` : nouvelle exécution 5 minutes après la précédente activation ;
- `Unit=horodatage-lab.service` : service déclenché par le timer ;
- `WantedBy=timers.target` : permet d'activer automatiquement le timer.

!!! note "Nom du service et nom du timer"
    Par convention, on utilise le même nom de base :
    
    - `horodatage-lab.service`
    - `horodatage-lab.timer`
    
    Cela rend la configuration plus simple à lire et à maintenir.

### Étape 6 : activer et démarrer le timer

Rechargez à nouveau `systemd`, puis activez immédiatement le timer :

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now horodatage-lab.timer
```

Vérifiez ensuite son état :

```bash
sudo systemctl status horodatage-lab.timer --no-pager
```

Affichez aussi la liste des timers connus du système :

```bash
sudo systemctl list-timers --all
```

Exemple de lecture :

```text
NEXT                         LEFT    LAST                         PASSED    UNIT                  ACTIVATES
Sat 2026-05-30 18:15:00 CEST 4min    Sat 2026-05-30 18:10:00 CEST 10s ago   horodatage-lab.timer  horodatage-lab.service
```

!!! success "Résultat attendu"
    Le timer `horodatage-lab.timer` doit apparaître dans la liste avec une prochaine exécution prévue.

### Étape 7 : vérifier l'exécution automatique

Après quelques minutes, contrôlez si de nouvelles lignes ont été ajoutées au fichier de log :

```bash
sudo tail -n 10 /var/log/horodatage-lab.log
```

Contrôlez également le journal systemd du service :

```bash
sudo journalctl -u horodatage-lab.service -n 20 --no-pager
```

Si vous voulez revoir l'état du timer :

```bash
sudo systemctl list-timers --all | grep horodatage-lab
```

!!! success "Résultat attendu"
    Vous devez voir plusieurs lignes horodatées dans le fichier, preuve que le timer relance bien le service automatiquement.

### Étape 8 : modifier le timer pour une exécution quotidienne

Dans un vrai environnement, on ne veut pas toujours lancer une tâche toutes les 5 minutes.
Vous pouvez remplacer le timer précédent par un déclenchement à heure fixe.

Exemple : exécuter le service tous les jours à **08:00**.

Modifiez `/etc/systemd/system/horodatage-lab.timer` pour obtenir :

```ini
[Unit]
Description=Exécuter horodatage-lab.service chaque jour à 08:00

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true
Unit=horodatage-lab.service

[Install]
WantedBy=timers.target
```

Rechargez ensuite la configuration et redémarrez le timer :

```bash
sudo systemctl daemon-reload
sudo systemctl restart horodatage-lab.timer
sudo systemctl list-timers --all | grep horodatage-lab
```

### Pourquoi `Persistent=true` ?

Avec un timer basé sur `OnCalendar`, `Persistent=true` permet de rattraper une exécution manquée si la machine était arrêtée au moment prévu.

Exemple :

- le timer devait s'exécuter à `08:00` ;
- la VM était éteinte à cette heure-là ;
- au redémarrage, `systemd` peut lancer le service immédiatement pour rattraper le passage manqué.

!!! warning "Important"
    Le comportement `Persistent=true` concerne les timers basés sur `OnCalendar`.
    Dans notre premier exemple avec `OnBootSec` et `OnUnitActiveSec`, on travaille avec une logique d'intervalle, pas avec une heure fixe dans le calendrier.

### Étape 9 : désactiver ou supprimer le timer si besoin

Pour arrêter le déclenchement automatique sans supprimer les fichiers :

```bash
sudo systemctl disable --now horodatage-lab.timer
```

Pour le réactiver plus tard :

```bash
sudo systemctl enable --now horodatage-lab.timer
```

Si vous voulez supprimer complètement le TP :

```bash
sudo systemctl disable --now horodatage-lab.timer
sudo rm -f /etc/systemd/system/horodatage-lab.timer
sudo rm -f /etc/systemd/system/horodatage-lab.service
sudo rm -f /usr/local/bin/horodatage-lab.sh
sudo systemctl daemon-reload
```

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `sudo systemctl daemon-reload` | Recharger les unités systemd après une modification |
| `sudo systemctl start horodatage-lab.service` | Lancer le service immédiatement |
| `sudo systemctl status horodatage-lab.service --no-pager` | Vérifier l'état du service |
| `sudo systemctl enable --now horodatage-lab.timer` | Activer et démarrer le timer |
| `sudo systemctl status horodatage-lab.timer --no-pager` | Vérifier l'état du timer |
| `sudo systemctl list-timers --all` | Lister les timers connus du système |
| `sudo journalctl -u horodatage-lab.service -n 20 --no-pager` | Lire les derniers journaux du service |
| `sudo systemctl disable --now horodatage-lab.timer` | Désactiver le timer |

## Glossaire

`service unit`
:   Fichier `systemd` décrivant comment exécuter une action, par exemple un script.

`timer unit`
:   Fichier `systemd` chargé de planifier l'activation d'un service.

`oneshot`
:   Type de service adapté à une commande courte qui s'exécute puis se termine.

`OnCalendar`
:   Directive utilisée pour planifier une exécution à un moment précis du calendrier.

## Vérification

Pour valider que le TP fonctionne de bout en bout :

```bash
sudo systemctl status horodatage-lab.timer --no-pager
sudo systemctl list-timers --all | grep horodatage-lab
sudo tail -n 10 /var/log/horodatage-lab.log
```

!!! success "Résultat attendu"
    Le timer doit être actif, une prochaine exécution doit être planifiée et le fichier `/var/log/horodatage-lab.log` doit contenir des lignes ajoutées automatiquement.

## Ressources

- [systemd.timer — documentation officielle](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) — Référence sur les timers, `OnBootSec`, `OnUnitActiveSec`, `OnCalendar` et `Persistent`
- [systemd.service — documentation officielle](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) — Référence sur les types de services comme `oneshot`
- [systemd.unit — documentation officielle](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html) — Structure générale des unités `systemd`
- [systemctl — documentation officielle](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) — Commandes d'administration et de vérification
- [systemd.time — documentation officielle](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html) — Syntaxe des dates, durées et expressions calendaires
