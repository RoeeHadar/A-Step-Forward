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

// Natural, earthy agent identities — each a distinct botanical/mineral hue
// that sits within the "warm editorial" palette rather than neon primaries.
export const agentColors: Record<string, string> = {
  tutor: 'hsl(158 40% 32%)', // evergreen
  mentor: 'hsl(28 55% 45%)', // ochre / bronze
  coach: 'hsl(122 34% 34%)', // moss
  qa_explainer: 'hsl(192 38% 36%)', // slate-teal
  reviewer: 'hsl(12 55% 48%)', // clay / terracotta
  note_taker: 'hsl(340 32% 48%)', // dusty rose
  accessibility: 'hsl(174 34% 34%)', // pine-teal
};
