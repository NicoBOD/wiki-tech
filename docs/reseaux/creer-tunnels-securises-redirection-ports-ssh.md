---
title: "Créer des tunnels sécurisés avec la redirection de ports SSH"
date: 2026-06-23
author: Nicolas BODAINE
tags: ["ssh", "reseau", "tunnel", "securite"]
difficulty: intermediaire
os: "linux"
status: publié
---

# Créer des tunnels sécurisés avec la redirection de ports SSH

Le protocole SSH (Secure Shell) est universellement utilisé pour l'administration sécurisée de serveurs à distance. Cependant, SSH possède une autre fonctionnalité très puissante souvent méconnue : la **redirection de ports** (*Port Forwarding*).

Cela permet de créer un tunnel chiffré à l'intérieur de votre connexion SSH pour rediriger le trafic réseau d'un port vers un autre. C'est particulièrement utile pour :
- Sécuriser l'accès à un service non chiffré (comme VNC, une base de données MySQL sans TLS, etc.).
- Contourner un pare-feu ou un routeur NAT qui bloque certains ports.
- Accéder à un service réseau interne non exposé sur Internet.

Dans ce tutoriel, nous aborderons les trois principaux types de redirection de ports SSH : **Local**, **Distant** (Remote) et **Dynamique** (SOCKS proxy).

---

## 1. Redirection de port locale (Local Port Forwarding)

La redirection locale permet de rediriger un port de votre **machine locale** (client) vers un port sur le **serveur distant** (ou une autre machine accessible par ce serveur). 

### Cas d'usage : 
Vous souhaitez vous connecter à une base de données PostgreSQL tournant sur le port `5432` d'un serveur distant, mais ce port est bloqué par le pare-feu du serveur. Seul le port SSH (22) est autorisé.

### La commande :
```bash
ssh -L [port_local]:[adresse_de_destination]:[port_de_destination] [utilisateur]@[serveur_ssh]
```

**Exemple concret :**
```bash
ssh -L 8080:localhost:5432 admin@srv-bdd.mondomaine.fr
```
*Ici, nous lions le port `8080` de notre ordinateur personnel (`localhost` d'un point de vue local) au port `5432` du serveur distant (qui est `localhost` depuis le point de vue du serveur `srv-bdd`).*

Ensuite, depuis votre machine locale, vous pouvez vous connecter à PostgreSQL en ciblant simplement : `localhost:8080`. Le trafic passera dans le tunnel chiffré SSH et atterrira sur le port 5432 du serveur.

---

## 2. Redirection de port distante (Remote Port Forwarding)

La redirection distante fait l'inverse : elle redirige un port du **serveur distant** vers un port de votre **machine locale** (ou de votre réseau local).

### Cas d'usage :
Vous développez une application web sur votre ordinateur personnel (sur le port `3000`), qui se trouve derrière la box de votre FAI (pas d'IP publique). Vous voulez faire tester cette application à un client via Internet, en passant par un serveur VPS public que vous contrôlez.

### La commande :
```bash
ssh -R [port_distant]:[adresse_locale]:[port_local] [utilisateur]@[serveur_ssh]
```

**Exemple concret :**
```bash
ssh -R 8080:localhost:3000 admin@vps.mondomaine.fr
```
*Le port `8080` du VPS public redirigera désormais tout le trafic vers le port `3000` de votre ordinateur portable personnel.*

Le client peut alors taper `http://vps.mondomaine.fr:8080` dans son navigateur et verra l'application tournant sur votre PC.

*(Note : pour que d'autres machines puissent accéder au port redirigé sur le serveur distant, l'option `GatewayPorts yes` doit être activée dans le fichier `/etc/ssh/sshd_config` du serveur).*

---

## 3. Redirection de port dynamique (Dynamic Port Forwarding)

La redirection dynamique transforme votre client SSH en un **proxy SOCKS**. Au lieu de rediriger un seul port spécifique vers une destination fixe, elle redirige le trafic à la volée vers n'importe quelle destination demandée par l'application locale.

### Cas d'usage :
Vous êtes connecté à un Wi-Fi public non sécurisé (hôtel, aéroport) et vous voulez chiffrer tout votre trafic de navigation web. Ou vous avez besoin de naviguer sur Internet avec l'adresse IP de votre serveur distant pour contourner un filtrage géographique.

### La commande :
```bash
ssh -D [port_local] [utilisateur]@[serveur_ssh]
```

**Exemple concret :**
```bash
ssh -D 9090 admin@vps.mondomaine.fr
```
Votre machine locale va écouter sur le port `9090`. 

**Configuration du navigateur :**
Il faut ensuite configurer votre navigateur web (ex: Firefox) pour utiliser un proxy :
- Proxy SOCKS v5
- Hôte : `localhost`
- Port : `9090`

Désormais, **tout** votre trafic web passera de manière chiffrée par le serveur SSH avant de ressortir sur Internet.

---

## Les options utiles pour la création de tunnels

Pour créer un tunnel pur (sans avoir besoin d'un shell interactif sur le serveur), vous pouvez combiner ces options très pratiques :

- `-N` : Ne pas exécuter de commande distante (utile uniquement pour transférer des ports).
- `-f` : Lancer SSH en arrière-plan (background) une fois le mot de passe saisi.
- `-q` : Mode silencieux (supprime la plupart des messages d'avertissement et de diagnostic).
- `-C` : Active la compression des données (utile pour les connexions lentes, comme VNC).

**Création du tunnel en tâche de fond (silencieux) :**
```bash
ssh -f -N -q -L 8080:localhost:5432 admin@srv-bdd.mondomaine.fr
```

*(N'oubliez pas que pour fermer un tunnel lancé en arrière-plan avec `-f`, vous devrez trouver son PID avec `ps aux | grep ssh` et le tuer avec `kill`).*

---

## Conclusion

La redirection de ports SSH est un outil polyvalent indispensable à tout administrateur système ou réseau. Elle permet de sécuriser des flux en clair et d'outrepasser les limites de l'architecture réseau existante sans devoir configurer des VPN lourds pour de simples tests ou accès ponctuels.