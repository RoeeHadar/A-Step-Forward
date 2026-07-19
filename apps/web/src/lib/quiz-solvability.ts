/**
 * Solvability guardrails for AI-generated exam quizzes (/app/quiz).
 *
 * LLMs invent Bagrut-style multi-part items that look authentic but ask
 * students to prove theorems from insufficient data (e.g. "prove diagonals
 * bisect each other" for a generic quadrilateral with two sides + a height).
 * These heuristics reject such items before they reach learners.
 */

export interface SolvabilityPart {
  label?: string;
  body_en?: string;
  body_he?: string;
}

export interface SolvabilityQuestionInput {
  stem_en?: string;
  stem_he?: string;
  parts?: SolvabilityPart[];
  sample_solution_en?: string;
  sample_solution_he?: string;
}

export interface SolvabilityResult {
  ok: boolean;
  reasons: string[];
}

function norm(s: string | undefined | null): string {
  return (s ?? '').toLowerCase().replace(/\s+/g, ' ').trim();
}

function combinedStem(q: SolvabilityQuestionInput): string {
  return `${norm(q.stem_en)} ${norm(q.stem_he)}`;
}

function combinedParts(q: SolvabilityQuestionInput): string {
  return (q.parts ?? [])
    .map((p) => `${norm(p.body_en)} ${norm(p.body_he)}`)
    .join(' | ');
}

function combinedSolution(q: SolvabilityQuestionInput): string {
  return `${norm(q.sample_solution_en)} ${norm(q.sample_solution_he)}`;
}

/** Stem already establishes a parallelogram-family shape. */
export function stemEstablishesParallelogramFamily(stem: string): boolean {
  const s = norm(stem);
  return (
    /parallelogram|rectangle|rhombus|square|מקבילית|מלבן|מעוין|ריבוע/.test(s) &&
    !/generic quadrilateral|מרובע כללי/.test(s)
  );
}

/** Part asks to prove that diagonals bisect each other. */
export function partAsksDiagonalBisectionProof(partText: string): boolean {
  const t = norm(partText);
  const bisect =
    /bisect each other|bisect one another|חוצים זה את זה|חוצה זה את זה|חוצות זו את זו/.test(
      t,
    );
  const diagonals = /diagonal|אלכסון|אלכסונ/.test(t);
  const prove = /prove|show that|הוכח|הוכיח|הראה ש/.test(t);
  return bisect && diagonals && prove;
}

/** Solution admits the item is under-determined / unsolvable. */
export function solutionAdmitsInsufficientData(solution: string): boolean {
  const s = norm(solution);
  return (
    /insufficient (data|information)|not enough (data|information)|cannot be prov|cannot prove|impossible to prov|חסרים נתונים|אין מספיק נתונים|לא ניתן להוכיח|לא ניתן לחשב|אי אפשר להוכיח/.test(
      s,
    )
  );
}

/**
 * Generic "quadrilateral" + one height + two sides, asked for area —
 * area formula is not uniquely determined without the shape type.
 */
export function asksAmbiguousQuadrilateralArea(stem: string, parts: string): boolean {
  const s = norm(stem);
  const p = norm(parts);
  const genericQuad =
    (/\bquadrilateral\b|מרובע/.test(s) || /\btrapazoid\b|\btrapezoid\b|טרפז/.test(s)) &&
    !stemEstablishesParallelogramFamily(s);
  const hasHeight = /height|גובה/.test(s);
  const asksArea = /area|שטח/.test(p);
  return genericQuad && hasHeight && asksArea;
}

/**
 * Pure solvability check. Returns ok:false with machine-readable reasons.
 */
export function assessQuizQuestionSolvability(
  q: SolvabilityQuestionInput,
): SolvabilityResult {
  const reasons: string[] = [];
  const stem = combinedStem(q);
  const parts = combinedParts(q);
  const solution = combinedSolution(q);

  if (!stem.trim()) {
    reasons.push('empty_stem');
  }

  if (partAsksDiagonalBisectionProof(parts) && !stemEstablishesParallelogramFamily(stem)) {
    reasons.push('diagonal_bisection_without_parallelogram');
  }

  if (asksAmbiguousQuadrilateralArea(stem, parts)) {
    reasons.push('ambiguous_quadrilateral_area');
  }

  if (solutionAdmitsInsufficientData(solution)) {
    reasons.push('solution_admits_insufficient_data');
  }

  // "Prove that …" parts require a non-empty sample solution that actually
  // attempts the proof (length floor) — empty/stub solutions are not exam-ready.
  const proveParts = (q.parts ?? []).filter((p) =>
    /prove|הוכח|הוכיח/.test(norm(`${p.body_en} ${p.body_he}`)),
  );
  if (proveParts.length > 0 && solution.replace(/\s+/g, '').length < 40) {
    reasons.push('proof_part_without_worked_solution');
  }

  return { ok: reasons.length === 0, reasons };
}

export function filterSolvableQuizQuestions<T extends SolvabilityQuestionInput>(
  questions: T[],
): { kept: T[]; dropped: Array<{ question: T; reasons: string[] }> } {
  const kept: T[] = [];
  const dropped: Array<{ question: T; reasons: string[] }> = [];
  for (const q of questions) {
    const result = assessQuizQuestionSolvability(q);
    if (result.ok) kept.push(q);
    else dropped.push({ question: q, reasons: result.reasons });
  }
  return { kept, dropped };
}
