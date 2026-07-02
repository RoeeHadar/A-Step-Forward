#!/usr/bin/env python3
"""Generate expanded modern_physics_intro.json and validate depth gates."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/modern_physics_intro.json"

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
            "Around 1900, experiments began producing results that **classical physics could not explain**. "
            "Two failures were especially dramatic:\n\n"
            "- **Blackbody radiation** — classical theory predicted infinite UV energy (the *ultraviolet catastrophe*).\n"
            "- **Photoelectric effect** — light below a threshold frequency ejects *no* electrons, no matter how bright the source.\n\n"
            "These crises led to **quantum mechanics** and **modern physics**:\n"
            "- **Planck (1900):** energy is quantized, $E=hf$.\n"
            "- **Einstein (1905):** light consists of particles (photons) with $E=hf$.\n"
            "- **de Broglie (1924):** matter has wave nature, $\\lambda=h/p$.\n"
            "- **Heisenberg (1927):** position and momentum cannot both be known precisely.\n\n"
            "In **Bagrut physics (5 units)**, you must calculate photon energy, apply the photoelectric "
            "equation $KE_{\\max}=hf-\\phi$, find threshold frequency, compute de Broglie wavelength, "
            "and state the uncertainty principle qualitatively. This lesson connects forward to "
            "`concept:atomic_models` and `concept:nuclear_physics`, and builds on logarithms and basic probability."
        ),
        "body_he_md": (
            "סביב 1900 ניסויים החלו להציג תוצאות ש**הפיזיקה הקלאסית לא יכלה להסביר**. "
            "שני כשלים היו דרמטיים במיוחד:\n\n"
            "- **קרינת גוף שחור** — התאוריה הקלאסית חזתה אנרגיית UV אינסופית (*אסון ה-UV*).\n"
            "- **אפקט פוטואלקטרי** — אור מתחת לתדר סף לא פולט אלקטרונים, לא משנה כמה חזק המקור.\n\n"
            "משברים אלה הובילו ל**מכניקת הקוונטים** ו**פיזיקה מודרנית**:\n"
            "- **פלנק (1900):** אנרגיה מקוונטת, $E=hf$.\n"
            "- **אינשטיין (1905):** אור מורכב מחלקיקים (פוטונים) עם $E=hf$.\n"
            "- **דה-ברויי (1924):** לחומר יש טבע גלי, $\\lambda=h/p$.\n"
            "- **הייזנברג (1927):** מיקום ותנע לא ניתנים לידיעה מדויקת יחד.\n\n"
            "ב**בגרות בפיזיקה (5 יחידות)** חובה לחשב אנרגיית פוטון, ליישם $KE_{\\max}=hf-\\phi$, "
            "למצוא תדר סף, לחשב אורך גל דה-ברויי ולנסח את עקרון אי-הוודאות. השיעור מוביל ל-"
            "`concept:atomic_models` ו-`concept:nuclear_physics`, ומבוסס על לוגריתמים והסתברות בסיסית."
        ),
    },
    "definition": {
        "body_en_md": (
            "**Photon energy** — the energy carried by one quantum of light:\n"
            "$$E_{\\text{photon}} = hf = \\frac{hc}{\\lambda}$$\n"
            "$h = 6.63\\times10^{-34}$ J·s (Planck's constant), $c=3\\times10^8$ m/s. "
            "In eV·nm problems, use the shortcut $hc=1240$ eV·nm.\n\n"
            "**Photoelectric effect (Einstein, 1905):**\n"
            "$$KE_{\\max} = hf - \\phi$$\n"
            "$\\phi$ = **work function** — minimum energy to eject an electron from the metal surface. "
            "Threshold frequency: $f_0=\\phi/h$. Below $f_0$, **no emission** regardless of intensity.\n\n"
            "**de Broglie wavelength (1924):**\n"
            "$$\\lambda = \\frac{h}{p} = \\frac{h}{mv}$$\n"
            "Every particle has an associated wavelength inversely proportional to momentum.\n\n"
            "**Heisenberg uncertainty principle:**\n"
            "$$\\Delta x \\cdot \\Delta p \\ge \\frac{h}{4\\pi}$$\n"
            "You cannot simultaneously know position and momentum with arbitrary precision. "
            "At low speeds, de Broglie wavelengths are tiny and quantum effects are negligible; "
            "at atomic scales they dominate. On Bagrut exams, keep $h$ and $c$ values handy and "
            "decide early whether to work in SI (J, m, s) or the eV·nm shortcut."
        ),
        "body_he_md": (
            "**אנרגיית פוטון** — האנרגיה שפוטון אחד של אור נושא:\n"
            "$$E_{\\text{photon}} = hf = \\frac{hc}{\\lambda}$$\n"
            "$h = 6.63\\times10^{-34}$ J·s (קבוע פלנק), $c=3\\times10^8$ m/s. "
            "בבעיות eV·nm השתמשו ב-$hc=1240$ eV·nm.\n\n"
            "**אפקט פוטואלקטרי (אינשטיין, 1905):**\n"
            "$$KE_{\\max} = hf - \\phi$$\n"
            "$\\phi$ = **פונקציית עבודה** — האנרגיה המינימלית לפליטת אלקטרון מפני המתכת. "
            "תדר סף: $f_0=\\phi/h$. מתחת ל-$f_0$, **אין פליטה** ללא קשר לעוצמה.\n\n"
            "**אורך גל דה-ברויי (1924):**\n"
            "$$\\lambda = \\frac{h}{p} = \\frac{h}{mv}$$\n"
            "לכל חלקיק יש אורך גל הפוך פרופורציונית לתנע.\n\n"
            "**עקרון אי-הוודאות של הייזנברג:**\n"
            "$$\\Delta x \\cdot \\Delta p \\ge \\frac{h}{4\\pi}$$\n"
            "לא ניתן לדעת מיקום ותנע במדויקות שרירותית יחד. "
            "במהירויות נמוכות אורכי גל דה-ברויי זעירים; בקנה מידה אטומי הם דומיננטיים. "
            "בבגרות, שמרו על ערכי $h$ ו-$c$ והחליטו מוקדם אם לעבוד ב-SI (J, m, s) "
            "או בקיצור eV·nm. שני המסלולים שווים — בחרו לפי הנתונים בשאלה."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Classical prediction (wrong)\n\n"
            "Classical wave theory says light is a continuous electromagnetic wave. "
            "Brighter light delivers more total energy over time — so electrons should eventually "
            "be ejected regardless of frequency, given enough intensity and exposure time.\n\n"
            "### Observed facts (Einstein's explanation)\n\n"
            "1. **Below threshold frequency $f_0$:** no electrons emitted, *no matter how bright*.\n"
            "2. **Above $f_0$:** electrons emitted **immediately**, even at very low intensity.\n"
            "3. **$KE_{\\max}=hf-\\phi$** depends on frequency, **not** intensity.\n"
            "4. **Higher intensity** → more electrons (more photons per second), but each electron's "
            "maximum KE stays the same.\n\n"
            "### Why photons explain everything\n\n"
            "Light arrives in **quanta** (photons). Each photon delivers $E=hf$ to **one** electron in "
            "a one-to-one interaction. If $hf<\\phi$, the electron cannot escape — no amount of "
            "waiting helps because each photon still carries too little energy.\n\n"
            "**Stopping potential:** $eV_s=KE_{\\max}=hf-\\phi$. The voltage needed to stop the "
            "fastest electrons measures their maximum kinetic energy directly.\n\n"
            "**Wave-particle duality:** light behaves as waves (interference) and particles (photoelectric "
            "effect); matter behaves as particles (mass) and waves (de Broglie, electron diffraction)."
        ),
        "body_he_md": (
            "### חיזוי קלאסי (שגוי)\n\n"
            "תאוריית הגל הקלאסית רואה באור גל אלקטרומגנטי רציף. "
            "אור בהיר יותר מספק יותר אנרגיה כוללת — ולכן אלקטרונים אמורים להיפלט בסופו של דבר "
            "בכל תדר, אם רק העוצמה והזמן מספיקים.\n\n"
            "### עובדות ניסוייות (הסבר אינשטיין)\n\n"
            "1. **מתחת לתדר סף $f_0$:** אין פליטת אלקטרונים, *לא משנה כמה בהיר*.\n"
            "2. **מעל $f_0$:** פליטה **מיידית**, אפילו בעוצמה נמוכה מאוד.\n"
            "3. **$KE_{\\max}=hf-\\phi$** תלוי בתדר, **לא** בעוצמה.\n"
            "4. **עוצמה גבוהה יותר** → יותר אלקטרונים (יותר פוטונים לשנייה), אך $KE_{\\max}$ של כל "
            "אלקטרון נשאר זהה.\n\n"
            "### למה פוטונים מסבירים הכל\n\n"
            "אור מגיע ב**קוונטים** (פוטונים). כל פוטון מעביר $E=hf$ ל**אלקטרון אחד** "
            "באינטראקציה אחת-לאחת. אם $hf<\\phi$, האלקטרון לא יכול לברוח — אין תועלת בהמתנה "
            "כי כל פוטון עדיין נושא מעט מדי אנרגיה.\n\n"
            "**פוטנציאל עצירה:** $eV_s=KE_{\\max}=hf-\\phi$. המתח הנדרש לעצור את האלקטרונים "
            "המהירים ביותר מודד ישירות את האנרגיה הקינטית המקסימלית.\n\n"
            "**דואליות גל-חלקיק:** אור מתנהג כגל (הפרעה) וכחלקיק (פוטואלקטרי); חומר כחלקיק (מסה) "
            "וכגל (דה-ברויי, עיפרון אלקטרונים)."
        ),
    },
    "worked_example_1": {
        "body_en_md": (
            "**Find the energy** of a photon of violet light with $\\lambda=400$ nm.\n\n"
            "### Move 1: Choose the formula\n"
            "Photon energy from wavelength: $E=hc/\\lambda$.\n\n"
            "### Move 2: Substitute in SI units\n"
            "$$E=\\frac{hc}{\\lambda}=\\frac{6.63\\times10^{-34}\\cdot3\\times10^8}{400\\times10^{-9}}"
            "=\\frac{1.989\\times10^{-25}}{4\\times10^{-7}}=4.97\\times10^{-19}\\text{ J}.$$\n\n"
            "### Move 3: Convert to eV\n"
            "$$E=\\frac{4.97\\times10^{-19}}{1.6\\times10^{-19}}\\approx3.1\\text{ eV}.$$\n\n"
            "### Move 4: Verify\n"
            "Using the shortcut: $E=1240/400=3.1$ eV ✓. Violet light (~400 nm) has photon energy "
            "around 3 eV — typical for visible photons.\n\n"
            "### Move 5: Physical context\n"
            "Visible light spans roughly 1.8–3.1 eV (700–400 nm). A 400 nm photon can ionize some "
            "materials but is below the UV threshold for many metals. Always state units in the final answer.\n\n"
            "### Move 6: Frequency check\n"
            "From $c=f\\lambda$, $f=c/\\lambda=3\\times10^8/(400\\times10^{-9})=7.5\\times10^{14}$ Hz. "
            "Cross-check: $E=hf=6.63\\times10^{-34}\\cdot7.5\\times10^{14}\\approx5.0\\times10^{-19}$ J $\\approx3.1$ eV ✓.\n\n"
            "**Answer:** $4.97\\times10^{-19}$ J $\\approx3.1$ eV. **Exam tip:** Always check whether "
            "the question asks for J or eV. The $hc=1240$ eV·nm shortcut saves time when $\\lambda$ is in nm. "
            "Shorter wavelength means higher photon energy — violet (~400 nm) is near the high-energy end of visible light. "
            "If the stem gives frequency instead of wavelength, use $E=hf$ with $h=4.14\\times10^{-15}$ eV·s."
        ),
        "body_he_md": (
            "**מצאו את האנרגיה** של פוטון באור סגול עם $\\lambda=400$ nm.\n\n"
            "### צעד 1: בחירת הנוסחה\n"
            "אנרגיית פוטון מאורך גל: $E=hc/\\lambda$.\n\n"
            "### צעד 2: הצבה ביחידות SI\n"
            "$$E=\\frac{hc}{\\lambda}=\\frac{6.63\\times10^{-34}\\cdot3\\times10^8}{400\\times10^{-9}}"
            "=\\frac{1.989\\times10^{-25}}{4\\times10^{-7}}=4.97\\times10^{-19}\\text{ J}.$$\n\n"
            "### צעד 3: המרה ל-eV\n"
            "$$E=\\frac{4.97\\times10^{-19}}{1.6\\times10^{-19}}\\approx3.1\\text{ eV}.$$\n\n"
            "### צעד 4: אימות\n"
            "בקיצור: $E=1240/400=3.1$ eV ✓. אור סגול (~400 nm) נושא ~3 eV — טיפוסי לפוטונים נראים.\n\n"
            "### צעד 5: הקשר פיזיקלי\n"
            "אור נראה בטווח ~1.8–3.1 eV (700–400 nm). פוטון 400 nm יכול ליionize חומרים מסוימים "
            "אך מתחת לסף UV לרוב המתכות. בבגרות, שאלות על אור נראה לעיתים קרובות נותנות $\\lambda$ ב-nm "
            "ומבקשות $E$ ב-eV — הקיצור $hc=1240$ חוסך זמן משמעותי.\n\n"
            "### צעד 6: בדיקת תדר\n"
            "מ-$c=f\\lambda$: $f=c/\\lambda=3\\times10^8/(400\\times10^{-9})=7.5\\times10^{14}$ Hz. "
            "אימות: $E=hf\\approx5.0\\times10^{-19}$ J $\\approx3.1$ eV ✓.\n\n"
            "**תשובה:** $4.97\\times10^{-19}$ J $\\approx3.1$ eV. **טיפ לבחינה:** בדקו אם השאלה "
            "מבקשת J או eV. $hc=1240$ eV·nm חוסך זמן כש-$\\lambda$ ב-nm. "
            "אורך גל קצר יותר → אנרגיית פוטון גבוהה יותר — סגול (~400 nm) קרוב לקצה האנרגטי של האור הנראה. "
            "אם הנתון הוא תדר ולא אורך גל, השתמשו ב-$E=hf$ עם $h=4.14\\times10^{-15}$ eV·s."
        ),
    },
    "worked_example_2": {
        "body_en_md": (
            "**Metal has work function $\\phi=2.3$ eV. Light of $\\lambda=250$ nm shines on it. Find:**\n"
            "(a) Photon energy. (b) $KE_{\\max}$. (c) Maximum speed of ejected electron.\n\n"
            "### Move 1: Photon energy (a)\n"
            "$$E=\\frac{hc}{\\lambda}=\\frac{1240}{250}=4.96\\text{ eV}$$\n"
            "(using $hc=1240$ eV·nm).\n\n"
            "### Move 2: Maximum kinetic energy (b)\n"
            "Since $E=4.96>\\phi=2.3$ eV, emission occurs:\n"
            "$$KE_{\\max}=4.96-2.3=2.66\\text{ eV}=2.66\\times1.6\\times10^{-19}=4.26\\times10^{-19}\\text{ J}.$$\n\n"
            "### Move 3: Maximum speed (c)\n"
            "$$KE=\\frac{1}{2}mv^2 \\Rightarrow v=\\sqrt{\\frac{2KE}{m_e}}"
            "=\\sqrt{\\frac{2\\cdot4.26\\times10^{-19}}{9.1\\times10^{-31}}}\\approx9.67\\times10^5\\text{ m/s}.$$\n\n"
            "### Move 4: Sanity check\n"
            "$v\\approx10^6$ m/s is non-relativistic ($v\\ll c$), so classical $KE=\\frac{1}{2}m_e v^2$ is valid. "
            "The stopping potential would be $V_s=KE_{\\max}/e=2.66$ V.\n\n"
            "**Answer:** (a) 4.96 eV, (b) 2.66 eV, (c) $9.67\\times10^5$ m/s.\n\n"
            "**Exam tip:** Always compare $hf$ to $\\phi$ first — if $hf<\\phi$, stop: no emission. "
            "Use $m_e=9.1\\times10^{-31}$ kg for electrons. Part (c) uses classical "
            "$KE=\\frac{1}{2}m_e v^2$ because ejected electrons are non-relativistic at these energies. "
            "UV light at 250 nm ($E\\approx5$ eV) is typical for photoelectric Bagrut problems — "
            "always verify $KE_{\\max}\\ge0$ before computing speed."
        ),
        "body_he_md": (
            "**למתכת פונקציית עבודה $\\phi=2.3$ eV. אור $\\lambda=250$ nm. מצאו:**\n"
            "(א) אנרגיית פוטון. (ב) $KE_{\\max}$. (ג) מהירות מקסימלית של אלקטרון נפלט.\n\n"
            "### צעד 1: אנרגיית פוטון (א)\n"
            "$$E=\\frac{hc}{\\lambda}=\\frac{1240}{250}=4.96\\text{ eV}$$\n"
            "(עם $hc=1240$ eV·nm).\n\n"
            "### צעד 2: אנרגיה קינטית מקסימלית (ב)\n"
            "מכיוון ש-$E=4.96>\\phi=2.3$ eV, יש פליטה:\n"
            "$$KE_{\\max}=4.96-2.3=2.66\\text{ eV}=2.66\\times1.6\\times10^{-19}=4.26\\times10^{-19}\\text{ J}.$$\n\n"
            "### צעד 3: מהירות מקסימalית (ג)\n"
            "$$KE=\\frac{1}{2}mv^2 \\Rightarrow v=\\sqrt{\\frac{2KE}{m_e}}"
            "=\\sqrt{\\frac{2\\cdot4.26\\times10^{-19}}{9.1\\times10^{-31}}}\\approx9.67\\times10^5\\text{ m/s}.$$\n\n"
            "### צעד 4: בדיקת סבירות\n"
            "$v\\approx10^6$ m/s אינו רלativistי ($v\\ll c$), ולכן $KE=\\frac{1}{2}m_e v^2$ תקף. "
            "פוטנציאל עצירה: $V_s=KE_{\\max}/e=2.66$ V.\n\n"
            "**תשובה:** (א) 4.96 eV, (ב) 2.66 eV, (ג) $9.67\\times10^5$ m/s.\n\n"
            "**טיפ לבחינה:** השוו $hf$ ל-$\\phi$ קודם — אם $hf<\\phi$, עצרו: אין פליטה. "
            "השתמשו ב-$m_e=9.1\\times10^{-31}$ kg. סעיף (ג) משתמש ב-$KE=\\frac{1}{2}m_e v^2$ הקלאסית "
            "כי האלקטרונים הנפלטים אינם רלativistיים. אור UV ב-250 nm ($E\\approx5$ eV) "
            "טיפוסי לשאלות פוטואלקטריות בבגרות — ודאו $KE_{\\max}\\ge0$ לפני חישוב מהירות."
        ),
    },
    "worked_example_3": {
        "body_en_md": (
            "**An electron** is accelerated through a potential difference $V=100$ V. "
            "Find its de Broglie wavelength.\n\n"
            "### Move 1: Kinetic energy gained\n"
            "$$KE=eV=1.6\\times10^{-19}\\cdot100=1.6\\times10^{-17}\\text{ J}.$$\n\n"
            "### Move 2: Velocity\n"
            "$$v=\\sqrt{\\frac{2KE}{m_e}}=\\sqrt{\\frac{2\\cdot1.6\\times10^{-17}}{9.1\\times10^{-31}}}"
            "=\\sqrt{3.516\\times10^{13}}\\approx5.93\\times10^6\\text{ m/s}.$$\n\n"
            "### Move 3: Momentum\n"
            "$$p=m_e v=9.1\\times10^{-31}\\cdot5.93\\times10^6=5.40\\times10^{-24}\\text{ kg·m/s}.$$\n\n"
            "### Move 4: de Broglie wavelength\n"
            "$$\\lambda=\\frac{h}{p}=\\frac{6.63\\times10^{-34}}{5.40\\times10^{-24}}"
            "\\approx1.23\\times10^{-10}\\text{ m}=0.123\\text{ nm}.$$\n\n"
            "### Move 5: Alternative formula\n"
            "Direct route: $\\lambda=h/\\sqrt{2m_e KE}=h/\\sqrt{2\\cdot9.1\\times10^{-31}\\cdot1.6\\times10^{-17}}"
            "\\approx0.123$ nm ✓.\n\n"
            "### Move 6: Compare scales\n"
            "Thermal electron at 300 K has $KE\\approx k_BT\\approx0.025$ eV and $\\lambda\\sim1.2$ nm. "
            "Our 100 V electron has 4000 times more energy and wavelength ~10 times shorter — "
            "entering the X-ray regime where crystal diffraction becomes possible.\n\n"
            "This is in the **X-ray range** — electron microscopes exploit this wavelength for atomic-scale imaging.\n\n"
            "**Answer:** $\\lambda\\approx0.123$ nm.\n\n"
            "**Exam tip:** For de Broglie problems, either use $\\lambda=h/\\sqrt{2m_e KE}$ directly "
            "or compute $v$ first — both paths work. Higher acceleration voltage → shorter wavelength. "
            "Compare with thermal electrons at room temperature ($\\lambda\\sim$ nm): a 100 V electron "
            "has wavelength ~1000 times shorter. Electron microscopes exploit this sub-nanometre "
            "wavelength for atomic-resolution imaging."
        ),
        "body_he_md": (
            "**אלקטרון** מאיץ דרך הפרש פוטנציאלים $V=100$ V. מצאו את אורך הגל דה-ברויי.\n\n"
            "### צעד 1: אנרגיה קינטית שנצברה\n"
            "$$KE=eV=1.6\\times10^{-19}\\cdot100=1.6\\times10^{-17}\\text{ J}.$$\n\n"
            "### צעד 2: מהירות\n"
            "$$v=\\sqrt{\\frac{2KE}{m_e}}=\\sqrt{\\frac{2\\cdot1.6\\times10^{-17}}{9.1\\times10^{-31}}}"
            "=\\sqrt{3.516\\times10^{13}}\\approx5.93\\times10^6\\text{ m/s}.$$\n\n"
            "### צעד 3: תנע\n"
            "$$p=m_e v=9.1\\times10^{-31}\\cdot5.93\\times10^6=5.40\\times10^{-24}\\text{ kg·m/s}.$$\n\n"
            "### צעד 4: אורך גל דה-ברויי\n"
            "$$\\lambda=\\frac{h}{p}=\\frac{6.63\\times10^{-34}}{5.40\\times10^{-24}}"
            "\\approx1.23\\times10^{-10}\\text{ m}=0.123\\text{ nm}.$$\n\n"
            "### צעד 5: נוסחה ישירה\n"
            "$\\lambda=h/\\sqrt{2m_e KE}\\approx0.123$ nm ✓ — אימות מהיר.\n\n"
            "### צעד 6: השוואת סדרי גודל\n"
            "אלקטרון תרמי ב-300 K נושא $KE\\approx0.025$ eV ו-$\\lambda\\sim1.2$ nm. "
            "אלקטרון 100 V נושא פי 4000 יותר אנרgy ואורך גל קצר פי ~10 — "
            "נכנס לטווח Röntgen שבו עיפרון מגביש אפשרי.\n\n"
            "זה ב**טווח Röntgen** — מיקרוסקופים אלקטרוניים מנצלים אורך גל זה לדימות ברמת האטום.\n\n"
            "**תשובה:** $\\lambda\\approx0.123$ nm.\n\n"
            "**טיפ לבחינה:** אפשר $\\lambda=h/\\sqrt{2m_e KE}$ ישירות או דרך $v$ — שני המסלולים תקפים. "
            "מתח האצה גבוה יותר → אורך גל קצר יותר. השוו לאלקטרונים תרמיים בטמפרטורת החדר "
            "($\\lambda\\sim$ nm): אלקטרון ב-100 V קצר פי ~1000. מיקroskopy אלקטרוני "
            "מנצל אורך גל sub-nanometre זה לדימות ברזולוציית אטום."
        ),
    },
    "checkpoint_1": {
        "checkpoint_solution_en": (
            "Find the energy of a photon with frequency $f=6\\times10^{14}$ Hz.\n\n"
            "**Step 1:** Write $E=hf$.\n"
            "**Step 2:** Substitute $h=6.63\\times10^{-34}$ J·s and $f=6\\times10^{14}$ Hz:\n"
            "$$E=6.63\\times10^{-34}\\cdot6\\times10^{14}=3.98\\times10^{-19}\\text{ J}.$$\n\n"
            "**Step 3:** Convert to eV:\n"
            "$$E=\\frac{3.98\\times10^{-19}}{1.6\\times10^{-19}}\\approx2.49\\text{ eV}.$$\n\n"
            "**Verify:** $f=6\\times10^{14}$ Hz corresponds to orange-red visible light (~500 nm). "
            "Check via $E=hc/\\lambda$: $1240/500=2.48$ eV ✓.\n\n"
            "**Answer:** $3.98\\times10^{-19}$ J $\\approx2.49$ eV."
        ),
        "checkpoint_solution_he": (
            "מצאו אנרגיית פוטון עם תדר $f=6\\times10^{14}$ Hz.\n\n"
            "**שלב 1:** כתבו $E=hf$.\n"
            "**שלב 2:** הציבו $h=6.63\\times10^{-34}$ J·s ו-$f=6\\times10^{14}$ Hz:\n"
            "$$E=6.63\\times10^{-34}\\cdot6\\times10^{14}=3.98\\times10^{-19}\\text{ J}.$$\n\n"
            "**שלב 3:** המרה ל-eV:\n"
            "$$E=\\frac{3.98\\times10^{-19}}{1.6\\times10^{-19}}\\approx2.49\\text{ eV}.$$\n\n"
            "**אימות:** $f=6\\times10^{14}$ Hz מתאים לאור כתום-אדום (~500 nm). "
            "בדיקה: $1240/500=2.48$ eV ✓.\n\n"
            "**תשובה:** $3.98\\times10^{-19}$ J $\\approx2.49$ eV."
        ),
    },
    "checkpoint_2": {
        "checkpoint_solution_en": (
            "A metal's work function is 1.8 eV. What is the threshold frequency?\n\n"
            "**Step 1:** At threshold, photon energy exactly equals work function: $hf_0=\\phi$.\n"
            "**Step 2:** Convert $\\phi$ to joules:\n"
            "$$\\phi=1.8\\times1.6\\times10^{-19}=2.88\\times10^{-19}\\text{ J}.$$\n\n"
            "**Step 3:** Solve for $f_0$:\n"
            "$$f_0=\\frac{\\phi}{h}=\\frac{2.88\\times10^{-19}}{6.63\\times10^{-34}}\\approx4.34\\times10^{14}\\text{ Hz}.$$\n\n"
            "**Verify:** Threshold wavelength $\\lambda_0=hc/\\phi=1240/1.8\\approx689$ nm (red light). "
            "Light with $\\lambda>689$ nm will not eject electrons.\n\n"
            "**Answer:** $f_0\\approx4.34\\times10^{14}$ Hz."
        ),
        "checkpoint_solution_he": (
            "פונקציית עבודה 1.8 eV. מה תדר הסף?\n\n"
            "**שלב 1:** בסף, אנרגיית הפוטון שווה לפונקציית העבודה: $hf_0=\\phi$.\n"
            "**שלב 2:** המרת $\\phi$ לג'ול:\n"
            "$$\\phi=1.8\\times1.6\\times10^{-19}=2.88\\times10^{-19}\\text{ J}.$$\n\n"
            "**שלב 3:** פתרון ל-$f_0$:\n"
            "$$f_0=\\frac{\\phi}{h}=\\frac{2.88\\times10^{-19}}{6.63\\times10^{-34}}\\approx4.34\\times10^{14}\\text{ Hz}.$$\n\n"
            "**אימות:** אורך גל סף $\\lambda_0=1240/1.8\\approx689$ nm (אור אדום). "
            "אור עם $\\lambda>689$ nm לא יפלוט אלקטרונים.\n\n"
            "**תשובה:** $f_0\\approx4.34\\times10^{14}$ Hz."
        ),
    },
    "method_guide": {
        "body_en_md": (
            "**Step-by-step recipe for any modern-physics problem:**\n\n"
            "| Task | Formula | Key note |\n"
            "|---|---|---|\n"
            "| Photon energy | $E=hf=hc/\\lambda$ | Use $hc=1240$ eV·nm when $\\lambda$ in nm |\n"
            "| Check if emission occurs | Compare $hf$ vs $\\phi$ | If $hf<\\phi$: **no emission** |\n"
            "| Max KE of electron | $KE_{\\max}=hf-\\phi$ | Depends on frequency, not intensity |\n"
            "| Threshold frequency | $f_0=\\phi/h$ | Below $f_0$: zero electrons |\n"
            "| Max electron speed | $v=\\sqrt{2KE_{\\max}/m_e}$ | Use $m_e=9.1\\times10^{-31}$ kg |\n"
            "| de Broglie wavelength | $\\lambda=h/(mv)=h/p$ | Higher momentum → shorter $\\lambda$ |\n"
            "| Uncertainty | $\\Delta x\\cdot\\Delta p\\ge h/(4\\pi)$ | Estimate lower bound on $\\Delta p$ |\n\n"
            "**Decision tree:** (1) Is it photon energy or photoelectric? (2) Compare $hf$ to $\\phi$. "
            "(3) If de Broglie, find momentum first. (4) Check units (eV vs J, nm vs m). "
            "(5) Verify: $KE_{\\max}\\ge0$ and $\\lambda>0$."
        ),
        "body_he_md": (
            "**מתכון שלב-אחר-שלב לכל בעיית פיזיקה מודרנית:**\n\n"
            "| משימה | נוסחה | הערה |\n"
            "|---|---|---|\n"
            "| אנרגיית פוטון | $E=hf=hc/\\lambda$ | $hc=1240$ eV·nm כש-$\\lambda$ ב-nm |\n"
            "| בדיקת פליטה | השוו $hf$ ל-$\\phi$ | אם $hf<\\phi$: **אין פליטה** |\n"
            "| $KE_{\\max}$ | $KE_{\\max}=hf-\\phi$ | תלוי בתדר, לא בעוצמה |\n"
            "| תדר סף | $f_0=\\phi/h$ | מתחת ל-$f_0$: אפס אלקטרונים |\n"
            "| מהירות מקסימalית | $v=\\sqrt{2KE_{\\max}/m_e}$ | $m_e=9.1\\times10^{-31}$ kg |\n"
            "| אורך גל דה-ברויי | $\\lambda=h/(mv)=h/p$ | תנע גבוה → $\\lambda$ קצר |\n"
            "| אי-וודאות | $\\Delta x\\cdot\\Delta p\\ge h/(4\\pi)$ | הערכת תחתית ל-$\\Delta p$ |\n\n"
            "**עץ החלטות:** (1) אנרגיית פוטון או פוטואלקטרי? (2) השוו $hf$ ל-$\\phi$. "
            "(3) דה-ברויי — מצאו תנע קודם. (4) בדקו יחידות (eV מול J, nm מול m). "
            "(5) אימות: $KE_{\\max}\\ge0$ ו-$\\lambda>0$."
        ),
    },
    "pitfall": {
        "body_en_md": (
            "1. **Confusing intensity and frequency:** Intensity affects the **number** of photons per "
            "second, not the energy per photon ($E=hf$). Brighter light below threshold still ejects nothing.\n\n"
            "2. **Forgetting the work function:** $KE_{\\max}=hf-\\phi$, not simply $hf$. "
            "The electron must overcome the binding energy $\\phi$ first.\n\n"
            "3. **Wrong units for $h$:** $h=6.63\\times10^{-34}$ J·s in SI, but $h=4.14\\times10^{-15}$ eV·s "
            "when working directly in eV and Hz. Mixing units causes errors of order $10^{19}$.\n\n"
            "4. **Misusing $hc=1240$ eV·nm:** Valid only when $\\lambda$ is in **nm** and $E$ in **eV**. "
            "If $\\lambda$ is in metres, use SI formula $E=hc/\\lambda$.\n\n"
            "**Example misconception:** Brighter light can eject electrons even below threshold.\n\n"
            "**Fix:** No. Below threshold frequency, no emission regardless of intensity or exposure time."
        ),
        "body_he_md": (
            "1. **בלבול עוצמה ותדר:** עוצמה משפיעה על **כמות** הפוטונים לשנייה, לא על האנרגיה לפוטון ($E=hf$). "
            "אור בהיר מתחת לסף עדיין לא פולט כלום.\n\n"
            "2. **שכחת פונקציית עבודה:** $KE_{\\max}=hf-\\phi$, לא רק $hf$. "
            "האלקטרון חייב להתגבר על אנרגיית הקשר $\\phi$ קודם.\n\n"
            "3. **יחידות שגויות ל-$h$:** $h=6.63\\times10^{-34}$ J·s ב-SI, אך $h=4.14\\times10^{-15}$ eV·s "
            "כשעובדים ישירות ב-eV ו-Hz. ערבוב יחידות גורם לשגיאות בסדר $10^{19}$.\n\n"
            "4. **שימוש שגוי ב-$hc=1240$ eV·nm:** תקף רק כש-$\\lambda$ ב-**nm** ו-$E$ ב-**eV**. "
            "אם $\\lambda$ במטרים, השתמשו ב-$E=hc/\\lambda$ ב-SI.\n\n"
            "**אשליה נפוצה:** אור חזק יכול לפלוט אלקטרונים גם מתחת לסף.\n\n"
            "**תיקון:** לא. מתחת לתדר סף, אין פליטה ללא קשר לעוצמה או לזמן חשיפה."
        ),
    },
    "why_matters": {
        "body_en_md": (
            "Modern physics is not an isolated topic — it is the foundation of atomic structure, "
            "spectroscopy, semiconductors, lasers, and nuclear energy.\n\n"
            "**You will use this to unlock:**\n"
            "- `concept:atomic_models` **Atomic Models & Hydrogen Spectrum** (direct prerequisite)\n"
            "- `concept:nuclear_physics` **Nuclear Physics** (mass-energy, binding energy)\n\n"
            "**Builds on:**\n"
            "- `concept:logarithms` **Logarithms** (orders of magnitude in $h$, $c$)\n"
            "- `concept:probability_basic` **Basic Probability** (quantum interpretation)\n\n"
            "**Why it matters for exams:** Bagrut 5-unit physics regularly tests photoelectric calculations "
            "and de Broglie wavelength. University courses extend these to atomic orbitals and particle physics. "
            "When studying, always ask: \"Is this a photon-energy problem or a photoelectric comparison?\""
        ),
        "body_he_md": (
            "פיזיקה מודרנית אינה נושא מבודד — היא הבסיס למבנה אטומי, ספектroskopy, מוליכים למחצה, "
            "לייזרים ואנרגיה גרעינית.\n\n"
            "**תשתמשו בזה כדי להתקדם ל:**\n"
            "- `concept:atomic_models` **מודלים אטומיים וספקטרום המימן** (דרישת קדם ישירה)\n"
            "- `concept:nuclear_physics` **פיזיקה גרעינית** (מסה-אנרגיה, אנרגיית קשר)\n\n"
            "**מבוסס על:**\n"
            "- `concept:logarithms` **לוגריתמים** (סדרי גודל ב-$h$, $c$)\n"
            "- `concept:probability_basic` **הסתברות בסיסית** (פרשנות קוונטית)\n\n"
            "**למה זה חשוב לבחינות:** בגרות 5 יחידות בודקת לעיתים קרובות חישובי פוטואלקטרי "
            "ואורך גל דה-ברויי. קורסים באוניברסיטה מרחיבים לרמות אטומיות ופיזיקת חלקיקים. "
            "בזמן לימוד, שאלו: \"האם זו בעיית אנרגיית פוטון או השוואת פוטואלקטרי?\""
        ),
    },
    "before_exam": {
        "body_en_md": (
            "**Formula checklist for Bagrut modern physics:**\n\n"
            "- Photon: $E=hf=hc/\\lambda$. Shortcut: $hc=1240$ eV·nm.\n"
            "- Photoelectric: $KE_{\\max}=hf-\\phi$. **No emission if $hf<\\phi$.**\n"
            "- Threshold: $f_0=\\phi/h$, $\\lambda_0=hc/\\phi$.\n"
            "- de Broglie: $\\lambda=h/(mv)=h/p$.\n"
            "- Uncertainty: $\\Delta x\\cdot\\Delta p\\ge h/(4\\pi)$.\n"
            "- Intensity → more photons per second, **not** higher photon energy.\n\n"
            "**Last review:** Say each formula aloud once, then solve one checkpoint without looking. "
            "Practice comparing $hf$ to $\\phi$ before any calculation — it saves time on \"no emission\" questions. "
            "For de Broglie, write $p=mv$ explicitly before dividing $h$ by momentum. "
            "Remember: intensity changes photon count, not photon energy."
        ),
        "body_he_md": (
            "**רשימת נוסחאות לבגרות — פיזיקה מודרנית:**\n\n"
            "- פוטון: $E=hf=hc/\\lambda$. קיצור: $hc=1240$ eV·nm.\n"
            "- פוטואלקטרי: $KE_{\\max}=hf-\\phi$. **אין פליטה אם $hf<\\phi$.**\n"
            "- סף: $f_0=\\phi/h$, $\\lambda_0=hc/\\phi$.\n"
            "- דה-ברויי: $\\lambda=h/(mv)=h/p$.\n"
            "- אי-וודאות: $\\Delta x\\cdot\\Delta p\\ge h/(4\\pi)$.\n"
            "- עוצמה → יותר פוטונים לשנייה, **לא** אנרגיה גבוהה יותר לפוטון.\n\n"
            "**חזרה אחרונה:** אמרו כל נוסחה בקול, ואז פתרו checkpoint אחד בלי להסתכל. "
            "תרגלו השוואת $hf$ ל-$\\phi$ לפני כל חישוב — חוסך זמן בשאלות \"אין פליטה\". "
            "בדה-ברויי, כתבו $p=mv$ במפורש לפני חלוקת $h$ בתנע."
        ),
    },
    "summary": {
        "body_en_md": (
            "**Key takeaways from this lesson:**\n\n"
            "- Light comes in **photons**: $E=hf=hc/\\lambda$.\n"
            "- **Photoelectric effect:** $KE_{\\max}=hf-\\phi$. Below threshold frequency: **no emission**, "
            "regardless of intensity.\n"
            "- **Matter waves:** every particle has $\\lambda=h/p$ (de Broglie).\n"
            "- **Quantum mechanics:** energy is discrete; measurements are probabilistic; wave-particle duality "
            "is fundamental.\n"
            "- **Heisenberg:** $\\Delta x\\cdot\\Delta p\\ge h/(4\\pi)$ limits simultaneous precision.\n\n"
            "**Takeaway:** You should now recognize whether a problem needs photon energy, photoelectric "
            "comparison, or de Broglie calculation from the wording alone."
        ),
        "body_he_md": (
            "**עיקרי השיעור:**\n\n"
            "- אור מגיע ב**פוטונים**: $E=hf=hc/\\lambda$.\n"
            "- **אפקט פוטואלקטרי:** $KE_{\\max}=hf-\\phi$. מתחת לתדר סף: **אין פליטה**, "
            "ללא קשר לעוצמה.\n"
            "- **גלי חומר:** לכל חלקיק $\\lambda=h/p$ (דה-ברויי).\n"
            "- **מכניקת קוונטים:** אנרגיה דיסקרטית; מדידות הסתברותיות; דואליות גל-חלקיק בסיסית.\n"
            "- **הייזנברג:** $\\Delta x\\cdot\\Delta p\\ge h/(4\\pi)$ מגביל דיוק simultanי.\n\n"
            "**סיכום:** כעת תוכלו לזהות אם בעיה דורשת אנרגיית פוטון, השוואת פוטואלקטרי "
            "או חישוב דה-ברויי מהניסוח בלבד."
        ),
    },
}

QUESTION_EXPLANATIONS = [
    {
        "explanation_en": (
            "Compare photon energy to the work function: $hf=2.0$ eV and $\\phi=2.5$ eV. "
            "Since $hf<\\phi$, each photon carries **insufficient energy** to eject an electron — "
            "no emission occurs, regardless of light intensity or exposure time.\n\n"
            "Option \"Yes, with KE = 0.5 eV\" subtracts in the wrong direction ($2.5-2.0$). "
            "Option \"Depends on intensity\" reflects the classical misconception that brighter light "
            "eventually ejects electrons below threshold.\n\n"
            "**Exam tip:** Always compare $hf$ to $\\phi$ **before** calculating $KE_{\\max}$. "
            "If $hf<\\phi$, the answer is simply \"no emission.\" Intensity only affects photon count, "
            "not individual photon energy. **Answer:** No."
        ),
        "explanation_he": (
            "השוו אנרגיית פוטון לפונקציית עבודה: $hf=2.0$ eV ו-$\\phi=2.5$ eV. "
            "מכיוון ש-$hf<\\phi$, כל פוטון נושא **מעט מדי אנרגיה** לפליטת אלקטרון — "
            "אין פליטה, ללא קשר לעוצמת האור או לזמן חשיפה.\n\n"
            "האפשרות \"כן, $KE=0.5$ eV\" מחסרת בכיוון שגוי ($2.5-2.0$). "
            "האפשרות \"תלוי בעוצמה\" משקפת את האשליה הקלאסית שאור חזק בסופו של דבר פולט.\n\n"
            "**טיפ לבחינה:** תמיד השוו $hf$ ל-$\\phi$ **לפני** חישוב $KE_{\\max}$. "
            "אם $hf<\\phi$, התשובה פשוט \"אין פליטה\". עוצמה משפיעה רק על כמות פוטונים, "
            "לא על אנרגיה לפוטון. **תשובה:** לא."
        ),
    },
    {
        "explanation_en": (
            "Photon energy from wavelength using the Bagrut shortcut:\n"
            "$$E = \\frac{hc}{\\lambda} = \\frac{1240}{500} = 2.48\\text{ eV}$$\n\n"
            "The shortcut $hc=1240$ eV·nm works when $\\lambda$ is in nanometres and $E$ in eV. "
            "Green light (~500 nm) has photon energy around 2.5 eV — reasonable for visible spectrum.\n\n"
            "**Common error:** Using $\\lambda=500$ m instead of $500\\times10^{-9}$ m in SI, "
            "or forgetting to convert J to eV at the end.\n\n"
            "**Self-check:** $E=hc/\\lambda$ with $\\lambda=400$ nm gives 3.1 eV (violet, higher energy). "
            "Longer wavelength → lower photon energy. **Exam tip:** Memorize $hc=1240$ eV·nm. **Answer:** 2.48 eV."
        ),
        "explanation_he": (
            "אנרגיית פוטון מאורך גל בקיצור הבגרות:\n"
            "$$E = \\frac{hc}{\\lambda} = \\frac{1240}{500} = 2.48\\text{ eV}$$\n\n"
            "הקיצור $hc=1240$ eV·nm עובד כש-$\\lambda$ ב-nm ו-$E$ ב-eV. "
            "אור ירוק (~500 nm) נושא כ-2.5 eV — סביר לטווח האור הנראה. "
            "אם השאלה נותנת תדר במקום אורך גל, השתמשו ב-$E=hf$ עם $h=4.14\\times10^{-15}$ eV·s. "
            "זהו תמיד יחידות לפני ההצבה.\n\n"
            "**טעות נפוצה:** שימוש ב-$\\lambda=500$ m במקום nm ב-SI, "
            "או שכחת המרה מ-J ל-eV בסוף. **בדיקה:** $\\lambda=400$ nm נותן 3.1 eV (סגול). "
            "אורך גל ארוך → אנרגיה נמוכה. **טיפ לבחינה:** שיננו $hc=1240$ eV·nm. **תשובה:** 2.48 eV."
        ),
    },
    {
        "explanation_en": (
            "Apply the photoelectric threshold condition: emission occurs only when $hf\\ge\\phi$. "
            "Here $E_{\\text{ph}}=1.5$ eV and $\\phi=2.0$ eV, so $hf=1.5<\\phi=2.0$ — **no emission**.\n\n"
            "Each photon delivers 1.5 eV to one electron, but 2.0 eV is needed to escape the metal surface. "
            "Increasing intensity adds more photons per second but each still carries only 1.5 eV.\n\n"
            "**Common error:** Answering \"yes, slowly\" by assuming classical energy accumulation over time. "
            "The photoelectric effect is instantaneous and quantum — one photon, one electron.\n\n"
            "**Exam tip:** Write the inequality $hf$ vs $\\phi$ explicitly. If the inequality fails, "
            "stop — do not compute $KE_{\\max}$. **Answer:** No emission."
        ),
        "explanation_he": (
            "יישמו תנאי סף פוטואלקטרי: פליטה רק כש-$hf\\ge\\phi$. "
            "כאן $E_{\\text{ph}}=1.5$ eV ו-$\\phi=2.0$ eV, ולכן $hf=1.5<\\phi=2.0$ — **אין פליטה**.\n\n"
            "כל פוטון מעביר 1.5 eV לאלקטרון אחד, אך 2.0 eV נדרשים לבריחה מפני המתכת. "
            "הגברת עוצמה מוסיפה פוטונים לשנייה אך כל אחד עדיין נושא 1.5 eV בלבד.\n\n"
            "**טעות נפוצה:** \"כן, לאט\" — הנחה קלאסית של הצטברות אנרגיה. "
            "האפקט מיידי וקוונטי — פוטון אחד, אלקטרון אחד.\n\n"
            "**טיפ לבחינה:** כתבו $hf$ מול $\\phi$ במפורש. אם אי-השוויון נכשל, "
            "עצרו — אל תחשבו $KE_{\\max}$. **תשובה:** אין פליטה."
        ),
    },
    {
        "explanation_en": (
            "In the photoelectric effect, **intensity** measures photons per unit area per unit time — "
            "it does **not** change the energy of individual photons ($E=hf$, set by frequency alone).\n\n"
            "Higher intensity → more photons arrive per second → more electrons ejected per second, "
            "but each ejected electron still has the same maximum kinetic energy $KE_{\\max}=hf-\\phi$.\n\n"
            "**Common error:** Claiming brighter light gives faster (more energetic) electrons. "
            "This confuses photon **count** with photon **energy** — a central Bagrut distinction.\n\n"
            "**Exam tip:** If the question changes intensity but not frequency, $KE_{\\max}$ is unchanged. "
            "Only the **photocurrent** (number of electrons) increases. This was Einstein's key insight in 1905."
        ),
        "explanation_he": (
            "באפקט הפוטואלקטרי, **עוצמה** מודדת פוטונים ליחידת שטח ליחידת זמן — "
            "היא **לא** משנה את אנרגיית הפוטונים הבודדים ($E=hf$, נקבע רק על ידי תדר).\n\n"
            "עוצמה גבוהה → יותר פוטונים מגיעים לשנייה → יותר אלקטרונים נפלטים לשנייה, "
            "אך לכל אלקטרון נפלט עדיין אותה $KE_{\\max}=hf-\\phi$.\n\n"
            "**טעות נפוצה:** טענה שאור בהיר נותן אלקטרונים מהירים (אנרגטיים) יותר. "
            "זה מבלבל **כמות** פוטונים עם **אנergy** פוטון — הבחנה מרכזית בבגרות.\n\n"
            "**טיפ לבחינה:** אם השאלה משנה עוצמה אך לא תדר, $KE_{\\max}$ לא משתנה. "
            "רק **זרם הפוטואלקטרי** (מספר אלקטרונים) גדל. זו תובנת המפתח של אינשטיין ב-1905."
        ),
    },
    {
        "explanation_en": (
            "de Broglie's hypothesis (1924) states that **every particle** has an associated wave "
            "with wavelength inversely proportional to its momentum:\n"
            "$$\\lambda = \\frac{h}{p} = \\frac{h}{mv}$$\n\n"
            "This unified matter and light under wave-particle duality. Electron diffraction experiments "
            "(Davisson–Germer, 1927) confirmed it: electrons scattered from crystals produce "
            "interference patterns exactly as predicted by $\\lambda=h/p$.\n\n"
            "**Common error:** Stating only \"light is a wave\" — de Broglie applies to **matter**, not light. "
            "For light, $\\lambda=c/f$; for matter, $\\lambda=h/p$.\n\n"
            "**Exam tip:** de Broglie wavelength decreases as momentum increases. "
            "A 100 V electron has $\\lambda\\approx0.12$ nm — atomic scale."
        ),
        "explanation_he": (
            "השערת דה-ברויי (1924) קובעת של**כל חלקיק** יש גל קשור "
            "שאורכו הפוך פרופורציונית לתנע:\n"
            "$$\\lambda = \\frac{h}{p} = \\frac{h}{mv}$$\n\n"
            "זה איחד חומר ואור תחת דואליות גל-חלקיק. ניסויי עיפרון אלקטרונים "
            "(Davisson–Germer, 1927) אישרו: אלקטרונים מפוזרים מגבישים יוצרים "
            "דוגמאות הפרעה בדיוק כפי שחזה $\\lambda=h/p$.\n\n"
            "**טעות נפוצה:** \"אור הוא גל\" בלבד — דה-ברויי חל על **חומר**, לא על אור. "
            "לאור: $\\lambda=c/f$; לחומר: $\\lambda=h/p$. **טיפ לבחינה:** "
            "אורך גל דה-ברויי קטן ככל שהתנע גדול. אלקטרון ב-100 V: $\\lambda\\approx0.12$ nm — "
            "קנה מידה אטומי, הבסis למיקroskopy אלקטרוני."
        ),
    },
    {
        "explanation_en": (
            "Two-step photoelectric calculation:\n"
            "**Step 1:** Photon energy: $E=hc/\\lambda=1240/200=6.2$ eV.\n"
            "**Step 2:** Compare to work function: $6.2>4.0$ eV → emission occurs.\n"
            "**Step 3:** $KE_{\\max}=hf-\\phi=6.2-4.0=2.2$ eV.\n\n"
            "UV light (200 nm) carries enough energy to overcome the 4.0 eV work function, "
            "leaving 2.2 eV as kinetic energy of the fastest electrons.\n\n"
            "**Common error:** Forgetting to subtract $\\phi$, giving $KE=6.2$ eV. "
            "Another slip: using $\\lambda=200$ m instead of 200 nm.\n\n"
            "**Exam tip:** Always compute photon energy first, then subtract work function. "
            "If $KE_{\\max}<0$, you made an arithmetic error or emission does not occur. **Answer:** 2.2 eV."
        ),
        "explanation_he": (
            "חישוב פוטואלקטרי בשני שלבים:\n"
            "**שלב 1:** אנרגיית פוטון: $E=1240/200=6.2$ eV.\n"
            "**שלב 2:** השוואה לפונקציית עבודה: $6.2>4.0$ eV → יש פליטה.\n"
            "**שלב 3:** $KE_{\\max}=6.2-4.0=2.2$ eV.\n\n"
            "אור UV (200 nm) נושא מספיק אנרגיה להתגבר על $\\phi=4.0$ eV, "
            "ומשאיר 2.2 eV כאנרגיה קינטית של האלקטרונים המהירים ביותר.\n\n"
            "**טעות נפוצה:** שכחת חיסור $\\phi$, וקבלת $KE=6.2$ eV. "
            "טעות נוספת: $\\lambda=200$ m במקום 200 nm.\n\n"
            "**טיפ לבחינה:** חשבו אנרגיית פוטון קודם, ואז חסרו פונקציית עבודה. "
            "אם $KE_{\\max}<0$ — שגיאה או אין פליטה. **תשובה:** 2.2 eV."
        ),
    },
    {
        "explanation_en": (
            "de Broglie wavelength for a moving proton:\n"
            "$$\\lambda = \\frac{h}{mv} = \\frac{6.63\\times10^{-34}}{1.67\\times10^{-27}\\cdot10^5}"
            "= \\frac{6.63\\times10^{-34}}{1.67\\times10^{-22}} \\approx 3.97\\times10^{-12}\\text{ m}$$\n\n"
            "Protons are ~1836 times heavier than electrons, so at the same speed their de Broglie "
            "wavelength is ~1836 times shorter. At $10^5$ m/s the wavelength is sub-picometre — "
            "far too small for diffraction experiments.\n\n"
            "**Common error:** Using electron mass instead of proton mass, or arithmetic slip in powers of ten.\n\n"
            "**Self-check:** $\\lambda$ should be extremely small for macroscopic particles. "
            "**Exam tip:** Write $mv$ before dividing into $h$. Check units: kg·m/s in denominator → metres in result."
        ),
        "explanation_he": (
            "אורך גל דה-ברויי לפרוטון נע:\n"
            "$$\\lambda = \\frac{h}{mv} = \\frac{6.63\\times10^{-34}}{1.67\\times10^{-27}\\cdot10^5}"
            "= \\frac{6.63\\times10^{-34}}{1.67\\times10^{-22}} \\approx 3.97\\times10^{-12}\\text{ m}$$\n\n"
            "פרוטונים כ-1836 פעמים כבדים מאלקטרונים, ולכן באותה מהירות אורך הגל "
            "קצר פי ~1836. ב-$10^5$ m/s האורך sub-picometre — קטן מדי לעיפרון ניסויי. "
            "לעומת אלקטרון באותה מהירות, $\\lambda$ קצר פי ~43 ($\\sqrt{1836}$) בגלל $\\lambda\\propto 1/m$.\n\n"
            "**טעות נפוצה:** שימוש במסת אלקטרון ($9.1\\times10^{-31}$ kg) במקום פרוטון "
            "($1.67\\times10^{-27}$ kg), או שגיאה בסדרי גודל. **בדיקה:** $\\lambda$ צריך להיות זעיר "
            "לחלקיקים מאקרוסקופיים — פרוטון ב-$10^5$ m/s נותן picometre scale. "
            "**טיפ לבחינה:** כתבו $mv$ לפני חלוקה ב-$h$. בדקו יחידות: kg·m/s במכנה → מטרים בתוצאה."
        ),
    },
    {
        "explanation_en": (
            "Classical wave theory treats light as a continuous wave whose total energy depends on "
            "amplitude (intensity). It predicts that sufficiently bright light of **any frequency** "
            "should eventually eject electrons given enough time.\n\n"
            "**Experiment contradicts this:** below threshold frequency $f_0$, **zero electrons** are "
            "emitted regardless of intensity or exposure duration. Above $f_0$, emission is **instantaneous** "
            "even at low intensity.\n\n"
            "Einstein's photon model resolves this: each photon carries $E=hf$. Below threshold, "
            "every individual photon lacks sufficient energy — waiting longer only sends more "
            "underpowered photons.\n\n"
            "**Exam tip:** Bagrut often asks this conceptually. Emphasize the **threshold frequency** "
            "and **instantaneous emission** as the two key experimental facts classical theory cannot explain."
        ),
        "explanation_he": (
            "תאוריית הגל הקלאסית רואה באור גל רציף שאנרgy הכוללת תלויה בעוצמה (amplitude). "
            "היא חוזה שאור בהיר מספיק ב**כל תדר** יפלוט אלקטרונים בסופו של דבר.\n\n"
            "**הניסוי סותר:** מתחת לתדר סף $f_0$, **אפס אלקטרונים** "
            "ללא קשר לעוצמה או לזמן חשיפה. מעל $f_0$, הפליטה **מיידית** "
            "אפילו בעוצמה נמוכה.\n\n"
            "מודל הפוטונים של אינשטיין פותר: כל פוטון נושא $E=hf$. מתחת לסף, "
            "כל פוטון בודד חסר אנרגיה — המתנה רק שולחת עוד פוטונים חלשים.\n\n"
            "**טיפ לבחינה:** בבגרות שואלים לעיתים קרובות זאת בהבנה. "
            "הדגישו **תדר סף** ו**פליטה מיידית** כשתי עובדות ניסוי שתאוריה קלאסית לא מסבירה."
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


if __name__ == "__main__":
    main()
