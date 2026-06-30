<!--
  Gabarit de rapport de fact-check — COPIER puis remplir.
  Style aligné sur le MkDocs Material du wiki (admonitions !!!, emojis de statut, frontmatter).
  Ne PAS charger ce fichier en contexte au-delà de la copie : c'est un modèle, pas une référence à lire.
  Remplacer chaque champ <…> et chaque ligne d'exemple par les données réelles de la vérification.
  Tout en français. Chemins en slash avant. Ne jamais inventer d'URL : domaine officiel réel + requête site: si l'URL profonde est incertaine.
-->

# Rapport de fact-check — <sujet ou fichier vérifié>

!!! abstract "Contexte de vérification"
    - **Source / fichier vérifié** : `docs/<domaine>/<fichier>.md` (ou titre du brouillon LLM)
    - **Date de consultation** : 2026-06-29 *(repère de fraîcheur — réutiliser la date du jour ; sur un sujet versionné, cette date n'atteste que de l'état constaté ce jour-là, à re-vérifier ensuite)*
    - **OS / version cible** : Ubuntu 24.04 LTS *(défaut du wiki ; préciser une autre cible si l'auteur l'indique)*
    - **Domaine(s) concerné(s)** : <Systèmes / Réseaux / Cloud / Cybersécurité / IA / Automatisation / Logiciels / Debug / Astuces>
    - **Affirmations analysées** : <N> (numérotées A1 … A`<N>`)

## Verdicts

!!! note "Barème et règle de source"
    🟢 **Vrai** (confirmé tel quel) · 🟠 **Nuancé** (exact sous condition : version, OS, valeur conseillée ≠ valeur par défaut) · 🔴 **Faux** (contredit — correction obligatoire) · ⚪ **Inconnu** (aucune source officielle — **jamais comblé par la mémoire du modèle**).
    La colonne **Source** porte une **référence précise** : page/section + **version (dès que le sujet est versionné)** + date de consultation. **Jamais un domaine racine seul** (`man7.org` interdit), **jamais une source Tier 3** (IT-Connect, Korben, Arch Wiki, forums) pour un fait technique (port, flag, valeur par défaut, norme).

| # | Statut | Affirmation évaluée | Correction / Précision factuelle | Source de confiance (page/section + version + date) |
|----|--------|---------------------|----------------------------------|----------------------------------------------|
| A1 | 🟢 Vrai | WireGuard écoute par défaut sur le port UDP 51820. | Exact, et bien en **UDP** (WireGuard fonctionne exclusivement en UDP, *UDP-only*). Conserver la clé officielle `ListenPort`. | Doc officielle WireGuard (`wg-quick(8)` / quickstart) ; requête `default listen port site:wireguard.com` ; consultée 2026-06-29 |
| A2 | 🟠 Nuancé | « Mettre `PersistentKeepalive = 25` est obligatoire pour que le tunnel fonctionne. » | Exact **sous condition** : 25 s est une **valeur conseillée** pour un pair derrière un NAT/pare-feu, **pas une obligation**. La **valeur par défaut est `0`** (fonction désactivée). Préciser le contexte (pair derrière NAT) et distinguer *conseillé* de *défaut*. | Doc officielle WireGuard, format de conf `wg(8)` (section *Configuration File Format*) ; requête `PersistentKeepalive default off site:wireguard.com` ; consultée 2026-06-29 |
| A3 | 🟠 Nuancé | « Sous Ubuntu 24.04, on déclare la passerelle par défaut avec `gateway4:` dans Netplan. » | **Dépend de la version** : `gateway4:` **fonctionne encore mais est déprécié** ; la forme actuelle est un bloc `routes:` (`to: default`, `via: <gw>`). Vrai sur d'anciennes versions, à proscrire sur 24.04. Reformuler avec `routes:`. | Doc Netplan, page *Netplan reference* (clé `routes` / dépréciation `gateway4`) ; requête `netplan gateway4 deprecated routes site:netplan.io` ; consultée 2026-06-29 |
| A4 | 🔴 Faux | « Le champ `version:` est requis en tête de `compose.yaml`. » | **Obsolète** : la Compose Specification actuelle traite `version:` comme **informatif et obsolète** (avertissement émis, valeur ignorée pour la validation). Le **retirer** ; ne pas le présenter comme requis. | Compose Specification, section *Version and name* ; requête `version field obsolete site:compose-spec.io` ; consultée 2026-06-29 |
| A5 | 🔴 Faux | « Le VLAN 802.1Q est défini par une RFC de l'IETF. » | **Mauvaise autorité** : 802.1Q est une norme **IEEE**, pas une RFC IETF. Corriger l'attribution. | IEEE Standards Association, norme IEEE 802.1Q ; requête `802.1Q VLAN tag standard site:standards.ieee.org` ; consultée 2026-06-29 |
| A6 | 🔴 Faux | « NIST recommande de changer son mot de passe tous les 90 jours. » | **Contredit par la source** (et non « nuancé ») : NIST SP 800-63B **déconseille** la rotation périodique forcée (« verifiers SHOULD NOT require periodic change ») et la complexité imposée — il privilégie la longueur et le filtrage des mots de passe compromis. Le changement n'est forcé qu'en cas de compromission avérée. Reformuler selon la version courante. | NIST SP 800-63B, Digital Identity Guidelines, §5.1.1.2 (préciser la révision citée : Rev. 3 ou Rev. 4) ; requête `password rotation guidance memorized secret site:nist.gov` ; consultée 2026-06-29 |
| A7 | ⚪ Inconnu | « Le quota par défaut est de X requêtes/min pour le service <…>. » | **Aucune source officielle datée trouvée** confirmant cette valeur — **à re-sourcer** (les quotas changent). Ne **pas** combler par la mémoire du modèle. | — (requête `<service> default rate limit site:<doc officielle>` restée sans preuve datée au 2026-06-29) |

*Remplacer les lignes ci-dessus par les affirmations réelles. Conserver au moins un exemple par statut tant que la vérification est en cours, puis nettoyer.*

## Synthèse

**Décompte** : `<n>` 🟢 Vrai · `<n>` 🟠 Nuancé · `<n>` 🔴 Faux · `<n>` ⚪ Inconnu (total `<N>`).

**Hallucinations notables détectées** *(liste courte — supprimer les lignes non applicables)* :

- 🔴 **Port / valeur par défaut inventé(e)** — ex. port annoncé en TCP au lieu d'UDP, port fantaisiste non assigné par l'IANA.
- 🔴 **Flag / option inexistant(e) ou déprécié(e) donné(e) comme actuel(le)** — ex. `version:` Compose présenté comme requis, option de man page disparue d'une version à l'autre.
- 🔴 **Mauvaise autorité** — ex. norme IEEE attribuée à une RFC IETF, spec HTTP attribuée au W3C au lieu de l'IETF.
- 🔴 **Doctrine périmée présentée comme actuelle** — ex. rotation forcée des mots de passe attribuée au NIST actuel, algorithme déprécié (SHA-1, RSA-1024) donné comme sûr : c'est **contredit** par la source, donc 🔴 (pas 🟠).
- 🟠 **Valeur par défaut supposée vs valeur conseillée** — ex. `PersistentKeepalive` (défaut `0`) ou `proxy_read_timeout` présenté comme défaut alors que c'est une valeur conseillée/différente.
- 🟠 **Syntaxe dépréciée mais encore tolérée** — ex. `gateway4` Netplan (fonctionne encore, à proscrire sur la version cible) : vrai sous condition de version.
- 🟠 **Outil confondu avec le service sous-jacent** — ex. Certbot ↔ Let's Encrypt, UFW ↔ nftables, Portainer ↔ Docker, Open WebUI ↔ Ollama.

## Verdict de publication

> Conserver **une seule** des trois admonitions ci-dessous selon le niveau de risque ; supprimer les deux autres.

!!! success "Publiable en l'état"
    Aucune 🔴 et aucune ⚪ bloquante. Les 🟠 sont déjà explicitées (version / condition mentionnée dans le texte). Le contenu peut être mis en ligne.

!!! warning "Publiable après corrections"
    Présence de 🔴 à corriger et/ou de 🟠 à expliciter (mention de version, condition, valeur conseillée vs défaut). **Appliquer les corrections de la section suivante**, puis republier.

!!! danger "À ne pas publier en l'état"
    Plusieurs 🔴 (faits faux) et/ou des ⚪ sur des éléments centraux (port, flag, commande exécutée par le lecteur). Risque de propager une hallucination. **Re-sourcer et corriger avant toute mise en ligne.**

## Recommandations actionnables

- [ ] **Appliquer les corrections 🔴** : remplacer chaque valeur/syntaxe contredite par la formulation officielle exacte (citée en colonne Source).
- [ ] **Expliciter les conditions / versions 🟠** : ajouter la mention « valable pour `<logiciel> <version>` / Ubuntu 24.04 LTS » et distinguer *valeur par défaut* vs *valeur conseillée*.
- [ ] **Re-sourcer les ⚪ avant publication** : relancer une requête `site:` sur le domaine officiel ; si aucune source datée n'existe, retirer l'affirmation plutôt que de la deviner.
- [ ] **Ajouter les mentions de version + date** pour tout sujet versionné (Compose, Terraform / provider, `az` / `gcloud`, Netplan, OpenSSH, Ollama, rate limits Let's Encrypt, quotas cloud, révision d'une SP NIST).
- [ ] **Vérifier l'attribution d'autorité** des normes citées (IEEE vs IETF vs W3C vs NVD/cve.org) et le couple outil ↔ service sous-jacent.
- [ ] **Recouper les vulnérabilités** (CVE / CVSS) sur NVD + cve.org (+ CERT-FR / CISA pour l'exploitation active) ; ne jamais publier un identifiant ou un score non recoupé.

---

<!--
  RAPPEL DE FORME (à NE PAS publier dans le rapport final) :
  - Ne jamais inventer d'URL — citer un domaine officiel réel + une requête site: si l'URL profonde est incertaine.
  - Horodater chaque vérification (date de consultation) ; préciser la version du logiciel / de la doc dès qu'un sujet est versionné.
  - La colonne Source ne contient jamais un domaine racine seul ni une source Tier 3 pour un fait technique.
  - Barème : « contredit par la source » = 🔴 (y compris une doctrine périmée donnée comme actuelle) ; « exact sous condition » = 🟠 ; ne pas confondre les deux.
-->
