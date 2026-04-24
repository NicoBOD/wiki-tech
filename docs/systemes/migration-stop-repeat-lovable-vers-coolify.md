---
title: "Migration de mon application Stop Repeat de Lovable vers un Coolify self-hosted"
date: 2026-04-25
author: Nicolas BODAINE
tags:
  - coolify
  - supabase
  - self-hosting
  - docker
  - traefik
  - ci-cd
  - github-app
  - lovable
  - migration
  - react
  - vite
difficulty: avancé
os: Debian 13 (Azure VM)
status: publié
---

# Migration de mon application Stop Repeat de Lovable vers un Coolify self-hosted

!!! abstract "Résumé"
    J'ai migré mon application **Stop Repeat** (gestionnaire de tâches familiales React/Vite) hébergée chez **Lovable Cloud** avec une base **Supabase managée** vers une infrastructure entièrement self-hosted sur ma VM Azure (Coolify + Traefik + Supabase complet).
    Cette note retrace toute la procédure : refactor du code, déploiement de Supabase self-hosted (15 conteneurs), mise en place de la CI/CD via GitHub App, configuration des edge functions, du SMTP, des cron jobs et de Google OAuth.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Avancé |
| OS / Environnement | Debian 13, Coolify v4.0.0-beta.470, Traefik v3.6, Supabase self-hosted |
| Dernière mise à jour | 2026-04-25 |

## Contexte

Mon app **Stop Repeat** est un SPA React + Vite + TypeScript permettant à des parents de créer des tâches récurrentes pour leurs enfants, avec gamification (récompenses, pénalités, streaks, badges) et notifications push. Le code est public sur [TutoTech/family-flow](https://github.com/TutoTech/family-flow).

Initialement, le projet était hébergé sur **Lovable Cloud** :

- **Frontend** servi par Lovable
- **Base de données + Auth + Storage + 10 Edge Functions** sur un projet Supabase managé (`fzstjebbxbejypgwamqx.supabase.co`)
- **Authentification Google** via un wrapper propriétaire `@lovable.dev/cloud-auth-js`
- **Paiements Stripe** + **notifications push VAPID**

J'avais plusieurs raisons de vouloir m'auto-héberger :

- **Autonomie** vis-à-vis de Lovable et Supabase Cloud
- **Maîtrise** de mes données et de l'infrastructure
- **Coûts** (Supabase Cloud devient payant au-delà des limites du free tier)
- **CI/CD** : déclencher un redéploiement automatique à chaque push GitHub

Je disposais déjà d'un serveur **Coolify** (v4) sur une VM Azure Debian 13 avec **Traefik** comme reverse proxy. J'ai donc décidé d'y déployer toute la stack.

J'ai gardé en parallèle le déploiement Lovable comme **fallback de sécurité** pendant toute la durée de la migration, en travaillant sur une branche dédiée `coolify-deploy`.

## Prérequis

- Une VM avec **au moins 8 Go de RAM** (j'ai dû redimensionner la mienne en `Standard_B2as_v2` Azure car Supabase self-hosted ajoute environ 2 Go d'utilisation)
- **Coolify** déjà installé et fonctionnel avec **Traefik** comme reverse proxy
- Un domaine pointant vers le serveur (j'utilise `tutotech.org`) avec la possibilité de créer des sous-domaines
- Un fournisseur DNS supportant l'**API DNS challenge** pour Let's Encrypt (j'utilise Infomaniak)
- Une **clé SSH** pour pousser sur GitHub
- Le repo de l'app **clonable** localement
- Les secrets de l'app (VAPID, Stripe, OAuth Google, SMTP) à portée de main

## Architecture cible

```
                     INTERNET
                        │
                        ▼
              [Traefik (coolify-proxy)]
              ────────┬──────────┬──────────┬──────────────┐
                      │          │          │              │
                      ▼          ▼          ▼              ▼
          stop-repeat       supabase    studio.supabase    webhook
          .tutotech.org   .tutotech.org .tutotech.org  .tutotech.org
              │               │              │              │
              ▼               ▼              ▼              ▼
          [nginx-           [Kong       [Studio UI]     [Coolify
           unprivileged]    gateway]         │           webhook]
              │               │              │              │
          [SPA Vite]      ┌──┴───┐           │              │
                          ▼      ▼           │              │
                    [GoTrue] [PostgREST]     │              │
                    [Storage] [Realtime]     │              │
                    [Edge functions]         │              │
                          │                  │              │
                          ▼                  ▼              │
                       [PostgreSQL 15 + pg_cron + pg_net]   │
                                                             │
              GitHub push → coolify-deploy ─────────────────┘
                  ↓
              Auto-build + redeploy
```

## Procédure

J'ai découpé la migration en **7 phases** que j'ai exécutées dans l'ordre.

### Phase 1 : Préparation du code

Je devais d'abord adapter le code de l'app pour qu'il soit déployable hors de Lovable.

#### 1.1 Cloner le repo et créer une branche dédiée

J'ai configuré ma clé SSH et cloné le repo, puis créé une branche `coolify-deploy` pour que `main` reste exclusivement utilisé par Lovable comme fallback :

```bash
git clone git@github.com:TutoTech/family-flow.git
cd family-flow
git checkout -b coolify-deploy
```

#### 1.2 Remplacer Lovable Auth par Supabase OAuth natif

Le wrapper `@lovable.dev/cloud-auth-js` était utilisé uniquement dans `LoginForm.tsx` et `SignupForm.tsx` pour le bouton « Continuer avec Google ». C'était une fine couche d'OAuth relais qui pouvait être remplacée par l'API native de Supabase.

J'ai supprimé le wrapper Lovable :

```bash
rm -rf src/integrations/lovable/
```

Puis dans `src/components/auth/LoginForm.tsx` et `src/components/auth/SignupForm.tsx`, j'ai remplacé l'import et l'appel :

```typescript title="Avant (Lovable)"
import { lovable } from "@/integrations/lovable/index";
// ...
const { error } = await lovable.auth.signInWithOAuth("google", {
  redirect_uri: window.location.origin
});
```

```typescript title="Après (Supabase natif)"
import { supabase } from "@/integrations/supabase/client";
// ...
const { error } = await supabase.auth.signInWithOAuth({
  provider: "google",
  options: { redirectTo: window.location.origin + "/" },
});
```

J'ai également retiré la dépendance `@lovable.dev/cloud-auth-js` du `package.json`.

!!! warning "Attention au redirect_to"
    À mon premier essai, j'avais mis `redirectTo: window.location.origin + "/auth/callback"` mais cette route n'existait pas dans React Router et le user tombait sur une **404** après le login Google. J'ai dû corriger en pointant vers `/` (la landing page) — le client Supabase parse automatiquement le hash de l'URL au chargement de la page et établit la session.

#### 1.3 Créer un Dockerfile multi-stage

Le repo n'avait aucune containerisation. J'ai créé un `Dockerfile` multi-stage : étape **builder** avec Node 20 pour `npm run build`, puis étape **runtime** avec `nginx-unprivileged:1.27-alpine`.

```dockerfile title="Dockerfile"
# syntax=docker/dockerfile:1.7

# ---------- Build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# Build-time Supabase config (injected by Coolify as ARG)
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_PUBLISHABLE_KEY
ARG VITE_SUPABASE_PROJECT_ID
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_PUBLISHABLE_KEY=$VITE_SUPABASE_PUBLISHABLE_KEY
ENV VITE_SUPABASE_PROJECT_ID=$VITE_SUPABASE_PROJECT_ID

COPY . .
RUN npm run build

# ---------- Runtime stage ----------
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
```

J'ai accompagné ce Dockerfile d'un `nginx.conf` avec **fallback SPA** (essentiel pour React Router), **gzip**, **cache assets** et **headers de sécurité** :

```nginx title="nginx.conf"
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/javascript application/json image/svg+xml;

    location ~* \.(js|css|woff2?|png|jpg|svg|ico)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-store, no-cache, must-revalidate";
    }
}
```

J'ai testé le build localement avec `docker build` et `docker run` — image fonctionnelle, page Stop Repeat servie correctement.

#### 1.4 Commit et push

```bash
git add Dockerfile nginx.conf .dockerignore package.json src/components/auth/
git commit -m "Prépare le déploiement Coolify self-hosted"
git push -u origin coolify-deploy
```

### Phase 2 : Déployer Supabase self-hosted

C'est la phase la plus lourde — Supabase self-hosted comporte **15 conteneurs** : `db` (PostgreSQL 15), `auth` (GoTrue), `rest` (PostgREST), `realtime`, `storage`, `imgproxy`, `kong`, `studio`, `meta`, `functions` (Deno), `analytics` (Logflare), `vector`, `supavisor` (pooler), `db-config`, `deno-cache`.

#### 2.1 Récupérer le compose officiel

J'ai téléchargé les fichiers officiels du repo Supabase :

```bash
mkdir -p /opt/docker/supabase
cd /opt/docker/supabase

curl -fsSL https://raw.githubusercontent.com/supabase/supabase/master/docker/docker-compose.yml -o docker-compose.yml
curl -fsSL https://raw.githubusercontent.com/supabase/supabase/master/docker/.env.example -o .env.example

# Récupérer aussi le dossier volumes/ qui contient kong.yml, init SQL, etc.
git clone --depth 1 --filter=blob:none --sparse https://github.com/supabase/supabase.git /tmp/supabase-src
cd /tmp/supabase-src && git sparse-checkout set docker/volumes
cp -r docker/volumes /opt/docker/supabase/volumes
```

#### 2.2 Générer les secrets

Supabase fournit deux scripts de génération : `generate-keys.sh` (clés HS256 legacy) et `add-new-auth-keys.sh` (clés ES256 asymétriques).

```bash
cd /opt/docker/supabase
mkdir utils
curl -fsSL https://raw.githubusercontent.com/supabase/supabase/master/docker/utils/generate-keys.sh -o utils/generate-keys.sh
curl -fsSL https://raw.githubusercontent.com/supabase/supabase/master/docker/utils/add-new-auth-keys.sh -o utils/add-new-auth-keys.sh

# Génère JWT_SECRET, ANON_KEY, SERVICE_ROLE_KEY, POSTGRES_PASSWORD, etc.
sh utils/generate-keys.sh | tee /tmp/supabase-keys.txt

# Génère les nouvelles clés ES256 (nécessite Node + openssl)
docker run --rm -v "$(pwd):/work" -w /work node:20-alpine \
  sh -c "apk add --no-cache openssl && sh utils/add-new-auth-keys.sh --update-env"
```

Ensuite j'ai consolidé toutes les variables (URLs, DB, Auth, Storage, Functions, Kong, etc.) dans le fichier `.env`.

!!! tip "Variables URL importantes"
    J'ai bien renseigné :
    
    - `SUPABASE_PUBLIC_URL=https://supabase.tutotech.org`
    - `API_EXTERNAL_URL=https://supabase.tutotech.org`
    - `SITE_URL=https://stop-repeat.tutotech.org`
    - `ADDITIONAL_REDIRECT_URLS=https://stop-repeat.tutotech.org/**`

#### 2.3 Adapter le compose pour Traefik

Je n'ai pas modifié le `docker-compose.yml` officiel, j'ai créé un `docker-compose.override.yml` qui :

- Retire l'exposition des ports 8000/8443 de Kong sur l'hôte (Traefik intercepte)
- Ajoute les **labels Traefik** sur Kong pour `supabase.tutotech.org` (avec CORS)
- Ajoute les **labels Traefik** sur Studio pour `studio.supabase.tutotech.org` (avec **IPWhiteList VPN only**)
- Connecte Kong et Studio au réseau `traefik-supabase`

```yaml title="docker-compose.override.yml (extrait Kong)"
services:
  kong:
    ports: !reset []
    networks:
      - default
      - traefik-supabase
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=traefik-supabase"
      - "traefik.http.routers.supabase-api.rule=Host(`supabase.tutotech.org`)"
      - "traefik.http.routers.supabase-api.entrypoints=https"
      - "traefik.http.routers.supabase-api.tls.certresolver=letsencrypt"
      - "traefik.http.services.supabase-api.loadbalancer.server.port=8000"
      - "traefik.http.routers.supabase-api.middlewares=supabase-cors"
      - "traefik.http.middlewares.supabase-cors.headers.accesscontrolalloworiginlist=https://stop-repeat.tutotech.org"
      # ...

  studio:
    networks:
      - default
      - traefik-supabase
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.supabase-studio.rule=Host(`studio.supabase.tutotech.org`)"
      - "traefik.http.routers.supabase-studio.middlewares=studio-vpn-only"
      - "traefik.http.middlewares.studio-vpn-only.ipwhitelist.sourcerange=10.223.172.0/24,127.0.0.1/32"
      # ...

networks:
  traefik-supabase:
    external: true
    name: traefik-supabase
```

J'ai créé le réseau externe puis connecté `coolify-proxy` (Traefik) à ce réseau :

```bash
docker network create traefik-supabase
docker network connect traefik-supabase coolify-proxy
```

J'ai aussi ajouté `traefik-supabase` (et plus tard `traefik-stop-repeat`) au compose **persistant** de Coolify-proxy (`/data/coolify/proxy/docker-compose.yml`) pour que les réseaux soient maintenus aux restarts de Traefik.

#### 2.4 Créer les enregistrements DNS

J'ai créé chez Infomaniak :

| Sous-domaine | Type | Cible | Usage |
|---|---|---|---|
| `supabase.tutotech.org` | A | IP publique du serveur | API Supabase (Kong) |
| `studio.supabase.tutotech.org` | A | IP publique du serveur | Studio (filtré VPN) |
| `stop-repeat.tutotech.org` | A | IP publique du serveur | Frontend |
| `webhook.tutotech.org` | A | IP publique du serveur | Webhooks GitHub |

#### 2.5 Démarrer la stack

```bash
cd /opt/docker/supabase
docker compose pull
docker compose up -d
```

Au bout de **30 secondes**, les 15 services étaient `healthy`. La RAM est passée de 2.6 Go à 4.4 Go utilisés (sur 7.7 Go disponibles).

#### 2.6 Appliquer les 67 migrations SQL

Mon repo `family-flow` contenait **67 migrations SQL** dans `supabase/migrations/`. Je les ai rejouées en ordre chronologique :

```bash
cd /home/nicolas-bodaine/git/family-flow/supabase/migrations
POSTGRES_PW=$(grep "^POSTGRES_PASSWORD=" /opt/docker/supabase/.env | cut -d= -f2)

for f in $(ls *.sql | sort); do
    docker exec -i supabase-db env PGPASSWORD="$POSTGRES_PW" \
      psql -U postgres -d postgres < "$f"
done
```

J'ai obtenu **66 succès et 1 erreur** sur une migration qui tentait d'insérer des données liées à un user (FK vers `auth.users`). Ce n'était pas bloquant — la DB est vierge à ce stade. **19 tables publiques** ont été créées (`families`, `profiles`, `task_templates`, `task_instances`, `rewards`, `child_stats`, etc.).

### Phase 3 : Déploiement du frontend avec CI/CD GitHub App

#### 3.1 Créer l'application Coolify via API

J'ai utilisé l'API Coolify pour créer l'application (j'avais déjà créé une **GitHub App** « coolify-tutotech-org-github-app-1 » sous mon organisation TutoTech) :

```bash
COOLIFY_TOKEN="..."
SERVER_UUID="..."
PROJECT_TUTOTECH="..."
GITHUB_APP_UUID="..."  # uuid de coolify-tutotech-org-github-app-1

curl -X POST "http://localhost:8000/api/v1/applications/private-github-app" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_uuid\": \"$PROJECT_TUTOTECH\",
    \"server_uuid\": \"$SERVER_UUID\",
    \"github_app_uuid\": \"$GITHUB_APP_UUID\",
    \"environment_name\": \"production\",
    \"git_repository\": \"TutoTech/family-flow\",
    \"git_branch\": \"coolify-deploy\",
    \"build_pack\": \"dockerfile\",
    \"ports_exposes\": \"8080\",
    \"name\": \"stop-repeat\",
    \"domains\": \"https://stop-repeat.tutotech.org\",
    \"instant_deploy\": false
  }"
```

#### 3.2 Configurer les variables d'environnement build-time

Les variables `VITE_*` doivent être disponibles **au build** (pas au runtime) pour que Vite les inline dans le bundle JS. Je les ai ajoutées via l'API :

```bash
APP_UUID="..."
ANON_KEY=$(grep "^ANON_KEY=" /opt/docker/supabase/.env | cut -d= -f2)

curl -X POST "http://localhost:8000/api/v1/applications/$APP_UUID/envs" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key": "VITE_SUPABASE_URL", "value": "https://supabase.tutotech.org"}'

curl -X POST ".../envs" -d "{\"key\": \"VITE_SUPABASE_PUBLISHABLE_KEY\", \"value\": \"$ANON_KEY\"}"
curl -X POST ".../envs" -d '{"key": "VITE_SUPABASE_PROJECT_ID", "value": "stop-repeat-selfhosted"}'
```

#### 3.3 Premier déploiement

J'ai déclenché un déploiement manuel via l'API et il a réussi en **~17 secondes** (build Docker + nginx).

```bash
curl "http://localhost:8000/api/v1/deploy?uuid=$APP_UUID&force=false" \
  -H "Authorization: Bearer $COOLIFY_TOKEN"
```

L'app était accessible sur `https://stop-repeat.tutotech.org` avec un certificat **Let's Encrypt** valide (DNS challenge Infomaniak via la config Traefik existante).

#### 3.4 Activer le webhook CI/CD

C'est ici que j'ai rencontré un piège : mon domaine `coolify.tutotech.org` pointe vers l'IP **VPN privée** (10.223.172.1) pour des raisons de sécurité. GitHub ne pouvait donc **pas atteindre l'endpoint webhook** depuis Internet.

!!! tip "Solution : un domaine public dédié pour les webhooks"
    J'ai créé un sous-domaine `webhook.tutotech.org` pointant vers l'**IP publique**, et configuré une route Traefik dédiée qui n'expose **que** le path `/webhooks/` de Coolify.

J'ai créé un fichier de config dynamique Traefik :

```yaml title="/data/coolify/proxy/dynamic/coolify-webhook.yml"
http:
  routers:
    coolify-webhook:
      rule: "Host(`webhook.tutotech.org`) && PathPrefix(`/webhooks/`)"
      entryPoints:
        - https
      tls:
        certResolver: letsencrypt
      service: coolify-dashboard

  services:
    coolify-dashboard:
      loadBalancer:
        servers:
          - url: "http://coolify:8080"
```

Puis dans la **GitHub App** (paramètres de l'organisation TutoTech), j'ai mis à jour l'URL du webhook vers :

```
https://webhook.tutotech.org/webhooks/source/github/events
```

!!! warning "Ne pas mettre `/manage` à la fin"
    Mon premier essai avec `/webhooks/source/github/events/manage` ne fonctionnait pas (cette route n'existe pas dans Coolify). La bonne URL est juste `/webhooks/source/github/events`.

À mon push suivant, le webhook a déclenché le déploiement en **~5 secondes**. La CI/CD était opérationnelle.

### Phase 4 : Edge Functions et secrets

#### 4.1 Copier les 10 fonctions

Le service `supabase-edge-functions` du compose monte le dossier `/opt/docker/supabase/volumes/functions/` vers `/home/deno/functions/`. J'ai copié mes 10 functions :

```bash
for fn in /home/nicolas-bodaine/git/family-flow/supabase/functions/*/; do
    cp -r "$fn" /opt/docker/supabase/volumes/functions/
done
docker restart supabase-edge-functions
```

Les functions deviennent immédiatement accessibles sur :

```
https://supabase.tutotech.org/functions/v1/<nom-fonction>
```

#### 4.2 Injecter les secrets via l'override

Les fonctions ont besoin de secrets pour fonctionner (Stripe, VAPID). Je les ai ajoutés au `.env` puis injectés dans le service `functions` via l'override :

```yaml title="docker-compose.override.yml (extrait functions)"
services:
  functions:
    environment:
      VAPID_PUBLIC_KEY: ${VAPID_PUBLIC_KEY}
      VAPID_PRIVATE_KEY: ${VAPID_PRIVATE_KEY}
      VAPID_EMAIL: ${VAPID_EMAIL}
      STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY}
      STRIPE_WEBHOOK_SECRET: ${STRIPE_WEBHOOK_SECRET}
```

!!! tip "Réutiliser les VAPID de Lovable"
    J'ai récupéré les **mêmes** VAPID keys depuis le dashboard Supabase Lovable plutôt que d'en générer de nouvelles. Ainsi, les enfants déjà inscrits aux notifications push n'auront **pas** à re-autoriser au moment de la migration des données.

#### 4.3 Configurer le SMTP pour les emails de confirmation

Au premier signup test, j'ai obtenu une erreur **« Error sending confirmation email »**. La cause : le `.env` pointait vers `supabase-mail:2500` (le service mock du compose), inexistant.

J'ai créé un **mot de passe d'application** sur Infomaniak pour le compte `admin@tutotech.org`, puis configuré :

```ini title=".env"
SMTP_HOST=mail.infomaniak.com
SMTP_PORT=465
SMTP_USER=admin@tutotech.org
SMTP_PASS=<mot-de-passe-application>
SMTP_SENDER_NAME=Stop Repeat
SMTP_ADMIN_EMAIL=admin@tutotech.org
```

Après `docker compose up -d auth`, le test de signup envoyait bien l'email de confirmation.

### Phase 5 : pg_cron jobs

L'app a besoin de **3 tâches planifiées** :

- **`daily-task-reset`** : régénère les instances de tâches du jour pour toutes les familles (5h UTC)
- **`task-reminders`** : envoie les rappels push (toutes les 15 min)
- **`cleanup-evidence-photos`** : supprime les photos preuve expirées (toutes les heures)

Les extensions `pg_cron` et `pg_net` étaient déjà installées dans l'image `supabase/postgres`. J'ai créé les jobs :

```sql title="Création des cron jobs"
-- Job 1 : daily-task-reset (5h UTC)
SELECT cron.schedule(
  'daily-task-reset',
  '0 5 * * *',
  $$
  SELECT net.http_post(
    url := 'https://supabase.tutotech.org/functions/v1/daily-task-reset',
    headers := '{"Content-Type": "application/json", "Authorization": "Bearer <ANON_KEY>"}'::jsonb,
    body := '{}'::jsonb
  );
  $$
);

-- Job 2 : task-reminders (toutes les 15 min)
SELECT cron.schedule(
  'task-reminders',
  '*/15 * * * *',
  $$ SELECT net.http_post(url := 'https://supabase.tutotech.org/functions/v1/task-reminders', ...); $$
);

-- Job 3 : cleanup-evidence-photos (toutes les heures, fonction SQL native)
SELECT cron.schedule(
  'cleanup-evidence-photos',
  '0 * * * *',
  $$ SELECT public.cleanup_expired_evidence_photos(); $$
);
```

J'ai vérifié leur bon fonctionnement en déclenchant un appel manuel via `pg_net` :

```sql
SELECT net.http_post(url := 'https://supabase.tutotech.org/functions/v1/task-reminders', ...);
SELECT id, status_code, content::text FROM net._http_response ORDER BY id DESC LIMIT 1;
-- Retour : status_code=200, content={"reminders_sent":0}  ✓
```

### Phase 6 : Google OAuth provider

Pour activer le bouton « Continuer avec Google », j'ai créé un **OAuth 2.0 Client ID** sur Google Cloud Console :

1. **OAuth consent screen** → External, app name « Stop Repeat », support email `admin@tutotech.org`
2. **Credentials** → Create OAuth client ID → Web application
3. **Authorized JavaScript origins** : `https://stop-repeat.tutotech.org`
4. **Authorized redirect URIs** : `https://supabase.tutotech.org/auth/v1/callback`

J'ai injecté le `Client ID` et `Client Secret` dans `.env` puis dans le service `auth` via l'override :

```yaml title="docker-compose.override.yml (extrait auth)"
services:
  auth:
    environment:
      GOTRUE_EXTERNAL_GOOGLE_ENABLED: ${GOOGLE_ENABLED}
      GOTRUE_EXTERNAL_GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
      GOTRUE_EXTERNAL_GOOGLE_SECRET: ${GOOGLE_SECRET}
      GOTRUE_EXTERNAL_GOOGLE_REDIRECT_URI: ${API_EXTERNAL_URL}/auth/v1/callback
```

Après `docker compose up -d auth`, GoTrue exposait `"google": true` dans son endpoint `/auth/v1/settings`, et un `GET /auth/v1/authorize?provider=google` retournait bien un **302** vers `accounts.google.com`.

### Phase 7 : Tests fonctionnels

J'ai validé le bout-en-bout :

- **Signup parent** avec email/mot de passe → email de confirmation reçu sur `admin@tutotech.org` → confirmation OK
- **Création d'un enfant** via la edge function `create-child-account` → OK
- **OAuth Google** : après correction du `redirectTo` (de `/auth/callback` vers `/`), le compte Google est correctement créé dans `auth.users` avec son nom (récupéré depuis Google) et l'utilisateur est redirigé vers la landing page avec sa session active
- **CI/CD GitHub App** : un push sur `coolify-deploy` déclenche un build Coolify en moins de 5 secondes, et le déploiement aboutit en ~17 secondes

## Vérification

Quelques commandes utiles pour vérifier que tout fonctionne :

```bash
# Tous les conteneurs Supabase healthy
docker ps --filter "name=supabase" --format "{{.Names}}\t{{.Status}}"

# Test API REST (avec apikey)
ANON=$(grep "^ANON_KEY=" /opt/docker/supabase/.env | cut -d= -f2)
curl -s "https://supabase.tutotech.org/rest/v1/" -H "apikey: $ANON" | jq '.swagger'

# Test Auth settings
curl -s "https://supabase.tutotech.org/auth/v1/settings" -H "apikey: $ANON" | jq '.external'

# Test edge function
curl -s "https://supabase.tutotech.org/functions/v1/push-vapid-key" -H "apikey: $ANON"

# Test Google OAuth (doit renvoyer 302 vers accounts.google.com)
curl -sI "https://supabase.tutotech.org/auth/v1/authorize?provider=google&redirect_to=https://stop-repeat.tutotech.org/" -H "apikey: $ANON"

# Lister les cron jobs
docker exec supabase-db psql -U postgres -d postgres -c "SELECT jobid, jobname, schedule FROM cron.job;"

# Tester la CI/CD
git commit --allow-empty -m "test ci/cd" && git push origin coolify-deploy
# → Vérifier dans l'UI Coolify qu'un build se lance
```

!!! success "Résultat attendu"
    Tous les endpoints répondent avec un code HTTP 2xx (ou 302 pour OAuth, ou 401 si auth requise), les certificats sont émis par Let's Encrypt, et un push GitHub déclenche bien un nouveau déploiement automatique.

## Pièges rencontrés et solutions

| Piège | Symptôme | Solution |
|---|---|---|
| Coolify domain en VPN-only | GitHub ne peut pas envoyer de webhook | Créer un sous-domaine public `webhook.*` exposant uniquement `/webhooks/*` |
| Mauvaise URL webhook | Le push ne déclenche rien | Utiliser `/webhooks/source/github/events` (sans `/manage`) |
| `acme.json` permissions | Cert auto-signé Traefik au lieu de Let's Encrypt | `chmod 600 /data/coolify/proxy/acme.json` (Coolify l'écrase parfois en `770`) |
| Route `/auth/callback` inexistante | 404 après login Google | Pointer `redirectTo` vers `/` (Supabase parse le hash automatiquement) |
| SMTP `supabase-mail` introuvable | « Error sending confirmation email » | Configurer un vrai SMTP (j'utilise Infomaniak avec mot de passe d'application) |
| RAM serrée | OOM kill possible avec 4 Go | Redimensionner la VM Azure à `B2as_v2` (8 Go) |
| `is_build_time` non accepté par l'API | Erreur de validation à l'ajout d'env | Ne pas l'envoyer — Coolify détecte automatiquement les `VITE_*` comme build-time |

## Ce qui reste à faire

!!! note "Prochaine étape : migration des données de production"
    Cette note couvre le **déploiement de l'infrastructure self-hosted**. Il me reste à migrer les **données de production** depuis Lovable :
    
    - **`auth.users`** (avec les hashes bcrypt préservés pour que les users n'aient pas à réinitialiser leur mot de passe)
    - Toutes les données métier (familles, tâches, récompenses, statistiques, etc.)
    - Le **bucket Storage `task-evidence`** (photos de preuve)
    - Les **identités OAuth Google** liées aux comptes existants
    
    Cette étape sera documentée dans un complément à cette note.

## Aide-mémoire — Sous-domaines

| Sous-domaine | Usage | Accès |
|---|---|---|
| `stop-repeat.tutotech.org` | Frontend SPA | Public |
| `supabase.tutotech.org` | API Supabase (Kong gateway : REST, Auth, Storage, Realtime, Functions) | Public |
| `studio.supabase.tutotech.org` | Dashboard Studio (admin DB) | VPN uniquement |
| `coolify.tutotech.org` | UI Coolify | VPN uniquement |
| `webhook.tutotech.org` | Endpoint webhooks GitHub (uniquement `/webhooks/*`) | Public |

## Aide-mémoire — Commandes utiles

| Commande / Action | Description |
|---|---|
| `docker compose up -d` (depuis `/opt/docker/supabase`) | Démarrer la stack Supabase |
| `docker compose logs -f auth` | Suivre les logs de GoTrue |
| `docker exec supabase-db psql -U postgres -d postgres` | Console SQL avec super-user |
| `SELECT * FROM cron.job;` | Lister les jobs planifiés |
| `SELECT * FROM net._http_response ORDER BY id DESC LIMIT 5;` | Voir les dernières réponses pg_net |
| `git push origin coolify-deploy` | Déclencher un redéploiement automatique |
| `curl /api/v1/deploy?uuid=...` (API Coolify) | Forcer un redéploiement manuel |

## Ressources

- [Supabase Self-Hosting Docker](https://supabase.com/docs/guides/self-hosting/docker) — Documentation officielle
- [Coolify Documentation](https://coolify.io/docs) — Documentation officielle
- [Traefik v3 — Routing](https://doc.traefik.io/traefik/routing/overview/) — Configuration des routers, services, middlewares
- [GoTrue / Auth API](https://supabase.com/docs/reference/self-hosting-auth/introduction) — API d'authentification
- [pg_cron](https://github.com/citusdata/pg_cron) — Planification de jobs PostgreSQL
- [Let's Encrypt DNS Challenge](https://doc.traefik.io/traefik/https/acme/#dnschallenge) — Émission de certificats wildcard via DNS
