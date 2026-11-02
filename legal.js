// Legal pages: Japanese is the original; every other site language shows the English translation.
(function () {
  const LANGS = ["ja", "en", "id", "vi", "zh", "zh-TW", "ko"];
  const ok = l => LANGS.includes(l);
  let lang = new URLSearchParams(location.search).get("lang");
  if (!ok(lang)) { try { lang = localStorage.getItem("aun-lang"); } catch (e) {} }
  if (!ok(lang)) lang = (navigator.language || "en").toLowerCase().startsWith("ja") ? "ja" : "en";
  const set = l => {
    document.documentElement.lang = l === "ja" ? "ja" : "en";
    document.querySelectorAll(".switch button").forEach(b => b.setAttribute("aria-pressed", String((b.dataset.to === "ja") === (l === "ja"))));
  };
  set(lang);
  document.querySelectorAll(".switch button").forEach(b => b.addEventListener("click", () => {
    set(b.dataset.to);
    try { localStorage.setItem("aun-lang", b.dataset.to); } catch (e) {}
  }));
})();
