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
pages=list((OUT/'posts').glob('*.html'))
assert pages, 'At least one public article is required for this smoke test'
math_found=0
for page in pages:
    article=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
    assert article.select_one('.prose')
    assert article.select_one('link[href="../assets/katex/katex.min.css"]')
    assert article.select_one('#article-comments')
    assert article.select_one('link[rel="canonical"]')
    if article.select('.katex'):
        math_found += len(article.select('.katex'))
        assert article.select_one('math'), 'Accessible MathML missing'
    for anchor in article.select('.toc a'):
        assert article.select_one('[id="'+anchor['href'][1:]+'"]'), 'Broken TOC anchor: '+anchor['href']
assert math_found>=1, 'No server-rendered math found; check test examples'
for key in ('mai','yukino','frieren','eru'):
    assert (OUT/'assets/themes'/f'{key}.webp').exists()
assert (OUT/'assets/katex/katex.min.css').exists()
assert (OUT/'assets/katex/fonts/KaTeX_Main-Regular.woff2').exists()
assert not list(OUT.rglob('*.html'))==[], 'HTML files missing'
print('PASS build: articles + KaTeX + MathML + site editor + 4 themes')
