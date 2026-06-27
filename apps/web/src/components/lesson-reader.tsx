'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import katex from 'katex';
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
  Target,
  Info,
} from 'lucide-react';
import type { LessonSection, LessonWithQuestions, LessonPointsLevel } from '@/lib/neon-db';

/**
 * Renders a string that may contain inline LaTeX delimited by $...$.
 * Text outside dollar signs is rendered as plain text.
 * This is used for section titles and other short strings that aren't
 * full markdown but may contain inline math.
 */
function MathText({ text, dir }: { text: string; dir?: 'ltr' | 'rtl' }) {
  const parts = text.split(/(\$[^$\n]+\$)/g);
  return (
    <span dir={dir}>
      {parts.map((part, i) => {
        if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
          const math = part.slice(1, -1);
          try {
            const html = katex.renderToString(math, {
              throwOnError: false,
              output: 'html',
            });
            return (
              <span
                key={i}
                // eslint-disable-next-line react/no-danger
                dangerouslySetInnerHTML={{ __html: html }}
              />
            );
          } catch {
            return <span key={i}>{part}</span>;
          }
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}

type Lang = 'en' | 'he';

// Points levels in ascending order — used for "at least X" filtering
const LEVEL_ORDER: LessonPointsLevel[] = ['3pt', '4pt', '5pt', 'hs_physics', 'calc1', 'la'];

function levelIndex(l: LessonPointsLevel): number {
  return LEVEL_ORDER.indexOf(l);
}

function shouldShowSection(section: LessonSection, learnerLevel: LessonPointsLevel | null): boolean {
  if (!section.level_min) return true;
  if (!learnerLevel) return true;
  return levelIndex(learnerLevel) >= levelIndex(section.level_min);
}

function getBodyForLevel(
  section: LessonSection,
  lang: Lang,
  learnerLevel: LessonPointsLevel | null,
): string {
  if (learnerLevel && section.body_by_level) {
    // Try exact level first, then fall back to the closest lower level
    const idx = levelIndex(learnerLevel);
    for (let i = idx; i >= 0; i--) {
      const lvl = LEVEL_ORDER[i];
      if (lvl && section.body_by_level[lvl]) {
        const variant = section.body_by_level[lvl]!;
        return lang === 'he' ? variant.body_he_md : variant.body_en_md;
      }
    }
  }
  return lang === 'he' ? section.body_he_md : section.body_en_md;
}

const LEVEL_LABELS: Record<LessonPointsLevel, { en: string; he: string; color: string }> = {
  '3pt': { en: '3-Unit', he: '3 יח״ל', color: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30' },
  '4pt': { en: '4-Unit', he: '4 יח״ל', color: 'bg-blue-500/15 text-blue-700 dark:text-blue-400 border-blue-500/30' },
  '5pt': { en: '5-Unit', he: '5 יח״ל', color: 'bg-violet-500/15 text-violet-700 dark:text-violet-400 border-violet-500/30' },
  'hs_physics': { en: 'HS Physics', he: 'פיזיקה תיכון', color: 'bg-orange-500/15 text-orange-700 dark:text-orange-400 border-orange-500/30' },
  'calc1': { en: 'Calc I', he: 'חשבון דיפרנציאלי', color: 'bg-pink-500/15 text-pink-700 dark:text-pink-400 border-pink-500/30' },
  'la': { en: 'Linear Algebra', he: 'אלגברה לינארית', color: 'bg-cyan-500/15 text-cyan-700 dark:text-cyan-400 border-cyan-500/30' },
};

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
  learnerLevel,
}: {
  section: LessonSection;
  lang: Lang;
  defaultOpen: boolean;
  learnerLevel: LessonPointsLevel | null;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const meta = SECTION_META[section.kind];
  const Icon = meta.icon;
  const title = lang === 'he' ? section.title_he : section.title_en;
  const label = lang === 'he' ? meta.label_he : meta.label_en;
  const body = getBodyForLevel(section, lang, learnerLevel);
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
            <span className="block text-base font-semibold text-foreground">
              <MathText text={title} dir={dir} />
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
  learnerLevel,
}: {
  data: LessonWithQuestions;
  lang: Lang;
  learnerLevel?: LessonPointsLevel | null;
}) {
  const { lesson } = data;
  const summary = lang === 'he' ? lesson.summary_he : lesson.summary_en;
  const dir = lang === 'he' ? 'rtl' : 'ltr';
  const level = learnerLevel ?? null;

  // Level focus block for this student
  const levelFocus = level && lesson.level_focus?.[level];

  // Filter sections to what's appropriate for this learner's level
  const visibleSections = lesson.sections.filter((s) => shouldShowSection(s, level));

  return (
    <div className="space-y-4">
      {/* Lesson meta card */}
      <div className="glass-surface rounded-2xl border-border/60 p-5" dir={dir}>
        <p className="text-sm leading-relaxed text-foreground/80">
          <MathText text={summary} dir={dir} />
        </p>
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
          {level && LEVEL_LABELS[level] ? (
            <span
              className={`rounded-full border px-2 py-0.5 font-semibold ${LEVEL_LABELS[level].color}`}
            >
              {lang === 'he' ? LEVEL_LABELS[level].he : LEVEL_LABELS[level].en}
            </span>
          ) : null}
          <span className="rounded-full bg-muted px-2 py-0.5 font-medium uppercase text-muted-foreground">
            v{lesson.version}
          </span>
        </div>
      </div>

      {/* Level focus callout — tells the student exactly what they need to master */}
      {levelFocus ? (
        <div
          className="flex gap-3 rounded-2xl border border-primary/30 bg-primary/5 px-5 py-4"
          dir={dir}
        >
          <Target className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-primary">
              {lang === 'he' ? 'מה נדרש ממך ברמה זו' : 'What you need to master at your level'}
            </p>
            <p className="mt-1 text-sm leading-relaxed text-foreground/80">
              {lang === 'he' ? levelFocus.he : levelFocus.en}
            </p>
            {levelFocus.not_required ? (
              <p className="mt-2 text-[11px] text-muted-foreground">
                <Info className="mr-1 inline h-3 w-3" />
                {lang === 'he'
                  ? `לא נדרש ברמה זו: ${levelFocus.not_required.join(', ')}`
                  : `Not required at your level: ${levelFocus.not_required.join(', ')}`}
              </p>
            ) : null}
          </div>
        </div>
      ) : null}

      {/* Sections filtered + rendered at the right depth */}
      {visibleSections.map((section, i) => (
        <SectionCard
          key={`${section.kind}-${i}`}
          section={section}
          lang={lang}
          defaultOpen={i < 2}
          learnerLevel={level}
        />
      ))}
    </div>
  );
}
