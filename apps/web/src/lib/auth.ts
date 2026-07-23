import 'server-only';

import { auth, clerkClient, currentUser } from '@clerk/nextjs/server';
import { getAppUser, toSocialRole, type SocialRole } from '@/lib/social-db';

export type AppRole = 'learner' | 'educator' | 'admin' | 'parent';

export interface AuthContext {
  userId: string;
  learnerId: string;
  role: AppRole;
  displayName: string;
  socialRole: SocialRole | null;
  username: string | null;
  realName: string | null;
}

export async function getAuthContext(): Promise<AuthContext | null> {
  const { userId } = await auth();
  if (!userId) return null;

  const user = await currentUser();
  const metaRole = (user?.publicMetadata?.role as AppRole | undefined) ?? 'learner';
  const appUser = await getAppUser(userId).catch(() => null);
  // Clerk publicMetadata.role=admin must win over Neon app_users (e.g. educator
  // from identity setup). Otherwise admins look like educators and lose /admin +
  // booking-guard behavior.
  const role: AppRole =
    metaRole === 'admin' || metaRole === 'parent'
      ? metaRole
      : appUser?.role === 'educator' || metaRole === 'educator'
        ? 'educator'
        : 'learner';

  const displayName =
    appUser?.real_name ??
    user?.firstName ??
    user?.username ??
    user?.emailAddresses?.[0]?.emailAddress ??
    'Learner';

  return {
    userId,
    learnerId: userId,
    role,
    displayName,
    socialRole: appUser ? toSocialRole(appUser.role) : null,
    username: appUser?.username ?? null,
    realName: appUser?.real_name ?? null,
  };
}

export function requireRole(ctx: AuthContext, allowed: AppRole[]): void {
  if (!allowed.includes(ctx.role)) {
    throw new Error(`Forbidden: role ${ctx.role} not in [${allowed.join(', ')}]`);
  }
}

/** Best-effort sync of Clerk publicMetadata.role with app_users. */
export async function syncClerkRole(userId: string, role: SocialRole): Promise<void> {
  try {
    const existing = await clerkClient.users.getUser(userId);
    if ((existing.publicMetadata?.role as string | undefined) === 'admin') {
      // Never demote an admin via social/identity sync.
      return;
    }
    // Clerk session JWT may lag; Neon app_users is authoritative for routing.
    await clerkClient.users.updateUserMetadata(userId, {
      publicMetadata: { role },
    });
  } catch (err) {
    console.warn('[auth] syncClerkRole failed', err);
  }
}
