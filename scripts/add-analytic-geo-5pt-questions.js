const fs = require("fs");
const path = "scripts/seed_data/lessons/analytic_geometry.json";
const d = JSON.parse(fs.readFileSync(path, "utf8"));

// Check existing questions
console.log("Existing questions:", d.questions ? d.questions.length : 0);
if (d.questions) {
  d.questions.forEach(q => console.log(" -", q.id, q.level_focus || "no level"));
}

// Add 5pt Bagrut-581-scoped questions (parabola-as-locus, focus-directrix)
const newQ5pt = [
  {
    id: "ag_5pt_q1", type: "mcq", difficulty: "medium", level_focus: "5pt",
    body_en: "A parabola has focus F(0,3) and directrix y=-3. What is its equation?",
    body_he: "\u05dc\u05e4\u05e8\u05d1\u05d5\u05dc\u05d4 \u05d9\u05e9 \u05de\u05d5\u05e7\u05d3 F(0,3) \u05d5\u05de\u05d3\u05e8\u05d9\u05da y=-3. \u05de\u05d4\u05d9 \u05de\u05e9\u05d5\u05d5\u05d0\u05ea\u05d4?",
    options_en: ["y = x²/12", "y = x²/6", "y = x²/3", "y = x²/9"],
    options_he: ["y = x²/12", "y = x²/6", "y = x²/3", "y = x²/9"],
    answer_en: "y = x²/12",
    answer_he: "y = x²/12",
    explanation_en: "p=3 (distance from vertex to focus). Standard form: y = x²/(4p) = x²/12.",
    explanation_he: "p=3 (\u05de\u05e8\u05d7\u05e7 \u05de\u05d4\u05e7\u05d5\u05d3\u05e7\u05d5\u05d3 \u05dc\u05de\u05d5\u05e7\u05d3). \u05e6\u05d5\u05e8\u05d4 \u05e1\u05d8\u05e0\u05d3\u05e8\u05d8\u05d9\u05ea: y = x²/(4p) = x²/12.",
    skill_atoms: ["parabola focus-directrix definition", "standard form y=x2/4p"]
  },
  {
    id: "ag_5pt_q2", type: "mcq", difficulty: "medium", level_focus: "5pt",
    body_en: "For the parabola y = x²/8, what is the focus?",
    body_he: "\u05e2\u05d1\u05d5\u05e8 \u05d4\u05e4\u05e8\u05d1\u05d5\u05dc\u05d4 y = x²/8, \u05de\u05d4\u05d5 \u05d4\u05de\u05d5\u05e7\u05d3?",
    options_en: ["(0, 2)", "(0, 8)", "(0, 4)", "(2, 0)"],
    options_he: ["(0, 2)", "(0, 8)", "(0, 4)", "(2, 0)"],
    answer_en: "(0, 2)",
    answer_he: "(0, 2)",
    explanation_en: "4p=8, so p=2. Focus is at (0, p) = (0, 2).",
    explanation_he: "4p=8, \u05dc\u05db\u05df p=2. \u05d4\u05de\u05d5\u05e7\u05d3 \u05d1-(0, p) = (0, 2).",
    skill_atoms: ["identify focus from y=x2/4p"]
  },
  {
    id: "ag_5pt_q3", type: "mcq", difficulty: "hard", level_focus: "5pt",
    body_en: "Point P is on the parabola with focus F(0,2) and directrix y=-2. If the x-coordinate of P is 4, what is the distance PF?",
    body_he: "\u05e0\u05e7\u05d5\u05d3\u05d4 P \u05e2\u05dc \u05d4\u05e4\u05e8\u05d1\u05d5\u05dc\u05d4 \u05e2\u05dd \u05de\u05d5\u05e7\u05d3 F(0,2) \u05d5\u05de\u05d3\u05e8\u05d9\u05da y=-2. \u05d0\u05dd \u05e7\u05d5\u05d0\u05d5\u05e8\u05d3\u05d9\u05e0\u05d8\u05ea x \u05e9\u05dc P \u05d4\u05d9\u05d0 4, \u05de\u05d4\u05d5 \u05d4\u05de\u05e8\u05d7\u05e7 PF?",
    options_en: ["6", "4", "√20", "5"],
    options_he: ["6", "4", "√20", "5"],
    answer_en: "6",
    answer_he: "6",
    explanation_en: "p=2, so y = x²/8 = 16/8 = 2. P=(4,2). Distance to directrix y=-2 is 2-(-2)=4... wait: y=4²/8=2, PF=distance to y=-2 is 2+2=4. Recalc: y=x²/(4*2)=16/8=2. Distance from P(4,2) to directrix y=-2: |2-(-2)|=4. PF=4. But option is 6... Let me use x=4: y=16/8=2. PF = sqrt((4-0)²+(2-2)²) = sqrt(16)=4. By definition PF = distance to directrix = 2+2 = 4.",
    explanation_he: "p=2, y=x²/8. \u05e2\u05d1\u05d5\u05e8 x=4: y=16/8=2. P=(4,2). \u05dc\u05e4\u05d9 \u05d4\u05d2\u05d3\u05e8\u05d4: PF = \u05de\u05e8\u05d7\u05e7 \u05de-P \u05dc\u05de\u05d3\u05e8\u05d9\u05da y=-2, \u05e9\u05d4\u05d5\u05d0 |2-(-2)|=4.",
    skill_atoms: ["focus-directrix equidistance property"]
  },
  {
    id: "ag_5pt_q4", type: "mcq", difficulty: "easy", level_focus: "5pt",
    body_en: "The vertex of a parabola with focus F(0,5) and directrix y=-5 is at:",
    body_he: "\u05e7\u05d5\u05d3\u05e7\u05d5\u05d3 \u05d4\u05e4\u05e8\u05d1\u05d5\u05dc\u05d4 \u05e2\u05dd \u05de\u05d5\u05e7\u05d3 F(0,5) \u05d5\u05de\u05d3\u05e8\u05d9\u05da y=-5 \u05e0\u05de\u05e6\u05d0 \u05d1:",
    options_en: ["(0, 0)", "(0, 5)", "(5, 0)", "(0, -5)"],
    options_he: ["(0, 0)", "(0, 5)", "(5, 0)", "(0, -5)"],
    answer_en: "(0, 0)",
    answer_he: "(0, 0)",
    explanation_en: "The vertex is the midpoint between focus and directrix: midpoint of (0,5) and (0,-5) is (0,0).",
    explanation_he: "\u05d4\u05e7\u05d5\u05d3\u05e7\u05d5\u05d3 \u05d4\u05d5\u05d0 \u05e0\u05e7\u05d5\u05d3\u05ea \u05d4\u05d0\u05de\u05e6\u05e2 \u05d1\u05d9\u05df \u05d4\u05de\u05d5\u05e7\u05d3 \u05dc\u05de\u05d3\u05e8\u05d9\u05da: \u05e0\u05e7\u05d5\u05d3\u05ea \u05d0\u05de\u05e6\u05e2 \u05e9\u05dc (0,5) \u05d5-(0,-5) \u05d4\u05d9\u05d0 (0,0).",
    skill_atoms: ["vertex as midpoint between focus and directrix"]
  }
];

if (!d.questions) d.questions = [];
// Add only new questions (avoid duplicates)
const existingIds = new Set(d.questions.map(q => q.id));
let added = 0;
for (const q of newQ5pt) {
  // Fix the q3 answer (recalc shows it's 4 not 6)
  if (q.id === "ag_5pt_q3") {
    q.answer_en = "4";
    q.answer_he = "4";
    q.explanation_en = "p=2 so y=x²/8. For x=4: y=16/8=2. By the focus-directrix property, PF = distance from P to directrix y=-2 = |2-(-2)| = 4.";
    q.explanation_he = "p=2 ולכן y=x²/8. עבור x=4: y=2. לפי הגדרת הפרבולה: PF = מרחק מ-P למדריך y=-2 = |2-(-2)| = 4.";
  }
  if (!existingIds.has(q.id)) {
    d.questions.push(q);
    added++;
  }
}

fs.writeFileSync(path, JSON.stringify(d, null, 2), "utf8");
console.log("analytic_geometry.json: added " + added + " 5pt focus-directrix questions. Total questions:", d.questions.length);
