/**
 * Curriculum category catalogue — aligned with Israeli Bagrut curriculum levels.
 *
 * `points_levels` is used to:
 *   - Filter the onboarding self-assessment concepts to the student's track.
 *   - Tag lessons and questions with which track they belong to.
 *   - Drive the quiz builder's concept picker.
 *
 * Values: '3pt' | '4pt' | '5pt' | 'hs_physics' | 'calc1' | 'la' | 'physics1'
 *
 * Removed: 'physics-2' (university EM / optics / quantum — out of scope for
 *          our target audience: high school, pre-university, first-year uni).
 * Removed: multivariable / Calculus 2/3 sections — same reason.
 */

export type PointsLevel = '3pt' | '4pt' | '5pt' | 'hs_physics' | 'calc1' | 'la' | 'physics1';

export interface CurriculumSection {
  id: string;
  heLabel: string;
  enLabel: string;
}

export interface CurriculumCategory {
  id: string;
  heLabel: string;
  enLabel: string;
  emoji: string;
  points_levels: PointsLevel[];
  sections: CurriculumSection[];
}

export const CURRICULUM_CATEGORIES: CurriculumCategory[] = [
  {
    id: 'math-hs-3',
    heLabel: 'מתמטיקה לתיכון 3 יחידות',
    enLabel: 'High School Math (3 units)',
    emoji: '📐',
    points_levels: ['3pt'],
    sections: [
      { id: 'arithmetic-and-algebra', heLabel: 'אריתמטיקה ואלגברה', enLabel: 'Arithmetic & Algebra' },
      { id: 'linear-equations', heLabel: 'משוואות מדרגה ראשונה', enLabel: 'Linear Equations' },
      { id: 'quadratic-functions', heLabel: 'פונקציה ריבועית', enLabel: 'Quadratic Functions' },
      { id: 'geometry-basic', heLabel: 'גיאומטריה בסיסית', enLabel: 'Basic Geometry' },
      { id: 'sequences-basic', heLabel: 'סדרות חשבוניות', enLabel: 'Arithmetic Sequences' },
      { id: 'statistics-basic', heLabel: 'סטטיסטיקה בסיסית', enLabel: 'Basic Statistics' },
      { id: 'probability-basic', heLabel: 'הסתברות בסיסית', enLabel: 'Basic Probability' },
    ],
  },
  {
    id: 'math-hs-4',
    heLabel: 'מתמטיקה לתיכון 4 יחידות',
    enLabel: 'High School Math (4 units)',
    emoji: '📏',
    points_levels: ['4pt'],
    sections: [
      { id: 'algebra-and-functions', heLabel: 'אלגברה ופונקציות', enLabel: 'Algebra & Functions' },
      { id: 'quadratic-equations', heLabel: 'משוואות ריבועיות', enLabel: 'Quadratic Equations' },
      { id: 'exponential-functions', heLabel: 'פונקציה אקספוננציאלית', enLabel: 'Exponential Functions' },
      { id: 'geometry', heLabel: 'גיאומטריה', enLabel: 'Geometry' },
      { id: 'trigonometry-basic', heLabel: 'טריגונומטריה בסיסית', enLabel: 'Basic Trigonometry' },
      { id: 'sequences-geometric', heLabel: 'סדרות הנדסיות', enLabel: 'Geometric Sequences' },
      { id: 'analytic-geometry-basic', heLabel: 'גיאומטריה אנליטית', enLabel: 'Analytic Geometry' },
      { id: 'combinatorics', heLabel: 'קומבינטוריקה', enLabel: 'Combinatorics' },
    ],
  },
  {
    id: 'math-hs-5',
    heLabel: 'מתמטיקה לתיכון 5 יחידות',
    enLabel: 'High School Math (5 units)',
    emoji: '🔢',
    points_levels: ['5pt'],
    sections: [
      { id: 'logarithms', heLabel: 'לוגריתמים', enLabel: 'Logarithms' },
      { id: 'trigonometry', heLabel: 'טריגונומטריה', enLabel: 'Trigonometry' },
      { id: 'analytic-geometry', heLabel: 'גיאומטריה אנליטית', enLabel: 'Analytic Geometry' },
      { id: 'vectors-2d', heLabel: 'וקטורים', enLabel: 'Vectors' },
      { id: 'calculus-hs', heLabel: 'חשבון דיפרנציאלי לתיכון', enLabel: 'Calculus (HS)' },
      { id: 'integrals-hs', heLabel: 'אינטגרלים', enLabel: 'Integrals' },
      { id: 'probability-hs', heLabel: 'הסתברות', enLabel: 'Probability & Distributions' },
    ],
  },
  {
    id: 'math-middle',
    heLabel: 'מתמטיקה לחטיבת ביניים',
    enLabel: 'Middle School Math',
    emoji: '🔣',
    points_levels: [],
    sections: [
      { id: 'numbers-and-operations', heLabel: 'מספרים ופעולות', enLabel: 'Numbers & Operations' },
      { id: 'fractions-and-decimals', heLabel: 'שברים ועשרוניים', enLabel: 'Fractions & Decimals' },
      { id: 'ratios', heLabel: 'יחסים ופרופורציות', enLabel: 'Ratios & Proportions' },
      { id: 'intro-algebra', heLabel: 'מבוא לאלגברה', enLabel: 'Intro to Algebra' },
      { id: 'geometry-middle', heLabel: 'גיאומטריה לחטיבה', enLabel: 'Middle School Geometry' },
    ],
  },
  {
    id: 'calculus',
    heLabel: 'חדו״א 1 (אוניברסיטה)',
    enLabel: 'Calculus 1 (University)',
    emoji: '∫',
    points_levels: ['calc1'],
    sections: [
      { id: 'limits', heLabel: 'גבולות', enLabel: 'Limits' },
      { id: 'derivatives', heLabel: 'נגזרות', enLabel: 'Derivatives' },
      { id: 'integrals', heLabel: 'אינטגרלים', enLabel: 'Integrals' },
      { id: 'series-and-sequences', heLabel: 'סדרות וטורים', enLabel: 'Sequences & Series' },
    ],
  },
  {
    id: 'pre-calculus',
    heLabel: 'מבוא לחשבון — הכנה לאוניברסיטה',
    enLabel: 'Pre-Calculus (University Prep)',
    emoji: '📈',
    points_levels: ['5pt', 'calc1'],
    sections: [
      { id: 'functions-and-graphs', heLabel: 'פונקציות וגרפים', enLabel: 'Functions & Graphs' },
      { id: 'polynomial-functions', heLabel: 'פונקציות פולינומיות', enLabel: 'Polynomial Functions' },
      { id: 'trigonometry-full', heLabel: 'טריגונומטריה מלאה', enLabel: 'Full Trigonometry' },
      { id: 'exponentials-and-logs', heLabel: 'אקספוננטים ולוגריתמים', enLabel: 'Exponentials & Logs' },
    ],
  },
  {
    id: 'linear-algebra',
    heLabel: 'אלגברה לינארית (אוניברסיטה)',
    enLabel: 'Linear Algebra (University)',
    emoji: '🔲',
    points_levels: ['la'],
    sections: [
      { id: 'vectors', heLabel: 'וקטורים', enLabel: 'Vectors' },
      { id: 'matrices-and-systems', heLabel: 'מטריצות ומערכות משוואות', enLabel: 'Matrices & Systems' },
      { id: 'determinants', heLabel: 'דטרמיננטות', enLabel: 'Determinants' },
      { id: 'eigenvalues', heLabel: 'ערכים עצמיים', enLabel: 'Eigenvalues' },
      { id: 'linear-transformations', heLabel: 'העתקות לינאריות', enLabel: 'Linear Transformations' },
    ],
  },
  {
    id: 'statistics',
    heLabel: 'סטטיסטיקה והסתברות',
    enLabel: 'Statistics & Probability',
    emoji: '📊',
    points_levels: ['5pt', 'calc1'],
    sections: [
      { id: 'descriptive-statistics', heLabel: 'סטטיסטיקה תיאורית', enLabel: 'Descriptive Statistics' },
      { id: 'probability-theory', heLabel: 'תורת ההסתברות', enLabel: 'Probability Theory' },
      { id: 'distributions', heLabel: 'התפלגויות', enLabel: 'Distributions' },
    ],
  },
  {
    id: 'physics-hs',
    heLabel: 'פיזיקה לתיכון — בגרות 5 יח׳',
    enLabel: 'High School Physics (Bagrut 5 units)',
    emoji: '⚡',
    points_levels: ['hs_physics'],
    sections: [
      { id: 'mechanics', heLabel: 'מכניקה', enLabel: 'Mechanics' },
      { id: 'waves-and-optics', heLabel: 'גלים ואופטיקה', enLabel: 'Waves & Optics' },
      { id: 'electricity', heLabel: 'חשמל ומגנטיות', enLabel: 'Electricity & Magnetism' },
      { id: 'modern-physics', heLabel: 'פיזיקה מודרנית', enLabel: 'Modern Physics' },
    ],
  },
  {
    id: 'physics-middle',
    heLabel: 'מדעים לחטיבת ביניים',
    enLabel: 'Middle School Science',
    emoji: '🔭',
    points_levels: [],
    sections: [
      { id: 'forces-and-motion', heLabel: 'כוחות ותנועה', enLabel: 'Forces & Motion' },
      { id: 'energy-and-work', heLabel: 'אנרגיה ועבודה', enLabel: 'Energy & Work' },
      { id: 'waves', heLabel: 'גלים', enLabel: 'Waves' },
      { id: 'light-and-sound', heLabel: 'אור וצליל', enLabel: 'Light & Sound' },
    ],
  },
  {
    id: 'physics-1',
    heLabel: 'פיזיקה 1 — מכניקה ותרמודינמיקה',
    enLabel: 'Physics 1 (University) — Mechanics & Thermodynamics',
    emoji: '🌀',
    points_levels: ['physics1'],
    sections: [
      { id: 'kinematics-advanced', heLabel: 'קינמטיקה', enLabel: 'Kinematics' },
      { id: 'newton-laws-advanced', heLabel: 'חוקי ניוטון', enLabel: "Newton's Laws" },
      { id: 'work-energy-theorem', heLabel: 'עבודה ואנרגיה', enLabel: 'Work & Energy' },
      { id: 'momentum-advanced', heLabel: 'תנע ומומנט', enLabel: 'Momentum & Angular Momentum' },
      { id: 'rotation', heLabel: 'תנועה סיבובית', enLabel: 'Rotation' },
      { id: 'oscillations', heLabel: 'תנדות', enLabel: 'Oscillations & Waves' },
      { id: 'fluids', heLabel: 'מכניקת זורמים', enLabel: 'Fluid Mechanics' },
      { id: 'thermodynamics', heLabel: 'תרמודינמיקה', enLabel: 'Thermodynamics' },
    ],
  },
];
