'use client';

import { useState } from 'react';
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
  BookMarked,
  PenLine,
  Map,
  GraduationCap,
  Dumbbell,
  Trophy,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { normalizeLatexInMarkdown } from '@/lib/normalize-latex';
import { MarkdownMath } from '@/components/markdown-math';
import type { LessonSection, LessonWithQuestions, LessonPointsLevel } from '@/lib/neon-db';
// MATH_GLOSSARY terms (see @/lib/math-glossary) could be wrapped with
// GlossaryTooltip for inline hover hints; full Markdown post-processing is
// intentionally avoided here due to complexity and rendering risk.

/**
 * Renders a string that may contain inline LaTeX delimited by $...$.
 * Text outside dollar signs is rendered as plain text.
 * This is used for section titles and other short strings that aren't
 * full markdown but may contain inline math.
 */
function MathText({ text, dir }: { text: string; dir?: 'ltr' | 'rtl' }) {
  const normalized = normalizeLatexInMarkdown(text);
  const parts = normalized.split(/(\$[^$\n]+\$)/g);
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

function levelVariantBody(
  variant: NonNullable<LessonSection['body_by_level']>[LessonPointsLevel],
  lang: Lang,
  fallback: string,
): string {
  if (!variant) return fallback;
  const text = lang === 'he' ? variant.body_he_md : variant.body_en_md;
  if (!text?.trim()) return fallback;
  // Guard against truncated Hebrew level variants (common seed-data issue)
  if (lang === 'he' && variant.body_en_md?.trim()) {
    const ratio = text.length / variant.body_en_md.length;
    if (ratio < 0.65) return fallback;
  }
  return text;
}

function getBodyForLevel(
  section: LessonSection,
  lang: Lang,
  learnerLevel: LessonPointsLevel | null,
): string {
  const fallback = lang === 'he' ? section.body_he_md : section.body_en_md;
  if (learnerLevel && section.body_by_level) {
    // Try exact level first, then fall back to the closest lower level
    const idx = levelIndex(learnerLevel);
    for (let i = idx; i >= 0; i--) {
      const lvl = LEVEL_ORDER[i];
      const variant = lvl ? section.body_by_level[lvl] : undefined;
      if (variant) {
        return levelVariantBody(variant, lang, fallback);
      }
    }
  }
  return fallback;
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
  definition: {
    label_en: 'Definition',
    label_he: 'הגדרה',
    icon: BookMarked,
    tint: 'border-blue-500/50 bg-blue-500/5',
  },
  checkpoint: {
    label_en: 'Stop & Practice',
    label_he: 'עצור ותרגל',
    icon: PenLine,
    tint: 'border-amber-500/50 bg-amber-500/5',
  },
  method_guide: {
    label_en: 'Method Guide',
    label_he: 'מדריך שיטות',
    icon: Map,
    tint: 'border-cyan-500/50 bg-cyan-500/5',
  },
  before_exam: {
    label_en: 'Before the Exam',
    label_he: 'לפני הבחינה',
    icon: GraduationCap,
    tint: 'border-violet-500/50 bg-violet-500/5',
  },
  exercise_set: {
    label_en: 'Practice Exercises',
    label_he: 'תרגילים',
    icon: Dumbbell,
    tint: 'border-green-500/50 bg-green-500/5',
  },
  exam_problems: {
    label_en: 'Exam-Level Problems',
    label_he: 'בעיות ברמת בחינה',
    icon: Trophy,
    tint: 'border-rose-500/50 bg-rose-500/5',
  },
};

// ── Difficulty badge helper ──────────────────────────────────────────────────

function DifficultyBadge({ difficulty, lang }: { difficulty: 'easy' | 'medium' | 'hard'; lang: Lang }) {
  return (
    <span
      className={cn(
        'rounded-full border px-2 py-0.5 text-[10px] font-bold',
        difficulty === 'easy' && 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
        difficulty === 'medium' && 'border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400',
        difficulty === 'hard' && 'border-rose-500/30 bg-rose-500/10 text-rose-600 dark:text-rose-400',
      )}
    >
      {difficulty === 'easy' ? '⭐' : difficulty === 'medium' ? '⭐⭐' : '⭐⭐⭐'}
      {' '}
      {lang === 'he'
        ? difficulty === 'easy' ? 'קל' : difficulty === 'medium' ? 'בינוני' : 'קשה'
        : difficulty === 'easy' ? 'Easy' : difficulty === 'medium' ? 'Medium' : 'Hard'}
    </span>
  );
}

// ── CheckpointCard ───────────────────────────────────────────────────────────

function CheckpointCard({
  section,
  lang,
  dir,
}: {
  section: LessonSection;
  lang: Lang;
  dir: 'rtl' | 'ltr';
}) {
  const [showSolution, setShowSolution] = useState(false);
  const body = lang === 'he' ? section.body_he_md : section.body_en_md;
  const solution = lang === 'he' ? section.checkpoint_solution_he : section.checkpoint_solution_en;

  return (
    <div className="rounded-2xl border-2 border-amber-500/40 bg-amber-500/5 overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-3 bg-amber-500/10">
        <PenLine className="h-4 w-4 text-amber-600 dark:text-amber-400" />
        <span className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
          {lang === 'he' ? '✋ עצור ותרגל' : '✋ Stop & Practice'}
        </span>
      </div>
      <div className="px-5 py-4" dir={dir}>
        <MarkdownMath>{body}</MarkdownMath>
        {solution ? (
          <div className="mt-4">
            <button
              type="button"
              onClick={() => setShowSolution((v) => !v)}
              className="inline-flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/5 px-3 py-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/10 transition-colors"
            >
              {showSolution
                ? lang === 'he' ? '▲ הסתר פתרון' : '▲ Hide solution'
                : lang === 'he' ? '▼ הצג פתרון' : '▼ Show solution'}
            </button>
            {showSolution ? (
              <div className="mt-3 rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4">
                <p className="mb-2 text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                  {lang === 'he' ? 'פתרון' : 'Solution'}
                </p>
                <MarkdownMath>{solution}</MarkdownMath>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}

// ── ExerciseItem ─────────────────────────────────────────────────────────────

function ExerciseItem({
  exercise,
  lang,
  dir,
}: {
  exercise: NonNullable<LessonSection['exercises']>[number];
  lang: Lang;
  dir: 'rtl' | 'ltr';
}) {
  const [showSolution, setShowSolution] = useState(false);
  const body = lang === 'he' ? exercise.body_he : exercise.body_en;
  const solution = lang === 'he' ? exercise.solution_he : exercise.solution_en;

  return (
    <div className="rounded-xl border border-border bg-background/60 p-4">
      <div className="mb-2 flex items-center gap-2">
        <DifficultyBadge difficulty={exercise.difficulty} lang={lang} />
        {exercise.points ? (
          <span className="text-[10px] text-muted-foreground">{exercise.points} pts</span>
        ) : null}
      </div>
      <MarkdownMath dir={dir}>{body}</MarkdownMath>
      {solution ? (
        <>
          <button
            type="button"
            onClick={() => setShowSolution((v) => !v)}
            className="mt-2 text-[11px] text-primary underline-offset-2 hover:underline"
          >
            {showSolution
              ? lang === 'he' ? 'הסתר פתרון' : 'Hide solution'
              : lang === 'he' ? 'הצג פתרון' : 'Show solution'}
          </button>
          {showSolution ? (
            <div className="mt-2 rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3">
              <MarkdownMath dir={dir}>{solution}</MarkdownMath>
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}

// ── ExerciseSetCard ──────────────────────────────────────────────────────────

function ExerciseSetCard({
  section,
  lang,
  dir,
}: {
  section: LessonSection;
  lang: Lang;
  dir: 'rtl' | 'ltr';
}) {
  return (
    <div className="rounded-2xl border-2 border-green-500/40 bg-green-500/5 overflow-hidden">
      <div className="px-5 py-3 bg-green-500/10 flex items-center gap-2">
        <Dumbbell className="h-4 w-4 text-green-600 dark:text-green-400" />
        <span className="text-xs font-bold uppercase tracking-wider text-green-600 dark:text-green-400">
          {lang === 'he' ? 'תרגילים' : 'Practice Exercises'}
        </span>
      </div>
      <div className="p-4 space-y-3">
        {section.exercises?.map((ex, i) => (
          <ExerciseItem key={ex.id || String(i)} exercise={ex} lang={lang} dir={dir} />
        ))}
        {!section.exercises ? (
          <MarkdownMath dir={dir}>{lang === 'he' ? section.body_he_md : section.body_en_md}</MarkdownMath>
        ) : null}
      </div>
    </div>
  );
}

// ── defaultOpen logic ────────────────────────────────────────────────────────

function getDefaultOpen(section: LessonSection, i: number): boolean {
  switch (section.kind) {
    case 'intro':
    case 'definition':
    case 'method_guide':
    case 'before_exam':
    case 'summary':
      return true;
    case 'worked_example':
      return section.difficulty !== 'hard';
    case 'theory':
      return i <= 2;
    case 'pitfall':
    case 'exercise_set':
      return false;
    default:
      return i < 2;
  }
}

// ── SectionCard ──────────────────────────────────────────────────────────────

function SectionCard({
  section,
  lang,
  defaultOpen,
  learnerLevel,
  sectionIndex,
  onFocus,
}: {
  section: LessonSection;
  lang: Lang;
  defaultOpen: boolean;
  learnerLevel: LessonPointsLevel | null;
  sectionIndex: number;
  onFocus?: (sectionNumber: number) => void;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const meta = SECTION_META[section.kind];
  const Icon = meta.icon;
  const title = lang === 'he' ? section.title_he : section.title_en;
  const label = lang === 'he' ? meta.label_he : meta.label_en;
  const body = getBodyForLevel(section, lang, learnerLevel);
  const dir = lang === 'he' ? 'rtl' : 'ltr';

  // Sections with dedicated card renderers bypass the accordion entirely
  if (section.kind === 'checkpoint') {
    return <CheckpointCard section={section} lang={lang} dir={dir} />;
  }
  if (section.kind === 'exercise_set') {
    return <ExerciseSetCard section={section} lang={lang} dir={dir} />;
  }

  // method_guide and before_exam: always open, no collapse button
  const alwaysOpen = section.kind === 'method_guide' || section.kind === 'before_exam';

  const headerContent = (
    <div className="flex items-center gap-3">
      <span className="grid h-9 w-9 place-items-center rounded-full bg-background/60">
        <Icon className="h-4 w-4 text-foreground" />
      </span>
      <div>
        <span className="block text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          {section.kind === 'worked_example' && section.example_number
            ? `${label} ${section.example_number}`
            : label}
        </span>
        <span className="block text-base font-semibold text-foreground">
          <MathText text={title} dir={dir} />
        </span>
      </div>
      {section.kind === 'worked_example' && section.difficulty ? (
        <DifficultyBadge difficulty={section.difficulty} lang={lang} />
      ) : null}
    </div>
  );

  const bodyContent = (
    <div
      className={cn(
        'border-t border-border/40 px-5 py-4',
        section.kind === 'worked_example'
          ? 'bg-gradient-to-br from-background/60 to-accent-magenta/5'
          : 'bg-background/40',
      )}
      dir={dir}
    >
      <MarkdownMath dir={dir}>{body}</MarkdownMath>
    </div>
  );

  if (alwaysOpen) {
    return (
      <div className={`glass-surface overflow-hidden rounded-2xl border-2 ${meta.tint} transition-all`}>
        <div className="flex items-center gap-3 px-5 py-4">
          {headerContent}
        </div>
        {bodyContent}
      </div>
    );
  }

  return (
    <div
      className={`glass-surface overflow-hidden rounded-2xl border-2 ${meta.tint} transition-all`}
    >
      <button
        type="button"
        onClick={() => {
          setOpen((v) => {
            const next = !v;
            if (next) onFocus?.(sectionIndex + 1);
            return next;
          });
        }}
        className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left"
        aria-expanded={open}
      >
        {headerContent}
        {open ? (
          <ChevronUp className="h-5 w-5 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-5 w-5 shrink-0 text-muted-foreground" />
        )}
      </button>

      {open ? bodyContent : null}
    </div>
  );
}

// ── LessonReader ─────────────────────────────────────────────────────────────

export function LessonReader({
  data,
  lang,
  learnerLevel,
  onSectionFocus,
}: {
  data: LessonWithQuestions;
  lang: Lang;
  learnerLevel?: LessonPointsLevel | null;
  onSectionFocus?: (sectionNumber: number) => void;
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

      {/* Compact table of contents for longer lessons */}
      {visibleSections.length > 3 ? (
        <div className="rounded-xl border border-border bg-muted/30 p-3" dir={dir}>
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            {lang === 'he' ? 'תוכן הלימוד' : 'In this lesson'}
          </p>
          <ol className="space-y-1">
            {visibleSections.map((s, i) => {
              const tocMeta = SECTION_META[s.kind];
              const TocIcon = tocMeta?.icon ?? BookOpen;
              const tocTitle = lang === 'he' ? s.title_he : s.title_en;
              return (
                <li key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                  <TocIcon className="h-3 w-3 shrink-0" />
                  <span className="truncate">{tocTitle}</span>
                </li>
              );
            })}
          </ol>
        </div>
      ) : null}

      {/* Sections filtered + rendered at the right depth */}
      {visibleSections.map((section, i) => (
        <SectionCard
          key={`${section.kind}-${i}`}
          section={section}
          lang={lang}
          defaultOpen={getDefaultOpen(section, i)}
          learnerLevel={level}
          sectionIndex={i}
          onFocus={onSectionFocus}
        />
      ))}
    </div>
  );
}
