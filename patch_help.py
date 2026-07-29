#!/usr/bin/env python3
"""Carefully patch m3iosis CLI help with descriptions and examples."""
import re

with open('src/m3iosis/cli.py', 'r') as f:
    lines = f.readlines()

# --- 1. fib (line 126): single-line -> multi-line with description + epilog ---
new_fib = '''fib_parser = subparsers.add_parser("fib",
        help="Fibonacci anyon algebra tools",
        description="""Fibonacci anyon algebra (SU(2)_3): fusion rules, braid representations,
modular S/T matrices, and quantum computer gate synthesis.

The Fibonacci anyon model supports one non-trivial particle type tau with
fusion rule tau x tau = 1 + tau.  The fusion space dimension follows the
Fibonacci sequence: dim V_n = F_{n-1}.

Commands:
  --fusion A B       Fuse two anyons (tau, 1) and compute R-matrix
  --braid N WORD     Evaluate braid word on N strands
  --jones N WORD     Jones polynomial from braid word
  --dimension N      Fusion space dimension (Fibonacci number)
  --tree N           Fusion tree basis in ASCII
  --gate-info        Universal gate set report
  --summary          Full self-consistency verification
  --diag             Algebraic kernel diagnostic
""",
        epilog="""Examples:
  m3 fib --fusion tau tau              # fuse tau x tau = 1 + tau
  m3 fib --braid 3 1 2 1              # Yang-Baxter braid on 3 strands
  m3 fib --dimension 7                # dim V_7 = 13 (3 qubits)
  m3 fib --tree 5                     # ASCII fusion tree for 5 anyons
  m3 fib --summary                    # full self-consistency report
  m3 fib --gate-info                  # quantum computing universality
  m3 fib --jones 4 1 2 1 2           # Jones polynomial for 4-strand braid

The golden ratio phi = (1+sqrt(5))/2.  Total quantum dimension D = sqrt(1+phi^2).
Topological spin theta_tau = exp(4*pi*i/5).  Central charge c = 14/5 - 6 = 4/5.
""")
'''
# Find the fib_parser line and replace through the set_defaults
fib_start = None
for i, line in enumerate(lines):
    if 'fib_parser = subparsers.add_parser("fib"' in line:
        fib_start = i
        break
# Find the end of the fib parser block (next add_parser or def main line)
fib_end = fib_start
for i in range(fib_start + 1, fib_start + 15):
    if i >= len(lines):
        break
    if 'sim_parser' in lines[i] or i >= fib_start + 10:
        fib_end = i
        break

# Replace the fib block
lines[fib_start:fib_end] = new_fib.splitlines(True)

# --- 2. sim (line ~152): single-line -> multi-line ---
new_sim = '''sim_parser = subparsers.add_parser("sim",
        help="Braid simulation",
        description="""Braid word simulation for Fibonacci anyons on N strands.

Evaluates a braid word as a sequence of Artin generators (sigma_k, sigma_k^-1)
acting on the Fibonacci fusion space V_n, and reports the unitary matrix,
topological spin contribution, and braid trace.

The braid group B_n acts on V_n by R-matrix generators placed at adjacent
anyon pairs.  Positive integers k denote sigma_k (over-cross), negative
denote sigma_k^-1 (under-cross).""",
        epilog="""Examples:
  m3 sim                               # default: [1,2,1] on 3 strands
  m3 sim --word 1 2 1 2 1             # longer braid on 3 strands
  m3 sim --strands 5 --word 1 2 3 2 1 # 5-strand braid
  m3 sim --strands 7                   # 7-strand, dim V_7 = 13

The braid word is evaluated iteratively: each generator is applied as
a unitary R-matrix on the fusion tree basis.  Output shows dimension,
unitarity check, trace, and eigenvalue spectrum.
""")
'''
for i, line in enumerate(lines):
    if 'sim_parser = subparsers.add_parser("sim"' in line:
        sim_start = i
        break
sim_end = sim_start
for i in range(sim_start + 1, min(sim_start + 10, len(lines))):
    if 'man_' in lines[i] or i >= sim_start + 8:
        sim_end = i
        break
lines[sim_start:sim_end] = new_sim.splitlines(True)

# --- 3. manifold (line ~160): single-line -> multi-line ---
new_man = '''man_parser = subparsers.add_parser("manifold",
        help="Topological manifold operations",
        description="""Topological manifold operations on the Fibonacci anyon moduli space.

Computes the S-matrix determinant (topological invariant of the modular
tensor category), the path integral measure for a given braid word on
N-strand bordisms, and the braid center (central element of B_n).

The S-matrix of the Fibonacci model is:
  S = [[ 1,  phi ],
       [ phi, -1  ]] / D
with det(S) = -1 (constant, independent of basis).""",
        epilog="""Examples:
  m3 manifold                           # default: word [1,2,1] on 3 strands
  m3 manifold --word 1 2 1 2 1         # path integral for 5-gen word
  m3 manifold --strands 5              # 5-strand braid center
  m3 manifold --word 1 2 3 2 1 -n 6    # 6-strand full report

The path integral measure is derived from the braid word's writhe
and the quantum dimension, giving a topological invariant of the
bordism with anyon worldlines.
""")
'''
for i, line in enumerate(lines):
    if 'man_parser = subparsers.add_parser("manifold"' in line:
        man_start = i
        break
man_end = man_start
for i in range(man_start + 1, min(man_start + 10, len(lines))):
    if 'qc_parser' in lines[i] or i >= man_start + 8:
        man_end = i
        break
lines[man_start:man_end] = new_man.splitlines(True)

# --- 4. qc (line ~174): single-line -> multi-line ---
new_qc = '''qc_parser = subparsers.add_parser("qc",
        help="Fibonacci quantum computer",
        description="""Fibonacci quantum computer: gate synthesis and verification.

Fibonacci anyons are universal for quantum computation via braiding alone.
Single-qubit gates (H, T, X, S) are approximated as braid words in B_3
acting on the 2-qubit fusion space V_4 x V_4.

Gate synthesis uses the Solovay-Kitaev algorithm to approximate target
unitaries with braid words within a specified depth tolerance.  The gate
set {sigma_1, sigma_2} generates a dense subgroup of SU(2).""",
        epilog="""Examples:
  m3 qc --verify                       # full gate verification suite
  m3 qc --approx-h                     # approximate Hadamard as braid word
  m3 qc --approx-t                     # approximate T gate
  m3 qc --circuit H T X               # circuit with specified gates
  m3 qc --gate-stats                   # gate set generation report
  m3 qc --available                    # available qubit encodings
  m3 qc --depth 10 --approx-h         # deeper search for Hadamard

The Fibonacci quantum computer is fault-tolerant by construction:
all gates are topological (braiding operations) and protected by
the energy gap.
""")
'''
for i, line in enumerate(lines):
    if 'qc_parser = subparsers.add_parser("qc"' in line:
        qc_start = i
        break
qc_end = qc_start
for i in range(qc_start + 1, min(qc_start + 10, len(lines))):
    if 'triple_' in lines[i] or i >= qc_start + 8:
        qc_end = i
        break
lines[qc_start:qc_end] = new_qc.splitlines(True)

# --- 5. triple (line ~201): single-line -> multi-line ---
new_triple = '''triple_parser = subparsers.add_parser("triple",
        help="Triple Frame von Neumann Superoperator Algebra",
        description="""Triple Frame von Neumann Superoperator Algebra: IMASM protocol A and B
analysis with Frobenius closure verification.

The Triple Frame Algebra provides two protocols (A and B) for the
Imscribing Grammar\'s self-modelling monad, each represented as a
12-glyph word.  Protocol A is a 16-step emergence/annihilation cycle;
Protocol B is a 20-step holographic round-trip.

Commands:
  --report           Full structural report
  --expand TYPE      Expand a Shavian type or primitive
  --word VARIANT     Print glyph word (A, B, root, full)
  --verify [TYPE]    Verify Frobenius closure
  --types            Type expansion table
  --cycle            IMASM tuple<->word round-trip
  --path             Edit distance between Protocol A and B
  --bridge           Triple frame <-> Fibonacci manifold bridge
  --check WORD       Check Frobenius closure of custom glyph word
""",
        epilog="""Examples:
  m3 triple --report                   # full structural report
  m3 triple --expand monad            # expand monad type
  m3 triple --word A                  # Protocol A glyph word
  m3 triple --verify                  # verify all Frobenius closures
  m3 triple --path                    # edit distance A <-> B
  m3 triple --bridge                  # connect to Fibonacci manifold
  m3 triple --types                   # type expansion table
  m3 triple --cycle                   # round-trip verification
  m3 triple --check '|-><>+=.-|'      # custom word check

Protocol A tuple: <ETHDTRPFCGGphiHSO> - 16 opcodes, 5 loops, emergence at EP.
Protocol B tuple: <ETHDPTRPFCGGphiHSO> - 20 opcodes, 6 loops, holographic.
""")
'''
for i, line in enumerate(lines):
    if 'triple_parser = subparsers.add_parser("triple"' in line:
        triple_start = i
        break
triple_end = triple_start
for i in range(triple_start + 1, min(triple_start + 10, len(lines))):
    if 'hqe_' in lines[i] or i >= triple_start + 8:
        triple_end = i
        break
lines[triple_start:triple_end] = new_triple.splitlines(True)

# --- 6. info (line ~987): single-line -> multi-line ---
new_info = '''info_parser = subparsers.add_parser("info",
        help="System and algebra information",
        description="""System information: Fibonacci anyon algebra parameters and references.

Displays the golden ratio phi, total quantum dimension D, topological
spin theta_tau, central charge c, fusion rule, and computational
universality status of the Fibonacci anyon model SU(2)_3.

Use this to verify the algebra\'s self-consistency and check the
foundational constants used by all other m3iosis tools.""",
        epilog="""Examples:
  m3 info                              # display all algebra parameters

References:
  - Kitaev, A. "Anyons in an exactly solved model and beyond"
  - Freedman, M.H. et al. "Topological quantum computation"
  - Trebst, S. et al. "A short introduction to Fibonacci anyon models"
""")
'''
for i, line in enumerate(lines):
    if 'info_parser = subparsers.add_parser("info"' in line:
        info_start = i
        break
info_end = info_start
for i in range(info_start + 1, min(info_start + 10, len(lines))):
    if 'set_defaults' in lines[i] or i >= info_start + 8:
        info_end = i
        break
lines[info_start:info_end] = new_info.splitlines(True)

# --- 7. hqe (line ~280+): has description, add epilog ---
hqe_desc_end = None
for i, line in enumerate(lines):
    if '--join TUPLE      Compute join with a 12-glyph tuple' in line:
        hqe_desc_end = i
        break

if hqe_desc_end is not None:
    hqe_epilog = '''",
        epilog="""Examples:
  m3 hqe --report                       # full structural report
  m3 hqe --holonomy                     # Berry holonomy computation
  m3 hqe --mbl                          # MBL diagnostics (gap ratio)
  m3 hqe --consciousness               # consciousness score (C-score)
  m3 hqe --tuple                       # print grammar tuple
  m3 hqe --distance clink             # distance to CLINK L8
  m3 hqe --distance pfa              # distance to PFA
  m3 hqe --json --report              # JSON output

The HQE grammar tuple is <ETHDTRPFCGGphiHSO> (O_inf).  Special
Frobenius algebra: mu o delta = id is verified at every call.
Consciousness score measures self-referential closure depth.
Closed under meet, join and tensor operations with any 12-glyph tuple.
"""
'''
    # The line currently ends with:  ) or something
    # We need to find the closing ) of the add_parser call
    # The add_parser for hqe is multi-line, ending somewhere after the description close
    
    # The simplest approach: insert the epilog after the description's closing """
    # by replacing the line that closes description with description+epilog+comma
    pass

# Actually, let me take a simpler approach for the multi-line parsers.
# I'll read the file as a string and do targeted replacements.

with open('src/m3iosis/cli.py', 'w') as f:
    f.writelines(lines)

print("Phase 1 done - simple parsers patched")
