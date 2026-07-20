'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { Input } from '@asf/ui/input';
import { useI18n } from '@/providers/i18n-provider';

interface Props {
  studentId: string;
  studentName: string;
  username: string;
  goal: string | null;
  hoursPerWeek: number | null;
  planWeekConcepts: string[];
  masterySample: Array<{ concept_id: string; score: number }>;
  attempts: Array<{
    id: string;
    kind: string;
    score: number | null;
    passed: boolean | null;
    created_at: string;
  }>;
  personaPreview: string | null;
  notes: Array<{ id: string; kind: string; content: string; created_at: string }>;
}

export function EducatorStudentWorkspace({
  studentId,
  studentName,
  username,
  goal,
  hoursPerWeek,
  planWeekConcepts,
  masterySample,
  attempts,
  personaPreview,
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

      {tab === 'overview' || tab === 'progress' ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <section className="rounded-xl border border-border p-4">
            <h2 className="font-semibold">{isHe ? 'התקדמות' : 'Progress'}</h2>
            <ul className="mt-3 space-y-2 text-sm">
              {masterySample.length === 0 ? (
                <li className="text-muted-foreground">{isHe ? 'אין נתונים' : 'No data'}</li>
              ) : (
                masterySample.map((m) => (
                  <li key={m.concept_id} className="flex justify-between gap-2">
                    <span className="font-mono text-xs">{m.concept_id}</span>
                    <span>{Math.round(m.score * 100)}%</span>
                  </li>
                ))
              )}
            </ul>
          </section>
          {tab === 'overview' ? (
            <section className="rounded-xl border border-border p-4">
              <h2 className="font-semibold">{isHe ? 'מיקוד השבוע' : 'This week focus'}</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {planWeekConcepts.length === 0 ? (
                  <span className="text-sm text-muted-foreground">{isHe ? 'אין' : 'None'}</span>
                ) : (
                  planWeekConcepts.map((id) => (
                    <span key={id} className="rounded-full bg-surface-2 px-2 py-1 text-xs font-mono">
                      {id}
                    </span>
                  ))
                )}
              </div>
            </section>
          ) : null}
        </div>
      ) : null}

      {tab === 'plan' ? (
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
              />
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={passed} onChange={(e) => setPassed(e.target.checked)} disabled={reopen} />
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
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-surface-1/50 p-3 text-xs">
            {personaPreview?.trim() || (isHe ? 'אין פרסונה עדיין' : 'No persona yet')}
          </pre>
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
