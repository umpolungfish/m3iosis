#!/usr/bin/env python3
"""Complete merge: 8-dialect system into k3v-with-ucf.html.
Performs all modifications in one pass and writes k3v-with-dialects.html.
"""
import re, sys

K3V = '/home/mrnob0dy666/imsgct/k3v-with-ucf.html'
DIA = '/home/mrnob0dy666/imsgct/mOMonadOS/dialect_3d_torus.html'
OUT = '/home/mrnob0dy666/imsgct/k3v-with-dialects.html'

with open(K3V) as f: html = f.read()
with open(DIA) as f: dia = f.read()

# ─── Extract dialect data structures from dialect file ───
def extract_js_var(text, varname):
    pat = re.compile(r'(?:const|let|var)\s+' + re.escape(varname) + r'\s*=\s*(\[[^;]*?\])\s*;', re.DOTALL)
    m = pat.search(text)
    if m: return m.group(0)
    pat2 = re.compile(r'(?:const|let|var)\s+' + re.escape(varname) + r'\s*=\s*(\{[^;]*?\})\s*;', re.DOTALL)
    m2 = pat2.search(text)
    if m2: return m2.group(0)
    return None

def extract_function(text, func_name):
    pat = re.compile(r'function\s+' + re.escape(func_name) + r'\s*\([^)]*\)\s*\{', re.DOTALL)
    m = pat.search(text)
    if not m: return None
    start = m.start()
    depth = 0; i = start
    while i < len(text):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0: return text[start:i+1]
        i += 1
    return None

# Extract all needed JS
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

missing = [(k, v) for k, v in [
    ('DIALECTS', dialects_js), ('KNOT_MAP', knot_map_js), ('KNOT_COLORS', knot_colors_js),
    ('PRIM_NAMES', prim_names_js), ('TOKEN_TUPLES', token_tuples_js),
    ('evalTokenGates', eval_gates_fn), ('tokenColor', token_color_fn),
    ('hornKnot', horn_knot_fn), ('setDialect', set_dialect_fn), ('glyphMark', glyph_mark_fn)
] if not v]
if missing:
    print(f"ERROR: Could not extract: {[m[0] for m in missing]}")
    sys.exit(1)

print("All dialect data structures extracted successfully.")

# ─── 1. Inject dialect CSS ───
css_block = """
/* ── Dialect system styles ── */
#gate-panel {
    position: absolute;
    bottom: 240px; left: 12px;
    background: rgba(0,0,0,0.95);
    padding: 8px 14px; border-radius: 8px;
    border: 2px solid #56B4E9;
    font-size: 11.5px; line-height: 1.4;
    z-index: 10; max-width: 320px; min-width: 200px;
    color: #ddd;
    max-height: calc(100vh - 300px); overflow-y: auto;
}
#gate-panel h3 { font-size: 12px; color: #56B4E9; margin: 0 0 4px; text-transform: uppercase; letter-spacing: 0.5px; }
#gate-panel #dialect-name { font-size: 14px; font-weight: bold; color: #e8b84b; text-align: center; }
#gate-panel #knot-info { font-size: 11px; color: #009E73; text-align: center; margin-top: 2px; }
#gate-panel #gate-ordering { font-size: 10px; color: #999; text-align: center; margin: 2px 0 4px; }
#gate-panel .gr { display: flex; justify-content: space-between; margin: 2px 0; padding: 2px 6px; border-radius: 3px; font-size: 11px; }
#gate-panel .gr.pass { background: rgba(0,255,136,0.10); border-left: 3px solid #39FF14; }
#gate-panel .gr.fail { background: rgba(68,68,68,0.3); border-left: 3px solid #555; }
#gate-panel .gr .gl { color: #ccc; flex: 1; }
#gate-panel .gr .gv { font-weight: bold; text-align: right; }
#gate-panel .sub { opacity: 0.7; font-size: 10px; margin-top: 4px; border-top: 1px solid #333; padding-top: 4px; color: #ccc; }
#gate-panel.collapsed { max-height: 36px; overflow: hidden; padding-bottom: 6px; }
#dialect-panel {
    position: absolute;
    bottom: 12px; left: 12px;
    background: rgba(0,0,0,0.95);
    padding: 6px 14px; border-radius: 8px;
    border: 2px solid #e8b84b;
    font-size: 11.5px; z-index: 15;
    display: flex; align-items: center; gap: 6px;
}
#dialect-panel label { color: #e8b84b; font-weight: bold; font-size: 11px; white-space: nowrap; }
#dialect-panel select {
    background: #1a1a1a; color: #fff;
    border: 1px solid #e8b84b; border-radius: 6px;
    padding: 4px 10px; cursor: pointer;
    font-size: 12px; font-family: inherit;
    min-width: 140px; max-width: 220px;
}
#dialect-panel select:hover { background: #2a2410; }
#knot-legend { margin: 4px 0; font-size: 11px; }
#knot-legend .knot-row {
    display: flex; justify-content: space-between; padding: 2px 6px;
    border-radius: 4px; margin: 2px 0; cursor: pointer;
    font-size: 11px; background: rgba(255,255,255,0.03);
    transition: background 0.15s;
}
#knot-legend .knot-row:hover { background: rgba(255,255,255,0.10); }
#knot-legend .knot-row.active { background: rgba(0,255,136,0.15); border-left: 3px solid #39FF14; }
#knot-legend .knot-row .kp { color: #009E73; font-weight: bold; font-family: monospace; }
#knot-legend .knot-row .kn { color: #ccc; }
@media (max-width: 820px) {
    #gate-panel { bottom: 200px; left: 8px; max-width: 170px; max-height: 120px; font-size: 10px; }
    #dialect-panel { bottom: 6px; left: 6px; padding: 4px 8px; flex-wrap: wrap; }
    #dialect-panel select { min-width: 80px; font-size: 10px; }
}
"""
# Inject CSS before @media (prefers-reduced-motion)
css_anchor = "@media (prefers-reduced-motion: reduce)"
css_idx = html.find(css_anchor)
if css_idx < 0:
    css_idx = html.find('</style>')
html = html[:css_idx] + css_block + html[css_idx:]
print("1. CSS injected")

# ─── 2. Inject dialect HTML panels ───
# Gate panel - insert before UCF panel
gate_html = '''    <!-- ─── GATE PANEL ─── -->
    <div id="gate-panel">
        <div class="drag-handle"></div>
        <h3>GATE</h3>
        <div id="dialect-name">canonical (U₀)</div>
        <div id="knot-info">(p,q) = (1,1)</div>
        <div id="gate-ordering">sequential: G1(⊙≥3) → G2(Ω≥3) → G3(Φ≥3)</div>
        <div id="gate-content"><div class="gr fail"><span class="gl">G1: —</span><span class="gv">—</span></div></div>
        <div class="sub" id="dialect-desc">Standard gate thresholds</div>
        <div class="sub" id="token-tuple-display" style="margin-top:4px;border-top:1px solid #e8b84b;padding-top:4px;font-family:monospace;font-size:10px;color:#ffe08a;word-break:break-all;">—</div>
    </div>
'''
ucf_anchor = '<div id="ucf"'
ucf_idx = html.find(ucf_anchor)
if ucf_idx < 0:
    print("ERROR: ucf anchor not found")
    sys.exit(1)
html = html[:ucf_idx] + gate_html + html[ucf_idx:]
print("2a. Gate panel HTML injected")

# Dialect selector - insert before exec or after color scheme picker
# Find the exec div closing. Insert after color-scheme-picker.
dialect_html = '''    <!-- ─── DIALECT SELECTOR ─── -->
    <div id="dialect-panel">
        <label>DIALECT</label>
        <select id="dialect-sel">
            <option value="0">U₀ canonical ⊙≥3 Ω≥3 Φ≥3 (1,1)</option>
            <option value="1">U₁ low_gate ⊙≥1 Ω≥1 Φ≥1 (1,2)</option>
            <option value="2">U₂ strict_frob ⊙≥4 Ω≥4 Φ≥4 (2,3)</option>
            <option value="3">U₃ inverted Ω≥3 Φ≥3 ⊙≥3 (3,2)</option>
            <option value="4">U₄ no_ord ⊙≥3‖Ω≥3‖Φ≥3 (2,5)</option>
            <option value="5">U₅ high_gate ⊙≥5 Ω≥5 Φ≥4 (3,5)</option>
            <option value="6">U₆ winding Ω≥3 ⊙≥3 Φ≥3 (5,2)</option>
            <option value="7">U₇ t_struct Þ≥4 ⊙≥3 Ω≥3 (1,3)</option>
        </select>
    </div>
'''
# Find a good insertion point - after color-scheme-picker's closing
cp_anchor = 'id="color-scheme-picker"'
cp_idx = html.find(cp_anchor)
if cp_idx < 0:
    print("ERROR: color-scheme-picker not found")
    sys.exit(1)
# Find the outermost div closing after the picker (several </div> tags)
closes = []
pos = cp_idx
while len(closes) < 4:
    pos = html.find('</div>', pos + 1)
    if pos < 0: break
    closes.append(pos)
if len(closes) >= 4:
    insert_at = closes[3] + 6
    html = html[:insert_at] + "\n" + dialect_html + html[insert_at:]
    print("2b. Dialect selector injected")
else:
    print("ERROR: Could not find proper insertion point for dialect selector")
    sys.exit(1)

# ─── 3. Inject dialect JS data structures ───
# Inject after TOKEN_META and GLYPH_TO_TOKEN, before PROGRAMS
prog_anchor = 'const PROGRAMS = {'
prog_idx = html.find(prog_anchor)
if prog_idx < 0:
    print("ERROR: PROGRAMS anchor not found")
    sys.exit(1)

dialect_js_block = f"""
// ─── 8-DIALECT SYSTEM (merged) ───
let currentDialect = 0;

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

html = html[:prog_idx] + dialect_js_block + html[prog_idx:]
print("3. Dialect JS data injected")

# ─── 4. Replace horn() to use dialect's (p,q) knot ───
# Find the exact horn function
pat_horn = re.compile(r'function\s+horn\s*\(\s*t\s*\)\s*\{[^}]*\}')
horn_match = pat_horn.search(html)
if horn_match:
    new_horn = """function horn(t) {
            const kn = KNOT_MAP[currentDialect];
            return hornKnot(t, kn.p, kn.q);
        }"""
    html = html[:horn_match.start()] + new_horn + html[horn_match.end():]
    print("4. horn() replaced with dialect-aware version")
else:
    print("ERROR: horn() regex not matched")
    sys.exit(1)

# ─── 5. Add 8 knot lines after poloidal rings ───
ring_anchor = "// ─── 16 poloidal rings ───"
ring_idx = html.find(ring_anchor)
if ring_idx < 0:
    print("ERROR: poloidal rings anchor not found")
    sys.exit(1)

# Find the next major section after poloidal rings
sphere_anchor = "// ─── Spheres and evaluators ───"
sphere_idx = html.find(sphere_anchor, ring_idx)
if sphere_idx < 0:
    print("ERROR: spheres anchor not found")
    sys.exit(1)

knot_lines_code = """
        // ─── All 8 dialect knot lines ───
        const KNOT_SAMPLES = 600;
        const knotLineGroups = [];
        const KNOT_COLORS_ACTIVE_OPACITY = 0.6;
        const KNOT_COLORS_INACTIVE_OPACITY = 0.12;
        for (let d = 0; d < 8; d++) {
            const kn = KNOT_MAP[d];
            const pts = [];
            for (let k = 0; k <= KNOT_SAMPLES; k++) {
                pts.push(hornKnot(2 * Math.PI * k / KNOT_SAMPLES, kn.p, kn.q));
            }
            const line = new THREE.Line(
                new THREE.BufferGeometry().setFromPoints(pts),
                new THREE.LineBasicMaterial({
                    color: KNOT_COLORS[d],
                    transparent: true,
                    opacity: (d === currentDialect ? KNOT_COLORS_ACTIVE_OPACITY : KNOT_COLORS_INACTIVE_OPACITY),
                })
            );
            mainGroup.add(line);
            knotLineGroups.push(line);
        }
"""
html = html[:sphere_idx] + knot_lines_code + html[sphere_idx:]
print("5. 8 knot lines added")

# ─── 6. Modify station creation to use tokenColor ───
# Find the station mesh creation loop and add gate-based coloring
# Look for where stationMeshes.push happens with a sphere
pat_stpush = re.compile(r'(stationMeshes\.push\([^)]+\))')
stpush_matches = list(pat_stpush.finditer(html))
print(f"6a. Found {len(stpush_matches)} stationMeshes.push occurrences")

# Find the station mesh creation section - search for station sphere creation
st_create_anchor = "const m = new THREE.Mesh("
st_create_idx = html.find(st_create_anchor, sphere_idx + 1000)
if st_create_idx < 0:
    # Try a more specific search
    st_create_idx = html.find('sphere_for_station_material', sphere_idx)
    if st_create_idx < 0:
        # Try to find the station loop by looking for marker = new THREE.Mesh(... SphereGeometry
        st_create_idx = html.find('new THREE.SphereGeometry(0.12', sphere_idx)
        if st_create_idx < 0:
            st_create_idx = html.find('stationMeshes.push', sphere_idx)
            if st_create_idx < 0:
                print("ERROR: station creation not found")
                # Show what's around the area
                region = html[sphere_idx:sphere_idx+3000]
                print(region)
                sys.exit(1)

print(f"6b. Station creation found at {st_create_idx}")
# Show context
start_ctx = max(0, st_create_idx - 100)
end_ctx = min(len(html), st_create_idx + 500)
ctx = html[start_ctx:end_ctx]
# Print first/last 200 chars
print(f"Context: ...{ctx[:200]}...")
print(f"...{ctx[-200:]}...")

# Now find the full station construction block
# It likely looks like:
# for (let i = 0; i < N; i++) { ... const m = new THREE.Mesh(...) ... stationMeshes.push(m) ... }
# We need to add tokenColor coloring to each station sphere
# Find the loop
pat_loop = re.compile(r'for\s*\(\s*let\s+i\s*=\s*0\s*;\s*i\s*<\s*N\s*;\s*i\s*\+\+\s*\)\s*\{')
loop_match = pat_loop.search(html, sphere_idx)
if loop_match:
    print(f"6c. Found station loop at {loop_match.start()}")
    # Inject tokenColor coloring logic inside the loop - find where the mesh color is set
    # and replace/add gate-based coloring
    loop_start = loop_match.start()
    # Find the closing brace by counting
    depth = 0
    i = loop_start
    while i < len(html):
        if html[i] == '{': depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                loop_end = i + 1
                break
        i += 1
    
    loop_body = html[loop_start:loop_end]
    print(f"6d. Loop body length: {len(loop_body)}")
    
    # Add station coloring: set emissive/color based on tokenColor at creation time
    # We need to modify the mesh material to use tokenColor
    # Find "stationMeshes.push" inside the loop
    push_in_loop = loop_body.find('stationMeshes.push')
    if push_in_loop >= 0:
        # Add the coloring code right before the push
        coloring_code = """
            // Color station by gate evaluation for current dialect
            const tc = tokenColor(TOKENS[i].name, currentDialect);
            m.material.color.setHex(tc.color);
            if (tc.emissive) m.material.emissive.setHex(tc.emissive);
            m.material.emissiveIntensity = tc.emissiveIntensity;
            m.userData.glevel = tc.glevel;
"""
        # Find the exact position in the full html
        abs_push = loop_start + push_in_loop
        html = html[:abs_push] + coloring_code + html[abs_push:]
        print("6e. Station coloring injected")
    else:
        print("ERROR: push not found in station loop")
        print(loop_body[:500])
else:
    print("ERROR: station loop not found")
    # Try alternative pattern
    # Show area around st_create_idx
    print(html[max(0, st_create_idx-200):st_create_idx+400])

# ─── 7. Add updateGatePanel() and updateDialect() functions ───
# Inject before the exec object initialization (look for "const exec = {")
exec_anchor = "const exec = {"
exec_idx = html.find(exec_anchor)
if exec_idx < 0:
    print("ERROR: exec anchor not found")
    sys.exit(1)

gate_update_fn = """
// ─── Gate panel UI update ────────────────────────────────────
function updateGatePanel() {
    const d = DIALECTS[currentDialect];
    const kn = KNOT_MAP[currentDialect];
    const dnEl = document.getElementById('dialect-name');
    const kiEl = document.getElementById('knot-info');
    const goEl = document.getElementById('gate-ordering');
    const gcEl = document.getElementById('gate-content');
    const ddEl = document.getElementById('dialect-desc');
    const tdEl = document.getElementById('token-tuple-display');
    if (dnEl) dnEl.textContent = d.name + ' (U' + currentDialect + ')';
    if (kiEl) kiEl.textContent = '(p,q) = (' + kn.p + ',' + kn.q + ')';
    if (goEl) {
        const order = d.seq ? 'sequential' : 'parallel';
        const g1n = d.g1p.charAt(0).toUpperCase() + d.g1p.slice(1);
        const g2n = d.g2p.charAt(0).toUpperCase() + d.g2p.slice(1);
        const g3n = d.g3p.charAt(0).toUpperCase() + d.g3p.slice(1);
        goEl.textContent = order + ': ' + g1n + '(' + d.g1p + '≥' + d.g1m + ')' +
            (d.seq ? ' → ' : ' ‖ ') +
            g2n + '(' + d.g2p + '≥' + d.g2m + ')' +
            (d.seq ? ' → ' : ' ‖ ') +
            g3n + '(' + d.g3p + '≥' + d.g3m + ')';
    }
    if (ddEl) ddEl.textContent = d.desc;
    if (gcEl && TOKENS.length > 0) {
        const tok = TOKENS[exec.ip] || TOKENS[0];
        const g = evalTokenGates(tok.name, currentDialect);
        const p1 = g.g1p.charAt(0).toUpperCase() + g.g1p.slice(1);
        const p2 = g.g2p.charAt(0).toUpperCase() + g.g2p.slice(1);
        const p3 = g.g3p.charAt(0).toUpperCase() + g.g3p.slice(1);
        gcEl.innerHTML =
            '<div class="gr ' + (g.g1 ? 'pass' : 'fail') + '"><span class="gl">' + p1 + ' ' + tok.glyph + ' ≥ ' + g.g1m + ':</span><span class="gv">' + g.v1 + ' ' + (g.g1 ? '✓' : '✗') + '</span></div>' +
            '<div class="gr ' + (g.g2 ? 'pass' : 'fail') + '"><span class="gl">' + p2 + ' ' + tok.glyph + ' ≥ ' + g.g2m + ':</span><span class="gv">' + g.v2 + ' ' + (g.g2 ? '✓' : '✗') + '</span></div>' +
            '<div class="gr ' + (g.g3 ? 'pass' : 'fail') + '"><span class="gl">' + p3 + ' ' + tok.glyph + ' ≥ ' + g.g3m + ':</span><span class="gv">' + g.v3 + ' ' + (g.g3 ? '✓' : '✗') + '</span></div>';
    }
    if (tdEl && TOKENS.length > 0) {
        const tok = TOKENS[exec.ip] || TOKENS[0];
        const tup = TOKEN_TUPLES[tok.name];
        if (tup) {
            tdEl.textContent = '⟨' + tup.join(' ') + '⟩ ' + tok.name;
        } else {
            tdEl.textContent = '—';
        }
    }
}

function setDialect(idx) {
    currentDialect = Math.min(Math.max(0, idx), DIALECTS.length - 1);
    // Update knot line opacities
    if (typeof knotLineGroups !== 'undefined') {
        for (let d = 0; d < Math.min(8, knotLineGroups.length); d++) {
            knotLineGroups[d].material.opacity = (d === currentDialect ? 0.6 : 0.12);
        }
    }
    // Rebuild stations if program loaded
    if (typeof rebuildProgram === 'function') {
        rebuildProgram(currentProgram);
    }
    // Update gate panel
    updateGatePanel();
    // Update legend knot active state
    const rows = document.querySelectorAll('#knot-legend .knot-row');
    rows.forEach((r, i) => r.classList.toggle('active', i === currentDialect));
    // Update dialect selector
    const dsel = document.getElementById('dialect-sel');
    if (dsel) dsel.value = currentDialect;
}
"""

html = html[:exec_idx] + gate_update_fn + html[exec_idx:]
print("7. Gate panel functions injected")

# ─── 8. Modify rebuildProgram to recolor stations and update gate panel ───
# Find the end of rebuildProgram to add coloring
# The rebuildProgram function resets station colors - find its end
pat_rebuild = re.compile(r'function\s+rebuildProgram\s*\([^)]*\)\s*\{')
rebuild_match = pat_rebuild.search(html, exec_idx)
if rebuild_match:
    print(f"8a. rebuildProgram found at {rebuild_match.start()}")
    # Find the function body end
    rstart = rebuild_match.start()
    depth = 0
    i = rstart
    while i < len(html):
        if html[i] == '{': depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                r_end = i
                break
        i += 1
    
    # At the end of rebuildProgram, before the closing }, add station recoloring
    station_recolor = """
            // Recolor stations for current dialect
            for (let si = 0; si < stationMeshes.length; si++) {
                const m = stationMeshes[si];
                if (!m || !m.material) continue;
                const tok = TOKENS[si];
                if (tok) {
                    const tc = tokenColor(tok.name, currentDialect);
                    m.material.color.setHex(tc.color);
                    if (tc.emissive) m.material.emissive.setHex(tc.emissive);
                    m.material.emissiveIntensity = tc.emissiveIntensity;
                    m.userData.glevel = tc.glevel;
                }
                // Also recolor IMSCRIB (gold, always)
                if (si === IMSCRIB_I) {
                    m.material.color.setHex(0xffd700);
                    m.material.emissive.setHex(0x8a6a10);
                    m.material.emissiveIntensity = 0.35;
                }
            }
            updateGatePanel();
"""
    html = html[:r_end] + station_recolor + html[r_end:]
    print("8b. Station recoloring added to rebuildProgram")
else:
    print("8a. rebuildProgram not found - trying to find it...")
    # Search more broadly
    rp_idx = html.find('rebuildProgram', 2000)
    if rp_idx >= 0:
        # Find the function keyword before it
        func_start = html.rfind('function', 0, rp_idx)
        print(f"rebuildProgram-like function found at {func_start}")

# ─── 9. Wire dialect selector ───
# Find the DOMContentLoaded or initialization section to wire the dialect selector
# Look for where other event listeners are set up
init_anchor = 'addEventListener'
# Find where btnStep etc are registered
btn_reset_anchor = 'btnReset'
btn_reset_idx = html.find(btn_reset_anchor)
if btn_reset_idx < 0:
    print("ERROR: btnReset not found")
    sys.exit(1)

# Find the block after the reset handler where other UI wiring happens
# Look for the event listener setup zone between btnStep and keyboard listener
# Find '}));' which closes the btnReset listener
reset_close = html.find('});', btn_reset_idx)
if reset_close < 0:
    reset_close = btn_reset_idx + 500
    print("Warning: using approximate position for reset close")

# After btnReset, look for btnTransit
btn_transit_idx = html.find('btnTransit', reset_close)
if btn_transit_idx < 0:
    print("Warning: btnTransit not found")
    btn_transit_idx = reset_close + 200

# Find the keyboard event listener to inject before it
keyboard_anchor = "addEventListener('keydown'"
keyboard_idx = html.find(keyboard_anchor, btn_transit_idx)
if keyboard_idx < 0:
    print("ERROR: keyboard listener not found")
    sys.exit(1)

dialect_wiring = """
        // ─── Wire dialect selector ───
        const dsel = document.getElementById('dialect-sel');
        if (dsel) {
            dsel.addEventListener('change', function() {
                setDialect(parseInt(this.value));
            });
        }

"""
html = html[:keyboard_idx] + dialect_wiring + html[keyboard_idx:]
print("9. Dialect selector wired")

# ─── 10. Add knot legend rows to the legend panel ───
# Find the legend panel content and add knot rows
legend_anchor = '<div id="legend"'
legend_idx = html.find(legend_anchor)
if legend_idx < 0:
    print("ERROR: legend not found")
    sys.exit(1)

# Find the first <h2> in legend and insert knot rows after the R2 section
# Look for the existing geo-box and insert before it
geo_box_anchor = 'class="geo-box"'
geo_box_idx = html.find(geo_box_anchor, legend_idx)
if geo_box_idx < 0:
    print("ERROR: geo-box not found in legend")
    sys.exit(1)

# Find the closing </div> of the element containing geo-box
geo_div_close = html.find('</div>', geo_box_idx)
geo_div_close2 = html.find('</div>', geo_div_close + 6)
geo_div_close3 = html.find('</div>', geo_div_close2 + 6)

knot_legend_html = """
        <div class="sub" style="margin-top:8px;border-top:2px solid #009E73;padding-top:6px;">
            <strong style="color:#009E73;font-size:12px;">KNOTS · (p,q) per dialect</strong>
            <div id="knot-legend"></div>
        </div>
"""

# Insert before the geo-box
html = html[:geo_box_idx] + knot_legend_html + html[geo_box_idx:]
print("10. Knot legend container added")

# ─── 11. Add JS to populate knot legend ───
# This needs to run at initialization, so find where the initial program is loaded
# Look for rebuildProgram call or similar initialization
init_call_anchor = 'rebuildProgram'
init_call_idx = html.find(init_call_anchor)
if init_call_idx < 0:
    print("ERROR: rebuildProgram call not found")
    sys.exit(1)

# Find the part of init code where the knot legend gets populated
# Inject near the beginning of the initialization
knot_legend_js = """
        // ─── Populate knot legend ───
        const klegend = document.getElementById('knot-legend');
        if (klegend) {
            const DIALECT_NAMES = ['canonical','low_gate','strict_frob','inverted','no_ordering','high_gate','winding_first','t_struct'];
            klegend.innerHTML = DIALECT_NAMES.map((n, i) => {
                const kn = KNOT_MAP[i];
                const c = KNOT_COLORS_HEX[i] || '#ffffff';
                return '<div class="knot-row' + (i === currentDialect ? ' active' : '') +
                    '" onclick="setDialect(' + i + ')" style="border-left:3px solid ' + c + '">' +
                    '<span class="kp">(' + kn.p + ',' + kn.q + ')</span>' +
                    '<span class="kn">U' + i + ' ' + n + '</span></div>';
            }).join('');
        }

"""
# Inject after the first few lines of initialization (after program select is set up)
# Find where the program select is populated
psel_populate = html.find('psel.innerHTML', init_call_idx - 500)
if psel_populate < 0:
    psel_populate = html.find('program-select')
    if psel_populate < 0:
        psel_populate = init_call_idx - 200

# Inject the knot legend JS right after where the program options are set up
html = html[:psel_populate] + knot_legend_js + "\n" + html[psel_populate:]
print("11. Knot legend population JS added")

# ─── 12. Update highlightStations to use gate colors ───
# Find the highlightStations function
pat_highlight = re.compile(r'function\s+highlightStations\s*\(\)\s*\{')
highlight_match = pat_highlight.search(html)
if highlight_match:
    print(f"12a. highlightStations found at {highlight_match.start()}")
    # Replace the body to respect gate colors
    h_start = highlight_match.start()
    h_body_start = html.find('{', h_start)
    # Find the closing brace
    depth = 0
    i = h_body_start
    while i < len(html):
        if html[i] == '{': depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                h_end = i + 1
                break
        i += 1
    
    new_highlight = """function highlightStations() {
            for (let i = 0; i < N; i++) {
                const m = stationMeshes[i];
                if (!m || !m.material) continue;
                const on = (i === exec.ip);
                const tok = TOKENS[i];
                if (i === IMSCRIB_I) {
                    m.material.emissiveIntensity = on ? 1.1 : 0.35;
                    m.scale.setScalar(on ? 1.15 : 1);
                } else if (tok) {
                    const tc = tokenColor(tok.name, currentDialect);
                    if (on) {
                        m.material.emissiveIntensity = Math.min(1.0, tc.emissiveIntensity * 2.5);
                        m.scale.setScalar(1.35);
                    } else {
                        m.material.emissiveIntensity = tc.emissiveIntensity;
                        m.scale.setScalar(1);
                    }
                }
            }
            // Update gate panel each highlight
            updateGatePanel();
        }"""
    html = html[:h_start] + new_highlight + html[h_end:]
    print("12b. highlightStations replaced with gate-aware version")
else:
    print("12a. highlightStations not found")
    # Find it
    hs_idx = html.find('highlightStations')
    if hs_idx >= 0:
        print(f"Found 'highlightStations' at {hs_idx}")
        print(html[hs_idx:hs_idx+200])

# ─── 13. Update fireToken to call updateGatePanel ───
# Find fireToken to add gate panel update
pat_fire = re.compile(r'function\s+fireToken\s*\([^)]*\)\s*\{')
fire_match = pat_fire.search(html)
if fire_match:
    print(f"13a. fireToken found at {fire_match.start()}")
    # Add updateGatePanel() call near the end of fireToken
    f_start = fire_match.start()
    f_body_start = html.find('{', f_start)
    depth = 0
    i = f_body_start
    while i < len(html):
        if html[i] == '{': depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                f_end = i
                break
        i += 1
    
    # Add updateGatePanel call before the closing brace
    html = html[:f_end] + "\n            updateGatePanel();\n        " + html[f_end+1:]
    print("13b. updateGatePanel call added to fireToken")
else:
    print("13a. fireToken not found")

# ─── 14. Show gate panel on initial load ───
# At the end of the init block, add gate panel visibility
html = html.replace(
    'id="gate-panel" style="display:none;"',
    'id="gate-panel"'
)
html = html.replace(
    "id='gate-panel' style='display:none;'",
    "id='gate-panel'"
)
print("14. Gate panel made visible")

# ─── 15. Add initial gate panel update after program load ───
# Find where rebuildProgram is called and add updateGatePanel nearby
init_final = html.find('// ─── Resize & animate', init_call_idx)
if init_final < 0:
    init_final = html.find('function resize()', init_call_idx)
    if init_final < 0:
        init_final = html.find('addEventListener', init_call_idx)

# Add call to updateGatePanel at initialization
init_update = "\n        // Initial gate panel update\n        setTimeout(updateGatePanel, 100);\n"
# Find the last significant JS before animation starts
animate_anchor = 'function animate('
animate_idx = html.find(animate_anchor)
if animate_idx >= 0:
    html = html[:animate_idx] + init_update + html[animate_idx:]
    print("15. Initial gate panel update call added")
else:
    print("15. animate not found, trying alternative anchor")
    resize_anchor = 'function resize()'
    resize_idx = html.find(resize_anchor)
    if resize_idx >= 0:
        html = html[:resize_idx] + init_update + html[resize_idx:]
        print("15. Initial gate panel update call added (before resize)")

# ─── Write output ───
with open(OUT, 'w') as f:
    f.write(html)
print(f"\n=== MERGE COMPLETE ===")
print(f"Output: {OUT}")
print(f"Size: {len(html)} chars")

# ═══════════════════════════════════════════════════════════════
# POST-PROCESS FIXES — Run after Phase 1
# ═══════════════════════════════════════════════════════════════

FIX_PATH = OUT

with open(FIX_PATH) as f: h = f.read()

# Fix 1: Add tokenColor coloring to stationMeshes assignments in rebuildProgram
# Pattern: stationMeshes[i] = m; — two occurrences inside rebuildProgram
# We need to add coloring right after each assignment

# Find rebuildProgram function
rp_start = h.find('function rebuildProgram(key)')
if rp_start < 0:
    rp_start = h.find('function rebuildProgram(')
    
if rp_start >= 0:
    print(f"rebuildProgram found at {rp_start}")
    
    # Find all stationMeshes[i] = m inside rebuildProgram
    search_start = rp_start
    count = 0
    replacements = []
    while True:
        idx = h.find('stationMeshes[i] = m;', search_start)
        if idx < 0:
            idx = h.find('stationMeshes[i]=m;', search_start)
        if idx < 0:
            break
        # Verify we're still inside rebuildProgram (check not past the closing brace)
        rp_end = h.find('}\n', rp_start)
        if rp_end < 0: rp_end = rp_start + 12000
        if idx > rp_end + 1000:
            break
        
        # Add coloring after the assignment
        coloring = """stationMeshes[i] = m;
                // Color by gate evaluation for current dialect
                const tc_ = tokenColor(TOKENS[i].name, currentDialect);
                m.material.color.setHex(tc_.color);
                if (tc_.emissive) m.material.emissive.setHex(tc_.emissive);
                m.material.emissiveIntensity = tc_.emissiveIntensity;
                m.userData.glevel = tc_.glevel;
                if (i === IMSCRIB_I) {
                    m.material.color.setHex(0xffd700);
                    m.material.emissive.setHex(0x8a6a10);
                    m.material.emissiveIntensity = 0.35;
                }"""
        # Replace "stationMeshes[i] = m;" with the full block
        old = h[idx:idx+len("stationMeshes[i] = m;")]
        h = h[:idx] + coloring + h[idx+len("stationMeshes[i] = m;"):]
        search_start = idx + len(coloring)
        count += 1
        print(f"  Fixed stationMeshes[{count}]")
    
    if count == 0:
        print("  No stationMeshes[i] = m found — checking for alternative pattern")
        # Check the actual pattern
        ctx = h[rp_start:rp_start+2000]
        # Print station-related lines
        for line in ctx.split('\n'):
            if 'stationMesh' in line or 'push' in line:
                print(f"  LINE: {line.strip()}")
else:
    print("ERROR: rebuildProgram not found in output")
