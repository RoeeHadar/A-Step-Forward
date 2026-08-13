import { auth } from '@clerk/nextjs/server';
import { cn } from '@asf/ui';
import { AppSidebar } from '@/components/app-sidebar';
import { AppMobileNav } from '@/components/app-mobile-nav';
import { SiteHeader } from '@/components/site-header';
import { AmbientBackground } from '@/components/ambient-background';

/**
 * Public-or-signed-in chrome for routes that must stay reachable without
 * onboarding (`/learn`, week quiz, persona settings). Signed-in learners keep
 * the app sidebar + mobile bar; guests only get the site header.
 */
export async function OptionalAppShell({ children }: { children: React.ReactNode }) {
  const { userId } = await auth();
  const signedIn = Boolean(userId);

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <div className="flex flex-1">
        {signedIn ? <AppSidebar /> : null}
        <div
          className={cn(
            'relative isolate min-w-0 flex-1 overflow-x-hidden',
            signedIn && 'pb-[calc(4.5rem+env(safe-area-inset-bottom))] md:pb-0',
          )}
        >
          <AmbientBackground />
          {children}
        </div>
      </div>
      {signedIn ? <AppMobileNav /> : null}
    </div>
  );
}
