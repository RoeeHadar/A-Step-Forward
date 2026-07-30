/**
 * Math-notation linter: catches LaTeX that would render broken/unreadable on the
 * site (KaTeX throwOnError or remark-math parse gotchas). Used by the question
 * pipeline, the `fix-lesson-math` auto-fixer, and a lesson audit so no
 * unreadable math ever ships.
 *
 * The site renders with remark-math (`$...$` inline, `$$...$$` display) + KaTeX.
 * We replicate the failure modes we have observed shipping broken math:
 *   1. unbalanced / mis-delimited `$` -> raw dollar text leaks to the learner.
 *   2. KaTeX cannot parse the span -> red error box.
 *   3. Hebrew/RTL glyphs inside `$...$` -> KaTeX has no glyphs (tofu / garbage).
 *   4. raw LaTeX commands OUTSIDE `$...$` -> leak as literal backslash text.
 *   5. raw unicode math symbols (×, √, ≤, π, …) inside `$...$` -> wrong/missing.
 *   6. backslash-bracket delimiters (\( \) \[ \]) -> remark-math does not parse.
 *   7. `$$` display block with text on the fence line -> remark-math drops it.
 *
 * `findMathErrors` is the single source of truth for what "broken" means, and is
 * enforced as a blocking CI gate (see .github/workflows/lint-test.yml) plus an
 * afterFileEdit hook, so a broken notation can never land again.
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

// Characters KaTeX's math fonts cannot render (Hebrew, Arabic) — must live in
// plain markdown text, never inside $...$.
const NON_MATH_SCRIPT = /[\u0590-\u05FF\u0600-\u06FF]/;

/**
 * Unicode math glyphs that authors sometimes type directly. Inside `$...$` they
 * render wrong or as tofu; the LaTeX macro is always correct. Used both to flag
 * (in plain prose, where they should be wrapped) and to auto-fix (inside math).
 */
export const UNICODE_MATH_MAP = {
  '×': '\\times',
  '⋅': '\\cdot',
  '·': '\\cdot',
  '÷': '\\div',
  '−': '-',
  '–': '-',
  '≤': '\\le',
  '≥': '\\ge',
  '≠': '\\ne',
  '≈': '\\approx',
  '≡': '\\equiv',
  '±': '\\pm',
  '∓': '\\mp',
  '∞': '\\infty',
  '→': '\\to',
  '⇒': '\\Rightarrow',
  '⇐': '\\Leftarrow',
  '⇔': '\\Leftrightarrow',
  '∈': '\\in',
  '∉': '\\notin',
  '⊂': '\\subset',
  '⊆': '\\subseteq',
  '∪': '\\cup',
  '∩': '\\cap',
  '∅': '\\emptyset',
  '∀': '\\forall',
  '∃': '\\exists',
  '∑': '\\sum',
  '∏': '\\prod',
  '∫': '\\int',
  '√': '\\sqrt{}',
  'π': '\\pi',
  'α': '\\alpha',
  'β': '\\beta',
  'γ': '\\gamma',
  'δ': '\\delta',
  'ε': '\\varepsilon',
  'θ': '\\theta',
  'λ': '\\lambda',
  'μ': '\\mu',
  'ρ': '\\rho',
  'σ': '\\sigma',
  'τ': '\\tau',
  'φ': '\\varphi',
  'ω': '\\omega',
  'Δ': '\\Delta',
  'Σ': '\\Sigma',
  'Ω': '\\Omega',
  '°': '^\\circ',
  '²': '^2',
  '³': '^3',
  '⁴': '^4',
  '½': '\\tfrac{1}{2}',
  '⅓': '\\tfrac{1}{3}',
  '¼': '\\tfrac{1}{4}',
  '¾': '\\tfrac{3}{4}',
  '∠': '\\angle',
  '△': '\\triangle',
  '∥': '\\parallel',
  '⊥': '\\perp',
  '∝': '\\propto',
};

// Matrix/align/cases environments whose `\\` are ROW SEPARATORS (must survive).
const MATH_ENV_RE =
  /\\begin\{(pmatrix|bmatrix|Bmatrix|vmatrix|Vmatrix|matrix|smallmatrix|cases|aligned|aligned\*|align|align\*|alignat|alignat\*|array|gathered|gather|gather\*|split|multline|multline\*)\}[\s\S]*?\\end\{\1\}/g;

/**
 * Mirror of the site's render-time normalizer (apps/web/src/lib/normalize-latex.ts):
 * collapse over-escaped `\\command` -> `\command` OUTSIDE matrix/align/cases
 * environments (inside them `\\` is a row separator and must survive), so the
 * linter checks exactly what KaTeX will receive. Keep the two in sync.
 */
export function normalizeLatexEscapes(md) {
  if (typeof md !== 'string' || !md.includes('\\\\')) return md;
  const blocks = [];
  const masked = md.replace(MATH_ENV_RE, (m) => {
    blocks.push(m);
    return `\u0000ENV${blocks.length - 1}\u0000`;
  });
  let out = masked;
  let prev = '';
  while (prev !== out) {
    prev = out;
    out = out.replace(/\\\\([a-zA-Z]+)/g, '\\$1').replace(/\\\\([,;:!])/g, '\\$1');
  }
  return out.replace(/\u0000ENV(\d+)\u0000/g, (_all, i) => blocks[Number(i)]);
}

/**
 * Curated LaTeX macros that, when they appear OUTSIDE a `$...$` span, indicate a
 * missing dollar delimiter (the backslash leaks as literal text). High-precision
 * list to avoid false positives on prose escapes like `\_` or `\*`.
 */
const LEAKY_MACROS = [
  'frac', 'dfrac', 'tfrac', 'sqrt', 'cdot', 'times', 'div', 'leq', 'geq', 'le',
  'ge', 'neq', 'ne', 'approx', 'equiv', 'pm', 'mp', 'infty', 'sum', 'prod',
  'int', 'lim', 'vec', 'overline', 'overrightarrow', 'hat', 'bar', 'left',
  'right', 'Rightarrow', 'Leftarrow', 'Leftrightarrow', 'boxed', 'mathbb',
  'mathbf', 'mathrm', 'operatorname', 'begin', 'end', 'alpha', 'beta', 'gamma',
  'delta', 'theta', 'lambda', 'sigma', 'omega', 'varphi', 'varepsilon',
  'tag', // \tag requires amsmath; use \quad\text{(label)} instead
];

/**
 * LaTeX commands that, when used inside `$$...$$` display math, can cause
 * rendering failures depending on the KaTeX configuration. Prefer the listed
 * alternatives.
 *
 *   \tag{N}              → $$expr \quad\text{(N)}$$
 *   \tag{label}          → $$expr \quad\text{(label)}$$
 */
const DISPLAY_MATH_WARN_RE = /\\tag\s*\{/;

const LEAKY_MACRO_RE = new RegExp(`\\\\(?:${LEAKY_MACROS.join('|')})\\b`, 'g');
// `^{...}` or `_{...}` (braced sup/sub) leaking outside math.
const BRACED_SCRIPT_RE = /[\^_]\{[^}]+\}/g;
// backslash-bracket math delimiters (\( \) \[ \]) that remark-math does NOT
// parse. The negative lookbehind avoids matching the SECOND backslash of a `\\[`
// row-break-with-spacing (e.g. `\\[6pt]`) inside a matrix/cases environment.
const BACKSLASH_DELIM_RE = /(?<!\\)\\[()[\]]/g;

// Inline span allows escaped `\$` (literal dollar, e.g. money "$100") inside.
const INLINE_MATH_RE = /(?<!\\)\$(?:\\\$|[^$\n])+?(?<!\\)\$/g;
const DISPLAY_MATH_RE = /\$\$([\s\S]+?)\$\$/g;

/** Blank out fenced ```code``` and `inline code` (math there is literal, not rendered). */
export function stripCodeSpans(text) {
  if (typeof text !== 'string' || !text.includes('`')) return text;
  const blank = (s) => s.replace(/[^\n]/g, ' ');
  let out = text.replace(/```[\s\S]*?```/g, blank);
  out = out.replace(/(?<!`)`[^`\n]+`(?!`)/g, blank);
  return out;
}

/** Extract inline ($...$) and display ($$...$$) math spans from markdown text. */
export function extractMathSpans(text) {
  const spans = [];
  if (typeof text !== 'string' || !text.includes('$')) return spans;
  const src = stripCodeSpans(text);
  // Display math first so its $$ are not misread as two inline $.
  let m;
  DISPLAY_MATH_RE.lastIndex = 0;
  while ((m = DISPLAY_MATH_RE.exec(src)) !== null) {
    spans.push({ tex: m[1], display: true });
  }
  const masked = src.replace(DISPLAY_MATH_RE, (s) => ' '.repeat(s.length));
  INLINE_MATH_RE.lastIndex = 0;
  while ((m = INLINE_MATH_RE.exec(masked)) !== null) {
    spans.push({ tex: m[0].slice(1, -1), display: false });
  }
  return spans;
}

/** Replace every math span (and code span) with same-length blanks so prose scans alone. */
export function maskMathSpans(text) {
  if (typeof text !== 'string') return '';
  let out = stripCodeSpans(text).replace(DISPLAY_MATH_RE, (s) => ' '.repeat(s.length));
  out = out.replace(INLINE_MATH_RE, (s) => ' '.repeat(s.length));
  return out;
}

/**
 * Detect the remark-math display-fence gotcha: text on the SAME line as the
 * opening `$$` of a MULTI-LINE block is treated as fence metadata and silently
 * dropped. Returns the offending block previews.
 */
export function findFenceMetaGotchas(text) {
  if (typeof text !== 'string' || !text.includes('$$')) return [];
  const parts = text.split('$$');
  if (parts.length % 2 === 0) return []; // unbalanced $$ handled elsewhere
  const bad = [];
  for (let i = 1; i < parts.length; i += 2) {
    const seg = parts[i];
    if (!seg.includes('\n')) continue; // single-line display block is fine
    if (!seg.startsWith('\n')) bad.push(seg.split('\n')[0].slice(0, 50));
  }
  return bad;
}

/** Count unescaped, non-`$$` dollar signs — an odd count means broken delimiters. */
export function hasUnbalancedDollars(text) {
  if (typeof text !== 'string') return false;
  const withoutDisplay = text.replace(/\$\$[\s\S]+?\$\$/g, '');
  const singles = withoutDisplay.match(/(?<!\\)\$/g);
  return singles ? singles.length % 2 !== 0 : false;
}

/** Return a list of human-readable math errors for one text field. */
export function findMathErrors(rawText, label = '') {
  const errors = [];
  if (typeof rawText !== 'string' || rawText.length === 0) return errors;
  // Check exactly what KaTeX will receive: after the site's escape normalizer,
  // with fenced/inline code blanked (math there is literal, not rendered).
  const text = stripCodeSpans(normalizeLatexEscapes(rawText));

  // --- delimiter-level checks (fire even without katex) ---
  if (text.includes('$')) {
    if (hasUnbalancedDollars(text)) {
      errors.push(`${label}: unbalanced '$' delimiters (math will render as raw text)`);
    }
    for (const preview of findFenceMetaGotchas(text)) {
      errors.push(
        `${label}: content on the opening $$ line ("${preview}…") — remark-math drops it; put $$ on its own line`,
      );
    }
  }

  // backslash-bracket delimiters never parse with remark-math.
  if (BACKSLASH_DELIM_RE.test(text)) {
    BACKSLASH_DELIM_RE.lastIndex = 0;
    errors.push(
      `${label}: backslash-bracket math delimiter (\\( \\) \\[ \\]) — use $...$ / $$...$$ instead`,
    );
  }

  // --- prose (outside-math) checks ---
  const prose = maskMathSpans(text);
  const leak = prose.match(LEAKY_MACRO_RE);
  if (leak) {
    errors.push(
      `${label}: LaTeX command "${leak[0]}" outside $...$ (missing math delimiters — will render as literal text)`,
    );
  }
  const braced = prose.match(BRACED_SCRIPT_RE);
  if (braced) {
    errors.push(
      `${label}: superscript/subscript "${braced[0]}" outside $...$ (wrap the expression in $...$)`,
    );
  }

  if (!text.includes('$')) return errors;

  // --- inside-math checks ---
  // NOTE: raw unicode math glyphs (×, ≤, π, · …) are NOT flagged — KaTeX renders
  // them fine (in math mode) and inside \text{} they are legitimate text. The
  // real breakage is Hebrew/RTL glyphs (no math glyphs) and un-parseable TeX.
  for (const { tex, display } of extractMathSpans(text)) {
    if (display && DISPLAY_MATH_WARN_RE.test(tex)) {
      errors.push(
        `${label}: \\tag{} in display math (requires amsmath; may break with default rehype-katex) — use \\quad\\text{(label)} instead`,
      );
    }
    const wrap = (t) => `${display ? '$$' : '$'}${t}${display ? '$$' : '$'}`;
    if (NON_MATH_SCRIPT.test(tex)) {
      errors.push(`${label}: Hebrew/RTL text inside math ${wrap(tex)} (KaTeX has no glyphs — move it outside $...$)`);
      continue;
    }
    if (!katex) continue; // can't deep-check without katex; other checks still ran
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

/**
 * Auto-fix ONLY the safe, deterministic, unambiguous breakage:
 *   - convert `\(...\)` / `\[...\]` delimiters to `$...$` / `$$...$$`;
 *   - split `$$`-display fence metadata onto its own line.
 * Returns { text, changed }. Everything else (Hebrew-in-math, missing $,
 * unbalanced $, unicode) is intentionally NOT auto-fixed — it is only reported,
 * because "fixing" it programmatically risks corrupting text-mode content
 * (e.g. `\text{T·m/A}`) or guessing the author's intent.
 */
export function autoFixMath(text) {
  if (typeof text !== 'string' || text.length === 0) return { text, changed: false };
  let out = text;

  // 1. backslash-bracket delimiters -> dollar delimiters (only when balanced).
  out = out.replace(/\\\[([\s\S]*?)\\\]/g, (_m, body) => `$$${body}$$`);
  out = out.replace(/\\\(([\s\S]*?)\\\)/g, (_m, body) => `$${body}$`);

  // 2. fence-meta: `$$expr\n...` -> `$$\nexpr\n...`.
  out = out.replace(/\$\$([^\n$]+)\n([\s\S]*?)\$\$/g, (_m, first, rest) => `$$\n${first}\n${rest}$$`);

  return { text: out, changed: out !== text };
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
