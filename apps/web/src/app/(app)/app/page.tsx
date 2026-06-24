import { redirect } from 'next/navigation';
import { DashboardContent } from '@/components/dashboard-content';
import { getAuthContext } from '@/lib/auth';
import { fetchDashboard } from '@/lib/data';

export default async function DashboardPage() {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  const dashboard = await fetchDashboard(auth);

  return <DashboardContent displayName={auth.displayName} dashboard={dashboard} />;
}
