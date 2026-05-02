---
title: "NVIDIA — Écran noir après sortie de veille"
date: 2026-05-03
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
| Driver | nvidia-driver-580 (580.142) |
| Dernière mise à jour | 2026-05-03 |

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

### 5. Confirmer que nvidia-resume.service s'est exécuté au dernier réveil

```bash
journalctl -b -1 -u nvidia-suspend.service -u nvidia-resume.service -u nvidia-display-restore.service
```

!!! warning "Signe d'alerte — WantedBy silencieusement ignoré"
    Si `nvidia-suspend.service` apparaît mais **pas** `nvidia-resume.service`, le mécanisme
    `WantedBy=systemd-suspend.service` ne fonctionne pas dans le chemin de retour de veille
    sur **systemd 255** (Ubuntu 24.04).

    Les services sont activés et correctement liés dans `systemd-suspend.service.wants/`
    mais ne sont jamais déclenchés au réveil — même si les étapes 2 et 3 ont déjà été appliquées.
    → Appliquer l'**Étape 4** ci-dessous.

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

!!! warning "Limitation sur systemd 255 / Ubuntu 24.04"
    Ce service utilise `WantedBy=systemd-suspend.service`, le même mécanisme que
    `nvidia-resume.service`. Sur systemd 255, ce mécanisme peut échouer silencieusement
    au réveil : le service est activé mais jamais déclenché.
    Si l'écran reste noir malgré cette étape, appliquer l'**Étape 4**.

### Étape 4 : Drop-in systemd — garantir l'exécution au réveil

!!! info "Quand appliquer cette étape"
    À appliquer si, après les étapes 2 et 3, `nvidia-resume.service` n'apparaît toujours
    pas dans les journaux après un réveil (cf. Diagnostic — étape 5).

Ce drop-in attache `nvidia-sleep.sh resume` directement à `ExecStartPost` de
`systemd-suspend.service`, ce qui garantit son exécution indépendamment du mécanisme `WantedBy`.

```bash
sudo mkdir -p /etc/systemd/system/systemd-suspend.service.d/
sudo tee /etc/systemd/system/systemd-suspend.service.d/nvidia-resume.conf << 'EOF'
[Service]
ExecStartPost=-/usr/bin/nvidia-sleep.sh resume
EOF
sudo systemctl daemon-reload
```

!!! success "Pourquoi ce fix est plus fiable"
    - `ExecStartPost` s'exécute **toujours** dès que `systemd-sleep suspend` se termine (après le réveil), indépendamment de la version de systemd.
    - Le préfixe `-` ignore les erreurs éventuelles sans bloquer le service.
    - Le fichier est dans `/etc/systemd/system/` et ne sera pas écrasé par une mise à jour du driver.
    - `nvidia-sleep.sh resume` est idempotent : l'appeler en doublon avec le hook `/usr/lib/systemd/system-sleep/nvidia` existant est sans danger.

### Étape 5 : Vérifier la cohérence de la config modprobe

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

# Drop-in appliqué
systemctl cat systemd-suspend.service | grep -A2 ExecStart

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

    ExecStart=/usr/lib/systemd/systemd-sleep suspend
    # /etc/systemd/system/systemd-suspend.service.d/nvidia-resume.conf
    ExecStartPost=-/usr/bin/nvidia-sleep.sh resume

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

Après le réveil, vérifier que le drop-in s'est exécuté :

```bash
journalctl -b 0 -u systemd-suspend.service
```

!!! success "Résultat attendu après réveil"
    La sortie doit contenir une ligne mentionnant `nvidia-sleep.sh` dans l'`ExecStartPost`.

!!! tip "Astuce"
    Si l'écran met 2-3 secondes à revenir après le réveil, c'est normal (délai du service de restauration).

## Ressources

- [NVIDIA Driver README — Power Management](https://us.download.nvidia.com/XFree86/Linux-x86_64/580.126.09/README/powermanagement.html) — Documentation officielle NVIDIA sur la gestion de la veille
- [Arch Wiki — NVIDIA/Tips and tricks — Preserve video memory](https://wiki.archlinux.org/title/NVIDIA/Tips_and_tricks#Preserve_video_memory_after_suspend) — Guide de référence communautaire
