import type { LearnerProfileRow } from '@/lib/neon-db';

export function learnerHasPhysicsEnrollment(
  profile: LearnerProfileRow | null | undefined,
): boolean {
  if (!profile) return false;
  const personality = profile.personality_profile as { hs_physics?: boolean } | null;
  return (
    profile.points_group === 'hs_physics' ||
    profile.subjects.includes('physics') ||
    profile.subjects.includes('bagrut_physics') ||
    personality?.hs_physics === true
  );
}

export function deriveSubjectFromProfile(profile: LearnerProfileRow | null): string {
  if (!profile) return 'math_5';

  const pg = profile.points_group;
  const subjects = profile.subjects ?? [];

  const hasPhysics =
    pg === 'hs_physics' ||
    subjects.includes('physics') ||
    subjects.includes('bagrut_physics');

  if (hasPhysics && (pg === 'hs_physics' || !pg || !/^(\d|3pt|4pt|5pt)$/.test(pg))) {
    return 'hs_physics';
  }

  const units = pg?.replace(/pt$/, '') ?? '';
  if (units === '3') return 'math_3';
  if (units === '4') return 'math_4';
  if (units === '5') return 'math_5';

  return 'math_5';
}

export function deriveSubjectsStudied(profile: LearnerProfileRow | null): string[] {
  if (!profile) return [];

  const out: string[] = [];
  const pg = profile.points_group;

  if (pg === '3pt') out.push('math_3pt');
  else if (pg === '4pt') out.push('math_4pt');
  else if (pg === '5pt') out.push('math_5pt');
  else if (pg && /^math/.test(pg)) out.push(pg);
  else if (pg && !['hs_physics'].includes(pg)) {
    out.push('math_5pt');
  }

  if (learnerHasPhysicsEnrollment(profile)) {
    out.push('physics');
  }

  return [...new Set(out)];
}
