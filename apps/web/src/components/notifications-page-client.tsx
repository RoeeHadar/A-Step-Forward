'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
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

function linkIdOf(n: Notif): string | null {
  const v = n.payload?.link_id ?? n.payload?.linkId;
  return typeof v === 'string' && v.trim() ? v.trim() : null;
}

function friendshipIdOf(n: Notif): string | null {
  const v = n.payload?.friendship_id ?? n.payload?.friendshipId;
  return typeof v === 'string' && v.trim() ? v.trim() : null;
}

function isResolved(n: Notif): boolean {
  return n.payload?.resolved === true || n.kind.endsWith('_ack');
}

export function NotificationsPageClient() {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const [items, setItems] = useState<Notif[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    void fetch('/api/notifications')
      .then((r) => r.json())
      .then((data: { items?: Notif[] }) => {
        setItems(data.items ?? []);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  async function markAll() {
    await fetch('/api/notifications', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ all: true }),
    });
    reload();
  }

  async function markOne(id: string) {
    await fetch('/api/notifications', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id }),
    });
    reload();
  }

  async function respondTeacher(n: Notif, accept: boolean) {
    setError(null);
    setBusyId(n.id);
    try {
      const res = await fetch('/api/social/teacher-invite/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          link_id: linkIdOf(n) ?? undefined,
          notification_id: n.id,
          accept,
        }),
      });
      const data = (await res.json()) as { error?: string };
      if (!res.ok) {
        setError(data.error ?? (isHe ? 'הפעולה נכשלה' : 'Action failed'));
        return;
      }
      reload();
    } finally {
      setBusyId(null);
    }
  }

  async function respondFriend(n: Notif, accept: boolean) {
    setError(null);
    setBusyId(n.id);
    const friendshipId = friendshipIdOf(n);
    if (!friendshipId) {
      setError(isHe ? 'בקשה לא תקינה' : 'Invalid request');
      setBusyId(null);
      return;
    }
    try {
      const res = await fetch('/api/social/friend/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ friendship_id: friendshipId, accept }),
      });
      const data = (await res.json()) as { error?: string };
      if (!res.ok) {
        setError(data.error ?? (isHe ? 'הפעולה נכשלה' : 'Action failed'));
        return;
      }
      reload();
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-4" dir={isHe ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between gap-3">
        <h1 className="font-display text-2xl font-bold">
          {isHe ? 'התראות' : 'Notifications'}
        </h1>
        <Button type="button" variant="outline" size="sm" onClick={() => void markAll()}>
          {isHe ? 'סמן הכל כנקרא' : 'Mark all read'}
        </Button>
      </div>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      {loading ? (
        <p className="text-sm text-muted-foreground">{isHe ? 'טוען…' : 'Loading…'}</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {isHe ? 'אין התראות עדיין.' : 'No notifications yet.'}
        </p>
      ) : (
        <ul className="space-y-3">
          {items.map((n) => {
            const showTeacherActions = n.kind === 'teacher_invite' && !isResolved(n);
            const showFriendActions =
              n.kind === 'friend_request' && !isResolved(n) && Boolean(friendshipIdOf(n));
            return (
              <li
                key={n.id}
                className={`rounded-xl border px-4 py-3 ${
                  n.read_at ? 'border-border/50 bg-surface-1/20' : 'border-primary/30 bg-primary/5'
                }`}
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium">{n.title}</p>
                    {n.body ? (
                      <p className="mt-1 text-sm text-muted-foreground">{n.body}</p>
                    ) : null}
                    <p className="mt-1 text-xs text-muted-foreground">
                      {new Date(n.created_at).toLocaleString(isHe ? 'he-IL' : 'en-US')}
                    </p>
                  </div>
                  {!n.read_at ? (
                    <Button type="button" variant="ghost" size="sm" onClick={() => void markOne(n.id)}>
                      {isHe ? 'נקרא' : 'Read'}
                    </Button>
                  ) : null}
                </div>

                {showTeacherActions ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      disabled={busyId === n.id}
                      onClick={() => void respondTeacher(n, true)}
                    >
                      {isHe ? 'אשר' : 'Accept'}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={busyId === n.id}
                      onClick={() => void respondTeacher(n, false)}
                    >
                      {isHe ? 'דחה' : 'Decline'}
                    </Button>
                  </div>
                ) : null}

                {showFriendActions ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      disabled={busyId === n.id}
                      onClick={() => void respondFriend(n, true)}
                    >
                      {isHe ? 'אשר' : 'Accept'}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={busyId === n.id}
                      onClick={() => void respondFriend(n, false)}
                    >
                      {isHe ? 'דחה' : 'Decline'}
                    </Button>
                  </div>
                ) : null}

                {n.href && n.kind !== 'teacher_invite' && n.kind !== 'friend_request' ? (
                  <Link href={n.href} className="mt-2 inline-block text-sm text-primary hover:underline">
                    {isHe ? 'פתח' : 'Open'}
                  </Link>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
