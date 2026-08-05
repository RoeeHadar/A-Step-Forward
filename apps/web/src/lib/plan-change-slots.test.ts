import { describe, expect, it } from 'vitest';
import type { PlanChangeSessionSlots } from '@/lib/neon-db';
import {
  REQUIRED_PLAN_SLOTS,
  SLOT_REASK_LIMIT,
  bumpReask,
  buildProposalDiff,
  buildProposalFromSlots,
  escalationPrompt,
  goalScopeIssue,
  mergeSlots,
  missingRequiredSlots,
  shouldEscalate,
  slotPrompt,
} from './plan-change-slots';

describe('mergeSlots', () => {
  it('starts from empty and keeps new input', () => {
    const out = mergeSlots({}, { goal: 'Calculus 1 exam', target_date: '2026-09-15' });
    expect(out.goal).toBe('Calculus 1 exam');
    expect(out.target_date).toBe('2026-09-15');
  });

  it('lets new input override existing slots', () => {
    const existing: PlanChangeSessionSlots = { goal: 'old goal', target_date: '2026-01-01' };
    const out = mergeSlots(existing, { goal: 'Calculus 1 exam' });
    expect(out.goal).toBe('Calculus 1 exam');
    // untouched slot survives
    expect(out.target_date).toBe('2026-01-01');
  });

  it('clamps absurd weekly hours and trims notes', () => {
    const out = mergeSlots({}, { goal: 'x', hours_per_week: 999, notes: '  focus limits  ' });
    expect(out.hours_per_week).toBe(84);
    expect(out.notes).toBe('focus limits');
  });

  it('ignores empty/whitespace input without clobbering existing', () => {
    const existing: PlanChangeSessionSlots = { goal: 'keep me' };
    const out = mergeSlots(existing, { goal: '   ' });
    expect(out.goal).toBe('keep me');
  });
});

describe('missingRequiredSlots', () => {
  it('reports both when nothing is set', () => {
    expect(missingRequiredSlots({})).toEqual(REQUIRED_PLAN_SLOTS);
  });

  it('reports only target_date when goal is present but date missing', () => {
    expect(missingRequiredSlots({ goal: 'Calculus 1 exam' })).toEqual(['target_date']);
  });

  it('treats a non-ISO date as still missing', () => {
    expect(missingRequiredSlots({ goal: 'g', target_date: 'in two weeks' })).toContain(
      'target_date',
    );
  });

  it('is empty once goal + ISO date are present', () => {
    expect(
      missingRequiredSlots({ goal: 'Calculus 1 exam', target_date: '2026-09-15' }),
    ).toEqual([]);
  });
});

describe('goalScopeIssue', () => {
  it('flags a generic math goal as too broad', () => {
    expect(goalScopeIssue('math test')).toBe('math');
  });

  it('flags a generic physics goal as too broad', () => {
    expect(goalScopeIssue('physics test')).toBe('physics');
  });

  it('accepts a specific exam goal', () => {
    expect(goalScopeIssue('Calculus 1 exam')).toBeNull();
  });

  it('returns null for an empty goal', () => {
    expect(goalScopeIssue(undefined)).toBeNull();
  });
});

describe('buildProposalFromSlots', () => {
  it('builds an exam proposal with target date + exam name', () => {
    const proposal = buildProposalFromSlots(
      { goal: 'Calculus 1 exam', target_date: '2026-09-15' },
      'tutor',
    );
    expect(proposal.goal).toBe('Calculus 1 exam');
    expect(proposal.final_goal_date).toBe('2026-09-15');
    expect(proposal.next_test_name).toBe('Calculus 1 exam');
    expect(proposal.agent).toBe('tutor');
  });

  it('does not set a test name for a non-exam goal', () => {
    const proposal = buildProposalFromSlots(
      { goal: 'master derivatives', target_date: '2026-09-15' },
      'mentor',
    );
    expect(proposal.next_test_name).toBeNull();
  });
});

describe('buildProposalDiff', () => {
  it('shows an arrow only for changed fields', () => {
    const proposal = buildProposalFromSlots(
      { goal: 'Calculus 1 exam', target_date: '2026-09-15' },
      'tutor',
    );
    const diff = buildProposalDiff(
      { goal: 'old goal', final_goal_date: '2026-01-01' },
      proposal,
      'en',
    );
    expect(diff).toContain('→');
    expect(diff).toContain('**');
    expect(diff).toContain('Goal');
  });

  it('omits the arrow when a field is unchanged', () => {
    const proposal = buildProposalFromSlots(
      { goal: 'Calculus 1 exam', target_date: '2026-09-15' },
      'tutor',
    );
    const diff = buildProposalDiff(
      { goal: 'Calculus 1 exam', final_goal_date: '2026-09-15' },
      proposal,
      'en',
    );
    // goal + date both unchanged → no transformation arrow
    expect(diff).not.toContain('→');
  });
});

describe('slotPrompt', () => {
  it('is localized and slot-specific', () => {
    const heGoal = slotPrompt('goal', 'he');
    const enGoal = slotPrompt('goal', 'en');
    expect(heGoal).not.toBe(enGoal);
    expect(enGoal.toLowerCase()).toContain('goal');
    const enDate = slotPrompt('target_date', 'en');
    expect(enDate.toLowerCase()).toContain('date');
  });
});

describe('re-ask escalation bounds', () => {
  it('increments the per-slot counter', () => {
    const a = bumpReask(undefined, 'goal');
    expect(a.count).toBe(1);
    const b = bumpReask(a.reask, 'goal');
    expect(b.count).toBe(2);
    // unrelated slot unaffected
    expect(b.reask.target_date).toBeUndefined();
  });

  it('escalates only after the initial ask + SLOT_REASK_LIMIT re-asks', () => {
    expect(shouldEscalate(SLOT_REASK_LIMIT + 1)).toBe(false);
    expect(shouldEscalate(SLOT_REASK_LIMIT + 2)).toBe(true);
  });

  it('offers a Mentor handoff for the tutor and pause for the mentor', () => {
    expect(escalationPrompt('tutor', 'en').toLowerCase()).toContain('mentor');
    expect(escalationPrompt('mentor', 'en').toLowerCase()).toContain('pause');
  });
});
