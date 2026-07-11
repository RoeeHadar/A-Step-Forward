'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
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
import {
  clearDiagnosticSubjectsSession,
  DIAGNOSTIC_QUESTIONS_PER_SESSION,
  readApiErrorMessage,
  readDiagnosticSubjectsFromSession,
} from '@/lib/diagnostic-start';
import {
  generatePlanWithRetry,
  isRetryablePlanError,
  retryDelayMs,
  type DiagnosticFlowPhase,
} from '@/lib/diagnostic-plan-client';
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
    question_label: (n: number) => `שאלה ${n}`,
    loading: 'טוען את האבחון שלך…',
    loadFailed: 'לא הצלחנו לטעון את האבחון.',
    retry: 'נסה שוב',
    contactSupport: 'אם זה חוזר, התנתק/י והתחבר/י מחדש, או פנה/י לתמיכה.',
    submit: 'שלח תשובה',
    checking: 'בודק…',
    calibrating: 'מנתח את התשובות שלך…',
    generating_plan: 'יוצר את תוכנית הלמידה האישית שלך…',
    rate_limited: (sec: number) =>
      `המערכת עמוסה זמנית — ממתין ${sec} שניות לפני ניסיון נוסף…`,
    redirecting: 'התוכנית מוכנה — מעביר אותך ללוח הבקרה…',
    status_label: 'מה קורה עכשיו',
    your_mastery: 'סיימנו את האבחון',
    based_on: (n: number) =>
      n === 1
        ? 'כיול ראשוני משאלת אימות אחת — התוכנית תיבנה על בסיס התשובות שלך.'
        : `כיול ראשוני מ-${n} שאלות אימות — התוכנית תיבנה על בסיס התשובות שלך.`,
    generating_plan_elapsed: (sec: number) =>
      sec > 0
        ? `יוצר את תוכנית הלמידה האישית שלך… (${sec} שניות)`
        : 'יוצר את תוכנית הלמידה האישית שלך…',
    generate_plan: 'יצירת תוכנית הלמידה שלי ←',
    generating: 'יוצר…',
    retry_plan: 'נסה שוב ליצור תוכנית',
    no_mastery: 'אין עדיין נתוני שליטה.',
    option_label: (k: string, text: string) => `אפשרות ${k}: ${text.replace(/\$/g, '')}`,
    fallback_plan_error: 'לא הצלחתי לייצר תוכנית למידה. נסה שוב מהכפתור למטה.',
    lang_toggle: 'EN',
  },
  en: {
    question_label: (n: number) => `Question ${n}`,
    loading: 'Loading your diagnostic…',
    loadFailed: 'We could not load your diagnostic.',
    retry: 'Try again',
    contactSupport: 'If this keeps happening, sign out and back in, or contact support.',
    submit: 'Submit answer',
    checking: 'Checking…',
    calibrating: 'Analyzing your answers…',
    generating_plan: 'Building your personal learning plan…',
    rate_limited: (sec: number) =>
      `The system is busy — waiting ${sec}s before trying again…`,
    redirecting: 'Your plan is ready — taking you to your dashboard…',
    status_label: 'What’s happening now',
    your_mastery: 'Diagnostic complete',
    based_on: (n: number) =>
      n === 1
        ? 'Initial calibration from 1 validation question — your plan will build on your answers.'
        : `Initial calibration from ${n} validation questions — your plan will build on your answers.`,
    generating_plan_elapsed: (sec: number) =>
      sec > 0
        ? `Building your personal learning plan… (${sec}s)`
        : 'Building your personal learning plan…',
    generate_plan: 'Generate my learning plan →',
    generating: 'Generating…',
    retry_plan: 'Retry plan generation',
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
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(1);
  const [answeredCount, setAnsweredCount] = useState(0);
  const [sessionTotal, setSessionTotal] = useState(DIAGNOSTIC_QUESTIONS_PER_SESSION);
  const [chosen, setChosen] = useState('');
  const [complete, setComplete] = useState(false);
  const [mastery, setMastery] = useState<Record<string, number>>({});
  const [phase, setPhase] = useState<DiagnosticFlowPhase>('loading');
  const [phaseDetail, setPhaseDetail] = useState('');
  const [planReady, setPlanReady] = useState(false);
  const [answerRetrySec, setAnswerRetrySec] = useState(0);

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
    setPhase('loading');
    setError('');
    try {
      const sessionSubjects = readDiagnosticSubjectsFromSession();
      const res = await fetch('/api/diagnostic/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topics: [],
          ...(sessionSubjects ? { subjects: sessionSubjects } : {}),
        }),
      });
      if (!res.ok) throw new Error(await readApiErrorMessage(res));
      const data = (await res.json()) as {
        session_id?: string;
        question?: DiagnosticQuestion;
        question_number?: number;
        total?: number;
        complete?: boolean;
        results?: { mastery_by_topic?: Record<string, number> };
        questions_answered?: number;
        resumed?: boolean;
      };
      if (data.complete) {
        if ((data.questions_answered ?? 0) < 1) {
          throw new Error(t.loadFailed);
        }
        clearDiagnosticSubjectsSession();
        setSessionId(data.session_id ?? null);
        setComplete(true);
        setMastery(data.results?.mastery_by_topic ?? {});
        setQuestion(null);
        setAnsweredCount(data.questions_answered ?? 0);
        if (data.total) setSessionTotal(data.total);
        setPhase('calibrating');
        return;
      }
      if (!data.session_id || !data.question?.stem?.trim()) {
        throw new Error(t.loadFailed);
      }
      if (!data.question.options?.length) {
        throw new Error(t.loadFailed);
      }
      clearDiagnosticSubjectsSession();
      setSessionId(data.session_id);
      setQuestion(data.question);
      const qNum = data.question_number ?? 1;
      setCurrentQuestionIndex(qNum);
      setAnsweredCount(Math.max(0, qNum - 1));
      setSessionTotal(data.total ?? DIAGNOSTIC_QUESTIONS_PER_SESSION);
      setPhase('question');
    } catch (err) {
      setError(err instanceof Error && err.message ? err.message : t.loadFailed);
      setQuestion(null);
      setSessionId(null);
      setPhase('error');
    } finally {
      setLoading(false);
    }
  }, [t.loadFailed]);

  useEffect(() => {
    void startSession();
  }, [startSession]);

  const planRunRef = useRef(false);

  const runPlanGeneration = useCallback(async () => {
    if (planRunRef.current) return;
    planRunRef.current = true;
    setError('');
    try {
      await generatePlanWithRetry({
        onPhase: (nextPhase, detail) => {
          setPhase(nextPhase);
          setPhaseDetail(detail ?? '');
        },
      });
      setPlanReady(true);
      router.push('/app');
    } catch (err) {
      planRunRef.current = false;
      setPhase('error');
      setError(err instanceof Error ? err.message : t.fallback_plan_error);
    }
  }, [router, t.fallback_plan_error]);

  useEffect(() => {
    if (complete && !planReady && phase !== 'error') {
      void runPlanGeneration();
    }
  }, [complete, planReady, phase, runPlanGeneration]);

  async function submitAnswer() {
    if (!sessionId || !question || !chosen) return;
    setSubmitting(true);
    setPhase('checking');
    setError('');
    try {
      const res = await fetch(`/api/diagnostic/${sessionId}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: question.id, chosen }),
      });
      const text = await res.text();
      if (!res.ok) {
        let message = text.trim() || `Request failed (${res.status})`;
        let retryAfterSec = 15;
        try {
          const body = JSON.parse(text) as {
            error?: string;
            message?: string;
            retry_after_sec?: number;
          };
          message = body.error ?? body.message ?? message;
          if (body.retry_after_sec) retryAfterSec = body.retry_after_sec;
        } catch {
          /* plain text */
        }
        if (isRetryablePlanError(res.status, message)) {
          setPhase('rate_limited');
          setAnswerRetrySec(retryAfterSec);
          await new Promise((r) => setTimeout(r, retryDelayMs(0, retryAfterSec)));
          setPhase('question');
          setSubmitting(false);
          return;
        }
        throw new Error(message);
      }
      const data = JSON.parse(text) as {
        complete?: boolean;
        question?: DiagnosticQuestion;
        question_number?: number;
        total?: number;
        results?: { mastery_by_topic?: Record<string, number> };
        questions_answered?: number;
      };
      if (data.complete) {
        setPhase('calibrating');
        setComplete(true);
        setMastery(data.results?.mastery_by_topic ?? {});
        setQuestion(null);
        setAnsweredCount(data.questions_answered ?? answeredCount + 1);
        if (data.total) setSessionTotal(data.total);
      } else {
        if (!data.question?.stem?.trim() || !data.question.options?.length) {
          throw new Error(t.loadFailed);
        }
        const qNum = data.question_number ?? currentQuestionIndex + 1;
        setQuestion(data.question);
        setCurrentQuestionIndex(qNum);
        setAnsweredCount(Math.max(0, qNum - 1));
        if (data.total) setSessionTotal(data.total);
        setChosen('');
        setPhase('question');
      }
    } catch (err) {
      setPhase('error');
      setError(err instanceof Error ? err.message : 'Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  }

  const radarData = Object.entries(mastery).map(([topic, score]) => ({
    topic: topic.replace(/_/g, ' '),
    mastery: Math.round(score * 100),
  }));

  const progressPct = complete
    ? 100
    : sessionTotal > 0
      ? Math.min(100, Math.round((answeredCount / sessionTotal) * 100))
      : 0;

  const statusMessage = (() => {
    switch (phase) {
      case 'loading':
        return t.loading;
      case 'checking':
        return t.checking;
      case 'calibrating':
        return t.calibrating;
      case 'generating_plan':
        return t.generating_plan_elapsed(Number(phaseDetail) || 0);
      case 'rate_limited':
        return t.rate_limited(Number(phaseDetail) || answerRetrySec || 15);
      case 'redirecting':
        return t.redirecting;
      default:
        return '';
    }
  })();

  return (
    <div className="min-h-screen bg-neutral-950 text-white" dir={isHe ? 'rtl' : 'ltr'} lang={lang}>
      <SiteHeader />
      <main className="mx-auto max-w-2xl px-4 py-10">
        {!complete && (
          <div className="mb-8">
            <div className="flex justify-between text-xs text-white/50 mb-2">
              <span>{t.question_label(currentQuestionIndex)}</span>
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
            {statusMessage && phase !== 'question' && (
              <p className="mt-3 text-xs text-accent-cyan/90">{statusMessage}</p>
            )}
          </div>
        )}

        {complete && statusMessage && (
          <div className="mb-6 rounded-xl border border-accent-cyan/30 bg-accent-cyan/10 px-4 py-3">
            <p className="text-xs uppercase tracking-wider text-accent-cyan/70 mb-1">
              {t.status_label}
            </p>
            <p className="text-sm text-white/90">{statusMessage}</p>
          </div>
        )}

        {loading && (
          <p className="text-center text-white/50 py-20">{t.loading}</p>
        )}

        {error && (
          <div className="mb-6 space-y-3 rounded-lg border border-red-400/30 bg-red-400/10 px-4 py-3">
            <p className="text-sm text-red-400">{error}</p>
            <p className="text-xs text-white/50">{t.contactSupport}</p>
            <button
              type="button"
              onClick={() => {
                if (complete) {
                  void runPlanGeneration();
                } else if (sessionId && question && chosen) {
                  void submitAnswer();
                } else {
                  void startSession();
                }
              }}
              className="rounded-lg border border-white/20 px-4 py-2 text-sm text-white hover:border-white/40"
            >
              {t.retry}
            </button>
          </div>
        )}

        {!loading && !complete && !question && !error && (
          <div className="space-y-4 py-20 text-center">
            <p className="text-white/50">{t.loadFailed}</p>
            <button
              type="button"
              onClick={() => void startSession()}
              className="rounded-xl bg-accent-cyan px-5 py-2.5 text-sm font-semibold text-neutral-950 hover:bg-cyan-300"
            >
              {t.retry}
            </button>
          </div>
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
              <p className="text-sm text-white/50">{t.based_on(answeredCount)}</p>
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
              disabled={phase === 'generating_plan' || phase === 'redirecting' || phase === 'rate_limited'}
              onClick={() => void runPlanGeneration()}
              className="w-full py-3 rounded-xl bg-accent-cyan text-neutral-950 font-semibold text-sm disabled:opacity-50 hover:bg-cyan-300 transition-colors"
            >
              {phase === 'generating_plan' || phase === 'redirecting' || phase === 'rate_limited'
                ? t.generating
                : error
                  ? t.retry_plan
                  : t.generating}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
