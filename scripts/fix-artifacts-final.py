import os, re, json

lesson_dir = "scripts/seed_data/lessons"
files = [f for f in os.listdir(lesson_dir) if f.endswith(".json")]

def repair_json_bytes(raw_bytes):
    text = raw_bytes.decode("utf-8", errors="replace")
    # Remove ###HE=== (with or without spaces) and everything after it on that line
    text = re.sub(r"###\s*HE\s*===.*", "", text)
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
for fname in sorted(files):
    path = os.path.join(lesson_dir, fname)
    with open(path, "rb") as f:
        raw = f.read()
    if b"###" not in raw:
        continue
    if b"HE===" not in raw and b"HE ===" not in raw:
        continue
    fixed_str = repair_json_bytes(raw)
    try:
        parsed = json.loads(fixed_str)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        count = len(re.findall(b"###.*?HE.*?===", raw))
        print(f"Fixed ({count} artifacts): {fname}")
        fixed_count += 1
    except json.JSONDecodeError as e:
        err_pos = getattr(e, "pos", 0)
        print(f"FAILED: {fname} - {e} | near: {repr(fixed_str[max(0,err_pos-20):err_pos+40])}")

print(f"\nTotal files fixed: {fixed_count}")
