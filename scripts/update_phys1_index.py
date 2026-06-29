#!/usr/bin/env python3
"""Update lessons-index.generated.json with the 5 Physics 1 university lessons."""
import json, os

INDEX_PATH = os.path.join("apps", "web", "src", "lib", "lessons-index.generated.json")

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    index = json.load(f)

# New/updated entries for the 5 Physics 1 lessons
phys1_entries = {
    "rigid_body_torque_equilibrium": {
        "id": "rigid_body_torque_equilibrium",
        "title_en": "Rigid Body Statics — Torque & Equilibrium (University)",
        "title_he": "סטטיקה של גוף קשיח — מומנט ושיווי משקל (אוניברסיטה)",
        "est_minutes": 28,
        "math_track": ["university_physics_1"],
        "subject": "university_physics_1",
        "duration_min": 28,
        "type": "interactive",
        "level_min": "university",
    },
    "harmonic_oscillation": {
        "id": "harmonic_oscillation",
        "title_en": "Harmonic Oscillations — SHM, Pendula, and Damping (University)",
        "title_he": "תנודות הרמוניות — SHM, מטוטלות ובלימה (אוניברסיטה)",
        "est_minutes": 26,
        "math_track": ["university_physics_1"],
        "subject": "university_physics_1",
        "duration_min": 26,
        "type": "interactive",
        "level_min": "university",
    },
    "fluids_hydrostatics": {
        "id": "fluids_hydrostatics",
        "title_en": "Fluids — Hydrostatics and Bernoulli's Equation (University)",
        "title_he": "נוזלים — הידרוסטטיקה ומשוואת ברנולי (אוניברסיטה)",
        "est_minutes": 26,
        "math_track": ["university_physics_1"],
        "subject": "university_physics_1",
        "duration_min": 26,
        "type": "interactive",
        "level_min": "university",
    },
    "center_of_mass_uni": {
        "id": "center_of_mass_uni",
        "title_en": "Center of Mass and Systems of Particles — Calculus Treatment (University)",
        "title_he": "מרכז מסה ומערכות חלקיקים — גישה בחשבון אינטגרלי (אוניברסיטה)",
        "est_minutes": 25,
        "math_track": ["university_physics_1"],
        "subject": "university_physics_1",
        "duration_min": 25,
        "type": "interactive",
        "level_min": "university",
    },
    "angular_momentum_particles": {
        "id": "angular_momentum_particles",
        "title_en": "Angular Momentum — Particles, Rigid Bodies, and Rolling (University)",
        "title_he": "תנע זוויתי — חלקיקים, גופים קשיחים וגלגול (אוניברסיטה)",
        "est_minutes": 27,
        "math_track": ["university_physics_1"],
        "subject": "university_physics_1",
        "duration_min": 27,
        "type": "interactive",
        "level_min": "university",
    },
}

ids_in_index = {entry["id"] for entry in index}
updated = 0
added = 0

new_index = []
for entry in index:
    if entry["id"] in phys1_entries:
        new_index.append(phys1_entries[entry["id"]])
        updated += 1
    else:
        new_index.append(entry)

# Add any new entries not already present
for eid, edata in phys1_entries.items():
    if eid not in ids_in_index:
        new_index.append(edata)
        added += 1

# Sort by id to keep consistent with existing order
new_index.sort(key=lambda x: x["id"])

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    json.dump(new_index, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Updated {updated} existing entries, added {added} new entries.")
print(f"Total entries: {len(new_index)}")
