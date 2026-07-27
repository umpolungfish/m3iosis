# M3Iosis CLI Reference

The `m3` tool provides a unified command-line interface for meta-mathematical morphogenesis and anyonic algebra.

## Usage

```bash
m3 [COMMAND] [OPTIONS]
```

## Commands

### `fib`
Fibonacci Anyon operations.

*   `--diag`: Run algebraic kernel verification. Checks for unitarity, Frobenius consistency (B4=T), and topological consistency of the S-matrix.
*   `--fusion A B`: Fuse two anyons. Example: `--fusion tau tau` → `tau x tau = 1 + tau`
*   `--braid N GENS...`: Evaluate a braid word on N strands. Example: `--braid 4 1 2 3 1 2 3`
*   `--jones N GENS...`: Compute the Jones polynomial (normalized Markov trace) from a braid word.
*   `--gate-info`: Report on quantum computational universality. Shows available qubit counts where dim V_n is a power of 2.
*   `--tree N`: Show the fusion tree basis states for N tau-anyons fusing to vacuum.
*   `--dimension N`: Print the fusion space dimension dim V_n = Fibonacci F_{n-1}.
*   `--summary`: Full self-consistency report of the Fibonacci anyon algebra.
*   `--sim`: Simulate a braid sequence (uses `--word` for the braid word).
*   `--manifold`: Topological manifold operations (curvature, path integral).
*   `--word GENS...`: Braid word for simulation (default: `[1, 2, 1]`).

### `sim`
Braid simulation.

*   `--word GENS...`: Braid word to simulate.
*   `--strands N`: Number of strands (default: 3).

### `manifold`
Topological manifold operations.

*   `--word GENS...`: Braid word for path integral.
*   `--strands N`: Number of strands (default: 3).

### `info`
System and algebra information. Prints key constants: golden ratio, total quantum dimension, topological spin, central charge, fusion rules, and universality status.

## Installation
The `m3iosis` package is installed in the local environment and manages its own internal dependencies via `pyproject.toml`.

## Internal Structure
*   **Algebraic Kernel:** `m3iosis.fibonacci_anyon_algebra`
*   **Operational Tools:** `m3iosis.fibonacci_anyon_tool`
*   **CLI Entry:** `m3iosis.cli`
*   **Tool Bridge:** `m3iosis.fibonacci_anyon_tool`

## Operational Tool Classes

### `FibonacciAnyonAlgebra`
High-level charge algebra operations:
- `quantum_dimension(label)`: d_1 = 1, d_tau = phi
- `topological_spin(label)`: theta_j = exp(2*pi*i*h_j)
- `total_quantum_dimension()`: D = sqrt(1 + phi^2)
- `central_charge()`: c = 14/5 = 2.8
- `fuse(a, b)`: Fusion product a x b → list of outcomes
- `fusion_multiplicity(a, b, c)`: N_{a,b}^c
- `f_move(...)`: F-move associator coefficient
- `r_move(a, b, c)`: R-symbol braiding phase
- `braid_generator(n, k)`: sigma_k matrix on V_n
- `braid_word(n, word)`: Evaluate braid word to unitary
- `braid_to_quantum_gate(n, word)`: Map braid to qubit gate

### `FibonacciBraidSimulator`
Full fusion-tree braid representation:
- `get_braid_matrix(strand_idx, num_strands)`: Embedded braid generator
- `evaluate_braid_word(word, num_strands)`: Product of braid operators
- `get_fusion_probabilities(state)`: |1> and |tau> probabilities
- `braid_statistics(n, word)`: Unitary, eigenvalues, trace, dimension

### `FibonacciQuantumComputer`
Braid-to-gate synthesis for universal quantum computation:
- `available_qubit_counts()`: n values where dim V_n = 2^k
- `synthesize_gate(n, word)`: Braid → unitary quantum gate
- `gate_set_report()`: Universality report
- `jones_polynomial(n, word)`: Jones polynomial from Markov trace

### `FibonacciDiagram`
ASCII and LaTeX diagrammatic rendering:
- `fusion_tree_ascii(n)`: ASCII art fusion tree basis
- `braid_word_ascii(word)`: ASCII art braid diagram
- `fusion_tree_latex(n)`: TikZ code for fusion trees
- `braid_word_latex(word)`: TikZ code for braid diagrams

## Mathematical Background

Fibonacci anyons form the simplest non-Abelian topological quantum field theory. They arise from SU(2) Chern-Simons theory at level k=3 (the even subcategory), with two particle types:

- **1** (vacuum): trivial anyon, quantum dimension d_1 = 1
- **tau** (Fibonacci anyon): non-Abelian anyon, quantum dimension d_tau = phi = (1+√5)/2

### Key Data
- **Fusion rule:** tau × tau = 1 + tau
- **Quantum dimension:** d_tau = phi ≈ 1.618034
- **Total quantum dimension:** D = sqrt(1 + phi²) ≈ 1.902113
- **Topological spin:** theta_tau = exp(4*pi*i/5) ≈ -0.809017 + 0.587785j
- **Central charge:** c = 14/5 = 2.8
- **Temperley-Lieb loop value:** delta = phi

### Computational Universality
Fibonacci anyons are computationally universal: any unitary operation on qubits can be approximated to arbitrary precision by braiding Fibonacci anyons (Freedman-Kitaev theorem). The braid group representation is dense in the unitary group for sufficiently large n.

### Available Qubit Encodings
The fusion space V_n = Hom(tau^n, 1) has dimension F_{n-1} (Fibonacci numbers). Qubit encodings require dim V_n = 2^k:

| n | dim V_n | qubits |
|---|---------|--------|
| 2 | 1       | 0      |
| 3 | 1       | 0      |
| 4 | 2       | 1      |
| 7 | 8       | 3      |
