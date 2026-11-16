---
title: "Défi final du parcours virtualisation : projet de migration et QCM"
date: 2026-11-16
author: Nicolas BODAINE
tags:
  - virtualisation
  - cloud
  - travaux-pratiques
difficulty: intermédiaire
os: Indépendant du logiciel ; VMware Workstation Pro 26H1, Debian 13.7, Proxmox VE 9.2
status: publié
---

# Défi final

!!! abstract "Résumé"
    Ce défi de synthèse mobilise les cinq jours du parcours. Il se déroule en trois temps :

    1. un **projet de conception** : proposer la nouvelle infrastructure virtualisée d'une PME, chiffres et schéma à l'appui ;
    2. un **diagnostic** : quatre incidents à résoudre, chacun lié à une partie du parcours ;
    3. un **QCM** de vingt questions pour faire le point.

    Les corrigés sont repliés : chercher d'abord, en s'aidant des parties du parcours et des [annexes](annexes.md).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| Durée estimée | 3 h (projet 1 h 45, diagnostic 30 min, QCM 30 min, correction 15 min) |
| Version décrite | Indépendant du logiciel |
| Place dans le parcours | Partie 17 sur 17 du parcours [Virtualisation](index.md) — jour 5 |
| Dernière mise à jour | 2026-11-16 |

---

<!-- NOTE DE RÉDACTION (non affichée) : QCM construit à partir du « QCM virtu avec réponses » du formateur (questions 1, 2, 3, 5, 6 et 8 reprises sous forme de questions à choix multiples, avec corrections : Workstation Pro gratuit depuis novembre 2024, FreeNAS devenu TrueNAS) et des parties 1 à 16. -->

## 1. Projet : la nouvelle infrastructure de Bureautix

### 1.1 La situation

La société *Bureautix* (40 salariés, un siège à Lyon, 30 % de télétravail) a une salle serveur vieillissante :

| Serveur physique | Rôle | Processeur | Mémoire | Disque utilisé | Utilisation moyenne du processeur |
|---|---|---|---|---|---|
| SRV-AD | Contrôleur de domaine, DNS, DHCP | 4 cœurs | 16 Go | 80 Go | 5 % |
| SRV-FIC | Serveur de fichiers | 4 cœurs | 16 Go | 1,5 To | 10 % |
| SRV-COMPTA | Logiciel de comptabilité (Windows) | 8 cœurs | 32 Go | 200 Go | 20 % |
| SRV-MAIL | Messagerie Exchange (fin de support) | 8 cœurs | 32 Go | 400 Go | 15 % |
| SRV-WEB | Site intranet sous Linux | 4 cœurs | 8 Go | 50 Go | 5 % |
| SRV-IMP | Serveur d'impression | 2 cœurs | 8 Go | 40 Go | 2 % |

La direction demande :

- une infrastructure **virtualisée**, qui supporte la **panne d'un serveur** sans arrêt de plus de quelques minutes ;
- un budget **maîtrisé** (les licences VMware ont été jugées trop chères) ;
- des **sauvegardes** fiables, dont une copie hors du bâtiment ;
- un accès sécurisé pour les **télétravailleurs** ;
- un avis argumenté sur ce qui pourrait partir dans le **cloud**.

### 1.2 Le travail demandé

Par deux (ou seul), en **1 h 45**, produire un dossier de deux pages maximum, avec :

1. **Dimensionnement** : la mémoire et le processeur réellement nécessaires (hypothèse : la mémoire **réellement utilisée** est de 50 % de la mémoire installée), le nombre d'hôtes et leur configuration minimale, avec la règle N+1 ([partie 1](01-comprendre-la-virtualisation.md#43-exercice-chiffre-combien-de-serveurs-economiser)).
2. **Hyperviseur** : le produit choisi et deux raisons ([parties 2](02-hyperviseur-et-machine-virtuelle.md), [9](09-panorama-des-technologies.md) et [10](10-types-hyperviseurs-paravirtualisation.md)).
3. **Stockage** : stockage partagé (NAS, SAN, ou stockage distribué hyperconvergé), justifié ([parties 7](07-virtualiser-le-stockage.md) et [12](12-stockage-sds-hyperconvergence.md)).
4. **Réseau** : un schéma avec au moins trois réseaux séparés (serveurs, postes, administration), les VLAN, et la place du pare-feu ([parties 6](06-virtualiser-le-reseau.md) et [13](13-reseau-virtuel-sdn-nfv.md)).
5. **Haute disponibilité et sauvegarde** : ce qui se passe si un hôte tombe en panne, et la stratégie de sauvegarde (règle 3-2-1).
6. **Cloud et postes** : ce qui part en SaaS, ce qui reste sur site, et la solution pour les télétravailleurs ([parties 14](14-virtualiser-les-applications.md) et [15](15-le-cloud.md)).
7. **Risques** : trois risques du projet et la parade pour chacun.

??? success "Corrigé indicatif"
    **1. Dimensionnement**

    - Processeur réellement utilisé : 4 × 5 % + 4 × 10 % + 8 × 20 % + 8 × 15 % + 4 × 5 % + 2 × 2 % = 0,2 + 0,4 + 1,6 + 1,2 + 0,2 + 0,04 ≈ **3,6 cœurs**.
    - Mémoire réellement utilisée : (16 + 16 + 32 + 32 + 8 + 8) × 50 % = 112 × 0,5 = **56 Go**.
    - Si la messagerie part en SaaS (voir le point 6), il reste environ 2,4 cœurs et 40 Go.
    - Avec une marge (croissance, pics, hyperviseur) et la règle **N+1** : **trois hôtes** de 16 cœurs et 128 Go chacun, par exemple. Deux hôtes suffiraient pour la charge, mais trois sont nécessaires pour un stockage distribué de type Ceph et donnent une vraie marge en cas de panne ou de maintenance.

    **2. Hyperviseur** : **Proxmox VE** (libre, sans licence par cœur, cluster, haute disponibilité, Ceph et sauvegarde intégrés, compétences Linux déjà présentes) ; ou **Hyper-V** si l'entreprise a déjà des licences Windows Server Datacenter et des compétences Microsoft. VMware est écarté par la direction pour son coût.

    **3. Stockage** : hyperconvergence avec **Ceph** sur les trois hôtes (pas de baie à acheter, tolère la perte d'un hôte) ; ou un **NAS/SAN** redondant en iSCSI ou NFS, plus simple à comprendre mais qui devient un point unique de défaillance s'il n'est pas lui-même redondé.

    **4. Réseau** : VLAN 10 serveurs, VLAN 20 postes, VLAN 30 administration (consoles des hyperviseurs, accès réservé), VLAN 40 stockage et migration (réseau dédié au trafic Ceph ou iSCSI) ; un pare-feu (par exemple pfSense ou OPNsense, en cluster) entre les VLAN et vers Internet ; ponts « VLAN aware » sur les hôtes.

    **5. Haute disponibilité et sauvegarde** : si un hôte tombe, la haute disponibilité redémarre ses VM sur les deux autres (coupure de la durée d'un redémarrage). Sauvegardes quotidiennes des VM (par exemple Proxmox Backup Server ou Veeam) sur un serveur dédié, une **copie hors site** (cloud ou second site), et des **tests de restauration** réguliers ; les instantanés ne servent qu'avant les opérations risquées.

    **6. Cloud et postes** : la **messagerie** part en **SaaS** (Microsoft 365 ou une offre européenne) : Exchange sur site arrive en fin de support et coûte cher à maintenir. Le contrôleur de domaine, les fichiers et la comptabilité restent sur site (ou dans un IaaS souverain). Pour les télétravailleurs : **VPN** avec authentification multifacteur vers les ressources internes, ou **publication** de la comptabilité (RemoteApp) ; un VDI complet serait surdimensionné pour 12 télétravailleurs.

    **7. Risques** : panne pendant la migration → migrer serveur par serveur, avec retour arrière prévu (garder les anciens serveurs quelques semaines) ; manque de compétences → formation de l'équipe et documentation ; console des hyperviseurs compromise → VLAN d'administration, comptes nominatifs, authentification multifacteur, mises à jour régulières.

## 2. Diagnostic : quatre incidents

Pour chaque incident, donner la cause la plus probable, la vérification et la correction.

1. Dans Workstation, une VM Debian refuse de démarrer avec le message : *This host supports Intel VT-x, but Intel VT-x is disabled*.
2. Après avoir cloné une VM Linux trois fois, les trois clones obtiennent la même adresse IP et le serveur DHCP mélange leurs baux.
3. Un disque dynamique de 40 Go occupe 38 Go sur l'hôte alors que la VM n'en utilise que 6 Go. L'administrateur veut récupérer la place, mais la commande de réduction refuse de s'exécuter.
4. Deux serveurs Linux montent le même disque iSCSI formaté en ext4 ; au bout d'une heure, des fichiers sont corrompus.

??? success "Corrigé"
    1. La **virtualisation matérielle** est désactivée dans le **BIOS/UEFI** du PC. Vérifier dans le Gestionnaire des tâches (ligne **Virtualisation**), l'activer dans le BIOS/UEFI, éteindre complètement le PC et le rallumer ([partie 2](02-hyperviseur-et-machine-virtuelle.md#41-la-virtualisation-materielle-est-elle-activee)).
    2. Les clones ont gardé la **même identité** : identifiant de machine, identifiant DHCP (DUID). Lancer le script de personnalisation (ou les commandes de la [partie 4](04-partager-les-ressources.md#63-donner-une-identite-propre-au-clone)) sur chaque clone, puis redémarrer.
    3. Le disque a des **instantanés** (ou il est préalloué) : la réduction est impossible tant qu'ils existent. Supprimer les instantanés devenus inutiles, puis relancer `sudo vmware-toolbox-cmd disk shrink /` ([partie 4](04-partager-les-ressources.md#42-tp-regarder-le-disque-grandir)).
    4. Un système de fichiers **ext4** n'est pas fait pour être monté par **deux** machines à la fois : chacune écrit sans coordination. Un disque bloc partagé exige un **système de fichiers de cluster** (VMFS, CSV, GFS2, OCFS2), ou bien il faut partager des **fichiers** en NFS ou SMB ([partie 7](07-virtualiser-le-stockage.md#42-cote-client-se-connecter-a-la-cible)).

## 3. QCM de fin de parcours

Une seule bonne réponse par question, sauf mention contraire.

1. Quel type d'hyperviseur est dit *bare metal* ?
    a) Type 1 · b) Type 2 · c) Les deux · d) Aucun
2. VMware Workstation Pro est :
    a) un hyperviseur de type 1, payant · b) un hyperviseur de type 2, gratuit depuis novembre 2024 · c) un hyperviseur de type 2, payant · d) un conteneur
3. Quelle extension du processeur faut-il activer pour faire tourner des VM 64 bits dans Workstation ?
    a) Hyper-Threading · b) Intel VT-x ou AMD-V · c) TPM · d) Secure Boot
4. Un instantané est stocké :
    a) sur un autre disque, ce qui en fait une sauvegarde · b) dans le dossier de la VM, sur le même disque · c) dans le cloud · d) dans la mémoire de la VM
5. Un clone lié :
    a) est indépendant de la VM d'origine · b) partage le disque figé de la VM d'origine · c) occupe autant de place qu'un clone complet · d) ne peut pas démarrer
6. La surallocation de la mémoire consiste à :
    a) donner à une VM plus de mémoire que ce dont elle a besoin · b) attribuer au total aux VM plus de mémoire que l'hôte n'en possède · c) ajouter de la mémoire physique · d) désactiver l'espace d'échange
7. En mode **NAT** de Workstation, une VM :
    a) est joignable par tous les PC de la salle · b) sort sur Internet derrière l'adresse du PC · c) n'a pas accès à Internet · d) reçoit une adresse du routeur de la salle
8. Quelle est la différence entre un SAN et un NAS ?
    a) Le SAN partage des fichiers, le NAS des blocs · b) Le SAN partage des blocs (LUN), le NAS des fichiers · c) Aucune · d) Le NAS n'utilise pas le réseau
9. SMB signifie :
    a) *Server Message Block*, le partage de fichiers de Windows · b) *Simple Mail Box* · c) *Storage Management Bus* · d) *Secure Mount Base*
10. Quel port utilise iSCSI ?
    a) 445 · b) 2049 · c) 3260 · d) 8006
11. La migration à chaud (vMotion) :
    a) arrête la VM pendant le déplacement · b) déplace une VM allumée sans coupure perceptible · c) redémarre les VM d'un hôte en panne · d) copie la VM vers le cloud
12. La haute disponibilité (HA) :
    a) supprime toute coupure · b) redémarre automatiquement les VM d'un hôte en panne sur les autres hôtes · c) est une sauvegarde · d) ne fonctionne qu'avec un seul hôte
13. Qu'est-ce qui distingue un conteneur d'une VM ?
    a) Le conteneur a son propre noyau · b) Le conteneur partage le noyau de l'hôte · c) Le conteneur est toujours plus sûr · d) Il n'y a pas de différence
14. La paravirtualisation consiste à :
    a) émuler un vieux matériel connu · b) utiliser dans l'invité des pilotes ou un noyau qui dialoguent directement avec l'hyperviseur · c) virtualiser deux fois · d) désactiver VT-x
15. Un VLAN permet :
    a) de chiffrer le réseau · b) de séparer plusieurs réseaux logiques sur les mêmes équipements physiques · c) d'augmenter le débit · d) de remplacer le routeur
16. Quelle offre relève du **PaaS** ?
    a) Amazon EC2 · b) Microsoft 365 · c) Azure App Service · d) Un serveur Proxmox VE sur site
17. En IaaS, qui met à jour le système d'exploitation de la VM ?
    a) Le fournisseur · b) Le client · c) Personne · d) L'éditeur de l'hyperviseur
18. Quelles affirmations sont vraies ? (plusieurs réponses)
    a) Proxmox VE est basé sur Debian · b) Hyper-V est un hyperviseur de type 1 · c) FreeNAS s'appelle aujourd'hui TrueNAS · d) Une LUN ext4 peut être montée sans risque par deux serveurs à la fois
19. Quelle est la différence entre VMware Workstation et VirtualBox ?
    a) Workstation est de type 1, VirtualBox de type 2 · b) Les deux sont de type 2 et gratuits ; VirtualBox fonctionne aussi sur macOS, Workstation utilise le format VMDK commun à la gamme VMware · c) VirtualBox ne sait pas faire d'instantanés · d) Workstation ne fonctionne que sous Linux
20. Citer cinq avantages et cinq inconvénients de la virtualisation (réponse libre).

??? success "Corrigé du QCM"
    1. **a** (type 1). 2. **b**. 3. **b**. 4. **b** : un instantané n'est pas une sauvegarde. 5. **b**. 6. **b**. 7. **b**. 8. **b**. 9. **a**. 10. **c** (445 = SMB, 2049 = NFS, 8006 = interface web de Proxmox VE). 11. **b**. 12. **b**. 13. **b**. 14. **b**. 15. **b**. 16. **c** (EC2 = IaaS, Microsoft 365 = SaaS, Proxmox sur site = virtualisation sur site). 17. **b**. 18. **a, b, c** (d est faux : il faut un système de fichiers de cluster). 19. **b**.
    20. Avantages : moins de serveurs physiques (économies d'énergie, de place et de matériel) ; meilleure disponibilité (migration à chaud, haute disponibilité) ; isolation des services ; sauvegardes et retours arrière simplifiés (instantanés) ; souplesse (modèles, ajout de ressources en quelques clics). Inconvénients : point unique de défaillance si l'hôte tombe ; risques de sécurité propres (évasion de VM, console d'administration) ; contention des ressources entre VM ; stockage partagé à protéger ; coûts de licences et de compétences.

    **Barème indicatif** : 1 point par question de 1 à 19 (question 18 : 1 point si les trois bonnes réponses, et elles seules, sont cochées), question 20 sur 1 point. 16 sur 20 et plus : les bases sont solides ; de 10 à 15 : relire les parties des questions manquées ; moins de 10 : refaire les TP des jours 1 et 2.

---

## Ressources

- [Accueil du parcours](index.md) — le plan complet et les liens vers toutes les parties.
- [Annexes](annexes.md) — dépannage, aide-mémoire et glossaire.
- Partie précédente : [Tendances et métier](16-tendances-et-metier.md).

*[VM]: Virtual Machine — machine virtuelle
*[PME]: Petite ou moyenne entreprise
*[VLAN]: Virtual LAN — réseau local virtuel
*[SaaS]: Software as a Service — logiciel fourni en service
*[PaaS]: Platform as a Service — plateforme fournie en service
*[IaaS]: Infrastructure as a Service — infrastructure fournie en service
*[SAN]: Storage Area Network — partage de blocs
*[NAS]: Network Attached Storage — partage de fichiers
*[LUN]: Logical Unit Number — disque logique présenté par une baie
*[SMB]: Server Message Block — partage de fichiers Windows
*[DUID]: DHCP Unique Identifier — identifiant d'un client DHCP
*[VPN]: Virtual Private Network — réseau privé virtuel
*[HA]: High Availability — haute disponibilité
