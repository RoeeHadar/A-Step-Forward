#!/usr/bin/env node
/**
 * Deepen HS physics facet families: vectors_*, kinematics_*, newton_*, electric_*.
 * Usage: node scripts/deepen-physics-family.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.join(
  path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'),
  'scripts/seed_data/lessons',
);

const FAMILIES = {
  vectors: {
    bases: [
      'vectors_basics',
      'vectors_2d',
      'vectors_plane',
      'vectors_dot_product_3d',
      'vectors_kinematics_2d_3d',
    ],
    facets: ['component_geometry', 'dot_product_meaning'],
    depthMarker: 'PHYS_VEC_DEPTH',
    depthTitle: {
      en: 'HS physics vectors craft: components then meaning',
      he: 'מלאכת וקטורים בפיזיקה: רכיבים ואז משמעות',
    },
    depthBody: {
      en: `**Vectors habit.** Resolve into components (רכיבים / unit vector language) before adding.
Then interpret the **dot product** as projection / work-related alignment — not just a formula.
Sketch arrows in the plane; label $i$-hat / $j$-hat directions when useful.`,
      he: `**הרגל וקטורים.** פרקו לרכיבים לפני חיבור.
ואז פרשו את ה**מכפלה הסקלרית** כהטלה / יישור קשור לעבודה — לא רק נוסחה.
סקצו חצים במישור; סמנו כיווני $i$ / $j$ כשמועיל.`,
    },
    facetSection: {
      title_en: 'Facet depth: component geometry and dot-product meaning',
      title_he: 'העמקת פנים: גאומטריית רכיבים ומשמעות מכפלה סקלרית',
      body_en_md: `**Component geometry.** Write $\\vec{a}=a_x\\hat{\\imath}+a_y\\hat{\\jmath}$ (components) and add component-wise.

**Dot product meaning.** $\\vec{a}\\cdot\\vec{b}=|\\vec{a}||\\vec{b}|\\cos\\theta$ measures projection of one vector onto the other — useful for work and for testing perpendicularity.`,
      body_he_md: `**גאומטריית רכיבים.** כתבו $\\vec{a}=a_x\\hat{\\imath}+a_y\\hat{\\jmath}$ וחברו לפי רכיבים.

**משמעות מכפלה סקלרית.** $\\vec{a}\\cdot\\vec{b}=|\\vec{a}||\\vec{b}|\\cos\\theta$ מודדת הטלה של וקטור על משנהו — שימושי לעבודה ולבדיקת ניצבות.`,
    },
    questions: [
      {
        facets: ['component_geometry'],
        stem_en:
          'Resolve a vector from this lesson into components, sketch the unit-vector directions, and recombine to check.',
        stem_he:
          'פרקו וקטור מהשיעור לרכיבים, סקצו כיווני יחידה, והרכיבו מחדש לבדיקה.',
        correct_answer: 'ax i-hat + ay j-hat; sketch; recombine',
        explanation_en:
          'Component geometry starts with a sketch: choose axes, read $a_x$ and $a_y$, write the vector as a sum of unit-vector terms, then recombine magnitudes to verify. Mistakes usually come from mixing sine/cosine against the wrong angle — keep the right triangle visible beside the arrow.',
        explanation_he:
          'גאומטריית רכיבים מתחילה בסקיצה: בחרו צירים, קראו $a_x$ ו-$a_y$, כתבו את הווקטור כסכום איברי יחידה, והרכיבו גדלים לאימות. טעויות לרוב מערבוב סינוס/קוסינוס מול הזווית הלא נכונה — השאירו משולש ישר גלוי ליד החץ.',
      },
      {
        facets: ['dot_product_meaning'],
        stem_en:
          'Compute a dot product from this lesson and interpret it as a projection (including the perpendicular case).',
        stem_he:
          'חשבו מכפלה סקלרית מהשיעור ופרשו אותה כהטלה (כולל מקרה הניצב).',
        correct_answer: 'a·b = |a||b|cosθ; zero iff perpendicular',
        explanation_en:
          'Dot product meaning: the scalar $\\vec{a}\\cdot\\vec{b}$ equals $|\\vec{a}|$ times the projection of $\\vec{b}$ onto $\\vec{a}$ (or vice versa). If the vectors are perpendicular, the projection is zero and the dot product vanishes. State this geometric reading before expanding in components.',
        explanation_he:
          'משמעות מכפלה סקלרית: הסקלר $\\vec{a}\\cdot\\vec{b}$ שווה ל-$|\\vec{a}|$ כפול ההטלה של $\\vec{b}$ על $\\vec{a}$ (או להפך). אם הווקטורים ניצבים, ההטלה אפס והמכפלה נעלמת. ציינו את הקריאה הגאומטרית לפני פיתוח ברכיבים.',
      },
    ],
  },
  kinematics: {
    bases: ['kinematics_1d', 'kinematics_2d'],
    facets: ['motion_graph_reading', 'vector_vs_scalar'],
    depthMarker: 'PHYS_KIN_DEPTH',
    depthTitle: {
      en: 'HS kinematics craft: graphs and vector vs scalar',
      he: 'מלאכת קינמטיקה: גרפים ווקטור מול סקלר',
    },
    depthBody: {
      en: `**Kinematics habit.** Read **position-time** and **velocity graph** (גרף מקום / גרף מהירות) before plugging numbers.
Separate **vector vs scalar**: displacement vs distance, velocity vs speed. Sign and direction matter for vectors.`,
      he: `**הרגל קינמטיקה.** קראו **גרף מקום** ו**גרף מהירות** לפני הצבת מספרים.
הבחינו בין **וקטור לסקלר**: העתק מול דרך, מהירות מול מהירות-גודל. סימן וכיוון חשובים לווקטורים.`,
    },
    facetSection: {
      title_en: 'Facet depth: motion-graph reading; vector vs scalar',
      title_he: 'העמקת פנים: קריאת גרפי תנועה; וקטור מול סקלר',
      body_en_md: `**Motion graph reading.** On a position-time graph, slope is velocity. On a velocity graph, area relates to displacement. Mark axes and units before reading values.

**Vector vs scalar.** Displacement and velocity are vectors; distance and speed are scalars. Do not add speeds as if they were signed velocities.`,
      body_he_md: `**קריאת גרפי תנועה.** בגרף מקום–זמן, השיפוע הוא מהירות. בגרף מהירות, השטח קשור להעתק. סמנו צירים ויחידות לפני קריאה.

**וקטור מול סקלר.** העתק ומהירות הם וקטורים; דרך ומהירות-גודל הם סקלרים. אל תוסיפו מהירויות-גודל כאילו היו מהירויות מסומנות.`,
    },
    questions: [
      {
        facets: ['motion_graph_reading'],
        stem_en:
          'From a position-time or velocity graph in this lesson, read one slope or area quantity and state what physical quantity it represents.',
        stem_he:
          'מגרף מקום או גרף מהירות בשיעור זה, קראו שיפוע או שטח אחד וציינו איזו גודל פיזיקלי הוא מייצג.',
        correct_answer: 'slope of x-t = v; area under v-t = displacement',
        explanation_en:
          'Motion graph reading: the slope of a position-time graph is velocity; the area under a velocity graph over a time interval is the change in position (displacement). Label axes, then compute rise/run or the geometric area. Sign on the velocity graph indicates direction.',
        explanation_he:
          'קריאת גרף תנועה: שיפוע גרף מקום–זמן הוא מהירות; שטח תחת גרף מהירות בקטע זמן הוא שינוי המקום (העתק). סמנו צירים, ואז חשבו עלייה/ריצה או שטח. הסימן בגרף המהירות מציין כיוון.',
      },
      {
        facets: ['vector_vs_scalar'],
        stem_en:
          'Classify two quantities from this lesson as vector or scalar, and show one calculation where mixing them would give a wrong answer.',
        stem_he:
          'סווגו שני גדלים מהשיעור כווקטור או סקלר, והציגו חישוב אחד שבו ערבוב ביניהם נותן תשובה שגויה.',
        correct_answer: 'displacement/velocity vector; distance/speed scalar',
        explanation_en:
          'Vector vs scalar: displacement and velocity carry direction; distance and speed do not. Adding speeds to get a net velocity, or ignoring sign on a one-dimensional velocity, are classic mix-ups. State the type before computing.',
        explanation_he:
          'וקטור מול סקלר: להעתק ולמהירות יש כיוון; לדרך ולמהירות-גודל אין. חיבור מהירויות-גודל לקבלת מהירות נטו, או התעלמות מסימן במהירות חד-ממדית, הן טעויות קלאסיות. ציינו סוג לפני החישוב.',
      },
    ],
  },
  newton: {
    bases: ['newton_laws', 'work_energy'],
    facets: ['free_body_diagram', 'net_force_setup'],
    depthMarker: 'PHYS_NEWTON_DEPTH',
    depthTitle: {
      en: 'HS Newton craft: FBD then ΣF',
      he: 'מלאכת ניוטון: דיאגרמת כוחות ואז כוח שקול',
    },
    depthBody: {
      en: `**Newton habit.** Draw a **free-body diagram** (FBD / דיאגרמת כוחות) before any equation.
Then write **net force** $\\Sigma \\vec{F}=m\\vec{a}$ along chosen axes (כוח שקול). Never skip the diagram.`,
      he: `**הרגל ניוטון.** ציירו **דיאגרמת כוחות** (FBD) לפני כל משוואה.
ואז כתבו **כוח שקול** $\\Sigma \\vec{F}=m\\vec{a}$ לאורך צירים שנבחרו. לעולם אל תדלגו על הדיאגרמה.`,
    },
    facetSection: {
      title_en: 'Facet depth: free-body diagrams and net-force setup',
      title_he: 'העמקת פנים: דיאגרמות כוחות והכנת כוח שקול',
      body_en_md: `**Free-body diagram.** Isolate the object; draw every force at the point of action with clear labels (gravity, normal, tension, friction).

**Net force setup.** Choose axes, resolve components, write $\\Sigma F_x$ and $\\Sigma F_y$, then relate to $ma$.`,
      body_he_md: `**דיאגרמת כוחות.** בודדו את הגוף; ציירו כל כוח בנקודת הפעולה עם תוויות (כבידה, נורמל, מתיחות, חיכוך).

**הכנת כוח שקול.** בחרו צירים, פרקו לרכיבים, כתבו $\\Sigma F_x$ ו-$\\Sigma F_y$, וקשרו ל-$ma$.`,
    },
    questions: [
      {
        facets: ['free_body_diagram'],
        stem_en:
          'Draw (or fully describe) a free-body diagram for a scenario from this lesson, naming every force.',
        stem_he:
          'ציירו (או תארו במלואה) דיאגרמת כוחות לתרחיש מהשיעור, עם שם לכל כוח.',
        correct_answer: 'isolated object; all forces labeled at points of action',
        explanation_en:
          'A free-body diagram isolates one object and shows every force acting on it — gravity, normal, tension, friction — at the correct point of action. Missing a force or drawing a force on the wrong body is the most common setup error. Complete the FBD before writing $\\Sigma F$.',
        explanation_he:
          'דיאגרמת כוחות מבודדת גוף אחד ומראה כל כוח שפועל עליו — כבידה, נורמל, מתיחות, חיכוך — בנקודת הפעולה הנכונה. כוח חסר או כוח על הגוף הלא נכון היא טעות ההכנה הנפוצה ביותר. השלימו FBD לפני כתיבת $\\Sigma F$.',
      },
      {
        facets: ['net_force_setup'],
        stem_en:
          'From your FBD, write the net-force equations $\\Sigma F_x$ and $\\Sigma F_y$ (or 1D $\\Sigma F$) and relate them to acceleration.',
        stem_he:
          'מתוך דיאגרמת הכוחות, כתבו משוואות כוח שקול $\\Sigma F_x$ ו-$\\Sigma F_y$ (או $\\Sigma F$ בחד-ממד) וקשרו לתאוצה.',
        correct_answer: 'ΣF = ma along each axis after resolving components',
        explanation_en:
          'Net force setup: after the FBD, choose axes, resolve each force into components, and write $\\Sigma F_x=ma_x$ and $\\Sigma F_y=ma_y$ (or a single axis in 1D). Include signs consistently with your axis choice. Do not plug numbers until the symbolic $\\Sigma F$ lines are written.',
        explanation_he:
          'הכנת כוח שקול: אחרי FBD, בחרו צירים, פרקו כל כוח לרכיבים, וכתבו $\\Sigma F_x=ma_x$ ו-$\\Sigma F_y=ma_y$ (או ציר אחד בחד-ממד). שמרו על סימנים עקביים עם בחירת הצירים. אל תציבו מספרים לפני כתיבת שורות $\\Sigma F$ הסימבוליות.',
      },
    ],
  },
  electric: {
    bases: [
      'electric_field',
      'electric_potential',
      'electric_circuits',
      'electric_field_gauss',
      'magnetism',
      'magnetic_field_biot_savart',
    ],
    facets: ['circuit_analysis_steps', 'field_vs_potential'],
    depthMarker: 'PHYS_ELEC_DEPTH',
    depthTitle: {
      en: 'HS E&M craft: field vs potential; circuit steps',
      he: 'מלאכת חשמל ומגנטיות: שדה מול פוטנציאל; שלבי מעגל',
    },
    depthBody: {
      en: `**E&M habit.** Separate **electric field** from **potential** (שדה חשמלי / פוטנציאל) before computing.
For circuits: follow **circuit analysis steps** — label nodes, write loop/junction equations (Kirchhoff), then solve.`,
      he: `**הרגל חשמל ומגנטיות.** הבחינו בין **שדה חשמלי** ל**פוטנציאל** לפני חישוב.
במעגלים: עקבו אחרי **שלבי ניתוח מעגל** — סמנו צמתים, כתבו משוואות לולאה/צומת (קירכהוף), ואז פתרו.`,
    },
    facetSection: {
      title_en: 'Facet depth: field vs potential; circuit analysis steps',
      title_he: 'העמקת פנים: שדה מול פוטנציאל; שלבי ניתוח מעגל',
      body_en_md: `**Field vs potential.** The electric field is a vector (force per charge); potential is a scalar (energy per charge). $E$ relates to minus the gradient of $V$ in simple geometries.

**Circuit analysis steps.** (1) Redraw and label. (2) Mark loops and junctions. (3) Write Kirchhoff loop/junction equations. (4) Solve; check units and power signs.`,
      body_he_md: `**שדה מול פוטנציאל.** השדה החשמלי הוא וקטור (כוח ליחידת מטען); הפוטנציאל הוא סקלר (אנרגיה ליחידת מטען). $E$ קשור למינוס גרדיאנט של $V$ בגיאומטריות פשוטות.

**שלבי ניתוח מעגל.** (1) שרטוט ותיוג. (2) סימון לולאות וצמתים. (3) משוואות קירכהוף. (4) פתרון; בדיקת יחידות וסימני הספק.`,
    },
    questions: [
      {
        facets: ['field_vs_potential'],
        stem_en:
          'For a situation from this lesson, state one electric-field quantity and one potential quantity, and explain how they differ (vector vs scalar / force vs energy).',
        stem_he:
          'למצב מהשיעור, ציינו גודל אחד של שדה חשמלי וגודל אחד של פוטנציאל, והסבירו במה הם נבדלים (וקטור מול סקלר / כוח מול אנרגיה).',
        correct_answer: 'E vector force/charge; V scalar energy/charge',
        explanation_en:
          'Field vs potential: $\\vec{E}$ is a vector describing force per unit charge; $V$ is a scalar describing energy per unit charge. Confusing them leads to wrong units and wrong vector algebra. State which object you need before choosing a formula.',
        explanation_he:
          'שדה מול פוטנציאל: $\\vec{E}$ הוא וקטור של כוח ליחידת מטען; $V$ הוא סקלר של אנרגיה ליחידת מטען. בלבול ביניהם מוביל ליחידות שגויות ולאלגברה וקטורית שגויה. ציינו איזה עצם נדרש לפני בחירת נוסחה.',
      },
      {
        facets: ['circuit_analysis_steps'],
        stem_en:
          'Outline Kirchhoff circuit analysis steps for a multi-element circuit from this lesson: nodes, one loop equation, one junction equation.',
        stem_he:
          'תארו שלבי ניתוח מעגל קירכהוף למעגל רב-רכיבים מהשיעור: צמתים, משוואת לולאה אחת, משוואת צומת אחת.',
        correct_answer: 'label; loops+junctions; Kirchhoff equations; solve',
        explanation_en:
          'Circuit analysis steps: redraw and label currents/voltages, identify independent loops and junctions, write Kirchhoff loop and junction (צומת / לולאה) equations, then solve the linear system. Check that the number of independent equations matches the unknowns before substituting numbers.',
        explanation_he:
          'שלבי ניתוח מעגל: שרטוט מחדש ותיוג זרמים/מתחים, זיהוי לולאות וצמתים בלתי תלויים, כתיבת משוואות קירכהוף ללולאה ולצומת, ואז פתרון המערכת. בדקו שמספר המשוואות הבלתי תלויות תואם לנעלמים לפני הצבת מספרים.',
      },
    ],
  },
};

function deepenFile(fileBase, fam) {
  const fp = path.join(DIR, `${fileBase}.json`);
  if (!fs.existsSync(fp)) return false;
  const lesson = JSON.parse(fs.readFileSync(fp, 'utf8'));
  lesson.sections = lesson.sections || [];

  const marker = `${fam.depthMarker}`;
  if (!lesson.sections.some((s) => (s.body_en_md || '').includes(marker))) {
    const insert = {
      kind: 'theory',
      title_en: fam.depthTitle.en,
      title_he: fam.depthTitle.he,
      body_en_md: `<!-- ${marker} -->\n${fam.depthBody.en}`,
      body_he_md: fam.depthBody.he,
    };
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, insert);
    else lesson.sections.push(insert);
  }

  if (!lesson.sections.some((s) => s.title_en && /Facet depth:/i.test(s.title_en) && fam.facets.some((f) => (s.body_en_md || '').toLowerCase().includes(f.split('_')[0])))) {
    // simpler: match facet section title
  }
  if (!lesson.sections.some((s) => s.title_en === fam.facetSection.title_en)) {
    const sumIdx = lesson.sections.findIndex((s) => s.kind === 'summary');
    const sec = { kind: 'theory', ...fam.facetSection };
    if (sumIdx >= 0) lesson.sections.splice(sumIdx, 0, sec);
    else lesson.sections.push(sec);
  }

  lesson.questions = lesson.questions || [];
  const existing = new Set();
  for (const q of lesson.questions) for (const f of q.facets || []) existing.add(f);
  for (const q of fam.questions) {
    if ((q.facets || []).some((f) => existing.has(f))) continue;
    lesson.questions.push({
      kind: 'open',
      difficulty: 'medium',
      ...q,
      id: `${fileBase}-facet-phys-${lesson.questions.length + 1}`,
      ord: lesson.questions.length + 1,
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
    for (const f of q.facets || []) existing.add(f);
  }

  const qid = `${fileBase}-phys-depth`;
  if (!lesson.questions.some((q) => q.id === qid)) {
    lesson.questions.push({
      id: qid,
      ord: lesson.questions.length + 1,
      kind: 'open',
      difficulty: 'hard',
      facets: fam.facets,
      stem_en: `Track drill: apply the ${fam.facets.join(' + ')} habits to one core scenario from this lesson, with a sketch and labeled equations.`,
      stem_he: `תרגיל מסלול: יישמו את הרגלי ${fam.facets.join(' + ')} על תרחיש מרכזי מהשיעור, עם סקיצה ומשוואות מסומנות.`,
      explanation_en:
        '**Worked path.** Sketch first, name the facet tools explicitly (components, graphs, FBD, field vs potential, etc.), write governing equations with labels, then compute. Keep vector/scalar and diagram discipline visible for method marks.',
      explanation_he:
        '**דרך פתרון.** סקיצה תחילה, ציינו במפורש את כלי הפנים (רכיבים, גרפים, FBD, שדה מול פוטנציאל וכו׳), כתבו משוואות שלטות עם תוויות, ואז חשבו. השאירו משמעת וקטור/סקלר ודיאגרמות גלויה לניקוד שיטה.',
      correct_answer: 'see physics track-depth + facet sections',
      skill_atoms: (lesson.skill_atom_bank || []).slice(0, 2),
    });
  }

  if (lesson.summary_en && !lesson.summary_en.includes('physics-family depth')) {
    lesson.summary_en = `${lesson.summary_en} Taught with HS physics-family depth habits.`;
  }

  fs.writeFileSync(fp, `${JSON.stringify(lesson, null, 2)}\n`);
  return true;
}

let n = 0;
for (const fam of Object.values(FAMILIES)) {
  for (const base of fam.bases) {
    const files = fs
      .readdirSync(DIR)
      .filter((f) => f === `${base}.json` || f.startsWith(`${base}__`))
      .map((f) => f.replace(/\.json$/, ''));
    for (const id of files) {
      if (deepenFile(id, fam)) {
        console.log('deepened', id);
        n++;
      }
    }
  }
}
console.log('deepened files', n);
