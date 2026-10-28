import { describe, expect, it } from 'vitest';
import kg from './kg-data.json';
import { CURRICULUM_CATEGORIES } from './curriculum-categories';
import { canonicalCourseRedirect, courseContainsConcept, coursesForConcept } from './concept-course';
import { getSiteUrl } from './site-url';
import { sitemapEntries } from '../app/sitemap';

const catalogIds = (c: (typeof CURRICULUM_CATEGORIES)[number]) => [
  ...c.concept_ids,
  ...c.sections.flatMap((s) => s.concept_ids ?? []),
];
const allCatalogIds = [...new Set(CURRICULUM_CATEGORIES.flatMap(catalogIds))];

describe('canonicalCourseRedirect (M4)', () => {
  it('keeps every lesson URL that a course page links to', () => {
    const moved: string[] = [];
    for (const c of CURRICULUM_CATEGORIES) {
      for (const id of catalogIds(c)) {
        if (canonicalCourseRedirect(c.id, id) !== null) moved.push(`${c.id}/${id}`);
      }
    }
    expect(moved).toEqual([]);
  });

  it('moves a lesson opened under the wrong course to the first course listing it, in one hop', () => {
    for (const id of allCatalogIds) {
      for (const c of CURRICULUM_CATEGORIES) {
        const target = canonicalCourseRedirect(c.id, id);
        if (target === null) {
          expect(courseContainsConcept(c.id, id)).toBe(true);
          continue;
        }
        expect(target).toBe(coursesForConcept(id)[0]);
        expect(courseContainsConcept(target, id)).toBe(true);
        expect(canonicalCourseRedirect(target, id)).toBeNull();
      }
      expect(canonicalCourseRedirect('math', id)).toBe(coursesForConcept(id)[0]);
    }
  });

  it('maps legacy course slugs to the canonical course id', () => {
    const c5 = CURRICULUM_CATEGORIES.find((c) => c.id === 'high_school_math_5pt');
    const id = c5?.concept_ids[0];
    expect(id).toBeTruthy();
    expect(canonicalCourseRedirect('high_school_math_5_points', id!)).toBe('high_school_math_5pt');
  });

  it('leaves concepts that are in no course catalog alone', () => {
    const kgOnly = (kg as { concepts: { id: string }[] }).concepts
      .map((c) => c.id)
      .filter((id) => coursesForConcept(id).length === 0);
    for (const id of kgOnly) {
      expect(canonicalCourseRedirect('calculus_1', id)).toBeNull();
      expect(canonicalCourseRedirect('math', id)).toBeNull();
    }
    expect(canonicalCourseRedirect('calculus_1', 'not_a_real_concept')).toBeNull();
  });
});

describe('getSiteUrl (M4)', () => {
  it('prefers the explicit override, then Vercel production domain, then vercel.app', () => {
    expect(getSiteUrl({ NEXT_PUBLIC_SITE_URL: 'https://example.org/', VERCEL_PROJECT_PRODUCTION_URL: 'x.vercel.app' })).toBe('https://example.org');
    expect(getSiteUrl({ VERCEL_PROJECT_PRODUCTION_URL: 'a-step-forward-waij.vercel.app' })).toBe('https://a-step-forward-waij.vercel.app');
    expect(getSiteUrl({})).toBe('https://a-step-forward-waij.vercel.app');
    expect(getSiteUrl({ NEXT_PUBLIC_SITE_URL: '  ' })).toBe('https://a-step-forward-waij.vercel.app');
  });
});

describe('sitemap (M4)', () => {
  it('lists unique absolute URLs, and every lesson URL is its own canonical', () => {
    const entries = sitemapEntries();
    const urls = entries.map((e) => e.url);
    expect(new Set(urls).size).toBe(urls.length);
    const origin = getSiteUrl();
    const lessonUrls = urls.filter((u) => u.includes('/concept/'));
    expect(lessonUrls.length).toBeGreaterThan(200);
    for (const u of urls) expect(u.startsWith(`${origin}/`)).toBe(true);
    for (const u of lessonUrls) {
      const m = new URL(u).pathname.match(/^\/learn\/([^/]+)\/concept\/([^/]+)$/);
      expect(m).not.toBeNull();
      expect(canonicalCourseRedirect(m![1] ?? '', m![2] ?? '')).toBeNull();
    }
  });
});
