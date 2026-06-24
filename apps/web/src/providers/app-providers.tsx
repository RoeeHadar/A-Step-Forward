'use client';

import { ClerkProvider } from '@clerk/nextjs';
import { enUS, heIL } from '@clerk/localizations';
import { dark } from '@clerk/themes';
import { ThemeProvider } from './theme-provider';
import { QueryProvider } from './query-provider';
import { I18nProvider, useI18n } from './i18n-provider';
import type { Locale } from '@/i18n/config';

const clerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ?? '';
const clerkReady = clerkKey.startsWith('pk_test_') || clerkKey.startsWith('pk_live_') ? clerkKey !== 'pk_test_REPLACE_ME' : false;

function WithClerk({ children }: { children: React.ReactNode }) {
  const { locale } = useI18n();
  if (!clerkReady) return <>{children}</>;
  return (
    <ClerkProvider
      key={locale}
      publishableKey={clerkKey}
      // Clerk @clerk/localizations types differ slightly from @clerk/nextjs DeepPartial wrapper
      localization={(locale === 'he' ? heIL : enUS) as never}
      appearance={{ baseTheme: dark, variables: { colorPrimary: 'hsl(221 83% 53%)' } }}
    >
      {children}
    </ClerkProvider>
  );
}

export function AppProviders({ children, initialLocale }: { children: React.ReactNode; initialLocale: Locale }) {
  return (
    <ThemeProvider>
      <QueryProvider>
        <I18nProvider initialLocale={initialLocale}>
          <WithClerk>{children}</WithClerk>
        </I18nProvider>
      </QueryProvider>
    </ThemeProvider>
  );
}
