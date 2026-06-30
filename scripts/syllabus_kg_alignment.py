#!/usr/bin/env python3
"""Syllabus KG alignment: create missing lesson stubs + update lessons index."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts" / "seed_data" / "lessons"
INDEX_PATH = ROOT / "apps" / "web" / "src" / "lib" / "lessons-index.generated.json"
CAT_PATH = ROOT / "apps" / "web" / "src" / "lib" / "curriculum-categories.ts"

# Priority tracks → category id in curriculum-categories.ts
PRIORITY_TRACKS = {
    "calculus_1": "CALCULUS_1_CONCEPTS",
    "hs_physics": "HS_PHYSICS_CONCEPTS",
    "high_school_math_5pt": ("MATH_5PT_NEW_CONCEPTS", "MATH_5PT_KG_LEGACY"),
    "linear_algebra": "LINEAR_ALGEBRA_CONCEPTS",
}

# New concepts needing stubs (not yet in lessons dir)
NEW_STUBS: dict[str, dict] = {
    "number_sets_review": {
        "subject": "calculus_1",
        "title_en": "Number Sets Review — ℕ, ℤ, ℚ, ℝ",
        "title_he": "חזרה על קבוצות מספרים — ℕ, ℤ, ℚ, ℝ",
        "math_track": ["calc1"],
        "level_min": "calculus_1",
    },
    "function_basics_uni": {
        "subject": "calculus_1",
        "title_en": "Functions — Domain, Range, Injectivity & Surjectivity",
        "title_he": "פונקציות — תחום, טווח, חד-חד-ערכיות ועל",
        "math_track": ["calc1"],
        "level_min": "calculus_1",
    },
    "limits_at_infinity": {
        "subject": "calculus_1",
        "title_en": "Limits at Infinity & Horizontal Asymptotes",
        "title_he": "גבולות באינסוף ואסימפטוטות אופקיות",
        "math_track": ["calc1"],
        "level_min": "calculus_1",
    },
    "continuity_discontinuity": {
        "subject": "calculus_1",
        "title_en": "Continuity & Types of Discontinuity",
        "title_he": "רציפות וסוגי אי-רציפות",
        "math_track": ["calc1"],
        "level_min": "calculus_1",
    },
    "function_investigation_uni": {
        "subject": "calculus_1",
        "title_en": "Full Function Analysis (University Level)",
        "title_he": "חקירת פונקציות — רמה אוניברסיטאית",
        "math_track": ["calc1"],
        "level_min": "calculus_1",
    },
    "absolute_extrema": {
        "subject": "calculus_1",
        "title_en": "Absolute Extrema on a Closed Interval",
        "title_he": "קיצון מוחלט בקטע סגור",
        "math_track": ["calc1"],
        "level_min": "calculus_1",
    },
    "antiderivatives": {
        "subject": "calculus_1",
        "title_en": "Antiderivatives & Indefinite Integrals",
        "title_he": "פונקציה קדומה ואינטגרל לא מסוים",
        "math_track": ["calc1"],
        "level_min": "calculus_1",
    },
    "definite_integral_area": {
        "subject": "calculus_1",
        "title_en": "Definite Integrals & Area Calculation",
        "title_he": "אינטגרל מסוים וחישוב שטחים",
        "math_track": ["calc1"],
        "level_min": "calculus_1",
    },
    "systems_linear_equations": {
        "subject": "linear_algebra",
        "title_en": "Systems of Linear Equations — Gaussian Elimination",
        "title_he": "מערכות משוואות לינאריות — elimination של גאוס",
        "math_track": ["la"],
        "level_min": "university",
    },
    "matrix_representation": {
        "subject": "linear_algebra",
        "title_en": "Matrices as Linear Transformations",
        "title_he": "מטריצות כהצגה של העתקות לינאריות",
        "math_track": ["la"],
        "level_min": "university",
    },
    "data_representation": {
        "subject": "high_school_math_3pt",
        "title_en": "Data Representation — Histograms, Bar & Pie Charts",
        "title_he": "ייצוג נתונים — היסטוגרמה, מקלות ועוגה",
        "math_track": ["3pt"],
        "level_min": "3pt",
    },
    "linear_regression_3pt": {
        "subject": "high_school_math_3pt",
        "title_en": "Linear Regression & Correlation (3 Units)",
        "title_he": "רגרסיה לינארית ומתאם (3 יחידות)",
        "math_track": ["3pt"],
        "level_min": "3pt",
    },
    "limits_4pt": {
        "subject": "high_school_math_4pt",
        "title_en": "Intuitive Limits (4 Units)",
        "title_he": "גבולות — מושג אינטואיטיבי (4 יחידות)",
        "math_track": ["4pt"],
        "level_min": "4pt",
    },
    "implicit_differentiation": {
        "subject": "high_school_math_5pt",
        "title_en": "Implicit Differentiation",
        "title_he": "גזירה סתומה",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "algebra_review": {
        "subject": "high_school_math_5pt",
        "title_en": "Implicit Differentiation",
        "title_he": "גזירה סתומה",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "combinatorics_5pt": {
        "subject": "high_school_math_5pt",
        "title_en": "Combinatorics — Permutations, Combinations & Binomial Theorem",
        "title_he": "קומבינטוריקה — תמורות, צירופים ובינום",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "algebra_review": {
        "subject": "makhina",
        "title_en": "Algebra Review — Equations, Inequalities & Factoring",
        "title_he": "חזרה על אלגברה — משוואות, אי-שוויונות ופירוק",
        "math_track": ["makhina"],
        "level_min": "makhina",
    },
    "quadratic_equations_makhina": {
        "subject": "makhina",
        "title_en": "Quadratic Equations & Factoring (מכינה)",
        "title_he": "משוואות ריבועיות ופירוק לגורמים (מכינה)",
        "math_track": ["makhina"],
        "level_min": "makhina",
    },
    "functions_makhina": {
        "subject": "makhina",
        "title_en": "Functions — Domain, Range & Graph Transformations (מכינה)",
        "title_he": "פונקציות — תחום, טווח וטרנספורמציות (מכינה)",
        "math_track": ["makhina"],
        "level_min": "makhina",
    },
    "trigonometry_makhina": {
        "subject": "makhina",
        "title_en": "Trigonometry — Identities & Equations (מכינה)",
        "title_he": "טריגונומטריה — זהויות ומשוואות (מכינה)",
        "math_track": ["makhina"],
        "level_min": "makhina",
    },
    "exponential_logarithmic": {
        "subject": "makhina",
        "title_en": "Exponential & Logarithmic Functions (מכינה)",
        "title_he": "פונקציות מעריכיות ולוגריתמיות (מכינה)",
        "math_track": ["makhina"],
        "level_min": "makhina",
    },
    "calculus_intro_makhina": {
        "subject": "makhina",
        "title_en": "Intro to Derivatives & Integrals (מכינה)",
        "title_he": "מבוא לנגזרות ואינטegrals (מכינה)",
        "math_track": ["makhina"],
        "level_min": "makhina",
    },
    "mechanics_makhina": {
        "subject": "makhina_physics",
        "title_en": "Mechanics — Kinematics & Newton's Laws (Engineering Prep)",
        "title_he": "מכניקה — קינמטיקה וחוקי ניוטון (מכינה הנדסה)",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
    "energy_work_makhina": {
        "subject": "makhina_physics",
        "title_en": "Work, Energy & Power (Engineering Prep)",
        "title_he": "עבודה, אנרגיה והספק (מכינה הנדסה)",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
    "waves_sound_makhina": {
        "subject": "makhina_physics",
        "title_en": "Waves & Sound (Engineering Prep)",
        "title_he": "גלים וקול (מכינה הנדסה)",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
    "thermodynamics_makhina": {
        "subject": "makhina_physics",
        "title_en": "Thermodynamics Basics (Engineering Prep)",
        "title_he": "יסודות תרמodynamika (מכינה הנדסה)",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
    "electricity_makhina": {
        "subject": "makhina_physics",
        "title_en": "Electricity — Fields & Circuits (Engineering Prep)",
        "title_he": "חשמל — שדות ומעגלים (מכינה הנדסה)",
        "math_track": ["makhina_physics"],
        "level_min": "makhina",
    },
    "limits_5pt": {
        "subject": "high_school_math_5pt",
        "title_en": "Limits — Rigorous (5 Units)",
        "title_he": "גבולות — גישה מחמירה (5 יחידות)",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "function_analysis_4pt": {
        "subject": "high_school_math_4pt",
        "title_en": "Function Analysis (4 Units)",
        "title_he": "חקירת פונקציות (4 יחידות)",
        "math_track": ["4pt"],
        "level_min": "4pt",
    },
    "function_analysis_5pt": {
        "subject": "high_school_math_5pt",
        "title_en": "Function Analysis (5 Units)",
        "title_he": "חקירת פונקציות (5 יחידות)",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "integrals_4pt": {
        "subject": "high_school_math_4pt",
        "title_en": "Integration — Polynomial & Rational (4 Units)",
        "title_he": "אינטegration — פולינום ורציונל (4 יחידות)",
        "math_track": ["4pt"],
        "level_min": "4pt",
    },
    "derivatives_trig_exp": {
        "subject": "high_school_math_5pt",
        "title_en": "Derivatives of Trig, Exp & Log (5 Units)",
        "title_he": "נגזרות טrig, מעריכית ולוג (5 יחידות)",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "integrals_trig_exp": {
        "subject": "high_school_math_5pt",
        "title_en": "Integrals of Trig, Exp & Log (5 Units)",
        "title_he": "אינטegrals טrig, מעריכית ולוג (5 יחידות)",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "sequences_5pt": {
        "subject": "high_school_math_5pt",
        "title_en": "Sequences with Formal Proofs (5 Units)",
        "title_he": "סדרות עם הוכחות (5 יחידות)",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "complex_numbers_5pt": {
        "subject": "high_school_math_5pt",
        "title_en": "Complex Numbers & De Moivre (5 Units)",
        "title_he": "מספרים מרוכבים ודה-מואבר (5 יחידות)",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "analytic_geometry_4pt": {
        "subject": "high_school_math_4pt",
        "title_en": "Analytic Geometry — Circles & Lines (4 Units)",
        "title_he": "גאומטריה אנליטית — מעגלים וישרים (4 יחידות)",
        "math_track": ["4pt"],
        "level_min": "4pt",
    },
    "analytic_geometry_5pt": {
        "subject": "high_school_math_5pt",
        "title_en": "Analytic Geometry — Conic Sections (5 Units)",
        "title_he": "גאומטריה אנליטית — חתכי חרוט (5 יחידות)",
        "math_track": ["5pt"],
        "level_min": "5pt",
    },
    "sample_space": {
        "subject": "statistics_probability",
        "title_en": "Sample Space & Probability Axioms",
        "title_he": "מרחב מדגם ואקסיומות הסתברות",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
    "random_variables": {
        "subject": "statistics_probability",
        "title_en": "Random Variables — Discrete & Continuous",
        "title_he": "משתנים מקריים — בדידים ורציפים",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
    "sampling_estimation": {
        "subject": "statistics_probability",
        "title_en": "Sampling & Point Estimation",
        "title_he": "דגימה ואמידה נקודתית",
        "math_track": ["stats_prob"],
        "level_min": "university",
    },
}


def extract_array(name: str) -> list[str]:
    text = CAT_PATH.read_text(encoding="utf-8")
    m = re.search(rf"const {name} = \[(.*?)\];", text, re.S)
    if not m:
        return []
    return re.findall(r"'([a-z][a-z0-9_]*)'", m.group(1))


def stub_payload(concept_id: str, meta: dict) -> dict:
    return {
        "concept_id": concept_id,
        "subject": meta.get("subject", "math"),
        "level": meta.get("level_min", "intermediate"),
        "math_track": meta["math_track"],
        "title_en": meta["title_en"],
        "title_he": meta["title_he"],
        "summary_en": "Lesson stub — content to be authored.",
        "summary_he": "שיעור stub — תוכן ייכתב בהמשך.",
        "est_minutes": 20,
        "sections": [],
        "questions": [],
        "agent_hints": "Lesson stub — content to be authored.",
    }


def index_entry(concept_id: str, meta: dict) -> dict:
    return {
        "id": concept_id,
        "title_en": meta["title_en"],
        "title_he": meta["title_he"],
        "est_minutes": 20,
        "math_track": meta["math_track"],
        "subject": meta["subject"],
        "duration_min": 20,
        "type": "interactive",
        "level_min": meta["level_min"],
    }


def main() -> None:
    existing = {p.stem for p in LESSONS_DIR.glob("*.json")}
    created: list[str] = []

    for cid, meta in NEW_STUBS.items():
        if cid in existing:
            continue
        path = LESSONS_DIR / f"{cid}.json"
        path.write_text(
            json.dumps(stub_payload(cid, meta), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        created.append(cid)
        existing.add(cid)

    # Update index
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8-sig"))
    by_id = {e["id"]: e for e in index}
    for cid in created:
        meta = NEW_STUBS[cid]
        by_id[cid] = index_entry(cid, meta)
    index = sorted(by_id.values(), key=lambda e: e["id"])
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Report gaps in priority tracks after KG update (read fresh arrays)
    print(f"Created {len(created)} stub lessons:")
    for c in created:
        print(f"  + {c}")

    for track, arrays in PRIORITY_TRACKS.items():
        if isinstance(arrays, str):
            arrays = (arrays,)
        ids: list[str] = []
        for a in arrays:
            ids.extend(extract_array(a))
        ids = list(dict.fromkeys(ids))
        missing = [c for c in ids if c not in existing]
        print(f"\n{track}: {len(missing)} concepts still without lesson files")
        if missing:
            print(" ", ", ".join(missing[:20]), ("..." if len(missing) > 20 else ""))


if __name__ == "__main__":
    main()
