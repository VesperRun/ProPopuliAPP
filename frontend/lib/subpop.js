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

/** Case- and numeric-aware slug order (e.g. aries1, Aries1, aries2, aries10). */
const slugCollator = new Intl.Collator(undefined, { numeric: true, sensitivity: "base" });

export function compareSubpopSlugs(a, b) {
  return slugCollator.compare(String(a), String(b));
}

export function sortHubsBySlug(hubs) {
  return [...hubs].sort((x, y) => compareSubpopSlugs(x.slug, y.slug));
}

/**
 * Subpop directory order: higher participant_count first, then slug (numeric-aware).
 * When counts are tied (often all zero early on), order matches pure slug sort.
 */
export function sortHubsForDisplay(hubs) {
  return [...hubs].sort((a, b) => {
    const pa = a.participant_count ?? 0;
    const pb = b.participant_count ?? 0;
    if (pb !== pa) return pb - pa;
    return compareSubpopSlugs(a.slug, b.slug);
  });
}
