# Méthodologie de fact-check — procédure détaillée et reproductible

> Méthodologie détaillée et reproductible. Consulter pour **atomiser** un texte, fixer le **standard de preuve**, **vérifier la syntaxe d'une commande** et gérer **versions / dépréciation**.

Ce fichier outille les étapes **2 (atomiser)**, **4 (construire la requête)**, **5 (vérifier à la source primaire)** et **6 (statuer)** du workflow `it-fact-checker`. Il fournit les règles opérationnelles que `SKILL.md` résume : comment découper, comment prouver, comment lire une man page, comment chasser la dépréciation, comment attribuer un statut sans halluciner. Pour le **choix de l'autorité par Tier** voir `references/sources-fiables.md` ; pour les **requêtes `site:` et pièges par domaine** voir `references/domaines.md` ; pour le **gabarit du livrable** voir `assets/modele-rapport.md`.

**Principe central** : on ne valide jamais un fait « de mémoire ». Chaque donnée factuelle est isolée, rattachée à une autorité compétente, confrontée à un texte officiel **daté et versionné**, puis statuée. À défaut de preuve primaire → **⚪ Inconnu**, jamais 🟢.

## Table des matières

1. [Atomiser les affirmations](#1-atomiser-les-affirmations)
2. [Standard de preuve](#2-standard-de-preuve)
3. [Vérifier la syntaxe d'une commande](#3-vérifier-la-syntaxe-dune-commande)
4. [Ports & RFC](#4-ports--rfc)
5. [Versions & dépréciation (garde-fou central)](#5-versions--dépréciation-garde-fou-central)
6. [Vulnérabilités (CVE / CVSS / ATT&CK)](#6-vulnérabilités-cve--cvss--attck)
7. [Scoring de confiance & barème](#7-scoring-de-confiance--barème)
8. [Garde-fous anti-hallucination (récap opérationnel)](#8-garde-fous-anti-hallucination-récap-opérationnel)

---

## 1. Atomiser les affirmations

**Règle d'or : une donnée factuelle = une ligne = une affirmation vérifiable.** Une phrase de tutoriel comme « WireGuard écoute en UDP sur le port 51820 par défaut et il faut régler `PersistentKeepalive` à 25 » contient **trois** affirmations distinctes (protocole UDP, port 51820, valeur 25) qui se vérifient et se statuent **séparément**. Ne jamais statuer en bloc : une phrase peut être 🟢 sur le port et 🟠 sur le keepalive.

### Procédure

1. Lire le texte soumis et **surligner mentalement** chaque donnée technique objective.
2. Réécrire chaque donnée en une proposition **atomique** (un seul fait), au présent, sans condition implicite.
3. **Numéroter** : `A1`, `A2`, `A3`, … L'ordre suit le texte source pour faciliter la relecture.
4. **Écarter** opinion, style, transition, justification pédagogique : non vérifiable ⇒ non listé.

### Cibles prioritaires (éléments hallucinables)

| Catégorie | Exemples typiques | Autorité de vérification |
|-----------|-------------------|--------------------------|
| **Numéros de port** | `51820`, `5201`, `2049`, `11434`, `8080` | `iana.org` (cf. §4) |
| **Flags / options de commande** | `rsync -a`, `nmap -sS`, `ssh -J`, `git pull --rebase` | man page / doc CLI (cf. §3) |
| **Chemins de fichiers** | `/etc/ssh/sshd_config`, `/etc/netplan/*.yaml`, `/etc/sudoers.d/` | doc projet / man page section 5 |
| **Valeurs par défaut** | préfixe tmux `Ctrl-b`, `proxy_read_timeout 60s`, port Ollama `11434` | doc projet (jamais supposée, cf. §8) |
| **Actions IAM / noms d'API** | `s3:ListAllMyBuckets`, `aws ec2 run-instances` | `docs.aws.amazon.com` (Service Authorization Reference) |
| **Clés / directives de config** | YAML Netplan, `compose.yaml`, `sshd_config`, HCL Terraform | doc projet + spec (cf. §5) |
| **Acronymes & attribution** | « VLAN 802.1Q est une RFC », « HTTP/2 est une norme W3C » | autorité réelle (cf. `sources-fiables.md`) |
| **Numéros / titres de RFC** | `RFC 8446`, « RFC 2616 décrit HTTP/1.1 » | `rfc-editor.org` (cf. §4) |
| **CVE / CVSS** | `CVE-2024-XXXX`, score `9.8`, versions affectées | NVD + cve.org (cf. §6) |
| **Comportements liés à une version** | `gateway4` Netplan, `version:` Compose, rotation NIST | doc datée + checklist dépréciation (cf. §5) |

!!! example "Atomisation — avant / après"
    **Texte soumis** : « Pour ouvrir le pare-feu, on autorise le port 51820 en TCP, car WireGuard utilise TCP comme la plupart des VPN. »

    **Affirmations atomiques** :

    - `A1` — Le port par défaut de WireGuard est `51820`.
    - `A2` — WireGuard utilise le protocole **TCP**.
    - `A3` — « La plupart des VPN utilisent TCP » (généralité — **à écarter** : opinion non atomique / non vérifiable telle quelle).

    Résultat anticipé : `A1` 🟢 (port correct) mais `A2` 🔴 (WireGuard est **UDP-only**) — une seule phrase, deux verdicts opposés. C'est exactement ce que l'atomisation révèle.

!!! tip "Granularité"
    Si une affirmation est encore décomposable en sous-faits qui pourraient diverger de statut, **décompose encore**. Une affirmation bien atomisée ne peut être qu'« entièrement vraie » ou « entièrement fausse » — jamais « à moitié vraie ».

---

## 2. Standard de preuve

**Hiérarchie : Tier 1 > Tier 2 >> Tier 3.** Le détail des sources par Tier est dans `references/sources-fiables.md` ; ici on fixe la **règle d'usage**.

| Niveau | Rôle dans la preuve | Peut trancher un fait technique ? |
|--------|---------------------|-----------------------------------|
| **Tier 1** (IANA, IETF/RFC Editor, NIST, NVD, IEEE, ANSSI/CERT-FR, ISO, W3C) | Preuve **primaire d'autorité** : ports, RFC, normes, algos, scores | **Oui** |
| **Tier 2** (man7.org, doc éditeur/projet : AWS, MS Learn, GCP, Docker, OpenSSH, Netplan, nginx…) | Preuve **primaire d'implémentation** : syntaxe, flags, valeurs par défaut | **Oui** |
| **Tier 3** (Arch Wiki, Nmap/Lynis/CrowdSec docs, cve.org descriptif, IT-Connect, Korben) | **Corroboration & contexte** uniquement | **Non — jamais seul** |

### Règles non négociables

1. **Un fait technique exige Tier 1 ou Tier 2.** Un port, un flag, une valeur par défaut, une clé de config, un numéro de RFC ne se valident **que** sur du Tier 1/2.
2. **Copier la formulation officielle, pas une paraphrase.** Le verdict cite le **texte exact** de la source (libellé d'option, nom de directive, valeur littérale). Une paraphrase introduit le risque d'hallucination qu'on cherche à éliminer.
3. **Citer page + version + date.** La colonne « Source » du rapport porte une **référence précise** (ex. `man7.org systemctl.1 ; consultée 2026-06-29`), jamais un domaine racine vague (`man7.org` seul est interdit).
4. **Tier 3 corrobore, ne tranche pas.** Il sert à *pister* une réponse ou à *contextualiser*, puis on remonte au Tier 1/2 pour le verdict. Il n'apparaît **jamais** comme unique source d'un verdict 🟢 factuel.
5. **Pas de source officielle ⇒ ⚪ Inconnu.** On ne comble jamais l'absence de preuve par la mémoire du modèle (cf. §7 et §8).

!!! warning "Le piège de la paraphrase"
    Un LLM (y compris celui qui rédige le rapport) peut « se souvenir » d'une formulation **plausible mais inexacte**. La parade est mécanique : ouvrir la source, **lire l'option/la valeur littérale**, la recopier. Si l'on ne peut pas recopier le texte officiel, c'est qu'on ne l'a pas vérifié → ⚪.

### Construire la requête de preuve

Pour chaque affirmation, formuler une requête `site:` ciblée sur **le domaine officiel approprié** (modèles détaillés par domaine dans `references/domaines.md`) :

```
# Forcer la doc officielle, court-circuiter les blogs SEO
wireguard default listen port site:wireguard.com
systemctl enable --now behavior site:man7.org
IAM action list buckets exact name site:docs.aws.amazon.com
802.1Q VLAN tag standard site:standards.ieee.org
service names port numbers registry site:iana.org
```

- **Forcer Tier 1/2** dans la requête (`site:<domaine officiel>`).
- **Bloquer la denylist** (blogs SEO, forums/Q&A en source primaire, contenu IA, pages non datées sur sujets versionnés) — voir denylist dans `sources-fiables.md`.
- **Ne jamais inventer d'URL** : se limiter aux domaines racines réels listés ; si l'URL profonde est incertaine, citer le domaine officiel + la requête `site:` plutôt que fabriquer un chemin.

---

## 3. Vérifier la syntaxe d'une commande

C'est la zone la plus hallucinée : flags inventés, options renommées, confusion court/long, sous-commande cloud inexistante. Procédure stricte.

### 3.1 Lire la man page dans la BONNE section

`man7.org` (et les man pages officielles du projet) sont organisées en **sections numérotées**. Lire la mauvaise section = vérifier le mauvais objet.

| Section | Contenu | Exemples wiki |
|---------|---------|---------------|
| **1** | Commandes utilisateur (binaires) | `rsync.1`, `ssh.1`, `git.1`, `dig.1`, `tmux.1`, `nmap.1` |
| **5** | Formats de fichiers / fichiers de configuration | `sshd_config.5`, `ssh_config.5`, `sudoers.5`, `pwquality.conf.5` (conf du module) |
| **8** | Administration système / démons | `mount.8`, `sshd.8`, `cryptsetup.8`, `nft.8` (syntaxe nftables), `pam_pwquality.8` (module PAM) |

!!! example "Section = objet vérifié"
    - Vérifier l'**option `-a` de rsync** → `rsync.1` (commande). On confirme que `-a` = `-rlptgoD` (archive).
    - Vérifier la **directive `AuthenticationMethods`** → `sshd_config.5` (fichier de conf), **pas** `ssh.1`.
    - Vérifier le **comportement du démon** SSH → `sshd.8`.
    - Vérifier `pam_pwquality` : le **module PAM** est en section **8** (`pam_pwquality.8`), mais ses **options de conf** (`minlen`, `dcredit`…) sont aussi documentées dans **`pwquality.conf.5`** (le fichier de conf). Lire la section qui correspond à l'objet vérifié.
    Requête type : `rsync archive option -a equals site:man7.org` puis `sshd_config AuthenticationMethods site:man7.org`.

### 3.2 Vérifier qu'un flag EXISTE et n'est pas déprécié/renommé

- Le flag est-il **présent** dans la man page de la version cible ? (un flag « plausible » n'existe pas forcément).
- A-t-il été **renommé / déprécié** ? (OpenSSH renomme/retire des directives entre versions — cf. §5).
- Son **comportement** correspond-il à l'affirmation ? (ex. `nmap -sS` = scan SYN ≠ `-sT` = connect ; les confondre est une erreur factuelle).

### 3.3 Ne pas confondre option courte et option longue

Beaucoup d'outils exposent `-x` **et** `--xxxx`. Vérifier que la forme citée existe réellement et qu'elle correspond bien à la forme longue supposée. Recopier la **forme officielle** (l'équivalence courte/longue est documentée, ne pas la supposer).

### 3.4 CLI cloud : verbe/sous-commande exact + statut GA vs beta/preview

Pour `aws`, `az`, `gcloud` :

- Vérifier le **verbe et la sous-commande exacts** (ex. `aws ec2 run-instances`, `az container create`, `gcloud run deploy`) dans la doc officielle — pas une commande « vraisemblable ».
- Vérifier le **statut** : une commande peut être en **`beta`/`preview`** (`gcloud beta …`) et non GA, ou inversement promue en GA. Le préciser conditionne un 🟢 vs 🟠.
- Pour les **actions IAM** (policies JSON AWS), vérifier **chaque `Action`** dans la *Service Authorization Reference* (ex. `s3:ListAllMyBuckets` existe ; `s3:ListAllBuckets` est une **hallucination** classique).

!!! danger "Mélange de syntaxes"
    Ne jamais valider une règle qui **mélange deux outils** : `-A POSTROUTING` (iptables) glissé dans une règle **nftables** est faux. La syntaxe `nft` (tables/chaînes/hooks/priorités) se vérifie sur `netfilter.org`, pas par analogie avec iptables.

---

## 4. Ports & RFC

### 4.1 Tout numéro de port se confirme sur `iana.org`

Le **Service Name and Transport Protocol Port Number Registry** de l'IANA est l'**autorité absolue** : numéro, nom de service, **protocole de transport** (TCP/UDP), plage (well-known 0-1023 / registered 1024-49151 / dynamic 49152-65535).

- Confirmer le **numéro** ET le **protocole** (un port peut être TCP, UDP, ou les deux — ne pas supposer).
- Les ports sont **la première chose qu'un LLM invente** : ne jamais valider « de mémoire ».
- Requête : `service names port numbers registry site:iana.org`, puis recouper la **valeur par défaut réelle** du projet sur sa doc (Tier 2) — l'IANA donne l'assignation officielle, le projet donne le **défaut applicatif** (ils peuvent différer : un projet peut écouter sur un port non assigné par défaut).

!!! example "Port : assignation IANA vs défaut projet"
    - WireGuard : **UDP 51820** est le défaut documenté par le projet (`wireguard.com`) ; confirmer le protocole **UDP** (UDP-only).
    - Ollama : **11434/TCP** est le défaut documenté (`ollama.com`) — à ne pas confondre avec Open WebUI (**8080**).
    - iperf3 : **5201** ; NFSv4 : **2049**. Chacun se confirme, jamais ne se devine.

### 4.2 Toute RFC se vérifie sur `rfc-editor.org`

Pour chaque RFC citée, vérifier **quatre** choses :

1. Le **numéro** existe et correspond au sujet.
2. Le **titre EXACT** (recopier, ne pas paraphraser).
3. Le **statut (maturity level)** : `Internet Standard` / `Proposed Standard` / `Experimental` / `Informational` / `Historic`. Attention : « obsolète » n'est **pas** un statut mais une **relation** — vérifier en plus les mentions **« Obsoleted by »** et **« Updated by »** (une RFC peut rester « Proposed Standard » tout en étant remplacée par une autre).
4. Les **errata** éventuels.

!!! danger "Le piège de la RFC remplacée (hallucination classique)"
    Citer une RFC **obsolète** comme courante est une erreur factuelle fréquente. Exemple typique : attribuer HTTP/1.1 à `RFC 2616` alors qu'elle est **obsolète**, remplacée par les RFC 7230-7235 (puis refondues en RFC 9110-9114). Le réflexe : lire le bandeau « Obsoleted by » sur `rfc-editor.org` avant de citer.

!!! warning "Attribuer la BONNE autorité (pas toujours une RFC)"
    Une norme citée comme « RFC » alors qu'elle n'en est pas une est une hallucination en soi :

    - **VLAN 802.1Q = IEEE** (`standards.ieee.org`), **jamais** une RFC IETF.
    - **HTTP moderne = IETF** (`rfc-editor.org`), pas le W3C ; **HTML = WHATWG**.
    - **Cryptographie / mots de passe = NIST** (SP 800-series), pas une RFC.

    Vérifier l'autorité compétente dans `references/sources-fiables.md` avant de citer.

---

## 5. Versions & dépréciation (garde-fou central)

**Une affirmation « vraie en 2018 » peut être 🔴 aujourd'hui.** C'est le risque n°1 sur un wiki de tutoriels : un LLM ressort une syntaxe morte avec une assurance totale.

### 5.1 Toujours fixer OS et version

- **Cible par défaut du wiki : Ubuntu 24.04 LTS** (sauf indication contraire de l'auteur).
- Citer dans le verdict la **version de la doc** ET la **version du logiciel** concernées. Une option valide sur une version peut être absente/renommée sur une autre.
- Utiliser la **date du jour** comme repère de fraîcheur (rate limits, quotas, API évoluent — cf. §8).

### 5.2 Checklist de dépréciation (sujets versionnés)

Pour tout sujet versionné, vérifier **explicitement** que la syntaxe/valeur n'est pas obsolète :

| Sujet | Forme DÉPRÉCIÉE / morte | Forme ACTUELLE à confirmer | Autorité |
|-------|-------------------------|----------------------------|----------|
| Docker Compose | champ **`version:`** en tête de `compose.yaml` | omis (Compose Specification) | `compose-spec.io`, `docs.docker.com` |
| Docker Compose CLI | **`docker-compose`** (v1, tiret, EOL) | **`docker compose`** (v2, plugin) | `docs.docker.com` |
| Netplan | **`gateway4:`** | **`routes:`** (avec `to: default`, `via:`) | `netplan.io` |
| OpenSSH | directives **renommées/retirées** selon version | libellé exact de la version cible | `openssh.com` |
| Packer | ancienne syntaxe **JSON** | **HCL2** (standard actuel) | `developer.hashicorp.com` |
| Terraform | interpolation `"${…}"` hors contexte, `provider` legacy | `required_providers`, attributs du Registry | `registry.terraform.io` |
| Kubernetes | **`apiVersion`** d'une API retirée | `apiVersion` de la version du cluster | `kubernetes.io` |
| `gcloud` / `az` | verbe en **`beta`/`preview`** présenté comme GA | statut réel (GA vs preview) | `cloud.google.com`, `learn.microsoft.com` |

### 5.3 Recommandations de sécurité périmées (NIST — piège fréquent)

Un LLM ressort souvent la **doctrine ancienne** des mots de passe. Référence actuelle : **NIST SP 800-63B**.

- **Pas de rotation forcée** périodique (les « 90 jours » sont une recommandation **abandonnée**, sauf compromission avérée).
- **Pas de complexité imposée** par classes de caractères ; privilégier la **longueur** et le contrôle contre les listes de mots de passe compromis.
- **Algorithmes dépréciés** présentés comme sûrs : **SHA-1, RSA-1024, DES/3DES** sont déconseillés — recouper **NIST SP 800-131A** (transitions d'algorithmes) et, côté FR, les guides **ANSSI** (`cyber.gouv.fr`, en vérifiant la **date** du guide).

!!! tip "Réflexe dépréciation"
    Devant toute valeur/syntaxe sur un sujet versionné, poser la question : **« cette forme est-elle toujours la forme actuelle, ou une survivance ? »** et le vérifier sur la doc **datée**. Une page sans date ni version sur un sujet versionné relève de la **denylist**.

---

## 6. Vulnérabilités (CVE / CVSS / ATT&CK)

**Ne jamais inventer un identifiant `CVE-AAAA-NNNNN` ni un score CVSS.** C'est l'une des hallucinations les plus dommageables.

### Procédure de recoupement (≥ 2 sources)

| Élément à vérifier | Source autoritaire | Tier |
|--------------------|--------------------|------|
| **Score CVSS** + **versions affectées** | NVD (`nvd.nist.gov`) | Tier 1 (fait de vulnérabilité) |
| **Existence + description de référence** du CVE | CVE Program (`cve.org`) | Tier 3 (descriptif) — recouper le score sur NVD |
| **Exploitation active** (KEV / avis) | CISA (`cisa.gov`), CERT-FR (`cert.ssi.gouv.fr`) | Tier 1/3 |

- Confirmer que l'identifiant **existe** et correspond au produit/à la version cités.
- Recouper le **score CVSS** sur NVD (ne pas le « deviner » — un score inventé est faux par construction).
- Vérifier les **versions affectées** : une vulnérabilité peut ne concerner qu'une plage précise.
- Pour l'**exploitation active**, corroborer via CISA KEV ou un avis **CERT-FR** (`CERTFR-AAAA-AVI-NNNN`).

### Techniques d'attaque — MITRE ATT&CK

- Nommer une technique via son **ID `Txxxx`** sur `attack.mitre.org`.
- Vérifier que l'ID **existe** et n'est **pas déprécié/renommé** entre versions du framework (les IDs sont parfois fusionnés/retirés).
- Requête : `<nom technique> technique id site:attack.mitre.org`.

!!! danger "CVE / score = jamais de mémoire"
    Si NVD/cve.org ne confirment ni l'identifiant ni le score → **⚪ Inconnu** et re-sourçage exigé. Un CVE « plausible » non confirmé est traité comme **non vérifié**, jamais comme 🟢.

---

## 7. Scoring de confiance & barème

Attribuer **un** statut par affirmation atomique. Le barème est celui de `SKILL.md` et du gabarit `assets/modele-rapport.md`.

| Statut | Quand l'attribuer | Exigence de source |
|--------|-------------------|--------------------|
| 🟢 **Vrai** | Confirmé **tel quel** par la source primaire | Tier 1 **ou** Tier 2, formulation officielle recopiée |
| 🟠 **Nuancé** | Exact **sous condition** (voir ci-dessous) | Tier 1/2 + précision de la condition |
| 🔴 **Faux** | **Contredit** par la source primaire | Tier 1/2 + **correction exacte** |
| ⚪ **Inconnu** | Aucune source officielle ne tranche | — (à re-sourcer, **jamais** comblé) |

### Quand 🟠 Nuancé (et pas 🟢)

Le 🟠 est réservé aux cas **« exact sous condition »** — l'affirmation n'est pas fausse, mais une réserve manque :

- **Dépend de la version / de l'OS** (vrai sur 24.04, faux ailleurs ; vrai à partir de telle version d'un outil).
- **Valeur CONSEILLÉE ≠ valeur PAR DÉFAUT.** Exemple : `PersistentKeepalive 25` (WireGuard) est **conseillé** derrière du NAT, mais **n'est pas un défaut** — une affirmation qui le présente comme « le défaut » est 🟠 (ou 🔴 si elle l'affirme explicitement comme défaut).
- **Dépend du contexte** (renderer Netplan networkd vs NetworkManager ; édition CE vs BE d'un outil ; OSS vs commercial).
- **Vrai mais incomplet** d'une manière qui changerait l'action de l'utilisateur (prérequis omis, condition d'activation tue).

### Règle anti-hallucination du scoring

!!! danger "Mémoire du modèle ou Tier 3 seul ⇒ ⚪, jamais 🟢"
    Si la **seule** justification d'un fait est la **mémoire du modèle** ou une **source Tier 3** (Arch Wiki, IT-Connect, Korben, descriptif cve.org…), le verdict est **⚪ Inconnu** — **pas** 🟢. Un 🟢 exige une preuve Tier 1/2 recopiée. C'est la barrière qui empêche le fact-checker de propager l'hallucination qu'il est censé détecter.

- Un **doute non levé** ne devient pas 🟢 « par défaut » : il reste ⚪.
- Un 🔴 **doit** s'accompagner de la **correction exacte** (la bonne valeur/syntaxe, avec sa source).
- Un 🟠 **doit** expliciter la **condition** manquante (quelle version, quel défaut réel, quel contexte).

---

## 8. Garde-fous anti-hallucination (récap opérationnel)

Synthèse actionnable — à appliquer à chaque affirmation, en complément des règles d'autorité de `sources-fiables.md`.

1. **Forcer `site:` vers les domaines confirmés ; bloquer la denylist.** Une requête comme `… site:iana.org` / `… site:man7.org` / `… site:cyber.gouv.fr` court-circuite les blogs SEO. Ne **jamais inventer d'URL** : domaines racines réels uniquement, requête `site:` quand l'URL profonde est incertaine.
2. **Distinguer outil et service sous-jacent.** Vérifier le fait sur la doc du **composant réellement responsable** :
    - **Certbot** (client, `certbot.eff.org`) ≠ **Let's Encrypt** (CA, `letsencrypt.org`).
    - **UFW** (frontend) ≠ **nftables/iptables** (moteur, `netfilter.org`).
    - **Portainer** (`docs.portainer.io`) ≠ **Docker** (`docs.docker.com`).
    - **Open WebUI** (`docs.openwebui.com`, port 8080) ≠ **Ollama** (`ollama.com`, port 11434).
    - **dig** (résolveur direct) ≠ **resolvectl** (systemd-resolved).
3. **Dater chaque vérification.** Indiquer la **date de consultation** (repère du jour). Les **rate limits Let's Encrypt**, **quotas/budgets cloud** et **API IA** changent — un fait juste hier peut être périmé.
4. **Se méfier des valeurs par défaut « évidentes ».** Les supposer est une source d'erreur silencieuse. Confirmer **chacune** à la source :
    - Préfixe **tmux** = `Ctrl-b` (le `Ctrl-a` est **screen**) → man `tmux.1`.
    - **Nginx** `proxy_read_timeout` = **60 s** par défaut → `nginx.org`.
    - **Ollama** : port **11434** → `ollama.com`.
    - **WireGuard** : **UDP 51820** → `wireguard.com`.
    - **NFSv4** : **2049** ; **iperf3** : **5201** → `iana.org` + doc projet.
5. **Recopier la formulation officielle**, jamais une paraphrase (cf. §2).
6. **Chasser la dépréciation** sur tout sujet versionné (cf. §5) : `version:` Compose, `gateway4` Netplan, `docker-compose` v1, directives OpenSSH renommées, doctrine mots de passe NIST.
7. **Confirmer ports sur IANA et flags dans la man page exacte** (cf. §3, §4) — les deux objets les plus hallucinés.
8. **Statuer ⚪ plutôt que combler.** Absence de source officielle ⇒ **⚪ Inconnu** et re-sourçage exigé. La discipline anti-hallucination prime toujours sur l'envie de « compléter ».

> Rappel de discipline : ce skill existe pour **ne pas propager** les hallucinations d'un brouillon LLM. Chaque raccourci (port supposé, paraphrase, RFC « de mémoire », valeur par défaut « évidente », Tier 3 érigé en preuve) réintroduit précisément le risque qu'on traque. En cas de doute : **source primaire datée, ou ⚪**.
