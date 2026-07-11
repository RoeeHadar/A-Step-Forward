export type DiagnosticFlowPhase =
  | 'loading'
  | 'question'
  | 'checking'
  | 'calibrating'
  | 'generating_plan'
  | 'rate_limited'
  | 'redirecting'
  | 'error';

export function isRateLimitResponse(status: number, message: string): boolean {
  return status === 429 || /rate.?limit|too many requests/i.test(message);
}

export function isPlanLockError(message: string): boolean {
  return /plan update is already in progress/i.test(message);
}

export function isRetryablePlanError(status: number, message: string): boolean {
  if (/exhausted|no further questions/i.test(message)) return false;
  if (isPlanLockError(message)) return false;
  return (
    isRateLimitResponse(status, message) ||
    status === 503 ||
    status === 502 ||
    /temporarily unavailable/i.test(message)
  );
}

export function retryDelayMs(attempt: number, retryAfterSec?: number): number {
  if (retryAfterSec != null && retryAfterSec > 0) {
    return Math.min(retryAfterSec, 60) * 1000;
  }
  return Math.min(4000 + attempt * 3000, 25000);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function learnerHasActivePlan(): Promise<boolean> {
  const res = await fetch('/api/plans/current', { cache: 'no-store' });
  if (!res.ok) return false;
  const data = (await res.json()) as { plan?: { weeks?: unknown[] } | null };
  return Boolean(data.plan?.weeks?.length);
}

export async function pollForActivePlan(
  maxAttempts = 90,
  delayMs = 1000,
): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i += 1) {
    if (await learnerHasActivePlan()) return true;
    if (i < maxAttempts - 1) await sleep(delayMs);
  }
  return false;
}

export async function generatePlanWithRetry(options: {
  onPhase: (phase: DiagnosticFlowPhase, detail?: string) => void;
  maxAttempts?: number;
}): Promise<void> {
  if (await learnerHasActivePlan()) {
    options.onPhase('redirecting');
    return;
  }

  const maxAttempts = options.maxAttempts ?? 3;

  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    options.onPhase('generating_plan');
    const res = await fetch('/api/plans/generate', { method: 'POST' });

    if (res.ok) {
      options.onPhase('redirecting');
      return;
    }

    const text = await res.text();
    let message = text.trim() || `Request failed (${res.status})`;
    let retryAfterSec: number | undefined;
    try {
      const body = JSON.parse(text) as {
        error?: string;
        message?: string;
        retry_after_sec?: number;
      };
      message = body.error ?? body.message ?? message;
      retryAfterSec = body.retry_after_sec;
    } catch {
      /* plain text error */
    }

    if (isPlanLockError(message)) {
      options.onPhase('generating_plan', 'waiting');
      if (await pollForActivePlan()) {
        options.onPhase('redirecting');
        return;
      }
    }

    if (isRetryablePlanError(res.status, message) && attempt < maxAttempts - 1) {
      const waitMs = retryDelayMs(attempt, retryAfterSec);
      const waitSec = Math.ceil(waitMs / 1000);
      options.onPhase('rate_limited', String(waitSec));
      await sleep(waitMs);
      continue;
    }

    throw new Error(message);
  }

  if (await pollForActivePlan(10, 400)) {
    options.onPhase('redirecting');
    return;
  }

  throw new Error('Plan generation failed');
}
