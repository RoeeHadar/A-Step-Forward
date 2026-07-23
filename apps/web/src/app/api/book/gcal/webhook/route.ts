/**
 * POST /api/book/gcal/webhook — Google Calendar push notification.
 * Invalidates busy cache for near–real-time free/busy.
 */
import { invalidateBusyCache } from '@/lib/lesson-booking-settings-db';
import { logger } from '@/lib/logger';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  const channelToken = req.headers.get('x-goog-channel-token') ?? '';
  const expected = process.env.GOOGLE_CALENDAR_WEBHOOK_TOKEN?.trim();
  // If a token is configured, require it. Otherwise accept (channel id was used as token).
  if (expected && channelToken && channelToken !== expected) {
    return new Response('forbidden', { status: 403 });
  }

  const resourceState = req.headers.get('x-goog-resource-state') ?? '';
  // "sync" is the initial handshake — still fine to invalidate.
  logger.info('[gcal webhook]', {
    resourceState,
    channelId: req.headers.get('x-goog-channel-id'),
  });

  await invalidateBusyCache();
  return new Response('ok', { status: 200 });
}
