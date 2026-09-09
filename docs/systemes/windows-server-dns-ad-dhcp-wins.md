---
title: "Découvrir les services d'infrastructure Windows Server — DNS, Active Directory, DHCP et WINS"
date: 2026-05-09
author: Nicolas BODAINE
tags:
  - windows-server
  - tssr
  - active-directory
  - dns
  - dhcp
  - wins
  - administration-systeme
  - travaux-diriges
difficulty: débutant
os: Windows Server 2025 et Windows 11
status: brouillon
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                        -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant afin de référencer ce     -->
<!-- nouvel article et permettre aux visiteurs de le trouver !    -->
<!-- ============================================================ -->

# Découvrir les services d'infrastructure Windows Server — DNS, Active Directory, DHCP et WINS

!!! abstract "Résumé"
    Ce support propose **21 heures de formation**, réparties sur **3 journées de 7 heures**, pour découvrir les quatre services d'infrastructure qui structurent la plupart des réseaux Windows : la **résolution de noms DNS**, l'**annuaire Active Directory Domain Services**, l'**attribution dynamique d'adresses DHCP** et le service historique **WINS**.

    Ce cours fait suite au support consacré aux fonctions serveur de base (stockage, partage SMB, FSRM, IIS, sauvegarde). Il réutilise les mêmes principes pédagogiques : beaucoup de pratique en machines virtuelles, une progression pas à pas, et une vérification systématique du résultat obtenu.

    Les apprenants transforment un serveur autonome en **contrôleur de domaine**, structurent un annuaire, appliquent une stratégie de groupe, déploient un serveur DHCP autorisé dans le domaine, puis installent et testent un serveur WINS pour en comprendre l'historique et les limites.

    Le parcours comprend environ **15 heures de travaux dirigés** et **6 heures d'explications, de démonstrations et de corrections**.

| Propriété | Valeur |
|-----------|--------|
| Public | Techniciens Supérieurs en Systèmes et Réseaux — niveau Bac +2 |
| Difficulté | Débutant |
| Durée | 3 jours × 7 heures, soit 21 heures pédagogiques |
| OS serveur | Windows Server 2025 Standard avec Expérience de bureau |
| OS client | Windows 11 Pro |
| Organisation | Travail individuel ou en binôme |
| Modalité dominante | Travaux dirigés sur machines virtuelles |
| Dernière mise à jour | 2026-05-09 |

!!! note "Convention de lecture"
    - Une commande indiquée **sur le serveur** s'exécute sur `SRV-DC01`.
    - Une commande indiquée **sur le client** s'exécute sur `CLT-01` ou `CLT-02`.
    - Les commandes d'administration s'exécutent dans **Windows PowerShell 5.1 en tant qu'administrateur**, sauf indication contraire.
    - Le domaine du laboratoire se nomme **`tssr.lan`** (nom NetBIOS `TSSR`). Le choix de `.lan` évite d'utiliser `.local`, réservé en pratique à la résolution multicast (mDNS) et déconseillé par Microsoft pour un domaine Active Directory.
    - Les noms de menus peuvent légèrement varier selon la langue et les mises à jour de Windows.

---

## 1. Contexte professionnel

Le serveur préparé lors du cours précédent fonctionnait en **groupe de travail** : chaque machine gérait ses propres comptes, et l'accès aux services se faisait par adresse IP.

Cette approche atteint vite ses limites :

- il faut recréer chaque compte sur chaque machine ;
- il n'existe aucune règle de sécurité commune ;
- il faut retenir des adresses IP plutôt que des noms ;
- chaque poste doit être configuré manuellement avec une adresse IP fixe ou improvisée.

L'entreprise souhaite maintenant :

- que les utilisateurs se connectent avec **un seul compte**, quel que soit le poste ;
- que les postes et serveurs se désignent par un **nom** plutôt que par une adresse IP ;
- que les adresses IP des postes soient **attribuées automatiquement** ;
- que les anciens équipements et applications utilisant des **noms NetBIOS** continuent, temporairement, à fonctionner.

Vous êtes chargé de mettre en place cette infrastructure de base, de la documenter, et de savoir diagnostiquer les pannes les plus courantes.

!!! warning "Périmètre pédagogique"
    Ce cours reste centré sur la **découverte** de ces quatre services dans un laboratoire isolé à un seul contrôleur de domaine.

    Les sujets avancés — plusieurs contrôleurs de domaine, réplication multi-site, redondance DHCP, sécurisation fine de l'annuaire, PKI — ne sont pas traités ici.

---

## 2. Objectifs pédagogiques

À l'issue des trois journées, l'apprenant doit être capable de :

1. expliquer le rôle du DNS dans un réseau Windows ;
2. installer un serveur DNS et créer des zones et des enregistrements ;
3. distinguer résolution directe et résolution inverse ;
4. expliquer les notions de forêt, domaine, arbre, contrôleur de domaine et catalogue global ;
5. promouvoir un serveur Windows Server en contrôleur de domaine ;
6. joindre un poste client au domaine et s'y connecter avec un compte de domaine ;
7. créer une structure d'unités d'organisation, d'utilisateurs et de groupes ;
8. expliquer les portées de groupe et leur utilité ;
9. créer une stratégie de groupe simple et comprendre son application ;
10. expliquer le fonctionnement du protocole DHCP ;
11. installer, autoriser et configurer un serveur DHCP ;
12. créer une étendue, des exclusions, des réservations et des options ;
13. expliquer le principe de la résolution NetBIOS et le rôle historique de WINS ;
14. installer et tester un serveur WINS ;
15. expliquer les interactions entre DNS, AD DS, DHCP et WINS ;
16. diagnostiquer un incident simple touchant l'un de ces services.

### Critère de réussite général

Un service d'infrastructure n'est validé que si :

- il répond correctement depuis un poste client, pas seulement depuis le serveur ;
- son fonctionnement peut être prouvé par une commande de vérification ;
- sa configuration est documentée de façon exploitable par un collègue ;
- les limites du laboratoire sont explicitement connues.

---

## 3. Organisation des trois journées

### Jour 1 — DNS et fondations d'Active Directory

| Séquence | Durée | Modalité |
|----------|------:|----------|
| Architecture de la résolution de noms | 30 min | Cours |
| TD 1 — Installer et tester un serveur DNS autonome | 90 min | Pratique |
| Introduction à Active Directory Domain Services | 45 min | Cours |
| TD 2 — Promouvoir le serveur en contrôleur de domaine | 90 min | Pratique |
| DNS intégré à Active Directory | 30 min | Cours |
| TD 3 — Joindre le client au domaine | 60 min | Pratique |
| TD 4 — Explorer l'annuaire avec les outils RSAT | 75 min | Pratique |
| **Total** | **420 min** | **7 h** |

### Jour 2 — Structurer l'annuaire, appliquer une GPO, déployer le DHCP

| Séquence | Durée | Modalité |
|----------|------:|----------|
| Organiser l'annuaire : OU, comptes, groupes | 30 min | Cours |
| TD 5 — Créer la structure d'annuaire | 90 min | Pratique |
| Stratégies de groupe : notions | 30 min | Cours |
| TD 6 — Créer et appliquer une GPO | 75 min | Pratique |
| Le protocole DHCP | 30 min | Cours |
| TD 7 — Installer et configurer le serveur DHCP | 90 min | Pratique |
| TD 8 — Réservations, exclusions et DNS dynamique | 75 min | Pratique |
| **Total** | **420 min** | **7 h** |

### Jour 3 — WINS, intégration des services et diagnostic

| Séquence | Durée | Modalité |
|----------|------:|----------|
| WINS et résolution NetBIOS : un service historique | 30 min | Cours |
| TD 9 — Installer et tester un serveur WINS | 60 min | Pratique |
| Interactions entre DNS, AD DS, DHCP et WINS | 30 min | Cours |
| TD 10 — Diagnostiquer un incident d'infrastructure | 90 min | Pratique |
| Méthode de diagnostic et préparation de l'évaluation | 30 min | Cours |
| TD 11 — Mise en situation professionnelle | 135 min | Pratique évaluée |
| Bilan, correction et consolidation | 45 min | Correction collective |
| **Total** | **420 min** | **7 h** |

!!! tip "Organisation conseillée en binôme"
    Alternez les rôles à chaque TD : une personne manipule, l'autre vérifie et documente. Chaque apprenant doit néanmoins savoir reproduire seul les opérations essentielles, en particulier la promotion du contrôleur de domaine et la création d'une étendue DHCP.

---

## 4. Prérequis et préparation du laboratoire

### 4.1 Prérequis des apprenants

- avoir suivi le cours précédent sur les fonctions serveur de Windows Server, ou posséder un niveau équivalent ;
- savoir utiliser une console PowerShell de base ;
- savoir configurer une adresse IPv4 statique ;
- savoir créer une machine virtuelle et un réseau virtuel isolé.

### 4.2 Machines virtuelles

| VM | Rôle | vCPU | RAM indicative | Disque |
|----|------|-----:|---------------:|--------|
| `SRV-DC01` | DNS, AD DS, DHCP, WINS | 2 | 4 à 6 Go | 80 Go |
| `CLT-01` | Poste client principal | 2 | 4 Go | 64 Go |
| `CLT-02` | Poste client secondaire (DHCP/WINS) | 2 | 4 Go | 64 Go |

`CLT-02` est optionnel mais fortement conseillé : il permet d'observer plusieurs baux DHCP simultanés et deux enregistrements NetBIOS distincts au TD 9.

!!! note "Réutilisation du matériel du cours précédent"
    Si le laboratoire précédent est encore disponible, `SRV-FIC01` peut être réutilisé et renommé, à condition de repartir d'un état propre. En cas de doute, repartir d'une VM neuve évite de mélanger deux configurations pédagogiques différentes.

### 4.3 Réseau du laboratoire

```text
              Hôte de virtualisation
                       |
            Réseau virtuel LAB-TSSR-AD
           /            |              \
   SRV-DC01         CLT-01            CLT-02
192.168.60.10   192.168.60.20    DHCP (plus tard)
```

| Paramètre | SRV-DC01 | CLT-01 (avant jonction) | CLT-02 |
|-----------|----------|--------------------------|--------|
| IPv4 | `192.168.60.10` (statique) | `192.168.60.20` (statique, temporaire) | DHCP dès le jour 2 |
| Préfixe | `/24` | `/24` | `/24` |
| DNS préféré | `127.0.0.1` puis lui-même | `192.168.60.10` | Fourni par DHCP |
| Groupe de travail initial | `WORKGROUP` | `WORKGROUP` | `WORKGROUP` |
| Domaine cible | `tssr.lan` | `tssr.lan` (à partir du TD 3) | `tssr.lan` (à partir du jour 2) |

!!! danger "Une adresse IP fixe pour le contrôleur de domaine"
    L'adresse IP de `SRV-DC01` doit rester fixe et connue de tous les postes. Un contrôleur de domaine dont l'adresse change perturbe la résolution DNS, l'authentification et la réplication.

### 4.4 Préparation du formateur

- [ ] Vérifier que `SRV-DC01` dispose d'une adresse IPv4 statique avant toute installation.
- [ ] Préparer un instantané juste avant la promotion en contrôleur de domaine.
- [ ] Préparer un second instantané juste après la promotion, pour permettre de reprendre le TD 3 en cas d'incident.
- [ ] Vérifier que l'horloge des VM est cohérente (Kerberos est sensible à un décalage horaire important).
- [ ] Préparer les mots de passe de laboratoire conformes à la politique par défaut d'Active Directory (longueur, complexité).
- [ ] Prévoir un support pour les binômes en retard (contrôleur de domaine pré-promu).

!!! warning "Sensibilité de Kerberos à l'heure système"
    Un écart de plus de cinq minutes entre le contrôleur de domaine et un client peut provoquer des échecs d'authentification difficiles à diagnostiquer pour un débutant. Vérifier l'heure sur toutes les VM avant chaque séance.

### 4.5 Dossier de preuves

```text
Nom_Prenom_WindowsServer_DNS_AD_DHCP_WINS
├── 01-dns-autonome.md
├── 02-promotion-ad.md
├── 03-jonction-domaine.md
├── 04-annuaire.md
├── 05-gpo.md
├── 06-dhcp.md
├── 07-wins.md
├── 08-diagnostic.md
└── 09-recette-finale.md
```

**Ne jamais inclure de mot de passe dans les livrables.**

---

# Jour 1 — DNS et fondations d'Active Directory

## 5. Cours — Architecture de la résolution de noms

### 5.1 Pourquoi résoudre des noms ?

Les machines communiquent par adresses IP, mais les humains retiennent plus facilement des noms.

```text
Utilisateur → tape "srv-dc01" ou "http://intranet.tssr.lan"
                    ↓
              Résolution de noms
                    ↓
              192.168.60.10
                    ↓
           Communication réseau réelle
```

Sans résolution de noms, chaque application devrait connaître par cœur l'adresse IP de chaque service, ce qui devient ingérable dès que le réseau grandit ou change.

### 5.2 Le DNS : une base de données hiérarchique

Le **DNS** (Domain Name System) organise les noms en arborescence :

```text
                    . (racine)
                     |
                   lan (exemple pédagogique)
                     |
                  tssr.lan
                 /         \
          srv-dc01      clt-01
       .tssr.lan       .tssr.lan
```

Un nom complet, comme `srv-dc01.tssr.lan`, est appelé **FQDN** (Fully Qualified Domain Name).

### 5.3 Les enregistrements DNS courants

| Type | Rôle |
|------|------|
| A | Associe un nom à une adresse IPv4 |
| AAAA | Associe un nom à une adresse IPv6 |
| PTR | Associe une adresse IP à un nom (résolution inverse) |
| CNAME | Fait pointer un alias vers un autre nom |
| MX | Indique le serveur de messagerie d'un domaine |
| NS | Indique le serveur faisant autorité sur une zone |
| SOA | Décrit les paramètres d'autorité et de synchronisation de la zone |
| SRV | Localise un service réseau, notamment utilisé par Active Directory |

### 5.4 Zone directe et zone inverse

- une **zone de résolution directe** répond à la question « quelle est l'adresse IP de ce nom ? » ;
- une **zone de résolution inverse** répond à la question « quel est le nom associé à cette adresse IP ? ».

Ces deux zones sont indépendantes : créer l'une ne crée pas automatiquement l'autre.

### 5.5 Requête récursive et requête itérative

```text
Client ---(requête récursive)---> Serveur DNS local
                                        |
                             (requêtes itératives successives
                              vers d'autres serveurs si nécessaire)
                                        |
Client <----------- réponse finale -----
```

- le **client** demande généralement une réponse complète : c'est une requête **récursive**.
- le **serveur DNS**, s'il ne connaît pas la réponse, peut interroger d'autres serveurs par des requêtes **itératives**, ou transmettre la demande à un **redirecteur (forwarder)**.

### 5.6 TTL et cache

Chaque réponse DNS est accompagnée d'une **durée de vie (TTL)**, exprimée en secondes, qui indique combien de temps la réponse peut être conservée en cache avant d'être redemandée.

Un TTL trop long ralentit la prise en compte des changements. Un TTL trop court multiplie inutilement les requêtes.

!!! note "Le DNS ne fait pas d'authentification"
    Le DNS répond à des questions de correspondance nom/adresse. Il ne vérifie pas qui pose la question ni ne protège l'accès aux services eux-mêmes. Confondre résolution de noms et sécurité d'accès est une erreur fréquente chez les débutants.

### Questions de compréhension

1. Une zone inverse est-elle indispensable au fonctionnement d'un réseau ?
2. Que se passe-t-il si le TTL d'un enregistrement est très long et que l'adresse IP change ?

??? note "Éléments de correction"
    1. Non, mais elle facilite le diagnostic et certains outils ou journaux l'utilisent pour afficher des noms.
    2. Les clients continueront à utiliser l'ancienne adresse en cache jusqu'à expiration du TTL, provoquant des échecs de connexion.

---

## 6. TD 1 — Installer et tester un serveur DNS autonome

**Durée : 90 minutes**

### Objectifs

- Installer le rôle DNS sur `SRV-DC01`, avant toute installation d'Active Directory.
- Créer une zone directe et une zone inverse.
- Créer des enregistrements manuellement.
- Configurer la résolution côté client.

!!! note "Pourquoi installer le DNS avant Active Directory ?"
    Il est possible de laisser Active Directory installer et configurer le DNS automatiquement. Ce TD choisit de l'installer manuellement d'abord, pour bien comprendre son fonctionnement autonome avant de voir, au TD 2, ce qu'Active Directory y ajoute automatiquement.

### Étape 1 — Vérifier la configuration IP du serveur

```powershell
Get-NetIPConfiguration
Get-NetAdapter
```

Vérifier que `SRV-DC01` possède l'adresse `192.168.60.10` en statique. Sinon, la configurer via `ncpa.cpl` comme dans le cours précédent.

### Étape 2 — Installer le rôle DNS

```powershell
Install-WindowsFeature DNS -IncludeManagementTools

Get-WindowsFeature DNS
Get-Service DNS
```

### Étape 3 — Créer la zone de résolution directe

```powershell
Add-DnsServerPrimaryZone `
    -Name "tssr.lan" `
    -ZoneFile "tssr.lan.dns" `
    -DynamicUpdate None
```

`DynamicUpdate None` interdit pour l'instant les mises à jour automatiques : nous créerons les enregistrements manuellement, pour bien comprendre leur structure.

Vérifier :

```powershell
Get-DnsServerZone
```

### Étape 4 — Créer la zone de résolution inverse

```powershell
Add-DnsServerPrimaryZone `
    -NetworkID "192.168.60.0/24" `
    -ZoneFile "60.168.192.in-addr.arpa.dns" `
    -DynamicUpdate None
```

!!! note "Lecture d'une zone inverse"
    Le nom `60.168.192.in-addr.arpa` inverse l'ordre des octets du réseau `192.168.60.0/24`. Cette inversion est une convention du DNS, pas une erreur de frappe.

### Étape 5 — Créer les enregistrements manuellement

```powershell
Add-DnsServerResourceRecordA `
    -ZoneName "tssr.lan" `
    -Name "srv-dc01" `
    -IPv4Address "192.168.60.10" `
    -CreatePtr
```

L'option `-CreatePtr` crée automatiquement l'enregistrement PTR correspondant dans la zone inverse, si celle-ci existe déjà.

Ajouter un alias pour un futur usage web :

```powershell
Add-DnsServerResourceRecordCName `
    -ZoneName "tssr.lan" `
    -Name "intranet" `
    -HostNameAlias "srv-dc01.tssr.lan"
```

Vérifier :

```powershell
Get-DnsServerResourceRecord -ZoneName "tssr.lan"
Get-DnsServerResourceRecord -ZoneName "60.168.192.in-addr.arpa"
```

### Étape 6 — Configurer la résolution DNS du serveur lui-même

Un serveur DNS doit généralement s'interroger lui-même en priorité :

```powershell
Set-DnsClientServerAddress `
    -InterfaceAlias "Ethernet" `
    -ServerAddresses "127.0.0.1"
```

Adapter le nom de l'interface au résultat de `Get-NetAdapter`.

### Étape 7 — Configurer le client

Sur `CLT-01`, définir l'adresse IP statique `192.168.60.20/24`, puis :

```powershell
Set-DnsClientServerAddress `
    -InterfaceAlias "Ethernet" `
    -ServerAddresses "192.168.60.10"
```

### Étape 8 — Tester la résolution

Sur le client :

```powershell
Resolve-DnsName srv-dc01.tssr.lan
Resolve-DnsName intranet.tssr.lan
nslookup 192.168.60.10
```

Résultat attendu : les trois commandes renvoient une correspondance cohérente avec `192.168.60.10`.

!!! failure "Erreur fréquente : nom court sans suffixe"
    `Resolve-DnsName srv-dc01` peut échouer si le suffixe DNS `tssr.lan` n'est pas configuré sur le client. Utiliser le FQDN complet lève l'ambiguïté pendant cette phase du cours.

### Étape 9 — Observer le service depuis le serveur

```powershell
Get-DnsServerStatistics
Get-DnsServerCache
```

### Livrable

Dans `01-dns-autonome.md` :

- capture des zones créées ;
- liste des enregistrements ;
- résultat des tests `Resolve-DnsName` ;
- explication de la différence entre zone directe et zone inverse.

### Vérification

- [ ] Le rôle DNS est installé.
- [ ] La zone `tssr.lan` existe.
- [ ] La zone inverse existe.
- [ ] L'enregistrement A et le PTR correspondant existent.
- [ ] Le client résout correctement les deux noms testés.

---

## 7. Cours — Introduction à Active Directory Domain Services

### 7.1 Ce que résout un annuaire

Le DNS résout des noms en adresses. **Active Directory Domain Services (AD DS)** résout un besoin différent : centraliser les **identités** (utilisateurs, ordinateurs, groupes) et les **règles de sécurité** applicables à ces identités.

### 7.2 Vocabulaire fondamental

| Terme | Définition simplifiée |
|-------|------------------------|
| Domaine | Espace de gestion regroupant des objets partageant une base de sécurité commune |
| Forêt | Ensemble d'un ou plusieurs domaines partageant un schéma et une configuration communs |
| Arbre de domaines | Domaines reliés par un espace de noms DNS contigu au sein d'une forêt |
| Contrôleur de domaine (DC) | Serveur hébergeant une copie de la base d'annuaire et assurant l'authentification |
| Catalogue global | Copie partielle de tous les objets de la forêt, utilisée pour les recherches inter-domaines |
| Unité d'organisation (OU) | Conteneur permettant d'organiser des objets et d'y appliquer des stratégies |
| Objet | Élément géré par l'annuaire : utilisateur, ordinateur, groupe, imprimante partagée... |
| Schéma | Définition des types d'objets et d'attributs possibles dans la forêt |
| SYSVOL | Dossier partagé répliqué contenant notamment les stratégies de groupe |
| NTDS.dit | Fichier contenant la base de données de l'annuaire sur chaque contrôleur de domaine |

!!! example "Analogie"
    Un **domaine** ressemble à un établissement administratif : il tient un registre commun de ses membres et de ses règles. Une **forêt** ressemble à un groupe d'établissements qui partagent un même règlement de fonctionnement (le schéma), tout en gérant chacun leur propre registre.

### 7.3 Pourquoi un seul DC dans ce laboratoire

En production, on installe généralement **au moins deux contrôleurs de domaine** pour la tolérance de panne et pour répartir la charge d'authentification.

Ce cours utilise un seul contrôleur de domaine pour rester accessible à des débutants. Il est important de retenir que :

- ce DC concentre alors la totalité des rôles ;
- sa perte rendrait le domaine inutilisable ;
- les mécanismes de réplication entre plusieurs DC ne peuvent pas être observés dans ce laboratoire.

### 7.4 Les rôles FSMO, en bref

Cinq rôles particuliers, appelés **FSMO** (Flexible Single Master Operations), ne peuvent être détenus que par un seul contrôleur de domaine à la fois pour certaines opérations sensibles :

| Rôle | Portée | Rôle simplifié |
|------|--------|-----------------|
| Maître de schéma | Forêt | Autorise les modifications du schéma |
| Maître de nommage de domaine | Forêt | Gère l'ajout ou le retrait de domaines |
| Maître RID | Domaine | Distribue des blocs d'identifiants uniques pour les nouveaux objets |
| Émulateur PDC | Domaine | Référence de temps et compatibilité avec d'anciens mécanismes |
| Maître d'infrastructure | Domaine | Maintient les références entre objets de domaines différents |

Avec un seul DC, celui-ci détient automatiquement les cinq rôles. Ce point sera vérifié en pratique au TD 4.

### 7.5 Compte local et compte de domaine

| Aspect | Compte local | Compte de domaine |
|--------|--------------|--------------------|
| Stocké sur | Une seule machine | Le contrôleur de domaine |
| Utilisable sur | Cette machine uniquement | Tous les postes joints au domaine |
| Format de connexion | `NomMachine\utilisateur` | `TSSR\utilisateur` ou `utilisateur@tssr.lan` |
| Gestion centralisée | Non | Oui |

!!! warning "Un domaine ne supprime pas les comptes locaux"
    Joindre une machine à un domaine ajoute une nouvelle source d'authentification possible. Les comptes locaux de cette machine continuent d'exister, sauf désactivation volontaire.

---

## 8. TD 2 — Promouvoir le serveur en contrôleur de domaine

**Durée : 90 minutes**

### Objectifs

- Installer le rôle AD DS.
- Promouvoir `SRV-DC01` en premier contrôleur de domaine d'une nouvelle forêt `tssr.lan`.
- Vérifier la création automatique des zones DNS nécessaires à Active Directory.

!!! danger "Point de non-retour pédagogique"
    La promotion en contrôleur de domaine modifie profondément le serveur. Le formateur s'assure qu'un instantané a été pris juste avant cette étape.

### Étape 1 — Installer le rôle AD DS

```powershell
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

Get-WindowsFeature AD-Domain-Services
```

### Étape 2 — Promouvoir le serveur

```powershell
Import-Module ADDSDeployment

$motDePasseRestauration = Read-Host `
    -Prompt "Mot de passe DSRM (restauration des services d'annuaire)" `
    -AsSecureString

Install-ADDSForest `
    -DomainName "tssr.lan" `
    -DomainNetbiosName "TSSR" `
    -InstallDns `
    -SafeModeAdministratorPassword $motDePasseRestauration `
    -Force
```

| Paramètre | Explication |
|-----------|-------------|
| `-DomainName` | Nom de domaine complet (FQDN) de la nouvelle forêt |
| `-DomainNetbiosName` | Nom court utilisé par les anciens mécanismes (NetBIOS) |
| `-InstallDns` | Installe et configure automatiquement le rôle DNS si nécessaire |
| `-SafeModeAdministratorPassword` | Mot de passe utilisé en cas de restauration de l'annuaire en mode DSRM |

Le serveur redémarre automatiquement à la fin de l'opération.

!!! note "Le mot de passe DSRM"
    Ce mot de passe sert uniquement en cas de maintenance avancée de l'annuaire (mode de restauration des services d'annuaire). Il doit être noté par le formateur dans un emplacement sécurisé, hors des livrables des apprenants.

### Étape 3 — Se reconnecter après redémarrage

Après redémarrage, la session s'ouvre désormais avec un compte de domaine :

```text
TSSR\Administrateur
```

### Étape 4 — Vérifier la promotion

```powershell
Get-ADDomain
Get-ADForest
Get-ADDomainController -Filter *
```

Vérifier notamment :

- le nom de domaine ;
- le nom NetBIOS ;
- le niveau fonctionnel de la forêt et du domaine ;
- le nom du contrôleur de domaine.

### Étape 5 — Exécuter un diagnostic de l'annuaire

```powershell
dcdiag /v
```

Cette commande est volontairement verbeuse. Rechercher en particulier les lignes contenant `passed test` et l'absence de `failed test`.

### Étape 6 — Observer les zones DNS créées automatiquement

```powershell
Get-DnsServerZone
```

Résultat attendu : en plus de `tssr.lan` et de la zone inverse déjà créées au TD 1, apparaissent notamment :

| Zone | Rôle |
|------|------|
| `_msdcs.tssr.lan` | Localisation des contrôleurs de domaine et des services associés |
| `tssr.lan` (mise à jour) | Contient désormais des enregistrements SRV supplémentaires |

Explorer :

```powershell
Get-DnsServerResourceRecord -ZoneName "_msdcs.tssr.lan" -RRType Srv
Get-DnsServerResourceRecord -ZoneName "tssr.lan" -RRType Srv
```

Repérer notamment un enregistrement SRV pour le service LDAP :

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.tssr.lan
```

!!! success "Résultat attendu"
    Cette requête renvoie une réponse pointant vers `srv-dc01.tssr.lan`. C'est ainsi qu'un poste client localise un contrôleur de domaine sans connaître son adresse IP à l'avance : **Active Directory dépend structurellement du DNS**.

### Étape 7 — Vérifier les rôles FSMO

```powershell
Get-ADDomain | Select-Object InfrastructureMaster, RIDMaster, PDCEmulator
Get-ADForest | Select-Object SchemaMaster, DomainNamingMaster
```

Les cinq rôles doivent tous être détenus par `SRV-DC01`.

### Livrable

Dans `02-promotion-ad.md` :

- résultat de `Get-ADDomain` et `Get-ADForest` ;
- extrait pertinent de `dcdiag /v` ;
- liste des nouvelles zones DNS ;
- capture du test `Resolve-DnsName -Type SRV`.

---

## 9. Cours — DNS intégré à Active Directory

### 9.1 Zone AD-intégrée

Une zone DNS peut être stockée :

- dans un simple fichier texte sur un serveur (zone standard) ;
- ou directement **dans la base Active Directory** (zone intégrée à AD).

Une zone intégrée à AD est répliquée automatiquement avec l'annuaire vers les autres contrôleurs de domaine, sans configuration de réplication DNS séparée.

```powershell
Get-DnsServerZone | Select-Object ZoneName, ZoneType, IsDsIntegrated
```

### 9.2 Mises à jour dynamiques sécurisées

Une fois le domaine en place, il devient pertinent d'autoriser les **mises à jour dynamiques sécurisées** : seuls les ordinateurs authentifiés dans le domaine peuvent alors mettre à jour leur propre enregistrement DNS.

```powershell
Set-DnsServerPrimaryZone `
    -Name "tssr.lan" `
    -DynamicUpdate Secure
```

!!! warning "Ne jamais utiliser de mise à jour dynamique non sécurisée en production"
    L'option `NonsecureAndSecure` accepte des mises à jour non authentifiées et expose la zone à des usurpations d'enregistrements. Elle n'est pas utilisée dans ce cours.

### 9.3 Scavenging (nettoyage des enregistrements obsolètes)

Avec le temps, des enregistrements DNS obsolètes peuvent s'accumuler, notamment si des postes changent de nom ou disparaissent sans se désinscrire proprement. Le **scavenging** permet de nettoyer automatiquement ces enregistrements après une période d'inactivité.

Ce mécanisme est présenté ici pour la culture générale ; il n'est pas activé dans ce laboratoire de courte durée.

---

## 10. TD 3 — Joindre le client au domaine

**Durée : 60 minutes**

### Étape 1 — Préparer le client

Sur `CLT-01`, vérifier que le DNS préféré pointe bien vers `SRV-DC01` :

```powershell
Get-DnsClientServerAddress -AddressFamily IPv4
```

Corriger si nécessaire :

```powershell
Set-DnsClientServerAddress `
    -InterfaceAlias "Ethernet" `
    -ServerAddresses "192.168.60.10"
```

!!! danger "Cause n°1 d'échec de jonction au domaine"
    Un client configuré avec un serveur DNS public ou incorrect ne pourra pas localiser le contrôleur de domaine et échouera systématiquement à rejoindre `tssr.lan`. Ce point doit être vérifié avant toute tentative.

### Étape 2 — Vérifier la localisation du contrôleur de domaine

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.tssr.lan
Test-NetConnection 192.168.60.10 -Port 389
```

### Étape 3 — Joindre le domaine

```powershell
Add-Computer `
    -DomainName "tssr.lan" `
    -Credential (Get-Credential "TSSR\Administrateur") `
    -Restart
```

Une fenêtre demande le mot de passe du compte administrateur du domaine.

### Étape 4 — Vérifier après redémarrage

Sur l'écran de connexion, sélectionner le domaine `TSSR` et se connecter avec `Administrateur`.

```powershell
Get-ComputerInfo | Select-Object CsDomain, CsPartOfDomain
whoami
```

Résultat attendu :

```text
CsDomain       : tssr.lan
CsPartOfDomain : True
```

### Étape 5 — Vérifier côté serveur

```powershell
Get-ADComputer -Filter *
```

Le compte `CLT-01` doit apparaître, créé automatiquement lors de la jonction, dans le conteneur `Computers` par défaut.

### Étape 6 — Vérifier le canal sécurisé

```powershell
Test-ComputerSecureChannel -Verbose
```

Résultat attendu : `True`. Cette commande vérifie que la relation de confiance entre le poste et le domaine est fonctionnelle.

### Livrable

Dans `03-jonction-domaine.md` :

- preuve de résolution SRV avant jonction ;
- preuve de jonction réussie ;
- capture de `Get-ADComputer` ;
- résultat de `Test-ComputerSecureChannel`.

### Questions

1. Pourquoi la jonction au domaine échoue-t-elle presque toujours si le DNS est mal configuré ?
2. Où le compte `CLT-01` a-t-il été créé automatiquement ?

??? note "Correction"
    1. Le client localise le contrôleur de domaine par une requête DNS de type SRV. Sans DNS correct, il ne peut pas trouver ce contrôleur.
    2. Dans le conteneur `Computers` par défaut de l'annuaire, tant qu'aucune règle de redirection n'a été définie.

---

## 11. TD 4 — Explorer l'annuaire avec les outils RSAT

**Durée : 75 minutes**

### Objectif

Découvrir les consoles graphiques et les commandes équivalentes avant de manipuler l'annuaire au jour 2.

### Étape 1 — Ouvrir les consoles d'administration

Depuis le Gestionnaire de serveur, ouvrir successivement :

- **Utilisateurs et ordinateurs Active Directory** (`dsa.msc`) ;
- **Sites et services Active Directory** (`dssite.msc`) ;
- **Domaines et approbations Active Directory** (`domain.msc`) ;
- **Gestion des stratégies de groupe** (`gpmc.msc`).

Pour chacune, identifier en une phrase à quoi elle sert.

### Étape 2 — Explorer la structure par défaut

```powershell
Get-ADObject -SearchBase "DC=tssr,DC=lan" -Filter * -SearchScope OneLevel |
    Select-Object Name, ObjectClass
```

Repérer notamment les conteneurs `Users`, `Computers`, `Domain Controllers` et `System`.

!!! note "Conteneur ou unité d'organisation ?"
    `Users` et `Computers` sont des **conteneurs**, pas des unités d'organisation : on ne peut pas leur appliquer directement de stratégie de groupe. C'est l'une des raisons pour lesquelles on crée généralement ses propres OU, comme cela sera fait au TD 5.

### Étape 3 — Consulter les groupes intégrés

```powershell
Get-ADGroup -Filter * |
    Select-Object Name |
    Sort-Object Name
```

Identifier notamment `Domain Admins`, `Domain Users`, `Domain Computers`.

### Étape 4 — Consulter les FSMO en graphique

Dans **Utilisateurs et ordinateurs Active Directory** :

1. clic droit sur le domaine ;
2. **Maîtres d'opérations** ;
3. parcourir les trois onglets (RID, PDC, Infrastructure).

Comparer avec le résultat obtenu en PowerShell au TD 2.

### Étape 5 — Découvrir `Get-ADUser` sur le compte administrateur

```powershell
Get-ADUser -Identity Administrateur -Properties *
```

Repérer notamment les attributs `whenCreated`, `memberOf`, `distinguishedName`.

Expliquer, en une phrase, ce qu'est un **nom distinctif (DN)** :

```text
CN=Administrateur,CN=Users,DC=tssr,DC=lan
```

### Livrable

Dans `04-annuaire.md` :

- rôle de chacune des quatre consoles RSAT ouvertes ;
- structure des conteneurs observée ;
- distinguished name de l'administrateur ;
- explication de la différence entre conteneur et unité d'organisation.

### Bilan du jour 1

L'apprenant doit pouvoir expliquer :

> « J'ai installé un serveur DNS autonome, transformé mon serveur en contrôleur de domaine, vérifié que la localisation d'un contrôleur de domaine repose sur le DNS, et joint un poste client au domaine. »

---

# Jour 2 — Structurer l'annuaire, appliquer une GPO, déployer le DHCP

## 12. Cours — Organiser l'annuaire : OU, comptes, groupes

### 12.1 Pourquoi créer ses propres unités d'organisation

Une **unité d'organisation (OU)** permet de :

- refléter l'organisation réelle de l'entreprise ;
- appliquer des stratégies de groupe différenciées ;
- déléguer des droits d'administration limités à un périmètre précis.

### 12.2 Structure retenue pour le laboratoire

```text
tssr.lan
└── OU TSSR-Entreprise
    ├── OU Comptabilite
    ├── OU Direction
    └── OU Ordinateurs
```

| OU | Contenu prévu |
|----|----------------|
| Comptabilite | Utilisateurs du service comptabilité |
| Direction | Utilisateurs de la direction |
| Ordinateurs | Comptes ordinateurs des postes du domaine |

### 12.3 Compte utilisateur de domaine

Un compte utilisateur AD DS porte notamment :

- un nom d'ouverture de session ;
- un mot de passe soumis à la politique de domaine ;
- une appartenance à des groupes ;
- un emplacement (une OU).

### 12.4 Types et portées de groupe

| Type de groupe | Utilisation |
|-----------------|-------------|
| Groupe de sécurité | Attribution de permissions |
| Groupe de distribution | Listes de diffusion, sans utilisation pour les permissions |

| Portée | Membres possibles | Utilisable pour des ressources |
|--------|--------------------|----------------------------------|
| Domaine local | Comptes de tout domaine approuvé | Dans le domaine local uniquement |
| Globale | Comptes du même domaine | Dans tout domaine approuvé |
| Universelle | Comptes de toute la forêt | Dans toute la forêt |

!!! note "Principe couramment enseigné : A-G-DL-P"
    Une pratique répandue consiste à placer les **comptes (A)** dans des **groupes globaux (G)**, ces groupes globaux dans des **groupes de domaine local (DL)**, auxquels on attribue des **permissions (P)**.

    Ce cours illustre une version simplifiée de ce principe, sans imposer tous les niveaux dans un laboratoire à un seul domaine.

### 12.5 Différence essentielle avec le cours précédent

| Aspect | Compte local (cours précédent) | Compte de domaine (ce cours) |
|--------|----------------------------------|-------------------------------|
| Création | `New-LocalUser` sur chaque machine | `New-ADUser` une seule fois |
| Utilisable sur | Une seule machine | Tous les postes joints au domaine |
| Groupe associé | `New-LocalGroup` | `New-ADGroup` |

---

## 13. TD 5 — Créer la structure d'annuaire

**Durée : 90 minutes**

### Situation

| Utilisateur | Service | Besoin |
|-------------|---------|--------|
| Aline Durand (`aline.durand`) | Comptabilité | Compte de domaine standard |
| Bruno Martin (`bruno.martin`) | Comptabilité | Compte de domaine standard |
| Chloé Leroy (`chloe.leroy`) | Direction | Compte de domaine standard |

### Étape 1 — Créer les unités d'organisation

```powershell
New-ADOrganizationalUnit -Name "TSSR-Entreprise" -Path "DC=tssr,DC=lan"

New-ADOrganizationalUnit -Name "Comptabilite" `
    -Path "OU=TSSR-Entreprise,DC=tssr,DC=lan"

New-ADOrganizationalUnit -Name "Direction" `
    -Path "OU=TSSR-Entreprise,DC=tssr,DC=lan"

New-ADOrganizationalUnit -Name "Ordinateurs" `
    -Path "OU=TSSR-Entreprise,DC=tssr,DC=lan"
```

Vérifier :

```powershell
Get-ADOrganizationalUnit -Filter * |
    Select-Object Name, DistinguishedName
```

!!! note "Protection contre la suppression accidentelle"
    Par défaut, `New-ADOrganizationalUnit` protège l'OU créée contre une suppression accidentelle. C'est volontaire : supprimer une OU par erreur peut supprimer tout son contenu.

### Étape 2 — Créer les utilisateurs

```powershell
$politiqueMotDePasse = Read-Host `
    -Prompt "Mot de passe de laboratoire (respectant la politique de domaine)" `
    -AsSecureString

New-ADUser `
    -Name "Aline Durand" `
    -GivenName "Aline" `
    -Surname "Durand" `
    -SamAccountName "aline.durand" `
    -UserPrincipalName "aline.durand@tssr.lan" `
    -Path "OU=Comptabilite,OU=TSSR-Entreprise,DC=tssr,DC=lan" `
    -AccountPassword $politiqueMotDePasse `
    -ChangePasswordAtLogon $true `
    -Enabled $true

New-ADUser `
    -Name "Bruno Martin" `
    -GivenName "Bruno" `
    -Surname "Martin" `
    -SamAccountName "bruno.martin" `
    -UserPrincipalName "bruno.martin@tssr.lan" `
    -Path "OU=Comptabilite,OU=TSSR-Entreprise,DC=tssr,DC=lan" `
    -AccountPassword $politiqueMotDePasse `
    -ChangePasswordAtLogon $true `
    -Enabled $true

New-ADUser `
    -Name "Chloe Leroy" `
    -GivenName "Chloe" `
    -Surname "Leroy" `
    -SamAccountName "chloe.leroy" `
    -UserPrincipalName "chloe.leroy@tssr.lan" `
    -Path "OU=Direction,OU=TSSR-Entreprise,DC=tssr,DC=lan" `
    -AccountPassword $politiqueMotDePasse `
    -ChangePasswordAtLogon $true `
    -Enabled $true
```

!!! warning "Politique de mot de passe par défaut"
    La politique de domaine par défaut impose une certaine complexité et une longueur minimale. Un mot de passe trop simple provoquera une erreur explicite lors de la création du compte.

### Étape 3 — Créer les groupes

```powershell
New-ADGroup `
    -Name "GG_Comptabilite" `
    -GroupScope Global `
    -GroupCategory Security `
    -Path "OU=Comptabilite,OU=TSSR-Entreprise,DC=tssr,DC=lan"

New-ADGroup `
    -Name "GG_Direction" `
    -GroupScope Global `
    -GroupCategory Security `
    -Path "OU=Direction,OU=TSSR-Entreprise,DC=tssr,DC=lan"
```

Ajouter les membres :

```powershell
Add-ADGroupMember -Identity "GG_Comptabilite" -Members aline.durand, bruno.martin
Add-ADGroupMember -Identity "GG_Direction" -Members chloe.leroy
```

Vérifier :

```powershell
Get-ADGroupMember -Identity "GG_Comptabilite"
Get-ADGroupMember -Identity "GG_Direction"
```

### Étape 4 — Déplacer le compte du poste client dans l'OU Ordinateurs

```powershell
Get-ADComputer -Identity "CLT-01" |
    Move-ADObject -TargetPath "OU=Ordinateurs,OU=TSSR-Entreprise,DC=tssr,DC=lan"
```

Vérifier :

```powershell
Get-ADComputer -Identity "CLT-01" -Properties DistinguishedName |
    Select-Object DistinguishedName
```

!!! note "Pourquoi ce déplacement est important"
    Les stratégies de groupe s'appliquent en fonction de l'emplacement de l'objet ordinateur ou utilisateur dans l'annuaire. Un ordinateur resté dans le conteneur par défaut `Computers` n'héritera d'aucune stratégie liée à une OU.

### Étape 5 — Tester la connexion avec un compte de domaine

Sur `CLT-01`, se déconnecter puis ouvrir une session avec `TSSR\aline.durand`.

Le changement de mot de passe est demandé, conformément à `ChangePasswordAtLogon`.

Vérifier :

```powershell
whoami
whoami /groups
```

### Livrable

Dans `04-annuaire.md` (complément) :

- structure des OU ;
- liste des utilisateurs créés ;
- composition des groupes ;
- preuve de connexion avec `aline.durand`.

### Vérification

- [ ] Les trois OU existent au bon emplacement.
- [ ] Les trois utilisateurs existent et sont activés.
- [ ] Les deux groupes existent avec les bons membres.
- [ ] `CLT-01` est déplacé dans l'OU `Ordinateurs`.
- [ ] La connexion avec un compte de domaine fonctionne.

---

## 14. Cours — Stratégies de groupe : notions

### 14.1 Ce qu'est une GPO

Un **objet de stratégie de groupe (GPO)** regroupe des paramètres qui s'appliquent automatiquement aux ordinateurs ou aux utilisateurs concernés, sans intervention manuelle sur chaque poste.

### 14.2 Deux grandes parties

| Partie | S'applique à | Exemple |
|--------|---------------|---------|
| Configuration ordinateur | L'ordinateur, quel que soit l'utilisateur connecté | Message d'avertissement à l'écran de connexion |
| Configuration utilisateur | L'utilisateur, quel que soit le poste utilisé | Restriction du Panneau de configuration |

### 14.3 Où lier une GPO

Une GPO peut être liée :

- au site ;
- au domaine ;
- à une unité d'organisation.

```text
GPO créée
    ↓
liée à une OU
    ↓
s'applique aux objets ordinateurs/utilisateurs contenus dans cette OU
(et ses sous-OU, sauf blocage d'héritage)
```

!!! warning "Une GPO liée au mauvais endroit ne produit aucun effet visible"
    Une erreur fréquente chez les débutants consiste à créer une bonne GPO, mais à la lier à une OU qui ne contient ni l'ordinateur ni l'utilisateur concerné. Le paramètre semble alors « ne pas fonctionner », alors que la GPO elle-même est correcte.

### 14.4 Actualisation et vérification

| Commande | Rôle |
|----------|------|
| `gpupdate /force` | Force l'actualisation immédiate des stratégies sur un poste |
| `gpresult /r` | Affiche un résumé des GPO appliquées |
| `gpresult /h rapport.html` | Génère un rapport détaillé au format HTML |

En conditions normales, un poste actualise ses stratégies automatiquement à intervalle régulier, sans action de l'utilisateur.

---

## 15. TD 6 — Créer et appliquer une GPO

**Durée : 75 minutes**

### Objectif

Illustrer la différence entre configuration **ordinateur** et configuration **utilisateur** à travers deux réglages simples et facilement observables.

### Étape 1 — Créer la GPO

```powershell
Import-Module GroupPolicy

New-GPO -Name "GPO_Message_Connexion" `
    -Comment "Message d'avertissement affiché avant ouverture de session"
```

### Étape 2 — Configurer un message d'accueil (paramètre ordinateur)

```powershell
Set-GPRegistryValue `
    -Name "GPO_Message_Connexion" `
    -Key "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System" `
    -ValueName "LegalNoticeCaption" `
    -Type String `
    -Value "Acces reserve - TSSR"

Set-GPRegistryValue `
    -Name "GPO_Message_Connexion" `
    -Key "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System" `
    -ValueName "LegalNoticeText" `
    -Type String `
    -Value "Ce poste appartient au domaine tssr.lan. Toute utilisation est tracee."
```

Ce paramètre étant une configuration **ordinateur**, il faut lier la GPO à une OU **contenant des objets ordinateur**.

### Étape 3 — Lier la GPO à l'OU Ordinateurs

```powershell
New-GPLink `
    -Name "GPO_Message_Connexion" `
    -Target "OU=Ordinateurs,OU=TSSR-Entreprise,DC=tssr,DC=lan"
```

### Étape 4 — Appliquer et vérifier sur le client

Sur `CLT-01` :

```powershell
gpupdate /force
```

Redémarrer, ou verrouiller puis déverrouiller la session, selon le comportement observé.

Vérifier l'apparition du message avant l'écran de connexion.

```powershell
gpresult /r
```

Repérer `GPO_Message_Connexion` dans la section des GPO appliquées côté ordinateur.

### Étape 5 — Créer une deuxième GPO côté utilisateur

```powershell
New-GPO -Name "GPO_Restriction_PanneauConfig" `
    -Comment "Interdit l'acces au Panneau de configuration pour la comptabilite"

Set-GPRegistryValue `
    -Name "GPO_Restriction_PanneauConfig" `
    -Key "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" `
    -ValueName "NoControlPanel" `
    -Type DWord `
    -Value 1
```

Ce paramètre étant une configuration **utilisateur**, il doit être lié à une OU contenant des **comptes utilisateur** :

```powershell
New-GPLink `
    -Name "GPO_Restriction_PanneauConfig" `
    -Target "OU=Comptabilite,OU=TSSR-Entreprise,DC=tssr,DC=lan"
```

### Étape 6 — Tester la différenciation par utilisateur

Sur `CLT-01`, se connecter avec `bruno.martin` (Comptabilité) :

```powershell
gpupdate /force
```

Tenter d'ouvrir le Panneau de configuration : l'accès doit être bloqué.

Se déconnecter, puis se connecter avec `chloe.leroy` (Direction) :

Le Panneau de configuration doit rester accessible, car `chloe.leroy` appartient à l'OU `Direction`, non concernée par cette GPO.

### Étape 7 — Documenter avec un rapport HTML

```powershell
gpresult /h "D:\Rapports\gpresult-bruno.html"
```

Adapter le chemin si nécessaire selon la configuration du poste.

### Livrable

Dans `05-gpo.md` :

- nom, contenu et lien de chaque GPO ;
- capture du message de connexion ;
- capture prouvant le blocage du Panneau de configuration pour `bruno.martin` ;
- capture prouvant l'absence de blocage pour `chloe.leroy` ;
- extrait du rapport `gpresult`.

### Questions

1. Pourquoi la GPO du message de connexion doit-elle être liée à une OU contenant des ordinateurs plutôt que des utilisateurs ?
2. Que se passerait-il si `bruno.martin` était déplacé dans l'OU `Direction` ?

??? note "Correction"
    1. Parce que ce paramètre relève de la configuration ordinateur : il s'applique à la machine, indépendamment de l'utilisateur connecté.
    2. Il ne serait plus concerné par la GPO liée à `Comptabilite` et retrouverait l'accès au Panneau de configuration, sauf autre restriction héritée.

---

## 16. Cours — Le protocole DHCP

### 16.1 Le problème résolu par DHCP

Configurer manuellement chaque poste avec une adresse IP, un masque, une passerelle et un DNS devient rapidement ingérable à mesure que le nombre de postes augmente, et source d'erreurs (doublons d'adresses, oublis).

**DHCP** (Dynamic Host Configuration Protocol) automatise cette configuration.

### 16.2 Le mécanisme DORA

```text
Client                          Serveur DHCP
   | ---- DHCP Discover ------------> |
   | <--- DHCP Offer ------------------|
   | ---- DHCP Request ---------------> |
   | <--- DHCP Acknowledge ------------|
```

| Étape | Sigle | Description |
|-------|-------|-------------|
| 1 | Discover | Le client diffuse une demande de configuration |
| 2 | Offer | Un serveur DHCP propose une adresse |
| 3 | Request | Le client confirme qu'il accepte cette proposition |
| 4 | Acknowledge | Le serveur confirme l'attribution |

### 16.3 Vocabulaire du DHCP

| Terme | Définition |
|-------|------------|
| Étendue (scope) | Plage d'adresses IP qu'un serveur DHCP peut distribuer |
| Bail (lease) | Durée pendant laquelle une adresse est attribuée à un client |
| Exclusion | Adresse de l'étendue volontairement non distribuée |
| Réservation | Association fixe entre une adresse MAC et une adresse IP |
| Option DHCP | Paramètre additionnel transmis au client (DNS, domaine, passerelle...) |

### 16.4 Autorisation dans Active Directory

Dans un domaine Active Directory, un serveur DHCP doit être **autorisé** par un compte disposant des droits nécessaires avant de pouvoir distribuer des adresses. Ce mécanisme empêche un serveur DHCP non approuvé de perturber le réseau.

!!! danger "Un serveur DHCP non autorisé, un risque réel"
    Un serveur DHCP non maîtrisé sur le réseau peut distribuer des adresses incorrectes à des postes qui ne s'y attendent pas, provoquant des pannes réseau difficiles à diagnostiquer. C'est pourquoi Active Directory impose une autorisation explicite.

---

## 17. TD 7 — Installer et configurer le serveur DHCP

**Durée : 90 minutes**

### Objectif

Distribuer automatiquement des adresses de `192.168.60.100` à `192.168.60.150`, avec le DNS et le suffixe de domaine corrects.

### Étape 1 — Installer le rôle DHCP

```powershell
Install-WindowsFeature DHCP -IncludeManagementTools

Get-WindowsFeature DHCP
```

### Étape 2 — Ajouter les groupes de sécurité DHCP

```powershell
netsh dhcp add securitygroups
Restart-Service DHCPServer
```

### Étape 3 — Autoriser le serveur dans Active Directory

```powershell
Add-DhcpServerInDC -DnsName "srv-dc01.tssr.lan" -IPAddress "192.168.60.10"

Get-DhcpServerInDC
```

### Étape 4 — Créer l'étendue

```powershell
Add-DhcpServerv4Scope `
    -Name "Scope-LAN-TSSR" `
    -StartRange "192.168.60.100" `
    -EndRange "192.168.60.150" `
    -SubnetMask "255.255.255.0" `
    -State Active
```

### Étape 5 — Définir les options de l'étendue

```powershell
Set-DhcpServerv4OptionValue `
    -ScopeId "192.168.60.0" `
    -DnsServer "192.168.60.10" `
    -DnsDomain "tssr.lan"
```

!!! note "Absence de passerelle dans ce laboratoire"
    Le réseau isolé du laboratoire ne dispose pas de routeur. L'option 003 (routeur/passerelle) n'est donc pas configurée. En production, cette option est indispensable pour permettre aux postes de communiquer en dehors de leur sous-réseau.

Vérifier :

```powershell
Get-DhcpServerv4Scope
Get-DhcpServerv4OptionValue -ScopeId "192.168.60.0"
```

### Étape 6 — Configurer le client en DHCP

Sur `CLT-02` (ou `CLT-01` si `CLT-02` n'est pas disponible), repasser la carte réseau en obtention automatique :

```powershell
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ResetServerAddresses

Set-NetIPInterface -InterfaceAlias "Ethernet" -Dhcp Enabled

netsh interface ip set address "Ethernet" dhcp
```

### Étape 7 — Obtenir un bail et vérifier

```powershell
ipconfig /release
ipconfig /renew
ipconfig /all
```

Résultat attendu : une adresse comprise entre `192.168.60.100` et `192.168.60.150`, un masque `255.255.255.0` et un serveur DNS `192.168.60.10`.

### Étape 8 — Vérifier côté serveur

```powershell
Get-DhcpServerv4Lease -ScopeId "192.168.60.0"
```

Identifier le bail attribué au client, son adresse MAC, et sa date d'expiration.

### Étape 9 — Vérifier l'inscription DNS dynamique

Si le client a mis à jour son enregistrement DNS automatiquement :

```powershell
Resolve-DnsName clt-02.tssr.lan
```

Sur le serveur :

```powershell
Get-DnsServerResourceRecord -ZoneName "tssr.lan" -Name "clt-02"
```

!!! note "DHCP peut inscrire le client dans le DNS à sa place"
    Un serveur DHCP Windows peut être configuré pour mettre à jour dynamiquement les enregistrements DNS d'un client, notamment lorsque celui-ci ne le fait pas lui-même. Cette configuration se trouve dans les propriétés DNS du serveur DHCP (onglet DNS des propriétés IPv4).

### Livrable

Dans `06-dhcp.md` :

- paramètres de l'étendue ;
- options configurées ;
- preuve du bail attribué ;
- preuve de résolution DNS du client ayant obtenu une adresse par DHCP.

---

## 18. TD 8 — Réservations, exclusions et DNS dynamique

**Durée : 75 minutes**

### Objectif

Ajouter une exclusion, une réservation, et observer le renouvellement de bail.

### Étape 1 — Créer une exclusion

```powershell
Add-DhcpServerv4ExclusionRange `
    -ScopeId "192.168.60.0" `
    -StartRange "192.168.60.100" `
    -EndRange "192.168.60.109"
```

Cette plage reste réservée à des usages manuels (imprimantes, serveurs futurs) et ne sera jamais distribuée automatiquement.

Vérifier :

```powershell
Get-DhcpServerv4ExclusionRange -ScopeId "192.168.60.0"
```

### Étape 2 — Créer une réservation

Relever l'adresse MAC du client :

```powershell
Get-NetAdapter | Select-Object Name, MacAddress
```

Créer la réservation, en adaptant l'adresse MAC observée :

```powershell
Add-DhcpServerv4Reservation `
    -ScopeId "192.168.60.0" `
    -IPAddress "192.168.60.130" `
    -ClientId "AA-BB-CC-DD-EE-FF" `
    -Description "Reservation pedagogique CLT-02"
```

Vérifier :

```powershell
Get-DhcpServerv4Reservation -ScopeId "192.168.60.0"
```

### Étape 3 — Vérifier l'effet de la réservation

Sur le client concerné :

```powershell
ipconfig /release
ipconfig /renew
ipconfig /all
```

Résultat attendu : le client obtient systématiquement l'adresse réservée `192.168.60.130`.

### Étape 4 — Réduire la durée de bail pour observer un renouvellement

```powershell
Set-DhcpServerv4Scope `
    -ScopeId "192.168.60.0" `
    -LeaseDuration 00:10:00
```

Renouveler puis observer :

```powershell
ipconfig /renew
Get-DhcpServerv4Lease -ScopeId "192.168.60.0" |
    Select-Object IPAddress, ClientId, AddressState, LeaseExpiryTime
```

Rétablir une durée réaliste après le test :

```powershell
Set-DhcpServerv4Scope `
    -ScopeId "192.168.60.0" `
    -LeaseDuration 08:00:00:00
```

### Étape 5 — Provoquer et corriger un épuisement d'étendue (exercice guidé)

Le formateur peut réduire volontairement l'étendue à deux adresses sur une VM de démonstration, connecter plusieurs clients successivement, et observer le message d'échec DHCP lorsque l'étendue est épuisée.

```powershell
Get-DhcpServerv4Statistics
```

Cette commande affiche notamment le nombre d'adresses disponibles et utilisées, utile pour diagnostiquer un épuisement d'étendue en production.

### Livrable

Dans `06-dhcp.md` (complément) :

- exclusion créée ;
- réservation créée avec l'adresse MAC ;
- preuve que le client obtient bien l'adresse réservée ;
- observation du bail après réduction de sa durée.

### Vérification

- [ ] Le serveur DHCP est autorisé dans l'annuaire.
- [ ] L'étendue est active avec les bonnes options.
- [ ] Une exclusion est en place.
- [ ] Une réservation fonctionne correctement.
- [ ] Le client obtient une adresse cohérente avec le suffixe DNS du domaine.

### Bilan du jour 2

L'apprenant doit pouvoir expliquer :

> « J'ai structuré l'annuaire avec des OU, des utilisateurs et des groupes, appliqué des stratégies de groupe différenciées selon l'emplacement des objets, puis déployé un serveur DHCP autorisé, avec exclusion et réservation. »

---

# Jour 3 — WINS, intégration des services et diagnostic

## 19. Cours — WINS et résolution NetBIOS : un service historique

### 19.1 Le nom NetBIOS

Avant la généralisation du DNS dans les réseaux Windows, les machines se désignaient par un **nom NetBIOS**, limité à 15 caractères significatifs, sans hiérarchie.

```text
Nom NetBIOS :  SRV-DC01
Nom DNS      :  srv-dc01.tssr.lan
```

Le nom NetBIOS reste présent aujourd'hui pour des raisons de compatibilité, même si la résolution DNS est désormais privilégiée.

### 19.2 Trois méthodes historiques de résolution NetBIOS

| Méthode | Principe | Limite |
|---------|----------|--------|
| Diffusion (broadcast) | La machine interroge tout le réseau local | Ne franchit pas les routeurs, trafic parasite |
| Fichier LMHOSTS | Fichier local de correspondances | Maintenance manuelle sur chaque poste |
| WINS | Serveur centralisant les correspondances nom NetBIOS / IP | Nécessite un serveur dédié |

### 19.3 Rôle historique de WINS

**WINS** (Windows Internet Name Service) a permis, dans les années 1990 et 2000, de résoudre des noms NetBIOS **à travers plusieurs sous-réseaux**, sans dépendre de la diffusion locale.

### 19.4 Pourquoi WINS est aujourd'hui largement obsolète

- le DNS, combiné à Active Directory, couvre la quasi-totalité des besoins modernes de résolution de noms ;
- IPv6 ne prend pas en charge NetBIOS ;
- Microsoft recommande depuis longtemps la migration vers des solutions fondées sur le DNS.

WINS reste néanmoins parfois rencontré en entreprise pour assurer la compatibilité d'applications ou d'équipements anciens qui n'ont pas été mis à jour.

!!! warning "Ne pas déployer WINS par réflexe"
    Installer WINS dans une infrastructure neuve sans besoin identifié ajoute un service supplémentaire à maintenir et à sécuriser, sans bénéfice réel. Ce TD a une vocation principalement pédagogique et patrimoniale.

### 19.5 Les types de nœuds NetBIOS

| Type de nœud | Comportement |
|---------------|--------------|
| B (Broadcast) | Résolution uniquement par diffusion locale |
| P (Peer-to-peer) | Résolution uniquement via un serveur WINS |
| M (Mixed) | Diffusion d'abord, puis WINS |
| H (Hybrid) | WINS d'abord, puis diffusion — comportement par défaut le plus courant |

---

## 20. TD 9 — Installer et tester un serveur WINS

**Durée : 60 minutes**

### Objectif

Installer WINS, configurer deux clients pour l'utiliser, et observer la résolution d'un nom NetBIOS à travers le serveur plutôt que par diffusion.

### Étape 1 — Installer le rôle WINS

```powershell
Install-WindowsFeature WINS -IncludeManagementTools

Get-Service WINS
```

### Étape 2 — Configurer les clients pour utiliser le serveur WINS

Sur `CLT-01` et `CLT-02` :

```powershell
netsh interface ip set wins "Ethernet" static 192.168.60.10
```

Vérifier :

```powershell
netsh interface ip show wins "Ethernet"
```

### Étape 3 — Observer l'enregistrement des noms

Sur chaque client, forcer une nouvelle inscription NetBIOS :

```powershell
nbtstat -RR
```

Sur le serveur, ouvrir la console **WINS** (`wins.msc`), ou utiliser PowerShell :

```powershell
Get-WinsServerStatistics
Get-WinsDatabaseRecord | Select-Object RecordName, RecordType, IPAddress
```

Repérer les enregistrements correspondant à `CLT-01` et `CLT-02`.

### Étape 4 — Tester la résolution NetBIOS

Depuis `CLT-01` :

```powershell
nbtstat -a CLT-02
ping CLT-02
```

Ce test réussit **sans qu'aucun enregistrement DNS** ne soit nécessaire : c'est le serveur WINS qui a fourni la correspondance nom/adresse.

### Étape 5 — Comparer avec l'absence de WINS

Le formateur peut, à titre de démonstration sur une VM isolée du domaine, retirer la configuration WINS d'un client et constater que la résolution du même nom court échoue en dehors du sous-réseau local, ou dépend uniquement de la diffusion.

### Étape 6 — Positionner WINS par rapport au DNS

```powershell
Resolve-DnsName clt-02.tssr.lan
nbtstat -a CLT-02
```

Les deux commandes aboutissent, mais par des mécanismes complètement différents : la première interroge le DNS, la seconde interroge WINS (ou le cache NetBIOS local).

!!! note "Une alternative moderne : la zone GlobalNames"
    Windows Server propose la **zone GlobalNames**, une zone DNS spéciale permettant de résoudre des noms courts uniques dans toute la forêt, sans les inconvénients de NetBIOS. Elle constitue une alternative moderne à WINS pour les besoins de noms courts, sans être mise en œuvre dans ce cours.

### Livrable

Dans `07-wins.md` :

- preuve d'installation du service WINS ;
- capture des enregistrements de la base WINS ;
- preuve de résolution NetBIOS entre les deux clients ;
- explication de la différence entre résolution WINS et résolution DNS.

---

## 21. Cours — Interactions entre DNS, AD DS, DHCP et WINS

### 21.1 Vue d'ensemble

```text
                      Active Directory Domain Services
                                    |
              (dépend de la localisation via)
                                    |
                                   DNS
                     /                          \
        mis à jour dynamiquement par      complété historiquement par
             DHCP (option et bail)                 WINS (NetBIOS)
```

### 21.2 Ce que chaque service apporte

| Service | Question à laquelle il répond |
|---------|-------------------------------|
| DNS | Quel est le nom ou l'adresse correspondant à... ? |
| AD DS | Qui est cet utilisateur ou cet ordinateur, et que peut-il faire ? |
| DHCP | Quelle configuration réseau ce poste doit-il utiliser ? |
| WINS | Quelle adresse correspond à ce nom NetBIOS historique ? |

### 21.3 Dépendances à retenir

- **Active Directory dépend du DNS** pour la localisation des contrôleurs de domaine (enregistrements SRV).
- **DHCP peut alimenter le DNS** en inscrivant automatiquement les clients.
- **DHCP doit être autorisé par Active Directory** avant de fonctionner dans un domaine.
- **WINS ne dépend pas du DNS ni d'Active Directory** : c'est un service historiquement indépendant, ce qui explique qu'il continue parfois à fonctionner même lorsque le DNS ou l'annuaire rencontrent un problème.

### 21.4 Ordre de dépannage conseillé

Lorsqu'un poste rencontre un problème d'authentification ou d'accès réseau dans un domaine, il est généralement pertinent de vérifier dans cet ordre :

1. la configuration IP et DNS du poste ;
2. la résolution DNS du contrôleur de domaine ;
3. l'état des services sur le contrôleur de domaine ;
4. le bail DHCP en cours ;
5. l'appartenance aux groupes et l'application des GPO ;
6. en dernier recours, la résolution NetBIOS/WINS, aujourd'hui secondaire.

---

## 22. TD 10 — Diagnostiquer un incident d'infrastructure

**Durée : 90 minutes**

### Méthode

1. qualifier le symptôme ;
2. délimiter le périmètre (un poste, un service, tout le domaine) ;
3. vérifier la configuration réseau du poste concerné ;
4. vérifier la résolution DNS ;
5. vérifier l'état des services sur le serveur ;
6. formuler une hypothèse et la tester ;
7. corriger, puis valider depuis le client.

### Scénario A — Le client ne parvient plus à ouvrir de session de domaine

Le formateur modifie, sur `CLT-01`, le serveur DNS préféré vers une adresse incorrecte.

Sur le client :

```powershell
Get-DnsClientServerAddress -AddressFamily IPv4
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.tssr.lan
```

La deuxième commande doit échouer, orientant immédiatement le diagnostic vers la configuration DNS plutôt que vers l'annuaire lui-même.

Corriger :

```powershell
Set-DnsClientServerAddress `
    -InterfaceAlias "Ethernet" `
    -ServerAddresses "192.168.60.10"
```

Vérifier :

```powershell
Test-ComputerSecureChannel -Verbose
```

### Scénario B — Le client n'obtient plus d'adresse IP

Le formateur arrête temporairement le service DHCP :

```powershell
Stop-Service DHCPServer
```

Sur le client :

```powershell
ipconfig /release
ipconfig /renew
```

Observer l'échec, puis vérifier sur le serveur :

```powershell
Get-Service DHCPServer
```

Corriger :

```powershell
Start-Service DHCPServer
```

Revalider :

```powershell
ipconfig /renew
ipconfig /all
```

### Scénario C — La GPO ne semble plus s'appliquer

Le formateur déplace `CLT-01` hors de l'OU `Ordinateurs`, par exemple vers le conteneur `Computers` par défaut.

Sur le client :

```powershell
gpupdate /force
gpresult /r
```

Constater la disparition de `GPO_Message_Connexion` de la liste des GPO appliquées.

Diagnostiquer :

```powershell
Get-ADComputer -Identity "CLT-01" -Properties DistinguishedName |
    Select-Object DistinguishedName
```

Corriger :

```powershell
Get-ADComputer -Identity "CLT-01" |
    Move-ADObject -TargetPath "OU=Ordinateurs,OU=TSSR-Entreprise,DC=tssr,DC=lan"
```

Revalider avec `gpupdate /force` puis `gpresult /r`.

### Fiche de diagnostic à compléter pour chaque scénario

```text
Symptôme :
Périmètre touché :
Commandes de diagnostic utilisées :
Résultat observé :
Hypothèse retenue :
Correction appliquée :
Preuve de rétablissement :
```

### Livrable

Dans `08-diagnostic.md`, les trois fiches complétées.

---

## 23. Cours — Méthode de diagnostic et préparation de l'évaluation

### 23.1 Grille de diagnostic par couches, appliquée à ce cours

| Couche | Question | Vérification |
|--------|----------|---------------|
| Réseau | Le poste a-t-il une configuration IP cohérente ? | `ipconfig /all` |
| DNS | Le poste résout-il le domaine et le contrôleur ? | `Resolve-DnsName` |
| Annuaire | Le compte ou l'ordinateur existe-t-il au bon endroit ? | `Get-ADUser`, `Get-ADComputer` |
| Sécurité | Le canal sécurisé et l'appartenance aux groupes sont-ils corrects ? | `Test-ComputerSecureChannel`, `whoami /groups` |
| Stratégie | La GPO attendue est-elle appliquée ? | `gpresult /r` |
| Adressage | Le bail DHCP est-il valide et cohérent ? | `Get-DhcpServerv4Lease` |
| Compatibilité historique | La résolution NetBIOS fonctionne-t-elle si nécessaire ? | `nbtstat -a` |

### 23.2 Ne pas confondre les symptômes

| Symptôme | Piste à privilégier en premier |
|----------|----------------------------------|
| Le poste ne peut pas rejoindre le domaine | Configuration DNS du poste |
| Le poste rejoint le domaine mais l'ouverture de session échoue ensuite | Heure système, canal sécurisé, mot de passe |
| Le poste n'a pas d'adresse IP valide | Service DHCP, étendue, câble ou commutateur virtuel |
| La GPO ne produit pas d'effet | Emplacement de l'objet dans l'annuaire, portée de la GPO |
| Un ancien partage ne répond plus par son nom court | Résolution NetBIOS/WINS |

---

## 24. TD 11 — Mise en situation professionnelle

**Durée : 135 minutes**

### Scénario

La direction souhaite une recette complète de l'infrastructure avant sa mise en service.

### Mission 1 — Vérifier le socle (20 min)

- `SRV-DC01` répond aux requêtes DNS ;
- `SRV-DC01` est bien contrôleur de domaine du domaine `tssr.lan` ;
- les cinq rôles FSMO sont détenus par `SRV-DC01`.

### Mission 2 — Recetter l'annuaire (25 min)

- présence des OU, utilisateurs et groupes attendus ;
- connexion réussie avec un compte de chaque OU ;
- vérification des appartenances de groupe.

### Mission 3 — Recetter les stratégies de groupe (20 min)

- message de connexion visible sur le poste ;
- restriction du Panneau de configuration active pour la comptabilité, inactive pour la direction ;
- rapport `gpresult` à l'appui.

### Mission 4 — Recetter le DHCP (25 min)

- étendue active avec les bonnes options ;
- exclusion en place ;
- réservation fonctionnelle ;
- résolution DNS du client ayant obtenu un bail.

### Mission 5 — Recetter WINS (15 min)

- service démarré ;
- résolution NetBIOS fonctionnelle entre deux postes ;
- explication écrite justifiant la conservation ou non de ce service dans un contexte réel.

### Mission 6 — Traiter un incident (20 min)

Le formateur choisit **un seul incident** parmi ceux du TD 10, ou une variante proche, sans en informer l'apprenant à l'avance.

### Mission 7 — Documentation finale (10 min)

Compléter `09-recette-finale.md` :

```text
1. Domaine et contrôleur de domaine
2. Zones et enregistrements DNS clés
3. Structure de l'annuaire (OU, utilisateurs, groupes)
4. GPO en place et leur portée
5. Étendue DHCP, exclusions et réservations
6. Service WINS et justification de son maintien ou de son retrait
7. Incident traité durant la recette
8. Limites connues du laboratoire
```

### Barème proposé

| Critère | Points |
|---------|-------:|
| Socle DNS et contrôleur de domaine | 15 |
| Structure d'annuaire et comptes | 15 |
| Stratégies de groupe correctement liées et vérifiées | 15 |
| DHCP autorisé, étendue, exclusion, réservation | 20 |
| WINS installé et testé, limites expliquées | 10 |
| Diagnostic de l'incident argumenté | 15 |
| Documentation claire et exploitable | 10 |
| **Total** | **100** |

**Seuil indicatif de validation : 70/100**, sous réserve des critères essentiels suivants :

- la localisation du contrôleur de domaine par DNS est démontrée ;
- au moins une GPO produit un effet vérifiable et correctement expliqué ;
- le DHCP distribue des adresses cohérentes avec les options attendues ;
- l'incident est corrigé et la correction est prouvée depuis le client.

---

## 25. Bilan et consolidation — 45 minutes

### Quiz

1. Pourquoi Active Directory dépend-il structurellement du DNS ?
2. Quelle est la différence entre une zone directe et une zone inverse ?
3. Qu'est-ce qu'un enregistrement SRV, et à quoi sert-il dans un domaine Active Directory ?
4. Pourquoi un seul contrôleur de domaine dans ce laboratoire est-il une simplification pédagogique ?
5. Quelle est la différence entre un conteneur et une unité d'organisation ?
6. Une GPO contenant un réglage de configuration utilisateur doit-elle être liée à une OU d'ordinateurs ou d'utilisateurs ?
7. Pourquoi un serveur DHCP doit-il être autorisé dans Active Directory ?
8. À quoi sert une réservation DHCP ?
9. Pourquoi WINS est-il aujourd'hui considéré comme obsolète ?
10. Quel service continuerait probablement à fonctionner si le DNS tombait en panne : WINS ou la localisation d'un contrôleur de domaine ?

??? note "Correction du quiz"
    1. Parce qu'un client localise un contrôleur de domaine par des requêtes DNS de type SRV, indispensables à l'authentification et à la réplication.
    2. La zone directe traduit un nom en adresse IP ; la zone inverse traduit une adresse IP en nom.
    3. Un enregistrement SRV localise un service réseau, notamment les contrôleurs de domaine et les services LDAP/Kerberos associés.
    4. En production, plusieurs contrôleurs de domaine assurent la tolérance de panne et la répartition de charge, absentes ici par choix pédagogique.
    5. Une unité d'organisation peut recevoir des stratégies de groupe et une délégation ; un conteneur par défaut ne le permet pas directement.
    6. À une OU contenant des comptes utilisateur, car ce type de réglage s'applique à l'utilisateur, pas à la machine.
    7. Pour empêcher un serveur DHCP non maîtrisé de distribuer des adresses incorrectes sur le réseau.
    8. À garantir qu'un poste identifié reçoit toujours la même adresse IP via DHCP.
    9. Parce que le DNS combiné à Active Directory couvre désormais l'essentiel des besoins, et qu'IPv6 ne prend pas en charge NetBIOS.
    10. WINS, car il constitue un mécanisme historiquement indépendant du DNS et de l'annuaire.

### Autoévaluation

| Compétence | 1 : à revoir | 2 : avec le support | 3 : autonome |
|------------|:---:|:---:|:---:|
| Créer une zone et des enregistrements DNS | | | |
| Promouvoir un contrôleur de domaine | | | |
| Joindre un poste au domaine | | | |
| Créer une structure d'OU, d'utilisateurs et de groupes | | | |
| Créer et lier une GPO en comprenant sa portée | | | |
| Installer et autoriser un serveur DHCP | | | |
| Créer une exclusion et une réservation DHCP | | | |
| Installer et tester un serveur WINS | | | |
| Diagnostiquer un incident lié au DNS, à l'AD ou au DHCP | | | |

---

## 26. Problèmes fréquents et solutions

### Problème — La promotion en contrôleur de domaine échoue

Vérifier :

```powershell
Get-NetIPConfiguration
```

- l'adresse IP doit être statique ;
- le nom du serveur ne doit pas contenir de caractères non pris en charge ;
- l'horloge système doit être correcte.

### Problème — Le client ne trouve pas le domaine lors de la jonction

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.tssr.lan
Get-DnsClientServerAddress -AddressFamily IPv4
```

Corriger systématiquement le DNS du client avant toute nouvelle tentative de jonction.

### Problème — Impossible d'ouvrir une session de domaine après jonction

```powershell
Test-ComputerSecureChannel -Verbose
```

Si le résultat est `False` :

```powershell
Test-ComputerSecureChannel -Repair -Credential (Get-Credential "TSSR\Administrateur")
```

Vérifier également la concordance de l'heure entre le poste et le contrôleur de domaine.

### Problème — La GPO ne s'applique jamais

Vérifier dans l'ordre :

1. l'emplacement réel de l'objet concerné (`Get-ADComputer` ou `Get-ADUser` avec `DistinguishedName`) ;
2. le lien de la GPO (`Get-GPInheritance -Target "OU=..."`) ;
3. l'exécution d'un `gpupdate /force` ;
4. le rapport `gpresult /h`.

### Problème — Le client n'obtient pas d'adresse IP par DHCP

```powershell
Get-Service DHCPServer
Get-DhcpServerv4Scope
Get-DhcpServerv4Statistics
```

Vérifier notamment que l'étendue est active et non épuisée, et que le serveur DHCP est bien autorisé dans l'annuaire.

### Problème — Deux postes obtiennent le même nom NetBIOS attendu, mais des adresses différentes

Vérifier la base WINS :

```powershell
Get-WinsDatabaseRecord | Where-Object RecordName -like "*NOM*"
```

Un enregistrement obsolète non nettoyé peut provoquer une confusion ; une nouvelle inscription avec `nbtstat -RR` peut résoudre l'incohérence.

---

## 27. Aide-mémoire

### DNS

| Commande | Description |
|----------|--------------|
| `Get-DnsServerZone` | Lister les zones DNS |
| `Add-DnsServerPrimaryZone` | Créer une zone primaire |
| `Add-DnsServerResourceRecordA` | Créer un enregistrement A |
| `Get-DnsServerResourceRecord` | Lister les enregistrements d'une zone |
| `Resolve-DnsName` | Tester une résolution côté client |
| `Set-DnsClientServerAddress` | Définir le serveur DNS d'une interface |

### Active Directory

| Commande | Description |
|----------|--------------|
| `Install-ADDSForest` | Créer une nouvelle forêt et promouvoir le premier DC |
| `Get-ADDomain` / `Get-ADForest` | Consulter les informations du domaine/de la forêt |
| `New-ADOrganizationalUnit` | Créer une unité d'organisation |
| `New-ADUser` / `New-ADGroup` | Créer un utilisateur / un groupe |
| `Add-ADGroupMember` | Ajouter un membre à un groupe |
| `Move-ADObject` | Déplacer un objet dans l'annuaire |
| `dcdiag /v` | Diagnostiquer l'état d'un contrôleur de domaine |
| `Test-ComputerSecureChannel` | Vérifier la relation de confiance poste/domaine |

### Stratégies de groupe

| Commande | Description |
|----------|--------------|
| `New-GPO` | Créer une nouvelle GPO |
| `Set-GPRegistryValue` | Définir un paramètre de registre via une GPO |
| `New-GPLink` | Lier une GPO à un domaine, un site ou une OU |
| `gpupdate /force` | Forcer l'actualisation des stratégies sur un poste |
| `gpresult /r` | Afficher les GPO appliquées |

### DHCP

| Commande | Description |
|----------|--------------|
| `Add-DhcpServerInDC` | Autoriser le serveur DHCP dans Active Directory |
| `Add-DhcpServerv4Scope` | Créer une étendue |
| `Set-DhcpServerv4OptionValue` | Définir des options d'étendue |
| `Add-DhcpServerv4ExclusionRange` | Créer une exclusion |
| `Add-DhcpServerv4Reservation` | Créer une réservation |
| `Get-DhcpServerv4Lease` | Lister les baux attribués |
| `ipconfig /release` / `/renew` | Libérer/renouveler un bail côté client |

### WINS

| Commande | Description |
|----------|--------------|
| `Install-WindowsFeature WINS` | Installer le service WINS |
| `netsh interface ip set wins` | Configurer le serveur WINS d'un client |
| `nbtstat -RR` | Forcer une nouvelle inscription NetBIOS |
| `nbtstat -a NOM` | Résoudre un nom NetBIOS |
| `Get-WinsDatabaseRecord` | Consulter la base WINS |

---

## 28. Checklist finale de livraison

### DNS

- [ ] Zone directe et zone inverse créées.
- [ ] Enregistrements A, PTR et CNAME vérifiés.
- [ ] Zone AD-intégrée avec mises à jour sécurisées.
- [ ] Enregistrements SRV du domaine résolus avec succès.

### Active Directory

- [ ] Contrôleur de domaine promu et diagnostiqué avec `dcdiag`.
- [ ] Rôles FSMO identifiés.
- [ ] Structure d'OU conforme au besoin.
- [ ] Utilisateurs et groupes créés et vérifiés.
- [ ] Client joint au domaine et canal sécurisé fonctionnel.

### Stratégies de groupe

- [ ] Une GPO côté ordinateur fonctionnelle et vérifiée.
- [ ] Une GPO côté utilisateur fonctionnelle et vérifiée.
- [ ] Portée de chaque GPO comprise et documentée.

### DHCP

- [ ] Serveur autorisé dans l'annuaire.
- [ ] Étendue active avec les bonnes options.
- [ ] Exclusion et réservation en place.
- [ ] Bail vérifié côté client et côté serveur.

### WINS

- [ ] Service installé et démarré.
- [ ] Résolution NetBIOS testée entre deux postes.
- [ ] Limites et obsolescence du service expliquées.

### Diagnostic et documentation

- [ ] Au moins un incident diagnostiqué et corrigé avec preuve.
- [ ] Livrables complets et déposés hors des VM.
- [ ] Aucun mot de passe présent dans la documentation.

---

## 29. Glossaire

AD DS
:   Active Directory Domain Services, service d'annuaire centralisant identités et règles de sécurité.

Bail (lease)
:   Durée pendant laquelle une adresse IP attribuée par DHCP reste valide.

Contrôleur de domaine
:   Serveur hébergeant une copie de la base d'annuaire et assurant l'authentification.

DHCP
:   Protocole permettant l'attribution automatique de paramètres réseau à un client.

DNS
:   Système hiérarchique de résolution de noms en adresses, et inversement.

Domaine
:   Espace de gestion regroupant des objets partageant une base de sécurité commune.

FQDN
:   Nom de domaine complet, incluant le nom d'hôte et le suffixe de domaine.

FSMO
:   Cinq rôles particuliers ne pouvant être détenus que par un contrôleur de domaine à la fois pour certaines opérations.

Forêt
:   Ensemble d'un ou plusieurs domaines partageant un schéma et une configuration communs.

GPO
:   Objet de stratégie de groupe regroupant des paramètres appliqués automatiquement.

NetBIOS
:   Ancien mécanisme de nommage et de résolution utilisé dans les réseaux Windows.

OU
:   Unité d'organisation, conteneur permettant d'organiser des objets et d'appliquer des stratégies.

Réservation
:   Association fixe entre une adresse MAC et une adresse IP dans une étendue DHCP.

SRV
:   Type d'enregistrement DNS permettant de localiser un service réseau.

TTL
:   Durée de vie d'une information en cache avant nouvelle interrogation.

WINS
:   Service historique de résolution de noms NetBIOS à travers plusieurs sous-réseaux.

Zone AD-intégrée
:   Zone DNS stockée dans la base Active Directory et répliquée avec l'annuaire.

---

## 30. Ressources

- [Vue d'ensemble du DNS Windows Server](https://learn.microsoft.com/fr-fr/windows-server/networking/dns/dns-top) — Fonctionnement et administration du DNS.
- [Vue d'ensemble d'Active Directory Domain Services](https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview) — Concepts fondamentaux de l'annuaire.
- [Module ADDSDeployment](https://learn.microsoft.com/en-us/powershell/module/addsdeployment/) — Cmdlets de promotion et de gestion des contrôleurs de domaine.
- [Module ActiveDirectory](https://learn.microsoft.com/en-us/powershell/module/activedirectory/) — Cmdlets de gestion des utilisateurs, groupes et OU.
- [Vue d'ensemble des stratégies de groupe](https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview) — Fonctionnement des GPO.
- [Vue d'ensemble du serveur DHCP](https://learn.microsoft.com/fr-fr/windows-server/networking/technologies/dhcp/dhcp-top) — Installation et gestion du DHCP.
- [Documentation WINS](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh831825(v=ws.11)) — Documentation historique du service WINS.


!!! success "Compétence centrale à retenir"
    Une infrastructure Windows repose sur des services **interdépendants** : le DNS localise, l'annuaire identifie et autorise, le DHCP configure automatiquement, et WINS rappelle qu'un service ancien peut perdurer par nécessité de compatibilité.

    Le travail du technicien est de comprendre **ces dépendances**, de savoir **où commencer un diagnostic**, et de **documenter** ce qui a été mis en place pour qu'un collègue puisse le reprendre.
