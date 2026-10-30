#!/usr/bin/env python3
"""Extend k3v-with-dialects.html from 8 to 89 dialects.

Keeps the 8 named reference dialects verbatim at indices 0-7. Generates 81
more by sweeping the same knobs the references vary: which closure primitive
(odot / Omega / Phi) each of the three gates checks, at a threshold tier
(loose / canonical / strict), sequential gating. 3^3 gate-assignments x 3
tiers = 81. Each gets its own coprime (p,q) knot and a wheel colour.

Also: extend KNOT_MAP / KNOT_COLORS / KNOT_COLORS_HEX to 89, build the dialect
<select> from JS, and turn the two hardcoded `< 8` render loops dynamic.
"""
import re, math, colorsys

TARGETS = [
    "/home/mrnob0dy666/imsgct/k3v-with-dialects.html",
    "/home/mrnob0dy666/imsgct/imscribing_grammar/k3v-with-dialects.html",
    "/home/mrnob0dy666/imsgct/ig-docs/k3v-with-dialects.html",
]

SYM = {"odot": "⊙", "Omega": "Ω", "Phi": "Φ"}
GATES = ["odot", "Omega", "Phi"]
TIERS = [("lo", 1), ("cn", 3), ("st", 4)]  # loose / canonical / strict

# ── the 8 reference dialects, verbatim (indices 0-7) ──
BASE_DIALECTS = """{ name: "canonical", desc: "Standard gate thresholds", g1p: "odot", g1m: 3, g2p: "Omega", g2m: 3,
g3p: "Phi", g3m: 3, seq: true },
{ name: "low_gate", desc: "Easy thresholds (all ≥1)", g1p: "odot", g1m: 1, g2p: "Omega", g2m: 1,
g3p: "Phi", g3m: 1, seq: true },
{ name: "strict_frobenius", desc: "Only full Frobenius (all ≥4)", g1p: "odot", g1m: 4, g2p: "Omega",
g2m: 4, g3p: "Phi", g3m: 4, seq: true },
{ name: "inverted_gates", desc: "Gates checked reverse order", g1p: "Omega", g1m: 3, g2p: "Phi",
g2m: 3, g3p: "odot", g3m: 3, seq: true },
{ name: "no_ordering", desc: "All gates independent", g1p: "odot", g1m: 3, g2p: "Omega", g2m: 3,
g3p: "Phi", g3m: 3, seq: false },
{ name: "high_gate", desc: "Very strict (odot≥5,Omega≥5,Phi≥4)", g1p: "odot", g1m: 5, g2p: "Omega",
g2m: 5, g3p: "Phi", g3m: 4, seq: true },
{ name: "winding_first", desc: "Omega is gate 1", g1p: "Omega", g1m: 3, g2p: "odot", g2m: 3,
g3p: "Phi", g3m: 3, seq: true },
{ name: "t_structural", desc: "Th topology is gate 1", g1p: "T", g1m: 4, g2p: "odot", g2m: 3,
g3p: "Omega", g3m: 3, seq: true }"""

BASE_KNOTS = [(1,1),(1,2),(2,3),(3,2),(2,5),(3,5),(5,2),(1,3)]
BASE_COLORS_HEX = ["#ffffff","#56B4E9","#E69F00","#009E73","#CC79A7","#F0E442","#D55E00","#0072B2"]

def coprime_pairs(n, used):
    out, q = [], 2
    while len(out) < n:
        for p in range(1, q):
            if math.gcd(p, q) == 1 and (p, q) not in used and (p, q) not in out:
                out.append((p, q))
                if len(out) >= n: break
        # also the mirror (q,p) for winding variety
        for p in range(1, q):
            if math.gcd(p, q) == 1 and (q, p) not in used and (q, p) not in out:
                out.append((q, p))
                if len(out) >= n: break
        q += 1
    return out[:n]

def gen():
    dialects, knots, colors_hex = [], [], []
    combos = [(a, b, c, t) for a in GATES for b in GATES for c in GATES for t in TIERS]
    assert len(combos) == 81, len(combos)
    kn = coprime_pairs(81, set(BASE_KNOTS))
    for i, (a, b, c, (tname, thr)) in enumerate(combos):
        name = f"{SYM[a]}{SYM[b]}{SYM[c]}·{tname}"
        desc = f"{SYM[a]}≥{thr} {SYM[b]}≥{thr} {SYM[c]}≥{thr}"
        dialects.append(
            f'{{ name: "{name}", desc: "{desc}", g1p: "{a}", g1m: {thr}, g2p: "{b}", g2m: {thr}, '
            f'g3p: "{c}", g3m: {thr}, seq: true }}'
        )
        knots.append(kn[i])
        h = (i * 137.508 % 360) / 360.0  # golden-angle hue spread
        r, g, bl = colorsys.hls_to_rgb(h, 0.6, 0.7)
        colors_hex.append("#%02x%02x%02x" % (int(r*255), int(g*255), int(bl*255)))
    return dialects, knots, colors_hex

def build_arrays():
    gd, gk, gc = gen()
    dialects_js = BASE_DIALECTS + ",\n" + ",\n".join(gd)
    all_knots = BASE_KNOTS + gk
    knot_js = ",\n".join(f"{{ p: {p}, q: {q} }}" for (p, q) in all_knots)
    all_hex = BASE_COLORS_HEX + gc
    colors_hex_js = ", ".join(f'"{h}"' for h in all_hex)
    colors_int_js = ", ".join(f"0x{h[1:]}" for h in all_hex)
    return dialects_js, knot_js, colors_hex_js, colors_int_js

def patch(html):
    dialects_js, knot_js, colors_hex_js, colors_int_js = build_arrays()
    # 1. replace the four array literals
    html = re.sub(r"const DIALECTS = \[.*?\n\s*\];",
                  "const DIALECTS = [\n" + dialects_js + "\n];", html, count=1, flags=re.S)
    html = re.sub(r"const KNOT_MAP = \[.*?\n\s*\];",
                  "const KNOT_MAP = [\n" + knot_js + "\n];", html, count=1, flags=re.S)
    html = re.sub(r"const KNOT_COLORS = \[[^\]]*\];",
                  "const KNOT_COLORS = [" + colors_int_js + "];", html, count=1)
    html = re.sub(r"const KNOT_COLORS_HEX = \[[^\]]*\];",
                  "const KNOT_COLORS_HEX = [" + colors_hex_js + "];", html, count=1)
    # 2. dynamize the knot-line loop and the legend loop
    html = html.replace("for (let d = 0; d < 8; d++) {\n            const kn = KNOT_MAP[d];",
                        "for (let d = 0; d < KNOT_MAP.length; d++) {\n            const kn = KNOT_MAP[d];")
    html = html.replace("for (let i = 0; i < 8; i++) {\n                const kn = KNOT_MAP[i];",
                        "for (let i = 0; i < DIALECTS.length; i++) {\n                const kn = KNOT_MAP[i];")
    # legend: use DIALECTS[i].name instead of the fixed DIALECT_NAMES[8]
    html = html.replace("'<span class=\"kn\">U' + i + ' ' + DIALECT_NAMES[i] + '</span>';",
                        "'<span class=\"kn\">U' + i + ' ' + DIALECTS[i].name + '</span>';")
    # 3. build the dialect <select> from JS (replace hardcoded options with a placeholder + populator)
    html = re.sub(r'(<select id="dialect-sel"[^>]*>).*?(</select>)',
                  r'\1\2', html, count=1, flags=re.S)
    populator = """
        // ─── Build dialect <select> from DIALECTS (89 dialects) ───
        (function populateDialectSelect() {
            const dsel = document.getElementById('dialect-sel');
            if (!dsel) return;
            dsel.innerHTML = '';
            for (let i = 0; i < DIALECTS.length; i++) {
                const kn = KNOT_MAP[i];
                const opt = document.createElement('option');
                opt.value = i;
                opt.textContent = 'U' + i + ' ' + DIALECTS[i].name + ' (' + kn.p + ',' + kn.q + ')';
                dsel.appendChild(opt);
            }
            dsel.value = currentDialect;
        })();
"""
    # inject the populator right before the knot legend populator
    anchor = "        // ─── Populate knot legend ───"
    html = html.replace(anchor, populator + anchor, 1)
    return html

changed = 0
for path in TARGETS:
    with open(path) as f: html = f.read()
    new = patch(html)
    if new != html:
        with open(path, "w") as f: f.write(new)
        changed += 1
        # report counts
        nd = new.count('{ name: "')
        print(f"patched {path}: DIALECTS entries≈{nd}, DIALECTS.length loops set")
print(f"done, {changed} files patched")
