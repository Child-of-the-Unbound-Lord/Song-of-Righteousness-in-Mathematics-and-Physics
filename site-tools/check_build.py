"""Fast static assertions for generated site, content and math."""
from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
index=BeautifulSoup((OUT/'index.html').read_text(encoding='utf-8'),'html.parser')
assert len(index.select('[data-settheme]'))==4
assert index.select_one('#theme-illustration')['src'].endswith('mai.webp')
assert index.select_one('.admin-link')['href']=='admin/'
assert index.select_one('#note-list')
assert (OUT/'admin/index.html').exists()
assert (OUT/'sitemap.xml').exists()
assert (OUT/'feed.xml').exists()
assert (OUT/'robots.txt').exists()
pages=list((OUT/'posts').glob('*.html'))
# A newly launched research site may intentionally have zero published posts.
# It may also contain articles with no mathematics: both are valid editor states.
import json, re
catalog=(OUT/'assets/data.js').read_text(encoding='utf-8')
match=re.search(r'window\.LAB_NOTES=(.*?);\s*window\.LAB_THEMES=',catalog,re.DOTALL)
assert match, 'Generated article catalog is missing'
notes=json.loads(match.group(1))
assert len(pages)==len(notes), 'Generated article catalog and post pages disagree'
assert len(index.select('#note-list > a.note'))==len(notes), 'Static post list missing from home page'
assert (OUT/'404.html').exists(), 'Missing user-friendly 404 page'
math_found=0
math_expected=sum(1 for a in notes if a.get('has_math'))
math_pages=0
for page in pages:
    article=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
    assert article.select_one('.prose')
    assert article.select_one('link[href="../assets/katex/katex.min.css"]')
    assert article.select_one('#article-comments')
    sources=[x.get('src') for x in article.select('script[src]')]
    assert '../assets/data.js' in sources and '../assets/comments.js' in sources, 'Article comments loader missing'
    assert sources.index('../assets/data.js') < sources.index('../assets/comments.js'), 'Comment script must load after config'
    assert article.select_one('link[rel="canonical"]')
    if article.select('.katex'):
        math_found += len(article.select('.katex'))
        math_pages+=1
        assert article.select_one('math'), 'Accessible MathML missing'
    for anchor in article.select('.toc a'):
        assert article.select_one('[id="'+anchor['href'][1:]+'"]'), 'Broken TOC anchor: '+anchor['href']
assert math_pages==math_expected, f'Expected math in {math_expected} pages; found {math_pages}'
for key in ('mai','yukino','frieren','eru'):
    assert (OUT/'assets/themes'/f'{key}.webp').exists()
assert (OUT/'assets/katex/katex.min.css').exists()
assert (OUT/'assets/katex/fonts/KaTeX_Main-Regular.woff2').exists()
assert not list(OUT.rglob('*.html'))==[], 'HTML files missing'
print(f'PASS build: {len(notes)} published articles, {math_pages} with math, static index + editor + 4 themes')

# Admin must link to real authenticated editors, not suggest that static Pages can save edits.
admin_html=(OUT/'admin/index.html').read_text(encoding='utf-8')
assert 'https://app.pagescms.org/' in admin_html
assert 'https://github.com/apps/pages-cms' in admin_html
assert '/edit/main/site-content/site.yml' in admin_html
assert '/new/main/site-content/articles' in admin_html
assert '不是可直接改字的编辑器' in admin_html
