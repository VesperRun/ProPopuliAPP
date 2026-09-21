export function safeReturnPath(path) {
  if (!path || typeof path !== "string") return "/hubs";
  if (!path.startsWith("/") || path.startsWith("//")) return "/hubs";
  return path;
}

export function authHref(basePath, returnPath) {
  const next = encodeURIComponent(safeReturnPath(returnPath));
  return `${basePath}?next=${next}`;
}
