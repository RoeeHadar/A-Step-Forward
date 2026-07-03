#!/usr/bin/env python3
"""Expand ac_circuits.json to MIN_WORDS + 80-150 word explanations."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "scripts" / "seed_data" / "lessons" / "ac_circuits.json"

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
    import re
    if not text:
        return 0
    stripped = re.sub(r"\$\$[\s\S]*?\$\$", " MATH ", text)
    stripped = re.sub(r"\$[^$\n]+\$", " MATH ", stripped)
    stripped = re.sub(r"[#*_`>\[\]()]", " ", stripped)
    return len([w for w in stripped.split() if w])


def hebrew_body_weak(body_he, body_en):
    import re
    he = (body_he or "").strip()
    en = (body_en or "").strip()
    if not he:
        return True
    he_chars = len(re.findall(r"[\u0590-\u05FF]", he))
    lat = len(re.findall(r"[a-zA-Z]{3,}", he))
    ratio = he_chars / (he_chars + lat + 1)
    if word_count(he) / max(word_count(en), 1) < 0.55:
        return True
    if ratio < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


def expl_en(why, think, slip, tip):
    return (
        f"**Why this is correct:**\n{why}\n\n"
        f"**How to think about it:**\n{think}\n\n"
        f"**Common slip:**\n{slip}\n\n"
        f"**Exam tip:**\n{tip}"
    )


def expl_he(why, think, slip, tip):
    return (
        f"**למה זה נכון:**\n{why}\n\n"
        f"**איך לחשוב:**\n{think}\n\n"
        f"**טעות נפוצה:**\n{slip}\n\n"
        f"**טיפ לבחינה:**\n{tip}"
    )


SECTIONS = {
    "intro": {
        "body_en_md": (
            "Direct current (DC) flows in one direction at constant magnitude — like a battery powering a flashlight. "
            "Alternating current (AC) reverses direction periodically, typically 50 times per second in Israel and Europe "
            "or 60 times per second in the United States. The instantaneous voltage and current follow sinusoidal laws:\n\n"
            "$$V(t) = V_0 \\sin(\\omega t), \\quad I(t) = I_0 \\sin(\\omega t - \\phi).$$\n\n"
            "Here $V_0$ and $I_0$ are peak values, $\\omega = 2\\pi f$ is the angular frequency, and $\\phi$ is the phase "
            "difference between voltage and current.\n\n"
            "**Why does the world use AC?**\n"
            "- **Transformers** work only with changing flux (AC). They efficiently step voltage **up** for long-distance "
            "transmission — higher voltage means lower current for the same power, so $I^2R$ line losses drop dramatically — "
            "and step voltage **down** for safe household use.\n"
            "- **Generators** naturally produce AC: a rotating coil in a uniform $\\vec{B}$ field yields "
            "$\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t)$.\n\n"
            "**Key numbers for exams:** Israel/EU mains: 230 V rms at 50 Hz. US mains: 120 V rms at 60 Hz. "
            "Always remember: the number printed on a wall outlet is **RMS**, not peak."
        ),
        "body_he_md": (
            "זרם ישר (DC) זורם בכיוון אחד ובגודל קבוע — כמו סוללה במנורת כיס. "
            "זרם חילופין (AC) מתהפך כיוונו באופן מחזורי, בדרך כלל 50 פעמים בשנייה בישראל ובאירופה "
            "או 60 פעמים בשנייה בארה\"ב. המתח והזרם הרגעיים עוקבים אחר חוק סינוס:\n\n"
            "$$V(t) = V_0 \\sin(\\omega t), \\quad I(t) = I_0 \\sin(\\omega t - \\phi).$$\n\n"
            "כאן $V_0$ ו-$I_0$ הם ערכי הפסגה, $\\omega = 2\\pi f$ היא התדירות הזוויתית, ו-$\\phi$ היא הפרש הפאזה בין מתח לזרם.\n\n"
            "**למה העולם משתמש ב-AC?**\n"
            "- **שנאים** פועלים רק עם שטף מגנטי משתנה (AC). הם מעלים מתח ל**העברה** למרחקים — מתח גבוה "
            "משמעו זרם נמוך לאותו הספק, ולכן אבדי $I^2R$ בקווים יורדים דרמטית — ומורידים מתח לשימוש בטוח בבית.\n"
            "- **גנרטורים** מייצרים AC באופן טבעי: סליל מסתובב בשדה $\\vec{B}$ אחיד נותן "
            "$\\mathcal{E}(t) = NBA\\omega\\sin(\\omega t)$.\n\n"
            "**מספרים חשובים לבחינה:** רשת ישראל/אירופה: 230 V rms ב-50 Hz. ארה\"ב: 120 V rms ב-60 Hz. "
            "תמיד זכרו: המספר על השקע הוא **RMS**, לא פסגה."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Peak value $V_0$ (or $I_0$):** the maximum magnitude reached in one half-cycle of the sine wave. "
            "A 230 V rms outlet has peak $V_0 = 230\\sqrt{2} \\approx 325$ V — dangerous if you confuse the two.\n\n"
            "**RMS (root-mean-square) value:**\n"
            "$$\\boxed{V_{\\text{rms}} = \\frac{V_0}{\\sqrt{2}}, \\qquad I_{\\text{rms}} = \\frac{I_0}{\\sqrt{2}}.}$$\n"
            "The RMS value is the DC-equivalent voltage/current that delivers the **same average power** to a resistor. "
            "That is why appliances are rated in watts at rms voltage.\n\n"
            "**Average power (resistive load):**\n"
            "$$\\bar{P} = V_{\\text{rms}} I_{\\text{rms}} = I_{\\text{rms}}^2 R = \\frac{V_{\\text{rms}}^2}{R}.$$\n"
            "Only resistors dissipate power; inductors and capacitors store and return energy each half-cycle.\n\n"
            "**Transformer ratio (ideal):**\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p}, \\qquad V_p I_p = V_s I_s \\text{ (power conservation).}$$\n\n"
            "**Reactance** (frequency-dependent opposition without dissipation):\n"
            "- Inductive: $X_L = \\omega L$ (increases with $f$).\n"
            "- Capacitive: $X_C = \\dfrac{1}{\\omega C}$ (decreases with $f$).\n\n"
            "**Impedance (RLC series):** $Z = \\sqrt{R^2 + (X_L - X_C)^2}$. Ohm's law for AC: $V_{\\text{rms}} = I_{\\text{rms}} Z$.\n\n"
            "**Phase angle (RLC):** $\\phi = \\arctan[(X_L - X_C)/R]$ — inductive if positive, capacitive if negative."
        ),
        "body_he_md": (
            "**ערך פסגה $V_0$ (או $I_0$):** הגודל המקסימלי במחצית מחזור של הגל הסינוסואידי. "
            "שקע 230 V rms נותן פסגה $V_0 = 230\\sqrt{2} \\approx 325$ V — מסוכן אם מערבבים.\n\n"
            "**ערך RMS (שורש ממוצע ריבועים):**\n"
            "$$\\boxed{V_{\\text{rms}} = \\frac{V_0}{\\sqrt{2}}, \\qquad I_{\\text{rms}} = \\frac{I_0}{\\sqrt{2}}.}$$\n"
            "ערך ה-RMS הוא המתח/זרם שווי-ערך DC שמספק **אותו הספק ממוצע** לנגד. "
            "לכן מכשירים מדורגים בוואט במתח rms.\n\n"
            "**הספק ממוצע (עומס נגדי):**\n"
            "$$\\bar{P} = V_{\\text{rms}} I_{\\text{rms}} = I_{\\text{rms}}^2 R = \\frac{V_{\\text{rms}}^2}{R}.$$\n"
            "רק נגדים מפזרים הספק; סלילים וקבלים מאחסנים ומחזירים אנרגיה.\n\n"
            "**יחס שנאי (אידיאלי):**\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p}, \\qquad V_p I_p = V_s I_s.$$\n\n"
            "**ראקטנס** (התנגדות תלוית-תדירות ללא פיזור):\n"
            "- השראותי: $X_L = \\omega L$ (עולה עם $f$).\n"
            "- קיבולי: $X_C = \\dfrac{1}{\\omega C}$ (יורד עם $f$).\n\n"
            "**אמפדנס (RLC טורי):** $Z = \\sqrt{R^2 + (X_L - X_C)^2}$. חוק אוהם ל-AC: $V_{\\text{rms}} = I_{\\text{rms}} Z$.\n\n"
            "**זווית פאזה (RLC):** $\\phi = \\arctan[(X_L - X_C)/R]$ — השראותי אם חיובי, קיבולי אם שלילי."
        ),
    },
    "theory": {
        "body_en_md": (
            "### RMS (root-mean-square)\n\n"
            "Because $V(t)$ and $I(t)$ oscillate symmetrically about zero, their **time averages** are zero — "
            "yet electrical appliances clearly deliver energy. The RMS value captures the effective magnitude:\n"
            "$$V_{\\text{rms}} = \\frac{V_0}{\\sqrt{2}}.$$\n"
            "A 230 V AC outlet means $V_{\\text{rms}} = 230$ V, so peak $V_0 = 230\\sqrt{2} \\approx 325$ V. "
            "For power, always pair rms voltage with rms current.\n\n"
            "### Transformers\n\n"
            "Two coils wound on a shared iron core. AC in the primary creates a changing flux; by Faraday's law "
            "and mutual induction, an EMF appears in the secondary:\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p}, \\qquad V_p I_p = V_s I_s.$$\n"
            "- **Step-up** ($N_s > N_p$): increases voltage, decreases current. Used at power plants before transmission.\n"
            "- **Step-down** ($N_s < N_p$): decreases voltage, increases current. Used in phone chargers and neighborhood substations.\n\n"
            "**Long-distance transmission:** For fixed power $P = VI$, doubling voltage halves current, "
            "and line loss $P_{\\text{lost}} = I^2 R_{\\text{line}}$ drops by a factor of four.\n\n"
            "### Reactance and Impedance\n\n"
            "- **Inductor:** $X_L = \\omega L$. Opposes changes in current; blocks high frequencies.\n"
            "- **Capacitor:** $X_C = 1/(\\omega C)$. Opposes changes in voltage; blocks DC ($X_C \\to \\infty$ as $f \\to 0$).\n"
            "- **RLC series impedance:** $Z = \\sqrt{R^2 + (X_L - X_C)^2}$. If $X_L > X_C$, the circuit is inductive (current lags voltage).\n\n"
            "### Resonance\n\n"
            "In an RLC series circuit, $X_L = X_C$ at $\\omega_0 = 1/\\sqrt{LC}$, giving minimum impedance $Z = R$ "
            "and maximum current. This is the basis of radio tuning and filter design. "
            "Near resonance, individual component voltages $V_L = IX_L$ and $V_C = IX_C$ can exceed the source voltage "
            "because they are nearly equal and opposite in phase."
        ),
        "body_he_md": (
            "### RMS (שורש ממוצע ריבועים)\n\n"
            "מכיוון ש-$V(t)$ ו-$I(t)$ מתנודדים סביב אפס, **הממוצעים** שלהם אפסים — "
            "ובכל זאת מכשירים חשמליים מספקים אנרגיה. ערך ה-RMS תופס את הגודל האפקטיבי:\n"
            "$$V_{\\text{rms}} = \\frac{V_0}{\\sqrt{2}}.$$\n"
            "שקע 230 V AC משמעו $V_{\\text{rms}} = 230$ V, ולכן פסגה $V_0 = 230\\sqrt{2} \\approx 325$ V. "
            "לחישוב הספק, תמיד צמדו מתח rms עם זרם rms.\n\n"
            "### שנאים\n\n"
            "שני סלילים על ליבת ברזל משותפת. AC בראשוני יוצר שטף משתנה; לפי חוק פרדיי והשראה הדדית, "
            "נוצר כ\"א במשני:\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p}, \\qquad V_p I_p = V_s I_s.$$\n"
            "- **מעלה** ($N_s > N_p$): מגביר מתח, מקטין זרם. בתחנות כוח לפני העברה.\n"
            "- **מוריד** ($N_s < N_p$): מקטין מתח, מגביר זרם. במטענים ותחנות משנה.\n\n"
            "**העברה למרחקים:** ל-$P = VI$ קבוע, הכפלת מתח מחצה זרם, "
            "ואבדן $P_{\\text{אבוד}} = I^2 R_{\\text{קו}}$ יורד פי ארבע.\n\n"
            "### ראקטנס ואמפדנס\n\n"
            "- **סליל:** $X_L = \\omega L$. מתנגד לשינויי זרם; חוסם תדירויות גבוהות.\n"
            "- **קבל:** $X_C = 1/(\\omega C)$. מתנגד לשינויי מתח; חוסם DC ($X_C \\to \\infty$ כש-$f \\to 0$).\n"
            "- **אמפדנס RLC טורי:** $Z = \\sqrt{R^2 + (X_L - X_C)^2}$. אם $X_L > X_C$, המעגל השראותי (זרם מפגר).\n\n"
            "### תהודה\n\n"
            "במעגל RLC טורי, $X_L = X_C$ ב-$\\omega_0 = 1/\\sqrt{LC}$, ולכן $Z = R$ מינימלי וזרם מקסימלי. "
            "זה בסיס לכוונון רדיו ולמסננים. "
            "קרוב לתהודה, מתחים $V_L = IX_L$ ו-$V_C = IX_C$ עלולים לעלות על מתח המקור "
            "כי הם כמעט שווים ובפאזה הפוכה."
        ),
    },
}


WORKED = {
    1: {
        "body_en_md": (
            "**Given:** A laptop charger transformer takes 230 V rms input and outputs 19 V rms. "
            "The primary has 1000 turns. (a) How many turns on the secondary? "
            "(b) If the laptop draws 3 A rms, what is the primary current?\n\n"
            "### Move 1: Identify the transformer type and write the turns ratio.\n"
            "This is a **step-down** transformer ($V_s < V_p$), so $N_s < N_p$.\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p}$$\n\n"
            "### Move 2: Solve for $N_s$.\n"
            "$$N_s = N_p \\cdot \\frac{V_s}{V_p} = 1000 \\cdot \\frac{19}{230} \\approx 83 \\text{ turns.}$$\n\n"
            "### Move 3: Apply power conservation for an ideal transformer: $V_p I_p = V_s I_s$.\n"
            "$$I_p = \\frac{V_s I_s}{V_p} = \\frac{19 \\times 3}{230} \\approx 0.248 \\text{ A.}$$\n\n"
            "### Move 4: Verify the power balance.\n"
            "$$P_{\\text{primary}} = 230 \\times 0.248 = 57.0 \\text{ W}, \\quad "
            "P_{\\text{secondary}} = 19 \\times 3 = 57.0 \\text{ W.} \\checkmark$$\n"
            "The turns ratio $N_s/N_p = 19/230 \\approx 0.083$ matches the voltage ratio exactly.\n\n"
            "**Answers:** $N_s \\approx 83$ turns; $I_p \\approx 0.25$ A. "
            "Note: the primary carries low current (thin wire); the secondary carries high current (thick wire). "
            "Always verify power in equals power out for an ideal transformer before submitting."
        ),
        "body_he_md": (
            "**נתון:** שנאי מטען למחשב נייד: כניסה 230 V rms, יציאה 19 V rms. "
            "בראשוני 1000 ליפופים. (א) כמה ליפופים במשני? "
            "(ב) אם המחשב צורך 3 A rms, מה זרם הראשוני?\n\n"
            "### צעד 1: זיהוי סוג השנאי וכתיבת יחס הליפופים.\n"
            "זהו **שנאי מוריד** ($V_s < V_p$), ולכן $N_s < N_p$.\n"
            "$$\\frac{V_s}{V_p} = \\frac{N_s}{N_p}$$\n\n"
            "### צעד 2: פתרון עבור $N_s$.\n"
            "$$N_s = 1000 \\cdot \\frac{19}{230} \\approx 83 \\text{ ליפופים.}$$\n\n"
            "### צעד 3: שימור הספק בשנאי אידיאלי: $V_p I_p = V_s I_s$.\n"
            "$$I_p = \\frac{19 \\times 3}{230} \\approx 0.248 \\text{ A.}$$\n\n"
            "### צעד 4: בדיקת איזון הספק.\n"
            "$$P_{\\text{ראשוני}} = 230 \\times 0.248 = 57 \\text{ W} = P_{\\text{משני}} \\checkmark$$\n"
            "יחס הליפופים $N_s/N_p = 19/230 \\approx 0.083$ תואם בדיוק ליחס המתחים.\n\n"
            "**תשובות:** $N_s \\approx 83$ ליפופים; $I_p \\approx 0.25$ A. "
            "הראשוני נושא זרם נמוך (חוט דק); המשני זרם גבוה (חוט עבה). "
            "תמיד וודאו שהספק הנכנס שווה ליוצא בשנאי אידיאלי לפני הגשה. "
            "בבגרות, סעיף (ב) על זרם ראשוני נותן נקודות חלקיות גם אם (א) שגוי."
        ),
    },
    2: {
        "body_en_md": (
            "**Given:** An RLC series circuit has $R = 30\\,\\Omega$, $L = 0.1$ H, $C = 100\\,\\mu$F, "
            "connected to 220 V rms at 50 Hz. Find: (a) $X_L$, $X_C$, $Z$; (b) $I_{\\text{rms}}$; "
            "(c) voltage across the resistor.\n\n"
            "### Move 1: Compute angular frequency.\n"
            "Convert the mains frequency to rad/s before calculating reactances.\n"
            "$$\\omega = 2\\pi f = 2\\pi \\times 50 \\approx 314 \\text{ rad/s.}$$\n\n"
            "### Move 2: Calculate reactances.\n"
            "$$X_L = \\omega L = 314 \\times 0.1 = 31.4\\,\\Omega.$$\n"
            "$$X_C = \\frac{1}{\\omega C} = \\frac{1}{314 \\times 100 \\times 10^{-6}} \\approx 31.8\\,\\Omega.$$\n\n"
            "### Move 3: Impedance of the series circuit.\n"
            "$$Z = \\sqrt{R^2 + (X_L - X_C)^2} = \\sqrt{30^2 + (31.4 - 31.8)^2} "
            "= \\sqrt{900 + 0.16} \\approx 30.0\\,\\Omega.$$\n\n"
            "### Move 4: RMS current via Ohm's law with impedance.\n"
            "$$I_{\\text{rms}} = \\frac{V_{\\text{rms}}}{Z} = \\frac{220}{30.0} \\approx 7.33 \\text{ A.}$$\n\n"
            "### Move 5: Voltage across the resistor only.\n"
            "$$V_R = I_{\\text{rms}} \\times R = 7.33 \\times 30 \\approx 220 \\text{ V.}$$\n\n"
            "### Move 6: Compare net reactance to resistance.\n"
            "Since $|X_L - X_C| = 0.4\\,\\Omega \\ll R = 30\\,\\Omega$, the circuit behaves almost like a pure resistor.\n\n"
            "**Insight:** This circuit is near resonance ($X_L \\approx X_C$), so $Z \\approx R$ and "
            "most of the source voltage appears across the resistor. "
            "At exact resonance, $V_L$ and $V_C$ would be much larger than $V_R$ even though $Z = R$."
        ),
        "body_he_md": (
            "**נתון:** מעגל RLC טורי: $R = 30\\,\\Omega$, $L = 0.1$ H, $C = 100\\,\\mu$F, "
            "מחובר ל-220 V rms ב-50 Hz. מצאו: (א) $X_L$, $X_C$, $Z$; (ב) $I_{\\text{rms}}$; "
            "(ג) מתח על הנגד.\n\n"
            "### צעד 1: חישוב תדירות זוויתית.\n"
            "המרו את תדירות הרשת ל-rad/s לפני חישוב הראקטנסים.\n"
            "$$\\omega = 2\\pi \\times 50 \\approx 314 \\text{ rad/s.}$$\n\n"
            "### צעד 2: חישוב ראקטנסים.\n"
            "$$X_L = 314 \\times 0.1 = 31.4\\,\\Omega.$$\n"
            "$$X_C = \\frac{1}{314 \\times 10^{-4}} \\approx 31.8\\,\\Omega.$$\n\n"
            "### צעד 3: אמפדנס המעגל הטורי.\n"
            "$$Z = \\sqrt{30^2 + (31.4-31.8)^2} \\approx 30.0\\,\\Omega.$$\n\n"
            "### צעד 4: זרם rms לפי חוק אוהם עם אמפדנס.\n"
            "$$I_{\\text{rms}} = 220/30.0 \\approx 7.33 \\text{ A.}$$\n\n"
            "### צעד 5: מתח על הנגד בלבד.\n"
            "$$V_R = 7.33 \\times 30 \\approx 220 \\text{ V.}$$\n\n"
            "### צעד 6: השוו ראקטנס נטו להתנגדות.\n"
            "מכיוון ש-$|X_L - X_C| = 0.4\\,\\Omega \\ll R = 30\\,\\Omega$, המעגל מתנהג כמעגל נגדי טהור כמעט.\n\n"
            "**תובנה:** המעגל קרוב לתהודה ($X_L \\approx X_C$), לכן $Z \\approx R$ "
            "ורוב מתח המקור מופיע על הנגד. "
            "בתהודה מדויקת, $V_L$ ו-$V_C$ גדולים מ-$V_R$ למרות ש-$Z = R$. "
            "זוהי תופעה שחוזרת בשאלות בגרות מתקדמות."
        ),
    },
    3: {
        "body_en_md": (
            "**Given:** A power plant generates 10 kW at 250 V rms. Electricity is transmitted over lines "
            "with total resistance $R_{\\text{line}} = 2\\,\\Omega$. A step-up transformer (ratio 1:20) "
            "is used before transmission.\n\n"
            "(a) What is the voltage and current after the step-up transformer?\n"
            "(b) What is the power lost in the lines?\n"
            "(c) What fraction of power is lost?\n"
            "(d) Compare to the case without the transformer.\n\n"
            "### Move 1: After step-up transformer ($N_s/N_p = 20$).\n"
            "First apply the turns ratio to the generator voltage before finding line current.\n"
            "$$V_{\\text{trans}} = 250 \\times 20 = 5000 \\text{ V rms.}$$\n"
            "$$I_{\\text{trans}} = \\frac{P}{V_{\\text{trans}}} = \\frac{10000}{5000} = 2 \\text{ A rms.}$$\n\n"
            "### Move 2: Power lost in transmission lines.\n"
            "$$P_{\\text{lost}} = I^2 R_{\\text{line}} = 2^2 \\times 2 = 8 \\text{ W.}$$\n\n"
            "### Move 3: Fraction of total power lost.\n"
            "$$\\frac{P_{\\text{lost}}}{P_{\\text{total}}} = \\frac{8}{10000} = 0.08\\% \\text{ — negligible!}$$\n\n"
            "### Move 4: Without transformer: transmit at 250 V directly.\n"
            "$$I = \\frac{10000}{250} = 40 \\text{ A.}$$\n"
            "$$P_{\\text{lost}} = 40^2 \\times 2 = 3200 \\text{ W} = 32\\% \\text{ of total!}$$\n\n"
            "### Move 5: Compare loss ratio.\n"
            "The transformer reduces line current by 20×, so loss drops by $20^2 = 400$× — from 3200 W to 8 W.\n\n"
            "**Conclusion:** The step-up transformer reduces losses by a factor of $(20)^2 = 400$. "
            "This is why high-voltage transmission is essential — the $I^2R$ penalty scales with current squared. "
            "Without the transformer, over 30% of generated power would heat the lines uselessly. "
            "Bagrut transmission questions often ask you to compute both scenarios side by side for comparison."
        ),
        "body_he_md": (
            "**נתון:** תחנת כוח מייצרת 10 kW ב-250 V rms. החשמל מועבר בקווים בעלי התנגדות "
            "$R_{\\text{קו}} = 2\\,\\Omega$. שנאי מעלה (יחס 1:20) לפני ההעברה.\n\n"
            "(א) מה המתח והזרם אחרי השנאי המעלה?\n"
            "(ב) כמה הספק אובד בקווים?\n"
            "(ג) מה שבר ההספק האבוד?\n"
            "(ד) השוו לתרחיש ללא שנאי.\n\n"
            "### צעד 1: אחרי שנאי מעלה ($N_s/N_p = 20$).\n"
            "קודם יישמו את יחס הליפופים על מתח הגנרטור לפני מציאת זרם הקו.\n"
            "$$V_{\\text{שנ}} = 250 \\times 20 = 5000 \\text{ V rms.}$$\n"
            "$$I_{\\text{שנ}} = 10000/5000 = 2 \\text{ A rms.}$$\n\n"
            "### צעד 2: הספק אבוד בקווי העברה.\n"
            "$$P_{\\text{אבוד}} = 2^2 \\times 2 = 8 \\text{ W.}$$\n\n"
            "### צעד 3: שבר מההספק הכולל.\n"
            "$$8/10000 = 0.08\\% \\text{ — זניח!}$$\n\n"
            "### צעד 4: ללא שנאי — העברה ב-250 V ישירות.\n"
            "$$I = 10000/250 = 40 \\text{ A.}$$\n"
            "$$P_{\\text{אבוד}} = 40^2 \\times 2 = 3200 \\text{ W} = 32\\%!$$\n\n"
            "### צעד 5: השוו יחס אבדן.\n"
            "השנאי מקטין זרם קו פי 20, ולכן האבדן יורד פי $20^2 = 400$ — מ-3200 W ל-8 W.\n\n"
            "**מסקנה:** שנאי המעלה מקטין אבדן בגורם $(20)^2 = 400$. "
            "לכן העברה במתח גבוה חיונית — קנס $I^2R$ גדל בריבוע הזרם. "
            "ללא השנאי, יותר מ-30% מההספק היה נחם בקווים לחינם. "
            "זו הסיבה שכל רשת חשמל לאומית משתמשת בשנאי מעלה. "
            "בבגרות לעתים מבקשים לחשב את שני התרחישים זה לצד זה להשוואה."
        ),
    },
}

CHECKPOINTS = [
    {
        "checkpoint_solution_en": (
            "**(a) Secondary voltage:** Use the turns ratio directly because the transformer is ideal.\n"
            "$$V_s = V_p \\cdot \\frac{N_s}{N_p} = 110 \\times \\frac{5000}{200} = 110 \\times 25 = 2750 \\text{ V rms.}$$\n"
            "The ratio $N_s/N_p = 25$ confirms this is a step-up transformer.\n\n"
            "**(b) Primary current:** Conserve power ($V_p I_p = V_s I_s$) or use the inverse turns ratio on current.\n"
            "$$I_p = \\frac{V_s I_s}{V_p} = \\frac{2750 \\times 0.5}{110} = 12.5 \\text{ A rms.}$$\n"
            "Check: $I_p/I_s = N_s/N_p = 25$, so $I_p = 0.5 \\times 25 = 12.5$ A. "
            "The primary carries much higher current because voltage is lower — expect thick primary wires in real step-up units at the plant side."
        ),
        "checkpoint_solution_he": (
            "**(א) מתח משני:** השתמשו ביחס הליפופים — השנאי אידיאלי.\n"
            "$$V_s = 110 \\times \\frac{5000}{200} = 110 \\times 25 = 2750 \\text{ V rms.}$$\n"
            "יחס $N_s/N_p = 25$ מאשר שזה שנאי מעלה.\n\n"
            "**(ב) זרם ראשוני:** שימור הספק ($V_p I_p = V_s I_s$) או יחס ליפופים הפוך על הזרם.\n"
            "$$I_p = \\frac{2750 \\times 0.5}{110} = 12.5 \\text{ A rms.}$$\n"
            "בדיקה: $I_p/I_s = 25$, ולכן $I_p = 0.5 \\times 25 = 12.5$ A. "
            "הראשוני נושא זרם גבוה כי המתח נמוך — בשנאי מעלה אמיתי הראשוני עבה יותר."
        ),
    },
    {
        "checkpoint_solution_en": (
            "**(a) Impedance:** Combine resistance and net reactance in quadrature.\n"
            "$$Z = \\sqrt{R^2 + (X_L - X_C)^2} = \\sqrt{40^2 + (50-20)^2} = \\sqrt{1600 + 900} = 50\\,\\Omega.$$\n\n"
            "**(b) RMS current:** Ohm's law with impedance, not just $R$.\n"
            "$$I_{\\text{rms}} = \\frac{V_{\\text{rms}}}{Z} = \\frac{120}{50} = 2.4 \\text{ A.}$$\n\n"
            "**(c) Circuit character:** Since $X_L = 50\\,\\Omega > X_C = 20\\,\\Omega$, the net reactance is inductive. "
            "The current **lags** the source voltage. A common exam follow-up asks for the phase angle "
            "$\\phi = \\arctan[(X_L-X_C)/R] = \\arctan(0.75) \\approx 37°$."
        ),
        "checkpoint_solution_he": (
            "**(א) אמפדנס:** צרפו התנגדות וראקטנס נטו בניצב.\n"
            "$$Z = \\sqrt{40^2 + (50-20)^2} = \\sqrt{2500} = 50\\,\\Omega.$$\n\n"
            "**(ב) זרם rms:** חוק אוהם עם $Z$, לא רק $R$.\n"
            "$$I_{\\text{rms}} = 120/50 = 2.4 \\text{ A.}$$\n\n"
            "**(ג) אופי המעגל:** מכיוון ש-$X_L > X_C$, הראקטנס הנטו השראותי. "
            "הזרם **מפגר** אחרי מתח המקור. שאלת המשך נפוצה: זווית פאזה "
            "$\\phi = \\arctan[(X_L-X_C)/R] \\approx 37°$."
        ),
    },
]

OTHER_SECTIONS = {
    "method_guide": {
        "body_en_md": (
            "| Problem type | Key formula | Watch out for |\n"
            "|---|---|---|\n"
            "| Find peak from rms | $V_0 = V_{\\text{rms}}\\sqrt{2}$ | 230 V outlet = rms, not peak |\n"
            "| Find rms from peak | $V_{\\text{rms}} = V_0/\\sqrt{2}$ | Applies to current too |\n"
            "| Average power (resistive) | $\\bar{P} = V_{\\text{rms}} I_{\\text{rms}} = I^2R = V^2/R$ | Use rms values, not peak |\n"
            "| Transformer: find $V_s$ | $V_s = V_p \\cdot (N_s/N_p)$ | Transformer needs AC |\n"
            "| Transformer: find $I_s$ | $I_s = I_p \\cdot (N_p/N_s)$ | Current is inverse of voltage ratio |\n"
            "| RLC impedance | $Z = \\sqrt{R^2 + (X_L-X_C)^2}$ | $X_L = \\omega L$, $X_C = 1/(\\omega C)$ |\n"
            "| RLC current | $I_{\\text{rms}} = V_{\\text{rms}}/Z$ | Ohm's law with $Z$ |\n"
            "| Resonance frequency | $\\omega_0 = 1/\\sqrt{LC}$, $f_0 = \\omega_0/(2\\pi)$ | At resonance: $Z = R$ (minimum) |\n"
            "| Transmission loss | $P_{\\text{lost}} = I^2 R_{\\text{line}}$ | Use transmission line current |\n\n"
            "**Decision tree for Bagrut-style problems:**\n"
            "1. **Transformer problem?** → Label step-up or step-down, write $N_s/N_p$ ratio, then apply power conservation.\n"
            "2. **Pure resistive AC load?** → Use rms values directly in $\\bar{P} = VI$.\n"
            "3. **RLC circuit?** → First compute $\\omega = 2\\pi f$, then $X_L$, $X_C$, then $Z$, finally $I = V/Z$.\n"
            "4. **Transmission problem?** → Find line current from $P = VI$ at the **transmission** voltage, then $P_{\\text{lost}} = I^2 R_{\\text{line}}$."
        ),
        "body_he_md": (
            "| סוג בעיה | נוסחה מפתח | שימו לב |\n"
            "|---|---|---|\n"
            "| פסגה מ-rms | $V_0 = V_{\\text{rms}}\\sqrt{2}$ | 230V בשקע = rms, לא פסגה |\n"
            "| rms מפסגה | $V_{\\text{rms}} = V_0/\\sqrt{2}$ | תקף גם לזרם |\n"
            "| הספק ממוצע (נגדי) | $\\bar{P} = V_{\\text{rms}} I_{\\text{rms}} = I^2R$ | ערכי rms, לא פסגה |\n"
            "| שנאי: מציאת $V_s$ | $V_s = V_p \\cdot (N_s/N_p)$ | שנאי דורש AC |\n"
            "| שנאי: מציאת $I_s$ | $I_s = I_p \\cdot (N_p/N_s)$ | זרם הפוך ממתח |\n"
            "| אמפדנס RLC | $Z = \\sqrt{R^2 + (X_L-X_C)^2}$ | $X_L = \\omega L$, $X_C = 1/(\\omega C)$ |\n"
            "| זרם RLC | $I_{\\text{rms}} = V_{\\text{rms}}/Z$ | חוק אוהם עם $Z$ |\n"
            "| תדירות תהודה | $\\omega_0 = 1/\\sqrt{LC}$ | בתהודה: $Z = R$ (מינימום) |\n"
            "| אבדן בקווים | $P_{\\text{אבוד}} = I^2 R_{\\text{קו}}$ | השתמשו בזרם הקו |\n\n"
            "**עץ החלטות לבעיות בסגנון בגרות:**\n"
            "1. **בעיית שנאי?** → סמנו מעלה/מוריד, כתבו יחס $N_s/N_p$, ואז שימור הספק.\n"
            "2. **עומס AC נגדי טהור?** → ערכי rms ישירות ב-$\\bar{P} = VI$.\n"
            "3. **מעגל RLC?** → קודם $\\omega = 2\\pi f$, אחר כך $X_L$, $X_C$, $Z$, ולבסוף $I = V/Z$.\n"
            "4. **בעיית העברה?** → מצאו זרם קו מ-$P = VI$ ב**מתח ההעברה**, ואז $P_{\\text{אבוד}} = I^2 R_{\\text{קו}}$."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Peak vs. RMS.** A wall outlet labeled 230 V (or 120 V in the US) is **RMS**. "
            "Peak is $V_0 = V_{\\text{rms}}\\sqrt{2} \\approx 325$ V. Using peak in a power formula doubles the correct answer.\n"
            "2. **Average power uses rms, not peak.** $\\bar{P} = V_{\\text{rms}} I_{\\text{rms}}$, **not** $V_0 I_0$. "
            "The product $V_0 I_0$ would give twice the correct average power for a sinusoid.\n"
            "3. **Transformers require AC.** DC produces constant flux → no changing flux → no induced EMF in the secondary. "
            "This is a conceptual question that appears on almost every Bagrut electricity section.\n"
            "4. **Power conservation in transformers.** For an ideal transformer, $V_p I_p = V_s I_s$. "
            "If voltage steps up, current steps down — never both increase.\n"
            "5. **Reactance direction with frequency.** $X_C = 1/(\\omega C)$ **decreases** as frequency rises (capacitors pass high $f$). "
            "$X_L = \\omega L$ **increases** with frequency (inductors block high $f$).\n"
            "6. **Impedance is not simply $R + X_L + X_C$.** Reactances combine as $X_L - X_C$ inside the square root, "
            "because they can partially cancel at resonance.\n"
            "7. **Transmission current uses the high-voltage side.** After step-up, use the **transmission** voltage "
            "to find $I$, not the generator's low voltage."
        ),
        "body_he_md": (
            "1. **פסגה לעומת RMS.** שקע שמסומן 230 V (או 120 V בארה\"ב) הוא **RMS**. "
            "פסגה: $V_0 = V_{\\text{rms}}\\sqrt{2} \\approx 325$ V. שימוש בפסגה בנוסחת הספק מכפיל את התשובה.\n"
            "2. **הספק ממוצע עם rms, לא פסגה.** $\\bar{P} = V_{\\text{rms}} I_{\\text{rms}}$, **לא** $V_0 I_0$. "
            "מכפלת הפסגות נותנת פי שניים מההספק הנכון.\n"
            "3. **שנאים דורשים AC.** DC = שטף קבוע → אין שינוי → אין כ\"א מושרה במשני. "
            "שאלה מושגית שחוזרת בכמעט כל שאלון חשמל בבגרות.\n"
            "4. **שימור הספק בשנאי.** $V_p I_p = V_s I_s$. אם מתח עולה, זרם יורד — לעולם לא שניהם עולים.\n"
            "5. **כיוון ראקטנס עם תדירות.** $X_C$ **יורד** כש-$f$ עולה (קבלים מעבירים תדירות גבוהה). "
            "$X_L$ **עולה** עם $f$ (סלילים חוסמים תדירות גבוהה).\n"
            "6. **אמפדנס אינו $R + X_L + X_C$.** ראקטנסים מתחברים כ-$X_L - X_C$ בתוך השורש, "
            "כי בתהודה הם מתבטלים חלקית.\n"
            "7. **זרם העברה משתמש במתח הגבוה.** אחרי שנאי מעלה, מצאו $I$ לפי **מתח ההעברה**, לא מתח הגנרטור הנמוך."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "AC circuits connect the physics of **electromagnetic induction** to the technology that powers modern civilization. "
            "Every time you plug in a charger, flip a light switch, or charge a phone wirelessly, you rely on sinusoidal AC, "
            "transformers, and the $I^2R$ logic of high-voltage transmission.\n\n"
            "**Builds on:**\n"
            "- `concept:electromagnetic_induction` — Faraday's law explains both generators and transformers.\n"
            "- `concept:trigonometry_identities` — sinusoidal $V(t)$ and phase angles require trig fluency.\n"
            "- `concept:dc_circuits_kirchhoff` — Ohm's law extends to $V = IZ$ with impedance replacing resistance.\n\n"
            "**Why it matters for exams:** Bagrut questionnaire 2 (electricity) routinely combines transformer ratios, "
            "RMS power calculations, and transmission-loss comparisons in multi-part questions worth 15–20 points. "
            "University intro physics treats RLC resonance and power factor as gateway topics for engineering circuits."
        ),
        "body_he_md": (
            "מעגלי AC מחברים את הפיזיקה של **השראה אלקטרומגנטית** לטכנולוגיה שמזינה את הציוויליזציה המודרנית. "
            "בכל פעם שמחברים מטען, מדליקים אור או טוענים טלפון — מסתמכים על AC סינוסואידי, "
            "שנאים, ולוגיקת $I^2R$ של העברה במתח גבוה.\n\n"
            "**מבוסס על:**\n"
            "- `concept:electromagnetic_induction` — חוק פרדיי מסביר גנרטורים ושנאים.\n"
            "- `concept:trigonometry_identities` — $V(t)$ סינוסואידי וזוויות פאזה דורשים שליטה בטריגונומטריה.\n"
            "- `concept:dc_circuits_kirchhoff` — חוק אוהם מתרחב ל-$V = IZ$ עם אמפדנס במקום התנגדות.\n\n"
            "**למה זה חשוב לבחינות:** שאלון 2 בבגרות (חשמל) משלב שגרה יחסי שנאים, "
            "חישובי הספק RMS והשוואות אבדן העברה בשאלות רב-סעיפיות של 15–20 נקודות. "
            "בפיזיקה אוניברסיטאית, תהודת RLC וגורם הספק הם שער להנדסת מעגלים."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Must-know formulas:**\n"
            "$$V_{\\text{rms}} = \\frac{V_0}{\\sqrt{2}}, \\quad \\bar{P} = V_{\\text{rms}} I_{\\text{rms}}, "
            "\\quad \\frac{V_s}{V_p} = \\frac{N_s}{N_p}, \\quad V_p I_p = V_s I_s.$$\n"
            "$$X_L = \\omega L, \\quad X_C = \\frac{1}{\\omega C}, "
            "\\quad Z = \\sqrt{R^2 + (X_L - X_C)^2}, \\quad \\omega_0 = \\frac{1}{\\sqrt{LC}}.$$\n\n"
            "**Exam strategy:**\n"
            "- Always label the transformer type (step-up or step-down) before calculating.\n"
            "- For AC power: confirm whether the load is purely resistive (simple $P=VI$) or RLC (find $Z$ first).\n"
            "- In transmission problems: step-up first → find $I$ at high voltage → compute $P_{\\text{lost}} = I^2 R_{\\text{line}}$.\n"
            "- Check units: $V$ in volts, $I$ in amperes, $P$ in watts, $\\omega$ in rad/s, $L$ in henries, $C$ in farads.\n\n"
            "**Red flags in your answer:**\n"
            "- Peak voltage where rms is needed (or vice versa).\n"
            "- Primary current larger than secondary in a step-up transformer.\n"
            "- Adding reactances instead of using $X_L - X_C$ inside the impedance formula."
        ),
        "body_he_md": (
            "**נוסחאות חובה:**\n"
            "$$V_{\\text{rms}} = V_0/\\sqrt{2}, \\quad \\bar{P} = V_{\\text{rms}} I_{\\text{rms}}, "
            "\\quad V_s/V_p = N_s/N_p, \\quad V_p I_p = V_s I_s.$$\n"
            "$$X_L = \\omega L, \\quad X_C = 1/(\\omega C), "
            "\\quad Z = \\sqrt{R^2+(X_L-X_C)^2}, \\quad \\omega_0 = 1/\\sqrt{LC}.$$\n\n"
            "**אסטרטגיית בחינה:**\n"
            "- תמיד סמנו סוג שנאי (מעלה/מוריד) לפני החישוב.\n"
            "- הספק AC: וודאו אם העומס נגדי טהור ($P=VI$) או RLC (קודם $Z$).\n"
            "- בעיות העברה: שנאי מעלה → $I$ במתח גבוה → $P_{\\text{אבוד}} = I^2 R_{\\text{קו}}$.\n"
            "- בדקו יחידות: V, A, W, rad/s, H, F.\n\n"
            "**דגלים אדומים:**\n"
            "- מתח פסגה במקום rms (או להפך).\n"
            "- זרם ראשוני גדול ממשני בשנאי מעלה.\n"
            "- חיבור ראקטנסים במקום $X_L - X_C$ בנוסחת האמפדנס.\n"
            "- שכחת המרת Hz ל-rad/s לפני חישוב $X_L$ או $X_C$."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **AC basics:** $V(t) = V_0\\sin(\\omega t)$ alternates direction at frequency $f$; $\\omega = 2\\pi f$.\n"
            "- **RMS:** $V_{\\text{rms}} = V_0/\\sqrt{2}$ — the value printed on outlets; use it for all power calculations.\n"
            "- **Average power:** $\\bar{P} = V_{\\text{rms}} I_{\\text{rms}} = I^2_{\\text{rms}} R$ on resistive loads.\n"
            "- **Transformers (AC only):** $V_s/V_p = N_s/N_p$; power conserved: $V_p I_p = V_s I_s$.\n"
            "- **Transmission:** High $V$ → low $I$ → low $I^2 R$ loss; losses scale as $(N_s/N_p)^2$ when stepping up.\n"
            "- **Reactance:** $X_L = \\omega L$ (inductive), $X_C = 1/(\\omega C)$ (capacitive).\n"
            "- **Impedance:** $Z = \\sqrt{R^2 + (X_L-X_C)^2}$; Ohm's law: $I_{\\text{rms}} = V_{\\text{rms}}/Z$.\n"
            "- **Resonance:** At $\\omega_0 = 1/\\sqrt{LC}$, $X_L = X_C$ and $Z_{\\min} = R$."
        ),
        "body_he_md": (
            "- **יסודות AC:** $V(t) = V_0\\sin(\\omega t)$ מתחלף בתדירות $f$; $\\omega = 2\\pi f$.\n"
            "- **RMS:** $V_{\\text{rms}} = V_0/\\sqrt{2}$ — המספר על השקע; השתמשו בו לכל חישובי הספק.\n"
            "- **הספק ממוצע:** $\\bar{P} = V_{\\text{rms}} I_{\\text{rms}} = I^2_{\\text{rms}} R$ בעומס נגדי.\n"
            "- **שנאים (AC בלבד):** $V_s/V_p = N_s/N_p$; שימור: $V_p I_p = V_s I_s$.\n"
            "- **העברה:** $V$ גבוה → $I$ נמוך → אבדן $I^2 R$ נמוך.\n"
            "- **ראקטנס:** $X_L = \\omega L$, $X_C = 1/(\\omega C)$.\n"
            "- **אמפדנס:** $Z = \\sqrt{R^2+(X_L-X_C)^2}$; $I_{\\text{rms}} = V_{\\text{rms}}/Z$.\n"
            "- **תהודה:** ב-$\\omega_0 = 1/\\sqrt{LC}$, $Z_{\\min} = R$."
        ),
    },
}

QUESTION_EXPLANATIONS = {
    1: {
        "explanation_en": expl_en(
            "$V_0 = V_{\\text{rms}}\\sqrt{2} = 120 \\times 1.414 \\approx 170$ V. "
            "The outlet rating is always RMS because that is the effective value that delivers the same heating power as DC.",
            "Start by identifying what the stem gives: 120 V **rms**. The peak is larger by a factor of $\\sqrt{2}$. "
            "Multiply and compare to the four options — 170 V is the only reasonable peak.",
            "Choosing 120 V means treating rms as peak — the most common AC mistake. "
            "Choosing 240 V doubles rms instead of multiplying by $\\sqrt{2}$.",
            "Memorize: Israeli outlet 230 V rms → peak ≈ 325 V; US 120 V rms → peak ≈ 170 V. "
            "Bagrut often asks this as a warm-up MCQ before harder transformer parts.",
        ),
        "explanation_he": expl_he(
            "$V_0 = V_{\\text{rms}}\\sqrt{2} = 120 \\times 1.414 \\approx 170$ V. "
            "דירוג השקע הוא תמיד RMS כי זה הערך האפקטיבי שמספק אותו הספק חימום כמו DC.",
            "זהו מה שנתון: 120 V **rms**. הפסגה גדולה בגורם $\\sqrt{2}$. "
            "הכפילו והשוו לאפשרויות — 170 V היא הפסגה הסבירה היחידה.",
            "בחירה ב-120 V = התייחסות ל-rms כפסגה — הטעות הנפוצה ביותר ב-AC. "
            "בחירה ב-240 V = הכפלת rms במקום $\\sqrt{2}$.",
            "שימו לב: שקע ישראלי 230 V rms → פסגה ≈ 325 V; ארה\"ב 120 V rms → פסגה ≈ 170 V. "
            "בבגרות זו לעתים שאלת פתיחה לפני חלקי שנאי.",
        ),
    },
    2: {
        "explanation_en": expl_en(
            "A transformer operates via **mutual induction**: AC current in the primary coil creates a changing magnetic flux "
            "in the iron core, which by Faraday's law induces an EMF in the secondary coil.",
            "Ask: what physical process links two coils without direct electrical contact? "
            "Only changing flux can induce EMF — Ohm's law describes current in a conductor, not induction between coils.",
            "Selecting Ohm's law confuses circuit analysis with electromagnetic induction. "
            "Conservation of charge is always true but does not explain voltage transformation.",
            "Bagrut conceptual items often pair 'transformer + DC' as a trap. "
            "If flux is constant (DC), secondary EMF is zero regardless of turns ratio.",
        ),
        "explanation_he": expl_he(
            "שנאי פועל באמצעות **השראה הדדית**: זרם AC בראשוני יוצר שטף מגנטי משתנה בליבה, "
            "שלפי חוק פרדיי משרה כ\"א במשני.",
            "שאלו: איזה תהליך פיזיקלי מקשר שני סלילים ללא מגע חשמלי ישיר? "
            "רק שטף משתנה משרה כ\"א — חוק אוהם מתאר זרם במוליך, לא השראה בין סלילים.",
            "בחירה בחוק אוהם מערבבת ניתוח מעגל עם השראה אלקטרומגנטית. "
            "שימור מטען תמיד נכון אך לא מסביר שינוי מתח.",
            "שאלות מושגיות בבגרות משלבות 'שנאי + DC' כמלכודת. "
            "אם השטף קבוע (DC), כ\"א במשני אפס ללא קשר ליחס ליפופים.",
        ),
    },
    3: {
        "explanation_en": expl_en(
            "For a purely resistive heater, average power is $\\bar{P} = V_{\\text{rms}} I_{\\text{rms}}$, "
            "so $I_{\\text{rms}} = P / V_{\\text{rms}} = 1500 / 230 \\approx 6.52$ A.",
            "The heater rating (1500 W) is average power at the stated rms voltage. "
            "Rearrange $P = VI$ directly — no impedance needed because a heating element is resistive.",
            "Using peak voltage (230$\\sqrt{2}$) in the denominator gives ~4.6 A — too small. "
            "Using $P = V_0 I_0$ without the rms correction doubles the current incorrectly.",
            "Always check: does the device convert power to heat? Then $P = VI$ with rms values. "
            "Show units: A = W/V. Bagrut expects 2–3 significant figures.",
        ),
        "explanation_he": expl_he(
            "לתנור נגדי טהור, $\\bar{P} = V_{\\text{rms}} I_{\\text{rms}}$, "
            "ולכן $I_{\\text{rms}} = 1500 / 230 \\approx 6.52$ A.",
            "דירוג התנור (1500 W) הוא הספק ממוצע במתח rms הנתון. "
            "ארגנו מחדש $P = VI$ ישירות — אין צורך באמפדנס כי אלמנט חימום הוא נגדי.",
            "שימוש במתח פסגה (230$\\sqrt{2}$) במכנה נותן ~4.6 A — קטן מדי. "
            "שימוש ב-$P = V_0 I_0$ ללא rms מכפיל את הזרם.",
            "בדקו: האם המכשיר ממיר הספק לחום? אז $P = VI$ עם rms. "
            "הציגו יחידות: A = W/V. בבגרות מצפים ל-2–3 ספרות משמעותיות.",
        ),
    },
    4: {
        "explanation_en": expl_en(
            "$V_s = V_p \\cdot (N_s/N_p) = 12 \\times (1000/100) = 12 \\times 10 = 120$ V. "
            "More secondary turns than primary turns means step-up: voltage increases by the turns ratio.",
            "Identify step-up ($N_s > N_p$) so voltage must **rise**. "
            "The ratio $N_s/N_p = 10$, so multiply primary voltage by 10. "
            "1.2 V would be step-down; 1200 V would use ratio 100.",
            "Inverting the ratio ($N_p/N_s$) gives 1.2 V — a classic transformer error. "
            "Choosing 12 V ignores the turns entirely.",
            "Write $V_s/V_p = N_s/N_p$ on your formula sheet and circle whether $N_s > N_p$ (step-up) "
            "before calculating. Bagrut often uses round ratios like 10:1 or 20:1.",
        ),
        "explanation_he": expl_he(
            "$V_s = V_p \\cdot (N_s/N_p) = 12 \\times 10 = 120$ V. "
            "יותר ליפופים במשני = שנאי מעלה: המתח עולה לפי יחס הליפופים.",
            "זהו שנאי מעלה ($N_s > N_p$) ולכן המתח **עולה**. "
            "יחס $N_s/N_p = 10$, הכפילו את מתח הראשוני ב-10. "
            "1.2 V = הורדה; 1200 V = יחס 100.",
            "היפוך היחס ($N_p/N_s$) נותן 1.2 V — טעות קלאסית. "
            "בחירה ב-12 V מתעלמת מהליפופים.",
            "כתבו $V_s/V_p = N_s/N_p$ וסמנו אם $N_s > N_p$ (מעלה) לפני החישוב. "
            "בבגרות משתמשים לעתים קרובות ביחסים עגולים כמו 10:1 או 20:1. "
            "בדקו שהתשובה הגיונית: מעלה → מתח עולה.",
        ),
    },
    5: {
        "explanation_en": expl_en(
            "After step-up: $V_{\\text{line}} = 10\\,\\text{kV} \\times 100 = 1\\,\\text{MV}$, "
            "$I_{\\text{line}} = P/V = 5\\times10^6 / 10^6 = 5$ A. "
            "Line loss: $P_{\\text{lost}} = I^2 R = 25 \\times 10 = 250$ W. "
            "Efficiency $\\approx (5\\times10^6 - 250)/(5\\times10^6) = 99.995\\%$.",
            "Follow the power path: generator → step-up → transmission line. "
            "Use the **high** transmission voltage to find line current, then $I^2R$ for losses. "
            "Compare to sending 5 MW at 10 kV directly ($I = 500$ A, loss = 2.5 MW).",
            "Using generator voltage (10 kV) for line current after step-up gives $I = 500$ A — "
            "a 100× error in loss. Forgetting to square current in $I^2R$ is another frequent slip.",
            "Multi-part transmission questions are Bagrut 5-point staples. "
            "Label each stage and state which voltage you use for $P = VI$.",
        ),
        "explanation_he": expl_he(
            "אחרי מעלה: $V_{\\text{קו}} = 10\\,\\text{kV} \\times 100 = 1\\,\\text{MV}$, "
            "$I_{\\text{קו}} = 5\\times10^6 / 10^6 = 5$ A. "
            "אבדן: $P_{\\text{אבוד}} = 25 \\times 10 = 250$ W. "
            "יעילות $\\approx 99.995\\%$.",
            "עקבו אחר מסלול ההספק: גנרטור → מעלה → קו. "
            "השתמשו ב**מתח ההעברה** הגבוה למציאת זרם הקו, ואז $I^2R$ לאבדן. "
            "השוו לשליחת 5 MW ב-10 kV ישירות ($I = 500$ A, אבדן = 2.5 MW).",
            "שימוש במתח הגנרטור (10 kV) אחרי מעלה נותן $I = 500$ A — "
            "טעות פי 100 באבדן. שכחת הריבוע ב-$I^2R$ שגיאה נפוצה נוספת.",
            "שאלות העברה רב-סעיפיות הן מרכיב קבוע ב-5 יח\"ל. "
            "סמנו כל שלב וציינו באיזה מתח משתמשים ב-$P = VI$.",
        ),
    },
    6: {
        "explanation_en": expl_en(
            "$\\omega = 2\\pi \\times 50 \\approx 314$ rad/s. "
            "$X_L = 31.4\\,\\Omega$, $X_C = 12.7\\,\\Omega$. "
            "$Z = \\sqrt{400 + (18.7)^2} \\approx 27.4\\,\\Omega$, $I \\approx 3.65$ A. "
            "$\\bar{P} = I^2 R \\approx 267$ W. "
            "$\\omega_0 = 1/\\sqrt{LC} = 200$ rad/s, $f_0 \\approx 31.8$ Hz.",
            "RLC problems have a fixed pipeline: $\\omega$ → reactances → impedance → current → power on $R$ only. "
            "Operating frequency (50 Hz) differs from resonance (31.8 Hz), so $X_L > X_C$ and the circuit is inductive.",
            "Using $Z = R + X_L + X_C$ instead of $\\sqrt{R^2+(X_L-X_C)^2}$ inflates impedance. "
            "Computing power as $VI$ without noting only $R$ dissipates overcounts — use $\\bar{P} = I^2R$.",
            "Show all intermediate values; partial credit is generous on open RLC items. "
            "Unit check: $X_L$ and $X_C$ must be in ohms before combining.",
        ),
        "explanation_he": expl_he(
            "$\\omega \\approx 314$ rad/s. $X_L = 31.4\\,\\Omega$, $X_C = 12.7\\,\\Omega$. "
            "$Z \\approx 27.4\\,\\Omega$, $I \\approx 3.65$ A. $\\bar{P} \\approx 267$ W. "
            "$f_0 \\approx 31.8$ Hz.",
            "לבעיות RLC יש סדר קבוע: $\\omega$ → ראקטנסים → אמפדנס → זרם → הספק על $R$ בלבד. "
            "תדירות העבודה (50 Hz) שונה מתהודה (31.8 Hz), ולכן $X_L > X_C$ והמעגל השראותי.",
            "שימוש ב-$Z = R + X_L + X_C$ במקום $\\sqrt{R^2+(X_L-X_C)^2}$ מנפח אמפדנס. "
            "חישוב $P = VI$ בלי לציין שרק $R$ מפזר — שגוי; $\\bar{P} = I^2R$.",
            "הציגו ערכי ביניים; נקודות חלקיות נדיבות בשאלות RLC פתוחות. "
            "בדיקת יחידות: $X_L$ ו-$X_C$ חייבים להיות ב-Ω לפני צירוף.",
        ),
    },
    7: {
        "explanation_en": expl_en(
            "$V_0 = V_{\\text{rms}}\\sqrt{2} = 120\\sqrt{2} \\approx 170$ V. "
            "This matches the MCQ version of the same concept — peak exceeds rms by factor $\\sqrt{2}$.",
            "The stem says **rms** explicitly. Multiply by $\\sqrt{2} \\approx 1.414$. "
            "Sanity check: peak must be greater than 120 V but less than 240 V.",
            "Answering 120 confuses peak with rms. Answering 240 uses $2\\times$ instead of $\\sqrt{2}\\times$.",
            "Short-answer items require the numeric value only, but show the formula in working for partial credit. "
            "170 V (or 169 V) is accepted; round to 3 significant figures.",
        ),
        "explanation_he": expl_he(
            "$V_0 = 120\\sqrt{2} \\approx 170$ V. "
            "זהה לגרסת ה-MCQ — פסגה גדולה מ-rms בגורם $\\sqrt{2}$.",
            "השאלה אומרת **rms** במפורש. הכפילו ב-$\\sqrt{2} \\approx 1.414$. "
            "בדיקה: פסגה חייבת להיות גדולה מ-120 V וקטנה מ-240 V.",
            "תשובה 120 = בלבול פסגה עם rms. תשובה 240 = $2\\times$ במקום $\\sqrt{2}\\times$.",
            "בשאלה קצרה מספיק הערך המספרי, אך הציגו נוסחה בדרך עבודה לנקודות חלקיות. "
            "170 V (או 169 V) מתקבל; עגלו ל-3 ספרות משמעותיות. "
            "זו אותה נוסחה כמו בשאלת ה-MCQ — תרגלו את שני הפורמטים.",
        ),
    },
    8: {
        "explanation_en": expl_en(
            "$I_{\\text{rms}} = P / V_{\\text{rms}} = 1000 / 230 \\approx 4.35$ A. "
            "A resistive heater converts all electrical power to heat, so $P = VI$ applies directly with rms values.",
            "Identify given quantities: power rating (1000 W) and mains voltage (230 V rms). "
            "Rearrange once — no reactance or impedance enters because the load is purely resistive.",
            "Dividing by peak voltage ($230\\sqrt{2}$) gives ~3.1 A. "
            "Multiplying $P$ and $V$ instead of dividing is an arithmetic reversal error.",
            "Verify: $230 \\times 4.35 \\approx 1000$ W. "
            "Bagrut short answers accept 4.3–4.4 A; state units.",
        ),
        "explanation_he": expl_he(
            "$I_{\\text{rms}} = 1000 / 230 \\approx 4.35$ A. "
            "תנור נגדי ממיר את כל ההספק לחום, ולכן $P = VI$ ישירות עם rms.",
            "זהו את הנתונים: 1000 W ו-230 V rms. "
            "ארגנו מחדש פעם אחת — אין ראקטנס כי העומס נגדי טהור. "
            "אם נתון גם $\\cos\\phi$, רק אז נדרש הספק אמיתי $P = VI\\cos\\phi$.",
            "חלוקה במתח פסגה ($230\\sqrt{2}$) נותנת ~3.1 A. "
            "הכפלת $P$ ב-$V$ במקום חלוקה — טעות חשבונית.",
            "בדיקה: $230 \\times 4.35 \\approx 1000$ W. "
            "בבגרות מתקבל 4.3–4.4 A; ציינו יחידות. "
            "שאלות הספק-זרם על תנור הן מהנפוצות ביותר בשאלון החשמל.",
        ),
    },
}


def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))

    for sec in data["sections"]:
        kind = sec["kind"]
        if kind in SECTIONS:
            sec["body_en_md"] = SECTIONS[kind]["body_en_md"]
            sec["body_he_md"] = SECTIONS[kind]["body_he_md"]
        elif kind == "worked_example":
            n = sec.get("example_number")
            if n in WORKED:
                sec["body_en_md"] = WORKED[n]["body_en_md"]
                sec["body_he_md"] = WORKED[n]["body_he_md"]
        elif kind in OTHER_SECTIONS:
            sec["body_en_md"] = OTHER_SECTIONS[kind]["body_en_md"]
            sec["body_he_md"] = OTHER_SECTIONS[kind]["body_he_md"]

    cp_idx = 0
    for sec in data["sections"]:
        if sec["kind"] == "checkpoint" and cp_idx < len(CHECKPOINTS):
            sec.update(CHECKPOINTS[cp_idx])
            cp_idx += 1

    for q in data["questions"]:
        ord_ = q["ord"]
        if ord_ in QUESTION_EXPLANATIONS:
            q["explanation_en"] = QUESTION_EXPLANATIONS[ord_]["explanation_en"]
            q["explanation_he"] = QUESTION_EXPLANATIONS[ord_]["explanation_he"]

    for sec in data["sections"]:
        if sec["kind"] == "why_matters":
            sec["body_en_md"] = OTHER_SECTIONS["why_matters"]["body_en_md"]
            sec["body_he_md"] = OTHER_SECTIONS["why_matters"]["body_he_md"]

    # Validate sections
    errors = []
    for sec in data["sections"]:
        kind = sec["kind"]
        if kind not in MIN_WORDS:
            continue
        en_w = word_count(sec.get("body_en_md", ""))
        he_w = word_count(sec.get("body_he_md", ""))
        if en_w < MIN_WORDS[kind]["en"]:
            errors.append(f"{kind} EN: {en_w} < {MIN_WORDS[kind]['en']}")
        if he_w < MIN_WORDS[kind]["he"]:
            errors.append(f"{kind} HE: {he_w} < {MIN_WORDS[kind]['he']}")
        if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
            errors.append(f"{kind} HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            w = word_count(q.get(f"explanation_{lang}", ""))
            if w < 80 or w > 150:
                errors.append(f"Q{q['ord']} expl_{lang}: {w} words (need 80-150)")

    if errors:
        print("VALIDATION WARNINGS:")
        for e in errors:
            print(" ", e)

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(PATH.read_text(encoding="utf-8"))
    print(f"Wrote {PATH}")
    print(f"Sections: {len(data['sections'])}, Questions: {len(data['questions'])}")


if __name__ == "__main__":
    main()
