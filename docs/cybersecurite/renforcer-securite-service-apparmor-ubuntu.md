---
title: Renforcer la sécurité d'un service avec AppArmor sous Ubuntu
date: 2026-06-19
author: Nicolas BODAINE
tags:
  - apparmor
  - linux
  - securite
  - ubuntu
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Renforcer la sécurité d'un service avec AppArmor sous Ubuntu

!!! abstract "Résumé"
    AppArmor (Application Armor) est un module de sécurité du noyau Linux (LSM) qui permet de restreindre les capacités des programmes à l'aide de profils de sécurité. Dans ce tutoriel, nous allons voir comment créer et appliquer un profil AppArmor pour limiter drastiquement les accès d'un service spécifique (par exemple, un serveur web Nginx ou un script personnalisé), empêchant ainsi toute compromission du système en cas de faille de l'application.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-19 |

## Contexte

Lorsqu'un service est exposé (comme un serveur web), une vulnérabilité logicielle peut permettre à un attaquant d'exécuter des commandes sur le serveur. Par défaut, le processus a accès à une grande partie du système selon les droits de l'utilisateur qui l'exécute. AppArmor permet de définir un périmètre d'exécution ("sandbox") très strict pour chaque service : fichiers lisibles, fichiers inscriptibles, exécution d'autres binaires, accès réseau, etc. Si le service est compromis, l'attaquant reste bloqué dans cette cage.

## Prérequis

- Un serveur sous Ubuntu 24.04 (ou Debian avec AppArmor installé).
- Les privilèges `root` ou `sudo`.
- Le paquet `apparmor-utils` installé.

## Procédure

### Étape 1 : Installer les utilitaires AppArmor

Sur Ubuntu, AppArmor est installé et activé par défaut. Toutefois, pour créer et gérer facilement les profils, les utilitaires dédiés sont indispensables.

```bash
sudo apt update
sudo apt install apparmor-utils -y
```

Vérifiez que le service AppArmor est actif :

```bash
sudo systemctl status apparmor
```

### Étape 2 : Choisir un programme à protéger

Pour ce tutoriel, nous allons créer un petit script bash vulnérable qui écoute sur un port ou lit des fichiers, pour illustrer la méthode. Créons un script `/usr/local/bin/mon_service.sh` :

```bash
sudo nano /usr/local/bin/mon_service.sh
```

Ajoutez le contenu suivant :

```bash
#!/bin/bash
# Un script qui affiche son propre contenu et la date du système.
echo "Service démarré."
cat /etc/hostname
date
```

Rendez-le exécutable :

```bash
sudo chmod +x /usr/local/bin/mon_service.sh
```

### Étape 3 : Générer un profil AppArmor avec `aa-genprof`

L'outil `aa-genprof` permet de générer un profil AppArmor interactif. Il surveille l'exécution du programme, journalise les accès demandés, et vous propose d'autoriser ou refuser chaque action.

Lancez la génération de profil :

```bash
sudo aa-genprof /usr/local/bin/mon_service.sh
```

L'outil affiche :
```text
Writing updated profile for /usr/local/bin/mon_service.sh.
Setting /usr/local/bin/mon_service.sh to complain mode.
...
Please start the application to be profiled in another window and exercise its functionality now.
```

Ouvrez un second terminal (ou utilisez tmux/screen), puis exécutez le script :

```bash
/usr/local/bin/mon_service.sh
```

Revenez sur le premier terminal où tourne `aa-genprof` et appuyez sur **S** (Scan). L'outil va lire les logs et vous poser des questions sur les accès que le script a tentés :
- Exécution de `/bin/bash`
- Lecture de `/etc/hostname`
- Exécution de `/usr/bin/date`

Répondez **A** (Allow) ou **I** (Inherit) pour autoriser ces accès spécifiques. À la fin, appuyez sur **S** (Save) puis **F** (Finish).

### Étape 4 : Analyser le profil généré

Le profil a été créé dans `/etc/apparmor.d/` avec un nom qui remplace les `/` par des `.`.

Affichez le profil :

```bash
cat /etc/apparmor.d/usr.local.bin.mon_service.sh
```

Vous devriez voir quelque chose comme :

```text
#include <tunables/global>

/usr/local/bin/mon_service.sh {
  #include <abstractions/base>
  #include <abstractions/bash>

  /bin/bash ix,
  /bin/cat mrix,
  /etc/hostname r,
  /usr/bin/date mrix,
  /usr/local/bin/mon_service.sh r,
}
```

Les lettres en fin de ligne indiquent les droits :
- `r` : read (lecture)
- `w` : write (écriture)
- `ix` : inherit execute (exécution dans le même profil)

### Étape 5 : Appliquer et activer le mode "Enforce"

Actuellement, le profil peut être en mode "Complain" (apprentissage). Pour bloquer réellement les actions non autorisées, passez le profil en mode "Enforce" :

```bash
sudo aa-enforce /usr/local/bin/mon_service.sh
```

Rechargez ensuite AppArmor pour appliquer ce mode :

```bash
sudo systemctl reload apparmor
```

## Vérification

Pour vérifier que le profil fonctionne, modifions notre script cible pour tenter une action non autorisée, par exemple lire le fichier `/etc/shadow`.

Éditez `/usr/local/bin/mon_service.sh` et ajoutez `cat /etc/shadow` à la fin.

Exécutez le script :

```bash
/usr/local/bin/mon_service.sh
```

!!! success "Résultat attendu"
    Vous devez obtenir une erreur "Permission denied" ou "Accès refusé" pour l'accès à `/etc/shadow`, même si vous exécutez le script en root.

    ```text
    cat: /etc/shadow: Permission denied
    ```

Pour confirmer que le blocage vient d'AppArmor, lisez les logs du noyau avec `dmesg` :

```bash
sudo dmesg -T | grep apparmor | tail -n 1
```

Vous devriez voir un message contenant `apparmor="DENIED" operation="open" profile="/usr/local/bin/mon_service.sh" name="/etc/shadow"`.

## Ressources

- [Documentation officielle Ubuntu Server - AppArmor](https://ubuntu.com/server/docs/security-apparmor) — Guide de référence et syntaxes de profil
- [Wiki AppArmor](https://gitlab.com/apparmor/apparmor/-/wikis/home) — Dépôt officiel et documentation technique
