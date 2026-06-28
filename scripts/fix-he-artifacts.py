import os, re, json

lesson_dir = "scripts/seed_data/lessons"
artifact_files = [
    "arithmetic.json","complex_numbers.json","derivatives_rules.json",
    "electric_potential.json","equations_linear.json","exponents.json",
    "functions_linear.json","functions_quadratic.json","integrals_intro.json",
    "limits.json","trigonometry_ratios.json"
]

def fix_file(fname):
    path = os.path.join(lesson_dir, fname)
    with open(path, "rb") as f:
        raw = f.read()
    content = raw.decode("utf-8", errors="replace")
    # Remove ###HE=== and everything after it on that line
    content = re.sub(r"###HE===.*", "", content)
    # Try direct parse
    try:
        parsed = json.loads(content)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        print(f"Fixed: {fname}")
        return True
    except json.JSONDecodeError:
        pass
    # Hard mode: escape raw control chars inside JSON strings
    fixed = []
    in_string = False
    escape_next = False
    for i, c in enumerate(content):
        if escape_next:
            fixed.append(c)
            escape_next = False
        elif c == "\\":
            fixed.append(c)
            escape_next = True
        elif c == '"' and not escape_next:
            in_string = not in_string
            fixed.append(c)
        elif in_string and c == "\n":
            fixed.append("\\n")
        elif in_string and c == "\r":
            pass
        elif in_string and c == "\t":
            fixed.append("\\t")
        elif in_string and ord(c) < 0x20:
            pass
        else:
            fixed.append(c)
    fixed_str = "".join(fixed)
    try:
        parsed = json.loads(fixed_str)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        print(f"Fixed (hard): {fname}")
        return True
    except Exception as e2:
        print(f"FAILED: {fname} - {e2}")
        return False

for fname in artifact_files:
    fix_file(fname)
