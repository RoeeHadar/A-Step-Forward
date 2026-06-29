# S05 — Mohammed Abo Saleh — QA Simulation Report

**Student:** Mohammed Abo Saleh · 11th grade · 3pt math Bagrut  
**Persona:** Arabic-speaking family, Jewish-Arab mixed school, simple Hebrew preferred, 20–30 min sessions before bed  
**QA Date:** 29 Jun 2026  
**Simulator version:** Round 6

---

## JSON Report

```json
{
  "student_id": "S05-mohammed-abo-saleh",
  "persona": {
    "grade": "11",
    "track": "3pt",
    "native_language": "Arabic",
    "school_language": "Hebrew",
    "hebrew_fluency": "functional_non_native",
    "goal": "Pass Bagrut 3pt math with 56+",
    "weak_areas": ["word_problems", "sequences_arithmetic", "probability_basic"],
    "session_pattern": "20-30 min before bed"
  },
  "checkpoints": [
    {
      "label": "Day 1",
      "narrative": "אני פותח את האתר בסביבות 10 בלילה. הכל בעברית — מגניב, זה נראה בסדר. שאלה ראשונה: 'לקראת מה את/ה לומד/ת?' — הבנתי אבל ה-'את/ה' נראה קצת מוזר בשבילי, אנחנו לא כותבים ככה בבית. בחרתי 'בגרות במתמטיקה — 3 יח׳' — זה ברור. אחרי כמה שאלות על עצמי הגעתי לדשבורד. ראיתי כפתור שכתוב בו 'Back to lessons' — מה זה? אנגלית פתאום? לחצתי בכל זאת. דף הלימוד פתח — בעברית. טוב. פתחתי את שיעור החשבון. הכותרת הראשית 'Arithmetic — The Number System and Its Rules' — שוב אנגלית?? ויש כתוביות קטנות בעברית מתחת. לא הבנתי למה אנגלית ראשונה. בכל זאת, גללתי לתוך השיעור — ההסברים בעברית כולם, נקי ומובן. עשיתי שאלה אחת (MCQ) — הבנתי אותה. יצאתי מרוצה. 6/10.",
      "ux_score": 6,
      "stress_level": 5,
      "knowledge_scores": {
        "arithmetic": 3,
        "sequences_arithmetic": 2,
        "probability_basic": 2,
        "word_problems": 2
      },
      "green_lights": [
        "Onboarding fully in Hebrew — labels, goals, grade levels all translated",
        "3pt goal selection is clear and immediately recognizable",
        "Arithmetic lesson body text in Hebrew is clean, natural, and grade-appropriate",
        "MCQ questions have proper Hebrew stems (stem_he) — Mohammed could read them unaided",
        "Dashboard Bagrut countdown in Hebrew is motivating and well-worded",
        "NextLessonCard 'למד עכשיו' and 'הנושא החלש ביותר' labels — excellent simple Hebrew"
      ],
      "red_flags": [
        "CRITICAL: Lesson page primary <h1> shows English title ('Arithmetic — The Number System and Its Rules') — Hebrew is the secondary, smaller line. For a student who reads Hebrew as his school language, this inverts the expected hierarchy.",
        "HIGH: 'Back to lessons' navigation link is hardcoded English — first confusing element encountered post-onboarding. No Hebrew equivalent ('חזרה לשיעורים').",
        "MEDIUM: Gender-inclusive Hebrew forms ('את/ה לומד/ת', 'מרגיש/ה') in onboarding add visual noise — Arabic native speakers are used to gender-separated forms and the slash pattern looks like a typo or special character.",
        "LOW: Lesson subject and duration shown as '12 min · math' — 'math' is not localized to 'מתמטיקה'."
      ],
      "would_continue": true
    },
    {
      "label": "Week 1",
      "narrative": "חזרתי כמה פעמים השבוע. ניסיתי לחפש שיעור על סדרות חשבוניות כי המורה שלי לימדה את זה השבוע. מצאתי את הנושא ברשימה — 'סדרות חשבוניות'. פתחתי. אבל מה שהיה שם היה קשה מדי לי. מדברים על 'הטריק של גאוס', נוסחאות עם $a_n$, הוכחה של הסכום... במקצה שלי אנחנו עובדים על דברים יותר פשוטים. ניסיתי גם שיעור על הסתברות — שם היה עוד יותר קשה: הסתברות מותנית, נוסחת בייס... זה לא 3 יחידות. זה נראה כמו תוכן לתלמידי 4-5 יחידות. סגרתי ופתחתי את 'המורה' בצ'אט. כתבתי לו 'אני לא מבין את הסדרות, עזור לי'. הוא ענה בעברית פשוטה — טוב! אבל בלי שיעור בדרגה שלי, אני מרגיש שאני מבזבז זמן.",
      "ux_score": 5,
      "stress_level": 7,
      "knowledge_scores": {
        "arithmetic": 4,
        "sequences_arithmetic": 2,
        "probability_basic": 2,
        "word_problems": 2
      },
      "green_lights": [
        "AI Tutor chat responded in simple, direct Hebrew — matched Mohammed's needs",
        "Lesson catalog shows Hebrew category labels — student can find subjects without English",
        "Arithmetic lesson practice questions progressing well — MCQ and numeric types handled"
      ],
      "red_flags": [
        "CRITICAL: sequences_arithmetic.json is tagged math_track: ['4pt', '5pt'] — there is NO authored 3pt content for this topic. The lesson loaded 4pt-level content (Gauss proof, parametric sum formulas). A 3pt student is immediately out of depth.",
        "CRITICAL: probability_basic.json is tagged math_track: ['4pt', '5pt'] — same problem. Conditional probability and Bayes' formula are NOT in the 3pt Bagrut syllabus. Mohammed hit this content and closed the app.",
        "HIGH: The body_by_level content for 4pt in both sequences and probability lessons has body_he_md fields that contain English text, not Hebrew. Example from sequences_arithmetic 4pt body_he_md: 'In this section, we will explore the closed-form formulas...' — the label says Hebrew but the content is English.",
        "HIGH: Several 3pt body_he_md sections in arithmetic are truncated mid-sentence. Example pitfall section 3pt: '...ראשית, נבצע את החיל' cuts off mid-word. Mohammed reads an incomplete explanation and cannot understand the step.",
        "MEDIUM: Word problems concept has no dedicated lesson — it appears in Mohammed's 3pt concept list but clicking on word_problems would yield a notFound() since there's no authored lesson or seed lesson for it."
      ],
      "would_continue": true
    },
    {
      "label": "Month 1",
      "narrative": "מיחד להשתמש באתר כל לילה לפחות 20 דקות. שיעור החשבון סיימתי. עברתי לשיעור משוואות — גם טוב. הצ'אט עם המורה עוזר לי כשאני תקוע. פעם אחת כתבתי לו בעברית שבורה וענה לי בסבלנות — נחמד. אבל הסתברות ממשיכה להיות בעיה. ניסיתי שוב לפתוח את שיעור ההסתברות ולקרוא. ראיתי 'הסתברות מותנית: $P(A|B) = \\frac{P(A \\cap B)}{P(B)}$' ולא הבנתי בכלל. במקצה שלי עדיין לא הגענו לזה. ביקשתי מהמורה בצ'אט להסביר הסתברות פשוטה לרמת 3 יחידות. הוא הסביר יפה! אבל האם יש לי מבחן אחרי זה? לא ראיתי אפשרות לתרגל הסתברות ברמת 3 יחידות. לחצתי על 'מבחן' — בחרתי הסתברות. המבחן שנוצר — שאלות הסתברות. כמה היו ברמה טובה אבל אחת שאלה על בייס שלא הכרתי.",
      "ux_score": 6,
      "stress_level": 6,
      "knowledge_scores": {
        "arithmetic": 6,
        "sequences_arithmetic": 3,
        "probability_basic": 3,
        "word_problems": 3,
        "equations_linear": 5,
        "equations_quadratic": 4
      },
      "green_lights": [
        "AI Tutor adapted to 3pt level when asked explicitly — compensates partially for lesson gaps",
        "Custom quiz (/app/quiz) generated probability questions — some were appropriate 3pt level",
        "Arithmetic mastery progress visible in dashboard mastery panel — Hebrew concept names shown correctly",
        "Dashboard streak counter motivating — simple numbers, no language barrier"
      ],
      "red_flags": [
        "HIGH: Custom quiz cannot guarantee 3pt-only content because the underlying lesson/concept data doesn't have strict 3pt probability content. Some generated questions were above 3pt level.",
        "HIGH: 'word_problems' concept is in the 3pt learning plan but has no authored lesson and no seed lesson fallback — navigating to /app/lessons/l/word_problems returns 404 (notFound()).",
        "MEDIUM: The AI Tutor personalizes well in chat but there's no structured lesson to reinforce what was discussed — no handoff from agent conversation to a lesson exercise at the correct level.",
        "LOW: Some Hebrew in the probability lesson body_he_md at the base level uses terms like 'מרחב מדגם', 'מאורע', 'איחוד/חיתוך' — mathematically correct but heavy academic Hebrew for a non-native speaker without glossary tooltips."
      ],
      "would_continue": true
    },
    {
      "label": "Month 4",
      "narrative": "חודש 4. שיעורי חשבון, אלגברה, משוואות — כולם עשיתי. יש לי ציוני שליטה טובים על אלה. הדשבורד מראה לי שהנושאים האלה ירוקים. אבל הסתברות וסדרות — עדיין 40-50%. ניסיתי שוב שיעור סדרות. הפעם קצת יותר הבנתי (אחרי שהמורה בצ'אט לימד אותי). אבל הנוסחה $a_n = a_1 + (n-1)d$ — למדתי אותה מהצ'אט ולא מהשיעור. עבדתי עם 'המאמן' בצ'אט כדי לתרגל. הוא נתן לי תרגילים. אחד הכלל בעיות מילוליות — 'חנות מוכרת...' — הבנתי, אבל לפעמים הניסוח בעברית קצת מורכב. לא רע, אבל לא קל כמו בבית ספר. הייתי רוצה שיהיה לי משהו שעוזר לי לפרק בעיות מילוליות צעד אחר צעד.",
      "ux_score": 6,
      "stress_level": 6,
      "knowledge_scores": {
        "arithmetic": 8,
        "sequences_arithmetic": 5,
        "probability_basic": 4,
        "word_problems": 4,
        "equations_linear": 7,
        "equations_quadratic": 6,
        "functions_linear": 5
      },
      "green_lights": [
        "Mastery dashboard shows real progress — concept scores visible in Hebrew, motivating",
        "AI Coach drilling via chat is effective — adapts question difficulty based on answers",
        "Arithmetic, linear equations, quadratic equations: genuine improvement from lessons + chat",
        "Memory agents appear to retain context — Tutor recalls Mohammed's weak spots across sessions"
      ],
      "red_flags": [
        "HIGH: No structured 3pt lesson for sequences — student learned the formula purely via chat, with no reinforcing exercise bank at the correct level. Risk of gaps under exam pressure.",
        "HIGH: Probability still at 3pt-content level via chat only — no lesson to anchor understanding. Without a written worked example at the right level, student may forget under exam conditions.",
        "MEDIUM: Word problems require reading comprehension in academic Hebrew — no explicit word-problem decomposition skill in the lesson bank. AI Tutor helps but no repeatable structured practice.",
        "MEDIUM: No Arabic-language fallback at any point. Mohammed's parents and older siblings who could review content with him cannot engage with the platform at all — a support gap unique to this persona."
      ],
      "would_continue": true
    },
    {
      "label": "Month 8",
      "narrative": "חודש 8 — הבגרות בעוד חודשיים. רוב הנושאים עשיתי. בדשבורד רואים ששיעורי שליטה: חשבון 85%, משוואות 78%, אי-שוויונות 70%. הסתברות — 52%. סדרות — 55%. יש לי ספירת ימים בדשבורד שמראה 60 ימים לבגרות — מאוד מוטיבציה. אבל אני חרד מהסתברות. ידעתי שבבגרות 3 יחידות יש תמיד שאלה על הסתברות. פתחתי את השיעור שוב — ועדיין רואה תוכן של 4 יחידות. בסופו של דבר פניתי ל-ChatGPT להסברים פשוטים בהסתברות — כי שם כתבתי בערבית ובעברית פשוטה וקיבלתי תשובה. עכשיו מרגיש שיש פה מתחרה. אם האתר היה לי שיעור הסתברות ברמת 3 יחידות — הייתי נשאר פה. אבל עבור ההסתברות — עברתי לChatGPT.",
      "ux_score": 6,
      "stress_level": 8,
      "knowledge_scores": {
        "arithmetic": 8,
        "sequences_arithmetic": 6,
        "probability_basic": 5,
        "word_problems": 5,
        "equations_linear": 8,
        "equations_quadratic": 7,
        "functions_linear": 6,
        "functions_quadratic": 5
      },
      "green_lights": [
        "Bagrut countdown in dashboard (60 days left) — 'מחצית הדרך. כדאי להתעמד על הנושאים החלשים' — exactly right message, motivating and simple Hebrew",
        "Arithmetic, algebra, equations: solid improvement — platform delivered real value here",
        "AI Tutor memory of past sessions enables continuity across 8 months",
        "Quiz tool helped with drilling — though some q's above level"
      ],
      "red_flags": [
        "CRITICAL: Student is actively using ChatGPT for probability because ASF has no 3pt lesson content for it. This is a retention/churn event for a core exam topic.",
        "HIGH: Final Bagrut readiness for probability is approximately 50% — the platform's biggest coverage gap coincides with one of Mohammed's identified weak areas AND a guaranteed Bagrut topic.",
        "HIGH: sequences_arithmetic mastery at 55% — still below the 70% threshold. Sequences is also a 3pt Bagrut topic (legacy questionnaire 802). Gap unresolved after 8 months.",
        "MEDIUM: Word problems — no dedicated lesson across 8 months. Improvement came only from AI chat practice."
      ],
      "would_continue": false
    }
  ],
  "rubric_scores": {
    "learning_improvement_progress": {
      "weight": 0.20,
      "score": 5.5,
      "rationale": "Strong improvement in arithmetic, linear/quadratic equations (8/10). Sequences and probability remained weak despite 8 months — only chat-based learning, no structured 3pt lessons. Word problems improved marginally. Arithmetic success is real but insufficient for full Bagrut coverage."
    },
    "material_coverage_3pt": {
      "weight": 0.20,
      "score": 5.0,
      "rationale": "3pt onboarding scoping is correct (17 relevant concepts identified). BUT probability_basic and sequences_arithmetic authored lessons are tagged math_track 4pt/5pt only — 2 of Mohammed's 3 weak areas have NO 3pt-adapted lesson content. word_problems has no lesson at all. Only ~12 of 17 3pt concepts have lesson coverage."
    },
    "language_fit": {
      "weight": 0.15,
      "score": 5.5,
      "rationale": "Onboarding Hebrew is clear and accessible (8/10). Dashboard motivational text is well-written for a non-native (7/10). BUT: lesson page primary H1 is English; 'Back to lessons' hardcoded English; gender-inclusive forms (את/ה) add visual noise; some 3pt body_he_md sections are truncated mid-sentence; several 4pt body_he_md fields contain English text. No Arabic support for family assistance."
    },
    "retention": {
      "weight": 0.10,
      "score": 6.0,
      "rationale": "Streak tracking, mastery scores, NextLessonCard work well. AI memory agents retain context across sessions. But retention loops for sequences and probability are broken — no lesson anchors the chat-learned content, increasing forgetting risk under exam conditions."
    },
    "accessibility": {
      "weight": 0.10,
      "score": 6.0,
      "rationale": "RTL layout implemented correctly. Progress bars have aria-labels. Hebrew UI is mostly clear. But no Arabic language option (significant for this persona), 'Back to lessons' is English, lesson H1 is English-primary, lesson meta (duration, subject) always in English. Some body_he_md truncations render as incomplete sentences — broken reading experience."
    },
    "uniqueness_vs_chatgpt": {
      "weight": 0.10,
      "score": 5.5,
      "rationale": "Bagrut countdown, personalized learning plan, 3pt scoping, and AI Tutor memory are unique differentiators. However, Mohammed explicitly switched to ChatGPT for probability because ASF had no appropriate 3pt content. The platform's structural lesson gap undermines its uniqueness advantage for this student's highest-priority gap."
    },
    "bagrut_success_likelihood": {
      "weight": 0.15,
      "score": 4.5,
      "rationale": "Arithmetic and equations improvement is genuine — student would score well on those sections. But probability (guaranteed topic) and sequences (in legacy 802 questionnaire) remain at ~50-55% mastery with no 3pt lesson reinforcement. Word problem reading is only partially improved. Estimated Bagrut outcome: 55-62 range — passes but barely. Platform did not close the most important gaps."
    }
  },
  "weighted_final_score": 5.38,
  "final_satisfaction": 5,
  "final_knowledge_gain": "fair",
  "summary": "The platform successfully onboarded Mohammed in Hebrew and delivered real improvement in arithmetic, linear equations, and quadratic equations. However, two of his three identified weak areas — probability and sequences — have no authored 3pt-level lesson content (lessons are tagged 4pt/5pt only), forcing him to rely solely on AI chat for these topics and ultimately defecting to ChatGPT for probability. The lesson page also shows an English primary heading regardless of locale, and 'Back to lessons' is hardcoded English — small but jarring breaks for a non-native Hebrew speaker. Fixing the 3pt lesson content for probability_basic and sequences_arithmetic is the single highest-impact change that would retain this student and meaningfully improve his Bagrut outcome.",
  "issues": [
    {
      "id": "ISS-01",
      "category": "content",
      "severity": "critical",
      "description": "probability_basic.json and sequences_arithmetic.json are tagged math_track: ['4pt', '5pt']. There is no 3pt body_by_level variant in either lesson. A 3pt student receives 4pt-level content or the base (un-differentiated) content which still references conditional probability and Bayes' formula — outside the 3pt Bagrut syllabus.",
      "root_cause": "Lesson JSON files were seeded without 3pt variant bodies for these concepts, and the math_track field excludes '3pt'. The onboarding correctly identifies both as 3pt concepts but no lesson delivers them at the right level.",
      "suggested_fix": "Add body_by_level['3pt'] variants to probability_basic.json and sequences_arithmetic.json following the 3pt curriculum spec (uniform probability, sample spaces, basic event math for probability; arithmetic sequence formula and sum formula for sequences — no proofs). Update math_track to include '3pt'. Target: 10–15 questions at 3pt difficulty for each.",
      "affects_students": ["3pt"]
    },
    {
      "id": "ISS-02",
      "category": "content",
      "severity": "critical",
      "description": "No authored lesson exists for the 'word_problems' concept. It is listed as a 3pt concept in the onboarding and curriculum, but /app/lessons/l/word_problems returns notFound(). This concept is Mohammed's primary weak area and a recurring component of every 3pt Bagrut questionnaire.",
      "root_cause": "The word_problems lesson was never seeded. The concept exists in the KG and onboarding concept list but no seed JSON or DB entry exists.",
      "suggested_fix": "Author a word_problems.json lesson with 3pt-appropriate sections covering: parsing math from Hebrew sentence structure, setting up linear/quadratic equations from word problems, rate/mixture/age problems. Add 8–10 graded questions with Hebrew stems. Tag math_track: ['3pt', '4pt', '5pt'].",
      "affects_students": ["3pt", "4pt", "5pt"]
    },
    {
      "id": "ISS-03",
      "category": "bilingual",
      "severity": "high",
      "description": "Lesson page primary <h1> displays title_en regardless of user locale. Hebrew title is shown in a secondary <p> tag with text-muted-foreground styling. For a Hebrew-interface student, this inverts the expected language hierarchy and creates immediate disorientation.",
      "root_cause": "In apps/web/src/app/(app)/app/lessons/l/[lessonId]/page.tsx line 69: <h1>{lesson.title_en}</h1> is hardcoded. locale is not read from useI18n() at the server component level.",
      "suggested_fix": "In the server component, read the locale cookie (or pass as a param). If locale is 'he' and title_he exists, make title_he the primary H1 and title_en the secondary subheading (or omit it). Alternatively: render both equally but show title_he first when locale is 'he'.",
      "affects_students": ["3pt", "4pt", "5pt", "physics", "university"]
    },
    {
      "id": "ISS-04",
      "category": "bilingual",
      "severity": "high",
      "description": "'Back to lessons' navigation link on the lesson page (apps/web/src/app/(app)/app/lessons/l/[lessonId]/page.tsx line 62) is hardcoded English and never localized. All other navigation is in Hebrew when locale is 'he'.",
      "root_cause": "The ArrowLeft + 'Back to lessons' link was not included in any i18n string map. This page lacks useI18n() at the server render level.",
      "suggested_fix": "Add a bilingual string map to the lesson page: { he: 'חזרה לשיעורים', en: 'Back to lessons' }. Pass locale through search params or cookie, and render the appropriate string.",
      "affects_students": ["3pt", "4pt", "5pt", "physics", "university"]
    },
    {
      "id": "ISS-05",
      "category": "content",
      "severity": "high",
      "description": "Multiple body_by_level[level].body_he_md fields in seeded lessons contain English text instead of Hebrew. Examples: arithmetic.json intro 4pt body_he_md starts 'Arithmetic is the foundation of mathematics...'; sequences_arithmetic.json theory 4pt body_he_md starts 'In this section, we will explore...' These fields are labeled as Hebrew but deliver English content.",
      "root_cause": "Seed generation likely copied body_en_md into body_he_md for non-base level variants without translating. Quality check on Hebrew field content was not enforced.",
      "suggested_fix": "Audit all lesson JSON files: for every body_by_level[level].body_he_md field, verify it contains Hebrew. Add a CI lint step that flags any body_he_md field containing >40% ASCII-only text as a build warning. Translate or remove the affected sections.",
      "affects_students": ["3pt", "4pt", "5pt"]
    },
    {
      "id": "ISS-06",
      "category": "content",
      "severity": "high",
      "description": "Several 3pt body_by_level['3pt'].body_he_md sections in arithmetic.json are truncated mid-word/mid-sentence. Examples: pitfall section 3pt body_he_md ends '...ראשית, נבצע את החיל' (truncated mid-word); theory 3pt body_he_md ends '...נבצע את החיסור בין' — incomplete. Student reads a broken explanation.",
      "root_cause": "Seed generation hit a token or character limit and the content was truncated without detection. No validation of Hebrew text completeness was performed.",
      "suggested_fix": "Add a JSON validation step in the lesson seeding pipeline: check that all body_he_md strings end with a sentence-final character (period, punctuation, or closing math delimiter). Flag and regenerate any truncated sections. Fix arithmetic.json pitfall and theory 3pt sections immediately.",
      "affects_students": ["3pt"]
    },
    {
      "id": "ISS-07",
      "category": "bilingual",
      "severity": "medium",
      "description": "Lesson page meta-info ('12 min · math') is always in English regardless of locale. 'math' should show 'מתמטיקה' in Hebrew mode.",
      "root_cause": "The subject field in lesson data stores lowercase English slugs ('math', 'physics'). The lesson page server component does not translate these to Hebrew.",
      "suggested_fix": "Add a SUBJECT_LABELS map in the lesson page (matching the one already in quiz/page.tsx) and use it to localize the subject string when locale is 'he'.",
      "affects_students": ["3pt", "4pt", "5pt", "physics"]
    },
    {
      "id": "ISS-08",
      "category": "accessibility",
      "severity": "medium",
      "description": "No Arabic language option exists. Arabic-speaking families (Mohammed's parents, siblings) cannot engage with the platform at all. This is relevant for COPPA-adjacent family engagement and for first-generation students who rely on family support.",
      "root_cause": "The i18n provider only supports 'en' and 'he' locales. Arabic RTL direction is not configured.",
      "suggested_fix": "Short-term: add a note in onboarding acknowledging the platform is in Hebrew/English. Long-term: add Arabic as a third locale for core navigation strings and onboarding — full Arabic content translation is complex but even partial support (labels, navigation) would help significantly for this student population.",
      "affects_students": ["3pt", "4pt"]
    },
    {
      "id": "ISS-09",
      "category": "ux",
      "severity": "medium",
      "description": "Gender-inclusive Hebrew orthography ('את/ה לומד/ת', 'מרגיש/ה', 'יכול/ה') appears throughout onboarding. While inclusively correct, this pattern creates visual noise for non-native Hebrew readers who are accustomed to gender-separate forms and read the slash as a separator character or typo.",
      "root_cause": "The STR map in onboarding/page.tsx uses gender-inclusive forms as a stylistic choice. No alternative rendering for non-native speakers exists.",
      "suggested_fix": "Consider defaulting to masculine forms in the onboarding labels (Israeli school standard) or using gender-neutral phrasing where possible. Alternatively, detect Hebrew proficiency from the onboarding and simplify forms. At minimum, document this as a known legibility tradeoff.",
      "affects_students": ["3pt", "4pt"]
    },
    {
      "id": "ISS-10",
      "category": "missing_feature",
      "severity": "medium",
      "description": "No structured word-problem decomposition scaffold exists anywhere in the platform. Word problems require a specific reading strategy (identify unknowns → write equation → solve) that is particularly hard for non-native Hebrew speakers. This skill is missing from lesson content AND from coach/tutor agent hints.",
      "root_cause": "The agent_hints in word_problems concept are empty (concept exists in KG but lesson doesn't exist). No skill atom maps 'Hebrew word problem parsing' to any lesson.",
      "suggested_fix": "Author a word_problems lesson with a 3-step decomposition framework. Add a 'word_problem_reading_strategy' skill atom. Wire the Tutor's agent_hints to this atom so it proactively offers the framework when a student struggles with a word problem containing keywords like 'אם', 'כמה', 'מחיר'.",
      "affects_students": ["3pt", "4pt", "5pt"]
    }
  ]
}
```

---

## Rubric Score Summary

| Dimension | Weight | Score (0–10) | Weighted |
|-----------|--------|--------------|----------|
| Learning improvement / progress | 20% | 5.5 | 1.10 |
| Material coverage — 3pt topics | 20% | 5.0 | 1.00 |
| Language fit (Hebrew simplicity) | 15% | 5.5 | 0.83 |
| Retention | 10% | 6.0 | 0.60 |
| Accessibility | 10% | 6.0 | 0.60 |
| Uniqueness vs ChatGPT | 10% | 5.5 | 0.55 |
| Bagrut success likelihood | 15% | 4.5 | 0.68 |
| **TOTAL** | **100%** | — | **5.36 / 10** |

---

## Top 3 Recommendations (Priority Order)

### 1. Add 3pt lesson content for `probability_basic` and `sequences_arithmetic` (ISS-01)
**Impact: CRITICAL.** These are guaranteed Bagrut topics at 3pt level AND Mohammed's two most prominent weak areas. Without 3pt-adapted lesson bodies + question banks, the platform cannot close these gaps no matter how good the AI chat is. This is the single change with the highest marginal Bagrut outcome improvement for the entire 3pt student population.

### 2. Fix lesson page locale (English H1, 'Back to lessons') (ISS-03, ISS-04)  
**Impact: HIGH.** The lesson page is the most-visited page after the dashboard. Every session, Mohammed sees an English primary heading. This creates a persistent sense of "this platform is for English speakers" — directly undermining trust for the target student. A 10-line fix.

### 3. Author a `word_problems` lesson with Hebrew reading scaffold (ISS-02, ISS-10)
**Impact: HIGH.** Word problems are the cross-cutting skill that every 3pt, 4pt, and 5pt student needs. For Arabic-speaking students, parsing academic Hebrew sentences under exam time pressure is a distinct skill gap. A structured lesson with explicit Hebrew-sentence-to-equation mapping would differentiate ASF from generic AI tutors.

---

## Verdict
**5.36 / 10 — BELOW THRESHOLD (8.5)**  
Mohammed received genuine value in arithmetic and core algebra, but the platform failed him on his three self-identified weak areas. Two of those (probability, sequences) have no 3pt content, and one (word problems) has no lesson at all. He churned to ChatGPT for probability in month 8 — a clear retention failure on a critical exam topic. The Hebrew language experience in onboarding and dashboard is solid; the lesson page undermines it. With the three priority fixes, this score would rise to approximately 7.5–8.0.
