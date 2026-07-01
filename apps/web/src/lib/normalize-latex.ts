/**
 * Normalize over-escaped LaTeX from lesson seed data before KaTeX render.
 * JSON `\\\\lim` → parsed `\\lim` → KaTeX treats `\\` as line break (broken math in RTL).
 */
export function normalizeLatexInMarkdown(md: string): string {
  if (!md || !md.includes('\\\\')) return md;
  let out = md;
  let prev = '';
  while (prev !== out) {
    prev = out;
    out = out.replace(/\\\\([a-zA-Z]+)/g, '\\$1');
    out = out.replace(/\\\\([,;:!])/g, '\\$1');
  }
  return out;
}
