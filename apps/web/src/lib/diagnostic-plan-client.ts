export type DiagnosticFlowPhase =
  | 'loading'
  | 'question'
  | 'checking'
  | 'calibrating'
  | 'generating_plan'
  | 'rate_limited'
  | 'redirecting'
  | 'error';

const PLAN_FETCH_TIMEOUT_MS = 55_000;
const PLAN_POLL_INTERVAL_MS = 2000;
const PLAN_MAX_WAIT_MS = 120_000;

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
  const res = await fetch('/api/plans/current?exists=1', { cache: 'no-store' });
  if (!res.ok) return false;
  const data = (await res.json()) as { has_plan?: boolean };
  return Boolean(data.has_plan);
}

export async function pollForActivePlan(
  onTick?: (elapsedSec: number) => void,
  maxWaitMs = PLAN_MAX_WAIT_MS,
): Promise<boolean> {
  const started = Date.now();
  while (Date.now() - started < maxWaitMs) {
    const elapsedSec = Math.floor((Date.now() - started) / 1000);
    onTick?.(elapsedSec);
    if (await learnerHasActivePlan()) return true;
    await sleep(PLAN_POLL_INTERVAL_MS);
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

  const maxAttempts = options.maxAttempts ?? 2;
  let pollTimer: ReturnType<typeof setInterval> | null = null;

  const startPollTicker = () => {
    const started = Date.now();
    pollTimer = setInterval(() => {
      const elapsedSec = Math.floor((Date.now() - started) / 1000);
      options.onPhase('generating_plan', String(elapsedSec));
    }, PLAN_POLL_INTERVAL_MS);
  };

  const stopPollTicker = () => {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  };

  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    options.onPhase('generating_plan', '0');
    startPollTicker();

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), PLAN_FETCH_TIMEOUT_MS);

    let res: Response;
    try {
      res = await fetch('/api/plans/generate', {
        method: 'POST',
        signal: controller.signal,
      });
    } catch (err) {
      stopPollTicker();
      clearTimeout(timeout);
      if (await pollForActivePlan((sec) => options.onPhase('generating_plan', String(sec)))) {
        options.onPhase('redirecting');
        return;
      }
      if (attempt < maxAttempts - 1) continue;
      throw new Error(
        err instanceof Error && err.name === 'AbortError'
          ? 'Plan generation timed out. Please try again.'
          : err instanceof Error
            ? err.message
            : 'Plan generation failed',
      );
    }

    stopPollTicker();
    clearTimeout(timeout);

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

    if (
      (isPlanLockError(message) || res.status === 504) &&
      (await pollForActivePlan((sec) => options.onPhase('generating_plan', String(sec))))
    ) {
      options.onPhase('redirecting');
      return;
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

  if (await pollForActivePlan((sec) => options.onPhase('generating_plan', String(sec)), 20_000)) {
    options.onPhase('redirecting');
    return;
  }

  throw new Error('Plan generation failed');
}
