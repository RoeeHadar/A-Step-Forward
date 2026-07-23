/**
 * Root-cause tutor intent router tests — includes the full user-reported session
 * transcript as regression matrix.
 */
import { describe, expect, it } from 'vitest';
import { buildPlanChangeRequest } from './plan-change-template';
import {
  appendTutorContractToContext,
  buildPlanTemplateSuggestion,
  buildTutorInteractionContract,
  classifyTutorChatIntent,
  wantsExamAnxietySupport,
} from './learner-chat-intent';
import {
  enrichPlanPayloadFromLearnerContext,
  planPayloadHasExamScope,
} from './plan-scope-enrichment';
import { proposalToUpdatePayload, inferGoalMetaFromText, inferConceptIdsFromText } from './plan-actions';
import { planPayloadNeedsClarification } from './plan-apply';

/** User-reported session (Jul 2026) — behavioral regression matrix. */
const SESSION = {
  readiness:
    'הבגרות שלי עוד שבוע, האם התוכנית אכן תכין אותי בזמן למבחן?',
  anxiety:
    'בבגרות אבל יש עוד נושאים שעוד לא נגענו בהם, ואני מרגיש שאני לא מוכן מספיק ושלא אהיה מוכן בזמן',
  hoursIncrease:
    'אני רוצה שהזמן שלי יגדל מ 5 שעות לימוד בשבוע הקריטי הזה. אני אעשה כמה שצריך כדי להיות מוכן בשבוע. תוסיף לי כמה שצריך ותגיד לי מה לעשות',
  casualPlanChange: 'אני רוצה שאתה תשנה את התוכנית שלי פה בהתאם',
  broadPhysicsTemplate: buildPlanChangeRequest(
    { goal: 'מבחן בפיזיקה', date: 'עוד שבוע', notes: 'עוד שבוע המבחן' },
    'he',
  ),
  mechanicsTemplate: buildPlanChangeRequest(
    {
      goal: 'פיזיקה בגרות מכניקה',
      date: 'עוד שבוע',
      notes: 'מוכן ללמוד כמה שצריך',
    },
    'he',
  ),
  continue: 'כתבת את זה כבר, תמשיך',
  affirm: 'כן אני יודע את הנושאים האלו',
};

const PHYSICS_PROFILE = {
  subjects: ['physics'] as string[],
  goal_key: 'bagrut_physics',
  goal: 'בגרות פיזיקה',
  planConceptIds: ['kinematics_1d', 'newton_laws', 'circular_motion'],
  planGoal: 'קינמטיקה ומכניקה',
};

describe('classifyTutorChatIntent — user session regression', () => {
  it('classifies each turn in the reported session correctly', () => {
    expect(classifyTutorChatIntent(SESSION.readiness)).toBe('exam_readiness');
    expect(classifyTutorChatIntent(SESSION.anxiety)).toBe('exam_anxiety');
    expect(classifyTutorChatIntent(SESSION.hoursIncrease)).toBe('study_hours_increase');
    expect(classifyTutorChatIntent(SESSION.casualPlanChange)).toBe('casual_plan_change');
    expect(classifyTutorChatIntent(SESSION.broadPhysicsTemplate)).toBe('plan_template');
    expect(classifyTutorChatIntent(SESSION.mechanicsTemplate)).toBe('plan_template');
    expect(classifyTutorChatIntent(SESSION.continue)).toBe('conversation_advance');
  });

  it('detects anxiety phrasing from user transcript', () => {
    expect(wantsExamAnxietySupport(SESSION.anxiety)).toBe(true);
  });

  it('classifies readiness follow-up after exam thread', () => {
    const recent = [
      { role: 'user', content: SESSION.readiness },
      { role: 'assistant', content: 'יש 7 ימים...' },
    ];
    expect(
      classifyTutorChatIntent(SESSION.affirm, { recentTurns: recent }),
    ).toBe('exam_readiness');
  });

  it('defaults to learn for pure curriculum questions', () => {
    expect(classifyTutorChatIntent('מה זה אינטגרל?')).toBe('learn');
    expect(classifyTutorChatIntent('explain Newton\'s second law')).toBe('learn');
  });

  it('prioritizes conversation_advance over exam_readiness on continue', () => {
    const recent = [{ role: 'user', content: SESSION.readiness }];
    expect(
      classifyTutorChatIntent(SESSION.continue, { recentTurns: recent }),
    ).toBe('conversation_advance');
  });
});

describe('buildTutorInteractionContract — mode contracts', () => {
  it('exam_readiness forbids Socratic opening and topic checklist', () => {
    const c = buildTutorInteractionContract('exam_readiness', 'he');
    expect(c.teachingStyle).toBe('direct');
    expect(c.allowSocraticOpening).toBe(false);
    expect(c.allowTopicChecklist).toBe(false);
    expect(c.turnInstruction).toContain('EXAM READINESS');
  });

  it('exam_anxiety uses 4-beat pressure mode without volunteering a template', () => {
    const c = buildTutorInteractionContract('exam_anxiety', 'he', {
      subjects: ['physics'],
      goalKey: 'bagrut_physics',
    });
    expect(c.templateSuggestion).toBeNull();
    expect(c.injectCasualPlanChangeGuide).toBe(false);
    expect(c.allowTopicChecklist).toBe(false);
    expect(c.injectLearningPlanSnapshot).toBe(true);
    expect(c.turnInstruction).toContain('ADR-0012');
    expect(c.turnInstruction).toContain('4-beat');
    expect(c.turnInstruction).not.toMatch(/Name 2–3|improvise gaps/i);
  });

  it('casual_plan_change includes copy-paste template example', () => {
    const c = buildTutorInteractionContract('casual_plan_change', 'he', {
      subjects: ['physics'],
    });
    expect(c.injectCasualPlanChangeGuide).toBe(true);
    expect(c.templateSuggestion).toContain('מטרה או מבחן');
  });

  it('study_hours_increase never defers to parents (instruction guard)', () => {
    const c = buildTutorInteractionContract('study_hours_increase', 'he');
    expect(c.turnInstruction).toContain('Never tell them to ask parents');
    expect(c.allowSocraticOpening).toBe(false);
  });

  it('learn respects socratic preference', () => {
    const socratic = buildTutorInteractionContract('learn', 'he', {
      tutorModePreference: 'socratic',
    });
    expect(socratic.allowSocraticOpening).toBe(true);

    const direct = buildTutorInteractionContract('learn', 'he', {
      tutorModePreference: 'direct',
    });
    expect(direct.allowSocraticOpening).toBe(false);
  });

  it('plan_template injects catalog and forbids invented plans', () => {
    const c = buildTutorInteractionContract('plan_template', 'he');
    expect(c.injectPlanCatalog).toBe(true);
    expect(c.planGuidanceLine).toContain('אל תמציא');
  });
});

describe('appendTutorContractToContext', () => {
  it('injects guardrails that block checklist for exam_readiness', () => {
    const contract = buildTutorInteractionContract('exam_readiness', 'he');
    const out = appendTutorContractToContext('BASE', contract);
    expect(out).toContain('Interaction guardrails');
    expect(out).toContain('Do NOT run a multi-step topic diagnostic checklist');
    expect(out).toContain('EXAM READINESS');
  });
});

describe('buildPlanTemplateSuggestion', () => {
  it('suggests mechanics scope for physics profile', () => {
    const s = buildPlanTemplateSuggestion(
      { subjects: ['physics'], goalKey: 'bagrut_physics' },
      'he',
    );
    expect(s).toContain('036-361');
    expect(s).toContain('שעות ביום');
  });
});

describe('plan-scope-enrichment — profile-based root cause', () => {
  it('enriches broad "מבחן בפיזיקה" from physics profile without learner knowing codes', () => {
    const meta = inferGoalMetaFromText(SESSION.broadPhysicsTemplate);
    const raw = proposalToUpdatePayload({
      reason: 'cram',
      ...meta,
      prepend_concepts: inferConceptIdsFromText(SESSION.broadPhysicsTemplate),
    });
    const enriched = enrichPlanPayloadFromLearnerContext(raw, PHYSICS_PROFILE);

    expect(enriched.goal).toContain('מכניקה');
    expect(enriched.prepend_concepts?.length).toBeGreaterThan(0);
    expect(enriched.goal_key).toBe('bagrut_physics');
    expect(planPayloadHasExamScope(enriched, PHYSICS_PROFILE)).toBe(true);
    expect(planPayloadNeedsClarification(enriched, PHYSICS_PROFILE)).toBeNull();
  });

  it('still requires clarification for broad physics without profile context', () => {
    const meta = inferGoalMetaFromText(SESSION.broadPhysicsTemplate);
    const payload = proposalToUpdatePayload({
      reason: 'cram',
      ...meta,
      prepend_concepts: [],
    });
    expect(planPayloadNeedsClarification(payload, {})).toBe('physics');
  });

  it('mechanics template has scope without enrichment', () => {
    const meta = inferGoalMetaFromText(SESSION.mechanicsTemplate);
    const payload = proposalToUpdatePayload({
      reason: 'cram',
      ...meta,
      prepend_concepts: inferConceptIdsFromText(SESSION.mechanicsTemplate),
    });
    expect(planPayloadNeedsClarification(payload, PHYSICS_PROFILE)).toBeNull();
  });
});

describe('intent priority edge cases', () => {
  it('casual plan change wins when extra chat text invalidates template-only wire', () => {
    const mixed = `${SESSION.casualPlanChange}\n${SESSION.mechanicsTemplate}`;
    expect(classifyTutorChatIntent(mixed)).toBe('casual_plan_change');
    expect(classifyTutorChatIntent(SESSION.mechanicsTemplate)).toBe('plan_template');
  });

  it('study_next for planner questions', () => {
    expect(classifyTutorChatIntent('מה ללמוד הלאה?')).toBe('study_next');
  });
});
