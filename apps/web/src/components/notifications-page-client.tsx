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

export function NotificationsPageClient() {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const [items, setItems] = useState<Notif[]>([]);
  const [loading, setLoading] = useState(true);

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

  async function respondTeacher(linkId: string, accept: boolean) {
    await fetch('/api/social/teacher-invite/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ link_id: linkId, accept }),
    });
    reload();
  }

  async function respondFriend(friendshipId: string, accept: boolean) {
    await fetch('/api/social/friend/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ friendship_id: friendshipId, accept }),
    });
    reload();
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

      {loading ? (
        <p className="text-sm text-muted-foreground">{isHe ? 'טוען…' : 'Loading…'}</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {isHe ? 'אין התראות עדיין.' : 'No notifications yet.'}
        </p>
      ) : (
        <ul className="space-y-3">
          {items.map((n) => (
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

              {n.kind === 'teacher_invite' && typeof n.payload.link_id === 'string' ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button
                    type="button"
                    size="sm"
                    onClick={() => void respondTeacher(String(n.payload.link_id), true)}
                  >
                    {isHe ? 'אשר' : 'Accept'}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => void respondTeacher(String(n.payload.link_id), false)}
                  >
                    {isHe ? 'דחה' : 'Decline'}
                  </Button>
                </div>
              ) : null}

              {n.kind === 'friend_request' && typeof n.payload.friendship_id === 'string' ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button
                    type="button"
                    size="sm"
                    onClick={() => void respondFriend(String(n.payload.friendship_id), true)}
                  >
                    {isHe ? 'אשר' : 'Accept'}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => void respondFriend(String(n.payload.friendship_id), false)}
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
          ))}
        </ul>
      )}
    </div>
  );
}
