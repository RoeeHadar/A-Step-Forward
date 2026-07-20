/**
 * Social identity + connections + notifications (Teacher / Friends platform).
 *
 * Same Neon DB as the rest of the free-tier app. Tables are created lazily
 * (house style) and also tracked in Alembic 0021.
 */
import 'server-only';
import { neon, neonConfig } from '@neondatabase/serverless';
import { logger } from '@/lib/logger';
import type { AppRole } from '@/lib/auth';
import {
  normalizeUsername,
  validateRealName,
  validateUsername,
} from '@/lib/social-identity';

export {
  normalizeUsername,
  suggestUsernameFromRealName,
  validateRealName,
  validateUsername,
} from '@/lib/social-identity';

neonConfig.fetchConnectionCache = true;

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = url ? neon(url) : null;

export type SocialRole = 'learner' | 'educator';

export interface AppUser {
  clerk_user_id: string;
  role: SocialRole;
  username: string;
  real_name: string;
  nickname: string | null;
  about_me: string | null;
  profile_complete: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationRow {
  id: string;
  user_id: string;
  kind: string;
  title: string;
  body: string;
  payload: Record<string, unknown>;
  href: string | null;
  read_at: string | null;
  created_at: string;
}

export type ConnectionStatus = 'pending' | 'accepted' | 'declined' | 'revoked';

export interface TeacherStudentLink {
  id: string;
  teacher_id: string;
  student_id: string;
  status: ConnectionStatus;
  initiated_by: string;
  message: string | null;
  created_at: string;
  updated_at: string;
  responded_at: string | null;
}

let ensured = false;

export async function ensureSocialTables(): Promise<boolean> {
  if (!sql) return false;
  if (ensured) return true;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS app_users (
        clerk_user_id   TEXT PRIMARY KEY,
        role            TEXT NOT NULL CHECK (role IN ('learner', 'educator')),
        username        TEXT NOT NULL,
        real_name       TEXT NOT NULL,
        nickname        TEXT,
        about_me        TEXT,
        profile_complete BOOLEAN NOT NULL DEFAULT FALSE,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await sql`CREATE UNIQUE INDEX IF NOT EXISTS ux_app_users_username_lower ON app_users (lower(username))`;
    await sql`CREATE INDEX IF NOT EXISTS ix_app_users_real_name ON app_users (lower(real_name))`;
    await sql`CREATE INDEX IF NOT EXISTS ix_app_users_role ON app_users (role)`;

    await sql`
      CREATE TABLE IF NOT EXISTS notifications (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id     TEXT NOT NULL,
        kind        TEXT NOT NULL,
        title       TEXT NOT NULL,
        body        TEXT NOT NULL DEFAULT '',
        payload     JSONB NOT NULL DEFAULT '{}'::jsonb,
        href        TEXT,
        read_at     TIMESTAMPTZ,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await sql`CREATE INDEX IF NOT EXISTS ix_notifications_user ON notifications (user_id, created_at DESC)`;
    await sql`CREATE INDEX IF NOT EXISTS ix_notifications_unread ON notifications (user_id) WHERE read_at IS NULL`;

    await sql`
      CREATE TABLE IF NOT EXISTS teacher_student_links (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        teacher_id    TEXT NOT NULL REFERENCES app_users(clerk_user_id),
        student_id    TEXT NOT NULL REFERENCES app_users(clerk_user_id),
        status        TEXT NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'accepted', 'declined', 'revoked')),
        initiated_by  TEXT NOT NULL,
        message       TEXT,
        created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        responded_at  TIMESTAMPTZ
      )
    `;
    await sql`CREATE INDEX IF NOT EXISTS ix_ts_links_teacher ON teacher_student_links (teacher_id, status)`;
    await sql`CREATE INDEX IF NOT EXISTS ix_ts_links_student ON teacher_student_links (student_id, status)`;
    await sql`
      CREATE UNIQUE INDEX IF NOT EXISTS ux_ts_one_active_teacher
      ON teacher_student_links (student_id)
      WHERE status IN ('pending', 'accepted')
    `;

    await sql`
      CREATE TABLE IF NOT EXISTS friendships (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        requester_id  TEXT NOT NULL REFERENCES app_users(clerk_user_id),
        addressee_id  TEXT NOT NULL REFERENCES app_users(clerk_user_id),
        status        TEXT NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'accepted', 'declined', 'revoked')),
        created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        responded_at  TIMESTAMPTZ,
        CHECK (requester_id <> addressee_id)
      )
    `;
    await sql`CREATE INDEX IF NOT EXISTS ix_friendships_requester ON friendships (requester_id, status)`;
    await sql`CREATE INDEX IF NOT EXISTS ix_friendships_addressee ON friendships (addressee_id, status)`;

    await sql`
      CREATE TABLE IF NOT EXISTS teacher_notes (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        teacher_id    TEXT NOT NULL,
        student_id    TEXT NOT NULL,
        kind          TEXT NOT NULL DEFAULT 'note',
        content       TEXT NOT NULL,
        created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await sql`CREATE INDEX IF NOT EXISTS ix_teacher_notes_student ON teacher_notes (student_id, created_at DESC)`;

    await sql`
      CREATE TABLE IF NOT EXISTS teacher_audit_log (
        id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        teacher_id    TEXT NOT NULL,
        student_id    TEXT NOT NULL,
        action        TEXT NOT NULL,
        reason        TEXT,
        payload       JSONB NOT NULL DEFAULT '{}'::jsonb,
        created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await sql`CREATE INDEX IF NOT EXISTS ix_teacher_audit_student ON teacher_audit_log (student_id, created_at DESC)`;

    ensured = true;
    return true;
  } catch (err) {
    logger.error('[social-db] ensureSocialTables failed', { err: String(err) });
    return false;
  }
}

function requireSql() {
  if (!sql) throw new Error('DATABASE_URL is not configured');
  return sql;
}

export async function getAppUser(clerkUserId: string): Promise<AppUser | null> {
  if (!sql) return null;
  await ensureSocialTables();
  const rows = (await sql`
    SELECT clerk_user_id, role, username, real_name, nickname, about_me,
           profile_complete, created_at::text, updated_at::text
    FROM app_users WHERE clerk_user_id = ${clerkUserId} LIMIT 1
  `) as AppUser[];
  return rows[0] ?? null;
}

export async function getAppUserByUsername(username: string): Promise<AppUser | null> {
  if (!sql) return null;
  await ensureSocialTables();
  const rows = (await sql`
    SELECT clerk_user_id, role, username, real_name, nickname, about_me,
           profile_complete, created_at::text, updated_at::text
    FROM app_users WHERE lower(username) = lower(${username.trim()}) LIMIT 1
  `) as AppUser[];
  return rows[0] ?? null;
}

export async function upsertAppUser(input: {
  clerkUserId: string;
  role: SocialRole;
  username: string;
  realName: string;
  nickname?: string | null;
  aboutMe?: string | null;
  profileComplete?: boolean;
}): Promise<AppUser> {
  const s = requireSql();
  await ensureSocialTables();
  const err = validateUsername(input.username);
  if (err) throw new Error(err);
  const username = normalizeUsername(input.username);
  const realName = input.realName.trim().replace(/\s+/g, ' ');
  const realErr = validateRealName(realName);
  if (realErr) throw new Error(realErr);

  const rows = (await s`
    INSERT INTO app_users (
      clerk_user_id, role, username, real_name, nickname, about_me, profile_complete, created_at, updated_at
    )
    VALUES (
      ${input.clerkUserId},
      ${input.role},
      ${username},
      ${realName},
      ${input.nickname?.trim() || null},
      ${input.aboutMe?.trim() || null},
      ${input.profileComplete ?? true},
      NOW(), NOW()
    )
    ON CONFLICT (clerk_user_id) DO UPDATE SET
      role = EXCLUDED.role,
      username = EXCLUDED.username,
      real_name = EXCLUDED.real_name,
      nickname = EXCLUDED.nickname,
      about_me = COALESCE(EXCLUDED.about_me, app_users.about_me),
      profile_complete = EXCLUDED.profile_complete,
      updated_at = NOW()
    RETURNING clerk_user_id, role, username, real_name, nickname, about_me,
              profile_complete, created_at::text, updated_at::text
  `) as AppUser[];
  return rows[0]!;
}

export async function updateTeacherAboutMe(teacherId: string, aboutMe: string): Promise<void> {
  const s = requireSql();
  await ensureSocialTables();
  await s`
    UPDATE app_users
    SET about_me = ${aboutMe.trim().slice(0, 2000)}, updated_at = NOW()
    WHERE clerk_user_id = ${teacherId} AND role = 'educator'
  `;
}

export async function searchLearnersForInvite(query: string, limit = 12): Promise<AppUser[]> {
  if (!sql) return [];
  await ensureSocialTables();
  const q = query.trim();
  if (q.length < 2) return [];
  const like = `%${q.toLowerCase()}%`;
  return (await sql`
    SELECT clerk_user_id, role, username, real_name, nickname, about_me,
           profile_complete, created_at::text, updated_at::text
    FROM app_users
    WHERE role = 'learner'
      AND profile_complete = TRUE
      AND (lower(username) LIKE ${like} OR lower(real_name) LIKE ${like})
    ORDER BY username ASC
    LIMIT ${limit}
  `) as AppUser[];
}

export async function searchLearnersForFriends(
  query: string,
  excludeUserId: string,
  limit = 12,
): Promise<AppUser[]> {
  if (!sql) return [];
  await ensureSocialTables();
  const q = query.trim();
  if (q.length < 2) return [];
  const like = `%${q.toLowerCase()}%`;
  return (await sql`
    SELECT clerk_user_id, role, username, real_name, nickname, about_me,
           profile_complete, created_at::text, updated_at::text
    FROM app_users
    WHERE role = 'learner'
      AND profile_complete = TRUE
      AND clerk_user_id <> ${excludeUserId}
      AND (lower(username) LIKE ${like} OR lower(real_name) LIKE ${like})
    ORDER BY username ASC
    LIMIT ${limit}
  `) as AppUser[];
}

export async function createNotification(input: {
  userId: string;
  kind: string;
  title: string;
  body?: string;
  payload?: Record<string, unknown>;
  href?: string | null;
}): Promise<string | null> {
  if (!sql) return null;
  await ensureSocialTables();
  try {
    const rows = (await sql`
      INSERT INTO notifications (user_id, kind, title, body, payload, href)
      VALUES (
        ${input.userId},
        ${input.kind},
        ${input.title},
        ${input.body ?? ''},
        ${JSON.stringify(input.payload ?? {})}::jsonb,
        ${input.href ?? null}
      )
      RETURNING id::text
    `) as Array<{ id: string }>;
    return rows[0]?.id ?? null;
  } catch (err) {
    logger.error('[social-db] createNotification failed', { err: String(err) });
    return null;
  }
}

export async function listNotifications(userId: string, limit = 40): Promise<NotificationRow[]> {
  if (!sql) return [];
  await ensureSocialTables();
  return (await sql`
    SELECT id::text, user_id, kind, title, body, payload, href,
           read_at::text, created_at::text
    FROM notifications
    WHERE user_id = ${userId}
    ORDER BY created_at DESC
    LIMIT ${limit}
  `) as NotificationRow[];
}

export async function countUnreadNotifications(userId: string): Promise<number> {
  if (!sql) return 0;
  await ensureSocialTables();
  const rows = (await sql`
    SELECT COUNT(*)::int AS n FROM notifications
    WHERE user_id = ${userId} AND read_at IS NULL
  `) as Array<{ n: number }>;
  return Number(rows[0]?.n ?? 0);
}

export async function markNotificationRead(userId: string, notificationId: string): Promise<boolean> {
  if (!sql) return false;
  await ensureSocialTables();
  const rows = (await sql`
    UPDATE notifications SET read_at = NOW()
    WHERE id = ${notificationId}::uuid AND user_id = ${userId} AND read_at IS NULL
    RETURNING id
  `) as unknown[];
  return rows.length > 0;
}

export async function markAllNotificationsRead(userId: string): Promise<number> {
  if (!sql) return 0;
  await ensureSocialTables();
  const rows = (await sql`
    UPDATE notifications SET read_at = NOW()
    WHERE user_id = ${userId} AND read_at IS NULL
    RETURNING id
  `) as unknown[];
  return rows.length;
}

export async function getAcceptedTeacherForStudent(studentId: string): Promise<AppUser | null> {
  if (!sql) return null;
  await ensureSocialTables();
  const rows = (await sql`
    SELECT u.clerk_user_id, u.role, u.username, u.real_name, u.nickname, u.about_me,
           u.profile_complete, u.created_at::text, u.updated_at::text
    FROM teacher_student_links l
    JOIN app_users u ON u.clerk_user_id = l.teacher_id
    WHERE l.student_id = ${studentId} AND l.status = 'accepted'
    LIMIT 1
  `) as AppUser[];
  return rows[0] ?? null;
}

export async function assertTeacherOfStudent(teacherId: string, studentId: string): Promise<boolean> {
  if (!sql) return false;
  await ensureSocialTables();
  const rows = (await sql`
    SELECT 1 FROM teacher_student_links
    WHERE teacher_id = ${teacherId}
      AND student_id = ${studentId}
      AND status = 'accepted'
    LIMIT 1
  `) as unknown[];
  return rows.length > 0;
}

export async function listTeacherStudents(
  teacherId: string,
): Promise<Array<AppUser & { linked_at: string }>> {
  if (!sql) return [];
  await ensureSocialTables();
  return (await sql`
    SELECT u.clerk_user_id, u.role, u.username, u.real_name, u.nickname, u.about_me,
           u.profile_complete, u.created_at::text, u.updated_at::text,
           l.updated_at::text AS linked_at
    FROM teacher_student_links l
    JOIN app_users u ON u.clerk_user_id = l.student_id
    WHERE l.teacher_id = ${teacherId} AND l.status = 'accepted'
    ORDER BY u.real_name ASC
  `) as Array<AppUser & { linked_at: string }>;
}

/** Accepted links for cron sweeps (weekly-gate-due, etc.). */
export async function listAcceptedTeacherStudentPairs(
  limit = 200,
): Promise<Array<{ teacher_id: string; student_id: string }>> {
  if (!sql) return [];
  await ensureSocialTables();
  return (await sql`
    SELECT teacher_id, student_id
    FROM teacher_student_links
    WHERE status = 'accepted'
    ORDER BY updated_at DESC
    LIMIT ${limit}
  `) as Array<{ teacher_id: string; student_id: string }>;
}

export async function countTeacherStudents(teacherId: string): Promise<number> {
  if (!sql) return 0;
  await ensureSocialTables();
  const rows = (await sql`
    SELECT COUNT(*)::int AS n FROM teacher_student_links
    WHERE teacher_id = ${teacherId} AND status = 'accepted'
  `) as Array<{ n: number }>;
  return Number(rows[0]?.n ?? 0);
}

export async function sendTeacherInvite(input: {
  teacherId: string;
  studentId: string;
  message?: string | null;
}): Promise<{ ok: true; id: string } | { ok: false; error: string }> {
  const s = requireSql();
  await ensureSocialTables();
  if (input.teacherId === input.studentId) {
    return { ok: false, error: 'Cannot invite yourself.' };
  }
  const teacher = await getAppUser(input.teacherId);
  const student = await getAppUser(input.studentId);
  if (!teacher || teacher.role !== 'educator') {
    return { ok: false, error: 'Only teachers can send invites.' };
  }
  if (!student || student.role !== 'learner') {
    return { ok: false, error: 'Invitee must be a student.' };
  }

  const blocking = (await s`
    SELECT status FROM teacher_student_links
    WHERE student_id = ${input.studentId}
      AND status IN ('pending', 'accepted')
    LIMIT 1
  `) as Array<{ status: string }>;
  if (blocking[0]?.status === 'accepted') {
    return { ok: false, error: 'Student already has a teacher.' };
  }
  if (blocking[0]?.status === 'pending') {
    return { ok: false, error: 'Student already has a pending invite.' };
  }

  try {
    const rows = (await s`
      INSERT INTO teacher_student_links (teacher_id, student_id, status, initiated_by, message)
      VALUES (${input.teacherId}, ${input.studentId}, 'pending', ${input.teacherId}, ${input.message?.trim() || null})
      RETURNING id::text
    `) as Array<{ id: string }>;
    const id = rows[0]?.id;
    if (!id) return { ok: false, error: 'Insert failed.' };

    await createNotification({
      userId: input.studentId,
      kind: 'teacher_invite',
      title: 'בקשת חיבור ממורה / Teacher connection request',
      body: `${teacher.real_name} (@${teacher.username}) רוצה להיות המורה שלך.`,
      payload: { link_id: id, teacher_id: input.teacherId },
      href: '/app/notifications',
    });
    return { ok: true, id };
  } catch (err) {
    logger.error('[social-db] sendTeacherInvite failed', { err: String(err) });
    return { ok: false, error: 'Could not send invite.' };
  }
}

export async function respondTeacherInvite(input: {
  studentId: string;
  linkId: string;
  accept: boolean;
}): Promise<{ ok: true } | { ok: false; error: string }> {
  const s = requireSql();
  await ensureSocialTables();
  const rows = (await s`
    SELECT id::text, teacher_id, student_id, status
    FROM teacher_student_links
    WHERE id = ${input.linkId}::uuid AND student_id = ${input.studentId}
    LIMIT 1
  `) as Array<{ id: string; teacher_id: string; student_id: string; status: string }>;
  const link = rows[0];
  if (!link || link.status !== 'pending') {
    return { ok: false, error: 'Invite not found or already handled.' };
  }

  const next = input.accept ? 'accepted' : 'declined';
  await s`
    UPDATE teacher_student_links
    SET status = ${next}, responded_at = NOW(), updated_at = NOW()
    WHERE id = ${input.linkId}::uuid
  `;

  const student = await getAppUser(input.studentId);
  await createNotification({
    userId: link.teacher_id,
    kind: input.accept ? 'teacher_invite_accepted' : 'teacher_invite_declined',
    title: input.accept ? 'התלמיד אישר חיבור' : 'התלמיד דחה חיבור',
    body: student
      ? `${student.real_name} (@${student.username}) ${input.accept ? 'אישר/ה' : 'דחה/תה'} את הבקשה.`
      : '',
    payload: { link_id: link.id, student_id: input.studentId },
    href: input.accept ? `/educator/students/${input.studentId}` : '/educator',
  });
  return { ok: true };
}

export async function disconnectTeacherStudent(input: {
  actorId: string;
  teacherId: string;
  studentId: string;
}): Promise<{ ok: true } | { ok: false; error: string }> {
  const s = requireSql();
  await ensureSocialTables();
  if (input.actorId !== input.teacherId && input.actorId !== input.studentId) {
    return { ok: false, error: 'Forbidden.' };
  }
  const updated = (await s`
    UPDATE teacher_student_links
    SET status = 'revoked', updated_at = NOW(), responded_at = NOW()
    WHERE teacher_id = ${input.teacherId}
      AND student_id = ${input.studentId}
      AND status = 'accepted'
    RETURNING id::text
  `) as Array<{ id: string }>;
  if (!updated[0]) return { ok: false, error: 'No active link.' };

  const otherId = input.actorId === input.teacherId ? input.studentId : input.teacherId;
  const otherIsTeacher = otherId === input.teacherId;
  await createNotification({
    userId: otherId,
    kind: 'teacher_disconnected',
    title: 'החיבור למורה בוטל / Teacher link ended',
    body: 'החיבור בין מורה לתלמיד בוטל.',
    payload: { teacher_id: input.teacherId, student_id: input.studentId },
    href: otherIsTeacher ? '/educator' : '/app/notifications',
  });
  return { ok: true };
}

export async function sendFriendRequest(input: {
  requesterId: string;
  addresseeId: string;
}): Promise<{ ok: true; id: string } | { ok: false; error: string }> {
  const s = requireSql();
  await ensureSocialTables();
  if (input.requesterId === input.addresseeId) {
    return { ok: false, error: 'Cannot friend yourself.' };
  }
  const a = await getAppUser(input.requesterId);
  const b = await getAppUser(input.addresseeId);
  if (!a || !b || a.role !== 'learner' || b.role !== 'learner') {
    return { ok: false, error: 'Friends are for students only.' };
  }

  const existing = (await s`
    SELECT id::text, status FROM friendships
    WHERE (requester_id = ${input.requesterId} AND addressee_id = ${input.addresseeId})
       OR (requester_id = ${input.addresseeId} AND addressee_id = ${input.requesterId})
    LIMIT 1
  `) as Array<{ id: string; status: string }>;
  if (existing[0]?.status === 'accepted') {
    return { ok: false, error: 'Already friends.' };
  }
  if (existing[0]?.status === 'pending') {
    return { ok: false, error: 'Request already pending.' };
  }

  try {
    const rows = (await s`
      INSERT INTO friendships (requester_id, addressee_id, status)
      VALUES (${input.requesterId}, ${input.addresseeId}, 'pending')
      RETURNING id::text
    `) as Array<{ id: string }>;
    const id = rows[0]?.id;
    if (!id) return { ok: false, error: 'Insert failed.' };
    await createNotification({
      userId: input.addresseeId,
      kind: 'friend_request',
      title: 'בקשת חברות / Friend request',
      body: `${a.real_name} (@${a.username}) רוצה להיות חבר/ה.`,
      payload: { friendship_id: id, requester_id: input.requesterId },
      href: '/app/friends',
    });
    return { ok: true, id };
  } catch (err) {
    logger.error('[social-db] sendFriendRequest failed', { err: String(err) });
    return { ok: false, error: 'Could not send request.' };
  }
}

export async function respondFriendRequest(input: {
  userId: string;
  friendshipId: string;
  accept: boolean;
}): Promise<{ ok: true } | { ok: false; error: string }> {
  const s = requireSql();
  await ensureSocialTables();
  const rows = (await s`
    SELECT id::text, requester_id, addressee_id, status
    FROM friendships WHERE id = ${input.friendshipId}::uuid LIMIT 1
  `) as Array<{ id: string; requester_id: string; addressee_id: string; status: string }>;
  const f = rows[0];
  if (!f || f.addressee_id !== input.userId || f.status !== 'pending') {
    return { ok: false, error: 'Request not found.' };
  }
  const next = input.accept ? 'accepted' : 'declined';
  await s`
    UPDATE friendships
    SET status = ${next}, responded_at = NOW(), updated_at = NOW()
    WHERE id = ${input.friendshipId}::uuid
  `;
  const me = await getAppUser(input.userId);
  await createNotification({
    userId: f.requester_id,
    kind: input.accept ? 'friend_accepted' : 'friend_declined',
    title: input.accept ? 'בקשת החברות אושרה' : 'בקשת החברות נדחתה',
    body: me ? `${me.real_name} (@${me.username})` : '',
    payload: { friendship_id: f.id },
    href: '/app/friends',
  });
  return { ok: true };
}

export async function listFriends(userId: string): Promise<AppUser[]> {
  if (!sql) return [];
  await ensureSocialTables();
  return (await sql`
    SELECT u.clerk_user_id, u.role, u.username, u.real_name, u.nickname, u.about_me,
           u.profile_complete, u.created_at::text, u.updated_at::text
    FROM friendships f
    JOIN app_users u ON u.clerk_user_id = CASE
      WHEN f.requester_id = ${userId} THEN f.addressee_id
      ELSE f.requester_id
    END
    WHERE f.status = 'accepted'
      AND (f.requester_id = ${userId} OR f.addressee_id = ${userId})
    ORDER BY u.real_name ASC
  `) as AppUser[];
}

export async function listPendingFriendRequests(
  userId: string,
): Promise<Array<{ id: string; from: AppUser }>> {
  if (!sql) return [];
  await ensureSocialTables();
  const rows = (await sql`
    SELECT f.id::text AS friendship_id,
           u.clerk_user_id, u.role, u.username, u.real_name, u.nickname, u.about_me,
           u.profile_complete, u.created_at::text, u.updated_at::text
    FROM friendships f
    JOIN app_users u ON u.clerk_user_id = f.requester_id
    WHERE f.addressee_id = ${userId} AND f.status = 'pending'
    ORDER BY f.created_at DESC
  `) as Array<AppUser & { friendship_id: string }>;
  return rows.map((r) => ({
    id: r.friendship_id,
    from: {
      clerk_user_id: r.clerk_user_id,
      role: r.role,
      username: r.username,
      real_name: r.real_name,
      nickname: r.nickname,
      about_me: r.about_me,
      profile_complete: r.profile_complete,
      created_at: r.created_at,
      updated_at: r.updated_at,
    },
  }));
}

export async function areFriends(a: string, b: string): Promise<boolean> {
  if (!sql) return false;
  await ensureSocialTables();
  const rows = (await sql`
    SELECT 1 FROM friendships
    WHERE status = 'accepted'
      AND (
        (requester_id = ${a} AND addressee_id = ${b})
        OR (requester_id = ${b} AND addressee_id = ${a})
      )
    LIMIT 1
  `) as unknown[];
  return rows.length > 0;
}

export async function addTeacherNote(input: {
  teacherId: string;
  studentId: string;
  content: string;
  kind?: 'note' | 'concern';
}): Promise<string | null> {
  if (!sql) return null;
  await ensureSocialTables();
  const ok = await assertTeacherOfStudent(input.teacherId, input.studentId);
  if (!ok) return null;
  const kind = input.kind ?? 'note';
  const rows = (await sql`
    INSERT INTO teacher_notes (teacher_id, student_id, kind, content)
    VALUES (${input.teacherId}, ${input.studentId}, ${kind}, ${input.content.trim().slice(0, 4000)})
    RETURNING id::text
  `) as Array<{ id: string }>;
  await createNotification({
    userId: input.studentId,
    kind: kind === 'concern' ? 'teacher_concern' : 'teacher_note',
    title: kind === 'concern' ? 'המורה סימן משהו לבדיקה' : 'הודעה מהמורה',
    body: input.content.trim().slice(0, 200),
    payload: { teacher_id: input.teacherId, note_id: rows[0]?.id },
    href: '/app/notifications',
  });
  return rows[0]?.id ?? null;
}

export async function listTeacherNotes(
  studentId: string,
  limit = 30,
): Promise<Array<{ id: string; teacher_id: string; kind: string; content: string; created_at: string }>> {
  if (!sql) return [];
  await ensureSocialTables();
  return (await sql`
    SELECT id::text, teacher_id, kind, content, created_at::text
    FROM teacher_notes
    WHERE student_id = ${studentId}
    ORDER BY created_at DESC
    LIMIT ${limit}
  `) as Array<{ id: string; teacher_id: string; kind: string; content: string; created_at: string }>;
}

export async function writeTeacherAudit(input: {
  teacherId: string;
  studentId: string;
  action: string;
  reason?: string | null;
  payload?: Record<string, unknown>;
}): Promise<void> {
  if (!sql) return;
  await ensureSocialTables();
  await sql`
    INSERT INTO teacher_audit_log (teacher_id, student_id, action, reason, payload)
    VALUES (
      ${input.teacherId},
      ${input.studentId},
      ${input.action},
      ${input.reason ?? null},
      ${JSON.stringify(input.payload ?? {})}::jsonb
    )
  `;
}

export function toSocialRole(role: AppRole | string | undefined): SocialRole {
  return role === 'educator' ? 'educator' : 'learner';
}

/**
 * Notify linked teacher (and student) when the active weekly gate is overdue.
 * Dedupes per (learner, week) for 7 days.
 */
export async function maybeNotifyWeeklyGateDue(input: {
  learnerId: string;
  weekId: string;
  weekNumber: number;
  quizDueAt: string;
}): Promise<void> {
  if (!sql) return;
  const dueMs = new Date(input.quizDueAt).getTime();
  if (Number.isNaN(dueMs) || Date.now() < dueMs) return;

  await ensureSocialTables();
  const teacher = await getAcceptedTeacherForStudent(input.learnerId);
  if (!teacher) return;

  const existing = (await sql`
    SELECT 1 FROM notifications
    WHERE user_id = ${teacher.clerk_user_id}
      AND kind = 'weekly_gate_due'
      AND payload->>'week_id' = ${input.weekId}
      AND created_at > NOW() - INTERVAL '7 days'
    LIMIT 1
  `) as unknown[];
  if (existing.length > 0) return;

  const student = await getAppUser(input.learnerId);
  const name = student
    ? `${student.real_name} (@${student.username})`
    : input.learnerId;

  await createNotification({
    userId: teacher.clerk_user_id,
    kind: 'weekly_gate_due',
    title: 'שער שבועי באיחור / Weekly gate overdue',
    body: `${name} — שבוע ${input.weekNumber}`,
    payload: {
      student_id: input.learnerId,
      week_id: input.weekId,
      week_number: input.weekNumber,
    },
    href: `/educator/students/${input.learnerId}`,
  });

  await createNotification({
    userId: input.learnerId,
    kind: 'weekly_gate_due',
    title: 'השער השבועי באיחור / Weekly gate overdue',
    body: `שבוע ${input.weekNumber} — הגיע הזמן לבצע את המבחן השבועי.`,
    payload: {
      week_id: input.weekId,
      week_number: input.weekNumber,
    },
    href: '/app/quiz',
  });
}
