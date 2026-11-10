import { src, track } from "./fb.js";

const T = window.AUN_I18N;
let lang = "ja";

function apply(l) {
  lang = l;
  const d = T[l];
  document.documentElement.lang = l;
  document.querySelectorAll("[data-i]").forEach(el => { const v = d[el.dataset.i]; if (v !== undefined) el.textContent = v; });
  document.querySelectorAll("[data-i-html]").forEach(el => { const v = d[el.dataset.iHtml]; if (v !== undefined) el.innerHTML = v; });
  document.querySelectorAll("[data-i-alt]").forEach(el => { el.alt = d[el.dataset.iAlt] ?? ""; });
}

// the language picker lives in the shared header (site.js)
document.addEventListener("aun:lang", e => { apply(e.detail.lang); if (e.detail.chosen) track("lang"); });

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
// generated pages use /test.html (absolute), the source uses test.html
const ctas = document.querySelectorAll('main a[href$="test.html"]');
ctas.forEach(a => a.addEventListener("click", () => track("cta")));
// The store badge for this device only; both when the device is unknown. Detection is a hint for display, never a redirect.
const os = (() => {
  const p = (navigator.userAgentData && navigator.userAgentData.platform) || "";
  const ua = navigator.userAgent || "";
  if (/android/i.test(p) || /Android/.test(ua)) return "android";
  if (/iphone|ipod/i.test(p) || /iPhone|iPod/.test(ua)) return "ios";
  return "";
})();
if (os) document.documentElement.dataset.os = os;
document.querySelectorAll(".allstores").forEach(a => a.addEventListener("click", e => { e.preventDefault(); a.closest(".appsec")?.querySelector(".badges")?.classList.add("all"); a.parentElement.hidden = true; track("store_other", { os }); }));
document.querySelectorAll(".badges a").forEach(a => a.addEventListener("click", () => track("store", { dest: /apple/.test(a.href) ? "ios" : "android", os, place: a.closest("#app") ? "app" : "other" })));
document.querySelectorAll(".applink").forEach(a => a.addEventListener("click", () => track("applink", { os })));
// Keep the visitor's source tag when they move on to the test page.
const tag = src();
if (!tag.startsWith("ref:") && tag !== "direct" && tag !== "other") ctas.forEach(a => { a.href = "/test.html?src=" + encodeURIComponent(tag); });

// Hero demo: plays the sample result once like a short video, then stays on the result.
const demo = document.getElementById("demo");
if (demo) {
  const prog = demo.querySelector(".prog");
  const clock = demo.querySelector(".clock");
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const steps = [["s0", 0, "0:00", 600], ["s1", 30, "0:03", 1700], ["s2", 58, "0:07", 1800], ["s3", 58, "0:07", 1500], ["s4", 58, "0:07", 0]];
  let timer = null;
  const set = (s, pct, t) => {
    demo.className = "demo " + s;
    prog.style.transition = pct === 0 || motion.matches ? "none" : "width 1.6s linear";
    prog.style.width = pct + "%";
    clock.textContent = t;
  };
  const end = () => { clearTimeout(timer); set("s4", 58, "0:07"); };
  const play = () => {
    if (motion.matches) return end();
    let i = 0;
    const tick = () => {
      const [s, p, t, ms] = steps[i++];
      set(s, p, t);
      if (i < steps.length) timer = setTimeout(tick, ms); else end();
    };
    tick();
  };
  motion.addEventListener("change", () => { if (motion.matches) end(); });
  play();
}
