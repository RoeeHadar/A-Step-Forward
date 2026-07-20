import { Suspense } from 'react';
import { redirect } from 'next/navigation';
import { IdentitySetupForm } from '@/components/identity-setup-form';
import { SiteHeader } from '@/components/site-header';
import { getAuthContext } from '@/lib/auth';
import { getAppUser } from '@/lib/social-db';

export const dynamic = 'force-dynamic';

export default async function IdentityPage() {
  const auth = await getAuthContext();
  if (!auth) redirect('/sign-in');

  const existing = await getAppUser(auth.userId).catch(() => null);
  if (existing?.profile_complete) {
    redirect(existing.role === 'educator' ? '/educator' : '/app');
  }

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="flex flex-1 items-start justify-center px-4 py-12">
        <Suspense fallback={null}>
          <IdentitySetupForm
            initialRole={existing?.role === 'educator' ? 'educator' : 'learner'}
            lockedRole={Boolean(existing?.role)}
          />
        </Suspense>
      </main>
    </div>
  );
}
