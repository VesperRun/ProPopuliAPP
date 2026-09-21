/** URL path for a subpop (hub). Display uses backslash: s\slug */
export function subpopPath(slug) {
  return `/s/${slug}`;
}

export function subpopLabel(slug) {
  return `s\\${slug}`;
}
