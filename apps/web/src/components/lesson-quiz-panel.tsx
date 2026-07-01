'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { MarkdownMath } from '@/components/markdown-math';
import { Check, X, HelpCircle, ChevronUp, ChevronDown, Pencil, Eye, EyeOff } from 'lucide-react';
import type {
  LessonQuestionKind,
  LessonPointsLevel,
  LessonQuestionRow,
  LessonWithQuestions,
} from '@/lib/neon-db';

const LEVEL_ORDER: LessonPointsLevel[] = ['3pt', '4pt', '5pt', 'hs_physics', 'calc1', 'la'];
function levelIndex(l: LessonPointsLevel) {
  return LEVEL_ORDER.indexOf(l);
}

type Lang = 'en' | 'he';

const DIFFICULTY_TINT: Record<LessonQuestionRow['difficulty'], string> = {
  easy: 'bg-emerald-500/10 text-emerald-400',
  medium: 'bg-accent-amber/10 text-accent-amber',
  hard: 'bg-destructive/10 text-destructive',
};

/** Label shown to the student, calibrated relative to their level. */
function difficultyLabel(
  raw: LessonQuestionRow['difficulty'],
  learnerLevel: LessonPointsLevel | null,
  lang: Lang,
): string {
  const isHe = lang === 'he';
  // For lower-level students, what they find "hard" is a different concept.
  // We relabel so the student understands the effort relative to their course.
  if (!learnerLevel || learnerLevel === '3pt') {
    const labels: Record<string, { en: string; he: string }> = {
      easy: { en: 'practice', he: 'תרגול' },
      medium: { en: 'standard', he: 'רגיל' },
      hard: { en: 'challenging', he: 'מאתגר' },
    };
    return isHe ? (labels[raw]?.he ?? raw) : (labels[raw]?.en ?? raw);
  }
  if (learnerLevel === '4pt') {
    const labels: Record<string, { en: string; he: string }> = {
      easy: { en: 'warm-up', he: 'חימום' },
      medium: { en: 'standard', he: 'רגיל' },
      hard: { en: 'exam-level', he: 'רמת בגרות' },
    };
    return isHe ? (labels[raw]?.he ?? raw) : (labels[raw]?.en ?? raw);
  }
  // 5pt, hs_physics, calc1, la
  const labels: Record<string, { en: string; he: string }> = {
    easy: { en: 'standard', he: 'רגיל' },
    medium: { en: 'challenging', he: 'מאתגר' },
    hard: { en: 'hard / exam+', he: 'קשה / מעל בגרות' },
  };
  return isHe ? (labels[raw]?.he ?? raw) : (labels[raw]?.en ?? raw);
}

const KIND_LABEL: Record<LessonQuestionKind, { en: string; he: string }> = {
  mcq: { en: 'Multiple choice', he: 'בחירה מרובה' },
  mcq_multi: { en: 'Pick all that apply', he: 'סמנו את כל הנכונות' },
  true_false: { en: 'True / False', he: 'נכון / לא נכון' },
  open: { en: 'Open answer', he: 'תשובה פתוחה' },
  short_answer: { en: 'Short answer', he: 'תשובה קצרה' },
  fill_blank: { en: 'Fill in the blank', he: 'השלמת חסר' },
  numeric: { en: 'Numeric', he: 'מספרי' },
  match: { en: 'Match the pairs', he: 'התאימו זוגות' },
  ordering: { en: 'Order the steps', he: 'סדרו את השלבים' },
  derivation: { en: 'Derivation', he: 'גזירה' },
};

function MarkdownInline({ content }: { content: string }) {
  return <MarkdownMath>{content}</MarkdownMath>;
}

function normalizeAnswer(s: string, caseSensitive = false): string {
  const trimmed = s.trim().replace(/\s+/g, ' ');
  return caseSensitive ? trimmed : trimmed.toLowerCase();
}

function numericClose(a: string, b: string): boolean {
  const na = Number.parseFloat(a);
  const nb = Number.parseFloat(b);
  if (Number.isNaN(na) || Number.isNaN(nb)) return false;
  const tol = Math.max(1e-3, Math.abs(nb) * 0.01);
  return Math.abs(na - nb) <= tol;
}

function arraysEqual(a: number[], b: number[]): boolean {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i += 1) if (a[i] !== b[i]) return false;
  return true;
}

function setEqual(a: number[], b: number[]): boolean {
  if (a.length !== b.length) return false;
  const sa = [...a].sort((x, y) => x - y);
  const sb = [...b].sort((x, y) => x - y);
  return arraysEqual(sa, sb);
}

interface AnswerState {
  submitted: boolean;
  correct: boolean | null;
  userAnswer: unknown;
  selfAssessed: 'correct' | 'partial' | 'wrong' | null;
}

function QuestionCard({
  question,
  lang,
  lessonId,
  conceptId,
  onAnswered,
  learnerLevel,
}: {
  question: LessonQuestionRow;
  lang: Lang;
  lessonId: string;
  conceptId: string;
  onAnswered: (q: LessonQuestionRow, correct: boolean) => void;
  learnerLevel?: LessonPointsLevel | null;
}) {
  const [state, setState] = useState<AnswerState>({
    submitted: false,
    correct: null,
    userAnswer: null,
    selfAssessed: null,
  });
  const [revealed, setRevealed] = useState(false);
  const [openText, setOpenText] = useState('');
  const [multiSelected, setMultiSelected] = useState<Set<number>>(new Set());
  const [matchSelections, setMatchSelections] = useState<Record<number, number | null>>({});
  const [ordering, setOrdering] = useState<number[]>(() => {
    const payload = question.answer_payload;
    if (question.kind === 'ordering' && payload?.steps_en) {
      // Present the steps shuffled deterministically so the page is stable
      // across server/client renders (we identity-shuffle index list 0..n-1).
      const n = payload.steps_en.length;
      const shuffled: number[] = [];
      for (let i = 0; i < n; i += 2) shuffled.push(i);
      for (let i = 1; i < n; i += 2) shuffled.push(i);
      return shuffled.reverse();
    }
    return [];
  });
  const [busy, setBusy] = useState(false);

  const dir = lang === 'he' ? 'rtl' : 'ltr';
  const stem = lang === 'he' ? question.stem_he : question.stem_en;
  const explanation = lang === 'he' ? question.explanation_he : question.explanation_en;
  const rubric = lang === 'he' ? question.rubric_he : question.rubric_en;
  const options = lang === 'he' ? question.options_he : question.options_en;
  const kindLabel = KIND_LABEL[question.kind][lang];
  const payload = question.answer_payload;

  async function reportAnswer(correct: boolean, userAnswer: unknown) {
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
          user_answer: userAnswer,
        }),
      });
    } catch {
      // Network is best-effort; UI feedback already shown.
    } finally {
      setBusy(false);
    }
  }

  // -------- per-kind submit handlers ---------------------------------------
  function handleMcq(idx: number) {
    if (state.submitted) return;
    const correct = idx === question.correct_index;
    setState({ submitted: true, correct, userAnswer: idx, selfAssessed: null });
    void reportAnswer(correct, idx);
  }

  function handleMcqMultiSubmit() {
    if (state.submitted) return;
    const picked = [...multiSelected];
    const expected = payload?.correct_indices ?? [];
    const correct = setEqual(picked, expected);
    setState({ submitted: true, correct, userAnswer: picked, selfAssessed: null });
    void reportAnswer(correct, picked);
  }

  function handleTrueFalse(value: boolean) {
    if (state.submitted) return;
    const correct = value === (payload?.correct_bool ?? false);
    setState({ submitted: true, correct, userAnswer: value, selfAssessed: null });
    void reportAnswer(correct, value);
  }

  function handleNumericOrFill() {
    if (state.submitted) return;
    const expected = question.correct_answer ?? '';
    const correct =
      question.kind === 'numeric'
        ? numericClose(openText, expected)
        : normalizeAnswer(openText) === normalizeAnswer(expected);
    setState({ submitted: true, correct, userAnswer: openText, selfAssessed: null });
    void reportAnswer(correct, openText);
  }

  function handleShortAnswer() {
    if (state.submitted) return;
    const cs = payload?.case_sensitive ?? false;
    const user = normalizeAnswer(openText, cs);
    const accepted = (payload?.acceptable_answers ?? []).map((a) => normalizeAnswer(a, cs));
    const correct = accepted.includes(user);
    setState({ submitted: true, correct, userAnswer: openText, selfAssessed: null });
    void reportAnswer(correct, openText);
  }

  function handleMatchSubmit() {
    if (state.submitted) return;
    const expected = payload?.correct_pairs ?? [];
    const n = expected.length;
    const userPairs: number[] = [];
    let anyMissing = false;
    for (let i = 0; i < n; i += 1) {
      const v = matchSelections[i];
      if (v == null) anyMissing = true;
      userPairs.push(v ?? -1);
    }
    const correct = !anyMissing && arraysEqual(userPairs, expected);
    setState({ submitted: true, correct, userAnswer: userPairs, selfAssessed: null });
    void reportAnswer(correct, userPairs);
  }

  function handleOrderingSubmit() {
    if (state.submitted) return;
    const expected = payload?.correct_order ?? [];
    const correct = arraysEqual(ordering, expected);
    setState({ submitted: true, correct, userAnswer: [...ordering], selfAssessed: null });
    void reportAnswer(correct, [...ordering]);
  }

  function moveOrderingItem(idx: number, delta: -1 | 1) {
    setOrdering((prev) => {
      const next = [...prev];
      const target = idx + delta;
      if (target < 0 || target >= next.length) return prev;
      const a = next[idx];
      const b = next[target];
      if (a === undefined || b === undefined) return prev;
      next[idx] = b;
      next[target] = a;
      return next;
    });
  }

  function handleSelfAssess(grade: 'correct' | 'partial' | 'wrong') {
    if (state.submitted) return;
    const correct = grade !== 'wrong';
    setState({ submitted: true, correct, userAnswer: openText, selfAssessed: grade });
    void reportAnswer(correct, openText);
  }

  return (
    <div className="glass-surface rounded-2xl border-border/60 p-5" dir={dir}>
      <div className="mb-3 flex flex-wrap items-center gap-2 text-[10px] font-semibold uppercase">
        <span className="rounded-full bg-muted px-2 py-0.5 text-muted-foreground">
          #{question.ord}
        </span>
        {question.kind === 'open' || question.kind === 'derivation' ? (
          <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 text-amber-800 dark:text-amber-300">
            <Pencil className="h-3 w-3" aria-hidden />
            {kindLabel}
          </span>
        ) : (
          <span className="rounded-full bg-muted px-2 py-0.5 text-muted-foreground">
            {kindLabel}
          </span>
        )}
        <span
          className={`rounded-full px-2 py-0.5 ${DIFFICULTY_TINT[question.difficulty]}`}
        >
          {difficultyLabel(question.difficulty, learnerLevel ?? null, lang)}
        </span>
      </div>

      <div className="mb-4 text-base font-medium text-foreground">
        <MarkdownInline content={stem} />
      </div>

      {/* mcq (single-correct) */}
      {question.kind === 'mcq' && options ? (
        <div className="space-y-2">
          {options.map((opt, i) => {
            const isUser = state.userAnswer === i;
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
                <span className="shrink-0 font-mono text-xs text-muted-foreground" dir="ltr">
                  {`${String.fromCharCode(65 + i)}. `}
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

      {/* mcq_multi — pick all that apply */}
      {question.kind === 'mcq_multi' && options ? (
        <div className="space-y-2">
          {options.map((opt, i) => {
            const isUser = multiSelected.has(i);
            const isCorrect = (payload?.correct_indices ?? []).includes(i);
            let cls = 'border-border bg-surface-1/50 hover:border-primary/40';
            if (state.submitted) {
              if (isCorrect && isUser) cls = 'border-emerald-500/60 bg-emerald-500/10';
              else if (isCorrect && !isUser) cls = 'border-emerald-500/40 bg-emerald-500/5';
              else if (!isCorrect && isUser) cls = 'border-destructive/60 bg-destructive/10';
              else cls = 'border-border/30 bg-surface-1/30 opacity-60';
            } else if (isUser) {
              cls = 'border-primary/60 bg-primary/10';
            }
            return (
              <button
                key={i}
                type="button"
                disabled={state.submitted || busy}
                onClick={() => {
                  setMultiSelected((prev) => {
                    const next = new Set(prev);
                    if (next.has(i)) next.delete(i);
                    else next.add(i);
                    return next;
                  });
                }}
                className={`flex w-full items-start gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-colors ${cls}`}
              >
                <span
                  className={`mt-0.5 inline-flex h-4 w-4 items-center justify-center rounded border ${
                    isUser ? 'border-primary bg-primary text-primary-foreground' : 'border-border'
                  }`}
                  aria-hidden
                >
                  {isUser ? <Check className="h-3 w-3" /> : null}
                </span>
                <span className="flex-1">
                  <MarkdownInline content={opt} />
                </span>
              </button>
            );
          })}
          {!state.submitted ? (
            <button
              type="button"
              onClick={handleMcqMultiSubmit}
              disabled={multiSelected.size === 0 || busy}
              className="mt-2 rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
            >
              {lang === 'he' ? 'בדקו' : 'Check'}
            </button>
          ) : null}
        </div>
      ) : null}

      {/* true_false */}
      {question.kind === 'true_false' ? (
        <div className="flex gap-3">
          {(
            [
              { v: true, en: 'True', he: 'נכון' },
              { v: false, en: 'False', he: 'לא נכון' },
            ] as const
          ).map((opt) => {
            const isUser = state.userAnswer === opt.v;
            const isCorrect = opt.v === (payload?.correct_bool ?? false);
            let cls = 'border-border bg-surface-1/50 hover:border-primary/40';
            if (state.submitted) {
              if (isCorrect) cls = 'border-emerald-500/60 bg-emerald-500/10';
              else if (isUser) cls = 'border-destructive/60 bg-destructive/10';
              else cls = 'border-border/30 bg-surface-1/30 opacity-60';
            }
            return (
              <button
                key={opt.en}
                type="button"
                disabled={state.submitted || busy}
                onClick={() => handleTrueFalse(opt.v)}
                className={`flex flex-1 items-center justify-center gap-2 rounded-lg border px-4 py-3 text-sm font-semibold transition-colors ${cls}`}
              >
                {opt.v ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                {lang === 'he' ? opt.he : opt.en}
              </button>
            );
          })}
        </div>
      ) : null}

      {/* numeric / fill_blank */}
      {(question.kind === 'numeric' || question.kind === 'fill_blank') && !state.submitted ? (
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            type="text"
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

      {/* short_answer — text input, normalized matched against acceptable_answers */}
      {question.kind === 'short_answer' && !state.submitted ? (
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            type="text"
            value={openText}
            onChange={(e) => setOpenText(e.target.value)}
            placeholder={lang === 'he' ? 'תשובה קצרה' : 'Short answer'}
            className="flex-1 rounded-lg border border-border bg-surface-1/50 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            dir={dir}
          />
          <button
            type="button"
            onClick={handleShortAnswer}
            disabled={!openText.trim() || busy}
            className="rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
          >
            {lang === 'he' ? 'בדקו' : 'Check'}
          </button>
        </div>
      ) : null}

      {/* match — left list with a dropdown picking the corresponding right item */}
      {question.kind === 'match' && payload?.left_en && payload?.right_en ? (
        <div className="space-y-2">
          {(lang === 'he' ? payload.left_he ?? payload.left_en : payload.left_en).map((left, i) => {
            const rightOptions = lang === 'he' ? payload.right_he ?? payload.right_en! : payload.right_en!;
            const userChoice = matchSelections[i] ?? null;
            const correctIdx = (payload.correct_pairs ?? [])[i] ?? -1;
            const correctRight = correctIdx >= 0 ? rightOptions[correctIdx] ?? '' : '';
            let cls = 'border-border';
            if (state.submitted) {
              cls = userChoice === correctIdx ? 'border-emerald-500/60 bg-emerald-500/10' : 'border-destructive/60 bg-destructive/10';
            }
            return (
              <div key={i} className={`flex flex-col gap-2 rounded-lg border bg-surface-1/50 p-3 text-sm sm:flex-row sm:items-center ${cls}`}>
                <span className="flex-1 font-medium">
                  <MarkdownInline content={left} />
                </span>
                <span className="text-xs text-muted-foreground">→</span>
                <select
                  disabled={state.submitted || busy}
                  value={userChoice ?? ''}
                  onChange={(e) => {
                    const v = e.target.value === '' ? null : Number(e.target.value);
                    setMatchSelections((prev) => ({ ...prev, [i]: v }));
                  }}
                  className="rounded-md border border-border bg-surface-1 px-2 py-1.5 text-sm focus:border-primary focus:outline-none"
                >
                  <option value="">{lang === 'he' ? 'בחרו…' : 'Choose…'}</option>
                  {rightOptions.map((r, ri) => (
                    <option key={ri} value={ri}>
                      {r}
                    </option>
                  ))}
                </select>
                {state.submitted && userChoice !== correctIdx ? (
                  <span className="text-xs text-emerald-400">
                    {lang === 'he' ? 'נכון: ' : 'Correct: '}
                    {correctRight}
                  </span>
                ) : null}
              </div>
            );
          })}
          {!state.submitted ? (
            <button
              type="button"
              onClick={handleMatchSubmit}
              disabled={busy}
              className="mt-2 rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
            >
              {lang === 'he' ? 'בדקו' : 'Check'}
            </button>
          ) : null}
        </div>
      ) : null}

      {/* ordering — list with up/down chevrons to reorder */}
      {question.kind === 'ordering' && payload?.steps_en ? (
        <div className="space-y-2">
          {ordering.map((stepIdx, displayIdx) => {
            const steps = lang === 'he' ? payload.steps_he ?? payload.steps_en! : payload.steps_en!;
            const stepText = steps[stepIdx] ?? '';
            const correctPos = (payload.correct_order ?? []).indexOf(stepIdx);
            let cls = 'border-border';
            if (state.submitted) {
              cls = displayIdx === correctPos ? 'border-emerald-500/60 bg-emerald-500/10' : 'border-destructive/60 bg-destructive/10';
            }
            return (
              <div key={stepIdx} className={`flex items-center gap-2 rounded-lg border bg-surface-1/50 p-3 text-sm ${cls}`}>
                <span className="font-mono text-xs text-muted-foreground">{displayIdx + 1}.</span>
                <span className="flex-1">
                  <MarkdownInline content={stepText} />
                </span>
                {state.submitted ? (
                  displayIdx === correctPos ? (
                    <Check className="h-4 w-4 text-emerald-500" />
                  ) : (
                    <span className="text-xs text-muted-foreground">
                      {lang === 'he' ? `נכון: ${correctPos + 1}` : `should be #${correctPos + 1}`}
                    </span>
                  )
                ) : (
                  <span className="flex gap-1">
                    <button
                      type="button"
                      disabled={displayIdx === 0 || busy}
                      onClick={() => moveOrderingItem(displayIdx, -1)}
                      className="rounded-md border border-border bg-surface-1 px-1.5 py-1 hover:border-primary/40 disabled:opacity-30"
                      aria-label={lang === 'he' ? 'הזיזו למעלה' : 'Move up'}
                    >
                      <ChevronUp className="h-3.5 w-3.5" />
                    </button>
                    <button
                      type="button"
                      disabled={displayIdx === ordering.length - 1 || busy}
                      onClick={() => moveOrderingItem(displayIdx, 1)}
                      className="rounded-md border border-border bg-surface-1 px-1.5 py-1 hover:border-primary/40 disabled:opacity-30"
                      aria-label={lang === 'he' ? 'הזיזו למטה' : 'Move down'}
                    >
                      <ChevronDown className="h-3.5 w-3.5" />
                    </button>
                  </span>
                )}
              </div>
            );
          })}
          {!state.submitted ? (
            <button
              type="button"
              onClick={handleOrderingSubmit}
              disabled={busy}
              className="mt-2 rounded-lg bg-gradient-to-r from-primary to-accent-magenta px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
            >
              {lang === 'he' ? 'בדקו' : 'Check'}
            </button>
          ) : null}
        </div>
      ) : null}

      {/* open / derivation — written answer, self-assessed via rubric */}
      {(question.kind === 'open' || question.kind === 'derivation') && !state.submitted ? (
        <div className="space-y-3 rounded-xl border-2 border-amber-500/25 bg-amber-500/5 p-4">
          <textarea
            value={openText}
            onChange={(e) => setOpenText(e.target.value)}
            rows={6}
            placeholder={
              lang === 'he'
                ? question.kind === 'derivation'
                  ? 'כתבו את הגזירה צעד-אחר-צעד…'
                  : 'כתבו את הפתרון המלא שלכם כאן — הציגו כל שלב…'
                : question.kind === 'derivation'
                  ? 'Write the derivation step by step…'
                  : 'Write your full solution here — show all steps…'
            }
            className="w-full rounded-lg border border-amber-500/20 bg-background/80 px-3 py-2.5 text-sm leading-relaxed focus:border-amber-500/50 focus:outline-none"
            dir={dir}
          />
          <button
            type="button"
            onClick={() => setRevealed((v) => !v)}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background/60 px-3 py-2 text-xs font-semibold hover:border-amber-500/40"
          >
            {revealed ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
            {revealed
              ? lang === 'he'
                ? 'הסתירו פתרון'
                : 'Hide Solution'
              : lang === 'he'
                ? 'חשפו פתרון'
                : 'Reveal Solution'}
          </button>
          {revealed ? (
            <div className="space-y-4 rounded-lg border border-border/60 bg-background/50 p-4 text-sm">
              {(() => {
                const steps =
                  lang === 'he'
                    ? payload?.steps_he ?? payload?.steps_en
                    : payload?.steps_en;
                if (steps && steps.length > 0) {
                  return (
                    <div>
                      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                        {lang === 'he' ? 'שלבים צפויים' : 'Expected Steps'}
                      </p>
                      <ol className="list-decimal space-y-1 ps-5">
                        {steps.map((step, i) => (
                          <li key={i}>
                            <MarkdownInline content={step} />
                          </li>
                        ))}
                      </ol>
                    </div>
                  );
                }
                return null;
              })()}
              {explanation ? (
                <div>
                  <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                    {lang === 'he' ? 'פתרון לדוגמה' : 'Sample Solution'}
                  </p>
                  <MarkdownInline content={explanation} />
                </div>
              ) : null}
              {rubric ? (
                <div className="border-t border-border/40 pt-3">
                  <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                    {lang === 'he' ? 'מחוון ניקוד' : 'Grading Rubric'}
                  </p>
                  <MarkdownInline content={rubric} />
                </div>
              ) : null}
              <div className="flex flex-wrap items-center gap-2 border-t border-border/40 pt-3">
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
            {question.kind !== 'mcq' &&
            question.kind !== 'mcq_multi' &&
            question.kind !== 'true_false' &&
            question.kind !== 'match' &&
            question.kind !== 'ordering' &&
            question.correct_answer ? (
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
  learnerLevel,
}: {
  data: LessonWithQuestions;
  lang: Lang;
  conceptId: string;
  learnerLevel?: LessonPointsLevel | null;
}) {
  const { lesson, questions: allQuestions } = data;
  const [score, setScore] = useState({ answered: 0, correct: 0 });

  // Filter questions to those appropriate for the learner's level
  const questions = useMemo(() => {
    if (!learnerLevel) return allQuestions;
    const li = levelIndex(learnerLevel);
    return allQuestions.filter((q) => {
      if (!q.points_level_min) return true;
      return li >= levelIndex(q.points_level_min);
    });
  }, [allQuestions, learnerLevel]);

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
          learnerLevel={learnerLevel}
          onAnswered={(_, correct) =>
            setScore((s) => ({ answered: s.answered + 1, correct: s.correct + (correct ? 1 : 0) }))
          }
        />
      ))}

      {/* Skill-atom targeted drill section */}
      {lesson.skill_atom_bank && learnerLevel && Object.keys(lesson.skill_atom_bank).length > 0 ? (
        <SkillAtomDrillSection
          bank={lesson.skill_atom_bank}
          learnerLevel={learnerLevel}
          lang={lang}
          lessonId={lesson.id}
          conceptId={conceptId}
        />
      ) : null}

      {score.answered > 0 ? (
        <div className="mt-6 flex flex-wrap items-center gap-3 rounded-2xl border border-border/60 bg-surface-1/30 p-4">
          <p className="text-sm text-muted-foreground">
            {lang === 'he'
              ? `עניתם על ${score.answered} שאלות — ${score.correct} נכונות`
              : `You answered ${score.answered} questions — ${score.correct} correct`}
          </p>
          <Link
            href="/app?completed=1"
            className="inline-flex rounded-lg border border-border bg-surface-1/50 px-4 py-2 text-sm font-medium hover:border-primary/40"
          >
            {lang === 'he' ? 'חזרה ללוח הבקרה' : 'Back to Dashboard'}
          </Link>
        </div>
      ) : null}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Skill-atom targeted drill section
// ---------------------------------------------------------------------------
function SkillAtomDrillSection({
  bank,
  learnerLevel,
  lang,
  lessonId,
  conceptId,
}: {
  bank: NonNullable<import('@/lib/neon-db').LessonRow['skill_atom_bank']>;
  learnerLevel: LessonPointsLevel;
  lang: 'en' | 'he';
  lessonId: string;
  conceptId: string;
}) {
  const [selectedAtom, setSelectedAtom] = useState<string | null>(null);
  const [score, setScore] = useState({ answered: 0, correct: 0 });

  const atoms = Object.keys(bank);

  // Get questions for the selected atom at or below the learner's level
  const atomQuestions = useMemo<import('@/lib/neon-db').LessonQuestionRow[]>(() => {
    if (!selectedAtom) return [];
    const atomBank = bank[selectedAtom];
    if (!atomBank) return [];
    // Try exact level first, then cascade down
    const li = levelIndex(learnerLevel);
    for (let i = li; i >= 0; i--) {
      const lvl = LEVEL_ORDER[i];
      if (lvl && atomBank[lvl] && (atomBank[lvl]?.length ?? 0) > 0) {
        return atomBank[lvl] ?? [];
      }
    }
    return [];
  }, [bank, selectedAtom, learnerLevel]);

  if (atoms.length === 0) return null;

  const atomLabel = (atom: string) =>
    atom
      .split('_')
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');

  return (
    <div className="mt-6 space-y-4">
      <div className="flex items-center gap-2">
        <span className="h-5 w-5 text-accent-amber">⚡</span>
        <h3 className="font-display text-lg font-semibold">
          {lang === 'he' ? 'תרגול לפי מיומנות' : 'Practice by skill'}
        </h3>
      </div>
      <p className="text-sm text-muted-foreground">
        {lang === 'he'
          ? 'בחרו מיומנות ספציפית לתרגול ממוקד'
          : 'Choose a specific skill to practice in depth'}
      </p>

      <div className="flex flex-wrap gap-2">
        {atoms.map((atom) => (
          <button
            key={atom}
            type="button"
            onClick={() => {
              setSelectedAtom((a) => (a === atom ? null : atom));
              setScore({ answered: 0, correct: 0 });
            }}
            className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
              selectedAtom === atom
                ? 'border-primary bg-primary text-primary-foreground'
                : 'border-border bg-surface-1/50 text-muted-foreground hover:border-primary/40 hover:text-foreground'
            }`}
          >
            {atomLabel(atom)}
          </button>
        ))}
      </div>

      {selectedAtom && atomQuestions.length > 0 ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">
              {lang === 'he' ? `מיומנות: ${atomLabel(selectedAtom)}` : `Skill: ${atomLabel(selectedAtom)}`}
            </span>
            <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">
              {score.correct}/{score.answered}
            </span>
          </div>
          {atomQuestions.map((q) => (
            <QuestionCard
              key={q.id}
              question={q}
              lang={lang}
              lessonId={lessonId}
              conceptId={conceptId}
              learnerLevel={learnerLevel}
              onAnswered={(_, correct) =>
                setScore((s) => ({
                  answered: s.answered + 1,
                  correct: s.correct + (correct ? 1 : 0),
                }))
              }
            />
          ))}
        </div>
      ) : selectedAtom && atomQuestions.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {lang === 'he'
            ? 'שאלות לתרגול ייווצרו בקרוב עבור מיומנות זו'
            : 'Practice questions for this skill will be generated soon'}
        </p>
      ) : null}
    </div>
  );
}
