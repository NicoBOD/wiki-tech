---
title: "Diagnostiquer une panne DNS avec `dig`, `host` et `resolvectl` sur Ubuntu"
date: 2026-06-02
author: Nicolas BODAINE
tags:
  - dns
  - dig
  - host
  - resolvectl
  - ubuntu
  - diagnostic
difficulty: débutant
os: Ubuntu Server 24.04
status: publié
---

# Diagnostiquer une panne DNS avec `dig`, `host` et `resolvectl` sur Ubuntu

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour **identifier rapidement si une panne vient vraiment du DNS** ou d'un autre problème réseau sur **Ubuntu**. Nous allons utiliser une méthode simple avec **`ping`**, **`resolvectl`**, **`dig`** et **`host`** pour tester la connectivité IP, voir quels serveurs DNS sont utilisés, interroger un résolveur précis et interpréter les résultats.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu Server 24.04 |
| Dernière mise à jour | 2026-06-02 |

## Contexte

Quand « Internet ne marche pas » ou qu'un serveur « ne résout plus les noms », le problème n'est pas toujours le DNS.
En pratique, on rencontre souvent plusieurs cas différents :

- l'interface réseau n'a pas la bonne adresse IP ;
- la passerelle par défaut n'est pas correcte ;
- le serveur DNS configuré n'est pas joignable ;
- le résolveur local utilise un mauvais DNS ;
- le nom demandé n'existe pas réellement dans la zone DNS ;
- seul un résolveur précis répond, mais pas celui configuré sur la machine.

Dans un TP, le plus important n'est pas seulement de « relancer le réseau », mais de **savoir isoler la panne**.
Une bonne démarche de diagnostic permet de répondre clairement à ces questions :

1. la machine a-t-elle bien une connectivité IP ?
2. le résolveur local connaît-il les bons DNS ?
3. une requête DNS fonctionne-t-elle avec le DNS courant ?
4. la même requête fonctionne-t-elle si l'on vise directement un autre serveur DNS ?
5. le problème vient-il du réseau, du résolveur local, ou du serveur DNS interrogé ?

!!! tip "Complément utile"
    Si vous découvrez que le problème vient de la configuration réseau ou des serveurs DNS déclarés dans Netplan, vous pouvez compléter avec l'article [Configurer une adresse IP statique avec Netplan sur Ubuntu Server 24.04](configurer-ip-statique-netplan-ubuntu-server.md).

### Lab de démonstration

| Élément | Exemple |
|---------|---------|
| Machine test | `ubuntu-lab-01` |
| Interface réseau | `ens18` |
| Test IP | `1.1.1.1` |
| Nom de test | `example.com` |
| DNS externes de comparaison | `1.1.1.1` et `8.8.8.8` |

!!! note "Adaptez à votre environnement"
    Dans un lab d'entreprise, remplacez `1.1.1.1` et `8.8.8.8` par les **DNS internes autorisés**.
    L'important n'est pas le DNS choisi, mais la logique de comparaison entre **résolveur local** et **serveur DNS ciblé explicitement**.

## Prérequis

- Une VM ou un serveur Ubuntu de test
- Un compte avec les droits `sudo`
- Une connectivité réseau minimale vers votre passerelle ou vers Internet
- Le nom de l'interface réseau principale, par exemple `ens18`
- Un nom de domaine de test stable, par exemple `example.com`

!!! note "À propos des outils"
    Sur Ubuntu, **`resolvectl`** est généralement déjà disponible avec `systemd`.
    Si `dig` et `host` ne sont pas installés, nous les ajouterons dans la procédure avec le paquet `dnsutils`.

## Procédure

### Étape 1 : vérifier si le problème est vraiment lié au DNS

Commencez par distinguer un problème **IP** d'un problème **DNS**.

```bash
ping -c 2 1.1.1.1
ping -c 2 example.com
```

### Comment interpréter ce test ?

- si `ping 1.1.1.1` **échoue**, le problème n'est probablement **pas d'abord DNS** ;
- si `ping 1.1.1.1` **fonctionne** mais `ping example.com` **échoue**, le DNS devient un suspect sérieux ;
- si les deux fonctionnent, le problème est peut-être intermittent ou lié à une application précise.

!!! success "Résultat attendu"
    Vous devez savoir dès cette étape si la machine sait au moins **sortir en IP**.

### Étape 2 : contrôler l'adresse IP et la route par défaut

Avant d'accuser le DNS, vérifiez que la machine a bien une configuration réseau cohérente.

```bash
ip -br addr
ip route
```

Exemple de lecture :

```text
lo               UNKNOWN        127.0.0.1/8 ::1/128
ens18            UP             192.168.56.20/24
```

et :

```text
default via 192.168.56.1 dev ens18
192.168.56.0/24 dev ens18 proto kernel scope link src 192.168.56.20
```

Si l'interface n'a pas d'adresse utile, ou si la route par défaut pointe vers une mauvaise passerelle, vos requêtes DNS risquent d'échouer simplement parce que la machine ne sait pas joindre le réseau.

### Étape 3 : afficher les DNS vus par le système avec `resolvectl`

Sur Ubuntu récent, `resolvectl` permet de voir l'état du résolveur système et les DNS utilisés par interface.

```bash
resolvectl status
```

Regardez en particulier :

- l'interface réseau active ;
- la section **DNS Servers** ;
- l'éventuel **DNS Domain** ou suffixe de recherche ;
- la présence du service `systemd-resolved`.

Vous pouvez compléter avec :

```bash
systemctl status systemd-resolved --no-pager
ls -l /etc/resolv.conf
cat /etc/resolv.conf
```

### Ce qu'il faut comprendre

Sur Ubuntu, `/etc/resolv.conf` pointe souvent vers un résolveur local, par exemple `127.0.0.53`.
Ce n'est pas forcément une erreur : cela signifie souvent que **`systemd-resolved`** joue le rôle d'intermédiaire local et relaie ensuite les requêtes vers les vrais DNS configurés.

!!! warning "Ne concluez pas trop vite"
    Voir `127.0.0.53` dans `/etc/resolv.conf` n'indique pas, à lui seul, une panne DNS.
    Il faut surtout vérifier dans `resolvectl status` **quels serveurs DNS réels** sont utilisés derrière ce résolveur local.

### Étape 4 : installer `dig` et `host` si nécessaire

Vérifiez d'abord si les outils sont déjà présents :

```bash
command -v dig
command -v host
```

S'ils ne sont pas trouvés, installez-les :

```bash
sudo apt update
sudo apt install -y dnsutils
```

Puis revérifiez :

```bash
command -v dig
command -v host
```

!!! success "Résultat attendu"
    Les commandes `dig` et `host` doivent maintenant être disponibles sur la machine.

### Étape 5 : interroger le DNS actuellement utilisé par la machine

Faites une requête simple vers un nom connu.

```bash
dig example.com A
```

Version plus concise :

```bash
dig example.com A +short
```

Faites ensuite le même test avec `host` :

```bash
host example.com
```

Et enfin avec `resolvectl` :

```bash
resolvectl query example.com
```

### Interpréter les résultats

- si `dig`, `host` et `resolvectl query` répondent correctement, la résolution fonctionne ;
- si `dig example.com` retourne un **timeout**, le serveur DNS configuré n'est peut-être pas joignable ;
- si la réponse est **NXDOMAIN**, le nom demandé n'existe probablement pas ;
- si la réponse est **SERVFAIL**, le résolveur interrogé a rencontré un problème lors du traitement de la requête.

Exemple de sortie courte attendue :

```text
93.184.216.34
```

### Étape 6 : viser directement un serveur DNS précis avec `dig`

C'est l'étape clé pour isoler la panne.
Si la requête échoue avec la configuration courante, interrogez un DNS précis avec `@serveur`.

```bash
dig @1.1.1.1 example.com A +short
dig @8.8.8.8 example.com A +short
```

Vous pouvez aussi faire le même test avec `host` :

```bash
host example.com 1.1.1.1
```

### Comment lire ce résultat ?

- si `dig example.com` échoue mais `dig @1.1.1.1 example.com` fonctionne, le souci vient souvent du **DNS configuré localement** ou du **résolveur système** ;
- si les deux échouent, le problème peut venir du réseau, d'un filtrage, ou du domaine testé ;
- si seul un DNS répond et pas l'autre, le comportement du serveur DNS interrogé devient le point d'analyse principal.

!!! tip "Méthode terrain"
    Toujours comparer une requête DNS via la **configuration locale** puis via un **serveur explicitement désigné** est l'une des façons les plus rapides d'isoler la source d'une panne.

### Étape 7 : tester une résolution inverse

Le DNS ne sert pas seulement à transformer un nom en adresse IP.
Il peut aussi tenter une résolution **inverse** (reverse lookup).

```bash
dig -x 1.1.1.1 +short
host 1.1.1.1
```

Ce test est utile pour comprendre :

- la différence entre résolution **directe** et **inverse** ;
- qu'une machine peut parfois être joignable en IP sans avoir d'enregistrement PTR pertinent ;
- que l'absence de reverse DNS n'empêche pas forcément le service de fonctionner, mais peut compliquer certains diagnostics.

### Étape 8 : vider le cache DNS local après une correction

Après avoir corrigé une configuration réseau ou DNS, vous pouvez purger le cache local du résolveur :

```bash
sudo resolvectl flush-caches
```

Puis relancez immédiatement un test :

```bash
resolvectl query example.com
dig example.com A +short
```

Cela évite d'interpréter à tort une ancienne réponse mise en cache.

## Vérification

Une fois le diagnostic terminé ou la configuration corrigée, vérifiez l'ensemble avec cette séquence courte :

```bash
ping -c 2 1.1.1.1
resolvectl status
dig example.com A +short
host example.com
resolvectl query example.com
```

Vous devez confirmer que :

- la connectivité IP fonctionne ;
- les DNS attendus apparaissent dans `resolvectl status` ;
- `dig`, `host` et `resolvectl query` retournent une réponse cohérente ;
- les requêtes ne restent pas bloquées en timeout.

!!! success "Résultat attendu"
    Vous êtes capable de dire clairement si la panne venait de la **connectivité réseau**, du **résolveur local**, ou du **serveur DNS interrogé**.

## Problèmes fréquents

### Cas 1 : `ping 1.1.1.1` échoue aussi

Ce n'est généralement **pas un problème DNS en premier lieu**.
Commencez par vérifier :

- l'adresse IP de l'interface ;
- la passerelle par défaut ;
- le VLAN ou le réseau virtuel utilisé ;
- un éventuel pare-feu ou filtrage sortant.

### Cas 2 : `dig @1.1.1.1 example.com` fonctionne, mais pas `dig example.com`

Le chemin réseau fonctionne probablement.
Le souci est alors souvent lié à :

- un mauvais DNS déclaré côté réseau ;
- un problème avec `systemd-resolved` ;
- une configuration incohérente dans Netplan ou via DHCP.

### Cas 3 : `resolvectl status` n'affiche pas le DNS attendu

La machine n'utilise peut-être pas les bons serveurs DNS.
Sur Ubuntu Server, il faut souvent vérifier la configuration réseau appliquée par Netplan.

### Cas 4 : le nom court ne fonctionne pas, mais le FQDN fonctionne

Exemple : `ping srv01` échoue mais `ping srv01.lab.local` fonctionne.
Dans ce cas, le problème vient souvent du **suffixe de recherche DNS** (*search domain*).

### Cas 5 : la réponse change selon le serveur interrogé

Cela peut arriver avec :

- des DNS internes et externes différents ;
- un split-DNS en entreprise ;
- une zone non répliquée partout ;
- une panne partielle sur un seul résolveur.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `ip -br addr` | Afficher rapidement les adresses IP des interfaces |
| `ip route` | Vérifier la route par défaut |
| `resolvectl status` | Voir les DNS utilisés par le système |
| `dig example.com A` | Faire une requête DNS détaillée |
| `dig example.com A +short` | Obtenir seulement la réponse utile |
| `dig @1.1.1.1 example.com A +short` | Tester un serveur DNS précis |
| `dig -x 1.1.1.1 +short` | Faire une résolution inverse |
| `host example.com` | Requête DNS simple et lisible |
| `resolvectl query example.com` | Interroger le résolveur système |
| `sudo resolvectl flush-caches` | Vider le cache DNS local |

## Glossaire

`DNS`
:   Système qui associe des noms comme `example.com` à des adresses IP.

`Résolveur`
:   Service ou serveur qui reçoit une requête DNS et tente d'y répondre.

`FQDN`
:   *Fully Qualified Domain Name*, c'est-à-dire un nom complet comme `srv01.lab.local`.

`PTR`
:   Enregistrement DNS utilisé pour la résolution inverse, de l'adresse IP vers un nom.

`NXDOMAIN`
:   Réponse indiquant que le nom demandé n'existe pas dans le DNS interrogé.

`SERVFAIL`
:   Réponse indiquant qu'un problème est survenu côté résolveur lors du traitement de la requête.

## Ressources

- [Ubuntu Manpages — `dig(1)`](https://manpages.ubuntu.com/manpages/noble/man1/dig.1.html) — Référence de l'outil `dig`
- [Ubuntu Manpages — `host(1)`](https://manpages.ubuntu.com/manpages/noble/man1/host.1.html) — Référence de l'outil `host`
- [Ubuntu Manpages — `resolvectl(1)`](https://manpages.ubuntu.com/manpages/noble/man1/resolvectl.1.html) — Référence pour interroger et diagnostiquer le résolveur système
- [BIND 9 Manual Pages](https://bind9.readthedocs.io/en/latest/manpages.html) — Documentation de référence autour des outils DNS BIND
- [Ubuntu Server documentation — Set up a name server (DNS)](https://documentation.ubuntu.com/server/how-to/networking/install-dns/) — Documentation Ubuntu sur les services DNS côté serveur
