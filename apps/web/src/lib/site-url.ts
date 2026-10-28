/**
 * Absolute origin used for canonical URLs, og:url, robots.txt and the sitemap.
 *
 * Order: NEXT_PUBLIC_SITE_URL (explicit override) → Vercel's production domain
 * (VERCEL_PROJECT_PRODUCTION_URL, set by Vercel on every deployment, previews
 * included) → the current vercel.app address. No custom domain is live yet
 * (plan v2, M4 item 7), so the fallback is the vercel.app URL.
 */
const FALLBACK_SITE_URL = 'https://a-step-forward-waij.vercel.app';

function normalize(raw: string | undefined): string | null {
  const value = raw?.trim();
  if (!value) return null;
  const withScheme = /^https?:\/\//i.test(value) ? value : `https://${value}`;
  try {
    return new URL(withScheme).origin;
  } catch {
    return null;
  }
}

export function getSiteUrl(env: Record<string, string | undefined> = process.env): string {
  return (
    normalize(env.NEXT_PUBLIC_SITE_URL) ??
    normalize(env.VERCEL_PROJECT_PRODUCTION_URL) ??
    FALLBACK_SITE_URL
  );
}

export function absoluteUrl(pathname: string): string {
  return new URL(pathname, `${getSiteUrl()}/`).toString();
}
