export interface SkillTagCandidate { file: string; index: number; ord: number | null; current: string[]; suggested: string; score?: number }
export function toks(s: string): Set<string>;
export function scanLesson(file: string, lesson: unknown): SkillTagCandidate[];
export function scanDir(dir: string): SkillTagCandidate[];
export function keyOf(r: SkillTagCandidate): string;
export function newCandidates(rows: SkillTagCandidate[], baseline: SkillTagCandidate[]): SkillTagCandidate[];
