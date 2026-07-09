import { describe, expect, it } from 'vitest';
import {
  WEB_LIVE_AGENTS,
  resolveWebChatAgent,
  isWebLiveAgent,
  isDeprecatedChatAgent,
} from './web-agents';

describe('web-agents', () => {
  it('lists exactly four live agents', () => {
    expect(WEB_LIVE_AGENTS).toEqual(['tutor', 'mentor', 'coach', 'reviewer']);
  });

  it('resolves deprecated slugs to tutor', () => {
    expect(resolveWebChatAgent('qa_explainer')).toBe('tutor');
    expect(resolveWebChatAgent('note_taker')).toBe('tutor');
  });

  it('passes through live agents', () => {
    expect(resolveWebChatAgent('coach')).toBe('coach');
    expect(isWebLiveAgent('reviewer')).toBe(true);
  });

  it('flags deprecated chat agents', () => {
    expect(isDeprecatedChatAgent('qa_explainer')).toBe(true);
    expect(isDeprecatedChatAgent('tutor')).toBe(false);
  });
});
