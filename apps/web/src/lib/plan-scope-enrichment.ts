/**
 * Enrich plan-update payloads from learner profile + active plan so vague goals
 * like "מבחן בפיזיקה" resolve without forcing learners to know exam codes.
 */
import type { PlanUpdatePayload } from '@/lib/plan-catalog';
import {
  inferConceptIdsFromText,
  PHYSICS_ELECTRICITY_EXAM_CONCEPTS,
  PHYSICS_MECHANICS_EXAM_CONCEPTS,
  PHYSICS_RADIATION_MATTER_EXAM_CONCEPTS,
} from '@/lib/plan-actions';

export interface LearnerPlanContext {
  subjects?: string[];
  goal_key?: string | null;
  points_group?: string | null;
  goal?: string | null;
  planConceptIds?: string[];
  planGoal?: string | null;
}

const PHYSICS_SPECIFIC_RE =
  /036-361|036-371|036-282|036-382|מכניק|קינמט|דינמיק|ניוטון|חשמל|מעגל|קרינה|חומר|mechanics?|kinematics?|electric(?:ity|al)?|circuits?|radiation|matter/i;

const MATH_SPECIFIC_RE =
  /חדו|calculus|\bcalc\s*1|בדיד|discrete|5\s*יח|4\s*יח|3\s*יח|bagrut|בגרות|אלגבר|algebra|לינאר|linear/i;

function defaultPhysicsConcepts(ctx: LearnerPlanContext): string[] {
  const blob = [ctx.goal, ctx.planGoal, ...(ctx.planConceptIds ?? [])].join(' ');
  if (/חשמל|036-371|electric|circuits?/i.test(blob)) {
    return [...PHYSICS_ELECTRICITY_EXAM_CONCEPTS];
  }
  if (/קרינה|036-282|036-382|radiation|matter|optics/i.test(blob)) {
    return [...PHYSICS_RADIATION_MATTER_EXAM_CONCEPTS];
  }
  if (ctx.goal_key === 'bagrut_physics' || ctx.subjects?.includes('physics')) {
    return [...PHYSICS_MECHANICS_EXAM_CONCEPTS];
  }
  return [];
}

function defaultMathConcepts(ctx: LearnerPlanContext): string[] {
  if (ctx.goal_key === 'calculus1' || /חדו|חדוא|calculus\s*1/i.test(ctx.goal ?? '')) {
    return inferConceptIdsFromText('חדו״א 1 calculus 1');
  }
  if (/בדיד|discrete/i.test(ctx.goal ?? '')) {
    return inferConceptIdsFromText('מתמטיקה בדידה');
  }
  return [];
}

function refinePhysicsGoalText(goal: string, ctx: LearnerPlanContext): string {
  if (PHYSICS_SPECIFIC_RE.test(goal)) return goal;
  if (/חשמל|electric/i.test(goal)) return `${goal} — חשמל (036-371)`;
  if (ctx.goal_key === 'bagrut_physics' || ctx.subjects?.includes('physics')) {
    return 'בגרות פיזיקה מכניקה (036-361)';
  }
  return goal;
}

/** Returns true when payload has enough scope to build a plan without clarification. */
export function planPayloadHasExamScope(
  payload: PlanUpdatePayload,
  ctx: LearnerPlanContext = {},
): boolean {
  const text = [payload.goal, payload.next_test_name, payload.reason]
    .filter(Boolean)
    .join('\n');
  if ((payload.prepend_concepts?.length ?? 0) > 0) return true;
  if ((payload.priority_concepts?.length ?? 0) > 0) return true;
  if (inferConceptIdsFromText(text).length > 0) return true;

  if (/פיזיק|physics/i.test(text)) {
    return (
      PHYSICS_SPECIFIC_RE.test(text) || defaultPhysicsConcepts(ctx).length > 0
    );
  }
  if (/מתמטיק|math/i.test(text)) {
    return MATH_SPECIFIC_RE.test(text) || defaultMathConcepts(ctx).length > 0;
  }
  return false;
}

/** Fill prepend_concepts + goal_key + goal text from profile when learner goal is vague. */
export function enrichPlanPayloadFromLearnerContext(
  payload: PlanUpdatePayload,
  ctx: LearnerPlanContext,
): PlanUpdatePayload {
  const out: PlanUpdatePayload = { ...payload };
  const text = [out.goal, out.next_test_name, out.reason].filter(Boolean).join('\n');
  const hasPrepend = (out.prepend_concepts?.length ?? 0) > 0;
  const hasPriority = (out.priority_concepts?.length ?? 0) > 0;

  if (!out.goal_key && ctx.goal_key) {
    out.goal_key = ctx.goal_key;
  }

  if (/פיזיק|physics/i.test(text) || ctx.subjects?.includes('physics')) {
    if (out.goal) out.goal = refinePhysicsGoalText(out.goal, ctx);
    if (!hasPrepend && !hasPriority) {
      const inferred = [
        ...inferConceptIdsFromText(text),
        ...defaultPhysicsConcepts(ctx),
        ...(ctx.planConceptIds ?? []),
      ];
      const unique = [...new Set(inferred)];
      if (unique.length) out.prepend_concepts = unique;
    }
    if (!out.goal_key) out.goal_key = 'bagrut_physics';
  }

  if (/מתמטיק|math/i.test(text) || ctx.subjects?.includes('math')) {
    if (!hasPrepend && !hasPriority) {
      const inferred = [
        ...inferConceptIdsFromText(text),
        ...defaultMathConcepts(ctx),
      ];
      const unique = [...new Set(inferred)];
      if (unique.length) out.prepend_concepts = unique;
    }
  }

  return out;
}
