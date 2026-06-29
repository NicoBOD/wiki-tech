---
name: it-fact-checker
description: Vérifie des faits et affirmations informatiques en se basant sur des sources officielles (NIST, ANSSI, éditeurs).
category: research
---

# IT Fact Checker

Ce skill est utilisé pour vérifier la véracité des affirmations techniques dans les domaines de l'informatique (systèmes, réseaux, cybersécurité, cloud computing, DevOps, automatisation, IA, protocoles).

## 🎯 Déclenchement
Quand l'utilisateur demande de vérifier un texte, un article, un TP ou une affirmation technique. Particulièrement utile pour valider des contenus potentiellement générés par l'IA (qui peuvent contenir des hallucinations).

## 🛠️ Règles de Vérification (Autorité et Fiabilité)
1. **Sources Autorisées Uniquement** : 
   - Organismes d'état ou de standardisation : ANSSI, NIST, ISO, IETF (RFCs), W3C.
   - Éditeurs officiels et documentations officielles : Microsoft Learn, Cisco, Fortinet, AWS Docs, documentation Linux (man pages, Kernel.org), Docker Docs, Kubernetes.io, etc.
   - Acteurs reconnus et fiables : IT-Connect, Korben (mentionnés dans les préférences utilisateur pour la vulgarisation).
2. **Recherche de Preuves** :
   - Extraire les affirmations clés du texte soumis (chiffres, concepts techniques, commandes, pré-requis).
   - Utiliser la recherche web (si disponible) en forçant la recherche sur des domaines de confiance (ex: `site:cisco.com`, `site:ssi.gouv.fr`).
3. **Méfiance Anti-Hallucination** : Ne **JAMAIS** faire confiance à des blogs SEO génériques. Toujours remonter à la source officielle ou une source experte validée.

## 📋 Format de Sortie
Présentez le résultat sous forme de tableau Markdown :

| Statut | Affirmation évaluée | Correction / Précision factuelle | Source de confiance |
|--------|---------------------|----------------------------------|---------------------|
| 🟢 Vrai | [L'affirmation] | [Pourquoi c'est exact] | [Lien ou Référence exacte] |
| 🟠 Nuancé | [L'affirmation] | [Le contexte manquant / Limites] | [Lien ou Référence exacte] |
| 🔴 Faux | [L'affirmation] | [La vraie information] | [Lien ou Référence exacte] |
| ⚪ Inconnu | [L'affirmation] | Impossible à vérifier | Aucune source officielle trouvée |

## ⚠️ Pièges à éviter
- Ne pas s'appuyer uniquement sur les connaissances internes du modèle sans les vérifier, les IA peuvent halluciner des configurations, des numéros de ports ou des acronymes.
- Si le texte contient des commandes (CLI, Linux, Cisco), vérifier leur syntaxe exacte dans le manuel officiel.
