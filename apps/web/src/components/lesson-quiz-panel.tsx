'use client';

import { useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { Check, X, HelpCircle, Sparkles } from 'lucide-react';
import type { LessonQuestionRow, LessonWithQuestions } from '@/lib/neon-db';

type Lang = 'en' | 'he';

const DIFFICULTY_TINT: Record<LessonQuestionRow['difficulty'], string> = {
  easy: 'bg-emerald-500/10 text-emerald-400',
  medium: 'bg-accent-amber/10 text-accent-amber',
  hard: 'bg-destructive/10 text-destructive',
};

const KIND_LABEL: Record<
  LessonQuestionRow['kind'],
  { en: string; he: string }
> = {
  mcq: { en: 'Multiple choice', he: 'בחירה מרובה' },
  open: { en: 'Open answer', he: 'תשובה פתוחה' },
  fill_blank: { en: 'Fill in the blank', he: 'השלמת חסר' },
  numeric: { en: 'Numeric', he: 'מספרי' },
};

function MarkdownInline({ content }: { content: string }) {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

function normalizeAnswer(s: string): string {
  return s.trim().toLowerCase().replace(/\s+/g, ' ');
}

function numericClose(a: string, b: string): boolean {
  const na = Number.parseFloat(a);
  const nb = Number.parseFloat(b);
  if (Number.isNaN(na) || Number.isNaN(nb)) return false;
  const tol = Math.max(1e-3, Math.abs(nb) * 0.01);
  return Math.abs(na - nb) <= tol;
}

interface AnswerState {
  submitted: boolean;
  correct: boolean | null;
  userInput: string | number | null;
  selfAssessed: 'correct' | 'partial' | 'wrong' | null;
}

function QuestionCard({
  question,
  lang,
  lessonId,
  conceptId,
  onAnswered,
}: {
  question: LessonQuestionRow;
  lang: Lang;
  lessonId: string;
  conceptId: string;
  onAnswered: (q: LessonQuestionRow, correct: boolean) => void;
}) {
  const [state, setState] = useState<AnswerState>({
    submitted: false,
    correct: null,
    userInput: null,
    selfAssessed: null,
  });
  const [revealed, setRevealed] = useState(false);
  const [openText, setOpenText] = useState('');
  const [busy, setBusy] = useState(false);

  const dir = lang === 'he' ? 'rtl' : 'ltr';
  const stem = lang === 'he' ? question.stem_he : question.stem_en;
  const explanation = lang === 'he' ? question.explanation_he : question.explanation_en;
  const rubric = lang === 'he' ? question.rubric_he : question.rubric_en;
  const options = lang === 'he' ? question.options_he : question.options_en;
  const kindLabel = KIND_LABEL[question.kind][lang];

  async function reportAnswer(correct: boolean) {
    if (busy) return;
    setBusy(true);
    onAnswered(question, correct);
    try {
      await fetch('/api/lesson/answer', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          lesson_id: lessonId,
          question_id: question.id,
          concept_id: conceptId,
          correct,
          skill_atoms: question.skill_atoms ?? [],
        }),
      });
    } catch {
      // Network is best-effort; UI feedback already shown.
    } finally {
      setBusy(false);
    }
  }

  function handleMcq(idx: number) {
    if (state.submitted) return;
    const correct = idx === question.correct_index;
    setState({ submitted: true, correct, userInput: idx, selfAssessed: null });
    void reportAnswer(correct);
  }

  function handleNumericOrFill() {
    if (state.submitted) return;
    const expected = question.correct_answer ?? '';
    const correct =
      question.kind === 'numeric'
        ? numericClose(openText, expected)
        : normalizeAnswer(openText) === normalizeAnswer(expected);
    setState({ submitted: true, correct, userInput: openText, selfAssessed: null });
    void reportAnswer(correct);
  }

  function handleSelfAssess(grade: 'correct' | 'partial' | 'wrong') {
    if (state.submitted) return;
    const correct = grade !== 'wrong';
    setState({ submitted: true, correct, userInput: openText, selfAssessed: grade });
    void reportAnswer(correct);
  }

  return (
    <div className="glass-surface rounded-2xl border-border/60 p-5" dir={dir}>
      <div className="mb-3 flex flex-wrap items-center gap-2 text-[10px] font-semibold uppercase">
        <span className="rounded-full bg-muted px-2 py-0.5 text-muted-foreground">
          #{question.ord}
        </span>
        <span className="rounded-full bg-muted px-2 py-0.5 text-muted-foreground">
          {kindLabel}
        </span>
        <span
          className={`rounded-full px-2 py-0.5 ${DIFFICULTY_TINT[question.difficulty]}`}
        >
          {question.difficulty}
        </span>
      </div>

      <div className="mb-4 text-base font-medium text-foreground">
        <MarkdownInline content={stem} />
      </div>

      {question.kind === 'mcq' && options ? (
        <div className="space-y-2">
          {options.map((opt, i) => {
            const isUser = state.userInput === i;
            const isCorrect = i === question.correct_index;
            let cls = 'border-border bg-surface-1/50 hover:border-primary/40';
            if (state.submitted) {
              if (isCorrect) cls = 'border-emerald-500/60 bg-emerald-500/10';
              else if (isUser) cls = 'border-destructive/60 bg-destructive/10';
              else cls = 'border-border/30 bg-surface-1/30 opacity-60';
            }
            return (
              <button
                key={i}
                type="button"
                disabled={state.submitted || busy}
                onClick={() => handleMcq(i)}
                className={`flex w-full items-start gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-colors ${cls}`}
              >
                <span className="font-mono text-xs text-muted-foreground">
                  {String.fromCharCode(65 + i)}.
                </span>
                <span className="flex-1">
                  <MarkdownInline content={opt} />
                </span>
                {state.submitted && isCorrect ? (
                  <Check className="h-4 w-4 text-emerald-500" />
                ) : null}
                {state.submitted && isUser && !isCorrect ? (
                  <X className="h-4 w-4 text-destructive" />
                ) : null}
              </button>
            );
          })}
        </div>
      ) : null}

      {(question.kind === 'numeric' || question.kind === 'fill_blank') && !state.submitted ? (
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            type={question.kind === 'numeric' ? 'text' : 'text'}
            value={openText}
            onChange={(e) => setOpenText(e.target.value)}
            placeholder={
              lang === 'he'
                ? question.kind === 'numeric'
                  ? 'הקלידו תשובה מספרית'
                  : 'הקלידו תשובה'
                : question.kind === 'numeric'
                  ? 'Enter a number'
                  : 'Type your answer'
            }
            className="flex-1 rounded-lg border border-border bg-surface-1/50 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            dir={dir}
          />
          <button
            type="button"
            onClick={handleNumericOrFill}
            disabled={!openText.trim() || busy}
            className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
          >
            {lang === 'he' ? 'בדקו' : 'Check'}
          </button>
        </div>
      ) : null}

      {question.kind === 'open' && !state.submitted ? (
        <div className="space-y-3">
          <textarea
            value={openText}
            onChange={(e) => setOpenText(e.target.value)}
            rows={4}
            placeholder={
              lang === 'he'
                ? 'כתבו את הפתרון שלכם כאן…'
                : 'Write your reasoning here…'
            }
            className="w-full rounded-lg border border-border bg-surface-1/50 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            dir={dir}
          />
          <button
            type="button"
            onClick={() => setRevealed(true)}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-surface-1/50 px-3 py-2 text-xs font-medium hover:border-primary/40"
          >
            <Sparkles className="h-3.5 w-3.5" />
            {lang === 'he' ? 'הראו פתרון מודל ומחווני ניקוד' : 'Reveal model answer + rubric'}
          </button>
          {revealed && rubric ? (
            <div className="rounded-lg border border-border/60 bg-surface-1/40 p-3 text-xs">
              <p className="mb-2 font-semibold uppercase tracking-wide text-muted-foreground">
                {lang === 'he' ? 'מחוון' : 'Rubric'}
              </p>
              <MarkdownInline content={rubric} />
              <p className="mt-3 mb-1 font-semibold uppercase tracking-wide text-muted-foreground">
                {lang === 'he' ? 'הסבר' : 'Explanation'}
              </p>
              <MarkdownInline content={explanation} />
              <div className="mt-3 flex flex-wrap items-center gap-2">
                <span className="text-[11px] text-muted-foreground">
                  {lang === 'he' ? 'איך הייתם מדרגים את עצמכם?' : 'How would you grade yourself?'}
                </span>
                <button
                  type="button"
                  onClick={() => handleSelfAssess('correct')}
                  className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400 hover:bg-emerald-500/20"
                >
                  {lang === 'he' ? 'נכון' : 'Correct'}
                </button>
                <button
                  type="button"
                  onClick={() => handleSelfAssess('partial')}
                  className="rounded-full bg-accent-amber/10 px-3 py-1 text-xs font-medium text-accent-amber hover:bg-accent-amber/20"
                >
                  {lang === 'he' ? 'חלקי' : 'Partial'}
                </button>
                <button
                  type="button"
                  onClick={() => handleSelfAssess('wrong')}
                  className="rounded-full bg-destructive/10 px-3 py-1 text-xs font-medium text-destructive hover:bg-destructive/20"
                >
                  {lang === 'he' ? 'לא נכון' : 'Wrong'}
                </button>
              </div>
            </div>
          ) : null}
        </div>
      ) : null}

      {state.submitted ? (
        <div
          className={`mt-4 rounded-lg border p-3 text-sm ${
            state.correct
              ? 'border-emerald-500/40 bg-emerald-500/5'
              : 'border-destructive/40 bg-destructive/5'
          }`}
        >
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
            {state.correct ? (
              <>
                <Check className="h-4 w-4 text-emerald-500" />
                <span className="text-emerald-500">
                  {lang === 'he' ? 'נכון' : 'Correct'}
                </span>
              </>
            ) : (
              <>
                <X className="h-4 w-4 text-destructive" />
                <span className="text-destructive">
                  {lang === 'he' ? 'לא לגמרי' : 'Not quite'}
                </span>
              </>
            )}
            {question.kind !== 'mcq' && question.correct_answer ? (
              <span className="ms-2 text-xs font-normal text-muted-foreground">
                {lang === 'he' ? 'תשובה: ' : 'Answer: '}
                <code className="rounded bg-muted px-1 py-0.5 font-mono">
                  {question.correct_answer}
                </code>
              </span>
            ) : null}
          </div>
          <MarkdownInline content={explanation} />
        </div>
      ) : null}
    </div>
  );
}

export function LessonQuizPanel({
  data,
  lang,
  conceptId,
}: {
  data: LessonWithQuestions;
  lang: Lang;
  conceptId: string;
}) {
  const { lesson, questions } = data;
  const [score, setScore] = useState({ answered: 0, correct: 0 });

  const totalEasy = useMemo(
    () => questions.filter((q) => q.difficulty === 'easy').length,
    [questions],
  );
  const totalMedium = useMemo(
    () => questions.filter((q) => q.difficulty === 'medium').length,
    [questions],
  );
  const totalHard = useMemo(
    () => questions.filter((q) => q.difficulty === 'hard').length,
    [questions],
  );

  if (questions.length === 0) return null;

  return (
    <section className="mt-8 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <HelpCircle className="h-5 w-5 text-primary" />
          <h2 className="font-display text-xl font-semibold">
            {lang === 'he' ? 'בדקו את עצמכם' : 'Test yourself'}
          </h2>
        </div>
        <div className="flex items-center gap-3 text-[11px] uppercase tracking-wide text-muted-foreground">
          <span>
            {lang === 'he' ? 'קל' : 'Easy'}: {totalEasy}
          </span>
          <span>
            {lang === 'he' ? 'בינוני' : 'Medium'}: {totalMedium}
          </span>
          <span>
            {lang === 'he' ? 'קשה' : 'Hard'}: {totalHard}
          </span>
          <span className="rounded-full bg-primary/10 px-2 py-0.5 font-semibold text-primary">
            {score.correct}/{score.answered}
          </span>
        </div>
      </div>

      {questions.map((q) => (
        <QuestionCard
          key={q.id}
          question={q}
          lang={lang}
          lessonId={lesson.id}
          conceptId={conceptId}
          onAnswered={(_, correct) =>
            setScore((s) => ({ answered: s.answered + 1, correct: s.correct + (correct ? 1 : 0) }))
          }
        />
      ))}
    </section>
  );
}
