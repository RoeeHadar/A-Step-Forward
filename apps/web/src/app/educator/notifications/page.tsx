import { redirect } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { NotificationsPageClient } from '@/components/notifications-page-client';
import { getAuthContext, requireRole } from '@/lib/auth';
import { ensureIdentityComplete } from '@/lib/identity-gate';

export const dynamic = 'force-dynamic';

export default async function EducatorNotificationsPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');
  await ensureIdentityComplete(auth.userId, '/educator/notifications');
  try {
    requireRole(auth, ['educator', 'admin']);
  } catch {
    redirect('/app/notifications');
  }

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-6">
        <NotificationsPageClient />
      </main>
    </div>
  );
}
