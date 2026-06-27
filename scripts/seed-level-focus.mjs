#!/usr/bin/env node
/**
 * seed-level-focus.mjs
 *
 * Adds hand-crafted `level_focus` blocks to the most important math+physics
 * lesson files. These are based on the official Israeli Bagrut curriculum.
 *
 * Run: node scripts/seed-level-focus.mjs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LESSONS_DIR = path.join(__dirname, 'seed_data', 'lessons');

/** Map from concept_id to its level_focus object */
const LEVEL_FOCUS_MAP = {

  // ══════════════════════════════════════════════════════════════════════
  // MATH — 3pt / 4pt / 5pt
  // ══════════════════════════════════════════════════════════════════════

  equations_quadratic: {
    '3pt': {
      en: 'Solve quadratic equations using the quadratic formula. Determine the number of solutions using the discriminant Δ = b²-4ac. No factoring or completing-the-square required.',
      he: 'פתרון משוואות ריבועיות בנוסחת הפתרון. קביעת מספר הפתרונות באמצעות הדיסקרימיננטה Δ = b²-4ac. פירוק גורמים והשלמה לריבוע אינם נדרשים.',
      bagrut_questionnaires: ['801', '802'],
      skills: ['quadratic_formula', 'discriminant_count_solutions'],
      not_required: ['completing_the_square', 'factoring_trinomials', 'sum_product_of_roots_vieta'],
    },
    '4pt': {
      en: 'All 3pt skills, PLUS: factoring trinomials; Vieta\'s formulas (sum and product of roots); solving by completing the square; quadratic inequalities from sign analysis.',
      he: 'כל כישורי 3 יח׳, בנוסף: פירוק טרינומים; נוסחאות ויאטה (סכום ומכפלת שורשים); פתרון בהשלמה לריבוע; אי-שוויונות ריבועיות מניתוח סימנים.',
      bagrut_questionnaires: ['804'],
      skills: ['factoring_trinomials', 'vieta_formulas', 'completing_the_square', 'quadratic_inequalities'],
    },
    '5pt': {
      en: 'All 4pt skills, PLUS: parametric equations in quadratics (find k such that roots satisfy a condition); equations with two parameters; connection to function analysis and derivatives.',
      he: 'כל כישורי 4 יח׳, בנוסף: משוואות פרמטריות בריבועיות (מציאת k כך שהשורשים יקיימו תנאי); משוואות עם שני פרמטרים; קשר לניתוח פונקציות ונגזרות.',
      bagrut_questionnaires: ['581', '807'],
      skills: ['parametric_quadratics', 'root_conditions', 'connection_to_derivatives'],
    },
  },

  sequences_arithmetic: {
    '3pt': {
      en: 'Find terms of arithmetic and geometric sequences using the nth-term formula. Find the sum of arithmetic sequences (Sn formula). Identify common difference/ratio. Solve simple word problems.',
      he: 'מציאת איברים בסדרות חשבוניות והנדסיות בנוסחת האיבר הכללי. מציאת סכום סדרות חשבוניות (נוסחת Sn). זיהוי הפרש/מנה קבועה. פתרון בעיות מילוליות פשוטות.',
      bagrut_questionnaires: ['801', '802'],
      skills: ['nth_term_arithmetic', 'nth_term_geometric', 'sum_arithmetic_series'],
      not_required: ['sum_geometric_series', 'infinite_geometric_series', 'recursive_sequences'],
    },
    '4pt': {
      en: 'All 3pt skills, PLUS: sum of geometric series (finite); recursive sequence definitions; given sum and number of terms, find the sequence; mixed arithmetic+geometric problems.',
      he: 'כל כישורי 3 יח׳, בנוסף: סכום סדרות הנדסיות (סופיות); הגדרות רקורסיביות; נתון הסכום ומספר האיברים, מציאת הסדרה; בעיות מעורבות חשבוני+הנדסי.',
      bagrut_questionnaires: ['804'],
      skills: ['sum_geometric_series', 'recursive_sequences', 'given_sum_find_sequence'],
    },
    '5pt': {
      en: 'All 4pt skills, PLUS: infinite geometric series (|r|<1); proofs by induction involving series; connection between series sums and integrals; Riemann sum interpretation.',
      he: 'כל כישורי 4 יח׳, בנוסף: סדרות הנדסיות אינסופיות (|q|<1); הוכחות באינדוקציה הכוללות סדרות; קשר בין סכומי סדרות לאינטגרלים; פרשנות סכום רימן.',
      bagrut_questionnaires: ['581'],
      skills: ['infinite_geometric_series', 'proof_by_induction', 'riemann_sum_interpretation'],
    },
  },

  trigonometry_ratios: {
    '3pt': {
      en: 'SOH-CAH-TOA in right triangles. Pythagorean theorem. Find missing sides/angles. Simple word problems (heights, distances). Degrees only — no radians.',
      he: 'SOH-CAH-TOA במשולשי ישר זווית. משפט פיתגורס. מציאת צלעות/זוויות חסרות. בעיות מילוליות פשוטות (גבהים, מרחקים). מעלות בלבד — ללא רדיאנים.',
      bagrut_questionnaires: ['801', '802'],
      skills: ['sin_cos_tan_right_triangle', 'pythagorean_theorem', 'inverse_trig_angles', 'word_problems_trig'],
      not_required: ['sine_rule', 'cosine_rule', 'unit_circle', 'trig_identities', 'radians'],
    },
    '4pt': {
      en: 'All 3pt skills, PLUS: sine rule and cosine rule for non-right triangles; area of triangle = ½ab·sinC; unit circle (key angles 0°,30°,45°,60°,90°,...); basic trig identities (sin²+cos²=1, tan=sin/cos).',
      he: 'כל כישורי 3 יח׳, בנוסף: משפט הסינוסים ומשפט הקוסינוסים למשולשים לא-ישרים; שטח משולש = ½ab·sinC; מעגל היחידה (זוויות מרכזיות); זהויות טריגונומטריות בסיסיות.',
      bagrut_questionnaires: ['804'],
      skills: ['sine_rule', 'cosine_rule', 'area_formula_sinC', 'unit_circle', 'basic_identities'],
    },
    '5pt': {
      en: 'All 4pt skills, PLUS: radians; trigonometric functions as periodic; solving trig equations (sinθ=k, cosθ=k in given intervals); addition formulas; double angle formulas; graphs of sin/cos/tan.',
      he: 'כל כישורי 4 יח׳, בנוסף: רדיאנים; פונקציות טריגונומטריות כפריודיות; פתרון משוואות טריג (sinθ=k, cosθ=k בקטעים נתונים); נוסחאות חיבור; נוסחאות כפול זווית; גרפים.',
      bagrut_questionnaires: ['581', '807'],
      skills: ['radians', 'trig_functions_periodic', 'solving_trig_equations', 'addition_formulas', 'double_angle'],
    },
  },

  probability_basic: {
    '3pt': {
      en: 'Classical probability (favorable/total outcomes). Complementary probability P(A\'). Simple combined experiments (multiplication principle). Two-way tables. No conditional probability or combinations formula.',
      he: 'הסתברות קלאסית (תוצאות נוחות/כלל). הסתברות משלימה P(A\'). ניסויים מורכבים פשוטים (עקרון הכפל). טבלאות דו-כיווניות. ללא הסתברות מותנית או נוסחת צירופים.',
      bagrut_questionnaires: ['801', '802'],
      skills: ['classical_probability', 'complementary_event', 'multiplication_principle', 'two_way_tables'],
      not_required: ['conditional_probability', 'bayes', 'combinations', 'permutations', 'binomial_distribution'],
    },
    '4pt': {
      en: 'All 3pt skills, PLUS: combinations C(n,r) and permutations P(n,r); conditional probability P(A|B); independence; at-least-one problems using complement.',
      he: 'כל כישורי 3 יח׳, בנוסף: צירופים C(n,r) ותמורות P(n,r); הסתברות מותנית P(A|B); עצמאות; בעיות לפחות-אחד בעזרת משלים.',
      bagrut_questionnaires: ['804'],
      skills: ['combinations_formula', 'permutations', 'conditional_probability', 'independence', 'at_least_one'],
    },
    '5pt': {
      en: 'All 4pt skills, PLUS: Bayes\' theorem; binomial distribution; expected value; probability generating functions; geometric distribution; normal distribution intro.',
      he: 'כל כישורי 4 יח׳, בנוסף: משפט בייס; התפלגות בינומית; תוחלת; ערך מצופה; התפלגות גיאומטרית; מבוא לתפלגות נורמלית.',
      bagrut_questionnaires: ['581', '807'],
      skills: ['bayes_theorem', 'binomial_distribution', 'expected_value', 'normal_distribution_intro'],
    },
  },

  analytic_geometry: {
    '3pt': {
      en: 'Distance formula; midpoint formula; slope of a line; equation of a line (y=mx+b and point-slope form); parallel and perpendicular lines (slopes). Simple: is a point on a line? Intersection of two lines.',
      he: 'נוסחת המרחק; נוסחת נקודת האמצע; שיפוע ישר; משוואת ישר (y=mx+b וצורת נקודה-שיפוע); ישרים מקבילים וניצבים (שיפועים). פשוט: האם נקודה על ישר? חיתוך שני ישרים.',
      bagrut_questionnaires: ['801', '802'],
      skills: ['distance_formula', 'midpoint_formula', 'slope_formula', 'line_equation', 'parallel_perpendicular_slopes'],
      not_required: ['circle_equation', 'tangent_to_circle', 'locus_problems'],
    },
    '4pt': {
      en: 'All 3pt skills, PLUS: circle equation (x-a)²+(y-b)²=r²; center and radius; point-on-circle check; intersection of line and circle; tangent to circle from external point.',
      he: 'כל כישורי 3 יח׳, בנוסף: משוואת מעגל (x-a)²+(y-b)²=r²; מרכז ורדיוס; בדיקת נקודה על מעגל; חיתוך ישר ומעגל; משיק למעגל מנקודה חיצונית.',
      bagrut_questionnaires: ['804'],
      skills: ['circle_equation', 'circle_center_radius', 'line_circle_intersection', 'tangent_from_external'],
    },
    '5pt': {
      en: 'All 4pt skills, PLUS: parabola as a locus; focus-directrix; conic sections overview; distance from point to line formula; geometric proofs using coordinates.',
      he: 'כל כישורי 4 יח׳, בנוסף: פרבולה כגיאומטרי מיקום; מוקד ומדריך; סקירת חתכי חרוט; מרחק מנקודה לישר; הוכחות גיאומטריות בכלים אנליטיים.',
      bagrut_questionnaires: ['581'],
      skills: ['parabola_locus', 'focus_directrix', 'point_to_line_distance', 'coordinate_proofs'],
    },
  },

  derivatives_applications: {
    '4pt': {
      en: 'Find where f\'(x) = 0 to locate critical points. Determine if they are max or min by sign change of f\'. Monotonicity intervals (increasing/decreasing). Simple optimization: maximum area/minimum distance.',
      he: 'מציאת מקום f\'(x) = 0 לאיתור נקודות קריטיות. קביעת מקסימום/מינימום לפי שינוי סימן f\'. קטעי מונוטוניות (עולה/יורד). אופטימיזציה פשוטה: שטח מקסימלי/מרחק מינימלי.',
      bagrut_questionnaires: ['804'],
      skills: ['critical_points_from_derivative', 'max_min_sign_change', 'monotonicity_intervals', 'simple_optimization'],
      not_required: ['second_derivative_test', 'concavity', 'inflection_points', 'curve_sketching_full'],
    },
    '5pt': {
      en: 'All 4pt skills, PLUS: second derivative test (f\'\'(a)>0 → local min); concavity and inflection points; complete curve sketching; Rolle\'s theorem and MVT (conceptual); harder optimization problems; tangent line at a point.',
      he: 'כל כישורי 4 יח׳, בנוסף: מבחן הנגזרת השנייה (f\'\'(a)>0 → מינימום מקומי); קעירות ונקודות פיתול; סקיצת עקומות מלאה; משפט רול ו-MVT (מושגי); בעיות אופטימיזציה קשות; משיק בנקודה.',
      bagrut_questionnaires: ['581', '807'],
      skills: ['second_derivative_test', 'concavity', 'inflection_points', 'curve_sketching_full', 'complex_optimization', 'tangent_line_equation'],
    },
  },

  definite_integrals: {
    '5pt': {
      en: 'Antiderivatives (indefinite integrals). Fundamental Theorem of Calculus (FTC): ∫ₐᵇ f(x)dx = F(b)-F(a). Area under a curve. Area between two curves. Integration by substitution. Area of region bounded by parabola and line.',
      he: 'אנטי-נגזרות (אינטגרלים לא-מוגדרים). המשפט היסודי של החשבון: ∫ₐᵇ f(x)dx = F(b)-F(a). שטח מתחת לעקומה. שטח בין שתי עקומות. אינטגרציה בהצבה. שטח תחום על-ידי פרבולה וישר.',
      bagrut_questionnaires: ['581', '807'],
      skills: ['antiderivative_rules', 'ftc_application', 'area_under_curve', 'area_between_curves', 'u_substitution'],
      not_required: ['integration_by_parts', 'partial_fractions', 'improper_integrals'],
    },
  },

  // ══════════════════════════════════════════════════════════════════════
  // PHYSICS
  // ══════════════════════════════════════════════════════════════════════

  kinematics_1d: {
    hs_physics: {
      en: 'Uniform motion (v=d/t) and uniformly accelerated motion (SUVAT equations). Free fall (g=10 m/s²). Velocity-time graphs and their interpretation. Reaction time problems. No calculus — use kinematic formulas directly.',
      he: 'תנועה אחידה (v=d/t) ותנועה מואצת אחידה (נוסחאות SUVAT). נפילה חופשית (g=10 מ/ש²). גרפי מהירות-זמן ופירושם. בעיות זמן תגובה. ללא חשבון דיפרנציאלי — שימוש ישיר בנוסחאות קינמטיות.',
      bagrut_questionnaires: ['physics_5_units'],
      skills: ['suvat_equations', 'free_fall', 'vt_graph_interpretation', 'relative_motion'],
      not_required: ['calculus_kinematics', '2d_kinematics_projectile'],
    },
  },

  newton_laws: {
    hs_physics: {
      en: 'Newton\'s three laws (F=ma for N2). Free body diagrams. Normal force, tension, friction (f=μN). Inclined planes. Equilibrium (ΣF=0). Problems involving connected masses (Atwood machine). No rotation — translational only.',
      he: 'שלושת חוקי ניוטון (F=ma לחוק 2). דיאגרמות גוף חופשי. כוח נורמלי, מתיחה, חיכוך (f=μN). מישורים משופעים. שיווי משקל (ΣF=0). בעיות מסות מחוברות (מכונת אטווד). ללא סיבוב — תנועה לינארית בלבד.',
      bagrut_questionnaires: ['physics_5_units'],
      skills: ['free_body_diagrams', 'F_equals_ma', 'friction_force', 'inclined_plane', 'equilibrium', 'atwood_machine'],
    },
  },

  electric_circuits: {
    hs_physics: {
      en: 'Ohm\'s law (V=IR). Series and parallel circuits — equivalent resistance. Kirchhoff\'s laws. Power (P=VI=I²R=V²/R). Capacitors in circuits (basic). Voltmeter and ammeter placement. Internal resistance of battery.',
      he: 'חוק אוהם (V=IR). מעגלים טורים ומקביל — התנגדות שקולה. חוקי קירכהוף. הספק (P=VI=I²R=V²/R). קבלים במעגלים (בסיסי). מיקום וולטמטר ואמפרמטר. התנגדות פנימית של סוללה.',
      bagrut_questionnaires: ['physics_5_units'],
      skills: ['ohm_law', 'series_parallel_resistance', 'kirchhoff_laws', 'power_dissipation', 'battery_internal_resistance'],
    },
  },
};

// ── Main ──────────────────────────────────────────────────────────────────────

const files = fs.readdirSync(LESSONS_DIR).filter(f => f.endsWith('.json'));
let seeded = 0;

for (const file of files) {
  const fp = path.join(LESSONS_DIR, file);
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  const conceptId = lesson.concept_id;

  if (!LEVEL_FOCUS_MAP[conceptId]) continue;
  if (lesson.level_focus && Object.keys(lesson.level_focus).length > 0) {
    console.log(`  → ${conceptId} already has level_focus, merging...`);
  }

  lesson.level_focus = { ...(lesson.level_focus ?? {}), ...LEVEL_FOCUS_MAP[conceptId] };
  fs.writeFileSync(fp, JSON.stringify(lesson, null, 2) + '\n');
  console.log(`  ✓ ${conceptId}`);
  seeded++;
}

console.log(`\nSeeded level_focus for ${seeded} lessons.`);
