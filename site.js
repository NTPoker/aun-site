// Shared header and footer for every page: one place for the menu, the language picker and the footer links.
// Pages put <header id="site-top"></header><script src="site.js"></script> at the top and <footer id="site-foot"></footer> at the end.
// The chosen language is kept in localStorage "aun-lang"; pages listen for the "aun:lang" event to redraw their own text.
(function () {
  const NAMES = { ja: "日本語", en: "English", id: "Bahasa Indonesia", vi: "Tiếng Việt", zh: "简体中文", "zh-TW": "繁體中文", ko: "한국어" };
  const T = {
    ja: { menu: "メニュー", story: "物語で話す", storyCta: "無料で話す", storyFree: "無料で遊べます", test: "阿吽のテスト", arts: "記事", app: "アプリ", how: "テストの中身", cta: "無料で受ける", svc: "サービス", co: "会社", rules: "ご利用にあたって", signup: "先行登録", faq: "よくある質問", about: "運営会社", contact: "お問い合わせ", privacy: "プライバシーポリシー", terms: "利用規約", legal: "特定商取引法に基づく表記", op: "運営：株式会社1900（東京・銀座）", free: "いまは無料で受けられます" },
    en: { menu: "Menu", test: "AUN test", arts: "Articles", app: "App", how: "How the test works", cta: "Take it free", svc: "Service", co: "Company", rules: "Policies", signup: "Early sign-up", faq: "FAQ", about: "About", contact: "Contact", privacy: "Privacy Policy", terms: "Terms", legal: "Legal notice", op: "Operated by 1900 Co., Ltd. (Ginza, Tokyo)", free: "Free to take for now" },
    id: { menu: "Menu", test: "Tes AUN", arts: "Artikel", app: "Aplikasi", how: "Cara kerja tes", cta: "Ikut gratis", svc: "Layanan", co: "Perusahaan", rules: "Kebijakan", signup: "Daftar awal", faq: "Pertanyaan umum", about: "Tentang kami", contact: "Kontak", privacy: "Kebijakan privasi", terms: "Ketentuan", legal: "Pemberitahuan hukum", op: "Dikelola oleh 1900 Co., Ltd. (Ginza, Tokyo)", free: "Saat ini gratis" },
    vi: { menu: "Menu", test: "Bài kiểm tra AUN", arts: "Bài viết", app: "Ứng dụng", how: "Cách bài kiểm tra hoạt động", cta: "Làm bài miễn phí", svc: "Dịch vụ", co: "Công ty", rules: "Chính sách", signup: "Đăng ký trước", faq: "Câu hỏi thường gặp", about: "Về chúng tôi", contact: "Liên hệ", privacy: "Chính sách quyền riêng tư", terms: "Điều khoản", legal: "Thông báo pháp lý", op: "Vận hành bởi 1900 Co., Ltd. (Ginza, Tokyo)", free: "Hiện đang miễn phí" },
    zh: { menu: "菜单", test: "AUN 测试", arts: "文章", app: "应用", how: "测试内容", cta: "免费参加", svc: "服务", co: "公司", rules: "使用须知", signup: "提前登记", faq: "常见问题", about: "运营公司", contact: "联系我们", privacy: "隐私政策", terms: "使用条款", legal: "法律声明", op: "运营：株式会社1900（东京・银座）", free: "目前可免费参加" },
    "zh-TW": { menu: "選單", test: "AUN 測驗", arts: "文章", app: "應用程式", how: "測驗內容", cta: "免費參加", svc: "服務", co: "公司", rules: "使用須知", signup: "提前登記", faq: "常見問題", about: "營運公司", contact: "聯絡我們", privacy: "隱私權政策", terms: "使用條款", legal: "法律聲明", op: "營運：株式会社1900（東京・銀座）", free: "目前可免費參加" },
    ko: { menu: "메뉴", test: "AUN 테스트", arts: "아티클", app: "앱", how: "테스트 안내", cta: "무료로 응시", svc: "서비스", co: "회사", rules: "이용 안내", signup: "사전 등록", faq: "자주 묻는 질문", about: "운영 회사", contact: "문의", privacy: "개인정보 처리방침", terms: "이용약관", legal: "특정상거래법에 따른 표기", op: "운영: 1900 Co., Ltd.(도쿄 긴자)", free: "지금은 무료로 볼 수 있어요" }
  };
  const ok = l => Object.prototype.hasOwnProperty.call(NAMES, l);
  const fromBrowser = tag => {
    const n = tag.toLowerCase();
    if (n.startsWith("zh")) {
      if (n.includes("hant")) return "zh-TW";
      if (n.includes("hans")) return "zh";
      return /-(tw|hk|mo)\b/.test(n) ? "zh-TW" : "zh";
    }
    const base = n.split("-")[0];
    return ok(base) ? base : null;
  };
  // landing pages per language (/, /en/, …) declare themselves with <html data-fixed-lang> and <link rel="alternate" data-lang>
  const fixed = document.documentElement.getAttribute("data-fixed-lang");
  const alt = l => document.querySelector('link[rel="alternate"][data-lang="' + l + '"]');
  // Only the source tag travels with a language change. ?lang= must not: the picker would bounce straight back.
  const keep = () => { const q = new URLSearchParams(location.search), o = new URLSearchParams(); ["src", "ref"].forEach(k => { if (q.get(k)) o.set(k, q.get(k)); }); const t = o.toString(); return t ? "?" + t : ""; };
  const homeOf = l => ({ en: "/", "zh-TW": "/zh-tw/" })[l] || "/" + l + "/";
  const home = () => homeOf(lang);
  // The Japanese top is the story page (NT 11/19・11/21); the speaking test's page moved to /ja/test/. Other languages: the test is still the top.
  const testOf = l => (l === "ja" ? "/ja/test/" : homeOf(l));
  const STORY_APP = "https://app.aunjapanese.com/";
  const kind = document.documentElement.getAttribute("data-kind");   // "story" on the story page
  // / is the English page. A visitor who chose another language before, or whose browser is in another of ours, goes there.
  if (document.documentElement.hasAttribute("data-lang-home")) {
    let pref = new URLSearchParams(location.search).get("lang");
    if (!ok(pref)) { try { pref = localStorage.getItem("aun-lang"); } catch (e) {} }
    if (!ok(pref)) { for (const tag of navigator.languages || [navigator.language || ""]) { pref = fromBrowser(tag); if (pref) break; } }
    if (ok(pref) && pref !== "en" && alt(pref)) { location.replace((pref === "ja" ? "/ja/" : new URL(alt(pref).href).pathname) + keep() + (pref === "ja" ? "" : location.hash)); return; }
  }
  const pick = () => {
    if (ok(fixed)) { try { localStorage.setItem("aun-lang", fixed); } catch (e) {} return fixed; }
    const q = new URLSearchParams(location.search).get("lang");
    if (ok(q)) { try { localStorage.setItem("aun-lang", q); } catch (e) {} return q; }
    try { const s = localStorage.getItem("aun-lang"); if (ok(s)) return s; } catch (e) {}
    for (const tag of navigator.languages || [navigator.language || ""]) { const l = fromBrowser(tag); if (l) return l; }
    return "en";
  };
  const page = location.pathname.split("/").pop() || "index.html";
  const MARK = '<img class="s-mark" src="/mark.svg" alt="" width="46" height="40">';
  const GLOBE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.8 3 2.8 16 0 19M12 2.5c-2.8 3-2.8 16 0 19"/></svg>';
  let lang = pick();

  const MENU_ICON = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';
  function menuItems(d) {
    const items = lang === "ja" ? [[STORY_APP, d.story], [testOf(lang), d.test], ["/ja/how-it-works.html", d.how], ["/ja/articles.html", d.arts]]
                                : [[testOf(lang), d.test], ["/how-it-works.html", d.how], ["/articles.html", d.arts]];
    return items.map(([h, t]) => '<li><a href="' + h + '"' + (h === location.pathname ? ' aria-current="page"' : "") + ">" + t + "</a></li>").join("");
  }
  function drawTop(el) {
    const d = T[lang];
    const cta = kind === "story" && d.storyCta ? '<a class="s-cta" href="' + STORY_APP + '" data-pos="header">' + d.storyCta + "</a>"
              : page === "test.html" ? "" : '<a class="s-cta" href="/test.html">' + d.cta + "</a>";
    el.innerHTML = '<div class="s-top-in"><a href="' + home() + '" class="s-brand" aria-label="AUN 阿吽">' + MARK + '<span>AUN</span><em class="s-kanji" aria-hidden="true">阿吽</em></a>' +
      '<div class="s-right">' + cta +
      '<div class="s-lang"><button type="button" class="s-lang-btn" aria-haspopup="true" aria-expanded="false" aria-label="Language">' + GLOBE + '<span>' + NAMES[lang] + '</span></button>' +
      '<ul class="s-lang-menu" hidden>' + Object.keys(NAMES).map(l => '<li><button type="button" lang="' + l + '" data-lang="' + l + '" aria-current="' + (l === lang) + '">' + NAMES[l] + '</button></li>').join("") + '</ul></div>' +
      '<div class="s-lang s-menu"><button type="button" class="s-lang-btn s-menu-btn" aria-haspopup="true" aria-expanded="false" aria-label="' + d.menu + '">' + MENU_ICON + '</button>' +
      '<ul class="s-lang-menu s-menu-list" hidden>' + menuItems(d) + '</ul></div></div></div>';
    el.querySelectorAll(".s-lang").forEach(box => {
      const btn = box.querySelector("button"), menu = box.querySelector("ul");
      btn.addEventListener("click", () => {
        const open = menu.hidden;
        el.querySelectorAll(".s-lang-menu").forEach(m => { m.hidden = true; });
        el.querySelectorAll(".s-lang-btn").forEach(b => b.setAttribute("aria-expanded", "false"));
        menu.hidden = !open; btn.setAttribute("aria-expanded", String(open));
      });
    });
    el.querySelector(".s-lang-menu").addEventListener("click", e => { const b = e.target.closest("button[data-lang]"); if (b) set(b.dataset.lang, true); });
  }
  function drawFoot(el) {
    const d = T[lang], a = (href, k) => '<a href="' + href + '">' + d[k] + "</a>";
    el.innerHTML = '<div class="s-foot-in">' +
      '<div class="s-foot-brand"><a href="' + home() + '" class="s-brand" aria-label="AUN 阿吽">' + MARK + '<span>AUN</span></a><p>' + d.op + '</p><p class="s-free">' + (kind === "story" && d.storyFree ? d.storyFree : d.free) + '</p><p><a href="mailto:hello@aunjapanese.com">hello@aunjapanese.com</a></p><p class="s-social"><a href="https://x.com/aun_japanese" target="_blank" rel="noopener" aria-label="X @aun_japanese"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.9 2H22l-6.8 7.8L23.2 22h-6.3l-4.9-6.4L6.4 22H3.3l7.3-8.3L2.8 2h6.4l4.4 5.9L18.9 2zm-1.1 18h1.7L8.3 3.9H6.5L17.8 20z"/></svg><span>@aun_japanese</span></a></p></div>' +
      '<nav class="s-foot-cols" aria-label="Footer">' +
      '<div><h2>' + d.svc + '</h2>' + (lang === "ja" ? a(STORY_APP, "story") + a(testOf(lang), "test") : a("/test.html", "cta")) + a((lang === "ja" ? "/ja" : "") + "/how-it-works.html", "how") + a((lang === "ja" ? "/ja" : "") + "/articles.html", "arts") + a(home() + "#faq", "faq") + "</div>" +
      '<div><h2>' + d.co + '</h2>' + a("/about.html", "about") + a("/contact.html", "contact") + "</div>" +
      '<div><h2>' + d.rules + '</h2>' + a("/privacy.html", "privacy") + a("/terms.html", "terms") + a("/tokushoho.html", "legal") + "</div></nav>" +
      '<p class="s-copy">© 2026 1900 Co., Ltd.</p></div>';
  }
  function draw() {
    const top = document.getElementById("site-top"), foot = document.getElementById("site-foot");
    if (top) { top.lang = lang; drawTop(top); }
    if (foot) { foot.lang = lang; drawFoot(foot); }
  }
  function set(l, chosen) {
    if (!ok(l)) return;
    lang = l;
    try { localStorage.setItem("aun-lang", l); } catch (e) {}
    const dest = alt(l) ? new URL(alt(l).href).pathname : (fixed && l !== fixed ? homeOf(l) : null);
    if (chosen && dest && dest !== location.pathname) { location.href = dest + keep() + (alt(l) ? location.hash : ""); return; }
    draw();
    if (chosen) { const b = document.querySelector("#site-top .s-lang-btn"); if (b) b.focus(); }
    document.dispatchEvent(new CustomEvent("aun:lang", { detail: { lang: l, chosen: !!chosen } }));
  }
  document.addEventListener("click", e => {
    if (e.target.closest(".s-lang")) return;
    document.querySelectorAll(".s-lang-menu").forEach(m => { m.hidden = true; });
    document.querySelectorAll(".s-lang-btn").forEach(b => b.setAttribute("aria-expanded", "false"));
  });
  // Opening: the red circle is brushed in, 阿 then 吽 appear (breath in, breath out), then the page opens.
  // Once per visit (sessionStorage), skipped for reduced motion; a tap skips it.
  function intro() {
    try { if (sessionStorage.getItem("aun-intro")) return; sessionStorage.setItem("aun-intro", "1"); } catch (e) { return; }
    if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const el = document.createElement("div");
    el.className = "s-intro";
    el.setAttribute("aria-hidden", "true");
    el.innerHTML = '<div class="s-intro-c"><img src="/mark.svg" alt=""><p><span>阿</span><span>吽</span></p></div><b>AUN</b>';
    if (!(window.CSS && CSS.registerProperty)) el.classList.add("plain");  // no animatable mask: fade the circle in instead
    document.body.appendChild(el);
    document.documentElement.classList.add("s-intro-on");
    const done = () => { if (!el.isConnected) return; el.classList.add("out"); document.documentElement.classList.remove("s-intro-on"); setTimeout(() => el.remove(), 700); };
    el.addEventListener("click", done);
    setTimeout(done, 1700);
  }
  intro();

  window.AUN_SITE = { get lang() { return lang; }, set, langs: Object.keys(NAMES) };
  draw();
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", draw);
})();
