const BANNED = /sub\s*[-]?\s*reddits?/i;

const HUB_DISALLOWED =
  /(p[o0]rn|xxx|nsfw|onlyfans|hentai|nude|nudes|gonewild|camgirl|camming|stripper|stripclub|hookup|hookups|fwb|personals|escort|escorts|sugar[\s-]?daddy|sugar[\s-]?baby|kink|bdsm|swinger|swingers|fetish|dating[\s-]?sex|singles[\s-]?only|cocaine|fentanyl|heroin|methamphetamine|\bmeth\b|carding|counterfeit|guns[\s-]?for[\s-]?sale|darknet|dark[\s-]?web[\s-]?market)/i;

function normalizeHubText(text) {
  return text.toLowerCase().replace(/0/g, "o").replace(/1/g, "i").replace(/3/g, "e").replace(/4/g, "a");
}

export function contentPolicyViolation(...parts) {
  return parts.some((p) => p && BANNED.test(p));
}

export function hubPolicyViolation(...parts) {
  return parts.some((p) => {
    if (!p) return false;
    return HUB_DISALLOWED.test(p) || HUB_DISALLOWED.test(normalizeHubText(p));
  });
}

export const CONTENT_POLICY_MESSAGE =
  "That wording isn't allowed on ProPopuli. Remove it and try again.";

export const HUB_POLICY_MESSAGE =
  "This subpop name or description is not allowed on ProPopuli.";

/** Pre-seeded Austin / San Antonio corridor slugs (for /hubs grouping). */
export const CORRIDOR_HUB_SLUGS = new Set([
  "austin",
  "spurs-fans",
  "san-antonio",
  "austin-tables",
  "univ-tex-austin",
  "austin-answers",
  "austin-sendup",
  "univ-tex-sports",
  "austin-hiring",
  "san-marcos",
  "round-rock",
  "austin-swap",
  "austin-soccer",
  "zilker-fest",
  "austin-plots",
  "utsa",
  "austin-meetups",
  "pflugerville",
  "boerne",
  "austin-wheels",
  "cedar-park",
  "texas-state",
  "georgetown-tx",
  "south-by-southwest",
  "new-braunfels",
  "univ-tex-admit",
  "leander",
  "austin-taps",
  "spurs-bench",
  "sa-tables",
  "austin-rooms",
  "austin-families",
  "austin-bands",
  "bastrop",
  "austin-stages",
]);

export const PLATFORM_HUB_SLUGS = new Set(["general", "build"]);
