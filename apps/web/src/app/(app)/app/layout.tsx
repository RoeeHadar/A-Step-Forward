import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { AppSidebar } from '@/components/app-sidebar';
import { SiteHeader } from '@/components/site-header';

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <div className="flex flex-1">
        <AppSidebar />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
