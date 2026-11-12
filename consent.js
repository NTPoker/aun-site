// Google Analytics consent: granted by default, but denied in the EEA, UK and Switzerland until
// the visitor agrees (Google applies the region rule by IP). The banner only appears for visitors
// whose time zone is in Europe, and their choice is remembered in this browser.
(function () {
  var KEY = "aun-ga-consent";
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (saved === "granted" || saved === "denied") {
    gtag("consent", "update", { analytics_storage: saved });
  }
  var tz = "";
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  if (saved || tz.indexOf("Europe/") !== 0) return;
  var ja = (document.documentElement.lang || "").indexOf("ja") === 0;
  var bar = document.createElement("div");
  bar.className = "consent-bar";
  bar.innerHTML = (ja
    ? '<p>利用状況の分析に Cookie（Google アナリティクス）を使ってもよいですか？ <a href="/privacy.html">プライバシーポリシー</a></p>'
    : '<p>May we use cookies (Google Analytics) to understand how the site is used? <a href="/privacy.html">Privacy Policy</a></p>')
    + '<div><button type="button" data-v="denied">' + (ja ? "使わない" : "No") + '</button>'
    + '<button type="button" data-v="granted">' + (ja ? "使ってよい" : "Yes") + '</button></div>';
  bar.addEventListener("click", function (e) {
    var v = e.target && e.target.getAttribute && e.target.getAttribute("data-v");
    if (!v) return;
    gtag("consent", "update", { analytics_storage: v });
    try { localStorage.setItem(KEY, v); } catch (err) {}
    bar.remove();
  });
  document.addEventListener("DOMContentLoaded", function () { document.body.appendChild(bar); });
  if (document.readyState !== "loading") document.body.appendChild(bar);
})();
