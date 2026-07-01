/**
 * Editorial cleanup for rule-based enrichment artifacts.
 * Removes template filler, deduplicates paragraphs, strips EN pasted into HE bodies,
 * and synthesizes missing bilingual summaries.
 */
import { wordCount } from './lesson-depth.mjs';

const BOILERPLATE_PATTERNS = [
  /\n\n\*\*By the end of this lesson\*\* you will be able to solve standard exam problems on[^.\n]+\..*?(?=\n\n|$)/gs,
  /\n\n\*\*בסוף השיעור\*\* you will be able to solve standard exam problems on[^.\n]+\..*?(?=\n\n|$)/gs,
  /\n\n\*\*Intuition:\*\*[^\n]*(?:\n\n\*\*How to use this section:\*\*[^\n]*)?/g,
  /\n\n\*\*אינטואיציה:\*\*[^\n]*(?:\n\n\*\*איך להשתמש בחלק זה:\*\*[^\n]*)?/g,
  /\n\n\*\*How to use this section:\*\* Read each definition, then immediately try the matching checkpoint or exercise before moving on\./g,
  /\n\n\*\*איך להשתמש בחלק זה:\*\* Read each definition, then immediately try the matching checkpoint or exercise before moving on\./g,
  /\n\n> \*\*Why this path:\*\* We use the method from the method guide because it matches the pattern in the problem \(same givens, same goal\)\. If you get stuck, name which move you are on before guessing the next algebra step\./g,
  /\n\n> \*\*למה הנתיב הזה:\*\* We use the method from the method guide because it matches the pattern in the problem \(same givens, same goal\)\. If you get stuck, name which move you are on before guessing the next algebra step\./g,
  /\n\n\*\*After you finish:\*\* Compare your result to the checkpoint or a simpler special case \(e\.g\. set a parameter to \$0\$ or \$1\$\) to catch algebra slips\./g,
  /\n\n\*\*Exam tip:\*\* When reviewing mistakes, ask "which pitfall did I hit\?" — not just "what is the right number\?"/g,
];

const HE_PHRASE_FIXES = [
  [
    /\*\*בסוף השיעור\*\* you will be able to solve standard exam problems on[^.\n]+\./g,
    '',
  ],
  [
    /\*\*איך להשתמש בחלק זה:\*\* Read each definition, then immediately try the matching checkpoint or exercise before moving on\./g,
    '**איך להשתמש בחלק זה:** קראו כל הגדרה, ואז נסו מיד את נקודת הביקורת או התרגיל המתאים לפני שממשיכים.',
  ],
  [
    /> \*\*למה הנתיב הזה:\*\* We use the method from the method guide because it matches the pattern in the problem \(same givens, same goal\)\. If you get stuck, name which move you are on before guessing the next algebra step\./g,
    '',
  ],
  [/\*\*After you finish:\*\* Compare your result to the checkpoint or a simpler special case \(e\.g\. set a parameter to \$0\$ or \$1\$\) to catch algebra slips\./g, ''],
  [/\*\*When to use:\*\*/g, '**מתי להשתמש:**'],
  [/\*\*Key insight:\*\*/g, '**תובנת מפתח:**'],
  [/\*\*Warning:\*\*/g, '**אזהרה:**'],
  [/\*\*Remark:\*\*/g, '**הערה:**'],
  [/\*\*Problem:\*\*/g, '**בעיה:**'],
  [/\*\*Solution:\*\*/g, '**פתרון:**'],
  [/\*\*Check:\*\*/g, '**בדיקה:**'],
  [/\*\*Verify:\*\*/g, '**אימות:**'],
  [/\*\*Compute\*\*/g, '**חשבו**'],
  [/\*\*Find\*\*/g, '**מצאו**'],
  [/\*\*Expand\*\*/g, '**פתחו**'],
  [/\*\*Directly:\*\*/g, '**ישירות:**'],
  [/\*\*Relationship:\*\*/g, '**קשר:**'],
  [/\*\*Properties:\*\*/g, '**תכונות:**'],
  [/\*\*Applications:\*\*/g, '**יישומים:**'],
  [/\*\*Note:\*\*/g, '**הערה:**'],
  [/\*\*Units:\*\*/g, '**יחידות:**'],
  [/\*\*Direction:\*\*/g, '**כיוון:**'],
  [/\*\*Magnitude:\*\*/g, '**גודל:**'],
];

function splitParas(text) {
  if (!text) return [];
  return text.split(/\n\n+/).map((p) => p.trim()).filter(Boolean);
}

function normalizePara(p) {
  return p
    .replace(/\s+/g, ' ')
    .replace(/[""]/g, '"')
    .trim()
    .toLowerCase();
}

function hebrewCharRatio(text) {
  if (!text) return 0;
  const he = (text.match(/[\u0590-\u05FF]/g) || []).length;
  const lat = (text.match(/[a-zA-Z]/g) || []).length;
  return he / (he + lat + 1);
}

function dedupeParagraphs(text) {
  const paras = splitParas(text);
  const seen = new Set();
  const kept = [];
  for (const p of paras) {
    const key = normalizePara(p);
    if (key.length < 30) {
      kept.push(p);
      continue;
    }
    if (seen.has(key)) continue;
    seen.add(key);
    kept.push(p);
  }
  return kept.join('\n\n').trim();
}

function stripBoilerplate(text) {
  let out = text ?? '';
  for (const re of BOILERPLATE_PATTERNS) {
    out = out.replace(re, '');
  }
  return out.trim();
}

function fixHePhrases(text) {
  let out = text ?? '';
  for (const [re, rep] of HE_PHRASE_FIXES) {
    out = out.replace(re, rep);
  }
  return out.trim();
}

/** Remove paragraphs in HE that duplicate EN (phase-3 append artifact). */
function stripEnDuplicatesFromHe(he, en) {
  if (!he || !en) return he ?? '';
  const enNorm = new Set(splitParas(en).map(normalizePara));
  const heParas = splitParas(he);
  const kept = [];
  for (const p of heParas) {
    const norm = normalizePara(p);
    if (norm.length >= 40 && enNorm.has(norm)) continue;
    // Drop HE paragraphs that are clearly appended EN blocks (low Hebrew, long, in EN)
    if (p.length > 60 && hebrewCharRatio(p) < 0.08 && en.includes(p.slice(0, Math.min(80, p.length)))) {
      continue;
    }
    kept.push(p);
  }
  return kept.join('\n\n').trim();
}

export function cleanBodyEn(text) {
  return dedupeParagraphs(stripBoilerplate(text ?? ''));
}

function translateStructureMarkers(text) {
  return text
    .replace(/\*\*Step (\d+)[^*]*\*\*/g, '**צעד $1:**')
    .replace(/### Move (\d+)/g, '### צעד $1')
    .replace(/\*\*Given:\*\*/g, '**נתון:**')
    .replace(/\*\*Problem:\*\*/g, '**בעיה:**')
    .replace(/\*\*Solution path:\*\*/g, '**דרך פתרון:**')
    .replace(/\*\*Solution:\*\*/g, '**פתרון:**')
    .replace(/\*\*Analysis:\*\*/g, '**ניתוח:**')
    .replace(/\*\*Check:\*\*/g, '**בדיקה:**')
    .replace(/\*\*Verify:\*\*/g, '**אימות:**')
    .replace(/\*\*Intuition:\*\*/g, '**אינטואיציה:**')
    .replace(/\*\*Why this path:\*\*/g, '**למה הנתיב הזה:**')
    .replace(/\*\*The mistake\.\*\*/g, '**הטעות.**')
    .replace(/\*\*Why it's wrong\.\*\*/g, '**למה זה שגוי.**')
    .replace(/\*\*The fix\.\*\*/g, '**התיקון.**')
    .replace(/\*\*By the end of this lesson\*\*/g, '**בסוף השיעור**')
    .replace(/\*\*How to use this section:\*\*/g, '**איך להשתמש בחלק זה:**')
    .replace(/\*\*When to use:\*\*/g, '**מתי להשתמש:**')
    .replace(/\*\*Exam tip:\*\*/g, '**טיפ לבחינה:**')
    .replace(/\*\*Directly:\*\*/g, '**ישירות:**')
    .replace(/\*\*Relationship:\*\*/g, '**קשר:**')
    .replace(/\*\*Properties:\*\*/g, '**תכונות:**')
    .replace(/\*\*Applications:\*\*/g, '**יישומים:**')
    .replace(/\*\*Note:\*\*/g, '**הערה:**')
    .replace(/\*\*Units:\*\*/g, '**יחידות:**')
    .replace(/\*\*Direction:\*\*/g, '**כיוון:**')
    .replace(/\*\*Magnitude:\*\*/g, '**גודל:**')
    .replace(/\*\*Compute\*\*/g, '**חשבו**')
    .replace(/\*\*Find\*\*/g, '**מצאו**')
    .replace(/\*\*Expand\*\*/g, '**פתחו**');
}

function fallbackHeFromEn(en) {
  return fixHePhrases(translateStructureMarkers(cleanBodyEn(en)));
}

export function cleanBodyHe(text, en) {
  const cleanedEn = cleanBodyEn(en ?? '');
  let out = stripEnDuplicatesFromHe(text ?? '', en ?? '');
  out = stripBoilerplate(out);
  out = fixHePhrases(out);
  out = dedupeParagraphs(out);
  if (!out.trim() && cleanedEn.trim()) {
    out = fallbackHeFromEn(cleanedEn);
  }
  return out;
}

function stripMarkdown(text) {
  return (text ?? '')
    .replace(/\$\$[\s\S]*?\$\$/g, ' ')
    .replace(/\$[^$\n]+\$/g, ' ')
    .replace(/[#*_`>\[\]|]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function firstSentences(text, maxWords = 28) {
  const plain = stripMarkdown(text);
  if (!plain) return '';
  const sentences = plain.split(/(?<=[.!?])\s+/).filter(Boolean);
  let out = '';
  let words = 0;
  for (const s of sentences) {
    const w = s.split(/\s+/).filter(Boolean).length;
    if (words + w > maxWords && out) break;
    out = out ? `${out} ${s}` : s;
    words += w;
  }
  return out.trim();
}

function bulletTopics(text, max = 4) {
  const items = [];
  for (const line of (text ?? '').split('\n')) {
    const m = line.match(/^[-*]\s+\*\*([^*]+)\*\*/);
    if (m) items.push(m[1].trim());
    if (items.length >= max) break;
  }
  return items;
}

export function synthesizeSummary(raw, lang) {
  const intro = raw.sections?.find((s) => s.kind === 'intro');
  const theory = raw.sections?.find((s) => s.kind === 'theory' || s.kind === 'definition');
  const body =
    lang === 'he'
      ? intro?.body_he_md || theory?.body_he_md || ''
      : intro?.body_en_md || theory?.body_en_md || '';
  const title = lang === 'he' ? raw.title_he : raw.title_en;
  const lead = firstSentences(body, 22);
  const bullets = bulletTopics(body);
  if (bullets.length >= 2) {
    const joiner = lang === 'he' ? ' — ' : ': ';
    const list = bullets.slice(0, 3).join(lang === 'he' ? ', ' : ', ');
    return `${title}${joiner}${list}.`;
  }
  if (lead) return lead.endsWith('.') ? lead : `${lead}.`;
  return title ?? raw.concept_id ?? '';
}

export function editorialCleanup(raw) {
  const sections = (raw.sections ?? []).map((s) => {
    const body_en_md = cleanBodyEn(s.body_en_md);
    const body_he_md = cleanBodyHe(s.body_he_md, s.body_en_md);
    if (body_en_md === s.body_en_md && body_he_md === s.body_he_md) return s;
    return { ...s, body_en_md, body_he_md };
  });

  const questions = (raw.questions ?? []).map((q) => {
    const explanation_en = cleanBodyEn(q.explanation_en);
    const explanation_he = cleanBodyHe(q.explanation_he, q.explanation_en);
    if (explanation_en === q.explanation_en && explanation_he === q.explanation_he) return q;
    return { ...q, explanation_en, explanation_he };
  });

  let summary_en = raw.summary_en?.trim() ?? '';
  let summary_he = raw.summary_he?.trim() ?? '';
  if (!summary_en) summary_en = synthesizeSummary({ ...raw, sections }, 'en');
  if (!summary_he) summary_he = synthesizeSummary({ ...raw, sections }, 'he');

  return { ...raw, sections, questions, summary_en, summary_he };
}

export function editorialMetrics(raw) {
  let boilerplate = 0;
  let heDup = 0;
  const blob = JSON.stringify(raw);
  if (blob.includes('Why this path')) boilerplate++;
  if (blob.includes('How to use this section')) boilerplate++;
  if (blob.includes('By the end of this lesson')) boilerplate++;
  for (const s of raw.sections ?? []) {
    const he = s.body_he_md ?? '';
    const en = s.body_en_md ?? '';
    if (he.length > 80 && en.length > 80) {
      const probe = en.slice(0, Math.min(100, en.length)).trim();
      if (probe.length > 40 && he.includes(probe)) heDup++;
    }
  }
  return { boilerplate, heDup, missingSummaryHe: !(raw.summary_he ?? '').trim() };
}
