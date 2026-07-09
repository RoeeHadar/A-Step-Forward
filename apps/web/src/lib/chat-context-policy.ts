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
- Never open with meta-phrases like "אני חושב שאני יודע מה קרה" or repeat the same checklist from your prior turn.
- End with one clear next step or one focused question — not both unless needed.`;

export const EXAM_READINESS_TURN_INSTRUCTION = `## THIS TURN — exam readiness / timeline (mandatory)
The learner asked whether their plan will prepare them in time for an exam.
You MUST:
1. Answer DIRECTLY first — honest verdict using: days until exam, hours/week, active plan topics, and known mastery gaps.
2. Practical tone. No topic-by-topic diagnostic checklist unless they explicitly ask for one.
3. If they already said they know the topics, accept it — recommend focused practice (timed problems, weak spots, Coach drills).
4. End with ONE concrete action for the remaining days before the exam.
5. Plan edits only via the Tutor sidebar template — do not offer to recalculate or "נסער את התוכנית" from chat.`;

export const CONVERSATION_ADVANCE_INSTRUCTION = `## THIS TURN — stop repeating (mandatory)
The learner said you already covered this or asked you to continue.
You MUST:
1. Do NOT repeat prior questions, topic bullet lists, or openings from your last reply.
2. Advance: give the next actionable step, a short readiness summary, or offer a drill / mini quiz.
3. Acknowledge in one short clause, then move forward.`;

export const EXAM_ANXIETY_TURN_INSTRUCTION = `## THIS TURN — exam anxiety / missing topics (mandatory)
The learner worries they are not ready or that the plan misses Bagrut/exam topics.
You MUST:
1. Validate the concern briefly — do not dismiss it.
2. Name 2–3 highest-priority gaps from the plan + mastery (if known), not an open-ended "pick topics" quiz.
3. Give a realistic cram strategy for the days left (review vs new material).
4. For plan changes (more hours, different topics): point to the Tutor sidebar template **עדכון תוכנית לימוד** with a concrete example goal line (e.g. "בגרות פיזיקה מכניקה 036-361") — do NOT tell them to ask parents/teachers for permission to study.`;

export const STUDY_HOURS_INCREASE_INSTRUCTION = `## THIS TURN — learner wants more study hours (mandatory)
They want to increase weekly/daily study time for exam cram.
You MUST:
1. Acknowledge their commitment positively.
2. Explain that hours + topics are updated via the sidebar template **עדכון תוכנית לימוד** (goal + date + notes like "5 שעות ביום").
3. Offer to spell out the exact template fields they should paste — do NOT defer to parents/teachers.
4. You may suggest a daily hour target (e.g. 3–5h/day in the last week) while they fill the template.`;

const STUDY_NEXT_RE =
  /what should i study|what.?s next|study next|root cause|why am i stuck|what to learn|מה ללמוד|מה הלאה|למה אני תקוע|מה כדאי|הבא בתור|עוד נושא/i;

const EXAM_READINESS_RE =
  /(?:האם|האם\s+התוכנית).{0,50}(?:תכין|מספיק|מוכן|בזמן)/i;

const EXAM_READINESS_EN_RE =
  /(?:will the plan|is the plan|am i ready).{0,40}(?:prepare|ready|enough|in time)/i;

const CONVERSATION_ADVANCE_RE =
  /(?:כתבת את זה כבר|אמרת את זה|חזרת על|תמשיך|המשך|די עם|stop repeating|you already (?:said|wrote|asked)|move on|continue\b)/i;

const READINESS_AFFIRM_RE =
  /^(?:כן(?:\s|,|$)|נכון|בטח|ברור|יודע|אני יודע|כן,? אני יודע|yes\b|i know|i do\b)/i;

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

export function wantsExamReadinessAnswer(message: string): boolean {
  const t = message.trim();
  if (!t) return false;
  const lower = t.toLowerCase();
  return (
    EXAM_READINESS_RE.test(t) ||
    EXAM_READINESS_EN_RE.test(lower) ||
    /(?:התוכנית|the plan).{0,40}(?:תכין|מספיק|prepare|ready|enough).{0,40}(?:מבחן|בגרות|exam|test)/i.test(
      t,
    ) ||
    /(?:מבחן|בגרות|exam).{0,30}(?:עוד|in)\s+(?:שבוע|יום|week|day)/i.test(t)
  );
}

export function wantsConversationAdvance(message: string): boolean {
  return CONVERSATION_ADVANCE_RE.test(message.trim());
}

export function wantsExamAnxietySupport(message: string): boolean {
  const t = message.trim();
  return /(?:לא מוכן|לא אהיה מוכן|לא מספיק|עוד נושאים|נושאים נוספים|חסר|לא נגענו|missing topics|not ready|won't be ready)/i.test(
    t,
  );
}

export function wantsStudyHoursIncrease(message: string): boolean {
  const t = message.trim();
  return /(?:יותר שעות|הגדיל|להגדיל|להוסיף שעות|more hours|increase.*hours|study more|ללמוד יותר|כמה שצריך)/i.test(
    t,
  );
}

export function isReadinessFollowUp(
  message: string,
  recent: Array<{ role: string; content: string }>,
): boolean {
  const t = message.trim();
  if (!t || t.length > 120) return false;
  if (!READINESS_AFFIRM_RE.test(t)) return false;
  return recent.some((turn) =>
    /(?:בגרות|מבחן|exam|תוכנית|תכין|prepare|readiness|שבוע|week)/i.test(turn.content),
  );
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
