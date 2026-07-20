'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { useI18n } from '@/providers/i18n-provider';

interface FriendUser {
  clerk_user_id: string;
  username: string;
  real_name: string;
  nickname: string | null;
}

interface Pending {
  id: string;
  from: FriendUser;
}

export function FriendsPageClient() {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const [friends, setFriends] = useState<FriendUser[]>([]);
  const [pending, setPending] = useState<Pending[]>([]);
  const [hits, setHits] = useState<FriendUser[]>([]);
  const [q, setQ] = useState('');
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const reload = useCallback((search = '') => {
    setLoading(true);
    const url = search.trim().length >= 2
      ? `/api/social/friend?q=${encodeURIComponent(search.trim())}`
      : '/api/social/friend';
    void fetch(url)
      .then((r) => r.json())
      .then((data: {
        friends?: FriendUser[];
        pending?: Pending[];
        results?: FriendUser[];
        error?: string;
      }) => {
        if (data.error) {
          setMsg(data.error);
          return;
        }
        setFriends(data.friends ?? []);
        setPending(data.pending ?? []);
        setHits(data.results ?? []);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  async function invite(username: string) {
    setMsg(null);
    const res = await fetch('/api/social/friend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username }),
    });
    const data = (await res.json()) as { error?: string };
    setMsg(res.ok ? (isHe ? 'הבקשה נשלחה' : 'Request sent') : data.error ?? 'Failed');
    if (res.ok) reload(q);
  }

  async function respond(friendshipId: string, accept: boolean) {
    setMsg(null);
    const res = await fetch('/api/social/friend/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ friendship_id: friendshipId, accept }),
    });
    if (!res.ok) {
      const data = (await res.json().catch(() => ({}))) as { code?: string; error?: string };
      setMsg(
        data.code === 'internal' || res.status >= 500
          ? isHe
            ? 'שגיאה פנימית. נסו שוב בעוד רגע.'
            : 'Internal error. Please try again in a moment.'
          : isHe
            ? 'לא הצלחנו לטפל בבקשה. נסו שוב.'
            : data.error || 'Could not process this request.',
      );
      return;
    }
    reload(q);
  }

  function displayName(u: FriendUser) {
    return u.real_name;
  }

  return (
    <div className="space-y-8" dir={isHe ? 'rtl' : 'ltr'}>
      <header>
        <h1 className="font-display text-2xl font-bold">
          {isHe ? 'חברים' : 'Friends'}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {isHe
            ? 'חפשו לפי שם משתמש או שם מלא. בפרופיל רואים התקדמות כללית בלבד.'
            : 'Search by username or real name. Profiles show high-level progress only.'}
        </p>
      </header>

      <section className="space-y-3 rounded-2xl border border-border p-5">
        <h2 className="font-semibold">{isHe ? 'הוסף חבר/ה' : 'Add a friend'}</h2>
        <div className="flex flex-wrap gap-2">
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={isHe ? 'שם משתמש או שם מלא' : 'Username or real name'}
            className="max-w-sm"
          />
          <Button type="button" onClick={() => reload(q)}>
            {isHe ? 'חיפוש' : 'Search'}
          </Button>
        </div>
        {hits.length > 0 ? (
          <ul className="space-y-2">
            {hits.map((h) => (
              <li
                key={h.clerk_user_id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-sm"
              >
                <Link href={`/u/${h.username}`} className="hover:underline">
                  {displayName(h)}{' '}
                  <span className="font-mono text-muted-foreground">@{h.username}</span>
                </Link>
                <Button type="button" size="sm" onClick={() => void invite(h.username)}>
                  {isHe ? 'שלח בקשה' : 'Add'}
                </Button>
              </li>
            ))}
          </ul>
        ) : null}
        {msg ? <p className="text-sm text-muted-foreground">{msg}</p> : null}
      </section>

      {pending.length > 0 ? (
        <section className="space-y-3">
          <h2 className="font-semibold">{isHe ? 'בקשות ממתינות' : 'Pending requests'}</h2>
          <ul className="space-y-2">
            {pending.map((p) => (
              <li
                key={p.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border px-3 py-2 text-sm"
              >
                <span>
                  {displayName(p.from)}{' '}
                  <span className="font-mono text-muted-foreground">@{p.from.username}</span>
                </span>
                <div className="flex gap-2">
                  <Button type="button" size="sm" onClick={() => void respond(p.id, true)}>
                    {isHe ? 'אשר' : 'Accept'}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => void respond(p.id, false)}
                  >
                    {isHe ? 'דחה' : 'Decline'}
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="space-y-3">
        <h2 className="font-semibold">
          {isHe ? `הרשימה שלי (${friends.length})` : `My friends (${friends.length})`}
        </h2>
        {loading ? (
          <p className="text-sm text-muted-foreground">{isHe ? 'טוען…' : 'Loading…'}</p>
        ) : friends.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            {isHe ? 'עדיין אין חברים.' : 'No friends yet.'}
          </p>
        ) : (
          <ul className="grid gap-3 sm:grid-cols-2">
            {friends.map((f) => (
              <li key={f.clerk_user_id}>
                <Link
                  href={`/u/${f.username}`}
                  className="block rounded-xl border border-border bg-card px-4 py-3 transition hover:border-primary/40"
                >
                  <p className="font-medium">{displayName(f)}</p>
                  <p className="font-mono text-xs text-muted-foreground">@{f.username}</p>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
