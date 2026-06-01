---
title: "Mettre en place un VPN WireGuard simple entre deux machines Ubuntu"
date: 2026-06-01
author: Nicolas BODAINE
tags:
  - ubuntu
  - wireguard
  - vpn
  - reseau
  - chiffrement
difficulty: débutant
os: Ubuntu Server 24.04
status: publié
---

# Mettre en place un VPN WireGuard simple entre deux machines Ubuntu

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour créer un tunnel **WireGuard** simple entre **deux machines Ubuntu**. Nous allons installer WireGuard, générer une paire de clés sur chaque machine, créer les fichiers `wg0.conf`, ouvrir le port UDP nécessaire, démarrer le tunnel et vérifier que les deux hôtes communiquent bien via leurs adresses VPN.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu Server 24.04 |
| Dernière mise à jour | 2026-06-01 |

## Contexte

**WireGuard** est un VPN moderne, léger et rapide.
Il permet de créer un **tunnel chiffré** entre deux machines pour faire circuler du trafic réseau de manière plus sûre.

Dans un TP ou un lab, c'est un excellent sujet pour apprendre :

- la notion de **paire de clés** ;
- le rôle d'un **endpoint** réseau ;
- l'ouverture d'un **port UDP** ;
- la différence entre l'**adresse réseau normale** d'une machine et son **adresse VPN** ;
- la vérification d'un service réseau avec des commandes simples.

Dans ce tutoriel, nous restons volontairement sur un scénario **simple et reproductible** :

- **deux machines Ubuntu** ;
- **un tunnel point à point** ;
- **pas de routage de sous-réseaux complets** ;
- **pas d'IP forwarding** à activer dans ce premier TP.

L'objectif est de faire communiquer deux hôtes avec des adresses VPN privées, par exemple `10.10.10.1` et `10.10.10.2`.

!!! note "Ce que ce tutoriel ne couvre pas"
    Nous ne configurons pas ici un VPN **site-à-site** entre deux LAN complets.
    Pour ce premier niveau, nous créons simplement un tunnel entre **deux machines**.
    C'est plus facile à comprendre avant d'ajouter du routage, du NAT ou plusieurs pairs.

## Prérequis

- Deux machines sous **Ubuntu Server 24.04**
- Un compte avec les droits `sudo` sur chaque machine
- Les deux machines doivent pouvoir se joindre sur leur réseau principal
- Un port UDP disponible, par défaut **`51820/udp`**
- Si un pare-feu est actif, l'autorisation du port **`51820/udp`**

### Topologie d'exemple utilisée dans ce tutoriel

| Rôle | Nom | Adresse réseau principale | Adresse VPN WireGuard |
|------|-----|---------------------------|-----------------------|
| Machine 1 | `srv-vpn-01` | `192.168.56.21` | `10.10.10.1/24` |
| Machine 2 | `srv-vpn-02` | `192.168.56.22` | `10.10.10.2/24` |

!!! tip "Adaptez les valeurs à votre lab"
    Si vos machines n'ont pas ces adresses, remplacez simplement les IP d'exemple par les vôtres.
    Le plus important est de bien distinguer :
    
    - l'**IP réelle** de la machine sur le réseau ;
    - l'**IP WireGuard** utilisée à l'intérieur du tunnel.

## Procédure

### Étape 1 : identifier les adresses IP des deux machines

Sur chaque machine, commencez par vérifier l'adresse réseau déjà utilisée par Ubuntu.

```bash
hostname
ip -br addr
ip route
```

Exemple de lecture possible :

```text
srv-vpn-01
lo               UNKNOWN        127.0.0.1/8 ::1/128
ens18            UP             192.168.56.21/24
```

et sur l'autre machine :

```text
srv-vpn-02
lo               UNKNOWN        127.0.0.1/8 ::1/128
ens18            UP             192.168.56.22/24
```

Ces adresses seront utilisées comme **endpoints** dans la configuration WireGuard.

!!! warning "Si les machines ne se voient déjà pas"
    Si vous ne pouvez pas joindre `192.168.56.21` depuis `192.168.56.22` ou l'inverse, le tunnel WireGuard ne pourra pas fonctionner.
    Vérifiez d'abord le réseau de base, la VM, le VLAN, le NAT ou le pare-feu.

### Étape 2 : installer WireGuard sur les deux machines

Exécutez les commandes suivantes sur **les deux machines**.

=== "srv-vpn-01"

    ```bash
    sudo apt update
    sudo apt install -y wireguard
    ```

=== "srv-vpn-02"

    ```bash
    sudo apt update
    sudo apt install -y wireguard
    ```

Vous pouvez vérifier que les outils sont bien présents :

```bash
wg --version
wg-quick --version
```

### Étape 3 : générer une paire de clés sur chaque machine

Chaque machine doit avoir :

- une **clé privée** à garder secrète ;
- une **clé publique** que l'on peut partager à l'autre pair.

Créez les clés sur **chaque machine**.

=== "srv-vpn-01"

    ```bash
    sudo install -d -m 700 /etc/wireguard
    wg genkey | sudo tee /etc/wireguard/private.key > /dev/null
    sudo chmod 600 /etc/wireguard/private.key
    sudo sh -c 'wg pubkey < /etc/wireguard/private.key > /etc/wireguard/public.key'
    sudo chmod 644 /etc/wireguard/public.key
    ```

=== "srv-vpn-02"

    ```bash
    sudo install -d -m 700 /etc/wireguard
    wg genkey | sudo tee /etc/wireguard/private.key > /dev/null
    sudo chmod 600 /etc/wireguard/private.key
    sudo sh -c 'wg pubkey < /etc/wireguard/private.key > /etc/wireguard/public.key'
    sudo chmod 644 /etc/wireguard/public.key
    ```

Affichez ensuite la **clé publique** de chaque machine :

=== "srv-vpn-01"

    ```bash
    sudo cat /etc/wireguard/public.key
    ```

=== "srv-vpn-02"

    ```bash
    sudo cat /etc/wireguard/public.key
    ```

Conservez ces deux valeurs :

- la clé publique de `srv-vpn-01` sera copiée dans la configuration de `srv-vpn-02` ;
- la clé publique de `srv-vpn-02` sera copiée dans la configuration de `srv-vpn-01`.

!!! danger "Ne partagez jamais la clé privée"
    Le fichier `/etc/wireguard/private.key` doit rester **strictement local** à sa machine.
    Seule la **clé publique** est échangée.

### Étape 4 : récupérer la clé privée locale pour préparer la configuration

WireGuard attend la **clé privée locale** dans le fichier de configuration `wg0.conf`.
Affichez-la sur chaque machine pour la recopier dans le bon fichier.

=== "srv-vpn-01"

    ```bash
    sudo cat /etc/wireguard/private.key
    ```

=== "srv-vpn-02"

    ```bash
    sudo cat /etc/wireguard/private.key
    ```

!!! warning "Attention aux inversions"
    Dans `wg0.conf` d'une machine :
    
    - `PrivateKey` = **clé privée de la machine locale** ;
    - `PublicKey` dans le bloc `[Peer]` = **clé publique de la machine distante**.

### Étape 5 : créer le fichier `wg0.conf` sur la machine 1

Sur `srv-vpn-01`, créez le fichier suivant :

```bash
sudo nano /etc/wireguard/wg0.conf
```

Contenu :

```ini
[Interface]
Address = 10.10.10.1/24
ListenPort = 51820
PrivateKey = <CLE_PRIVEE_DE_SRV_VPN_01>

[Peer]
PublicKey = <CLE_PUBLIQUE_DE_SRV_VPN_02>
Endpoint = 192.168.56.22:51820
AllowedIPs = 10.10.10.2/32
```

Appliquez ensuite des permissions strictes :

```bash
sudo chmod 600 /etc/wireguard/wg0.conf
```

### Étape 6 : créer le fichier `wg0.conf` sur la machine 2

Sur `srv-vpn-02`, créez le fichier suivant :

```bash
sudo nano /etc/wireguard/wg0.conf
```

Contenu :

```ini
[Interface]
Address = 10.10.10.2/24
ListenPort = 51820
PrivateKey = <CLE_PRIVEE_DE_SRV_VPN_02>

[Peer]
PublicKey = <CLE_PUBLIQUE_DE_SRV_VPN_01>
Endpoint = 192.168.56.21:51820
AllowedIPs = 10.10.10.1/32
```

Appliquez ensuite des permissions strictes :

```bash
sudo chmod 600 /etc/wireguard/wg0.conf
```

### Comprendre les paramètres importants

- `Address` : adresse IP que la machine utilisera **dans le tunnel VPN** ;
- `ListenPort` : port UDP d'écoute de WireGuard ;
- `PrivateKey` : clé privée **locale** ;
- `PublicKey` : clé publique **du pair distant** ;
- `Endpoint` : adresse IP ou nom DNS joignable de la machine distante, avec son port UDP ;
- `AllowedIPs` : adresses que l'on enverra dans le tunnel pour ce pair.

Dans notre cas très simple :

- `srv-vpn-01` doit joindre `10.10.10.2` à travers le tunnel ;
- `srv-vpn-02` doit joindre `10.10.10.1` à travers le tunnel.

C'est pourquoi nous utilisons respectivement `10.10.10.2/32` et `10.10.10.1/32` dans `AllowedIPs`.

!!! note "Pourquoi ne pas mettre tout un sous-réseau distant ?"
    C'est possible dans un scénario plus avancé.
    Mais pour un premier TP entre deux machines, limiter `AllowedIPs` à l'IP VPN exacte du pair évite beaucoup de confusion.

### Étape 7 : ouvrir le port UDP 51820 si un pare-feu est actif

Si vous utilisez **UFW** sur une ou deux machines, autorisez le port WireGuard.

Vérifiez d'abord l'état du pare-feu :

```bash
sudo ufw status verbose
```

Si UFW est actif, ajoutez la règle sur **chaque machine** :

```bash
sudo ufw allow 51820/udp
```

Vérifiez ensuite :

```bash
sudo ufw status numbered
```

!!! tip "Si UFW est inactif"
    Si `Status: inactive` s'affiche, vous pouvez passer cette étape.
    L'important est que le trafic **UDP 51820** ne soit pas bloqué par le système, l'hyperviseur, le routeur ou un firewall intermédiaire.

### Étape 8 : démarrer l'interface WireGuard sur les deux machines

Démarrez d'abord l'interface sur `srv-vpn-01`, puis sur `srv-vpn-02`.

=== "srv-vpn-01"

    ```bash
    sudo wg-quick up wg0
    ```

=== "srv-vpn-02"

    ```bash
    sudo wg-quick up wg0
    ```

Si tout se passe bien, WireGuard crée l'interface `wg0` et applique la configuration.

Vous pouvez vérifier la présence de l'interface :

```bash
ip addr show wg0
```

Exemple de résultat attendu sur `srv-vpn-01` :

```text
wg0: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1420 qdisc noqueue state UNKNOWN group default
    inet 10.10.10.1/24 scope global wg0
```

### Étape 9 : tester le tunnel et le handshake

Commencez par lancer un ping à travers le VPN.

=== "Depuis srv-vpn-01 vers srv-vpn-02"

    ```bash
    ping -c 4 10.10.10.2
    ```

=== "Depuis srv-vpn-02 vers srv-vpn-01"

    ```bash
    ping -c 4 10.10.10.1
    ```

Ensuite, affichez l'état WireGuard :

```bash
sudo wg show
```

Exemple de sortie attendue :

```text
interface: wg0
  public key: ...
  private key: (hidden)
  listening port: 51820

peer: ...
  endpoint: 192.168.56.22:51820
  allowed ips: 10.10.10.2/32
  latest handshake: 1 minute, 20 seconds ago
  transfer: 1.36 KiB received, 1.52 KiB sent
```

!!! success "Ce que vous devez observer"
    Après le premier échange réseau, la commande `wg show` doit afficher un **latest handshake** récent et des compteurs `transfer` non nuls.
    Si vous ne voyez aucun handshake, le problème vient souvent d'une clé erronée, d'un endpoint incorrect ou d'un port UDP bloqué.

### Étape 10 : activer WireGuard au démarrage

Quand votre test est concluant, activez le service sur les deux machines :

```bash
sudo systemctl enable wg-quick@wg0
```

Vous pouvez contrôler l'état du service :

```bash
sudo systemctl status wg-quick@wg0 --no-pager
```

Pour redémarrer proprement l'interface plus tard :

```bash
sudo systemctl restart wg-quick@wg0
```

Pour l'arrêter :

```bash
sudo wg-quick down wg0
```

### Étape 11 : ajouter `PersistentKeepalive` si une machine est derrière NAT

Dans certains labs, une machine est derrière une box, un routeur NAT ou un firewall qui oublie la session UDP après une période d'inactivité.

Dans ce cas, ajoutez sur le pair qui initie ou qui doit rester joignable une ligne comme :

```ini
PersistentKeepalive = 25
```

Exemple sur `srv-vpn-02` :

```ini
[Peer]
PublicKey = <CLE_PUBLIQUE_DE_SRV_VPN_01>
Endpoint = 192.168.56.21:51820
AllowedIPs = 10.10.10.1/32
PersistentKeepalive = 25
```

Après modification :

```bash
sudo systemctl restart wg-quick@wg0
```

!!! note "Quand utiliser cette option ?"
    La documentation officielle WireGuard indique que `PersistentKeepalive` est surtout utile derrière un NAT ou un firewall pour maintenir la connectivité entrante après une longue inactivité.
    Si votre tunnel fonctionne parfaitement sans cette option, ne l'ajoutez pas par réflexe.

## Vérification

Pour valider votre TP, contrôlez les points suivants.

### 1. L'interface `wg0` existe

```bash
ip addr show wg0
```

### 2. WireGuard écoute sur le port attendu

```bash
sudo ss -lunp | grep 51820
```

### 3. Le pair apparaît dans `wg show`

```bash
sudo wg show
```

### 4. Le ping via les IP VPN répond

=== "Depuis srv-vpn-01"

    ```bash
    ping -c 2 10.10.10.2
    ```

=== "Depuis srv-vpn-02"

    ```bash
    ping -c 2 10.10.10.1
    ```

!!! success "Résultat attendu"
    Les deux machines doivent se répondre sur leurs **adresses VPN** et `wg show` doit afficher un **handshake récent**.

## Problèmes fréquents

### 1. `wg show` n'affiche aucun handshake

Vérifiez en priorité :

- l'adresse `Endpoint` ;
- la bonne **clé publique du pair distant** ;
- le port `51820/udp` ouvert ;
- la présence d'un firewall sur l'hôte, l'hyperviseur ou le réseau.

Commandes utiles :

```bash
sudo wg show
sudo ss -lunp | grep 51820
sudo ufw status verbose
```

### 2. `ping` ne passe pas mais l'interface existe

Vérifiez les `AllowedIPs` des deux côtés.
Dans ce TP, elles doivent pointer vers l'**IP VPN du pair**, pas vers l'IP physique du serveur.

### 3. Le service redémarre mal après modification

Après une erreur dans `wg0.conf`, regardez les logs :

```bash
sudo systemctl status wg-quick@wg0 --no-pager
sudo journalctl -u wg-quick@wg0 -n 50 --no-pager
```

### 4. Une machine est derrière NAT

Si le tunnel fonctionne au début puis plus après un certain temps d'inactivité, essayez d'ajouter :

```ini
PersistentKeepalive = 25
```

sur le pair concerné, puis redémarrez l'interface.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `sudo apt install -y wireguard` | Installer WireGuard sur Ubuntu |
| `wg genkey` | Générer une clé privée |
| `wg pubkey` | Déduire la clé publique depuis la clé privée |
| `sudo wg-quick up wg0` | Monter l'interface `wg0` |
| `sudo wg-quick down wg0` | Arrêter l'interface `wg0` |
| `sudo wg show` | Afficher l'état du tunnel et des pairs |
| `ip addr show wg0` | Vérifier l'interface VPN |
| `sudo systemctl enable wg-quick@wg0` | Démarrer WireGuard automatiquement au boot |
| `sudo ss -lunp | grep 51820` | Vérifier l'écoute UDP du service |
| `sudo ufw allow 51820/udp` | Autoriser le port WireGuard dans UFW |

## Glossaire

`Peer`
:   Pair WireGuard, c'est-à-dire la machine distante avec laquelle on établit le tunnel.

`Endpoint`
:   Adresse IP ou nom DNS joignable de la machine distante, avec son port UDP.

`AllowedIPs`
:   Liste des adresses ou réseaux envoyés dans le tunnel pour un pair donné.

`Handshake`
:   Échange qui permet de confirmer qu'une communication WireGuard a bien eu lieu récemment entre les deux pairs.

`PersistentKeepalive`
:   Envoi périodique minimal permettant de garder une connectivité utile derrière certains NAT ou firewalls.

## Ressources

- [WireGuard Quick Start](https://www.wireguard.com/quickstart/) — Documentation officielle WireGuard pour démarrer rapidement
- [Ubuntu Server documentation — WireGuard VPN](https://documentation.ubuntu.com/server/how-to/wireguard-vpn/) — Vue d'ensemble officielle Ubuntu Server
- [Ubuntu Server documentation — WireGuard VPN peer-to-site](https://documentation.ubuntu.com/server/how-to/wireguard-vpn/peer-to-site/) — Explications officielles sur un scénario simple de connexion entre pairs
- [Ubuntu Server documentation — Common tasks in WireGuard VPN](https://documentation.ubuntu.com/server/how-to/wireguard-vpn/common-tasks/) — Démarrage automatique et tâches courantes
- [Ubuntu Server documentation — Security tips for WireGuard VPN](https://documentation.ubuntu.com/server/how-to/wireguard-vpn/security-tips/) — Bonnes pratiques de sécurité
- [Ubuntu Server documentation — Troubleshooting WireGuard VPN](https://documentation.ubuntu.com/server/how-to/wireguard-vpn/troubleshooting/) — Checklist officielle de dépannage
- [Manpage `wg(8)` pour Ubuntu 24.04](https://manpages.ubuntu.com/manpages/noble/en/man8/wg.8.html) — Référence de la commande `wg`
- [Manpage `wg-quick(8)` pour Ubuntu 24.04](https://manpages.ubuntu.com/manpages/noble/en/man8/wg-quick.8.html) — Référence de `wg-quick`
