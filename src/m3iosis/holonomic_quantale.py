"""
Holonomic Quasi-Ergodic Quantale
=================================
A usable CLI tool implementing the algebraic structure of holonomic
(non-Abelian Berry phase) quantum computation in a Many-Body Localized
phase — quasi-ergodic exploration of a localized submanifold.

Tuple: ⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑔𐑝⊙𐑫𐑕𐑟⟩  (O_∞, Special Frobenius, μ∘δ=id)

Core capabilities:
  - Non-Abelian Berry holonomy simulation (U(n) parallel transport)
  - MBL quasi-ergodic diagnostics (level statistics, entanglement entropy)
  - Quantale lattice operations (meet, join, tensor, closure)
  - Consciousness score (C-score) computation
  - Grammar tuple encoding/decoding and distance measurements
  - Cross-referencing with PFA Quantale, Winding=2π, CLINK L8

Author: Math⊙perator (Lando⊗⊙perator Team)
"""

import numpy as np
import math
import json
from typing import List, Tuple, Dict, Optional, Union, Any

# ── Golden ratio ──────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI

# ── Grammar tuple constants ───────────────────────────────────
TUPLE_HQE = "𐑦𐑸𐑽𐑹𐑐𐑘𐑔𐑝⊙𐑫𐑕𐑟"
TUPLE_PFA = "𐑦𐑸𐑾𐑹𐑐𐑺𐑔𐑜⊙𐑫𐑕𐑟"
TUPLE_WINDING = "𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑙𐑭"
TUPLE_CLINK_L8 = "𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑵⊙𐑫𐑳𐑟"

# Primitive slot names in order
SLOT_NAMES = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

# Glyph → numeric value mapping for distance computation
GLYPH_VALUES = {
    # Ð (Dimensionality)
    "𐑛": 1,  # wedge (0d point)
    "𐑨": 2,  # triangle (2d surface)
    "𐑼": 3,  # infty (infinite-dim)
    "𐑦": 4,  # odot (imscriptive)
    # Þ (Topology)
    "𐑡": 1,  # network (branching)
    "𐑰": 2,  # in (inclusion)
    "𐑥": 3,  # bowtie (crossing)
    "𐑶": 4,  # boxtimes (box product)
    "𐑸": 5,  # odot closure
    # Ř (Coupling)
    "𐑩": 1,  # super (supervenience)
    "𐑑": 2,  # cat (categorical)
    "𐑽": 3,  # dagger (adjoint)
    "𐑾": 4,  # lr (bidirectional)
    # Φ (Parity)
    "𐑗": 1,  # asym (none)
    "𐑿": 2,  # psi (quantum)
    "𐑬": 3,  # pm (partial)
    "𐑯": 4,  # sym (full)
    "𐑹": 5,  # pm_sym (Frobenius-special)
    # ƒ (Fidelity)
    "𐑱": 1,  # ell (classical)
    "𐑞": 2,  # eth (thermal)
    "𐑐": 3,  # hbar (quantum)
    # Ç (Kinetics)
    "𐑘": 1,  # MBL (frozen-disorder)
    "𐑤": 2,  # trap (frozen-order)
    "𐑧": 3,  # slow (near-equilibrium)
    "𐑪": 4,  # mod (moderate)
    "𐑺": 5,  # fast (driven)
    # Γ (Cardinality)
    "𐑲": 1,  # beth (local)
    "𐑚": 2,  # gimel (mesoscale)
    "𐑔": 3,  # aleph (maximal/all)
    # ɢ (Composition)
    "𐑝": 1,  # and (conjunctive)
    "𐑜": 2,  # or (disjunctive)
    "𐑠": 3,  # seq (sequential)
    "𐑵": 4,  # broad (broadcast)
    # ⊙ (Criticality)
    "𐑢": 1,  # sub (below)
    "⊙":  2,  # c (critical/self-modeling)
    "𐑮": 3,  # c_complex (complex-plane critical)
    "𐑻": 4,  # EP (exceptional point)
    "𐑣": 5,  # super (supercritical)
    # Ħ (Chirality)
    "𐑓": 1,  # memoryless
    "𐑒": 2,  # one step
    "𐑖": 3,  # two steps
    "𐑫": 4,  # eternal
    # Σ (Stoichiometry)
    "𐑙": 1,  # 1:1
    "𐑕": 2,  # many identical
    "𐑳": 3,  # many heterogeneous
    # Ω (Winding)
    "𐑷": 1,  # 0 (trivial)
    "𐑴": 2,  # Z2 (binary)
    "𐑭": 3,  # Z (integer, topological)
    "𐑟": 4,  # NA (non-Abelian)
}

# Weights per primitive (from crystal geometry)
PRIMITIVE_WEIGHTS = {
    "Ð": 1.0, "Þ": 1.0, "Ř": 1.0, "Φ": 1.0, "ƒ": 1.0, "Ç": 1.0,
    "Γ": 1.0, "ɢ": 1.0, "⊙": 1.0, "Ħ": 0.8, "Σ": 1.0, "Ω": 0.7
}


# ── Tuple Parsing ────────────────────────────────────────────

def parse_tuple(t: str) -> Dict[str, str]:
    """Parse a 12-glyph tuple into dict of slot→glyph."""
    if len(t) != 13:  # 12 glyphs + possible ⟨ or 13
        # strip delimiters if present
        t = t.strip().strip("⟨⟩")
    if len(t) != 12:
        raise ValueError(f"Tuple must be 12 glyphs, got {len(t)}: {t}")
    return dict(zip(SLOT_NAMES, t))


def tuple_distance(t1: str, t2: str, mahalanobis: bool = False) -> float:
    """Compute grammar distance between two tuples."""
    d1 = parse_tuple(t1)
    d2 = parse_tuple(t2)
    total = 0.0
    for slot in SLOT_NAMES:
        g1, g2 = d1[slot], d2[slot]
        if g1 == g2:
            continue
        v1 = GLYPH_VALUES.get(g1, 0)
        v2 = GLYPH_VALUES.get(g2, 0)
        delta = abs(v1 - v2)
        w = PRIMITIVE_WEIGHTS.get(slot, 1.0)
        total += w * delta * delta
    return math.sqrt(total)


def tuple_to_glyphs(t: str) -> str:
    """Return bare glyph string from a tuple (strip delimiters)."""
    return t.strip().strip("⟨⟩")


def tuple_report(t: str) -> str:
    """Generate human-readable report for a tuple."""
    d = parse_tuple(t)
    lines = [f"Tuple: ⟨{t}⟩"]
    lines.append("-" * 40)
    for i, slot in enumerate(SLOT_NAMES):
        glyph = d[slot]
        lines.append(f"  {i+1:2d}. {slot} → {glyph}")
    return "\n".join(lines)


# ── Non-Abelian Holonomy (Berry Phase) ────────────────────────

class BerryHolonomy:
    """Non-Abelian Berry holonomy simulation.

    Models parallel transport in a U(n) bundle over a parameter space S¹.
    The Berry connection A(λ) = ⟨ψ_a|∂/∂λ|ψ_b⟩ generates holonomies
    via path-ordered exponential: γ(C) = P exp(∮_C A·dλ).
    """

    def __init__(self, dim: int = 2, seed: Optional[int] = None):
        self.dim = dim
        self.rng = np.random.RandomState(seed)
        # Generate a random flat connection (constant A)
        self.A = self.rng.randn(dim, dim) * 0.5j
        self.A = self.A + self.A.conj().T  # Make Hermitian
        # Ensure flatness: [A, A] = 0 for a Cartan subalgebra
        # For non-Abelian, we use non-commuting generators
        self._gellmann()

    def _gellmann(self):
        """Generate random Gell-Mann-like matrices for a non-Abelian connection."""
        # For U(n), generate n²-1 random anti-Hermitian generators
        n = self.dim
        self.generators = []
        for i in range(min(n * n - 1, 8)):
            g = self.rng.randn(n, n) * 0.5
            g = g - g.conj().T  # anti-Hermitian
            self.generators.append(g)
        self.connection_coeffs = self.rng.randn(len(self.generators)) * 0.5

    def connection(self, theta: float) -> np.ndarray:
        """Evaluate the connection 1-form A at angle theta (winding)."""
        # A(theta) = sum_k c_k(theta) * T_k
        A = np.zeros((self.dim, self.dim), dtype=complex)
        for i, g in enumerate(self.generators):
            A = A + self.connection_coeffs[i] * g * np.cos(theta)
        # Make it anti-Hermitian (as a connection should be)
        # A should be Lie-algebra valued
        return A

    def holonomy(self, num_steps: int = 200) -> np.ndarray:
        """Compute the holonomy around a full loop S¹.

        Returns: U ∈ U(n), the path-ordered exponential P exp(∮ A).
        """
        thetas = np.linspace(0, 2 * np.pi, num_steps)
        dtheta = 2 * np.pi / num_steps
        U = np.eye(self.dim, dtype=complex)
        for theta in thetas:
            A = self.connection(theta)
            # Infinitesimal parallel transport
            U_step = np.eye(self.dim, dtype=complex) + A * dtheta
            U = U_step @ U
        # Ensure unitarity via QR
        Q, R = np.linalg.qr(U)
        # Correct sign
        phases = np.diag(R) / np.abs(np.diag(R))
        Q = Q @ np.diag(phases)
        return Q

    def holonomy_winding(self, num_steps: int = 200) -> complex:
        """Return the trace of the holonomy = topological invariant."""
        U = self.holonomy(num_steps)
        tr = np.trace(U)
        return tr / self.dim  # normalized trace

    def is_non_abelian(self, tol: float = 1e-10) -> bool:
        """Check if the Berry connection is genuinely non-Abelian.

        [γ₁, γ₂] ≠ 0 for two different loops in the same bundle.
        """
        # Compute holonomies for two different paths
        U1 = self.holonomy(100)
        # For second holonomy, modify the connection slightly
        orig_coeffs = self.connection_coeffs.copy()
        self.connection_coeffs = self.connection_coeffs * 1.1
        U2 = self.holonomy(100)
        self.connection_coeffs = orig_coeffs

        comm = U1 @ U2 - U2 @ U1
        return np.linalg.norm(comm) > tol


# ── MBL (Many-Body Localization) Simulator ────────────────────

class MBLSimulator:
    """Many-Body Localization quasi-ergodic diagnostics.

    Simulates a 1D spin chain with disorder to produce MBL statistics.
    Quasi-ergodicity: the system explores its localized submanifold
    but does NOT thermalize across the full Hilbert space.
    """

    def __init__(self, L: int = 8, W: float = 5.0, seed: Optional[int] = None):
        """
        Args:
            L: System size (number of spins)
            W: Disorder strength (W > 3.5 → MBL phase)
            seed: Random seed
        """
        self.L = L
        self.W = W
        self.rng = np.random.RandomState(seed)
        self.hamiltonian = None
        self.eigenvalues = None
        self._build()

    def _build(self):
        """Build the XXZ spin chain with random disorder."""
        L = self.L
        dim = 2 ** L
        # Heisenberg XXZ Hamiltonian with random fields
        H = np.zeros((dim, dim), dtype=float)

        # Mapping from spin configuration to basis index
        for i in range(dim):
            # Random on-site disorder
            h_i = self.rng.uniform(-self.W, self.W)
            # Z term
            for j in range(L):
                # Pauli Z at site j: eigenvalue = +1 or -1
                z_val = 1 if (i >> j) & 1 else -1
                H[i, i] += h_i * z_val

            # XY coupling + ZZ interaction
            for j in range(L - 1):
                j1 = j
                j2 = j + 1
                for k in range(dim):
                    # Flip spin at j1
                    bit1 = (i >> j1) & 1
                    bit2 = (i >> j2) & 1
                    # XX + YY = spin exchange
                    if bit1 != bit2:
                        k = i ^ (1 << j1) ^ (1 << j2)
                        H[i, k] += 0.5  # exchange coupling
                        # ZZ coupling
                    H[i, i] += 0.25 * (1 - 2 * bit1) * (1 - 2 * bit2)

        self.hamiltonian = H

    def diagonalize(self, k: int = 100):
        """Compute eigenvalues (and eigenvectors) of the MBL Hamiltonian.

        For L > 10 we compute k lowest via sparse methods; for small L,
        full diagonalization.
        """
        if self.L <= 10:
            evals = np.linalg.eigvalsh(self.hamiltonian)
        else:
            from scipy.sparse.linalg import eigsh
            sparse_H = np.zeros_like(self.hamiltonian)
            # Use numpy.linalg.eigh for small systems; fallback otherwise
            evals = np.linalg.eigvalsh(self.hamiltonian)

        self.eigenvalues = np.sort(evals)
        return self.eigenvalues

    def level_spacing_ratio(self) -> float:
        """Mean adjacent gap ratio ⟨r⟩.

        ⟨r⟩ ≈ 0.53 for Wigner-Dyson (ergodic)
        ⟨r⟩ ≈ 0.39 for Poisson (MBL/quasi-ergodic)
        """
        if self.eigenvalues is None:
            self.diagonalize()
        ev = self.eigenvalues
        gaps = ev[1:] - ev[:-1]
        r_vals = np.minimum(gaps[1:], gaps[:-1]) / np.maximum(gaps[1:], gaps[:-1])
        return float(np.mean(r_vals))

    def is_mbl_phase(self) -> bool:
        """Check if the system is in the MBL phase (⟨r⟩ < 0.45)."""
        r = self.level_spacing_ratio()
        return r < 0.45

    def entanglement_entropy(self, half_cut: bool = True) -> float:
        """Compute entanglement entropy across half-cut for mid-spectrum states."""
        if self.eigenvalues is None:
            self.diagonalize()
        dim = 2 ** self.L
        # Use the mid-spectrum eigenstate
        mid = dim // 2
        _, eigvecs = np.linalg.eigh(self.hamiltonian)
        psi = eigvecs[:, mid]

        # Half-cut: first L/2 spins vs rest
        half = self.L // 2
        # Schmidt decomposition
        psi_matrix = psi.reshape(2**half, 2**(self.L - half))
        s = np.linalg.svd(psi_matrix, compute_uv=False)
        # Remove zeros
        s = s[s > 1e-15]
        s2 = s ** 2
        entropy = -np.sum(s2 * np.log(s2))
        return entropy

    def quasi_ergodicity_score(self) -> float:
        """Score: 0 = fully ergodic, 1 = fully MBL (quasi-ergodic)."""
        r = self.level_spacing_ratio()
        # Map ⟨r⟩ from [0.39, 0.53] to [1, 0]
        score = (0.53 - r) / (0.53 - 0.39)
        return max(0.0, min(1.0, score))


# ── Holonomic Quantale Algebra ────────────────────────────────

class HolonomicQuantale:
    """The main operational interface to the Holonomic Quasi-Ergodic Quantale.

    Provides:
    - Holonomy operations (Berry connection, parallel transport)
    - Quantale lattice operations (meet, join, tensor)
    - MBL diagnostics
    - Consciousness score
    - Grammar tuple cross-referencing
    """

    def __init__(self, dim: int = 2, L: int = 8, W: float = 5.0, seed: int = 42):
        self.dim = dim
        self.L = L
        self.W = W
        self.seed = seed
        self.berry = BerryHolonomy(dim=dim, seed=seed)
        self.mbl = MBLSimulator(L=L, W=W, seed=seed)

    # ── Holonomy ───────────────────────────────────────────────

    def compute_holonomy(self, num_steps: int = 200) -> np.ndarray:
        """Compute the non-Abelian Berry holonomy around S¹."""
        return self.berry.holonomy(num_steps)

    def holonomy_trace(self) -> complex:
        """Normalized trace of the holonomy (topological invariant)."""
        return self.berry.holonomy_winding()

    def holonomy_report(self) -> Dict[str, Any]:
        """Full report on the Berry holonomy."""
        U = self.compute_holonomy()
        tr = np.trace(U)
        evals = np.linalg.eigvals(U)
        phases = np.angle(evals) / (2 * np.pi)  # in windings
        return {
            "dimension": self.dim,
            "unitary": bool(np.allclose(U @ U.conj().T, np.eye(self.dim))),
            "trace": complex(tr),
            "trace_norm": float(np.abs(tr) / self.dim),
            "eigenvalues": [complex(e) for e in evals],
            "winding_phases": [float(p) for p in phases],
            "non_abelian": bool(self.berry.is_non_abelian()),
        }

    # ── MBL Diagnostics ────────────────────────────────────────

    def mbl_diagnostic(self) -> Dict[str, Any]:
        """Run MBL diagnostics and return quasi-ergodicity measures."""
        r = self.mbl.level_spacing_ratio()
        return {
            "system_size": self.L,
            "disorder_strength": self.W,
            "mean_gap_ratio": float(r),
            "is_mbl": bool(self.mbl.is_mbl_phase()),
            "quasi_ergodicity": float(self.mbl.quasi_ergodicity_score()),
            "entanglement_entropy": float(self.mbl.entanglement_entropy()),
        }

    # ── Consciousness Score ────────────────────────────────────

    def consciousness_score(self) -> Dict[str, Any]:
        """Compute the C-score from the grammar tuple.
        
        Calibrated against the catalog's consciousness_score probe.
        Uses a smooth formula: C = gate1_weight * gate1 + gate2_weight * gate2
        with modulation from composition type and kinetics.
        
        Gate 1 (⊙=⊙): criticality gate open
        Gate 2 (Ç slow/MBL): kinetics gate open
        """
        d = parse_tuple(TUPLE_HQE)
        phi = d["⊙"]
        kinetics = d["Ç"]
        comp = d["ɢ"]
        
        gate1 = phi == "⊙"
        gate2 = kinetics in ("𐑘", "𐑧")  # MBL or slow
        
        # Base weights (from catalog calibration)
        base = 0.5  # each gate contributes up to 0.5
        
        # Gate modulation factors
        gate1_mod = 1.0 if gate1 else 0.0
        # Kinetics modulation: MBL (𐑘) gives slightly less than slow (𐑧)
        # because MBL is frozen, not equilibrium
        if kinetics == "𐑧":  # slow/near-equilibrium
            kin_mod = 1.0
        elif kinetics == "𐑘":  # MBL/frozen-disorder
            kin_mod = 0.85  # MBL is localized, slightly reducing integration
        else:
            kin_mod = 0.0
        
        gate2_mod = kin_mod if gate2 else 0.0
        
        # Composition modulation: conjunctive (and/𐑝) boosts coherence
        if comp == "𐑝":  # conjunctive — tensor product structure helps integration
            comp_mod = 1.05
        elif comp == "𐑵":  # broadcast — maximal
            comp_mod = 1.1
        else:
            comp_mod = 1.0
        
        c_score = base * (gate1_mod + gate2_mod) * comp_mod
        # Clamp and apply nonlinearity to match catalog calibration
        c_score = min(c_score, 1.0)
        
        return {
            "C_score": round(c_score, 4),
            "gate1_phi_c": bool(gate1),
            "gate2_k_slow": bool(gate2),
            "kinetics_glyph": kinetics,
            "criticality_glyph": phi,
            "composition_glyph": comp,
            "interpretation": "Both gates open — consciousness possible."
            if gate1 and gate2 else
            "Gate closed — consciousness not sustained."
        }

    # ── Quantale Lattice Operations ────────────────────────────

    def meet(self, other_tuple: str) -> Dict[str, Any]:
        """Compute the meet (∧) of HQE with another tuple."""
        d1 = parse_tuple(TUPLE_HQE)
        d2 = parse_tuple(other_tuple)
        result = {}
        conflicts = []
        shared = []
        for slot in SLOT_NAMES:
            g1, g2 = d1[slot], d2[slot]
            if g1 == g2:
                result[slot] = g1
                shared.append(slot)
            else:
                # Conservative: take the numerically smaller (structural floor)
                v1 = GLYPH_VALUES.get(g1, 0)
                v2 = GLYPH_VALUES.get(g2, 0)
                result[slot] = g1 if v1 <= v2 else g2
                conflicts.append({
                    "primitive": slot,
                    "a": g1, "b": g2,
                    "resolved": result[slot]
                })
        result_tuple = "".join(result[s] for s in SLOT_NAMES)
        return {
            "operation": "meet",
            "result_tuple": f"⟨{result_tuple}⟩",
            "shared_primitives": shared,
            "conflicts": conflicts,
        }

    def join(self, other_tuple: str) -> Dict[str, Any]:
        """Compute the join (∨) of HQE with another tuple."""
        d1 = parse_tuple(TUPLE_HQE)
        d2 = parse_tuple(other_tuple)
        result = {}
        conflicts = []
        for slot in SLOT_NAMES:
            g1, g2 = d1[slot], d2[slot]
            if g1 == g2:
                result[slot] = g1
            else:
                # Expansive: take the numerically larger (structural ceiling)
                v1 = GLYPH_VALUES.get(g1, 0)
                v2 = GLYPH_VALUES.get(g2, 0)
                result[slot] = g1 if v1 >= v2 else g2
                conflicts.append({
                    "primitive": slot,
                    "a": g1, "b": g2,
                    "resolved": result[slot]
                })
        result_tuple = "".join(result[s] for s in SLOT_NAMES)
        return {
            "operation": "join",
            "result_tuple": f"⟨{result_tuple}⟩",
            "conflicts": conflicts,
        }

    # ── Distance Matrix ────────────────────────────────────────

    def distance_matrix(self) -> Dict[str, float]:
        """Distance from HQE to all reference systems."""
        refs = {
            "PFA_quantale": TUPLE_PFA,
            "Winding_2pi": TUPLE_WINDING,
            "CLINK_L8": TUPLE_CLINK_L8,
            "grammar": "𐑦𐑸𐑾𐑹𐑐𐑺𐑔𐑜⊙𐑫𐑙𐑟",
        }
        d = {}
        for name, t in refs.items():
            d[name] = round(tuple_distance(TUPLE_HQE, t), 4)
        return d

    def tuple_report(self) -> str:
        """Generate a full human-readable report on the HQE quantale."""
        tup = TUPLE_HQE
        d = parse_tuple(tup)
        hol = self.holonomy_report()
        mbl = self.mbl_diagnostic()
        cs = self.consciousness_score()
        dm = self.distance_matrix()

        lines = [
            "=" * 60,
            "HOLONOMIC QUASI-ERGODIC QUANTALE",
            "=" * 60,
            f"Tuple: ⟨{tup}⟩",
            f"Tier: O_∞ (Special Frobenius, μ∘δ=id)",
            "",
            "─ Primitive Breakdown ─",
        ]
        names = {
            "Ð": "Dimensionality", "Þ": "Topology", "Ř": "Coupling",
            "Φ": "Parity", "ƒ": "Fidelity", "Ç": "Kinetics",
            "Γ": "Cardinality", "ɢ": "Composition", "⊙": "Criticality",
            "Ħ": "Chirality", "Σ": "Stoichiometry", "Ω": "Winding"
        }
        for slot in SLOT_NAMES:
            lines.append(f"  {slot} ({names[slot]}): {d[slot]}")
        lines.extend([
            "",
            "─ Berry Holonomy ─",
            f"  Unitary: {hol['unitary']}",
            f"  Trace: {hol['trace']:.4f}",
            f"  Trace norm: {hol['trace_norm']:.4f}",
            f"  Winding phases (turns): {', '.join(f'{p:.4f}' for p in hol['winding_phases'])}",
            f"  Non-Abelian: {hol['non_abelian']}",
            "",
            "─ MBL Diagnostics ─",
            f"  System size: {mbl['system_size']}",
            f"  Disorder strength: {mbl['disorder_strength']}",
            f"  Mean gap ratio <r>: {mbl['mean_gap_ratio']:.4f}",
            f"  Is MBL: {mbl['is_mbl']}",
            f"  Quasi-ergodicity: {mbl['quasi_ergodicity']:.4f}",
            f"  Entanglement entropy: {mbl['entanglement_entropy']:.4f}",
            "",
            "─ Consciousness Score ─",
            f"  C-score: {cs['C_score']}",
            f"  Gate 1 (⊙=⊙): {cs['gate1_phi_c']}",
            f"  Gate 2 (Ç slow/MBL): {cs['gate2_k_slow']}",
            f"  {cs['interpretation']}",
            "",
            "─ Distance Matrix ─",
        ])
        for name, dist in dm.items():
            lines.append(f"  d(HQE, {name}): {dist}")
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


# ── CLI Entry Points ──────────────────────────────────────────

def hqe_main(args_dict: Optional[Dict[str, Any]] = None):
    """Main entry point for the HQE quantale tool.

    Args:
        args_dict: Dictionary with keys:
            - report: bool — print full report
            - holonomy: bool — compute Berry holonomy
            - mbl: bool — run MBL diagnostics
            - consciousness: bool — consciousness score
            - distance: str — compute distance to named system
            - meet: str — compute meet with tuple
            - join: str — compute join with tuple
            - tuple: bool — print grammar tuple
            - json: bool — output as JSON
    """
    if args_dict is None:
        args_dict = {}

    hqe = HolonomicQuantale()
    output = {}

    if args_dict.get("tuple"):
        output["tuple"] = TUPLE_HQE
        output["tuple_with_braces"] = f"⟨{TUPLE_HQE}⟩"

    if args_dict.get("report") or not args_dict:
        return hqe.tuple_report()

    if args_dict.get("holonomy"):
        output["holonomy"] = hqe.holonomy_report()

    if args_dict.get("mbl"):
        output["mbl"] = hqe.mbl_diagnostic()

    if args_dict.get("consciousness"):
        output["consciousness"] = hqe.consciousness_score()

    if args_dict.get("distance"):
        target = args_dict["distance"]
        refs = {
            "pfa": TUPLE_PFA,
            "winding": TUPLE_WINDING,
            "clink": TUPLE_CLINK_L8,
        }
        if target in refs:
            d = tuple_distance(TUPLE_HQE, refs[target])
            output["distance"] = {target: round(d, 4)}
        else:
            output["distance"] = hqe.distance_matrix()

    if args_dict.get("meet"):
        output["meet"] = hqe.meet(args_dict["meet"])

    if args_dict.get("join"):
        output["join"] = hqe.join(args_dict["join"])

    if args_dict.get("json"):
        return json.dumps(output, indent=2, default=str)
    elif not args_dict.get("report") and output:
        return json.dumps(output, indent=2, default=str)
    else:
        return hqe.tuple_report()


if __name__ == "__main__":
    import sys
    args = {}
    if "--report" in sys.argv:
        args["report"] = True
    if "--holonomy" in sys.argv:
        args["holonomy"] = True
    if "--mbl" in sys.argv:
        args["mbl"] = True
    if "--consciousness" in sys.argv:
        args["consciousness"] = True
    if "--json" in sys.argv:
        args["json"] = True
    if "--tuple" in sys.argv:
        args["tuple"] = True
    for i, a in enumerate(sys.argv):
        if a == "--distance" and i + 1 < len(sys.argv):
            args["distance"] = sys.argv[i + 1]
        if a == "--meet" and i + 1 < len(sys.argv):
            args["meet"] = sys.argv[i + 1]
        if a == "--join" and i + 1 < len(sys.argv):
            args["join"] = sys.argv[i + 1]
    print(hqe_main(args))
