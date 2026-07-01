'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { MarkdownMath } from '@/components/markdown-math';
import { Clock, CheckCircle2, ArrowLeft } from 'lucide-react';
import { OpenWrittenQuestion } from '@/components/open-written-question';
import type { SeedMockExam, MockExamIndexEntry } from '@/lib/mock-exam-seed-types';

type Lang = 'he' | 'en';

function formatTime(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return `${m}:${String(s).padStart(2, '0')}`;
}

function ExamMarkdown({ content, dir }: { content: string; dir: 'ltr' | 'rtl' }) {
  return <MarkdownMath dir={dir}>{content}</MarkdownMath>;
}

function MockExamRunner({
  exam,
  lang,
  onBack,
}: {
  exam: SeedMockExam;
  lang: Lang;
  onBack: () => void;
}) {
  const isHe = lang === 'he';
  const dir = isHe ? 'rtl' : 'ltr';
  const totalSeconds = exam.duration_min * 60;

  const [secondsLeft, setSecondsLeft] = useState(totalSeconds);
  const [started, setStarted] = useState(false);
  const [finished, setFinished] = useState(false);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [selectedBySection, setSelectedBySection] = useState<Record<string, Set<string>>>({});
  const [revealedSections, setRevealedSections] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!started || finished) return;
    const id = window.setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          setFinished(true);
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => window.clearInterval(id);
  }, [started, finished]);

  const title = isHe ? exam.title_he : exam.title_en;
  const instructions = isHe ? exam.instructions_he : exam.instructions_en;

  function toggleQuestion(sectionId: string, questionId: string, choose: number) {
    setSelectedBySection((prev) => {
      const current = new Set(prev[sectionId] ?? []);
      if (current.has(questionId)) current.delete(questionId);
      else if (current.size < choose) current.add(questionId);
      return { ...prev, [sectionId]: current };
    });
  }

  if (!started) {
    return (
      <div className="mx-auto max-w-2xl" dir={dir}>
        <button
          type="button"
          onClick={onBack}
          className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          {isHe ? 'חזרה לרשימה' : 'Back to list'}
        </button>
        <article className="rounded-2xl border-2 border-border bg-card p-8 shadow-sm">
          <header className="border-b border-border pb-6 text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              {isHe ? 'מבחן מדומה' : 'Mock Exam'}
            </p>
            <h1 className="mt-2 font-display text-2xl font-bold">{title}</h1>
            <p className="mt-2 flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              {exam.duration_min} {isHe ? 'דקות' : 'minutes'}
            </p>
          </header>
          <div className="mt-6 text-sm leading-relaxed text-foreground/90">
            <ExamMarkdown content={instructions} dir={dir} />
          </div>
          <ul className="mt-6 space-y-2 text-sm text-muted-foreground">
            {exam.sections.map((sec) => (
              <li
                key={sec.id}
                className="flex justify-between gap-4 border-b border-dashed border-border/60 pb-2"
              >
                <span>{isHe ? sec.title_he : sec.title_en}</span>
                <span className="shrink-0 font-mono text-xs">{sec.points} pts</span>
              </li>
            ))}
          </ul>
          <button
            type="button"
            onClick={() => setStarted(true)}
            className="mt-8 w-full rounded-xl bg-primary py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90"
          >
            {isHe ? 'התחל מבחן' : 'Start Exam'}
          </button>
        </article>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl pb-16" dir={dir}>
      <div className="sticky top-0 z-10 mb-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-background/95 px-4 py-3 backdrop-blur">
        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">{title}</p>
          <p className="text-sm font-medium">
            {finished ? (isHe ? 'המבחן הסתיים' : 'Exam finished') : isHe ? 'זמן שנותר' : 'Time remaining'}
          </p>
        </div>
        <span
          className={`font-mono text-lg font-bold tabular-nums ${
            secondsLeft < 600 && !finished ? 'text-destructive' : 'text-foreground'
          }`}
        >
          {finished ? '0:00' : formatTime(secondsLeft)}
        </span>
        {!finished ? (
          <button
            type="button"
            onClick={() => setFinished(true)}
            className="rounded-lg border border-border px-3 py-1.5 text-xs font-semibold hover:border-primary/40"
          >
            {isHe ? 'סיים מבחן' : 'Finish Exam'}
          </button>
        ) : null}
      </div>

      <div className="mb-8 rounded-xl border border-border/60 bg-muted/30 px-5 py-4 text-sm">
        <ExamMarkdown content={instructions} dir={dir} />
      </div>

      {exam.sections.map((section, si) => {
        const secTitle = isHe ? section.title_he : section.title_en;
        const secInstr = isHe ? section.instructions_he : section.instructions_en;
        const selected = selectedBySection[section.id] ?? new Set<string>();
        const solutionsVisible = revealedSections.has(section.id) || finished;
        const canSelect = section.choose < section.questions.length;

        return (
          <section
            key={section.id}
            className="mb-10 rounded-2xl border-2 border-border bg-card p-6 shadow-sm"
          >
            <header className="mb-4 border-b border-border pb-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {isHe ? `פרק ${si + 1}` : `Section ${si + 1}`} · {section.points}{' '}
                {isHe ? 'נקודות' : 'points'}
              </p>
              <h2 className="mt-1 font-display text-xl font-bold">{secTitle}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{secInstr}</p>
            </header>

            <div className="space-y-6">
              {section.questions.map((q, qi) => {
                const isChosen = !canSelect || selected.has(q.id);
                return (
                  <div key={q.id} className="space-y-3">
                    {canSelect ? (
                      <label className="flex cursor-pointer items-center gap-2 text-sm font-medium">
                        <input
                          type="checkbox"
                          checked={selected.has(q.id)}
                          disabled={
                            finished || (!selected.has(q.id) && selected.size >= section.choose)
                          }
                          onChange={() => toggleQuestion(section.id, q.id, section.choose)}
                          className="h-4 w-4 rounded border-border"
                        />
                        <span>{isHe ? `בחר שאלה ${qi + 1}` : `Select question ${qi + 1}`}</span>
                      </label>
                    ) : null}

                    {isChosen ? (
                      <OpenWrittenQuestion
                        lang={lang}
                        allowReveal={false}
                        forceRevealed={solutionsVisible}
                        questionLabel={`${isHe ? 'שאלה' : 'Question'} ${qi + 1}`}
                        content={{
                          body: isHe ? q.body_he : q.body_en,
                          points: q.points,
                          expectedSteps: solutionsVisible
                            ? isHe
                              ? q.expected_steps_he
                              : q.expected_steps_en
                            : undefined,
                          sampleSolution: solutionsVisible
                            ? isHe
                              ? q.sample_solution_he
                              : q.sample_solution_en
                            : undefined,
                          rubric: solutionsVisible
                            ? isHe
                              ? q.rubric_he
                              : q.rubric_en
                            : undefined,
                        }}
                        answer={answers[q.id] ?? ''}
                        onAnswerChange={(v) => setAnswers((prev) => ({ ...prev, [q.id]: v }))}
                      />
                    ) : null}
                  </div>
                );
              })}
            </div>

            {!finished ? (
              <button
                type="button"
                onClick={() => setRevealedSections((prev) => new Set(prev).add(section.id))}
                className="mt-6 inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-xs font-semibold hover:border-primary/40"
              >
                <CheckCircle2 className="h-4 w-4" />
                {isHe ? 'סיימתי פרק — חשוף פתרונות' : 'Section done — reveal solutions'}
              </button>
            ) : null}
          </section>
        );
      })}

      {finished ? (
        <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/5 p-6 text-center">
          <p className="font-semibold text-emerald-700 dark:text-emerald-400">
            {isHe
              ? 'המבחן הוגש. השוו את הפתרונות שלכם למחוונים.'
              : 'Exam submitted. Compare your work to the rubrics.'}
          </p>
          <button type="button" onClick={onBack} className="mt-4 text-sm text-primary hover:underline">
            {isHe ? 'בחר מבחן אחר' : 'Choose another exam'}
          </button>
        </div>
      ) : null}
    </div>
  );
}

export function MockExamClient({
  exams,
  getExam,
  initialExamId,
}: {
  exams: MockExamIndexEntry[];
  getExam: (id: string) => SeedMockExam | null;
  initialExamId?: string | null;
}) {
  const [lang, setLang] = useState<Lang>('he');
  const [activeId, setActiveId] = useState<string | null>(initialExamId ?? null);
  const isHe = lang === 'he';
  const activeExam = activeId ? getExam(activeId) : null;

  return (
    <div className="min-h-[60vh] p-4 md:p-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-full border border-border bg-surface-1/50 p-1">
          <button
            type="button"
            onClick={() => setLang('he')}
            className={`rounded-full px-4 py-1.5 text-xs font-semibold ${
              lang === 'he' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'
            }`}
          >
            עברית
          </button>
          <button
            type="button"
            onClick={() => setLang('en')}
            className={`rounded-full px-4 py-1.5 text-xs font-semibold ${
              lang === 'en' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'
            }`}
          >
            English
          </button>
        </div>
        <Link href="/app/quiz" className="text-sm text-muted-foreground hover:text-foreground">
          {isHe ? '← בוחן מותאם' : '← Custom Quiz'}
        </Link>
      </div>

      {activeExam ? (
        <MockExamRunner exam={activeExam} lang={lang} onBack={() => setActiveId(null)} />
      ) : (
        <div className="mx-auto max-w-2xl">
          <header className="mb-8 text-center">
            <h1 className="font-display text-2xl font-bold">
              {isHe ? 'מבחנים מדומים' : 'Mock Exams'}
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {isHe
                ? 'מבחני בגרות ואוניברסיטה — שאלות פתוחות בלבד, מבנה אמיתי'
                : 'Bagrut & university exams — open-ended only, real exam structure'}
            </p>
          </header>
          <ul className="space-y-3">
            {exams.map((e) => (
              <li key={e.id}>
                <button
                  type="button"
                  onClick={() => setActiveId(e.id)}
                  className="flex w-full items-center justify-between gap-4 rounded-xl border border-border bg-card px-5 py-4 text-left transition hover:border-primary/40 hover:shadow-sm"
                  dir={isHe ? 'rtl' : 'ltr'}
                >
                  <div>
                    <p className="font-semibold">{isHe ? e.title_he : e.title_en}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{e.subject}</p>
                  </div>
                  <span className="flex shrink-0 items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3.5 w-3.5" />
                    {e.duration_min} {isHe ? 'דק׳' : 'min'}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
