/**
 * Budgets and helpers for learner chat context — keep Groq payloads small so
 * sessions last longer. Durable memory lives in persona + agent notes (dreaming
 * / consolidation), not in verbatim chat_turns replay.
 */
import type { LLMFailureKind } from '@/lib/llm-provider';

export {
  wantsLearningPlanSnapshot,
  wantsExamReadinessAnswer,
  wantsConversationAdvance,
  wantsExamAnxietySupport,
  wantsStudyHoursIncrease,
  isReadinessFollowUp,
  wantsProgressStatus,
  wantsRecoverySimplify,
  wantsWorkedSolution,
  wantsExpandedOutputBudget,
} from '@/lib/learner-chat-intent';

export const CHAT_CONTEXT = {
  maxMemoryTurns: 4,
  maxMemoryTurnChars: 1_200,
  maxMemoryCharsTotal: 4_500,
  maxPersonaChars: 2_500,
  maxAgentNotes: 3,
  maxAgentNoteChars: 280,
  maxSystemChars: 18_000,
  /** Default reply budget — keeps cost/latency down for normal turns. */
  maxOutputTokens: 768,
  /** Worked solutions / continue-from-partial (ADR-0011). */
  maxOutputTokensWorked: 1400,
  maxStoredTurnChars: 2_800,
  dreamNoteThreshold: 22,
  maxWeakStrongConcepts: 3,
  maxHintInsights: 2,
} as const;

export const CHAT_BREVITY_RULE = `## Response style (mandatory)
- Be concise and relevant: answer the learner's question first.
- Default length: 2–4 short paragraphs (or ≤6 bullets) unless they ask for depth.
- Do not repeat injected profile/plan/persona/XP back to them — paraphrase the bilingual progress briefing.
- Never open with meta-phrases like "אני חושב שאני יודע מה קרה", "אני חושב שזה יעזור", "אני צריך להסביר זאת בצורה שונה", or repeat the same checklist from your prior turn.
- End with one clear next step or one focused question — not both unless needed.
- Follow the ## Interaction mode / THIS TURN block for this turn — it overrides default Socratic behavior.`;

/** Whether this turn should use the higher output token budget. */
export function resolveChatMaxTokens(opts: {
  wantsWorkedSolution?: boolean;
  wantsContinue?: boolean;
}): number {
  if (opts.wantsWorkedSolution || opts.wantsContinue) {
    return CHAT_CONTEXT.maxOutputTokensWorked;
  }
  return CHAT_CONTEXT.maxOutputTokens;
}

export function truncationContinueNotice(locale: 'he' | 'en'): string {
  return locale === 'he'
    ? '\n\n—\nהתשובה נחתכה באמצע בגלל אורך. כתוב «המשך» ואמשיך בדיוק מהמקום שעצרתי (בלי לחזור על השלבים הקודמים).'
    : '\n\n—\nThe answer was cut off due to length. Reply “continue” and I will resume exactly where I stopped (without repeating earlier steps).';
}

const ERROR_MARKERS = ['**מה קרה:**', '**What happened:**', '[שירות המודל לא זמין', '[Model service temporarily'];

export function truncateChatText(content: string, maxChars: number): string {
  if (content.length <= maxChars) return content;
  return `${content.slice(0, maxChars)}…`;
}

export function trimPersonaForChat(text: string): string {
  return truncateChatText(text.trim(), CHAT_CONTEXT.maxPersonaChars);
}

export function isLearnerVisibleErrorContent(content: string): boolean {
  return ERROR_MARKERS.some((m) => content.includes(m));
}

/** Short text stored in chat_turns so failures don't bloat the memory window. */
export function compactStoredTurnContent(
  content: string,
  role: 'user' | 'assistant',
  locale: 'he' | 'en' = 'he',
): string {
  if (role === 'assistant' && isLearnerVisibleErrorContent(content)) {
    return locale === 'he'
      ? '[שירות המודל לא זמין זמנית — נסה שוב בעוד רגע]'
      : '[Model service temporarily unavailable — try again shortly]';
  }
  return truncateChatText(content, CHAT_CONTEXT.maxStoredTurnChars);
}

/**
 * Minimum chars to protect at the head (compact baseline + longest persona ≈ 10.5 k).
 * The head contains universal rules and the agent's identity — never trim it.
 */
export const HEAD_GUARD_CHARS = 11_000;

/**
 * Priority-aware system-prompt trimmer.
 *
 * Layers (highest → lowest priority):
 *   1. `tail`   — THIS TURN overrides + brevity rule (always at end, never trimmed).
 *   2. head     — compact baseline + agent persona (first HEAD_GUARD_CHARS of `system`).
 *   3. middle   — profile, notes, concepts, learning plan (trimmed first when over budget).
 *
 * Calling with no `tail` (default `''`) is fully backward-compatible: the whole
 * prompt is treated as body and head+middle trimming applies if needed.
 */
const MIDDLE_TRIM_NOTICE =
  '\n\n[Some background context was trimmed to fit model limits. Use learner profile and weekly plan above.]';

export function fitSystemPrompt(system: string, tail = ''): string {
  const total = system.length + tail.length;
  if (total <= CHAT_CONTEXT.maxSystemChars) {
    return tail ? `${system}${tail}` : system;
  }

  const available = CHAT_CONTEXT.maxSystemChars - tail.length;
  if (available <= 0) {
    // Tail alone exceeds budget — pathological, keep as much tail as possible.
    return tail.slice(0, CHAT_CONTEXT.maxSystemChars);
  }

  if (available <= HEAD_GUARD_CHARS) {
    // Middle entirely dropped — truncate head to whatever space the tail leaves.
    return `${system.slice(0, available)}${tail}`;
  }

  // Middle trim: keep full head + as much middle as fits + full tail.
  const head = system.slice(0, HEAD_GUARD_CHARS);
  const middle = system.slice(HEAD_GUARD_CHARS);
  const middleAvailable = available - HEAD_GUARD_CHARS;

  const trimmedMiddle =
    middle.length > middleAvailable
      ? `${middle.slice(0, Math.max(0, middleAvailable - MIDDLE_TRIM_NOTICE.length))}${MIDDLE_TRIM_NOTICE}`
      : middle;

  return `${head}${trimmedMiddle}${tail}`;
}

export function compactMemoryTurns(
  turns: Array<{ role: 'user' | 'assistant'; content: string }>,
): Array<{ role: 'user' | 'assistant'; content: string }> {
  const out: Array<{ role: 'user' | 'assistant'; content: string }> = [];
  let used = 0;
  for (let i = turns.length - 1; i >= 0; i -= 1) {
    const t = turns[i]!;
    const slice = truncateChatText(t.content, CHAT_CONTEXT.maxMemoryTurnChars);
    if (used + slice.length > CHAT_CONTEXT.maxMemoryCharsTotal && out.length > 0) break;
    out.unshift({ role: t.role, content: slice });
    used += slice.length;
  }
  return out;
}

/**
 * One-line summary of a learning plan for the agent system prompt.
 * Used by Tutor/Mentor agents when the Active week block is already present,
 * to avoid duplicating full plan detail (~1 800 → ≤1 000 chars combined).
 *
 * Format: "Plan: <goal> · <start> → <end> · N week(s) · M concepts"
 */
export function buildPlanHeaderLine(plan: {
  goal: string;
  start_date: string;
  end_date: string | null;
  weeks: Array<{ concepts: Array<unknown> }>;
}): string {
  const totalConcepts = plan.weeks.reduce((s, w) => s + w.concepts.length, 0);
  const n = plan.weeks.length;
  return (
    `Plan: ${plan.goal} · ${plan.start_date} → ${plan.end_date ?? 'open'}` +
    ` · ${n} week${n !== 1 ? 's' : ''} · ${totalConcepts} concept${totalConcepts !== 1 ? 's' : ''}`
  );
}

export function formatPlanWeeksCompact(
  weeks: Array<{
    week_number: number;
    status: string;
    concepts: Array<{ concept_id: string; name: string; name_he?: string | null }>;
  }>,
  mode: 'full' | 'minimal',
): string {
  if (!weeks.length) return 'No active plan.';
  const active = weeks.find((w) => w.status === 'active') ?? weeks[0]!;
  const next = weeks.find((w) => w.week_number === active.week_number + 1);
  const pick = mode === 'minimal' ? [active] : [active, next].filter(Boolean) as typeof weeks;

  return pick
    .map((w) => {
      const names = w.concepts
        .slice(0, mode === 'minimal' ? 4 : 8)
        .map((c) => c.name_he || c.name)
        .join(', ');
      const more = w.concepts.length > (mode === 'minimal' ? 4 : 8)
        ? ` +${w.concepts.length - (mode === 'minimal' ? 4 : 8)}`
        : '';
      return `Week ${w.week_number} [${w.status}]: ${names}${more}`;
    })
    .join('\n');
}

export function learnerErrorKindLabel(kind: LLMFailureKind, locale: 'he' | 'en'): string {
  const he: Record<LLMFailureKind, string> = {
    not_configured: 'שירות הבינה המלאכותית לא מוגדר',
    auth_failure: 'בעיית אימות מול ספק המודל',
    rate_limited: 'יותר מדי בקשות זמניות — נסה שוב בעוד דקה',
    timeout: 'הבקשה ארכה יותר מדי',
    context_too_large: 'הבקשה גדולה מדי לספק המודל',
    provider_error: 'שגיאה זמנית מספק המודל',
    empty_response: 'המודל החזיר תשובה ריקה',
    network_error: 'בעיית חיבור לרשת',
    stream_interrupted: 'התשובה נקטעה באמצע',
    unknown: 'משהו השתבש',
  };
  const en: Record<LLMFailureKind, string> = {
    not_configured: 'AI service is not configured',
    auth_failure: 'Model provider authentication error',
    rate_limited: 'Too many requests — wait a minute and retry',
    timeout: 'The request took too long',
    context_too_large: 'Request too large for the model provider',
    provider_error: 'Temporary model provider error',
    empty_response: 'The model returned an empty response',
    network_error: 'Network connection problem',
    stream_interrupted: 'Response was interrupted',
    unknown: 'Something went wrong',
  };
  return (locale === 'he' ? he : en)[kind] ?? (locale === 'he' ? he.unknown : en.unknown);
}
