"""
Update lessons-index.generated.json entries for biology lessons to match
the actual lesson JSON files.
"""
import json, os

INDEX_PATH = "apps/web/src/lib/lessons-index.generated.json"
LESSONS_DIR = "scripts/seed_data/lessons"

BIOLOGY_LESSONS = ["cell_structure.json", "heredity_mendelian.json", "natural_selection.json"]

# Load index
with open(INDEX_PATH, encoding="utf-8") as f:
    index = json.load(f)

# Build lookup from lesson files
lesson_data = {}
for fname in BIOLOGY_LESSONS:
    path = os.path.join(LESSONS_DIR, fname)
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    concept_id = d["concept_id"]
    lesson_data[concept_id] = {
        "id": concept_id,
        "title_en": d["title_en"],
        "title_he": d["title_he"],
        "est_minutes": d["est_minutes"],
        "math_track": d["math_track"],
    }

# Update matching entries in index
updated = 0
for entry in index:
    cid = entry.get("id")
    if cid in lesson_data:
        entry.update(lesson_data[cid])
        updated += 1

# Write back
with open(INDEX_PATH, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"Updated {updated} biology entries in lessons-index.generated.json")
