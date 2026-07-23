import { redirect } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { AdminDashboardClient } from '@/components/admin-dashboard-client';
import { getAuthContext, requireRole } from '@/lib/auth';
import { fetchAdminStats } from '@/lib/data';

export const dynamic = 'force-dynamic';

export default async function AdminPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  try {
    requireRole(auth, ['admin']);
  } catch {
    redirect('/app');
  }

  const stats = await fetchAdminStats(auth);

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl p-6">
        <AdminDashboardClient stats={stats} />
      </main>
    </div>
  );
}
