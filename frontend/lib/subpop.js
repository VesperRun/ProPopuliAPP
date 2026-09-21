/** URL path for a subpop (hub). Display uses backslash: s\slug */
export function subpopPath(slug) {
  return `/s/${slug}`;
}

export function subpopLabel(slug) {
  return `s\\${slug}`;
}

/** Strip decorative s\ or s/ prefix if user pastes full symbolic name. */
export function normalizeSubpopSlug(raw) {
  let s = raw.trim().toLowerCase();
  if (s.startsWith("s\\") || s.startsWith("s/")) {
    s = s.slice(2);
  }
  return s;
}
