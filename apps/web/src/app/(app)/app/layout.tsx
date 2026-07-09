import { redirect } from 'next/navigation';
import { getAuthContext } from '@/lib/auth';
import { ensureOnboarded } from '@/lib/onboarding-gate';
import { AppSidebar } from '@/components/app-sidebar';
import { SiteHeader } from '@/components/site-header';
import { AmbientBackground } from '@/components/ambient-background';

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  let auth;
  try {
    auth = await getAuthContext();
  } catch {
    redirect('/sign-in');
  }
  if (!auth) redirect('/sign-in');

  await ensureOnboarded(auth.learnerId, '/app');

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <div className="flex flex-1">
        <AppSidebar />
        <main className="relative isolate flex-1 overflow-x-hidden">
          <AmbientBackground />
          <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:py-10">{children}</div>
        </main>
      </div>
    </div>
  );
}
