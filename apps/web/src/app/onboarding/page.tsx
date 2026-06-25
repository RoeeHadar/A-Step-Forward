'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { SiteHeader } from '@/components/site-header';

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
}

interface Step2 {
  hoursPerWeek: number;
  selfRating: number;
  teacherRating: number;
  style: Style;
  attentionSpan: number;
}

interface Step3 {
  selfScores: Record<string, number>;
}

// ── Constants ────────────────────────────────────────────────────────────────

const GOALS: { value: Goal; label: string }[] = [
  { value: 'bagrut_math_5', label: 'Pass Bagrut — Math 5pt (מגמה 5 יח׳)' },
  { value: 'bagrut_math_4', label: 'Pass Bagrut — Math 4pt (מגמה 4 יח׳)' },
  { value: 'bagrut_math_3', label: 'Pass Bagrut — Math 3pt (מגמה 3 יח׳)' },
  { value: 'bagrut_physics', label: 'Pass Bagrut — Physics (פיזיקה)' },
  { value: 'calculus1', label: 'University — Calculus 1 (חדו״א 1)' },
  { value: 'linear_algebra', label: 'University — Linear Algebra (אלגברה לינארית)' },
  { value: 'university_prep', label: 'General university preparation' },
  { value: 'other', label: 'Other goal (specify below)' },
];

const GRADE_LEVELS = [
  { value: '7', label: '7th grade' },
  { value: '8', label: '8th grade' },
  { value: '9', label: '9th grade' },
  { value: '10', label: '10th grade' },
  { value: '11', label: '11th grade' },
  { value: '12', label: '12th grade' },
  { value: 'university_1', label: 'University — 1st year' },
  { value: 'university_2plus', label: 'University — 2nd year+' },
];

const CONCEPTS_BY_SUBJECT: Record<Subject, { id: string; label: string }[]> = {
  math: [
    { id: 'arithmetic', label: 'Arithmetic & Number Sense (חשבון)' },
    { id: 'algebra_basics', label: 'Algebra Basics (אלגברה בסיסית)' },
    { id: 'equations_linear', label: 'Linear Equations (משוואות)' },
    { id: 'equations_quadratic', label: 'Quadratic Equations (משוואות ריבועיות)' },
    { id: 'fractions_algebraic', label: 'Algebraic Fractions (שברים)' },
    { id: 'trigonometry', label: 'Trigonometry (טריגונומטריה)' },
    { id: 'functions', label: 'Functions (פונקציות)' },
    { id: 'sequences', label: 'Sequences & Series (סדרות)' },
    { id: 'limits', label: 'Limits (גבולות)' },
    { id: 'derivatives', label: 'Derivatives (נגזרות)' },
    { id: 'integrals', label: 'Integrals (אינטגרלים)' },
  ],
  physics: [
    { id: 'kinematics', label: 'Kinematics (קינמטיקה)' },
    { id: 'dynamics_newton', label: "Newton's Laws (חוקי ניוטון)" },
    { id: 'energy_work', label: 'Energy & Work (אנרגיה)' },
    { id: 'waves', label: 'Waves & Oscillations (גלים)' },
    { id: 'electricity_circuits', label: 'Electric Circuits (חשמל)' },
    { id: 'optics', label: 'Optics (אופטיקה)' },
  ],
};

// ── Step components ──────────────────────────────────────────────────────────

function StepIndicator({ current, total }: { current: number; total: number }) {
  return (
    <div className="flex items-center gap-2 mb-8">
      {Array.from({ length: total }, (_, i) => (
        <div key={i} className="flex items-center gap-2">
          <div
            className={`h-2.5 w-2.5 rounded-full transition-all ${
              i < current
                ? 'bg-accent-cyan'
                : i === current
                  ? 'bg-accent-cyan ring-2 ring-accent-cyan/30 w-5'
                  : 'bg-white/20'
            }`}
          />
          {i < total - 1 && (
            <div className={`h-px w-8 ${i < current ? 'bg-accent-cyan' : 'bg-white/20'}`} />
          )}
        </div>
      ))}
      <span className="ml-2 text-sm text-white/50">
        Step {current + 1} of {total}
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
}: {
  label: string;
  min: number;
  max: number;
  step?: number;
  value: number;
  onChange: (v: number) => void;
  displayValue?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-white/70">{label}</span>
        <span className="font-semibold text-accent-cyan">{displayValue ?? value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-cyan-400 h-1.5 cursor-pointer"
      />
      <div className="flex justify-between text-xs text-white/30">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────────────────────

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [s1, setS1] = useState<Step1>({
    goal: '',
    goalOther: '',
    gradeLevel: '11',
    pointsGroup: '5',
    subjects: ['math'],
  });

  const [s2, setS2] = useState<Step2>({
    hoursPerWeek: 5,
    selfRating: 5,
    teacherRating: 5,
    style: 'mixed',
    attentionSpan: 45,
  });

  const [s3, setS3] = useState<Step3>({ selfScores: {} });

  function toggleSubject(sub: Subject) {
    setS1((prev) => ({
      ...prev,
      subjects: prev.subjects.includes(sub)
        ? prev.subjects.filter((s) => s !== sub)
        : [...prev.subjects, sub],
    }));
  }

  function setScore(conceptId: string, val: number) {
    setS3((prev) => ({ ...prev, selfScores: { ...prev.selfScores, [conceptId]: val } }));
  }

  const conceptsForStep3 = s1.subjects.flatMap((sub) => CONCEPTS_BY_SUBJECT[sub] ?? []);
  const needsPointsGroup = s1.subjects.includes('math') && s1.gradeLevel !== 'university_1' && s1.gradeLevel !== 'university_2plus';

  async function handleSubmit() {
    setSubmitting(true);
    setError('');
    try {
      const goalText = s1.goal === 'other' ? s1.goalOther : (GOALS.find((g) => g.value === s1.goal)?.label ?? s1.goal);
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
          self_scores: s3.selfScores,
          background_notes: `Self-rating: ${s2.selfRating}/10. Teacher rating: ${s2.teacherRating}/10.`,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      router.push('/diagnostic');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <SiteHeader />
      <main className="mx-auto max-w-xl px-4 py-12">
        <StepIndicator current={step} total={3} />

        {/* ── Step 0: Goals ── */}
        {step === 0 && (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold mb-1">What are you working towards?</h1>
              <p className="text-sm text-white/50">This helps us build your personalized plan.</p>
            </div>

            <div className="space-y-2">
              <p className="block text-sm text-white/70 mb-1">Learning goal</p>
              {GOALS.map((g) => (
                <button
                  key={g.value}
                  onClick={() => setS1((p) => ({ ...p, goal: g.value }))}
                  className={`w-full text-left px-4 py-2.5 rounded-lg border text-sm transition-all ${
                    s1.goal === g.value
                      ? 'border-accent-cyan bg-accent-cyan/10 text-white'
                      : 'border-white/10 bg-white/5 text-white/70 hover:border-white/30'
                  }`}
                >
                  {g.label}
                </button>
              ))}
              {s1.goal === 'other' && (
                <input
                  type="text"
                  placeholder="Describe your goal..."
                  value={s1.goalOther}
                  onChange={(e) => setS1((p) => ({ ...p, goalOther: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-lg border border-white/20 bg-white/5 text-sm focus:outline-none focus:border-accent-cyan"
                />
              )}
            </div>

            <div className="space-y-2">
              <p className="block text-sm text-white/70 mb-1">Subjects</p>
              <div className="flex gap-3">
                {(['math', 'physics'] as Subject[]).map((sub) => (
                  <button
                    key={sub}
                    onClick={() => toggleSubject(sub)}
                    className={`flex-1 py-2.5 rounded-lg border text-sm font-medium transition-all ${
                      s1.subjects.includes(sub)
                        ? 'border-accent-cyan bg-accent-cyan/10 text-white'
                        : 'border-white/10 bg-white/5 text-white/50 hover:border-white/30'
                    }`}
                  >
                    {sub === 'math' ? '📐 Math' : '⚛️ Physics'}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="grade-level" className="block text-xs text-white/50 mb-1.5">Grade level</label>
                <select
                  id="grade-level"
                  value={s1.gradeLevel}
                  onChange={(e) => setS1((p) => ({ ...p, gradeLevel: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg border border-white/10 bg-neutral-900 text-sm focus:outline-none focus:border-accent-cyan"
                >
                  {GRADE_LEVELS.map((g) => (
                    <option key={g.value} value={g.value}>{g.label}</option>
                  ))}
                </select>
              </div>
              {needsPointsGroup && (
                <div>
                  <label htmlFor="points-group" className="block text-xs text-white/50 mb-1.5">Math units</label>
                  <select
                    id="points-group"
                    value={s1.pointsGroup}
                    onChange={(e) => setS1((p) => ({ ...p, pointsGroup: e.target.value }))}
                    className="w-full px-3 py-2 rounded-lg border border-white/10 bg-neutral-900 text-sm focus:outline-none focus:border-accent-cyan"
                  >
                    <option value="3">3 units (בסיסי)</option>
                    <option value="4">4 units (רגיל)</option>
                    <option value="5">5 units (מורחב)</option>
                  </select>
                </div>
              )}
            </div>

            <button
              disabled={!s1.goal || s1.subjects.length === 0}
              onClick={() => setStep(1)}
              className="w-full py-3 rounded-xl bg-accent-cyan text-neutral-950 font-semibold text-sm disabled:opacity-40 hover:bg-cyan-300 transition-colors"
            >
              Next →
            </button>
          </div>
        )}

        {/* ── Step 1: Background ── */}
        {step === 1 && (
          <div className="space-y-7">
            <div>
              <h1 className="text-2xl font-bold mb-1">Tell us about yourself</h1>
              <p className="text-sm text-white/50">This calibrates your plan difficulty and pacing.</p>
            </div>

            <SliderField
              label="Hours available to study per week"
              min={1}
              max={20}
              value={s2.hoursPerWeek}
              onChange={(v) => setS2((p) => ({ ...p, hoursPerWeek: v }))}
              displayValue={`${s2.hoursPerWeek} hrs/week`}
            />

            <SliderField
              label="How did you do in your last math/physics class?"
              min={1}
              max={10}
              value={s2.selfRating}
              onChange={(v) => setS2((p) => ({ ...p, selfRating: v }))}
              displayValue={`${s2.selfRating}/10`}
            />

            <SliderField
              label="How good was your teacher? (affects pacing expectations)"
              min={1}
              max={10}
              value={s2.teacherRating}
              onChange={(v) => setS2((p) => ({ ...p, teacherRating: v }))}
              displayValue={`${s2.teacherRating}/10`}
            />

            <div>
              <p className="block text-sm text-white/70 mb-2">Preferred learning style</p>
              <div className="grid grid-cols-3 gap-2">
                {(
                  [
                    { v: 'theory_first', label: '📖 Theory first' },
                    { v: 'practice_first', label: '✏️ Practice first' },
                    { v: 'mixed', label: '⚖️ Mixed' },
                  ] as const
                ).map(({ v, label }) => (
                  <button
                    key={v}
                    onClick={() => setS2((p) => ({ ...p, style: v }))}
                    className={`py-2.5 rounded-lg border text-xs font-medium transition-all ${
                      s2.style === v
                        ? 'border-accent-cyan bg-accent-cyan/10 text-white'
                        : 'border-white/10 bg-white/5 text-white/50 hover:border-white/30'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="block text-sm text-white/70 mb-2">
                How long can you focus in one sitting?
              </p>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { v: 20, label: '20 min' },
                  { v: 45, label: '45 min' },
                  { v: 90, label: '90 min' },
                ].map(({ v, label }) => (
                  <button
                    key={v}
                    onClick={() => setS2((p) => ({ ...p, attentionSpan: v }))}
                    className={`py-2.5 rounded-lg border text-sm font-medium transition-all ${
                      s2.attentionSpan === v
                        ? 'border-accent-cyan bg-accent-cyan/10 text-white'
                        : 'border-white/10 bg-white/5 text-white/50 hover:border-white/30'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(0)}
                className="flex-1 py-3 rounded-xl border border-white/20 text-sm text-white/70 hover:border-white/40 transition-colors"
              >
                ← Back
              </button>
              <button
                onClick={() => setStep(2)}
                className="flex-1 py-3 rounded-xl bg-accent-cyan text-neutral-950 font-semibold text-sm hover:bg-cyan-300 transition-colors"
              >
                Next →
              </button>
            </div>
          </div>
        )}

        {/* ── Step 2: Self-assessment ── */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold mb-1">Rate your understanding</h1>
              <p className="text-sm text-white/50">
                Be honest — this is just the starting point. The system will verify and adapt.
              </p>
            </div>

            <div className="space-y-5">
              {conceptsForStep3.map(({ id, label }) => (
                <SliderField
                  key={id}
                  label={label}
                  min={1}
                  max={10}
                  value={s3.selfScores[id] ?? 5}
                  onChange={(v) => setScore(id, v)}
                  displayValue={`${s3.selfScores[id] ?? 5}/10`}
                />
              ))}
            </div>

            {error && (
              <p className="text-sm text-red-400 bg-red-400/10 px-4 py-2 rounded-lg">{error}</p>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-3 rounded-xl border border-white/20 text-sm text-white/70 hover:border-white/40 transition-colors"
              >
                ← Back
              </button>
              <button
                disabled={submitting}
                onClick={handleSubmit}
                className="flex-1 py-3 rounded-xl bg-accent-cyan text-neutral-950 font-semibold text-sm disabled:opacity-50 hover:bg-cyan-300 transition-colors"
              >
                {submitting ? 'Saving…' : 'Start my diagnostic →'}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
