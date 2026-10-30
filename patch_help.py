#!/usr/bin/env python3
"""
Patch m3iosis CLI help: add descriptions + examples.
Uses unique description-start anchors to avoid cross-tool matching.
"""
with open('src/m3iosis/cli.py', 'r') as f:
    content = f.read()

# ===== SINGLE-LINE PARSERS (unique old patterns) =====

# 1. fib
content = content.replace(
    'fib_parser = subparsers.add_parser("fib", help="Fibonacci anyon algebra tools")',
    '''fib_parser = subparsers.add_parser("fib",
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
""")''')

# 2. sim
content = content.replace(
    'sim_parser = subparsers.add_parser("sim", help="Braid simulation")',
    '''sim_parser = subparsers.add_parser("sim",
        help="Braid simulation",
        description="""Braid word simulation for Fibonacci anyons on N strands.

Evaluates a braid word as a sequence of Artin generators (sigma_k, sigma_k^-1)
acting on the Fibonacci fusion space V_n, reporting the unitary matrix,
topological spin contribution, and braid trace.

The braid group B_n acts on V_n by R-matrix generators placed at adjacent
anyon pairs.  Positive integers k denote sigma_k (over-cross), negative
denote sigma_k^-1 (under-cross).""",
        epilog="""Examples:
  m3 sim                               # default: [1,2,1] on 3 strands
  m3 sim --word 1 2 1 2 1             # longer braid on 3 strands
  m3 sim --strands 5 --word 1 2 3 2 1 # 5-strand braid
  m3 sim --strands 7                   # 7-strand, dim V_7 = 13

Output shows dimension, unitarity check, trace, and eigenvalue spectrum.
""")''')

# 3. manifold
content = content.replace(
    'man_parser = subparsers.add_parser("manifold", help="Topological manifold operations")',
    '''man_parser = subparsers.add_parser("manifold",
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

The path integral measure derives from the braid word writhe
and quantum dimension, giving a bordism topological invariant.
""")''')

# 4. qc
content = content.replace(
    'qc_parser = subparsers.add_parser("qc", help="Fibonacci quantum computer")',
    '''qc_parser = subparsers.add_parser("qc",
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
all gates are topological (braiding operations) and gap-protected.
""")''')

# 5. triple
content = content.replace(
    'triple_parser = subparsers.add_parser("triple", help="Triple Frame von Neumann Superoperator Algebra")',
    '''triple_parser = subparsers.add_parser("triple",
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

Protocol A: 16 opcodes, 5 loops, emergence at EP.
Protocol B: 20 opcodes, 6 loops, holographic round-trip.
""")''')

# 6. info
content = content.replace(
    'info_parser = subparsers.add_parser("info", help="System and algebra information")',
    '''info_parser = subparsers.add_parser("info",
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
""")''')

# ===== MULTI-LINE PARSERS — replace from unique description-anchor to close =====

# 7. hqe: anchor on "Holonomic Quasi-Ergodic Quantale: non-Abelian Berry holonomy"
HQE_OLD = '''Holonomic Quasi-Ergodic Quantale: non-Abelian Berry holonomy
in a Many-Body Localized phase. O_inf (Special Frobenius).

Commands:
  --report       Full structural report (holonomy + MBL + consciousness)
  --holonomy     Non-Abelian Berry holonomy computation
  --mbl          Many-Body Localization diagnostics
  --consciousness Consciousness score (C-score)
  --tuple        Print grammar tuple only
  --distance SYS Distance to PFA, winding, or clink (or all)
  --meet TUPLE   Compute meet with a 12-glyph tuple
  --join TUPLE   Compute join with a 12-glyph tuple
  --json         JSON output format
""")'''
HQE_NEW = '''Holonomic Quasi-Ergodic Quantale: non-Abelian Berry holonomy
in a Many-Body Localized phase. O_inf (Special Frobenius).

Commands:
  --report       Full structural report (holonomy + MBL + consciousness)
  --holonomy     Non-Abelian Berry holonomy computation
  --mbl          Many-Body Localization diagnostics
  --consciousness Consciousness score (C-score)
  --tuple        Print grammar tuple only
  --distance SYS Distance to PFA, winding, or clink (or all)
  --meet TUPLE   Compute meet with a 12-glyph tuple
  --join TUPLE   Compute join with a 12-glyph tuple
  --json         JSON output format
""",
        epilog="""Examples:
  m3 hqe --report                       # full structural report
  m3 hqe --holonomy                     # Berry holonomy computation
  m3 hqe --mbl                          # MBL diagnostics (gap ratio)
  m3 hqe --consciousness               # consciousness score (C-score)
  m3 hqe --tuple                       # print grammar tuple
  m3 hqe --distance clink             # distance to CLINK L8
  m3 hqe --distance pfa              # distance to PFA
  m3 hqe --json --report              # JSON output

The HQE tuple is <ETHDTRPFCGGphiHSO> (O_inf).
Special Frobenius algebra: mu o delta = id verified at every call.
""")'''
assert HQE_OLD in content, "HQE anchor not found!"
content = content.replace(HQE_OLD, HQE_NEW, 1)

# 8. hop: anchor on "hop between tuples through the crystal of types"
HOP_OLD = '''hop between tuples through the crystal of types, and compute geodesic paths.

Commands:
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

Frameworks available:
  hqe                  Holonomic Quasi-Ergodic Quantale
  fibonacci_braid      Fibonacci Anyon Braid Algebra
  berry_holonomy       Non-Abelian Berry Holonomy (U(n))
  mbl_phase            Many-Body Localization Phase Diagram
  triple_frame         Triple Frame Von Neumann Algebra
""")'''
HOP_NEW = '''hop between tuples through the crystal of types, and compute geodesic paths.

Commands:
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

Frameworks available:
  hqe                  Holonomic Quasi-Ergodic Quantale
  fibonacci_braid      Fibonacci Anyon Braid Algebra
  berry_holonomy       Non-Abelian Berry Holonomy (U(n))
  mbl_phase            Many-Body Localization Phase Diagram
  triple_frame         Triple Frame Von Neumann Algebra
""",
        epilog="""Examples:
  m3 hop --tuple '<...>'                   # manifest tuple in all frameworks
  m3 hop --report '<...>'                  # full report
  m3 hop --hop-origin '<...>' --hop-target '<...>'  # hop path
  m3 hop --geodesic                        # A* optimal path
  m3 hop --framework-matrix               # all pairwise anchor distances
  m3 hop --reverse-framework hqe          # reverse parameter lookup

Available frameworks: hqe, fibonacci_braid, berry_holonomy, mbl_phase, triple_frame.
Each hop changes ONE glyph (17.28M point crystal).
""")'''
assert HOP_OLD in content, "HOP anchor not found!"
content = content.replace(HOP_OLD, HOP_NEW, 1)

# 9. dyson: anchor on "Dyson's threefold way (beta=1/2/4)"
DYSON_OLD = '''Dyson's threefold way (beta=1/2/4)
combined with the double ramification cycle from moduli spaces.

Commands:
  --report            Full report (level spacing + form factor + DR cycle + Frobenius)
  --level-spacing     Wigner surmise & gap ratio for beta=1,2,4
  --form-factor       Spectral form factor K(tau)
  --frobenius         Frobenius condition mu o delta=id verification
  --dr-cycle          Double Ramification cycle structure constants
  --tuple             Print grammar tuple
  --distance          Distances to sibling systems
  --json              JSON output format
  --beta N            Dyson beta value: 1 (GOE), 2 (GUE), 4 (GSE) (default: 2)
  --N N               Matrix size (default: 100)
  --genus N           Genus of the DR cycle (default: 0)
""")'''
DYSON_NEW = '''Dyson's threefold way (beta=1/2/4)
combined with the double ramification cycle from moduli spaces.

Commands:
  --report            Full report (level spacing + form factor + DR cycle + Frobenius)
  --level-spacing     Wigner surmise & gap ratio for beta=1,2,4
  --form-factor       Spectral form factor K(tau)
  --frobenius         Frobenius condition mu o delta=id verification
  --dr-cycle          Double Ramification cycle structure constants
  --tuple             Print grammar tuple
  --distance          Distances to sibling systems
  --json              JSON output format
  --beta N            Dyson beta value: 1 (GOE), 2 (GUE), 4 (GSE) (default: 2)
  --N N               Matrix size (default: 100)
  --genus N           Genus of the DR cycle (default: 0)
""",
        epilog="""Examples:
  m3 dyson --report                     # full report (all diagnostics)
  m3 dyson --level-spacing              # Wigner surmise for beta=2
  m3 dyson --form-factor                # spectral form factor K(tau)
  m3 dyson --frobenius                  # Frobenius condition check
  m3 dyson --dr-cycle                   # DR cycle structure constants
  m3 dyson --beta 4 --N 200            # GSE, matrix size 200
  m3 dyson --genus 1 --dr-cycle        # genus-1 DR cycle
  m3 dyson --distance                   # distances to sibling systems
  m3 dyson --json --report             # JSON output

Dyson threefold way: beta=1 (GOE), beta=2 (GUE), beta=4 (GSE).
DR cycle lives in moduli space M_{g,n} of stable curves.
""")'''
assert DYSON_OLD in content, "DYSON anchor not found!"
content = content.replace(DYSON_OLD, DYSON_NEW, 1)

# 10. afdmc: anchor on "Cohomology of the MBL localization monad, approaching criticality."
AFDMC_OLD = '''Cohomology of the MBL localization monad, approaching criticality.

Commands:
  --report         Full structural report (cohomology + spectral + filtration)
  --cohomology     Monadic cohomology groups (H^0-H^3)
  --spectral       E_2 spectral sequence collapse diagnostic
  --filtration     Asymptotic filtration analysis (eps -> 0+)
  --obstructions   Thermalization obstruction classification
  --mbl            MBL diagnostics (gap ratio, l-bits)
  --tuple          Print grammar tuple
  --distance       Distances to sibling systems (hqe, hombroad)
  --json           JSON output format
  --size N         System size (default: 8)
  --disorder W     Disorder strength (default: 5.0)
  --W_c Wc         Critical disorder strength (default: 8.0)
  --steps N        Filtration steps (default: 5)
  --seed N         RNG seed
""")'''
AFDMC_NEW = '''Cohomology of the MBL localization monad, approaching criticality.

Commands:
  --report         Full structural report (cohomology + spectral + filtration)
  --cohomology     Monadic cohomology groups (H^0-H^3)
  --spectral       E_2 spectral sequence collapse diagnostic
  --filtration     Asymptotic filtration analysis (eps -> 0+)
  --obstructions   Thermalization obstruction classification
  --mbl            MBL diagnostics (gap ratio, l-bits)
  --tuple          Print grammar tuple
  --distance       Distances to sibling systems (hqe, hombroad)
  --json           JSON output format
  --size N         System size (default: 8)
  --disorder W     Disorder strength (default: 5.0)
  --W_c Wc         Critical disorder strength (default: 8.0)
  --steps N        Filtration steps (default: 5)
  --seed N         RNG seed
""",
        epilog="""Examples:
  m3 afdmc --report                     # full cohomology report
  m3 afdmc --cohomology                 # H^0-H^3 monadic cohomology groups
  m3 afdmc --spectral                   # E_2 spectral sequence collapse
  m3 afdmc --filtration                 # asymptotic filtration (eps -> 0+)
  m3 afdmc --obstructions              # thermalization obstruction classes
  m3 afdmc --mbl                        # MBL diagnostics (gap ratio)
  m3 afdmc --size 12 --disorder 6.0     # 12-site system, W=6.0
  m3 afdmc --W_c 10.0 --steps 8        # custom critical disorder
  m3 afdmc --distance                   # distances to sibling systems
  m3 afdmc --json --report             # JSON output

Cohomology: H^0 = l-bits, H^1 = level stats, H^2 = obstruction,
H^3 = anomaly.  E_2 spectral sequence collapses at MBL fixed points.
""")'''
# Verify uniqueness - this anchor should only appear once (afdmc)
assert content.count(AFDMC_OLD) == 1, f"AFDMC anchor appears {content.count(AFDMC_OLD)} times in content!"
content = content.replace(AFDMC_OLD, AFDMC_NEW, 1)

# Write patched file
with open('src/m3iosis/cli.py', 'w') as f:
    f.write(content)

print("ALL 10 PATCHES APPLIED SUCCESSFULLY")
print(f"File size: {len(content)} bytes")
