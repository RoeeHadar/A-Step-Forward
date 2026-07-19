/**
 * Guards for the math-notation linter (the "won't break again" gate).
 * Run: node --test scripts/lib/katex-check.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  findMathErrors,
  autoFixMath,
  normalizeLatexEscapes,
  maskMathSpans,
} from './katex-check.mjs';

test('clean inline + display math produces no errors', () => {
  assert.deepEqual(findMathErrors('The slope is $\\frac{1}{2}$ here.'), []);
  assert.deepEqual(findMathErrors('$$\\int_0^1 x\\,dx = \\tfrac{1}{2}$$'), []);
});

test('matrix / cases row breaks (\\\\) are preserved, not flagged', () => {
  // In-memory string as it reaches the renderer: `\\` is a real row separator.
  const m = 'Matrix $A=\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}$ done.';
  assert.deepEqual(findMathErrors(m), [], 'row-break matrix must be clean');
  const cases = '$$f(x)=\\begin{cases}1&x\\in\\mathbb{Q}\\\\0&x\\notin\\mathbb{Q}\\end{cases}$$';
  assert.deepEqual(findMathErrors(cases), []);
});

test('row-break spacing \\\\[6pt] is not mistaken for a \\[ delimiter', () => {
  const s = '$$\\begin{cases}a&x>0\\\\[6pt]b&x\\le 0\\end{cases}$$';
  assert.deepEqual(findMathErrors(s), []);
});

test('the site escape-normalizer preserves matrix rows but collapses \\\\lim', () => {
  assert.equal(normalizeLatexEscapes('\\\\lim_{x\\to0}'), '\\lim_{x\\to0}');
  const kept = normalizeLatexEscapes('\\begin{pmatrix}a\\\\b\\end{pmatrix}');
  assert.ok(kept.includes('a\\\\b'), 'row break inside pmatrix must survive');
});

test('Hebrew inside math is flagged', () => {
  const errs = findMathErrors('The value $x = \\text{מרחק}$ here.');
  assert.equal(errs.length, 1);
  assert.match(errs[0], /Hebrew\/RTL/);
});

test('raw LaTeX leaking outside $...$ is flagged', () => {
  const errs = findMathErrors('The slope is \\frac{1}{2} of the run.');
  assert.ok(errs.some((e) => /outside \$/.test(e)));
});

test('braced sup/sub outside math is flagged', () => {
  const errs = findMathErrors('As x^{0.1} grows...');
  assert.ok(errs.some((e) => /superscript\/subscript/.test(e)));
});

test('backslash-bracket delimiters are flagged', () => {
  const errs = findMathErrors('Compute \\(x+1\\) now.');
  assert.ok(errs.some((e) => /backslash-bracket/.test(e)));
});

test('unbalanced $ is flagged', () => {
  const errs = findMathErrors('Half of $x is missing.');
  assert.ok(errs.some((e) => /unbalanced/.test(e)));
});

test('math inside fenced/inline code is ignored (literal, not rendered)', () => {
  assert.deepEqual(findMathErrors('```\nGiven lim_{x→a} f(x)\n```'), []);
  assert.deepEqual(findMathErrors('Use `x^{2}` in the API.'), []);
});

test('escaped \\$ (money) inside math does not desync the parser', () => {
  assert.deepEqual(findMathErrors('Start with $\\$100$ and $\\times 0.8$ gives $\\$80$.'), []);
});

test('unicode math glyphs render fine and are NOT flagged (math or \\text)', () => {
  assert.deepEqual(findMathErrors('$x \\le 5$ and $30°$ and $\\text{T·m/A}$'), []);
});

test('autoFixMath converts backslash-bracket delimiters, leaves the rest', () => {
  assert.equal(autoFixMath('\\(x+1\\)').text, '$x+1$');
  assert.equal(autoFixMath('\\[y=2\\]').text, '$$y=2$$');
  // does NOT touch matrix content
  assert.equal(autoFixMath('\\begin{pmatrix}a\\\\b\\end{pmatrix}').changed, false);
});

test('maskMathSpans blanks math + code, keeps prose length', () => {
  const t = 'a $x+1$ b';
  assert.equal(maskMathSpans(t).length, t.length);
  assert.ok(!maskMathSpans(t).includes('x+1'));
});
