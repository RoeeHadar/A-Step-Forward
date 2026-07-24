/**
 * Hybrid tool packs for Coach / Tutor (ADR-0014).
 * Authoritative server results labeled as tool outputs — no LLM tools API.
 */
import type { DueReviewItem } from '@/lib/neon-db';
import type { LessonSection, LessonWithQuestions, LearnerAgentNote } from '@/lib/neon-db';
import {
  trySolveAuthoritative,
  type AuthoritativeSolve,
  type MeanMissingSolve,
} from '@/lib/agent-solver-verify';

export interface WeakAtomPathNode {
  concept_id: string;
  name?: string;
  name_he?: string | null;
  weak_atoms: Array<{ atom: string; mastery: number }>;
}

export type HybridToolId =
  | 'get_due_queue'
  | 'get_weak_atoms'
  | 'memory.expand'
  | 'curriculum.get_worked_example'
  | 'solver.verify_numeric';

export interface HybridToolPack {
  /** Markdown block for system prompt */
  block: string;
  toolsUsed: HybridToolId[];
  /** Deterministic expected final when verify tool ran */
  verifyExpected: AuthoritativeSolve | null;
}

function clip(s: string, max: number): string {
  const t = s.replace(/\s+/g, ' ').trim();
  return t.length <= max ? t : `${t.slice(0, max - 1)}…`;
}

function workedExampleSnippet(section: LessonSection, locale: 'he' | 'en'): string {
  const title = locale === 'he' ? section.title_he || section.title_en : section.title_en;
  const body = locale === 'he' ? section.body_he_md || section.body_en_md : section.body_en_md;
  return clip(`${title}: ${body}`, 420);
}

export function formatDueQueueToolResult(due: DueReviewItem[], max = 5): string {
  if (due.length === 0) {
    return `- (empty) No FSRS-due items in scope.`;
  }
  return due
    .slice(0, max)
    .map(
      (d) =>
        `- ${d.concept_name} [\`concept:${d.concept_id}\`] atom=${d.atom_id} last=${Math.round(d.last_score * 100)}%`,
    )
    .join('\n');
}

export function formatWeakAtomsToolResult(
  path: WeakAtomPathNode[],
  blocking: Array<{ atom: string }> = [],
  maxNodes = 4,
): string {
  const lines: string[] = [];
  for (const node of path.slice(0, maxNodes)) {
    if (!node.weak_atoms?.length) continue;
    const atoms = node.weak_atoms
      .slice(0, 3)
      .map((a) => `${a.atom} (${Math.round(a.mastery * 100)}%)`)
      .join(', ');
    const label = node.name_he || node.name || node.concept_id;
    lines.push(`- [\`concept:${node.concept_id}\`] ${label}: ${atoms}`);
  }
  if (blocking.length) {
    lines.push(`- blocking: ${blocking.slice(0, 3).map((b) => b.atom).join(', ')}`);
  }
  if (lines.length === 0) return `- (none) No weak atoms on the current path snapshot.`;
  return lines.join('\n');
}

export function formatWorkedExampleToolResult(
  lesson: LessonWithQuestions | null,
  locale: 'he' | 'en' = 'he',
): string {
  if (!lesson?.lesson) return `- (none) No authored lesson for this concept.`;
  const row = lesson.lesson;
  const examples = (row.sections ?? []).filter((s: LessonSection) => s.kind === 'worked_example');
  if (examples.length === 0) {
    const hints = row.agent_hints?.key_insights?.slice(0, 3) ?? [];
    if (hints.length) {
      return [
        `- lesson:\`concept:${row.concept_id}\` (hints only — no worked_example section)`,
        ...hints.map((h: string) => `  - ${clip(h, 160)}`),
      ].join('\n');
    }
    return `- (none) Lesson \`concept:${row.concept_id}\` has no worked_example / key_insights.`;
  }
  const lines = [
    `- lesson:\`concept:${row.concept_id}\` title=${locale === 'he' ? row.title_he || row.title_en : row.title_en}`,
  ];
  for (const ex of examples.slice(0, 2)) {
    lines.push(`  - ${workedExampleSnippet(ex, locale)}`);
  }
  return lines.join('\n');
}

export function formatMemoryExpandToolResult(
  notes: LearnerAgentNote[],
  conceptId?: string | null,
): string {
  const filtered = conceptId
    ? notes.filter((n) => !n.related_concept_id || n.related_concept_id === conceptId)
    : notes;
  if (filtered.length === 0) {
    return `- (empty) No expandable notes for this topic.`;
  }
  return filtered
    .slice(0, 6)
    .map((n) => `- [${n.kind}|imp=${n.importance}] ${clip(n.content, 160)}`)
    .join('\n');
}

export function formatVerifyNumericToolResult(solve: AuthoritativeSolve | null): string {
  if (!solve) {
    return `- (n/a) Stem did not match a deterministic verify pattern. Rely on arithmetic self-check + worked example.`;
  }
  if (solve.kind === 'isosceles_trapezoid') {
    return [
      `- pattern: isosceles_trapezoid_height_area`,
      `- bases=${solve.baseShort},${solve.baseLong}; leg=${solve.leg}`,
      `- CANONICAL METHOD (mandatory): drop perpendiculars from the short base onto the long base.`,
      `- Each side overhang = (|long−short|)/2 = ${solve.overhang}. Right triangles have legs (overhang, height) and hypotenuse = trap leg.`,
      `- NEVER invent an "upper isosceles triangle" whose base is the short trap base and whose sides are the trap legs.`,
      `- height = √(leg² − overhang²) = $${solve.height}$`,
      `- area = ½(short+long)·height = $${solve.area}$`,
      `- AUTHORITATIVE expected primary final: $${solve.expected}$`,
    ].join('\n');
  }
  const mean = solve as MeanMissingSolve;
  return [
    `- pattern: missing_value_for_target_mean`,
    `- n=${mean.n}, known=${mean.knownValues.join('+')}=${mean.knownSum}, target_mean=${mean.targetMean}`,
    `- AUTHORITATIVE expected final: $${mean.expected}$`,
    `- Formula: x = target_mean * n − known_sum (never n−1).`,
  ].join('\n');
}

const SOFT_CITE_HINT = `When you use any result below, emit once at the end (stripped from learner view): [[ASF_CITE:{"tools":["tool_id",…],"concept_id":"…"}]]`;

/**
 * Coach pack: due + weak atoms + optional expand + worked example + verify.
 */
export function buildCoachHybridToolPack(params: {
  due: DueReviewItem[];
  pathNodes: WeakAtomPathNode[];
  blockingAtoms?: Array<{ atom: string }>;
  lesson: LessonWithQuestions | null;
  expandNotes: LearnerAgentNote[];
  expand: boolean;
  userMessage: string;
  locale?: 'he' | 'en';
  conceptId?: string | null;
}): HybridToolPack {
  const locale = params.locale ?? 'he';
  const toolsUsed: HybridToolId[] = ['get_due_queue', 'get_weak_atoms'];
  const parts: string[] = [
    `## Hybrid tool results (authoritative — ADR-0014)`,
    `Treat these as ground truth for this turn. Prefer corpus method from worked examples; persona is tie-break only.`,
    SOFT_CITE_HINT,
    ``,
    `### get_due_queue`,
    formatDueQueueToolResult(params.due),
    ``,
    `### get_weak_atoms`,
    formatWeakAtomsToolResult(params.pathNodes, params.blockingAtoms ?? []),
  ];

  if (params.expand) {
    toolsUsed.push('memory.expand');
    parts.push(``, `### memory.expand`, formatMemoryExpandToolResult(params.expandNotes, params.conceptId));
  }

  toolsUsed.push('curriculum.get_worked_example');
  parts.push(
    ``,
    `### curriculum.get_worked_example`,
    formatWorkedExampleToolResult(params.lesson, locale),
  );

  const verify = trySolveAuthoritative(params.userMessage);
  toolsUsed.push('solver.verify_numeric');
  parts.push(``, `### solver.verify_numeric`, formatVerifyNumericToolResult(verify));

  return { block: parts.join('\n'), toolsUsed, verifyExpected: verify };
}

/**
 * Tutor pack: worked example + verify (+ optional memory.expand). No due/weak-atom tools.
 */
export function buildTutorSolverToolPack(params: {
  lesson: LessonWithQuestions | null;
  expandNotes: LearnerAgentNote[];
  expand: boolean;
  userMessage: string;
  locale?: 'he' | 'en';
  conceptId?: string | null;
}): HybridToolPack {
  const locale = params.locale ?? 'he';
  const toolsUsed: HybridToolId[] = ['curriculum.get_worked_example', 'solver.verify_numeric'];
  const parts: string[] = [
    `## Hybrid tool results (authoritative — ADR-0014)`,
    `Shared solver for Tutor. Corpus/canonical method first; cite concept/lesson ids.`,
    SOFT_CITE_HINT,
    ``,
    `### curriculum.get_worked_example`,
    formatWorkedExampleToolResult(params.lesson, locale),
  ];

  if (params.expand) {
    toolsUsed.push('memory.expand');
    parts.push(``, `### memory.expand`, formatMemoryExpandToolResult(params.expandNotes, params.conceptId));
  }

  const verify = trySolveAuthoritative(params.userMessage);
  parts.push(``, `### solver.verify_numeric`, formatVerifyNumericToolResult(verify));

  return { block: parts.join('\n'), toolsUsed, verifyExpected: verify };
}
