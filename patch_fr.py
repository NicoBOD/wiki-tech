import sys

slug = "automatiser-consolidation-indicateurs-cles"

card = f'''                <div class="article-card">
                    <img src="../images/blog/img-{slug}.jpg" alt="Ne perdez plus 4 heures chaque lundi : automatisez la consolidation de vos indicateurs clés" class="article-image">
                    <div class="article-content">
                        <span class="article-date">5 Juin 2026</span>
                        <h3 class="article-title">Ne perdez plus 4 heures chaque lundi : automatisez la consolidation de vos indicateurs clés</h3>
                        <p class="article-excerpt">Découvrez comment l'automatisation de vos tableaux de bord vous permet d'obtenir une synthèse fiable de votre activité globale sans aucune manipulation manuelle.</p>
                        <a href="{slug}.html" class="btn-read-more">Lire l'article</a>
                    </div>
                </div>
'''

with open('/opt/data/website-zamania/blog/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<!-- ARTICLES_LIST_START -->', '<!-- ARTICLES_LIST_START -->\n' + card)

with open('/opt/data/website-zamania/blog/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
