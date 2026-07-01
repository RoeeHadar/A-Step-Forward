/**
 * Live LLM smoke — verifies Mentor emits a sanitizable ASF_PLAN_UPDATE tag.
 * Skipped when LLM is not configured. Does NOT write to Neon.
 */
import { describe, expect, it } from 'vitest';
import { extractPlanUpdate, learnerConfirmedChange } from './plan-actions';
import { sanitizePlanUpdatePayload } from './plan-catalog';
import { llmComplete, llmConfigured } from './llm-provider';

describe.skipIf(!llmConfigured())('mentor plan tag (live LLM)', () => {
  it('returns ASF_PLAN_UPDATE with in-catalog concept after confirm scenario', async () => {
    const system = [
      'You are the Mentor on A Step Forward.',
      'When the learner confirms a plan change, append EXACTLY ONE tag at the end:',
      '[[ASF_PLAN_UPDATE:{"confirmed":true,"reason":"learner wants limits focus","goal_key":"bagrut_math_5","priority_concepts":["limits"],"prepend_concepts":[],"exclude_concepts":[]}]]',
      'ALLOWLIST concept ids include: limits, derivatives_intro, algebra_basics.',
      'Never recommend Khan Academy or external courses.',
    ].join('\n');

    const userMessage = 'yes, please update my plan to focus on limits';
    expect(learnerConfirmedChange(userMessage)).toBe(true);

    const result = await llmComplete({
      system,
      messages: [
        {
          role: 'user',
          content:
            'I want to focus more on limits for my bagrut prep. yes, please update my plan to focus on limits',
        },
      ],
      maxTokens: 600,
      temperature: 0.2,
      timeoutMs: 45_000,
      modelTier: 'primary',
    });

    expect(result).not.toBeNull();
    const content = result!.content;
    expect(content.length).toBeGreaterThan(20);

    const { visible, payload } = extractPlanUpdate(content);
    expect(visible).not.toContain('ASF_PLAN_UPDATE');
    expect(payload).not.toBeNull();
    expect(payload!.confirmed).toBe(true);
    expect(sanitizePlanUpdatePayload(payload!)).not.toBeNull();
    expect(payload!.priority_concepts).toContain('limits');
    expect(content.toLowerCase()).not.toMatch(/khan academy|youtube\.com/);
  }, 60_000);
});
