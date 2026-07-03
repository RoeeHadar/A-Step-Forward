/**
 * Parse and apply learning-plan updates emitted by agents in chat.
 * Formats:
 *   [[ASF_PLAN_PROPOSAL:{...json...}]]  — store pending until learner confirms
 *   [[ASF_PLAN_UPDATE:{...json...}]]    — apply when learner confirmed
 */
import type { GeneratePlanOptions } from '@/lib/neon-db';
import {
  isPlanChangeTemplate,
  planChangeTextForParsing,
  recentMessagesIncludePlanTemplate,
} from '@/lib/plan-change-template';
import {
  sanitizeConceptIds,
  sanitizePlanUpdatePayload,
  type PlanUpdatePayload,
} from '@/lib/plan-catalog';

export type { PlanUpdatePayload };

export interface PlanProposalPayload {
  reason: string;
  goal?: string;
  goal_key?: string;
  next_test_date?: string | null;
  next_test_name?: string | null;
  final_goal_date?: string | null;
  clear_next_test?: boolean;
  priority_concepts?: string[];
  prepend_concepts?: string[];
  exclude_concepts?: string[];
}

export interface InferredGoalMeta {
  goal?: string;
  goal_key?: string;
  final_goal_date?: string;
  next_test_date?: string | null;
  next_test_name?: string | null;
  clear_next_test?: boolean;
}

const PLAN_UPDATE_RE = /\[\[ASF_PLAN_UPDATE:(\{[\s\S]*?\})\]\]/g;
const PLAN_PROPOSAL_RE = /\[\[ASF_PLAN_PROPOSAL:(\{[\s\S]*?\})\]\]/g;
const ALL_PLAN_TAGS_RE =
  /\[\[ASF_PLAN_(?:UPDATE|PROPOSAL):(\{[\s\S]*?\})\]\]/g;

/** Map free-text / Hebrew topic names → in-catalog concept_id values. */
/** Canonical calc1 exam review concepts (no generic HS foundations). */
export const CALC1_EXAM_CONCEPTS = [
  'limits',
  'derivatives_intro',
  'derivatives_applications',
  'integrals_intro',
  'integrals_techniques',
] as const;

const TOPIC_KEYWORD_RULES: Array<{ pattern: RegExp; concepts: string[] }> = [
  {
    pattern: /חדו[\"']?א\s*1|חדוא\s*1|calculus\s*1\b|\bcalc1\b/i,
    concepts: [...CALC1_EXAM_CONCEPTS],
  },
  { pattern: /קומבינטוריק|combinatoric/i, concepts: ['combinatorics'] },
  { pattern: /תורת (ה)?קבוצ|set theory|\bsets\b/i, concepts: ['functions_intro'] },
  { pattern: /תורת (ה)?גרפ|graph theory|\bgraphs\b/i, concepts: ['combinatorics'] },
  {
    pattern: /מתמטיקה בדיד|discrete math|discrete mathematics/i,
    concepts: ['combinatorics', 'probability_basic'],
  },
  { pattern: /הסתברות|probability/i, concepts: ['probability_basic'] },
  { pattern: /אינדוקצ|induction/i, concepts: ['combinatorics'] },
  { pattern: /גבולות|limits/i, concepts: ['limits'] },
  { pattern: /סדרות|sequences/i, concepts: ['sequences'] },
  { pattern: /שדות וקטור|vector field/i, concepts: ['uni_vector_fields'] },
  { pattern: /חשבון|calculus/i, concepts: ['derivatives_intro', 'integrals_intro'] },
];

export function extractPlanUpdate(content: string): {
  visible: string;
  payload: PlanUpdatePayload | null;
} {
  const match = PLAN_UPDATE_RE.exec(content);
  PLAN_UPDATE_RE.lastIndex = 0;
  if (!match) return { visible: stripPlanMachineTags(content), payload: null };
  try {
    const raw = JSON.parse(match[1]!) as PlanUpdatePayload;
    const payload = sanitizePlanUpdatePayload(raw);
    PLAN_UPDATE_RE.lastIndex = 0;
    return { visible: stripPlanMachineTags(content), payload };
  } catch {
    PLAN_UPDATE_RE.lastIndex = 0;
    return { visible: stripPlanMachineTags(content), payload: null };
  }
}

export function extractPlanProposal(content: string): {
  visible: string;
  proposal: PlanProposalPayload | null;
} {
  const match = PLAN_PROPOSAL_RE.exec(content);
  PLAN_PROPOSAL_RE.lastIndex = 0;
  if (!match) return { visible: stripPlanMachineTags(content), proposal: null };
  try {
    const raw = JSON.parse(match[1]!) as PlanProposalPayload;
    if (!raw.reason?.trim()) {
      return { visible: stripPlanMachineTags(content), proposal: null };
    }
    PLAN_PROPOSAL_RE.lastIndex = 0;
    return {
      visible: stripPlanMachineTags(content),
      proposal: {
        ...raw,
        priority_concepts: sanitizeConceptIds(raw.priority_concepts),
        prepend_concepts: sanitizeConceptIds(raw.prepend_concepts),
        exclude_concepts: sanitizeConceptIds(raw.exclude_concepts),
      },
    };
  } catch {
    PLAN_PROPOSAL_RE.lastIndex = 0;
    return { visible: stripPlanMachineTags(content), proposal: null };
  }
}

export function stripPlanMachineTags(content: string): string {
  return content.replace(ALL_PLAN_TAGS_RE, '').trim();
}

export function inferConceptIdsFromText(...texts: string[]): string[] {
  const blob = texts.join('\n');
  const ids: string[] = [];
  for (const rule of TOPIC_KEYWORD_RULES) {
    if (rule.pattern.test(blob)) {
      ids.push(...rule.concepts);
    }
  }
  return sanitizeConceptIds(ids);
}

function addMonths(base: Date, months: number): Date {
  const d = new Date(base);
  d.setMonth(d.getMonth() + months);
  return d;
}

function toIsoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/** Parse goal text, track key, and target dates from Hebrew/English chat. */
export function inferGoalMetaFromText(...texts: string[]): InferredGoalMeta {
  const parsedTexts = planChangeTextForParsing(...texts);
  const blob = parsedTexts.join('\n');
  const out: InferredGoalMeta = {};

  const templateGoal = blob.match(
    /(?:מטרה(?:\s*\/?\s*מבחן|\s*או\s*מבחן)?|goal(?:\s*\/?\s*exam)?)\s*:\s*([^\n]+)/i,
  );
  if (templateGoal?.[1]?.trim()) {
    out.goal = templateGoal[1].trim();
  }

  const templateDate = blob.match(
    /(?:מועד|target\s*date)\s*:\s*([^\n]+)/i,
  );
  if (templateDate?.[1]?.trim()) {
    const dateText = templateDate[1].trim();
    const dateMeta = inferGoalMetaFromText(dateText);
    if (dateMeta.final_goal_date) out.final_goal_date = dateMeta.final_goal_date;
    if (dateMeta.next_test_date) out.next_test_date = dateMeta.next_test_date;
  }

  const heNewGoal = blob.match(/המטרה החדשה(?: שלי)?(?: היא|:)\s*([^\n.]+)/i);
  if (heNewGoal?.[1]) {
    out.goal = heNewGoal[1].trim();
  } else if (/מתמטיקה בדיד|discrete math/i.test(blob)) {
    out.goal = /[\u0590-\u05FF]/.test(blob)
      ? 'מבחן במתמטיקה בדידה'
      : 'Discrete mathematics exam';
  } else if (/חדו[\"']?א\s*1|חדוא\s*1|calculus\s*1\b|\bcalc1\b/i.test(blob)) {
    out.goal = /[\u0590-\u05FF]/.test(blob) ? 'מבחן בחדו״א 1' : 'Calculus 1 exam';
    out.goal_key = 'calculus1';
  }

  if (/בדיד|discrete|אוניברסיט|university|open university|מכינה|makhina/i.test(blob)) {
    out.goal_key = out.goal_key ?? 'university_prep';
  }

  if (/חדו[\"']?א\s*1|חדוא\s*1|calculus\s*1\b|\bcalc1\b/i.test(blob)) {
    out.goal_key = 'calculus1';
  }

  if (/לא עושה בגרות|לא בגרות|not doing bagrut|no longer.*bagrut|ביטול.*בגרות/i.test(blob)) {
    out.clear_next_test = true;
  }

  const monthsMatch = blob.match(/(?:בעוד|in)\s*(\d+)\s*(חודש|חודשים|months?)/i);
  if (monthsMatch?.[1]) {
    const months = Number.parseInt(monthsMatch[1], 10);
    if (months > 0 && months <= 36) {
      out.final_goal_date = toIsoDate(addMonths(new Date(), months));
      out.clear_next_test = true;
    }
  }

  const weeksMatch = blob.match(/(?:בעוד|in)\s*(\d+)\s*(שבוע|שבועות|weeks?)/i);
  if (weeksMatch?.[1] && !out.final_goal_date) {
    const weeks = Number.parseInt(weeksMatch[1], 10);
    if (weeks > 0 && weeks <= 52) {
      const d = new Date();
      d.setDate(d.getDate() + weeks * 7);
      out.final_goal_date = toIsoDate(d);
      out.next_test_date = toIsoDate(d);
    }
  }

  if (
    !out.final_goal_date &&
    /(?:עוד|בעוד)\s+שבוע(?:\s|$)|in\s+a\s+week\b/i.test(blob)
  ) {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    out.final_goal_date = toIsoDate(d);
    out.next_test_date = toIsoDate(d);
  }

  if (out.goal && /מבחן|exam|test/i.test(out.goal)) {
    out.next_test_name = out.next_test_name ?? out.goal;
    if (!out.next_test_date && out.final_goal_date) {
      out.next_test_date = out.final_goal_date;
    }
  }

  const enGoal = blob.match(/new goal(?: is|:)\s*([^\n.]+)/i);
  if (enGoal?.[1] && !out.goal) out.goal = enGoal[1].trim();

  return out;
}

/**
 * Official plan-change signal: learner pasted the ASF plan-update template.
 * Only this triggers plan apply on the server and in chat UI.
 */
export function learnerPlanChangeIntent(message: string): boolean {
  return isPlanChangeTemplate(message);
}

/** @deprecated broad heuristics — kept for reference; apply is template-only. */
export function learnerPlanChangeIntentHeuristic(message: string): boolean {
  const t = message.trim();
  if (!t) return false;
  const lower = t.toLowerCase();

  const planWord =
    /(?:תוכנית(?:\s+(?:לימוד|שבועית|הלימוד|השבועית))?|מסלול(?:\s+לימוד)?|לוח(?:\s+לימוד)?|study\s*plan|learning\s*plan|weekly\s*plan|study\s*schedule|learning\s*path|curriculum\s*path)/i;
  const changeWord =
    /(?:שנה|שינוי|עדכן|עדכון|תשנה|תעדכן|התאם|התאמה|תתאם|ארג(?:ן|מ)?\s*מחדש|re(?:prioriti|organiz|schedul)|adjust|update|change|shift|modify|tweak|התמקד|העדף|תעד(?:ף|וף)|הוסף|הורד|add|remove|drop|focus|prepare|התכונ|דח(?:ף|י(?:ף|פה))\s+(?:את\s+)?)/i;
  const goalWord = /(?:המטרה|מטר(?:ה|ת)|goal|objective|target)/i;

  if (
    /^(שנה|עדכן|שינוי)\s+(את\s+)?(ה)?(מטרה|תוכנית)/i.test(t) ||
    /(?:שנה|עדכן|שינוי).{0,32}תוכנית/i.test(t) ||
    /(?:מבחן|exam).{0,48}(?:שנה|עדכן).{0,32}תוכנית/i.test(t) ||
    /(?:שנה|עדכן).{0,32}תוכנית.{0,48}(?:מבחן|exam)/i.test(t) ||
    /(?:רוצה|בבקשה|אפשר).{0,20}ש(?:ת)?(?:שנה|עדכן).{0,32}תוכנית/i.test(t) ||
    /ש(?:ת)?שנה\s+לי.{0,24}תוכנית/i.test(t) ||
    /המטרה החדשה(?: שלי)?/i.test(t) ||
    /שנה את התוכנית|עדכן את התוכנית|תעד(?:כ|)ן(?:\s+לי)?\s+את\s+התוכנית/i.test(t) ||
    /change my goal|update my goal|new goal is/i.test(lower) ||
    /change my (weekly )?plan|update my (weekly )?plan|adjust my (study )?plan/i.test(
      lower,
    ) ||
    /re(?:prioriti|organiz)z?e my (plan|schedule|path)/i.test(lower) ||
    /please (?:update|change|adjust) my (plan|goal|schedule)/i.test(lower) ||
    /can you (?:update|change|adjust) my (plan|goal|schedule)/i.test(lower)
  ) {
    return true;
  }

  if (planWord.test(t) && changeWord.test(t)) return true;
  if (goalWord.test(t) && changeWord.test(t)) return true;
  if (/לא עושה בגרות|not doing bagrut|no longer.*bagrut|ביטול.*בגרות/i.test(t)) return true;
  if (
    /(?:מבחן|exam|test).{0,80}(?:תוכנית|plan|schedule|path)/i.test(t) ||
    /(?:תוכנית|plan|schedule|path).{0,80}(?:מבחן|exam|test)/i.test(t)
  ) {
    return true;
  }
  if (
    /(?:focus|התמקד|priority|עד(?:ף|וף)).{0,40}(?:on|ב|ב)?/i.test(t) &&
    inferConceptIdsFromText(t).length > 0
  ) {
    return true;
  }
  if (changeWord.test(t) && inferConceptIdsFromText(t).length > 0) return true;

  return false;
}

/** @deprecated alias — use learnerPlanChangeIntent */
export function learnerExplicitChangeRequest(message: string): boolean {
  return learnerPlanChangeIntent(message);
}

/** Tutor/Mentor prose indicating they are applying a plan or goal change. */
export function looksLikePlanApplyIntent(text: string): boolean {
  return /אעדכן|אשנה|עודכן|מעדכן|הולך לשנות|אני הולך לשנות|אתאים את|מתאים את|מותאם ל|בהתאם ל|אוודא שהתוכנית|התוכנית החדשה|will update|updating your|will change your|המטרה החדשה שלך|מותאם למטרה|I will change your goal/i.test(
    text,
  );
}

function hasActionablePlanChangeRequest(...texts: string[]): boolean {
  const parsed = planChangeTextForParsing(...texts.filter(Boolean));
  const blob = parsed.join('\n');
  if (!blob.trim()) return false;
  const meta = inferGoalMetaFromText(...parsed);
  const concepts = inferConceptIdsFromText(...parsed);
  if (
    Boolean(meta.goal || meta.final_goal_date || meta.goal_key || meta.clear_next_test) ||
    concepts.length > 0
  ) {
    return true;
  }
  return texts.some((t) => isPlanChangeTemplate(t));
}

/** Direct plan-change request — apply without waiting for tutor Q&A. */
export function shouldApplyPlanImmediately(userMessage: string): boolean {
  return isPlanChangeTemplate(userMessage);
}

export function looksLikePlanChangeAcknowledgment(text: string): boolean {
  return (
    looksLikePlanApplyIntent(text) ||
    /התוכנית החדשה תכלול|התוכנית החדשה|אני מאמין שהתוכנית|new plan will/i.test(text)
  );
}

export function shouldApplyPlanChange(
  userMessage: string,
  assistantRaw: string,
  priorUserMessage?: string,
  recentUserMessages?: string[],
): boolean {
  const userHistory = (
    recentUserMessages?.length
      ? recentUserMessages
      : [priorUserMessage, userMessage]
  ).filter(Boolean) as string[];

  if (learnerConfirmedChange(userMessage)) {
    return recentMessagesIncludePlanTemplate(userHistory);
  }

  if (!userHistory.some((m) => isPlanChangeTemplate(m))) return false;

  const contextTexts = [...userHistory, assistantRaw];

  if (
    looksLikePlanChangeAcknowledgment(assistantRaw) ||
    looksLikePlanApplyIntent(assistantRaw)
  ) {
    return true;
  }

  if (!hasActionablePlanChangeRequest(...contextTexts)) return false;
  if (!assistantRaw.trim()) return false;

  return true;
}

export function looksLikePlanProposal(text: string): boolean {
  const t = text.trim();
  if (!t) return false;
  const goalMeta = inferGoalMetaFromText(t);
  const hasGoalChange = Boolean(
    goalMeta.goal || goalMeta.final_goal_date || goalMeta.goal_key || goalMeta.clear_next_test,
  );
  const hasPlanLanguage =
    /תוכנית|שבוע\s*\d|weekly plan|update (your|my) plan|אעדכן|להוסיף|הוספת|מטרה/i.test(t);
  const hasProposalCue =
    /האם אתה מסכים|do you agree|would you like|האם תרצה|לאשר|confirm/i.test(t);
  const hasConceptCue = inferConceptIdsFromText(t).length > 0;
  return (
    hasGoalChange ||
    (hasPlanLanguage && hasConceptCue) ||
    (hasProposalCue && hasConceptCue) ||
    (looksLikePlanApplyIntent(t) && (hasConceptCue || hasGoalChange))
  );
}

export function proposalToUpdatePayload(
  proposal: PlanProposalPayload & { proposed_at?: string },
): PlanUpdatePayload {
  return {
    confirmed: true,
    reason: proposal.reason,
    goal: proposal.goal,
    goal_key: proposal.goal_key,
    next_test_date: proposal.clear_next_test ? null : proposal.next_test_date,
    next_test_name: proposal.clear_next_test ? null : proposal.next_test_name,
    final_goal_date: proposal.final_goal_date,
    clear_next_test: proposal.clear_next_test,
    priority_concepts: proposal.priority_concepts,
    prepend_concepts: proposal.prepend_concepts,
    exclude_concepts: proposal.exclude_concepts,
  };
}

export function planPayloadToOptions(payload: PlanUpdatePayload): GeneratePlanOptions {
  let numWeeksOverride: number | undefined;
  const targetDate = payload.next_test_date ?? payload.final_goal_date;
  if (targetDate) {
    const days = Math.ceil(
      (new Date(targetDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
    );
    if (days > 0) {
      numWeeksOverride = Math.max(1, Math.min(24, Math.ceil(days / 7)));
    }
  }

  const prepend = payload.prepend_concepts ?? [];
  const isExamFocus = prepend.length > 0 || (payload.priority_concepts?.length ?? 0) > 0;

  return {
    goalOverride: payload.goal,
    priorityConcepts: payload.priority_concepts,
    prependConcepts: payload.prepend_concepts,
    excludeConcepts: payload.exclude_concepts,
    planChangeReason: payload.reason,
    numWeeksOverride,
    focusConceptsOnly: isExamFocus,
  };
}

export function learnerConfirmedChange(message: string): boolean {
  const trimmed = message.trim();
  const lower = trimmed.toLowerCase();
  const heConfirm =
    /^(כן|אישור|עדכן|בסדר|מאשר|תעדכן|קדימה|מסכים|מסכימה)/.test(trimmed) ||
    /\b(אני מסכים|אני מסכימה|מאשר את|אישור)\b/.test(trimmed);
  const enConfirm =
    /^(yes|yep|yeah|ok|okay|confirm|do it|go ahead|update|sure|please update|approved)/i.test(
      lower,
    ) ||
    lower.includes('update my plan') ||
    lower.includes('change my plan') ||
    lower.includes('yes, update') ||
    lower.includes('yes update') ||
    /\bi agree\b/.test(lower);
  return heConfirm || enConfirm;
}

export const PLAN_AGENT_INSTRUCTIONS = `
## Learning-plan & goal modification protocol (Tutor only)

The site applies plan changes when the learner sends the official plan-update template from the sidebar. Casual phrasing does **not** update Neon — direct them to the sidebar template.

When you receive the template:
1. **Read goal/exam and date** — optional notes may mention topics; you already know the learner from memory and mastery. Do NOT require them to list every topic.
2. **Exam cram (≤2 weeks)**: focus ONLY on concepts directly on the exam (e.g. calc1 → limits, derivatives, integrals). Do NOT add arithmetic, combinatorics, or unrelated foundations.
3. **Summarize briefly** and confirm the plan was updated. The server applies immediately — no multi-turn Q&A first.

**Apply turn**: append at the **end**:
\`[[ASF_PLAN_UPDATE:{"confirmed":true,"reason":"<why>","goal":"מבחן בחדו״א 1","goal_key":"calculus1","final_goal_date":"2026-07-10","next_test_date":"2026-07-10","priority_concepts":[],"prepend_concepts":["limits","derivatives_intro","derivatives_applications","integrals_intro","integrals_techniques"],"exclude_concepts":[]}]]\`

Rules:
- Use ONLY \`concept_id\` values from the ALLOWLIST.
- \`confirmed\` MUST be true on UPDATE tags.
- For a test in ~1 week, the weekly plan should be **one week only** — intensive review of exam topics.
`.trim();
