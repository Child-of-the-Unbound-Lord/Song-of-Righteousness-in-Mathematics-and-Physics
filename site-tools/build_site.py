#!/usr/bin/env python3
"""Build the Moonlit Lab public site from editor-friendly YAML + Markdown.

Use `python site-tools/build_site.py --preview` without npm for local layout previews.
Production runs with `node_modules/katex` and fails if mathematics cannot render.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime
from html import escape
from pathlib import Path
import json
import re
import subprocess
import sys
import unicodedata
from urllib.parse import urlsplit

import yaml
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "site-content"
OUTPUT = ROOT / "docs"
TEMPLATES = ROOT / "site-tools" / "templates"
SITE_ROOT = "https://child-of-the-unbound-lord.github.io/Song-of-Righteousness-in-Mathematics-and-Physics/"
MEDIA_BASE = "/Song-of-Righteousness-in-Mathematics-and-Physics/"


def read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def text(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value or "")


def asset_path(value):
    raw = text(value).strip()
    return raw[len(MEDIA_BASE):] if raw.startswith(MEDIA_BASE) else raw


def safe_url(url):
    """Allow normal web links and site-local paths, never script or protocol-relative URLs."""
    u = text(url).strip()
    if not u or any(c.isspace() or ord(c) < 32 for c in u):
        return "#"
    if u.startswith("//") or u.startswith("\\"):
        return "#"
    if u.startswith(("/", "#")):
        return u
    try:
        parts = urlsplit(u)
        if parts.scheme.lower() in {"https", "http"} and parts.netloc and not parts.username and not parts.password:
            return u
    except ValueError:
        pass  # Bad URLs should not prevent publication of the whole website.
    return "#"  # do not allow javascript:, data:, and other unsupported links


def tag(soup, name, attrs=None, value=None):
    t = soup.new_tag(name, attrs=attrs or {})
    if value is not None:
        t.string = text(value)
    return t


def set_string(soup, selector, value):
    node = soup.select_one(selector)
    if node is None:
        raise ValueError("Missing template selector: " + selector)
    node.string = text(value)


def slugify(value):
    t = unicodedata.normalize("NFKC", text(value)).lower().strip()
    t = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", t, flags=re.UNICODE).strip("-")
    return t or "section"


def extract_math(source):
    """Recognize $, $$, \\(, \\[ outside fenced code and inline backticks."""
    records = []

    def store(expr, display):
        token = f"MOONLITMATHPLACEHOLDER{len(records):05d}END"
        records.append({"tex": expr.strip(), "display": display, "token": token})
        return token

    # A block may start with $$ or \\[ and finish later; code fences are excluded.
    lines = source.splitlines(keepends=True)
    stage1 = []
    fence = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if not fence:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = ""
            stage1.append(line)
            i += 1
            continue
        if fence:
            stage1.append(line)
            i += 1
            continue
        stripped = line.strip()
        pair = (("$$", "$$"), (r"\[", r"\]"))
        matched = next(((a, b) for a, b in pair if stripped.startswith(a)), None)
        if matched:
            a, b = matched
            remainder = stripped[len(a):]
            if b in remainder:
                expr, rest = remainder.split(b, 1)
                if not rest.strip():
                    stage1.append("\n" + store(expr, True) + "\n")
                    i += 1
                    continue
            buffer = [remainder]
            j = i + 1
            done = False
            while j < len(lines):
                fragment = lines[j]
                if b in fragment:
                    part, rest = fragment.split(b, 1)
                    if not rest.strip():
                        buffer.append(part)
                        done = True
                        break
                buffer.append(fragment)
                j += 1
            if done:
                stage1.append("\n" + store("".join(buffer), True) + "\n")
                i = j + 1
                continue
        stage1.append(line)
        i += 1
    raw = "".join(stage1)
    inline_re = re.compile(r"(?<!\\)(?<!\$)\$\$(?!\$)(.+?)\$\$(?!\$)|(?<!\\)\\\((.+?)\\\)|(?<!\\)(?<!\$)\$(?![\s$])(.+?)(?<!\\)\$(?!\$)")
    # Inline processing only on non-fenced lines; do not parse inline code spans.
    result = []
    fence = ""
    for line in raw.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if not fence:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = ""
            result.append(line)
            continue
        if fence:
            result.append(line)
            continue
        spans = re.split(r"(`+[^`\n]*`+)", line)
        for index in range(0, len(spans), 2):
            spans[index] = inline_re.sub(lambda m: store(m.group(1) or m.group(2) or m.group(3), bool(m.group(1))), spans[index])
        result.append("".join(spans))
    return "".join(result), records


def render_tex(items, preview):
    if not items:
        return []
    cmd = ["node", str(ROOT / "site-tools" / "render_math.cjs")]
    proc = subprocess.run(cmd, input=json.dumps(items, ensure_ascii=False), capture_output=True, text=True, cwd=ROOT)
    if proc.returncode:
        if not preview:
            raise RuntimeError("KaTeX build failure: " + proc.stderr.strip())
        print("PREVIEW ONLY: KaTeX is not installed. Rendered equations are placeholders.", file=sys.stderr)
        return [f'<span class="math-tex-fallback">{escape(item["tex"])}</span>' for item in items]
    return json.loads(proc.stdout)


def make_markdown_renderer():
    md = MarkdownIt("commonmark", {"html": False, "breaks": False}).enable("table").enable("strikethrough")
    # Footnotes are essential for academic notes. Raw HTML stays disabled.
    md.use(footnote_plugin)

    def fence(tokens, idx, options, env):
        entry = tokens[idx]
        language = entry.info.strip().split()[0] if entry.info.strip() else "text"
        try:
            lexer = get_lexer_by_name(language)
        except Exception:
            lexer = TextLexer()
        return highlight(entry.content, lexer, HtmlFormatter(cssclass="highlight", nowrap=False))

    md.renderer.rules["fence"] = fence
    return md


def render_article_body(raw, preview):
    stripped, spans = extract_math(raw)
    md = make_markdown_renderer()
    toks = md.parse(stripped)
    headings = []
    used = {}
    for i, tok in enumerate(toks):
        if tok.type == "heading_open" and i + 1 < len(toks):
            title = toks[i + 1].content
            slug = slugify(title)
            n = used.get(slug, 0) + 1
            used[slug] = n
            if n > 1:
                slug += f"-{n}"
            tok.attrSet("id", slug)
            headings.append({"id": slug, "title": title, "level": tok.tag})
    html = md.renderer.render(toks, md.options, {})
    rendered = render_tex(spans, preview)
    for record, formula in zip(spans, rendered):
        token = record["token"]
        replacement = (f'<div class="math-display">{formula}</div>' if record["display"]
                       else f'<span class="math-inline">{formula}</span>')
        html = html.replace(f"<p>{token}</p>", replacement)
        html = html.replace(token, replacement)
    return html, headings, spans


def load_articles():
    data = []
    for file in sorted((SOURCE / "articles").glob("*.md")):
        src = file.read_text(encoding="utf-8")
        fm = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", src, flags=re.DOTALL)
        if not fm:
            raise ValueError(f"Missing YAML frontmatter: {file}")
        meta = yaml.safe_load(fm.group(1)) or {}
        slug = text(meta.get("slug") or file.stem).strip()
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"Invalid slug: {slug}")
        meta["slug"] = slug
        meta["body"] = fm.group(2)
        meta["date"] = text(meta.get("date"))
        meta["file"] = str(file)
        if not meta.get("draft", False):
            data.append(meta)
    if len({x["slug"] for x in data}) != len(data):
        raise ValueError("Duplicate article slugs")
    return sorted(data, key=lambda a: a["date"], reverse=True)


def update_index(config, themes, articles, projects, research, publications, comments):
    soup = BeautifulSoup((TEMPLATES / "index.html").read_text(encoding="utf-8"), "html.parser")
    set_string(soup, "title", config["title"] + " · " + config.get("english_title", ""))
    set_string(soup, ".brand span", config["title"])
    set_string(soup, ".brand small", config["english_title"])
    set_string(soup, ".eyebrow", config["role"])
    set_string(soup, ".hero-copy h1", config.get("headline", config["title"]))
    set_string(soup, ".hero-copy .lead", config["lead"])
    set_string(soup, ".hero-copy .intro", config["intro"])
    action = soup.select_one(".actions .primary")
    action.clear(); action.append(config["hero_action"] + " ↗")
    set_string(soup, ".status span", config["interest_label"])
    set_string(soup, ".status b", config["interests"])
    set_string(soup, ".section#research h2", config["research_title"])
    set_string(soup, ".section#research .section-heading > p", config["research_intro"])
    set_string(soup, ".section#publications h2", config["publications_title"])
    set_string(soup, ".section#publications .section-heading > p", config["publications_intro"])
    set_string(soup, ".section#projects h2", config["projects_title"])
    set_string(soup, ".section#projects .section-heading > p", config["projects_intro"])
    set_string(soup, ".section#notes h2", config["notes_title"])
    set_string(soup, ".section#notes .section-heading > p", config["notes_intro"])
    set_string(soup, ".section#about h2", config["about_title"])
    set_string(soup, ".section#comments h2", config["comments_title"])
    # Editable projects and research, not hard-coded HTML.
    three = soup.select_one("#research .three"); three.clear()
    for idx, entry in enumerate(research, 1):
        box = tag(soup, "article", {"class": "topic"})
        box.append(tag(soup, "span", {"class": "num"}, f"{idx:02}"))
        box.append(tag(soup, "h3", value=entry.get("title")))
        box.append(tag(soup, "p", value=entry.get("summary")))
        tags = tag(soup, "div", {"class": "tags"})
        for label in text(entry.get("tags")).split(","):
            if label.strip():
                tags.append(tag(soup, "span", value=label.strip()))
        box.append(tags); three.append(box)
    proj_list = soup.select_one("#projects .project-list"); proj_list.clear()
    for item in projects:
        card = tag(soup, "a", {"class": "project", "href": safe_url(item.get("url")), "target": "_blank", "rel": "noopener noreferrer"})
        info = tag(soup, "div")
        info.append(tag(soup, "small", value=item.get("kind", "PROJECT")))
        info.append(tag(soup, "h3", value=item.get("title")))
        info.append(tag(soup, "p", value=item.get("description")))
        card.append(info); card.append(tag(soup, "span", {"class": "arrow"}, "↗")); proj_list.append(card)
    pub_area = soup.select_one("#publications .empty")
    if publications:
        ul = tag(soup, "div", {"class": "publication-list"})
        for row in publications:
            item = tag(soup, "article", {"class": "publication"})
            item.append(tag(soup, "small", value=row.get("year")))
            item.append(tag(soup, "h3", value=row.get("title")))
            item.append(tag(soup, "p", value=" · ".join(filter(None, [text(row.get("authors")), text(row.get("venue"))]))))
            links = tag(soup, "div", {"class": "publication-links"})
            for field, label in (("doi", "论文 / DOI ↗"), ("pdf", "PDF ↗")):
                if row.get(field):
                    links.append(tag(soup, "a", {"href": safe_url(row[field]), "target": "_blank", "rel": "noopener noreferrer"}, label))
            if row.get("bibtex"):
                b = tag(soup, "button", {"class": "bibtex-copy", "type": "button", "data-bibtex": text(row["bibtex"])}, "复制 BibTeX")
                links.append(b)
            item.append(links); ul.append(item)
        pub_area.replace_with(ul)
    about = soup.select_one("#about .about-grid > div"); about.clear()
    for paragraph in config.get("about_paragraphs", []):
        about.append(tag(soup, "p", value=paragraph))
    identity = soup.select_one(".identity")
    username = text(config["github_username"])
    identity.select_one("strong").string = username
    identity.select_one("a")["href"] = safe_url(f"https://github.com/{username}")
    identity.select_one("img")["src"] = f"https://github.com/{username}.png?size=112"
    # Optional public contact links live in the same CMS-managed file as the bio.
    contact_links = tag(soup, "div", {"class": "contact-links"})
    email = text(config.get("contact_email", "")).strip()
    if email and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        contact_links.append(tag(soup, "a", {"href": "mailto:" + email}, "联系邮箱 ↗"))
    for field, label in (("scholar_url", "Google Scholar ↗"), ("orcid_url", "ORCID ↗")):
        url = safe_url(config.get(field, ""))
        if url != "#" and url.startswith("https://"):
            contact_links.append(tag(soup, "a", {"href": url, "target": "_blank", "rel": "noopener noreferrer"}, label))
    if contact_links.contents:
        identity.select_one("div").append(contact_links)
    for anchor in soup.select("a[href='https://github.com/Child-of-the-Unbound-Lord']"):
        anchor["href"] = safe_url(f"https://github.com/{username}")
    for f in soup.select("footer > span"):
        if config["title"] in f.get_text():
            f.clear(); f.append(text(config["footer"]))
    default_theme = next((theme for theme in themes if theme.get("id") == "mai"), themes[0])
    buttons = soup.select("[data-settheme]")
    wrapper = buttons[0].parent; wrapper.clear()
    for theme in themes:
        button = tag(soup, "button", {"data-settheme": theme["id"], "aria-pressed": "true" if theme["id"] == default_theme["id"] else "false", "title": theme.get("description", "")})
        button.append(tag(soup, "i")); button.append(theme["label"])
        wrapper.append(button)
    art = soup.select_one(".hero-art")
    for decorative in art.select(".orbit, .big-moon, .landscape"):
        decorative.decompose()
    figure = tag(soup, "img", {"class": "theme-illustration", "id": "theme-illustration", "src": asset_path(default_theme["image"]), "alt": default_theme["description"], "width": "1100", "height": "740", "fetchpriority": "high"})
    art.insert(0, figure)
    set_string(soup, "#theme-caption", default_theme["caption"])
    scene_foot = soup.select_one(".scene-foot")
    scene_foot.clear()
    scene_foot.append("有些问题，值得再想一遍。")
    scene_foot.append(tag(soup, "span", value="ILLUSTRATED THEME · ORIGINAL SCENES"))
    # Navigation and content management link: visible but editing requires write access.
    nav = soup.select_one(".topbar nav")
    nav.append(tag(soup, "a", {"href": "admin/", "class": "admin-link"}, "管理内容"))
    # Introduce theme metadata as JSON in JS payload, not inline code.
    payload = [{**x, "image": asset_path(x.get("image"))} for x in themes]
    js = OUTPUT / "assets" / "data.js"
    notes = [{"slug": a["slug"], "title": a.get("title", ""), "date": a["date"], "tag": a.get("category", "arts"),
              "type": a.get("category_label", ""), "excerpt": a.get("excerpt", ""),
              "keywords": [v.strip() for v in text(a.get("keywords")).split(",") if v.strip()],
              "demo": bool(a.get("sample", False)), "has_math": bool(extract_math(a["body"])[1]),
              "reading_minutes": max(1, (len(re.sub(r"\s+", "", a["body"])) + 499) // 500)}
             for a in articles]
    # Progressive enhancement: articles are visible and indexable even without JavaScript.
    list_node = soup.select_one("#note-list")
    list_node.clear()
    for note in notes:
        card = tag(soup, "a", {"class": "note", "href": "posts/" + note["slug"] + ".html"})
        info = tag(soup, "div")
        info.append(tag(soup, "small", value=f'{note["date"]} · {note["type"]} · 约 {note["reading_minutes"]} 分钟'))
        h3 = tag(soup, "h3", value=note["title"])
        if note["demo"]:
            h3.append(tag(soup, "em", value="排版示例"))
        info.append(h3)
        info.append(tag(soup, "p", value=note["excerpt"]))
        card.append(info)
        card.append(tag(soup, "span", {"aria-hidden": "true"}, "↗"))
        list_node.append(card)
    if not notes:
        soup.select_one("#no-results").attrs.pop("hidden", None)
        set_string(soup, "#no-results", "还没有公开文章。你可以从内容后台发布第一篇 Markdown 手记。")
    # Content data is user-controlled. Escaping < removes accidental script-close sequences.
    def jsobj(obj):
        return json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028")
    js.write_text("window.LAB_NOTES=" + jsobj(notes) + ";\nwindow.LAB_THEMES=" + jsobj(payload) + ";\nwindow.LAB_GISCUS=" + jsobj(comments) + ";\n", encoding="utf-8")
    comments_box = soup.select_one("#comment-box")
    if not (comments.get("enabled") and comments.get("category_id")):
        set_string(soup, "#comment-box b", "GitHub Discussions 评论尚未启用")
        set_string(soup, "#comment-box p", comments.get("notice", "管理员正在配置评论。"))
    # Feed link makes new essays discoverable without a platform account.
    soup.head.append(tag(soup, "link", {"rel": "alternate", "type": "application/rss+xml", "title": "月下研究室 · 研究手记", "href": "feed.xml"}))
    footer = soup.select_one("footer")
    if footer:
        footer.append(tag(soup, "a", {"href": "feed.xml", "title": "订阅最新文章"}, "RSS 订阅"))
    # Keep social previews consistent with the editor-managed site content.
    soup.select_one('meta[name="description"]')["content"] = config["intro"]
    for prop, value in (("og:title", config["title"] + " · " + config.get("english_title", "")),
                        ("og:description", config["intro"])):
        element = soup.select_one('meta[property="' + prop + '"]')
        if element:
            element["content"] = value
    if themes:
        soup.head.append(tag(soup, "meta", {"property": "og:image", "content": SITE_ROOT + asset_path(default_theme["image"])}))
    soup.body.append(tag(soup, "script", {"src": "assets/comments.js"}))
    (OUTPUT / "index.html").write_text(str(soup), encoding="utf-8")


def update_article(meta, article_html, headings, comments):
    soup = BeautifulSoup((TEMPLATES / "article.html").read_text(encoding="utf-8"), "html.parser")
    heading = text(meta.get("title"))
    soup.select_one("title").string = heading + " · 月下研究室"
    set_string(soup, ".article-meta", " · ".join(filter(None, [text(meta.get("category_label")), meta["date"]])))
    set_string(soup, ".article h1", heading)
    notice = soup.select_one(".article .notice")
    if meta.get("sample"):
        notice.string = "这是一篇排版示例，可在内容后台替换。不是已发表的个人研究成果。"
    else:
        notice.decompose()
    for child in list(soup.select_one(".article").children):
        if getattr(child, "name", "") in ("p", "h2", "pre", "div") and child is not notice and "article-tools" not in child.get("class", []):
            if "article-meta" not in child.get("class", []):
                child.decompose()
    body = tag(soup, "div", {"class": "prose"})
    fragment = BeautifulSoup(article_html, "html.parser")
    for child in list(fragment.contents):
        body.append(child)
    tools = soup.select_one(".article-tools")
    # An editable source link is useful for the owner and harmless for readers.
    tools.append(tag(soup, "a", {"class": "edit-source", "target": "_blank", "rel": "noopener noreferrer",
                                 "href": "https://github.com/Child-of-the-Unbound-Lord/Song-of-Righteousness-in-Mathematics-and-Physics/edit/main/site-content/articles/" + meta["slug"] + ".md"}, "编辑这篇原稿 ↗"))
    tools.insert_before(body)
    toc = soup.select_one(".toc"); toc.clear()
    toc.append(tag(soup, "b", value="本文目录"))
    for h in headings:
        if h["level"] in ("h2", "h3"):
            toc.append(tag(soup, "a", {"href": "#" + h["id"], "class": "toc-h3" if h["level"] == "h3" else ""}, h["title"]))
    # Add self-hosted KaTeX stylesheet; actual math HTML is already generated at build time.
    soup.select_one('link[href="../assets/article.css"]').insert_after(tag(soup, "link", {"rel": "stylesheet", "href": "../assets/katex/katex.min.css"}))
    soup.select_one('link[href="../assets/style.css"]').insert_after(tag(soup, "link", {"rel": "stylesheet", "href": "../assets/code.css"}))
    comment = tag(soup, "section", {"class": "article-comment", "id": "article-comments"})
    comment.append(tag(soup, "h2", value="讨论"))
    comment.append(tag(soup, "div", {"id": "comment-box", "class": "article-comment-box"}))
    if not (comments.get("enabled") and comments.get("category_id")):
        comment.select_one("#comment-box").append(tag(soup, "p", value=comments.get("notice", "评论尚未开放。")))
    tools.insert_after(comment)
    # Modern link previews
    soup.head.append(tag(soup, "meta", {"name": "description", "content": text(meta.get("excerpt"))}))
    soup.head.append(tag(soup, "link", {"rel": "canonical", "href": SITE_ROOT + "posts/" + meta["slug"] + ".html"}))
    soup.head.append(tag(soup, "meta", {"property": "og:title", "content": heading}))
    soup.head.append(tag(soup, "meta", {"property": "og:type", "content": "article"}))
    soup.head.append(tag(soup, "meta", {"property": "og:description", "content": text(meta.get("excerpt"))}))
    soup.head.append(tag(soup, "link", {"rel": "icon", "type": "image/svg+xml", "href": "../assets/favicon.svg"}))
    soup.head.append(tag(soup, "link", {"rel": "alternate", "type": "application/rss+xml", "title": "月下研究室 · 研究手记", "href": "../feed.xml"}))
    # Site-wide giscus data already in data.js; use same loader on articles.
    script = tag(soup, "script", {"src": "../assets/data.js"}); soup.body.append(script)
    soup.body.append(tag(soup, "script", {"src": "../assets/comments.js"}))
    (OUTPUT / "posts" / (meta["slug"] + ".html")).write_text(str(soup), encoding="utf-8")


def build_discovery_files(config, articles):
    """Generate sitemap and RSS from the same published Markdown catalog."""
    import xml.etree.ElementTree as ET
    from datetime import timezone
    from email.utils import format_datetime
    title = text(config.get("title", "月下研究室"))
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", ns)
    root = ET.Element(f"{{{ns}}}urlset")
    for url, lastmod in [(SITE_ROOT, ""), *[(SITE_ROOT + "posts/" + item["slug"] + ".html", item.get("date", "")) for item in articles]]:
        node = ET.SubElement(root, f"{{{ns}}}url")
        ET.SubElement(node, f"{{{ns}}}loc").text = url
        if lastmod:
            ET.SubElement(node, f"{{{ns}}}lastmod").text = lastmod
    (OUTPUT / "sitemap.xml").write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    for field, value in (("title", title + " · 研究手记"), ("link", SITE_ROOT),
                         ("description", text(config.get("notes_intro", "个人学术笔记"))),
                         ("language", "zh-cn")):
        ET.SubElement(channel, field).text = value
    for article in articles[:30]:
        item = ET.SubElement(channel, "item")
        url = SITE_ROOT + "posts/" + article["slug"] + ".html"
        for field, value in (("title", text(article.get("title"))), ("link", url),
                             ("guid", url), ("description", text(article.get("excerpt")))):
            ET.SubElement(item, field).text = value
        date_text = text(article.get("date"))
        if date_text:
            try:
                parsed = datetime.fromisoformat(date_text).replace(tzinfo=timezone.utc)
                ET.SubElement(item, "pubDate").text = format_datetime(parsed)
            except ValueError:
                pass
    (OUTPUT / "feed.xml").write_bytes(ET.tostring(rss, encoding="utf-8", xml_declaration=True))
    (OUTPUT / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + SITE_ROOT + "sitemap.xml\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preview", action="store_true", help="Permit LaTeX placeholders for offline layout preview")
    args = p.parse_args()
    site = read_yaml(SOURCE / "site.yml")
    research = read_yaml(SOURCE / "research.yml") or []
    projects = read_yaml(SOURCE / "projects.yml") or []
    publications = read_yaml(SOURCE / "publications.yml") or []
    themes = read_yaml(SOURCE / "themes.yml")
    comments = read_yaml(SOURCE / "comments.yml")
    articles = load_articles()
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "posts").mkdir(exist_ok=True)
    update_index(site, themes, articles, projects, research, publications, comments)
    formula_count = 0
    slugs = {a["slug"] for a in articles}
    for old in (OUTPUT / "posts").glob("*.html"):
        if old.stem not in slugs:
            old.unlink()
    for article in articles:
        html, headings, spans = render_article_body(article["body"], args.preview)
        formula_count += len(spans)
        update_article(article, html, headings, comments)
    # Include a printable code highlight theme, generated with Pygments.
    formatter = HtmlFormatter(style="monokai", cssclass="highlight")
    (OUTPUT / "assets" / "code.css").write_text(formatter.get_style_defs(".highlight") + "\n", encoding="utf-8")
    build_discovery_files(site, articles)
    # Friendly fallback when a shared article was renamed, deleted or left as draft.
    (OUTPUT / "404.html").write_text((TEMPLATES / "404.html").read_text(encoding="utf-8"), encoding="utf-8")
    # Prevent github pages default Jekyll processing.
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Build complete: {len(articles)} articles; {formula_count} math expressions; {len(themes)} themes.")
    if not args.preview and formula_count:
        count = sum((OUTPUT / "posts" / (a["slug"] + ".html")).read_text(encoding="utf-8").count('class="katex') for a in articles)
        if count < formula_count:
            raise AssertionError(f"Math not rendered: expected {formula_count} KaTeX nodes, found {count}")


if __name__ == "__main__":
    main()
