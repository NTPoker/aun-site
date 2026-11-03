import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
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

// Which link brought the visitor. Only our own tags count (?src=tiktok-0103, ?src=reddit-wed);
// anything else is recorded as "other" so free text never reaches the database.
const TAG = /^(tiktok|ig|yt|reddit|wk|discord|x|fb|line|qr|mail|trial|test)(-[a-z0-9]{1,16}){0,2}$/;
export const src = () => {
  const p = new URLSearchParams(location.search);
  const v = (p.get("src") || p.get("ref") || "").toLowerCase();
  if (v) return TAG.test(v) ? v : "other";
  let host = "";
  try { host = document.referrer ? new URL(document.referrer).hostname : ""; } catch (e) {}
  if (!host || host === location.hostname) return "direct";
  return "ref:" + host.replace(/[^a-z0-9.-]/g, "").slice(0, 36);
};

// Anonymous page events. A random id per page load only; nothing is stored in the browser.
const sid = Math.random().toString(36).slice(2, 12);
const page = location.pathname.split("/").pop() || "index";
// The sign-up event carries no visit id, so browsing is never tied to a person.
export const track = (t, extra = {}) => {
  const ev = { t, page: page.slice(0, 39), lang: (document.documentElement.lang || "").slice(0, 9), src: src(), w: Math.min(10000, Math.round(innerWidth)), ...extra };
  if (t !== "signup") ev.sid = sid;
  save("events", ev).catch(err => { if (location.hostname === "localhost") console.warn("track", err); });
  // Mirror the meaningful actions to Google Analytics (page views and scrolls it measures itself).
  const GA = { cta: "cta_click", signup: "sign_up", lang: "select_language" };
  if (GA[t] && typeof window.gtag === "function") window.gtag("event", GA[t], { page: ev.page, src: ev.src, lang: ev.lang });
};

// Shows a "still sending" note if the database has not confirmed within a few seconds.
// We never resend: the first write may still complete.
export const slowNote = (el, text) => setTimeout(() => { el.className = "msg"; el.textContent = text; }, 6000);
