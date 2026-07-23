import { redirect } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { AdminBookingsClient } from '@/components/admin-bookings-client';
import { getAuthContext, requireRole } from '@/lib/auth';

export const dynamic = 'force-dynamic';

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

export default async function AdminBookingsPage({ searchParams }: Props) {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');
  try {
    requireRole(auth, ['admin']);
  } catch {
    redirect('/app');
  }

  const sp = await searchParams;
  const gcal = typeof sp.gcal === 'string' ? `gcal=${sp.gcal}` : null;
  const watch = typeof sp.watch === 'string' ? `&watch=${sp.watch}` : '';
  const gcalQuery = gcal ? `${gcal}${watch}` : null;

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl space-y-6 p-6">
        <AdminBookingsClient gcalQuery={gcalQuery} />
      </main>
    </div>
  );
}
