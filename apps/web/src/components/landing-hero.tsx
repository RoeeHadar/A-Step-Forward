'use client';

import Link from 'next/link';
import { motion, useReducedMotion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { useI18n } from '@/providers/i18n-provider';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';

type FeatureKey = keyof ReturnType<typeof useI18n>['messages']['landing']['features'];

const agentFeatures: Array<{
  emoji: string;
  titleKey: FeatureKey;
  descKey: FeatureKey;
  specialtyKey: FeatureKey;
  badgeClass: string;
  chatPath: string;
}> = [
  {
    emoji: '📚',
    titleKey: 'tutor',
    descKey: 'tutorDesc',
    specialtyKey: 'tutorSpecialty',
    badgeClass: 'bg-violet-500/15 text-violet-300 border-violet-500/20',
    chatPath: '/app/chat/tutor',
  },
  {
    emoji: '🌟',
    titleKey: 'mentor',
    descKey: 'mentorDesc',
    specialtyKey: 'mentorSpecialty',
    badgeClass: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/20',
    chatPath: '/app/chat/mentor',
  },
  {
    emoji: '💪',
    titleKey: 'coach',
    descKey: 'coachDesc',
    specialtyKey: 'coachSpecialty',
    badgeClass: 'bg-violet-500/15 text-violet-300 border-violet-500/20',
    chatPath: '/app/chat/coach',
  },
  {
    emoji: '✍️',
    titleKey: 'reviewer',
    descKey: 'reviewerDesc',
    specialtyKey: 'reviewerSpecialty',
    badgeClass: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/20',
    chatPath: '/app/chat/reviewer',
  },
];

const trustChips = [
  { dotClass: 'bg-violet-400', key: 'trustOpenSource' as const },
  { dotClass: 'bg-cyan-400', key: 'trustGroq' as const },
  { dotClass: 'bg-green-400', key: 'trustFree' as const },
];

const statItems = [
  { valueKey: 'statsCoursesValue' as const, labelKey: 'statsCoursesLabel' as const, color: 'text-violet-400' },
  { valueKey: 'statsAgentsValue' as const, labelKey: 'statsAgentsLabel' as const, color: 'text-cyan-400' },
  { valueKey: 'statsLessonsValue' as const, labelKey: 'statsLessonsLabel' as const, color: 'text-violet-400' },
];

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

  const heroLines = t.hero.split('\n');

  return (
    <>
      {/* ── Section 1: Hero ── */}
      <section className="relative flex min-h-[90vh] flex-col items-center justify-center overflow-hidden px-4 py-24 text-center">
        {/* Animated gradient mesh background */}
        <div className="hero-mesh-bg pointer-events-none absolute inset-0 -z-10" aria-hidden />

        {/* Subtle grid overlay */}
        <div
          className="pointer-events-none absolute inset-0 -z-10 opacity-[0.03]"
          style={{
            backgroundImage:
              'linear-gradient(hsl(var(--foreground)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--foreground)) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }}
          aria-hidden
        />

        {/* Badge */}
        <motion.div {...fadeUp(0)}>
          <span className="mb-6 inline-flex items-center rounded-full border border-violet-500/30 bg-violet-950/60 px-3 py-1 text-xs font-medium text-violet-300 backdrop-blur-sm">
            {t.heroBadge}
          </span>
        </motion.div>

        {/* Hero headline */}
        <motion.h1
          className="mb-6 max-w-4xl text-5xl font-bold leading-[1.05] tracking-tight text-transparent sm:text-6xl md:text-7xl lg:text-8xl"
          style={{
            backgroundImage: 'linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.9) 50%, rgba(255,255,255,0.5) 100%)',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
          }}
          {...fadeUp(0.08)}
        >
          {heroLines.map((line, i) => (
            <span key={i}>
              {line}
              {i < heroLines.length - 1 && <br />}
            </span>
          ))}
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          className="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-muted-foreground md:text-xl"
          {...fadeUp(0.16)}
        >
          {t.subtitle}
        </motion.p>

        {/* CTA row */}
        <motion.div
          className="flex flex-wrap items-center justify-center gap-3 sm:gap-4"
          {...fadeUp(0.24)}
        >
          <Link
            href="/sign-up"
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-violet-600 to-violet-700 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:from-violet-500 hover:to-violet-600 hover:shadow-violet-500/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            {t.cta}
            <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
          </Link>
          <Link
            href="/sign-in"
            className="inline-flex items-center gap-2 rounded-lg border border-white/15 px-6 py-3 text-base font-medium text-white/80 transition-all hover:border-white/30 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20"
          >
            {messages.nav.signIn}
          </Link>
        </motion.div>

        {/* Trust chips */}
        <motion.div
          className="mt-8 flex flex-wrap items-center justify-center gap-5"
          {...fadeUp(0.32)}
        >
          {trustChips.map(({ dotClass, key }) => (
            <div key={key} className="flex items-center gap-2 text-xs text-muted-foreground">
              <div className={`h-1.5 w-1.5 rounded-full ${dotClass}`} aria-hidden />
              {t[key]}
            </div>
          ))}
        </motion.div>
      </section>

      {/* ── Section 2: Stats bar ── */}
      <motion.section
        className="border-y border-white/5 bg-white/[0.02] py-10"
        {...fadeUpInView(0)}
      >
        <div className="mx-auto flex max-w-3xl flex-col items-center justify-around gap-8 px-4 sm:flex-row sm:gap-4">
          {statItems.map(({ valueKey, labelKey, color }) => (
            <div key={valueKey} className="flex flex-col items-center gap-1 text-center">
              <span className={`text-4xl font-bold tabular-nums tracking-tight sm:text-5xl ${color}`}>
                {t[valueKey]}
              </span>
              <span className="text-sm text-muted-foreground">{t[labelKey]}</span>
            </div>
          ))}
        </div>
      </motion.section>

      {/* ── Section 3: Agent cards ── */}
      <section className="py-20 sm:py-24">
        <div className="mx-auto max-w-6xl px-4">
          <motion.h2
            className="mb-12 text-center text-3xl font-bold md:text-4xl"
            {...fadeUpInView(0)}
          >
            {t.featuresHeading}
          </motion.h2>
          <div className="grid gap-4 sm:grid-cols-2 sm:gap-5 lg:grid-cols-4">
            {agentFeatures.map(({ emoji, titleKey, descKey, specialtyKey, badgeClass, chatPath }, i) => (
              <motion.article
                key={titleKey}
                className="group flex flex-col rounded-2xl border border-white/[0.08] bg-card p-6 transition-all hover:border-violet-500/30 hover:shadow-lg hover:shadow-violet-500/10"
                {...fadeUpInView(i * 0.08)}
              >
                {/* Card header */}
                <div className="mb-4 flex items-start justify-between gap-2">
                  <span className="text-[2.5rem] leading-none" role="img" aria-hidden>
                    {emoji}
                  </span>
                  <span
                    className={`mt-1 inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${badgeClass}`}
                  >
                    {t.features[specialtyKey]}
                  </span>
                </div>

                {/* Agent name with gradient */}
                <h3
                  className="mb-2 text-lg font-semibold text-transparent"
                  style={{
                    backgroundImage:
                      'linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.7) 100%)',
                    WebkitBackgroundClip: 'text',
                    backgroundClip: 'text',
                  }}
                >
                  {t.features[titleKey]}
                </h3>

                {/* Description */}
                <p className="flex-1 text-sm leading-relaxed text-muted-foreground">
                  {t.features[descKey]}
                </p>

                {/* Open chat link */}
                <Link
                  href={chatPath}
                  className="mt-5 inline-flex text-sm font-medium text-violet-400 transition-colors hover:text-violet-300"
                >
                  {t.openChat}
                </Link>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* ── Section 4: Subject categories teaser ── */}
      <motion.section
        className="py-16 sm:py-20"
        {...fadeUpInView(0)}
      >
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="mb-8 text-center text-3xl font-bold md:text-4xl">
            {t.subjectsHeading}
          </h2>
          <div className="-mx-4 flex gap-3 overflow-x-auto px-4 pb-3">
            {CURRICULUM_CATEGORIES.slice(0, 6).map((cat) => (
              <div
                key={cat.id}
                className="inline-flex shrink-0 cursor-default items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.03] px-4 py-2.5 text-sm text-muted-foreground transition-colors hover:border-violet-500/30 hover:text-foreground"
              >
                <span aria-hidden>{cat.emoji}</span>
                <span>{locale === 'he' ? cat.heLabel : cat.enLabel}</span>
              </div>
            ))}
          </div>
          <div className="mt-6 text-center">
            <Link
              href="/app/lessons"
              className="inline-flex items-center gap-1 text-sm font-medium text-violet-400 transition-colors hover:text-violet-300"
            >
              {t.viewAll}
            </Link>
          </div>
        </div>
      </motion.section>

      {/* ── Section 5: Closing CTA banner ── */}
      <motion.section
        className="relative overflow-hidden py-24 sm:py-32"
        {...fadeUpInView(0)}
      >
        {/* Gradient background */}
        <div
          className="pointer-events-none absolute inset-0 -z-10"
          style={{
            background:
              'linear-gradient(135deg, rgba(109,40,217,0.40) 0%, transparent 50%, rgba(8,145,178,0.20) 100%)',
          }}
          aria-hidden
        />
        {/* Subtle border top/bottom */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-violet-500/30 to-transparent" aria-hidden />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" aria-hidden />

        <div className="mx-auto max-w-3xl px-4 text-center">
          <motion.h2
            className="mb-4 text-balance text-3xl font-bold sm:text-4xl md:text-5xl"
            {...fadeUpInView(0)}
          >
            {t.closingHeading}
          </motion.h2>
          <motion.p
            className="mx-auto mb-10 max-w-xl text-pretty text-lg text-muted-foreground"
            {...fadeUpInView(0.08)}
          >
            {t.closingSubtitle}
          </motion.p>
          <motion.div {...fadeUpInView(0.16)}>
            <Link
              href="/sign-up"
              className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-violet-600 to-violet-700 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-violet-500/25 transition-all hover:from-violet-500 hover:to-violet-600 hover:shadow-violet-500/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              {t.cta}
              <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
            </Link>
          </motion.div>
        </div>
      </motion.section>
    </>
  );
}
