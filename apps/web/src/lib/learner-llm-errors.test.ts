import { describe, expect, it } from 'vitest';
import { classifyFetchError, classifyHttpStatus } from './llm-provider';
import { buildChatFailureMessage } from './learner-llm-errors';

describe('classifyHttpStatus', () => {
  it('maps 429 to rate_limited', () => {
    expect(classifyHttpStatus(429, 'groq').kind).toBe('rate_limited');
  });

  it('maps 413 to context_too_large', () => {
    expect(classifyHttpStatus(413, 'groq').kind).toBe('context_too_large');
  });

  it('maps 503 to provider_error', () => {
    expect(classifyHttpStatus(503, 'groq').kind).toBe('provider_error');
  });
});

describe('classifyFetchError', () => {
  it('maps AbortError to timeout', () => {
    const err = new DOMException('Aborted', 'AbortError');
    expect(classifyFetchError(err).kind).toBe('timeout');
  });
});

describe('buildChatFailureMessage', () => {
  it('returns Hebrew copy with reason and actions when locale is he', () => {
    const msg = buildChatFailureMessage({
      agent: 'tutor',
      locale: 'he',
      failure: { kind: 'context_too_large', status: 413, provider: 'groq' },
      messagePreview: 'מה הסטטוס שלי',
    });
    expect(msg).toContain('אני המורה שלך');
    expect(msg).toContain('מה קרה');
    expect(msg).toContain('מה לעשות');
    expect(msg).not.toContain('קוד שגיאה');
    expect(msg).toContain('מה הסטטוס שלי');
  });

  it('returns English copy when locale is en', () => {
    const msg = buildChatFailureMessage({
      agent: 'tutor',
      locale: 'en',
      failure: { kind: 'timeout', provider: 'groq' },
      messagePreview: 'Will I be ready?',
    });
    expect(msg).toContain("I'm your Tutor");
    expect(msg).toContain('took too long');
    expect(msg).toContain('What happened');
    expect(msg).toContain('Will I be ready?');
  });
});
