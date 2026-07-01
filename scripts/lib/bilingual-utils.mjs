/**
 * Bilingual quality helpers for lesson JSON.
 */

export function wordCount(text) {
  if (!text || typeof text !== 'string') return 0;
  const stripped = text
    .replace(/\$\$[\s\S]*?\$\$/g, ' MATH ')
    .replace(/\$[^$\n]+\$/g, ' MATH ')
    .replace(/[#*_`>\[\]()]/g, ' ');
  return stripped.split(/\s+/).filter((w) => w.length > 0).length;
}

export function hebrewCharRatio(text) {
  if (!text) return 0;
  const he = (text.match(/[\u0590-\u05FF]/g) || []).length;
  const lat = (text.match(/[a-zA-Z]{3,}/g) || []).length;
  return he / (he + lat + 1);
}

/** True when Hebrew body looks like English prose slipped in. */
export function hebrewBodyWeak(bodyHe, bodyEn) {
  const he = (bodyHe ?? '').trim();
  const en = (bodyEn ?? '').trim();
  if (!he) return true;
  if (!en) return hebrewCharRatio(he) < 0.12;
  const ratio = wordCount(he) / Math.max(wordCount(en), 1);
  if (ratio < 0.55) return true;
  if (hebrewCharRatio(he) < 0.15 && wordCount(he) > 25) return true;
  // Same opening English sentence
  const probe = en.slice(0, Math.min(60, en.length)).trim();
  if (probe.length > 20 && he.includes(probe)) return true;
  return false;
}

export const MIN_WORDS = {
  intro: { en: 110, he: 90 },
  definition: { en: 130, he: 110 },
  theory: { en: 160, he: 130 },
  worked_example: { en: 130, he: 110 },
  pitfall: { en: 100, he: 85 },
  why_matters: { en: 90, he: 75 },
  method_guide: { en: 100, he: 85 },
  before_exam: { en: 90, he: 75 },
  summary: { en: 70, he: 60 },
  practice_tip: { en: 60, he: 50 },
};

export const EXPAND_SECTION_KINDS = new Set([
  'intro',
  'definition',
  'theory',
  'worked_example',
  'pitfall',
  'why_matters',
  'method_guide',
  'before_exam',
  'summary',
  'practice_tip',
]);
