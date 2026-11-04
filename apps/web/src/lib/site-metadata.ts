import type { Metadata } from 'next';

/**
 * Shared Open Graph / Twitter defaults. Next.js replaces (does not merge) a
 * nested metadata object like `openGraph` when a page sets it, so pages that
 * set their own og:url spread these to keep the site name and share image.
 */
export const SITE_NAME = 'A Step Forward';
export const SHARE_IMAGE = { url: '/og.png', width: 1200, height: 630, alt: SITE_NAME };

export function pageOpenGraph(
  og: NonNullable<Metadata['openGraph']>,
): NonNullable<Metadata['openGraph']> {
  return { type: 'website', siteName: SITE_NAME, images: [SHARE_IMAGE], ...og };
}

export function pageTwitter(
  tw: NonNullable<Metadata['twitter']> = {},
): NonNullable<Metadata['twitter']> {
  return { card: 'summary_large_image', images: [SHARE_IMAGE.url], ...tw };
}
