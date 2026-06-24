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
  sections: CurriculumSection[];
}

export const CURRICULUM_CATEGORIES: CurriculumCategory[] = [
  {
    id: 'math-hs-3',
    heLabel: 'מתמטיקה לתיכון 3 יחידות',
    enLabel: 'High School Math (3 units)',
    emoji: '📐',
    sections: [
      { id: 'arithmetic-and-algebra', heLabel: 'אריתמטיקה ואלגברה', enLabel: 'Arithmetic & Algebra' },
      { id: 'geometry-basic', heLabel: 'גאומטריה בסיסית', enLabel: 'Basic Geometry' },
      { id: 'statistics-basic', heLabel: 'סטטיסטיקה בסיסית', enLabel: 'Basic Statistics' },
      { id: 'linear-equations', heLabel: 'משוואות לינאריות', enLabel: 'Linear Equations' },
    ],
  },
  {
    id: 'math-hs-4',
    heLabel: 'מתמטיקה לתיכון 4 יחידות',
    enLabel: 'High School Math (4 units)',
    emoji: '📏',
    sections: [
      { id: 'algebra-and-functions', heLabel: 'אלגברה ופונקציות', enLabel: 'Algebra & Functions' },
      { id: 'geometry', heLabel: 'גאומטריה', enLabel: 'Geometry' },
      { id: 'trigonometry-basic', heLabel: 'טריגונומטריה בסיסית', enLabel: 'Basic Trigonometry' },
      { id: 'probability-basics', heLabel: 'יסודות ההסתברות', enLabel: 'Probability Basics' },
    ],
  },
  {
    id: 'math-hs-5',
    heLabel: 'מתמטיקה לתיכון 5 יחידות',
    enLabel: 'High School Math (5 units)',
    emoji: '🔢',
    sections: [
      { id: 'algebra-and-functions', heLabel: 'אלגברה ופונקציות', enLabel: 'Algebra & Functions' },
      { id: 'trigonometry', heLabel: 'טריגונומטריה', enLabel: 'Trigonometry' },
      { id: 'analytic-geometry', heLabel: 'גאומטריה אנליטית', enLabel: 'Analytic Geometry' },
      { id: 'calculus-hs', heLabel: 'חשבון דיפרנציאלי לתיכון', enLabel: 'Calculus (HS)' },
      { id: 'probability-hs', heLabel: 'הסתברות לתיכון', enLabel: 'Probability (HS)' },
    ],
  },
  {
    id: 'math-middle',
    heLabel: 'מתמטיקה לחטיבת ביניים',
    enLabel: 'Middle School Math',
    emoji: '🔣',
    sections: [
      { id: 'numbers-and-operations', heLabel: 'מספרים ופעולות', enLabel: 'Numbers & Operations' },
      { id: 'fractions-and-decimals', heLabel: 'שברים ועשרוניים', enLabel: 'Fractions & Decimals' },
      { id: 'ratios', heLabel: 'יחסים ופרופורציות', enLabel: 'Ratios & Proportions' },
      { id: 'intro-algebra', heLabel: 'מבוא לאלגברה', enLabel: 'Intro to Algebra' },
      { id: 'geometry-middle', heLabel: 'גאומטריה לחטיבה', enLabel: 'Middle School Geometry' },
    ],
  },
  {
    id: 'calculus',
    heLabel: 'חשבון דיפרנציאלי ואינטגרלי',
    enLabel: 'Calculus',
    emoji: '∫',
    sections: [
      { id: 'limits', heLabel: 'גבולות', enLabel: 'Limits' },
      { id: 'derivatives', heLabel: 'נגזרות', enLabel: 'Derivatives' },
      { id: 'integrals', heLabel: 'אינטגרלים', enLabel: 'Integrals' },
      { id: 'series-and-sequences', heLabel: 'סדרות וטורים', enLabel: 'Series & Sequences' },
      { id: 'multivariable-intro', heLabel: 'מבוא לחשבון רב-משתנים', enLabel: 'Multivariable Intro' },
    ],
  },
  {
    id: 'pre-calculus',
    heLabel: 'קדם-חשבון',
    enLabel: 'Pre-Calculus',
    emoji: '📈',
    sections: [
      { id: 'functions-and-graphs', heLabel: 'פונקציות וגרפים', enLabel: 'Functions & Graphs' },
      { id: 'polynomial-functions', heLabel: 'פונקציות פולינומיות', enLabel: 'Polynomial Functions' },
      { id: 'trigonometry-full', heLabel: 'טריגונומטריה מלאה', enLabel: 'Full Trigonometry' },
      { id: 'exponentials-and-logs', heLabel: 'אקספוננטים ולוגריתמים', enLabel: 'Exponentials & Logs' },
    ],
  },
  {
    id: 'linear-algebra',
    heLabel: 'אלגברה לינארית',
    enLabel: 'Linear Algebra',
    emoji: '🔲',
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
    sections: [
      { id: 'descriptive-statistics', heLabel: 'סטטיסטיקה תיאורית', enLabel: 'Descriptive Statistics' },
      { id: 'probability-theory', heLabel: 'תורת ההסתברות', enLabel: 'Probability Theory' },
      { id: 'distributions', heLabel: 'התפלגויות', enLabel: 'Distributions' },
      { id: 'hypothesis-testing', heLabel: 'בדיקת השערות', enLabel: 'Hypothesis Testing' },
      { id: 'bayesian-inference', heLabel: 'היסק בייסיאני', enLabel: 'Bayesian Inference' },
    ],
  },
  {
    id: 'physics-hs',
    heLabel: 'פיזיקה לתיכון',
    enLabel: 'High School Physics',
    emoji: '⚡',
    sections: [
      { id: 'mechanics', heLabel: 'מכניקה', enLabel: 'Mechanics' },
      { id: 'waves-and-optics', heLabel: 'גלים ואופטיקה', enLabel: 'Waves & Optics' },
      { id: 'electricity', heLabel: 'חשמל', enLabel: 'Electricity' },
      { id: 'modern-physics', heLabel: 'פיזיקה מודרנית', enLabel: 'Modern Physics' },
    ],
  },
  {
    id: 'physics-middle',
    heLabel: 'פיזיקה לחטיבת ביניים',
    enLabel: 'Middle School Physics',
    emoji: '🔭',
    sections: [
      { id: 'forces-and-motion', heLabel: 'כוחות ותנועה', enLabel: 'Forces & Motion' },
      { id: 'energy-and-work', heLabel: 'אנרגיה ועבודה', enLabel: 'Energy & Work' },
      { id: 'waves', heLabel: 'גלים', enLabel: 'Waves' },
      { id: 'light-and-sound', heLabel: 'אור וצליל', enLabel: 'Light & Sound' },
    ],
  },
  {
    id: 'physics-pre-uni',
    heLabel: 'קדם-פיזיקה לאוניברסיטה',
    enLabel: 'Pre-University Physics',
    emoji: '🎓',
    sections: [
      { id: 'kinematics', heLabel: 'קינמטיקה', enLabel: 'Kinematics' },
      { id: 'newton-laws', heLabel: 'חוקי ניוטון', enLabel: "Newton's Laws" },
      { id: 'energy-conservation', heLabel: 'שימור אנרגיה', enLabel: 'Energy Conservation' },
      { id: 'thermodynamics-intro', heLabel: 'מבוא לתרמודינמיקה', enLabel: 'Intro to Thermodynamics' },
    ],
  },
  {
    id: 'physics-1',
    heLabel: 'פיזיקה 1',
    enLabel: 'Physics 1',
    emoji: '🌀',
    sections: [
      { id: 'kinematics-advanced', heLabel: 'קינמטיקה מתקדמת', enLabel: 'Advanced Kinematics' },
      { id: 'newton-laws-advanced', heLabel: 'חוקי ניוטון מתקדם', enLabel: "Advanced Newton's Laws" },
      { id: 'work-energy-theorem', heLabel: 'משפט עבודה-אנרגיה', enLabel: 'Work-Energy Theorem' },
      { id: 'rotation', heLabel: 'תנועה סיבובית', enLabel: 'Rotation' },
      { id: 'fluids', heLabel: 'נוזלים', enLabel: 'Fluids' },
    ],
  },
  {
    id: 'physics-2',
    heLabel: 'פיזיקה 2',
    enLabel: 'Physics 2',
    emoji: '🔋',
    sections: [
      { id: 'electrostatics', heLabel: 'אלקטרוסטטיקה', enLabel: 'Electrostatics' },
      { id: 'current-circuits', heLabel: 'זרם ומעגלים', enLabel: 'Current & Circuits' },
      { id: 'magnetic-fields', heLabel: 'שדות מגנטיים', enLabel: 'Magnetic Fields' },
      { id: 'electromagnetic-induction', heLabel: 'השראה אלקטרומגנטית', enLabel: 'Electromagnetic Induction' },
      { id: 'optics-advanced', heLabel: 'אופטיקה מתקדמת', enLabel: 'Advanced Optics' },
    ],
  },
];
