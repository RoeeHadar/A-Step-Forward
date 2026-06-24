'use client';

import { ClerkProvider } from '@clerk/nextjs';
import { dark } from '@clerk/themes';
import { ThemeProvider } from './theme-provider';
import { QueryProvider } from './query-provider';
import { I18nProvider } from './i18n-provider';

const clerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ?? '';
const clerkReady = clerkKey.startsWith('pk_test_') || clerkKey.startsWith('pk_live_')
  ? clerkKey !== 'pk_test_REPLACE_ME'
  : false;

function WithClerk({ children }: { children: React.ReactNode }) {
  if (!clerkReady) return <>{children}</>;
  return (
    <ClerkProvider
      publishableKey={clerkKey}
      appearance={{
        baseTheme: dark,
        variables: { colorPrimary: 'hsl(221 83% 53%)' },
      }}
    >
      {children}
    </ClerkProvider>
  );
}

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <WithClerk>
      <ThemeProvider>
        <QueryProvider>
          <I18nProvider>{children}</I18nProvider>
        </QueryProvider>
      </ThemeProvider>
    </WithClerk>
  );
}
