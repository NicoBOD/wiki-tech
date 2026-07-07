---
title: Activer le lecteur d'empreintes digitales (login + sudo) sur ThinkPad sous Ubuntu 24.04
date: 2026-07-05
author: Nicolas BODAINE
tags:
  - linux
  - securite
  - authentification
  - empreinte
  - fprintd
  - pam
  - thinkpad
difficulty: avancé
os: Ubuntu 24.04
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL : entrée ajoutée dans docs/cybersecurite/index.md   -->
<!-- et dans la nav de mkdocs.yml.                                 -->
<!-- ============================================================ -->

# Activer le lecteur d'empreintes digitales (login + sudo) sur ThinkPad sous Ubuntu 24.04

!!! abstract "Résumé"
    Comment faire fonctionner un lecteur d'empreintes **Validity/Synaptics « Prometheus » `138a:0097`** (fréquent sur les ThinkPad) pour **déverrouiller la session GNOME** et **authentifier `sudo`**, sur Ubuntu 24.04. Ce capteur n'a pas de pilote natif : on utilise le pilote rétro-ingénieré **`python-validity` / `open-fprintd`**, puis on branche l'empreinte dans **PAM** — en gardant **toujours le mot de passe en repli** (aucun risque de blocage).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Avancé |
| OS / Environnement | Ubuntu 24.04 (GNOME / Wayland) |
| Matériel de référence | Lenovo ThinkPad T470s — capteur Validity `138a:0097` |
| Dernière mise à jour | 2026-07-05 |

!!! warning "Capteur capricieux + composants tiers"
    Le `138a:0097` est un capteur **Match-on-Chip** notoirement difficile sous Linux. La solution repose sur un **PPA communautaire** et un **pilote qui remplace le `fprintd` officiel**. C'est fiable pour beaucoup d'exemplaires, mais pas garanti à 100 %. Rien de risqué cependant : tout est **post-boot**, l'empreinte ne peut **pas** déverrouiller LUKS au démarrage, et le **mot de passe reste toujours accepté**.

## Contexte

L'objectif : utiliser l'empreinte pour **ouvrir/déverrouiller la session** et pour les demandes de mot de passe (`sudo`, fenêtres de privilège **polkit**). Le lecteur d'empreintes **ne déverrouille pas le disque chiffré (LUKS) au boot** — cela n'intervient qu'après le démarrage, via PAM.

!!! note "Identifier son capteur d'abord"
    ```bash
    lsusb | grep -i -E 'finger|validity|synaptic|138a|06cb|27c6|goodix|egis'
    ```
    Cette procédure vise le **`138a:0097`**. Pour d'autres modèles (ex. `138a:0090`), la méthode `libfprint-2-tod` / `validity-sensors-tools` peut convenir — voir la section *Alternative*.

## Prérequis

- Ubuntu 24.04 (GNOME).
- Un lecteur `138a:0097` (vérifié avec `lsusb`).
- Accès `sudo` et une connexion Internet (téléchargement du firmware du capteur).
- Comprendre que l'empreinte sera **« suffisante »** dans PAM : le **mot de passe reste un repli permanent**.

## Pourquoi pas le pilote « standard » ?

Ce capteur n'est pas géré par le `libfprint` natif d'Ubuntu (`fprintd-list` répond *No devices available*). Deux pilotes rétro-ingénierés existent :

| Pilote | Verdict pour le `138a:0097` |
|--------|------------------------------|
| `validity-sensors-tools` (snap, 3v1n0) + `libfprint-2-tod` | Adapté surtout au `138a:0090`. Sur certains `0097`, l'initialisation du flash **échoue** (`Failed: 04af` → `Unexpected TLS version 4 0`). |
| **`python-validity` / `open-fprintd`** | ✅ **Recommandé pour le `0097`** : télécharge le bon firmware (`_qm`) et réussit l'appairage là où le précédent échoue. |

## Procédure (python-validity / open-fprintd)

### Étape 1 : Ajouter le PPA et installer le pilote

```bash
sudo add-apt-repository -y ppa:ubuntuhandbook1/open-fprintd
sudo apt update
sudo apt install -y open-fprintd fprintd-clients python3-validity
```

L'installation télécharge automatiquement le firmware Lenovo adapté au capteur (`6_07f_lenovo_mis_qm.xpfwext`).

!!! note "Ce que ça remplace"
    `open-fprintd` fournit le service D-Bus `net.reactivated.Fprint` **à la place** du `fprintd` officiel (qui passe en état `rc`). Le module PAM `pam_fprintd.so` et les clients `fprintd-*` continuent de fonctionner avec ce service.

### Étape 2 : Initialiser / appairer le capteur

Le service `python3-validity` gère l'appairage tout seul au démarrage. S'il échoue (capteur dans un état résiduel), forcer un cycle propre :

```bash
sudo systemctl stop python3-validity
# Reset "propre" via l'implémentation python-validity (le capteur va se ré-énumérer)
sudo python3 /usr/share/python-validity/playground/factory-reset.py
# Purger l'éventuel back-off d'échecs
sudo rm -f /usr/share/python-validity/backoff
# Attendre ~5 s que le capteur réapparaisse sur l'USB, puis relancer
sudo systemctl restart python3-validity
```

Vérifier que le service est **actif** et sans traceback fatal :

```bash
systemctl is-active python3-validity
sudo journalctl -u python3-validity -n 30 --no-pager | grep -viE '>cmd>|<cmd<'
```

!!! tip "Vérifier la présence USB si « No matching devices found »"
    Après un factory-reset le capteur se ré-énumère (son numéro de device USB change). S'il a disparu momentanément, attendez qu'il revienne :
    ```bash
    lsusb | grep -i 138a
    ```
    puis relancez `sudo systemctl restart python3-validity`.

### Étape 3 : Confirmer que le périphérique est vu

```bash
fprintd-list "$USER"
```

!!! success "Attendu"
    ```
    found 1 devices
    Device at /net/reactivated/Fprint/Device/0
    User <user> has no fingers enrolled for DBus driver.
    ```

### Étape 4 : Enrôler un ou plusieurs doigts

C'est un capteur **tactile** (on pose/relève, on ne glisse pas). Répéter le contact ≈ 6–10 fois.

```bash
fprintd-enroll -f right-index-finger
fprintd-enroll -f left-index-finger   # optionnel : un second doigt
```

Attendu : plusieurs `enroll-stage-passed` puis **`enroll-completed`**. Vérifier :

```bash
fprintd-list "$USER"     # doit lister les doigts enrôlés
```

Noms de doigts valides : `{left,right}-{thumb,index,middle,ring,little}-finger`.

### Étape 5 : Activer l'empreinte dans PAM (login, sudo, polkit)

```bash
# Sauvegarde de sécurité
sudo cp -a /etc/pam.d/common-auth /etc/pam.d/common-auth.bak-$(date +%F)
# Active le profil fprintd (empreinte "suffisante", mot de passe conservé)
sudo pam-auth-update --enable fprintd
```

Le `/etc/pam.d/common-auth` obtenu ressemble à :

```text
auth [success=3 default=ignore] pam_fprintd.so max_tries=1 timeout=10
auth [success=2 default=ignore] pam_unix.so nullok try_first_pass
...
```

!!! success "Lecture rassurante"
    L'empreinte est essayée en premier ; si elle échoue/expire (`default=ignore`), PAM **bascule automatiquement sur le mot de passe** (`pam_unix`). **Impossible de se bloquer.**

### Étape 6 (souvent nécessaire) : autoriser `sudo` à demander l'empreinte

Si `sudo` est configuré en **NOPASSWD**, il **n'authentifie pas du tout** → aucune empreinte demandée. Vérifier :

```bash
sudo grep -nE 'NOPASSWD' /etc/sudoers /etc/sudoers.d/* 2>/dev/null
```

Pour que `sudo` demande l'empreinte (et gagner en sécurité), retirer la règle NOPASSWD **en validant la syntaxe** pour ne jamais casser sudo :

```bash
sudo cp -a /etc/sudoers /etc/sudoers.bak-$(date +%F)
sudo visudo    # commenter la ligne  «  user ALL=(ALL) NOPASSWD: ALL  »
```

`visudo` valide la syntaxe à l'enregistrement. On conserve la règle standard `%sudo ALL=(ALL:ALL) ALL` (l'utilisateur du groupe `sudo` garde l'accès, désormais authentifié).

## Vérification

```bash
# Empreinte seule
fprintd-verify           # poser le doigt -> attendu : verify-match

# sudo : vider le cache puis tester
sudo -k && sudo true     # -> "Placez votre doigt sur le lecteur d'empreintes"
```

- **Session GNOME** : verrouiller (++super+l++) puis poser le doigt → déverrouillage.
- **Fenêtres polkit** (mises à jour, montage disque…) : proposent aussi l'empreinte.

!!! success "Résultat attendu"
    `verify-match` pour l'empreinte ; `sudo` affiche « Placez votre doigt… » puis exécute la commande (ou bascule au mot de passe via ++esc++/++enter++).

## Problèmes fréquents et solutions

!!! failure "`Unexpected TLS version 4 0` / `Failed: 04af` (avec validity-sensors-tools)"
    Incompatibilité de l'outil `vfs-tools` avec le firmware de certains `0097`. **Solution : utiliser `python-validity`** (cette procédure).

!!! failure "`python3-validity.service` en échec / `Message too long`"
    Erreurs transitoires du pilote. Refaire un cycle **stop → factory-reset → purge backoff → restart** (Étape 2). Si l'empreinte rate ponctuellement à l'usage, utiliser le **mot de passe** (toujours dispo).

!!! failure "`No matching devices found`"
    Le capteur est en cours de ré-énumération après un reset. Attendre qu'il réapparaisse (`lsusb | grep 138a`) puis `sudo systemctl restart python3-validity`.

!!! question "Après un redémarrage"
    Le service `python3-validity` est activé au boot et ré-ouvre le capteur déjà appairé ; les empreintes (stockées **sur la puce**) persistent. En cas de non-réponse : `sudo systemctl restart python3-validity`.

## Retour en arrière

```bash
# Désactiver l'empreinte dans PAM
sudo pam-auth-update    # décocher "Fingerprint authentication"
# (ou restaurer /etc/pam.d/common-auth.bak-AAAA-MM-JJ)

# Revenir à sudo NOPASSWD : sudo visudo, décommenter la ligne
# (ou restaurer /etc/sudoers.bak-AAAA-MM-JJ)

# Désinstaller complètement le pilote
sudo apt remove --purge open-fprintd python3-validity fprintd-clients
sudo add-apt-repository -r ppa:ubuntuhandbook1/open-fprintd
```

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `lsusb \| grep 138a` | Identifier le capteur Validity |
| `fprintd-list "$USER"` | Lister périphérique + doigts enrôlés |
| `fprintd-enroll -f <doigt>` | Enrôler un doigt |
| `fprintd-verify` | Tester la reconnaissance |
| `fprintd-delete "$USER"` | Supprimer les empreintes enrôlées |
| `sudo pam-auth-update --enable fprintd` | Brancher l'empreinte dans PAM |
| `systemctl status python3-validity` | État du pilote |
| `sudo systemctl restart python3-validity` | Relancer le pilote |

## Glossaire

Match-on-Chip (MOC)
:   Capteur où la comparaison des empreintes se fait **dans la puce** ; les gabarits ne quittent pas le lecteur.

fprintd
:   Démon D-Bus standard de gestion des empreintes sous Linux. Ici remplacé par **open-fprintd** (même interface D-Bus).

python-validity / open-fprintd
:   Pilote rétro-ingénieré (userspace) pour les capteurs Synaptics « Prometheus » (`138a:0090/0097/009d`).

PAM
:   *Pluggable Authentication Modules* : la pile d'authentification de Linux (login, `sudo`, polkit…). `pam_fprintd.so` y ajoute l'empreinte.

polkit
:   Cadre d'autorisation pour les actions privilégiées des applications de bureau (montage, mises à jour…), qui passe aussi par PAM.

## Ressources

- [uunicorn/python-validity](https://github.com/uunicorn/python-validity) — pilote pour capteurs Prometheus.
- [PPA ubuntuhandbook1/open-fprintd](https://launchpad.net/~ubuntuhandbook1/+archive/ubuntu/open-fprintd) — paquets Ubuntu 24.04.
- [Activer le lecteur d'empreintes sur ThinkPad (UbuntuHandbook)](https://ubuntuhandbook.org/index.php/2024/02/fingerprint-reader-t480s/) — tutoriel de référence.
- [3v1n0/libfprint (vfs0090)](https://github.com/3v1n0/libfprint/blob/vfs0090/README.md) — alternative pour la famille `138a:0090`.
