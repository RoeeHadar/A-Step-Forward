'use client';

import Link from 'next/link';
import { motion, useReducedMotion } from 'framer-motion';
import { Brain, Route, Users } from 'lucide-react';
import { Button } from '@asf/ui/button';
import { Card, CardDescription, CardHeader, CardTitle } from '@asf/ui/card';
import { useI18n } from '@/providers/i18n-provider';

const features = [
  { icon: Brain, titleKey: 'memory' as const, descKey: 'memoryDesc' as const },
  { icon: Route, titleKey: 'adaptive' as const, descKey: 'adaptiveDesc' as const },
  { icon: Users, titleKey: 'multi' as const, descKey: 'multiDesc' as const },
];

export function LandingHero() {
  const { messages } = useI18n();
  const t = messages.landing;
  const reduceMotion = useReducedMotion();

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
      <motion.section className="mx-auto max-w-5xl px-4 py-20 text-center" {...fadeUp}>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">{t.hero}</h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">{t.subtitle}</p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Button asChild size="lg">
            <Link href="/sign-up">{t.cta}</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/sign-in">Sign in</Link>
          </Button>
        </div>
      </motion.section>

      <section className="border-t border-border bg-muted/30 py-16">
        <div className="mx-auto grid max-w-5xl gap-6 px-4 md:grid-cols-3">
          {features.map(({ icon: Icon, titleKey, descKey }, i) => (
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
              <Card className="h-full">
                <CardHeader>
                  <Icon className="mb-2 h-8 w-8 text-primary" aria-hidden />
                  <CardTitle>{t.features[titleKey]}</CardTitle>
                  <CardDescription>{t.features[descKey]}</CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      <motion.section className="py-16" {...fadeUp}>
        <div className="mx-auto max-w-3xl px-4 text-center">
          <h2 className="text-2xl font-semibold">Ready to take a step forward?</h2>
          <p className="mt-3 text-muted-foreground">
            Join learners who study with AI agents that remember, adapt, and grow with them.
          </p>
          <Button asChild className="mt-6" size="lg">
            <Link href="/sign-up">{t.cta}</Link>
          </Button>
        </div>
      </motion.section>
    </>
  );
}
