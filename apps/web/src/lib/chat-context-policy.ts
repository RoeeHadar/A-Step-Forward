/**
 * Budgets and helpers for learner chat context — keep Groq payloads small so
 * sessions last longer. Durable memory lives in persona + agent notes (dreaming
 * / consolidation), not in verbatim chat_turns replay.
 */
import type { LLMFailureKind } from '@/lib/llm-provider';

export const CHAT_CONTEXT = {
  maxMemoryTurns: 4,
  maxMemoryTurnChars: 1_200,
  maxMemoryCharsTotal: 4_500,
  maxPersonaChars: 2_500,
  maxAgentNotes: 3,
  maxAgentNoteChars: 280,
  maxSystemChars: 18_000,
  maxOutputTokens: 768,
  maxStoredTurnChars: 2_800,
  dreamNoteThreshold: 22,
  maxWeakStrongConcepts: 3,
  maxHintInsights: 2,
} as const;

export const CHAT_BREVITY_RULE = `## Response style (mandatory)
- Be concise and relevant: answer the learner's question first.
- Default length: 2–4 short paragraphs (or ≤6 bullets) unless they ask for depth.
- Do not repeat injected profile/plan/persona back to them.
- End with one clear next step or one focused question — not both unless needed.`;

const STUDY_NEXT_RE =
  /what should i study|what.?s next|study next|root cause|why am i stuck|what to learn|מה ללמוד|מה הלאה|למה אני תקוע|מה כדאי|הבא בתור|עוד נושא/i;

const ERROR_MARKERS = ['**מה קרה:**', '**What happened:**', '[שירות המודל לא זמין', '[Model service temporarily'];

export function truncateChatText(content: string, maxChars: number): string {
  if (content.length <= maxChars) return content;
  return `${content.slice(0, maxChars)}…`;
}

export function trimPersonaForChat(text: string): string {
  return truncateChatText(text.trim(), CHAT_CONTEXT.maxPersonaChars);
}

export function wantsLearningPlanSnapshot(message: string): boolean {
  return STUDY_NEXT_RE.test(message);
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

export function fitSystemPrompt(system: string): string {
  if (system.length <= CHAT_CONTEXT.maxSystemChars) return system;
  return `${system.slice(0, CHAT_CONTEXT.maxSystemChars)}\n\n[Some background context was trimmed to fit model limits. Use learner profile and weekly plan above.]`;
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
