const BANNED = /sub\s*[-]?\s*reddits?/i;

export function contentPolicyViolation(...parts) {
  return parts.some((p) => p && BANNED.test(p));
}

export const CONTENT_POLICY_MESSAGE =
  "That wording isn't allowed on ProPopuli. Remove it and try again.";
