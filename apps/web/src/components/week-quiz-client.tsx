'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@asf/ui/button';
import { Badge } from '@asf/ui/badge';
import { cn } from '@asf/ui';
import { CheckCircle2, XCircle, Clock, ChevronRight, ChevronLeft, Loader2 } from 'lucide-react';
import {
  gradingUiPhase,
  maxGradeNextPolls,
} from '@/lib/assessment-grading-logic';
import type { QuizQuestion, QuizStartResponse, QuizSubmitResponse } from '@asf/schemas/learning_path';
import { useLanguagePreference, type Lang } from '@/hooks/use-language-preference';
import { MarkdownMath } from '@/components/markdown-math';
import { pickConceptTitle, resolveConceptTitles } from '@/lib/concept-display-names';
import { AgentSidePanel } from '@/components/agent-side-panel';

interface Props {
  quiz: QuizStartResponse;
  planId: string;
  weekNum: number;
  token: string;
}

type AnswerMap = Record<string, string>; // item_id → chosen key

/**
 * Localised strings for the week-quiz flow. Hebrew is the default; the
 * `dir="auto"` attribute on the user-content elements (question stem,
 * options, topic chip) keeps mixed Hebrew/LaTeX strings rendering with
 * the correct base direction even when the UI is RTL.
 */
const STR = {
  he: {
    title: (n: number) => `מבחן שבוע ${n}`,
    answered: (a: number, total: number) => `${a} מתוך ${total} נענו`,
    question_x_of_y: (i: number, total: number) => `שאלה ${i} מתוך ${total}`,
    submit: 'שלח מבחן',
    submitting: 'שולח…',
    submitError: 'לא הצלחנו לשלוח את המבחן. נסה שוב.',
    needAnswer: 'ענה לפחות על שאלה אחת לפני שליחה.',
    next: 'הבא',
    previous: 'הקודם',
    back_to_dashboard: 'חזרה ללוח',
    great: 'עבודה מצוינת! המשך כך.',
    keep_studying: 'המשך ללמוד — אפשר לעשות את המבחן שוב.',
    per_topic_scores: 'ציונים לפי נושא',
    plan_adapted: 'תכנית הלימוד שלך עודכנה בעקבות תוצאות המבחן.',
    next_up: (cs: string) => ` הבא בתור: ${cs}.`,
    review_concepts: 'מושגים לחזרה:',
    view_in_tests: 'צפייה במבחן בארכיון',
    write_answer: 'כתבו את הפתרון המלא — שלבים, נימוקים ותשובה סופית.',
    write_short: 'כתבו את התשובה הקצרה',
    write_numeric: 'הזינו את התשובה המספרית',
    kind_open: 'שאלה פתוחה',
    kind_numeric: 'חישוב',
    kind_short: 'תשובה קצרה',
    kind_mcq: 'רב-ברירה',
    reviewing: 'בודקים את הפתרונות שלכם…',
    review_progress: (done: number, total: number) => `נבדקו ${done} מתוך ${total} שאלות פתוחות`,
    score_after_review: 'הציון יופיע רק אחרי בדיקת התהליך המלא.',
    feedback_title: 'משוב לפי שאלה',
    strengths: 'חוזקות',
    steps_present: 'שלבים שהופיעו',
    steps_skipped: 'שלבים שדולגו',
    logic: 'היגיון',
    material: 'עיגון לחומר',
    points: 'נקודות',
    next_fix: 'תיקון הבא',
    grader_busy: 'הבודק עסוק — ממשיכים בעוד רגע…',
    grader_failed: 'לא הצלחנו לסיים את הבדיקה. נסו לרענן.',
  },
  en: {
    title: (n: number) => `Week ${n} Quiz`,
    answered: (a: number, total: number) => `${a} of ${total} answered`,
    question_x_of_y: (i: number, total: number) => `Question ${i} of ${total}`,
    submit: 'Submit quiz',
    submitting: 'Submitting…',
    submitError: 'Could not submit the quiz. Please try again.',
    needAnswer: 'Answer at least one question before submitting.',
    next: 'Next',
    previous: 'Previous',
    back_to_dashboard: 'Back to dashboard',
    great: 'Great work! Keep it up.',
    keep_studying: 'Keep studying — you can retake this quiz.',
    per_topic_scores: 'Per-topic scores',
    plan_adapted: 'Your learning plan has been updated based on your quiz results.',
    next_up: (cs: string) => ` Next up: ${cs}.`,
    review_concepts: 'Concepts to review:',
    view_in_tests: 'View this test in your archive',
    write_answer: 'Write a full solution — steps, reasoning, and final answer.',
    write_short: 'Enter a short answer',
    write_numeric: 'Enter the numeric answer',
    kind_open: 'Open response',
    kind_numeric: 'Calculation',
    kind_short: 'Short answer',
    kind_mcq: 'Multiple choice',
    reviewing: 'Reviewing your solutions…',
    review_progress: (done: number, total: number) => `Reviewed ${done} of ${total} open questions`,
    score_after_review: 'Your score appears only after full process review.',
    feedback_title: 'Per-question feedback',
    strengths: 'Strengths',
    steps_present: 'Steps present',
    steps_skipped: 'Steps skipped',
    logic: 'Logic',
    material: 'Material anchoring',
    points: 'Points',
    next_fix: 'Next fix',
    grader_busy: 'Grader busy — retrying shortly…',
    grader_failed: 'Could not finish grading. Try refreshing.',
  },
} as const;

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function kindLabel(
  kind: QuizQuestion['kind'] | undefined,
  t: { kind_open: string; kind_numeric: string; kind_short: string; kind_mcq: string },
): string {
  switch (kind) {
    case 'open':
    case 'derivation':
      return t.kind_open;
    case 'numeric':
      return t.kind_numeric;
    case 'short_answer':
      return t.kind_short;
    default:
      return t.kind_mcq;
  }
}

function QuizQuestionCard({
  question,
  index,
  total,
  chosen,
  onChoose,
  lang,
}: {
  question: QuizQuestion;
  index: number;
  total: number;
  chosen: string | undefined;
  onChoose: (key: string) => void;
  lang: Lang;
}) {
  const t = STR[lang];
  const titles = resolveConceptTitles(question.topic);
  const topicLabel = pickConceptTitle(titles, lang);
  const kind = question.kind ?? 'mcq';
  const isClosed =
    (kind === 'mcq' || kind === 'true_false') &&
    Array.isArray(question.options) &&
    question.options.filter((o) => o.text && o.text !== '—').length >= 2;
  const placeholder =
    kind === 'numeric' ? t.write_numeric : kind === 'short_answer' ? t.write_short : t.write_answer;

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-3">
        <span className="text-sm text-muted-foreground">
          {t.question_x_of_y(index + 1, total)}
        </span>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <Badge variant="secondary" className="text-xs">
            {kindLabel(kind, t)}
          </Badge>
          <Badge variant="outline" className="text-xs" dir={lang === 'he' ? 'rtl' : 'ltr'}>
            {topicLabel}
          </Badge>
        </div>
      </div>

      <div className="rounded-xl bg-surface-1/40 p-4 text-lg font-medium leading-relaxed">
        <MarkdownMath
          className="prose-p:my-0 prose-p:leading-relaxed"
          dir={lang === 'he' ? 'rtl' : 'ltr'}
        >
          {question.stem}
        </MarkdownMath>
      </div>

      {question.parts && question.parts.length >= 2 ? (
        <div className="space-y-3 rounded-xl border border-border/60 bg-surface-1/20 p-4">
          {question.parts.map((part) => (
            <div key={part.label} className="space-y-1">
              <div className="flex items-center gap-2 text-sm font-semibold">
                <span>({part.label})</span>
                {typeof part.points === 'number' ? (
                  <span className="text-xs font-normal text-muted-foreground">
                    {part.points} {lang === 'he' ? "נק'" : 'pts'}
                  </span>
                ) : null}
              </div>
              <MarkdownMath
                className="prose-p:my-0 text-sm leading-relaxed"
                dir={lang === 'he' ? 'rtl' : 'ltr'}
              >
                {part.body}
              </MarkdownMath>
            </div>
          ))}
          {typeof question.total_points === 'number' ? (
            <p className="text-xs text-muted-foreground">
              {lang === 'he' ? 'סה״כ' : 'Total'}: {question.total_points}{' '}
              {lang === 'he' ? "נק'" : 'pts'}
            </p>
          ) : null}
        </div>
      ) : null}

      {isClosed ? (
        <div className="space-y-2">
          {question.options
            .filter((opt) => opt.text && opt.text !== '—')
            .map((opt) => (
              <button
                key={opt.key}
                type="button"
                onClick={() => onChoose(opt.key)}
                className={cn(
                  'flex w-full items-start gap-3 rounded-xl border px-4 py-3 text-start transition-all',
                  chosen === opt.key
                    ? 'border-primary bg-primary/10 font-medium text-primary'
                    : 'border-border bg-surface-1/40 hover:border-primary/40 hover:bg-surface-2/60',
                )}
              >
                <span
                  className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-muted font-mono text-xs font-semibold"
                  dir="ltr"
                  aria-hidden
                >
                  {opt.key}
                </span>
                <span className="min-w-0 flex-1">
                  <MarkdownMath
                    className="prose-p:my-0 prose-p:leading-relaxed"
                    dir={lang === 'he' ? 'rtl' : 'ltr'}
                  >
                    {opt.text}
                  </MarkdownMath>
                </span>
              </button>
            ))}
        </div>
      ) : (
        <div className="space-y-2">
          <label className="text-sm text-muted-foreground" htmlFor={`gate-ans-${question.id}`}>
            {placeholder}
          </label>
          <textarea
            id={`gate-ans-${question.id}`}
            value={chosen ?? ''}
            onChange={(e) => onChoose(e.target.value)}
            rows={kind === 'numeric' || kind === 'short_answer' ? 2 : 8}
            dir={lang === 'he' ? 'rtl' : 'ltr'}
            className="w-full resize-y rounded-xl border border-border bg-surface-1/40 px-4 py-3 text-base leading-relaxed outline-none focus:border-primary"
            placeholder={placeholder}
          />
        </div>
      )}
    </div>
  );
}

function ProcessFeedbackList({
  result,
  t,
}: {
  result: QuizSubmitResponse;
  t: (typeof STR)[Lang];
}) {
  const entries = Object.values(result.item_feedback ?? {}).filter(
    (f) => f.status === 'graded' || f.status === 'failed',
  );
  if (entries.length === 0) return null;
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">{t.feedback_title}</h3>
      {entries.map((f) => (
        <div key={f.item_id} className="glass-surface space-y-2 rounded-xl p-4 text-sm">
          <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
            <span dir="ltr">{f.item_id.slice(0, 12)}</span>
            <span>
              {t.points}: {f.points_earned}/{f.points_available}
            </span>
          </div>
          {f.strengths ? (
            <p>
              <span className="font-medium">{t.strengths}: </span>
              {f.strengths}
            </p>
          ) : null}
          {f.steps_present ? (
            <p>
              <span className="font-medium">{t.steps_present}: </span>
              {f.steps_present}
            </p>
          ) : null}
          {f.steps_skipped ? (
            <p>
              <span className="font-medium">{t.steps_skipped}: </span>
              {f.steps_skipped}
            </p>
          ) : null}
          {f.logic ? (
            <p>
              <span className="font-medium">{t.logic}: </span>
              {f.logic}
            </p>
          ) : null}
          {f.material_anchoring ? (
            <p>
              <span className="font-medium">{t.material}: </span>
              {f.material_anchoring}
            </p>
          ) : null}
          {f.next_fix ? (
            <p className="text-amber-700 dark:text-amber-400">
              <span className="font-medium">{t.next_fix}: </span>
              {f.next_fix}
            </p>
          ) : null}
        </div>
      ))}
    </div>
  );
}

function ResultView({
  result,
  onGoToDashboard,
  lang,
  grading,
}: {
  result: QuizSubmitResponse;
  onGoToDashboard: () => void;
  lang: Lang;
  grading?: boolean;
}) {
  const t = STR[lang];
  const isHe = lang === 'he';
  const phase = gradingUiPhase({
    grading_status: result.grading_status,
    score: result.score,
  });
  const openTotal = result.open_total ?? 0;
  const gradedOpen = result.graded_open ?? 0;

  if (phase === 'failed') {
    return (
      <div className="space-y-6 text-center" dir={isHe ? 'rtl' : 'ltr'}>
        <XCircle className="mx-auto h-16 w-16 text-destructive" />
        <p className="text-muted-foreground">{t.grader_failed}</p>
        <ProcessFeedbackList result={result} t={t} />
        <Button className="w-full" onClick={onGoToDashboard}>
          {t.back_to_dashboard}
        </Button>
      </div>
    );
  }

  if (phase === 'pending') {
    return (
      <div className="space-y-6" dir={isHe ? 'rtl' : 'ltr'}>
        <div className="text-center">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary" />
          <h2 className="mt-4 font-display text-2xl font-bold">{t.reviewing}</h2>
          <p className="mt-2 text-sm text-muted-foreground">{t.score_after_review}</p>
          {openTotal > 0 ? (
            <p className="mt-1 text-sm text-muted-foreground">
              {t.review_progress(gradedOpen, openTotal)}
            </p>
          ) : null}
          {result.busy || result.message ? (
            <p className="mt-2 text-sm text-amber-700 dark:text-amber-400" role="status">
              {result.message ?? t.grader_busy}
            </p>
          ) : null}
          {grading ? (
            <p className="mt-2 text-xs text-muted-foreground" aria-live="polite">
              …
            </p>
          ) : null}
        </div>
        <ProcessFeedbackList result={result} t={t} />
      </div>
    );
  }

  const pct = Math.round((result.score ?? 0) * 100);
  const passed = result.passed ?? (result.score ?? 0) >= 0.6;

  return (
    <div className="space-y-6" dir={isHe ? 'rtl' : 'ltr'}>
      <div className="text-center">
        {passed ? (
          <CheckCircle2 className="mx-auto h-16 w-16 text-green-500" />
        ) : (
          <XCircle className="mx-auto h-16 w-16 text-destructive" />
        )}
        <h2 className="mt-4 font-display text-3xl font-bold">{pct}%</h2>
        <p className="mt-1 text-muted-foreground">
          {passed ? t.great : t.keep_studying}
        </p>
      </div>

      <ProcessFeedbackList result={result} t={t} />

      {Object.keys(result.per_topic).length > 0 && (
        <div className="glass-surface rounded-xl p-4">
          <h3 className="mb-3 text-sm font-semibold">{t.per_topic_scores}</h3>
          <div className="space-y-2">
            {Object.entries(result.per_topic).map(([topic, score]) => (
              <div key={topic} className="flex items-center justify-between gap-3">
                <span className="text-sm" dir="auto">
                  {topic.replace(/_/g, ' ')}
                </span>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-24 overflow-hidden rounded-full bg-muted">
                    <div
                      className={cn(
                        'h-full rounded-full',
                        score >= 0.7
                          ? 'bg-green-500'
                          : score >= 0.4
                            ? 'bg-amber-500'
                            : 'bg-destructive',
                      )}
                      style={{ width: `${Math.round(score * 100)}%` }}
                    />
                  </div>
                  <span className="w-10 text-right text-xs text-muted-foreground">
                    {Math.round(score * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.plan_adapted && (
        <div className="rounded-xl border border-accent-cyan/30 bg-accent-cyan/10 px-4 py-3 text-sm text-accent-cyan">
          {t.plan_adapted}
          {result.next_week_concepts && result.next_week_concepts.length > 0 && (
            <span>
              {t.next_up(
                result.next_week_concepts
                  .slice(0, 3)
                  .map((c) => c.replace(/_/g, ' '))
                  .join(', '),
              )}
            </span>
          )}
        </div>
      )}

      {result.weak_concepts.length > 0 && (
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            {t.review_concepts}
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {result.weak_concepts.map((c) => (
              <Badge key={c} variant="secondary" dir="auto">
                {c.replace(/_/g, ' ')}
              </Badge>
            ))}
          </div>
        </div>
      )}

      <Button className="w-full" onClick={onGoToDashboard}>
        {t.back_to_dashboard}
      </Button>
      {result.attempt_id ? (
        <Link
          href={`/app/tests/${result.attempt_id}`}
          className="block text-center text-sm text-primary hover:underline"
        >
          {t.view_in_tests}
        </Link>
      ) : null}
      <AgentSidePanel
        topic={result.weak_concepts[0]}
        fabLabel={{ he: 'שאל את הסוכן על המבחן', en: 'Ask an agent about this test' }}
      />
    </div>
  );
}

export function WeekQuizClient({ quiz, planId, weekNum, token }: Props) {
  const router = useRouter();
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';

  const [answers, setAnswers] = useState<AnswerMap>({});
  const [currentIdx, setCurrentIdx] = useState(0);
  const [timeLeft, setTimeLeft] = useState(quiz.time_limit_s);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [result, setResult] = useState<QuizSubmitResponse | null>(null);
  const [grading, setGrading] = useState(false);

  const handleSubmit = useCallback(
    async (opts?: { allowEmpty?: boolean }) => {
      if (submitting) return;
      setSubmitting(true);
      setSubmitError(null);
      try {
        const answerList = quiz.questions
          .filter((q) => answers[q.id]?.trim())
          .map((q) => ({
            item_id: q.id,
            chosen: answers[q.id]!,
            time_spent_s: null,
          }));

        if (answerList.length === 0 && !opts?.allowEmpty) {
          setSubmitError(t.needAnswer);
          return;
        }

        const res = await fetch(`/api/quiz/${quiz.quiz_id}/submit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            plan_id: planId,
            week_num: weekNum,
            answers: answerList,
            locale: lang,
            token,
          }),
        });

        if (!res.ok) {
          setSubmitError(t.submitError);
          return;
        }

        const data = (await res.json()) as QuizSubmitResponse;
        setResult(data);
      } catch {
        setSubmitError(t.submitError);
      } finally {
        setSubmitting(false);
      }
    },
    [answers, quiz, planId, weekNum, token, submitting, t, lang],
  );

  // Chunked process grading: keep calling grade-next until complete.
  useEffect(() => {
    if (!result?.attempt_id) return;
    const status = result.grading_status ?? 'complete';
    if (status === 'complete' || status === 'failed') return;
    // Closed-only submits already have score.
    if ((result.open_total ?? 0) === 0 && result.score != null) return;

    const attemptId = result.attempt_id;
    const maxPolls = maxGradeNextPolls(result.open_total ?? 4);
    let polls = 0;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    const tick = async () => {
      if (cancelled) return;
      if (polls >= maxPolls) {
        setResult((prev) =>
          prev
            ? {
                ...prev,
                grading_status: 'failed',
                message:
                  lang === 'he'
                    ? 'בדיקה ארכה מדי — נסו לרענן.'
                    : 'Grading took too long — try refreshing.',
              }
            : prev,
        );
        return;
      }
      polls += 1;
      setGrading(true);
      try {
        const res = await fetch('/api/quiz/grade-next', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ attempt_id: attemptId }),
        });
        if (!res.ok) {
          if (!cancelled) timer = setTimeout(() => void tick(), 2500);
          return;
        }
        const data = (await res.json()) as QuizSubmitResponse;
        if (cancelled) return;
        setResult(data);
        const next = data.grading_status ?? 'complete';
        if (next !== 'complete' && next !== 'failed') {
          const delay = data.busy ? 3000 : 400;
          timer = setTimeout(() => void tick(), delay);
        }
      } catch {
        if (!cancelled) timer = setTimeout(() => void tick(), 3000);
      } finally {
        if (!cancelled) setGrading(false);
      }
    };

    timer = setTimeout(() => void tick(), 200);
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
    // Intentionally only re-start when a new attempt appears (not on every grade chunk).
    // eslint-disable-next-line react-hooks/exhaustive-deps -- poll loop owns updates
  }, [result?.attempt_id]);

  // Countdown timer
  useEffect(() => {
    if (result) return;
    const id = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(id);
          void handleSubmit({ allowEmpty: true });
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [result, handleSubmit]);

  if (result) {
    return (
      <ResultView
        result={result}
        onGoToDashboard={() => router.push('/app')}
        lang={lang}
        grading={grading}
      />
    );
  }

  const current = quiz.questions[currentIdx] ?? quiz.questions[0];
  if (!current) return null;
  const answered = Object.keys(answers).length;
  const isLast = currentIdx === quiz.questions.length - 1;
  const timeWarning = timeLeft < 120;
  // Forward/back chevrons need to mirror in RTL so "next" still points
  // in the reading direction.
  const NextIcon = isHe ? ChevronLeft : ChevronRight;

  return (
    <div className="space-y-6" dir={isHe ? 'rtl' : 'ltr'}>
      <header className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold">{t.title(weekNum)}</h1>
          <p className="text-sm text-muted-foreground">
            {t.answered(answered, quiz.questions.length)}
          </p>
        </div>
        <div
          className={cn(
            'flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium',
            timeWarning
              ? 'bg-destructive/10 text-destructive'
              : 'bg-surface-1/60 text-muted-foreground',
          )}
          dir="ltr"
        >
          <Clock className="h-4 w-4" />
          {formatTime(timeLeft)}
        </div>
      </header>

      {/* Progress bar */}
      <div className="h-1.5 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${((currentIdx + 1) / quiz.questions.length) * 100}%` }}
        />
      </div>

      <div className="glass-surface rounded-2xl p-6">
        <QuizQuestionCard
          question={current}
          index={currentIdx}
          total={quiz.questions.length}
          chosen={answers[current.id]}
          onChoose={(key) =>
            setAnswers((prev) => ({ ...prev, [current.id]: key }))
          }
          lang={lang}
        />
      </div>

      {submitError ? (
        <p className="text-sm text-destructive" role="alert">
          {submitError}
        </p>
      ) : null}

      <div className="flex items-center justify-between gap-3">
        <Button
          variant="outline"
          onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
          disabled={currentIdx === 0}
        >
          {t.previous}
        </Button>

        {isLast ? (
          <Button onClick={() => void handleSubmit()} disabled={submitting} className="gap-2">
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                {t.submitting}
              </>
            ) : (
              t.submit
            )}
          </Button>
        ) : (
          <Button
            onClick={() =>
              setCurrentIdx((i) =>
                Math.min(quiz.questions.length - 1, i + 1),
              )
            }
            className="gap-2"
          >
            {t.next}
            <NextIcon className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
