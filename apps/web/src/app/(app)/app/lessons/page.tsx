'use client';

/**
 * /app/lessons — "video lectures coming soon" placeholder.
 *
 * The lessons section has been hidden from the sidebar; this route is kept
 * alive so any stale deep links land somewhere sensible (instead of a 404)
 * and so the user understands what's planned for this surface in the future.
 *
 * Today, practice happens through the AI-generated Quiz builder at /app/quiz
 * and through chat with the Tutor agent.
 */
import Link from 'next/link';
import { Button } from '@asf/ui/button';
import { useI18n } from '@/providers/i18n-provider';

const STR = {
  he: {
    eyebrow: 'בקרוב',
    title: 'הרצאות וידאו של מורים נמצאות בפיתוח',
    blurb:
      'בעתיד, הסעיף הזה יכיל הרצאות וידאו של מורים מובילים, מסודרות לפי קטגוריה ונושא. נכון לעכשיו, האזור הזה ריק — אנחנו בונים אותו.',
    bullet1: 'הרצאות וידאו לכל נושא במתמטיקה ופיזיקה',
    bullet2: 'תרגול אינטראקטיבי שמותאם להרצאה',
    bullet3: 'סימוני זמן וקפיצה לרגעי מפתח',
    blurb2: 'בינתיים, אפשר לתרגל בעזרת ה-AI:',
    cta_quiz: 'בנה מבחן מותאם אישית',
    cta_chat: 'דבר עם המורה',
  },
  en: {
    eyebrow: 'Coming soon',
    title: 'Video lectures are in the works',
    blurb:
      'In the future, this section will host video lectures from leading teachers, organised by category and topic. For now this area is intentionally empty — we are building it.',
    bullet1: 'Video lectures for every math and physics topic',
    bullet2: 'Interactive practice synced to the lecture',
    bullet3: 'Timestamps and jump-to key moments',
    blurb2: 'In the meantime, practice with the AI:',
    cta_quiz: 'Build a custom quiz',
    cta_chat: 'Chat with the Tutor',
  },
} as const;

export default function LessonsComingSoonPage() {
  const { locale } = useI18n();
  const lang = locale === 'he' ? 'he' : 'en';
  const t = STR[lang];
  const isHe = lang === 'he';
  return (
    <div className="mx-auto max-w-2xl" dir={isHe ? 'rtl' : 'ltr'}>
      <div className="card-punch rounded-2xl p-8">
        <p className="text-xs font-medium uppercase tracking-wider text-primary">
          {t.eyebrow}
        </p>
        <h1 className="mt-2 font-display text-3xl font-bold">{t.title}</h1>
        <p className="mt-3 text-muted-foreground">{t.blurb}</p>
        <ul className="mt-4 list-disc space-y-1 ps-5 text-sm text-muted-foreground">
          <li>{t.bullet1}</li>
          <li>{t.bullet2}</li>
          <li>{t.bullet3}</li>
        </ul>
        <p className="mt-6 text-muted-foreground">{t.blurb2}</p>
        <div className="mt-3 flex flex-wrap gap-3">
          <Button asChild>
            <Link href="/app/quiz">{t.cta_quiz}</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/app/chat/tutor">{t.cta_chat}</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
