#!/usr/bin/env node
/**
 * Generate/update concept hub notes in obsidian-vault/concepts/ from kg-data.json.
 *
 * Usage:
 *   node scripts/sync-obsidian-concepts.mjs
 *   node scripts/sync-obsidian-concepts.mjs --dry-run
 *
 * Preserves user content below "## Expansion notes" in existing notes.
 */
import fs from 'node:fs';
import path from 'node:path';
import { resolveConceptAlias, buildReverseAliasIndex } from './lib/concept-aliases.mjs';

const ROOT = path.resolve(import.meta.dirname, '..');
const KG_PATH = path.join(ROOT, 'apps/web/src/lib/kg-data.json');
const CONCEPTS_DIR = path.join(ROOT, 'obsidian-vault/concepts');
const LESSONS_DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const PROGRESS_PATH = path.join(ROOT, 'scripts/.cursor-expansion-progress.json');

function loadProgress() {
  if (!fs.existsSync(PROGRESS_PATH)) return { completed: [] };
  return JSON.parse(fs.readFileSync(PROGRESS_PATH, 'utf8'));
}

function lessonPathFor(lessonId) {
  return path.join(LESSONS_DIR, `${lessonId}.json`);
}

function loadLesson(lessonId) {
  const p = lessonPathFor(lessonId);
  if (!fs.existsSync(p)) return null;
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch {
    return null;
  }
}

function resolveLesson(conceptId) {
  const lessonId = resolveConceptAlias(conceptId);
  const lesson = loadLesson(lessonId);
  return { lessonId, lesson, aliased: lessonId !== conceptId };
}

function expansionStatus(conceptId, completed, lesson) {
  if (completed.has(conceptId)) return 'done';
  if (!lesson) return 'missing-lesson';
  return 'todo';
}

function dataCompleteness(concept, lesson) {
  const hasKgAtoms = (concept.skill_atoms?.length ?? 0) > 0;
  const hasKgScope = Object.keys(concept.level_scope ?? {}).length > 0;
  if (hasKgAtoms && hasKgScope) return 'full';
  if (lesson) return 'kg-sparse';
  return 'syllabus-only';
}

function wikilink(id) {
  return id ? `[[concepts/${id}|${id}]]` : '—';
}

function formatLevelScope(scope) {
  if (!scope || typeof scope !== 'object' || Object.keys(scope).length === 0) {
    return '_No level scope in KG._';
  }
  return Object.entries(scope)
    .map(([level, text]) => `- **${level}:** ${text}`)
    .join('\n');
}

function formatSkillAtoms(atoms) {
  if (!Array.isArray(atoms) || atoms.length === 0) return '_None listed in KG._';
  return atoms.map((a) => `- ${a}`).join('\n');
}

function formatLessonOverview(lesson) {
  if (!lesson) return '';
  const lines = ['## Lesson overview', ''];
  if (lesson.title_en) lines.push(`**Lesson:** ${lesson.title_en}`);
  if (lesson.title_he) lines.push(`**HE:** ${lesson.title_he}`);
  if (lesson.summary_en) {
    lines.push('');
    lines.push(lesson.summary_en);
  }
  if (lesson.summary_he) {
    lines.push('');
    lines.push(`> ${lesson.summary_he}`);
  }
  const qCount = lesson.questions?.length ?? 0;
  const sCount = lesson.sections?.length ?? 0;
  lines.push('');
  lines.push(`_${sCount} sections · ${qCount} questions in authored JSON._`);
  lines.push('');
  return lines.join('\n');
}

function formatLessonSections(lesson) {
  if (!lesson?.sections?.length) return '';
  const lines = ['## Lesson sections', ''];
  for (const s of lesson.sections) {
    const title = s.title_en ?? s.id ?? s.kind;
    lines.push(`- **${s.kind}:** ${title}`);
  }
  lines.push('');
  return lines.join('\n');
}

function formatRelatedConcepts(conceptId, lessonId, reverseAliases) {
  const siblings = (reverseAliases.get(lessonId) ?? []).filter((id) => id !== conceptId);
  if (siblings.length === 0) return '';
  const lines = [
    '## Related KG concepts (same lesson)',
    '',
    '_These syllabus concepts alias to the same authored lesson JSON._',
    '',
    siblings.map((id) => `- ${wikilink(id)}`).join('\n'),
    '',
  ];
  return lines.join('\n');
}

function formatDataGapNote(concept, lesson, aliased, lessonId) {
  if (lesson) return '';
  const lines = [
    '## Data gap',
    '',
    '_No authored lesson JSON found for this KG concept (even after alias lookup)._',
    '',
    `- Expected: \`scripts/seed_data/lessons/${concept.id}.json\``,
  ];
  if (aliased) {
    lines.push(`- Alias target tried: \`scripts/seed_data/lessons/${lessonId}.json\` (also missing)`);
  }
  lines.push(
    '',
    '_This KG entry is syllabus scaffolding — enrich `kg-data.json` or author a matching lesson._',
    '',
  );
  return lines.join('\n');
}

function preserveTail(existing) {
  const marker = '## Expansion notes';
  const idx = existing.indexOf(marker);
  if (idx === -1) return '';
  return existing.slice(idx);
}

function buildNote(concept, status, meta) {
  const { lesson, lessonId, aliased, reverseAliases } = meta;
  const prereqLinks =
    (concept.prerequisites ?? []).length > 0
      ? (concept.prerequisites ?? []).map((p) => wikilink(p)).join(', ')
      : '—';

  const points = (concept.points_levels ?? []).map((p) => `"${p}"`).join(', ');
  const completeness = dataCompleteness(concept, lesson);
  const lessonJsonPath = `scripts/seed_data/lessons/${lessonId}.json`;

  const fm = [
    '---',
    `concept_id: "${concept.id}"`,
    `name: "${concept.name.replace(/"/g, '\\"')}"`,
    `name_he: "${(concept.name_he ?? '').replace(/"/g, '\\"')}"`,
    `subject: ${concept.subject}`,
    `level: ${concept.level}`,
    `bagrut_chapter: ${concept.bagrut_chapter ?? 'null'}`,
    `points_levels: [${points}]`,
    `expansion_status: ${status}`,
    `data_completeness: ${completeness}`,
    `lesson_id: "${lessonId}"`,
    `lesson_aliased: ${aliased}`,
    `lesson_json: ${lessonJsonPath}`,
    `prerequisites: [${(concept.prerequisites ?? []).map((p) => `"${p}"`).join(', ')}]`,
    'tags:',
    `  - concept/${concept.subject}`,
    `  - status/${status}`,
    `  - completeness/${completeness}`,
    '---',
    '',
    `# ${concept.name}`,
    '',
    `**HE:** ${concept.name_he ?? ''}`,
    '',
    formatLessonOverview(lesson),
    formatDataGapNote(concept, lesson, aliased, lessonId),
    '## Prerequisites',
    '',
    prereqLinks,
    '',
    '## Skill atoms',
    '',
    formatSkillAtoms(concept.skill_atoms),
    '',
    '## Level scope',
    '',
    formatLevelScope(concept.level_scope),
    '',
    formatLessonSections(lesson),
    formatRelatedConcepts(concept.id, lessonId, reverseAliases),
    '## Links',
    '',
    `- Lesson JSON: \`${lessonJsonPath}\`${aliased ? ` _(alias from \`${concept.id}\`)_` : ''}`,
    '- Aliases: `apps/web/src/lib/concept-aliases.ts`',
    '- Research: [[research/README|Research index]]',
    '- Checklist: [[curriculum/goren-geva-checklist|Goren/Geva]]',
    '- Depth guide: `docs/bagrut-math-depth.md` (repo)',
    '',
    '## Expansion notes',
    '',
    '<!-- Queue reasons, Hebrew parity issues, draft links -->',
    '',
    '## QA feedback',
    '',
    '<!-- Links to .cursor/qa-loop reports -->',
    '',
  ].join('\n');

  return fm;
}

const dryRun = process.argv.includes('--dry-run');
const kg = JSON.parse(fs.readFileSync(KG_PATH, 'utf8'));
const completed = new Set(loadProgress().completed ?? []);
const reverseAliases = buildReverseAliasIndex();

if (!dryRun) fs.mkdirSync(CONCEPTS_DIR, { recursive: true });

let created = 0;
let updated = 0;
let skipped = 0;
const stats = { full: 0, 'kg-sparse': 0, 'syllabus-only': 0 };

for (const concept of kg.concepts) {
  const outPath = path.join(CONCEPTS_DIR, `${concept.id}.md`);
  const { lessonId, lesson, aliased } = resolveLesson(concept.id);
  const status = expansionStatus(concept.id, completed, lesson);
  const meta = { lesson, lessonId, aliased, reverseAliases };
  const body = buildNote(concept, status, meta);
  stats[dataCompleteness(concept, lesson)]++;

  if (fs.existsSync(outPath)) {
    const existing = fs.readFileSync(outPath, 'utf8');
    const tail = preserveTail(existing);
    const merged =
      tail && tail.includes('## Expansion notes')
        ? body.replace(/## Expansion notes[\s\S]*$/, tail.trimEnd() + '\n')
        : body;
    if (merged === existing) {
      skipped++;
      continue;
    }
    if (!dryRun) fs.writeFileSync(outPath, merged, 'utf8');
    updated++;
  } else {
    if (!dryRun) fs.writeFileSync(outPath, body, 'utf8');
    created++;
  }
}

console.log(
  `sync-obsidian-concepts: ${kg.concepts.length} concepts — created ${created}, updated ${updated}, unchanged ${skipped}${dryRun ? ' (dry-run)' : ''}`,
);
console.log(
  `  completeness: full=${stats.full}, kg-sparse=${stats['kg-sparse']}, syllabus-only=${stats['syllabus-only']}`,
);
