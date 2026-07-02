#!/usr/bin/env python3
"""Expand kirchhoff_laws.json — substantive bilingual content per expand-lessons-cursor."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/kirchhoff_laws.json"

MIN_WORDS = {
    "intro": {"en": 110, "he": 90},
    "definition": {"en": 130, "he": 110},
    "theory": {"en": 160, "he": 130},
    "worked_example": {"en": 130, "he": 110},
    "pitfall": {"en": 100, "he": 85},
    "why_matters": {"en": 90, "he": 75},
    "method_guide": {"en": 100, "he": 85},
    "before_exam": {"en": 90, "he": 75},
    "summary": {"en": 70, "he": 60},
}


def word_count(text):
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


def hebrew_char_ratio(text):
    he = len(re.findall(r"[\u0590-\u05FF]", text or ""))
    lat = len(re.findall(r"[a-zA-Z]{3,}", text or ""))
    return he / (he + lat + 1)


def hebrew_body_weak(body_he, body_en):
    he = (body_he or "").strip()
    en = (body_en or "").strip()
    if not he:
        return True
    if not en:
        return hebrew_char_ratio(he) < 0.12
    ratio = word_count(he) / max(word_count(en), 1)
    if ratio < 0.55:
        return True
    if hebrew_char_ratio(he) < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


EXPLANATIONS = {
    1: {
        "en": (
            "Kirchhoff's Current Law (KCL) is the junction rule: charge cannot accumulate at a "
            "node, so every ampere entering must leave. Mathematically, "
            "$\\sum I_{\\text{in}} = \\sum I_{\\text{out}}$ at every junction.\n\n"
            "**Why option 2 is correct:** It states exactly this balance of incoming and outgoing "
            "currents. Option 1 describes KVL (voltage around a loop), not KCL. Option 3 is "
            "Ohm's law for a single resistor. Option 4 describes power balance, which follows "
            "from energy conservation but is not the statement of KCL.\n\n"
            "**Common wrong path:** Picking \"sum of voltages = 0\" because both Kirchhoff laws "
            "appear together in circuit problems — remember KCL is about **currents at nodes**, "
            "KVL about **voltages around loops**.\n\n"
            "**Exam tip:** When a Bagrut stem says \"at a junction\" or \"at a node,\" reach for "
            "KCL immediately. Label arrows in and out before writing the equation."
        ),
        "he": (
            "חוק הזרם של קירכהוף (KCL) הוא כלל הצמתים: מטען לא יכול להצטבר בצומת, ולכן כל "
            "אמפר שנכנס חייב לצאת. מתמטית: $\\sum I_{\\text{נכנסים}} = \\sum I_{\\text{יוצאים}}$ "
            "בכל צומת.\n\n"
            "**למה אפשרות 2 נכונה:** היא מציינת בדיוק את האיזון בין זרמים נכנסים ליוצאים. "
            "אפשרות 1 מתארת KVL (מתח סביב לולאה), לא KCL. אפשרות 3 היא חוק אוהם לנגד בודד. "
            "אפשרות 4 מתארת איזון הספק — נובע משימור אנרגיה אך אינה ניסוח KCL.\n\n"
            "**טעות נפוצה:** בחירת \"סכום מתחים = 0\" כי שני חוקי קירכהוף מופיעים יחד — "
            "זכרו: KCL על **זרמים בצמתים**, KVL על **מתחים בלולאות**.\n\n"
            "**טיפ לבחינה:** כשבשאלה מופיע \"בצומת\" או \"בנקודת חיבור,\" פנו מיד ל-KCL. "
            "סמנו חצים נכנסים ויוצאים לפני כתיבת המשוואה."
        ),
    },
    2: {
        "en": (
            "At a node, KCL requires that the sum of currents entering equals the sum leaving. "
            "Here $I_1 = 5$ A and $I_2 = 2$ A both flow **into** the junction, and $I_3$ flows "
            "out:\n"
            "$$I_1 + I_2 = I_3 \\quad\\Rightarrow\\quad 5 + 2 = I_3 = 7\\text{ A}$$\n\n"
            "The answer is positive, confirming $I_3$ leaves in the assumed direction.\n\n"
            "**Common wrong path:** Subtracting only one incoming current ($5 - 2 = 3$ A) or "
            "adding all three as if they were in the same direction. Always classify each branch "
            "as in or out first.\n\n"
            "**Exam tip:** Write \"in = out\" as words before substituting numbers. A quick check: "
            "7 A out balances 5 + 2 A in. Units stay in amperes throughout — no conversion needed."
        ),
        "he": (
            "בצומת, KCL דורש שסכום הזרמים הנכנסים ישווה לסכום היוצאים. כאן $I_1 = 5$ A "
            "ו-$I_2 = 2$ A נכנסים **פנימה**, ו-$I_3$ יוצא:\n"
            "$$I_1 + I_2 = I_3 \\quad\\Rightarrow\\quad 5 + 2 = I_3 = 7\\text{ A}$$\n\n"
            "התשובה חיובית — מאשרת ש-$I_3$ יוצא בכיוון ההנחה.\n\n"
            "**טעות נפוצה:** חיסור רק זרם נכנס אחד ($5 - 2 = 3$ A) או חיבור שלושת הזרמים "
            "כאילו באותו כיוון. תמיד סווגו כל ענף כנכנס או יוצא.\n\n"
            "**טיפ לבחינה:** כתבו \"נכנס = יוצא\" במילים לפני הצבת מספרים. בדיקה מהירה: "
            "7 A יוצא מאזן 5 + 2 A נכנס. יחידות נשארות באמפר — אין צורך בהמרה."
        ),
    },
    3: {
        "en": (
            "A single-loop circuit has one current $I$ everywhere. Apply KVL by traversing the loop "
            "clockwise from the battery's negative terminal: EMF rise, then resistor drop:\n"
            "$$\\mathcal{E} - IR = 0 \\quad\\Rightarrow\\quad I = \\frac{\\mathcal{E}}{R} "
            "= \\frac{6}{2} = 3\\text{ A}$$\n\n"
            "This is equivalent to Ohm's law because there is only one branch — KVL generalizes "
            "Ohm's law to multi-component loops.\n\n"
            "**Common wrong path:** Dividing $R$ by $\\mathcal{E}$ (getting 0.33 A) or forgetting "
            "the sign convention and writing $6 + 2I = 0$. Choose a traversal direction and stick "
            "to it.\n\n"
            "**Exam tip:** For a lone battery and resistor, KVL and $I = V/R$ must agree. "
            "If they differ, recheck your sign for the resistor drop ($-IR$ when current flows "
            "with your traversal)."
        ),
        "he": (
            "במעגל לולאה אחת יש זרם $I$ אחד בכל מקום. יישמו KVL במעבר עם כיוון השעון "
            "ממינוס הסוללה: עליית כ\"א, אחר כך ירידה על הנגד:\n"
            "$$\\mathcal{E} - IR = 0 \\quad\\Rightarrow\\quad I = \\frac{\\mathcal{E}}{R} "
            "= \\frac{6}{2} = 3\\text{ A}$$\n\n"
            "זה שקול לחוק אוהם כי יש ענף אחד — KVL מכליל את חוק אוהם למעגלים מורכבים.\n\n"
            "**טעות נפוצה:** חלוקת $R$ ב-$\\mathcal{E}$ (0.33 A) או שכחת מוסכמת הסימן "
            "($6 + 2I = 0$). בחרו כיוון מעבר והיצמדו אליו.\n\n"
            "**טיפ לבחינה:** לסוללה ונגד בודדים, KVL ו-$I = V/R$ חייבים להתאים. "
            "אם לא — בדקו סימן ירידת הנגד ($-IR$ כשהזרם בכיוון המעבר)."
        ),
    },
    4: {
        "en": (
            "The voltage across a resistor follows Ohm's law: $V = IR$. With $R = 5\\,\\Omega$ "
            "and $I = 2$ A:\n"
            "$$V = 5 \\times 2 = 10\\text{ V}$$\n\n"
            "This is not a Kirchhoff equation by itself, but every KVL loop contains terms of "
            "the form $-IR$ or $+IR$ for each resistor. Knowing $V = IR$ lets you verify individual "
            "drops after solving the full system.\n\n"
            "**Common wrong path:** Dividing $I/R$ instead of multiplying, or reporting "
            "$0.4$ V from $2/5$. Always check: higher current through a fixed resistor means "
            "higher voltage drop.\n\n"
            "**Exam tip:** After solving a multi-loop problem, compute $V = IR$ on each resistor "
            "and confirm the drops around each loop sum to zero — a powerful self-check."
        ),
        "he": (
            "המתח על נגד עוקב אחר חוק אוהם: $V = IR$. עם $R = 5\\,\\Omega$ ו-$I = 2$ A:\n"
            "$$V = 5 \\times 2 = 10\\text{ V}$$\n\n"
            "זו לא משוואת קירכהוף בפני עצמה, אך כל לולאת KVL מכילה איברים $-IR$ או $+IR$ "
            "לכל נגד. ידיעת $V = IR$ מאפשרת לאמת ירידות בודדות אחרי פתרון המערכת.\n\n"
            "**טעות נפוצה:** חלוקת $I/R$ במקום כפל, או דיווח $0.4$ V מ-$2/5$. "
            "תמיד בדקו: זרם גבוה יותר בנגד קבוע ⇒ ירידת מתח גבוהה יותר.\n\n"
            "**טיפ לבחינה:** אחרי פתרון מעגל מרובה לולאות, חשבו $V = IR$ על כל נגד "
            "וודאו שהירידות סביב כל לולאה מסתכמות לאפס — בדיקה עצמית חזקה."
        ),
    },
    5: {
        "en": (
            "Voltage is defined as energy per unit charge: $V = W/Q$. When a charge $Q$ completes "
            "a full closed loop, it returns to the same potential — no net energy gain or loss. "
            "Therefore the algebraic sum of all voltage rises and drops around the loop must be "
            "zero: $\\sum V_i = 0$. This is Kirchhoff's Voltage Law, a direct statement of "
            "conservation of energy for electric charges in a circuit.\n\n"
            "**Common wrong path:** Confusing KVL with KCL (\"energy at a node\") or claiming "
            "energy is lost because resistors dissipate heat. Resistors convert electrical energy "
            "to heat, but the battery supplies exactly that energy — net around the loop is zero.\n\n"
            "**Exam tip:** In Bagrut conceptual questions, link KVL to \"charge returns to start "
            "with same energy.\" Draw a loop arrow and label each rise and drop."
        ),
        "he": (
            "מתח מוגדר כאנרגיה ליחידת מטען: $V = W/Q$. כשמטען $Q$ משלים לולאה סגורה, "
            "הוא חוזר לאותו פוטנציאל — ללא שינוי אנרגיה נטו. לכן סכום עליות וירידות המתח "
            "בלולאה חייב להיות אפס: $\\sum V_i = 0$. זה חוק המתח של קירכהוף — "
            "ניסוח ישיר של שימור אנרגיה למטענים במעגל.\n\n"
            "**טעות נפוצה:** בלבול KVL עם KCL (\"אנרגיה בצומת\") או טענה שאנרגיה \"אבדה\" "
            "כי נגדים מפזרים חום. נגדים ממירים אנרגיה חשמלית לחום, אך הסוללה מספקת "
            "בדיוק את האנרגיה הזו — נטו סביב הלולאה הוא אפס.\n\n"
            "**טיפ לבחינה:** בשאלות מושגיות בבגרות, קשרו KVL ל\"מטען חוזר להתחלה "
            "באותה אנרגיה.\" שרטטו חץ לולאה וסמנו כל עלייה וירידה."
        ),
    },
    6: {
        "en": (
            "Two opposing batteries mean their EMFs subtract in KVL. Traversing the series loop "
            "clockwise from the 10 V battery's negative terminal:\n"
            "$$10 - 4 - 2I - 2I = 0 \\quad\\Rightarrow\\quad 6 = 4I \\quad\\Rightarrow\\quad "
            "I = 1.5\\text{ A}$$\n\n"
            "The net EMF is $10 - 4 = 6$ V driving current through $R_1 + R_2 = 4\\,\\Omega$, "
            "giving $I = 6/4 = 1.5$ A — consistent.\n\n"
            "**Common wrong path:** Adding both EMFs ($10 + 4 = 14$ V) when they oppose, or "
            "using only one resistor ($6/2 = 3$ A). Trace the loop and assign $+\\mathcal{E}$ "
            "or $-\\mathcal{E}$ based on crossing direction.\n\n"
            "**Exam tip:** \"Opposing\" batteries in Bagrut usually means subtract EMFs. "
            "Verify: $1.5$ A through $4\\,\\Omega$ gives total drop $6$ V matching net EMF."
        ),
        "he": (
            "שתי סוללות מנוגדות ⇒ כוחות הכ\"א מתחסרים ב-KVL. מעבר בלולאה עם כיוון השעון "
            "ממינוס הסוללה 10 V:\n"
            "$$10 - 4 - 2I - 2I = 0 \\quad\\Rightarrow\\quad 6 = 4I \\quad\\Rightarrow\\quad "
            "I = 1.5\\text{ A}$$\n\n"
            "כ\"א נטו $10 - 4 = 6$ V מניע זרם דרך $R_1 + R_2 = 4\\,\\Omega$, "
            "כלומר $I = 6/4 = 1.5$ A — עקבי.\n\n"
            "**טעות נפוצה:** חיבור שני כוחות הכ\"א ($10 + 4$) כשהם מנוגדים, או שימוש "
            "בנגד אחד בלבד ($6/2 = 3$ A). עקבו אחרי הלולאה והקצו $+\\mathcal{E}$ או "
            "$-\\mathcal{E}$ לפי כיוון המעבר.\n\n"
            "**טיפ לבחינה:** \"מנוגדות\" בבגרות בדרך כלל ⇒ חיסור כוחות כ\"א. "
            "אימות: $1.5$ A דרך $4\\,\\Omega$ נותן ירידה $6$ V = כ\"א נטו."
        ),
    },
    7: {
        "en": (
            "KCL at the node: current in equals current out. Only $I_1 = 3$ A enters; "
            "$I_2 = 1$ A and $I_3$ both leave:\n"
            "$$I_1 = I_2 + I_3 \\quad\\Rightarrow\\quad 3 = 1 + I_3 \\quad\\Rightarrow\\quad "
            "I_3 = 2\\text{ A}$$\n\n"
            "The positive result confirms $I_3$ flows out as assumed.\n\n"
            "**Common wrong path:** Writing $I_1 + I_2 = I_3$ (adding an outgoing current "
            "to the incoming side) or answering $I_3 = 4$ A from $3 + 1$. Draw the node "
            "with three arrows before writing the equation.\n\n"
            "**Exam tip:** Two outgoing branches is the standard KCL setup after single-branch "
            "problems. Always list \"in\" on one side and \"out\" on the other — never mix signs "
            "mid-equation."
        ),
        "he": (
            "KCL בצומת: זרם נכנס = זרם יוצא. רק $I_1 = 3$ A נכנס; $I_2 = 1$ A ו-$I_3$ "
            "שניהם יוצאים:\n"
            "$$I_1 = I_2 + I_3 \\quad\\Rightarrow\\quad 3 = 1 + I_3 \\quad\\Rightarrow\\quad "
            "I_3 = 2\\text{ A}$$\n\n"
            "תוצאה חיובית — מאשרת ש-$I_3$ יוצא בכיוון ההנחה.\n\n"
            "**טעות נפוצה:** כתיבת $I_1 + I_2 = I_3$ (חיבור זרם יוצא לצד הנכנס) "
            "או תשובה $I_3 = 4$ A מ-$3 + 1$. שרטטו צומת עם שלושה חצים לפני המשוואה.\n\n"
            "**טיפ לבחינה:** שני ענפים יוצאים — תצורת KCL סטנדרטית אחרי בעיות ענף בודד. "
            "תמיד \"נכנס\" בצד אחד ו\"יוצא\" בצד שני — אל תערבבו סימנים באמצע. "
            "בדיקה: $1 + 2 = 3$ A יוצא = $3$ A נכנס — מאזן מושלם."
        ),
    },
    8: {
        "en": (
            "Both batteries aid the current in the same direction, so their EMFs add in KVL. "
            "Two resistors in series give total drop $4I + I = 5I$:\n"
            "$$15 + 5 - 4I - I = 0 \\quad\\Rightarrow\\quad 20 = 5I \\quad\\Rightarrow\\quad "
            "I = 4\\text{ A}$$\n\n"
            "Net EMF $20$ V across $5\\,\\Omega$ total resistance confirms $I = 20/5 = 4$ A.\n\n"
            "**Common wrong path:** Subtracting one battery EMF, or using parallel resistance "
            "formula instead of adding $R_1 + R_2$ for series. Read \"same direction\" carefully — "
            "both get $+\\mathcal{E}$ when traversed consistently.\n\n"
            "**Exam tip:** After finding $I$, compute $V_1 = 4 \\times 4 = 16$ V and "
            "$V_2 = 4 \\times 1 = 4$ V; check $16 + 4 = 20$ V = sum of EMFs."
        ),
        "he": (
            "שתי הסוללות תומכות בזרם באותו כיוון — כוחות הכ\"א מתחברים ב-KVL. "
            "שני נגדים בטור נותנים ירידה $4I + I = 5I$:\n"
            "$$15 + 5 - 4I - I = 0 \\quad\\Rightarrow\\quad 20 = 5I \\quad\\Rightarrow\\quad "
            "I = 4\\text{ A}$$\n\n"
            "כ\"א נטו $20$ V על $5\\,\\Omega$ מאשר $I = 20/5 = 4$ A.\n\n"
            "**טעות נפוצה:** חיסור EMF של סוללה אחת, או נוסחת מקביל במקום $R_1 + R_2$ "
            "בטור. קראו \"אותו כיוון\" — שתיהן $+\\mathcal{E}$ במעבר עקבי.\n\n"
            "**טיפ לבחינה:** אחרי מציאת $I$, חשבו $V_1 = 16$ V ו-$V_2 = 4$ V; "
            "בדקו $16 + 4 = 20$ V = סכום כוחות הכ\"א. "
            "שאלות \"באותו כיוון\" בבגרות = חיבור EMF; \"מנוגדות\" = חיסור. "
            "סה\"כ התנגדות $5\\,\\Omega$ — זכרו שזה טור, לא מקביל."
        ),
    },
}


def build_lesson():
    return {
        "concept_id": "kirchhoff_laws",
        "subject": "physics",
        "level": "high_school",
        "math_track": [],
        "title_en": "Kirchhoff's Laws",
        "title_he": "חוקי קירכהוף",
        "summary_en": "Kirchhoff's Current Law (KCL) and Voltage Law (KVL). Node and mesh analysis. Solving multi-loop circuits.",
        "summary_he": "חוק הזרם (KCL) וחוק המתח (KVL). ניתוח צמתים ולולאות. פתרון מעגלים מרובי לולאות.",
        "sections": [
            {
                "kind": "intro",
                "title_en": "Beyond Simple Circuits",
                "title_he": "מעבר למעגלים פשוטים",
                "body_en_md": (
                    "A single resistor connected to a battery is straightforward — one application of "
                    "Ohm's law gives the current. But real circuits in Bagrut electricity (questionnaire 2) "
                    "and engineering rarely look that simple. Household wiring, phone chargers, and lab "
                    "breadboards all contain **multiple loops and branches** where current splits at "
                    "junctions and recombines elsewhere.\n\n"
                    "When resistors connect in ways that are neither pure series nor pure parallel, "
                    "Ohm's law alone cannot determine every branch current. You need a systematic method "
                    "that handles arbitrary topology.\n\n"
                    "**Kirchhoff's Laws** (Gustav Kirchhoff, 1845) provide two conservation principles:\n"
                    "1. **KCL** (Current Law): charge is conserved at every node — current in equals current out.\n"
                    "2. **KVL** (Voltage Law): energy is conserved around every closed loop — net voltage change is zero.\n\n"
                    "Together, these laws let you write enough independent equations to solve **any** "
                    "linear DC circuit, no matter how many loops or branches it contains."
                ),
                "body_he_md": (
                    "נגד בודד עם סוללה — פשוט: חוק אוהם אחד נותן את הזרם. אבל מעגלים אמיתיים "
                    "בבגרות (שאלון 2 — חשמל) ובהנדסה נדירים כך. חיווט ביתי, מטענים לטלפון "
                    "ולוחות ניסוי — כולם מכילים **לולאות וענפים מרובים** שבהם זרם מתפצל "
                    "בצמתים ומתאחד במקום אחר.\n\n"
                    "כשנגדים מחוברים בצורה שאינה טור טהור או מקביל טהור, חוק אוהם לבד "
                    "לא מספיק לקבוע כל זרם ענף. צריך שיטה שיטתית לכל טופולוגיה.\n\n"
                    "**חוקי קירכהוף** (גוסטב קירכהוף, 1845) מספקים שני עקרונות שימור:\n"
                    "1. **KCL** (חוק הזרם): שימור מטען בכל צומת — זרם נכנס = זרם יוצא.\n"
                    "2. **KVL** (חוק המתח): שימור אנרגיה בכל לולאה סגורה — שינוי מתח נטו = 0.\n\n"
                    "יחד, החוקים מאפשרים לכתוב מספיק משוואות עצמאיות לפתרון **כל** "
                    "מעגל DC לינארי, ללא קשר למספר הלולאות והענפים."
                ),
            },
            {
                "kind": "definition",
                "title_en": "KCL and KVL — Formal Statements",
                "title_he": "KCL ו-KVL — הגדרות פורמליות",
                "body_en_md": (
                    "**KCL (Kirchhoff's Current Law — Junction Rule):**\n"
                    "> The algebraic sum of currents at any node (junction) equals zero.\n"
                    "$$\\sum I_{\\text{in}} = \\sum I_{\\text{out}} \\quad\\text{or}\\quad "
                    "\\sum_{k} I_k = 0$$\n"
                    "Physical basis: charge cannot accumulate at a point in a wire. Every coulomb "
                    "that enters must leave.\n\n"
                    "**KVL (Kirchhoff's Voltage Law — Loop Rule):**\n"
                    "> The algebraic sum of voltage changes around any closed loop equals zero.\n"
                    "$$\\sum V_i = 0 \\quad\\text{(around any closed loop)}$$\n"
                    "Physical basis: a charge completing a loop returns to the same potential — "
                    "no net energy gain.\n\n"
                    "**Sign conventions (critical for Bagrut):**\n"
                    "- **KVL:** Voltage **rises** when crossing a battery from $-$ to $+$ (add $+\\mathcal{E}$). "
                    "Voltage **drops** when crossing a resistor in the direction of assumed current (add $-IR$).\n"
                    "- **KCL:** Choose a sign convention — currents entering a node are positive, leaving are "
                    "negative (or vice versa, but stay consistent).\n\n"
                    "These conventions are arbitrary; consistency within one problem is what matters."
                ),
                "body_he_md": (
                    "**KCL (חוק הזרם — כלל הצמתים):**\n"
                    "> הסכום האלגברי של הזרמים בכל צומת שווה לאפס.\n"
                    "$$\\sum I_{\\text{נכנסים}} = \\sum I_{\\text{יוצאים}} \\quad\\text{או}\\quad "
                    "\\sum_{k} I_k = 0$$\n"
                    "בסיס פיזיקלי: מטען לא יכול להצטבר בנקודה בתוך מוליך. כל קולון "
                    "שנכנס חייב לצאת.\n\n"
                    "**KVL (חוק המתח — כלל הלולאות):**\n"
                    "> הסכום האלגברי של שינויי המתח סביב כל לולאה סגורה שווה לאפס.\n"
                    "$$\\sum V_i = 0 \\quad\\text{(בכל לולאה סגורה)}$$\n"
                    "בסיס פיזיקלי: מטען שמשלים לולאה חוזר לאותו פוטנציאל — "
                    "ללא שינוי אנרגיה נטו.\n\n"
                    "**מוסכמות סימן (קריטי לבגרות):**\n"
                    "- **KVL:** **עלייה** במעבר סוללה מ-$-$ ל-$+$ (הוסף $+\\mathcal{E}$). "
                    "**ירידה** במעבר נגד בכיוון זרם מניח ($-IR$).\n"
                    "- **KCL:** בחרו מוסכמה — זרמים נכנסים חיוביים, יוצאים שליליים "
                    "(או להפך, אך עקביים).\n\n"
                    "המוסכמות שרירותיות; עקביות בתוך בעיה אחת היא מה שחשוב."
                ),
            },
            {
                "kind": "theory",
                "title_en": "Solving Multi-Loop Circuits",
                "title_he": "פתרון מעגלים מרובי לולאות",
                "body_en_md": (
                    "**Systematic procedure for any DC circuit:**\n"
                    "1. **Label all nodes** (junctions where three or more branches meet). Give them names "
                    "(A, B, C…) for clarity in equations.\n"
                    "2. **Assign a current variable** to each branch. Draw an arrow showing the **assumed** "
                    "direction — if wrong, the algebra gives a negative value.\n"
                    "3. **Apply KCL** at each node except one (the last node is redundant). Write "
                    "$\\sum I_{\\text{in}} = \\sum I_{\\text{out}}$.\n"
                    "4. **Apply KVL** around each independent loop. Choose a consistent traversal direction "
                    "(clockwise is common) and apply sign rules for batteries and resistors.\n"
                    "5. **Solve the system** of linear equations (substitution, elimination, or matrix methods).\n"
                    "6. **Interpret negative currents** — magnitude is correct; sign means actual direction "
                    "is opposite to your arrow.\n\n"
                    "**How many equations do you need?**\n"
                    "For a circuit with $n$ nodes and $b$ branches:\n"
                    "- **KCL:** $n - 1$ independent equations (one node is dependent).\n"
                    "- **KVL:** $b - n + 1$ independent loop equations.\n"
                    "- **Total:** $b$ equations for $b$ unknown branch currents — exactly determined.\n\n"
                    "**Mesh vs. node analysis:** Bagrut problems typically use the loop method (KVL + KCL). "
                    "University courses also teach nodal analysis (assigning node voltages), but the physics "
                    "principles are identical."
                ),
                "body_he_md": (
                    "**נוהל שיטתי לכל מעגל DC:**\n"
                    "1. **תייגו כל צומת** (נקודת חיבור של שלושה ענפים ומעלה). תנו שמות "
                    "(A, B, C…) לבהירות במשוואות.\n"
                    "2. **הקצו משתנה זרם** לכל ענף. ציירו חץ ל**כיוון המניח** — "
                    "אם שגוי, החישוב ייתן ערך שלילי.\n"
                    "3. **יישמו KCL** בכל צומת חוץ מאחת (האחרונה מיותרת). "
                    "כתבו $\\sum I_{\\text{נכנסים}} = \\sum I_{\\text{יוצאים}}$.\n"
                    "4. **יישמו KVL** סביב כל לולאה עצמאית. בחרו כיוון מעבר עקבי "
                    "(עם כיוון השעון נפוץ) והחילו כללי סימן לסוללות ונגדים.\n"
                    "5. **פתרו את המערכת** (הצבה, דריכה, או מטריצות).\n"
                    "6. **פרשו זרמים שליליים** — העוצמה נכונה; הסימן = כיוון הפוך לחץ.\n\n"
                    "**כמה משוואות צריך?**\n"
                    "למעגל עם $n$ צמתים ו-$b$ ענפים:\n"
                    "- **KCL:** $n - 1$ משוואות עצמאיות.\n"
                    "- **KVL:** $b - n + 1$ משוואות לולאה עצמאיות.\n"
                    "- **סה\"כ:** $b$ משוואות ל-$b$ זרמי ענף — נקבע במדויק.\n\n"
                    "**ניתוח לולאות מול צמתים:** בבגרות בדרך כלל שיטת לולאות (KVL + KCL). "
                    "באוניברסיטה גם ניתוח צמתים (מתחי צומת), אך עקרונות הפיזיקה זהים."
                ),
            },
            {
                "kind": "worked_example",
                "difficulty": "easy",
                "example_number": 1,
                "title_en": "Worked Example 1 — KCL at a Node",
                "title_he": "דוגמה פתורה 1 — KCL בצומת",
                "body_en_md": (
                    "**Problem:** At a three-branch junction, current $I_1 = 3$ A and $I_2 = 2$ A "
                    "flow **into** the node. Current $I_3$ flows **out**. Find $I_3$.\n\n"
                    "### Move 1: Draw and classify\n"
                    "Sketch the node with arrows: two arrows pointing in ($I_1$, $I_2$), one pointing "
                    "out ($I_3$). This visual step prevents sign errors.\n\n"
                    "### Move 2: Write KCL\n"
                    "By conservation of charge at the node:\n"
                    "$$I_1 + I_2 = I_3$$\n\n"
                    "### Move 3: Substitute and solve\n"
                    "$$I_3 = 3 + 2 = \\boxed{5\\text{ A}}$$\n\n"
                    "### Move 4: Verify\n"
                    "Total in ($5$ A) equals total out ($5$ A) ✓. The positive result confirms $I_3$ "
                    "flows out in the assumed direction.\n\n"
                    "**Key insight:** KCL never involves resistances or voltages — only currents at "
                    "the junction. This makes node problems the fastest warm-up before multi-loop KVL.\n\n"
                    "**Bagrut pattern:** Junction questions often appear as the first sub-question in a "
                    "multi-part electricity problem — solve them in seconds to build confidence."
                ),
                "body_he_md": (
                    "**בעיה:** בצומת של שלושה ענפים, זרמים $I_1 = 3$ A ו-$I_2 = 2$ A "
                    "נכנסים **פנימה**. זרם $I_3$ יוצא **החוצה**. מצאו $I_3$.\n\n"
                    "### צעד 1: שרטוט וסיווג\n"
                    "שרטטו צומת עם חצים: שני חצים פנימה ($I_1$, $I_2$), אחד החוצה ($I_3$). "
                    "שלב ויזואלי זה מונע טעויות סימן.\n\n"
                    "### צעד 2: כתיבת KCL\n"
                    "לפי שימור מטען בצומת:\n"
                    "$$I_1 + I_2 = I_3$$\n\n"
                    "### צעד 3: הצבה ופתרון\n"
                    "$$I_3 = 3 + 2 = \\boxed{5\\text{ A}}$$\n\n"
                    "### צעד 4: אימות\n"
                    "סה\"כ נכנס ($5$ A) = סה\"כ יוצא ($5$ A) ✓. תוצאה חיובית — "
                    "$I_3$ יוצא בכיוון ההנחה.\n\n"
                    "**תובנה:** KCL לא כולל התנגדויות או מתחים — רק זרמים בצומת. "
                    "זה הופך בעיות צומת לחימום המהיר לפני KVL מרובה לולאות.\n\n"
                    "**דפוס בגרות:** שאלות צומת מופיעות לעיתים כסעיף ראשון בבעיה "
                    "רב-חלקית — פתרו אותן תוך שניות לבניית ביטחון."
                ),
            },
            {
                "kind": "checkpoint",
                "title_en": "Stop & Practice",
                "title_he": "עצור ותרגל",
                "body_en_md": "At a node: $I_1=4$ A enters, $I_2=1$ A exits, $I_3=?$ exits. Find $I_3$.",
                "body_he_md": "צומת: $I_1=4$ A נכנס, $I_2=1$ A יוצא, $I_3$ יוצא. מצא $I_3$.",
                "checkpoint_solution_en": (
                    "**Setup:** $I_1 = 4$ A enters; $I_2 = 1$ A and $I_3$ both exit.\n\n"
                    "**KCL:** $I_1 = I_2 + I_3$.\n\n"
                    "**Solve:** $4 = 1 + I_3 \\Rightarrow I_3 = \\boxed{3\\text{ A}}$.\n\n"
                    "**Check:** $1 + 3 = 4$ A out = $4$ A in ✓."
                ),
                "checkpoint_solution_he": (
                    "**הכנה:** $I_1 = 4$ A נכנס; $I_2 = 1$ A ו-$I_3$ יוצאים.\n\n"
                    "**KCL:** $I_1 = I_2 + I_3$.\n\n"
                    "**פתרון:** $4 = 1 + I_3 \\Rightarrow I_3 = \\boxed{3\\text{ A}}$.\n\n"
                    "**בדיקה:** $1 + 3 = 4$ A יוצא = $4$ A נכנס ✓."
                ),
            },
            {
                "kind": "worked_example",
                "difficulty": "medium",
                "example_number": 2,
                "title_en": "Worked Example 2 — KVL in a Single Loop",
                "title_he": "דוגמה פתורה 2 — KVL בלולאה אחת",
                "body_en_md": (
                    "**Problem:** A single loop contains a battery $\\mathcal{E} = 12$ V and two "
                    "series resistors $R_1 = 3\\,\\Omega$, $R_2 = 1\\,\\Omega$. Find the current $I$ "
                    "and the voltage across each resistor.\n\n"
                    "### Move 1: Identify the loop\n"
                    "One current $I$ flows everywhere (series connection). Choose clockwise traversal "
                    "starting at the battery's negative terminal. Label the battery EMF as a rise "
                    "and each resistor as a drop in the direction of $I$.\n\n"
                    "### Move 2: Write KVL\n"
                    "$$\\mathcal{E} - I R_1 - I R_2 = 0$$\n"
                    "$$12 - 3I - 1I = 0 \\Rightarrow 4I = 12 \\Rightarrow I = \\boxed{3\\text{ A}}$$\n\n"
                    "### Move 3: Individual voltages\n"
                    "$$V_{R_1} = IR_1 = 3 \\times 3 = 9\\text{ V}, \\quad "
                    "V_{R_2} = IR_2 = 3 \\times 1 = 3\\text{ V}$$\n\n"
                    "### Move 4: Verify KVL\n"
                    "Battery rise $12$ V = sum of drops $9 + 3 = 12$ V ✓.\n\n"
                    "**Alternative path:** Total resistance $R_1 + R_2 = 4\\,\\Omega$, so "
                    "$I = \\mathcal{E}/R = 12/4 = 3$ A directly. KVL and Ohm's law must agree — "
                    "if they differ, recheck sign conventions.\n\n"
                    "**Note:** This agrees with $I = \\mathcal{E}/(R_1+R_2) = 12/4 = 3$ A — "
                    "KVL on a single loop reduces to Ohm's law.\n\n"
                    "**Power check (optional):** $P_{R_1} = I^2 R_1 = 27$ W, $P_{R_2} = 9$ W, "
                    "battery supplies $P = \\mathcal{E} I = 36$ W. Sum $27 + 9 = 36$ W ✓."
                ),
                "body_he_md": (
                    "**בעיה:** לולאה אחת עם סוללה $\\mathcal{E} = 12$ V ושני נגדים בטור "
                    "$R_1 = 3\\,\\Omega$, $R_2 = 1\\,\\Omega$. מצאו זרם $I$ ומתח על כל נגד.\n\n"
                    "### צעד 1: זיהוי הלולאה\n"
                    "זרם $I$ אחד בכל מקום (חיבור טור). בחרו מעבר עם כיוון השעון "
                    "ממינוס הסוללה. סמנו כ\"א כעלייה וכל נגד כירידה בכיוון $I$.\n\n"
                    "### צעד 2: כתיבת KVL\n"
                    "$$\\mathcal{E} - I R_1 - I R_2 = 0$$\n"
                    "$$12 - 3I - 1I = 0 \\Rightarrow 4I = 12 \\Rightarrow I = \\boxed{3\\text{ A}}$$\n\n"
                    "### צעד 3: מתחים בודדים\n"
                    "$$V_{R_1} = IR_1 = 3 \\times 3 = 9\\text{ V}, \\quad "
                    "V_{R_2} = IR_2 = 3 \\times 1 = 3\\text{ V}$$\n\n"
                    "### צעד 4: אימות KVL\n"
                    "עליית סוללה $12$ V = סכום ירידות $9 + 3 = 12$ V ✓.\n\n"
                    "**דרך חלופית:** התנגדות $R_1 + R_2 = 4\\,\\Omega$, "
                    "לכן $I = \\mathcal{E}/R = 12/4 = 3$ A ישירות. KVL וחוק אוהם חייבים להתאים — "
                    "אם לא, בדקו מוסכמות סימן.\n\n"
                    "**הערה:** מתאים ל-$I = \\mathcal{E}/(R_1+R_2) = 12/4 = 3$ A — "
                    "KVL בלולאה בודדת מתכווץ לחוק אוהם.\n\n"
                    "**בדיקת הספק (אופציונלי):** $P_{R_1} = I^2 R_1 = 27$ W, $P_{R_2} = 9$ W, "
                    "סוללה מספקת $P = \\mathcal{E} I = 36$ W. סכום $27 + 9 = 36$ W ✓."
                ),
            },
            {
                "kind": "checkpoint",
                "title_en": "Stop & Practice",
                "title_he": "עצור ותרגל",
                "body_en_md": "Loop with $\\mathcal{E}=9$ V and three resistors $R_1=R_2=R_3=1\\Omega$ in series. Find $I$.",
                "body_he_md": "לולאה: $\\mathcal{E}=9$ V, שלושה נגדים $1\\Omega$ בסדרה. $I$?",
                "checkpoint_solution_en": (
                    "**KVL (clockwise):** $\\mathcal{E} - IR_1 - IR_2 - IR_3 = 0$.\n\n"
                    "$$9 - I - I - I = 0 \\Rightarrow 3I = 9 \\Rightarrow I = \\boxed{3\\text{ A}}$$\n\n"
                    "**Check:** Total resistance $3\\,\\Omega$; $I = 9/3 = 3$ A ✓. "
                    "Each resistor drops $3$ V; $3 + 3 + 3 = 9$ V ✓."
                ),
                "checkpoint_solution_he": (
                    "**KVL (עם כיוון השעון):** $\\mathcal{E} - IR_1 - IR_2 - IR_3 = 0$.\n\n"
                    "$$9 - I - I - I = 0 \\Rightarrow 3I = 9 \\Rightarrow I = \\boxed{3\\text{ A}}$$\n\n"
                    "**בדיקה:** התנגדות $3\\,\\Omega$; $I = 9/3 = 3$ A ✓. "
                    "כל נגד יורד $3$ V; $3 + 3 + 3 = 9$ V ✓."
                ),
            },
            {
                "kind": "worked_example",
                "difficulty": "hard",
                "example_number": 3,
                "title_en": "Worked Example 3 — Two-Loop Circuit",
                "title_he": "דוגמה פתורה 3 — מעגל דו-לולאות",
                "body_en_md": (
                    "**Circuit:** $\\mathcal{E}_1 = 12$ V (left), $\\mathcal{E}_2 = 6$ V (right), "
                    "$R_1 = 4\\,\\Omega$ (left branch), $R_2 = 2\\,\\Omega$ (middle/shared), "
                    "$R_3 = 6\\,\\Omega$ (right branch). Assign $I_1$ (left), $I_2$ (middle), "
                    "$I_3$ (right).\n\n"
                    "### Move 1: KCL at the top node\n"
                    "$$I_1 = I_2 + I_3$$\n\n"
                    "### Move 2: KVL — left loop (clockwise)\n"
                    "Starting at $\\mathcal{E}_1$ negative terminal:\n"
                    "$$\\mathcal{E}_1 - I_1 R_1 - I_2 R_2 = 0 \\Rightarrow 12 - 4I_1 - 2I_2 = 0$$\n\n"
                    "### Move 3: KVL — right loop (clockwise)\n"
                    "Middle resistor traversed against $I_2$ (rise), then $\\mathcal{E}_2$ (fall), "
                    "then $R_3$:\n"
                    "$$I_2 R_2 - \\mathcal{E}_2 - I_3 R_3 = 0 \\Rightarrow 2I_2 - 6 - 6I_3 = 0$$\n\n"
                    "### Move 4: Substitute and solve\n"
                    "From KCL: $I_1 = I_2 + I_3$. Substitute into left loop:\n"
                    "$$12 - 4(I_2 + I_3) - 2I_2 = 0 \\Rightarrow 12 = 6I_2 + 4I_3 \\quad\\text{(A)}$$\n"
                    "From right loop: $2I_2 - 6I_3 = 6 \\Rightarrow I_2 = 3 + 3I_3 \\quad\\text{(B)}$\n\n"
                    "Substitute (B) into (A): $12 = 6(3 + 3I_3) + 4I_3 = 18 + 22I_3 \\Rightarrow "
                    "I_3 = -3/11 \\approx -0.27$ A.\n"
                    "$I_2 = 3 + 3(-3/11) = 24/11 \\approx 2.18$ A. "
                    "$I_1 = 21/11 \\approx 1.91$ A.\n\n"
                    "**Interpretation:** $I_3 < 0$ means current in the right branch actually flows "
                    "opposite to the assumed arrow — magnitude $0.27$ A is still valid.\n\n"
                    "**Verification:** Substitute all three currents back into both KVL equations to "
                    "confirm both equal zero — always do this on Bagrut for partial credit safety."
                ),
                "body_he_md": (
                    "**מעגל:** $\\mathcal{E}_1 = 12$ V (שמאל), $\\mathcal{E}_2 = 6$ V (ימין), "
                    "$R_1 = 4\\,\\Omega$ (ענף שמאל), $R_2 = 2\\,\\Omega$ (אמצע/משותף), "
                    "$R_3 = 6\\,\\Omega$ (ענף ימין). הקצו $I_1$, $I_2$, $I_3$.\n\n"
                    "### צעד 1: KCL בצומת עליון\n"
                    "$$I_1 = I_2 + I_3$$\n\n"
                    "### צעד 2: KVL — לולאה שמאלית (עם כיוון השעון)\n"
                    "ממינוס $\\mathcal{E}_1$:\n"
                    "$$\\mathcal{E}_1 - I_1 R_1 - I_2 R_2 = 0 \\Rightarrow 12 - 4I_1 - 2I_2 = 0$$\n\n"
                    "### צעד 3: KVL — לולאה ימנית (עם כיוון השעון)\n"
                    "נגד אמצעי נגד כיוון $I_2$ (עלייה), אחר כך $\\mathcal{E}_2$ (ירידה), "
                    "אחר כך $R_3$:\n"
                    "$$I_2 R_2 - \\mathcal{E}_2 - I_3 R_3 = 0 \\Rightarrow 2I_2 - 6 - 6I_3 = 0$$\n\n"
                    "### צעד 4: הצבה ופתרון\n"
                    "מ-KCL: $I_1 = I_2 + I_3$. הצבה בלולאה שמאלית:\n"
                    "$$12 - 4(I_2 + I_3) - 2I_2 = 0 \\Rightarrow 12 = 6I_2 + 4I_3 \\quad\\text{(א)}$$\n"
                    "מלולאה ימנית: $2I_2 - 6I_3 = 6 \\Rightarrow I_2 = 3 + 3I_3 \\quad\\text{(ב)}$\n\n"
                    "הצבת (ב) ב-(א): $12 = 6(3 + 3I_3) + 4I_3 = 18 + 22I_3 \\Rightarrow "
                    "I_3 = -3/11 \\approx -0.27$ A.\n"
                    "$I_2 = 24/11 \\approx 2.18$ A. $I_1 = 21/11 \\approx 1.91$ A.\n\n"
                    "**פרשנות:** $I_3 < 0$ ⇒ זרם בענף ימין זורם **הפוך** לחץ — "
                    "עוצמה $0.27$ A עדיין תקפה.\n\n"
                    "**אימות:** הציבו את שלושת הזרמים חזרה בשתי משוואות KVL "
                    "לוודא ששתיהן מתאפסות — תמיד בבגרות לביטחון ניקוד חלקי."
                ),
            },
            {
                "kind": "method_guide",
                "title_en": "Method Guide — Kirchhoff's Laws",
                "title_he": "מדריך שיטה — חוקי קירכהוף",
                "body_en_md": (
                    "Follow this checklist for every Kirchhoff problem on Bagrut:\n\n"
                    "1. **Draw and label** the circuit. Mark nodes (A, B, C…) and assign branch "
                    "current arrows ($I_1$, $I_2$, …).\n"
                    "2. **Count unknowns:** one current per branch. Count nodes ($n$) and branches ($b$).\n"
                    "3. **Write KCL** at $n - 1$ nodes: $\\sum I_{\\text{in}} = \\sum I_{\\text{out}}$.\n"
                    "4. **Write KVL** for $b - n + 1$ independent loops:\n"
                    "   - Traverse consistently (clockwise recommended).\n"
                    "   - Battery $-$ to $+$: add $+\\mathcal{E}$.\n"
                    "   - Resistor with current: add $-IR$ (drop).\n"
                    "   - Resistor against current: add $+IR$ (rise).\n"
                    "5. **Solve** the linear system. Show substitution steps — partial credit on Bagrut.\n"
                    "6. **Check:** negative current → reverse arrow; verify KVL on each loop with "
                    "computed values.\n\n"
                    "**Time saver:** If the circuit simplifies to series/parallel, use equivalent "
                    "resistance first. Kirchhoff is for when that fails."
                ),
                "body_he_md": (
                    "עקבו אחרי רשימה זו בכל בעיית קירכהוף בבגרות:\n\n"
                    "1. **שרטוט ותיוג.** סמנו צמתים (A, B, C…) והקצו חצי זרם ($I_1$, $I_2$, …).\n"
                    "2. **ספירת נעלמים:** זרם אחד לענף. ספרו צמתים ($n$) וענפים ($b$).\n"
                    "3. **כתבו KCL** ב-$n - 1$ צמתים: $\\sum I_{\\text{נכנסים}} = \\sum I_{\\text{יוצאים}}$.\n"
                    "4. **כתבו KVL** ל-$b - n + 1$ לולאות עצמאיות:\n"
                    "   - מעבר עקבי (עם כיוון השעון מומלץ).\n"
                    "   - סוללה $-$ ל-$+$: $+\\mathcal{E}$.\n"
                    "   - נגד עם זרם: $-IR$ (ירידה).\n"
                    "   - נגד נגד זרם: $+IR$ (עלייה).\n"
                    "5. **פתרו** מערכת לינארית. הציגו שלבי הצבה — ניקוד חלקי בבגרות.\n"
                    "6. **בדקו:** זרם שלילי → הפוך חץ; אמתו KVL בכל לולאה.\n\n"
                    "**חיסכון זמן:** אם המעגל מתפשט לטור/מקביל, השתמשו בהתנגדות שקולה "
                    "קודם. קירכהוף כשזה לא עובד."
                ),
            },
            _exercise_set_section(),
            {
                "kind": "pitfall",
                "title_en": "Common Pitfalls",
                "title_he": "מלכודות נפוצות",
                "body_en_md": (
                    "1. **KVL sign errors:** The most frequent Bagrut mistake. Pick a traversal direction "
                    "and apply $+\\mathcal{E}$ / $-IR$ consistently. Mixing conventions mid-loop gives "
                    "wrong currents that look plausible.\n\n"
                    "2. **Too few or too many equations:** You need exactly $n - 1$ KCL + $b - n + 1$ KVL "
                    "equations. Writing KCL at every node creates a redundant dependent equation.\n\n"
                    "3. **Forgetting internal resistance:** Real batteries have internal resistance $r$. "
                    "Add $-Ir$ as a drop in KVL: $\\mathcal{E} - Ir - IR = 0$.\n\n"
                    "4. **Treating negative current as error:** A negative solved current means your "
                    "arrow was backwards — the magnitude is still correct. Do not restart the problem.\n\n"
                    "5. **Confusing KCL and KVL:** KCL sums **currents** at nodes; KVL sums **voltages** "
                    "around loops. Writing $\\sum I = 0$ around a loop is wrong.\n\n"
                    "**Fix for misconception \"KVL = sum of currents\":** KVL = sum of voltages = 0; "
                    "KCL = sum of currents = 0 at each node."
                ),
                "body_he_md": (
                    "1. **שגיאות סימן ב-KVL:** הטעות הנפוצה ביותר בבגרות. בחרו כיוון מעבר "
                    "והחילו $+\\mathcal{E}$ / $-IR$ עקבית. ערבוב מוסכמות באמצע לולאה "
                    "נותן זרמים שגויים שנראים סבירים.\n\n"
                    "2. **יותר מדי/פחות מדי משוואות:** צריך בדיוק $n - 1$ KCL + $b - n + 1$ KVL. "
                    "KCL בכל צומת יוצר משוואה תלויה מיותרת.\n\n"
                    "3. **שכחת התנגדות פנימית:** לסוללה אמיתית יש $r$. הוסיפו $-Ir$ "
                    "ב-KVL: $\\mathcal{E} - Ir - IR = 0$.\n\n"
                    "4. **זרם שלילי כשגיאה:** זרם שלילי = חץ הפוך — העוצמה נכונה. "
                    "אל תתחילו מחדש.\n\n"
                    "5. **בלבול KCL ו-KVL:** KCL מסכם **זרמים** בצמתים; KVL מסכם **מתחים** "
                    "בלולאות. $\\sum I = 0$ סביב לולאה — שגוי.\n\n"
                    "**תיקון:** KVL = סכום מתחים = 0; KCL = סכום זרמים = 0 בכל צומת."
                ),
            },
            {
                "id": "why_matters",
                "kind": "why_matters",
                "title_en": "Why it matters",
                "title_he": "למה זה חשוב",
                "body_en_md": (
                    "Kirchhoff's laws are the bridge from simple Ohm's-law circuits to real-world "
                    "electrical analysis. Every circuit board, power grid segment, and Bagrut "
                    "multi-loop problem relies on KCL + KVL.\n\n"
                    "**Builds on:**\n"
                    "- `concept:electric_circuits` — Ohm's law, series/parallel equivalents, power $P = IV$.\n"
                    "- `concept:dc_circuits_kirchhoff` — prerequisite circuit vocabulary.\n\n"
                    "**Leads to:**\n"
                    "- `concept:electromagnetic_induction` — time-varying circuits extend KVL with inductors.\n"
                    "- Engineering: nodal/mesh analysis in university circuits courses.\n\n"
                    "**Why it matters for exams:** Bagrut questionnaire 2 regularly includes two-loop "
                    "problems worth 15–20 points. The method (label → KCL → KVL → solve) is graded "
                    "step-by-step — setup errors cost more than arithmetic slips."
                ),
                "body_he_md": (
                    "חוקי קירכהוף הם הגשר ממעגלי חוק אוהם פשוטים לניתוח חשמלי אמיתי. "
                    "כל לוח מעגלים, קטע ברשת חשמל ובעיית בגרות מרובת לולאות "
                    "מסתמכים על KCL + KVL.\n\n"
                    "**מבוסס על:**\n"
                    "- `concept:electric_circuits` — חוק אוהם, שקולי טור/מקביל, הספק $P = IV$.\n"
                    "- `concept:dc_circuits_kirchhoff` — אוצר מילים של מעגלים.\n\n"
                    "**מוביל ל:**\n"
                    "- `concept:electromagnetic_induction` — מעגלים משתנים מרחיבים KVL עם סלילים.\n"
                    "- הנדסה: ניתוח צמתים/לולאות בקורסי מעגלים.\n\n"
                    "**למה חשוב לבחינות:** שאלון 2 בבגרות כולל לעיתים קרובות בעיות "
                    "דו-לולאות בשווי 15–20 נקודות. השיטה (תיוג → KCL → KVL → פתרון) "
                    "מקבלת ניקוד שלבי — שגיאות הכנה עולות יותר מטעויות חשבון."
                ),
            },
            {
                "kind": "before_exam",
                "title_en": "Before the Exam",
                "title_he": "לפני הבחינה",
                "body_en_md": (
                    "**Memorize these four facts:**\n"
                    "- **KCL:** $\\sum I_{\\text{in}} = \\sum I_{\\text{out}}$ at every node.\n"
                    "- **KVL:** $\\sum V = 0$ around every closed loop.\n"
                    "- **Sign rules:** Battery $-$ to $+$ → $+\\mathcal{E}$. Resistor with current → $-IR$.\n"
                    "- **Equation count:** $n - 1$ KCL + $b - n + 1$ KVL = $b$ unknowns.\n\n"
                    "**Quick drill (5 minutes):**\n"
                    "1. Solve one KCL node problem (no resistors).\n"
                    "2. Solve one single-loop KVL problem.\n"
                    "3. Set up (don't need to finish) a two-loop problem: label, KCL, two KVL equations.\n\n"
                    "**Last review:** Say each formula aloud once, then solve one checkpoint without notes."
                ),
                "body_he_md": (
                    "**ארבעה עובדות לזכור:**\n"
                    "- **KCL:** $\\sum I_{\\text{נכנס}} = \\sum I_{\\text{יוצא}}$ בכל צומת.\n"
                    "- **KVL:** $\\sum V = 0$ בכל לולאה סגורה.\n"
                    "- **סימנים:** סוללה $-$ ל-$+$ → $+\\mathcal{E}$. נגד עם זרם → $-IR$.\n"
                    "- **מספר משוואות:** $n - 1$ KCL + $b - n + 1$ KVL = $b$ נעלמים.\n\n"
                    "**תרגול מהיר (5 דקות):**\n"
                    "1. בעיית KCL בצומת (ללא נגדים).\n"
                    "2. KVL בלולאה אחת.\n"
                    "3. הכנת בעיה דו-לולאות: תיוג, KCL, שתי KVL.\n\n"
                    "**חזרה אחרונה:** אמרו כל נוסחה בקול, ופתרו checkpoint אחד בלי רשימות."
                ),
            },
            {
                "kind": "summary",
                "title_en": "Take-away",
                "title_he": "סיכום",
                "body_en_md": (
                    "- **KCL** = conservation of charge at nodes: current in = current out.\n"
                    "- **KVL** = conservation of energy around loops: net voltage change = 0.\n"
                    "- **Method:** label nodes and currents → write $n-1$ KCL + $b-n+1$ KVL → solve.\n"
                    "- **Negative current** = arrow was backwards; magnitude is still valid.\n\n"
                    "**Takeaway:** You should now recognize whether a problem needs KCL alone, KVL alone, "
                    "or a combined system — and set up the equations before reaching for a calculator."
                ),
                "body_he_md": (
                    "- **KCL** = שימור מטען בצמתים: זרם נכנס = זרם יוצא.\n"
                    "- **KVL** = שימור אנרגיה בלולאות: שינוי מתח נטו = 0.\n"
                    "- **שיטה:** תיוג → $n-1$ KCL + $b-n+1$ KVL → פתרון.\n"
                    "- **זרם שלילי** = חץ הפוך; העוצמה תקפה.\n\n"
                    "**מסקנה:** כעת תזהו האם בעיה דורשת KCL בלבד, KVL בלבד, "
                    "או מערכת משולבת — ותכינו משוואות לפני המחשבון. "
                    "תרגלו לפחות בעיה אחת דו-לולאות לפני הבחינה."
                ),
            },
        ],
        "agent_hints": {
            "key_insights": [
                "KCL: current in = current out at every node.",
                "KVL: sum of all voltage rises and drops = 0 around any closed loop.",
                "Battery crossed - to +: voltage rise. Resistor in current direction: voltage drop.",
                "Write n-1 KCL + b-n+1 KVL equations for complete solution.",
            ],
            "common_misconceptions": [
                {
                    "wrong": "KVL = sum of currents",
                    "correction": "KVL = sum of voltages = 0; KCL = sum of currents = 0.",
                    "detect_phrase_en": "KVL current sum",
                    "detect_phrase_he": "KVL זרמים סכום",
                }
            ],
            "skill_atoms_unlocked": [
                "KCL",
                "KVL",
                "multi_loop_circuits",
                "node_analysis",
                "mesh_analysis",
            ],
            "tutor_pacing_hint": "KCL single node first, then KVL single loop, then two-loop system.",
            "next_recommended": ["electrostatics", "electric_circuits"],
        },
        "questions": _build_questions(),
        "est_minutes": 45,
        "author": "cursor-claude-2026",
        "version": 1,
        "level_focus": None,
        "skill_atom_bank": None,
    }


def _exercise_set_section():
    with open(OUT, encoding="utf-8") as f:
        orig = json.load(f)
    for sec in orig["sections"]:
        if sec["kind"] == "exercise_set":
            return sec
    raise ValueError("exercise_set not found")


def _build_questions():
    with open(OUT, encoding="utf-8") as f:
        orig = json.load(f)
    questions = orig["questions"]
    for q in questions:
        ord_ = q["ord"]
        if ord_ in EXPLANATIONS:
            q["explanation_en"] = EXPLANATIONS[ord_]["en"]
            q["explanation_he"] = EXPLANATIONS[ord_]["he"]
    return questions


def validate(lesson):
    errors = []
    for sec in lesson["sections"]:
        kind = sec["kind"]
        if kind not in MIN_WORDS:
            continue
        en_w = word_count(sec.get("body_en_md", ""))
        he_w = word_count(sec.get("body_he_md", ""))
        if en_w < MIN_WORDS[kind]["en"]:
            errors.append(f"{kind} EN: {en_w} words (need {MIN_WORDS[kind]['en']})")
        if he_w < MIN_WORDS[kind]["he"]:
            errors.append(f"{kind} HE: {he_w} words (need {MIN_WORDS[kind]['he']})")
        if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
            errors.append(f"{kind}: weak Hebrew body")
    for q in lesson["questions"]:
        for lang in ("en", "he"):
            w = word_count(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                errors.append(f"Q{q['ord']} expl_{lang}: {w} words (need 80-150)")
    return errors


def main():
    lesson = build_lesson()
    errors = validate(lesson)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {OUT}")
    print("All depth gates passed.")


if __name__ == "__main__":
    main()
