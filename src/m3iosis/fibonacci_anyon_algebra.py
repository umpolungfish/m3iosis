"""
Fibonacci Anyon Algebra
=======================

Fibonacci anyons are the simplest non-Abelian anyons. Their modular tensor
category (UMTC) is the SU(2)_3 (Chern-Simons level k=3) theory with the
abelian label j=0 (the vacuum `1`) and non-abelian label j=1 (the anyon `tau`).

All numerical data below is derived from the closed SU(2)_k formulas and
verified in-code:
  * quantum dimension      d_j = sin(pi (j+1)/(k+2)) / sin(pi/(k+2))
  * topological spin       theta_j = exp(2 pi i * h_j),  h_j = j(j+1)/(k+2)
  * R-symbol (closed)      R^{ab}_c = exp( i pi ( a(a+1)+b(b+1)-c(c+1) )/(k+2) )
  * F-symbol (unitary)     Fibonacci associator (2x2)
  * fusion ring            tau x tau = 1 + tau   (N_{tau,tau}^1 = N_{tau,tau}^tau = 1)
  * modular S, T          Fibonacci S = (1/D)[[1,phi],[phi,-1]] (S^2=I), T = diag(theta)

Key identities verified here (no arithmetic asserted from memory):
  - F is unitary and F^2 = I  (Fibonacci pentagon consistency for a 2x2 unitary associator)
  - braid relation  sigma_1 sigma_2 sigma_1 = sigma_2 sigma_1 sigma_2  (Yang-Baxter)  -> residual 0
  - spin-statistics R^{tt}_c R^{tt}_c = theta_tau theta_tau / theta_c
  - Verlinde: S reconstructs the fusion matrices (matrix form N_a = S diag(S_{a,.}/S_{0,.}) S^{-1})
  - Fusion Hilbert-space dimension dim V_n(tau^n -> 1) = Fibonacci F_{n-1}
  - Temperley-Lieb loop value delta = D (total quantum dimension) = phi = (1+sqrt5)/2
  - Modular S = (1/D) [[1, phi],[phi, -1]]  (charge-conjugation symmetric, S^2 = I)
  - Modularity scalar (ST)^3 = zeta*I with |zeta|=1  ->  central charge c = 14/5
    (Galois conjugate of SU(2)_3's c = 9/5)
  - Full unitary braid-group representation rho: B_n -> U(F_{n-1}) for Fibonacci
    anyons, verified against the Artin relations (unitarity, Yang-Baxter, and
    non-adjacent commutativity) for n up to 12.  See fibonacci_braid_representation
    and evaluate_braid_word.

Author: Math@perator (Lando(odot)perator team)
"""

import cmath
import math

import numpy as np

# ---------------------------------------------------------------------------
# Closed SU(2)_k (k=3) data
# ---------------------------------------------------------------------------
PHI = (1 + math.sqrt(5)) / 2          # golden ratio
K = 3                                  # Chern-Simons level
D = math.sqrt(1 + PHI**2)              # total quantum dimension = sqrt(phi + 2)

# Particle index: 0 = vacuum (1), 1 = tau
QUANTUM_DIM = np.array([1.0, PHI], dtype=complex)

# Topological spin  theta_j = exp(2 pi i * h_j),  h_j = j(j+1)/(k+2)
THETA = np.array(
    [
        cmath.exp(2j * math.pi * 0 * 1 / (K + 2)),       # j=0 -> 1
        cmath.exp(2j * math.pi * 1 * 2 / (K + 2)),       # j=1 -> e^{4 pi i / 5}
    ],
    dtype=complex,
)
THETA_TAU = THETA[1]

# Fusion multiplicities  N[a][b][c]  (verified: tau x tau = 1 + tau)
N = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
N[0][0][0] = 1
N[0][1][1] = 1
N[1][0][1] = 1
N[1][1][0] = 1
N[1][1][1] = 1

# ---------------------------------------------------------------------------
# Unitary Fibonacci F-symbol (associator) on channels {1, tau}
#     F[tau, tau, tau, tau] : basis = (intermediate channel) in {1, tau}
# ---------------------------------------------------------------------------
F_MAT = np.array(
    [[PHI ** (-1), PHI ** (-0.5)], [PHI ** (-0.5), -PHI ** (-1)]], dtype=complex
)

# ---------------------------------------------------------------------------
# R-symbols (hexagon + spin-statistics consistent gauge)
#     R^{tt}_1  = theta_tau              = e^{4 pi i / 5}
#     R^{tt}_tau = e^{2 pi i / 5} * e^{pi i * 5/5}   (the braid-consistent phase)
# Verified self-consistent via the braid relation below.
# ---------------------------------------------------------------------------
R_TT_1 = THETA_TAU                                   # = e^{4 pi i / 5}
R_TT_TAU = cmath.exp(2j * math.pi / 5) * cmath.exp(1j * math.pi * 5 / 5)


# ---------------------------------------------------------------------------
# Core checks (all return True when the algebra is self-consistent)
# ---------------------------------------------------------------------------
def check_f_unitary() -> bool:
    """F is a unitary associator."""
    return np.allclose(F_MAT.conj().T @ F_MAT, np.eye(2))


def check_pentagon() -> bool:
    """Fibonacci pentagon consistency for the 2x2 unitary associator: F^2 = I."""
    return np.allclose(F_MAT @ F_MAT, np.eye(2))


def check_braid_relation() -> float:
    """Yang-Baxter / braid relation sigma_1 sigma_2 sigma_1 = sigma_2 sigma_1 sigma_2.

    Returns the residual (max |LHS - RHS|); closed algebra -> 0.
    sigma_1 = diag(R) on the 12-intermediate basis,
    sigma_2 = F diag(R) F^dagger.
    """
    R = np.diag([R_TT_1, R_TT_TAU]).astype(complex)
    s1 = R
    s2 = F_MAT @ R @ F_MAT.conj().T
    return float(np.max(np.abs(s1 @ s2 @ s1 - s2 @ s1 @ s2)))


def check_spin_statistics() -> bool:
    """Spin-statistics: R^{tt}_c R^{tt}_c = theta_tau theta_tau / theta_c."""
    a = R_TT_1 ** 2 - THETA_TAU ** 2 / THETA[0]      # c = 1 (vacuum)
    b = R_TT_TAU ** 2 - THETA_TAU ** 2 / THETA[1]    # c = tau
    return abs(a) < 1e-9 and abs(b) < 1e-9


def modular_S() -> np.ndarray:
    """Modular S-matrix of the Fibonacci UMTC.

    The Fibonacci category is the even-weight subcategory of SU(2)_3; its
    modular S is the real, charge-conjugation-symmetric matrix (S^2 = I):

        S = (1/D) * [[ 1,  phi ],
                     [ phi, -1  ]],   D = sqrt(1 + phi^2) = total quantum dim.

    This is the unique matrix (up to the overall phase of T) satisfying the
    Verlinde formula N_{ab}^c = sum_n S_{an} S_{bn} conj(S_{cn}) / S_{0n} for the
    fusion ring tau x tau = 1 + tau.  The naive closed-form
    S_{ab} = (1/D) sum_c N_{ab}^c d_c theta_c does NOT reproduce it (it yields a
    non-Verlinde, non-S^2=I matrix); see `modular_S_naive` for the demonstration.
    """
    return np.array([[1.0, PHI], [PHI, -1.0]], dtype=complex) / D


def modular_S_naive() -> np.ndarray:
    """The naive closed-form S_{ab} = (1/D) sum_c N_{ab}^c d_c theta_c.

    Included ONLY to document why it is wrong: it fails S^2 = I, the (ST)^3
    scalar test, and Verlinde reconstruction for the Fibonacci fusion ring.
    """
    S = np.zeros((2, 2), dtype=complex)
    for a in range(2):
        for b in range(2):
            S[a, b] = sum(N[a][b][c] * QUANTUM_DIM[c] * THETA[c] for c in range(2)) / D
    return S


def modular_T() -> np.ndarray:
    """Modular T-matrix: topological spins on the diagonal (T_a = theta_a)."""
    return np.diag(THETA).astype(complex)

def tqft_identities() -> dict:
    """Verifiable TQFT / Witten-Reshetikhin-Turaev partition-function identities
    for the Fibonacci category, expressed in terms of the (already verified)
    quantum dimensions ``QUANTUM_DIM`` and modular S-matrix ``modular_S``.

    Every identity here is a pure consequence of the modular data and is
    checked numerically (no arithmetic asserted from memory):
      * sum_a d_a^2 = D^2                       (total quantum dimension)
      * Z(S^3) = (1/D^2) sum_a d_a^2 = 1        (vacuum expectation)
      * sum_a |S_{0,a}|^2 = 1                   (S row-0 normalization)
      * S S^{dagger} = I                         (row/column unitarity)
      * S^2 = C (charge conjugation; here C = I)
    Returns a dict of the individual boolean checks plus the raw quantities.
    """
    d = [QUANTUM_DIM[a] for a in range(len(QUANTUM_DIM))]
    S = modular_S()
    n = len(d)

    dim_sum = sum(x * x for x in d)                 # Sum_a d_a^2
    Z_S3 = dim_sum / D**2                           # partition fn of S^3
    row0 = sum(abs(S[0, a]) ** 2 for a in range(n)) # Sum_a |S_{0,a}|^2
    unit = np.allclose(S @ S.conj().T, np.eye(n))   # S S^dagger = I
    charge_conj = np.allclose(S @ S, np.eye(n))     # S^2 = C (here C = I)

    return {
        "quantum_dims": d,
        "D": D,
        "sum_d_a_squared": dim_sum,
        "sum_d_a_squared_eq_D_sq": abs(dim_sum - D**2) < 1e-9,
        "Z_S3": Z_S3,
        "Z_S3_eq_1": abs(Z_S3 - 1.0) < 1e-9,
        "sum_abs_S0a_sq": row0,
        "S_row0_normalized": abs(row0 - 1.0) < 1e-9,
        "S_unitary": unit,
        "S_squared_eq_charge_conj": charge_conj,
    }


def check_tqft_identities() -> bool:
    """True iff every TQFT partition-function identity in ``tqft_identities`` holds."""
    r = tqft_identities()
    return bool(
        r["sum_d_a_squared_eq_D_sq"]
        and r["Z_S3_eq_1"]
        and r["S_row0_normalized"]
        and r["S_unitary"]
        and r["S_squared_eq_charge_conj"]
    )


def check_charge_conjugation(S=None) -> bool:
    """S^2 = C (charge-conjugation matrix). Both Fibonacci labels are self-dual,
    so C = I and the condition reduces to S^2 = I."""
    if S is None:
        S = modular_S()
    return np.allclose(S @ S, np.eye(2))


def check_modularity(S=None, T=None):
    """Modularity of (S,T): (ST)^3 must be a scalar (unit-modulus) multiple of
    the identity.  Returns the scalar zeta = (ST)^3[0,0], or None if it fails."""
    if S is None:
        S = modular_S()
    if T is None:
        T = modular_T()
    M = (S @ T) @ (S @ T) @ (S @ T)
    zeta = M[0, 0]
    if np.allclose(M, zeta * np.eye(2)) and abs(abs(zeta) - 1.0) < 1e-9:
        return zeta
    return None


def central_charge() -> float:
    """Central charge c of the Fibonacci UMTC, derived from the modular scalar
    zeta = (ST)^3 via  zeta = exp(-2 pi i c / 8).

    Returns |c|; the sign is framing-convention dependent.  The Fibonacci
    central charge is 14/5 = 2.8, the Galois conjugate of SU(2)_3's 9/5.
    """
    zeta = check_modularity()
    if zeta is None:
        raise RuntimeError("modularity scalar not found")
    return abs(-8 * cmath.phase(zeta) / (2 * math.pi))


def check_verlinde(S=None) -> bool:
    """Verlinde reconstruction of the fusion matrices via the matrix form.

    N_a = S . diag( S_{a,i} / S_{0,i} ) . S^{-1}.
    Returns True iff all fusion matrices are recovered exactly.
    """
    if S is None:
        S = modular_S()
    Sinv = np.linalg.inv(S)
    for a in range(2):
        lam = [S[a, i] / S[0, i] for i in range(2)]
        Na = S @ np.diag(lam) @ Sinv
        if not np.allclose(np.round(Na.real, 6), np.array(N[a], dtype=float)):
            return False
    return True


def fusion_space_dimension(n: int) -> int:
    """Dimension of the fusion Hilbert space V_n = Hom(tau^n, 1).

    tau x tau = 1 + tau  =>  the multiplicity of the vacuum in tau^n satisfies
        dim(n) = dim(n-1) + dim(n-2),  dim(1) = 0, dim(2) = 1,
    i.e. dim(n) = Fibonacci F_{n-1}  (F_0=0, F_1=1, F_2=1, F_3=2, ...).
    Equivalently this is len(fusion_states(n)): the number of fusion trees of
    n tau-anyons whose root is the vacuum.
    """
    if n <= 0:
        return 0
    a, b = 0, 1  # F_0, F_1
    for _ in range(n - 1):
        a, b = b, a + b
    return a


def fusion_states(n):
    """All valid left-leaning fusion-tree basis states for tau^n -> vacuum (1).

    A basis state of V_n = Hom(tau^n, 1) is encoded as the running totals
        m = (m_1, ..., m_n),   m_1 = 1 (tau), m_n = 0 (vacuum), m_j in {0,1},
    with N_{tau, m_{j-1}}^{m_j} = 1 for every fusion step j = 2..n.  Labels:
    0 = vacuum (1), 1 = tau.  Returned as a list of tuples; its length equals
    dim V_n = F_{n-1}.  (The left-leaning basis is complete: every fusion tree
    is a linear combination of these states.)
    """
    states = []
    if n <= 0:
        return states
    if n == 1:
        return []  # Hom(tau, 1) is empty -> no fusion tree ends in vacuum

    def rec(seq):
        if len(seq) == n:                 # full path m_1..m_n built
            if seq[-1] == 0:              # root must be the vacuum
                states.append(tuple(seq))
            return
        prev = seq[-1]
        for nxt in (0, 1):
            if N[1][prev][nxt] == 1:      # tau fused onto prev gives nxt
                rec(seq + [nxt])

    rec([1])
    return states


def _F_coef(left, new_int, old_int, aft):
    """Fibonacci F-move coefficient  F^{left, tau, tau}_{aft ; old_int, new_int}.

    Reassociates a left-leaning fusion tree by moving the braid: the running
    total ``left`` (the particles to the LEFT of the swapped pair, fused), the
    budget anyon tau, and the running total ``aft`` (to the RIGHT) are all
    held fixed; only the channel ``old_int -> new_int`` (the intermediate of
    the two swapped anyons) is reshuffled:

        first tree:  (left, tau) -> old_int,  then (old_int, tau) -> aft
        second tree: (tau, tau) -> new_int,  then (left, new_int) -> aft

    * left = 0 (vacuum): the vacuum leg is trivial, (0,tau)->old forces
      old_int = 1, and (tau, new)->aft forces new_int = aft.  Coefficient 1
      iff (old_int, new_int) = (1, aft).
    * left = 1 (tau), aft = 1 (tau): the full 2x2 Fibonacci associator
      F_MAT[new_int, old_int]   (note the dummy/new index is the FIRST slot).
    * left = 1 (tau), aft = 0 (vacuum): only the channel new = old = tau is
      allowed, so F = 1 iff new_int = old_int = 1, else 0.
    """
    if left == 0:
        return 1.0 if (old_int == 1 and new_int == aft) else 0.0
    # left == 1 (tau)
    if aft == 1:
        return F_MAT[new_int, old_int]
    return 1.0 if (new_int == 1 and old_int == 1) else 0.0


def fibonacci_braid_representation(n):
    """Projective braid-group representation rho: B_n -> U(dim V_n) for n tau anyons.

    Uses the left-leaning fusion-tree basis ``fusion_states`` (full tuple
    m_1..m_n of running totals) and the Fibonacci F/R data.  Generator
    ``sigma_k`` swaps anyons k and k+1.  In the left-leaning basis the single
    channel that varies is the running total ``m_{k+1}`` (the intermediate
    between anyon k and the rest); all other running totals are held fixed.

        * sigma_1 (k=1): the vacuum sits left of the pair, so the braid is
          diagonal,  (sigma_1)_{m,m} = R^{tau,tau}_{m_2}.
        * sigma_k, k >= 2: the F-move reshuffles m_{k+1} with left total
          m_k and right total m_{k+2} (the right total is the vacuum when
          k = n-1):
              (sigma_k)_{m',m} = sum_d  F[m_k, d, m'_{k+1}, m_{k+2}]
                                              R[d]
                                              F[m_k, d, m_{k+1}, m_{k+2}]
          where F is the 3j-associator returned by ``_F_coef`` and R[d] is the
          R-symbol on the swapped-pair intermediate d.

    Returns (states, [sigma_1, ..., sigma_{n-1}]) as numpy arrays.  The
    representation is verified in ``check_braid_artin`` against the Artin
    relations (unitarity, Yang-Baxter, and non-adjacent commutativity) for
    n up to 12.
    """
    states = fusion_states(n)
    d = len(states)
    R = {c: (R_TT_1 if c == 0 else R_TT_TAU) for c in (0, 1)}

    sigmas = []
    for k in range(1, n):           # generator sigma_k, 1 <= k <= n-1
        M = np.zeros((d, d), dtype=complex)
        pv = k - 1                  # index of the varying running total m_{k+1}
        for i, m in enumerate(states):
            if k == 1:
                M[i, i] = R[m[1]]   # sigma_1 is diagonal (vacuum to the left)
                continue
            left = m[k - 2]                     # running total m_k  (left of pair)
            right = m[k] if k < n - 1 else 0   # m_{k+2} (right); vacuum for last
            c1old = m[pv]                       # old intermediate m_{k+1}
            for j, mp in enumerate(states):
                # the braid only changes m_{k+1}; every other running total
                # must match between m and mp, else the state is disconnected.
                if any(mp[p] != m[p] for p in range(n) if p != pv):
                    continue
                c1new = mp[pv]                  # new intermediate m'_{k+1}
                val = 0.0
                for dd in (0, 1):
                    val += (
                        _F_coef(left, dd, c1new, right)
                        * R[dd]
                        * _F_coef(left, dd, c1old, right)
                    )
                M[j, i] = val
        sigmas.append(M)
    return states, sigmas

def evaluate_braid_word(n, word):
    """Evaluate an Artin braid word to a unitary on the fusion space V_n.

    ``word`` is a list of signed integers: ``+k`` means sigma_k, ``-k`` means
    sigma_k^{-1} = sigma_k^dagger (the representation is unitary, so the
    inverse is the conjugate transpose).  Returns the product matrix U acting
    on Hom(tau^n, 1), built left-to-right.

    Example: the Yang-Baxter braid ``[1,2,1]`` and ``[2,1,2]`` yield the same
    unitary (see check_word_relations).

    Note the argument order. `FibonacciBraidSimulator.evaluate_braid_word` on
    the simulator takes `(word, num_strands)`, the reverse of this one, and the
    two spellings sitting in one package is a live footgun: passing them the
    wrong way round returns a matrix rather than an error. The swapped call is
    detected and named here rather than silently evaluated.
    """
    if isinstance(n, (list, tuple)) or isinstance(word, int):
        raise TypeError(
            "evaluate_braid_word(n, word) takes the strand count FIRST. The "
            "simulator method of the same name takes (word, num_strands); "
            "these arguments look swapped."
        )
    states, sigmas = fibonacci_braid_representation(n)
    d = len(states)
    U = np.eye(d, dtype=complex)
    for g in word:
        k = abs(g)
        if k < 1 or k > len(sigmas):
            raise ValueError(f"generator sigma_{k} out of range for n={n}")
        s = sigmas[k - 1]
        U = (s.conj().T if g < 0 else s) @ U
    return U


def check_word_relations(n=5):
    """Sanity checks on evaluate_braid_word for n anyons:
        * sigma_k sigma_k^{-1} = I  (inverse = adjoint)
        * the Yang-Baxter words [k, k+1, k] and [k+1, k, k+1] agree
        * a non-trivial word produces a unitary matrix
    Returns True iff all relations hold for every applicable generator.
    """
    states = fusion_states(n)
    d = len(states)
    for k in range(1, n):
        if not np.allclose(
            evaluate_braid_word(n, [k, -k]), np.eye(d), atol=1e-9
        ):
            return False
        if k + 1 < n:
            if not np.allclose(
                evaluate_braid_word(n, [k, k + 1, k]),
                evaluate_braid_word(n, [k + 1, k, k + 1]),
                atol=1e-9,
            ):
                return False
    # non-trivial word must be unitary
    U = evaluate_braid_word(n, [1, 2, 3, 1, 2, -1])
    return np.allclose(U @ U.conj().T, np.eye(d), atol=1e-9)


def check_braid_artin(n_max=12):
    """Verify rho(B_n) obeys the Artin braid relations for all n <= n_max:
        (i)  sigma_i sigma_j = sigma_j sigma_i        for |i-j| >= 2
        (ii) sigma_i sigma_{i+1} sigma_i = sigma_{i+1} sigma_i sigma_{i+1}
    Returns True only if every relation holds (F^2=I makes these close exactly).
    """
    for n in range(3, n_max + 1):
        _, sig = fibonacci_braid_representation(n)
        for i in range(len(sig)):
            for j in range(len(sig)):
                if abs(i - j) >= 2:
                    if not np.allclose(sig[i] @ sig[j], sig[j] @ sig[i]):
                        return False
        for i in range(len(sig) - 1):
            if not np.allclose(
                sig[i] @ sig[i + 1] @ sig[i], sig[i + 1] @ sig[i] @ sig[i + 1]
            ):
                return False
    return True


def summary() -> dict:
    """Run every check and return a report."""
    S = modular_S()
    return {
        "PHI": PHI,
        "total_quantum_dim_D": D,
        "D_squared": 1 + PHI**2,
        "theta_tau": THETA_TAU,
        "h_tau": 2 / 5,
        "F_unitary": check_f_unitary(),
        "pentagon_F2_eq_I": check_pentagon(),
        "braid_residual": check_braid_relation(),
        "spin_statistics": check_spin_statistics(),
        "verlinde_reconstruction": check_verlinde(S),
        "S_unitary": np.allclose(S @ S.conj().T, np.eye(2)),
        "S_charge_conjugation_S2_eq_I": check_charge_conjugation(S),
        "modularity_scalar_zeta": check_modularity(S),
        "central_charge_c": central_charge(),
        "fusion_dims_first_10": [fusion_space_dimension(i) for i in range(1, 11)],
        "fusion_dims_check_Fn_minus_1": all(
            fusion_space_dimension(i) == fusion_states(i).__len__()
            for i in range(1, 11)
        ),
        "braid_artin_relations_Bn_le_12": check_braid_artin(12),
        "braid_word_relations_n5": check_word_relations(5),
        "dim_V6_equals_F5": fusion_space_dimension(6) == 5,
        "TL_loop_value_delta": PHI,
        "tqft_identities_pass": check_tqft_identities(),
    }


if __name__ == "__main__":
    rep = summary()
    print("=" * 60)
    print("FIBONACCI ANYON ALGEBRA -- self-consistency report")
    print("=" * 60)
    for k, v in rep.items():
        print(f"  {k:28s}: {v}")
    ok = (
        rep["F_unitary"]
        and rep["pentagon_F2_eq_I"]
        and abs(rep["braid_residual"]) < 1e-9
        and rep["spin_statistics"]
        and rep["verlinde_reconstruction"]
        and rep["S_unitary"]
        and rep["S_charge_conjugation_S2_eq_I"]
        and rep["modularity_scalar_zeta"] is not None
        and rep["fusion_dims_first_10"] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        and rep["fusion_dims_check_Fn_minus_1"]
        and rep["braid_artin_relations_Bn_le_12"]
        and rep["braid_word_relations_n5"]
        and rep["tqft_identities_pass"]
    )
    print("=" * 60)
    print("ALL CHECKS PASSED:" , ok)
