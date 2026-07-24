/**
 * ADR-0014 — hybrid tools / solver / handoff digest unit tests (no live LLM).
 */
import { describe, expect, it } from 'vitest';
import { buildHandoffDigest, wantsMemoryExpand } from './agent-handoff-digest';
import {
  buildCoachHybridToolPack,
  buildTutorSolverToolPack,
  formatVerifyNumericToolResult,
} from './agent-hybrid-tools';
import {
  buildSolverRevealInstruction,
  countSolverHintCycles,
  learnerConfirmedReveal,
  softRepairNumericReply,
  trySolveIsoscelesTrapezoid,
  trySolveMissingMean,
  wantsFullSolutionNow,
} from './agent-solver-verify';
import { parseCiteTags, stripCiteMachineTags } from './chat-cite-tags';
import { buildAgentSkillsPrompt } from './agent-skills';

describe('trySolveMissingMean', () => {
  it('solves classic missing score for target mean', () => {
    const solve = trySolveMissingMean(
      'ממוצע של 5 ציונים. הציונים: 70, 80, 90, 85. רוצים ממוצע 84. מה החסר?',
    );
    expect(solve).not.toBeNull();
    expect(solve!.n).toBe(5);
    expect(solve!.knownValues).toHaveLength(4);
    expect(solve!.expected).toBe(84 * 5 - (70 + 80 + 90 + 85));
  });

  it('solves English mean-of-n pattern', () => {
    const solve = trySolveMissingMean(
      'Mean of 4 scores. The scores are 10, 12, 14. Want mean 13. Find the missing value.',
    );
    expect(solve).not.toBeNull();
    expect(solve!.expected).toBe(13 * 4 - (10 + 12 + 14));
  });
});

describe('trySolveIsoscelesTrapezoid', () => {
  it('solves the bagrut bases+legs height/area case from the user transcript', () => {
    const solve = trySolveIsoscelesTrapezoid(
      'טרפז שווה-שוקיים עם בסיסים 8 ו- 14 ושוקיים 5. הסבירו מציאת גובה ואז חשבו שטח.',
    );
    expect(solve).not.toBeNull();
    expect(solve!.overhang).toBe(3);
    expect(solve!.height).toBe(4);
    expect(solve!.area).toBe(44);
    expect(solve!.expected).toBe(44); // area asked
  });

  it('soft-repairs invented upper-triangle method', () => {
    const solve = trySolveIsoscelesTrapezoid(
      'טרפז שווה-שוקיים עם בסיסים 8 ו-14 ושוקיים 5. שטח?',
    )!;
    const bad =
      'חשב את המשולש העליון: בסיס 8 ושוקיים 5. g = sqrt(8^2 - 5^2) = sqrt(39).';
    const r = softRepairNumericReply(bad, solve, 'he');
    expect(r.repaired).toBe(true);
    expect(r.text).toContain('4');
    expect(r.text).toContain('44');
    expect(r.text).toMatch(/בליטה|overhang|אנכים/i);
  });
});

describe('softRepairNumericReply', () => {
  it('appends correction when final mismatches', () => {
    const r = softRepairNumericReply('התשובה היא $90$.', 95, 'he');
    expect(r.repaired).toBe(true);
    expect(r.text).toContain('95');
  });

  it('leaves matching finals alone', () => {
    const r = softRepairNumericReply('התשובה היא $95$.', 95, 'he');
    expect(r.repaired).toBe(false);
  });
});

describe('solver reveal policy', () => {
  it('counts hint/attempt cycles', () => {
    const cycles = countSolverHintCycles([
      { role: 'user', content: 'אני חושב שהתשובה 10' },
      { role: 'assistant', content: 'רמז: חשבו על הממוצע' },
      { role: 'user', content: 'תקוע' },
      { role: 'assistant', content: 'נסה לחשוב על setup' },
    ]);
    expect(cycles).toBe(2);
  });

  it('blocks full dump when asked early', () => {
    expect(wantsFullSolutionNow('תן לי את הפתרון המלא')).toBe(true);
    expect(wantsFullSolutionNow('אוקיי, אז איך לפתור')).toBe(true);
    const block = buildSolverRevealInstruction({
      cycles: 0,
      wantsFull: true,
      confirmed: false,
      inPracticeArena: false,
    });
    expect(block).toMatch(/concrete method step|Do NOT dump/i);
  });

  it('forces teaching when authoritative solve is present', () => {
    const block = buildSolverRevealInstruction({
      cycles: 1,
      wantsFull: true,
      confirmed: false,
      inPracticeArena: false,
      hasAuthoritativeSolve: true,
    });
    expect(block).toContain('AUTHORITATIVE SOLVE PRESENT');
    expect(block).toContain('Do NOT invent');
  });

  it('does not treat bare כן as reveal confirm', () => {
    expect(learnerConfirmedReveal('כן')).toBe(false);
    expect(learnerConfirmedReveal('כן תן')).toBe(true);
  });

  it('keeps practice arena sealed', () => {
    const block = buildSolverRevealInstruction({
      cycles: 5,
      wantsFull: true,
      confirmed: true,
      inPracticeArena: true,
      practiceGraded: false,
    });
    expect(block).toContain('practice arena');
    expect(block).toContain('NEVER reveal');
  });
});

describe('handoff digest + cite tags', () => {
  it('builds compressed peer digest', () => {
    const d = buildHandoffDigest({
      readingAgent: 'coach',
      notes: [
        {
          agent: 'tutor',
          kind: 'misconception',
          content: 'Confuses mean with median on bagrut stats',
          importance: 4,
        },
        {
          agent: 'coach',
          kind: 'strategy',
          content: 'own note should be excluded',
          importance: 5,
        },
      ],
    });
    expect(d).toContain('handoff digest');
    expect(d).toContain('tutor/misconception');
    expect(d).not.toContain('own note');
  });

  it('detects memory expand asks', () => {
    expect(wantsMemoryExpand('מה אתה זוכר עליי?')).toBe(true);
    expect(wantsMemoryExpand('פתור תרגיל')).toBe(false);
  });

  it('strips ASF_CITE tags', () => {
    const raw = 'answer [[ASF_CITE:{"tools":["get_due_queue"],"concept_id":"stats_mean"}]]';
    expect(parseCiteTags(raw)[0]?.tools).toContain('get_due_queue');
    expect(stripCiteMachineTags(raw)).toBe('answer');
  });
});

describe('hybrid tool packs', () => {
  it('coach pack lists allowlisted tools', () => {
    const pack = buildCoachHybridToolPack({
      due: [],
      pathNodes: [
        {
          concept_id: 'stats_mean',
          name: 'Mean',
          name_he: 'ממוצע',
          weak_atoms: [{ atom: 'compute_mean', mastery: 0.2 }],
        },
      ],
      lesson: null,
      expandNotes: [],
      expand: false,
      userMessage: 'mean of 3 scores. scores are 2, 4. want mean 5.',
      locale: 'en',
      conceptId: 'stats_mean',
    });
    expect(pack.toolsUsed).toContain('get_due_queue');
    expect(pack.toolsUsed).toContain('solver.verify_numeric');
    expect(pack.block).toContain('Hybrid tool results');
    expect(pack.verifyExpected?.expected).toBe(5 * 3 - (2 + 4));
    expect(formatVerifyNumericToolResult(pack.verifyExpected)).toContain('AUTHORITATIVE');
  });

  it('tutor pack excludes drill-only tools', () => {
    const pack = buildTutorSolverToolPack({
      lesson: null,
      expandNotes: [],
      expand: true,
      userMessage: 'hello',
      locale: 'he',
    });
    expect(pack.toolsUsed).toContain('curriculum.get_worked_example');
    expect(pack.toolsUsed).not.toContain('get_due_queue');
    expect(pack.block).toContain('memory.expand');
  });
});

describe('agent-skills ADR-0014', () => {
  it('coach and tutor mention hybrid/solver policy', () => {
    const coach = buildAgentSkillsPrompt('coach');
    expect(coach).toContain('ADR-0014');
    expect(coach).toContain('get_due_queue');
    const tutor = buildAgentSkillsPrompt('tutor');
    expect(tutor).toContain('Shared solver');
    expect(tutor).toContain('Soft citation');
  });
});
