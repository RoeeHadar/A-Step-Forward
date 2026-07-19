#!/usr/bin/env node
/**
 * Build apps/web/src/lib/exam-style-corpus.generated.json from:
 *   1) scripts/seed_data/exam-style/*.json  (authored multipart items)
 *   2) scripts/seed_data/mock_exams/*.json  (extract open multipart questions)
 *
 * All items are ASF-original practice material — never MoE transcripts.
 */
import { readFileSync, writeFileSync, readdirSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');
const examDir = join(root, 'scripts/seed_data/exam-style');
const mockDir = join(root, 'scripts/seed_data/mock_exams');
const outPath = join(root, 'apps/web/src/lib/exam-style-corpus.generated.json');

const GOAL_FROM_SUBJECT = {
  high_school_math_3pt: 'bagrut_math_3',
  high_school_math_4pt: 'bagrut_math_4',
  high_school_math_5pt: 'bagrut_math_5',
  hs_physics: 'bagrut_physics',
  calculus_1: 'calculus1',
  linear_algebra: 'linear_algebra',
  university_physics_1: 'physics1',
};

const LEVEL_FROM_SUBJECT = {
  high_school_math_3pt: '3pt',
  high_school_math_4pt: '4pt',
  high_school_math_5pt: '5pt',
  hs_physics: 'hs_physics',
  calculus_1: 'calc1',
  linear_algebra: 'la',
  university_physics_1: 'uni_physics',
};

function parsePartsFromBody(bodyEn, bodyHe, totalPoints) {
  const en = String(bodyEn ?? '');
  const he = String(bodyHe ?? '');
  const enParts = [...en.matchAll(/\(([a-d])\)\s*([\s\S]*?)(?=\([a-d]\)|$)/gi)];
  const heParts = [...he.matchAll(/[\(（]([אבגד])[\)）]\s*([\s\S]*?)(?=[\(（][אבגד][\)）]|$)/g)];
  if (enParts.length >= 2) {
    const pts = Math.max(1, Math.floor(totalPoints / enParts.length));
    const labels = ['א', 'ב', 'ג', 'ד'];
    return enParts.map((m, i) => ({
      label: labels[i] ?? String.fromCharCode(97 + i),
      body_en: m[2].trim(),
      body_he: (heParts[i]?.[2] ?? m[2]).trim(),
      points: i === enParts.length - 1 ? totalPoints - pts * (enParts.length - 1) : pts,
    }));
  }
  return [
    {
      label: 'א',
      body_en: en.trim() || 'Solve the problem. Show all work.',
      body_he: he.trim() || 'פתרו את השאלה. הראו את כל השלבים.',
      points: totalPoints,
    },
  ];
}

function stemFromBody(body, maxLen = 400) {
  const s = String(body ?? '').trim();
  // Prefer text before first (a)/(א) as shared stem.
  const cut = s.search(/\([aא]\)|（א）/);
  if (cut > 20) return s.slice(0, cut).trim().slice(0, maxLen);
  return s.slice(0, Math.min(maxLen, 220)).trim();
}

function loadAuthored() {
  const items = [];
  let files = [];
  try {
    files = readdirSync(examDir).filter((f) => f.endsWith('.json'));
  } catch {
    return items;
  }
  for (const f of files) {
    const raw = JSON.parse(readFileSync(join(examDir, f), 'utf8'));
    const arr = Array.isArray(raw) ? raw : raw.items ?? [];
    for (const it of arr) {
      if (!it?.id || !it.stem_en || !it.parts?.length) continue;
      items.push({
        ...it,
        source: it.source ?? 'asf_original',
        style_tags: Array.from(new Set([...(it.style_tags ?? []), 'multipart', 'exam_corpus'])),
      });
    }
  }
  return items;
}

const LEVEL_TO_GOAL = {
  '3pt': 'bagrut_math_3',
  '4pt': 'bagrut_math_4',
  '5pt': 'bagrut_math_5',
  hs_physics: 'bagrut_physics',
  calc1: 'calculus1',
  la: 'linear_algebra',
};

/** Hard open drills from content/question-store (single-part → exam-style envelope). */
function loadFromQuestionStore() {
  const items = [];
  const storePath = join(root, 'content/question-store/items.json');
  let raw;
  try {
    raw = JSON.parse(readFileSync(storePath, 'utf8'));
  } catch {
    return items;
  }
  const arr = Array.isArray(raw) ? raw : raw.items ?? [];
  for (const q of arr) {
    if (q.difficulty !== 'hard' && q.difficulty !== 'very_hard') continue;
    if (!['open', 'derivation', 'short_answer'].includes(q.kind)) continue;
    const partStems = Array.isArray(q.parts) ? q.parts : [];
    const stemEn = (q.stem_en || partStems[0]?.stem_en || '').trim();
    const stemHe = (q.stem_he || partStems[0]?.stem_he || '').trim();
    if (stemEn.length < 40 && stemHe.length < 40) continue;
    // Prefer substantial stems (skip trivial one-liners under ~60 chars unless derivation).
    const primary = stemHe.length >= stemEn.length ? stemHe : stemEn;
    if (primary.length < 55 && q.kind !== 'derivation') continue;

    const pl = q.points_level || (Array.isArray(q.math_track) ? q.math_track[q.math_track.length - 1] : null);
    const goal = LEVEL_TO_GOAL[pl] ?? null;
    const parts =
      partStems.length >= 2
        ? partStems.slice(0, 4).map((p, i) => ({
            label: ['א', 'ב', 'ג', 'ד'][i],
            body_en: (p.stem_en || '').trim(),
            body_he: (p.stem_he || p.stem_en || '').trim(),
            points: 8,
          }))
        : [
            {
              label: 'א',
              body_en: stemEn || 'Solve. Show all steps.',
              body_he: stemHe || 'פתרו. הראו את כל השלבים.',
              points: 20,
            },
          ];
    if (parts.some((p) => !p.body_en && !p.body_he)) continue;

    items.push({
      id: `qstore_${q.id}`,
      goal_keys: goal ? [goal] : [],
      concept_ids: [q.concept_id, ...(q.extra_concept_ids || [])].filter(Boolean),
      subject: q.subject === 'physics' ? 'physics' : 'math',
      level: pl || '5pt',
      paper_pattern: 'question_store_hard',
      difficulty: 'hard',
      total_points: parts.reduce((s, p) => s + p.points, 0),
      stem_he: stemHe.slice(0, 400) || parts[0].body_he.slice(0, 200),
      stem_en: stemEn.slice(0, 400) || parts[0].body_en.slice(0, 200),
      parts,
      sample_solution_he: (partStems[0]?.answer_payload?.steps_he || []).join('\n') || '',
      sample_solution_en: (partStems[0]?.answer_payload?.steps_en || []).join('\n') || '',
      rubric_he: 'ניקוד על תהליך מלא ותשובה נכונה',
      rubric_en: 'Credit for complete process and correct answer',
      style_tags: ['exam_corpus', 'from_question_store', parts.length >= 2 ? 'multipart' : 'hard_open'],
      source: 'asf_original',
    });
  }
  return items;
}

function loadFromMocks() {
  const items = [];
  const files = readdirSync(mockDir).filter((f) => f.endsWith('.json') && f !== 'index.json');
  for (const f of files) {
    const paper = JSON.parse(readFileSync(join(mockDir, f), 'utf8'));
    const goal = GOAL_FROM_SUBJECT[paper.subject] ?? null;
    const level = LEVEL_FROM_SUBJECT[paper.subject] ?? '5pt';
    const subject =
      String(paper.subject).includes('physics') ? 'physics' : 'math';
    for (const sec of paper.sections ?? []) {
      for (const q of sec.questions ?? []) {
        if (q.type && q.type !== 'open') continue;
        const total = typeof q.points === 'number' ? q.points : 20;
        const parts = parsePartsFromBody(q.body_en, q.body_he, total);
        if (parts.length < 2 && total < 15) continue; // skip thin items
        const id = `mockextract_${paper.id}_${q.id}`;
        items.push({
          id,
          goal_keys: goal ? [goal] : [],
          concept_ids: [],
          subject,
          level,
          paper_pattern: sec.id ?? 'section',
          difficulty: 'hard',
          total_points: total,
          stem_he: stemFromBody(q.body_he),
          stem_en: stemFromBody(q.body_en),
          parts,
          sample_solution_he: q.sample_solution_he ?? '',
          sample_solution_en: q.sample_solution_en ?? '',
          rubric_he: q.rubric_he ?? '',
          rubric_en: q.rubric_en ?? '',
          style_tags: ['multipart', 'exam_corpus', 'from_mock_paper'],
          source: 'asf_original',
        });
      }
    }
  }
  return items;
}

function main() {
  const authored = loadAuthored();
  const extracted = loadFromMocks();
  const fromStore = loadFromQuestionStore();
  const byId = new Map();
  // Priority: authored > mock extract > question-store hard opens.
  for (const it of [...fromStore, ...extracted, ...authored]) {
    byId.set(it.id, it);
  }
  const items = [...byId.values()];
  const byGoal = {};
  for (const it of items) {
    for (const g of it.goal_keys?.length ? it.goal_keys : ['_untagged']) {
      byGoal[g] = (byGoal[g] ?? 0) + 1;
    }
  }
  const payload = {
    generated_at: new Date().toISOString(),
    count: items.length,
    by_goal: byGoal,
    items,
  };
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, JSON.stringify(payload, null, 2), 'utf8');
  console.log(`Wrote ${items.length} exam-style items → ${outPath}`);
  console.log('By goal:', byGoal);
}

main();
