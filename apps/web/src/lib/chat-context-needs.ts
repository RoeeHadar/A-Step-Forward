/**
 * Deterministic context-needs router (ADR-0015).
 * Decides which optional packs to inject for the current learner message.
 */

import {
  classifyTutorChatIntent,
  isPressureFamilyIntent,
  type TutorChatIntent,
  type TutorIntentContext,
} from '@/lib/learner-chat-intent';
import { isPlanChangeTemplate, normalizePlanChangeMessage } from '@/lib/plan-change-template';
import { shouldApplyPlanImmediately } from '@/lib/plan-actions';

export interface ContextNeeds {
  intent: TutorChatIntent;
  /** Inject shared persona + private notes (relevance-filtered elsewhere). */
  durableMemory: boolean;
  profile: boolean;
  mastery: boolean;
  activeWeek: boolean;
  statusPack: boolean;
  bilingualBriefing: boolean;
  planCatalog: boolean;
  learningPlanSnapshot: boolean;
  curriculumHints: boolean;
  hybridTools: boolean;
  methodAuthority: boolean;
  wellbeing: boolean;
  handoffDigest: boolean;
  xp: boolean;
}

const MATH_TEACHING_RE =
  /(?:פתור|חשב|מה החסר|ממוצע|אינטגרל|נגזר|משולש|טרפז|משווא|\\int|\\frac|x\^|∫|מהו|מה זה|explain|solve|calculate|derivative|integral)/i;

export function buildContextNeeds(opts: {
  agent: string;
  message: string;
  intentCtx?: TutorIntentContext;
  hasTopic?: boolean;
  hasPractice?: boolean;
  minimal?: boolean;
}): ContextNeeds {
  const {
    agent,
    message,
    intentCtx = {},
    hasTopic = false,
    hasPractice = false,
    minimal = false,
  } = opts;

  const intent = classifyTutorChatIntent(message, intentCtx);
  const isTutor = agent === 'tutor';
  const isCoach = agent === 'coach';
  const isMentor = agent === 'mentor';
  const live =
    agent === 'tutor' || agent === 'mentor' || agent === 'coach' || agent === 'reviewer';

  if (minimal || !live) {
    return {
      intent,
      durableMemory: false,
      profile: true,
      mastery: false,
      activeWeek: false,
      statusPack: false,
      bilingualBriefing: false,
      planCatalog: false,
      learningPlanSnapshot: false,
      curriculumHints: false,
      hybridTools: false,
      methodAuthority: false,
      wellbeing: false,
      handoffDigest: false,
      xp: false,
    };
  }

  const pressure = isPressureFamilyIntent(intent);
  const mathAsk = MATH_TEACHING_RE.test(message) || intent === 'worked_solution' || intent === 'recovery_simplify';
  const teachTurn =
    intent === 'learn' ||
    intent === 'worked_solution' ||
    intent === 'recovery_simplify' ||
    intent === 'agent_correction' ||
    mathAsk;

  const planAsk =
    intent === 'plan_template' ||
    intent === 'casual_plan_change' ||
    intent === 'study_hours_increase' ||
    isPlanChangeTemplate(normalizePlanChangeMessage(message)) ||
    shouldApplyPlanImmediately(message);

  const statusAsk =
    pressure ||
    intent === 'progress_status' ||
    intent === 'exam_readiness' ||
    intent === 'exam_anxiety' ||
    intent === 'study_next' ||
    intent === 'context_challenge' ||
    intent === 'plan_ownership';

  // Status packs only when the turn is actually about status/pressure — never on pure math.
  const wantStatus = statusAsk && !hasPractice && !(teachTurn && !pressure);
  // Pure teach turns skip profile/mastery dumps so ordinary Q&A stays on-topic.
  const wantProfile = !teachTurn || wantStatus || planAsk || isMentor || hasPractice;
  const wantMastery =
    wantStatus ||
    isCoach ||
    isMentor ||
    intent === 'study_next' ||
    intent === 'recovery_simplify' ||
    hasPractice;

  return {
    intent,
    durableMemory: !teachTurn || isCoach || isMentor || intent === 'agent_correction',
    profile: wantProfile,
    mastery: wantMastery,
    // Active week: mentors/status/coach drills, or tutor when asking what-next — not every math stem.
    activeWeek:
      isMentor ||
      isCoach ||
      wantStatus ||
      intent === 'study_next' ||
      (isTutor && (planAsk || statusAsk)),
    statusPack: wantStatus && (isTutor || isMentor || isCoach || agent === 'reviewer'),
    bilingualBriefing: wantStatus || isMentor || intent === 'progress_status',
    planCatalog: (isTutor || isMentor) && planAsk,
    learningPlanSnapshot:
      (isTutor && (intent === 'study_next' || intent === 'recovery_simplify' || intent === 'exam_anxiety' || hasTopic)) ||
      isCoach,
    curriculumHints: (isTutor || isCoach) && (teachTurn || hasTopic || hasPractice),
    hybridTools: (isTutor || isCoach) && (teachTurn || hasPractice || isCoach),
    methodAuthority: (isTutor || isCoach) && (teachTurn || hasPractice),
    wellbeing: (isTutor || isMentor) && (intent === 'exam_anxiety' || pressure),
    // Handoff digests only when expanding memory or coach session — not every tutor math turn.
    handoffDigest: (isTutor || isCoach) && (isCoach || intent === 'agent_correction'),
    xp: wantStatus || isMentor,
  };
}
