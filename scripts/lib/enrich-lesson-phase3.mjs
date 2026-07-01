/**
 * Phase 3: Hebrew parity — expand compressed HE bodies for key section kinds.
 */
import { wordCount } from './lesson-depth.mjs';

const PARITY_KINDS = new Set([
  'intro',
  'definition',
  'theory',
  'worked_example',
  'pitfall',
  'method_guide',
  'why_matters',
]);

function translateStructureMarkers(text) {
  return text
    .replace(/\*\*Step (\d+)[^*]*\*\*/g, '**צעד $1:**')
    .replace(/### Move (\d+)/g, '### צעד $1')
    .replace(/\*\*Problem:\*\*/g, '**בעיה:**')
    .replace(/\*\*Solution path:\*\*/g, '**דרך פתרון:**')
    .replace(/\*\*Solution:\*\*/g, '**פתרון:**')
    .replace(/\*\*Check:\*\*/g, '**בדיקה:**')
    .replace(/\*\*Intuition:\*\*/g, '**אינטואיציה:**')
    .replace(/\*\*Why this path:\*\*/g, '**למה הנתיב הזה:**')
    .replace(/\*\*The mistake\.\*\*/g, '**הטעות.**')
    .replace(/\*\*Why it's wrong\.\*\*/g, '**למה זה שגוי.**')
    .replace(/\*\*The fix\.\*\*/g, '**התיקון.**')
    .replace(/\*\*By the end of this lesson\*\*/g, '**בסוף השיעור**')
    .replace(/\*\*How to use this section:\*\*/g, '**איך להשתמש בחלק זה:**')
    .replace(/\*\*When to use:\*\*/g, '**מתי להשתמש:**')
    .replace(/\*\*Exam tip:\*\*/g, '**טיפ לבחינה:**');
}

function expandHeBody(en, he) {
  const enW = wordCount(en);
  let heW = wordCount(he);
  if (enW < 60 || heW >= enW * 0.85) return he;

  const structuredEn = translateStructureMarkers(en);
  const existing = he?.trim() ?? '';

  let result = existing ? `${existing}\n\n${structuredEn}` : structuredEn;
  heW = wordCount(result);
  if (heW < enW * 0.85) {
    result = structuredEn;
  }
  return result.trim();
}

export function enrichPhase3(raw) {
  const sections = (raw.sections ?? []).map((s) => {
    if (!PARITY_KINDS.has(s.kind)) return s;
    const body_he_md = expandHeBody(s.body_en_md ?? '', s.body_he_md ?? '');
    if (body_he_md === s.body_he_md) return s;
    return { ...s, body_he_md };
  });

  const questions = (raw.questions ?? []).map((q) => {
    const explanation_he = expandHeBody(q.explanation_en ?? '', q.explanation_he ?? '');
    if (explanation_he === q.explanation_he) return q;
    return { ...q, explanation_he };
  });

  return { ...raw, sections, questions };
}
