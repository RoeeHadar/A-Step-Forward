/**
 * Notify learner (+ linked teacher) when a sealed attempt is released or needs human check.
 */
import 'server-only';
import { createNotification, getAcceptedTeacherForStudent } from '@/lib/social-db';
import { logger } from '@/lib/logger';

export async function notifyAttemptReleased(input: {
  learnerId: string;
  attemptId: string;
  score: number;
  passed: boolean;
  kind?: string;
}): Promise<void> {
  const pct = Math.round(input.score * 100);
  const title = input.passed ? 'המבחן נבדק — עברת' : 'המבחן נבדק — יש מה לשפר';
  const body = `ציון ${pct}%. לחצו לצפייה במשוב המלא.`;
  const href = `/app/tests/${input.attemptId}`;
  try {
    await createNotification({
      userId: input.learnerId,
      kind: 'test_released',
      title,
      body,
      payload: {
        attempt_id: input.attemptId,
        score: input.score,
        passed: input.passed,
        kind: input.kind ?? null,
      },
      href,
    });
  } catch (err) {
    logger.warn('[release-notify] student notify failed', { err: String(err) });
  }

  try {
    const teacher = await getAcceptedTeacherForStudent(input.learnerId);
    if (teacher?.clerk_user_id) {
      await createNotification({
        userId: teacher.clerk_user_id,
        kind: 'test_released_teacher',
        title: 'מבחן תלמיד שוחרר אחרי בדיקה',
        body: `ציון ${pct}% · ${input.passed ? 'עבר' : 'לא עבר'}`,
        payload: {
          attempt_id: input.attemptId,
          student_id: input.learnerId,
          score: input.score,
          passed: input.passed,
        },
        href: `/educator/students/${input.learnerId}?tab=tests&attempt=${input.attemptId}`,
      });
    }
  } catch (err) {
    logger.warn('[release-notify] teacher notify failed', { err: String(err) });
  }
}

export async function notifyAttemptNeedsHuman(input: {
  learnerId: string;
  attemptId: string;
}): Promise<void> {
  const href = `/app/tests/${input.attemptId}`;
  try {
    await createNotification({
      userId: input.learnerId,
      kind: 'test_needs_human',
      title: 'המבחן ממתין לבדיקת מורה',
      body: 'הבודק האוטומטי לא סיים — המורה יקבל את המבחן לתור.',
      payload: { attempt_id: input.attemptId },
      href,
    });
  } catch (err) {
    logger.warn('[release-notify] needs_human student notify failed', { err: String(err) });
  }

  try {
    const teacher = await getAcceptedTeacherForStudent(input.learnerId);
    if (teacher?.clerk_user_id) {
      await createNotification({
        userId: teacher.clerk_user_id,
        kind: 'test_needs_human_teacher',
        title: 'מבחן דורש בדיקה ידנית',
        body: 'הבודק האוטומטי נכשל — פתחו את תור המבחנים.',
        payload: {
          attempt_id: input.attemptId,
          student_id: input.learnerId,
        },
        href: `/educator/students/${input.learnerId}?tab=tests&attempt=${input.attemptId}`,
      });
    }
  } catch (err) {
    logger.warn('[release-notify] needs_human teacher notify failed', { err: String(err) });
  }
}
