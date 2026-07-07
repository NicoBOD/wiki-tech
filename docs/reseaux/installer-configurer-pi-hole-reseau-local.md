---
title: Bloquer les requêtes malveillantes et publicités avec Pi-hole
date: 2026-06-30
author: Nicolas BODAINE
tags:
  - dns
  - securite
  - pihole
  - linux
difficulty: débutant
os: Ubuntu 24.04 / Debian 12
status: publié
---

# Bloquer les requêtes malveillantes et publicités avec Pi-hole

!!! abstract "Résumé"
    Pi-hole est un "trou noir" DNS qui protège votre réseau local. En l'utilisant comme serveur DNS par défaut, vous bloquez les publicités, les traqueurs et les domaines malveillants pour tous les appareils connectés (PC, smartphones, TV connectées) sans rien installer sur ces derniers.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 ou Debian 12 |
| Dernière mise à jour | 2026-06-30 |

## Contexte

La plupart des appareils connectés émettent des requêtes vers des domaines publicitaires ou de télémétrie. Installer un bloqueur de publicités sur chaque navigateur est fastidieux, et impossible sur certains appareils (comme les TV connectées). Pi-hole résout ce problème en agissant au niveau du réseau : il intercepte les requêtes DNS et bloque celles destinées à des domaines connus pour être nuisibles.

## Prérequis

- Une machine sous Linux (serveur physique, VM ou Raspberry Pi) allumée en permanence.
- Une **adresse IP statique** configurée sur cette machine.
- Un accès root ou un utilisateur avec privilèges `sudo`.
- Savoir comment modifier les paramètres DNS sur votre box internet/routeur.

## Procédure

### Étape 1 : Mise à jour du système

Avant d'installer Pi-hole, assurez-vous que votre système est à jour et dispose des utilitaires de base.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install curl dnsutils -y
```

### Étape 2 : Lancer le script d'installation de Pi-hole

L'équipe de Pi-hole fournit un script d'installation automatisé très simple.

```bash
curl -sSL https://install.pi-hole.net | bash
```

Une interface en mode texte (ncurses) va s'afficher. Suivez ces étapes :

1. Validez les messages d'accueil et les avertissements concernant l'IP statique.
2. **Choix de l'interface réseau** : Sélectionnez votre interface principale (ex: `eth0` ou `enp3s0`).
3. **Fournisseur DNS en amont (Upstream DNS)** : Choisissez un fournisseur public (ex: Quad9, Cloudflare ou Google) vers lequel Pi-hole renverra les requêtes légitimes.
4. **Listes de blocage** : Laissez la liste par défaut (StevenBlack) cochée.
5. **Interface d'administration web** : Acceptez l'installation de l'interface web et du serveur web (lighthttpd).
6. **Journalisation (Logging)** : Gardez l'option par défaut (Show everything) pour pouvoir analyser le trafic.

À la fin de l'installation, un résumé s'affiche avec **votre mot de passe d'administration web**. Notez-le soigneusement.

### Étape 3 : Modifier le mot de passe de l'interface web (optionnel)

Si vous avez oublié de noter le mot de passe généré ou si vous souhaitez le personnaliser, exécutez :

```bash
pihole -a -p
```
Entrez et confirmez votre nouveau mot de passe.

### Étape 4 : Configurer vos appareils pour utiliser Pi-hole

L'installation est terminée, mais vos appareils doivent maintenant interroger Pi-hole au lieu du serveur DNS de votre FAI.

**Méthode 1 : Via votre box internet/routeur (Recommandé)**
1. Connectez-vous à l'interface d'administration de votre box.
2. Cherchez les paramètres **DHCP**.
3. Remplacez le serveur DNS primaire par l'adresse IP de votre machine Pi-hole.

**Méthode 2 : Manuellement sur un poste (Pour tester)**
1. Sur Windows : `Paramètres > Réseau > Modifier les options d'adaptateur > IPv4 > Serveur DNS`.
2. Entrez l'IP de votre serveur Pi-hole.

## Vérification

Depuis un ordinateur utilisant Pi-hole comme serveur DNS, ouvrez un terminal et testez la résolution d'un domaine bloqué, puis d'un domaine légitime.

```bash
# Test d'un domaine publicitaire (doit retourner 0.0.0.0 ou échouer)
nslookup doubleclick.net

# Test d'un domaine légitime (doit retourner une vraie IP)
nslookup wikipedia.org
```

!!! success "Résultat attendu"
    La résolution du domaine publicitaire est interceptée par Pi-hole, tandis que les sites normaux chargent correctement. Sur l'interface web (accessible via `http://<IP_PIHOLE>/admin`), vous verrez le compteur de "Queries Blocked" augmenter.

## Ressources

- [Documentation officielle Pi-hole](https://docs.pi-hole.net/) — Guide complet et FAQ.
- [Dépôt GitHub du projet](https://github.com/pi-hole/pi-hole)