---
title: "Le cloud : IaaS, PaaS, SaaS, responsabilité partagée et acteurs du marché"
date: 2026-11-16
author: Nicolas BODAINE
tags:
  - virtualisation
  - cloud
  - cours
  - travaux-pratiques
difficulty: débutant
os: Indépendant du logiciel (navigateur web)
status: publié
---

# Le cloud : IaaS, PaaS, SaaS

!!! abstract "Résumé"
    Le **cloud** (ou *informatique en nuage*) vend à la demande, par Internet, ce que les jours précédents ont fait construire à la main : des VM, des réseaux, du stockage, et même des applications toutes prêtes. Sans virtualisation, pas de cloud : chaque grand fournisseur fait tourner des millions de VM et de conteneurs sur ses hyperviseurs.

    Cette partie donne la **définition officielle** du cloud, explique les trois modèles de service **IaaS**, **PaaS** et **SaaS** et le **modèle de responsabilité partagée** (qui s'occupe de quoi, entre le client et le fournisseur), puis présente les **acteurs** du marché mondial et européen, avec la question de la **souveraineté** des données. Le TP se fait **sans créer de compte** : classer des services, répartir les responsabilités, et estimer le coût d'une VM avec les **calculatrices de prix** publiques d'AWS, d'Azure et de Google Cloud.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| Durée estimée | 2 h |
| Version décrite | Indépendant du logiciel ; chiffres du marché de novembre 2026 |
| Place dans le parcours | Partie 15 sur 17 du parcours [Virtualisation](index.md) — jour 5 |
| Dernière mise à jour | 2026-11-16 |

---

<!-- NOTE DE RÉDACTION (non affichée) : la présentation du formateur proposait un TP « créer un compte gratuit Azure et une VM » ; remplacé par un TP sans compte (décision du formateur au cadrage : Azure demande une carte bancaire). Arguments « cloud contre virtualisation classique » de la diapositive VIII repris en activité. Faits : NIST SP 800-145 ; responsabilité partagée Microsoft (page du 24/08/2026) ; parts de marché Synergy T3 2026 (publié le 30/10/2026) : AWS 26 %, Microsoft 19 %, Google 16 %, 167,7 Md$ ; SecNumCloud v3.2 (arrêté du 12/08/2026) ; S3NS qualifié (déc. 2025), Bleu en cours ; CLOUD Act mars 2018 ; EUCS non adopté ; calculatrices AWS, Azure, Google utilisables sans compte, pas de calculatrice publique OVHcloud (grille tarifaire publique). La liste ANSSI des offres qualifiées bloque les robots : la page renvoie le lecteur à la liste officielle plutôt que de figer des noms. -->

## 1. Qu'est-ce que le cloud ?

### 1.1 La définition du NIST

La définition de référence est celle du NIST, l'institut américain des normes (publication SP 800-145, 2011). Le cloud est un modèle qui donne accès, par le réseau, à un ensemble partagé de ressources informatiques configurables, qu'on peut obtenir et libérer **rapidement**, avec un minimum d'intervention du fournisseur. Il a **cinq caractéristiques essentielles** :

| Caractéristique | Ce que cela veut dire | Exemple |
|---|---|---|
| **Libre-service à la demande** | Le client obtient seul des ressources, sans appeler personne | Créer une VM en trois clics dans une console web |
| **Accès réseau large** | Les ressources sont accessibles par le réseau, depuis tout type d'appareil | Administrer ses serveurs depuis un navigateur ou une application |
| **Mutualisation des ressources** | Les ressources physiques du fournisseur sont partagées entre de nombreux clients | Des VM de clients différents sur les mêmes serveurs : c'est la virtualisation |
| **Élasticité rapide** | On augmente ou on réduit les ressources en quelques minutes, parfois automatiquement | Ajouter dix serveurs web pendant les soldes, les supprimer après |
| **Service mesuré** | La consommation est mesurée et facturée | Payer une VM à la seconde ou à l'heure |

Le NIST définit aussi **quatre modèles de déploiement** : le cloud **public** (ouvert à tous les clients), **privé** (pour une seule organisation, chez elle ou chez un hébergeur), **communautaire** (partagé par des organisations qui ont les mêmes besoins) et **hybride** (une combinaison, par exemple un cloud privé qui déborde sur un cloud public).

### 1.2 Trois modèles de service

![Quatre colonnes de couches empilées, du réseau à l'application : sur site, le client gère tout ; en IaaS, le fournisseur gère le matériel, le réseau, le stockage et la virtualisation ; en PaaS, il gère aussi le système et l'environnement d'exécution ; en SaaS, il gère tout, sauf les données et les comptes](images/schema-iaas-paas-saas.svg){ loading=lazy }
/// caption
Plus on monte de l'IaaS vers le SaaS, plus le fournisseur prend en charge de couches
///

| Modèle | Ce que le fournisseur fournit | Ce que le client gère | Exemples |
|---|---|---|---|
| **IaaS** (*Infrastructure as a Service*) | Des **VM**, du stockage et des réseaux virtuels | Le système d'exploitation, ses mises à jour, les logiciels, les données | Amazon EC2, Azure Virtual Machines, Google Compute Engine, OVHcloud Public Cloud |
| **PaaS** (*Platform as a Service*) | Une **plateforme** prête à exécuter du code : système, serveur web, base de données, mises à jour | Son application et ses données | Azure App Service, Google App Engine, AWS Elastic Beanstalk, Heroku |
| **SaaS** (*Software as a Service*) | Une **application** complète, prête à l'emploi | Ses données, ses utilisateurs et leurs droits | Microsoft 365, Gmail, Salesforce |

!!! question "Une image pour s'en souvenir : la pizza"
    - **Sur site** : on fait la pâte, on achète les ingrédients, on cuit dans son four, on mange chez soi.
    - **IaaS** : on loue une cuisine équipée ; on apporte ses ingrédients et sa recette.
    - **PaaS** : on commande une pizza à emporter ; on fournit seulement la table et les boissons.
    - **SaaS** : on mange au restaurant ; on choisit dans le menu, tout le reste est fait pour nous.

### 1.3 Le modèle de responsabilité partagée

Passer au cloud ne transfère **pas** toute la responsabilité au fournisseur. AWS résume la règle ainsi : le fournisseur est responsable de la sécurité **du** cloud (centres de données, matériel, hyperviseurs), le client de la sécurité **dans** le cloud (ce qu'il y installe et y stocke).

| Qui s'en occupe ? | Sur site | IaaS | PaaS | SaaS |
|---|---|---|---|---|
| Centre de données, matériel, réseau physique | Client | Fournisseur | Fournisseur | Fournisseur |
| Virtualisation (hyperviseurs) | Client | Fournisseur | Fournisseur | Fournisseur |
| Système d'exploitation et ses mises à jour | Client | **Client** | Fournisseur | Fournisseur |
| Applications | Client | Client | **Client** | Fournisseur |
| Données, comptes utilisateurs et droits d'accès, postes des utilisateurs | Client | **Client** | **Client** | **Client** |

!!! danger "Les données restent toujours la responsabilité du client"
    Quel que soit le modèle, Microsoft le rappelle : le client reste responsable de ses **données**, de ses **comptes**, de ses **appareils** et de la **gestion des accès**. Un mot de passe faible sur un compte Microsoft 365, une sauvegarde absente ou une VM IaaS jamais mise à jour sont des fautes du **client**, pas du fournisseur.

## 2. Les acteurs du cloud

### 2.1 Le marché mondial

Le marché mondial des services d'infrastructure cloud (IaaS, PaaS et cloud privé hébergé) est dominé par trois fournisseurs américains. Au troisième trimestre 2026, d'après le cabinet Synergy Research Group :

| Fournisseur | Part de marché (T3 2026) |
|---|---|
| **Amazon Web Services** (AWS) | 26 % |
| **Microsoft** (Azure) | 19 % |
| **Google Cloud** | 16 % |

Le marché a atteint **167,7 milliards de dollars** sur ce seul trimestre, en hausse de 55 % sur un an, tiré en grande partie par les services d'intelligence artificielle.

### 2.2 Les acteurs français et européens, et la souveraineté

Les données confiées à un fournisseur **américain** restent soumises au droit américain, même stockées en Europe : le **CLOUD Act** (2018) permet aux autorités des États-Unis d'exiger d'une entreprise américaine les données qu'elle héberge, où qu'elles soient. Pour les données sensibles, l'État français a créé une qualification exigeante, délivrée par l'**ANSSI** : **SecNumCloud** (référentiel en version 3.2). Elle impose notamment que le fournisseur et ses données échappent aux lois non européennes.

Quelques acteurs à connaître :

- **OVHcloud** (Roubaix) : le premier fournisseur européen, avec des offres qualifiées SecNumCloud ;
- **Scaleway** (groupe Iliad), **Outscale** (Dassault Systèmes), **Orange** (Cloud Avenue), **Cloud Temple** ;
- des offres « de confiance » construites avec des technologies américaines, mais exploitées par des sociétés françaises : **S3NS** (Thales avec Google Cloud), qualifiée SecNumCloud fin 2025, et **Bleu** (Orange et Capgemini avec Microsoft), dont la qualification est en cours.

!!! tip "Toujours vérifier la liste officielle"
    Les qualifications SecNumCloud sont délivrées, renouvelées ou retirées par l'ANSSI. Avant de recommander une offre, consulter la [liste officielle des prestataires qualifiés](https://cyber.gouv.fr/produits-services-qualifies) sur le site de l'ANSSI.

## 3. TP sans compte

### 3.1 ✍️ Exercice : classer les services

Classer chaque service en **IaaS**, **PaaS** ou **SaaS** :

1. Une VM Debian louée chez OVHcloud, sur laquelle on installe nginx soi-même.
2. Microsoft Teams.
3. Azure App Service, où l'on dépose le code d'un site web en PHP.
4. Amazon EC2.
5. Google Workspace (Gmail, Drive, Docs).
6. Une base de données gérée (Azure SQL Database, Amazon RDS) : on crée des tables, le fournisseur gère le serveur et les mises à jour.
7. Un espace de stockage en ligne pour particuliers, comme Dropbox.
8. Un serveur Proxmox VE installé dans la salle machine de l'entreprise.

??? success "Corrigé"
    1. **IaaS** : on loue une VM et on gère le système.
    2. **SaaS** : une application prête à l'emploi.
    3. **PaaS** : on fournit seulement le code, la plateforme est gérée.
    4. **IaaS** : des VM à la demande.
    5. **SaaS**.
    6. **PaaS** : une plateforme de base de données gérée (on parle aussi de *DBaaS*).
    7. **SaaS**.
    8. **Ni l'un ni l'autre** : c'est de la virtualisation **sur site**. Si l'entreprise y ajoute le libre-service, l'élasticité et la mesure de la consommation pour ses services internes, on parle de **cloud privé**.

### 3.2 ✍️ Exercice : qui est responsable ?

Pour chaque incident, dire qui est responsable (client ou fournisseur), et ce qu'il aurait fallu faire.

1. Une VM IaaS Windows Server est infectée par un rançongiciel qui exploitait une faille corrigée depuis six mois.
2. Un incendie détruit une salle du centre de données du fournisseur.
3. Un salarié supprime par erreur un dossier partagé dans Microsoft 365, et l'entreprise n'a aucune sauvegarde.
4. Le compte administrateur Azure de l'entreprise, protégé par un mot de passe simple, est piraté.

??? success "Corrigé"
    1. **Client** : en IaaS, les mises à jour du système de la VM sont à sa charge. Il fallait appliquer les correctifs (et surveiller les avis de sécurité).
    2. **Fournisseur** pour le centre de données ; mais le **client** est responsable de la **continuité** de ses services : répartir ses VM sur plusieurs zones ou régions, et garder des sauvegardes ailleurs.
    3. **Client** : les données restent sa responsabilité, même en SaaS. Il fallait une politique de rétention et une sauvegarde externe des données Microsoft 365 (règle 3-2-1).
    4. **Client** : les comptes et les accès lui reviennent toujours. Il fallait une authentification multifacteur et un mot de passe robuste.

### 3.3 TP : estimer le coût d'une VM avec les calculatrices

Les trois grands fournisseurs publient une **calculatrice de prix** utilisable **sans compte**. Objectif : estimer le coût mensuel d'**une VM Linux** de **2 vCPU** et **4 Go** de mémoire, avec un disque de **30 Go**, allumée **en permanence** (730 heures par mois), dans une région **française** quand elle existe.

| Fournisseur | Calculatrice | Région à choisir |
|---|---|---|
| AWS | [calculator.aws](https://calculator.aws/#/) : **Create estimate**, service **Amazon EC2** | Europe (Paris) |
| Microsoft Azure | [Calculatrice de prix Azure](https://azure.microsoft.com/fr-fr/pricing/calculator/) : produit **Machines virtuelles** | France Central |
| Google Cloud | [Calculatrice Google Cloud](https://cloud.google.com/products/calculator?hl=fr) : **Compute Engine** | europe-west9 (Paris) |

Pour chacun, noter dans un tableau : le nom du type de VM retenu, le prix mensuel, puis le prix si la VM n'est allumée que **10 heures par jour, 22 jours par mois** (220 heures).

Chez **OVHcloud**, il n'y a pas de calculatrice publique, mais la [grille tarifaire Public Cloud](https://www.ovhcloud.com/fr/public-cloud/prices/) est consultable sans compte : y relever le prix horaire ou mensuel d'une instance de taille proche.

??? success "Ce qu'il faut retenir (les prix exacts changent souvent)"
    - Les prix varient d'un fournisseur à l'autre, d'une région à l'autre et d'un mois à l'autre : c'est pourquoi on n'en donne pas ici. L'important est la **méthode**.
    - Une VM éteinte la nuit et le week-end coûte environ **trois fois moins** (220 heures au lieu de 730) : en IaaS, **éteindre ce qui ne sert pas** est la première économie. Attention : le **disque** reste facturé même VM éteinte.
    - Les calculatrices proposent des **réductions** contre un engagement d'un ou trois ans (instances réservées, plans d'économies) : intéressant pour un serveur qui tourne en permanence.
    - Comparer avec l'exercice de la [partie 1](01-comprendre-la-virtualisation.md#43-exercice-chiffre-combien-de-serveurs-economiser) : un serveur physique coûte cher à l'achat mais peu chaque mois ; le cloud ne coûte rien à l'achat mais se paie tous les mois. Le bon choix dépend de la durée d'utilisation et de la variabilité de la charge.

### 3.4 💬 Débat : le cloud ou la virtualisation sur site ?

**Par deux, 15 minutes.** L'un défend le **cloud public**, l'autre la **virtualisation sur site** (comme le Proxmox du jour 3), pour l'entreprise *Bureautix* (40 salariés). Chacun expose **cinq arguments distincts**. **Seul** : écrire cinq arguments pour chaque camp.

??? success "Éléments de réponse"
    - **Cloud** : pas d'investissement de départ ; élasticité ; haute disponibilité et sauvegardes plus faciles à mettre en place ; accès depuis partout ; le fournisseur gère le matériel, l'énergie, la sécurité physique ; PCA et PRA à moindre coût.
    - **Sur site** : maîtrise totale et données chez soi (souveraineté) ; coût prévisible et souvent plus bas sur plusieurs années pour une charge stable ; pas de dépendance à la connexion Internet ; pas de risque de hausse de prix imposée ; compétences internes conservées.
    - **Conclusion fréquente** : un modèle **hybride** (services standards en SaaS, comme la messagerie ; serveurs métier sur site ou en IaaS souverain), choisi service par service.

## 4. Questions de révision

1. Citer les cinq caractéristiques essentielles du cloud selon le NIST.
2. Quelle est la différence entre IaaS, PaaS et SaaS ? Donner un exemple de chacun.
3. En IaaS, qui applique les mises à jour du système d'exploitation de la VM ?
4. Quelle responsabilité reste **toujours** au client, quel que soit le modèle ?
5. Qu'est-ce que le CLOUD Act, et pourquoi a-t-on créé la qualification SecNumCloud ?
6. Quel lien y a-t-il entre la virtualisation et le cloud ?

??? success "Corrigé"
    1. Libre-service à la demande, accès réseau large, mutualisation des ressources, élasticité rapide, service mesuré.
    2. L'**IaaS** fournit l'infrastructure (VM, stockage, réseau) : le client gère le système et au-dessus (Amazon EC2). Le **PaaS** fournit une plateforme d'exécution : le client fournit son code (Azure App Service). Le **SaaS** fournit une application prête à l'emploi (Microsoft 365).
    3. Le **client**.
    4. Ses **données**, ses **comptes** et les **droits d'accès** (et ses appareils).
    5. Une loi américaine de 2018 qui permet aux autorités des États-Unis d'exiger d'une entreprise américaine les données qu'elle héberge, même hors des États-Unis. SecNumCloud, délivrée par l'ANSSI, qualifie des offres cloud dont le fournisseur et les données échappent aux lois non européennes, pour les données sensibles.
    6. Le cloud **repose** sur la virtualisation : la **mutualisation** des ressources et l'**élasticité** sont possibles parce que les serveurs, le stockage et les réseaux des fournisseurs sont virtualisés. Une VM IaaS est une VM comme celles du parcours, sur l'hyperviseur du fournisseur.

---

## Ressources

- [NIST SP 800-145 — The NIST Definition of Cloud Computing](https://csrc.nist.gov/pubs/sp/800/145/final) — la définition de référence (en anglais).
- [Microsoft — Responsabilité partagée dans le cloud](https://learn.microsoft.com/fr-fr/azure/security/fundamentals/shared-responsibility) — la matrice détaillée sur site, IaaS, PaaS, SaaS.
- [AWS — Modèle de responsabilité partagée](https://aws.amazon.com/fr/compliance/shared-responsibility-model/) — « la sécurité du cloud » et « la sécurité dans le cloud ».
- [ANSSI — Produits et services qualifiés](https://cyber.gouv.fr/produits-services-qualifies) — la liste officielle des offres SecNumCloud.
- Partie précédente : [Virtualiser les applications et les postes de travail](14-virtualiser-les-applications.md) · Partie suivante : [Tendances et métier](16-tendances-et-metier.md).

*[NIST]: National Institute of Standards and Technology — institut américain des normes
*[IaaS]: Infrastructure as a Service — infrastructure fournie en service
*[PaaS]: Platform as a Service — plateforme fournie en service
*[SaaS]: Software as a Service — logiciel fourni en service
*[DBaaS]: Database as a Service — base de données fournie en service
*[ANSSI]: Agence nationale de la sécurité des systèmes d'information
*[AWS]: Amazon Web Services
*[VM]: Virtual Machine — machine virtuelle
*[vCPU]: processeur virtuel
*[PCA]: plan de continuité d'activité
*[PRA]: plan de reprise d'activité
