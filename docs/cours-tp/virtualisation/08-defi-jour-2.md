---
title: "Défi du jour 2 : une petite infrastructure virtualisée, sans pas-à-pas"
date: 2026-11-16
author: Nicolas BODAINE
tags:
  - virtualisation
  - reseau
  - stockage
  - travaux-pratiques
difficulty: intermédiaire
os: VMware Workstation Pro 26H1, Debian 13.7
status: publié
---

# Défi du jour 2

!!! abstract "Résumé"
    Ce défi mobilise tout le jour 2 **sans pas-à-pas** : déployer un serveur à partir du modèle, le placer derrière le routeur, lui faire servir un site stocké sur le serveur de stockage, le publier, puis **diagnostiquer trois pannes** typiques d'un réseau virtuel. Le corrigé détaillé est replié en bas de page : chercher d'abord, à l'aide des parties [5](05-virtualiser-des-serveurs.md), [6](06-virtualiser-le-reseau.md) et [7](07-virtualiser-le-stockage.md).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| Durée estimée | 1 h 15 |
| Version décrite | VMware Workstation Pro 26H1, Debian 13.7 |
| Place dans le parcours | Partie 8 sur 17 du parcours [Virtualisation](index.md) — jour 2 |
| Dernière mise à jour | 2026-11-16 |

---

<!-- NOTE DE RÉDACTION (non affichée) : le montage d'un export NFS en lecture seule sur /var/www/html et la publication par nginx ont été vérifiés sur KVM (page servie depuis /srv/site). Les trois pannes correspondent à des effets mesurés en partie 6 (sans masquerade : 100 % de perte vers Internet). -->

**Point de départ** : le lab de la fin de la [partie 7](07-virtualiser-le-stockage.md) : `routeur` (NAT sur VMnet8, `10.10.10.1` sur VMnet2), `web1` (`10.10.10.10`), `stockage` (`10.10.10.20`, NFS et iSCSI), et le modèle `modele-debian`. 🖥️ Démarrer, dans cet ordre, `routeur`, `stockage`, puis `web1`.

## 1. Mission : un deuxième serveur web pour Bureautix

La société fictive *Bureautix* veut **deux** serveurs web qui affichent **le même site**, pour pouvoir arrêter l'un pendant une maintenance sans couper le site. Le contenu du site doit être rangé **à un seul endroit**, sur le serveur de stockage.

Réaliser, sans pas-à-pas :

1. sur `stockage`, un dossier `/srv/site` qui contient une page `index.html` affichant « Site de Bureautix », partagé en **NFS en lecture seule** pour le réseau `10.10.10.0/24` ;
2. un nouveau serveur `web4`, **clone lié** du modèle, branché **uniquement** sur VMnet2, avec l'adresse fixe `10.10.10.11`, la passerelle et le DNS qui conviennent, une identité propre et nginx ;
3. sur `web1` **et** sur `web4`, le partage `/srv/site` monté **automatiquement au démarrage** à la place de `/var/www/html` ;
4. sur `routeur`, la publication de `web1` sur le **port 8080** (si elle n'a pas été faite en section 5.2 de la partie 6) et de `web4` sur le **port 8081** ;
5. la preuve, depuis le navigateur du PC, que les deux serveurs affichent la même page, puis qu'une modification de `index.html` sur `stockage` apparaît sur les deux après un rechargement de la page ;
6. une **fiche de documentation** du lab : pour chaque VM, son rôle, ses cartes réseau (VMnet), ses adresses, sa mémoire, ses services et ses instantanés.

## 2. Diagnostic : trois pannes

Un collègue a « bricolé » le lab. Pour chaque symptôme, trouver la cause **la plus probable**, la **commande** qui le prouve et la **correction**.

| N° | Symptôme |
|:---:|---|
| A | `web1` joint `10.10.10.1` mais ni `1.1.1.1` ni `deb.debian.org`. Sur `routeur`, `sudo nft list ruleset` affiche bien la table `ip nat` avec sa règle `masquerade`. |
| B | `web1` joint `1.1.1.1`, mais `ping deb.debian.org` répond « Échec temporaire dans la résolution du nom ». |
| C | Après un redémarrage de `routeur`, plus aucune machine de VMnet2 ne sort sur Internet, alors que tout fonctionnait avant. `sudo nft list ruleset` **n'affiche plus rien**. |

Indice : chaque panne correspond à **une** étape de la partie 6.

## 3. Corrigé

??? success "Corrigé de la mission"
    **1. Le site sur `stockage`**

    ```bash
    sudo mkdir -p /srv/site
    echo "<h1>Site de Bureautix</h1>" | sudo tee /srv/site/index.html
    echo "/srv/site 10.10.10.0/24(ro,sync,no_subtree_check)" | sudo tee -a /etc/exports
    sudo exportfs -ra
    sudo exportfs -v
    ```

    `ro` (*read only*) : les serveurs web n'ont besoin que de **lire** le site ; un serveur web compromis ne pourra pas le modifier.

    **2. Le serveur `web4`**

    - 🖥️ Clone lié de `modele-debian` (`modele-v1`), nommé `web4`, carte réseau sur **Custom > VMnet2**.
    - 🐧 `sudo personnaliser-clone.sh web4`.
    - 🐧 Dans `/etc/network/interfaces`, sur la ligne `iface … inet dhcp` de la carte (nom affiché par `ip -br link`, souvent `ens33`) : `inet static`, `address 10.10.10.11/24`, `gateway 10.10.10.1` ; `sudo reboot` ; **après** le redémarrage, `echo "nameserver 192.168.x.2" | sudo tee /etc/resolv.conf` (adresse notée sur `routeur` en partie 6).
    - 🐧 `sudo apt install -y nginx nfs-common` : le paquet `nfs-common` est indispensable pour monter un partage NFS.

    **3. Le montage automatique**, sur `web1` et sur `web4` :

    ```bash
    echo "10.10.10.20:/srv/site  /var/www/html  nfs  ro,_netdev,nofail  0  0" | sudo tee -a /etc/fstab
    sudo systemctl daemon-reload
    sudo mount -a
    findmnt /var/www/html
    ```

    Le partage **recouvre** le contenu local de `/var/www/html` (la page « Serveur web1 » n'est pas effacée, elle est seulement cachée tant que le partage est monté).

    **4. La publication de `web4`** : sur `routeur`, ajouter une ligne dans la chaîne `prerouting` de la table `redirection` de `/etc/nftables.conf` (ou créer la table comme en partie 6, section 5.2) :

    ```text
    iifname "ens33" tcp dport 8081 dnat to 10.10.10.11:80
    ```

    (et la ligne équivalente vers `10.10.10.10:80` pour le port 8080 si elle manque), avec le **vrai** nom de la carte VMnet8 du routeur à la place de `ens33`, puis `sudo nft -c -f /etc/nftables.conf && sudo systemctl restart nftables`.

    **5. La preuve** : 🌐 `http://<IP ens33 du routeur>:8080` et `http://<IP ens33 du routeur>:8081` affichent tous deux « Site de Bureautix ». Sur `stockage`, modifier la page (`echo "<h1>Site de Bureautix — version 2</h1>" | sudo tee /srv/site/index.html`) : un rechargement de chaque page (++f5++) affiche la version 2 ; si l'un des serveurs affiche encore l'ancienne version, patienter quelques secondes : le client NFS garde brièvement en cache les informations sur les fichiers, puis relit la nouvelle version. C'est le principe d'une **ferme de serveurs web** : plusieurs serveurs identiques, un seul contenu partagé ; un **répartiteur de charge** (*load balancer*) placé devant enverrait chaque visiteur vers l'un ou l'autre.

    **6. La fiche de documentation** (exemple) :

    | VM | Rôle | Réseaux | Adresses | Mémoire | Services | Instantanés |
    |---|---|---|---|---|---|---|
    | `routeur` | Routeur, NAT, publication | VMnet8 (NAT) + VMnet2 | DHCP sur VMnet8 · `10.10.10.1` | 512 Mo | nftables (NAT, DNAT 8080 et 8081) | `routeur-ok` |
    | `web1` | Serveur web | VMnet2 | `10.10.10.10` | 1 Go | nginx, montages NFS, initiateur iSCSI | `stockage-ok` |
    | `web4` | Serveur web | VMnet2 | `10.10.10.11` | 1 Go | nginx, montage NFS | — |
    | `stockage` | Serveur de fichiers et cible iSCSI | VMnet2 | `10.10.10.20` | 1 Go | NFS (`/srv/partage`, `/srv/site`), iSCSI (`lun0` = `sdb`) | `stockage-ok` |
    | `modele-debian` | Modèle (mode modèle) | VMnet8 | — | 1 Go | — | `modele-v1` (base des clones liés) |

??? success "Corrigé du diagnostic"
    **A — le routage IP est désactivé**, ou la règle `masquerade` vise une carte qui n'existe pas. Les paquets de `web1` arrivent au routeur, qui ne les fait pas passer d'une carte à l'autre, ou les fait sortir sans traduction d'adresse. Preuves : 🐧 **routeur** `cat /proc/sys/net/ipv4/ip_forward` répond `0` ; ou le nom après `oifname` dans `sudo nft list ruleset` diffère du nom de la carte VMnet8 affiché par `ip -br link`. Corrections : recréer `/etc/sysctl.d/99-routeur.conf` avec `net.ipv4.ip_forward=1`, puis `sudo sysctl --system` ; ou corriger le nom de la carte dans `/etc/nftables.conf`, puis `sudo systemctl restart nftables`.

    **B — le DNS est mal configuré.** Le réseau fonctionne (le ping par adresse répond), seule la **résolution des noms** échoue. Preuve : 🐧 **web1** `cat /etc/resolv.conf` ne contient pas de ligne `nameserver 192.168.x.2` valide (fichier vide, mauvaise adresse, ou adresse d'un serveur injoignable). Correction : `echo "nameserver 192.168.x.2" | sudo tee /etc/resolv.conf`.

    **C — nftables n'est pas lancé au démarrage.** Les règles avaient été chargées à la main (`sudo systemctl start nftables` ou `sudo nft -f /etc/nftables.conf`), mais le service n'a pas été **activé** : au redémarrage, rien n'est chargé, d'où un `nft list ruleset` vide. Preuve : 🐧 **routeur** `systemctl is-enabled nftables` répond `disabled`. Correction : `sudo systemctl enable --now nftables`. (Variante : si `nft list ruleset` montrait la table `inet filter` mais pas la table `ip nat`, c'est que la règle avait été tapée en ligne de commande sans être écrite dans `/etc/nftables.conf`.)

    **Méthode à retenir** : on teste **couche par couche**, du plus proche au plus lointain. Adresse et passerelle (`ip a`, `ip route`), puis la passerelle (`ping 10.10.10.1`), puis Internet par adresse (`ping 1.1.1.1`), puis par nom (`ping deb.debian.org`). La première étape qui échoue désigne la panne.

---

## Ressources

- [Wiki nftables — Quick reference](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes) — l'essentiel de la syntaxe de nftables (en anglais).
- [Manuel Debian — `exports(5)`](https://manpages.debian.org/trixie/nfs-kernel-server/exports.5.en.html) — toutes les options d'un partage NFS (en anglais).
- Partie précédente : [Virtualiser le stockage](07-virtualiser-le-stockage.md) · Partie suivante : [Panorama des technologies](09-panorama-des-technologies.md).

*[VM]: Virtual Machine — machine virtuelle
*[NFS]: Network File System — partage de fichiers Unix et Linux
*[NAT]: Network Address Translation — traduction d'adresses
*[DNAT]: Destination NAT — redirection de port
*[DNS]: Domain Name System — résolution des noms
*[iSCSI]: Internet Small Computer System Interface — disques SCSI sur IP
