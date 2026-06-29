"""
Generate 3 Bagrut biology seed lessons for A Step Forward platform.
Run from project root: python gen_bio_lessons.py
"""
import json, os

LESSONS_DIR = "scripts/seed_data/lessons"

# ─── 1. cell_structure ───────────────────────────────────────────────────────

cell_structure = {
    "concept_id": "cell_structure",
    "subject": "biology",
    "level": "high_school",
    "math_track": ["biology_4pt"],
    "title_en": "The Cell — Structure and Organelles",
    "title_he": "התא — מבנה ואברונים",
    "summary_en": "Every living organism is built from cells. This lesson covers key organelles of eukaryotic cells, their functions, and the structural differences between plant and animal cells — core knowledge for the Bagrut biology exam.",
    "summary_he": "כל יצור חי בנוי מתאים. שיעור זה עוסק באברונים המרכזיים של תאים אאוקריוטיים, תפקידיהם, וההבדלים המבניים בין תאי צמח לתאי בעל-חיים.",
    "est_minutes": 22,
    "sections": [
        {
            "kind": "intro",
            "title_en": "What is a cell?",
            "title_he": "מה הוא תא?",
            "body_en_md": (
                "The **cell** (Hebrew: תא, *ta*) is the basic structural and functional unit of all living organisms.\n\n"
                "Two major categories:\n\n"
                "| Feature | Prokaryotic (e.g. bacteria) | Eukaryotic (animals, plants) |\n"
                "|---|---|---|\n"
                "| Nucleus | No — DNA free in cytoplasm | Yes — membrane-bound **nucleus** (גרעין) |\n"
                "| Size | ~1–10 µm | ~10–100 µm |\n"
                "| Organelles | Minimal | Many, membrane-bound |\n\n"
                "Bagrut biology questions focus almost entirely on **eukaryotic cells** and their organelles."
            ),
            "body_he_md": (
                "**תא** הוא היחידה המבנית והתפקודית הבסיסית של כל יצורי החיים.\n\n"
                "שתי קטגוריות עיקריות:\n\n"
                "| מאפיין | פרוקריוטי (כגון חיידק) | אאוקריוטי (בעלי-חיים, צמחים) |\n"
                "|---|---|---|\n"
                "| גרעין | אין — DNA חופשי בציטופלזמה | יש — מוקף ממברנה |\n"
                "| גודל | כ-1–10 מיקרומטר | כ-10–100 מיקרומטר |\n"
                "| אברונים | מינימלי | רבים, מוקפי ממברנה |\n\n"
                "שאלות בגרות עוסקות כמעט תמיד ב**תאים אאוקריוטיים** ואברוניהם."
            )
        },
        {
            "kind": "theory",
            "title_en": "Key organelles and their functions",
            "title_he": "אברונים מרכזיים ותפקידיהם",
            "body_en_md": (
                "**Nucleus (גרעין):** Control center. Contains DNA in chromosomes. Surrounded by nuclear envelope "
                "(double membrane with pores). Directs protein synthesis and cell division.\n\n"
                "**Cell membrane (ממברנת התא):** Phospholipid bilayer. Selectively permeable barrier "
                "controlling what enters and exits.\n\n"
                "**Mitochondria (מיטוכונדריה):** Powerhouse of the cell. Perform **cellular respiration**:\n"
                "$$C_6H_{12}O_6 + 6O_2 \\rightarrow 6CO_2 + 6H_2O + ATP$$\n"
                "Inner membrane folded into **cristae** to maximize surface area.\n\n"
                "**Ribosomes (ריבוזומים):** Synthesize proteins. Free in cytoplasm or attached to rough ER.\n\n"
                "**Rough ER:** Ribosomes attached; makes secretory and membrane proteins.\n\n"
                "**Smooth ER:** No ribosomes; synthesizes lipids, detoxifies substances.\n\n"
                "**Golgi apparatus (מנגנון גולג'י):** Modifies, packages, and ships proteins. Produces secretory vesicles.\n\n"
                "**Lysosomes (ליזוזומים):** Contain digestive enzymes; break down waste, debris, and pathogens."
            ),
            "body_he_md": (
                "**גרעין (Nucleus):** מרכז הבקרה. מכיל DNA בכרומוזומים. מוקף במעטפת גרעין (ממברנה כפולה עם נקבוביות). "
                "מכוון סינתזת חלבונים וחלוקת תא.\n\n"
                "**ממברנת התא:** שכבה כפולה של פוספוליפידים. חדירות בררנית — שולטת במה שנכנס ויוצא.\n\n"
                "**מיטוכונדריה (Mitochondria):** תחנות הכוח של התא. מבצעות **נשימה תאית**:\n"
                "$$C_6H_{12}O_6 + 6O_2 \\rightarrow 6CO_2 + 6H_2O + ATP$$\n"
                "הממברנה הפנימית מקופלת ל**קריסטות** להגדלת שטח הפנים.\n\n"
                "**ריבוזומים (Ribosomes):** מסנתזים חלבונים. חופשיים בציטופלזמה או מחוברים ל-ER הגס.\n\n"
                "**ER גס:** עם ריבוזומים; מייצר חלבוני הפרשה וממברנה.\n\n"
                "**ER חלק:** ללא ריבוזומים; מסנתז שומנים, מפרק רעלים.\n\n"
                "**מנגנון גולג'י:** משנה, אורז ומשלח חלבונים. מייצר שלפוחיות הפרשה.\n\n"
                "**ליזוזומים (Lysosomes):** מכילים אנזימי עיכול; מפרקים פסולת, שאריות תאיות ופתוגנים."
            )
        },
        {
            "kind": "theory",
            "title_en": "Plant cells vs. animal cells",
            "title_he": "תאי צמח לעומת תאי בעל-חיים",
            "body_en_md": (
                "Both are eukaryotic, but differ in three key structures:\n\n"
                "| Structure | Animal cell | Plant cell |\n"
                "|---|---|---|\n"
                "| **Cell wall (דופן תא)** | No | Yes (cellulose; outside membrane) |\n"
                "| **Chloroplasts (כלורופלסטים)** | No | Yes (site of photosynthesis) |\n"
                "| **Large central vacuole** | Small/absent | Yes (up to 90% of cell volume; maintains turgor) |\n\n"
                "> **Exam tip:** On Bagrut diagrams, identify plant vs. animal cells by cell wall, chloroplasts, or large central vacuole."
            ),
            "body_he_md": (
                "שתיהן אאוקריוטיות, אך שונות בשלושה מבנים מרכזיים:\n\n"
                "| מבנה | תא בעל-חיים | תא צמח |\n"
                "|---|---|---|\n"
                "| **דופן תא** | אין | יש (תאית; מחוץ לממברנה) |\n"
                "| **כלורופלסטים** | אין | יש (אתר הפוטוסינתזה) |\n"
                "| **ווקואולה מרכזית גדולה** | קטנה/אין | יש (עד 90% מנפח התא; לחץ טורגור) |\n\n"
                "> **טיפ לבגרות:** בדיאגרמות בגרות, זהה תאי צמח לפי דופן תא, כלורופלסטים, או ווקואולה מרכזית גדולה."
            )
        },
        {
            "kind": "worked_example",
            "title_en": "Worked example: organelle damage scenarios",
            "title_he": "דוגמה פתורה: תרחישי נזק לאברונים",
            "body_en_md": (
                "**Scenario 1:** A cell cannot produce sufficient ATP. Which organelle is damaged, "
                "and which structural feature normally maximizes energy output?\n\n"
                "**Answer:** The **mitochondria** are damaged. ATP is produced by cellular respiration occurring "
                "in the mitochondria. Their inner membrane is folded into **cristae**, maximizing surface area for "
                "the electron transport chain enzymes that synthesize ATP.\n\n"
                "---\n\n"
                "**Scenario 2:** A cell cannot secrete hormones after synthesis. Ribosomes are intact. "
                "Which organelle is most likely damaged?\n\n"
                "**Answer:** The **Golgi apparatus** — it receives proteins from the ER, modifies and packages them "
                "into vesicles, and ships them for secretion. Without it, proteins cannot exit the cell."
            ),
            "body_he_md": (
                "**תרחיש 1:** תא אינו יכול לייצר ATP מספיק. איזה אברון ניזוק, "
                "ואיזה מאפיין מבני מגדיל בדרך כלל את ייצור האנרגיה?\n\n"
                "**תשובה:** **המיטוכונדריה** ניזוקו. ATP מיוצר בנשימה תאית המתרחשת במיטוכונדריה. "
                "הממברנה הפנימית מקופלת ל**קריסטות**, המגדילות את שטח הפנים לאנזימי שרשרת "
                "ההעברה האלקטרונית שמסנתזים ATP.\n\n"
                "---\n\n"
                "**תרחיש 2:** תא אינו יכול להפריש הורמונים לאחר סינתזתם. הריבוזומים תקינים. "
                "איזה אברון ניזוק ככל הנראה?\n\n"
                "**תשובה:** **מנגנון גולג'י** — הוא מקבל חלבונים מה-ER, משנה ואורז אותם "
                "בשלפוחיות, ומשלח אותם להפרשה. בלעדיו, חלבונים אינם יכולים לצאת מהתא."
            )
        },
        {
            "kind": "summary",
            "title_en": "Key take-aways",
            "title_he": "עיקרי השיעור",
            "body_en_md": (
                "- **Cell (תא)** = basic unit of life; prokaryotes lack a nucleus; eukaryotes have a membrane-bound **nucleus (גרעין)**.\n"
                "- **Mitochondria (מיטוכונדריה)** = ATP via cellular respiration; cristae maximize surface area.\n"
                "- **Ribosomes (ריבוזומים)** = protein synthesis.\n"
                "- **Golgi apparatus (מנגנון גולג'י)** = modify, package, and ship proteins.\n"
                "- **Plant cell unique features:** cell wall (דופן תא), chloroplasts (כלורופלסטים), large central vacuole."
            ),
            "body_he_md": (
                "- **תא** = יחידת החיים הבסיסית; פרוקריוטים חסרי גרעין; אאוקריוטים מכילים **גרעין** מוקף ממברנה.\n"
                "- **מיטוכונדריה** = ATP בנשימה תאית; קריסטות מגדילות שטח פנים.\n"
                "- **ריבוזומים** = סינתזת חלבונים.\n"
                "- **מנגנון גולג'י** = שינוי, אריזה ומשלוח חלבונים.\n"
                "- **ייחודי לתא צמח:** דופן תא, כלורופלסטים, ווקואולה מרכזית גדולה."
            )
        }
    ],
    "questions": [
        {
            "ord": 1, "kind": "mcq", "difficulty": "easy",
            "stem_en": "Which organelle is responsible for producing ATP through cellular respiration?",
            "stem_he": "איזה אברון אחראי לייצור ATP באמצעות נשימה תאית?",
            "options_en": ["Nucleus", "Ribosome", "Mitochondria", "Golgi apparatus"],
            "options_he": ["גרעין", "ריבוזום", "מיטוכונדריה", "מנגנון גולג'י"],
            "correct_index": 2,
            "explanation_en": "Mitochondria perform cellular respiration, converting glucose and oxygen into ATP — the cell's usable energy currency.",
            "explanation_he": "המיטוכונדריה מבצעות נשימה תאית, המרת גלוקוז וחמצן ל-ATP — מטבע האנרגיה השמיש של התא.",
            "skill_atoms": ["identify_organelle_function"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 2, "kind": "mcq", "difficulty": "easy",
            "stem_en": "Which structure is found in plant cells but NOT in animal cells?",
            "stem_he": "איזה מבנה קיים בתאי צמח אך לא בתאי בעל-חיים?",
            "options_en": ["Mitochondria", "Cell membrane", "Ribosome", "Cell wall"],
            "options_he": ["מיטוכונדריה", "ממברנת תא", "ריבוזום", "דופן תא"],
            "correct_index": 3,
            "explanation_en": "The cell wall (cellulose) is unique to plant cells. Mitochondria, cell membrane, and ribosomes are found in both.",
            "explanation_he": "דופן התא (תאית) ייחודי לתאי צמח. מיטוכונדריה, ממברנת תא וריבוזומים קיימים בשניהם.",
            "skill_atoms": ["plant_vs_animal_cell"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 3, "kind": "mcq", "difficulty": "medium",
            "stem_en": "A student observes a cell with a large central vacuole and a cell wall. What type of cell is this?",
            "stem_he": "תלמיד רואה תא עם ווקואולה מרכזית גדולה ודופן תא. מהו סוג התא?",
            "options_en": ["Prokaryotic cell", "Animal cell", "Plant cell", "Bacterial cell"],
            "options_he": ["תא פרוקריוטי", "תא בעל-חיים", "תא צמח", "תא חיידק"],
            "correct_index": 2,
            "explanation_en": "Large central vacuole + cell wall together are hallmarks of plant cells. Animal cells have neither; bacteria have walls but no large vacuole.",
            "explanation_he": "ווקואולה מרכזית גדולה + דופן תא = סימני היכר של תאי צמח. לבעלי-חיים אין שניהם; לחיידקים יש דופן אך לא ווקואולה גדולה.",
            "skill_atoms": ["plant_vs_animal_cell"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 4, "kind": "mcq", "difficulty": "medium",
            "stem_en": "What is the primary function of the Golgi apparatus?",
            "stem_he": "מה תפקידו העיקרי של מנגנון גולג'י?",
            "options_en": ["Synthesizing DNA", "Producing ATP", "Modifying and packaging proteins for secretion", "Cellular digestion of waste"],
            "options_he": ["סינתוז DNA", "ייצור ATP", "שינוי ואריזת חלבונים להפרשה", "עיכול פסולת תאי"],
            "correct_index": 2,
            "explanation_en": "The Golgi receives proteins from the ER, modifies them (e.g. adds sugar chains), packages them into vesicles, and ships them to their destination.",
            "explanation_he": "גולג'י מקבל חלבונים מה-ER, משנה אותם (למשל מוסיף שרשראות סוכר), אורז לשלפוחיות ומשלח ליעדם.",
            "skill_atoms": ["identify_organelle_function"], "points_level_min": "biology_4pt"
        }
    ],
    "agent_hints": (
        "Foundational biology lesson for Bagrut 4pt. Key exam patterns: (1) organelle labeling diagrams — "
        "students must identify each organelle and state its function; (2) plant vs. animal cell comparison "
        "tables; (3) match-damage-to-organelle reasoning. Most common mistake: confusing cell wall (unique to "
        "plant cells) with cell membrane (found in all cells). "
        "Biology Hebrew terms: תא=cell, גרעין=nucleus, מיטוכונדריה=mitochondria, ריבוזום=ribosome, "
        "כלורופלסט=chloroplast, דופן תא=cell wall, ממברנת תא=cell membrane."
    ),
    "skill_atoms": [
        {"id": "identify_organelle_function", "description_en": "Match each organelle to its primary function", "description_he": "התאמת כל אברון לתפקידו העיקרי"},
        {"id": "plant_vs_animal_cell", "description_en": "Distinguish plant from animal cells by structural features", "description_he": "הבחנה בין תאי צמח לתאי בעל-חיים לפי מאפיינים מבניים"},
        {"id": "prokaryote_vs_eukaryote", "description_en": "Distinguish prokaryotic from eukaryotic cells", "description_he": "הבחנה בין תאים פרוקריוטיים לאאוקריוטיים"}
    ]
}

# ─── 2. heredity_mendelian ───────────────────────────────────────────────────

heredity_mendelian = {
    "concept_id": "heredity_mendelian",
    "subject": "biology",
    "level": "high_school",
    "math_track": ["biology_4pt"],
    "title_en": "Mendelian Genetics — Dominant and Recessive Traits",
    "title_he": "גנטיקה מנדלית — תכונות דומיננטיות ורצסיביות",
    "summary_en": "Gregor Mendel discovered that traits are inherited as discrete units (genes). This lesson covers alleles, dominant/recessive inheritance, Punnett squares, and genotype vs. phenotype — essential for Bagrut genetics questions.",
    "summary_he": "גרגור מנדל גילה כי תכונות עוברות בירושה כיחידות נפרדות (גנים). שיעור זה עוסק באללים, ירושה דומיננטית/רצסיבית, ריבועי פאנט, וגנוטיפ לעומת פנוטיפ — חיוני לשאלות גנטיקה בבגרות.",
    "est_minutes": 24,
    "sections": [
        {
            "kind": "intro",
            "title_en": "From parents to offspring: the concept of inheritance",
            "title_he": "מהורים לצאצאים: מושג הירושה",
            "body_en_md": (
                "Why do children resemble their parents — but not perfectly? The answer lies in **genes**.\n\n"
                "Gregor Mendel (1865) crossed pea plants and found that traits are inherited in predictable **ratios**. "
                "His two laws:\n\n"
                "1. **Law of Segregation:** Each organism has two copies of each gene (alleles). "
                "During reproduction, each parent passes ONE allele to the offspring at random.\n"
                "2. **Law of Independent Assortment:** Alleles of different genes are inherited independently "
                "(for genes on different chromosomes).\n\n"
                "Key vocabulary:\n"
                "- **Gene (גן):** a DNA sequence encoding a trait.\n"
                "- **Allele (אלל):** one version of a gene (e.g. B or b).\n"
                "- **Dominant (דומיננטי):** allele that masks the other when present; written as capital letter (B).\n"
                "- **Recessive (רצסיבי):** allele that is masked by the dominant; written as lowercase (b).\n"
                "- **Genotype (גנוטיפ):** the genetic makeup (e.g. BB, Bb, bb).\n"
                "- **Phenotype (פנוטיפ):** the observable trait (e.g. brown eyes).\n"
                "- **Homozygous (הומוזיגוט):** two identical alleles (BB or bb).\n"
                "- **Heterozygous (הטרוזיגוט):** two different alleles (Bb)."
            ),
            "body_he_md": (
                "מדוע ילדים דומים להוריהם — אך לא בצורה מושלמת? התשובה טמונה ב**גנים**.\n\n"
                "גרגור מנדל (1865) הצליב צמחי אפונה ומצא כי תכונות עוברות בירושה ביחסים צפויים. שני חוקיו:\n\n"
                "1. **חוק ההפרדה:** לכל יצור שני עותקים של כל גן (אללים). "
                "בהתרבות, כל הורה מעביר אלל **אחד** לצאצא באקראי.\n"
                "2. **חוק האסורטמנט העצמאי:** אללים של גנים שונים עוברים בירושה בצורה עצמאית "
                "(לגנים על כרומוזומים שונים).\n\n"
                "אוצר מילים מרכזי:\n"
                "- **גן:** רצף DNA המקודד תכונה.\n"
                "- **אלל:** גרסה אחת של גן (למשל B או b).\n"
                "- **דומיננטי:** אלל המסתיר את האחר כשנוכח; נכתב באות גדולה (B).\n"
                "- **רצסיבי:** אלל המוסתר על-ידי הדומיננטי; נכתב באות קטנה (b).\n"
                "- **גנוטיפ:** ההרכב הגנטי (למשל BB, Bb, bb).\n"
                "- **פנוטיפ:** התכונה הנצפית (למשל עיניים חומות).\n"
                "- **הומוזיגוט:** שני אללים זהים (BB או bb).\n"
                "- **הטרוזיגוט:** שני אללים שונים (Bb)."
            )
        },
        {
            "kind": "theory",
            "title_en": "Dominant and recessive: who wins?",
            "title_he": "דומיננטי ורצסיבי: מי מנצח?",
            "body_en_md": (
                "### The dominance rule\n\n"
                "When an organism has two different alleles for a gene (heterozygous, Bb), only the **dominant** allele "
                "is expressed in the phenotype. The recessive allele is **hidden** but still present.\n\n"
                "| Genotype | Phenotype | Description |\n"
                "|---|---|---|\n"
                "| BB | Dominant trait | Homozygous dominant |\n"
                "| Bb | Dominant trait | Heterozygous (carrier) |\n"
                "| bb | Recessive trait | Homozygous recessive |\n\n"
                "**Example:** Brown eye color (B) is dominant over blue (b).\n"
                "- BB → brown eyes\n"
                "- Bb → brown eyes (carries blue allele)\n"
                "- bb → blue eyes\n\n"
                "### Punnett square (ריבוע פאנט)\n\n"
                "A Punnett square predicts the probability of offspring genotypes from two parents.\n\n"
                "**Example:** Cross Bb × Bb\n\n"
                "```\n"
                "      B    b\n"
                "  B [ BB ] [ Bb ]\n"
                "  b [ Bb ] [ bb ]\n"
                "```\n\n"
                "Results: 1 BB : 2 Bb : 1 bb → **3 dominant : 1 recessive** phenotype ratio."
            ),
            "body_he_md": (
                "### כלל הדומיננטיות\n\n"
                "כאשר ליצור יש שני אללים שונים לגן (הטרוזיגוט, Bb), רק האלל **הדומיננטי** מתבטא בפנוטיפ. "
                "האלל הרצסיבי **נסתר** אך עדיין קיים.\n\n"
                "| גנוטיפ | פנוטיפ | תיאור |\n"
                "|---|---|---|\n"
                "| BB | תכונה דומיננטית | הומוזיגוט דומיננטי |\n"
                "| Bb | תכונה דומיננטית | הטרוזיגוט (נשא) |\n"
                "| bb | תכונה רצסיבית | הומוזיגוט רצסיבי |\n\n"
                "**דוגמה:** צבע עיניים חום (B) דומיננטי על כחול (b).\n"
                "- BB → עיניים חומות\n"
                "- Bb → עיניים חומות (נושא אלל כחול)\n"
                "- bb → עיניים כחולות\n\n"
                "### ריבוע פאנט (Punnett square)\n\n"
                "ריבוע פאנט מנבא את הסבירות לגנוטיפים של צאצאים משני הורים.\n\n"
                "**דוגמה:** הצלבה Bb × Bb\n\n"
                "```\n"
                "      B    b\n"
                "  B [ BB ] [ Bb ]\n"
                "  b [ Bb ] [ bb ]\n"
                "```\n\n"
                "תוצאות: 1 BB : 2 Bb : 1 bb → יחס פנוטיפי **3 דומיננטי : 1 רצסיבי**."
            )
        },
        {
            "kind": "worked_example",
            "title_en": "Worked example: Punnett square crosses",
            "title_he": "דוגמה פתורה: הצלבות בריבוע פאנט",
            "body_en_md": (
                "**Problem:** Flower color in peas: purple (P) is dominant over white (p). "
                "Cross a heterozygous purple plant (Pp) with a white plant (pp). "
                "What fraction of offspring will have purple flowers?\n\n"
                "**Step 1 — Write the cross:** Pp × pp\n\n"
                "**Step 2 — Fill the Punnett square:**\n\n"
                "```\n"
                "      P    p\n"
                "  p [ Pp ] [ pp ]\n"
                "  p [ Pp ] [ pp ]\n"
                "```\n\n"
                "**Step 3 — Read the results:**\n"
                "- Pp : pp = 2 : 2 = **1 : 1**\n"
                "- 50% purple (Pp), 50% white (pp).\n\n"
                "**Answer:** 1/2 (50%) of offspring will have purple flowers.\n\n"
                "---\n\n"
                "**Follow-up:** Two white-flowered plants are crossed (pp × pp). Can any purple-flowered offspring result?\n\n"
                "**Answer:** No. Both parents are homozygous recessive (pp). "
                "All offspring receive one p from each parent → all are pp → all white."
            ),
            "body_he_md": (
                "**בעיה:** צבע פרחים באפונה: סגול (P) דומיננטי על לבן (p). "
                "מצליבים צמח סגול הטרוזיגוט (Pp) עם צמח לבן (pp). "
                "איזה שבר מהצאצאים יהיה בעל פרחים סגולים?\n\n"
                "**שלב 1 — כתוב את ההצלבה:** Pp × pp\n\n"
                "**שלב 2 — מלא ריבוע פאנט:**\n\n"
                "```\n"
                "      P    p\n"
                "  p [ Pp ] [ pp ]\n"
                "  p [ Pp ] [ pp ]\n"
                "```\n\n"
                "**שלב 3 — קרא את התוצאות:**\n"
                "- Pp : pp = 2 : 2 = **1 : 1**\n"
                "- 50% סגול (Pp), 50% לבן (pp).\n\n"
                "**תשובה:** 1/2 (50%) מהצאצאים יהיו בעלי פרחים סגולים.\n\n"
                "---\n\n"
                "**המשך:** שני צמחים לבנים מוצלבים (pp × pp). האם ייתכנו צאצאים סגולים?\n\n"
                "**תשובה:** לא. שני ההורים הומוזיגוטים רצסיביים (pp). "
                "כל הצאצאים מקבלים p אחד מכל הורה → כולם pp → כולם לבנים."
            )
        },
        {
            "kind": "pitfall",
            "title_en": "Common mistakes",
            "title_he": "טעויות נפוצות",
            "body_en_md": (
                "1. **Confusing genotype with phenotype.** Bb and BB both give the SAME phenotype (dominant), "
                "but different genotypes. Two organisms can look identical yet have different genetics.\n\n"
                "2. **Dominant does not mean 'more common'.** A dominant allele is simply the one expressed. "
                "A recessive trait can be very common in a population (e.g. blue eyes).\n\n"
                "3. **Forgetting that carriers (Bb) show the dominant trait.** Carriers appear phenotypically "
                "dominant but can pass the recessive allele to offspring.\n\n"
                "4. **Incorrect Punnett square.** Always write one allele per cell, not two. "
                "Check: 4 cells total, each inheriting one allele from each parent."
            ),
            "body_he_md": (
                "1. **בלבול גנוטיפ ופנוטיפ.** Bb ו-BB נותנים את **אותו פנוטיפ** (דומיננטי), "
                "אך גנוטיפים שונים. שני יצורים יכולים להיראות זהה ועדיין להיות שונים גנטית.\n\n"
                "2. **דומיננטי לא אומר 'נפוץ יותר'.** אלל דומיננטי פשוט מתבטא. "
                "תכונה רצסיבית יכולה להיות נפוצה מאוד באוכלוסייה (כגון עיניים כחולות).\n\n"
                "3. **שכחה שנשאים (Bb) מראים את התכונה הדומיננטית.** נשאים נראים פנוטיפית דומיננטיים "
                "אך יכולים להעביר את האלל הרצסיבי לצאצאים.\n\n"
                "4. **ריבוע פאנט שגוי.** תמיד כתוב אלל אחד בכל תא. "
                "בדוק: 4 תאים בסך הכל, כל אחד מקבל אלל אחד מכל הורה."
            )
        },
        {
            "kind": "summary",
            "title_en": "Key take-aways",
            "title_he": "עיקרי השיעור",
            "body_en_md": (
                "- **Gene (גן):** unit of heredity; each organism has 2 copies (**alleles**).\n"
                "- **Dominant (דומיננטי):** expressed when at least one copy present (BB or Bb).\n"
                "- **Recessive (רצסיבי):** expressed only in homozygous state (bb).\n"
                "- **Punnett square:** predicts offspring genotype/phenotype probabilities.\n"
                "- Classic monohybrid cross Bb × Bb → 3:1 phenotype ratio.\n"
                "- **Genotype ≠ phenotype:** BB and Bb look the same but differ genetically."
            ),
            "body_he_md": (
                "- **גן:** יחידת הירושה; לכל יצור 2 עותקים (**אללים**).\n"
                "- **דומיננטי:** מתבטא כשנוכח לפחות עותק אחד (BB או Bb).\n"
                "- **רצסיבי:** מתבטא רק במצב הומוזיגוטי (bb).\n"
                "- **ריבוע פאנט:** מנבא הסתברויות לגנוטיפ/פנוטיפ של צאצאים.\n"
                "- הצלבה חד-גורמית קלאסית Bb × Bb → יחס פנוטיפי 3:1.\n"
                "- **גנוטיפ ≠ פנוטיפ:** BB ו-Bb נראים זהה אך שונים גנטית."
            )
        }
    ],
    "questions": [
        {
            "ord": 1, "kind": "mcq", "difficulty": "easy",
            "stem_en": "An organism with genotype Bb for flower color (B = purple, b = white) will have which phenotype?",
            "stem_he": "יצור עם גנוטיפ Bb לצבע פרח (B = סגול, b = לבן) יהיה בעל איזה פנוטיפ?",
            "options_en": ["White, because b is present", "Purple, because B is dominant", "A mixture of purple and white", "Cannot be determined"],
            "options_he": ["לבן, כי b קיים", "סגול, כי B דומיננטי", "תערובת של סגול ולבן", "לא ניתן לקבוע"],
            "correct_index": 1,
            "explanation_en": "B is dominant over b. In Bb (heterozygous), the dominant allele B is expressed, so the flower is purple. The b allele is present but hidden.",
            "explanation_he": "B דומיננטי על b. ב-Bb (הטרוזיגוט), האלל הדומיננטי B מתבטא, ולכן הפרח סגול. האלל b קיים אך נסתר.",
            "skill_atoms": ["dominance_rule"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 2, "kind": "mcq", "difficulty": "medium",
            "stem_en": "Two heterozygous parents (Bb × Bb) are crossed. What fraction of offspring will show the recessive phenotype (bb)?",
            "stem_he": "שני הורים הטרוזיגוטים (Bb × Bb) מוצלבים. איזה שבר מהצאצאים יראה את הפנוטיפ הרצסיבי (bb)?",
            "options_en": ["1/4", "1/2", "3/4", "All offspring"],
            "options_he": ["1/4", "1/2", "3/4", "כל הצאצאים"],
            "correct_index": 0,
            "explanation_en": "Punnett square: BB, Bb, Bb, bb. Only bb (1 out of 4) shows the recessive phenotype → 1/4 probability.",
            "explanation_he": "ריבוע פאנט: BB, Bb, Bb, bb. רק bb (1 מתוך 4) מראה את הפנוטיפ הרצסיבי → הסתברות 1/4.",
            "skill_atoms": ["punnett_square"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 3, "kind": "mcq", "difficulty": "medium",
            "stem_en": "Which of the following is TRUE about a carrier (heterozygous Bb individual)?",
            "stem_he": "איזה מהאמירות הבאות נכון לגבי נשא (יחיד הטרוזיגוטי Bb)?",
            "options_en": ["Shows the recessive phenotype", "Cannot pass b to offspring", "Shows the dominant phenotype but can pass b to offspring", "Is homozygous"],
            "options_he": ["מראה את הפנוטיפ הרצסיבי", "לא יכול להעביר b לצאצאים", "מראה את הפנוטיפ הדומיננטי אך יכול להעביר b לצאצאים", "הומוזיגוט"],
            "correct_index": 2,
            "explanation_en": "A carrier (Bb) shows the dominant phenotype because B masks b. However, during meiosis, the b allele is segregated and may be passed to offspring.",
            "explanation_he": "נשא (Bb) מראה את הפנוטיפ הדומיננטי כי B מסתיר את b. אך במיוזה, האלל b מופרד ויכול לעבור לצאצאים.",
            "skill_atoms": ["dominance_rule", "carrier_concept"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 4, "kind": "mcq", "difficulty": "hard",
            "stem_en": "Brown eyes (B) are dominant over blue eyes (b). Two brown-eyed parents have a blue-eyed child. What must be true about the parents?",
            "stem_he": "עיניים חומות (B) דומיננטיות על עיניים כחולות (b). לשני הורים עם עיניים חומות נולד ילד עם עיניים כחולות. מה חייב להיות נכון לגבי ההורים?",
            "options_en": ["Both parents are BB", "Both parents are bb", "Both parents are Bb (carriers)", "One parent is BB, one is Bb"],
            "options_he": ["שני ההורים הם BB", "שני ההורים הם bb", "שני ההורים הם Bb (נשאים)", "הורה אחד BB, אחד Bb"],
            "correct_index": 2,
            "explanation_en": "A blue-eyed child (bb) must receive one b allele from each parent. Since the parents have brown eyes, they cannot be bb. They must each carry the b allele → both are Bb (heterozygous carriers).",
            "explanation_he": "ילד עם עיניים כחולות (bb) חייב לקבל אלל b אחד מכל הורה. מכיוון שלהורים עיניים חומות, הם לא יכולים להיות bb. הם חייבים להיות נשאים של b → שניהם Bb (הטרוזיגוטים).",
            "skill_atoms": ["punnett_square", "dominance_rule", "carrier_concept"], "points_level_min": "biology_4pt"
        }
    ],
    "agent_hints": (
        "Mendelian genetics is one of the highest-yield topics in Bagrut biology. Exam patterns: "
        "(1) given two parent genotypes, draw Punnett square and find offspring ratios; "
        "(2) given offspring ratios, work backwards to determine parent genotypes; "
        "(3) pedigree reading (rare on 4pt but possible). "
        "Common mistake: students confuse genotype and phenotype — reinforce that Bb looks IDENTICAL to BB in phenotype. "
        "Hebrew: גן=gene, אלל=allele, דומיננטי=dominant, רצסיבי=recessive, גנוטיפ=genotype, פנוטיפ=phenotype, "
        "הומוזיגוט=homozygous, הטרוזיגוט=heterozygous, נשא=carrier, ריבוע פאנט=Punnett square."
    ),
    "skill_atoms": [
        {"id": "dominance_rule", "description_en": "Apply dominant/recessive inheritance rules", "description_he": "יישום כללי ירושה דומיננטית/רצסיבית"},
        {"id": "punnett_square", "description_en": "Construct and read Punnett squares for monohybrid crosses", "description_he": "בניית וקריאת ריבועי פאנט להצלבות חד-גוריות"},
        {"id": "carrier_concept", "description_en": "Identify and reason about heterozygous carriers", "description_he": "זיהוי והנמקה על נשאים הטרוזיגוטים"}
    ]
}

# ─── 3. natural_selection ────────────────────────────────────────────────────

natural_selection = {
    "concept_id": "natural_selection",
    "subject": "biology",
    "level": "high_school",
    "math_track": ["biology_4pt"],
    "title_en": "Natural Selection and Evolution",
    "title_he": "ברירה טבעית ואבולוציה",
    "summary_en": "Charles Darwin's theory of natural selection explains how populations change over generations: individuals with advantageous traits survive and reproduce more, passing those traits on. This lesson covers the four key components, examples, and the concept of adaptation.",
    "summary_he": "תיאוריית הברירה הטבעית של צ'ארלס דרווין מסבירה כיצד אוכלוסיות משתנות לאורך דורות: יחידים עם תכונות מועילות שורדים ומתרבים יותר, ומעבירים את התכונות הללו. שיעור זה עוסק בארבעה המרכיבים המרכזיים, דוגמאות ומושג ההסתגלות.",
    "est_minutes": 23,
    "sections": [
        {
            "kind": "intro",
            "title_en": "Why populations change: the idea of natural selection",
            "title_he": "מדוע אוכלוסיות משתנות: רעיון הברירה הטבעית",
            "body_en_md": (
                "**Evolution (אבולוציה)** is the change in the inherited characteristics of a population "
                "over successive generations. The primary mechanism is **natural selection (ברירה טבעית)**.\n\n"
                "Darwin's insight (1859): in any population, some individuals have traits that make them "
                "**better suited** to their environment. These individuals are more likely to survive, "
                "reproduce, and pass their advantageous traits to offspring.\n\n"
                "Over many generations, the proportion of individuals with favorable traits **increases** "
                "in the population — the population **evolves**.\n\n"
                "Natural selection works on **variation** that already exists in a population. "
                "It does not create new traits — it **selects** among existing ones."
            ),
            "body_he_md": (
                "**אבולוציה** היא שינוי במאפיינים הגנטיים של אוכלוסייה לאורך דורות רצופים. "
                "המנגנון העיקרי הוא **ברירה טבעית**.\n\n"
                "תובנתו של דרווין (1859): בכל אוכלוסייה, לחלק מהיחידים יש תכונות שהופכות אותם "
                "**מותאמים יותר** לסביבתם. יחידים אלה נוטים יותר לשרוד, להתרבות, "
                "ולהעביר את תכונותיהם המועילות לצאצאים.\n\n"
                "לאורך דורות רבים, שיעור היחידים עם תכונות נוחות **גדל** באוכלוסייה — "
                "האוכלוסייה **מתפתחת**.\n\n"
                "הברירה הטבעית פועלת על **וריאציה** הקיימת כבר באוכלוסייה. "
                "היא אינה יוצרת תכונות חדשות — היא **בוררת** בין הקיימות."
            )
        },
        {
            "kind": "theory",
            "title_en": "The four components of natural selection",
            "title_he": "ארבעת מרכיבי הברירה הטבעית",
            "body_en_md": (
                "For natural selection to occur, four conditions must be met:\n\n"
                "1. **Variation (וריאציה):** Individuals in a population differ in their traits. "
                "Without variation, all individuals are identical — nothing to select.\n\n"
                "2. **Heritability (תורשתיות):** The differences must be heritable — passed from "
                "parent to offspring through genes. Non-genetic differences (e.g. a scar) are not selected.\n\n"
                "3. **Differential reproduction / fitness (כושר הסתגלות):** "
                "Individuals with certain traits leave more offspring than others. "
                "**Fitness** = reproductive success relative to others.\n\n"
                "4. **Selection pressure (לחץ סלקציה):** An environmental factor (predators, disease, "
                "food availability, climate) that favors some traits over others.\n\n"
                "**Result:** Over generations, alleles that increase fitness become more common; "
                "those that decrease fitness become rarer or disappear.\n\n"
                "### Adaptation (הסתגלות)\n\n"
                "An **adaptation** is a heritable trait that increases an organism's fitness in its environment. "
                "Examples:\n"
                "- **Camouflage** (הסוואה): cryptic coloration reduces predation risk.\n"
                "- **Antibiotic resistance** (עמידות לאנטיביוטיקה): bacteria with resistance survive antibiotic treatment.\n"
                "- **Long neck in giraffes:** allows access to higher leaves when food is scarce."
            ),
            "body_he_md": (
                "כדי שברירה טבעית תתרחש, ארבעה תנאים חייבים להתקיים:\n\n"
                "1. **וריאציה:** ליחידים באוכלוסייה יש תכונות שונות. "
                "ללא וריאציה, כל היחידים זהים — אין מה לבחור.\n\n"
                "2. **תורשתיות:** ההבדלים חייבים להיות תורשתיים — להיות מועברים מהורה לצאצא דרך גנים. "
                "הבדלים לא-גנטיים (כגון צלקת) אינם נבררים.\n\n"
                "3. **רבייה דיפרנציאלית / כושר הסתגלות:** "
                "ליחידים עם תכונות מסוימות יש יותר צאצאים מאחרים. "
                "**כושר הסתגלות** = הצלחה רבייתית ביחס לאחרים.\n\n"
                "4. **לחץ סלקציה:** גורם סביבתי (טורפים, מחלות, זמינות מזון, אקלים) "
                "המעדיף תכונות מסוימות על פני אחרות.\n\n"
                "**תוצאה:** לאורך דורות, אללים המגדילים כושר הסתגלות נעשים נפוצים יותר; "
                "אלה המפחיתים אותו הופכים נדירים יותר או נעלמים.\n\n"
                "### הסתגלות (Adaptation)\n\n"
                "**הסתגלות** היא תכונה תורשתית המגדילה את כושר ההישרדות והרבייה של יצור בסביבתו. "
                "דוגמאות:\n"
                "- **הסוואה:** צבעוניות צופנית מקטינה סיכון לטריפה.\n"
                "- **עמידות לאנטיביוטיקה:** חיידקים בעלי עמידות שורדים טיפול אנטיביוטי.\n"
                "- **צוואר ארוך בג'ירפות:** מאפשר גישה לעלים גבוהים יותר כשמזון דליל."
            )
        },
        {
            "kind": "worked_example",
            "title_en": "Worked example: antibiotic resistance — natural selection in action",
            "title_he": "דוגמה פתורה: עמידות לאנטיביוטיקה — ברירה טבעית בפעולה",
            "body_en_md": (
                "**Scenario:** A patient takes an antibiotic to treat a bacterial infection. "
                "After a few days they stop treatment early because they feel better. "
                "A week later, the infection returns and the same antibiotic no longer works.\n\n"
                "**Explain using natural selection:**\n\n"
                "1. **Variation:** In the original bacterial population, a small fraction of bacteria "
                "had a mutation giving resistance to the antibiotic.\n\n"
                "2. **Selection pressure:** The antibiotic kills non-resistant bacteria. "
                "Resistant bacteria survive.\n\n"
                "3. **Differential reproduction:** Resistant bacteria reproduce freely "
                "(non-resistant competitors eliminated). Their numbers grow rapidly.\n\n"
                "4. **Heritability:** The resistance gene is passed to all daughter cells.\n\n"
                "**Result:** The new bacterial population is almost entirely resistant — "
                "the antibiotic is no longer effective.\n\n"
                "**Lesson:** Completing a full antibiotic course kills even resistant stragglers "
                "before they can multiply and dominate the population."
            ),
            "body_he_md": (
                "**תרחיש:** מטופל לוקח אנטיביוטיקה לטיפול בזיהום חיידקי. "
                "אחרי כמה ימים הוא מפסיק את הטיפול מוקדם כי הוא מרגיש טוב יותר. "
                "שבוע לאחר מכן הזיהום חוזר ואותה אנטיביוטיקה כבר לא עובדת.\n\n"
                "**הסבר באמצעות ברירה טבעית:**\n\n"
                "1. **וריאציה:** באוכלוסיית החיידקים המקורית, שבריר קטן מהחיידקים "
                "נשא מוטציה המקנה עמידות לאנטיביוטיקה.\n\n"
                "2. **לחץ סלקציה:** האנטיביוטיקה הורגת חיידקים רגישים. חיידקים עמידים שורדים.\n\n"
                "3. **רבייה דיפרנציאלית:** חיידקים עמידים מתרבים ללא הפרעה "
                "(המתחרים הרגישים הושמדו). מספרם גדל במהירות.\n\n"
                "4. **תורשתיות:** גן העמידות מועבר לכל תאי הבת.\n\n"
                "**תוצאה:** האוכלוסייה החיידקית החדשה עמידה כמעט לחלוטין — "
                "האנטיביוטיקה כבר אינה יעילה.\n\n"
                "**לקח:** השלמת מסלול אנטיביוטיקה מלא הורגת אפילו חיידקים עמידים לפני שהם יכולים "
                "להתרבות ולשלוט באוכלוסייה."
            )
        },
        {
            "kind": "summary",
            "title_en": "Key take-aways",
            "title_he": "עיקרי השיעור",
            "body_en_md": (
                "- **Evolution (אבולוציה):** change in inherited traits of a population over generations.\n"
                "- **Natural selection (ברירה טבעית):** the mechanism; requires 4 conditions: variation, "
                "heritability, differential reproduction, selection pressure.\n"
                "- **Adaptation (הסתגלות):** heritable trait increasing fitness.\n"
                "- **Fitness:** reproductive success relative to others — NOT physical strength.\n"
                "- Natural selection acts on existing **variation**; it does not create new traits.\n"
                "- Classic examples: antibiotic resistance, peppered moths, Darwin's finches."
            ),
            "body_he_md": (
                "- **אבולוציה:** שינוי במאפיינים התורשתיים של אוכלוסייה לאורך דורות.\n"
                "- **ברירה טבעית:** המנגנון; דורש 4 תנאים: וריאציה, תורשתיות, רבייה דיפרנציאלית, לחץ סלקציה.\n"
                "- **הסתגלות:** תכונה תורשתית המגדילה כושר הישרדות.\n"
                "- **כושר הסתגלות:** הצלחה רבייתית ביחס לאחרים — לא כוח פיזי.\n"
                "- הברירה הטבעית פועלת על **וריאציה** קיימת; היא אינה יוצרת תכונות חדשות.\n"
                "- דוגמאות קלאסיות: עמידות לאנטיביוטיקה, עש הפלפל, חנוכיות דרווין."
            )
        }
    ],
    "questions": [
        {
            "ord": 1, "kind": "mcq", "difficulty": "easy",
            "stem_en": "Which of the following is NOT a requirement for natural selection to occur?",
            "stem_he": "איזה מהבאים אינו תנאי הכרחי לקיום ברירה טבעית?",
            "options_en": ["Variation among individuals", "Heritability of traits", "Equal reproductive success for all individuals", "Selection pressure from the environment"],
            "options_he": ["וריאציה בין יחידים", "תורשתיות של תכונות", "הצלחה רבייתית שווה לכל היחידים", "לחץ סלקציה מהסביבה"],
            "correct_index": 2,
            "explanation_en": "Natural selection REQUIRES unequal reproductive success (differential reproduction). Equal success means no selection — the population's genetics stays the same.",
            "explanation_he": "ברירה טבעית דורשת הצלחה רבייתית **לא שווה** (רבייה דיפרנציאלית). הצלחה שווה פירושה אין סלקציה — הגנטיקה של האוכלוסייה נשארת זהה.",
            "skill_atoms": ["natural_selection_conditions"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 2, "kind": "mcq", "difficulty": "easy",
            "stem_en": "A population of beetles lives on a brown forest floor. Most are brown, but a few are green. Birds preferentially eat green beetles. After many generations, what will happen to the population?",
            "stem_he": "אוכלוסיית חיפושיות חיה על רצפת יער חומה. רובן חומות, אך מעטות ירוקות. ציפורים אוכלות חיפושיות ירוקות בעדיפות. לאחר דורות רבים, מה יקרה לאוכלוסייה?",
            "options_en": ["The proportion of green beetles will increase", "The proportion of brown beetles will increase", "All beetles will become green", "The population will stay the same"],
            "options_he": ["שיעור החיפושיות הירוקות יגדל", "שיעור החיפושיות החומות יגדל", "כל החיפושיות יהפכו לירוקות", "האוכלוסייה תישאר זהה"],
            "correct_index": 1,
            "explanation_en": "Green beetles are eaten preferentially (selection pressure against green color). Brown beetles survive and reproduce more. Over generations, brown becomes more common — natural selection for camouflage.",
            "explanation_he": "חיפושיות ירוקות נאכלות בעדיפות (לחץ סלקציה נגד צבע ירוק). חיפושיות חומות שורדות ומתרבות יותר. לאורך דורות, חום הופך נפוץ יותר — ברירה טבעית עבור הסוואה.",
            "skill_atoms": ["natural_selection_conditions", "adaptation_concept"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 3, "kind": "mcq", "difficulty": "medium",
            "stem_en": "Why does stopping antibiotic treatment early increase the risk of antibiotic-resistant bacteria developing?",
            "stem_he": "מדוע הפסקת טיפול אנטיביוטי מוקדם מגדילה את הסיכון לפיתוח חיידקים עמידים לאנטיביוטיקה?",
            "options_en": [
                "The remaining bacteria mutate in response to the antibiotic",
                "Bacteria learn to avoid the antibiotic over time",
                "Resistant bacteria that survived the early treatment reproduce without competition from dead non-resistant bacteria",
                "The antibiotic weakens all bacteria equally"
            ],
            "options_he": [
                "החיידקים הנותרים מתמחים בתגובה לאנטיביוטיקה",
                "חיידקים לומדים להימנע מהאנטיביוטיקה עם הזמן",
                "חיידקים עמידים ששרדו את הטיפול המוקדם מתרבים ללא תחרות מחיידקים רגישים שמתו",
                "האנטיביוטיקה מחלישה את כל החיידקים באופן שווה"
            ],
            "correct_index": 2,
            "explanation_en": "Early stopping leaves resistant bacteria alive (they survived the antibiotic). With non-resistant competitors killed off, resistant bacteria reproduce freely and dominate. This is natural selection in action — not adaptation by individual bacteria.",
            "explanation_he": "הפסקה מוקדמת משאירה חיידקים עמידים בחיים (הם שרדו את האנטיביוטיקה). עם מות המתחרים הרגישים, חיידקים עמידים מתרבים ללא הפרעה ושולטים. זו ברירה טבעית בפעולה — לא הסתגלות של חיידקים בודדים.",
            "skill_atoms": ["natural_selection_conditions", "adaptation_concept"], "points_level_min": "biology_4pt"
        },
        {
            "ord": 4, "kind": "mcq", "difficulty": "medium",
            "stem_en": "Which statement BEST defines 'fitness' in the context of natural selection?",
            "stem_he": "איזה משפט מגדיר בצורה הטובה ביותר 'כושר הסתגלות' בהקשר של ברירה טבעית?",
            "options_en": [
                "Physical strength of an individual organism",
                "The ability to run fast to escape predators",
                "Reproductive success relative to other individuals in the population",
                "Having the largest body size in the population"
            ],
            "options_he": [
                "הכוח הגופני של יחיד",
                "היכולת לרוץ מהר כדי להימלט מטורפים",
                "הצלחה רבייתית ביחס ליחידים אחרים באוכלוסייה",
                "גוף הגדול ביותר באוכלוסייה"
            ],
            "correct_index": 2,
            "explanation_en": "In evolutionary biology, 'fitness' is specifically defined as reproductive success — how many offspring an organism leaves relative to others. A weak organism that leaves many offspring is more 'fit' than a strong one with few offspring.",
            "explanation_he": "בביולוגיה אבולוציונית, 'כושר הסתגלות' מוגדר ספציפית כהצלחה רבייתית — כמה צאצאים יצור משאיר ביחס לאחרים. יצור חלש שמשאיר צאצאים רבים 'כשיר' יותר מיצור חזק עם מעט צאצאים.",
            "skill_atoms": ["fitness_definition"], "points_level_min": "biology_4pt"
        }
    ],
    "agent_hints": (
        "Natural selection is a high-yield topic for Bagrut biology. Key exam patterns: "
        "(1) describe how a population changes using the 4 conditions of natural selection; "
        "(2) apply the antibiotic resistance or camouflage examples; "
        "(3) define and distinguish fitness, adaptation, and variation. "
        "Most common mistake: students say bacteria 'learn' or 'adapt' to antibiotics — "
        "correct this firmly: natural selection acts on EXISTING variation; bacteria do not choose to mutate. "
        "Hebrew: ברירה טבעית=natural selection, אבולוציה=evolution, הסתגלות=adaptation, "
        "וריאציה=variation, תורשתיות=heritability, כושר הסתגלות=fitness, לחץ סלקציה=selection pressure."
    ),
    "skill_atoms": [
        {"id": "natural_selection_conditions", "description_en": "List and apply the 4 conditions of natural selection", "description_he": "פירוט ויישום 4 תנאי הברירה הטבעית"},
        {"id": "adaptation_concept", "description_en": "Define adaptation and provide examples", "description_he": "הגדרת הסתגלות ומתן דוגמאות"},
        {"id": "fitness_definition", "description_en": "Define biological fitness as reproductive success", "description_he": "הגדרת כושר הסתגלות כהצלחה רבייתית"}
    ]
}

# ─── Write all three files ────────────────────────────────────────────────────

for name, data in [
    ("cell_structure.json", cell_structure),
    ("heredity_mendelian.json", heredity_mendelian),
    ("natural_selection.json", natural_selection),
]:
    path = os.path.join(LESSONS_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"Written {name} — sections: {len(data['sections'])}, questions: {len(data['questions'])}")

print("Done.")
