---
title: "Chiffrer un poste Windows 11 Pro avec BitLocker : disque système, BitLocker To Go, manage-bde et déblocage helpdesk"
date: 2026-09-01
author: Nicolas BODAINE
tags:
  - bitlocker
  - windows
  - chiffrement
  - tpm
  - manage-bde
  - helpdesk
  - securite
difficulty: intermédiaire
os: Windows 11 Pro (24H2 / 25H2) — compatible Windows 10 Pro
status: publié
---

# Chiffrer un poste Windows 11 Pro avec BitLocker : disque système, BitLocker To Go, manage-bde et déblocage helpdesk

!!! abstract "Résumé"
    Prise en main complète de **BitLocker** sur un poste Windows 11 Pro, du clic dans le Panneau de configuration jusqu'au dépannage d'un utilisateur bloqué sur l'écran de récupération. Au programme : chiffrement du lecteur système `C:`, sécurisation d'une clé USB avec **BitLocker To Go**, administration en ligne de commande avec **`manage-bde`** (état, suspension pour une mise à jour de BIOS, reprise, extraction de la clé de récupération), et une **procédure helpdesk de niveau 1** pour débloquer un poste qui réclame ses 48 chiffres.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Windows 11 Pro 24H2 / 25H2 (physique ou VM avec TPM virtuel) |
| Édition requise | Pro, Entreprise ou Éducation — **pas** Famille |
| Matériel | TPM 2.0 + démarrage UEFI + une clé USB de test |
| Dernière mise à jour | 2026-09-01 |

!!! danger "Règle numéro un : pas de clé de récupération = pas de données"
    BitLocker fait exactement ce qu'on lui demande : rendre les données **illisibles** sans le bon secret. Si vous perdez à la fois le mot de passe/PIN **et** la clé de récupération à 48 chiffres, **personne** — ni vous, ni Microsoft, ni un logiciel de récupération — ne pourra relire le disque. Avant de cliquer sur « Activer BitLocker », sachez déjà **où** la clé de récupération sera stockée.

---

## Contexte

### À quoi sert le chiffrement de disque

Un mot de passe de session Windows protège **l'ouverture de session**, pas les données. Si on extrait le disque d'un portable volé pour le brancher sur une autre machine, les fichiers sont lisibles immédiatement. Le chiffrement de disque, dit **chiffrement au repos** (*data at rest*), déplace la protection sur le support lui‑même : sans la clé, le contenu du disque n'est qu'une suite d'octets aléatoires.

C'est l'équivalent Windows de ce que fait **LUKS** sous Linux (voir l'article connexe en fin de page).

### Les trois secrets à ne jamais confondre

C'est **la** source de confusion au support niveau 1. Prenez cinq minutes pour l'assimiler :

| Secret | À quoi ça ressemble | Qui le connaît | Quand est-il demandé |
|--------|---------------------|----------------|----------------------|
| **Mot de passe de session** | Le mot de passe Windows habituel | L'utilisateur | À l'ouverture de session, **après** le démarrage |
| **Mot de passe / PIN de déverrouillage** | Ce que l'utilisateur choisit (BitLocker To Go, ou PIN de démarrage) | L'utilisateur | Au quotidien, pour ouvrir le lecteur |
| **Clé de récupération** | **48 chiffres**, en 8 blocs de 6 : `123456-654321-…` | Le service IT / le compte Microsoft | **Uniquement** en cas de problème (secours) |

!!! warning "L'ID de clé n'est pas la clé"
    L'écran de récupération affiche aussi un **ID de la clé de récupération** (8 caractères hexadécimaux du type `8F3C1A2B`). C'est un **identifiant public**, non secret : il sert juste à savoir **quelle** clé chercher dans le coffre quand on en gère des centaines. Le taper dans le champ ne déverrouillera rien.

### Le rôle de la puce TPM

Sur un poste correctement équipé, l'utilisateur ne saisit **rien** au démarrage : le disque se déverrouille tout seul. Ce n'est pas de la magie, c'est le **TPM**.

Le TPM est un petit coprocesseur sécurisé soudé à la carte mère (ou intégré au CPU : *Intel PTT*, *AMD fTPM*). Il **scelle** la clé de chiffrement et ne la libère que si l'état de démarrage mesuré correspond à celui enregistré lors du chiffrement (firmware, Secure Boot, bootloader). Concrètement :

- démarrage normal → le TPM libère la clé → Windows démarre sans rien demander ;
- démarrage anormal (BIOS modifié, disque déplacé dans une autre machine, Secure Boot désactivé…) → le TPM **refuse** → BitLocker bascule en **mode récupération** et réclame les 48 chiffres.

!!! tip "Pourquoi c'est une bonne chose"
    Ce comportement « paranoïaque » est une **fonctionnalité**, pas un bug. Le passage en récupération signifie que quelque chose a changé dans la chaîne de démarrage — et c'est exactement le scénario contre lequel BitLocker protège.

---

## Prérequis

- **Windows 11 Pro / Entreprise / Éducation** (ou Windows 10 Pro). L'édition **Famille** ne propose que le *Chiffrement de l'appareil*, sans gestion fine ni BitLocker To Go.
- Un **compte administrateur local** sur le poste.
- Un **TPM 2.0** activé dans l'UEFI et un démarrage en mode **UEFI** (pas Legacy/CSM).
- Une **clé USB de test**, dont le contenu peut être perdu.
- Un **support externe** (autre clé USB, partage réseau, gestionnaire de mots de passe) pour y déposer les clés de récupération.
- **20 à 60 minutes** de chiffrement en tâche de fond pour `C:` (variable selon le disque et l'option choisie).

### Vérifier l'environnement en 4 commandes

Ouvrez **PowerShell en administrateur** (++win+x++ puis *Terminal (Admin)*) :

```powershell title="Contrôles préalables"
winver
Get-Tpm
Confirm-SecureBootUEFI
manage-bde -status
```

| Commande | Ce qu'on vérifie |
|----------|------------------|
| `winver` | L'édition et la version, par exemple *Windows 11 Pro 25H2*. Si vous lisez « Famille », inutile d'aller plus loin. |
| `Get-Tpm` | `TpmPresent : True` et `TpmReady : True` sont attendus. Équivalent graphique : ++win+r++ → `tpm.msc`. |
| `Confirm-SecureBootUEFI` | Renvoie `True` si Secure Boot est actif. Une **erreur** signifie que la machine démarre en mode Legacy/BIOS. |
| `manage-bde -status` | Dresse l'état BitLocker de **tous** les volumes de la machine. |

??? note "Cas particulier : machine virtuelle sans TPM"
    Pour un lab, deux options.

    **Option A — ajouter un TPM virtuel** (recommandé, c'est le scénario réaliste) :

    | Hyperviseur | Où l'activer |
    |-------------|--------------|
    | Hyper‑V | VM de **génération 2** → *Paramètres* → *Sécurité* → cocher *Activer le module de plateforme sécurisée* |
    | VMware Workstation / ESXi | La VM doit d'abord être **chiffrée**, puis *Ajouter un périphérique* → *Trusted Platform Module* |
    | VirtualBox 7.x | *Configuration* → *Système* → *TPM : v2.0* |
    | Proxmox VE | *Hardware* → *Add* → *TPM State* (v2.0), machine type **q35** + **OVMF/UEFI** |

    **Option B — autoriser BitLocker sans TPM** (dégradé : impose la saisie d'un mot de passe ou d'une clé USB à chaque démarrage) :

    ++win+r++ → `gpedit.msc` → *Configuration ordinateur* → *Modèles d'administration* → *Composants Windows* → *Chiffrement de lecteur BitLocker* → *Lecteurs du système d'exploitation* → **Exiger une authentification supplémentaire au démarrage** → **Activé** → cocher *Autoriser BitLocker sans un TPM compatible*. Puis `gpupdate /force`.

!!! note "BitLocker ≠ Chiffrement de l'appareil"
    Depuis Windows 11 24H2, beaucoup de postes récents sortent d'usine avec le **Chiffrement automatique de l'appareil** (*Auto‑DE*) déjà actif, la clé étant sauvegardée dans le compte Microsoft de l'utilisateur. C'est le même moteur cryptographique, mais sans les options de gestion. Si `manage-bde -status` indique déjà `Protection activée` alors que vous n'avez rien fait, c'est ça — et la clé est sur `https://aka.ms/myrecoverykey`.

---

## Partie 1 — Chiffrer le lecteur système `C:`

### Étape 1 : ouvrir la console BitLocker

Menu **Démarrer** → tapez `BitLocker` → **Gérer BitLocker**.

Chemins équivalents :

- ++win+r++ → `control /name Microsoft.BitLockerDriveEncryption`
- *Panneau de configuration* → *Système et sécurité* → *Chiffrement de lecteur BitLocker*
- *Paramètres* → *Confidentialité et sécurité* → *Chiffrement de lecteur BitLocker*

La console liste les volumes en trois familles : **Lecteur du système d'exploitation**, **Lecteurs de données fixes**, **Lecteurs de données amovibles**.

!!! failure "L'entrée « Gérer BitLocker » n'existe pas"
    Vous êtes sur **Windows 11 Famille**. Vérifiez avec `winver`. Seule une mise à niveau vers l'édition Pro débloque BitLocker.

### Étape 2 : lancer l'assistant

Sous **Lecteur du système d'exploitation (C:)**, cliquez sur **Activer BitLocker**. Windows contrôle le TPM, l'espace disque et la présence de la partition système, puis démarre l'assistant.

### Étape 3 : sauvegarder la clé de récupération ⚠️

L'assistant propose plusieurs destinations. **C'est l'étape la plus importante du tutoriel.**

| Option proposée | Usage recommandé |
|-----------------|------------------|
| **Enregistrer dans votre compte Microsoft** | Poste personnel — récupérable depuis n'importe quel navigateur |
| **Enregistrer sur une clé USB** | Poste hors domaine, lab, machine isolée |
| **Enregistrer dans un fichier** | Fichier `.txt` déposé sur un **autre** volume, un partage réseau ou un coffre de mots de passe |
| **Imprimer la clé de récupération** | Archivage papier en coffre — le grand classique en entreprise |

!!! danger "La règle d'or : jamais sur le volume en cours de chiffrement"
    Enregistrer la clé de `C:` **sur `C:`** revient à laisser la clé de la maison à l'intérieur de la maison. Le jour où le poste réclame la clé, le disque est **verrouillé** : le fichier existe toujours, mais il est illisible. Windows refuse d'ailleurs explicitement cette destination — ne cherchez pas à contourner par un dossier synchronisé qui pointe vers `C:`.

    **Bonne pratique : deux emplacements distincts**, par exemple le compte Microsoft (ou l'AD) **et** une impression / un fichier hors ligne.

!!! tip "En entreprise"
    La clé est normalement **remontée automatiquement** dans **Active Directory (AD DS)** ou **Microsoft Entra ID / Intune** par stratégie de groupe. Cela évite de dépendre de l'utilisateur — c'est précisément ce qui rend le scénario helpdesk de la partie 4 tenable à l'échelle d'un parc.

### Étape 4 : choisir l'étendue du chiffrement

| Option | Quand la choisir |
|--------|------------------|
| **Chiffrer uniquement l'espace disque utilisé** | Poste **neuf** ou fraîchement réinstallé. Rapide (quelques minutes). |
| **Chiffrer tout le lecteur** | Poste **déjà utilisé**. Plus lent, mais écrase aussi les résidus de fichiers supprimés dans l'espace libre. |

!!! warning "Le piège du « espace utilisé » sur un poste ancien"
    Un fichier supprimé n'est pas effacé, seulement déréférencé. Sur une machine en service depuis deux ans, l'espace « libre » contient encore des fragments de documents en clair. Sur un poste existant, prenez **Chiffrer tout le lecteur**.

### Étape 5 : choisir le mode de chiffrement

| Mode | Algorithme | À utiliser pour |
|------|-----------|-----------------|
| **Nouveau mode de chiffrement** | XTS‑AES 128 | Disques **internes** — plus performant et plus robuste |
| **Mode compatible** | AES‑CBC 128 | Supports **amovibles** destinés à être lus sur d'anciennes machines |

Pour `C:`, choisissez **Nouveau mode de chiffrement**.

### Étape 6 : exécuter le test système

Cochez **Exécuter le test système BitLocker**, puis **Continuer** et **Redémarrer maintenant**.

!!! question "À quoi sert ce test ?"
    Avant de chiffrer un seul octet, Windows fait une **répétition générale** : il redémarre et vérifie que le TPM libère bien la clé et que le disque est lisible. Si ce test échoue, BitLocker **annule** l'opération — le disque est encore en clair, donc rien n'est perdu. Sauter ce test, c'est risquer de découvrir un problème de firmware **après** avoir chiffré 200 Go.

### Étape 7 : suivre l'avancement

Au redémarrage, la session s'ouvre normalement et le chiffrement démarre **en tâche de fond**. Vous pouvez travailler pendant ce temps.

- Icône **BitLocker** dans la zone de notification → double‑clic pour la barre de progression.
- Ou en ligne de commande : `manage-bde -status C:` (voir partie 3).

!!! tip "Le poste peut être éteint pendant le chiffrement"
    L'opération est reprise automatiquement au démarrage suivant. Évitez tout de même une coupure de courant brutale ; sur un portable, laissez‑le sur secteur.

### Critère de validation

Ouvrez l'**Explorateur de fichiers** (++win+e++) → **Ce PC**, et regardez la vignette du lecteur `C:` :

| Ce que vous voyez sur l'icône | Signification |
|-------------------------------|---------------|
| **Cadenas gris ouvert** | Lecteur chiffré et **déverrouillé** — état normal de `C:` en session ✅ |
| **Cadenas doré fermé** | Lecteur chiffré et **verrouillé** — il faut un secret pour y accéder |
| **Cadenas avec un point d'exclamation** | Chiffrement en cours **ou** protection **suspendue** ⚠️ |
| **Aucun cadenas** | Lecteur **non chiffré** |

Contrôle en ligne de commande (la référence, sans ambiguïté) :

```console
manage-bde -status C:
```

!!! success "Résultat attendu"
    ```
        État de la conversion :         Complètement chiffré
        Pourcentage chiffré :           100,0%
        Méthode de chiffrement :        XTS-AES 128
        État de la protection :         Protection activée
        État du verrou :                Déverrouillé
    ```
    Les deux lignes qui comptent sont **Complètement chiffré** et **Protection activée**.

---

## Partie 2 — Sécuriser une clé USB avec BitLocker To Go

**BitLocker To Go** est la déclinaison de BitLocker pour les supports amovibles. La grande différence avec `C:` : il n'y a pas de TPM en face, donc le déverrouillage repose sur un **mot de passe** (ou une carte à puce) — puisque la clé doit pouvoir être lue sur n'importe quel poste.

!!! warning "Sauvegardez la clé USB avant de commencer"
    Le chiffrement d'un support déjà rempli est possible sans perte, mais toute manipulation sur une clé USB peut mal tourner. Utilisez une **clé de test** vide, comme prévu dans les prérequis.

### Étape 1 : lancer l'assistant depuis l'Explorateur

Branchez la clé USB, puis dans l'Explorateur : **clic droit** sur le lecteur (ex. `E:`) → **Afficher plus d'options** → **Activer BitLocker**.

!!! note "Le menu contextuel de Windows 11"
    Le menu court de Windows 11 masque la plupart des entrées héritées. **Afficher plus d'options** (ou ++shift+f10++) ouvre le menu complet. Alternative sans menu contextuel : *Panneau de configuration* → *Chiffrement de lecteur BitLocker* → section **Lecteurs de données amovibles**.

### Étape 2 : définir le mot de passe de déverrouillage

Cochez **Utiliser un mot de passe pour déverrouiller le lecteur** et saisissez‑le deux fois.

!!! tip "Choisir un bon mot de passe"
    Il sera tapé à la main, souvent sur un poste qui n'est pas le sien. Visez une **phrase de passe** longue et mémorisable plutôt qu'une bouillie de symboles. Et **stockez‑la dans un gestionnaire de mots de passe** — ce n'est pas parce qu'il existe une clé de récupération qu'il faut compter dessus au quotidien.

### Étape 3 : exporter la clé de récupération dans un fichier

Choisissez **Enregistrer dans un fichier**, puis une destination qui **n'est pas la clé USB en cours de chiffrement**.

Windows produit un fichier nommé `Clé de récupération BitLocker <ID>.txt` contenant :

```text title="Clé de récupération BitLocker 8F3C1A2B.txt"
Clé de récupération BitLocker

Pour vérifier que la clé de récupération est correcte, comparez le début
de l'identificateur ci-dessous avec la valeur affichée sur votre PC.

Identificateur :
	8F3C1A2B-4D5E-4F60-9A7B-1C2D3E4F5A6B

Clé de récupération :
	123456-654321-112233-445566-778899-009988-776655-443322
```

!!! example "Anatomie du fichier — à comprendre maintenant, ça servira en partie 4"
    - L'**identificateur** commence par `8F3C1A2B` : ce sont les **8 caractères** que l'écran de récupération affichera.
    - La **clé de récupération** est la suite de **48 chiffres**, en 8 blocs de 6.
    - Un même parc contient des dizaines de fichiers comme celui‑ci : l'identificateur est ce qui permet de retrouver le bon.

### Étape 4 : étendue et mode de chiffrement

- **Étendue** : « espace utilisé » sur une clé neuve, « tout le lecteur » sur une clé ayant déjà servi.
- **Mode** : choisissez le **mode compatible** (AES‑CBC). Le « nouveau mode » (XTS‑AES) n'est pas lisible par les versions de Windows antérieures à 1511 — pénalisant pour un support nomade.

Cliquez sur **Démarrer le chiffrement**. Le temps dépend de la taille et de la vitesse du support (comptez plusieurs minutes pour une clé USB 2.0).

### Étape 5 : test pratique de déverrouillage

1. **Éjectez proprement** la clé (zone de notification → *Retirer le périphérique en toute sécurité*).
2. **Rebranchez‑la**.
3. Dans l'Explorateur, le lecteur affiche désormais un **cadenas doré fermé** 🔒 et son contenu est inaccessible.
4. **Double‑cliquez** dessus : Windows ouvre la fenêtre *Déverrouiller le lecteur*.
5. Saisissez le **mot de passe** → **Déverrouiller**.
6. Le cadenas passe au **gris ouvert** 🔓 et le contenu apparaît.

!!! warning "La case « Déverrouiller automatiquement sur ce PC »"
    Pratique sur **votre** poste, dangereuse ailleurs : elle mémorise la clé dans le registre de la machine, et n'importe qui utilisant ce poste ouvrira la clé USB sans mot de passe. À réserver à un poste de confiance. Pour faire le ménage : `manage-bde -autounlock -clearallkeys C:`.

### Critère de validation

Sur le lecteur déverrouillé :

```powershell
"test BitLocker To Go" | Out-File E:\test.txt   # écriture
Get-Content E:\test.txt                          # lecture
Remove-Item E:\test.txt                          # nettoyage
```

!!! success "Résultat attendu"
    Le fichier se crée, se relit et se supprime sans erreur : le volume est bien monté en lecture/écriture. Vérification de l'état :

    ```console
    manage-bde -status E:
    ```
    → `État de la conversion : Complètement chiffré`, `État du verrou : Déverrouillé`, `Méthode de chiffrement : AES-CBC 128`.

    Le chiffrement est **transparent** : les applications lisent et écrivent normalement, le déchiffrement se fait à la volée en mémoire.

---

## Partie 3 — Administration en ligne de commande avec `manage-bde`

L'interface graphique convient au poste unitaire. Dès qu'il s'agit de scripter, de dépanner à distance ou de documenter un incident, `manage-bde` est l'outil de référence — il est présent sur **toutes** les installations Windows, sans rien à installer.

### Ouvrir une invite de commandes en administrateur

!!! danger "Sans élévation, rien ne fonctionne"
    `manage-bde` en mode utilisateur renvoie `ERREUR : Accès refusé` ou `FVE_E_NOT_ADMIN`. Vérifiez que le titre de la fenêtre contient bien **Administrateur**.

=== "Invite de commandes"

    ++win+x++ → **Terminal (Admin)** → onglet **Invite de commandes**.

    Ou : Démarrer → `cmd` → clic droit sur *Invite de commandes* → **Exécuter en tant qu'administrateur**.

=== "PowerShell"

    ++win+x++ → **Terminal (Admin)** (PowerShell est l'onglet par défaut).

    `manage-bde` fonctionne à l'identique dans PowerShell, qui dispose en plus de son propre module `BitLocker`.

=== "Raccourci clavier"

    ++win+r++ → tapez `cmd` → validez avec ++ctrl+shift+enter++ (élévation directe).

---

### 1. `manage-bde -status` — l'état des lieux

```console title="Consulter l'état du lecteur système"
manage-bde -status C:
```

Sans lettre de lecteur, la commande balaie **tous** les volumes de la machine — le réflexe à avoir en début de diagnostic.

```text title="Sortie type (chiffrement en cours)"
Chiffrement de lecteur BitLocker : outil de configuration version 10.0.26100
Copyright (C) 2013 Microsoft Corporation. Tous droits réservés.

Volume C: [Windows]
[Volume du système d'exploitation]

    Taille :                        237,25 Go
    Version de BitLocker :          2.0
    État de la conversion :         Chiffrement en cours
    Pourcentage chiffré :           37,4%
    Méthode de chiffrement :        XTS-AES 128
    État de la protection :         Protection désactivée
    État du verrou :                Déverrouillé
    Champ d'identification :        Inconnu
    Protecteurs de clé :
        TPM
        Mot de passe numérique
```

**Comment lire cette sortie :**

| Champ | Interprétation |
|-------|----------------|
| **État de la conversion** | Où en est l'opération : `Complètement déchiffré`, `Chiffrement en cours`, `Complètement chiffré`, `Déchiffrement en cours`. |
| **Pourcentage chiffré** | Avancement. Utile pour estimer le temps restant. |
| **Méthode de chiffrement** | `XTS-AES 128` (défaut interne), `AES-CBC 128` (mode compatible / amovible). |
| **État de la protection** | **Le champ le plus important.** `Protection activée` = les protecteurs sont réellement appliqués. `Protection désactivée` = la clé est disponible **en clair** sur le disque. |
| **État du verrou** | `Déverrouillé` = le volume est lisible maintenant. `Verrouillé` = il faut fournir un secret. |
| **Protecteurs de clé** | La liste des moyens d'ouvrir le volume : `TPM`, `Mot de passe numérique` (= la clé de récupération), `Mot de passe`, `Clé externe`, `TPM+PIN`… |

!!! question "Pourquoi « Protection désactivée » alors que le chiffrement tourne ?"
    Ce n'est **pas** une anomalie. Tant que le chiffrement n'est pas terminé, BitLocker conserve la clé accessible pour pouvoir reprendre le travail après un redémarrage. La protection ne s'arme (*clé claire* retirée) qu'à **100 %**. Attendez la fin avant de vous inquiéter.

!!! danger "Le piège de l'audit"
    `Complètement chiffré` **+** `Protection désactivée` = disque chiffré mais **ouvert à quiconque**. C'est l'état d'une protection **suspendue** (voir ci‑dessous) qu'on aurait oublié de reprendre. Sur un audit de parc, c'est exactement ce couple qu'il faut traquer.

---

### 2. `manage-bde -protectors -disable` — suspendre temporairement

```console title="Suspendre la protection sur C:"
manage-bde -protectors -disable C:
```

**Cas d'usage typique :** mise à jour du **BIOS/UEFI**, changement de configuration Secure Boot, remplacement d'un composant, déploiement d'une image ou d'un correctif qui touche au démarrage.

!!! question "Que fait exactement cette commande ?"
    Elle **ne déchiffre rien** et **ne supprime aucun protecteur**. Elle ajoute simplement une **clé en clair** (*clear key*) sur le volume, ce qui permet à Windows de démarrer sans consulter le TPM. Les nouvelles données restent chiffrées.

    Pourquoi c'est indispensable avant une mise à jour de firmware ? Parce que flasher le BIOS **modifie les mesures du TPM**. Sans suspension, le TPM refuserait de libérer la clé au redémarrage suivant et le poste réclamerait ses 48 chiffres — le fameux « l'utilisateur a mis à jour son BIOS et il est bloqué ». La suspension revient à prévenir BitLocker : *« attends‑toi à un changement, ne panique pas »*.

Contrôler le nombre de redémarrages avant reprise automatique :

```console
manage-bde -protectors -disable C: -RebootCount 3
```

| Valeur | Comportement |
|--------|--------------|
| *(omise)* | Protection reprise au **prochain** démarrage (équivaut à `1`). |
| `1` à `15` | Nombre de redémarrages avant reprise automatique. `3` couvre confortablement un flash de BIOS. |
| `0` | Suspension **indéfinie** jusqu'à un `-enable` explicite. ⚠️ |

!!! danger "`-RebootCount 0` : à manier avec précaution"
    Le poste reste chiffré mais **sans protection**, indéfiniment, même s'il est volé. À réserver aux opérations longues et supervisées — et à ne jamais laisser traîner. Le compteur automatique est un excellent filet de sécurité : privilégiez‑le.

Vérification immédiate :

```console
manage-bde -status C:
```

!!! success "Résultat attendu après suspension"
    ```
        État de la conversion :         Complètement chiffré
        État de la protection :         Protection désactivée
    ```
    Dans l'Explorateur, l'icône du lecteur affiche un **cadenas avec un point d'exclamation**. Un protecteur supplémentaire de type *clé claire* (**Clear Key**) apparaît dans `-protectors -get`.

---

### 3. `manage-bde -protectors -enable` — reprendre la protection

```console title="Réactiver la protection"
manage-bde -protectors -enable C:
```

À exécuter **immédiatement après** l'opération de maintenance. La commande retire la clé en clair et réarme l'ensemble des protecteurs (TPM, PIN, mot de passe numérique).

!!! tip "Le réflexe à prendre"
    `-disable` et `-enable` vont **par paire**, dans la même intervention. Beaucoup d'incidents de sécurité en parc viennent d'un `-disable` posé « le temps de tester » et jamais repris. Si vous scriptez une maintenance, mettez le `-enable` dans le bloc de fin, y compris en cas d'erreur.

Contrôle :

```console
manage-bde -status C: | findstr /C:"protection"
```

!!! success "Résultat attendu"
    `État de la protection : Protection activée`, et l'icône de `C:` redevient un **cadenas gris ouvert**.

---

### 4. `manage-bde -protectors -get` — extraire la clé de récupération

```console title="Lister tous les protecteurs de C:"
manage-bde -protectors -get C:
```

```text title="Sortie type"
Volume C: [Windows]
Tous les protecteurs de clé

    TPM :
      ID : {A1B2C3D4-E5F6-4789-A0B1-C2D3E4F5A6B7}
      Profil de validation PCR :
        7, 11

    Mot de passe numérique :
      ID : {8F3C1A2B-4D5E-4F60-9A7B-1C2D3E4F5A6B}
      Mot de passe :
        123456-654321-112233-445566-778899-009988-776655-443322
```

**Ce qu'il faut retenir de cette sortie :**

- `Mot de passe numérique` est le nom interne de la **clé de récupération**.
- Son **ID** commence par `8F3C1A2B` : ce sont les 8 caractères que l'écran de récupération affiche.
- `Mot de passe :` est la clé à **48 chiffres** proprement dite.

Filtrer pour n'obtenir que la clé de récupération :

```console
manage-bde -protectors -get C: -Type RecoveryPassword
```

Exporter vers un fichier — **sur un autre volume que celui concerné** :

```console
manage-bde -protectors -get C: -Type RecoveryPassword > E:\cle-recuperation-PC01.txt
```

!!! danger "Une clé de récupération est un secret de niveau maximal"
    Quiconque possède ces 48 chiffres **et** un accès physique au disque lit toutes les données. Ne la laissez pas dans `C:\temp`, ne l'envoyez pas par messagerie instantanée, ne la collez pas dans un ticket public. Destination correcte : coffre‑fort de mots de passe, AD DS / Entra ID, ou papier en armoire forte.

Sauvegarder la clé dans l'annuaire (poste joint au domaine) :

```console title="Vers Active Directory"
manage-bde -protectors -adbackup C: -id {8F3C1A2B-4D5E-4F60-9A7B-1C2D3E4F5A6B}
```

```console title="Vers Microsoft Entra ID"
manage-bde -protectors -aadbackup C: -id {8F3C1A2B-4D5E-4F60-9A7B-1C2D3E4F5A6B}
```

---

### Les équivalents PowerShell

Le module `BitLocker` renvoie des **objets** exploitables en script, là où `manage-bde` produit du texte à parser.

| Objectif | `manage-bde` | PowerShell |
|----------|--------------|------------|
| État d'un volume | `manage-bde -status C:` | `Get-BitLockerVolume -MountPoint C:` |
| Suspendre | `manage-bde -protectors -disable C: -rc 3` | `Suspend-BitLocker -MountPoint C: -RebootCount 3` |
| Reprendre | `manage-bde -protectors -enable C:` | `Resume-BitLocker -MountPoint C:` |
| Lister les protecteurs | `manage-bde -protectors -get C:` | `(Get-BitLockerVolume -MountPoint C:).KeyProtector` |
| Déverrouiller | `manage-bde -unlock E: -Password` | `Unlock-BitLocker -MountPoint E: -Password (Read-Host -AsSecureString)` |

```powershell title="Audit rapide de tous les volumes"
Get-BitLockerVolume |
    Select-Object MountPoint, VolumeStatus, ProtectionStatus, EncryptionPercentage, EncryptionMethod |
    Format-Table -AutoSize
```

```powershell title="Extraire uniquement les clés de récupération"
Get-BitLockerVolume | ForEach-Object {
    $_.KeyProtector |
        Where-Object KeyProtectorType -eq 'RecoveryPassword' |
        Select-Object @{n='Lecteur';e={$_.MountPoint}}, KeyProtectorId, RecoveryPassword
}
```

---

## Partie 4 — Scénario helpdesk : débloquer un utilisateur sur l'écran de récupération

### Mise en situation

> *Lundi matin, 8 h 42. Un utilisateur appelle : « Mon PC ne démarre plus, il y a un écran bleu qui me demande une clé de récupération. Je n'ai jamais vu ça. »*

Le poste s'est arrêté **avant** Windows, sur l'écran **Récupération BitLocker**. Il affiche un pavé de texte, un champ de saisie, et un **ID de la clé de récupération**.

!!! note "Bleu ou noir ?"
    Historiquement bleu, cet écran peut apparaître **noir** selon la version de Windows 11 et la charte de l'OEM. Le contenu, lui, ne change pas : titre *Récupération BitLocker*, ID de clé, champ de saisie. Ce n'est **pas** un écran bleu d'erreur (BSOD) : la machine n'a pas planté, elle demande une autorisation.

### Comprendre la cause avant de raccrocher

BitLocker ne réclame la clé de récupération que si l'état de démarrage a changé. Les causes fréquentes :

| Cause | Fréquence | Indice à demander à l'utilisateur |
|-------|-----------|-----------------------------------|
| Mise à jour du **BIOS/UEFI** sans suspension préalable | ⭐⭐⭐ | « Une fenêtre de mise à jour Dell/HP/Lenovo hier ? » |
| **Secure Boot** désactivé ou ordre de démarrage modifié | ⭐⭐⭐ | « Vous êtes allé dans le BIOS ? Branché une clé USB bootable ? » |
| **Périphérique** ajouté/retiré (station d'accueil, carte, disque) | ⭐⭐ | « Un nouveau matériel branché ? » |
| Mise à jour Windows touchant au démarrage | ⭐⭐ | « Le PC a redémarré tout seul cette nuit ? » |
| **TPM réinitialisé** ou pile CMOS morte | ⭐ | « L'heure du PC est‑elle correcte ? » |
| Disque déplacé dans une **autre machine** | ⭐ | À croiser avec l'inventaire — ou avec un vol |

!!! warning "Un doute légitime avant de donner la clé"
    Si le contexte ne colle pas (poste déclaré volé, appel d'un numéro inconnu, utilisateur qui ne sait pas dire ce qui a changé), **vérifiez l'identité de l'appelant** avant de communiquer 48 chiffres. Une clé de récupération dictée au téléphone à la mauvaise personne annule tout le bénéfice du chiffrement.

---

### Procédure de support niveau 1

#### Étape 1 : faire lire l'ID de la clé de récupération

L'écran affiche une ligne du type :

```text
ID de la clé de récupération : 8F3C1A2B
```

Formulation à utiliser au téléphone :

> *« Sur l'écran, cherchez la ligne "ID de la clé de récupération". Lisez‑moi les 8 caractères, lettre par lettre — dites‑moi "B comme Bernard" pour les lettres, s'il vous plaît. »*

!!! tip "Astuce terrain"
    Demandez plutôt une **photo de l'écran** envoyée par SMS ou messagerie. C'est plus rapide et cela élimine les erreurs de lecture entre `0`/`O`, `1`/`I`, `B`/`8`. Certaines versions récentes affichent aussi un **QR code** pointant vers la page d'aide Microsoft.

!!! danger "Ne cherchez pas à saisir cet ID"
    Encore une fois : l'ID **n'ouvre rien**. C'est une référence de catalogue, pas un secret.

#### Étape 2 : retrouver la clé correspondante

Cherchez, dans l'ordre de ce dont vous disposez :

=== "Fichier / document de sauvegarde"

    Les fichiers exportés s'appellent `Clé de récupération BitLocker <ID>.txt`. Cherchez `8F3C1A2B` dans le nom **ou** dans le contenu :

    ```powershell
    Select-String -Path "\\serveur\cles-bitlocker\*.txt" -Pattern "8F3C1A2B" -Context 0,4
    ```

    Contrôlez que le bloc `Identificateur :` commence bien par les 8 caractères lus par l'utilisateur.

=== "Active Directory"

    *Utilisateurs et ordinateurs Active Directory* → activez *Fonctionnalités avancées* → propriétés de l'objet ordinateur → onglet **Récupération BitLocker**.

    Ou en PowerShell :

    ```powershell
    Get-ADObject -Filter "objectClass -eq 'msFVE-RecoveryInformation'" `
        -SearchBase (Get-ADComputer PC01).DistinguishedName `
        -Properties msFVE-RecoveryPassword, Name
    ```

=== "Intune / Entra ID"

    *Microsoft Intune* → *Appareils* → sélectionner le poste → **Clés de récupération**.

    Côté portail utilisateur : `https://myaccount.microsoft.com/device-list`.

=== "Compte Microsoft (poste personnel)"

    Depuis un autre appareil : `https://aka.ms/myrecoverykey`. Les clés y sont listées **avec leur ID** — d'où l'intérêt de l'étape 1.

!!! failure "Aucune clé ne correspond"
    Si l'ID affiché n'existe nulle part, la clé n'a **jamais** été sauvegardée (chiffrement activé manuellement sans dépôt, ou hors périmètre de gestion). Il n'existe alors **aucune solution technique** : les données sont perdues. La seule issue est la réinstallation du poste après effacement. Faites remonter l'incident — c'est un défaut de procédure, pas un défaut de l'utilisateur.

#### Étape 3 : guider la saisie au clavier

C'est ici que le support de niveau 1 gagne (ou perd) dix minutes.

!!! warning "Les quatre pièges classiques du clavier en pré‑démarrage"
    1. **Le pavé numérique ne répond pas.** L'environnement de pré‑démarrage n'active pas toujours le **Verr. Num.** Faites appuyer sur ++num-lock++ (le voyant doit s'allumer) ou, plus sûr, faites utiliser la **rangée de chiffres au‑dessus des lettres**.
    2. **Sur certains firmwares, seules les touches ++f1++ à ++f10++ fonctionnent** : ++f1++ à ++f9++ pour les chiffres `1` à `9`, et ++f10++ pour le `0`. C'est un vestige des claviers pré‑boot ; à tenter si aucune touche numérique ne donne rien.
    3. **Ne pas taper les tirets.** La clé est composée **uniquement de chiffres**. Le curseur saute automatiquement au bloc suivant tous les 6 chiffres.
    4. **La disposition du clavier est souvent QWERTY/US**, mais comme la clé ne contient que des chiffres, cela n'a d'impact que sur la rangée du haut d'un clavier AZERTY — d'où l'intérêt du pavé numérique une fois ++num-lock++ activé.

    Dictée : annoncez **par blocs de 6 chiffres**, en marquant une pause entre chaque bloc, et faites relire le bloc avant de passer au suivant.

Une fois les 48 chiffres saisis : ++enter++.

#### Étape 4 : déverrouillage et retour au bureau

Le poste poursuit son démarrage et arrive à l'écran d'ouverture de session Windows. L'utilisateur saisit son mot de passe de session **habituel** — celui‑ci n'a jamais changé.

!!! success "Critère de réussite"
    Retour au bureau Windows. Contrôle final en invite de commandes administrateur :

    ```console
    manage-bde -status C:
    ```
    → `État de la protection : Protection activée` et `État du verrou : Déverrouillé`. Le poste est protégé **et** utilisable.

#### Étape 5 : ne pas s'arrêter là

Un déblocage n'est pas une résolution : si la cause persiste, l'écran reviendra au prochain démarrage.

- [ ] **Identifier la cause racine** (journal *Observateur d'événements* → `Journaux des applications et des services` → `Microsoft` → `Windows` → `BitLocker-API` → **Management**).
- [ ] **Terminer proprement l'opération** qui a déclenché la récupération (finir le flash BIOS, réactiver Secure Boot, remettre l'ordre de démarrage d'origine).
- [ ] **Vérifier que la clé est bien sauvegardée** et, si ce n'était pas le cas, la déposer dans le coffre : `manage-bde -protectors -adbackup C: -id {…}`.
- [ ] **Régénérer une clé de récupération** si les 48 chiffres ont été dictés par téléphone ou transmis par un canal non maîtrisé :

    ```console
    manage-bde -protectors -delete C: -type RecoveryPassword
    manage-bde -protectors -add C: -RecoveryPassword
    manage-bde -protectors -get C: -type RecoveryPassword
    ```

    !!! danger "Ordre impératif"
        Générez et **notez** la nouvelle clé avant de considérer l'ancienne comme périmée. Ne supprimez jamais **tous** les protecteurs d'un volume : à la suppression du dernier, BitLocker se désactive et le volume se déchiffre intégralement.

- [ ] **Documenter le ticket** avec l'ID de clé (jamais la clé elle‑même) et la cause identifiée.

---

## Vérification globale

Checklist de fin d'atelier :

- [x] `C:` chiffré : `manage-bde -status C:` → `Complètement chiffré` + `Protection activée`.
- [x] Clé de récupération de `C:` sauvegardée **hors du disque** et retrouvable par son ID.
- [x] Clé USB chiffrée avec BitLocker To Go, cadenas doré fermé après reconnexion.
- [x] Déverrouillage de la clé USB par mot de passe, lecture **et** écriture validées.
- [x] Cycle `-protectors -disable` → `-enable` maîtrisé, avec contrôle de l'état à chaque étape.
- [x] Extraction de l'ID et du mot de passe de récupération avec `-protectors -get`.
- [x] Correspondance comprise entre les **8 caractères** de l'écran de récupération et l'`Identificateur` du fichier de sauvegarde.

---

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `manage-bde -status` | État de **tous** les volumes |
| `manage-bde -status C:` | État d'un volume précis |
| `manage-bde -on C: -RecoveryPassword` | Activer BitLocker + générer une clé de récupération |
| `manage-bde -on E: -Password` | Activer BitLocker To Go avec mot de passe |
| `manage-bde -off C:` | **Déchiffrer** le volume et désactiver BitLocker (long) |
| `manage-bde -pause C:` / `-resume C:` | Mettre en pause / reprendre la **conversion** en cours |
| `manage-bde -protectors -get C:` | Lister tous les protecteurs (ID + clé de récupération) |
| `manage-bde -protectors -get C: -Type RecoveryPassword` | N'afficher que la clé de récupération |
| `manage-bde -protectors -disable C: -rc 3` | **Suspendre** la protection pour 3 redémarrages |
| `manage-bde -protectors -enable C:` | **Reprendre** la protection |
| `manage-bde -protectors -add C: -RecoveryPassword` | Ajouter une nouvelle clé de récupération |
| `manage-bde -protectors -add C: -TPMAndPIN` | Exiger un PIN au démarrage (en plus du TPM) |
| `manage-bde -protectors -adbackup C: -id {GUID}` | Sauvegarder la clé dans Active Directory |
| `manage-bde -unlock E: -RecoveryPassword <48 chiffres>` | Déverrouiller avec la clé de récupération |
| `manage-bde -unlock E: -Password` | Déverrouiller par mot de passe (saisie interactive) |
| `manage-bde -lock E:` | Reverrouiller un volume de données |
| `manage-bde -autounlock -clearallkeys C:` | Supprimer les déverrouillages automatiques mémorisés |
| `manage-bde -changepin C:` | Modifier le PIN de démarrage |
| `repair-bde <source> <cible> -rp <48 chiffres>` | Récupérer les données d'un volume endommagé |
| `tpm.msc` / `Get-Tpm` | État du module TPM |

---

## Erreurs courantes

!!! failure "`ERREUR : Accès refusé` (FVE_E_NOT_ADMIN)"
    L'invite de commandes n'est pas élevée. Relancez‑la via ++win+x++ → *Terminal (Admin)*.

!!! failure "`Ce périphérique ne peut pas utiliser un module de plateforme sécurisée`"
    Pas de TPM détecté, ou TPM désactivé dans l'UEFI. Vérifiez avec `tpm.msc`, activez *Intel PTT* / *AMD fTPM* dans le firmware, ou appliquez la stratégie *Autoriser BitLocker sans un TPM compatible* (voir Prérequis).

!!! failure "L'assistant refuse d'enregistrer la clé à l'emplacement choisi"
    Vous tentez de la sauvegarder **sur le volume en cours de chiffrement**. C'est un garde‑fou, pas un bug : choisissez un autre support.

!!! failure "Le lecteur est utilisé par un autre programme"
    Fermez toutes les fenêtres de l'Explorateur, les fichiers ouverts et les antivirus qui scannent le support, puis relancez. Sur une clé USB, un `chkdsk E: /f` préalable règle souvent le problème.

!!! failure "Le poste demande la clé de récupération à chaque démarrage"
    La suspension n'a pas été reprise, ou la cause racine persiste (Secure Boot instable, firmware à jour non appliqué). Déverrouillez, puis :

    ```console
    manage-bde -protectors -disable C: -rc 1
    shutdown /r /t 0
    ```
    Après le redémarrage, la protection se réarme sur les **nouvelles** mesures du TPM. Consultez le journal `BitLocker-API/Management` pour identifier le PCR fautif.

!!! failure "Windows Famille : impossible de créer une clé USB BitLocker To Go"
    L'édition Famille peut **lire et écrire** sur un support chiffré (après déverrouillage) mais **ne peut pas en créer**. Effectuez le chiffrement depuis un poste Pro.

---

## Glossaire

BitLocker
:   Fonctionnalité de chiffrement de volume intégrée à Windows (éditions Pro, Entreprise, Éducation). Elle chiffre le volume entier, de façon transparente pour les applications.

BitLocker To Go
:   Déclinaison de BitLocker pour les **supports amovibles** (clés USB, disques externes). Le déverrouillage repose sur un mot de passe ou une carte à puce, puisqu'aucun TPM n'est disponible en face.

TPM
:   *Trusted Platform Module* — coprocesseur sécurisé qui **scelle** la clé de chiffrement et ne la libère que si l'état de démarrage mesuré correspond à l'état enregistré. Version 2.0 requise par Windows 11.

PCR
:   *Platform Configuration Register* — registre du TPM contenant l'empreinte d'un aspect du démarrage. BitLocker s'appuie par défaut sur les PCR 7 (état Secure Boot) et 11 (état BitLocker).

Protecteur de clé
:   Mécanisme autorisé à déverrouiller le volume : `TPM`, `TPM+PIN`, `Mot de passe`, `Clé externe` (fichier `.bek` sur USB), `Mot de passe numérique` (clé de récupération). Un volume en possède généralement plusieurs.

Mot de passe numérique
:   Nom interne de la **clé de récupération** à 48 chiffres dans les sorties de `manage-bde`.

Clé de récupération
:   Secret de secours de **48 chiffres** (8 blocs de 6), généré à l'activation du chiffrement et associé à un **identificateur** public. Dernier recours quand le déverrouillage normal échoue.

ID de la clé de récupération
:   GUID **non secret** identifiant une clé de récupération. Ses 8 premiers caractères s'affichent sur l'écran de récupération pour retrouver la bonne clé dans un coffre.

Clé claire (*clear key*)
:   Protecteur temporaire ajouté lors d'une **suspension** : la clé de chiffrement est stockée en clair sur le volume, ce qui permet de démarrer sans consulter le TPM. Retirée par `-protectors -enable`.

XTS‑AES
:   Mode de chiffrement par blocs conçu pour le stockage, utilisé par défaut par BitLocker depuis Windows 10 1511 sur les disques internes. AES‑CBC reste employé en *mode compatible* pour les supports amovibles.

Chiffrement au repos
:   Protection des données **stockées** sur un support, par opposition au chiffrement en transit (TLS, VPN).

*[TPM]: Trusted Platform Module
*[PCR]: Platform Configuration Register
*[UEFI]: Unified Extensible Firmware Interface
*[AES]: Advanced Encryption Standard
*[XTS]: XEX-based Tweaked codebook mode with ciphertext Stealing
*[GUID]: Globally Unique Identifier
*[AD DS]: Active Directory Domain Services
*[GPO]: Group Policy Object
*[L1]: Support de niveau 1

---

## Ressources

- [BitLocker — documentation Microsoft Learn](https://learn.microsoft.com/fr-fr/windows/security/operating-system-security/data-protection/bitlocker/) — référence officielle (architecture, stratégies, déploiement).
- [Référence de la commande `manage-bde`](https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/manage-bde) — syntaxe complète de tous les sous‑ensembles.
- [`manage-bde protectors`](https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/manage-bde-protectors) — détail de `-get`, `-add`, `-disable`, `-enable`, `-adbackup`.
- [Guide de récupération BitLocker](https://learn.microsoft.com/fr-fr/windows/security/operating-system-security/data-protection/bitlocker/recovery-overview) — causes de passage en récupération et procédures de déblocage.
- [Module PowerShell BitLocker](https://learn.microsoft.com/fr-fr/powershell/module/bitlocker/) — cmdlets `Get-BitLockerVolume`, `Suspend-BitLocker`, `Unlock-BitLocker`…
- [Retrouver sa clé de récupération (compte Microsoft)](https://aka.ms/myrecoverykey) — portail à donner à un utilisateur en poste personnel.
- [Recommandations de l'ANSSI](https://cyber.gouv.fr/) — bonnes pratiques de chiffrement des postes nomades.
- Article connexe du wiki : [Sécuriser un volume de données avec le chiffrement LUKS sous Linux](securiser-volume-donnees-chiffrement-luks-linux.md) — l'équivalent côté Linux.
- Article connexe du wiki : [Déverrouiller automatiquement LUKS au démarrage avec le TPM2 et Clevis](dechiffrer-automatiquement-luks-tpm2-clevis-secure-boot-ubuntu.md) — le même rôle du TPM, vu depuis Ubuntu.
