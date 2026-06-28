const fs = require("fs");

// FIX 1: arithmetic.json - replace 3pt theory section English body_he_md with Hebrew
const arithPath = "scripts/seed_data/lessons/arithmetic.json";
const arith = JSON.parse(fs.readFileSync(arithPath, "utf8"));
arith.sections.forEach(s => {
  if (s.body_by_level && s.body_by_level["3pt"] && s.id === "theory" || (s.body_by_level && s.body_by_level["3pt"] && /^[A-Za-z]/.test((s.body_by_level["3pt"].body_he_md || "").trim()))) {
    const he = s.body_by_level["3pt"].body_he_md || "";
    if (/^[A-Za-z]/.test(he.trim())) {
      s.body_by_level["3pt"].body_he_md = "\u05de\u05e2\u05e8\u05db\u05ea \u05d4\u05de\u05e1\u05e4\u05e8\u05d9\u05dd \u05d4\u05e9\u05dc\u05de\u05d5\u05ea \u05db\u05d5\u05dc\u05dc\u05ea \u05d0\u05e8\u05d1\u05e2\u05d4 \u05e1\u05d5\u05d2\u05d9 \u05de\u05e1\u05e4\u05e8\u05d9\u05dd \u05e2\u05d9\u05e7\u05e8\u05d9\u05d9\u05dd:\n\n- **\u05de\u05e1\u05e4\u05e8\u05d9\u05dd \u05e9\u05dc\u05de\u05d9\u05dd** (\u05db\u05e0\u05d9\u05d9\u05dd): \u2026, -2, -1, 0, 1, 2, 3, \u2026\n- **\u05e9\u05d1\u05e8\u05d9\u05dd** (\u05e8\u05d0\u05e6\u05d9\u05d5\u05e0\u05dc\u05d9\u05d9\u05dd): \u05de\u05e1\u05e4\u05e8\u05d9\u05dd \u05db\u05de\u05d5 $\\frac{3}{4}$ \u05d0\u05d5 $\\frac{1}{2}$\n- **\u05de\u05e1\u05e4\u05e8\u05d9\u05dd \u05e2\u05e9\u05e8\u05d5\u05e0\u05d9\u05d9\u05dd**: \u05db\u05de\u05d5 0.5, 3.14\n- **\u05d0\u05d7\u05d5\u05d6\u05d9\u05dd**: \u05d7\u05dc\u05e7 \u05de\u05de\u05d0\u05d4, \u05db\u05de\u05d5 50% = $\\frac{1}{2}$\n\n**\u05e1\u05d3\u05e8 \u05d4\u05e4\u05e2\u05d5\u05dc\u05d5\u05ea (PEMDAS):**\n1. \u05e1\u05d5\u05d2\u05e8\u05d9\u05d9\u05dd ()\n2. \u05d7\u05d6\u05e7\u05d5\u05ea $a^b$\n3. \u05db\u05e4\u05dc \u05d5\u05d7\u05d9\u05dc\u05d5\u05e7 \u05de\u05e9\u05de\u05d0\u05dc \u05dc\u05d9\u05de\u05d9\u05df\n4. \u05d7\u05d9\u05d1\u05d5\u05e8 \u05d5\u05d7\u05d9\u05e1\u05d5\u05e8 \u05de\u05e9\u05de\u05d0\u05dc \u05dc\u05d9\u05de\u05d9\u05df\n\n\u05d3\u05d5\u05d2\u05de\u05d0: $2 + 3 \\times 4 = 2 + 12 = 14$ (\u05dc\u05d0 $5 \\times 4 = 20$!)";
      console.log("Fixed arithmetic 3pt theory body_he_md (" + he.slice(0,40) + " -> Hebrew)");
    }
  }
});
fs.writeFileSync(arithPath, JSON.stringify(arith, null, 2), "utf8");

// FIX 2: analytic_geometry Q7-Q10 - normalize schema to match Q1-Q6 (stem_en/stem_he/correct_index)
const agPath = "scripts/seed_data/lessons/analytic_geometry.json";
const ag = JSON.parse(fs.readFileSync(agPath, "utf8"));
ag.questions = ag.questions.map((q, idx) => {
  // Only transform new questions (ag_5pt_q1 through ag_5pt_q4)
  if (!q.id || !q.id.startsWith("ag_5pt")) return q;
  // Find correct_index from answer_en in options_en
  const correctIdx = (q.options_en || []).indexOf(q.answer_en);
  return {
    ord: 7 + (parseInt(q.id.slice(-1)) - 1),
    kind: "mcq",
    difficulty: q.difficulty,
    points_level_min: "5pt",
    stem_en: q.body_en,
    stem_he: q.body_he,
    options_en: q.options_en,
    options_he: q.options_he,
    correct_index: correctIdx >= 0 ? correctIdx : 0,
    explanation_en: q.explanation_en,
    explanation_he: q.explanation_he,
    skill_atoms: q.skill_atoms
  };
});
fs.writeFileSync(agPath, JSON.stringify(ag, null, 2), "utf8");
console.log("Normalized analytic_geometry Q7-Q10 schema. Total questions:", ag.questions.length);
console.log("Q7 sample keys:", Object.keys(ag.questions[6]).join(", "));
