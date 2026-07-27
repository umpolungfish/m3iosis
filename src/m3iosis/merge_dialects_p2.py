#!/usr/bin/env python3
"""Full merge: inject 8-dialect system into k3v-with-ucf.html.
Phase 2: Build the merged HTML using targeted injections.
"""
import re

K3V_PATH = '/home/mrnob0dy666/imsgct/k3v-with-ucf.html'
DIALECT_PATH = '/home/mrnob0dy666/imsgct/mOMonadOS/dialect_3d_torus.html'
OUT_PATH = '/home/mrnob0dy666/imsgct/k3v-with-dialects.html'

with open(K3V_PATH) as f: k3v = f.read()
with open(DIALECT_PATH) as f: dia = f.read()

def extract_js_var(text, varname):
    pat = re.compile(
        r'(?:const|let|var)\s+' + re.escape(varname) + r'\s*=\s*(\[[^;]*?\])\s*;',
        re.DOTALL
    )
    m = pat.search(text)
    if m: return m.group(0)
    pat2 = re.compile(
        r'(?:const|let|var)\s+' + re.escape(varname) + r'\s*=\s*(\{[^;]*?\})\s*;',
        re.DOTALL
    )
    m2 = pat2.search(text)
    if m2: return m2.group(0)
    return None

def extract_function(text, func_name):
    pat = re.compile(
        r'function\s+' + re.escape(func_name) + r'\s*\([^)]*\)\s*\{',
        re.DOTALL
    )
    m = pat.search(text)
    if not m: return None
    start = m.start()
    brace_depth = 0
    i = start
    while i < len(text):
        if text[i] == '{': brace_depth += 1
        elif text[i] == '}':
            brace_depth -= 1
            if brace_depth == 0:
                return text[start:i+1]
        i += 1
    return None

# Extract all needed JS from dialect file
dialects_js = extract_js_var(dia, 'DIALECTS')
knot_map_js = extract_js_var(dia, 'KNOT_MAP')
knot_colors_js = extract_js_var(dia, 'KNOT_COLORS')
knot_colors_hex_js = extract_js_var(dia, 'KNOT_COLORS_HEX')
prim_names_js = extract_js_var(dia, 'PRIM_NAMES')
token_tuples_js = extract_js_var(dia, 'TOKEN_TUPLES')
eval_gates_fn = extract_function(dia, 'evalTokenGates')
token_color_fn = extract_function(dia, 'tokenColor')
horn_knot_fn = extract_function(dia, 'hornKnot')
set_dialect_fn = extract_function(dia, 'setDialect')
glyph_mark_fn = extract_function(dia, 'glyphMark')

# Build the dialect injection block
dialect_injection = f"""
// ─── 8-DIALECT SYSTEM (merged from dialect_3d_torus.html) ───
{dialects_js}

{knot_map_js}

{knot_colors_js}

{knot_colors_hex_js}

{prim_names_js}

{token_tuples_js}

{eval_gates_fn}

{token_color_fn}

{horn_knot_fn}

{set_dialect_fn}

{glyph_mark_fn}

"""

# We inject this right after the TOKEN_META definition
injection_point = "const TOKEN_META ="
injection_idx = k3v.find(injection_point)
if injection_idx < 0:
    print("ERROR: TOKEN_META not found")
    exit(1)

# Find end of TOKEN_META block
end_of_token_meta = k3v.find("const PROGRAMS =", injection_idx)
if end_of_token_meta < 0:
    print("ERROR: PROGRAMS not found after TOKEN_META")
    exit(1)

# Inject dialect data structures right before "const PROGRAMS ="
before = k3v[:end_of_token_meta]
after = k3v[end_of_token_meta:]

# Add currentDialect variable and KNOT_COLORS after the extract
extra_vars = """
let currentDialect = 0;
const KNOT_COLORS = """
# Find KNOT_COLORS in our extracted block
kc_start = knot_colors_js.find('KNOT_COLORS')
kc_line = knot_colors_js[kc_start:] if kc_start >= 0 else "const KNOT_COLORS = [0xffffff, 0x56B4E9, 0xE69F00, 0x009E73, 0xCC79A7, 0xF0E442, 0xD55E00, 0x0072B2];"
extra_vars += kc_line + "\n"
extra_vars += dialect_injection

merged = before + extra_vars + after

# Now we need to modify the scene to render 8 knots instead of 1
# and change station positions to use hornKnot with current dialect

# Save intermediate result for inspection
with open(OUT_PATH, 'w') as f: f.write(merged)
print(f"Phase 1 written: {len(merged)} chars")
print("Now need to: (1) add 8 knot lines to scene, (2) add gate panel UI, (3) add dialect selector")
