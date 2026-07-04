---
icon: material/bug
description: Outils et méthodologies pour diagnostiquer et résoudre des problèmes informatiques.
---

# Dépannage & Debug

Outils et méthodologies pour diagnostiquer et résoudre des problèmes informatiques.

## Serveurs Web

- [Diagnostiquer une erreur 502/504 Bad Gateway sur un serveur web](diagnostiquer-erreur-502-504-bad-gateway-serveur-web.md) — Comprendre et résoudre les erreurs de proxy HTTP fréquentes.

## Analyse Système & Réseau

- [Diagnostiquer les problèmes matériels et pilotes sous Linux avec dmesg](diagnostiquer-materiel-pilotes-linux-dmesg.md) — Surveiller le tampon du noyau pour détecter les pannes matérielles et les problèmes de pilotes.
- [Diagnostiquer la consommation CPU et mémoire sous Linux avec htop et free](diagnostiquer-consommation-cpu-memoire-htop-free.md) — Surveiller les ressources de son serveur et identifier les processus gourmands.
- [Diagnostiquer un disque plein ou une saturation I/O sur Linux avec iostat et iotop](diagnostiquer-disque-plein-saturation-io-iostat-iotop-linux.md) — Repérer un disque saturé et identifier les processus responsables des entrées/sorties excessives.
- [Lire, filtrer et suivre les logs avec journalctl](journalctl-lire-filtrer-suivre-logs-systemd-linux.md) — Plonger dans les journaux système de systemd pour comprendre les crashs.
- [Identifier les ports ouverts et les services à l’écoute avec `ss` et `lsof` sous Linux](identifier-ports-ouverts-services-ecoute-ss-lsof-linux.md) — Savoir quel daemon occupe quel port pour éviter les conflits.
- [Capturer et diagnostiquer le trafic réseau en ligne de commande avec tcpdump](capturer-diagnostiquer-trafic-reseau-tcpdump.md) — Analyser et filtrer les paquets réseau depuis un terminal pour le dépannage.
- [Diagnostiquer un processus défaillant avec strace](diagnostiquer-processus-defaillant-strace.md) — Tracer les appels système d'un processus pour comprendre pourquoi il échoue, se bloque ou ralentit.

## Conteneurisation

- [Diagnostiquer un conteneur Docker en échec avec logs et inspect](diagnostiquer-conteneur-docker-en-echec-logs-inspect.md) — Utiliser docker logs et docker inspect pour comprendre l'arrêt inattendu d'un conteneur.

## Développement & Scripts

- [Déboguer une application Python avec pdb en ligne de commande](deboguer-application-python-pdb-cli.md) — Inspecter le comportement d'un script en cours d'exécution de manière interactive.

## Cas Résolus

- [NVIDIA — Écran noir après sortie de veille](nvidia-veille-ecran-noir.md) — Correction d'un problème d'affichage sur les pilotes propriétaires sous Linux.
- [Sniffnet AppImage — Installation et lancement sur Ubuntu 24.04](sniffnet-appimage-ubuntu-2404.md) — Astuce pour faire fonctionner l'interface de surveillance réseau de Sniffnet.
- [AppImageLauncher — Échec d'intégration sur Ubuntu 24.04 (compression zstd)](appimagelauncher-compression-zstd-ubuntu-2404.md) — Contourner l'erreur de compression Zstandard qui empêche l'intégration des AppImages.