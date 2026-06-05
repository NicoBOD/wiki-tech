import sys

slug = "automatiser-consolidation-indicateurs-cles"

card = f'''                <div class="article-card">
                    <img src="../../images/blog/img-{slug}.jpg" alt="Stop Losing 4 Hours Every Monday: Automate Your Key Metrics Consolidation" class="article-image">
                    <div class="article-content">
                        <span class="article-date">June 5, 2026</span>
                        <h3 class="article-title">Stop Losing 4 Hours Every Monday: Automate Your Key Metrics Consolidation</h3>
                        <p class="article-excerpt">Discover how automating your dashboards provides a reliable summary of your overall activity without any manual data manipulation.</p>
                        <a href="{slug}.html" class="btn-read-more">Read article</a>
                    </div>
                </div>
'''

with open('/opt/data/website-zamania/en/blog/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<!-- ARTICLES_LIST_START -->', '<!-- ARTICLES_LIST_START -->\n' + card)

with open('/opt/data/website-zamania/en/blog/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
