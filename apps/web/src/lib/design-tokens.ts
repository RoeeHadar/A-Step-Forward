/** Design tokens — single source for spacing, radii, and motion. */
export const tokens = {
  radius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  },
  spacing: {
    page: '1.5rem',
    section: '2rem',
    card: '1.5rem',
  },
  motion: {
    fast: '150ms',
    normal: '250ms',
    slow: '400ms',
  },
} as const;

export const agentColors: Record<string, string> = {
  tutor: 'hsl(221 83% 53%)',
  mentor: 'hsl(262 83% 58%)',
  coach: 'hsl(142 71% 45%)',
  qa_explainer: 'hsl(199 89% 48%)',
  reviewer: 'hsl(24 95% 53%)',
  note_taker: 'hsl(330 81% 60%)',
  accessibility: 'hsl(173 80% 40%)',
};
