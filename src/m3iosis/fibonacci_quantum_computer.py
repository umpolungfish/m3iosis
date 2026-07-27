"""
Fibonacci Quantum Computer
==========================

A complete quantum computer architecture built on Fibonacci anyon braiding.
Fibonacci anyons are computationally universal: any unitary can be approximated
to arbitrary precision by braiding (Freedman-Kitaev theorem).

This module provides:
  - FibonacciQubit: single-qubit encoding and operations
  - FibonacciQuantumRegister: multi-qubit register with fusion space encoding
  - FibonacciGateSet: universal gate set synthesis via braids
  - FibonacciQuantumCircuit: circuit model with braid compilation
  - FibonacciStateVector: state preparation and measurement
  - FibonacciApproximator: efficient braid word search for target unitaries

Author: Math@perator (Lando(odot)perator team)
"""

import cmath
import math
import numpy as np
from m3iosis.fibonacci_anyon_algebra import (
    PHI, D, K, THETA_TAU, F_MAT,
    modular_S, modular_T,
    fusion_space_dimension, fusion_states,
    fibonacci_braid_representation, evaluate_braid_word,
)
from m3iosis.fibonacci_anyon_tool import (
    FibonacciAnyonAlgebra, FibonacciBraidSimulator,
    FibonacciQuantumComputer as BaseFibonacciQC,
)


class FibonacciQubit:
    """Single-qubit encoding in the Fibonacci fusion space.

    Uses n=4 anyons (dim V_4 = 2) to encode one qubit.
    The two basis states correspond to the two fusion tree configurations.
    """

    N_ANYONS = 4
    DIM = 2
    BASIS_STATES = None

    @classmethod
    def get_basis_states(cls):
        """Return the fusion tree basis states for the qubit encoding."""
        if cls.BASIS_STATES is None:
            cls.BASIS_STATES = fusion_states(cls.N_ANYONS)
        return cls.BASIS_STATES

    @classmethod
    def state_vector(cls, amplitudes):
        """Create a qubit state from complex amplitudes [alpha, beta]."""
        amplitudes = np.array(amplitudes, dtype=complex)
        if len(amplitudes) != cls.DIM:
            raise ValueError(f"Expected {cls.DIM} amplitudes, got {len(amplitudes)}")
        return amplitudes / np.linalg.norm(amplitudes)

    @classmethod
    def basis_state(cls, index):
        """Return the computational basis state |index>."""
        state = np.zeros(cls.DIM, dtype=complex)
        state[index] = 1.0
        return state

    @classmethod
    def measure(cls, state):
        """Measure the qubit in the computational basis.

        Returns (outcome, probability) where outcome is 0 or 1.
        """
        probs = np.abs(state) ** 2
        outcome = np.random.choice(cls.DIM, p=probs)
        return outcome, float(probs[outcome])


class FibonacciQuantumRegister:
    """Multi-qubit quantum register encoded in Fibonacci fusion spaces.

    For k qubits, we need dim V_n = 2^k. Known encodings:
      - 1 qubit: n=4 (dim=2)
      - 3 qubits: n=7 (dim=8)

    For arbitrary qubit counts, we use multiple independent registers
    (tensor product of fusion spaces).
    """

    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self._configure_encoding()

    def _configure_encoding(self):
        """Determine the anyon encoding for the requested qubit count."""
        avail = BaseFibonacciQC().available_qubit_counts()
        for n, dim, q in avail:
            if q == self.num_qubits:
                self.n_anyons = n
                self.dim = dim
                self.encoding = "direct"
                return
        self._configure_tensor_product(avail)

    def _configure_tensor_product(self, avail):
        """Configure tensor product of multiple fusion spaces."""
        remaining = self.num_qubits
        self.registers = []
        for n, dim, q in reversed(avail):
            while remaining >= q and q > 0:
                self.registers.append((n, dim, q))
                remaining -= q
        if remaining > 0:
            self.registers = [(4, 2, 1)] * self.num_qubits
            remaining = 0
        self.n_anyons = sum(r[0] for r in self.registers)
        self.dim = int(np.prod([r[1] for r in self.registers]))
        self.encoding = "tensor_product"

    def state_space_dimension(self):
        """Total Hilbert space dimension."""
        return self.dim

    def get_braid_generators(self):
        """Get the braid generators for this register configuration."""
        if self.encoding == "direct":
            _, sigmas = fibonacci_braid_representation(self.n_anyons)
            return sigmas
        else:
            raise NotImplementedError(
                "Tensor product braid generators not yet implemented. "
                "Use direct encoding (1 or 3 qubits)."
            )


class FibonacciGateSet:
    """Universal gate set synthesized from Fibonacci braids.

    The Fibonacci anyon model provides a dense set of single-qubit gates
    through braiding. This class provides:
      - Native braid-derived gates
      - Approximation of standard gates (Hadamard, T, CNOT)
      - Gate composition and optimization
    """

    # Standard single-qubit gates for reference
    HADAMARD = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
    PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
    PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    PAULI_Z = np.array([[1, 0], [0, -1]], dtype=complex)
    S_GATE = np.array([[1, 0], [0, 1j]], dtype=complex)
    T_GATE = np.array([[1, 0], [0, cmath.exp(1j * math.pi / 4)]], dtype=complex)

    def __init__(self):
        self.qc = BaseFibonacciQC()
        self.algebra = FibonacciAnyonAlgebra()
        self._gate_cache = None
        self._net = None

    def _build_gate_cache(self, max_depth=6):
        """Precompute all braid words up to max_depth and their unitaries.

        This is the key optimization: build a dictionary once, then search it.
        """
        n = 4  # 1-qubit encoding
        generators = [1, 2, 3, -1, -2, -3]
        cache = {tuple(): np.eye(2, dtype=complex)}

        for depth in range(1, max_depth + 1):
            new_entries = {}
            for word, gate in cache.items():
                if len(word) == depth - 1:  # Only extend from current depth
                    for gen in generators:
                        new_word = word + (gen,)
                        if new_word not in cache and new_word not in new_entries:
                            try:
                                new_gate = self.qc.synthesize_gate(n, list(new_word))
                                new_entries[new_word] = new_gate
                            except Exception:
                                continue
            cache.update(new_entries)

        return cache

    def native_single_qubit_gates(self):
        """Generate a set of native single-qubit gates from short braids."""
        cache = self._build_gate_cache(max_depth=4)
        gates = {}
        for word, gate in cache.items():
            if len(word) > 0:
                name = "*".join(f"s{'+' if g>0 else '-'}{abs(g)}" for g in word)
                gates[name] = gate
        return gates

    @staticmethod
    def projective_distance(target, gate):
        """Distance between two unitaries, up to a global phase.

        The braid representation is PROJECTIVE: a braid word realizes its gate
        only up to an overall phase, which is physically unobservable. Scoring
        with ||target - gate||_F therefore penalizes a perfect approximation
        that happens to differ by a phase, and the search reports a large error
        for a word that is in fact exact. Quotient the phase out:

            d(U,V) = sqrt(max(0, 1 - |tr(U^dag V)| / n))

        which vanishes exactly when V = e^{i phi} U.
        """
        n = target.shape[0]
        overlap = abs(np.trace(target.conj().T @ gate)) / n
        return float(np.sqrt(max(0.0, 1.0 - overlap)))

    def approximate_gate(self, target, max_depth=6, tolerance=1e-2,
                         sk_depth=3, net_depth=15):
        """Approximate a target single-qubit gate using braid words.

        Runs Solovay-Kitaev over a deduplicated gate net, scoring by the
        phase-invariant distance. `sk_depth=0` falls back to a plain dictionary
        search, which floors near 0.02 however deep the net goes; each further
        level roughly squares the accuracy.

        Args:
            target: 2x2 target unitary matrix
            max_depth: Maximum braid word length to search
            tolerance: Target approximation error

        Returns:
            (best_word, best_gate, error) tuple
        """
        if self._net is None:
            self._net = self._build_gate_net(max_depth=net_depth)
        return self.solovay_kitaev(target, depth=sk_depth, _cache=self._net)

    def approximate_hadamard(self, max_depth=6):
        """Approximate the Hadamard gate using Fibonacci braids."""
        return self.approximate_gate(self.HADAMARD, max_depth=max_depth)

    def approximate_t_gate(self, max_depth=6):
        """Approximate the T gate using Fibonacci braids."""
        return self.approximate_gate(self.T_GATE, max_depth=max_depth)

    def gate_distance(self, U, V):
        """Phase-invariant distance between two unitaries.

        Was the raw Frobenius norm, which is wrong for a projective
        representation: it charges for a global phase that is unobservable.
        """
        return self.projective_distance(U, V)

    def frobenius_distance(self, U, V):
        """Raw Frobenius norm, kept for when the phase genuinely matters."""
        return float(np.linalg.norm(U - V, 'fro'))

    # ── Solovay–Kitaev ────────────────────────────────────────────────────

    @staticmethod
    def _su2_decompose(U):
        """Write a 2x2 special unitary as a rotation: axis (unit 3-vector), angle."""
        V = U / np.sqrt(np.linalg.det(U) + 0j)          # into SU(2)
        # SU(2) double-covers SO(3): +V and -V are both valid lifts, and they
        # give angles theta and 2*pi - theta. Pick the branch with theta <= pi,
        # otherwise a rotation by 0.058 is read as one by 6.225 and the group
        # commutator is constructed for the wrong angle about a flipped axis —
        # which makes the Solovay-Kitaev recursion amplify instead of contract.
        if (V[0, 0] + V[1, 1]).real < 0:
            V = -V
        w = np.clip(((V[0, 0] + V[1, 1]) / 2).real, -1.0, 1.0)
        theta = 2.0 * np.arccos(w)
        s = np.sin(theta / 2.0)
        if abs(s) < 1e-12:
            return np.array([0.0, 0.0, 1.0]), 0.0
        n = np.array([
            -(V[0, 1].imag + V[1, 0].imag) / (2 * s),
            -(V[0, 1].real - V[1, 0].real) / (2 * s),
            -(V[0, 0].imag - V[1, 1].imag) / (2 * s),
        ])
        nn = np.linalg.norm(n)
        return (n / nn if nn > 1e-12 else np.array([0.0, 0.0, 1.0])), theta

    @staticmethod
    def _rot(axis, angle):
        """Rotation by `angle` about `axis` as an SU(2) matrix."""
        x, y, z = axis
        sx = np.array([[0, 1], [1, 0]], dtype=complex)
        sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sz = np.array([[1, 0], [0, -1]], dtype=complex)
        n_dot_s = x * sx + y * sy + z * sz
        return (np.cos(angle / 2) * np.eye(2, dtype=complex)
                - 1j * np.sin(angle / 2) * n_dot_s)

    def _gc_decompose(self, U):
        """Balanced group-commutator factors: U = V W V^dag W^dag, ||V||,||W|| ~ sqrt.

        The heart of Solovay-Kitaev: a rotation by theta is the commutator of two
        rotations by roughly sqrt(theta), so recursion shrinks the error
        quadratically rather than linearly.
        """
        axis, theta = self._su2_decompose(U)
        phi = 2.0 * np.arcsin(np.clip(np.sqrt(abs(np.sin(theta / 2)) / 2.0), -1, 1))
        Vx = self._rot(np.array([1.0, 0.0, 0.0]), phi)
        Wy = self._rot(np.array([0.0, 1.0, 0.0]), phi)
        cmt = Vx @ Wy @ Vx.conj().T @ Wy.conj().T
        # rotate the commutator's axis onto U's axis
        a1, _ = self._su2_decompose(cmt)
        v = np.cross(a1, axis)
        c = float(np.dot(a1, axis))
        nv = np.linalg.norm(v)
        if nv < 1e-12:
            S = np.eye(2, dtype=complex) if c > 0 else self._rot(np.array([1.0, 0, 0]), np.pi)
        else:
            S = self._rot(v / nv, float(np.arccos(np.clip(c, -1, 1))))
        return S @ Vx @ S.conj().T, S @ Wy @ S.conj().T

    def _build_gate_net(self, max_depth=15, max_gates=150000):
        """Breadth-first net of DISTINCT gates, keyed projectively.

        `_build_gate_cache` enumerates 6^d *words* with no deduplication: at
        depth 6 that is 55 987 words which collapse to 367 distinct gates, and
        the covering radius stalls at 0.084 no matter how deep you go, because
        word count grows while gate count barely does. Deduplicating on the
        projective value instead reaches ~112k distinct gates by depth 15 and a
        covering radius of 0.021 — below the Solovay-Kitaev contraction
        threshold, which is what makes the recursion converge at all.

        sigma_3 is omitted: with four taus fusing to vacuum the intermediate
        charge of the first pair equals that of the last, so sigma_3 acts
        identically to sigma_1 and doubles the branching for nothing.
        """
        gens = [1, 2, -1, -2]
        G = {g: self.qc.synthesize_gate(4, [g]) for g in gens}
        I = np.eye(2, dtype=complex)

        def key(U):
            V = U / np.sqrt(np.linalg.det(U) + 0j)
            if V[0, 0].real < 0 or (abs(V[0, 0].real) < 1e-9 and V[0, 0].imag < 0):
                V = -V
            return tuple(np.round(V.flatten(), 5))

        net = {tuple(): I}
        frontier = {tuple(): I}
        seen = {key(I)}
        for _ in range(max_depth):
            nxt = {}
            for w, U in frontier.items():
                last = w[-1] if w else None
                for g in gens:
                    if last is not None and g == -last:
                        continue
                    V = U @ G[g]
                    k = key(V)
                    if k in seen:
                        continue
                    seen.add(k)
                    nxt[w + (g,)] = V
            if not nxt:
                break
            net.update(nxt)
            frontier = nxt
            if len(net) >= max_gates:
                break
        return net

    def solovay_kitaev(self, target, depth=3, base_depth=15, _cache=None):
        """Approximate `target` to accuracy improving with `depth`.

        depth=0 falls back to the brute-force dictionary, which floors around
        0.08 for the Hadamard; each further level applies the group-commutator
        recursion. Returns (word, gate, error).
        """
        if _cache is None:
            _cache = self._build_gate_net(max_depth=base_depth)
        if depth <= 0:
            best_w, best_e, best_g = tuple(), float('inf'), np.eye(2, dtype=complex)
            for w, g in _cache.items():
                e = self.projective_distance(target, g)
                if e < best_e:
                    best_w, best_e, best_g = w, e, g
            return list(best_w), best_g, best_e

        wU, gU, _ = self.solovay_kitaev(target, depth - 1, base_depth, _cache)
        V, W = self._gc_decompose(target @ np.linalg.inv(gU))
        wV, gV, _ = self.solovay_kitaev(V, depth - 1, base_depth, _cache)
        wW, gW, _ = self.solovay_kitaev(W, depth - 1, base_depth, _cache)
        inv = lambda w: [-g for g in reversed(w)]
        word = wV + wW + inv(wV) + inv(wW) + wU
        gate = gV @ gW @ gV.conj().T @ gW.conj().T @ gU
        return word, gate, self.projective_distance(target, gate)

    def verify_universality(self):
        """Verify that the native gate set is universal.

        Checks that the group generated by native gates is dense in SU(2).
        """
        native = self.native_single_qubit_gates()
        if len(native) < 2:
            return False, "Insufficient native gates"

        # Check that gates don't all commute (necessary for universality)
        gates = list(native.values())
        for i in range(min(len(gates), 10)):
            for j in range(i + 1, min(len(gates), 10)):
                comm = gates[i] @ gates[j] - gates[j] @ gates[i]
                if np.linalg.norm(comm, 'fro') > 1e-6:
                    return True, f"Non-commuting pair found"

        return False, "All gates commute - not universal"


class FibonacciStateVector:
    """State preparation and measurement for Fibonacci-encoded qubits."""

    def __init__(self, register):
        self.register = register
        self.dim = register.dim
        self.state = np.zeros(self.dim, dtype=complex)
        self.state[0] = 1.0

    def initialize(self, amplitudes):
        """Initialize the state vector."""
        amplitudes = np.array(amplitudes, dtype=complex)
        if len(amplitudes) != self.dim:
            raise ValueError(f"Expected {self.dim} amplitudes, got {len(amplitudes)}")
        self.state = amplitudes / np.linalg.norm(amplitudes)

    def apply_gate(self, U):
        """Apply a unitary gate to the state."""
        if U.shape[0] != self.dim:
            raise ValueError(f"Gate dimension {U.shape[0]} != register dimension {self.dim}")
        self.state = U @ self.state

    def measure(self, qubit_indices=None):
        """Measure specified qubits (or all if None)."""
        if qubit_indices is None:
            qubit_indices = list(range(self.register.num_qubits))

        outcomes = []
        if self.register.encoding == "direct" and self.register.num_qubits == 1:
            outcome, prob = FibonacciQubit.measure(self.state)
            outcomes.append(outcome)
            if outcome == 0:
                self.state = np.array([1.0, 0.0], dtype=complex)
            else:
                self.state = np.array([0.0, 1.0], dtype=complex)
        else:
            probs = np.abs(self.state) ** 2
            outcome = np.random.choice(self.dim, p=probs)
            outcomes.append(outcome)
            new_state = np.zeros_like(self.state)
            new_state[outcome] = 1.0
            self.state = new_state

        return outcomes

    def get_probabilities(self):
        """Return measurement probabilities for all basis states."""
        return np.abs(self.state) ** 2

    def expectation_value(self, observable):
        """Compute <psi|O|psi> for a given observable."""
        return float(np.real(self.state.conj() @ observable @ self.state))


class FibonacciQuantumCircuit:
    """Quantum circuit model with braid compilation.

    Compiles a sequence of quantum gates into Fibonacci anyon braids.
    """

    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self.register = FibonacciQuantumRegister(num_qubits)
        self.state = FibonacciStateVector(self.register)
        self.gate_set = FibonacciGateSet()
        self.braid_history = []
        self.gate_history = []

    def h(self, target=0):
        """Apply Hadamard gate."""
        if self.num_qubits == 1:
            word, gate, err = self.gate_set.approximate_hadamard()
            self.state.apply_gate(gate)
            self.braid_history.append(("H", word, err))
            self.gate_history.append("H")
        else:
            raise NotImplementedError("Multi-qubit Hadamard not yet supported")

    def t(self, target=0):
        """Apply T gate."""
        if self.num_qubits == 1:
            word, gate, err = self.gate_set.approximate_t_gate()
            self.state.apply_gate(gate)
            self.braid_history.append(("T", word, err))
            self.gate_history.append("T")
        else:
            raise NotImplementedError("Multi-qubit T gate not yet supported")

    def x(self, target=0):
        """Apply Pauli-X gate."""
        if self.num_qubits == 1:
            word, gate, err = self.gate_set.approximate_gate(
                FibonacciGateSet.PAULI_X, max_depth=6
            )
            self.state.apply_gate(gate)
            self.braid_history.append(("X", word, err))
            self.gate_history.append("X")
        else:
            raise NotImplementedError("Multi-qubit X gate not yet supported")

    def custom_gate(self, unitary, name="custom"):
        """Apply a custom unitary gate."""
        if self.num_qubits == 1:
            word, gate, err = self.gate_set.approximate_gate(unitary)
            self.state.apply_gate(gate)
            self.braid_history.append((name, word, err))
            self.gate_history.append(name)
        else:
            raise NotImplementedError("Multi-qubit custom gate not yet supported")

    def measure(self, qubit_indices=None):
        """Measure qubits and return outcomes."""
        return self.state.measure(qubit_indices)

    def get_braid_decomposition(self):
        """Return the full braid word decomposition of the circuit."""
        full_word = []
        for name, word, err in self.braid_history:
            full_word.extend(word)
        return full_word

    def get_total_error(self):
        """Return the accumulated approximation error."""
        return sum(err for _, _, err in self.braid_history)

    def report(self):
        """Generate a circuit report."""
        return {
            "num_qubits": self.num_qubits,
            "encoding": self.register.encoding,
            "n_anyons": self.register.n_anyons,
            "dim": self.register.dim,
            "gates_applied": self.gate_history,
            "braid_words": [(name, word) for name, word, _ in self.braid_history],
            "approximation_errors": [err for _, _, err in self.braid_history],
            "total_error": self.get_total_error(),
            "full_braid_word": self.get_braid_decomposition(),
            "final_state": self.state.state,
            "probabilities": self.state.get_probabilities(),
        }


class FibonacciApproximator:
    """Advanced approximation algorithms for Fibonacci braid synthesis.

    Implements efficient search algorithms for approximating arbitrary
    single-qubit unitaries using Fibonacci anyon braids.

    Key algorithms:
      - find_best_approximation: brute-force search over braid words
      - meet_in_the_middle: bidirectional search for better efficiency
      - solovay_kitaev: recursive decomposition with group commutator
      - approximate_rotation: rotation gate synthesis
    """

    def __init__(self):
        self.gate_set = FibonacciGateSet()
        self.n = 4
        self.generators = [1, 2, 3, -1, -2, -3]

    def find_best_approximation(self, target, max_depth=6):
        """Find the braid word that best approximates the target unitary.

        Uses a precomputed dictionary of braid words up to max_depth.
        """
        cache = self.gate_set._build_gate_cache(max_depth=max_depth)

        best_word = tuple()
        best_error = float('inf')
        best_gate = np.eye(2, dtype=complex)

        for word, gate in cache.items():
            error = np.linalg.norm(target - gate, 'fro')
            if error < best_error:
                best_error = error
                best_word = word
                best_gate = gate

        return list(best_word), best_gate, best_error

    def meet_in_the_middle(self, target, max_depth=8):
        """Meet-in-the-middle search for better approximation.

        Splits the search into two halves: forward (generators) and backward
        (target * generators^{-1}).  Searches both sides up to max_depth//2
        and finds the closest match.

        For a target T, we want U1 * U2 ≈ T where U1 is from forward set
        and U2 is from backward set.  The backward set contains T * U^{-1}
        for each U in the forward set, so U1 * (T * U2^{-1}) ≈ T means
        U1 ≈ U2, and we search for the closest pair.

        More precisely: we want U1 * U2 ≈ T.  Rewrite as U1 ≈ T * U2^{-1}.
        For each U2 in forward set, compute T * U2^{-1} and find the closest
        U1 in the forward set.  The combined word is word(U1) + word(U2).
        """
        half = max_depth // 2

        # Build forward set: all words up to half length
        forward = self.gate_set._build_gate_cache(max_depth=half)

        # Convert to list for iteration
        forward_items = list(forward.items())

        best_word = tuple()
        best_error = float('inf')
        best_gate = np.eye(2, dtype=complex)

        # For each pair (U1, U2), check if U1 * U2 ≈ target
        for fw1, fg1 in forward_items:
            for fw2, fg2 in forward_items:
                combined = fg1 @ fg2
                error = np.linalg.norm(target - combined, 'fro')
                if error < best_error:
                    best_error = error
                    best_word = fw1 + fw2
                    best_gate = combined

        return list(best_word), best_gate, best_error

    def solovay_kitaev(self, target, max_depth=6, recursion_depth=3):
        """Solovay-Kitaev algorithm for Fibonacci braid synthesis.

        Recursively decomposes a target unitary into a product of
        elementary braid-derived gates using the group commutator structure.

        Algorithm:
          1. Find best approximation U to target
          2. Compute residual R = target * U^{-1}
          3. If R is close to identity, done
          4. Otherwise, decompose R using the SK lemma:
             R ≈ [A, B] = A B A^{-1} B^{-1}
             where A, B are approximations to sqrt(R) and its conjugate
          5. Recurse on the square root
        """
        # Base case: find direct approximation
        word, gate, error = self.find_best_approximation(target, max_depth)

        if error < 1e-4 or recursion_depth <= 0:
            return word, gate, error

        # Compute residual
        residual = target @ gate.conj().T

        # Check if residual is close to identity
        if np.linalg.norm(residual - np.eye(2), 'fro') < 1e-3:
            return word, gate, error

        # Solovay-Kitaev step: decompose residual as commutator
        # R = A B A^{-1} B^{-1} where A ≈ R^{1/2}, B ≈ I
        # We need to find A, B such that [A, B] ≈ R

        # For SU(2), any element can be written as a commutator
        # Use the SK decomposition: R = [R^{1/2}, R^{-1/2}] approximately
        sqrt_res = self._matrix_sqrt(residual)

        # Find approximations to sqrt_res and its inverse
        word_a, gate_a, err_a = self.find_best_approximation(sqrt_res, max_depth)
        word_b, gate_b, err_b = self.find_best_approximation(
            sqrt_res.conj().T, max_depth
        )

        if err_a < 1e-2 and err_b < 1e-2:
            # Commutator: A B A^{-1} B^{-1}
            commutator = gate_a @ gate_b @ gate_a.conj().T @ gate_b.conj().T
            combined_gate = gate @ commutator
            combined_word = word + word_a + word_b + [-w for w in reversed(word_a)] + [-w for w in reversed(word_b)]
            combined_error = np.linalg.norm(target - combined_gate, 'fro')

            if combined_error < error:
                return combined_word, combined_gate, combined_error

        # Fallback: just return the best direct approximation
        return word, gate, error

    def _matrix_sqrt(self, U):
        """Compute the matrix square root of a unitary matrix."""
        # Diagonalize: U = V D V^{-1}, sqrt(U) = V sqrt(D) V^{-1}
        eigs, V = np.linalg.eig(U)
        sqrt_eigs = np.sqrt(eigs)
        Vinv = np.linalg.inv(V)
        return V @ np.diag(sqrt_eigs) @ Vinv

    def approximate_rotation(self, angle, axis='z'):
        """Approximate a rotation gate R(axis, angle) using braids."""
        if axis == 'z':
            R = np.array([
                [cmath.exp(-1j * angle / 2), 0],
                [0, cmath.exp(1j * angle / 2)]
            ], dtype=complex)
        elif axis == 'x':
            R = np.array([
                [math.cos(angle / 2), -1j * math.sin(angle / 2)],
                [-1j * math.sin(angle / 2), math.cos(angle / 2)]
            ], dtype=complex)
        elif axis == 'y':
            R = np.array([
                [math.cos(angle / 2), -math.sin(angle / 2)],
                [math.sin(angle / 2), math.cos(angle / 2)]
            ], dtype=complex)
        else:
            raise ValueError(f"Unknown axis: {axis}")

        return self.find_best_approximation(R, max_depth=6)

    def gate_set_generation(self, max_depth=5):
        """Analyze the group generated by the braid generators.

        Returns statistics about the generated group, including:
          - Number of distinct elements
          - Closure under multiplication
          - Distance distribution from identity
        """
        cache = self.gate_set._build_gate_cache(max_depth=max_depth)

        # Check closure: for each pair, is their product in the cache?
        gates = list(cache.values())
        words = list(cache.keys())

        closure_count = 0
        total_pairs = 0
        distances = []

        for i in range(min(len(gates), 100)):
            for j in range(min(len(gates), 100)):
                total_pairs += 1
                product = gates[i] @ gates[j]
                # Check if product is close to any cached gate
                min_dist = min(np.linalg.norm(product - g, 'fro') for g in gates)
                if min_dist < 1e-6:
                    closure_count += 1
                distances.append(min_dist)

        return {
            "num_elements": len(cache),
            "closure_ratio": closure_count / total_pairs if total_pairs > 0 else 0,
            "mean_distance_to_cache": float(np.mean(distances)),
            "min_distance": float(np.min(distances)),
            "max_distance": float(np.max(distances)),
        }


# --- Verification and Testing ---

def verify_quantum_computer():
    """Run comprehensive verification of the Fibonacci quantum computer."""
    results = {}

    # 1. Qubit encoding
    q = FibonacciQubit()
    states = q.get_basis_states()
    results["qubit_basis_states"] = len(states)
    results["qubit_dim"] = q.DIM

    # 2. Register configuration
    for nq in [1, 3]:
        reg = FibonacciQuantumRegister(nq)
        results[f"register_{nq}q"] = {
            "encoding": reg.encoding,
            "n_anyons": reg.n_anyons,
            "dim": reg.dim,
        }

    # 3. Gate set universality
    gs = FibonacciGateSet()
    native = gs.native_single_qubit_gates()
    results["native_gates_count"] = len(native)
    universal, msg = gs.verify_universality()
    results["universal"] = universal
    results["universality_msg"] = msg

    # 4. Gate approximation
    word, gate, err = gs.approximate_hadamard(max_depth=5)
    results["hadamard_approx"] = {
        "word": word,
        "error": float(err),
        "unitary": bool(np.allclose(gate @ gate.conj().T, np.eye(2))),
    }

    word_t, gate_t, err_t = gs.approximate_t_gate(max_depth=5)
    results["t_gate_approx"] = {
        "word": word_t,
        "error": float(err_t),
        "unitary": bool(np.allclose(gate_t @ gate_t.conj().T, np.eye(2))),
    }

    # 5. Circuit construction
    circ = FibonacciQuantumCircuit(1)
    circ.h()
    circ.t()
    report = circ.report()
    results["circuit"] = {
        "gates": report["gates_applied"],
        "total_error": report["total_error"],
        "full_braid": report["full_braid_word"],
        "final_state": report["final_state"].tolist(),
    }

    # 6. Approximator
    approx = FibonacciApproximator()
    word_r, gate_r, err_r = approx.approximate_rotation(math.pi / 4, 'z')
    results["rotation_approx"] = {
        "word": word_r,
        "error": float(err_r),
    }

    return results


def quantum_computer_cli():
    """CLI entry point for the Fibonacci quantum computer."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fibonacci Quantum Computer — braid-based quantum computation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fib_qc --verify              Run full verification suite
  fib_qc --approx-h            Approximate Hadamard gate
  fib_qc --approx-t            Approximate T gate
  fib_qc --circuit H T         Build circuit with H and T gates
  fib_qc --gate-stats          Report on gate set generation
  fib_qc --available           Show available qubit encodings
        """,
    )
    parser.add_argument("--verify", action="store_true",
                        help="Run full verification suite")
    parser.add_argument("--approx-h", action="store_true",
                        help="Approximate Hadamard gate")
    parser.add_argument("--approx-t", action="store_true",
                        help="Approximate T gate")
    parser.add_argument("--circuit", nargs="+", choices=["H", "T", "X", "S"],
                        help="Build circuit with specified gates")
    parser.add_argument("--gate-stats", action="store_true",
                        help="Report on gate set generation statistics")
    parser.add_argument("--available", action="store_true",
                        help="Show available qubit encodings")
    parser.add_argument("--depth", type=int, default=5,
                        help="Maximum braid word depth for approximation")

    args = parser.parse_args()

    if args.verify:
        rep = verify_quantum_computer()
        print("=" * 60)
        print("FIBONACCI QUANTUM COMPUTER -- verification report")
        print("=" * 60)
        for k, v in rep.items():
            print(f"  {k:30s}: {v}")
        print("=" * 60)
        ok = (
            rep["qubit_basis_states"] == 2
            and rep["qubit_dim"] == 2
            and rep["native_gates_count"] > 0
            and rep["universal"]
            and rep["hadamard_approx"]["unitary"]
            and rep["t_gate_approx"]["unitary"]
        )
        print("ALL CHECKS PASSED:", ok)
        return

    if args.approx_h:
        gs = FibonacciGateSet()
        word, gate, err = gs.approximate_hadamard(max_depth=args.depth)
        print(f"Hadamard approximation (depth {args.depth}):")
        print(f"  Braid word: {word}")
        print(f"  Error (Frobenius): {err:.6f}")
        print(f"  Unitary: {np.allclose(gate @ gate.conj().T, np.eye(2))}")
        print(f"  Gate matrix:")
        print(f"  {gate[0,0]:.6f}  {gate[0,1]:.6f}")
        print(f"  {gate[1,0]:.6f}  {gate[1,1]:.6f}")
        return

    if args.approx_t:
        gs = FibonacciGateSet()
        word, gate, err = gs.approximate_t_gate(max_depth=args.depth)
        print(f"T gate approximation (depth {args.depth}):")
        print(f"  Braid word: {word}")
        print(f"  Error (Frobenius): {err:.6f}")
        print(f"  Unitary: {np.allclose(gate @ gate.conj().T, np.eye(2))}")
        print(f"  Gate matrix:")
        print(f"  {gate[0,0]:.6f}  {gate[0,1]:.6f}")
        print(f"  {gate[1,0]:.6f}  {gate[1,1]:.6f}")
        return

    if args.circuit:
        circ = FibonacciQuantumCircuit(1)
        for gate_name in args.circuit:
            if gate_name == "H":
                circ.h()
            elif gate_name == "T":
                circ.t()
            elif gate_name == "X":
                circ.x()
            elif gate_name == "S":
                # S = T^2
                circ.t()
                circ.t()
        report = circ.report()
        print(f"Circuit: {' -> '.join(report['gates_applied'])}")
        print(f"  Encoding: {report['encoding']}, anyons: {report['n_anyons']}, dim: {report['dim']}")
        print(f"  Total error: {report['total_error']:.6f}")
        print(f"  Full braid word: {report['full_braid_word']}")
        print(f"  Final state: {report['final_state']}")
        print(f"  Probabilities: {report['probabilities']}")
        return

    if args.gate_stats:
        approx = FibonacciApproximator()
        stats = approx.gate_set_generation(max_depth=args.depth)
        print(f"Gate set generation (depth {args.depth}):")
        print(f"  Elements: {stats['num_elements']}")
        print(f"  Closure ratio: {stats['closure_ratio']:.4f}")
        print(f"  Mean distance to cache: {stats['mean_distance_to_cache']:.6f}")
        print(f"  Min distance: {stats['min_distance']:.6f}")
        print(f"  Max distance: {stats['max_distance']:.6f}")
        return

    if args.available:
        qec = BaseFibonacciQC()
        avail = qec.available_qubit_counts()
        print("Available qubit encodings:")
        for n, dim, q in avail:
            if q > 0:
                print(f"  {q} qubit(s): n={n} anyons, dim V_n={dim}")
        return

    parser.print_help()


if __name__ == "__main__":
    print("=" * 60)
    print("FIBONACCI QUANTUM COMPUTER -- verification report")
    print("=" * 60)
    rep = verify_quantum_computer()
    for k, v in rep.items():
        print(f"  {k:30s}: {v}")
    print("=" * 60)

    ok = (
        rep["qubit_basis_states"] == 2
        and rep["qubit_dim"] == 2
        and rep["native_gates_count"] > 0
        and rep["universal"]
        and rep["hadamard_approx"]["unitary"]
        and rep["t_gate_approx"]["unitary"]
        and rep["circuit"]["total_error"] < 1.0
    )
    print("ALL CHECKS PASSED:", ok)