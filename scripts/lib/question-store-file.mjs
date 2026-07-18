/**
 * File-backed question store — a drop-in for question-store-io.mjs when no Neon
 * DATABASE_URL is available (local pipeline runs, CI dry-runs). Persists to a
 * single JSON array; ids are the same deterministic content hashes, so switching
 * to the DB store later re-uses identical ids (idempotent migration).
 */
import fs from 'node:fs';
import path from 'node:path';
import { _internal } from './question-store-io.mjs';

const { normalizeForStore, VERIFIED_STATUSES } = _internal;

export function loadStore(storePath) {
  if (!fs.existsSync(storePath)) return [];
  const parsed = JSON.parse(fs.readFileSync(storePath, 'utf8'));
  return Array.isArray(parsed) ? parsed : [];
}

function writeStore(storePath, items) {
  fs.mkdirSync(path.dirname(storePath), { recursive: true });
  fs.writeFileSync(storePath, JSON.stringify(items, null, 2) + '\n', 'utf8');
}

/** Upsert by deterministic id; enforces the license policy via normalizeForStore. */
export function upsertItemsFile(storePath, rawItems) {
  const existing = loadStore(storePath);
  const byId = new Map(existing.map((it) => [it.id, it]));
  const ids = [];
  for (const raw of rawItems) {
    const it = normalizeForStore(raw);
    // preserve `verify` metadata (used by the CAS runner) if present
    if (raw.parts) it.parts = raw.parts;
    it.updated_at = new Date().toISOString();
    byId.set(it.id, { ...byId.get(it.id), ...it });
    ids.push(it.id);
  }
  writeStore(storePath, [...byId.values()]);
  return ids;
}

export function setVerificationStatusFile(storePath, id, status, verification = null) {
  const items = loadStore(storePath);
  const it = items.find((x) => x.id === id);
  if (!it) return false;
  it.verification_status = status;
  it.verification = verification;
  it.updated_at = new Date().toISOString();
  writeStore(storePath, items);
  return true;
}

export function queryItemsForBakingFile(storePath, { conceptId, gradedOnly = true } = {}) {
  return loadStore(storePath)
    .filter((it) => it.concept_id === conceptId)
    .filter((it) => !gradedOnly || VERIFIED_STATUSES.includes(it.verification_status))
    .sort((a, b) => `${a.difficulty}${a.kind}`.localeCompare(`${b.difficulty}${b.kind}`));
}

export function countByStatusFile(storePath, conceptId) {
  const counts = {};
  for (const it of loadStore(storePath)) {
    if (conceptId && it.concept_id !== conceptId) continue;
    counts[it.verification_status] = (counts[it.verification_status] ?? 0) + 1;
  }
  return counts;
}
