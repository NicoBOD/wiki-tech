---
title: "Bluetooth — Écouteurs appairés mais absents des sorties audio (WirePlumber/HFP)"
date: 2026-09-08
author: Nicolas BODAINE
tags:
  - bluetooth
  - wireplumber
  - pipewire
  - audio
  - hfp
  - a2dp
  - gnome
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Bluetooth — Écouteurs appairés mais absents des sorties audio (WirePlumber/HFP)

!!! abstract "Résumé"
    Un casque ou des écouteurs Bluetooth s'appairent et se connectent normalement (`Connected: yes` dans `bluetoothctl`), mais **n'apparaissent jamais dans la liste des sorties audio** de GNOME Paramètres, ni dans `pactl`/`wpctl`. Tout se passe comme si l'appareil n'existait pas pour le son, alors que Bluetooth le voit parfaitement.

    La cause n'est **pas** un problème d'appairage. Le journal de WirePlumber tourne en boucle sur `RFCOMM receive command but modem not available: AT+CCLK?` : l'appareil ouvre une session **mains-libres (HFP)** que WirePlumber ne peut pas satisfaire, et cette négociation qui échoue en continu empêche le profil **A2DP** (lecture stéréo) de se stabiliser. Résultat : PipeWire ne crée jamais la carte audio correspondante, donc GNOME n'a rien à proposer.

    Le correctif force, pour cet appareil précis, une connexion en A2DP uniquement — sans désactiver le mode mains-libres pour le reste de vos périphériques Bluetooth.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 Desktop — GNOME |
| Serveur audio | PipeWire 1.0.5 + WirePlumber 0.4.17 |
| Dernière mise à jour | 2026-09-08 |

## Contexte

Diagnostiqué sur `pc-fixe` après l'appairage d'écouteurs Bluetooth (modèle Eumo V1). L'appairage se déroule sans erreur, mais l'appareil reste invisible dans **Paramètres → Son → Sortie**. Ce cas s'applique à n'importe quel casque/écouteurs Bluetooth affichant le même symptôme, pas seulement à ce modèle précis : la cause est un comportement de négociation de profil, pas un défaut matériel propre à un appareil.

!!! info "Ne pas confondre avec l'absence totale de son Bluetooth"
    Si **aucun** appareil Bluetooth n'a jamais fonctionné en audio sur cette machine (même un casque déjà connu pour bien fonctionner ailleurs), le problème est probablement plus basique : le paquet `libspa-0.2-bluetooth` (fourni par `pipewire-audio`) est absent. Vérifier avec `dpkg -l | grep libspa-0.2-bluetooth`. Cette fiche traite d'un cas différent : Bluetooth fonctionne, mais un appareil précis échoue à devenir une sortie audio.

## Comprendre la chaîne audio Bluetooth sous Linux

Sur un poste Ubuntu 24.04 (GNOME, PipeWire), un appareil audio Bluetooth traverse plusieurs couches avant d'apparaître dans les paramètres système. Chacune peut fonctionner indépendamment des autres :

```text
Bluetooth (contrôleur HCI, appairage)
  └─ BlueZ (bluetoothd) — daemon Bluetooth Linux, expose org.bluez sur D-Bus
       └─ WirePlumber (moniteur bluez5) — décide QUELS profils deviennent des nœuds PipeWire
            └─ PipeWire — graphe audio réel (carte, sink, source)
                 └─ pipewire-pulse — compatibilité protocole PulseAudio
                      └─ GNOME Paramètres → Son — liste les sinks disponibles
```

!!! note "BlueZ, D-Bus, PipeWire, WirePlumber : qui fait quoi ?"
    **BlueZ** est la pile Bluetooth officielle de Linux (le daemon `bluetoothd`). Il gère l'appairage, la connexion radio, et annonce les capacités audio de l'appareil (A2DP, HFP...) via **D-Bus** — un bus de communication inter-processus standard sur Linux, utilisé par les applications pour s'échanger des messages et exposer des services (ici, BlueZ expose l'objet `/org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX` représentant l'appareil connecté).

    **PipeWire** est le serveur multimédia qui a remplacé PulseAudio (audio) et JACK (audio professionnel) sur les distributions Linux récentes. Il gère le graphe réel des flux audio : cartes, sinks (sorties), sources (entrées).

    **WirePlumber** est le gestionnaire de politique de PipeWire : c'est lui qui décide, pour chaque périphérique détecté, s'il devient un nœud PipeWire et avec quels réglages. Pour le Bluetooth, WirePlumber embarque un greffon (« moniteur bluez5 ») qui dialogue avec BlueZ en D-Bus. **C'est cette étape précise qui échoue dans le cas traité ici** : BlueZ voit l'appareil connecté, mais WirePlumber ne parvient jamais à en faire une carte audio.

Cette distinction explique pourquoi `bluetoothctl` peut afficher une connexion parfaitement saine alors que le son est absent : `bluetoothctl` ne parle qu'à BlueZ (les deux premières couches), pas à PipeWire.

## Symptômes

!!! failure "Symptôme principal"
    - L'appareil apparaît dans `bluetoothctl devices` et passe à `Connected: yes` après appairage.
    - GNOME Paramètres → Son ne propose pas l'appareil dans la liste des sorties, comme s'il n'existait pas.
    - `pactl list cards short` et `pactl list sinks short` ne montrent **aucune** entrée `bluez_card.*` / `bluez_output.*` pour cet appareil.
    - Le journal de WirePlumber répète en boucle (toutes les ~10 secondes) :
      ```text
      RFCOMM receive command but modem not available: AT+CCLK?
      ```

## Diagnostic

!!! tip "Méthode"
    Avant de modifier quoi que ce soit, on vérifie chaque couche du schéma ci-dessus dans l'ordre, pour localiser précisément celle qui casse. Un correctif appliqué sans cette étape risque de traiter le mauvais symptôme.

### 1. Vérifier la connexion côté BlueZ

```bash
bluetoothctl devices
# Device AA:BB:CC:DD:EE:FF Nom de l'appareil

bluetoothctl info AA:BB:CC:DD:EE:FF
```

Vérifier dans la sortie :

- `Paired: yes` et `Connected: yes` — la connexion Bluetooth elle-même est saine.
- La présence de `UUID: Audio Sink` (A2DP) — l'appareil sait faire de la lecture stéréo.
- La présence de `UUID: Handsfree` — l'appareil propose aussi le profil mains-libres, source probable du conflit (voir plus bas).

Si `Connected` n'est pas `yes`, le problème est en amont (appairage/connexion Bluetooth) et sort du cadre de cette fiche.

### 2. Chercher la carte audio correspondante côté PipeWire

```bash
pactl list cards short | grep bluez
pactl list sinks short | grep bluez
wpctl status   # section "Audio > Devices" : chercher [bluez5]
```

**Aucun résultat** alors que `bluetoothctl` annonce `Connected: yes` confirme que la rupture se situe entre BlueZ et PipeWire — c'est-à-dire au niveau de WirePlumber.

### 3. Identifier la boucle HFP dans les journaux de WirePlumber

```bash
journalctl --user -u wireplumber --since "30 min ago" --no-pager \
  | grep -iE "AT\+CCLK|modem not available|unknown transport"
```

La présence de lignes répétées `RFCOMM receive command but modem not available: AT+CCLK?` confirme le diagnostic : l'appareil envoie des commandes AT (protocole de contrôle d'appel hérité des modems, réutilisé par le profil mains-libres) que WirePlumber ne sait pas traiter.

!!! note "Que sont HFP/HSP, et pourquoi des commandes « modem » sur un PC ?"
    **A2DP** (Advanced Audio Distribution Profile) transporte de l'audio stéréo haute qualité dans un seul sens — c'est le profil utilisé pour écouter de la musique.

    **HFP** (Hands-Free Profile) et son ancêtre **HSP** (Headset Profile) sont conçus pour les appels téléphoniques : audio bidirectionnel mais mono et basse qualité, plus un canal de contrôle qui transporte des **commandes AT** — le même jeu de commandes texte historiquement utilisé pour piloter les modems (`AT+CCLK?` demande l'heure courante, typiquement pour synchroniser l'horloge affichée par un kit mains-libres de voiture). Ce canal de contrôle circule sur **RFCOMM**, un protocole Bluetooth qui émule un port série.

    Un PC ne sait pas répondre comme le ferait un téléphone à toutes ces commandes. Si l'appareil Bluetooth insiste pour ouvrir une session HFP dès la connexion, et que cette négociation échoue en boucle, elle peut empêcher le profil A2DP de se stabiliser sur le même appareil.

### 4. Écarter un second serveur de son concurrent

Le journal WirePlumber peut aussi afficher cet avertissement :

```text
Properties changed in unknown transport '.../sep1/fd0'. Multiple sound server
instances (PipeWire/Pulseaudio/bluez-alsa) are probably trying to use
Bluetooth audio at the same time...
```

Ce message est trompeur pris isolément : il apparaît aussi quand la négociation HFP instable (étape 3) perturbe le suivi interne de WirePlumber, sans qu'un second serveur soit réellement en cause. Vérifier avant de conclure :

```bash
ps aux | grep -iE "pulseaudio|bluealsa" | grep -v grep
dpkg -l | grep -iE "^ii.*(pulseaudio-module-bluetooth|bluealsa)"
systemctl --user list-units --all --type=service | grep -iE "pulseaudio|bluealsa"
```

Si ces commandes ne renvoient rien (aucun processus, aucun paquet, aucun service actif), il n'y a pas de second serveur de son : l'avertissement corrobore simplement l'instabilité de la négociation HFP identifiée à l'étape 3.

## Solution

WirePlumber 0.4.x (celui d'Ubuntu 24.04) se configure en Lua. Le réglage qui désactive complètement HFP/HSP (`bluez5.hfphsp-backend`) est **global à tout le Bluetooth** : l'appliquer couperait le micro Bluetooth de tous vos autres casques, pas seulement de l'appareil fautif. La solution ci-dessous cible uniquement l'appareil concerné.

### Étape 1 : récupérer l'adresse MAC de l'appareil

```bash
bluetoothctl devices
# Device AA:BB:CC:DD:EE:FF Nom de l'appareil
```

WirePlumber désigne les cartes Bluetooth par un nom dérivé de cette adresse, deux-points remplacés par des underscores :

```bash
echo "AA:BB:CC:DD:EE:FF" | tr ':' '_'
# AA_BB_CC_DD_EE_FF   →  device.name = bluez_card.AA_BB_CC_DD_EE_FF
```

### Étape 2 : créer une règle WirePlumber ciblée sur cet appareil

```bash
mkdir -p ~/.config/wireplumber/bluetooth.lua.d
```

Créer `~/.config/wireplumber/bluetooth.lua.d/51-<nom-appareil>.lua` (remplacer `<nom-appareil>` par un repère lisible, ex. `casque-sport`) :

```lua title="~/.config/wireplumber/bluetooth.lua.d/51-<nom-appareil>.lua"
-- Restreint UN appareil Bluetooth précis à l'auto-connexion A2DP,
-- sans toucher au réglage HFP global (qui reste actif pour les autres
-- périphériques). Remplacer l'adresse ci-dessous par la vôtre (étape 1).
table.insert(bluez_monitor.rules, {
  matches = {
    {
      { "device.name", "matches", "bluez_card.AA_BB_CC_DD_EE_FF" },
    },
  },
  apply_properties = {
    ["bluez5.auto-connect"] = "[ a2dp_sink ]",
    ["device.profile"] = "a2dp-sink",
  },
})
```

!!! note "Pourquoi un nouveau fichier plutôt que modifier la config existante"
    WirePlumber charge **tous** les fichiers `.lua` du dossier `bluetooth.lua.d/`, aussi bien ceux du système (`/usr/share/wireplumber/bluetooth.lua.d/`) que ceux de l'utilisateur (`~/.config/wireplumber/bluetooth.lua.d/`), et les fusionne. `table.insert(bluez_monitor.rules, ...)` **ajoute** une règle à la liste existante au lieu de la remplacer : le fichier système d'origine reste intact, et la modification survit aux mises à jour du paquet `wireplumber`.

### Étape 3 : redémarrer WirePlumber et forcer une reconnexion

```bash
systemctl --user restart wireplumber
bluetoothctl disconnect AA:BB:CC:DD:EE:FF
bluetoothctl connect AA:BB:CC:DD:EE:FF
```

!!! success "Aucun droit root nécessaire"
    Toute cette procédure agit au niveau utilisateur (`~/.config`, `systemctl --user`) : pas de `sudo`, pas de redémarrage de la machine.

!!! warning "Effet de bord attendu, sans gravité"
    Si l'appareil continue d'ouvrir une session HFP de son propre chef (certains modèles le font sans que le PC ait rien demandé), la boucle `AT+CCLK?` peut persister dans les journaux. Dans les tests menés sur ce cas, cela n'a pas empêché le flux A2DP de rester stable — c'est un bruit de journal, pas un dysfonctionnement. Si le son venait à couper ou se déconnecter régulièrement, voir le repli ci-dessous.

!!! tip "Si le correctif ciblé ne suffit pas : le repli global"
    `bluez5.hfphsp-backend` ne peut se régler qu'au niveau du moniteur entier, pas par appareil. En dernier recours, dans `~/.config/wireplumber/bluetooth.lua.d/51-no-hfp.lua` :

    ```lua
    bluez_monitor.properties = {
      ["bluez5.hfphsp-backend"] = "none",
    }
    ```

    Puis `systemctl --user restart wireplumber`. Ceci désactive HFP/HSP pour **tous** les périphériques Bluetooth de la machine : plus de micro/appel via Bluetooth sur aucun appareil, mais la lecture audio A2DP reste intacte partout. À réserver au cas où le correctif ciblé de l'étape 2 ne suffit pas.

## Vérification

```bash
pactl list cards short | grep bluez
# doit afficher : NNN  bluez_card.AA_BB_CC_DD_EE_FF  module-bluez5-device.c

pactl list sinks short | grep bluez
# doit afficher : NNN  bluez_output.AA_BB_CC_DD_EE_FF.1  PipeWire  ...  RUNNING (ou SUSPENDED au repos)

wpctl status
# section Audio > Devices : l'appareil apparaît avec le tag [bluez5]
```

!!! success "Résultat attendu"
    L'appareil apparaît désormais dans **Paramètres → Son → Sortie** et peut y être sélectionné. Jouer un son doit faire passer le sink de `SUSPENDED` à `RUNNING` dans `pactl list sinks short`.

## Checklist

- [ ] `bluetoothctl info <MAC>` confirme `Connected: yes`
- [ ] `pactl list cards short` ne montre pas encore la carte `bluez_card.*` (avant correctif)
- [ ] Boucle `AT+CCLK?` repérée dans `journalctl --user -u wireplumber`
- [ ] Absence de second serveur de son confirmée (`ps aux`, `dpkg -l`, `systemctl --user list-units`)
- [ ] Règle créée dans `~/.config/wireplumber/bluetooth.lua.d/51-<nom-appareil>.lua`
- [ ] `systemctl --user restart wireplumber` puis reconnexion de l'appareil
- [ ] `pactl list cards short` / `wpctl status` montrent désormais l'appareil
- [ ] L'appareil est sélectionnable dans GNOME Paramètres → Son

## Glossaire

BlueZ
:   Pile Bluetooth officielle de Linux (daemon `bluetoothd`). Gère l'appairage, les connexions, et expose les appareils sur D-Bus.

D-Bus
:   Bus de communication inter-processus standard sur Linux, utilisé par les services système et applications pour s'échanger messages et appels de méthode.

A2DP (Advanced Audio Distribution Profile)
:   Profil Bluetooth de diffusion audio stéréo haute qualité, à sens unique (lecture de musique).

HFP / HSP (Hands-Free / Headset Profile)
:   Profils Bluetooth pour les appels téléphoniques : audio bidirectionnel mono basse qualité, plus un canal de contrôle par commandes AT.

RFCOMM
:   Protocole Bluetooth qui émule un port série (RS-232), utilisé notamment pour transporter les commandes AT du profil HFP/HSP.

PipeWire
:   Serveur multimédia Linux qui unifie audio et vidéo, remplaçant PulseAudio et JACK tout en restant compatible avec leurs clients respectifs.

WirePlumber
:   Gestionnaire de politique de PipeWire : décide quels périphériques deviennent quels nœuds audio, avec quels réglages. Configuré en Lua sur les versions 0.4.x (Ubuntu 24.04).

Service `systemd --user`
:   Service systemd démarré et géré dans la session d'un utilisateur connecté (`systemctl --user ...`), indépendamment des services système nécessitant les droits root.

## Ressources

- [ArchWiki — PipeWire](https://wiki.archlinux.org/title/PipeWire) — référence communautaire sur la configuration de PipeWire, y compris le Bluetooth.
- [ArchWiki — Bluetooth](https://wiki.archlinux.org/title/Bluetooth) — dépannage général de la pile Bluetooth sous Linux.
- [Documentation officielle WirePlumber](https://pipewire.pages.freedesktop.org/wireplumber/) — référence des propriétés et règles de configuration Lua.
