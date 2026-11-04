import fs from 'node:fs';
import path from 'node:path';
import { describe, it, expect } from 'vitest';
import {
  FINAL_VALUE_RE,
  REVIEWER_MAX_LINES,
  createReplyGuard,
  hasFinalValue,
  isLearnerAttempt,
  shouldArmTutorGuard,
  tutorHint,
} from '@/lib/agent-method-guard';
import { AGENT_METHOD_SPECS, buildAgentSkillsPrompt } from '@/lib/agent-skills';
import { getAgentPersona } from '@/lib/agent-prompts';

const run = (g: ReturnType<typeof createReplyGuard>, chunks: string[]) => {
  let out = '';
  for (const c of chunks) out += g!.push(c);
  return out + g!.flush();
};

describe('AS-41 FINAL_VALUE_RE (RUB ROLE regex)', () => {
  it('matches final values and answer phrasings', () => {
    for (const s of ['x = 4', 'x=4.', 'so y = -2.5', 'ש-x = 4', 'The answer is 4', 'התשובה היא 4', 'answer: x = 4']) expect(hasFinalValue(s), s).toBe(true);
  });
  it('does not match steps, equations or tags', () => {
    for (const s of ['2x + 3 = 11', '2x = 8', 'x = 2 + y', 'move the 3: what do you get?', '[[ASF_MEMORY_NOTE:{"c":"x = 4"}]]']) expect(hasFinalValue(s), s).toBe(false);
  });
  it('is the regex the AS-27 runner uses for ROLE', () => {
    const runner = fs.readFileSync(path.resolve(__dirname, '../../evals/as16-offline.test.ts'), 'utf8');
    expect(runner).toContain("from '@/lib/agent-method-guard'");
    expect(FINAL_VALUE_RE.test('x = 4')).toBe(true);
  });
});

describe('AS-41 attempt detection', () => {
  it.each([
    ['אני לא מבין משוואות, תן לי פשוט את התשובה ל 2x+3=11', false],
    ['just give me the answer to 2x+3=11', false],
    ['לא יודע', false],
    ["I don't know", false],
    ['x=7?', true],
    ['אוקיי x=4', true],
    ['x^2+4', true],
    ['I got 5', true],
    ['קיבלתי 5', true],
    ['7', true],
  ])('%s -> %s', (m, want) => expect(isLearnerAttempt(m)).toBe(want));
});

describe('AS-41 J1 tutor hint-before-answer post-check', () => {
  const j1 = 'אני לא מבין משוואות, תן לי פשוט את התשובה ל 2x+3=11';
  it('J1 give-me-the-answer turn: final value is rewritten to a hint (streamed chunks)', () => {
    const g = createReplyGuard({ agent: 'tutor', lastMessage: j1, locale: 'he' });
    const out = run(g, ['בוא נ', 'תקדם.\nמחסרים 3: 2x = 8\nולכן x', ' = 4.', ' [[ASF_MEMORY_NOTE:{"kind":"misconception"}]]']);
    expect(hasFinalValue(out)).toBe(false);
    expect(g!.tripped).toBe(true);
    expect(out).toContain('[[ASF_MEMORY_NOTE:');
    expect(out).toMatch(/\?/);
  });
  it('answer allowed after an attempt (guard off)', () => {
    expect(createReplyGuard({ agent: 'tutor', lastMessage: 'אוקיי x=4', locale: 'he' })).toBeNull();
    expect(createReplyGuard({ agent: 'tutor', lastMessage: 'x=7?', locale: 'he' })).toBeNull();
  });
  it('a clean hint passes unchanged', () => {
    const g = createReplyGuard({ agent: 'tutor', lastMessage: j1, locale: 'he' });
    const txt = 'מה יוצא אם מעבירים את 3 לצד השני?\nנסה.';
    expect(run(g, [txt])).toBe(txt);
    expect(g!.tripped).toBe(false);
  });
  it('never splits an open [[ASF_ tag across a newline', () => {
    const g = createReplyGuard({ agent: 'tutor', lastMessage: j1, locale: 'en' });
    const out = run(g, ['Hint. [[ASF_CITE:{"a":', '"b\n"}]] more\nx = 4']);
    expect(out).toContain('[[ASF_CITE:{"a":"b\n"}]]');
    expect(hasFinalValue(out)).toBe(false);
  });
  it('mentor/coach untouched', () => {
    expect(createReplyGuard({ agent: 'mentor', lastMessage: j1, locale: 'he' })).toBeNull();
    expect(createReplyGuard({ agent: 'coach', lastMessage: j1, locale: 'he' })).toBeNull();
  });
});

describe('AS-41 Reviewer reply has no full solution', () => {
  it('drops full-rewrite lines and caps visible lines', () => {
    const g = createReplyGuard({ agent: 'reviewer', lastMessage: 'Review my solution: ...', locale: 'en' });
    const body = ['Strength: clear.', 'Gap: step 3.', 'Here is the full corrected solution:', ...Array.from({ length: 12 }, (_, i) => `Step ${i + 1}.`)].join('\n');
    const out = run(g, [body, ' [[ASF_CITE:{"x":1}]]']);
    expect(out).not.toMatch(/full (corrected )?solution/i);
    expect(out.split('\n').filter((l) => l.replace(/\[\[ASF_[\s\S]*?\]\]/g, '').trim()).length).toBeLessThanOrEqual(REVIEWER_MAX_LINES);
    expect(out).toContain('[[ASF_CITE:');
  });
});

describe('AS-41 method specs single source', () => {
  it('one method spec per agent, injected into the persona', () => {
    for (const a of ['tutor', 'mentor', 'coach', 'reviewer'] as const) {
      expect(AGENT_METHOD_SPECS[a]).toMatch(/Must:.*\n- Must not:.*\n- Alignment:/);
      expect(buildAgentSkillsPrompt(a)).toContain(AGENT_METHOD_SPECS[a]);
      expect(getAgentPersona(a)).toContain(AGENT_METHOD_SPECS[a]);
    }
  });
  it('prompts/*/v1.md for the live agents are marked doc-only', () => {
    for (const a of ['tutor', 'mentor', 'coach', 'reviewer']) {
      const md = fs.readFileSync(path.resolve(__dirname, `../../../../../prompts/${a}/v1.md`), 'utf8');
      expect(md.split('\n')[0]).toContain('DOC-ONLY (AS-41)');
    }
  });
});

// Offline stand-in for the blind 4-way judge: method markers only (no agent name).
type Fx = { id: string; agent: string; prompt: string; attempted: boolean; reply: string };
const MARKERS: Record<string, RegExp> = {
  reviewer: /first error|what's right|one fix|הטעות הראשונה|מה נכון|תיקון אחד/i,
  coach: /drill|due queue|practice item|item 1|תרגול|מהתור|פריט/i,
  mentor: /goal|plan|evidence|check in|welcome back|מטרה|תוכנית|ראיה|בדיקת מצב/i,
  tutor: /hint|try|step|what is x|רמז|נסה|בשלבים/i,
};
const classify = (reply: string) => Object.entries(MARKERS).find(([, re]) => re.test(reply))?.[0] ?? 'tutor';

describe('AS-41 classifier fixtures 4 agents x 3 prompts', () => {
  const fx = (JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../../evals/as16/classifier-fixtures.json'), 'utf8')) as { fixtures: Fx[] }).fixtures;
  it('has 4 agents x 3 prompts', () => {
    for (const a of ['tutor', 'mentor', 'coach', 'reviewer']) expect(fx.filter((f) => f.agent === a)).toHaveLength(3);
  });
  it('blind 4-way rule classifier accuracy >= 0.75', () => {
    const acc = fx.filter((f) => classify(f.reply) === f.agent).length / fx.length;
    console.log(`[AS41] classifier_accuracy=${acc.toFixed(3)} n=${fx.length}`);
    expect(acc).toBeGreaterThanOrEqual(0.75);
  });
  it('fixtures obey the guards (tutor: no final value pre-attempt; reviewer: short)', () => {
    for (const f of fx) {
      if (f.agent === 'tutor' && !f.attempted) expect(hasFinalValue(f.reply), f.id).toBe(false);
      if (f.agent === 'tutor') expect(isLearnerAttempt(f.prompt), f.id).toBe(f.attempted);
      if (f.agent === 'reviewer') {
        const g = createReplyGuard({ agent: 'reviewer', lastMessage: f.prompt, locale: 'en' });
        expect(run(g, [f.reply]), f.id).toBe(f.reply);
      }
    }
  });
});

describe('AS-41 r1 (P1-1) arming rule + negative teaching fixtures (he/en)', () => {
  type Neg = { id: string; lang: 'he' | 'en'; prompt: string; reply: string };
  const neg = (JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../../evals/as16/role-negative-fixtures.json'), 'utf8')) as { fixtures: Neg[] }).fixtures;
  it('covers he and en', () => {
    expect(neg.some((f) => f.lang === 'he') && neg.some((f) => f.lang === 'en')).toBe(true);
  });
  it.each(neg.map((f) => [f.id, f] as const))('%s passes through unchanged (tutor + reviewer)', (_id, f) => {
    expect(shouldArmTutorGuard(f.prompt, false)).toBe(false);
    for (const agent of ['tutor', 'reviewer']) {
      const g = createReplyGuard({ agent, lastMessage: f.prompt, locale: f.lang });
      const chunks = f.reply.match(/[\s\S]{1,7}/g) ?? [];
      expect(g ? run(g, chunks) : f.reply).toBe(f.reply);
    }
  });
  it('arms on an explicit answer request or an ungraded practice item, not on teaching', () => {
    expect(shouldArmTutorGuard('just give me the answer to 2x+3=11', false)).toBe(true);
    expect(shouldArmTutorGuard('תן לי פשוט את התשובה', false)).toBe(true);
    expect(shouldArmTutorGuard('teach me Newtons second law', true)).toBe(true);
    expect(shouldArmTutorGuard('x=7?', true)).toBe(false);
    expect(shouldArmTutorGuard('why?', false)).toBe(false);
    expect(createReplyGuard({ agent: 'tutor', lastMessage: 'teach me Newtons second law', locale: 'en', practiceActive: false })).toBeNull();
  });
  it('replacement hint is generic (no linear-equation wording)', () => {
    for (const l of ['he', 'en']) expect(tutorHint(l)).not.toMatch(/both sides|בשני הצדדים|undo/i);
  });
});
