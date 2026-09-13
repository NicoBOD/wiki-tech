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
    USBGuard applique une politique d’autorisation sur le bus USB : seuls les périphériques correspondant à une règle d’autorisation peuvent être utilisés par le noyau. Les autres sont bloqués ou rejetés selon la politique configurée.

    Cette note couvre l’installation sur Ubuntu 24.04, la génération d’une liste blanche à partir du matériel de confiance, la configuration des droits IPC et la gestion quotidienne des nouveaux périphériques. Elle explique également comment éviter — ou réparer — le verrouillage du clavier et de la souris qui peut survenir lors d’une première installation mal préparée.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 LTS (Desktop et Server) |
| Version d’USBGuard | À vérifier avec `apt policy usbguard` et `usbguard --version` |
| Privilèges requis | `root` / `sudo` |
| Durée estimée | 20 à 30 minutes |
| Dernière mise à jour | 2026-09-13 |

---

## Contexte

Le bus USB a été conçu pour la commodité, pas pour la sécurité. Par défaut, un périphérique branché est détecté par le noyau, ses interfaces sont examinées et les pilotes correspondants peuvent être chargés.

C’est notamment ce qu’exploite la famille d’attaques dite **BadUSB** : un objet ressemblant à une clé de stockage peut se déclarer comme un clavier USB, puis injecter automatiquement des frappes afin d’ouvrir un terminal ou d’exécuter des commandes. D’autres variantes se présentent comme une carte réseau, un adaptateur série ou un périphérique composite exposant plusieurs fonctions à la fois.

USBGuard s’appuie sur le mécanisme d’autorisation USB du noyau Linux. Chaque périphérique USB expose dans `sysfs` un attribut `authorized`, généralement sous :

```text
/sys/bus/usb/devices/*/authorized
```

Lorsqu’un périphérique est désautorisé, ses interfaces ne peuvent normalement pas être utilisées par les pilotes du noyau.

Le démon `usbguard-daemon` automatise cette décision :

1. Il surveille l’apparition et la disparition des périphériques USB.
2. Il compare chaque périphérique aux règles de la politique.
3. Les règles sont examinées dans l’ordre et la première règle correspondante détermine la décision.
4. Si aucune règle ne correspond, la cible définie par `ImplicitPolicyTarget` est appliquée.

Une politique configurée avec une cible implicite `block` suit donc un modèle de **liste blanche** : tout ce qui n’est pas explicitement autorisé reste bloqué.

!!! danger "Le piège principal : se verrouiller hors de sa propre machine"
    Lors de l’installation du paquet, le service peut être activé ou démarré automatiquement par les scripts du paquet. Selon la version, la configuration et le mode d’installation, une politique initiale peut également être générée à partir des périphériques présents.

    Il ne faut pas dépendre de ce comportement :

    - une politique vide ou incomplète peut bloquer le clavier et la souris ;
    - une politique générée automatiquement peut autoriser un périphérique indésirable déjà branché ;
    - un périphérique indispensable placé derrière un hub non autorisé peut devenir inaccessible.

    La procédure ci-dessous masque donc le service **avant** l’installation, afin de préparer et de relire la politique avant toute mise en application.

!!! info "USBGuard n’est pas un antivirus"
    USBGuard décide quel matériel peut être utilisé par le noyau. Il n’analyse pas les fichiers présents sur les supports USB et ne détecte aucun logiciel malveillant.

    Il peut être combiné au chiffrement, à la désactivation du montage automatique, aux options `nosuid,nodev,noexec` et à une solution d’analyse des fichiers. L’option `noexec` constitue seulement une barrière supplémentaire : elle n’empêche pas nécessairement un interpréteur d’exécuter explicitement un script présent sur le support.

---

## Prérequis

- Un poste ou serveur sous **Ubuntu 24.04 LTS**.
- Un compte disposant des droits `sudo`.
- Tous les périphériques USB indispensables branchés avant la génération de la politique :
  - clavier ;
  - souris ;
  - récepteur sans fil ;
  - hub ou dock ;
  - webcam ;
  - casque ;
  - adaptateur réseau USB ;
  - clé de sécurité FIDO2 ;
  - lecteur d’empreintes ;
  - périphériques internes reliés en USB.
- Les périphériques non indispensables ou non vérifiés doivent être débranchés.
- Fortement recommandé : un second canal d’accès déjà testé, par exemple :
  - une session SSH ouverte depuis une autre machine ;
  - une console d’hyperviseur ;
  - une console série ;
  - une interface IPMI ou équivalente.

!!! warning "Vérifiez la nature du clavier interne"
    Un clavier ou un pavé tactile interne utilisant `i8042`, I²C-HID ou SPI n’est normalement pas contrôlé par USBGuard. Certains périphériques internes sont cependant reliés au bus USB.

    Vérifiez la topologie réelle de la machine :

    ```bash
    lsusb
    lsusb -t
    grep -iE 'keyboard|mouse|touchpad' /proc/bus/input/devices
    ```

!!! warning "Cas particulier : serveur distant"
    Sur un serveur administré uniquement en SSH, vérifiez attentivement les adaptateurs réseau USB, les périphériques KVM, les clés de licence et les supports contenant des données nécessaires au démarrage.

    Si l’interface réseau utilisée par SSH est elle-même raccordée en USB et qu’elle est bloquée, vous perdrez également l’accès distant.

---

## Procédure

### Étape 1 : contrôler les périphériques présents

Avant de générer une politique, débranchez les périphériques non indispensables puis examinez la topologie USB :

```bash
lsusb
lsusb -t
```

!!! danger "La génération de politique ne vérifie pas la fiabilité du matériel"
    `usbguard generate-policy` crée des règles à partir des périphériques détectés. Il ne sait pas déterminer si un périphérique est légitime, compromis ou malveillant.

    Un périphérique indésirable déjà branché pendant la génération risque donc d’être ajouté à la liste blanche.

---

### Étape 2 : neutraliser le démarrage automatique du service

Masquez les unités systemd avant d’installer le paquet :

```bash
sudo systemctl mask usbguard.service usbguard-dbus.service
```

`systemctl mask` crée des liens vers `/dev/null` dans `/etc/systemd/system/`. Une unité masquée ne peut pas être démarrée, y compris par un script de post-installation.

!!! note "Pourquoi masquer plutôt que désactiver ?"
    `systemctl disable` empêche principalement le lancement automatique au démarrage de la machine. Il n’empêche pas nécessairement un script de paquet de démarrer immédiatement le service.

    `systemctl mask` bloque également les démarrages manuels et les démarrages demandés par une autre unité.

Une unité peut être masquée avant même que son fichier soit installé. Selon la version de systemd, un avertissement indiquant que l’unité n’existe pas encore peut être affiché sans empêcher la création du masque.

Vérifiez les liens :

```bash
ls -l /etc/systemd/system/usbguard.service
ls -l /etc/systemd/system/usbguard-dbus.service
```

Les liens doivent pointer vers `/dev/null`.

---

### Étape 3 : installer le paquet

```bash
sudo apt update
sudo apt install usbguard
```

Vérifiez la version réellement installée et l’état du service :

```bash
apt policy usbguard
usbguard --version

systemctl is-enabled usbguard.service
systemctl is-active usbguard.service
```

Résultat attendu :

- `usbguard.service` est `masked` ;
- `usbguard.service` est `inactive` ;
- les périphériques USB continuent de fonctionner.

!!! note "Version du paquet"
    Ubuntu 24.04 fournit un paquet basé sur USBGuard 1.1.2 au moment de la rédaction. Le numéro de révision Ubuntu et la version disponible peuvent évoluer avec les mises à jour.

    Utilisez toujours les commandes ci-dessus plutôt que de supposer une version précise.

---

### Étape 4 : examiner la configuration du démon

Affichez les paramètres principaux :

```bash
sudo grep -E '^[[:space:]]*(RuleFile|RuleFolder|ImplicitPolicyTarget|PresentDevicePolicy|PresentControllerPolicy|InsertedDevicePolicy|RestoreControllerDeviceState)=' \
    /etc/usbguard/usbguard-daemon.conf
```

Vérifiez notamment les valeurs suivantes :

```text
ImplicitPolicyTarget=block
PresentDevicePolicy=apply-policy
InsertedDevicePolicy=apply-policy
RestoreControllerDeviceState=false
```

Les lignes exactes peuvent différer selon la version du paquet. Si un paramètre n’est pas présent, consultez sa valeur par défaut dans le manuel installé :

```bash
man usbguard-daemon.conf
```

!!! warning "RuleFile et RuleFolder"
    Vérifiez si le démon utilise un fichier unique avec `RuleFile` ou un dossier avec `RuleFolder`.

    La configuration Ubuntu habituelle utilise :

    ```text
    RuleFile=/etc/usbguard/rules.conf
    ```

    Ne supposez pas que `/etc/usbguard/rules.d/` est automatiquement chargé. Ce dossier n’est utilisé que si `RuleFolder` est explicitement configuré et pris en charge par la version installée.

---

### Étape 5 : générer la politique initiale

Générez la politique dans un fichier temporaire avec des permissions restrictives :

```bash
sudo sh -c 'umask 077; usbguard generate-policy > /tmp/usbguard-rules.conf'
```

Relisez intégralement son contenu :

```bash
sudo nano /tmp/usbguard-rules.conf
```

Vous devez retrouver les périphériques USB de confiance actuellement présents :

- clavier ;
- souris ;
- récepteur sans fil ;
- webcam ;
- Bluetooth interne ;
- lecteur d’empreintes ;
- clé FIDO2 ;
- hubs et docks éventuels ;
- adaptateur réseau USB, le cas échéant.

Les contrôleurs hôtes USB sont traités séparément par USBGuard, notamment au moyen de `PresentControllerPolicy`. Leur absence parmi les règles ordinaires n’est donc pas nécessairement une anomalie.

Installez ensuite le fichier avec les bons droits :

```bash
sudo install -m 0600 -o root -g root \
    /tmp/usbguard-rules.conf \
    /etc/usbguard/rules.conf
```

Vérifiez le résultat :

```bash
sudo cat /etc/usbguard/rules.conf
stat -c '%A %U:%G %n' /etc/usbguard/rules.conf
```

Résultat attendu :

```text
-rw------- root:root /etc/usbguard/rules.conf
```

!!! warning "Ne remplacez pas à l’aveugle une politique active"
    Lors d’une modification ultérieure, générez toujours la nouvelle politique dans un fichier temporaire. Relisez-la avant de remplacer le fichier utilisé par le démon.

    Sauvegardez la politique existante :

    ```bash
    sudo cp -a /etc/usbguard/rules.conf \
        /etc/usbguard/rules.conf.backup
    ```

#### Lire une règle USBGuard

Une règle générée peut ressembler à ceci :

```text title="/etc/usbguard/rules.conf"
allow id 046d:c52b serial "" name "USB Receiver" hash "jEP/6WzviqdJ5VSeTUY8Pat…" parent-hash "kv0Xb…" with-interface { 03:01:01 03:01:02 03:00:00 }
```

| Élément | Signification |
|---------|---------------|
| `allow` | Cible de la règle : `allow` autorise le périphérique, `block` le maintient désautorisé et `reject` tente de le retirer logiquement du système. |
| `id 046d:c52b` | Identifiants VID:PID du constructeur et du modèle. Ils sont déclarés par le périphérique et sont falsifiables. |
| `serial ""` | Numéro de série déclaré par le périphérique. Il est vide sur de nombreux matériels et reste falsifiable. |
| `name "…"` | Nom déclaré par le périphérique. Lorsqu’il figure dans la règle, il participe à la correspondance, mais il reste falsifiable. |
| `hash "…"` | Empreinte calculée à partir des descripteurs USB. Elle rend la règle plus précise, sans constituer une authentification cryptographique. |
| `parent-hash "…"` | Empreinte des descripteurs du périphérique parent, généralement un hub. Elle ne désigne pas à elle seule un port physique précis. |
| `via-port "…"` | Chemin ou port USB auquel la règle est associée. Ce critère dépend de la topologie physique. |
| `with-interface { … }` | Classes d’interface annoncées par le périphérique, au format `classe:sous-classe:protocole`. |

!!! warning "Le hash n’est pas une preuve d’identité"
    Le `hash` USBGuard est calculé à partir des descripteurs annoncés par le périphérique. Il ne s’agit ni d’une signature cryptographique, ni d’une attestation du firmware, ni d’une identité matérielle infalsifiable.

    Un périphérique programmable connaissant les valeurs attendues peut tenter de reproduire les mêmes descripteurs.

    Le hash reste néanmoins utile pour réduire les correspondances accidentelles entre plusieurs périphériques partageant le même VID:PID.

#### Lier une règle à un port

Pour une machine dont le câblage est stable, il est possible de générer des règles liées à la topologie des ports :

```bash
sudo sh -c 'umask 077; usbguard generate-policy --with-ports > /tmp/usbguard-rules.conf'
```

Cette option ajoute des critères `via-port`.

!!! warning "Inconvénient de `via-port`"
    Une règle liée à un port peut cesser de correspondre après :

    - un changement de port ;
    - l’ajout ou le retrait d’un hub ;
    - le remplacement d’un dock ;
    - une modification de la topologie USB ;
    - certains changements de firmware ou de matériel.

#### Générer sans hash

Il est possible de générer une politique sans empreintes :

```bash
sudo sh -c 'umask 077; usbguard generate-policy --no-hashes > /tmp/usbguard-rules.conf'
```

Cette politique est généralement plus tolérante aux changements de descripteurs, mais elle est aussi moins précise.

Si vous retirez les hashes, essayez de conserver plusieurs critères :

- `id` ;
- `serial`, lorsqu’il est réellement unique ;
- `name` ;
- `with-interface` ;
- éventuellement `via-port`.

Aucun de ces champs ne constitue cependant une authentification cryptographique.

#### Classes d’interface importantes

| Classe | Fonction habituelle |
|--------|---------------------|
| `03` | HID : clavier, souris, manette |
| `08` | Stockage de masse |
| `09` | Hub USB |
| `0e` | Vidéo, par exemple webcam |
| `e0` | Sans fil, notamment certains adaptateurs Bluetooth |
| `ff` | Fonction spécifique au constructeur |

Une règle placée avant les règles d’autorisation peut rejeter les périphériques composites annonçant simultanément une interface de stockage et une interface HID :

```text
reject with-interface all-of { 08:*:* 03:*:* }
```

!!! warning "Cette règle ne bloque pas tous les BadUSB"
    Elle bloque seulement les périphériques présentant simultanément une fonction de stockage et une fonction HID.

    Un périphérique malveillant se présentant uniquement comme clavier HID ne correspond pas à cette règle. La protection principale reste donc une liste blanche précise des périphériques HID autorisés.

    Certains périphériques légitimes sont également composites. Vérifiez l’impact d’une telle règle sur les téléphones, docks, claviers avec lecteur de cartes et matériels spécialisés.

---

### Étape 6 : accorder les droits d’administration via l’IPC

Le démon expose une interface IPC permettant à l’outil `usbguard` de consulter les périphériques et de modifier leur état.

USBGuard prend en charge des fichiers de contrôle d’accès dans :

```text
/etc/usbguard/IPCAccessControl.d/
```

Vérifiez d’abord la syntaxe prise en charge par la version installée :

```bash
usbguard add-user --help
```

Pour accorder les droits au groupe `sudo` :

```bash
sudo usbguard add-user sudo --group \
    --devices ALL \
    --policy modify,list \
    --exceptions listen
```

!!! warning "Position de l’option `--group`"
    Avec USBGuard 1.1.x, le nom du groupe est généralement fourni comme argument positionnel et `--group` indique que cet argument désigne un groupe :

    ```bash
    usbguard add-user NOM_DU_GROUPE --group ...
    ```

    Vérifiez toujours `usbguard add-user --help`, car la syntaxe exacte peut varier selon la version empaquetée.

| Option | Effet |
|--------|-------|
| `sudo` | Nom du groupe auquel les droits sont accordés |
| `--group` | Indique que la cible est un groupe et non un utilisateur |
| `--devices ALL` | Autorise la consultation, l’écoute et la modification de l’état des périphériques |
| `--policy modify,list` | Autorise la lecture et la modification de la politique |
| `--exceptions listen` | Autorise la réception des événements d’exception |

Vérifiez le fichier créé :

```bash
sudo ls -l /etc/usbguard/IPCAccessControl.d/
sudo cat /etc/usbguard/IPCAccessControl.d/:sudo
```

Le contenu doit être proche de :

```text
Devices=modify list listen
Policy=modify list
Exceptions=listen
```

!!! warning "Ces droits permettent de modifier la politique de sécurité"
    `Devices=modify` permet d’autoriser ou de bloquer des périphériques à chaud.

    `Policy=modify` permet d’ajouter des règles persistantes et donc, potentiellement, d’affaiblir fortement la politique.

    Sur un poste personnel, les accorder au groupe `sudo` n’ajoute généralement pas de privilège fondamental, puisque ses membres peuvent déjà devenir `root`. Sur un système multi-utilisateur, utilisez un groupe administratif dédié :

    ```bash
    sudo groupadd --system usbguard-admin
    sudo usermod -aG usbguard-admin "$USER"

    sudo usbguard add-user usbguard-admin --group \
        --devices ALL \
        --policy modify,list \
        --exceptions listen
    ```

    L’appartenance au nouveau groupe ne devient effective qu’après une reconnexion complète de la session.

Les fichiers de contrôle d’accès sont lus au démarrage du démon. Toute modification nécessite donc un démarrage ou un redémarrage d’USBGuard.

---

### Étape 7 : démarrer le démon

La politique et les droits IPC étant en place, démasquez puis activez le service :

```bash
sudo systemctl unmask usbguard.service
sudo systemctl enable --now usbguard.service
```

Vérifiez son état :

```bash
systemctl --no-pager --full status usbguard.service
journalctl -u usbguard.service -b --no-pager
```

Puis interrogez USBGuard :

```bash
usbguard list-devices
usbguard list-rules
```

Résultat attendu :

- le service est `active (running)` ;
- les périphériques de confiance sont indiqués comme `allow` ;
- le clavier et la souris continuent de fonctionner ;
- `usbguard list-devices` fonctionne sans `sudo` pour les membres du groupe autorisé.

!!! warning "Si l’accès IPC échoue"
    Testez d’abord les commandes avec `sudo` :

    ```bash
    sudo usbguard list-devices
    sudo usbguard list-rules
    ```

    Si elles fonctionnent avec `sudo` mais pas sans, le problème vient probablement des droits IPC ou de l’appartenance au groupe, et non de la politique USB elle-même.

---

### Étape 8 : tester la politique

Commencez par un périphérique non indispensable.

1. Débranchez puis rebranchez une souris ou un périphérique autorisé.
2. Vérifiez qu’il redevient immédiatement utilisable.
3. Branchez ensuite une clé USB inconnue.
4. Vérifiez qu’elle n’est pas montée.
5. Affichez les périphériques bloqués :

```bash
usbguard list-devices --blocked
```

Selon la version installée, la forme courte suivante peut également être disponible :

```bash
usbguard list-devices -b
```

Un périphérique inconnu doit apparaître avec l’état `block`.

!!! danger "Ne commencez pas avec un périphérique critique"
    Ne testez pas initialement avec :

    - votre seul clavier ;
    - l’adaptateur réseau utilisé pour SSH ;
    - le support contenant le système ;
    - un dock indispensable ;
    - le seul périphérique permettant la récupération.

---

### Étape 9 : autoriser un nouveau périphérique

#### Identifier son identifiant interne

```bash
usbguard list-devices --blocked
```

Exemple :

```text
16: block id 0951:1666 serial "60A44C..." name "DataTraveler 3.0" hash "…" with-interface { 08:06:50 }
```

Le premier nombre, `16` dans cet exemple, est l’identifiant interne attribué par le démon au périphérique.

Il ne faut pas le confondre avec :

- le VID:PID `0951:1666` ;
- l’identifiant d’une règle affiché par `usbguard list-rules`.

L’identifiant du périphérique peut changer après un rebranchement ou un redémarrage du démon.

#### Autorisation temporaire

```bash
usbguard allow-device 16
```

Cette décision n’ajoute pas de règle persistante. Elle disparaît notamment après le redémarrage du démon ou la disparition du périphérique.

Utilisez cette méthode pour un périphérique de passage dont vous ne souhaitez pas conserver l’autorisation.

#### Autorisation permanente

```bash
usbguard allow-device 16 -p
```

Le drapeau `-p` ou `--permanent` ajoute une règle persistante à la politique configurée par le démon.

Avec la configuration Ubuntu habituelle utilisant :

```text
RuleFile=/etc/usbguard/rules.conf
```

la règle est enregistrée dans ce fichier.

!!! warning "Relisez toute règle permanente"
    Une règle générée automatiquement peut être plus large ou plus fragile que prévu. Après une autorisation permanente, examinez la politique :

    ```bash
    usbguard list-rules
    sudo grep -nF '0951:1666' /etc/usbguard/rules.conf
    ```

    Remplacez `0951:1666` par un attribut du périphérique concerné.

!!! warning "Le sens de `-p` dépend de la sous-commande"
    Avec `allow-device`, `block-device` et `reject-device`, `-p` signifie généralement `--permanent`.

    Avec `generate-policy`, `-p` peut signifier `--with-ports`.

    Vérifiez l’aide de la sous-commande avant utilisation :

    ```bash
    usbguard allow-device --help
    usbguard generate-policy --help
    ```

#### Suivre les événements en direct

```bash
usbguard watch
```

Cette commande permet d’observer les branchements, les blocages et les modifications d’état en temps réel.

---

### Étape 10 facultative : notifications sur le bureau

#### Installer `usbguard-notifier`

```bash
sudo apt install usbguard-notifier
```

Vérifiez le mécanisme de lancement fourni par le paquet :

```bash
dpkg -L usbguard-notifier | grep -E 'systemd|autostart|\.desktop$'
systemctl --user list-unit-files 'usbguard*'
```

Si une unité utilisateur `usbguard-notifier.service` est effectivement installée :

```bash
systemctl --user enable --now usbguard-notifier.service
```

Si le paquet fournit uniquement un fichier XDG Autostart, déconnectez-vous puis reconnectez-vous.

Le notifier doit disposer au minimum du droit IPC nécessaire pour écouter les événements :

```text
Devices=listen
```

!!! warning "Ne donnez pas de droits excessifs au notifier"
    Un outil chargé uniquement d’afficher des notifications n’a pas besoin du droit `Policy=modify`.

    Ne rendez jamais les sockets ou fichiers USBGuard accessibles à tous avec `chmod 666` ou `chmod 777`, et n’exécutez pas une application graphique avec `sudo` pour contourner un problème de permissions.

#### Protection USB proposée par GNOME

Certaines versions de GNOME peuvent utiliser le service D-Bus d’USBGuard afin de renforcer la politique lorsque la session est verrouillée.

Cette fonction dépend :

- de la version de GNOME ;
- des paquets installés ;
- des correctifs Ubuntu ;
- de la présence du service D-Bus ;
- de la présence des clés `gsettings` correspondantes.

Vérifiez d’abord les éléments disponibles :

```bash
systemctl list-unit-files 'usbguard*'
gsettings list-keys org.gnome.desktop.privacy | grep '^usb-protection'
```

Si `usbguard-dbus.service` et les clés correspondantes existent :

```bash
sudo systemctl unmask usbguard-dbus.service
sudo systemctl enable --now usbguard-dbus.service

gsettings set org.gnome.desktop.privacy usb-protection true
gsettings set org.gnome.desktop.privacy usb-protection-level 'lockscreen'
```

La valeur `'always'` peut être disponible selon le schéma installé :

```bash
gsettings range org.gnome.desktop.privacy usb-protection-level
```

!!! note "Le service D-Bus est facultatif"
    `usbguard.service` et son interface IPC suffisent à appliquer la politique USBGuard.

    N’activez `usbguard-dbus.service` que si GNOME ou un autre client installé en a réellement besoin.

---

## Vérification

Effectuez les contrôles suivants une fois la configuration terminée.

### État du service

```bash
systemctl is-active usbguard.service
systemctl is-enabled usbguard.service
```

Résultat attendu :

```text
active
enabled
```

### Politique chargée

```bash
usbguard list-rules
```

La liste ne doit pas être vide.

### Paramètres actifs

```bash
usbguard get-parameter ImplicitPolicyTarget
usbguard get-parameter PresentDevicePolicy
usbguard get-parameter InsertedDevicePolicy
```

Les valeurs attendues pour une politique de liste blanche sont généralement :

```text
block
apply-policy
apply-policy
```

Vérifiez également la configuration sur disque :

```bash
sudo grep -E '^[[:space:]]*(ImplicitPolicyTarget|PresentDevicePolicy|InsertedDevicePolicy|PresentControllerPolicy|RestoreControllerDeviceState)=' \
    /etc/usbguard/usbguard-daemon.conf
```

### Journaux

```bash
journalctl -u usbguard.service -b --no-pager | tail -n 50
```

Recherchez notamment :

- une erreur de syntaxe dans une règle ;
- une erreur de chargement du fichier ;
- une erreur de permission ;
- un problème IPC ;
- un périphérique indispensable bloqué.

### Tests finaux

1. Redémarrez la machine.
2. Vérifiez le clavier et la souris à l’écran de connexion.
3. Vérifiez le réseau si un adaptateur USB est utilisé.
4. Rebranchez un périphérique autorisé.
5. Branchez un périphérique inconnu non indispensable et confirmez son blocage.
6. Si la machine utilise un dock ou une topologie complexe, effectuez également un arrêt complet suivi d’un démarrage.
7. Vérifiez la procédure de récupération pendant qu’un accès de secours reste disponible.

---

## Aide-mémoire

| Commande ou action | Description |
|--------------------|-------------|
| `usbguard list-devices` | Lister les périphériques connus du démon et leur état |
| `usbguard list-devices --blocked` | Lister les périphériques bloqués |
| `usbguard list-devices -t` | Afficher les périphériques sous forme d’arborescence, si l’option est prise en charge |
| `usbguard allow-device <ID>` | Autoriser temporairement un périphérique |
| `usbguard allow-device <ID> -p` | Autoriser un périphérique et ajouter une règle persistante |
| `usbguard block-device <ID> -p` | Bloquer un périphérique avec une règle persistante |
| `usbguard reject-device <ID>` | Rejeter logiquement un périphérique |
| `usbguard list-rules` | Afficher la politique chargée et les identifiants de règles |
| `usbguard list-rules -d` | Afficher des informations supplémentaires sur les règles, si l’option est prise en charge |
| `usbguard append-rule '<règle>'` | Ajouter une règle à la politique |
| `usbguard remove-rule <ID>` | Supprimer une règle à partir de son identifiant |
| `usbguard generate-policy` | Générer une politique à partir des périphériques présents |
| `usbguard generate-policy --no-hashes` | Générer une politique sans empreintes |
| `usbguard generate-policy --with-ports` | Générer des règles liées à la topologie des ports |
| `usbguard watch` | Suivre les événements USBGuard en temps réel |
| `usbguard add-user <nom> …` | Créer un contrôle d’accès IPC |
| `usbguard remove-user <nom>` | Supprimer un contrôle d’accès IPC |
| `usbguard get-parameter <nom>` | Lire un paramètre exposé par le démon |
| `usbguard set-parameter <nom> <valeur>` | Modifier un paramètre à chaud, sans nécessairement le rendre persistant |
| `lsusb` | Lister les périphériques vus par le noyau |
| `lsusb -t` | Afficher l’arborescence USB vue par le noyau |
| `journalctl -u usbguard.service -b` | Consulter les journaux du démon pour le démarrage courant |

Vérifiez les options disponibles dans la version installée :

```bash
usbguard --help
usbguard list-devices --help
usbguard generate-policy --help
```

### Fichiers importants

| Chemin | Rôle |
|--------|------|
| `/etc/usbguard/usbguard-daemon.conf` | Configuration du démon |
| `/etc/usbguard/rules.conf` | Fichier de politique habituel sur Ubuntu |
| `/etc/usbguard/rules.d/` | Dossier de politiques uniquement si `RuleFolder` est configuré |
| `/etc/usbguard/IPCAccessControl.d/` | Contrôles d’accès IPC pour les utilisateurs et les groupes |
| `/var/log/usbguard/usbguard-audit.log` | Journal d’audit si `AuditBackend=FileAudit` est configuré |
| `/var/log/journal/` | Journaux persistants de systemd, lorsqu’ils sont activés |

### Paramètres clés de `usbguard-daemon.conf`

| Paramètre | Valeur habituelle à vérifier | Signification |
|-----------|------------------------------|---------------|
| `RuleFile` | `/etc/usbguard/rules.conf` | Fichier principal de politique |
| `RuleFolder` | Variable selon la configuration | Dossier contenant des politiques additionnelles |
| `ImplicitPolicyTarget` | `block` | Décision appliquée lorsqu’aucune règle ne correspond |
| `PresentDevicePolicy` | `apply-policy` | Traitement des périphériques présents au démarrage du démon |
| `PresentControllerPolicy` | `keep` | Traitement des contrôleurs USB déjà présents |
| `InsertedDevicePolicy` | `apply-policy` | Traitement des périphériques branchés à chaud |
| `RestoreControllerDeviceState` | `false` | Restauration éventuelle de l’état antérieur des contrôleurs lors de l’arrêt propre du démon |

!!! warning "Conservez de préférence `RestoreControllerDeviceState=false`"
    Avec `true`, USBGuard tente de restaurer l’état antérieur des contrôleurs lors d’un **arrêt propre** du démon. Si cet état était permissif, de nouveaux périphériques pourraient alors être autorisés après l’arrêt du service.

    Un processus interrompu brutalement ne peut généralement pas exécuter cette restauration. Il est donc incorrect d’affirmer qu’un simple crash restaure automatiquement un état permissif.

    La valeur `false` reste néanmoins préférable pour conserver un comportement aussi proche que possible du « fail closed » après l’arrêt du service.

---

## Problèmes fréquents

### Problème 1 : plus de clavier ni de souris après l’installation

!!! failure "Symptôme"
    Après l’installation ou le démarrage du service, l’écran ne réagit plus, le clavier ne saisit rien et la souris reste figée.

**Causes possibles :**

- le service a démarré avec une politique vide ;
- la politique ne contient aucune règle correspondant aux périphériques de saisie ;
- le clavier ou la souris se trouve derrière un hub bloqué ;
- les descripteurs actuels ne correspondent plus à la règle ;
- la politique présente au démarrage n’est pas celle que vous avez modifiée.

Avec `ImplicitPolicyTarget=block`, le matériel concerné est alors désautorisé.

#### Si vous avez un accès SSH

Masquez et arrêtez les services :

```bash
sudo systemctl mask --now usbguard.service usbguard-dbus.service
systemctl is-enabled usbguard.service
sudo reboot
```

L’arrêt du démon ne réautorise pas nécessairement les périphériques déjà bloqués. Leur rebranchement ou un redémarrage peut être nécessaire.

Après le redémarrage, reprenez la procédure à l’étape de génération de la politique.

#### Si vous n’avez que la console locale

Un clavier USB directement connecté est généralement pris en charge par le firmware dans GRUB, avant le démarrage d’USBGuard. Ce n’est toutefois pas garanti avec :

- un clavier Bluetooth ;
- certains récepteurs sans fil ;
- un dock USB-C ;
- un KVM ;
- certaines configurations UEFI.

Si le clavier fonctionne dans GRUB :

1. Redémarrez la machine.
2. Affichez le menu GRUB.
3. Appuyez sur ++e++ pour modifier l’entrée.
4. Repérez la ligne commençant par `linux`.
5. Ajoutez à la fin :

    ```text
    systemd.mask=usbguard.service systemd.mask=usbguard-dbus.service
    ```

6. Appuyez sur ++ctrl+x++ ou ++f10++ pour démarrer.
7. Une fois la session ouverte, rendez le masquage permanent :

    ```bash
    sudo systemctl mask usbguard.service usbguard-dbus.service
    ```

!!! tip "Le menu GRUB ne s’affiche pas"
    Maintenez ++shift++ sur certaines machines BIOS ou appuyez plusieurs fois sur ++esc++ sur certaines machines UEFI.

    Pour rendre le menu temporairement visible lors des prochains démarrages, modifiez `/etc/default/grub` :

    ```text
    GRUB_TIMEOUT_STYLE=menu
    GRUB_TIMEOUT=5
    ```

    Puis appliquez la configuration :

    ```bash
    sudo update-grub
    ```

!!! danger "Ne dépendez pas d’une méthode de récupération non testée"
    Le mode de récupération ne garantit pas que le clavier fonctionnera. Sur une machine chiffrée ou sans périphérique d’entrée indépendant de l’USB, prévoyez une console distante, un accès série ou un support de secours testé.

---

### Problème 2 : erreur de connexion à l’IPC

!!! failure "Symptôme"
    `usbguard list-devices` renvoie une erreur de connexion ou de permission alors que le démon fonctionne.

Testez d’abord :

```bash
sudo usbguard list-devices
```

Si la commande fonctionne avec `sudo`, vérifiez les éléments suivants.

#### Le démon n’a pas été redémarré

Les fichiers de contrôle d’accès sont lus au démarrage :

```bash
sudo systemctl restart usbguard.service
```

#### L’appartenance au groupe n’est pas active

```bash
id
id -nG
```

Déconnectez-vous complètement puis reconnectez-vous si le groupe manque.

#### Le fichier de contrôle d’accès porte un mauvais nom

Pour un groupe, le fichier est normalement préfixé par `:` :

```text
/etc/usbguard/IPCAccessControl.d/:sudo
```

Pour un utilisateur, il ne possède pas ce préfixe.

#### Le service ne fonctionne pas

```bash
systemctl status usbguard.service
journalctl -u usbguard.service -b --no-pager
```

!!! danger "Ne contournez pas le problème avec des permissions globales"
    N’utilisez pas `chmod 666`, `chmod 777`, `xhost +` ou l’exécution d’un programme graphique avec `sudo`.

    Corrigez les droits IPC au moyen des mécanismes fournis par USBGuard.

---

### Problème 3 : une autorisation n’a pas survécu au redémarrage

!!! failure "Symptôme"
    Un périphérique autorisé précédemment est de nouveau bloqué après le redémarrage.

**Causes possibles :**

- l’option `-p` a été oubliée ;
- le compte possède `Devices=modify`, mais pas `Policy=modify` ;
- le démon utilise un autre `RuleFile` ou un `RuleFolder` ;
- la règle persistante ne correspond plus au périphérique ;
- le périphérique a été branché sur un autre port alors que la règle contient `via-port`.

Vérifiez :

```bash
usbguard list-rules
sudo grep -E '^[[:space:]]*(RuleFile|RuleFolder)=' \
    /etc/usbguard/usbguard-daemon.conf
```

Avec la configuration habituelle :

```bash
sudo grep -nF 'VID:PID' /etc/usbguard/rules.conf
```

Remplacez `VID:PID` par l’identifiant réel, par exemple `0951:1666`.

---

### Problème 4 : le périphérique est autorisé mais ne fonctionne pas

!!! failure "Symptôme"
    `usbguard list-devices` indique `allow`, mais aucun pilote ne se charge ou aucun support n’apparaît.

L’USB forme une arborescence. Un périphérique placé derrière un hub, un dock ou un écran-concentrateur dépend de ses parents.

Affichez la hiérarchie :

```bash
usbguard list-devices -t
lsusb -t
```

Vérifiez que les hubs parents sont également autorisés.

Si nécessaire :

```bash
usbguard allow-device <ID_DU_HUB> -p
```

Consultez aussi les journaux du noyau :

```bash
journalctl -k -b --no-pager | tail -n 100
```

Un périphérique autorisé par USBGuard peut rester inutilisable pour une autre raison :

- pilote absent ;
- erreur de montage ;
- périphérique défectueux ;
- alimentation insuffisante ;
- problème de câble ;
- règle udev ;
- verrouillage LUKS ;
- politique de bureau.

---

### Problème 5 : un périphérique connu est bloqué après une mise à jour

!!! failure "Symptôme"
    Un périphérique présent dans la politique depuis longtemps apparaît soudainement en `block`.

**Causes possibles :**

- ses descripteurs ont changé après une mise à jour de firmware ;
- son `hash` a changé ;
- son nom ou son numéro de série déclaré a changé ;
- ses interfaces ont changé ;
- le périphérique se trouve derrière un autre hub ;
- son port a changé alors que la règle utilise `via-port`.

Commencez par sauvegarder la politique :

```bash
sudo cp -a /etc/usbguard/rules.conf \
    /etc/usbguard/rules.conf.backup
```

Comparez ensuite le périphérique et la règle :

```bash
usbguard list-devices
usbguard list-rules
```

N’enlevez pas systématiquement le hash. Construisez plutôt une nouvelle règle suffisamment précise à partir des descripteurs actuels, puis testez-la avec un accès de secours disponible.

Si vous choisissez une règle sans hash, conservez autant que possible plusieurs critères :

```text
allow id 0951:1666 serial "60A44C..." name "DataTraveler 3.0" with-interface { 08:06:50 }
```

Le numéro de série et le nom restent falsifiables. La suppression du hash constitue donc un compromis de maintenance, pas une amélioration de sécurité.

---

### Problème 6 : la désinstallation semble bloquée

!!! failure "Symptôme"
    `apt remove` ou `apt purge` semble rester bloqué pendant l’arrêt du service.

Masquez et arrêtez d’abord les unités :

```bash
sudo systemctl mask --now usbguard.service usbguard-dbus.service
```

Puis désinstallez :

```bash
sudo apt purge usbguard
```

Après la désinstallation, vérifiez les masques éventuellement laissés dans `/etc/systemd/system/` :

```bash
ls -l /etc/systemd/system/usbguard*.service
```

Si vous souhaitez supprimer ces masques :

```bash
sudo systemctl unmask usbguard.service usbguard-dbus.service
sudo systemctl daemon-reload
```

---

## Limites de la protection

USBGuard réduit l’exposition aux périphériques USB inconnus, mais ne constitue pas une authentification matérielle et ne couvre pas tous les risques liés aux connecteurs modernes.

- Les VID, PID, noms, numéros de série et descripteurs sont déclarés par le périphérique et peuvent être imités.
- Le hash USBGuard est une empreinte de descripteurs, pas une attestation cryptographique.
- Un périphérique déjà autorisé peut devenir malveillant ou exploiter une vulnérabilité de son pilote.
- Une règle autorisant tous les claviers, tous les supports de stockage ou tous les périphériques d’un constructeur affaiblit fortement la protection.
- USBGuard ne contrôle pas le contenu des fichiers.
- USBGuard ne remplace pas un antivirus ou une solution EDR.
- USBGuard ne couvre pas nécessairement Thunderbolt, le tunneling PCIe, les modes alternatifs USB-C ou toutes les fonctions d’un dock.
- La protection ne s’applique qu’une fois le noyau, le démon et la politique opérationnels.
- Un administrateur disposant de `root` ou de `Policy=modify` peut modifier ou désactiver la politique.
- Un attaquant disposant d’un accès physique prolongé peut employer d’autres techniques que l’USB.

USBGuard doit donc être considéré comme une couche de défense parmi d’autres :

- mises à jour du noyau ;
- chiffrement du disque ;
- verrouillage de session ;
- contrôle physique ;
- moindre privilège ;
- configuration sécurisée de Thunderbolt et USB-C ;
- restrictions de montage ;
- supervision des journaux.

---

## Checklist

- [ ] Les périphériques non indispensables ou non vérifiés sont débranchés
- [ ] Les périphériques de confiance nécessaires sont branchés
- [ ] La sortie de `lsusb` et `lsusb -t` a été contrôlée
- [ ] Un second canal d’accès testé est disponible
- [ ] `usbguard.service` et `usbguard-dbus.service` sont masqués avant l’installation
- [ ] Le paquet est installé et sa version réelle a été vérifiée
- [ ] `RuleFile` ou `RuleFolder` a été vérifié dans `usbguard-daemon.conf`
- [ ] La politique initiale a été générée dans un fichier temporaire
- [ ] Chaque périphérique autorisé a été identifié et justifié
- [ ] La politique est installée en `0600 root:root`
- [ ] Le clavier, la souris, les hubs, le dock et le réseau USB nécessaires sont couverts
- [ ] Les droits IPC suivent le principe du moindre privilège
- [ ] Le service est démasqué, activé et actif
- [ ] `usbguard list-devices` fonctionne pour le compte autorisé
- [ ] Une règle permanente apparaît dans la politique chargée
- [ ] Un périphérique inconnu est bloqué
- [ ] Un périphérique connu fonctionne après rebranchement
- [ ] La machine a été redémarrée
- [ ] Les périphériques indispensables fonctionnent à l’écran de connexion
- [ ] La procédure de récupération a été vérifiée
- [ ] Les limites de sécurité d’USBGuard sont comprises
- [ ] Les composants GNOME ou notifier n’ont été activés qu’après vérification de leur présence

---

## Glossaire

BadUSB
:   Famille d’attaques exploitant la capacité d’un périphérique USB à déclarer une fonction différente de son apparence. Un objet ressemblant à une clé peut se présenter comme un clavier, une carte réseau ou un périphérique composite.

Liste blanche
:   Modèle de sécurité dans lequel tout est interdit sauf ce qui est explicitement autorisé. Le terme anglais recommandé est *allow-list*.

VID / PID
:   *Vendor ID* et *Product ID*. Ces deux entiers identifient le constructeur et le modèle déclarés par le périphérique, par exemple `046d:c52b`. Ils sont falsifiables.

Classe d’interface USB
:   Catégorie fonctionnelle déclarée par une interface USB au format `classe:sous-classe:protocole`. Un même périphérique physique peut exposer plusieurs interfaces.

HID
:   *Human Interface Device*, classe USB `03`. Cette classe couvre notamment les claviers, souris et manettes.

Périphérique composite
:   Périphérique USB exposant plusieurs interfaces ou fonctions, par exemple stockage, clavier et carte réseau dans un même appareil.

Hash USBGuard
:   Empreinte calculée à partir des descripteurs USB. Elle aide à produire une règle plus précise, mais ne prouve pas cryptographiquement l’identité physique du périphérique.

`parent-hash`
:   Empreinte des descripteurs du périphérique parent, généralement un hub. Elle ne désigne pas nécessairement un port physique unique.

`via-port`
:   Critère décrivant le chemin ou le port utilisé dans la topologie USB. Il peut rendre une règle plus restrictive, mais aussi plus sensible aux changements de câblage.

sysfs
:   Pseudo-système de fichiers monté sous `/sys`, qui expose des objets et attributs du noyau sous forme de fichiers.

Démon
:   Processus fonctionnant en arrière-plan et généralement supervisé par systemd. Dans ce document, il s’agit de `usbguard-daemon`.

IPC
:   *Inter-Process Communication*. USBGuard expose une interface IPC permettant au client `usbguard` de communiquer avec le démon selon des droits précis.

Cible implicite
:   Décision appliquée à un périphérique ne correspondant à aucune règle. Une cible `block` permet d’appliquer un modèle de liste blanche.

Attaque « evil maid »
:   Scénario dans lequel un attaquant obtient un accès physique temporaire à une machine laissée sans surveillance.

*[USB]: Universal Serial Bus
*[HID]: Human Interface Device
*[IPC]: Inter-Process Communication
*[VID]: Vendor ID
*[PID]: Product ID
*[ACL]: Access Control List
*[FIDO2]: Fast IDentity Online 2
*[IPMI]: Intelligent Platform Management Interface
*[EDR]: Endpoint Detection and Response

---

## Ressources

- [Site officiel USBGuard](https://usbguard.github.io/) — documentation et présentation du projet
- [Documentation de configuration](https://usbguard.github.io/documentation/configuration) — configuration du démon et contrôle d’accès IPC
- [`usbguard(1)` — manuel Debian](https://manpages.debian.org/testing/usbguard/usbguard.1.en.html) — commandes et options du client
- [`usbguard-rules.conf(5)` — manuel Debian](https://manpages.debian.org/testing/usbguard/usbguard-rules.conf.5.en.html) — grammaire des règles
- [`usbguard-daemon.conf(5)` — manuel Debian](https://manpages.debian.org/testing/usbguard/usbguard-daemon.conf.5.en.html) — paramètres du démon
- [Red Hat — Protecting systems against intrusive USB devices](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/security_hardening/protecting-systems-against-intrusive-usb-devices_security-hardening) — recommandations de durcissement
- [USBGuard sur ArchWiki](https://wiki.archlinux.org/title/USBGuard) — exemples de configuration et intégration au bureau
- [Dépôt GitHub du projet](https://github.com/USBGuard/usbguard) — sources, versions et suivi des anomalies
