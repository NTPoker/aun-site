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
UPDATED = {"iso": "2026-11-12", "ja": "2026年11月12日", "en": "12 November 2026"}
T = json.loads(subprocess.run(
    ["node", "-e", 'global.window={};require("./i18n.js");process.stdout.write(JSON.stringify(window.AUN_I18N))'],
    cwd=ROOT, check=True, capture_output=True, text=True).stdout)
SRC = (ROOT / "_tools/index.src.html").read_text(encoding="utf-8")
LP = (ROOT / "ja/index.html").read_text(encoding="utf-8")
V = lambda name: re.search(re.escape(name) + r"\?v=([0-9a-z]+)", LP).group(1)
CSS_V = "20261112f"


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
    title="阿吽（AUN）とは？ 約10分の日本語スピーキングテストの中身",
    desc="阿吽（AUN）は、日本語を話す力を測る約10分のスピーキングテストです。誰に向くか、何を聞かれるか、AI の振り返りと日本人が聞いた結果に何が入っているか、料金、録音の扱いをまとめました。",
    kick="テストの中身", h1="阿吽（AUN）とは？<br>約10分の日本語スピーキングテストの中身",
    cta="無料でテストを受ける", by="阿吽（AUN）運営・株式会社1900", upd="最終更新日",
    toc="この記事の内容", rel="あわせて読む", rel_link=("scoring.html", "阿吽の点はどう決まる？ 6つの力と 0〜5 の読み方"),
    body="""
<p class="art-lead">阿吽（AUN）は、日本語を話す力を測るスピーキングテストです。スマホで約10分、質問を聞いて声で答えます。出した直後に AI の振り返りが届きます。頼めば、日本人があなたの録音を聞いて、6つの力の点と、困らずに話せる場面を返します。</p>
<p>日本語能力試験（JLPT）には、話す試験がありません。阿吽は、読む・聞くはできるのに話すのに自信がない人が、話す力を日本人の耳で確かめるためのテストです。</p>

<table class="art-facts">
<tr><th>測るもの</th><td>日本語を話す力（6つの力：伝わる内容・まとまり・流暢さ・文法・語彙・発音）</td></tr>
<tr><th>時間</th><td>約10分</td></tr>
<tr><th>答え方</th><td>声で答えます。書く問題、選ぶ問題はありません。</td></tr>
<tr><th>受ける場所</th><td>スマホのブラウザ、またはアプリ（iPhone・Android）</td></tr>
<tr><th>すぐ届くもの</th><td>AI の振り返り（聞き取った言葉、伝わりにくいかもしれない所。点は出ません）</td></tr>
<tr><th>頼むと届くもの</th><td>日本人が聞いた結果（6つの力の点 0〜5、場面ごとの○△×、次に直す所）。週1回まで、数日で届きます。</td></tr>
<tr><th>料金</th><td>いまは無料です（先着順）。</td></tr>
<tr><th>運営</th><td>株式会社1900（東京・銀座）</td></tr>
</table>

<h2 id="who">誰のためのテストですか？</h2>
<p>「自分の日本語は、日本人に本当に伝わっているのか」を知りたい人のためのテストです。読む・聞くの試験では分からない、話す力の今の位置を見ます。</p>
<div class="art-two">
<div class="art-box"><h3>向いている人</h3><ul>
<li>読む・聞くはできるのに、話すのに自信がない人</li>
<li>日本で働く、面接を受ける、留学する予定があり、いまの話す力を知りたい人</li>
<li>日本人の友だちや先生に「上手ですね」と言われるが、どこが伝わっていないのかを知りたい人</li>
<li>次に何を直せばいいかを、1つに絞りたい人</li>
<li>前より話せるようになったかを、同じ物差しで確かめたい人</li>
</ul></div>
<div class="art-box no"><h3>向いていない人</h3><ul>
<li>ビザや入学、就職の出願に出す、公的な証明が必要な人（阿吽の結果は、いまは公的な証明として使えません）</li>
<li>読む・聞く・書く力を測りたい人</li>
<li>単語や文法を教える教材、会話の練習相手を探している人</li>
<li>日本語を始めたばかりで、短い文もまだ言えない人（受けることはできますが、分かることは少なくなります）</li>
</ul></div>
</div>

<h2 id="what">何が分かりますか？</h2>
<p>分かることは3つです。</p>
<ol>
<li><strong>いまの位置</strong>：自己紹介、雑談、面接、会議など、どの場面なら日本人と困らずに話せるか。</li>
<li><strong>次に直す所</strong>：話せる場面を増やすために、6つの力のうち先に直すとよいものを1つ。</li>
<li><strong>前との違い</strong>：日本人が聞いた結果が2回分あると、アプリの「記録」で、6つの力の点が前回からどう変わったかが見られます。</li>
</ol>
<p>点の決まり方と、0〜5 のそれぞれが指す話し方は、<a href="scoring.html">阿吽の点はどう決まる？</a>にまとめています。</p>

<h2 id="flow">テストはどう進みますか？</h2>
{PIC1}
<p>質問は日本語の音声と文字で出ます。あなたは声で答えます。流れは次のとおりです。</p>
<ol>
<li>マイクの確認をして、練習を1問します。</li>
<li>全員が同じ3問に答えます：自分のこと、お店で頼む、最近あった出来事。</li>
<li>ここまでの答えをもとに、残りの質問が「標準の組」か「やさしい組」に決まります。</li>
</ol>
<div class="art-scroll"><table class="art-cmp art-sets">
<tr><th>残りの質問</th><th>標準の組</th><th>やさしい組</th></tr>
<tr><th>説明する</th><td>よく食べる料理を、食べたことがない人に説明する</td><td>好きな食べ物を話す</td></tr>
<tr><th>意見を言う</th><td>意見を言い、そのあと反対の意見に答える</td><td>意見と理由を言う</td></tr>
<tr><th>AI の聞き手と話す</th><td>あなたの答えを受けて、4問</td><td>あなたの答えを受けて、やさしい言葉で4問</td></tr>
<tr><th>考えを話す</th><td>少し込み入った話題。よく話せた人には、さらに2問</td><td>身近な話題。意見がよく言えた人は、標準の組の話題に変わります</td></tr>
</table></div>
<table>
<tr><th>答える時間</th><td>質問によって15〜75秒。上限なので、話し終えたら次へ進めます。</td></tr>
<tr><th>準備の時間</th><td>質問によって0〜20秒。すぐ話しはじめてもかまいません。</td></tr>
<tr><th>AI の聞き返し</th><td>答えに足りない所があると、AI が聞き返すことがあります（1つの質問につき1回まで。例：「それで、どうなりましたか。」）。</td></tr>
<tr><th>AI が作る質問</th><td>反対の意見の質問と、AI の聞き手の質問は、あなたの答えに合わせて AI が作ります。</td></tr>
</table>
<p>質問を2つの組に分けるのは、始めたばかりの人に難しすぎる質問を出さず、よく話せる人には力を見せる機会を出すためです。</p>

<h2 id="ai">出した直後に、何が届きますか？</h2>
{PIC2}
<p>テストを出すと、その場で AI の振り返りが届きます。入っているのは次の3つです。</p>
<ul>
<li>AI が聞き取った、あなたの言葉（質問ごと）</li>
<li>伝わりにくいかもしれない所と、その理由（最大3か所）</li>
<li>言いたいことが1つに決まる時は、言い換えの例</li>
</ul>
<p>AI の振り返りに、点は出ません。AI は聞き取りを間違えることがあるので、「伝わりにくいかもしれない所」として出しています。点と場面は、日本人が聞いた結果で返します。</p>

<h2 id="human">日本人が聞いた結果には、何が入っていますか？</h2>
{PIC3}
<p>テストのあとに頼むと、日本人があなたの録音を聞いて、結果を返します。入っているのは次の3つです。</p>
{CARDS}
<ul>
<li><strong>6つの力の点</strong>：伝わる内容・まとまり・流暢さ・文法・語彙・発音を、それぞれ 0〜5 で。</li>
<li><strong>場面ごとの目安</strong>：生活・人づきあい・仕事・学校の13の場面（自己紹介、買い物、役所・病院、電話で予約、雑談、遊びの相談、飲み会で話す、指示を受けて動く、接客、面接、打ち合わせ・会議、授業で発言、ゼミで議論）ごとに、○（困らずに話せる）・△（あと少し）・×（まだ）。</li>
<li><strong>次に直す所</strong>：6つの力のうち1つ。いまの話し方と、1つ上の段の話し方も示します。</li>
</ul>
<table>
<tr><th>頼める回数</th><td>週1回まで</td></tr>
<tr><th>頼める期間</th><td>テストを受けてから14日以内</td></tr>
<tr><th>届くまで</th><td>数日。受け付けた順に聞くので、混んでいる時は延びます。届く見込みの日は、頼んだ時に表示します。</td></tr>
<tr><th>届く場所</th><td>アプリの「記録」、またはメール</td></tr>
<tr><th>料金</th><td>いまは無料です。</td></tr>
</table>

<h2 id="listener">誰が聞くのですか？</h2>
<p>聞くのは、阿吽 代表の難波です。日本語の先生ではありません。ふつうの日本人が聞いて分かるか、という耳で聞きます。</p>
<p>聞き方には決まりがあります。録音は止めずに1回聞き、聞き直しは2回までです。質問ごとに、見る力を先に決めてあり、段ごとの説明と例に照らして、いちばん近い段を選びます。AI は聞き取った言葉と下書きを用意しますが、結果を決めるのは聞き手です。</p>

<h2 id="compare">ほかの方法と、何が違いますか？</h2>
<p>日本語の話す力を知る方法は、ほかにもあります。目的に合うものを選んでください。</p>
<div class="art-scroll"><table class="art-cmp">
<tr><th>方法</th><th>分かること</th><th>気をつける所</th></tr>
<tr><th>読む・聞くの試験（日本語能力試験 JLPT、JFT-Basic など）</th><td>読む力、聞く力。出願や在留資格で広く使われています。</td><td>話す試験はありません。</td></tr>
<tr><th>試験官と話す会話テスト</th><td>人とのやりとりを含めた話す力。証明として使えるものもあります。</td><td>予約が要り、費用と時間がかかります。</td></tr>
<tr><th>AI だけで採点する会話テスト</th><td>すぐに出る点。何度でも受けやすい。</td><td>日本人が実際に聞いて分かるか、とは別の物差しです。</td></tr>
<tr><th>AI の会話アプリ、先生のレッスン</th><td>話す練習と、その場の直し。</td><td>いまの位置を、同じ物差しで測るものではありません。</td></tr>
<tr><th>阿吽（AUN）</th><td>日本人が録音を聞いて分かるか。6つの力の点、話せる場面、次に直す所。</td><td>やりとりと敬語は測っていません。聞き手は、いまは1人です。</td></tr>
</table></div>

<h2 id="price">料金と、受け方は？</h2>
<p>いまは無料です（先着順）。スマホのブラウザから、そのまま受けられます。アプリ（<a href="https://apps.apple.com/app/id6831656467">iPhone</a>・<a href="https://play.google.com/store/apps/details?id=com.aunjapanese.app">Android</a>）で受けると、結果が届いた時に通知が来て、記録が残ります。</p>
<p>静かな場所で、マイクのあるスマホを用意してください。約10分、続けて話せる時間が必要です。</p>

<h2 id="privacy">録音は、どうなりますか？</h2>
<p>録音は、東京の Google Cloud に保存します。文字起こしと、AI の振り返り・下書きの作成には、OpenAI の API を使います（API で送ったデータは、同社の AI の学習には使われません）。消す時期は次のとおりです。</p>
<table>
<tr><th>日本人に頼んだ回</th><td>結果が届いてから30日後</td></tr>
<tr><th>頼まなかった回</th><td>1年後</td></tr>
<tr><th>頼んだのに結果を返せなかった回</th><td>テストを受けた日から90日後</td></tr>
<tr><th>採点の改善に使ってよいと選んだ回</th><td>最長5年（あとで変えられます）</td></tr>
</table>
<p>いつでも<a href="https://test.aunjapanese.com/account/delete">削除を頼めます</a>。くわしくは<a href="privacy.html">プライバシーポリシー</a>をご覧ください。</p>

<h2 id="limits">阿吽で分からないこと、まだ無いもの</h2>
<ul>
<li>聞き返しや確認などのやりとりと、敬語は測っていません。</li>
<li>結果は公的な証明ではありません。点と場面の印は、目安です。</li>
<li>聞き手は、いまは1人です。同じ人が2回受けた時に点がどれだけ動くか、などの調査結果は、まだ公表していません。</li>
<li>場面ごとの基準は、受けた人の結果を見ながら直していきます。</li>
</ul>

<h2 id="faq">よくある質問</h2>
<div class="lp-faq">
<details><summary>日本語能力試験（JLPT）の代わりになりますか？</summary><p>なりません。JLPT は読む力と聞く力の試験で、阿吽は話す力だけを見ます。JLPT には話す試験がないので、話す力を知るために、あわせて使えます。</p></details>
<details><summary>Duolingo English Test の日本語版のようなものですか？</summary><p>似ている所と、違う所があります。似ているのは、家からオンラインで短い時間で受けられる所です。違うのは、阿吽は日本語の話す力だけを見ること、点を決めるのが AI ではなく日本人の聞き手であること、結果が公的な証明ではないことです。</p></details>
<details><summary>何回でも受けられますか？</summary><p>テストは何回でも受けられ、毎回 AI の振り返りが届きます。日本人に聞いてもらえるのは、週1回までです。</p></details>
<details><summary>初級でも受けられますか？</summary><p>受けられます。最初の3問の答えをもとに、やさしい組の質問に切り替わります。</p></details>
<details><summary>AI が点を付けるのですか？</summary><p>付けません。受けた人に届く点は、日本人が録音を聞いて決めます。AI は、聞き取った言葉と下書きを用意し、テストの中で質問を作ります。</p></details>
<details><summary>結果を、履歴書や出願に使えますか？</summary><p>公的な証明としては使えません。自分の話す力を知り、次に直す所を決めるための結果です。</p></details>
</div>
"""),
"en": dict(
    title="What is AUN? Inside the 10-minute Japanese speaking test",
    desc="AUN is a Japanese speaking test that takes about 10 minutes. Who it is for, what you are asked, what the AI review and the Japanese listener’s result contain, the price, and what happens to your recordings.",
    kick="How the test works", h1="What is AUN?<br>Inside the 10-minute Japanese speaking test",
    cta="Take the test free", by="AUN, run by 1900 Co., Ltd.", upd="Last updated",
    toc="In this article", rel="Read next", rel_link=("scoring.html", "How AUN results are decided: six skills, scored 0 to 5"),
    body="""
<p class="art-lead">AUN (阿吽) is a test of spoken Japanese. You listen to questions on your phone and answer out loud, for about 10 minutes. Right after you submit, you get an AI review. If you ask, a Japanese person listens to your recording and sends back scores for six skills and the situations you can already handle.</p>
<p>The Japanese-Language Proficiency Test (JLPT) has no speaking section. AUN is for people who can read and listen but are not confident speaking, and who want a Japanese person’s ear on how well they speak.</p>

<table class="art-facts">
<tr><th>What it measures</th><td>Spoken Japanese, as six skills: content, organisation, fluency, grammar, vocabulary and pronunciation</td></tr>
<tr><th>Length</th><td>About 10 minutes</td></tr>
<tr><th>How you answer</th><td>By voice. There is no writing and no multiple choice.</td></tr>
<tr><th>Where</th><td>In your phone’s browser, or in the app (iPhone and Android)</td></tr>
<tr><th>Right away</th><td>An AI review: the words it heard and the places that may have been hard to understand. No scores.</td></tr>
<tr><th>If you ask</th><td>A result from a Japanese listener: six scores from 0 to 5, a ○△× mark for each situation, and what to fix next. Once a week; it arrives in a few days.</td></tr>
<tr><th>Price</th><td>Free for now (first come, first served).</td></tr>
<tr><th>Run by</th><td>1900 Co., Ltd. (Ginza, Tokyo)</td></tr>
</table>

<h2 id="who">Who is the test for?</h2>
<p>It is for people who want to know whether Japanese people really understand their spoken Japanese. It shows where your speaking is now, which reading and listening exams cannot tell you.</p>
<div class="art-two">
<div class="art-box"><h3>A good fit</h3><ul>
<li>You can read and listen, but you are not confident when you speak.</li>
<li>You plan to work, interview or study in Japan and want to know where your speaking stands.</li>
<li>Japanese friends and teachers say your Japanese is good, and you want to know what is actually not getting through.</li>
<li>You want one thing to fix next, not a long list.</li>
<li>You want to check, on the same scale, whether you speak better than before.</li>
</ul></div>
<div class="art-box no"><h3>Not a good fit</h3><ul>
<li>You need an official certificate for a visa, admission or a job application. AUN results cannot be used as official proof at this time.</li>
<li>You want to measure reading, listening or writing.</li>
<li>You are looking for vocabulary or grammar lessons, or a conversation partner to practise with.</li>
<li>You have just started and cannot yet say short sentences. You can still take the test, but it will tell you less.</li>
</ul></div>
</div>

<h2 id="what">What will you find out?</h2>
<p>Three things.</p>
<ol>
<li><strong>Where you are now</strong>: the situations, such as introducing yourself, small talk, a job interview or a meeting, in which you can talk with Japanese people without trouble.</li>
<li><strong>What to fix next</strong>: the one skill, out of six, to work on first in order to open up more situations.</li>
<li><strong>What has changed</strong>: once you have two results from a Japanese listener, the Record screen in the app shows how each of the six scores moved since last time.</li>
</ol>
<p>How the scores are decided, and what each level from 0 to 5 sounds like, is explained in <a href="scoring.html">How AUN results are decided</a>.</p>

<h2 id="flow">What happens in the test?</h2>
{PIC1}
<p>Each question is given in Japanese, as audio and text. You answer by voice. The test runs like this.</p>
<ol>
<li>You check your microphone and do one practice question.</li>
<li>Everyone answers the same three questions: about yourself, asking for something in a shop, and something that happened recently.</li>
<li>Based on those answers, the rest of the test is either the standard set or the easier set.</li>
</ol>
<div class="art-scroll"><table class="art-cmp art-sets">
<tr><th>The rest of the test</th><th>Standard set</th><th>Easier set</th></tr>
<tr><th>Explain</th><td>Explain a dish you often eat to someone who has never had it</td><td>Talk about a food you like</td></tr>
<tr><th>Give an opinion</th><td>Give an opinion, then respond to the opposite view</td><td>Give an opinion and a reason</td></tr>
<tr><th>Talk with an AI interviewer</th><td>Four questions based on your answers</td><td>Four questions based on your answers, in simple words</td></tr>
<tr><th>Give your thinking</th><td>A more complex topic; two more questions if you handle it well</td><td>An everyday topic. If your opinion answer went well, you get the standard topic instead</td></tr>
</table></div>
<table>
<tr><th>Answer time</th><td>15 to 75 seconds, depending on the question. It is an upper limit: when you finish speaking, you move on.</td></tr>
<tr><th>Preparation time</th><td>0 to 20 seconds, depending on the question. You can start speaking straight away.</td></tr>
<tr><th>AI follow-ups</th><td>If something is missing from an answer, the AI may ask a follow-up (at most one per question; for example, “And then what happened?”).</td></tr>
<tr><th>Questions written by AI</th><td>The opposite-view question and the AI interviewer’s questions are written by the AI to fit your answers.</td></tr>
</table>
<p>There are two sets so that beginners are not given questions that are too hard, and stronger speakers get the chance to show what they can do.</p>

<h2 id="ai">What do you get right after you submit?</h2>
{PIC2}
<p>As soon as you submit the test, you get an AI review. It contains three things.</p>
<ul>
<li>The words the AI heard you say, question by question</li>
<li>Places that may have been hard to understand, and why (up to three)</li>
<li>Another way to say it, when it is clear what you meant</li>
</ul>
<p>The AI review has no scores. The AI can mishear you, so these are shown as places that <em>may</em> have been hard to understand. Scores and situations come from the Japanese listener.</p>

<h2 id="human">What is in the Japanese listener’s result?</h2>
{PIC3}
<p>If you ask after the test, a Japanese person listens to your recording and sends back a result. It contains three things.</p>
{CARDS}
<ul>
<li><strong>Scores for six skills</strong>: content, organisation, fluency, grammar, vocabulary and pronunciation, each from 0 to 5.</li>
<li><strong>A guide by situation</strong>: 13 situations across daily life, socialising, work and school (introducing yourself, shopping, city office or hospital, booking by phone, small talk, making plans with friends, talking at a drinking party, following instructions at work, customer service, job interview, meetings, speaking up in class, seminar discussion), each marked ○ (you can handle it), △ (almost) or × (not yet).</li>
<li><strong>What to fix next</strong>: one of the six skills, with a description of how you speak now and how the next level up sounds.</li>
</ul>
<table>
<tr><th>How often</th><td>Once a week</td></tr>
<tr><th>When to ask</th><td>Within 14 days of taking the test</td></tr>
<tr><th>How long it takes</th><td>A few days. Recordings are listened to in the order received, so it takes longer when it is busy. You are shown the expected date when you ask.</td></tr>
<tr><th>Where it arrives</th><td>On the Record screen in the app, or by email</td></tr>
<tr><th>Price</th><td>Free for now.</td></tr>
</table>

<h2 id="listener">Who listens?</h2>
<p>The listener is Namba, the founder of AUN. He is not a Japanese teacher. He listens for whether an ordinary Japanese person would understand you.</p>
<p>There are rules for how he listens. He plays the recording once without stopping, and may replay it at most twice. For each question, the skills to look at are fixed in advance, and he chooses the closest level by comparing your answer with the written description and examples for each level. The AI prepares a transcript and a draft, but the listener decides the result.</p>

<h2 id="compare">How is it different from other options?</h2>
<p>There are other ways to find out how well you speak Japanese. Choose the one that fits your purpose.</p>
<div class="art-scroll"><table class="art-cmp">
<tr><th>Option</th><th>What it tells you</th><th>Keep in mind</th></tr>
<tr><th>Reading and listening exams (the Japanese-Language Proficiency Test (JLPT), JFT-Basic and others)</th><td>Reading and listening. Widely used for applications and visas.</td><td>They have no speaking section.</td></tr>
<tr><th>Interview tests with a live examiner</th><td>Speaking, including real back-and-forth. Some can be used as proof.</td><td>You need to book, and they cost more time and money.</td></tr>
<tr><th>Speaking tests scored only by AI</th><td>A score right away. Easy to retake.</td><td>It is a different yardstick from whether a Japanese person understands you.</td></tr>
<tr><th>AI conversation apps and lessons with a teacher</th><td>Practice, and corrections on the spot.</td><td>They do not measure where you are on a fixed scale.</td></tr>
<tr><th>AUN</th><td>Whether a Japanese person understands your recording: six scores, the situations you can handle, and what to fix next.</td><td>Back-and-forth and keigo are not measured. There is one listener at present.</td></tr>
</table></div>

<h2 id="price">What does it cost, and how do you take it?</h2>
<p>It is free for now (first come, first served). You can take it straight away in your phone’s browser. If you take it in the app (<a href="https://apps.apple.com/app/id6831656467">iPhone</a>, <a href="https://play.google.com/store/apps/details?id=com.aunjapanese.app">Android</a>), you get a notification when your result arrives, and your results are kept in one place.</p>
<p>Find a quiet place and use a phone with a working microphone. You need about 10 minutes in which you can speak without interruption.</p>

<h2 id="privacy">What happens to your recordings?</h2>
<p>Recordings are stored on Google Cloud in Tokyo. Transcription, the AI review and the draft are produced with the OpenAI API (data sent through the API is not used to train its models). Recordings are deleted as follows.</p>
<table>
<tr><th>You asked for a listener</th><td>30 days after your result arrives</td></tr>
<tr><th>You did not ask</th><td>After one year</td></tr>
<tr><th>You asked, but we could not send a result</th><td>90 days after the test</td></tr>
<tr><th>You chose to let us use it to improve scoring</th><td>Up to five years (you can change this later)</td></tr>
</table>
<p>You can <a href="https://test.aunjapanese.com/account/delete">ask us to delete them</a> at any time. See the <a href="privacy.html">Privacy Policy</a> for details.</p>

<h2 id="limits">What AUN does not tell you, and what we do not have yet</h2>
<ul>
<li>Back-and-forth, such as asking again or checking, and keigo (polite language) are not measured.</li>
<li>The result is not an official certificate. Scores and marks are a guide.</li>
<li>There is one listener at present. We have not yet published studies of, for example, how much a score moves when the same person takes the test twice.</li>
<li>The thresholds for each situation will be adjusted as we see more results.</li>
</ul>

<h2 id="faq">Frequently asked questions</h2>
<div class="lp-faq">
<details><summary>Can AUN replace the JLPT?</summary><p>No. The JLPT tests reading and listening; AUN looks only at speaking. The JLPT has no speaking section, so you can use AUN alongside it to find out how well you speak.</p></details>
<details><summary>Is it like a Japanese version of the Duolingo English Test?</summary><p>In some ways. Like it, AUN is short and taken online from home. Unlike it, AUN looks only at spoken Japanese, the scores are decided by a Japanese listener rather than by AI, and the result is not an official certificate.</p></details>
<details><summary>Can I take it as many times as I like?</summary><p>You can take the test as often as you like, and you get an AI review every time. You can ask for a Japanese listener once a week.</p></details>
<details><summary>Can beginners take it?</summary><p>Yes. Based on your first three answers, the test switches to the easier set of questions.</p></details>
<details><summary>Does AI give the scores?</summary><p>No. The scores you receive are decided by a Japanese person who listens to your recording. The AI prepares a transcript and a draft, and writes some of the questions during the test.</p></details>
<details><summary>Can I use the result on a CV or an application?</summary><p>Not as official proof. It is a result for understanding your own speaking and deciding what to fix next.</p></details>
</div>
"""),
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
    zero = {"ja": "判断できる話がほとんどない（無言、母語だけ、聞き取れない）。", "en": "Almost nothing to judge (silence, only your first language, or inaudible)."}[lang]
    out = []
    for name, what, rows in LV[lang]:
        trs = f"<tr><th>0</th><td>{zero}</td></tr>" + "".join(f"<tr><th>{i + 1}</th><td>{r}</td></tr>" for i, r in enumerate(rows))
        out.append(f'<h3>{name}</h3><p>{what}</p><table class="art-lv">{trs}</table>')
    return "\n".join(out)


SCORING = {
"ja": dict(
    title="阿吽の点はどう決まる？ 6つの力と 0〜5 の読み方",
    desc="阿吽（AUN）の結果がどう決まるかを説明します。6つの力（伝わる内容・まとまり・流暢さ・文法・語彙・発音）の 0〜5 がどんな話し方を指すか、日本人の聞き手がどう聞くか、場面の○△×の決まり方、AI の役割、限界。",
    kick="点の決まり方", h1="阿吽の点はどう決まる？<br>6つの力と 0〜5 の読み方",
    cta="無料でテストを受ける", by="阿吽（AUN）運営・株式会社1900", upd="最終更新日",
    toc="この記事の内容", rel="あわせて読む", rel_link=("how-it-works.html", "阿吽（AUN）とは？ 約10分の日本語スピーキングテストの中身"),
    body="""
<p class="art-lead">阿吽（AUN）の点は、日本人の聞き手があなたの録音を聞いて決めます。話す力を6つに分け、それぞれを 0〜5 の6段で見ます。この記事では、6つの力が何を指すか、各段がどんな話し方か、場面の○△×がどう決まるかを説明します。</p>

<table class="art-facts">
<tr><th>点を決める人</th><td>日本人の聞き手（阿吽 代表の難波）。AI は下書きを用意します。</td></tr>
<tr><th>見るもの</th><td>6つの力：伝わる内容・まとまり・流暢さ・文法・語彙・発音</td></tr>
<tr><th>点の幅</th><td>それぞれ 0〜5 の6段</td></tr>
<tr><th>場面の印</th><td>13の場面ごとに、○（困らずに話せる）・△（あと少し）・×（まだ）</td></tr>
<tr><th>測らないもの</th><td>聞き返しや確認などのやりとり、敬語</td></tr>
</table>

<h2 id="six">6つの力とは、何ですか？</h2>
<p>「日本語が話せる」を、聞き手が感じる6つの面に分けたものです。「伝わる内容」が結果で、ほかの5つはその原因にあたります。似た力は、次のように分けて見ます。</p>
<div class="art-scroll"><table class="art-cmp">
<tr><th>力</th><th>見るもの</th><th>含めないもの</th></tr>
<tr><th>伝わる内容</th><td>詳しさ、理由や気持ちが分かるか、誤解なく伝わったか</td><td>話の順番（まとまりで見ます）、意見の立派さ</td></tr>
<tr><th>まとまり</th><td>出来事の順番、「だから」「でも」などのつなぎ、理由・例・結論の筋道</td><td>1つ1つの文の正しさ（文法で見ます）</td></tr>
<tr><th>流暢さ</th><td>間の長さと数、言い直し、話す速さ</td><td>言葉が出ずに止まった時間（語彙で見ます）、音の分かりやすさ（発音で見ます）</td></tr>
<tr><th>文法</th><td>単語の並び → 短い文 → 文をつなぐ → 複雑な文。崩れで誤解しないか</td><td>言葉の選び方（語彙で見ます）。自然な省略では下げません</td></tr>
<tr><th>語彙</th><td>言葉の広さ、合う言葉を選べるか、言い換えられるか</td><td>文の組み立て（文法で見ます）</td></tr>
<tr><th>発音</th><td>別の言葉に聞こえないか、聞く側の負担、区切りや抑揚</td><td>間や速さ（流暢さで見ます）、なまりの強さそのもの</td></tr>
</table></div>

<h2 id="levels">0〜5 は、どんな話し方ですか？</h2>
<p>上の段は、下の段でできることを全部できます。段ごとの説明は次のとおりです。</p>
{LEVELS}
{CARDS}
<p>この段は、ヨーロッパの言語の枠組み CEFR の、話す力の説明を参考に設計しています。CEFR のレベルと同じだと示すものではありません。</p>

<h2 id="listen">聞き手は、どう聞いて、どう付けますか？</h2>
<ol>
<li>録音を、止めずに1回聞きます。聞き直しは2回までです。ふつうの会話では、相手は何度も聞き直せないからです。</li>
<li>質問ごとに、見る力は先に決めてあります。短い質問では一部の力だけを、長く話す質問では6つ全部を見ます。</li>
<li>それぞれの力について、段ごとの説明と例に照らして、いちばん近い段を選びます。</li>
<li>その答えの大半がどの段に近いかで選びます。一度の言い間違いや、一か所の詰まりでは下げません。</li>
<li>何も話していない答えは、その質問で見る力を 0 として数えます。録音の問題で聞けない答えは、数えません。</li>
</ol>
<p>力ごとの点は、2つ以上の答えで見せた、いちばん高い段です。1回だけうまく言えた段ではなく、くり返し出せる段を取るためです。AI の聞き返しのあとに出た答えは、伝わる内容とまとまりを1段下げて数えます。自分から話せた段と分けるためです。</p>

<h2 id="scenes">場面の○△×は、どう決まりますか？</h2>
<p>場面ごとに、「この場面で困らずに話すには、どの力がどの段まで要るか」を決めてあります。たとえば雑談は、相手を待たせずに話が続くことが大事なので、流暢さを高めに見ます。電話の予約は、顔が見えないので、発音を高めに見ます。</p>
<table>
<tr><th>○ 困らずに話せる</th><td>その場面に要る力が、全部その段以上</td></tr>
<tr><th>△ あと少し</th><td>要る力のうち1つだけが、1段足りない（その力が 2 以上の時）</td></tr>
<tr><th>× まだ</th><td>それ以外</td></tr>
<tr><th>判定できない</th><td>要る力が、今回の答えからは十分に見えなかった</td></tr>
</table>
<p>いまの場面は13個です：自己紹介、買い物、役所・病院、電話で予約、雑談、遊びの相談、飲み会で話す、指示を受けて動く、接客、面接、打ち合わせ・会議、授業で発言、ゼミで議論。</p>

<h2 id="next">「次に直す所」は、どう選びますか？</h2>
<p>△と×の場面で、足りていないことがいちばん多い力を選びます。△（あと少し）の場面は、×の場面より重く数えます。○に近い場面から先に届くようにするためです。同じ数の時は、点が低い方を選びます。点がいちばん低い力とは限りません。結果には、いまの話し方と、1つ上の段の話し方をあわせて示します。</p>

<h2 id="ai">AI は、何をしていますか？</h2>
<table>
<tr><th>AI がすること</th><td>答えを文字にする／テストの中で、聞き返しや質問を作る／出した直後の振り返りを作る／聞き手のための下書きを用意する</td></tr>
<tr><th>AI がしないこと</th><td>受けた人に届く点と場面の印を決めること</td></tr>
</table>
<p>AI の振り返りに点を出していないのは、AI の聞き取りが、学習者の話し方を間違えることがあるためです。</p>

<h2 id="limits">この点で、分からないこと</h2>
<ul>
<li>聞き返しや確認などのやりとりと、敬語は測っていません。録音に一人で答える形では、見えないためです。</li>
<li>点と場面の印は目安で、公的な証明ではありません。</li>
<li>聞き手は、いまは1人です。聞き手による違いや、受け直した時の点の動きについての調査結果は、まだ公表していません。</li>
<li>場面ごとに要る段は、受けた人の結果を見ながら直していきます。</li>
</ul>

<h2 id="faq">よくある質問</h2>
<div class="lp-faq">
<details><summary>点は、JLPT の N1〜N5 と対応していますか？</summary><p>対応していません。JLPT は読む力と聞く力の試験で、阿吽は話す力を見ます。別の物差しです。</p></details>
<details><summary>文法の点が低いのに、伝わる内容が高いことはありますか？</summary><p>あります。文が崩れていても、言いたいことが具体的に伝わることはあるためです。6つの力は、同じ原因でまとめて下げないように、分けて見ています。</p></details>
<details><summary>なまりがあると、発音の点は下がりますか？</summary><p>なまりの強さそのものでは下げません。別の言葉に聞こえるか、聞く側が聞き返したくなるかで見ます。</p></details>
<details><summary>点は、何回か受けると変わりますか？</summary><p>話す内容やその日の調子で、動くことはあります。どれくらい動くかの調査結果は、まだ公表していません。</p></details>
</div>
"""),
"en": dict(
    title="How AUN results are decided: six skills, scored 0 to 5",
    desc="How results on the AUN Japanese speaking test are decided: what each level from 0 to 5 sounds like for the six skills, how the Japanese listener listens, how the ○△× marks for each situation are set, what the AI does, and the limits.",
    kick="How scoring works", h1="How AUN results are decided:<br>six skills, scored 0 to 5",
    cta="Take the test free", by="AUN, run by 1900 Co., Ltd.", upd="Last updated",
    toc="In this article", rel="Read next", rel_link=("how-it-works.html", "What is AUN? Inside the 10-minute Japanese speaking test"),
    body="""
<p class="art-lead">Scores on AUN (阿吽) are decided by a Japanese listener who listens to your recording. Speaking is split into six skills, and each one is placed on a six-step scale from 0 to 5. This article explains what the six skills are, what each level sounds like, and how the ○△× mark for each situation is set.</p>

<table class="art-facts">
<tr><th>Who decides</th><td>A Japanese listener (Namba, the founder of AUN). The AI prepares a draft.</td></tr>
<tr><th>What is scored</th><td>Six skills: content, organisation, fluency, grammar, vocabulary and pronunciation</td></tr>
<tr><th>Scale</th><td>0 to 5 for each skill</td></tr>
<tr><th>Situation marks</th><td>For each of 13 situations: ○ (you can handle it), △ (almost) or × (not yet)</td></tr>
<tr><th>Not measured</th><td>Back-and-forth such as asking again or checking, and keigo (polite language)</td></tr>
</table>

<h2 id="six">What are the six skills?</h2>
<p>They are six sides of “being able to speak Japanese” as a listener experiences it. Content is the outcome; the other five are the causes. Skills that are close to each other are kept apart like this.</p>
<div class="art-scroll"><table class="art-cmp">
<tr><th>Skill</th><th>What is looked at</th><th>What is left out</th></tr>
<tr><th>Content</th><td>Detail, whether reasons and feelings are clear, whether it came across without misunderstanding</td><td>The order of the talk (that is organisation); how impressive the opinion is</td></tr>
<tr><th>Organisation</th><td>The order of events, linking words such as “so” and “but”, the line from reason to example to conclusion</td><td>Whether each sentence is correct (that is grammar)</td></tr>
<tr><th>Fluency</th><td>The length and number of pauses, restarts, speed</td><td>Time stopped because a word would not come (that is vocabulary); how clear the sounds are (that is pronunciation)</td></tr>
<tr><th>Grammar</th><td>From words side by side, to short sentences, to joined sentences, to complex ones; whether errors mislead</td><td>Word choice (that is vocabulary). Natural omissions do not lower the score.</td></tr>
<tr><th>Vocabulary</th><td>Range of words, whether the right word is chosen, whether you can rephrase</td><td>How the sentence is built (that is grammar)</td></tr>
<tr><th>Pronunciation</th><td>Whether it sounds like a different word, the effort for the listener, phrasing and intonation</td><td>Pauses and speed (that is fluency); how strong an accent is in itself</td></tr>
</table></div>

<h2 id="levels">What does each level from 0 to 5 sound like?</h2>
<p>A higher level can do everything a lower level can. The descriptions are as follows.</p>
{LEVELS}
{CARDS}
<p>These levels were designed with reference to the descriptions of spoken ability in the CEFR, the European framework for languages. They are not a statement that a score equals a CEFR level.</p>

<h2 id="listen">How does the listener listen and score?</h2>
<ol>
<li>He plays the recording once without stopping, and may replay it at most twice. In a real conversation, the other person cannot keep replaying you.</li>
<li>For each question, the skills to look at are fixed in advance. Short questions use only some of the skills; longer answers use all six.</li>
<li>For each skill, he chooses the closest level by comparing your answer with the description and examples for each level.</li>
<li>He chooses by what most of the answer is like. One slip or one stumble does not lower the level.</li>
<li>An answer with no speech counts as 0 for the skills that question looks at. An answer that cannot be heard because of a recording problem is not counted.</li>
</ol>
<p>Your score for each skill is the highest level you showed in at least two answers. This takes the level you can produce repeatedly, not one you reached once. Answers given after an AI follow-up count one level lower for content and organisation, to separate them from what you said unprompted.</p>

<h2 id="scenes">How are the ○△× marks for each situation set?</h2>
<p>For each situation, we have set which skills are needed, and at what level, to talk without trouble. Small talk, for example, depends on keeping the talk going without making the other person wait, so it asks more of fluency. Booking by phone asks more of pronunciation, because the other person cannot see your face.</p>
<table>
<tr><th>○ You can handle it</th><td>Every skill the situation needs is at or above the required level</td></tr>
<tr><th>△ Almost</th><td>Just one of the needed skills is one level short (and that skill is at 2 or above)</td></tr>
<tr><th>× Not yet</th><td>Anything else</td></tr>
<tr><th>Cannot judge</th><td>Your answers did not show enough of a skill the situation needs</td></tr>
</table>
<p>There are 13 situations at present: introducing yourself, shopping, city office or hospital, booking by phone, small talk, making plans with friends, talking at a drinking party, following instructions at work, customer service, job interview, meetings, speaking up in class, and seminar discussion.</p>

<h2 id="next">How is “what to fix next” chosen?</h2>
<p>It is the skill that most often falls short across your △ and × situations. △ (almost) situations count for more than × ones, so that you reach the situations closest to ○ first. On a tie, the lower score is chosen. It is not always your lowest score. The result shows how you speak now and how the next level up sounds.</p>

<h2 id="ai">What does the AI do?</h2>
<table>
<tr><th>The AI does</th><td>Turn your answers into text; write follow-ups and some questions during the test; write the review you get right away; prepare a draft for the listener</td></tr>
<tr><th>The AI does not</th><td>Decide the scores and situation marks you receive</td></tr>
</table>
<p>The AI review carries no scores because speech recognition can get a learner’s speech wrong.</p>

<h2 id="limits">What these scores do not tell you</h2>
<ul>
<li>Back-and-forth, such as asking again or checking, and keigo are not measured. They cannot be seen when you answer a recording on your own.</li>
<li>Scores and marks are a guide, not an official certificate.</li>
<li>There is one listener at present. We have not yet published studies of differences between listeners or of how scores move when someone retakes the test.</li>
<li>The levels each situation needs will be adjusted as we see more results.</li>
</ul>

<h2 id="faq">Frequently asked questions</h2>
<div class="lp-faq">
<details><summary>Do the scores map to JLPT N1 to N5?</summary><p>No. The JLPT tests reading and listening; AUN looks at speaking. They are different yardsticks.</p></details>
<details><summary>Can grammar be low while content is high?</summary><p>Yes. Your point can come across in detail even when sentences are broken. The six skills are kept apart so that one cause does not pull all of them down.</p></details>
<details><summary>Does an accent lower my pronunciation score?</summary><p>Not in itself. The listener looks at whether a word sounds like a different word and whether he wants to ask again.</p></details>
<details><summary>Will my scores change if I take the test again?</summary><p>They can move with what you talk about and how you are on the day. We have not yet published studies of how much.</p></details>
</div>
"""),
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


def toc(body: str, label: str) -> str:
    items = re.findall(r'<h2 id="([\w-]+)">(.*?)</h2>', body)
    return f'<nav class="art-toc" aria-label="{label}"><p>{label}</p><ol>' + "".join(f'<li><a href="#{{L}}-{i}">{t}</a></li>' for i, t in items) + "</ol></nav>"


def section(c: dict, lang: str, extra: dict) -> str:
    body = c["body"]
    for k, v in extra.items():
        body = body.replace("{" + k + "}", v)
    assert not re.search(r"\{[A-Z0-9]+\}", body), re.findall(r"\{[A-Z0-9]+\}", body)
    body = label_cells(body)
    t = toc(body, c["toc"]).replace("{L}", lang)
    body = re.sub(r'<h2 id="([\w-]+)">', lambda m: f'<h2 id="{lang}-{m.group(1)}">', body)
    lead_end = body.index("</table>") + len("</table>")   # the contents list goes after the lead and the facts table
    body = body[:lead_end] + "\n" + f'<p class="art-ctaw"><a href="/test.html" class="lp-cta">{c["cta"]}</a></p>\n' + t + body[lead_end:]
    return f'''<article class="art" data-l="{lang}" lang="{lang}">
<header class="art-head">
<p class="lp-kick">{c["kick"]}</p>
<h1>{c["h1"]}</h1>
<p class="art-meta">{c["by"]}　｜　{c["upd"]}：<time datetime="{UPDATED["iso"]}">{UPDATED[lang]}</time></p>
</header>
{body}
<aside class="art-rel"><p>{c["rel"]}</p><a href="/{c["rel_link"][0]}">{c["rel_link"][1]}</a></aside>
<p class="art-ctaw end"><a href="/test.html" class="lp-cta">{c["cta"]}</a></p>
</article>'''


def page(name: str, content: dict, extras) -> None:
    ja = content["ja"]
    faq = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", ja["body"])
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    url = f"{SITE}/{name}"
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": ja["title"], "description": ja["desc"], "inLanguage": ["ja", "en"],
           "datePublished": UPDATED["iso"], "dateModified": UPDATED["iso"], "mainEntityOfPage": url,
           "author": {"@type": "Organization", "name": "阿吽 AUN", "url": SITE + "/"},
           "publisher": {"@type": "Organization", "name": "1900 Co., Ltd.", "url": SITE + "/about.html"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faq]}]
    head = LP.split("<title>")[0].split("<!-- meta:start -->")[0]
    head = re.sub(r"<html[^>]*>", '<html lang="ja">', head)
    head = re.sub(r"<!-- 生成ファイル.*?-->", "<!-- 生成ファイル（_tools/build_articles.py）。直すのは _tools/build_articles.py -->", head)
    e = lambda s: html.escape(s, quote=True)
    out = head + f'''<title>{e(ja["title"])}｜阿吽 AUN</title>
<meta name="description" content="{e(ja["desc"])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="阿吽 AUN">
<meta property="og:title" content="{e(ja["title"])}">
<meta property="og:description" content="{e(ja["desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og/og3-ja.png">
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
{section(content["ja"], "ja", extras("ja"))}
{section(content["en"], "en", extras("en"))}
</main>
<footer id="site-foot" class="s-foot"></footer>
<script src="/legal.js?v=20261103q"></script>
</body>
</html>
'''
    (ROOT / name).write_text(out, encoding="utf-8")
    words = len(strip(content["en"]["body"]).split())
    print(f"wrote {name}: {len(out)} bytes, ja {len(strip(ja['body']))} chars, en {words} words")


CAP = {"ja": ["テスト中の画面。答えに足りない所があると、AI が聞き返します。", "AI の振り返りの例。伝わりにくいかもしれない所と、言い換えの例。", "日本人が聞いた結果の例。話せる場面と、6つの力の点。"],
       "en": ["The test screen. If something is missing from an answer, the AI asks a follow-up.", "A sample AI review: a place that may have been hard to understand, and another way to say it.", "A sample result from the Japanese listener: a situation you can handle, and six scores."]}


def how_extras(lang):
    p = pictures(lang)
    return {"PIC1": fig(p[0], CAP[lang][0]), "PIC2": fig(p[1], CAP[lang][1]), "PIC3": fig(p[2], CAP[lang][2]), "CARDS": cards(lang)}


page("how-it-works.html", HOW, how_extras)
page("scoring.html", SCORING, lambda lang: {"LEVELS": levels(lang), "CARDS": cards(lang)})
