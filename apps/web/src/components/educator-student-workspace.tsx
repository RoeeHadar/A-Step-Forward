'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { useI18n } from '@/providers/i18n-provider';

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
  weak: Array<{ concept_id: string; score: number }>;
  strong: Array<{ concept_id: string; score: number }>;
  notes_by_agent: Array<{ agent: string; count: number; preview: string | null }>;
  recent_chat: Array<{ agent: string; role: string; content: string; created_at: string }>;
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
  attempts: Array<{
    id: string;
    kind: string;
    score: number | null;
    passed: boolean | null;
    created_at: string;
  }>;
  notes: Array<{ id: string; kind: string; content: string; created_at: string }>;
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
  const [tab, setTab] = useState<'overview' | 'plan' | 'progress' | 'tests' | 'memory'>('overview');
  const [msg, setMsg] = useState<string | null>(null);

  const [reason, setReason] = useState('');
  const [goalEdit, setGoalEdit] = useState(goal ?? '');
  const [hoursEdit, setHoursEdit] = useState(String(hoursPerWeek ?? ''));
  const [priority, setPriority] = useState(planWeekConcepts.join(', '));

  const [note, setNote] = useState('');
  const [concern, setConcern] = useState(false);

  const [gradeAttemptId, setGradeAttemptId] = useState(attempts[0]?.id ?? '');
  const [feedback, setFeedback] = useState('');
  const [score, setScore] = useState('0.75');
  const [passed, setPassed] = useState(true);
  const [reopen, setReopen] = useState(false);

  const activeWeek =
    planWeeks.find((w) => w.status === 'active') ?? planWeeks[0] ?? null;

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
      }),
    });
    const data = (await res.json()) as { error?: string };
    setMsg(res.ok ? (isHe ? 'המבחן עודכן' : 'Test updated') : data.error ?? 'Failed');
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
            onClick={() => setTab(t.id)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
              tab === t.id ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-surface-2'
            }`}
          >
            {t.label}
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
                <dd className="mt-1 line-clamp-3">{goal || (isHe ? '—' : '—')}</dd>
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
                ? 'חובה לציין סיבה — התלמיד יקבל התראה והזיכרון יתעדכן.'
                : 'A reason is required — the student is notified and memory updates.'}
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
            <Button type="button" onClick={() => void savePlan()}>
              {isHe ? 'שמור תוכנית' : 'Save plan'}
            </Button>
          </section>
        </div>
      ) : null}

      {tab === 'progress' ? (
        <div className="space-y-4">
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: isHe ? 'רצף ימים' : 'Streak', value: progress?.streak_days ?? 0 },
              {
                label: isHe ? 'שיעורים שהושלמו' : 'Lessons done',
                value: progress?.lessons_completed ?? 0,
              },
              {
                label: isHe ? 'שליטה ממוצעת' : 'Avg mastery',
                value: `${Math.round((progress?.avg_mastery ?? 0) * 100)}%`,
              },
              {
                label: isHe ? 'XP' : 'XP',
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
          </section>
          <section className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'מושגים' : 'Concepts'}</h2>
            <ul className="mt-3 space-y-2 text-sm">
              {(progress?.concepts ?? []).length === 0 ? (
                <li className="text-muted-foreground">{isHe ? 'אין נתונים' : 'No data'}</li>
              ) : (
                (progress?.concepts ?? []).map((m) => (
                  <li key={m.concept_id} className="flex justify-between gap-2">
                    <span>{m.title}</span>
                    <span className="tabular-nums">{Math.round(m.score * 100)}%</span>
                  </li>
                ))
              )}
            </ul>
          </section>
        </div>
      ) : null}

      {tab === 'tests' ? (
        <section className="space-y-4 rounded-xl border border-border p-4">
          <h2 className="font-semibold">{isHe ? 'מבחנים' : 'Tests'}</h2>
          <ul className="space-y-2 text-sm">
            {attempts.map((a) => (
              <li key={a.id} className="flex flex-wrap justify-between gap-2 rounded-lg bg-surface-1/40 px-3 py-2">
                <span>
                  {a.kind} · {new Date(a.created_at).toLocaleDateString(isHe ? 'he-IL' : 'en-US')}
                </span>
                <span>
                  {a.score == null ? '—' : `${Math.round(a.score * 100)}%`}
                  {a.passed == null ? '' : a.passed ? ' ✓' : ' ✗'}
                </span>
              </li>
            ))}
          </ul>
          <div className="space-y-3 border-t border-border pt-4">
            <h3 className="text-sm font-medium">{isHe ? 'משוב / ציון מורה' : 'Teacher feedback / score'}</h3>
            <label className="block space-y-1 text-sm">
              <span>Attempt ID</span>
              <select
                className="w-full rounded-lg border border-border bg-background px-3 py-2"
                value={gradeAttemptId}
                onChange={(e) => setGradeAttemptId(e.target.value)}
              >
                {attempts.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.kind} — {a.id.slice(0, 8)}
                  </option>
                ))}
              </select>
            </label>
            <textarea
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
              rows={3}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder={isHe ? 'משוב לתלמיד…' : 'Feedback for student…'}
            />
            <div className="flex flex-wrap gap-3">
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
                <input type="checkbox" checked={reopen} onChange={(e) => setReopen(e.target.checked)} />
                {isHe ? 'פתח מחדש' : 'Reopen'}
              </label>
              <Button type="button" onClick={() => void gradeTest()}>
                {isHe ? 'שמור בדיקה' : 'Save grading'}
              </Button>
            </div>
          </div>
        </section>
      ) : null}

      {tab === 'memory' ? (
        <section className="space-y-4 rounded-xl border border-border p-4">
          <h2 className="font-semibold">{isHe ? 'זיכרון' : 'Memory'}</h2>
          <div className="grid gap-4 lg:grid-cols-2">
            <div>
              <h3 className="text-sm font-medium">{isHe ? 'פרסונה' : 'Persona'}</h3>
              <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-surface-1/50 p-3 text-xs">
                {memory?.persona?.trim() || (isHe ? 'אין פרסונה עדיין' : 'No persona yet')}
              </pre>
            </div>
            <div>
              <h3 className="text-sm font-medium">{isHe ? 'פרופיל' : 'Profile'}</h3>
              <p className="mt-2 text-sm">{memory?.profile_goal || goal || '—'}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                {(memory?.subjects ?? []).join(', ') || '—'}
              </p>
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <p className="font-medium text-muted-foreground">{isHe ? 'חלש' : 'Weak'}</p>
                  <ul className="mt-1 space-y-1">
                    {(memory?.weak ?? []).slice(0, 5).map((c) => (
                      <li key={c.concept_id} className="font-mono">
                        {c.concept_id} · {Math.round(c.score * 100)}%
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">{isHe ? 'חזק' : 'Strong'}</p>
                  <ul className="mt-1 space-y-1">
                    {(memory?.strong ?? []).slice(0, 5).map((c) => (
                      <li key={c.concept_id} className="font-mono">
                        {c.concept_id} · {Math.round(c.score * 100)}%
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium">{isHe ? 'הערות סוכנים' : 'Agent notes'}</h3>
            <ul className="mt-2 space-y-2 text-sm">
              {(memory?.notes_by_agent ?? []).map((n) => (
                <li key={n.agent} className="rounded-lg border border-border/60 px-3 py-2">
                  <span className="font-medium">{n.agent}</span>
                  <span className="ms-2 text-xs text-muted-foreground">({n.count})</span>
                  {n.preview ? <p className="mt-1 text-muted-foreground line-clamp-2">{n.preview}</p> : null}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-medium">{isHe ? 'צ׳אט אחרון' : 'Recent chat'}</h3>
            <ul className="mt-2 max-h-40 space-y-1 overflow-auto text-xs">
              {(memory?.recent_chat ?? []).slice(0, 8).map((c, i) => (
                <li key={`${c.created_at}-${i}`} className="rounded bg-surface-1/40 px-2 py-1">
                  <span className="font-medium">{c.agent}/{c.role}</span>: {c.content.slice(0, 120)}
                </li>
              ))}
            </ul>
          </div>

          <h3 className="text-sm font-medium">{isHe ? 'הערות מורה' : 'Teacher notes'}</h3>
          <ul className="space-y-2 text-sm">
            {notes.map((n) => (
              <li key={n.id} className="rounded-lg border border-border/60 px-3 py-2">
                <span className="text-xs text-muted-foreground">{n.kind}</span>
                <p>{n.content}</p>
              </li>
            ))}
          </ul>
          <textarea
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
            rows={3}
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={concern} onChange={(e) => setConcern(e.target.checked)} />
            {isHe ? 'סמן כחשש (התראה לתלמיד)' : 'Mark as concern (notifies student)'}
          </label>
          <Button type="button" onClick={() => void saveNote()}>
            {isHe ? 'הוסף הערה' : 'Add note'}
          </Button>
        </section>
      ) : null}
    </div>
  );
}
