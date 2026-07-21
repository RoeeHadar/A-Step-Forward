import { describe, expect, it } from 'vitest';
import {
  XP_PER_LEVEL,
  XP_REWARDS,
  answerSourceId,
  gateSourceId,
  levelFromXp,
  masterySourceId,
  quizPassSourceId,
  streakSourceId,
  xpProgressInLevel,
} from './learner-xp-math';

describe('levelFromXp', () => {
  it('starts at level 1 with 0 XP', () => {
    expect(levelFromXp(0)).toBe(1);
  });

  it('stays at level 1 until 100 XP', () => {
    expect(levelFromXp(99)).toBe(1);
    expect(levelFromXp(100)).toBe(2);
  });

  it('scales by XP_PER_LEVEL', () => {
    expect(levelFromXp(250)).toBe(3);
    expect(levelFromXp(XP_PER_LEVEL * 4)).toBe(5);
  });

  it('clamps negatives and non-numbers', () => {
    expect(levelFromXp(-10)).toBe(1);
    expect(levelFromXp(Number.NaN)).toBe(1);
  });
});

describe('xpProgressInLevel', () => {
  it('reports remainder and distance to next level', () => {
    expect(xpProgressInLevel(0)).toEqual({ into_level: 0, to_next: 100, level: 1 });
    expect(xpProgressInLevel(40)).toEqual({ into_level: 40, to_next: 60, level: 1 });
    expect(xpProgressInLevel(100)).toEqual({ into_level: 0, to_next: 100, level: 2 });
    expect(xpProgressInLevel(175)).toEqual({ into_level: 75, to_next: 25, level: 2 });
  });
});

describe('XP_REWARDS', () => {
  it('matches the planned economy', () => {
    expect(XP_REWARDS.correct_answer).toBe(5);
    expect(XP_REWARDS.mastery_threshold).toBe(40);
    expect(XP_REWARDS.gate_pass).toBe(25);
    expect(XP_REWARDS.quiz_pass).toBe(25);
    expect(XP_REWARDS.streak_day).toBe(10);
  });
});

describe('source id helpers', () => {
  it('builds stable idempotent keys', () => {
    expect(masterySourceId('limits')).toBe('mastery:limits');
    expect(answerSourceId('q-1')).toBe('answer:q-1');
    expect(streakSourceId('2026-07-20T12:00:00Z')).toBe('streak:2026-07-20');
    expect(gateSourceId('2026-W29')).toBe('gate:2026-W29');
    expect(quizPassSourceId('att-9')).toBe('quiz:att-9');
  });
});
