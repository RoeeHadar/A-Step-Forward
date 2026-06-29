'use client';

/**
 * Custom AI quiz: builder ➜ runner ➜ results.
 *
 * All three views live in one client component because they share the
 * generated quiz envelope and per-item answer state. The component is
 * fully bilingual and renders right-to-left when the user's language
 * preference is Hebrew, while keeping math (`$...$`, `$$...$$`) rendered
 * left-to-right via KaTeX.
 *
 * Flow:
 *   builder ── POST /api/quiz/custom ──► running ── submit ──► results
 *                                                            ▲
 *                                              "Build another" button
 *
 * Closed kinds (mcq, true_false, numeric, short_answer) are graded on the
 * client at submit time. Open kinds get a 3-way self-assessment (correct /
 * partial / wrong) so the score is at least directionally honest. We post
 * each answered item to `/api/lesson/answer` so the mastery engine still
 * sees the practice, but the quiz envelope itself is NOT persisted — it's
 * ephemeral per session.
 */

import { useMemo, useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import {
  ChevronLeft,
  ChevronRight,
  Clock,
  Loader2,
  Search,
  Sparkles,
  Check,
  X,
  HelpCircle,
} from 'lucide-react';
import { Button } from '@asf/ui/button';
import { Badge } from '@asf/ui/badge';
import { Input } from '@asf/ui/input';
import { Textarea } from '@asf/ui/textarea';
import { Progress } from '@asf/ui/progress';
import { cn } from '@asf/ui';
import { useLanguagePreference } from '@/hooks/use-language-preference';

export interface TopicOption {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  subject_label_en: string;
  subject_label_he: string;
}

type KindMix = 'closed' | 'open' | 'mixed';

interface CustomQuizQuestion {
  ord: number;
  kind: 'mcq' | 'true_false' | 'numeric' | 'short_answer' | 'open';
  difficulty: 'easy' | 'medium' | 'hard';
  concept_id: string;
  skill_atoms: string[];
  stem_en: string;
  stem_he: string;
  explanation_en: string;
  explanation_he: string;
  options_en?: string[];
  options_he?: string[];
  correct_index?: number;
  correct_bool?: boolean;
  correct_answer?: string;
  acceptable_answers?: string[];
  rubric_en?: string;
  rubric_he?: string;
}

interface CustomQuizEnvelope {
  quiz_id: string;
  kind_mix: KindMix;
  time_limit_s: number;
  concepts: Array<{ id: string; name: string; name_he: string | null; subject: string }>;
  questions: CustomQuizQuestion[];
  picked_reason: 'user_topics' | 'weakest_mastery' | 'subject_bootstrap';
  model?: string;
}

const STR = {
  he: {
    title: 'בנה מבחן מותאם אישית',
    subtitle:
      'בחר סוג שאלות, מסגרת זמן, ונושאים אופציונליים. ה-AI יבנה מבחן בדיוק לפי מה שאתה יודע ומה שכדאי לחזק.',
    typeLabel: 'סוג שאלות',
    typeClosed: 'סגורות (בחירה / נכון-לא נכון / מספרי)',
    typeOpen: 'פתוחות (קצרות / חיבור)',
    typeMixed: 'משולב',
    timeLabel: 'מסגרת זמן (דקות)',
    timeHint: 'נשאל יותר שאלות בזמן ארוך יותר. טווח: 3–90 דקות.',
    quickTime: 'בחירה מהירה',
    topicsLabel: 'נושאים (אופציונלי)',
    topicsHint:
      'בחר נושאים מסוימים, או השאר ריק כדי שה-AI יבחר את הנושאים החלשים שלך.',
    topicsSelected: 'נבחרו {n}',
    topicsSearchPh: 'חפש נושא…',
    topicsClear: 'נקה',
    topicsExpand: 'פתח הכל',
    topicsCollapse: 'סגור הכל',
    generate: 'צור מבחן',
    generating: 'בונה מבחן…',
    genError: 'המבחן לא נוצר. נסה זמן או נושאים אחרים.',
    questionOf: 'שאלה {i} מתוך {n}',
    timeLeft: 'נשאר',
    timesUp: 'נגמר הזמן — עוד אפשר להגיש',
    prev: 'הקודמת',
    next: 'הבאה',
    submit: 'הגש מבחן',
    submitting: 'מגיש…',
    truen: 'נכון',
    falsen: 'לא נכון',
    writeAnswer: 'כתוב את התשובה כאן…',
    rubric: 'קריטריון להערכה עצמית',
    selfAssess: 'איך הייתי?',
    selfCorrect: 'נכון',
    selfPartial: 'חלקי',
    selfWrong: 'לא נכון',
    resultsTitle: 'תוצאות המבחן',
    resultsScore: 'ציון',
    resultsTime: 'זמן',
    resultsPerConcept: 'לפי נושא',
    resultsExplain: 'הסבר',
    yourAnswer: 'התשובה שלך',
    correctAnswer: 'התשובה הנכונה',
    buildAnother: 'בנה מבחן נוסף',
    newQuiz: 'מבחן חדש',
    backToDashboard: 'חזרה ללוח הבקרה',
    pickedFromTopics: 'מבוסס על הנושאים שבחרת',
    pickedFromWeak: 'מבוסס על הנושאים שאתה הכי חלש בהם',
    pickedFromBootstrap: 'התחלת היכרות — מבוסס על המקצועות שלך',
    minute: 'דקה',
    minutes: 'דקות',
  },
  en: {
    title: 'Build a custom quiz',
    subtitle:
      'Pick a question type, a time budget, and optional topics. The AI will tailor the test to what you know and what to reinforce.',
    typeLabel: 'Question type',
    typeClosed: 'Closed (MCQ / true-false / numeric)',
    typeOpen: 'Open (short answer / essay)',
    typeMixed: 'Mixed',
    timeLabel: 'Time budget (minutes)',
    timeHint: 'More minutes ➜ more questions. Range: 3–90 minutes.',
    quickTime: 'Quick picks',
    topicsLabel: 'Topics (optional)',
    topicsHint:
      'Pick specific topics, or leave empty to let the AI focus on your weakest concepts.',
    topicsSelected: '{n} selected',
    topicsSearchPh: 'Search topics…',
    topicsClear: 'Clear',
    topicsExpand: 'Expand all',
    topicsCollapse: 'Collapse all',
    generate: 'Generate quiz',
    generating: 'Building your quiz…',
    genError: 'Could not generate. Try a different time or topics.',
    questionOf: 'Question {i} of {n}',
    timeLeft: 'Left',
    timesUp: "Time's up — you can still submit",
    prev: 'Previous',
    next: 'Next',
    submit: 'Submit quiz',
    submitting: 'Submitting…',
    truen: 'True',
    falsen: 'False',
    writeAnswer: 'Write your answer here…',
    rubric: 'Self-assessment rubric',
    selfAssess: 'How did I do?',
    selfCorrect: 'Correct',
    selfPartial: 'Partial',
    selfWrong: 'Wrong',
    resultsTitle: 'Quiz results',
    resultsScore: 'Score',
    resultsTime: 'Time',
    resultsPerConcept: 'By concept',
    resultsExplain: 'Explanation',
    yourAnswer: 'Your answer',
    correctAnswer: 'Correct answer',
    buildAnother: 'Build another quiz',
    newQuiz: 'New quiz',
    backToDashboard: 'Back to dashboard',
    pickedFromTopics: 'Based on the topics you chose',
    pickedFromWeak: 'Based on the topics you struggle with most',
    pickedFromBootstrap: 'Starter quiz — based on your subjects',
    minute: 'minute',
    minutes: 'minutes',
  },
} as const;

function MarkdownInline({ content, dir }: { content: string; dir: 'rtl' | 'ltr' }) {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none" dir={dir}>
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}

function fmtT(s: number): string {
  const sign = s < 0 ? '-' : '';
  const abs = Math.abs(s);
  const m = Math.floor(abs / 60);
  const sec = (abs % 60).toString().padStart(2, '0');
  return `${sign}${m}:${sec}`;
}

function tx(s: string, params: Record<string, string | number>): string {
  return Object.entries(params).reduce(
    (acc, [k, v]) => acc.replaceAll(`{${k}}`, String(v)),
    s,
  );
}

function normalize(s: string): string {
  return s.trim().replace(/\s+/g, ' ').toLowerCase();
}

function numericClose(answer: string, correct: string): boolean {
  const a = Number.parseFloat(answer);
  const c = Number.parseFloat(correct);
  if (Number.isNaN(a) || Number.isNaN(c)) return normalize(answer) === normalize(correct);
  const tol = Math.max(1e-3, Math.abs(c) * 0.01);
  return Math.abs(a - c) <= tol;
}

interface AnswerState {
  mcq?: number;
  bool?: boolean;
  text?: string;
  self?: 'correct' | 'partial' | 'wrong';
}

type Phase = 'builder' | 'generating' | 'running' | 'results';

const QUIZ_SESSION_KEY = 'asf-quiz-session';

interface QuizSessionPersist {
  phase: 'running' | 'results';
  envelope: CustomQuizEnvelope;
  answers: AnswerState[];
  cursor: number;
  secondsLeft: number;
  startedAt: number | null;
  kindMix: KindMix;
  timeMin: number;
  selected: string[];
  results: {
    correctCount: number;
    total: number;
    perConcept: Record<string, { correct: number; total: number }>;
    secondsUsed: number;
  } | null;
}

function saveQuizSession(data: QuizSessionPersist) {
  try {
    sessionStorage.setItem(QUIZ_SESSION_KEY, JSON.stringify(data));
  } catch {
    // ignore quota / private mode
  }
}

function clearQuizSession() {
  try {
    sessionStorage.removeItem(QUIZ_SESSION_KEY);
  } catch {
    // ignore
  }
}

const QUICK_TIMES = [5, 10, 15, 30, 45];

export function QuizPageClient({ topics }: { topics: TopicOption[] }) {
  const [language] = useLanguagePreference();
  const lang = language === 'he' ? 'he' : 'en';
  const t = STR[lang];
  const isHe = lang === 'he';
  const dir: 'rtl' | 'ltr' = isHe ? 'rtl' : 'ltr';

  const [phase, setPhase] = useState<Phase>('builder');
  const [kindMix, setKindMix] = useState<KindMix>('mixed');
  const [timeMin, setTimeMin] = useState(10);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState('');
  const [genError, setGenError] = useState<string | null>(null);

  const [envelope, setEnvelope] = useState<CustomQuizEnvelope | null>(null);
  const [answers, setAnswers] = useState<AnswerState[]>([]);
  const [cursor, setCursor] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState<null | {
    correctCount: number;
    total: number;
    perConcept: Record<string, { correct: number; total: number }>;
    secondsUsed: number;
  }>(null);
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // All hooks must be called unconditionally; this one is read inside the
  // builder branch but lives up here to satisfy the rules of hooks.
  const grouped = useMemoGroupedTopics(topics, isHe, search);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(QUIZ_SESSION_KEY);
      if (raw) {
        const saved = JSON.parse(raw) as QuizSessionPersist;
        if (
          saved.envelope?.questions?.length &&
          (saved.phase === 'running' || saved.phase === 'results')
        ) {
          setEnvelope(saved.envelope);
          setAnswers(
            saved.answers?.length === saved.envelope.questions.length
              ? saved.answers
              : saved.envelope.questions.map(() => ({} as AnswerState)),
          );
          setCursor(saved.cursor ?? 0);
          setSecondsLeft(saved.secondsLeft ?? saved.envelope.time_limit_s);
          setStartedAt(saved.startedAt ?? null);
          setKindMix(saved.kindMix ?? 'mixed');
          setTimeMin(saved.timeMin ?? 10);
          setSelected(new Set(saved.selected ?? []));
          setResults(saved.results ?? null);
          setPhase(saved.phase);
        }
      }
    } catch {
      clearQuizSession();
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated || !envelope || phase === 'builder' || phase === 'generating') return;
    saveQuizSession({
      phase: phase === 'results' ? 'results' : 'running',
      envelope,
      answers,
      cursor,
      secondsLeft,
      startedAt,
      kindMix,
      timeMin,
      selected: Array.from(selected),
      results,
    });
  }, [
    hydrated,
    phase,
    envelope,
    answers,
    cursor,
    secondsLeft,
    startedAt,
    results,
    kindMix,
    timeMin,
    selected,
  ]);

  useEffect(() => {
    if (phase !== 'running' || !envelope) return;
    const id = setInterval(() => {
      setSecondsLeft((prev) => (prev <= -3600 ? prev : prev - 1));
    }, 1000);
    return () => clearInterval(id);
  }, [phase, envelope]);

  function toggleTopic(id: string) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelected(next);
  }

  function clearTopics() {
    setSelected(new Set());
    setSearch('');
  }

  async function generate() {
    setGenError(null);
    setPhase('generating');
    try {
      const resp = await fetch('/api/quiz/custom', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          kind_mix: kindMix,
          time_limit_min: timeMin,
          topics: Array.from(selected),
        }),
      });
      if (!resp.ok) {
        const body = (await resp.json().catch(() => null)) as {
          message?: string;
        } | null;
        setGenError(body?.message ?? t.genError);
        setPhase('builder');
        return;
      }
      const env = (await resp.json()) as CustomQuizEnvelope;
      setEnvelope(env);
      setAnswers(env.questions.map(() => ({} as AnswerState)));
      setCursor(0);
      setSecondsLeft(env.time_limit_s);
      setStartedAt(Date.now());
      setResults(null);
      setPhase('running');
    } catch {
      setGenError(t.genError);
      setPhase('builder');
    }
  }

  function gradeOne(q: CustomQuizQuestion, a: AnswerState): boolean | null {
    if (q.kind === 'mcq') {
      if (a.mcq == null || q.correct_index == null) return null;
      return a.mcq === q.correct_index;
    }
    if (q.kind === 'true_false') {
      if (a.bool == null || q.correct_bool == null) return null;
      return a.bool === q.correct_bool;
    }
    if (q.kind === 'numeric') {
      if (!a.text || !q.correct_answer) return null;
      return numericClose(a.text, q.correct_answer);
    }
    if (q.kind === 'short_answer') {
      if (!a.text || !q.acceptable_answers) return null;
      const norm = normalize(a.text);
      return q.acceptable_answers.some((x) => normalize(x) === norm);
    }
    if (q.kind === 'open') {
      if (!a.self) return null;
      return a.self === 'correct';
    }
    return null;
  }

  async function submitQuiz() {
    if (!envelope) return;
    setSubmitting(true);
    const perConcept: Record<string, { correct: number; total: number }> = {};
    let correctCount = 0;
    for (let i = 0; i < envelope.questions.length; i += 1) {
      const q = envelope.questions[i];
      if (!q) continue;
      const a = answers[i] ?? {};
      const graded = gradeOne(q, a);
      const isCorrect = graded === true;
      if (isCorrect) correctCount += 1;
      const bucket = (perConcept[q.concept_id] ??= { correct: 0, total: 0 });
      bucket.total += 1;
      if (isCorrect) bucket.correct += 1;
      // Best-effort: record practice against the regular mastery pipeline
      // so this quiz feeds skill_practice + concept_mastery just like an
      // authored-lesson answer. Failure here is silent — the UI still
      // shows results either way.
      try {
        if (graded != null) {
          await fetch('/api/lesson/answer', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({
              lesson_id: envelope.quiz_id,
              question_id: `${envelope.quiz_id}:${q.ord}`,
              concept_id: q.concept_id,
              correct: isCorrect,
              skill_atoms: q.skill_atoms ?? [],
              user_answer: a,
              kind: q.kind,
              ephemeral: true,
            }),
          });
        }
      } catch {
        // ignore
      }
    }
    const secondsUsed = startedAt ? Math.round((Date.now() - startedAt) / 1000) : 0;
    setResults({
      correctCount,
      total: envelope.questions.length,
      perConcept,
      secondsUsed,
    });
    setPhase('results');
    setSubmitting(false);
  }

  function resetToBuilder() {
    clearQuizSession();
    setEnvelope(null);
    setAnswers([]);
    setResults(null);
    setCursor(0);
    setPhase('builder');
  }

  // ---------- builder ------------------------------------------------------
  if (phase === 'builder' || phase === 'generating') {
    return (
      <div className="mx-auto max-w-3xl" dir={dir}>
        <header className="mb-6">
          <h1 className="font-display text-3xl font-bold">{t.title}</h1>
          <p className="mt-2 text-muted-foreground">{t.subtitle}</p>
        </header>

        <section className="card-punch mb-6 rounded-2xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            {t.typeLabel}
          </h2>
          <div className="mt-3 grid gap-2 sm:grid-cols-3">
            {(['closed', 'open', 'mixed'] as const).map((k) => {
              const label =
                k === 'closed' ? t.typeClosed : k === 'open' ? t.typeOpen : t.typeMixed;
              const selectedNow = kindMix === k;
              return (
                <button
                  key={k}
                  type="button"
                  onClick={() => setKindMix(k)}
                  className={cn(
                    'rounded-xl border px-4 py-3 text-start text-sm transition-colors',
                    selectedNow
                      ? 'border-primary bg-primary/10 text-foreground'
                      : 'border-border bg-background hover:bg-muted',
                  )}
                  aria-pressed={selectedNow}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </section>

        <section className="card-punch mb-6 rounded-2xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            {t.timeLabel}
          </h2>
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <Input
              type="number"
              min={3}
              max={90}
              value={timeMin}
              onChange={(e) => {
                const n = Number(e.target.value);
                if (Number.isFinite(n)) setTimeMin(Math.max(3, Math.min(90, Math.round(n))));
              }}
              className="w-28"
              inputMode="numeric"
            />
            <span className="text-sm text-muted-foreground">
              {timeMin === 1 ? t.minute : t.minutes}
            </span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">{t.timeHint}</p>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="text-xs text-muted-foreground">{t.quickTime}:</span>
            {QUICK_TIMES.map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => setTimeMin(n)}
                className={cn(
                  'rounded-full border px-3 py-1 text-xs transition-colors',
                  timeMin === n
                    ? 'border-primary bg-primary/10 text-foreground'
                    : 'border-border bg-background text-muted-foreground hover:bg-muted',
                )}
              >
                {n}
              </button>
            ))}
          </div>
        </section>

        <section className="card-punch mb-6 rounded-2xl p-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              {t.topicsLabel}
            </h2>
            <Badge variant="secondary">
              {tx(t.topicsSelected, { n: selected.size })}
            </Badge>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">{t.topicsHint}</p>
          <div className="mt-3 flex items-center gap-2">
            <div className="relative flex-1">
              <Search
                className="absolute start-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
                aria-hidden
              />
              <Input
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t.topicsSearchPh}
                className="ps-8"
                dir={dir}
              />
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearTopics}
              disabled={selected.size === 0 && search.length === 0}
            >
              {t.topicsClear}
            </Button>
          </div>

          <div className="mt-3 max-h-72 overflow-y-auto rounded-lg border border-border">
            {grouped.length === 0 ? (
              <p className="p-4 text-sm text-muted-foreground">—</p>
            ) : (
              grouped.map((g) => (
                <div key={g.subject} className="border-b border-border last:border-b-0">
                  <div className="bg-muted/40 px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    {g.label}
                  </div>
                  <ul>
                    {g.items.map((c) => {
                      const checked = selected.has(c.id);
                      const display = isHe && c.name_he ? c.name_he : c.name;
                      return (
                        <li key={c.id}>
                          <button
                            type="button"
                            onClick={() => toggleTopic(c.id)}
                            className={cn(
                              'flex w-full items-center justify-between gap-2 px-3 py-1.5 text-start text-sm transition-colors hover:bg-muted/50',
                              checked && 'bg-primary/5',
                            )}
                            aria-pressed={checked}
                          >
                            <span className="truncate" dir="auto">
                              {display}
                            </span>
                            {checked ? (
                              <Check className="h-4 w-4 shrink-0 text-primary" aria-hidden />
                            ) : null}
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))
            )}
          </div>
        </section>

        {genError ? (
          <p className="mb-3 text-sm text-destructive" role="alert">
            {genError}
          </p>
        ) : null}

        <div className="flex flex-wrap items-center gap-3">
          <Button
            size="lg"
            onClick={generate}
            disabled={phase === 'generating'}
            className="gap-2"
          >
            {phase === 'generating' ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : (
              <Sparkles className="h-4 w-4" aria-hidden />
            )}
            {phase === 'generating' ? t.generating : t.generate}
          </Button>
        </div>
      </div>
    );
  }

  // ---------- running ------------------------------------------------------
  if (phase === 'running' && envelope) {
    const q = envelope.questions[cursor];
    if (!q) return null;
    const a = answers[cursor] ?? {};
    const total = envelope.questions.length;
    const stem = isHe ? q.stem_he : q.stem_en;
    const options = isHe ? q.options_he : q.options_en;
    const overdue = secondsLeft < 0;
    const reasonStr =
      envelope.picked_reason === 'user_topics'
        ? t.pickedFromTopics
        : envelope.picked_reason === 'weakest_mastery'
          ? t.pickedFromWeak
          : t.pickedFromBootstrap;

    function setAnswer(patch: AnswerState) {
      setAnswers((prev) => {
        const copy = [...prev];
        copy[cursor] = { ...(copy[cursor] ?? {}), ...patch };
        return copy;
      });
    }

    return (
      <div className="mx-auto max-w-3xl" dir={dir}>
        <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0">
            <h1 className="truncate font-display text-2xl font-bold">{t.title}</h1>
            <p className="mt-1 text-xs text-muted-foreground">{reasonStr}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="ghost" size="sm" onClick={resetToBuilder}>
              {t.newQuiz}
            </Button>
            <div
              className={cn(
                'inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-mono',
                overdue
                  ? 'border-destructive bg-destructive/10 text-destructive'
                  : 'border-border bg-muted/40 text-foreground',
              )}
            >
              <Clock className="h-4 w-4" aria-hidden />
              <span>{overdue ? t.timesUp : `${t.timeLeft} ${fmtT(secondsLeft)}`}</span>
            </div>
          </div>
        </header>

        <Progress
          value={((cursor + 1) / total) * 100}
          className="mb-4 h-2 overflow-hidden rounded-full bg-secondary [&>div]:rounded-full [&>div]:bg-gradient-to-r [&>div]:from-primary [&>div]:to-accent-cyan"
        />

        <section className="card-punch rounded-2xl p-6">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <Badge variant="secondary">{tx(t.questionOf, { i: cursor + 1, n: total })}</Badge>
            <Badge
              className={cn(
                q.difficulty === 'easy' && 'bg-emerald-500/10 text-emerald-400',
                q.difficulty === 'medium' && 'bg-accent-amber/10 text-accent-amber',
                q.difficulty === 'hard' && 'bg-destructive/10 text-destructive',
              )}
              variant="secondary"
            >
              {q.difficulty}
            </Badge>
            <Badge variant="outline">{q.kind}</Badge>
          </div>

          <MarkdownInline content={stem} dir={dir} />

          <div className="mt-4">
            {q.kind === 'mcq' && options ? (
              <ul className="space-y-2">
                {options.map((opt, idx) => {
                  const selectedNow = a.mcq === idx;
                  return (
                    <li key={idx}>
                      <button
                        type="button"
                        onClick={() => setAnswer({ mcq: idx })}
                        className={cn(
                          'w-full rounded-lg border px-4 py-3 text-start text-sm transition-colors',
                          selectedNow
                            ? 'border-primary bg-primary/10'
                            : 'border-border bg-background hover:bg-muted',
                        )}
                        aria-pressed={selectedNow}
                      >
                        <MarkdownInline content={opt} dir={dir} />
                      </button>
                    </li>
                  );
                })}
              </ul>
            ) : null}

            {q.kind === 'true_false' ? (
              <div className="flex gap-2">
                {[
                  { v: true, label: t.truen },
                  { v: false, label: t.falsen },
                ].map((opt) => {
                  const selectedNow = a.bool === opt.v;
                  return (
                    <button
                      key={String(opt.v)}
                      type="button"
                      onClick={() => setAnswer({ bool: opt.v })}
                      className={cn(
                        'flex-1 rounded-lg border px-4 py-3 text-sm transition-colors',
                        selectedNow
                          ? 'border-primary bg-primary/10'
                          : 'border-border bg-background hover:bg-muted',
                      )}
                      aria-pressed={selectedNow}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            ) : null}

            {q.kind === 'numeric' || q.kind === 'short_answer' ? (
              <Input
                type="text"
                value={a.text ?? ''}
                onChange={(e) => setAnswer({ text: e.target.value })}
                placeholder={t.writeAnswer}
                dir="auto"
              />
            ) : null}

            {q.kind === 'open' ? (
              <div className="space-y-3">
                <Textarea
                  rows={6}
                  value={a.text ?? ''}
                  onChange={(e) => setAnswer({ text: e.target.value })}
                  placeholder={t.writeAnswer}
                  dir="auto"
                />
                {q.rubric_en || q.rubric_he ? (
                  <div className="rounded-lg border border-dashed border-border p-3 text-xs text-muted-foreground">
                    <div className="mb-1 inline-flex items-center gap-1 font-semibold uppercase tracking-wider">
                      <HelpCircle className="h-3 w-3" aria-hidden />
                      {t.rubric}
                    </div>
                    <MarkdownInline content={isHe ? q.rubric_he ?? '' : q.rubric_en ?? ''} dir={dir} />
                  </div>
                ) : null}
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs text-muted-foreground">{t.selfAssess}</span>
                  {(['correct', 'partial', 'wrong'] as const).map((s) => {
                    const label =
                      s === 'correct' ? t.selfCorrect : s === 'partial' ? t.selfPartial : t.selfWrong;
                    const selectedNow = a.self === s;
                    return (
                      <button
                        key={s}
                        type="button"
                        onClick={() => setAnswer({ self: s })}
                        className={cn(
                          'rounded-full border px-3 py-1 text-xs transition-colors',
                          selectedNow
                            ? 'border-primary bg-primary/10'
                            : 'border-border bg-background text-muted-foreground hover:bg-muted',
                        )}
                        aria-pressed={selectedNow}
                      >
                        {label}
                      </button>
                    );
                  })}
                </div>
              </div>
            ) : null}
          </div>
        </section>

        <div className="mt-6 flex items-center justify-between gap-2">
          <Button
            variant="outline"
            onClick={() => setCursor((c) => Math.max(0, c - 1))}
            disabled={cursor === 0}
            className="gap-2"
          >
            {isHe ? <ChevronRight className="h-4 w-4" aria-hidden /> : <ChevronLeft className="h-4 w-4" aria-hidden />}
            {t.prev}
          </Button>
          {cursor < total - 1 ? (
            <Button onClick={() => setCursor((c) => Math.min(total - 1, c + 1))} className="gap-2">
              {t.next}
              {isHe ? <ChevronLeft className="h-4 w-4" aria-hidden /> : <ChevronRight className="h-4 w-4" aria-hidden />}
            </Button>
          ) : (
            <Button onClick={submitQuiz} disabled={submitting} className="gap-2">
              {submitting ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : null}
              {submitting ? t.submitting : t.submit}
            </Button>
          )}
        </div>
      </div>
    );
  }

  // ---------- results ------------------------------------------------------
  if (phase === 'results' && envelope && results) {
    const percent =
      results.total > 0 ? Math.round((results.correctCount / results.total) * 100) : 0;
    return (
      <div className="mx-auto max-w-3xl" dir={dir}>
        <header className="mb-6">
          <h1 className="font-display text-3xl font-bold">{t.resultsTitle}</h1>
        </header>

        <section className="card-punch mb-6 rounded-2xl p-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <Stat label={t.resultsScore} value={`${results.correctCount}/${results.total}`} sub={`${percent}%`} />
            <Stat label={t.resultsTime} value={fmtT(results.secondsUsed)} />
          </div>
        </section>

        <section className="card-punch mb-6 rounded-2xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            {t.resultsPerConcept}
          </h2>
          <ul className="mt-3 space-y-2">
            {envelope.concepts.map((c) => {
              const bucket = results.perConcept[c.id];
              if (!bucket) return null;
              const pct = bucket.total > 0 ? Math.round((bucket.correct / bucket.total) * 100) : 0;
              const name = isHe && c.name_he ? c.name_he : c.name;
              return (
                <li key={c.id} className="space-y-1">
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-sm" dir="auto">
                      {name}
                    </span>
                    <Badge variant={pct >= 70 ? 'success' : 'secondary'}>
                      {bucket.correct}/{bucket.total} · {pct}%
                    </Badge>
                  </div>
                  <Progress
                    value={pct}
                    className="h-1.5 overflow-hidden rounded-full bg-secondary [&>div]:rounded-full [&>div]:bg-gradient-to-r [&>div]:from-primary [&>div]:to-accent-cyan"
                  />
                </li>
              );
            })}
          </ul>
        </section>

        <section className="card-punch mb-6 rounded-2xl p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            {t.resultsExplain}
          </h2>
          <ul className="mt-3 space-y-4">
            {envelope.questions.map((q, i) => {
              const a = answers[i] ?? {};
              const graded = gradeOne(q, a);
              const stem = isHe ? q.stem_he : q.stem_en;
              const explanation = isHe ? q.explanation_he : q.explanation_en;
              return (
                <li key={i} className="border-b border-border pb-4 last:border-b-0">
                  <div className="mb-2 flex items-center gap-2">
                    <span className="font-mono text-xs text-muted-foreground">#{i + 1}</span>
                    {graded === true ? (
                      <Badge variant="success" className="gap-1">
                        <Check className="h-3 w-3" aria-hidden />
                        {t.selfCorrect}
                      </Badge>
                    ) : graded === false ? (
                      <Badge
                        variant="secondary"
                        className="gap-1 bg-destructive/15 text-destructive"
                      >
                        <X className="h-3 w-3" aria-hidden />
                        {t.selfWrong}
                      </Badge>
                    ) : (
                      <Badge variant="secondary">—</Badge>
                    )}
                  </div>
                  <MarkdownInline content={stem} dir={dir} />
                  <div className="mt-2 text-xs text-muted-foreground">
                    <strong>{t.yourAnswer}:</strong>{' '}
                    {a.mcq != null
                      ? `#${a.mcq + 1}`
                      : a.bool != null
                        ? a.bool
                          ? t.truen
                          : t.falsen
                        : a.text ?? '—'}
                  </div>
                  {q.correct_index != null || q.correct_bool != null || q.correct_answer || q.acceptable_answers ? (
                    <div className="mt-1 text-xs text-muted-foreground">
                      <strong>{t.correctAnswer}:</strong>{' '}
                      {q.correct_index != null
                        ? `#${q.correct_index + 1}`
                        : q.correct_bool != null
                          ? q.correct_bool
                            ? t.truen
                            : t.falsen
                          : q.correct_answer
                            ? q.correct_answer
                            : q.acceptable_answers?.join(' · ')}
                    </div>
                  ) : null}
                  <div className="mt-2">
                    <MarkdownInline content={explanation} dir={dir} />
                  </div>
                </li>
              );
            })}
          </ul>
        </section>

        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={resetToBuilder} className="gap-2">
            <Sparkles className="h-4 w-4" aria-hidden />
            {t.buildAnother}
          </Button>
          <Button variant="outline" asChild>
            <a href="/app">{t.backToDashboard}</a>
          </Button>
        </div>
      </div>
    );
  }

  return null;
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="mt-1 font-display text-2xl font-bold">{value}</p>
      {sub ? <p className="text-xs text-muted-foreground">{sub}</p> : null}
    </div>
  );
}

function useMemoGroupedTopics(topics: TopicOption[], isHe: boolean, search: string) {
  return useMemo(() => {
    const q = search.trim().toLowerCase();
    const filtered = q
      ? topics.filter((c) => {
          const a = c.name.toLowerCase();
          const b = (c.name_he ?? '').toLowerCase();
          return a.includes(q) || b.includes(q);
        })
      : topics;
    const bySubject = new Map<string, { label: string; items: TopicOption[] }>();
    for (const c of filtered) {
      const label = isHe ? c.subject_label_he : c.subject_label_en;
      const bucket = bySubject.get(c.subject);
      if (bucket) bucket.items.push(c);
      else bySubject.set(c.subject, { label, items: [c] });
    }
    for (const bucket of bySubject.values()) {
      bucket.items.sort((a, b) => {
        const an = isHe && a.name_he ? a.name_he : a.name;
        const bn = isHe && b.name_he ? b.name_he : b.name;
        return an.localeCompare(bn);
      });
    }
    return Array.from(bySubject.entries()).map(([subject, v]) => ({
      subject,
      label: v.label,
      items: v.items,
    }));
  }, [topics, isHe, search]);
}
