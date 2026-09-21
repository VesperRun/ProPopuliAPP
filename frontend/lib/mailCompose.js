/** Open webmail compose in the tab — avoids OS mailto "pick an app" dialogs. */

function domain(email) {
  const part = email.trim().toLowerCase().split("@")[1];
  return part || "";
}

export function composeUrlForUserEmail(userEmail, { to, subject = "", body = "" } = {}) {
  const d = domain(userEmail);
  const q = (params) =>
    Object.entries(params)
      .filter(([, v]) => v)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join("&");

  if (d === "gmail.com" || d === "googlemail.com") {
    return `https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(to)}&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  }
  if (d === "proton.me" || d === "protonmail.com" || d === "pm.me") {
    return `https://mail.proton.me/inbox#composer?${q({ to, subject, body })}`;
  }
  if (["outlook.com", "hotmail.com", "live.com", "msn.com"].includes(d)) {
    return `https://outlook.live.com/mail/0/deeplink/compose?${q({ to, subject, body })}`;
  }
  if (d === "yahoo.com" || d.endsWith(".yahoo.com")) {
    return `https://compose.mail.yahoo.com/?${q({ to, subject, body })}`;
  }
  if (["icloud.com", "me.com", "mac.com"].includes(d)) {
    return `https://www.icloud.com/mail/`;
  }
  return null;
}
