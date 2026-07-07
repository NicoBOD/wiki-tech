---
title: "Installer et configurer Fail2ban pour protéger SSH sur Ubuntu Server 24.04"
date: 2026-05-30
author: Nicolas BODAINE
tags:
  - ubuntu
  - fail2ban
  - ssh
  - sshd
  - securite
  - brute-force
difficulty: débutant
os: Ubuntu Server 24.04
status: publié
---

# Installer et configurer Fail2ban pour protéger SSH sur Ubuntu Server 24.04

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour installer **Fail2ban** sur **Ubuntu Server 24.04**, activer la protection du service **SSH**, vérifier qu'une jail fonctionne correctement et savoir débannir une adresse IP pendant un TP ou un lab.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu Server 24.04 |
| Dernière mise à jour | 2026-05-30 |

## Contexte

Quand un serveur SSH est exposé, même dans un petit lab, il reçoit souvent des tentatives de connexion ratées.
Cela peut venir :

- d'erreurs de mot de passe répétées ;
- de scans automatiques ;
- de robots qui testent des identifiants courants ;
- d'un stagiaire qui oublie quel compte il doit utiliser.

**Fail2ban** surveille les journaux système et bannit temporairement une adresse IP quand trop d'échecs sont détectés.

Dans ce TP, l'objectif est simple :

- installer `fail2ban` ;
- activer une **jail `sshd`** ;
- définir des seuils faciles à comprendre ;
- vérifier que la protection fonctionne ;
- savoir retirer un bannissement si besoin.

## Prérequis

- Une VM ou un serveur de test sous **Ubuntu Server 24.04**
- Un compte avec les droits `sudo`
- Le service **OpenSSH Server** installé et démarré
- Idéalement une **deuxième machine** ou une autre VM pour faire les tests SSH

!!! warning "Ne modifiez pas `jail.conf` directement"
    La documentation Fail2ban recommande de faire ses personnalisations dans **`jail.local`** ou dans des fichiers **`.local`** sous **`/etc/fail2ban/jail.d/`**.
    C'est plus propre et cela évite d'écraser vos réglages lors d'une mise à jour.

## Procédure

### Étape 1 : vérifier que SSH fonctionne déjà

Avant de protéger SSH, commencez par confirmer que le service existe et écoute bien.

```bash
systemctl status ssh --no-pager
ss -tulpn | grep ':22'
```

Si OpenSSH Server n'est pas encore installé :

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

!!! success "Résultat attendu"
    Le service `ssh` doit être **actif** et le port `22/tcp` doit apparaître à l'écoute.

### Étape 2 : installer Fail2ban

Installez le paquet depuis les dépôts Ubuntu :

```bash
sudo apt update
sudo apt install -y fail2ban
```

Vérifiez ensuite l'état du service :

```bash
systemctl status fail2ban --no-pager
```

Vous pouvez aussi tester la communication avec le client Fail2ban :

```bash
sudo fail2ban-client ping
```

!!! success "Résultat attendu"
    La commande `fail2ban-client ping` doit répondre `Server replied: pong`.

### Étape 3 : repérer les fichiers de configuration utiles

Sur Ubuntu, les emplacements à connaître sont :

- `/etc/fail2ban/jail.conf` : configuration par défaut du paquet ;
- `/etc/fail2ban/jail.local` : surcharge locale globale ;
- `/etc/fail2ban/jail.d/*.local` : surcharges locales plus ciblées.

Pour un TP simple et lisible, nous allons créer un fichier dédié à SSH.

```bash
sudo mkdir -p /etc/fail2ban/jail.d
```

### Étape 4 : créer une jail pour `sshd`

Créez le fichier `/etc/fail2ban/jail.d/sshd.local` :

```bash
sudo nano /etc/fail2ban/jail.d/sshd.local
```

Collez le contenu suivant :

```ini
[sshd]
enabled = true
backend = systemd
port = ssh
maxretry = 5
findtime = 10m
bantime = 1h
```

### Comprendre les paramètres

- `enabled = true` : active la jail `sshd` ;
- `backend = systemd` : lit les événements depuis le journal systemd ;
- `port = ssh` : cible le service SSH ;
- `maxretry = 5` : bannissement après **5 échecs** ;
- `findtime = 10m` : les 5 échecs doivent se produire dans les **10 minutes** ;
- `bantime = 1h` : l'adresse IP est bannie pendant **1 heure**.

!!! tip "Pourquoi `backend = systemd` ?"
    Sur Ubuntu Server 24.04, cette approche est pratique et robuste pour surveiller les événements de `sshd` sans dépendre d'un chemin de fichier de log particulier.

### Étape 5 : redémarrer Fail2ban et activer le démarrage automatique

Rechargez la configuration puis activez le service au boot :

```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

Vérifiez ensuite son état :

```bash
systemctl status fail2ban --no-pager
```

Si vous voulez lire les derniers messages du service :

```bash
sudo journalctl -u fail2ban -n 30 --no-pager
```

### Étape 6 : vérifier que la jail `sshd` est bien chargée

Affichez d'abord la liste générale des jails actives :

```bash
sudo fail2ban-client status
```

Puis contrôlez la jail SSH précisément :

```bash
sudo fail2ban-client status sshd
```

Exemple de résultat attendu :

```text
Status for the jail: sshd
|- Filter
|  |- Currently failed: 0
|  |- Total failed: 0
|  `- Journal matches: ...
`- Actions
   |- Currently banned: 0
   |- Total banned: 0
   `- Banned IP list:
```

!!! success "Résultat attendu"
    La jail `sshd` doit apparaître dans la sortie de `fail2ban-client status`.

### Étape 7 : tester le fonctionnement en lab

Depuis une autre machine du lab, essayez plusieurs connexions SSH volontairement erronées.

Exemple :

```bash
ssh mauvais_utilisateur@IP_DU_SERVEUR
```

Entrez un mauvais mot de passe plusieurs fois, puis recommencez jusqu'à dépasser le seuil configuré.

Ensuite, sur le serveur protégé, contrôlez l'état :

```bash
sudo fail2ban-client status sshd
```

Vous pouvez aussi regarder les événements récents :

```bash
sudo journalctl -u fail2ban -n 50 --no-pager
```

!!! success "Résultat attendu"
    Après plusieurs échecs rapprochés, l'adresse IP de la machine de test doit apparaître dans `Banned IP list`.

### Étape 8 : débannir une adresse IP si nécessaire

En TP, il est fréquent de se bannir soi-même en faisant les tests.

Pour retirer manuellement une IP de la jail `sshd` :

```bash
sudo fail2ban-client set sshd unbanip IP_A_DEBANNIR
```

Exemple :

```bash
sudo fail2ban-client set sshd unbanip 192.168.1.50
```

Vérifiez ensuite :

```bash
sudo fail2ban-client status sshd
```

### Étape 9 : ajuster le niveau de tolérance

Une fois le premier TP réussi, vous pouvez adapter le comportement de Fail2ban.

Exemple plus strict :

```ini
[sshd]
enabled = true
backend = systemd
port = ssh
maxretry = 3
findtime = 10m
bantime = 24h
```

Après chaque modification du fichier `.local`, redémarrez le service :

```bash
sudo systemctl restart fail2ban
```

!!! note "Bon réflexe"
    Commencez par une configuration simple et compréhensible avant de durcir fortement les seuils.
    En environnement pédagogique, il vaut mieux voir clairement ce qui se passe plutôt que de rendre le diagnostic trop compliqué.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `sudo apt install -y fail2ban` | Installer Fail2ban |
| `systemctl status fail2ban --no-pager` | Vérifier l'état du service |
| `sudo fail2ban-client ping` | Tester la communication avec le serveur Fail2ban |
| `sudo fail2ban-client status` | Lister les jails actives |
| `sudo fail2ban-client status sshd` | Afficher le détail de la jail SSH |
| `sudo journalctl -u fail2ban -n 50 --no-pager` | Lire les derniers journaux Fail2ban |
| `sudo systemctl restart fail2ban` | Recharger la configuration |
| `sudo fail2ban-client set sshd unbanip IP` | Débannir une adresse IP |

## Vérification

Après la configuration, contrôlez les points suivants.

### 1. Le service Fail2ban est actif

```bash
systemctl is-active fail2ban
```

!!! success "Résultat attendu"
    La commande doit retourner `active`.

### 2. La jail `sshd` est chargée

```bash
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

!!! success "Résultat attendu"
    La jail `sshd` doit être listée et ne pas remonter d'erreur.

### 3. Une IP peut être bannie après plusieurs échecs

```bash
sudo fail2ban-client status sshd
```

!!! success "Résultat attendu"
    En cas de test de connexion raté répété dans le lab, l'IP source doit apparaître dans `Banned IP list`.

## Checklist

- [x] OpenSSH vérifié ou installé
- [x] Fail2ban installé
- [x] Fichier `.local` créé sans modifier `jail.conf`
- [x] Jail `sshd` activée
- [x] Service redémarré et activé au démarrage
- [x] Vérification de `fail2ban-client status sshd`
- [x] Procédure de débannissement connue

## Glossaire

`Fail2ban`
:   Outil de protection qui surveille des journaux et bannit temporairement des adresses IP après trop d'échecs.

`Jail`
:   Bloc de configuration Fail2ban associant un service, un filtre et une action de bannissement.

`sshd`
:   Service serveur SSH utilisé pour l'administration distante des machines Linux.

`backend`
:   Méthode utilisée par Fail2ban pour lire les événements, par exemple `systemd` ou un fichier de log.

`bantime`
:   Durée pendant laquelle l'adresse IP reste bannie.

## Ressources

- [Fail2ban — How Fail2Ban Works](https://github.com/fail2ban/fail2ban/wiki/How-Fail2Ban-Works) — Explication officielle du fonctionnement général
- [Manpage Ubuntu `jail.conf(5)`](https://manpages.ubuntu.com/manpages/noble/man5/jail.conf.5.html) — Référence sur `jail.conf`, `jail.local` et les paramètres des jails
- [Manpage Ubuntu `fail2ban-client(1)`](https://manpages.ubuntu.com/manpages/noble/man1/fail2ban-client.1.html) — Commandes de contrôle, statut et débannissement
