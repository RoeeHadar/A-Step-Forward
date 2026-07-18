#!/usr/bin/env node
/**
 * Per-source-tier ingestion for the question store.
 *
 * Enforces the source-tier policy decided in the plan:
 *   - moe_meyda  : official MoE Meyda exams -> stored VERBATIM (license
 *                  public-official), official answer keys retained as verifier
 *                  ground truth, display_publicly allowed.
 *   - wikibooks / motib / openclass : copyleft or no-license -> STYLE-ONLY.
 *                  We never store their text; we emit metadata-only "seeds"
 *                  (concept/atoms/difficulty/kind) that the clean-room generator
 *                  may use as inspiration.
 *
 * Staging layout (you drop transcribed JSON here):
 *   content/question-sources/<tier>/*.json   (array of raw source items)
 * Outputs:
 *   content/question-store/ingested/<tier>.json  (verbatim store items)
 *   content/question-store/seeds/<tier>.json     (metadata-only generation seeds)
 *
 * Raw source item shape (see content/question-sources/README.md).
 *
 * Usage:
 *   node scripts/ingest-question-sources.mjs                 # all staged tiers
 *   node scripts/ingest-question-sources.mjs --tier=moe_meyda
 */
import fs from 'node:fs';
import path from 'node:path';
import { assertStorable } from './lib/question-store-io.mjs';

const SOURCES_DIR = 'content/question-sources';
const INGESTED_DIR = 'content/question-store/ingested';
const SEEDS_DIR = 'content/question-store/seeds';

const VERBATIM_TIERS = { moe_meyda: { license: 'public-official', source: 'moe_meyda' } };
const STYLE_ONLY_TIERS = new Set(['wikibooks', 'motib', 'openclass']);

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}

function readTierRaw(tier) {
  const dir = path.join(SOURCES_DIR, tier);
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .flatMap((f) => {
      const parsed = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
      return Array.isArray(parsed) ? parsed : [parsed];
    });
}

/** Verbatim tier -> store items (license public-official). */
function toStoreItem(raw, tier) {
  const cfg = VERBATIM_TIERS[tier];
  const part = {
    ord: 1,
    kind: raw.kind,
    difficulty: raw.difficulty,
    stem_en: raw.stem_en ?? '',
    stem_he: raw.stem_he ?? '',
    answer_payload: raw.answer_payload ?? null,
    explanation_en: raw.explanation_en ?? '',
    explanation_he: raw.explanation_he ?? '',
    skill_atoms: raw.skill_atoms ?? [],
    ...(raw.verify ? { verify: raw.verify } : {}),
  };
  const item = {
    concept_id: raw.concept_id,
    subject: raw.subject ?? 'math',
    level: raw.level ?? 'high_school',
    math_track: raw.math_track ?? ['5pt'],
    points_level: raw.points_level ?? '5pt',
    kind: raw.kind,
    difficulty: raw.difficulty,
    stem_en: raw.parts ? (raw.stem_en ?? '') : '',
    stem_he: raw.parts ? (raw.stem_he ?? '') : '',
    parts: raw.parts ?? [part],
    skill_atoms: raw.skill_atoms ?? [],
    answer_payload: raw.answer_payload ?? null,
    source: cfg.source,
    source_ref: raw.source_ref ?? null,
    license: cfg.license,
    provenance: {
      tier,
      official_answer: raw.official_answer ?? null,
      transcriber: raw.transcriber ?? 'assisted',
    },
    display_publicly: Boolean(raw.display_publicly),
    verification_status: 'unverified',
  };
  assertStorable(item); // license/kind/parts safety gate
  return item;
}

/** Style-only tier -> metadata-only generation seed (NO source text stored). */
function toSeed(raw, tier) {
  return {
    concept_id: raw.concept_id,
    skill_atoms: raw.skill_atoms ?? [],
    difficulty: raw.difficulty ?? 'medium',
    kind: raw.kind ?? 'short_answer',
    inspiration_tier: tier,
    note: 'style-only: generate an ORIGINAL item; do not reproduce source text',
  };
}

function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

function main() {
  const onlyTier = args.get('tier') && args.get('tier') !== 'true' ? args.get('tier') : null;
  const tiers = onlyTier ? [onlyTier] : [...Object.keys(VERBATIM_TIERS), ...STYLE_ONLY_TIERS];

  let totalStored = 0;
  let totalSeeds = 0;
  let anyStaged = false;

  for (const tier of tiers) {
    const raw = readTierRaw(tier);
    if (raw.length === 0) continue;
    anyStaged = true;

    if (VERBATIM_TIERS[tier]) {
      const items = raw.map((r) => toStoreItem(r, tier));
      writeJson(path.join(INGESTED_DIR, `${tier}.json`), items);
      totalStored += items.length;
      console.log(`[${tier}] ${items.length} verbatim store items -> ${INGESTED_DIR}/${tier}.json`);
      console.log(`  next: node scripts/pipeline-run.mjs --concept=<id> --generated=${INGESTED_DIR}/${tier}.json`);
    } else if (STYLE_ONLY_TIERS.has(tier)) {
      const seeds = raw.map((r) => toSeed(r, tier));
      writeJson(path.join(SEEDS_DIR, `${tier}.json`), seeds);
      totalSeeds += seeds.length;
      console.log(`[${tier}] ${seeds.length} STYLE-ONLY seeds (no verbatim text) -> ${SEEDS_DIR}/${tier}.json`);
    } else {
      console.log(`[${tier}] unknown tier — skipped`);
    }
  }

  if (!anyStaged) {
    console.log('No staged sources found under', SOURCES_DIR);
    console.log('Stage transcribed JSON per content/question-sources/README.md, then re-run.');
    console.log('Tiers: moe_meyda (verbatim), wikibooks/motib/openclass (style-only).');
    return;
  }
  console.log(`\nDone. verbatim items=${totalStored}, style-only seeds=${totalSeeds}`);
}

main();
