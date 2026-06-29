'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { cn } from '@asf/ui';

// ─── Progress Bar ────────────────────────────────────────────────────────────

/**
 * Thin reading-progress bar for 3pt-friendly legacy lessons.
 * Fills as the learner scrolls through the page, giving a gentle
 * sense of how far along they are without adding cognitive load.
 */
export function LegacySeedProgressBar({
  totalTopics,
  locale,
}: {
  totalTopics: number;
  locale: 'en' | 'he';
}) {
  const [pct, setPct] = useState(5);
  const isHe = locale === 'he';

  useEffect(() => {
    function onScroll() {
      const scrolled = window.scrollY;
      const total = document.documentElement.scrollHeight - window.innerHeight;
      if (total <= 0) return;
      setPct(Math.max(5, Math.min(100, Math.round((scrolled / total) * 100))));
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    // Trigger once on mount so initial position is reflected.
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const topicsLabel =
    pct >= 99
      ? isHe
        ? `${totalTopics} / ${totalTopics} נושאים ✓`
        : `${totalTopics} / ${totalTopics} topics ✓`
      : isHe
        ? `שיעור • ${totalTopics} נושאים`
        : `Lesson • ${totalTopics} topics`;

  return (
    <div className="mb-5" dir={isHe ? 'rtl' : 'ltr'}>
      <div className="mb-1 flex items-center justify-between text-[11px] text-muted-foreground">
        <span>{topicsLabel}</span>
        <span className="font-medium">{pct}%</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
        <div
          className="h-1.5 rounded-full bg-blue-200 dark:bg-blue-900 transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

// ─── Complete Area ────────────────────────────────────────────────────────────

/**
 * Complete button with a one-time motivational message shown after the learner
 * marks the lesson done. Navigates to the dashboard after a short pause so
 * the student has time to read the encouragement.
 */
export function LegacySeedCompleteArea({
  conceptId,
  locale,
}: {
  conceptId: string;
  locale: 'en' | 'he';
}) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [completed, setCompleted] = useState(false);
  const isHe = locale === 'he';

  async function handleComplete() {
    if (saving || completed) return;
    setSaving(true);
    try {
      await fetch('/api/lessons/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept_id: conceptId }),
      });
    } catch {
      // Best-effort — mark done in UI regardless.
    } finally {
      setSaving(false);
      setCompleted(true);
      // Navigate after a brief pause so the learner sees the message.
      setTimeout(() => router.push('/app?completed=1'), 3000);
    }
  }

  const buttonLabel = saving
    ? isHe
      ? 'שומר…'
      : 'Saving…'
    : completed
      ? isHe
        ? '✓ סיימת את השיעור!'
        : '✓ Lesson complete!'
      : isHe
        ? '✓ סיימתי את השיעור'
        : '✓ Mark lesson complete';

  return (
    <div className="flex flex-col gap-2">
      <button
        type="button"
        disabled={saving || completed}
        onClick={() => void handleComplete()}
        className={cn(
          'inline-flex w-fit items-center justify-center gap-2 rounded-lg border px-5 py-2.5 text-sm font-semibold transition-all disabled:opacity-80',
          completed
            ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
            : 'border-border bg-background hover:border-primary/40',
        )}
      >
        {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : null}
        {buttonLabel}
      </button>

      {/* Motivational micro-message — shown once after completion. */}
      {completed ? (
        <p
          className="mt-1 animate-in fade-in slide-in-from-bottom-2 text-sm text-emerald-700 dark:text-emerald-400 duration-500"
          dir={isHe ? 'rtl' : 'ltr'}
        >
          {isHe
            ? 'כל שיעור שמסיים מקרב אותך למטרה. המשיך כך! 🌟'
            : 'Every lesson you finish puts you closer to your goal. Keep it up! 🌟'}
        </p>
      ) : null}
    </div>
  );
}
