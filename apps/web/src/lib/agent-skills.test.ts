/**
 * ADR-0011 — agent skills prompt regression (no live LLM).
 */
import { describe, expect, it } from 'vitest';
import { buildAgentSkillsPrompt } from './agent-skills';

describe('agent-skills ADR-0011 / ADR-0012 / ADR-0015', () => {
  it('shared block bans filler, hybrid knowledge, and pressure failures', () => {
    const shared = buildAgentSkillsPrompt('tutor');
    expect(shared).toContain('ADR-0015');
    expect(shared).toContain('Hybrid knowledge');
    expect(shared).toContain('אני חושב שזה יעזור');
    expect(shared).toContain('Never invent ASF facts');
    expect(shared).toContain('current message still wins');
    expect(shared).toContain('חשוך');
    expect(shared).toContain('Arithmetic self-check');
    expect(shared).toContain('target_mean * n');
    expect(shared).toContain('PRACTICE ARENA');
    expect(shared).toContain('Method grounding');
    expect(shared).toContain('calm classroom teacher');
    expect(shared).toContain('math and physics only');
    expect(shared).toContain('/app/practice');
  });

  it('tutor includes recovery and answer-ordinary-questions', () => {
    const tutor = buildAgentSkillsPrompt('tutor');
    expect(tutor).toContain('Recovery');
    expect(tutor).toContain('Answer ordinary questions');
    expect(tutor).toContain('How to teach this learner');
    expect(tutor).toContain('AUTHORITATIVE pack');
    expect(tutor).toContain('never ask for pace/hours');
    expect(tutor).toContain('never offer a new plan');
    expect(tutor).toContain('never redirect to Mentor');
  });

  it('mentor owns status narration and conversational plan updates', () => {
    const mentor = buildAgentSkillsPrompt('mentor');
    expect(mentor).toContain('Status/readiness');
    expect(mentor).toContain('never dump raw fields');
    expect(mentor).toContain('guided conversation');
    expect(mentor).not.toMatch(/open a form|paste a form/i);
  });
});
