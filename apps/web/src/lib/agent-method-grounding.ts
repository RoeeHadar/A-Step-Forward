/**
 * Method-grounding contract for Tutor/Coach (ADR-0014 disease fix).
 *
 * Disease: inventing constructions/arithmetic paths not authorized by injected
 * corpus. Cure: method-first protocol + explicit source inventory each turn —
 * not a growing catalog of shape-specific solvers.
 */
import type { LessonAgentHints, LessonWithQuestions } from '@/lib/neon-db';
import type { AuthoritativeSolve } from '@/lib/agent-solver-verify';

export interface MethodSourceInventory {
  conceptId: string | null;
  hasWorkedExample: boolean;
  hasKeyInsights: boolean;
  hasVerifySolve: boolean;
  /** Thin = no worked example AND no key insights AND no verify */
  thin: boolean;
  insightSnippets: string[];
  workedExampleTitles: string[];
}

export function isMathTeachingTurn(message: string): boolean {
  const t = message.trim();
  if (!t) return false;
  return /(?:חשב|מצא(?:ו)?|פתור|הסבר|הסבירו|גובה|שטח|הוכח|נגזר|אינטגרל|משווא|טרפז|משולש|מעגל|ממוצע|solve|find|compute|prove|explain|height|area|derivative|integral|equation|triangle|trapezoid|circle|mean|how (?:do|to)|איך (?:לחשב|למצוא|לפתור|מחשבים))/i.test(
    t,
  );
}

export function buildMethodSourceInventory(params: {
  conceptId?: string | null;
  lesson: LessonWithQuestions | null;
  hints?: LessonAgentHints | null;
  verify: AuthoritativeSolve | null;
}): MethodSourceInventory {
  const row = params.lesson?.lesson ?? null;
  const hints = params.hints ?? row?.agent_hints ?? null;
  const examples = (row?.sections ?? []).filter((s) => s.kind === 'worked_example');
  const insights = (hints?.key_insights ?? []).map((h) => h.trim()).filter(Boolean);
  const hasWorkedExample = examples.length > 0;
  const hasKeyInsights = insights.length > 0;
  const hasVerifySolve = params.verify != null;
  return {
    conceptId: params.conceptId ?? row?.concept_id ?? null,
    hasWorkedExample,
    hasKeyInsights,
    hasVerifySolve,
    thin: !hasWorkedExample && !hasKeyInsights && !hasVerifySolve,
    insightSnippets: insights.slice(0, 4),
    workedExampleTitles: examples
      .slice(0, 2)
      .map((e) => e.title_he || e.title_en)
      .filter(Boolean),
  };
}

/**
 * System-prompt block: inventory + protocol. Shape-agnostic.
 */
export function buildMethodAuthorityBlock(
  inventory: MethodSourceInventory,
  locale: 'he' | 'en' = 'he',
): string {
  const cite =
    inventory.conceptId != null
      ? `\`concept:${inventory.conceptId}\` / \`lesson:${inventory.conceptId}\``
      : '`concept:<id>` / `lesson:<id>` when known';

  const lines = [
    `## Method authority (ADR-0014 — mandatory for math teaching)`,
    `This block treats **method invention** as the failure mode. Deterministic verify solvers (when present) are safety nets — not a catalog to expand case-by-case.`,
    ``,
    `### Sources available this turn`,
    `- worked_example sections: ${inventory.hasWorkedExample ? `yes (${inventory.workedExampleTitles.join('; ') || 'present'})` : 'no'}`,
    `- agent_hints.key_insights: ${inventory.hasKeyInsights ? 'yes' : 'no'}`,
    `- solver.verify_numeric match: ${inventory.hasVerifySolve ? 'yes (AUTHORITATIVE numbers — must match)' : 'no'}`,
    `- source richness: ${inventory.thin ? 'THIN' : 'usable'}`,
  ];

  if (inventory.insightSnippets.length) {
    lines.push(`- insight snippets:`);
    for (const s of inventory.insightSnippets) {
      lines.push(`  - ${s.slice(0, 160)}`);
    }
  }

  lines.push(
    ``,
    `### Protocol (do this every math turn)`,
    `1. **Method first.** Before any invented construction or formula, name the method and cite ${cite}.`,
    `2. **Only authorized steps.** Use constructions that appear in worked_example / key_insights / verify pack. Persona may only tie-break among those.`,
    `3. **Thin sources → refuse to invent.** If sources are THIN: say clearly that the injected corpus does not authorize a freestyle construction; give only standard named formulas that *do* appear above, or ask which concept/lesson they are on. Do **not** invent a clever diagram or identity to fill the gap.`,
    `4. **Challenge / "you're wrong" / "what triangle?".** Drop the failed path immediately. Re-ground from sources above. Teach 2–3 concrete correct steps. Ban empty Socratic stalls ("how do you think you can find…?").`,
    `5. **Soft-cite** once: \`[[ASF_CITE:{"tools":["curriculum.get_worked_example"],"concept_id":"…"}]]\`.`,
  );

  if (locale === 'he') {
    lines.push(
      `6. Hebrew default; math LTR in \`$...$\`. Complete sentences — never paste prompt labels.`,
    );
  }

  return lines.join('\n');
}

/** Turn overlay when learner is in a math teaching / solve turn. */
export const METHOD_GROUNDING_TURN_INSTRUCTION = `## THIS TURN — method grounding (mandatory)
You are teaching or solving math. Follow \`## Method authority\` above.
- Name the method + cite before numbers.
- Do not invent constructions absent from sources.
- If sources are THIN: refuse freestyle invention; stay with named corpus formulas or ask for the concept.
- If the learner challenges your method: drop it and re-teach from sources — no stalling.`;

/**
 * Heuristic: math-heavy reply without any corpus citation.
 * Used for shadow logging / offline evals — not a hard stream block yet.
 */
export function lacksMethodCitation(reply: string): boolean {
  const r = reply.trim();
  if (r.length < 40) return false;
  const mathHeavy =
    /(\$|\\\\sqrt|√|גובה|שטח|משולש|טרפז|נוסח|derivative|integral|triangle|trapezoid|height|area)/i.test(
      r,
    );
  if (!mathHeavy) return false;
  const cited =
    /lesson:[a-z0-9_.:-]+|concept:[a-z0-9_.:-]+|\[\[ASF_CITE:|Sources:|מקורות:/i.test(r);
  return !cited;
}

/** Empty Socratic stall after a challenge (disease symptom). */
export const SOCRATIC_STALL_RE =
  /(?:איך אתה חושב|how do you think|מה אתה חושב ש|נסה לזכור את המבנה|try to remember the (?:geometric )?structure)/i;

export function looksLikeSocraticStall(reply: string): boolean {
  return SOCRATIC_STALL_RE.test(reply) && reply.trim().length < 420;
}
