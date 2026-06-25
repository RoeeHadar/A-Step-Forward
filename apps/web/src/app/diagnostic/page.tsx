'use client';

import { useCallback, useEffect, useState } from 'react';
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
}

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
      const res = await fetch('/api/plan/generate', { method: 'POST' });
      if (res.status === 404 || res.status === 501) {
        router.push('/plan');
        return;
      }
      if (!res.ok) throw new Error(await res.text());
      router.push('/plan');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Plan generation is not available yet');
      router.push('/plan');
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
    <div className="min-h-screen bg-neutral-950 text-white">
      <SiteHeader />
      <main className="mx-auto max-w-2xl px-4 py-10">
        {!complete && (
          <div className="mb-8">
            <div className="flex justify-between text-xs text-white/50 mb-2">
              <span>Question {questionNumber} of ~{totalEstimate}</span>
              <span>{progressPct}%</span>
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
          <p className="text-center text-white/50 py-20">Loading your diagnostic…</p>
        )}

        {error && (
          <p className="text-sm text-red-400 bg-red-400/10 px-4 py-3 rounded-lg mb-6">{error}</p>
        )}

        {!loading && !complete && question && (
          <div className="space-y-6">
            <div
              className="rounded-2xl border border-white/10 bg-white/5 p-6 prose prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: renderLatex(question.stem) }}
            />
            <div className="space-y-3">
              {question.options.map((opt) => (
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
                    aria-label={`Option ${opt.key}: ${opt.text.replace(/\$/g, '')}`}
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
              {submitting ? 'Checking…' : 'Submit answer'}
            </button>
          </div>
        )}

        {complete && (
          <div className="space-y-8">
            <div className="text-center">
              <h1 className="text-2xl font-bold mb-2">Your mastery profile</h1>
              <p className="text-sm text-white/50">
                Based on {questionNumber} adaptive questions across your topics.
              </p>
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
              <p className="text-center text-white/50 text-sm">No mastery data yet.</p>
            )}

            <button
              disabled={planLoading}
              onClick={() => void generatePlan()}
              className="w-full py-3 rounded-xl bg-accent-cyan text-neutral-950 font-semibold text-sm disabled:opacity-50 hover:bg-cyan-300 transition-colors"
            >
              {planLoading ? 'Generating…' : 'Generate my learning plan →'}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
