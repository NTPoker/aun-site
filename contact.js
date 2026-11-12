import { save, slowNote } from "./fb.js?v=20261112c";

const form = document.getElementById("cform");
const out = document.getElementById("cmsgout");
const send = document.getElementById("csend");
const ja = () => document.documentElement.lang === "ja";
const say = (cls, j, e) => { out.className = "msg " + cls; out.textContent = ja() ? j : e; };

form.addEventListener("submit", async e => {
  e.preventDefault();
  const email = document.getElementById("cemail").value.trim();
  const message = document.getElementById("cmsg").value.trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return say("err", "メールアドレスを確認してください。", "Please check your email address.");
  if (!message) return say("err", "内容を書いてください。", "Please write a message.");
  if (!document.getElementById("cagree").checked) return say("err", "同意のチェックを入れてください。", "Please tick the consent box.");
  send.disabled = true;
  const slow = slowNote(out, ja() ? "送信を確認しています。このままお待ちください。" : "Still sending. Please keep this page open.");
  try {
    await save("contacts", { email, topic: document.getElementById("ctopic").value, message, lang: document.documentElement.lang, consent: true });
    form.reset();
    say("ok", "送りました。ありがとうございます。", "Sent. Thank you.");
  } catch (err) {
    console.error(err);
    say("err", "送れませんでした。時間をおいて、もう一度お試しください。", "Couldn’t send. Please try again later.");
  } finally {
    clearTimeout(slow);
    send.disabled = false;
  }
});
