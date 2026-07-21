/** Pure XP math — safe for unit tests (no server-only / Neon). */

export const XP_REWARDS = {
  correct_answer: 5,
  mastery_threshold: 40,
  gate_pass: 25,
  quiz_pass: 25,
  streak_day: 10,
} as const;

export const XP_PER_LEVEL = 100;
export const MASTERY_XP_THRESHOLD = 0.7;

export function levelFromXp(totalXp: number): number {
  const t = Math.max(0, Math.floor(Number(totalXp) || 0));
  return 1 + Math.floor(t / XP_PER_LEVEL);
}

export function xpProgressInLevel(totalXp: number): {
  into_level: number;
  to_next: number;
  level: number;
} {
  const t = Math.max(0, Math.floor(Number(totalXp) || 0));
  const level = levelFromXp(t);
  const into_level = t % XP_PER_LEVEL;
  return { into_level, to_next: XP_PER_LEVEL - into_level, level };
}

export function masterySourceId(conceptId: string): string {
  return `mastery:${conceptId}`;
}

export function answerSourceId(questionId: string): string {
  return `answer:${questionId}`;
}

export function streakSourceId(dayIso: string): string {
  return `streak:${dayIso.slice(0, 10)}`;
}

export function gateSourceId(weekKey: string): string {
  return `gate:${weekKey}`;
}

export function quizPassSourceId(attemptId: string): string {
  return `quiz:${attemptId}`;
}
