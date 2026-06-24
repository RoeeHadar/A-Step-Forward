'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';
import { Moon, Sun } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import { useTheme } from '@/providers/theme-provider';
import { useI18n } from '@/providers/i18n-provider';
import type { Locale } from '@/i18n/config';

const navLinks = [
  { href: '/app', labelKey: 'dashboard' as const },
  { href: '/app/progress', labelKey: 'progress' as const },
  { href: '/app/memory', labelKey: 'memory' as const },
];

const localeToggleLabel: Record<Locale, string> = {
  he: 'EN',
  en: 'עב',
};

export function SiteHeader() {
  const pathname = usePathname();
  const { resolved, setTheme } = useTheme();
  const { messages, locale, setLocale } = useI18n();
  const toggleTheme = () => setTheme(resolved === 'dark' ? 'light' : 'dark');
  const otherLocale: Locale = locale === 'he' ? 'en' : 'he';

  const isActive = (href: string) =>
    pathname === href || (href !== '/' && pathname.startsWith(href + '/'));

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/70 backdrop-blur-xl backdrop-saturate-150">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        {/* Brand */}
        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="flex items-center gap-2 transition-opacity hover:opacity-80"
          >
            <div
              className="h-2 w-2 rounded-full bg-gradient-to-br from-primary via-accent-magenta to-accent-cyan shadow-lg shadow-primary/50"
              aria-hidden
            />
            <span className="font-display text-base font-bold tracking-tight text-foreground">
              A Step Forward
            </span>
          </Link>

          <SignedIn>
            <nav
              className="hidden items-center gap-1 md:flex"
              aria-label={messages.common.mainNavigation}
            >
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'relative px-3 py-2 text-sm transition-colors hover:text-foreground',
                    isActive(link.href) ? 'font-medium text-foreground' : 'text-muted-foreground',
                  )}
                >
                  {messages.nav[link.labelKey]}
                  {isActive(link.href) && (
                    <span
                      className="absolute inset-x-3 -bottom-[13px] h-0.5 rounded-full bg-primary"
                      aria-hidden
                    />
                  )}
                </Link>
              ))}
            </nav>
          </SignedIn>
        </div>

        {/* Right-side controls */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setLocale(otherLocale)}
            className="h-8 min-w-8 px-2 text-xs font-semibold text-muted-foreground hover:text-foreground"
            aria-label={messages.common.selectLanguage}
          >
            {localeToggleLabel[locale]}
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={messages.common.toggleTheme}
            className="text-muted-foreground hover:text-foreground"
          >
            {resolved === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          <SignedOut>
            <SignInButton mode="modal">
              <Button
                variant="ghost"
                size="sm"
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                {messages.nav.signIn}
              </Button>
            </SignInButton>
            <Link
              href="/sign-up"
              className="inline-flex items-center rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground shadow-sm shadow-primary/20 transition-all hover:shadow-primary/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {messages.nav.signUp}
            </Link>
          </SignedOut>

          <SignedIn>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
        </div>
      </div>
    </header>
  );
}
