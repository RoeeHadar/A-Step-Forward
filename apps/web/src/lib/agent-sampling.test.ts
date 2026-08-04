import { describe, expect, it } from 'vitest';
import {
  DEFAULT_SAMPLING,
  ROUTER_SAMPLING,
  resolveAgentSampling,
} from './agent-sampling';

describe('resolveAgentSampling', () => {
  it('returns distinct per-agent profiles', () => {
    expect(resolveAgentSampling('tutor')).toEqual({ temperature: 0.3, topP: 0.9 });
    expect(resolveAgentSampling('coach')).toEqual({ temperature: 0.2, topP: 0.9 });
    expect(resolveAgentSampling('reviewer')).toEqual({ temperature: 0.2, topP: 0.85 });
    expect(resolveAgentSampling('mentor')).toEqual({ temperature: 0.5, topP: 0.95 });
  });

  it('falls back to the default profile for unknown agents', () => {
    expect(resolveAgentSampling('orchestrator')).toEqual(DEFAULT_SAMPLING);
    expect(resolveAgentSampling('')).toEqual(DEFAULT_SAMPLING);
  });

  it('router sampling is deterministic', () => {
    expect(ROUTER_SAMPLING).toEqual({ temperature: 0, topP: 1 });
  });

  it('all profiles use valid ranges', () => {
    for (const agent of ['tutor', 'coach', 'reviewer', 'mentor']) {
      const s = resolveAgentSampling(agent);
      expect(s.temperature).toBeGreaterThanOrEqual(0);
      expect(s.temperature).toBeLessThanOrEqual(1);
      expect(s.topP).toBeGreaterThan(0);
      expect(s.topP).toBeLessThanOrEqual(1);
    }
  });
});
