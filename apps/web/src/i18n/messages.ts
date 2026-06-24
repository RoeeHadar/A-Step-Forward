import type { Locale } from './config';

const messages = {
  en: {
    nav: {
      home: 'Home',
      dashboard: 'Dashboard',
      chat: 'Chat',
      lessons: 'Lessons',
      memory: 'Memory',
      progress: 'Progress',
      educator: 'Educator',
      admin: 'Admin',
      signIn: 'Sign in',
      signUp: 'Get started',
    },
    landing: {
      hero: 'Learn with AI agents that remember you',
      subtitle:
        'A Step Forward is an AI-native learning center where personalized tutors, coaches, and mentors teach, assess, and evolve with every learner.',
      cta: 'Start learning',
      features: {
        memory: 'Persistent memory',
        memoryDesc: 'Agents remember your preferences, progress, and struggles across sessions.',
        adaptive: 'Adaptive curriculum',
        adaptiveDesc: 'Personalized paths with spaced repetition for lasting retention.',
        multi: 'Multi-agent team',
        multiDesc: 'Tutor, Coach, Mentor, and more — each specialized for your goals.',
      },
    },
    dashboard: {
      welcome: 'Welcome back',
      recentLessons: 'Recent lessons',
      mastery: 'Mastery summary',
      agents: 'Your agents',
    },
  },
  he: {
    nav: {
      home: 'בית',
      dashboard: 'לוח בקרה',
      chat: 'צ׳אט',
      lessons: 'שיעורים',
      memory: 'זיכרון',
      progress: 'התקדמות',
      educator: 'מחנך',
      admin: 'ניהול',
      signIn: 'התחברות',
      signUp: 'התחל',
    },
    landing: {
      hero: 'למד עם סוכני AI שזוכרים אותך',
      subtitle:
        'צעד קדימה הוא מרכז למידה מבוסס AI שבו מורים, מאמנים ומנטורים מותאמים אישית מלמדים, מעריכים ומתפתחים עם כל לומד.',
      cta: 'התחל ללמוד',
      features: {
        memory: 'זיכרון מתמשך',
        memoryDesc: 'סוכנים זוכרים את ההעדפות, ההתקדמות והקשיים שלך בין מפגשים.',
        adaptive: 'תוכנית לימודים מותאמת',
        adaptiveDesc: 'מסלולים מותאמים אישית עם חזרה מרווחת לשימור לטווח ארוך.',
        multi: 'צוות רב-סוכנים',
        multiDesc: 'מורה, מאמן, מנטור ועוד — כל אחד מתמחה במטרות שלך.',
      },
    },
    dashboard: {
      welcome: 'ברוך שובך',
      recentLessons: 'שיעורים אחרונים',
      mastery: 'סיכום שליטה',
      agents: 'הסוכנים שלך',
    },
  },
} as const;

export type Messages = (typeof messages)['en'];

export function getMessages(locale: Locale): Messages {
  // Both locales share the same key structure; Hebrew literal values don't
  // satisfy the English literal types, so we cast through unknown.
  return (messages[locale] ?? messages.en) as unknown as Messages;
}
