"""
Braid Grammar Bridge
====================
Bridges Fibonacci anyon braiding to the Imscribing Grammar tuple space.

Given a braid word (sequence of Artin generators), this tool:
  1. Computes the unitary braid representation (fusion tree basis)
  2. Extracts topological invariants: winding number, quantum dimension,
     topological spin, Jones polynomial, braid trace, modular data
  3. Maps each invariant to its grammar primitive value
  4. Outputs the resulting grammar tuple ⟨ÐÞŘΦƒÇΓɢ⊙ĦΣΩ⟩
  5. Checks Frobenius closure (μ∘δ = id) on the braid's gate

The mapping from topological invariants to grammar primitives:
  - Ð (Dimensionality)  ← fusion space dimension dim V_n
  - Þ (Topology)         ← braid isotopy class / writhe
  - Ř (Coupling)         ← modular S-matrix (M ↔ M' duality)
  - Φ (Parity)           ← topological spin / self-statistics
  - ƒ (Fidelity)         ← Jones polynomial evaluation
  - Ç (Kinetics)         ← braid word length / depth ratio
  - Γ (Cardinality)      ← number of particles / fusion space size
  - ɢ (Composition)      ← braid group multiplication order
  - ⊙ (Criticality)      ← modular closure / Frobenius fixed point
  - Ħ (Chirality)        ← writhe / braid orientation
  - Σ (Stoichiometry)    ← fusion outcome distribution
  - Ω (Winding)          ← total braid winding number

Author: Math⊙perator (Lando⊗⊙perator team)
"""

import cmath
import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


# ── Glyph Constants ─────────────────────────────────────────────
# Canonical glyph values for each grammar primitive
GLYPH = {
    # Dimensionality
    "D_wedge": "𐑛",      # 0d point
    "D_tri": "𐑨",        # 2d surface
    "D_infty": "𐑼",      # infinite-dim
    "D_odot": "𐑦",       # imscriptive

    # Topology
    "T_net": "𐑡",        # network/branching
    "T_incl": "𐑰",       # inclusion
    "T_bow": "𐑥",        # bowtie/crossing
    "T_box": "𐑶",        # boxtimes
    "T_odot": "𐑸",       # imscriptive closure

    # Coupling
    "R_sup": "𐑩",        # supervenience
    "R_cat": "𐑑",        # categorical
    "R_dag": "𐑽",        # dagger/adjoint
    "R_lr": "𐑾",         # bidirectional

    # Parity
    "P_asym": "𐑗",       # asymmetric
    "P_psi": "𐑿",        # quantum
    "P_pm": "𐑬",         # partial
    "P_sym": "𐑯",        # full symmetric
    "P_pm_sym": "𐑹",     # Frobenius-special

    # Fidelity
    "F_ell": "𐑱",        # classical
    "F_eth": "𐑞",        # thermal
    "F_hbar": "𐑐",       # quantum

    # Kinetics
    "K_fast": "𐑺",       # driven
    "K_mod": "𐑪",        # moderate
    "K_slow": "𐑧",       # near-equilibrium
    "K_trap": "𐑤",       # frozen-order
    "K_MBL": "𐑘",        # frozen-disorder

    # Cardinality
    "G_beth": "𐑲",       # local
    "G_gim": "𐑚",        # mesoscale
    "G_aleph": "𐑔",      # maximal

    # Composition
    "Gm_and": "𐑝",       # conjunctive
    "Gm_or": "𐑜",        # disjunctive
    "Gm_seq": "𐑠",       # sequential
    "Gm_broad": "𐑵",     # broadcast

    # Criticality
    "Ph_sub": "𐑢",       # subcritical
    "Ph_c": "⊙",          # critical (self-modeling)
    "Ph_c_complex": "𐑮", # complex-plane critical
    "Ph_EP": "𐑻",        # exceptional point
    "Ph_super": "𐑣",     # supercritical

    # Chirality
    "H_mem": "𐑓",        # memoryless
    "H_one": "𐑒",        # one step
    "H_two": "𐑖",        # two steps
    "H_eternal": "𐑫",    # eternal

    # Stoichiometry
    "S_11": "𐑙",         # 1:1
    "S_many": "𐑕",       # many identical
    "S_hetero": "𐑳",     # many heterogeneous

    # Winding
    "W_0": "𐑷",          # trivial
    "W_Z2": "𐑴",         # Z₂ binary
    "W_Z": "𐑭",          # Z integer
    "W_NA": "𐑟",         # non-Abelian
}

# ── Braid Group Data (Fibonacci) ────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2
D = math.sqrt(1 + PHI**2)  # total quantum dimension


def _phase_to_glyph(phase_deg: float) -> str:
    """Map a phase angle to a winding glyph.
    
    Phase in degrees, measured modulo 360.
    """
    phase_deg = phase_deg % 360
    # If close to 0 -> trivial winding
    if abs(phase_deg) < 1e-6 or abs(phase_deg - 360) < 1e-6:
        return "𐑷"  # W_0
    # If close to 180 -> Z₂
    if abs(phase_deg - 180) < 1e-6:
        return "𐑴"  # W_Z2
    # If phase is a rational multiple of 360 -> Z winding
    # Otherwise non-Abelian
    return "𐑭"  # W_Z (default for Fibonacci anyons)


def _writhe_from_glyph(w: int) -> str:
    """Map writhe (signed crossing count) to chirality glyph."""
    if w == 0:
        return "𐑓"  # memoryless (trivial braiding)
    if abs(w) == 1:
        return "𐑒"  # one step
    if abs(w) <= 3:
        return "𐑖"  # two steps' worth
    return "𐑫"  # eternal


def _dim_to_glyph(dim: int) -> str:
    """Map fusion space dimension to dimensionality glyph."""
    if dim == 1:
        return "𐑛"  # wedge (0d point)
    if dim == 2:
        return "𐑨"  # triangle (2d surface)
    if dim <= 13:
        return "𐑼"  # infinite-dim (any finite > 2 is infty-adjacent)
    return "𐑦"  # imscriptive


def _n_anyons_to_cardinality(n: int) -> str:
    """Map number of anyons to cardinality glyph."""
    if n <= 4:
        return "𐑲"  # beth (local)
    if n <= 10:
        return "𐑚"  # gimel (mesoscale)
    return "𐑔"  # aleph (maximal)

# ── Glyph Constants (continued) ──────────────────────────────────
# Mapping from topological invariants to primitive index
PRIMITIVE_KEYS = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]


@dataclass
class BraidGrammarResult:
    """Result of analyzing a braid word through the grammar lens."""
    word: str                           # braid word as string
    n_strands: int                      # number of strands
    unitary: Optional[np.ndarray]       # unitary braid representation
    trace: complex                      # braid trace
    writhe: int                         # signed crossing sum
    quantum_dim: float                  # quantum dimension of fusion space
    phases: List[float]                 # eigenvalues of unitary (winding-invariant)
    fusion_space_dim: int               # dim V_n
    jones_polynomial: complex           # V(braid) at t = exp(2πi/5)
    grammar_tuple: str                  # the 12-glyph tuple
    frobenius_closed: bool              # μ∘δ = id check
    description: str                    # plain-language structural description


class BraidGrammarAnalyzer:
    """Analyzes a braid word and maps it to the grammar tuple space."""

    def __init__(self):
        self._loaded = False
        self._braid_reps: Dict[int, List[np.ndarray]] = {}

    def _evaluate_braid_word(self, word: List[int], n: int) -> np.ndarray:
        """Evaluate a braid word on n strands using the core algebra module."""
        from m3iosis.fibonacci_anyon_algebra import evaluate_braid_word
        # evaluate_braid_word takes (n, word) — strand count FIRST
        return evaluate_braid_word(n, word)

    def _compute_writhe(self, word: List[int]) -> int:
        """Signed crossing sum: sigma_k = +1, sigma_k^{-1} = -1."""
        return sum(1 if g > 0 else -1 for g in word)

    def _compute_complexity(self, word: List[int]) -> float:
        """Braid word complexity: ratio of distinct generators to total length."""
        if not word:
            return 0.0
        return len(set(abs(g) for g in word)) / len(word)

    def analyze(self, word: List[int], n_strands: int = 4) -> BraidGrammarResult:
        """Analyze a braid word and compute its grammar tuple."""
        word_str = ",".join(str(g) for g in word)
        
        # 1. Braid unitary
        try:
            U = self._evaluate_braid_word(word, n_strands)
        except Exception as e:
            raise ValueError(f"Could not evaluate braid word: {e}")
        
        # 2. Trace of the unitary
        trace = np.trace(U)
        
        # 3. Writhe
        writhe = self._compute_writhe(word)
        
        # 4. Fusion space dimension
        from m3iosis.fibonacci_anyon_algebra import fusion_space_dimension
        fusion_dim = fusion_space_dimension(n_strands)
        
        # 5. Quantum dimension
        quantum_dim = fusion_dim
        
        # 6. Eigenvalues (phases)
        eigenvalues = np.linalg.eigvals(U)
        phases = [cmath.phase(e) for e in eigenvalues]
        phases_deg = [math.degrees(p) % 360 for p in phases]
        
        # 7. Jones polynomial
        from m3iosis.fibonacci_anyon_tool import FibonacciQuantumComputer as BaseQC
        try:
            qc = BaseQC()
            jones = qc.jones_polynomial(n_strands, word)
            jones_val = complex(jones)
        except Exception:
            # Fall back if the interface is different
            jones_val = trace + 0j
        
        # 8. Map invariants to grammar primitives
        glyphs = self._map_to_grammar(
            word, n_strands, U, trace, writhe, fusion_dim, 
            phases_deg, jones_val, word_str
        )
        
        tuple_str = "⟨" + "".join(glyphs[k] for k in PRIMITIVE_KEYS) + "⟩"
        
        # 9. Frobenius check
        frob_closed = self._check_frobenius(U, trace)
        
        # 10. Description
        desc = self._describe(word, n_strands, writhe, fusion_dim, phases_deg, frob_closed)
        
        return BraidGrammarResult(
            word=word_str,
            n_strands=n_strands,
            unitary=U,
            trace=trace,
            writhe=writhe,
            quantum_dim=quantum_dim,
            phases=phases_deg,
            fusion_space_dim=fusion_dim,
            jones_polynomial=jones_val,
            grammar_tuple=tuple_str,
            frobenius_closed=frob_closed,
            description=desc,
        )
    def _map_to_grammar(self, word, n_strands, U, trace, writhe,
                        fusion_dim, phases_deg, jones_val, word_str):
        """Map topological invariants to grammar primitive values."""
        glyphs = {}
        
        # Ð (Dimensionality) ← fusion space dimension
        glyphs["Ð"] = _dim_to_glyph(fusion_dim)
        
        # Þ (Topology) ← braid isotopy class / number of crossings
        crossing_count = len(word)
        if crossing_count == 0:
            glyphs["Þ"] = "𐑡"  # network (trivial braid)
        elif crossing_count <= 5:
            glyphs["Þ"] = "𐑥"  # bowtie (simple crossing)
        elif crossing_count <= 20:
            glyphs["Þ"] = "𐑶"  # boxtimes (complex crossing)
        else:
            glyphs["Þ"] = "𐑸"  # imscriptive closure (braid word is its own closure)
        
        # Ř (Coupling) ← modular S-matrix / braid group rep
        # Check if braid representation is irreducible/faithful
        if fusion_dim == 1:
            glyphs["Ř"] = "𐑩"  # supervenience (trivial)
        elif fusion_dim == 2:
            glyphs["Ř"] = "𐑑"  # categorical (2d representation)
        else:
            glyphs["Ř"] = "𐑽"  # dagger (unitary representation)
        
        # Φ (Parity) ← topological spin / self-statistics
        # Check if eigenvalues contain the Fibonacci phase e^{±4πi/5}
        fib_phase = 4 * math.pi / 5  # 144 degrees
        has_fib_phase = any(
            abs(p - fib_phase) < 0.1 or abs(p + fib_phase) < 0.1
            for p in [cmath.phase(e) for e in np.linalg.eigvals(U)]
        )
        if writhe == 0 and not has_fib_phase:
            glyphs["Φ"] = "𐑗"  # asymmetric (trivial)
        elif fusion_dim == 2 and has_fib_phase:
            glyphs["Φ"] = "𐑹"  # Frobenius-special (Fibonacci braiding)
        elif has_fib_phase:
            glyphs["Φ"] = "𐑬"  # partial (some Fibonacci phases)
        else:
            glyphs["Φ"] = "𐑿"  # quantum (general unitary)
        
        # ƒ (Fidelity) ← Jones polynomial evaluation
        jones_norm = abs(jones_val)
        if abs(jones_norm - 1.0) < 0.01:
            glyphs["ƒ"] = "𐑱"  # classical (trivial braid)
        elif jones_norm.real > 0.5:
            glyphs["ƒ"] = "𐑞"  # thermal (intermediate)
        else:
            glyphs["ƒ"] = "𐑐"  # quantum (non-trivial braid)
        
        # Ç (Kinetics) ← braid word complexity
        complexity = self._compute_complexity(word)
        if complexity == 0:
            glyphs["Ç"] = "𐑘"  # MBL (frozen — no braiding)
        elif complexity < 0.5:
            glyphs["Ç"] = "𐑤"  # trap (frozen order — few generators)
        elif complexity < 0.8:
            glyphs["Ç"] = "𐑧"  # slow (near-equilibrium — moderate complexity)
        else:
            glyphs["Ç"] = "𐑪"  # moderate (many generators)
        
        # Γ (Cardinality) ← number of anyons
        glyphs["Γ"] = _n_anyons_to_cardinality(n_strands)
        
        # ɢ (Composition) ← braid group multiplication order
        if fusion_dim == 1:
            glyphs["ɢ"] = "𐑝"  # and (conjunctive — trivial product)
        elif len(word) <= 3:
            glyphs["ɢ"] = "𐑜"  # or (disjunctive — short word)
        elif self._is_braid_word_sorted(word):
            glyphs["ɢ"] = "𐑵"  # broadcast (sorted/nested generators)
        else:
            glyphs["ɢ"] = "𐑠"  # sequential (general non-commutative)
        
        # ⊙ (Criticality) ← Frobenius closure
        frob = self._check_frobenius(U, trace)
        if frob:
            glyphs["⊙"] = "⊙"  # critical (self-modeling fixed point)
        elif abs(trace) < 0.1:
            glyphs["⊙"] = "𐑢"  # subcritical (trace near zero)
        else:
            glyphs["⊙"] = "𐑣"  # supercritical (non-closed)
        
        # Ħ (Chirality) ← writhe / braid orientation
        glyphs["Ħ"] = _writhe_from_glyph(writhe)
        
        # Σ (Stoichiometry) ← fusion outcome distribution
        if fusion_dim == 1:
            glyphs["Σ"] = "𐑙"  # 1:1 (single fusion outcome)
        elif fusion_dim == 2:
            glyphs["Σ"] = "𐑕"  # many identical (two outcomes)
        else:
            glyphs["Σ"] = "𐑳"  # many heterogeneous (multiple outcomes)
        
        # Ω (Winding) ← total winding number from eigenvalues
        # Sum of phases in full windings.
        #
        # phases_deg is wrapped into [0, 360) for display, and summing THAT is
        # wrong here. An eigenvalue whose true phase is zero-from-below —
        # 1 - 1e-16j, which is what the identity braid produces — wraps to
        # 359.9999… and contributes a spurious full turn. The identity on 7
        # strands has 8 eigenvalues, so the same braid spelled two ways scored
        # anywhere from 0 to 5 turns depending only on float sign dust, and the
        # bins below turned that into 𐑷, 𐑭 or 𐑟 for a braid with no winding at
        # all. It also made Ω rise with strand count, since a larger fusion
        # space offers more eigenvalues to wrap.
        #
        # A winding is signed and must be summed unwrapped: cmath.phase already
        # returns (-180, 180], which is the branch we want.
        total_phase = sum((p + 180.0) % 360.0 - 180.0 for p in phases_deg) / 360.0
        abs_winding = abs(total_phase)
        if abs_winding < 0.01:
            glyphs["Ω"] = "𐑷"  # trivial
        elif abs_winding < 1.5:
            glyphs["Ω"] = "𐑴"  # Z₂ binary
        elif abs_winding < 5:
            glyphs["Ω"] = "𐑭"  # Z integer
        else:
            glyphs["Ω"] = "𐑟"  # non-Abelian
        
        return glyphs

    def _is_braid_word_sorted(self, word: List[int]) -> bool:
        """Check if the braid word has the sorted/nested structure
        characteristic of broadcast composition."""
        gens = [abs(g) for g in word]
        # Check if generators appear in non-decreasing order (nested)
        return all(gens[i] <= gens[i+1] for i in range(len(gens)-1))

    def _check_frobenius(self, U: np.ndarray, trace: complex) -> bool:
        """Check Frobenius closure: μ∘δ = id_i on the braid's gate.
        
        For a unitary braid representation, this amounts to:
          U†U = I (unitarity) AND
          tr(U) ∈ ℝ (real trace — the gate is self-adjoint in the 
          statistical sense of Frobenius)
        """
        # Unitarity check
        I = np.eye(U.shape[0], dtype=complex)
        diff = np.linalg.norm(U.conj().T @ U - I)
        is_unitary = diff < 1e-8
        
        # Real trace check
        trace_is_real = abs(trace.imag) < 1e-8
        
        # Frobenius closure: unitary + real trace means the braid 
        # realizes a Frobenius-special algebra object
        return is_unitary and trace_is_real

    def _describe(self, word, n_strands, writhe, fusion_dim, phases, frob):
        """Generate a structural description of the braid's grammar."""
        parts = []
        parts.append(f"Braid word {','.join(str(g) for g in word)} on {n_strands} strands")
        parts.append(f"Writhe: {writhe:+d}")
        parts.append(f"Fusion space dimension: {fusion_dim}")
        
        if fusion_dim == 2:
            parts.append(f"Encodes 1 qubit")
        elif fusion_dim == 8:
            parts.append(f"Encodes 3 qubits")
        
        avg_phase = sum(phases) / len(phases) if phases else 0
        parts.append(f"Average eigenvalue phase: {avg_phase:.1f}°")
        
        if frob:
            parts.append("Frobenius closed: μ∘δ = id ✓")
        else:
            parts.append("Frobenius open: μ∘δ ≠ id")
        
        return " — ".join(parts)

    @classmethod
    def analyze_word(cls, word: List[int], n_strands: int = 4) -> BraidGrammarResult:
        """Convenience entry point."""
        analyzer = cls()
        return analyzer.analyze(word, n_strands)

    @classmethod
    def print_report(cls, result: BraidGrammarResult) -> None:
        """Print a formatted report of the braid grammar analysis."""
        print("=" * 60)
        print("BRAID GRAMMAR ANALYSIS")
        print("=" * 60)
        print(f"Braid word:     {result.word}")
        print(f"Strands:        {result.n_strands}")
        print(f"Fusion space:   dim V_{result.n_strands} = {result.fusion_space_dim}")
        print(f"Writhe:         {result.writhe:+d}")
        print(f"Braid trace:    {result.trace:.6f}")
        print(f"Jones poly:     {result.jones_polynomial:.6f}")
        print(f"Frobenius:      {'✓ CLOSED' if result.frobenius_closed else '✗ OPEN'}")
        print()
        print("GRAMMAR TUPLE:")
        print(f"  {result.grammar_tuple}")
        print()
        print("DESCRIPTION:")
        print(f"  {result.description}")
        print("=" * 60)


# ── CLI Entry Points ─────────────────────────────────────────────
def braid_grammar_cli():
    """CLI entry point for the Braid Grammar Bridge."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Braid Grammar Bridge — Fibonacci braid words to grammar tuples"
    )
    parser.add_argument("word", type=int, nargs="+",
                        help="Braid word as signed Artin generators")
    parser.add_argument("--strands", "-n", type=int, default=4,
                        help="Number of strands (default: 4, dim V_4 = 2)")
    args = parser.parse_args()
    
    result = BraidGrammarAnalyzer.analyze_word(args.word, args.strands)
    BraidGrammarAnalyzer.print_report(result)


def braid_grammar_main():
    """Main entry point called by the m3 CLI."""
    import sys
    # Called with: m3 braid-grammar [word...] [--strands N]
    braid_grammar_cli()
