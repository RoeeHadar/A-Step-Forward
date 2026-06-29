'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { Badge } from '@asf/ui/badge';
import { cn } from '@asf/ui';
import {
  CheckCircle2,
  XCircle,
  ChevronLeft,
  ChevronRight,
  Loader2,
  ClipboardList,
  Clock,
} from 'lucide-react';
import type {
  ClientMockExamQuestion,
  MockExamSubmitFeedback,
  MockExamSubmitResponse,
} from '@/lib/mock-exam-types';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import { EXAM_FORMAT_DISCLAIMER } from '@/lib/exam-disclaimer';

type Phase = 'setup' | 'exam' | 'review';

const STR = {
  he: {
    title: 'תרגול שאלות אמריקאיות',
    titleEn: 'MCQ Practice Set',
    subtitle: 'בחר מקצוע, רמה ומשך — תרגול מוגבל בזמן עם שאלות אמריקאיות ותשובות קצרות',
    subject: 'מקצוע',
    level: 'רמה',
    duration: 'משך',
    start: 'התחל תרגול',
    starting: 'מכין תרגול…',
    submit: 'הגש תרגול',
    submitting: 'מגיש…',
    prev: 'הקודם',
    next: 'הבא',
    jumpTo: 'קפיצה לשאלה',
    questionOf: (i: number, n: number) => `שאלה ${i} מתוך ${n}`,
    timeLeft: 'זמן שנותר',
    autoSubmit: 'הזמן נגמר — התרגול הוגש אוטומטית',
    estimatedScore: (s: number) => `הציון המשוער שלך: ${s}/100`,
    mcqScore: (a: number, b: number) => `שאלות אמריקאיות: ${a}/${b}`,
    yourAnswer: 'התשובה שלך',
    correctAnswer: 'תשובה נכונה',
    modelAnswer: 'תשובה לדוגמה',
    backDashboard: 'חזרה לאזור הבחינות',
    retake: 'תרגול חדש',
    openAnswer: 'כתוב את התשובה שלך…',
    kinds: { mcq: 'שאלות אמריקאיות', short_answer: 'תשובה קצרה', extended: 'שאלות פתוחות' },
    subjects: { math: 'מתמטיקה', physics: 'פיזיקה', biology: 'ביולוגיה' },
    levels: {
      '3pt': '3 יחידות',
      '4pt': '4 יחידות',
      '5pt': '5 יחידות',
      hs_physics: 'פיזיקה 5 יח״ל',
      biology_4pt: 'ביולוגיה 4 יח״ל',
      biology_5pt: 'ביולוגיה 5 יח״ל',
    },
    minutes: (n: number) => `${n} דקות`,
    points: (n: number) => `${n} נק׳`,
    reviewTitle: 'סקירת תרגול',
    openNote: 'לא נבדק אוטומטית — השווה לדוגמה',
    timerLabel: (t: string) => `⏱ ${t} נותרות`,
  },
  en: {
    title: 'MCQ Practice Set',
    titleEn: 'תרגול שאלות אמריקאיות',
    subtitle: 'Pick subject, level, and duration — timed practice with MCQ and short-answer questions',
    subject: 'Subject',
    level: 'Level',
    duration: 'Duration',
    start: 'Start Practice',
    starting: 'Preparing practice…',
    submit: 'Submit Practice',
    submitting: 'Submitting…',
    prev: 'Previous',
    next: 'Next',
    jumpTo: 'Jump to question',
    questionOf: (i: number, n: number) => `Question ${i} of ${n}`,
    timeLeft: 'Time remaining',
    autoSubmit: 'Time is up — practice submitted automatically',
    estimatedScore: (s: number) => `Your estimated score: ${s}/100`,
    mcqScore: (a: number, b: number) => `Multiple Choice: ${a}/${b}`,
    yourAnswer: 'Your answer',
    correctAnswer: 'Correct answer',
    modelAnswer: 'Model answer',
    backDashboard: 'Back to Practice Tests',
    retake: 'New practice',
    openAnswer: 'Write your answer…',
    kinds: { mcq: 'Multiple Choice', short_answer: 'Short answer', extended: 'Open Questions' },
    subjects: { math: 'Math', physics: 'Physics', biology: 'Biology' },
    levels: {
      '3pt': '3 units',
      '4pt': '4 units',
      '5pt': '5 units',
      hs_physics: 'HS Physics 5pt',
      biology_4pt: 'Biology 4pt',
      biology_5pt: 'Biology 5pt',
    },
    minutes: (n: number) => `${n} min`,
    points: (n: number) => `${n} pts`,
    reviewTitle: 'Practice Review',
    openNote: 'Not auto-graded — compare with model answer',
    timerLabel: (t: string) => `⏱ ${t} remaining`,
  },
} as const;

const SUBJECTS = ['math', 'physics', 'biology'] as const;
const LEVELS_BY_SUBJECT: Record<(typeof SUBJECTS)[number], string[]> = {
  math: ['3pt', '4pt', '5pt'],
  physics: ['hs_physics'],
  biology: ['biology_4pt', 'biology_5pt'],
};
const DURATIONS = [45, 60, 90] as const;

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function MockExamPage() {
  const [locale] = useLanguagePreference('he');
  const t = STR[locale];
  const isHe = locale === 'he';

  const [phase, setPhase] = useState<Phase>('setup');
  const [subject, setSubject] = useState<(typeof SUBJECTS)[number]>('math');
  const [level, setLevel] = useState('5pt');
  const [duration, setDuration] = useState<number>(90);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [examId, setExamId] = useState<number | null>(null);
  const [questions, setQuestions] = useState<ClientMockExamQuestion[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<MockExamSubmitResponse | null>(null);
  const startTimeRef = useRef<number>(0);
  const submittedRef = useRef(false);

  useEffect(() => {
    const levels = LEVELS_BY_SUBJECT[subject];
    if (!levels.includes(level)) setLevel(levels[0]!);
  }, [subject, level]);

  const handleSubmit = useCallback(async () => {
    if (submittedRef.current || !examId) return;
    submittedRef.current = true;
    setSubmitting(true);
    const elapsed = Math.round((Date.now() - startTimeRef.current) / 1000);
    try {
      const res = await fetch('/api/quiz/mock-exam/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exam_id: examId,
          answers,
          time_taken_seconds: elapsed,
        }),
      });
      if (!res.ok) throw new Error('Submit failed');
      const data = (await res.json()) as MockExamSubmitResponse;
      setResult(data);
      setPhase('review');
    } catch {
      submittedRef.current = false;
      setError(isHe ? 'שגיאה בהגשה — נסה שוב' : 'Submit failed — try again');
    } finally {
      setSubmitting(false);
    }
  }, [examId, answers, isHe]);

  useEffect(() => {
    if (phase !== 'exam' || secondsLeft <= 0) return;
    const id = window.setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          window.clearInterval(id);
          void handleSubmit();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => window.clearInterval(id);
  }, [phase, secondsLeft, handleSubmit]);

  async function startExam() {
    setLoading(true);
    setError(null);
    submittedRef.current = false;
    try {
      const res = await fetch('/api/quiz/mock-exam', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, level, duration_minutes: duration, locale }),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as { message?: string };
        throw new Error(err.message ?? 'Generation failed');
      }
      const data = (await res.json()) as {
        exam_id: number;
        questions: ClientMockExamQuestion[];
        duration_minutes: number;
      };
      setExamId(data.exam_id);
      setQuestions(data.questions);
      setSecondsLeft(data.duration_minutes * 60);
      startTimeRef.current = Date.now();
      setCurrentIdx(0);
      setAnswers({});
      setResult(null);
      setPhase('exam');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed');
    } finally {
      setLoading(false);
    }
  }

  function resetExam() {
    setPhase('setup');
    setExamId(null);
    setQuestions([]);
    setResult(null);
    submittedRef.current = false;
  }

  const q = questions[currentIdx];
  const feedbackMap = new Map(
    (result?.feedback_by_question ?? []).map((f) => [f.question_id, f]),
  );
  const estimatedScore =
    result && result.max_mcq > 0
      ? Math.round((result.score_mcq / result.max_mcq) * 100)
      : 0;
  const urgentTimer = secondsLeft > 0 && secondsLeft <= 600;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8" dir={isHe ? 'rtl' : 'ltr'}>
      <header className="mb-8">
        <div className="flex items-center gap-3">
          <ClipboardList className="h-8 w-8 text-primary" aria-hidden />
          <div>
            <h1 className="font-display text-2xl font-bold">{t.title}</h1>
            <p className="text-sm text-muted-foreground">{t.titleEn}</p>
          </div>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">{t.subtitle}</p>
      </header>

      <p className="mb-6 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm leading-relaxed text-foreground">
        {EXAM_FORMAT_DISCLAIMER[isHe ? 'he' : 'en']}
      </p>

      {error ? (
        <p className="mb-4 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      {phase === 'setup' ? (
        <div className="card-punch space-y-6 rounded-2xl p-6">
          <div>
            <label className="mb-2 block text-sm font-medium">{t.subject}</label>
            <div className="flex flex-wrap gap-2">
              {SUBJECTS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setSubject(s)}
                  className={cn(
                    'rounded-lg border px-4 py-2 text-sm font-medium transition-colors',
                    subject === s
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/40',
                  )}
                >
                  {t.subjects[s]}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">{t.level}</label>
            <div className="flex flex-wrap gap-2">
              {LEVELS_BY_SUBJECT[subject].map((lv) => (
                <button
                  key={lv}
                  type="button"
                  onClick={() => setLevel(lv)}
                  className={cn(
                    'rounded-lg border px-4 py-2 text-sm font-medium transition-colors',
                    level === lv
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/40',
                  )}
                >
                  {t.levels[lv as keyof typeof t.levels] ?? lv}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">{t.duration}</label>
            <div className="flex flex-wrap gap-2">
              {DURATIONS.map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDuration(d)}
                  className={cn(
                    'rounded-lg border px-4 py-2 text-sm font-medium transition-colors',
                    duration === d
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/40',
                  )}
                >
                  {t.minutes(d)}
                </button>
              ))}
            </div>
          </div>

          <Button
            onClick={() => void startExam()}
            disabled={loading}
            className="w-full bg-gradient-to-r from-primary to-accent-magenta font-semibold"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t.starting}
              </>
            ) : (
              t.start
            )}
          </Button>
        </div>
      ) : null}

      {phase === 'exam' && q ? (
        <>
          <div
            className={cn(
              'sticky top-0 z-10 mb-6 flex items-center justify-between rounded-xl border px-4 py-3 backdrop-blur',
              urgentTimer
                ? 'border-destructive bg-destructive/15 text-destructive'
                : 'border-border bg-background/95',
            )}
          >
            <div className="flex items-center gap-2 font-display text-xl font-bold">
              <Clock className="h-5 w-5" aria-hidden />
              <span>{t.timerLabel(formatTime(secondsLeft))}</span>
            </div>
            <span className="text-sm text-muted-foreground">
              {t.questionOf(currentIdx + 1, questions.length)}
            </span>
          </div>

          <div className="card-punch mb-4 rounded-2xl p-6">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <Badge variant="outline">{t.kinds[q.kind]}</Badge>
              <Badge variant="secondary">{t.points(q.points)}</Badge>
            </div>
            <p className="mb-2 text-lg font-medium leading-relaxed" dir="auto">
              {isHe ? q.stem_he : q.stem_en}
            </p>
            {!isHe ? (
              <p className="mb-4 text-sm text-muted-foreground" dir="rtl">
                {q.stem_he}
              </p>
            ) : (
              <p className="mb-4 text-sm text-muted-foreground" dir="ltr">
                {q.stem_en}
              </p>
            )}

            {q.kind === 'mcq' && q.options ? (
              <div className="space-y-2">
                {q.options.map((opt) => (
                  <label
                    key={opt.key}
                    className={cn(
                      'flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors',
                      answers[q.id] === opt.key
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/40',
                    )}
                  >
                    <input
                      type="radio"
                      name={q.id}
                      value={opt.key}
                      checked={answers[q.id] === opt.key}
                      onChange={() => setAnswers((a) => ({ ...a, [q.id]: opt.key }))}
                      className="mt-1"
                    />
                    <span dir="auto">
                      <strong>{opt.key}.</strong>{' '}
                      {isHe ? opt.text_he : opt.text_en}
                    </span>
                  </label>
                ))}
              </div>
            ) : (
              <textarea
                className="min-h-[120px] w-full rounded-lg border border-border bg-background p-3 text-sm"
                placeholder={t.openAnswer}
                value={answers[q.id] ?? ''}
                onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value }))}
                dir="auto"
              />
            )}
          </div>

          <div className="mb-4 flex flex-wrap gap-1">
            <span className="w-full text-xs text-muted-foreground">{t.jumpTo}:</span>
            {questions.map((_, i) => (
              <button
                key={questions[i]!.id}
                type="button"
                onClick={() => setCurrentIdx(i)}
                className={cn(
                  'h-8 w-8 rounded-md text-xs font-medium',
                  i === currentIdx
                    ? 'bg-primary text-primary-foreground'
                    : answers[questions[i]!.id]
                      ? 'bg-primary/20 text-primary'
                      : 'bg-muted text-muted-foreground',
                )}
              >
                {i + 1}
              </button>
            ))}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <Button
              variant="outline"
              disabled={currentIdx === 0}
              onClick={() => setCurrentIdx((i) => i - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
              {t.prev}
            </Button>
            {currentIdx < questions.length - 1 ? (
              <Button onClick={() => setCurrentIdx((i) => i + 1)}>
                {t.next}
                <ChevronRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={() => void handleSubmit()}
                disabled={submitting}
                className="bg-gradient-to-r from-primary to-accent-magenta"
              >
                {submitting ? t.submitting : t.submit}
              </Button>
            )}
          </div>
        </>
      ) : null}

      {phase === 'review' && result ? (
        <div className="space-y-6">
          <div className="card-punch rounded-2xl p-6 text-center">
            <p className="font-display text-3xl font-bold text-primary">
              {t.estimatedScore(estimatedScore)}
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              {t.mcqScore(result.score_mcq, result.max_mcq)}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">{t.openNote}</p>
          </div>

          <h2 className="font-display text-xl font-semibold">{t.reviewTitle}</h2>
          <div className="space-y-4">
            {questions.map((question, i) => {
              const fb = feedbackMap.get(question.id);
              return (
                <ReviewCard
                  key={question.id}
                  index={i + 1}
                  question={question}
                  feedback={fb}
                  answer={answers[question.id]}
                  isHe={isHe}
                  t={t}
                />
              );
            })}
          </div>

          <div className="flex flex-wrap gap-3">
            <Button variant="outline" asChild>
              <Link href="/app/exams">{t.backDashboard}</Link>
            </Button>
            <Button onClick={resetExam}>{t.retake}</Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function ReviewCard({
  index,
  question,
  feedback,
  answer,
  isHe,
  t,
}: {
  index: number;
  question: ClientMockExamQuestion;
  feedback?: MockExamSubmitFeedback;
  answer?: string;
  isHe: boolean;
  t: (typeof STR)['he'] | (typeof STR)['en'];
}) {
  const stem = isHe ? question.stem_he : question.stem_en;
  const isMcq = question.kind === 'mcq';
  const correct = feedback?.correct;

  return (
    <div className="card-punch rounded-xl p-4">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-sm font-medium">#{index}</span>
        <Badge variant="outline">{t.kinds[question.kind]}</Badge>
        {isMcq && correct === true ? (
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
        ) : isMcq && correct === false ? (
          <XCircle className="h-4 w-4 text-destructive" />
        ) : null}
      </div>
      <p className="mb-3 text-sm" dir="auto">{stem}</p>
      {answer ? (
        <p className="text-sm">
          <span className="font-medium">{t.yourAnswer}: </span>
          <span dir="auto">{answer}</span>
        </p>
      ) : null}
      {isMcq && feedback?.correct_answer ? (
        <p className="mt-1 text-sm text-emerald-600">
          <span className="font-medium">{t.correctAnswer}: </span>
          {feedback.correct_answer}
        </p>
      ) : null}
      {!isMcq && (feedback?.explanation_he || feedback?.explanation_en) ? (
        <p className="mt-2 text-sm text-muted-foreground" dir="auto">
          <span className="font-medium">{t.modelAnswer}: </span>
          {isHe ? feedback.explanation_he : feedback.explanation_en}
        </p>
      ) : null}
    </div>
  );
}
