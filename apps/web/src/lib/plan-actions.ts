/**
 * Parse and apply learning-plan updates emitted by agents in chat.
 * Format: [[ASF_PLAN_UPDATE:{...json...}]]
 */
import type { GeneratePlanOptions } from '@/lib/neon-db';
import {
  sanitizePlanUpdatePayload,
  type PlanUpdatePayload,
} from '@/lib/plan-catalog';

export type { PlanUpdatePayload };

const PLAN_TAG_RE = /\[\[ASF_PLAN_UPDATE:(\{[\s\S]*?\})\]\]/g;

export function extractPlanUpdate(content: string): {
  visible: string;
  payload: PlanUpdatePayload | null;
} {
  const match = PLAN_TAG_RE.exec(content);
  PLAN_TAG_RE.lastIndex = 0;
  if (!match) return { visible: content, payload: null };
  try {
    const raw = JSON.parse(match[1]!) as PlanUpdatePayload;
    const payload = sanitizePlanUpdatePayload(raw);
    const visible = content.replace(PLAN_TAG_RE, '').trim();
    PLAN_TAG_RE.lastIndex = 0;
    return { visible, payload };
  } catch {
    return { visible: content.replace(PLAN_TAG_RE, '').trim(), payload: null };
  }
}

export function planPayloadToOptions(payload: PlanUpdatePayload): GeneratePlanOptions {
  return {
    goalOverride: payload.goal,
    priorityConcepts: payload.priority_concepts,
    prependConcepts: payload.prepend_concepts,
    excludeConcepts: payload.exclude_concepts,
    planChangeReason: payload.reason,
  };
}

export function learnerConfirmedChange(message: string): boolean {
  const trimmed = message.trim();
  const lower = trimmed.toLowerCase();
  const heConfirm = /^(כן|אישור|עדכן|בסדר|מאשר|תעדכן|קדימה|מסכים|מסכימה)/.test(trimmed);
  const enConfirm =
    /^(yes|yep|yeah|ok|okay|confirm|do it|go ahead|update|sure|please update|approved)/i.test(
      lower,
    ) ||
    lower.includes('update my plan') ||
    lower.includes('change my plan') ||
    lower.includes('yes, update') ||
    lower.includes('yes update');
  return heConfirm || enConfirm;
}

export const PLAN_AGENT_INSTRUCTIONS = `
## Learning-plan modification protocol (Mentor + Tutor)

You CAN update the learner's weekly plan stored in our database (NOT external LMS). Before changing anything:
1. **Understand why** — ask 1–2 clarifying questions if the request is vague.
2. **Push back when helpful** — suggest in-catalog alternatives using the ALLOWLIST + KG prerequisites.
3. **Summarize the diff** — explain what will change vs the current plan shown above.
4. **Get explicit confirmation** — only after the learner clearly agrees (e.g. "yes", "עדכן", "כן"), emit the machine tag below.

When confirmed, append EXACTLY ONE tag at the **end** of your message (hidden from the learner):
\`[[ASF_PLAN_UPDATE:{"confirmed":true,"reason":"<why>","goal_key":"bagrut_math_5","priority_concepts":["limits"],"prepend_concepts":[],"exclude_concepts":[],"next_test_date":null}]]\`

Rules:
- Use ONLY \`concept_id\` values from the ALLOWLIST block and \`goal_key\` from onboarding tracks.
- \`confirmed\` MUST be true AND the learner must have agreed in their latest message.
- Do NOT emit the tag on the first request unless the learner already confirmed in the same turn.
- If a topic is not in the catalog, do NOT add it — explain the gap and pick the closest in-catalog prerequisite.
`.trim();
