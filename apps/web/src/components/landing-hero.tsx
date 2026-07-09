'use client';

import Link from 'next/link';
import { motion, useReducedMotion } from 'framer-motion';
import {
  ArrowRight,
  BookOpen,
  Brain,
  Compass,
  GraduationCap,
  Network,
  Route,
  Sprout,
  UserPlus,
  Users,
} from 'lucide-react';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';
import { AnimatedCounter } from '@/components/animated-counter';
import { Marquee } from '@/components/marquee';
import { GrowthPathMotif } from '@/components/growth-path-motif';
import { MemoryConstellation } from '@/components/memory-constellation';
import { LivingAgentDemo } from '@/components/living-agent-demo';

type FeatureKey = keyof ReturnType<typeof useI18n>['messages']['landing']['features'];

const agentFeatures: Array<{
  emoji: string;
  titleKey: FeatureKey;
  descKey: FeatureKey;
  specialtyKey: FeatureKey;
  accentText: string;
  accentChip: string;
  accentRule: string;
  accentGlow: string;
  chatPath: string;
  /** Bento grid placement on lg+ */
  bento: string;
  featured?: boolean;
}> = [
  {
    emoji: '📚',
    titleKey: 'tutor',
    descKey: 'tutorDesc',
    specialtyKey: 'tutorSpecialty',
    accentText: 'text-primary',
    accentChip: 'border-primary/25 bg-primary/10 text-primary',
    accentRule: 'bg-primary',
    accentGlow: 'hover:shadow-[0_20px_50px_-20px_hsl(158_40%_32%_/_0.45)]',
    chatPath: '/app/chat/tutor',
    bento: 'lg:col-span-5 lg:row-span-2',
    featured: true,
  },
  {
    emoji: '🌟',
    titleKey: 'mentor',
    descKey: 'mentorDesc',
    specialtyKey: 'mentorSpecialty',
    accentText: 'text-accent-amber',
    accentChip: 'border-accent-amber/25 bg-accent-amber/10 text-accent-amber',
    accentRule: 'bg-accent-amber',
    accentGlow: 'hover:shadow-[0_20px_50px_-20px_hsl(32_68%_46%_/_0.4)]',
    chatPath: '/app/chat/mentor',
    bento: 'lg:col-span-4',
  },
  {
    emoji: '💪',
    titleKey: 'coach',
    descKey: 'coachDesc',
    specialtyKey: 'coachSpecialty',
    accentText: 'text-accent-cyan',
    accentChip: 'border-accent-cyan/25 bg-accent-cyan/10 text-accent-cyan',
    accentRule: 'bg-accent-cyan',
    accentGlow: 'hover:shadow-[0_20px_50px_-20px_hsl(172_30%_34%_/_0.4)]',
    chatPath: '/app/chat/coach',
    bento: 'lg:col-span-3',
  },
  {
    emoji: '✍️',
    titleKey: 'reviewer',
    descKey: 'reviewerDesc',
    specialtyKey: 'reviewerSpecialty',
    accentText: 'text-accent-magenta',
    accentChip: 'border-accent-magenta/25 bg-accent-magenta/10 text-accent-magenta',
    accentRule: 'bg-accent-magenta',
    accentGlow: 'hover:shadow-[0_20px_50px_-20px_hsl(12_55%_50%_/_0.4)]',
    chatPath: '/app/chat/reviewer',
    bento: 'lg:col-span-7',
  },
];

const subjectEmojis = ['📐', '∫', '🧮', '⚛️'];

const trustChips = [
  { dotClass: 'bg-primary', key: 'trustPersonalized' as const },
  { dotClass: 'bg-accent-cyan', key: 'trustAiPowered' as const },
  { dotClass: 'bg-accent-amber', key: 'trustFree' as const },
];

const howItWorksSteps = [
  {
    step: 1,
    titleKey: 'howItWorksStep1Title' as const,
    descKey: 'howItWorksStep1Desc' as const,
    icon: UserPlus,
  },
  {
    step: 2,
    titleKey: 'howItWorksStep2Title' as const,
    descKey: 'howItWorksStep2Desc' as const,
    icon: BookOpen,
  },
  {
    step: 3,
    titleKey: 'howItWorksStep3Title' as const,
    descKey: 'howItWorksStep3Desc' as const,
    icon: GraduationCap,
  },
];

const uniquenessPillars = [
  {
    icon: Brain,
    titleKey: 'memory' as const,
    descKey: 'memoryDesc' as const,
    accent: 'text-primary',
    motif: 'memory' as const,
  },
  {
    icon: Route,
    titleKey: 'adaptive' as const,
    descKey: 'adaptiveDesc' as const,
    accent: 'text-accent-amber',
    motif: 'path' as const,
  },
  {
    icon: Users,
    titleKey: 'multi' as const,
    descKey: 'multiDesc' as const,
    accent: 'text-accent-cyan',
    motif: 'none' as const,
  },
] as const;

export function LandingHero() {
  const { messages, locale } = useI18n();
  const t = messages.landing;
  const reduceMotion = useReducedMotion();

  const fadeUp = (delay = 0) =>
    reduceMotion
      ? {}
      : {
          initial: { opacity: 0, y: 18 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] as const },
        };

  const fadeUpInView = (delay = 0) =>
    reduceMotion
      ? {}
      : {
          initial: { opacity: 0, y: 22 },
          whileInView: { opacity: 1, y: 0 },
          viewport: { once: true, margin: '-60px' },
          transition: { duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] as const },
        };

  const categoryPreview = CURRICULUM_CATEGORIES.slice(0, 8);

  return (
    <>
      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        <div
          className="mesh-gradient pointer-events-none absolute inset-x-0 -top-24 h-[560px] opacity-70"
          aria-hidden
        />
        <div className="bg-dot-grid pointer-events-none absolute inset-0 opacity-40" aria-hidden />

        {/* Signature growth path — brand motif anchored to the hero corner */}
        <GrowthPathMotif
          variant="hero"
          className="pointer-events-none absolute -bottom-4 end-0 hidden h-28 w-48 lg:block xl:h-36 xl:w-64"
        />
        <MemoryConstellation
          variant="subtle"
          className="pointer-events-none absolute start-4 top-24 hidden h-24 w-40 opacity-60 lg:block"
        />

        <div className="relative mx-auto max-w-7xl px-4 pb-16 pt-16 sm:px-6 lg:pb-24 lg:pt-24">
          <div className="grid items-center gap-12 lg:grid-cols-[1fr_1.05fr] lg:gap-10 xl:gap-16">
            {/* Copy — slightly offset for asymmetry */}
            <div className="max-w-xl lg:pe-4">
              <motion.div
                className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-surface-1/70 px-3.5 py-1.5 text-xs font-medium text-muted-foreground shadow-sm backdrop-blur-sm"
                {...fadeUp(0)}
              >
                <Sprout className="h-3.5 w-3.5 text-primary" aria-hidden />
                {t.heroBadge}
              </motion.div>

              <motion.h1
                className="font-display text-[2.75rem] font-medium leading-[1.06] tracking-tight text-foreground sm:text-6xl xl:text-[4.5rem]"
                {...fadeUp(0.08)}
              >
                {t.heroLine1}
                <br />
                <span className="relative inline-block text-primary">
                  {t.heroLine2}
                  <svg
                    viewBox="0 0 200 24"
                    fill="none"
                    aria-hidden
                    className="absolute -bottom-2 start-0 h-3 w-full text-accent-amber/70"
                  >
                    <path
                      d="M 4 18 Q 50 4, 100 14 T 196 10"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                      className="growth-path-stroke"
                      style={{ strokeDasharray: 220, animationDuration: '2.5s' }}
                    />
                  </svg>
                </span>
              </motion.h1>

              <motion.p
                className="mt-8 max-w-lg text-lg leading-relaxed text-muted-foreground"
                {...fadeUp(0.16)}
              >
                {t.subtitle}
              </motion.p>

              <motion.div className="mt-9 flex flex-wrap items-center gap-3" {...fadeUp(0.24)}>
                <Link
                  href="/sign-up"
                  className="group inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-base font-semibold text-primary-foreground shadow-md transition-all hover:brightness-110 hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                >
                  {t.cta}
                  <ArrowRight
                    className="h-4 w-4 transition-transform group-hover:translate-x-0.5 rtl:rotate-180 rtl:group-hover:-translate-x-0.5"
                    aria-hidden
                  />
                </Link>
                <Link
                  href="/learn"
                  className="inline-flex items-center gap-2 rounded-xl border border-border-bright bg-surface-1 px-6 py-3 text-base font-medium text-foreground transition-colors hover:bg-surface-2"
                >
                  {t.browseContent}
                </Link>
              </motion.div>

              <motion.div
                className="mt-9 flex flex-wrap items-center gap-x-6 gap-y-2"
                {...fadeUp(0.32)}
              >
                {trustChips.map(({ dotClass, key }) => (
                  <div key={key} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span className={cn('h-1.5 w-1.5 rounded-full', dotClass)} aria-hidden />
                    {t[key]}
                  </div>
                ))}
              </motion.div>
            </div>

            {/* Living multi-agent demo */}
            <motion.div
              {...(reduceMotion
                ? {}
                : {
                    initial: { opacity: 0, y: 28, scale: 0.98 },
                    animate: { opacity: 1, y: 0, scale: 1 },
                    transition: { duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] },
                  })}
            >
              <LivingAgentDemo />
            </motion.div>
          </div>

          {/* Asymmetric stats bento */}
          <motion.div
            className="mt-16 grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-12"
            {...fadeUpInView(0.1)}
          >
            <div className="card-punch relative col-span-1 overflow-hidden rounded-2xl p-5 lg:col-span-3">
              <GrowthPathMotif
                variant="subtle"
                className="absolute -end-2 -top-2 h-16 w-28"
              />
              <AnimatedCounter
                end={13}
                className="font-display relative text-3xl font-semibold text-foreground tabular-nums sm:text-4xl"
              />
              <p className="relative mt-1 text-sm text-muted-foreground">{t.statsCoursesLabel}</p>
            </div>
            <div className="card-punch col-span-1 rounded-2xl p-5 lg:col-span-3">
              <AnimatedCounter
                end={4}
                className="font-display text-3xl font-semibold text-foreground tabular-nums sm:text-4xl"
              />
              <p className="mt-1 text-sm text-muted-foreground">{t.statsAgentsLabel}</p>
            </div>
            <div className="card-punch col-span-2 rounded-2xl p-5 lg:col-span-4">
              <div className="mb-2 flex gap-1.5">
                {subjectEmojis.map((emoji) => (
                  <span
                    key={emoji}
                    className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface-2 text-base transition-transform hover:scale-110"
                    aria-hidden
                  >
                    {emoji}
                  </span>
                ))}
              </div>
              <p className="text-sm leading-snug text-muted-foreground">{t.platformHighlight}</p>
            </div>
            <div className="card-punch relative col-span-2 overflow-hidden rounded-2xl p-5 lg:col-span-2">
              <MemoryConstellation className="absolute -end-4 -top-2 h-20 w-32" variant="subtle" />
              <Brain className="relative h-7 w-7 text-primary" aria-hidden />
              <p className="relative mt-2 text-sm font-medium text-foreground">
                {t.features.memory}
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Uniqueness pillars — what only ASF has ─────────────────────── */}
      <section className="relative border-y border-border bg-surface-2/50 py-16 lg:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.div className="mx-auto max-w-2xl text-center" {...fadeUpInView(0)}>
            <span className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-primary">
              <Network className="h-3.5 w-3.5" aria-hidden />
              {t.uniqueHeading}
            </span>
            <p className="mt-3 text-lg leading-relaxed text-muted-foreground">
              {t.uniqueSubheading}
            </p>
          </motion.div>

          <div className="mt-12 grid gap-4 md:grid-cols-3">
            {uniquenessPillars.map(({ icon: Icon, titleKey, descKey, accent, motif }, i) => (
              <motion.article
                key={titleKey}
                className="card-punch group relative overflow-hidden rounded-2xl p-6"
                {...fadeUpInView(i * 0.08)}
              >
                {motif === 'memory' ? (
                  <MemoryConstellation
                    className="absolute -end-6 -top-4 h-24 w-40 transition-opacity group-hover:opacity-80"
                    variant="subtle"
                  />
                ) : null}
                {motif === 'path' ? (
                  <GrowthPathMotif
                    className="absolute -end-4 -top-2 h-20 w-36 transition-opacity group-hover:opacity-90"
                    variant="subtle"
                  />
                ) : null}
                {motif === 'none' ? (
                  <div
                    className="absolute -end-2 top-4 flex gap-1 opacity-40 transition-opacity group-hover:opacity-70"
                    aria-hidden
                  >
                    {['📚', '🌟', '💪', '✍️'].map((e) => (
                      <span
                        key={e}
                        className="flex h-8 w-8 items-center justify-center rounded-full bg-surface-2 text-sm"
                      >
                        {e}
                      </span>
                    ))}
                  </div>
                ) : null}
                <Icon className={cn('relative h-6 w-6', accent)} aria-hidden />
                <h3 className={cn('relative mt-4 font-display text-xl font-medium', accent)}>
                  {t.features[titleKey]}
                </h3>
                <p className="relative mt-2 text-sm leading-relaxed text-muted-foreground">
                  {t.features[descKey]}
                </p>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* ── Agents bento ────────────────────────────────────────────────── */}
      <section className="relative bg-surface-1/60 py-20 lg:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.div className="mx-auto max-w-2xl text-center" {...fadeUpInView(0)}>
            <span className="text-xs font-semibold uppercase tracking-widest text-accent-amber">
              {t.platformLabel}
            </span>
            <h2 className="mt-3 font-display text-4xl font-medium tracking-tight text-foreground lg:text-5xl">
              {t.featuresHeading}
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
              {t.featuresSubheading}
            </p>
          </motion.div>

          <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-12 lg:grid-rows-2">
            {agentFeatures.map(
              (
                {
                  emoji,
                  titleKey,
                  descKey,
                  specialtyKey,
                  accentText,
                  accentChip,
                  accentRule,
                  accentGlow,
                  chatPath,
                  bento,
                  featured,
                },
                i,
              ) => (
                <motion.article
                  key={titleKey}
                  className={cn(
                    'agent-card card-punch group relative flex flex-col overflow-hidden rounded-2xl p-6',
                    accentGlow,
                    bento,
                    featured && 'lg:p-8',
                  )}
                  {...fadeUpInView(i * 0.07)}
                >
                  <span className={cn('absolute inset-x-0 top-0 h-1', accentRule)} aria-hidden />
                  <div className="mb-4 flex items-start justify-between gap-2">
                    <span
                      className={cn('leading-none', featured ? 'text-5xl' : 'text-3xl')}
                      role="img"
                      aria-hidden
                    >
                      {emoji}
                    </span>
                    <span
                      className={cn(
                        'rounded-full border px-2.5 py-0.5 text-xs font-medium',
                        accentChip,
                      )}
                    >
                      {t.features[specialtyKey]}
                    </span>
                  </div>

                  <h3
                    className={cn(
                      'font-display mb-2 font-medium',
                      accentText,
                      featured ? 'text-3xl' : 'text-2xl',
                    )}
                  >
                    {t.features[titleKey]}
                  </h3>

                  <p
                    className={cn(
                      'flex-1 leading-relaxed text-muted-foreground',
                      featured ? 'text-base' : 'text-sm',
                    )}
                  >
                    {t.features[descKey]}
                  </p>

                  <Link
                    href={chatPath}
                    className={cn(
                      'mt-5 inline-flex items-center gap-1 text-sm font-medium transition-all group-hover:gap-2',
                      accentText,
                    )}
                  >
                    {t.openChat}
                    <ArrowRight className="h-3.5 w-3.5 rtl:rotate-180" aria-hidden />
                  </Link>
                </motion.article>
              ),
            )}
          </div>
        </div>
      </section>

      {/* ── How it works — growth path connects the steps ───────────────── */}
      <section className="py-20 lg:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.h2
            className="text-center font-display text-4xl font-medium tracking-tight text-foreground lg:text-5xl"
            {...fadeUpInView(0)}
          >
            {t.howItWorksHeading}
          </motion.h2>

          <div className="relative mt-16">
            <GrowthPathMotif
              variant="subtle"
              className="pointer-events-none absolute -top-6 start-1/2 hidden h-16 w-full max-w-lg -translate-x-1/2 md:block"
            />

            <div className="grid gap-12 md:grid-cols-3 md:gap-8">
              {howItWorksSteps.map(({ step, titleKey, descKey, icon: Icon }, i) => (
                <motion.div
                  key={step}
                  className="relative flex flex-col items-center text-center"
                  {...fadeUpInView(i * 0.1)}
                >
                  <div className="relative z-10 mb-5 flex h-14 w-14 items-center justify-center rounded-full border border-border bg-surface-1 shadow-sm transition-transform hover:scale-105">
                    <Icon className="h-6 w-6 text-primary" aria-hidden />
                    <span className="absolute -end-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                      {step}
                    </span>
                  </div>
                  <h3 className="font-display mb-2 text-xl font-medium text-foreground">
                    {t[titleKey]}
                  </h3>
                  <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
                    {t[descKey]}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>

          <motion.div className="mt-20" {...fadeUpInView(0)}>
            <Marquee speed={35} className="py-1">
              {categoryPreview.map((cat) => (
                <span
                  key={cat.id}
                  className="inline-flex shrink-0 items-center gap-2 rounded-full border border-border bg-surface-1 px-4 py-2 text-sm text-foreground shadow-sm transition-colors hover:border-primary/40 hover:bg-primary/5"
                >
                  <span aria-hidden>{cat.emoji}</span>
                  {locale === 'he' ? cat.heLabel : cat.enLabel}
                </span>
              ))}
            </Marquee>
            <div className="mt-6 text-center">
              <Link
                href="/learn"
                className="inline-flex items-center gap-1.5 text-sm font-medium text-primary transition-opacity hover:opacity-70"
              >
                <Compass className="h-4 w-4" aria-hidden />
                {t.viewAll}
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Closing CTA ─────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-primary py-24 lg:py-32">
        <div className="bg-grain pointer-events-none absolute inset-0" aria-hidden />
        <GrowthPathMotif
          variant="hero"
          className="pointer-events-none absolute -start-8 bottom-8 h-24 w-40 opacity-30 invert dark:opacity-20 dark:invert-0"
        />
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            backgroundImage:
              'radial-gradient(at 20% 20%, hsl(32 68% 55% / 0.35), transparent 55%), radial-gradient(at 80% 80%, hsl(12 55% 55% / 0.3), transparent 55%)',
          }}
          aria-hidden
        />
        <div className="relative z-10 mx-auto max-w-3xl px-4 text-center text-primary-foreground">
          <motion.h2
            className="font-display text-4xl font-medium tracking-tight lg:text-6xl"
            {...fadeUpInView(0)}
          >
            {t.closingHeading}
          </motion.h2>
          <motion.p
            className="mx-auto mt-5 max-w-xl text-lg leading-relaxed text-primary-foreground/80"
            {...fadeUpInView(0.08)}
          >
            {t.closingSubtitle}
          </motion.p>
          <motion.div className="mt-10" {...fadeUpInView(0.16)}>
            <Link
              href="/sign-up"
              className="group inline-flex items-center gap-2 rounded-xl bg-surface-1 px-8 py-4 text-base font-semibold text-primary shadow-lg transition-all hover:-translate-y-0.5 hover:shadow-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-1 focus-visible:ring-offset-2 focus-visible:ring-offset-primary"
            >
              {t.cta}
              <ArrowRight
                className="h-4 w-4 transition-transform group-hover:translate-x-0.5 rtl:rotate-180 rtl:group-hover:-translate-x-0.5"
                aria-hidden
              />
            </Link>
          </motion.div>
        </div>
      </section>
    </>
  );
}
