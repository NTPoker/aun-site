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
