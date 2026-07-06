---
title: Déployer une instance GitLab CE auto-hébergée avec Docker Compose sur Ubuntu Server
date: 2026-07-05
author: Nicolas BODAINE
tags:
  - gitlab
  - docker
  - docker-compose
  - self-hosted
  - devops
  - linux
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Déployer une instance GitLab CE auto-hébergée avec Docker Compose sur Ubuntu Server

!!! abstract "Résumé"
    **GitLab CE** (Community Edition) est une plateforme DevOps complète et open source qui combine hébergement de dépôts Git, gestion de tickets (issues), intégration continue (CI/CD) et revue de code. Contrairement à GitHub, l'auto-hébergement de GitLab permet de garder le contrôle total sur ses données et son infrastructure. Ce tutoriel pas à pas montre comment déployer une instance GitLab CE fonctionnelle à partir de l'image Docker officielle, via un simple fichier `docker-compose.yml`, sur un serveur Ubuntu 24.04.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-07-05 |

## Contexte

Dans le cadre d'un apprentissage des outils DevOps (stagiaires TIP/TSSR, étudiants AIS) ou d'un projet collectif, il est fréquent de vouloir disposer d'une forge logicielle privée. **GitLab CE** répond à ce besoin en proposant le clonage Git, le suivi des tickets (issues) et la CI/CD le tout depuis une seule instance. L'**auto-hébergement** reste pertinent pour héberger ses dépôts en interne, maîtriser ses données et mettre en œuvre des pipelines CI/CD sans dépendance externe.

L'image Docker officielle **`gitlab/gitlab-ce:latest`** embarque l'ensemble des composants de GitLab (front-end web Puma, Nginx interne, Sidekiq, PostgreSQL, Redis, Prometheus) dans un seul conteneur, ce qui rend le déploiement particulièrement adapté à Docker Compose.

## Prérequis

- Une machine physique ou une **machine virtuelle** sous **Ubuntu 24.04**.
- **4 vCPU et 8 Go de RAM minimum** (les recommandations officielles GitLab Omnibus pour de petites équipes ; en-dessous, le démarrage et l'usage resteront instables).
- Au moins **20 Go d'espace disque libre** (dont 10 Go pour les données persistantes GitLab).
- Disposer des droits `sudo`.
- Avoir suivi le tutoriel [Installer Docker Engine et le plugin Docker Compose sur Ubuntu 24.04](installer-docker-engine-ubuntu-2404.md).
- Avoir lu [Créer et lancer une application multi-conteneurs avec Docker Compose](creer-lancer-application-multi-conteneurs-docker-compose.md) pour les notions de base (services, volumes, `restart`).
- Un **nom de domaine** (ou au minimum un enregistrement DNS local dans `/etc/hosts`) pointant vers le serveur, par exemple `gitlab.exemple.lan`.

!!! warning "Ressources minimales"
    GitLab est une application gourmande. En dessous de 4 Go de RAM, le conteneur peut ne pas démarrer correctement et le runner JobProcessor peut être tué par l'OOM killer. Les environnements de lab avec très peu de ressources devraient lancer GitLab en ajoutant la variable `GITLAB_SKIP_TAIL_LOGS=true` et `puma['worker_processes']=2` pour limiter la charge au démarrage.

## Procédure

### Étape 1 : Préparer la structure du projet

Comme pour tout projet Docker Compose, on dédie un dossier par application afin de séparer les configurations et suivre une convention de nommage claire.

```bash
sudo mkdir -p /srv/gitlab/{config,data,logs} && cd /srv/gitlab
sudo tree -L 2  /srv/gitlab
```

Les trois répertoires recevront les données persistantes de GitLab :

- `config/` : configuration principale (`gitlab.rb`) et secrets.
- `data/` : dépôts Git, base PostgreSQL, uploads utilisateurs.
- `logs/` : journaux d'application de GitLab et de Nginx interne.

### Étape 2 : Créer le fichier docker-compose.yml

Créez ensuite le fichier de déclaration de service à l'aide d'un éditeur de texte.

```bash
sudo nano docker-compose.yml
```

Insérez le contenu suivant. **Remplacez** `gitlab.exemple.lan` par votre nom de domaine et adaptez les chemins si vous n'utilisez pas `/srv/gitlab`.

```yaml title="docker-compose.yml"
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: gitlab
    restart: always
    hostname: gitlab.exemple.lan
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://gitlab.exemple.lan'
        gitlab_rails['gitlab_shell_ssh_port'] = 2222
        # Active le mode "minimal" pour les environnements de test
        puma['worker_processes'] = 2
        sidekiq['max_concurrency'] = 5
        prometheus_monitoring['enable'] = false
    ports:
      - "80:80"     # Interface web HTTP
      - "443:443"   # Interface web HTTPS (futur prise en charge TLS)
      - "2222:22"  # Ports SSH pour les opérations git over SSH
    volumes:
      - /srv/gitlab/config:/etc/gitlab
      - /srv/gitlab/logs:/var/log/gitlab
      - /srv/gitlab/data:/var/opt/gitlab
    shm_size: "256m"
```

!!! tip "Variable `GITLAB_OMNIBUS_CONFIG`"
    Cette variable spéciale permet d'injecter du contenu du fichier de configuration `gitlab.rb` **avant** le premier démarrage. Elle évite d'avoir à éditer manuellement le fichier dans le conteneur. Tout paramètre valide de GitLab Omnibus peut y être placé en respectant la syntaxe Ruby (par ex. `gitlab_rails['...'] = ...`).

### Étape 3 : Configurer la résolution DNS

Sur le serveur lui-même, vous devez être en mesure de vous connecter au côté web. Si vous ne disposez pas encore d'entrée DNS publique, créez une entrée locale dans le fichier `/etc/hosts`.

```bash
# Récupérer l'adresse IP du serveur
ip a | grep inet
# Ajouter une ligne correspondante vers « 192.168.x.x gitlab.exemple.lan »
sudo nano /etc/hosts
```

Exemple de contenu à ajouter dans `/etc/hosts` :

```text title="/etc/hosts"
192.168.1.20   gitlab.exemple.lan
```

Sur votre poste de travail client (mobile, PC de lab), ajoutez la même entrée pour accéder à l'interface web et au dépôt Git.

### Étape 4 : Démarrer l'instance

Lancez le conteneur en arrière-plan. GitLab démarre alors l'ensemble de ses composants internes, cela peut prendre **plusieurs minutes** lors du premier lancement (initialisation de la base de données et migrations).

```bash
sudo docker compose up -d
```

Vérifiez d'abord que le conteneur s'est correctement lancé :

```bash
sudo docker compose ps
```

```text title="Résultat attendu"
NAME      IMAGE                     COMMAND             SERVICE   STATUS          PORTS
gitlab    gitlab/gitlab-ce:latest   "/assets/wrapper"   gitlab    Up (healthy)    0.0.0.0:80->80/tcp, ...
```

### Étape 5 : Surveiller le démarrage

Le statut `Up` ne signifie pas que GitLab est prêt : il faut attendre que tous les services internes soient réellement disponibles. Le script officiel fournit une commande dédiée à cette vérification.

```bash
# Logs en direct
sudo docker compose logs -f gitlab
```

Le démarrage complet est signalé par les messages：

```text
gitlab | Thank you for using GitLab Community Edition!
gitlab | Running handlers complete
gitlab | Chef Infra Client finished
```

Interrompez l'affichage en direct avec `Ctrl+C`. Vérifiez alors spécifiquement le statut applicatif :

```bash
sudo docker exec -it gitlab gitlab-ctl status
```

```text title="Résultat attendu"
run: gitaly: (pid 1234) 300s
run: logrotate: (pid 1235) 300s
run: nginx: (pid 1236) 300s
run: postgresql: (pid 1237) 300s
run: puma: (pid 1238) 300s
run: redis: (pid 1239) 300s
run: sidekiq: (pid 1240) 300s
...
```

### Étape 6 : Récupérer le mot de passe initial de l'administrateur `root`

Au premier démarrage, GitLab génère automatiquement un **mot de passe administrateur temporaire**. Ce dernier est stocké dans un fichier spécifique, disponible dans le conteneur.

```bash
sudo docker exec -it gitlab cat /etc/gitlab/initial_root_password
```

```text title="Résultat"
# WARNING: This value is valid for the first 24 hours after installation.
# You MUST change this password immediately after the first login.

Password: NoZd8X8e2dW84bUo6Ytc5jpJf6qDe1o8xqkskM5MAdQ=
```

Copiez la valeur de `Password:` (sans le mot `Password:` lui-même) et conservez-la pour la prochaine étape.

!!! danger "Mot de passe temporaire expirant après 24 h"
    GitLab supprime automatiquement ce fichier après le premier redémarrage suivant l'installation ou après 24 heures. Si vous perdez ce mot de passe, la récupération nécessitera de réinitialiser le compte `root` via commandes Rails.

### Étape 7 : Première connexion au panneau Web

Ouvrez un navigateur sur votre poste client et accédez à l'URL :

```text
http://gitlab.exemple.lan
```

1. Saisissez l'identifiant `root` et le mot de passe récupéré à l'étape précédente.
2. Cliquez sur **Sign in**.
3. GitLab vous redirige immédiatement pour réinitialiser votre mot de passe. Choisissez un mot de passe fort et mémorisez-le (celui-ci remplace définitivement le mot de passe temporaire).
4. Vous arrivez sur le tableau de bord GitLab. Le déploiement de base est **opérationnel**.

### Étape 8 : Créer son premier projet

Le test de validation consiste à créer un premier dépôt, puis à le cloner en SSH pour vérifier le cycle complet.

Depuis l'interface Web :

1. Cliquez en haut à droite sur l'icône de menu et choisissez **Create new project**.
2. Sélectionnez **Create blank project**.
3. Saisissez le nom `test-gitlab` ; laissez la visibilité sur "Private".
4. Cochez **Initialiser with a README**, puis cliquez sur **Create project**.

### Étape 9 : Ajouter sa clé SSH publique

Pour manipuler les dépôts via le protocole SSH, GitLab doit connaître votre clé publique. Si vous n'en avez pas encore sur votre poste client, générez-en une :

```bash
# Sur le poste client
ssh-keygen -t ed25519 -C "mon.email@exemple.lan"
cat ~/.ssh/id_ed25519.pub
```

Dans l'interface GitLab :

1. Cliquez sur votre avatar en haut à droite, puis **Preferences**.
2. Dans le menu latéral gauche : **SSH Keys**.
3. Collez le contenu de votre clé publique dans le champ **Key**.
4. Donnez-lui un nom explicite et cliquez **Add key**.

### Étape 10 : Configurer le port SSH et cloner le projet en local

Rappelez-vous du fichier `docker-compose.yml` : le port SSH interne au conteneur (22) est exposé sur le port hôte **2222**. Vous devez l'indiquer à votre client SSH.

Sur votre poste client, créez ou éditez le fichier de configuration SSH :

```bash
nano ~/.ssh/config
```

```text title="~/.ssh/config"
Host gitlab.exemple.lan
    HostName gitlab.exemple.lan
    User git
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

Vérifiez ensuite la connectivité SSH :

```bash
ssh -T git@gitlab.exemple.lan
```

```text title="Résultat attendu"
PTY allocation request failed on channel 0
Welcome to GitLab, @root!
```

Clonez enfin votre dépôt fraîchement créé :

```bash
git clone git@gitlab.exemple.lan:root/test-gitlab.git
cd test-gitlab
echo "# Mon premier projet sur GitLab auto-hébergé" >> README.md
git add README.md && git commit -m "feat: premier commit depuis le clone SSH"
git push -u origin main
```

Le commit doit apparaître dans l'interface web GitLab sous **Code → Commits**.

## Vérification

Pour confirmer que l'instance est pleinement opérationnelle :

```bash
# Statut des services internes
sudo docker exec -it gitlab gitlab-ctl status

# Test de connectivité HTTP
curl -I http://gitlab.exemple.lan | head -n 5

# Test de clonage SSH (doit renvoyer le message de bienvenue GitLab)
ssh -T git@gitlab.exemple.lan
```

!!! success "Résultat attendu"
    - `gitlab-ctl status` : tous les services en `run: ... (pid N) Ns`.
    - `curl -I http://gitlab.exemple.lan` renvoie `HTTP/1.1 302 Found` (redirige vers la page de connexion).
    - `ssh -T` renvoie `Welcome to GitLab, @root!`.
    - L'interface web répond sur `http://gitlab.exemple.lan` et la création/le clone d'un projet fonctionne.

## Allumer son premier Runner CI/CD local (optionnel)

GitLab dispose d'un moteur de **CI/CD** intégré, mais son exécution nécessite le déploiement d'un **GitLab Runner** présent en parallèle du serveur principal. Pour rester dans le cadre d'un lab, on peut faire tourner le runner sur le même hôte via Docker Compose. Créez un second fichier `docker-compose.runner.yml` dans un dossier séparé :

```bash
mkdir -p /srv/gitlab-runner && cd /srv/gitlab-runner
nano docker-compose.yml
```

```yaml title="/srv/gitlab-runner/docker-compose.yml"
services:
  runner:
    image: gitlab/gitlab-runner:latest
    container_name: gitlab-runner
    restart: always
    volumes:
      - /srv/gitlab-runner/config:/etc/gitlab-runner
      - /var/run/docker.sock:/var/run/docker.sock
```

Lancez le runner, puis enregistrez-le auprès de votre instance (récupérez le **Registration token** depuis **Admin Area → CI/CD → Runners** dans l'interface GitLab) :

```bash
sudo docker compose up -d
sudo docker exec -it gitlab-runner gitlab-runner register \
  --url http://gitlab.exemple.lan \
  --token glrt-XXXXXXXXXXXXXXXX \
  --executor docker \
  --docker-image "alpine:latest" \
  --description "runner-lab-local"
```

Vous pouvez ensuite valider l'enregistrement :

```bash
sudo docker exec -it gitlab-runner gitlab-runner verify
```

!!! tip "Executor Docker"
    Pour l'`executor docker`, le runner monte la socket Docker du serveur (`/var/run/docker.sock`) afin de démarrer ses jobs dans des conteneurs isolés. Soyez conscient que cela accorde au Runner une grande puissance sur l'environnement Docker : en production, on privilégiera l'exécution depuis un serveur distinct, et non sur le même hôte que GitLab.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `sudo docker compose up -d` | Démarre GitLab en arrière-plan. |
| `sudo docker compose logs -f gitlab` | Affiche les journaux de GitLab en direct. |
| `sudo docker compose restart gitlab` | Redémarre proprement GitLab (les données sont conservées). |
| `sudo docker exec -it gitlab gitlab-ctl status` | Statut des services internes (Puma, PostgreSQL, Redis…). |
| `sudo docker exec -it gitlab gitlab-ctl reconfigure` | Reconfigure GitLab après modification de `/etc/gitlab/gitlab.rb`. Cette reconfiguration peut aussi être propagée en éditant la directive `GITLAB_OMNIBUS_CONFIG` puis en relançant le conteneur (qui appliquera les changements de configuration). |
| `sudo docker exec -it gitlab gitlab-ctl tail` | Affiche les logs en cours (équivalent à `tail -f`). |
| `sudo docker compose down` | Arrête le conteneur GitLab (les volumes persistent). |
| `ssh -T git@gitlab.exemple.lan` | Test de connexion SSH à GitLab. |

## Prochaines étapes recommandées

Pour aller plus loin après ce premier déploiement de lab, les étapes classiques sont :

1. **Activer HTTPS** avec Let's Encrypt (via le plugin `acme` intégré à GitLab et la directive `letsencrypt['enable'] = true` dans `GITLAB_OMNIBUS_CONFIG`).
2. **Mettre en place des sauvegardes** : utilisez `gitlab-backup create` (commande disponible via `gitlab-ctl`) et montez les archives de `/var/opt/gitlab/backups` vers un volume persistant ou distant.
3. **Restreindre les inscriptions** : dans **Admin Area → Settings → General → Sign-up restrictions**, désactivez les inscriptions publiques (le compte `root` peut créer les utilisateurs manuellement).
4. **Configurer le SMTP** pour les notifications par e-mail au sein du `GITLAB_OMNIBUS_CONFIG`.
5. **Branchez votre Runner à un projet** spécifique et lancez votre premier pipeline `.gitlab-ci.yml` (voir plus tard le tutoriel dédié CI/CD GitHub Actions comme point de comparaison).

## Ressources

- [Documentation officielle GitLab — Installation par image Docker](https://gitlab.com/docs/install/docker/) — Référence officielle pour le déploiement avec Docker Compose.
- [Documentation officielle GitLab — Omnibus configuration (gitlab.rb)](https://gitlab.com/docs/install/install.html#configure-the-docker-container-via-gitlab-omnibus-config) — Détails sur la variable `GITLAB_OMNIBUS_CONFIG` et tous les paramètres disponibles.
- [Documentation officielle GitLab — System requirements](https://gitlab.com/install/requirements/) — Recommandations matérielles minimales et conseillées pour l'Omnibus.
- [Documentation GitLab Runner — Install as Docker image](https://docs.gitlab.com/runner/install/docker.html) — Déploiement et enregistrement d'un Runner conteneurisé.
- [Documentation Ubuntu Server — `ufw` firewall](https://documentation.ubuntu.com/server/how-to/security/firewalls/) — Gestion du pare-feu pour ouvrir les ports 80, 443 et 2222.
- [Documentation Docker / Docker Compose](https://docs.docker.com/compose/) — Approfondissement des notions de services, volumes et `restart`.
