/**
 * Plan work items encoded in plan_weeks.concepts TEXT[] (zero-migration):
 * - bare concept id → lesson
 * - train:<concept_id>:<n> → train N closed items
 * - rest → rest/reflect day
 */
import {
  lessonTrainSplit,
  trainTargetCount,
  type PlanStudyMode,
  type PlanTimePhase,
} from './plan-mode';

export type PlanWorkKind = 'lesson' | 'train' | 'rest';

export interface PlanWorkItem {
  kind: PlanWorkKind;
  concept_id?: string;
  target_count?: number;
}

export function encodeWorkItem(item: PlanWorkItem): string {
  if (item.kind === 'rest') return 'rest';
  if (item.kind === 'train') {
    const id = (item.concept_id ?? '').trim();
    const n = Math.max(1, Math.floor(item.target_count ?? 10));
    return `train:${id}:${n}`;
  }
  return (item.concept_id ?? '').trim();
}

export function parseWorkItemToken(raw: string): PlanWorkItem {
  const t = String(raw ?? '').trim();
  if (!t || t === 'rest' || t.startsWith('rest:')) return { kind: 'rest' };
  if (t.startsWith('train:')) {
    const rest = t.slice('train:'.length);
    const lastColon = rest.lastIndexOf(':');
    if (lastColon > 0) {
      const concept_id = rest.slice(0, lastColon);
      const n = Number(rest.slice(lastColon + 1));
      return {
        kind: 'train',
        concept_id,
        target_count: Number.isFinite(n) && n > 0 ? Math.floor(n) : 10,
      };
    }
    return { kind: 'train', concept_id: rest || undefined, target_count: 10 };
  }
  return { kind: 'lesson', concept_id: t };
}

export function conceptIdsFromWorkItems(items: PlanWorkItem[]): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const it of items) {
    if (it.kind === 'rest' || !it.concept_id) continue;
    if (seen.has(it.concept_id)) continue;
    seen.add(it.concept_id);
    out.push(it.concept_id);
  }
  return out;
}

export function buildWeekWorkItems(
  conceptIds: string[],
  mode: PlanStudyMode,
  phase: PlanTimePhase,
): PlanWorkItem[] {
  const split = lessonTrainSplit(conceptIds.length, mode, phase);
  if (split.rest) return [{ kind: 'rest' }];

  const target = trainTargetCount(mode, phase);
  const items: PlanWorkItem[] = [];
  const lessonIds = conceptIds.slice(0, split.lessons);
  const trainIds =
    split.trains > 0
      ? conceptIds.slice(Math.max(0, conceptIds.length - split.trains))
      : [];

  for (const id of lessonIds) {
    items.push({ kind: 'lesson', concept_id: id });
  }
  const lessonSet = new Set(lessonIds);
  for (const id of trainIds) {
    if (lessonSet.has(id) && mode === 'lessons_and_train') {
      items.push({ kind: 'train', concept_id: id, target_count: target });
    } else if (!lessonSet.has(id)) {
      items.push({ kind: 'train', concept_id: id, target_count: target });
    } else if (mode === 'train_dominant') {
      items.push({ kind: 'train', concept_id: id, target_count: target });
    }
  }

  if (mode === 'train_dominant') {
    const haveTrain = new Set(
      items.filter((i) => i.kind === 'train').map((i) => i.concept_id),
    );
    for (const id of conceptIds) {
      if (!haveTrain.has(id)) {
        items.push({ kind: 'train', concept_id: id, target_count: target });
      }
    }
  }

  return items.length
    ? items
    : conceptIds.map((id) => ({ kind: 'lesson' as const, concept_id: id }));
}

export function encodeWeekWorkItems(items: PlanWorkItem[]): string[] {
  return items.map(encodeWorkItem).filter(Boolean);
}

export function applyTrainDominantOverlay(
  conceptIds: string[],
  targetCount = 12,
): PlanWorkItem[] {
  if (conceptIds.length === 0) return [{ kind: 'rest' }];
  const out: PlanWorkItem[] = [];
  const [first, ...rest] = conceptIds;
  if (first) out.push({ kind: 'lesson', concept_id: first });
  const seen = new Set<string>();
  for (const id of [first, ...rest].filter(Boolean) as string[]) {
    if (seen.has(id)) continue;
    seen.add(id);
    out.push({ kind: 'train', concept_id: id, target_count: targetCount });
  }
  return out;
}
