"""Public-network smoke test executed on GitHub's runner after deployment."""
from __future__ import annotations
from html.parser import HTMLParser
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

SITE = os.environ.get("PAGE_URL", "").strip().rstrip("/") + "/"
if not SITE.startswith("https://"):
    sys.exit("PAGE_URL must be a public HTTPS URL")

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.ids=set()
    def handle_starttag(self, name, pairs):
        attrs=dict(pairs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        attr = 'src' if name in ('script','img') else 'href' if name in ('a','link') else None
        if attr and attrs.get(attr):
            self.links.append(attrs[attr])

def request(path):
    url = urljoin(SITE,path)
    last=None
    for attempt in range(7):
        try:
            req=Request(url,headers={'User-Agent':'Moonlit-Lab-CI/2.0','Cache-Control':'no-cache'})
            with urlopen(req,timeout=30) as stream:
                if stream.status!=200:
                    raise RuntimeError(f'HTTP {stream.status}')
                body=stream.read(3_000_000)
            print(f'PASS HTTP 200 {path or "/"} ({len(body)} bytes)',flush=True)
            return body.decode('utf-8',errors='replace')
        except (HTTPError,URLError,RuntimeError) as err:
            last=err
            if attempt<6:
                time.sleep(4)
    raise RuntimeError(f'{url} could not be reached: {last}')

home=request('')
for text in ('月下研究室','data-settheme="mai"','id="note-list"','id="theme-illustration"'):
    if text not in home:sys.exit(f'Missing homepage element: {text}')
# Read the content catalog rather than assuming any example article will stay forever.
import json
catalog=request('assets/data.js')
match=re.search(r'window\.LAB_NOTES=(.*?);\s*window\.LAB_THEMES=',catalog,re.DOTALL)
if not match:sys.exit('Cannot find generated article catalog')
notes=json.loads(match.group(1))
articles={}
for entry in notes:
    slug=entry['slug']
    if not re.fullmatch(r'[a-z0-9-]+',slug):sys.exit('Unsafe article slug')
    articles[f'posts/{slug}.html']=request(f'posts/{slug}.html')
# A site with only draft articles or prose-only essays is perfectly publishable.
for entry in notes:
    html=articles['posts/'+entry['slug']+'.html']
    if entry.get('has_math') and not ('class="katex' in html and '<math' in html):
        sys.exit('Server-rendered KaTeX + MathML missing: '+entry['slug'])
if len(re.findall(r'class="note"',home)) != len(notes):
    sys.exit('Home page static article list differs from published notes')
for path,html in articles.items():
    if 'article-comment' not in html:sys.exit('Article missing discussion component: '+path)
    if '../assets/comments.js' not in html:sys.exit('Article comment loader missing: '+path)
for path in ('feed.xml', 'sitemap.xml', 'robots.txt', '404.html', 'assets/comments.js', 'assets/admin.js'):
    request(path)
admin=request('admin/')
if 'app.pagescms.org' not in admin:sys.exit('Admin editing entry is missing')
seen=set()
for page,html in [('',home),('admin/',admin),*articles.items()]:
    parsed=LinkParser();parsed.feed(html)
    for href in parsed.links:
        u=urlsplit(href)
        if u.scheme or u.netloc or href.startswith('//'):continue
        if not u.path and u.fragment:
            if u.fragment not in parsed.ids:
                # Templates can link to dynamic toc headings; those are checked in local build tests.
                print(f'WARN unresolved local fragment {page} {href}')
            continue
        target=urljoin(page,u.path)
        if not target or target in seen:continue
        if re.search(r'\.(woff2?|ttf|otf)$',target):continue
        seen.add(target)
        request(target)
# Additional article pages and local assets not necessarily linked from prose.
for target in ('assets/themes/mai.webp','assets/themes/yukino.webp','assets/themes/frieren.webp','assets/themes/eru.webp','assets/katex/katex.min.css','assets/katex/fonts/KaTeX_Main-Regular.woff2'):
    if target not in seen:
        seen.add(target)
        # font asset is binary, so check it through a separate binary request
        if target.endswith('.woff2'):
            with urlopen(Request(urljoin(SITE,target),headers={'User-Agent':'Moonlit-Lab-CI/2.0'}),timeout=20) as stream:
                assert stream.status==200 and len(stream.read())>100
            print('PASS HTTP 200 '+target)
        else:
            request(target)
print(f'PASS public site with KaTeX and {len(seen)} additional internal targets: {SITE}')
