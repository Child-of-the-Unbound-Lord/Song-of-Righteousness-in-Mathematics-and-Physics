"""Run an HTTP smoke check of the public GitHub Pages website."""
from __future__ import annotations

import os
import sys
import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

SITE = os.environ.get("PAGE_URL", "").strip().rstrip("/") + "/"
if not SITE.startswith("https://"):
    sys.exit("PAGE_URL must contain the published HTTPS address.")

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag in ("a", "link") and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag in ("script", "img") and attrs.get("src"):
            self.links.append(attrs["src"])

def get(path, attempts=8):
    url = urljoin(SITE, path)
    error = None
    for attempt in range(attempts):
        try:
            req = Request(url, headers={
                "User-Agent": "Moonlit-Lab-Public-Site-Check/1.0",
                "Cache-Control": "no-cache"
            })
            with urlopen(req, timeout=20) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                data = response.read(400000)
            print(f"PASS HTTP 200 {path or '/'} ({len(data)} bytes)", flush=True)
            return data.decode("utf-8")
        except (URLError, HTTPError, UnicodeError, RuntimeError) as ex:
            error = ex
            if attempt < attempts - 1:
                time.sleep(5)
    raise RuntimeError(f"Failed {url}: {error}")

home = get("")
for expected in ("<title>月下研究室", "Child-of-the-Unbound-Lord", 'data-settheme="mai"', 'id="note-list"'):
    if expected not in home:
        sys.exit(f"Public home page missing: {expected}")

visited = set()
for page in ("index.html", "posts/proof-reading.html", "posts/models-and-errors.html", "posts/narrative-and-memory.html"):
    html = home if page == "index.html" else get(page)
    parsed = Document()
    parsed.feed(html)
    for href in parsed.links:
        parsed_url = urlsplit(href)
        if not parsed_url.path and parsed_url.fragment:
            if parsed_url.fragment not in parsed.ids:
                sys.exit(f"Broken anchor in {page}: {href}")
            continue
        if parsed_url.scheme or parsed_url.netloc or href.startswith("//"):
            continue
        relative = urljoin(page, parsed_url.path)
        if not relative or relative in visited:
            continue
        visited.add(relative)
        get(relative)

print(f"PASS published website and {len(visited)} internal targets: {SITE}", flush=True)
