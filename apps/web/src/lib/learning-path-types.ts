import { learningPlanSchema, type LearningPlan, type PlanWeek, type PlanConcept } from '@asf/schemas/learning_path';

export type { LearningPlan, PlanWeek, PlanConcept };

export function currentActiveWeek(plan: LearningPlan): PlanWeek | undefined {
  const active = plan.weeks.find((w) => w.status === 'active');
  if (active) return active;
  return plan.weeks.find((w) => w.status === 'upcoming') ?? plan.weeks[0];
}

export { learningPlanSchema };
