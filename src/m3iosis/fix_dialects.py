#!/usr/bin/env python3
"""Fix conflicts and add station coloring in the merged file."""
import re

OUT = '/home/mrnob0dy666/imsgct/k3v-with-dialects.html'

with open(OUT) as f: h = f.read()

# 1. Remove the WRONG setDialect function (the one from dialect_3d_torus.html extraction)
# It calls rebuildProgram(currentProgram) which doesn't match k3v's rebuildProgram(key)
# And it has updateGatePanel which was injected separately
# Find: "function setDialect(idx) {" near line 1222
pat_set1 = re.compile(r'function\s+setDialect\s*\(\s*idx\s*\)\s*\{[^}]*?\}', re.DOTALL)
set1_matches = list(pat_set1.finditer(h))
print(f"Found {len(set1_matches)} setDialect functions")

# Identify which one is the dialect file extraction (wrong one)
# The wrong one will be the FIRST one (around line 1222)
# The correct one is the SECOND one (around line 2924), which is more comprehensive
# Let me check by looking at context
if len(set1_matches) >= 2:
    first = set1_matches[0]
    second = set1_matches[1]
    
    # Check which one has the wrong content
    ctx1 = h[first.start():first.end()]
    ctx2 = h[second.start():second.end()]
    
    print(f"setDialect #1 ({len(ctx1)} chars at {first.start()}): calls rebuildProgram: {'rebuildProgram' in ctx1}")
    print(f"setDialect #2 ({len(ctx2)} chars at {second.start()}): calls rebuildProgram: {'rebuildProgram' in ctx2}")
    
    if 'rebuildProgram' in ctx1:
        # First one is the extracted one from dialect file - remove it
        h = h[:first.start()] + h[first.end():]
        print("Removed extracted setDialect (wrong one)")

# 2. Remove duplicate setDialect at line 1222 (simpler extracted one)
# The one at 2924 is more comprehensive
idx1 = h.find('function setDialect(idx) {')
# Find the second occurrence
idx2 = h.find('function setDialect(idx) {', idx1 + 10)
print(f"setDialect #1 at {idx1}, setDialect #2 at {idx2}")

# Find the end of the first setDialect (find the next function keyword or significant marker)
# It ends at "rebuildProgram(currentProgram);\n        }\n\nfunction glyphMark"
end1 = h.find('\nfunction glyphMark', idx1)
if end1 < 0:
    end1 = h.find('function glyphMark', idx1)
    
if end1 > 0:
    # Remove the first setDialect (and its closing whitespace)
    h = h[:idx1] + h[end1:]
    print(f"Removed first setDialect at {idx1}")
else:
    print("ERROR: could not find end of first setDialect")

# 3. Add tokenColor station coloring in rebuildProgram
# Find the station creation section inside rebuildProgram
rp_start = h.find('function rebuildProgram(key)')
print(f"rebuildProgram at {rp_start}")

# Find the IMSCRIB station creation block
imsc_block = h.find('tok.name === "IMSCRIB"', rp_start)
if imsc_block > 0:
    # After the IMSCRIB station, before "const imG = glyphMark", add coloring
    imsc_coloring = """
                // Color by gate evaluation for current dialect
                const tc = tokenColor(tok.name, currentDialect);
                m.material.color.setHex(tc.color);
                if (tc.emissive) m.material.emissive.setHex(tc.emissive);
                m.material.emissiveIntensity = tc.emissiveIntensity;
                m.userData.glevel = tc.glevel;
                // IMSCRIB is always gold
                m.material.color.setHex(0xffd700);
                m.material.emissive.setHex(0x8a6a10);
                m.material.emissiveIntensity = 0.35;
"""
    # Find where to insert - right after m.position.copy(p); programGroup.add(m); stationMeshes[i] = m;
    # Look for "programGroup.add(m);" followed by "stationMeshes[i] = m;" 
    anchor = 'stationMeshes[i] = m;'
    st_idx = h.find(anchor, imsc_block)
    if st_idx > 0:
        st_end = st_idx + len(anchor)
        # Insert coloring after the station assignment
        h = h[:st_end] + imsc_coloring + h[st_end:]
        print(f"IMSCRIB station coloring added")
    else:
        print(f"No stationMeshes[i] = m found near IMSCRIB block")
else:
    print("IMSCRIB block not found")

# 4. Add tokenColor coloring for non-IMSCRIB stations
# Find the else block (non-IMSCRIB) and add coloring there too
else_block = h.find('} else {', imsc_block)
if else_block > 0:
    else_coloring = """
                // Color by gate evaluation for current dialect
                const tc = tokenColor(tok.name, currentDialect);
                m.material.color.setHex(tc.color);
                if (tc.emissive) m.material.emissive.setHex(tc.emissive);
                m.material.emissiveIntensity = tc.emissiveIntensity;
                m.userData.glevel = tc.glevel;
"""
    # Find stationMeshes[i] = m in the else block
    st_idx2 = h.find('stationMeshes[i] = m;', else_block)
    if st_idx2 > 0:
        st_end2 = st_idx2 + len('stationMeshes[i] = m;')
        h = h[:st_end2] + else_coloring + h[st_end2:]
        print(f"Non-IMSCRIB station coloring added")
    else:
        print(f"No stationMeshes[i] = m found in else block")
        # Look for it
        ctx = h[else_block:else_block+300]
        for line in ctx.split('\n'):
            if 'stationMesh' in line or 'push' in line or 'm.position' in line:
                print(f"  LINE: {line.strip()}")
else:
    print("else block not found")

# 5. Write output
with open(OUT, 'w') as f:
    f.write(h)

print(f"\n=== FIXES COMPLETE ===")
print(f"Output size: {len(h)} chars")
