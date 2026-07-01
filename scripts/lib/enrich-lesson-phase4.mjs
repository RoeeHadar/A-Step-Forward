/**
 * Phase 4: Add why_matters sections from KG cross-edges + agent_hints.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CROSS_EDGES_PATH = path.join(__dirname, '../../apps/web/src/lib/kg-cross-edges.json');
const KG_PATH = path.join(__dirname, '../../apps/web/src/lib/kg-data.json');

let crossEdgesCache = null;
let kgByIdCache = null;

function loadCrossEdges() {
  if (crossEdgesCache) return crossEdgesCache;
  const data = JSON.parse(fs.readFileSync(CROSS_EDGES_PATH, 'utf8'));
  crossEdgesCache = data.edges ?? [];
  return crossEdgesCache;
}

function loadKgById() {
  if (kgByIdCache) return kgByIdCache;
  const data = JSON.parse(fs.readFileSync(KG_PATH, 'utf8'));
  kgByIdCache = data.byId ?? {};
  return kgByIdCache;
}

function conceptLabel(id, lang = 'en') {
  const c = loadKgById()[id];
  if (!c) return id.replace(/_/g, ' ');
  return lang === 'he' && c.name_he ? c.name_he : c.name;
}

function buildWhyMattersBodies(conceptId, raw) {
  const edges = loadCrossEdges();
  const asSrc = edges.filter((e) => e.src === conceptId).slice(0, 3);
  const asDst = edges.filter((e) => e.dst === conceptId).slice(0, 2);
  const nextRec = raw.agent_hints?.next_recommended ?? [];

  const linesEn = [
    'This topic is not isolated — it connects to the rest of your learning path on A Step Forward.',
  ];
  const linesHe = ['נושא זה אינו מבודד — הוא מחובר לשאר מסלול הלימוד שלך ב-A Step Forward.'];

  if (asSrc.length) {
    linesEn.push('', '**You will use this to unlock:**');
    linesHe.push('', '**תשתמשו בזה כדי להתקדם ל:**');
    for (const e of asSrc) {
      const note = e.note ? ` — ${e.note}` : '';
      linesEn.push(`- \`concept:${e.dst}\` **${conceptLabel(e.dst, 'en')}** (${e.relation})${note}`);
      linesHe.push(`- \`concept:${e.dst}\` **${conceptLabel(e.dst, 'he')}** (${e.relation})${note}`);
    }
  }

  if (asDst.length) {
    linesEn.push('', '**Builds on:**');
    linesHe.push('', '**מבוסס על:**');
    for (const e of asDst) {
      linesEn.push(`- \`concept:${e.src}\` **${conceptLabel(e.src, 'en')}**`);
      linesHe.push(`- \`concept:${e.src}\` **${conceptLabel(e.src, 'he')}**`);
    }
  }

  if (!asSrc.length && !asDst.length && nextRec.length) {
    linesEn.push('', '**Recommended next topics:**');
    linesHe.push('', '**נושאים מומלצים להמשך:**');
    for (const id of nextRec.slice(0, 4)) {
      linesEn.push(`- \`concept:${id}\` **${conceptLabel(id, 'en')}**`);
      linesHe.push(`- \`concept:${id}\` **${conceptLabel(id, 'he')}**`);
    }
  }

  linesEn.push(
    '',
    '**Why it matters for exams:** Bagrut and university courses reward *transfer* — applying this idea in a new context. When you study, always ask: "Where else did I see this pattern?"',
  );
  linesHe.push(
    '',
    '**למה זה חשוב לבחינות:** בבגרות ובאוניברסיטה מעריכים *העברה* — יישום הרעיון בהקשר חדש. בזמן לימוד, שאלו תמיד: "איפה עוד ראיתי את הדפוס הזה?"',
  );

  return {
    body_en_md: linesEn.join('\n'),
    body_he_md: linesHe.join('\n'),
  };
}

export function enrichPhase4(raw) {
  const conceptId = raw.concept_id ?? raw.id;
  if ((raw.sections ?? []).some((s) => s.kind === 'why_matters')) {
    return raw;
  }

  const { body_en_md, body_he_md } = buildWhyMattersBodies(conceptId, raw);
  const whySection = {
    id: 'why_matters',
    kind: 'why_matters',
    title_en: 'Why it matters',
    title_he: 'למה זה חשוב',
    body_en_md,
    body_he_md,
  };

  const sections = [...(raw.sections ?? [])];
  const insertBefore = sections.findIndex((s) => s.kind === 'before_exam');
  const idx = insertBefore >= 0 ? insertBefore : sections.findIndex((s) => s.kind === 'summary');
  const at = idx >= 0 ? idx : sections.length;
  sections.splice(at, 0, whySection);

  return { ...raw, sections };
}
