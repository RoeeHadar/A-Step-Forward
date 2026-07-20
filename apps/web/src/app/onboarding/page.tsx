'use client';

/**
 * Onboarding questionnaire — fully bilingual + theme-aware.
 *
 * Before this rewrite, every label and prompt was a hardcoded English
 * string literal, and the root div used `bg-neutral-950 text-white` with
 * `border-white/10` / `text-white/50` utilities, so:
 *   - The site-header EN/עב toggle had no effect on this page.
 *   - The site-header sun/moon theme toggle had no effect on this page.
 *
 * The fix is purely surface-level (no behaviour changes):
 *   1. A local bilingual STR map covers every visible string.
 *   2. Locale + direction come from `useI18n()`, which is the same context
 *      the header toggles, so flipping EN/עב in the header now updates this
 *      page live.
 *   3. Every hardcoded dark token is replaced with the semantic
 *      `bg-background` / `text-foreground` / `text-muted-foreground` /
 *      `border-border` / `bg-card` / `bg-muted` tokens. Those tokens
 *      switch automatically when the user clicks the sun/moon in the
 *      header (see `providers/theme-provider.tsx`).
 *
 * Canonical option values (Goal / Subject / Style / etc.) stay English so
 * the database remains consistent across learners; only the displayed
 * labels are localised.
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { FieldLabel } from '@/components/field-hint';
import { useI18n } from '@/providers/i18n-provider';
import { cn } from '@asf/ui';
import {
  clearOnboardingDraft,
  loadOnboardingDraft,
  saveOnboardingDraft,
} from '@/lib/onboarding-draft';
import {
  filterAdultGoals,
  filterGoalsForLearner,
  HS_BAGRUT_GRADES,
  needsUniversityPicker,
  subjectLabel,
  yearsGapLabelForSubject,
  type OnboardingGoal,
  type OnboardingSubject,
} from '@/lib/onboarding-options';

// ── Types ────────────────────────────────────────────────────────────────────

type Goal =
  | 'bagrut_math_5'
  | 'bagrut_math_4'
  | 'bagrut_math_3'
  | 'bagrut_physics'
  | 'calculus1'
  | 'linear_algebra'
  | 'university_prep'
  | 'other';


type Subject = OnboardingSubject;
type Style = 'theory_first' | 'practice_first' | 'mixed' | 'unknown';
type TutorMode = 'direct' | 'socratic';

interface Step1 {
  goal: Goal | '';
  goalOther: string;
  gradeLevel: string;
  pointsGroup: string;
  targetUniversity: string;
  adultGoal: string;
  yearsGapBySubject: Partial<Record<Subject, string>>;
  subjects: Subject[];
  nextTestName: string;
  nextTestDate: string;
  finalGoalDate: string;
}

type TeacherOverall =
  | 'mostly_good'
  | 'mixed'
  | 'mostly_bad'
  | 'unknown'
  | 'no_teacher';

type SubjectExperienceMode = 'share' | 'no_prior' | 'prefer_skip';

interface SubjectPastExperience {
  mode: SubjectExperienceMode;
  selfRating: number;
  teacherOverall: TeacherOverall;
  teacherNotes: string;
}

interface Step2 {
  hoursAuto: boolean;
  hoursPerWeek: number;
  subjectExperience: Partial<Record<Subject, SubjectPastExperience>>;
  style: Style;
  attentionSpan: number | null;
}

interface Step3 {
  motivation: number;
  anxiety: number;
  confidence: number;
  preferredTime: 'morning' | 'afternoon' | 'evening' | 'night';
  hasQuietSpace: boolean;
  supportSystem: 'strong' | 'some' | 'none';
  whyThisGoal: string;
}

interface Step4 {
  selfScores: Record<string, number>;
}

// ── Bilingual labels ─────────────────────────────────────────────────────────

const STR = {
  en: {
    stepOf: 'Step {i} of {n}',
    s0_title: 'What are you working towards?',
    s0_sub:
      'We will use your next test date and final goal date to pace your weekly plan.',
    s0_goal: 'Learning goal',
    s0_goalOtherPh: 'Describe your goal…',
    s0_subjects: 'Subjects',
    s0_subj_math: 'Math',
    s0_subj_physics: 'Physics',
    s0_grade: 'Grade level',
    s0_adultGoal: 'What is your goal?',
    s0_yearsGap: 'How long since you last studied math?',
    s0_yearsGap_lt1: 'Less than a year',
    s0_yearsGap_1_3: '1–3 years',
    s0_yearsGap_gt3: 'More than 3 years',
    s0_units: 'Math units (Bagrut)',
    s0_unitsHint: 'Only for high-school students taking Bagrut math.',
    s0_university: 'Target university / program',
    s0_universityHint:
      'Different universities use different syllabi and prerequisites. We tailor your path accordingly.',
    s0_timeline: 'Timeline',
    s0_nextTestName: 'Next big event / test',
    s0_nextTestNamePh: 'e.g. school midterm, mock Bagrut, semester final',
    s0_nextTestDate: 'Date of next event',
    s0_finalGoalDate: 'Final goal date',
    s0_timelineHint: 'Optional — leave blank if you do not have a specific deadline yet.',
    s0_missingPrefix: 'To continue:',
    s0_missingYearsGap: 'Time since last studied ({subject})',
    s1_title: 'Tell us about yourself',
    s1_sub: 'This calibrates your plan difficulty and pacing.',
    s1_hours: 'Weekly study time (optional)',
    s1_hoursHint:
      'If you skip this, we estimate hours from your goal and deadline so the plan stays reachable.',
    s1_hoursAuto: 'Let the system estimate from my goal',
    s1_hoursUnit: 'hrs/week',
    s1_pastExperience: 'How has your learning experience been in {subject}?',
    s1_pastExperienceHint:
      'Rate classes, tutors, and self-study for this subject — skip if you prefer not to say.',
    s1_exp_share: 'I have prior experience',
    s1_exp_none: 'No prior experience',
    s1_exp_skip: 'Prefer not to answer',
    s1_teacherOverall: 'How were your {subject} teachers overall?',
    s1_teacher_good: 'Mostly helpful',
    s1_teacher_mixed: 'Mixed',
    s1_teacher_bad: 'Mostly unhelpful',
    s1_teacher_unknown: 'Hard to say',
    s1_teacher_none: 'No regular teacher',
    s1_teacherNotes:
      'What worked or did not work with past {subject} teachers? (optional)',
    s1_teacherNotesPh:
      'e.g. moved too fast, great at examples, never explained the why…',
    s1_style: 'Preferred learning style',
    s1_style_theory: 'Theory first',
    s1_style_practice: 'Practice first',
    s1_style_mixed: 'Mixed',
    s1_style_unknown: "I don't know yet",
    s1_attention: 'How long can you focus in one sitting?',
    s1_attention_unknown: "I don't know yet",
    s1_attention_20: '20 min',
    s1_attention_45: '45 min',
    s1_attention_90: '90 min',
    s2_title: 'How are you feeling about this?',
    s2_sub:
      'We tailor tone, frequency, and check-ins based on this. Be honest.',
    s2_motivation: 'How motivated do you feel right now?',
    s2_anxiety: 'How much test anxiety do you usually feel?',
    s2_anxietyHint:
      '1 = none, 10 = a lot. Affects how the AI talks to you about quizzes.',
    s2_anxietyConsent:
      'Self-reported stress helps us adjust study pacing and topic order — not a diagnosis, and not shared with third parties.',
    s2_confidence:
      'How confident do you feel in your ability to reach your goal?',
    s2_when: 'When do you study best?',
    s2_whenHint:
      'The Tutor may suggest light review in your peak window and heavier practice later in the day.',
    s2_when_morning: 'Morning',
    s2_when_afternoon: 'Afternoon',
    s2_when_evening: 'Evening',
    s2_when_night: 'Night',
    s2_quiet: 'Do you have a quiet study space?',
    s2_yes: 'Yes',
    s2_no: 'No',
    s2_support: 'Support system',
    s2_supportHint:
      'Family, friends, or mentors who help you stay on track with school — not technical IT support.',
    s2_support_strong: 'Strong',
    s2_support_some: 'Some',
    s2_support_none: 'None',
    s2_why: 'In your own words: why does this goal matter to you? (optional)',
    s2_whyPh:
      'e.g. I want to qualify for engineering, prove to myself I can, get into a specific program…',
    s3_title: 'Rate your understanding',
    s3_sub:
      'Rate building-block topics from your path — be honest; the diagnostic will refine this.',
    s3_scale_low: '1 — never studied',
    s3_scale_high: '10 — exam-ready',
    s4_title: 'How do you prefer to learn with the Tutor?',
    s4_sub:
      'Pick the style that feels most comfortable. You can change this later in settings.',
    s4_direct: 'Explain it to me directly',
    s4_socratic: 'Guide me with questions (Socratic)',
    next: 'Next',
    back: 'Back',
    saving: 'Creating your plan…',
    createPlan: 'Create my learning plan',
    errorGeneric: 'Something went wrong',
    errorNoPlan: 'Your profile was saved but the plan could not be created. Try again.',
  },
  he: {
    stepOf: 'שלב {i} מתוך {n}',
    s0_title: 'לקראת מה את/ה לומד/ת?',
    s0_sub:
      'נשתמש בתאריך המבחן הבא ובתאריך היעד הסופי כדי לקבוע את הקצב השבועי שלך.',
    s0_goal: 'מטרת למידה',
    s0_goalOtherPh: 'תאר/י את המטרה שלך…',
    s0_subjects: 'מקצועות',
    s0_subj_math: 'מתמטיקה',
    s0_subj_physics: 'פיזיקה',
    s0_grade: 'כיתה / שכבה',
    s0_adultGoal: 'מה המטרה שלך?',
    s0_yearsGap: 'כמה זמן עבר מאז שלמדת מתמטיקה?',
    s0_yearsGap_lt1: 'פחות משנה',
    s0_yearsGap_1_3: '1–3 שנים',
    s0_yearsGap_gt3: 'יותר מ-3 שנים',
    s0_units: 'יחידות במתמטיקה (בגרות)',
    s0_unitsHint: 'רק לתלמידי תיכון שנבחנים בבגרות במתמטיקה.',
    s0_university: 'אוניברסיטה / מסלול יעד',
    s0_universityHint:
      'לכל מוסד לימודים סילabus ודרישות קדם שונים — נתאים את המסלול בהתאם.',
    s0_timeline: 'לוח זמנים',
    s0_nextTestName: 'אירוע או מבחן קרוב',
    s0_nextTestNamePh: 'למשל: מבחן בית-ספרי, בגרות מתכונת, בוחן סוף סמסטר',
    s0_nextTestDate: 'תאריך האירוע הבא',
    s0_finalGoalDate: 'תאריך היעד הסופי',
    s0_timelineHint:
      'לא חובה — אפשר להשאיר ריק אם אין תאריך יעד ספציפי כרגע.',
    s0_missingPrefix: 'כדי להמשיך:',
    s0_missingYearsGap: 'זמן מאז למידה ({subject})',
    s1_title: 'ספר/י לנו על עצמך',
    s1_sub: 'זה מכייל את רמת הקושי והקצב של התוכנית שלך.',
    s1_hours: 'זמן לימוד שבועי (לא חובה)',
    s1_hoursHint:
      'אם תדלג/י, נעריך שעות לפי המטרה והדד-ליין כדי שהתוכנית תישאר ברת-השגה.',
    s1_hoursAuto: 'תנו למערכת להעריך לפי המטרה שלי',
    s1_hoursUnit: 'שעות בשבוע',
    s1_pastExperience: 'איך הייתה חוויית הלמידה שלך ב{subject}?',
    s1_pastExperienceHint:
      'דרג/י שיעורים, מורים פרטיים ולמידה עצמית במקצוע הזה — אפשר לדלג אם לא רוצים לענות.',
    s1_exp_share: 'יש לי ניסיון קודם',
    s1_exp_none: 'אין לי ניסיון קודם',
    s1_exp_skip: 'מעדיף/ה לא לענות',
    s1_teacherOverall: 'איך היו המורים שלך ב{subject} בכלל?',
    s1_teacher_good: 'בעיקר עזרו',
    s1_teacher_mixed: 'מעורב',
    s1_teacher_bad: 'בעיקר לא עזרו',
    s1_teacher_unknown: 'קשה לומר',
    s1_teacher_none: 'לא היה מורה קבוע',
    s1_teacherNotes: 'מה עבד או לא עבד עם מורים ב{subject}? (לא חובה)',
    s1_teacherNotesPh:
      'למשל: התקדמו מהר מדי, דוגמאות מצוינות, לא הסבירו את ה״למה״…',
    s1_style: 'סגנון למידה מועדף',
    s1_style_theory: 'קודם תיאוריה',
    s1_style_practice: 'קודם תרגול',
    s1_style_mixed: 'מעורב',
    s1_style_unknown: 'עדיין לא יודע/ת',
    s1_attention: 'כמה זמן את/ה מצליח/ה להתרכז ברצף?',
    s1_attention_unknown: 'עדיין לא יודע/ת',
    s1_attention_20: '20 דק׳',
    s1_attention_45: '45 דק׳',
    s1_attention_90: '90 דק׳',
    s2_title: 'איך את/ה מרגיש/ה לגבי זה?',
    s2_sub:
      'אנחנו מתאימים את הטון, התדירות ונקודות הבדיקה לפי זה. בכנות.',
    s2_motivation: 'עד כמה את/ה מרגיש/ה מוטיבציה כרגע?',
    s2_anxiety: 'כמה חרדת מבחנים את/ה בדרך כלל מרגיש/ה?',
    s2_anxietyHint:
      '1 = בכלל לא, 10 = מאוד. משפיע על איך ה-AI מדבר איתך על מבחנים.',
    s2_anxietyConsent:
      'רמת הלחץ שתדווח/י עוזרת לנו להתאים קצב וסדר נושאים — לא אבחון, ולא משותף עם צד שלישי.',
    s2_confidence: 'עד כמה את/ה מאמין/ה ביכולת שלך להגיע ליעד?',
    s2_when: 'מתי את/ה הכי טוב/ה ללמוד?',
    s2_whenHint:
      'המורה יכול להציע סקירה קלה בשעות השיא שלך ותרגול ממוקד יותר מאוחר ביום.',
    s2_when_morning: 'בוקר',
    s2_when_afternoon: 'צהריים',
    s2_when_evening: 'ערב',
    s2_when_night: 'לילה',
    s2_quiet: 'יש לך מקום שקט ללימוד?',
    s2_yes: 'כן',
    s2_no: 'לא',
    s2_support: 'מערכת תמיכה',
    s2_supportHint:
      'משפחה, חברים או מנטורים שעוזרים לך להתמיד — לא תמיכה טכנית של המערכת.',
    s2_support_strong: 'חזקה',
    s2_support_some: 'בינונית',
    s2_support_none: 'אין',
    s2_why: 'במילים שלך: למה המטרה הזו חשובה לך? (לא חובה)',
    s2_whyPh:
      'למשל: אני רוצה להתקבל להנדסה, להוכיח לעצמי שאני יכול/ה, להיכנס לתוכנית מסוימת…',
    s3_title: 'דרג/י את ההבנה שלך',
    s3_sub:
      'דרג/י נושאי יסוד מהמסלול שלך — בכנות; האבחון ידייק את זה.',
    s3_scale_low: '1 — לא למדתי',
    s3_scale_high: '10 — מוכן/ה לבחינה',
    s4_title: 'כיצד אתה מעדיף ללמוד עם המורה?',
    s4_sub: 'בחר/י את הסגנון שהכי נוח לך. אפשר לשנות את זה בהמשך בהגדרות.',
    s4_direct: 'הסבר לי ישירות',
    s4_socratic: 'הנחה אותי עם שאלות (סוקרטי)',
    next: 'הבא',
    back: 'חזרה',
    saving: 'יוצרים את התוכנית…',
    createPlan: 'צור/י את תוכנית הלמידה',
    errorGeneric: 'משהו השתבש',
    errorNoPlan: 'הפרופיל נשמר אבל לא הצלחנו ליצור תוכנית. נסה/י שוב.',
  },
} as const;

type Lang = 'en' | 'he';

function tx(s: string, params: Record<string, string | number>): string {
  return Object.entries(params).reduce(
    (acc, [k, v]) => acc.replaceAll(`{${k}}`, String(v)),
    s,
  );
}

// ── Constants (canonical English values + bilingual labels) ──────────────────

const GOALS: { value: Goal; label_en: string; label_he: string }[] = [
  {
    value: 'bagrut_math_5',
    label_en: 'Pass Bagrut — Math 5pt',
    label_he: 'בגרות במתמטיקה — 5 יח׳',
  },
  {
    value: 'bagrut_math_4',
    label_en: 'Pass Bagrut — Math 4pt',
    label_he: 'בגרות במתמטיקה — 4 יח׳',
  },
  {
    value: 'bagrut_math_3',
    label_en: 'Pass Bagrut — Math 3pt',
    label_he: 'בגרות במתמטיקה — 3 יח׳',
  },
  {
    value: 'bagrut_physics',
    label_en: 'Pass Bagrut — Physics',
    label_he: 'בגרות בפיזיקה',
  },
  {
    value: 'calculus1',
    label_en: 'University — Calculus 1',
    label_he: 'אוניברסיטה — חדו״א 1',
  },
  {
    value: 'linear_algebra',
    label_en: 'University — Linear Algebra',
    label_he: 'אוניברסיטה — אלגברה לינארית',
  },
  {
    value: 'university_prep',
    label_en: 'General university preparation',
    label_he: 'הכנה כללית לאוניברסיטה',
  },
  {
    value: 'other',
    label_en: 'Other goal (specify below)',
    label_he: 'מטרה אחרת (פרט/י למטה)',
  },
];

const GRADE_LEVELS: { value: string; label_en: string; label_he: string }[] = [
  {
    value: 'adult_learner',
    label_en: 'College student or adult learner',
    label_he: 'סטודנט/י או בוגר/ת תיכון',
  },
  { value: '10', label_en: '10th grade', label_he: 'כיתה י׳' },
  { value: '11', label_en: '11th grade', label_he: 'כיתה י״א' },
  { value: '12', label_en: '12th grade', label_he: 'כיתה י״ב' },
  {
    value: 'adult_bagrut',
    label_en: 'External Bagrut / Adult Learner',
    label_he: 'בגרות חיצונית / בוגרים',
  },
  {
    value: 'pre_university',
    label_en: 'Pre-university (Mechina / prep year)',
    label_he: 'מכינה / הכנה לאוניברסיטה',
  },
  {
    value: 'university_1',
    label_en: 'University — 1st year',
    label_he: 'אוניברסיטה — שנה א׳',
  },
  {
    value: 'university_2plus',
    label_en: 'University — 2nd year+',
    label_he: 'אוניברסיטה — שנה ב׳+',
  },
];

const UNIVERSITIES: { value: string; label_en: string; label_he: string }[] = [
  { value: 'technion', label_en: 'Technion (IIT)', label_he: 'הטכניון' },
  { value: 'huji', label_en: 'Hebrew University', label_he: 'האוניברסיטה העברית' },
  { value: 'tau', label_en: 'Tel Aviv University', label_he: 'אוניברסיטת תל אביב' },
  { value: 'biu', label_en: 'Bar-Ilan University', label_he: 'בר-אילן' },
  { value: 'bgu', label_en: 'Ben-Gurion University', label_he: 'בן-גוריון' },
  { value: 'haifa', label_en: 'University of Haifa', label_he: 'אוניברסיטת חיפה' },
  { value: 'other', label_en: 'Other / not sure yet', label_he: 'אחר / עדיין לא יודע/ת' },
];

const DEFAULT_SUBJECT_EXPERIENCE = (): SubjectPastExperience => ({
  mode: 'share',
  selfRating: 5,
  teacherOverall: 'mixed',
  teacherNotes: '',
});

function emptySubjectExperience(): Partial<Record<Subject, SubjectPastExperience>> {
  return {};
}

const ADULT_GOALS: { value: string; label_en: string; label_he: string }[] = [
  { value: 'bagrut_math', label_en: 'Bagrut in Mathematics', label_he: 'בגרות במתמטיקה' },
  { value: 'bagrut_physics', label_en: 'Bagrut in Physics', label_he: 'בגרות בפיזיקה' },
  {
    value: 'university_math',
    label_en: 'University math course',
    label_he: 'קורס מתמטיקה באוניברסיטה',
  },
  {
    value: 'university_physics',
    label_en: 'University physics course',
    label_he: 'קורס פיזיקה באוניברסיטה',
  },
  { value: 'general_improvement', label_en: 'General improvement', label_he: 'שיפור כללי' },
];

const YEARS_GAP_OPTIONS: { value: string; label_en: string; label_he: string }[] = [
  { value: 'less_than_1_year', label_en: 'Less than a year', label_he: 'פחות משנה' },
  { value: '1_3_years', label_en: '1–3 years', label_he: '1–3 שנים' },
  { value: 'more_than_3_years', label_en: 'More than 3 years', label_he: 'יותר מ-3 שנים' },
];

const POINTS_GROUPS: { value: string; label_en: string; label_he: string }[] = [
  { value: '3', label_en: '3 units', label_he: '3 יחידות' },
  { value: '4', label_en: '4 units', label_he: '4 יחידות' },
  { value: '5', label_en: '5 units', label_he: '5 יחידות' },
];

// ── Step components ──────────────────────────────────────────────────────────

function StepIndicator({
  current,
  total,
  lang,
  t,
  dir,
}: {
  current: number;
  total: number;
  lang: Lang;
  t: (typeof STR)[Lang];
  dir: 'rtl' | 'ltr';
}) {
  return (
    <div className="mb-8 flex items-center gap-2" dir={dir}>
      {Array.from({ length: total }, (_, i) => (
        <div key={i} className="flex items-center gap-2">
          <div
            className={cn(
              'h-2.5 w-2.5 rounded-full transition-all',
              i < current
                ? 'bg-accent-cyan'
                : i === current
                  ? 'w-5 bg-accent-cyan ring-2 ring-accent-cyan/30'
                  : 'bg-muted-foreground/30',
            )}
          />
          {i < total - 1 && (
            <div
              className={cn(
                'h-px w-8',
                i < current ? 'bg-accent-cyan' : 'bg-muted-foreground/30',
              )}
            />
          )}
        </div>
      ))}
      <span className={cn('text-sm text-muted-foreground', lang === 'he' ? 'mr-2' : 'ml-2')}>
        {tx(t.stepOf, { i: current + 1, n: total })}
      </span>
    </div>
  );
}

function SliderField({
  label,
  min,
  max,
  step = 1,
  value,
  onChange,
  displayValue,
  hint,
}: {
  label: string;
  min: number;
  max: number;
  step?: number;
  value: number;
  onChange: (v: number) => void;
  displayValue?: string;
  hint?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-semibold text-accent-cyan">{displayValue ?? value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer accent-cyan-400"
        aria-label={label}
      />
      <div className="flex justify-between text-xs text-muted-foreground/60">
        <span>{min}</span>
        <span>{max}</span>
      </div>
      {hint && <p className="text-xs text-muted-foreground/70">{hint}</p>}
    </div>
  );
}

// Shared button style helpers — both rely on theme tokens so they
// repaint correctly when the user toggles light/dark in the header.
const OPTION_BTN =
  'w-full text-start px-4 py-2.5 rounded-lg border text-sm transition-colors';
const optionBtnCls = (selected: boolean) =>
  cn(
    OPTION_BTN,
    selected
      ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
      : 'border-border bg-card text-muted-foreground hover:border-border-bright hover:text-foreground',
  );
const inputCls =
  'w-full rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground focus:border-accent-cyan focus:outline-none';
const primaryBtnCls =
  'w-full rounded-xl bg-accent-cyan py-3 text-sm font-semibold text-neutral-950 transition-colors hover:bg-cyan-300 disabled:opacity-40';
const secondaryBtnCls =
  'flex-1 rounded-xl border border-border py-3 text-sm text-muted-foreground transition-colors hover:border-border-bright hover:text-foreground';

function getStep0MissingFields(input: {
  s1: Step1;
  isAdultLearner: boolean;
  needsPointsGroup: boolean;
  needsUniversity: boolean;
  lang: Lang;
  t: (typeof STR)[Lang];
}): string[] {
  const { s1, isAdultLearner, needsPointsGroup, needsUniversity, lang, t } = input;
  const missing: string[] = [];

  if (s1.subjects.length === 0) missing.push(t.s0_subjects);
  if (!s1.gradeLevel) missing.push(t.s0_grade);
  if (needsPointsGroup && !s1.pointsGroup) missing.push(t.s0_units);
  if (needsUniversity && !s1.targetUniversity) missing.push(t.s0_university);

  if (isAdultLearner) {
    if (!s1.adultGoal) missing.push(t.s0_adultGoal);
    for (const sub of s1.subjects) {
      if (!s1.yearsGapBySubject[sub]) {
        missing.push(tx(t.s0_missingYearsGap, { subject: subjectLabel(sub, lang) }));
      }
    }
  } else if (!s1.goal) {
    missing.push(t.s0_goal);
  }

  return missing;
}

// ── Main page ────────────────────────────────────────────────────────────────

export default function OnboardingPage() {
  const router = useRouter();
  const { locale, dir } = useI18n();
  const lang: Lang = locale === 'he' ? 'he' : 'en';
  const t = STR[lang];
  const goalLabel = (g: (typeof GOALS)[number]) =>
    lang === 'he' ? g.label_he : g.label_en;
  const gradeLabel = (g: (typeof GRADE_LEVELS)[number]) =>
    lang === 'he' ? g.label_he : g.label_en;

  const [step, setStep] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [draftLoaded, setDraftLoaded] = useState(false);

  const [s1, setS1] = useState<Step1>({
    goal: '',
    goalOther: '',
    gradeLevel: '',
    pointsGroup: '',
    targetUniversity: '',
    adultGoal: '',
    yearsGapBySubject: {},
    subjects: ['math'],
    nextTestName: '',
    nextTestDate: '',
    finalGoalDate: '',
  });

  const [s2, setS2] = useState<Step2>({
    hoursAuto: true,
    hoursPerWeek: 5,
    subjectExperience: emptySubjectExperience(),
    style: 'mixed',
    attentionSpan: 45,
  });

  const [s3, setS3] = useState<Step3>({
    motivation: 7,
    anxiety: 5,
    confidence: 5,
    preferredTime: 'evening',
    hasQuietSpace: true,
    supportSystem: 'some',
    whyThisGoal: '',
  });

  const [s4, setS4] = useState<Step4>({ selfScores: {} });
  const [tutorMode, setTutorMode] = useState<TutorMode>('direct');

  useEffect(() => {
    const draft = loadOnboardingDraft();
    if (draft) {
      setStep(draft.step);
      setS1((prev) => {
        const merged = { ...prev, ...(draft.s1 as Partial<Step1>) };
        const subjects = merged.subjects ?? prev.subjects;
        const allowedGoals = filterGoalsForLearner({
          gradeLevel: merged.gradeLevel,
          subjects,
        });
        const allowedAdult = filterAdultGoals(subjects);
        return {
          ...merged,
          goal: allowedGoals.includes(merged.goal as OnboardingGoal)
            ? merged.goal
            : '',
          adultGoal: allowedAdult.includes(
            merged.adultGoal as ReturnType<typeof filterAdultGoals>[number],
          )
            ? merged.adultGoal
            : '',
        };
      });
      setS2((prev) => ({ ...prev, ...(draft.s2 as Partial<Step2>) }));
      setS3((prev) => ({ ...prev, ...(draft.s3 as Partial<Step3>) }));
      setS4((prev) => ({ ...prev, ...(draft.s4 as Partial<Step4>) }));
      if (draft.tutorMode === 'direct' || draft.tutorMode === 'socratic') {
        setTutorMode(draft.tutorMode);
      }
    }
    setDraftLoaded(true);
  }, []);

  useEffect(() => {
    if (!draftLoaded) return;
    saveOnboardingDraft({
      step,
      s1: s1 as unknown as Record<string, unknown>,
      s2: s2 as unknown as Record<string, unknown>,
      s3: s3 as unknown as Record<string, unknown>,
      s4: s4 as unknown as Record<string, unknown>,
      tutorMode,
    });
  }, [step, s1, s2, s3, s4, tutorMode, draftLoaded]);

  useEffect(() => {
    if (!draftLoaded) return;
    setS2((prev) => {
      const subjectExperience = { ...prev.subjectExperience };
      let changed = false;
      for (const sub of s1.subjects) {
        if (!subjectExperience[sub]) {
          subjectExperience[sub] = DEFAULT_SUBJECT_EXPERIENCE();
          changed = true;
        }
      }
      for (const sub of Object.keys(subjectExperience) as Subject[]) {
        if (!s1.subjects.includes(sub)) {
          delete subjectExperience[sub];
          changed = true;
        }
      }
      return changed ? { ...prev, subjectExperience } : prev;
    });
  }, [s1.subjects, draftLoaded]);

  function toggleSubject(sub: Subject) {
    const isRemoving = s1.subjects.includes(sub);
    const nextSubjects = isRemoving
      ? s1.subjects.filter((s) => s !== sub)
      : [...s1.subjects, sub];

    setS1((prev) => {
      const yearsGapBySubject = { ...prev.yearsGapBySubject };
      if (isRemoving) delete yearsGapBySubject[sub];
      const allowedGoals = filterGoalsForLearner({
        gradeLevel: prev.gradeLevel,
        subjects: nextSubjects,
      });
      const goal = allowedGoals.includes(prev.goal as OnboardingGoal) ? prev.goal : '';
      const allowedAdult = filterAdultGoals(nextSubjects);
      const adultGoal = allowedAdult.includes(prev.adultGoal as ReturnType<typeof filterAdultGoals>[number])
        ? prev.adultGoal
        : '';
      return {
        ...prev,
        subjects: nextSubjects,
        yearsGapBySubject,
        goal,
        adultGoal,
      };
    });

    setS2((prev) => {
      const subjectExperience = { ...prev.subjectExperience };
      if (isRemoving) delete subjectExperience[sub];
      else subjectExperience[sub] = DEFAULT_SUBJECT_EXPERIENCE();
      return { ...prev, subjectExperience };
    });
  }

  function patchSubjectExperience(
    sub: Subject,
    patch: Partial<SubjectPastExperience>,
  ) {
    setS2((prev) => {
      const current = prev.subjectExperience[sub] ?? DEFAULT_SUBJECT_EXPERIENCE();
      return {
        ...prev,
        subjectExperience: {
          ...prev.subjectExperience,
          [sub]: { ...current, ...patch },
        },
      };
    });
  }

  const visibleGoalKeys = filterGoalsForLearner({
    gradeLevel: s1.gradeLevel,
    subjects: s1.subjects,
  });
  const visibleGoals = GOALS.filter((g) =>
    visibleGoalKeys.includes(g.value as OnboardingGoal),
  );
  const visibleAdultGoalKeys = filterAdultGoals(s1.subjects);
  const visibleAdultGoals = ADULT_GOALS.filter((g) =>
    visibleAdultGoalKeys.includes(g.value as (typeof visibleAdultGoalKeys)[number]),
  );

  const isAdultLearner = s1.gradeLevel === 'adult_learner';
  const needsPointsGroup =
    HS_BAGRUT_GRADES.has(s1.gradeLevel) && s1.subjects.includes('math');

  const needsUniversity = needsUniversityPicker({
    gradeLevel: s1.gradeLevel,
    isAdultLearner,
    adultGoal: s1.adultGoal,
  });

  const isPhysicsOnly =
    s1.subjects.includes('physics') && !s1.subjects.includes('math');

  const step0MissingFields = getStep0MissingFields({
    s1,
    isAdultLearner,
    needsPointsGroup,
    needsUniversity,
    lang,
    t,
  });
  const step0CanProceed = step0MissingFields.length === 0;

  function normalizePointsGroup(raw: string): string {
    if (raw === '3' || raw === '4' || raw === '5') return `${raw}pt`;
    return raw;
  }

  function resolvePointsGroupForSubmit(): string | null {
    if (isPhysicsOnly) return 'hs_physics';
    if (needsPointsGroup && s1.pointsGroup) {
      return normalizePointsGroup(s1.pointsGroup);
    }
    return null;
  }

  function formatSubjectExperienceSummary(): string {
    return s1.subjects
      .map((sub) => {
        const exp = s2.subjectExperience[sub] ?? DEFAULT_SUBJECT_EXPERIENCE();
        const name = subjectLabel(sub, 'en');
        if (exp.mode === 'prefer_skip') {
          return `${name}: learner prefers not to answer.`;
        }
        if (exp.mode === 'no_prior') {
          return `${name}: no prior experience.`;
        }
        const teacher = exp.teacherOverall.replace(/_/g, ' ');
        const notes = exp.teacherNotes.trim()
          ? ` Teacher notes: ${exp.teacherNotes.trim()}`
          : '';
        return `${name}: experience ${exp.selfRating}/10; teachers ${teacher}.${notes}`;
      })
      .join(' ');
  }

  function formatYearsGapSummary(): string {
    return s1.subjects
      .map((sub) => {
        const gap = s1.yearsGapBySubject[sub];
        if (!gap) return null;
        return `${subjectLabel(sub, 'en')}: ${gap.replace(/_/g, ' ')}`;
      })
      .filter(Boolean)
      .join('; ');
  }

  async function handleSubmit() {
    setSubmitting(true);
    setError('');
    try {
      // Backend stays canonical English so cross-learner aggregations work.
      const goalText = isAdultLearner
        ? (ADULT_GOALS.find((g) => g.value === s1.adultGoal)?.label_en ?? s1.adultGoal)
        : s1.goal === 'other'
          ? s1.goalOther
          : (GOALS.find((g) => g.value === s1.goal)?.label_en ?? s1.goal);
      const experienceSummary = formatSubjectExperienceSummary();
      const yearsGapSummary = formatYearsGapSummary();
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 25_000);
      let res: Response;
      try {
        res = await fetch('/api/onboarding/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: controller.signal,
          body: JSON.stringify({
            goal: goalText,
            grade_level: s1.gradeLevel,
            points_group: resolvePointsGroupForSubmit(),
            subjects: s1.subjects,
            hours_per_week: s2.hoursAuto ? 6 : s2.hoursPerWeek,
            preferred_style: s2.style === 'unknown' ? null : s2.style,
            attention_span: s2.attentionSpan,
            self_scores: {},
            background_notes: isAdultLearner
              ? `${experienceSummary}${yearsGapSummary ? ` Years since last study: ${yearsGapSummary}.` : ''}`
              : experienceSummary,
            next_test_name: s1.nextTestName || null,
            next_test_date: s1.nextTestDate || null,
            final_goal_date: s1.finalGoalDate || null,
            adult_learner: isAdultLearner,
            years_gap: isAdultLearner ? yearsGapSummary || null : null,
            mental_state: {
              motivation: s3.motivation,
              anxiety: s3.anxiety,
              confidence: s3.confidence,
              preferred_study_time: s3.preferredTime,
              has_quiet_space: s3.hasQuietSpace,
              support_system: s3.supportSystem,
              why_this_goal: s3.whyThisGoal,
              target_university: needsUniversity ? s1.targetUniversity || null : null,
            },
            personality_profile: {
              subject_experience: s2.subjectExperience,
              learning_style_unknown: s2.style === 'unknown',
              attention_span_min: s2.attentionSpan,
              attention_span_unknown: s2.attentionSpan == null,
              hours_per_week: s2.hoursAuto ? null : s2.hoursPerWeek,
              hours_per_week_auto: s2.hoursAuto,
              goal_key: isAdultLearner ? s1.adultGoal : s1.goal || null,
              target_university: needsUniversity ? s1.targetUniversity || null : null,
              years_gap_by_subject: isAdultLearner ? s1.yearsGapBySubject : null,
              ...(isAdultLearner
                ? {
                    adult_learner: true,
                    years_gap: yearsGapSummary || null,
                    adult_goal: s1.adultGoal,
                  }
                : {}),
            },
            tutor_mode: tutorMode,
          }),
        });
      } catch (err) {
        clearTimeout(timeout);
        // Client abort / network — profile may already be saved; finish plan on plan-setup.
        if (err instanceof Error && err.name === 'AbortError') {
          clearOnboardingDraft();
          router.push('/plan-setup');
          return;
        }
        throw err;
      } finally {
        clearTimeout(timeout);
      }
      if (!res.ok) {
        const errText = await res.text();
        let message = errText.trim() || `Request failed (${res.status})`;
        try {
          const body = JSON.parse(errText) as { error?: string };
          message = body.error ?? message;
        } catch {
          /* plain text */
        }
        throw new Error(message);
      }
      const data = (await res.json()) as { has_plan?: boolean; plan_id?: string };
      if (!data.has_plan) {
        clearOnboardingDraft();
        router.push('/plan-setup');
        return;
      }
      clearOnboardingDraft();
      router.push('/app');
    } catch (err) {
      setError(err instanceof Error ? err.message : t.errorGeneric);
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader />
      <main className="mx-auto max-w-xl px-4 py-12" dir={dir}>
        <StepIndicator current={step} total={4} lang={lang} t={t} dir={dir} />

        {/* ── Step 0: Goals + timeline ── */}
        {step === 0 && (
          <div className="space-y-6">
            <div>
              <h1 className="mb-1 text-2xl font-bold">{t.s0_title}</h1>
              <p className="text-sm text-muted-foreground">{t.s0_sub}</p>
            </div>

            <div className="space-y-2">
              <p className="mb-1 block text-sm text-muted-foreground">
                {t.s0_subjects}
              </p>
              <div className="flex flex-wrap gap-3">
                {(['math', 'physics'] as Subject[]).map((sub) => (
                  <button
                    key={sub}
                    type="button"
                    onClick={() => toggleSubject(sub)}
                    className={cn(
                      'flex-1 min-w-[7rem] rounded-lg border py-2.5 text-sm font-medium transition-colors',
                      s1.subjects.includes(sub)
                        ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
                        : 'border-border bg-card text-muted-foreground hover:border-border-bright hover:text-foreground',
                    )}
                  >
                    {sub === 'math' ? t.s0_subj_math : t.s0_subj_physics}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label
                  htmlFor="grade-level"
                  className="mb-1.5 block text-xs text-muted-foreground"
                >
                  {t.s0_grade}
                </label>
                <select
                  id="grade-level"
                  value={s1.gradeLevel}
                  onChange={(e) => {
                    const gradeLevel = e.target.value;
                    setS1((p) => {
                      const allowedGoals = filterGoalsForLearner({
                        gradeLevel,
                        subjects: p.subjects,
                      });
                      const goal = allowedGoals.includes(p.goal as OnboardingGoal)
                        ? p.goal
                        : '';
                      const allowedAdult = filterAdultGoals(p.subjects);
                      const adultGoal = allowedAdult.includes(
                        p.adultGoal as (typeof allowedAdult)[number],
                      )
                        ? p.adultGoal
                        : '';
                      const showUniversity = needsUniversityPicker({
                        gradeLevel,
                        isAdultLearner: gradeLevel === 'adult_learner',
                        adultGoal,
                      });
                      return {
                        ...p,
                        gradeLevel,
                        goal,
                        adultGoal,
                        targetUniversity: showUniversity ? p.targetUniversity : '',
                      };
                    });
                  }}
                  className={inputCls}
                  required
                >
                  <option value="" disabled>
                    {lang === 'he' ? 'בחר/י כיתה…' : 'Select grade…'}
                  </option>
                  {GRADE_LEVELS.map((g) => (
                    <option key={g.value} value={g.value}>
                      {gradeLabel(g)}
                    </option>
                  ))}
                </select>
              </div>
              {needsPointsGroup && (
                <div>
                  <FieldLabel hint={t.s0_unitsHint} className="mb-1.5 block text-xs">
                    {t.s0_units}
                  </FieldLabel>
                  <select
                    id="points-group"
                    value={s1.pointsGroup}
                    onChange={(e) =>
                      setS1((p) => ({ ...p, pointsGroup: e.target.value }))
                    }
                    className={inputCls}
                    required
                  >
                    <option value="" disabled>
                      {lang === 'he' ? 'בחר/י יחידות…' : 'Select units…'}
                    </option>
                    {POINTS_GROUPS.map((p) => (
                      <option key={p.value} value={p.value}>
                        {lang === 'he' ? p.label_he : p.label_en}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {!isAdultLearner && s1.gradeLevel ? (
              <div className="space-y-2">
                <p className="mb-1 block text-sm text-muted-foreground">{t.s0_goal}</p>
                {visibleGoals.map((g) => (
                  <button
                    key={g.value}
                    type="button"
                    onClick={() => setS1((p) => ({ ...p, goal: g.value }))}
                    className={optionBtnCls(s1.goal === g.value)}
                  >
                    {goalLabel(g)}
                  </button>
                ))}
                {s1.goal === 'other' && (
                  <input
                    type="text"
                    placeholder={t.s0_goalOtherPh}
                    value={s1.goalOther}
                    onChange={(e) =>
                      setS1((p) => ({ ...p, goalOther: e.target.value }))
                    }
                    className={inputCls}
                    dir="auto"
                  />
                )}
              </div>
            ) : null}

            {needsUniversity ? (
              <div>
                <FieldLabel hint={t.s0_universityHint} className="mb-1.5 block text-xs">
                  {t.s0_university}
                </FieldLabel>
                <select
                  id="target-university"
                  value={s1.targetUniversity}
                  onChange={(e) =>
                    setS1((p) => ({ ...p, targetUniversity: e.target.value }))
                  }
                  className={inputCls}
                  required
                >
                  <option value="" disabled>
                    {lang === 'he' ? 'בחר/י מוסד…' : 'Select institution…'}
                  </option>
                  {UNIVERSITIES.map((u) => (
                    <option key={u.value} value={u.value}>
                      {lang === 'he' ? u.label_he : u.label_en}
                    </option>
                  ))}
                </select>
              </div>
            ) : null}

            {isAdultLearner ? (
              <>
                <div className="space-y-2">
                  <p className="mb-1 block text-sm text-muted-foreground">{t.s0_adultGoal}</p>
                  {visibleAdultGoals.map((g) => (
                    <button
                      key={g.value}
                      type="button"
                      onClick={() =>
                        setS1((p) => {
                          const showUniversity = needsUniversityPicker({
                            gradeLevel: p.gradeLevel,
                            isAdultLearner: true,
                            adultGoal: g.value,
                          });
                          return {
                            ...p,
                            adultGoal: g.value,
                            targetUniversity: showUniversity ? p.targetUniversity : '',
                          };
                        })
                      }
                      className={optionBtnCls(s1.adultGoal === g.value)}
                    >
                      {lang === 'he' ? g.label_he : g.label_en}
                    </button>
                  ))}
                </div>
                {s1.subjects.map((sub) => (
                  <div key={sub} className="space-y-2">
                    <p className="mb-1 block text-sm text-muted-foreground">
                      {yearsGapLabelForSubject(sub, lang)}
                    </p>
                    {YEARS_GAP_OPTIONS.map((g) => (
                      <button
                        key={g.value}
                        type="button"
                        onClick={() =>
                          setS1((p) => ({
                            ...p,
                            yearsGapBySubject: {
                              ...p.yearsGapBySubject,
                              [sub]: g.value,
                            },
                          }))
                        }
                        className={optionBtnCls(s1.yearsGapBySubject[sub] === g.value)}
                      >
                        {lang === 'he' ? g.label_he : g.label_en}
                      </button>
                    ))}
                  </div>
                ))}
              </>
            ) : null}

            <div className="space-y-3 rounded-xl border border-border bg-card p-4">
              <p className="text-sm font-medium text-foreground">
                {t.s0_timeline}
              </p>
              <div>
                <label
                  htmlFor="next-test-name"
                  className="mb-1.5 block text-xs text-muted-foreground"
                >
                  {t.s0_nextTestName}
                </label>
                <input
                  id="next-test-name"
                  type="text"
                  placeholder={t.s0_nextTestNamePh}
                  value={s1.nextTestName}
                  onChange={(e) =>
                    setS1((p) => ({ ...p, nextTestName: e.target.value }))
                  }
                  className={inputCls}
                  dir="auto"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label
                    htmlFor="next-test-date"
                    className="mb-1.5 block text-xs text-muted-foreground"
                  >
                    {t.s0_nextTestDate}
                  </label>
                  <input
                    id="next-test-date"
                    type="date"
                    value={s1.nextTestDate}
                    onChange={(e) =>
                      setS1((p) => ({ ...p, nextTestDate: e.target.value }))
                    }
                    className={inputCls}
                  />
                </div>
                <div>
                  <label
                    htmlFor="final-goal-date"
                    className="mb-1.5 block text-xs text-muted-foreground"
                  >
                    {t.s0_finalGoalDate}
                  </label>
                  <input
                    id="final-goal-date"
                    type="date"
                    value={s1.finalGoalDate}
                    onChange={(e) =>
                      setS1((p) => ({ ...p, finalGoalDate: e.target.value }))
                    }
                    className={inputCls}
                  />
                </div>
              </div>
              <p className="text-xs text-muted-foreground/70">
                {t.s0_timelineHint}
              </p>
            </div>

            {!step0CanProceed ? (
              <p
                id="step0-missing-hint"
                className="text-sm text-muted-foreground"
                role="status"
                aria-live="polite"
              >
                {t.s0_missingPrefix}{' '}
                {step0MissingFields.join(lang === 'he' ? ' · ' : ', ')}
              </p>
            ) : null}

            <button
              type="button"
              disabled={!step0CanProceed}
              aria-describedby={!step0CanProceed ? 'step0-missing-hint' : undefined}
              onClick={() => setStep(1)}
              className={primaryBtnCls}
            >
              {t.next}
            </button>
          </div>
        )}

        {/* ── Step 1: Background ── */}
        {step === 1 && (
          <div className="space-y-7">
            <div>
              <h1 className="mb-1 text-2xl font-bold">{t.s1_title}</h1>
              <p className="text-sm text-muted-foreground">{t.s1_sub}</p>
            </div>

            <div className="space-y-3">
              <FieldLabel hint={t.s1_hoursHint} className="block">
                {t.s1_hours}
              </FieldLabel>
              <label className="flex cursor-pointer items-center gap-2 text-sm text-muted-foreground">
                <input
                  type="checkbox"
                  checked={s2.hoursAuto}
                  onChange={(e) =>
                    setS2((p) => ({ ...p, hoursAuto: e.target.checked }))
                  }
                  className="accent-cyan-400"
                />
                {t.s1_hoursAuto}
              </label>
              {!s2.hoursAuto ? (
                <SliderField
                  label={t.s1_hours}
                  min={2}
                  max={25}
                  value={s2.hoursPerWeek}
                  onChange={(v) => setS2((p) => ({ ...p, hoursPerWeek: v }))}
                  displayValue={`${s2.hoursPerWeek} ${t.s1_hoursUnit}`}
                />
              ) : null}
            </div>

            {s1.subjects.map((sub) => {
              const exp = s2.subjectExperience[sub] ?? DEFAULT_SUBJECT_EXPERIENCE();
              const subName = subjectLabel(sub, lang);
              return (
                <div
                  key={sub}
                  className="space-y-4 rounded-xl border border-border bg-card p-4"
                >
                  <p className="text-sm font-medium text-foreground">{subName}</p>
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                    {(
                      [
                        { v: 'share', label: t.s1_exp_share },
                        { v: 'no_prior', label: t.s1_exp_none },
                        { v: 'prefer_skip', label: t.s1_exp_skip },
                      ] as const
                    ).map(({ v, label }) => (
                      <button
                        key={v}
                        type="button"
                        onClick={() => patchSubjectExperience(sub, { mode: v })}
                        className={cn(
                          'rounded-lg border py-2.5 text-xs font-medium transition-colors',
                          exp.mode === v
                            ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
                            : 'border-border bg-background text-muted-foreground hover:border-border-bright hover:text-foreground',
                        )}
                      >
                        {label}
                      </button>
                    ))}
                  </div>

                  {exp.mode === 'share' ? (
                    <>
                      <SliderField
                        label={tx(t.s1_pastExperience, { subject: subName })}
                        min={1}
                        max={10}
                        value={exp.selfRating}
                        onChange={(v) => patchSubjectExperience(sub, { selfRating: v })}
                        displayValue={`${exp.selfRating}/10`}
                        hint={t.s1_pastExperienceHint}
                      />
                      <div>
                        <FieldLabel className="mb-2 block">
                          {tx(t.s1_teacherOverall, { subject: subName })}
                        </FieldLabel>
                        <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
                          {(
                            [
                              { v: 'mostly_good', label: t.s1_teacher_good },
                              { v: 'mixed', label: t.s1_teacher_mixed },
                              { v: 'mostly_bad', label: t.s1_teacher_bad },
                              { v: 'unknown', label: t.s1_teacher_unknown },
                              { v: 'no_teacher', label: t.s1_teacher_none },
                            ] as const
                          ).map(({ v, label }) => (
                            <button
                              key={v}
                              type="button"
                              onClick={() =>
                                patchSubjectExperience(sub, { teacherOverall: v })
                              }
                              className={cn(
                                'rounded-lg border py-2.5 text-xs font-medium transition-colors',
                                exp.teacherOverall === v
                                  ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
                                  : 'border-border bg-background text-muted-foreground hover:border-border-bright hover:text-foreground',
                              )}
                            >
                              {label}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label
                          htmlFor={`teacher-notes-${sub}`}
                          className="mb-1.5 block text-xs text-muted-foreground"
                        >
                          {tx(t.s1_teacherNotes, { subject: subName })}
                        </label>
                        <textarea
                          id={`teacher-notes-${sub}`}
                          rows={2}
                          placeholder={t.s1_teacherNotesPh}
                          value={exp.teacherNotes}
                          onChange={(e) =>
                            patchSubjectExperience(sub, { teacherNotes: e.target.value })
                          }
                          className={cn(inputCls, 'resize-none')}
                          dir="auto"
                        />
                      </div>
                    </>
                  ) : null}
                </div>
              );
            })}

            <div>
              <p className="mb-2 block text-sm text-muted-foreground">{t.s1_style}</p>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {(
                  [
                    { v: 'theory_first', label: t.s1_style_theory },
                    { v: 'practice_first', label: t.s1_style_practice },
                    { v: 'mixed', label: t.s1_style_mixed },
                    { v: 'unknown', label: t.s1_style_unknown },
                  ] as const
                ).map(({ v, label }) => (
                  <button
                    key={v}
                    type="button"
                    onClick={() => setS2((p) => ({ ...p, style: v }))}
                    className={cn(
                      'rounded-lg border py-2.5 text-xs font-medium transition-colors',
                      s2.style === v
                        ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
                        : 'border-border bg-card text-muted-foreground hover:border-border-bright hover:text-foreground',
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <FieldLabel className="mb-2 block">{t.s1_attention}</FieldLabel>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                {[
                  { v: 20, label: t.s1_attention_20 },
                  { v: 45, label: t.s1_attention_45 },
                  { v: 90, label: t.s1_attention_90 },
                  { v: null, label: t.s1_attention_unknown },
                ].map(({ v, label }) => (
                  <button
                    key={String(v)}
                    type="button"
                    onClick={() => setS2((p) => ({ ...p, attentionSpan: v }))}
                    className={cn(
                      'rounded-lg border py-2.5 text-sm font-medium transition-colors',
                      s2.attentionSpan === v
                        ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
                        : 'border-border bg-card text-muted-foreground hover:border-border-bright hover:text-foreground',
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button type="button" onClick={() => setStep(0)} className={secondaryBtnCls}>
                {t.back}
              </button>
              <button
                type="button"
                onClick={() => setStep(2)}
                className="flex-1 rounded-xl bg-accent-cyan py-3 text-sm font-semibold text-neutral-950 transition-colors hover:bg-cyan-300"
              >
                {t.next}
              </button>
            </div>
          </div>
        )}

        {/* ── Step 2: Mental / motivation ── */}
        {step === 2 && (
          <div className="space-y-7">
            <div>
              <h1 className="mb-1 text-2xl font-bold">{t.s2_title}</h1>
              <p className="text-sm text-muted-foreground">{t.s2_sub}</p>
            </div>

            <SliderField
              label={t.s2_motivation}
              min={1}
              max={10}
              value={s3.motivation}
              onChange={(v) => setS3((p) => ({ ...p, motivation: v }))}
              displayValue={`${s3.motivation}/10`}
            />

            <SliderField
              label={t.s2_anxiety}
              min={1}
              max={10}
              value={s3.anxiety}
              onChange={(v) => setS3((p) => ({ ...p, anxiety: v }))}
              displayValue={`${s3.anxiety}/10`}
              hint={t.s2_anxietyHint}
            />
            <p className="-mt-4 text-xs text-muted-foreground">{t.s2_anxietyConsent}</p>

            <SliderField
              label={t.s2_confidence}
              min={1}
              max={10}
              value={s3.confidence}
              onChange={(v) => setS3((p) => ({ ...p, confidence: v }))}
              displayValue={`${s3.confidence}/10`}
            />

            <div>
              <FieldLabel hint={t.s2_whenHint} className="mb-2 block">
                {t.s2_when}
              </FieldLabel>
              <div className="grid grid-cols-4 gap-2">
                {(
                  [
                    { v: 'morning', label: t.s2_when_morning },
                    { v: 'afternoon', label: t.s2_when_afternoon },
                    { v: 'evening', label: t.s2_when_evening },
                    { v: 'night', label: t.s2_when_night },
                  ] as const
                ).map(({ v, label }) => (
                  <button
                    key={v}
                    type="button"
                    onClick={() => setS3((p) => ({ ...p, preferredTime: v }))}
                    className={cn(
                      'rounded-lg border py-2.5 text-xs font-medium transition-colors',
                      s3.preferredTime === v
                        ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
                        : 'border-border bg-card text-muted-foreground hover:border-border-bright hover:text-foreground',
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="mb-2 block text-sm text-muted-foreground">{t.s2_quiet}</p>
                <div className="flex gap-2">
                  {[
                    { v: true, label: t.s2_yes },
                    { v: false, label: t.s2_no },
                  ].map(({ v, label }) => (
                    <button
                      key={String(v)}
                      type="button"
                      onClick={() => setS3((p) => ({ ...p, hasQuietSpace: v }))}
                      className={cn(
                        'flex-1 rounded-lg border py-2.5 text-xs font-medium transition-colors',
                        s3.hasQuietSpace === v
                          ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
                          : 'border-border bg-card text-muted-foreground hover:border-border-bright hover:text-foreground',
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <FieldLabel hint={t.s2_supportHint} className="mb-2 block">
                  {t.s2_support}
                </FieldLabel>
                <div className="flex gap-2">
                  {(
                    [
                      { v: 'strong', label: t.s2_support_strong },
                      { v: 'some', label: t.s2_support_some },
                      { v: 'none', label: t.s2_support_none },
                    ] as const
                  ).map(({ v, label }) => (
                    <button
                      key={v}
                      type="button"
                      onClick={() => setS3((p) => ({ ...p, supportSystem: v }))}
                      className={cn(
                        'flex-1 rounded-lg border py-2.5 text-xs font-medium transition-colors',
                        s3.supportSystem === v
                          ? 'border-accent-cyan bg-accent-cyan/10 text-foreground'
                          : 'border-border bg-card text-muted-foreground hover:border-border-bright hover:text-foreground',
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <label
                htmlFor="why-this-goal"
                className="mb-1.5 block text-xs text-muted-foreground"
              >
                {t.s2_why}
              </label>
              <textarea
                id="why-this-goal"
                rows={3}
                placeholder={t.s2_whyPh}
                value={s3.whyThisGoal}
                onChange={(e) =>
                  setS3((p) => ({ ...p, whyThisGoal: e.target.value }))
                }
                className={cn(inputCls, 'resize-none')}
                dir="auto"
              />
            </div>

            <div className="flex gap-3">
              <button type="button" onClick={() => setStep(1)} className={secondaryBtnCls}>
                {t.back}
              </button>
              <button
                type="button"
                onClick={() => setStep(3)}
                className="flex-1 rounded-xl bg-accent-cyan py-3 text-sm font-semibold text-neutral-950 transition-colors hover:bg-cyan-300"
              >
                {t.next}
              </button>
            </div>
          </div>
        )}

        {/* ── Step 3: Tutor mode ── */}
        {step === 3 && (
          <div className="space-y-7">
            <div>
              <h1 className="mb-1 text-2xl font-bold">{t.s4_title}</h1>
              <p className="text-sm text-muted-foreground">{t.s4_sub}</p>
            </div>

            <div className="space-y-2">
              {(
                [
                  { v: 'direct' as const, label: t.s4_direct },
                  { v: 'socratic' as const, label: t.s4_socratic },
                ] as const
              ).map(({ v, label }) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => setTutorMode(v)}
                  className={optionBtnCls(tutorMode === v)}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="flex gap-3">
              <button type="button" onClick={() => setStep(2)} className={secondaryBtnCls}>
                {t.back}
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={() => void handleSubmit()}
                className="flex-1 rounded-xl bg-accent-cyan py-3 text-sm font-semibold text-neutral-950 transition-colors hover:bg-cyan-300 disabled:opacity-50"
              >
                {submitting ? t.saving : t.createPlan}
              </button>
            </div>
            {error && (
              <p
                className="rounded-lg bg-destructive/10 px-4 py-2 text-sm text-destructive"
                role="alert"
              >
                {error}
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
