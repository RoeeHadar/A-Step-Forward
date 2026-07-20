'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { useI18n } from '@/providers/i18n-provider';

type RoleChoice = 'learner' | 'educator';

export function IdentitySetupForm({
  initialRole,
  lockedRole,
}: {
  initialRole?: RoleChoice;
  /** When true, role was already chosen and cannot change. */
  lockedRole?: boolean;
}) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const router = useRouter();
  const search = useSearchParams();
  const next = search.get('next') || '/app';

  const [role, setRole] = useState<RoleChoice>(initialRole ?? 'learner');
  const [username, setUsername] = useState('');
  const [realName, setRealName] = useState('');
  const [nickname, setNickname] = useState('');
  const [aboutMe, setAboutMe] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await fetch('/api/identity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role,
          username,
          real_name: realName,
          nickname: nickname || null,
          about_me: role === 'educator' ? aboutMe || null : null,
        }),
      });
      const data = (await res.json()) as { error?: string; redirect?: string };
      if (!res.ok) {
        setError(data.error ?? (isHe ? 'שמירה נכשלה' : 'Save failed'));
        setSaving(false);
        return;
      }
      router.replace(data.redirect ?? (role === 'educator' ? '/educator' : next));
      router.refresh();
    } catch {
      setError(isHe ? 'שגיאת רשת' : 'Network error');
      setSaving(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="mx-auto max-w-lg space-y-6" dir={isHe ? 'rtl' : 'ltr'}>
      <header className="space-y-2 text-center">
        <h1 className="font-display text-2xl font-bold">
          {isHe ? 'הגדרת חשבון' : 'Set up your account'}
        </h1>
        <p className="text-sm text-muted-foreground">
          {isHe
            ? 'בחרו תפקיד, שם משתמש ושם מלא — נדרש לחיבורים במערכת.'
            : 'Choose a role, username, and real name — required for connections.'}
        </p>
      </header>

      {!lockedRole ? (
        <fieldset className="grid gap-3 sm:grid-cols-2">
          <legend className="mb-2 text-sm font-medium">
            {isHe ? 'אני…' : 'I am a…'}
          </legend>
          <button
            type="button"
            onClick={() => setRole('learner')}
            className={`rounded-xl border-2 px-4 py-4 text-start transition ${
              role === 'learner'
                ? 'border-primary bg-primary/10'
                : 'border-border hover:border-primary/40'
            }`}
          >
            <p className="font-semibold">{isHe ? 'תלמיד/ה' : 'Student'}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {isHe ? 'תוכנית לימוד, התקדמות וזיכרון' : 'Learning plan, progress & memory'}
            </p>
          </button>
          <button
            type="button"
            onClick={() => setRole('educator')}
            className={`rounded-xl border-2 px-4 py-4 text-start transition ${
              role === 'educator'
                ? 'border-primary bg-primary/10'
                : 'border-border hover:border-primary/40'
            }`}
          >
            <p className="font-semibold">{isHe ? 'מורה' : 'Teacher'}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {isHe ? 'גישה לתלמידים — בלי תוכנית אישית' : 'Access students — no personal plan'}
            </p>
          </button>
        </fieldset>
      ) : null}

      <div className="space-y-4">
        <label className="block space-y-1.5">
          <span className="text-sm font-medium">{isHe ? 'שם משתמש' : 'Username'}</span>
          <Input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="student_anna"
            required
            autoComplete="username"
            dir="ltr"
            className="font-mono"
          />
          <span className="text-xs text-muted-foreground">
            {isHe ? '3–24 תווים, אותיות באנגלית, מספרים וקו תחתון' : '3–24 chars, letters, numbers, underscore'}
          </span>
        </label>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium">{isHe ? 'שם מלא (אמיתי)' : 'Real full name'}</span>
          <Input
            value={realName}
            onChange={(e) => setRealName(e.target.value)}
            placeholder={isHe ? 'ישראל ישראלי' : 'Jane Cohen'}
            required
            autoComplete="name"
          />
          <span className="text-xs text-muted-foreground">
            {isHe
              ? 'המורים מחפשים לפי שם מלא ושם משתמש — לא לפי אימייל'
              : 'Teachers find you by real name and username — not email'}
          </span>
        </label>

        {role === 'learner' ? (
          <label className="block space-y-1.5">
            <span className="text-sm font-medium">
              {isHe ? 'כינוי (אופציונלי לחברים)' : 'Nickname (optional, for friends)'}
            </span>
            <Input
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              placeholder={isHe ? 'אני' : 'Annie'}
            />
          </label>
        ) : (
          <label className="block space-y-1.5">
            <span className="text-sm font-medium">
              {isHe ? 'אודותיי (אופציונלי)' : 'About me (optional)'}
            </span>
            <textarea
              value={aboutMe}
              onChange={(e) => setAboutMe(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
              placeholder={isHe ? 'מורה למתמטיקה לבגרות…' : 'Math teacher for Bagrut…'}
            />
          </label>
        )}
      </div>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      <Button type="submit" className="w-full" disabled={saving}>
        {saving
          ? isHe
            ? 'שומר…'
            : 'Saving…'
          : isHe
            ? 'המשך'
            : 'Continue'}
      </Button>
    </form>
  );
}
