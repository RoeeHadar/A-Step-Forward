import { describe, expect, it } from 'vitest';

import { agentNameSchema, learnerFacingAgents } from '../ts/agents';
import { memoryRecordSchema } from '../ts/memory';

describe('shared Zod schemas', () => {
  it('validates agent names', () => {
    expect(agentNameSchema.parse('tutor')).toBe('tutor');
    expect(learnerFacingAgents).toContain('tutor');
  });

  it('validates memory records', () => {
    const record = memoryRecordSchema.parse({
      id: 'mem-1',
      learner_id: 'user-1',
      type: 'semantic',
      content: 'Prefers visual learning',
      provenance: { kind: 'chat', agent: 'tutor' },
    });
    expect(record.type).toBe('semantic');
  });
});
