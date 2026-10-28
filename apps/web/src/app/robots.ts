import type { MetadataRoute } from 'next';
import { absoluteUrl } from '@/lib/site-url';

export const dynamic = 'force-dynamic';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [{ userAgent: '*', allow: '/', disallow: ['/api/', '/admin', '/educator', '/app'] }],
    sitemap: absoluteUrl('/sitemap.xml'),
  };
}
