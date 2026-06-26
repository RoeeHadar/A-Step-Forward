/**
 * Learning-plan path planner.
 *
 * Walks the combined knowledge graph (per-concept `prerequisites` from
 * `kg-data.json` plus directed cross-subject edges from `kg_edges`) backwards
 * from a learner's goal concept, weighing each prerequisite by:
 *
 *   - whether the learner has an authored lesson for it (`hasLesson`),
 *   - the learner's per-skill-atom mastery from `skill_practice`, and
 *   - the edge weight from `kg_edges` (cross-subject links can be soft).
 *
 * Returns a sequenced path so the Curriculum Designer and Coach can present
 * "your next concrete step" — and so the Progress Analyzer can do root-cause
 * diagnosis ("you keep missing kinematics_2d problems because vectors_2d is
 * at 35% mastery and you've never practiced the trigonometry_ratios atoms it
 * depends on").
 */
import 'server-only';
import { neon } from '@neondatabase/serverless';
import kg from '@/lib/kg-data.json';
import crossEdges from '@/lib/kg-cross-edges.json';

const databaseUrl = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
const sql = databaseUrl ? neon(databaseUrl) : null;

interface KgConceptRow {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  prerequisites: string[];
}
const kgConcepts: KgConceptRow[] = (kg as { concepts: KgConceptRow[] }).concepts;
const kgById = new Map(kgConcepts.map((c) => [c.id, c]));

interface CrossEdge {
  src: string;
  dst: string;
  relation: string;
  weight?: number;
  note?: string;
}
const crossEdgesArr: CrossEdge[] = (crossEdges as { edges: CrossEdge[] }).edges;
// Pre-index edges by destination so we can compute "what does X depend on?"
// in O(1). Per-subject prereqs from kg-data are merged with the cross-subject
// edges where relation = "prereq" or "generalizes" (both indicate the source
// concept is needed before the destination concept can be mastered).
const edgesByDst = new Map<string, CrossEdge[]>();
for (const e of crossEdgesArr) {
  if (e.relation !== 'prereq' && e.relation !== 'generalizes' && e.relation !== 'applies_to') continue;
  const list = edgesByDst.get(e.dst);
  if (list) list.push(e);
  else edgesByDst.set(e.dst, [e]);
}

export interface SkillMastery {
  /** 0..1 ratio of successes/attempts (0 if no attempts yet). */
  mastery: number;
  attempts: number;
  /** Days since last practice; Infinity if never practiced. */
  staleness_days: number;
}

export interface LearningPlanNode {
  concept_id: string;
  name: string;
  name_he: string | null;
  subject: string;
  /** Inverse-mastery score in [0, 1]; higher = more urgent to study. */
  urgency: number;
  hasLesson: boolean;
  /** Edge weight from the planning walk (how strongly this is a prereq). */
  edge_weight: number;
  relation: 'self' | 'prereq' | 'generalizes' | 'applies_to';
  /** Atoms this concept teaches that the learner has the WEAKEST mastery in. */
  weak_atoms: Array<{ atom: string; mastery: number; attempts: number }>;
  /** Why this node was inserted into the plan, in plain English/Hebrew. */
  why_en: string;
  why_he: string;
}

export interface LearningPlan {
  goal: { concept_id: string; name: string; name_he: string | null; subject: string };
  /**
   * Ordered list — index 0 is the next concrete step the learner should take,
   * later entries are downstream goals that depend on completing earlier ones.
   */
  path: LearningPlanNode[];
  /** Skill atoms across the whole walk where mastery is below the threshold. */
  blocking_atoms: Array<{ atom: string; concepts: string[]; mastery: number }>;
  generated_at: string;
}

/**
 * Pulls per-atom mastery for the given learner. Returns an empty map if Neon
 * is not configured or the learner has no practice yet.
 */
export async function fetchLearnerMastery(
  learnerId: string,
): Promise<Map<string, SkillMastery>> {
  const out = new Map<string, SkillMastery>();
  if (!sql) return out;
  try {
    const rows = (await sql`
      SELECT skill_atom, attempts, successes,
             EXTRACT(EPOCH FROM (NOW() - last_practiced)) / 86400.0 AS staleness_days
      FROM skill_practice
      WHERE learner_id = ${learnerId}
    `) as Array<{ skill_atom: string; attempts: number; successes: number; staleness_days: number | null }>;
    for (const r of rows) {
      const mastery = r.attempts > 0 ? r.successes / r.attempts : 0;
      out.set(r.skill_atom, {
        mastery,
        attempts: r.attempts,
        staleness_days: r.staleness_days ?? Number.POSITIVE_INFINITY,
      });
    }
    return out;
  } catch (err) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('fetchLearnerMastery failed:', err);
    }
    return out;
  }
}

/** All concept_ids that have an authored lesson, indexed for O(1) lookup. */
async function fetchLessonConceptSet(): Promise<Set<string>> {
  if (!sql) return new Set();
  try {
    const rows = (await sql`SELECT concept_id FROM lessons`) as Array<{ concept_id: string }>;
    return new Set(rows.map((r) => r.concept_id));
  } catch {
    return new Set();
  }
}

/**
 * For each given concept_id, returns the set of skill_atoms it teaches
 * (role = 'teaches' in lesson_skill_atoms). Empty map if Neon is not
 * configured.
 */
async function fetchConceptAtoms(conceptIds: string[]): Promise<Map<string, string[]>> {
  const out = new Map<string, string[]>();
  if (!sql || conceptIds.length === 0) return out;
  try {
    const rows = (await sql`
      SELECT l.concept_id, lsa.skill_atom
      FROM lesson_skill_atoms lsa
      JOIN lessons l ON l.id = lsa.lesson_id
      WHERE l.concept_id = ANY(${conceptIds}::text[])
        AND lsa.role = 'teaches'
    `) as Array<{ concept_id: string; skill_atom: string }>;
    for (const r of rows) {
      const list = out.get(r.concept_id);
      if (list) list.push(r.skill_atom);
      else out.set(r.concept_id, [r.skill_atom]);
    }
    return out;
  } catch {
    return out;
  }
}

/**
 * Builds a learning plan toward `goalConceptId` for `learnerId`.
 *
 * Algorithm (intentionally simple, intentionally explainable):
 *
 *  1. BFS backwards from the goal across (within-subject prereqs ∪ kg_edges).
 *     Each visited concept gets the strongest edge_weight encountered, the
 *     shortest path-distance, and the union of "why" notes.
 *  2. For each visited concept, score urgency = 1 - mean_mastery_of_taught_atoms.
 *     Concepts with no practiced atoms count as urgency 1.0 (you've never
 *     touched them).
 *  3. Drop any concept whose urgency < `MASTERY_THRESHOLD` AND that has been
 *     practiced — those are already "good enough" and the learner doesn't
 *     need to revisit them right now.
 *  4. Sort by (distance asc, urgency desc) so the next concrete step is at
 *     index 0. Distance ties break in favour of higher urgency.
 *  5. Return the goal as the LAST entry (`relation: 'self'`) so the UI can
 *     show "you're working toward …".
 */
export async function buildLearningPlan(args: {
  learnerId: string;
  goalConceptId: string;
  maxNodes?: number;
}): Promise<LearningPlan | null> {
  const goal = kgById.get(args.goalConceptId);
  if (!goal) return null;
  const MAX_NODES = args.maxNodes ?? 12;
  const MASTERY_THRESHOLD = 0.8;

  const [mastery, lessonSet] = await Promise.all([
    fetchLearnerMastery(args.learnerId),
    fetchLessonConceptSet(),
  ]);

  // BFS backwards from the goal.
  interface Visit {
    concept_id: string;
    distance: number;
    edge_weight: number;
    relation: 'self' | 'prereq' | 'generalizes' | 'applies_to';
    why: string[];
  }
  const visits = new Map<string, Visit>();
  visits.set(goal.id, {
    concept_id: goal.id,
    distance: 0,
    edge_weight: 1,
    relation: 'self',
    why: ['your goal'],
  });
  const queue: string[] = [goal.id];
  while (queue.length > 0 && visits.size < MAX_NODES * 3) {
    const id = queue.shift()!;
    const node = kgById.get(id);
    if (!node) continue;
    const prereqs: Array<{ src: string; weight: number; relation: Visit['relation']; note?: string }> = [];
    for (const p of node.prerequisites ?? []) {
      prereqs.push({ src: p, weight: 1, relation: 'prereq' });
    }
    for (const e of edgesByDst.get(id) ?? []) {
      prereqs.push({
        src: e.src,
        weight: e.weight ?? 1,
        relation: e.relation === 'prereq' ? 'prereq' : e.relation === 'generalizes' ? 'generalizes' : 'applies_to',
        note: e.note,
      });
    }
    const current = visits.get(id)!;
    for (const p of prereqs) {
      const existing = visits.get(p.src);
      const newDist = current.distance + 1;
      if (!existing || newDist < existing.distance) {
        visits.set(p.src, {
          concept_id: p.src,
          distance: newDist,
          edge_weight: p.weight,
          relation: p.relation,
          why: [p.note ?? `prereq for ${kgById.get(id)?.name ?? id}`],
        });
        queue.push(p.src);
      } else if (existing && p.weight > existing.edge_weight) {
        existing.edge_weight = p.weight;
        if (p.note) existing.why.push(p.note);
      }
    }
  }

  const conceptIds = [...visits.keys()];
  const conceptAtoms = await fetchConceptAtoms(conceptIds);

  const nodes: LearningPlanNode[] = [];
  const blockingByAtom = new Map<string, { mastery: number; concepts: Set<string> }>();
  for (const id of conceptIds) {
    const v = visits.get(id)!;
    const c = kgById.get(id);
    if (!c) continue;
    const atoms = conceptAtoms.get(id) ?? [];
    let meanMastery = 1;
    let anyPracticed = false;
    const weakAtoms: Array<{ atom: string; mastery: number; attempts: number }> = [];
    if (atoms.length > 0) {
      let total = 0;
      for (const a of atoms) {
        const m = mastery.get(a);
        if (m && m.attempts > 0) anyPracticed = true;
        const score = m?.mastery ?? 0;
        total += score;
        weakAtoms.push({ atom: a, mastery: score, attempts: m?.attempts ?? 0 });
        if (score < MASTERY_THRESHOLD) {
          const slot = blockingByAtom.get(a);
          if (slot) slot.concepts.add(id);
          else blockingByAtom.set(a, { mastery: score, concepts: new Set([id]) });
        }
      }
      meanMastery = total / atoms.length;
    } else {
      meanMastery = 0;
    }
    const urgency = Math.max(0, Math.min(1, 1 - meanMastery));
    weakAtoms.sort((a, b) => a.mastery - b.mastery);

    // Skip already-mastered prerequisites (but always keep the goal).
    if (id !== goal.id && anyPracticed && meanMastery >= MASTERY_THRESHOLD) continue;

    const why_en =
      v.relation === 'self'
        ? `Your goal: ${c.name}.`
        : v.relation === 'prereq'
          ? `Prerequisite for ${kgById.get(goal.id)?.name ?? 'your goal'}${urgency >= 0.8 ? ' — you haven\u2019t practiced these skills yet.' : '.'}`
          : v.relation === 'generalizes'
            ? `${c.name} generalises a concept your goal builds on.`
            : `${c.name} is applied directly in your goal area.`;
    const why_he =
      v.relation === 'self'
        ? `המטרה שלכם: ${c.name_he ?? c.name}.`
        : v.relation === 'prereq'
          ? `דרישת קדם ל-${kgById.get(goal.id)?.name_he ?? kgById.get(goal.id)?.name}${urgency >= 0.8 ? ' — לא תרגלתם את הכישורים האלו עדיין.' : '.'}`
          : v.relation === 'generalizes'
            ? `${c.name_he ?? c.name} מכליל מושג שהמטרה שלכם נשענת עליו.`
            : `${c.name_he ?? c.name} מוחל ישירות באזור המטרה שלכם.`;

    nodes.push({
      concept_id: id,
      name: c.name,
      name_he: c.name_he,
      subject: c.subject,
      urgency,
      hasLesson: lessonSet.has(id),
      edge_weight: v.edge_weight,
      relation: v.relation,
      weak_atoms: weakAtoms.slice(0, 5),
      why_en,
      why_he,
    });
  }

  nodes.sort((a, b) => {
    if (a.relation === 'self' && b.relation !== 'self') return 1;
    if (b.relation === 'self' && a.relation !== 'self') return -1;
    // Most urgent first within the same effective distance band.
    return b.urgency - a.urgency || b.edge_weight - a.edge_weight;
  });

  const path = nodes.slice(0, MAX_NODES);
  const blocking_atoms = [...blockingByAtom.entries()]
    .map(([atom, v]) => ({ atom, mastery: v.mastery, concepts: [...v.concepts] }))
    .sort((a, b) => a.mastery - b.mastery)
    .slice(0, 20);

  return {
    goal: { concept_id: goal.id, name: goal.name, name_he: goal.name_he, subject: goal.subject },
    path,
    blocking_atoms,
    generated_at: new Date().toISOString(),
  };
}
