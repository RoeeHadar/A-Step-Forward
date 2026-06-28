const fs = require("fs");
const data = {
  id: "la_determinants",
  concept_id: "la_determinants",
  title_en: "Determinants",
  title_he: "\u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d5\u05ea",
  subject: "math",
  math_track: ["la"],
  est_minutes: 30,
  summary_en: "The determinant encodes invertibility and area/volume scaling, and enables Cramer's rule.",
  summary_he: "\u05d4\u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4 \u05de\u05e7\u05d5\u05d3\u05d3\u05ea \u05d4\u05e4\u05d9\u05db\u05d5\u05ea \u05d5\u05e7\u05e0\u05d4 \u05de\u05d9\u05d3\u05d4 \u05e9\u05dc \u05e9\u05d8\u05d7/\u05e0\u05e4\u05d7.",
  sections: [
    {
      id: "intro",
      kind: "intro",
      title_en: "What is a Determinant? (2x2)",
      title_he: "\u05de\u05d4\u05d9 \u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4? (2x2)",
      body_en_md: "For a 2x2 matrix A with entries a,b,c,d: det(A) = ad - bc.\n\nIf det(A) = 0, the matrix is singular (not invertible). |det(A)| equals the area of the parallelogram formed by the rows.\n\nExample: A = [[3,1],[2,4]] gives det(A) = 12-2 = 10 (invertible). B = [[2,4],[1,2]] gives det(B) = 4-4 = 0 (singular).",
      body_he_md: "\u05e2\u05d1\u05d5\u05e8 \u05de\u05d8\u05e8\u05d9\u05e6\u05d4 2x2: det(A) = ad - bc.\n\n\u05d0\u05dd det(A) = 0, \u05d4\u05de\u05d8\u05e8\u05d9\u05e6\u05d4 \u05e1\u05d9\u05e0\u05d2\u05d5\u05dc\u05e8\u05d9\u05ea (\u05dc\u05d0 \u05d4\u05e4\u05d9\u05db\u05d4). |det(A)| \u05e9\u05d5\u05d5\u05d4 \u05dc\u05e9\u05d8\u05d7 \u05d4\u05de\u05e7\u05d1\u05d9\u05dc\u05d9\u05ea \u05e9\u05e0\u05d5\u05e6\u05e8\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 \u05d4\u05e9\u05d5\u05e8\u05d5\u05ea.",
      body_by_level: {
        la: {
          body_en_md: "det(A) = ad - bc for 2x2. Zero determinant iff linearly dependent rows iff singular matrix.",
          body_he_md: "det(A) = ad - bc \u05e2\u05d1\u05d5\u05e8 2x2. \u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4 \u05d0\u05e4\u05e1\u05d9\u05ea \u05d0\u05dd \u05d5\u05e8\u05e7 \u05d0\u05dd \u05e9\u05d5\u05e8\u05d5\u05ea \u05ea\u05dc\u05d5\u05d9\u05d5\u05ea \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9\u05ea \u05d0\u05dd \u05d5\u05e8\u05e7 \u05d0\u05dd \u05de\u05d8\u05e8\u05d9\u05e6\u05d4 \u05e1\u05d9\u05e0\u05d2\u05d5\u05dc\u05e8\u05d9\u05ea."
        }
      }
    },
    {
      id: "cofactor",
      kind: "theory",
      title_en: "3x3 Determinant — Cofactor Expansion",
      title_he: "\u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4 3x3 \u2014 \u05e4\u05d9\u05ea\u05d5\u05d7 \u05dc\u05e4\u05d9 \u05e9\u05d5\u05e8\u05d4",
      body_en_md: "Expand along any row or column. Signs alternate: + - + for row 1.\n\nExample: det([[1,2,0],[3,-1,4],[0,2,1]])\nExpand row 1 (0 in position 3 helps):\n= 1*det([[-1,4],[2,1]]) - 2*det([[3,4],[0,1]]) + 0\n= 1*(-1-8) - 2*(3-0)\n= -9 - 6 = -15\n\nTip: Choose the row/column with the most zeros.",
      body_he_md: "\u05e4\u05ea\u05d7 \u05dc\u05d0\u05d5\u05e8\u05da \u05db\u05dc \u05e9\u05d5\u05e8\u05d4 \u05d0\u05d5 \u05e2\u05de\u05d5\u05d3\u05d4. \u05d4\u05e1\u05d9\u05de\u05e0\u05d9\u05dd \u05de\u05ea\u05d7\u05dc\u05e4\u05d9\u05dd: + - + \u05dc\u05e9\u05d5\u05e8\u05d4 1.\n\n\u05d3\u05d5\u05d2\u05de\u05d4: det([[1,2,0],[3,-1,4],[0,2,1]])\n\u05e4\u05ea\u05d7 \u05e9\u05d5\u05e8\u05d4 1 (0 \u05d1\u05de\u05d9\u05e7\u05d5\u05dd 3 \u05e2\u05d5\u05d6\u05e8):\n= 1*det([[-1,4],[2,1]]) - 2*det([[3,4],[0,1]])\n= -9 - 6 = -15\n\n\u05d8\u05d9\u05e4: \u05d1\u05d7\u05e8 \u05d0\u05ea \u05d4\u05e9\u05d5\u05e8\u05d4/\u05e2\u05de\u05d5\u05d3\u05d4 \u05e2\u05dd \u05d4\u05db\u05d9 \u05d4\u05e8\u05d1\u05d4 \u05d0\u05e4\u05e1\u05d9\u05dd.",
      body_by_level: {
        la: {
          body_en_md: "Cofactor expansion along any row/column. Sign at position (i,j) is (-1)^(i+j). Optimal: expand along row or column with most zeros.",
          body_he_md: "\u05e4\u05d9\u05ea\u05d5\u05d7 \u05e7\u05d5\u05e4\u05e7\u05d8\u05d5\u05e8\u05d9\u05dd \u05dc\u05d0\u05d5\u05e8\u05da \u05db\u05dc \u05e9\u05d5\u05e8\u05d4/\u05e2\u05de\u05d5\u05d3\u05d4. \u05d4\u05e1\u05d9\u05de\u05df \u05d1\u05de\u05d9\u05e7\u05d5\u05dd (i,j) \u05d4\u05d5\u05d0 (-1)^(i+j). \u05d0\u05d5\u05e4\u05d8\u05d9\u05de\u05dc\u05d9: \u05e4\u05ea\u05d7 \u05dc\u05d0\u05d5\u05e8\u05da \u05e9\u05d5\u05e8\u05d4 \u05d0\u05d5 \u05e2\u05de\u05d5\u05d3\u05d4 \u05e2\u05dd \u05d4\u05db\u05d9 \u05d4\u05e8\u05d1\u05d4 \u05d0\u05e4\u05e1\u05d9\u05dd."
        }
      }
    },
    {
      id: "properties",
      kind: "theory",
      title_en: "Properties of Determinants",
      title_he: "\u05ea\u05db\u05d5\u05e0\u05d5\u05ea \u05d4\u05d3\u05d8\u05e8\u05de\u05d9\u05e0\u05e0\u05d8\u05d4",
      body_en_md: "Key properties:\n- Row scaling: multiply row by k => det multiplied by k\n- Row swap: swap two rows => sign flips\n- Row addition: add multiple of row to another => det unchanged\n- Triangular: det = product of diagonal entries\n- Product rule: det(AB) = det(A)det(B)\n- Transpose: det(A^T) = det(A)\n- Orthogonal matrix Q: det(Q) = +/-1",
      body_he_md: "\u05ea\u05db\u05d5\u05e0\u05d5\u05ea \u05e2\u05d9\u05e7\u05e8\u05d9\u05d5\u05ea:\n- \u05db\u05e4\u05dc \u05e9\u05d5\u05e8\u05d4 \u05d1-k: det \u05de\u05d5\u05db\u05e4\u05dc \u05d1-k\n- \u05d4\u05d7\u05dc\u05e4\u05ea \u05e9\u05d5\u05e8\u05d5\u05ea: \u05e1\u05d9\u05de\u05df \u05de\u05ea\u05d4\u05e4\u05da\n- \u05d7\u05d9\u05d1\u05d5\u05e8 \u05e9\u05d5\u05e8\u05d5\u05ea: det \u05d0\u05d9\u05e0\u05d5 \u05de\u05e9\u05ea\u05e0\u05d4\n- \u05de\u05e9\u05d5\u05dc\u05e9\u05d9\u05ea: det = \u05de\u05db\u05e4\u05dc\u05d4 \u05d0\u05dc\u05db\u05e1\u05d5\u05e0\u05d9\u05ea\n- \u05db\u05dc\u05dc \u05de\u05db\u05e4\u05dc\u05d4: det(AB) = det(A)det(B)\n- \u05de\u05d8\u05e8\u05d9\u05e6\u05d4 \u05d0\u05d5\u05e8\u05ea\u05d5\u05d2\u05d5\u05e0\u05dc\u05d9\u05ea Q: det(Q) = +/-1",
      body_by_level: {
        la: {
          body_en_md: "det(AB)=det(A)det(B); row swap flips sign; scale row by k scales det by k; triangular det = product of diagonal.",
          body_he_md: "det(AB)=det(A)det(B); \u05d4\u05d7\u05dc\u05e4\u05ea \u05e9\u05d5\u05e8\u05d5\u05ea \u05d4\u05d5\u05e4\u05db\u05ea \u05e1\u05d9\u05de\u05df; \u05db\u05e4\u05dc \u05e9\u05d5\u05e8\u05d4 \u05d1-k \u05de\u05db\u05e4\u05d9\u05dc det \u05d1-k; \u05de\u05e9\u05d5\u05dc\u05e9\u05d9\u05ea \u2014 det = \u05de\u05db\u05e4\u05dc\u05d4 \u05d0\u05dc\u05db\u05e1\u05d5\u05e0\u05d9\u05ea."
        }
      }
    },
    {
      id: "geometric",
      kind: "theory",
      title_en: "Geometric Meaning",
      title_he: "\u05de\u05e9\u05de\u05e2\u05d5\u05ea \u05d2\u05d9\u05d0\u05d5\u05de\u05d8\u05e8\u05d9\u05ea",
      body_en_md: "2x2: |det(A)| = area of parallelogram formed by row vectors.\n3x3: |det(A)| = volume of parallelepiped.\nSign encodes orientation (positive = right-handed; negative = flipped).\nExample: rotation matrix has det = 1 — preserves area.",
      body_he_md: "2x2: |det(A)| = \u05e9\u05d8\u05d7 \u05d4\u05de\u05e7\u05d1\u05d9\u05dc\u05d9\u05ea.\n3x3: |det(A)| = \u05e0\u05e4\u05d7 \u05d4\u05de\u05e7\u05d1\u05d9\u05dc\u05d5\u05df.\n\u05d4\u05e1\u05d9\u05de\u05df \u05de\u05e7\u05d5\u05d3\u05d3 \u05d0\u05d5\u05e8\u05d9\u05d9\u05e0\u05d8\u05e6\u05d9\u05d4. \u05de\u05d8\u05e8\u05d9\u05e6\u05ea \u05e1\u05d9\u05d1\u05d5\u05d1 \u05de\u05e7\u05d9\u05d9\u05de\u05ea det = 1 \u2014 \u05e9\u05d5\u05de\u05e8\u05ea \u05e9\u05d8\u05d7.",
      body_by_level: {
        la: {
          body_en_md: "|det(A)| = area (2x2) or volume (3x3) scaling factor. det = 0 iff rows are linearly dependent.",
          body_he_md: "|det(A)| = \u05e4\u05e7\u05d8\u05d5\u05e8 \u05e7\u05e0\u05d4 \u05de\u05d9\u05d3\u05d4 \u05e9\u05dc \u05e9\u05d8\u05d7 (2x2) \u05d0\u05d5 \u05e0\u05e4\u05d7 (3x3). det = 0 \u05d0\u05dd \u05d5\u05e8\u05e7 \u05d0\u05dd \u05e9\u05d5\u05e8\u05d5\u05ea \u05ea\u05dc\u05d5\u05d9\u05d5\u05ea \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9\u05ea."
        }
      }
    },
    {
      id: "cramers",
      kind: "worked_example",
      title_en: "Cramer's Rule",
      title_he: "\u05db\u05dc\u05dc \u05e7\u05e8\u05de\u05e8",
      body_en_md: "For Ax=b with det(A) != 0: x_j = det(A_j)/det(A), where A_j replaces column j with b.\n\nExample: 3x+y=7, x-y=1\ndet(A) = (3)(-1)-(1)(1) = -4\nx = det([[7,1],[1,-1]])/(-4) = (-8)/(-4) = 2\ny = det([[3,7],[1,1]])/(-4) = (-4)/(-4) = 1\nCheck: 3(2)+1=7 and 2-1=1. Correct!",
      body_he_md: "\u05e2\u05d1\u05d5\u05e8 Ax=b \u05e2\u05dd det(A) != 0: x_j = det(A_j)/det(A), \u05db\u05d0\u05e9\u05e8 A_j \u05de\u05d7\u05dc\u05d9\u05e3 \u05e2\u05de\u05d5\u05d3\u05d4 j \u05d1-b.\n\n\u05d3\u05d5\u05d2\u05de\u05d4: 3x+y=7, x-y=1\ndet(A) = -4\nx = (-8)/(-4) = 2, y = (-4)/(-4) = 1\n\u05d1\u05d3\u05d9\u05e7\u05d4: 3(2)+1=7 \u2713 \u05d5-2-1=1 \u2713",
      body_by_level: {
        la: {
          body_en_md: "Cramer's rule: x_j = det(A_j)/det(A). Efficient for 2x2/3x3. Use Gaussian elimination for larger systems.",
          body_he_md: "\u05db\u05dc\u05dc \u05e7\u05e8\u05de\u05e8: x_j = det(A_j)/det(A). \u05d9\u05e2\u05d9\u05dc \u05dc-2x2/3x3. \u05d4\u05e9\u05ea\u05de\u05e9 \u05d1\u05d0\u05dc\u05d9\u05de\u05d9\u05e0\u05e6\u05d9\u05d4 \u05d2\u05d0\u05d5\u05e1\u05d9\u05d0\u05e0\u05d9\u05ea \u05dc\u05de\u05e2\u05e8\u05db\u05d5\u05ea \u05d2\u05d3\u05d5\u05dc\u05d5\u05ea \u05d9\u05d5\u05ea\u05e8."
        }
      }
    }
  ],
  questions: [
    {
      id: "det_q1", type: "mcq", difficulty: "easy", level_focus: "la",
      body_en: "What is det([[4,2],[1,3]])?",
      body_he: "\u05de\u05d4\u05d9 det([[4,2],[1,3]])?",
      options_en: ["10","14","8","0"], options_he: ["10","14","8","0"],
      answer_en: "10", answer_he: "10",
      explanation_en: "det = (4)(3)-(2)(1) = 10.",
      explanation_he: "det = (4)(3)-(2)(1) = 10.",
      skill_atoms: ["2x2 determinant formula ad-bc"]
    },
    {
      id: "det_q2", type: "mcq", difficulty: "easy", level_focus: "la",
      body_en: "If det(A) = 0, which is necessarily true?",
      body_he: "\u05d0\u05dd det(A) = 0, \u05de\u05d4 \u05d1\u05d4\u05db\u05e8\u05d7 \u05e0\u05db\u05d5\u05df?",
      options_en: ["A is invertible","A has linearly dependent rows","A is the zero matrix","All eigenvalues are zero"],
      options_he: ["A \u05d4\u05e4\u05d9\u05db\u05d4","\u05dc-A \u05e9\u05d5\u05e8\u05d5\u05ea \u05ea\u05dc\u05d5\u05d9\u05d5\u05ea \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9\u05ea","A \u05d4\u05d9\u05d0 \u05de\u05d8\u05e8\u05d9\u05e6\u05ea \u05d4\u05d0\u05e4\u05e1","\u05db\u05dc \u05d4\u05e2\u05e8\u05db\u05d9\u05dd \u05d4\u05e2\u05e6\u05de\u05d9\u05d9\u05dd \u05d0\u05e4\u05e1\u05d9\u05dd"],
      answer_en: "A has linearly dependent rows", answer_he: "\u05dc-A \u05e9\u05d5\u05e8\u05d5\u05ea \u05ea\u05dc\u05d5\u05d9\u05d5\u05ea \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9\u05ea",
      explanation_en: "det(A) = 0 iff rows are linearly dependent iff A is singular.",
      explanation_he: "det(A) = 0 \u05d0\u05dd \u05d5\u05e8\u05e7 \u05d0\u05dd \u05d4\u05e9\u05d5\u05e8\u05d5\u05ea \u05ea\u05dc\u05d5\u05d9\u05d5\u05ea \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9\u05ea.",
      skill_atoms: ["determinant zero iff singular"]
    },
    {
      id: "det_q3", type: "mcq", difficulty: "medium", level_focus: "la",
      body_en: "If det(A)=6 and det(B)=-2, what is det(AB)?",
      body_he: "\u05d0\u05dd det(A)=6 \u05d5-det(B)=-2, \u05de\u05d4\u05d9 det(AB)?",
      options_en: ["-12","12","-3","4"], options_he: ["-12","12","-3","4"],
      answer_en: "-12", answer_he: "-12",
      explanation_en: "det(AB) = det(A)*det(B) = 6*(-2) = -12.",
      explanation_he: "det(AB) = 6*(-2) = -12.",
      skill_atoms: ["det product rule det(AB)=det(A)det(B)"]
    },
    {
      id: "det_q4", type: "mcq", difficulty: "medium", level_focus: "la",
      body_en: "Compute det([[1,0,2],[3,1,0],[0,0,4]]).",
      body_he: "\u05d7\u05e9\u05d1 det([[1,0,2],[3,1,0],[0,0,4]]).",
      options_en: ["6","4","8","-4"], options_he: ["6","4","8","-4"],
      answer_en: "4", answer_he: "4",
      explanation_en: "Expand row 3: 4*det([[1,0],[3,1]]) = 4*(1) = 4.",
      explanation_he: "\u05e4\u05ea\u05d7 \u05e9\u05d5\u05e8\u05d4 3: 4*det([[1,0],[3,1]]) = 4.",
      skill_atoms: ["3x3 cofactor expansion","efficient row selection"]
    },
    {
      id: "det_q5", type: "mcq", difficulty: "hard", level_focus: "la",
      body_en: "Use Cramer's rule for 2x+y=5, x-y=1. What is x?",
      body_he: "\u05d4\u05e9\u05ea\u05de\u05e9 \u05d1\u05db\u05dc\u05dc \u05e7\u05e8\u05de\u05e8: 2x+y=5, x-y=1. \u05de\u05d4\u05d5 x?",
      options_en: ["2","3","1","4"], options_he: ["2","3","1","4"],
      answer_en: "2", answer_he: "2",
      explanation_en: "det(A)=-3. det(A1)=(5)(-1)-(1)(1)=-6. x=-6/-3=2.",
      explanation_he: "det(A)=-3. det(A1)=-6. x=2.",
      skill_atoms: ["Cramer's rule 2x2"]
    },
    {
      id: "det_q6", type: "mcq", difficulty: "hard", level_focus: "la",
      body_en: "Swapping two rows of A gives B with det(B)=5. What is det(A)?",
      body_he: "\u05d4\u05d7\u05dc\u05e4\u05ea \u05e9\u05ea\u05d9 \u05e9\u05d5\u05e8\u05d5\u05ea \u05e9\u05dc A \u05e0\u05d5\u05ea\u05e0\u05ea B \u05e2\u05dd det(B)=5. \u05de\u05d4\u05d9 det(A)?",
      options_en: ["-5","5","10","0"], options_he: ["-5","5","10","0"],
      answer_en: "-5", answer_he: "-5",
      explanation_en: "Swapping two rows flips the sign, so det(A) = -det(B) = -5.",
      explanation_he: "\u05d4\u05d7\u05dc\u05e4\u05ea \u05e9\u05d5\u05e8\u05d5\u05ea \u05d4\u05d5\u05e4\u05db\u05ea \u05e1\u05d9\u05de\u05df, \u05dc\u05db\u05df det(A) = -5.",
      skill_atoms: ["row swap negates determinant"]
    }
  ]
};
fs.writeFileSync("scripts/seed_data/lessons/la_determinants.json", JSON.stringify(data, null, 2), "utf8");
const parsed = JSON.parse(fs.readFileSync("scripts/seed_data/lessons/la_determinants.json", "utf8"));
console.log("la_determinants.json created: sections=" + parsed.sections.length + " questions=" + parsed.questions.length + " track=" + JSON.stringify(parsed.math_track));
