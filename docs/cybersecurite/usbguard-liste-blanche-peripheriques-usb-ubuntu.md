---
title: Contrôler les périphériques USB avec USBGuard sur Ubuntu (liste blanche anti-BadUSB)
date: 2026-09-06
author: Nicolas BODAINE
tags:
  - usbguard
  - usb
  - durcissement
  - badusb
  - securite
  - ubuntu
  - linux
difficulty: intermédiaire
os: Ubuntu 24.04 LTS (Desktop & Server)
status: publié
---

# Contrôler les périphériques USB avec USBGuard sur Ubuntu (liste blanche anti-BadUSB)

!!! abstract "Résumé"
    USBGuard applique une politique d'autorisation sur le bus USB : seuls les périphériques explicitement listés dans la politique peuvent dialoguer avec le noyau, tous les autres sont bloqués à chaud. Cette note couvre l'installation sur Ubuntu, la génération d'une liste blanche à partir du matériel de confiance, l'ouverture des droits IPC, la gestion quotidienne des nouveaux périphériques — et surtout la façon d'éviter (ou de réparer) le classique verrouillage clavier/souris qui piège la majorité des premières installations.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 LTS (paquet `usbguard` 1.1.2) |
| Privilèges requis | `root` / `sudo` |
| Durée estimée | 20 à 30 minutes |
| Dernière mise à jour | 2026-09-06 |

---

## Contexte

Le bus USB a été conçu pour la commodité, pas pour la sécurité : par défaut, **tout périphérique branché est immédiatement énuméré, pilote chargé, et considéré comme légitime**. C'est exactement ce qu'exploite la classe d'attaques dite **BadUSB** : un objet qui ressemble à une clé de stockage annonce au système qu'il est en réalité un **clavier** (classe HID), puis « tape » à 1 000 caractères par minute un script qui ouvre un shell inversé. Les variantes commerciales de ce type d'outil (Rubber Ducky, O.MG Cable, Bash Bunny) coûtent quelques dizaines d'euros et fonctionnent sur un poste déverrouillé en moins de trois secondes.

USBGuard répond à ce problème en s'appuyant sur un mécanisme peu connu du noyau Linux : chaque périphérique USB expose dans `sysfs` un attribut `authorized` (`/sys/bus/usb/devices/*/authorized`). Tant qu'il vaut `0`, le noyau énumère bien le périphérique mais **ne lie aucun pilote** : le matériel est électriquement présent mais fonctionnellement inerte.

Le démon `usbguard-daemon` se place au-dessus de ce mécanisme et automatise la décision :

1. Il écoute les événements `uevent` du noyau (branchement, débranchement).
2. Il compare le périphérique aux règles de sa politique (`/etc/usbguard/rules.conf`), dans l'ordre, **première règle correspondante gagnante**.
3. Si aucune règle ne correspond, il applique la cible implicite `ImplicitPolicyTarget`, qui vaut `block` par défaut.

C'est une approche **liste blanche** (allow-list) : ce qui n'est pas explicitement autorisé est refusé. Elle est très efficace, mais elle a une conséquence directe qu'il faut avoir en tête avant de taper la première commande : **si le démon démarre avec une politique vide, votre clavier et votre souris USB sont bloqués eux aussi**.

!!! danger "Le piège n°1 : se verrouiller hors de sa propre machine"
    Sur Debian et Ubuntu, le paquet `usbguard` **active et démarre le service dès la fin de l'installation `apt`**, avec un fichier `rules.conf` vide. Sur un poste fixe équipé d'un clavier et d'une souris USB, l'écran devient inerte dans la seconde qui suit, avant même que vous ayez pu générer la moindre règle. La procédure ci-dessous neutralise ce comportement **avant** d'installer le paquet. Si vous êtes déjà tombé dans le piège, sautez directement à [Problèmes fréquents](#probleme-1-plus-de-clavier-ni-de-souris-apres-linstallation).

!!! info "USBGuard n'est pas un antivirus"
    USBGuard décide *quel matériel* a le droit de parler au noyau. Il ne lit pas le contenu des clés USB et ne détecte aucun malware dans les fichiers. Il se combine donc utilement avec le chiffrement des supports, une politique de montage `noexec,nosuid,nodev` et un antivirus si le poste échange des fichiers avec l'extérieur.

---

## Prérequis

- Un poste ou serveur sous **Ubuntu 24.04 LTS** (la procédure vaut aussi pour Debian 12/13 et les dérivés).
- Un compte disposant des droits `sudo`.
- **Tous les périphériques USB indispensables branchés** avant de commencer : clavier, souris, dongle sans fil, hub, webcam externe, casque, clé de sécurité FIDO2, lecteur d'empreintes… La liste blanche initiale est une photographie de ce qui est branché à l'instant `t`.
- Fortement recommandé : **un second canal d'accès** (session SSH ouverte depuis une autre machine, ou console d'hyperviseur/IPMI). C'est votre filet de sécurité si le clavier local est bloqué.
- Un ordinateur portable dont le clavier interne est en PS/2 émulé (`i8042`) est nettement plus indulgent qu'un poste fixe : il continuera à fonctionner même en cas d'erreur de politique.

!!! warning "Cas particulier : serveur distant"
    Sur un serveur administré uniquement en SSH, le risque de verrouillage clavier est nul, **mais** attention aux adaptateurs réseau USB, aux dongles KVM-over-IP et aux clés de licence : s'ils ne figurent pas dans la liste blanche, vous perdez respectivement le réseau, la console et l'application. Vérifiez la sortie de `lsusb` avant de démarrer le démon.

---

## Procédure

### Étape 1 : Neutraliser le démarrage automatique du service

On masque les unités systemd **avant** l'installation. `systemctl mask` crée un lien symbolique vers `/dev/null` dans `/etc/systemd/system/`, ce qui rend l'unité impossible à démarrer — y compris par les scripts post-installation du paquet.

```bash
sudo systemctl mask usbguard.service usbguard-dbus.service
```

!!! note "Pourquoi masquer et non désactiver ?"
    `systemctl disable` empêche seulement le démarrage **au boot** ; le script `postinst` du paquet, lui, lance le service immédiatement via `deb-systemd-invoke`. Seul `mask` bloque les deux cas. On peut d'ailleurs masquer une unité qui n'existe pas encore : le lien est créé et sera pris en compte dès l'apparition du fichier de service.

*Vérification :* la commande doit afficher deux lignes `Created symlink …`. Aucune erreur n'est attendue même si le paquet n'est pas encore installé.

---

### Étape 2 : Installer le paquet

```bash
sudo apt update && sudo apt install usbguard
```

Le paquet `usbguard` d'Ubuntu 24.04 fournit la version **1.1.2**. Il installe le démon, l'outil en ligne de commande `usbguard`, les unités systemd et une configuration par défaut dans `/etc/usbguard/`.

*Vérification :*

```bash
usbguard --version
systemctl is-enabled usbguard.service   # doit répondre : masked
systemctl is-active usbguard.service    # doit répondre : inactive
```

!!! success "Résultat attendu"
    Le numéro de version s'affiche (`usbguard 1.1.2`), le service est bien `masked` et `inactive`, et **tous vos périphériques USB fonctionnent toujours normalement**.

---

### Étape 3 : Générer la politique initiale

`usbguard generate-policy` inspecte le matériel actuellement branché et produit une règle `allow` par périphérique. Deux approches, selon le niveau de rigueur souhaité :

=== "Méthode recommandée (avec relecture)"

    ```bash
    # 1. Générer dans un fichier temporaire, sans écraser quoi que ce soit
    sudo usbguard generate-policy > /tmp/rules.conf

    # 2. Relire et corriger le contenu
    sudo nano /tmp/rules.conf

    # 3. Installer avec les bons droits et le bon propriétaire
    sudo install -m 0600 -o root -g root /tmp/rules.conf /etc/usbguard/rules.conf
    ```

=== "Méthode rapide (une ligne)"

    ```bash
    sudo usbguard generate-policy | sudo tee /etc/usbguard/rules.conf
    ```

    !!! warning "Contrôlez les permissions"
        `tee` conserve les droits d'un fichier existant, mais crée un fichier en `0644` s'il n'existe pas. Or `rules.conf` contient les numéros de série de votre matériel : il doit rester illisible par les utilisateurs ordinaires.
        ```bash
        sudo chmod 0600 /etc/usbguard/rules.conf
        sudo chown root:root /etc/usbguard/rules.conf
        ```

*Vérification :*

```bash
sudo cat /etc/usbguard/rules.conf
stat -c '%A %U:%G %n' /etc/usbguard/rules.conf   # attendu : -rw------- root:root
```

Vous devez retrouver vos contrôleurs USB (`xHCI Host Controller`), votre clavier, votre souris, la webcam et le Bluetooth internes (qui sont, eux aussi, des périphériques USB sur la quasi-totalité des portables).

#### Lire une règle USBGuard

Une ligne générée ressemble à ceci :

```text title="/etc/usbguard/rules.conf"
allow id 046d:c52b serial "" name "USB Receiver" hash "jEP/6WzviqdJ5VSeTUY8Pat…" parent-hash "kv0Xb…" with-interface { 03:01:01 03:01:02 03:00:00 }
```

| Élément | Signification |
|---------|---------------|
| `allow` | **Cible** de la règle : `allow` (autoriser), `block` (refuser l'autorisation) ou `reject` (retirer logiquement le périphérique du système). |
| `id 046d:c52b` | Identifiants **VID:PID** — constructeur (`046d` = Logitech) et modèle. Facilement falsifiables par un attaquant. |
| `serial ""` | Numéro de série déclaré. Vide sur beaucoup de matériels bas de gamme. |
| `name "…"` | Nom déclaré par le périphérique. Purement informatif, falsifiable également. |
| `hash "…"` | Empreinte calculée par USBGuard à partir de l'ensemble des descripteurs. Bien plus difficile à usurper qu'un simple VID:PID. |
| `parent-hash "…"` | Empreinte du port/hub parent : elle attache le périphérique à un emplacement physique de l'arborescence USB. |
| `with-interface { … }` | Classes d'interface annoncées, au format `classe:sous-classe:protocole`. C'est **le champ le plus intéressant en sécurité**. |

!!! tip "Les classes d'interface, le cœur de la défense anti-BadUSB"
    Quelques classes à connaître : `03` = HID (clavier, souris), `08` = stockage de masse, `09` = hub, `0e` = vidéo (webcam), `e0` = sans fil (Bluetooth), `ff` = spécifique constructeur.
    Une clé USB piégée se trahit en annonçant à la fois `08` (stockage) et `03:00:01` (clavier). On peut donc écrire une règle explicite :
    ```text
    reject with-interface all-of { 08:*:* 03:00:* }
    ```
    Ajoutée **avant** les règles `allow`, elle refuse tout périphérique qui prétend être simultanément une clé et un clavier.

!!! question "Faut-il conserver les `hash` ?"
    Le hash est l'attribut le plus robuste, mais il change si le firmware du périphérique est mis à jour ou si le noyau modifie sa façon d'exposer les descripteurs — la règle cesse alors de correspondre et le matériel se retrouve bloqué sans raison apparente. Pour un parc de postes ou pour du matériel amené à être mis à jour, on préfère souvent générer sans hash puis ajouter le numéro de série :
    ```bash
    sudo usbguard generate-policy --no-hashes > /tmp/rules.conf
    ```

---

### Étape 4 : Accorder les droits d'administration via l'IPC

Le démon expose une interface **IPC** (Inter-Process Communication) qui permet à l'outil `usbguard` de lui parler sans être `root` à chaque branchement. Depuis la version 0.7, la bonne méthode consiste à créer un **fichier de contrôle d'accès** dans `/etc/usbguard/IPCAccessControl.d/` — les anciennes directives `IPCAllowedUsers` et `IPCAllowedGroups` de `usbguard-daemon.conf` sont considérées comme héritées et ne sont plus la voie recommandée.

```bash
sudo usbguard add-user --group sudo --devices ALL --policy modify,list --exceptions listen
```

Décomposition des options :

| Option | Effet |
|--------|-------|
| `--group sudo` | La cible est le **groupe** `sudo` (et non un utilisateur). Sans `-g`/`--group`, le nom serait interprété comme un identifiant utilisateur. |
| `--devices ALL` | Toutes les permissions sur les périphériques : `list` (les lister), `modify` (changer leur état d'autorisation), `listen` (recevoir les événements). |
| `--policy modify,list` | Droit de lire **et de modifier** la politique. `modify` est indispensable pour que l'option `-p` (règle permanente) fonctionne. |
| `--exceptions listen` | Réception des messages d'exception du démon. |

!!! warning "Un droit `sudo` élargi"
    Donner ces privilèges au groupe `sudo` est pratique sur un poste personnel, car les membres de ce groupe peuvent déjà devenir `root`. Sur un serveur multi-utilisateurs, préférez un groupe dédié et n'y placez que les comptes concernés :
    ```bash
    sudo groupadd --system usbguard
    sudo usermod -aG usbguard "$USER"
    sudo usbguard add-user --group usbguard --devices ALL --policy modify,list --exceptions listen
    ```
    L'appartenance à un nouveau groupe n'est effective qu'après une reconnexion complète de la session.

*Vérification :* la commande crée un fichier dont le nom est celui du groupe **préfixé par deux-points** :

```bash
sudo ls -l /etc/usbguard/IPCAccessControl.d/
sudo cat /etc/usbguard/IPCAccessControl.d/:sudo
```

!!! success "Résultat attendu"
    ```text
    Devices=modify list listen
    Policy=modify list
    Exceptions=listen
    ```
    Toute modification apportée par `add-user` ou `remove-user` **n'est prise en compte qu'après un (re)démarrage du démon** — ce qui tombe bien, il n'est pas encore lancé.

---

### Étape 5 : Démarrer le démon

La politique est en place et les droits IPC sont configurés : on peut lever le masquage et activer le service.

```bash
sudo systemctl unmask usbguard.service
sudo systemctl enable --now usbguard.service
```

*Vérification :*

```bash
systemctl status usbguard.service
usbguard list-devices
```

!!! success "Résultat attendu"
    Le service est `active (running)`. La sortie de `list-devices` affiche vos périphériques avec la mention `allow`. Le clavier, la souris et le pointeur continuent de répondre. Notez que `usbguard list-devices` fonctionne désormais **sans `sudo`** : c'est la preuve que les droits IPC de l'étape 4 sont opérationnels.

!!! tip "Test de non-régression, sans risque"
    Débranchez puis rebranchez votre souris : elle doit repartir instantanément (elle est dans la liste blanche). Branchez ensuite une clé USB inconnue : elle ne doit **pas** apparaître dans le gestionnaire de fichiers, et `usbguard list-devices` doit la montrer en `block`.

---

### Étape 6 : Autoriser un nouveau périphérique au quotidien

Tout périphérique absent de la liste blanche reste inerte. Pour l'admettre :

**1. Identifier son numéro de périphérique interne**

```bash
usbguard list-devices --blocked
```

```text
16: block id 0951:1666 serial "60A44C..." name "DataTraveler 3.0" hash "…" with-interface { 08:06:50 }
```

Le premier nombre (`16` ici) est **l'identifiant interne du périphérique** attribué par le démon — à ne pas confondre ni avec le VID:PID `0951:1666`, ni avec un identifiant de règle (ceux de `usbguard list-rules`, utilisés avec `append-rule`/`remove-rule`). Il change à chaque rebranchement.

**2. Autoriser le périphérique**

=== "Autorisation temporaire (session en cours)"

    ```bash
    usbguard allow-device 16
    ```

    L'autorisation disparaît au redémarrage du démon. C'est le bon choix pour une clé de passage appartenant à un tiers.

=== "Autorisation permanente"

    ```bash
    usbguard allow-device 16 -p
    ```

    Le drapeau `-p` / `--permanent` ajoute une règle `allow` spécifique à `/etc/usbguard/rules.conf`. Le périphérique sera reconnu après chaque redémarrage.

!!! warning "Piège de syntaxe : le sens de `-p` change selon la sous-commande"
    Avec `allow-device`, `block-device` et `reject-device`, `-p` signifie `--permanent`.
    Avec `generate-policy`, `-p` signifie `--with-ports` (générer des règles liées au port physique). Deux options homonymes, deux effets sans rapport.

*Vérification :*

```bash
usbguard list-devices | grep -i datatraveler
sudo grep -c '^allow' /etc/usbguard/rules.conf   # le compteur augmente si -p a été utilisé
```

Le périphérique doit être passé en `allow` et devenir accessible dans le système (montage automatique, `lsblk`, etc.).

!!! tip "Voir les événements en direct"
    Dans un terminal laissé ouvert, `usbguard watch` affiche en temps réel les branchements, les blocages et les modifications de politique. Très pratique pendant la phase de mise au point.

---

### Étape 7 (optionnel) : Notifications sur le bureau

En environnement graphique, être bloqué sans le moindre message est déroutant. Deux compléments existent :

**a. `usbguard-notifier`** — une petite fenêtre surgissante à chaque branchement ou blocage :

```bash
sudo apt install usbguard-notifier
systemctl enable --now --user usbguard-notifier.service
```

Ce service a besoin, au minimum, du privilège IPC `Devices=listen` pour votre compte — déjà couvert par l'étape 4 si vous appartenez au groupe visé.

**b. L'intégration native de GNOME** — GNOME sait piloter USBGuard via D-Bus pour rejeter les périphériques branchés **pendant que la session est verrouillée** (scénario classique de l'attaque « evil maid ») :

```bash
sudo systemctl unmask usbguard-dbus.service
sudo systemctl enable --now usbguard-dbus.service

gsettings set org.gnome.desktop.privacy usb-protection true
gsettings set org.gnome.desktop.privacy usb-protection-level lockscreen   # ou 'always'
```

---

## Vérification

Récapitulatif des contrôles à effectuer une fois l'ensemble en place :

```bash
# 1. Le service tourne et démarrera au boot
systemctl is-active usbguard.service && systemctl is-enabled usbguard.service

# 2. La politique est chargée et non vide
usbguard list-rules | head

# 3. Les paramètres de sécurité par défaut sont bien appliqués
usbguard get-parameter ImplicitPolicyTarget    # attendu : block
usbguard get-parameter InsertedDevicePolicy    # attendu : apply-policy

# 4. Les journaux ne contiennent pas d'erreur de chargement
journalctl -u usbguard.service -b --no-pager | tail -n 20
```

!!! success "Résultat attendu"
    `active` + `enabled`, une liste de règles numérotées, les deux paramètres aux valeurs ci-dessus, et un journal se terminant par le chargement de la politique sans message `error`.

**Test final, celui qui compte :** redémarrez la machine. Après le retour de l'écran de connexion, le clavier et la souris doivent fonctionner immédiatement. C'est le seul moyen de valider que `PresentDevicePolicy=apply-policy` retrouve bien votre matériel au démarrage.

---

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `usbguard list-devices` | Lister tous les périphériques reconnus et leur état |
| `usbguard list-devices -b` | Ne lister que les périphériques bloqués |
| `usbguard list-devices -t` | Affichage en arborescence (utile pour repérer les hubs) |
| `usbguard allow-device <ID> -p` | Autoriser un périphérique de façon permanente |
| `usbguard block-device <ID> -p` | Bloquer un périphérique de façon permanente |
| `usbguard reject-device <ID>` | Retirer logiquement le périphérique du système |
| `usbguard list-rules` | Afficher la politique en vigueur, avec les identifiants de règle |
| `usbguard list-rules -d` | Afficher la politique et les périphériques concernés par chaque règle |
| `usbguard append-rule '<règle>'` | Ajouter une règle à la fin de la politique |
| `usbguard remove-rule <ID>` | Supprimer une règle par son identifiant |
| `usbguard generate-policy` | Générer une politique à partir du matériel branché |
| `usbguard generate-policy --no-hashes` | Générer une politique sans empreintes (plus tolérante) |
| `usbguard watch` | Suivre les événements USB en temps réel |
| `usbguard add-user <nom> …` | Créer un fichier de contrôle d'accès IPC |
| `usbguard remove-user <nom>` | Supprimer un fichier de contrôle d'accès IPC |
| `usbguard get-parameter <nom>` | Lire un paramètre à chaud (`ImplicitPolicyTarget`, `InsertedDevicePolicy`) |
| `usbguard set-parameter <nom> <valeur>` | Modifier un paramètre à chaud (non persistant) |
| `lsusb -t` | Vue noyau de l'arborescence USB, indépendante d'USBGuard |

### Fichiers importants

| Chemin | Rôle |
|--------|------|
| `/etc/usbguard/usbguard-daemon.conf` | Configuration du démon (cibles implicites, chemins, audit) |
| `/etc/usbguard/rules.conf` | Politique principale — `0600 root:root` |
| `/etc/usbguard/rules.d/` | Politiques additionnelles, chargées par ordre alphanumérique |
| `/etc/usbguard/IPCAccessControl.d/` | Fichiers de contrôle d'accès IPC (`utilisateur` ou `:groupe`) |
| `/var/log/usbguard/usbguard-audit.log` | Journal d'audit, si `AuditBackend=FileAudit` est configuré |

### Paramètres clés de `usbguard-daemon.conf`

| Paramètre | Valeur par défaut | Signification |
|-----------|-------------------|---------------|
| `ImplicitPolicyTarget` | `block` | Sort réservé aux périphériques ne correspondant à aucune règle |
| `PresentDevicePolicy` | `apply-policy` | Traitement des périphériques déjà branchés au démarrage du démon |
| `PresentControllerPolicy` | `keep` | Traitement des contrôleurs USB déjà présents |
| `InsertedDevicePolicy` | `apply-policy` | Traitement des périphériques branchés à chaud |
| `RestoreControllerDeviceState` | `false` | Restaurer ou non l'état permissif d'origine à l'arrêt du démon |

!!! danger "Ne passez jamais `RestoreControllerDeviceState` à `true`"
    Avec cette valeur, il suffit de faire planter ou de couper le démon pour que le système revienne à son état d'origine — c'est-à-dire permissif. La protection devient contournable par une simple attaque en déni de service sur le processus.

---

## Problèmes fréquents

### Problème 1 : Plus de clavier ni de souris après l'installation

!!! failure "Symptôme"
    Immédiatement après `apt install usbguard`, l'écran ne réagit plus. Aucune saisie n'est possible, la souris est figée. Rien n'est affiché à l'écran pour l'expliquer.

**Cause :** le service a démarré avec une politique vide et `ImplicitPolicyTarget=block` : tout le matériel USB a été désautorisé, y compris les périphériques de saisie.

**Solution :**

=== "Si vous avez un accès SSH"

    Depuis une autre machine, connectez-vous et neutralisez le service :

    ```bash
    sudo systemctl stop usbguard.service
    sudo systemctl mask usbguard.service usbguard-dbus.service
    sudo reboot
    ```

    Reprenez ensuite la procédure à l'[étape 3](#etape-3-generer-la-politique-initiale).

=== "Si vous n'avez que la console locale"

    Le clavier fonctionne encore dans GRUB, car c'est le firmware UEFI/BIOS qui le gère à ce stade — USBGuard n'entre en scène qu'après le démarrage du noyau.

    1. Redémarrez la machine (bouton d'alimentation si nécessaire).
    2. Au menu GRUB, appuyez sur ++e++ pour éditer l'entrée de démarrage.
    3. Repérez la ligne commençant par `linux` et ajoutez à la **fin** de celle-ci :

        ```text
        systemd.mask=usbguard.service
        ```

    4. Appuyez sur ++ctrl+x++ pour démarrer. Le service ne sera pas lancé pour cette session uniquement.
    5. Une fois la session ouverte, rendez le masquage durable :

        ```bash
        sudo systemctl mask usbguard.service usbguard-dbus.service
        ```

!!! tip "Le menu GRUB ne s'affiche pas ?"
    Maintenez ++shift++ (BIOS hérité) ou appuyez plusieurs fois sur ++esc++ (UEFI) pendant le démarrage. Pour rendre le menu permanent une fois l'accès retrouvé : `GRUB_TIMEOUT_STYLE=menu` et `GRUB_TIMEOUT=5` dans `/etc/default/grub`, puis `sudo update-grub`.

---

### Problème 2 : Erreur de connexion à l'IPC

!!! failure "Symptôme"
    `usbguard list-devices` renvoie une erreur de connexion ou de permission alors que le démon tourne bien.

**Causes possibles, dans l'ordre à tester :**

1. **Le démon n'a pas été redémarré** après `add-user`. Les fichiers de `IPCAccessControl.d/` ne sont lus qu'au démarrage :
   ```bash
   sudo systemctl restart usbguard.service
   ```
2. **L'appartenance au groupe n'est pas active** dans la session courante. Vérifiez avec `id -nG` ; si le groupe manque, déconnectez-vous et reconnectez-vous (un simple `su - $USER` ne suffit pas pour une session graphique).
3. **Le fichier de contrôle d'accès ne porte pas le bon nom.** Un groupe doit être préfixé par `:` — `/etc/usbguard/IPCAccessControl.d/:sudo` — alors qu'un utilisateur n'a pas de préfixe. C'est le symptôme typique d'un `add-user` lancé sans `-g`.

---

### Problème 3 : La règle n'a pas survécu au redémarrage

!!! failure "Symptôme"
    Un périphérique autorisé la veille est de nouveau bloqué après un `reboot`.

**Causes :**

- Le drapeau `-p` a été oublié : l'autorisation n'existait qu'en mémoire.
- Ou le privilège IPC `Policy=modify` est absent : le démon a accepté l'autorisation temporaire mais a refusé d'écrire dans `rules.conf`. Corrigez en rejouant l'[étape 4](#etape-4-accorder-les-droits-dadministration-via-lipc) avec `--policy modify,list`, puis redémarrez le démon.

Contrôle rapide : la règle correspondante doit apparaître dans `sudo cat /etc/usbguard/rules.conf`, pas seulement dans `usbguard list-rules`.

---

### Problème 4 : Le périphérique est « allow » mais ne fonctionne toujours pas

!!! failure "Symptôme"
    `usbguard list-devices` indique `allow`, mais rien ne se monte et aucun pilote ne se charge.

**Cause :** l'USB est une **arborescence**. Un périphérique branché derrière un hub, un dock ou un écran-concentrateur ne peut être atteint que si **tous ses parents** sont eux-mêmes autorisés. Un hub bloqué rend inaccessible tout ce qui se trouve derrière lui.

**Solution :** affichez la hiérarchie et autorisez le hub parent, puis le périphérique :

```bash
usbguard list-devices -t
usbguard allow-device <ID_DU_HUB> -p
```

---

### Problème 5 : Un périphérique connu est bloqué après une mise à jour

!!! failure "Symptôme"
    Un matériel présent dans la politique depuis des mois se retrouve subitement en `block`.

**Cause :** son attribut `hash` a changé — mise à jour de firmware du périphérique, ou changement dans la façon dont le noyau expose ses descripteurs après une montée de version.

**Solution :** remplacez la règle par une version sans hash, adossée au numéro de série lorsqu'il existe :

```bash
usbguard list-rules | grep -i "nom du périphérique"   # relever l'ID de règle
usbguard remove-rule <ID_DE_REGLE>
usbguard append-rule 'allow id 0951:1666 serial "60A44C..." name "DataTraveler 3.0"'
```

---

### Problème 6 : `apt remove usbguard` se fige

!!! failure "Symptôme"
    La désinstallation reste bloquée pendant l'arrêt du service.

**Solution :** arrêtez et masquez d'abord les services, puis désinstallez :

```bash
sudo systemctl stop usbguard.service usbguard-dbus.service
sudo systemctl mask usbguard.service usbguard-dbus.service
sudo apt purge usbguard
```

---

## Checklist

- [ ] Tous les périphériques de confiance sont branchés avant de commencer
- [ ] Un second canal d'accès (SSH ou console d'hyperviseur) est disponible
- [ ] `usbguard.service` et `usbguard-dbus.service` sont masqués **avant** `apt install`
- [ ] Le paquet est installé et `usbguard --version` répond
- [ ] La politique initiale est générée, relue et installée en `0600 root:root`
- [ ] La politique contient bien le clavier, la souris et les périphériques internes
- [ ] Le fichier de contrôle d'accès IPC est créé dans `IPCAccessControl.d/` avec `Policy=modify`
- [ ] Le service est démasqué, activé et actif
- [ ] `usbguard list-devices` fonctionne sans `sudo`
- [ ] Une clé inconnue est bien refusée, une clé autorisée avec `-p` est bien acceptée
- [ ] La machine a été redémarrée et le clavier fonctionne dès l'écran de connexion
- [ ] (optionnel) Notifications de bureau ou protection GNOME à l'écran verrouillé activées

---

## Glossaire

BadUSB
:   Famille d'attaques exploitant la capacité d'un périphérique USB à mentir sur sa propre nature. Un objet ressemblant à une clé de stockage se déclare clavier et injecte des frappes à grande vitesse, ou se déclare carte réseau pour détourner le trafic DNS du poste.

Liste blanche (allow-list)
:   Modèle de sécurité où tout est interdit sauf ce qui est explicitement autorisé. Plus contraignant qu'une liste noire, mais seul modèle capable de résister à une menace inconnue à l'avance.

VID / PID
:   *Vendor ID* et *Product ID* : deux entiers 16 bits identifiant le constructeur et le modèle d'un périphérique USB (`046d:c52b`). Ils sont déclarés par le périphérique lui-même et sont donc trivialement falsifiables.

Classe d'interface USB
:   Catégorie fonctionnelle déclarée par le périphérique au format `classe:sous-classe:protocole`. Elle indique au noyau quel pilote charger. Un même périphérique physique peut exposer plusieurs interfaces de classes différentes — ce qui est précisément le mécanisme des attaques BadUSB.

HID
:   *Human Interface Device*, classe `03` : claviers, souris, manettes. C'est la classe visée par la majorité des attaques par injection de frappes, car aucun pilote spécifique ni aucune confirmation utilisateur n'est requis.

sysfs
:   Pseudo-système de fichiers monté sur `/sys`, qui expose les objets du noyau sous forme de fichiers. USBGuard s'appuie sur l'attribut `/sys/bus/usb/devices/*/authorized` pour autoriser ou désautoriser un périphérique.

Démon (daemon)
:   Processus qui tourne en arrière-plan, sans terminal attaché, généralement lancé et supervisé par `systemd`. Ici, `usbguard-daemon`.

IPC
:   *Inter-Process Communication* : mécanisme permettant à deux processus d'échanger. USBGuard expose un canal IPC pour que l'outil `usbguard` pilote le démon sans être `root`, avec un contrôle fin des privilèges.

Cible implicite (`ImplicitPolicyTarget`)
:   Décision appliquée à un périphérique ne correspondant à aucune règle de la politique. `block` par défaut, c'est ce qui fait d'USBGuard une liste blanche.

Attaque « evil maid »
:   Scénario où un attaquant obtient un accès physique bref à une machine laissée sans surveillance (chambre d'hôtel, open space) pour y brancher un périphérique malveillant. La protection GNOME à l'écran verrouillé cible directement ce cas.

*[USB]: Universal Serial Bus
*[HID]: Human Interface Device
*[IPC]: Inter-Process Communication
*[VID]: Vendor ID
*[PID]: Product ID
*[ACL]: Access Control List
*[FIDO2]: Fast IDentity Online 2
*[IPMI]: Intelligent Platform Management Interface

---

## Ressources

- [Site officiel USBGuard](https://usbguard.github.io/) — Documentation de référence du projet
- [Documentation : configuration du démon](https://usbguard.github.io/documentation/configuration) — Détail de `usbguard-daemon.conf` et du contrôle d'accès IPC
- [`usbguard(1)` — manuel Debian](https://manpages.debian.org/testing/usbguard/usbguard.1.en.html) — Toutes les sous-commandes et leurs options
- [`usbguard-rules.conf(5)` — manuel Debian](https://manpages.debian.org/testing/usbguard/usbguard-rules.conf.5.en.html) — Grammaire complète du langage de règles
- [Red Hat — Protecting systems against intrusive USB devices](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/security_hardening/protecting-systems-against-intrusive-usb-devices_security-hardening) — Bonnes pratiques et politiques structurées dans `rules.d/`
- [USBGuard sur ArchWiki](https://wiki.archlinux.org/title/USBGuard) — Intégration GNOME et cas particuliers
- [Dépôt GitHub du projet](https://github.com/USBGuard/usbguard) — Sources, journal des versions et suivi des bugs
