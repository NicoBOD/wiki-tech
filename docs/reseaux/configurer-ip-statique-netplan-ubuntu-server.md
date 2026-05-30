---
title: Configurer une adresse IP statique avec Netplan sur Ubuntu Server 24.04
date: 2026-05-30
author: Nicolas BODAINE
tags:
  - ubuntu
  - netplan
  - reseau
  - ip-statique
  - dns
difficulty: débutant
os: Ubuntu Server 24.04
status: publié
---

# Configurer une adresse IP statique avec Netplan sur Ubuntu Server 24.04

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour remplacer une configuration DHCP par une **adresse IP statique** sur **Ubuntu Server 24.04** avec **Netplan**, puis vérifier correctement l'adresse, la passerelle par défaut et les serveurs DNS.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu Server 24.04 |
| Dernière mise à jour | 2026-05-30 |

## Contexte

Dans un lab, une machine virtuelle récupère souvent son adresse IP en **DHCP**.
C'est pratique pour démarrer, mais ce n'est pas toujours adapté :

- un serveur DNS, web ou proxy doit souvent garder la **même adresse** ;
- une VM d'administration est plus simple à retrouver avec une IP fixe ;
- certaines règles de pare-feu, redirections NAT ou scripts supposent une adresse stable.

Sur Ubuntu Server, la configuration réseau moderne passe en général par **Netplan**.
Netplan lit des fichiers YAML dans `/etc/netplan/`, puis génère la configuration du backend réseau utilisé, souvent `systemd-networkd` sur un serveur.

L'objectif du TP est simple :

- repérer l'interface réseau correcte ;
- sauvegarder la configuration actuelle ;
- définir une adresse IP statique, une passerelle et des DNS ;
- tester sans se couper l'accès ;
- valider le résultat.

!!! warning "Point important si vous êtes connecté en SSH"
    Faites ce TP de préférence depuis la **console de la VM** ou en gardant une **session de secours** ouverte.
    La commande `netplan try` est justement faite pour éviter de se verrouiller hors du serveur en cas d'erreur réseau.

## Prérequis

- Une VM ou un serveur de test sous **Ubuntu Server 24.04**
- Un compte avec les droits `sudo`
- Une plage IP connue sur votre réseau local
- Les informations suivantes :
  - l'adresse IP souhaitée, par exemple `192.168.1.50/24`
  - la passerelle par défaut, par exemple `192.168.1.1`
  - un ou plusieurs DNS, par exemple `1.1.1.1` et `8.8.8.8`

!!! tip "Exemple utilisé dans ce tutoriel"
    Dans les exemples ci-dessous, j'utilise :
    
    - IP : `192.168.1.50/24`
    - passerelle : `192.168.1.1`
    - DNS : `1.1.1.1` et `8.8.8.8`
    - interface réseau : `ens18`
    
    **Adaptez ces valeurs à votre lab.**

## Procédure

### Étape 1 : identifier l'interface réseau et l'adressage actuel

Commencez par repérer le nom réel de l'interface réseau.

```bash
ip -br link
ip -br addr
ip route
```

Exemple de lecture :

```text
lo               UNKNOWN        127.0.0.1/8 ::1/128
ens18            UP             192.168.1.23/24
```

Dans cet exemple, l'interface utile est **`ens18`**.

!!! note "Pourquoi cette étape est indispensable"
    Sur Ubuntu Server, l'interface ne s'appelle pas toujours `eth0`.
    On rencontre souvent `ens18`, `ens160`, `enp1s0` ou d'autres noms prévisibles.

### Étape 2 : repérer le fichier Netplan actuel

Affichez les fichiers présents dans `/etc/netplan/` :

```bash
sudo find /etc/netplan -maxdepth 1 -type f -name '*.yaml' -print
```

Vous verrez souvent un fichier comme :

```text
/etc/netplan/50-cloud-init.yaml
```

ou :

```text
/etc/netplan/01-netcfg.yaml
```

Affichez ensuite son contenu :

```bash
sudo cat /etc/netplan/50-cloud-init.yaml
```

Exemple fréquent avec DHCP :

```yaml
network:
  version: 2
  ethernets:
    ens18:
      dhcp4: true
```

!!! tip "Bon réflexe"
    Pour un premier TP, modifiez le **fichier déjà utilisé** par le système au lieu d'en créer plusieurs.
    Cela évite les conflits entre plusieurs fichiers YAML Netplan.

### Étape 3 : sauvegarder la configuration actuelle

Avant toute modification, créez une sauvegarde.

```bash
sudo cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.bak
```

Vérifiez la présence de la copie :

```bash
sudo find /etc/netplan -maxdepth 1 -type f \( -name '*.yaml' -o -name '*.bak' \) -print
```

### Étape 4 : écrire la configuration IP statique

Éditez le fichier Netplan avec votre éditeur préféré :

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Remplacez le contenu par une configuration de ce type :

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens18:
      dhcp4: false
      addresses:
        - 192.168.1.50/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8
        search:
          - lab.local
```

### Explication rapide du fichier

- `ens18` : nom de l'interface à configurer
- `dhcp4: false` : on désactive le DHCP IPv4
- `addresses` : adresse IP statique et masque CIDR
- `routes` : route par défaut vers la passerelle
- `nameservers` : serveurs DNS utilisés pour la résolution de noms
- `search` : suffixe DNS facultatif pour le lab

!!! warning "Respectez l'indentation YAML"
    YAML est sensible aux espaces.
    N'utilisez pas de tabulations et gardez une indentation régulière de 2 espaces.

!!! note "À propos de `gateway4`"
    Vous verrez encore beaucoup d'exemples avec `gateway4`.
    La documentation Netplan indique que cette syntaxe est **dépréciée**.
    Pour un nouveau tutoriel, il est plus propre d'utiliser la section `routes` avec `to: default`.

### Étape 5 : vérifier la syntaxe avant d'appliquer

Demandez à Netplan de générer la configuration sans l'appliquer immédiatement :

```bash
sudo netplan generate
```

Si la syntaxe est correcte, la commande ne renvoie généralement rien.

En cas d'erreur d'indentation ou de clé mal écrite, corrigez le fichier puis relancez la commande.

### Étape 6 : tester sans se couper l'accès avec `netplan try`

La méthode la plus sûre consiste à utiliser :

```bash
sudo netplan try
```

Cette commande applique temporairement la configuration puis vous demande de la confirmer.
Si vous ne confirmez pas dans le délai prévu, Netplan tente de revenir en arrière.

!!! success "Pourquoi `netplan try` est précieux"
    D'après la documentation officielle de `netplan-try`, la configuration est automatiquement annulée si l'utilisateur ne la confirme pas dans le délai imparti.
    C'est très utile sur un serveur distant pour éviter une coupure réseau définitive après une erreur.

Si le test est concluant, confirmez la configuration quand Netplan le demande.

### Étape 7 : appliquer la configuration de façon classique

Si vous travaillez en console locale, ou après un test concluant, vous pouvez appliquer la configuration :

```bash
sudo netplan apply
```

Ensuite, contrôlez immédiatement l'état réseau.

### Étape 8 : vérifier l'adresse IP, la route et les DNS

#### Vérifier l'adresse IP

```bash
ip -br addr show ens18
```

Résultat attendu :

```text
ens18            UP             192.168.1.50/24
```

#### Vérifier la route par défaut

```bash
ip route
```

Résultat attendu :

```text
default via 192.168.1.1 dev ens18
192.168.1.0/24 dev ens18 proto kernel scope link src 192.168.1.50
```

#### Vérifier les DNS vus par le système

```bash
resolvectl status
```

Vous devez retrouver l'interface concernée et les serveurs DNS configurés.

#### Vérifier la connectivité

```bash
ping -c 4 192.168.1.1
ping -c 4 1.1.1.1
ping -c 4 google.com
```

Interprétation :

- si le ping vers la **passerelle** échoue, le problème vient souvent de l'IP, du masque ou du VLAN ;
- si le ping vers **1.1.1.1** fonctionne mais pas vers `google.com`, le problème vient souvent du **DNS** ;
- si tout fonctionne, la configuration est correcte.

### Étape 9 : revenir en arrière si nécessaire

Si la nouvelle configuration ne fonctionne pas, restaurez la sauvegarde :

```bash
sudo cp /etc/netplan/50-cloud-init.yaml.bak /etc/netplan/50-cloud-init.yaml
sudo netplan apply
```

Si vous êtes à distance et que le réseau est déjà coupé, passez par la **console de la VM** pour restaurer le fichier.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `ip -br addr` | Afficher rapidement les adresses IP des interfaces |
| `ip route` | Afficher la table de routage |
| `sudo find /etc/netplan -maxdepth 1 -type f -name '*.yaml' -print` | Lister les fichiers Netplan |
| `sudo netplan generate` | Vérifier et générer la configuration sans l'appliquer |
| `sudo netplan try` | Tester temporairement une configuration réseau |
| `sudo netplan apply` | Appliquer la configuration Netplan |
| `resolvectl status` | Afficher l'état du résolveur DNS |

## Vérification

Pour valider le TP, vous devez pouvoir confirmer les points suivants :

- [x] l'interface réseau correcte a été identifiée ;
- [x] le fichier Netplan d'origine a été sauvegardé ;
- [x] l'interface possède l'adresse IP statique attendue ;
- [x] la route par défaut pointe vers la bonne passerelle ;
- [x] les DNS configurés sont visibles avec `resolvectl status` ;
- [x] la machine répond aux tests réseau de base.

!!! success "Résultat attendu"
    Le serveur conserve désormais une **adresse IP fixe** après redémarrage et la résolution DNS fonctionne correctement.

## Ressources

- [Netplan documentation — Configure a static IP address on an interface](https://netplan.readthedocs.io/en/stable/examples/) — Exemples officiels Netplan
- [Netplan documentation — YAML configuration reference](https://netplan.readthedocs.io/en/stable/netplan-yaml/) — Référence officielle des clés YAML
- [Ubuntu Manpages — `netplan-try(8)`](https://manpages.ubuntu.com/manpages/noble/man8/netplan-try.8.html) — Test de configuration avec rollback automatique
- [Ubuntu Manpages — `resolvectl(1)`](https://manpages.ubuntu.com/manpages/noble/man1/resolvectl.1.html) — Vérification de la configuration DNS côté système
