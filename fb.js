import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { src } from "./src.js";
import { getFirestore, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const app = initializeApp({
  apiKey: "AIzaSyCHsu4QvmccC6feQ2qBltt7zxUjZ2aP7VA",
  authDomain: "aun-japanese-1900.firebaseapp.com",
  projectId: "aun-japanese-1900",
  storageBucket: "aun-japanese-1900.firebasestorage.app",
  messagingSenderId: "464841605680",
  appId: "1:464841605680:web:fb414a0f7e4f935b38e3f5"
});
const db = getFirestore(app);

export const save = (name, data) => addDoc(collection(db, name), { ...data, createdAt: serverTimestamp() });

// Which link brought the visitor: in src.js so pages can read it without waiting for Firebase.
export { src };

// Anonymous page events. A random id per page load only; nothing is stored in the browser.
export const sid = Math.random().toString(36).slice(2, 12);  // test.html also hands it to the test, so a tap can be followed there (NT 11/5)
const page = location.pathname.split("/").pop() || "index";
// The sign-up event carries no visit id, so browsing is never tied to a person.
// Pages opened on this computer (previews, checks) are not measured, unless the address has ?track=1.
const LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) && !/[?&]track=1/.test(location.search);
// ga: extra parameters for Google Analytics only (the database accepts a fixed set of fields).
export const track = (t, extra = {}, ga = {}) => {
  if (LOCAL) return;
  const ev = { t, page: page.slice(0, 39), lang: (document.documentElement.lang || "").slice(0, 9), src: src(), w: Math.min(10000, Math.round(innerWidth)), ...extra };
  if (t !== "signup") ev.sid = sid;
  save("events", ev).catch(() => {});
  // Mirror the meaningful actions to Google Analytics (page views and scrolls it measures itself).
  // cta_click = a person tapped a button; test_redirect = test.html passed them on to the test (it happens by itself).
  const GA = { cta: page === "test.html" ? "test_redirect" : "cta_click", signup: "sign_up", lang: "select_language" };
  if (GA[t] && typeof window.gtag === "function") window.gtag("event", GA[t], { page: ev.page, src: ev.src, lang: ev.lang, ...ga });
};

// Shows a "still sending" note if the database has not confirmed within a few seconds.
// We never resend: the first write may still complete.
export const slowNote = (el, text) => setTimeout(() => { el.className = "msg"; el.textContent = text; }, 6000);
