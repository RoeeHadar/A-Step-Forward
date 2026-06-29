'use client';

import { useState, useEffect } from 'react';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';

const STORAGE_KEY = 'asf-agents-intro-seen';

const AGENTS = [
  {
    emoji: '\uD83C\uDF93',
    name_he: '\u05DE\u05D5\u05E8\u05D4',
    name_en: 'Tutor',
    desc_he: '\u05DE\u05D3\u05E8\u05D9\u05DA \u05E2\u05DD \u05E9\u05D0\u05DC\u05D5\u05EA \u2014 \u05DC\u05DC\u05DE\u05D9\u05D3\u05D4 \u05E2\u05DE\u05D5\u05E7\u05D4',
    desc_en: 'Guides with questions \u2014 deep understanding',
  },
  {
    emoji: '\uD83D\uDCA1',
    name_he: '\u05DE\u05E1\u05D1\u05D9\u05E8 \u05E9\u05D0\u05DC\u05D5\u05EA \u05D5\u05EA\u05E9\u05D5\u05D1\u05D5\u05EA',
    name_en: 'Q&A Explainer',
    desc_he: '\u05E2\u05D5\u05E0\u05D4 \u05D9\u05E9\u05D9\u05E8\u05D5\u05EA \u05DE\u05EA\u05D5\u05DA \u05D4\u05D7\u05D5\u05DE\u05E8',
    desc_en: 'Direct answers from the curriculum',
  },
  {
    emoji: '\uD83C\uDFCB\uFE0F',
    name_he: '\u05DE\u05D0\u05DE\u05DF',
    name_en: 'Coach',
    desc_he: '\u05EA\u05E8\u05D2\u05D5\u05DC \u05D9\u05D5\u05DE\u05D9 \u05D5\u05E2\u05D9\u05D5\u05DF \u05D1\u05D7\u05D5\u05DC\u05E9\u05D5\u05EA',
    desc_en: 'Daily drills targeting your weak spots',
  },
  {
    emoji: '\uD83E\uDDED',
    name_he: '\u05DE\u05E0\u05D8\u05D5\u05E8',
    name_en: 'Mentor',
    desc_he: '\u05DE\u05D5\u05D8\u05D9\u05D1\u05E6\u05D9\u05D4, \u05D4\u05E8\u05D2\u05DC\u05D9\u05DD \u05D5\u05EA\u05DB\u05E0\u05D5\u05DF',
    desc_en: 'Motivation, habits, and planning',
  },
] as const;

function detectLocale(): 'he' | 'en' {
  if (typeof document === 'undefined') return 'he';
  const match = document.cookie.match(/(?:^|;\s*)asf-locale=([^;]+)/);
  return match?.[1] === 'en' ? 'en' : 'he';
}

export function AgentsIntroBanner() {
  const [visible, setVisible] = useState(false);
  const [isHe, setIsHe] = useState(true);

  useEffect(() => {
    const seen = localStorage.getItem(STORAGE_KEY);
    if (!seen) {
      setIsHe(detectLocale() === 'he');
      setVisible(true);
    }
  }, []);

  function dismiss() {
    localStorage.setItem(STORAGE_KEY, '1');
    setVisible(false);
  }

  if (!visible) return null;

  const dir = isHe ? 'rtl' : 'ltr';
  const title = isHe ? '\u05D4\u05DB\u05D9\u05E8\u05D5 \u05D0\u05EA \u05D4\u05E6\u05D5\u05D5\u05EA \u05E9\u05DC\u05DB\u05DD' : 'Meet Your Learning Team';
  const gotIt = isHe ? '\u05D4\u05D1\u05E0\u05EA\u05D9' : 'Got it';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div
        className={cn('card-punch w-full max-w-lg rounded-2xl p-6')}
        dir={dir}
      >
        <h2 className="font-display mb-1 text-2xl font-bold">
          <span className="bg-gradient-to-r from-primary via-accent-magenta to-accent-cyan bg-clip-text text-transparent">
            {title}
          </span>
        </h2>
        <p className="mb-5 text-sm text-muted-foreground">
          {isHe
            ? '\u05DB\u05DC \u05E1\u05D5\u05DB\u05DF \u05DE\u05D9\u05D5\u05E2\u05D3 \u05DC\u05E6\u05D5\u05E8\u05DA \u05E9\u05D5\u05E0\u05D4 \u2014 \u05D1\u05D7\u05E8 \u05D0\u05EA \u05D4\u05E0\u05DB\u05D5\u05DF \u05DC\u05DA.'
            : 'Each agent serves a different purpose \u2014 pick the right one for your goal.'}
        </p>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {AGENTS.map((a) => (
            <div
              key={a.name_en}
              className="iridescent-border flex items-start gap-3 rounded-xl p-4"
            >
              <span className="text-2xl" aria-hidden>
                {a.emoji}
              </span>
              <div className="min-w-0">
                <p className="font-display font-semibold">
                  {isHe ? a.name_he : a.name_en}
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {isHe ? a.desc_he : a.desc_en}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex justify-center">
          <Button
            onClick={dismiss}
            className="bg-gradient-to-r from-primary to-accent-magenta px-8 font-semibold text-primary-foreground hover:opacity-90"
          >
            {gotIt}
          </Button>
        </div>
      </div>
    </div>
  );
}