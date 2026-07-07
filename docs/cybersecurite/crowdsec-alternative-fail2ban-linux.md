---
title: Protéger un serveur Linux avec CrowdSec
date: 2026-06-22
author: Nicolas BODAINE
tags:
  - securite
  - crowdsec
  - fail2ban
  - firewall
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Protéger un serveur Linux avec CrowdSec : l'alternative collaborative à Fail2ban

!!! abstract "Résumé"
    CrowdSec est un système de détection d'intrusion (IDS) open-source et collaboratif. Contrairement à Fail2ban qui travaille seul dans son coin, CrowdSec partage les adresses IP malveillantes avec toute sa communauté. Si une IP attaque un autre utilisateur de CrowdSec dans le monde, elle sera bloquée sur votre serveur avant même de vous atteindre.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-22 |

## Contexte

Historiquement, l'outil de référence pour protéger un serveur des attaques par force brute (notamment sur SSH) est Fail2ban. Il analyse les logs locaux et bloque les attaquants. Cependant, les attaquants utilisent de plus en plus de botnets avec des milliers d'IP différentes, rendant la détection purement locale de moins en moins efficace. 

CrowdSec résout ce problème avec une approche communautaire (CTI - *Cyber Threat Intelligence*). Il analyse vos logs pour détecter les comportements malveillants, bloque les attaques, mais surtout, il télécharge les listes d'IPs bloquées par la communauté pour anticiper les attaques.

## Prérequis

- Un serveur sous Ubuntu 24.04 (ou Debian/autre distribution compatible).
- Accès `root` ou privilèges `sudo`.
- Le pare-feu UFW ou `iptables` actif sur le serveur.

## Procédure

### Étape 1 : Installation de CrowdSec

CrowdSec fournit son propre dépôt officiel, ce qui permet d'avoir toujours la dernière version.

```bash
# Ajouter le dépôt officiel de CrowdSec
curl -s https://install.crowdsec.net | sudo bash

# Installer CrowdSec
sudo apt update
sudo apt install -y crowdsec
```

Une fois installé, CrowdSec détecte automatiquement les services courants présents sur votre machine (comme SSH ou Nginx) et installe les "collections" (règles de détection) correspondantes.

### Étape 2 : Vérification de l'installation

Vérifiez que le service est bien actif :

```bash
sudo systemctl status crowdsec
```

!!! success "Résultat attendu"
    Le service doit être indiqué comme `active (running)`.

Vous pouvez ensuite utiliser la commande CLI de CrowdSec (nommée `cscli`) pour voir ce qui a été détecté et configuré automatiquement. Par exemple, pour lister les "collections" actives :

```bash
sudo cscli collections list
```

Vous devriez voir `crowdsecurity/linux` et `crowdsecurity/sshd`.

### Étape 3 : Installation du "Bouncer" (Remédiation)

**Attention :** CrowdSec seul se contente de *détecter* les attaques. Pour qu'il puisse *bloquer* les IPs (la remédiation), il faut installer un "Bouncer".

Dans le cas d'un serveur Linux standard, nous allons installer le bouncer pour pare-feu, qui va créer des règles `iptables` ou `nftables` pour bloquer le trafic.

```bash
# Installer le bouncer pour pare-feu
sudo apt install -y crowdsec-firewall-bouncer-iptables
```

Le service du bouncer démarre automatiquement. Vérifiez son statut :

```bash
sudo systemctl status crowdsec-firewall-bouncer
```

### Étape 4 : Visualiser l'activité et les alertes

Pour voir les alertes locales et les IPs actuellement bloquées, utilisez la commande suivante :

```bash
sudo cscli decisions list
```

!!! note "L'avantage collaboratif"
    Cette commande n'affiche que les décisions prises localement (si quelqu'un attaque votre serveur). En arrière-plan, le bouncer charge également la liste communautaire (des milliers d'IPs), que vous ne voyez pas dans ce tableau local, mais qui sont bien bloquées !

## Aide-mémoire cscli

Voici les commandes `cscli` les plus utiles au quotidien :

| Commande | Description |
|----------|-------------|
| `sudo cscli decisions list` | Liste les IPs bloquées localement |
| `sudo cscli decisions delete -i <IP>` | Débloque une adresse IP spécifique |
| `sudo cscli decisions add -i <IP>` | Banni manuellement une adresse IP |
| `sudo cscli metrics` | Affiche les statistiques (logs lus, IPs bannies, etc.) |
| `sudo cscli hub update` | Met à jour le catalogue des règles |
| `sudo cscli hub upgrade` | Met à jour les règles actuellement installées |

## Vérification

Pour vérifier que le pare-feu applique bien les règles de CrowdSec, vous pouvez lister les règles de votre pare-feu local, ou vérifier via le bouncer :

```bash
sudo cscli bouncers list
```

!!! success "Résultat attendu"
    Vous verrez `crowdsec-firewall-bouncer` avec la mention `valid` (✅), ce qui confirme que le composant de blocage est connecté au composant de détection.

Pour un test plus direct, vous pouvez bannir manuellement une IP (par exemple `1.2.3.4`) puis l'enlever :

```bash
# Banni l'IP
sudo cscli decisions add -i 1.2.3.4
# Vérifie qu'elle est listée
sudo cscli decisions list
# Débanni l'IP
sudo cscli decisions delete -i 1.2.3.4
```

## Ressources

- [Documentation officielle de CrowdSec](https://docs.crowdsec.net/) — Installation, configuration et utilisation avancée.
- [GitHub de CrowdSec](https://github.com/crowdsecurity/crowdsec) — Code source et annonces de versions.
