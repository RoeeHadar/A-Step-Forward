import { expect, it } from 'vitest';
// AS-67 fixture: leaks env on purpose; env-leak-b must not see it (run in one fork, a then b).
it('leaks env vars', () => {
  process.env.AS67_LEAK = 'leaked';
  (process.env as Record<string, string>).NODE_ENV = 'as67-changed';
  expect(process.env.AS67_LEAK).toBe('leaked');
});
