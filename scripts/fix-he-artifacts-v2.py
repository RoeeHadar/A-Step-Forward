import os, re, json

lesson_dir = "scripts/seed_data/lessons"
artifact_files = [
    "arithmetic.json","complex_numbers.json","derivatives_rules.json",
    "electric_potential.json","equations_linear.json","exponents.json",
    "functions_linear.json","functions_quadratic.json","integrals_intro.json",
    "limits.json","trigonometry_ratios.json"
]

def repair_json_bytes(raw_bytes):
    """
    Fix raw (unescaped) newlines/tabs inside JSON strings, 
    and remove ###HE=== markers with the Hebrew content that follows them 
    (keeping only the English content before the marker).
    """
    text = raw_bytes.decode("utf-8", errors="replace")
    
    # Strategy: character-by-character state machine
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
            # Check for ###HE=== marker - truncate the string here
            if text[i:i+9] == "###HE===":
                # Skip everything until the closing quote of this string
                # But we need to find the end of this string properly
                j = i + 9
                depth = 0
                while j < len(text):
                    if text[j] == "\\" :
                        j += 2  # skip escaped char
                        continue
                    if text[j] == '"':
                        # This is the closing quote
                        out.append('"')  # close the string
                        i = j + 1
                        in_string = False
                        break
                    j += 1
                else:
                    # Didn't find closing quote - just close string
                    out.append('"')
                    i = len(text)
                    in_string = False
                continue
            
            # Handle raw control characters
            if c == "\n":
                out.append("\\n")
            elif c == "\r":
                pass  # skip
            elif c == "\t":
                out.append("\\t")
            elif ord(c) < 0x20:
                pass  # skip other control chars
            else:
                out.append(c)
        else:
            out.append(c)
        
        i += 1
    
    return "".join(out)

for fname in artifact_files:
    path = os.path.join(lesson_dir, fname)
    with open(path, "rb") as f:
        raw = f.read()
    
    # Check if needs fixing
    if b"###HE===" not in raw:
        print(f"Skip (no marker): {fname}")
        continue
    
    fixed_str = repair_json_bytes(raw)
    
    try:
        parsed = json.loads(fixed_str)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        print(f"Fixed: {fname}")
    except json.JSONDecodeError as e:
        # Show a snippet around the error
        err_pos = e.pos if hasattr(e, "pos") else 0
        print(f"FAILED: {fname} - {e} | snippet: {repr(fixed_str[max(0,err_pos-30):err_pos+50])}")
