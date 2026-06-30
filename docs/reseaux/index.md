---
icon: material/network
description: Configuration réseau, routage, VPN, et services de proxy sous Linux.
---

# Réseaux

Configuration réseau, routage, VPN, et services de proxy sous Linux.

## Services d'Infrastructure

- [Bloquer les requêtes malveillantes et publicités avec Pi-hole](installer-configurer-pi-hole-reseau-local.md) — Déployer un trou noir DNS pour sécuriser votre réseau local.
- [Mettre en place un serveur DHCP local avec Kea sur Ubuntu](installer-configurer-serveur-dhcp-kea-ubuntu.md) — Remplacer isc-dhcp-server par le serveur moderne de l'ISC pour gérer vos adresses IP locales.

## Routage & Pare-feu

- [Configurer le NAT et le routage pour transformer un serveur Linux en routeur avec nftables](configurer-nat-routage-serveur-linux-nftables.md) — Transformer un serveur Linux standard en véritable routeur pour votre réseau local (LAN).

## Configuration IP & DNS

- [Configurer des VLANs (802.1q) sur un serveur Linux avec Netplan](configurer-vlans-8021q-netplan-linux.md) — Connecter et partitionner une interface physique sur un lien trunk.
- [Configurer une adresse IP statique avec Netplan sur Ubuntu Server 24.04](configurer-ip-statique-netplan-ubuntu-server.md) — Fixer l'adresse de son serveur via le nouveau standard YAML d'Ubuntu.
- [Configurer une agrégation de liens (Bonding/LACP) avec Netplan sous Ubuntu](configurer-agregation-liens-bonding-lacp-netplan-ubuntu.md) — Regrouper plusieurs interfaces réseau pour de la redondance et de la bande passante.
- [Diagnostiquer une panne DNS avec `dig`, `host` et `resolvectl` sur Ubuntu](diagnostiquer-panne-dns-dig-host-resolvectl-ubuntu.md) — Trouver d'où vient le problème de résolution des noms de domaine.

## Sécurité & Accès Distant

- [Créer des tunnels sécurisés avec la redirection de ports SSH](creer-tunnels-securises-redirection-ports-ssh.md) — Créer des tunnels locaux, distants et dynamiques (SOCKS proxy) pour sécuriser des flux ou contourner un NAT.
- [Mettre en place un VPN WireGuard simple entre deux machines Ubuntu](mettre-en-place-vpn-wireguard-simple-entre-deux-machines-ubuntu.md) — Créer un tunnel chiffré, rapide et moderne entre deux points du réseau.

## Diagnostic & Outils

- [Analyser le trafic réseau avec Wireshark : Capturer et filtrer les paquets](analyser-trafic-reseau-wireshark-capturer-filtrer.md) — Comprendre ce qui transite sur votre réseau grâce au sniffer le plus populaire.
- [Diagnostiquer les problèmes de routage et de latence réseau avec mtr](diagnostiquer-routage-latence-reseau-mtr.md) — Combiner les fonctions de ping et traceroute pour analyser les pertes de paquets en temps réel.
- [Mesurer la bande passante réelle entre deux machines avec iperf3](mesurer-bande-passante-iperf3.md) — Outil indispensable pour tester le débit maximal et la fiabilité de vos liens réseau.

## Proxy & Web

- [Mettre en place un Reverse Proxy (Proxy Inverse) avec Nginx](mettre-en-place-reverse-proxy-nginx-ubuntu.md) — Exposer plusieurs services locaux sur le port 80 sous un même nom de domaine.
