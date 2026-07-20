#!/usr/bin/env node
/**
 * Deepen thin exam archetypes: sequences (last-N / middle-N / prove),
 * theoretical function graphs, optimization geo/real/functional.
 *
 * Usage: node scripts/deepen-exam-archetypes.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

function load(id) {
  const fp = path.join(DIR, `${id}.json`);
  if (!fs.existsSync(fp)) return null;
  return JSON.parse(fs.readFileSync(fp, 'utf8'));
}

function save(lesson) {
  fs.writeFileSync(path.join(DIR, `${lesson.concept_id}.json`), `${JSON.stringify(lesson, null, 2)}\n`);
  console.log('deepened', lesson.concept_id);
}

function upsertTheory(lesson, marker, section) {
  lesson.sections = lesson.sections || [];
  if (lesson.sections.some((s) => (s.body_en_md || '').includes(marker))) return;
  const insert = { ...section, body_en_md: `<!-- ${marker} -->\n${section.body_en_md}` };
  const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
  if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
  else lesson.sections.push(insert);
}

function upsertQuestions(lesson, tag, questions) {
  lesson.questions = lesson.questions || [];
  const existing = new Set();
  for (const q of lesson.questions) for (const f of q.facets || []) existing.add(f);
  for (const q of questions) {
    if ((q.facets || []).some((f) => existing.has(f))) continue;
    const ord = lesson.questions.length + 1;
    lesson.questions.push({
      ...q,
      id: `${lesson.concept_id}-${tag}-${ord}`,
      ord,
      skill_atoms: q.skill_atoms || (lesson.skill_atom_bank || []).slice(0, 2).concat(['exam_archetype']).slice(0, 2),
    });
    for (const f of q.facets || []) existing.add(f);
  }
}

const SEQ_TARGETS = [
  'sequences_arithmetic',
  'sequences_arithmetic__4pt',
  'sequences_geometric',
  'sequences_geometric__4pt',
  'sequences_5pt',
];

const SEQ_THEORY = {
  kind: 'theory',
  title_en: 'Exam archetypes: last-N, middle-N, odd/even index sums, prove arithmetic/geometric',
  title_he: 'ארכיטיפי בחינה: N אחרונים, אמצעיים, סכומי אינדקס זוגי/אי-זוגי, הוכחת חשבונית/הנדסית',
  body_en_md: `**Sum of last N terms.** For an arithmetic sequence, $S_{\\text{last }n}=S_N-S_{N-n}$. For geometric, same with geometric partial sums.

**Middle / central terms.** The middle term(s) of an arithmetic progression of $N$ terms sit at index $\\lceil N/2\\rceil$ (and neighbor if $N$ even). Sum of central block = total sum minus two end blocks.

**Odd/even index sums.** Split $a_1+a_3+\\cdots$ vs $a_2+a_4+\\cdots$ — each is itself arithmetic or geometric with common difference/ratio $2d$ or $r^2$.

**Prove arithmetic / geometric.** Show $a_{k+1}-a_k$ constant (arithmetic) or $a_{k+1}/a_k$ constant (geometric) for all $k$ in range — or use the closed form and reverse-engineer.`,
  body_he_md: `**סכום N אחרונים.** בחשבונית $S_{\\text{אחרונים}}=S_N-S_{N-n}$. בהנדסית אותו רעיון עם סכומים חלקיים.

**איברים אמצעיים.** בחשבונית של $N$ איברים — אינדקס אמצעי. סכום בלוק מרכזי = סה״כ פחות שני הקצוות.

**סכומי אינדקס זוגי/אי-זוגי.** מפצלים לשתי סדרות עם הפרש $2d$ או מנה $r^2$.

**הוכחת חשבונית/הנדסית.** מראים $a_{k+1}-a_k$ קבוע או $a_{k+1}/a_k$ קבוע לכל $k$.`,
};

const SEQ_QS = (arith) => [
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['sum_last_n'],
    archetypes: ['procedural', 'conceptual'],
    stem_en: arith
      ? 'An arithmetic sequence has $S_{20}=500$ and $S_{15}=300$. Find the sum of the last 5 terms ($S_{20}-S_{15}$).'
      : 'A geometric sequence has partial sums $S_{10}$ and $S_{7}$. Express the sum of the last 3 terms as $S_{10}-S_{7}$ and compute when $a_1=2$, $r=2$.',
    stem_he: arith
      ? 'סדרה חשבונית עם $S_{20}=500$ ו-$S_{15}=300$. מצאו את סכום 5 האיברים האחרונים ($S_{20}-S_{15}$).'
      : 'סדרה הנדסית עם $S_{10}$ ו-$S_{7}$. ביטאו את סכום 3 האחרונים כ-$S_{10}-S_{7}$ וחשבו כאשר $a_1=2$, $r=2$.',
    correct_answer: arith ? '200' : 'S_10-S_7 = 2^7+2^8+2^9',
    explanation_en: arith
      ? 'Sum of last 5 = $S_{20}-S_{15}=500-300=200$. This last-N pattern avoids recomputing from $a_1$.'
      : 'Last-N geometric sum is $S_N-S_{N-n}$. With $a_1=2$, $r=2$: $S_{10}-S_7=2(2^{10}-1)-2(2^7-1)=2^{11}-2-2^8+2=2^{11}-2^8-0$ wait — prefer listing $a_8+a_9+a_{10}=2^7+2^8+2^9$.',
    explanation_he: arith
      ? 'סכום 5 אחרונים = $S_{20}-S_{15}=200$. תבנית N-אחרונים חוסכת חישוב מחדש מ-$a_1$.'
      : 'סכום N אחרונים = $S_N-S_{N-n}$. עם $a_1=2$, $r=2$: $a_8+a_9+a_{10}=2^7+2^8+2^9$.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['sum_middle_n'],
    archetypes: ['procedural', 'proof'],
    stem_en:
      'For an arithmetic sequence of 9 terms, identify the middle term (index 5) and express the sum of the three central terms in terms of $a_1$ and $d$.',
    stem_he:
      'בסדרה חשבונית בת 9 איברים, זהו את האיבר האמצעי (אינדקס 5) ובטאו את סכום שלושת האיברים המרכזיים במונחי $a_1$ ו-$d$.',
    correct_answer: 'a5=a1+4d; sum a4+a5+a6 = 3a1+12d',
    explanation_en:
      'Middle index of 9 terms is 5: $a_5=a_1+4d$. Central three: $a_4+a_5+a_6=(a_1+3d)+(a_1+4d)+(a_1+5d)=3a_1+12d$. Middle-N sums are end-trimmed total sums.',
    explanation_he:
      'אמצע של 9 הוא אינדקס 5. שלושה מרכזיים: $3a_1+12d$. סכומי אמצע = סה״כ פחות קצוות.',
  },
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['odd_even_index_sums'],
    archetypes: ['procedural', 'conceptual'],
    stem_en: arith
      ? 'In arithmetic $a_n=a_1+(n-1)d$, write the sum of odd-indexed terms $a_1+a_3+\\cdots+a_{2k-1}$ as an arithmetic series with difference $2d$.'
      : 'In geometric $a_n=a_1 r^{n-1}$, show odd-indexed terms form a geometric series with ratio $r^2$.',
    stem_he: arith
      ? 'בחשבונית, כתבו את סכום האיברים באינדקס אי-זוגי כסדרה עם הפרש $2d$.'
      : 'בהנדסית, הראו שאיברי אינדקס אי-זוגי הם הנדסית עם מנה $r^2$.',
    correct_answer: arith ? 'AP with first a1, diff 2d' : 'GP with first a1, ratio r^2',
    explanation_en: arith
      ? 'Odd indices: $a_1,a_3,a_5,\\ldots$ differ by $2d$. Sum with standard AP formulas on this thinned sequence.'
      : 'Odd indices: $a_1, a_1 r^2, a_1 r^4,\\ldots$ — geometric with ratio $r^2$.',
    explanation_he: arith
      ? 'אינדקסים אי-זוגיים נבדלים ב-$2d$. סכום עם נוסחאות חשבונית על הסדרה המדוללת.'
      : 'אינדקסים אי-זוגיים: מנה $r^2$.',
  },
  {
    kind: 'derivation',
    difficulty: 'hard',
    facets: [arith ? 'prove_arithmetic' : 'prove_geometric'],
    archetypes: ['proof', 'procedural'],
    stem_en: arith
      ? 'Prove that the sequence defined by $a_n=3n+1$ is arithmetic by showing $a_{n+1}-a_n$ is constant.'
      : 'Prove that $a_n=5\\cdot 2^{n-1}$ is geometric by showing $a_{n+1}/a_n$ is constant.',
    stem_he: arith
      ? 'הוכיחו ש-$a_n=3n+1$ חשבונית על ידי הצגת $a_{n+1}-a_n$ קבוע.'
      : 'הוכיחו ש-$a_n=5\\cdot 2^{n-1}$ הנדסית על ידי הצגת $a_{n+1}/a_n$ קבוע.',
    correct_answer: arith ? 'a_{n+1}-a_n=3' : 'a_{n+1}/a_n=2',
    explanation_en: arith
      ? '$a_{n+1}-a_n=(3(n+1)+1)-(3n+1)=3$, constant — definition of arithmetic (prove arithmetic).'
      : '$a_{n+1}/a_n=(5\\cdot 2^n)/(5\\cdot 2^{n-1})=2$, constant — definition of geometric (prove geometric).',
    explanation_he: arith
      ? '$a_{n+1}-a_n=3$ קבוע — הגדרת חשבונית.'
      : '$a_{n+1}/a_n=2$ קבוע — הגדרת הנדסית.',
  },
];

for (const id of SEQ_TARGETS) {
  const lesson = load(id);
  if (!lesson) continue;
  const arith = /arithmetic/i.test(id) || id === 'sequences_5pt';
  upsertTheory(lesson, 'EXAM_SEQ_ARCHETYPES', SEQ_THEORY);
  upsertQuestions(lesson, 'seq-arch', SEQ_QS(arith));
  // sequences_5pt needs both prove facets
  if (id === 'sequences_5pt') {
    upsertQuestions(lesson, 'seq-arch-g', [
      {
        kind: 'derivation',
        difficulty: 'hard',
        facets: ['prove_geometric'],
        archetypes: ['proof'],
        stem_en:
          'Prove $b_n=3\\cdot(\\tfrac12)^{n-1}$ is geometric by showing the ratio $b_{n+1}/b_n$ is constant.',
        stem_he:
          'הוכיחו ש-$b_n=3\\cdot(\\tfrac12)^{n-1}$ הנדסית על ידי יחס קבוע $b_{n+1}/b_n$.',
        correct_answer: 'ratio = 1/2',
        explanation_en: '$b_{n+1}/b_n=1/2$ for all $n$ — prove geometric.',
        explanation_he: '$b_{n+1}/b_n=1/2$ — הוכחת הנדסית.',
      },
    ]);
  }
  save(lesson);
}

// Function analysis theoretical graphs
const FN_TARGETS = [
  'function_analysis_5pt',
  'derivatives_applications',
  'derivatives_applications__5pt',
  'functions_quadratic__5pt',
];

const FN_THEORY = {
  kind: 'theory',
  title_en: 'Theoretical graph reasoning: y=k meetings; graph ↔ f / f′ / F',
  title_he: 'חשיבה תיאורטית מגרף: מפגשי y=k; גרף ↔ f / f′ / F',
  body_en_md: `**Meetings with $y=k$.** Horizontally slice the graph: count solutions of $f(x)=k$, read multiplicity from tangency vs crossing.

**Graph ↔ $f$ / $f'$ / $F$.** From a sketch of $f$, deduce sign charts of $f'$ (increasing/decreasing) and of an antiderivative $F$ (area accumulation). From a sketch of $f'$, reconstruct monotonicity of $f$. Multi-part stems chain these readings.`,
  body_he_md: `**מפגשים עם $y=k$.** חיתוך אופקי: ספירת פתרונות ל-$f(x)=k$, ריבוי ממשיק מול חוצה.

**גרף ↔ $f$ / $f'$ / $F$.** משרטוט של $f$ גוזרים סימני $f'$ ושל קדומה $F$. משרטוט של $f'$ משחזרים מונוטוניות של $f$. ניסוחים רב-חלקיים משרשרים את הקריאות.`,
};

const FN_QS = [
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['theoretical_graph_reasoning', 'meetings_y_equals_k', 'y_equals_k'],
    archetypes: ['graphical', 'conceptual', 'procedural'],
    stem_en:
      'Given a sketch of $y=f(x)$, for each horizontal line $y=k$ in a multi-part stem, count intersections and state whether $f(x)=k$ has 0, 1, or 2 solutions in the drawn window. Then, from the same graph, mark intervals where $f^{\\prime}>0$.',
    stem_he:
      'נתון שרטוט של $y=f(x)$. לכל ישר $y=k$ בחלקי השאלה, ספרו חיתוכים וקבעו אם ל-$f(x)=k$ יש 0, 1 או 2 פתרונות. מאותו גרף סמנו קטעים שבהם $f^{\\prime}>0$.',
    correct_answer: 'count y=k hits; f\'>0 where f increasing',
    explanation_en:
      'Theoretical graph reasoning: each $y=k$ is a horizontal probe. Tangency means a repeated root. Where the graph rises, $f^{\\prime}>0$; where it falls, $f^{\\prime}<0$. Link part (a) root counts to part (b) derivative signs without recomputing a formula.',
    explanation_he:
      'חשיבה תיאורטית מגרף: כל $y=k$ הוא בדיקה אופקית. משיקות = שורש כפול. עלייה ⟹ $f^{\\prime}>0$. קשרו בין ספירת שורשים לסימני נגזרת בלי לחשב נוסחה מחדש.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['graph_f_fprime_F', 'theoretical_graph_reasoning'],
    archetypes: ['graphical', 'proof'],
    stem_en:
      'From a given graph of $f$, sketch a qualitative graph of $f^{\\prime}$ and of an antiderivative $F$ with $F(0)=0$, explaining how zeros of $f^{\\prime}$ match extrema of $f$ and how area under $f$ builds $F$.',
    stem_he:
      'מגרף נתון של $f$, שרטטו איכותית את $f^{\\prime}$ ואת קדומה $F$ עם $F(0)=0$; הסבירו איך אפסי $f^{\\prime}$ תואמים קיצון של $f$ ואיך שטח תחת $f$ בונה את $F$.',
    correct_answer: 'f\' zeros at f extrema; F accumulates signed area',
    explanation_en:
      'Zeros of $f^{\\prime}$ sit at horizontal tangents of $f$. $F(x)=\\int_0^x f$ grows when $f>0$ and shrinks when $f<0$. Exam multipart: (a) read $f$, (b) draw $f^{\\prime}$, (c) draw $F$.',
    explanation_he:
      'אפסי $f^{\\prime}$ בנקודות משיק אופקי של $f$. $F$ צוברת שטח מסומן. חלקי בחינה: (א) $f$, (ב) $f^{\\prime}$, (ג) $F$.',
  },
];

for (const id of FN_TARGETS) {
  const lesson = load(id);
  if (!lesson) continue;
  upsertTheory(lesson, 'EXAM_FN_GRAPH', FN_THEORY);
  upsertQuestions(lesson, 'fn-graph', FN_QS);
  save(lesson);
}

// Optimization archetypes
const OPT_TARGETS = ['optimization_problems', 'optimization_related_rates'];

const OPT_THEORY = {
  kind: 'theory',
  title_en: 'Optimization archetypes: geometry, real-world, functional',
  title_he: 'ארכיטיפי אופטימיזציה: גאומטריה, עולם אמיתי, פונקציונלי',
  body_en_md: `**opt_geometry.** Max/min area, perimeter, or distance in a geometric figure (rectangle in triangle, cylinder in sphere, path reflection).

**opt_real_world.** Cost, profit, material, time — same calculus, with units and domain constraints from the story.

**opt_functional.** Maximize/minimize a pure function value: max slope on a curve, max vertical distance between $f$ and $g$, max $|f(x)-L|$.`,
  body_he_md: `**opt_geometry.** מקסימום/מינימום שטח, היקף או מרחק באיור גאומטרי.

**opt_real_world.** עלות, רווח, חומר, זמן — אותו חשבון דיפרנציאלי עם יחידות ואילוצי תחום.

**opt_functional.** מקסימום שיפוע, מרחק אנכי מקסימלי בין $f$ ל-$g$, מקסימום $|f(x)-L|$.`,
};

const OPT_QS = [
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['opt_geometry'],
    archetypes: ['procedural', 'graphical'],
    stem_en:
      'A rectangle is inscribed in a right triangle with legs 6 and 8, with sides parallel to the legs. Maximize the rectangle area: set $A(x)$, find critical points, and justify the maximum.',
    stem_he:
      'מלבן חסום במשולש ישר-זווית עם ניצבים 6 ו-8, צלעות מקבילות לניצבים. מקסמו את שטח המלבן: הציבו $A(x)$, מצאו נקודות קריטיות והצדיקו מקסימום.',
    correct_answer: 'A(x)=x*(8-8x/6); A\'=0; endpoint check',
    explanation_en:
      'Geometry optimization: similar triangles give height in terms of width $x$, area $A(x)=x\\cdot h(x)$, solve $A\'(x)=0$, compare endpoints. Sketch first — opt_geometry stems fail when the figure constraint is wrong.',
    explanation_he:
      'אופטימיזציה גאומטרית: דמיון משולשים נותן גובה במונחי $x$, $A(x)=x\\cdot h(x)$, $A\'=0$, השוואת קצוות. סקצו תחילה.',
  },
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['opt_real_world'],
    archetypes: ['procedural', 'conceptual'],
    stem_en:
      'A manufacturer’s cost is $C(x)=x^3-6x^2+20x$ for $x$ units (domain $x\\ge 0$). Find the production level that minimizes average cost $C(x)/x$ on $(0,\\infty)$, interpreting units.',
    stem_he:
      'עלות יצרן $C(x)=x^3-6x^2+20x$ ל-$x$ יחידות. מצאו רמת ייצור שמזערת עלות ממוצעת $C(x)/x$ ב-$(0,\\infty)$, עם יחידות.',
    correct_answer: 'minimize A(x)=x^2-6x+20; A\'=2x-6=0 => x=3',
    explanation_en:
      'Real-world optimization: average cost $A(x)=C(x)/x=x^2-6x+20$, $A\'(x)=2x-6=0\\Rightarrow x=3$. Check $A\'\'>0$. State that $x$ is units produced — units matter in the story.',
    explanation_he:
      'אופטימיזציה מהעולם האמיתי: $A(x)=C/x$, $A\'=0$ ב-$x=3$. ציינו יחידות.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['opt_functional'],
    archetypes: ['procedural', 'proof'],
    stem_en:
      'For $f(x)=x^2$ and $g(x)=2x$ on $[0,2]$, maximize the vertical distance $|f(x)-g(x)|$. Also state where the slope of $f$ is maximized on the interval.',
    stem_he:
      'עבור $f(x)=x^2$ ו-$g(x)=2x$ ב-$[0,2]$, מקסמו את המרחק האנכי $|f-g|$. ציינו גם היכן שיפוע $f$ מקסימלי בקטע.',
    correct_answer: 'h=x^2-2x; critical at x=1; slope of f is 2x max at x=2',
    explanation_en:
      'Functional optimization: maximize $|f-g|$ via $h=f-g$ critical points; max slope of $f$ is $\\max f\'$ on the interval (here $f\'=2x$, max at right endpoint). These are pure function-value / derivative extrema — not a story problem.',
    explanation_he:
      'אופטימיזציה פונקציונלית: מקסמו $|f-g|$ דרך קריטיים של $h=f-g$; שיפוע מקסימלי = מקס׳ $f\'$ בקטע.',
  },
];

for (const id of OPT_TARGETS) {
  const lesson = load(id);
  if (!lesson) continue;
  upsertTheory(lesson, 'EXAM_OPT_ARCH', OPT_THEORY);
  upsertQuestions(lesson, 'opt-arch', OPT_QS);
  save(lesson);
}

console.log('deepen-exam-archetypes: done');
