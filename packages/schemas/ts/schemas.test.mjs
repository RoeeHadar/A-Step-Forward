import assert from 'node:assert/strict';
import test from 'node:test';

import { agentNameSchema, learnerFacingAgents } from './agents.ts';
import { memoryRecordSchema } from './memory.ts';

test('agent schema accepts learner-facing agents', () => {
  assert.equal(agentNameSchema.parse('tutor'), 'tutor');
  assert.ok(learnerFacingAgents.includes('tutor'));
});

test('memory record schema accepts persisted memory records', () => {
  const record = memoryRecordSchema.parse({ id: 'm1', type: 'concept', text: 'Needs practice' });
  assert.equal(record.id, 'm1');
});
