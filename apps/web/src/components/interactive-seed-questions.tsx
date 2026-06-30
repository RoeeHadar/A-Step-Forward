'use client';

import { useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { OpenWrittenQuestion } from '@/components/open-written-question';

export type InteractiveSeedMcqOption = {
  id: string;
  text_en: string;
  text_he: string;
  correct?: boolean;
};

export type InteractiveSeedQuestion =
  | {
      id: string;
      type: 'mcq';
      body_en: string;
      body_he: string;
      options: InteractiveSeedMcqOption[];
    }
  | {
      id: string;
      type: 'open';
      body_en: string;
      body_he: string;
      points?: number;
      expected_steps_en?: string[];
      expected_steps_he?: string[];
      sample_solution_en?: string;
      sample_solution_he?: string;
      rubric_en?: string;
      rubric_he?: string;
    };

type Lang = 'en' | 'he';

function MarkdownInline({ content, dir }: { content: string; dir: 'ltr' | 'rtl' }) {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none" dir={dir}>
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}

function McqQuestion({
  question,
  lang,
}: {
  question: Extract<InteractiveSeedQuestion, { type: 'mcq' }>;
  lang: Lang;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const dir = lang === 'he' ? 'rtl' : 'ltr';
  const body = lang === 'he' ? question.body_he : question.body_en;

  return (
    <div className="glass-surface rounded-2xl border-border/60 p-5" dir={dir}>
      <span className="mb-3 inline-block rounded-full bg-muted px-2 py-0.5 text-[10px] font-semibold uppercase text-muted-foreground">
        {lang === 'he' ? 'בחירה מרובה' : 'Multiple Choice'}
      </span>
      <div className="mb-4 text-base font-medium">
        <MarkdownInline content={body} dir={dir} />
      </div>
      <div className="space-y-2">
        {question.options.map((opt) => {
          const text = lang === 'he' ? opt.text_he : opt.text_en;
          const isSelected = selected === opt.id;
          const isCorrect = opt.correct === true;
          let cls = 'border-border bg-surface-1/50 hover:border-primary/40';
          if (submitted) {
            if (isCorrect) cls = 'border-emerald-500/60 bg-emerald-500/10';
            else if (isSelected) cls = 'border-destructive/60 bg-destructive/10';
            else cls = 'border-border/30 opacity-60';
          } else if (isSelected) {
            cls = 'border-primary/50 bg-primary/5';
          }
          return (
            <button
              key={opt.id}
              type="button"
              disabled={submitted}
              onClick={() => {
                setSelected(opt.id);
                setSubmitted(true);
              }}
              className={`flex w-full items-start gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-colors ${cls}`}
            >
              <span className="shrink-0 font-mono text-xs uppercase text-muted-foreground" dir="ltr">
                {opt.id}.
              </span>
              <span className="flex-1">
                <MarkdownInline content={text} dir={dir} />
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function InteractiveSeedQuestions({
  questions,
  lang,
}: {
  questions: InteractiveSeedQuestion[];
  lang: Lang;
}) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const panels = useMemo(
    () =>
      questions.map((q, i) => {
        if (q.type === 'mcq') {
          return <McqQuestion key={q.id} question={q} lang={lang} />;
        }
        const body = lang === 'he' ? q.body_he : q.body_en;
        const expectedSteps =
          lang === 'he' ? q.expected_steps_he : q.expected_steps_en;
        const sampleSolution =
          lang === 'he' ? q.sample_solution_he : q.sample_solution_en;
        const rubric = lang === 'he' ? q.rubric_he : q.rubric_en;
        return (
          <OpenWrittenQuestion
            key={q.id}
            lang={lang}
            questionLabel={`${lang === 'he' ? 'שאלה' : 'Question'} ${i + 1}`}
            content={{
              body,
              points: q.points,
              expectedSteps,
              sampleSolution,
              rubric,
            }}
            answer={answers[q.id] ?? ''}
            onAnswerChange={(value) =>
              setAnswers((prev) => ({ ...prev, [q.id]: value }))
            }
          />
        );
      }),
    [answers, lang, questions],
  );

  if (questions.length === 0) return null;

  return (
    <section className="mt-8 space-y-4">
      <h2 className="font-display text-lg font-semibold">
        {lang === 'he' ? 'תרגול' : 'Practice'}
      </h2>
      {panels}
    </section>
  );
}
