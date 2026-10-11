---
title: "NordVPN — Plus aucune résolution DNS (bascule de clé racine KSK-2024) et Tailscale hors ligne"
date: 2026-10-11
author: Nicolas BODAINE
tags:
  - reseau
  - vpn
  - nordvpn
  - dns
  - dnssec
  - systemd-resolved
  - tailscale
  - nftables
  - routage
  - systemd
  - ubuntu
difficulty: avancé
os: Ubuntu 24.04
status: publié
---

# NordVPN — Plus aucune résolution DNS (bascule de clé racine KSK-2024) et Tailscale hors ligne

!!! abstract "Résumé"
    Le **11 octobre 2026**, sur un PC sous Ubuntu 24.04, l'activation de **NordVPN** coupe toute résolution de noms : `ping 1.1.1.1` répond, mais `ping free.fr` renvoie `Nom ou service inconnu`. Sans VPN, tout fonctionne.

    La cause ne vient ni de NordVPN ni du réseau, mais d'un **événement mondial** : ce jour-là, la zone racine du DNS commence à signer avec sa nouvelle clé **KSK-2024** (key tag `38696`). NordVPN active la validation **DNSSEC** sur son interface, et le `systemd-resolved` d'Ubuntu 24.04 (version 255) ne connaît que l'ancienne clé **KSK-2017** (`20326`), inscrite en dur dans son binaire. Toute la chaîne de confiance échoue (`DNSSEC validation failed: missing-key`), y compris pour les domaines non signés. La correction consiste à déclarer les deux clés racine dans `/etc/dnssec-trust-anchors.d/`, via un lien vers le fichier du paquet `dns-root-data`, pour suivre automatiquement les prochaines bascules.

    En testant la correction, un second problème apparaît : **Tailscale reste « offline » dès que NordVPN est connecté**. tailscaled marque ses propres paquets (`0x80000`) pour qu'ils contournent les tunnels, et le pare-feu nftables de NordVPN (`policy drop`) les jette. Les exceptions UDP habituelles ne suffisent pas, car la coordination et les relais DERP passent en **TCP 443**. La solution ajoute une seule règle de routage, persistée par un service systemd, qui fait passer le TCP de tailscaled **dans** le tunnel NordVPN. L'option `nordvpn set fwmark 0x80000`, tentante, est écartée : elle casse le trafic entre les appareils du tailnet.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Avancé |
| OS / Environnement | Ubuntu 24.04 LTS Desktop (GNOME) |
| Composants clés | systemd-resolved 255, NordVPN 5.4 (NordWhisper), Tailscale 1.104, nftables, routage par politique (`ip rule`) |
| Élément déclencheur | Bascule de la clé racine DNSSEC (KSK-2017 → KSK-2024) le 11/10/2026 |
| Dernière mise à jour | 2026-10-11 |

*(Dans les exemples ci-dessous, nous utilisons l'interface Ethernet `enp3s0`, le réseau local `192.168.1.0/24`, la box `192.168.1.1`, le tailnet fictif `tailnet-exemple.ts.net` et des adresses Tailscale fictives en `100.64.0.x`. Les serveurs DNS de NordVPN, les numéros de clés et les règles de pare-feu sont, eux, réels.)*

## Contexte

- PC fixe sous Ubuntu 24.04, **NordVPN** en connexion automatique au démarrage, technologie **NordWhisper** (interface `qtun` ; avec NordLynx ou OpenVPN, l'interface s'appelle `nordlynx` ou `nordtun`).
- **Tailscale** installé en parallèle, avec des exceptions NordVPN prévues pour lui : ports UDP `41641` et `3478`, sous-réseau `100.64.0.0/10`.
- Symptômes, uniquement quand NordVPN est connecté :
    - `ping 1.1.1.1` fonctionne, `ping free.fr` échoue (`Nom ou service inconnu`) ;
    - même après `tailscale down`, le problème persiste : Tailscale n'est donc pas en cause pour le DNS ;
    - plus tard : `tailscale status` affiche **la machine elle-même** comme `offline`, et les réglages DNS modifiés dans la console Tailscale ne sont jamais appliqués.

---

## Partie 1 — DNS : la bascule de la clé racine DNSSEC

### Comprendre la chaîne de confiance

DNSSEC signe les réponses DNS. Un résolveur qui **valide** vérifie la signature de proche en proche : la racine `.` garantit la clé de `.fr`, `.fr` garantit celle de `free.fr`, etc. Tout en haut, il faut connaître à l'avance la clé de la racine (la **KSK**, *Key Signing Key*) : c'est l'**ancre de confiance**.

```text
Ancre de confiance (connue localement) ── doit correspondre à ──> KSK de la racine
                                                                    │ signe
                                                                    ▼
                                                     DNSKEY de la racine (ZSK)
                                                                    │ signent
                                                                    ▼
                                                     DS de .fr → DNSKEY de .fr → … → réponse
```

Si l'ancre locale ne correspond à aucune clé qui signe réellement la racine, **rien** ne peut être validé en dessous. C'est vrai aussi pour un domaine non signé : prouver qu'il n'est *pas* signé demande aussi une chaîne validée depuis la racine.

### Le calendrier de la bascule 2024-2026

| Date | Étape |
|------|-------|
| 11 janvier 2025 | KSK-2024 (`38696`) publiée dans la racine, à côté de KSK-2017 (`20326`) |
| 10 février 2025 | Les résolveurs qui appliquent le RFC 5011 l'adoptent automatiquement (30 jours de délai de garde) |
| **11 octobre 2026** | **KSK-2024 signe seule** ; KSK-2017 reste publiée mais ne signe plus |
| 11 janvier 2027 | KSK-2017 révoquée |

### Pourquoi presque personne n'a rien vu… sauf ce PC

- La plupart des machines **ne valident pas** DNSSEC elles-mêmes : elles font confiance au résolveur de la box, du FAI ou d'un service public. Ces résolveurs (Unbound, BIND, services publics…) appliquent le **RFC 5011** : ils ont vu la nouvelle clé apparaître en 2025 et l'ont adoptée seuls (plus de 95 % d'adoption mesurée avant la bascule).
- Hors VPN, toutes les interfaces de ce PC sont en `DNSSEC=no` : aucune validation locale, aucun impact.
- **Sous NordVPN**, l'interface `qtun` passe en `DNSSEC=allow-downgrade` : le PC devient lui-même validateur.
- `systemd-resolved` **n'applique pas le RFC 5011**. Sa clé racine est compilée dans le binaire. La version 255 livrée avec Ubuntu 24.04 est antérieure à KSK-2024 et ne la contient pas (des versions plus récentes de systemd l'intègrent).
- Ironie : la nouvelle clé était déjà sur le disque depuis 2024, dans `/usr/share/dns/root.ds` (paquet `dns-root-data`, utilisé par dnsmasq ou Unbound)… mais `systemd-resolved` ne lit pas ce fichier.

!!! note "Pourquoi `allow-downgrade` ne « rétrograde » pas"
    Le mode `allow-downgrade` ne renonce à la validation que si le serveur **ne gère pas du tout** DNSSEC (aucune signature renvoyée). Ici, les serveurs DNS de NordVPN renvoient bien les signatures ; elles sont simplement jugées invalides faute de la bonne ancre. Une réponse dont la signature ne peut être validée est **refusée** : sinon, un attaquant pourrait falsifier des signatures pour forcer le retour au DNS non protégé.

### Diagnostic pas-à-pas

#### 1. Isoler la couche DNS

```bash
ping -c 2 1.1.1.1     # répond : le tunnel et le routage fonctionnent
ping -c 2 free.fr     # « Nom ou service inconnu » : seule la résolution est cassée
```

#### 2. Distinguer le serveur DNS du résolveur local

`ping` passe par `getaddrinfo()`, qui ramène toutes les erreurs à « Nom ou service inconnu ». Il faut interroger les deux maillons séparément :

```bash
# Le serveur DNS de NordVPN, interrogé directement : il répond
dig +short @103.86.96.100 free.fr

# Le résolveur local (systemd-resolved) : il échoue, et dit pourquoi
resolvectl query free.fr
```

```text
212.27.48.10
free.fr: resolve call failed: DNSSEC validation failed: missing-key
```

Le serveur est sain : le problème est **local**.

#### 3. Repérer qui valide DNSSEC

```bash
resolvectl dnssec
```

```text
Global: no
Link 2 (enp3s0): no
Link 6 (tailscale0): no
Link 23 (qtun): allow-downgrade
```

Seule l'interface du VPN valide DNSSEC.

#### 4. Mesurer l'ampleur dans le journal

```bash
# Nombre d'échecs de validation par démarrage
for b in -3 -2 -1 0; do
  echo "boot $b : $(journalctl -u systemd-resolved -b $b --no-pager | grep -c 'DNSSEC validation failed')"
done
```

```text
boot -3 : 21
boot -2 : 43
boot -1 : 66877
boot 0 : 14128
```

Quelques dizaines d'échecs par démarrage relèvent du bruit normal (domaines mal configurés). Des dizaines de milliers, à partir d'une date précise, signent une panne de la chaîne de confiance.

#### 5. Vérifier quelle clé signe la racine aujourd'hui

!!! warning "Interroger les serveurs racine, pas un résolveur public"
    L'enregistrement `DNSKEY` de la racine a une durée de vie de 48 h dans les caches. Un résolveur public peut encore renvoyer l'**ancienne** signature pendant deux jours et masquer la bascule. Seuls les serveurs racine (sans cache) montrent l'état réel.

```bash
dig +dnssec +norec @a.root-servers.net . DNSKEY | awk '$4=="RRSIG"{print "signé par key tag", $11, "valide du", $10}'
```

```text
signé par key tag 38696 valide du 20261011000000
```

#### 6. Vérifier quelles clés connaît `systemd-resolved`

```bash
python3 - <<'EOF'
data = open("/usr/lib/systemd/systemd-resolved", "rb").read()
cles = {
    "KSK-2017 (20326)": "E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D",
    "KSK-2024 (38696)": "683D2D0ACB8C9B712A1948B27F741219298D0A450D612C483AF444A4C0FB2B16",
}
for nom, empreinte in cles.items():
    print(nom, "présente" if bytes.fromhex(empreinte) in data else "ABSENTE")
EOF
```

```text
KSK-2017 (20326) présente
KSK-2024 (38696) ABSENTE
```

Le diagnostic est complet : la racine signe avec `38696`, le résolveur local ne connaît que `20326`.

### Résolution

#### 1. Contrôler le fichier de clés du paquet `dns-root-data`

```bash
cat /usr/share/dns/root.ds
```

```text
. IN DS 20326 8 2 E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D
. IN DS 38696 8 2 683D2D0ACB8C9B712A1948B27F741219298D0A450D612C483AF444A4C0FB2B16
```

Ces deux empreintes sont identiques à celles publiées par l'IANA dans [root-anchors.xml](https://data.iana.org/root-anchors/root-anchors.xml).

#### 2. Déclarer les ancres via un lien symbolique

```bash
sudo mkdir -p /etc/dnssec-trust-anchors.d
sudo ln -sf /usr/share/dns/root.ds /etc/dnssec-trust-anchors.d/root.positive
sudo systemctl restart systemd-resolved
```

!!! warning "Le fichier remplace la clé intégrée : il doit contenir les deux clés"
    Dès qu'une ancre positive pour la racine est déclarée dans `/etc/dnssec-trust-anchors.d/`, `systemd-resolved` **ignore sa clé intégrée**. Le fichier doit donc contenir l'ancienne et la nouvelle clé pendant la transition.

!!! tip "Pourquoi un lien plutôt qu'une copie"
    Une copie resterait figée et désactiverait à jamais la clé intégrée, même après une mise à jour de systemd. Le lien suit le paquet `dns-root-data`, qu'Ubuntu met à jour bien avant chaque bascule (il contenait KSK-2024 près de deux ans avant le 11 octobre 2026).

!!! failure "Contournement temporaire (à éviter durablement)"
    En urgence, on peut couper la validation sur l'interface du VPN jusqu'à la prochaine reconnexion : `sudo resolvectl dnssec qtun no`. C'est aussi un excellent **test de confirmation** : si tout remarche, DNSSEC est bien en cause. Mais la protection DNSSEC est alors perdue.

### Vérification

```bash
# Les deux ancres sont chargées au démarrage du résolveur
journalctl -u systemd-resolved -b --no-pager | grep -A2 "Positive Trust Anchors"

# Sous NordVPN : un domaine signé est authentifié…
resolvectl query isc.org | grep authenticated

# … un domaine volontairement mal signé est refusé…
resolvectl query dnssec-failed.org

# … et la navigation fonctionne
ping -c 2 free.fr
```

!!! success "Résultat attendu"
    ```text
    Positive Trust Anchors:
    . IN DS 20326 8 2 e06d44b8…
    . IN DS 38696 8 2 683d2d0a…
    -- Data is authenticated: yes; Data was acquired via local or encrypted transport: no
    dnssec-failed.org: resolve call failed: DNSSEC validation failed: missing-key
    2 packets transmitted, 2 received, 0% packet loss
    ```

    `free.fr` ou `github.com` affichent `authenticated: no` : c'est normal, ces domaines ne sont pas signés.

### Anticiper les prochaines bascules

| Échéance | Impact avec le lien `root.positive` |
|----------|-------------------------------------|
| 11 janvier 2027 — révocation de KSK-2017 | Aucun : KSK-2024 est dans le fichier |
| 2027 → 2029 — changement d'algorithme RSA → ECDSA (proposition ICANN) | Aucun si `dns-root-data` est mis à jour à temps |
| Ensuite — un cycle de bascule tous les 3 ans | Idem |

- Les bascules sont annoncées **des mois à l'avance** (blog et liste `ksk-rollover` de l'ICANN, listes FRnOG ou dns-operations, presse spécialisée).
- À chaque annonce, se poser une question : **une de mes machines valide-t-elle DNSSEC avec une ancre figée ?** Les candidats habituels sont `systemd-resolved` (dès qu'un VPN ou un réglage active DNSSEC) et les résolveurs configurés sans mise à jour automatique des clés.
- Avant la date de bascule, vérifier que la nouvelle clé est présente :

```bash
grep <key-tag-de-la-nouvelle-clé> /usr/share/dns/root.ds
```

---

## Partie 2 — Tailscale « offline » dès que NordVPN est connecté

### Symptômes

```bash
tailscale status --json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["Self"]["Online"]); print(*d.get("Health") or [], sep="\n")'
```

```text
False
Unable to connect to the Tailscale coordination server to synchronize the state of your tailnet.
You are logged out. The last login error was: register request: … context deadline exceeded
```

```bash
journalctl -u tailscaled --since "-10min" --no-pager | grep -iE "timeout|failed"
```

```text
logtail: dial "log.tailscale.com:443" failed: dial tcp …:443: i/o timeout
derp.Recv(derp-…): derphttp.Client.Recv connect to region …: context deadline exceeded
control: controlhttp: failed dialing using DialPlan … connect: cannot assign requested address
```

Conséquence sournoise : tant que tailscaled ne joint pas son serveur de coordination, **aucun changement fait dans la console Tailscale n'arrive sur la machine** (réglages DNS compris). `tailscale dns status` continue d'afficher l'ancienne configuration.

### Comprendre le blocage

```text
tailscaled (sockets marqués 0x80000 = « ne pas passer par un tunnel »)
  │
  ├─ ip rule 5210 : fwmark 0x80000/0xff0000 → table main → enp3s0 (sortie directe)
  │
  └─ nftables « inet nordvpn », chaîne output, policy DROP. N'accepte que :
       • oifname "qtun"                         (le tunnel)
       • meta mark 0xe1f1                       (marque propre à NordVPN)
       • ip daddr @allowlist_subnets            (ex. 100.64.0.0/10)
       • udp sport @udp_allowlist               (ex. 41641, 3478)
     ⇒ UDP 41641 (WireGuard / STUN)  : accepté
     ⇒ TCP 443 (coordination, DERP)  : JETÉ
```

Les exceptions NordVPN habituellement conseillées pour Tailscale laissent passer le trafic WireGuard, mais pas le TCP 443 qui sert à joindre le serveur de coordination et les relais DERP.

### Diagnostic

#### 1. Comparer la route d'un paquet normal et d'un paquet de tailscaled

```bash
ip route get 1.1.1.1
ip route get 1.1.1.1 mark 0x80000
```

```text
1.1.1.1 dev qtun table 205 src 10.3.0.2
1.1.1.1 via 192.168.1.1 dev enp3s0 src 192.168.1.50 mark 0x80000
```

#### 2. Prouver le blocage avec une connexion marquée

Ce script ouvre une connexion TCP vers le serveur de coordination avec chacune des marques (la marque d'un socket exige les droits root) :

```bash
sudo python3 - <<'EOF'
import socket
SO_MARK = 36
ip = socket.gethostbyname("controlplane.tailscale.com")
for nom, marque in [("sans marque", None), ("marque tailscaled 0x80000", 0x80000), ("marque NordVPN 0xe1f1", 0xE1F1)]:
    s = socket.socket(); s.settimeout(6)
    if marque is not None:
        s.setsockopt(socket.SOL_SOCKET, SO_MARK, marque)
    try:
        s.connect((ip, 443)); print(f"{nom:28} -> connecté via {s.getsockname()[0]}")
    except OSError as e:
        print(f"{nom:28} -> ÉCHEC ({e})")
    s.close()
EOF
```

```text
sans marque                  -> connecté via 10.3.0.2
marque tailscaled 0x80000    -> ÉCHEC (timed out)
marque NordVPN 0xe1f1        -> connecté via 192.168.1.50
```

Le chemin réseau fonctionne : c'est bien le pare-feu de NordVPN qui jette les paquets de tailscaled.

### La fausse bonne idée : `nordvpn set fwmark 0x80000`

Donner à NordVPN la même marque que Tailscale semble logique : son pare-feu accepterait alors les paquets de tailscaled. **Mais cela casse le tailnet.** L'exception `100.64.0.0/10` de NordVPN **re-marque** le trafic vers les appareils Tailscale avec la marque de NordVPN. Avec `0x80000`, ce trafic tomberait sur la règle 5210 de Tailscale et partirait vers la box au lieu de `tailscale0` :

```bash
ip route get 100.64.0.20 mark 0xe1f1     # marque actuelle de NordVPN
ip route get 100.64.0.20 mark 0x80000    # marque proposée
```

```text
100.64.0.20 dev tailscale0 table 52 src 100.64.0.10 mark 0xe1f1
100.64.0.20 via 192.168.1.1 dev enp3s0 src 192.168.1.50 mark 0x80000
```

Tailscale joindrait ses serveurs, mais les appareils ne se joindraient plus entre eux.

### Résolution : faire passer le TCP de tailscaled dans le tunnel NordVPN

#### 1. Prérequis : les exceptions NordVPN pour le trafic Tailscale

```bash
nordvpn allowlist add port 41641 protocol UDP
nordvpn allowlist add port 3478 protocol UDP
nordvpn allowlist add subnet 100.64.0.0/10
```

#### 2. Repérer la table de routage de NordVPN

```bash
ip rule | grep "not from all fwmark"
ip route show table 205
```

```text
32765:	not from all fwmark 0xe1f1 lookup 205
default dev qtun scope link
```

Ici, la table est `205`. Adaptez la suite si votre version de NordVPN en utilise une autre.

#### 3. Tester la règle à chaud

```bash
sudo ip rule add priority 5100 fwmark 0x80000/0xff0000 ipproto tcp lookup 205
```

En une minute environ, `tailscale status` doit repasser la machine en ligne. Pour annuler : `sudo ip rule del priority 5100`.

!!! tip "Pourquoi cette règle est sûre"
    - **Priorité 5100** : avant les règles de Tailscale (5210 à 5270), et hors de la plage qu'il gère lui-même, qui ne l'efface donc pas en redémarrant.
    - **TCP uniquement** : la coordination et les relais DERP passent dans le tunnel, le seul chemin accepté par NordVPN. L'UDP de WireGuard reste direct grâce à l'exception, ce qui préserve les connexions directes entre appareils.
    - **Sans NordVPN**, la table 205 est vide : la règle ne trouve aucune route et le routage continue normalement, sans effet.
    - Le trafic de NordVPN lui-même (marque `0xe1f1`) et celui du tailnet ne sont pas concernés.

#### 4. Rendre la règle permanente avec un service systemd

```bash
cat << 'EOF' | sudo tee /etc/systemd/system/tailscale-via-nordvpn.service > /dev/null
# Fait passer les connexions TCP propres à tailscaled (coordination, relais DERP)
# dans le tunnel NordVPN (table 205), seul chemin accepté par le pare-feu NordVPN.
# Sans NordVPN, la table 205 est vide et la règle est sans effet.
[Unit]
Description=Faire passer le TCP de tailscaled dans le tunnel NordVPN (table 205)
After=network-pre.target
Before=tailscaled.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=-/usr/sbin/ip rule del priority 5100
ExecStart=/usr/sbin/ip rule add priority 5100 fwmark 0x80000/0xff0000 ipproto tcp lookup 205
ExecStop=/usr/sbin/ip rule del priority 5100

[Install]
WantedBy=multi-user.target
EOF

sudo systemd-analyze verify /etc/systemd/system/tailscale-via-nordvpn.service
sudo ip rule del priority 5100 2>/dev/null   # retirer la règle de test
sudo systemctl daemon-reload
sudo systemctl enable --now tailscale-via-nordvpn.service
```

!!! note "Message `ExecStartPre … status=2` dans `systemctl status`"
    Avant de poser la règle, le service tente de supprimer une éventuelle copie existante. Quand il n'y en a pas, cette suppression échoue, et le préfixe `-` demande à systemd d'ignorer cet échec. C'est ce qui garantit l'absence de doublon lors d'un `restart`.

!!! warning "Ce que voient les tiers"
    Les serveurs de Tailscale voient désormais une IP NordVPN pour la coordination. En revanche, l'UDP direct, indispensable aux connexions pair à pair, révèle toujours l'IP publique réelle aux autres appareils du tailnet et aux serveurs STUN. C'était déjà le cas avec les exceptions UDP : c'est le prix des connexions directes.

### Bonus : le DNS de Tailscale en concurrence avec celui de NordVPN

Si l'option **« Override DNS servers »** (aussi appelée « Override local DNS ») est activée dans la console Tailscale, l'interface `tailscale0` réclame **tous** les domaines (`~.`), exactement comme NordVPN :

```bash
resolvectl domain
```

```text
Link 6 (tailscale0): tailnet-exemple.ts.net ~.
Link 23 (qtun): ~.
```

Chaque requête part alors **en parallèle** vers NordVPN et vers MagicDNS (`100.100.100.100`), qui la relaie à ses propres serveurs globaux. Il n'y a pas de fuite hors tunnel (une capture le confirme), mais plusieurs résolveurs voient chaque requête, et un nom en échec fait patienter les applications au lieu d'échouer immédiatement.

En désactivant cette option, `tailscale0` ne traite plus que les noms du tailnet (et les zones inverses `100.x`). Tout le reste passe par NordVPN, et MagicDNS continue de fonctionner, y compris pour les noms courts. Rappel : ce changement n'atteint la machine que si tailscaled est en ligne (voir la résolution ci-dessus).

### Vérification

```bash
# 1. Tailscale en ligne, sans alerte
tailscale status --json | python3 -c 'import json,sys; d=json.load(sys.stdin); print("Online:", d["Self"]["Online"], "| alertes:", len(d.get("Health") or []))'

# 2. La règle est en place et gérée par systemd
systemctl is-active tailscale-via-nordvpn.service
ip rule | grep "^5100:"

# 3. Le DNS : noms du tailnet via tailscale0, le reste via le VPN
resolvectl query laptop                # nom court MagicDNS
resolvectl query free.fr

# 4. La sortie Internet passe bien par NordVPN
nordvpn status

# 5. Le trafic entre appareils (avec un appareil du tailnet allumé)
tailscale ping laptop
```

!!! success "Résultat attendu"
    ```text
    Online: True | alertes: 0
    active
    5100:	from all fwmark 0x80000/0xff0000 ipproto tcp lookup 205
    laptop: 100.64.0.20                                    -- link: tailscale0
    free.fr: 212.27.48.10                                  -- link: qtun
    ```

Tests de robustesse réalisés : la règle survit à `systemctl restart tailscaled`, à un changement de serveur NordVPN et à une coupure suivie d'une reconnexion du VPN. Tailscale revient en ligne en quelques secondes à chaque fois.

#### Contrôler l'absence de fuite hors tunnel

Capturez tout ce qui sort par la carte physique, sauf le tunnel lui-même (l'IP du serveur NordVPN figure dans `nordvpn status`) :

```bash
sudo tcpdump -nqi enp3s0 "ip and not host <IP_SERVEUR_NORDVPN> and not arp"
```

Pendant que vous naviguez et résolvez des noms, seuls doivent apparaître :

- le trafic propre au démon `nordvpnd` (son API, ses notifications), qui contourne le tunnel par conception ;
- l'UDP `41641` ↔ `3478` de tailscaled (WireGuard et STUN, autorisés par l'exception) ;
- du trafic local vers la box (NAT-PMP `5351`, UPnP `1900`, mDNS `5353`).

Pour identifier un flux inattendu, `ss` affiche le processus et la marque de chaque socket :

```bash
sudo ss -tunpe | grep <IP_DESTINATION>
```

```text
tcp ESTAB … users:(("nordvpnd",pid=…)) … fwmark:0xe1f1 cgroup:/system.slice/nordvpnd.service
```

---

## Réflexes de diagnostic à retenir

1. **IP joignable mais noms introuvables** : le problème est le DNS, pas le réseau.
2. **Ne jamais diagnostiquer le DNS avec `ping`** : `resolvectl query <nom>` donne la vraie raison de l'échec.
3. **Serveur ou résolveur local ?** `dig @<serveur> <nom>` réussit et `resolvectl query` échoue : le problème est local.
4. **Lire le journal du résolveur** : `journalctl -u systemd-resolved -b`. Un volume anormal d'erreurs à partir d'une date précise oriente vers un événement extérieur.
5. **Message `missing-key` ou `failed-auxiliary`** : penser à l'ancre de confiance DNSSEC, et vérifier la racine directement avec `dig @a.root-servers.net`.
6. **Un service « offline » derrière un VPN à pare-feu** : comparer `ip route get <ip>` avec et sans la marque du service, puis lire la chaîne `output` de nftables.
7. **Avant d'appliquer un correctif de routage**, simuler son effet sur **tous** les flux, y compris ceux qui fonctionnent déjà, avec `ip route get … mark …`.

---

## Aide-mémoire

| Commande | Rôle |
| :--- | :--- |
| `resolvectl query <nom>` | Résoudre un nom via systemd-resolved et afficher la cause exacte d'un échec |
| `resolvectl status` / `resolvectl domain` | Voir, par interface, les serveurs DNS et les domaines de routage |
| `resolvectl dnssec` | Voir le mode DNSSEC de chaque interface |
| `sudo resolvectl dnssec <iface> no` | Couper temporairement la validation DNSSEC sur une interface (test ou urgence) |
| `journalctl -u systemd-resolved -b \| grep "DNSSEC validation failed"` | Repérer les échecs de validation |
| `dig +dnssec +norec @a.root-servers.net . DNSKEY` | Voir quelle clé signe réellement la racine, sans cache |
| `cat /usr/share/dns/root.ds` | Lister les ancres racine fournies par le paquet `dns-root-data` |
| `tailscale status --json` | État interne de Tailscale (`Online`, alertes de santé) |
| `tailscale dns status` | Configuration DNS reçue du serveur de coordination |
| `ip route get <ip> mark <marque>` | Simuler le routage d'un paquet portant une marque donnée |
| `sudo nft list chain inet nordvpn output` | Lire les règles de sortie du pare-feu NordVPN |
| `sudo ss -tunpe` | Lister les sockets avec leur processus et leur marque (`fwmark`) |

---

## Glossaire

DNSSEC
:   Extension du DNS qui signe cryptographiquement les réponses. Un résolveur validant vérifie chaque signature, de la racine jusqu'au nom demandé.

KSK (Key Signing Key)
:   Clé qui signe l'ensemble des clés d'une zone. La KSK de la racine est le point de départ de toute validation DNSSEC.

Ancre de confiance (trust anchor)
:   Clé (ou empreinte `DS` de clé) connue à l'avance par un résolveur et qui sert de point de départ à la validation. Avec systemd-resolved, elle est soit intégrée au binaire, soit déclarée dans `/etc/dnssec-trust-anchors.d/*.positive`.

RFC 5011
:   Mécanisme de mise à jour automatique des ancres de confiance : un résolveur qui voit une nouvelle KSK publiée de façon stable pendant 30 jours l'adopte. systemd-resolved ne l'implémente pas.

`allow-downgrade`
:   Mode de systemd-resolved qui valide DNSSEC quand le serveur le permet et y renonce s'il ne renvoie aucune signature. Une signature présente mais invalide entraîne un refus.

Domaine de routage (`~domaine`)
:   Indique à systemd-resolved d'envoyer les requêtes d'un domaine vers une interface donnée. `~.` signifie « tous les domaines ».

Marque de pare-feu (`fwmark`)
:   Étiquette numérique posée sur un paquet (par un socket avec `SO_MARK` ou par nftables) et utilisée par les règles de routage par politique (`ip rule`). Tailscale utilise `0x80000`, NordVPN `0xe1f1` par défaut.

Routage par politique (`ip rule`)
:   Liste ordonnée de règles qui choisit la table de routage à consulter selon la marque, la source, la destination ou le protocole d'un paquet.

MagicDNS
:   Résolveur DNS intégré à Tailscale (`100.100.100.100`) qui résout les noms des appareils du tailnet.

DERP
:   Relais chiffrés de Tailscale, joints en TCP 443, utilisés quand deux appareils ne peuvent pas établir de connexion UDP directe.

---

## Ressources

- [ICANN — Se préparer à la bascule de la KSK de la zone racine](https://www.icann.org/fr/blogs/details/preparing-for-the-root-zone-ksk-rollover-what-you-need-to-know-27-07-2026-en)
- [Cloudflare — The keys to the Internet change on October 11](https://blog.cloudflare.com/root-ksk-2024-rollover/)
- [Verisign — The 2024-2026 Root Zone KSK Rollover: updates and observations](https://blog.verisign.com/security/2024-2026-root-zone-ksk-rollover-updates-observations/)
- [ICANN — Proposition de changement d'algorithme de la KSK racine (consultation publique)](https://www.icann.org/fr/public-comment/proceeding/proposed-root-ksk-algorithm-rollover-03-02-2026)
- [IANA — Ancres de confiance de la racine (root-anchors.xml)](https://data.iana.org/root-anchors/root-anchors.xml)
- [RFC 5011 — Automated Updates of DNS Security Trust Anchors](https://www.rfc-editor.org/rfc/rfc5011)
- [Manuel Ubuntu 24.04 — dnssec-trust-anchors.d(5)](https://manpages.ubuntu.com/manpages/noble/man5/dnssec-trust-anchors.d.5.html)
- [Manuel Ubuntu 24.04 — resolvectl(1)](https://manpages.ubuntu.com/manpages/noble/man1/resolvectl.1.html)
- [Tailscale — Utiliser Tailscale avec d'autres VPN](https://tailscale.com/kb/1105/other-vpns)
- [Tailscale — DNS dans Tailscale](https://tailscale.com/kb/1054/dns)
- [Tailscale — Ports à ouvrir dans un pare-feu](https://tailscale.com/kb/1082/firewall-ports)
- Sur ce wiki : [NordVPN — Perte de connexion Ethernet après redémarrage de la box](nordvpn-perte-connexion-ethernet-reboot-box-onduleur.md) (autre conséquence de la politique `drop` du pare-feu NordVPN), [Lire, filtrer et suivre les logs avec journalctl](journalctl-lire-filtrer-suivre-logs-systemd-linux.md) et [Capturer et diagnostiquer le trafic réseau avec tcpdump](capturer-diagnostiquer-trafic-reseau-tcpdump.md)
