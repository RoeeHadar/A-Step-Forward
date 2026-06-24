'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';
import { Moon, Sun, Globe } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import { useTheme } from '@/providers/theme-provider';
import { useI18n } from '@/providers/i18n-provider';
import { locales, localeNames, type Locale } from '@/i18n/config';

const navLinks = [
  { href: '/app', labelKey: 'dashboard' as const },
  { href: '/app/progress', labelKey: 'progress' as const },
  { href: '/app/memory', labelKey: 'memory' as const },
];

export function SiteHeader() {
  const pathname = usePathname();
  const { resolved, setTheme } = useTheme();
  const { messages, locale, setLocale } = useI18n();
  const toggleTheme = () => setTheme(resolved === 'dark' ? 'light' : 'dark');

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-lg font-semibold tracking-tight">
            A Step Forward
          </Link>
          <SignedIn>
            <nav className="hidden items-center gap-1 md:flex" aria-label={messages.common.mainNavigation}>
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'rounded-md px-3 py-2 text-sm transition-colors hover:bg-muted',
                    pathname === link.href || pathname.startsWith(link.href + '/')
                      ? 'bg-muted font-medium'
                      : 'text-muted-foreground',
                  )}
                >
                  {messages.nav[link.labelKey]}
                </Link>
              ))}
            </nav>
          </SignedIn>
        </div>
        <div className="flex items-center gap-2">
          <label className="sr-only" htmlFor="locale-select">
            {messages.common.language}
          </label>
          <div className="relative flex items-center">
            <Globe className="pointer-events-none absolute start-2 h-4 w-4 text-muted-foreground" aria-hidden />
            <select
              id="locale-select"
              value={locale}
              onChange={(e) => setLocale(e.target.value as Locale)}
              className="h-9 rounded-md border border-border bg-background ps-8 pe-2 text-sm"
              aria-label={messages.common.selectLanguage}
            >
              {locales.map((l) => (
                <option key={l} value={l}>
                  {localeNames[l]}
                </option>
              ))}
            </select>
          </div>
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label={messages.common.toggleTheme}>
            {resolved === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <SignedOut>
            <SignInButton mode="modal">
              <Button variant="ghost" size="sm">
                {messages.nav.signIn}
              </Button>
            </SignInButton>
            <Button asChild size="sm">
              <Link href="/sign-up">{messages.nav.signUp}</Link>
            </Button>
          </SignedOut>
          <SignedIn>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
        </div>
      </div>
    </header>
  );
}
