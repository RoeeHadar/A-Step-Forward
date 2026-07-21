/**
 * Rules-only chat safety (parity with packages/agents SafetyModeration use_llm=false).
 * No LLM classifier in v1 — port of Python _rule_classify + refusals + child_mode.
 */
export type SafetyKind =
  | 'blocked_topic'
  | 'prompt_injection'
  | 'self_harm_risk'
  | 'child_mode_violation'
  | 'pii_overshare';

export const COPPA_AGE_THRESHOLD = 13;

const BLOCKED_PATTERNS = [
  /\bhow do i (?:make|build) (?:a bomb|explosives?)\b/i,
  /\bself[- ]?harm\b/i,
];

const PROMPT_INJECTION_PATTERNS = [
  /ignore (?:all|previous) instructions/i,
  /reveal (?:your |the )?system prompt/i,
  /you are now [a-z ]{3,30}/i,
  /disregard (?:your |the )?(?:rules|guidelines)/i,
  /developer mode/i,
];

const PII_OVERSHARE_PATTERNS = [/\b\d{3}-\d{2}-\d{4}\b/, /\b(?:\d[ -]*?){13,16}\b/];

const CHILD_BLOCKED_PATTERNS = [
  /\b(porn|sexual|sex|drug|cocaine|heroin|marijuana)\b/i,
  /\b(graphic violence|gore|suicide method)\b/i,
  /\b(nude|naked|onlyfans)\b/i,
];

const REFUSAL_TEMPLATES: Record<SafetyKind, string> = {
  blocked_topic:
    "I can't help with that topic. Let's get back to your learning — what would you like to work on next?",
  prompt_injection:
    "I need to stay focused on helping you learn. Ask me a question about your lesson or practice, and I'll do my best.",
  self_harm_risk:
    "It sounds like you might be going through something difficult. Please talk to a trusted adult or contact a crisis helpline. I'm here to support your learning when you're ready.",
  child_mode_violation:
    "That topic isn't appropriate for your learning space. Let's pick something else from your lessons.",
  pii_overshare:
    "For your privacy, please don't share personal details like IDs or payment information here. We can continue without those.",
};

export function resolveChildMode(opts: {
  age: number | null;
  childModeFlag: boolean;
}): boolean {
  if (opts.childModeFlag) return true;
  return opts.age != null && opts.age < COPPA_AGE_THRESHOLD;
}

export function childModeViolation(text: string): boolean {
  return CHILD_BLOCKED_PATTERNS.some((pat) => pat.test(text));
}

export function ruleClassify(
  text: string,
  opts: { childMode: boolean },
): SafetyKind | null {
  for (const pat of BLOCKED_PATTERNS) {
    if (pat.test(text)) return 'blocked_topic';
  }
  for (const pat of PROMPT_INJECTION_PATTERNS) {
    if (pat.test(text)) return 'prompt_injection';
  }
  if (/\b(kill myself|end my life|want to die)\b/i.test(text)) {
    return 'self_harm_risk';
  }
  if (opts.childMode && childModeViolation(text)) {
    return 'child_mode_violation';
  }
  if (!opts.childMode) {
    for (const pat of PII_OVERSHARE_PATTERNS) {
      if (pat.test(text)) return 'pii_overshare';
    }
  }
  return null;
}

export function refusalFor(kind: SafetyKind, redirect?: string): string {
  if (redirect) return redirect;
  return REFUSAL_TEMPLATES[kind] ?? REFUSAL_TEMPLATES.blocked_topic;
}

/** Vercel AI data-stream shaped refusal (same protocol as chat route). */
export function refusalStreamResponse(message: string): Response {
  const encoder = new TextEncoder();
  const body = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(`0:${JSON.stringify(message)}\n`));
      controller.enqueue(
        encoder.encode(
          `d:${JSON.stringify({ finishReason: 'stop', usage: { promptTokens: 0, completionTokens: 0 } })}\n`,
        ),
      );
      controller.close();
    },
  });
  return new Response(body, {
    status: 200,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'X-Vercel-AI-Data-Stream': 'v1',
      'Cache-Control': 'no-cache, no-transform',
    },
  });
}
