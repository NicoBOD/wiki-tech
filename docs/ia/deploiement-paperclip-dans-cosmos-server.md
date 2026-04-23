---
title: Déploiement de Paperclip derrière Cosmos Server
date: 2026-04-15
author: Nicolas BODAINE
tags:
  - docker
  - paperclip
  - cosmos-server
  - reverse-proxy
  - self-hosted
  - ia
difficulty: intermédiaire
os: Debian 13 (Azure VM)
status: publié
---

# Déploiement de Paperclip derrière Cosmos Server

!!! abstract "Résumé"
    Ce guide décrit le déploiement complet de **Paperclip AI** sur une VM Debian 13 hébergée dans Azure, en cohabitation avec **Cosmos Server** qui agit comme reverse proxy HTTPS. Paperclip est déployé via `docker-compose` (conteneurs isolés), Cosmos assure le certificat Let's Encrypt et le routage HTTPS vers `paperclip.tutotech.org`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Debian 13 — Azure VM |
| Reverse proxy | Cosmos Server v0.22.9 (service systemd natif) |
| Application | Paperclip AI (image GHCR) |
| Dernière mise à jour | 2026-04-15 |

---

## Contexte

### Qu'est-ce que Paperclip ?

[Paperclip AI](https://github.com/paperclipai/paperclip) est une plateforme open-source d'**orchestration d'agents IA**. Elle permet de créer, gérer et surveiller des équipes d'agents autonomes (Claude, Cursor, etc.) depuis un tableau de bord centralisé. Elle fournit :

- Un tableau de bord web (UI)
- Une API REST
- Une base de données PostgreSQL pour la persistance
- Un système d'authentification (mode `authenticated`)

### Qu'est-ce que Cosmos Server ?

[Cosmos Server](https://github.com/azukaar/Cosmos-Server) est une plateforme de gestion de serveur self-hosted. Dans ce guide, on l'utilise principalement comme **reverse proxy HTTPS** avec génération automatique de certificats **Let's Encrypt** (via challenge DNS Infomaniak).

!!! note "Installation de Cosmos Server"
    Cosmos est installé en tant que **service systemd natif** (binaire `/opt/cosmos/cosmos`), **pas** comme conteneur Docker. Cette distinction est importante pour la configuration réseau.

### Architecture mise en place

```
Internet
    │
    ▼ HTTPS (443)
Cosmos Server (systemd, ports 80/443 sur l'hôte)
    │
    │ http://localhost:3100
    ▼
paperclip-server-1 (Docker, port 127.0.0.1:3100)
    │
    │ réseau Docker interne
    ▼
paperclip-db-1 (PostgreSQL 17, port 5432 interne uniquement)
```

**Points clés de cette architecture :**

- Cosmos tourne nativement sur l'hôte → il peut atteindre `localhost:3100` directement
- Paperclip n'expose son port que sur `127.0.0.1` (pas accessible depuis Internet sans passer par Cosmos)
- PostgreSQL n'est **jamais** exposé à l'extérieur (réseau Docker interne uniquement)
- Cosmos gère automatiquement le certificat TLS pour `paperclip.tutotech.org`

---

## Prérequis

- VM Debian 13 avec Docker et Docker Compose installés
- Cosmos Server opérationnel (service `CosmosCloud` actif) avec un domaine configuré (ex: `cosmos.tutotech.org`)
- Entrée DNS **A** pointant `paperclip.tutotech.org` vers l'IP publique de la VM (ex: `20.x.x.x`)
- Accès `sudo` sur la VM
- Cosmos configuré avec un provider DNS Let's Encrypt (ex: Infomaniak) pour le challenge DNS automatique

!!! tip "Vérifier que le DNS est propagé"
    Avant de commencer, vérifiez que votre enregistrement DNS est actif :
    ```bash
    dig +short paperclip.tutotech.org
    # Doit retourner l'IP publique de votre VM
    ```

---

## Procédure

### Étape 1 : Vérifier l'environnement existant

Avant de déployer, vérifiez que Cosmos fonctionne et identifiez les réseaux Docker existants pour éviter les conflits.

```bash
# Vérifier que Cosmos tourne bien
systemctl status CosmosCloud

# Lister les conteneurs actifs
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"

# Lister les réseaux Docker
docker network ls
```

!!! success "Résultat attendu"
    Le service `CosmosCloud` doit être `active (running)`. Vérifiez qu'aucun conteneur existant n'utilise le port 3100.

---

### Étape 2 : Créer le répertoire de déploiement

Par convention, tous les stacks docker-compose sont regroupés dans `/home/<user>/docker-compose/`.

```bash
mkdir -p /home/nicolas.bodaine/docker-compose/paperclip
cd /home/nicolas.bodaine/docker-compose/paperclip
```

---

### Étape 3 : Générer les secrets

Paperclip nécessite deux secrets : un pour l'authentification (`BETTER_AUTH_SECRET`) et un mot de passe PostgreSQL.

```bash
# Générer BETTER_AUTH_SECRET (64 caractères hex)
openssl rand -hex 32

# Générer le mot de passe PostgreSQL (32 caractères hex)
openssl rand -hex 16
```

!!! warning "Notez ces valeurs"
    Sauvegardez ces deux chaînes, vous en aurez besoin dans les fichiers de configuration ci-dessous.

---

### Étape 4 : Créer le fichier `.env`

Le fichier `.env` contient tous les secrets et variables de configuration. Il est lu automatiquement par `docker compose`.

```bash
nano /home/nicolas.bodaine/docker-compose/paperclip/.env
```

Contenu du fichier :

```ini title=".env"
# ============================================================
# Paperclip - Configuration
# ============================================================
# IMPORTANT : Ce fichier contient des secrets.
# Ne jamais le committer dans un dépôt Git.
# ============================================================

# Secret d'authentification (généré avec openssl rand -hex 32)
BETTER_AUTH_SECRET=<votre_secret_64_chars>

# Mot de passe PostgreSQL interne (généré avec openssl rand -hex 16)
POSTGRES_PASSWORD=<votre_password_32_chars>

# Clés API IA (optionnel, à renseigner plus tard)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

Sécurisez le fichier (lisible uniquement par le propriétaire) :

```bash
chmod 600 /home/nicolas.bodaine/docker-compose/paperclip/.env
```

---

### Étape 5 : Créer le fichier `docker-compose.yml`

Ce fichier définit deux services : le serveur Paperclip et sa base de données PostgreSQL.

```bash
nano /home/nicolas.bodaine/docker-compose/paperclip/docker-compose.yml
```

Contenu du fichier :

```yaml title="docker-compose.yml" linenums="1"
services:
  db:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: paperclip
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: paperclip
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U paperclip -d paperclip"]
      interval: 2s
      timeout: 5s
      retries: 30
    volumes:
      - pgdata:/var/lib/postgresql/data
    # PostgreSQL n'est PAS exposé à l'hôte — réseau Docker interne uniquement

  server:
    image: ghcr.io/paperclipai/paperclip:latest
    restart: unless-stopped
    ports:
      # Exposé uniquement sur localhost : Cosmos (service natif) peut y accéder,
      # mais le port n'est pas accessible depuis l'extérieur directement.
      - "127.0.0.1:3100:3100"
    environment:
      DATABASE_URL: postgres://paperclip:${POSTGRES_PASSWORD}@db:5432/paperclip
      PORT: "3100"
      HOST: "0.0.0.0"
      SERVE_UI: "true"
      PAPERCLIP_DEPLOYMENT_MODE: "authenticated"
      PAPERCLIP_DEPLOYMENT_EXPOSURE: "private"
      PAPERCLIP_PUBLIC_URL: "https://paperclip.tutotech.org"  # ← Adapter à votre domaine
      BETTER_AUTH_SECRET: "${BETTER_AUTH_SECRET}"
      OPENAI_API_KEY: "${OPENAI_API_KEY:-}"
      ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY:-}"
      # Stocke le token OAuth Claude CLI dans le volume persistant /paperclip
      # Sans cette variable, le token est perdu à chaque recréation du conteneur
      CLAUDE_CONFIG_DIR: "/paperclip/.claude-config"
    volumes:

      - paperclip-data:/paperclip
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
  paperclip-data:
```

**Explications des choix importants :**

| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| `image` | `ghcr.io/paperclipai/paperclip:latest` | Image pré-compilée sur GitHub Container Registry — pas besoin de cloner et builder le code source |
| `ports` | `127.0.0.1:3100:3100` | Expose sur localhost uniquement — Cosmos y accède via `http://localhost:3100`, Internet ne peut pas y accéder directement |
| `PAPERCLIP_DEPLOYMENT_MODE` | `authenticated` | Mode multi-utilisateurs avec authentification — indispensable pour une exposition sur Internet |
| `PAPERCLIP_PUBLIC_URL` | `https://paperclip.tutotech.org` | URL publique utilisée pour les cookies d'auth et les redirections OAuth |
| `restart: unless-stopped` | — | Le conteneur redémarre automatiquement après un reboot de la VM |
| `depends_on` + `healthcheck` | — | Le serveur attend que PostgreSQL soit prêt avant de démarrer |
| `CLAUDE_CONFIG_DIR` | `/paperclip/.claude-config` | Persiste le token OAuth de Claude CLI dans le volume — indispensable pour la connexion via abonnement |


!!! warning "Adapter le domaine"
    Remplacez toutes les occurrences de `paperclip.tutotech.org` par votre propre domaine.

---

### Étape 6 : Démarrer le stack Docker

```bash
cd /home/nicolas.bodaine/docker-compose/paperclip

# Télécharger les images
docker compose pull

# Démarrer en arrière-plan
docker compose up -d

# Vérifier que les deux conteneurs tournent
docker compose ps
```

!!! success "Résultat attendu"
    ```
    NAME                 STATUS
    paperclip-db-1       Up (healthy)
    paperclip-server-1   Up
    ```

Vérifiez les logs du serveur :

```bash
docker compose logs server --tail=30
```

!!! success "Résultat attendu dans les logs"
    ```
    [INFO] Using external PostgreSQL via DATABASE_URL/config
    [INFO] Authenticated mode auth origin configuration {"authPublicBaseUrl":"https://paperclip.tutotech.org"...}
    [INFO] Server listening on 0.0.0.0:3100
    ```

---

### Étape 7 : Configurer le reverse proxy dans Cosmos Server

Cosmos Server stocke sa configuration dans `/var/lib/cosmos/cosmos.config.json`. Ce fichier contient notamment un tableau `HTTPConfig.ProxyConfig.Routes` qui liste toutes les routes de reverse proxy.

!!! danger "Fichier sensible"
    Ce fichier contient des **certificats TLS et des clés privées**. Faites toujours une sauvegarde avant de le modifier.

!!! tip "En cas de redéploiement"
    Si vous redéployez Paperclip sur un serveur où Cosmos était déjà configuré pour ce domaine, vérifiez si la route existe avant de lancer le script :

    ```bash
    sudo python3 -c "
    import json
    c = json.load(open('/var/lib/cosmos/cosmos.config.json'))
    routes = c['HTTPConfig']['ProxyConfig']['Routes']
    for r in routes: print(r['Name'], '->', r['Target'])
    "
    ```

    Si la ligne `paperclip -> http://localhost:3100` apparaît, **passez directement à l'Étape 8** — la route et le certificat Let's Encrypt sont encore valides.

#### 7.1 — Sauvegarder la configuration Cosmos

```bash
sudo cp /var/lib/cosmos/cosmos.config.json \
    /var/lib/cosmos/cosmos.config.json.bak.$(date +%Y%m%d_%H%M%S)
```

#### 7.2 — Injecter la route Paperclip

Le script Python suivant lit le fichier de config, ajoute la route si elle n'existe pas, et réécrit le fichier en JSON valide.

```bash
sudo python3 - << 'PYEOF'
import json

config_path = "/var/lib/cosmos/cosmos.config.json"

with open(config_path, "r") as f:
    config = json.load(f)

paperclip_route = {
    "Name": "paperclip",                          # Nom unique de la route
    "Description": "Paperclip AI Platform",
    "UseHost": True,                              # Matcher sur le nom d'hôte
    "Host": "paperclip.tutotech.org",             # ← Adapter à votre domaine
    "UsePathPrefix": False,
    "PathPrefix": "",
    "Target": "http://localhost:3100",            # Cible du proxy
    "Mode": "PROXY",                              # Mode proxy HTTP
    "SmartShield": {"Enabled": False},
    "AuthEnabled": False,                         # Pas d'auth supplémentaire (Paperclip gère lui-même)
    "AdminOnly": False,
    "Disabled": False,
    "Timeout": 0,
    "ThrottlePerMinute": 0,
    "CORSOrigin": "",
    "BlockCommonBots": False,
    "BlockAPIAbuse": False,
    "AcceptInsecureHTTPSTarget": False,
    "HideFromDashboard": False,
    "DisableHeaderHardening": False
}

routes = config["HTTPConfig"]["ProxyConfig"]["Routes"]
existing = [r for r in routes if r.get("Name") == "paperclip"]

if existing:
    print("Route 'paperclip' existe déjà.")
else:
    routes.append(paperclip_route)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    print("Route 'paperclip' ajoutée avec succès.")

# Vérification
with open(config_path, "r") as f:
    verify = json.load(f)
for r in verify["HTTPConfig"]["ProxyConfig"]["Routes"]:
    print(f"  Route: {r['Name']} → {r['Target']}")
PYEOF
```

!!! note "Format JSON de Cosmos"
    Le fichier `cosmos.config.json` utilise des noms de champs en **PascalCase** (ex: `UseHost`, `PathPrefix`). C'est le format natif Go de Cosmos Server.

#### 7.3 — Redémarrer Cosmos pour appliquer la route

```bash
sudo systemctl restart CosmosCloud

# Suivre les logs pour voir la demande de certificat
sudo journalctl -u CosmosCloud -f --no-pager
```

!!! success "Résultat attendu dans les logs"
    ```
    [INFO] [paperclip.tutotech.org] acme: Obtaining bundled SAN certificate
    [INFO] [paperclip.tutotech.org] acme: use dns-01 solver
    [INFO] Saved new LETSENCRYPT TLS certificate
    [INFO] Added route: [PROXY] paperclip.tutotech.org to http://localhost:3100
    [INFO] TLS certificate exist, starting HTTPS servers and redirecting HTTP to HTTPS
    ```

    Cosmos demande automatiquement un certificat Let's Encrypt pour `paperclip.tutotech.org` via le challenge DNS. Le certificat est un **SAN** qui regroupe tous vos domaines.

---

### Étape 8 : Initialiser l'instance Paperclip

Au premier démarrage, Paperclip n'a pas de fichier de configuration d'instance (`config.json`). Il faut le générer via la commande `onboard`.

#### 8.1 — Lancer l'onboarding

```bash
docker exec paperclip-server-1 \
    node cli/node_modules/tsx/dist/cli.mjs cli/src/index.ts onboard --yes
```

Cette commande crée le fichier `/paperclip/instances/default/config.json` dans le volume Docker.

Vérifiez que les fichiers ont bien été créés avant de passer à l'étape suivante :

```bash
sudo ls /var/lib/docker/volumes/paperclip_paperclip-data/_data/instances/default/
```

!!! success "Résultat attendu"
    ```
    .env  config.json  data  logs  secrets  telemetry
    ```

Si config.json n'apparaît pas encore, attendez quelques secondes et relancez la commande.

#### 8.2 — Corriger la configuration d'instance

!!! warning "La commande `onboard --yes` génère une config incomplète"
    Par défaut, `onboard --yes` crée une configuration en mode `local_trusted` (adapté pour un usage local) alors que nous avons besoin du mode `authenticated` (pour une exposition Internet). De plus, certains champs de la section `auth` sont absents ou incorrects. Il faut corriger ces valeurs manuellement.

Trouvez le volume Docker sur l'hôte :

```bash
docker volume inspect paperclip_paperclip-data --format '{{.Mountpoint}}'
# Retourne généralement : /var/lib/docker/volumes/paperclip_paperclip-data/_data
```

Corrigez le fichier de configuration :

```bash
sudo python3 - << 'PYEOF'
import json

path = "/var/lib/docker/volumes/paperclip_paperclip-data/_data/instances/default/config.json"

with open(path) as f:
    c = json.load(f)

# Correction 1 : mode de déploiement
c['server']['deploymentMode'] = 'authenticated'

# Correction 2 : bind sur toutes les interfaces (nécessaire pour Docker)
# Valeurs acceptées : 'loopback' | 'lan' | 'tailnet' | 'custom'
# 'lan' = 0.0.0.0 (toutes interfaces), ce qui est nécessaire pour que
# Docker puisse router le trafic vers le conteneur
c['server']['bind'] = 'lan'
c['server']['host'] = '0.0.0.0'

# Correction 3 : URL publique dans la section server
c['server']['publicUrl'] = 'https://paperclip.tutotech.org'  # ← Adapter
c['server']['allowedHostnames'] = ['paperclip.tutotech.org']  # ← Adapter

# Correction 4 : configuration auth
# 'explicit' = utiliser l'URL ci-dessous pour les cookies et redirections
c['auth']['baseUrlMode'] = 'explicit'
c['auth']['publicBaseUrl'] = 'https://paperclip.tutotech.org'  # ← Adapter
c['auth'].pop('baseUrl', None)  # Supprimer l'ancienne clé incorrecte si présente

with open(path, 'w') as f:
    json.dump(c, f, indent=2)

print("Configuration corrigée :")
print(f"  deploymentMode : {c['server']['deploymentMode']}")
print(f"  bind           : {c['server']['bind']}")
print(f"  publicUrl      : {c['server']['publicUrl']}")
print(f"  auth.mode      : {c['auth']['baseUrlMode']}")
print(f"  auth.publicUrl : {c['auth']['publicBaseUrl']}")
PYEOF
```

#### 8.3 — Corriger les permissions

La commande `onboard` s'exécute en tant que `root` dans le conteneur, ce qui crée des fichiers inaccessibles au processus Paperclip (qui tourne en tant que `node`, uid 1000).

```bash
sudo chown -R 1000:1000 \
    /var/lib/docker/volumes/paperclip_paperclip-data/_data/instances/default/
```

#### 8.4 — Redémarrer le conteneur

```bash
cd /home/nicolas.bodaine/docker-compose/paperclip
docker compose restart server

# Vérifier les logs
docker compose logs server --tail=20
```

!!! success "Résultat attendu"
    ```
    [INFO] Using external PostgreSQL via DATABASE_URL/config
    [INFO] Authenticated mode auth origin configuration
           {"authBaseUrlMode":"explicit","authPublicBaseUrl":"https://paperclip.tutotech.org"...}
    [INFO] Server listening on 0.0.0.0:3100
    ```

---

### Étape 9 : Créer le premier compte administrateur

Paperclip en mode `authenticated` requiert la création d'un premier compte admin via une URL d'invitation spéciale.

```bash
docker exec paperclip-server-1 \
    node cli/node_modules/tsx/dist/cli.mjs cli/src/index.ts auth bootstrap-ceo
```

!!! success "Résultat attendu"
    ```
    ◆  Created bootstrap CEO invite.
    │
    │  Invite URL: https://paperclip.tutotech.org/invite/pcp_bootstrap_xxxxx
    │
    │  Expires: 2026-04-18T18:16:56.822Z
    ```

!!! warning "L'URL d'invitation est à usage unique et expire dans 72h"
    Ouvrez immédiatement ce lien dans votre navigateur pour créer votre compte administrateur. Si le lien expire, relancez la commande pour en générer un nouveau.

Ouvrez l'URL dans votre navigateur :

```
https://paperclip.tutotech.org/invite/pcp_bootstrap_xxxxx
```

---
## Connexion à Claude via abonnement (sans clé API)

### Contexte : deux façons d'utiliser Claude avec Paperclip

Paperclip peut se connecter à Claude de deux manières différentes :

| Méthode | Fonctionnement | Quand l'utiliser |
|---------|----------------|-----------------|
| **Clé API** (`ANTHROPIC_API_KEY`) | Appels directs à l'API Anthropic, facturés à l'usage (tokens) | Usage professionnel, volume important |
| **Abonnement OAuth** | Utilise votre compte Claude.ai (Pro, Max, Team) via une connexion OAuth | Vous avez déjà un abonnement Claude actif |

Ce guide décrit la méthode **abonnement OAuth**, qui permet d'utiliser Paperclip sans consommer de tokens API.

!!! note "Claude CLI déjà inclus"
    Contrairement à certains guides tiers, **il n'est pas nécessaire d'installer Node.js ni Claude CLI manuellement** dans le conteneur. L'image `ghcr.io/paperclipai/paperclip:latest` inclut déjà Claude CLI (`/usr/local/bin/claude`). Installer une deuxième version crée des conflits.

---

### Étape 10 : Préparer la persistance du token OAuth

Le token d'authentification OAuth est stocké par Claude CLI dans un répertoire de configuration. Par défaut, ce répertoire est `~/.claude/` — qui se trouve dans la **couche éphémère** du conteneur et est effacé à chaque recréation (mise à jour d'image, `docker compose down && up`).

La solution est de définir la variable `CLAUDE_CONFIG_DIR` pour pointer vers un chemin à l'intérieur du volume `/paperclip`, qui lui est persistant.

Vérifiez que votre `docker-compose.yml` contient bien cette ligne dans la section `environment` du service `server` :

```yaml title="docker-compose.yml (extrait)"
environment:
  # ...autres variables...
  CLAUDE_CONFIG_DIR: "/paperclip/.claude-config"
```

## Problèmes rencontrés

### Problème 1 : `onboard --yes` génère un mode `local_trusted`

!!! failure "Symptôme"
    Après avoir lancé `onboard --yes`, la commande `bootstrap-ceo` répond :
    ```
    Deployment mode is local_trusted. Bootstrap CEO invite is only required for authenticated mode.
    ```

**Cause :** La commande `onboard --yes` accepte tous les défauts qui correspondent à un usage local (sans authentification). Elle génère un `config.json` avec `deploymentMode: "local_trusted"`.

**Solution :** Corriger manuellement le `config.json` dans le volume Docker en suivant l'étape 8.2.

---

### Problème 2 : Valeur invalide pour `server.bind`

!!! failure "Message d'erreur"
    ```
    Invalid config at /paperclip/instances/default/config.json:
    server.bind: Invalid enum value. Expected 'loopback' | 'lan' | 'tailnet' | 'custom', received 'all'
    ```

**Cause :** La valeur `"all"` n'est pas acceptée pour `server.bind`.

**Solution :** Utiliser `"lan"` qui correspond à `0.0.0.0` (toutes les interfaces réseau).

---

### Problème 3 : Champ `auth.publicBaseUrl` manquant

!!! failure "Message d'erreur"
    ```
    Invalid config: auth.publicBaseUrl: auth.publicBaseUrl is required when auth.baseUrlMode is explicit
    ```

**Cause :** Lorsque `auth.baseUrlMode` est `"explicit"`, le champ `auth.publicBaseUrl` est obligatoire. Le champ incorrect `auth.baseUrl` (sans "public") ne suffit pas.

**Solution :** Utiliser `auth.publicBaseUrl` (voir étape 8.2).

---

### Problème 4 : Permission denied sur `.env`

!!! failure "Message d'erreur"
    ```
    Error: EACCES: permission denied, open '/paperclip/instances/default/.env'
    ```

**Cause :** La commande `onboard` s'exécute en `root` dans le conteneur et crée des fichiers avec `owner: root`. Mais le serveur Paperclip tourne en tant qu'utilisateur `node` (uid 1000) qui n'a pas accès aux fichiers root.

**Solution :** Corriger la propriété des fichiers avec `chown` (étape 8.3).

---

## Vérification

### Vérifier que les conteneurs tournent

```bash
cd /home/nicolas.bodaine/docker-compose/paperclip
docker compose ps
```

!!! success "Résultat attendu"
    ```
    NAME                 STATUS
    paperclip-db-1       Up (healthy)
    paperclip-server-1   Up
    ```

### Vérifier que le port est accessible depuis l'hôte

```bash
curl -s http://localhost:3100/api/health | python3 -m json.tool
```

!!! success "Résultat attendu"
    Un objet JSON avec le statut de santé de l'application.

### Vérifier que le HTTPS fonctionne depuis l'extérieur

```bash
curl -I https://paperclip.tutotech.org/api/health
```

!!! success "Résultat attendu"
    ```
    HTTP/2 200
    ```

### Vérifier les logs Cosmos pour le routing

```bash
sudo journalctl -u CosmosCloud --since "5 minutes ago" --no-pager \
    | grep paperclip
```

!!! success "Résultat attendu"
    Des lignes `[REQ] GET https://paperclip.tutotech.org/...` avec le code `200`.

---

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `docker compose up -d` | Démarrer le stack en arrière-plan |
| `docker compose down` | Arrêter et supprimer les conteneurs (les volumes sont conservés) |
| `docker compose restart server` | Redémarrer uniquement le serveur Paperclip |
| `docker compose logs server -f` | Suivre les logs en temps réel |
| `docker compose pull && docker compose up -d` | Mettre à jour vers la dernière image |
| `sudo systemctl restart CosmosCloud` | Redémarrer Cosmos après modification de sa config |
| `sudo journalctl -u CosmosCloud -f` | Suivre les logs Cosmos en temps réel |

### Ajouter les clés API plus tard

Éditez le fichier `.env` :

```bash
nano /home/nicolas.bodaine/docker-compose/paperclip/.env
```

Renseignez les valeurs :

```ini
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
```

Puis redémarrez le serveur :

```bash
cd /home/nicolas.bodaine/docker-compose/paperclip
docker compose up -d
```

### Régénérer une invitation admin

Si l'URL d'invitation a expiré ou a déjà été utilisée :

```bash
docker exec paperclip-server-1 \
    node cli/node_modules/tsx/dist/cli.mjs cli/src/index.ts auth bootstrap-ceo
```

### Redéploiement complet (volumes supprimés)

Si vous avez supprimé la stack et ses volumes et souhaitez repartir de zéro, voici la séquence complète dans l'ordre correct :

```bash
cd /home/nicolas.bodaine/docker-compose/paperclip

# 1. Démarrer la stack
docker compose up -d

# 2. Lancer l'onboarding (génère master key + config.json)
docker exec paperclip-server-1 \
    node cli/node_modules/tsx/dist/cli.mjs cli/src/index.ts onboard --yes

# 3. Vérifier que config.json est créé avant de continuer
sudo ls /var/lib/docker/volumes/paperclip_paperclip-data/_data/instances/default/

# 4. Corriger config.json (authenticated, lan, publicUrl, auth)
sudo python3 - << 'PYEOF'
import json
path = "/var/lib/docker/volumes/paperclip_paperclip-data/_data/instances/default/config.json"
with open(path) as f: c = json.load(f)
c['server']['deploymentMode'] = 'authenticated'
c['server']['bind'] = 'lan'
c['server']['host'] = '0.0.0.0'
c['server']['publicUrl'] = 'https://paperclip.tutotech.org'
c['server']['allowedHostnames'] = ['paperclip.tutotech.org']
c['auth']['baseUrlMode'] = 'explicit'
c['auth']['publicBaseUrl'] = 'https://paperclip.tutotech.org'
c['auth'].pop('baseUrl', None)
with open(path, 'w') as f: json.dump(c, f, indent=2)
print("config.json corrigé ✓")
PYEOF

# 5. Corriger les permissions
sudo chown -R 1000:1000 \
    /var/lib/docker/volumes/paperclip_paperclip-data/_data/instances/default/

# 6. Redémarrer le serveur
docker compose restart server

# 7. Générer l'invitation admin
docker exec paperclip-server-1 \
    node cli/node_modules/tsx/dist/cli.mjs cli/src/index.ts auth bootstrap-ceo
```

### Ajouter une nouvelle route dans Cosmos

Pour tout nouveau service à proxifier derrière Cosmos, répliquer le script Python de l'étape 7.2 en adaptant `Name`, `Host` et `Target`, puis `sudo systemctl restart CosmosCloud`.

---

## Glossaire

Cosmos Server
:   Plateforme de gestion de serveur self-hosted (reverse proxy, gestion Docker, authentification, VPN). Dans ce guide, utilisé uniquement comme reverse proxy HTTPS.

Paperclip AI
:   Plateforme d'orchestration d'agents IA. Fournit un tableau de bord web et une API pour gérer des agents autonomes.

Reverse proxy
:   Composant réseau qui reçoit les requêtes HTTP(S) entrantes et les redirige vers le bon service interne selon le nom d'hôte ou le chemin URL.

Challenge DNS
:   Méthode de validation Let's Encrypt qui prouve la propriété d'un domaine en créant un enregistrement DNS `_acme-challenge`. Utilisé ici via l'API Infomaniak.

SAN (Subject Alternative Name)
:   Extension d'un certificat TLS permettant de couvrir plusieurs noms de domaine avec un seul certificat. Cosmos regroupe tous ses domaines dans un seul certificat SAN.

Mode `authenticated`
:   Mode de déploiement Paperclip avec authentification obligatoire. Obligatoire pour une exposition sur Internet. À opposer à `local_trusted` (accès libre, usage local uniquement).

GHCR (GitHub Container Registry)
:   Registre d'images Docker hébergé par GitHub. Les images Paperclip sont publiées sur `ghcr.io/paperclipai/paperclip`.

`docker-entrypoint.s…`
:   Script de démarrage standard des conteneurs Docker — visible dans `docker ps`.

---

## Ressources

- [Paperclip AI — Dépôt GitHub](https://github.com/paperclipai/paperclip) — Code source et documentation
- [Cosmos Server — Dépôt GitHub](https://github.com/azukaar/Cosmos-Server) — Code source
- [Cosmos Server — Documentation officielle](https://cosmos-cloud.io/docs/index/) — Guide d'installation et configuration
- [GHCR — Image Paperclip](https://github.com/paperclipai/paperclip/pkgs/container/paperclip) — Images Docker disponibles
- [Let's Encrypt — Challenge DNS](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) — Explication du challenge DNS-01
