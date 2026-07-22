'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { MarkdownMath } from '@/components/markdown-math';
import { useI18n } from '@/providers/i18n-provider';

type TabId = 'overview' | 'plan' | 'progress' | 'tests' | 'memory';

interface PlanWeekView {
  week_number: number;
  status: string;
  quiz_due_at: string | null;
  concepts: Array<{ concept_id: string; name: string; mastery?: number | null }>;
}

interface ProgressView {
  streak_days: number;
  lessons_completed: number;
  avg_mastery: number;
  atoms_practiced: number;
  total_minutes: number;
  total_xp?: number;
  level?: number;
  concepts: Array<{ concept_id: string; title: string; score: number }>;
  daily_activity: Array<{ date: string; count: number }>;
}

interface MemoryView {
  persona: string | null;
  profile_goal: string | null;
  subjects: string[];
  preferred_style?: string | null;
  hours_per_week?: number | null;
  background_notes?: string | null;
  weak: Array<{ concept_id: string; score: number }>;
  strong: Array<{ concept_id: string; score: number }>;
  notes_by_agent: Array<{
    agent: string;
    count: number;
    notes: Array<{ content: string; kind: string; created_at: string; importance: number }>;
  }>;
  recent_chat: Array<{ agent: string; role: string; content: string; created_at: string }>;
}

interface AttemptRow {
  id: string;
  kind: string;
  score: number | null;
  passed: boolean | null;
  created_at: string;
  grading_status?: string | null;
}

interface AttemptDetail {
  grading_status?: string;
  score?: number | null;
  passed?: boolean | null;
  feedback?: Record<string, unknown> | null;
  questions?: Array<{
    id: string;
    stem: string;
    kind?: string;
    topic?: string;
    options?: Array<{ key: string; text: string }>;
    correct?: string;
    model_answer?: string | null;
    rubric?: string | null;
  }>;
  answers?: Array<{ item_id: string; chosen: string }>;
  item_feedback?: Record<
    string,
    {
      strengths?: string;
      next_fix?: string;
      process_score?: number;
      status?: string;
      logic?: string;
      steps_present?: string;
      steps_skipped?: string;
      material_anchoring?: string;
    }
  >;
  item_scores?: Record<string, number>;
}

interface ItemEdit {
  strengths: string;
  next_fix: string;
  logic: string;
  process_score: string;
}

interface Props {
  studentId: string;
  studentName: string;
  username: string;
  goal: string | null;
  hoursPerWeek: number | null;
  planWeeks: PlanWeekView[];
  planWeekConcepts: string[];
  progress: ProgressView | null;
  memory: MemoryView | null;
  attempts: AttemptRow[];
  notes: Array<{ id: string; kind: string; content: string; created_at: string }>;
}

const TAB_IDS: TabId[] = ['overview', 'plan', 'progress', 'tests', 'memory'];

function parseTab(raw: string | null): TabId {
  if (raw && TAB_IDS.includes(raw as TabId)) return raw as TabId;
  return 'overview';
}

export function EducatorStudentWorkspace({
  studentId,
  studentName,
  username,
  goal,
  hoursPerWeek,
  planWeeks,
  planWeekConcepts,
  progress,
  memory,
  attempts,
  notes,
}: Props) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [tab, setTab] = useState<TabId>(() => parseTab(searchParams.get('tab')));
  const [msg, setMsg] = useState<string | null>(null);

  const [reason, setReason] = useState('');
  const [goalEdit, setGoalEdit] = useState(goal ?? '');
  const [hoursEdit, setHoursEdit] = useState(String(hoursPerWeek ?? ''));
  const [priority, setPriority] = useState(planWeekConcepts.join(', '));

  const [note, setNote] = useState('');
  const [concern, setConcern] = useState(false);

  const initialAttempt =
    searchParams.get('attempt') ??
    attempts.find((a) => a.grading_status === 'needs_human')?.id ??
    attempts[0]?.id ??
    '';

  const [gradeAttemptId, setGradeAttemptId] = useState(initialAttempt);
  const [feedback, setFeedback] = useState('');
  const [score, setScore] = useState('0.75');
  const [passed, setPassed] = useState(true);
  const [reopen, setReopen] = useState(false);
  const [review, setReview] = useState<AttemptDetail | null>(null);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [itemEdits, setItemEdits] = useState<Record<string, ItemEdit>>({});
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const activeWeek =
    planWeeks.find((w) => w.status === 'active') ?? planWeeks[0] ?? null;

  const needsReview = useMemo(
    () => attempts.filter((a) => a.grading_status === 'needs_human'),
    [attempts],
  );

  const syncUrl = useCallback(
    (nextTab: TabId, attemptId?: string) => {
      const params = new URLSearchParams();
      if (nextTab !== 'overview') params.set('tab', nextTab);
      if (nextTab === 'tests' && attemptId) params.set('attempt', attemptId);
      const qs = params.toString();
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    },
    [pathname, router],
  );

  const loadAttemptReview = useCallback(
    async (attemptId: string) => {
      if (!attemptId) return;
      setReviewLoading(true);
      setReviewError(null);
      try {
        const res = await fetch(
          `/api/educator/students/${studentId}/attempts/${attemptId}`,
        );
        const data = (await res.json()) as {
          attempt?: AttemptDetail;
          error?: string;
        };
        if (!res.ok || !data.attempt) {
          setReview(null);
          setReviewError(data.error ?? 'Failed to load');
          return;
        }
        const a = data.attempt;
        setReview(a);
        if (typeof a.score === 'number') setScore(String(a.score));
        if (typeof a.passed === 'boolean') setPassed(a.passed);
        const teacherFb = a.feedback?.teacher_feedback;
        if (typeof teacherFb === 'string' && teacherFb.trim()) {
          setFeedback(teacherFb);
        }
        const edits: Record<string, ItemEdit> = {};
        for (const q of a.questions ?? []) {
          const fb = a.item_feedback?.[q.id];
          const scored = a.item_scores?.[q.id] ?? fb?.process_score;
          edits[q.id] = {
            strengths: fb?.strengths ?? '',
            next_fix: fb?.next_fix ?? '',
            logic: fb?.logic ?? '',
            process_score:
              typeof scored === 'number' && Number.isFinite(scored) ? String(scored) : '',
          };
        }
        setItemEdits(edits);
      } catch {
        setReview(null);
        setReviewError('Failed to load');
      } finally {
        setReviewLoading(false);
      }
    },
    [studentId],
  );

  function selectTab(next: TabId) {
    setTab(next);
    syncUrl(next, next === 'tests' ? gradeAttemptId : undefined);
  }

  function selectAttempt(attemptId: string) {
    setGradeAttemptId(attemptId);
    setTab('tests');
    syncUrl('tests', attemptId);
    void loadAttemptReview(attemptId);
  }

  useEffect(() => {
    const t = parseTab(searchParams.get('tab'));
    const a = searchParams.get('attempt');
    setTab(t);
    if (a) setGradeAttemptId(a);
    if (t === 'tests') {
      const id = a ?? attempts.find((x) => x.grading_status === 'needs_human')?.id ?? attempts[0]?.id;
      if (id) void loadAttemptReview(id);
    }
  }, [searchParams, loadAttemptReview, attempts]);

  async function savePlan() {
    setMsg(null);
    const res = await fetch('/api/educator/student-action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'plan',
        student_id: studentId,
        reason,
        plan: {
          goal: goalEdit || undefined,
          hours_per_week: hoursEdit ? Number(hoursEdit) : undefined,
          priority_concepts: priority
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean),
        },
      }),
    });
    const data = (await res.json()) as { error?: string };
    setMsg(res.ok ? (isHe ? 'התוכנית עודכנה' : 'Plan updated') : data.error ?? 'Failed');
  }

  async function saveNote() {
    setMsg(null);
    const res = await fetch('/api/educator/student-action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'note',
        student_id: studentId,
        content: note,
        kind: concern ? 'concern' : 'note',
      }),
    });
    const data = (await res.json()) as { error?: string };
    setMsg(res.ok ? (isHe ? 'נשמר' : 'Saved') : data.error ?? 'Failed');
    if (res.ok) setNote('');
  }

  async function gradeTest() {
    setMsg(null);
    const item_feedback: Record<
      string,
      {
        strengths?: string;
        next_fix?: string;
        logic?: string;
        process_score?: number;
        status: string;
      }
    > = {};
    const item_scores: Record<string, number> = {};
    for (const [id, edit] of Object.entries(itemEdits)) {
      const processScore = edit.process_score.trim()
        ? Number(edit.process_score)
        : undefined;
      item_feedback[id] = {
        strengths: edit.strengths.trim() || undefined,
        next_fix: edit.next_fix.trim() || undefined,
        logic: edit.logic.trim() || undefined,
        process_score:
          typeof processScore === 'number' && Number.isFinite(processScore)
            ? Math.min(1, Math.max(0, processScore))
            : undefined,
        status: 'graded',
      };
      if (typeof processScore === 'number' && Number.isFinite(processScore)) {
        item_scores[id] = Math.min(1, Math.max(0, processScore));
      }
    }
    const res = await fetch('/api/educator/test-grade', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: studentId,
        attempt_id: gradeAttemptId,
        feedback,
        reason: feedback,
        score: reopen ? undefined : Number(score),
        passed: reopen ? undefined : passed,
        reopen,
        item_feedback,
        item_scores,
      }),
    });
    const data = (await res.json()) as { error?: string };
    setMsg(res.ok ? (isHe ? 'המבחן עודכן' : 'Test updated') : data.error ?? 'Failed');
    if (res.ok) void loadAttemptReview(gradeAttemptId);
  }

  async function disconnect() {
    if (!window.confirm(isHe ? 'לבטל את החיבור?' : 'Disconnect from this student?')) return;
    await fetch('/api/educator/student-action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'disconnect', student_id: studentId }),
    });
    window.location.href = '/educator';
  }

  const tabs = [
    { id: 'overview' as const, label: isHe ? 'סקירה' : 'Overview' },
    { id: 'plan' as const, label: isHe ? 'תוכנית' : 'Plan' },
    { id: 'progress' as const, label: isHe ? 'התקדמות' : 'Progress' },
    { id: 'tests' as const, label: isHe ? 'מבחנים' : 'Tests' },
    { id: 'memory' as const, label: isHe ? 'זיכרון' : 'Memory' },
  ];

  const maxHeat = Math.max(1, ...(progress?.daily_activity.map((d) => d.count) ?? [1]));
  const masterySorted = [...(progress?.concepts ?? [])].sort((a, b) => a.score - b.score);
  const weakMastery = masterySorted.filter((c) => c.score < 0.5).slice(0, 8);
  const strongMastery = [...masterySorted].reverse().filter((c) => c.score >= 0.7).slice(0, 8);

  const statusLabel = (status: string | null | undefined) => {
    switch (status) {
      case 'needs_human':
        return isHe ? 'דורש בדיקה' : 'Needs review';
      case 'pending':
      case 'grading':
        return isHe ? 'בבדיקה אוטומטית' : 'Auto-grading';
      case 'reopened':
        return isHe ? 'נפתח מחדש' : 'Reopened';
      case 'complete':
        return isHe ? 'שוחרר' : 'Released';
      case 'failed':
        return isHe ? 'נכשל' : 'Failed';
      default:
        return status ?? '—';
    }
  };

  return (
    <div className="space-y-6" dir={isHe ? 'rtl' : 'ltr'}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link href="/educator" className="text-sm text-muted-foreground hover:underline">
            {isHe ? '← חזרה לתלמידים' : '← Back to students'}
          </Link>
          <h1 className="mt-2 font-display text-2xl font-bold">{studentName}</h1>
          <p className="font-mono text-sm text-muted-foreground">@{username}</p>
        </div>
        <Button type="button" variant="outline" size="sm" onClick={() => void disconnect()}>
          {isHe ? 'נתק חיבור' : 'Disconnect'}
        </Button>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-border pb-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => selectTab(t.id)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
              tab === t.id ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-surface-2'
            }`}
          >
            {t.label}
            {t.id === 'tests' && needsReview.length > 0 ? (
              <span className="ms-1.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-amber-500/20 px-1.5 text-[10px] font-semibold text-amber-800 dark:text-amber-300">
                {needsReview.length}
              </span>
            ) : null}
          </button>
        ))}
      </div>

      {msg ? <p className="text-sm text-muted-foreground">{msg}</p> : null}

      {tab === 'overview' ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <section className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'מצב כללי' : 'At a glance'}</h2>
            <dl className="mt-3 grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-muted-foreground">{isHe ? 'רצף' : 'Streak'}</dt>
                <dd className="text-xl font-semibold tabular-nums">{progress?.streak_days ?? 0}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">{isHe ? 'שליטה ממוצעת' : 'Avg mastery'}</dt>
                <dd className="text-xl font-semibold tabular-nums">
                  {Math.round((progress?.avg_mastery ?? 0) * 100)}%
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">{isHe ? 'מטרה' : 'Goal'}</dt>
                <dd className="mt-1 line-clamp-3">{goal || '—'}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">{isHe ? 'שעות/שבוע' : 'Hours/week'}</dt>
                <dd className="text-xl font-semibold tabular-nums">{hoursPerWeek ?? '—'}</dd>
              </div>
            </dl>
          </section>
          <section className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'מיקוד השבוע הפעיל' : 'Active week focus'}</h2>
            <p className="mt-1 text-xs text-muted-foreground">
              {activeWeek
                ? `${isHe ? 'שבוע' : 'Week'} ${activeWeek.week_number} · ${activeWeek.status}`
                : isHe
                  ? 'אין תוכנית'
                  : 'No plan'}
            </p>
            {activeWeek?.quiz_due_at ? (
              <p className="mt-1 text-xs text-muted-foreground">
                {isHe ? 'שער עד' : 'Gate due'}{' '}
                {new Date(activeWeek.quiz_due_at).toLocaleDateString(isHe ? 'he-IL' : 'en-US')}
              </p>
            ) : null}
            <div className="mt-3 flex flex-wrap gap-2">
              {(activeWeek?.concepts ?? []).length === 0 ? (
                <span className="text-sm text-muted-foreground">{isHe ? 'אין' : 'None'}</span>
              ) : (
                activeWeek!.concepts.map((c) => (
                  <span key={c.concept_id} className="rounded-full bg-surface-2 px-2 py-1 text-xs">
                    {c.name || c.concept_id}
                  </span>
                ))
              )}
            </div>
          </section>
          <section className="rounded-xl border border-border p-4 lg:col-span-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="font-semibold">
                {isHe ? 'פריטים לבדיקה' : 'Open grading'}
              </h2>
              {needsReview.length > 0 ? (
                <Button type="button" size="sm" variant="outline" onClick={() => selectTab('tests')}>
                  {isHe ? 'עבור למבחנים' : 'Go to Tests'}
                </Button>
              ) : null}
            </div>
            {needsReview.length === 0 ? (
              <p className="mt-2 text-sm text-muted-foreground">
                {isHe ? 'אין מבחנים שממתינים לבדיקת מורה.' : 'No attempts waiting for teacher review.'}
              </p>
            ) : (
              <ul className="mt-3 space-y-2">
                {needsReview.map((a) => (
                  <li key={a.id}>
                    <button
                      type="button"
                      onClick={() => selectAttempt(a.id)}
                      className="flex w-full flex-wrap items-center justify-between gap-2 rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-start text-sm hover:border-amber-500/50"
                    >
                      <span>
                        {a.kind} ·{' '}
                        {new Date(a.created_at).toLocaleDateString(isHe ? 'he-IL' : 'en-US')}
                      </span>
                      <span className="text-amber-800 dark:text-amber-300">
                        {isHe ? 'דורש בדיקה' : 'Needs review'}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      ) : null}

      {tab === 'plan' ? (
        <div className="space-y-4">
          <section className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'תוכנית נוכחית (קריאה)' : 'Current plan (read)'}</h2>
            {planWeeks.length === 0 ? (
              <p className="mt-2 text-sm text-muted-foreground">
                {isHe ? 'לתלמיד אין תוכנית עדיין.' : 'Student has no plan yet.'}
              </p>
            ) : (
              <ul className="mt-3 space-y-3">
                {planWeeks.map((w) => (
                  <li key={w.week_number} className="rounded-lg border border-border/60 px-3 py-2 text-sm">
                    <div className="flex flex-wrap justify-between gap-2">
                      <span className="font-medium">
                        {isHe ? 'שבוע' : 'Week'} {w.week_number} · {w.status}
                      </span>
                      <span className="text-muted-foreground">
                        {w.quiz_due_at
                          ? `${isHe ? 'שער עד' : 'Gate due'} ${new Date(w.quiz_due_at).toLocaleDateString(isHe ? 'he-IL' : 'en-US')}`
                          : '—'}
                      </span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {w.concepts.map((c) => (
                        <span key={c.concept_id} className="rounded bg-surface-2 px-2 py-0.5 text-xs">
                          {c.name || c.concept_id}
                          {c.mastery != null ? ` · ${Math.round(c.mastery * 100)}%` : ''}
                        </span>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="space-y-4 rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'עריכת תוכנית' : 'Edit plan'}</h2>
            <p className="text-sm text-muted-foreground">
              {isHe
                ? 'השינוי נשמר מיד. חובה לציין סיבה — התלמיד יקבל התראה והזיכרון יתעדכן.'
                : 'Changes apply immediately. A reason is required — the student is notified and memory updates.'}
            </p>
            <label className="block space-y-1 text-sm">
              <span>{isHe ? 'סיבה (חובה)' : 'Reason (required)'}</span>
              <Input value={reason} onChange={(e) => setReason(e.target.value)} required />
            </label>
            <label className="block space-y-1 text-sm">
              <span>{isHe ? 'מטרה' : 'Goal'}</span>
              <Input value={goalEdit} onChange={(e) => setGoalEdit(e.target.value)} />
            </label>
            <label className="block space-y-1 text-sm">
              <span>{isHe ? 'שעות בשבוע' : 'Hours / week'}</span>
              <Input value={hoursEdit} onChange={(e) => setHoursEdit(e.target.value)} type="number" min={1} />
            </label>
            <label className="block space-y-1 text-sm">
              <span>{isHe ? 'מושגים בעדיפות (מופרדים בפסיק)' : 'Priority concepts (comma-separated)'}</span>
              <Input value={priority} onChange={(e) => setPriority(e.target.value)} dir="ltr" />
            </label>
            <Button type="button" onClick={() => void savePlan()} disabled={reason.trim().length < 3}>
              {isHe ? 'שמור תוכנית' : 'Save plan'}
            </Button>
          </section>
        </div>
      ) : null}

      {tab === 'progress' ? (
        <div className="space-y-4">
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {[
              { label: isHe ? 'רצף ימים' : 'Streak', value: progress?.streak_days ?? 0 },
              {
                label: isHe ? 'שיעורים' : 'Lessons',
                value: progress?.lessons_completed ?? 0,
              },
              {
                label: isHe ? 'שליטה ממוצעת' : 'Avg mastery',
                value: `${Math.round((progress?.avg_mastery ?? 0) * 100)}%`,
              },
              {
                label: isHe ? 'אטומים' : 'Atoms practiced',
                value: progress?.atoms_practiced ?? 0,
              },
              {
                label: isHe ? 'רמה' : 'Level',
                value: progress?.level ?? '—',
              },
              {
                label: 'XP',
                value: progress?.total_xp ?? progress?.total_minutes ?? 0,
              },
            ].map((c) => (
              <div key={c.label} className="rounded-xl border border-border p-4">
                <p className="text-xs text-muted-foreground">{c.label}</p>
                <p className="mt-1 text-2xl font-semibold tabular-nums">{c.value}</p>
              </div>
            ))}
          </section>
          <section className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'פעילות 30 יום' : '30-day activity'}</h2>
            <div className="mt-3 flex flex-wrap gap-1" aria-hidden>
              {(progress?.daily_activity ?? []).map((d) => {
                const intensity = d.count / maxHeat;
                return (
                  <span
                    key={d.date}
                    title={`${d.date}: ${d.count}`}
                    className="h-4 w-4 rounded-sm"
                    style={{
                      backgroundColor:
                        d.count === 0
                          ? 'hsl(var(--muted))'
                          : `hsl(var(--primary) / ${0.25 + intensity * 0.75})`,
                    }}
                  />
                );
              })}
            </div>
            {(progress?.daily_activity ?? []).length === 0 ? (
              <p className="mt-2 text-sm text-muted-foreground">
                {isHe ? 'אין פעילות רשומה.' : 'No activity recorded.'}
              </p>
            ) : null}
          </section>
          <div className="grid gap-4 lg:grid-cols-2">
            <section className="rounded-xl border border-border p-4">
              <h2 className="font-semibold">{isHe ? 'חלש יחסית' : 'Needs work'}</h2>
              <ul className="mt-3 space-y-2 text-sm">
                {weakMastery.length === 0 ? (
                  <li className="text-muted-foreground">{isHe ? 'אין נתונים' : 'No data'}</li>
                ) : (
                  weakMastery.map((m) => (
                    <li key={m.concept_id} className="flex justify-between gap-2">
                      <span className="min-w-0 truncate">{m.title}</span>
                      <span className="shrink-0 tabular-nums text-amber-700 dark:text-amber-400">
                        {Math.round(m.score * 100)}%
                      </span>
                    </li>
                  ))
                )}
              </ul>
            </section>
            <section className="rounded-xl border border-border p-4">
              <h2 className="font-semibold">{isHe ? 'חזק' : 'Strong'}</h2>
              <ul className="mt-3 space-y-2 text-sm">
                {strongMastery.length === 0 ? (
                  <li className="text-muted-foreground">{isHe ? 'אין נתונים' : 'No data'}</li>
                ) : (
                  strongMastery.map((m) => (
                    <li key={m.concept_id} className="flex justify-between gap-2">
                      <span className="min-w-0 truncate">{m.title}</span>
                      <span className="shrink-0 tabular-nums text-emerald-700 dark:text-emerald-400">
                        {Math.round(m.score * 100)}%
                      </span>
                    </li>
                  ))
                )}
              </ul>
            </section>
          </div>
          <section className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'כל המושגים' : 'All concepts'}</h2>
            <ul className="mt-3 max-h-72 space-y-2 overflow-auto text-sm">
              {(progress?.concepts ?? []).length === 0 ? (
                <li className="text-muted-foreground">{isHe ? 'אין נתונים' : 'No data'}</li>
              ) : (
                masterySorted.map((m) => (
                  <li key={m.concept_id} className="flex items-center justify-between gap-3">
                    <span className="min-w-0 truncate">{m.title}</span>
                    <div className="flex w-28 shrink-0 items-center gap-2">
                      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-2">
                        <div
                          className="h-full rounded-full bg-primary"
                          style={{ width: `${Math.round(m.score * 100)}%` }}
                        />
                      </div>
                      <span className="w-10 text-end tabular-nums">{Math.round(m.score * 100)}%</span>
                    </div>
                  </li>
                ))
              )}
            </ul>
          </section>
        </div>
      ) : null}

      {tab === 'tests' ? (
        <div className="grid gap-4 lg:grid-cols-[minmax(0,240px)_minmax(0,1fr)]">
          <aside className="rounded-xl border border-border p-3">
            <h2 className="px-1 text-sm font-semibold">{isHe ? 'מבחנים' : 'Attempts'}</h2>
            {attempts.length === 0 ? (
              <p className="mt-3 px-1 text-sm text-muted-foreground">
                {isHe ? 'אין מבחנים עדיין.' : 'No attempts yet.'}
              </p>
            ) : (
              <ul className="mt-2 max-h-[70vh] space-y-1 overflow-auto">
                {attempts.map((a) => {
                  const selected = a.id === gradeAttemptId;
                  return (
                    <li key={a.id}>
                      <button
                        type="button"
                        onClick={() => selectAttempt(a.id)}
                        className={`w-full rounded-lg px-2.5 py-2 text-start text-sm transition ${
                          selected
                            ? 'bg-primary text-primary-foreground'
                            : 'hover:bg-surface-2'
                        }`}
                      >
                        <span className="block font-medium">{a.kind}</span>
                        <span
                          className={`mt-0.5 block text-xs ${
                            selected ? 'text-primary-foreground/80' : 'text-muted-foreground'
                          }`}
                        >
                          {new Date(a.created_at).toLocaleDateString(isHe ? 'he-IL' : 'en-US')}
                          {' · '}
                          {a.score == null ? '—' : `${Math.round(a.score * 100)}%`}
                          {a.grading_status === 'needs_human'
                            ? isHe
                              ? ' · בדיקה'
                              : ' · review'
                            : ''}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </aside>

          <section className="space-y-4 rounded-xl border border-border p-4">
            {!gradeAttemptId ? (
              <p className="text-sm text-muted-foreground">
                {isHe ? 'בחרו מבחן מהרשימה.' : 'Select an attempt from the list.'}
              </p>
            ) : reviewLoading ? (
              <p className="text-sm text-muted-foreground">{isHe ? 'טוען סקירה…' : 'Loading review…'}</p>
            ) : reviewError ? (
              <p className="text-sm text-destructive">{reviewError}</p>
            ) : review ? (
              <>
                <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border pb-3">
                  <div>
                    <h2 className="font-semibold">{isHe ? 'סקירת בדיקה' : 'Split review'}</h2>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {statusLabel(review.grading_status)}
                      {' · '}
                      {review.score == null ? '—' : `${Math.round(review.score * 100)}%`}
                      {review.passed == null ? '' : review.passed ? (isHe ? ' · עבר' : ' · passed') : isHe ? ' · לא עבר' : ' · failed'}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  {(review.questions ?? []).map((q, idx) => {
                    const ans = review.answers?.find((x) => x.item_id === q.id)?.chosen ?? '';
                    const fb = review.item_feedback?.[q.id];
                    const edit = itemEdits[q.id] ?? {
                      strengths: '',
                      next_fix: '',
                      logic: '',
                      process_score: '',
                    };
                    const chosenKey = ans.trim().toUpperCase();
                    const correctKey = (q.correct ?? '').trim().toUpperCase();
                    const hasOptions = (q.options?.length ?? 0) > 0;
                    return (
                      <article
                        key={q.id}
                        className="overflow-hidden rounded-lg border border-border/70"
                      >
                        <header className="border-b border-border/60 bg-surface-1/40 px-3 py-2 text-sm font-medium">
                          {isHe ? 'שאלה' : 'Question'} {idx + 1}
                          {q.kind ? (
                            <span className="ms-2 text-xs font-normal text-muted-foreground">
                              {q.kind}
                            </span>
                          ) : null}
                          {q.topic ? (
                            <span className="ms-2 text-xs font-normal text-muted-foreground">
                              · {q.topic}
                            </span>
                          ) : null}
                        </header>
                        <div className="border-b border-border/40 px-3 py-2 text-sm">
                          <MarkdownMath dir={isHe ? 'rtl' : 'ltr'}>{q.stem}</MarkdownMath>
                        </div>
                        <div className="grid gap-0 md:grid-cols-2">
                          <div className="border-b border-border/40 p-3 md:border-b-0 md:border-e">
                            <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                              {isHe ? 'שאלה + תשובת התלמיד' : 'Question + student answer'}
                            </h3>
                            {hasOptions ? (
                              <ul className="mt-3 space-y-1.5 text-sm">
                                {(q.options ?? []).map((opt) => {
                                  const key = opt.key.toUpperCase();
                                  const isChosen = key === chosenKey;
                                  const isCorrect = Boolean(correctKey) && key === correctKey;
                                  return (
                                    <li
                                      key={opt.key}
                                      className={`rounded-md border px-2.5 py-1.5 ${
                                        isCorrect
                                          ? 'border-emerald-500/40 bg-emerald-500/10'
                                          : isChosen
                                            ? 'border-amber-500/40 bg-amber-500/10'
                                            : 'border-border/50'
                                      }`}
                                    >
                                      <span className="font-mono text-xs me-2">{opt.key}.</span>
                                      <MarkdownMath dir={isHe ? 'rtl' : 'ltr'}>{opt.text}</MarkdownMath>
                                      <span className="ms-2 text-[10px] text-muted-foreground">
                                        {isChosen
                                          ? isHe
                                            ? '(נבחר)'
                                            : '(chosen)'
                                          : ''}
                                        {isCorrect
                                          ? isHe
                                            ? ' (נכון)'
                                            : ' (correct)'
                                          : ''}
                                      </span>
                                    </li>
                                  );
                                })}
                              </ul>
                            ) : (
                              <div className="mt-3 rounded-md bg-surface-1/50 p-2.5 text-sm">
                                <p className="text-xs text-muted-foreground mb-1">
                                  {isHe ? 'תשובה פתוחה' : 'Open answer'}
                                </p>
                                <MarkdownMath dir={isHe ? 'rtl' : 'ltr'}>
                                  {ans.trim() || (isHe ? '(ריק)' : '(empty)')}
                                </MarkdownMath>
                              </div>
                            )}
                            {hasOptions &&
                            ans &&
                            !(q.options ?? []).some((o) => o.key.toUpperCase() === chosenKey) ? (
                              <p className="mt-2 text-xs text-muted-foreground whitespace-pre-wrap">
                                {isHe ? 'ערך שנשמר:' : 'Stored value:'} {ans}
                              </p>
                            ) : null}
                            {q.correct ? (
                              <p className="mt-3 text-xs text-muted-foreground" dir="ltr">
                                {isHe ? 'מפתח:' : 'Key:'} {q.correct}
                              </p>
                            ) : null}
                            {q.model_answer ? (
                              <div className="mt-2 text-xs text-muted-foreground">
                                <p className="font-medium">
                                  {isHe ? 'תשובת מודל' : 'Model answer'}
                                </p>
                                <div className="mt-1 whitespace-pre-wrap">
                                  <MarkdownMath dir={isHe ? 'rtl' : 'ltr'}>
                                    {String(q.model_answer)}
                                  </MarkdownMath>
                                </div>
                              </div>
                            ) : null}
                            {q.rubric ? (
                              <div className="mt-2 text-xs text-muted-foreground">
                                <p className="font-medium">{isHe ? 'רובריקה' : 'Rubric'}</p>
                                <p className="mt-1 whitespace-pre-wrap">{String(q.rubric)}</p>
                              </div>
                            ) : null}
                            {fb?.steps_present || fb?.steps_skipped || fb?.material_anchoring ? (
                              <dl className="mt-3 space-y-1 text-xs text-muted-foreground">
                                {fb.steps_present ? (
                                  <div>
                                    <dt className="font-medium">
                                      {isHe ? 'צעדים שנמצאו' : 'Steps present'}
                                    </dt>
                                    <dd className="whitespace-pre-wrap">{fb.steps_present}</dd>
                                  </div>
                                ) : null}
                                {fb.steps_skipped ? (
                                  <div>
                                    <dt className="font-medium">
                                      {isHe ? 'צעדים שדולגו' : 'Steps skipped'}
                                    </dt>
                                    <dd className="whitespace-pre-wrap">{fb.steps_skipped}</dd>
                                  </div>
                                ) : null}
                                {fb.material_anchoring ? (
                                  <div>
                                    <dt className="font-medium">
                                      {isHe ? 'עיגון בחומר' : 'Material anchoring'}
                                    </dt>
                                    <dd className="whitespace-pre-wrap">{fb.material_anchoring}</dd>
                                  </div>
                                ) : null}
                              </dl>
                            ) : null}
                          </div>
                          <div className="space-y-3 p-3">
                            <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                              {isHe ? 'ניתוח גרדר → עריכת מורה' : 'Grader draft → teacher edit'}
                            </h3>
                            <p className="text-[11px] text-muted-foreground">
                              {isHe
                                ? 'ערכו את טיוטת הגרדר. השמירה מחליפה את הניתוח לתלמיד.'
                                : 'Edit the Grader draft. Saving replaces the analysis shown to the student.'}
                            </p>
                            <label className="block space-y-1 text-xs">
                              <span className="text-muted-foreground">
                                {isHe ? 'ציון פריט (0–1)' : 'Item score (0–1)'}
                              </span>
                              <Input
                                className="h-8"
                                value={edit.process_score}
                                onChange={(e) =>
                                  setItemEdits((prev) => ({
                                    ...prev,
                                    [q.id]: { ...edit, process_score: e.target.value },
                                  }))
                                }
                                type="number"
                                step="0.01"
                                min={0}
                                max={1}
                                disabled={reopen}
                              />
                            </label>
                            <label className="block space-y-1 text-xs">
                              <span className="text-muted-foreground">
                                {isHe ? 'חוזקות' : 'Strengths'}
                              </span>
                              <textarea
                                className="w-full rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
                                rows={2}
                                value={edit.strengths}
                                onChange={(e) =>
                                  setItemEdits((prev) => ({
                                    ...prev,
                                    [q.id]: { ...edit, strengths: e.target.value },
                                  }))
                                }
                              />
                            </label>
                            <label className="block space-y-1 text-xs">
                              <span className="text-muted-foreground">
                                {isHe ? 'לתיקון / ניתוח' : 'Next fix / analysis'}
                              </span>
                              <textarea
                                className="w-full rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
                                rows={3}
                                value={edit.next_fix}
                                onChange={(e) =>
                                  setItemEdits((prev) => ({
                                    ...prev,
                                    [q.id]: { ...edit, next_fix: e.target.value },
                                  }))
                                }
                              />
                            </label>
                            <label className="block space-y-1 text-xs">
                              <span className="text-muted-foreground">
                                {isHe ? 'היגיון' : 'Logic notes'}
                              </span>
                              <textarea
                                className="w-full rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
                                rows={2}
                                value={edit.logic}
                                onChange={(e) =>
                                  setItemEdits((prev) => ({
                                    ...prev,
                                    [q.id]: { ...edit, logic: e.target.value },
                                  }))
                                }
                              />
                            </label>
                          </div>
                        </div>
                      </article>
                    );
                  })}
                </div>

                <div className="space-y-3 border-t border-border pt-4">
                  <h3 className="text-sm font-medium">
                    {isHe ? 'דריסת מורה' : 'Teacher override'}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    {isHe
                      ? 'עדכון ציון/עבר משחרר את המבחן לתלמיד ומתאם את שערי השבוע.'
                      : 'Updating score/pass releases the attempt to the student and syncs week gates.'}
                  </p>
                  <textarea
                    className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                    rows={3}
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    placeholder={isHe ? 'משוב / סיבה (חובה)…' : 'Feedback / reason (required)…'}
                  />
                  <div className="flex flex-wrap items-center gap-3">
                    <label className="flex items-center gap-2 text-sm">
                      <span className="text-muted-foreground">{isHe ? 'ציון' : 'Score'}</span>
                      <Input
                        className="w-28"
                        value={score}
                        onChange={(e) => setScore(e.target.value)}
                        type="number"
                        step="0.01"
                        min={0}
                        max={1}
                        disabled={reopen}
                      />
                    </label>
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={passed}
                        onChange={(e) => setPassed(e.target.checked)}
                        disabled={reopen}
                      />
                      {isHe ? 'עבר' : 'Passed'}
                    </label>
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={reopen}
                        onChange={(e) => setReopen(e.target.checked)}
                      />
                      {isHe ? 'פתח מחדש' : 'Reopen'}
                    </label>
                    <Button
                      type="button"
                      onClick={() => void gradeTest()}
                      disabled={feedback.trim().length < 2}
                    >
                      {isHe ? 'שמור בדיקה' : 'Save grading'}
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">
                {isHe ? 'בחרו מבחן מהרשימה.' : 'Select an attempt from the list.'}
              </p>
            )}
          </section>
        </div>
      ) : null}

      {tab === 'memory' ? (
        <section className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-xl border border-border p-4">
              <h2 className="font-semibold">{isHe ? 'פרסונה משותפת' : 'Shared persona'}</h2>
              <pre className="mt-3 max-h-80 overflow-auto whitespace-pre-wrap rounded-lg bg-surface-1/50 p-3 text-xs leading-relaxed">
                {memory?.persona?.trim() || (isHe ? 'אין פרסונה עדיין' : 'No persona yet')}
              </pre>
            </div>
            <div className="rounded-xl border border-border p-4">
              <h2 className="font-semibold">{isHe ? 'פרופיל' : 'Profile'}</h2>
              <dl className="mt-3 space-y-2 text-sm">
                <div>
                  <dt className="text-xs text-muted-foreground">{isHe ? 'מטרה' : 'Goal'}</dt>
                  <dd>{memory?.profile_goal || goal || '—'}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted-foreground">{isHe ? 'מקצועות' : 'Subjects'}</dt>
                  <dd>{(memory?.subjects ?? []).join(', ') || '—'}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted-foreground">{isHe ? 'סגנון' : 'Style'}</dt>
                  <dd>{memory?.preferred_style || '—'}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted-foreground">{isHe ? 'שעות/שבוע' : 'Hours/week'}</dt>
                  <dd>{memory?.hours_per_week ?? hoursPerWeek ?? '—'}</dd>
                </div>
                {memory?.background_notes ? (
                  <div>
                    <dt className="text-xs text-muted-foreground">
                      {isHe ? 'הערות רקע' : 'Background'}
                    </dt>
                    <dd className="whitespace-pre-wrap text-muted-foreground">
                      {memory.background_notes}
                    </dd>
                  </div>
                ) : null}
              </dl>
              <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
                <div>
                  <p className="font-medium text-muted-foreground">{isHe ? 'חלש' : 'Weak'}</p>
                  <ul className="mt-1 space-y-1">
                    {(memory?.weak ?? []).slice(0, 8).map((c) => (
                      <li key={c.concept_id} className="font-mono">
                        {c.concept_id} · {Math.round(c.score * 100)}%
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">{isHe ? 'חזק' : 'Strong'}</p>
                  <ul className="mt-1 space-y-1">
                    {(memory?.strong ?? []).slice(0, 8).map((c) => (
                      <li key={c.concept_id} className="font-mono">
                        {c.concept_id} · {Math.round(c.score * 100)}%
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'הערות סוכנים (קריאה)' : 'Agent notes (read-only)'}</h2>
            <ul className="mt-3 space-y-2">
              {(memory?.notes_by_agent ?? []).map((n) => {
                const open = expandedAgent === n.agent;
                return (
                  <li key={n.agent} className="rounded-lg border border-border/60">
                    <button
                      type="button"
                      className="flex w-full items-center justify-between gap-2 px-3 py-2 text-start text-sm"
                      onClick={() => setExpandedAgent(open ? null : n.agent)}
                    >
                      <span>
                        <span className="font-medium capitalize">{n.agent}</span>
                        <span className="ms-2 text-xs text-muted-foreground">({n.count})</span>
                      </span>
                      <span className="text-xs text-muted-foreground">{open ? '−' : '+'}</span>
                    </button>
                    {open ? (
                      <ul className="space-y-2 border-t border-border/50 px-3 py-2">
                        {n.notes.length === 0 ? (
                          <li className="text-xs text-muted-foreground">
                            {isHe ? 'אין הערות' : 'No notes'}
                          </li>
                        ) : (
                          n.notes.map((noteItem, i) => (
                            <li
                              key={`${n.agent}-${i}-${noteItem.created_at}`}
                              className="rounded bg-surface-1/40 px-2 py-1.5 text-xs"
                            >
                              <div className="flex flex-wrap gap-2 text-[10px] text-muted-foreground">
                                <span>{noteItem.kind}</span>
                                <span>
                                  {new Date(noteItem.created_at).toLocaleString(
                                    isHe ? 'he-IL' : 'en-US',
                                  )}
                                </span>
                                <span>imp {noteItem.importance}</span>
                              </div>
                              <p className="mt-1 whitespace-pre-wrap">{noteItem.content}</p>
                            </li>
                          ))
                        )}
                      </ul>
                    ) : n.notes[0] ? (
                      <p className="border-t border-border/40 px-3 pb-2 text-xs text-muted-foreground line-clamp-2">
                        {n.notes[0].content}
                      </p>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'צ׳אט אחרון' : 'Recent chat'}</h2>
            <ul className="mt-3 max-h-80 space-y-2 overflow-auto">
              {(memory?.recent_chat ?? []).length === 0 ? (
                <li className="text-sm text-muted-foreground">
                  {isHe ? 'אין הודעות אחרונות.' : 'No recent turns.'}
                </li>
              ) : (
                (memory?.recent_chat ?? []).map((c, i) => (
                  <li
                    key={`${c.created_at}-${i}`}
                    className="rounded-lg bg-surface-1/40 px-3 py-2 text-xs"
                  >
                    <div className="flex flex-wrap gap-2 text-[10px] text-muted-foreground">
                      <span className="font-medium text-foreground">
                        {c.agent}/{c.role}
                      </span>
                      <span>
                        {new Date(c.created_at).toLocaleString(isHe ? 'he-IL' : 'en-US')}
                      </span>
                    </div>
                    <p className="mt-1 whitespace-pre-wrap leading-relaxed">{c.content}</p>
                  </li>
                ))
              )}
            </ul>
          </div>

          <div className="space-y-3 rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'הערות מורה' : 'Teacher notes'}</h2>
            <p className="text-xs text-muted-foreground">
              {isHe
                ? 'ניתן לכתוב הערות או חששות בלבד — לא לערוך פרסונה או הערות סוכנים.'
                : 'Write notes or concerns only — persona and agent notes are read-only.'}
            </p>
            <ul className="space-y-2 text-sm">
              {notes.length === 0 ? (
                <li className="text-muted-foreground">{isHe ? 'אין הערות עדיין.' : 'No notes yet.'}</li>
              ) : (
                notes.map((n) => (
                  <li key={n.id} className="rounded-lg border border-border/60 px-3 py-2">
                    <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                      <span className={n.kind === 'concern' ? 'text-amber-700 dark:text-amber-400' : ''}>
                        {n.kind}
                      </span>
                      <span>
                        {new Date(n.created_at).toLocaleString(isHe ? 'he-IL' : 'en-US')}
                      </span>
                    </div>
                    <p className="mt-1 whitespace-pre-wrap">{n.content}</p>
                  </li>
                ))
              )}
            </ul>
            <textarea
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
              rows={3}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder={isHe ? 'הערה חדשה…' : 'New note…'}
            />
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={concern} onChange={(e) => setConcern(e.target.checked)} />
              {isHe ? 'סמן כחשש (התראה לתלמיד)' : 'Mark as concern (notifies student)'}
            </label>
            <Button type="button" onClick={() => void saveNote()} disabled={note.trim().length < 2}>
              {isHe ? 'הוסף הערה' : 'Add note'}
            </Button>
          </div>
        </section>
      ) : null}
    </div>
  );
}
