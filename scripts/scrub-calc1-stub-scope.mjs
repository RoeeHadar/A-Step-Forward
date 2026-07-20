#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const IDS = [
  'intermediate_value_theorem',
  'extreme_value_theorem',
  'sequences_monotone_bounded',
  'series_absolute_convergence',
  'convergence_divergence_integrals',
];

function scrub(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/Bagrut/gi, 'course exam')
    .replace(/בגרות/g, 'מבחן קורס')
    .replace(/שאלון\s*\d*/g, 'מבחן קורס')
    .replace(/\bMoE\b/g, 'course')
    .replace(/\b[345]\s*-?\s*units?\b/gi, 'course level')
    .replace(/\b[345]pt\b/gi, 'course')
    .replace(/יחידות לימוד/g, 'רמת קורס')
    .replace(/points on the exam/gi, 'points on the course exam')
    .replace(/exam tip for Bagrut/gi, 'exam tip for the course');
}

function walk(obj) {
  if (Array.isArray(obj)) return obj.map(walk);
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      out[k] = typeof v === 'string' ? scrub(v) : walk(v);
    }
    return out;
  }
  return obj;
}

for (const id of IDS) {
  const fp = path.join(DIR, `${id}.json`);
  const j = walk(JSON.parse(fs.readFileSync(fp, 'utf8')));
  j.math_track = ['university', 'calc1'];
  fs.writeFileSync(fp, `${JSON.stringify(j, null, 2)}\n`);
  console.log('scrubbed', id);
}
