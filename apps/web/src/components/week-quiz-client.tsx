'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@asf/ui/button';
import { Badge } from '@asf/ui/badge';
import { cn } from '@asf/ui';
import { CheckCircle2, XCircle, Clock, ChevronRight, ChevronLeft, Loader2 } from 'lucide-react';
import type { QuizQuestion, QuizStartResponse, QuizSubmitResponse } from '@asf/schemas/learning_path';
import { useLanguagePreference, type Lang } from '@/hooks/use-language-preference';

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
    next: 'הבא',
    previous: 'הקודם',
    back_to_dashboard: 'חזרה ללוח',
    great: 'עבודה מצוינת! המשך כך.',
    keep_studying: 'המשך ללמוד — אפשר לעשות את המבחן שוב.',
    per_topic_scores: 'ציונים לפי נושא',
    plan_adapted: 'תכנית הלימוד שלך עודכנה בעקבות תוצאות המבחן.',
    next_up: (cs: string) => ` הבא בתור: ${cs}.`,
    review_concepts: 'מושגים לחזרה:',
  },
  en: {
    title: (n: number) => `Week ${n} Quiz`,
    answered: (a: number, total: number) => `${a} of ${total} answered`,
    question_x_of_y: (i: number, total: number) => `Question ${i} of ${total}`,
    submit: 'Submit quiz',
    submitting: 'Submitting…',
    next: 'Next',
    previous: 'Previous',
    back_to_dashboard: 'Back to dashboard',
    great: 'Great work! Keep it up.',
    keep_studying: 'Keep studying — you can retake this quiz.',
    per_topic_scores: 'Per-topic scores',
    plan_adapted: 'Your learning plan has been updated based on your quiz results.',
    next_up: (cs: string) => ` Next up: ${cs}.`,
    review_concepts: 'Concepts to review:',
  },
} as const;

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
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
  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-3">
        <span className="text-sm text-muted-foreground">
          {t.question_x_of_y(index + 1, total)}
        </span>
        <Badge variant="outline" className="text-xs" dir="auto">
          {question.topic.replace(/_/g, ' ')}
        </Badge>
      </div>

      <p className="text-lg font-medium leading-relaxed" dir="auto">
        {question.stem}
      </p>

      <div className="space-y-2">
        {question.options.map((opt) => (
          <button
            key={opt.key}
            onClick={() => onChoose(opt.key)}
            className={cn(
              'w-full rounded-xl border px-4 py-3 text-left transition-all',
              chosen === opt.key
                ? 'border-primary bg-primary/10 font-medium text-primary'
                : 'border-border bg-surface-1/40 hover:border-primary/40 hover:bg-surface-2/60',
            )}
          >
            {/* Option key (A/B/C/D) is always LTR; option text picks its own
                direction. `me-3` keeps spacing correct in both RTL and LTR. */}
            <span className="me-3 font-semibold" dir="ltr">
              {opt.key}.
            </span>
            <span dir="auto">{opt.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function ResultView({
  result,
  onGoToDashboard,
  lang,
}: {
  result: QuizSubmitResponse;
  onGoToDashboard: () => void;
  lang: Lang;
}) {
  const t = STR[lang];
  const isHe = lang === 'he';
  const pct = Math.round(result.score * 100);
  const passed = result.score >= 0.6;

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
  const [result, setResult] = useState<QuizSubmitResponse | null>(null);

  const handleSubmit = useCallback(async () => {
    if (submitting) return;
    setSubmitting(true);
    try {
      const answerList = quiz.questions.map((q) => ({
        item_id: q.id,
        chosen: answers[q.id] ?? 'A',
        time_spent_s: null,
      }));

      const res = await fetch(`/api/quiz/${quiz.week_id}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_id: planId,
          week_num: weekNum,
          answers: answerList,
          token,
        }),
      });

      if (res.ok) {
        const data = (await res.json()) as QuizSubmitResponse;
        setResult(data);
      }
    } catch {
      // silently fail — let user retry
    } finally {
      setSubmitting(false);
    }
  }, [answers, quiz, planId, weekNum, token, submitting]);

  // Countdown timer
  useEffect(() => {
    if (result) return;
    const id = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(id);
          handleSubmit();
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
        onGoToDashboard={() => router.push('/dashboard')}
        lang={lang}
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

      <div className="flex items-center justify-between gap-3">
        <Button
          variant="outline"
          onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
          disabled={currentIdx === 0}
        >
          {t.previous}
        </Button>

        {isLast ? (
          <Button onClick={handleSubmit} disabled={submitting} className="gap-2">
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
