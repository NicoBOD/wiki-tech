---
title: Diagnostiquer les problèmes de routage et de latence réseau avec mtr
date: 2026-06-27
author: Nicolas BODAINE
tags:
  - reseau
  - diagnostic
  - linux
  - mtr
difficulty: débutant
os: Linux
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Diagnostiquer les problèmes de routage et de latence réseau avec mtr

!!! abstract "Résumé"
    Cet article explique comment utiliser `mtr` (My Traceroute), un outil de diagnostic réseau puissant qui combine les fonctionnalités de `ping` et de `traceroute`. Vous apprendrez à l'installer, à lire ses rapports et à identifier l'origine des ralentissements ou des coupures de connexion.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 / Linux en général |
| Dernière mise à jour | 2026-06-27 |

## Contexte

Lorsque l'accès à un service distant est lent ou instable, il est souvent difficile de déterminer si le problème vient de votre réseau local, de votre fournisseur d'accès à Internet (FAI), ou du serveur distant lui-même. 

Les outils classiques comme `ping` (qui mesure la latence globale) et `traceroute` (qui liste les sauts successifs) sont utiles, mais ne donnent qu'une vision fragmentée et statique de la situation. `mtr` fusionne ces deux commandes pour fournir une interface de diagnostic en temps réel, permettant de repérer rapidement à quel "saut" (nœud réseau) se produit la perte de paquets ou la montée en latence.

## Prérequis

- Un système d'exploitation Linux (Ubuntu, Debian, CentOS, etc.).
- Des droits d'administration (privilèges `root` ou `sudo`) pour exécuter l'outil, car il nécessite l'envoi de paquets ICMP spécifiques.

## Procédure

### Étape 1 : Installer mtr

La commande `mtr` n'est généralement pas préinstallée sur la plupart des distributions Linux, mais elle est présente dans les dépôts officiels.

=== "Ubuntu / Debian"

    ```bash
    sudo apt update
    sudo apt install -y mtr
    ```

=== "RHEL / Rocky / AlmaLinux"

    ```bash
    sudo dnf install -y mtr
    ```

=== "Arch Linux"

    ```bash
    sudo pacman -S mtr
    ```

### Étape 2 : Lancer une analyse de base

Pour démarrer un diagnostic vers une cible (une adresse IP ou un nom de domaine), exécutez simplement `mtr` suivi de la cible. 

Par exemple, pour tester la connexion vers le DNS public de Cloudflare :

```bash
sudo mtr 1.1.1.1
```

L'interface de `mtr` s'ouvre et se met à jour en continu. Vous verrez une liste de "sauts" (Hops) correspondant aux différents routeurs traversés pour atteindre la cible.

### Étape 3 : Comprendre et lire l'interface de mtr

L'interface présente plusieurs colonnes qui sont cruciales pour le diagnostic :

- **Host** : L'adresse IP ou le nom d'hôte du routeur traversé.
- **Loss%** : Le pourcentage de paquets perdus à ce saut. *C'est la métrique la plus importante.*
- **Snt** (Sent) : Le nombre total de paquets envoyés.
- **Last** : La latence du dernier paquet reçu (en millisecondes).
- **Avg** (Average) : La latence moyenne sur l'ensemble des paquets.
- **Best** : La latence la plus faible enregistrée.
- **Wrst** (Worst) : La latence la plus élevée enregistrée.
- **StDev** : L'écart type, qui indique la stabilité de la latence (une valeur élevée signifie que la connexion est instable / "jitter").

!!! tip "Analyser la perte de paquets"
    Une légère perte de paquets (ex: 5%) sur un seul routeur au milieu de la chaîne n'est **pas forcément un problème**. Certains routeurs limitent volontairement les réponses ICMP (Rate Limiting) pour s'économiser. 
    Cependant, si la perte de paquets **se propage sur tous les sauts suivants** jusqu'à la destination finale, alors c'est la preuve d'un véritable problème réseau à partir de ce saut.

### Étape 4 : Utiliser les options avancées

`mtr` peut être exécuté en ligne de commande pour générer des rapports ponctuels plutôt qu'une interface interactive. C'est particulièrement utile pour conserver une trace ou pour des scripts d'automatisation.

**1. Afficher un rapport statique (10 cycles) :**
```bash
sudo mtr --report -c 10 1.1.1.1
```
*L'option `-c 10` indique qu'il va envoyer 10 paquets, puis afficher un résumé textuel et quitter.*

**2. Forcer l'utilisation des ports TCP plutôt qu'ICMP :**
Si les requêtes ICMP (`ping`) sont bloquées par un pare-feu sur le trajet, vous pouvez forcer `mtr` à utiliser le protocole TCP sur un port spécifique (par exemple le port 443, généralement ouvert pour le HTTPS).
```bash
sudo mtr --tcp --port 443 1.1.1.1
```

**3. Désactiver la résolution DNS :**
Pour afficher uniquement les adresses IP et accélérer l'affichage (utile si votre serveur DNS est lui-même défaillant) :
```bash
sudo mtr --no-dns 1.1.1.1
```

## Aide-mémoire

| Touches dans l'interface `mtr` | Action |
|--------------------------------|-------------|
| `q` | Quitter l'application |
| `d` | Alterner l'affichage (modes de présentation) |
| `n` | Activer/désactiver la résolution DNS (Hostname ↔ IP) |
| `p` | Mettre en pause ou reprendre la collecte de données |
| `r` | Réinitialiser les compteurs |

## Vérification

Pour confirmer que l'outil est bien opérationnel et que vos règles de pare-feu sortantes ne bloquent pas le diagnostic réseau, générez un rapport rapide sur l'interface de boucle locale (localhost) :

```bash
sudo mtr --report -c 1 127.0.0.1
```

!!! success "Résultat attendu"
    Vous devriez obtenir une seule ligne correspondant au saut sur `localhost` avec une latence moyenne (`Avg`) proche de `0.0` ms et aucune perte de paquet (`Loss%` = `0.0%`).

## Ressources

- [Cloudflare Learning : Qu'est-ce que MTR ?](https://www.cloudflare.com/fr-fr/learning/network-layer/what-is-mtr/) — Explication détaillée de son fonctionnement et de la lecture des résultats.
- `man mtr` — Documentation complète de l'outil et de ses options sur votre système Linux.