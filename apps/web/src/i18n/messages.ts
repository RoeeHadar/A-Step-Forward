import type { Locale } from './config';

const messages = {
  en: {
    nav: { home: 'Home', dashboard: 'Dashboard', chat: 'Chat', lessons: 'Lessons', memory: 'Memory', progress: 'Progress', educator: 'Educator', admin: 'Admin', signIn: 'Sign in', signUp: 'Get started' },
    landing: {
      hero: 'Your learning, only smarter',
      subtitle: 'A Step Forward is an AI-native learning center where Tutor, Mentor, Coach, and Reviewer teach, assess, and grow with every learner.',
      cta: 'Start learning →',
      featuresHeading: 'Meet your AI team',
      closingHeading: 'Ready to take a step forward?',
      closingSubtitle: 'Join learners who study with AI agents that remember, adapt, and grow with them.',
      features: {
        tutor: 'Tutor', tutorDesc: 'Socratic lessons that adapt to your pace and level.',
        mentor: 'Mentor', mentorDesc: 'Goals, motivation, and habits for the long run.',
        coach: 'Coach', coachDesc: 'Drills and spaced repetition to lock in mastery.',
        reviewer: 'Reviewer', reviewerDesc: 'Thoughtful feedback on code, essays, and solutions.',
      },
    },
    dashboard: { welcome: 'Welcome back', recentLessons: 'Recent lessons', mastery: 'Mastery summary', agents: 'Your agents' },
    common: { back: 'Back', language: 'Language', selectLanguage: 'Select language', toggleTheme: 'Toggle theme', appNavigation: 'App navigation', mainNavigation: 'Main' },
  },
  he: {
    nav: { home: 'בית', dashboard: 'לוח בקרה', chat: 'צ׳אט', lessons: 'שיעורים', memory: 'זיכרון', progress: 'התקדמות', educator: 'מחנך', admin: 'ניהול', signIn: 'התחברות', signUp: 'התחל' },
    landing: {
      hero: 'הלמידה שלך, רק חכמה יותר',
      subtitle: 'צעד קדימה הוא מרכז למידה מבוסס AI — מורה, מנטור, מאמן ומבקר שמלמדים, מעריכים ומתפתחים איתך.',
      cta: 'התחל ללמוד →',
      featuresHeading: 'הכירו את צוות ה-AI שלכם',
      closingHeading: 'מוכנים לצעד קדימה?',
      closingSubtitle: 'הצטרפו ללומדים שלומדים עם סוכני AI שזוכרים, מתאימים את עצמם וגדלים איתכם.',
      features: {
        tutor: 'מורה', tutorDesc: 'שיעורים סוקרטיים שמתאימים את עצמם לקצב ולרמה שלך.',
        mentor: 'מנטור', mentorDesc: 'מטרות, מוטיבציה והרגלים לטווח הארוך.',
        coach: 'מאמן', coachDesc: 'תרגילים וחזרה מרווחת לשליטה אמיתית.',
        reviewer: 'מבקר', reviewerDesc: 'משוב מעמיק על קוד, חיבורים ופתרונות.',
      },
    },
    dashboard: { welcome: 'ברוך שובך', recentLessons: 'שיעורים אחרונים', mastery: 'סיכום שליטה', agents: 'הסוכנים שלך' },
    common: { back: 'חזרה', language: 'שפה', selectLanguage: 'בחר שפה', toggleTheme: 'החלפת ערכת נושא', appNavigation: 'ניווט באפליקציה', mainNavigation: 'ראשי' },
  },
} as const;

export type Messages = (typeof messages)['en'];

export function getMessages(locale: Locale): Messages {
  return (messages[locale] ?? messages.en) as unknown as Messages;
}
