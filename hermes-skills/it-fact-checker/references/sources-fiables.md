# Sources fiables — Référentiel des sources autoritatives

> Référentiel des sources autoritatives. Consulter pour attribuer la bonne autorité à une affirmation et écarter les sources non fiables.

Ce fichier est appelé par l'étape **2 (classer par domaine & attribuer l'autorité)** et l'étape **3 (construire la recherche de preuve)** du workflow `it-fact-checker`. Il fixe la hiérarchie des sources (Tiers), la liste des domaines bannis (denylist) et les règles d'attribution d'autorité.

**Principe central** : un fait technique (port, flag, valeur par défaut, syntaxe, numéro de RFC) ne se valide que sur du **Tier 1** (normes/autorités) ou du **Tier 2** (doc officielle du projet/éditeur). Le **Tier 3** corrobore et contextualise ; il ne tranche jamais seul. Tout ce qui n'est ni Tier 1 ni Tier 2 est de la corroboration, et la **denylist** ne sert jamais de preuve. Si la seule justification est la mémoire du modèle ou une source Tier 3 → verdict **⚪ Inconnu**, jamais 🟢.

## Table des matières

1. [Tier 1 — Normalisation, état et autorités](#tier-1-normalisation-tat-et-autorits)
2. [Tier 2 — Documentation officielle éditeurs/projets](#tier-2-documentation-officielle-diteursprojets)
3. [Tier 3 — Experts, bases de menaces, vulgarisation FR](#tier-3-experts-bases-de-menaces-vulgarisation-fr)
4. [Denylist — sources interdites en preuve primaire](#denylist-sources-interdites-en-preuve-primaire)
5. [Règles d'autorité (synthèse normative)](#rgles-dautorit-synthse-normative)
6. [Rappel de discipline](#rappel-de-discipline)

---

## Tier 1 — Normalisation, état et autorités

**Source PRIMAIRE d'autorité** : protocoles, normes, valeurs officielles, posture de sécurité. À citer pour trancher un numéro de port, un numéro/statut de RFC, un algorithme déprécié, l'attribution d'une norme, le score/le périmètre d'une vulnérabilité.

| Source | Domaine racine | Périmètre |
|--------|----------------|-----------|
| IETF | `ietf.org` | Spécifications des protocoles Internet (RFC : TCP/IP, DNS, TLS, HTTP, SSH, IPsec). Autorité pour le statut normatif (Proposed/Draft/Internet Standard, Obsoleted by) et la sémantique MUST/SHOULD/MAY. |
| RFC Editor | `rfc-editor.org` | Texte canonique + **statut** de chaque RFC (errata, « Obsoleted by », « Updated by »). À utiliser pour citer le numéro EXACT d'une RFC et vérifier qu'elle n'est pas remplacée. |
| IANA | `iana.org` | Registre officiel des **numéros de ports** (well-known/registered), codes de protocole, paramètres DNS, plages d'adresses. **Autorité absolue** contre un port inventé par un LLM. |
| NIST | `nist.gov` | Standards cryptographiques (FIPS, SP 800-series). Réf. pour tailles de clés, algos dépréciés (SHA-1, RSA-1024, DES), mots de passe/MFA (SP 800-63B), TLS (SP 800-52), algos (SP 800-131A). |
| NVD | `nvd.nist.gov` | Base US officielle des vulnérabilités : **score CVSS**, versions affectées, statut d'un CVE. Tier 1 pour les FAITS de vulnérabilité (le descriptif narratif relève de cve.org/Tier 3). |
| ANSSI (actuel) | `cyber.gouv.fr` | Site officiel **actuel** de l'ANSSI (ex-ssi.gouv.fr). Guides de durcissement (OpenSSH, GNU/Linux, mots de passe, TLS), référentiels (SecNumCloud, PRIS). Autorité francophone de la posture sécurité. |
| ANSSI (ancien) | `ssi.gouv.fr` | Ancien domaine, encore référencé ; guides historiques. Vérifier la **redirection** vers cyber.gouv.fr et la **date** du guide (un guide ancien peut citer des algos désormais déconseillés). |
| CERT-FR | `cert.ssi.gouv.fr` | CSIRT gouvernemental français. Avis (`CERTFR-AAAA-AVI-NNNN`), alertes, bulletins. Autorité FR pour confirmer l'existence/le périmètre d'une vulnérabilité ou d'une menace active. |
| CNIL | `cnil.fr` | Autorité FR de protection des données. Réf. RGPD : durées de conservation, journalisation/logs licites, chiffrement côté conformité. Pertinent dès qu'un TP touche aux données personnelles. |
| W3C | `w3.org` | Standards du Web (CSS, ARIA, specs liées). Pertinent côté front et headers. **Piège** : la plupart des specs HTTP modernes sont à l'IETF et HTML au WHATWG — recouper, ne pas tout attribuer au W3C. |
| ISO | `iso.org` | Normes internationales (ISO/IEC 27001/27002, ISO 8601). Autorité pour la **dénomination/le périmètre** exact d'une norme. **Texte intégral payant** → vérifier le numéro ET l'année de révision, jamais le contenu paraphrasé. |
| IEEE SA | `standards.ieee.org` | Normes IEEE — notamment **802.1Q (VLAN tagging)** et 802.3 (Ethernet). À citer pour les VLAN : c'est de l'IEEE, **pas une RFC**. |

!!! warning "Pièges d'autorité Tier 1 (hallucinations LLM classiques)"
    - **VLAN 802.1Q = IEEE** (`standards.ieee.org`), **jamais** une RFC IETF.
    - **HTTP moderne = IETF** (`rfc-editor.org`), pas le W3C ; HTML = WHATWG.
    - **ISO = texte payant** : un LLM peut « citer » un contenu ISO inventé. Ne valider que le numéro + l'année.
    - **CVSS / versions affectées = NVD** (`nvd.nist.gov`) ; **description de référence = cve.org**. Ne pas confondre.

---

## Tier 2 — Documentation officielle éditeurs/projets

**Source PRIMAIRE d'implémentation** : syntaxe exacte, flags/options, valeurs par défaut, comportements, versions. À lire mot pour mot (copier la formulation officielle, ne pas paraphraser). La colonne « À vérifier en priorité » rappelle les zones de dépréciation où un LLM ressort souvent une syntaxe morte.

| Source | Domaine racine | Périmètre | À vérifier en priorité (dépréciation / piège) |
|--------|----------------|-----------|------------------------------------------------|
| Linux man-pages | `man7.org` | Rendu HTML officiel des man pages (espace utilisateur + glibc). Syntaxe, options, **section** exacte (1/5/8) : systemctl.1, rsync.1, mount.8, sudoers.5, cryptsetup.8, pam_pwquality.8. | Section correcte ; flags renommés entre versions ; `-a` rsync = `-rlptgoD`. |
| kernel.org | `kernel.org` | Doc du noyau Linux + projet man-pages (`kernel.org/doc/man-pages`). Comportements noyau, namespaces, cgroups, sysctl. | Paramètres sysctl par version de noyau. |
| Ubuntu / Canonical | `documentation.ubuntu.com` | Doc serveur Ubuntu officielle (Samba, NFS, LVM, cloud-init). **Cible du wiki = Ubuntu 24.04 LTS.** | Recouper la version LTS ; procédure LVM (lvextend → resize2fs/xfs_growfs). |
| Netplan (Canonical) | `netplan.io` | Syntaxe YAML Netplan, renderers (networkd/NetworkManager), VLAN, `netplan status`. | **`gateway4` DÉPRÉCIÉ** → `routes:` ; clés YAML / indentation hallucinées. |
| OpenSSH | `openssh.com` | Manuels `sshd_config`, `ssh_config` ; MFA via `AuthenticationMethods` ; algos KEX/cipher. | Directives obsolètes/renommées selon la version ; syntaxe MFA exacte. |
| netfilter / nftables | `netfilter.org` | Wiki nftables : tables/chaînes/règles, NAT (masquerade, dnat/snat), hooks et priorités. | **Ne pas mélanger syntaxe iptables et nftables** (`-A POSTROUTING` ≠ nft). |
| WireGuard | `wireguard.com` | Quickstart, conf `wg`/`wg-quick`. | Port **UDP 51820** par défaut (UDP-only) ; `PersistentKeepalive` (25 s **conseillé**, pas un défaut). |
| nginx | `nginx.org` | Directives `proxy_pass`, `proxy_set_header`, `upstream`, `ssl`. Reverse proxy. | Distinguer nginx.org (OSS) de NGINX Plus (commercial) ; timeouts (`proxy_read_timeout` 60 s par défaut) ; 502 ≠ 504. |
| Docker | `docs.docker.com` | Docker / Docker Compose : `compose.yaml`, réseaux, volumes, healthcheck, restart policies. | **Champ `version:` OBSOLÈTE** ; `docker compose` v2 ≠ `docker-compose` v1 (EOL) ; ordre `source:cible` des volumes. |
| Compose Specification | `compose-spec.io` | Spec ouverte du format Compose ; clés YAML modernes (`services`, `networks`, `depends_on` conditions). | Trancher entre v2/v3/spec actuelle ; le `version:` n'est plus requis. |
| Kubernetes | `kubernetes.io` | `kubectl`, manifests, terminologie. | **`apiVersion` change souvent** entre versions (API deprecations). |
| Microsoft Learn | `learn.microsoft.com` | Azure VM, ACI, `az` CLI, PowerShell ; noms de ressources, quotas. | Anciennes URL `docs.microsoft.com` redirigent ici ; vérifier que le cmdlet/verbe existe encore ; GA vs preview. |
| AWS Documentation | `docs.aws.amazon.com` | EC2, IAM, VPC, RDS, S3, AWS CLI, Budgets ; **Service Authorization Reference** (actions IAM). | **Chaque `Action` IAM** d'une policy JSON (ex. `s3:ListAllMyBuckets`, pas `s3:ListAllBuckets`) ; types d'instance ; limites de service. |
| Google Cloud | `cloud.google.com` | Cloud Run, `gcloud` CLI, régions. | `gcloud` **GA vs beta** ; flags exacts de `gcloud run deploy`. |
| HashiCorp Developer | `developer.hashicorp.com` | Terraform, Packer, Vagrant : HCL, arguments de provider, commandes. | Remplace `terraform.io`/`packer.io`/`vagrantup.com` (redirigent) ; Packer **HCL2** vs ancien JSON. |
| Terraform Registry | `registry.terraform.io` | Arguments EXACTS d'une ressource (ex. `aws_instance`), statut `deprecated`, **version du provider**. | Attributs inventés ; vérifier ressource par ressource avec la version du provider. |
| Proxmox VE | `pve.proxmox.com` | Wiki/doc PVE : `qm` (VM/KVM), `pct` (LXC), réseaux, API. | **`qm` ≠ `pct`** ; options CLI inventées. |
| Let's Encrypt | `letsencrypt.org` | CA ACME : **rate limits**, durée de validité (90 j), challenges ACME. | Rate limits **changent** → dater ; ne pas confondre avec le client (Certbot). |
| Certbot (EFF) | `certbot.eff.org`, `eff-certbot.readthedocs.io` | Client ACME **Certbot** (projet de l'EFF) : commandes `certbot`, plugins (nginx/standalone/webroot), renouvellement. | **Certbot (client) ≠ Let's Encrypt (CA)** ; citer la doc Certbot (`certbot.eff.org` / `eff-certbot.readthedocs.io`), **pas** la page d'accueil `eff.org` (qui est le site associatif de l'EFF, pas la doc de l'outil). |
| Ollama | `ollama.com` | API REST locale, **port 11434** par défaut, `ollama run/pull`, Modelfile, `/api/generate`, `/api/chat`. | Endpoints évolutifs (recouper `github.com/ollama/ollama`) ; tags `:7b`, `:q4_K_M` non garantis. |
| Open WebUI | `docs.openwebui.com` | Interface (Ollama / OpenAI-compatible) ; config, branchement Ollama, **port 8080** par défaut. | **Open WebUI ≠ Ollama** ; ne pas confondre les ports (8080 vs 11434). |
| n8n | `docs.n8n.io` | Nodes, expressions, mode webhook. | Noms de nodes/options de webhook **évolutifs** → dater la version. |
| Wireshark | `wireshark.org` | Doc + wiki : **filtres d'affichage** (display filters) vs **filtres de capture** (BPF). | Confusion fréquente display ↔ capture ; noms de champs de protocole exacts. |
| Postman | `learning.postman.com` | Collections, environnements, scripts pre-request/test. | Fonctionnalités **cloud/équipe payantes** présentées comme gratuites/locales. |
| VS Code | `code.visualstudio.com` | Remote-SSH : prérequis serveur, réglages. | Prérequis serveur (glibc, accès SSH) omis ; confusion avec Remote-Containers/WSL. |
| Git SCM | `git-scm.com` | Site officiel + Pro Book + man pages git : syntaxe, options, comportements par défaut. | `pull` = fetch+merge (sauf `--rebase`/config) ; branche par défaut `main` vs `master` selon version. |

!!! note "Docs hébergées ailleurs mais officielles"
    Certaines docs de projets vivent sur des hébergeurs tiers tout en étant **officielles** : `cloudinit.readthedocs.io` (cloud-init), `eff-certbot.readthedocs.io` (Certbot), le wiki/les releases du dépôt GitHub officiel d'un projet (ex. `github.com/ollama/ollama`, `github.com/tmux/tmux/wiki`). Elles restent du Tier 2 **si** elles sont le dépôt/le rendu officiel du projet — pas un miroir tiers (voir denylist).

---

## Tier 3 — Experts, bases de menaces, vulgarisation FR

**CORROBORATION et CONTEXTE seulement — jamais source primaire d'un fait technique.** Sert à pister une piste, comprendre une démarche, confirmer l'exploitation active d'une vulnérabilité. **Toujours recouper Tier 1/2 avant de publier un fait.**

| Source | Domaine racine | Périmètre | Usage autorisé |
|--------|----------------|-----------|----------------|
| CVE Program (MITRE) | `cve.org` | Catalogue officiel d'attribution des identifiants `CVE-AAAA-NNNNN` + description de référence. | Confirmer l'existence/le libellé d'un CVE ; **recouper le score avec NVD (Tier 1)**. |
| MITRE ATT&CK | `attack.mitre.org` | Tactiques/techniques adverses (ID `Txxxx`). | Nommer correctement une technique ; vérifier l'ID et qu'il n'est pas déprécié/renommé. |
| CISA | `cisa.gov` | Agence US cyber : Known Exploited Vulnerabilities (KEV), advisories. | Corroborer l'**exploitation active** ; complément US du CERT-FR. |
| Lynis (CISOfy) | `cisofy.com` | Doc de l'outil d'audit Lynis : `lynis audit system`, contrôles. | Sens d'un contrôle Lynis ; corroborer une recommandation de durcissement. |
| Nmap | `nmap.org` | Reference Guide (Gordon Lyon) : flags de scan, phases, types. | Vérifier un flag de scan ; **`-sS` SYN ≠ `-sT` connect**. Beaucoup d'options hallucinées. |
| CrowdSec | `docs.crowdsec.net` | Config, scénarios, bouncers. | Comprendre la logique CrowdSec ; **logique ≠ Fail2ban**. |
| Arch Wiki | `wiki.archlinux.org` | Réf. Linux experte de haute qualité (LUKS, AppArmor, systemd, GPG). | Détails/syntaxe ; **TOUJOURS recouper la man page Tier 2** avant de publier un fait. |
| GnuPG | `gnupg.org` | Projet officiel GnuPG : `gpg`, gestion de clés, algos. | Tier 2/3 selon usage ; vérifier la version (`gpg` vs `gpg2`, options renommées). |
| IT-Connect | `it-connect.fr` | Vulgarisation FR de qualité (Linux/Windows/réseau/sécurité). | **Contexte pédagogique uniquement.** JAMAIS pour un port/flag/valeur par défaut/norme. |
| Korben | `korben.info` | Vulgarisation FR (découverte d'outils, actualité). | **Repérage et contexte uniquement.** Aucune autorité sur la syntaxe ou les normes. |

!!! danger "Limite stricte du Tier 3"
    **IT-Connect, Korben et l'Arch Wiki ne tranchent jamais seuls un fait technique.** Ils ne doivent **jamais** apparaître dans la colonne « Source de confiance » d'un verdict 🟢 portant sur un port, un flag, une valeur par défaut ou une norme. Si c'est la seule source disponible → verdict **⚪ Inconnu** (à re-sourcer sur Tier 1/2).

---

## Denylist — sources interdites en preuve primaire

Ces sources **ne valident jamais** un fait dans un verdict. Bannir des requêtes (`-site:...` mentalement) ; ne pas les citer dans la colonne « Source de confiance ».

| Catégorie bannie | Exemples | Usage toléré (hors verdict) |
|------------------|----------|------------------------------|
| Blogs SEO génériques | `medium.com` / `dev.to` / `hashnode` (posts anonymes), articles « top 10 », « comment faire » génériques | Aucun pour un fait. Au mieux, pister une piste à reconfirmer en Tier 1/2. |
| Contenu généré/agrégé par IA | Sites de réponses automatiques, fermes de contenu sans auteur ni source primaire | Aucun. |
| Forums & Q&A | `stackoverflow.com`, `serverfault.com`, `superuser.com`, `reddit.com` | **Pister une réponse**, jamais citer un port/flag/valeur par défaut. |
| Wikis grand public | `wikipedia.org` comme source d'une commande ou d'un n° de RFC | Survol culturel ; le fait se vérifie sur IANA/RFC Editor/man page. |
| Docs miroir/non officielles | dépôts « unofficial-docs », tutoriels recopiant une doc sans la dater | Aucun ; remonter à la doc officielle du projet. |
| Pages périmées non datées | Toute page sans date ni n° de version sur un sujet versionné (Compose, Terraform, az/gcloud, Ollama, Netplan) | Aucun ; danger de dépréciation. |
| Vendeurs/affiliés | Page promotionnelle d'un produit présentée comme neutre | Aucun. |
| IT-Connect / Korben **en preuve primaire** | `it-connect.fr`, `korben.info` cités pour un port/flag/valeur par défaut/norme | Contexte/vulgarisation seulement (voir Tier 3). |
| Sorties d'autres LLM | Réponses de chatbots citées comme preuve | Aucun ; c'est précisément ce que le skill cherche à vérifier. |
| Snapshots de cache | Google cache, archive non datée substituée à la source vivante | Aucun ; consulter la source officielle vivante et dater. |

---

## Règles d'autorité (synthèse normative)

1. **Remonter à la source primaire.** Un fait (port, flag, valeur par défaut, syntaxe, n° de RFC) se valide sur **Tier 1** ou **Tier 2**. Le Tier 3 corrobore ; il ne tranche jamais seul.
2. **Attribuer la BONNE autorité.** VLAN **802.1Q = IEEE** (pas une RFC) ; **HTTP moderne = IETF** (pas le W3C) ; **CVSS/versions affectées = NVD** + **description = cve.org**. Une mauvaise attribution est une hallucination en soi.
3. **Confirmer chaque port sur `iana.org`.** Les ports sont la première chose qu'un LLM invente. Ne jamais valider un port « de mémoire ».
4. **Confirmer chaque flag/option dans la man page exacte** (`man7.org`, section 1/5/8) ou la doc CLI officielle ; copier la **formulation officielle**, pas une paraphrase.
5. **Vérifier le STATUT d'une RFC** sur `rfc-editor.org` : « Obsoleted by » / « Updated by » / errata. Citer une RFC remplacée comme courante est un piège classique.
6. **Recouper toute vulnérabilité** sur ≥ 2 sources : **NVD** (score CVSS) + **cve.org** (description) + **CERT-FR**/**CISA** (exploitation active). Ne jamais inventer un `CVE-AAAA-NNNNN` ni un score.
7. **Chasser la dépréciation** sur tout sujet versionné : Compose `version:`, Terraform HCL, `az`/`gcloud` GA vs beta, Netplan `gateway4`, directives OpenSSH, recommandations mots de passe NIST SP 800-63B. Une affirmation « vraie en 2018 » peut être 🔴 aujourd'hui.
8. **Vérifier version & OS.** Le wiki cible **Ubuntu 24.04 LTS**. Citer la version de la doc ET du logiciel concernés dans le verdict.
9. **Distinguer l'outil et le service sous-jacent.** **Certbot ≠ Let's Encrypt** ; **UFW ≠ nftables** ; **Portainer ≠ Docker** ; **Open WebUI ≠ Ollama**. Vérifier le fait sur la doc du composant **réellement responsable** (ex. une commande `certbot` se vérifie sur `certbot.eff.org`, un rate limit ACME sur `letsencrypt.org`).
10. **Tracer la source dans le verdict.** Chaque ligne porte une **référence précise (page + version + date de consultation)**, jamais un domaine racine seul. Sans source officielle → **⚪ Inconnu**, jamais comblé par la mémoire du modèle.

---

## Rappel de discipline

- **Ne jamais inventer d'URL.** Se limiter aux domaines racines réels listés ci-dessus + des **requêtes `site:` ciblées** (modèles dans `references/domaines.md`).
- Forcer la recherche vers le domaine officiel approprié : `site:iana.org`, `site:man7.org`, `site:rfc-editor.org`, `site:standards.ieee.org`, `site:docs.aws.amazon.com`, `site:cyber.gouv.fr`, etc. — pour court-circuiter les blogs SEO.
- La colonne « Source de confiance » d'un verdict **ne contient jamais** un domaine racine seul ni une source Tier 3 pour un fait technique.
- Horodater chaque vérification (date du jour comme repère de fraîcheur) : rate limits Let's Encrypt, quotas cloud et API IA changent.
