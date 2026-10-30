"""
Fibonacci Anyon Algebra Operational Tool - Addendum
===================================================
Implementation of 15 functional primitives for topological process synthesis.
"""
import numpy as np
import cmath
import math
from scipy.linalg import logm, eigvals
from m3iosis.fibonacci_anyon_tool import FibonacciBraidSimulator

class FibonacciExtensions(FibonacciBraidSimulator):
    
    # 1. Braid Inverse (Analytic)
    def braid_inv(self, strand_idx, n): return np.linalg.inv(self.get_braid_matrix(strand_idx, n))
    
    # 2. Braid Powers (Analytic)
    def braid_power(self, idx, n, p): return np.linalg.matrix_power(self.get_braid_matrix(idx, n), p)
    
    # 3. Fusion Tree Basis (Analytic)
    def get_vacuum_basis(self): return np.array([1.0, 0.0], dtype=complex)
    
    # 4. Tau Basis (Analytic)
    def get_tau_basis(self): return np.array([0.0, 1.0], dtype=complex)
    
    # 5. Charge-sector weights
    def charge_sector_weights(self, rho):
        """Weight of a density matrix in each total-charge sector.

        This replaces a method that was called `partial_trace` and returned
        `[[rho00 + rho11, 0], [0, 0]]`. That is not a partial trace: a
        two-dimensional fusion space carries no tensor factorization to trace
        out, so there is no subsystem to discard. Splitting a fusion tree needs
        the F-matrix, and the result is a sum over sectors rather than a
        smaller matrix on the same space.

        What IS well defined without any splitting is the weight the state
        carries in each total-charge sector, since the sectors are orthogonal
        by superselection. That is what this returns.
        """
        diag = np.real(np.diag(rho))
        return {"vacuum": float(diag[0]), "tau": float(sum(diag[1:]))}
    
    # 6. Expectation Value (Analytic)
    def exp_val(self, state, op): return state.conj().T @ op @ state
    
    # 7. Entropy (Von Neumann: Calculated from density matrix)
    def vne(self, rho): 
        evals = eigvals(rho)
        evals = evals[evals > 1e-12]
        return -np.sum(evals * np.log2(evals))
    
    # 8. Braid Word Commutator (Analytic)
    def commutator(self, w1, w2, n): 
        op1 = self.evaluate_braid_word(w1, n)
        op2 = self.evaluate_braid_word(w2, n)
        return op1 @ op2 - op2 @ op1
    
    # 9. Random Braid Word (Probabilistic)
    def random_word(self, n, length): return [int(i) for i in np.random.randint(1, n, length)]
    
    # 10. Trace calculation (Analytic)
    def trace(self, op): return np.trace(op)
    
    # 11. Density Matrix (Analytic)
    def get_rho(self, state): return np.outer(state, state.conj().T)
    
    # 12. Fidelity Calculation (Analytic)
    def fidelity(self, s1, s2): return abs(s1.conj().T @ s2)**2
    
    # 13. Global phase, and a rotation that is not one
    def global_phase(self, state, angle):
        """Multiply by exp(i*angle). Named for what it is.

        This carried the name `rotate`, which promised an observable change.
        A global phase changes no expectation value and no fusion probability;
        it is exactly the quantity a projective representation quotients out.
        """
        return cmath.exp(1j * angle) * state

    def rotate(self, state, angle):
        """Rotate about the charge axis: exp(-i*angle*Z/2), a relative phase.

        The relative phase between the vacuum and tau amplitudes IS observable,
        being what an interference measurement reads, so this is the rotation
        the old name promised.
        """
        z = np.diag([np.exp(-0.5j * angle), np.exp(0.5j * angle)])
        return z @ np.asarray(state, dtype=complex)
    
    # 14. Braid Word Concatenation (Literal)
    def concat(self, w1, w2): return list(w1) + list(w2)
    
    # 15. System Dimension (Defined by Fusion Basis)
    def sys_dim(self): return int(self.F.shape[0])
