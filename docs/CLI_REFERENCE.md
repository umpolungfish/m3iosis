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
*   `--jones N GENS...`: Jones polynomial of the braid closure at t = e^{2πi/5}, the evaluation Fibonacci anyons perform natively. The quantum trace runs over both total-charge sectors weighted by quantum dimension. Its two normalization constants are forced by the Markov moves on the unknot rather than fitted, and come out as the framing phase e^{-iπ/5} and the loop value -φ. Verified against exact values for the trefoil, its mirror, the figure-eight and the cinquefoil. Note that σ₁ here is the negative crossing in the standard Jones orientation, and that one root of unity is not a complete invariant: T(2,9), T(2,11) and 8₁₉ all evaluate to 1 as the unknot does.
*   `--gate-info`: Report on quantum computational universality. Shows available qubit counts where dim V_n is a power of 2.
*   `--tree N`: Show the fusion tree basis states for N tau-anyons fusing to vacuum.
*   `--dimension N`: Print the fusion space dimension dim V_n = Fibonacci F_{n-1}.
*   `--summary`: Full self-consistency report of the Fibonacci anyon algebra.
*   `--sim`: Simulate a braid sequence (uses `--word` for the braid word).
*   `--manifold`: Topological manifold operations (curvature, path integral).
*   `--word GENS...`: Braid word for simulation (default: `[1, 2, 1]`).

### `qc`
Fibonacci quantum computer: compile standard gates down to braid words.

*   `--circuit GATES...`: Compile a circuit over `H`, `T`, `S`, `X`. The whole circuit is compiled as one unitary rather than gate by gate, so the approximation error is incurred once instead of accumulating across the gates, and the braid comes out shorter.
*   `--approx-h`, `--approx-t`: Compile the Hadamard or T gate on its own.
*   `--verify`: Full verification suite.
*   `--gate-stats`: Report on the generated gate group.
*   `--available`: Qubit encodings available in the fusion space.
*   `--depth N`: Maximum braid word depth (default 5).

The reported error is phase-invariant, because a braid realizes its gate only up to a global phase and that phase is not observable. It is measured by removing the optimal phase and comparing elementwise, not by the usual `sqrt(1 - |tr(U†V)|/n)`, which subtracts two numbers agreeing to fifteen digits and therefore carries a few percent of error at 1e-5 and collapses to exactly zero below about 1e-8. Braids in this range routinely reach that floor, so the closed form reports perfect gates that are not perfect.

Compilation splits and fuses rather than ranking. Several braid words typically sit at the same distance from the target; each seeds a different trajectory and leaves a residual rotation pointing its own way. Every one of them is followed as a separate arm, and then the arms that lost compile the residual left by the arm that won, which gets appended. The composite therefore beats every arm it was chosen from. Present accuracy at recursion depth 3, against the same net without the split:

| circuit | single arm | split and fused | braid length |
|---------|-----------|-----------------|--------------|
| `T`     | 3.15e-05  | 5.41e-06        | 1486 → 1410  |
| `T S`   | 9.54e-05  | 1.83e-07        | 1801 → 5247  |
| `H T`   | 1.41e-05  | 2.92e-06        | 1732 → 2660  |
| `H`     | 4.18e-05  | 1.35e-06        | 1797 → 4165  |

`T` is the one case where the correction is not appended at all: a different tied base wins outright, so the braid gets shorter as well as more accurate. Elsewhere the accuracy is bought with roughly two to three times the length, and the cost is eight arms plus eight residual compilations instead of one pass.

Every reported unitary is checked against its own printed word by resynthesizing the word from scratch, which agrees to about 1e-13. The determinant identity `det(braid) = det(sigma_1)^(sum of exponents)` is reported as context but is not the check: `det(sigma_1)` is a primitive tenth root of unity, so that test passes by chance one time in ten, and it sees only the sum of the exponents, so every permutation of a word passes it.

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

### `braid-grammar`
Braid Grammar Bridge — Fibonacci braid words to Imscribing Grammar tuples.

*   `word...`: Braid word as signed Artin generators (positive = sigma_k, negative = sigma_k^{-1}). Required positional argument.
*   `--strands N`, `-n N`: Number of strands (default: 4, dim V_4 = 2 = 1 qubit).

Takes a braid word and evaluates it on the Fibonacci braid group representation in the fusion space V_n = Hom(tau^n, 1). Extracts topological invariants (writhe, braid trace, eigenvalues, Jones polynomial, fusion space dimension) and maps each to a grammar primitive value. Outputs the 12-glyph canonical tuple and a Frobenius closure verdict (μ∘δ = id).

**Grammar primitive mapping:**
| Invariant | Slot | Rationale |
|-----------|------|-----------|
| Fusion space dimension | Ð | Dimensionality of the fusion space |
| Crossing count / isotopy class | Þ | Topological complexity of the braid |
| Unitary braid representation | Ř | Dagger/adjoint coupling of the rep |
| Topological spin / eigenvalue spectrum | Φ | Self-statistics parity |
| Jones polynomial evaluation | ƒ | Quantum fidelity of the braid closure |
| Braid word complexity | Ç | Kinetics of the braid operation |
| Number of anyons | Γ | Cardinality of the fusion input |
| Generator multiplication order | ɢ | Sequential vs broadcast composition |
| Frobenius closure (μ∘δ = id) | φ̂ | Criticality — self-modeling fixed point |
| Writhe (signed crossing sum) | Ħ | Chirality — braid orientation |
| Fusion outcome multiplicity | Σ | Stoichiometry of fusion channels |
| Total eigenvalue winding | Ω | Topological winding invariant |

**Examples:**
```bash
m3 braid-grammar 1 2 1                       # Yang-Baxter → ⟨𐑨𐑥𐑑𐑹𐑱𐑧𐑲𐑜⊙𐑖𐑕𐑴⟩ (CLOSED)
m3 braid-grammar 1 2 1 2 1                   # Longer braid → ⟨𐑨𐑥𐑑𐑹𐑞𐑤𐑲𐑠𐑣𐑫𐑕𐑴⟩ (OPEN)
m3 braid-grammar -1 -2 -1                    # Inverse → same tuple as YB (writhe sign not in glyphs)
m3 braid-grammar --strands 7 1 2 3 2 1       # 7 strands, dim V_7 = 8 = 3 qubits
m3 braid-grammar                             # Empty word → identity braid
```

Frobenius closure (CLOSED/OPEN) indicates whether the braid's unitary representation satisfies μ∘δ = id (unitary + real trace). CLOSED means the braid is self-adjoint in the statistical sense; OPEN means the braid carries non-trivial topological winding.

**Source:** `m3iosis.braid_grammar_bridge.BraidGrammarAnalyzer`
