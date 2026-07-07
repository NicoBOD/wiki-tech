---
title: Configurer le NAT et le routage pour transformer un serveur Linux en routeur avec nftables
date: 2026-06-17
author: Nicolas BODAINE
tags:
  - reseau
  - linux
  - nftables
  - routage
  - nat
difficulty: intermédiaire
os: Linux (Debian/Ubuntu)
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Configurer le NAT et le routage pour transformer un serveur Linux en routeur avec nftables

!!! abstract "Résumé"
    Ce tutoriel explique pas-à-pas comment transformer une machine Linux standard en véritable routeur pour votre réseau local (LAN). En activant le transfert de paquets (IP forwarding) et en configurant la traduction d'adresses (NAT) avec **nftables** (le remplaçant moderne d'iptables), vous permettrez à vos équipements internes d'accéder à Internet à travers cette machine.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux (Debian 12 / Ubuntu 24.04) |
| Dernière mise à jour | 2026-06-17 |

## Contexte

Il est fréquent dans un laboratoire de tests (homelab) ou une infrastructure cloud de vouloir isoler un réseau privé tout en lui donnant un accès sortant vers Internet. Une machine Linux possédant deux interfaces réseau (une publique et une privée) peut parfaitement remplir le rôle de passerelle et de pare-feu (routeur NAT), remplaçant ainsi un équipement matériel dédié ou une solution packagée.

## Prérequis

- Une machine Linux avec **deux interfaces réseau** :
    - `eth0` (interface publique connectée à Internet/WAN).
    - `eth1` (interface privée connectée au réseau local/LAN).
- Les droits d'administration (`root` ou `sudo`).
- L'outil `nftables` installé (paquet `nftables`).

## Procédure

### Étape 1 : Activer l'IP forwarding (routage)

Par défaut, le noyau Linux refuse de transférer des paquets d'une interface réseau à une autre par mesure de sécurité. Il faut l'autoriser explicitement.

Éditez le fichier de configuration `sysctl` :

```bash
sudo nano /etc/sysctl.d/99-routing.conf
```

Ajoutez-y la ligne suivante pour le trafic IPv4 :

```ini
net.ipv4.ip_forward=1
```

Appliquez immédiatement le changement sans redémarrer :

```bash
sudo sysctl -p /etc/sysctl.d/99-routing.conf
```

### Étape 2 : Installer et préparer nftables

Si ce n'est pas déjà fait, installez le paquet `nftables`. Sur les distributions récentes, il remplace `iptables`.

```bash
sudo apt update
sudo apt install nftables
```

Assurez-vous que le service démarrera automatiquement :

```bash
sudo systemctl enable nftables
```

### Étape 3 : Configurer les règles NAT avec nftables

Nous allons créer un ensemble de règles minimaliste pour autoriser le trafic sortant et effectuer du Source NAT (SNAT/Masquerade), pour que les paquets venant du LAN prennent l'IP publique du routeur en sortant vers Internet.

Éditez le fichier de configuration principal `/etc/nftables.conf` :

```bash
sudo nano /etc/nftables.conf
```

Remplacez son contenu par la configuration suivante (en ajustant `eth0` et `eth1` aux noms de vos interfaces réseau) :

```nftables title="/etc/nftables.conf"
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy accept;
        
        # Accepter le trafic de la boucle locale
        iif "lo" accept
        
        # Accepter le trafic lié aux connexions établies
        ct state established,related accept
    }

    chain forward {
        type filter hook forward priority 0; policy drop;

        # Accepter le trafic sortant depuis le LAN vers le WAN (eth0)
        iifname "eth1" oifname "eth0" accept
        
        # Accepter les retours des connexions déjà établies
        iifname "eth0" oifname "eth1" ct state established,related accept
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}

table ip nat {
    chain postrouting {
        type nat hook postrouting priority 100; policy accept;
        
        # Masquerade : cacher le réseau local derrière l'IP publique de l'interface WAN
        oifname "eth0" masquerade
    }
}
```

!!! warning "Sécurité"
    Cette configuration `filter` est basique. En production, il est recommandé de restreindre la chaîne `input` (hook input) pour bloquer les accès non sollicités sur l'interface publique (WAN) en changeant la `policy drop;` et en autorisant explicitement certains ports (ex: SSH).

### Étape 4 : Appliquer les règles

Chargez la nouvelle configuration nftables :

```bash
sudo nft -f /etc/nftables.conf
```

Vérifiez que les règles sont bien en place :

```bash
sudo nft list ruleset
```

Démarrez (ou redémarrez) le service nftables :

```bash
sudo systemctl restart nftables
```

## Vérification

Sur une machine cliente située dans votre réseau local (LAN), configurez sa passerelle par défaut pour pointer vers l'adresse IP privée de votre nouveau routeur Linux.

Ensuite, depuis ce client, testez la connectivité Internet :

```bash
ping 8.8.8.8
```

!!! success "Résultat attendu"
    Le client doit recevoir des réponses au ping, prouvant que la machine Linux a correctement routé et "NATé" le trafic vers Internet.

## Ressources

- [Documentation officielle nftables](https://wiki.nftables.org/) — Wiki complet sur la syntaxe et les cas d'usage.
- [Wiki Arch Linux : nftables](https://wiki.archlinux.org/title/Nftables) — Excellente ressource vulgarisée sur le filtrage réseau (page en anglais, la version française a été retirée du wiki).