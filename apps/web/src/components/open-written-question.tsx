'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Eye, EyeOff, Pencil } from 'lucide-react';
import 'katex/dist/katex.min.css';

type Lang = 'en' | 'he';

function MarkdownBlock({ content, dir }: { content: string; dir: 'ltr' | 'rtl' }) {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none" dir={dir}>
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}

export type OpenWrittenQuestionContent = {
  body: string;
  points?: number;
  expectedSteps?: string[];
  sampleSolution?: string;
  rubric?: string;
};

export function OpenWrittenQuestion({
  content,
  lang,
  answer,
  onAnswerChange,
  questionLabel,
  revealLabel,
  hideLabel,
  writtenAnswerLabel,
  expectedStepsLabel,
  sampleSolutionLabel,
  rubricLabel,
  placeholder,
  className = '',
  allowReveal = true,
  forceRevealed = false,
}: {
  content: OpenWrittenQuestionContent;
  lang: Lang;
  answer: string;
  onAnswerChange: (value: string) => void;
  questionLabel?: string;
  revealLabel?: string;
  hideLabel?: string;
  writtenAnswerLabel?: string;
  expectedStepsLabel?: string;
  sampleSolutionLabel?: string;
  rubricLabel?: string;
  placeholder?: string;
  className?: string;
  /** When false, hides the per-question reveal control (parent controls timing). */
  allowReveal?: boolean;
  /** When true, shows solution block without user clicking reveal. */
  forceRevealed?: boolean;
}) {
  const [revealed, setRevealed] = useState(forceRevealed);
  const dir = lang === 'he' ? 'rtl' : 'ltr';
  const isHe = lang === 'he';

  useEffect(() => {
    if (forceRevealed) setRevealed(true);
  }, [forceRevealed]);

  return (
    <div
      className={`rounded-xl border-2 border-amber-500/30 bg-amber-500/5 p-5 ${className}`}
      dir={dir}
    >
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-800 dark:text-amber-300">
          <Pencil className="h-3.5 w-3.5" aria-hidden />
          {writtenAnswerLabel ?? (isHe ? 'תשובה בכתב' : 'Written Answer')}
        </span>
        {content.points != null ? (
          <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-semibold uppercase text-muted-foreground">
            {content.points} {isHe ? 'נק׳' : 'pts'}
          </span>
        ) : null}
        {questionLabel ? (
          <span className="text-[10px] font-semibold uppercase text-muted-foreground">
            {questionLabel}
          </span>
        ) : null}
      </div>

      <div className="mb-4 text-base font-medium text-foreground">
        <MarkdownBlock content={content.body} dir={dir} />
      </div>

      <textarea
        value={answer}
        onChange={(e) => onAnswerChange(e.target.value)}
        rows={6}
        placeholder={
          placeholder ??
          (isHe ? 'כתבו את הפתרון המלא שלכם כאן — הציגו כל שלב…' : 'Write your full solution here — show all steps…')
        }
        className="w-full rounded-lg border border-amber-500/20 bg-background/80 px-3 py-2.5 text-sm leading-relaxed focus:border-amber-500/50 focus:outline-none focus:ring-1 focus:ring-amber-500/30"
        dir={dir}
      />

      {allowReveal ? (
        <div className="mt-3">
          <button
            type="button"
            onClick={() => setRevealed((v) => !v)}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background/60 px-3 py-2 text-xs font-semibold transition hover:border-amber-500/40"
          >
            {revealed ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
            {revealed
              ? (hideLabel ?? (isHe ? 'הסתירו פתרון' : 'Hide Solution'))
              : (revealLabel ?? (isHe ? 'חשפו פתרון' : 'Reveal Solution'))}
          </button>
        </div>
      ) : null}

      {revealed && (allowReveal || forceRevealed) ? (
        <div className="mt-4 space-y-4 rounded-lg border border-border/60 bg-background/50 p-4 text-sm">
          {content.expectedSteps && content.expectedSteps.length > 0 ? (
            <div>
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                {expectedStepsLabel ?? (isHe ? 'שלבים צפויים' : 'Expected Steps')}
              </p>
              <ol className="list-decimal space-y-1 ps-5">
                {content.expectedSteps.map((step, i) => (
                  <li key={i} className="text-foreground/90">
                    <MarkdownBlock content={step} dir={dir} />
                  </li>
                ))}
              </ol>
            </div>
          ) : null}

          {content.sampleSolution ? (
            <div>
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                {sampleSolutionLabel ?? (isHe ? 'פתרון לדוגמה' : 'Sample Solution')}
              </p>
              <MarkdownBlock content={content.sampleSolution} dir={dir} />
            </div>
          ) : null}

          {content.rubric ? (
            <div className="border-t border-border/40 pt-3">
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                {rubricLabel ?? (isHe ? 'מחוון ניקוד' : 'Grading Rubric')}
              </p>
              <MarkdownBlock content={content.rubric} dir={dir} />
              <p className="mt-2 text-[11px] text-muted-foreground italic">
                {isHe
                  ? 'שאלה זו מדורגת עצמית — השוו את עבודתכם למחוון.'
                  : 'Self-assessed — compare your work against the rubric.'}
              </p>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
