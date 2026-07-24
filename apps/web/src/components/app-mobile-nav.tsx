'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu } from 'lucide-react';
import { cn } from '@asf/ui';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@asf/ui/dialog';
import { useI18n } from '@/providers/i18n-provider';
import { agentAccentVars } from '@/lib/design-tokens';
import {
  APP_MOBILE_PRIMARY_NAV,
  appMobileMoreNavItems,
  isAppNavItemActive,
  type AppNavItem,
} from '@/lib/app-nav-items';

function NavLink({
  item,
  pathname,
  label,
  onNavigate,
  compact = false,
}: {
  item: AppNavItem;
  pathname: string;
  label: string;
  onNavigate?: () => void;
  compact?: boolean;
}) {
  const active = isAppNavItemActive(pathname, item);
  const Icon = item.icon;
  const isChat = item.labelKey === 'chat';
  const chatAgentSlug = pathname.startsWith('/app/chat/')
    ? (pathname.split('/')[3] ?? 'tutor')
    : null;
  const accentStyle =
    isChat && active && chatAgentSlug ? agentAccentVars(chatAgentSlug) : undefined;

  if (compact) {
    return (
      <Link
        href={item.href}
        onClick={onNavigate}
        aria-current={active ? 'page' : undefined}
        className={cn(
          'relative flex min-h-11 min-w-0 flex-1 flex-col items-center justify-center gap-1 px-1 py-1.5 text-[10px] font-medium transition-colors',
          active ? 'text-foreground' : 'text-muted-foreground hover:text-foreground',
        )}
      >
        {active ? (
          <span
            className="absolute inset-x-2 top-0 h-0.5 rounded-full"
            style={{
              ...accentStyle,
              backgroundColor:
                isChat && chatAgentSlug ? 'var(--agent-accent)' : 'hsl(var(--primary))',
            }}
            aria-hidden
          />
        ) : null}
        <Icon
          className={cn(
            'h-5 w-5 shrink-0',
            active
              ? isChat && chatAgentSlug
                ? undefined
                : 'text-primary'
              : 'text-muted-foreground',
          )}
          style={
            active && isChat && chatAgentSlug ? { color: 'var(--agent-accent)' } : undefined
          }
          aria-hidden
        />
        <span className="truncate">{label}</span>
      </Link>
    );
  }

  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? 'page' : undefined}
      className={cn(
        'relative flex min-h-11 items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors',
        active
          ? 'font-semibold text-foreground'
          : 'text-muted-foreground hover:bg-surface-2/60 hover:text-foreground',
      )}
    >
      {active ? (
        <span
          className="absolute inset-y-2 start-0 w-0.5 rounded-full"
          style={{
            ...accentStyle,
            backgroundColor:
              isChat && chatAgentSlug ? 'var(--agent-accent)' : 'hsl(var(--primary))',
          }}
          aria-hidden
        />
      ) : null}
      <Icon
        className={cn(
          'h-4 w-4 shrink-0',
          active
            ? isChat && chatAgentSlug
              ? undefined
              : 'text-primary'
            : 'text-muted-foreground',
        )}
        style={active && isChat && chatAgentSlug ? { color: 'var(--agent-accent)' } : undefined}
        aria-hidden
      />
      {label}
    </Link>
  );
}

export function AppMobileNav() {
  const pathname = usePathname();
  const { messages, locale } = useI18n();
  const [moreOpen, setMoreOpen] = useState(false);
  const moreItems = appMobileMoreNavItems();
  const moreActive = moreItems.some((item) => isAppNavItemActive(pathname, item));
  const moreLabel = locale === 'he' ? 'עוד' : 'More';

  return (
    <>
      <nav
        className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background/95 backdrop-blur-xl md:hidden"
        aria-label={messages.common.appNavigation}
      >
        <div className="mx-auto flex max-w-lg items-stretch justify-around px-1 pb-[max(0.25rem,env(safe-area-inset-bottom))] pt-1">
          {APP_MOBILE_PRIMARY_NAV.map((item) => (
            <NavLink
              key={item.href}
              item={item}
              pathname={pathname}
              label={messages.nav[item.labelKey]}
              compact
            />
          ))}
          <button
            type="button"
            onClick={() => setMoreOpen(true)}
            aria-expanded={moreOpen}
            aria-haspopup="dialog"
            className={cn(
              'relative flex min-h-11 min-w-0 flex-1 flex-col items-center justify-center gap-1 px-1 py-1.5 text-[10px] font-medium transition-colors',
              moreActive || moreOpen
                ? 'text-foreground'
                : 'text-muted-foreground hover:text-foreground',
            )}
          >
            {moreActive && !moreOpen ? (
              <span
                className="absolute inset-x-2 top-0 h-0.5 rounded-full bg-primary"
                aria-hidden
              />
            ) : null}
            <Menu className="h-5 w-5 shrink-0" aria-hidden />
            <span className="truncate">{moreLabel}</span>
          </button>
        </div>
      </nav>

      <Dialog open={moreOpen} onOpenChange={setMoreOpen}>
        <DialogContent className="fixed inset-x-0 bottom-0 top-auto max-h-[min(70vh,32rem)] w-full max-w-none translate-x-0 translate-y-0 rounded-b-none rounded-t-2xl border-border p-0 sm:max-w-lg sm:translate-x-[-50%] sm:rounded-lg">
          <DialogHeader className="border-b border-border px-4 py-4 text-start">
            <DialogTitle>{messages.common.appNavigation}</DialogTitle>
          </DialogHeader>
          <nav
            className="flex max-h-[calc(min(70vh,32rem)-4.5rem)] flex-col gap-1 overflow-y-auto p-3"
            aria-label={messages.common.appNavigation}
          >
            {moreItems.map((item) => (
              <NavLink
                key={item.href}
                item={item}
                pathname={pathname}
                label={messages.nav[item.labelKey]}
                onNavigate={() => setMoreOpen(false)}
              />
            ))}
          </nav>
        </DialogContent>
      </Dialog>
    </>
  );
}
