---
title: "NVIDIA — Écran noir après sortie de veille"
date: 2026-09-06
author: Nicolas BODAINE
tags:
  - nvidia
  - veille
  - suspend
  - écran noir
  - systemd
  - kernel
  - fbcon
difficulty: avancé
os: Ubuntu 24.04
status: publié
---

# NVIDIA — Écran noir après sortie de veille

!!! abstract "Résumé"
    Après une mise en veille (suspend S3), le PC se réveille mais l'écran reste noir, et `Ctrl+Alt+F3` ne répond pas non plus : la machine est totalement figée et seul l'arrêt forcé permet d'en sortir.

    La cause n'est **pas** une VRAM mal restaurée. C'est un **interblocage entre deux verrous du noyau** — le verrou console (`console_lock`) et le verrou de gestion d'énergie de `nvidia-modeset` (`nvkms_pm_lock`) — qui ne peut se produire **qu'au premier réveil de chaque démarrage**.

    Le correctif tient en un paramètre noyau : **`fbcon=nodefer`**.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Avancé |
| OS / Environnement | Ubuntu 24.04 Desktop — GNOME — X11 |
| GPU | NVIDIA GeForce GTX 1060 6GB (GP106, Pascal) |
| Driver | nvidia-driver-580 (580.173.02) |
| Noyau | 7.0.0-31-generic (HWE) |
| Dernière mise à jour | 2026-09-06 |

!!! warning "Cette fiche corrige entièrement une version précédente"
    La version du 2026-05-30 attribuait la panne à une restauration de VRAM défaillante et à un mécanisme `WantedBy` cassé. **Ces deux diagnostics étaient faux.** Les remèdes qui en découlaient étaient structurellement inopérants : ils s'exécutaient en aval du point de blocage et n'ont jamais tourné lors d'un seul incident. Le détail et les preuves sont en fin de fiche, section « Pourquoi les correctifs précédents ne pouvaient pas fonctionner ».

## Contexte

Sur un poste Ubuntu 24.04 + GNOME + X11 avec pilote NVIDIA propriétaire, la mise en veille S3 se déroule normalement et le système se réveille bien (les ventilateurs repartent, le réseau revient, la machine reste joignable en SSH), mais l'affichage ne revient jamais.

Le point qui égare le diagnostic est l'**intermittence** : la panne ne survient pas à chaque veille. Sur le poste de référence, la mesure sur près de quatre mois donne **8 gels sur 22 mises en veille, soit 36 %**. Cette irrégularité fait croire à une régression de version ou à un effet de mise à jour, alors qu'il s'agit d'une course entre deux tâches du noyau.

!!! info "L'exposition est d'un seul événement par démarrage"
    Le mécanisme ne peut se déclencher qu'à la **première** sortie de veille suivant un démarrage. Une fois cette première sortie passée sans encombre, toutes les veilles suivantes du même démarrage sont sûres. Sur le poste de référence, un démarrage a enchaîné trois veilles avec une seule fenêtre d'exposition.

## Symptômes

!!! failure "Symptôme principal — gel total au réveil"
    - Le système sort de veille S3 (`PM: suspend exit` présent dans les journaux).
    - L'écran reste noir définitivement.
    - `Ctrl+Alt+F3` puis `Ctrl+Alt+F2` ne restaurent rien : **aucune console virtuelle ne peut plus s'ouvrir**.
    - Le bouton d'alimentation est enregistré (`Power key pressed short`) mais sans effet.
    - La machine répond encore au réseau (SSH, Tailscale, ping) : le noyau tourne, seul l'affichage et le sous-système TTY sont bloqués.
    - Au bout de 121 secondes, le noyau signale des tâches bloquées (`INFO: task ... blocked for more than 121 seconds`).

Ne pas confondre avec un symptôme voisin et distinct : la veille qui **refuse de s'enclencher** avec `nvidia 0000:01:00.0: PM: failed to suspend async: error -5`. Ce cas-là est traité en fin de fiche.

## Le mécanisme réel

### La condition structurelle : la prise de console différée

Le noyau Ubuntu est compilé avec `CONFIG_FRAMEBUFFER_CONSOLE_DEFERRED_TAKEOVER=y`. Combiné à `quiet splash` et `vt.handoff=7` dans la ligne de commande, cela signifie que la console graphique `fbcon` **n'est pas attachée au démarrage** : elle attend qu'un message soit imprimé sur une console en mode texte pour prendre la main, afin de ne pas gâcher l'animation Plymouth.

```bash
grep FRAMEBUFFER_CONSOLE_DEFERRED /boot/config-$(uname -r)
# CONFIG_FRAMEBUFFER_CONSOLE_DEFERRED_TAKEOVER=y

journalctl -k -b 0 | grep 'Deferring console take-over'
# fbcon: Deferring console take-over   (x2)

ls /sys/class/vtconsole/
# vtcon0 seulement — et son nom est "(S) dummy device"
```

Ce piège est **réarmé à chaque démarrage**.

### Le déclencheur : `chvt 63` puis un message noyau au réveil

À l'endormissement, le script du pilote `/usr/bin/nvidia-sleep.sh` bascule sur la console virtuelle 63, une VT neuve en mode texte (contrairement à la VT de la session X, qui est en mode graphique) :

```bash
fgconsole > "${XORG_VT_FILE}"
chvt 63
echo "$1" > /proc/driver/nvidia/suspend
```

Cette dernière écriture fait prendre à `nvidia_modeset_suspend()` le verrou `nvkms_pm_lock` **en écriture**, et ce verrou est conservé pendant **toute la durée de la veille**.

Au réveil, `resume_console()` vide la file des messages noyau vers la VT63, qui est en mode texte. Le premier message dont la priorité passe le filtre `console_loglevel` déclenche alors la prise de console différée. Sur le poste de référence, avec `console_loglevel = 4`, ce message est `Bluetooth: hci0: No support for _PRR ACPI method` (priorité 3), et `fbcon: Taking over console` suit **31 microsecondes plus tard**.

!!! tip "Identifier le déclencheur sur votre machine"
    Le message coupable dépend du matériel. Il faut chercher, parmi les messages du réveil, le dernier dont la priorité est **strictement inférieure** au premier chiffre de `/proc/sys/kernel/printk`.

    ```bash
    cat /proc/sys/kernel/printk        # ex. : 4 4 1 7  -> seuls les niveaux 0 à 3 s'affichent
    journalctl -k -b -1 -o json | \
      python3 -c "
    import sys,json
    for l in sys.stdin:
        try: j=json.loads(l)
        except: continue
        m=j.get('MESSAGE','')
        if isinstance(m,list): m=''.join(map(chr,m))
        if 'Taking over console' in m or int(j.get('PRIORITY',9))<4:
            print(j.get('__MONOTONIC_TIMESTAMP'), j.get('PRIORITY'), m[:70])
    "
    ```

    Un message de priorité 4 ou plus (`xhci_hcd ... xHC error in resume` par exemple) ne peut **pas** être le déclencheur : il n'est pas imprimé sur la console.

### L'interblocage

Deux chemins se croisent alors, chacun détenant ce que l'autre attend.

**Chemin A — la prise de console.** Le worker noyau prend `console_lock`, puis descend jusqu'au pilote NVIDIA et demande `nvkms_pm_lock` en lecture :

```text
fbcon_register_existing_fbs
  └─ do_fb_registered → do_fbcon_takeover
       └─ do_take_over_console        ← PREND console_lock
            └─ do_bind_con_driver → visual_init → fbcon_init
                 └─ drm_fb_helper_set_par
                      └─ __drm_fb_helper_restore_fbdev_mode_unlocked
                           └─ drm_fb_helper_hotplug_event
                                └─ drm_client_modeset_probe
                                     └─ drm_helper_probe_single_connector_modes
                                          └─ nv_drm_connector_detect [nvidia_drm]
                                               └─ nvkms_ioctl_from_kapi [nvidia_modeset]
                                                    └─ down_read(nvkms_pm_lock)  ← BLOQUE
```

**Chemin B — la sortie de veille du pilote.** `echo resume > /proc/driver/nvidia/suspend` appelle `nv_resume_devices()`, qui exécute d'abord `nvidia_resume()` puis, **en dernier seulement**, `nvidia_modeset_resume(0)` — c'est-à-dire l'unique libérateur de `nvkms_pm_lock`. Or `nvidia_resume()` passe par `rm_power_management()` → `os_disable_console_access()`, qui demande… `console_lock`.

Le libérateur du verrou qu'attend le chemin A est donc lui-même bloqué derrière le verrou que le chemin A détient. Les deux verrous sont ininterruptibles : **aucune tâche n'est tuable, plus aucun terminal ne peut s'ouvrir**, d'où l'écran noir et l'impossibilité de basculer sur une console texte.

!!! quote "Le noyau nomme lui-même le cycle"
    ```text
    INFO: task kworker/5:0:27371 <reader> blocked on an rw-semaphore
          likely owned by task kworker/u32:27:27352 <writer>
    INFO: task nvidia-sleep.sh:27414 blocked on a semaphore
          likely last held by task kworker/5:0:27371
    ```
    La première ligne est le worker `fbcon` (`Workqueue: events fbcon_register_existing_fbs`) qui attend le verrou NVIDIA. La seconde est `nvidia-sleep.sh` qui attend le verrou console détenu par ce même worker. Le cycle est fermé.

## Diagnostic

### 1. Vérifier que le piège est armé sur le démarrage courant

```bash
journalctl -k -b 0 | grep -c 'Deferring console take-over'   # 2 = piège armé
ls /sys/class/vtconsole/                                      # vtcon0 seul = fbcon non attaché
cat /proc/fb                                                  # 0 nvidia-drmdrmfb
```

### 2. Déterminer si un réveil a réussi ou échoué

Le marqueur le plus fiable est la présence de la ligne de bascule framebuffer après un `Taking over console` :

```bash
journalctl -k -b -1 | grep -E 'Taking over console|switching to colour frame buffer'
```

!!! success "Réveil réussi"
    Les **deux** lignes sont présentes : la prise de console est allée au bout.

!!! failure "Réveil bloqué"
    `fbcon: Taking over console` est présent mais `Console: switching to colour frame buffer device` est **absent** : la prise de console s'est arrêtée en plein milieu, dans le pilote NVIDIA.

Sur le poste de référence, cette séparation est parfaite sur six démarrages : les deux démarrages où la seconde ligne manquait sont exactement les deux qui ont gelé.

### 3. Confirmer par les tâches bloquées

```bash
journalctl -k -b -1 | grep -A25 'blocked for more than'
```

La signature à reconnaître est un `kworker` avec `Workqueue: events fbcon_register_existing_fbs`, bloqué sur `down_read` via `nv_drm_connector_detect` et `nvkms_ioctl_from_kapi`.

### 4. Capturer la pile du détenteur du verrou (depuis un autre poste)

La machine reste joignable par le réseau pendant le gel. C'est la seule occasion d'obtenir la donnée décisive.

```bash
ssh utilisateur@machine-gelee
sudo sh -c 'echo w > /proc/sysrq-trigger'          # liste les tâches en attente ininterruptible
P=$(pgrep -f 'nvidia-sleep.sh resume'); sudo cat /proc/$P/stack
sudo dmesg | tail -300 | tee /tmp/gel.txt
sudo systemctl reboot -f                            # seulement APRÈS la capture
```

!!! danger "N'utilisez que `echo w`"
    `echo w` se contente d'imprimer les tâches bloquées. Les touches magiques `b` (redémarrage immédiat) et `c` (plantage volontaire) provoquent une perte de données.

## Solution

### Étape 1 : rendre le menu GRUB visible (filet de sécurité, à faire en premier)

Sur beaucoup d'installations Ubuntu, `GRUB_TIMEOUT=0` et `GRUB_TIMEOUT_STYLE=hidden` : aucun menu ne s'affiche, donc aucun moyen de retirer un paramètre noyau qui poserait problème. Cette étape ne change rien au fonctionnement, elle ouvre seulement la porte de secours.

```bash
sudo mkdir -p /root/rollback-nvidia
sudo cp -a /etc/default/grub /boot/grub/grub.cfg /root/rollback-nvidia/
printf '%s\n' 'GRUB_TIMEOUT_STYLE=menu' 'GRUB_TIMEOUT=5' \
  | sudo tee /etc/default/grub.d/98-menu-visible.cfg
sudo update-grub
```

### Étape 2 : appliquer `fbcon=nodefer`

Le paramètre attache `fbcon` **dès le démarrage**, alors que le GPU est éveillé et qu'aucun verrou de gestion d'énergie n'est détenu. Dès lors, `fbcon_register_existing_fbs` ne peut plus jamais être programmé au réveil : l'arête du cycle disparaît, au lieu de voir sa probabilité réduite.

```bash
sudo tee /etc/default/grub.d/99-fbcon-nodefer.cfg >/dev/null <<'EOF'
# Correctif ecran noir au premier reveil : attache fbcon des le demarrage
# pour supprimer l'interblocage console_lock <-> nvkms_pm_lock.
GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT fbcon=nodefer"
EOF
sudo update-grub
```

!!! warning "Contrôler avant de redémarrer"
    ```bash
    sudo grep -m1 -o 'quiet splash[^"]*' /boot/grub/grub.cfg
    # attendu : quiet splash ... fbcon=nodefer $vt_handoff
    ```
    Si `fbcon=nodefer` n'apparaît pas, **ne pas redémarrer** : le fichier n'a pas été pris en compte.

    La présence de `$vt_handoff` est normale et voulue : `/etc/grub.d/10_linux` le réinjecte tant que `splash` est présent. Plymouth est conservé.

!!! tip "Pourquoi un fichier dans `/etc/default/grub.d/` plutôt qu'une édition de `/etc/default/grub`"
    `grub-mkconfig` lit ce répertoire, et `/etc/kernel/postinst.d/zz-update-grub` relance `update-grub` à chaque nouveau noyau : le paramètre est donc réappliqué automatiquement à chaque mise à jour, sans intervention.

### Étape 3 : retirer les remèdes empilés par l'ancien diagnostic

Si vous aviez appliqué la version précédente de cette fiche, ces éléments sont inutiles et ajoutent 3 à 4 secondes de latence à chaque réveil. On les déplace plutôt que de les supprimer.

```bash
sudo systemctl disable --now nvidia-display-restore.service
sudo mkdir -p /root/rollback-nvidia/systemd
sudo mv /etc/systemd/system/nvidia-display-restore.service /root/rollback-nvidia/systemd/
sudo mv /etc/systemd/system/systemd-suspend.service.d/nvidia-resume.conf /root/rollback-nvidia/systemd/
sudo systemctl daemon-reload
```

!!! danger "Ne pas toucher aux unités du paquet"
    `nvidia-suspend.service`, `nvidia-resume.service`, `nvidia-hibernate.service` et le hook `/usr/lib/systemd/system-sleep/nvidia` appartiennent à `nvidia-kernel-common-580` et doivent rester **activés et intacts**. Ce sont eux qui font réellement le travail.

### Étape 4 : redémarrer et vérifier

```bash
sudo reboot
```

## Vérification

À lancer après le redémarrage, **avant** toute mise en veille :

```bash
grep -o 'fbcon=nodefer' /proc/cmdline                          # attendu : fbcon=nodefer
journalctl -k -b 0 | grep -c 'Deferring console take-over'     # attendu : 0   (avant : 2)
ls /sys/class/vtconsole/                                        # attendu : vtcon0 ET vtcon1
cat /sys/class/vtconsole/vtcon1/name                            # attendu : frame buffer device
journalctl -k -b 0 | grep -c 'switching to colour frame buffer' # attendu : >= 1, au démarrage
cat /proc/fb                                                    # attendu : 0 nvidia-drmdrmfb
```

Puis vérifier manuellement que `Ctrl+Alt+F3` affiche bien une invite de connexion et que `Ctrl+Alt+F2` ramène la session graphique.

Après chaque réveil de veille :

```bash
journalctl -k -b 0 | grep -c 'Taking over console'    # attendu : 0
journalctl -k -b 0 | grep -c 'blocked for more than'  # attendu : 0
```

!!! warning "Un seul réveil réussi ne prouve rien"
    Le taux d'échec de référence étant d'environ 36 %, un unique réveil réussi avait déjà près de deux chances sur trois de survenir par hasard. Comme l'exposition est d'un événement par démarrage, un cycle de test utile est : **redémarrage → première veille → réveil**. Il faut environ 6 à 8 cycles sans échec pour conclure sérieusement.

!!! failure "Ce qui invaliderait ce diagnostic"
    Un gel au réveil **alors que** `journalctl -k -b 0 | grep 'Taking over console'` ne renvoie rien. Dans ce cas, `fbcon` est hors de cause : capturer la pile du détenteur (section Diagnostic, point 4) avant toute autre modification.

## Pourquoi les correctifs précédents ne pouvaient pas fonctionner

Cette section conserve la trace des erreurs de la version du 2026-05-30, pour éviter qu'elles ne soient réintroduites.

!!! failure "Erreur 1 — « `WantedBy=systemd-suspend.service` est cassé sur systemd 255 »"
    **Faux.** C'est cette affirmation qui a motivé la construction de trois couches de redondance.

    Le mécanisme fonctionne parfaitement : les liens existent dans `/etc/systemd/system/systemd-suspend.service.wants/`, et les journaux de tous les réveils **réussis** contiennent `nvidia-resume.service ExecStartPre TRIGGERED`. Il paraissait cassé parce qu'on ne l'observait que les jours de gel, où `systemd-suspend.service` ne se termine jamais et où, par conséquent, rien de ce qui vient après ne s'exécute.

!!! failure "Erreur 2 — les remèdes ajoutés étaient en aval du blocage"
    `nvidia-display-restore.service` et le drop-in `ExecStartPost` sur `systemd-suspend.service` ne s'exécutent qu'**après** la fin de `systemd-suspend.service`. Or le blocage se produit à l'intérieur du hook `/usr/lib/systemd/system-sleep/nvidia`, donc pendant l'exécution de ce service.

    Mesure sur le poste de référence : 22 réveils tracés, 14 lignes `ExecStartPost reached`. Lors des 8 gels, ces remèdes ont tourné **zéro fois**. Ils ne pouvaient pas fonctionner, et ils coûtaient 3 à 4 secondes à chaque réveil réussi.

!!! failure "Erreur 3 — « `nvidia-sleep.sh resume` est idempotent, l'appeler plusieurs fois est sans risque »"
    **Faux.** Dans `nv.c`, `nv_set_system_power_state()` prend un sémaphore **ininterruptible** *avant* son test d'idempotence :

    ```c
    down(&nv_system_power_state_lock);
    ...
    if (nv_system_power_state == power_state) { status = NV_OK; goto done; }
    ```

    Une seconde écriture concurrente ne « ne fait rien » : elle se bloque en état D, non tuable. Multiplier les chemins de restauration ne fiabilise rien, cela multiplie les tâches ingérables.

!!! failure "Erreur 4 — « `NVreg_PreserveVideoMemoryAllocations=0` provoque l'erreur -5 »"
    **Inversion de causalité.** Le code de `nvidia_suspend()` montre que le message provient de la condition inverse :

    ```c
    if (nv->preserve_vidmem_allocations && !is_procfs_suspend) {
        /* "PreserveVideoMemoryAllocations module parameter is set.
            System Power Management attempted without driver procfs suspend interface." */
        status = NV_ERR_NOT_SUPPORTED;   /* remonté en -EIO = -5 */
    }
    ```

    L'erreur -5 survient donc quand `Preserve` vaut **1** *et* que l'interface procfs n'est pas utilisée — typiquement après avoir masqué `nvidia-suspend.service`. C'est le cas traité par les étapes ci-dessous, et il est distinct du gel au réveil.

!!! failure "Erreur 5 — attribuer la panne à une mise à jour de noyau ou de firmware"
    Sur le poste de référence, les gels s'étalent de façon continue sur quatre mois, dont sept sans aucune mise à jour préalable. De plus, le firmware NVIDIA GSP ne concerne que les architectures Turing et ultérieures : une carte Pascal (GTX 10xx) n'en charge aucun. Et une recompilation DKMS pour un noyau qui n'est pas celui en cours d'exécution ne touche pas le module chargé, lequel réside entièrement en mémoire.

## Cas voisin : la veille refuse de s'enclencher (erreur -5)

Ce symptôme est **différent** du gel au réveil et se traite séparément.

```text
nvidia 0000:01:00.0: PM: failed to suspend async: error -5
Failed to put system to sleep. System resumed again: Input/output error
```

Il signifie que `NVreg_PreserveVideoMemoryAllocations=1` est actif mais que les scripts qui font réellement la sauvegarde de VRAM ne sont pas exécutés. Vérifier dans l'ordre :

```bash
# 1. Le module DKMS est-il compilé pour le noyau courant ?
dkms status                                    # "installed" et non "added"
sudo apt-get install -y linux-headers-$(uname -r)

# 2. Les unités du pilote sont-elles activées ?
systemctl is-enabled nvidia-suspend nvidia-resume nvidia-hibernate
sudo systemctl enable nvidia-suspend.service nvidia-resume.service nvidia-hibernate.service

# 3. Le chemin de sauvegarde est-il cohérent ?
grep -r 'NVreg_' /etc/modprobe.d/
cat /proc/driver/nvidia/params | grep -E 'Preserve|TemporaryFilePath'
```

`NVreg_TemporaryFilePath` doit pointer vers un répertoire disposant d'assez d'espace libre pour le contenu de la VRAM (`/var/tmp` convient).

## Piège annexe : ne pas purger le métapaquet orphelin

Sur ce type d'installation, on trouve parfois un ancien métapaquet (`nvidia-driver-575` par exemple) resté installé à côté du pilote courant. Il est tentant de le purger par propreté.

!!! danger "Vérifier avant de purger"
    Ce métapaquet peut être le **seul** paquet NVIDIA marqué « installé manuellement ». Le retirer fait alors basculer toute la pile graphique en « installée automatiquement », et le premier `apt autoremove` supprime le pilote.

    ```bash
    apt-mark showmanual | grep -i nvidia          # qui ancre la pile ?
    apt-get -s remove <metapaquet> | grep -ci nvidia   # simulation, aucune modification
    ```

    Corriger d'abord l'ancrage, purger ensuite :

    ```bash
    sudo apt-mark manual nvidia-driver-580 nvidia-dkms-580 nvidia-utils-580 \
                         xserver-xorg-video-nvidia-580 nvidia-kernel-common-580 dkms
    ```

## Ressources

- [NVIDIA Driver README — Power Management](https://download.nvidia.com/XFree86/Linux-x86_64/580.65.06/README/powermanagement.html) — comportement officiel du pilote en veille, rôle de `NVreg_PreserveVideoMemoryAllocations`
- [NVIDIA Driver README — GSP Firmware](https://download.nvidia.com/XFree86/Linux-x86_64/580.65.06/README/gsp.html) — confirme que le firmware GSP ne concerne que Turing et au-delà
- [LWN — Deferred console takeover](https://lwn.net/Articles/758312/) — le mécanisme `CONFIG_FRAMEBUFFER_CONSOLE_DEFERRED_TAKEOVER` à l'origine du piège
- [Arch Wiki — NVIDIA/Tips and tricks : Preserve video memory](https://wiki.archlinux.org/title/NVIDIA/Tips_and_tricks) — guide de référence communautaire
- [Ubuntu Launchpad #2158993](https://bugs.launchpad.net/ubuntu/+source/linux/+bug/2158993) — rapport amont décrivant le même interblocage entre `nvidia_modeset` et le sous-système console/fbcon, dans un contexte différent (pilote 595-open, Wayland) : le mécanisme n'est donc pas propre à cette configuration
