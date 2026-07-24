'use client';

import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';

// ---------------------------------------------------------------------------
// Types (client-safe — no import from server-only modules)
// ---------------------------------------------------------------------------

type TrainingActionKind = 'drill' | 'review' | 'quiz_gate' | 'custom_quiz';

interface TrainingAction {
  kind: TrainingActionKind;
  label_he: string;
  label_en: string;
  href: string;
  reason_he: string;
  reason_en: string;
}

export interface ClientWeekTrainingSpec {
  week_id: string;
  plan_id: string;
  week_number: number;
  drills: Array<{ atom: string; mastery: number; concept_name: string; concept_name_he: string | null }>;
  due_reviews: { count: number };
  gate: { due_at: string | null; passed: boolean };
  recommended: TrainingAction[];
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const KIND_ICON: Record<TrainingActionKind, string> = {
  drill: '🎯',
  review: '🔁',
  quiz_gate: '🏆',
  custom_quiz: '🧩',
};

/** Tailwind classes for the icon badge per kind — use semantic color tokens, one accent each. */
const KIND_BADGE: Record<TrainingActionKind, string> = {
  drill: 'bg-primary/10 text-primary',
  review: 'bg-accent-cyan/15 text-accent-cyan',
  quiz_gate: 'bg-accent-amber/15 text-accent-amber',
  custom_quiz: 'bg-accent-magenta/15 text-accent-magenta',
};

const STR = {
  he: {
    sectionTitle: 'אימון לשבוע הזה',
    week: (n: number) => `שבוע ${n}`,
  },
  en: {
    sectionTitle: "This week's training",
    week: (n: number) => `Week ${n}`,
  },
} as const;

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ActionRow({
  action,
  isHe,
}: {
  action: TrainingAction;
  isHe: boolean;
}) {
  const label = isHe ? action.label_he : action.label_en;
  const reason = isHe ? action.reason_he : action.reason_en;
  const icon = KIND_ICON[action.kind];
  const badge = KIND_BADGE[action.kind];

  return (
    <Link
      href={action.href}
      className={cn(
        'group flex items-start gap-3 rounded-xl p-3 transition-all duration-150',
        'hover:bg-muted/60 hover:scale-[1.005]',
      )}
    >
      {/* Icon badge */}
      <span
        className={cn(
          'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-base',
          badge,
        )}
        aria-hidden
      >
        {icon}
      </span>

      {/* Text */}
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium leading-snug text-foreground" dir="auto">
          {label}
        </p>
        <p className="mt-0.5 truncate text-xs leading-relaxed text-muted-foreground" dir="auto">
          {reason}
        </p>
      </div>

      {/* Trailing chevron — flipped in RTL via rotate */}
      <ChevronRight
        className={cn(
          'mt-1 h-4 w-4 shrink-0 text-muted-foreground/60 transition-transform duration-150',
          'group-hover:translate-x-0.5',
          isHe && 'rotate-180 group-hover:-translate-x-0.5 group-hover:translate-x-0',
        )}
        aria-hidden
      />
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Main card
// ---------------------------------------------------------------------------

/**
 * Compact bilingual "This week's training" card.
 * Renders 1–4 recommended training actions derived from the active plan week.
 * RTL-aware, design-token compliant, taste-reviewed.
 */
export function WeekTrainingCard({
  spec,
}: {
  spec: ClientWeekTrainingSpec;
}) {
  const { locale } = useI18n();
  const isHe = locale === 'he';
  const t = STR[isHe ? 'he' : 'en'];

  if (!spec.recommended.length) return null;

  return (
    <section
      dir={isHe ? 'rtl' : 'ltr'}
      className="rounded-2xl border border-border bg-card p-5 shadow-sm md:p-6"
    >
      {/* Section heading — matches SectionHeading in dashboard-content */}
      <h2 className="font-display mb-4 flex items-center gap-2.5 text-xl font-semibold text-foreground">
        <span className="h-5 w-1 rounded-full bg-primary" aria-hidden />
        {t.sectionTitle}
        <span className="ms-auto text-xs font-normal text-muted-foreground">
          {t.week(spec.week_number)}
        </span>
      </h2>

      {/* Action rows */}
      <div className="divide-y divide-border/40">
        {spec.recommended.map((action, idx) => (
          <ActionRow key={`${action.kind}-${idx}`} action={action} isHe={isHe} />
        ))}
      </div>
    </section>
  );
}
