"""Regression tests for editable content, math, safety and academic footnotes."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

PATH=Path(__file__).resolve().parents[1]/"build_site.py"
spec=importlib.util.spec_from_file_location("moonlit_builder", PATH)
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class ContentRegression(unittest.TestCase):
    def test_project_url_safety(self):
        for value in ("javascript:alert(1)", "data:text/html,hello", "//evil.example/x", "https://user:password@evil.example/"):
            self.assertEqual(builder.safe_url(value), "#")
        self.assertEqual(builder.safe_url("https://github.com/Child-of-the-Unbound-Lord"), "https://github.com/Child-of-the-Unbound-Lord")
        self.assertEqual(builder.safe_url("/assets/example.png"), "/assets/example.png")

    def test_math_inside_code_is_not_rendered(self):
        raw = "`$not_math$`\n\n```python\nprice = '$literal$'\n```\n\nA real equation: $x^2+y^2=z^2$.\n"
        converted, items=builder.extract_math(raw)
        self.assertEqual(len(items),1)
        self.assertIn("$literal$", converted)
        self.assertEqual(items[0]['tex'], "x^2+y^2=z^2")

    def test_footnotes_render_and_html_stays_escaped(self):
        markup, heads, formulas=builder.render_article_body("## Citation\nSee note[^1].\n\n[^1]: Source page 12.\n\n<script>alert(1)</script>", True)
        self.assertIn('footnote', markup)
        self.assertIn('Source page 12.', markup)
        self.assertNotIn('<script>', markup)
        self.assertFalse(formulas)

    def test_empty_or_draft_only_catalog(self):
        with tempfile.TemporaryDirectory() as base:
            src=Path(base)
            (src/'articles').mkdir()
            with patch.object(builder,'SOURCE',src):
                self.assertEqual(builder.load_articles(),[])
                (src/'articles'/'draft.md').write_text('---\ntitle: Draft\nslug: draft\ndraft: true\n---\nAn unfinished thought.',encoding='utf-8')
                self.assertEqual(builder.load_articles(),[])
                (src/'articles'/'simple.md').write_text('---\ntitle: Plain Text\nslug: simple\ndraft: false\n---\nA paragraph without formulas.',encoding='utf-8')
                articles=builder.load_articles()
                self.assertEqual([x['slug'] for x in articles],['simple'])
                self.assertEqual(builder.extract_math(articles[0]['body'])[1],[])

if __name__=='__main__':unittest.main()
