/**
 * ADR-0011 — agent skills prompt regression (no live LLM).
 */
import { describe, expect, it } from 'vitest';
import { buildAgentSkillsPrompt } from './agent-skills';

describe('agent-skills ADR-0011 / ADR-0012', () => {
  it('shared block bans filler, invented bridges, and pressure failures', () => {
    const shared = buildAgentSkillsPrompt('tutor');
    expect(shared).toContain('ADR-0011');
    expect(shared).toContain('ADR-0012');
    expect(shared).toContain('אני חושב שזה יעזור');
    expect(shared).toContain('Do NOT invent');
    expect(shared).toContain('Never trade correctness for simplicity');
    expect(shared).toContain('never deny it');
    expect(shared).toContain('4-beat');
    expect(shared).toContain('חשוך');
  });

  it('tutor includes recovery and plan-anchored extra material', () => {
    const tutor = buildAgentSkillsPrompt('tutor');
    expect(tutor).toContain('Recovery');
    expect(tutor).toContain('Extra material beyond the plan');
  });

  it('mentor owns status narration', () => {
    const mentor = buildAgentSkillsPrompt('mentor');
    expect(mentor).toContain('Status / readiness');
    expect(mentor).toContain('Never dump raw fields');
  });
});
