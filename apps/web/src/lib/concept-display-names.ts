/**
 * Resolve human-readable concept/lesson titles from opaque IDs stored in
 * `concept_mastery`. Diagnostic seeds and legacy rows sometimes use shortened
 * slugs (`derivatives`, `integrals`) that do not match KG node ids
 * (`derivatives_intro`) or lesson ids — this helper unifies display.
 */
import kg from './kg-data.json';
import lessonsIndex from './lessons-index.generated.json';

interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
}

interface LessonIndexEntry {
  id: string;
  title_en: string;
  title_he?: string;
}

const kgById: Record<string, KgConcept> = (kg as { byId: Record<string, KgConcept> }).byId;
const lessons = lessonsIndex as LessonIndexEntry[];
const lessonsById = new Map(lessons.map((l) => [l.id, l]));

/** Common abbreviated slugs → bilingual labels. */
const CHAPTER_ALIASES: Record<string, { en: string; he: string }> = {
  derivatives: { en: 'Derivatives', he: 'נגזרות' },
  integrals: { en: 'Integrals', he: 'אינטגרלים' },
  sequences: { en: 'Sequences & Series', he: 'סדרות וטורים' },
  trigonometry: { en: 'Trigonometry', he: 'טריגונומטריה' },
  limits: { en: 'Limits', he: 'גבולות' },
  functions: { en: 'Functions', he: 'פונקציות' },
  probability: { en: 'Probability', he: 'הסתברות' },
  statistics: { en: 'Statistics', he: 'סטטיסטיקה' },
  vectors: { en: 'Vectors', he: 'וקטורים' },
  kinematics: { en: 'Kinematics', he: 'קינמטיקה' },
  electricity: { en: 'Electricity', he: 'חשמל' },
  optics: { en: 'Optics', he: 'אופטיקה' },
  gravitation: { en: 'Gravitation', he: 'כבידה' },
  uni_vector_fields: { en: 'Vector Fields (Calculus)', he: 'שדות וקטוריים' },
  uni_multivariable: { en: 'Multivariable Calculus', he: 'חדו״א רב-משתני' },
  calculus: { en: 'Calculus', he: 'חשבון דифרנציאלי ואינטגרלי' },
};

function humanizeId(id: string): string {
  return id
    .replace(/^uni_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

function findPrefixMatch<T extends { id: string }>(
  id: string,
  items: T[],
): T | undefined {
  if (items.find((x) => x.id === id)) return items.find((x) => x.id === id);
  return items.find((x) => x.id.startsWith(`${id}_`) || x.id.startsWith(`${id}-`));
}

export interface ConceptTitles {
  title_en: string;
  title_he: string | null;
}

export function resolveConceptTitles(
  conceptId: string,
  lessonMeta?: { title_en: string | null; title_he: string | null } | null,
): ConceptTitles {
  if (lessonMeta?.title_en) {
    return {
      title_en: lessonMeta.title_en,
      title_he: lessonMeta.title_he ?? null,
    };
  }

  const lesson = lessonsById.get(conceptId) ?? findPrefixMatch(conceptId, lessons);
  if (lesson) {
    return {
      title_en: lesson.title_en,
      title_he: lesson.title_he ?? null,
    };
  }

  const kgInfo = kgById[conceptId] ?? findPrefixMatch(conceptId, Object.values(kgById));
  if (kgInfo) {
    return { title_en: kgInfo.name, title_he: kgInfo.name_he };
  }

  const alias = CHAPTER_ALIASES[conceptId];
  if (alias) {
    return { title_en: alias.en, title_he: alias.he };
  }

  const base = conceptId.split('_')[0] ?? conceptId;
  const baseAlias = CHAPTER_ALIASES[base];
  if (baseAlias) {
    return { title_en: baseAlias.en, title_he: baseAlias.he };
  }

  return { title_en: humanizeId(conceptId), title_he: null };
}

export function pickConceptTitle(titles: ConceptTitles, locale: 'en' | 'he'): string {
  if (locale === 'he' && titles.title_he) return titles.title_he;
  return titles.title_en;
}
