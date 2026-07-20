'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { useI18n } from '@/providers/i18n-provider';
import {
  normalizeUsername,
  suggestUsernameFromRealName,
  validateRealName,
  validateUsername,
} from '@/lib/social-identity';

type RoleChoice = 'learner' | 'educator';

function heError(en: string): string {
  if (en.includes('Real name must use English')) {
    return 'השם המלא חייב להיות באנגלית בלבד (ניתן רווח, מקף וגרש).';
  }
  if (en.includes('Real name is required')) {
    return 'יש להזין שם מלא באנגלית.';
  }
  if (en.includes('already taken')) {
    return 'שם המשתמש תפוס — בחרו שם אחר.';
  }
  if (en.includes('at least 3') || en.includes('3–24') || en.includes('3-24')) {
    return 'שם משתמש: 3–24 תווים באנגלית, מספרים וקו תחתון בלבד (בלי רווחים — רווח הופך ל־_).';
  }
  return en;
}

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
  const { user } = useUser();
  const search = useSearchParams();
  const next = search.get('next') || '/app';

  const [role, setRole] = useState<RoleChoice>(initialRole ?? 'learner');
  const [username, setUsername] = useState('');
  const [realName, setRealName] = useState('');
  const [aboutMe, setAboutMe] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [usernameTouched, setUsernameTouched] = useState(false);

  function onRealNameChange(value: string) {
    setRealName(value);
    if (!usernameTouched) {
      const suggestion = suggestUsernameFromRealName(value);
      if (suggestion) setUsername(suggestion);
    }
  }

  function onUsernameChange(value: string) {
    setUsernameTouched(true);
    // Live-normalize spaces so "Alon Oren" becomes alon_oren as they type.
    setUsername(normalizeUsername(value) || value.replace(/\s+/g, '_').toLowerCase());
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);

    const realErr = validateRealName(realName);
    if (realErr) {
      setError(isHe ? heError(realErr) : realErr);
      setSaving(false);
      return;
    }
    const normalized = normalizeUsername(username);
    const userErr = validateUsername(normalized);
    if (userErr) {
      setError(isHe ? heError(userErr) : userErr);
      setSaving(false);
      return;
    }
    setUsername(normalized);

    try {
      const res = await fetch('/api/identity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role,
          username: normalized,
          real_name: realName.trim().replace(/\s+/g, ' '),
          about_me: role === 'educator' ? aboutMe || null : null,
        }),
      });
      const data = (await res.json()) as { error?: string; redirect?: string };
      if (!res.ok) {
        const msg = data.error ?? (isHe ? 'שמירה נכשלה' : 'Save failed');
        setError(isHe ? heError(msg) : msg);
        setSaving(false);
        return;
      }
      // Refresh Clerk client cache so publicMetadata.role is visible ASAP.
      await user?.reload().catch(() => undefined);
      const dest = data.redirect ?? (role === 'educator' ? '/educator' : next);
      // Hard navigation avoids RSC cache serving a stale redirect loop.
      window.location.assign(dest);
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
            ? 'שם מלא באנגלית (יכול להיות משותף) ושם משתמש ייחודי באנגלית.'
            : 'English real name (may be shared) and a unique English username.'}
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
          <span className="text-sm font-medium">
            {isHe ? 'שם מלא באנגלית' : 'Real full name (English)'}
          </span>
          <Input
            value={realName}
            onChange={(e) => onRealNameChange(e.target.value)}
            placeholder="Alon Oren"
            required
            autoComplete="name"
            dir="ltr"
            className="text-start"
          />
          <span className="text-xs text-muted-foreground">
            {isHe
              ? 'באנגלית בלבד. כמה אנשים יכולים לחלוק אותו שם — החיפוש יציג את כולם עם שם המשתמש.'
              : 'English only. Several people may share a name — search lists all matches with usernames.'}
          </span>
        </label>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium">
            {isHe ? 'שם משתמש ייחודי' : 'Unique username'}
          </span>
          <Input
            value={username}
            onChange={(e) => onUsernameChange(e.target.value)}
            onBlur={() => setUsername(normalizeUsername(username))}
            placeholder="alon_oren"
            required
            autoComplete="username"
            dir="ltr"
            className="font-mono text-start"
          />
          <span className="text-xs text-muted-foreground">
            {isHe
              ? 'ייחודי במערכת · 3–24 תווים · אותיות באנגלית, מספרים ו־_ · רווחים הופכים ל־_'
              : 'Must be unique · 3–24 chars · English letters, numbers, _ · spaces become _'}
          </span>
        </label>

        {role === 'educator' ? (
          <label className="block space-y-1.5">
            <span className="text-sm font-medium">
              {isHe ? 'אודותיי (אופציונלי, עברית או אנגלית)' : 'About me (optional, Hebrew or English)'}
            </span>
            <textarea
              value={aboutMe}
              onChange={(e) => setAboutMe(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
              placeholder={isHe ? 'מורה למתמטיקה לבגרות…' : 'Math teacher for Bagrut…'}
            />
          </label>
        ) : null}
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
