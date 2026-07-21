'use client';

import Link from 'next/link';
import { Badge } from '@asf/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@asf/ui/card';
import { MarkdownMath } from '@/components/markdown-math';
import { isOpenAssessmentKind } from '@/lib/assessment-grading-logic';
import { pickConceptTitle, resolveConceptTitles } from '@/lib/concept-display-names';
import { useLanguagePreference, type Lang } from '@/hooks/use-language-preference';
import type {
  TestAttemptDetail,
  TestAttemptItemFeedback,
  TestAttemptListItem,
  TestAttemptQuestionSnapshot,
} from '@/lib/test-attempts';

const STR = {
  he: {
    title: 'המבחנים שלי',
    subtitle: 'מבחנים קודמים, התשובות שלך והמשוב — כדי ללמוד מהם.',
    empty: 'עדיין אין מבחנים. השלם מבחן שבועי כדי לראות אותו כאן.',
    week: (n: number | null) => (n == null ? 'מבחן' : `שבוע ${n}`),
    kind_mock: 'סימולציה מלאה',
    kind_milestone: 'מבחן ביניים',
    kind_generic: 'מבחן',
    open_pending: 'ממתין למשוב מורה',
    open_failed: 'הבדיקה נכשלה — נסו שוב בהמשך',
    passed: 'עברת',
    failed: 'לא עברת',
    score: 'ציון',
    questions: (n: number) => `${n} שאלות`,
    per_topic: 'ציונים לפי נושא',
    review: 'סקירת שאלות',
    your_answer: 'התשובה שלך',
    correct_answer: 'התשובה הנכונה',
    sample_solution: 'פתרון לדוגמה',
    teacher_feedback: 'משוב המורה',
    strengths: 'מה עשית טוב',
    next_fix: 'מה לתקן',
    steps_skipped: 'צעדים שדילגת',
    points: 'נקודות',
    correct: 'נכון',
    incorrect: 'שגוי',
    partial: 'חלקי',
    no_answer: 'לא נענתה',
    back: '\u2192 חזרה לכל המבחנים',
    view: 'צפייה',
  },
  en: {
    title: 'My tests',
    subtitle: 'Past tests, your answers and feedback — so you can learn from them.',
    empty: 'No tests yet. Complete a weekly quiz to see it here.',
    week: (n: number | null) => (n == null ? 'Test' : `Week ${n}`),
    kind_mock: 'Full mock exam',
    kind_milestone: 'Milestone test',
    kind_generic: 'Test',
    open_pending: 'Awaiting teacher feedback',
    open_failed: 'Grading failed — try again later',
    passed: 'Passed',
    failed: 'Not passed',
    score: 'Score',
    questions: (n: number) => `${n} questions`,
    per_topic: 'Per-topic scores',
    review: 'Question review',
    your_answer: 'Your answer',
    correct_answer: 'Correct answer',
    sample_solution: 'Sample solution',
    teacher_feedback: 'Teacher feedback',
    strengths: 'What you did well',
    next_fix: 'What to fix',
    steps_skipped: 'Steps skipped',
    points: 'points',
    correct: 'Correct',
    incorrect: 'Incorrect',
    partial: 'Partial',
    no_answer: 'Not answered',
    back: '\u2190 Back to all tests',
    view: 'View',
  },
} as const;

function fmtDate(iso: string, lang: Lang): string {
  try {
    return new Date(iso).toLocaleDateString(lang === 'he' ? 'he-IL' : 'en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

function topicName(conceptId: string, lang: Lang): string {
  return pickConceptTitle(resolveConceptTitles(conceptId), lang);
}

/** Human label for an attempt by kind (falls back to the weekly "Week N" label). */
function attemptLabel(
  kind: string,
  weekNum: number | null,
  t: (typeof STR)[Lang],
): string {
  if (kind === 'mock_exam') return t.kind_mock;
  if (kind === 'milestone' || kind === 'milestone_test' || kind === 'unit_test') return t.kind_milestone;
  if (kind === 'weekly_gate') return t.week(weekNum);
  return weekNum == null ? t.kind_generic : t.week(weekNum);
}

function isOpenQuestion(q: TestAttemptQuestionSnapshot): boolean {
  if (q.kind) return isOpenAssessmentKind(q.kind);
  return !q.options || q.options.length === 0;
}

function itemProcessScore(
  q: TestAttemptQuestionSnapshot,
  itemScores: Record<string, number>,
  fb: TestAttemptItemFeedback | undefined,
): number | null {
  if (typeof itemScores[q.id] === 'number') return itemScores[q.id]!;
  if (typeof fb?.process_score === 'number') return fb.process_score;
  return null;
}

function OutcomeBadge({
  isOpen,
  chosen,
  gotIt,
  processScore,
  fb,
  t,
}: {
  isOpen: boolean;
  chosen: string;
  gotIt: boolean;
  processScore: number | null;
  fb: TestAttemptItemFeedback | undefined;
  t: (typeof STR)[Lang];
}) {
  if (isOpen) {
    if (fb?.status === 'pending' || fb?.status === 'grading') {
      return <Badge variant="secondary">{t.open_pending}</Badge>;
    }
    if (fb?.status === 'failed') {
      return <Badge variant="warning">{t.open_failed}</Badge>;
    }
    if (processScore != null) {
      if (processScore >= 0.85) return <Badge variant="success">{t.correct}</Badge>;
      if (processScore <= 0.15) return <Badge variant="warning">{t.incorrect}</Badge>;
      return (
        <Badge variant="secondary">
          {t.partial} · {Math.round(processScore * 100)}%
        </Badge>
      );
    }
    return <Badge variant="secondary">{t.open_pending}</Badge>;
  }
  if (!chosen) return <Badge variant="secondary">{t.no_answer}</Badge>;
  return <Badge variant={gotIt ? 'success' : 'warning'}>{gotIt ? t.correct : t.incorrect}</Badge>;
}

function TeacherFeedbackBlock({
  fb,
  modelAnswer,
  showSample,
  t,
  isHe,
}: {
  fb: TestAttemptItemFeedback | undefined;
  modelAnswer?: string | null;
  showSample: boolean;
  t: (typeof STR)[Lang];
  isHe: boolean;
}) {
  const graded = fb?.status === 'graded';
  const hasText =
    graded &&
    Boolean(fb?.strengths || fb?.next_fix || fb?.steps_skipped || fb?.steps_present || fb?.logic);
  if (!hasText && !(showSample && modelAnswer)) return null;

  return (
    <div className="mt-3 space-y-2 rounded-lg border border-primary/20 bg-primary/5 p-3 text-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {t.teacher_feedback}
      </p>
      {graded && fb?.points_available != null ? (
        <p className="text-xs text-muted-foreground">
          {fb.points_earned ?? 0}/{fb.points_available} {t.points}
          {typeof fb.process_score === 'number'
            ? ` · ${Math.round(fb.process_score * 100)}%`
            : ''}
        </p>
      ) : null}
      {fb?.strengths ? (
        <p dir="auto">
          <span className="font-medium">{t.strengths}: </span>
          {fb.strengths}
        </p>
      ) : null}
      {fb?.steps_skipped ? (
        <p dir="auto">
          <span className="font-medium">{t.steps_skipped}: </span>
          {fb.steps_skipped}
        </p>
      ) : null}
      {fb?.next_fix ? (
        <p className="text-amber-800 dark:text-amber-400" dir="auto">
          <span className="font-medium">{t.next_fix}: </span>
          {fb.next_fix}
        </p>
      ) : null}
      {showSample && modelAnswer ? (
        <div className="border-t border-border/50 pt-2" dir="auto">
          <span className="mb-1 block text-xs text-muted-foreground">{t.sample_solution}</span>
          <MarkdownMath dir={isHe ? 'rtl' : 'ltr'}>{modelAnswer}</MarkdownMath>
        </div>
      ) : null}
    </div>
  );
}

export function TestsArchiveList({ items }: { items: TestAttemptListItem[] }) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';

  return (
    <div className="space-y-6" dir={isHe ? 'rtl' : 'ltr'}>
      <header>
        <h1 className="font-display text-3xl font-bold">{t.title}</h1>
        <p className="mt-2 text-sm text-muted-foreground">{t.subtitle}</p>
      </header>

      {items.length === 0 ? (
        <p className="text-muted-foreground">{t.empty}</p>
      ) : (
        <div className="grid gap-3">
          {items.map((a) => (
            <Link key={a.id} href={`/app/tests/${a.id}`} className="block">
              <Card className="glass-surface border-border/60 transition-opacity hover:opacity-90">
                <CardContent className="flex flex-wrap items-center justify-between gap-3 py-4">
                  <div className="min-w-0">
                    <p className="font-medium">{attemptLabel(a.kind, a.week_num, t)}</p>
                    <p className="text-xs text-muted-foreground">
                      {fmtDate(a.created_at, lang)} · {t.questions(a.question_count)}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-semibold tabular-nums">
                      {a.score == null
                        ? a.grading_status === 'needs_human'
                          ? lang === 'he'
                            ? 'ממתין למורה'
                            : 'Needs teacher'
                          : lang === 'he'
                            ? 'בבדיקה…'
                            : 'Reviewing…'
                        : `${Math.round(a.score * 100)}%`}
                    </span>
                    {a.passed != null ? (
                      <Badge variant={a.passed ? 'success' : 'warning'}>
                        {a.passed ? t.passed : t.failed}
                      </Badge>
                    ) : (
                      <Badge variant="secondary">
                        {lang === 'he' ? 'ממתין למשוב' : 'Awaiting feedback'}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function TestAttemptView({ attempt }: { attempt: TestAttemptDetail }) {
  const [lang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';
  const answerByItem = new Map(attempt.answers.map((a) => [a.item_id, a.chosen]));
  const complete = attempt.grading_status === 'complete';
  const teacherOverride =
    typeof attempt.feedback?.teacher_feedback === 'string'
      ? attempt.feedback.teacher_feedback.trim()
      : '';

  return (
    <div className="space-y-6" dir={isHe ? 'rtl' : 'ltr'}>
      <Link href="/app/tests" className="text-sm text-primary">
        {t.back}
      </Link>

      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-bold">
            {attemptLabel(attempt.kind, attempt.week_num, t)}
          </h1>
          <p className="text-xs text-muted-foreground">{fmtDate(attempt.created_at, lang)}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-2xl font-semibold tabular-nums">
            {attempt.score == null
              ? lang === 'he'
                ? 'בבדיקה…'
                : 'Reviewing…'
              : `${Math.round(attempt.score * 100)}%`}
          </span>
          <Badge
            variant={
              attempt.passed == null ? 'secondary' : attempt.passed ? 'success' : 'warning'
            }
          >
            {attempt.passed == null
              ? isHe
                ? 'ממתין למשוב'
                : 'Awaiting feedback'
              : attempt.passed
                ? t.passed
                : t.failed}
          </Badge>
        </div>
      </header>

      {teacherOverride ? (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">{t.teacher_feedback}</CardTitle>
          </CardHeader>
          <CardContent className="text-sm" dir="auto">
            {teacherOverride}
          </CardContent>
        </Card>
      ) : null}

      {Object.keys(attempt.per_topic).length > 0 ? (
        <Card className="border-border/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">{t.per_topic}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(attempt.per_topic).map(([topic, score]) => (
              <div key={topic}>
                <div className="mb-1 flex justify-between text-xs">
                  <span dir="auto">{topicName(topic, lang)}</span>
                  <span className="text-muted-foreground">{Math.round(score * 100)}%</span>
                </div>
                <div className="h-1.5 rounded-full bg-muted">
                  <div
                    className={`h-full rounded-full ${
                      score >= 0.7 ? 'bg-emerald-500' : score >= 0.4 ? 'bg-amber-500' : 'bg-rose-500'
                    }`}
                    style={{ width: `${Math.round(score * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}

      <section className="space-y-4">
        <h2 className="text-sm font-semibold text-muted-foreground">{t.review}</h2>
        {attempt.questions.map((q, idx) => {
          const isOpen = isOpenQuestion(q);
          const rawChosen = answerByItem.get(q.id) ?? '';
          const chosen = rawChosen.toUpperCase();
          const correct = (q.correct ?? '').toUpperCase();
          const gotIt = !isOpen && Boolean(correct) && chosen === correct;
          const fb = attempt.item_feedback[q.id];
          const processScore = itemProcessScore(q, attempt.item_scores, fb);

          return (
            <Card key={q.id} className="border-border/60">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-medium text-muted-foreground">#{idx + 1}</span>
                  <OutcomeBadge
                    isOpen={isOpen}
                    chosen={chosen}
                    gotIt={gotIt}
                    processScore={processScore}
                    fb={fb}
                    t={t}
                  />
                </div>
                <MarkdownMath dir={isHe ? 'rtl' : 'ltr'}>{q.stem}</MarkdownMath>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {(isOpen || ((q.options?.length ?? 0) === 0)) && rawChosen ? (
                  <div className="rounded-md border border-border/50 px-3 py-2 text-sm" dir="auto">
                    <span className="mb-1 block text-xs text-muted-foreground">{t.your_answer}</span>
                    <MarkdownMath dir={isHe ? 'rtl' : 'ltr'}>{rawChosen}</MarkdownMath>
                  </div>
                ) : null}
                {!complete && !isOpen ? (
                  <p className="text-xs text-muted-foreground">
                    {isHe
                      ? 'הציון והמשוב יופיעו אחרי שחרור הבדיקה.'
                      : 'Score and feedback appear after the check is released.'}
                  </p>
                ) : null}
                {(q.options ?? []).map((opt) => {
                  const key = opt.key.toUpperCase();
                  const isCorrect = Boolean(correct) && key === correct;
                  const isChosen = key === chosen;
                  return (
                    <div
                      key={opt.key}
                      className={`flex items-start gap-2 rounded-md border px-3 py-2 text-sm ${
                        isCorrect
                          ? 'border-emerald-500/50 bg-emerald-500/10'
                          : isChosen
                            ? 'border-rose-500/50 bg-rose-500/10'
                            : 'border-border/50'
                      }`}
                      dir="auto"
                    >
                      <span className="font-semibold">{opt.key}.</span>
                      <span className="min-w-0 flex-1">
                        <MarkdownMath dir={isHe ? 'rtl' : 'ltr'}>{opt.text}</MarkdownMath>
                      </span>
                      {isCorrect ? (
                        <span className="shrink-0 text-xs text-emerald-600">{t.correct_answer}</span>
                      ) : isChosen ? (
                        <span className="shrink-0 text-xs text-rose-600">{t.your_answer}</span>
                      ) : null}
                    </div>
                  );
                })}
                <TeacherFeedbackBlock
                  fb={fb}
                  modelAnswer={q.model_answer}
                  showSample={complete && isOpen}
                  t={t}
                  isHe={isHe}
                />
              </CardContent>
            </Card>
          );
        })}
      </section>
    </div>
  );
}
