'use client';

import { useCallback, useEffect, useId, useRef, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Bell } from 'lucide-react';
import { cn } from '@asf/ui';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';

interface Notif {
  id: string;
  kind: string;
  title: string;
  body: string;
  href: string | null;
  read_at: string | null;
  created_at: string;
  payload: Record<string, unknown>;
}

export function NotificationsBell() {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const router = useRouter();
  const pathname = usePathname();
  const panelId = useId();
  const rootRef = useRef<HTMLDivElement>(null);

  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<Notif[]>([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);

  const archiveHref = pathname.startsWith('/educator')
    ? '/educator/notifications'
    : '/app/notifications';

  const reload = useCallback(() => {
    setLoading(true);
    void fetch('/api/notifications')
      .then((r) => (r.ok ? r.json() : null))
      .then((data: { items?: Notif[]; unread?: number } | null) => {
        if (!data) return;
        setItems(data.items ?? []);
        setUnread(typeof data.unread === 'number' ? data.unread : 0);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    reload();
    const id = window.setInterval(reload, 60_000);
    return () => window.clearInterval(id);
  }, [reload]);

  useEffect(() => {
    if (!open) return;
    reload();
    function onDoc(e: MouseEvent) {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('mousedown', onDoc);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDoc);
      document.removeEventListener('keydown', onKey);
    };
  }, [open, reload]);

  async function markOne(id: string) {
    await fetch('/api/notifications', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id }),
    });
  }

  async function markAll() {
    await fetch('/api/notifications', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ all: true }),
    });
    reload();
  }

  async function openNotification(n: Notif) {
    if (!n.read_at) await markOne(n.id);
    setOpen(false);
    if (n.href) {
      router.push(n.href);
    } else {
      reload();
    }
  }

  async function respondTeacher(linkId: string, accept: boolean, notifId: string) {
    await fetch('/api/social/teacher-invite/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ link_id: linkId, accept }),
    });
    await markOne(notifId);
    reload();
  }

  async function respondFriend(friendshipId: string, accept: boolean, notifId: string) {
    await fetch('/api/social/friend/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ friendship_id: friendshipId, accept }),
    });
    await markOne(notifId);
    reload();
  }

  return (
    <div ref={rootRef} className="relative" dir={isHe ? 'rtl' : 'ltr'}>
      <button
        type="button"
        className={cn(
          'relative inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-surface-2/60 hover:text-foreground',
          open && 'bg-surface-2/60 text-foreground',
        )}
        aria-label={isHe ? 'התראות' : 'Notifications'}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
      >
        <Bell className="h-4 w-4" aria-hidden />
        {unread > 0 ? (
          <span className="absolute -end-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground">
            {unread > 9 ? '9+' : unread}
          </span>
        ) : null}
      </button>

      {open ? (
        <div
          id={panelId}
          role="dialog"
          aria-label={isHe ? 'התראות' : 'Notifications'}
          className={cn(
            'absolute top-full z-50 mt-2 w-[min(22rem,calc(100vw-1.5rem))] overflow-hidden rounded-xl border border-border bg-background shadow-lg',
            isHe ? 'start-0 sm:start-auto sm:end-0' : 'end-0',
          )}
        >
          <div className="flex items-center justify-between gap-2 border-b border-border px-3 py-2">
            <p className="text-sm font-semibold">{isHe ? 'התראות' : 'Notifications'}</p>
            <Button type="button" variant="ghost" size="sm" className="h-7 text-xs" onClick={() => void markAll()}>
              {isHe ? 'סמן הכל כנקרא' : 'Mark all read'}
            </Button>
          </div>

          <div className="max-h-[min(24rem,70vh)] overflow-y-auto">
            {loading && items.length === 0 ? (
              <p className="px-3 py-6 text-center text-sm text-muted-foreground">
                {isHe ? 'טוען…' : 'Loading…'}
              </p>
            ) : items.length === 0 ? (
              <p className="px-3 py-6 text-center text-sm text-muted-foreground">
                {isHe ? 'אין התראות עדיין.' : 'No notifications yet.'}
              </p>
            ) : (
              <ul>
                {items.map((n) => {
                  const unreadItem = !n.read_at;
                  const isActionable =
                    (n.kind === 'teacher_invite' && typeof n.payload.link_id === 'string') ||
                    (n.kind === 'friend_request' && typeof n.payload.friendship_id === 'string');

                  return (
                    <li key={n.id} className="border-b border-border/60 last:border-b-0">
                      <button
                        type="button"
                        className={cn(
                          'w-full px-3 py-2.5 text-start transition-colors',
                          unreadItem
                            ? 'bg-primary/10 hover:bg-primary/15'
                            : 'bg-muted/30 text-muted-foreground hover:bg-muted/50',
                        )}
                        onClick={() => {
                          if (isActionable) return;
                          void openNotification(n);
                        }}
                      >
                        <p className={cn('text-sm', unreadItem ? 'font-semibold text-foreground' : 'font-medium')}>
                          {n.title}
                        </p>
                        {n.body ? (
                          <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">{n.body}</p>
                        ) : null}
                        <p className="mt-1 text-[10px] text-muted-foreground">
                          {new Date(n.created_at).toLocaleString(isHe ? 'he-IL' : 'en-US')}
                        </p>
                      </button>

                      {n.kind === 'teacher_invite' && typeof n.payload.link_id === 'string' ? (
                        <div className="flex gap-2 px-3 pb-2.5">
                          <Button
                            type="button"
                            size="sm"
                            className="h-7"
                            onClick={() => void respondTeacher(String(n.payload.link_id), true, n.id)}
                          >
                            {isHe ? 'אשר' : 'Accept'}
                          </Button>
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            className="h-7"
                            onClick={() => void respondTeacher(String(n.payload.link_id), false, n.id)}
                          >
                            {isHe ? 'דחה' : 'Decline'}
                          </Button>
                        </div>
                      ) : null}

                      {n.kind === 'friend_request' && typeof n.payload.friendship_id === 'string' ? (
                        <div className="flex gap-2 px-3 pb-2.5">
                          <Button
                            type="button"
                            size="sm"
                            className="h-7"
                            onClick={() => void respondFriend(String(n.payload.friendship_id), true, n.id)}
                          >
                            {isHe ? 'אשר' : 'Accept'}
                          </Button>
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            className="h-7"
                            onClick={() => void respondFriend(String(n.payload.friendship_id), false, n.id)}
                          >
                            {isHe ? 'דחה' : 'Decline'}
                          </Button>
                        </div>
                      ) : null}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div className="border-t border-border px-3 py-2">
            <button
              type="button"
              className="w-full text-center text-xs font-medium text-primary hover:underline"
              onClick={() => {
                setOpen(false);
                router.push(archiveHref);
              }}
            >
              {isHe ? 'כל ההתראות' : 'View all'}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
