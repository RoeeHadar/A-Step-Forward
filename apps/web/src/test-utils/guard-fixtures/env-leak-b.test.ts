import { expect, it } from 'vitest';
it('does not see env leaked by env-leak-a', () => {
  expect(process.env.AS67_LEAK).toBeUndefined();
  expect(process.env.NODE_ENV).not.toBe('as67-changed');
});
