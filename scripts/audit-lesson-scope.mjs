#!/usr/bin/env node
/**
 * audit-lesson-scope — curriculum-track-contract leakage + required ownership gate (v2).
 *
 * Usage:
 *   node scripts/audit-lesson-scope.mjs --strict
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LESSONS_DIR = path.join(ROOT, 'scripts/seed_data/lessons');
const CONTRACT_PATH = path.join(ROOT, 'scripts/seed_data/curriculum-track-contract.json');

const PT = ['3pt', '4pt', '5pt'];
const TRACK_SUFFIX = {
  '3pt': ['__3pt', '_3pt'],
  '4pt': ['__4pt', '_4pt'],
  '5pt': ['__5pt', '_5pt'],
  university: ['__uni', '_uni', '__university', '_university'],
  hs_physics: ['__hs_physics', '_hs_physics'],
  makhina: ['__makhina', '_makhina'],
};

const args = new Map();
for (const a of process.argv.slice(2)) {
  if (!a.startsWith('--')) continue;
  const [k, v] = a.slice(2).split('=');
  args.set(k, v ?? 'true');
}
const strict = args.has('strict');
const asJson = args.get('json') === 'true';
const only =
  args.get('only') && args.get('only') !== 'true'
    ? new Set(args.get('only').split(',').map((s) => s.trim()))
    : null;

function loadContract() {
  return JSON.parse(fs.readFileSync(CONTRACT_PATH, 'utf8'));
}

function loadLessons() {
  return fs
    .readdirSync(LESSONS_DIR)
    .filter((f) => f.endsWith('.json'))
    .map((f) => {
      const lesson = JSON.parse(fs.readFileSync(path.join(LESSONS_DIR, f), 'utf8'));
      const fileId = f.replace(/\.json$/, '');
      return { file: f, id: fileId, lesson };
    });
}

function flattenText(lesson) {
  const parts = [];
  const push = (v) => {
    if (v == null) return;
    if (typeof v === 'string') parts.push(v);
    else if (typeof v === 'number' || typeof v === 'boolean') parts.push(String(v));
    else if (Array.isArray(v)) v.forEach(push);
    else if (typeof v === 'object') Object.values(v).forEach(push);
  };
  push(lesson);
  return parts.join('\n');
}

function tracksOf(lesson) {
  return Array.isArray(lesson.math_track) ? lesson.math_track.map(String) : [];
}

function isFivePtLesson(lesson) {
  const tracks = tracksOf(lesson);
  if (tracks.includes('5pt')) return true;
  if (lesson.level === 'university') return false;
  const id = String(lesson.concept_id || '');
  return /(?:__|_)5pt$/.test(id);
}

function isUniversityLesson(lesson) {
  if (lesson.level === 'university') return true;
  const tracks = tracksOf(lesson);
  if (tracks.includes('university') || tracks.includes('calc1') || tracks.includes('uni')) return true;
  const id = String(lesson.concept_id || '');
  return /(?:__|_)(?:uni|university)$/.test(id);
}

function canonicalBase(id) {
  return String(id || '')
    .replace(/__(?:3pt|4pt|5pt|uni|university|makhina|hs_physics)$/, '')
    .replace(/_(?:3pt|4pt|5pt|uni|university|makhina)$/, '');
}

function ptCount(tracks) {
  return tracks.filter((t) => PT.includes(t)).length;
}

function lessonServesTrack(entry, track) {
  const { id, lesson } = entry;
  const tracks = tracksOf(lesson);
  const cid = lesson.concept_id || id;

  if (track === 'university') {
    if (!isUniversityLesson(lesson)) return false;
    if (/(?:__|_)(?:uni|university)$/.test(id) || /(?:__|_)(?:uni|university)$/.test(cid)) return true;
    // Explicit uni / calc1 / LA / analysis tracks count as university-owned
    const uniish = tracks.filter((t) =>
      ['university', 'uni', 'calc1', 'calc2', 'analysis', 'la', 'statistics', 'stats'].includes(t),
    );
    if (uniish.length >= 1 && ptCount(tracks) === 0) return true;
    // Polluted 5pt+university: not clean uni ownership
    if (ptCount(tracks) > 0) return false;
    if (lesson.level === 'university') return true;
    return false;
  }

  if (track === 'hs_physics') {
    if (lesson.subject !== 'physics') return false;
    if (lesson.level === 'university') return false;
    if (tracks.includes('hs_physics') && tracks.length === 1) return true;
    if (tracks.length === 0 && lesson.level === 'high_school') return true;
    return false;
  }

  if (track === 'makhina') {
    if (tracks.includes('makhina') && tracks.filter((t) => t === 'makhina' || PT.includes(t)).length === 1)
      return true;
    if (/makhina/.test(id) && (tracks.includes('makhina') || tracks.length === 0)) return true;
    return false;
  }

  if (tracks.includes(track) && ptCount(tracks) === 1) return true;

  const suffixes = TRACK_SUFFIX[track] || [];
  if (suffixes.some((s) => id.endsWith(s) || cid.endsWith(s))) {
    if (tracks.length === 0) return false;
    return tracks.includes(track) && ptCount(tracks) <= 1;
  }

  if (tracks.length === 1 && tracks[0] === track) {
    return !/(?:__|_)(?:3pt|4pt|5pt|uni|university)$/.test(id) || id.endsWith(`__${track}`) || id.endsWith(`_${track}`);
  }
  return false;
}

function matchesConcept(entry, concept) {
  const base = canonicalBase(entry.id);
  const cid = entry.lesson.concept_id || base;
  return cid === concept || base === concept || entry.id === concept || canonicalBase(cid) === concept;
}

function audit(contract, entries) {
  const errors = [];
  const warnings = [];

  const fivePtRules = (contract.five_pt_denylist || []).map((r) => ({
    ...r,
    re: new RegExp(r.pattern, 'iu'),
  }));
  const uniRules = (contract.university_denylist || []).map((r) => ({
    ...r,
    re: new RegExp(r.pattern, 'iu'),
  }));

  const moeCore = new Set(contract.moe_core_concepts || []);
  const filtered = only
    ? entries.filter((e) => only.has(e.id) || only.has(canonicalBase(e.id)))
    : entries;

  for (const { id, file, lesson } of filtered) {
    const text = flattenText(lesson);

    if (isFivePtLesson(lesson) && !isUniversityLesson(lesson)) {
      for (const rule of fivePtRules) {
        if (rule.re.test(text)) {
          errors.push({ code: 'five_pt_denylist', id, file, rule: rule.id, note: rule.note });
        }
      }
    }

    if (isUniversityLesson(lesson)) {
      for (const rule of uniRules) {
        if (rule.re.test(text)) {
          errors.push({ code: 'university_denylist', id, file, rule: rule.id, note: rule.note });
        }
      }
    }
  }

  // Single-track bans
  const singleTrackBases = new Set();
  if (contract.matrix_basics_single_track || contract.single_track_moe_core) {
    for (const id of moeCore) singleTrackBases.add(id);
    for (const list of Object.values(contract.required_basics || {})) {
      for (const id of list) singleTrackBases.add(id);
    }
  }

  for (const { id, file, lesson } of filtered) {
    const base = canonicalBase(id);
    const cid = lesson.concept_id || base;
    const ptTracks = tracksOf(lesson).filter((t) => PT.includes(t));

    if (contract.single_track_moe_core && (moeCore.has(base) || moeCore.has(cid) || singleTrackBases.has(base))) {
      if (ptTracks.length > 1) {
        errors.push({
          code: 'moe_core_multi_track_leak',
          id,
          file,
          tracks: ptTracks,
          note: 'MoE-core lessons must have a single primary Bagrut track',
        });
      }
    }

    if (contract.single_track_physics && lesson.subject === 'physics') {
      const tracks = tracksOf(lesson);
      const physTracks = tracks.filter((t) => t === 'hs_physics' || t === 'university' || t === 'makhina');
      if (physTracks.length > 1) {
        errors.push({
          code: 'physics_multi_track_leak',
          id,
          file,
          tracks: physTracks,
          note: 'Physics lessons must have a single primary track',
        });
      }
    }

    if (contract.single_track_makhina && (/makhina/.test(id) || tracksOf(lesson).includes('makhina'))) {
      const tracks = tracksOf(lesson);
      if (ptTracks.length > 0 && tracks.includes('makhina')) {
        errors.push({
          code: 'makhina_multi_track_leak',
          id,
          file,
          tracks,
          note: 'Makhina lessons must not also claim Bagrut pt tracks',
        });
      }
    }
  }

  function requireOwners(map, label) {
    for (const [track, concepts] of Object.entries(map || {})) {
      for (const concept of concepts) {
        const owners = entries.filter((e) => matchesConcept(e, concept) && lessonServesTrack(e, track));
        if (owners.length === 0) {
          errors.push({
            code: 'required_missing',
            track,
            concept,
            note: `No track-owned lesson for ${concept} @ ${track} (${label})`,
          });
        }
      }
    }
  }

  requireOwners(contract.required_basics, 'required_basics');
  requireOwners(contract.physics_required, 'physics_required');
  requireOwners(contract.makhina_required, 'makhina_required');

  return { errors, warnings };
}

function main() {
  const contract = loadContract();
  const entries = loadLessons();
  const { errors, warnings } = audit(contract, entries);

  if (asJson) {
    console.log(JSON.stringify({ errors, warnings, errorCount: errors.length }, null, 2));
  } else {
    console.log(`audit-lesson-scope: ${errors.length} error(s), ${warnings.length} warning(s)`);
    for (const e of errors) {
      console.log(
        `  [E] ${e.code}: ${e.id || `${e.concept}@${e.track}`} ${e.rule ? `(${e.rule})` : ''} — ${e.note || ''}`,
      );
    }
  }

  if (strict && errors.length > 0) process.exit(1);
}

main();
