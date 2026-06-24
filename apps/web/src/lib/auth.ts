import 'server-only';

import { auth, currentUser } from '@clerk/nextjs/server';

export type AppRole = 'learner' | 'educator' | 'admin' | 'parent';

export interface AuthContext {
  userId: string;
  learnerId: string;
  role: AppRole;
  displayName: string;
}

export async function getAuthContext(): Promise<AuthContext | null> {
  const { userId } = await auth();
  if (!userId) return null;

  const user = await currentUser();
  const role = (user?.publicMetadata?.role as AppRole | undefined) ?? 'learner';
  const displayName =
    user?.firstName ?? user?.username ?? user?.emailAddresses?.[0]?.emailAddress ?? 'Learner';

  return {
    userId,
    learnerId: userId,
    role,
    displayName,
  };
}

export function requireRole(ctx: AuthContext, allowed: AppRole[]): void {
  if (!allowed.includes(ctx.role)) {
    throw new Error(`Forbidden: role ${ctx.role} not in [${allowed.join(', ')}]`);
  }
}
