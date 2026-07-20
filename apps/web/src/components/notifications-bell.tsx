'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Bell } from 'lucide-react';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';

export function NotificationsBell({ href = '/app/notifications' }: { href?: string }) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const load = () => {
      void fetch('/api/notifications')
        .then((r) => (r.ok ? r.json() : null))
        .then((data: { unread?: number } | null) => {
          if (!cancelled && data && typeof data.unread === 'number') {
            setUnread(data.unread);
          }
        })
        .catch(() => undefined);
    };
    load();
    const id = window.setInterval(load, 60_000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  return (
    <Link
      href={href}
      className={cn(
        'relative inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-surface-2/60 hover:text-foreground',
      )}
      aria-label={isHe ? 'התראות' : 'Notifications'}
    >
      <Bell className="h-4 w-4" aria-hidden />
      {unread > 0 ? (
        <span className="absolute -end-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground">
          {unread > 9 ? '9+' : unread}
        </span>
      ) : null}
    </Link>
  );
}
