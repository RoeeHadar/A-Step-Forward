'use client';

import { useEffect, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { cn } from '@asf/ui';
import { useI18n } from '@/providers/i18n-provider';

type DemoAgent = 'tutor' | 'mentor' | 'coach' | 'reviewer';

const AGENTS: Array<{
  id: DemoAgent;
  emoji: string;
  titleKey: 'tutor' | 'mentor' | 'coach' | 'reviewer';
  userKey: 'demoUserMsg' | 'demoMentorUserMsg' | 'demoCoachUserMsg' | 'demoReviewerUserMsg';
  agentKey: 'demoTutorMsg' | 'demoMentorMsg' | 'demoCoachMsg' | 'demoReviewerMsg';
  bubbleClass: string;
  chipClass: string;
  orbitClass: string;
}> = [
  {
    id: 'tutor',
    emoji: '📚',
    titleKey: 'tutor',
    userKey: 'demoUserMsg',
    agentKey: 'demoTutorMsg',
    bubbleClass: 'bg-primary text-primary-foreground',
    chipClass: 'border-primary/30 bg-primary/10 text-primary',
    orbitClass: 'orbit-drift-a',
  },
  {
    id: 'mentor',
    emoji: '🌟',
    titleKey: 'mentor',
    userKey: 'demoMentorUserMsg',
    agentKey: 'demoMentorMsg',
    bubbleClass: 'bg-accent-amber text-primary-foreground',
    chipClass: 'border-accent-amber/30 bg-accent-amber/10 text-accent-amber',
    orbitClass: 'orbit-drift-b',
  },
  {
    id: 'coach',
    emoji: '💪',
    titleKey: 'coach',
    userKey: 'demoCoachUserMsg',
    agentKey: 'demoCoachMsg',
    bubbleClass: 'bg-accent-cyan text-primary-foreground',
    chipClass: 'border-accent-cyan/30 bg-accent-cyan/10 text-accent-cyan',
    orbitClass: 'orbit-drift-c',
  },
  {
    id: 'reviewer',
    emoji: '✍️',
    titleKey: 'reviewer',
    userKey: 'demoReviewerUserMsg',
    agentKey: 'demoReviewerMsg',
    bubbleClass: 'bg-accent-magenta text-primary-foreground',
    chipClass: 'border-accent-magenta/30 bg-accent-magenta/10 text-accent-magenta',
    orbitClass: 'orbit-drift-d',
  },
];

/** Orbit positions around the demo card — RTL-aware via logical properties. */
const ORBIT_SLOTS = [
  'top-6 -start-3',
  '-top-2 end-8',
  'bottom-16 -end-2',
  'bottom-4 start-6',
] as const;

function TypedMessage({ text, active }: { text: string; active: boolean }) {
  const [display, setDisplay] = useState('');
  useEffect(() => {
    if (!active) return;
    let i = 0;
    setDisplay('');
    const id = setInterval(() => {
      i++;
      setDisplay(text.slice(0, i));
      if (i >= text.length) clearInterval(id);
    }, 28);
    return () => clearInterval(id);
  }, [text, active]);
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

/**
 * Living hero demo — cycles through all four agents so visitors immediately
 * see the multi-agent team in action, not a static single chat screenshot.
 */
export function LivingAgentDemo({ className }: { className?: string }) {
  const { messages } = useI18n();
  const t = messages.landing;
  const reduceMotion = useReducedMotion();
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);

  const agent = AGENTS[index] ?? AGENTS[0]!;
  const userMsg = t[agent.userKey];
  const agentMsg = t[agent.agentKey];
  const agentName = t.features[agent.titleKey];

  useEffect(() => {
    if (reduceMotion || paused) return;
    const id = setInterval(() => setIndex((i) => (i + 1) % AGENTS.length), 9000);
    return () => clearInterval(id);
  }, [reduceMotion, paused]);

  return (
    <div
      className={cn('relative', className)}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
    >
      {/* Orbiting agent chips — the "team around you" signature moment */}
      {AGENTS.map((a, i) => (
        <button
          key={a.id}
          type="button"
          onClick={() => setIndex(i)}
          className={cn(
            'absolute z-20 hidden rounded-full border px-2.5 py-1 text-xs font-medium shadow-sm backdrop-blur-sm transition-all sm:inline-flex sm:items-center sm:gap-1.5 sm:px-3 sm:py-1.5',
            ORBIT_SLOTS[i],
            a.orbitClass,
            a.chipClass,
            index === i ? 'scale-105 ring-2 ring-ring/40' : 'opacity-70 hover:opacity-100',
          )}
          aria-label={t.features[a.titleKey]}
          aria-pressed={index === i}
        >
          <span aria-hidden>{a.emoji}</span>
          <span className="hidden lg:inline">{t.features[a.titleKey]}</span>
        </button>
      ))}

      <div className="iridescent-border relative flex min-h-[360px] flex-col overflow-hidden p-6 lg:min-h-[440px]">
        {/* Agent-color wash that shifts with the active agent */}
        <AnimatePresence mode="wait">
          <motion.div
            key={agent.id}
            className={cn(
              'pointer-events-none absolute inset-0 opacity-[0.07]',
              agent.id === 'tutor' && 'bg-primary',
              agent.id === 'mentor' && 'bg-accent-amber',
              agent.id === 'coach' && 'bg-accent-cyan',
              agent.id === 'reviewer' && 'bg-accent-magenta',
            )}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.07 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            aria-hidden
          />
        </AnimatePresence>

        <div className="relative mb-5 flex items-center justify-between gap-2 border-b border-border pb-4">
          <AnimatePresence mode="wait">
            <motion.span
              key={agent.id}
              className="flex items-center gap-2 text-sm font-medium text-foreground"
              initial={reduceMotion ? false : { opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={reduceMotion ? undefined : { opacity: 0, x: 8 }}
              transition={{ duration: 0.25 }}
            >
              <span className="text-lg" aria-hidden>
                {agent.emoji}
              </span>
              {agentName}
            </motion.span>
          </AnimatePresence>
          <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
            {t.demoLabel}
          </span>
        </div>

        {/* Mobile agent picker */}
        <div className="relative mb-4 flex flex-wrap gap-1.5 sm:hidden">
          {AGENTS.map((a, i) => (
            <button
              key={a.id}
              type="button"
              onClick={() => setIndex(i)}
              className={cn(
                'rounded-full border px-2.5 py-0.5 text-xs font-medium transition-all',
                a.chipClass,
                index === i ? 'ring-2 ring-ring/40' : 'opacity-60',
              )}
              aria-pressed={index === i}
            >
              {a.emoji} {t.features[a.titleKey]}
            </button>
          ))}
        </div>

        <div className="relative flex flex-1 flex-col justify-end gap-3">
          <AnimatePresence mode="wait">
            <motion.div
              key={`${agent.id}-convo`}
              className="flex flex-col gap-3"
              initial={reduceMotion ? false : { opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={reduceMotion ? undefined : { opacity: 0, y: -8 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            >
              <div className="flex justify-end">
                <div
                  className={cn(
                    'max-w-[85%] rounded-2xl rounded-ee-sm px-4 py-3 text-sm shadow-sm',
                    agent.bubbleClass,
                  )}
                >
                  {userMsg}
                </div>
              </div>
              <div className="flex justify-start">
                <div className="max-w-[90%] rounded-2xl rounded-es-sm border border-border bg-surface-2 px-4 py-3 text-sm leading-relaxed text-foreground">
                  <TypedMessage text={agentMsg} active />
                </div>
              </div>
              <TypingIndicator />
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Progress dots */}
        <div className="relative mt-4 flex justify-center gap-1.5" aria-hidden>
          {AGENTS.map((a, i) => (
            <span
              key={a.id}
              className={cn(
                'h-1.5 rounded-full transition-all duration-300',
                index === i ? 'w-5 bg-primary' : 'w-1.5 bg-border-bright',
              )}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
