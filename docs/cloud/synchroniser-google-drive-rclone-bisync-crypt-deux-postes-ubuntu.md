---
title: "Synchroniser Google Drive sur deux postes Ubuntu avec rclone bisync et chiffrement Crypt"
date: 2026-08-08
author: Nicolas BODAINE
tags:
  - rclone
  - google-drive
  - chiffrement
  - bisync
  - systemd
  - sauvegarde
  - cloud
difficulty: avancé
os: Ubuntu 24.04
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Synchroniser Google Drive sur deux postes Ubuntu avec rclone bisync et chiffrement Crypt

!!! abstract "Résumé"
    Mise en place complète d'une synchronisation **bidirectionnelle** entre deux postes Ubuntu et des **Drive partagés Google Workspace**, avec une zone **chiffrée côté client** (rclone Crypt) et une zone en clair. Couvre la création d'un **Client ID OAuth dédié**, le chiffrement du fichier de configuration adossé au **trousseau GNOME**, les **services systemd** d'automatisation, et surtout les **pièges rencontrés en conditions réelles** — dont plusieurs ne se révèlent qu'au test et peuvent coûter des données.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Avancé |
| OS / Environnement | Ubuntu 24.04 LTS, rclone 1.75.0 |
| Dernière mise à jour | 2026-08-09 |

!!! warning "Avertissement préalable"
    `rclone bisync` **supprime et écrase des fichiers des deux côtés**. Une configuration bancale peut détruire des données. Chaque garde-fou décrit ici a une raison d'être : ne les retirez pas pour « simplifier ». Testez toujours sur un jeu de données jetable avant de viser vos vraies données.

## Contexte

Le besoin : accéder aux mêmes fichiers depuis un poste fixe et un portable, avec un **accès hors ligne réel** sur les deux, tout en stockant sur des Drive partagés Google Workspace. Une partie des données est sensible et ne doit **jamais** être lisible par Google ; le reste doit rester consultable depuis l'interface web Drive et l'application mobile.

Trois décisions structurent tout le reste :

- **`bisync` plutôt que `mount`** : un montage réseau ne donne pas d'accès hors ligne. bisync maintient un miroir local complet, synchronisé dans les deux sens. Un montage reste utile **en complément**, pour consulter à la demande ce qui n'est pas dans le miroir.
- **Deux Drive partagés distincts**, un chiffré et un clair, plutôt que deux dossiers dans le même. Les quotas d'éléments et les droits de partage sont ainsi indépendants, et on ne dépose pas un fichier en clair dans la zone chiffrée par erreur.
- **Un Client ID OAuth personnel**. Sans lui, on partage le quota d'API public de rclone avec le monde entier et on récolte des erreurs `403 rate limit`.

## Prérequis

- Deux postes Ubuntu 24.04 avec session **GNOME** (le trousseau est utilisé pour le déverrouillage automatique).
- Un compte **Google Workspace administrateur**, capable de créer des Drive partagés et un projet Google Cloud dans l'organisation.
- Un espace disque local suffisant pour le miroir : bisync stocke une **copie complète en clair** sur chaque machine.
- Un gestionnaire de mots de passe pour conserver les clés Crypt (KeePassXC, Bitwarden…).
- Notions de `systemd --user`, de `git`, et à l'aise en ligne de commande.

!!! danger "Le point de non-retour"
    Le mot de passe **et** le sel (`password2`) du remote Crypt sont les **seules** choses qui permettent de relire vos données. Aucune sauvegarde du fichier de configuration ne les remplace si vous les perdez. Notez-les dans votre gestionnaire de mots de passe **au moment où l'assistant les affiche** : il ne les remontrera pas.

## Architecture retenue

| Élément | Choix | Pourquoi |
|---|---|---|
| Mode de synchro | `bisync` sur les deux postes | Seul mode offrant un accès hors ligne modifiable |
| Point de rencontre | Google Drive | Les deux postes ne se parlent pas directement : Drive est le pivot |
| Zone chiffrée | Remote `crypt` sur un **sous-dossier** | Voir le piège n°1 |
| Noms de fichiers | `filename_encryption = standard` | Masque aussi l'arborescence, au prix de la lisibilité côté web |
| Configuration | Chiffrée + trousseau GNOME | Les clés Crypt ne traînent pas en clair |
| Automatisation | `systemd --user` + timer | Le trousseau impose une session utilisateur, donc pas de service *system* |
| Conflits | Le plus récent gagne, perdant conservé | Aucune perte silencieuse |

```
   PC FIXE                      GOOGLE DRIVE                    PC PORTABLE
┌──────────────┐          ┌────────────────────┐          ┌──────────────┐
│ Miroir/      │          │ DRIVE-CHIFFRE      │          │ Miroir/      │
│  Chiffre/  ──┼─ bisync ─┤  Rclone/ (opaque)  ├─ bisync ─┼── Chiffre/   │
│  Clair/    ──┼─ bisync ─┤ DRIVE-CLAIR        ├─ bisync ─┼── Clair/     │
└──────────────┘          │  Rclone/ (lisible) │          └──────────────┘
   timer 15 min           └────────────────────┘             timer 15 min
```

!!! note "Convention de nommage dans cet article"
    Les identifiants, chemins et mots de passe ci-dessous sont **fictifs**. Remplacez-les par les vôtres :
    `0AXXXXXXXXXXXXXXXXX` et `0AYYYYYYYYYYYYYYYYY` (ID de Drive partagés), `/mnt/donnees` (disque du miroir), `/mnt/nvme` (disque du cache), `192.168.1.42` (IP du portable).

## Procédure

### Étape 1 : installer rclone en version récente

La version des dépôts Ubuntu 24.04 est **1.60.1**, datée de 2022. Les garde-fous essentiels de bisync (`--resilient`, `--recover`, `--conflict-resolve`, `--max-lock`) n'apparaissent qu'à partir de la **1.66**. Cette mise à niveau n'est pas un confort, c'est un prérequis.

!!! tip "Il n'existe pas de dépôt apt officiel rclone"
    Contrairement à une idée répandue, le projet ne publie pas de dépôt apt. La méthode propre est le paquet `.deb` officiel, qui reste géré par dpkg et peut être figé.

```bash
cd /tmp && curl -fsSL -O https://downloads.rclone.org/v1.75.0/rclone-v1.75.0-linux-amd64.deb && curl -fsSL -O https://downloads.rclone.org/v1.75.0/SHA256SUMS
```

Vérifiez l'empreinte **et** la signature avant d'installer, dans un trousseau GPG jetable pour ne pas polluer le vôtre :

```bash
cd /tmp && sha256sum -c --ignore-missing SHA256SUMS 2>/dev/null | grep rclone && export GNUPGHOME=$(mktemp -d) && curl -fsSL https://rclone.org/KEYS | gpg --quiet --import && gpg --verify SHA256SUMS
```

!!! success "Résultat attendu"
    `rclone-v1.75.0-linux-amd64.deb: Réussi` puis `Bonne signature de « Nick Craig-Wood »`. L'avertissement « cette clef n'est pas certifiée » est normal : il signale seulement que la clé n'est pas dans votre réseau de confiance, pas que la signature est invalide. L'empreinte de la clé de release est `FBF7 37EC E9F8 AB18 604B D2AC 9393 5E02 FF3B 54FA`.

```bash
sudo apt install -y /tmp/rclone-v1.75.0-linux-amd64.deb && sudo apt-mark hold rclone
```

Le `hold` empêche `apt upgrade` de vous ramener en 1.60. Pour les mises à jour ultérieures : `rclone selfupdate --package deb`.

### Étape 2 : créer un Client ID OAuth dédié

Dans la [console Google Cloud](https://console.cloud.google.com/) :

1. **Créer le projet** — le champ *Organisation* doit afficher votre domaine Workspace, pas « Aucune organisation ». C'est ce qui conditionne l'étape 3.
2. **Activer l'API Drive** — bibliothèque d'API, rechercher *Google Drive API*, activer.
3. **Écran de consentement** — section *Google Auth Platform* (ex-« écran de consentement OAuth »). Choisir **Interne**.
4. **Identifiants** — créer un client OAuth de type **Application de bureau** (surtout pas « Application Web »).
5. **Créer les deux Drive partagés** depuis `drive.google.com`. L'identifiant est la portion d'URL après `/folders/`, il commence par `0A`.

!!! warning "Interne ou Externe : la différence qui casse tout"
    En mode **Externe / Testing**, le jeton de rafraîchissement OAuth **expire au bout de 7 jours**. Toute automatisation systemd s'arrête donc chaque semaine en réclamant une réautorisation manuelle. En **Interne**, pas d'expiration, pas de vérification Google, et l'application reste cantonnée à votre domaine. C'est le seul choix viable pour du service automatisé.

### Étape 3 : créer les remotes

Utilisez l'assistant **interactif**. En passant par `rclone config create`, votre *client secret* et vos clés Crypt atterriraient dans l'historique du shell.

```bash
rclone config
```

**Remote 1 — `gd-chiffre`** : `n` → nom `gd-chiffre` → stockage `drive` → *client\_id* et *client\_secret* → *scope* `1` (accès complet) → *service\_account\_file* vide → *Edit advanced config* `n` → *Use web browser* `y` → **_Configure this as a Shared Drive (Team Drive)_ : `y`**, puis choisir le Drive chiffré dans la liste proposée.

**Remote 2 — `gcrypt`** : `n` → nom `gcrypt` → stockage `crypt` → **remote : `gd-chiffre:Rclone`** → `filename_encryption` : `1` (standard) → `directory_name_encryption` : `1` (true) → mot de passe : `g` (générer) → **256 bits** → sel (`password2`) : `g`, 256 bits également.

**Remote 3 — `gd-clair`** : identique au remote 1, en sélectionnant l'autre Drive partagé.

!!! question "Pourquoi 256 bits et pas 1024 ?"
    L'assistant propose jusqu'à 1024 bits, mais rclone ne se sert **jamais** de ce mot de passe comme clé. Il le passe, avec le sel, dans une fonction de dérivation (scrypt) qui produit une quantité **fixe** de matériel de clé : 256 bits pour les données, 256 pour les noms de fichiers. Au-delà, l'entropie supplémentaire n'a nulle part où aller. Mesures faites sur 200 Mo chiffrés : 371 ms en 128 bits contre 370 ms en 1024 — aucun écart. Le seul effet réel de 1024 bits est un mot de passe de **171 caractères** au lieu de 43, à retranscrire sans erreur le jour où vous reconstruirez la configuration à la main. 256 bits est le point d'équilibre.

### Étape 4 : chiffrer la configuration et l'adosser au trousseau

```bash
rclone config encryption set
```

Puis, **avec exactement le même mot de passe** :

```bash
secret-tool store --label='rclone config' service rclone key config
```

Toutes les invocations utiliseront ensuite `--password-command "secret-tool lookup service rclone key config"`.

!!! warning "Le paquet libsecret-tools n'est pas installé par défaut"
    Le démon `gnome-keyring-daemon` (le coffre) est présent sur Ubuntu Desktop, mais `secret-tool` (le client en ligne de commande qui l'interroge) ne l'est pas. Sans lui, `--password-command` n'a rien à appeler : `sudo apt install -y libsecret-tools`.

!!! danger "Supprimez toute sauvegarde en clair"
    Si vous aviez copié `rclone.conf` avant de le chiffrer, cette copie contient vos clés en clair et annule tout le bénéfice de l'opération. `shred -u ~/.config/rclone/rclone.conf.sauvegarde`.

### Étape 5 : le fichier de filtres

```text title="~/.config/rclone/filters.txt"
# Filtres rclone partagés entre les deux postes.
# Syntaxe : "- motif" = exclure. Les motifs {{...}} sont des expressions régulières.

# --- Noms trop longs pour Crypt (limite ~143 caractères par composant) ---
- {{[^/]{144,}$}}
- {{[^/]{144,}}}/**

# --- Garde-fou anti-collision avec d'autres agents de synchronisation ---
- .SynologyWorkingDirectory/**
- @eaDir/**
- .dropbox
- .dropbox.cache/**
- desktop.ini
- Thumbs.db
- .DS_Store

# --- Coffres chiffrés gérés par un autre outil (Cryptomator, VeraCrypt…) ---
- masterkey.cryptomator
- masterkey.cryptomator.bkup
- vault.cryptomator

# --- Caches et environnements reconstructibles ---
- .cache/**
- node_modules/**
- .venv/**
- venv/**
- __pycache__/**
- .mypy_cache/**
- .pytest_cache/**
- target/debug/**
- target/release/**

# --- Fichiers temporaires, verrous, corbeilles ---
- .~lock.*
- ~$*
- .goutputstream*
- *.partial
- *.crdownload
- *.tmp
- *.swp
- .Trash-*/**
- lost+found/**
- .fuse_hidden*
```

!!! tip "Les filtres rclone ignorent la longueur des noms"
    Il n'existe pas d'option « exclure au-delà de N caractères ». Il faut passer par la syntaxe d'expression régulière `{{...}}`. Attention au piège : le motif intuitif `{{^.{144,}$}}` s'applique au **chemin complet** et écarte donc à tort un fichier au nom court situé dans une arborescence profonde. Les deux motifs ci-dessus ont été validés par test : ils portent bien sur le **dernier composant** du chemin.

### Étape 6 : les paramètres propres à chaque machine

Un seul fichier diffère entre les deux postes. Scripts et unités systemd sont rigoureusement identiques.

```bash title="~/.config/rclone/machine.env — poste fixe"
RCLONE_MIRROR_ROOT=/mnt/donnees/GoogleDrive
RCLONE_CACHE_DIR=/mnt/nvme/rclone-cache
RCLONE_VFS_CACHE_MAX_SIZE=60G
RCLONE_TRANSFERS=8
RCLONE_CHECKERS=16
RCLONE_BACKUP_ROOT=/mnt/donnees/GoogleDrive-corbeille
```

```bash title="~/.config/rclone/machine.env — portable"
RCLONE_MIRROR_ROOT=/home/user/GoogleDrive
RCLONE_CACHE_DIR=/home/user/.cache/rclone/vfs
RCLONE_VFS_CACHE_MAX_SIZE=30G
RCLONE_TRANSFERS=4
RCLONE_CHECKERS=8
RCLONE_BACKUP_ROOT=/home/user/GoogleDrive-corbeille
# Garde-fous propres à une machine mobile
RCLONE_SKIP_ON_METERED=1
RCLONE_BATTERY_MIN=30
```

!!! danger "N'utilisez jamais un support amovible pour le miroir"
    Carte SD, clé USB, disque externe : leur retrait en cours de passe fait interpréter l'absence des fichiers comme des **suppressions à propager sur Drive**. Le garde-fou `--max-delete` bloquerait, mais mieux vaut ne pas créer la situation.

### Étape 7 : l'audit pre-flight

Ce script tourne avant chaque passe. Il recense ce que les filtres écarteront **silencieusement** et détecte les recouvrements avec d'autres outils de synchronisation.

```bash title="~/.local/bin/rclone-bisync-preflight.sh" linenums="1"
#!/usr/bin/env bash
# Audit pre-flight du miroir rclone bisync.
# Usage : rclone-bisync-preflight.sh <racine-du-miroir>
# Sortie : 0 = rien à signaler, 1 = anomalie bloquante, 2 = avertissements
set -uo pipefail

MIRROR="${1:?usage: $0 <racine-du-miroir>}"
LOGDIR="${XDG_DATA_HOME:-$HOME/.local/share}/rclone/logs"
REPORT="$LOGDIR/preflight-$(basename "$MIRROR").txt"
MAXLEN=143   # limite Crypt avec filename_encryption = standard

mkdir -p "$LOGDIR"
rc=0
{ echo "Audit pre-flight — $MIRROR"; echo "Démarré : $(date -Is)"; echo; } > "$REPORT"

if [[ ! -d "$MIRROR" ]]; then
  echo "BLOQUANT : le miroir $MIRROR n'existe pas." | tee -a "$REPORT"; exit 1
fi

# Témoin exigé par --check-access
if [[ ! -e "$MIRROR/RCLONE_TEST" ]]; then
  echo "BLOQUANT : $MIRROR/RCLONE_TEST absent." | tee -a "$REPORT"; rc=1
fi

# Recouvrement avec un autre agent de synchronisation
for concurrent in SynologyDrive OneDrive Dropbox Nextcloud; do
  if [[ "$MIRROR" == *"/$concurrent/"* || "$MIRROR" == *"/$concurrent" ]]; then
    echo "BLOQUANT : miroir situé dans $concurrent — collision." | tee -a "$REPORT"; rc=1
  fi
  if find "$MIRROR" -maxdepth 3 -type d -name "$concurrent" -print -quit 2>/dev/null | grep -q .; then
    echo "BLOQUANT : dossier $concurrent DANS le miroir — collision." | tee -a "$REPORT"; rc=1
  fi
done

# Noms écartés par les filtres
long_files=$(find "$MIRROR" -type f -printf '%f\t%p\n' 2>/dev/null | awk -F'\t' -v m="$MAXLEN" 'length($1)>m')
long_dirs=$(find "$MIRROR" -type d -printf '%f\t%p\n' 2>/dev/null | awk -F'\t' -v m="$MAXLEN" 'length($1)>m')
nf=$(printf '%s' "$long_files" | grep -c . || true)
nd=$(printf '%s' "$long_dirs"  | grep -c . || true)

if (( nf > 0 || nd > 0 )); then
  {
    echo "AVERTISSEMENT : noms de plus de $MAXLEN caractères — EXCLUS de la synchronisation."
    echo "  fichiers : $nf / dossiers : $nd (contenu entier écarté)"; echo
    [[ -n "$long_files" ]] && { echo "--- fichiers ---"; printf '%s\n' "$long_files" | cut -f2; echo; }
    [[ -n "$long_dirs"  ]] && { echo "--- dossiers ---"; printf '%s\n' "$long_dirs"  | cut -f2; echo; }
  } >> "$REPORT"
  echo "AVERTISSEMENT : $nf fichier(s) et $nd dossier(s) exclus — détail dans $REPORT"
  (( rc == 0 )) && rc=2
fi

count=$(find "$MIRROR" -type f 2>/dev/null | wc -l)
{
  echo "--- volumétrie ---"
  echo "fichiers : $count"
  echo "taille   : $(du -sh "$MIRROR" 2>/dev/null | cut -f1)"
  echo "Terminé : $(date -Is) — code $rc"
} >> "$REPORT"

# Marge sous la limite d'éléments d'un Drive partagé (~500 000)
if (( count > 400000 )); then
  echo "AVERTISSEMENT : $count fichiers — limite de ~500 000 éléments par Drive partagé en vue."
  (( rc == 0 )) && rc=2
fi

(( rc == 0 )) && echo "Pre-flight OK — $count fichiers, rien à signaler."
exit "$rc"
```

### Étape 8 : le script de synchronisation

```bash title="~/.local/bin/rclone-bisync.sh" linenums="1"
#!/usr/bin/env bash
# Passe bisync des deux paires (chiffrée + claire).
#   rclone-bisync.sh                  → passe normale
#   rclone-bisync.sh --resync         → amorçage initial
#   rclone-bisync.sh --dry-run        → simulation
#   rclone-bisync.sh --only Chiffre   → une seule paire
#   rclone-bisync.sh --force-run      → ignore les garde-fous mobiles
set -uo pipefail

MACHINE_ENV="${XDG_CONFIG_HOME:-$HOME/.config}/rclone/machine.env"
if [[ -r "$MACHINE_ENV" ]]; then set -a; . "$MACHINE_ENV"; set +a; fi

MIRROR_ROOT="${RCLONE_MIRROR_ROOT:?RCLONE_MIRROR_ROOT non défini — voir $MACHINE_ENV}"
FILTERS="${XDG_CONFIG_HOME:-$HOME/.config}/rclone/filters.txt"
LOGDIR="${XDG_DATA_HOME:-$HOME/.local/share}/rclone/logs"
WORKDIR="${XDG_CACHE_HOME:-$HOME/.cache}/rclone/bisync"
PREFLIGHT="$HOME/.local/bin/rclone-bisync-preflight.sh"

# <sous-dossier local>:<remote>
PAIRS=(
  "Chiffre:gcrypt:"
  "Clair:gd-clair:Rclone"
)

EXTRA=(); RESYNC=0; ONLY=""
while (( $# )); do
  case "$1" in
    --resync)    RESYNC=1 ;;
    --dry-run)   EXTRA+=(--dry-run) ;;
    --only)      ONLY="${2:?--only attend un nom de paire}"; shift ;;
    --force-run) FORCE_RUN=1 ;;
    *) echo "option inconnue : $1" >&2; exit 64 ;;
  esac
  shift
done
FORCE_RUN="${FORCE_RUN:-0}"

mkdir -p "$LOGDIR" "$WORKDIR"

# --- Garde-fous ------------------------------------------------------------
# Une passe sautée n'est PAS un échec : on sort en 0, sinon systemd
# déclencherait une alerte pour un comportement voulu.

# Au démarrage, le rattrapage du timer et le dispatcher réseau déclenchent des
# passes AVANT que la session ne déverrouille le trousseau. secret-tool échoue,
# rclone renvoie "Using --password-command returned: exit status 1" et chaque
# tentative produit une notification. Voir le piège n°9.
trousseau_requis_indisponible() {
  local conf="${RCLONE_CONFIG:-${XDG_CONFIG_HOME:-$HOME/.config}/rclone/rclone.conf}"
  head -1 "$conf" 2>/dev/null | grep -qi "Encrypted" || return 1   # config en clair : sans objet
  command -v secret-tool >/dev/null 2>&1 || return 1
  ! secret-tool lookup service rclone key config >/dev/null 2>&1
}

connexion_limitee() {
  local m
  m=$(busctl get-property org.freedesktop.NetworkManager /org/freedesktop/NetworkManager \
        org.freedesktop.NetworkManager Metered 2>/dev/null | awk '{print $2}')
  [[ "$m" == "1" || "$m" == "3" ]]   # 1=oui, 3=oui (deviné)
}
batterie_faible() {
  local ac
  for ac in /sys/class/power_supply/*/online; do
    [[ -r "$ac" ]] || continue
    [[ "$(cat "$ac" 2>/dev/null)" == "1" ]] && return 1   # sur secteur
  done
  local total=0 n=0 c b
  for b in /sys/class/power_supply/*/; do
    [[ "$(cat "$b/type" 2>/dev/null)" == "Battery" ]] || continue
    c=$(cat "$b/capacity" 2>/dev/null) || continue
    [[ "$c" =~ ^[0-9]+$ ]] || continue
    total=$((total + c)); n=$((n + 1))
  done
  (( n == 0 )) && return 1
  (( total / n < RCLONE_BATTERY_MIN ))
}
# Volontairement NON contournable par --force-run : forcer ne ferait qu'échouer,
# rclone étant incapable de déchiffrer sa configuration sans le trousseau.
if trousseau_requis_indisponible; then
  echo "Passe sautée : trousseau verrouillé ou indisponible (session pas encore ouverte ?)."
  exit 0
fi

if (( ! FORCE_RUN )); then
  if [[ "${RCLONE_SKIP_ON_METERED:-0}" == "1" ]] && connexion_limitee; then
    echo "Passe sautée : connexion limitée (forcer avec --force-run)."; exit 0
  fi
  if [[ -n "${RCLONE_BATTERY_MIN:-}" ]] && (( RCLONE_BATTERY_MIN > 0 )) && batterie_faible; then
    echo "Passe sautée : batterie sous ${RCLONE_BATTERY_MIN}% et débranché."; exit 0
  fi
fi

COMMON=(
  --filter-from "$FILTERS"
  --check-access                    # refuse de tourner si RCLONE_TEST manque d'un côté
  --max-delete 10                   # abandonne si plus de 10 % des entrées disparaîtraient
  --conflict-resolve newer          # le plus récent gagne
  --conflict-loser num              # ... et le perdant est conservé, suffixé
  --conflict-suffix conflict
  --resilient                       # tolère les erreurs transitoires
  --recover                         # reprend après une interruption
  --max-lock 15m                    # sans quoi les verrous n'expirent JAMAIS
  --create-empty-src-dirs           # sinon les dossiers vides ne remontent pas
  --drive-skip-gdocs                # les Docs natifs n'ont pas de taille stable
  --fast-list                       # une seule liste récursive : moins d'appels API
  --tpslimit 10                     # Drive limite la création de fichiers
  --tpslimit-burst 20
  --transfers "${RCLONE_TRANSFERS:-8}"
  --checkers  "${RCLONE_CHECKERS:-16}"
  --drive-pacer-min-sleep 10ms      # possible grâce au Client ID dédié
  --workdir "$WORKDIR"
  --log-level INFO
)
if command -v secret-tool >/dev/null 2>&1; then
  COMMON+=(--password-command "secret-tool lookup service rclone key config")
fi

rc=0
for pair in "${PAIRS[@]}"; do
  local_sub="${pair%%:*}"; remote="${pair#*:}"
  [[ -n "$ONLY" && "$ONLY" != "$local_sub" ]] && continue
  local_path="$MIRROR_ROOT/$local_sub"
  log="$LOGDIR/bisync-$local_sub.log"
  echo "=== paire $local_sub ↔ $remote ==="

  if ! "$PREFLIGHT" "$local_path"; then
    pf=$?
    if (( pf == 1 )); then echo "pre-flight BLOQUANT — paire ignorée." >&2; rc=1; continue; fi
    echo "pre-flight : avertissements, on continue."
  fi

  state_present=$(find "$WORKDIR" -maxdepth 1 -name "*$local_sub*" -print -quit 2>/dev/null)
  args=("${COMMON[@]}" "${EXTRA[@]}" --log-file "$log")

  # Corbeille locale. PAS de --suffix ici : voir le piège n°4.
  [[ -n "${RCLONE_BACKUP_ROOT:-}" ]] && args+=(--backup-dir1 "$RCLONE_BACKUP_ROOT/$local_sub")

  if (( RESYNC )); then
    echo "AMORÇAGE (--resync) demandé explicitement."; args+=(--resync)
  elif [[ -z "$state_present" ]]; then
    echo "ERREUR : aucun état bisync pour $local_sub." >&2
    echo "         Premier lancement ? Utilise : $0 --resync" >&2
    rc=1; continue
  fi

  if rclone bisync "$local_path" "$remote" "${args[@]}"; then
    echo "paire $local_sub : OK"
  else
    echo "paire $local_sub : ECHEC (voir $log)" >&2; rc=1
  fi
done
exit "$rc"
```

!!! tip "Pourquoi le script refuse de resynchroniser tout seul"
    Si l'état bisync disparaît — nettoyage de `~/.cache`, réinstallation — un `--resync` automatique **réécrirait les deux côtés** et pourrait écraser la version la plus récente. Il doit rester une décision consciente.

### Étape 9 : les unités systemd

```ini title="~/.config/systemd/user/rclone-bisync.service"
[Unit]
Description=Synchronisation bidirectionnelle rclone vers Google Drive
After=graphical-session.target
PartOf=graphical-session.target
OnFailure=rclone-notify@%n.service

[Service]
Type=oneshot
EnvironmentFile=%h/.config/rclone/machine.env
ExecStart=%h/.local/bin/rclone-bisync.sh
TimeoutStartSec=3h
Nice=10
IOSchedulingClass=idle

[Install]
WantedBy=graphical-session.target
```

```ini title="~/.config/systemd/user/rclone-bisync.timer"
[Unit]
Description=Déclenchement périodique de la synchronisation rclone

[Timer]
OnCalendar=*:0/15
Persistent=true
RandomizedDelaySec=120
AccuracySec=30s
Unit=rclone-bisync.service

[Install]
WantedBy=timers.target
```

!!! note "Le rôle de RandomizedDelaySec"
    Sans ce décalage, les deux machines taperaient l'API Drive à la même seconde. `Persistent=true` rattrape par ailleurs la passe manquée si la machine était éteinte.

```ini title="~/.config/systemd/user/rclone-notify@.service"
[Unit]
Description=Notification d'échec pour %i

[Service]
Type=oneshot
ExecStart=/usr/bin/notify-send --urgency=critical --icon=dialog-error \
    "rclone : échec de %i" \
    "Détail : journalctl --user -u %i -n 50"
```

```ini title="~/.config/systemd/user/rclone-mount@.service"
[Unit]
Description=Montage rclone du remote %i
After=graphical-session.target
PartOf=graphical-session.target
OnFailure=rclone-notify@%n.service

[Service]
Type=notify
EnvironmentFile=%h/.config/rclone/machine.env
# L'ORDRE COMPTE : le démontage doit précéder le mkdir. Voir le piège n°5.
ExecStartPre=-/bin/fusermount3 -uz %h/mnt/%i
ExecStartPre=/bin/mkdir -p %h/mnt/%i ${RCLONE_CACHE_DIR}
ExecStart=/usr/bin/rclone mount %i: %h/mnt/%i \
    --config %h/.config/rclone/rclone.conf \
    --password-command "secret-tool lookup service rclone key config" \
    --vfs-cache-mode full \
    --cache-dir ${RCLONE_CACHE_DIR} \
    --vfs-cache-max-size ${RCLONE_VFS_CACHE_MAX_SIZE} \
    --vfs-cache-max-age 168h \
    --vfs-read-chunk-size 32M \
    --vfs-read-chunk-size-limit 1G \
    --buffer-size 32M \
    --dir-cache-time 1000h \
    --poll-interval 15s \
    --drive-skip-gdocs \
    --tpslimit 10 \
    --umask 077 \
    --log-level INFO \
    --log-file %h/.local/share/rclone/logs/mount-%i.log
ExecStop=/bin/fusermount3 -uz %h/mnt/%i
ExecStopPost=-/bin/fusermount3 -uz %h/mnt/%i
Restart=on-failure
RestartSec=10

[Install]
WantedBy=graphical-session.target
```

!!! tip "dir-cache-time à 1000 h n'est pas une erreur"
    Google Drive gère la notification de changements. Avec `--poll-interval 15s`, rclone est prévenu des modifications distantes ; un cache de répertoires très long est donc sans risque et économise énormément d'appels API.

### Étape 10 : déclenchement réseau et rotation des logs

```bash title="/etc/NetworkManager/dispatcher.d/90-rclone-bisync"
#!/bin/sh
# Relance la synchronisation au retour de connectivité.
# NetworkManager exécute ce script en root ; le service visé est --user.
RCLONE_USER="user"
STATUS="$2"
case "$STATUS" in up|vpn-up) ;; *) exit 0 ;; esac

# Les événements réseau arrivent en rafale : ne rien faire si une passe tourne.
if systemctl --user --machine="${RCLONE_USER}@.host" is-active --quiet rclone-bisync.service 2>/dev/null; then
  exit 0
fi
systemctl --user --machine="${RCLONE_USER}@.host" start --no-block rclone-bisync.service 2>/dev/null
exit 0
```

```text title="/etc/logrotate.d/rclone"
/home/user/.local/share/rclone/logs/*.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su user user
    create 0640 user user
}
```

```bash
sudo install -o root -g root -m 0755 /tmp/90-rclone-bisync /etc/NetworkManager/dispatcher.d/90-rclone-bisync && sudo install -o root -g root -m 0644 /tmp/logrotate-rclone /etc/logrotate.d/rclone
```

!!! warning "La directive su du logrotate n'est pas facultative"
    logrotate refuse de traiter un répertoire inscriptible par un non-root sans indication explicite du propriétaire.

### Étape 11 : amorçage

Créez l'arborescence et les fichiers témoins des deux côtés, puis simulez **avant** d'exécuter :

```bash
mkdir -p /mnt/donnees/GoogleDrive/{Chiffre,Clair} && touch /mnt/donnees/GoogleDrive/{Chiffre,Clair}/RCLONE_TEST && rclone copy /mnt/donnees/GoogleDrive/Chiffre/RCLONE_TEST gcrypt: && rclone copy /mnt/donnees/GoogleDrive/Clair/RCLONE_TEST gd-clair:Rclone
```

```bash
~/.local/bin/rclone-bisync.sh --resync --dry-run
```

Si la simulation est propre :

```bash
~/.local/bin/rclone-bisync.sh --resync && systemctl --user enable --now rclone-bisync.timer
```

!!! warning "Le plafond des 750 Go par jour"
    Google limite l'envoi à **750 Go par jour et par utilisateur**. Pour un amorçage volumineux, étalez avec `--max-transfer 700G --cutoff-mode soft` et relancez les jours suivants.

### Étape 12 : la seconde machine

Scripts, filtres et unités sont **identiques**. Seul `machine.env` diffère. Le fichier `rclone.conf` étant chiffré, il peut transiter par `scp` sans risque.

```bash
scp ~/.config/rclone/{rclone.conf,filters.txt} user@192.168.1.42:.config/rclone/ && scp ~/.local/bin/rclone-bisync*.sh user@192.168.1.42:.local/bin/ && scp ~/.config/systemd/user/rclone-*.service ~/.config/systemd/user/rclone-*.timer user@192.168.1.42:.config/systemd/user/
```

Sur la seconde machine, déposez le mot de passe de configuration dans le trousseau local (`secret-tool store …`), adaptez `machine.env`, puis amorcez avec `--resync`.

## Pièges rencontrés

Cette section est la plus utile de l'article. Chacun de ces défauts n'est apparu qu'**au test**, et plusieurs peuvent coûter des données.

### Piège n°1 — Ne jamais pointer Crypt sur la racine d'un remote

L'assistant prévient discrètement que `monremote:` est déconseillé. Voici ce qui se passe si le Drive contient déjà des dossiers en clair :

!!! failure "Message d'erreur"
    ```
    NOTICE: Projets: Skipping undecryptable dir name: not a multiple of blocksize
    NOTICE: Factures: Skipping undecryptable dir name: not a multiple of blocksize
    ```

Le listage renvoyé est **vide**, et le message se répète à chaque passe. Un remote Crypt à la racine part du principe que *tout* ce qui s'y trouve est chiffré. **Solution** : toujours viser un sous-dossier dédié, `gd-chiffre:Rclone`. Son nom reste en clair — c'est le point d'ancrage, sans conséquence.

!!! tip "Corollaire souvent oublié"
    Les dossiers en clair qui subsistent à côté divulguent votre **structure organisationnelle**, c'est-à-dire vos sujets, même si aucun fichier n'est lisible. Si vous avez choisi `directory_name_encryption = true`, recréez cette arborescence **dans** la zone chiffrée et supprimez la version en clair.

### Piège n°2 — L'abandon « all files were changed » sur un miroir presque vide

!!! failure "Message d'erreur"
    ```
    ERROR : Safety abort: all files were changed on Path2 "gd-clair:Rclone/". Run with --force if desired.
    NOTICE: Bisync aborted. Please try again.
    ```

Quand une paire ne contient qu'**un seul fichier** (typiquement `RCLONE_TEST` juste après l'amorçage), sa réécriture par l'autre machine représente 100 % du contenu — ce que bisync interprète comme un côté vidé par accident. Le garde-fou fonctionne parfaitement ; c'est le jeu de données minuscule qui le rend pathologique.

Le défaut est **persistant** : la paire échoue à chaque passe, donc toutes les 15 minutes, avec une notification à chaque fois. **Solution** : déposer un second fichier stable dans chaque zone. Un `LISEZMOI.txt` documentant le dossier fait très bien l'affaire et sert deux fois.

### Piège n°3 — `--max-delete` est un pourcentage, pas un nombre

L'aide générique annonce `--max-delete int : When synchronizing, limit the number of deletes`. C'est vrai pour `rclone sync`, **faux pour bisync**, qui en redéfinit le sens :

!!! failure "Message d'erreur"
    ```
    ERROR : Safety abort: too many deletes (>10%, 19 of 31) on Path1 "/mnt/donnees/GoogleDrive/Chiffre/". Run with --force if desired.
    ```

Deux subtilités vérifiées par l'expérience : le dénominateur inclut les **dossiers**, pas seulement les fichiers ; et la comparaison est un « strictement supérieur ». Une suppression tombant à exactement 10 % passe donc sans être bloquée.

### Piège n°4 — `--suffix` neutralise silencieusement `--max-delete`

En ajoutant `--backup-dir1` pour disposer d'une corbeille locale, la tentation est d'y joindre un `--suffix` horodaté pour éviter que deux sauvegardes successives ne s'écrasent. **Ne le faites pas.**

`--suffix` est un drapeau **global**. En l'absence de `--backup-dir2`, rclone l'applique aussi au côté distant, où il **renomme** les fichiers au lieu de les supprimer. Conséquence : plus aucune suppression à compter, donc `--max-delete` ne protège plus rien, et l'arborescence Drive se remplit de copies suffixées. Le symptôme est trompeur — la passe se termine par un `OK` rassurant.

### Piège n°5 — Un montage qui ne survit pas à un plantage

Après un `kill -9` du processus `rclone mount`, systemd relance bien le service, mais celui-ci reste bloqué :

!!! failure "Message d'erreur"
    ```
    mkdir: impossible d'évaluer «/home/user/mnt/gd-clair»: Noeud final de transport n'est pas connecté
    rclone-mount@gd-clair.service: Control process exited, code=exited, status=1/FAILURE
    ```

Deux causes cumulées. D'abord, **`ExecStop` n'est pas exécuté quand le processus principal est déjà mort** : le montage FUSE fantôme subsiste. Il faut un `ExecStopPost`, qui lui tourne systématiquement. Ensuite, l'**ordre des `ExecStartPre` compte** : si `mkdir` précède le `fusermount3 -uz`, il échoue en tentant d'inspecter un chemin cassé, ce qui coûte un cycle d'échec et une notification inutile avant que le service ne se rétablisse.

### Piège n°6 — Le verrou bisync est local, et par défaut éternel

`--max-lock` vaut **0** par défaut, c'est-à-dire que les verrous n'expirent jamais. Après une interruption — mise en veille, coupure réseau, plantage — la machine concernée reste bloquée :

!!! failure "Message d'erreur"
    ```
    NOTICE: Failed to bisync: prior lock file found: ~/.cache/rclone/bisync/….lck
    Tip: this indicates that another bisync run (of these same paths) either is still
    running or was interrupted before completion.
    ```

Deux précisions utiles. Le verrou est **local** (`~/.cache/rclone/bisync/*.lck`), pas sur le remote : il ne bloque donc que la machine concernée, pas les deux. Et `--max-lock 15m` suffit à le rendre auto-expirant, rclone le renouvelant tant que la passe tourne. Sans cette option, il faut supprimer le fichier à la main.

Bonne nouvelle vérifiée au test : une fois le verrou levé, la passe suivante se termine **sans `--resync`** grâce à `--resilient` et `--recover`. Un test réel — passe tuée par `SIGKILL` à 8 fichiers sur 300 — s'est soldé par une reprise complète et automatique.

### Piège n°7 — Faire cohabiter bisync avec un autre client de synchronisation

Si votre disque héberge déjà Nextcloud, Synology Drive, Dropbox ou OneDrive, **le miroir bisync doit vivre dans un répertoire strictement disjoint**. Deux agents sur les mêmes fichiers produisent une boucle de conflits, et les fichiers temporaires ou partiels de l'un partent sur le cloud de l'autre. Le script pre-flight de l'étape 7 détecte ce recouvrement et refuse de démarrer.

### Piège n°8 — Nettoyer avec les timers actifs

Erreur d'exploitation classique, à connaître : supprimer des fichiers sur les deux machines et sur Drive **pendant que les timers tournent** ne fonctionne pas. Une passe automatique se déclenche au milieu et repousse ce que vous venez d'effacer. La procédure correcte :

```bash
systemctl --user stop rclone-bisync.timer
```

Puis supprimer sur **les trois côtés**, relancer un `--resync`, et seulement ensuite redémarrer le timer.

### Piège n°9 — Le trousseau n'est pas encore déverrouillé au démarrage

Celui-ci ne se manifeste qu'au **premier vrai redémarrage**, et il se reproduit à chacun.

!!! failure "Message d'erreur"
    ```
    gnome-keyring-daemon: couldn't create system prompt:
      GDBus.Error:org.freedesktop.DBus.Error.Spawn.ChildExited:
      Process org.gnome.keyring.SystemPrompter exited with status 1
    ERROR : Using --password-command returned: exit status 1
    ```

Au démarrage, deux mécanismes déclenchent des passes **avant** que la session graphique n'ait déverrouillé le trousseau : le rattrapage `Persistent=true` du timer, qui compense la passe manquée pendant l'extinction, et le dispatcher NetworkManager, qui réagit à *chaque* interface qui monte — filaire, VPN, ponts. Sur une machine réelle, cela fait facilement quatre déclenchements dans les deux minutes suivant le démarrage, contre quatre pour le timer sur l'heure entière.

À ce moment-là `secret-tool` ne peut pas ouvrir la collection : elle est verrouillée et le prompteur graphique n'est pas encore disponible. rclone ne peut donc pas déchiffrer sa configuration, le service tombe en échec, et `OnFailure` déclenche une notification à chaque tentative. Le tout se résorbe seul une fois la session ouverte — mais l'utilisateur a déjà reçu une volée d'alertes pour un problème qui n'en est pas un.

!!! tip "Détail savoureux"
    La toute première notification échoue elle aussi, avec `org.freedesktop.Notifications exited with status 1` : le démon de notification n'est pas davantage démarré que le trousseau.

**Solution** : la fonction `trousseau_requis_indisponible()` du script (étape 8). Si la configuration est chiffrée et que le trousseau ne répond pas, la passe est **sautée avec un code de sortie 0**. systemd la considère comme réussie, aucune alerte n'est levée, et la passe suivante s'exécutera normalement une fois la session ouverte.

Deux choix de conception méritent d'être soulignés. Le garde-fou est **délibérément non contournable** par `--force-run` : forcer ne ferait qu'échouer plus bruyamment, rclone étant de toute façon incapable de déchiffrer sa configuration. Et il ne s'active **que si la configuration est réellement chiffrée** — sur une machine où elle est en clair, il ne doit jamais bloquer quoi que ce soit.

!!! warning "Ne confondez pas avec une vraie panne"
    Tant que ce garde-fou n'est pas en place, le symptôme visible est un service en échec au démarrage. Il est tentant d'incriminer le réseau, les identifiants OAuth ou la configuration rclone. Le seul indice fiable est `Using --password-command returned: exit status 1` dans les journaux rclone : c'est le trousseau, rien d'autre.

## Vérification

Une configuration bisync ne se déclare pas fonctionnelle parce qu'elle affiche `OK` une fois. Voici la batterie de tests à passer.

**1. Le chiffrement est-il réel ?** Comparez la vue déchiffrée et la vue brute :

```bash
rclone lsf -R gcrypt: --password-command "secret-tool lookup service rclone key config" && echo "--- ce que Google stocke ---" && rclone lsf -R gd-chiffre:Rclone --password-command "secret-tool lookup service rclone key config"
```

!!! success "Résultat attendu"
    La première commande affiche vos noms réels. La seconde ne doit montrer **que** des chaînes opaques du type `ikdg52let48cvkrm2adjanbcbo/g240t6gvaie4vj8d6lsgr804nk/`, dossiers compris.

**2. Le conflit est-il arbitré sans perte ?** Modifiez le même fichier sur les deux machines sans synchroniser entre les deux, puis lancez une passe de chaque côté.

!!! success "Résultat attendu"
    La version la plus récente conserve son nom ; l'autre est présente à côté sous `nomdufichier.conflict1`. Les deux machines convergent vers le même état.

**3. Le garde-fou de suppression tient-il ?** Supprimez plus de 10 % des entrées d'une paire et lancez une passe. La passe doit **échouer** et rien ne doit disparaître du côté distant.

**4. Le montage se relève-t-il ?**

```bash
systemctl --user show -p MainPID --value rclone-mount@gd-clair.service | xargs -r kill -9 && sleep 18 && systemctl --user is-active rclone-mount@gd-clair.service && ls ~/mnt/gd-clair
```

!!! danger "Piège de ce test"
    N'utilisez pas `pgrep -f "rclone mount"` pour trouver le PID : le motif correspond aussi à **votre propre ligne de commande**, et vous tuerez votre shell. Passez par `systemctl show -p MainPID`.

**5. L'alerte fonctionne-t-elle vraiment ?** Provoquez un échec réel et vérifiez que `OnFailure` déclenche :

```bash
mv /mnt/donnees/GoogleDrive/Chiffre/RCLONE_TEST /mnt/donnees/GoogleDrive/Chiffre/.masque && systemctl --user start rclone-bisync.service; journalctl --user -u "rclone-notify@*" --since "2 min ago" --no-pager | tail -3
```

Pensez à restaurer le témoin ensuite.

**6. La propagation automatique.** Déposez un fichier sur une machine et **ne lancez rien**. Il doit apparaître sur l'autre en deux cycles de timer, soit une trentaine de minutes avec `OnCalendar=*:0/15`.

**7. Après redémarrage.** C'est la vérification la plus révélatrice, et celle qu'on oublie le plus souvent. Redémarrez réellement, ouvrez votre session, puis attendez une heure avant d'inspecter :

```bash
systemctl --user list-timers rclone-bisync.timer; journalctl --user -b -u rclone-bisync.service --no-pager | grep -c Starting; grep -c "password-command" ~/.local/share/rclone/logs/*.log
```

!!! success "Résultat attendu"
    Une prochaine échéance affichée, et **zéro** occurrence de `password-command` dans les journaux. Le nombre de déclenchements dépassera celui du timer seul — c'est normal, voir le piège n°9. Ce qui compte est qu'aucun ne se solde par un échec.

## Aide-mémoire

| Commande | Description |
|---|---|
| `rclone-bisync.sh` | Passe normale sur les deux paires |
| `rclone-bisync.sh --dry-run` | Simulation, n'écrit rien |
| `rclone-bisync.sh --resync` | Amorçage / re-base (à utiliser sciemment) |
| `rclone-bisync.sh --only Chiffre` | Traite une seule paire |
| `rclone-bisync.sh --force-run` | Ignore les garde-fous batterie et connexion limitée |
| `systemctl --user list-timers rclone-bisync.timer` | Prochaine et dernière exécution |
| `journalctl --user -u rclone-bisync.service -n 50` | Journal de la dernière passe |
| `systemctl --user start rclone-mount@gd-clair.service` | Monte un remote à la demande |
| `rclone lsf -R gcrypt:` | Vue déchiffrée du contenu distant |
| `rclone lsf -R gd-chiffre:Rclone` | Vue brute, telle que Google la stocke |
| `rm ~/.cache/rclone/bisync/*.lck` | Lève un verrou bloquant après un plantage |
| `rclone selfupdate --package deb` | Met à jour rclone en conservant le paquet |

## Checklist de déploiement

- [ ] rclone ≥ 1.66 installé depuis le `.deb` officiel, signature vérifiée, paquet figé
- [ ] `libsecret-tools` installé sur **chaque** machine
- [ ] Projet Google Cloud dans l'organisation, écran de consentement en **Interne**
- [ ] Client OAuth de type **Application de bureau**
- [ ] Remote Crypt pointant sur un **sous-dossier**, jamais sur la racine
- [ ] Mot de passe **et sel** Crypt notés dans le gestionnaire de mots de passe
- [ ] Configuration chiffrée, mot de passe dans le trousseau, sauvegarde en clair détruite
- [ ] Miroir sur un support **non amovible**, disjoint de tout autre client de synchronisation
- [ ] Fichiers `RCLONE_TEST` présents des deux côtés de chaque paire
- [ ] Second fichier stable dans chaque zone (évite le piège n°2)
- [ ] `--dry-run` propre avant le premier `--resync`
- [ ] Test de conflit provoqué concluant
- [ ] Test de suppression massive bloqué par `--max-delete`
- [ ] Notification d'échec vérifiée par un échec réel
- [ ] Garde-fou trousseau en place dans le script (sinon échecs à chaque démarrage)
- [ ] Comportement après **redémarrage réel** vérifié, journaux sans `password-command`
- [ ] Aller-retour création / modification / suppression testé **dans les deux sens**

## Glossaire

bisync
:   Mode de rclone assurant une synchronisation **bidirectionnelle** entre deux emplacements, avec détection des conflits. À distinguer de `sync`, unidirectionnel et destructif pour la destination.

Crypt
:   Type de remote rclone servant d'enveloppe autour d'un autre remote. Il chiffre le contenu, et optionnellement les noms de fichiers et de dossiers, **avant** l'envoi. Le fournisseur ne voit jamais les données en clair.

Sel (`password2`)
:   Second secret combiné au mot de passe lors de la dérivation de clé. Perdre le sel équivaut à perdre le mot de passe : les données deviennent irrécupérables.

VFS cache
:   Cache local utilisé par `rclone mount` pour permettre lecture et écriture aléatoires sur un système de fichiers distant. Sans lui, beaucoup d'applications échouent sur un montage réseau.

Drive partagé
:   Espace Google Workspace appartenant à l'organisation et non à un utilisateur. Plafonné à environ **500 000 éléments**, indépendamment du volume — c'est le nombre de fichiers, et non les téraoctets, qui devient contraignant.

## Ressources

- [Documentation rclone bisync](https://rclone.org/bisync/) — Référence des options et des garde-fous
- [Documentation rclone crypt](https://rclone.org/crypt/) — Fonctionnement du chiffrement et dérivation de clé
- [Configurer son propre Client ID Google Drive](https://rclone.org/drive/#making-your-own-client-id) — Procédure officielle
- [Limites d'un Drive partagé](https://support.google.com/a/answer/7338880) — Plafonds d'éléments et de contenus
- [Vérification des signatures rclone](https://rclone.org/release_signing/) — Empreinte de la clé de release
