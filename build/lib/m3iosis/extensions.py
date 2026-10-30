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
    
    # 5. Partial Trace (Analytic: for 2x2 system, trace out B)
    def partial_trace(self, rho): return np.array([[rho[0,0]+rho[1,1], 0], [0, 0]], dtype=complex)
    
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
    
    # 13. State Rotation (U=exp(i*theta))
    def rotate(self, state, angle): return cmath.exp(1j * angle) * state
    
    # 14. Braid Word Concatenation (Literal)
    def concat(self, w1, w2): return list(w1) + list(w2)
    
    # 15. System Dimension (Defined by Fusion Basis)
    def sys_dim(self): return int(self.F.shape[0])
