#!/usr/bin/env python3
"""Assisted transcription helper for official MoE Meyda Bagrut math exams.

Turns a Hebrew exam (PDF, or pre-extracted .txt when no PDF lib is installed)
into review-ready draft scaffolds in the question-store ingestion schema. The
math and mappings still need a human pass — this only removes the mechanical
work: extraction, question segmentation, and schema scaffolding.

Workflow:
  1. Drop exams in  content/question-sources/moe_meyda/_pdf/  (or _txt/).
  2. Draft:   python scripts/gen/transcribe_moe.py draft --input <file|dir> \
                  --exam-id 35582 --year 2023 --season summer
     -> writes content/question-sources/moe_meyda/_drafts/<exam>.draft.json
  3. Human fixes each item (LaTeX math, concept_id, skill_atoms, answer_payload,
     official_answer, verify) and sets "reviewed": true, then saves the file to
     content/question-sources/moe_meyda/<exam>.json  (the approved location).
  4. Check:   python scripts/gen/transcribe_moe.py check   (gates before ingest)

PDF extraction uses pymupdf / pdfplumber / pypdf if available; otherwise pass a
.txt you extracted yourself. Extraction is best-effort — always human-verify.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

DRAFTS_DIR = os.path.join("content", "question-sources", "moe_meyda", "_drafts")
APPROVED_DIR = os.path.join("content", "question-sources", "moe_meyda")

VALID_KINDS = {
    "mcq", "mcq_multi", "true_false", "open", "short_answer",
    "fill_blank", "numeric", "match", "ordering", "derivation",
}

# A question starts with "1." / "2)" / "3 ." / "שאלה 4" — best effort, RTL-safe.
QUESTION_START = re.compile(r"^\s*(?:שאלה\s*)?(\d{1,2})\s*[.)]\s*")


def extract_text(path: str) -> str:
    """Extract text from a PDF (if a lib exists) or read a .txt verbatim."""
    if path.lower().endswith(".txt"):
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    if path.lower().endswith(".pdf"):
        text = _extract_pdf(path)
        if text is None:
            raise SystemExit(
                "No PDF library available (pymupdf/pdfplumber/pypdf). "
                f"Extract '{path}' to a .txt yourself and pass that instead."
            )
        return text
    raise SystemExit(f"Unsupported input (need .pdf or .txt): {path}")


def _extract_pdf(path: str):
    try:
        import fitz  # pymupdf

        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    except Exception:
        pass
    try:
        import pdfplumber

        with pdfplumber.open(path) as pdf:
            return "\n".join((page.extract_text() or "") for page in pdf.pages)
    except Exception:
        pass
    try:
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return None


def segment_questions(text: str) -> list[tuple[str, str]]:
    """Split raw exam text into (number, body) chunks by question markers."""
    chunks: list[tuple[str, str]] = []
    current_num = None
    buf: list[str] = []
    for line in text.splitlines():
        m = QUESTION_START.match(line)
        if m:
            if current_num is not None:
                chunks.append((current_num, "\n".join(buf).strip()))
            current_num = m.group(1)
            buf = [QUESTION_START.sub("", line, count=1)]
        elif current_num is not None:
            buf.append(line)
    if current_num is not None:
        chunks.append((current_num, "\n".join(buf).strip()))
    return chunks


def scaffold(num: str, body: str, meta: dict) -> dict:
    """One draft item in the ingestion schema — placeholders for the human."""
    ref = f"MoE Meyda {meta['year']} {meta['season']} {meta['exam_id']} Q{num}"
    return {
        "reviewed": False,
        "concept_id": "",  # TODO map to a concept id from kg-data.json
        "extra_concept_ids": [],
        "subject": "math",
        "level": meta.get("level", "high_school"),
        "math_track": meta.get("math_track", ["5pt"]),
        "points_level": meta.get("points_level", "5pt"),
        "kind": "open",  # TODO refine (numeric/mcq/short_answer/...)
        "difficulty": "medium",  # TODO
        "stem_en": "",  # TODO translate
        "stem_he": body,  # extracted; human fixes LaTeX / OCR artifacts
        "answer_payload": None,  # TODO fill per kind
        "explanation_en": "",
        "explanation_he": "",
        "skill_atoms": [],  # TODO tag atoms
        "verify": None,  # TODO CAS spec for auto-verify (see cas_check.py)
        "official_answer": None,  # TODO from the MoE answer key (verifier ground truth)
        "display_publicly": True,  # public-official; confirm legal sign-off
        "source_ref": ref,
        "transcriber": "assisted",
        "_raw_text": body,  # keep the raw extraction for the reviewer
    }


def cmd_draft(args) -> None:
    inputs = []
    if os.path.isdir(args.input):
        inputs = [
            os.path.join(args.input, f)
            for f in sorted(os.listdir(args.input))
            if f.lower().endswith((".pdf", ".txt"))
        ]
    else:
        inputs = [args.input]
    if not inputs:
        raise SystemExit(f"no .pdf/.txt inputs found at {args.input}")

    os.makedirs(DRAFTS_DIR, exist_ok=True)
    meta = {
        "exam_id": args.exam_id or "unknown",
        "year": args.year or "unknown",
        "season": args.season or "unknown",
        "level": args.level,
        "math_track": [args.points_level],
        "points_level": args.points_level,
    }
    total = 0
    for path in inputs:
        text = extract_text(path)
        chunks = segment_questions(text)
        items = [scaffold(num, body, meta) for num, body in chunks]
        base = args.exam_id or os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(DRAFTS_DIR, f"{base}.draft.json")
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(items, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        total += len(items)
        print(f"[draft] {path}: {len(items)} question(s) -> {out}")
    if total == 0:
        print("  ! no question markers detected — check extraction / segmentation.")
    print(
        f"\nDrafted {total} item(s). Review each in {DRAFTS_DIR}, fix math + mappings, "
        f"set reviewed=true, and save approved files to {APPROVED_DIR}/<exam>.json"
    )


REQUIRED = ["concept_id", "kind", "stem_he", "stem_en", "skill_atoms"]


def _validate_item(idx: int, it: dict) -> list[str]:
    errs = []
    if not it.get("reviewed"):
        errs.append(f"item[{idx}] not reviewed (set reviewed=true after human sign-off)")
    for field in REQUIRED:
        val = it.get(field)
        if val in (None, "", []) or (isinstance(val, list) and not val):
            errs.append(f"item[{idx}] missing {field}")
    if it.get("kind") and it["kind"] not in VALID_KINDS:
        errs.append(f"item[{idx}] invalid kind '{it['kind']}'")
    if it.get("answer_payload") is None:
        errs.append(f"item[{idx}] missing answer_payload")
    # Auto-verifiable requires ground truth: an official key or a CAS verify spec.
    if not it.get("official_answer") and not it.get("verify"):
        errs.append(f"item[{idx}] needs official_answer or a verify spec (else stays unverified)")
    return errs


def cmd_check(args) -> None:
    target = args.dir or APPROVED_DIR
    if not os.path.isdir(target):
        raise SystemExit(f"no approved dir: {target}")
    files = [
        os.path.join(target, f)
        for f in sorted(os.listdir(target))
        if f.endswith(".json") and not f.endswith(".draft.json")
    ]
    if not files:
        print(f"No approved moe_meyda files in {target}. Nothing to check.")
        return
    total_err = 0
    for path in files:
        with open(path, encoding="utf-8") as fh:
            items = json.load(fh)
        items = items if isinstance(items, list) else [items]
        errs = [e for i, it in enumerate(items) for e in _validate_item(i, it)]
        status = "OK" if not errs else f"{len(errs)} issue(s)"
        print(f"[check] {os.path.basename(path)}: {len(items)} item(s) — {status}")
        for e in errs:
            print(f"    - {e}")
        total_err += len(errs)
    print(f"\nTotal issues: {total_err}")
    if args.strict and total_err:
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Assisted MoE Meyda transcription helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("draft", help="extract + scaffold drafts from PDF/TXT")
    d.add_argument("--input", required=True, help="PDF/TXT file or a directory")
    d.add_argument("--exam-id")
    d.add_argument("--year")
    d.add_argument("--season")
    d.add_argument("--level", default="high_school")
    d.add_argument("--points-level", default="5pt")
    d.set_defaults(func=cmd_draft)

    c = sub.add_parser("check", help="validate approved files before ingestion")
    c.add_argument("--dir")
    c.add_argument("--strict", action="store_true")
    c.set_defaults(func=cmd_check)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
