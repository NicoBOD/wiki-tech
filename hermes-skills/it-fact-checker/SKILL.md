---
name: it-fact-checker
description: Vérifie la véracité d'affirmations, de TP et de tutoriels IT francophones avant publication et traque les hallucinations d'IA dans les brouillons générés par LLM : ports inventés, flags inexistants ou dépréciés, syntaxe de commande fausse, acronymes erronés, valeurs par défaut inexactes, RFC ou normes mal attribuées. À utiliser pour relire un brouillon rédigé ou reformulé par un LLM, contrôler un tutoriel pas-à-pas (commandes, ports, chemins, valeurs par défaut), ou lever un doute ponctuel sur un port, un flag, une RFC ou un CVE. Couvre Systèmes, Réseaux, Cloud, Cybersécurité, IA, Automatisation, Logiciels et Debug, cible Ubuntu 24.04 LTS par défaut. Remonte exclusivement à des sources officielles via des recherches site: ciblées et rend un verdict actionnable par affirmation (🟢 Vrai, 🟠 Nuancé, 🔴 Faux, ⚪ Inconnu) avec source précise et datée. Produit un rapport en français au style MkDocs Material du wiki (admonitions !!!, emojis de statut).
---

# IT Fact-Checker — vérification anti-hallucination pour le wiki

Ce skill confronte des affirmations techniques IT à des sources **officielles** et rend un **verdict actionnable** avant publication sur le wiki-tech. Il est conçu pour traquer les hallucinations d'IA dans les brouillons générés par LLM.

## Quand utiliser ce skill

Déclencheurs principaux :

- **Relecture d'un brouillon généré ou reformulé par un LLM** avant mise en ligne.
- **Contrôle d'un TP / tutoriel pas-à-pas** (commandes, ports, chemins, valeurs par défaut).
- **Doute ponctuel** sur un port, un flag, un chemin, une valeur par défaut, une RFC, un CVE.

**Périmètre** : Systèmes, Réseaux, Cloud, Cybersécurité, IA, Automatisation, Logiciels, Debug, Astuces.
**Cible OS par défaut** : Ubuntu 24.04 LTS (sauf indication contraire de l'auteur).

## Principe directeur — les 3 règles d'or

1. **Source PRIMAIRE obligatoire.** Un fait technique (port, flag, valeur par défaut, syntaxe) se valide sur **Tier 1** (normes/autorités) ou **Tier 2** (doc officielle projet/éditeur). Jamais sur la mémoire du modèle, jamais sur un blog.
2. **Vérifier VERSION et DÉPRÉCIATION.** Une vérité datée peut être fausse aujourd'hui (ex. `version:` dans compose.yaml, `gateway4` Netplan, rotation forcée des mots de passe). Citer la version de la doc et du logiciel.
3. **Doute non levé → ⚪ Inconnu.** Si aucune source officielle ne tranche, statuer ⚪ — **ne jamais combler par une supposition**.

## Workflow de vérification

1. **Périmètre & date.** Confirmer que la demande relève du fact-check IT. Noter la date du jour (repère de fraîcheur, ex. `2026-06-29`) et l'OS/version cible si connu.
2. **Atomiser.** Découper le texte en affirmations **atomiques et vérifiables** (une donnée factuelle par ligne), numérotées `A1, A2, …`. Cibler les éléments hallucinables (ports, flags, chemins, valeurs par défaut, actions IAM, clés YAML, directives, acronymes, RFC, CVE). Ignorer l'opinion et le style.
3. **Classer & attribuer l'autorité.** Pour chaque affirmation : domaine + autorité compétente. Vérifier l'attribution (ex. VLAN 802.1Q = **IEEE**, pas une RFC IETF ; HTTP moderne = IETF, pas W3C ; CVSS = NVD + cve.org). Distinguer outil et service (Certbot ≠ Let's Encrypt, UFW ≠ nftables, Portainer ≠ Docker, Open WebUI ≠ Ollama).
4. **Construire la requête.** Formuler une requête `site:` ciblée sur le domaine officiel (ex. `wireguard default listen port site:wireguard.com`, `IAM action s3 list exact name site:docs.aws.amazon.com`). Forcer Tier 1/2 comme preuve primaire ; Tier 3 seulement pour corroborer. Bannir la denylist (blogs SEO, forums/Q&A en source primaire, contenu IA, pages non datées sur sujets versionnés).
5. **Vérifier à la source primaire.** Confronter au texte officiel : ports sur **iana.org** ; flags dans la **man page exacte** (man7.org, section 1/5/8) ou la doc CLI, en **copiant la formulation officielle** ; RFC sur **rfc-editor.org** (numéro, titre, statut Obsoleted/Updated) ; CVE en recoupant NVD + cve.org. **Chasser la dépréciation.**
6. **Statuer par affirmation** selon le barème ci-dessous. Règle anti-hallucination : si la seule justification est la mémoire du modèle ou une source Tier 3, le verdict est **⚪**, jamais 🟢.
7. **Rédiger le rapport** à partir de `assets/modele-rapport.md` : tableau de verdicts → synthèse → recommandations → verdict de publication.

## Barème de verdict

| Statut | Définition |
|--------|------------|
| 🟢 **Vrai** | Confirmé tel quel par la source primaire (Tier 1/2). |
| 🟠 **Nuancé** | Exact **sous condition** : version, OS, contexte, valeur conseillée ≠ valeur par défaut. |
| 🔴 **Faux** | Contredit par la source primaire. **Fournir la correction exacte.** |
| ⚪ **Inconnu** | Aucune source officielle trouvée. **Ne pas combler par la mémoire du modèle.** |

> Règle anti-hallucination : **Tier 3 seul ou mémoire du modèle ⇒ ⚪**, jamais 🟢.

## Format de sortie

Utiliser le gabarit **`assets/modele-rapport.md`** pour produire le tableau de verdicts, la synthèse et les recommandations, au style Markdown du wiki (admonitions `!!!`, emojis de statut). Chaque ligne du tableau porte une **source précise** (page + version + date de consultation), jamais un domaine racine vague, jamais une source Tier 3 pour un fait technique. Conclure par un verdict de publication : *publiable* / *publiable après corrections* / *à ne pas publier en l'état*.

## Fichiers liés (progressive disclosure)

- **`references/sources-fiables.md`** — Consulter pour **choisir la bonne autorité** par Tier et appliquer l'allowlist / denylist.
- **`references/methodologie.md`** — Consulter pour **atomiser**, fixer le standard de preuve, **vérifier la syntaxe d'une commande** et gérer versions / dépréciation.
- **`references/domaines.md`** — Consulter pour les **sources prioritaires, requêtes `site:` types et pièges d'hallucination** propres à un domaine (Systèmes, Réseaux, Cloud, Sécurité, IA, Automatisation, Logiciels).
- **`assets/modele-rapport.md`** — **Copier comme gabarit** du rapport final.

## Garde-fous

- **Ne JAMAIS inventer d'URL.** Se limiter aux domaines racines officiels réels (iana.org, ietf.org, rfc-editor.org, man7.org, cyber.gouv.fr, nvd.nist.gov, cve.org, standards.ieee.org, docs.aws.amazon.com, learn.microsoft.com, cloud.google.com, netplan.io, openssh.com, nginx.org, docs.docker.com, …) + une requête `site:` quand l'URL profonde n'est pas certaine.
- **Toujours dater** la vérification (rate limits Let's Encrypt, quotas cloud, API IA changent).
- **Distinguer outil et service sous-jacent** ; vérifier le fait sur la doc du composant réellement responsable.
- **Copier la formulation officielle** plutôt qu'une paraphrase.
- Se méfier des **valeurs par défaut "évidentes"** : préfixe tmux (Ctrl-b), `proxy_read_timeout` Nginx (60s), port Ollama (11434), WireGuard (UDP 51820) — confirmer chacune à la source.
