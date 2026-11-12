#!/usr/bin/env python3
"""Build how-it-works.html (テストの中身): a picture-first page of facts about the test, in Japanese and English.

The three phone pictures are taken from _tools/index.src.html (the landing page's steps) and filled from i18n.js,
so they stay the same as the landing page. Everything else is written here. Other site languages see English.
Run after editing this file, _tools/index.src.html or i18n.js:  python3 _tools/build_how.py
"""
import html, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = json.loads(subprocess.run(
    ["node", "-e", 'global.window={};require("./i18n.js");process.stdout.write(JSON.stringify(window.AUN_I18N))'],
    cwd=ROOT, check=True, capture_output=True, text=True).stdout)
SRC = (ROOT / "_tools/index.src.html").read_text(encoding="utf-8")
LP = (ROOT / "ja/index.html").read_text(encoding="utf-8")
V = lambda name: re.search(re.escape(name) + r"\?v=([0-9a-z]+)", LP).group(1)


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


C = {
    "ja": dict(
        kick="テストの中身", h1='約10分話すと、<br><em>これが届く。</em>',
        chips=["約10分", "声で答える", "いまは無料"], cta="無料でテストを受ける",
        steps=[
            ("話す", '声で答える。<br><em>約10分。</em>', "質問を聞いて、声で答えます。答えに合わせて、AI が聞き返したり、次の質問を変えたりします。"),
            ("すぐに", 'AI の<br><em>振り返り</em>が届く。', "聞き取った言葉、伝わりにくいかもしれない所、言い換えの例。点は出ません。"),
            ("数日で", '<em>日本人</em>が<br>聞いた結果が届く。', "頼むと、6つの力の点、話せる場面、次に直す所が届きます。頼めるのは週1回まで。"),
        ],
        sixK="見るもの", sixH='見るのは、<br><em>6つの力。</em>', sixS="それぞれ 0〜5 の点で返します。",
        six=[("伝わる内容", "言いたいことが、伝わったか"), ("まとまり", "話の順番を、追えるか"), ("流暢さ", "止まらずに、話せるか"),
             ("文法", "文を、組み立てられるか"), ("語彙", "合う言葉が、出るか"), ("発音", "聞き返さずに、分かるか")],
        scK="結果", scH='話せる場面が、<br><em>○△×でわかる。</em>', scEg="結果の例", scNext="次に直す",
        scenes=[("自己紹介", "o", ""), ("雑談", "o", ""), ("電話で予約", "o", ""), ("接客", "n", "あと少し：文法"), ("面接", "n", "あと少し：文法"), ("会議", "x", "")],
        scS="自己紹介、買い物、雑談、電話で予約、接客、面接、会議などの場面ごとに、○（困らずに話せる）・△（あと少し）・×（まだ）で返します。",
        moreH="くわしく",
        more=[
            ("どんな質問が出る？", "<p>マイクの確認と練習のあと、全員が同じ3問に答えます（自分のこと、お店で頼む、最近あった出来事）。その答えをもとに、残りが「標準の組」か「やさしい組」に決まります。</p><p>標準の組：よく食べる料理を説明する → 意見を言う → 反対の意見に答える → AI の聞き手と4問 → 少し込み入った話題について考えを話す。よく話せた人には、さらに2問あります。</p><p>やさしい組：好きな食べ物を話す → 意見を言う → AI の聞き手と4問 → 身近な話題について考えを話す。</p>"),
            ("1問の時間は？", "<p>答える時間の上限は、質問によって15〜75秒です。上限なので、話し終えたら次へ進めます。話す前の準備の時間は、質問によって0〜20秒です。</p><p>答えに足りない所があると、AI が聞き返すことがあります（1つの質問につき1回まで）。</p>"),
            ("日本人には、どう頼む？", "<p>テストのあとに頼みます。頼めるのは週1回まで、テストを受けてから14日以内です。いまは無料です。結果は数日で、アプリの記録か、メールに届きます。</p><p>聞くのは、阿吽 代表の難波です。日本語の先生ではなく、ふつうの日本人の耳で聞きます。</p>"),
            ("測らないものは？", "<p>聞き返しや確認などのやりとりと、敬語は測っていません。</p>"),
            ("点と場面の印は、どう読む？", "<p>その場面に必要な話す力の目安です。AI は下書きを作りますが、結果を決めるのは聞き手です。必要な力が今回の答えから見えなかった場面は、「判定できない」と出ます。</p>"),
            ("録音は、どうなる？", '<p>東京の Google Cloud に保存します。日本人に頼んだ回は結果が届いてから30日後、頼まなかった回は1年後に消します。頼んだのに結果を返せなかった回は、テストを受けた日から90日後に消します。採点の改善に使ってよいと選んだ回は、最長5年残します（あとで変えられます）。いつでも<a href="https://test.aunjapanese.com/account/delete">削除を頼めます</a>。くわしくは<a href="/privacy.html">プライバシーポリシー</a>へ。</p>'),
            ("運営は？", '<p>東京の株式会社1900が運営しています。<a href="/about.html">運営会社</a>／<a href="/contact.html">お問い合わせ</a></p>'),
        ],
        endH='<span class="nw">伝わりにくい所が、</span><br><em>わかる。</em>',
    ),
    "en": dict(
        kick="How the test works", h1='Talk for 10 minutes.<br><em>Here is what you get.</em>',
        chips=["About 10 minutes", "Answer by voice", "Free for now"], cta="Take the test free",
        steps=[
            ("Speak", 'Answer out loud.<br><em>About 10 minutes.</em>', "You hear a question and answer by voice. The AI asks follow-ups and adapts the next question to your answers."),
            ("Right away", 'You get an<br><em>AI review.</em>', "The words it heard, places that may have been hard to understand, and another way to say it. No scores."),
            ("In a few days", 'A result from a<br><em>Japanese listener.</em>', "If you ask, you get scores for six skills, the situations you can handle, and what to fix next. You can ask once a week."),
        ],
        sixK="What we look at", sixH='Six skills,<br><em>scored 0 to 5.</em>', sixS="Each skill gets its own score.",
        six=[("Content", "Did your point come across?"), ("Organisation", "Can the listener follow the order?"), ("Fluency", "Can you keep talking?"),
             ("Grammar", "Can you build the sentence?"), ("Vocabulary", "Do the right words come out?"), ("Pronunciation", "Is it clear without asking again?")],
        scK="Your result", scH='See which situations<br><em>you can handle.</em>', scEg="Sample result", scNext="Fix next",
        scenes=[("Introducing yourself", "o", ""), ("Small talk", "o", ""), ("Booking by phone", "o", ""), ("Serving customers", "n", "Almost: grammar"), ("Job interview", "n", "Almost: grammar"), ("Meeting", "x", "")],
        scS="For situations such as introducing yourself, shopping, small talk, booking by phone, serving customers, a job interview and a meeting, you get ○ (you can handle it), △ (almost) or × (not yet).",
        moreH="Details",
        more=[
            ("What questions are asked?", "<p>After a microphone check and one practice question, everyone answers the same three questions (about yourself, asking for something in a shop, something that happened recently). Based on those answers, the rest of the test is either the standard set or the easier set.</p><p>Standard set: explain a dish you often eat → give an opinion → respond to the opposite view → four questions from an AI interviewer → give your thinking on a more complex topic. People who handle that well get two more questions.</p><p>Easier set: talk about a food you like → give an opinion → four questions from an AI interviewer → give your thinking on an everyday topic.</p>"),
            ("How long is each answer?", "<p>The time limit for an answer is 15 to 75 seconds, depending on the question. It is only an upper limit: when you finish speaking, you move on. Preparation time before you speak is 0 to 20 seconds, depending on the question.</p><p>If something is missing from an answer, the AI may ask a follow-up (at most one per question).</p>"),
            ("How do I ask for a Japanese listener?", "<p>You ask after the test. You can ask once a week, within 14 days of taking the test. It is free for now. The result arrives in a few days, on the Record screen in the app or by email.</p><p>The listener is Namba, the founder of AUN. He is not a Japanese teacher; he listens the way an ordinary Japanese person would.</p>"),
            ("What is not measured?", "<p>Back-and-forth, such as asking again or checking, and keigo (polite language) are not measured.</p>"),
            ("How should I read the scores and marks?", "<p>They are a guide to the speaking each situation needs. The AI prepares a draft, but the listener decides the result. If your answers did not show a skill that a situation needs, that situation is marked “cannot judge”.</p>"),
            ("What happens to my recordings?", '<p>They are stored on Google Cloud in Tokyo. If you asked for a listener, the recording is deleted 30 days after your result arrives; if you did not, after one year. If you asked but we could not send a result, it is deleted 90 days after the test. If you chose to let us use a recording to improve scoring, it is kept for up to five years (you can change this later). You can <a href="https://test.aunjapanese.com/account/delete">ask us to delete it</a> at any time. See the <a href="/privacy.html">Privacy Policy</a>.</p>'),
            ("Who runs it?", '<p>AUN is run by 1900 Co., Ltd., a company in Tokyo. <a href="/about.html">About us</a> / <a href="/contact.html">Contact</a></p>'),
        ],
        endH='Find out what was<br><em>hard to understand.</em>',
    ),
}
MARK = {"o": "○", "n": "△", "x": "×"}
HEX = ('<svg viewBox="30 20 240 260" aria-hidden="true"><polygon class="g" points="150.0,79.2 211.3,114.6 211.3,185.4 150.0,220.8 88.7,185.4 88.7,114.6"/>'
       '<polygon class="g" points="150.0,32.0 252.2,91.0 252.2,209.0 150.0,268.0 47.8,209.0 47.8,91.0"/>'
       '<polygon class="poly" points="150.0,55.6 211.3,114.6 211.3,185.4 150.0,197.2 88.7,185.4 68.2,102.8"/></svg>')
SCORES = [4, 3, 3, 2, 3, 4]  # the same sample as the landing page's step 3 (next to fix: grammar)


def section(lang: str) -> str:
    c, pics = C[lang], pictures(lang)
    steps = "\n".join(
        f'<article class="lp-step"><div class="lp-st"><p class="lp-sl"><b>{i + 1}</b><span>{l}</span></p><h3>{h}</h3><p class="lp-sd">{d}</p></div>\n{pics[i]}\n</article>'
        for i, (l, h, d) in enumerate(c["steps"]))
    six = "".join(f'<li{" class=nx" if SCORES[i] == min(SCORES) else ""}><b>{SCORES[i]}</b><strong>{n}</strong><span>{d}</span></li>' for i, (n, d) in enumerate(c["six"]))
    scenes = "".join(f'<li class="{m}"><i>{MARK[m]}</i><strong>{n}</strong>{f"<span>{w}</span>" if w else ""}</li>' for n, m, w in c["scenes"])
    more = "\n".join(f"<details><summary>{q}</summary>{a}</details>" for q, a in c["more"])
    chips = "".join(f"<li>{x}</li>" for x in c["chips"])
    return f'''<div data-l="{lang}" lang="{lang}">
<section class="lp-sec hw-hero"><div class="hw-in">
<p class="lp-kick">{c["kick"]}</p>
<h1 class="lp-cap">{c["h1"]}</h1>
<ul class="hw-chips">{chips}</ul>
<a href="/test.html" class="lp-cta">{c["cta"]}</a>
</div></section>
<section class="lp-sec lp-method"><div class="hw-in">
<div class="lp-steps">
{steps}
</div>
</div></section>
<section class="lp-sec hw-six"><div class="hw-in">
<p class="lp-kick">{c["sixK"]}</p>
<h2 class="lp-cap">{c["sixH"]}</h2>
<div class="hw-card hw-sixc"><p class="hw-eg">{c["scEg"]}</p><div class="hw-hex">{HEX}</div><ul class="hw-sixl">{six}</ul></div>
<p class="hw-note">{c["sixS"]}</p>
</div></section>
<section class="lp-sec lp-method hw-sc"><div class="hw-in">
<p class="lp-kick">{c["scK"]}</p>
<h2 class="lp-cap">{c["scH"]}</h2>
<div class="hw-card"><p class="hw-eg">{c["scEg"]}</p><ul class="hw-scl">{scenes}</ul><p class="hw-next"><span>{c["scNext"]}</span><strong>{c["six"][3][0]}</strong></p></div>
<p class="hw-note">{c["scS"]}</p>
</div></section>
<section class="lp-sec lp-more"><div class="hw-in">
<div class="lp-faq"><h2>{c["moreH"]}</h2>
{more}
</div>
</div></section>
<section class="lp-sec lp-end"><div class="hw-in">
<h2 class="lp-cap">{c["endH"]}</h2>
<a href="/test.html" class="lp-cta">{c["cta"]}</a>
</div></section>
</div>'''


faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "ja",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in C["ja"]["more"]]}
head = LP.split("<title>")[0].split("<!-- meta:start -->")[0]
head = re.sub(r"<html[^>]*>", '<html lang="ja">', head)
head = re.sub(r"<!-- 生成ファイル.*?-->", "<!-- 生成ファイル（_tools/build_how.py）。直すのは _tools/build_how.py -->", head)
page = head + f'''<title>テストの中身 — 阿吽 AUN｜日本語スピーキングテスト</title>
<meta name="description" content="阿吽（AUN）は約10分の日本語スピーキングテストです。声で答えると、すぐに AI の振り返りが届き、頼めば日本人が録音を聞いて、6つの力の点と、話せる場面を返します。">
<link rel="canonical" href="https://aunjapanese.com/how-it-works.html">
<meta property="og:type" content="article">
<meta property="og:site_name" content="阿吽 AUN">
<meta property="og:title" content="阿吽（AUN）のテストの中身">
<meta property="og:description" content="約10分の日本語スピーキングテスト。何を聞かれ、誰が聞き、何が届くか。">
<meta property="og:url" content="https://aunjapanese.com/how-it-works.html">
<meta property="og:image" content="https://aunjapanese.com/og/og3-ja.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F0F0F">
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=Zen+Old+Mincho:wght@700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
<link rel="stylesheet" href="/lp.css?v={V("lp.css")}">
<link rel="stylesheet" href="/site.css?v={V("site.css")}">
<link rel="stylesheet" href="/how.css?v=20261112a">
</head>
<body class="lp hw">
<header id="site-top" class="s-top"></header><script src="/site.js?v={V("site.js")}"></script>
<main>
{section("ja")}
{section("en")}
</main>
<footer id="site-foot" class="s-foot"></footer>
<script src="/legal.js?v=20261103q"></script>
</body>
</html>
'''
(ROOT / "how-it-works.html").write_text(page, encoding="utf-8")
print("wrote how-it-works.html", len(page))
