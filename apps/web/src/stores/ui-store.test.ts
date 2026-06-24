import { describe, expect, it, beforeEach } from 'vitest';
import { useChatUiStore } from './ui-store';

describe('useChatUiStore', () => {
  beforeEach(() => {
    useChatUiStore.setState({ lastAgent: 'tutor', sessionId: null });
  });

  it('tracks last selected agent', () => {
    useChatUiStore.getState().setLastAgent('coach');
    expect(useChatUiStore.getState().lastAgent).toBe('coach');
  });
});
