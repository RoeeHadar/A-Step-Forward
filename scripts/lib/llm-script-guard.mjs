/**
 * AS-96: opt-in guard for scripts that call a real LLM (Groq) outside the
 * guarded app clients (apps/web/src/lib/llm, packages/agents/agents/base/llm.py).
 *
 * Such a script refuses to run unless ALLOW_REAL_LLM=1 is set explicitly,
 * the same opt-in that the test suites keep unset. Python twin:
 * scripts/llm_script_guard.py.
 */

export const LLM_OPT_IN_ENV = 'ALLOW_REAL_LLM';
export const LLM_GUARD_EXIT_CODE = 3;

export class LlmScriptGuardError extends Error {
  constructor(message) {
    super(message);
    this.name = 'LlmScriptGuardError';
  }
}

/** True only when ALLOW_REAL_LLM is exactly "1". */
export function realLlmAllowed(env = process.env) {
  return (env[LLM_OPT_IN_ENV] ?? '').trim() === '1';
}

function refusalMessage(script) {
  return (
    `[llm-guard] ${script} calls a real LLM (Groq) and is refused by default. ` +
    `Set ${LLM_OPT_IN_ENV}=1 to opt in explicitly (AS-96).`
  );
}

/** Library form: throw before any request when the opt-in is missing. */
export function assertRealLlmAllowed(script, env = process.env) {
  if (!realLlmAllowed(env)) throw new LlmScriptGuardError(refusalMessage(script));
}

/** CLI form: print a clear message and exit nonzero when the opt-in is missing. */
export function requireRealLlmOptIn(script, env = process.env) {
  if (!realLlmAllowed(env)) {
    console.error(refusalMessage(script));
    process.exit(LLM_GUARD_EXIT_CODE);
  }
}
