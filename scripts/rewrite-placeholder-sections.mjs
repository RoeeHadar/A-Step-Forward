#!/usr/bin/env node
/**
 * Replace any section body in content_export.json whose body links to
 * /content/lessons/ (the local-only PDF fallback paths that can't be
 * hosted on Vercel due to file-size limits) with the OCR-coming-soon
 * placeholder text. Idempotent: sections without a /content/lessons/
 * link are untouched.
 */
import fs from 'node:fs';
import path from 'node:path';

const inputPath = process.argv[2] ?? path.join('scripts', 'seed_data', 'content_export.json');

const data = JSON.parse(fs.readFileSync(inputPath, 'utf-8'));
let rewritten = 0;

for (const section of data.sections ?? []) {
  if (typeof section.body_md !== 'string') continue;
  if (!section.body_md.includes('/content/lessons/')) continue;
  const title = section.title || 'שיעור';
  section.body_md =
    `### ${title}\n\n` +
    `החומר עבור נושא זה מבוסס על קובץ PDF שעדיין לא ניתן לחילוץ ` +
    `טקסט אוטומטי (PDF סרוק / מקודד בפונט מוטמע).\n\n` +
    `החומר יתווסף בקרוב לאחר שלב ה-OCR. בינתיים, ניתן לפנות למורה ` +
    `או לבחור שיעור אחר באותו נושא.\n`;
  rewritten += 1;
}

fs.writeFileSync(inputPath, JSON.stringify(data, null, 2), 'utf-8');
console.log(`[rewrite] ${rewritten} placeholder sections updated in ${inputPath}`);
