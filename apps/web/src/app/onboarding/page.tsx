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

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';
import { useI18n } from '@/providers/i18n-provider';
import { cn } from '@asf/ui';

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

type Subject = 'math' | 'physics';
type Style = 'theory_first' | 'practice_first' | 'mixed';

interface Step1 {
  goal: Goal | '';
  goalOther: string;
  gradeLevel: string;
  pointsGroup: string;
  subjects: Subject[];
  nextTestName: string;
  nextTestDate: string;
  finalGoalDate: string;
}

interface Step2 {
  hoursPerWeek: number;
  selfRating: number;
  teacherRating: number;
  style: Style;
  attentionSpan: number;
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
    s0_units: 'Math units',
    s0_timeline: 'Timeline',
    s0_nextTestName: 'Next big event / test',
    s0_nextTestNamePh: 'e.g. school midterm, mock Bagrut, semester final',
    s0_nextTestDate: 'Date of next event',
    s0_finalGoalDate: 'Final goal date',
    s0_timelineHint: 'Optional — leave blank if you do not have a specific deadline yet.',
    s1_title: 'Tell us about yourself',
    s1_sub: 'This calibrates your plan difficulty and pacing.',
    s1_hours: 'Hours available to study per week',
    s1_hoursUnit: 'hrs/week',
    s1_selfRating: 'How did you do in your last math/physics class?',
    s1_teacherRating: 'How good was your teacher? (affects pacing expectations)',
    s1_style: 'Preferred learning style',
    s1_style_theory: 'Theory first',
    s1_style_practice: 'Practice first',
    s1_style_mixed: 'Mixed',
    s1_attention: 'How long can you focus in one sitting?',
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
    s2_confidence:
      'How confident do you feel in your ability to reach your goal?',
    s2_when: 'When do you study best?',
    s2_when_morning: 'Morning',
    s2_when_afternoon: 'Afternoon',
    s2_when_evening: 'Evening',
    s2_when_night: 'Night',
    s2_quiet: 'Do you have a quiet study space?',
    s2_yes: 'Yes',
    s2_no: 'No',
    s2_support: 'Support system',
    s2_support_strong: 'Strong',
    s2_support_some: 'Some',
    s2_support_none: 'None',
    s2_why: 'In your own words: why does this goal matter to you? (optional)',
    s2_whyPh:
      'e.g. I want to qualify for engineering, prove to myself I can, get into a specific program…',
    s3_title: 'Rate your understanding',
    s3_sub:
      'Be honest — this is just the starting point. The diagnostic will verify and adapt.',
    next: 'Next',
    back: 'Back',
    saving: 'Saving…',
    startDiagnostic: 'Start my diagnostic',
    errorGeneric: 'Something went wrong',
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
    s0_units: 'יחידות במתמטיקה',
    s0_timeline: 'לוח זמנים',
    s0_nextTestName: 'אירוע או מבחן קרוב',
    s0_nextTestNamePh: 'למשל: מבחן בית-ספרי, בגרות מתכונת, בוחן סוף סמסטר',
    s0_nextTestDate: 'תאריך האירוע הבא',
    s0_finalGoalDate: 'תאריך היעד הסופי',
    s0_timelineHint:
      'לא חובה — אפשר להשאיר ריק אם אין תאריך יעד ספציפי כרגע.',
    s1_title: 'ספר/י לנו על עצמך',
    s1_sub: 'זה מכייל את רמת הקושי והקצב של התוכנית שלך.',
    s1_hours: 'שעות פנויות ללימוד בשבוע',
    s1_hoursUnit: 'שעות בשבוע',
    s1_selfRating: 'איך הסתדרת בשיעור האחרון במתמטיקה/פיזיקה?',
    s1_teacherRating:
      'עד כמה המורה שלך היה/הייתה טוב/ה? (משפיע על ציפיות הקצב)',
    s1_style: 'סגנון למידה מועדף',
    s1_style_theory: 'קודם תיאוריה',
    s1_style_practice: 'קודם תרגול',
    s1_style_mixed: 'מעורב',
    s1_attention: 'כמה זמן את/ה מצליח/ה להתרכז ברצף?',
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
    s2_confidence: 'עד כמה את/ה מאמין/ה ביכולת שלך להגיע ליעד?',
    s2_when: 'מתי את/ה הכי טוב/ה ללמוד?',
    s2_when_morning: 'בוקר',
    s2_when_afternoon: 'צהריים',
    s2_when_evening: 'ערב',
    s2_when_night: 'לילה',
    s2_quiet: 'יש לך מקום שקט ללימוד?',
    s2_yes: 'כן',
    s2_no: 'לא',
    s2_support: 'מערכת תמיכה',
    s2_support_strong: 'חזקה',
    s2_support_some: 'בינונית',
    s2_support_none: 'אין',
    s2_why: 'במילים שלך: למה המטרה הזו חשובה לך? (לא חובה)',
    s2_whyPh:
      'למשל: אני רוצה להתקבל להנדסה, להוכיח לעצמי שאני יכול/ה, להיכנס לתוכנית מסוימת…',
    s3_title: 'דרג/י את ההבנה שלך',
    s3_sub:
      'בכנות — זו רק נקודת ההתחלה. האבחון יאמת ויתאים את עצמו.',
    next: 'הבא',
    back: 'חזרה',
    saving: 'שומר…',
    startDiagnostic: 'התחל אבחון',
    errorGeneric: 'משהו השתבש',
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
  { value: '7', label_en: '7th grade', label_he: 'כיתה ז׳' },
  { value: '8', label_en: '8th grade', label_he: 'כיתה ח׳' },
  { value: '9', label_en: '9th grade', label_he: 'כיתה ט׳' },
  { value: '10', label_en: '10th grade', label_he: 'כיתה י׳' },
  { value: '11', label_en: '11th grade', label_he: 'כיתה י״א' },
  { value: '12', label_en: '12th grade', label_he: 'כיתה י״ב' },
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

const POINTS_GROUPS: { value: string; label_en: string; label_he: string }[] = [
  { value: '3', label_en: '3 units', label_he: '3 יחידות' },
  { value: '4', label_en: '4 units', label_he: '4 יחידות' },
  { value: '5', label_en: '5 units', label_he: '5 יחידות' },
];

const CONCEPTS_BY_SUBJECT: Record<
  Subject,
  { id: string; label_en: string; label_he: string }[]
> = {
  math: [
    { id: 'arithmetic', label_en: 'Arithmetic & Number Sense', label_he: 'חשבון ותחושת מספר' },
    { id: 'algebra_basics', label_en: 'Algebra Basics', label_he: 'יסודות האלגברה' },
    { id: 'equations_linear', label_en: 'Linear Equations', label_he: 'משוואות לינאריות' },
    { id: 'equations_quadratic', label_en: 'Quadratic Equations', label_he: 'משוואות ריבועיות' },
    { id: 'fractions_algebraic', label_en: 'Algebraic Fractions', label_he: 'שברים אלגבריים' },
    { id: 'trigonometry', label_en: 'Trigonometry', label_he: 'טריגונומטריה' },
    { id: 'functions', label_en: 'Functions', label_he: 'פונקציות' },
    { id: 'sequences', label_en: 'Sequences & Series', label_he: 'סדרות וטורים' },
    { id: 'limits', label_en: 'Limits', label_he: 'גבולות' },
    { id: 'derivatives', label_en: 'Derivatives', label_he: 'נגזרות' },
    { id: 'integrals', label_en: 'Integrals', label_he: 'אינטגרלים' },
  ],
  physics: [
    { id: 'kinematics', label_en: 'Kinematics', label_he: 'קינמטיקה' },
    { id: 'dynamics_newton', label_en: "Newton's Laws", label_he: 'חוקי ניוטון' },
    { id: 'energy_work', label_en: 'Energy & Work', label_he: 'אנרגיה ועבודה' },
    { id: 'waves', label_en: 'Waves & Oscillations', label_he: 'גלים ותנודות' },
    { id: 'electricity_circuits', label_en: 'Electric Circuits', label_he: 'מעגלים חשמליים' },
    { id: 'optics', label_en: 'Optics', label_he: 'אופטיקה' },
  ],
};

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
  const conceptLabel = (c: { label_en: string; label_he: string }) =>
    lang === 'he' ? c.label_he : c.label_en;

  const [step, setStep] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [s1, setS1] = useState<Step1>({
    goal: '',
    goalOther: '',
    gradeLevel: '11',
    pointsGroup: '5',
    subjects: ['math'],
    nextTestName: '',
    nextTestDate: '',
    finalGoalDate: '',
  });

  const [s2, setS2] = useState<Step2>({
    hoursPerWeek: 5,
    selfRating: 5,
    teacherRating: 5,
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

  function toggleSubject(sub: Subject) {
    setS1((prev) => ({
      ...prev,
      subjects: prev.subjects.includes(sub)
        ? prev.subjects.filter((s) => s !== sub)
        : [...prev.subjects, sub],
    }));
  }

  function setScore(conceptId: string, val: number) {
    setS4((prev) => ({
      ...prev,
      selfScores: { ...prev.selfScores, [conceptId]: val },
    }));
  }

  const conceptsForStep4 = s1.subjects.flatMap(
    (sub) => CONCEPTS_BY_SUBJECT[sub] ?? [],
  );
  const needsPointsGroup =
    s1.subjects.includes('math') &&
    s1.gradeLevel !== 'university_1' &&
    s1.gradeLevel !== 'university_2plus';

  async function handleSubmit() {
    setSubmitting(true);
    setError('');
    try {
      // Backend stays canonical English so cross-learner aggregations work.
      const goalText =
        s1.goal === 'other'
          ? s1.goalOther
          : (GOALS.find((g) => g.value === s1.goal)?.label_en ?? s1.goal);
      const res = await fetch('/api/onboarding/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: goalText,
          grade_level: s1.gradeLevel,
          points_group: needsPointsGroup ? s1.pointsGroup : null,
          subjects: s1.subjects,
          hours_per_week: s2.hoursPerWeek,
          preferred_style: s2.style,
          attention_span: s2.attentionSpan,
          self_scores: s4.selfScores,
          background_notes: `Self-rating: ${s2.selfRating}/10. Teacher rating: ${s2.teacherRating}/10.`,
          next_test_name: s1.nextTestName || null,
          next_test_date: s1.nextTestDate || null,
          final_goal_date: s1.finalGoalDate || null,
          mental_state: {
            motivation: s3.motivation,
            anxiety: s3.anxiety,
            confidence: s3.confidence,
            preferred_study_time: s3.preferredTime,
            has_quiet_space: s3.hasQuietSpace,
            support_system: s3.supportSystem,
            why_this_goal: s3.whyThisGoal,
          },
          personality_profile: {
            past_teacher_rating: s2.teacherRating,
            self_rating: s2.selfRating,
            learning_style: s2.style,
            attention_span_min: s2.attentionSpan,
            hours_per_week: s2.hoursPerWeek,
          },
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      router.push('/diagnostic');
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
              <p className="mb-1 block text-sm text-muted-foreground">{t.s0_goal}</p>
              {GOALS.map((g) => (
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

            <div className="space-y-2">
              <p className="mb-1 block text-sm text-muted-foreground">
                {t.s0_subjects}
              </p>
              <div className="flex gap-3">
                {(['math', 'physics'] as Subject[]).map((sub) => (
                  <button
                    key={sub}
                    type="button"
                    onClick={() => toggleSubject(sub)}
                    className={cn(
                      'flex-1 rounded-lg border py-2.5 text-sm font-medium transition-colors',
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
                  onChange={(e) =>
                    setS1((p) => ({ ...p, gradeLevel: e.target.value }))
                  }
                  className={inputCls}
                >
                  {GRADE_LEVELS.map((g) => (
                    <option key={g.value} value={g.value}>
                      {gradeLabel(g)}
                    </option>
                  ))}
                </select>
              </div>
              {needsPointsGroup && (
                <div>
                  <label
                    htmlFor="points-group"
                    className="mb-1.5 block text-xs text-muted-foreground"
                  >
                    {t.s0_units}
                  </label>
                  <select
                    id="points-group"
                    value={s1.pointsGroup}
                    onChange={(e) =>
                      setS1((p) => ({ ...p, pointsGroup: e.target.value }))
                    }
                    className={inputCls}
                  >
                    {POINTS_GROUPS.map((p) => (
                      <option key={p.value} value={p.value}>
                        {lang === 'he' ? p.label_he : p.label_en}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

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

            <button
              type="button"
              disabled={!s1.goal || s1.subjects.length === 0}
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

            <SliderField
              label={t.s1_hours}
              min={1}
              max={20}
              value={s2.hoursPerWeek}
              onChange={(v) => setS2((p) => ({ ...p, hoursPerWeek: v }))}
              displayValue={`${s2.hoursPerWeek} ${t.s1_hoursUnit}`}
            />

            <SliderField
              label={t.s1_selfRating}
              min={1}
              max={10}
              value={s2.selfRating}
              onChange={(v) => setS2((p) => ({ ...p, selfRating: v }))}
              displayValue={`${s2.selfRating}/10`}
            />

            <SliderField
              label={t.s1_teacherRating}
              min={1}
              max={10}
              value={s2.teacherRating}
              onChange={(v) => setS2((p) => ({ ...p, teacherRating: v }))}
              displayValue={`${s2.teacherRating}/10`}
            />

            <div>
              <p className="mb-2 block text-sm text-muted-foreground">{t.s1_style}</p>
              <div className="grid grid-cols-3 gap-2">
                {(
                  [
                    { v: 'theory_first', label: t.s1_style_theory },
                    { v: 'practice_first', label: t.s1_style_practice },
                    { v: 'mixed', label: t.s1_style_mixed },
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
              <p className="mb-2 block text-sm text-muted-foreground">
                {t.s1_attention}
              </p>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { v: 20, label: t.s1_attention_20 },
                  { v: 45, label: t.s1_attention_45 },
                  { v: 90, label: t.s1_attention_90 },
                ].map(({ v, label }) => (
                  <button
                    key={v}
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

            <SliderField
              label={t.s2_confidence}
              min={1}
              max={10}
              value={s3.confidence}
              onChange={(v) => setS3((p) => ({ ...p, confidence: v }))}
              displayValue={`${s3.confidence}/10`}
            />

            <div>
              <p className="mb-2 block text-sm text-muted-foreground">{t.s2_when}</p>
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
                <p className="mb-2 block text-sm text-muted-foreground">{t.s2_support}</p>
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

        {/* ── Step 3: Self-assessment ── */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h1 className="mb-1 text-2xl font-bold">{t.s3_title}</h1>
              <p className="text-sm text-muted-foreground">{t.s3_sub}</p>
            </div>

            <div className="space-y-5">
              {conceptsForStep4.map((c) => (
                <SliderField
                  key={c.id}
                  label={conceptLabel(c)}
                  min={1}
                  max={10}
                  value={s4.selfScores[c.id] ?? 5}
                  onChange={(v) => setScore(c.id, v)}
                  displayValue={`${s4.selfScores[c.id] ?? 5}/10`}
                />
              ))}
            </div>

            {error && (
              <p
                className="rounded-lg bg-destructive/10 px-4 py-2 text-sm text-destructive"
                role="alert"
              >
                {error}
              </p>
            )}

            <div className="flex gap-3">
              <button type="button" onClick={() => setStep(2)} className={secondaryBtnCls}>
                {t.back}
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={handleSubmit}
                className="flex-1 rounded-xl bg-accent-cyan py-3 text-sm font-semibold text-neutral-950 transition-colors hover:bg-cyan-300 disabled:opacity-50"
              >
                {submitting ? t.saving : t.startDiagnostic}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
