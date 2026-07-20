'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useI18n } from '@/providers/i18n-provider';

export function TeacherChip({
  realName,
  username,
}: {
  realName: string;
  username: string;
}) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const [busy, setBusy] = useState(false);

  async function disconnect() {
    if (!window.confirm(isHe ? 'לבטל את החיבור למורה?' : 'Disconnect from your teacher?')) {
      return;
    }
    setBusy(true);
    await fetch('/api/social/teacher-link/disconnect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    setBusy(false);
    window.location.reload();
  }

  return (
    <span className="inline-flex flex-wrap items-center gap-2">
      <Link
        href={`/u/${username}`}
        className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-4 py-2 text-sm font-medium backdrop-blur-sm hover:bg-white/25"
      >
        {isHe ? `מורה: ${realName}` : `Teacher: ${realName}`}
      </Link>
      <button
        type="button"
        disabled={busy}
        onClick={() => void disconnect()}
        className="rounded-full bg-white/10 px-3 py-1.5 text-xs font-medium hover:bg-white/20 disabled:opacity-50"
      >
        {isHe ? 'נתק' : 'Disconnect'}
      </button>
    </span>
  );
}
