#!/usr/bin/env python3
"""
Update lessons-index.generated.json with the 5 university Physics 2 lessons.
Run from the monorepo root.
"""
import json, os

INDEX_PATH = "apps/web/src/lib/lessons-index.generated.json"

with open(INDEX_PATH, encoding="utf-8") as f:
    index = json.load(f)

# The 4 lessons that already have stubs in the index — update them in place.
updates = {
    "electric_field_gauss": {
        "title_en": "Gauss's Law — Electric Flux and Symmetric Fields",
        "title_he": "חוק גאוס — שטף חשמלי ושדות בעלי סימטריה",
        "est_minutes": 30,
        "subject": "university_physics_2",
        "math_track": ["university_physics_2"],
        "type": "interactive",
        "level_min": "university",
        "duration_min": 30,
    },
    "magnetic_field_biot_savart": {
        "title_en": "Biot-Savart Law — Magnetic Fields from Currents",
        "title_he": "חוק ביו-סבר — שדות מגנטיים מזרמים",
        "est_minutes": 30,
        "subject": "university_physics_2",
        "math_track": ["university_physics_2"],
        "type": "interactive",
        "level_min": "university",
        "duration_min": 30,
    },
    "ampere_law": {
        "title_en": "Ampère's Law — Magnetic Fields from Symmetric Currents",
        "title_he": "חוק אמפר — שדות מגנטיים מזרמים סימטריים",
        "est_minutes": 30,
        "subject": "university_physics_2",
        "math_track": ["university_physics_2"],
        "type": "interactive",
        "level_min": "university",
        "duration_min": 30,
    },
    "maxwell_equations": {
        "title_en": "Maxwell's Equations and Electromagnetic Waves",
        "title_he": "משוואות מקסוול וגלים אלקטרומגנטיים",
        "est_minutes": 35,
        "subject": "university_physics_2",
        "math_track": ["university_physics_2"],
        "type": "interactive",
        "level_min": "university",
        "duration_min": 35,
    },
}

updated_ids = set()
for entry in index:
    eid = entry.get("id")
    if eid in updates:
        entry.update(updates[eid])
        updated_ids.add(eid)

# Add faraday_induction_uni (new entry, not yet in index)
new_entry = {
    "id": "faraday_induction_uni",
    "title_en": "Faraday's Law and Electromagnetic Induction — University Level",
    "title_he": "חוק פאראדיי והשראה אלקטרומגנטית — רמה אוניברסיטאית",
    "est_minutes": 35,
    "subject": "university_physics_2",
    "math_track": ["university_physics_2"],
    "type": "interactive",
    "level_min": "university",
    "duration_min": 35,
}

# Only add if not already there
if not any(e.get("id") == "faraday_induction_uni" for e in index):
    index.append(new_entry)
    print("Added faraday_induction_uni to index.")

# Sort by id for clean diffs
index.sort(key=lambda e: e.get("id", ""))

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"Updated {len(updated_ids)} existing entries: {', '.join(sorted(updated_ids))}")
print("Done.")
