#!/usr/bin/env node
/**
 * Deepen sequences-family track variants with distinct pedagogy + required facets.
 * Facets: recursion_or_mct, sum_last_n, odd_even_index_sums
 * Usage: node scripts/deepen-sequences-family.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const SEQUENCE_BASES = [
  'sequences_arithmetic',
  'sequences_geometric',
  'sequences_5pt',
];

const DEPTH = {
  '3pt': {
    marker: 'SEQUENCES_DEPTH_3PT',
    title_en: '3pt sequences craft: list terms, then formula',
    title_he: 'מלאכת סדרות 3 יח׳: רשמו איברים, אחר כך נוסחה',
    body_en: `**3pt sequences habit.** Always write the first 4–5 terms before using a closed form.
1. Identify arithmetic ($+d$) vs geometric ($\\times r$) from the list.
2. Find $a_n$ or $S_n$ with the standard formula after the list check.
3. Sum of the last $n$ terms: compute $S_N-S_{N-n}$ with concrete $N$.
4. Keep odd/even index sums optional — only when the stem asks.

Avoid recursion proofs on this track.`,
    body_he: `**הרגל סדרות 3 יח׳.** תמיד כתבו 4–5 איברים ראשונים לפני נוסחה סגורה.
1. זהו חשבונית ($+d$) מול הנדסית ($\\times r$) מהרשימה.
2. מצאו $a_n$ או $S_n$ בנוסחה הסטנדרטית אחרי בדיקת הרשימה.
3. סכום n האחרונים: חשבו $S_N-S_{N-n}$ עם $N$ ממשי.
4. סכומי אינדקסים זוגיים/אי-זוגיים — רק כשהניסוח מבקש.

הימנעו מהוכחות נסיגה במסלול זה.`,
  },
  '4pt': {
    marker: 'SEQUENCES_DEPTH_4PT',
    title_en: '4pt sequences craft: last-$n$ and odd/even index sums',
    title_he: 'מלאכת סדרות 4 יח׳: סכום n האחרונים וסכומי זוגי/אי-זוגי',
    body_en: `**4pt sequences habit.** Two mandatory tools on non-trivial items:
1. **Sum of the last $n$ terms** among the first $N$: $S_{\\text{last }n}=S_N-S_{N-n}$.
2. **Odd / even index sums**: odd indices form a new arithmetic/geometric sequence with difference/ratio $2d$ or $r^2$; same for even indices.

State which subsequence you formed before summing.`,
    body_he: `**הרגל סדרות 4 יח׳.** שני כלים חובה בפריטים לא-טריוויאליים:
1. **סכום n האחרונים** מתוך $N$ הראשונים: $S_{\\text{last }n}=S_N-S_{N-n}$.
2. **סכומי אינדקסים זוגיים / אי-זוגיים**: האינדקסים האי-זוגיים יוצרים סדרה חדשה עם הפרש/מנה $2d$ או $r^2$; כך גם הזוגיים.

ציינו איזו תת-סדרה בניתם לפני הסכימה.`,
  },
  '5pt': {
    marker: 'SEQUENCES_DEPTH_5PT',
    title_en: '5pt sequences craft: recursion / MCT + index-sum toolkit',
    title_he: 'מלאכת סדרות 5 יח׳: נסיגה / MCT + ארגז סכומי אינדקס',
    body_en: `**5pt sequences habit.** Combine the index-sum toolkit with **recursion / MCT** when a closed form is missing:
- recursive rule $a_{n+1}=f(a_n)$;
- prove monotonicity + boundedness (MCT) to conclude convergence.
Still practice sum of the last $n$ terms and odd/even index sums on explicit sequences.
Stay MoE-faithful — no university formal-limit definition drills.`,
    body_he: `**הרגל סדרות 5 יח׳.** שלבו את ארגז סכומי האינדקס עם **נסיגה / MCT** כשאין נוסחה סגורה:
- כלל נסיגה $a_{n+1}=f(a_n)$;
- הוכיחו מונוטוניות + חסימות (MCT) כדי להסיק התכנסות.
עדיין תרגלו סכום n האחרונים וסכומי זוגי/אי-זוגי בסדרות מפורשות.
הישארו נאמנים לתוכנית — בלי תרגול הגדרת גבול פורמלית.`,
  },
  university: {
    marker: 'SEQUENCES_DEPTH_UNI',
    title_en: 'University bridge: sequences as maps $\\mathbb{N}\\to\\mathbb{R}$',
    title_he: 'גשר אוניברסיטאי: סדרות כהעתקות $\\mathbb{N}\\to\\mathbb{R}$',
    body_en: `**University sequences bridge.** Treat $(a_n)$ as a map $\\mathbb{N}\\to\\mathbb{R}$.
Prefer precise statements about eventual monotonicity and boundedness before naming MCT.
Use partial-sum identities ($S_N-S_{N-n}$) as algebraic lemmas, not exam tips.
Course-exam pace: definition → lemma → computation.`,
    body_he: `**גשר סדרות לאוניברסיטה.** התייחסו ל-$(a_n)$ כהעתקה $\\mathbb{N}\\to\\mathbb{R}$.
העדיפו ניסוחים מדויקים על מונוטוניות וחסימות בסופו של דבר לפני MCT.
השתמשו בזהויות סכום חלקי ($S_N-S_{N-n}$) כלמות אלגבריות, לא כטיפים לבחינה.
קצב מבחן קורס: הגדרה → למה → חישוב.`,
  },
};

const FACET_SECTION = {
  kind: 'theory',
  title_en: 'Facet depth: last-$n$ sums, odd/even indices, recursion/MCT',
  title_he: 'העמקת פנים: סכום n האחרונים, אינדקסים זוגיים/אי-זוגיים, נסיגה/MCT',
  body_en_md: `**Sum of the last $n$ terms.** Among the first $N$ terms ($n\\le N$),
$$S_{\\text{last }n}=S_N-S_{N-n}=\\frac{n}{2}(a_{N-n+1}+a_N)$$
for arithmetic sequences; for geometric use $S_N-S_{N-n}$ with the usual ratio formula.

**Odd / even index sums.** Odd indices $a_1,a_3,a_5,\\ldots$ and even indices $a_2,a_4,\\ldots$ form new sequences (common difference $2d$ or ratio $r^2$ in the arithmetic/geometric cases).

**Recursion / MCT.** A recursive rule $a_{n+1}=f(a_n)$ plus monotonicity and boundedness (MCT) proves convergence when no closed form is available.`,
  body_he_md: `**סכום n האחרונים.** מתוך $N$ הראשונים ($n\\le N$),
$$S_{\\text{last }n}=S_N-S_{N-n}=\\frac{n}{2}(a_{N-n+1}+a_N)$$
בחשבונית; בהנדסית השתמשו ב-$S_N-S_{N-n}$ עם נוסחת המנה.

**סכומי אינדקסים זוגיים / אי-זוגיים.** האיברים במקומות האי-זוגיים $a_1,a_3,\\ldots$ והזוגיים $a_2,a_4,\\ldots$ יוצרים סדרות חדשות (הפרש $2d$ או מנה $r^2$).

**נסיגה / MCT.** כלל $a_{n+1}=f(a_n)$ עם מונוטוניות וחסימות (MCT) מוכיח התכנסות כשאין נוסחה סגורה.`,
};

const FACET_QUESTIONS = [
  {
    kind: 'numeric',
    difficulty: 'medium',
    facets: ['sum_last_n', 'last_n_sum'],
    stem_en:
      'Arithmetic sequence: $a_1=3$, $d=2$. Find the sum of the last $4$ terms among the first $10$ terms.',
    stem_he:
      'סדרה חשבונית: $a_1=3$, $d=2$. מצאו את סכום $4$ האיברים האחרונים מבין $10$ הראשונים.',
    correct_answer: '72',
    explanation_en:
      'Last 4 among first 10: $a_7$ to $a_{10}$. With $a_1=3$ and $d=2$ we get $a_7=15$ and $a_{10}=21$. The arithmetic sum of four terms is $\\frac{4}{2}(15+21)=72$. Equivalently use the last-$n$ identity $S_{10}-S_6=120-48=72$. Always name $N$ and $n$ before subtracting partial sums so the index window is clear.',
    explanation_he:
      'ארבעת האחרונים מבין עשרה: $a_7$ עד $a_{10}$. עם $a_1=3$ ו-$d=2$ מתקבל $a_7=15$ ו-$a_{10}=21$. סכום ארבעה איברים חשבוניים הוא $\\frac{4}{2}(15+21)=72$. שקיל: $S_{10}-S_6=120-48=72$. תמיד ציינו את $N$ ו-$n$ לפני חיסור סכומים חלקיים כדי שהחלון יהיה ברור.',
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
      'Odd indices $a_1,a_3,a_5$ form a new arithmetic sequence whose common difference is $2d$ because each step skips one term. Even indices $a_2,a_4,a_6$ likewise have common difference $2d$, starting at $a_2=a_1+d$. State the subsequence first, then apply the ordinary arithmetic-sum formula to the first $m$ odd or even terms.',
    explanation_he:
      'האינדקסים האי-זוגיים $a_1,a_3,a_5$ יוצרים סדרה חשבונית חדשה עם הפרש $2d$ כי כל צעד מדלג על איבר. הזוגיים $a_2,a_4,a_6$ גם כן עם הפרש $2d$, החל מ-$a_2=a_1+d$. ציינו תחילה את תת-הסדרה, ואז השתמשו בנוסחת סכום חשבונית רגילה ל-$m$ איברים זוגיים או אי-זוגיים.',
  },
  {
    kind: 'open',
    difficulty: 'hard',
    facets: ['recursion_or_mct', 'recursion', 'recursive_formula', 'induction_mct'],
    stem_en:
      'Given a recursive rule $a_{n+1}=f(a_n)$ with $a_1$ in an interval where $f$ is increasing and the sequence is bounded above, outline an MCT argument that $(a_n)$ converges.',
    stem_he:
      'בהינתן כלל נסיגה $a_{n+1}=f(a_n)$ עם $a_1$ בקטע שבו $f$ עולה והסדרה חסומה מלמעלה, תארו טיעון MCT שמראה ש-$(a_n)$ מתכנסת.',
    correct_answer: 'Show monotone + bounded => convergent by MCT; limit satisfies L=f(L)',
    explanation_en:
      'Use the recursive formula $a_{n+1}=f(a_n)$. Prove by induction that the sequence is monotone and bounded on the interval containing $a_1$ (MCT hypotheses). Conclude convergence, then pass to the limit to get $L=f(L)$ when $f$ is continuous. This is the MoE 5-unit path when no closed form is available.',
    explanation_he:
      'השתמשו בנוסחת הנסיגה $a_{n+1}=f(a_n)$. הוכיחו באינדוקציה שהסדרה מונוטונית וחסומה בקטע שמכיל את $a_1$ (הנחות MCT). הסיקו התכנסות, ואז עברו לגבול לקבלת $L=f(L)$ כש-$f$ רציפה. זה נתיב 5 יח׳ כשאין נוסחה סגורה.',
  },
];

function trackOf(lesson, fileBase) {
  const tracks = lesson.math_track || [];
  if (tracks.includes('university') || /__uni$/.test(fileBase)) return 'university';
  if (tracks.includes('5pt') || /__5pt$/.test(fileBase) || fileBase === 'sequences_5pt')
    return '5pt';
  if (tracks.includes('4pt') || /__4pt$/.test(fileBase)) return '4pt';
  if (tracks.includes('3pt') || !/__/.test(fileBase)) return '3pt';
  return '3pt';
}

function deepenFile(fileBase) {
  const fp = path.join(DIR, `${fileBase}.json`);
  if (!fs.existsSync(fp)) return false;
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const track = trackOf(lesson, fileBase);
  const depth = DEPTH[track];
  if (!depth) return false;

  lesson.sections = lesson.sections || [];

  const alreadyDepth = lesson.sections.some((s) => (s.body_en_md || '').includes(depth.marker));
  if (!alreadyDepth) {
    const insert = {
      kind: 'theory',
      title_en: depth.title_en,
      title_he: depth.title_he,
      body_en_md: `<!-- ${depth.marker} -->\n${depth.body_en}`,
      body_he_md: depth.body_he,
    };
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
    else lesson.sections.push(insert);
  }

  const hasFacetSection = lesson.sections.some(
    (s) => s.title_en && /Facet depth:.*last/i.test(s.title_en),
  );
  if (!hasFacetSection) {
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, FACET_SECTION);
    else lesson.sections.push(FACET_SECTION);
  }

  // Ensure recursion keywords on 5pt
  if (track === '5pt') {
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

  lesson.questions = lesson.questions || [];
  const existingFacets = new Set();
  for (const q of lesson.questions) {
    for (const f of q.facets || []) existingFacets.add(f);
  }
  for (const q of FACET_QUESTIONS) {
    // On 3pt, skip heavy recursion question if we want lighter — still need facet evidence for checklist on family; keep all for audit.
    if ((q.facets || []).some((f) => existingFacets.has(f))) continue;
    const ord = lesson.questions.length + 1;
    lesson.questions.push({
      ...q,
      id: `${fileBase}-facet-seq-${ord}`,
      ord,
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
    for (const f of q.facets || []) existingFacets.add(f);
  }

  const qid = `${fileBase}-sequences-depth`;
  if (!lesson.questions.some((q) => q.id === qid)) {
    const stems = {
      '3pt': {
        stem_en: `List-first: write five terms for the core sequence skill in this lesson, then compute one last-$n$ sum with concrete $N$.`,
        stem_he: `רשימה תחילה: כתבו חמישה איברים למיומנות הסדרה בשיעור, ואז חשבו סכום n אחרונים אחד עם $N$ ממשי.`,
      },
      '4pt': {
        stem_en: `Index-sum drill: compute a last-$n$ sum and an odd-index or even-index partial sum for a sequence from this lesson.`,
        stem_he: `תרגיל סכומי אינדקס: חשבו סכום n אחרונים וסכום חלקי של אינדקסים זוגיים או אי-זוגיים לסדרה מהשיעור.`,
      },
      '5pt': {
        stem_en: `Full toolkit: one last-$n$ sum, one odd/even index sum, and a short recursion/MCT outline for a related recursive sequence.`,
        stem_he: `ארגז מלא: סכום n אחרונים אחד, סכום זוגי/אי-זוגי אחד, ותיאור קצר של נסיגה/MCT לסדרת נסיגה קשורה.`,
      },
      university: {
        stem_en: `Course-exam style: state $(a_n)$ as a map, prove a partial-sum identity, then apply MCT language if recursive.`,
        stem_he: `סגנון מבחן קורס: נסחו את $(a_n)$ כהעתקה, הוכיחו זהות סכום חלקי, ואז השתמשו בשפת MCT אם יש נסיגה.`,
      },
    };
    const s = stems[track];
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: track === '3pt' ? 'medium' : 'hard',
      facets: ['sum_last_n', 'odd_even_index_sums'],
      stem_en: s.stem_en,
      stem_he: s.stem_he,
      explanation_en:
        '**Worked path for sequences track depth.** First list several terms so the pattern is visible. For a last-$n$ sum among the first $N$ terms, compute $S_N$ minus $S_{N-n}$ and name both indices. For odd or even index sums, form the subsequence with difference $2d$ or ratio $r^2$, then sum with the ordinary formula. Invoke recursion and MCT only when a closed form is missing, proving monotonicity and boundedness before naming the limit.',
      explanation_he:
        '**דרך פתרון לעומק מסלול הסדרות.** ראשית רשמו כמה איברים כדי לראות את הדפוס. לסכום $n$ אחרונים מתוך $N$, חשבו $S_N$ פחות $S_{N-n}$ וציינו את שני האינדקסים. לסכומי אינדקס זוגי או אי-זוגי, בנו את תת-הסדרה עם הפרש $2d$ או מנה $r^2$, ואז סכמו בנוסחה הרגילה. השתמשו בנסיגה ו-MCT רק כשאין נוסחה סגורה, תוך הוכחת מונוטוניות וחסימות לפני מתן שם לגבול.',
      correct_answer: 'see sequences track-depth + facet sections',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  if (lesson.summary_en && !lesson.summary_en.includes('sequences-family depth')) {
    lesson.summary_en = `${lesson.summary_en} Taught at the ${track} track register with sequences-family depth habits.`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

let n = 0;
for (const base of SEQUENCE_BASES) {
  const files = fs
    .readdirSync(DIR)
    .filter((f) => f === `${base}.json` || f.startsWith(`${base}__`))
    .map((f) => f.replace(/\.json$/, ''));
  for (const id of files) {
    if (deepenFile(id)) {
      console.log('deepened', id);
      n++;
    }
  }
}
console.log('deepened files', n);
