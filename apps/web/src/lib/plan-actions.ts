/**
 * Parse and apply learning-plan updates emitted by agents in chat.
 * Formats:
 *   [[ASF_PLAN_PROPOSAL:{...json...}]]  — store pending until learner confirms
 *   [[ASF_PLAN_UPDATE:{...json...}]]    — apply when learner confirmed
 */
import type { GeneratePlanOptions } from '@/lib/neon-db';
import {
  isPlanChangeTemplate,
  parsePlanChangeTemplateFields,
  planChangeTextForParsing,
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
  hours_per_week?: number;
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
  hours_per_week?: number;
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

/** Canonical discrete-math exam review concepts. */
export const DISCRETE_EXAM_CONCEPTS = [
  'combinatorics',
  'probability_basic',
  'mathematical_induction',
  'functions_intro',
] as const;

export const PHYSICS_MECHANICS_EXAM_CONCEPTS = [
  'kinematics_1d',
  'kinematics_2d',
  'newton_laws',
  'work_energy',
  'momentum',
  'circular_motion',
] as const;

export const PHYSICS_ELECTRICITY_EXAM_CONCEPTS = [
  'coulomb_law',
  'electrostatics',
  'electric_field',
  'electric_potential',
  'electric_circuits',
  'kirchhoff_laws',
] as const;

export const PHYSICS_RADIATION_MATTER_EXAM_CONCEPTS = [
  'waves_basics',
  'sound_waves',
  'optics_geometric',
  'optics_physical',
  'modern_physics_intro',
  'nuclear_physics',
] as const;

const TOPIC_KEYWORD_RULES: Array<{ pattern: RegExp; concepts: string[] }> = [
  {
    pattern: /חדו[\"']?א\s*1|חדוא\s*1|calculus\s*1\b|\bcalc1\b/i,
    concepts: [...CALC1_EXAM_CONCEPTS],
  },
  {
    pattern: /מתמטיקה בדיד|discrete math|discrete mathematics/i,
    concepts: [...DISCRETE_EXAM_CONCEPTS],
  },
  { pattern: /קומבינטוריק|combinatoric/i, concepts: ['combinatorics'] },
  { pattern: /תורת (ה)?קבוצ|set theory|\bsets\b/i, concepts: ['functions_intro'] },
  { pattern: /תורת (ה)?גרפ|graph theory|\bgraphs\b/i, concepts: ['combinatorics'] },
  { pattern: /הסתברות|probability/i, concepts: ['probability_basic'] },
  { pattern: /אינדוקצ|induction/i, concepts: ['combinatorics'] },
  {
    pattern: /036-361|מכניק|קינמט|דינמיק|ניוטון|mechanics?|kinematics?|dynamics?|newton/i,
    concepts: [...PHYSICS_MECHANICS_EXAM_CONCEPTS],
  },
  {
    pattern: /036-371|חשמל|מגנט|מעגל|electric(?:ity|al)?|magnet|circuits?/i,
    concepts: [...PHYSICS_ELECTRICITY_EXAM_CONCEPTS],
  },
  {
    pattern: /036-282|קרינה|חומר|גלים|גלי|אופטיק|אור|מודרנ|גרעינ|radiation|matter|waves?|optics?|modern physics|nuclear/i,
    concepts: [...PHYSICS_RADIATION_MATTER_EXAM_CONCEPTS],
  },
  {
    pattern: /physics\s*1|פיזיקה\s*1/i,
    concepts: [...PHYSICS_MECHANICS_EXAM_CONCEPTS],
  },
  {
    pattern: /physics\s*2|פיזיקה\s*2/i,
    concepts: [...PHYSICS_ELECTRICITY_EXAM_CONCEPTS],
  },
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

function addWeeks(base: Date, weeks: number): Date {
  const d = new Date(base);
  d.setDate(d.getDate() + weeks * 7);
  return d;
}

function inferRelativeWeeksFromText(blob: string): number | null {
  if (/(?:עוד|בעוד)\s+שבועיים(?:\s|$|[^\u0590-\u05FF])/i.test(blob)) return 2;
  if (/(?:עוד|בעוד)\s+שלוש(?:ה)?\s+שבועות/i.test(blob)) return 3;
  if (/(?:עוד|בעוד)\s+ארבע(?:ה)?\s+שבועות/i.test(blob)) return 4;

  const weeksMatch = blob.match(/(?:בעוד|עוד|in)\s*(\d+)\s*(?:שבוע|שבועות|weeks?)/i);
  if (weeksMatch?.[1]) {
    const weeks = Number.parseInt(weeksMatch[1], 10);
    if (weeks > 0 && weeks <= 52) return weeks;
  }
  return null;
}

/** Parse goal text, track key, and target dates from Hebrew/English chat. */
export function inferGoalMetaFromText(...texts: string[]): InferredGoalMeta {
  const parsedTexts = planChangeTextForParsing(...texts);
  const blob = parsedTexts.join('\n');
  const out: InferredGoalMeta = {};

  const templateFields = texts
    .map((t) => (isPlanChangeTemplate(t) ? parsePlanChangeTemplateFields(t) : null))
    .find(Boolean);

  if (templateFields?.goal?.trim()) {
    out.goal = templateFields.goal.trim();
  } else {
    const templateGoal = blob.match(
      /(?:מטרה(?:\s*\/?\s*מבחן|\s*או\s*מבחן)?|goal(?:\s*\/?\s*exam)?)\s*:\s*([^\n]+)/i,
    );
    if (templateGoal?.[1]?.trim()) {
      out.goal = templateGoal[1].trim();
    }
  }

  const dateText = (
    templateFields?.date?.trim() ??
    blob.match(/(?:מועד|target\s*date)\s*:\s*([^\n]+)/i)?.[1]?.trim()
  )?.replace(/\[\[\/ASF-PLAN-UPDATE\]\]/gi, '').trim();
  if (dateText) {
    const relativeFromDate = inferRelativeWeeksFromText(dateText);
    if (relativeFromDate != null) {
      out.final_goal_date = toIsoDate(addWeeks(new Date(), relativeFromDate));
      out.next_test_date = out.final_goal_date;
    } else {
      const dateMeta = inferGoalMetaFromText(dateText);
      if (dateMeta.final_goal_date) out.final_goal_date = dateMeta.final_goal_date;
      if (dateMeta.next_test_date) out.next_test_date = dateMeta.next_test_date;
    }
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

  if (/מתמטיקה בדיד|discrete math/i.test(blob) || /בדיד/i.test(out.goal ?? '')) {
    out.goal_key = 'university_prep';
  }

  if (/פיזיק|physics/i.test(blob) || /פיזיק|physics/i.test(out.goal ?? '')) {
    out.goal_key = out.goal_key ?? 'bagrut_physics';
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

  const relativeWeeks = inferRelativeWeeksFromText(blob);
  if (relativeWeeks != null && !out.final_goal_date) {
    out.final_goal_date = toIsoDate(addWeeks(new Date(), relativeWeeks));
    out.next_test_date = out.final_goal_date;
  }

  if (
    !out.final_goal_date &&
    /(?:עוד|בעוד)\s+שבוע(?:\s|$|[^\u0590-\u05FF])|in\s+a\s+week\b/i.test(blob)
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

  const notesBlob = [templateFields?.notes, blob].filter(Boolean).join('\n');
  const hoursPerDay = notesBlob.match(/(\d+)\s*שעות?\s*(?:ביום|לימוד\s*ביום|בכל\s*יום)/i);
  if (hoursPerDay?.[1]) {
    const daily = Number.parseInt(hoursPerDay[1], 10);
    if (daily > 0 && daily <= 12) out.hours_per_week = daily * 7;
  } else if (
    /(?:יותר\s*מ[-\s]*\d+|כמה\s*שצריך|כול\s*מה\s*שצריך|מוכן\s*ללמוד\s*כמה|as\s*much\s*as)/i.test(
      notesBlob,
    ) &&
    (/(?:עוד|בעוד)\s+שבוע/i.test(notesBlob) || out.final_goal_date)
  ) {
    out.hours_per_week = 35;
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

  const readinessQuestion =
    /(?:האם|האם\s+התוכנית).{0,50}(?:תכין|מספיק|מוכן|בזמן)/i.test(t) ||
    /(?:התוכנית|the plan).{0,40}(?:תכין|מספיק|prepare|ready|enough).{0,40}(?:מבחן|בגרות|exam|test)/i.test(
      t,
    ) ||
    /(?:will the plan|is the plan).{0,40}(?:prepare|ready|enough|in time)/i.test(lower) ||
    /מה הסטטוס|what(?:'s| is) my (?:status|progress)/i.test(t);
  const explicitPlanChangeVerb =
    /(?:שנה|עדכן|שינוי|change|update|adjust|modify|re(?:prioriti|organiz))/i.test(t);

  if (readinessQuestion && !explicitPlanChangeVerb) {
    return false;
  }

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
    /(?:מבחן|exam|test|בגרות).{0,80}(?:תוכנית|plan|schedule|path)/i.test(t) ||
    /(?:תוכנית|plan|schedule|path).{0,80}(?:מבחן|exam|test|בגרות)/i.test(t)
  ) {
    return changeWord.test(t);
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

/** Direct plan-change request — apply without waiting for tutor Q&A. */
export function shouldApplyPlanImmediately(userMessage: string): boolean {
  return isPlanChangeTemplate(userMessage);
}

/** Plan writes happen only on the turn the learner sends the official template. */
export function shouldApplyPlanChange(userMessage: string, ...context: unknown[]): boolean {
  void context;
  return isPlanChangeTemplate(userMessage);
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
    hours_per_week: proposal.hours_per_week,
    priority_concepts: proposal.priority_concepts,
    prepend_concepts: proposal.prepend_concepts,
    exclude_concepts: proposal.exclude_concepts,
  };
}

export function planPayloadToOptions(payload: PlanUpdatePayload): GeneratePlanOptions {
  // Do NOT derive numWeeksOverride from the exam date here. Materialising up to 24 weeks
  // caused FUNCTION_INVOCATION_TIMEOUT on the chat/template apply path (historical P0).
  // The exam horizon (next_test_date / final_goal_date) is already persisted on the
  // learner profile via applyPlanProfileUpdates and is used as end_date metadata only.
  // The rolling window (2 visible weeks) is enforced unconditionally by generateLearningPlan.

  const prepend = payload.prepend_concepts ?? [];
  const isExamFocus = prepend.length > 0 || (payload.priority_concepts?.length ?? 0) > 0;

  return {
    goalOverride: payload.goal,
    priorityConcepts: payload.priority_concepts,
    prependConcepts: payload.prepend_concepts,
    excludeConcepts: payload.exclude_concepts,
    planChangeReason: payload.reason,
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
## Learning-plan & goal modification protocol (Tutor / Mentor)

The site applies plan changes **only** when the learner sends the official plan-update template from the **Tutor chat sidebar** — **by itself**, with no extra chat text before or after it. Casual phrasing never updates Neon, even if the template is pasted in the same message.

When the learner asks to change their plan in casual chat (without the template):
1. **Do NOT** claim the plan was or will be updated.
2. **Do NOT** ask exam-scope or goal-clarification questions as a substitute for a plan update.
3. Tell them clearly (in their language): open **Tutor** chat → use the sidebar template **עדכון תוכנית לימוד** / **Learning plan update** → fill goal/exam + target date → send that message **alone**.
4. You may briefly explain how to fill the template or answer unrelated learning questions — keep plan updates separate.

When you receive a valid template-only message:
1. **Read goal/exam and date** — optional notes may mention topics; you already know the learner from memory and mastery.
2. If the goal is still too broad for the server to build a plan, the server will refuse — do not claim success; help them refine the template fields.
3. **Exam cram (≤2 weeks)**: focus ONLY on exam concepts. Do NOT add unrelated foundations.
4. **Never** say the plan was updated unless the server confirmation appears in the chat (✅ notice). Do NOT emit \`[[ASF_PLAN_UPDATE:...]]\` tags.

Rules:
- Casual phrasing + template in one message = **no apply** — tell them to send the template alone.
- For a test in ~1 week, the weekly plan should be **one week only**.
`.trim();

/** Injected on turns where the learner asked to change the plan without the official template. */
export const CASUAL_PLAN_CHANGE_TURN_INSTRUCTION = `
## THIS TURN — casual plan-change request (mandatory response)
The learner asked to change their learning plan WITHOUT the official Tutor sidebar template.
You MUST:
1. NOT claim the plan was or will be updated from this chat message.
2. NOT ask exam-scope or goal-clarification questions as a substitute for a plan update.
3. Tell them clearly: plan changes happen ONLY via **עדכון תוכנית לימוד** / **Learning plan update** in the Tutor chat sidebar (left). Fill goal + date + optional notes, send that message alone.
4. Give a **copy-paste example** for their case when possible, e.g.:
   - מטרה או מבחן: בגרות פיזיקה מכניקה (036-361)
   - מועד: עוד שבוע
   - הערות: מוכן ללמוד 5 שעות ביום — תכין תוכנית מלאה
5. You may answer unrelated learning questions in the same reply — keep plan update steps separate and short.
`.trim();
