---
title: "Les tests en informatique : cas de synthèse et glossaire"
date: 2026-11-25
author: Nicolas BODAINE
tags:
  - tests
  - glossaire
  - cours
difficulty: intermédiaire
os: Indépendant du système
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Annexes : cas de synthèse et glossaire

!!! abstract "Résumé"
    Un **cas de synthèse** qui mobilise les cinq parties du parcours, sans pas-à-pas, puis le **glossaire** des termes rencontrés.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| Durée estimée | 15 min pour le cas de synthèse ; le glossaire sert de référence |
| Version décrite | Indépendante des outils |
| Place dans le parcours | Annexes du parcours [Les tests en informatique](index.md) |
| Dernière mise à jour | 2026-11-25 |

---

## 1. Cas de synthèse : la stratégie de tests d'une migration

Une collectivité de 400 agents remplace son vieil intranet par une application web de gestion des congés. L'équipe d'infrastructure doit installer deux serveurs web derrière un répartiteur de charge et un serveur de base de données, écrire un **script PowerShell** qui crée chaque nuit les comptes des nouveaux agents à partir de l'annuaire Active Directory, **exposer l'application sur Internet** pour le télétravail, et tout mettre en service le **lundi 4 janvier à 8 h**, jour où tous les agents posent leurs congés d'hiver. Le prestataire fournit son code dans un dépôt Git et utilise déjà Jenkins.

Proposer la **stratégie de tests** du projet :

1. Quels tests unitaires pour le script PowerShell, avec quel outil et quelles doublures ?
2. Quels tests d'intégration, et dans quel environnement ?
3. Quel test de performance, avec quelle exigence chiffrée et quelles précautions ?
4. Quels tests de sécurité avant l'ouverture sur Internet, et avec quel accord ?
5. Quelles étapes dans le pipeline Jenkins, et dans quel ordre ?
6. Quel test de fumée le lundi à 7 h 30 ?

??? success "Corrigé proposé"
    Il n'existe pas de réponse unique ; voici une stratégie argumentée.

    1. **Pester.** Découper le script en fonctions testables : construire l'identifiant (`prenom.nom`), gérer les homonymes, les accents et les noms composés (« Hélène Dupont-Lefèvre »), appeler l'API de l'application. Remplacer par des **doublures** (`Mock`) la commande `Get-ADUser` et l'appel à l'API (sur un poste sans le module Active Directory, déclarer d'abord une fonction vide `function Get-ADUser {}` pour que Pester puisse la remplacer). Tester les **cas limites** : annuaire vide, agent sans prénom, API indisponible.
    2. **En recette**, avec un annuaire de test et des comptes fictifs : les comptes sont-ils vraiment créés ? Le compte de service a-t-il les bons droits ? Les accents arrivent-ils intacts ? Les serveurs web joignent-ils la base (pare-feu, DNS, certificats) ? Le répartiteur de charge fonctionne-t-il si un serveur s'arrête ?
    3. Un **test de pic** : une grande partie des agents se connecte dans le même quart d'heure. Exigence possible : « avec 400 utilisateurs simultanés, 95 % des pages en moins de 2 secondes, moins de 1 % d'erreurs ». **JMeter** en ligne de commande, depuis une autre machine, avec un scénario réaliste (connexion, consultation du solde, dépôt d'une demande), en surveillant les serveurs. Puis un **test d'endurance** d'une nuit. Le tout en recette dimensionnée comme la production.
    4. **Scan de vulnérabilités** authentifié des trois serveurs (OpenVAS ou Nessus) ; **Nmap** sur tous les ports (`nmap -p- <adresse>`) depuis Internet pour vérifier que seul le port 443 est ouvert ; **Lynis** sur les serveurs Linux ; **ZAP** sur l'application ; un **test d'intrusion** en boîte grise centré sur le **contrôle d'accès** (A01 : un agent ne doit pas voir les congés d'un autre). **Autorisation écrite** de la direction obligatoire. Contre-audit après corrections.
    5. Du plus rapide au plus lent : tests unitaires → analyses statiques et SCA → déploiement en recette → tests d'intégration → scan ZAP → test de charge (la nuit) → **validation humaine** → production. Rapports JUnit publiés, alerte en cas d'échec, secrets dans les identifiants Jenkins.
    6. La page répond en HTTPS avec un certificat valide, un compte de test se connecte et voit son solde, les journaux ne montrent pas d'erreur, la supervision voit les trois serveurs. Et le **retour arrière** (l'ancien intranet prêt à être rallumé) est vérifié.

---

## 2. Glossaire

**Agent, contrôleur, job, build (Jenkins)** — Machine qui exécute les tâches ; serveur central ; tâche configurée ; exécution numérotée d'une tâche.

**Apdex** — Indice de satisfaction des utilisateurs entre 0 et 1, calculé à partir des temps de réponse.

**API** — Interface qui permet à des programmes de dialoguer entre eux.

**Assertion** — Vérification automatique que le résultat obtenu est égal au résultat attendu.

**Big bang / intégration incrémentale** — Assembler tous les composants d'un coup / un par un, avant de tester.

**Boîte noire / grise / blanche** — Connaissance de l'intérieur du système au moment du test : aucune, partielle, complète.

**Cas de test** — Description d'un test : conditions de départ, actions, données, résultat attendu.

**Couverture de code** — Part du code exécutée au moins une fois par les tests.

**CVE** — Identifiant unique d'une vulnérabilité publique (`CVE-2021-44228`).

**CVSS** — Note de gravité d'une vulnérabilité, de 0 à 10.

**Cycle en V** — Modèle où chaque étape de conception est vérifiée par un niveau de test correspondant.

**Débit** — Nombre de requêtes traitées par seconde.

**Décaler à gauche** (*shift left*) — Placer les tests le plus tôt possible dans le pipeline.

**Défaillance** — Comportement incorrect observé quand un défaut s'exécute.

**Défaut** (bug) — Imperfection dans le code ou la configuration.

**Déploiement continu** — Mise en production automatique de chaque version qui passe tous les tests.

**DevOps / DevSecOps** — Démarche qui rapproche développement et exploitation ; avec la sécurité intégrée à chaque étape.

**Doublure** (*mock*, *stub*) — Objet qui remplace une dépendance réelle (disque, base, annuaire) pendant un test.

**Durcissement** — Réduction de la surface d'attaque d'un système.

**Environnement de recette** (ou de préproduction) — Copie fidèle de la production, réservée aux tests.

**Erreur** — Action humaine qui crée un défaut.

**Exploit** — Programme ou technique qui utilise concrètement une vulnérabilité.

**Faux positif** — Alerte pour un problème qui n'existe pas réellement.

**Goulet d'étranglement** — Composant qui sature le premier et limite tout le système.

**IaC** (*Infrastructure as Code*) — Infrastructure décrite par des fichiers de code (Ansible, Terraform).

**Intégration continue** — Construction et test automatiques à chaque modification envoyée dans le dépôt.

**Jenkinsfile** — Fichier qui décrit un pipeline Jenkins, versionné avec le projet.

**Linter** — Outil d'analyse statique qui repère les erreurs dans le code (shellcheck, PSScriptAnalyzer).

**Livraison continue** — Chaque version validée est prête pour la production ; la décision reste humaine.

**OWASP** — Fondation qui publie des guides et outils libres de sécurité applicative, dont le Top 10.

**Percentile** — Valeur sous laquelle se trouve un pourcentage donné des mesures (P95 : 95 % des requêtes sont plus rapides).

**Pipeline** — Suite d'étapes automatiques qu'une modification traverse du dépôt à la production.

**Port** — Numéro par lequel un service réseau écoute sur une machine (22 pour SSH, 443 pour HTTPS).

**Proxy** — Intermédiaire placé entre un navigateur et un site, qui voit passer toutes les requêtes.

**Pyramide des tests** — Beaucoup de tests unitaires, moins de tests d'intégration, peu de tests de bout en bout.

**Recette** (test d'acceptation) — Vérification, par le client ou les utilisateurs, que le système répond au besoin.

**Régression (test de)** — Nouvelle exécution des tests existants pour vérifier qu'une modification n'a rien cassé.

**SAST / DAST / SCA** — Analyse du code source sans l'exécuter / attaque de l'application en fonctionnement / inventaire des bibliothèques vulnérables.

**Scan de vulnérabilités** — Recherche automatique des failles connues sur des machines ou des applications.

**Surface d'attaque** — Tout ce qu'un attaquant peut atteindre : ports, applications, comptes, personnes.

**TDD** — Écrire le test avant le code, en cycles rouge – vert – remanier.

**Test d'endurance / de pic / de stress / de charge** — Charge normale sur une longue durée / montée brutale et brève / au-delà de la capacité jusqu'à la rupture / charge attendue.

**Test d'intégration** — Vérifie que plusieurs composants fonctionnent correctement ensemble.

**Test d'intrusion** (*pentest*) — Simulation d'attaque autorisée qui exploite les failles pour prouver un impact réel.

**Test de confirmation** — Nouvelle exécution du test qui avait échoué, pour vérifier une correction.

**Test de fumée** — Quelques vérifications rapides après une installation ou un déploiement.

**Test fonctionnel / non fonctionnel** — Vérifie ce que fait le système / comment il le fait (performance, sécurité…).

**Test négatif** — Test qui vérifie que ce qui doit être refusé ou bloqué l'est vraiment.

**Test unitaire** — Test automatique d'un petit morceau de code isolé, le plus souvent une fonction.

**Vulnérabilité** — Faiblesse d'un système qui peut être exploitée pour nuire.

**Webhook** — Requête HTTP envoyée automatiquement par un service pour en prévenir un autre d'un événement.

---

Partie précédente : [Tests d'intégration et CI/CD](05-tests-integration-et-ci-cd.md) · Retour à l'[accueil du parcours](index.md)

*[API]: Application Programming Interface : interface de programmation
*[SSH]: Secure Shell
*[HTTPS]: HTTP sécurisé par TLS
*[SCA]: Software Composition Analysis
*[DNS]: Domain Name System
