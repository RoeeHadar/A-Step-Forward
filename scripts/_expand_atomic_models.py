#!/usr/bin/env python3
"""Generate expanded atomic_models.json and validate depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/atomic_models.json"

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


def hebrew_body_weak(body_he, body_en):
    he = (body_he or "").strip()
    en = (body_en or "").strip()
    if not he:
        return True
    if not en:
        return len(re.findall(r"[\u0590-\u05FF]", he)) / (
            len(re.findall(r"[\u0590-\u05FF]", he))
            + len(re.findall(r"[a-zA-Z]{3,}", he))
            + 1
        ) < 0.12
    ratio = word_count(he) / max(word_count(en), 1)
    if ratio < 0.55:
        return True
    he_chars = len(re.findall(r"[\u0590-\u05FF]", he))
    lat = len(re.findall(r"[a-zA-Z]{3,}", he))
    if he_chars / (he_chars + lat + 1) < 0.15 and word_count(he) > 25:
        return True
    probe = en[: min(60, len(en))].strip()
    if len(probe) > 20 and probe in he:
        return True
    return False


SECTION_BODIES = {
    "intro": {
        "body_en_md": (
            "How did scientists figure out what atoms look like when they cannot see them directly? "
            "They **inferred structure from experiments** — each new result shattered the previous picture.\n\n"
            "The story unfolds in three stages:\n"
            "1. **Thomson's plum-pudding (1904)** — positive sphere with embedded electrons. "
            "Disproved by Rutherford's gold-foil experiment.\n"
            "2. **Rutherford's nuclear model (1911)** — tiny dense nucleus + mostly empty space. "
            "Could not explain discrete spectral lines.\n"
            "3. **Bohr's quantized orbits (1913)** — electrons in fixed energy levels. "
            "Successfully explains the hydrogen spectrum.\n\n"
            "In **Bagrut Physics (5 units)**, you must **describe each model, state its key failure, "
            "and calculate** photon energies, wavelengths, and spectral series using $E_n=-13.6/n^2$ eV. "
            "This lesson builds on `concept:modern_physics_intro` (photon energy) and leads to "
            "`concept:nuclear_physics`."
        ),
        "body_he_md": (
            "איך גילו מדענים את מבנה האטום מבלי לראות אותו ישירות? "
            "הם **הסיקו מבנה מניסויים** — כל תוצאה חדשה שברה את התמונה הקודמת.\n\n"
            "הסיפור מתפתח בשלושה שלבים:\n"
            "1. **מודל תומסון (1904)** — כדור חיובי עם אלקטרונים טמונים. "
            "הופרך בניסוי עלה הזהב של רתרפורד.\n"
            "2. **מודל רתרפורד (1911)** — גרעין קטן ודחוס + מרחב ריק. "
            "לא הסביר קווי ספקטרום בדידים.\n"
            "3. **מודל בוהר (1913)** — אלקטרונים ברמות אנרגיה קוונטיות קבועות. "
            "מסביר בהצלחה את ספקטרום המימן.\n\n"
            "ב**בגרות בפיזיקה (5 יחידות)** חובה **לתאר כל מודל, לציין את כשלונו, "
            "ולחשב** אנרגיות פוטון, אורכי גל וסדרות ספקטרום עם $E_n=-13.6/n^2$ eV. "
            "השיעור מבוסס על `concept:modern_physics_intro` (אנרגיית פוטון) "
            "ומוביל ל-`concept:nuclear_physics`."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Thomson model (1904):** The atom is a uniform positive sphere with electrons "
            "embedded like plums in pudding. There is no nucleus. "
            "**Failure:** Rutherford's gold-foil experiment showed most of the atom is empty space.\n\n"
            "**Rutherford model (1911):** A tiny, dense, positively charged **nucleus** at the centre, "
            "with electrons orbiting in mostly empty space. Based on alpha-particle scattering. "
            "**Failure:** Classical electrodynamics predicts an orbiting electron should radiate energy "
            "and spiral into the nucleus in $\\sim10^{-12}$ s — atoms would be unstable.\n\n"
            "**Bohr model (1913):** Electrons occupy **fixed quantized orbits** with specific energies "
            "$E_n$. They do NOT radiate while in a stable orbit. They emit or absorb photons when "
            "jumping between levels:\n"
            "$$E_{\\text{photon}} = |E_f - E_i| = hf = \\frac{hc}{\\lambda}$$\n\n"
            "For hydrogen: $E_n = -\\dfrac{13.6}{n^2}\\text{ eV}$, where $n=1,2,3,\\ldots$ "
            "Negative values mean the electron is **bound** to the nucleus. "
            "Ionization occurs when $E=0$ (electron escapes)."
        ),
        "body_he_md": (
            "**מודל תומסון (1904):** האטום הוא כדור חיובי אחיד עם אלקטרונים טמונים. "
            "אין גרעין. **כשל:** ניסוי עלה הזהב של רתרפורד הראה שרוב האטום הוא מרחב ריק.\n\n"
            "**מודל רתרפורד (1911):** גרעין קטן, דחוס וחיובי במרכז, "
            "עם אלקטרונים במסלולים במרחב ריק. מבוסס על פיזור חלקיקי אלפא. "
            "**כשל:** אלקטרודינמיקה קלאסית חוזה שאלקטרון במסלול יפלוט אנרגיה ויסתובב לגרעין "
            "תוך $\\sim10^{-12}$ s — האטומים לא יהיו יציבים.\n\n"
            "**מודל בוהר (1913):** אלקטרונים ב**מסלולים קוונטיים קבועים** עם אנרגיות $E_n$ מוגדרות. "
            "הם **לא** פולטים קרינה במסלול יציב. הם פולטים או קולטים פוטונים בקפיצות:\n"
            "$$E_{\\text{photon}} = |E_f - E_i| = hf = \\frac{hc}{\\lambda}$$\n\n"
            "למימן: $E_n = -\\dfrac{13.6}{n^2}\\text{ eV}$, כאשר $n=1,2,3,\\ldots$ "
            "ערכים שליליים פירושם שהאלקטרון **קשור** לגרעין. "
            "יינון מתרחש כש-$E=0$ (האלקטרון בורח לחופש). "
            "נוסחה זו תקפה למימן בלבד."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Energy levels of hydrogen\n\n"
            "$$E_n = -\\frac{13.6}{n^2} \\text{ eV} \\quad (n=1,2,3,\\ldots)$$\n"
            "- **Ground state:** $n=1$, $E_1=-13.6$ eV (most bound).\n"
            "- **First excited:** $n=2$, $E_2=-3.4$ eV.\n"
            "- **Ionization limit:** $E_\\infty=0$ (electron free).\n\n"
            "### Transitions and photons\n\n"
            "For a transition from initial level $n_i$ to final level $n_f$:\n"
            "$$\\Delta E = E_{n_f} - E_{n_i}$$\n"
            "- **Downward jump** ($n_i>n_f$): electron emits a photon with $E_{\\text{photon}}=|\\Delta E|$.\n"
            "- **Upward jump** ($n_i<n_f$): electron absorbs a photon with $E_{\\text{photon}}=|\\Delta E|$.\n\n"
            "### Wavelength from energy\n\n"
            "$$\\lambda = \\frac{hc}{|\\Delta E|} \\quad \\text{with } hc=1240\\text{ eV·nm}$$\n\n"
            "### Spectral series (hydrogen)\n\n"
            "Named by the **final level** $n_f$:\n"
            "- **Lyman series** ($n_f=1$): UV region.\n"
            "- **Balmer series** ($n_f=2$): visible light (H-alpha red at 656 nm).\n"
            "- **Paschen series** ($n_f=3$): infrared.\n\n"
            "**Ionization energy** from ground state = $|E_1|=13.6$ eV. "
            "From $n=2$: only 3.4 eV needed because the electron is already partially excited.\n\n"
            "### Counting spectral lines\n\n"
            "If an atom is excited to level $n_{\\max}$, the number of distinct emission lines is "
            "$\\binom{n_{\\max}}{2}$ — every pair of levels with $n_i > n_f$ contributes one photon wavelength. "
            "For $n_{\\max}=4$: six lines total ($4\\to3$, $4\\to2$, $4\\to1$, $3\\to2$, $3\\to1$, $2\\to1$). "
            "On Bagrut exams, always state the series name from $n_f$ after computing $\\Delta E$."
        ),
        "body_he_md": (
            "### רמות אנרגיה של מימן\n\n"
            "$$E_n = -\\frac{13.6}{n^2} \\text{ eV} \\quad (n=1,2,3,\\ldots)$$\n"
            "- **מצב היסוד:** $n=1$, $E_1=-13.6$ eV (הכי קשור).\n"
            "- **מצב מעורר ראשון:** $n=2$, $E_2=-3.4$ eV.\n"
            "- **גבול יינון:** $E_\\infty=0$ (אלקטרון חופשי).\n\n"
            "### מעברים ופוטונים\n\n"
            "למעבר מרמה $n_i$ לרמה $n_f$:\n"
            "$$\\Delta E = E_{n_f} - E_{n_i}$$\n"
            "- **קפיצה כלפי מטה** ($n_i>n_f$): האלקטרון פולט פוטון עם $E_{\\text{photon}}=|\\Delta E|$.\n"
            "- **קפיצה כלפי מעלה** ($n_i<n_f$): האלקטרון קולט פוטון עם $E_{\\text{photon}}=|\\Delta E|$.\n\n"
            "### אורך גל מאנרגיה\n\n"
            "$$\\lambda = \\frac{hc}{|\\Delta E|} \\quad \\text{עם } hc=1240\\text{ eV·nm}$$\n\n"
            "### סדרות ספקטרום (מימן)\n\n"
            "נקראות לפי **הרמה הסופית** $n_f$:\n"
            "- **סדרת לימן** ($n_f=1$): אזור UV.\n"
            "- **סדרת בלמר** ($n_f=2$): אור נראה (H-alpha אדום ב-656 nm).\n"
            "- **סדרת פשן** ($n_f=3$): אינפרא-אדום.\n\n"
            "**אנרגיית יינון** ממצב היסוד = $|E_1|=13.6$ eV. "
            "מ-$n=2$: נדרשים רק 3.4 eV כי האלקטרון כבר מעורר חלקית.\n\n"
            "### ספירת קווי ספקטרום\n\n"
            "אם אטום מעורר לרמה $n_{\\max}$, מספר קווי הפליטה השונים הוא "
            "$\\binom{n_{\\max}}{2}$ — כל זוג רמות עם $n_i > n_f$ תורם אורך גל פוטון אחד. "
            "ל-$n_{\\max}=4$: שישה קווים ($4\\to3$, $4\\to2$, $4\\to1$, $3\\to2$, $3\\to1$, $2\\to1$). "
            "בבגרות, תמיד ציינו את שם הסדרה לפי $n_f$ אחרי חישוב $\\Delta E$."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Find** the energy of a photon emitted when a hydrogen electron falls from $n=3$ to $n=2$.\n\n"
            "### Move 1: Energy of level $n=3$\n"
            "$$E_3 = -\\frac{13.6}{9} = -1.511\\text{ eV}$$\n\n"
            "### Move 2: Energy of level $n=2$\n"
            "$$E_2 = -\\frac{13.6}{4} = -3.4\\text{ eV}$$\n\n"
            "### Move 3: Energy difference\n"
            "$$\\Delta E = E_2 - E_3 = -3.4 - (-1.511) = -1.889\\text{ eV}$$\n"
            "Photon energy = $|\\Delta E| = 1.889$ eV.\n\n"
            "### Move 4: Identify the series\n"
            "Final level is $n=2$ → **Balmer series** (visible light).\n\n"
            "### Move 5: Wavelength\n"
            "$$\\lambda = \\frac{1240}{1.889} \\approx 656\\text{ nm}$$\n"
            "This is the famous **H-alpha red line**.\n\n"
            "### Move 6: Frequency check\n"
            "$$f = \\frac{E}{h} = \\frac{1.889\\times1.6\\times10^{-19}}{6.63\\times10^{-34}} \\approx 4.56\\times10^{14}\\text{ Hz}$$\n"
            "Cross-check via $f=c/\\lambda$: $3\\times10^8/(656\\times10^{-9})\\approx4.57\\times10^{14}$ Hz ✓.\n\n"
            "**Answer:** Photon energy $=1.89$ eV, $\\lambda\\approx656$ nm (Balmer, red). "
            "**Exam tip:** Always identify the series from the **final** level $n_f$, not the initial level. "
            "The $3\\to2$ transition is the most famous Balmer line — memorize its energy (~1.89 eV) and wavelength (656 nm). "
            "This red line is easily observed in hydrogen discharge tubes."
        ),
        "body_he_md": (
            "**מצאו** את אנרגיית הפוטון הנפלט כשאלקטרון מימן קופץ מ-$n=3$ ל-$n=2$.\n\n"
            "### צעד 1: אנרgy רמה $n=3$\n"
            "$$E_3 = -\\frac{13.6}{9} = -1.511\\text{ eV}$$\n\n"
            "### צעד 2: אנרgy רמה $n=2$\n"
            "$$E_2 = -\\frac{13.6}{4} = -3.4\\text{ eV}$$\n\n"
            "### צעד 3: הפרש אנרgy\n"
            "$$\\Delta E = E_2 - E_3 = -3.4 - (-1.511) = -1.889\\text{ eV}$$\n"
            "אנרgy פוטון = $|\\Delta E| = 1.889$ eV.\n\n"
            "### צעד 4: זיהוי הסדרה\n"
            "הרמה הסופית $n=2$ → **סדרת בלמר** (אור נראה).\n\n"
            "### צעד 5: אורך גל\n"
            "$$\\lambda = \\frac{1240}{1.889} \\approx 656\\text{ nm}$$\n"
            "זהו **קו H-alpha האדום** המפורסם.\n\n"
            "### צעד 6: בדיקת תדר\n"
            "$$f = \\frac{E}{h} = \\frac{1.889\\times1.6\\times10^{-19}}{6.63\\times10^{-34}} \\approx 4.56\\times10^{14}\\text{ Hz}$$\n"
            "אימות דרך $f=c/\\lambda$: $3\\times10^8/(656\\times10^{-9})\\approx4.57\\times10^{14}$ Hz ✓.\n\n"
            "**תשובה:** אנרגיית פוטון $=1.89$ eV, $\\lambda\\approx656$ nm (בלמר, אדום). "
            "**טיפ לבחינה:** זהו את הסדרה לפי הרמה **הסופית** $n_f$, לא לפי הרמה ההתחלתית. "
            "מעבר $3\\to2$ הוא קו הבלמר המפורסם ביותר — שיננו את האנרגיה (~1.89 eV) ואורך הגל (656 nm)."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "A hydrogen electron drops from $n=4$ to $n=2$. Find the photon energy and state the series.\n\n"
            "**Step 1:** Compute level energies:\n"
            "$$E_4 = -\\frac{13.6}{16} = -0.85\\text{ eV}, \\quad E_2 = -3.4\\text{ eV}$$\n\n"
            "**Step 2:** Energy difference:\n"
            "$$\\Delta E = E_2 - E_4 = -3.4 - (-0.85) = -2.55\\text{ eV}$$\n"
            "Photon energy $= |\\Delta E| = 2.55$ eV.\n\n"
            "**Step 3:** Wavelength check:\n"
            "$$\\lambda = \\frac{1240}{2.55} \\approx 486\\text{ nm}$$\n"
            "This is blue-green visible light.\n\n"
            "**Step 4:** Series identification: final level $n=2$ → **Balmer series**.\n\n"
            "**Answer:** $E_{\\text{photon}}=2.55$ eV, Balmer series, $\\lambda\\approx486$ nm (blue-green)."
        ),
        "checkpoint_solution_he": (
            "אלקטרון מימן קופץ מ-$n=4$ ל-$n=2$. חשבו אנרgy פוטון וזהו את הסדרה.\n\n"
            "**שלב 1:** חישוב אנרgy רמות:\n"
            "$$E_4 = -\\frac{13.6}{16} = -0.85\\text{ eV}, \\quad E_2 = -3.4\\text{ eV}$$\n\n"
            "**שלב 2:** הפרש אנרgy:\n"
            "$$\\Delta E = E_2 - E_4 = -3.4 - (-0.85) = -2.55\\text{ eV}$$\n"
            "אנרgy פוטון $= |\\Delta E| = 2.55$ eV.\n\n"
            "**שלב 3:** בדיקת אורך גל:\n"
            "$$\\lambda = \\frac{1240}{2.55} \\approx 486\\text{ nm}$$\n"
            "זהו אור כחול-ירוק נראה.\n\n"
            "**שלב 4:** זיהוי סדרה: רמה סופית $n=2$ → **סדרת בלמר**.\n\n"
            "**תשובה:** $E_{\\text{photon}}=2.55$ eV, סדרת בלמר, $\\lambda\\approx486$ nm (כחול-ירוק)."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**A hydrogen atom in the ground state absorbs a 12.1 eV photon. Find the new state.**\n\n"
            "### Move 1: Ground state energy\n"
            "$$E_1 = -13.6\\text{ eV}$$\n\n"
            "### Move 2: Energy after absorption\n"
            "The electron gains 12.1 eV:\n"
            "$$E_{\\text{new}} = E_1 + 12.1 = -13.6 + 12.1 = -1.5\\text{ eV}$$\n\n"
            "### Move 3: Match to a Bohr level\n"
            "Set $E_n = -13.6/n^2 = -1.5$:\n"
            "$$\\frac{13.6}{n^2} = 1.5 \\Rightarrow n^2 = \\frac{13.6}{1.5} = 9.07 \\approx 9 \\Rightarrow n = 3$$\n\n"
            "### Move 4: Verify\n"
            "$E_3 = -13.6/9 = -1.511$ eV ≈ $-1.5$ eV ✓ (small rounding difference from given 12.1 eV).\n\n"
            "### Move 5: Physical interpretation\n"
            "The electron jumped from ground state ($n=1$) to the **second excited state** ($n=3$). "
            "It absorbed exactly the energy difference $|E_3 - E_1| = 12.09$ eV.\n\n"
            "### Move 6: Could the electron be ionized?\n"
            "Ionization requires $E_{\\text{new}}\\ge0$. Here $E_{\\text{new}}=-1.5$ eV $<0$, so the electron "
            "remains bound — it is not ionized.\n\n"
            "**Answer:** Electron is in $n=3$. **Exam tip:** For absorption, add photon energy to initial level energy, "
            "then solve $-13.6/n^2 = E_{\\text{new}}$ for integer $n$. If no integer $n$ matches, check whether "
            "the photon energy exceeds the ionization threshold."
        ),
        "body_he_md": (
            "**אטום מימן במצב היסוד קולט פוטון של 12.1 eV. מצאו את המצב החדש.**\n\n"
            "### צעד 1: אנרגיית מצב היסוד\n"
            "$$E_1 = -13.6\\text{ eV}$$\n\n"
            "### צעד 2: אנרגיה אחרי קליטה\n"
            "האלקטרון מקבל 12.1 eV:\n"
            "$$E_{\\text{new}} = E_1 + 12.1 = -13.6 + 12.1 = -1.5\\text{ eV}$$\n\n"
            "### צעד 3: התאמה לרמת בוהר\n"
            "נקבע $E_n = -13.6/n^2 = -1.5$:\n"
            "$$\\frac{13.6}{n^2} = 1.5 \\Rightarrow n^2 = \\frac{13.6}{1.5} = 9.07 \\approx 9 \\Rightarrow n = 3$$\n\n"
            "### צעד 4: אימות\n"
            "$E_3 = -13.6/9 = -1.511$ eV ≈ $-1.5$ eV ✓ (הפרש קטן מעיגול 12.1 eV).\n\n"
            "### צעד 5: פרשנות פיזיקלית\n"
            "האלקטרון קפץ ממצב היסוד ($n=1$) ל**מצב מעורר שני** ($n=3$). "
            "קלט בדיוק את הפרש האנרגיה $|E_3 - E_1| = 12.09$ eV.\n\n"
            "### צעד 6: האם האלקטרון יכול להיות מיונן?\n"
            "יינון דורש $E_{\\text{new}}\\ge0$. כאן $E_{\\text{new}}=-1.5$ eV $<0$, ולכן האלקטרון "
            "נשאר קשור — הוא לא מיונן.\n\n"
            "**תשובה:** האלקטרון ב-$n=3$. **טיפ לבחינה:** בקליטה, חברו אנרגיית פוטון לרמה ההתחלתית, "
            "ואז פתרו $-13.6/n^2 = E_{\\text{new}}$ עבור $n$ שלם. אם אין $n$ שלם מתאים, בדקו "
            "האם אנרגיית הפוטון עולה על סף היינון."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "What is the minimum energy needed to ionize hydrogen from $n=2$?\n\n"
            "**Step 1:** Energy of $n=2$ level:\n"
            "$$E_2 = -\\frac{13.6}{4} = -3.4\\text{ eV}$$\n\n"
            "**Step 2:** Ionization means reaching $E=0$ (electron free):\n"
            "$$E_{\\text{ionization}} = 0 - E_2 = 0 - (-3.4) = 3.4\\text{ eV}$$\n\n"
            "**Step 3:** Compare to ground-state ionization:\n"
            "From $n=1$: 13.6 eV needed. From $n=2$: only 3.4 eV — the electron is already partially excited.\n\n"
            "**Step 4:** Wavelength of threshold photon:\n"
            "$$\\lambda = \\frac{1240}{3.4} \\approx 365\\text{ nm}$$ (UV, near Balmer limit).\n\n"
            "**Answer:** 3.4 eV minimum to ionize from $n=2$."
        ),
        "checkpoint_solution_he": (
            "מה אנרgy היינון המינימלית ממצב $n=2$?\n\n"
            "**שלב 1:** אנרgy רמה $n=2$:\n"
            "$$E_2 = -\\frac{13.6}{4} = -3.4\\text{ eV}$$\n\n"
            "**שלב 2:** יינון פירושו הגעה ל-$E=0$ (אלקטרון חופשי):\n"
            "$$E_{\\text{ionization}} = 0 - E_2 = 0 - (-3.4) = 3.4\\text{ eV}$$\n\n"
            "**שלב 3:** השוואה ליינון ממצב היסוד:\n"
            "מ-$n=1$: נדרשים 13.6 eV. מ-$n=2$: רק 3.4 eV — האלקטרון כבר מעורר חלקית.\n\n"
            "**שלב 4:** אורך גל של פוטון סף:\n"
            "$$\\lambda = \\frac{1240}{3.4} \\approx 365\\text{ nm}$$ (UV, קרוב לגבול בלמר).\n\n"
            "**תשובה:** 3.4 eV מינימום ליינון מ-$n=2$."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**A hydrogen atom is excited to $n=4$. How many distinct photon wavelengths can be emitted "
            "as it returns to ground state? Calculate the highest and lowest energy photons.**\n\n"
            "### Move 1: Count possible transitions\n"
            "From $n=4$, all downward paths: $4\\to3$, $4\\to2$, $4\\to1$, $3\\to2$, $3\\to1$, $2\\to1$.\n"
            "Total $= \\binom{4}{2} = 6$ distinct spectral lines.\n\n"
            "### Move 2: Highest energy photon ($4\\to1$, Lyman series)\n"
            "$$E_4 = -0.85\\text{ eV}, \\quad E_1 = -13.6\\text{ eV}$$\n"
            "$$\\Delta E = 12.75\\text{ eV}, \\quad \\lambda = \\frac{1240}{12.75} \\approx 97.3\\text{ nm (UV)}$$\n\n"
            "### Move 3: Lowest energy photon ($4\\to3$, Paschen series)\n"
            "$$E_3 = -1.511\\text{ eV}, \\quad \\Delta E = 0.661\\text{ eV}, \\quad \\lambda \\approx 1876\\text{ nm (IR)}$$\n\n"
            "### Move 4: Intermediate example ($3\\to2$, Balmer)\n"
            "$$\\Delta E = 1.889\\text{ eV}, \\quad \\lambda \\approx 656\\text{ nm (red)}$$\n\n"
            "### Move 5: Physical picture\n"
            "The atom may cascade through intermediate levels, but each individual transition produces "
            "one photon of a specific energy. All six lines appear in the emission spectrum.\n\n"
            "**Answer:** 6 spectral lines. Highest: 12.75 eV (97 nm, UV). Lowest: 0.66 eV (1876 nm, IR). "
            "**Exam tip:** Use $\\binom{n_{\\max}}{2}$ to count lines quickly."
        ),
        "body_he_md": (
            "**אטום מימן מעורר ל-$n=4$. כמה אורכי גל פוטון שונים יכולים להיפלט "
            "בחזרה למצב היסוד? חשבו את הפוטונים בעלי האנרגיה הגבוהה והנמוכה ביותר.**\n\n"
            "### צעד 1: ספירת מעברים אפשריים\n"
            "מ-$n=4$, כל הנתיבים כלפי מטה: $4\\to3$, $4\\to2$, $4\\to1$, $3\\to2$, $3\\to1$, $2\\to1$.\n"
            "סה\"כ $= \\binom{4}{2} = 6$ קווי ספקטרום שונים.\n\n"
            "### צעד 2: פוטון בעל האנרגיה הגבוהה ביותר ($4\\to1$, לימן)\n"
            "$$E_4 = -0.85\\text{ eV}, \\quad E_1 = -13.6\\text{ eV}$$\n"
            "$$\\Delta E = 12.75\\text{ eV}, \\quad \\lambda = \\frac{1240}{12.75} \\approx 97.3\\text{ nm (UV)}$$\n\n"
            "### צעד 3: פוטון בעל האנרגיה הנמוכה ביותר ($4\\to3$, פשן)\n"
            "$$E_3 = -1.511\\text{ eV}, \\quad \\Delta E = 0.661\\text{ eV}, \\quad \\lambda \\approx 1876\\text{ nm (IR)}$$\n\n"
            "### צעד 4: דוגמה ביניים ($3\\to2$, בלמר)\n"
            "$$\\Delta E = 1.889\\text{ eV}, \\quad \\lambda \\approx 656\\text{ nm (אדום)}$$\n\n"
            "### צעד 5: תמונה פיזיקלית\n"
            "האטום עשוי לרדת דרך רמות ביניים, אך כל מעבר בודד מייצר "
            "פוטון אחד באנרגיה מוגדרת. כל ששת הקווים מופיעים בספקטרום הפליטה.\n\n"
            "**תשובה:** 6 קווי ספקטרום. הגבוה: 12.75 eV (97 nm, UV). הנמוך: 0.66 eV (1876 nm, IR). "
            "**טיפ לבחינה:** השתמשו ב-$\\binom{n_{\\max}}{2}$ לספירה מהירה."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "**Step-by-step recipe for atomic model problems:**\n\n"
            "| Task | Method | Key note |\n"
            "|---|---|---|\n"
            "| Describe model & failure | Thomson→Rutherford (gold foil); Rutherford→Bohr (spiral collapse) | Each model solved one problem but created another |\n"
            "| Energy of level $n$ | $E_n=-13.6/n^2$ eV | Valid for hydrogen only |\n"
            "| Photon emitted/absorbed | $E_{\\text{ph}}=\\|E_{n_f}-E_{n_i}\\|$ | Emission: $n_i>n_f$; absorption: $n_i<n_f$ |\n"
            "| Wavelength from energy | $\\lambda=1240/E_{\\text{eV}}$ nm | Requires energy in eV, result in nm |\n"
            "| Identify series | Final level $n_f$: $n_f=1$ Lyman; $n_f=2$ Balmer; $n_f=3$ Paschen | Named by destination, not origin |\n"
            "| Count spectral lines | $\\binom{n_{\\max}}{2}$ | All downward pairs from excited level |\n\n"
            "**Decision tree:** (1) Conceptual (model/failure) or calculation? "
            "(2) If calculation: find $E_n$ values first. (3) Compute $\\Delta E$, take absolute value. "
            "(4) Convert to $\\lambda$ if needed. (5) Name the series from $n_f$."
        ),
        "body_he_md": (
            "**מתכון שלב-אחר-שלב לבעיות מודלים אטומיים:**\n\n"
            "| משימה | שיטה | הערה |\n"
            "|---|---|---|\n"
            "| תאר מודל וכשלונו | תומסון→רתרפורד (עלה זהב); רתרפורד→בוהר (קריסה אלקטרונית) | כל מודל פתר בעיה אחת אך יצר אחרת |\n"
            "| אנרגיית רמה $n$ | $E_n=-13.6/n^2$ eV | תקף למימן בלבד |\n"
            "| פוטון נפלט/נקלט | $E_{\\text{ph}}=\\|E_{n_f}-E_{n_i}\\|$ | פליטה: $n_i>n_f$; קליטה: $n_i<n_f$ |\n"
            "| אורך גל מאנרגיה | $\\lambda=1240/E_{\\text{eV}}$ nm | דורש אנרגיה ב-eV, תוצאה ב-nm |\n"
            "| זהה סדרה | רמה סופית $n_f$: $n_f=1$ לימן; $n_f=2$ בלמר; $n_f=3$ פשן | נקראת לפי יעד, לא מקור |\n"
            "| ספור קווי ספקטרום | $\\binom{n_{\\max}}{2}$ | כל זוגות הירידה מרמה מעוררת |\n\n"
            "**עץ החלטות:** (1) שאלה מושגית (מודל/כשל) או חישובית? "
            "(2) אם חישוב: מצאו $E_n$ קודם. (3) חשבו $\\Delta E$, קחו ערך מוחלט. "
            "(4) המירו ל-$\\lambda$ אם נדרש. (5) קראו לסדרה לפי $n_f$."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Sign error on $E_n$:** Energy levels are **negative** (bound electron). "
            "When computing $\\Delta E = E_f - E_i$, keep the minus signs — then take $|\\Delta E|$ for photon energy.\n\n"
            "2. **Confusing models:** Rutherford explained *why* the atom is mostly empty space; "
            "Bohr explained *discrete spectral lines*. They address different experimental failures.\n\n"
            "3. **Emission vs absorption direction:** Downward jump ($n_i\\to n_f$, $n_i>n_f$) → photon **emitted**. "
            "Upward jump → photon **absorbed**. The energy magnitude is the same; the process differs.\n\n"
            "4. **Series naming:** The series is named by the **final** level $n_f$, not the starting level. "
            "$3\\to2$ is Balmer (not \"level 3 series\").\n\n"
            "5. **Unit trap with $hc=1240$:** This shortcut requires energy in **eV** and gives wavelength in **nm**. "
            "Mixing joules with 1240 gives nonsense.\n\n"
            "**Example misconception:** Treating $E_n$ as positive binding energy.\n\n"
            "**Fix:** $E_n<0$ means bound; $|E_n|$ is the binding energy."
        ),
        "body_he_md": (
            "1. **שגיאת סימן ב-$E_n$:** רמות אנרגיה **שליליות** (אלקטרון קשור). "
            "בחישוב $\\Delta E = E_f - E_i$, שמרו על הסימנים — ואז קחו $|\\Delta E|$ לאנרגיית הפוטון.\n\n"
            "2. **בלבול בין מודלים:** רתרפורד הסביר *למה* האטום בעיקרו ריק; "
            "בוהר הסביר *קווי ספקטרום בדידים*. כל אחד ענה על כשל ניסויי שונה.\n\n"
            "3. **כיוון פליטה מול קליטה:** קפיצה למטה ($n_i\\to n_f$, $n_i>n_f$) → פוטון **נפלט**. "
            "קפיצה למעלה → פוטון **נקלט**. גודל האנרגיה זהה; התהליך שונה.\n\n"
            "4. **שם הסדרה:** הסדרה נקראת לפי הרמה **הסופית** $n_f$, לא ההתחלתית. "
            "$3\\to2$ הוא בלמר (לא \"סדרת רמה 3\").\n\n"
            "5. **מלכודת יחידות עם $hc=1240$:** הקיצור דורש אנרגיה ב-**eV** ונותן אורך גל ב-**nm**. "
            "ערבוב ג'אול עם 1240 נותן תוצאה שגויה.\n\n"
            "**תפיסה שגויה:** לראות ב-$E_n$ אנרגיית קשר חיובית.\n\n"
            "**תיקון:** $E_n<0$ פירושו קשור; $|E_n|$ היא אנרגיית הקשר."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Atomic models are the bridge between classical mechanics and quantum physics — "
            "understanding how each model failed teaches you **why** quantum mechanics was necessary.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:nuclear_physics` **Nuclear Physics & Radioactivity** (prerequisite)\n"
            "- Spectroscopy applications in chemistry and astrophysics\n\n"
            "**Builds on:**\n"
            "- `concept:modern_physics_intro` **Quantum Physics Basics (Photoelectric Effect)**\n\n"
            "**Why it matters for exams:** Bagrut rewards both conceptual understanding (describe each model's failure) "
            "and quantitative skill (Bohr calculations). The hydrogen spectrum is one of the most tested topics "
            "in 5-unit physics. When studying, connect each formula to a physical picture — not just algebra."
        ),
        "body_he_md": (
            "מודלים אטומיים הם הגשר בין מכניקה קלאסית לפיזיקה קוונטית — "
            "הבנת כשל כל מודל מלמדת **למה** מכניקת הקוונטים הייתה הכרחית.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:nuclear_physics` **פיזיקה גרעינית ורדיואקטיביות** (דרישת קדם)\n"
            "- יישומי ספקטרוסקופיה בכימיה ובאסטרופיזיקה\n\n"
            "**מבוסס על:**\n"
            "- `concept:modern_physics_intro` **מבוא לפיזיקה קוונטית (אפקט פוטואלקטרי)**\n\n"
            "**למה זה חשוב לבחינות:** בבגרות מעריכים גם הבנה מושגית (תיאור כשל כל מודל) "
            "וגם מיומנות כמותית (חישובי בוהר). ספקטרום המימן הוא מהנושאים הנבחנים ביותר "
            "בפיזיקה 5 יחידות. בלימוד, קשרו כל נוסחה לתמונה פיזיקלית — לא רק לחישוב."
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Conceptual checklist:**\n"
            "- Thomson: plum pudding, no nucleus → disproved by gold foil.\n"
            "- Rutherford: dense nucleus, empty space → can't explain spectral lines or stability.\n"
            "- Bohr: quantized orbits, no radiation in stable orbit → explains hydrogen spectrum.\n\n"
            "**Formula checklist:**\n"
            "- $E_n=-13.6/n^2$ eV (hydrogen only).\n"
            "- Photon: $E_{\\text{ph}}=|E_{n_f}-E_{n_i}|=hf=hc/\\lambda$. Use $hc=1240$ eV·nm.\n"
            "- Series: Lyman ($n_f=1$, UV), Balmer ($n_f=2$, visible), Paschen ($n_f=3$, IR).\n"
            "- Number of lines from $n_{\\max}$: $\\binom{n_{\\max}}{2}$.\n\n"
            "**Last review:** Draw the energy level diagram, label three series, then solve one full transition problem without notes."
        ),
        "body_he_md": (
            "**רשימת בדיקה מושגית:**\n"
            "- תומסון: כדור חיובי אחיד, אין גרעין → הופרך על ידי עלה הזהb.\n"
            "- רתרפורד: גרעין דחוס, מרחב ריק → לא מסביר קווי ספקטרום או יציבות.\n"
            "- בוהר: מסלולים קוונטיים, ללא קרינה במסלול יציב → מסביר ספקטרום מימן.\n\n"
            "**רשימת בדיקה נוסחאות:**\n"
            "- $E_n=-13.6/n^2$ eV (מימן בלבד).\n"
            "- פוטון: $E_{\\text{ph}}=|E_{n_f}-E_{n_i}|=hf=hc/\\lambda$. $hc=1240$ eV·nm.\n"
            "- סדרות: לימן ($n_f=1$, UV), בלמר ($n_f=2$, נראה), פשן ($n_f=3$, IR).\n"
            "- מספר קווים מ-$n_{\\max}$: $\\binom{n_{\\max}}{2}$.\n\n"
            "**חזרה אחרונה:** ציירו דיאגרמת רמות אנרגיה, סמנו שלוש סדרות, ואז פתרו בעיית מעבר מלאה בלי רשימות."
        ),
    },
    "summary": {
        "body_en_md": (
            "- **Three models:** Thomson (uniform positive sphere) → Rutherford (nuclear, mostly empty) "
            "→ Bohr (quantized orbits).\n"
            "- **Bohr energy levels:** $E_n=-13.6/n^2$ eV for hydrogen.\n"
            "- **Photon energy** = absolute level difference; emission on downward jump, absorption on upward.\n"
            "- **Wavelength:** $\\lambda=1240/\\Delta E_{\\text{eV}}$ nm.\n"
            "- **Three series:** Lyman (UV, to $n=1$), Balmer (visible, to $n=2$), Paschen (IR, to $n=3$).\n\n"
            "**Takeaway:** You should now recognize which model or calculation method applies from the problem wording alone."
        ),
        "body_he_md": (
            "- **שלושה מודלים:** תומסון (כדור חיובי אחיד) → רתרפורד (גרעיני, בעיקר ריק) "
            "→ בוהר (מסלולים קוונטיים).\n"
            "- **רמות אנרגיית בוהר:** $E_n=-13.6/n^2$ eV למימן.\n"
            "- **אנרגיית פוטון** = הפרש רמות בערך מוחלט; פליטה בקפיצה למטה, קליטה בקפיצה למעלה.\n"
            "- **אורך גל:** $\\lambda=1240/\\Delta E_{\\text{eV}}$ nm.\n"
            "- **שלוש סדרות:** לימן (UV, ל-$n=1$), בלמר (נראה, ל-$n=2$), פשן (IR, ל-$n=3$).\n\n"
            "**סיכום:** כעת תוכלו לזהות איזה מודל או שיטת חישוב מתאימים לפי ניסוח השאלה בלבד."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "The **Lyman series** consists of all transitions that end at the ground state ($n_f=1$). "
            "In this question, the electron drops from $n=3$ to $n=1$, so the final level is $n_f=1$.\n\n"
            "Series naming rule: always look at the **destination** level, not where the electron started. "
            "$3\\to1$, $4\\to1$, and $\\infty\\to1$ are all Lyman lines (UV region).\n\n"
            "**Common error:** Choosing Balmer because $n=3$ is involved. Balmer requires $n_f=2$ "
            "(e.g. the famous $3\\to2$ red line at 656 nm).\n\n"
            "**Exam tip:** Write $n_f$ explicitly before selecting the series name. "
            "Lyman = UV, Balmer = visible, Paschen = IR."
        ),
        "explanation_he": (
            "**סדרת לימן** כוללת את כל המעברים שמסתיימים במצב היסוד ($n_f=1$). "
            "בשאלה זו, האלקטרון קופץ מ-$n=3$ ל-$n=1$, ולכן הרמה הסופית $n_f=1$.\n\n"
            "כלל שם הסדרה: תמיד הסתכלו על רמת **היעד**, לא מאיפה האלקטרון התחיל. "
            "$3\\to1$, $4\\to1$ ו-$\\infty\\to1$ — כולם קווי לימן (אזור UV).\n\n"
            "**טעות נפוצה:** בחירה בבלמר כי $n=3$ מעורב. בלמר דורש $n_f=2$ "
            "(למשל קו $3\\to2$ האדום המפורסם ב-656 nm).\n\n"
            "**טיפ לבחינה:** כתבו $n_f$ במפורש לפני בחירת שם הסדרה. "
            "לימן = UV, בלמר = נראה, פשן = IR."
        ),
    },
    {
        "explanation_en": (
            "Rutherford's nuclear model correctly placed a dense positive nucleus at the centre, "
            "but it treated electrons as classical particles in circular orbits.\n\n"
            "According to **classical electrodynamics**, any accelerating charge (including an electron "
            "in circular motion) must radiate electromagnetic energy. This radiation would cause the "
            "electron to lose energy and **spiral inward**, collapsing the atom in approximately "
            "$10^{-12}$ seconds.\n\n"
            "**Common error:** Stating that Rutherford's model \"couldn't explain the nucleus.\" "
            "The nucleus was Rutherford's discovery — the failure is about **electron stability** "
            "and the lack of discrete spectral lines.\n\n"
            "**Exam tip:** Pair each model with its specific failure: Thomson (no nucleus), "
            "Rutherford (spiral collapse), Bohr (hydrogen only, no electron-electron interactions)."
        ),
        "explanation_he": (
            "מודל רתרפורד הגרעיני הציב נכון גרעין חיובי דחוס במרכז, "
            "אך התייחס לאלקטרונים כחלקיקים קלאסיים במסלולים מעגליים.\n\n"
            "לפי **אלקטרודינמיקה קלאסית**, כל מטען מאיץ (כולל אלקטרון בתנועה מעגלית) חייב לפלוט "
            "אנרגיה אלקטרומגנטית. קרינה זו תגרום לאלקטרון לאבד אנרגיה ו**להיסחף פנימה**, "
            "וקריסת האטום תוך כ-$10^{-12}$ שניות.\n\n"
            "**טעות נפוצה:** לטעון שמודל רתרפורד \"לא הסביר את הגרעין\". "
            "הגרעין הוא גילוי רתרפורד — הכשל הוא ב**יציבות האלקטרון** "
            "ובהיעדר קווי ספקטרום בדידים.\n\n"
            "**טיפ לבחינה:** צמדו כל מודל לכשל הייחודי שלו: תומסון (אין גרעין), "
            "רתרפורד (קריסה אלקטרונית), בוהר (מימן בלבד, ללא אינטראקציות בין-אלקטרוניות)."
        ),
    },
    {
        "explanation_en": (
            "Apply the Bohr energy formula for hydrogen:\n"
            "$$E_n = -\\frac{13.6}{n^2}\\text{ eV}$$\n\n"
            "For $n=5$:\n"
            "$$E_5 = -\\frac{13.6}{25} = -0.544\\text{ eV}$$\n\n"
            "The negative sign confirms the electron is bound. The binding energy is $|E_5|=0.544$ eV — "
            "much less tightly bound than the ground state (13.6 eV).\n\n"
            "**Common error:** Forgetting to square $n$ in the denominator, giving $-13.6/5=-2.72$ eV. "
            "Another slip: dropping the minus sign.\n\n"
            "**Self-check:** Verify with $n=1$: $E_1=-13.6$ eV (ground state). "
            "With $n=2$: $E_2=-3.4$ eV. The pattern $E_n\\propto 1/n^2$ should hold.\n\n"
            "**Exam tip:** Higher $n$ means energy closer to zero (less bound). "
            "As $n\\to\\infty$, $E_n\\to0$ (ionization threshold). Level $n=5$ is weakly bound at only 0.544 eV."
        ),
        "explanation_he": (
            "יישמו את נוסחת האנרגיה של בוהר למימן:\n"
            "$$E_n = -\\frac{13.6}{n^2}\\text{ eV}$$\n\n"
            "עבור $n=5$:\n"
            "$$E_5 = -\\frac{13.6}{25} = -0.544\\text{ eV}$$\n\n"
            "הסימן השלילי מאשר שהאלקטרון קשור. אנרגיית הקשר היא $|E_5|=0.544$ eV — "
            "קשור הרבה פחות חזק ממצב היסוד (13.6 eV).\n\n"
            "**טעות נפוצה:** שכחת ריבוע $n$ במכנה, וקבלת $-13.6/5=-2.72$ eV. "
            "טעות נוספת: הזנחת הסימן השלילי.\n\n"
            "**בדיקה:** אמתו עם $n=1$: $E_1=-13.6$ eV. עם $n=2$: $E_2=-3.4$ eV. "
            "הדפוס $E_n\\propto 1/n^2$ צריך להתקיים.\n\n"
            "**טיפ לבחינה:** $n$ גבוה יותר פירושו אנרגיה קרובה יותר לאפס (פחות קשור). "
            "כש-$n\\to\\infty$, $E_n\\to0$ (סף יינון). רמה $n=5$ קשורה חלש ב-0.544 eV בלבד."
        ),
    },
    {
        "explanation_en": (
            "A 1.9 eV photon matches the energy difference between the $n=3$ and $n=2$ levels:\n"
            "$$E_3 - E_2 = -1.511 - (-3.4) = 1.889\\text{ eV} \\approx 1.9\\text{ eV}$$\n\n"
            "Since the final level is $n_f=2$, this is a **Balmer series** transition ($3\\to2$). "
            "The corresponding wavelength is $\\lambda=1240/1.89\\approx656$ nm — the red H-alpha line.\n\n"
            "**Common error:** Naming the series by the initial level ($n=3$) instead of the final level ($n=2$). "
            "Another mistake: confusing emission (electron falling) with absorption.\n\n"
            "**Self-check:** Compute $\\lambda=1240/1.89\\approx656$ nm — red visible light confirms Balmer.\n\n"
            "**Exam tip:** When given photon energy, compute all nearby $\\Delta E$ values and match. "
            "Then identify the series from $n_f$. The $3\\to2$ line is the brightest Balmer line in hydrogen spectra."
        ),
        "explanation_he": (
            "פוטון של 1.9 eV תואם את הפרש האנרגיה בין רמות $n=3$ ו-$n=2$:\n"
            "$$E_3 - E_2 = -1.511 - (-3.4) = 1.889\\text{ eV} \\approx 1.9\\text{ eV}$$\n\n"
            "מכיוון שהרמה הסופית $n_f=2$, זהו מעבר **סדרת בלמר** ($3\\to2$). "
            "אורך הגל המתאים $\\lambda=1240/1.89\\approx656$ nm — קו H-alpha האדום.\n\n"
            "**טעות נפוצה:** קריאה לסדרה לפי הרמה ההתחלתית ($n=3$) במקום הסופית ($n=2$). "
            "טעות נוספת: בלבול בין פליטה (ירידה) לקליטה.\n\n"
            "**בדיקה:** $\\lambda=1240/1.89\\approx656$ nm — אור אדום נראה מאשר בלמר.\n\n"
            "**טיפ לבחינה:** כשניתנת אנרגיית פוטון, חשבו את כל ערכי $\\Delta E$ הסמוכים והתאימו. "
            "ואז זהו את הסדרה לפי $n_f$. קו $3\\to2$ הוא קו הבלמר הבהיר ביותר בספקטרום מימן."
        ),
    },
    {
        "explanation_en": (
            "Ionization energy is the energy required to remove an electron from a bound state to $E=0$ (free).\n\n"
            "From the ground state ($n=1$):\n"
            "$$E_{\\text{ion}} = 0 - E_1 = 0 - (-13.6) = 13.6\\text{ eV}$$\n\n"
            "This is also $|E_1|$ — the magnitude of the ground-state binding energy. "
            "It takes 13.6 eV to completely free a hydrogen electron from its most tightly bound orbit.\n\n"
            "**Common error:** Answering 13.6 eV without explaining that ionization means reaching $E=0$. "
            "Another slip: using $E_n=+13.6/n^2$ (wrong sign convention).\n\n"
            "**Self-check:** The Rydberg constant for hydrogen is 13.6 eV — this is exactly the ground-state ionization energy.\n\n"
            "**Exam tip:** Ionization from $n=2$ requires only 3.4 eV. Always check which level the question specifies. "
            "Binding energy $|E_n|$ decreases as $n$ increases."
        ),
        "explanation_he": (
            "אנרגיית יינון היא האנרגיה הנדרשת להסרת אלקטרון ממצב קשור ל-$E=0$ (חופשי).\n\n"
            "ממצב היסוד ($n=1$):\n"
            "$$E_{\\text{ion}} = 0 - E_1 = 0 - (-13.6) = 13.6\\text{ eV}$$\n\n"
            "זה גם $|E_1|$ — גודל אנרגיית הקשר במצב היסוד. "
            "נדרשים 13.6 eV כדי לשחרר לחלוטין אלקטרון מימן מהמסלול הכי קשור.\n\n"
            "**טעות נפוצה:** מענה 13.6 eV בלי להסביר שיינון פירושו הגעה ל-$E=0$. "
            "טעות נוספת: שימוש ב-$E_n=+13.6/n^2$ (קונבנציית סימן שגויה).\n\n"
            "**בדיקה:** קבוע רידברג למימן הוא 13.6 eV — זו בדיוק אנרגיית היינון ממצב היסוד.\n\n"
            "**טיפ לבחינה:** יינון מ-$n=2$ דורש רק 3.4 eV. תמיד בדקו איזו רמה השאלה מציינת. "
            "אנרגיית הקשר $|E_n|$ קטנה ככל ש-$n$ גדל."
        ),
    },
    {
        "explanation_en": (
            "Calculate the energy difference for the $n=4\\to n=1$ transition:\n"
            "$$E_4 = -\\frac{13.6}{16} = -0.85\\text{ eV}, \\quad E_1 = -13.6\\text{ eV}$$\n"
            "$$\\Delta E = E_1 - E_4 = -13.6 - (-0.85) = -12.75\\text{ eV}$$\n\n"
            "Photon energy $=12.75$ eV. Wavelength:\n"
            "$$\\lambda = \\frac{1240}{12.75} \\approx 97.3\\text{ nm}$$\n\n"
            "This is in the **UV region** — it belongs to the **Lyman series** (final level $n_f=1$).\n\n"
            "**Common error:** Sign error giving wrong $\\Delta E$, "
            "or using $hc=1240$ with energy in joules.\n\n"
            "**Self-check:** $\\lambda=97$ nm is UV — consistent with Lyman series (large energy jump to $n=1$).\n\n"
            "**Exam tip:** Large $\\Delta E$ (big jump) → short $\\lambda$ (UV). Small jump → long $\\lambda$ (visible/IR). "
            "The $4\\to1$ line is one of the higher-energy Lyman transitions."
        ),
        "explanation_he": (
            "חשבו את הפרש האנרגיה למעבר $n=4\\to n=1$:\n"
            "$$E_4 = -\\frac{13.6}{16} = -0.85\\text{ eV}, \\quad E_1 = -13.6\\text{ eV}$$\n"
            "$$\\Delta E = E_1 - E_4 = -13.6 - (-0.85) = -12.75\\text{ eV}$$\n\n"
            "אנרגיית פוטון $=12.75$ eV. אורך גל:\n"
            "$$\\lambda = \\frac{1240}{12.75} \\approx 97.3\\text{ nm}$$\n\n"
            "זה ב**אזור UV** — שייך ל**סדרת לימן** (רמה סופית $n_f=1$).\n\n"
            "**טעות נפוצה:** שגיאת סימן ב-$\\Delta E$, "
            "או שימוש ב-$hc=1240$ עם אנרגיה בג'אול.\n\n"
            "**בדיקה:** $\\lambda=97$ nm הוא UV — עקבי עם סדרת לימן (קפיצת אנרגיה גדולה ל-$n=1$).\n\n"
            "**טיפ לבחינה:** $\\Delta E$ גדול (קפיצה גדולה) → $\\lambda$ קצר (UV). קפיצה קטנה → $\\lambda$ ארוך (נראה/IR). "
            "קו $4\\to1$ הוא אחד ממעברי הלימן בעלי האנרגיה הגבוהה."
        ),
    },
    {
        "explanation_en": (
            "When a hydrogen atom is excited to $n=3$, it can emit photons through all possible "
            "**downward** transitions until reaching the ground state.\n\n"
            "The distinct transitions are: $3\\to2$, $3\\to1$, and $2\\to1$. "
            "Total $= \\binom{3}{2} = 3$ spectral lines.\n\n"
            "Each line has a unique energy and wavelength. The atom may cascade "
            "(e.g. $3\\to2\\to1$), producing two photons in sequence, but the spectrum shows all three lines.\n\n"
            "**Common error:** Counting only direct transitions from $n=3$ ($3\\to2$ and $3\\to1$) "
            "and forgetting the $2\\to1$ line that appears when the atom passes through $n=2$.\n\n"
            "**Exam tip:** Use $\\binom{n_{\\max}}{2}$ for quick counting. "
            "Verify by listing all pairs with $n_i > n_f$."
        ),
        "explanation_he": (
            "כשאטום מימן מעורר ל-$n=3$, הוא יכול לפלוט פוטונים דרך כל המעברים "
            "**כלפי מטה** האפשריים עד הגעה למצב היסוד.\n\n"
            "המעברים השונים: $3\\to2$, $3\\to1$, ו-$2\\to1$. "
            "סה\"כ $= \\binom{3}{2} = 3$ קווי ספקטרום.\n\n"
            "לכל קו אנרgy ואורך גל ייחודיים. האטום עשוי לרדת בcascade "
            "(למשל $3\\to2\\to1$), ולייצר שני פוטונים ברצף, אך הספקטרום מציג את שלושת הקווים.\n\n"
            "**טעות נפוצה:** ספירה רק של מעברים ישירים מ-$n=3$ ($3\\to2$ ו-$3\\to1$) "
            "ושכחת קו $2\\to1$ שמופיע כשהאטום עובר דרך $n=2$.\n\n"
            "**טיפ לבחינה:** השתמשו ב-$\\binom{n_{\\max}}{2}$ לספירה מהירה. "
            "אמתו על ידי רישום כל הזוגות עם $n_i > n_f$."
        ),
    },
    {
        "explanation_en": (
            "Convert photon wavelength to energy, then find the matching Bohr level:\n\n"
            "**Step 1:** $E = hc/\\lambda = 1240/122 \\approx 10.2$ eV.\n\n"
            "**Step 2:** Add to ground-state energy:\n"
            "$$E_{\\text{new}} = E_1 + 10.2 = -13.6 + 10.2 = -3.4\\text{ eV}$$\n\n"
            "**Step 3:** Match to $E_n = -13.6/n^2$:\n"
            "$$-3.4 = -13.6/4 \\Rightarrow n=2$$\n\n"
            "The electron absorbed the photon and jumped from $n=1$ to $n=2$ (first excited state). "
            "Note: $10.2$ eV is exactly $|E_2-E_1|=12.09$ eV... actually $|E_2-E_1|=|-3.4-(-13.6)|=10.2$ eV ✓.\n\n"
            "**Common error:** Subtracting photon energy instead of adding (absorption vs emission confusion). "
            "Another slip: using $\\lambda$ in metres instead of nm with the 1240 shortcut.\n\n"
            "**Self-check:** $n=2$ is the first excited state — the most common absorption target in hydrogen problems.\n\n"
            "**Exam tip:** For absorption, always **add** photon energy to the initial level. "
            "For emission, subtract. The 122 nm photon is in the Lyman UV region."
        ),
        "explanation_he": (
            "המרת אורך גל פוטון לאנרגיה, ואז מציאת רמת בוהר מתאימה:\n\n"
            "**שלב 1:** $E = 1240/122 \\approx 10.2$ eV.\n\n"
            "**שלב 2:** חיבור לאנרגיית מצב היסוד:\n"
            "$$E_{\\text{new}} = E_1 + 10.2 = -13.6 + 10.2 = -3.4\\text{ eV}$$\n\n"
            "**שלב 3:** התאמה ל-$E_n = -13.6/n^2$:\n"
            "$$-3.4 = -13.6/4 \\Rightarrow n=2$$\n\n"
            "האלקטרון קלט את הפוטון וקפץ מ-$n=1$ ל-$n=2$ (מצב מעורר ראשון). "
            "שימו לב: $10.2$ eV הוא בדיוק $|E_2-E_1|=|-3.4-(-13.6)|=10.2$ eV ✓.\n\n"
            "**טעות נפוצה:** חיסור אנרגיית פוטון במקום חיבור (בלבול קליטה/פליטה). "
            "טעות נוספת: שימוש ב-$\\lambda$ במטרים במקום nm עם קיצור 1240.\n\n"
            "**בדיקה:** $n=2$ הוא מצב מעורר ראשון — יעד הקליטה הנפוץ ביותר בבעיות מימן.\n\n"
            "**טיפ לבחינה:** בקליטה, תמיד **חברו** אנרגיית פוטון לרמה ההתחלתית. "
            "בפליטה, חסרו. הפוטון 122 nm נמצא באזור UV של לימן."
        ),
    },
]


def apply_expansion(data):
    ex_num = 0
    cp_num = 0
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "intro":
            sec.update(SECTION_BODIES["intro"])
        elif kind == "definition":
            sec.update(SECTION_BODIES["definition"])
        elif kind == "theory":
            sec.update(SECTION_BODIES["theory"])
        elif kind == "worked_example":
            ex_num += 1
            sec.update(SECTION_BODIES[f"worked_example_{ex_num}"])
        elif kind == "checkpoint":
            cp_num += 1
            sec.update(SECTION_BODIES[f"checkpoint_{cp_num}"])
        elif kind == "method_guide":
            sec.update(SECTION_BODIES["method_guide"])
        elif kind == "pitfall":
            sec.update(SECTION_BODIES["pitfall"])
        elif kind == "why_matters":
            sec.update(SECTION_BODIES["why_matters"])
        elif kind == "before_exam":
            sec.update(SECTION_BODIES["before_exam"])
        elif kind == "summary":
            sec.update(SECTION_BODIES["summary"])

    for i, q in enumerate(data["questions"]):
        if i < len(QUESTION_EXPLANATIONS):
            q.update(QUESTION_EXPLANATIONS[i])

    return data


def validate_depth(data):
    issues = []
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind in MIN_WORDS:
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS[kind]["en"]:
                issues.append(f"{kind} EN: {en_w} < {MIN_WORDS[kind]['en']}")
            if he_w < MIN_WORDS[kind]["he"]:
                issues.append(f"{kind} HE: {he_w} < {MIN_WORDS[kind]['he']}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"{kind} HE weak parity")
        elif kind == "worked_example":
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            n = sec.get("example_number", "?")
            if en_w < MIN_WORDS["worked_example"]["en"]:
                issues.append(f"worked_example {n} EN: {en_w}")
            if he_w < MIN_WORDS["worked_example"]["he"]:
                issues.append(f"worked_example {n} HE: {he_w}")
            if hebrew_body_weak(sec.get("body_he_md"), sec.get("body_en_md")):
                issues.append(f"worked_example {n} HE weak")

    for q in data["questions"]:
        for lang in ("en", "he"):
            key = f"explanation_{lang}"
            w = word_count(q.get(key, ""))
            if w < 80 or w > 150:
                issues.append(f"Q{q['ord']} {key}: {w} words")

    return issues


def main():
    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)

    data = apply_expansion(data)

    issues = validate_depth(data)
    if issues:
        print("DEPTH ISSUES:")
        for i in issues:
            print(f"  - {i}")
        raise SystemExit(1)
    else:
        print("All depth gates passed.")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {OUT}")

    result = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(result.returncode)
    print("seed-lessons --dry-run OK")


if __name__ == "__main__":
    main()
