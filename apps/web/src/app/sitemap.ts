import type { MetadataRoute } from 'next';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';
import { dedupeConceptIdsForCatalog } from '@/lib/concept-aliases';
import { isConceptInLessonIndex } from '@/lib/lesson-index';
import { aliasRedirectTarget, resolveLessonConceptId } from '@/lib/lesson-concept-resolve';
import { absoluteUrl } from '@/lib/site-url';

export const dynamic = 'force-dynamic';

/** Public pages only: home, booking, legal pages, the course list, each course,
 * and each authored lesson under every course that lists it. Alias ids are
 * resolved the same way the lesson page redirects them, so every URL is a 200. */
export function sitemapEntries(): MetadataRoute.Sitemap {
  const entries: MetadataRoute.Sitemap = [
    { url: absoluteUrl('/'), changeFrequency: 'weekly', priority: 1 },
    { url: absoluteUrl('/learn'), changeFrequency: 'weekly', priority: 0.9 },
    { url: absoluteUrl('/book'), changeFrequency: 'monthly', priority: 0.6 },
    ...['/privacy', '/terms', '/accessibility'].map((path) => ({
      url: absoluteUrl(path),
      changeFrequency: 'yearly' as const,
      priority: 0.2,
    })),
  ];
  const seen = new Set<string>();
  for (const category of CURRICULUM_CATEGORIES) {
    entries.push({ url: absoluteUrl(`/learn/${category.id}`), changeFrequency: 'weekly', priority: 0.8 });
    const ids = dedupeConceptIdsForCatalog(category.concept_ids);
    for (const catalogId of ids) {
      const id = aliasRedirectTarget(catalogId) ?? catalogId;
      const hasLesson = isConceptInLessonIndex(id) || isConceptInLessonIndex(resolveLessonConceptId(id));
      if (!hasLesson) continue;
      const url = absoluteUrl(`/learn/${category.id}/concept/${id}`);
      if (seen.has(url)) continue;
      seen.add(url);
      entries.push({ url, changeFrequency: 'monthly', priority: 0.7 });
    }
  }
  return entries;
}

export default function sitemap(): MetadataRoute.Sitemap {
  return sitemapEntries();
}
