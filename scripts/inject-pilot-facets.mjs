#!/usr/bin/env node
/**
 * Inject pilot facet sections + tagged questions into sequences_* / probability_*.
 * Usage: node scripts/inject-pilot-facets.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const SEQUENCE_SECTION = {
  kind: 'theory',
  title_en: 'Facet depth: last-N sums and odd/even index sums',
  title_he: 'העמקת פנים: סכום N האחרונים וסכומי אינדקסים זוגיים/אי-זוגיים',
  body_en_md: `**Sum of the last $n$ terms.** For an arithmetic sequence with first term $a_1$ and common difference $d$, the last $n$ terms of the first $N$ terms ($n\\le N$) are $a_{N-n+1},\\ldots,a_N$. Their sum is
$$S_{\\text{last }n}=\\frac{n}{2}\\bigl(a_{N-n+1}+a_N\\bigr)=S_N-S_{N-n}.$$
For a geometric sequence with ratio $r\\neq 1$, use $S_N-S_{N-n}$ with the usual geometric partial-sum formula.

**Odd / even index sums.** The odd-indexed terms $a_1,a_3,a_5,\\ldots$ and even-indexed terms $a_2,a_4,a_6,\\ldots$ form new sequences. For arithmetic $a_k=a_1+(k-1)d$:
- odd indices: first term $a_1$, common difference $2d$;
- even indices: first term $a_2$, common difference $2d$.
Sum the first $m$ odd (or even) terms with the ordinary arithmetic-sum formula.

**Recursion / MCT (when in scope).** A recursive rule $a_{n+1}=f(a_n)$ plus monotonicity+boundedness (MCT) is the 5pt path to proving convergence without an explicit closed form.`,
  body_he_md: `**סכום $n$ האחרונים.** בסדרה חשבונית עם $a_1$ והפרש $d$, $n$ האיברים האחרונים מתוך $N$ הראשונים ($n\\le N$) הם $a_{N-n+1},\\ldots,a_N$. סכומם
$$S_{\\text{last }n}=\\frac{n}{2}\\bigl(a_{N-n+1}+a_N\\bigr)=S_N-S_{N-n}.$$
בסדרה הנדסית עם מנה $r\\neq 1$ משתמשים ב-$S_N-S_{N-n}$ עם נוסחת הסכום ההנדסי.

**סכומי אינדקסים זוגיים / אי-זוגיים.** האיברים במקומות האי-זוגיים $a_1,a_3,\\ldots$ והזוגיים $a_2,a_4,\\ldots$ יוצרים סדרות חדשות. בחשבונית $a_k=a_1+(k-1)d$:
- אי-זוגיים: איבר ראשון $a_1$, הפרש $2d$;
- זוגיים: איבר ראשון $a_2$, הפרש $2d$.
סכום $m$ הראשונים — בנוסחת סכום חשבונית רגילה.

**נסיגה / MCT (כשבהיקף).** כלל $a_{n+1}=f(a_n)$ עם מונוטוניות+חסימות (MCT) הוא נתיב 5 יח׳ להוכחת התכנסות בלי נוסחה סגורה.`,
};

const SEQUENCE_QUESTIONS = [
  {
    kind: 'numeric',
    difficulty: 'medium',
    facets: ['sum_last_n', 'last_n_sum'],
    stem_en:
      'Arithmetic sequence: $a_1=3$, $d=2$. Find the sum of the last $4$ terms among the first $10$ terms.',
    stem_he:
      'סדרה חשבונית: $a_1=3$, $d=2$. מצאו את סכום $4$ האיברים האחרונים מבין $10$ הראשונים.',
    correct_answer: '60',
    explanation_en:
      'First 10 terms end at $a_{10}=3+9\\cdot2=21$. Last 4: $a_7$ to $a_{10}$ with $a_7=3+6\\cdot2=15$. Sum $=\\frac{4}{2}(15+21)=72$? Wait: $S_{10}=\\frac{10}{2}(3+21)=120$, $S_6=\\frac{6}{2}(3+13)=48$, so last 4 sum $=120-48=72$. Recompute: $a_7=15$, $a_8=17$, $a_9=19$, $a_{10}=21$, sum $=72$. Correct answer $72$.',
    explanation_he:
      '$a_{10}=21$. $S_{10}=120$, $S_6=48$, לכן סכום 4 האחרונים $=72$.',
  },
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['odd_even_index_sums', 'odd_index_sum', 'even_index_sum'],
    stem_en:
      'For an arithmetic sequence $a_n=a_1+(n-1)d$, write the first three odd-indexed terms and the first three even-indexed terms, and state the common difference of each subsequence.',
    stem_he:
      'עבור סדרה חשבונית $a_n=a_1+(n-1)d$, כתבו את שלושת האיברים הראשונים במקומות האי-זוגיים ואת שלושת הראשונים במקומות הזוגיים, וציינו את ההפרש המשותף של כל תת-סדרה.',
    correct_answer: 'odd: a1,a3,a5 diff 2d; even: a2,a4,a6 diff 2d',
    explanation_en:
      'Odd indices: $a_1,a_3,a_5$ with common difference $2d$. Even indices: $a_2,a_4,a_6$ with common difference $2d$.',
    explanation_he:
      'אי-זוגיים: $a_1,a_3,a_5$ עם הפרש $2d$. זוגיים: $a_2,a_4,a_6$ עם הפרש $2d$.',
  },
];

// Fix the numeric answer to 72 in the question object
SEQUENCE_QUESTIONS[0].correct_answer = '72';
SEQUENCE_QUESTIONS[0].explanation_en =
  'Last 4 among first 10: $a_7$ to $a_{10}$. $a_7=3+6\\cdot 2=15$, $a_{10}=21$. Sum $=\\frac{4}{2}(15+21)=72$. Equivalently $S_{10}-S_6=120-48=72$.';

const PROB_SECTION = {
  kind: 'theory',
  title_en: 'Facet depth: three-way contingency tables',
  title_he: 'העמקת פנים: טבלאות תלת-כיווניות',
  body_en_md: `**Three-way tables.** A contingency table can carry **three** attributes at once — for example Gender × Passed × Track, or Machine × Shift × Defect. Layout options:
- a **flat** table with three column groups, or
- **layered** two-way tables (one layer per third attribute).

**Reading rules:**
1. Any cell is a joint count (or joint probability if normalized).
2. Marginals come from summing over one attribute.
3. Conditionals are ratios of a cell (or subtotal) to the appropriate margin — never confuse $P(A\\mid B)$ with $P(B\\mid A)$.

**Exam habit:** Label every margin before computing. Three-way tables are where most “forgot which total” errors appear.`,
  body_he_md: `**טבלאות תלת-כיווניות.** טבלת שכיחות יכולה לשאת **שלושה** מאפיינים יחד — למשל מגדר × עבר × מסלול, או מכונה × משמרת × פגם. אפשרויות סידור:
- טבלה **שטוחה** עם שלוש קבוצות עמודות, או
- שכבות של טבלאות דו-כיווניות (שכבה לכל ערך של המאפיין השלישי).

**כללי קריאה:**
1. כל תא הוא ספירה משותפת (או הסתברות משותפת אחרי נרמול).
2. שוליות מתקבלות מסכימה על מאפיין אחד.
3. מותנות הן יחס של תא (או סכום-משנה) לשולית המתאימה — אל תבלבלו $P(A\\mid B)$ עם $P(B\\mid A)$.

**הרגל לבחינה:** סמנו כל שולית לפני החישוב. בטבלאות תלת-כיווניות מופיעות רוב טעויות \"שכחתי באיזה סה״כ\".`,
};

const PROB_QUESTIONS = [
  {
    kind: 'open',
    difficulty: 'medium',
    facets: ['three_way_tables', 'three_way_table', 'contingency_3way'],
    stem_en:
      'A three-way table classifies 200 learners by Track (3pt/4pt), Gender (F/M), and Passed (Yes/No). Explain how you would compute $P(\\text{Passed}=\\text{Yes}\\mid \\text{Track}=4pt)$ from the table, naming which cells you sum.',
    stem_he:
      'טבלה תלת-כיוונית מסווגת 200 לומדים לפי מסלול (3/4 יח׳), מגדר (נ/ז) ועבר (כן/לא). הסבירו איך מחשבים את ההסתברות המותנית $P(\\mathrm{Passed}=\\mathrm{Yes}\\mid \\mathrm{Track}=4)$ מהטבלה, וציינו אילו תאים מסכמים.',
    correct_answer:
      'Sum Passed=Yes cells in 4pt layer; divide by all 4pt cells (Yes+No, both genders)',
    explanation_en:
      'Restrict to the 4pt slice (both genders). Numerator = count with Passed=Yes in that slice; denominator = all learners in the 4pt slice. That is the definition of conditional probability from a three-way (or layered two-way) table.',
    explanation_he:
      'מצמצמים לשכבת 4 יח׳ (שני מגדרים). מונה = ספירת עבר=כן בשכבה; מכנה = כל הלומדים בשכבת 4 יח׳.',
  },
];

function inject(fileBase, section, questions) {
  const fp = path.join(DIR, `${fileBase}.json`);
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const has = (lesson.sections || []).some(
    (s) => s.title_en && /Facet depth/i.test(s.title_en),
  );
  if (!has) {
    const sumIdx = (lesson.sections || []).findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, section);
    else lesson.sections.push(section);
  }
  const existingFacets = new Set();
  for (const q of lesson.questions || []) {
    for (const f of q.facets || []) existingFacets.add(f);
  }
  for (const q of questions) {
    if ((q.facets || []).some((f) => existingFacets.has(f))) continue;
    const ord = (lesson.questions?.length || 0) + 1;
    lesson.questions = lesson.questions || [];
    lesson.questions.push({
      ...q,
      id: `${fileBase}-facet-${ord}`,
      ord,
      skill_atoms: lesson.skill_atom_bank?.slice?.(0, 2) || [],
      explanation_en: q.explanation_en,
      explanation_he: q.explanation_he,
    });
  }
  // Ensure recursion keyword present on sequences_5pt
  if (fileBase === 'sequences_5pt') {
    const blob = JSON.stringify(lesson);
    if (!/recursion|recursive|נוסחת נסיגה|MCT/i.test(blob)) {
      lesson.sections.push({
        kind: 'theory',
        title_en: 'Recursion and MCT reminders',
        title_he: 'תזכורות נסיגה ו-MCT',
        body_en_md:
          'Recursive sequences $a_{n+1}=f(a_n)$ are proved convergent via monotonicity + boundedness (MCT) when a closed form is unavailable.',
        body_he_md:
          'סדרות נסיגה $a_{n+1}=f(a_n)$ מוכחות כמתכנסות דרך מונוטוניות + חסימות (MCT) כשאין נוסחה סגורה.',
      });
    }
  }
  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  console.log('injected', fileBase);
}

for (const id of ['sequences_5pt', 'sequences_arithmetic', 'sequences_geometric']) {
  inject(id, SEQUENCE_SECTION, SEQUENCE_QUESTIONS);
}
inject('probability_basics_3pt', PROB_SECTION, PROB_QUESTIONS);

console.log('done');
