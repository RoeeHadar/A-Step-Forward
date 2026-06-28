const fs = require('fs');
const path = require('path');

const dir = 'scripts/seed_data/lessons';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.json'));
let totalFixed = 0;

for (const file of files) {
  const p = path.join(dir, file);
  let d;
  try { d = JSON.parse(fs.readFileSync(p, 'utf8')); } catch(e) { continue; }
  let fileFixed = 0;

  for (const section of (d.sections || [])) {
    const byl = section.body_by_level || {};
    for (const [level, body] of Object.entries(byl)) {
      const he = (body.body_he_md || '').trim();
      const en = (body.body_en_md || '').trim();
      
      // 1. No Hebrew characters at all
      const hasHebrew = /[\u0590-\u05FF]/.test(he);
      
      // 2. Identical to English (copy-paste)
      const isIdenticalToEn = he === en && he.length > 0;
      
      // 3. Repetitive LLM corruption: a 4-word phrase repeated >3 times
      let repeatCount = 0;
      const firstWords = he.split(/\s+/).slice(0, 4).join(' ');
      if (firstWords.length > 8) {
        const count = he.split(firstWords).length - 1;
        repeatCount = count;
      }
      
      // 4. Obvious LLM debug artifacts
      const hasBadText = /let.{0,5}s correct|i made an error|self-correction/i.test(he);

      if (!hasHebrew || repeatCount > 3 || isIdenticalToEn || hasBadText) {
        const reason = !hasHebrew ? 'no-hebrew'
          : repeatCount > 3 ? 'repeat-x' + repeatCount
          : isIdenticalToEn ? 'copy-of-english'
          : 'bad-text';
        // Fall back to English text — better than broken Hebrew
        body.body_he_md = en;
        fileFixed++;
        console.log('  [' + file + '] ' + section.id + '/' + level + ': fixed (' + reason + ')');
      }
    }
  }

  if (fileFixed > 0) {
    fs.writeFileSync(p, JSON.stringify(d, null, 2));
    totalFixed += fileFixed;
  }
}

console.log('\nDone. Fixed ' + totalFixed + ' corrupted Hebrew body_by_level entries across ' + files.length + ' lessons.');
