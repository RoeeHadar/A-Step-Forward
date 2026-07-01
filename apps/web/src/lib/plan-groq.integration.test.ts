/**
 * Live Groq smoke — verifies Mentor emits a sanitizable ASF_PLAN_UPDATE tag.
 * Skipped when GROQ_API_KEY is unset. Does NOT write to Neon.
 */
import { describe, expect, it } from 'vitest';
import { extractPlanUpdate, learnerConfirmedChange } from './plan-actions';
import { sanitizePlanUpdatePayload } from './plan-catalog';

const hasGroq = Boolean(process.env.GROQ_API_KEY?.trim());

describe.skipIf(!hasGroq)('mentor plan tag (live Groq)', () => {
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

    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [
          { role: 'system', content: system },
          {
            role: 'user',
            content:
              'I want to focus more on limits for my bagrut prep. yes, please update my plan to focus on limits',
          },
        ],
        max_tokens: 600,
        temperature: 0.2,
      }),
    });

    expect(res.ok).toBe(true);
    const json = (await res.json()) as {
      choices?: Array<{ message?: { content?: string } }>;
    };
    const content = json.choices?.[0]?.message?.content ?? '';
    expect(content.length).toBeGreaterThan(20);

    const { visible, payload } = extractPlanUpdate(content);
    expect(visible).not.toContain('ASF_PLAN_UPDATE');
    expect(payload).not.toBeNull();
    expect(payload!.confirmed).toBe(true);
    expect(sanitizePlanUpdatePayload(payload!)).not.toBeNull();
    expect(payload!.priority_concepts).toContain('limits');
    expect(content.toLowerCase()).not.toMatch(/khan academy|youtube\.com/);
  }, 45_000);
});
