'use client';

/**
 * Intensive practice arena UI (ADR-0013).
 * One sealed item at a time; hints never reveal the final answer.
 */

import { useCallback, useMemo, useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import { MarkdownMath } from '@/components/markdown-math';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import type { PracticeItemPublic, PracticeSessionPublic } from '@/lib/practice-arena';
import { Loader2, Lightbulb, ArrowRight, Flag } from 'lucide-react';

type Phase = 'idle' | 'loading' | 'active' | 'feedback' | 'done' | 'error';

interface FeedbackPayload {
  correct: boolean;
  gave_up: boolean;
  explanation_en: string;
  explanation_he: string;
}

export function PracticeArenaClient({
  initialConceptId = null,
}: {
  initialConceptId?: string | null;
}) {
  const [lang] = useLanguagePreference();
  const he = lang === 'he';

  const [phase, setPhase] = useState<Phase>('idle');
  const [session, setSession] = useState<PracticeSessionPublic | null>(null);
  const [item, setItem] = useState<PracticeItemPublic | null>(null);
  const [answer, setAnswer] = useState<string>('');
  const [mcqIndex, setMcqIndex] = useState<number | null>(null);
  const [tf, setTf] = useState<boolean | null>(null);
  const [feedback, setFeedback] = useState<FeedbackPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const stem = useMemo(() => {
    if (!item) return '';
    return he ? item.stem_he : item.stem_en;
  }, [item, he]);

  const options = useMemo(() => {
    if (!item) return [];
    return (he ? item.options_he : item.options_en) ?? [];
  }, [item, he]);

  const start = useCallback(async () => {
    setBusy(true);
    setError(null);
    setPhase('loading');
    try {
      const res = await fetch('/api/practice/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept_id: initialConceptId || undefined,
          goal_items: 10,
          goal_minutes: 15,
        }),
      });
      const data = (await res.json()) as PracticeSessionPublic & {
        error?: string;
        message?: string;
      };
      if (!res.ok) {
        setError(data.message || data.error || 'Failed to start');
        setPhase('error');
        return;
      }
      setSession(data);
      setItem(data.item);
      setAnswer('');
      setMcqIndex(null);
      setTf(null);
      setFeedback(null);
      setPhase(data.item ? 'active' : 'error');
    } catch {
      setError(he ? 'שגיאת רשת' : 'Network error');
      setPhase('error');
    } finally {
      setBusy(false);
    }
  }, [he, initialConceptId]);

  const requestHint = useCallback(async () => {
    if (!session || busy) return;
    setBusy(true);
    try {
      const res = await fetch('/api/practice/hint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.session_id }),
      });
      const data = (await res.json()) as {
        session?: PracticeSessionPublic;
        error?: string;
      };
      if (res.ok && data.session) {
        setSession(data.session);
        setItem(data.session.item);
      }
    } finally {
      setBusy(false);
    }
  }, [busy, session]);

  const submit = useCallback(
    async (giveUp = false) => {
      if (!session || !item || busy) return;
      setBusy(true);
      try {
        let payload: unknown = answer;
        if (item.kind === 'mcq') payload = mcqIndex;
        if (item.kind === 'true_false') payload = tf;

        const res = await fetch('/api/practice/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: session.session_id,
            item_id: item.id,
            answer: payload,
            give_up: giveUp,
          }),
        });
        const data = (await res.json()) as {
          feedback?: FeedbackPayload;
          session?: PracticeSessionPublic;
          goal_reached?: boolean;
          error?: string;
        };
        if (!res.ok) {
          setError(data.error || 'Submit failed');
          return;
        }
        if (data.session) setSession(data.session);
        if (data.feedback) setFeedback(data.feedback);
        setPhase(data.goal_reached ? 'done' : 'feedback');
      } finally {
        setBusy(false);
      }
    },
    [answer, busy, item, mcqIndex, session, tf],
  );

  const continueNext = useCallback(async () => {
    if (!session || busy) return;
    if (session.status === 'ended') {
      setPhase('done');
      return;
    }
    setBusy(true);
    setFeedback(null);
    try {
      const res = await fetch('/api/practice/next', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.session_id }),
      });
      const data = (await res.json()) as {
        session?: PracticeSessionPublic;
        ended?: boolean;
        error?: string;
      };
      if (!res.ok) {
        setError(data.error || 'No more items');
        setPhase('error');
        return;
      }
      if (data.ended || !data.session?.item) {
        setSession(data.session ?? session);
        setPhase('done');
        return;
      }
      setSession(data.session);
      setItem(data.session.item);
      setAnswer('');
      setMcqIndex(null);
      setTf(null);
      setPhase('active');
    } finally {
      setBusy(false);
    }
  }, [busy, session]);

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-8">
      <header className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {he ? 'זירת תרגול' : 'Practice arena'}
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-foreground">
          {he ? 'תרגול אינטנסיבי' : 'Intensive practice'}
        </h1>
        <p className="text-sm text-muted-foreground">
          {he
            ? 'שאלה אחת בכל פעם, לפי מה שאתה צריך. רמזים בלי לחשוף את התשובה.'
            : 'One question at a time, matched to what you need. Hints never reveal the answer.'}
        </p>
      </header>

      {session ? (
        <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          <span>
            {he ? 'התקדמות' : 'Progress'}: {session.attempted}/{session.goal_items}
          </span>
          <span>
            {he ? 'נכון' : 'Correct'}: {session.correct_count}
          </span>
          <span>
            {he ? 'רמזים' : 'Hints'}: {session.hints_used}
          </span>
        </div>
      ) : null}

      {phase === 'idle' || phase === 'error' ? (
        <div className="space-y-4 rounded-xl border border-border/60 bg-surface-1/50 p-6">
          {error ? <p className="text-sm text-destructive">{error}</p> : null}
          <Button onClick={() => void start()} disabled={busy}>
            {busy ? <Loader2 className="me-2 h-4 w-4 animate-spin" /> : null}
            {he ? 'התחל תרגול' : 'Start practice'}
          </Button>
          <p className="text-xs text-muted-foreground">
            {he ? 'יעד רך: 10 שאלות · 15 דקות' : 'Soft goal: 10 items · 15 minutes'}
          </p>
        </div>
      ) : null}

      {phase === 'loading' ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          {he ? 'טוען שאלה…' : 'Loading item…'}
        </div>
      ) : null}

      {(phase === 'active' || phase === 'feedback') && item ? (
        <div className="space-y-5 rounded-xl border border-border/60 bg-surface-1/40 p-6">
          <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
            <span>
              {item.difficulty} · {item.kind} · {item.source}
            </span>
            <Link
              href={`/app/chat/coach?practice=${encodeURIComponent(item.concept_id)}`}
              className="underline-offset-2 hover:underline"
            >
              {he ? 'עזרה ממאמן' : 'Ask Coach'}
            </Link>
          </div>

          <div className="prose prose-sm dark:prose-invert max-w-none" dir={he ? 'rtl' : 'ltr'}>
            <MarkdownMath>{stem}</MarkdownMath>
          </div>

          {phase === 'active' ? (
            <>
              {item.kind === 'mcq' ? (
                <ul className="space-y-2">
                  {options.map((opt, i) => (
                    <li key={i}>
                      <button
                        type="button"
                        onClick={() => setMcqIndex(i)}
                        className={cn(
                          'w-full rounded-lg border px-3 py-2 text-start text-sm transition-colors',
                          mcqIndex === i
                            ? 'border-primary bg-primary/10'
                            : 'border-border/70 hover:bg-surface-2/50',
                        )}
                      >
                        <MarkdownMath>{opt}</MarkdownMath>
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}

              {item.kind === 'true_false' ? (
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={tf === true ? 'default' : 'outline'}
                    onClick={() => setTf(true)}
                  >
                    {he ? 'נכון' : 'True'}
                  </Button>
                  <Button
                    type="button"
                    variant={tf === false ? 'default' : 'outline'}
                    onClick={() => setTf(false)}
                  >
                    {he ? 'לא נכון' : 'False'}
                  </Button>
                </div>
              ) : null}

              {item.kind === 'numeric' ||
              item.kind === 'short_answer' ||
              item.kind === 'fill_blank' ? (
                <input
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder={he ? 'התשובה שלך' : 'Your answer'}
                  dir="ltr"
                />
              ) : null}

              {item.unlocked_hints.length > 0 ? (
                <div className="space-y-2 rounded-lg bg-surface-2/40 p-3 text-sm">
                  <p className="font-medium">{he ? 'רמזים' : 'Hints'}</p>
                  {item.unlocked_hints.map((h, i) => (
                    <p key={i} className="text-muted-foreground">
                      {i + 1}. {he ? h.he : h.en}
                    </p>
                  ))}
                </div>
              ) : null}

              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => void requestHint()}
                  disabled={busy || (item.hint_step ?? 0) >= 3}
                >
                  <Lightbulb className="me-2 h-4 w-4" />
                  {he ? 'רמז' : 'Hint'}
                </Button>
                <Button type="button" onClick={() => void submit(false)} disabled={busy}>
                  {he ? 'שלח' : 'Submit'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => void submit(true)}
                  disabled={busy}
                >
                  <Flag className="me-2 h-4 w-4" />
                  {he ? 'ויתור' : 'Give up'}
                </Button>
              </div>
            </>
          ) : null}

          {phase === 'feedback' && feedback ? (
            <div className="space-y-3">
              <p
                className={cn(
                  'text-sm font-semibold',
                  feedback.correct ? 'text-emerald-600' : 'text-amber-700',
                )}
              >
                {feedback.correct
                  ? he
                    ? 'נכון!'
                    : 'Correct!'
                  : feedback.gave_up
                    ? he
                      ? 'ויתרת — הנה הפתרון'
                      : 'Gave up — here’s the solution'
                    : he
                      ? 'לא מדויק — הנה ההסבר'
                      : 'Not quite — here’s the explanation'}
              </p>
              <div className="prose prose-sm dark:prose-invert max-w-none" dir={he ? 'rtl' : 'ltr'}>
                <MarkdownMath>
                  {he ? feedback.explanation_he : feedback.explanation_en}
                </MarkdownMath>
              </div>
              <Button type="button" onClick={() => void continueNext()} disabled={busy}>
                {he ? 'הבא' : 'Next'}
                <ArrowRight className="ms-2 h-4 w-4" />
              </Button>
            </div>
          ) : null}
        </div>
      ) : null}

      {phase === 'done' && session ? (
        <div className="space-y-4 rounded-xl border border-border/60 bg-surface-1/50 p-6">
          <h2 className="text-lg font-semibold">
            {he ? 'סשן הושלם' : 'Session complete'}
          </h2>
          <p className="text-sm text-muted-foreground">
            {he
              ? `${session.correct_count} נכונות מתוך ${session.attempted}`
              : `${session.correct_count} correct out of ${session.attempted}`}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => void start()}>{he ? 'סבב נוסף' : 'Another round'}</Button>
            <Button asChild variant="outline">
              <Link href="/app">{he ? 'ללוח הבקרה' : 'Dashboard'}</Link>
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
