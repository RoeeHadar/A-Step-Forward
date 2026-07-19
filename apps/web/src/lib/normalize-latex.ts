/**
 * Normalize over-escaped LaTeX from lesson seed data before KaTeX render.
 * JSON `\\\\lim` → parsed `\\lim` → KaTeX treats `\\` as a line break (broken math).
 *
 * IMPORTANT: `\\` is a legitimate ROW SEPARATOR inside matrix / cases / align
 * environments. Collapsing it there (e.g. `\\c` → `\c` in `\begin{pmatrix}a&b\\c&d`)
 * silently corrupts the matrix. So we protect those environments and only
 * collapse over-escaped commands OUTSIDE them.
 *
 * Keep this in sync with `scripts/lib/katex-check.mjs` (`normalizeLatexEscapes`).
 */
const MATH_ENV =
  /\\begin\{(pmatrix|bmatrix|Bmatrix|vmatrix|Vmatrix|matrix|smallmatrix|cases|aligned|aligned\*|align|align\*|alignat|alignat\*|array|gathered|gather|gather\*|split|multline|multline\*)\}[\s\S]*?\\end\{\1\}/g;

function collapseEscapes(text: string): string {
  let out = text;
  let prev = '';
  while (prev !== out) {
    prev = out;
    out = out.replace(/\\\\([a-zA-Z]+)/g, '\\$1');
    out = out.replace(/\\\\([,;:!])/g, '\\$1');
  }
  return out;
}

export function normalizeLatexInMarkdown(md: string): string {
  if (!md || !md.includes('\\\\')) return md;
  // Protect matrix/align/cases blocks whose `\\` are row separators.
  const blocks: string[] = [];
  const masked = md.replace(MATH_ENV, (m) => {
    blocks.push(m);
    return `\u0000ENV${blocks.length - 1}\u0000`;
  });
  const collapsed = collapseEscapes(masked);
  return collapsed.replace(/\u0000ENV(\d+)\u0000/g, (all, i) => blocks[Number(i)] ?? all);
}
