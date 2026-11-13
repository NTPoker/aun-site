// Articles: count the page view and the taps on the test buttons (same events as the landing page).
import { src } from "./src.js";

let send = null;
const early = [];
const track = (...a) => { if (send) send(...a); else if (early.length < 20) early.push(a); };
import("./fb.js?v=20261112c").then(m => { send = m.track; early.splice(0).forEach(a => send(...a)); }).catch(() => { early.length = 0; });

track("view");
// Until 11/12 both languages shared one address and headings were #ja-result, #en-levels: old links still land.
const old = /^#(ja|en)-([\w-]+)$/.exec(location.hash);
if (old && document.getElementById(old[2])) location.replace("#" + old[2]);
const tag = src();
const tagged = !tag.startsWith("ref:") && tag !== "direct" && tag !== "other";
document.addEventListener("click", e => {
  const a = e.target.closest && e.target.closest("a[href]");
  if (!a) return;
  // The source tag also travels to the articles, so a visitor who reads one first is still counted under their source.
  const art = /^(\/ja)?\/(how-it-works|scoring|jlpt-speaking-test|japanese-speaking-levels|passed-jlpt-cant-speak|articles)\.html(#.*)?$/.exec(a.getAttribute("href"));
  if (art && tagged) { a.href = a.getAttribute("href").replace(/(#.*)?$/, "?src=" + encodeURIComponent(tag) + (art[3] || "")); return; }
  if (!/(^|\/)test\.html($|[?#])/.test(a.getAttribute("href"))) return;
  if (tagged && !/[?&]src=/.test(a.getAttribute("href"))) a.href = "/test.html?src=" + encodeURIComponent(tag);
  track("cta", {}, { placement: a.closest("header") ? "header" : a.closest("footer") ? "footer" : "article" });
});
