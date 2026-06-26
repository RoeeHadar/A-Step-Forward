'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import {
  ChevronDown,
  ChevronUp,
  BookOpen,
  Lightbulb,
  AlertTriangle,
  Wrench,
  CheckCircle2,
  FileText,
} from 'lucide-react';
import type { LessonSection, LessonWithQuestions } from '@/lib/neon-db';

type Lang = 'en' | 'he';

const SECTION_META: Record<
  LessonSection['kind'],
  { label_en: string; label_he: string; icon: typeof BookOpen; tint: string }
> = {
  intro: {
    label_en: 'Introduction',
    label_he: 'מבוא',
    icon: BookOpen,
    tint: 'border-primary/40 bg-primary/5',
  },
  theory: {
    label_en: 'Theory',
    label_he: 'תיאוריה',
    icon: Lightbulb,
    tint: 'border-accent-amber/40 bg-accent-amber/5',
  },
  worked_example: {
    label_en: 'Worked Example',
    label_he: 'דוגמה פתורה',
    icon: Wrench,
    tint: 'border-accent-magenta/40 bg-accent-magenta/5',
  },
  pitfall: {
    label_en: 'Common Pitfalls',
    label_he: 'מלכודות נפוצות',
    icon: AlertTriangle,
    tint: 'border-destructive/40 bg-destructive/5',
  },
  practice_tip: {
    label_en: 'Practice Tip',
    label_he: 'טיפ לתרגול',
    icon: FileText,
    tint: 'border-muted-foreground/40 bg-muted/30',
  },
  summary: {
    label_en: 'Take-away',
    label_he: 'סיכום',
    icon: CheckCircle2,
    tint: 'border-emerald-500/40 bg-emerald-500/5',
  },
};

function SectionCard({
  section,
  lang,
  defaultOpen,
}: {
  section: LessonSection;
  lang: Lang;
  defaultOpen: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const meta = SECTION_META[section.kind];
  const Icon = meta.icon;
  const title = lang === 'he' ? section.title_he : section.title_en;
  const label = lang === 'he' ? meta.label_he : meta.label_en;
  const body = lang === 'he' ? section.body_he_md : section.body_en_md;
  const dir = lang === 'he' ? 'rtl' : 'ltr';

  return (
    <div
      className={`glass-surface overflow-hidden rounded-2xl border-2 ${meta.tint} transition-all`}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left"
        aria-expanded={open}
      >
        <div className="flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center rounded-full bg-background/60">
            <Icon className="h-4 w-4 text-foreground" />
          </span>
          <div>
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              {label}
            </span>
            <span className="block text-base font-semibold text-foreground" dir={dir}>
              {title}
            </span>
          </div>
        </div>
        {open ? (
          <ChevronUp className="h-5 w-5 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-5 w-5 text-muted-foreground" />
        )}
      </button>

      {open ? (
        <div
          className="border-t border-border/40 bg-background/40 px-5 py-4"
          dir={dir}
        >
          <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:font-display prose-pre:bg-muted/40">
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeKatex]}
            >
              {body}
            </ReactMarkdown>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export function LessonReader({
  data,
  lang,
}: {
  data: LessonWithQuestions;
  lang: Lang;
}) {
  const { lesson } = data;
  const summary = lang === 'he' ? lesson.summary_he : lesson.summary_en;
  const dir = lang === 'he' ? 'rtl' : 'ltr';

  return (
    <div className="space-y-4">
      <div
        className="glass-surface rounded-2xl border-border/60 p-5"
        dir={dir}
      >
        <p className="text-sm leading-relaxed text-foreground/80">{summary}</p>
        <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
          <span className="rounded-full bg-primary/10 px-2 py-0.5 font-medium uppercase text-primary">
            {lesson.est_minutes} min
          </span>
          {lesson.math_track.length > 0
            ? lesson.math_track.map((t) => (
                <span
                  key={t}
                  className="rounded-full bg-accent-amber/10 px-2 py-0.5 font-medium uppercase text-accent-amber"
                >
                  {t.toUpperCase()}
                </span>
              ))
            : null}
          <span className="rounded-full bg-muted px-2 py-0.5 font-medium uppercase text-muted-foreground">
            v{lesson.version}
          </span>
        </div>
      </div>

      {lesson.sections.map((section, i) => (
        <SectionCard
          key={`${section.kind}-${i}`}
          section={section}
          lang={lang}
          defaultOpen={i < 2}
        />
      ))}
    </div>
  );
}
