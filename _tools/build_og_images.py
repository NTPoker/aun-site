#!/usr/bin/env python3
"""Open Graph images per language: og/og-<lang>.png (1200x630), the hero headline on the black-and-white photo.
Uses the headline and lead from i18n.js. Needs Google Chrome. Run: python3 _tools/build_og_images.py"""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
T = json.loads(subprocess.run(
    ["node", "-e", 'global.window={};require("./i18n.js");process.stdout.write(JSON.stringify(window.AUN_I18N))'],
    cwd=ROOT, check=True, capture_output=True, text=True).stdout)
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wght@500;800&family=Zen+Old+Mincho:wght@900"
         "&family=Zen+Kaku+Gothic+New:wght@500;700&family=Noto+Sans+SC:wght@700&family=Noto+Sans+TC:wght@700"
         "&family=Noto+Sans+KR:wght@700&display=swap")
HEAD_FONT = {"ja": "'Zen Old Mincho',serif", "zh": "'Noto Sans SC',sans-serif", "zh-TW": "'Noto Sans TC',sans-serif",
             "ko": "'Noto Sans KR',sans-serif"}
LATIN = "'Archivo',sans-serif"

PAGE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><link rel="stylesheet" href="{fonts}">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#000}}
.ph{{position:absolute;top:0;right:0;bottom:0;width:640px;background:url('{photo}') 50% 26%/cover no-repeat}}
.ph::after{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#000 0,rgba(0,0,0,.5) 30%,rgba(0,0,0,0) 60%)}}
.c{{position:absolute;left:84px;top:70px;right:420px;bottom:60px;display:flex;flex-direction:column;color:#EFECE4;font-family:'Zen Kaku Gothic New',{latin}}}
.brand{{display:flex;align-items:center;gap:14px;font-family:{latin};font-weight:800;font-size:30px;letter-spacing:.14em}}
.brand img{{width:50px}}
h1{{margin:auto 0 0;font-family:{head};font-weight:{hw};font-size:{size}px;line-height:1.16;letter-spacing:0}}
h1 .red{{color:#E8735F}}
p{{margin:26px 0 0;font-size:{lead}px;line-height:1.5;color:#D9D4C8;font-weight:500}}
p .nw{{display:inline}}
</style></head><body><div class="ph"></div><div class="c">
<div class="brand"><img src="{mark}" alt="">AUN</div><h1>{h}</h1><p>{l}</p></div></body></html>"""

out_dir = ROOT / "og"
out_dir.mkdir(exist_ok=True)
for lang, d in T.items():
    latin_head = lang in ("en", "id", "vi")
    page = PAGE.format(lang=lang, fonts=FONTS, photo=(ROOT / "hero-bw.jpg").as_uri(), mark=(ROOT / "mark.svg").as_uri(),
                       latin=LATIN, head=LATIN if latin_head else HEAD_FONT[lang], hw=800 if latin_head else 900,
                       size=70 if latin_head else 96, lead=30 if latin_head else 32, h=d["heroH"], l=d["heroLead"])
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(page)
    target = out_dir / f"og-{lang.lower()}.png"
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1", "--window-size=1200,630",
                    "--virtual-time-budget=6000", f"--screenshot={target}", Path(f.name).as_uri()],
                   check=True, capture_output=True)
    print("wrote", target.relative_to(ROOT))
