---
title: "Premiers pas avec Ansible : créer un inventaire et lancer un premier playbook sur plusieurs VM Linux"
date: 2026-05-31
author: Nicolas BODAINE
tags:
  - ansible
  - automatisation
  - linux
  - inventaire
  - playbook
  - ssh
difficulty: débutant
os: Ubuntu 24.04 / Debian 13
status: publié
---

# Premiers pas avec Ansible : créer un inventaire et lancer un premier playbook sur plusieurs VM Linux

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour découvrir **Ansible** dans un petit lab Linux. Nous allons installer Ansible sur une machine d'administration, préparer l'accès SSH vers **deux VM cibles**, créer un **inventaire**, puis exécuter un **premier playbook** pour installer un paquet et déployer un fichier de configuration simple.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 / Debian 13 |
| Dernière mise à jour | 2026-05-31 |

## Contexte

**Ansible** est un outil d'automatisation très utilisé pour :

- administrer plusieurs serveurs en même temps ;
- appliquer la même configuration sur plusieurs machines ;
- déployer des fichiers ;
- installer des paquets ;
- standardiser des actions répétitives dans un lab, un parc ou un petit SI.

Son intérêt pédagogique est immédiat : au lieu de se connecter à chaque VM une par une, on décrit ce que l'on veut dans un fichier, puis Ansible applique cette configuration sur l'ensemble des machines ciblées.

Dans ce TP, on utilise un scénario volontairement simple et reproductible.

### Topologie de lab proposée

| Rôle | Nom | Exemple d'IP | Description |
|------|-----|--------------|-------------|
| Nœud de contrôle | `adm-ansible` | `192.168.56.10` | Machine depuis laquelle on lance Ansible |
| VM cible 1 | `srv-lab-01` | `192.168.56.21` | Première VM Linux à administrer |
| VM cible 2 | `srv-lab-02` | `192.168.56.22` | Deuxième VM Linux à administrer |

!!! note "Important"
    Vous pouvez remplacer les noms d'hôtes, les adresses IP et l'utilisateur de connexion par vos propres valeurs. L'important est de garder la même logique de travail.

## Prérequis

- Une machine Linux qui servira de **nœud de contrôle**
- Deux VM Linux joignables en réseau depuis ce nœud de contrôle
- Un utilisateur SSH valide sur les VM cibles, par exemple `formation`
- Des droits `sudo` sur les VM cibles pour installer des paquets et écrire dans `/etc`
- Une connectivité réseau fonctionnelle entre la machine de contrôle et les VM

!!! tip "Environnement conseillé"
    Ce tutoriel fonctionne très bien dans un lab VirtualBox, VMware, Proxmox ou sur trois VM de test dans un réseau privé.

## Procédure

### Étape 1 : vérifier la connectivité de base entre les machines

Depuis le nœud de contrôle, commencez par vérifier que les deux VM répondent sur le réseau.

```bash
ping -c 2 192.168.56.21
ping -c 2 192.168.56.22
```

Ensuite, vérifiez que le port SSH est bien accessible :

```bash
ssh formation@192.168.56.21
ssh formation@192.168.56.22
```

Lors de la première connexion, acceptez l'empreinte SSH si elle est proposée.
Puis quittez chaque session avec :

```bash
exit
```

!!! success "Résultat attendu"
    Vous devez pouvoir joindre les deux VM en réseau et vous connecter en SSH au moins une fois manuellement.

### Étape 2 : installer Ansible sur le nœud de contrôle

Sur la machine d'administration, installez Ansible avec `apt` :

```bash
sudo apt update
sudo apt install -y ansible
```

Vérifiez ensuite la version installée :

```bash
ansible --version
```

Exemple de résultat attendu :

```text
ansible [core 2.x]
  config file = None
  ...
```

!!! note "Pourquoi installer Ansible seulement ici ?"
    Ansible fonctionne selon un modèle très pratique pour débuter : **il s'installe sur la machine de contrôle**, puis se connecte en SSH aux machines cibles. Il n'y a pas d'agent Ansible à installer sur chaque VM dans ce scénario.

### Étape 3 : créer une paire de clés SSH dédiée au lab

Pour éviter de saisir le mot de passe SSH à chaque commande, créez une paire de clés dédiée à ce TP :

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ansible-lab -C "ansible-lab"
```

Quand la commande vous demande une passphrase, vous pouvez :

- en définir une si vous voulez une meilleure sécurité ;
- laisser vide dans un lab isolé et temporaire.

Copiez ensuite la clé publique vers chaque VM cible :

```bash
ssh-copy-id -i ~/.ssh/ansible-lab.pub formation@192.168.56.21
ssh-copy-id -i ~/.ssh/ansible-lab.pub formation@192.168.56.22
```

Testez enfin la connexion sans mot de passe SSH :

```bash
ssh -i ~/.ssh/ansible-lab formation@192.168.56.21 "hostname"
ssh -i ~/.ssh/ansible-lab formation@192.168.56.22 "hostname"
```

!!! success "Résultat attendu"
    Chaque commande doit retourner le nom d'hôte distant sans redemander le mot de passe SSH du compte cible.

### Étape 4 : créer le dossier de travail Ansible

Créez un dossier dédié à ce premier lab :

```bash
mkdir -p ~/ansible-lab
cd ~/ansible-lab
```

Créez ensuite un fichier `ansible.cfg` :

```bash
nano ansible.cfg
```

Contenu proposé :

```ini
[defaults]
inventory = ./inventory.ini
private_key_file = ~/.ssh/ansible-lab
host_key_checking = True
interpreter_python = auto_silent
```

### À quoi sert ce fichier ?

- `inventory` : indique à Ansible quel inventaire utiliser par défaut ;
- `private_key_file` : précise la clé SSH à utiliser pour le lab ;
- `host_key_checking = True` : conserve la vérification des empreintes SSH ;
- `interpreter_python = auto_silent` : aide Ansible à détecter automatiquement Python côté cible.

!!! tip "Bonne pratique"
    Garder un dossier de projet Ansible avec un inventaire, une configuration et des playbooks séparés rend le travail beaucoup plus lisible qu'un inventaire global modifié à la main.

### Étape 5 : créer l'inventaire des machines cibles

Créez maintenant le fichier `inventory.ini` :

```bash
nano inventory.ini
```

Collez le contenu suivant, puis adaptez les adresses IP et l'utilisateur si nécessaire :

```ini
[linux]
srv-lab-01 ansible_host=192.168.56.21
srv-lab-02 ansible_host=192.168.56.22

[linux:vars]
ansible_user=formation
ansible_python_interpreter=/usr/bin/python3
```

### Comprendre cet inventaire

- `[linux]` : nom du groupe de machines ;
- `srv-lab-01` et `srv-lab-02` : noms logiques vus par Ansible ;
- `ansible_host` : adresse IP ou FQDN réellement utilisé pour la connexion ;
- `[linux:vars]` : variables communes à toutes les machines du groupe ;
- `ansible_user` : utilisateur SSH utilisé par défaut ;
- `ansible_python_interpreter` : chemin Python à utiliser sur la cible.

Affichez ensuite l'inventaire sous forme d'arborescence :

```bash
ansible-inventory --graph
```

Exemple de résultat attendu :

```text
@all:
  |--@ungrouped:
  |--@linux:
  |  |--srv-lab-01
  |  |--srv-lab-02
```

!!! success "Résultat attendu"
    Les deux machines doivent apparaître dans le groupe `linux`.

### Étape 6 : tester les hôtes avec le module `ping` d'Ansible

Nous allons maintenant lancer une première commande Ansible sans playbook, uniquement pour vérifier que tout est prêt.

```bash
ansible all -m ansible.builtin.ping
```

Exemple de résultat attendu :

```text
srv-lab-01 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
srv-lab-02 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

!!! note "Que vérifie ce test ?"
    Le module `ansible.builtin.ping` ne teste pas l'ICMP comme la commande système `ping`. Il vérifie surtout qu'Ansible peut se connecter, exécuter du code distant et récupérer une réponse valide.

!!! warning "Si vous obtenez une erreur"
    Les causes les plus fréquentes sont :
    
    - mauvaise adresse IP dans l'inventaire ;
    - utilisateur SSH incorrect ;
    - clé SSH non copiée sur la cible ;
    - `python3` absent sur la machine distante ;
    - port SSH filtré ou machine éteinte.

### Étape 7 : écrire le premier playbook

Créez le fichier `first-playbook.yml` :

```bash
nano first-playbook.yml
```

Collez le contenu suivant :

```yaml
---
- name: Premier playbook Ansible sur plusieurs VM Linux
  hosts: linux
  become: true

  tasks:
    - name: Vérifier la connectivité Ansible
      ansible.builtin.ping:

    - name: Installer curl
      ansible.builtin.apt:
        name: curl
        state: present
        update_cache: true
        cache_valid_time: 3600

    - name: Déployer un fichier de lab géré par Ansible
      ansible.builtin.copy:
        dest: /etc/ansible-lab.txt
        content: |
          Ce fichier a été déployé par Ansible.
          Hôte d'inventaire : {{ inventory_hostname }}
          Adresse cible : {{ ansible_host }}
        owner: root
        group: root
        mode: '0644'
```

### Ce que fait ce playbook

- il cible le groupe `linux` ;
- il utilise `become: true` pour exécuter les tâches avec élévation de privilèges ;
- il vérifie d'abord la connectivité ;
- il installe le paquet `curl` ;
- il crée un fichier `/etc/ansible-lab.txt` sur chaque VM.

!!! note "À propos de `become: true`"
    Cette directive demande à Ansible d'utiliser `sudo` sur les machines cibles. Si votre compte distant n'a pas de `sudo`, le playbook échouera.

### Étape 8 : vérifier la syntaxe avant exécution

Avant de lancer le playbook, faites une vérification de syntaxe :

```bash
ansible-playbook --syntax-check first-playbook.yml
```

Si tout est correct, vous devez obtenir un message de validation sans erreur.

Vous pouvez aussi simuler l'exécution sans modifier les machines :

```bash
ansible-playbook --check --diff -K first-playbook.yml
```

L'option `-K` signifie qu'Ansible demandera le mot de passe `sudo` du compte distant si nécessaire.

!!! tip "Pourquoi utiliser `--check` ?"
    Le mode check est très utile en production comme en lab : il permet d'anticiper les changements avant de les appliquer réellement.

### Étape 9 : exécuter le playbook sur les deux VM

Lancez maintenant le playbook :

```bash
ansible-playbook -K first-playbook.yml
```

Si votre utilisateur distant dispose déjà d'un `sudo` sans mot de passe dans le lab, vous pouvez essayer sans `-K` :

```bash
ansible-playbook first-playbook.yml
```

Exemple de résumé de fin d'exécution :

```text
PLAY RECAP *********************************************************************
srv-lab-01 : ok=3  changed=2  unreachable=0  failed=0
srv-lab-02 : ok=3  changed=2  unreachable=0  failed=0
```

### Comment lire ce résultat ?

- `ok` : tâche exécutée correctement ;
- `changed` : Ansible a réellement modifié quelque chose ;
- `unreachable` : machine non joignable ;
- `failed` : échec d'une tâche.

### Étape 10 : vérifier ce qui a été modifié sur les VM

Contrôlez d'abord que `curl` est bien installé :

```bash
ansible all -a "curl --version | head -n 1"
```

Vérifiez ensuite le contenu du fichier déployé :

```bash
ansible all -a "cat /etc/ansible-lab.txt" -b
```

Exemple de contenu attendu :

```text
Ce fichier a été déployé par Ansible.
Hôte d'inventaire : srv-lab-01
Adresse cible : 192.168.56.21
```

et sur l'autre machine :

```text
Ce fichier a été déployé par Ansible.
Hôte d'inventaire : srv-lab-02
Adresse cible : 192.168.56.22
```

### Étape 11 : relancer le playbook pour comprendre l'idempotence

Relancez exactement la même commande :

```bash
ansible-playbook -K first-playbook.yml
```

Si rien n'a changé depuis le premier passage, le résumé final doit cette fois être proche de :

```text
PLAY RECAP *********************************************************************
srv-lab-01 : ok=3  changed=0  unreachable=0  failed=0
srv-lab-02 : ok=3  changed=0  unreachable=0  failed=0
```

C'est un point fondamental d'Ansible : on décrit un **état attendu**, pas une suite d'actions aveugles.
Si la machine est déjà dans le bon état, Ansible ne refait pas inutilement le travail.

## Vérification

Pour refaire un contrôle rapide de l'ensemble du TP, utilisez ces commandes :

```bash
cd ~/ansible-lab
ansible-inventory --graph
ansible all -m ansible.builtin.ping
ansible-playbook --syntax-check first-playbook.yml
ansible all -a "dpkg -s curl | grep '^Status'"
ansible all -a "cat /etc/ansible-lab.txt" -b
```

!!! success "Résultat attendu"
    L'inventaire doit lister les deux VM, le module `ping` doit répondre `pong`, le playbook doit être syntaxiquement valide, le paquet `curl` doit être installé et le fichier `/etc/ansible-lab.txt` doit être présent sur chaque machine.

## Glossaire

`Nœud de contrôle`
:   Machine depuis laquelle on lance les commandes Ansible.

`Inventaire`
:   Fichier qui contient la liste des machines cibles et éventuellement leurs variables.

`Playbook`
:   Fichier YAML décrivant les actions à appliquer sur un ou plusieurs groupes de machines.

`Module`
:   Brique fonctionnelle utilisée par Ansible pour réaliser une action, par exemple `ping`, `apt` ou `copy`.

`Idempotence`
:   Propriété d'un outil qui permet de relancer la même configuration plusieurs fois sans produire de changements inutiles lorsque l'état attendu est déjà atteint.

## Ressources

- [Getting started with Ansible](https://docs.ansible.com/ansible/latest/getting_started/index.html) — Documentation officielle pour débuter avec Ansible
- [How to build your inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html) — Documentation officielle sur la construction d'un inventaire
- [Ansible playbooks](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html) — Introduction officielle aux playbooks
- [ansible.builtin.ping module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ping_module.html) — Module officiel pour vérifier la connectivité Ansible
- [ansible.builtin.apt module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html) — Module officiel pour gérer les paquets APT
- [ansible.builtin.copy module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html) — Module officiel pour copier un fichier ou un contenu vers une machine distante
