// Articles: count the page view and the taps on the test buttons (same events as the landing page).
import { src } from "./src.js";

let send = null;
const early = [];
const track = (...a) => { if (send) send(...a); else if (early.length < 20) early.push(a); };
import("./fb.js?v=20261112c").then(m => { send = m.track; early.splice(0).forEach(a => send(...a)); }).catch(() => { early.length = 0; });

track("view");
const tag = src();
const tagged = !tag.startsWith("ref:") && tag !== "direct" && tag !== "other";
document.addEventListener("click", e => {
  const a = e.target.closest && e.target.closest("a[href]");
  if (!a || !/(^|\/)test\.html($|[?#])/.test(a.getAttribute("href"))) return;
  if (tagged && !/[?&]src=/.test(a.getAttribute("href"))) a.href = "/test.html?src=" + encodeURIComponent(tag);
  track("cta", {}, { placement: a.closest("header") ? "header" : a.closest("footer") ? "footer" : "article" });
});
