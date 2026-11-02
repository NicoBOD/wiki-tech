---
title: "Sauvegarder vers Azure Blob Storage avec Veeam Backup & Replication (cours illustré)"
date: 2026-11-02
author: Nicolas BODAINE
tags:
  - sauvegarde
  - veeam
  - azure
  - stockage-objet
  - cours
difficulty: intermédiaire
os: Veeam Backup & Replication 12.1 (captures) et 13.1 (remarques) — Microsoft Azure
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Sauvegarder vers Azure Blob Storage avec Veeam

!!! abstract "Résumé"
    Cette partie montre comment envoyer des sauvegardes Veeam **hors site**, dans un **stockage objet Azure Blob** : création du compte de stockage et du conteneur dans le portail Azure, ajout du dépôt dans Veeam, puis sauvegarde d'un serveur Linux vers ce dépôt.

    Les deux erreurs rencontrées en conditions réelles sont expliquées : options de protection des données d'Azure incompatibles avec Veeam, et bibliothèque `libfuse` manquante sur le serveur Linux.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| Durée estimée | 1 h de lecture ; 1 h 30 pour qui dispose d'un abonnement Azure et veut la réaliser |
| Prérequis | Parties [1](01-comprendre-la-sauvegarde.md) à [6](06-sauvegarder-restaurer-serveur-linux.md) ; pour la pratique, un abonnement Azure (Azure for Students convient) |
| Place dans le parcours | Partie 7 sur 7 du parcours [Veeam Backup & Replication](index.md) |
| Dernière mise à jour | 2026-11-02 |

!!! warning "Partie illustrée"
    Cette partie se lit avec les captures. La réaliser demande un **abonnement Azure** et **génère des coûts**. Les captures montrent Veeam Backup & Replication **12.1** installé sur Windows et une version antérieure du portail Azure.

    Les principes restent valables en version 13. Les différences d'interface sont signalées dans des encadrés « En version 13 ». Le portail Azure évolue souvent : un libellé ou un onglet peut avoir légèrement changé.

---

## 1. Comprendre le stockage objet dans Azure

### 1.1 Pourquoi une copie dans le cloud ?

La règle [3-2-1](01-comprendre-la-sauvegarde.md#31-la-regle-3-2-1) demande **une copie hors site**. Le cloud la fournit sans second bâtiment : la copie part chez un fournisseur, dans un centre de données éloigné, et survit à un incendie ou à un vol dans l'entreprise. Avec l'**immuabilité**, elle répond aussi au « 1 » de la règle 3-2-1-1-0.

### 1.2 Le vocabulaire d'Azure Blob Storage

Azure Blob Storage est un **stockage objet** : on n'y range pas des fichiers dans des dossiers d'un disque, mais des **objets** (*blobs*) dans des **conteneurs**, accessibles par une API web (HTTPS).

| Terme | Rôle | Dans cette partie |
|-------|------|-------------------|
| **Abonnement** | Le contrat de facturation Azure | Azure for Students |
| **Groupe de ressources** | Un dossier logique qui regroupe des ressources liées, pratique pour tout supprimer d'un coup | `rg-veeam` |
| **Compte de stockage** | L'espace de stockage, avec un nom unique au monde | `storageaccountforveeam2` |
| **Conteneur** | Un « compartiment » dans le compte de stockage | `veeam` |
| **Blob** | Un objet stocké. Veeam découpe ses sauvegardes en très nombreux petits blobs | — |
| **Niveau d'accès** | *Hot* (chaud), *Cool* (froid), *Cold*, *Archive* : plus l'accès est rare, moins le stockage coûte cher, mais plus la lecture coûte cher | *Hot* |
| **Redondance** | Nombre de copies gardées par Azure : LRS (3 copies dans un centre de données), ZRS (3 zones), GRS (copie dans une seconde région) | GRS |

!!! danger "Le cloud se paie à l'usage"
    On paie le volume stocké, mais aussi les **opérations** (chaque écriture ou lecture de blob) et la **sortie de données** lors d'une restauration. Avant de pratiquer : créer une **alerte budgétaire**, et **supprimer le groupe de ressources** à la fin (voir la [partie 4](#4-supprimer-les-ressources-a-la-fin)). L'article [Stocker et partager des fichiers dans Azure Blob Storage](../../cloud/stocker-partager-fichiers-azure-blob-storage.md) présente aussi le service.

---

## 2. Créer le dépôt de sauvegarde dans Azure

### 2.1 Créer le groupe de ressources et le compte de stockage

1. Dans le [portail Azure](https://portal.azure.com), créer un **groupe de ressources** (par exemple `rg-veeam`) s'il n'en existe pas.
2. Ouvrir **Comptes de stockage > Créer**. Sur l'onglet **Informations de base** :
    - choisir l'abonnement et le groupe de ressources ;
    - donner un **nom unique** au compte (minuscules et chiffres uniquement, 3 à 24 caractères), ici `storageaccountforveeam2` ;
    - choisir une **région** proche, par exemple *(Europe) West Europe* ou *France Central* ;
    - garder les performances **Standard** (disques durs, suffisants pour de la sauvegarde) ;
    - choisir la **redondance** : *GRS* dans l'exemple (copie dans une seconde région), *LRS* pour un TP moins cher.

<figure markdown="span">
  ![Portail Azure, création d'un compte de stockage, onglet Informations de base](images/azure/az-01-compte-stockage-base.png){ loading=lazy }
  <figcaption>Onglet Informations de base : nom unique, région, performances Standard et redondance.</figcaption>
</figure>

3. Cliquer sur **Suivant**. Les onglets **Avancé** et **Réseau** peuvent garder leurs valeurs par défaut.

<figure markdown="span">
  ![Onglet Avancé de la création du compte de stockage, valeurs par défaut](images/azure/az-02-compte-stockage-avance.png){ loading=lazy }
  <figcaption>Onglet Avancé : valeurs par défaut (HTTPS obligatoire, TLS 1.2 minimum).</figcaption>
</figure>

<figure markdown="span">
  ![Onglet Réseau de la création du compte de stockage, accès public depuis tous les réseaux](images/azure/az-03-compte-stockage-reseau.png){ loading=lazy }
  <figcaption>Onglet Réseau : l'accès depuis Internet est nécessaire, le serveur Veeam étant hors d'Azure.</figcaption>
</figure>

4. Sur l'onglet **Protection des données**, **décocher les cases cochées par défaut** (suppression réversible des blobs, des conteneurs, etc.).

<figure markdown="span">
  ![Onglet Protection des données avec toutes les options de suppression réversible décochées](images/azure/az-04-protection-donnees.png){ loading=lazy }
  <figcaption>Onglet Protection des données : options de suppression réversible décochées.</figcaption>
</figure>

!!! question "Pourquoi désactiver une protection ?"
    La **suppression réversible** (*soft delete*) d'Azure garde quelque temps les blobs supprimés. Utile en général, elle entre en conflit avec Veeam, qui gère lui-même la rétention et l'immuabilité de ses sauvegardes. Veeam refuse alors d'ajouter le compte de stockage :

    ![Message de Veeam : impossible d'ajouter le compte de stockage, la suppression réversible est activée](images/azure/az-05-erreur-suppression-reversible.png){ loading=lazy width="420" }
    /// caption
    Erreur de Veeam quand la suppression réversible est activée
    ///

    De même, des **instantanés de blobs** présents dans le conteneur empêchent Veeam de lire la configuration d'immuabilité (erreur `SnapshotsPresent`) :

    ![Message de Veeam : échec de lecture de la configuration d'immuabilité du conteneur, des instantanés de blob sont présents](images/azure/az-06-erreur-immuabilite-instantanes.png){ loading=lazy width="420" }
    /// caption
    Erreur de Veeam quand le conteneur contient des instantanés de blobs
    ///

    La protection contre la suppression doit donc venir de **Veeam** (option d'immuabilité du dépôt, plus bas), pas des options génériques d'Azure.

5. Laisser les onglets suivants par défaut, cliquer sur **Vérifier + créer**, puis sur **Créer**.

<figure markdown="span">
  ![Onglet Vérifier + créer récapitulant les options du compte de stockage](images/azure/az-07-verifier-creer.png){ loading=lazy }
  <figcaption>Récapitulatif avant création.</figcaption>
</figure>

<figure markdown="span">
  ![Page indiquant que le déploiement du compte de stockage a réussi](images/azure/az-08-deploiement-termine.png){ loading=lazy }
  <figcaption>Le compte de stockage est déployé.</figcaption>
</figure>

### 2.2 Récupérer la clé d'accès

Dans le compte de stockage, ouvrir **Sécurité + réseau > Clés d'accès**, cliquer sur **Afficher** et copier le **nom du compte de stockage** et la **clé** (*key1*). Veeam s'en servira pour se connecter.

<figure markdown="span">
  ![Page Clés d'accès du compte de stockage, avec le nom du compte encadré ; la valeur de la clé est floutée](images/azure/az-09-cles-acces.png){ loading=lazy }
  <figcaption>Le nom du compte et la clé d'accès (floutée ici) servent d'identifiants à Veeam.</figcaption>
</figure>

!!! danger "Une clé d'accès vaut un mot de passe administrateur"
    La clé d'accès donne **tous les droits** sur le compte de stockage, y compris celui de supprimer les sauvegardes. Elle ne doit jamais apparaître dans un document, une capture ou un dépôt Git. Bonnes pratiques :

    - la **permuter** (*rotation*) régulièrement, et immédiatement en cas de fuite ;
    - préférer, quand c'est possible, l'option **Microsoft Azure storage account (Entra ID)** de Veeam, qui utilise une application Entra ID aux droits limités au lieu de la clé du compte.

### 2.3 Créer un conteneur

Ouvrir **Stockage des données > Conteneurs**, cliquer sur **+ Conteneur**, nommer le conteneur `veeam` et garder le niveau d'accès **Privé**.

<figure markdown="span">
  ![Liste des conteneurs du compte de stockage](images/azure/az-10-conteneurs.png){ loading=lazy }
  <figcaption>Menu Conteneurs du compte de stockage.</figcaption>
</figure>

<figure markdown="span">
  ![Panneau Nouveau conteneur avec le nom veeam et un accès privé](images/azure/az-11-nouveau-conteneur.png){ loading=lazy width="380" }
  <figcaption>Le conteneur reste privé : seul Veeam, avec la clé, y accède.</figcaption>
</figure>

!!! tip "Pour des sauvegardes immuables"
    L'immuabilité de Veeam sur Azure repose sur l'**immuabilité au niveau des versions** d'Azure. Deux réglages sont nécessaires :

    - sur le **compte de stockage**, activer le **contrôle de version des blobs** (onglet **Protection des données**) ;
    - sur le **conteneur**, cocher **Activer la prise en charge de l'immuabilité de niveau version** (*Enable version-level immutability support* dans le portail en anglais), dans le panneau **Avancé**, sans définir de stratégie de rétention par défaut : c'est Veeam qui fixe la durée.

    Dans l'exemple, la case n'est pas cochée : le dépôt ne sera pas immuable.

### 2.4 Ajouter le dépôt dans Veeam

1. Dans Veeam, ouvrir **Backup Infrastructure > Backup Repositories > Add Repository**, puis choisir **Object storage**.

<figure markdown="span">
  ![Assistant Add Backup Repository de la console Veeam, choix Object storage encadré](images/azure/az-12-vbr-ajout-depot-objet.png){ loading=lazy }
  <figcaption>Ajout d'un dépôt de type stockage objet.</figcaption>
</figure>

2. Choisir **Microsoft Azure Storage**, puis **Azure Blob Storage** (stockage chaud ou froid). *Azure Archive Storage* sert à l'archivage longue durée et *Azure Data Box* à l'envoi initial de gros volumes par colis.

<figure markdown="span">
  ![Liste des fournisseurs de stockage objet avec Microsoft Azure Storage encadré](images/azure/az-13-vbr-object-storage.png){ loading=lazy width="560" }
  <figcaption>Choix du fournisseur de stockage objet.</figcaption>
</figure>

<figure markdown="span">
  ![Choix du type de stockage Azure avec Azure Blob Storage encadré](images/azure/az-14-vbr-azure-blob.png){ loading=lazy width="560" }
  <figcaption>Azure Blob Storage pour des sauvegardes récentes.</figcaption>
</figure>

3. Nommer le dépôt (ici `Cloud_Azure_Repo_4`).

<figure markdown="span">
  ![Étape Name de l'assistant de dépôt objet](images/azure/az-15-vbr-nom-depot.png){ loading=lazy }
  <figcaption>Nom et description du dépôt.</figcaption>
</figure>

4. À l'étape **Account**, cliquer sur **Add** > **Microsoft Azure storage account (shared key)**, puis saisir le **nom du compte** et la **clé** copiés plus haut. La région reste *Azure Global (Standard)*.

<figure markdown="span">
  ![Étape Account, menu Add ouvert sur Microsoft Azure storage account (shared key)](images/azure/az-16-vbr-compte-ajout.png){ loading=lazy }
  <figcaption>Deux méthodes d'authentification : clé partagée ou Entra ID.</figcaption>
</figure>

<figure markdown="span">
  ![Fenêtre Credentials avec le nom du compte de stockage et la clé masquée](images/azure/az-17-vbr-identifiants.png){ loading=lazy }
  <figcaption>Identifiants du compte de stockage.</figcaption>
</figure>

5. Patienter pendant la connexion. À l'étape **Container**, Veeam détecte le conteneur `veeam`. Cliquer sur **Browse**, créer un dossier (ici `Backup_repo_Veeam`) et valider avec ++enter++.

<figure markdown="span">
  ![Fenêtre Select Folder affichant le conteneur veeam et le nouveau dossier Backup_repo_Veeam](images/azure/az-18-vbr-dossier.png){ loading=lazy }
  <figcaption>Un dossier dans le conteneur accueillera les sauvegardes.</figcaption>
</figure>

6. Garder les options par défaut pour ce TP, puis cliquer deux fois sur **Next**.

<figure markdown="span">
  ![Étape Container avec le conteneur, le dossier et les options de limite, d'immuabilité et de niveau Cool décochées](images/azure/az-19-vbr-conteneur-options.png){ loading=lazy }
  <figcaption>Options du conteneur : limite de consommation, immuabilité, niveau Cool.</figcaption>
</figure>

Ces options méritent d'être comprises :

- **Limit object storage consumption to** : plafond de volume, pour maîtriser la facture.
- **Make recent backups immutable for … days** : rend les sauvegardes récentes immuables pendant *n* jours (nécessite l'immuabilité de niveau version côté Azure). C'est l'option à activer en production.
- **Use cool blob storage tier** : stockage moins cher mais lectures plus chères ; adapté aux sauvegardes longues durées (complètes GFS).

!!! info "En version 13 : les options du conteneur"
    L'étape **Container** garde le plafond **Limit object storage consumption to**, mais les deux autres options changent de forme :

    - l'immuabilité se règle par la case **Make backups immutable (recommended)**, qui ouvre la fenêtre **Immutability Settings** : soit **For the entire duration of their retention policy** (la durée suit la rétention du job), soit **For the minimum immutability period only** avec une durée explicite (30 jours par défaut, de 1 à 999 jours) ;
    - le niveau d'accès se choisit dans la section **Access tier**, en cliquant sur le lien **Hot** : la fenêtre **Access Tier Settings** propose **Hot** ou **Cool**.

<figure markdown="span">
  ![Étape Apply : installation des composants et enregistrement du dépôt réussis](images/azure/az-20-vbr-application.png){ loading=lazy }
  <figcaption>Veeam installe les composants nécessaires et enregistre le dépôt.</figcaption>
</figure>

<figure markdown="span">
  ![Étape Summary récapitulant le dépôt Azure créé](images/azure/az-21-vbr-resume.png){ loading=lazy }
  <figcaption>Résumé : passerelle en connexion directe, serveur de montage, immuabilité désactivée.</figcaption>
</figure>

<figure markdown="span">
  ![Liste des dépôts de sauvegarde de la console Veeam avec le dépôt Azure encadré](images/azure/az-22-vbr-liste-depots.png){ loading=lazy }
  <figcaption>Le dépôt Azure apparaît avec les dépôts locaux et SMB.</figcaption>
</figure>

!!! info "En version 13 avec l'appliance"
    L'interface web de la version 13 ne sait ajouter que des dépôts Windows, Linux et durcis (*Hardened Repository*) : un dépôt Azure Blob s'ajoute depuis la **console Windows** installée sur `srv-fichiers` en [partie 3](03-preparer-le-lab-installer-appliance.md#11-installer-la-console-windows-sur-srv-fichiers). Le chemin y est **Backup Infrastructure > Backup Repositories > Add Repository > Object storage > Hyperscalers > Microsoft Azure Storage > Azure Blob Storage** (le niveau *Hyperscalers* regroupe les grands fournisseurs de cloud) ; la suite de l'assistant est celle décrite ci-dessus.

    L'appliance joue par défaut le rôle de **passerelle** et de **serveur de montage** (à moins d'en désigner d'autres). Elle doit pouvoir joindre `*.blob.core.windows.net` en HTTPS (port 443) : dans le lab, elle sort par le cluster pfSense.

---

## 3. Sauvegarder un serveur Linux vers Azure

Les captures montrent d'abord la sauvegarde d'une VM **Kali Linux**, puis, après des erreurs, celle d'un **serveur Ubuntu sans interface graphique**. Les étapes suivent le même assistant que la [partie 6](06-sauvegarder-restaurer-serveur-linux.md), avec un dépôt Azure comme destination.

### 3.1 Vérifier l'accès SSH

Veeam installe et pilote l'agent Linux **par SSH** : le service SSH doit être démarré sur la machine à protéger, joignable depuis le serveur Veeam, et la machine doit accéder à Internet pour télécharger ses dépendances.

<figure markdown="span">
  ![Session SSH ouverte avec MobaXterm vers la machine Kali Linux](images/azure/azj-01-connexion-ssh.png){ loading=lazy }
  <figcaption>Test de connexion SSH vers la machine à protéger.</figcaption>
</figure>

### 3.2 Créer le job de sauvegarde par agent

1. **Home > Backup Job > Linux computer**.

<figure markdown="span">
  ![Console Veeam, menu Backup Job ouvert sur Linux computer](images/azure/azj-02-nouveau-job-agent.png){ loading=lazy }
  <figcaption>Création d'un job de sauvegarde pour un ordinateur Linux.</figcaption>
</figure>

2. **Job Mode** : choisir **Workstation** (Kali est un poste de travail) ou **Server**, et le mode de gestion.

<figure markdown="span">
  ![Étape Job Mode avec Workstation sélectionné et le mode Managed by agent](images/azure/azj-03-mode-workstation.png){ loading=lazy }
  <figcaption>Type de machine et mode de gestion.</figcaption>
</figure>

!!! question "Géré par le serveur ou par l'agent ?"
    - **Managed by backup server** : le serveur Veeam lance les sauvegardes lui-même. Adapté aux serveurs toujours allumés et joignables.
    - **Managed by agent** : le serveur pousse une politique, puis l'agent sauvegarde **de lui-même** selon le planning, même si le serveur Veeam n'est pas joignable au moment voulu. Adapté aux postes de travail et aux portables. C'est le mode choisi ici.

3. Nommer le job, puis ajouter l'ordinateur par son **adresse IP** et ses identifiants SSH.

<figure markdown="span">
  ![Étape Name du job d'agent Linux](images/azure/azj-04-nom.png){ loading=lazy }
  <figcaption>Nom du job.</figcaption>
</figure>

<figure markdown="span">
  ![Fenêtre Add Computer avec l'adresse IP et le menu des identifiants SSH](images/azure/azj-05-ajout-ordinateur.png){ loading=lazy }
  <figcaption>Ajout de l'ordinateur par son adresse IP ; identifiants SSH à créer.</figcaption>
</figure>

4. Dans la fenêtre des identifiants, renseigner le compte et son mot de passe. Pour un compte qui n'est pas `root`, cocher **Elevate account privileges automatically** ; si `sudo` n'est pas installé (fréquent sur Debian quand un mot de passe `root` a été défini à l'installation), cocher aussi **Use "su" if "sudo" fails** et renseigner le mot de passe `root`.

<figure markdown="span">
  ![Fenêtre Credentials avec le nom d'utilisateur, le mot de passe et les options d'élévation de privilèges](images/azure/azj-06-identifiants-elevation.png){ loading=lazy }
  <figcaption>Élévation de privilèges par sudo, ou par su à défaut.</figcaption>
</figure>

<figure markdown="span">
  ![Liste des ordinateurs protégés contenant l'adresse IP de la machine](images/azure/azj-07-ordinateur-ajoute.png){ loading=lazy }
  <figcaption>L'ordinateur est ajouté au job.</figcaption>
</figure>

5. **Backup Mode** : **Entire computer** sauvegarde toute la machine. Pour économiser la bande passante vers le cloud, **File level backup (slower)** ne sauvegarde que des dossiers choisis, par exemple `/home/kali/`, avec des **exclusions** possibles (bouton **Advanced**).

<figure markdown="span">
  ![Étape Backup Mode avec Entire computer sélectionné](images/azure/azj-08-mode-machine-entiere.png){ loading=lazy }
  <figcaption>Sauvegarde de la machine entière.</figcaption>
</figure>

<figure markdown="span">
  ![Étape Backup Mode avec File level backup sélectionné](images/azure/azj-09-mode-fichiers.png){ loading=lazy }
  <figcaption>Variante : sauvegarde au niveau fichier.</figcaption>
</figure>

<figure markdown="span">
  ![Étape Objects avec le dossier /home/kali/ à sauvegarder](images/azure/azj-10-objets.png){ loading=lazy }
  <figcaption>Choix des dossiers à sauvegarder.</figcaption>
</figure>

<figure markdown="span">
  ![Fenêtre File Filters avec deux fichiers exclus](images/azure/azj-11-filtres.png){ loading=lazy width="460" }
  <figcaption>Masques d'inclusion et d'exclusion.</figcaption>
</figure>

6. **Destination** : **Veeam backup repository**, puis indiquer l'adresse du serveur Veeam et choisir le **dépôt Azure** à l'étape **Storage**.

<figure markdown="span">
  ![Étape Destination avec Veeam backup repository sélectionné](images/azure/azj-12-destination.png){ loading=lazy }
  <figcaption>Les sauvegardes passent par un dépôt géré par Veeam.</figcaption>
</figure>

<figure markdown="span">
  ![Étape Backup Server avec le nom du serveur Veeam](images/azure/azj-13-serveur.png){ loading=lazy }
  <figcaption>L'agent doit pouvoir résoudre et joindre ce nom ou cette adresse.</figcaption>
</figure>

<figure markdown="span">
  ![Étape Storage avec le dépôt Cloud_Azure_Repo_4 sélectionné et 7 points de restauration](images/azure/azj-14-stockage-azure.png){ loading=lazy }
  <figcaption>Le dépôt Azure est choisi comme destination.</figcaption>
</figure>

7. Laisser **Guest Processing** désactivé (pas d'application à préparer), définir un **planning** quotidien, vérifier le **résumé** et terminer.

<figure markdown="span">
  ![Étape Guest Processing, options désactivées](images/azure/azj-15-traitement-invite.png){ loading=lazy }
  <figcaption>Traitement applicatif désactivé.</figcaption>
</figure>

<figure markdown="span">
  ![Étape Schedule avec une exécution quotidienne](images/azure/azj-16-planification.png){ loading=lazy }
  <figcaption>Planification quotidienne.</figcaption>
</figure>

<figure markdown="span">
  ![Étape Summary du job d'agent Linux](images/azure/azj-17-resume.png){ loading=lazy }
  <figcaption>Résumé du job.</figcaption>
</figure>

### 3.3 Dépanner l'échec du *rescan* : la bibliothèque libfuse

Le premier essai a échoué à l'étape de **rescan**, l'inventaire que fait Veeam après avoir déployé l'agent :

<figure markdown="span">
  ![Fenêtre Machine rescan avec le statut Failed](images/azure/azj-18-echec-rescan.png){ loading=lazy }
  <figcaption>Le rescan de la machine échoue.</figcaption>
</figure>

La démarche de dépannage, à reproduire face à ce type d'échec :

1. **Vérifier le service** de l'agent sur la machine Linux : `sudo systemctl status veeamservice`. Il est arrêté et refuse de démarrer.

<figure markdown="span">
  ![Terminal : le service veeamservice est inactif et son démarrage échoue](images/azure/azj-19-service-arrete.png){ loading=lazy }
  <figcaption>Le service de l'agent Veeam ne démarre pas.</figcaption>
</figure>

2. **Lire le message d'erreur** dans les journaux (`journalctl -u veeamservice`) : une bibliothèque partagée est introuvable.

<figure markdown="span">
  ![Ligne de journal : error while loading shared libraries: libfuse.so.2](images/azure/azj-20-erreur-libfuse.png){ loading=lazy }
  <figcaption>La bibliothèque libfuse.so.2 est absente.</figcaption>
</figure>

3. **Installer la dépendance** manquante, puis redémarrer le service.

<figure markdown="span">
  ![Terminal : installation de libfuse2 et réparation des dépendances avec apt --fix-broken install](images/azure/azj-21-installation-libfuse.png){ loading=lazy }
  <figcaption>Installation de libfuse2 (après réparation des dépendances).</figcaption>
</figure>

<figure markdown="span">
  ![Terminal : le service veeamservice est actif](images/azure/azj-22-service-demarre.png){ loading=lazy }
  <figcaption>Le service démarre enfin.</figcaption>
</figure>

```bash title="Correctif selon la distribution"
# Ubuntu 22.04, Debian 12
sudo apt install libfuse2
# Ubuntu 24.04, Debian 13 (paquet renommé)
sudo apt install libfuse2t64
sudo systemctl restart veeamservice
```

!!! question "Pourquoi libfuse ?"
    **FUSE** (*Filesystem in Userspace*) permet de monter un système de fichiers sans modifier le noyau. L'agent Veeam s'en sert pour **monter le contenu d'une sauvegarde** et restaurer des fichiers. Les distributions récentes installent `libfuse3` par défaut, mais l'agent dépend aussi de l'ancienne version 2. Normalement, l'agent 13.1 installe lui-même ses dépendances pendant le déploiement, dont `libfuse2t64` sur Debian 13 (voir la [partie 6](06-sauvegarder-restaurer-serveur-linux.md#25-ce-que-lagent-a-installe)) : quand la bibliothèque manque, la cause est le plus souvent une machine sans accès correct aux dépôts de paquets au moment du déploiement, ou des paquets cassés (d'où le `apt --fix-broken install` de la capture).

4. **Relancer le rescan** : il réussit, et la sauvegarde vers Azure démarre.

<figure markdown="span">
  ![Console Veeam : rescan réussi du groupe de protection](images/azure/azj-23-rescan-reussi.png){ loading=lazy }
  <figcaption>Le rescan réussit.</figcaption>
</figure>

<figure markdown="span">
  ![Fenêtre de session : sauvegarde en cours avec le graphique de débit](images/azure/azj-24-sauvegarde-en-cours.png){ loading=lazy }
  <figcaption>La sauvegarde vers Azure est en cours.</figcaption>
</figure>

<figure markdown="span">
  ![Portail Azure : le conteneur contient le dossier Veeam et les objets de la sauvegarde](images/azure/azj-25-conteneur-azure.png){ loading=lazy }
  <figcaption>Les objets de la sauvegarde apparaissent dans le conteneur Azure.</figcaption>
</figure>

<figure markdown="span">
  ![Console Veeam : progression de la sauvegarde d'agent vers Azure](images/azure/azj-26-sauvegarde-progression.png){ loading=lazy }
  <figcaption>Suivi de la session dans Veeam.</figcaption>
</figure>

!!! tip "Le débit Internet compte"
    Envoyer une sauvegarde complète dans le cloud prend du temps : quelques Go mettent plusieurs minutes, quelques To plusieurs jours. En entreprise, on garde la sauvegarde rapide **en local** et on envoie une **copie** dans le cloud (*Backup Copy Job*, ou niveau de capacité d'un dépôt évolutif SOBR), plutôt que de sauvegarder directement vers le cloud.

---

## 4. Supprimer les ressources à la fin

Pour arrêter toute facturation après l'exercice :

1. dans Veeam, supprimer le job puis le dépôt Azure (**Remove**) ;
2. dans le portail Azure, supprimer le **groupe de ressources** `rg-veeam` : le compte de stockage et toutes les sauvegardes qu'il contient disparaissent avec lui ;
3. vérifier, quelques jours plus tard, la page **Coûts** de l'abonnement.

---

## 5. Questions de révision

1. Quelle règle de sauvegarde justifie l'envoi d'une copie dans le cloud ?
2. Pourquoi faut-il désactiver la suppression réversible d'Azure pour un dépôt Veeam ?
3. Que permet une clé d'accès de compte de stockage, et comment la protéger ?
4. Quelle différence entre un job « géré par le serveur » et « géré par l'agent » ?
5. Le rescan d'une machine Linux échoue. Quelles sont les trois premières vérifications ?
6. Pourquoi est-il préférable d'envoyer une **copie** de sauvegarde dans le cloud plutôt que la sauvegarde principale ?

??? success "Corrigé"
    1. La règle **3-2-1** (une copie hors site) ; avec l'immuabilité, la règle **3-2-1-1-0**.
    2. Parce que Veeam gère lui-même rétention et immuabilité : la suppression réversible d'Azure entre en conflit avec ses opérations, et Veeam refuse le compte de stockage.
    3. **Tous les droits** sur le compte de stockage, y compris la suppression des sauvegardes. On la garde secrète (jamais dans un document), on la permute régulièrement, et on préfère une authentification Entra ID aux droits limités.
    4. **Géré par le serveur** : le serveur Veeam déclenche les sauvegardes (serveurs toujours joignables). **Géré par l'agent** : l'agent applique la politique et sauvegarde seul selon le planning (postes de travail, portables).
    5. Le service de l'agent tourne-t-il (`systemctl status veeamservice`) ? Que disent les journaux (`journalctl -u veeamservice`) ? La machine a-t-elle accès aux dépôts de paquets pour installer les dépendances (ici `libfuse`) ?
    6. Pour **restaurer vite** depuis la copie locale (débit du réseau local, pas de frais de sortie), tout en gardant une copie hors site pour les sinistres.

---

## Ressources

- [Ajouter un dépôt Azure Blob Storage (documentation Veeam)](https://helpcenter.veeam.com/docs/vbr/userguide/adding_azure_object_storage.html) — assistant détaillé (en anglais).
- [Immuabilité au niveau des versions dans Azure Blob Storage](https://learn.microsoft.com/fr-fr/azure/storage/blobs/immutable-version-level-worm-policies) — documentation Microsoft.
- [Niveaux d'accès d'Azure Blob Storage](https://learn.microsoft.com/fr-fr/azure/storage/blobs/access-tiers-overview) — chaud, froid, archive.
- [Stocker et partager des fichiers dans Azure Blob Storage](../../cloud/stocker-partager-fichiers-azure-blob-storage.md) — article du wiki sur le service.
- Partie précédente : [Sauvegarder et restaurer un serveur Linux](06-sauvegarder-restaurer-serveur-linux.md) · Retour au [sommaire du parcours](index.md).
