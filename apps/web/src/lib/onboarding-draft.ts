const DRAFT_KEY = 'asf_onboarding_draft_v1';

export interface OnboardingDraft {
  step: number;
  s1: Record<string, unknown>;
  s2: Record<string, unknown>;
  s3: Record<string, unknown>;
  s4: Record<string, unknown>;
  tutorMode: string;
}

export function loadOnboardingDraft(): OnboardingDraft | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as OnboardingDraft;
  } catch {
    return null;
  }
}

export function saveOnboardingDraft(draft: OnboardingDraft): void {
  if (typeof window === 'undefined') return;
  try {
    sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  } catch {
    // quota or private mode — ignore
  }
}

export function clearOnboardingDraft(): void {
  if (typeof window === 'undefined') return;
  sessionStorage.removeItem(DRAFT_KEY);
}
