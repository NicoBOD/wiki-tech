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

    Une attention particulière est portée à trois comportements propres au paquet Ubuntu, qui prennent en défaut la plupart des procédures génériques : l’accès IPC complet accordé d’office au groupe `plugdev`, l’ajout automatique d’un critère `via-port` aux périphériques sans numéro de série, et le chargement effectif de `/etc/usbguard/rules.d/`.

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

!!! danger "Ce que le paquet Ubuntu a déjà fait à votre place"
    Sur Ubuntu 24.04, le script de post-installation du paquet n’est pas passif. S’il ne trouve pas de fichier `/etc/usbguard/rules.conf`, il exécute :

    ```sh
    usbguard generate-policy >> /etc/usbguard/rules.conf || true
    usbguard add-user -g plugdev --devices=modify,list,listen --policy=list --exceptions=listen
    ```

    Deux conséquences à retenir :

    - une politique a **déjà** été générée à partir des périphériques branchés au moment de l’installation. L’étape 5 la remplacera, mais vérifiez dès maintenant qu’elle n’est pas vide, car le `|| true` masque un éventuel échec de génération — et une politique vide est exactement ce qui verrouille clavier et souris au démarrage du service ;
    - un fichier de contrôle d’accès IPC a **déjà** été créé pour le groupe `plugdev`. Ce point est traité à l’étape 4.

    ```bash
    sudo wc -l /etc/usbguard/rules.conf
    sudo ls -l /etc/usbguard/IPCAccessControl.d/
    ```

!!! success "Le masque survit bien à l’installation"
    Le script du paquet appelle `deb-systemd-helper unmask` sur les deux unités. Cet utilitaire refuse toutefois de retirer un masque qu’il n’a pas posé lui-même : il exige la présence d’un fichier d’état dans `/var/lib/systemd/deb-systemd-helper-masked/`. Un masque créé par l’administrateur avec `systemctl mask` est donc conservé.

    Une seule exception : si `usbguard` avait déjà été installé puis retiré par `apt remove` sans purge, le masque appartiendrait au paquet et serait levé, ce qui démarrerait le service. La vérification `systemctl is-enabled` ci-dessus détecte ce cas.

!!! note "Version et dépôt du paquet"
    Ubuntu 24.04 fournit `usbguard` 1.1.2 et `usbguard-notifier` 0.1.0, tous deux dans le composant **`universe`**. Il est actif par défaut sur une installation Desktop ou Server standard, mais pas nécessairement sur une image minimale ou personnalisée.

    Le numéro de révision Ubuntu peut évoluer avec les mises à jour : utilisez toujours les commandes ci-dessus plutôt que de supposer une version précise.

---

### Étape 4 : examiner la configuration du démon

Affichez les paramètres principaux :

```bash
sudo grep -E '^[[:space:]]*(RuleFile|RuleFolder|ImplicitPolicyTarget|PresentDevicePolicy|PresentControllerPolicy|InsertedDevicePolicy|AuthorizedDefault|RestoreControllerDeviceState|DeviceRulesWithPort|IPCAllowedUsers|IPCAllowedGroups|IPCAccessControlFiles|AuditBackend|AuditFilePath)=' \
    /etc/usbguard/usbguard-daemon.conf
```

Sur une Ubuntu 24.04 fraîchement installée, le paquet livre exactement ceci :

```text
RuleFile=/etc/usbguard/rules.conf
RuleFolder=/etc/usbguard/rules.d/
ImplicitPolicyTarget=block
PresentDevicePolicy=apply-policy
PresentControllerPolicy=keep
InsertedDevicePolicy=apply-policy
AuthorizedDefault=none
RestoreControllerDeviceState=false
DeviceManagerBackend=uevent
IPCAllowedUsers=root
IPCAllowedGroups=root plugdev
IPCAccessControlFiles=/etc/usbguard/IPCAccessControl.d/
DeviceRulesWithPort=false
AuditBackend=FileAudit
AuditFilePath=/var/log/usbguard/usbguard-audit.log
HidePII=false
```

Les valeurs de `ImplicitPolicyTarget`, `PresentDevicePolicy` et `InsertedDevicePolicy` sont celles attendues pour une liste blanche. **Les deux lignes `IPCAllowedUsers` et `IPCAllowedGroups` méritent en revanche une attention particulière**, traitée plus bas dans cette étape.

Les lignes exactes peuvent différer selon la version du paquet. Si un paramètre n’est pas présent, consultez sa valeur par défaut dans le manuel installé :

```bash
man usbguard-daemon.conf
```

#### `RuleFile` et `RuleFolder` sont tous les deux actifs sur Ubuntu

Contrairement à une idée répandue, ces deux directives ne s’excluent pas. Ubuntu 24.04 les configure **toutes les deux**, et USBGuard 1.1.2 les traite de façon **additive** : le démon construit une liste de jeux de règles en chargeant d’abord `RuleFile`, puis chaque fichier de `RuleFolder` dans l’ordre alphanumérique.

Deux conséquences pratiques :

- `/etc/usbguard/rules.conf` étant chargé **en premier**, ses règles restent prioritaires puisque la première règle correspondante l’emporte. La politique produite à l’étape 5 fait donc bien autorité.
- `/etc/usbguard/rules.d/` **est bel et bien lu**. Le dossier est vide à l’installation, mais tout fichier qui y sera déposé participera à la politique.

!!! danger "Un fichier mal protégé dans `rules.d/` empêche le démon de démarrer"
    Au chargement, le démon applique un contrôle de permissions à `usbguard-daemon.conf`, à `RuleFile` **et à chaque fichier présent dans `RuleFolder`**. Un fichier qui porte le moindre bit de permission pour le groupe ou pour les autres — les `0644` par défaut, typiquement — provoque une exception et **le service refuse de démarrer**.

    L’unité livrée par Ubuntu lance `usbguard-daemon -f -s -c /etc/usbguard/usbguard-daemon.conf`, sans l’option `-P` qui désactiverait ce contrôle : la vérification est donc bien active.

    Tout fichier déposé dans `/etc/usbguard/rules.d/` doit être en `0600 root:root`, au même titre que `rules.conf` :

    ```bash
    sudo install -m 0600 -o root -g root source.conf /etc/usbguard/rules.d/50-exemple.conf
    sudo find /etc/usbguard -type f ! -perm 0600 -printf '%m %p\n'
    ```

    La dernière commande ne doit rien afficher. Notez que le démon qui refuse de démarrer laisse le système **sans aucune protection USB** : c’est une panne silencieuse, à surveiller dans les journaux.

#### Les droits IPC déjà accordés par Ubuntu

C’est le point le plus important de cette étape, et celui qui invalide le plus souvent le modèle de sécurité que l’on croit avoir mis en place.

La configuration livrée contient :

```text
IPCAllowedUsers=root
IPCAllowedGroups=root plugdev
```

`IPCAllowedUsers` et `IPCAllowedGroups` sont les directives **héritées** de contrôle d’accès. Le manuel `usbguard-daemon.conf(5)` les documente sous le titre « Legacy » avec cette formulation sans ambiguïté : *« Example configuration allowing **full IPC access** »*. Elles n’accordent pas un droit partiel : dans le code d’USBGuard 1.1.2, elles appliquent l’autorisation par défaut `Section::ALL, Privilege::ALL`.

À cela s’ajoute le fichier de contrôle d’accès `:plugdev` créé automatiquement par le script de post-installation.

!!! danger "Sur un poste Ubuntu par défaut, votre compte peut désactiver la liste blanche sans mot de passe"
    Le premier compte créé lors de l’installation d’Ubuntu appartient au groupe `plugdev`. Vérifiez-le :

    ```bash
    id -nG | tr ' ' '\n' | grep -x plugdev
    ```

    Si ce groupe apparaît, alors **sans `sudo`** ce compte peut notamment :

    ```bash
    usbguard allow-device <ID> -p                      # ajouter une règle permanente
    usbguard set-parameter ImplicitPolicyTarget allow  # neutraliser toute la liste blanche
    ```

    La deuxième commande fait tomber le modèle liste blanche dans son intégralité. Tant que cette configuration est en place, l’étape 6 et le principe du moindre privilège n’ont aucun effet réel.

Pour retrouver un contrôle d’accès cohérent, neutralisez la directive héritée et retirez l’autorisation accordée au groupe `plugdev`. Conservez `IPCAllowedUsers=root`, qui permet à `root` d’utiliser l’IPC et donc à vos commandes `sudo usbguard …` de fonctionner :

```bash
sudo cp -a /etc/usbguard/usbguard-daemon.conf \
    /etc/usbguard/usbguard-daemon.conf.backup

sudo sed -i 's/^IPCAllowedGroups=/#IPCAllowedGroups=/' \
    /etc/usbguard/usbguard-daemon.conf

sudo usbguard remove-user plugdev -g
```

Vérifiez le résultat :

```bash
sudo grep -nE '^[[:space:]]*#?IPCAllowed' /etc/usbguard/usbguard-daemon.conf
sudo ls -l /etc/usbguard/IPCAccessControl.d/
```

Les droits nominatifs seront ensuite accordés explicitement à l’étape 6. Comme les fichiers de contrôle d’accès et la configuration ne sont lus qu’au démarrage du démon, ces modifications ne prendront effet qu’à l’étape 7.

!!! note "Si vous préférez conserver l’accès de `plugdev`"
    C’est un choix défendable sur un poste strictement personnel, où le compte concerné peut de toute façon devenir `root`. Faites-le alors sciemment, et non par méconnaissance : sur une machine partagée, cela revient à confier la politique USB à tous les comptes du groupe.

---

### Étape 5 : générer la politique initiale

Générez la politique dans un fichier de travail accessible au seul `root` :

```bash
sudo install -d -m 0700 -o root -g root /root/usbguard
sudo sh -c 'umask 077; usbguard generate-policy > /root/usbguard/rules.conf.new'
```

Relisez intégralement son contenu — en lecture seule, pour éviter toute modification involontaire :

```bash
sudo less /root/usbguard/rules.conf.new
```

!!! danger "Par défaut, `generate-policy` lie déjà vos règles à un port physique"
    C’est le piège le plus coûteux de cette procédure, car il ne se manifeste que des semaines plus tard.

    Sans aucune option, `usbguard generate-policy` ajoute un attribut `via-port` à **tout périphérique qui ne déclare pas de numéro de série**. Le manuel `usbguard(1)` le dit à propos de `--with-ports` : *« By default, port specific rules are generated only for devices which do not export an iSerial value »*, et le générateur d’USBGuard 1.1.2 active bien ce comportement par défaut.

    Or la majorité des claviers, souris, récepteurs sans fil et hubs d’entrée de gamme ne déclarent aucun numéro de série. **Leurs règles seront donc liées au port sur lequel ils étaient branchés pendant la génération**, et changer de prise suffira à les faire bloquer.

    Mesurez l’ampleur du phénomène avant d’aller plus loin :

    ```bash
    sudo grep -c 'via-port' /root/usbguard/rules.conf.new
    sudo grep 'via-port' /root/usbguard/rules.conf.new
    ```

    Deux choix s’offrent alors à vous :

    - **conserver ce comportement** : plus restrictif, c’est une réelle protection contre un périphérique qui usurperait l’identité d’un matériel connu, mais vous devez accepter qu’un changement de prise, l’ajout d’un hub ou le remplacement d’un dock bloque le périphérique ;
    - **le désactiver** avec `-P` / `--no-ports-sn`, pour une politique stable quel que soit le port :

        ```bash
        sudo sh -c 'umask 077; usbguard generate-policy --no-ports-sn > /root/usbguard/rules.conf.new'
        ```

    Sur un poste de bureau dont on rebranche régulièrement le matériel, la seconde option évite la grande majorité des blocages inattendus. Sur une machine au câblage figé, la première est préférable.

    Quel que soit votre choix, faites-le **maintenant** et en conscience : c’est ce détail qui détermine si votre clavier fonctionnera encore le jour où vous le brancherez sur une autre prise.

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
    /root/usbguard/rules.conf.new \
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
    Lors d’une modification ultérieure, générez toujours la nouvelle politique dans un fichier de travail réservé à `root`. Relisez-la avant de remplacer le fichier utilisé par le démon.

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

#### Maîtriser le critère `via-port`

Trois comportements sont possibles, et il est essentiel de savoir lequel s’applique :

| Commande | Périphériques recevant un `via-port` |
|----------|--------------------------------------|
| `usbguard generate-policy` | **Ceux sans numéro de série** — comportement par défaut |
| `usbguard generate-policy --with-ports` (`-p`) | **Tous**, y compris ceux qui déclarent un numéro de série |
| `usbguard generate-policy --no-ports-sn` (`-P`) | **Aucun** |

`--with-ports` convient à une machine dont le câblage ne bouge jamais et pour laquelle on souhaite la politique la plus stricte possible.

!!! warning "Inconvénient de `via-port`"
    Une règle liée à un port cesse de correspondre après :

    - un changement de port ;
    - l’ajout ou le retrait d’un hub ;
    - le remplacement d’un dock ;
    - une modification de la topologie USB ;
    - certains changements de firmware ou de matériel.

    Rappelez-vous que ce risque concerne aussi la génération par défaut, et pas seulement `--with-ports`.

!!! warning "Supprimer `via-port` ne rend pas un périphérique totalement indépendant de sa prise"
    Même généré avec `--no-ports-sn`, chaque règle conserve un attribut `parent-hash`, et le manuel `usbguard-rules.conf(5)` est explicite : *« Match a hash of the parent device »*. C’est donc bien un critère de correspondance, pas une simple annotation.

    Le parent d’un périphérique branché directement sur la carte mère est le concentrateur racine du contrôleur USB concerné. En pratique :

    - déplacer un périphérique vers une autre prise **du même contrôleur** ne change pas le `parent-hash` : la règle continue de correspondre ;
    - le déplacer vers une prise servie par **un autre contrôleur** change le `parent-hash` : la règle ne correspond plus et le périphérique est bloqué.

    Une machine possédant deux contrôleurs xHCI a donc deux « zones » de prises entre lesquelles un périphérique autorisé ne circule pas librement. Repérez-les avant de conclure qu’un déplacement est sans risque :

    ```bash
    lsusb -t
    ```

    Chaque ligne `/: Bus 0XX...Port 001: Dev 001, Class=root_hub` correspond à un contrôleur distinct.

!!! note "Les règles permanentes ajoutées plus tard ne suivent pas la même règle"
    La configuration Ubuntu contient `DeviceRulesWithPort=false`. Les règles créées à chaud par `usbguard allow-device <ID> -p` **n’incluent donc pas** de `via-port`, contrairement à celles produites par `generate-policy`.

    Votre politique peut ainsi mélanger deux styles de règles. Ce n’est pas une anomalie, mais cela explique qu’un périphérique autorisé après coup se révèle plus tolérant au changement de prise que ceux de la politique initiale.

#### Générer sans hash

Il est possible de générer une politique sans empreintes :

```bash
sudo sh -c 'umask 077; usbguard generate-policy --no-hashes > /root/usbguard/rules.conf.new'
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

!!! warning "Cette règle doit impérativement être placée en tête de la politique"
    La première règle correspondante l’emporte. Une règle `reject` située **après** les règles `allow` ne servirait donc à rien.

    Or `usbguard append-rule` ajoute en fin de politique et ne propose que l’option `-a` / `--after <ID>` : il n’existe pas de `--before`. La façon fiable de procéder est d’écrire la règle en première ligne du fichier de politique, démon arrêté :

    ```bash
    sudo systemctl stop usbguard.service
    sudo cp -a /etc/usbguard/rules.conf /etc/usbguard/rules.conf.backup
    sudo sed -i '1i reject with-interface all-of { 08:*:* 03:*:* }' /etc/usbguard/rules.conf
    sudo systemctl start usbguard.service
    usbguard list-rules
    ```

    Relisez la politique obtenue avant de rebrancher quoi que ce soit d’indispensable.

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

C’est la méthode recommandée, car elle permet de descendre à la granularité de la section et du privilège, là où les directives héritées `IPCAllowedUsers` et `IPCAllowedGroups` accordent tout ou rien.

!!! info "Cette étape n’a de sens qu’après le nettoyage de l’étape 4"
    Si vous n’avez pas neutralisé `IPCAllowedGroups=root plugdev` ni retiré le fichier `:plugdev`, les droits accordés ici ne restreignent rien : le groupe `plugdev` conserve un accès complet à l’IPC, y compris la modification des paramètres du démon.

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

!!! note "Sur la syntaxe de `add-user`"
    Le nom est un argument positionnel et `--group` (`-g`) indique qu’il désigne un groupe plutôt qu’un utilisateur. L’analyse des options étant réalisée par `getopt_long` sans contrainte d’ordre, les deux écritures suivantes sont équivalentes :

    ```bash
    usbguard add-user NOM_DU_GROUPE --group --devices ALL
    usbguard add-user -g NOM_DU_GROUPE --devices=ALL
    ```

    Le mot-clé `ALL` est officiellement documenté : *« You can also use ALL instead of privileges to automatically assign all relevant privileges to a given section »*. Les privilèges disponibles sont `list`, `modify` et `listen`.

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

Sur Ubuntu 24.04, ce paquet livre une unité **utilisateur** `/usr/lib/systemd/user/usbguard-notifier.service`, et aucun fichier XDG Autostart. Vous pouvez le confirmer :

```bash
dpkg -L usbguard-notifier | grep -E 'systemd|autostart|\.desktop$'
systemctl --user list-unit-files 'usbguard*'
```

L’activation se fait donc au niveau de la session :

```bash
systemctl --user enable --now usbguard-notifier.service
systemctl --user status usbguard-notifier.service
```

Le notifier doit disposer du droit IPC lui permettant d’écouter les événements, au minimum :

```text
Devices=listen
```

!!! note "Droits nécessaires après le nettoyage de l’étape 4"
    Tant que `plugdev` disposait d’un accès complet, le notifier fonctionnait sans configuration. Ce n’est plus le cas une fois cet accès retiré.

    Si votre compte appartient au groupe auquel vous avez accordé les droits à l’étape 6, il n’y a rien à faire. Sinon, accordez le strict nécessaire à votre seul compte :

    ```bash
    sudo usbguard add-user "$USER" --devices list,listen --exceptions listen
    sudo systemctl restart usbguard.service
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

!!! danger "Activer le service D-Bus ouvre une voie polkit sans authentification"
    Le paquet Ubuntu installe `/usr/share/polkit-1/rules.d/org.usbguard1.rules`, dont le commentaire est explicite : *« Allow users in plugdev and sudo group to run usbguard actions without authentication »*.

    Cette règle accorde `polkit.Result.YES`, c’est-à-dire **aucune demande de mot de passe**, à tout membre des groupes `plugdev` ou `sudo` disposant d’une session locale active, pour trois actions :

    | Action polkit | Effet |
    |---------------|-------|
    | `org.usbguard1.setParameter` | Modifier un paramètre du démon, `ImplicitPolicyTarget` compris |
    | `org.usbguard.Policy1.appendRule` | Ajouter une règle à la politique |
    | `org.usbguard.Devices1.applyDevicePolicy` | Autoriser ou bloquer un périphérique |

    Tant que `usbguard-dbus.service` reste arrêté, cette voie d’accès n’existe pas. Le nettoyage réalisé à l’étape 4 ne la referme pas non plus : il porte sur l’IPC, alors que cette règle s’applique à l’interface D-Bus.

    Si vous activez le service D-Bus, inspectez la règle et, le cas échéant, restreignez-la avec un fichier de priorité supérieure dans `/etc/polkit-1/rules.d/` :

    ```bash
    cat /usr/share/polkit-1/rules.d/org.usbguard1.rules
    ```

Si `usbguard-dbus.service` et les clés correspondantes existent, et après avoir pris connaissance de l’avertissement ci-dessus :

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

!!! warning "Ces commandes exigent le privilège `Parameters`, que l’étape 6 n’accorde pas"
    Le contrôle d’accès recommandé à l’étape 6 couvre les sections `Devices`, `Policy` et `Exceptions`, mais **pas** `Parameters`. Un compte pourtant autorisé obtient donc :

    ```text
    IPC ERROR: request id=1: IPC method: usbguard.IPC.getParameter: Permission denied
    ```

    Ce n’est pas une anomalie : ne pas accorder `Parameters=modify` est précisément ce qui empêche un processus tournant sous votre compte d’exécuter `usbguard set-parameter ImplicitPolicyTarget allow` et de désarmer la liste blanche.

    Deux façons de procéder, au choix :

    ```bash
    # soit interroger le démon en tant que root
    sudo usbguard get-parameter ImplicitPolicyTarget

    # soit accorder la lecture seule des paramètres, sans le droit de les modifier
    sudo usbguard add-user sudo --group \
        --devices ALL --policy modify,list --exceptions listen --parameters list
    sudo systemctl restart usbguard.service
    ```

    N’accordez `--parameters modify` que si vous en avez un besoin précis.

```bash
sudo usbguard get-parameter ImplicitPolicyTarget
sudo usbguard get-parameter PresentDevicePolicy
sudo usbguard get-parameter InsertedDevicePolicy
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

### Contrôle d’accès IPC

C’est la vérification que l’on oublie le plus souvent, alors qu’elle conditionne la valeur réelle de toute la politique.

```bash
sudo grep -nE '^[[:space:]]*#?(IPCAllowedUsers|IPCAllowedGroups)=' /etc/usbguard/usbguard-daemon.conf
sudo ls -l /etc/usbguard/IPCAccessControl.d/
```

Résultat attendu après le nettoyage de l’étape 4 :

- `IPCAllowedGroups` est commentée, ou ne contient plus `plugdev` ;
- `IPCAllowedUsers=root` subsiste ;
- le dossier `IPCAccessControl.d/` ne contient plus `:plugdev`, mais uniquement les accès que vous avez accordés.

Confirmez ensuite qu’un compte non privilégié **ne peut pas** désarmer la politique. Depuis un compte qui ne fait partie d’aucun groupe autorisé :

```bash
usbguard set-parameter ImplicitPolicyTarget allow
```

La commande doit échouer sur une erreur d’accès. Si elle aboutit, la liste blanche vient d’être neutralisée — remettez immédiatement la valeur `block` et reprenez l’étape 4 :

```bash
sudo usbguard set-parameter ImplicitPolicyTarget block
```

### Permissions des fichiers

```bash
sudo find /etc/usbguard -type f ! -perm 0600 -printf '%m %p\n'
```

Cette commande ne doit rien afficher : un seul fichier trop permissif dans `/etc/usbguard/` ou `/etc/usbguard/rules.d/` empêche le démon de démarrer.

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
| `usbguard list-devices -t` | Afficher les périphériques sous forme d’arborescence (`--tree`) |
| `usbguard allow-device <ID>` | Autoriser temporairement un périphérique |
| `usbguard allow-device <ID> -p` | Autoriser un périphérique et ajouter une règle persistante |
| `usbguard block-device <ID> -p` | Bloquer un périphérique avec une règle persistante |
| `usbguard reject-device <ID>` | Rejeter logiquement un périphérique |
| `usbguard list-rules` | Afficher la politique chargée et les identifiants de règles |
| `usbguard list-rules -d` | Afficher, pour chaque règle, les périphériques qu’elle concerne (`--show-devices`) |
| `usbguard append-rule '<règle>'` | Ajouter une règle **à la fin** de la politique |
| `usbguard append-rule '<règle>' -a <ID>` | Insérer une règle après celle portant cet identifiant (il n’existe pas de `--before`) |
| `usbguard remove-rule <ID>` | Supprimer une règle à partir de son identifiant |
| `usbguard generate-policy` | Générer une politique à partir des périphériques présents |
| `usbguard generate-policy --no-hashes` | Générer une politique sans empreintes |
| `usbguard generate-policy --with-ports` | Lier **tous** les périphériques à leur port (`via-port`) |
| `usbguard generate-policy --no-ports-sn` | N’ajouter `via-port` à **aucun** périphérique |
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
| `/etc/usbguard/rules.d/` | Politiques additionnelles — **actif par défaut sur Ubuntu 24.04** ; chaque fichier doit être en `0600 root:root` |
| `/etc/usbguard/IPCAccessControl.d/` | Contrôles d’accès IPC pour les utilisateurs et les groupes |
| `/usr/lib/systemd/system/usbguard.service` | Unité du démon ; le contrôle de permissions est actif faute de l’option `-P` |
| `/usr/share/polkit-1/rules.d/org.usbguard1.rules` | Règle polkit accordant `plugdev` et `sudo` sans authentification, **via D-Bus uniquement** |
| `/var/log/usbguard/usbguard-audit.log` | Journal d’audit — **actif par défaut sur Ubuntu 24.04** |
| `/etc/logrotate.d/usbguard` | Rotation du journal d’audit ; voir l’avertissement ci-dessous |
| `/var/log/journal/` | Journaux persistants de systemd, lorsqu’ils sont activés |

### Paramètres clés de `usbguard-daemon.conf`

| Paramètre | Valeur habituelle à vérifier | Signification |
|-----------|------------------------------|---------------|
| `RuleFile` | `/etc/usbguard/rules.conf` | Fichier principal de politique, chargé en premier |
| `RuleFolder` | `/etc/usbguard/rules.d/` | Politiques additionnelles, chargées **après** `RuleFile` et en ordre alphanumérique |
| `ImplicitPolicyTarget` | `block` | Décision appliquée lorsqu’aucune règle ne correspond |
| `PresentDevicePolicy` | `apply-policy` | Traitement des périphériques présents au démarrage du démon |
| `PresentControllerPolicy` | `keep` | Traitement des contrôleurs USB déjà présents |
| `InsertedDevicePolicy` | `apply-policy` | Traitement des périphériques branchés à chaud |
| `AuthorizedDefault` | `none` | État d’autorisation appliqué par le noyau avant toute décision d’USBGuard |
| `RestoreControllerDeviceState` | `false` | Restauration éventuelle de l’état antérieur des contrôleurs lors de l’arrêt propre du démon |
| `DeviceRulesWithPort` | `false` | Ajout ou non d’un `via-port` aux règles créées à chaud via l’IPC |
| `IPCAllowedUsers` | `root` | Directive héritée accordant un accès IPC **complet** aux utilisateurs listés |
| `IPCAllowedGroups` | `root plugdev` | Directive héritée accordant un accès IPC **complet** aux groupes listés — à revoir, voir l’étape 4 |
| `IPCAccessControlFiles` | `/etc/usbguard/IPCAccessControl.d/` | Méthode recommandée, granulaire par section et par privilège |
| `AuditBackend` | `FileAudit` | Destination du journal d’audit |

!!! warning "Conservez de préférence `RestoreControllerDeviceState=false`"
    Avec `true`, USBGuard tente de restaurer l’état antérieur des contrôleurs lors d’un **arrêt propre** du démon. Si cet état était permissif, de nouveaux périphériques pourraient alors être autorisés après l’arrêt du service.

    Un processus interrompu brutalement ne peut généralement pas exécuter cette restauration. Il est donc incorrect d’affirmer qu’un simple crash restaure automatiquement un état permissif.

    La valeur `false` reste néanmoins préférable pour conserver un comportement aussi proche que possible du « fail closed » après l’arrêt du service.

!!! warning "Le journal d’audit devient lisible par tous après la première rotation"
    Le démon crée `/var/log/usbguard/usbguard-audit.log` avec un masque `0077`, donc en `0600`. Mais le fichier `/etc/logrotate.d/usbguard` livré par le paquet contient `create 644 root root` : **après la première rotation hebdomadaire, le journal est lisible par n’importe quel compte local**.

    Comme `HidePII=false` est également la valeur par défaut, ce journal contient les noms et numéros de série des périphériques branchés. Si cela vous gêne, resserrez la directive :

    ```bash
    sudo sed -i 's/create 644 root root/create 640 root adm/' /etc/logrotate.d/usbguard
    sudo logrotate --debug /etc/logrotate.d/usbguard
    ```

    L’option `--debug` simule la rotation sans l’exécuter.

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

### Problème 7 : le démon refuse de démarrer après une modification de la politique

!!! failure "Symptôme"
    `usbguard.service` passe en `failed` au démarrage, et les périphériques USB fonctionnent tous — y compris ceux qui devraient être bloqués.

C’est une panne qui **ouvre** la protection au lieu de la fermer : sans démon, aucune politique n’est appliquée. Elle passe donc facilement inaperçue.

La cause la plus fréquente est un contrôle de permissions en échec. Le démon vérifie `usbguard-daemon.conf`, le fichier `RuleFile` et **chaque fichier présent dans `RuleFolder`** ; tout bit de permission accordé au groupe ou aux autres provoque une exception au chargement.

Identifiez le fichier fautif :

```bash
journalctl -u usbguard.service -b --no-pager | grep -i 'permission'
sudo find /etc/usbguard -type f ! -perm 0600 -printf '%m %p\n'
```

Corrigez puis redémarrez :

```bash
sudo chmod 0600 /etc/usbguard/rules.conf /etc/usbguard/usbguard-daemon.conf
sudo find /etc/usbguard/rules.d -type f -exec chmod 0600 {} +
sudo chown -R root:root /etc/usbguard
sudo systemctl restart usbguard.service
systemctl is-active usbguard.service
```

Les autres causes possibles sont une erreur de syntaxe dans une règle et un `RuleFile` inexistant :

```bash
sudo usbguard-rule-parser -f /etc/usbguard/rules.conf
```

!!! tip "Surveillez cette panne dans la durée"
    Puisqu’elle est silencieuse, ajoutez sa détection à vos vérifications périodiques :

    ```bash
    systemctl is-active usbguard.service || echo 'ALERTE : USBGuard ne tourne pas'
    ```

---

## Retour d’expérience : une première installation réelle

Cette section consigne le déroulé d’une mise en place effective sur un poste de bureau Ubuntu 24.04, et les trois surprises rencontrées. Les numéros de série et les empreintes sont tronqués.

### Le contexte

Un poste fixe équipé de six périphériques USB — webcam, adaptateur Bluetooth, casque audio avec contrôles HID, récepteur sans fil clavier/souris, souris filaire, clavier mécanique — répartis sur deux contrôleurs xHCI distincts.

Deux caractéristiques rendaient la manœuvre délicate :

- **aucun clavier PS/2**, donc pas de périphérique d’entrée échappant à USBGuard ;
- **un seul de ces périphériques déclarait un numéro de série** : la webcam. Les deux claviers n’en avaient aucun.

La seconde caractéristique est décisive. Avec une génération par défaut, les deux claviers auraient été épinglés à leur prise. La politique a donc été produite avec `--no-ports-sn`.

Le canal de secours a été vérifié avant tout : la session SSH transitait par une carte réseau PCI, insensible à USBGuard. Sur une machine dont l’interface réseau est un adaptateur USB, cette vérification n’est pas optionnelle.

### Le résultat

La politique générée comptait dix règles : six périphériques et quatre concentrateurs racine, à raison de deux par contrôleur, l’un pour l’USB 2.0 et l’autre pour l’USB 3.0.

Le test avec une clé USB inconnue a fonctionné du premier coup :

```text
21: block id ffff:5678 serial "65113912…" name "Disk 2.0" hash "ZWNWOD08xS…" with-interface 08:06:50
```

L’identifiant constructeur `ffff` mérite d’ailleurs un mot : aucun constructeur légitime ne se voit attribuer cette valeur. C’est le genre de détail qu’une liste blanche par empreinte rend visible.

### Surprise n° 1 : `list-devices` affiche `via-port` même sans règle `via-port`

C’est le piège le plus déroutant, car il donne l’impression que `--no-ports-sn` n’a pas fonctionné.

Après activation, `usbguard list-devices` affichait un `via-port` sur chaque ligne :

```text
20: allow id 1038:161a serial "" name "…" hash "CvHZUDg/dG…" via-port "1-14" with-interface { 03:01:01 … }
```

Il n’y avait pourtant aucun `via-port` dans la politique. **Les deux commandes ne montrent pas la même chose** :

| Commande | Ce qui est affiché |
|----------|--------------------|
| `usbguard list-devices` | La description complète de chaque **périphérique** présent, avec tous ses attributs observés — dont la prise qu’il occupe réellement. Le mot en tête de ligne est son **état** courant. |
| `usbguard list-rules` | Les **règles** de la politique chargée, c’est-à-dire les critères réellement utilisés pour décider. |

Pour savoir si votre politique dépend des ports, il faut donc interroger les règles, jamais les périphériques :

```bash
usbguard list-rules | grep -c 'via-port'
```

### Surprise n° 2 : `usbguard get-parameter` refusé malgré des droits IPC corrects

La vérification des paramètres actifs échouait alors que `usbguard list-devices` et `list-rules` fonctionnaient sans `sudo` :

```text
IPC ERROR: request id=1: IPC method: usbguard.IPC.getParameter: Permission denied
```

La cause est le contrôle d’accès de l’étape 6, qui couvre `Devices`, `Policy` et `Exceptions` mais laisse la section `Parameters` vide. Ce comportement est traité en détail dans la section « Paramètres actifs ».

C’est en réalité une bonne nouvelle : c’est exactement ce qui empêche un processus tournant sous votre compte de désarmer la politique d’une seule commande.

### Surprise n° 3 : `--no-ports-sn` ne suffit pas à libérer un périphérique de sa prise

Chaque règle conservait un `parent-hash`, qui reste un critère de correspondance. Sur cette machine à deux contrôleurs, déplacer un périphérique d’une prise à l’autre du même contrôleur est sans effet, mais le brancher sur une prise servie par l’autre contrôleur le ferait basculer en `block`. Voir l’avertissement de la section consacrée à `via-port`.

### Ce qui a le mieux fonctionné : une activation à retour arrière automatique

Plutôt que de démarrer le démon et d’espérer, l’activation a été enveloppée dans un test dont l’échec se corrige tout seul. L’idée : demander une confirmation **au clavier**, avec un délai. Si le clavier vient d’être bloqué, la confirmation est impossible, le délai expire et la protection se retire.

```bash
systemctl unmask usbguard.service
systemctl enable --now usbguard.service

if read -r -t 90 -p "Votre clavier fonctionne-t-il ? [oui] " R && [ "$R" = oui ]; then
    echo "Protection conservée."
else
    echo "Aucune réponse — retour arrière."
    systemctl mask --now usbguard.service usbguard-dbus.service
    for f in /sys/bus/usb/devices/*/authorized_default; do echo 1 > "$f" 2>/dev/null; done
    for f in /sys/bus/usb/devices/*/authorized;         do echo 1 > "$f" 2>/dev/null; done
fi
```

Les deux boucles finales sont la partie importante : **arrêter le démon ne réautorise pas les périphériques déjà bloqués**. Sans elles, il faudrait débrancher et rebrancher le matériel, ou redémarrer.

Ce filet ne dispense pas de la session SSH : si l’activation échoue d’une façon imprévue, avant même d’atteindre l’invite, seul un accès distant permet de reprendre la main.

### Le redémarrage, contrôle décisif

Le blocage d’un périphérique inconnu et le rebranchement du matériel de confiance se testent immédiatement. Mais **seul le redémarrage confirme que le clavier répondra à l’écran de connexion**, lorsque la politique est appliquée aux périphériques présents au démarrage du démon plutôt qu’à des branchements à chaud.

Sur l’installation décrite ici, il s’est déroulé sans incident : démon démarré une vingtaine de secondes après le début de l’amorçage, dix périphériques reconnus, dix autorisés, aucun bloqué.

```bash
systemctl is-active usbguard.service; systemctl is-enabled usbguard.service
usbguard list-devices --blocked      # doit ne rien afficher
```

Le journal permet de confirmer que chaque périphérique a bien été évalué au démarrage. Recherchez les entrées `type='Device.Present'` assorties de `target.new='allow'` :

```bash
journalctl -u usbguard.service -b --no-pager | grep "Device.Present"
```

!!! warning "Le redémarrage coupe aussi votre session SSH"
    C’est une évidence que l’on oublie : le filet de sécurité disparaît pendant l’opération même où l’on en aurait le plus besoin. Si le clavier ne revenait pas, il faudrait rouvrir une session SSH depuis l’autre machine — ce qui suppose que le service SSH démarre correctement et que le réseau monte sans intervention.

    Vérifiez donc **avant** de redémarrer que `ssh` est bien activé au démarrage :

    ```bash
    systemctl is-enabled ssh
    ```

### Surprise n° 4 : sur le matériel bas de gamme, `id` et `name` ne distinguent rien

Après quelques ajouts, la politique était passée de dix à dix-huit règles. Cinq des règles ajoutées correspondaient à cinq clés USB **physiquement distinctes**, d’un même modèle chinois d’entrée de gamme :

```text
allow id ffff:5678 serial "65113912…" name "Disk 2.0" hash "ZWNWOD08xS…" with-interface 08:06:50
allow id ffff:5678 serial "86219711…" name "Disk 2.0" hash "oWa6qVP8uz…" with-interface 08:06:50
allow id ffff:5678 serial "39274311…" name "Disk 2.0" hash "IpjRcqvOO7…" with-interface 08:06:50
allow id ffff:5678 serial "67576210…" name "Disk 2.0" hash "jfX9/9DdBD…" with-interface 08:06:50
allow id ffff:5678 serial "60366710…" name "Disk 2.0" hash "x1j39iAsa2…" with-interface 08:06:50
```

Identifiant identique, nom identique, cinq numéros de série différents. C’est le comportement normal d’un lot de clés bâties sur le même contrôleur générique — et c’est très instructif.

D’abord, **`ffff` n’est pas un identifiant constructeur attribué**. Il est absent de la base de l’USB-IF, alors que tous les autres identifiants de la politique s’y résolvent :

```bash
grep -m1 -iE '^ffff' /usr/share/misc/usb.ids   # aucun résultat
grep -m1 -iE '^0781' /usr/share/misc/usb.ids   # 0781  SanDisk Corp.
```

Ce n’est pas en soi un signe de malveillance : les contrôleurs de stockage bon marché sont couramment expédiés avec un identifiant non enregistré. Mais la conséquence est concrète.

!!! warning "Pour ce matériel, seuls `serial` et `hash` discriminent"
    Une règle qui reposerait sur le seul `id ffff:5678` autoriserait **n’importe quelle clé de cette famille**, y compris une que vous n’avez jamais vue. Le nom `"Disk 2.0"` est tout aussi générique et n’apporte aucune garantie.

    C’est un argument concret en faveur du maintien des empreintes, évoqué plus haut dans « Générer sans hash » : sur du matériel de marque, `id` et `serial` suffisent souvent à se repérer ; sur ce type de matériel, retirer les hashes reviendrait à ouvrir la porte à toute une catégorie de périphériques.

    Vérifiez donc qu’aucune de vos règles ne se réduit à un identifiant générique :

    ```bash
    usbguard list-rules | grep -v 'hash' | grep -v 'serial "[^"]\+"'
    ```

Ensuite, **chaque `usbguard allow-device <ID> -p` écrit une règle permanente supplémentaire, sans jamais vérifier qu’une règle équivalente existe déjà**. Cinq clés autorisées donnent cinq règles : c’est attendu. Mais la politique grossit sans que rien ne le signale, et il devient vite difficile de se rappeler ce que chaque ligne autorise.

### Auditer la politique périodiquement

```bash
usbguard list-rules | wc -l
usbguard list-rules | grep -oE 'id [0-9a-f]{4}:[0-9a-f]{4}' | sort | uniq -c | sort -rn
```

Un même identifiant apparaissant plusieurs fois a deux explications possibles, qu’il faut savoir départager :

- **plusieurs exemplaires d’un même modèle**, chacun avec son propre numéro de série — cas légitime, celui décrit ci-dessus ;
- **des règles mortes**, laissées par un périphérique qui présente une identité différente à chaque branchement.

!!! danger "Un périphérique qui change d’identité ne peut pas être mis en liste blanche"
    Si un périphérique annonce un numéro de série différent à chaque énumération, l’empreinte USBGuard change avec lui, puisqu’elle est calculée à partir des attributs du périphérique. Chaque autorisation permanente laisse alors derrière elle une règle qui ne correspondra plus jamais, et le périphérique est de toute façon bloqué au branchement suivant.

    Pour trancher entre les deux cas, branchez **le même exemplaire** deux fois de suite et comparez :

    ```bash
    usbguard list-devices --blocked
    # débrancher, rebrancher le même périphérique, puis :
    usbguard list-devices --blocked
    ```

    Si le `serial` diffère d’un relevé à l’autre pour un exemplaire unique, le comportement est confirmé et aucune règle fondée sur `serial` ou `hash` ne pourra le reconnaître durablement.

Le nettoyage d’éventuelles règles mortes se fait règle par règle. **Supprimez toujours des identifiants les plus élevés vers les plus bas**, car les numéros se décalent après chaque suppression :

```bash
usbguard list-rules                        # relever les identifiants à retirer
sudo usbguard remove-rule 15
sudo usbguard remove-rule 14
sudo usbguard remove-rule 13
usbguard list-rules                        # vérifier le résultat
```

Sauvegardez la politique avant l’opération.

---

## Scripts de mise en place

Les trois scripts ci-dessous automatisent la procédure décrite plus haut, avec les garde-fous qui en font l’intérêt. Ils sont donnés pour une installation dans `/usr/local/sbin/` ; adaptez le chemin si vous les placez ailleurs, car les deux premiers se renvoient l’un à l’autre.

Ils sont volontairement séparés en deux temps. Le premier ne change rien au fonctionnement du système : il prépare la politique et les droits, mais laisse le démon masqué. Le second est le seul moment où l’on prend un risque, et il sait revenir en arrière tout seul.

!!! warning "À relire avant de les exécuter"
    Ces scripts appliquent les choix décrits dans cette note : politique sans liaison aux ports, révocation de l’accès `plugdev`, report des droits sur le groupe `sudo`, service D-Bus laissé masqué. Si vos arbitrages diffèrent, modifiez-les plutôt que de les lancer tels quels.

    Ouvrez une session SSH depuis une autre machine avant de commencer, et vérifiez que votre interface réseau n’est pas un adaptateur USB — le premier script refuse de continuer dans ce cas.

??? example "`usbguard-1-preparer.sh`"

    Contrôles préalables, masquage, installation, génération de la politique et durcissement des droits IPC. **N’active rien** : à l’issue de ce script, le démon est toujours masqué et le système fonctionne comme avant. Il refuse d’aller plus loin si la politique est vide, si un périphérique branché n’a pas de règle, ou si aucune interface HID n’est couverte.

    ```bash
    #!/usr/bin/env bash
    #
    # USBGuard — phase 1 : préparation (n'active RIEN)
    #
    # À l'issue de ce script, la politique et les droits IPC sont en place mais le
    # démon reste masqué et arrêté : le système fonctionne exactement comme avant.
    # L'activation se fait séparément avec usbguard-2-activer.sh.
    #
    set -euo pipefail

    RESET=$'\e[0m'; RED=$'\e[31m'; GRN=$'\e[32m'; YEL=$'\e[33m'; BLD=$'\e[1m'
    ok()   { printf '  %s✓%s %s\n' "$GRN" "$RESET" "$1"; }
    warn() { printf '  %s!%s %s\n' "$YEL" "$RESET" "$1"; }
    die()  { printf '\n%sÉCHEC :%s %s\n' "$RED" "$RESET" "$1" >&2; exit 1; }
    step() { printf '\n%s=== %s ===%s\n' "$BLD" "$1" "$RESET"; }

    WORKDIR=/root/usbguard
    POLICY=$WORKDIR/rules.conf.new

    # ---------------------------------------------------------------- pré-vols ---
    step "Contrôles préalables"

    [ "$(id -u)" -eq 0 ] || die "à lancer avec sudo."
    ok "exécuté en root"

    . /etc/os-release
    [ "${VERSION_ID:-}" = "24.04" ] || warn "Ubuntu ${VERSION_ID:-?} détecté, script validé pour 24.04"
    ok "système : ${PRETTY_NAME}"

    if dpkg -l usbguard 2>/dev/null | grep -q '^ii'; then
        die "usbguard est déjà installé. Ce script vise une première installation.
           Pour repartir de zéro : sudo systemctl mask --now usbguard.service usbguard-dbus.service
                                   sudo apt purge usbguard"
    fi
    ok "usbguard non installé"

    # Aucune interface réseau ne doit être portée par le bus USB : USBGuard
    # pourrait sinon couper l'accès distant en même temps que le clavier.
    for i in /sys/class/net/*; do
        n=$(basename "$i"); [ "$n" = lo ] && continue
        if readlink -f "$i/device" 2>/dev/null | grep -q usb; then
            die "l'interface réseau $n est un adaptateur USB.
           USBGuard risquerait de vous couper l'accès distant. Abandon."
        fi
    done
    ok "aucune interface réseau n'est sur le bus USB"

    # Détection de la session SSH de secours.
    SSH_PEER=$( { ss -tn state established '( sport = :22 )' 2>/dev/null \
                  | awk 'NR>1{sub(/:[0-9]+$/,"",$4); print $4}' | sort -u | head -1; } || true)
    if [ -n "${SSH_PEER:-}" ]; then
        NETIF=$(ip -o route get "$SSH_PEER" 2>/dev/null | grep -oP 'dev \K\S+' || true)
        ok "session SSH active depuis $SSH_PEER${NETIF:+ via $NETIF} — canal de secours confirmé"
    else
        warn "AUCUNE session SSH détectée."
        warn "Sans clavier PS/2, une erreur vous laisserait sans aucun moyen d'action."
        read -r -p "  Continuer malgré tout ? [oui/non] " R
        [ "$R" = "oui" ] || die "interrompu. Ouvrez une session SSH depuis une autre machine."
    fi

    # Inventaire des périphériques présents, hors contrôleurs racine.
    mapfile -t PRESENT < <(
        for d in /sys/bus/usb/devices/*/; do
            [ -f "$d/idVendor" ] || continue
            v=$(<"$d/idVendor"); p=$(<"$d/idProduct")
            [ "$v" = "1d6b" ] && continue
            printf '%s:%s\n' "$v" "$p"
        done | sort -u
    )
    [ "${#PRESENT[@]}" -gt 0 ] || die "aucun périphérique USB détecté, situation anormale."
    printf '  %s%d périphériques USB présents :%s\n' "$BLD" "${#PRESENT[@]}" "$RESET"
    for d in /sys/bus/usb/devices/*/; do
        [ -f "$d/idVendor" ] || continue
        v=$(<"$d/idVendor"); p=$(<"$d/idProduct")
        [ "$v" = "1d6b" ] && continue
        printf '      %s:%s  %s\n' "$v" "$p" "$(cat "$d/product" 2>/dev/null || echo '(sans nom)')"
    done
    echo
    read -r -p "  Ces périphériques sont-ils TOUS légitimes et à conserver ? [oui/non] " REP
    [ "$REP" = "oui" ] || die "interrompu. Débranchez l'intrus et relancez."

    # ------------------------------------------------------------- masquage ------
    step "Masquage des unités avant installation"
    systemctl mask usbguard.service usbguard-dbus.service >/dev/null 2>&1 || true
    for u in usbguard.service usbguard-dbus.service; do
        [ "$(readlink -f "/etc/systemd/system/$u" 2>/dev/null)" = /dev/null ] \
            || die "le masque de $u n'a pas été créé."
        ok "$u masqué"
    done

    # ----------------------------------------------------------- installation ----
    step "Installation du paquet"
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq usbguard >/dev/null
    ok "usbguard $(dpkg-query -W -f='${Version}' usbguard) installé"

    # Le service doit toujours être neutralisé après le postinst.
    STATE=$(systemctl is-enabled usbguard.service 2>/dev/null || true)
    [ "$STATE" = masked ] || die "usbguard.service n'est plus masqué (état : $STATE).
           Le paquet avait probablement été retiré sans purge auparavant.
           Lancez : sudo systemctl mask --now usbguard.service usbguard-dbus.service"
    ok "usbguard.service toujours masqué"
    systemctl is-active --quiet usbguard.service && die "le démon tourne, abandon." || true
    ok "démon inactif, périphériques USB intacts"

    # Ce que le postinst a fabriqué tout seul.
    [ -s /etc/usbguard/rules.conf ] \
        && ok "politique auto-générée par le paquet : $(wc -l < /etc/usbguard/rules.conf) règles (elle va être remplacée)" \
        || warn "politique auto-générée vide ou absente — sans importance, on la régénère"
    [ -e /etc/usbguard/IPCAccessControl.d/:plugdev ] \
        && warn "accès IPC plugdev créé par le paquet — il va être révoqué"

    # -------------------------------------------------------------- politique ----
    step "Génération de la politique (sans liaison aux ports)"
    install -d -m 0700 -o root -g root "$WORKDIR"
    sh -c "umask 077; usbguard generate-policy --no-ports-sn > '$POLICY'"

    RULES=$(grep -c '^allow' "$POLICY" || true)
    [ "$RULES" -gt 0 ] || die "politique générée vide. NE PAS ACTIVER."
    ok "$RULES règles allow générées"

    if grep -q 'via-port' "$POLICY"; then
        warn "des règles via-port subsistent malgré --no-ports-sn :"
        grep -n 'via-port' "$POLICY" | sed 's/^/      /'
    else
        ok "aucune règle liée à un port — vos périphériques resteront valides sur n'importe quelle prise"
    fi

    # Chaque périphérique présent doit avoir sa règle, sinon blocage à l'activation.
    MISSING=0
    for id in "${PRESENT[@]}"; do
        grep -q "id $id" "$POLICY" || { warn "ABSENT de la politique : $id"; MISSING=1; }
    done
    [ "$MISSING" -eq 0 ] || die "des périphériques présents n'ont pas de règle. NE PAS ACTIVER."
    ok "les ${#PRESENT[@]} périphériques présents ont tous une règle"

    # Garde-fou spécifique : au moins une règle couvrant un périphérique d'entrée.
    grep -q 'with-interface.*03:' "$POLICY" \
        || die "aucune règle ne couvre une interface HID (classe 03).
           Votre clavier et votre souris seraient bloqués. NE PAS ACTIVER."
    ok "au moins une interface HID (clavier/souris) est couverte"

    install -m 0600 -o root -g root "$POLICY" /etc/usbguard/rules.conf
    ok "politique installée en $(stat -c '%A %U:%G' /etc/usbguard/rules.conf)"

    # ------------------------------------------------------------- droits IPC ----
    step "Durcissement des droits IPC"
    cp -a /etc/usbguard/usbguard-daemon.conf /etc/usbguard/usbguard-daemon.conf.backup
    sed -i 's/^IPCAllowedGroups=/#IPCAllowedGroups=/' /etc/usbguard/usbguard-daemon.conf
    grep -q '^#IPCAllowedGroups=' /etc/usbguard/usbguard-daemon.conf \
        || die "IPCAllowedGroups n'a pas pu être neutralisée."
    ok "IPCAllowedGroups neutralisée (accès complet hérité de plugdev supprimé)"
    grep -q '^IPCAllowedUsers=root' /etc/usbguard/usbguard-daemon.conf \
        && ok "IPCAllowedUsers=root conservée (sudo usbguard … continuera de fonctionner)"

    usbguard remove-user plugdev -g 2>/dev/null || true
    [ -e /etc/usbguard/IPCAccessControl.d/:plugdev ] \
        && die "le fichier :plugdev n'a pas pu être retiré." \
        || ok "accès IPC de plugdev révoqué"

    usbguard add-user sudo --group --devices ALL --policy modify,list --exceptions listen
    [ -e /etc/usbguard/IPCAccessControl.d/:sudo ] || die "l'accès du groupe sudo n'a pas été créé."
    ok "droits accordés au groupe sudo :"
    sed 's/^/      /' /etc/usbguard/IPCAccessControl.d/:sudo

    # --------------------------------------------------------- permissions -------
    step "Contrôle des permissions"
    BAD=$(find /etc/usbguard -type f ! -perm 0600 -printf '%m %p\n' || true)
    [ -z "$BAD" ] || die "fichiers trop permissifs, le démon refuserait de démarrer :
    $BAD"
    ok "tous les fichiers de /etc/usbguard sont en 0600"

    # ------------------------------------------------------------------ bilan ----
    step "Préparation terminée — RIEN n'est encore actif"
    cat <<EOF

      Le démon est toujours masqué : votre système fonctionne comme avant.

      1. Relisez la politique qui sera appliquée :

           sudo less /etc/usbguard/rules.conf

      2. Quand vous êtes prêt, activez avec :

           sudo /usr/local/sbin/usbguard-2-activer.sh

         Gardez votre session SSH ouverte pendant l'activation.

    EOF
    ```

??? example "`usbguard-2-activer.sh`"

    Démarre le démon, puis demande une confirmation **au clavier** avec un délai de 90 secondes. Si le clavier vient d’être bloqué, la confirmation est impossible, le délai expire et la protection est retirée automatiquement : unités masquées et arrêtées, puis attributs `authorized` du sysfs remis à 1 pour réanimer les périphériques sans redémarrage.

    ```bash
    #!/usr/bin/env bash
    #
    # USBGuard — phase 2 : activation, avec retour arrière automatique
    #
    # Démarre le démon puis attend une confirmation au clavier. Si le clavier ne
    # répond plus (donc s'il vient d'être bloqué), le délai expire et la protection
    # est automatiquement retirée, les périphériques étant réautorisés.
    #
    set -euo pipefail

    RESET=$'\e[0m'; RED=$'\e[31m'; GRN=$'\e[32m'; YEL=$'\e[33m'; BLD=$'\e[1m'
    ok()   { printf '  %s✓%s %s\n' "$GRN" "$RESET" "$1"; }
    warn() { printf '  %s!%s %s\n' "$YEL" "$RESET" "$1"; }
    die()  { printf '\n%sÉCHEC :%s %s\n' "$RED" "$RESET" "$1" >&2; exit 1; }
    step() { printf '\n%s=== %s ===%s\n' "$BLD" "$1" "$RESET"; }

    DELAI=${DELAI:-90}

    reautoriser() {
        for f in /sys/bus/usb/devices/*/authorized_default; do [ -w "$f" ] && echo 1 > "$f" || true; done
        for f in /sys/bus/usb/devices/*/authorized;         do [ -w "$f" ] && echo 1 > "$f" || true; done
    }

    retour_arriere() {
        printf '\n%s>>> RETOUR ARRIÈRE EN COURS <<<%s\n' "$RED" "$RESET"
        systemctl mask --now usbguard.service usbguard-dbus.service >/dev/null 2>&1 || true
        reautoriser
        printf '%s\n' "  Démon arrêté et masqué, périphériques USB réautorisés."
        printf '%s\n' "  Si le clavier ne revient pas immédiatement, débranchez/rebranchez-le,"
        printf '%s\n' "  ou redémarrez : le masque survivra au redémarrage."
        printf '%s\n' "  Rien n'est perdu : la politique reste dans /etc/usbguard/rules.conf."
    }

    [ "$(id -u)" -eq 0 ] || die "à lancer avec sudo."

    step "Contrôles avant activation"
    [ -s /etc/usbguard/rules.conf ] || die "/etc/usbguard/rules.conf absent ou vide. Lancez d'abord la phase 1."
    NB_ALLOW=$(grep -c '^allow' /etc/usbguard/rules.conf || true)
    [ "$NB_ALLOW" -gt 0 ] || die "la politique ne contient aucune règle allow. NE PAS ACTIVER."
    ok "politique présente : $NB_ALLOW règles allow"
    [ "$(stat -c '%a %U:%G' /etc/usbguard/rules.conf)" = "600 root:root" ] \
        || die "permissions incorrectes sur rules.conf."
    ok "permissions correctes"
    BAD=$(find /etc/usbguard -type f ! -perm 0600 -printf '%m %p\n' || true)
    [ -z "$BAD" ] || die "fichiers trop permissifs :
    $BAD"
    ok "aucun fichier trop permissif"

    mapfile -t PRESENT < <(
        for d in /sys/bus/usb/devices/*/; do
            [ -f "$d/idVendor" ] || continue
            v=$(<"$d/idVendor"); p=$(<"$d/idProduct")
            [ "$v" = "1d6b" ] && continue
            printf '%s:%s\n' "$v" "$p"
        done | sort -u
    )
    for id in "${PRESENT[@]}"; do
        grep -q "id $id" /etc/usbguard/rules.conf \
            || die "le périphérique $id est branché mais absent de la politique.
           Il serait bloqué. Relancez la phase 1."
    done
    ok "les ${#PRESENT[@]} périphériques branchés ont tous une règle"

    step "Démarrage du démon"
    systemctl unmask usbguard.service >/dev/null
    systemctl enable --now usbguard.service >/dev/null 2>&1 || {
        journalctl -u usbguard.service -b --no-pager | tail -20
        die "le démon n'a pas démarré. Consultez le journal ci-dessus."
    }
    sleep 2
    systemctl is-active --quiet usbguard.service || {
        journalctl -u usbguard.service -b --no-pager | tail -20
        retour_arriere
        die "usbguard.service n'est pas actif."
    }
    ok "usbguard.service actif"

    step "État des périphériques"
    usbguard list-devices | sed 's/^/  /'

    BLOQUES=$( { usbguard list-devices --blocked 2>/dev/null | wc -l; } || true)
    if [ "$BLOQUES" -gt 0 ]; then
        warn "$BLOQUES périphérique(s) bloqué(s) :"
        usbguard list-devices --blocked | sed 's/^/      /'
    fi

    printf '\n%s' "$BLD"
    cat <<EOF
    ================================================================
      TEST DU CLAVIER — $DELAI secondes
    ================================================================
    $RESET
      Tapez  oui  puis Entrée pour CONSERVER la protection.

      Si votre clavier ne répond plus, ne faites rien : au bout de
      $DELAI secondes la protection sera retirée automatiquement et
      vos périphériques réautorisés.

    EOF

    REP=""
    if read -r -t "$DELAI" -p "  Votre clavier fonctionne-t-il ? [oui] " REP && [ "$REP" = "oui" ]; then
        step "Protection conservée"
        ok "usbguard.service : $(systemctl is-active usbguard.service) / $(systemctl is-enabled usbguard.service)"

        if [ -n "${SUDO_USER:-}" ]; then
            if runuser -u "$SUDO_USER" -- usbguard list-devices >/dev/null 2>&1; then
                ok "$SUDO_USER peut interroger USBGuard sans sudo"
            else
                warn "$SUDO_USER ne peut pas encore interroger USBGuard sans sudo — reconnectez votre session"
            fi
            if runuser -u "$SUDO_USER" -- usbguard set-parameter ImplicitPolicyTarget block >/dev/null 2>&1; then
                warn "$SUDO_USER peut modifier les paramètres (normal : il est dans le groupe sudo)"
            fi
        fi

        cat <<EOF

      Reste à faire, dans cet ordre :

        1. Branchez une clé USB inconnue et vérifiez qu'elle est refusée :
             usbguard list-devices --blocked

        2. Débranchez/rebranchez souris et clavier : ils doivent revenir seuls.

        3. Redémarrez la machine et vérifiez le clavier à l'écran de connexion.
           Gardez la session SSH ouverte pendant ce test.

      En cas de problème, depuis SSH :
           sudo /usr/local/sbin/usbguard-secours.sh

    EOF
    else
        [ -z "$REP" ] && printf '\n  %sAucune réponse dans le délai imparti.%s\n' "$YEL" "$RESET"
        retour_arriere
        exit 1
    fi
    ```

??? example "`usbguard-secours.sh`"

    À garder sous la main dans la session SSH. Arrête et masque USBGuard, puis réautorise tous les périphériques. La politique n’est pas supprimée : elle reste dans `/etc/usbguard/rules.conf` et pourra être reprise après diagnostic.

    ```bash
    #!/usr/bin/env bash
    #
    # USBGuard — script de secours
    #
    # À lancer depuis la session SSH si clavier et souris ne répondent plus.
    # Arrête et masque USBGuard, puis réautorise tous les périphériques USB.
    # La politique n'est pas supprimée : elle reste dans /etc/usbguard/rules.conf.
    #
    set -uo pipefail

    RESET=$'\e[0m'; GRN=$'\e[32m'; BLD=$'\e[1m'
    ok() { printf '  %s✓%s %s\n' "$GRN" "$RESET" "$1"; }

    [ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo." >&2; exit 1; }

    printf '%s=== Neutralisation d'"'"'USBGuard ===%s\n' "$BLD" "$RESET"

    systemctl mask --now usbguard.service usbguard-dbus.service >/dev/null 2>&1 || true
    ok "unités arrêtées et masquées"

    N=0
    for f in /sys/bus/usb/devices/*/authorized_default; do
        [ -w "$f" ] && { echo 1 > "$f" 2>/dev/null && N=$((N+1)); } || true
    done
    for f in /sys/bus/usb/devices/*/authorized; do
        [ -w "$f" ] && { echo 1 > "$f" 2>/dev/null && N=$((N+1)); } || true
    done
    ok "$N attributs d'autorisation remis à 1"

    printf '\n%sÉtat :%s\n' "$BLD" "$RESET"
    printf '  usbguard.service : %s / %s\n' \
        "$(systemctl is-active usbguard.service 2>/dev/null || echo inactive)" \
        "$(systemctl is-enabled usbguard.service 2>/dev/null || echo masked)"
    printf '  périphériques USB vus par le noyau : %s\n' "$(lsusb | wc -l)"

    cat <<'EOF'

      Si le clavier ne revient pas tout de suite, débranchez-le puis rebranchez-le.
      En dernier recours, redémarrez : le masque survit au redémarrage.

      Pour repartir sur de bonnes bases ensuite :
          sudo less /etc/usbguard/rules.conf     # voir ce qui avait été généré
          journalctl -u usbguard.service -b      # comprendre ce qui a bloqué

    EOF
    ```

### Installation et usage

```bash
sudo install -m 0750 -o root -g root usbguard-*.sh /usr/local/sbin/

sudo /usr/local/sbin/usbguard-1-preparer.sh
sudo less /etc/usbguard/rules.conf          # relire la politique avant d'activer
sudo /usr/local/sbin/usbguard-2-activer.sh
```

Le délai du test clavier se règle par variable d’environnement si 90 secondes ne conviennent pas :

```bash
sudo DELAI=180 /usr/local/sbin/usbguard-2-activer.sh
```

!!! tip "Les deux boucles qui comptent vraiment"
    Dans le script d’activation comme dans celui de secours, la réautorisation passe par une écriture directe dans `sysfs` :

    ```bash
    for f in /sys/bus/usb/devices/*/authorized_default; do echo 1 > "$f" 2>/dev/null; done
    for f in /sys/bus/usb/devices/*/authorized;         do echo 1 > "$f" 2>/dev/null; done
    ```

    C’est la partie indispensable : **arrêter le démon ne réautorise pas les périphériques déjà bloqués**. Sans ces deux boucles, un retour arrière laisserait le clavier inerte jusqu’à un rebranchement ou un redémarrage.

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
- Les valeurs par défaut d’une distribution peuvent accorder bien plus de droits que prévu : sur Ubuntu 24.04, `IPCAllowedGroups=root plugdev` et la règle polkit du paquet en sont deux exemples.
- Un démon qui ne démarre pas laisse le système sans aucune protection : cette panne est silencieuse et doit être surveillée.
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
- [ ] La politique générée automatiquement par le paquet a été inspectée et n’est pas vide
- [ ] `RuleFile` **et** `RuleFolder` ont été vérifiés dans `usbguard-daemon.conf`
- [ ] La politique initiale a été générée dans un fichier de travail réservé à `root`
- [ ] La présence de `via-port` dans la politique générée a été mesurée et le compromis a été tranché
- [ ] Chaque périphérique autorisé a été identifié et justifié
- [ ] La politique est installée en `0600 root:root`
- [ ] Aucun fichier de `/etc/usbguard/` n’est plus permissif que `0600`
- [ ] Le clavier, la souris, les hubs, le dock et le réseau USB nécessaires sont couverts
- [ ] `IPCAllowedGroups=root plugdev` a été neutralisée et l’accès `:plugdev` retiré
- [ ] Un compte non autorisé ne peut pas exécuter `usbguard set-parameter`
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
- [ ] Si `usbguard-dbus.service` a été activé, la règle polkit accordant `plugdev` et `sudo` sans authentification a été relue
- [ ] La rotation du journal d’audit a été resserrée si sa lisibilité par tous pose problème

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
