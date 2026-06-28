---
icon: material/cog
description: Ansible, n8n, scripts bash, CI/CD et tâches planifiées (cron/timers).
---

# Automatisation

Ansible, n8n, scripts bash, CI/CD et tâches planifiées (cron/timers).

## Orchestration & Configuration

- [Premiers pas avec Ansible : créer un inventaire et lancer un premier playbook sur plusieurs VM Linux](premiers-pas-ansible-inventaire-playbook-vm-linux.md) — Gérer un parc de serveurs depuis un point unique via SSH sans agent.

## Infrastructure as Code (IaC)

- [Créer des environnements de test locaux reproductibles avec Vagrant et VirtualBox](creer-environnements-test-vagrant-virtualbox.md) — Automatiser la création et configuration de machines virtuelles via un fichier Vagrantfile.
- [Déployer son infrastructure avec Terraform (premiers pas)](debuter-terraform-infrastructure-as-code.md) — Déployer automatiquement des ressources (ex: conteneur Docker) via le code.
- [Automatiser la création de machines virtuelles Proxmox avec Terraform](creer-vm-proxmox-terraform.md) — Déployer automatiquement des machines virtuelles via l'API Proxmox VE.
- [Automatiser la création d'images systèmes (Templates) avec Packer](automatiser-creation-images-systemes-packer.md) — Générer des templates de machines virtuelles de manière reproductible.

## Intégration & Déploiement Continus (CI/CD)

- [Créer son premier pipeline CI/CD avec GitHub Actions](premier-pipeline-ci-cd-github-actions.md) — Automatiser le test et la validation de son code via les workflows natifs de GitHub.

## Conteneurs & Maintenance

- [Mettre à jour automatiquement ses conteneurs Docker avec Watchtower](mettre-a-jour-automatiquement-conteneurs-docker-avec-watchtower.md) — Automatiser la mise à jour des images de vos conteneurs en cours d'exécution.

## Scripts & Outils Ligne de Commande

- [Créer des alertes automatisées via Webhook (Slack/Discord) en Bash](creer-alertes-automatisees-webhook-bash.md) — Envoyer des notifications à partir de scripts shell vers des plateformes de messagerie.
- [Simplifier et automatiser les commandes de ses projets avec un Makefile](simplifier-automatiser-commandes-projets-makefile.md) — Regrouper les commandes récurrentes (Docker, tests, build) sous des raccourcis simples.
- [Sauvegardes automatisées avec script Bash robuste](sauvegarde-automatisee-script-bash-robuste.md) — Créer un script Bash avec gestion des erreurs et journalisation.

## Tâches Planifiées

- [Planifier un script avec un timer systemd sous Linux](planifier-script-timer-systemd-linux.md) — Remplacer le classique cron par des timers plus flexibles et observables.

## Workflows & No-Code

- [Les bases de n8n](bases-n8n.md) — Comprendre et manipuler les noeuds pour automatiser des flux de travail complexes.
