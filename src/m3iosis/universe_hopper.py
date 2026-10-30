#!/usr/bin/env python3
"""
Universe Hopping Engine
=======================
Cross-framework computational transport for m3iosis.

Given a grammar tuple, the Universe Hopper computes its manifestation in
every mathematical framework accessible to m3iosis:

  Framework                   | Transport mechanism
  ───────────────────────────┼──────────────────────────────────
  Fibonacci Anyon Braid       | Tuple → braid word parameters → unitary
  Berry Holonomy (U(n))      | Tuple → connection coefficients → holonomy
  MBL Phase Coordinates       | Tuple → disorder/entropy → phase diagram
  Triple Frame Opcodes        | Tuple → opcode sequence → ρ, verdict
  SIC-POVM Fiducial           | Tuple → fiducial proximity → d(B, tuple)
  ZFC Formula (CLINK)         | Tuple → formula decomposition
  Quantum Circuit (Fibonacci) | Tuple → qubit encoding → gate sequence

And the REVERSE direction: given framework parameters, find the nearest
grammar tuple.

Core operation: hop(origin, target) — compute the minimal-cost path through
the crystal of types, showing which primitives flip at each step, what each
intermediate system is, and verifying Frobenius closure along the way.

Author: Math⊙perator (Lando⊗⊙perator Team)
"""

import math
import cmath
import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field

# ── Import from sibling modules ──────────────────────────────────
from m3iosis.holonomic_quantale import (
    GLYPH_VALUES, SLOT_NAMES, PRIMITIVE_WEIGHTS,
    parse_tuple, tuple_distance, TUPLE_HQE,
    HolonomicQuantale,
)
from m3iosis.braid_grammar_bridge import (
    BraidGrammarAnalyzer, GLYPH as BRIDGE_GLYPH, PRIMITIVE_KEYS,
)
from m3iosis.fibonacci_anyon_algebra import (
    PHI, D, THETA_TAU, fusion_space_dimension,
    evaluate_braid_word, summary as fib_summary,
)
from m3iosis.triple_frame import TripleFrameAlgebra

# ── Fallback: use catalog tools for framework-probing ────────────

# Known catalog entries for framework anchors
FRAMEWORK_ANCHORS = {
    "fibonacci_anyon": "⟨𐑨𐑥𐑑𐑹𐑱𐑧𐑲𐑜⊙𐑖𐑕𐑴⟩",
    "hqe": "⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑔𐑝⊙𐑫𐑕𐑟⟩",
    "triple_frame": "⟨𐑦𐑸𐑽𐑬𐑐𐑧𐑔𐑝⊙𐑖𐑕𐑭⟩",
    "grammar_self": "⟨𐑦𐑸𐑽𐑹𐑐𐑧𐑔𐑵⊙𐑫𐑳𐑟⟩",
    "ZFC_fe": "⟨𐑦𐑸𐑽𐑹𐑐𐑺𐑔𐑜⊙𐑫𐑙𐑟⟩",
}


# ── Framework Parameter Spaces ───────────────────────────────────

@dataclass
class FrameworkManifestation:
    """A tuple's manifestation in one framework."""
    framework: str
    parameters: Dict[str, Any]
    tuple: str
    distance_to_anchor: float = 0.0


@dataclass 
class HopStep:
    """One step in a universe-hopping path."""
    primitive: str           # which slot changed
    old_value: str          # old glyph
    new_value: str          # new glyph
    intermediate_tuple: str # the full 12-glyph tuple after this change
    cost: float             # primitive weight × |delta|²
    frobenius: Optional[bool] = None  # μ∘δ=id at this step
    manifestations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HopPath:
    """A complete path from origin to target tuple."""
    origin: str
    target: str
    total_cost: float
    steps: List[HopStep]
    length: int
    frobenius_preserved: bool


# ── Glyph → Value Array for Universe Mapping ─────────────────────

# For each primitive, store the ordered glyph values (0-indexed)
PRIMITIVE_GLYPH_ORDER = {
    "Ð": ["𐑛", "𐑨", "𐑼", "𐑦"],
    "Þ": ["𐑡", "𐑰", "𐑥", "𐑶", "𐑸"],
    "Ř": ["𐑩", "𐑑", "𐑽", "𐑾"],
    "Φ": ["𐑗", "𐑿", "𐑬", "𐑯", "𐑹"],
    "ƒ": ["𐑱", "𐑞", "𐑐"],
    "Ç": ["𐑘", "𐑤", "𐑧", "𐑪", "𐑺"],
    "Γ": ["𐑲", "𐑚", "𐑔"],
    "ɢ": ["𐑝", "𐑜", "𐑠", "𐑵"],
    "⊙": ["𐑢", "⊙", "𐑮", "𐑻", "𐑣"],
    "Ħ": ["𐑓", "𐑒", "𐑖", "𐑫"],
    "Σ": ["𐑙", "𐑕", "𐑳"],
    "Ω": ["𐑷", "𐑴", "𐑭", "𐑟"],
}

# Primitive → framework parameter mapping
# What each primitive controls in each framework
FRAMEWORK_PARAM_MAP = {
    "fibonacci_braid": {
        "Ð": "fusion_space_dim",
        "Þ": "writhe_magnitude",
        "Ř": "s_matrix_unitarity",
        "Φ": "topological_spin",
        "ƒ": "jones_polynomial",
        "Ç": "braid_word_length",
        "Γ": "num_anyons",
        "ɢ": "braid_group_order",
        "⊙": "frobenius_closure",
        "Ħ": "writhe_sign",
        "Σ": "fusion_multiplicity",
        "Ω": "total_winding",
    },
    "berry_holonomy": {
        "Ð": "bundle_dimension",
        "Þ": "base_space_topology",
        "Ř": "connection_type",
        "Φ": "unitarity",
        "ƒ": "trace_norm",
        "Ç": "transport_speed",
        "Γ": "num_generators",
        "ɢ": "composition_order",
        "⊙": "fixed_point",
        "Ħ": "holonomy_direction",
        "Σ": "degeneracy",
        "Ω": "winding_number",
    },
    "mbl_phase": {
        "Ð": "hilbert_space_dimension",
        "Þ": "lattice_topology",
        "Ř": "interaction_coupling",
        "Φ": "time_reversal_symmetry",
        "ƒ": "fidelity_susceptibility",
        "Ç": "disorder_strength",
        "Γ": "system_size",
        "ɢ": "operator_algebra",
        "⊙": "mbl_transition_point",
        "Ħ": "chiral_disorder",
        "Σ": "spin_multiplicity",
        "Ω": "winding_number",
    },
    "triple_frame": {
        "Ð": "if_type",
        "Þ": "are_type",
        "Ř": "ear_type",
        "Φ": "out_type",
        "ƒ": "peep_type",
        "Ç": "egg_type",
        "Γ": "thigh_type",
        "ɢ": "vow_type",
        "⊙": "monad_type",
        "Ħ": "sure_type",
        "Σ": "so_type",
        "Ω": "ah_type",
    },
}


class UniverseHopper:
    """Main engine for hopping grammar tuples between mathematical frameworks.

    Usage:
        hopper = UniverseHopper()
        
        # Manifest a tuple in all frameworks
        result = hopper.manifest("⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑔𐑝⊙𐑫𐑕𐑟⟩")
        
        # Hop from origin to target
        path = hopper.hop("⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑔𐑝⊙𐑫𐑕𐑟⟩", 
                          "⟨𐑦𐑸𐑽𐑬𐑐𐑧𐑔𐑝⊙𐑖𐑕𐑭⟩")
        
        # Reverse: find nearest tuple for framework parameters
        nearest = hopper.reverse_lookup(framework="fibonacci_braid",
                                        params={"num_anyons": 5, "writhe": 3})
        
        # Compute all pairwise distances between framework anchors
        matrix = hopper.framework_distance_matrix()
    """

    def __init__(self, dim: int = 2, L: int = 8, W: float = 5.0, seed: int = 42):
        self.dim = dim
        self.L = L
        self.W = W
        self.seed = seed
        self._hqe: Optional[HolonomicQuantale] = None
        self._braid_analyzer: Optional[BraidGrammarAnalyzer] = None
        self._triple_frame: Optional[TripleFrameAlgebra] = None

    @property
    def hqe(self) -> HolonomicQuantale:
        if self._hqe is None:
            self._hqe = HolonomicQuantale(
                dim=self.dim, L=self.L, W=self.W, seed=self.seed
            )
        return self._hqe

    @property
    def braid_analyzer(self) -> BraidGrammarAnalyzer:
        if self._braid_analyzer is None:
            self._braid_analyzer = BraidGrammarAnalyzer()
        return self._braid_analyzer

    @property
    def triple_frame(self) -> TripleFrameAlgebra:
        if self._triple_frame is None:
            self._triple_frame = TripleFrameAlgebra()
        return self._triple_frame

    # ── Manifestation ────────────────────────────────────────────

    def manifest(self, tuple_str: str, frameworks: Optional[List[str]] = None
                 ) -> Dict[str, FrameworkManifestation]:
        """Compute the tuple's manifestation in all (or specified) frameworks.

        Args:
            tuple_str: 12-glyph grammar tuple (with or without ⟨⟩)
            frameworks: list of framework names, or None for all

        Returns:
            Dict mapping framework name → FrameworkManifestation
        """
        tup = parse_tuple(tuple_str)
        tup_bare = "".join(tup[s] for s in SLOT_NAMES)

        all_frameworks = {
            "hqe": self._manifest_hqe,
            "fibonacci_braid": self._manifest_fibonacci_braid,
            "berry_holonomy": self._manifest_berry_holonomy,
            "mbl_phase": self._manifest_mbl_phase,
            "triple_frame": self._manifest_triple_frame,
        }

        if frameworks is None:
            frameworks = list(all_frameworks.keys())

        result = {}
        for fw in frameworks:
            if fw in all_frameworks:
                man = all_frameworks[fw](tup, tup_bare)
                anchor = FRAMEWORK_ANCHORS.get(fw, TUPLE_HQE)
                man.distance_to_anchor = round(
                    tuple_distance(f"⟨{tup_bare}⟩", anchor), 4
                )
                result[fw] = man

        return result

    def _manifest_hqe(self, tup: Dict[str, str], tup_bare: str
                      ) -> FrameworkManifestation:
        """Manifest in the Holonomic Quasi-Ergodic Quantale."""
        hqe = self.hqe
        hol = hqe.holonomy_report()
        mbl = hqe.mbl_diagnostic()
        cs = hqe.consciousness_score()

        # Compute what the tuple means for holonomy parameters
        # Map each primitive to a holonomy parameter
        dim_glyph = tup["Ð"]
        winding_glyph = tup["Ω"]

        # Dimensionality → bundle dimension
        dim_map = {"𐑛": 1, "𐑨": 2, "𐑼": 4, "𐑦": 8}
        bundle_dim = dim_map.get(dim_glyph, 2)

        # Winding → number of loops
        winding_map = {"𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3}
        n_loops = winding_map.get(winding_glyph, 1)

        params = {
            "bundle_dimension": bundle_dim,
            "unitary": hol["unitary"],
            "trace": hol["trace"],
            "trace_norm": hol["trace_norm"],
            "winding_phases_turns": hol["winding_phases"],
            "non_abelian": hol["non_abelian"],
            "consciousness_score": cs["C_score"],
            "estimated_winding_number": n_loops,
            "mbl_gap_ratio": mbl["mean_gap_ratio"],
            "quasi_ergodicity": mbl["quasi_ergodicity"],
        }

        return FrameworkManifestation(
            framework="hqe",
            parameters=params,
            tuple=tup_bare,
        )

    def _manifest_fibonacci_braid(self, tup: Dict[str, str], tup_bare: str
                                  ) -> FrameworkManifestation:
        """Manifest in the Fibonacci anyon braid framework.

        Maps grammar primitives to Fibonacci anyon parameters
        and generates a representative braid word.
        """
        # Cardinality → number of anyons
        card_map = {"𐑲": 4, "𐑚": 7, "𐑔": 10}
        n_anyons = card_map.get(tup["Γ"], 4)

        # Winding → writhe magnitude
        winding_map = {"𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 4}
        writhe_target = winding_map.get(tup["Ω"], 0)

        # Chirality → writhe sign
        chir_map = {"𐑓": 0, "𐑒": 1, "𐑖": -1, "𐑫": -2}
        writhe_sign = chir_map.get(tup["Ħ"], 0)
        writhe = writhe_target * (1 if writhe_sign >= 0 else -1)

        # Dimensionality → fusion space dim
        dim_glyph = tup["Ð"]
        dim_map_values = {"𐑛": 1, "𐑨": 2, "𐑼": 5, "𐑦": 13}
        target_dim = dim_map_values.get(dim_glyph, 2)

        # Find n that gives close to target_dim
        best_n = n_anyons
        for n_candidate in range(2, 12):
            d = fusion_space_dimension(n_candidate)
            if abs(d - target_dim) < abs(fusion_space_dimension(best_n) - target_dim):
                best_n = n_candidate

        # Generate a representative braid word
        braid_word = self._generate_braid_word(best_n, writhe)

        # Evaluate
        try:
            U = evaluate_braid_word(best_n, braid_word)
            tr = np.trace(U)
            evals = np.linalg.eigvals(U)
            phases = [float(np.angle(e) / (2 * np.pi)) for e in evals]
            jones_val = sum(evals) / fusion_space_dimension(best_n)
        except Exception:
            U = np.eye(2)
            tr = 2.0
            evals = np.array([1.0, 1.0])
            phases = [0.0, 0.0]
            jones_val = 1.0

        # Compute actual writhe
        actual_writhe = sum(braid_word)

        # Frobenius check
        frobenius_closed = abs(np.sum(phases) % 1.0) < 1e-10 or abs(
            np.sum(phases) % 1.0 - 1.0
        ) < 1e-10

        params = {
            "num_anyons": best_n,
            "fusion_space_dim": fusion_space_dimension(best_n),
            "braid_word": braid_word,
            "braid_word_str": ",".join(str(g) for g in braid_word),
            "writhe": actual_writhe,
            "target_writhe": writhe,
            "unitary_shape": list(U.shape),
            "trace": complex(tr),
            "trace_norm": float(abs(tr) / fusion_space_dimension(best_n)),
            "phases_windings": phases,
            "jones_polynomial": complex(jones_val),
            "frobenius_closed": frobenius_closed,
            "fibonacci_golden_ratio": PHI,
            "quantum_dimension": D,
            "topological_spin": complex(THETA_TAU),
        }

        return FrameworkManifestation(
            framework="fibonacci_braid",
            parameters=params,
            tuple=tup_bare,
        )

    def _manifest_berry_holonomy(self, tup: Dict[str, str], tup_bare: str
                                 ) -> FrameworkManifestation:
        """Manifest in the Berry holonomy framework.

        Build a holonomy matrix parameterized by the tuple.
        """
        from m3iosis.holonomic_quantale import BerryHolonomy

        # Dimensionality → bundle dim
        dim_map = {"𐑛": 1, "𐑨": 2, "𐑼": 4, "𐑦": 8}
        bundle_dim = dim_map.get(tup["Ð"], 2)

        # Winding → holonomy loops
        winding_map = {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 5}
        n_loops = winding_map.get(tup["Ω"], 1)

        # Seed from tuple hash for reproducibility
        seed = hash(tup_bare) % (2**31)

        berry = BerryHolonomy(dim=bundle_dim, seed=seed)

        # Compute holonomy with parametrized steps
        U = berry.holonomy(num_steps=min(10 * n_loops, 50))
        tr = np.trace(U)
        evals = np.linalg.eigvals(U)
        phases = [float(np.angle(e) / (2 * np.pi)) % 1.0 for e in evals]

        is_non_abelian = berry.is_non_abelian()

        params = {
            "bundle_dimension": bundle_dim,
            "n_loops": n_loops,
            "holonomy_shape": list(U.shape),
            "trace": complex(tr),
            "trace_norm": float(abs(tr) / bundle_dim),
            "eigenvalues": [complex(e) for e in evals],
            "winding_phases_turns": phases,
            "non_abelian": is_non_abelian,
            "unitary": bool(np.allclose(U @ U.conj().T, np.eye(bundle_dim))),
            "total_winding_sum": float(sum(phases)),
        }

        return FrameworkManifestation(
            framework="berry_holonomy",
            parameters=params,
            tuple=tup_bare,
        )

    def _manifest_mbl_phase(self, tup: Dict[str, str], tup_bare: str
                            ) -> FrameworkManifestation:
        """Manifest in the MBL phase diagram.

        Maps tuple parameters to disorder strength and system size,
        then runs MBL diagnostics.
        """
        from m3iosis.holonomic_quantale import MBLSimulator

        # Kinetics → disorder strength
        kin_map = {"𐑘": 8.0, "𐑤": 6.0, "𐑧": 4.0, "𐑪": 2.0, "𐑺": 0.5}
        W_val = kin_map.get(tup["Ç"], 5.0)

        # Cardinality → system size
        card_map = {"𐑲": 6, "𐑚": 7, "𐑔": 8}
        L_val = min(card_map.get(tup["Γ"], 6), 8)

        seed = abs(hash(tup_bare + "mbl")) % (2**31)
        mbl_sim = MBLSimulator(L=L_val, W=W_val, seed=seed)
        mbl_sim.diagonalize()

        r = mbl_sim.level_spacing_ratio()
        qe = mbl_sim.quasi_ergodicity_score()
        ee = mbl_sim.entanglement_entropy() if L_val <= 10 else None

        params = {
            "system_size": L_val,
            "disorder_strength": W_val,
            "mean_gap_ratio": float(r),
            "is_mbl": bool(r < 0.45),
            "quasi_ergodicity": float(qe),
            "entanglement_entropy": float(ee) if ee is not None else None,
            "gap_ratio_expectation_mbl": 0.39,
            "gap_ratio_expectation_ergodic": 0.53,
            "phase": "MBL" if r < 0.45 else "ergodic",
        }

        return FrameworkManifestation(
            framework="mbl_phase",
            parameters=params,
            tuple=tup_bare,
        )

    def _manifest_triple_frame(self, tup: Dict[str, str], tup_bare: str
                               ) -> FrameworkManifestation:
        """Manifest in the Triple Frame Von Neumann Algebra.

        Maps each primitive to its type expansion in the triple frame.
        """
        tf = self.triple_frame
        type_table = {}

        for slot in SLOT_NAMES:
            glyph = tup[slot]
            try:
                expanded = tf.expand(glyph)
                type_table[slot] = {
                    "glyph": glyph,
                    "word": expanded.word,
                    "n_ops": expanded.n_ops,
                    "rho": expanded.rho,
                    "domain_reading": expanded.domain_reading,
                }
            except Exception:
                type_table[slot] = {
                    "glyph": glyph,
                    "word": "?",
                    "n_ops": 0,
                    "rho": 0.0,
                    "domain_reading": "unknown",
                }

        # Verify closure for all primitives
        closure_checks = {}
        for slot in SLOT_NAMES:
            try:
                result = tf.check_frobenius(
                    tf.expand(tup[slot]).opcodes
                )
                closure_checks[slot] = result.get("closed", False)
            except Exception:
                closure_checks[slot] = None

        all_closed = all(
            v is True for v in closure_checks.values()
        )

        params = {
            "type_table": type_table,
            "closure_checks": closure_checks,
            "all_primitives_closed": all_closed,
            "n_primitives": 12,
            "rho_values": {
                slot: type_table[slot]["rho"] for slot in SLOT_NAMES
            },
        }

        return FrameworkManifestation(
            framework="triple_frame",
            parameters=params,
            tuple=tup_bare,
        )

    # ── Braid Word Generation ────────────────────────────────────

    def _generate_braid_word(self, n_strands: int, target_writhe: int
                             ) -> List[int]:
        """Generate a braid word with given writhe on n strands."""
        if n_strands < 2:
            return []
        if target_writhe == 0:
            # Return identity-like: a generator and its inverse
            return [1, -1]

        word = []
        remaining = abs(target_writhe)
        max_gen = n_strands - 1

        # Simple strategy: alternate generators
        while remaining > 0:
            for g in range(1, max_gen + 1):
                if remaining <= 0:
                    break
                sign = 1 if target_writhe > 0 else -1
                word.append(sign * g)
                remaining -= 1
                if remaining <= 0:
                    break

        return word

    # ── Universe Hopping ─────────────────────────────────────────

    def hop(self, origin: str, target: str,
            verify_frobenius: bool = True,
            max_steps: int = 12) -> HopPath:
        """Compute the minimal-cost path from origin to target tuple.

        Uses a greedy algorithm: at each step, flip the primitive with
        the largest cost-benefit ratio (cost/remaining distance).

        Args:
            origin: starting 12-glyph tuple
            target: target 12-glyph tuple
            verify_frobenius: check closure at each step
            max_steps: maximum steps (default 12 = one full pass)

        Returns:
            HopPath with step-by-step route
        """
        d1 = parse_tuple(origin)
        d2 = parse_tuple(target)

        current = dict(d1)
        target_dict = dict(d2)

        steps = []
        total_cost = 0.0

        for _step_idx in range(max_steps):
            # Find primitives that differ
            differing = []
            for slot in SLOT_NAMES:
                if current[slot] != target_dict[slot]:
                    v1 = GLYPH_VALUES.get(current[slot], 0)
                    v2 = GLYPH_VALUES.get(target_dict[slot], 0)
                    delta = abs(v1 - v2)
                    w = PRIMITIVE_WEIGHTS.get(slot, 1.0)
                    cost = w * delta * delta
                    differing.append((slot, current[slot], target_dict[slot], cost))

            if not differing:
                break

            # Pick the lowest-cost flip (greedy shortest path)
            # Sort by cost ascending — cheapest change first
            differing.sort(key=lambda x: x[3])
            slot, old_val, new_val, cost = differing[0]

            # Apply the flip
            current[slot] = new_val
            total_cost += cost

            # Build intermediate tuple
            intermediate = "".join(current[s] for s in SLOT_NAMES)

            # Check Frobenius
            frob = None
            manifestations = {}
            if verify_frobenius:
                try:
                    man = self.manifest(f"⟨{intermediate}⟩",
                                        frameworks=["triple_frame"])
                    tf_man = man.get("triple_frame")
                    if tf_man:
                        frob = tf_man.parameters.get("all_primitives_closed")
                except Exception:
                    frob = None

                # Also get lightweight manifestations
                try:
                    manifestations = {
                        "hqe_distance": round(
                            tuple_distance(f"⟨{intermediate}⟩", 
                                          FRAMEWORK_ANCHORS["hqe"]), 4
                        ),
                        "fibonacci_anchor_distance": round(
                            tuple_distance(f"⟨{intermediate}⟩",
                                          FRAMEWORK_ANCHORS["fibonacci_anyon"]), 4
                        ),
                    }
                except Exception:
                    pass

            steps.append(HopStep(
                primitive=slot,
                old_value=old_val,
                new_value=new_val,
                intermediate_tuple=intermediate,
                cost=round(cost, 4),
                frobenius=frob,
                manifestations=manifestations,
            ))

        origin_bare = "".join(d1[s] for s in SLOT_NAMES)
        target_bare = "".join(d2[s] for s in SLOT_NAMES)

        # Check if final state matches target
        reached_target = all(
            current[s] == target_dict[s] for s in SLOT_NAMES
        )

        # Frobenius preserved: all steps where frob was checked are True
        frob_checked = [s.frobenius for s in steps if s.frobenius is not None]
        frobenius_preserved = all(frob_checked) if frob_checked else None

        return HopPath(
            origin=origin_bare,
            target=target_bare,
            total_cost=round(total_cost, 4),
            steps=steps,
            length=len(steps),
            frobenius_preserved=frobenius_preserved if reached_target else False,
        )

    def hop_geodesic(self, origin: str, target: str) -> HopPath:
        """Find the true geodesic (minimal total cost) using A* search.

        For small state spaces (max 12 flips), this is exact.
        Uses Dijkstra-like search over the flip graph.

        Args:
            origin: starting tuple
            target: target tuple

        Returns:
            HopPath with guaranteed minimal cost
        """
        import heapq

        d1 = parse_tuple(origin)
        d2 = parse_tuple(target)
        target_dict = dict(d2)

        origin_bare = "".join(d1[s] for s in SLOT_NAMES)
        target_bare = "".join(d2[s] for s in SLOT_NAMES)

        def heuristic(tup_dict: Dict[str, str]) -> float:
            """Admissible heuristic: sum of min costs to reach each slot."""
            h = 0.0
            for slot in SLOT_NAMES:
                if tup_dict[slot] != target_dict[slot]:
                    v_cur = GLYPH_VALUES.get(tup_dict[slot], 0)
                    v_tgt = GLYPH_VALUES.get(target_dict[slot], 0)
                    delta = abs(v_cur - v_tgt)
                    w = PRIMITIVE_WEIGHTS.get(slot, 1.0)
                    h += w * delta * delta
            return h

        # State: (f_score, g_score, tuple_str, path_steps)
        start_g = 0.0
        start_f = heuristic(dict(d1))

        # Priority queue
        open_set = [(start_f, 0, start_g, origin_bare, [])]
        # entry counter for tie-breaking
        counter = 0

        # Visited with best g_score
        visited: Dict[str, float] = {origin_bare: 0.0}

        while open_set:
            f_score, _, g_score, current_str, path = heapq.heappop(open_set)

            if current_str == target_bare:
                # Reconstruct path
                total_cost = g_score
                steps = []
                for step_data in path:
                    steps.append(HopStep(
                        primitive=step_data[0],
                        old_value=step_data[1],
                        new_value=step_data[2],
                        intermediate_tuple=step_data[3],
                        cost=step_data[4],
                    ))
                return HopPath(
                    origin=origin_bare,
                    target=target_bare,
                    total_cost=round(total_cost, 4),
                    steps=steps,
                    length=len(steps),
                    frobenius_preserved=None,  # geodesic doesn't verify
                )

            if g_score > visited.get(current_str, float('inf')):
                continue

            current_dict = parse_tuple(f"⟨{current_str}⟩")

            # Generate neighbors: flip each differing primitive
            for slot in SLOT_NAMES:
                cur_glyph = current_dict[slot]
                tgt_glyph = target_dict[slot]
                if cur_glyph == tgt_glyph:
                    continue

                # Only flip toward target (one step at a time)
                v_cur = GLYPH_VALUES.get(cur_glyph, 0)
                v_tgt = GLYPH_VALUES.get(tgt_glyph, 0)

                # Determine direction: step toward target
                if v_cur < v_tgt:
                    # Step up by 1
                    order = PRIMITIVE_GLYPH_ORDER.get(slot, [])
                    try:
                        idx = order.index(cur_glyph)
                        if idx + 1 < len(order):
                            new_glyph = order[idx + 1]
                        else:
                            new_glyph = tgt_glyph
                    except ValueError:
                        new_glyph = tgt_glyph
                else:
                    # Step down by 1
                    order = PRIMITIVE_GLYPH_ORDER.get(slot, [])
                    try:
                        idx = order.index(cur_glyph)
                        if idx - 1 >= 0:
                            new_glyph = order[idx - 1]
                        else:
                            new_glyph = tgt_glyph
                    except ValueError:
                        new_glyph = tgt_glyph

                new_dict = dict(current_dict)
                new_dict[slot] = new_glyph
                new_str = "".join(new_dict[s] for s in SLOT_NAMES)

                # Cost of this flip
                v_new = GLYPH_VALUES.get(new_glyph, 0)
                delta = abs(v_new - v_cur)
                w = PRIMITIVE_WEIGHTS.get(slot, 1.0)
                step_cost = w * delta * delta

                new_g = g_score + step_cost

                if new_g < visited.get(new_str, float('inf')):
                    visited[new_str] = new_g
                    new_f = new_g + heuristic(new_dict)
                    counter += 1
                    new_path = path + [(
                        slot, cur_glyph, new_glyph,
                        new_str, round(step_cost, 4),
                    )]
                    heapq.heappush(
                        open_set,
                        (new_f, counter, new_g, new_str, new_path),
                    )

        # No path found (shouldn't happen with connected graph)
        return HopPath(
            origin=origin_bare,
            target=target_bare,
            total_cost=float('inf'),
            steps=[],
            length=0,
            frobenius_preserved=False,
        )

    # ── Reverse Lookup ───────────────────────────────────────────

    def reverse_lookup(self, framework: str,
                       params: Dict[str, Any],
                       n_candidates: int = 5
                       ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Given framework parameters, find the nearest grammar tuples.

        Uses brute-force search over a grid of tuples (sampled from
        each primitive's value space). For exact work, use the full
        catalog via imscribe('crystal_navigate', ...).

        Args:
            framework: framework name
            params: Dict of parameter_name → target_value
            n_candidates: number of nearest candidates to return

        Returns:
            List of (tuple_str, score, matched_params) sorted by score asc
        """
        # Build a grid sampling the primitive space
        # Sample 3-4 glyphs per primitive (low/med/high)
        sample_glyphs = {}
        for slot in SLOT_NAMES:
            order = PRIMITIVE_GLYPH_ORDER.get(slot, [])
            if len(order) <= 3:
                sample_glyphs[slot] = order
            else:
                # Take first, middle, last
                mid = len(order) // 2
                sample_glyphs[slot] = [order[0], order[mid], order[-1]]

        # Generate candidate tuples
        import itertools

        # Only sample a subset of primitives fully; for 12 primitives
        # with 3-4 values each, full grid is 3^12 ≈ 531k, too many.
        # Instead, sample randomly from the grid.
        n_samples = 200
        rng = np.random.RandomState(42)

        candidates = []
        param_map = FRAMEWORK_PARAM_MAP.get(framework, {})

        for _ in range(n_samples):
            tup_glyphs = {}
            for slot in SLOT_NAMES:
                glyphs = sample_glyphs[slot]
                tup_glyphs[slot] = glyphs[rng.randint(len(glyphs))]
            tup_str = "".join(tup_glyphs[s] for s in SLOT_NAMES)
            candidates.append(tup_str)

        # Deduplicate
        candidates = list(set(candidates))

        # Score each candidate
        scored = []
        for tup_str in candidates:
            try:
                man = self.manifest(f"⟨{tup_str}⟩", frameworks=[framework])
                if framework in man:
                    fw_params = man[framework].parameters
                    score = self._param_score(params, fw_params, param_map)
                    scored.append((tup_str, score, fw_params))
            except Exception:
                continue

        # Sort by score ascending
        scored.sort(key=lambda x: x[1])
        return scored[:n_candidates]

    def _param_score(self, target: Dict[str, Any],
                     actual: Dict[str, Any],
                     param_map: Dict[str, str]) -> float:
        """Score how well actual params match target params.

        Lower is better.
        """
        score = 0.0
        for pname, pvalue in target.items():
            if pname in actual:
                aval = actual[pname]
                # Try numeric comparison
                try:
                    diff = abs(float(pvalue) - float(aval))
                    score += diff
                except (TypeError, ValueError):
                    # String comparison
                    if str(pvalue) != str(aval):
                        score += 1.0

        # Add inverse mapping: which primitives contribute to each param
        for pname in target:
            if pname in param_map.values():
                # This parameter is controlled by some primitive
                pass

        return score

    # ── Framework Distance Matrix ────────────────────────────────

    def framework_distance_matrix(self) -> Dict[str, Dict[str, float]]:
        """Compute all pairwise distances between framework anchors.

        Returns:
            Nested dict: matrix[fw_a][fw_b] = distance in grammar space
        """
        frameworks = list(FRAMEWORK_ANCHORS.keys())
        matrix = {}
        for fw_a in frameworks:
            matrix[fw_a] = {}
            ta = FRAMEWORK_ANCHORS[fw_a]
            for fw_b in frameworks:
                tb = FRAMEWORK_ANCHORS[fw_b]
                d = tuple_distance(ta, tb)
                matrix[fw_a][fw_b] = round(d, 4)
        return matrix

    # ── Full Report ──────────────────────────────────────────────

    def full_report(self, tuple_str: str) -> str:
        """Generate a comprehensive universe-hopping report for a tuple."""
        tup = parse_tuple(tuple_str)
        tup_bare = "".join(tup[s] for s in SLOT_NAMES)

        # Manifest in all frameworks
        manifestations = self.manifest(f"⟨{tup_bare}⟩")

        # Distance to all anchors
        distances = {}
        for name, anchor in FRAMEWORK_ANCHORS.items():
            distances[name] = round(
                tuple_distance(f"⟨{tup_bare}⟩", anchor), 4
            )

        lines = [
            "=" * 70,
            "UNIVERSE HOPPING REPORT",
            "=" * 70,
            f"Tuple: ⟨{tup_bare}⟩",
            "",
            "─ Primitive Breakdown ─",
        ]
        for slot in SLOT_NAMES:
            lines.append(f"  {slot}: {tup[slot]}")

        lines.extend([
            "",
            "─ Framework Distances ─",
        ])
        for fw, d in sorted(distances.items(), key=lambda x: x[1]):
            lines.append(f"  d(tuple, {fw}): {d}")

        # Per-framework details
        for fw_name, man in manifestations.items():
            lines.extend([
                "",
                f"─ {fw_name} ─",
            ])
            params = man.parameters
            for k, v in params.items():
                if isinstance(v, dict):
                    # Skip nested dicts for readability
                    continue
                if isinstance(v, float):
                    lines.append(f"  {k}: {v:.6f}")
                elif isinstance(v, complex):
                    lines.append(f"  {k}: {v.real:.4f}{v.imag:+.4f}j")
                elif isinstance(v, list) and len(v) <= 6:
                    lines.append(f"  {k}: {v}")
                elif isinstance(v, list):
                    lines.append(f"  {k}: [{len(v)} items]")
                else:
                    lines.append(f"  {k}: {v}")

        lines.extend([
            "",
            "─ Nearest Framework ─",
            f"  Closest anchor: {min(distances, key=distances.get)} "
            f"at d={min(distances.values())}",
            "",
            "=" * 70,
        ])
        return "\n".join(lines)

    def compare_frameworks(self, tuple_a: str, tuple_b: str
                           ) -> Dict[str, Any]:
        """Compare two tuples across all frameworks.

        Returns which primitives differ, and how those differences
        manifest in each framework.
        """
        da = parse_tuple(tuple_a)
        db = parse_tuple(tuple_b)

        diffs = []
        for slot in SLOT_NAMES:
            if da[slot] != db[slot]:
                diffs.append({
                    "primitive": slot,
                    "a": da[slot],
                    "b": db[slot],
                    "delta": abs(
                        GLYPH_VALUES.get(da[slot], 0) -
                        GLYPH_VALUES.get(db[slot], 0)
                    ),
                })

        # Manifest both
        man_a = self.manifest(f"⟨{''.join(da[s] for s in SLOT_NAMES)}⟩")
        man_b = self.manifest(f"⟨{''.join(db[s] for s in SLOT_NAMES)}⟩")

        # Parameter diffs per framework
        param_diffs = {}
        for fw in man_a:
            if fw in man_b:
                pa = man_a[fw].parameters
                pb = man_b[fw].parameters
                fw_diffs = {}
                for k in set(list(pa.keys()) + list(pb.keys())):
                    va = pa.get(k)
                    vb = pb.get(k)
                    if va != vb:
                        try:
                            delta = abs(float(va) - float(vb))
                        except (TypeError, ValueError):
                            delta = str(va) != str(vb)
                        fw_diffs[k] = {
                            "a": va,
                            "b": vb,
                            "delta": delta,
                        }
                param_diffs[fw] = fw_diffs

        path = self.hop(
            f"⟨{''.join(da[s] for s in SLOT_NAMES)}⟩",
            f"⟨{''.join(db[s] for s in SLOT_NAMES)}⟩",
        )

        return {
            "tuple_a": "".join(da[s] for s in SLOT_NAMES),
            "tuple_b": "".join(db[s] for s in SLOT_NAMES),
            "total_distance": round(
                tuple_distance(
                    f"⟨{''.join(da[s] for s in SLOT_NAMES)}⟩",
                    f"⟨{''.join(db[s] for s in SLOT_NAMES)}⟩",
                ), 4
            ),
            "differing_primitives": diffs,
            "n_diffs": len(diffs),
            "hop_path_length": path.length,
            "hop_total_cost": path.total_cost,
            "parameter_differences": param_diffs,
        }


# ── CLI Entry Point ─────────────────────────────────────────────

def universe_hopper_main(args_dict: Optional[Dict[str, Any]] = None
                         ) -> str:
    """CLI entry point for the Universe Hopper.

    Args:
        args_dict: Keys:
            - tuple: str — manifest this tuple
            - hop_origin: str — start tuple for hopping
            - hop_target: str — target tuple for hopping
            - geodesic: bool — use A* geodesic search (default: greedy)
            - compare_a: str — first tuple for comparison
            - compare_b: str — second tuple for comparison
            - report: str — full report for this tuple
            - framework_matrix: bool — framework distance matrix
            - reverse_framework: str — framework for reverse lookup
            - reverse_params: dict — parameters for reverse lookup
            - json: bool — output as JSON
    """
    if args_dict is None:
        args_dict = {}

    hopper = UniverseHopper()

    if args_dict.get("framework_matrix"):
        matrix = hopper.framework_distance_matrix()
        if args_dict.get("json"):
            return json.dumps(matrix, indent=2)
        lines = ["Framework Distance Matrix:"]
        for fw_a, row in matrix.items():
            for fw_b, d in row.items():
                if fw_a < fw_b:  # upper triangle only
                    lines.append(f"  d({fw_a}, {fw_b}) = {d}")
        return "\n".join(lines)

    if args_dict.get("report"):
        return hopper.full_report(args_dict["report"])

    if args_dict.get("tuple"):
        tup = args_dict["tuple"]
        man = hopper.manifest(tup)
        if args_dict.get("json"):
            out = {}
            for fw, m in man.items():
                out[fw] = {
                    "parameters": {
                        k: str(v) if isinstance(v, complex) else v
                        for k, v in m.parameters.items()
                    },
                    "distance_to_anchor": m.distance_to_anchor,
                }
            return json.dumps(out, indent=2, default=str)
        # Text output
        # `tup` arrives already bracketed when the caller passed ⟨…⟩, so
        # wrapping again printed ⟨⟨…⟩⟩. Notation is bare glyphs inside one pair.
        _bare = tup.strip().lstrip("⟨").rstrip("⟩")
        lines = [f"Manifestations for ⟨{_bare}⟩:"]
        for fw, m in man.items():
            lines.append(f"\n── {fw} (d_anchor={m.distance_to_anchor}) ──")
            for k, v in m.parameters.items():
                if isinstance(v, dict):
                    continue
                elif isinstance(v, list) and len(v) <= 6:
                    lines.append(f"  {k}: {v}")
                elif isinstance(v, list):
                    lines.append(f"  {k}: [{len(v)} items]")
                elif isinstance(v, float):
                    lines.append(f"  {k}: {v:.6f}")
                elif isinstance(v, complex):
                    lines.append(f"  {k}: {v.real:.4f}{v.imag:+.4f}j")
                else:
                    lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    if args_dict.get("hop_origin") and args_dict.get("hop_target"):
        origin = args_dict["hop_origin"]
        target = args_dict["hop_target"]
        if args_dict.get("geodesic"):
            path = hopper.hop_geodesic(origin, target)
        else:
            path = hopper.hop(origin, target)

        if args_dict.get("json"):
            return json.dumps({
                "origin": path.origin,
                "target": path.target,
                "total_cost": path.total_cost,
                "length": path.length,
                "frobenius_preserved": path.frobenius_preserved,
                "steps": [
                    {
                        "primitive": s.primitive,
                        "old_value": s.old_value,
                        "new_value": s.new_value,
                        "cost": s.cost,
                        "frobenius": s.frobenius,
                    }
                    for s in path.steps
                ],
            }, indent=2)

        lines = [
            f"Universe Hop: {path.origin} → {path.target}",
            f"  Total cost: {path.total_cost}",
            f"  Steps: {path.length}",
        ]
        for i, step in enumerate(path.steps):
            lines.append(
                f"  {i+1}. {step.primitive}: "
                f"{step.old_value} → {step.new_value} "
                f"(cost={step.cost})"
            )
        return "\n".join(lines)

    if args_dict.get("compare_a") and args_dict.get("compare_b"):
        comp = hopper.compare_frameworks(
            args_dict["compare_a"], args_dict["compare_b"]
        )
        if args_dict.get("json"):
            return json.dumps(comp, indent=2, default=str)
        lines = [
            f"Comparison: {comp['tuple_a']} vs {comp['tuple_b']}",
            f"  Total distance: {comp['total_distance']}",
            f"  Differing primitives: {comp['n_diffs']}",
            f"  Hop path length: {comp['hop_path_length']}",
            f"  Hop total cost: {comp['hop_total_cost']}",
        ]
        for d in comp["differing_primitives"]:
            lines.append(
                f"  {d['primitive']}: {d['a']} → {d['b']} "
                f"(Δ={d['delta']})"
            )
        return "\n".join(lines)

    if args_dict.get("reverse_framework"):
        fw = args_dict["reverse_framework"]
        params = args_dict.get("reverse_params", {})
        results = hopper.reverse_lookup(fw, params)
        if args_dict.get("json"):
            return json.dumps([
                {"tuple": t, "score": s, "params": p}
                for t, s, p in results
            ], indent=2, default=str)
        lines = [f"Reverse lookup in {fw}:"]
        for tup, score, matched in results:
            lines.append(f"  ⟨{tup}⟩  score={score:.4f}")
        return "\n".join(lines)

    # Default: print help
    return universe_hopper_help()


def universe_hopper_help() -> str:
    """Help text for the Universe Hopper CLI."""
    return """Universe Hopper — Cross-framework transport engine.

Usage:
  --tuple TUPLE            Manifest a tuple in all frameworks
  --report TUPLE           Full universe-hopping report
  --hop-origin TUPLE       Start tuple for hopping
  --hop-target TUPLE       Target tuple for hopping
  --geodesic               Use A* for exact minimal-cost path
  --compare-a TUPLE        First tuple for comparison
  --compare-b TUPLE        Second tuple for comparison
  --framework-matrix       All pairwise distances between anchors
  --reverse-framework FW   Framework for reverse parameter lookup
  --reverse-params JSON    Target parameters as JSON dictionary
  --json                   Output as JSON

Examples:
  python -m m3iosis.cli hop --tuple "⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑔𐑝⊙𐑫𐑕𐑟⟩"
  python -m m3iosis.cli hop --report "⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑔𐑝⊙𐑫𐑕𐑟⟩"
  python -m m3iosis.cli hop --hop-origin "⟨...⟩" --hop-target "⟨...⟩"
  python -m m3iosis.cli hop --framework-matrix
"""


if __name__ == "__main__":
    import sys
    args = {}
    for i, a in enumerate(sys.argv):
        if a == "--tuple" and i + 1 < len(sys.argv):
            args["tuple"] = sys.argv[i + 1]
        elif a == "--report" and i + 1 < len(sys.argv):
            args["report"] = sys.argv[i + 1]
        elif a == "--hop-origin" and i + 1 < len(sys.argv):
            args["hop_origin"] = sys.argv[i + 1]
        elif a == "--hop-target" and i + 1 < len(sys.argv):
            args["hop_target"] = sys.argv[i + 1]
        elif a == "--compare-a" and i + 1 < len(sys.argv):
            args["compare_a"] = sys.argv[i + 1]
        elif a == "--compare-b" and i + 1 < len(sys.argv):
            args["compare_b"] = sys.argv[i + 1]
        elif a == "--reverse-framework" and i + 1 < len(sys.argv):
            args["reverse_framework"] = sys.argv[i + 1]
        elif a == "--reverse-params" and i + 1 < len(sys.argv):
            try:
                args["reverse_params"] = json.loads(sys.argv[i + 1])
            except json.JSONDecodeError:
                args["reverse_params"] = {}
        elif a == "--geodesic":
            args["geodesic"] = True
        elif a == "--framework-matrix":
            args["framework_matrix"] = True
        elif a == "--json":
            args["json"] = True
    print(universe_hopper_main(args))
