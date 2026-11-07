---
icon: material/school
description: Cours complets et travaux pratiques en laboratoire virtuel — sauvegarde, systèmes, réseaux — pour débutants et techniciens en formation.
---

# Cours et Travaux Pratiques

Cette catégorie rassemble des **supports de formation complets**. Chaque parcours enchaîne un ou plusieurs cours théoriques et des travaux pratiques (TP) détaillés pas à pas, pensés pour être réalisés **en autonomie** par des débutants.

Tous les TP se déroulent dans un **laboratoire virtuel** : les captures d'écran, les adresses et les mots de passe indiqués sont ceux du lab décrit dans chaque parcours.

## Parcours disponibles

<div class="grid cards" markdown>

- :material-backup-restore:{ .lg .middle } __Veeam Backup & Replication 13.1__

    ---

    Comprendre la sauvegarde (RAID, 3-2-1-1-0, PCA/PRA), installer l'appliance Linux de Veeam, créer des dépôts, sauvegarder un serveur de fichiers Windows et restaurer un serveur Linux complet après une panne.

    [:octicons-arrow-right-24: Commencer le parcours](veeam/index.md)

- :material-wall-fire:{ .lg .middle } __Cluster pfSense en haute disponibilité__

    ---

    Construire un cluster actif/passif de deux pare-feux pfSense : adresses IP virtuelles CARP, synchronisation pfsync et XML-RPC, tests de bascule, agrégation LACP et mise à jour du cluster sans interruption de service.

    [:octicons-arrow-right-24: Commencer le parcours](pfsense-ha/index.md)

</div>

## Autres cours et TP du wiki

Ces supports, plus anciens, sont rangés dans leur catégorie thématique :

- [Découvrir les fonctions serveur de Windows Server](../systemes/windows-server-fonctions-serveur.md) — 21 h de cours et travaux dirigés : stockage, partages SMB, quotas, IIS, sauvegarde.
- [Découvrir les services d'infrastructure Windows Server](../systemes/windows-server-dns-ad-dhcp-wins.md) — 21 h : DNS, Active Directory, GPO, DHCP et WINS.

## Comment utiliser ces supports

- **Suivre l'ordre** des parties : chaque TP s'appuie sur le précédent.
- **Prendre des instantanés** (*snapshots*) des machines virtuelles aux points indiqués (🛟) : en cas d'erreur, on revient en arrière en un clic au lieu de tout recommencer.
- **Chercher avant d'ouvrir les corrigés** : ils sont repliés exprès.
- **Lire les encadrés** « Pourquoi ? » : ils expliquent ce que fait chaque réglage. Comprendre vaut mieux que recopier.
