---
title: "Découvrir les fonctions serveur de Windows Server — Cours et travaux dirigés TSSR"
date: 2026-05-02
author: Nicolas BODAINE
tags:
  - windows-server
  - tssr
  - administration-systeme
  - virtualisation
  - travaux-diriges
  - stockage
  - smb
  - iis
  - sauvegarde
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

# Découvrir les fonctions serveur de Windows Server

!!! abstract "Résumé"
    Ce support propose **21 heures de formation**, réparties sur **3 journées de 7 heures**, pour découvrir l’administration d’un serveur Windows autonome.

    Les apprenants installent et administrent un environnement virtualisé, gèrent des utilisateurs locaux, préparent des volumes, publient des dossiers partagés, appliquent des permissions, mettent en place des quotas, hébergent un site web et réalisent une sauvegarde suivie d’une restauration.

    Le parcours comprend **15 heures de travaux dirigés et de mise en situation**, ainsi que **6 heures d’explications, de démonstrations et de corrections**.

    Les services DNS, AD, DHCP et WINS sont volontairement exclus : ils feront l’objet du cours suivant.

| Propriété | Valeur |
|-----------|--------|
| Public | Techniciens Supérieurs en Systèmes et Réseaux — niveau Bac +2 |
| Difficulté | Débutant |
| Durée | 3 jours × 7 heures, soit 21 heures pédagogiques |
| OS serveur | Windows Server 2025 Standard avec Expérience de bureau |
| OS client | Windows 11 Pro |
| Organisation | Travail individuel ou en binôme |
| Modalité dominante | Travaux dirigés sur machines virtuelles |
| Dernière mise à jour | 2026-05-02 |

!!! note "Convention de lecture"
    - Une commande indiquée **sur le serveur** s’exécute sur `SRV-FIC01`.
    - Une commande indiquée **sur le client** s’exécute sur `CLT-01`.
    - Les commandes d’administration sont exécutées dans **Windows PowerShell 5.1 ouvert en tant qu’administrateur**, sauf indication contraire.
    - Les commandes de test sur un lecteur réseau sont exécutées dans la **même session utilisateur que celle qui a établi la connexion au partage**.
    - Les noms des menus peuvent légèrement varier selon la langue et les mises à jour de Windows.

---

## 1. Contexte professionnel

Une petite structure souhaite disposer d’un serveur autonome pour :

- centraliser des documents ;
- séparer les droits de lecture et de modification ;
- éviter qu’un utilisateur remplisse tout l’espace disponible ;
- publier une page intranet ;
- administrer le serveur à distance ;
- surveiller son fonctionnement ;
- récupérer un fichier supprimé accidentellement.

Vous êtes le technicien chargé de préparer ce serveur, de vérifier son fonctionnement et de rédiger une documentation exploitable par un collègue.

Le serveur fonctionne dans un **groupe de travail**, sans infrastructure centralisée d’identités.

!!! warning "Périmètre pédagogique"
    L’accès aux services se fait principalement par **adresse IP**. Aucun service exclu du programme n’est installé ou configuré.

    Le laboratoire sert à comprendre les mécanismes. Il ne constitue pas, à lui seul, une architecture de production complète.

---

## 2. Objectifs pédagogiques

À l’issue des trois journées, l’apprenant doit être capable de :

1. expliquer la différence entre un poste client et un serveur ;
2. distinguer rôle, fonctionnalité, service et protocole ;
3. installer Windows Server dans une machine virtuelle ;
4. effectuer une configuration initiale simple ;
5. gérer des utilisateurs et des groupes locaux ;
6. préparer un disque et créer un volume NTFS ;
7. publier un partage SMB ;
8. expliquer l’articulation entre permissions de partage et permissions NTFS ;
9. mettre en place un quota et un filtrage de fichiers avec FSRM ;
10. publier une page web statique avec IIS ;
11. autoriser un accès réseau sans désactiver le pare-feu ;
12. consulter les services, journaux et indicateurs de ressources ;
13. automatiser un contrôle simple avec PowerShell et le Planificateur de tâches ;
14. sauvegarder des données et démontrer leur restauration ;
15. diagnostiquer un incident simple en s’appuyant sur des preuves.

### Critère de réussite général

Un service n’est pas considéré comme opérationnel uniquement parce que son installation se termine sans erreur.

Il faut démontrer :

- qu’il fonctionne depuis le client ;
- qu’il est accessible aux personnes autorisées ;
- qu’il refuse les opérations non autorisées ;
- que son état est vérifiable ;
- que sa configuration est documentée.

---

## 3. Organisation des trois journées

Les durées ci-dessous correspondent au **temps pédagogique effectif**. Les pauses et le déjeuner sont à ajouter dans l’organisation quotidienne.

### Jour 1 — Préparer le serveur et publier un partage

| Séquence | Durée | Modalité |
|----------|------:|----------|
| Architecture client-serveur et environnement de laboratoire | 30 min | Cours et démonstration |
| TD 1 — Installer et configurer le serveur | 90 min | Pratique |
| Comptes, groupes et principes de sécurité | 45 min | Cours |
| TD 2 — Créer les identités locales et administrer à distance | 60 min | Pratique |
| Disques, volumes et systèmes de fichiers | 30 min | Cours |
| TD 3 — Préparer les volumes de données et de sauvegarde | 75 min | Pratique |
| TD 4 — Publier un partage SMB sécurisé | 90 min | Pratique |
| **Total** | **420 min** | **7 h** |

### Jour 2 — Maîtriser les accès et déployer des services

| Séquence | Durée | Modalité |
|----------|------:|----------|
| Comprendre les permissions effectives | 30 min | Cours |
| TD 5 — Tester et corriger les permissions | 75 min | Pratique |
| Gestion des ressources du serveur de fichiers | 30 min | Cours |
| TD 6 — Configurer quotas et filtrage FSRM | 75 min | Pratique |
| Fonctionnement d’un serveur web IIS | 30 min | Cours |
| TD 7 — Publier un intranet statique | 90 min | Pratique |
| Services, événements et supervision | 30 min | Cours |
| TD 8 — Diagnostiquer un incident IIS | 60 min | Pratique |
| **Total** | **420 min** | **7 h** |

### Jour 3 — Protéger, automatiser et dépanner

| Séquence | Durée | Modalité |
|----------|------:|----------|
| Sauvegarde et continuité de service | 30 min | Cours |
| TD 9 — Sauvegarder et restaurer un fichier | 90 min | Pratique |
| Automatisation et tâches planifiées | 30 min | Cours |
| TD 10 — Automatiser un rapport de contrôle | 75 min | Pratique |
| Méthode de diagnostic et préparation de l’évaluation | 30 min | Cours |
| TD 11 — Mise en situation professionnelle | 120 min | Pratique évaluée |
| Bilan, correction et consolidation | 45 min | Correction collective |
| **Total** | **420 min** | **7 h** |

!!! tip "Organisation conseillée en binôme"
    Une personne manipule, l’autre lit la procédure, vérifie les résultats et prend les notes. Inversez les rôles à chaque TD.

    Chaque apprenant doit néanmoins être capable de reproduire individuellement les opérations essentielles.

---

## 4. Prérequis et préparation du laboratoire

### 4.1 Prérequis des apprenants

Il suffit de savoir :

- utiliser les fonctions courantes de Windows ;
- créer et retrouver un fichier ;
- reconnaître une adresse IPv4 ;
- ouvrir une console ;
- distinguer un ordinateur physique d’une machine virtuelle.

Aucune expérience préalable de Windows Server n’est requise.

### 4.2 Matériel et logiciels

Pour chaque poste de formation :

| Ressource | Minimum conseillé |
|-----------|-------------------|
| Processeur | 4 cœurs, virtualisation matérielle activée |
| Mémoire physique | 16 Go ; 24 Go ou plus pour davantage de confort |
| Stockage | SSD avec environ 200 Go disponibles |
| Hyperviseur | Hyper-V, VMware Workstation ou VirtualBox compatible avec les OS retenus |
| ISO serveur | Windows Server 2025, support officiel ou évaluation autorisée |
| ISO client | Windows 11 Pro, support et licence adaptés |
| Documentation | Ce support et un emplacement de dépôt des livrables |

!!! warning "Compatibilité Windows 11"
    Le formateur prépare un modèle de VM compatible avec les exigences de Windows 11, notamment le démarrage UEFI, le démarrage sécurisé et le TPM virtuel lorsque requis.

    Le contournement des exigences de l’OS ne fait pas partie de ce cours.

### 4.3 Machines virtuelles

| VM | Fonction | vCPU | RAM indicative | Disques virtuels |
|----|----------|-----:|---------------:|------------------|
| `SRV-FIC01` | Serveur autonome | 2 | 4 à 6 Go | OS : 80 Go ; données : 20 Go ; sauvegarde : 40 Go |
| `CLT-01` | Poste de test | 2 | 4 à 6 Go | OS : 64 Go ou plus |

Utiliser des disques virtuels à allocation dynamique si nécessaire, tout en surveillant l’espace réellement disponible sur l’hôte.

### 4.4 Réseau du laboratoire

Les deux VM sont connectées au **même commutateur virtuel isolé**.

Exemples :

- Hyper-V : commutateur **privé** ;
- VirtualBox : **réseau interne** ;
- VMware : segment LAN isolé.

```text
              Hôte de virtualisation
                       |
            Réseau virtuel LAB-TSSR
                 /             \
                /               \
       SRV-FIC01                 CLT-01
    192.168.50.10             192.168.50.20
```

| Paramètre | Serveur | Client |
|-----------|---------|--------|
| Nom | `SRV-FIC01` | `CLT-01` |
| IPv4 | `192.168.50.10` | `192.168.50.20` |
| Préfixe | `/24` | `/24` |
| Masque équivalent | `255.255.255.0` | `255.255.255.0` |
| Passerelle sur le réseau isolé | Aucune | Aucune |
| Groupe de travail | `WORKGROUP` | `WORKGROUP` |

!!! warning "Ne pas connecter le laboratoire au réseau de production"
    Aucun mode pont ou commutateur externe ne doit être utilisé sans validation du formateur.

    Les mises à jour et l’activation sont préparées avant la séance, ou réalisées à travers un accès temporaire contrôlé. Les VM reviennent ensuite sur le réseau isolé.

### 4.5 Préparation du formateur

Avant le cours :

- [ ] Tester le parcours sur la version exacte des ISO utilisées.
- [ ] Préparer une VM Windows 11 utilisable avec un compte local.
- [ ] Vérifier le fonctionnement du réseau isolé.
- [ ] Prévoir un serveur déjà installé pour les apprenants bloqués par l’installation.
- [ ] Vérifier les fonctionnalités Windows disponibles avec `Get-WindowsFeature`.
- [ ] Préparer un état de référence avant les exercices de panne.
- [ ] Vérifier l’espace libre sur tous les hôtes.
- [ ] Fournir des mots de passe temporaires de laboratoire selon la politique de l’établissement.
- [ ] Prévoir un emplacement de dépôt hors des VM.

!!! note "Instantané et sauvegarde"
    Un instantané d’hyperviseur peut faciliter le retour à un état pédagogique connu. Il ne remplace pas une sauvegarde indépendante.

    Les trois disques du serveur restent ici sur le même hôte physique : cette architecture n’offre pas une protection réelle contre la panne de cet hôte.

### 4.6 Dossier de preuves

Chaque apprenant crée un dossier nommé :

```text
Nom_Prenom_WindowsServer_3J
```

Il contient :

```text
01-inventaire.md
02-comptes-groupes.md
03-stockage.md
04-partages-permissions.md
05-fsrm.md
06-iis.md
07-diagnostic.md
08-sauvegarde-restauration.md
09-automatisation.md
10-recette-finale.md
```

Une preuve peut être :

- une capture d’écran pertinente ;
- une sortie de commande ;
- un extrait de journal ;
- un tableau de tests ;
- une explication courte de la décision prise.

**Ne jamais inclure de mot de passe dans les livrables.**

---

# Jour 1 — Préparer le serveur et publier un partage

## 5. Cours — Comprendre les fonctions serveur

### 5.1 Un serveur n’est pas seulement un ordinateur puissant

Un serveur est un système qui fournit un service à d’autres systèmes, appelés clients.

Exemples :

| Besoin | Service rendu |
|--------|---------------|
| Ouvrir un document stocké sur une autre machine | Service de fichiers |
| Afficher un intranet | Service web |
| Centraliser des files d’attente d’impression | Service d’impression |
| Administrer une machine sans être devant sa console | Administration distante |

La notion de serveur décrit donc principalement un **rôle dans un échange**.

Un même ordinateur peut être :

- serveur lorsqu’il fournit un fichier ;
- client lorsqu’il télécharge une mise à jour.

### 5.2 Windows Server et Windows client

Windows Server est conçu pour héberger et administrer des services partagés.

Il propose notamment :

- des rôles serveur ;
- des outils de gestion du stockage ;
- des outils d’administration ;
- des fonctions de contrôle des accès ;
- des mécanismes de journalisation et d’automatisation.

Un serveur doit être pensé en termes de :

- disponibilité ;
- sécurité ;
- capacité ;
- maintenabilité ;
- récupération après incident.

### 5.3 Rôle, fonctionnalité, service et protocole

| Terme | Explication | Exemple |
|-------|-------------|---------|
| Rôle | Grande fonction assurée par le serveur | Serveur web IIS |
| Fonctionnalité | Composant complémentaire | Sauvegarde Windows Server |
| Service Windows | Programme fonctionnant en arrière-plan | `W3SVC` |
| Protocole | Règles de communication entre machines | SMB, HTTP |
| Port réseau | Point d’entrée logique d’un service | TCP 445 pour SMB |

!!! example "Analogie"
    Un hôtel fournit plusieurs prestations : hébergement, restauration, blanchisserie.

    Les **rôles** correspondent aux grandes prestations. Les **services Windows** sont les équipes qui les font fonctionner. Les **protocoles** sont les règles suivies pour demander une prestation.

### 5.4 Quelques fonctions disponibles

| Fonction | Utilité | Traitement dans ce cours |
|----------|---------|-------------------------|
| Services de fichiers | Partage de documents | Installation et pratique |
| FSRM | Quotas et filtrage de fichiers | Installation et pratique |
| IIS | Hébergement web | Installation et pratique |
| Sauvegarde Windows Server | Protection et restauration | Installation et pratique |
| Administration distante | Intervention sur le serveur | Pratique RDP |
| Planificateur de tâches | Exécution automatique | Pratique |
| Services d’impression | Centralisation des imprimantes et files d’attente | Présentation |
| Hyper-V | Hébergement de VM | Mise en contexte uniquement |
| Espaces de stockage | Organisation et résilience du stockage | Présentation |

Les services d’impression nécessitent notamment de gérer les pilotes et la sécurité du spouleur. Ils ne seront pas installés sur notre serveur de fichiers et web.

L’administration RDP utilisée dans le laboratoire ne doit pas être confondue avec une infrastructure de bureaux multiutilisateurs, qui implique d’autres rôles et contraintes de licence.

### 5.5 Expérience de bureau et Server Core

- **Expérience de bureau** : interface graphique complète, adaptée à cette découverte.
- **Server Core** : interface locale réduite, administration principalement par commandes et outils distants.

Server Core réduit certains composants installés, mais demande davantage d’aisance avec les outils d’administration.

Le choix s’effectue à l’installation. Il ne faut pas prévoir une simple conversion ultérieure entre les deux modes.

### Questions de compréhension

1. Un serveur peut-il héberger plusieurs rôles ?
2. Un rôle installé est-il forcément accessible depuis le réseau ?
3. Quelle différence existe-t-il entre IIS et HTTP ?

??? note "Éléments de correction"
    1. Oui, sous réserve de capacité, de compatibilité et de sécurité.
    2. Non : configuration, service arrêté, pare-feu ou permissions peuvent empêcher son utilisation.
    3. IIS est un logiciel serveur ; HTTP est un protocole qu’il peut utiliser.

---

## 6. TD 1 — Installer et configurer le serveur

**Durée : 90 minutes**

### Objectifs

- Installer Windows Server.
- Identifier les principaux outils.
- Configurer le nom et l’adresse IP.
- Produire un inventaire de départ.

### Étape 1 — Créer la VM serveur

1. Créer `SRV-FIC01` dans l’hyperviseur.
2. Affecter les ressources prévues.
3. Connecter la carte réseau au réseau isolé.
4. Monter l’ISO.
5. Installer **Windows Server 2025 Standard avec Expérience de bureau**.
6. Effectuer une installation personnalisée sur le disque système.
7. Définir le mot de passe du compte administrateur local.

!!! warning "Éviter une erreur de disque"
    Pour simplifier l’installation, il est possible de ne connecter initialement que le disque système.

    Les deux disques supplémentaires seront ajoutés au TD 3, VM arrêtée si nécessaire.

### Étape 2 — Repérer les outils

Depuis le Gestionnaire de serveur, identifier :

- **Serveur local** ;
- **Gérer → Ajouter des rôles et fonctionnalités** ;
- **Outils → Gestion de l’ordinateur** ;
- **Outils → Observateur d’événements** ;
- **Outils → Services**.

Ouvrir ensuite Windows PowerShell en tant qu’administrateur.

```powershell
$PSVersionTable.PSVersion
hostname
whoami
Get-ComputerInfo |
    Select-Object WindowsProductName, WindowsVersion, OsBuildNumber
```

!!! note "Pourquoi vérifier la version de PowerShell ?"
    Ce support utilise Windows PowerShell 5.1, fourni avec Windows Server.

    Certains modules Windows utilisés ici, notamment celui d’IIS, ne se comportent pas de la même manière dans PowerShell 7.

### Étape 3 — Renommer le serveur

```powershell
Rename-Computer -NewName "SRV-FIC01" -Restart
```

Après redémarrage :

```powershell
hostname
```

Résultat attendu : `SRV-FIC01`.

### Étape 4 — Identifier la carte réseau

```powershell
Get-NetAdapter
Get-NetIPConfiguration
```

Noter :

- le nom de la carte ;
- son index ;
- son état ;
- son adresse MAC.

Ne pas supposer que la carte porte toujours le nom `Ethernet`.

### Étape 5 — Définir l’adresse IPv4

Méthode graphique recommandée pour la première manipulation :

1. Exécuter `ncpa.cpl`.
2. Ouvrir les propriétés de la carte du laboratoire.
3. Ouvrir les propriétés IPv4.
4. Renseigner `192.168.50.10`.
5. Renseigner le masque `255.255.255.0`.
6. Ne pas renseigner de passerelle sur cette carte isolée.
7. Valider.

Sur le client, effectuer la même opération avec `192.168.50.20`.

Vérifier :

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
    Select-Object InterfaceAlias, IPAddress, PrefixLength
```

### Étape 6 — Choisir le profil réseau du laboratoire

Afficher les profils :

```powershell
Get-NetConnectionProfile
```

Sur chaque VM, appliquer le profil **Privé** à l’interface du laboratoire, en remplaçant `5` par son index réel :

```powershell
Set-NetConnectionProfile -InterfaceIndex 5 -NetworkCategory Private
```

!!! warning "Le profil Privé n’est pas un bouton de sécurité universel"
    Il indique que ce réseau est considéré comme maîtrisé. Il influence l’application des règles de pare-feu.

    Cette opération n’est justifiée ici que parce que le réseau virtuel est isolé et contrôlé.

### Étape 7 — Vérifier le pare-feu

```powershell
Get-NetFirewallProfile |
    Select-Object Name, Enabled
```

Le pare-feu doit rester activé.

Un échec de `ping` ne prouve pas automatiquement une panne réseau : les requêtes ICMP peuvent être filtrées alors qu’un service TCP fonctionne.

Les prochains TD utiliseront des tests ciblés sur les ports utiles.

### Étape 8 — Réaliser l’inventaire

```powershell
Get-WindowsFeature | Where-Object Installed
Get-Service | Select-Object -First 15
Get-Volume
Get-NetAdapter
```

### Travail demandé

Compléter `01-inventaire.md` :

| Élément | Valeur observée |
|---------|----------------|
| Nom de la machine | |
| Version et édition | |
| Quantité de RAM | |
| Nombre de vCPU | |
| Adresse IPv4 | |
| Index de la carte réseau | |
| Profil réseau | |
| État du pare-feu | |

### Vérification

- [ ] Le serveur démarre.
- [ ] Le nom est correct.
- [ ] L’adresse IPv4 est correcte.
- [ ] Le client possède une adresse différente dans le même sous-réseau.
- [ ] Le pare-feu reste activé.
- [ ] L’inventaire est complété.

### Questions

1. Pourquoi ne pas donner la même adresse IP aux deux VM ?
2. Pourquoi relever l’état initial avant d’installer des rôles ?
3. Pourquoi conserver l’accès à la console de l’hyperviseur ?

??? note "Correction"
    1. Deux machines utilisant simultanément la même adresse créent un conflit.
    2. L’état initial permet de distinguer ce qui était déjà présent de ce qui a été ajouté.
    3. La console permet d’intervenir même lorsque l’administration réseau ne fonctionne plus.

---

## 7. Cours — Comptes, groupes et sécurité

### 7.1 Authentification et autorisation

**Authentification** : vérifier qui se présente.

**Autorisation** : déterminer ce que cette identité peut faire.

Un mot de passe correct ne donne pas automatiquement accès à tous les fichiers.

### 7.2 Compte local

Un compte local appartient à une machine précise.

```text
SRV-FIC01\alice
```

désigne le compte `alice` enregistré sur `SRV-FIC01`.

Un compte portant le même nom sur `CLT-01` reste un autre compte.

### 7.3 Groupe local

Un groupe rassemble des comptes pour faciliter l’attribution des droits.

Au lieu d’accorder une permission à dix utilisateurs, on peut :

1. créer un groupe ;
2. donner une permission à ce groupe ;
3. ajouter les utilisateurs concernés dans ce groupe.

Cette approche facilite les arrivées, départs et changements de fonction.

### 7.4 Moindre privilège

Chaque compte doit recevoir uniquement les permissions nécessaires à sa mission.

Un utilisateur qui consulte un document n’a pas besoin :

- d’installer un rôle ;
- d’arrêter un service ;
- de modifier le pare-feu ;
- d’être administrateur local.

### 7.5 Élévation et UAC

Un membre du groupe Administrateurs n’exécute pas nécessairement toutes ses applications avec un jeton élevé.

L’expression **« ouvrir en tant qu’administrateur »** signifie demander une élévation de privilèges.

Cela explique certains messages « Accès refusé » rencontrés dans une console ouverte normalement.

### 7.6 Accès distant : précautions

RDP permet de piloter une session graphique distante.

Pour ce laboratoire :

- l’accès est limité au client ;
- le pare-feu reste actif ;
- l’authentification au niveau du réseau reste activée ;
- aucun accès n’est publié sur Internet.

En production, l’administration distante doit s’inscrire dans une architecture dédiée et contrôlée.

---

## 8. TD 2 — Créer les identités locales et administrer à distance

**Durée : 60 minutes**

### Situation

Deux utilisateurs doivent accéder aux documents :

| Utilisateur | Besoin |
|-------------|--------|
| `alice` | Consulter les documents |
| `bruno` | Consulter, créer, modifier et supprimer des documents |

Groupes à créer :

| Groupe | Utilisation |
|--------|-------------|
| `GL_Compta_Lecture` | Accès en lecture |
| `GL_Compta_Modification` | Accès en modification |

### Étape 1 — Créer les utilisateurs

Sur le serveur, dans PowerShell administrateur :

```powershell
$mdpAlice = Read-Host "Mot de passe de laboratoire pour alice" -AsSecureString

New-LocalUser -Name "alice" `
    -Password $mdpAlice `
    -FullName "Alice Consultation" `
    -Description "Compte de test TSSR - lecture"

$mdpBruno = Read-Host "Mot de passe de laboratoire pour bruno" -AsSecureString

New-LocalUser -Name "bruno" `
    -Password $mdpBruno `
    -FullName "Bruno Contribution" `
    -Description "Compte de test TSSR - modification"
```

Les mots de passe doivent respecter la politique locale.

Ne pas utiliser un mot de passe personnel réel.

### Étape 2 — Créer les groupes

```powershell
New-LocalGroup -Name "GL_Compta_Lecture" `
    -Description "Lecture des documents comptables"

New-LocalGroup -Name "GL_Compta_Modification" `
    -Description "Modification des documents comptables"

Add-LocalGroupMember -Group "GL_Compta_Lecture" -Member "alice"
Add-LocalGroupMember -Group "GL_Compta_Modification" -Member "bruno"
```

Vérifier :

```powershell
Get-LocalUser | Select-Object Name, Enabled

Get-LocalGroupMember -Group "GL_Compta_Lecture"
Get-LocalGroupMember -Group "GL_Compta_Modification"
```

Retrouver les mêmes objets dans :

```text
Gestion de l’ordinateur
└── Utilisateurs et groupes locaux
    ├── Utilisateurs
    └── Groupes
```

!!! tip "Pourquoi utiliser à la fois la console et l’interface ?"
    L’interface aide à comprendre la structure des objets. Les commandes facilitent la répétition et la documentation des opérations.

### Étape 3 — Vérifier l’absence de privilèges administratifs

Le nom du groupe Administrateurs dépend de la langue de Windows. Son identifiant SID reste stable.

```powershell
$groupeAdmins = Get-LocalGroup -SID "S-1-5-32-544"

Get-LocalGroupMember -Group $groupeAdmins.Name
```

`alice` et `bruno` ne doivent pas appartenir à ce groupe.

### Étape 4 — Autoriser l’administration RDP

Dans ce TD, seul le compte administrateur du serveur est utilisé pour l’administration distante.

Sur le serveur :

```powershell
Set-ItemProperty `
    -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" `
    -Name "fDenyTSConnections" `
    -Value 0

Set-ItemProperty `
    -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" `
    -Name "UserAuthentication" `
    -Value 1

New-NetFirewallRule `
    -Name "TSSR-RDP-Client" `
    -DisplayName "TSSR - RDP depuis CLT-01" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 3389 `
    -RemoteAddress 192.168.50.20 `
    -Profile Private

Start-Service -Name TermService
```

!!! note "Portée de la règle"
    Cette règle autorise uniquement le client indiqué.

    Si d’autres règles RDP entrantes sont déjà actives, elles peuvent autoriser des accès supplémentaires. Le formateur fait vérifier leur portée dans `wf.msc`.

    Ajouter une règle restrictive ne rend pas automatiquement restrictives les autres règles existantes.

### Étape 5 — Tester depuis le client

```powershell
Test-NetConnection 192.168.50.10 -Port 3389
```

Résultat attendu :

```text
TcpTestSucceeded : True
```

Lancer :

```powershell
mstsc /v:192.168.50.10
```

Utiliser le compte administrateur local du serveur, par exemple :

```text
SRV-FIC01\Administrateur
```

Sur une installation anglophone, le nom peut être `Administrator`.

!!! warning "Avertissement de certificat RDP"
    Dans ce laboratoire isolé, un avertissement peut apparaître avec le certificat généré par le serveur. Vérifier que la machine contactée est bien la VM attendue.

    En production, ne pas prendre l’habitude d’ignorer systématiquement les avertissements d’identité.

### Étape 6 — Se déconnecter correctement

Dans la session distante, utiliser **Se déconnecter** lorsque le travail est terminé.

Fermer simplement la fenêtre RDP laisse généralement la session ouverte et déconnectée.

### Livrable

Dans `02-comptes-groupes.md` :

- liste des comptes et groupes ;
- tableau des appartenances ;
- preuve qu’Alice et Bruno ne sont pas administrateurs ;
- résultat du test TCP 3389 ;
- capture de la connexion distante.

### Questions

1. Quel compte est utilisé pour l’administration ?
2. Pourquoi ne pas ajouter Alice au groupe Administrateurs ?
3. Pourquoi limiter le port RDP à l’adresse du client ?

??? note "Correction"
    1. Le compte administrateur local de `SRV-FIC01`.
    2. Son besoin est de consulter des documents, pas d’administrer le système.
    3. Pour limiter les machines autorisées à établir la connexion réseau.

---

## 9. Cours — Disques, volumes et systèmes de fichiers

### 9.1 Du disque au fichier

```text
Disque virtuel
    └── Table de partitions
        └── Partition
            └── Volume formaté
                └── Dossiers et fichiers
```

| Élément | Explication |
|---------|-------------|
| Disque | Support de stockage vu par le système |
| Partition | Zone délimitée sur un disque |
| Volume | Espace utilisable par Windows |
| Système de fichiers | Organisation des données et métadonnées |
| Lettre de lecteur | Point d’accès comme `D:` |

### 9.2 GPT et NTFS

**GPT** est le format de table de partitions retenu pour les disques de données du laboratoire.

**NTFS** apporte notamment :

- des permissions sur fichiers et dossiers ;
- la journalisation du système de fichiers ;
- la prise en charge de nombreux outils Windows.

ReFS répond à d’autres besoins, mais n’est pas interchangeable avec NTFS pour toutes les fonctions. Les exercices FSRM de ce cours sont réalisés sur NTFS.

### 9.3 Séparer système, données et sauvegardes

| Volume | Contenu |
|--------|---------|
| `C:` | Système et applications |
| `D:` | Documents, site web et scripts |
| `E:` | Sauvegarde pédagogique |

Avantages :

- organisation plus lisible ;
- surveillance facilitée ;
- limitation de certains effets d’un volume de données plein.

Cette séparation logique ne garantit pas une séparation des risques matériels si tous les disques virtuels sont stockés sur le même hôte.

### 9.4 Résilience et sauvegarde : deux besoins différents

Un mécanisme de miroir ou de parité peut maintenir l’accès malgré la panne d’un disque.

Il ne protège pas nécessairement contre :

- une suppression accidentelle ;
- une modification incorrecte ;
- un chiffrement malveillant ;
- la destruction de l’hôte ;
- une erreur d’administration propagée à toutes les copies.

**La résilience du stockage n’est pas une sauvegarde.**

---

## 10. TD 3 — Préparer les volumes de données et de sauvegarde

**Durée : 75 minutes**

### Objectifs

Obtenir :

- `D:` — `DATA`, disque de 20 Go ;
- `E:` — `BACKUP`, disque de 40 Go.

### Étape 1 — Ajouter les disques

Si les disques ne sont pas encore présents :

1. arrêter proprement la VM ;
2. ajouter un disque virtuel de 20 Go ;
3. ajouter un disque virtuel de 40 Go ;
4. redémarrer la VM.

### Étape 2 — Identifier les disques

```powershell
Get-Disk |
    Select-Object Number, FriendlyName, SerialNumber,
        PartitionStyle, OperationalStatus,
        @{Name="TailleGo";Expression={[math]::Round($_.Size / 1GB, 1)}}
```

Comparer les résultats avec la configuration de l’hyperviseur.

!!! danger "Initialisation et formatage"
    Les opérations suivantes peuvent détruire des données si elles sont appliquées au mauvais disque.

    Ne jamais recopier un numéro de disque sans vérification. Ne jamais utiliser une commande qui initialise automatiquement tous les disques inconnus.

### Étape 3 — Vérifier les lettres disponibles

```powershell
Get-Volume
```

Si le lecteur DVD utilise `D:` ou `E:`, lui attribuer par exemple `Z:` depuis la Gestion des disques.

L’objectif est de conserver les mêmes chemins pendant toute la formation.

### Étape 4 — Préparer le disque DATA avec l’interface

1. Ouvrir `diskmgmt.msc`.
2. Identifier le disque de 20 Go.
3. Le mettre en ligne si nécessaire.
4. L’initialiser en GPT.
5. Créer un volume simple utilisant l’espace disponible.
6. Affecter la lettre `D:`.
7. Choisir NTFS.
8. Donner le nom `DATA`.
9. Effectuer un formatage rapide.

### Étape 5 — Préparer le disque BACKUP avec PowerShell

Exemple : le disque de sauvegarde vérifié porte le numéro `2`.

**Adapter ce numéro à la machine.**

```powershell
$numeroDisqueSauvegarde = 2

Get-Disk -Number $numeroDisqueSauvegarde
```

Après validation visuelle :

```powershell
# Seulement si le disque est hors ligne :
# Set-Disk -Number $numeroDisqueSauvegarde -IsOffline $false

Initialize-Disk -Number $numeroDisqueSauvegarde -PartitionStyle GPT

New-Partition `
    -DiskNumber $numeroDisqueSauvegarde `
    -UseMaximumSize `
    -DriveLetter E |
    Format-Volume `
        -FileSystem NTFS `
        -NewFileSystemLabel "BACKUP" `
        -Confirm
```

Cette commande suppose un disque neuf non initialisé.

### Étape 6 — Créer les dossiers

```powershell
New-Item -Path "D:\Partages\Compta" -ItemType Directory -Force
New-Item -Path "D:\Web" -ItemType Directory -Force
New-Item -Path "D:\Scripts" -ItemType Directory -Force
New-Item -Path "D:\Rapports" -ItemType Directory -Force
New-Item -Path "D:\Restauration" -ItemType Directory -Force
```

### Étape 7 — Contrôler

```powershell
Get-Volume |
    Select-Object DriveLetter, FileSystemLabel, FileSystem,
        HealthStatus,
        @{Name="TailleGo";Expression={[math]::Round($_.Size / 1GB, 2)}},
        @{Name="LibreGo";Expression={[math]::Round($_.SizeRemaining / 1GB, 2)}}
```

!!! success "Résultat attendu"
    Les volumes `D:` et `E:` sont accessibles, formatés en NTFS et identifiés par les étiquettes `DATA` et `BACKUP`.

### Travail demandé

Dans `03-stockage.md` :

1. dessiner le lien entre disque virtuel, volume et contenu ;
2. relever les numéros des trois disques ;
3. indiquer les tailles et systèmes de fichiers ;
4. expliquer pourquoi `E:` ne constitue pas ici une sauvegarde indépendante de l’hôte.

### Exercice d’observation

Créer un fichier sur `D:`, puis actualiser l’affichage de l’espace libre.

La variation est-elle visible immédiatement ? Est-elle significative pour un fichier texte de quelques octets ?

??? note "Correction"
    Un très petit fichier provoque une variation peu visible dans un affichage arrondi en gigaoctets. Il faut distinguer la précision de l’outil et la quantité réelle de données écrites.

---

## 11. TD 4 — Publier un partage SMB sécurisé

**Durée : 90 minutes**

### Situation

Le dossier :

```text
D:\Partages\Compta
```

doit être accessible depuis :

```text
\\192.168.50.10\Compta
```

Droits attendus :

| Identité | Lecture | Création/modification | Suppression |
|----------|:-------:|:---------------------:|:-----------:|
| Alice | Oui | Non | Non |
| Bruno | Oui | Oui | Oui |
| Administrateurs | Oui | Oui | Oui |

### Avant de manipuler : deux portes à franchir

Lors d’un accès SMB :

1. les permissions du **partage** contrôlent l’accès par le réseau ;
2. les permissions **NTFS** contrôlent l’accès au dossier et à son contenu.

Pour réussir une opération, l’utilisateur doit être autorisé par les deux niveaux.

### Étape 1 — Installer le rôle de serveur de fichiers

Sur le serveur :

```powershell
Install-WindowsFeature FS-FileServer -IncludeManagementTools
```

Si le rôle était déjà installé, la commande le signale : ce n’est pas une erreur.

Vérifier :

```powershell
Get-WindowsFeature FS-FileServer
Get-Service LanmanServer
```

### Étape 2 — Configurer les permissions NTFS

Dans l’Explorateur :

1. ouvrir les propriétés de `D:\Partages\Compta` ;
2. consulter l’onglet **Sécurité** ;
3. ouvrir **Avancé** ;
4. identifier les permissions héritées et explicites.

Ne rien supprimer sans savoir comment conserver l’accès administrateur.

Appliquer ensuite la configuration de référence :

```powershell
$dossier = "D:\Partages\Compta"
$gLecture = "$env:COMPUTERNAME\GL_Compta_Lecture"
$gModification = "$env:COMPUTERNAME\GL_Compta_Modification"

icacls $dossier /grant:r `
    '*S-1-5-18:(OI)(CI)(F)' `
    '*S-1-5-32-544:(OI)(CI)(F)' `
    "${gLecture}:(OI)(CI)(RX)" `
    "${gModification}:(OI)(CI)(M)"

icacls $dossier /inheritance:r
```

Explication :

| Élément | Sens |
|---------|------|
| `S-1-5-18` | Compte système Windows |
| `S-1-5-32-544` | Groupe Administrateurs intégré |
| `OI` | Transmission aux fichiers enfants |
| `CI` | Transmission aux sous-dossiers enfants |
| `F` | Contrôle total |
| `RX` | Lecture et exécution |
| `M` | Modification |
| `/inheritance:r` | Désactive l’héritage et retire les entrées héritées |

Les droits explicites nécessaires ont été ajoutés **avant** de retirer les droits hérités.

!!! warning "Commande de laboratoire, pas nettoyage universel"
    Cette procédure s’applique au dossier neuf créé dans ce cours.

    Elle ne supprime pas d’éventuelles autres entrées explicites déjà présentes sur un dossier réutilisé. Il faut toujours examiner l’ACL obtenue avec `icacls` et l’interface graphique.

Vérifier :

```powershell
icacls "D:\Partages\Compta"
```

### Étape 3 — Créer un document de référence

```powershell
@"
Documents comptables - laboratoire TSSR
Alice doit pouvoir lire ce fichier.
Bruno doit pouvoir le modifier.
"@ | Set-Content -Path "D:\Partages\Compta\consignes.txt" -Encoding UTF8
```

### Étape 4 — Créer le partage SMB

Résoudre le nom localisé du groupe Administrateurs :

```powershell
$admins = (
    [System.Security.Principal.SecurityIdentifier]::new("S-1-5-32-544")
).Translate([System.Security.Principal.NTAccount]).Value
```

Créer le partage :

```powershell
New-SmbShare `
    -Name "Compta" `
    -Path "D:\Partages\Compta" `
    -FullAccess $admins `
    -ChangeAccess "$env:COMPUTERNAME\GL_Compta_Modification" `
    -ReadAccess "$env:COMPUTERNAME\GL_Compta_Lecture" `
    -FolderEnumerationMode AccessBased
```

L’énumération basée sur l’accès peut masquer des éléments que l’utilisateur ne peut pas consulter. Elle ne remplace pas les permissions.

Vérifier :

```powershell
Get-SmbShare -Name Compta
Get-SmbShareAccess -Name Compta
```

### Étape 5 — Autoriser SMB dans le pare-feu

```powershell
New-NetFirewallRule `
    -Name "TSSR-SMB-Client" `
    -DisplayName "TSSR - SMB depuis CLT-01" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 445 `
    -RemoteAddress 192.168.50.20 `
    -Profile Private
```

Dans `wf.msc`, vérifier les autres règles SMB entrantes éventuellement activées par l’installation du rôle. Adapter leur portée si nécessaire pour ne pas conserver une autorisation plus large que prévue.

!!! warning "Ne pas activer SMBv1"
    Les versions modernes de Windows utilisent SMB 2/3. SMBv1 n’est pas nécessaire au laboratoire et ne doit pas être activé pour résoudre un problème d’accès.

    Ne pas activer non plus l’accès invité non sécurisé ou désactiver la signature SMB pour contourner une erreur.

### Étape 6 — Vérifier le port depuis le client

```powershell
Test-NetConnection 192.168.50.10 -Port 445
```

Le résultat attendu est `TcpTestSucceeded : True`.

Ce test prouve que le port est accessible. Il ne valide pas encore le mot de passe ou les permissions.

### Étape 7 — Se connecter avec Alice

Sur le client, dans une console normale :

```powershell
net use Z: \\192.168.50.10\Compta /user:SRV-FIC01\alice * /persistent:no
```

Le caractère `*` demande une saisie du mot de passe sans l’inscrire directement dans la commande.

Tester :

```powershell
Get-Content "Z:\consignes.txt"
Set-Content "Z:\test-alice.txt" -Value "Test Alice"
```

Résultats :

- lecture : réussite ;
- création : accès refusé.

### Étape 8 — Passer à Bruno

Fermer les fenêtres et applications utilisant le partage, puis :

```powershell
net use Z: /delete
net use
```

Vérifier qu’il ne reste pas de connexion vers le même serveur.

Se connecter :

```powershell
net use Z: \\192.168.50.10\Compta /user:SRV-FIC01\bruno * /persistent:no

Set-Content "Z:\test-bruno.txt" -Value "Créé par Bruno"
Add-Content "Z:\test-bruno.txt" -Value "Ligne ajoutée"
Get-Content "Z:\test-bruno.txt"
Remove-Item "Z:\test-bruno.txt"
```

!!! failure "Connexions avec plusieurs identifiants"
    Windows peut refuser une nouvelle connexion au même serveur avec un autre nom d’utilisateur lorsqu’une session SMB existe déjà.

    Fermer les applications utilisant le partage, examiner `net use`, puis supprimer les connexions concernées.

    Dans cette VM de laboratoire uniquement, `net use * /delete` peut aider, mais supprime **toutes** les connexions réseau de la session. Ne pas l’utiliser aveuglément sur un poste de production.

### Livrable

Compléter `04-partages-permissions.md` avec :

- le chemin local ;
- le chemin UNC ;
- les permissions NTFS ;
- les permissions de partage ;
- les tests Alice et Bruno ;
- l’explication d’un refus d’accès attendu.

### Bilan du jour 1

L’apprenant doit maintenant pouvoir expliquer :

> « J’ai préparé un serveur autonome, créé des identités locales, séparé les volumes et publié un dossier réseau avec des droits différents selon les utilisateurs. »

---

# Jour 2 — Maîtriser les accès et déployer des services

## 12. Cours — Comprendre les permissions effectives

### 12.1 Les permissions de partage

Les niveaux courants sont :

| Permission | Effet principal |
|------------|-----------------|
| Lecture | Consulter |
| Modification | Lire, créer, modifier, supprimer |
| Contrôle total | Inclut des possibilités supplémentaires de gestion des permissions via le partage, sous réserve des droits NTFS |

### 12.2 Les permissions NTFS

Les permissions usuelles comprennent :

- lecture ;
- lecture et exécution ;
- écriture ;
- modification ;
- contrôle total.

**Modification** autorise notamment la suppression, mais n’accorde pas les mêmes droits de gestion de sécurité que **Contrôle total**.

### 12.3 L’intersection entre partage et NTFS

Pour les opérations ordinaires sur les fichiers, on peut retenir :

```text
Accès réseau possible
    = opérations autorisées par le partage
      ET autorisées par NTFS
```

| Partage | NTFS | Résultat simplifié par le réseau |
|---------|------|----------------------------------|
| Lecture | Modification | Lecture |
| Modification | Lecture | Lecture |
| Modification | Modification | Modification |
| Contrôle total | Lecture | Lecture |

### 12.4 Le cumul des groupes

À un même niveau, les autorisations des groupes peuvent se cumuler.

Si Bruno appartient à :

- un groupe autorisant la lecture ;
- un autre autorisant la modification ;

ses autorisations ne sont pas limitées à la lecture simplement parce qu’un groupe ne donne que la lecture.

### 12.5 Les refus explicites

Les entrées **Refuser** peuvent neutraliser des autorisations, selon la nature des droits et l’ordre d’évaluation des entrées explicites et héritées.

Pour débuter :

- préférer une liste d’autorisations claire ;
- éviter d’utiliser « Refuser » comme mécanisme habituel ;
- vérifier l’accès réel et les permissions effectives.

!!! warning "Attention aux raccourcis"
    La formule « le droit le plus restrictif gagne » est utile pour comparer partage et NTFS.

    Elle ne décrit pas correctement, à elle seule, le cumul de toutes les appartenances à des groupes ni l’ensemble des règles d’évaluation d’une ACL.

### 12.6 Héritage

Un sous-dossier peut recevoir des permissions de son parent.

L’héritage :

- réduit les manipulations ;
- facilite la cohérence ;
- peut aussi transmettre un droit trop large.

Une permission héritée n’est pas indépendante de son parent.

### 12.7 Accès local et accès réseau

Une application ouvrant directement :

```text
D:\Partages\Compta\consignes.txt
```

n’utilise pas le partage SMB.

Une application ouvrant :

```text
\\192.168.50.10\Compta\consignes.txt
```

passe par SMB.

Les permissions de partage concernent le second cas ; les permissions NTFS concernent les deux.

---

## 13. TD 5 — Tester et corriger les permissions

**Durée : 75 minutes**

### Objectif

Démontrer les règles de permissions plutôt que les apprendre uniquement par cœur.

### Étape 1 — Compléter la matrice de tests

Sur le client, tester successivement Alice et Bruno avec des connexions SMB distinctes.

| Test | Alice attendu | Alice observé | Bruno attendu | Bruno observé |
|------|---------------|---------------|---------------|---------------|
| Lister le dossier | Autorisé | | Autorisé | |
| Lire `consignes.txt` | Autorisé | | Autorisé | |
| Créer un fichier | Refusé | | Autorisé | |
| Modifier un fichier | Refusé | | Autorisé | |
| Supprimer un fichier de test | Refusé | | Autorisé | |

Ne pas utiliser un document important pour tester la suppression.

### Étape 2 — Créer un sous-dossier

Avec Bruno :

```powershell
New-Item -Path "Z:\Archives" -ItemType Directory
Set-Content "Z:\Archives\exemple.txt" -Value "Document archivé"
```

Sur le serveur :

```powershell
icacls "D:\Partages\Compta\Archives"
```

Identifier les permissions héritées.

### Étape 3 — Réduire volontairement les permissions du partage

Sur le serveur :

```powershell
$gModification = "$env:COMPUTERNAME\GL_Compta_Modification"

Revoke-SmbShareAccess `
    -Name "Compta" `
    -AccountName $gModification `
    -Force

Grant-SmbShareAccess `
    -Name "Compta" `
    -AccountName $gModification `
    -AccessRight Read `
    -Force
```

Fermer les fichiers ouverts, déconnecter puis reconnecter Bruno.

Tester la création :

```powershell
Set-Content "Z:\test-limitation-partage.txt" -Value "Essai"
```

Elle doit échouer, bien que NTFS accorde toujours Modification.

### Étape 4 — Expliquer le résultat

Compléter :

```text
Identité testée :
Permission de partage :
Permission NTFS :
Opération demandée :
Résultat :
Explication :
```

### Étape 5 — Restaurer la configuration

Sur le serveur :

```powershell
Revoke-SmbShareAccess `
    -Name "Compta" `
    -AccountName $gModification `
    -Force

Grant-SmbShareAccess `
    -Name "Compta" `
    -AccountName $gModification `
    -AccessRight Change `
    -Force
```

Déconnecter puis reconnecter Bruno, et refaire le test.

### Étape 6 — Observer le cumul des groupes

Sur le serveur :

```powershell
Add-LocalGroupMember -Group "GL_Compta_Lecture" -Member "bruno"
```

Reconnecter Bruno et vérifier qu’il conserve la modification.

Retirer ensuite cette appartenance inutile :

```powershell
Remove-LocalGroupMember -Group "GL_Compta_Lecture" -Member "bruno"
```

### Étape 7 — Observer les sessions côté serveur

Pendant qu’un client utilise le partage :

```powershell
Get-SmbSession
Get-SmbOpenFile
```

`Get-SmbOpenFile` peut être vide si aucun fichier n’est maintenu ouvert.

!!! warning "Fermer une session n’est pas anodin"
    Une fermeture forcée peut interrompre une écriture. En production, prévenir l’utilisateur et vérifier les fichiers ouverts avant d’agir.

### Livrable

Ajouter au document des permissions :

- la matrice complète ;
- une capture des droits hérités ;
- l’explication du test « partage Lecture + NTFS Modification » ;
- la preuve du retour à la configuration initiale.

### Vérification finale

```powershell
Get-SmbShareAccess -Name Compta
Get-LocalGroupMember -Group GL_Compta_Modification
icacls "D:\Partages\Compta"
```

---

## 14. Cours — Gérer les ressources avec FSRM

### 14.1 Pourquoi gérer l’espace ?

Un serveur de fichiers ne doit pas seulement accepter des documents.

Il faut également :

- surveiller la capacité restante ;
- éviter la saturation ;
- informer les responsables ;
- appliquer des règles d’usage.

### 14.2 Présentation de FSRM

FSRM signifie **File Server Resource Manager**, ou Gestionnaire de ressources du serveur de fichiers.

Il permet notamment :

- d’appliquer des quotas à des dossiers ;
- de filtrer certains types de fichiers ;
- de produire des rapports de stockage ;
- d’associer des actions à des seuils.

### 14.3 Quota strict et quota souple

| Type | Comportement |
|------|--------------|
| Strict | Empêche les écritures dépassant la limite |
| Souple | Observe le dépassement sans le bloquer |

Un quota FSRM s’applique à un chemin et à son contenu. Il ne faut pas le confondre avec les quotas NTFS par propriétaire sur un volume.

### 14.4 Filtrage actif et passif

| Type | Comportement |
|------|--------------|
| Actif | Bloque les fichiers correspondant aux règles |
| Passif | Observe et peut déclencher des notifications |

!!! warning "FSRM n’est pas un antivirus"
    Le filtrage par motifs de noms, notamment les extensions, ne réalise pas une analyse de sécurité du contenu.

    Renommer un fichier peut suffire à contourner une règle basée uniquement sur son extension.

### 14.5 Un quota est aussi une décision de gestion

Avant de fixer une limite, il faut connaître :

- le besoin métier ;
- la taille habituelle des documents ;
- la croissance prévue ;
- la procédure de demande d’extension ;
- le responsable à prévenir.

Un quota arbitrairement trop faible crée des incidents au lieu de les prévenir.

---

## 15. TD 6 — Configurer quotas et filtrage FSRM

**Durée : 75 minutes**

### Objectifs

Sur `D:\Partages\Compta` :

- quota strict de 100 Mio ;
- seuil d’avertissement à 85 % ;
- blocage des extensions `.mp3`, `.mp4` et `.exe`.

Dans les commandes PowerShell, `1MB` représente ici 1 048 576 octets, soit un Mio.

### Étape 1 — Installer FSRM

```powershell
Install-WindowsFeature FS-Resource-Manager -IncludeManagementTools
Import-Module FileServerResourceManager
```

Ouvrir le Gestionnaire de ressources du serveur de fichiers depuis les outils du Gestionnaire de serveur.

### Étape 2 — Créer le quota

```powershell
New-FsrmQuota `
    -Path "D:\Partages\Compta" `
    -Size 100MB `
    -Description "Quota pédagogique strict - Compta"
```

En l’absence de l’option `SoftLimit`, le quota est strict.

Vérifier :

```powershell
Get-FsrmQuota -Path "D:\Partages\Compta" |
    Select-Object Path, Size, Usage, SoftLimit
```

### Étape 3 — Ajouter un seuil d’avertissement

Dans l’interface FSRM :

1. ouvrir **Gestion de quotas → Quotas** ;
2. modifier le quota du dossier ;
3. ajouter ou vérifier un seuil de 85 % ;
4. activer l’écriture d’un avertissement dans le journal d’événements ;
5. personnaliser le message ;
6. valider.

Aucune messagerie n’est nécessaire pour cet exercice.

### Étape 4 — Créer un groupe de fichiers

```powershell
New-FsrmFileGroup `
    -Name "TSSR-Extensions-interdites" `
    -IncludePattern @("*.mp3", "*.mp4", "*.exe")
```

### Étape 5 — Créer le filtre actif

```powershell
New-FsrmFileScreen `
    -Path "D:\Partages\Compta" `
    -IncludeGroup "TSSR-Extensions-interdites" `
    -Active `
    -Description "Filtrage pédagogique des extensions"
```

Vérifier :

```powershell
Get-FsrmFileScreen -Path "D:\Partages\Compta"
```

### Étape 6 — Tester le filtrage depuis le client

Connecter `Z:` avec Bruno.

```powershell
Set-Content "Z:\autorise.txt" -Value "Fichier autorisé"
Set-Content "Z:\bloque.mp3" -Value "Texte de test, pas un véritable fichier audio"
```

Résultats attendus :

- `.txt` : création autorisée ;
- `.mp3` : création refusée.

Ne pas utiliser de véritable programme ou de fichier malveillant pour ce test.

### Étape 7 — Tester le quota

Sur le client, définir cette fonction :

```powershell
function New-FichierTest {
    param(
        [Parameter(Mandatory)]
        [string]$Chemin,

        [Parameter(Mandatory)]
        [ValidateRange(1, 200)]
        [int]$TailleMo
    )

    $tampon = New-Object byte[] (1MB)
    $flux = [System.IO.File]::Open(
        $Chemin,
        [System.IO.FileMode]::Create,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )

    try {
        for ($i = 0; $i -lt $TailleMo; $i++) {
            $flux.Write($tampon, 0, $tampon.Length)
        }

        $flux.Flush()
    }
    finally {
        $flux.Dispose()
    }
}
```

Créer :

```powershell
New-FichierTest -Chemin "Z:\test-60.bin" -TailleMo 60
New-FichierTest -Chemin "Z:\test-30.bin" -TailleMo 30
```

L’utilisation dépasse alors 85 %, mais reste sous 100 Mio si les autres fichiers sont petits.

Tenter ensuite :

```powershell
New-FichierTest -Chemin "Z:\test-20.bin" -TailleMo 20
```

L’écriture doit échouer avant que la totalité du troisième fichier soit créée.

!!! note "Un fichier partiel peut rester présent"
    L’échec d’une écriture n’entraîne pas toujours la suppression automatique du fichier commencé.

    Relever sa taille, puis le supprimer lors du nettoyage.

### Étape 8 — Observer côté serveur

```powershell
Get-FsrmQuota -Path "D:\Partages\Compta" |
    Select-Object Path, Size, Usage, SoftLimit
```

Consulter l’Observateur d’événements, notamment le journal **Application**, autour de l’heure du test.

Si l’événement attendu n’apparaît pas :

- vérifier la configuration de l’action de seuil ;
- actualiser l’affichage ;
- vérifier que le seuil a réellement été franchi ;
- tenir compte d’un éventuel délai ou intervalle de notification.

### Étape 9 — Nettoyer

Depuis le client :

```powershell
Remove-Item "Z:\test-60.bin", "Z:\test-30.bin", "Z:\test-20.bin" `
    -ErrorAction SilentlyContinue
```

Conserver le quota et le filtre pour la suite.

### Livrable

Dans `05-fsrm.md` :

- chemin et limite du quota ;
- preuve de quota strict ;
- extensions bloquées ;
- résultats des tests ;
- preuve de notification, ou diagnostic documenté de son absence ;
- explication de la différence entre filtrage d’extension et antivirus.

---

## 16. Cours — Héberger un site web avec IIS

### 16.1 Le dialogue web

```text
Navigateur
    → requête HTTP
        → serveur IIS
            → fichier ou application
        ← réponse HTTP
    ← affichage de la page
```

Le navigateur ne lit pas directement le disque `D:` du serveur.

Il demande une ressource à IIS, qui construit une réponse.

### 16.2 Les composants utiles

| Élément | Fonction |
|---------|----------|
| Site web | Ensemble de contenus et de paramètres |
| Dossier physique | Emplacement des fichiers |
| Liaison ou binding | Adresse IP, port et éventuellement nom d’hôte |
| Pool d’applications | Cadre d’exécution et identité du traitement web |
| Document par défaut | Page utilisée pour une URL de dossier |
| Journal HTTP | Trace des requêtes traitées |

### 16.3 HTTP et HTTPS

- HTTP ne chiffre pas les échanges.
- HTTPS utilise TLS pour protéger le transport et permettre la vérification de l’identité du serveur.

Le TD utilise HTTP uniquement sur le réseau isolé, avec une page statique ne contenant aucune donnée sensible.

Une publication réelle contenant des identifiants ou des informations confidentielles nécessite une configuration HTTPS adaptée.

### 16.4 Quelques codes HTTP

| Code | Signification générale |
|------|------------------------|
| 200 | Requête traitée avec succès |
| 403 | Accès interdit |
| 404 | Ressource introuvable |
| 500 | Erreur interne |
| 503 | Service indisponible |

Le code et, dans IIS, le sous-code permettent d’orienter le diagnostic.

### 16.5 Ne pas confondre port ouvert et application fonctionnelle

Un port TCP 80 accessible ne prouve pas :

- que la bonne page est servie ;
- que le dossier existe ;
- que les permissions sont correctes ;
- que toutes les ressources sont accessibles.

Il faut tester plusieurs niveaux.

---

## 17. TD 7 — Publier un intranet statique

**Durée : 90 minutes**

### Objectif

Publier :

```text
http://192.168.50.10/
```

avec une page stockée dans :

```text
D:\Web\Intranet
```

### Étape 1 — Installer IIS

Sur le serveur :

```powershell
Install-WindowsFeature `
    Web-Server, Web-Static-Content, Web-Default-Doc, Web-Http-Logging, Web-Mgmt-Console `
    -IncludeManagementTools

Import-Module WebAdministration
```

### Étape 2 — Créer le contenu

```powershell
New-Item -Path "D:\Web\Intranet" -ItemType Directory -Force

@'
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Intranet TSSR</title>
</head>
<body>
    <h1>Bienvenue sur l’intranet TSSR</h1>
    <p>Cette page est publiée par Windows Server et IIS.</p>
    <ul>
        <li>Serveur : SRV-FIC01</li>
        <li>Environnement : laboratoire isolé</li>
        <li>Service : HTTP</li>
    </ul>
</body>
</html>
'@ | Set-Content -Path "D:\Web\Intranet\index.html" -Encoding UTF8
```

### Étape 3 — Préparer le pool et le site

Pour éviter la confusion avec le site fourni par défaut :

```powershell
if (Test-Path "IIS:\Sites\Default Web Site") {
    Stop-Website -Name "Default Web Site"
}
```

Créer un pool dédié :

```powershell
New-WebAppPool -Name "TSSR-Pool"
```

Créer le site :

```powershell
New-Website `
    -Name "Intranet-TSSR" `
    -IPAddress "192.168.50.10" `
    -Port 80 `
    -PhysicalPath "D:\Web\Intranet" `
    -ApplicationPool "TSSR-Pool"
```

### Étape 4 — Utiliser l’identité du pool pour l’accès anonyme

Par défaut, l’accès anonyme peut utiliser le compte intégré `IUSR`.

Nous choisissons ici l’identité du pool afin d’attribuer les droits à une identité dédiée :

```powershell
Set-WebConfigurationProperty `
    -PSPath "IIS:\" `
    -Location "Intranet-TSSR" `
    -Filter "system.webServer/security/authentication/anonymousAuthentication" `
    -Name "userName" `
    -Value ""
```

Dans le Gestionnaire IIS, vérifier :

```text
Intranet-TSSR
└── Authentification
    └── Authentification anonyme
        └── Modifier
            └── Identité du pool d’applications
```

### Étape 5 — Définir les permissions du dossier web

```powershell
icacls "D:\Web\Intranet" /grant:r `
    '*S-1-5-18:(OI)(CI)(F)' `
    '*S-1-5-32-544:(OI)(CI)(F)' `
    'IIS AppPool\TSSR-Pool:(OI)(CI)(RX)'

icacls "D:\Web\Intranet" /inheritance:r
```

Vérifier :

```powershell
icacls "D:\Web\Intranet"
```

Le pool peut lire la page. Il ne doit pas pouvoir la modifier.

!!! tip "Une application web n’a pas toujours besoin d’écrire"
    Pour un site statique, la lecture est suffisante. Accorder Modification « pour que cela marche » élargirait inutilement les possibilités d’un processus compromis.

### Étape 6 — Vérifier le document par défaut

Dans le Gestionnaire IIS :

1. sélectionner `Intranet-TSSR` ;
2. ouvrir **Document par défaut** ;
3. vérifier que `index.html` figure dans la liste ;
4. l’ajouter si nécessaire.

### Étape 7 — Autoriser HTTP

```powershell
New-NetFirewallRule `
    -Name "TSSR-HTTP-Client" `
    -DisplayName "TSSR - HTTP depuis CLT-01" `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 80 `
    -RemoteAddress 192.168.50.20 `
    -Profile Private
```

Comme pour SMB, vérifier qu’une règle installée avec IIS n’autorise pas une portée plus large que celle retenue pour le laboratoire.

### Étape 8 — Démarrer et contrôler

```powershell
Start-WebAppPool -Name "TSSR-Pool"
Start-Website -Name "Intranet-TSSR"

Get-Website
Get-WebBinding -Name "Intranet-TSSR"
Get-WebAppPoolState -Name "TSSR-Pool"
Get-Service W3SVC, WAS
```

Tester sur le serveur :

```powershell
Invoke-WebRequest -Uri "http://192.168.50.10/" -UseBasicParsing |
    Select-Object StatusCode, StatusDescription
```

### Étape 9 — Tester depuis le client

```powershell
Test-NetConnection 192.168.50.10 -Port 80

Invoke-WebRequest -Uri "http://192.168.50.10/" -UseBasicParsing |
    Select-Object StatusCode, StatusDescription
```

Ouvrir l’adresse dans le navigateur.

Résultat attendu : la page intranet apparaît et le code HTTP est `200`.

### Étape 10 — Produire une erreur contrôlée

Depuis le client, demander :

```text
http://192.168.50.10/page-absente.html
```

Résultat attendu : code HTTP `404`.

La présence d’un code HTTP indique qu’un serveur web a répondu. Ce n’est donc pas le même symptôme qu’une absence totale de connexion.

### Étape 11 — Consulter les journaux IIS

Emplacement habituel :

```text
C:\inetpub\logs\LogFiles\W3SVC<identifiant-du-site>
```

Trouver l’identifiant :

```powershell
Get-Website -Name "Intranet-TSSR" |
    Select-Object Name, ID, State, PhysicalPath
```

Dans le journal correspondant, repérer :

- l’adresse du client ;
- l’URL demandée ;
- le code `200` ;
- le code `404`.

Les journaux W3C utilisent habituellement UTC pour l’horodatage. Les écritures peuvent être différées.

### Livrable

Dans `06-iis.md` :

- nom du site ;
- liaison ;
- dossier physique ;
- pool et identité utilisés ;
- permissions NTFS ;
- capture depuis le client ;
- extrait de journal montrant une requête réussie et une requête absente.

---

## 18. Cours — Services, événements et supervision

### 18.1 Un service Windows

Un service peut fonctionner sans session utilisateur ouverte.

Il possède notamment :

- un nom technique ;
- un nom d’affichage ;
- un état ;
- un mode de démarrage ;
- un compte d’exécution ;
- des dépendances.

### 18.2 État et mode de démarrage

| Élément | Exemples |
|---------|----------|
| État actuel | En cours d’exécution, arrêté |
| Mode de démarrage | Automatique, manuel, désactivé |

Un service arrêté n’est pas forcément en panne : certains services démarrent seulement lorsqu’ils sont nécessaires.

À l’inverse, un service « en cours d’exécution » ne garantit pas que toutes ses fonctions sont opérationnelles.

### 18.3 Les principaux outils

| Outil | Usage |
|-------|-------|
| Gestionnaire des tâches | Vue rapide CPU, RAM, processus |
| Moniteur de ressources | Analyse plus détaillée |
| Analyseur de performances | Mesures dans le temps |
| Observateur d’événements | Événements système et applicatifs |
| Journaux IIS | Requêtes HTTP |
| PowerShell | Interrogation et automatisation |

### 18.4 Quels indicateurs observer ?

- utilisation CPU et durée de la charge ;
- mémoire disponible ;
- espace disque libre ;
- activité et latence disque ;
- état des services nécessaires ;
- résultat d’une requête fonctionnelle.

!!! note "Un indicateur isolé ne suffit pas"
    Un pic CPU de quelques secondes peut être normal.

    Un disque presque plein peut être critique même si le CPU est au repos.

### 18.5 Lire un événement

Relever :

1. l’heure ;
2. le fournisseur ;
3. l’identifiant ;
4. le niveau ;
5. le message ;
6. le contexte.

Un événement ancien sans lien avec l’incident peut détourner le diagnostic.

---

## 19. TD 8 — Diagnostiquer un incident IIS

**Durée : 60 minutes**

### Objectif

Suivre une méthode, identifier une panne simple, rétablir le service et prouver le retour à la normale.

### Étape 1 — Établir l’état de référence

Sur le serveur :

```powershell
Get-Service W3SVC, WAS
Get-Website
Get-WebAppPoolState -Name "TSSR-Pool"
```

Sur le client :

```powershell
Test-NetConnection 192.168.50.10 -Port 80
```

Vérifier aussi la page dans le navigateur.

### Étape 2 — Introduire une panne contrôlée

Le formateur ou le binôme arrête le service :

```powershell
Stop-Service W3SVC
```

Cette manipulation ne doit être faite que sur la VM de laboratoire.

### Étape 3 — Observer sans corriger immédiatement

Sur le client :

- actualiser la page en évitant de se fier à une copie en cache ;
- relever le message exact ;
- refaire le test TCP ;
- noter l’heure.

Un port peut parfois rester accessible au niveau de la pile HTTP alors que le service applicatif ne fournit plus la réponse attendue. Il faut relever le comportement réel, pas imposer une conclusion à partir du seul port.

### Étape 4 — Formuler des hypothèses

Exemples :

- service arrêté ;
- site arrêté ;
- pool arrêté ;
- liaison incorrecte ;
- pare-feu ;
- page manquante ;
- problème de permissions.

Pour chaque hypothèse, proposer un test.

### Étape 5 — Examiner les services et événements

```powershell
Get-Service W3SVC, WAS

Get-WinEvent -FilterHashtable @{
    LogName = "System"
    StartTime = (Get-Date).AddMinutes(-30)
} -MaxEvents 50 |
    Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message
```

Chercher les événements cohérents avec l’arrêt et l’heure du test.

### Étape 6 — Corriger

```powershell
Start-Service W3SVC
```

Puis :

```powershell
Get-Service W3SVC
```

### Étape 7 — Vérifier le service rendu

Depuis le client :

```powershell
Invoke-WebRequest -Uri "http://192.168.50.10/" -UseBasicParsing |
    Select-Object StatusCode, StatusDescription
```

### Étape 8 — Observer les ressources

Sur le serveur :

1. ouvrir le Gestionnaire des tâches ;
2. consulter CPU et mémoire ;
3. ouvrir le Moniteur de ressources ;
4. repérer l’activité réseau ou disque pendant plusieurs accès à la page.

Ne pas générer de charge massive : l’objectif est de comprendre l’outil.

### Livrable

Dans `07-diagnostic.md` :

```text
Symptôme :
Heure :
Périmètre touché :
Hypothèses :
Tests réalisés :
Résultats :
Cause identifiée :
Correction :
Vérification après correction :
```

!!! success "Résultat attendu"
    La cause est justifiée par une observation. Le rétablissement est confirmé depuis le client, pas seulement par l’état du service sur le serveur.

---

# Jour 3 — Protéger, automatiser et dépanner

## 20. Cours — Sauvegarde et continuité de service

### 20.1 Copier n’est pas toujours sauvegarder

Une copie simple peut être utile, mais une stratégie de sauvegarde doit répondre à plusieurs questions :

- quoi protéger ?
- à quelle fréquence ?
- où conserver les copies ?
- combien de versions garder ?
- qui peut les supprimer ?
- comment restaurer ?
- combien de temps prend la restauration ?

### 20.2 Trois notions à distinguer

| Notion | Finalité |
|--------|----------|
| Haute disponibilité | Réduire les interruptions |
| Sauvegarde | Conserver des données récupérables |
| Reprise après sinistre | Rétablir un service après incident majeur |

### 20.3 RPO et RTO

**RPO — Recovery Point Objective**

Perte de données maximale acceptable, exprimée en durée.

Exemple : un RPO de 24 heures signifie qu’une journée de modifications peut être perdue au maximum.

**RTO — Recovery Time Objective**

Durée maximale souhaitée pour rétablir le service.

Exemple : un RTO de 4 heures vise un rétablissement dans les quatre heures.

### 20.4 Principe 3-2-1

Une stratégie classique vise :

- 3 copies des données ;
- sur 2 supports ou systèmes de stockage distincts ;
- dont 1 copie hors site.

Selon les risques, on ajoute notamment des protections hors ligne ou immuables, et une vérification régulière de la récupérabilité.

### 20.5 Limites du laboratoire

Nous sauvegardons `D:` vers `E:`.

Cela permet d’apprendre :

- le lancement d’une sauvegarde ;
- la lecture du catalogue ;
- la restauration d’un fichier.

Cela ne protège pas contre la destruction de l’hôte ou de tous les disques virtuels.

La sauvegarde de `D:` ne constitue pas non plus une sauvegarde complète du serveur. Par exemple, une partie de la configuration IIS est stockée sur `C:`.

### 20.6 Une sauvegarde doit être testée

Le message « sauvegarde terminée » ne suffit pas.

Il faut restaurer, puis vérifier :

- la présence du fichier ;
- son contenu ;
- son intégrité ;
- et, selon le besoin, ses permissions.

---

## 21. TD 9 — Sauvegarder et restaurer un fichier

**Durée : 90 minutes**

### Objectif

Sauvegarder le volume de données, supprimer un fichier de test et restaurer ce fichier dans un autre emplacement.

### Étape 1 — Vérifier l’espace disponible

```powershell
Get-Volume -DriveLetter D, E |
    Select-Object DriveLetter, Size, SizeRemaining
```

Nettoyer les gros fichiers de test FSRM avant la sauvegarde.

### Étape 2 — Installer l’outil

```powershell
Install-WindowsFeature Windows-Server-Backup
```

Ouvrir **Sauvegarde Windows Server** depuis les outils du Gestionnaire de serveur.

### Étape 3 — Créer une preuve de restauration

```powershell
$fichierPreuve = "D:\Partages\Compta\preuve-restauration.txt"

@"
Fichier de preuve TSSR
Créé le : $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Ce contenu doit être récupéré après suppression.
"@ | Set-Content -Path $fichierPreuve -Encoding UTF8

$hashAvant = (Get-FileHash -Path $fichierPreuve -Algorithm SHA256).Hash
$hashAvant
```

Copier l’empreinte dans le livrable, hors du dossier qui sera supprimé.

Une empreinte permet de comparer le contenu binaire avant et après restauration.

### Étape 4 — Sauvegarder le volume D:

```powershell
wbadmin start backup -backupTarget:E: -include:D: -quiet
```

!!! warning "Ce que cette commande fait"
    Elle lance une sauvegarde ponctuelle du volume `D:` vers `E:`.

    Elle ne sauvegarde pas automatiquement tout le système et ne crée pas une stratégie de conservation complète.

Attendre la fin de l’opération.

Pour chaque commande native importante, relever immédiatement son code de sortie si nécessaire :

```powershell
$LASTEXITCODE
```

Un code de sortie ne remplace pas la lecture du message final et du catalogue.

### Étape 5 — Examiner le catalogue

```powershell
wbadmin get versions -backupTarget:E:
```

Relever l’identifiant de version affiché.

Puis remplacer le texte entre chevrons dans cette commande :

```powershell
wbadmin get items -version:<IDENTIFIANT_A_RECOPIER> -backupTarget:E:
```

!!! note "Ne pas deviner le format de la date"
    Recopier exactement l’identifiant renvoyé par `wbadmin get versions`.

    Le texte `<IDENTIFIANT_A_RECOPIER>` est un repère pédagogique, pas une valeur à exécuter telle quelle.

### Étape 6 — Simuler une suppression

Vérifier une dernière fois que le fichier de test a bien été sauvegardé.

```powershell
Remove-Item -Path "D:\Partages\Compta\preuve-restauration.txt" -Confirm
```

Contrôler :

```powershell
Test-Path "D:\Partages\Compta\preuve-restauration.txt"
```

Résultat attendu : `False`.

### Étape 7 — Restaurer dans un autre emplacement

Méthode graphique recommandée :

1. ouvrir Sauvegarde Windows Server ;
2. cliquer sur **Récupérer** ;
3. sélectionner la sauvegarde de ce serveur ;
4. choisir la bonne date et heure ;
5. sélectionner **Fichiers et dossiers** ;
6. retrouver `preuve-restauration.txt` ;
7. choisir un autre emplacement ;
8. indiquer `D:\Restauration` ;
9. lire les options concernant les conflits et permissions ;
10. lancer la récupération.

Équivalent en ligne de commande, en adaptant la version :

```powershell
wbadmin start recovery `
    -version:<IDENTIFIANT_A_RECOPIER> `
    -itemType:File `
    -items:D:\Partages\Compta\preuve-restauration.txt `
    -recoveryTarget:D:\Restauration `
    -backupTarget:E: `
    -quiet
```

Utiliser une seule des deux méthodes, puis vérifier son résultat.

### Étape 8 — Retrouver le fichier restauré

Selon les options et l’organisation recréée par l’outil, des sous-dossiers peuvent être présents :

```powershell
Get-ChildItem -Path "D:\Restauration" `
    -Recurse `
    -Filter "preuve-restauration.txt"
```

Affecter à `$fichierRestaure` le chemin réellement observé :

```powershell
$fichierRestaure = "D:\Restauration\chemin-observe\preuve-restauration.txt"
```

### Étape 9 — Vérifier l’intégrité

```powershell
Get-Content -Path $fichierRestaure

$hashApres = (Get-FileHash -Path $fichierRestaure -Algorithm SHA256).Hash

$hashAvant -eq $hashApres
```

Résultat attendu : `True`.

Si la console a été fermée, retrouver `$hashAvant` dans le livrable et comparer explicitement les deux empreintes.

### Étape 10 — Remettre le fichier à disposition

Après validation du contenu :

```powershell
Copy-Item `
    -Path $fichierRestaure `
    -Destination "D:\Partages\Compta\preuve-restauration.txt"
```

Contrôler les permissions :

```powershell
icacls "D:\Partages\Compta\preuve-restauration.txt"
```

Depuis le client, vérifier :

- lecture avec Alice ;
- possibilité de modification avec Bruno.

!!! note "Restaurer des données et restaurer un service"
    Retrouver les octets du fichier est une étape. Le remettre au bon endroit, avec les bons accès, termine le rétablissement du service utilisateur.

### Livrable

Dans `08-sauvegarde-restauration.md` :

- source et destination ;
- heure de début et de fin ;
- identifiant de version ;
- preuve de suppression ;
- chemin de restauration ;
- empreintes avant et après ;
- résultat du test utilisateur ;
- limites de cette sauvegarde.

---

## 22. Cours — Automatiser sans perdre le contrôle

### 22.1 Pourquoi automatiser ?

L’automatisation permet de :

- répéter une opération de manière cohérente ;
- réduire les oublis ;
- exécuter un contrôle à heure fixe ;
- conserver une trace ;
- gagner du temps.

Elle peut aussi répéter une erreur à grande échelle. Un script doit donc être testé et limité à son besoin.

### 22.2 Script et tâche planifiée

- Le **script** décrit le travail.
- La **tâche planifiée** définit quand, comment et avec quelle identité il s’exécute.

Une tâche peut fonctionner sans utilisateur connecté si elle est correctement configurée.

### 22.3 Une tâche doit être observable

Elle doit produire :

- un résultat ;
- un journal ;
- un code de sortie exploitable ;
- une date d’exécution.

L’absence de fenêtre à l’écran ne prouve ni la réussite ni l’échec.

### 22.4 Protéger les scripts privilégiés

Si une tâche exécutée avec de forts privilèges lance un script modifiable par un utilisateur ordinaire, cet utilisateur pourrait faire exécuter ses propres commandes avec ces privilèges.

Il faut donc protéger :

- le fichier ;
- son dossier ;
- les emplacements dont le script dépend.

!!! warning "Compte SYSTEM"
    Le compte SYSTEM possède des privilèges très élevés sur la machine locale.

    Il est utilisé ici pour simplifier un exercice local sans gérer de mot de passe dans la tâche. En production, rechercher une identité et des privilèges adaptés au strict besoin.

---

## 23. TD 10 — Automatiser un rapport de contrôle

**Durée : 75 minutes**

### Objectif

Créer un rapport quotidien contenant :

- la date ;
- le nom du serveur ;
- l’espace disponible sur les volumes ;
- l’état de plusieurs services ;
- les événements récents de niveau critique ou erreur.

### Étape 1 — Protéger les dossiers

Sur le serveur :

```powershell
foreach ($chemin in @("D:\Scripts", "D:\Rapports")) {
    icacls $chemin /grant:r `
        '*S-1-5-18:(OI)(CI)(F)' `
        '*S-1-5-32-544:(OI)(CI)(F)'

    icacls $chemin /inheritance:r
}
```

Vérifier qu’aucun compte de test ne dispose d’un accès en écriture.

### Étape 2 — Créer le script

Créer :

```text
D:\Scripts\controle-quotidien.ps1
```

Contenu :

```powershell
$ErrorActionPreference = "Stop"

$horodatage = Get-Date -Format "yyyyMMdd-HHmmss"
$rapport = "D:\Rapports\controle-$horodatage.txt"

try {
    "CONTROLE QUOTIDIEN DU SERVEUR" |
        Set-Content -Path $rapport -Encoding UTF8

    "Date : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" |
        Add-Content -Path $rapport -Encoding UTF8

    "Serveur : $env:COMPUTERNAME" |
        Add-Content -Path $rapport -Encoding UTF8

    "`r`n=== VOLUMES ===" |
        Add-Content -Path $rapport -Encoding UTF8

    Get-Volume |
        Where-Object DriveLetter |
        Select-Object DriveLetter, FileSystemLabel, HealthStatus,
            @{Name="TailleGo";Expression={
                [math]::Round($_.Size / 1GB, 2)
            }},
            @{Name="LibreGo";Expression={
                [math]::Round($_.SizeRemaining / 1GB, 2)
            }} |
        Format-Table -AutoSize |
        Out-String |
        Add-Content -Path $rapport -Encoding UTF8

    "`r`n=== SERVICES ===" |
        Add-Content -Path $rapport -Encoding UTF8

    Get-Service -Name LanmanServer, W3SVC, WAS, SrmSvc |
        Select-Object Name, Status, StartType |
        Format-Table -AutoSize |
        Out-String |
        Add-Content -Path $rapport -Encoding UTF8

    "`r`n=== EVENEMENTS SYSTEME RECENTS ===" |
        Add-Content -Path $rapport -Encoding UTF8

    # Get-WinEvent peut signaler l'absence de correspondance comme une erreur.
    # On ne neutralise explicitement que ce cas attendu.
    $erreursEvenements = @()

    $evenements = Get-WinEvent -FilterHashtable @{
        LogName = "System"
        Level = 1, 2
        StartTime = (Get-Date).AddHours(-24)
    } -MaxEvents 20 `
      -ErrorAction SilentlyContinue `
      -ErrorVariable erreursEvenements

    $erreursReelles = @(
        $erreursEvenements | Where-Object {
            $_.FullyQualifiedErrorId -notlike "NoMatchingEventsFound*"
        }
    )

    if ($erreursReelles.Count -gt 0) {
        throw $erreursReelles[0]
    }

    if ($evenements) {
        $evenements |
            Select-Object TimeCreated, ProviderName, Id, Message |
            Format-List |
            Out-String |
            Add-Content -Path $rapport -Encoding UTF8
    }
    else {
        "Aucun événement critique ou erreur trouvé sur la période." |
            Add-Content -Path $rapport -Encoding UTF8
    }

    "`r`nExécution du contrôle terminée." |
        Add-Content -Path $rapport -Encoding UTF8

    exit 0
}
catch {
    $message = "ECHEC : $($_.Exception.Message)"

    Write-Error $message -ErrorAction Continue

    try {
        $message | Add-Content -Path $rapport -Encoding UTF8
    }
    catch {
        # L'erreur initiale reste signalée par le code de sortie.
    }

    exit 1
}
```

!!! note "Lire avant d’exécuter"
    Le formateur explique :
    - une variable ;
    - le pipeline `|` ;
    - `Select-Object` ;
    - la redirection vers un fichier ;
    - `try`, `catch` et les codes de sortie.

    Il n’est pas attendu qu’un débutant écrive seul ce script complet dès le premier essai.

### Étape 3 — Tester manuellement

Lancer dans un processus PowerShell distinct :

```powershell
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned `
    -File "D:\Scripts\controle-quotidien.ps1"

$LASTEXITCODE
```

Cette option définit la politique pour le processus lancé ; elle ne change pas globalement la politique de la machine.

Lire le dernier rapport :

```powershell
Get-ChildItem "D:\Rapports\controle-*.txt" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1 |
    Get-Content
```

### Étape 4 — Créer la tâche planifiée

```powershell
$action = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Argument '-NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -File "D:\Scripts\controle-quotidien.ps1"'

$declencheur = New-ScheduledTaskTrigger -Daily -At "18:00"

$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName "TSSR-Controle-Quotidien" `
    -Action $action `
    -Trigger $declencheur `
    -Principal $principal `
    -Description "Rapport local de contrôle du serveur TSSR"
```

### Étape 5 — Déclencher sans attendre

```powershell
Start-ScheduledTask -TaskName "TSSR-Controle-Quotidien"
```

Après quelques secondes :

```powershell
Get-ScheduledTask -TaskName "TSSR-Controle-Quotidien"

Get-ScheduledTaskInfo -TaskName "TSSR-Controle-Quotidien" |
    Select-Object LastRunTime, LastTaskResult, NextRunTime
```

Si la tâche fonctionne encore, attendre avant d’interpréter le résultat final.

### Étape 6 — Vérifier deux niveaux

1. **Exécution** : un nouveau rapport a-t-il été créé ? La tâche se termine-t-elle avec le code attendu ?
2. **Fonctionnement du serveur** : le rapport indique-t-il des services arrêtés, un manque d’espace ou des événements à analyser ?

!!! warning "Code 0 ≠ serveur sans problème"
    Dans ce script, le code `0` signifie que la collecte s’est déroulée correctement.

    Un service arrêté peut être mentionné dans un rapport produit avec succès. Le script ne classe pas automatiquement tous les états comme incidents.

### Étape 7 — Exercice d’adaptation

Ajouter au rapport une ligne indiquant si `D:` dispose de moins de 2 Gio libres.

Exemple de logique :

```powershell
$volumeD = Get-Volume -DriveLetter D

if ($volumeD.SizeRemaining -lt 2GB) {
    "ALERTE : espace libre faible sur D:" |
        Add-Content -Path $rapport -Encoding UTF8
}
```

Insérer ce contrôle avant la fin du bloc `try`, puis refaire le test manuel et planifié.

### Livrable

Dans `09-automatisation.md` :

- chemin du script ;
- explication de cinq commandes ;
- identité d’exécution ;
- horaire ;
- preuve de permissions sur le dossier ;
- résultat de la tâche ;
- extrait du rapport.

---

## 24. Cours — Une méthode de diagnostic reproductible

### 24.1 Ne pas commencer par redémarrer

Un redémarrage peut faire disparaître temporairement le symptôme sans expliquer la cause.

Il peut aussi :

- interrompre d’autres utilisateurs ;
- effacer des indices temporaires ;
- prolonger inutilement l’incident.

### 24.2 La démarche en sept étapes

1. **Qualifier le symptôme** : que constate précisément l’utilisateur ?
2. **Délimiter le périmètre** : un compte, un poste, un service ou tous les services ?
3. **Relever le contexte** : heure, dernière modification, message exact.
4. **Formuler une hypothèse**.
5. **Tester sans modifier inutilement**.
6. **Corriger une cause identifiée**.
7. **Valider depuis le point de vue utilisateur et documenter**.

### 24.3 Grille de diagnostic par couches

| Couche | Question | Exemple de vérification |
|--------|----------|-------------------------|
| VM | La machine fonctionne-t-elle ? | Console de l’hyperviseur |
| Réseau | La bonne carte et la bonne IP sont-elles utilisées ? | `Get-NetIPConfiguration` |
| Transport | Le port est-il accessible ? | `Test-NetConnection` |
| Service | Le composant nécessaire est-il démarré ? | `Get-Service` |
| Configuration | Le partage, site ou chemin existe-t-il ? | `Get-SmbShare`, `Get-Website` |
| Identité | Quel compte est réellement utilisé ? | `net use`, sessions SMB |
| Autorisation | Le compte dispose-t-il du droit demandé ? | ACL et permissions de partage |
| Ressource | Reste-t-il de la capacité ? | `Get-Volume`, `Get-FsrmQuota` |
| Application | La réponse fonctionnelle est-elle correcte ? | Lecture de fichier, requête HTTP |

### 24.4 Différencier trois symptômes

| Symptôme | Orientation initiale |
|----------|----------------------|
| Connexion impossible au port 445 | Réseau, pare-feu, service SMB |
| Port 445 accessible, ouverture du partage refusée | Identifiants, sessions ou permissions |
| Lecture possible, écriture d’un gros fichier impossible | Permissions d’écriture, quota ou espace disponible |

Ce sont des pistes, pas des conclusions automatiques.

---

## 25. TD 11 — Mise en situation professionnelle

**Durée : 120 minutes**

### Scénario

Le responsable de la structure demande la livraison du serveur.

Avant de valider, il souhaite :

- une démonstration des accès ;
- une preuve que les limites de stockage fonctionnent ;
- une page intranet à jour ;
- une restauration démontrée ;
- un contrôle automatique ;
- une fiche d’exploitation.

Un incident volontaire est introduit par le formateur.

### Répartition du temps

| Phase | Durée |
|-------|------:|
| Lecture de la demande et plan d’action | 10 min |
| Recette et ajustements | 50 min |
| Diagnostic de l’incident | 25 min |
| Documentation et démonstration | 25 min |
| Nettoyage et contrôle final | 10 min |
| **Total** | **120 min** |

### Mission 1 — Vérifier le socle

Contrôler :

- nom et adresse du serveur ;
- volumes `D:` et `E:` ;
- pare-feu ;
- accès RDP depuis le client ;
- absence de privilèges administratifs pour Alice et Bruno.

### Mission 2 — Recetter le serveur de fichiers

Démontrer :

- Alice lit un document mais ne peut pas le modifier ;
- Bruno crée, modifie et supprime un fichier de test ;
- la configuration ne repose pas sur un accès invité ;
- le quota est strict ;
- un fichier `.mp3` de test est refusé.

### Mission 3 — Mettre à jour l’intranet

Ajouter à la page :

- nom de l’apprenant ou du binôme ;
- date de recette ;
- liste des services fournis ;
- mention « Environnement de laboratoire ».

Démontrer l’affichage depuis le client.

### Mission 4 — Prouver la récupération

Créer un nouveau petit fichier, réaliser une sauvegarde, le supprimer puis le restaurer.

Le formateur peut accepter la preuve du TD 9 si le temps disponible ou les performances du stockage imposent de ne pas relancer une sauvegarde complète pendant l’évaluation.

Dans tous les cas, l’apprenant doit expliquer :

- quelle version a été utilisée ;
- où la restauration a été effectuée ;
- comment l’intégrité a été vérifiée.

### Mission 5 — Contrôler l’automatisation

Déclencher la tâche et montrer :

- l’heure d’exécution ;
- le résultat ;
- le nouveau rapport ;
- les permissions protégeant le script.

### Mission 6 — Traiter un incident

Le formateur choisit **un seul incident** parmi les suivants.

| Incident | Symptôme attendu |
|----------|-----------------|
| Service `W3SVC` arrêté | Intranet indisponible |
| Droit SMB de Bruno réduit à Lecture | Lecture possible, écriture refusée |
| Document `index.html` renommé | Page d’accueil attendue absente ou erreur liée au document par défaut |
| Règle HTTP du laboratoire désactivée, sans autre règle autorisante | Test local possible, accès client bloqué |

!!! warning "Conditions d’introduction des pannes"
    Le formateur relève l’état initial avant modification.

    La panne de pare-feu n’est utilisée que si les règles effectives ont été vérifiées : une autre règle autorisant HTTP pourrait rendre la panne inopérante.

    Aucun changement ne doit toucher le réseau de production ou les fichiers personnels.

### Fiche d’incident obligatoire

```text
Numéro d’incident :
Service concerné :
Symptôme :
Heure :
Impact :
Tests et résultats :
Cause :
Correction appliquée :
Résultat de la recette :
Mesure de prévention :
```

### Fiche d’exploitation attendue

Dans `10-recette-finale.md` :

```text
1. Identification du serveur
2. Ressources de la VM
3. Plan d’adressage
4. Volumes et chemins utiles
5. Comptes et groupes
6. Partages et permissions
7. Quotas et filtrage
8. Site IIS et pool
9. Règles de pare-feu utiles
10. Sauvegarde et procédure de restauration
11. Tâche planifiée et emplacement des rapports
12. Vérifications quotidiennes
13. Limites connues du laboratoire
14. Incident traité
```

### Barème proposé

| Critère | Points |
|---------|-------:|
| Socle système, stockage et inventaire | 10 |
| Comptes, groupes et moindre privilège | 10 |
| Partage SMB et permissions correctement testées | 20 |
| Quota et filtrage FSRM | 10 |
| Site IIS fonctionnel et correctement protégé | 10 |
| Sauvegarde et restauration vérifiées | 15 |
| Automatisation observable et script protégé | 10 |
| Diagnostic argumenté | 10 |
| Documentation claire et exploitable | 5 |
| **Total** | **100** |

**Seuil indicatif de validation : 70/100**, sous réserve des critères essentiels suivants :

- aucune permission excessive ajoutée pour masquer une erreur ;
- pare-feu conservé actif ;
- restrictions Alice/Bruno démontrées ;
- restauration réellement vérifiée ;
- manipulation des disques réalisée sans risque non maîtrisé.

---

## 26. Bilan et consolidation — 45 minutes

### Déroulement conseillé

| Activité | Durée |
|----------|------:|
| Quiz individuel | 10 min |
| Correction collective | 15 min |
| Présentation de deux incidents rencontrés | 10 min |
| Autoévaluation et synthèse | 10 min |

### Quiz

1. Quelle différence existe-t-il entre authentification et autorisation ?
2. Pourquoi attribuer les permissions à des groupes ?
3. Alice a Lecture sur le partage et Modification en NTFS. Peut-elle modifier par SMB ?
4. Les permissions de partage s’appliquent-elles à une ouverture directe sur `D:` ?
5. Quelle différence existe-t-il entre quota strict et quota souple ?
6. Un filtre `.exe` constitue-t-il un antivirus ?
7. Un port 80 ouvert prouve-t-il que la bonne page est disponible ?
8. Pourquoi un instantané n’est-il pas une sauvegarde indépendante ?
9. À quoi sert un test de restauration ?
10. Pourquoi protéger un script exécuté par SYSTEM ?
11. Quelle différence existe-t-il entre l’état d’un service et son mode de démarrage ?
12. Pourquoi faut-il tester un service depuis le client ?

??? note "Correction du quiz"
    1. L’authentification vérifie l’identité ; l’autorisation détermine les actions permises.
    2. Pour simplifier la gestion et éviter les attributions individuelles dispersées.
    3. Non. Le partage limite l’accès à la lecture.
    4. Non. Les permissions NTFS restent applicables.
    5. Le quota strict bloque le dépassement ; le quota souple l’observe.
    6. Non. Il filtre des noms ou extensions, pas la dangerosité réelle du contenu.
    7. Non. Il faut vérifier la réponse HTTP et le contenu.
    8. Il dépend généralement de l’infrastructure qui héberge la VM et ne couvre pas tous les risques.
    9. À démontrer que les données sont réellement récupérables et exploitables.
    10. Pour empêcher qu’un utilisateur fasse exécuter son propre code avec des privilèges élevés.
    11. L’état décrit la situation actuelle ; le mode décrit le comportement prévu au démarrage ou à la demande.
    12. Pour vérifier le service tel qu’il est réellement utilisé, avec le réseau, l’identité et les permissions concernés.

### Autoévaluation

Pour chaque ligne, choisir :

- **1** : je ne sais pas encore faire ;
- **2** : je sais faire avec le support ;
- **3** : je sais faire et expliquer.

| Compétence | Niveau |
|------------|--------|
| Installer et identifier un serveur | |
| Configurer un volume | |
| Créer utilisateurs et groupes locaux | |
| Publier un partage SMB | |
| Expliquer partage + NTFS | |
| Tester un accès autorisé et un refus attendu | |
| Configurer un quota | |
| Publier une page IIS | |
| Lire un journal utile | |
| Restaurer un fichier | |
| Vérifier une tâche planifiée | |
| Documenter un incident | |

---

## 27. Problèmes fréquents et solutions

### Problème — Le client ne peut pas joindre un service

**Vérifications :**

1. Les deux VM sont-elles démarrées ?
2. Sont-elles connectées au même réseau virtuel ?
3. Les adresses sont-elles correctes ?
4. Le service est-il démarré ?
5. Le bon port est-il utilisé ?
6. La règle de pare-feu correspond-elle au profil actif et à l’adresse du client ?

```powershell
Get-NetIPConfiguration
Get-NetConnectionProfile
Get-NetFirewallProfile
Test-NetConnection 192.168.50.10 -Port 445
```

Ne pas désactiver globalement le pare-feu pour « résoudre » le problème.

### Problème — Le partage demande toujours le mauvais compte

Examiner sur le client :

```powershell
net use
```

Puis :

- fermer les applications utilisant le serveur ;
- supprimer les connexions concernées ;
- vérifier le Gestionnaire d’identification si des informations ont été enregistrées ;
- reconnecter avec `SRV-FIC01\alice` ou `SRV-FIC01\bruno`.

### Problème — Bruno peut lire, mais ne peut pas écrire

Vérifier successivement :

```powershell
Get-SmbShareAccess -Name Compta
Get-LocalGroupMember -Group GL_Compta_Modification
icacls "D:\Partages\Compta"
Get-FsrmQuota -Path "D:\Partages\Compta"
Get-Volume -DriveLetter D
```

Puis renouveler la connexion SMB si les groupes ou autorisations ont été modifiés.

### Problème — Le lecteur Z: existe dans l’Explorateur mais pas dans une console élevée

Les lecteurs réseau peuvent différer entre contextes de connexion ou d’élévation.

Effectuer le test dans la session qui a créé le lecteur, ou utiliser explicitement le chemin UNC après authentification appropriée.

Ne pas modifier le système pour masquer ce comportement sans en comprendre la cause.

### Problème — IIS répond avec une erreur 403

Vérifier :

- le sous-code IIS ;
- l’existence de `index.html` ;
- la configuration du document par défaut ;
- le dossier physique ;
- les permissions de l’identité utilisée ;
- les journaux.

Activer l’exploration de répertoire n’est pas une correction universelle.

### Problème — IIS affiche une autre page

Vérifier :

```powershell
Get-Website
Get-WebBinding
```

Contrôler :

- quel site est démarré ;
- sa liaison ;
- son dossier physique ;
- l’URL réellement demandée ;
- le cache du navigateur.

### Problème — La tâche planifiée semble réussir mais aucun rapport n’apparaît

Vérifier :

- l’heure réelle de dernière exécution ;
- le chemin complet de PowerShell ;
- les arguments ;
- le chemin du script ;
- les permissions de l’identité d’exécution ;
- le code de retour ;
- l’historique de la tâche lorsqu’il est activé ;
- un test manuel dans un processus séparé.

### Problème — La sauvegarde réussit, mais le fichier restauré semble ancien

Vérifier :

- la date de création ou de modification du fichier ;
- la date de la sauvegarde sélectionnée ;
- l’identifiant de version ;
- le chemin restauré ;
- l’empreinte attendue.

Une restauration peut être techniquement réussie tout en ayant utilisé la mauvaise version.

---

## 28. Aide-mémoire

### Système et réseau

| Commande / Action | Description |
|-------------------|-------------|
| `hostname` | Afficher le nom de la machine |
| `whoami` | Afficher l’identité courante |
| `Get-ComputerInfo` | Consulter les informations système |
| `Get-NetAdapter` | Lister les cartes réseau |
| `Get-NetIPConfiguration` | Afficher la configuration IP |
| `Get-NetConnectionProfile` | Afficher le profil réseau |
| `Test-NetConnection IP -Port N` | Tester l’accès à un port TCP |
| `Get-NetFirewallProfile` | Vérifier l’état des profils de pare-feu |
| `wf.msc` | Ouvrir le pare-feu avancé |

### Rôles et services

| Commande / Action | Description |
|-------------------|-------------|
| `Get-WindowsFeature` | Lister rôles et fonctionnalités |
| `Install-WindowsFeature NOM` | Installer un composant |
| `Get-Service` | Consulter les services |
| `Start-Service NOM` | Démarrer un service |
| `Stop-Service NOM` | Arrêter un service |
| `services.msc` | Ouvrir la console des services |
| `Get-WinEvent` | Consulter les événements |

### Comptes et permissions

| Commande / Action | Description |
|-------------------|-------------|
| `Get-LocalUser` | Lister les comptes locaux |
| `Get-LocalGroup` | Lister les groupes locaux |
| `Get-LocalGroupMember -Group NOM` | Afficher les membres |
| `Add-LocalGroupMember` | Ajouter un membre |
| `icacls CHEMIN` | Afficher les permissions NTFS |
| `Get-SmbShare` | Lister les partages |
| `Get-SmbShareAccess -Name NOM` | Afficher les permissions du partage |
| `Get-SmbSession` | Afficher les sessions SMB |
| `Get-SmbOpenFile` | Afficher les fichiers ouverts par SMB |
| `net use` | Afficher les connexions réseau du client |

### Stockage, FSRM et sauvegarde

| Commande / Action | Description |
|-------------------|-------------|
| `Get-Disk` | Afficher les disques |
| `Get-Partition` | Afficher les partitions |
| `Get-Volume` | Afficher les volumes |
| `diskmgmt.msc` | Ouvrir la Gestion des disques |
| `Get-FsrmQuota` | Afficher les quotas FSRM |
| `Get-FsrmFileScreen` | Afficher les filtres FSRM |
| `wbadmin get versions` | Consulter les versions de sauvegarde |
| `Get-FileHash` | Calculer une empreinte de fichier |

### IIS et automatisation

| Commande / Action | Description |
|-------------------|-------------|
| `Import-Module WebAdministration` | Charger le module IIS |
| `Get-Website` | Afficher les sites |
| `Get-WebBinding` | Afficher les liaisons |
| `Get-WebAppPoolState -Name NOM` | Afficher l’état d’un pool |
| `Invoke-WebRequest` | Tester une réponse web |
| `Get-ScheduledTask` | Afficher les tâches planifiées |
| `Get-ScheduledTaskInfo` | Consulter les dernières exécutions |
| `Start-ScheduledTask` | Déclencher une tâche |
| `taskschd.msc` | Ouvrir le Planificateur de tâches |

---

## 29. Checklist finale de livraison

### Système

- [ ] Nom du serveur conforme.
- [ ] Adresse IP documentée.
- [ ] Horloge vérifiée.
- [ ] Pare-feu actif.
- [ ] Accès RDP limité au besoin du laboratoire.
- [ ] Inventaire à jour.

### Identités

- [ ] Alice et Bruno existent.
- [ ] Les permissions sont attribuées aux groupes.
- [ ] Les utilisateurs de test ne sont pas administrateurs.
- [ ] Aucun mot de passe ne figure dans la documentation.

### Stockage et partage

- [ ] `D:` et `E:` sont correctement identifiés.
- [ ] Le partage `Compta` pointe vers le bon dossier.
- [ ] Les ACL NTFS ont été vérifiées.
- [ ] Les permissions SMB ont été vérifiées.
- [ ] Alice ne peut pas modifier.
- [ ] Bruno peut modifier.
- [ ] Les fichiers volumineux de test ont été supprimés.

### FSRM

- [ ] Quota strict de 100 Mio.
- [ ] Seuil d’avertissement configuré.
- [ ] Filtrage actif testé.
- [ ] Limites du filtrage expliquées.

### IIS

- [ ] Site `Intranet-TSSR` démarré.
- [ ] Pool dédié.
- [ ] Identité et permissions cohérentes.
- [ ] Page accessible depuis le client.
- [ ] Journaux retrouvés.
- [ ] Aucune donnée sensible publiée en HTTP.

### Protection et exploitation

- [ ] Sauvegarde présente dans le catalogue.
- [ ] Restauration réellement réalisée.
- [ ] Intégrité vérifiée.
- [ ] Accès utilisateur vérifié après récupération.
- [ ] Script protégé contre les modifications non autorisées.
- [ ] Tâche planifiée testée.
- [ ] Rapport lisible.
- [ ] Incident documenté.
- [ ] Livrables déposés hors des VM.

---

## 30. Glossaire

ACL
:   Liste de contrôle d’accès décrivant les autorisations et refus associés à un objet.

Authentification
:   Vérification de l’identité présentée.

Autorisation
:   Décision permettant ou refusant une action à une identité.

Client
:   Système ou application qui demande un service.

Compte local
:   Compte enregistré dans la base de comptes d’une machine précise.

FSRM
:   Gestionnaire de ressources du serveur de fichiers : quotas, filtrage et rapports.

GPT
:   Format moderne de table de partitions.

Groupe local
:   Ensemble de comptes utilisé notamment pour attribuer des permissions.

Héritage
:   Transmission de permissions d’un objet parent à ses objets enfants.

Hyperviseur
:   Logiciel ou composant permettant d’exécuter des machines virtuelles.

IIS
:   Internet Information Services, plateforme de services web de Microsoft.

Moindre privilège
:   Principe consistant à n’accorder que les droits nécessaires.

NTFS
:   Système de fichiers Windows prenant notamment en charge des permissions détaillées.

Pool d’applications
:   Cadre d’exécution IIS regroupant des applications sous une configuration et une identité données.

Quota
:   Limite d’utilisation d’un espace de stockage.

RDP
:   Protocole utilisé notamment pour l’administration graphique distante.

Rôle serveur
:   Grande fonction installable sur Windows Server.

RPO
:   Objectif de perte de données maximale acceptable.

RTO
:   Objectif de délai de rétablissement d’un service.

Service Windows
:   Programme exécuté en arrière-plan, indépendamment d’une application utilisateur interactive.

SID
:   Identifiant de sécurité utilisé par Windows pour représenter une identité ou un groupe.

SMB
:   Protocole utilisé notamment pour le partage de fichiers sur le réseau.

Snapshot / instantané
:   État de référence géré par un hyperviseur, utile pour certains retours arrière mais ne remplaçant pas une sauvegarde indépendante.

UNC
:   Forme de chemin réseau telle que `\\serveur\partage\fichier`.

Volume
:   Espace de stockage utilisable par le système, souvent associé à une lettre de lecteur.

---

## 31. Ressources

### Documentation Microsoft

- [Documentation Windows Server](https://learn.microsoft.com/fr-fr/windows-server/) — Point d’entrée général.
- [Gestionnaire de serveur](https://learn.microsoft.com/fr-fr/windows-server/administration/server-manager/server-manager) — Administration des rôles et fonctionnalités.
- [Vue d’ensemble de SMB](https://learn.microsoft.com/fr-fr/windows-server/storage/file-server/file-server-smb-overview) — Services de fichiers SMB.
- [Gestionnaire de ressources du serveur de fichiers](https://learn.microsoft.com/fr-fr/windows-server/storage/fsrm/fsrm-overview) — Quotas, filtrage et rapports.
- [Documentation IIS](https://learn.microsoft.com/fr-fr/iis/) — Configuration et exploitation du serveur web.
- [Commande wbadmin](https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/wbadmin) — Sauvegarde et récupération en ligne de commande.
- [Module ScheduledTasks](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/) — Administration des tâches planifiées.
- [Module LocalAccounts](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/) — Gestion des comptes et groupes locaux.
- [Centre d’évaluation Windows Server 2025](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-server-2025) — Supports d’évaluation officiels.


!!! success "Compétence centrale à retenir"
    Administrer un serveur ne consiste pas seulement à installer des composants.

    Le travail du technicien est de **configurer un service utile, limiter ses accès, vérifier son fonctionnement, prévoir sa récupération et transmettre une documentation fiable**.
