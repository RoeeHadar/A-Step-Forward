'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';
import { Moon, Sun, Sprout } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import { useTheme } from '@/providers/theme-provider';
import { useI18n } from '@/providers/i18n-provider';
import { useScrollY } from '@/hooks/use-scroll-y';
import { NotificationsBell } from '@/components/notifications-bell';
import type { Locale } from '@/i18n/config';

const publicNavLinks = [{ href: '/learn', labelKey: 'learn' as const }];

const appNavLinks = [
  { href: '/app', labelKey: 'dashboard' as const },
  { href: '/learn', labelKey: 'learn' as const },
  { href: '/app/progress', labelKey: 'progress' as const },
  { href: '/app/memory', labelKey: 'memory' as const },
];

const educatorNavLinks = [
  { href: '/educator', labelKey: 'roster' as const, exact: true },
  { href: '/educator/notifications', labelKey: 'notifications' as const },
  { href: '/educator/profile', labelKey: 'profile' as const },
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
  const isEducatorShell = pathname.startsWith('/educator');

  const isActive = (href: string, exact = false) => {
    if (exact) return pathname === href;
    return pathname === href || (href !== '/' && pathname.startsWith(`${href}/`));
  };

  const scrolled = useScrollY(8);

  const brandHref = isEducatorShell ? '/educator' : '/';

  return (
    <header
      className={cn(
        'sticky top-0 z-50 border-b backdrop-blur-xl backdrop-saturate-150 transition-[background-color,border-color,box-shadow] duration-300',
        scrolled
          ? 'border-border-bright bg-background/88 shadow-sm'
          : 'border-border/80 bg-background/70',
      )}
    >
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link
            href={brandHref}
            className="flex items-center gap-2 transition-opacity hover:opacity-80"
          >
            <span
              className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground shadow-sm"
              aria-hidden
            >
              <Sprout className="h-3.5 w-3.5" />
            </span>
            <span className="font-display text-lg font-semibold tracking-tight text-foreground">
              A Step Forward
            </span>
          </Link>

          <nav
            className="hidden items-center gap-1 md:flex"
            aria-label={messages.common.mainNavigation}
          >
            {isEducatorShell ? (
              educatorNavLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'relative px-3 py-2 text-sm transition-colors hover:text-foreground',
                    isActive(link.href, link.exact)
                      ? 'font-medium text-foreground'
                      : 'text-muted-foreground',
                  )}
                >
                  {messages.nav[link.labelKey]}
                  {isActive(link.href, link.exact) && (
                    <span
                      className="absolute inset-x-3 -bottom-[13px] h-0.5 rounded-full bg-primary"
                      aria-hidden
                    />
                  )}
                </Link>
              ))
            ) : (
              <>
                {publicNavLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={cn(
                      'relative px-3 py-2 text-sm transition-colors hover:text-foreground',
                      isActive(link.href)
                        ? 'font-medium text-foreground'
                        : 'text-muted-foreground',
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
                <SignedIn>
                  {appNavLinks
                    .filter((link) => !publicNavLinks.some((p) => p.href === link.href))
                    .map((link) => (
                      <Link
                        key={link.href}
                        href={link.href}
                        className={cn(
                          'relative px-3 py-2 text-sm transition-colors hover:text-foreground',
                          isActive(link.href)
                            ? 'font-medium text-foreground'
                            : 'text-muted-foreground',
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
                </SignedIn>
              </>
            )}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          {isEducatorShell ? (
            <Link
              href="/educator"
              className={cn(
                'inline-flex rounded-lg px-2.5 py-1.5 text-sm font-medium md:hidden',
                pathname === '/educator'
                  ? 'bg-primary/15 text-primary'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {messages.nav.roster}
            </Link>
          ) : (
            <Link
              href="/learn"
              className={cn(
                'inline-flex rounded-lg px-2.5 py-1.5 text-sm font-medium md:hidden',
                isActive('/learn')
                  ? 'bg-primary/15 text-primary'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {messages.nav.learn}
            </Link>
          )}
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
              className="inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-sm transition-all hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {messages.nav.signUp}
            </Link>
          </SignedOut>

          <SignedIn>
            <NotificationsBell />
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
        </div>
      </div>
    </header>
  );
}
