#!/usr/bin/env python3
"""Phase 3: Surgical modifications to merge dialect system.
Reads the Phase 1 output and applies targeted injections.
"""
import re

OUT_PATH = '/home/mrnob0dy666/imsgct/k3v-with-dialects.html'

with open(OUT_PATH) as f: html = f.read()

# 1. Add CSS for gate panel and dialect selector
# Find the end of existing CSS (before </style>)
css_injections = """
/* ── Dialect system styles ── */
#gate-panel {
    position: absolute;
    bottom: 240px;
    left: 12px;
    background: rgba(0,0,0,0.95);
    padding: 8px 14px;
    border-radius: 8px;
    border: 2px solid #56B4E9;
    font-size: 11.5px;
    line-height: 1.4;
    z-index: 10;
    max-width: 320px;
    min-width: 200px;
    color: #ddd;
}
#gate-panel h3 {
    font-size: 12px;
    color: #56B4E9;
    margin: 0 0 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
#gate-panel #dialect-name {
    font-size: 14px;
    font-weight: bold;
    color: #e8b84b;
    text-align: center;
}
#gate-panel #knot-info {
    font-size: 11px;
    color: #009E73;
    text-align: center;
    margin-top: 2px;
}
#gate-panel #gate-ordering {
    font-size: 10px;
    color: #999;
    text-align: center;
    margin: 2px 0 4px;
}
#gate-panel .gr {
    display: flex;
    justify-content: space-between;
    margin: 2px 0;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 11px;
}
#gate-panel .gr.pass {
    background: rgba(0,255,136,0.10);
    border-left: 3px solid #39FF14;
}
#gate-panel .gr.fail {
    background: rgba(68,68,68,0.3);
    border-left: 3px solid #555;
}
#gate-panel .gr .gl { color: #ccc; flex: 1; }
#gate-panel .gr .gv { font-weight: bold; text-align: right; }
#gate-panel .sub { opacity: 0.7; font-size: 10px; margin-top: 4px; border-top: 1px solid #333; padding-top: 4px; color: #ccc; }
#dialect-panel {
    position: absolute;
    bottom: 12px;
    left: 12px;
    background: rgba(0,0,0,0.95);
    padding: 6px 14px;
    border-radius: 8px;
    border: 2px solid #e8b84b;
    font-size: 11.5px;
    z-index: 15;
    display: flex;
    align-items: center;
    gap: 6px;
}
#dialect-panel label {
    color: #e8b84b;
    font-weight: bold;
    font-size: 11px;
    white-space: nowrap;
}
#dialect-panel select {
    background: #1a1a1a;
    color: #fff;
    border: 1px solid #e8b84b;
    border-radius: 6px;
    padding: 4px 10px;
    cursor: pointer;
    font-size: 12px;
    font-family: inherit;
    min-width: 140px;
    max-width: 220px;
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

# Inject after existing gate panel styles or before responsive section
# Find a good anchor
anchor_responsive = "@media (max-width: 820px)"
css_idx = html.find(anchor_responsive)
if css_idx < 0:
    print("ERROR: responsive CSS anchor not found")
    # Find </style> instead
    css_idx = html.find('</style>')
    if css_idx < 0: exit(1)

# Inject before the responsive section
html = html[:css_idx] + css_injections + "\n" + html[css_idx:]

# 2. Add gate-panel HTML div after the exec div
# Find exec closing div and insert gate panel before ucf panel
exec_close = '<div id="ucf"'
gate_panel_html = '''
    <!-- ─── GATE PANEL (dialect) ─── -->
    <div id="gate-panel" style="display:none;">
        <div id="dialect-name">canonical (U₀)</div>
        <div id="knot-info">(p,q) = (1,1)</div>
        <div id="gate-ordering">sequential: G1 → G2 → G3</div>
        <div id="gate-content"><div class="gr fail"><span class="gl">G1: —</span><span class="gv">—</span></div></div>
        <div class="sub" id="dialect-desc">Standard gate thresholds</div>
        <div class="sub" id="token-tuple-display" style="margin-top:4px;border-top:1px solid #e8b84b;padding-top:4px;font-family:monospace;font-size:10px;color:#ffe08a;word-break:break-all;">—</div>
    </div>
'''

gate_idx = html.find(exec_close)
if gate_idx < 0:
    print("ERROR: ucf div anchor not found")
    exit(1)
html = html[:gate_idx] + gate_panel_html + html[gate_idx:]

# 3. Add dialect selector panel
# Find the exec closing div (the last </div> of #exec) and insert dialect panel
dialect_selector = '''
    <!-- ─── DIALECT SELECTOR ─── -->
    <div id="dialect-panel">
        <label>DIALECT</label>
        <select id="dialect-sel" aria-label="Dialect selector">
            <option value="0">U₀ canonical (1,1)</option>
            <option value="1">U₁ low_gate (1,2)</option>
            <option value="2">U₂ strict_frobenius (2,3)</option>
            <option value="3">U₃ inverted_gates (3,2)</option>
            <option value="4">U₄ no_ordering (2,5)</option>
            <option value="5">U₅ high_gate (3,5)</option>
            <option value="6">U₆ winding_first (5,2)</option>
            <option value="7">U₇ t_structural (1,3)</option>
        </select>
    </div>
'''

# Find the color-scheme-picker closing </div> and insert after
cp_close = '</div>'  # Need a better anchor
# Insert after #color-scheme-picker
cp_idx = html.find('id="color-scheme-picker"')
if cp_idx < 0:
    print("ERROR: color-scheme-picker not found")
    exit(1)
# Find the last </div> after it
closing_div = html.find('</div>', cp_idx)
# Find another </div> after that (the picker ends a div)
closing_div2 = html.find('</div>', closing_div + 6)
closing_div3 = html.find('</div>', closing_div2 + 6)
# Insert after the picker's container div
insert_point = closing_div3 + 6

html = html[:insert_point] + "\n" + dialect_selector + html[insert_point:]

with open(OUT_PATH, 'w') as f: f.write(html)
print(f"Phase 3 written: {len(html)} chars")
print("Now need to modify JS: add 8 knot lines, station coloring, gate panel updates")
