"""
M3Iosis ↔ Hypergematria Bridge.

Imports the IMASM hypergematria engine from lattice_flow.py and exposes
it as a clean module that the M3Iosis CLI can call without reaching into
the grammar internals.

The bridge provides:
  hyper_gematria   — 177-dim rotation-invariant signature (opcode census,
                      ring transitions, landing spectrum, scalars)
  weight_flow      — weight movement through the machine
  banked_count     — was anything counted, then cleared with nothing banked?
  transitions      — opcode transitions on the ring (includes closing edge)
  lattice_cycle    — every rotation with landing register map
  steer_spectrum   — rotation+insertion path to a target register
  parse_word       — glyphs → opcode names
  render           — opcode names → glyphs

Author: Math⊙perator (Lando⊗⊙perator team)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Reach into the grammar for the lattice_flow engine.
_GRAMMAR = Path(__file__).resolve().parent.parent.parent.parent / "imscribing_grammar" / "scripts"
_OB3ECT  = Path(__file__).resolve().parent.parent.parent.parent / "ob3ect" / "digital"
for _p in (_GRAMMAR, _OB3ECT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from lattice_flow import (  # noqa: E402
    parse_word,
    render,
    cycle as _cycle,
    weight as _weight,
    transitions as _transitions,
    banked_count_check,
    hyper_gematria as _hyper_gematria,
    steer_spectrum as _steer_spectrum,
)


# ── public API ──────────────────────────────────────────────────────────────

def parse(word: str) -> tuple:
    """Parse glyphs to opcode names. Returns (steps, unknown)."""
    return parse_word(word)


def render_steps(steps: list) -> str:
    """Render opcode names back to glyphs."""
    return render(steps)


def hyper_gematria(word: str) -> Dict:
    """
    177-coordinate rotation-invariant signature of an IMASM word.

    Coordinates:
      opcode census      — 12   how many of each opcode (order discarded)
      ring transitions   — 144  ordered pairs with closing edge included
      landing spectrum   — 16   distribution of cut landings across registers
      scalars            —  5   length, pairs, max depth, total ordinal, distinct landings

    Every coordinate is verified rotation-invariant: the word is a ring,
    and nothing in the signature reads absolute position.
    """
    steps, unknown = parse_word(word)
    if unknown:
        return {"status": "error",
                "error": f"unknown glyphs: {' '.join(unknown)}"}
    return _hyper_gematria(steps)


def weight_flow(word: str) -> Dict:
    """
    Where the weight moves through an IMASM word.

    Records every movement: DEPOSIT, SEED, CLEAR, FUSE, INERT, OPEN.
    Seed and inert carry no weight but are recorded because both are
    otherwise invisible in a final register.
    """
    steps, unknown = parse_word(word)
    if unknown:
        return {"status": "error",
                "error": f"unknown glyphs: {' '.join(unknown)}"}
    return _weight(steps)


def banked_count(word: str) -> Dict:
    """
    Was anything counted, then cleared with nothing banked behind it?

    AREV empties the register and leaves open frames alone. A result
    fused back to depth zero is exposed to the next reversal.
    """
    steps, unknown = parse_word(word)
    if unknown:
        return {"status": "error",
                "error": f"unknown glyphs: {' '.join(unknown)}"}
    return banked_count_check(steps)


def ring_transitions(word: str) -> Dict:
    """
    Opcode-to-opcode transitions counted ON THE RING.

    A word of length n has n transitions, not n-1. The missing edge is
    the wrap from the last opcode back to the first. Anything read from
    absolute position on a ring measures the cut rather than the word.
    """
    steps, unknown = parse_word(word)
    if unknown:
        return {"status": "error",
                "error": f"unknown glyphs: {' '.join(unknown)}"}
    return _transitions(steps)


def lattice_cycle(word: str) -> Dict:
    """
    Every rotation of the word, with final register, deposits, clears,
    and the map from cut position to landing register.

    The orbit of a ring: what changes under rotation vs what is invariant.
    """
    steps, unknown = parse_word(word)
    if unknown:
        return {"status": "error",
                "error": f"unknown glyphs: {' '.join(unknown)}"}
    return _cycle(steps)


def steer(word: str, target: str = "T", depth: int = 1) -> Dict:
    """
    Find a rotation+insertion path to a target register.

    Insertion costs are measured, not stipulated: each opcode was
    inserted at every third position of 120 randomly generated live
    words, and the change in restored weight and vacate rate recorded.
    """
    steps, unknown = parse_word(word)
    if unknown:
        return {"status": "error",
                "error": f"unknown glyphs: {' '.join(unknown)}"}
    return _steer_spectrum(steps, target=target, depth=depth)


def full_report(word: str) -> str:
    """All six readouts formatted as a single printable report."""
    lines = []
    lines.append("═" * 60)
    lines.append("HYPERGEMATRIA — full analysis")
    lines.append("═" * 60)

    # Word rendering
    steps, unknown = parse_word(word)
    if unknown:
        return f"ERROR: unknown glyphs: {' '.join(unknown)}"
    lines.append(f"  Word:  {render(steps)}")
    lines.append(f"  Steps: {len(steps)}")
    lines.append("")

    # Hypergematria
    hg = _hyper_gematria(steps)
    lines.append("── 177-DIM SIGNATURE (rotation-invariant) ──")
    lines.append(f"  Dimension:      {hg['dimension']}")
    lines.append(f"  Invariant:      {hg['every_coordinate_rotation_invariant']}")
    lines.append(f"  Census:         {', '.join(f'{k}:{v}' for k,v in hg['opcode_census'].items())}")
    lines.append(f"  Scalars:        len={hg['scalars']['length']}, depth={hg['scalars']['max_depth']}, "
                 f"ord={hg['scalars']['total_ordinal']}, lands={hg['scalars']['distinct_landings']}")
    lines.append(f"  Landings:       {', '.join(f'{k}:{v}' for k,v in hg['landing_spectrum'].items())}")
    lines.append("")

    # Weight
    wf = _weight(steps)
    lines.append("── WEIGHT FLOW ──")
    lines.append(f"  Final register: {wf['final_register']}")
    lines.append(f"  Deposits:       {wf['deposits']}")
    lines.append(f"  Cleared:        {wf['cleared']}")
    lines.append(f"  Restored:       {wf['restored']}")
    lines.append(f"  Seeded:         {wf['seeded']}")
    lines.append(f"  Inert:          {wf['inert']}")
    lines.append(f"  Surviving:      {wf['surviving']}")
    lines.append("")

    # Banked count
    bc = banked_count_check(steps)
    lines.append("── BANKED COUNT ──")
    for k, v in bc.items():
        if k != "status":
            lines.append(f"  {k}: {v}")
    lines.append("")

    # Cycle
    cy = _cycle(steps)
    lines.append("── LATTICE CYCLE ──")
    lines.append(f"  Period:         {cy['period']}")
    lines.append(f"  Phase-bearing:  {', '.join(cy['phase_bearing'])}")
    lines.append(f"  Landings:       {cy['landing_by_cut']}")
    lines.append("")

    # Transitions
    tr = _transitions(steps)
    lines.append("── RING TRANSITIONS ──")
    lines.append(f"  Length: {tr['length']}  ring edges: {tr['ring_count']}  linear: {tr['linear_count']}")
    lines.append(f"  Wrap: {tr['wrap']}")
    for edge, count in sorted(tr['ring'].items()):
        lines.append(f"    {edge}: {count}")
    lines.append(f"  Note: {tr.get('note', '')}")
    lines.append("")

    return "\n".join(lines)
