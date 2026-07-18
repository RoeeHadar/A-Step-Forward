/**
 * Math-notation linter: catches LaTeX that would render broken/unreadable on the
 * site (KaTeX throwOnError or remark-math parse gotchas). Used by the question
 * pipeline and a lesson audit so no unreadable math ever ships.
 *
 * The site renders with remark-math (`$...$` inline, `$$...$$` display) + KaTeX.
 * We replicate the two failure modes:
 *   1. unbalanced / mis-delimited `$` -> raw dollar text leaks to the learner.
 *   2. KaTeX cannot parse the span -> red error box.
 */
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(path.join(process.cwd(), 'apps/web/package.json'));
let katex;
try {
  katex = require('katex');
} catch {
  katex = null;
}

/** Extract inline ($...$) and display ($$...$$) math spans from markdown text. */
export function extractMathSpans(text) {
  const spans = [];
  if (typeof text !== 'string' || !text.includes('$')) return spans;
  // Display math first so its $$ are not misread as two inline $.
  const display = /\$\$([\s\S]+?)\$\$/g;
  let masked = text;
  let m;
  while ((m = display.exec(text)) !== null) {
    spans.push({ tex: m[1], display: true });
  }
  masked = text.replace(display, (s) => ' '.repeat(s.length));
  // Inline: a $...$ pair on a single line, no unescaped $ inside.
  const inline = /(?<!\\)\$([^$\n]+?)(?<!\\)\$/g;
  while ((m = inline.exec(masked)) !== null) {
    spans.push({ tex: m[1], display: false });
  }
  return spans;
}

/** Count unescaped, non-`$$` dollar signs — an odd count means broken delimiters. */
export function hasUnbalancedDollars(text) {
  if (typeof text !== 'string') return false;
  const withoutDisplay = text.replace(/\$\$[\s\S]+?\$\$/g, '');
  const singles = withoutDisplay.match(/(?<!\\)\$/g);
  return singles ? singles.length % 2 !== 0 : false;
}

// Characters KaTeX's math fonts cannot render (Hebrew, Arabic) — must live in
// plain markdown text, never inside $...$.
const NON_MATH_SCRIPT = /[\u0590-\u05FF\u0600-\u06FF]/;

/** Return a list of human-readable math errors for one text field. */
export function findMathErrors(text, label = '') {
  const errors = [];
  if (typeof text !== 'string' || !text.includes('$')) return errors;
  if (hasUnbalancedDollars(text)) {
    errors.push(`${label}: unbalanced '$' delimiters (math will render as raw text)`);
  }
  if (!katex) return errors; // can't deep-check without katex; delimiter check still ran
  for (const { tex, display } of extractMathSpans(text)) {
    const wrap = (t) => `${display ? '$$' : '$'}${t}${display ? '$$' : '$'}`;
    if (NON_MATH_SCRIPT.test(tex)) {
      errors.push(`${label}: Hebrew/RTL text inside math ${wrap(tex)} (KaTeX has no glyphs — move it outside $...$)`);
      continue;
    }
    // KaTeX reports missing glyphs / bad spacing via console.warn, not throw.
    const warnings = [];
    const origWarn = console.warn;
    const origError = console.error;
    console.warn = (...a) => warnings.push(a.join(' '));
    console.error = (...a) => warnings.push(a.join(' '));
    try {
      katex.renderToString(tex, { throwOnError: true, strict: false, displayMode: display });
      if (warnings.length) {
        errors.push(`${label}: KaTeX warning on ${wrap(tex)} — ${warnings[0].split('\n')[0]}`);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message.split('\n')[0] : String(err);
      errors.push(`${label}: KaTeX cannot render ${wrap(tex)} — ${msg}`);
    } finally {
      console.warn = origWarn;
      console.error = origError;
    }
  }
  return errors;
}

/** Collect all learner-visible text fields from a lesson question. */
export function questionMathFields(q, i) {
  const out = [];
  const push = (v, name) => {
    if (typeof v === 'string') out.push([v, `q[${i}].${name}`]);
    else if (Array.isArray(v)) v.forEach((s, k) => typeof s === 'string' && out.push([s, `q[${i}].${name}[${k}]`]));
  };
  push(q.stem_en, 'stem_en');
  push(q.stem_he, 'stem_he');
  push(q.explanation_en, 'explanation_en');
  push(q.explanation_he, 'explanation_he');
  push(q.options_en, 'options_en');
  push(q.options_he, 'options_he');
  push(q.answer_payload?.options_en, 'answer_payload.options_en');
  push(q.answer_payload?.options_he, 'answer_payload.options_he');
  push(q.answer_payload?.steps_en, 'answer_payload.steps_en');
  push(q.answer_payload?.steps_he, 'answer_payload.steps_he');
  push(q.rubric_en, 'rubric_en');
  push(q.rubric_he, 'rubric_he');
  return out;
}
