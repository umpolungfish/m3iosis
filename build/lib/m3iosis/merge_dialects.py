#!/usr/bin/env python3
"""Merge the 8-dialect system from dialect_3d_torus.html into k3v-with-ucf.html.

Reads both files, injects dialect data structures + gate evaluation into the k3v
JavaScript, and writes the merged output to k3v-with-dialects.html.
"""
import re, os, json

K3V_PATH = '/home/mrnob0dy666/imsgct/k3v-with-ucf.html'
DIALECT_PATH = '/home/mrnob0dy666/imsgct/mOMonadOS/dialect_3d_torus.html'
OUT_PATH = '/home/mrnob0dy666/imsgct/k3v-with-dialects.html'

with open(K3V_PATH) as f: k3v = f.read()
with open(DIALECT_PATH) as f: dia = f.read()

# Extract dialect & knot data from dialect file
def extract_js_var(text, varname):
    """Extract a JS const/let variable definition as a string."""
    pat = re.compile(
        r'(?:const|let|var)\s+' + re.escape(varname) + r'\s*=\s*(\[[^;]*?\])\s*;',
        re.DOTALL
    )
    m = pat.search(text)
    if m: return m.group(0)
    # try object notation
    pat2 = re.compile(
        r'(?:const|let|var)\s+' + re.escape(varname) + r'\s*=\s*(\{[^;]*?\})\s*;',
        re.DOTALL
    )
    m2 = pat2.search(text)
    if m2: return m2.group(0)
    return None

# Extract key data from dialect file
dialects_block = extract_js_var(dia, 'DIALECTS')
knot_map_block = extract_js_var(dia, 'KNOT_MAP')
knot_colors_block = extract_js_var(dia, 'KNOT_COLORS')
knot_colors_hex_block = extract_js_var(dia, 'KNOT_COLORS_HEX')
prim_names_block = extract_js_var(dia, 'PRIM_NAMES')
token_tuples_block = extract_js_var(dia, 'TOKEN_TUPLES')

# Extract functions
def extract_function(text, func_name):
    pat = re.compile(
        r'function\s+' + re.escape(func_name) + r'\s*\([^)]*\)\s*\{',
        re.DOTALL
    )
    m = pat.search(text)
    if not m: return None
    start = m.start()
    # Count braces to find end
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

eval_token_gates_fn = extract_function(dia, 'evalTokenGates')
token_color_fn = extract_function(dia, 'tokenColor')
horn_knot_fn = extract_function(dia, 'hornKnot')
set_dialect_fn = extract_function(dia, 'setDialect')
glyph_mark_fn = extract_function(dia, 'glyphMark')

print("=== Extracted blocks ===")
print(f"DIALECTS: {len(dialects_block or '')} chars")
print(f"KNOT_MAP: {len(knot_map_block or '')} chars")
print(f"KNOT_COLORS: {len(knot_colors_block or '')} chars")
print(f"evalTokenGates: {len(eval_token_gates_fn or '')} chars")
print(f"tokenColor: {len(token_color_fn or '')} chars")
print(f"hornKnot: {len(horn_knot_fn or '')} chars")
print(f"setDialect: {len(set_dialect_fn or '')} chars")
print(f"glyphMark: {len(glyph_mark_fn or '')} chars")
for name, block in [
    ('DIALECTS', dialects_block),
    ('KNOT_MAP', knot_map_block),
    ('KNOT_COLORS', knot_colors_block),
    ('PRIM_NAMES', prim_names_block),
    ('TOKEN_TUPLES', token_tuples_block),
]:
    print(f"{name}: {'FOUND' if block else 'MISSING'}")

