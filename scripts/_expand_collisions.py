#!/usr/bin/env python3
"""Expand collisions.json — MIN_WORDS, Hebrew parity, 80-150 word explanations."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/seed_data/lessons/collisions.json"

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
    "checkpoint": {"en": 90, "he": 75},
    "exercise_set": {"en": 90, "he": 75},
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


SECTION_BODIES = {
    "intro": {
        "body_en_md": (
            "Collisions are everywhere in physics — billiard balls exchanging momentum, "
            "car crashes dissipating kinetic energy, subatomic particles scattering in "
            "accelerators. Despite the diversity of scales, they all obey one universal "
            "rule: **momentum is conserved** whenever no significant external force acts "
            "on the colliding system during the brief interaction.\n\n"
            "The key classification you must internalize:\n"
            "- **Elastic collision:** kinetic energy $K$ is also conserved (ideal model; "
            "billiard balls, atomic collisions at low energy).\n"
            "- **Inelastic collision:** $K$ is not conserved — some transforms to heat, "
            "sound, or permanent deformation.\n"
            "- **Perfectly inelastic:** the objects stick together afterward — maximum "
            "possible $K$ loss for given initial momenta.\n\n"
            "**Conservation of momentum** follows from Newton's 3rd law: internal collision "
            "forces are equal and opposite, so their impulses cancel and total $\\vec{p}$ "
            "is unchanged. This holds in 1D and 2D — always resolve momentum into "
            "components when directions change.\n\n"
            "**Course relevance:** Collision analysis appears in classical mechanics exams, "
            "nuclear scattering, astrophysics (galactic mergers), and engineering crash "
            "testing. Mastering the decision table here transfers directly to all these "
            "contexts. This lesson builds on `concept:momentum`."
        ),
        "body_he_md": (
            "התנגשויות נפוצות בכל מקום בפיזיקה — כדורי ביליארד שמחליפים תנע, "
            "תאונות דרכים שמפזרות אנרגיה קינטית, חלקיקים תת-אטומיים שמתפזרים "
            "במאיץ. למרות גיוון הסקלות, כולן מצייתות לכלל אחד: **תנע מתשמר** "
            "כאשר אין כוח חיצוני משמעותי על מערכת ההתנגשות במהלך האינטראקציה הקצרה.\n\n"
            "הסיווג שחובה לשלוט בו:\n"
            "- **התנגשות אלסטית:** גם $K$ מתשמרת (מודל אידיאלי; ביליארד, התנגשויות אטומיות).\n"
            "- **התנגשות לא-אלסטית:** $K$ לא מתשמרת — חלק הופך לחום, קול או עיוות.\n"
            "- **לא-אלסטית מוחלטת:** הגופים נדבקים — אובדן $K$ מקסימלי לתנע התחלתי נתון.\n\n"
            "**שימור תנע** נובע מחוק שלישי של ניוטון: כוחות פנימיים שווים ומנוגדים, "
            "המתקפים מתאזנים ו-$\\vec{p}$ הכולל לא משתנה. זה נכון ב-1D וב-2D — "
            "תמיד פרקו תנע לרכיבים כשהכיוונים משתנים.\n\n"
            "**רלוונטיות לקורס:** ניתוח התנגשויות מופיע בבחינות מכניקה, פיזור גרעיני, "
            "אסטרופיזיקה ובדיקות התרסקות. שליטה בטבלת ההחלטה כאן מעבירה ישירות "
            "להקשרים אלה. השיעור מבוסס על `concept:momentum`."
        ),
    },
    "definition": {
        "body_en_md": (
            "### Conservation of momentum (always valid)\n"
            "$$\\vec{p}_{total,i} = \\vec{p}_{total,f}: \\quad "
            "m_1\\vec{v}_1 + m_2\\vec{v}_2 = m_1\\vec{v}_1' + m_2\\vec{v}_2'.$$\n"
            "This applies to **every** collision type — elastic, inelastic, or perfectly "
            "inelastic — as long as external forces (friction with the track, gravity "
            "during a very brief impact) are negligible compared to the internal "
            "collision forces. Momentum is a **vector**: in 2D you must conserve each "
            "component separately.\n\n"
            "### Elastic collision ($K$ conserved)\n"
            "$$\\frac{1}{2}m_1v_1^2 + \\frac{1}{2}m_2v_2^2 = "
            "\\frac{1}{2}m_1v_1'^2 + \\frac{1}{2}m_2v_2'^2.$$\n"
            "Real macroscopic collisions are rarely perfectly elastic, but billiard "
            "balls and low-energy atomic collisions approximate this well.\n\n"
            "**Closed-form solution for 1D elastic collision:**\n"
            "$$v_1' = \\frac{m_1-m_2}{m_1+m_2}v_1 + \\frac{2m_2}{m_1+m_2}v_2,$$\n"
            "$$v_2' = \\frac{2m_1}{m_1+m_2}v_1 + \\frac{m_2-m_1}{m_1+m_2}v_2.$$\n\n"
            "**Special case — equal masses ($m_1=m_2$):** velocities **exchange**: "
            "$v_1'=v_2$, $v_2'=v_1$.\n\n"
            "### Perfectly inelastic collision\n"
            "$$m_1v_1 + m_2v_2 = (m_1+m_2)v_f.$$\n"
            "Both objects move together at final speed $v_f$. This gives the "
            "**maximum** kinetic energy loss for given initial momenta.\n\n"
            "### Energy lost in perfectly inelastic collision\n"
            "$$\\Delta KE = \\frac{1}{2}\\frac{m_1m_2}{m_1+m_2}(v_1-v_2)^2.$$\n\n"
            "### 2D: component form\n"
            "$$x: \\; m_1v_{1x}+m_2v_{2x}=m_1v_{1x}'+m_2v_{2x}'.$$\n"
            "$$y: \\; m_1v_{1y}+m_2v_{2y}=m_1v_{1y}'+m_2v_{2y}'.$$"
        ),
        "body_he_md": (
            "### שימור תנע (תמיד תקף)\n"
            "$$m_1\\vec{v}_1+m_2\\vec{v}_2=m_1\\vec{v}_1'+m_2\\vec{v}_2'.$$\n"
            "זה חל על **כל** סוג התנגשות — אלסטית, לא-אלסטית או לא-אלסטית מוחלטת — "
            "כל עוד כוחות חיצוניים (חיכוך, כבידה במהלך פגיעה קצרה) זניחים "
            "לעומת כוחות ההתנגשות הפנימיים. תנע הוא **וקטור**: ב-2D "
            "יש לשמר כל רכיב בנפרד.\n\n"
            "### התנגשות אלסטית ($K$ מתשמרת)\n"
            "$$\\tfrac{1}{2}m_1v_1^2+\\tfrac{1}{2}m_2v_2^2="
            "\\tfrac{1}{2}m_1v_1'^2+\\tfrac{1}{2}m_2v_2'^2.$$\n"
            "התנגשויות מאקרוסקופיות נדירות אלסטיות לגמרי, אך ביליארד "
            "והתנגשויות אטומיות באנרגיה נמוכה מקורבות לכך.\n\n"
            "**פתרון סגור 1D:**\n"
            "$$v_1'=\\frac{m_1-m_2}{m_1+m_2}v_1+\\frac{2m_2}{m_1+m_2}v_2, \\quad "
            "v_2'=\\frac{2m_1}{m_1+m_2}v_1+\\frac{m_2-m_1}{m_1+m_2}v_2.$$\n\n"
            "**מקרה מיוחד — מסות שוות ($m_1=m_2$):** **חלפת מהירויות**: "
            "$v_1'=v_2$, $v_2'=v_1$.\n\n"
            "### התנגשות לא-אלסטית מוחלטת\n"
            "$$m_1v_1+m_2v_2=(m_1+m_2)v_f.$$\n"
            "שני הגופים נעים יחד ב-$v_f$. זה נותן **אובדן $K$ מקסימלי** "
            "לתנע התחלתי נתון.\n\n"
            "### אנרגיה שאבדה (לא-אלסטית מוחלטת)\n"
            "$$\\Delta KE=\\frac{1}{2}\\frac{m_1m_2}{m_1+m_2}(v_1-v_2)^2.$$\n\n"
            "### 2D — שימור לפי רכיבים\n"
            "$x$: $\\sum m_i v_{ix}=\\sum m_i v_{ix}'$. "
            "$y$: $\\sum m_i v_{iy}=\\sum m_i v_{iy}'$."
        ),
    },
    "theory": {
        "body_en_md": (
            "### Center-of-mass velocity\n"
            "$$v_{cm} = \\frac{m_1v_1 + m_2v_2}{m_1+m_2}.$$\n"
            "The CM velocity is **unchanged** by any collision (momentum conservation). "
            "In the CM frame, total momentum is always zero before and after impact.\n\n"
            "### CM frame and elastic collisions\n"
            "In the CM frame, momenta are equal and opposite before collision. For an "
            "**elastic** collision in the CM frame, each object simply **reverses** its "
            "CM-frame velocity: $u_1' = -u_1$, $u_2' = -u_2$. This dramatically "
            "simplifies scattering analysis in nuclear and particle physics.\n\n"
            "### Coefficient of restitution $e$\n"
            "$$e = -\\frac{v_{1f}-v_{2f}}{v_{1i}-v_{2i}} = "
            "\\frac{\\text{relative speed after}}{\\text{relative speed before}}.$$\n"
            "- $e = 1$: perfectly elastic.\n"
            "- $e = 0$: perfectly inelastic (objects stick together).\n"
            "- $0 < e < 1$: partially inelastic.\n\n"
            "For 1D collisions with known $e$, combine momentum conservation with "
            "$v_1' - v_2' = -e(v_1 - v_2)$ to solve for final velocities.\n\n"
            "### 2D collisions: counting equations\n"
            "In 2D with two unknown final velocity vectors (4 unknowns: two speeds, two "
            "angles), momentum gives **2 equations** (x and y). An elastic collision "
            "adds a 3rd equation (KE conservation). A partially inelastic 2D problem "
            "with one final angle or speed given is typically solvable; without extra "
            "information, the system is under-determined."
        ),
        "body_he_md": (
            "### מהירות מרכז המסה\n"
            "$$v_{\\text{מ\"מ}}=\\frac{m_1v_1+m_2v_2}{m_1+m_2}.$$\n"
            "מהירות מ\"מ **לא משתנה** בשום התנגשות (שימור תנע). "
            "במערכת מ\"מ, התנע הכולל תמיד אפס לפני ואחרי.\n\n"
            "### מערכת מ\"מ והתנגשות אלסטית\n"
            "במערכת מ\"מ, התנעים שווים ומנוגדים לפני ההתנגשות. בהתנגשות **אלסטית** "
            "במערכת מ\"מ, כל גוף פשוט **הופך** את מהירותו: $u_1'=-u_1$, $u_2'=-u_2$. "
            "זה מפשט ניתוח פיזור בפיזיקה גרעינית.\n\n"
            "### מקדם שחזור $e$\n"
            "$$e=\\frac{v_{2f}-v_{1f}}{v_{1i}-v_{2i}}="
            "\\frac{\\text{מהירות יחסית לאחר}}{\\text{מהירות יחסית לפני}}.$$\n"
            "- $e=1$: אלסטית. $e=0$: לא-אלסטית מוחלטת. $0<e<1$: חלקית.\n\n"
            "ב-1D עם $e$ ידוע, שלבו שימור תנע עם "
            "$v_1'-v_2'=-e(v_1-v_2)$ לפתרון מהירויות סופיות.\n\n"
            "### התנגשות 2D — ספירת משוואות\n"
            "ב-2D עם שני וקטורי מהירות סופיים (4 נעלמים), תנע נותן **2 משוואות**. "
            "התנגשות אלסטית מוסיפה משוואה שלישית (שימור $K$). "
            "בעיה לא-אלסטית 2D עם זווית או מהירות סופית אחת נתונה — בדרך כלל פתירה; "
            "ללא מידע נוסף — המערכת לא-מוגדרת ויש לדרוש נתון נוסף."
        ),
    },
}

# Additional sections loaded from companion file to keep script manageable
exec((Path(__file__).parent / "_expand_collisions_bodies.py").read_text(encoding="utf-8"))

QUESTION_EXPLANATIONS = _QUESTION_EXPLANATIONS  # noqa: F821


def apply_expansion(data):
    cp_idx = 0
    for sec in data["sections"]:
        kind = sec.get("kind")
        if kind == "intro":
            sec.update(SECTION_BODIES["intro"])
        elif kind == "definition":
            sec.update(SECTION_BODIES["definition"])
        elif kind == "theory":
            sec.update(SECTION_BODIES["theory"])
        elif kind == "worked_example":
            n = sec.get("example_number")
            sec.update(SECTION_BODIES[f"worked_example_{n}"])
        elif kind == "checkpoint":
            cp_idx += 1
            sec.update(SECTION_BODIES[f"checkpoint_{cp_idx}"])
            # body_en_md / body_he_md stay as question stems
        elif kind == "method_guide":
            sec.update(SECTION_BODIES["method_guide"])
        elif kind == "exercise_set":
            sec.update(SECTION_BODIES["exercise_set"])
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
        if kind == "checkpoint":
            for field, lang in (
                ("checkpoint_solution_en", "en"),
                ("checkpoint_solution_he", "he"),
            ):
                w = word_count(sec.get(field, ""))
                if w < MIN_WORDS["checkpoint"][lang]:
                    issues.append(f"checkpoint {field}: {w}")
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
        elif kind in MIN_WORDS:
            en_w = word_count(sec.get("body_en_md", ""))
            he_w = word_count(sec.get("body_he_md", ""))
            if en_w < MIN_WORDS[kind]["en"]:
                issues.append(f"{kind} EN: {en_w} < {MIN_WORDS[kind]['en']}")
            if he_w < MIN_WORDS[kind]["he"]:
                issues.append(f"{kind} HE: {he_w} < {MIN_WORDS[kind]['he']}")
            if sec.get("body_he_md") and hebrew_body_weak(
                sec.get("body_he_md"), sec.get("body_en_md")
            ):
                issues.append(f"{kind} HE weak parity")

    for q in data["questions"]:
        for lang in ("en", "he"):
            key = f"explanation_{lang}"
            w = word_count(q.get(key, ""))
            if w < 80 or w > 150:
                issues.append(f"q{q['ord']} {key}: {w} words")
            if lang == "he" and hebrew_body_weak(
                q.get("explanation_he"), q.get("explanation_en")
            ):
                issues.append(f"q{q['ord']} expl-he-weak")

    return issues


def main():
    data = json.loads(OUT.read_text(encoding="utf-8"))
    data = apply_expansion(data)

    issues = validate_depth(data)
    if issues:
        print("VALIDATION FAILED:")
        for i in issues:
            print(" ", i)
        sys.exit(1)

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")

    r = subprocess.run(
        ["node", "scripts/seed-lessons.mjs", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(r.returncode)
    print("All depth gates OK; seed-lessons dry-run passed.")


if __name__ == "__main__":
    main()
