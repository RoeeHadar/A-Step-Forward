'use client';

import Link from 'next/link';
import { motion, useReducedMotion } from 'framer-motion';
import {
  ArrowRight,
  Brain,
  BookOpen,
  Github,
  Sparkles,
  UserPlus,
} from 'lucide-react';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';

type FeatureKey = keyof ReturnType<typeof useI18n>['messages']['landing']['features'];

const agentFeatures: Array<{
  emoji: string;
  titleKey: FeatureKey;
  descKey: FeatureKey;
  specialtyKey: FeatureKey;
  gradientClass: string;
  specialtyClass: string;
  chatPath: string;
}> = [
  {
    emoji: '📚',
    titleKey: 'tutor',
    descKey: 'tutorDesc',
    specialtyKey: 'tutorSpecialty',
    gradientClass: 'from-primary to-accent-magenta',
    specialtyClass: 'border-primary/30 bg-primary/10 text-primary',
    chatPath: '/app/chat/tutor',
  },
  {
    emoji: '🌟',
    titleKey: 'mentor',
    descKey: 'mentorDesc',
    specialtyKey: 'mentorSpecialty',
    gradientClass: 'from-accent-amber to-accent-magenta',
    specialtyClass: 'border-accent-amber/30 bg-accent-amber/10 text-accent-amber',
    chatPath: '/app/chat/mentor',
  },
  {
    emoji: '💪',
    titleKey: 'coach',
    descKey: 'coachDesc',
    specialtyKey: 'coachSpecialty',
    gradientClass: 'from-accent-cyan to-primary',
    specialtyClass: 'border-accent-cyan/30 bg-accent-cyan/10 text-accent-cyan',
    chatPath: '/app/chat/coach',
  },
  {
    emoji: '✍️',
    titleKey: 'reviewer',
    descKey: 'reviewerDesc',
    specialtyKey: 'reviewerSpecialty',
    gradientClass: 'from-accent-magenta to-accent-cyan',
    specialtyClass: 'border-accent-magenta/30 bg-accent-magenta/10 text-accent-magenta',
    chatPath: '/app/chat/reviewer',
  },
];

const agentAvatars = [
  { emoji: '📚', gradient: 'from-primary to-accent-magenta' },
  { emoji: '🌟', gradient: 'from-accent-amber to-accent-magenta' },
  { emoji: '💪', gradient: 'from-accent-cyan to-primary' },
  { emoji: '✍️', gradient: 'from-accent-magenta to-accent-cyan' },
];

const subjectEmojis = ['📐', '∫', '🧮', '⚛️'];

const trustChips = [
  { dotClass: 'bg-primary', key: 'trustOpenSource' as const },
  { dotClass: 'bg-accent-cyan', key: 'trustGroq' as const },
  { dotClass: 'bg-accent-magenta', key: 'trustFree' as const },
];

const howItWorksSteps = [
  {
    step: 1,
    titleKey: 'howItWorksStep1Title' as const,
    descKey: 'howItWorksStep1Desc' as const,
    icon: UserPlus,
    gradient: 'from-primary to-accent-magenta',
  },
  {
    step: 2,
    titleKey: 'howItWorksStep2Title' as const,
    descKey: 'howItWorksStep2Desc' as const,
    icon: BookOpen,
    gradient: 'from-accent-magenta to-accent-cyan',
  },
  {
    step: 3,
    titleKey: 'howItWorksStep3Title' as const,
    descKey: 'howItWorksStep3Desc' as const,
    icon: Sparkles,
    gradient: 'from-accent-cyan to-primary',
  },
];

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 ps-1 pt-1" aria-hidden>
      <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
      <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
      <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
    </div>
  );
}

export function LandingHero() {
  const { messages, locale } = useI18n();
  const t = messages.landing;
  const reduceMotion = useReducedMotion();

  const fadeUp = (delay = 0) =>
    reduceMotion
      ? {}
      : {
          initial: { opacity: 0, y: 20 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.5, delay, ease: [0.25, 0.1, 0.25, 1] },
        };

  const fadeUpInView = (delay = 0) =>
    reduceMotion
      ? {}
      : {
          initial: { opacity: 0, y: 24 },
          whileInView: { opacity: 1, y: 0 },
          viewport: { once: true, margin: '-60px' },
          transition: { duration: 0.5, delay, ease: [0.25, 0.1, 0.25, 1] },
        };

  const categoryPreview = CURRICULUM_CATEGORIES.slice(0, 6);

  return (
    <>
      {/* Section 1: Hero + Bento */}
      <section className="relative min-h-[85vh] overflow-hidden">
        {/* Floating colored orbs — one bright color each so the blur produces
            a vibrant glow instead of a washed-out three-color mush. */}
        <div
          className="orb-float orb-violet pointer-events-none absolute -start-32 -top-40 h-[420px] w-[420px] rounded-full sm:h-[560px] sm:w-[560px] lg:h-[680px] lg:w-[680px]"
          style={{ animationDelay: '0s' }}
          aria-hidden
        />
        <div
          className="orb-float orb-cyan pointer-events-none absolute -end-24 top-20 h-[340px] w-[340px] rounded-full sm:h-[460px] sm:w-[460px] lg:h-[560px] lg:w-[560px]"
          style={{ animationDelay: '-7s' }}
          aria-hidden
        />
        <div
          className="orb-float orb-magenta pointer-events-none absolute bottom-[-120px] start-1/2 h-[300px] w-[480px] -translate-x-1/2 rounded-full sm:h-[380px] sm:w-[620px] lg:h-[460px] lg:w-[820px]"
          style={{ animationDelay: '-14s' }}
          aria-hidden
        />
        <div
          className="orb-float orb-amber pointer-events-none absolute top-1/3 end-1/4 h-[220px] w-[220px] rounded-full sm:h-[300px] sm:w-[300px]"
          style={{ animationDelay: '-10s' }}
          aria-hidden
        />

        {/* Dot grid overlay */}
        <div
          className="bg-dot-grid pointer-events-none absolute inset-0 opacity-30 dark:opacity-50"
          aria-hidden
        />

        <div className="relative z-10 mx-auto max-w-7xl px-4 py-20 lg:py-28">
          {/* Hero text block */}
          <div className="max-w-4xl">
            <motion.div
              className="mb-6 inline-flex items-center gap-2 rounded-full glass-surface px-4 py-1.5 text-xs font-medium text-muted-foreground"
              {...fadeUp(0)}
            >
              <span className="h-2 w-2 animate-pulse rounded-full bg-primary" aria-hidden />
              {t.heroBadge}
            </motion.div>

            <motion.h1
              className="font-display text-5xl font-bold leading-[1.05] tracking-tight sm:text-7xl xl:text-8xl"
              {...fadeUp(0.08)}
            >
              <span className="text-foreground">{t.heroLine1}</span>
              <br />
              <span className="bg-gradient-to-r from-primary via-accent-magenta to-accent-cyan bg-clip-text text-transparent">
                {t.heroLine2}
              </span>
            </motion.h1>

            <motion.p
              className="mt-6 max-w-2xl text-lg text-muted-foreground lg:text-xl"
              {...fadeUp(0.16)}
            >
              {t.subtitle}
            </motion.p>

            <motion.div className="mt-8 flex flex-wrap items-center gap-3" {...fadeUp(0.24)}>
              <Link
                href="/sign-up"
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-base font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:shadow-primary/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                {t.cta}
                <ArrowRight className="h-4 w-4 rtl:rotate-180" aria-hidden />
              </Link>
              <Link
                href="/sign-in"
                className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface-1/50 px-6 py-3 text-base font-medium text-foreground backdrop-blur-sm transition-colors hover:border-border-bright"
              >
                {messages.nav.signIn}
              </Link>
            </motion.div>

            <motion.div className="mt-8 flex flex-wrap items-center gap-5" {...fadeUp(0.32)}>
              {trustChips.map(({ dotClass, key }) => (
                <div key={key} className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span className={cn('h-2 w-2 rounded-full', dotClass)} aria-hidden />
                  {t[key]}
                </div>
              ))}
            </motion.div>
          </div>

          {/* Bento grid */}
          <div className="mt-16 grid grid-cols-12 gap-4">
            {/* Tile A — Live Tutor Preview */}
            <motion.div
              className="iridescent-border col-span-12 flex min-h-[320px] flex-col p-5 lg:col-span-7 lg:row-span-2 lg:min-h-[420px] lg:p-6"
              {...fadeUpInView(0.1)}
            >
              <div className="mb-4 flex items-center justify-between gap-2">
                <span className="text-[10px] font-semibold tracking-widest text-muted-foreground">
                  {t.demoLabel}
                </span>
                <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-0.5 text-xs font-medium text-primary">
                  {t.features.tutor}
                </span>
              </div>

              <div className="flex flex-1 flex-col gap-3">
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-2xl rounded-ee-sm bg-primary px-4 py-3 text-sm text-primary-foreground">
                    {t.demoUserMsg}
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="max-w-[90%] rounded-2xl rounded-es-sm bg-surface-2 px-4 py-3 text-sm leading-relaxed text-foreground">
                    {t.demoTutorMsg}
                  </div>
                </div>
                <TypingIndicator />
              </div>
            </motion.div>

            {/* Tile B — 13 Subjects */}
            <motion.div
              className="glass-surface col-span-6 flex flex-col justify-between rounded-2xl p-5 lg:col-span-5 lg:row-span-1"
              {...fadeUpInView(0.15)}
            >
              <div>
                <span className="font-display text-6xl font-bold tabular-nums bg-gradient-to-br from-primary to-accent-magenta bg-clip-text text-transparent">
                  {t.statsCoursesValue}
                </span>
                <p className="mt-1 text-sm text-muted-foreground">{t.statsCoursesLabel}</p>
              </div>
              <div className="mt-4 flex gap-2">
                {subjectEmojis.map((emoji) => (
                  <span
                    key={emoji}
                    className="flex h-9 w-9 items-center justify-center rounded-full bg-surface-2 text-base"
                    aria-hidden
                  >
                    {emoji}
                  </span>
                ))}
              </div>
            </motion.div>

            {/* Tile C — 4 AI Agents */}
            <motion.div
              className="glass-surface col-span-6 flex flex-col justify-between rounded-2xl p-5 lg:col-span-3 lg:row-span-1"
              {...fadeUpInView(0.2)}
            >
              <div>
                <span className="font-display text-6xl font-bold tabular-nums bg-gradient-to-br from-accent-cyan to-primary bg-clip-text text-transparent">
                  {t.statsAgentsValue}
                </span>
                <p className="mt-1 text-sm text-muted-foreground">{t.statsAgentsLabel}</p>
              </div>
              <div className="mt-4 flex -space-x-2 rtl:space-x-reverse">
                {agentAvatars.map(({ emoji, gradient }, i) => (
                  <span
                    key={i}
                    className={cn(
                      'flex h-9 w-9 items-center justify-center rounded-full border-2 border-surface-1 bg-gradient-to-br text-sm',
                      gradient,
                    )}
                    aria-hidden
                  >
                    {emoji}
                  </span>
                ))}
              </div>
            </motion.div>

            {/* Tile D — Memory feature */}
            <motion.div
              className="glass-surface group col-span-12 flex flex-col gap-3 rounded-2xl p-5 transition-shadow hover:shadow-lg hover:shadow-primary/10 lg:col-span-2 lg:row-span-1"
              {...fadeUpInView(0.25)}
            >
              <Brain className="h-8 w-8 text-primary" aria-hidden />
              <h3 className="font-display text-lg font-semibold text-foreground">
                {t.features.memory}
              </h3>
              <p className="text-sm leading-relaxed text-muted-foreground">{t.features.memoryDesc}</p>
            </motion.div>

            {/* Tile E — Subject categories */}
            <motion.div
              className="glass-surface col-span-12 flex flex-col gap-4 rounded-2xl p-5 sm:flex-row sm:items-center sm:justify-between lg:col-span-7 lg:row-span-1"
              {...fadeUpInView(0.3)}
            >
              <div className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
                {categoryPreview.map((cat) => (
                  <span
                    key={cat.id}
                    className="inline-flex shrink-0 items-center gap-2 rounded-full glass-surface px-4 py-2 text-sm text-foreground transition-transform hover:scale-105"
                  >
                    <span aria-hidden>{cat.emoji}</span>
                    {locale === 'he' ? cat.heLabel : cat.enLabel}
                  </span>
                ))}
              </div>
              <Link
                href="/app/lessons"
                className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-primary transition-colors hover:text-primary/80"
              >
                {t.viewAll}
              </Link>
            </motion.div>

            {/* Tile F — Open source trust */}
            <motion.div
              className="iridescent-border col-span-6 flex flex-col gap-3 p-5 lg:col-span-5 lg:row-span-1"
              {...fadeUpInView(0.35)}
            >
              <span className="text-[10px] font-semibold tracking-widest text-muted-foreground">
                {t.openSourceLabel}
              </span>
              <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                <Github className="h-4 w-4" aria-hidden />
                {t.openSourceStack}
              </div>
              <p className="text-sm text-muted-foreground">{t.openSourceDesc}</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Section 3: Agent showcase */}
      <section className="border-y border-border bg-surface-1/50 py-20">
        <div className="mx-auto max-w-7xl px-4">
          <motion.h2
            className="font-display text-center text-4xl font-bold lg:text-5xl"
            {...fadeUpInView(0)}
          >
            {t.featuresHeading}
          </motion.h2>
          <motion.p
            className="mx-auto mt-4 max-w-2xl text-center text-muted-foreground"
            {...fadeUpInView(0.08)}
          >
            {t.featuresSubheading}
          </motion.p>

          <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {agentFeatures.map(
              ({ emoji, titleKey, descKey, specialtyKey, gradientClass, specialtyClass, chatPath }, i) => (
                <motion.article
                  key={titleKey}
                  className="iridescent-border flex flex-col p-6"
                  {...fadeUpInView(i * 0.08)}
                >
                  <div className="mb-4 flex items-start justify-between gap-2">
                    <span className="text-4xl leading-none" role="img" aria-hidden>
                      {emoji}
                    </span>
                    <span
                      className={cn(
                        'rounded-full border px-2.5 py-0.5 text-xs font-medium',
                        specialtyClass,
                      )}
                    >
                      {t.features[specialtyKey]}
                    </span>
                  </div>

                  <h3
                    className={cn(
                      'font-display mb-2 text-2xl font-bold bg-gradient-to-r bg-clip-text text-transparent',
                      gradientClass,
                    )}
                  >
                    {t.features[titleKey]}
                  </h3>

                  <p className="flex-1 text-sm leading-relaxed text-muted-foreground">
                    {t.features[descKey]}
                  </p>

                  <Link
                    href={chatPath}
                    className="mt-5 inline-flex items-center gap-1 text-sm font-medium text-primary transition-colors hover:text-primary/80"
                  >
                    {t.openChat}
                  </Link>
                </motion.article>
              ),
            )}
          </div>
        </div>
      </section>

      {/* Section 4: How it works */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4">
          <motion.h2
            className="font-display text-center text-4xl font-bold lg:text-5xl"
            {...fadeUpInView(0)}
          >
            {t.howItWorksHeading}
          </motion.h2>

          <div className="relative mt-16 grid gap-10 md:grid-cols-3 md:gap-8">
            <div
              className="pointer-events-none absolute top-8 hidden h-px w-full bg-gradient-to-r from-transparent via-border-bright to-transparent md:block"
              aria-hidden
            />

            {howItWorksSteps.map(({ step, titleKey, descKey, icon: Icon, gradient }, i) => (
              <motion.div
                key={step}
                className="relative flex flex-col items-center text-center"
                {...fadeUpInView(i * 0.1)}
              >
                <div
                  className={cn(
                    'relative z-10 mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br text-lg font-bold text-primary-foreground shadow-lg',
                    gradient,
                  )}
                >
                  {step}
                </div>
                <Icon className="mb-3 h-6 w-6 text-muted-foreground" aria-hidden />
                <h3 className="font-display mb-2 text-xl font-semibold">{t[titleKey]}</h3>
                <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">{t[descKey]}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Section 5: Final CTA */}
      <section className="relative overflow-hidden py-24 lg:py-32">
        <div className="mesh-gradient pointer-events-none absolute inset-0 opacity-60" aria-hidden />
        <div className="bg-dot-grid pointer-events-none absolute inset-0 opacity-20" aria-hidden />

        <div className="relative z-10 mx-auto max-w-4xl px-4 text-center">
          <motion.h2
            className="font-display text-4xl font-bold lg:text-6xl"
            {...fadeUpInView(0)}
          >
            {t.closingHeading}
          </motion.h2>
          <motion.p
            className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground"
            {...fadeUpInView(0.08)}
          >
            {t.closingSubtitle}
          </motion.p>
          <motion.div className="mt-10" {...fadeUpInView(0.16)}>
            <Link
              href="/sign-up"
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-8 py-4 text-base font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:shadow-primary/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {t.cta}
              <ArrowRight className="h-4 w-4 rtl:rotate-180" aria-hidden />
            </Link>
          </motion.div>
        </div>
      </section>
    </>
  );
}
