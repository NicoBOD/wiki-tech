---
title: "NVIDIA — Écran noir après sortie de veille"
date: 2026-04-07
author: Nicolas BODAINE
tags:
  - nvidia
  - veille
  - suspend
  - écran noir
  - systemd
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# NVIDIA — Écran noir après sortie de veille

!!! abstract "Résumé"
    Après une mise en veille (suspend S3), le PC sort bien de veille mais l'écran reste noir.
    Le problème vient du driver NVIDIA qui ne restaure pas correctement la VRAM et/ou le terminal virtuel (VT) au réveil.
    Cette fiche couvre le diagnostic complet et la correction définitive.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 Desktop — Gnome — X11 |
| GPU | NVIDIA GeForce GTX 1060 6GB |
| Driver | nvidia-driver-580 (580.126.09) |
| Dernière mise à jour | 2026-04-07 |

## Contexte

Après une mise à jour du noyau (ex. migration automatique via `unattended-upgrades`) ou du driver NVIDIA (ex. 535 → 580), la mise en veille peut échouer de deux façons :

1. **La veille ne s'enclenche pas** → le driver refuse de suspendre (erreur `-5`)
2. **L'écran reste noir au réveil** → la veille S3 fonctionne, le système revient, mais l'affichage n'est pas restauré

Les deux problèmes ont des causes liées mais distinctes.

## Problème

!!! failure "Symptôme 1 — La veille échoue immédiatement"
    ```
    nvidia 0000:01:00.0: PM: failed to suspend async: error -5
    PM: Some devices failed to suspend, or early wake event detected
    Failed to put system to sleep. System resumed again: Input/output error
    ```

!!! failure "Symptôme 2 — Écran noir au réveil"
    Le système sort de veille S3 (les ventilateurs tournent, le réseau revient) mais l'écran reste noir.
    `Ctrl+Alt+F3` puis `Ctrl+Alt+F2` ne restaure pas l'affichage.

## Diagnostic rapide

### 1. Vérifier les logs de la dernière veille

```bash
# Logs du boot actuel (si le système a été redémarré après le blocage)
journalctl -b -1 | grep -iE 'nvidia|suspend|resume|PM:|sleep'
```

### 2. Vérifier l'état DKMS

```bash
dkms status
```

!!! warning "Résultat à surveiller"
    Si le statut est `added` au lieu de `installed`, le module n'a pas été compilé.
    Cause probable : headers du noyau manquants.

### 3. Vérifier les services NVIDIA

```bash
systemctl is-enabled nvidia-suspend nvidia-resume nvidia-hibernate
```

### 4. Vérifier les paramètres du driver

```bash
cat /proc/driver/nvidia/params | grep -E 'Preserve|TemporaryFilePath'
```

## Solution

### Étape 1 : Installer les headers du noyau (si manquants)

```bash
sudo apt-get install -y linux-headers-$(uname -r)
```

Cela permet à DKMS de compiler le module NVIDIA pour le noyau actuel.

### Étape 2 : Activer les services NVIDIA de suspend/resume

```bash
sudo systemctl enable nvidia-suspend.service nvidia-resume.service nvidia-hibernate.service
```

!!! info "Pourquoi c'est nécessaire"
    Le paramètre `NVreg_PreserveVideoMemoryAllocations=1` demande au driver de sauvegarder la VRAM en veille.
    Mais sans ces services, les scripts `nvidia-sleep.sh` (qui font la sauvegarde/restauration effective) ne sont jamais exécutés → erreur -5 au suspend.

### Étape 3 : Créer un service de restauration d'affichage (filet de sécurité)

Le script `nvidia-sleep.sh` bascule sur le VT63 avant le suspend et doit revenir sur le bon VT au resume. Ce `chvt` échoue parfois silencieusement → écran noir.

Créer le service :

```bash
sudo tee /etc/systemd/system/nvidia-display-restore.service << 'EOF'
[Unit]
Description=Restore display after NVIDIA resume
After=nvidia-resume.service systemd-suspend.service
After=systemd-hibernate.service
After=systemd-suspend-then-hibernate.service

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 2
ExecStart=/bin/bash -c 'echo resume > /proc/driver/nvidia/suspend 2>/dev/null; VT=$(cat /sys/class/tty/tty0/active 2>/dev/null | tr -dc "0-9"); if [ "$VT" = "63" ] || [ -z "$VT" ] || [ "$VT" -gt 7 ]; then chvt 2; fi'

[Install]
WantedBy=systemd-suspend.service
WantedBy=systemd-hibernate.service
WantedBy=systemd-suspend-then-hibernate.service
EOF
```

Activer le service :

```bash
sudo systemctl daemon-reload
sudo systemctl enable nvidia-display-restore.service
```

### Étape 4 : Vérifier la cohérence de la config modprobe

```bash
grep -r 'NVreg_' /etc/modprobe.d/
```

S'assurer que `NVreg_TemporaryFilePath` pointe vers `/var/tmp` (et non `/var` tronqué) :

```bash
# Fichier généré par le driver :
cat /etc/modprobe.d/nvidia-graphics-drivers-kms.conf
```

Si nécessaire, corriger :

```bash
sudo sed -i 's|NVreg_TemporaryFilePath=/var$|NVreg_TemporaryFilePath=/var/tmp|' \
  /etc/modprobe.d/nvidia-graphics-drivers-kms.conf
```

## Vérification

Après avoir appliqué les corrections, vérifier la configuration complète :

```bash
# Services activés
systemctl is-enabled nvidia-suspend nvidia-resume nvidia-hibernate nvidia-display-restore

# Chaîne de services
systemctl list-dependencies systemd-suspend.service

# Paramètres NVIDIA
cat /proc/driver/nvidia/params | grep -E 'Preserve|TemporaryFilePath'

# Mode de veille
cat /sys/power/mem_sleep
```

!!! success "Résultat attendu"
    ```
    enabled
    enabled
    enabled
    enabled

    systemd-suspend.service
    ├─nvidia-display-restore.service
    ├─nvidia-resume.service
    ├─nvidia-suspend.service
    ├─system.slice
    └─sleep.target

    PreserveVideoMemoryAllocations: 1
    TemporaryFilePath: "/var/tmp"

    s2idle [deep]
    ```

Puis tester la mise en veille :

```bash
systemctl suspend
```

!!! tip "Astuce"
    Si l'écran met 2-3 secondes à revenir après le réveil, c'est normal (délai du service de restauration).

## Ressources

- [NVIDIA Driver README — Power Management](https://us.download.nvidia.com/XFree86/Linux-x86_64/580.126.09/README/powermanagement.html) — Documentation officielle NVIDIA sur la gestion de la veille
- [Arch Wiki — NVIDIA/Tips and tricks — Preserve video memory](https://wiki.archlinux.org/title/NVIDIA/Tips_and_tricks#Preserve_video_memory_after_suspend) — Guide de référence communautaire
