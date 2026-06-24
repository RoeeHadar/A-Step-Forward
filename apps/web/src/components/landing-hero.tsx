'use client';

import Link from 'next/link';
import { motion, useReducedMotion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { Card, CardDescription, CardHeader, CardTitle } from '@asf/ui/card';
import { useI18n } from '@/providers/i18n-provider';

const agentFeatures = [
  { emoji: '📚', titleKey: 'tutor' as const, descKey: 'tutorDesc' as const },
  { emoji: '🌟', titleKey: 'mentor' as const, descKey: 'mentorDesc' as const },
  { emoji: '💪', titleKey: 'coach' as const, descKey: 'coachDesc' as const },
  { emoji: '✍️', titleKey: 'reviewer' as const, descKey: 'reviewerDesc' as const },
];

const primaryCtaClass =
  'min-w-[10rem] bg-[#d1fe17] text-base text-[#0f1113] shadow-md hover:bg-[#d1fe17]/90 hover:shadow-lg focus-visible:ring-2 focus-visible:ring-[#d1fe17] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0f1113]';

export function LandingHero() {
  const { messages, locale } = useI18n();
  const t = messages.landing;
  const reduceMotion = useReducedMotion();
  const badgeText = locale === 'he' ? 'למידה מבוסס AI' : 'AI-NATIVE LEARNING';

  const fadeUp = reduceMotion
    ? {}
    : {
        initial: { opacity: 0, y: 16 },
        whileInView: { opacity: 1, y: 0 },
        viewport: { once: true, margin: '-40px' },
        transition: { duration: 0.45 },
      };

  return (
    <>
      <motion.section
        className="relative mx-auto max-w-5xl overflow-hidden px-4 py-16 text-center sm:py-20"
        {...fadeUp}
      >
        <div
          className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-64 bg-gradient-to-b from-primary/10 via-accent/5 to-transparent"
          aria-hidden
        />
        <span className="mb-4 inline-flex items-center rounded-full bg-[rgba(209,254,23,0.12)] px-3 py-1 text-xs font-semibold text-[#d1fe17]">
          {badgeText}
        </span>
        <h1 className="text-balance text-3xl font-bold leading-tight sm:text-5xl md:text-6xl">
          {t.hero}
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-pretty text-base text-muted-foreground sm:text-lg">
          {t.subtitle}
        </p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-3 sm:gap-4">
          <Button asChild size="lg" className={primaryCtaClass}>
            <Link href="/sign-up">
              {t.cta}
              <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="text-base">
            <Link href="/sign-in">{messages.nav.signIn}</Link>
          </Button>
        </div>
      </motion.section>

      <section className="border-t border-border bg-muted/30 py-14 sm:py-16">
        <div className="mx-auto max-w-5xl px-4">
          <h2 className="mb-8 text-center text-xl font-semibold sm:text-2xl">{t.featuresHeading}</h2>
          <div className="grid gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-4">
            {agentFeatures.map(({ emoji, titleKey, descKey }, i) => (
              <motion.div
                key={titleKey}
                {...(reduceMotion
                  ? {}
                  : {
                      initial: { opacity: 0, y: 20 },
                      whileInView: { opacity: 1, y: 0 },
                      viewport: { once: true },
                      transition: { duration: 0.4, delay: i * 0.08 },
                    })}
              >
                <Card className="glass-card h-full backdrop-blur-sm transition-shadow hover:shadow-md">
                  <CardHeader className="space-y-3">
                    <span className="text-3xl" role="img" aria-hidden>
                      {emoji}
                    </span>
                    <CardTitle className="text-lg">{t.features[titleKey]}</CardTitle>
                    <CardDescription className="text-pretty leading-relaxed">
                      {t.features[descKey]}
                    </CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <motion.section className="py-14 sm:py-16" {...fadeUp}>
        <div className="mx-auto max-w-3xl px-4 text-center">
          <h2 className="text-balance text-2xl font-semibold">{t.closingHeading}</h2>
          <p className="mt-3 text-pretty text-muted-foreground">{t.closingSubtitle}</p>
          <Button asChild className={primaryCtaClass} size="lg">
            <Link href="/sign-up">
              {t.cta}
              <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden />
            </Link>
          </Button>
        </div>
      </motion.section>
    </>
  );
}
