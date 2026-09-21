---
title: "NordVPN — Perte de connexion Ethernet après redémarrage de la box Internet (PC sur onduleur)"
date: 2026-09-21
author: Nicolas BODAINE
tags:
  - reseau
  - vpn
  - nordvpn
  - openvpn
  - networkmanager
  - ubuntu
  - systemd
  - nftables
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# NordVPN — Perte de connexion Ethernet après redémarrage de la box Internet (PC sur onduleur)

!!! abstract "Résumé"
    Sur un ordinateur sous Ubuntu raccordé à un **onduleur** et relié en **Ethernet (RJ45)** à une box Internet non secourue, une coupure de courant provoque l'extinction puis le redémarrage de la box. Au retour du courant, la carte Ethernet se reconnecte immédiatement et obtient bien une adresse IP locale par DHCP, mais **l'accès à Internet demeure totalement bloqué**. La connexion ne se rétablissait qu'en allumant manuellement le Wi-Fi.

    La cause racine provient de **NordVPN** en mode **OpenVPN avec Obfuscation**. Lors du redémarrage de la box, ses ports Ethernet locaux s'activent plusieurs dizaines de secondes avant que sa synchronisation Internet WAN (fibre ou ADSL) ne soit effective. OpenVPN subit alors un échec de négociation TLS et déclenche un redémarrage logiciel interne (`SIGUSR1`) qui se fige indéfiniment dans l'attente d'identifiants (`AUTH`). Pendant ce blocage, les règles de filtrage **nftables** de NordVPN maintiennent une politique de rejet strict (`policy drop`) et bloquent les requêtes DNS locales, isolant totalement la machine. L'activation manuelle du Wi-Fi générait un événement réseau forçant le démon à détruire et recréer le tunnel de zéro.

    La solution met en place un script de reprise automatique **NetworkManager Dispatcher** non intrusif : il surveille la remontée du câble Ethernet, s'assure de la présence de la box sur le réseau local, accorde un délai de grâce pour la reconnexion naturelle et, si le blocage persiste, redémarre proprement le démon NordVPN. En complément, la configuration **IPv6** de NetworkManager est harmonisée pour supprimer les erreurs en boucle dans les journaux système.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 LTS Desktop (GNOME) |
| Composants clés | NetworkManager, OpenVPN 2.6, NordVPN 5.4, nftables, systemd |
| Architecture | PC fixe sur onduleur, Box Internet reliée en RJ45 |
| Dernière mise à jour | 2026-09-21 |

## Contexte

Dans une installation informatique domestique ou professionnelle, il est fréquent de protéger l'unité centrale par un onduleur (UPS) pour parer aux coupures d'électricité. La box Internet (Freebox, Livebox, SFR Box, Bbox, etc.) est quant à elle souvent branchée sur une prise murale standard.

Lors d'un incident électrique :
1. Le PC reste alimenté et continue de tourner grâce à la batterie de l'onduleur.
2. La box Internet s'éteint brutalement.
3. Au rétablissement du secteur, la box redémarre électriquement.
4. L'ordinateur constate le retour du signal physique Ethernet et récupère sa configuration IP locale via DHCP.
5. Pourtant, la navigation web, le ping externe et la résolution DNS restent inopérants.

Sur cette machine, le protocole **OpenVPN** associé à la fonctionnalité **Obfuscate** (obfuscation du trafic pour masquer l'usage d'un VPN face aux pare-feux et mécanismes DPI) est strictement requis, ce qui exclut l'usage de NordLynx (WireGuard). Le Wi-Fi étant habituellement désactivé, l'objectif est d'obtenir une reconnexion Ethernet 100 % autonome et résiliente, sans aucune manipulation manuelle.

---

## Comprendre la chaîne réseau et l'origine du blocage

Pour appréhender ce dysfonctionnement, il convient d'analyser les différentes couches logicielles impliquées et la chronologie de redémarrage des équipements :

```text
[ Box Internet ] (Reboot électrique)
  ├─ Switch LAN (RJ45) ─────────────> Actif en ~10-15s (Lien UP + DHCP OK)
  └─ Synchronisation WAN (Fibre/DSL) ─> Actif en ~60-120s (Internet réel)
          │
[ PC Ubuntu ]
  ├─ Pilote Ethernet (e1000e) ───────> Détecte NIC Link Up (ex: enp3s0)
  ├─ NetworkManager ─────────────────> Récupère IP locale (ex: 192.168.1.50)
  └─ NordVPN (OpenVPN)
       ├─ Tente négociation TLS ────> Échoue (WAN pas encore prêt)
       ├─ Déclenche SIGUSR1 ─────────> Fige OpenVPN en état AUTH
       └─ nftables (inet nordvpn) ───> Bloque TOUT le trafic sortant (Policy DROP)
```

!!! note "Notions fondamentales : qui fait quoi ?"
    **Switch LAN vs Synchronisation WAN** : Une box Internet combine plusieurs rôles. À l'allumage, son commutateur réseau local (switch Ethernet) et son serveur DHCP démarrent presque instantanément. À l'inverse, l'alignement optique (fibre GPON) ou la synchronisation xDSL, suivi de l'authentification réseau opérateur (PPPoE / IPoE), demande une à deux minutes supplémentaires.

    **OpenVPN et signal SIGUSR1** : Dans l'architecture OpenVPN, le signal Unix `SIGUSR1` correspond à un « soft restart » (redémarrage doux sans libérer la mémoire). Le processus ne quitte pas le système d'exploitation, mais réinitialise sa machine à états interne. Lors de cette transition, OpenVPN redemande ses identifiants de session (`AUTH`) via son socket d'administration UNIX.

    **Le bug d'authentification du démon NordVPN** : Le démon en arrière-plan `nordvpnd` n'injecte les identifiants utilisateur qu'à l'initialisation initiale d'un nouveau processus binaire. Lorsqu'OpenVPN effectue un redémarrage interne sur `SIGUSR1`, `nordvpnd` n'intercepte pas la demande d'authentification. OpenVPN se retrouve ainsi en attente passive infinie (`could not read Auth username/password`), bloquant le tunnel `nordtun`.

    **Le piège du pare-feu nftables** : Pour empêcher les fuites de données hors VPN, NordVPN configure des règles de pare-feu avancées dans la table `inet nordvpn`. Sa chaîne `output` applique une politique par défaut `policy drop`. Seuls les paquets marqués spécifiquement par le socket VPN (`0xe1f1`) ou à destination du tunnel `nordtun` sont autorisés, tandis que les requêtes DNS locales (port 53 vers la box) sont expressément rejetées. Si le tunnel ne remonte pas, l'ensemble de la machine est plongé dans un trou noir réseau.

    **Pourquoi l'activation du Wi-Fi débloquait la situation** : Dès que l'interface Wi-Fi (`wlp2s0`) devenait active, le moniteur d'interfaces de NordVPN détectait un changement d'état (`monitored interfaces changed`). Cet événement interne forçait `nordvpnd` à exécuter sa routine `refresh VPN`, qui tue le processus OpenVPN figé avec un signal `SIGINT`, purge les règles et relance un binaire propre avec ses identifiants.

---

## Diagnostic pas-à-pas

Lors de l'incident, plusieurs commandes de diagnostic en lecture seule permettent d'identifier précisément le phénomène.

*(Dans les exemples ci-dessous, nous utilisons l'interface Ethernet `enp3s0`, le sous-réseau `192.168.1.0/24` et la passerelle `192.168.1.1` comme valeurs d'exemple).*

### 1. Constat du lien physique et de la configuration IP

La commande `ip route` et `nmcli device status` démontre que NetworkManager a correctement fait son travail :

```bash
nmcli device status
ip route
```

```text
DEVICE     TYPE      STATE     CONNECTION 
enp3s0     ethernet  connecté  enp3s0  

default via 192.168.1.1 dev enp3s0 proto dhcp src 192.168.1.50 metric 100
```

L'interface Ethernet est active, l'adresse IP locale est attribuée et la passerelle par défaut est bien renseignée.

### 2. Examen des journaux du noyau (`journalctl -k`)

Le journal du noyau confirme la séquence temporelle de la coupure :

```bash
journalctl -k --grep="NIC Link" --no-pager
```

```text
15:08:53 kernel: enp3s0: NIC Link is Down
15:13:41 kernel: enp3s0: NIC Link is Up 1000 Mbps Full Duplex
```

La box s'est éteinte à 15:08 et le lien physique s'est rétabli à 15:13.

### 3. Examen du démon NordVPN et du gel OpenVPN

En analysant les journaux de `nordvpnd`, le comportement défaillant apparaît distinctement :

```bash
journalctl -u nordvpnd --since "15:13:40" --until "15:15:00" --no-pager
```

```text
15:14:12 nordvpnd: TLS Error: TLS key negotiation failed to occur within 10 seconds
15:14:12 nordvpnd: SIGUSR1[soft,tls-error] received, process restarting
15:14:12 nordvpnd: MANAGEMENT: >STATE:1789996452,RECONNECTING,tls-error,,,,,
15:14:17 nordvpnd: MANAGEMENT: >STATE:1789996457,AUTH,,,,,,
```

Après cette ligne, plus aucun échange réseau n'a lieu. OpenVPN attend ses identifiants indéfiniment.

### 4. Vérification des règles de filtrage nftables

La commande `sudo nft list table inet nordvpn` met en évidence la politique de blocage :

```text
table inet nordvpn {
    chain output {
        type route hook output priority mangle; policy drop;
        oifname "lo" accept
        ct mark 0x0000e1f1 accept
        ip daddr @lan_ranges tcp dport 53 drop
        ip daddr @lan_ranges udp dport 53 drop
        oifname "nordtun" accept
    }
}
```

Tant que `nordtun` n'est pas actif, aucune trame vers Internet ne peut franchir le pare-feu.

### 5. Détection du conflit IPv6

Un examen des journaux de NetworkManager révèle un avertissement continu toutes les deux secondes :

```bash
journalctl -u NetworkManager -n 20 --no-pager
```

```text
NetworkManager[3376]: <warn> platform-linux: do-add-ip6-address[2: fe80::...]: failure 13 (Permission denied - ipv6: IPv6 is disabled on this device)
```

NordVPN désactivant IPv6 au niveau du noyau (`net.ipv6.conf.all.disable_ipv6 = 1`) pour empêcher les fuites d'adresses, NetworkManager échouait en boucle en tentant de configurer une adresse link-local IPv6 automatique.

---

## Procédure de résolution

La résolution s'articule en deux actions :
1. Harmoniser la méthode IPv6 pour assainir les journaux système.
2. Déployer un script NetworkManager Dispatcher pour redémarrer automatiquement le VPN en cas de désynchronisation consécutive à un reboot de box.

### Étape 1 : Désactiver IPv6 dans les profils NetworkManager

Pour aligner NetworkManager sur l'état réel du système imposé par NordVPN, configurez `ipv6.method` sur `disabled` :

```bash
# Identifier le nom exact de votre connexion Ethernet
nmcli connection show

# Désactiver IPv6 pour la connexion Ethernet (adapter 'enp3s0' avec votre nom de connexion)
sudo nmcli connection modify "enp3s0" ipv6.method disabled

# Optionnel : désactiver également IPv6 sur vos profils Wi-Fi habituels
sudo nmcli connection modify "MonWiFi_2.4G" ipv6.method disabled

# Réappliquer immédiatement les paramètres à chaud sans couper la liaison
sudo nmcli device reapply enp3s0
```

Vérifiez que les messages d'avertissement ont cessé :

```bash
journalctl -u NetworkManager -n 10 --no-pager
```

!!! success "Résultat attendu"
    Aucun avertissement de type `do-add-ip6-address` ne doit plus être généré.

---

### Étape 2 : Mettre en place le script de reprise NetworkManager Dispatcher

Le service **NetworkManager-dispatcher** exécute des scripts placés dans `/etc/NetworkManager/dispatcher.d/` lors de chaque changement d'état d'une interface réseau (connexion, déconnexion, attribution DHCP).

Créez le script `/etc/NetworkManager/dispatcher.d/95-nordvpn-recovery.sh` (pensez à adapter la variable `IFACE_TARGET` au nom de votre carte Ethernet, par exemple `eth0` ou `enp3s0`) :

```bash
cat << 'EOF' | sudo tee /etc/NetworkManager/dispatcher.d/95-nordvpn-recovery.sh > /dev/null
#!/bin/sh
# /etc/NetworkManager/dispatcher.d/95-nordvpn-recovery.sh
# Script NetworkManager dispatcher pour rétablir proprement NordVPN
# lors de la reconnexion Ethernet après coupure électrique de la box Internet.

IFACE="$1"
ACTION="$2"

# Remplacer par le nom de votre interface Ethernet principale (identifier avec : ip -br link)
IFACE_TARGET="enp3s0"

# Ne s'exécute que pour l'interface Ethernet ciblée lors de son passage à 'up'
if [ "$IFACE" != "$IFACE_TARGET" ] || [ "$ACTION" != "up" ]; then
    exit 0
fi

# Ne rien faire lors du démarrage initial du système (les services systemd s'initialisent déjà)
UPTIME_SECS=$(awk '{print int($1)}' /proc/uptime 2>/dev/null || echo 0)
if [ "$UPTIME_SECS" -lt 120 ]; then
    exit 0
fi

# Ne rien faire si le démon NordVPN n'est pas actif
if ! systemctl is-active --quiet nordvpnd.service; then
    exit 0
fi

# Exécution asynchrone en sous-shell pour ne pas bloquer NetworkManager
(
    # Déterminer dynamiquement l'adresse IP de la passerelle locale (la box Internet)
    GATEWAY="${IP4_GATEWAY:-$(ip route show default dev "$IFACE" 2>/dev/null | awk '{print $3}' | head -n 1)}"
    if [ -z "$GATEWAY" ]; then
        GATEWAY="192.168.1.1"
    fi

    logger -t nm-dispatcher-nordvpn "Ethernet ($IFACE) reconnecté. Surveillance de la connectivité..."

    # 1. Attendre que la passerelle locale réponde (démarrage du commutateur de la box)
    GW_REACHABLE=0
    for i in $(seq 1 12); do
        if ping -c 1 -W 2 "$GATEWAY" >/dev/null 2>&1; then
            GW_REACHABLE=1
            break
        fi
        sleep 5
    done

    if [ "$GW_REACHABLE" -ne 1 ]; then
        logger -t nm-dispatcher-nordvpn "Passerelle locale $GATEWAY injoignable après 60s, arrêt du contrôle."
        exit 0
    fi

    # 2. Laisser jusqu'à 30s à la box pour synchroniser sa liaison WAN et à NordVPN pour se reconnecter seul
    for i in $(seq 1 6); do
        sleep 5
        if ping -c 1 -W 2 1.1.1.1 >/dev/null 2>&1; then
            logger -t nm-dispatcher-nordvpn "Connectivité Internet opérationnelle via NordVPN, aucune action requise."
            exit 0
        fi
    done

    # 3. Si Internet est toujours inaccessible, OpenVPN est figé en état AUTH : redémarrage propre de secours
    logger -t nm-dispatcher-nordvpn "Internet toujours bloqué après retour de la box. Redémarrage propre de nordvpnd pour débloquer le VPN..."
    systemctl restart nordvpnd.service
) &

exit 0
EOF
```

Rendez le script exécutable et attribuez-lui les droits administrateur :

```bash
sudo chmod 755 /etc/NetworkManager/dispatcher.d/95-nordvpn-recovery.sh
sudo chown root:root /etc/NetworkManager/dispatcher.d/95-nordvpn-recovery.sh
```

!!! tip "Pourquoi ce script est sûr et n'engendre aucun effet de bord"
    - **Aucun ralentissement** : Le bloc principal est exécuté en arrière-plan `( ... ) &`. Le script rend la main à NetworkManager en quelques millisecondes.
    - **Protection au démarrage (`uptime < 120s`)** : Lors d'un démarrage normal de la machine, systemd gère lui-même l'ordonnancement des services dans l'ordre adéquat. Le script s'interdit d'intervenir.
    - **Attente passive prioritaire** : Le script teste la connectivité pendant 30 secondes. Si la box synchronise vite et qu'OpenVPN réussit à se relier sans encombre, le service n'est **jamais redémarré**.
    - **Traçabilité totale** : Toutes les étapes sont horodatées et consignées dans le journal système via la commande `logger`.

---

## Vérification et validation

### 1. Test syntaxique du script

Vérifiez l'absence d'erreur d'interprétation dans le shell :

```bash
sh -n /etc/NetworkManager/dispatcher.d/95-nordvpn-recovery.sh && echo "Syntaxe OK"
```

### 2. Test à chaud d'exécution

Simulez un appel de dispatcher pour valider son comportement sur une connexion saine (adapter avec votre nom d'interface) :

```bash
/etc/NetworkManager/dispatcher.d/95-nordvpn-recovery.sh enp3s0 up
sleep 6
journalctl -t nm-dispatcher-nordvpn -n 5 --no-pager
```

!!! success "Résultat attendu dans les logs"
    ```text
    nm-dispatcher-nordvpn: Ethernet (enp3s0) reconnecté. Surveillance de la connectivité...
    nm-dispatcher-nordvpn: Connectivité Internet opérationnelle via NordVPN, aucune action requise.
    ```

### 3. Test de connectivité globale sans Wi-Fi

Assurez-vous que le Wi-Fi est éteint et que l'ensemble du trafic passe par l'Ethernet et le VPN :

```bash
# Vérifier l'état de la puce Wi-Fi
nmcli radio wifi

# Vérifier la route et le statut NordVPN
ip route show default
nordvpn status

# Tester la résolution de nom et le ping
ping -c 2 1.1.1.1
resolvectl query google.com
```

---

## Aide-mémoire

| Commande | Rôle |
| :--- | :--- |
| `nmcli device status` | Lister les interfaces réseau et leur statut de connexion |
| `nmcli radio wifi off` | Couper totalement l'émission radio Wi-Fi |
| `sudo nmcli connection modify <conn> ipv6.method disabled` | Désactiver la gestion IPv6 sur un profil de connexion |
| `sudo nmcli device reapply <iface>` | Appliquer les changements d'un profil sans déconnecter l'interface |
| `journalctl -t nm-dispatcher-nordvpn -f` | Suivre en direct les actions du script de rétablissement VPN |
| `nordvpn status` | Afficher l'état du tunnel, l'IP publique et le protocole en cours |
| `sudo nft list table inet nordvpn` | Inspecter les règles de pare-feu actives générées par NordVPN |

---

## Glossaire

NetworkManager Dispatcher
:   Service système qui surveille les événements du gestionnaire de réseau (connexion d'un câble, attribution d'adresse IP, déconnexion) et exécute automatiquement les scripts présents dans `/etc/NetworkManager/dispatcher.d/`.

Soft-Restart (`SIGUSR1`)
:   Signal Unix standard permettant de demander à un démon de redémarrer de manière légère sans détruire son processus principal. Dans OpenVPN, il provoque une réinitialisation de la liaison TLS tout en conservant certaines options en mémoire, ce qui nécessite une ré-authentification par socket.

Obfuscated VPN (Obfuscation)
:   Technique cryptographique modifiant l'entête des paquets OpenVPN pour les faire ressembler à du trafic web sécurisé HTTPS (TLS standard), empêchant les pare-feux et les équipements d'inspection approfondie (DPI) de détecter l'usage d'un VPN.

nftables / Firewall Mark (`fwmark`)
:   Sous-système de filtrage de paquets du noyau Linux remplaçant iptables. La marque de pare-feu (`fwmark`) est une étiquette numérique interne à la pile réseau permettant d'associer un paquet à une table de routage spécifique (Policy Routing).

Link-Local IPv6 (`fe80::/10`)
:   Plage d'adresses IPv6 réservée aux communications sur le segment réseau local direct. Si le noyau a désactivé IPv6 au niveau global, toute tentative d'attribution d'adresse link-local échoue avec un code d'erreur `Permission denied` (EPERM / 13).

Onduleur (UPS - Uninterruptible Power Supply)
:   Appareil électrique muni d'une batterie permettant d'alimenter un équipement informatique sans coupure lors d'une défaillance du réseau électrique général.

---

## Ressources

- [Documentation officielle NetworkManager Dispatcher](https://networkmanager.dev/docs/api/latest/NetworkManager-dispatcher.html)
- [Guide de configuration nftables sous Linux](https://wiki.nftables.org/)
- [Documentation OpenVPN — Signaux et gestion de processus](https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/)
