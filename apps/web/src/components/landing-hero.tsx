'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import {
  ArrowRight,
  Brain,
  BookOpen,
  Compass,
  GraduationCap,
  Sprout,
  UserPlus,
} from 'lucide-react';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';
import { CURRICULUM_CATEGORIES } from '@/lib/curriculum-categories';
import { AnimatedCounter } from '@/components/animated-counter';
import { Marquee } from '@/components/marquee';

type FeatureKey = keyof ReturnType<typeof useI18n>['messages']['landing']['features'];

const agentFeatures: Array<{
  emoji: string;
  titleKey: FeatureKey;
  descKey: FeatureKey;
  specialtyKey: FeatureKey;
  accentText: string;
  accentChip: string;
  accentRule: string;
  chatPath: string;
}> = [
  {
    emoji: '📚',
    titleKey: 'tutor',
    descKey: 'tutorDesc',
    specialtyKey: 'tutorSpecialty',
    accentText: 'text-primary',
    accentChip: 'border-primary/25 bg-primary/10 text-primary',
    accentRule: 'bg-primary',
    chatPath: '/app/chat/tutor',
  },
  {
    emoji: '🌟',
    titleKey: 'mentor',
    descKey: 'mentorDesc',
    specialtyKey: 'mentorSpecialty',
    accentText: 'text-accent-amber',
    accentChip: 'border-accent-amber/25 bg-accent-amber/10 text-accent-amber',
    accentRule: 'bg-accent-amber',
    chatPath: '/app/chat/mentor',
  },
  {
    emoji: '💪',
    titleKey: 'coach',
    descKey: 'coachDesc',
    specialtyKey: 'coachSpecialty',
    accentText: 'text-accent-cyan',
    accentChip: 'border-accent-cyan/25 bg-accent-cyan/10 text-accent-cyan',
    accentRule: 'bg-accent-cyan',
    chatPath: '/app/chat/coach',
  },
  {
    emoji: '✍️',
    titleKey: 'reviewer',
    descKey: 'reviewerDesc',
    specialtyKey: 'reviewerSpecialty',
    accentText: 'text-accent-magenta',
    accentChip: 'border-accent-magenta/25 bg-accent-magenta/10 text-accent-magenta',
    accentRule: 'bg-accent-magenta',
    chatPath: '/app/chat/reviewer',
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

function TypedMessage({ text, restartMs = 12000 }: { text: string; restartMs?: number }) {
  const [display, setDisplay] = useState('');
  useEffect(() => {
    let i = 0;
    let typeId: ReturnType<typeof setInterval>;
    const startTyping = () => {
      i = 0;
      setDisplay('');
      typeId = setInterval(() => {
        i++;
        setDisplay(text.slice(0, i));
        if (i >= text.length) clearInterval(typeId);
      }, 35);
    };
    startTyping();
    const restartId = setInterval(startTyping, restartMs);
    return () => {
      clearInterval(typeId);
      clearInterval(restartId);
    };
  }, [text, restartMs]);
  return (
    <>
      {display}
      <span className="ms-0.5 inline-block h-3 w-0.5 animate-pulse bg-current align-middle" />
    </>
  );
}

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
        {/* Soft natural light wash — warm, blurred, anchored to one corner
            instead of floating neon orbs. */}
        <div
          className="mesh-gradient pointer-events-none absolute inset-x-0 -top-24 h-[520px] opacity-70"
          aria-hidden
        />
        <div
          className="bg-dot-grid pointer-events-none absolute inset-0 opacity-40"
          aria-hidden
        />

        <div className="relative mx-auto max-w-7xl px-4 pb-16 pt-16 sm:px-6 lg:pb-24 lg:pt-24">
          <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16">
            {/* Copy */}
            <div className="max-w-xl">
              <motion.div
                className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-surface-1/70 px-3.5 py-1.5 text-xs font-medium text-muted-foreground shadow-sm"
                {...fadeUp(0)}
              >
                <Sprout className="h-3.5 w-3.5 text-primary" aria-hidden />
                {t.heroBadge}
              </motion.div>

              <motion.h1
                className="font-display text-[2.75rem] font-medium leading-[1.08] tracking-tight text-foreground sm:text-6xl xl:text-[4.25rem]"
                {...fadeUp(0.08)}
              >
                {t.heroLine1}
                <br />
                <span className="relative text-primary">
                  {t.heroLine2}
                  <span
                    className="absolute inset-x-0 -bottom-1 h-[3px] rounded-full bg-accent-amber/60"
                    aria-hidden
                  />
                </span>
              </motion.h1>

              <motion.p
                className="mt-7 max-w-lg text-lg leading-relaxed text-muted-foreground"
                {...fadeUp(0.16)}
              >
                {t.subtitle}
              </motion.p>

              <motion.div className="mt-9 flex flex-wrap items-center gap-3" {...fadeUp(0.24)}>
                <Link
                  href="/sign-up"
                  className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-base font-semibold text-primary-foreground shadow-md transition-all hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                >
                  {t.cta}
                  <ArrowRight className="h-4 w-4 rtl:rotate-180" aria-hidden />
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

            {/* Tutor conversation preview — matte paper card, warm elevation */}
            <motion.div
              className="iridescent-border relative flex min-h-[360px] flex-col p-6 lg:min-h-[440px]"
              {...(reduceMotion
                ? {}
                : {
                    initial: { opacity: 0, y: 28, rotate: -0.6 },
                    animate: { opacity: 1, y: 0, rotate: 0 },
                    transition: { duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] },
                  })}
            >
              <div className="mb-5 flex items-center justify-between gap-2 border-b border-border pb-4">
                <span className="flex items-center gap-2 text-sm font-medium text-foreground">
                  <span className="text-lg" aria-hidden>
                    📚
                  </span>
                  {t.features.tutor}
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                  {t.demoLabel}
                </span>
              </div>

              <div className="flex flex-1 flex-col justify-end gap-3">
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-2xl rounded-ee-sm bg-primary px-4 py-3 text-sm text-primary-foreground shadow-sm">
                    {t.demoUserMsg}
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="max-w-[90%] rounded-2xl rounded-es-sm border border-border bg-surface-2 px-4 py-3 text-sm leading-relaxed text-foreground">
                    <TypedMessage text={t.demoTutorMsg} />
                  </div>
                </div>
                <TypingIndicator />
              </div>
            </motion.div>
          </div>

          {/* Stats strip */}
          <motion.div
            className="mt-16 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-border bg-border sm:grid-cols-4"
            {...fadeUpInView(0.1)}
          >
            <div className="flex flex-col gap-1 bg-surface-1 p-5">
              <AnimatedCounter
                end={13}
                className="font-display text-3xl font-semibold text-foreground tabular-nums"
              />
              <p className="text-sm text-muted-foreground">{t.statsCoursesLabel}</p>
            </div>
            <div className="flex flex-col gap-1 bg-surface-1 p-5">
              <AnimatedCounter
                end={4}
                className="font-display text-3xl font-semibold text-foreground tabular-nums"
              />
              <p className="text-sm text-muted-foreground">{t.statsAgentsLabel}</p>
            </div>
            <div className="flex flex-col justify-center gap-1 bg-surface-1 p-5">
              <div className="flex gap-1.5">
                {subjectEmojis.map((emoji) => (
                  <span
                    key={emoji}
                    className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-2 text-sm"
                    aria-hidden
                  >
                    {emoji}
                  </span>
                ))}
              </div>
              <p className="text-sm text-muted-foreground">{t.platformHighlight}</p>
            </div>
            <div className="flex flex-col justify-center gap-1 bg-surface-1 p-5">
              <Brain className="h-6 w-6 text-primary" aria-hidden />
              <p className="text-sm text-muted-foreground">{t.features.memory}</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Agents ──────────────────────────────────────────────────────── */}
      <section className="relative border-t border-border bg-surface-1/60 py-20 lg:py-28">
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

          <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {agentFeatures.map(
              ({ emoji, titleKey, descKey, specialtyKey, accentText, accentChip, accentRule, chatPath }, i) => (
                <motion.article
                  key={titleKey}
                  className="card-punch group relative flex flex-col overflow-hidden rounded-2xl p-6"
                  {...fadeUpInView(i * 0.08)}
                >
                  <span className={cn('absolute inset-x-0 top-0 h-1', accentRule)} aria-hidden />
                  <div className="mb-4 flex items-start justify-between gap-2">
                    <span className="text-3xl leading-none" role="img" aria-hidden>
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

                  <h3 className={cn('font-display mb-2 text-2xl font-medium', accentText)}>
                    {t.features[titleKey]}
                  </h3>

                  <p className="flex-1 text-sm leading-relaxed text-muted-foreground">
                    {t.features[descKey]}
                  </p>

                  <Link
                    href={chatPath}
                    className={cn(
                      'mt-5 inline-flex items-center gap-1 text-sm font-medium transition-opacity hover:opacity-70',
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

      {/* ── How it works ────────────────────────────────────────────────── */}
      <section className="py-20 lg:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.h2
            className="text-center font-display text-4xl font-medium tracking-tight text-foreground lg:text-5xl"
            {...fadeUpInView(0)}
          >
            {t.howItWorksHeading}
          </motion.h2>

          <div className="relative mt-16 grid gap-12 md:grid-cols-3 md:gap-8">
            <div
              className="pointer-events-none absolute top-7 hidden h-px w-full bg-gradient-to-r from-transparent via-border-bright to-transparent md:block"
              aria-hidden
            />

            {howItWorksSteps.map(({ step, titleKey, descKey, icon: Icon }, i) => (
              <motion.div
                key={step}
                className="relative flex flex-col items-center text-center"
                {...fadeUpInView(i * 0.1)}
              >
                <div className="relative z-10 mb-5 flex h-14 w-14 items-center justify-center rounded-full border border-border bg-surface-1 shadow-sm">
                  <Icon className="h-6 w-6 text-primary" aria-hidden />
                  <span className="absolute -end-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                    {step}
                  </span>
                </div>
                <h3 className="font-display mb-2 text-xl font-medium text-foreground">
                  {t[titleKey]}
                </h3>
                <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">{t[descKey]}</p>
              </motion.div>
            ))}
          </div>

          {/* Subject marquee */}
          <motion.div className="mt-20" {...fadeUpInView(0)}>
            <Marquee speed={35} className="py-1">
              {categoryPreview.map((cat) => (
                <span
                  key={cat.id}
                  className="inline-flex shrink-0 items-center gap-2 rounded-full border border-border bg-surface-1 px-4 py-2 text-sm text-foreground shadow-sm"
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

      {/* ── Closing CTA — deep evergreen band ───────────────────────────── */}
      <section className="relative overflow-hidden bg-primary py-24 lg:py-32">
        <div className="bg-grain pointer-events-none absolute inset-0" aria-hidden />
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
              className="inline-flex items-center gap-2 rounded-xl bg-surface-1 px-8 py-4 text-base font-semibold text-primary shadow-lg transition-transform hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surface-1 focus-visible:ring-offset-2 focus-visible:ring-offset-primary"
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
