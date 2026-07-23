'use client';

/**
 * Intensive practice arena UI (ADR-0013 v2).
 * Topic multi-select → open exam-style items → Finish + summary.
 */

import { useCallback, useMemo, useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';
import { MarkdownMath } from '@/components/markdown-math';
import { AgentSidePanel } from '@/components/agent-side-panel';
import { PracticeMathCheatSheet } from '@/components/practice-math-cheat-sheet';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import type {
  PracticeChatContext,
  PracticeItemPublic,
  PracticeSessionPublic,
  PracticeSessionSummary,
} from '@/lib/practice-arena';
import { practiceTopicLabels, practiceTopicsByGroup } from '@/lib/practice-topics';
import { Loader2, Lightbulb, ArrowRight, Flag, Square } from 'lucide-react';

type Phase = 'pick' | 'loading' | 'active' | 'feedback' | 'done' | 'error';

interface FeedbackPayload {
  correct: boolean;
  gave_up: boolean;
  grading_unavailable?: boolean;
  process_score?: number | null;
  process?: {
    strengths: string;
    steps_present: string;
    steps_skipped: string;
    logic: string;
    next_fix: string;
    points_earned: number;
    points_available: number;
  } | null;
  explanation_en: string;
  explanation_he: string;
  correct_answer?: string;
}

async function fetchJson<T>(
  url: string,
  init: RequestInit,
  timeoutMs = 45_000,
): Promise<{ ok: boolean; status: number; data: T }> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...init, signal: ctrl.signal });
    let data = {} as T;
    try {
      data = (await res.json()) as T;
    } catch {
      /* non-JSON */
    }
    return { ok: res.ok, status: res.status, data };
  } finally {
    clearTimeout(timer);
  }
}

export function PracticeArenaClient({
  initialConceptId = null,
  initialTopicIds = [],
}: {
  initialConceptId?: string | null;
  initialTopicIds?: string[];
}) {
  const [lang] = useLanguagePreference();
  const he = lang === 'he';

  const [phase, setPhase] = useState<Phase>('pick');
  const [topicIds, setTopicIds] = useState<string[]>(initialTopicIds);
  const [session, setSession] = useState<PracticeSessionPublic | null>(null);
  const [item, setItem] = useState<PracticeItemPublic | null>(null);
  const [answer, setAnswer] = useState('');
  const [mcqIndex, setMcqIndex] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<FeedbackPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [busyAction, setBusyAction] = useState<'hint' | 'submit' | 'giveup' | 'next' | 'finish' | null>(
    null,
  );
  const [summary, setSummary] = useState<PracticeSessionSummary | null>(null);

  const topicGroups = useMemo(() => practiceTopicsByGroup(he ? 'he' : 'en'), [he]);

  const stem = useMemo(() => {
    if (!item) return '';
    return he ? item.stem_he : item.stem_en;
  }, [item, he]);

  const options = useMemo(() => {
    if (!item) return [];
    return (he ? item.options_he : item.options_en) ?? [];
  }, [item, he]);

  const practiceContext = useMemo((): PracticeChatContext | null => {
    if (!session || !item) return null;
    return {
      session_id: session.session_id,
      item_id: item.id,
      concept_id: item.concept_id,
      kind: item.kind,
      difficulty: item.difficulty,
      hint_step: item.hint_step,
      stem_en: item.stem_en,
      stem_he: item.stem_he,
      item_graded: session.item_graded || phase === 'feedback',
    };
  }, [session, item, phase]);

  const toggleTopic = (id: string) => {
    setTopicIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id].slice(0, 12),
    );
  };

  const start = useCallback(async () => {
    if (!topicIds.length && !initialConceptId) {
      setError(he ? 'בחרו לפחות נושא אחד' : 'Select at least one topic');
      return;
    }
    setBusy(true);
    setError(null);
    setPhase('loading');
    try {
      const { ok, data } = await fetchJson<
        PracticeSessionPublic & { error?: string; message?: string }
      >('/api/practice/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept_id: initialConceptId || undefined,
          topic_ids: topicIds,
          goal_items: 10,
          goal_minutes: 15,
        }),
      }, 90_000);
      if (!ok) {
        setError(data.message || data.error || 'Failed to start');
        setPhase('error');
        return;
      }
      setSession(data);
      setItem(data.item);
      setAnswer('');
      setMcqIndex(null);
      setFeedback(null);
      setSummary(null);
      setPhase(data.item ? 'active' : 'error');
      if (!data.item) {
        setError(he ? 'לא נמצאו שאלות לנושאים אלה' : 'No items for these topics');
      }
    } catch {
      setError(he ? 'שגיאת רשת או פג תוקף הבקשה' : 'Network error or request timed out');
      setPhase('error');
    } finally {
      setBusy(false);
    }
  }, [he, initialConceptId, topicIds]);

  const requestHint = useCallback(async () => {
    if (!session || busy) return;
    setBusy(true);
    setBusyAction('hint');
    setError(null);
    try {
      const { ok, data } = await fetchJson<{
        session?: PracticeSessionPublic;
        error?: string;
      }>('/api/practice/hint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.session_id }),
      }, 30_000);
      if (!ok) {
        setError(
          data.error === 'already_submitted'
            ? he
              ? 'השאלה כבר נבדקה'
              : 'Item already graded'
            : data.error || (he ? 'לא ניתן לטעון רמז' : 'Could not load hint'),
        );
        return;
      }
      if (data.session) {
        setSession(data.session);
        setItem(data.session.item);
      }
    } catch {
      setError(he ? 'רמז נכשל — נסו שוב' : 'Hint failed — try again');
    } finally {
      setBusy(false);
      setBusyAction(null);
    }
  }, [busy, he, session]);

  const submit = useCallback(
    async (giveUp = false) => {
      if (!session || !item || busy) return;
      if (!giveUp && item.kind !== 'mcq' && !answer.trim()) {
        setError(he ? 'כתבו תשובה לפני שליחה, או ויתרו להצגת הפתרון' : 'Write an answer, or give up to see the solution');
        return;
      }
      if (!giveUp && item.kind === 'mcq' && mcqIndex === null) {
        setError(he ? 'בחרו אפשרות' : 'Select an option');
        return;
      }
      setBusy(true);
      setBusyAction(giveUp ? 'giveup' : 'submit');
      setError(null);
      try {
        let payload: unknown = answer;
        if (item.kind === 'mcq') payload = mcqIndex;

        // Client budget must exceed route maxDuration (60s) so we rarely abort mid-grade.
        const { ok, data } = await fetchJson<{
          feedback?: FeedbackPayload;
          session?: PracticeSessionPublic;
          error?: string;
          recovered?: boolean;
        }>(
          '/api/practice/submit',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: session.session_id,
              item_id: item.id,
              answer: payload,
              give_up: giveUp,
            }),
          },
          75_000,
        );
        if (!ok) {
          setError(
            data.error === 'grading_failed'
              ? he
                ? 'הבדיקה נכשלה זמנית — נסו שוב או ויתרו להצגת פתרון'
                : 'Grading failed temporarily — retry or give up to see the solution'
              : data.error || (he ? 'שליחה נכשלה' : 'Submit failed'),
          );
          return;
        }
        if (data.session) setSession(data.session);
        if (data.feedback) setFeedback(data.feedback);
        setPhase('feedback');
      } catch {
        // Timed out while server may still have graded — recover via idempotent resubmit.
        try {
          const recover = await fetchJson<{
            feedback?: FeedbackPayload;
            session?: PracticeSessionPublic;
          }>(
            '/api/practice/submit',
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                session_id: session.session_id,
                item_id: item.id,
                answer: giveUp ? '' : answer,
                give_up: giveUp,
              }),
            },
            20_000,
          );
          if (recover.ok && recover.data.feedback) {
            if (recover.data.session) setSession(recover.data.session);
            setFeedback(recover.data.feedback);
            setPhase('feedback');
            return;
          }
        } catch {
          /* fall through */
        }
        setError(
          he
            ? 'שליחה נכשלה או פג תוקף — נסו שוב, או ויתרו להצגת פתרון'
            : 'Submit failed or timed out — retry, or give up to see the solution',
        );
      } finally {
        setBusy(false);
        setBusyAction(null);
      }
    },
    [answer, busy, he, item, mcqIndex, session],
  );

  const continueNext = useCallback(async () => {
    if (!session || busy) return;
    setBusy(true);
    setBusyAction('next');
    setError(null);
    try {
      const { ok, data } = await fetchJson<{
        session?: PracticeSessionPublic;
        ended?: boolean;
        error?: string;
        message?: string;
      }>(
        '/api/practice/next',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: session.session_id }),
        },
        90_000,
      );
      if (data.ended || data.error === 'thin_topic') {
        if (data.session) {
          setSession(data.session);
          setSummary(data.session.summary ?? null);
        }
        setFeedback(null);
        setPhase('done');
        return;
      }
      if (!ok) {
        setError(data.message || data.error || 'No more items');
        // Keep feedback/solution visible so the learner can retry Next.
        return;
      }
      if (!data.session?.item) {
        setFeedback(null);
        setPhase('done');
        return;
      }
      setSession(data.session);
      setItem(data.session.item);
      setAnswer('');
      setMcqIndex(null);
      setFeedback(null);
      setPhase('active');
    } catch {
      setError(he ? 'טעינת השאלה הבאה נכשלה' : 'Failed to load next item');
    } finally {
      setBusy(false);
      setBusyAction(null);
    }
  }, [busy, he, session]);

  const finish = useCallback(async () => {
    if (!session || busy) return;
    setBusy(true);
    setBusyAction('finish');
    try {
      const { ok, data } = await fetchJson<{
        session?: PracticeSessionPublic;
        error?: string;
      }>('/api/practice/finish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.session_id }),
      }, 30_000);
      if (ok && data.session) {
        setSession(data.session);
        setSummary(data.session.summary ?? null);
        setPhase('done');
      } else {
        setError(data.error || 'Finish failed');
      }
    } catch {
      setError(he ? 'סיום נכשל' : 'Finish failed');
    } finally {
      setBusy(false);
      setBusyAction(null);
    }
  }, [busy, he, session]);

  const topicLabelList = practiceTopicLabels(session?.topic_ids ?? topicIds, he ? 'he' : 'en');
  const explanation = feedback
    ? he
      ? feedback.explanation_he
      : feedback.explanation_en
    : '';

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-8">
      <header className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {he ? 'זירת תרגול' : 'Practice arena'}
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-foreground">
          {he ? 'תרגול בסגנון מבחן' : 'Exam-style practice'}
        </h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          {he
            ? 'בחרו נושאים, ענו על שאלות פתוחות בסגנון בגרות/אוניברסיטה, וסיימו כשאתם מוכנים — בלי שעון.'
            : 'Pick topics, answer open bagrut/uni-style questions, and finish when ready — no timer.'}
        </p>
      </header>

      {error ? (
        <p className="rounded-lg border border-destructive/40 bg-destructive/5 px-3 py-2 text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      {session && phase !== 'pick' ? (
        <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          <span>
            {he ? 'התקדמות' : 'Progress'}: {session.attempted}/{session.goal_items}
          </span>
          <span>
            {he ? 'הצלחות' : 'Successes'}: {session.correct_count}
          </span>
          <span>
            {he ? 'רמזים' : 'Hints'}: {session.hints_used}
          </span>
          {topicLabelList.length ? (
            <span className="truncate">
              {he ? 'נושאים' : 'Topics'}: {topicLabelList.join(', ')}
            </span>
          ) : null}
          {phase !== 'done' ? (
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="ms-auto"
              onClick={() => void finish()}
              disabled={busy}
            >
              {busyAction === 'finish' ? (
                <Loader2 className="me-2 h-3.5 w-3.5 animate-spin" />
              ) : (
                <Square className="me-2 h-3.5 w-3.5" />
              )}
              {he ? 'סיים תרגול' : 'Finish training'}
            </Button>
          ) : null}
        </div>
      ) : null}

      {(phase === 'pick' || phase === 'error') && !session ? (
        <div className="space-y-4 rounded-xl border border-border/60 bg-surface-1/50 p-6">
          <fieldset className="space-y-4">
            <legend className="text-sm font-medium">
              {he ? 'מה תרצו לתרגל?' : 'What do you want to train?'}
            </legend>
            {topicGroups.map(({ group, topics }) => (
              <div key={group} className="space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {group}
                </p>
                <div className="flex flex-wrap gap-2">
                  {topics.map((t) => {
                    const on = topicIds.includes(t.id);
                    return (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => toggleTopic(t.id)}
                        className={cn(
                          'rounded-lg border px-3 py-1.5 text-sm transition-colors',
                          on
                            ? 'border-primary bg-primary/10'
                            : 'border-border/70 hover:bg-surface-2/50',
                        )}
                        aria-pressed={on}
                      >
                        {he ? t.label_he : t.label_en}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </fieldset>
          <Button onClick={() => void start()} disabled={busy || (!topicIds.length && !initialConceptId)}>
            {busy ? <Loader2 className="me-2 h-4 w-4 animate-spin" /> : null}
            {he ? 'התחל תרגול' : 'Start practice'}
          </Button>
          <p className="text-xs text-muted-foreground">
            {he
              ? 'יעד רך: ~10 שאלות · עד 12 נושאים · אפשר לסיים בכל רגע'
              : 'Soft goal: ~10 items · up to 12 topics · finish anytime'}
          </p>
          <p className="text-xs text-muted-foreground">
            <Link href="/app/practice/history" className="underline-offset-2 hover:underline">
              {he ? 'היסטוריית תרגולים' : 'Practice history'}
            </Link>
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
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(280px,340px)]">
          <div className="space-y-5 rounded-xl border border-border/60 bg-surface-1/40 p-6">
            <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
              <span>
                {item.difficulty} · {item.kind} · {item.source}
                {item.points_available ? ` · ${item.points_available}pt` : ''}
              </span>
            </div>

            <div className="prose prose-sm dark:prose-invert max-w-none" dir={he ? 'rtl' : 'ltr'}>
              <MarkdownMath>{stem}</MarkdownMath>
            </div>

            {phase === 'active' && !session?.item_graded ? (
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
                ) : (
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground" htmlFor="practice-answer">
                      {he ? 'התשובה שלך (עם שלבים)' : 'Your answer (show your work)'}
                    </label>
                    <textarea
                      id="practice-answer"
                      className="min-h-[160px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                      value={answer}
                      onChange={(e) => setAnswer(e.target.value)}
                      placeholder={
                        he
                          ? 'כתבו פתרון מלא. מתמטיקה ב-$...$'
                          : 'Write a full solution. Math in $...$'
                      }
                      dir={he ? 'rtl' : 'ltr'}
                    />
                    {answer.trim() ? (
                      <div className="rounded-lg bg-surface-2/40 p-3 text-sm" dir={he ? 'rtl' : 'ltr'}>
                        <p className="mb-1 text-xs text-muted-foreground">
                          {he ? 'תצוגה מקדימה' : 'Preview'}
                        </p>
                        <MarkdownMath>{answer}</MarkdownMath>
                      </div>
                    ) : null}
                  </div>
                )}

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
                    {busyAction === 'hint' ? (
                      <Loader2 className="me-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Lightbulb className="me-2 h-4 w-4" />
                    )}
                    {he ? 'רמז' : 'Hint'}
                  </Button>
                  <Button type="button" onClick={() => void submit(false)} disabled={busy}>
                    {busyAction === 'submit' ? (
                      <Loader2 className="me-2 h-4 w-4 animate-spin" />
                    ) : null}
                    {he ? 'שלח' : 'Submit'}
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => void submit(true)}
                    disabled={busy}
                    title={
                      he
                        ? 'מציג את הפתרון ומאפשר מעבר לשאלה הבאה'
                        : 'Shows the solution, then you can go to the next question'
                    }
                  >
                    {busyAction === 'giveup' ? (
                      <Loader2 className="me-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Flag className="me-2 h-4 w-4" />
                    )}
                    {he ? 'ויתור + פתרון → הבא' : 'Give up + solution → next'}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  {he
                    ? 'ויתור מציג את הפתרון המלא; אחר כך לחצו «השאלה הבאה».'
                    : 'Give up reveals the full solution; then click “Next question”.'}
                </p>
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
                      ? 'הצלחה (ציון תהליך מספיק)'
                      : 'Success (process score met)'
                    : feedback.gave_up
                      ? he
                        ? 'ויתרת — הנה הפתרון. אפשר להמשיך לשאלה הבאה.'
                        : 'Gave up — here’s the solution. Continue to the next question.'
                      : he
                        ? 'עדיין לא — הנה משוב'
                        : 'Not yet — here’s feedback'}
                  {typeof feedback.process_score === 'number'
                    ? ` · ${(feedback.process_score * 100).toFixed(0)}%`
                    : ''}
                </p>
                {feedback.grading_unavailable ? (
                  <p className="text-xs text-muted-foreground">
                    {he
                      ? 'הבדיקה האוטומטית לא הייתה זמינה; הוצג פתרון המודל.'
                      : 'Auto-grading was unavailable; model solution shown.'}
                  </p>
                ) : null}
                {feedback.process ? (
                  <div className="space-y-1 text-sm text-muted-foreground" dir={he ? 'rtl' : 'ltr'}>
                    {feedback.process.strengths ? <p>{feedback.process.strengths}</p> : null}
                    {feedback.process.next_fix ? <p>{feedback.process.next_fix}</p> : null}
                  </div>
                ) : null}
                {explanation ? (
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground">
                      {he ? 'פתרון / הסבר' : 'Solution / explanation'}
                    </p>
                    <div
                      className="prose prose-sm dark:prose-invert max-w-none rounded-lg border border-border/50 bg-surface-2/30 p-3"
                      dir={he ? 'rtl' : 'ltr'}
                    >
                      <MarkdownMath>{explanation}</MarkdownMath>
                    </div>
                  </div>
                ) : null}
                {feedback.correct_answer ? (
                  <p className="text-sm" dir="ltr">
                    {he ? 'תשובה: ' : 'Answer: '}
                    <MarkdownMath>{String(feedback.correct_answer)}</MarkdownMath>
                  </p>
                ) : null}
                <Button type="button" onClick={() => void continueNext()} disabled={busy}>
                  {busyAction === 'next' ? (
                    <Loader2 className="me-2 h-4 w-4 animate-spin" />
                  ) : null}
                  {he ? 'השאלה הבאה' : 'Next question'}
                  <ArrowRight className="ms-2 h-4 w-4" />
                </Button>
              </div>
            ) : null}
          </div>
          <PracticeMathCheatSheet />
        </div>
      ) : null}

      {phase === 'done' && session ? (
        <div className="space-y-4 rounded-xl border border-border/60 bg-surface-1/50 p-6">
          <h2 className="text-lg font-semibold">{he ? 'סיכום תרגול' : 'Training summary'}</h2>
          <p className="text-sm text-muted-foreground">
            {he
              ? `${session.correct_count} הצלחות מתוך ${session.attempted}`
              : `${session.correct_count} successes out of ${session.attempted}`}
            {summary?.avg_process_score != null
              ? he
                ? ` · ממוצע תהליך ${(summary.avg_process_score * 100).toFixed(0)}%`
                : ` · avg process ${(summary.avg_process_score * 100).toFixed(0)}%`
              : null}
          </p>
          {summary?.weak_concepts?.length ? (
            <p className="text-sm text-muted-foreground">
              {he ? 'מושגים לחיזוק: ' : 'Strengthen: '}
              {summary.weak_concepts.join(', ')}
            </p>
          ) : null}
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={() => {
                setSession(null);
                setItem(null);
                setPhase('pick');
                setError(null);
              }}
            >
              {he ? 'סבב נוסף' : 'Another round'}
            </Button>
            <Button asChild variant="outline">
              <Link href="/app/practice/history">{he ? 'היסטוריה' : 'History'}</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/app">{he ? 'ללוח הבקרה' : 'Dashboard'}</Link>
            </Button>
          </div>
        </div>
      ) : null}

      {practiceContext ? (
        <AgentSidePanel
          practiceContext={practiceContext}
          defaultAgent="coach"
          fabLabel={{ he: 'עזרה ממאמן', en: 'Ask Coach' }}
        />
      ) : null}
    </div>
  );
}
