import sys

slug = "automatiser-consolidation-indicateurs-cles"

card = f'''                <div class="article-card">
                    <img src="../../images/blog/img-{slug}.jpg" alt="لا تضيعوا 4 ساعات كل يوم اثنين: أتمتوا تجميع مؤشرات الأداء الرئيسية" class="article-image">
                    <div class="article-content">
                        <span class="article-date">5 يونيو 2026</span>
                        <h3 class="article-title">لا تضيعوا 4 ساعات كل يوم اثنين: أتمتوا تجميع مؤشرات الأداء الرئيسية</h3>
                        <p class="article-excerpt">اكتشفوا كيف تتيح لكم أتمتة لوحات المعلومات الحصول على ملخص موثوق لنشاطكم العام دون أي تدخل يدوي.</p>
                        <a href="{slug}.html" class="btn-read-more">اقرأ المقال</a>
                    </div>
                </div>
'''

with open('/opt/data/website-zamania/ar/blog/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<!-- ARTICLES_LIST_START -->', '<!-- ARTICLES_LIST_START -->\n' + card)

with open('/opt/data/website-zamania/ar/blog/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
