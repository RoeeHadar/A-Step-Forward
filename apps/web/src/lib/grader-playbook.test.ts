import { describe, expect, it } from 'vitest';
import { loadGraderPlaybook, resetGraderPlaybookCache } from './grader-playbook';

describe('grader playbook load', () => {
  it('returns non-empty playbook text', () => {
    resetGraderPlaybookCache();
    const text = loadGraderPlaybook();
    expect(text.length).toBeGreaterThan(40);
    expect(text.toLowerCase()).toMatch(/process|kpi|partial/i);
  });
});
