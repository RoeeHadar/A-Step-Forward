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
    <header className="sticky top-0 z-40 border-b border-white/[0.06] bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        {/* Brand */}
        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-lg font-semibold tracking-tight text-foreground transition-opacity hover:opacity-80"
          >
            <span className="text-violet-500" aria-hidden>◆</span>
            A Step Forward
          </Link>

          {/* Desktop nav — only shown when signed in */}
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
                    'rounded-md px-3 py-2 text-sm transition-colors hover:text-foreground',
                    pathname === link.href || pathname.startsWith(link.href + '/')
                      ? 'border-b-2 border-violet-500 font-medium text-foreground'
                      : 'text-muted-foreground',
                  )}
                >
                  {messages.nav[link.labelKey]}
                </Link>
              ))}
            </nav>
          </SignedIn>
        </div>

        {/* Right-side controls */}
        <div className="flex items-center gap-2">
          {/* Locale switcher */}
          <label className="sr-only" htmlFor="locale-select">
            {messages.common.language}
          </label>
          <div className="relative flex items-center">
            <Globe
              className="pointer-events-none absolute start-2 h-4 w-4 text-muted-foreground"
              aria-hidden
            />
            <select
              id="locale-select"
              value={locale}
              onChange={(e) => setLocale(e.target.value as Locale)}
              className="h-9 rounded-md border border-white/[0.08] bg-background/60 ps-8 pe-2 text-sm text-muted-foreground backdrop-blur-sm transition-colors hover:border-white/20 hover:text-foreground"
              aria-label={messages.common.selectLanguage}
            >
              {locales.map((l) => (
                <option key={l} value={l}>
                  {localeNames[l]}
                </option>
              ))}
            </select>
          </div>

          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={messages.common.toggleTheme}
            className="text-muted-foreground hover:text-foreground"
          >
            {resolved === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>

          {/* Auth buttons */}
          <SignedOut>
            <SignInButton mode="modal">
              <Button variant="ghost" size="sm" className="text-sm text-muted-foreground hover:text-foreground">
                {messages.nav.signIn}
              </Button>
            </SignInButton>
            <Link
              href="/sign-up"
              className="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-violet-600 to-violet-700 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-violet-500/20 transition-all hover:from-violet-500 hover:to-violet-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
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
