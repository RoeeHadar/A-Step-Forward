#!/usr/bin/env python3
"""Import content_sections and bagrut_exams from a JSON file exported by ingest_learning_db.py.

Usage (in CI):
    uv run python scripts/import_content_json.py --input tmp/content_export.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON exported by ingest_learning_db.py")
    parser.add_argument("--db-url", default="", help="Postgres URL (or DATABASE_URL env)")
    args = parser.parse_args()

    db_url = args.db_url or os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("[error] --db-url or DATABASE_URL required")
        return 1

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[error] file not found: {input_path}")
        return 1

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    sections = payload.get("sections", [])
    bagrut = payload.get("bagrut", [])

    print(f"Importing {len(sections)} sections + {len(bagrut)} bagrut rows...")

    with psycopg.connect(db_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            sec_inserted = 0
            for row in sections:
                cur.execute(
                    """
                    INSERT INTO content_sections
                        (subject, grade, source_file, chunk_index, title, body_md,
                         page_start, page_end, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                    ON CONFLICT (subject, source_file, chunk_index) DO UPDATE SET
                        grade=EXCLUDED.grade, title=EXCLUDED.title, body_md=EXCLUDED.body_md,
                        page_start=EXCLUDED.page_start, page_end=EXCLUDED.page_end, updated_at=NOW()
                    """,
                    (
                        row["subject"], row.get("grade"), row["source_file"], row["chunk_index"],
                        row["title"], row["body_md"], row.get("page_start"), row.get("page_end"),
                    ),
                )
                sec_inserted += cur.rowcount or 0

            bag_inserted = 0
            for row in bagrut:
                cur.execute(
                    """
                    INSERT INTO bagrut_exams
                        (subject, exam_type, year, source_file, display_name, file_url)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (subject, source_file) DO UPDATE SET
                        exam_type=EXCLUDED.exam_type, year=EXCLUDED.year,
                        display_name=EXCLUDED.display_name, file_url=EXCLUDED.file_url
                    """,
                    (
                        row["subject"], row.get("exam_type"), row.get("year"),
                        row["source_file"], row["display_name"], row["file_url"],
                    ),
                )
                bag_inserted += cur.rowcount or 0

        conn.commit()

    print(f"Done: {sec_inserted} sections upserted, {bag_inserted} bagrut rows upserted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
