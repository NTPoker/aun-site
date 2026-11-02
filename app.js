import { save, src, track, slowNote } from "./fb.js";

const T = window.AUN_I18N;
const LANGS = Object.keys(T);
let lang = "ja";

const ok = l => LANGS.includes(l);

function fromBrowser(tag) {
  const n = tag.toLowerCase();
  if (n.startsWith("zh")) {
    if (n.includes("hant")) return "zh-TW";
    if (n.includes("hans")) return "zh";
    return /-(tw|hk|mo)\b/.test(n) ? "zh-TW" : "zh";
  }
  const base = n.split("-")[0];
  return ok(base) ? base : null;
}

function pickLang() {
  const q = new URLSearchParams(location.search).get("lang");
  if (ok(q)) return q;
  try { const s = localStorage.getItem("aun-lang"); if (ok(s)) return s; } catch (e) {}
  for (const tag of navigator.languages || [navigator.language || ""]) {
    const l = fromBrowser(tag);
    if (l) return l;
  }
  return "en";
}

function apply(l) {
  lang = l;
  const d = T[l];
  document.documentElement.lang = l;
  document.querySelectorAll("[data-i]").forEach(el => { el.textContent = d[el.dataset.i] ?? ""; });
  document.querySelectorAll("[data-i-html]").forEach(el => { el.innerHTML = d[el.dataset.iHtml] ?? ""; });
  document.getElementById("langLabel").textContent = d.langLabel;
  document.querySelectorAll("#langMenu button").forEach(b => b.setAttribute("aria-current", String(b.dataset.lang === l)));
  try { localStorage.setItem("aun-lang", l); } catch (e) {}
}

const btn = document.getElementById("langBtn");
const menu = document.getElementById("langMenu");
btn.addEventListener("click", () => {
  const open = menu.hidden;
  menu.hidden = !open;
  btn.setAttribute("aria-expanded", String(open));
});
menu.addEventListener("click", e => {
  const b = e.target.closest("button[data-lang]");
  if (!b) return;
  apply(b.dataset.lang);
  track("lang");
  menu.hidden = true;
  btn.setAttribute("aria-expanded", "false");
});
document.addEventListener("click", e => {
  if (!e.target.closest(".lang")) { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); }
});

const form = document.getElementById("form");
const msg = document.getElementById("msg");
const submit = document.getElementById("submit");
form.addEventListener("submit", async e => {
  e.preventDefault();
  const d = T[lang];
  const email = form.email.value.trim();
  msg.className = "msg";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 199) { msg.textContent = d.msgEmail; msg.classList.add("err"); return; }
  if (!document.getElementById("consent").checked) { msg.textContent = d.msgConsent; msg.classList.add("err"); return; }
  submit.disabled = true;
  const slow = slowNote(msg, d.msgSlow);
  try {
    await save("signups", {
      email,
      lang,
      firstLanguage: form.firstLanguage.value.trim(),
      country: form.country.value.trim(),
      jlpt: form.jlpt.value,
      want: form.want.value.trim(),
      consent: true,
      ua: navigator.userAgent.slice(0, 390),
      src: src()
    });
    track("signup");
    form.reset();
    msg.textContent = d.msgOk;
    msg.classList.add("ok");
  } catch (err) {
    console.error(err);
    msg.textContent = d.msgErr;
    msg.classList.add("err");
  } finally {
    clearTimeout(slow);
    submit.disabled = false;
  }
});

apply(pickLang());

// Anonymous measurement: page view, how far people scroll, and which buttons they press.
track("view");
const seen = new Set();
const depth = () => {
  const max = document.documentElement.scrollHeight - innerHeight;
  if (max <= 0) return;
  const atBottom = scrollY >= max - 2;
  const pct = atBottom ? 100 : Math.min(99, Math.floor(scrollY / max * 100));
  for (const step of [25, 50, 75, 100]) {
    if (pct >= step && !seen.has(step)) { seen.add(step); track("scroll", { depth: step }); }
  }
};
addEventListener("scroll", depth, { passive: true });
addEventListener("load", depth);
document.querySelectorAll('a[href="#signup"]').forEach(a => a.addEventListener("click", () => track("cta")));

// Hero demo: plays the sample result once like a short video, then stays on the result.
const demo = document.getElementById("demo");
if (demo) {
  const prog = demo.querySelector(".prog");
  const clock = demo.querySelector(".clock");
  const replay = document.getElementById("replay");
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const steps = [["s0", 0, "0:00", 600], ["s1", 30, "0:03", 1700], ["s2", 58, "0:07", 1800], ["s3", 58, "0:07", 1500], ["s4", 58, "0:07", 0]];
  let timer = null;
  const set = (s, pct, t) => {
    demo.className = "demo " + s;
    prog.style.transition = pct === 0 || motion.matches ? "none" : "width 1.6s linear";
    prog.style.width = pct + "%";
    clock.textContent = t;
  };
  const end = () => { clearTimeout(timer); set("s4", 58, "0:07"); replay.hidden = motion.matches; };
  const play = () => {
    if (motion.matches) return end();
    replay.hidden = true;
    let i = 0;
    const tick = () => {
      const [s, p, t, ms] = steps[i++];
      set(s, p, t);
      if (i < steps.length) timer = setTimeout(tick, ms); else end();
    };
    tick();
  };
  replay.addEventListener("click", play);
  motion.addEventListener("change", () => { if (motion.matches) end(); });
  play();
}
