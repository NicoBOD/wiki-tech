---
icon: material/laptop
description: Administration système, stockage, sécurité locale et gestion des utilisateurs sous Linux.
---

# Systèmes

Administration système, stockage, sécurité locale et gestion des utilisateurs sous Linux.

## Administration & Services

- [Gérer les services Linux avec systemctl : l'essentiel pour l'administration](gerer-services-linux-systemctl-essentiel.md) — Maîtriser le démarrage, l'arrêt et l'état des daemons via systemd.
- [Comprendre et gérer le `machine-id` sous Linux](machine-id-linux.md) — Découvrir à quoi sert cet identifiant unique et comment le regénérer proprement.
- [Maintenir ses sessions terminal à distance avec tmux sous Linux](tmux-maintenir-sessions-terminal-distance.md) — Ne plus perdre son travail en cas de coupure réseau grâce aux multiplexeurs.
- [Installer une interface graphique légère (LXQt ou XFCE) sur Debian 13](installer-interface-graphique-legere-debian-13.md) — Ajouter Xorg, LightDM et un bureau sobre en ressources sur un serveur sans environnement graphique.

## Gestion des Fichiers & Permissions

- [Comprendre et gérer les permissions sous Linux (chmod, chown)](gerer-permissions-fichiers-chmod-chown-linux.md) — Sécuriser les accès locaux en modifiant propriétaires et droits d'exécution.
- [Rechercher des fichiers sous Linux avec la commande find](rechercher-fichiers-commande-find-linux.md) — Trouver rapidement n'importe quel fichier selon sa taille, son nom ou sa date.

## Stockage & Sauvegarde

- [Surveiller et analyser l'espace disque sous Linux avec df, du et ncdu](surveiller-analyser-espace-disque-linux-df-du-ncdu.md) — Identifier les dossiers volumineux et prévenir la saturation des disques.
- [Créer et gérer un fichier d'échange (Swap) sous Linux](creer-gerer-fichier-echange-swap-linux.md) — Configurer de la mémoire virtuelle pour éviter les arrêts inopinés par manque de RAM.
- [Étendre un volume logique LVM après ajout d’un disque sur une VM Linux](etendre-volume-logique-lvm-apres-ajout-disque-vm-linux.md) — Agrandir l'espace de stockage à chaud de manière transparente.
- [Sauvegarder et restaurer un dossier avec `rsync` sur Linux en local ou via SSH](sauvegarder-restaurer-dossier-rsync-linux-local-ssh.md) — Synchroniser des données efficacement et reprendre des transferts interrompus.

## Partage Réseau

- [Partager un dossier sur le réseau local avec Samba sur Ubuntu Server](partager-dossier-reseau-local-samba-ubuntu-server.md) — Rendre des fichiers accessibles nativement depuis des postes Windows et Linux.
- [Partager un dossier entre deux machines Linux avec NFS sur Ubuntu Server](partager-dossier-nfs-entre-deux-machines-linux-ubuntu-server.md) — Mettre en place un partage de fichiers performant de serveur à serveur.

## Virtualisation & Déploiement

- [virt-sysprep — préparer une image Linux au clonage](virt-sysprep-preparer-image-linux-clonage.md) — Nettoyer une VM (logs, clés SSH, MAC) avant d'en faire un template réutilisable.
- [Sysprep d'une VM Windows 11 25H2 et création d'un template sur Proxmox VE](sysprep-windows-11-25h2-template-proxmox.md) — Généraliser une image Windows et éviter les pièges BitLocker et Appx des builds 24H2/25H2.
- [Créer et gérer des snapshots de VM avec virsh (libvirt) sur Ubuntu Server](creer-gerer-snapshots-vm-virsh-libvirt-ubuntu-server.md) — Geler l'état d'une VM avant une opération risquée et revenir en arrière en une commande.
- [Migration de mon application Stop Repeat de Lovable vers un Coolify self-hosted](migration-stop-repeat-lovable-vers-coolify.md) — Retour d'expérience sur l'hébergement de projets avec une alternative libre à Vercel.
