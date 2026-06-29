#!/usr/bin/env python3
"""Update lessons-index.generated.json with the 5 makhina/3pt lessons."""
import json
import os

INDEX_PATH = os.path.join("apps", "web", "src", "lib", "lessons-index.generated.json")

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    index = json.load(f)

makhina_3pt_entries = {
    "basic_statistics_3pt": {
        "id": "basic_statistics_3pt",
        "title_en": "Basic Statistics — Friendly Numbers, Real Stories",
        "title_he": "סטטיסטיקה בסיסית — מספרים ידידותיים, סיפורים אמיתיים",
        "est_minutes": 25,
        "math_track": ["3pt"],
        "subject": "high_school_math_3pt",
        "duration_min": 25,
        "type": "interactive",
        "level_min": "3pt",
    },
    "fractions_and_ratios": {
        "id": "fractions_and_ratios",
        "title_en": "Fractions & Ratios — Building Confidence Step by Step",
        "title_he": "שברים ויחסים — צעד אחר צעד, בביטחון",
        "est_minutes": 25,
        "math_track": ["makhina"],
        "subject": "makhina",
        "duration_min": 25,
        "type": "interactive",
        "level_min": "makhina",
    },
    "geometry_area_perimeter": {
        "id": "geometry_area_perimeter",
        "title_en": "Area & Perimeter — Shapes Around You",
        "title_he": "שטח והיקף — צורות מסביבכם",
        "est_minutes": 25,
        "math_track": ["makhina"],
        "subject": "makhina",
        "duration_min": 25,
        "type": "interactive",
        "level_min": "makhina",
    },
    "linear_equations_basics": {
        "id": "linear_equations_basics",
        "title_en": "Linear Equations — Your First Steps to Algebra",
        "title_he": "משוואות לינאריות — הצעדים הראשונים שלכם לאלגברה",
        "est_minutes": 25,
        "math_track": ["makhina"],
        "subject": "makhina",
        "duration_min": 25,
        "type": "interactive",
        "level_min": "makhina",
    },
    "percentages_and_interest": {
        "id": "percentages_and_interest",
        "title_en": "Percentages & Simple Interest — Math You Use Every Day",
        "title_he": "אחוזים וריבית פשוטה — מתמטיקה מהיום-יום",
        "est_minutes": 25,
        "math_track": ["makhina"],
        "subject": "makhina",
        "duration_min": 25,
        "type": "interactive",
        "level_min": "makhina",
    },
}

ids_in_index = {entry["id"] for entry in index}
updated = 0
added = 0

new_index = []
for entry in index:
    if entry["id"] in makhina_3pt_entries:
        new_index.append(makhina_3pt_entries[entry["id"]])
        updated += 1
    else:
        new_index.append(entry)

for eid, edata in makhina_3pt_entries.items():
    if eid not in ids_in_index:
        new_index.append(edata)
        added += 1

new_index.sort(key=lambda x: x["id"])

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    json.dump(new_index, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Updated {updated} existing entries, added {added} new entries.")
print(f"Total entries: {len(new_index)}")
