#!/usr/bin/env python3
"""
Batch generate pen-mode diagrams for ALL ob3ects in ob3ect/digital/.

Regenerates pen-mode SVGs using updated symbolic_diagram.py with:
  - Vertical left-side legend (EDGES→GUARD→NODES→PAIRS→REG Δ)
  - Wider SVG (1220×630) for pen-mode to accommodate the legend
  - IFIX barrier with gap for ouroboric back-arc
  - Retrograde wire detection and arc routing
  - Ouroboricity tier labels (O₁/O₂/O_∞)

Usage:
    python3 batch_pen_diagrams.py
"""

import json, sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "IMSCRIBr"))
from tokens import Token
from wiring import imscr_wiring
from symbolic_diagram import render_wiring_svg_v3

OB3ECT_DIR = Path(__file__).resolve().parent / "ob3ect" / "digital"

CANONICAL_ORDER = [
    "VINIT", "TANCH", "AFWD", "AREV", "CLINK", "IMSCRIB",
    "FSPLIT", "FFUSE", "EVALT", "EVALF", "ENGAGR", "IFIX"
]

def get_opcodes_from_json(data: dict) -> list:
    phases = data.get("phases", {})
    p4 = phases.get("phase_4", {})
    steps = p4.get("steps", [])
    if steps and isinstance(steps, list):
        ops = []
        for step in sorted(steps, key=lambda s: s.get("step_num", 0)):
            op = step.get("opcode", "")
            if op: ops.append(op)
        if ops: return ops
    p1 = phases.get("phase_1", {})
    if isinstance(p1, dict):
        return [op for op in CANONICAL_ORDER if op in p1]
    return []

def determine_tier(tokens, graph) -> str:
    has_frob = Token.FSPLIT in tokens and Token.FFUSE in tokens
    self_ref = (tokens[0] == tokens[-1]) if len(tokens) > 0 else False
    has_cross = graph.has_cross_branch() if hasattr(graph, 'has_cross_branch') else False
    if self_ref and has_cross:
        return "O_∞"
    elif has_frob:
        return "O₂"
    else:
        return "O₁"

def main():
    dirs = sorted(d for d in OB3ECT_DIR.iterdir() if d.is_dir())
    ob3ect_dirs = []
    for d in dirs:
        jsons = list(d.glob("*_ob3ect.json"))
        if jsons:
            ob3ect_dirs.append((d, jsons[0]))

    print(f"Found {len(ob3ect_dirs)} ob3ect JSONs")
    results = {"generated": 0, "skipped": 0, "errors": []}

    for obj_dir, json_path in ob3ect_dirs:
        try:
            with open(json_path) as f:
                data = json.load(f)

            ops = get_opcodes_from_json(data)
            if not ops:
                results["skipped"] += 1
                continue

            token_list = []
            valid = True
            for op in ops:
                try:
                    token_list.append(Token[op])
                except KeyError:
                    valid = False
                    break
            if not valid or not token_list:
                results["skipped"] += 1
                continue

            tokens = tuple(token_list)
            graph = imscr_wiring(tokens)
            name = data.get("name", obj_dir.name).replace(" ", "_")[:40]
            graph.name = name

            tier = determine_tier(tokens, graph)

            svg = render_wiring_svg_v3(graph, name, tier, "", "", pen_mode=True)
            out_path = obj_dir / f"{obj_dir.name}_diagram_pen.svg"
            svg.save(out_path)
            results["generated"] += 1

            if results["generated"] % 30 == 0:
                print(f"  Progress: {results['generated']}")

        except Exception as e:
            results["errors"].append(f"  {obj_dir.name}: {e}")

    print(f"\n{'='*60}")
    print(f"Pen-mode diagram regeneration complete")
    print(f"  Generated: {results['generated']}")
    print(f"  Skipped:   {results['skipped']}")
    if results["errors"]:
        print(f"  Errors:    {len(results['errors'])}")
        for err in results["errors"][:10]:
            print(err)
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
