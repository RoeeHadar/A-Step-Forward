/**
 * Sympy-backed CAS runner — fills the `casRunner` hook in question-verifier.mjs.
 *
 * A part opts into CAS by carrying a `verify` spec (see scripts/gen/cas_check.py
 * for the shapes). The runner shells out to Python/sympy for an independent
 * ground-truth recomputation, so the verdict never depends on the value stored
 * in the item. Parts without a `verify` spec return { supported: false } and
 * fall through to the LLM/human tiers.
 */
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const CAS_SCRIPT = path.join(here, '..', 'gen', 'cas_check.py');

function firstClaimed(part) {
  const ap = part.answer_payload ?? {};
  if (ap.value !== undefined && ap.value !== null) return String(ap.value);
  if (Array.isArray(ap.acceptable_answers) && ap.acceptable_answers.length > 0) {
    return String(ap.acceptable_answers[0]);
  }
  return undefined;
}

/**
 * @param {{ python?: string }} [opts]
 * @returns {(part:object)=>Promise<{supported:boolean,matches:boolean,computed?:string,details?:string}>}
 */
export function makeSympyCasRunner(opts = {}) {
  const pythons = opts.python ? [opts.python] : ['python', 'py', 'python3'];

  return async function casRunner(part) {
    const verify = part.verify;
    if (!verify || typeof verify !== 'object') {
      return { supported: false, matches: false, details: 'no verify spec' };
    }
    const req = { ...verify };
    if (req.claimed === undefined) req.claimed = firstClaimed(part);
    if (req.claimed === undefined) {
      return { supported: false, matches: false, details: 'no claimed answer to check' };
    }

    let lastErr = 'no python interpreter found';
    for (const py of pythons) {
      const res = spawnSync(py, [CAS_SCRIPT], {
        input: JSON.stringify(req),
        encoding: 'utf8',
        timeout: 20000,
      });
      if (res.error) {
        lastErr = res.error.message;
        continue;
      }
      if (res.status !== 0) {
        lastErr = (res.stderr || '').trim() || `exit ${res.status}`;
        continue;
      }
      try {
        return JSON.parse(res.stdout.trim());
      } catch {
        lastErr = `unparseable CAS output: ${res.stdout.slice(0, 200)}`;
      }
    }
    return { supported: false, matches: false, details: `CAS unavailable: ${lastErr}` };
  };
}
