/**
 * Authoritative tutor chat intent router + interaction mode contracts.
 *
 * Replaces scattered regex → prompt patches in the chat route. Every tutor turn
 * is classified once; behavior (Socratic vs direct, plan catalog, instructions)
 * flows from the contract — not from ad-hoc heuristics in route.ts.
 */
import { isPlanChangeTemplate, normalizePlanChangeMessage } from '@/lib/plan-change-template';
import { learnerPlanChangeIntentHeuristic } from '@/lib/plan-actions';

/** Ordered by routing priority (classifier checks top → bottom). */
export type TutorChatIntent =
  | 'plan_template'
  | 'conversation_advance'
  | 'casual_plan_change'
  | 'study_hours_increase'
  | 'exam_anxiety'
  | 'exam_readiness'
  | 'progress_status'
  | 'recovery_simplify'
  | 'worked_solution'
  | 'study_next'
  | 'learn';

export type TutorTeachingStyle = 'socratic' | 'direct';

export interface TutorIntentContext {
  recentTurns?: Array<{ role: string; content: string }>;
  tutorModePreference?: 'socratic' | 'direct' | null;
  subjects?: string[];
  goalKey?: string | null;
  hoursPerWeek?: number | null;
  daysUntilExam?: number | null;
}

export interface TutorInteractionContract {
  intent: TutorChatIntent;
  teachingStyle: TutorTeachingStyle;
  /** May the tutor open with a Socratic question before answering? */
  allowSocraticOpening: boolean;
  /** May the tutor run a multi-step topic diagnostic checklist? */
  allowTopicChecklist: boolean;
  injectPlanCatalog: boolean;
  injectCasualPlanChangeGuide: boolean;
  injectLearningPlanSnapshot: boolean;
  planGuidanceLine: string;
  turnInstruction: string | null;
  /** When set, replaces default learner Socratic/direct preference line. */
  learnerPreferenceOverride: string | null;
  templateSuggestion: string | null;
}

export interface PlanTemplateSuggestionContext {
  subjects?: string[];
  goalKey?: string | null;
  goal?: string | null;
  hoursPerWeek?: number | null;
}

// --- Intent detectors (exported for tests) ---

const STUDY_NEXT_RE =
  /what should i study|what.?s next|study next|root cause|why am i stuck|what to learn|מה ללמוד|מה הלאה|למה אני תקוע|מה כדאי|הבא בתור|עוד נושא/i;

const EXAM_READINESS_RE =
  /(?:האם|האם\s+התוכנית).{0,50}(?:תכין|מספיק|מוכן|בזמן)/i;

const EXAM_READINESS_EN_RE =
  /(?:will the plan|is the plan|am i ready).{0,40}(?:prepare|ready|enough|in time)/i;

/** Bagrut / exam odds without requiring the word "plan". */
const EXAM_ODDS_RE =
  /(?:איך|מה).{0,25}(?:יהיה|יקרה|סיכוי).{0,40}(?:בגרות|מבחן)|how (?:will|would) i (?:do|fare).{0,30}(?:exam|bagrut|test)|bagrut odds|exam (?:odds|chances)/i;

const PROGRESS_STATUS_RE =
  /(?:מה|what(?:'s| is)?).{0,20}(?:הסטטוס|סטטוס|המצב|status)|איך אני מתקדם|מה המצב שלי|how am i doing|my (?:current )?status|current status|כמה XP|how much xp|מה ה-?XP/i;

const RECOVERY_SIMPLIFY_RE =
  /(?:מסובך|לא מבין|לא הבנתי|תסביר.{0,20}(?:פשוט|פשוטה|יותר)|בצורה יותר פשוטה|צריך להכיר(?: את)? זה|האם אני צריך|too (?:hard|complicated)|simplify|explain (?:simpler|more simply)|do i need (?:to know )?this|i don'?t understand)/i;

const WORKED_SOLUTION_RE =
  /(?:פתור|תפתור|הראה לי איך|תן לי את השלבים|שלב אחר שלב|worked example|show me how|solve (?:it|the)|step[- ]by[- ]step|המשך,?\s*התגובה)/i;

const CONVERSATION_ADVANCE_RE =
  /(?:כתבת את זה כבר|אמרת את זה|חזרת על|תמשיך|המשך|די עם|stop repeating|you already (?:said|wrote|asked)|move on|continue\b|נעצרה באמצע|cut off|was cut)/i;

const READINESS_AFFIRM_RE =
  /^(?:כן(?:\s|,|$)|נכון|בטח|ברור|יודע|אני יודע|כן,? אני יודע|yes\b|i know|i do\b)/i;

const EXAM_ANXIETY_RE =
  /(?:לא מוכן|לא אהיה מוכן|לא מספיק|עוד נושאים|נושאים נוספים|חסר|לא נגענו|missing topics|not ready|won't be ready|מרגיש שאני לא)/i;

const STUDY_HOURS_RE =
  /(?:יותר שעות|הגדיל|להגדיל|להוסיף שעות|more hours|increase.*hours|study more|ללמוד יותר|כמה שצריך|כמה זמן שצריך)/i;

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
    EXAM_ODDS_RE.test(t) ||
    /(?:התוכנית|the plan).{0,40}(?:תכין|מספיק|prepare|ready|enough).{0,40}(?:מבחן|בגרות|exam|test)/i.test(
      t,
    )
  );
}

export function wantsProgressStatus(message: string): boolean {
  return PROGRESS_STATUS_RE.test(message.trim());
}

export function wantsRecoverySimplify(message: string): boolean {
  return RECOVERY_SIMPLIFY_RE.test(message.trim());
}

export function wantsWorkedSolution(message: string): boolean {
  return WORKED_SOLUTION_RE.test(message.trim());
}

export function wantsConversationAdvance(message: string): boolean {
  return CONVERSATION_ADVANCE_RE.test(message.trim());
}

/** Higher maxTokens budget for continue / step-by-step asks (ADR-0011). */
export function wantsExpandedOutputBudget(message: string): boolean {
  return (
    wantsConversationAdvance(message) ||
    wantsWorkedSolution(message) ||
    wantsRecoverySimplify(message)
  );
}

export function wantsExamAnxietySupport(message: string): boolean {
  return EXAM_ANXIETY_RE.test(message.trim());
}

export function wantsStudyHoursIncrease(message: string): boolean {
  return STUDY_HOURS_RE.test(message.trim());
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

/** Single entry point — priority-ordered classification. */
export function classifyTutorChatIntent(
  message: string,
  ctx: TutorIntentContext = {},
): TutorChatIntent {
  const normalized = normalizePlanChangeMessage(message);
  const recent = ctx.recentTurns ?? [];

  if (isPlanChangeTemplate(normalized)) return 'plan_template';
  if (wantsConversationAdvance(message)) return 'conversation_advance';
  if (learnerPlanChangeIntentHeuristic(message) && !isPlanChangeTemplate(normalized)) {
    return 'casual_plan_change';
  }
  if (wantsStudyHoursIncrease(message)) return 'study_hours_increase';
  if (wantsExamAnxietySupport(message)) return 'exam_anxiety';
  if (wantsExamReadinessAnswer(message) || isReadinessFollowUp(message, recent)) {
    return 'exam_readiness';
  }
  if (wantsProgressStatus(message)) return 'progress_status';
  if (wantsRecoverySimplify(message)) return 'recovery_simplify';
  if (wantsWorkedSolution(message)) return 'worked_solution';
  if (wantsLearningPlanSnapshot(message)) return 'study_next';
  return 'learn';
}

// --- Mode contracts ---

const EXAM_READINESS_INSTRUCTION = `## Interaction mode: EXAM READINESS (mandatory)
Answer DIRECTLY — timeline verdict using days until exam, hours/week, plan topics, mastery gaps, and the bilingual progress briefing.
- No Socratic opening. No topic-by-topic diagnostic checklist unless explicitly requested.
- Never claim 100% / ~100% / "מאה אחוז" / "guaranteed" for bagrut success — not even as an aspirational target. Use humble readiness band/pace only (ADR-0010/0011).
- If learner already affirmed they know topics, accept it → recommend practice/drills.
- End with ONE concrete action for remaining days.
- Plan edits: Tutor sidebar template only — never "נסער את התוכנית" from chat.`;

const CONVERSATION_ADVANCE_INSTRUCTION = `## Interaction mode: CONTINUE (mandatory)
Learner asked you to stop repeating or to resume after a cut-off.
- Do NOT repeat prior questions, bullet lists, or earlier solution steps.
- If the prior assistant turn was cut mid-solution: resume from the unfinished step only.
- Do NOT say you need to "explain differently" unless you actually change method.
Acknowledge briefly, then advance.`;

const PROGRESS_STATUS_INSTRUCTION = `## Interaction mode: PROGRESS STATUS (mandatory)
Answer with a short plain-language status from the bilingual progress briefing (Mentor framing).
- No XP/ISO/raw dumps; no repeated gate score lines; no guaranteed bagrut %.
- Optional one-clause Mentor nudge for deeper goals talk.
- End with one concrete next step.`;

const RECOVERY_SIMPLIFY_INSTRUCTION = `## Interaction mode: RECOVERY / SIMPLIFY (mandatory)
1. Drop any failed explanation path from prior turns.
2. Say whether the topic is required for the current plan / bagrut track, or optional.
3. Teach the simplest CORRECT method from injected corpus context only.
4. Never invent a wrong "simple" answer. One short example, then check understanding.
5. Optional private note (misconception/strategy).`;

const WORKED_SOLUTION_INSTRUCTION = `## Interaction mode: WORKED SOLUTION (mandatory)
- Ground every step in corpus/KG; no invented bridges.
- If >~8 steps: roadmap + first 2–3 steps, then ask to continue.
- Math in \`$...$\` / \`$$...$$\`. No filler closers.`;

const EXAM_ANXIETY_INSTRUCTION = `## Interaction mode: EXAM ANXIETY (mandatory)
Validate concern briefly. Use the **learning-plan snapshot** (server-selected concepts) — do NOT improvise gap names or ask the learner to pick topics.
Frame priorities softly and rationally (e.g. "נחזק את הבסיס השבוע…" / "let's solidify foundations this week…"). Some snapshot topics may support confidence and pacing — do NOT reveal selection mechanism unless the learner asks directly.
Give a realistic cram strategy from the snapshot. For plan/hour changes, show the sidebar template example — never defer to parents/teachers.`;

const STUDY_HOURS_INSTRUCTION = `## Interaction mode: STUDY HOURS INCREASE (mandatory)
Acknowledge commitment. Hours change via sidebar template **עדכון תוכנית לימוד** with notes (e.g. "5 שעות ביום").
Spell out exact template fields. Never tell them to ask parents/teachers for permission.`;

const CASUAL_PLAN_CHANGE_INSTRUCTION = `## Interaction mode: CASUAL PLAN CHANGE (mandatory)
Plan changes apply ONLY via sidebar template **עדכון תוכנית לימוד** — sent alone, no extra chat text.
Do NOT claim the plan was updated. Do NOT substitute exam-scope Q&A for a plan update.
Provide the copy-paste example below when available.`;

const LEARN_DIRECT_NOTE = `## Interaction mode: DIRECT LEARN
Answer the question clearly first. One focused follow-up at most.`;

const LEARN_SOCRATIC_NOTE = `## Interaction mode: LEARN (Socratic)
Ask one targeted question before explaining unless the learner asked for the answer directly.`;

export function buildPlanTemplateSuggestion(
  ctx: PlanTemplateSuggestionContext,
  locale: 'he' | 'en' = 'he',
): string | null {
  const subjects = ctx.subjects ?? [];
  const isPhysics =
    subjects.includes('physics') ||
    ctx.goalKey === 'bagrut_physics' ||
    /פיזיק|physics/i.test(ctx.goal ?? '');
  const isMath =
    subjects.includes('math') ||
    /bagrut_math|calculus1|linear_algebra|university_prep/.test(ctx.goalKey ?? '') ||
    /מתמטיק|math/i.test(ctx.goal ?? '');

  const dailyHours =
    ctx.hoursPerWeek && ctx.hoursPerWeek >= 14
      ? Math.min(8, Math.round(ctx.hoursPerWeek / 7))
      : 5;

  if (locale === 'he') {
    if (isPhysics) {
      return [
        '**דוגמה להעתקה לתבנית:**',
        'מטרה או מבחן: בגרות פיזיקה מכניקה (036-361)',
        'מועד: עוד שבוע',
        `הערות: מוכן ללמוד ${dailyHours} שעות ביום — תכין תוכנית מלאה`,
      ].join('\n');
    }
    if (isMath) {
      return [
        '**דוגמה להעתקה לתבנית:**',
        'מטרה או מבחן: בגרות מתמטיקה 5 יח״ל',
        'מועד: עוד שבוע',
        `הערות: מוכן ללמוד ${dailyHours} שעות ביום`,
      ].join('\n');
    }
    return [
      '**דוגמה להעתקה לתבנית:**',
      'מטרה או מבחן: [מבחן / מטרה מדויקת]',
      'מועד: [תאריך או "עוד שבוע"]',
      'הערות: [שעות ביום, נושאים חשובים]',
    ].join('\n');
  }

  if (isPhysics) {
    return [
      '**Copy-paste example for the template:**',
      'Goal or exam: Bagrut Physics Mechanics (036-361)',
      'Target date: in one week',
      `Notes: ready to study ${dailyHours} hours/day — build a full cram plan`,
    ].join('\n');
  }
  return [
    '**Copy-paste example for the template:**',
    'Goal or exam: [specific exam]',
    'Target date: [date or "in one week"]',
    'Notes: [hours/day, priority topics]',
  ].join('\n');
}

export function buildTutorInteractionContract(
  intent: TutorChatIntent,
  locale: 'he' | 'en',
  ctx: TutorIntentContext = {},
): TutorInteractionContract {
  const pref = ctx.tutorModePreference ?? 'socratic';
  const suggestionCtx: PlanTemplateSuggestionContext = {
    subjects: ctx.subjects,
    goalKey: ctx.goalKey,
    hoursPerWeek: ctx.hoursPerWeek,
  };
  const templateSuggestion =
    intent === 'casual_plan_change' ||
    intent === 'study_hours_increase' ||
    intent === 'exam_anxiety'
      ? buildPlanTemplateSuggestion(suggestionCtx, locale)
      : null;

  const base: TutorInteractionContract = {
    intent,
    teachingStyle: pref,
    allowSocraticOpening: pref === 'socratic',
    allowTopicChecklist: true,
    injectPlanCatalog: false,
    injectCasualPlanChangeGuide: false,
    injectLearningPlanSnapshot: false,
    planGuidanceLine:
      locale === 'he'
        ? 'שינוי תוכנית — רק דרך תבנית עדכון תוכנית בצד שמאל.'
        : 'Plan changes — Tutor sidebar template only.',
    turnInstruction: null,
    learnerPreferenceOverride: null,
    templateSuggestion,
  };

  switch (intent) {
    case 'plan_template':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        injectPlanCatalog: true,
        planGuidanceLine:
          locale === 'he'
            ? 'הודעת תבנית בלבד — השרת מעדכן את התוכנית. אל תמציא תוכנית; המתן לאישור ✅ מהמערכת.'
            : 'Template-only message — server applies the plan. Do not invent a plan; wait for system ✅.',
        turnInstruction:
          locale === 'he'
            ? '## Interaction mode: PLAN TEMPLATE\nאל תוסיף שאלות. אל תמציא תוכנית. השרת מטפל בעדכון.'
            : '## Interaction mode: PLAN TEMPLATE\nNo questions. Do not invent a plan. Server handles the update.',
      };

    case 'conversation_advance':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        turnInstruction: CONVERSATION_ADVANCE_INSTRUCTION,
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct mode — advance the conversation, no repeated questions.',
      };

    case 'casual_plan_change':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        injectCasualPlanChangeGuide: true,
        turnInstruction: [
          CASUAL_PLAN_CHANGE_INSTRUCTION,
          templateSuggestion ?? '',
        ]
          .filter(Boolean)
          .join('\n\n'),
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct mode — route to sidebar template with example.',
      };

    case 'study_hours_increase':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        injectCasualPlanChangeGuide: true,
        turnInstruction: [
          STUDY_HOURS_INSTRUCTION,
          templateSuggestion ?? '',
        ]
          .filter(Boolean)
          .join('\n\n'),
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct mode — explain template fields for hour increase.',
      };

    case 'exam_anxiety':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        injectCasualPlanChangeGuide: true,
        injectLearningPlanSnapshot: true,
        planGuidanceLine:
          locale === 'he'
            ? 'לשינוי תוכנית/שעות — תבנית בצד שמאל. עכשיו: עזרה ללמידה ולחרדה, לא רשימת נושאים פתוחה.'
            : 'For plan/hour changes — sidebar template. Now: learning + anxiety support, not open topic quiz.',
        turnInstruction: [
          EXAM_ANXIETY_INSTRUCTION,
          templateSuggestion ?? '',
        ]
          .filter(Boolean)
          .join('\n\n'),
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct, reassuring mode — no Socratic checklist.',
      };

    case 'exam_readiness':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        planGuidanceLine:
          locale === 'he'
            ? 'תן פסק דין ישיר על מוכנות לפי התוכנית (ימים, שעות, נושאים). בלי רשימת נושאים. לעולם אל תבטיח הצלחה.'
            : 'Direct readiness verdict from plan (days, hours, topics). No topic checklist. Never promise success.',
        turnInstruction: EXAM_READINESS_INSTRUCTION,
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct mode — readiness verdict first, not discovery questions.',
      };

    case 'progress_status':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        turnInstruction: PROGRESS_STATUS_INSTRUCTION,
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct Mentor-style status — paraphrase briefing only.',
      };

    case 'recovery_simplify':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        injectLearningPlanSnapshot: true,
        turnInstruction: RECOVERY_SIMPLIFY_INSTRUCTION,
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct recovery — simplest correct corpus method.',
      };

    case 'worked_solution':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        allowTopicChecklist: false,
        turnInstruction: WORKED_SOLUTION_INSTRUCTION,
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct worked solution — chunk long proofs.',
      };

    case 'study_next':
      return {
        ...base,
        teachingStyle: 'direct',
        allowSocraticOpening: false,
        injectLearningPlanSnapshot: true,
        turnInstruction:
          locale === 'he'
            ? '## Interaction mode: STUDY NEXT\nהשתמש ב-learning-plan snapshot. הצע את הצעד הבא המבוסס מסטר.'
            : '## Interaction mode: STUDY NEXT\nUse learning-plan snapshot. Recommend next step from mastery.',
        learnerPreferenceOverride:
          'LEARNER PREFERENCE OVERRIDE: Direct recommendation from planner data.',
      };

    case 'learn':
    default:
      return {
        ...base,
        teachingStyle: pref,
        allowSocraticOpening: pref === 'socratic',
        turnInstruction: pref === 'direct' ? LEARN_DIRECT_NOTE : LEARN_SOCRATIC_NOTE,
        learnerPreferenceOverride:
          pref === 'direct'
            ? 'LEARNER PREFERENCE: Direct explanations — answer first, then check understanding.'
            : 'LEARNER PREFERENCE: Socratic guidance — one targeted question before explaining.',
      };
  }
}

/** Apply contract to system prompt fragments (testable without DB). */
export function appendTutorContractToContext(
  context: string,
  contract: TutorInteractionContract,
): string {
  let out = context;
  if (contract.learnerPreferenceOverride) {
    out = `${contract.learnerPreferenceOverride}\n\n${out}`;
  }
  out += `\n\n## Plan guidance`;
  out += `\n${contract.planGuidanceLine}`;
  if (contract.turnInstruction) {
    out += `\n\n${contract.turnInstruction}`;
  }
  out += `\n\n## Interaction guardrails`;
  out += contract.allowSocraticOpening
    ? '\n- Socratic opening allowed for this turn.'
    : '\n- Do NOT open with a Socratic question — answer directly first.';
  out += contract.allowTopicChecklist
    ? ''
    : '\n- Do NOT run a multi-step topic diagnostic checklist.';
  return out;
}
