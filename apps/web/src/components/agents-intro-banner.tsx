'use client';

import { useState, useEffect } from 'react';
import { Button } from '@asf/ui/button';
import { cn } from '@asf/ui';

const STORAGE_KEY = 'asf-agents-intro-seen';

const AGENTS = [
  {
    emoji: '🎓',
    name_he: 'מורה',
    name_en: 'Tutor',
    desc_he: 'מדריך עם שאלות — ללמידה עמוקה',
    desc_en: 'Guides with questions — deep understanding',
  },
  {
    emoji: '💡',
    name_he: 'מסביר שאלות ותשובות',
    name_en: 'Q&A Explainer',
    desc_he: 'עונה ישירות מתוך החומר',
    desc_en: 'Direct answers from the curriculum',
  },
  {
    emoji: '🏋️',
    name_he: 'מאמן',
    name_en: 'Coach',
    desc_he: 'תרגול יומי ועיון בחולשות',
    desc_en: 'Daily drills targeting your weak spots',
  },
  {
    emoji: '🧭',
    name_he: 'מנטור',
    name_en: 'Mentor',
    desc_he: 'מוטיבציה, הרגלים ותכנון',
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
  const title = isHe ? 'הכירו את הצוות שלכם' : 'Meet Your Learning Team';
  const gotIt = isHe ? 'הבנתי' : 'Got it';

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
            ? 'כל סוכן מיועד לצורך שונה — בחר את הנכון לך.'
            : 'Each agent serves a different purpose — pick the right one for your goal.'}
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