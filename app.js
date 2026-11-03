import { save, src, track, slowNote } from "./fb.js";

const T = window.AUN_I18N;
let lang = "ja";

function apply(l) {
  lang = l;
  const d = T[l];
  document.documentElement.lang = l;
  document.querySelectorAll("[data-i]").forEach(el => { el.textContent = d[el.dataset.i] ?? ""; });
  document.querySelectorAll("[data-i-html]").forEach(el => { el.innerHTML = d[el.dataset.iHtml] ?? ""; });
}

// the language picker lives in the shared header (site.js)
document.addEventListener("aun:lang", e => { apply(e.detail.lang); if (e.detail.chosen) track("lang"); });

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
      why: form.why.value,
      want: form.want.value.trim(),
      consent: true,
      ua: navigator.userAgent.slice(0, 390),
      src: src()
    });
    track("signup");
    const why = form.why.value;
    form.reset();
    msg.textContent = d.msgOk + " ";
    const go = document.createElement("a");
    go.className = "msg-go";
    const q = new URLSearchParams({ why });
    const tag = src();
    if (!tag.startsWith("ref:") && tag !== "direct" && tag !== "other") q.set("src", tag);
    go.href = "test.html?" + q;
    go.textContent = d.msgGo;
    go.addEventListener("click", () => track("cta"));
    msg.append(document.createElement("br"), go);
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

apply(window.AUN_SITE.lang);

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
document.querySelectorAll('a[href="#signup"], a[href="test.html"]').forEach(a => a.addEventListener("click", () => track("cta")));
// Keep the visitor's source tag when they move on to the test page.
const tag = src();
if (!tag.startsWith("ref:") && tag !== "direct" && tag !== "other") document.querySelectorAll('a[href="test.html"]').forEach(a => { a.href = "test.html?src=" + encodeURIComponent(tag); });

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
