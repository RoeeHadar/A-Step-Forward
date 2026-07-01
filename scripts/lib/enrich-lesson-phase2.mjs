/**
 * Phase 2: Deepen theory, worked examples, pitfalls (structure unchanged).
 */
import { sectionEnWords, wordCount } from './lesson-depth.mjs';

const THRESHOLDS = {
  intro: 80,
  definition: 70,
  theory: 90,
  worked_example: 100,
  pitfall: 80,
  method_guide: 70,
};

function firstInsight(raw) {
  const insights = raw.agent_hints?.key_insights ?? [];
  if (insights.length > 0) return insights[0];
  return 'Master the core definitions before attempting harder exercises.';
}

function expandIntro(body, raw) {
  if (wordCount(body) >= THRESHOLDS.intro) return body;
  const title = raw.title_en ?? raw.concept_id ?? 'this topic';
  return `${body.trim()}\n\n**By the end of this lesson** you will be able to solve standard exam problems on ${title.replace(/_/g, ' ')}, explain the main idea in your own words, and avoid the pitfalls listed below.`;
}

function expandDefinitionOrTheory(body, raw, kind) {
  const min = THRESHOLDS[kind] ?? 70;
  if (wordCount(body) >= min) return body;
  const insight = firstInsight(raw);
  return `${body.trim()}\n\n**Intuition:** ${insight}\n\n**How to use this section:** Read each definition, then immediately try the matching checkpoint or exercise before moving on.`;
}

function normalizeWorkedExampleMoves(body) {
  let out = body;
  out = out.replace(/\*\*Step (\d+)[^*]*\*\*/g, '### Move $1');
  out = out.replace(/^Step (\d+)[—–-]/gm, '### Move $1 —');
  if (!/### Move 1/.test(out) && /\*\*Problem:\*\*/.test(out)) {
    out = out.replace(/\*\*Problem:\*\*/g, '### Move 1 — Understand the problem\n\n**Problem:**');
  }
  return out;
}

function expandWorkedExample(body) {
  let normalized = normalizeWorkedExampleMoves(body);
  if (wordCount(normalized) < THRESHOLDS.worked_example) {
    normalized = `${normalized.trim()}\n\n> **Why this path:** We use the method from the method guide because it matches the pattern in the problem (same givens, same goal). If you get stuck, name which move you are on before guessing the next algebra step.\n\n**After you finish:** Compare your result to the checkpoint or a simpler special case (e.g. set a parameter to $0$ or $1$) to catch algebra slips.`;
  }
  return normalized;
}

function expandPitfall(body, raw) {
  if (wordCount(body) >= THRESHOLDS.pitfall) return body;
  const misconceptions = raw.agent_hints?.common_misconceptions ?? [];
  let extra = '';
  if (misconceptions.length > 0) {
    const m = misconceptions[0];
    extra = `\n\n**Example misconception:** ${m.wrong ?? m}\n\n**Fix:** ${m.correction ?? 'Re-read the definition and check which condition failed.'}`;
  }
  return `${body.trim()}${extra}\n\n**Exam tip:** When reviewing mistakes, ask "which pitfall did I hit?" — not just "what is the right number?"`;
}

export function enrichPhase2(raw) {
  const sections = (raw.sections ?? []).map((s) => {
    const en = s.body_en_md ?? '';
    let body_en_md = en;
    switch (s.kind) {
      case 'intro':
        body_en_md = expandIntro(en, raw);
        break;
      case 'definition':
      case 'theory':
        body_en_md = expandDefinitionOrTheory(en, raw, s.kind);
        break;
      case 'worked_example':
        body_en_md = expandWorkedExample(en);
        break;
      case 'pitfall':
        body_en_md = expandPitfall(en, raw);
        break;
      case 'method_guide':
        if (sectionEnWords(s) < THRESHOLDS.method_guide) {
          body_en_md = `${en.trim()}\n\n**When to use:** Pick the row that matches your problem type first; only then substitute numbers.\n\n**Tip:** If two rows seem to fit, list the givens and match them to the table columns before calculating.`;
        }
        break;
      case 'before_exam':
        if (sectionEnWords(s) < 60) {
          body_en_md = `${en.trim()}\n\n**Last review:** Say each formula out loud once, then solve one checkpoint without looking.`;
        }
        break;
      case 'summary':
        if (sectionEnWords(s) < 50) {
          body_en_md = `${en.trim()}\n\n**Takeaway:** You should now recognize which method applies from the problem wording alone.`;
        }
        break;
      default:
        break;
    }
    if (body_en_md === en) return s;
    return { ...s, body_en_md };
  });

  return { ...raw, sections };
}
