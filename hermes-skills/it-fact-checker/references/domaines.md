# Guide par domaine — sources prioritaires, requêtes `site:` et pièges d'hallucination

> Guide par domaine. Consulter pour les **sources prioritaires**, des **requêtes `site:` prêtes à l'emploi** et les **hallucinations IA récurrentes** selon le thème de l'affirmation.

Ce fichier est appelé par l'étape **2 (classer par domaine & attribuer l'autorité)** et l'étape **3 (construire la recherche de preuve)** du workflow `it-fact-checker`. Pour chaque affirmation : repérer son domaine ci-dessous, prendre la **source prioritaire** indiquée, lancer une **requête `site:`** type, puis vérifier le fait contre le texte officiel en gardant à l'esprit la liste des **pièges** propres à ce domaine.

**Discipline rappelée** (détaillée dans `sources-fiables.md`) : un fait (port, flag, valeur par défaut, syntaxe, norme) se valide uniquement sur **Tier 1** (normes/autorités) ou **Tier 2** (doc officielle projet/éditeur). Le **Tier 3** corrobore, ne tranche jamais seul. Sans source officielle → **⚪ Inconnu**, jamais comblé par la mémoire du modèle. **Ne jamais inventer d'URL** : domaines racines réels + requête `site:` quand l'URL profonde est incertaine.

## Table des matières

1. [Systèmes](#systèmes) — systemctl, LVM, permissions, rsync, Samba/NFS, tmux
2. [Réseaux](#réseaux) — Netplan, VLAN 802.1Q, DNS, WireGuard, nftables, Wireshark, mtr, iperf3, Nginx, SSH
3. [Cloud](#cloud) — AWS, Azure, GCP, cloud-init
4. [Cybersécurité](#cybersécurité) — sudo, PAM, SSH MFA, Fail2ban, CrowdSec, UFW, Certbot, Lynis, Nmap, LUKS, AppArmor, GPG
5. [IA](#ia) — Ollama, LLaVA, Open WebUI, CrewAI, Dify, AnythingLLM
6. [Automatisation](#automatisation) — Terraform, Packer, Vagrant, n8n, Proxmox, webhooks Bash
7. [Logiciels](#logiciels) — Docker/Compose, Git, VS Code Remote-SSH, Portainer, Postman
8. [Debug & Astuces](#debug--astuces) — table de rattachement vers les domaines ci-dessus

---

## Systèmes

**Domaine** : Linux/Ubuntu — `systemctl`, LVM, permissions, `rsync`, Samba/NFS, `tmux`.

### Sources prioritaires

| Priorité | Source | Domaine racine | Usage |
|----------|--------|----------------|-------|
| Tier 2 | Linux man-pages | `man7.org` | Syntaxe/flags exacts + **section** : `systemctl.1`, `rsync.1`, `mount.8`, `chmod.1`, `umask` (shell builtin / `bash.1`), composants LVM (`lvextend.8`, `resize2fs.8`, `xfs_growfs.8`), `exports.5`, `mount.nfs.8`. |
| Tier 2 | kernel.org | `kernel.org` | Comportements noyau, `sysctl`, namespaces, cgroups. |
| Tier 2 | Ubuntu / Canonical | `documentation.ubuntu.com` | Samba (`smb.conf`), NFS, LVM côté distro **Ubuntu 24.04 LTS** (cible du wiki). |
| Tier 3 | Arch Wiki | `wiki.archlinux.org` | Détails systemd/LVM de qualité — **à recouper** avec la man page avant publication. |
| Tier 2 | tmux (dépôt officiel) | `github.com/tmux/tmux/wiki` | Raccourcis, `tmux.conf`, guides (rendu officiel du projet). Pour le **préfixe par défaut** et les options, la référence canonique reste `tmux.1` sur `man7.org`. |

### Requêtes `site:` types

```text
systemctl enable vs start --now behavior site:man7.org
rsync -a archive option exact behavior --delete trailing slash site:man7.org
LVM lvextend then resize2fs procedure site:documentation.ubuntu.com
xfs_growfs cannot shrink site:man7.org
umask default 022 resulting permissions site:man7.org
chmod symbolic vs octal site:man7.org
Samba smb.conf valid users guest ok site:documentation.ubuntu.com
NFS exports sync async no_root_squash site:man7.org
NFSv4 port 2049 site:iana.org
tmux default prefix Ctrl-b site:man7.org
```

### Pièges / hallucinations IA récurrentes

!!! warning "Systèmes — pièges fréquents"
    - **`systemctl enable` ≠ `start`.** `enable` = activation **au boot** ; `start` = démarrage **immédiat** ; `--now` combine les deux. Un LLM décrit souvent `enable` comme démarrant le service tout de suite — **faux**.
    - **Flags `rsync` inventés/mal expliqués.** `-a` = `-rlptgoD` (archive) ; `--delete` est destructeur ; le **slash final** sur la source change le résultat (`src/` copie le contenu, `src` copie le dossier). Vérifier la formulation exacte dans `rsync.1`.
    - **`umask` confondu avec `chmod`.** `umask 022` ne « met » pas `644` : c'est un **masque soustractif** (fichiers `666 & ~022 = 644`, répertoires `777 & ~022 = 755`). Ne pas présenter une valeur d'umask comme un mode `chmod`.
    - **Ordre LVM inversé.** L'agrandissement va `lvextend` **puis** `resize2fs` (ext4) ou `xfs_growfs` (XFS) — souvent donné dans l'ordre inverse. **XFS ne se réduit pas** : toute « réduction XFS » est une hallucination.
    - **NFS/Samba — ports & options.** NFSv4 = **2049 uniquement** (confirmer sur `iana.org`) ; Samba n'est pas « un seul port ». `no_root_squash` est souvent mal compris (il **désactive** l'écrasement du root distant).
    - **Préfixe `tmux`.** Le préfixe par défaut est **`Ctrl-b`**, pas `Ctrl-a` (ça c'est `screen`, ou un `tmux.conf` personnalisé).

---

## Réseaux

**Domaine** : Netplan, VLAN 802.1Q, DNS (`dig`/`resolvectl`), WireGuard, nftables/NAT, Wireshark, `mtr`, `iperf3`, reverse proxy Nginx, SSH.

### Sources prioritaires

| Priorité | Source | Domaine racine | Usage |
|----------|--------|----------------|-------|
| Tier 1 | IETF / RFC Editor | `ietf.org`, `rfc-editor.org` | RFC (DNS, TLS, SSH, IPsec) : numéro, titre, **statut** Obsoleted/Updated. |
| Tier 1 | IANA | `iana.org` | **Registre officiel des numéros de ports** — autorité absolue contre un port inventé. |
| Tier 1 | IEEE SA | `standards.ieee.org` | **802.1Q (VLAN tagging)**, 802.3 (Ethernet) — pas une RFC. |
| Tier 2 | Netplan | `netplan.io` | Syntaxe YAML, renderers, VLAN, `netplan status`. |
| Tier 2 | netfilter / nftables | `netfilter.org` | Syntaxe nftables, NAT (`masquerade`, `dnat`/`snat`), hooks et priorités. |
| Tier 2 | WireGuard | `wireguard.com` | Conf `wg`/`wg-quick`, port UDP par défaut, `PersistentKeepalive`, `AllowedIPs`. |
| Tier 2 | nginx | `nginx.org` | Directives `proxy_pass`, `proxy_set_header`, `upstream`, timeouts. |
| Tier 2 | OpenSSH | `openssh.com` | `sshd_config`/`ssh_config`, `AuthenticationMethods`, algos KEX/cipher. |
| Tier 2 | Wireshark | `wireshark.org` | Filtres d'affichage vs filtres de capture, noms de champs. |
| Tier 2 | man-pages | `man7.org` | `dig.1`, `resolvectl.1` (systemd), `mtr.8`, `iperf3.1`, `ip.8`. |

### Requêtes `site:` types

```text
802.1Q VLAN tag standard site:standards.ieee.org
netplan vlans id link 802.1Q configuration site:netplan.io
netplan gateway4 deprecated routes site:netplan.io
wireguard default listen port PersistentKeepalive site:wireguard.com
nftables masquerade nat postrouting chain priority site:netfilter.org
nginx proxy_pass proxy_set_header Host Upgrade websocket site:nginx.org
nginx proxy_read_timeout default 60s 504 site:nginx.org
dig +short +trace usage site:man7.org
resolvectl query systemd-resolved site:man7.org
iperf3 -c -s default port 5201 bandwidth site:man7.org
service names and port numbers registry site:iana.org
```

### Pièges / hallucinations IA récurrentes

!!! warning "Réseaux — pièges fréquents"
    - **VLAN 802.1Q mal attribué.** C'est une norme **IEEE** (`standards.ieee.org`), **jamais** une RFC IETF. L'attribution à une RFC est une hallucination d'autorité classique.
    - **Ports inventés.** WireGuard est **UDP 51820** par défaut (et **UDP-only** — pas de TCP) ; `iperf3` écoute sur **5201** ; NFSv4 sur 2049. Confirmer **chaque** port sur `iana.org`, jamais de mémoire.
    - **`PersistentKeepalive`.** 25 s est une valeur **conseillée** (NAT/pare-feu), **pas un défaut** : par défaut il est désactivé (`0`). Ne pas présenter 25 s comme la valeur par défaut.
    - **Mélange iptables / nftables.** Une règle nft ne s'écrit pas avec la syntaxe iptables (`-A POSTROUTING …`). Vérifier table/chaîne/hook/priorité dans le wiki `netfilter.org`.
    - **Clés Netplan hallucinées.** Indentation/renderer fantaisistes ; surtout **`gateway4` est DÉPRÉCIÉ** au profit de `routes:` (route par défaut). Une conf « vraie en 2019 » est aujourd'hui 🔴/🟠.
    - **DNS : `dig` ≠ `resolvectl`.** `dig` interroge un résolveur **directement** ; `resolvectl` passe par **systemd-resolved**. `+short`, `+trace` souvent mal employés (`+trace` part de la racine).
    - **Reverse proxy Nginx.** Oubli de `proxy_set_header Host $host` et des en-têtes `Upgrade`/`Connection` pour le WebSocket. **502 ≠ 504** : **502 Bad Gateway** = upstream invalide/refus/réponse illisible ; **504 Gateway Timeout** = upstream trop lent (`proxy_read_timeout`, 60 s par défaut).
    - **SSH.** Directives `sshd_config` obsolètes ou mal nommées ; MFA via `AuthenticationMethods` (syntaxe `publickey,keyboard-interactive`) souvent mal écrite. Vérifier selon la version d'OpenSSH.
    - **Wireshark.** Confusion **filtre d'affichage** (`tcp.port == 443`, syntaxe Wireshark) vs **filtre de capture** (BPF, `tcp port 443`) — ce ne sont pas les mêmes langages.

---

## Cloud

**Domaine** : AWS (EC2/IAM/VPC/RDS/S3/CLI/Budgets), Azure (VM/ACI), GCP (Cloud Run), cloud-init.

### Sources prioritaires

| Priorité | Source | Domaine racine | Usage |
|----------|--------|----------------|-------|
| Tier 2 | AWS Documentation | `docs.aws.amazon.com` | AWS CLI, **actions IAM** (Service Authorization Reference), types d'instance, limites de service. |
| Tier 2 | Microsoft Learn | `learn.microsoft.com` | `az` CLI, Azure VM/ACI, noms de ressources, quotas. |
| Tier 2 | Google Cloud | `cloud.google.com` | `gcloud` CLI, Cloud Run, régions, flags. |
| Tier 2 | cloud-init (officiel) | `cloudinit.readthedocs.io`, `documentation.ubuntu.com` | Modules, clés YAML, en-tête `#cloud-config`. |

### Requêtes `site:` types

```text
IAM action s3 ListAllMyBuckets exact name site:docs.aws.amazon.com
aws ec2 run-instances cli options instance-type site:docs.aws.amazon.com
S3 bucket policy vs ACL difference site:docs.aws.amazon.com
aws budgets create-budget cli site:docs.aws.amazon.com
az container create ACI parameters site:learn.microsoft.com
az vm create image size site:learn.microsoft.com
gcloud run deploy flags region site:cloud.google.com
gcloud beta vs GA command site:cloud.google.com
cloud-init runcmd write_files module syntax site:cloudinit.readthedocs.io
cloud-config header required first line site:cloudinit.readthedocs.io
```

### Pièges / hallucinations IA récurrentes

!!! warning "Cloud — pièges fréquents"
    - **Actions IAM inventées.** Dans une policy JSON, un LLM fabrique des actions plausibles : `s3:ListAllBuckets` au lieu de **`s3:ListAllMyBuckets`**, ou un `ec2:`/`rds:` qui n'existe pas. Vérifier **CHAQUE** `Action` dans la **Service Authorization Reference** AWS — c'est l'une des hallucinations les plus fréquentes.
    - **Verbes/flags `az`/`gcloud` hallucinés.** Sous-commandes ou options inexistantes, ou mélange **GA / beta / preview** (`gcloud beta run …` vs `gcloud run …`). Confirmer que le verbe existe encore et dans quel canal.
    - **Types d'instance / SKU / régions inexistants.** Un nom d'instance EC2, une taille de VM Azure ou une région GCP plausibles mais faux. Les croiser à la doc officielle.
    - **cloud-init.** Modules et clés YAML inventés ; surtout l'**en-tête `#cloud-config`** en **première ligne** est obligatoire pour un fichier cloud-config (sinon c'est interprété autrement) — souvent omis ou confondu avec un script shell (`#!/bin/bash`).
    - **S3 régional vs global.** Le **nom de bucket** est globalement unique mais le bucket est **régional** ; un LLM les présente parfois comme « globaux ». Distinguer aussi **bucket policy** (recommandé) et **ACL** (legacy).
    - **Budgets / quotas / seuils datés.** Valeurs par défaut, quotas et seuils **changent** : toujours **dater** la vérification et citer la page, jamais affirmer un quota de mémoire.

---

## Cybersécurité

**Domaine** : `sudo`/`visudo`, `pam_pwquality`, SSH MFA, Fail2ban, CrowdSec, UFW, Certbot/Let's Encrypt, Lynis, Nmap, LUKS, AppArmor, GPG.

### Sources prioritaires

| Priorité | Source | Domaine racine | Usage |
|----------|--------|----------------|-------|
| Tier 1 | ANSSI | `cyber.gouv.fr` (ex-`ssi.gouv.fr`) | Guides de durcissement FR : OpenSSH, GNU/Linux, mots de passe, TLS. |
| Tier 1 | CERT-FR | `cert.ssi.gouv.fr` | Avis/alertes (`CERTFR-AAAA-AVI-NNNN`) — existence/périmètre d'une vulnérabilité. |
| Tier 1 | NIST | `nist.gov` | SP 800-63B (mots de passe/MFA), SP 800-131A (algos), SP 800-52 (TLS). |
| Tier 1 | NVD | `nvd.nist.gov` | Score **CVSS**, versions affectées d'un CVE. |
| Tier 2 | man-pages | `man7.org` | `sudoers.5`, `pam_pwquality` / `pwquality.conf.5`, `cryptsetup.8` (LUKS), outils `apparmor`. |
| Tier 3 | Nmap | `nmap.org` | Reference Guide : types/flags de scan. |
| Tier 3 | Lynis (CISOfy) | `cisofy.com` | Contrôles d'audit `lynis audit system`. |
| Tier 3 | CrowdSec | `docs.crowdsec.net` | Scénarios, bouncers (logique ≠ Fail2ban). |
| Tier 2 | Let's Encrypt + Certbot | `letsencrypt.org`, `certbot.eff.org` | CA (rate limits, validité) **vs** client Certbot (commandes/plugins). Doc Certbot = `certbot.eff.org` (pas la page d'accueil `eff.org`). |
| Tier 3 | CVE / ATT&CK | `cve.org`, `attack.mitre.org` | Description de CVE, ID de technique — recouper NVD. |
| Tier 3 | GnuPG, Arch Wiki | `gnupg.org`, `wiki.archlinux.org` | `gpg`, LUKS, AppArmor — recouper la man page. |

### Requêtes `site:` types

```text
recommandations durcissement OpenSSH site:cyber.gouv.fr
recommandations mots de passe site:cyber.gouv.fr
NIST SP 800-63B password length rotation memorized secret site:nist.gov
NIST SP 800-131A deprecated SHA-1 RSA-1024 site:nist.gov
pam_pwquality minlen dcredit ucredit options site:man7.org
sudoers NOPASSWD syntax visudo site:man7.org
cryptsetup luksFormat luksOpen options site:man7.org
nmap -sS SYN scan vs -sT connect scan site:nmap.org
Lets Encrypt rate limits certificates per registered domain site:letsencrypt.org
certbot --nginx renew plugins site:certbot.eff.org
CVE-2024-XXXXX CVSS score affected versions site:nvd.nist.gov
```

### Pièges / hallucinations IA récurrentes

!!! danger "Cybersécurité — pièges fréquents (impact sécurité réel)"
    - **Recommandations mots de passe périmées.** **NIST SP 800-63B** déconseille la **rotation périodique forcée** et la **complexité imposée** (classes de caractères) ; il privilégie la **longueur** et le filtrage par dictionnaire. Un LLM ressort souvent l'ancienne doctrine (90 jours, majuscule + chiffre + spécial) — c'est aujourd'hui 🔴/🟠. Recouper aussi `cyber.gouv.fr`.
    - **Algorithmes dépréciés présentés comme sûrs.** **SHA-1, RSA-1024, DES/3DES** sont déconseillés (NIST SP 800-131A). Vérifier les tailles de clés et l'algo avant de valider une commande `gpg`/`cryptsetup`/TLS.
    - **Syntaxe `sudoers` dangereuse/fausse.** Toujours éditer via **`visudo`** (validation de syntaxe) ; placement des règles (la dernière qui matche gagne) ; `NOPASSWD` mal posé ouvre une faille. Vérifier dans `sudoers.5`.
    - **Rate limits Let's Encrypt hallucinés.** Nombre de certificats par période, fenêtres, validité (**90 jours**) **changent** : re-vérifier la page **datée** sur `letsencrypt.org`, ne jamais citer un chiffre de mémoire.
    - **UFW ≠ nftables ≠ iptables.** **UFW** est un **frontend** ; le moteur sous-jacent (nftables/iptables) est distinct. Des « règles UFW » à la syntaxe iptables sont inventées. Vérifier le fait sur le composant réellement responsable.
    - **Nmap : type de scan mal décrit.** **`-sS`** = SYN (half-open) **≠ `-sT`** = connect (TCP complet) ; beaucoup de flags sont hallucinés. Vérifier dans le Reference Guide `nmap.org`.
    - **AppArmor confondu avec SELinux.** Sous **Ubuntu**, c'est **AppArmor** (profils, `aa-status`, `aa-enforce`, `aa-complain`), pas SELinux (`setenforce`, `getenforce`, contextes). Ne pas mélanger les deux jeux de commandes.
    - **CVE/CVSS inventés.** Ne **jamais** fabriquer un `CVE-AAAA-NNNNN`, un score CVSS ou une plage de versions affectées. Recouper **NVD** (score/versions) + **cve.org** (description) + **CERT-FR**/**CISA** (exploitation active). Sans recoupement → **⚪**.

---

## IA

**Domaine** : Ollama, LLaVA, Open WebUI, CrewAI, Dify, RAG AnythingLLM.

### Sources prioritaires

| Priorité | Source | Domaine racine | Usage |
|----------|--------|----------------|-------|
| Tier 2 | Ollama | `ollama.com` + `github.com/ollama/ollama` | API REST locale, **port 11434**, `ollama run/pull`, Modelfile, endpoints. |
| Tier 2 | Open WebUI | `docs.openwebui.com` | Config, branchement Ollama, **port applicatif 8080** (souvent publié sur l'hôte en `-p 3000:8080`). |
| Tier 2 (communautaire) | CrewAI | `docs.crewai.com` | Agents, Tasks, Crew — **dater la version** (API évolutive). |
| Tier 2 (communautaire) | Dify | `docs.dify.ai` | Workflows, knowledge base. |
| Tier 2 (communautaire) | AnythingLLM | `docs.anythingllm.com` | RAG, embeddings, providers. |
| Tier 2 | Dépôts GitHub officiels | `github.com/<projet>` | README/releases = vérité pour les API qui changent vite. |

### Requêtes `site:` types

```text
ollama default port 11434 API endpoint site:ollama.com
ollama API /api/generate /api/chat request body site:ollama.com
ollama Modelfile FROM PARAMETER SYSTEM TEMPLATE directives site:github.com/ollama/ollama
Open WebUI default port 8080 docker run -p 3000:8080 site:docs.openwebui.com
CrewAI Agent Task Crew process definition site:docs.crewai.com
Dify workflow knowledge base retrieval site:docs.dify.ai
AnythingLLM RAG embedding provider configuration site:docs.anythingllm.com
```

### Pièges / hallucinations IA récurrentes

!!! warning "IA — pièges fréquents"
    - **Port Ollama.** Par défaut **11434**. Ne pas le confondre avec **Open WebUI**, dont l'application écoute sur **8080** (et qui est souvent publié sur l'hôte via `-p 3000:8080`, d'où un accès en `:3000`). Bien distinguer **port applicatif** et **port publié sur l'hôte**, et **Open WebUI ≠ Ollama**.
    - **Endpoints d'API inventés/périmés.** Ollama expose notamment **`/api/generate`** et **`/api/chat`** ; ces frameworks bougent **vite** — recouper la **version exacte** sur la doc / le dépôt GitHub officiel.
    - **Directives Modelfile fabriquées.** Réelles : **`FROM`**, **`PARAMETER`**, **`SYSTEM`**, **`TEMPLATE`** (et `ADAPTER`, `LICENSE`, `MESSAGE`). D'autres sont souvent inventées. Vérifier la liste à la source.
    - **Tags de modèle / quantization non garantis.** `:7b`, `:q4_K_M`, etc. présentés comme certains alors qu'ils dépendent du modèle publié. Vérifier que le tag existe réellement dans le registre du modèle.
    - **Docs communautaires ≠ Tier 1.** CrewAI/Dify/AnythingLLM sont des docs **projet/communautaires** : utiles comme source d'implémentation, mais **dater la version** car l'API change de release en release. Ne pas les traiter comme une norme.
    - **Capacités mal attribuées.** **LLaVA = vision/multimodal** ; ne pas prêter de capacités multimodales à un modèle texte-seul (ni l'inverse). Vérifier la fiche du modèle.

---

## Automatisation

**Domaine** : Terraform, Packer, Vagrant, n8n, Proxmox, webhooks Bash.

### Sources prioritaires

| Priorité | Source | Domaine racine | Usage |
|----------|--------|----------------|-------|
| Tier 2 | HashiCorp Developer | `developer.hashicorp.com` | Terraform/Packer/Vagrant : HCL, CLI, cycle de vie. Remplace `terraform.io`/`packer.io`/`vagrantup.com`. |
| Tier 2 | Terraform Registry | `registry.terraform.io` | **Arguments EXACTS** d'une ressource (ex. `aws_instance`), statut `deprecated`, **version du provider**. |
| Tier 2 | n8n | `docs.n8n.io` | Nodes, expressions, mode webhook. |
| Tier 2 | Proxmox VE | `pve.proxmox.com` | `qm` (VM/KVM), `pct` (LXC), réseaux, API. |
| Tier 2 | man-pages | `man7.org` | `curl.1` (flags des webhooks Bash), scripting. |

### Requêtes `site:` types

```text
aws_instance argument reference instance_type ami site:registry.terraform.io
terraform required_providers provider block syntax site:developer.hashicorp.com
terraform resource lifecycle plan apply site:developer.hashicorp.com
packer hcl2 source build provisioner site:developer.hashicorp.com
vagrant Vagrantfile box provider config site:developer.hashicorp.com
n8n webhook node respond mode HTTP method site:docs.n8n.io
proxmox qm create vm cli site:pve.proxmox.com
proxmox pct create lxc container site:pve.proxmox.com
curl -d --data-binary -H Content-Type POST site:man7.org
```

### Pièges / hallucinations IA récurrentes

!!! warning "Automatisation — pièges fréquents"
    - **Arguments de ressource Terraform inventés.** Un attribut plausible mais inexistant (ou renommé/déprécié) sur une ressource. Vérifier **ressource par ressource** dans le **Registry**, en notant la **version du provider** (un argument valide en `v4` peut disparaître en `v5`).
    - **HCL obsolète.** Ancienne syntaxe d'interpolation `"${ … }"` employée hors contexte, ou `provider "aws" {}` seul là où il faut un bloc **`required_providers`** (Terraform ≥ 0.13). Vérifier la version Terraform ciblée.
    - **Packer : JSON vs HCL2.** L'ancienne syntaxe **JSON** est présentée comme actuelle alors que **HCL2** est le standard ; noms de **provisioners**/sources faux. Confirmer sur `developer.hashicorp.com`.
    - **n8n : nodes/options évolutifs.** Noms de nodes et options de webhook changent — **dater la version** et vérifier dans `docs.n8n.io`.
    - **Proxmox : `qm` ≠ `pct`.** `qm` gère les **VM (KVM)**, `pct` gère les **conteneurs LXC**. Les confondre, ou inventer des options CLI, est fréquent. Vérifier sur `pve.proxmox.com`.
    - **Webhooks Bash : `curl` mal employé.** `-d`/`--data` vs `--data-binary` (le premier peut transformer les données), **en-tête `Content-Type` oublié** (`-H 'Content-Type: application/json'`), méthode implicite (`-d` force déjà `POST`). Vérifier dans `curl.1`.

---

## Logiciels

**Domaine** : Docker/Docker Compose, Git, VS Code Remote-SSH, Portainer, Postman.

### Sources prioritaires

| Priorité | Source | Domaine racine | Usage |
|----------|--------|----------------|-------|
| Tier 2 | Docker | `docs.docker.com` | Docker / Docker Compose : `compose.yaml`, réseaux, volumes, healthcheck, restart. |
| Tier 2 | Compose Specification | `compose-spec.io` | Clés YAML Compose modernes ; trancher v2/v3/spec actuelle. |
| Tier 2 | Git SCM | `git-scm.com` | Commandes git, Pro Book, man pages, comportements par défaut. |
| Tier 2 | VS Code | `code.visualstudio.com` | Remote-SSH : prérequis serveur, réglages. |
| Tier 2 | Portainer | `docs.portainer.io` | Stacks, déploiement, **CE vs BE**. |
| Tier 2 | Postman | `learning.postman.com` | Collections, environnements, scripts pre-request/test. |

### Requêtes `site:` types

```text
docker compose version field obsolete top-level site:compose-spec.io
docker compose healthcheck depends_on condition site:compose-spec.io
docker run -v bind mount vs named volume source target order site:docs.docker.com
docker compose v2 plugin vs docker-compose v1 site:docs.docker.com
git pull fetch merge default rebase site:git-scm.com
git default branch main master init.defaultBranch site:git-scm.com
VS Code Remote-SSH requirements server prerequisites site:code.visualstudio.com
Portainer stack deploy compose CE vs Business site:docs.portainer.io
Postman pre-request script environment variable cloud vs local site:learning.postman.com
```

### Pièges / hallucinations IA récurrentes

!!! warning "Logiciels — pièges fréquents"
    - **Champ `version:` Compose présenté comme requis.** Il est **OBSOLÈTE** dans la **Compose Specification** actuelle (toléré mais ignoré, et déconseillé). Une affirmation « il faut mettre `version: '3.8'` en haut » est aujourd'hui 🔴/🟠 — hallucination très fréquente.
    - **`docker-compose` (v1) vs `docker compose` (v2).** Le binaire à tiret **v1 est EOL** ; la commande actuelle est le **plugin v2** (`docker compose`, sans tiret). Des commandes v1 données comme actuelles sont datées.
    - **Volumes : bind mount vs volume nommé + ordre.** `-v /host:/conteneur` (bind mount) ≠ `-v monvolume:/conteneur` (volume nommé) ; l'ordre est **`source:cible`** — souvent inversé.
    - **Git : comportement par défaut faux.** `git pull` = **fetch + merge** sauf si `--rebase`/`pull.rebase` est configuré ; la **branche par défaut** est `main` ou `master` **selon la version/config** (`init.defaultBranch`) — ne pas affirmer l'un sans vérifier.
    - **VS Code Remote-SSH : prérequis omis.** Prérequis côté **serveur** (accès SSH, glibc compatible) souvent oubliés ; confusion avec **Remote-Containers** / **WSL** (extensions distinctes).
    - **Portainer : CE vs BE.** Des fonctionnalités de **Business Edition** (payantes) présentées comme gratuites. Et **Portainer ≠ Docker** : c'est une **couche au-dessus** — vérifier un fait Docker sur `docs.docker.com`, pas sur Portainer.
    - **Postman : cloud vs local.** Fonctionnalités **cloud/équipe** (payantes) présentées comme gratuites/locales. Distinguer dans `learning.postman.com`.

---

## Debug & Astuces

Ces deux domaines n'ont **pas de source dédiée** : ils se vérifient via les sources des domaines ci-dessus.

| Sujet | Domaine de rattachement | Source à utiliser |
|-------|--------------------------|-------------------|
| `tcpdump` (capture, filtres BPF) | Réseaux | `man7.org` (`tcpdump.1`), `wireshark.org` (BPF) ; **filtre de capture BPF ≠ filtre d'affichage Wireshark**. |
| `pdb` (debugger Python) | Logiciels / Systèmes | Doc Python officielle (`docs.python.org`) ; vérifier les commandes (`b`, `n`, `s`, `c`, `p`). |
| `htop` / `free` (mémoire) | Systèmes | `man7.org` (`free.1`, `htop.1`) ; **`free` : `available` ≠ `free`**, le cache n'est pas « perdu ». |
| Debug conteneurs Docker (`logs`, `exec`, `inspect`) | Logiciels | `docs.docker.com`. |
| Erreurs **502 / 504** | Réseaux | `nginx.org` ; **502 Bad Gateway** (upstream invalide/refus) **≠ 504 Gateway Timeout** (upstream trop lent). |
| `awk`, `jq`, `fzf`, alias | Astuces → Systèmes | `man7.org` (`awk.1`), doc officielle `jq`/`fzf` (dépôts officiels) ; `alias` = builtin shell (`bash.1`). |

!!! note "Pas de référence imbriquée"
    Debug et Astuces ne renvoient vers **aucun autre fichier** `references/` : ils réutilisent directement les sources Systèmes / Réseaux / Logiciels listées plus haut. Pour la hiérarchie complète des Tiers et la denylist, voir `references/sources-fiables.md` ; pour la méthode d'atomisation et de preuve, voir `references/methodologie.md`.
