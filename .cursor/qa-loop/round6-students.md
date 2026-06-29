# QA Student Simulation — Round 6: Michal Peretz
**Simulated:** 2026-06-29 | **Model:** Sonnet 4.6 | **Persona:** 3pt Bagrut adult returner

---

## Full JSON Report

```json
{
  "student_id": "michal_peretz_3pt_adult_returner",
  "persona": {
    "age": 20,
    "goal": "bagrut_math_3",
    "background": "Dropped out at 17; 2-year gap; now in adult evening program",
    "language": "Hebrew (simple vocabulary)",
    "session_pattern": "30 min, 3-4x per week, evenings",
    "stress_profile": "high anxiety, rusty, motivated but fragile confidence"
  },

  "checkpoints": [
    {
      "label": "Day 1",
      "narrative": "פתחתי את האתר בפעם הראשונה בערב, אחרי העבודה. כל הדף בעברית — זה כבר הפתיע אותי לטובה. בחרתי 'בגרות במתמטיקה — 3 יח' ואז נתקלתי בשאלה 'כיתה / שכבה'. לא ידעתי מה לבחור — אני לא ב'כיתה י\"ב', אני בתוכנית ערב למבוגרים. בחרתי י\"ב כי זה הכי קרוב. ואז שאלו אותי 'עד כמה המורה שלך היה טוב?' — אין לי מורה כבר שנתיים! לא ידעתי מה לשים, שמתי 5. השאלה 'למה המטרה הזו חשובה לך?' היתה יפה — כתבתי שאני רוצה להוכיח לעצמי שאני יכולה. לאחר השלמת האבחון נכנסתי לדשבורד — הכל אפס. אפס רצף, אפס שיעורים, אפס ציון. לא היתה שום הודעת פתיחה כמו 'ברוכה הבאה, בואי נתחיל' — פשוט מספרים קפואים. לחצתי על 'מורה' כדי לראות מה קורה. השיחה היתה אדיבה ובעברית, ניסתה להבין איפה אני נמצאת. בסוף הרגשתי שהיה בסדר, אבל הכניסה הראשונה היתה קצת קרה.",
      "ux_score": 6,
      "stress_level": 7,
      "knowledge_scores": {
        "arithmetic": 3,
        "algebra_basics": 2,
        "equations_linear": 2,
        "equations_quadratic": 1,
        "functions_intro": 2,
        "geometry_basics": 3,
        "trigonometry_ratios": 1
      },
      "green_lights": [
        "הכל בעברית — כולל כל כפתור, תווית ושדה",
        "שאלת 'למה המטרה חשובה לך' — מרגישה אישית",
        "הבחירה 'בגרות — 3 יח' ברורה ומיידית",
        "שאלות רמת חרדה ומוטיבציה — מראות שהפלטפורמה מכירה בקושי הרגשי",
        "הטיימר ממועד הבגרות כבר נראה בדשבורד אחרי שהזנתי תאריך"
      ],
      "red_flags": [
        "אין אפשרות 'תוכנית ערב למבוגרים' בשדה כיתה — ניאלץ לבחור כיתה י\"ב שלא מייצגת את המצב",
        "שאלת 'עד כמה המורה שלך היה טוב' לא עובדת עבור מי שלא היה בבית ספר שנתיים — אין אפשרות 'לא רלוונטי'",
        "דשבורד עם כל אפס ביום הראשון — חסרה הודעת פתיחה מותאמת לחוזרים",
        "אין הנחיה 'מה לעשות עכשיו' לאחר האבחון"
      ],
      "would_continue": true
    },
    {
      "label": "Week 1",
      "narrative": "עברתי כמה שיעורים — חשבון ויסודות האלגברה. שיעור החשבון ב-3 יח' היה מצוין: בעברית, עם דוגמאות פתורות, בהירות, ללא ז'רגון. בדיוק מה שהייתי צריכה. אבל כשהגעתי לשיעור יסודות האלגברה ולחצתי על 'איברים דומים ושלוש הזהויות' — החלק התיאורטי ב-3 יח' פתאום עבר לאנגלית! הטקסט של section body_he_md היה בפועל באנגלית, לא עברית. הרגשתי אבודה. האם אני בדף הלא נכון? גוגל תרגום, הבנתי בסוף, אבל זה פגע בביטחון שלי. גם לחצן 'Back to lessons' בדף השיעור הוא באנגלית, בעוד שהשאר בעברית — מבלבל. הרצף עלה ל-3 ימים ← זה עודד אותי. הדשבורד מראה שיעורים שעשיתי ואחוזי שליטה — נראה טוב. ניסיתי את הכרטיסייה 'התקדמות' — הגרף מראה שיטת שליטה לנושא אחד בלבד, לא לכולם ביחד.",
      "ux_score": 6,
      "stress_level": 6,
      "knowledge_scores": {
        "arithmetic": 5,
        "algebra_basics": 4,
        "equations_linear": 3,
        "equations_quadratic": 2,
        "functions_intro": 2,
        "geometry_basics": 3,
        "trigonometry_ratios": 1
      },
      "green_lights": [
        "שיעור חשבון 3 יח' — בעברית, ברור, עם דוגמאות פתורות וסיכום המלכודות",
        "הרצף (streak) ↑ — מעודד",
        "הדשבורד מציג שיעורים אחרונים עם פרוגרס בר — בהיר",
        "אין תוכן ממוצע מ-5 יח' שנוחת על מי ש-3 יח' (הסינון עובד בחלק)"
      ],
      "red_flags": [
        "CRITICAL: algebra_basics — שדה body_he_md של section 3pt בחלק התיאוריה והדוגמה הפתורה הוא בפועל אנגלית, לא עברית. תלמידה שלומדת בעברית נחשפת לתוכן באנגלית ללא אזהרה.",
        "כפתור 'Back to lessons' בדף שיעור ← בעברית תמיד נשאר באנגלית",
        "גרף 'שליטה לאורך זמן' מציג נתוני היסטוריה של הנושא הראשון בלבד (concepts[0]) — תמונה חלקית מאוד",
        "אין 'כל הנושאים' view בגרף ההתקדמות — תלמידה לא יודעת מה קורה עם שאר הנושאים"
      ],
      "would_continue": true
    },
    {
      "label": "Month 1",
      "narrative": "עברתי חשבון, יסודות האלגברה, משוואות מדרגה ראשונה וריבועית, אי-שוויונים ופונקציות לינאריות. הקצב של 30 דקות בערב עובד טוב — השיעורים קצרים ומובנים. שמתי לב שבמסך השיעורים, 'סדרות חשבוניות' לא מופיע בחלק של 3 יח' — אין לו lesson שמתויג 3pt בסינון. זה מבלבל, כי ידוע לי מהלמידה בכיתה (לפני שנתיים) שסדרות חשבוניות הן חלק מהבגרות שלי. גם הסתברות בסיסית לא מופיעה בחלק 3 יח' — הכל רשום כ-4 יח' ומעלה. שאלתי את המורה-AI וקיבלתי תשובה כלליות. הסוכן לא הכיר את הבעיה. בנתיים, שיעורי המשוואות הריבועיות ופונקציות ריבועיות היו מצוינים — עברית, דוגמאות ברורות. הדשבורד 'הבא עכשיו' ממליץ נושאים בצורה חכמה.",
      "ux_score": 7,
      "stress_level": 5,
      "knowledge_scores": {
        "arithmetic": 7,
        "algebra_basics": 6,
        "equations_linear": 7,
        "equations_quadratic": 5,
        "inequalities": 5,
        "functions_linear": 6,
        "functions_quadratic": 4,
        "geometry_basics": 4,
        "trigonometry_ratios": 2,
        "sequences_arithmetic": 1,
        "probability_basic": 1
      },
      "green_lights": [
        "כרטיס 'למד עכשיו' בדשבורד — ממליץ על הנושא החלש הבא, מדויק",
        "שיעורי equations_quadratic, inequalities, functions_linear — כולם בעברית, כולם עם שאלות תרגול",
        "ציון הרצף ↑ עד 15 ימים — מוטיבציה",
        "כרטיסיית 'זיכרון' קיימת — נחמד לראות מה הסוכן זוכר עליי"
      ],
      "red_flags": [
        "CRITICAL: sequences_arithmetic ו-probability_basic מתויגים math_track=[4pt,5pt] בלבד בלסונס-אינדקס — לא מופיעים לתלמידת 3 יח' בסינון quiz ו-dashboard. אבל הם מוגדרים ב-MATH_3PT_LEGACY_EXTRA באונבורדינג! חוסר תיאום קריטי.",
        "statistics_descriptive — מוגדר כ-3pt concept באונבורדינג אבל אין לו שיעור מאוגר כלל (אין קובץ בלסונס-אינדקס)",
        "ה-progress chart עדיין מציג נתוני היסטוריה של נושא אחד בלבד"
      ],
      "would_continue": true
    },
    {
      "label": "Month 3",
      "narrative": "עברתי רוב הנושאים של 3 יח' — חשבון, אלגברה, פונקציות, גיאומטריה, טריגונומטריה. הרגשה של התקדמות אמיתית. הבאנר 'סיימת את יעד השבוע' הופיע שלוש פעמים ועודד מאוד. התקרבתי לסדרות חשבוניות — הנושא מופיע בשיחה עם המורה אבל כשניסיתי למצוא שיעור דרך ה-quiz, לא מצאתי אותו — הפילטר של 3pt לא כולל אותו. הצלחתי לגשת לשיעור בנתיב ישיר (/app/lessons/l/sequences_arithmetic) ואז ראיתי שהוא נכלל, אבל לא מוצע לי אוטומטית. ניסיתי גם לפתוח שיעור הסתברות — אותה בעיה. אני מבלה שיח ארוך עם סוכן המורה שממש מנסה לעזור, מסביר, שואל שאלות סוקרטיות — תחושת אישיות ממשית. ה-Coach עזר לי לתרגל אי-שוויונות בצורה ממוקדת. לאחר 3 חודשים, הניקוד שלי באחוזי שליטה: חשבון 80%, יסודות אלגברה 72%, משוואות 75%, פונקציות 65%.",
      "ux_score": 7,
      "stress_level": 4,
      "knowledge_scores": {
        "arithmetic": 8,
        "algebra_basics": 7,
        "equations_linear": 8,
        "equations_quadratic": 7,
        "inequalities": 7,
        "exponents": 6,
        "functions_linear": 8,
        "functions_quadratic": 6,
        "functions_intro": 7,
        "geometry_basics": 6,
        "analytic_geometry_basic": 5,
        "trigonometry_ratios": 5,
        "word_problems": 5,
        "sequences_arithmetic": 3,
        "probability_basic": 2,
        "descriptive_stats": 2
      },
      "green_lights": [
        "Goal completion banner — 'סיימת את יעד השבוע!' בעברית, מעודד, עם כפתורי פעולה",
        "שיחות עם המורה AI מרגישות אישיות — זוכר מה שיחקתי בשיעורים קודמים",
        "Coach מוצלח לתרגול ממוקד — שואל שאלות קצרות ומדויקות",
        "אחוזי שליטה per-concept בדשבורד — מראה איפה אני חזקה ואיפה חלשה",
        "Bagrut countdown מציג '90 ימים לבגרות' עם מסר 'מחצית הדרך' — קשור למציאות"
      ],
      "red_flags": [
        "sequences_arithmetic ו-probability_basic לא מוצעים אוטומטית לתלמידת 3pt — דורש גישה ישירה לURL",
        "אין 'mock Bagrut exam' — אין סימולציית מבחן שלמה בפורמט בגרות אמיתי",
        "כפתור 'הגדר יעד חדש' ב-GoalCompletionBanner מחזיר ל-onboarding מלא (4 צעדים) — חיכוך מיותר לחידוש יעד"
      ],
      "would_continue": true
    },
    {
      "label": "Month 6",
      "narrative": "מגיעה לשבועיים לפני הבגרות. ה-countdown מציג 14 ימים בצבע אדום-מגנטה — 'לחץ אחרון. אתה יכולה!' עם הבאנר הנכון. עברתי כמעט כל נושאי 3 יח': חשבון, אלגברה, פונקציות, גיאומטריה, טריגונומטריה. כמה נושאים (סדרות, הסתברות, סטטיסטיקה) השגתי רק בדרכי עקיפות — המורה הסביר אבל לא קיבלתי שיעורים מסודרים עם תרגול מלא. הרגשתי לא בטוחה בהם. אין סימולטור בגרות מלא — ניסיתי ה-quiz הממוחשב וזה עזר חלקית, אבל הוא לא בנוי כמו מבחן בגרות אמיתי (60-90 דקות, ניקוד). אחרי 6 חודשים על הפלטפורמה, ההרגשה הכללית: למדתי הרבה, הרבה יותר ממה שהייתי עושה לבד. הסוכנים (בעיקר מורה ומאמן) מאוד עזרו. אבל חסרים לי 3 נושאים ל-3 יח' שלא קיבלו כיסוי מלא, ואני לא בטוחה שאני מוכנה 100% לבגרות.",
      "ux_score": 7,
      "stress_level": 8,
      "knowledge_scores": {
        "arithmetic": 9,
        "algebra_basics": 8,
        "equations_linear": 9,
        "equations_quadratic": 8,
        "inequalities": 8,
        "exponents": 7,
        "word_problems": 7,
        "functions_intro": 8,
        "functions_linear": 9,
        "functions_quadratic": 7,
        "geometry_basics": 7,
        "analytic_geometry_basic": 6,
        "trigonometry_ratios": 6,
        "sequences_arithmetic": 5,
        "probability_basic": 4,
        "descriptive_stats": 4,
        "statistics_descriptive": 3
      },
      "green_lights": [
        "Bagrut countdown — צבע אדום בשבועיים האחרונים, מסר 'לחץ אחרון', מדויק ומעורר",
        "כיסוי הנושאים העיקריים (arithmetic → functions_quadratic) עמוק ומסודר",
        "שיחות מורה ממשיכות להיות אישיות — זוכר את כל ההתקדמות",
        "מוטיבציה גבוהה — עמדתי ב-3-4 פגישות בשבוע לכל 6 חודשים",
        "אחוזי שליטה גבוהים (75%+) ב-11 מתוך 17 נושאי 3 יח'"
      ],
      "red_flags": [
        "אין 'mock Bagrut exam' — סימולציה מלאה בפורמט בגרות עם ניקוד ותיזמון",
        "sequences_arithmetic, probability_basic, statistics_descriptive — כיסוי חלקי בגלל באג track mismatch",
        "GoalCompletionBanner — 'הגדר יעד חדש' שולח לאונבורדינג מלא, לא לתהליך עדכון מקוצר",
        "אחרי 6 חודשים, אין 'Bagrut readiness score' — לא ברור אם אני מוכנה"
      ],
      "would_continue": true
    }
  ],

  "issues": [
    {
      "id": "ISS-001",
      "category": "personalization",
      "severity": "high",
      "description": "אין נתיב 'תלמיד/ה חוזר/ת' או 'תוכנית ערב למבוגרים' באונבורדינג. שדה הכיתה מוגבל לכיתות ז'-י\"ב ואוניברסיטה. מי שחזר לאחר פסקה אינו מיוצג.",
      "root_cause": "GRADE_LEVELS array in onboarding/page.tsx does not include adult_education or returning_student options",
      "suggested_fix": "הוסף אפשרות 'חוזר/ת לאחר הפסקה / תוכנית ערב' לרשימת הכיתות. כאשר נבחרת, שנה את ניסוח השאלות ואת קצב תוכנית הלמידה לפי פסקה.",
      "affects_students": ["3pt", "4pt", "5pt", "physics"]
    },
    {
      "id": "ISS-002",
      "category": "ux",
      "severity": "medium",
      "description": "שאלת 'עד כמה המורה שלך היה טוב?' (teacherRating) מניחה שהיה מורה לאחרונה. עבור מי שלא היה בבית-ספר שנתיים, השאלה מבלבלת ואין אפשרות 'לא רלוונטי'.",
      "root_cause": "s1_teacherRating slider has no N/A option; phrasing assumes recent school attendance",
      "suggested_fix": "הוסף checkbox 'לא למדתי לאחרונה / לא רלוונטי' שמאפשר לדלג על שדה זה ולהגדיר ברירת מחדל מתאימה (5). עדכן את הניסוח ל-'עד כמה המורה האחרון שלך היה טוב? (אם רלוונטי)'",
      "affects_students": ["3pt", "4pt", "5pt", "physics"]
    },
    {
      "id": "ISS-003",
      "category": "content",
      "severity": "critical",
      "description": "בשיעור algebra_basics, ה-body_he_md של sections type=theory ו-worked_example בגרסת 3pt הוא בפועל טקסט אנגלי — לא עברית. תלמידה שלומדת בעברית נחשפת לאנגלית ללא אזהרה.",
      "root_cause": "algebra_basics.json body_by_level.3pt.body_he_md fields contain English text copied verbatim, not translated Hebrew",
      "suggested_fix": "תרגם את כל שדות body_he_md ב-sections theory ו-worked_example ל-3pt באנגלית לעברית. הוסף CI lint rule שמוודא ש-body_he_md מכיל לפחות X% תווים עבריים.",
      "affects_students": ["3pt", "4pt", "5pt"]
    },
    {
      "id": "ISS-004",
      "category": "content",
      "severity": "critical",
      "description": "arithmetic.json — ה-body_by_level.4pt intro section מכיל תוכן של פתרון משוואה $2^x+5^x=3^x$ בשיטת נגזרות/לוגריתמים — תוכן 5pt בלבד שהוצב בטעות בגרסת 4pt. גם body_he_md של section זה הוא באנגלית.",
      "root_cause": "Content generation error: 4pt body_by_level section contains 5pt-level material (derivatives, sign charts) and English text in the Hebrew field",
      "suggested_fix": "החלף את body_by_level.4pt.intro בתוכן המתאים ל-4pt (order of operations עם דוגמאות מעט מורכבות יותר מ-3pt). תרגם body_he_md לעברית.",
      "affects_students": ["4pt", "5pt"]
    },
    {
      "id": "ISS-005",
      "category": "content",
      "severity": "critical",
      "description": "sequences_arithmetic ו-probability_basic מוגדרים כנושאי 3pt ב-MATH_3PT_LEGACY_EXTRA ב-onboarding אבל מתויגים math_track=['4pt','5pt'] ב-lessons-index.generated.json. כתוצאה, סינון ה-quiz ו-computeNextLesson דשבורד לא מציעים אותם לתלמיד 3pt.",
      "root_cause": "Mismatch between onboarding concept registry (MATH_3PT_LEGACY_EXTRA) and lesson index math_track tags. The quiz page allowedLevels('3') returns Set(['3pt']) but sequences_arithmetic lesson is tagged ['4pt','5pt'].",
      "suggested_fix": "1) הוסף '3pt' ל-math_track של sequences_arithmetic.json ו-probability_basic.json. 2) אם אלו נושאי legacy שרוצים להחריג מהתוכנית החדשה, הסר אותם מ-MATH_3PT_LEGACY_EXTRA ועדכן את Self-Score concepts. 3) הוסף integration test שמוודא ש-concept IDs ב-CONCEPTS_BY_GOAL מוצאים match בלסונס-אינדקס.",
      "affects_students": ["3pt"]
    },
    {
      "id": "ISS-006",
      "category": "content",
      "severity": "high",
      "description": "statistics_descriptive מוגדר כ-3pt concept באונבורדינג אבל אין לו שיעור מאוגר כלל בלסונס-אינדקס (אין קובץ statistics_descriptive.json). תלמיד 3pt ישאל על כך בשלב האבחון העצמי ואז לא ימצא שיעור.",
      "root_cause": "statistics_descriptive concept in ALL_CONCEPTS and MATH_3PT_CONCEPTS has no corresponding authored lesson file",
      "suggested_fix": "צור שיעור statistics_descriptive.json עם math_track=['3pt','4pt','5pt'] שמכסה ממוצע, חציון, שכיח, טווח, שונות, גרפים סטטיסטיים. לחלופין, אחד עם descriptive_stats ועדכן את שמות הנושאים.",
      "affects_students": ["3pt"]
    },
    {
      "id": "ISS-007",
      "category": "navigation",
      "severity": "low",
      "description": "כפתור 'Back to lessons' בדף שיעור (apps/web/src/app/(app)/app/lessons/l/[lessonId]/page.tsx) הוא טקסט אנגלי קשוח — לא מתורגם כאשר האתר בעברית.",
      "root_cause": "Hardcoded English string 'Back to lessons' in lesson page, not using i18n/locale",
      "suggested_fix": "הוסף לוקאליזציה לכפתור: 'חזרה לשיעורים' בעברית. השתמש ב-useI18n() או העבר locale מה-server component.",
      "affects_students": ["3pt", "4pt", "5pt", "physics", "university"]
    },
    {
      "id": "ISS-008",
      "category": "ux",
      "severity": "medium",
      "description": "גרף 'שליטה לאורך זמן' בדף ההתקדמות מציג נתוני היסטוריה של הנושא הראשון בלבד (progress.concepts[0]?.history). תלמידה עם 10+ נושאים לא יכולה לראות מגמה כוללת.",
      "root_cause": "ProgressDashboard: historyData is computed only from progress.concepts[0]?.history — hardcoded first concept",
      "suggested_fix": "הוסף dropdown לבחירת נושא לגרף ההיסטוריה, או הצג aggregated progress line המחשב ממוצע שליטה כוללת לאורך זמן מכל הנושאים.",
      "affects_students": ["3pt", "4pt", "5pt", "physics", "university"]
    },
    {
      "id": "ISS-009",
      "category": "missing_feature",
      "severity": "high",
      "description": "אין סימולציית מבחן בגרות מלאה — mock exam בפורמט הרשמי (60-90 דקות, ניקוד מ-100, שאלות מכל הנושאים). ה-quiz המובנה מוגבל לנושא אחד ולא מדמה את לחץ הזמן.",
      "root_cause": "No full-exam simulation feature exists; /app/quiz generates per-concept quizzes only",
      "suggested_fix": "הוסף 'בגרות מדומה' — quiz שמערב נושאים מהרשימה הרלוונטית לרמה (3pt/4pt/5pt), עם זמן מוגבל, ניקוד ומשוב מפורט אחרי הסיום.",
      "affects_students": ["3pt", "4pt", "5pt", "physics"]
    },
    {
      "id": "ISS-010",
      "category": "ux",
      "severity": "low",
      "description": "בנר 'השלמת יעד' (GoalCompletionBanner) — כפתור 'הגדר יעד חדש' מנתב ל-/onboarding המלא (4 שלבים). מי שרוצה רק לעדכן תאריך יעד עובר תהליך ארוך.",
      "root_cause": "GoalCompletionBanner links to /onboarding instead of a lighter goal-update flow",
      "suggested_fix": "הוסף modal/drawer מקוצר לעדכון יעד (שלב 0 בלבד של האונבורדינג — goal + timeline). אם לא אפשרי, הנח את המשתמש מה לצפות: 'תגיעי לשלב 1 ותשמרי — שאר הנתונים יישמרו'.",
      "affects_students": ["3pt", "4pt", "5pt", "physics", "university"]
    },
    {
      "id": "ISS-011",
      "category": "ux",
      "severity": "medium",
      "description": "דשבורד יום 1 לתלמידה חדשה מציג 0 רצף, 0 שיעורים, 0 רמה. אין הודעת פתיחה מיוחדת לחוזר/ת אחרי הפסקה — הכניסה הראשונה קרה ומאיימת.",
      "root_cause": "DashboardContent shows pure zeros with no contextual welcome or guidance for brand-new learners; no adult-returner variant",
      "suggested_fix": "הצג 'ברוכה הבאה, [שם]! יחד נגיע לבגרות' card בדשבורד ל-24-48 שעות הראשונות. עבור תלמידים שסיימו אונבורדינג אך עדיין streak_days=0, הצג CTA 'התחל את השיעור הראשון' מוגדל.",
      "affects_students": ["3pt", "4pt", "5pt", "physics", "university"]
    },
    {
      "id": "ISS-012",
      "category": "content",
      "severity": "medium",
      "description": "fractions_algebraic מתויג math_track=['3pt','4pt','5pt'] בלסונס-אינדקס, אבל מוגדר ב-MATH_4PT_EXTRA באונבורדינג. תלמידת 3pt תראה אותו בסינון המערכת אבל לא תאמן עליו עצמית.",
      "root_cause": "Inconsistency between onboarding concept categorization and lesson index math_track for fractions_algebraic",
      "suggested_fix": "החלט: האם fractions_algebraic שייך ל-3pt? אם כן — הוסף ל-MATH_3PT_CONCEPTS. אם לא — שנה math_track ב-fractions_algebraic.json ל-['4pt','5pt'].",
      "affects_students": ["3pt"]
    }
  ],

  "rubric_scores": {
    "learning_improvement_progress": {
      "weight": 0.20,
      "raw_score": 6.5,
      "notes": "מנגנון הלמידה (mastery tracking, next-lesson logic, agent memory) עובד ומשפר ידע לאורך זמן. אבל גרף ההתקדמות מראה נושא אחד בלבד, אין 'Bagrut readiness score', והדשבורד ביום 1 קר."
    },
    "material_coverage_3pt": {
      "weight": 0.20,
      "raw_score": 5.5,
      "notes": "11 מתוך 17 נושאי 3 יח' מכוסים היטב עם שיעורים מאוגרים. אבל: sequences_arithmetic ו-probability_basic לא מוצגים לתלמידת 3pt בגלל track mismatch; statistics_descriptive חסר לגמרי; fractions_algebraic categorized incorrectly."
    },
    "language_fit_hebrew": {
      "weight": 0.15,
      "raw_score": 4.5,
      "notes": "האונבורדינג, הדשבורד וסוכני ה-AI בעברית מלאה ✅. אבל algebra_basics 3pt theory/worked_example body_he_md בפועל באנגלית ⚠️. arithmetic 4pt intro body_he_md באנגלית ⚠️. לכפתור 'Back to lessons' באנגלית ⚠️. מי שלומד בעברית נתקל באנגלית פתאומית."
    },
    "retention_memory": {
      "weight": 0.10,
      "raw_score": 7.0,
      "notes": "מערכת הזיכרון (per-agent notes, learner persona, chat_turns) עובדת ברקע. כרטיסיית 'זיכרון' קיימת. השיחות עם הסוכנים מרגישות ממשיות ומשתמשות בהיסטוריה. הדרימינג/קונסולידציה בנויים. ציון גבוה לפיצ'ר, לא בדקנו תוכן זיכרון בפועל."
    },
    "accessibility_adult_returner": {
      "weight": 0.10,
      "raw_score": 4.0,
      "notes": "אין נתיב 'תלמיד חוזר' / 'תוכנית ערב'. teacherRating לא עובד לחוזרים. grade_level אין adult_education. בחירת 'ערב' כזמן לימוד עובדת ✅. שאלת 'למה המטרה חשובה' מרגישה אישית ✅. בסך הכל הפלטפורמה מיועדת לתלמידי תיכון ולא התאימה עצמה לבוגרים."
    },
    "uniqueness_vs_classes": {
      "weight": 0.10,
      "raw_score": 8.0,
      "notes": "ה-Bagrut countdown, סוכני AI (מורה, מאמן, מנטור, מעריך), זיכרון לאורך זמן, אין שיעורי בית/מורה בשר ודם שלוחצים — אלו יתרונות אמיתיים על תוכנית ערב רגילה. ה-AI מסביר בסבלנות, זמין בלילה, לא שופט."
    },
    "bagrut_success_likelihood": {
      "weight": 0.15,
      "raw_score": 5.5,
      "notes": "הנושאים העיקריים (arithmetic→functions_quadratic) מכוסים טוב. אבל 3 נושאים חסרים/חלקיים (sequences, probability, stats). אין mock Bagrut exam. אין Bagrut readiness score. תלמידה לא יודעת אם היא מוכנה. סיכוי טוב אבל לא ודאי."
    }
  },

  "weighted_score_calculation": {
    "learning_improvement":  { "weight": 0.20, "score": 6.5, "contribution": 1.30 },
    "material_coverage":     { "weight": 0.20, "score": 5.5, "contribution": 1.10 },
    "language_fit":          { "weight": 0.15, "score": 4.5, "contribution": 0.675 },
    "retention_memory":      { "weight": 0.10, "score": 7.0, "contribution": 0.70 },
    "accessibility":         { "weight": 0.10, "score": 4.0, "contribution": 0.40 },
    "uniqueness":            { "weight": 0.10, "score": 8.0, "contribution": 0.80 },
    "bagrut_success":        { "weight": 0.15, "score": 5.5, "contribution": 0.825 },
    "TOTAL_WEIGHTED":        5.80
  },

  "final_satisfaction": 6,
  "final_knowledge_gain": "good",
  "summary": "מיכל מרגישה שהפלטפורמה עזרה לה באמת — שיחות ה-AI אישיות, הלמידה מסודרת, והיא עברה מ-2/10 ל-7/10 ב-11 נושאי ליבה תוך 6 חודשים. אבל שלושה נושאי חובה ל-3 יח' (סדרות, הסתברות, סטטיסטיקה תיאורית) לא הוצגו לה אוטומטית בגלל באג track-mismatch קריטי, ותוכן עברי חסר בשיעורי אלגברה פגע בחוויה. חסרים לה mock Bagrut exam ו-Bagrut readiness score לפני הבחינה — בלעדיהם, היא לא יודעת עד כמה היא מוכנה."
}
```

---

## Final Weighted Score

| ממד | משקל | ציון | תרומה |
|-----|------|------|-------|
| שיפור בלמידה / התקדמות | 20% | 6.5/10 | 1.30 |
| כיסוי תוכנית 3 יח' | 20% | 5.5/10 | 1.10 |
| התאמת שפה — עברית נגישה | 15% | 4.5/10 | 0.675 |
| שימור — זיכרון / פתקים | 10% | 7.0/10 | 0.70 |
| נגישות לתלמיד מבוגר חוזר | 10% | 4.0/10 | 0.40 |
| ייחודיות לעומת לימודים קלאסיים | 10% | 8.0/10 | 0.80 |
| סיכוי הצלחה בבגרות | 15% | 5.5/10 | 0.825 |
| **סה"כ משוקלל** | **100%** | | **5.80 / 10** |

---

## Critical Issues Summary (תיקונים דחופים)

| עדיפות | Issue | קובץ / מיקום |
|--------|-------|-------------|
| 🔴 CRITICAL | ISS-005: sequences_arithmetic + probability_basic track mismatch — לא מוצגים ל-3pt | `lessons-index.generated.json`, `quiz/page.tsx` |
| 🔴 CRITICAL | ISS-003: algebra_basics 3pt body_he_md באנגלית | `scripts/seed_data/lessons/algebra_basics.json` |
| 🔴 CRITICAL | ISS-006: statistics_descriptive — אין שיעור מאוגר | צריך ליצור `statistics_descriptive.json` |
| 🟠 HIGH | ISS-004: arithmetic 4pt intro — תוכן 5pt + אנגלית | `scripts/seed_data/lessons/arithmetic.json` |
| 🟠 HIGH | ISS-001: אין נתיב חוזר/ת למבוגרים באונבורדינג | `apps/web/src/app/onboarding/page.tsx` |
| 🟠 HIGH | ISS-009: אין mock Bagrut exam | feature request |
| 🟡 MEDIUM | ISS-008: גרף היסטוריה מציג נושא אחד בלבד | `apps/web/src/components/progress-dashboard.tsx` |
| 🟡 MEDIUM | ISS-002: teacherRating ללא אפשרות N/A | `apps/web/src/app/onboarding/page.tsx` |
| 🟡 MEDIUM | ISS-011: דשבורד קר ביום 1 | `apps/web/src/components/dashboard-content.tsx` |
| 🟡 MEDIUM | ISS-012: fractions_algebraic track mismatch | `lessons-index.generated.json` |
| 🟢 LOW | ISS-007: 'Back to lessons' בעברית | `apps/web/src/app/(app)/app/lessons/l/[lessonId]/page.tsx` |
| 🟢 LOW | ISS-010: goal completion banner → full onboarding | `apps/web/src/components/goal-completion-banner.tsx` |
