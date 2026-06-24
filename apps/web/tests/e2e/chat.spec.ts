import { test, expect } from '@playwright/test';

test.describe('tutor chat smoke', () => {
  test.skip(
    !process.env.CLERK_TEST_USER_EMAIL,
    'CLERK_TEST_USER_EMAIL not set',
  );

  test('sign in, send message, receive assistant reply', async ({ page }) => {
    await page.goto('/sign-in');
    await page.fill('input[name="identifier"]', process.env.CLERK_TEST_USER_EMAIL!);
    await page.click('button:has-text("Continue")');
    await page.fill('input[name="password"]', process.env.CLERK_TEST_USER_PASSWORD!);
    await page.click('button:has-text("Continue")');

    await page.waitForURL('**/app**', { timeout: 30_000 });
    await page.goto('/app/chat/tutor');

    const input = page.getByLabel('Message');
    await input.fill('What is a limit in calculus?');
    await page.getByRole('button', { name: 'Send message' }).click();

    const assistantMessage = page.locator('[role="log"] .me-auto').last();
    await expect(assistantMessage).not.toBeEmpty({ timeout: 25_000 });

    const reply = (await assistantMessage.textContent())?.trim() ?? '';
    expect(reply.length).toBeGreaterThanOrEqual(20);
  });
});
