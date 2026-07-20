'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { useI18n } from '@/providers/i18n-provider';

interface StudentRow {
  clerk_user_id: string;
  username: string;
  real_name: string;
  nickname: string | null;
  linked_at?: string;
}

interface SearchHit {
  clerk_user_id: string;
  username: string;
  real_name: string;
  goal?: string | null;
  plan_summary?: string | null;
}

export function EducatorStudentsClient({
  students,
  aboutMe,
}: {
  students: StudentRow[];
  aboutMe: string | null;
}) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const [q, setQ] = useState('');
  const [hits, setHits] = useState<SearchHit[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [about, setAbout] = useState(aboutMe ?? '');
  const [savingAbout, setSavingAbout] = useState(false);

  async function search() {
    setMsg(null);
    const res = await fetch(`/api/social/teacher-invite?q=${encodeURIComponent(q)}`);
    const data = (await res.json()) as { results?: SearchHit[]; error?: string };
    if (!res.ok) {
      setMsg(data.error ?? 'Search failed');
      return;
    }
    setHits(data.results ?? []);
  }

  async function invite(studentId: string) {
    setMsg(null);
    const res = await fetch('/api/social/teacher-invite', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId }),
    });
    const data = (await res.json()) as { error?: string };
    if (!res.ok) {
      setMsg(data.error ?? 'Invite failed');
      return;
    }
    setMsg(isHe ? 'הבקשה נשלחה לתלמיד' : 'Invite sent to student');
    setHits([]);
  }

  async function saveAbout() {
    setSavingAbout(true);
    await fetch('/api/educator/profile', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ about_me: about }),
    });
    setSavingAbout(false);
    setMsg(isHe ? 'הפרופיל נשמר' : 'Profile saved');
  }

  return (
    <div className="space-y-8" dir={isHe ? 'rtl' : 'ltr'}>
      <header>
        <h1 className="font-display text-2xl font-bold">
          {isHe ? 'התלמידים שלי' : 'My students'}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {isHe
            ? 'חפשו תלמיד לפי שם משתמש או שם מלא ושלחו בקשת חיבור.'
            : 'Search by username or real name and send a connection request.'}
        </p>
      </header>

      <section className="card-punch space-y-3 rounded-2xl p-5">
        <h2 className="font-semibold">{isHe ? 'הזמנת תלמיד' : 'Invite a student'}</h2>
        <div className="flex flex-wrap gap-2">
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={isHe ? 'שם משתמש או שם מלא' : 'Username or real name'}
            className="max-w-sm"
          />
          <Button type="button" onClick={() => void search()}>
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
                <div className="min-w-0 flex-1">
                  <p className="font-medium">
                    {h.real_name}{' '}
                    <span className="font-mono text-muted-foreground">@{h.username}</span>
                  </p>
                  {h.plan_summary || h.goal ? (
                    <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
                      {h.plan_summary || h.goal}
                    </p>
                  ) : (
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {isHe ? 'אין סיכום תוכנית עדיין' : 'No plan summary yet'}
                    </p>
                  )}
                </div>
                <Button type="button" size="sm" onClick={() => void invite(h.clerk_user_id)}>
                  {isHe ? 'שלח בקשה' : 'Invite'}
                </Button>
              </li>
            ))}
          </ul>
        ) : null}
        {msg ? <p className="text-sm text-muted-foreground">{msg}</p> : null}
      </section>

      <section className="space-y-3">
        <h2 className="font-semibold">
          {isHe ? `מחוברים (${students.length})` : `Connected (${students.length})`}
        </h2>
        {students.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            {isHe ? 'עדיין אין תלמידים מחוברים.' : 'No connected students yet.'}
          </p>
        ) : (
          <ul className="grid gap-3 sm:grid-cols-2">
            {students.map((s) => (
              <li key={s.clerk_user_id}>
                <Link
                  href={`/educator/students/${s.clerk_user_id}`}
                  className="block rounded-xl border border-border bg-card px-4 py-3 transition hover:border-primary/40"
                >
                  <p className="font-medium">{s.real_name}</p>
                  <p className="text-xs text-muted-foreground font-mono">@{s.username}</p>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card-punch space-y-3 rounded-2xl p-5">
        <h2 className="font-semibold">{isHe ? 'אודותיי (פרופיל מורה)' : 'About me (teacher profile)'}</h2>
        <textarea
          value={about}
          onChange={(e) => setAbout(e.target.value)}
          rows={4}
          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
        />
        <Button type="button" onClick={() => void saveAbout()} disabled={savingAbout}>
          {savingAbout ? (isHe ? 'שומר…' : 'Saving…') : isHe ? 'שמור' : 'Save'}
        </Button>
        <p>
          <Link href="/educator/profile" className="text-sm text-primary hover:underline">
            {isHe ? 'תצוגת פרופיל ציבורית' : 'Public profile view'}
          </Link>
        </p>
      </section>
    </div>
  );
}
