---
title: "Installer et configurer un résolveur DNS cache local avec Unbound sur Ubuntu"
date: 2026-07-05
author: Nicolas BODAINE
tags:
  - dns
  - unbound
  - résolveur
  - cache
  - ubuntu
  - reseaux
difficulty: intermédiaire
os: Ubuntu Server 24.04
status: publié
---

# Installer et configurer un résolveur DNS cache local avec Unbound sur Ubuntu

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour **installer et configurer Unbound**, un résolveur DNS **validateur, récursif et avec cache**, directement sur un serveur **Ubuntu Server 24.04**. Vous apprendrez à faire pointer le système vers ce résolveur local (`127.0.0.1`), à tester la résolution et le cache avec `dig`, et à durcir la configuration de base. Idéal en lab ou comme infrastructure DNS saine pour un petit réseau local.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu Server 24.04 |
| Dernière mise à jour | 2026-07-05 |

## Contexte

Quand on évoque le « DNS », on mélange souvent trois rôles très différents :

- **Le résolveur** (les anglais disent *resolver*) : le programme qui répond à la question « *quelle est l'adresse IP de `example.com` ?* » en remontant toute la hiérarchie DNS depuis la racine.
- **Le serveur de noms faisant autorité** : le serveur qui détient la vraie réponse pour une zone donnée (`bodaine.fr` chez un hébergeur, par exemple).
- **Le cache** : le stockage temporaire des réponses déjà obtenues, pour allez plus vite et consommer moins de bande passante.

Par défaut, Ubuntu interroge directement le résolveur fourni par le FAI ou par le cloud (1.1.1.1, 8.8.8.8…). Il n'y a rien de mal à cela, mais :

- ça dépend d'un **tiers externe** pour chaque requête ;
- ça **ne cache rien** sur la machine (ou peu) ;
- on ne peut pas facilement **personnaliser** les redirections locales (anti-publicité, domaines internes, etc.).

Installer **Unbound** sur sa propre machine permet d'obtenir un **résolveur local validateur** :

- il interroge lui-même **la racine DNS** (pas de dépendance au DNS du FAI) ;
- il met en **cache** les réponses — la deuxième résolution est instantanée ;
- il valide les réponses avec **DNSSEC** quand la zone est signée ;
- il reste **maître de sa configuration** (`127.0.0.1` ne fuit plus vers l'opérateur).

!!! tip "Complément utile"
    Si vous voulez partir de **cdot diag DNS** ou que vous venez de suivre [Diagnostiquer une panne DNS avec `dig`, `host` et `resolvectl` sur Ubuntu](diagnostiquer-panne-dns-dig-host-resolvectl-ubuntu.md), cet article est la suite naturelle : de l'analyse vous passez à la mise en place d'une **infrastructure DNS saine et autonome**.

### Lab de démonstration

| Élément | Exemple |
|---------|---------|
| Machine test | `ubuntu-lab-dns` |
| Interface réseau | `ens18` |
| Durée du cache par défaut | 1 heure |
| Adresse d'écoute | `127.0.0.1` (locale) |
| Plage serveur | Ubuntu Server 24.04 LTS |

!!! note "Adaptez à votre environnement"
    Dans un lab d'entreprise, vous pourrez ouvrir l'écoute sur le LAN (`0.0.0.0` ou l'IP LAN du serveur) pour servir un **DNS commun** à plusieurs VM. La procédure est strictement la même ; seule l'interface change.

## Prérequis

- Une VM ou un serveur **Ubuntu Server 24.04** (une VM VirtualBox libvirt fait parfaitement l'affaire).
- Un compte avec les droits **`sudo`**.
- Une **connectivité réseau** minimale vers Internet (on va interroger la racine `a.root-servers.net`).
- Les outils de test installés : `dig`/`nslookup`, contenus dans le paquet **`dnsutils`**.

!!! note "À propos d'Unbound"
    **Unbound** est développé par **NLnet Labs** (Pays-Bas), un institut reconnu pour ses implémentations DNS de référence. C'est l'alternative légitime et modernisée à BIND en mode résolveur. Il est disponible dans les dépôts Ubuntu sans ajout de PPA.

## Procédure

### Étape 1 : préparer la machine et installer Unbound

Commencez par installer les paquets nécessaires.

```bash
sudo apt update
sudo apt install -y unbound dnsutils
```

Vérifiez la version installée — il faut au moins la **1.19** sur Ubuntu 24.04 :

```bash
unbound -V
```

!!! success "Résultat attendu"
    La commande affiche la version d'Unbound, sa date de compilation et la liste des options activées. On doit notamment voir **`DNSSEC`** dans les fonctionnalités, car c'est ce qui permet la validation cryptographique des réponses.

### Étape 2 : comprendre la configuration par défaut

Sur Ubuntu, Unbound lit **deux fichiers** :

1. `/etc/unbound/unbound.conf` — le fichier principal, qui contient en général une directive `include`.
2. `/etc/unbound/unbound.conf.d/*.conf` — les fichiers ajoutés par l'administrateur, typiquement `root-auto-trust-anchor.conf` pour DNSSEC.

Regardez le contenu :

```bash
cat /etc/unbound/unbound.conf
ls /etc/unbound/unbound.conf.d/
```

On y trouve en général :

- `root-auto-trust-anchor.conf` — déclare la clé racine DNSSEC, rafraîchie automatiquement ;
- le fichier `qname-minimisation.conf` si activé sur votre système.

### Étape 3 : récupérer les hints de la racine (fichier `root.hints`)

Unbound est un **récursif partant de la racine**. Pour amorcer les requêtes, il doit connaître l'adresse des **13 serveurs racines** (`a.root-servers.net` à `m.root-servers.net`). Ces informations sont stockées dans un fichier **`root.hints`**.

Sur Ubuntu 24.04, ce fichier **n'est pas fourni** par défaut. On le récupère sur le site officiel de l'IANA :

```bash
sudo mkdir -p /var/lib/unbound
sudo wget -O /var/lib/unbound/root.hints https://www.internic.net/domain/named.root
```

Vérifiez rapidement le contenu :

```bash
head -20 /var/lib/unbound/root.hints
```

!!! success "Résultat attendu"
    Le fichier contient des lignes `A`, `AAAA` et `NS` listant les serveurs racines `.ROOT.` et `a.` à `m.root-servers.net`.

!!! warning "Mise à jour périodique"
    Ce fichier **`root.hints`** change rarement (les racines ne bougent que sur plusieurs années), mais il est conseillé de le rafraîchir **une fois par an**. On peut automatiser cela avec un timer `systemd` ou un simple `cron`.

### Étape 4 : écrire la configuration personnalisée

Créez un fichier de configuration dédié — on évite de modifier les fichiers système fournis par le paquet, c'est plus propre et plus survivable aux mises à jour :

```bash
sudo nano /etc/unbound/unbound.conf.d/00-resolveur-local.conf
```

Insérez la configuration suivante :

```yaml title="/etc/unbound/unbound.conf.d/00-resolveur-local.conf"
# --- Serveur ---
server:
    # On écoute uniquement sur la boucle locale pour ce TP.
    # Pour servir un LAN : remplacez par l'IP LAN du serveur,
    # puis ouvrez le port 53 (UDP/TCP) dans le pare-feu.
    interface: 127.0.0.1

    # On n'écoute que sur le port standard (53).
    port: 53

    # Access control : on autorise uniquement la machine locale.
    # Pour un LAN 192.168.1.0/24 :
    # access-control: 192.168.1.0/24 allow
    access-control: 127.0.0.1 allow
    access-control: ::1 allow

    # Désactive IPv6 si non utilisé dans le lab (accélère les tests).
    do-ip6: no

    # Active la récursivité pure (ne pas juste relayer).
    do-ip4: yes
    do-udp: yes
    do-tcp: yes

    # QNAME minimisation — réduit la quantité d'infos envoyées
    # aux serveurs faisant autorité (meilleur respect de la vie privée).
    qname-minimisation: yes

    # DNSSEC — validation activée par défaut sur Ubuntu via la
    # directive dans root-auto-trust-anchor.conf. On la force ici.
    module-config: "validator iterator"

    # Cache — taille mémoire du cache.
    num-threads: 1
    msg-cache-size: 32m
    rrset-cache-size: 64m

    # Journalisation modérée (utile en TP).
    verbosity: 1
    use-syslog: yes
    logfile: ""

# --- Racine ---
# Déclare où trouver les hints racines.
root-hints: "/var/lib/unbound/root.hints"

# --- Liens de confiance ---
# On désactive le forward par défaut : on partira de la racine.
# L'option inclue dans root-auto-trust-anchor.conf gère déjà DNSSEC.
```

!!! tip "Pour un lab sans réelle racine"
    Si votre réseau filtre le port 53 sortant (cas d'un TP cloisonné), ajoutez à la fin un bloc `forward-zone` qui pointe vers un résolveur public : Unbound fera alors office de **cache local** tout en gardant l'analyse DNSSEC.

    ```yaml
    forward-zone:
        name: "."
        forward-addr: 1.1.1.1
        forward-addr: 8.8.8.8
    ```

### Étape 5 : tester la syntaxe avant de démarrer

Unbound fournit un validateur de syntaxe — **utilisez-le systématiquement**, il évite de casser le service lors d'un redémarrage :

```bash
sudo unbound-checkconf
```

!!! success "Résultat attendu"
    `unbound-checkconf: no errors in /etc/unbound/unbound.conf` — la configuration est syntaxiquement valide.

### Étape 6 : démarrer et activer le service

```bash
sudo systemctl enable --now unbound
sudo systemctl restart unbound
sudo systemctl status unbound --no-pager
```

!!! success "Résultat attendu"
    Le service est **`active (running)`**, sans ligne `fail` ni erreur dans le journal. Le port 53 est désormais occupé par `unbound`.

### Étape 7 : libérer le port 53 de `systemd-resolved`

Sur Ubuntu 24.04, **`systemd-resolved`** écoute par défaut sur `127.0.0.53:53`. Ce n'est pas un conflit direct avec `127.0.0.1:53`, mais on va **faire pointer** `systemd-resolved` vers notre Unbound pour profiter du cache.

Vérifiez ce qui écoute sur le port 53 :

```bash
sudo ss -lntup | grep ':53'
```

On doit y voir `unbound` sur `127.0.0.1:53` et `systemd-resolved` sur `127.0.0.53:53`. C'est la configuration attendue.

Configurez maintenant `systemd-resolved` pour qu'il **passe par Unbound** :

```bash
sudo nano /etc/systemd/resolved.conf
```

Décommentez et adaptez les lignes suivantes :

```ini title="/etc/systemd/resolved.conf"
[Resolve]
DNS=127.0.0.1
FallbackDNS=
Domains=
DNSStubListener=yes
```

Puis relancez le service :

```bash
sudo systemctl restart systemd-resolved
```

### Étape 8 : faire pointer Netplan/Systemd directement vers 127.0.0.1

Vérifiez le résolveur actif via `resolvectl` :

```bash
resolvectl status
```

On doit voir `Current DNS Server: 127.0.0.1` sur l'interface principale (par exemple `ens18`).

Si ce n'est pas le cas, forcez le résolveur au niveau de l'interface :

```bash
sudo resolvectl dns ens18 127.0.0.1
```

!!! warning "Sur Netplan"
    Si votre Netplan gère le DNS explicitement (`nameservers: addresses: [...]`), ne mettez **plusieurs DNS**. Pointez uniquement vers **127.0.0.1**. Sinon `systemd-resolved` peut tour à tour interroger 127.0.0.1 et un DNS externe, ruining le bénéfice du cache.

## Vérification

### Test 1 : dig simple

```bash
dig example.com
```

!!! success "Résultat attendu"
    Dans la section `;; ANSWER SECTION:`, la colonne **flags** contient `ad` (authentic data = DNSSEC validé). L'heure de réponse (`Query time`) sur une ** Première résolution** se situe autour de **30 à 100 ms**.

### Test 2 : vérifier le cache

Relancez une fois la requête — le cache doit jouer :

```bash
dig example.com
```

!!! success "Résultat attendu"
    Sur cette **deuxième** requête, le `Query time` tombe à **0 ms** : la réponse sort du **cache local** d'Unbound, sans aucune interrogation réseau.

### Test 3 : validation DNSSEC explicite

Pour vérifier que la validation fonctionne, on interroge un domaine intentionnellement cassé :

```bash
dig dnssec-failed.org
```

!!! success "Résultat attendu"
    La réponse est **`SERVFAIL`** car la signature DNSSEC de ce domaine est volontairement cassée. Unbound la refuse — preuve que la validation DNSSEC est active.

### Test 4 : interrogation d'un record inconnu

```bash
dig +short NS .
```

On doit obtenir la liste des serveurs racines (`a.root-servers.net` à `m.root-servers.net`), preuve qu'Unbound interroge bien la **racine** et n'utilise pas un forward.

## Durcissement (aller plus loin)

### Activer le prefetching

Le prefetching permet à Unbound de **rafraîchir les enregistrements populaires** avant qu'ils n'expirerent du cache, ce qui réduit la latence moyennée côté client. Ajoutez dans votre bloc `server:` :

```yaml
server:
    prefetch: yes
    prefetch-key: yes
```

### Restreindre l'accès par interface (LAN)

Si vous servez un réseau local :

```yaml
server:
    interface: 192.168.1.10
    access-control: 192.168.1.0/24 allow
    access-control: 127.0.0.1 allow
```

Et **ouvrez le pare-feu** :

```bash
sudo ufw allow 53/udp
sudo ufw allow 53/tcp
```

### Combiner avec Pi-hole

Unbound est le compagnon idéal de [Pi-hole](installer-configurer-pi-hole-reseau-local.md) :

- Pi-hole gère le **bloqueur de publicité** ;
- Unbound fournit le **résolveur validateur**.

Pointez l'upstream DNS de Pi-hole sur `127.0.0.1#5335` (Unbound écoutant alors sur `5335`, Pi-hole gardant le `53`). Vous disposez alors d'un **DNS neutre, validateur, et sans publicité**.

!!! tip "Astuce de lab"
    Dans ce scénario, écoutez sur deux ports distincts pour éviter le conflit : Unbound sur `127.0.0.1@5335`, Pi-hole sur `0.0.0.0:53`.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `sudo unbound-checkconf` | Vérifie la syntaxe de la configuration avant redémarrage. |
| `sudo systemctl restart unbound` | Redémarre le service après modification de `unbound.conf`. |
| `dig example.com` | Test simple de résolution et lit le `Query time`. |
| `dig dnssec-failed.org` | Test de validation DNSSEC (doit renvoyer `SERVFAIL`). |
| `dig +short NS .` | Affiche les serveurs racines interrogés par Unbound. |
| `sudo ss -lntup \| grep ':53'` | Confirme qui écoute sur le port 53. |
| `resolvectl status` | Affiche le résolveur actif par interface. |
| `unbound-control stats` | Statistiques runtime (hits cache, débit) si contrôle local activé. |

## Glossaire

Résolveur (resolver)
:   Programme qui répond aux requêtes de noms de domaine en remontant la hiérarchie DNS depuis la racine jusqu'au serveur faisant autorité.

Cache DNS
:   Mémoire temporaire des réponses déjà obtenues, pour répondre instantanément sans refaire la récursion.

DNSSEC (DNS Security Extensions)
:   Extension de DNS qui **signe cryptographiquement** les réponses, détectant ainsi les falsifications et « man-in-the-middle ».

Root hints
:   Fichier listant les adresses IP des **13 serveurs racines**. Premier point de départ quand Unbound n'a encore rien en cache.

QNAME minimisation
:   Technique qui **réduit** la quantité d'informations transmises aux serveurs faisant autorité (meilleur respect de la vie privée).

Forwarder
:   Mode où Unbound **relaye** les requêtes vers un autre résolveur plutôt que d'interroger la racine. Utile quand le réseau du lab filtre le port 53 sortant.

## Checklist

- [x] `unbound` et `dnsutils` installés.
- [x] `root.hints` téléchargé dans `/var/lib/unbound/`.
- [x] Configuration personnalisée en place et validée par `unbound-checkconf`.
- [x] Service `unbound` **`active (running)`**.
- [x] `systemd-resolved` repointé sur `127.0.0.1`.
- [x] Le cache est vérifié : `Query time: 0 msec` sur la deuxième requête.
- [x] La validation DNSSEC est confirmée (`dnssec-failed.org` → `SERVFAIL`).

## Ressources

- [Documentation officielle Unbound — NLnet Labs](https://unbound.docs.nlnetlabs.nl/en/latest/) — Documentation de référence du résolveur, options et tutoriels.
- [Guide DNS pour serveurs — Ubuntu Server](https://ubuntu.com/server/docs/how-to/networking/install-dns/) — Démarche officielle Ubuntu pour déployer un service DNS (orientée BIND9, à adapter pour Unbound).
- [RFC 8499 — DNS Terminology](https://www.rfc-editor.org/rfc/rfc8499.html) — Terminologie normalisée des concepts DNS (récursif, cache, etc.).
- [ICANN — Root Servers](https://www.icann.org/) — Présentation de la racine DNS et des 13 serveurs.
- [IANA — Root hints](https://www.internic.net/domain/named.root) — Source officielle du fichier `root.hints` utilisé dans ce tutoriel.
