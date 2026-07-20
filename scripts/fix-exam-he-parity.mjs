#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const SEQ_HE = `**סכום N אחרונים.** בסדרה חשבונית, סכום האיברים האחרונים הוא $S_{\\mathrm{last}\\,n}=S_N-S_{N-n}$. בסדרה הנדסית משתמשים באותו רעיון עם סכומים חלקיים הנדסיים — בלי לחשב מחדש מ-$a_1$.

**איברים אמצעיים / מרכזיים.** בחשבונית בת $N$ איברים, האיבר(ים) האמצעי(ים) נמצא(ים) סביב אינדקס $\\lceil N/2\\rceil$. סכום בלוק מרכזי שווה לסכום הכולל פחות שני בלוקי הקצוות.

**סכומי אינדקס זוגי ואי-זוגי.** מפצלים ל-$a_1+a_3+\\cdots$ מול $a_2+a_4+\\cdots$. כל אחת מהן היא בעצמה חשבונית עם הפרש $2d$, או הנדסית עם מנה $r^2$.

**הוכחת חשבונית / הנדסית.** מראים ש-$a_{k+1}-a_k$ קבוע לכל $k$ (חשבונית), או ש-$a_{k+1}/a_k$ קבוע (הנדסית) — או גוזרים מהנוסחה הסגורה ובודקים את ההגדרה בכיוון ההפוך.`;

const OPT_HE = `**opt_geometry — אופטימיזציה גאומטרית.** מקסימום או מינימום של שטח, היקף או מרחק באיור (מלבן במשולש, גליל בכדור, מסלול השתקפות). תמיד סקצו תחילה וכתבו אילוץ דמיון או יחס לפני $A'(x)=0$.

**opt_real_world — עולם אמיתי.** עלות, רווח, חומר או זמן — אותו חשבון דיפרנציאלי, עם יחידות ואילוצי תחום שמגיעים מהסיפור. בדקו קצוות התחום וציינו יחידות בתשובה.

**opt_functional — אופטימיזציה פונקציונלית.** מקסימום/מינימום של ערך פונקציה טהור: שיפוע מקסימלי על עקום, מרחק אנכי מקסימלי בין $f$ ל-$g$, או מקסימום $|f(x)-L|$. אין סיפור — רק קיצון של פונקציה או נגזרת בקטע.`;

function patch(id, titleSubstr, heBody) {
  const fp = path.join(DIR, `${id}.json`);
  const j = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const s = j.sections.find((sec) => (sec.title_en || '').includes(titleSubstr));
  if (!s) {
    console.warn('missing section', id, titleSubstr);
    return;
  }
  // preserve marker if present
  const m = (s.body_en_md || '').match(/<!--[^>]+-->/);
  s.body_he_md = heBody;
  if (m && s.body_en_md && !s.body_en_md.startsWith('<!--')) {
    /* keep en as-is */
  }
  fs.writeFileSync(fp, `${JSON.stringify(j, null, 2)}\n`);
  console.log('patched HE', id);
}

for (const id of [
  'sequences_5pt',
  'sequences_arithmetic',
  'sequences_arithmetic__4pt',
  'sequences_geometric',
  'sequences_geometric__4pt',
]) {
  patch(id, 'Exam archetypes: last-N', SEQ_HE);
}

for (const id of ['optimization_problems', 'optimization_related_rates']) {
  patch(id, 'Optimization archetypes', OPT_HE);
}
