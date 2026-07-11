import { describe, expect, it } from 'vitest';
import {
  isRateLimitResponse,
  isRetryablePlanError,
  retryDelayMs,
} from './diagnostic-plan-client';

describe('diagnostic-plan-client', () => {
  it('detects rate limit responses', () => {
    expect(isRateLimitResponse(429, 'Too many requests')).toBe(true);
    expect(isRateLimitResponse(500, 'rate limit exceeded')).toBe(true);
    expect(isRateLimitResponse(500, 'database error')).toBe(false);
  });

  it('treats 503 as retryable for plan generation', () => {
    expect(isRetryablePlanError(503, 'temporarily unavailable')).toBe(true);
  });

  it('treats plan lock contention as retryable', () => {
    expect(isRetryablePlanError(500, 'A plan update is already in progress for this learner')).toBe(
      true,
    );
  });

  it('does not retry exhausted diagnostic responses', () => {
    expect(isRetryablePlanError(409, 'No further questions available for your profile yet.')).toBe(
      false,
    );
  });

  it('honors retry-after when provided', () => {
    expect(retryDelayMs(0, 20)).toBe(20000);
  });
});
