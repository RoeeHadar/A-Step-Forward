import { test, expect } from '@playwright/test';

/**
 * E2E: sign-in → open chat → send message → stream response.
 * Requires Clerk test credentials via env:
 *   E2E_CLERK_EMAIL, E2E_CLERK_PASSWORD
 */
test.describe('learner chat flow', () => {
  test.skip(!process.env.E2E_CLERK_EMAIL, 'Set E2E_CLERK_EMAIL and E2E_CLERK_PASSWORD to run');

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
    await page.goto('/');
    await expect(page.getByRole('heading', { level: 1 })).toContainText(/Step Forward|learn with AI/i);
  });

  test('health endpoint responds', async ({ request }) => {
    const res = await request.get('/api/health');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.status).toBe('ok');
  });
});
