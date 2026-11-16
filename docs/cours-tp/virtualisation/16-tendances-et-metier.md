---
title: "Tendances de la virtualisation et impact sur les métiers de l'informatique"
date: 2026-11-16
author: Nicolas BODAINE
tags:
  - virtualisation
  - cloud
  - conteneurs
  - cours
difficulty: débutant
os: Indépendant du logiciel
status: publié
---

# Tendances et métier

!!! abstract "Résumé"
    La virtualisation continue d'évoluer : les **conteneurs** et **Kubernetes** deviennent la norme pour les applications, le **calcul en périphérie** (*edge computing*) rapproche les serveurs des données, les **fonctions réseau** des opérateurs sont virtualisées, les **cartes graphiques** se partagent entre VM pour l'intelligence artificielle, et le rachat de VMware a rebattu les cartes du marché. Cette partie présente ces tendances avec des chiffres sourcés, puis s'interroge sur leurs **conséquences pour les métiers** de l'informatique, et pour le **TSSR** en particulier.

    Elle se termine par un **débat** et par la construction d'un **plan de compétences et de veille** personnel.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| Durée estimée | 1 h 30 |
| Version décrite | Indépendant du logiciel ; chiffres de novembre 2026 |
| Place dans le parcours | Partie 16 sur 17 du parcours [Virtualisation](index.md) — jour 5 |
| Dernière mise à jour | 2026-11-16 |

---

<!-- NOTE DE RÉDACTION (non affichée) : faits de faits-jours3-5.md §13 : CNCF Annual Cloud Native Survey publiée le 20/01/2026 (Kubernetes en production chez 82 % des utilisateurs de conteneurs) ; AWS Lambda annoncé le 13/11/2014 ; edge : pas de définition normative unique (NIST SP 500-325, ETSI MEC) ; NVIDIA vGPU (Proxmox VE pris en charge depuis vGPU 18) ; confidential computing (CCC, AMD SEV, Intel TDX) ; AIE : ~415 TWh en 2024, ~945 TWh projetés en 2030 ; heise / CloudBolt février 2026 : 86 % réduisent leur usage de VMware, 4 % l'ont entièrement remplacé ; REAC TSSR 2026 (cloud, cybersécurité, virtualisation). -->

## 1. Les grandes tendances

### 1.1 Les conteneurs et Kubernetes partout

Les applications modernes sont découpées en **microservices** (de petits services indépendants plutôt qu'un seul gros programme « monolithe »), chacun livré dans un **conteneur**. Pour faire tourner des centaines de conteneurs sur des dizaines de serveurs, on utilise un **orchestrateur** : **Kubernetes**, projet libre de la fondation CNCF, est devenu la référence. D'après l'enquête annuelle de la CNCF publiée en janvier 2026, **82 %** des organisations qui utilisent des conteneurs font tourner Kubernetes **en production**.

Les VM ne disparaissent pas pour autant : Kubernetes tourne très souvent **sur** des VM, et les hyperviseurs savent maintenant gérer VM et conteneurs côte à côte (Proxmox VE en est un exemple, vu en [partie 11](11-conteneurs.md)).

### 1.2 Le « sans serveur » (*serverless*)

Avec le **serverless**, le développeur ne gère même plus de VM ni de conteneur : il dépose une **fonction**, que le fournisseur exécute à chaque événement (une requête web, un fichier déposé) et facture à l'exécution. Le service **AWS Lambda**, lancé en novembre 2014, a popularisé le principe. Les serveurs existent toujours, mais ils sont entièrement gérés par le fournisseur.

### 1.3 Le calcul en périphérie (*edge computing*)

Il n'existe pas de définition unique, mais l'idée est de **traiter les données près de l'endroit où elles sont produites** (usine, magasin, antenne 5G, véhicule) plutôt que dans un centre de données lointain, pour réduire le **délai de réponse** et la **quantité de données** envoyées. On y retrouve des petits serveurs virtualisés, souvent avec des conteneurs, administrés **à distance** par centaines.

### 1.4 La virtualisation des fonctions réseau (NFV) et la 5G

Les opérateurs de télécommunications remplacent leurs équipements spécialisés (routeurs, pare-feux, cœurs de réseau mobile) par des **fonctions logicielles** qui tournent dans des VM (**VNF**) ou des conteneurs (**CNF**). Le cœur des réseaux 5G est ainsi virtualisé. C'est le même principe que le routeur Debian de la [partie 6](06-virtualiser-le-reseau.md), à très grande échelle (voir la [partie 13](13-reseau-virtuel-sdn-nfv.md)).

### 1.5 Les cartes graphiques virtualisées et l'intelligence artificielle

L'intelligence artificielle consomme énormément de calcul sur **cartes graphiques** (GPU). Les technologies de **GPU virtuel** (comme NVIDIA vGPU) partagent une carte entre plusieurs VM ; elles sont prises en charge par les principaux hyperviseurs, dont VMware ESXi, KVM et, depuis peu, Proxmox VE. Le marché du cloud est aujourd'hui tiré en grande partie par l'IA ([partie 15](15-le-cloud.md#21-le-marche-mondial)).

### 1.6 L'informatique confidentielle (*confidential computing*)

Une VM est protégée des **autres** VM, mais pas de l'**hyperviseur** ni de l'administrateur de l'hôte. L'**informatique confidentielle** chiffre la mémoire de la VM **pendant qu'elle s'exécute**, grâce au processeur (AMD SEV, Intel TDX) : l'hyperviseur et l'administrateur de l'hôte ne peuvent plus lire directement la mémoire de la VM. Ce n'est pas une garantie absolue (tout dépend du mode utilisé, de la vérification à distance de la VM, appelée *attestation*, et de qui détient les clés), mais c'est une réponse technique sérieuse à la question de la confiance envers les hébergeurs.

### 1.7 L'énergie

Les centres de données consomment de plus en plus d'électricité. L'Agence internationale de l'énergie (AIE) estime leur consommation mondiale à environ **415 TWh en 2024**, et prévoit qu'elle pourrait plus que **doubler**, jusqu'à environ **945 TWh en 2030**, surtout à cause de l'IA. La virtualisation reste l'un des premiers leviers d'économie (consolidation, extinction des ressources inutiles), comme l'a montré l'exercice de la [partie 1](01-comprendre-la-virtualisation.md#43-exercice-chiffre-combien-de-serveurs-economiser).

### 1.8 Le marché après le rachat de VMware

Depuis le rachat par Broadcom (fin 2023) et le passage aux abonnements, beaucoup d'entreprises ont réévalué leur dépendance à VMware. Une étude publiée début 2026 indique que **86 %** des entreprises interrogées **réduisent** leur usage de VMware, mais que seulement **4 %** l'ont **entièrement remplacé** : la migration se fait progressivement, vers Proxmox VE, Hyper-V, Nutanix ou le cloud. Savoir **migrer** des VM d'un hyperviseur à l'autre (V2V) et administrer **plusieurs** hyperviseurs devient un atout.

## 2. Quel impact sur les métiers de l'informatique ?

### 2.1 Ce qui change

| Hier | Aujourd'hui et demain |
|---|---|
| Installer des serveurs physiques un par un | Déployer des VM et des conteneurs à partir de **modèles** et de **scripts** |
| Configurer à la main, dans des interfaces graphiques | **Automatiser** : scripts, *Infrastructure as Code* (Ansible, Terraform…) |
| Un seul hyperviseur, un seul fournisseur | Environnements **hybrides** : sur site, plusieurs clouds, plusieurs hyperviseurs |
| Le matériel coûte à l'achat | Le cloud coûte **chaque mois** : surveiller et optimiser les dépenses (*FinOps*) |
| La sécurité, c'est le pare-feu | Sécuriser les **comptes**, les **hyperviseurs**, les consoles cloud et la **chaîne d'automatisation** |

### 2.2 Ce que cela veut dire pour un TSSR

Le référentiel du titre TSSR place la virtualisation et le cloud au cœur du métier (« exploiter des serveurs dans une infrastructure virtualisée », sur site ou dans le cloud), aux côtés de la cybersécurité. Les compétences qui comptent :

- **Linux et la ligne de commande** : Proxmox VE, les conteneurs et la plupart des clouds reposent sur Linux ;
- **les scripts et l'automatisation** (bash, PowerShell, puis Ansible), comme le script de personnalisation de la [partie 5](05-virtualiser-des-serveurs.md) ;
- **le réseau** : commutateurs virtuels, VLAN, routage, NAT, pare-feu ;
- **le stockage et la sauvegarde** : NAS, SAN, iSCSI, règle 3-2-1 ;
- **la sécurité** : comptes à privilèges, authentification multifacteur, mises à jour des hyperviseurs ;
- **la documentation** et la **veille technologique**, que le référentiel demande explicitement.

## 3. 💬 Débat : « Dans dix ans, plus besoin de techniciens systèmes et réseaux ? »

**En deux équipes, 30 minutes.** L'équipe « Oui » défend que le cloud, l'automatisation et l'intelligence artificielle rendront le métier inutile ; l'équipe « Non » défend qu'il se transforme. Chaque équipe prépare **cinq arguments** (10 minutes), puis débat (15 minutes), et la classe rédige une conclusion de cinq lignes (5 minutes). **Seul** : écrire trois arguments pour chaque camp, puis sa propre conclusion.

??? success "Éléments de réponse"
    - **Oui** : le SaaS supprime de nombreux serveurs internes ; le cloud gère le matériel ; l'automatisation et l'IA font une partie des tâches répétitives ; les petites entreprises n'ont plus de salle serveur.
    - **Non** : il faut toujours quelqu'un pour **choisir**, **configurer**, **sécuriser**, **surveiller** et **dépanner** (réseau local, postes, Wi-Fi, comptes, cloud, sauvegardes) ; les environnements hybrides sont plus complexes qu'avant ; les incidents de sécurité augmentent ; l'automatisation doit être écrite, testée et maintenue par des techniciens.
    - **Conclusion fréquente** : le métier **se transforme** plus qu'il ne disparaît ; les tâches manuelles répétitives diminuent, les compétences en automatisation, cloud, sécurité et documentation deviennent indispensables.

## 4. ✍️ Mon plan de compétences et de veille

Remplir ce tableau pour soi-même, puis le garder pour la suite de la formation.

| Rubrique | Ma réponse |
|---|---|
| Les trois compétences du parcours que je maîtrise le mieux | |
| Les trois compétences que je dois renforcer | |
| Une technologie que je vais approfondir dans les trois prochains mois (et pourquoi) | |
| Trois sources de veille que je vais suivre (dont une documentation officielle et le CERT-FR) | |
| Une certification ou un titre qui pourrait m'intéresser plus tard | |
| Un lab que je vais monter chez moi pour m'entraîner | |

## 5. Questions de révision

1. Qu'est-ce que Kubernetes, et pourquoi les conteneurs ne remplacent-ils pas complètement les VM ?
2. Quelle est l'idée du calcul en périphérie (*edge computing*) ?
3. Qu'apporte l'informatique confidentielle par rapport à une VM classique ?
4. Que sont une VNF et une CNF ?
5. Pourquoi la maîtrise de plusieurs hyperviseurs est-elle devenue un atout depuis 2023 ?
6. Citer trois compétences qui prennent de l'importance pour un TSSR.

??? success "Corrigé"
    1. Un **orchestrateur** libre qui déploie, répartit et surveille des conteneurs sur un ensemble de serveurs. Les VM restent utiles : isolation plus forte, systèmes différents (Windows et Linux), applications non conteneurisées ; et Kubernetes lui-même tourne souvent sur des VM.
    2. **Traiter les données près de leur source** (usine, magasin, antenne) pour réduire le délai de réponse et la quantité de données envoyées vers un centre de données lointain.
    3. La mémoire de la VM est **chiffrée pendant son exécution** par le processeur : l'hyperviseur et l'administrateur de l'hôte (donc le fournisseur de cloud) ne peuvent plus la lire directement. La protection dépend toutefois du mode utilisé, de l'attestation et de la gestion des clés.
    4. Une **VNF** est une fonction réseau (routeur, pare-feu, cœur de réseau mobile) qui tourne dans une **VM** ; une **CNF** est la même chose dans un **conteneur**.
    5. Parce que le rachat de VMware par Broadcom et le passage aux abonnements ont poussé de nombreuses entreprises à réduire leur usage de VMware et à migrer, progressivement, vers d'autres solutions (Proxmox VE, Hyper-V, Nutanix, cloud) : il faut savoir administrer et migrer entre plusieurs plateformes.
    6. Linux et la ligne de commande, l'automatisation (scripts, Ansible), le cloud hybride, la sécurité des comptes et des hyperviseurs, la documentation et la veille.

---

## Ressources

- [CNCF — Enquête annuelle Cloud Native 2025](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/) — l'adoption de Kubernetes (en anglais).
- [AIE — Energy and AI](https://www.iea.org/reports/energy-and-ai) — la consommation électrique des centres de données (en anglais).
- [Confidential Computing Consortium](https://confidentialcomputing.io/) — le consortium de la Linux Foundation sur l'informatique confidentielle (en anglais).
- [France Compétences — Titre TSSR (RNCP 37682)](https://www.francecompetences.fr/recherche/rncp/37682/) — les compétences du titre.
- Partie précédente : [Le cloud : IaaS, PaaS, SaaS](15-le-cloud.md) · Partie suivante : [Défi final](17-defi-final.md).

*[CNCF]: Cloud Native Computing Foundation
*[NFV]: Network Functions Virtualization — virtualisation des fonctions réseau
*[VNF]: Virtual Network Function — fonction réseau dans une VM
*[CNF]: Cloud-native Network Function — fonction réseau dans un conteneur
*[GPU]: Graphics Processing Unit — carte graphique
*[AIE]: Agence internationale de l'énergie
*[TWh]: térawattheure, un milliard de kilowattheures
*[IA]: intelligence artificielle
*[TSSR]: Technicien supérieur systèmes et réseaux
*[V2V]: Virtual to Virtual — migration d'une VM entre hyperviseurs
*[CERT-FR]: centre gouvernemental de veille et de réponse aux attaques informatiques
*[VM]: Virtual Machine — machine virtuelle
*[VLAN]: Virtual LAN — réseau local virtuel
*[NAT]: Network Address Translation — traduction d'adresses
