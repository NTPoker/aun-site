// Legal pages: Japanese is the original; every other site language shows the English translation.
// The language comes from the shared header (site.js).
(function () {
  const set = l => { document.documentElement.lang = l === "ja" ? "ja" : "en"; };
  set(window.AUN_SITE ? window.AUN_SITE.lang : "ja");
  document.addEventListener("aun:lang", e => set(e.detail.lang));
})();
