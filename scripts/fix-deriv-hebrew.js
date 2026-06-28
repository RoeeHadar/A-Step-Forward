const fs = require("fs");
const path = "scripts/seed_data/lessons/derivatives_intro.json";
const d = JSON.parse(fs.readFileSync(path, "utf8"));

let fixed = 0;
d.sections.forEach(s => {
  if (!s.body_by_level) return;
  ["3pt","4pt","5pt","calc1"].forEach(level => {
    const blevel = s.body_by_level[level];
    if (!blevel) return;
    if (blevel.body_he_md) {
      const orig = blevel.body_he_md;
      // Fix wrong terminology: replace incorrect Hebrew terms with correct ones
      blevel.body_he_md = orig
        .replace(/\u05d4\u05e0\u05d9\u05e6\u05d1/g, "\u05e0\u05d2\u05d6\u05e8\u05ea")   // הניצב -> נגזרת
        .replace(/\u05e0\u05d9\u05e6\u05d1(?!\u05d9\u05ea)/g, "\u05e0\u05d2\u05d6\u05e8\u05ea")  // ניצב (not ניצבית) -> נגזרת
        .replace(/ongoing-ness/g, "\u05e7\u05e6\u05d1 \u05d4\u05e9\u05d9\u05e0\u05d5\u05d9")  // ongoing-ness -> קצב השינוי
        .replace(/\u05e0\u05d9\u05e6\u05d1\u05d5\u05ea/g, "\u05e0\u05d2\u05d6\u05e8\u05d5\u05ea");  // ניצבות -> נגזרות
      if (blevel.body_he_md !== orig) fixed++;
    }
  });
});

fs.writeFileSync(path, JSON.stringify(d, null, 2), "utf8");
console.log("derivatives_intro: fixed Hebrew terminology in " + fixed + " level blocks");
