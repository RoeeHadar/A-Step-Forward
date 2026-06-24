import { test, expect } from '@playwright/test';

/**
 * E2E: sign-in -> open chat -> send message -> stream response.
 *
 * Requires Clerk test credentials via env:
 *   E2E_CLERK_EMAIL, E2E_CLERK_PASSWORD
 *
 * Skipped against the live Vercel deploy until Clerk Dev keys are configured
 * (see BLOCKED.md section 5b). The public-pages tests below run regardless.
 */
test.describe('learner chat flow', () => {
  test.skip(
    !process.env.E2E_CLERK_EMAIL || !process.env.E2E_CLERK_PASSWORD,
    'Set E2E_CLERK_EMAIL and E2E_CLERK_PASSWORD to run; see BLOCKED.md section 5b',
  );

  test('sign-in, chat, stream', async ({ page }) => {
    await page.goto('/sign-in');
    await page.getByLabel(/email/i).fill(process.env.E2E_CLERK_EMAIL!);
    await page.getByLabel(/password/i).fill(process.env.E2E_CLERK_PASSWORD!);
    await page.getByRole('button', { name: /continue|sign in/i }).click();

    await page.waitForURL('**/app**');
    await page.goto('/app/chat/tutor');

    const input = page.getByLabel('Message');
    await input.fill('What is a fraction?');
    await page.getByRole('button', { name: 'Send message' }).click();

    await expect(page.getByRole('log')).toContainText(/fraction|question|guide/i, {
      timeout: 15_000,
    });
  });
});

test.describe('public pages', () => {
  test('landing page loads', async ({ page }) => {
    const res = await page.goto('/');
    expect(res?.status(), 'landing page should return 2xx').toBeLessThan(400);
    await expect(page.getByRole('heading', { level: 1 })).toContainText(
      /Step Forward|learn with AI/i,
    );
  });

  test('health endpoint responds', async ({ request }) => {
    const res = await request.get('/api/health');
    expect(res.ok(), `expected 2xx, got ${res.status()}`).toBeTruthy();
    const body = (await res.json()) as { status?: string };
    expect(body.status).toBe('ok');
  });

  test('sign-in page renders', async ({ page }) => {
    const res = await page.goto('/sign-in');
    expect(res?.status(), 'sign-in page should return 2xx').toBeLessThan(400);
  });
});
