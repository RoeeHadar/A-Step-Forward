#!/usr/bin/env python3
"""Fix Hebrew gaps (identical body_he_md) and remove stub lessons from index/curriculum."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "scripts/seed_data/lessons"
INDEX_PATH = ROOT / "apps/web/src/lib/lessons-index.generated.json"
CURRICULUM_PATH = ROOT / "apps/web/src/lib/curriculum-categories.ts"
TRANSLATIONS_PATH = ROOT / "scripts/_hebrew_section_translations.json"

# Stub lesson IDs → replacement (str/list) or None to drop
STUB_REPLACEMENTS: dict[str, str | list[str] | None] = {
    "3d_solids_volume": None,
    "spatial_reasoning": None,
    "linear_programming_two_variables": None,
    "series_convergence_tests": None,
    "capacitors_dielectrics": None,
    "fluids_bernoulli": None,
    "pythagorean_theorem": "geometry_basics",
    "circle_area_circumference": "circles",
    "similar_triangles": "triangles_congruence",
    "linear_equations_one_variable": "equations_linear",
    "linear_functions": "functions_linear",
    "quadratic_model_fitting": "functions_quadratic",
    "exponential_growth_decay_models": "functions_exponential",
    "plane_trigonometry_right_triangle": "trigonometry_ratios",
    "percentages_applications": "percentages_and_interest",
    "scatter_plot_correlation_intro": "statistics_descriptive",
    "binomial_distribution_bernoulli": "distributions",
    "trigonometric_identities": "trigonometry_identities",
    "trigonometric_equations": "trigonometry_equations",
    "euclidean_geometry_circles": "circles",
    "vectors_kinematics_2d_3d": ["kinematics_2d", "vectors_2d"],
    "newton_laws_general": "newton_laws",
    "work_energy_power": "work_energy",
    "momentum_impulse_collisions": "momentum",
    "electrostatics_coulomb": "electrostatics",
    "electric_potential": "electric_field",
    "dc_circuits_kirchhoff": "kirchhoff_laws",
    "em_waves_propagation": "maxwell_equations",
    "geometric_optics": "optics_geometric",
    "interference_diffraction": "optics_physical",
    "continuity_uniform": "continuity",
    "derivatives_implicit": "derivatives_applications",
    "lhopital_rule": "derivatives_rules",
    "optimization_related_rates": "optimization_problems",
    "integration_partial_fractions": "integration_by_parts",
    "riemann_integral_ftc": "definite_integrals",
    "improper_integrals": "integrals_intro",
    "power_series_radius": "taylor_formula",
    "multivariable_limits": "limits",
    "gradient_directional_derivative": "partial_derivatives",
    "linear_systems_gaussian_elimination": "la_matrices",
    "matrix_operations_inverse": "la_matrices",
    "determinants_cramer": "la_determinants",
    "vector_spaces_basis_dimension": "la_vector_spaces",
    "linear_transformations_kernel_image": "la_matrices",
    "inner_product_gram_schmidt": "la_orthogonality",
    "orthogonal_matrices": "la_orthogonality",
    "discrete_distributions_binomial_poisson": "distributions",
}

STUB_TITLE_HE: dict[str, str] = {
    "binomial_distribution_bernoulli": "התפלגות בינומית וברנולי",
    "capacitors_dielectrics": "קבלים ודיאלקטריקים",
    "circle_area_circumference": "מעגל — שטח והיקף",
    "continuity_uniform": "רציפות אחידה",
    "derivatives_implicit": "נגזרות משתמות",
    "determinants_cramer": "דטרמיננטות וכלל קramer",
    "discrete_distributions_binomial_poisson": "התפלגויות בדידות — בינומית ופואסון",
    "electric_potential": "פוטנציאל חשמלי",
    "electrostatics_coulomb": "אלקטרוסטטיקה — חוק קולון",
    "em_waves_propagation": "גלים אלקטרומגנטיים",
    "euclidean_geometry_circles": "גיאומטריה אוקלידית — מעגלים",
    "exponential_growth_decay_models": "מודלים של גדילה ודעיכה מעריכית",
    "fluids_bernoulli": "נוזלים — משוואת ברנולי",
    "gradient_directional_derivative": "גרדיאנט ונגזרת כיוונית",
    "improper_integrals": "אינטגרלים לא אמתיים",
    "inner_product_gram_schmidt": "מכפלה פנימית ו-Gram-Schmidt",
    "integration_partial_fractions": "אינטגרציה בשברים חלקיים",
    "interference_diffraction": "התאבכות ועקיפה",
    "lhopital_rule": "כלל לופיטל",
    "linear_equations_one_variable": "משוואות לינאריות במשתנה אחד",
    "linear_functions": "פונקציות לינאריות",
    "linear_programming_two_variables": "תכנון לינארי בשני משתנים",
    "linear_systems_gaussian_elimination": "מערכות לינאריות — שיטת גaus",
    "linear_transformations_kernel_image": "העתקות לינאריות — גרעין ותמונה",
    "matrix_operations_inverse": "פעולות מטריצות והפוכה",
    "multivariable_limits": "גבולות של פונקציות רב-משתניות",
    "optimization_related_rates": "קצבים קשורים",
    "orthogonal_matrices": "מטריצות אורתוגונליות",
    "percentages_applications": "יישומי אחוזים",
    "plane_trigonometry_right_triangle": "טריגונומטריה במשולש ישר-זווית",
    "power_series_radius": "טורי חזקות ורדיוס התכנסות",
    "pythagorean_theorem": "משפט פיתגורס",
    "quadratic_model_fitting": "התאמת מודל ריבועי",
    "riemann_integral_ftc": "אינטגרל רiemann ומשפט היסוד",
    "scatter_plot_correlation_intro": "גרף פיזור ומתאם",
    "series_convergence_tests": "מבחני התכנסות לטורים",
    "similar_triangles": "משולשים דומים",
    "spatial_reasoning": "חשיבה מרחבית",
    "trigonometric_equations": "משוואות טריגונומטריות",
    "trigonometric_identities": "זהויות טריגונומטריות",
    "vector_spaces_basis_dimension": "מרחבי וקטורים — בסיס וממד",
    "vectors_kinematics_2d_3d": "וקטורים וקינמטיקה ב-2D/3D",
    "3d_solids_volume": "גופים תלת-ממדיים — נפח",
}


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_stub_lesson(d: dict) -> bool:
    sections = d.get("sections", [])
    if not sections:
        return True
    en = sections[0].get("body_en_md", sections[0].get("body_en", ""))
    return "Coming soon" in str(en) and not d.get("questions")


def apply_hebrew_translations() -> int:
    if not TRANSLATIONS_PATH.exists():
        print(f"SKIP Hebrew: {TRANSLATIONS_PATH} not found")
        return 0
    translations: dict[str, list[str]] = load_json(TRANSLATIONS_PATH)  # type: ignore
    updated = 0
    for lesson_id, he_bodies in translations.items():
        path = LESSONS_DIR / f"{lesson_id}.json"
        if not path.exists():
            print(f"WARN: no file for {lesson_id}")
            continue
        d = load_json(path)
        sections = d.get("sections", [])
        if len(he_bodies) != len(sections):
            print(f"WARN: {lesson_id} section count mismatch {len(he_bodies)} vs {len(sections)}")
            continue
        changed = False
        for i, he in enumerate(he_bodies):
            en = sections[i].get("body_en_md", "")
            if sections[i].get("body_he_md", "").strip() != en.strip():
                continue
            sections[i]["body_he_md"] = he
            changed = True
        if changed:
            save_json(path, d)
            updated += 1
            print(f"Hebrew: updated {lesson_id}")
    return updated


def resolve_concept_id(cid: str) -> list[str]:
    if cid not in STUB_REPLACEMENTS:
        return [cid]
    repl = STUB_REPLACEMENTS[cid]
    if repl is None:
        return []
    if isinstance(repl, list):
        return repl
    return [repl]


def dedupe_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def fix_curriculum() -> None:
    text = CURRICULUM_PATH.read_text(encoding="utf-8")

    def replace_array_block(match: re.Match[str]) -> str:
        prefix, body, suffix = match.group(1), match.group(2), match.group(3)
        ids = re.findall(r"'([a-z][a-z0-9_]*)'", body)
        new_ids: list[str] = []
        for cid in ids:
            new_ids.extend(resolve_concept_id(cid))
        new_ids = dedupe_preserve(new_ids)
        if not new_ids:
            return match.group(0)
        formatted = ",\n          ".join(f"'{x}'" for x in new_ids)
        if "\n" in body:
            return f"{prefix}\n          {formatted},\n        {suffix}"
        return f"{prefix} {formatted} {suffix}"

    # Replace concept_ids arrays in sections and const arrays
    pattern = re.compile(
        r"(concept_ids:\s*\[)([^\]]*?)(\])",
        re.DOTALL,
    )
    text = pattern.sub(replace_array_block, text)

    # Fix const arrays like MATH_3PT_NEW_CONCEPTS = [...]
    const_pattern = re.compile(
        r"(const\s+[A-Z_0-9]+\s*=\s*\[)([^\]]*?)(\];)",
        re.DOTALL,
    )

    def replace_const(match: re.Match[str]) -> str:
        prefix, body, suffix = match.group(1), match.group(2), match.group(3)
        ids = re.findall(r"'([a-z][a-z0-9_]*)'", body)
        if not ids:
            return match.group(0)
        new_ids: list[str] = []
        for cid in ids:
            new_ids.extend(resolve_concept_id(cid))
        new_ids = dedupe_preserve(new_ids)
        lines = ",\n  ".join(f"'{x}'" for x in new_ids)
        return f"{prefix}\n  {lines},\n{suffix}"

    text = const_pattern.sub(replace_const, text)

    CURRICULUM_PATH.write_text(text, encoding="utf-8")
    print("Curriculum: replaced stub concept IDs")


def remove_stubs_from_index() -> int:
    index: list[dict] = load_json(INDEX_PATH)  # type: ignore
    kept: list[dict] = []
    removed = 0
    for entry in index:
        lid = entry["id"]
        path = LESSONS_DIR / f"{lid}.json"
        if path.exists():
            d = load_json(path)
            if is_stub_lesson(d):
                removed += 1
                print(f"Index: removed stub {lid}")
                continue
        kept.append(entry)
    save_json(INDEX_PATH, kept)
    return removed


def fix_stub_title_he() -> None:
    """Fix title_he identical to title_en on remaining stub files (if any stay)."""
    for stub_id, title_he in STUB_TITLE_HE.items():
        path = LESSONS_DIR / f"{stub_id}.json"
        if not path.exists():
            continue
        d = load_json(path)
        if d.get("title_he") == d.get("title_en"):
            d["title_he"] = title_he
            save_json(path, d)


def main() -> None:
    n_he = apply_hebrew_translations()
    fix_curriculum()
    n_idx = remove_stubs_from_index()
    fix_stub_title_he()
    print(f"Done: {n_he} lessons Hebrew, {n_idx} stubs removed from index")


if __name__ == "__main__":
    main()
