import { describe, expect, it } from 'vitest';
import { agentNameSchema, learnerFacingAgents } from '@asf/schemas/agents';
import { memoryRecordSchema } from '@asf/schemas/memory';

describe('schemas', () => {
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
