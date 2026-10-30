#!/usr/bin/env python3
"""Phase 4: Critical JS modifications for dialect merge.
Adds: 8 knot lines, station coloring, gate panel updates, dialect switching.
"""
import re

OUT_PATH = '/home/mrnob0dy666/imsgct/k3v-with-dialects.html'
with open(OUT_PATH) as f: html = f.read()

# 1. FIND KEY JS ANCHORS
# The scene setup has a section creating the torus. After the torus mesh and poloidal rings,
# we need to add 8 knot lines. Find the section with poloidal rings.

# Find "// ─── 16 poloidal rings ───"
ring_anchor = "// ─── 16 poloidal rings ───"
ring_idx = html.find(ring_anchor)
if ring_idx < 0:
    print("ERROR: poloidal rings anchor not found")
    exit(1)

# After the poloidal rings loop, add the 8 knot lines
# Find the end of the rings loop (the next comment or section marker)
sphere_anchor = "// ─── Spheres and evaluators ───"
sphere_idx = html.find(sphere_anchor, ring_idx)
if sphere_idx < 0:
    print("ERROR: spheres anchor not found")
    exit(1)

# Insert 8 knot lines code between poloidal rings and spheres
knot_lines_code = """
        // ─── All 8 dialect knot lines ───
        const KNOT_SAMPLES = 600;
        const knotLineGroups = [];
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
                    opacity: (d === 0 ? 0.6 : 0.12),
                })
            );
            mainGroup.add(line);
            knotLineGroups.push(line);
        }
"""
html = html[:sphere_idx] + knot_lines_code + html[sphere_idx:]

# 2. Modify the horn() function to use the active dialect's (p,q) knot
# Find the horn() function definition
horn_fn_anchor = "function horn(t)"
horn_idx = html.find(horn_fn_anchor)
if horn_idx < 0:
    print("ERROR: horn function not found")
    exit(1)

# Find the end of the horn function (the next closing brace)
horn_fn_end = html.find('}', horn_idx)
horn_fn_end = html.find('}', horn_fn_end + 1)
# Replace the horn function body to use hornKnot with current dialect
horn_fn_start = html.find('{', horn_idx)
horn_replacement = """function horn(t) {
            const kn = KNOT_MAP[currentDialect];
            return hornKnot(t, kn.p, kn.q);
        }"""
html = html[:horn_fn_start+1] + "\n            const kn = KNOT_MAP[currentDialect];\n            return hornKnot(t, kn.p, kn.q);\n        " + html[horn_fn_end:]

# Wait, let me find the actual horn() function more carefully
# Reset and find the actual function
html_backup = html  # save

# Actually let me re-read the file and find horn() more carefully
with open(OUT_PATH) as f: content = f.read()

# Find the exact horn() function
pat_horn = re.compile(r'function\s+horn\s*\(\s*t\s*\)\s*\{[^}]*\}')
horn_match = pat_horn.search(content)
if horn_match:
    horn_full = horn_match.group(0)
    new_horn = """function horn(t) {
            const kn = KNOT_MAP[currentDialect];
            return hornKnot(t, kn.p, kn.q);
        }"""
    content = content[:horn_match.start()] + new_horn + content[horn_match.end():]
    print("horn() replaced")
else:
    print("ERROR: horn() regex not matched")
    # Try different approaches
    idx_fn = content.find('function horn(t)')
    if idx_fn >= 0:
        print(f"Found 'function horn(t)' at {idx_fn}")
        # Show surrounding context
        print(content[idx_fn:idx_fn+200])
    exit(1)

# 3. Add station coloring based on gate evaluation
# Find the station mesh creation code - look for station(ang(i))
pat_station = re.compile(r'let\s+stationMeshes\s*=')
st_idx = pat_station.search(content)
if st_idx:
    print("Found stationMeshes")
else:
    # Find the station() function
    pat_stfn = re.compile(r'function\s+station\s*\(\s*i\s*\)')
    stfn = pat_stfn.search(content)
    if stfn:
        print(f"Found station() at {stfn.start()}")
    else:
        print("ERROR: station() not found")
        exit(1)

# 4. Find the station creation loop and add tokenColor coloring
# Look for where station spheres are created with push
pat_stpush = re.compile(r'stationMeshes\.push')
stpush_matches = list(pat_stpush.finditer(content))
print(f"Found {len(stpush_matches)} stationMeshes.push calls")

# Find the rebuildStations function or the main station creation
pat_rebuild = re.compile(r'rebuildStations|function\s+createStations')
rebuild_match = pat_rebuild.search(content)
if rebuild_match:
    print(f"Found station builder at {rebuild_match.start()}")
else:
    print("Looking for station creation block...")
    # Show context around station mesh creation
    for m in stpush_matches[:2]:
        start = max(0, m.start() - 100)
        end = min(len(content), m.end() + 200)
        print(content[start:end])
        print("---")
