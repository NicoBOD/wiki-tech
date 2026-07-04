---
title: Analyser son réseau Wi-Fi en mode moniteur et tester l'injection avec Aircrack-ng
date: 2026-07-04
author: Nicolas BODAINE
tags:
  - wifi
  - aircrack-ng
  - audit
  - reseau
  - cybersecurite
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Analyser son réseau Wi-Fi en mode moniteur et tester l'injection avec Aircrack-ng

!!! abstract "Résumé"
    Utiliser une carte Wi-Fi USB compatible mode moniteur (ex : chipset Realtek RTL8814AU) pour scanner les réseaux environnants, capturer un handshake WPA/WPA2/WPA3, tester la robustesse d'un mot de passe par dictionnaire, et comprendre les limites imposées par les protections modernes (PMF/802.11w).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 (ou toute distribution Linux) |
| Dernière mise à jour | 2026-07-04 |

## Contexte

La plupart des cartes Wi-Fi internes de laptop sont bridées par leur driver/firmware et ne supportent ni le **mode moniteur** ni l'**injection de paquets**. Pour faire du diagnostic ou de l'audit Wi-Fi sérieux, on utilise généralement un adaptateur USB dédié — le chipset **Realtek RTL8814AU** (802.11ac, 3-4 flux MIMO) est un des plus répandus dans ce rôle, notamment parce qu'il est aujourd'hui bien supporté nativement par le driver in-kernel `rtw88` (basé sur `mac80211`/`cfg80211`), sans avoir besoin de compiler un driver externe.

Cette note documente le passage en mode moniteur, le scan, la capture d'un handshake et le test de robustesse d'un mot de passe Wi-Fi, avec les commandes et les explications théoriques associées.

!!! warning "Avertissement légal"
    Le mode moniteur et l'injection de paquets (deauth, capture de handshake, cracking) ne doivent être utilisés **que sur des réseaux dont vous êtes propriétaire**, ou pour lesquels vous disposez d'une **autorisation explicite et écrite** (audit professionnel encadré par contrat, CTF, labo dédié). Intercepter ou injecter des trames sur un réseau tiers sans autorisation est illégal dans la quasi-totalité des juridictions (interception de communications, accès frauduleux à un système). Vérifiez toujours deux fois le BSSID ciblé avant toute action.

## Prérequis

- Une carte Wi-Fi USB supportant le mode moniteur et l'injection (ex : chipset Realtek RTL8814AU, RTL8812AU, Atheros AR9271...).
- Les droits d'administrateur (`sudo`).
- `NetworkManager` installé (utilisé pour désactiver proprement la gestion automatique de l'interface).

## Procédure

### Étape 1 : Identifier la carte et installer les outils

```bash
# Vérifier que la carte est bien détectée et connaître son chipset
lsusb | grep -i realtek

# Voir le nom de l'interface, son état, et le driver utilisé
ip link show
readlink -f /sys/class/net/<interface>/device/driver

# Installer les outils nécessaires
sudo apt update
sudo apt install -y iw aircrack-ng
```

Pour connaître les capacités radio complètes de la carte (bandes 2.4/5 GHz, débits, modes supportés) :

```bash
iw dev <interface> info      # état actuel (mode, canal, phy)
iw phy phy<N> info           # capacités complètes de la puce radio
iw reg get                   # domaine réglementaire actif (impacte canaux/puissance autorisés)
```

### Étape 2 : Comprendre le mode moniteur et l'injection

Terme | Définition
------|-----------
Mode `managed` | Mode par défaut d'une carte Wi-Fi : elle est associée à un unique point d'accès (AP) et ne remonte que les trames qui lui sont destinées.
Mode `monitor` | La carte capture **toutes** les trames radio passant sur le canal écouté (beacons, probes, authentification, données...), quel que soit le destinataire. C'est la base de tout outil de diagnostic Wi-Fi (Wireshark, Kismet, aircrack-ng).
Injection de paquets | Capacité de la carte à émettre des trames 802.11 forgées manuellement (pas générées par la pile réseau normale), par exemple une trame de désauthentification. Beaucoup de drivers/firmwares le bloquent ; c'est un point de compatibilité clé pour l'audit Wi-Fi.

### Étape 3 : Basculer l'interface en mode moniteur

```bash
# 1. Empêcher NetworkManager de reprendre la main sur l'interface
sudo nmcli device set <interface> managed no

# 2. Couper l'interface
sudo ip link set <interface> down

# 3. Passer en mode monitor
sudo iw dev <interface> set type monitor

# 4. Réactiver l'interface
sudo ip link set <interface> up
```

!!! success "Résultat attendu"
    `iw dev <interface> info` doit maintenant afficher `type monitor` et un canal actif.

### Étape 4 : Tester l'injection

```bash
sudo aireplay-ng --test <interface>
```

Un pourcentage d'injection non nul confirme que la carte peut émettre des trames forgées vers les AP environnants.

### Étape 5 : Scanner les réseaux environnants

```bash
sudo airodump-ng <interface>
```

Affiche en direct les AP visibles (BSSID, canal, chiffrement WEP/WPA/WPA2/WPA3, puissance, ESSID) et les stations (clients) associées. `Ctrl+C` pour arrêter.

Pour un scan de durée fixe exploitable ensuite (CSV) :

```bash
sudo timeout 20 airodump-ng --output-format csv -w scan <interface>
cat scan-01.csv
```

**Repérez précisément le BSSID et le canal de votre propre AP** avant de poursuivre — ne jamais cibler un BSSID dont vous n'êtes pas certain de la propriété.

### Étape 6 : Capturer le trafic ciblé sur son propre AP

```bash
sudo airodump-ng -c <canal> --bssid <BSSID_de_mon_AP> -w capture <interface>
```

- `-c` fixe le canal d'écoute (indispensable pour une capture propre, évite le saut de canal en canal).
- `--bssid` filtre uniquement les trames de cet AP.
- `-w capture` écrit les paquets dans `capture-01.cap`.

### Étape 7 : Provoquer une reconnexion pour capturer le handshake

Une connexion WPA/WPA2-PSK repose sur un **4-way handshake** : l'AP et le client échangent 4 messages EAPOL pour dériver une clé de session à partir du mot de passe partagé, sans jamais le transmettre en clair. En le capturant, on peut ensuite tester hors-ligne si un mot de passe de dictionnaire aboutit à la même clé.

Si un client est déjà visible comme associé à l'AP (dans `airodump-ng`), on peut forcer sa reconnexion avec une désauthentification ciblée :

```bash
sudo aireplay-ng --deauth 5 -a <BSSID_de_mon_AP> -c <MAC_du_client> <interface>
```

- `--deauth 5` : envoie 5 salves de trames de deauth.
- `-a` : BSSID de l'AP à usurper.
- `-c` : adresse MAC du client ciblé (omis = deauth broadcast, touche tous les clients).

Pendant ce temps, `airodump-ng` (étape 6) doit tourner pour capturer la reconnexion. Un `WPA handshake: <BSSID>` apparaît dans son affichage une fois capturé.

!!! note "Cas du WPA3-SAE et de la protection PMF (802.11w)"
    Sur un AP annonçant `WPA3 WPA2 SAE PSK` avec la capacité **MFP (Management Frame Protection)**, un client ayant négocié PMF **ignore les trames de deauth non protégées** — 0 ACK reçu, pas de déconnexion forcée possible. C'est une protection normale, pas un dysfonctionnement.

    Pour vérifier si le PMF est actif :

    ```bash
    # Repasser brièvement en mode managed
    sudo ip link set <interface> down
    sudo iw dev <interface> set type managed
    sudo ip link set <interface> up

    sudo iw dev <interface> scan | grep -A 10 "SSID: <mon_reseau>" | grep -A5 RSN
    # Chercher "MFP-required" (PMF obligatoire, deauth impossible)
    # vs "MFP-capable" (PMF optionnel, dépend du client)
    ```

    `MFP-required` pour tous les clients est un bon signe d'audit : le réseau résiste par conception au deauth attack. Un vieux client WPA2-only peut cependant rester vulnérable même si l'AP est `MFP-capable`.

### Étape 8 : Vérifier que le handshake est capturé

```bash
aircrack-ng capture-01.cap
```

Affiche `WPA (1 handshake)` en face de l'ESSID si la capture a réussi, `WPA (0 handshake)` sinon (retenter le deauth, ou attendre une reconnexion naturelle : redémarrage d'un appareil, retour de veille Wi-Fi...).

### Étape 9 : Tester la robustesse du mot de passe par dictionnaire

```bash
sudo apt install wordlists
sudo gunzip -k /usr/share/wordlists/rockyou.txt.gz

aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap
```

Un mot de passe trouvé par cette méthode doit être changé pour quelque chose de plus long, complexe et non standard. Un mot de passe non cassé par `rockyou.txt` n'est pas pour autant garanti "fort" — ce n'est qu'un test contre une wordlist connue.

### Étape 10 : Revenir en mode normal

```bash
sudo ip link set <interface> down
sudo iw dev <interface> set type managed
sudo ip link set <interface> up
sudo nmcli device set <interface> managed yes
```

## Glossaire

Mode moniteur
:   Mode de fonctionnement d'une carte Wi-Fi dans lequel elle capture toutes les trames radio d'un canal, sans être associée à un AP particulier.

Injection de paquets
:   Capacité d'une carte Wi-Fi à émettre des trames 802.11 forgées manuellement, indépendamment de la pile réseau normale (ex : trame de deauth).

4-way handshake (WPA/WPA2)
:   Échange de 4 messages EAPOL entre l'AP et le client permettant de dériver une clé de session à partir du mot de passe partagé, sans le transmettre en clair.

SAE / Dragonfly handshake (WPA3)
:   Mécanisme d'authentification de WPA3 qui remplace le 4-way handshake classique. Résiste par conception aux attaques par dictionnaire hors-ligne, car chaque tentative de mot de passe nécessite une interaction en direct avec l'AP.

PMF / 802.11w
:   Protection des trames de gestion (deauth, disassoc...) par chiffrement, empêchant leur falsification par un tiers. Rend les attaques de deauth classiques inopérantes contre les clients qui l'ont négocié.

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `sudo nmcli device set <iface> managed no` | Retire l'interface de la gestion automatique de NetworkManager. |
| `sudo iw dev <iface> set type monitor` | Passe l'interface en mode moniteur (à faire interface `down`). |
| `sudo airodump-ng <iface>` | Scanne tous les réseaux et stations visibles. |
| `sudo airodump-ng -c <canal> --bssid <BSSID> -w capture <iface>` | Capture le trafic d'un AP précis dans un fichier `.cap`. |
| `sudo aireplay-ng --test <iface>` | Teste la capacité d'injection de la carte. |
| `sudo aireplay-ng --deauth 5 -a <BSSID> -c <MAC_client> <iface>` | Force la déconnexion/reconnexion d'un client pour capturer le handshake. |
| `aircrack-ng capture-01.cap` | Vérifie la présence d'un handshake dans une capture. |
| `aircrack-ng -w <wordlist> capture-01.cap` | Teste un mot de passe par dictionnaire contre un handshake capturé. |

## Ressources

- [Documentation officielle Aircrack-ng](https://www.aircrack-ng.org/documentation.html) — Référence complète de la suite d'outils.
- [Documentation du driver `rtw88` (kernel.org)](https://wireless.wiki.kernel.org/) — Compatibilité mode moniteur/injection selon les chipsets Realtek.
- [SecNumacadémie (ANSSI)](https://secnumacademie.gouv.fr/) — Sensibilisation et cours de sécurité, y compris sur les réseaux sans fil.
