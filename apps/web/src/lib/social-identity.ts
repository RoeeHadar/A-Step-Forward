/**
 * Client + server shared identity validation (no DB / server-only imports).
 */

const USERNAME_RE = /^[a-z0-9_]{3,24}$/;
/** Latin letters, spaces, hyphen, apostrophe, period — real names may repeat. */
const REAL_NAME_RE = /^[A-Za-z]+(?:[ '\-.][A-Za-z]+)*$/;

/** Spaces → underscores, lowercase, strip other punctuation. */
export function normalizeUsername(raw: string): string {
  return raw
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_]/g, '')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '')
    .slice(0, 24);
}

export function validateUsername(username: string): string | null {
  const u = normalizeUsername(username);
  if (u.length < 3) {
    return 'Username must be at least 3 characters (English letters, numbers, underscore). Spaces become underscores.';
  }
  if (!USERNAME_RE.test(u)) {
    return 'Username must be 3–24 characters: English letters, numbers, and underscore only (no spaces).';
  }
  return null;
}

export function validateRealName(realName: string): string | null {
  const n = realName.trim().replace(/\s+/g, ' ');
  if (n.length < 2) return 'Real name is required (English letters).';
  if (n.length > 80) return 'Real name is too long.';
  if (!REAL_NAME_RE.test(n)) {
    return 'Real name must use English letters only (spaces, hyphen, and apostrophe allowed).';
  }
  return null;
}

export function suggestUsernameFromRealName(realName: string): string {
  return normalizeUsername(realName);
}
