/**
 * Lightweight in-process sliding-window rate limiter for social discovery APIs.
 * Best-effort on serverless (per-instance); still blocks obvious scrapers.
 */
const buckets = new Map<string, number[]>();

export function checkSocialRateLimit(
  key: string,
  opts: { limit: number; windowMs: number } = { limit: 30, windowMs: 60_000 },
): { ok: true } | { ok: false; retryAfterSec: number } {
  const now = Date.now();
  const windowStart = now - opts.windowMs;
  const prev = buckets.get(key) ?? [];
  const recent = prev.filter((t) => t >= windowStart);
  if (recent.length >= opts.limit) {
    const oldest = recent[0] ?? now;
    const retryAfterSec = Math.max(1, Math.ceil((oldest + opts.windowMs - now) / 1000));
    buckets.set(key, recent);
    return { ok: false, retryAfterSec };
  }
  recent.push(now);
  buckets.set(key, recent);
  // Bound map size on long-lived processes
  if (buckets.size > 5000) {
    const first = buckets.keys().next().value;
    if (first) buckets.delete(first);
  }
  return { ok: true };
}
