/**
 * Parse and apply learning-plan updates emitted by agents in chat.
 * Formats:
 *   [[ASF_PLAN_PROPOSAL:{...json...}]]  — store pending until learner confirms
 *   [[ASF_PLAN_UPDATE:{...json...}]]    — apply when learner confirmed
 */
import type { GeneratePlanOptions } from '@/lib/neon-db';
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
const TOPIC_KEYWORD_RULES: Array<{ pattern: RegExp; concepts: string[] }> = [
  {
    pattern: /חדו[\"']?א\s*1|חדוא\s*1|calculus\s*1\b|\bcalc1\b/i,
    concepts: [
      'limits',
      'derivatives_intro',
      'derivatives_applications',
      'integrals_intro',
      'integrals_techniques',
    ],
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
  const blob = texts.join('\n');
  const out: InferredGoalMeta = {};

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

export function learnerExplicitChangeRequest(message: string): boolean {
  const t = message.trim();
  const lower = t.toLowerCase();
  return (
    /^(שנה|עדכן|שינוי)\s+(את\s+)?(ה)?(מטרה|תוכנית)/i.test(t) ||
    /(?:שנה|עדכן|שינוי).{0,24}תוכנית/i.test(t) ||
    /(?:מבחן|exam).{0,48}(?:שנה|עדכן).{0,24}תוכנית/i.test(t) ||
    /(?:שנה|עדכן).{0,24}תוכנית.{0,48}(?:מבחן|exam)/i.test(t) ||
    /המטרה החדשה שלי/i.test(t) ||
    /שנה את התוכנית|עדכן את התוכנית/i.test(t) ||
    /change my goal|update my goal|new goal is/i.test(lower) ||
    /change my (weekly )?plan|update my (weekly )?plan/i.test(lower)
  );
}

/** Tutor/Mentor prose indicating they are applying a plan or goal change. */
export function looksLikePlanApplyIntent(text: string): boolean {
  return /אעדכן|אשנה|עודכן|מעדכן|הולך לשנות|אני הולך לשנות|אתאים את|מתאים את|מותאם ל|בהתאם ל|אוודא שהתוכנית|התוכנית החדשה|will update|updating your|will change your|המטרה החדשה שלך|מותאם למטרה|I will change your goal/i.test(
    text,
  );
}

function hasActionablePlanChangeRequest(...texts: string[]): boolean {
  const blob = texts.filter(Boolean).join('\n');
  if (!blob.trim()) return false;
  const meta = inferGoalMetaFromText(...texts);
  const concepts = inferConceptIdsFromText(...texts);
  return (
    Boolean(meta.goal || meta.final_goal_date || meta.goal_key || meta.clear_next_test) ||
    concepts.length > 0
  );
}

function isOnlyClarifyingQuestion(assistantRaw: string): boolean {
  const t = assistantRaw.trim();
  if (!t) return false;
  if (looksLikePlanApplyIntent(t)) return false;
  return (
    /^(האם|מה |מתי |איך |לפני |why |what |when |how |can you|could you|would you)/i.test(t) ||
    (/[?؟]\s*$/.test(t) && !/תוכנית|plan|מטרה|goal/i.test(t))
  );
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
): boolean {
  if (learnerConfirmedChange(userMessage)) return true;

  const userTexts = [priorUserMessage, userMessage].filter(Boolean) as string[];
  const hasExplicit = userTexts.some((m) => learnerExplicitChangeRequest(m));
  if (!hasExplicit) return false;

  const contextTexts = [...userTexts, assistantRaw];

  if (
    looksLikePlanChangeAcknowledgment(assistantRaw) ||
    looksLikePlanApplyIntent(assistantRaw)
  ) {
    return true;
  }

  if (
    userTexts.some(
      (m) => learnerExplicitChangeRequest(m) && looksLikePlanApplyIntent(m),
    )
  ) {
    return true;
  }

  if (!hasActionablePlanChangeRequest(...contextTexts)) return false;
  if (!assistantRaw.trim()) return false;
  if (isOnlyClarifyingQuestion(assistantRaw)) return false;

  // Direct imperative with inferable exam/goal data — apply after tutor replies.
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
  if (payload.final_goal_date) {
    const days = Math.ceil(
      (new Date(payload.final_goal_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
    );
    if (days > 0) {
      numWeeksOverride = Math.max(2, Math.min(24, Math.ceil(days / 7)));
    }
  }

  return {
    goalOverride: payload.goal,
    priorityConcepts: payload.priority_concepts,
    prependConcepts: payload.prepend_concepts,
    excludeConcepts: payload.exclude_concepts,
    planChangeReason: payload.reason,
    numWeeksOverride,
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
## Learning-plan & goal modification protocol (Mentor + Tutor)

You CAN update the learner's **goal** (profile text, exam dates) and **weekly plan** in Neon. Before changing anything:
1. **Understand why** — ask 1–2 clarifying questions if the request is vague.
2. **Summarize the diff** — current goal vs new goal; current weeks vs projected weeks (concept names in the learner's language).
3. **Confirmation** — if the learner gave a direct imperative ("שנה את המטרה", "המטרה החדשה שלי היא…"), you may apply after summarizing; otherwise ask for explicit agreement ("כן", "עדכן").

**Proposal turn** (optional, before confirmation): append at the **end**:
\`[[ASF_PLAN_PROPOSAL:{"reason":"<why>","goal":"מבחן במתמטיקה בדידה","goal_key":"university_prep","final_goal_date":"2026-11-01","clear_next_test":true,"prepend_concepts":["combinatorics"],"priority_concepts":[],"exclude_concepts":[]}]]\`

**Apply turn** (learner confirmed OR you stated you are updating): append at the **end**:
\`[[ASF_PLAN_UPDATE:{"confirmed":true,"reason":"<why>","goal":"מבחן במתמטיקה בדידה","goal_key":"university_prep","final_goal_date":"2026-11-01","next_test_date":null,"priority_concepts":[],"prepend_concepts":["combinatorics","probability_basic"],"exclude_concepts":[]}]]\`

Rules:
- **Goal fields**: \`goal\` (free text shown on dashboard), \`goal_key\` from onboarding tracks, \`final_goal_date\` (ISO YYYY-MM-DD), \`next_test_date:null\` when dropping a near-term Bagrut deadline.
- Use ONLY \`concept_id\` values from the ALLOWLIST.
- \`confirmed\` MUST be true on UPDATE tags.
- If a topic is not in the catalog, pick the closest in-catalog prerequisite.
- After the server applies a change it appends a ✅ block with week preview — do not claim the site updated unless you emitted the UPDATE tag.
`.trim();
