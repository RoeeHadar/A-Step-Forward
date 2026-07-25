/**
 * Tiered concept resolver for chat grounding.
 *
 * Tier 'exact'      — direct substring match on concept id / name / name_he.
 * Tier 'alias'      — offline bilingual alias table lookup (longest-first).
 * Tier 'classifier' — LLM classifier, only when tiers 0–1 return 'none'.
 * Tier 'none'       — no match found.
 */
import 'server-only';
import kg from './kg-data.json';
import aliasTable from './kg-concept-aliases.json';
import { llmComplete, getLLMConfig, resolveClassifierModelChain } from '@/lib/llm-provider';

export interface KgConcept {
  id: string;
  name: string;
  name_he: string | null;
  subject: string;
  level: string;
  prerequisites: string[];
}

export interface ResolveResult {
  concepts: KgConcept[];
  tier: 'exact' | 'alias' | 'none';
}

const kgByName: Record<string, KgConcept> = Object.fromEntries(
  (kg as { concepts: KgConcept[] }).concepts.map((c) => [c.id, c]),
);

const CONCEPT_CAP = 3;

/** Replicate the exact same substring logic from chat/route.ts. */
function resolveExact(lower: string, subjects: string[]): KgConcept[] {
  const matches: KgConcept[] = [];
  for (const concept of Object.values(kgByName)) {
    if (subjects.length && !subjects.includes(concept.subject)) continue;
    const id = concept.id.replace(/_/g, ' ');
    if (
      lower.includes(id) ||
      lower.includes(concept.name.toLowerCase()) ||
      (concept.name_he && lower.includes(concept.name_he.toLowerCase()))
    ) {
      matches.push(concept);
    }
  }
  return matches.slice(0, CONCEPT_CAP);
}

/**
 * Build a sorted lookup structure once:
 * [ { conceptId, alias (lowercased), subject } ] sorted longest-alias-first.
 */
interface AliasEntry {
  conceptId: string;
  alias: string;
  subject: string;
}

const sortedAliases: AliasEntry[] = (
  Object.entries(aliasTable as Record<string, string[]>).flatMap(([conceptId, aliases]) => {
    const concept = kgByName[conceptId];
    if (!concept) return [];
    return aliases.map((a) => ({ conceptId, alias: a.toLowerCase(), subject: concept.subject }));
  })
).sort((a, b) => b.alias.length - a.alias.length);

function resolveAlias(lower: string, subjects: string[]): KgConcept[] {
  const seen = new Set<string>();
  const matches: KgConcept[] = [];
  for (const entry of sortedAliases) {
    if (subjects.length && !subjects.includes(entry.subject)) continue;
    if (!lower.includes(entry.alias)) continue;
    if (seen.has(entry.conceptId)) continue;
    seen.add(entry.conceptId);
    const concept = kgByName[entry.conceptId];
    if (concept) matches.push(concept);
    if (matches.length >= CONCEPT_CAP) break;
  }
  return matches;
}

export function resolveConceptsTiered(message: string, subjects: string[]): ResolveResult {
  if (!message) return { concepts: [], tier: 'none' };
  const lower = message.toLowerCase();

  const exact = resolveExact(lower, subjects);
  if (exact.length > 0) return { concepts: exact, tier: 'exact' };

  const alias = resolveAlias(lower, subjects);
  if (alias.length > 0) return { concepts: alias, tier: 'alias' };

  return { concepts: [], tier: 'none' };
}

// ── Tier 2: LLM classifier ───────────────────────────────────────────────────

export interface ClassifierResolveResult {
  concepts: KgConcept[];
  tier: 'exact' | 'alias' | 'classifier' | 'none';
}

const CLASSIFIER_TIMEOUT_MS = 2000;
const CLASSIFIER_MAX_TOKENS = 64;

/**
 * Trivial-message guards — skip LLM for messages that are obviously not
 * subject questions. Keep the list small; prefer false-negatives (call LLM
 * when unsure) over false-positives (skip a real question).
 *
 * Patterns:
 *   1. EN greetings / social openers
 *   2. HE greetings and common affirmations
 *   3. Exam-date meta ("מתי המבחן" / "when is the exam")
 *   4. Single-word yes/no replies
 */
const TRIVIAL_PATTERNS: RegExp[] = [
  /^\s*(hi|hello|hey|yo|bye|ciao|ok|okay|sure|thanks|thank\s+you)\b/i,
  /^\s*(שלום|היי|הי|תודה|בסדר|אוקיי|אוקי|נכון|ממש|בדיוק)\s*[,\s\!\?]?/,
  /מתי\s+ה?מבחן|מתי\s+ה?בחינה|when\s+is\s+(the\s+)?(exam|test)\b/i,
  /^\s*(yes|no|כן|לא|wow|waw)\s*[\.\!\?]*\s*$/i,
];

/**
 * Tier-2 resolver: calls a fast Groq LLM when tiers 0–1 return 'none'.
 *
 * Guards: skips messages < 12 chars or matching trivial patterns (greetings,
 * exam-date meta, single-word replies). On any error / timeout → returns
 * tier 'none'. Never throws.
 *
 * On classifier hits, logs an `ASF_RESOLVER_T2` line for the offline
 * alias-promotion flywheel (grep in Vercel logs).
 */
export async function resolveConceptsWithClassifier(
  message: string,
  subjects: string[],
): Promise<ClassifierResolveResult> {
  // Tier 0 (exact) & Tier 1 (alias) — return immediately when they hit
  const tiered = resolveConceptsTiered(message, subjects);
  if (tiered.tier !== 'none') {
    return tiered as ClassifierResolveResult;
  }

  // Guard: message too short for a subject question
  if (message.length < 12) {
    return { concepts: [], tier: 'none' };
  }
  // Guard: trivial / non-subject messages
  for (const pattern of TRIVIAL_PATTERNS) {
    if (pattern.test(message)) {
      return { concepts: [], tier: 'none' };
    }
  }

  // Build the subject-filtered concept list for the classifier prompt
  const filteredConcepts = subjects.length
    ? Object.values(kgByName).filter((c) => subjects.includes(c.subject))
    : Object.values(kgByName);

  if (filteredConcepts.length === 0) {
    return { concepts: [], tier: 'none' };
  }

  const conceptLines = filteredConcepts
    .map((c) => `${c.id} | ${c.name} | ${c.name_he ?? ''}`)
    .join('\n');

  const systemPrompt =
    `You are a concept-classifier for an AI tutoring system.\n` +
    `Given a learner message, identify which of the following concepts (if any) it is about.\n` +
    `Return STRICT JSON: {"ids": ["id1", ...]} with 0–${CONCEPT_CAP} ids ONLY from the list below.\n` +
    `Return {"ids": []} when the message is not about any listed concept.\n\n` +
    `Concepts (id | English name | Hebrew name):\n${conceptLines}`;

  const cfg = getLLMConfig();
  const models = resolveClassifierModelChain();
  const model = models[0] ?? cfg.cheapModels[0] ?? 'llama-3.1-8b-instant';

  const completionPromise = llmComplete({
    system: systemPrompt,
    messages: [{ role: 'user', content: message }],
    maxTokens: CLASSIFIER_MAX_TOKENS,
    temperature: 0,
    jsonMode: true,
    timeoutMs: CLASSIFIER_TIMEOUT_MS,
    models: [model],
  });

  // Hard outer ceiling in case the LLM client itself hangs
  const timeoutFence = new Promise<null>((resolve) =>
    setTimeout(() => resolve(null), CLASSIFIER_TIMEOUT_MS),
  );

  let result: Awaited<typeof completionPromise> | null;
  try {
    result = await Promise.race([completionPromise, timeoutFence]);
  } catch {
    return { concepts: [], tier: 'none' };
  }

  if (!result?.content) {
    return { concepts: [], tier: 'none' };
  }

  let parsed: { ids?: unknown };
  try {
    parsed = JSON.parse(result.content) as { ids?: unknown };
  } catch {
    return { concepts: [], tier: 'none' };
  }

  if (!Array.isArray(parsed.ids)) {
    return { concepts: [], tier: 'none' };
  }

  const validIds = (parsed.ids as unknown[])
    .filter((id): id is string => {
      if (typeof id !== 'string') return false;
      const concept = kgByName[id];
      if (!concept) return false;
      // Honour the subject filter even if the LLM ignores it
      if (subjects.length && !subjects.includes(concept.subject)) return false;
      return true;
    })
    .slice(0, CONCEPT_CAP);

  if (validIds.length === 0) {
    return { concepts: [], tier: 'none' };
  }

  const concepts = validIds.map((id) => kgByName[id]!);

  // Tier-2 hit: log for offline alias-promotion flywheel (grep: ASF_RESOLVER_T2)
  console.log(
    JSON.stringify({ tag: 'ASF_RESOLVER_T2', message: message.slice(0, 200), ids: validIds, subjects }),
  );

  return { concepts, tier: 'classifier' };
}
