/**
 * Two-tier question verification (docs/curriculum/lesson-rewrite-scope-map.md §"Verification").
 *
 * Tier 1 — deterministic re-derivation. A question may carry an optional `verify`
 * block. When present, CI re-computes the expression with a safe, dependency-free
 * evaluator and fails if it does not match the declared expected value (and, for
 * numeric questions, the question's own `correct_answer`).
 *
 *   "verify": { "expr": "2 + 2*3", "expected": 8, "tol": 1e-9 }
 *   "verify": { "expr": "deriv(x^2, x, 3)", "expected": 6 }   // numeric derivative at x=3
 *
 * Tier 2 — non-verifiable items (open/derivation/proof, or any item without a
 * `verify` block that is not itself a discrete-answer kind) MUST carry
 * `needs_review: true` and a full, multi-step worked solution. One-line solutions
 * are rejected.
 */

const FUNCS = {
  sqrt: Math.sqrt,
  cbrt: Math.cbrt,
  abs: Math.abs,
  sin: Math.sin,
  cos: Math.cos,
  tan: Math.tan,
  asin: Math.asin,
  acos: Math.acos,
  atan: Math.atan,
  sinh: Math.sinh,
  cosh: Math.cosh,
  tanh: Math.tanh,
  ln: Math.log,
  log: (x, b) => (b === undefined ? Math.log10(x) : Math.log(x) / Math.log(b)),
  log2: Math.log2,
  exp: Math.exp,
  floor: Math.floor,
  ceil: Math.ceil,
  round: Math.round,
  sign: Math.sign,
  pow: Math.pow,
  min: Math.min,
  max: Math.max,
  fact: (n) => {
    if (n < 0 || !Number.isInteger(n)) return NaN;
    let r = 1;
    for (let i = 2; i <= n; i += 1) r *= i;
    return r;
  },
  choose: (n, k) => {
    if (k < 0 || k > n || !Number.isInteger(n) || !Number.isInteger(k)) return NaN;
    let r = 1;
    for (let i = 0; i < k; i += 1) r = (r * (n - i)) / (i + 1);
    return Math.round(r);
  },
  // Numerical derivative of f(var) at point: deriv(<expr>, <var>, <point>)
  deriv: null, // handled specially below (needs sub-expression)
};

const CONSTS = { pi: Math.PI, e: Math.E, tau: 2 * Math.PI };

// Tokenizer -----------------------------------------------------------------
function tokenize(src) {
  const tokens = [];
  let i = 0;
  const s = src.replace(/\s+/g, '');
  while (i < s.length) {
    const c = s[i];
    if (/[0-9.]/.test(c)) {
      let j = i + 1;
      while (j < s.length && /[0-9.eE]/.test(s[j])) {
        // allow scientific notation e.g. 1e-9
        if ((s[j] === 'e' || s[j] === 'E') && (s[j + 1] === '+' || s[j + 1] === '-')) j += 1;
        j += 1;
      }
      tokens.push({ t: 'num', v: parseFloat(s.slice(i, j)) });
      i = j;
    } else if (/[a-zA-Z_]/.test(c)) {
      let j = i + 1;
      while (j < s.length && /[a-zA-Z_0-9]/.test(s[j])) j += 1;
      tokens.push({ t: 'name', v: s.slice(i, j) });
      i = j;
    } else if ('+-*/^%(),'.includes(c)) {
      tokens.push({ t: 'op', v: c });
      i += 1;
    } else {
      throw new Error(`bad char '${c}' in expression`);
    }
  }
  return tokens;
}

// Recursive-descent parser → evaluator (with a variable scope) --------------
function makeParser(tokens) {
  let pos = 0;
  const peek = () => tokens[pos];
  const next = () => tokens[pos++];
  const expect = (v) => {
    const tk = next();
    if (!tk || tk.v !== v) throw new Error(`expected '${v}'`);
  };

  function parseExpr(scope) {
    let left = parseTerm(scope);
    while (peek() && peek().t === 'op' && (peek().v === '+' || peek().v === '-')) {
      const op = next().v;
      const right = parseTerm(scope);
      left = op === '+' ? left + right : left - right;
    }
    return left;
  }

  function parseTerm(scope) {
    let left = parseUnary(scope);
    while (peek() && peek().t === 'op' && (peek().v === '*' || peek().v === '/' || peek().v === '%')) {
      const op = next().v;
      const right = parseUnary(scope);
      if (op === '*') left *= right;
      else if (op === '/') left /= right;
      else left %= right;
    }
    return left;
  }

  // Unary binds looser than exponentiation: -2^2 === -(2^2).
  function parseUnary(scope) {
    if (peek() && peek().t === 'op' && (peek().v === '-' || peek().v === '+')) {
      const op = next().v;
      const v = parseUnary(scope);
      return op === '-' ? -v : v;
    }
    return parsePow(scope);
  }

  // Exponentiation is right-associative; the exponent may carry its own sign.
  function parsePow(scope) {
    const base = parsePrimary(scope);
    if (peek() && peek().t === 'op' && peek().v === '^') {
      next();
      const exp = parseUnary(scope);
      return Math.pow(base, exp);
    }
    return base;
  }

  function parsePrimary(scope) {
    const tk = next();
    if (!tk) throw new Error('unexpected end of expression');
    if (tk.t === 'num') return tk.v;
    if (tk.t === 'op' && tk.v === '(') {
      const v = parseExpr(scope);
      expect(')');
      return v;
    }
    if (tk.t === 'name') {
      // function call?
      if (peek() && peek().t === 'op' && peek().v === '(') {
        // capture raw arg expressions for special functions (deriv)
        return parseCall(tk.v, scope);
      }
      if (tk.v in scope) return scope[tk.v];
      if (tk.v in CONSTS) return CONSTS[tk.v];
      throw new Error(`unknown symbol '${tk.v}'`);
    }
    throw new Error(`unexpected token '${tk.v}'`);
  }

  function parseCall(name, scope) {
    expect('(');
    if (name === 'deriv') {
      // deriv(<expr>, <var>, <point>) — numeric central difference.
      const exprTokens = captureArg();
      expect(',');
      const varTk = next();
      if (!varTk || varTk.t !== 'name') throw new Error('deriv: 2nd arg must be a variable');
      expect(',');
      const point = parseExpr(scope);
      expect(')');
      const h = 1e-6;
      const f = (x) => {
        const p = makeParser(exprTokens);
        return p.parseExpr({ ...scope, [varTk.v]: x });
      };
      return (f(point + h) - f(point - h)) / (2 * h);
    }
    const args = [parseExpr(scope)];
    while (peek() && peek().t === 'op' && peek().v === ',') {
      next();
      args.push(parseExpr(scope));
    }
    expect(')');
    const fn = FUNCS[name];
    if (typeof fn !== 'function') throw new Error(`unknown function '${name}'`);
    return fn(...args);
  }

  // Capture the token slice for the first argument (up to the matching comma at depth 0).
  function captureArg() {
    const start = pos;
    let depth = 0;
    while (pos < tokens.length) {
      const tk = tokens[pos];
      if (tk.t === 'op' && tk.v === '(') depth += 1;
      else if (tk.t === 'op' && tk.v === ')') {
        if (depth === 0) break;
        depth -= 1;
      } else if (tk.t === 'op' && tk.v === ',' && depth === 0) {
        break;
      }
      pos += 1;
    }
    return tokens.slice(start, pos);
  }

  return { parseExpr };
}

export function evalExpr(src, scope = {}) {
  const tokens = tokenize(src);
  const parser = makeParser(tokens);
  const v = parser.parseExpr(scope);
  if (typeof v !== 'number' || Number.isNaN(v)) {
    throw new Error(`expression did not evaluate to a number: '${src}'`);
  }
  return v;
}

// Kinds whose answer key is discrete / string-checkable at grade time. Only the
// genuinely open kinds (open, derivation) fall through to the Tier-2 requirement.
const DETERMINISTIC_KINDS = new Set([
  'mcq',
  'mcq_multi',
  'true_false',
  'fill_blank',
  'numeric',
  'match',
  'ordering',
  'short_answer',
]);

function wordCount(s) {
  return String(s ?? '').trim().split(/\s+/).filter(Boolean).length;
}

function hasMultiStepSolution(q) {
  const en = q.explanation_en ?? q.explanation ?? q.answer_payload?.explanation_en ?? '';
  const he = q.explanation_he ?? q.answer_payload?.explanation_he ?? '';
  const enWords = wordCount(en);
  const heWords = wordCount(he);
  // Multi-step = multiple sentences/lines or a step marker, and not a one-liner.
  const stepish = /(\n|;|\.|→|=>|step|שלב)/i.test(en);
  return enWords >= 25 && heWords >= 15 && stepish;
}

/**
 * @returns {{ checked: boolean, ok: boolean, reason?: string }}
 */
export function verifyQuestion(q) {
  // Tier 1: explicit verify block → re-derive.
  if (q.verify && typeof q.verify === 'object') {
    const { expr, expected, tol } = q.verify;
    if (typeof expr !== 'string' || expected === undefined) {
      return { checked: true, ok: false, reason: 'verify block missing expr/expected' };
    }
    let got;
    try {
      got = evalExpr(expr, q.verify.scope ?? {});
    } catch (err) {
      return { checked: true, ok: false, reason: `verify eval error: ${err.message}` };
    }
    const tolerance = typeof tol === 'number' ? tol : 1e-6;
    if (Math.abs(got - Number(expected)) > tolerance) {
      return { checked: true, ok: false, reason: `verify mismatch: expr=${got} vs expected=${expected}` };
    }
    // Cross-check against the question's declared answer for numeric kinds.
    if (q.kind === 'numeric' && q.correct_answer !== undefined && q.correct_answer !== null) {
      const declared = Number(q.correct_answer);
      if (!Number.isNaN(declared) && Math.abs(got - declared) > tolerance) {
        return {
          checked: true,
          ok: false,
          reason: `verify vs correct_answer mismatch: ${got} vs ${declared}`,
        };
      }
    }
    return { checked: true, ok: true };
  }

  // Tier 2: no verify block. Non-deterministic kinds must be flagged + solved.
  if (!DETERMINISTIC_KINDS.has(q.kind)) {
    if (q.needs_review !== true) {
      return { checked: false, ok: false, reason: `non-verifiable kind '${q.kind}' must set needs_review:true` };
    }
    if (!hasMultiStepSolution(q)) {
      return { checked: false, ok: false, reason: `non-verifiable kind '${q.kind}' needs a full multi-step worked solution (no one-liners)` };
    }
    return { checked: false, ok: true };
  }

  // Deterministic kind with no verify block: allowed (answer is discrete/self-declared),
  // but still no one-line solutions for the harder ones.
  return { checked: false, ok: true };
}

export { DETERMINISTIC_KINDS };
