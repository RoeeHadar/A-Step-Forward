const fs = require("fs");

// Fix analytic_geometry 4pt LaTeX
const agPath = "scripts/seed_data/lessons/analytic_geometry.json";
const ag = JSON.parse(fs.readFileSync(agPath, "utf8"));
const content4ptEn = "For 4pt students, analytic geometry covers **circles and parabolas**.\n\n**Circle:** center $(a,b)$, radius $r$: $(x-a)^2 + (y-b)^2 = r^2$\n\n**Parabola** as a function: $y = ax^2 + bx + c$\n- Vertex at $x = -b/(2a)$\n- Opens up if $a > 0$, down if $a < 0$\n\n**Line-curve intersections:** Substitute the line into the curve equation, then solve the resulting quadratic.";
const content4ptHe = "\u05dc\u05ea\u05dc\u05de\u05d9\u05d3\u05d9 4 \u05e0\u05e7\u05d5\u05d3\u05d5\u05ea, \u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9\u05d4 \u05d0\u05e0\u05dc\u05d9\u05d8\u05d9\u05ea \u05de\u05db\u05e1\u05d4 **\u05e2\u05d9\u05d2\u05d5\u05dc\u05d9\u05dd \u05d5\u05e4\u05e8\u05d1\u05d5\u05dc\u05d5\u05ea**.\n\n**\u05e2\u05d9\u05d2\u05d5\u05dc:** \u05de\u05e8\u05db\u05d6 $(a,b)$, \u05e8\u05d3\u05d9\u05d5\u05e1 $r$: $(x-a)^2 + (y-b)^2 = r^2$\n\n**\u05e4\u05e8\u05d1\u05d5\u05dc\u05d4** \u05db\u05e4\u05d5\u05e0\u05e7\u05e6\u05d9\u05d4: $y = ax^2 + bx + c$\n- \u05e7\u05d5\u05d3\u05e7\u05d5\u05d3 \u05d1-$x = -b/(2a)$\n- \u05e0\u05e4\u05ea\u05d7\u05ea \u05db\u05dc\u05e4\u05d9 \u05de\u05e2\u05dc\u05d4 \u05d0\u05dd $a > 0$, \u05db\u05dc\u05e4\u05d9 \u05de\u05d8\u05d4 \u05d0\u05dd $a < 0$";
let fixed4 = 0;
for (const s of ag.sections) {
  if (s.body_by_level && s.body_by_level["4pt"] && s.body_by_level["4pt"].body_en_md.includes("^2 + (y-b)")) {
    s.body_by_level["4pt"].body_en_md = content4ptEn;
    s.body_by_level["4pt"].body_he_md = content4ptHe;
    fixed4++;
  }
}
fs.writeFileSync(agPath, JSON.stringify(ag, null, 2), "utf8");
console.log("analytic_geometry 4pt fixed:", fixed4);

// Rebuild la_determinants
const det = {
  concept_id: "la_determinants",
  subject: "math",
  level: "university",
  math_track: ["la"],
  title_en: "Determinants",
  title_he: "\u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d5\u05ea",
  summary_en: "The determinant encodes invertibility, area/volume scaling, and enables Cramer's rule.",
  summary_he: "\u05d4\u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4 \u05de\u05e7\u05d5\u05d3\u05d3\u05ea \u05d4\u05e4\u05d9\u05db\u05d5\u05ea \u05d5\u05e7\u05e0\u05d4 \u05de\u05d9\u05d3\u05d4 \u05e9\u05dc \u05e9\u05d8\u05d7/\u05e0\u05e4\u05d7.",
  est_minutes: 30,
  sections: [
    { kind: "intro", title_en: "What is a Determinant? (2x2)", title_he: "\u05de\u05d4\u05d9 \u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4? (2x2)",
      body_en_md: "For $2\\times2$: $\\det(A)=ad-bc$. Zero det iff singular. $|det(A)|$ = parallelogram area.",
      body_he_md: "\u05e2\u05d1\u05d5\u05e8 $2\\times2$: $\\det(A)=ad-bc$. \u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4 \u05d0\u05e4\u05e1\u05d9\u05ea \u05d0\u05dd \u05d5\u05e8\u05e7 \u05d0\u05dd \u05e1\u05d9\u05e0\u05d2\u05d5\u05dc\u05e8\u05d9\u05ea.",
      body_by_level: { la: { body_en_md: "$\\det(A)=ad-bc$. Zero iff singular.", body_he_md: "$\\det(A)=ad-bc$. \u05d0\u05e4\u05e1 \u05d0\u05dd \u05d5\u05e8\u05e7 \u05d0\u05dd \u05e1\u05d9\u05e0\u05d2\u05d5\u05dc\u05e8\u05d9\u05ea." } } },
    { kind: "theory", title_en: "3x3 Cofactor Expansion", title_he: "\u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4 3x3",
      body_en_md: "Expand along row/column with most zeros. Example: $\\det\\begin{pmatrix}1&2&0\\\\3&-1&4\\\\0&2&1\\end{pmatrix}=-15$.",
      body_he_md: "\u05e4\u05ea\u05d7 \u05dc\u05d0\u05d5\u05e8\u05da \u05e9\u05d5\u05e8\u05d4/\u05e2\u05de\u05d5\u05d3\u05d4 \u05e2\u05dd \u05d4\u05db\u05d9 \u05d4\u05e8\u05d1\u05d4 \u05d0\u05e4\u05e1\u05d9\u05dd. \u05d3\u05d5\u05d2\u05de\u05d4: $\\det=-15$.",
      body_by_level: { la: { body_en_md: "Sign at $(i,j)$ is $(-1)^{i+j}$.", body_he_md: "\u05d4\u05e1\u05d9\u05de\u05df \u05d1-$(i,j)$ \u05d4\u05d5\u05d0 $(-1)^{i+j}$." } } },
    { kind: "theory", title_en: "Properties", title_he: "\u05ea\u05db\u05d5\u05e0\u05d5\u05ea",
      body_en_md: "$\\det(AB)=\\det(A)\\det(B)$; row swap flips sign; triangular det = product of diagonal.",
      body_he_md: "$\\det(AB)=\\det(A)\\det(B)$; \u05d4\u05d7\u05dc\u05e4\u05ea \u05e9\u05d5\u05e8\u05d5\u05ea \u05d4\u05d5\u05e4\u05db\u05ea \u05e1\u05d9\u05de\u05df.",
      body_by_level: { la: { body_en_md: "Product rule + row operations.", body_he_md: "\u05db\u05dc\u05dc \u05de\u05db\u05e4\u05dc\u05d4 + \u05e4\u05e2\u05d5\u05dc\u05d5\u05ea \u05e9\u05d5\u05e8\u05d5\u05ea." } } },
    { kind: "worked_example", title_en: "Cramer's Rule", title_he: "\u05db\u05dc\u05dc \u05e7\u05e8\u05de\u05e8",
      body_en_md: "$x_j=\\det(A_j)/\\det(A)$. Example: $3x+y=7$, $x-y=1$ gives $x=2$, $y=1$.",
      body_he_md: "$x_j=\\det(A_j)/\\det(A)$. \u05d3\u05d5\u05d2\u05de\u05d4: $x=2$, $y=1$.",
      body_by_level: { la: { body_en_md: "Efficient for 2x2/3x3.", body_he_md: "\u05d9\u05e2\u05d9\u05dc \u05dc-2x2/3x3." } } },
    { kind: "summary", title_en: "Summary", title_he: "\u05e1\u05d9\u05db\u05d5\u05dd",
      body_en_md: "det=0 iff singular; |det| = scaling factor; Cramer for small systems.",
      body_he_md: "det=0 \u05d0\u05dd \u05d5\u05e8\u05e7 \u05d0\u05dd \u05e1\u05d9\u05e0\u05d2\u05d5\u05dc\u05e8\u05d9\u05ea; |det| = \u05e7\u05e0\u05d4 \u05de\u05d9\u05d3\u05d4.",
      body_by_level: { la: { body_en_md: "Prerequisite for eigenvalues.", body_he_md: "\u05ea\u05e0\u05d0\u05d9 \u05dc\u05d0\u05d9 \u05dc\u05e2\u05e8\u05db\u05d9\u05dd \u05e2\u05e6\u05de\u05d9\u05d9\u05dd." } } },
  ],
  questions: [
    { ord: 1, kind: "mcq", difficulty: "easy", points_level_min: "la", stem_en: "What is det([[4,2],[1,3]])?", stem_he: "\u05de\u05d4\u05d9 det([[4,2],[1,3]])?", options_en: ["10","14","8","0"], options_he: ["10","14","8","0"], correct_index: 0, explanation_en: "det=12-2=10.", explanation_he: "det=10.", skill_atoms: ["2x2_det"] },
    { ord: 2, kind: "mcq", difficulty: "easy", points_level_min: "la", stem_en: "If det(A)=0, which is necessarily true?", stem_he: "\u05d0\u05dd det(A)=0, \u05de\u05d4 \u05d1\u05d4\u05db\u05e8\u05d7 \u05e0\u05db\u05d5\u05df?", options_en: ["A invertible","Linearly dependent rows","Zero matrix","All eigenvalues zero"], options_he: ["A \u05d4\u05e4\u05d9\u05db\u05d4","\u05e9\u05d5\u05e8\u05d5\u05ea \u05ea\u05dc\u05d5\u05d9\u05d5\u05ea","\u05de\u05d8\u05e8\u05d9\u05e6\u05ea \u05d0\u05e4\u05e1","\u05db\u05dc \u05d4\u05e2\u05e8\u05db\u05d9\u05dd \u05d0\u05e4\u05e1\u05d9\u05dd"], correct_index: 1, explanation_en: "det=0 iff singular.", explanation_he: "det=0 \u05d0\u05dd \u05d5\u05e8\u05e7 \u05d0\u05dd \u05e1\u05d9\u05e0\u05d2\u05d5\u05dc\u05e8\u05d9\u05ea.", skill_atoms: ["det_zero"] },
    { ord: 3, kind: "mcq", difficulty: "medium", points_level_min: "la", stem_en: "If det(A)=6 and det(B)=-2, det(AB)?", stem_he: "\u05d0\u05dd det(A)=6 \u05d5-det(B)=-2, det(AB)?", options_en: ["-12","12","-3","4"], options_he: ["-12","12","-3","4"], correct_index: 0, explanation_en: "6*(-2)=-12.", explanation_he: "-12.", skill_atoms: ["det_product"] },
    { ord: 4, kind: "mcq", difficulty: "medium", points_level_min: "la", stem_en: "Compute det([[1,0,2],[3,1,0],[0,0,4]]).", stem_he: "\u05d7\u05e9\u05d1 det([[1,0,2],[3,1,0],[0,0,4]]).", options_en: ["6","4","8","-4"], options_he: ["6","4","8","-4"], correct_index: 1, explanation_en: "Expand row 3: 4*1=4.", explanation_he: "4.", skill_atoms: ["3x3_cofactor"] },
    { ord: 5, kind: "mcq", difficulty: "hard", points_level_min: "la", stem_en: "Cramer: 2x+y=5, x-y=1. x=?", stem_he: "\u05db\u05dc\u05dc \u05e7\u05e8\u05de\u05e8: x=?", options_en: ["2","3","1","4"], options_he: ["2","3","1","4"], correct_index: 0, explanation_en: "x=2.", explanation_he: "x=2.", skill_atoms: ["cramers_rule"] },
    { ord: 6, kind: "mcq", difficulty: "hard", points_level_min: "la", stem_en: "Row swap gives det(B)=5. det(A)?", stem_he: "\u05d4\u05d7\u05dc\u05e4\u05ea \u05e9\u05d5\u05e8\u05d5\u05ea: det(B)=5. det(A)?", options_en: ["-5","5","10","0"], options_he: ["-5","5","10","0"], correct_index: 0, explanation_en: "Sign flips: -5.", explanation_he: "-5.", skill_atoms: ["row_swap"] },
  ],
  agent_hints: {
    key_insights: ["det=0 iff singular", "2x2: ad-bc", "det(AB)=det(A)det(B)"],
    skill_atoms_unlocked: ["2x2_det","det_zero","det_product","3x3_cofactor","cramers_rule"],
    prerequisites_to_check_before_teaching: ["la_matrices"],
    next_recommended: ["la_eigenvalues"]
  }
};
const detPath = "scripts/seed_data/lessons/la_determinants.json";
fs.writeFileSync(detPath, JSON.stringify(det, null, 2), "utf8");
const v = JSON.parse(fs.readFileSync(detPath, "utf8"));
console.log("la_determinants rebuilt:", v.questions[0].stem_en, "agent_hints:", !!v.agent_hints);
