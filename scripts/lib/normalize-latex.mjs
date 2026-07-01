/**
 * Collapse over-escaped LaTeX in parsed lesson strings before seed/bundle.
 * JSON `\\\\lim` → parsed `\\lim` → KaTeX treats `\\` as line break (broken in RTL).
 */
export function normalizeLatexInMarkdown(md) {
  if (!md || typeof md !== 'string' || !md.includes('\\\\')) return md;
  let out = md;
  let prev = '';
  while (prev !== out) {
    prev = out;
    out = out.replace(/\\\\([a-zA-Z]+)/g, '\\$1');
    out = out.replace(/\\\\([,;:!])/g, '\\$1');
  }
  return out;
}

const MD_STRING_KEYS = new Set([
  'body_en_md',
  'body_he_md',
  'checkpoint_solution_en',
  'checkpoint_solution_he',
  'stem_en',
  'stem_he',
  'explanation_en',
  'explanation_he',
  'rubric_en',
  'rubric_he',
  'summary_en',
  'summary_he',
  'title_en',
  'title_he',
]);

function normalizeMdStrings(obj) {
  if (!obj || typeof obj !== 'object') return;
  if (Array.isArray(obj)) {
    for (const item of obj) normalizeMdStrings(item);
    return;
  }
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      if (
        MD_STRING_KEYS.has(key) ||
        key.endsWith('_md') ||
        key.endsWith('_en') ||
        key.endsWith('_he') ||
        key.includes('solution')
      ) {
        obj[key] = normalizeLatexInMarkdown(value);
      }
    } else if (value && typeof value === 'object') {
      normalizeMdStrings(value);
    }
  }
}

/** Walk lesson object and normalize LaTeX in all markdown-bearing fields. */
export function normalizeLessonLatex(lesson) {
  normalizeMdStrings(lesson);
  return lesson;
}
