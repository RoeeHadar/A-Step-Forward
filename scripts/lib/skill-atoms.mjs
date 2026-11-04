/**
 * AS-66: skill_atoms must be id strings. Some lesson files once listed question atoms as
 * objects `{id,label_en,label_he}`; the neon driver then sent the object's JSON text as the id,
 * creating junk skill_atoms rows. Policy: COERCE object atoms to their `id` (with a warning);
 * reject (throw) anything that has no usable string id.
 */

/** @returns {string} the atom id */
export function coerceAtomId(atom, where = '', warn = console.warn) {
  if (typeof atom === 'string') return atom;
  if (atom && typeof atom === 'object' && typeof atom.id === 'string' && atom.id.trim()) {
    warn(`[skill-atoms] coerced object atom to id "${atom.id}"${where ? ` (${where})` : ''}`);
    return atom.id;
  }
  throw new TypeError(`[skill-atoms] invalid skill atom ${JSON.stringify(atom)}${where ? ` (${where})` : ''}`);
}

/** Unique atom ids of one normalized lesson: taught (agent_hints) and exercised (questions). */
export function collectLessonAtoms(data, where = '', warn = console.warn) {
  const taught = new Set(
    (data.agent_hints?.skill_atoms_unlocked ?? []).map((a) => coerceAtomId(a, where, warn)),
  );
  const exercised = new Set();
  for (const q of data.questions ?? []) {
    for (const a of q.skill_atoms ?? []) exercised.add(coerceAtomId(a, where, warn));
  }
  return { taught, exercised, all: new Set([...taught, ...exercised]) };
}
