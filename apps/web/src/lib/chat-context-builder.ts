/**
 * Typed chat context assembly (ADR-0015).
 *
 * Trust hierarchy (highest → lowest):
 *   current message > verified profile/plan/mastery > recent turns >
 *   inferred persona/private notes > cross-agent digest.
 *
 * Callers build named packs; this module assigns priorities and runs
 * whole-section budgeting via `fitSystemSections`.
 */

import { fitSystemSections, type PromptSection } from '@/lib/chat-context-policy';

/** Higher = kept longer under budget pressure. Core (≥90) is never dropped. */
export const CHAT_SECTION_PRIORITY = {
  core: 100,
  language: 95,
  howToTeach: 88,
  profile: 72,
  statusPack: 80,
  bilingualBriefing: 78,
  durableMemory: 76,
  planCatalog: 68,
  activeWeek: 65,
  ragGrounding: 62,
  mastery: 60,
  curriculum: 58,
  hybridTools: 55,
  methodAuthority: 54,
  learningPlan: 52,
  diagnostic: 45,
  handoffDigest: 35,
  xp: 30,
  practiceArena: 70,
} as const;

export type ChatSectionId = keyof typeof CHAT_SECTION_PRIORITY | (string & {});

export interface ChatContextPack {
  id: ChatSectionId;
  content: string;
  /** Override default priority from CHAT_SECTION_PRIORITY. */
  priority?: number;
}

/**
 * Assemble the final system prompt from an always-on core + optional packs.
 * Never cuts mid-section; drops lowest-priority packs first.
 */
export function assembleChatSystemPrompt(
  core: string,
  packs: ChatContextPack[],
  tail = '',
): { system: string; dropped: string[]; sections: PromptSection[] } {
  const sections: PromptSection[] = [
    { id: 'core', content: core.trim(), priority: CHAT_SECTION_PRIORITY.core },
  ];
  for (const pack of packs) {
    const content = pack.content.trim();
    if (!content) continue;
    const priority =
      pack.priority ??
      (CHAT_SECTION_PRIORITY as Record<string, number>)[pack.id] ??
      50;
    sections.push({ id: String(pack.id), content, priority });
  }
  const fitted = fitSystemSections(sections, tail);
  return { ...fitted, sections };
}

/**
 * Keep private notes that share a token with the current message, high
 * importance (≥4), or durable kinds (preference / misconception / strategy / win)
 * — those must influence teaching even when the question uses different words.
 */
export function filterNotesByRelevance<
  T extends { content: string; importance?: number | null; kind?: string | null },
>(notes: T[], message: string, opts: { maxKeep?: number; minImportanceKeep?: number } = {}): T[] {
  const { maxKeep = 5, minImportanceKeep = 4 } = opts;
  const durableKind = /^(preference|misconception|strategy|win)$/i;
  const msg = message.toLowerCase();
  const tokens = new Set(
    msg
      .split(/[^\p{L}\p{N}]+/u)
      .map((t) => t.trim())
      .filter((t) => t.length >= 3),
  );

  const scored = notes.map((n) => {
    const lower = n.content.toLowerCase();
    let hits = 0;
    for (const t of tokens) {
      if (lower.includes(t)) hits += 1;
    }
    const importance = n.importance ?? 0;
    const kindBoost = durableKind.test(n.kind ?? '') ? 3 : 0;
    const importanceBoost = importance >= minImportanceKeep ? 2 : 0;
    return { n, score: hits * 2 + kindBoost + importanceBoost };
  });

  return scored
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxKeep)
    .map((x) => x.n);
}

/** Map known ## headers → section ids for whole-section budgeting. */
const HEADER_SECTION_MAP: Array<{ match: RegExp; id: keyof typeof CHAT_SECTION_PRIORITY }> = [
  { match: /^## How to teach this learner/i, id: 'howToTeach' },
  { match: /^## What I know about this learner/i, id: 'durableMemory' },
  { match: /^## My private notes/i, id: 'durableMemory' },
  { match: /^## XP /i, id: 'xp' },
  { match: /^## Learner XP/i, id: 'xp' },
  { match: /^## Learner profile/i, id: 'profile' },
  { match: /^## Mastery so far/i, id: 'mastery' },
  { match: /^## Active week/i, id: 'activeWeek' },
  { match: /^## Diagnostic/i, id: 'diagnostic' },
  { match: /^## (?:Current |Learning )?plan/i, id: 'planCatalog' },
  { match: /^## Source passages/i, id: 'ragGrounding' },
  { match: /^## Retrieved context/i, id: 'ragGrounding' },
  { match: /^## Relevant curriculum/i, id: 'curriculum' },
  { match: /^## Lesson-level guidance/i, id: 'curriculum' },
  { match: /^## Learning-plan snapshot/i, id: 'learningPlan' },
  { match: /^## Hybrid tool/i, id: 'hybridTools' },
  { match: /^## Method (?:authority|grounding)/i, id: 'methodAuthority' },
  { match: /^## PRACTICE ARENA/i, id: 'practiceArena' },
  { match: /^## Learner progress briefing/i, id: 'bilingualBriefing' },
  { match: /^## AUTHORITATIVE learner-facing status/i, id: 'statusPack' },
  { match: /^## Cross-agent|^## Handoff/i, id: 'handoffDigest' },
];

/**
 * Partition a concatenated context string into core + named packs so
 * `fitSystemSections` can drop whole packs instead of mid-string chops.
 * Content before the first optional ## pack stays in `core`.
 */
export function partitionInjectedContext(full: string): {
  core: string;
  packs: ChatContextPack[];
} {
  const parts = full.split(/\n(?=## )/);
  if (parts.length <= 1) {
    return { core: full, packs: [] };
  }

  const coreChunks: string[] = [];
  const packs: ChatContextPack[] = [];
  let seenOptional = false;

  for (const part of parts) {
    const header = part.split('\n', 1)[0] ?? '';
    const mapped = HEADER_SECTION_MAP.find((h) => h.match.test(header));
    if (!mapped) {
      if (!seenOptional) {
        coreChunks.push(part);
      } else {
        packs.push({ id: 'misc', content: part, priority: 25 });
      }
      continue;
    }
    seenOptional = true;
    packs.push({ id: mapped.id, content: part });
  }

  const merged = new Map<string, ChatContextPack>();
  for (const p of packs) {
    const prev = merged.get(String(p.id));
    if (prev) {
      const defaultPri =
        CHAT_SECTION_PRIORITY[p.id as keyof typeof CHAT_SECTION_PRIORITY] ?? 50;
      merged.set(String(p.id), {
        id: p.id,
        content: `${prev.content}\n\n${p.content}`,
        priority: Math.max(prev.priority ?? defaultPri, p.priority ?? defaultPri),
      });
    } else {
      merged.set(String(p.id), p);
    }
  }

  return {
    core: coreChunks.join('\n\n').trim(),
    packs: [...merged.values()],
  };
}

export function buildHowToTeachBlock(opts: {
  tutorMode?: string | null;
  preferredStyle?: string | null;
  attentionSpanMin?: number | null;
}): string {
  const mode = opts.tutorMode === 'direct' ? 'direct' : 'socratic';
  const style = (opts.preferredStyle ?? 'mixed').trim() || 'mixed';
  const lines = [
    '## How to teach this learner (mandatory — tailor every reply)',
    `- Dialogue mode: **${mode}**. ${
      mode === 'direct'
        ? 'Answer fully first; one check-understanding question after.'
        : 'One targeted question before explaining, unless they asked for the answer or a THIS TURN block says Direct.'
    }`,
    `- Explanation style: **${style}**.`,
  ];
  if (style === 'theory_first') {
    lines.push('- Start with the idea/definition, then one short example.');
  } else if (style === 'practice_first') {
    lines.push('- Start with a tiny worked example, then name the rule.');
  } else if (style === 'mixed') {
    lines.push('- One-sentence idea + one example in the same turn.');
  } else {
    lines.push('- Observe which of theory vs practice they respond to; mix until clear.');
  }
  if (opts.attentionSpanMin && opts.attentionSpanMin > 0) {
    lines.push(
      `- Attention: ~${opts.attentionSpanMin} min blocks — keep this reply inside that budget unless they asked for depth.`,
    );
  }
  lines.push(
    '- Use shared persona + private notes (mistakes, wins, strategies) when present. Do **not** give a generic one-size-fits-all lesson.',
    '- If a note flags a misconception on this topic, address it explicitly.',
    '- Register: calm teacher talking to this student — not a form, not a chatbot disclaimer.',
  );
  return lines.join('\n');
}
