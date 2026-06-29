import json
import os
import re

lesson_dir = "scripts/seed_data/lessons"
files = sorted([f for f in os.listdir(lesson_dir) if f.endswith(".json")])

MARKERS = ["###HE===", "### HE ==="]

def repair_json_bytes(raw_bytes):
    """Fix raw newlines inside JSON strings AND remove ###HE=== markers + trailing Hebrew content."""
    text = raw_bytes.decode("utf-8", errors="replace")
    out = []
    in_string = False
    escape_next = False
    i = 0
    while i < len(text):
        c = text[i]
        if escape_next:
            out.append(c)
            escape_next = False
            i += 1
            continue
        if c == "\\":
            out.append(c)
            escape_next = True
            i += 1
            continue
        if c == '"':
            in_string = not in_string
            out.append(c)
            i += 1
            continue
        if in_string:
            # Check for HE markers (correct length comparison)
            found_marker = None
            for mk in MARKERS:
                if text[i:i+len(mk)] == mk:
                    found_marker = mk
                    break
            if found_marker:
                # Skip forward to find the actual closing quote of this string
                j = i + len(found_marker)
                while j < len(text):
                    ch = text[j]
                    if ch == "\\":
                        j += 2  # skip escaped char
                        continue
                    if ch == '"':
                        # This is the closing quote
                        out.append('"')
                        i = j + 1
                        in_string = False
                        break
                    j += 1
                else:
                    out.append('"')
                    i = len(text)
                    in_string = False
                continue
            # Handle raw control characters
            if c == "\n":
                out.append("\\n")
            elif c == "\r":
                pass
            elif c == "\t":
                out.append("\\t")
            elif ord(c) < 0x20:
                pass
            else:
                out.append(c)
        else:
            out.append(c)
        i += 1
    return "".join(out)

fixed_count = 0
for fname in files:
    path = os.path.join(lesson_dir, fname)
    with open(path, "rb") as f:
        raw = f.read()
    has_marker = any(mk.encode() in raw for mk in MARKERS)
    if not has_marker:
        continue
    fixed_str = repair_json_bytes(raw)
    try:
        parsed = json.loads(fixed_str)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        # Verify no markers remain
        with open(path, "rb") as f:
            verify = f.read()
        remaining = sum(mk.encode() in verify for mk in MARKERS)
        status = "OK" if remaining == 0 else f"STILL HAS {remaining} MARKERS"
        print(f"Fixed {fname}: {status}")
        fixed_count += 1
    except json.JSONDecodeError as e:
        err_pos = getattr(e, "pos", 0)
        snippet = fixed_str[max(0,err_pos-30):err_pos+60].replace("\n","\\n")
        print(f"FAILED {fname}: {e.msg} at char {err_pos} | near: {snippet!r}")

print(f"\nTotal files fixed: {fixed_count}")
