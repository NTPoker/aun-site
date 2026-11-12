#!/usr/bin/env python3
"""Build the long-form articles: how-it-works.html (the test, in detail) and scoring.html (how results are decided).

Text first, with a few pictures. Each page holds Japanese and English (other site languages see English), like the
legal pages. The phone pictures come from _tools/index.src.html filled from i18n.js, so they match the landing page.
Every statement must be true of the shipped product: check app/web/kaiwa_web (exam.py, s_exam.py, account.py,
instant.py) and docs 70/72/73 in the kaiwa repo before changing a fact.
Run after editing this file, _tools/index.src.html or i18n.js:  python3 _tools/build_articles.py
"""
import html, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://aunjapanese.com"
PUBLISHED = "2026-11-12"
UPDATED = {"iso": "2026-11-12", "ja": "2026年11月12日", "en": "12 November 2026"}
T = json.loads(subprocess.run(
    ["node", "-e", 'global.window={};require("./i18n.js");process.stdout.write(JSON.stringify(window.AUN_I18N))'],
    cwd=ROOT, check=True, capture_output=True, text=True).stdout)
SRC = (ROOT / "_tools/index.src.html").read_text(encoding="utf-8")
LP = (ROOT / "ja/index.html").read_text(encoding="utf-8")
V = lambda name: re.search(re.escape(name) + r"\?v=([0-9a-z]+)", LP).group(1)
CSS_V = "20261112j"


def fill(s: str, d: dict) -> str:
    def one(m):
        tag, is_html, key, close = m.group(1), m.group(2), m.group(3), m.group(4)
        v = d.get(key, "")
        return re.sub(r'\sdata-i(-html)?="[\w-]+"', "", tag) + (v if is_html else html.escape(v)) + close
    return re.sub(r'(<[^>]*?\sdata-i(-html)?="([\w-]+)"[^>]*>)(</)', one, s)


def pictures(lang: str) -> list:
    """The three phone pictures of the landing page's steps, with this language's text."""
    pics = re.findall(r'<div class="lp-sv pz" data-a>.*?</div></div></div>(?=\n</article>)', SRC, flags=re.S)
    assert len(pics) == 3, len(pics)
    return [fill(p.replace(' data-a', ''), T[lang]).replace('src="listener-nt2.jpg"', 'src="/listener-nt2.jpg"') for p in pics]


SCORES = [4, 3, 3, 2, 3, 4]  # the same sample as the landing page's step 3 (next to fix: grammar)
HEX = ('<svg viewBox="30 20 240 260" aria-hidden="true"><polygon class="g" points="150.0,79.2 211.3,114.6 211.3,185.4 150.0,220.8 88.7,185.4 88.7,114.6"/>'
       '<polygon class="g" points="150.0,32.0 252.2,91.0 252.2,209.0 150.0,268.0 47.8,209.0 47.8,91.0"/>'
       '<polygon class="poly" points="150.0,55.6 211.3,114.6 211.3,185.4 150.0,197.2 88.7,185.4 68.2,102.8"/></svg>')
MARK = {"o": "○", "n": "△", "x": "×"}
SIX = {"ja": ["伝わる内容", "まとまり", "流暢さ", "文法", "語彙", "発音"],
       "en": ["Content", "Organisation", "Fluency", "Grammar", "Vocabulary", "Pronunciation"]}
SCENES = {"ja": [("自己紹介", "o", ""), ("雑談", "o", ""), ("電話で予約", "o", ""), ("接客", "n", "あと少し：文法"), ("面接", "n", "あと少し：文法"), ("打ち合わせ・会議", "x", "")],
          "en": [("Introducing yourself", "o", ""), ("Small talk", "o", ""), ("Booking by phone", "o", ""), ("Customer service", "n", "Almost: grammar"), ("Job interview", "n", "Almost: grammar"), ("Meetings", "x", "")]}
EG = {"ja": ("結果の例｜点は 0〜5", "結果の例｜場面は一部", "次に直す"), "en": ("Sample result | scores are 0 to 5", "Sample result | some of the situations", "Fix next")}


def cards(lang: str) -> str:
    six = "".join(f'<li{" class=nx" if SCORES[i] == min(SCORES) else ""}><b>{SCORES[i]}</b><strong>{n}</strong></li>' for i, n in enumerate(SIX[lang]))
    sc = "".join(f'<li class="{m}"><i>{MARK[m]}</i><strong>{n}</strong>{f"<span>{w}</span>" if w else ""}</li>' for n, m, w in SCENES[lang])
    e = EG[lang]
    return (f'<div class="hw-cards" aria-hidden="true"><div class="hw-card hw-sixc"><p class="hw-eg">{e[0]}</p><div class="hw-hex">{HEX}</div><ul class="hw-sixl">{six}</ul></div>'
            f'<div class="hw-card"><p class="hw-eg">{e[1]}</p><ul class="hw-scl">{sc}</ul><p class="hw-next"><span>{e[2]}</span><strong>{SIX[lang][3]}</strong></p></div></div>')


def fig(pic: str, cap: str) -> str:
    return f'<figure class="art-fig">{pic}<figcaption>{cap}</figcaption></figure>'


# ---------------------------------------------------------------------------------------------------------------------
# Article 1: the test, in detail
# ---------------------------------------------------------------------------------------------------------------------
HOW = {
"ja": dict(
    title="阿吽（AUN）とは：日本人が聞く、約10分の日本語スピーキングテスト",
    desc="阿吽（AUN）は、日本語を話す力を測る約10分のスピーキングテストです。誰に向くか、何を聞かれるか、AI の振り返りと日本人が聞いた結果に何が入っているか、料金、録音の扱いをまとめました。",
    kick="阿吽について", h1="阿吽（AUN）とは<br>日本人が聞く、約10分の日本語スピーキングテスト",
    cta="無料でテストを受ける", by="阿吽（AUN）運営・株式会社1900", upd="最終更新日",
    toc="この記事の内容", rel="あわせて読む", rel_link=("scoring.html", "阿吽の点の決まり方：6つの力と、0 から 5 の段"),
    body=None),
"en": dict(
    title="AUN Japanese speaking test: 10 minutes, scored by a Japanese listener",
    desc="AUN is a Japanese speaking test that takes about 10 minutes. Who it is for, what you are asked, what the AI review and the Japanese listener’s result contain, the price, and what happens to your recordings.",
    kick="About AUN", h1="What is AUN?<br>A 10-minute Japanese speaking test, scored by a Japanese listener",
    cta="Take the test free", by="AUN, run by 1900 Co., Ltd.", upd="Last updated",
    toc="In this article", rel="Read next", rel_link=("scoring.html", "How AUN results are decided: six skills, scored 0 to 5"),
    body=None),
}

# ---------------------------------------------------------------------------------------------------------------------
# Article 2: how results are decided
# ---------------------------------------------------------------------------------------------------------------------
LV = {
"ja": [
 ("伝わる内容", "聞かれたことに答えて、言いたいことがどこまで具体的に、正しく伝わったか。", ["単語から、話題がなんとなく分かる。中身は聞き手がかなり補う。", "言いたいことの中心（何を・どこで など）は分かるが、詳しいことは伝わらない。", "中心に加えて、理由や気持ち、いくつかの詳しいことが伝わる。ところどころ聞き手が補う。", "具体例や詳しいことまで、誤解なく伝わる。補う必要はほとんどない。", "細かいニュアンスや、条件・ただし書きまで正確に伝わる。"]),
 ("まとまり", "話の順番とつながりを、迷わずに追えるか。", ["単語や短い言葉がばらばら。つながりが追えない。", "「そして」「でも」などで、短い文を並べられる。", "出来事などを順番に、筋が追える形で話せる。", "理由・例・結論がはっきりつながり、聞き手が頭の中で並べ直さなくてよい。", "長い話でも組み立てがはっきりし、話の切り替えや要点のまとめも自然。"]),
 ("流暢さ", "止まらずに話し続けられるか。", ["一言ずつ。長く止まり、話がとぎれる。", "短い答えなら言える。止まりや言い直しは多いが、待てば分かる。", "間や言い直しはあるが、話は途切れずに続く。", "ほぼ会話のテンポ。迷っても、長く止まることは少ない。", "苦労なく、自然にすらすら。難しい話題でも流れが止まらない。"]),
 ("文法", "文を正しく組み立てられるか。どこまで複雑な文が言えるか。", ["ほとんど単語や決まった言い方を並べるだけ。", "短い文で言える。崩れは多いが、言いたいことは分かる。", "よく使う形で文をつなげて言える（〜て・〜から・〜とき）。崩れはときどきで、誤解にはならない。", "理由・条件・比べるなど、少し複雑な文も使える。誤解につながる崩れはほとんどない。", "複雑な文も正確に使い分ける。崩れはまれで、すぐ自分で直す。"]),
 ("語彙", "言いたいことに合う言葉が出るか。", ["決まった言葉しか出ず、言葉が出ずに止まる。", "身近なことを、よく使う簡単な言葉で言える。言葉が足りずに止まることがある。", "身近な話題なら、言いたい言葉がだいたい出る。出ない時も言い換えて続けられる。", "意見や説明に合う言葉が出て、くり返しが少ない。選び違いで誤解しそうになることはほとんどない。", "話題が広がっても言葉に困らない。言い回しを選び、細かい違いも言い分ける。"]),
 ("発音", "音が、聞き返さずに分かるか。", ["別の言葉に聞こえる所が多く、聞く側がかなり補う。", "聞き返したい所がときどきある。注意して聞けば分かる。", "だいたい楽に分かる。聞き返したい所はまれ。", "聞く側の負担はほとんどない。区切りや抑揚も分かりやすい。", "負担がない。抑揚で気持ちや強調も伝わる。"]),
],
"en": [
 ("Content", "Whether you answered the question, and how specifically and accurately your point came across.", ["The topic can be guessed from single words. The listener has to fill in most of the meaning.", "The core of what you mean (what, where and so on) is clear, but details do not come across.", "Beyond the core, reasons, feelings and some details come across. The listener fills in here and there.", "Examples and details come across without misunderstanding. Almost nothing needs filling in.", "Fine shades of meaning, conditions and caveats come across accurately."]),
 ("Organisation", "Whether the listener can follow the order of what you say and how the parts connect.", ["Words and short phrases are scattered. The connection cannot be followed.", "Short sentences are lined up with words like “and” and “but”.", "Events and the like are told in order, in a way that can be followed.", "Reasons, examples and conclusions connect clearly; the listener does not have to rearrange them.", "Even a long answer is clearly built, with natural shifts of topic and summing up."]),
 ("Fluency", "Whether you can keep talking without stopping.", ["One word at a time. Long stops; the talk breaks off.", "Short answers are possible. Many stops and restarts, but understandable if the listener waits.", "There are pauses and restarts, but the talk keeps going.", "Close to conversational pace. Even when unsure, long stops are rare.", "Effortless and natural. The flow does not stop even on difficult topics."]),
 ("Grammar", "Whether you build sentences correctly, and how complex a sentence you can say.", ["Mostly single words and fixed phrases put side by side.", "Short sentences. Many errors, but the meaning is clear.", "Sentences are joined with common forms (〜て, 〜から, 〜とき). Errors are occasional and do not cause misunderstanding.", "Somewhat complex sentences are used, such as reasons, conditions and comparisons. Errors that could mislead are rare.", "Complex sentences are used accurately. Errors are rare and quickly self-corrected."]),
 ("Vocabulary", "Whether you find words that fit what you want to say.", ["Only fixed words come out; you stop because words do not come.", "Familiar things can be said in common, simple words. You sometimes stop for lack of a word.", "On familiar topics, the words you need mostly come. When they do not, you rephrase and carry on.", "Words that fit opinions and explanations come out, with little repetition. Wrong word choices that could mislead are rare.", "You are not short of words even as the topic widens. You choose your wording and express fine differences."]),
 ("Pronunciation", "Whether your sounds can be understood without the listener asking again.", ["Many parts sound like other words; the listener has to fill in a lot.", "The listener sometimes wants to ask again, but can understand by listening carefully.", "Mostly easy to understand. The listener rarely wants to ask again.", "Almost no effort for the listener. Phrasing and intonation are easy to follow.", "No effort for the listener. Intonation carries feeling and emphasis."]),
],
}


def levels(lang: str) -> str:
    """One table per skill, levels 1 to 5 (level 0 is the same for every skill and is explained once in the text)."""
    out = []
    for name, what, rows in LV[lang]:
        trs = "".join(f"<tr><th>{i + 1}</th><td>{r}</td></tr>" for i, r in enumerate(rows))
        out.append(f'<h3>{name}</h3><p>{what}</p><table class="art-lv">{trs}</table>')
    return "\n".join(out)


SCORING = {
"ja": dict(
    title="阿吽の点の決まり方：6つの力と、0 から 5 の段",
    desc="阿吽（AUN）の結果がどう決まるかを説明します。6つの力（伝わる内容・まとまり・流暢さ・文法・語彙・発音）の 0〜5 がどんな話し方を指すか、日本人の聞き手がどう聞くか、場面の○△×の決まり方、AI の役割、限界。",
    kick="点の決まり方", h1="阿吽の点の決まり方<br>6つの力と、0 から 5 の段",
    cta="無料でテストを受ける", by="阿吽（AUN）運営・株式会社1900", upd="最終更新日",
    toc="この記事の内容", rel="あわせて読む", rel_link=("how-it-works.html", "阿吽（AUN）とは：日本人が聞く、約10分の日本語スピーキングテスト"),
    body=None),
"en": dict(
    title="How AUN results are decided: six skills, scored 0 to 5",
    desc="How results on the AUN Japanese speaking test are decided: what each level from 0 to 5 sounds like for the six skills, how the Japanese listener listens, how the ○△× marks for each situation are set, what the AI does, and the limits.",
    kick="How scoring works", h1="How AUN results are decided:<br>six skills, scored 0 to 5",
    cta="Take the test free", by="AUN, run by 1900 Co., Ltd.", upd="Last updated",
    toc="In this article", rel="Read next", rel_link=("how-it-works.html", "What is AUN? A 10-minute Japanese speaking test, scored by a Japanese listener"),
    body=None),
}


def label_cells(body: str) -> str:
    """Comparison tables: copy each column heading onto its cells (data-label), so phones can show a row as a stacked card."""
    def table(m):
        rows = re.findall(r"<tr>(.*?)</tr>", m.group(0), flags=re.S)
        heads = re.findall(r"<th>(.*?)</th>", rows[0])
        out = m.group(0)
        for r in rows[1:]:
            cells = re.findall(r"<td>(.*?)</td>", r, flags=re.S)
            new = r
            for h, c in zip(heads[1:], cells):
                new = new.replace(f"<td>{c}</td>", f'<td data-label="{html.escape(re.sub("<[^>]+>", "", h), quote=True)}">{c}</td>', 1)
            out = out.replace(r, new, 1)
        return out
    return re.sub(r'<table class="art-cmp[^"]*">.*?</table>', table, body, flags=re.S)


for _name, _c in (("how", HOW), ("scoring", SCORING)):   # the article text lives in _tools/articles/<name>.<lang>.html
    for _lang in ("ja", "en"):
        _c[_lang]["body"] = (ROOT / f"_tools/articles/{_name}.{_lang}.html").read_text(encoding="utf-8")


PREFIX = {"ja": "/ja/", "en": "/"}   # like the landing page: English at the root, Japanese under /ja/
ARTICLES = ("how-it-works.html", "scoring.html")


def link(href: str, lang: str) -> str:
    """Site-absolute link: the two articles live per language, everything else at the root."""
    if re.match(r"https?:|/|#|mailto:", href):
        return href
    return (PREFIX[lang] if href in ARTICLES else "/") + href


def toc(body: str, label: str) -> str:
    items = re.findall(r'<h2 id="([\w-]+)">(.*?)</h2>', body)
    return f'<nav class="art-toc" aria-label="{label}"><p>{label}</p><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>"


def section(c: dict, lang: str, extra: dict, other: str) -> str:
    body = c["body"]
    for k, v in extra.items():
        body = body.replace("{" + k + "}", v)
    assert not re.search(r"\{(?!TOC\})[A-Z0-9]+\}", body), re.findall(r"\{[A-Z0-9]+\}", body)
    body = label_cells(body)
    body = re.sub(r'<a href="([^"]+)"', lambda m: f'<a href="{link(m.group(1), lang)}"', body)
    t = toc(body, c["toc"])
    assert body.count("{TOC}") == 1   # where the button and the contents list go: after the lead (and the facts table)
    body = body.replace("{TOC}", f'<p class="art-ctaw"><a href="/test.html" class="lp-cta">{c["cta"]}</a></p>\n' + t)
    return f'''<article class="art" lang="{lang}">
<header class="art-head">
<p class="lp-kick">{c["kick"]}</p>
<h1>{c["h1"]}</h1>
<p class="art-meta">{c["by"]}　｜　{c["upd"]}：<time datetime="{UPDATED["iso"]}">{UPDATED[lang]}</time>　｜　<a href="{other}" hreflang="{"en" if lang == "ja" else "ja"}" lang="{"en" if lang == "ja" else "ja"}">{"English" if lang == "ja" else "日本語"}</a></p>
</header>
{body}
<aside class="art-rel"><p>{c["rel"]}</p><a href="{link(c["rel_link"][0], lang)}">{c["rel_link"][1]}</a></aside>
<p class="art-ctaw end"><a href="/test.html" class="lp-cta">{c["cta"]}</a></p>
</article>'''


OG_LOCALE = {"ja": "ja_JP", "en": "en_US"}
SITE_NAME = {"ja": "阿吽 AUN", "en": "AUN"}
OTHER_LANGS = ("id", "vi", "zh", "zh-TW", "ko")   # no article in these yet: the language picker sends them to the English one


def page(name: str, content: dict, extras) -> None:
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    e = lambda s: html.escape(s, quote=True)
    urls = {l: f"{SITE}{PREFIX[l]}{name}" for l in content}
    for lang, c in content.items():
        faq_html = re.search(r'<div class="art-faq">(.*?)</div>', c["body"], flags=re.S).group(1)
        faq = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", faq_html, flags=re.S)
        assert faq, (name, lang)
        url = urls[lang]
        home = SITE + PREFIX[lang]
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": c["title"], "description": c["desc"], "inLanguage": lang,
               "datePublished": PUBLISHED, "dateModified": UPDATED["iso"], "mainEntityOfPage": url, "image": f"{SITE}/og/og3-{lang}.png",
               "author": {"@type": "Organization", "name": "AUN (阿吽)", "url": SITE + "/"},
               "publisher": {"@type": "Organization", "name": "1900 Co., Ltd.", "alternateName": "株式会社1900", "url": SITE + "/about.html"}},
              {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang,
               "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faq]},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": SITE_NAME[lang], "item": home},
                  {"@type": "ListItem", "position": 2, "name": c["title"], "item": url}]}]
        head = LP.split("<title>")[0].split("<!-- meta:start -->")[0]
        # Japanese is its own page (fixed). The English page also serves the languages that have no article, so the
        # header keeps the visitor's language. No automatic redirect: each address always shows its own language (a link under the title leads to the other).
        attrs = 'lang="ja" data-fixed-lang="ja"' if lang == "ja" else 'lang="en"'
        head = re.sub(r"<html[^>]*>", f"<html {attrs}>", head)
        head = re.sub(r"<!-- 生成ファイル.*?-->", "<!-- 生成ファイル（_tools/build_articles.py）。直すのは _tools/build_articles.py と _tools/articles/ -->", head)
        alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{u}" data-lang="{l}">\n' for l, u in urls.items())
        alts += f'<link rel="alternate" hreflang="x-default" href="{urls["en"]}">\n'
        if lang == "ja":   # for the language picker only (no hreflang: these are not translations)
            alts += "".join(f'<link rel="alternate" href="{urls["en"]}" data-lang="{l}">\n' for l in OTHER_LANGS)
        out = head + f'''<title>{e(c["title"])}｜{SITE_NAME[lang]}</title>
<meta name="description" content="{e(c["desc"])}">
<link rel="canonical" href="{url}">
{alts}<meta property="og:type" content="article">
<meta property="og:site_name" content="{SITE_NAME[lang]}">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
<meta property="og:title" content="{e(c["title"])}">
<meta property="og:description" content="{e(c["desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og/og3-{lang}.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F0F0F">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=Zen+Old+Mincho:wght@700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
<link rel="stylesheet" href="/lp.css?v={V("lp.css")}">
<link rel="stylesheet" href="/site.css?v={V("site.css")}">
<link rel="stylesheet" href="/how.css?v={CSS_V}">
</head>
<body class="lp hw">
<header id="site-top" class="s-top"></header><script src="/site.js?v={V("site.js")}"></script>
<main>
{section(c, lang, extras(lang), PREFIX["en" if lang == "ja" else "ja"] + name)}
</main>
<footer id="site-foot" class="s-foot"></footer>
<script type="module" src="/art.js?v=20261112d"></script>
</body>
</html>
'''
        dest = ROOT / PREFIX[lang].strip("/") / name
        dest.write_text(out, encoding="utf-8")
        n = len(strip(c["body"])) if lang == "ja" else len(strip(c["body"]).split())
        print(f"wrote {dest.relative_to(ROOT)}: {len(out)} bytes, {n} {'chars' if lang == 'ja' else 'words'}")


def sitemap() -> None:
    """The articles, each language with its alternates (build_lang_pages.py keeps whatever else is listed)."""
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sm = re.sub(r"<url><loc>[^<]*/(?:" + "|".join(re.escape(a) for a in ARTICLES) + r")</loc>.*?</url>\n", "", sm)
    add = ""
    for name in ARTICLES:
        urls = {l: f"{SITE}{PREFIX[l]}{name}" for l in PREFIX}
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for l, u in urls.items())
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{urls["en"]}"/>'
        add += "".join(f"<url><loc>{u}</loc><lastmod>{UPDATED['iso']}</lastmod>{alts}</url>\n" for u in urls.values())
    (ROOT / "sitemap.xml").write_text(sm.replace("</urlset>", add + "</urlset>"), encoding="utf-8")
    print("updated sitemap.xml")


CAP = {"ja": ["テスト中の画面。答えに足りない所があると、AI が聞き返します。", "AI の振り返りの例。伝わりにくいかもしれない所と、言い換えの例。", "日本人が聞いた結果の例。話せる場面と、6つの力の点。"],
       "en": ["The test screen. If something is missing from an answer, the AI asks a follow-up.", "A sample AI review: a place that may have been hard to understand, and another way to say it.", "A sample result from the Japanese listener: a situation you can handle, and six scores."]}


def how_extras(lang):
    p = pictures(lang)
    return {"PIC1": fig(p[0], CAP[lang][0]), "PIC2": fig(p[1], CAP[lang][1]), "PIC3": fig(p[2], CAP[lang][2]), "CARDS": cards(lang)}


page("how-it-works.html", HOW, how_extras)
page("scoring.html", SCORING, lambda lang: {"LEVELS": levels(lang), "CARDS": cards(lang)})
sitemap()
