#!/usr/bin/env python3
"""Per-language landing pages and metadata (title, description, Open Graph, hreflang).

index.html (Japanese, at /) stays the hand-edited source. This script:
  - rewrites the block between <!-- meta:start --> and <!-- meta:end --> in index.html (Japanese metadata + hreflang),
  - writes /en/ /id/ /vi/ /zh/ /zh-tw/ /ko/ index.html from it: that language's metadata, absolute asset paths,
    and the page text filled in from i18n.js so crawlers and link previews see that language,
  - writes sitemap.xml with the language alternates.
Run after editing index.html, i18n.js or _tools/meta.json:  python3 _tools/build_lang_pages.py
Open Graph images (og/og-<lang>.png) come from _tools/build_og_images.sh.
"""
import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://aunjapanese.com"
META = json.loads((ROOT / "_tools/meta.json").read_text(encoding="utf-8"))
T = json.loads(subprocess.run(
    ["node", "-e", 'global.window={};require("./i18n.js");process.stdout.write(JSON.stringify(window.AUN_I18N))'],
    cwd=ROOT, check=True, capture_output=True, text=True).stdout)
START, END = "<!-- meta:start -->", "<!-- meta:end -->"


def head_block(lang: str) -> str:
    m = META[lang]
    url = SITE + m["path"]
    e = lambda s: html.escape(s, quote=True)
    alts = "\n".join(f'<link rel="alternate" hreflang="{v["hreflang"]}" href="{SITE}{v["path"]}" data-lang="{k}">' for k, v in META.items())
    others = "\n".join(f'<meta property="og:locale:alternate" content="{v["locale"]}">' for k, v in META.items() if k != lang)
    return f"""{START}
<title>{e(m["title"])}</title>
<meta name="description" content="{e(m["desc"])}">
<link rel="canonical" href="{url}">
{alts}
<link rel="alternate" hreflang="x-default" href="{SITE}/en/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="阿吽 AUN">
<meta property="og:title" content="{e(m["ogTitle"])}">
<meta property="og:description" content="{e(m["ogDesc"])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{m["locale"]}">
{others}
<meta property="og:image" content="{SITE}/og/og-{lang.lower()}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F0F0F">
{END}"""


def fill_text(s: str, d: dict) -> str:
    """Put each language's text into the empty data-i / data-i-html elements (app.js keeps redrawing them)."""
    def one(mt):
        tag, is_html, key, close = mt.group(1), mt.group(2), mt.group(3), mt.group(4)
        v = d.get(key, "")
        return tag + (v if is_html else html.escape(v)) + close
    return re.sub(r'(<[^>]*?\sdata-i(-html)?="([\w-]+)"[^>]*>)(</)', one, s)


def absolute_paths(s: str) -> str:
    return re.sub(r'\b(src|href)="(?!https?:|/|#|mailto:|data:|tel:)([^"]+)"', r'\1="/\2"', s)


src = (ROOT / "index.html").read_text(encoding="utf-8")
if START not in src:
    raise SystemExit("index.html has no meta markers")
src = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: head_block("ja"), src, flags=re.S)
(ROOT / "index.html").write_text(src, encoding="utf-8")

for lang, m in META.items():
    if lang == "ja":
        continue
    page = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: head_block(lang), src, flags=re.S)
    page = page.replace('<html lang="ja">', f'<html lang="{lang}" data-fixed-lang="{lang}">', 1)
    page = absolute_paths(page)
    page = fill_text(page, T[lang])
    out = ROOT / m["path"].strip("/") / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))

# sitemap: the landing page in every language (with alternates) + the legal pages
sm = re.sub(r"<lastmod>.*?</lastmod>", "", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
others = [u for u in re.findall(r"<loc>(.*?)</loc>", sm) if u.rstrip("/") != SITE]
alts = "".join(f'<xhtml:link rel="alternate" hreflang="{v["hreflang"]}" href="{SITE}{v["path"]}"/>' for v in META.values())
alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/"/>'
urls = "".join(f"<url><loc>{SITE}{v['path']}</loc>{alts}</url>\n" for v in META.values())
urls += "".join(f"<url><loc>{u}</loc></url>\n" for u in others)
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n", encoding="utf-8")
print("wrote sitemap.xml")
