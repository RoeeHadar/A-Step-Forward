'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import katex from 'katex';
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from 'recharts';
import { SiteHeader } from '@/components/site-header';
import { useLanguagePreference } from '@/hooks/use-language-preference';
import 'katex/dist/katex.min.css';

interface DiagnosticOption {
  key: string;
  text: string;
}

interface DiagnosticQuestion {
  id: string;
  topic: string;
  subject: string;
  difficulty: number;
  stem: string;
  options: DiagnosticOption[];
  stem_he?: string | null;
  options_he?: DiagnosticOption[] | null;
}

/**
 * Localised UI strings for the diagnostic page. Kept inline here (rather
 * than a global i18n bundle) because the diagnostic is the very first
 * thing a new learner sees and we want zero coupling to a translation
 * framework we haven't introduced yet.
 */
const STR = {
  he: {
    question_n_of: (n: number, total: number) => `שאלה ${n} מתוך ~${total}`,
    loading: 'טוען את האבחון שלך…',
    submit: 'שלח תשובה',
    checking: 'בודק…',
    your_mastery: 'פרופיל השליטה שלך',
    based_on: (n: number) => `מבוסס על ${n} שאלות מותאמות לפי תחומי הלימוד שלך.`,
    generate_plan: 'יצירת תוכנית הלמידה שלי ←',
    generating: 'יוצר…',
    no_mastery: 'אין עדיין נתוני שליטה.',
    option_label: (k: string, text: string) => `אפשרות ${k}: ${text.replace(/\$/g, '')}`,
    fallback_plan_error: 'לא הצלחתי לייצר תוכנית למידה. נסה שוב מהכפתור למטה.',
    lang_toggle: 'EN',
  },
  en: {
    question_n_of: (n: number, total: number) => `Question ${n} of ~${total}`,
    loading: 'Loading your diagnostic…',
    submit: 'Submit answer',
    checking: 'Checking…',
    your_mastery: 'Your mastery profile',
    based_on: (n: number) => `Based on ${n} adaptive questions across your topics.`,
    generate_plan: 'Generate my learning plan →',
    generating: 'Generating…',
    no_mastery: 'No mastery data yet.',
    option_label: (k: string, text: string) => `Option ${k}: ${text.replace(/\$/g, '')}`,
    fallback_plan_error: 'Could not generate your learning plan. Try the button below.',
    lang_toggle: 'עב',
  },
} as const;

function renderLatex(text: string): string {
  return text.replace(/\$\$([^$]+)\$\$/g, (_m, expr: string) => {
    try {
      return katex.renderToString(expr, { throwOnError: false, displayMode: true });
    } catch {
      return expr;
    }
  }).replace(/\$([^$]+)\$/g, (_m, expr: string) => {
    try {
      return katex.renderToString(expr, { throwOnError: false });
    } catch {
      return expr;
    }
  }).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}

export default function DiagnosticPage() {
  const router = useRouter();
  const [lang, setLang] = useLanguagePreference('he');
  const t = STR[lang];
  const isHe = lang === 'he';
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState<DiagnosticQuestion | null>(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalEstimate] = useState(18);
  const [chosen, setChosen] = useState('');
  const [complete, setComplete] = useState(false);
  const [mastery, setMastery] = useState<Record<string, number>>({});
  const [planLoading, setPlanLoading] = useState(false);

  // Resolve which language to show for the current question. Falls back to
  // English if the HE columns aren't populated yet for this item.
  const display = useMemo<{ stem: string; options: DiagnosticOption[] } | null>(() => {
    if (!question) return null;
    if (isHe && question.stem_he && question.options_he && question.options_he.length > 0) {
      return { stem: question.stem_he, options: question.options_he };
    }
    return { stem: question.stem, options: question.options };
  }, [question, isHe]);

  const startSession = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/diagnostic/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topics: [] }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setSessionId(data.session_id);
      setQuestion(data.question);
      setQuestionNumber(data.question_number ?? 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start diagnostic');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void startSession();
  }, [startSession]);

  async function submitAnswer() {
    if (!sessionId || !question || !chosen) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await fetch(`/api/diagnostic/${sessionId}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: question.id, chosen }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (data.complete) {
        setComplete(true);
        setMastery(data.results?.mastery_by_topic ?? {});
        setQuestion(null);
        setPlanLoading(true);
        try {
          const planRes = await fetch('/api/plans/generate', { method: 'POST' });
          if (planRes.ok) {
            router.push('/dashboard');
            return;
          }
          const errText = await planRes.text();
          setError(errText || t.fallback_plan_error);
        } catch (planErr) {
          setError(
            planErr instanceof Error ? planErr.message : 'Could not generate your learning plan.',
          );
        } finally {
          setPlanLoading(false);
        }
      } else {
        setQuestion(data.question);
        setQuestionNumber(data.question_number ?? questionNumber + 1);
        setChosen('');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  }

  async function generatePlan() {
    setPlanLoading(true);
    setError('');
    try {
      const res = await fetch('/api/plans/generate', { method: 'POST' });
      if (!res.ok) throw new Error(await res.text());
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Plan generation failed');
    } finally {
      setPlanLoading(false);
    }
  }

  const radarData = Object.entries(mastery).map(([topic, score]) => ({
    topic: topic.replace(/_/g, ' '),
    mastery: Math.round(score * 100),
  }));

  const progressPct = complete ? 100 : Math.min(100, Math.round((questionNumber / totalEstimate) * 100));

  return (
    <div className="min-h-screen bg-neutral-950 text-white" dir={isHe ? 'rtl' : 'ltr'} lang={lang}>
      <SiteHeader />
      <main className="mx-auto max-w-2xl px-4 py-10">
        {!complete && (
          <div className="mb-8">
            <div className="flex justify-between text-xs text-white/50 mb-2">
              <span>{t.question_n_of(questionNumber, totalEstimate)}</span>
              <div className="flex items-center gap-3">
                <span>{progressPct}%</span>
                <button
                  type="button"
                  onClick={() => setLang(isHe ? 'en' : 'he')}
                  className="rounded border border-white/20 px-2 py-0.5 text-[10px] uppercase tracking-wider text-white/70 hover:text-white"
                  aria-label="Toggle language"
                >
                  {t.lang_toggle}
                </button>
              </div>
            </div>
            <div className="h-2 rounded-full bg-white/10 overflow-hidden">
              <div
                className="h-full bg-accent-cyan transition-all duration-300"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>
        )}

        {loading && (
          <p className="text-center text-white/50 py-20">{t.loading}</p>
        )}

        {error && (
          <p className="text-sm text-red-400 bg-red-400/10 px-4 py-3 rounded-lg mb-6">{error}</p>
        )}

        {!loading && !complete && question && display && (
          <div className="space-y-6">
            <div
              className="rounded-2xl border border-white/10 bg-white/5 p-6 prose prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: renderLatex(display.stem) }}
            />
            <div className="space-y-3">
              {display.options.map((opt) => (
                <label
                  key={opt.key}
                  htmlFor={`opt-${opt.key}`}
                  className={`flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all ${
                    chosen === opt.key
                      ? 'border-accent-cyan bg-accent-cyan/10'
                      : 'border-white/10 bg-white/5 hover:border-white/30'
                  }`}
                >
                  <input
                    id={`opt-${opt.key}`}
                    type="radio"
                    name="answer"
                    value={opt.key}
                    checked={chosen === opt.key}
                    onChange={() => setChosen(opt.key)}
                    aria-label={t.option_label(opt.key, opt.text)}
                    className="mt-1 h-5 w-5 accent-cyan-400"
                  />
                  <span className="text-sm leading-relaxed">
                    <span className="font-semibold me-2">{opt.key}.</span>
                    <span dangerouslySetInnerHTML={{ __html: renderLatex(opt.text) }} />
                  </span>
                </label>
              ))}
            </div>
            <button
              disabled={!chosen || submitting}
              onClick={() => void submitAnswer()}
              className="w-full py-3 rounded-xl bg-accent-cyan text-neutral-950 font-semibold text-sm disabled:opacity-40 hover:bg-cyan-300 transition-colors"
            >
              {submitting ? t.checking : t.submit}
            </button>
          </div>
        )}

        {complete && (
          <div className="space-y-8">
            <div className="text-center">
              <h1 className="text-2xl font-bold mb-2">{t.your_mastery}</h1>
              <p className="text-sm text-white/50">{t.based_on(questionNumber)}</p>
            </div>

            {radarData.length > 0 ? (
              <div className="h-80 rounded-2xl border border-white/10 bg-white/5 p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.15)" />
                    <PolarAngleAxis dataKey="topic" tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10 }} />
                    <Radar
                      name="Mastery"
                      dataKey="mastery"
                      stroke="#22d3ee"
                      fill="#22d3ee"
                      fillOpacity={0.35}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-center text-white/50 text-sm">{t.no_mastery}</p>
            )}

            <button
              disabled={planLoading}
              onClick={() => void generatePlan()}
              className="w-full py-3 rounded-xl bg-accent-cyan text-neutral-950 font-semibold text-sm disabled:opacity-50 hover:bg-cyan-300 transition-colors"
            >
              {planLoading ? t.generating : t.generate_plan}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
