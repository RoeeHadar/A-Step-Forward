export type DiagnosticFlowPhase =
  | 'loading'
  | 'question'
  | 'checking'
  | 'calibrating'
  | 'generating_plan'
  | 'rate_limited'
  | 'redirecting'
  | 'error';

const PLAN_GENERATE_TIMEOUT_MS = 90_000;
const PLAN_POLL_INTERVAL_MS = 2000;
const PLAN_MAX_WAIT_MS = 90_000;

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
    status === 504 ||
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

type GenerateAttemptResult =
  | { kind: 'ok' }
  | { kind: 'timeout' }
  | { kind: 'error'; status: number; message: string; retryAfterSec?: number };

async function postPlanGenerate(): Promise<GenerateAttemptResult> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), PLAN_GENERATE_TIMEOUT_MS);
  try {
    const res = await fetch('/api/plans/generate?fast=1', {
      method: 'POST',
      signal: controller.signal,
      cache: 'no-store',
    });
    if (res.ok) return { kind: 'ok' };

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
    return { kind: 'error', status: res.status, message, retryAfterSec };
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      return { kind: 'timeout' };
    }
    return {
      kind: 'error',
      status: 0,
      message: err instanceof Error ? err.message : 'Plan generation failed',
    };
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Kick off plan generation and poll `exists=1` in parallel until the plan row
 * is visible or we hit the wait budget.
 */
export async function generatePlanWithRetry(options: {
  onPhase: (phase: DiagnosticFlowPhase, detail?: string) => void;
  maxAttempts?: number;
}): Promise<void> {
  if (await learnerHasActivePlan()) {
    options.onPhase('redirecting');
    return;
  }

  const maxAttempts = options.maxAttempts ?? 2;
  const started = Date.now();
  let retriesUsed = 0;
  let pendingGenerate: Promise<GenerateAttemptResult> | null = postPlanGenerate();
  let fatalError: string | null = null;

  const tick = () => {
    const elapsedSec = Math.floor((Date.now() - started) / 1000);
    options.onPhase('generating_plan', String(elapsedSec));
  };

  while (Date.now() - started < PLAN_MAX_WAIT_MS) {
    tick();

    if (await learnerHasActivePlan()) {
      options.onPhase('redirecting');
      return;
    }

    if (!pendingGenerate) {
      await sleep(PLAN_POLL_INTERVAL_MS);
      continue;
    }

    const race = await Promise.race([
      pendingGenerate.then((result) => ({ source: 'generate' as const, result })),
      sleep(PLAN_POLL_INTERVAL_MS).then(() => ({ source: 'poll' as const, result: null })),
    ]);

    if (race.source === 'poll') continue;

    const result = race.result;
    pendingGenerate = null;

    if (result.kind === 'ok') {
      if (await learnerHasActivePlan()) {
        options.onPhase('redirecting');
        return;
      }
      continue;
    }

    if (result.kind === 'timeout' || isPlanLockError(result.message)) {
      continue;
    }

    if (
      isRetryablePlanError(result.status, result.message) &&
      retriesUsed < maxAttempts - 1
    ) {
      retriesUsed += 1;
      const waitMs = retryDelayMs(retriesUsed - 1, result.retryAfterSec);
      options.onPhase('rate_limited', String(Math.ceil(waitMs / 1000)));
      await sleep(waitMs);
      pendingGenerate = postPlanGenerate();
      continue;
    }

    fatalError = result.message;
    break;
  }

  if (await learnerHasActivePlan()) {
    options.onPhase('redirecting');
    return;
  }

  if (fatalError) {
    throw new Error(fatalError);
  }

  throw new Error(
    'Plan generation timed out. Please refresh the page or open the dashboard to retry.',
  );
}
