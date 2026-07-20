#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

function fix(id, mut) {
  const fp = path.join(DIR, `${id}.json`);
  const j = JSON.parse(fs.readFileSync(fp, 'utf8'));
  mut(j);
  fs.writeFileSync(fp, `${JSON.stringify(j, null, 2)}\n`);
  console.log('fixed', id);
}

fix('analytic_geometry_parabola', (j) => {
  const s = j.sections.find((sec) => (sec.title_en || '').includes('Parabola focus'));
  if (s) {
    s.body_he_md = `**מוקד–מכוון.** עבור $y^2=4px$, המוקד הוא $(p,0)$ והמכוון הוא $x=-p$. כל נקודה $P$ על הפרבולה מקיימת $|PF|=$ מרחק למכוון — זו ההגדרה המרכזית בתוכנית, בלי חיתוך עקום תלת־ממדי.

**קשר למעגל.** מעגל שעובר בקדקוד וחולק משיק עם הפרבולה, או חותך אותה בנקודות ידועות, הוא כלי שכיח: מציבים, מחסרים, וקוראים מיתר משותף. הישארו אלגבריים — הציבו וספרו נקודות חיתוך לפני שאתם מציירים מסקנות.`;
  }
});

fix('functions_even_odd', (j) => {
  const intro = j.sections.find((s) => s.kind === 'intro');
  if (intro) {
    intro.body_he_md = `פונקציה **זוגית** מקיימת $f(-x)=f(x)$ לכל $x$ בתחום סימטרי (סימטריית מראה סביב ציר $y$). פונקציה **אי־זוגית** מקיימת $f(-x)=-f(x)$ (סימטריית סיבוב $180^\\circ$ סביב הראשית). ניסוחי בחינה מבקשים להחליט מהנוסחה **או מהגרף**, ואז לנצל זוגיות באינטגרלים על $[-a,a]$.`;
  }
  const th = j.sections.find((s) => (s.title_en || '').includes('Even function, odd'));
  if (th) {
    th.body_he_md = `**פונקציה זוגית.** $f(-x)=f(x)$. הגרף סימטרי ביחס לציר $y$. דוגמאות: $x^2$, $\\cos x$.

**פונקציה אי־זוגית.** $f(-x)=-f(x)$. הגרף סימטרי תחת סיבוב $180^\\circ$ סביב הראשית. דוגמאות: $x^3$, $\\sin x$.

**זוגיות מהגרף.** שיקפו ביחס לציר $y$ — אם הגרף חופף, הפונקציה זוגית. סובבו $180^\\circ$ סביב הראשית — אם חופף, אי־זוגית. אחרת אף אחת מהן.

**אינטגרלים.** בקטע $[-a,a]$, פונקציה אי־זוגית אינטגרבילית נותנת $0$; פונקציה זוגית נותנת $2\\int_0^a f$.`;
  }
});

fix('probability_bernoulli', (j) => {
  const already = j.sections.some((s) => (s.body_en_md || '').includes('THREE_WAY_BRIDGE'));
  if (already) return;
  const sumIdx = j.sections.findIndex((s) => s.kind === 'summary');
  const sec = {
    kind: 'theory',
    title_en: 'Related tool: three-way tables vs Bernoulli setup',
    title_he: 'כלי קשור: טבלאות תלת־ממדיות מול הצבת ברנולי',
    body_en_md: `<!-- THREE_WAY_BRIDGE -->
When data arrive as a **three-way table** (for example track × gender × pass), you can still extract a success probability $p$ for a Bernoulli/binomial model by fixing two factors and reading the pass rate from the remaining two-way slice. Tree diagrams and three-way tables organize the same joint information; Bernoulli setup begins only after $p$ (and $n$) are identified.`,
    body_he_md: `כשהנתונים מגיעים כ**טבלה תלת־ממדית** (למשל מסלול × מגדר × עבר), אפשר עדיין לחלץ הסתברות הצלחה $p$ למודל ברנולי/בינומי על ידי קיבוע שני גורמים וקריאת שיעור העברה מהשכבה הדו־ממדית שנותרה. דיאגרמות עץ וטבלאות תלת־ממדיות מארגנות את אותו מידע משותף; הצבת ברנולי מתחילה רק אחרי שזיהיתם את $p$ (ואת $n$).`,
  };
  if (sumIdx >= 0) j.sections.splice(sumIdx, 0, sec);
  else j.sections.push(sec);
});
