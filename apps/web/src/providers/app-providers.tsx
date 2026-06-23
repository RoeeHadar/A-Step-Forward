'use client';

import { ClerkProvider } from '@clerk/nextjs';
import { dark } from '@clerk/themes';
import { ThemeProvider } from './theme-provider';
import { QueryProvider } from './query-provider';
import { I18nProvider } from './i18n-provider';

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider
      appearance={{
        baseTheme: dark,
        variables: { colorPrimary: 'hsl(221 83% 53%)' },
      }}
    >
      <ThemeProvider>
        <QueryProvider>
          <I18nProvider>{children}</I18nProvider>
        </QueryProvider>
      </ThemeProvider>
    </ClerkProvider>
  );
}
