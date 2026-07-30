#!/usr/bin/env python3
"""
M3Iosis CLI — Meta-Mathematical Morphogenesis command-line interface.

Commands:
  fib       Fibonacci anyon algebra and operational tools
  manifold  Topological manifold operations
  sim       Braid simulation
  info      System and algebra information

Author: Math@perator (Lando(odot)perator team)
"""
import argparse
import sys
from m3iosis.fibonacci_quantum_computer import quantum_computer_cli
from m3iosis.fibonacci_anyon_tool import (
    FibonacciAnyonAlgebra,
    FibonacciBraidSimulator,
    FibonacciQuantumComputer,
    FibonacciDiagram,
    fibonacci_tool_main,
)
from m3iosis.simulation import simulate_braid
from m3iosis.manifold import FibonacciManifold
from m3iosis.fibonacci_anyon_algebra import (
    fusion_space_dimension, fusion_states, summary,
    PHI, D, THETA_TAU, central_charge,
)
from m3iosis.pericyclic_frobenoid import pf_cli
from m3iosis.pericyclic_compiler import pqc_cli


def fib_command(args):
    """Handle the 'fib' subcommand with all operational tools."""
    if args.diag:
        sim = FibonacciBraidSimulator()
        print(sim.run_diagnostic())
        return

    if args.fusion:
        alg = FibonacciAnyonAlgebra()
        a, b = args.fusion
        outcomes = alg.fuse(a, b)
        print(f"{a} x {b} = {' + '.join(outcomes) if outcomes else '0'}")
        for c in outcomes:
            r = alg.r_move(a, b, c)
            print(f"  R^{{{a},{b}}}_{{{c}}} = {r:.6f}  (|R| = {abs(r):.6f})")
        return

    if args.braid:
        n = args.braid[0]
        word = args.braid[1:]
        sim = FibonacciBraidSimulator()
        stats = sim.braid_statistics(n, word)
        print(f"Braid word {word} on {n} strands:")
        print(f"  dim V_{n} = {stats['dimension']}")
        print(f"  Unitary: {stats['is_unitary']}")
        print(f"  Trace: {stats['trace']:.6f}")
        print(f"  Eigenvalues: {', '.join(f'{e:.4f}' for e in stats['eigenvalues'])}")
        return

    if args.jones:
        n = args.jones[0]
        word = args.jones[1:]
        qec = FibonacciQuantumComputer()
        val = qec.jones_polynomial(n, word)
        print(f"Jones polynomial (normalized) for braid {word} on {n} strands:")
        print(f"  V = {val:.6f}")
        return

    if args.gate_info:
        qec = FibonacciQuantumComputer()
        report = qec.gate_set_report()
        print(f"Universal: {report['universal']}")
        print(f"Available qubit counts (n, dim, qubits):")
        for n_val, d, q in report["available_qubit_counts"]:
            print(f"  n={n_val}: dim={d}, qubits={q}")
        print(f"Note: {report['note']}")
        return

    if args.tree:
        n = args.tree
        print(FibonacciDiagram.fusion_tree_ascii(n))
        return

    if args.dimension:
        n = args.dimension
        d = fusion_space_dimension(n)
        print(f"dim V_{n} = {d}  (= Fibonacci F_{n-1})")
        return

    if args.summary:
        rep = summary()
        print("=" * 60)
        print("FIBONACCI ANYON ALGEBRA -- self-consistency report")
        print("=" * 60)
        for k, v in rep.items():
            print(f"  {k:28s}: {v}")
        return

    if args.sim:
        simulate_braid(args.word, getattr(args, "strands", 3))
        return

    if args.manifold:
        man = FibonacciManifold()
        print(f"det(S) [constant, = -1]: {man.s_matrix_determinant()}")
        print(f"Path Integral Measure: {man.path_integral(args.word, 3)}")
        print(f"Braid center word: {man.braid_center(3)}")
        return

    # Default: print help. The parser is local to main(), so reaching it by
    # name here raised NameError on every flagless `cli.py fib`; it arrives on
    # args instead.
    parser = getattr(args, "_parser", None)
    if parser is not None:
        parser.print_help()


def main():
    parser = argparse.ArgumentParser(
        description="M3Iosis Advanced CLI — Meta-Mathematical Morphogenesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- fib subcommand ---
    fib_parser = subparsers.add_parser("fib", help="Fibonacci anyon algebra tools")
    fib_parser.add_argument("--diag", action="store_true",
                            help="Run algebraic kernel verification")
    fib_parser.add_argument("--fusion", nargs=2, metavar=("A", "B"),
                            help="Fuse two anyons (e.g. --fusion tau tau)")
    fib_parser.add_argument("--braid", nargs="+", type=int, metavar=("N", "GENS..."),
                            help="Evaluate braid word on N strands (e.g. --braid 3 1 2 1)")
    fib_parser.add_argument("--jones", nargs="+", type=int, metavar=("N", "GENS..."),
                            help="Compute Jones polynomial from braid word")
    fib_parser.add_argument("--gate-info", action="store_true",
                            help="Report on quantum computational universality")
    fib_parser.add_argument("--tree", type=int, metavar="N",
                            help="Show fusion tree basis for N anyons")
    fib_parser.add_argument("--dimension", type=int, metavar="N",
                            help="Fusion space dimension for N anyons")
    fib_parser.add_argument("--summary", action="store_true",
                            help="Full self-consistency summary")
    fib_parser.add_argument("--sim", action="store_true",
                            help="Simulate a braid sequence")
    fib_parser.add_argument("--manifold", action="store_true",
                            help="Topological manifold operations")
    fib_parser.add_argument("--word", type=int, nargs="+", default=[1, 2, 1],
                            help="Braid word for simulation (default: [1,2,1])")
    fib_parser.set_defaults(func=fib_command, _parser=fib_parser)

    # --- sim subcommand ---
    sim_parser = subparsers.add_parser("sim", help="Braid simulation")
    sim_parser.add_argument("--word", type=int, nargs="+", default=[1, 2, 1],
                            help="Braid word to simulate")
    sim_parser.add_argument("--strands", type=int, default=3,
                            help="Number of strands")
    sim_parser.set_defaults(func=lambda a: simulate_braid(a.word, a.strands))

    # --- manifold subcommand ---
    man_parser = subparsers.add_parser("manifold", help="Topological manifold operations")
    man_parser.add_argument("--word", type=int, nargs="+", default=[1, 2, 1],
                            help="Braid word for path integral")
    man_parser.add_argument("--strands", type=int, default=3,
                            help="Number of strands")
    man_parser.set_defaults(
        func=lambda a: (
            print(f"det(S) [constant, = -1]: {FibonacciManifold().s_matrix_determinant()}"),
            print(f"Path Integral Measure: {FibonacciManifold().path_integral(a.word, a.strands)}"),
            print(f"Braid center word: {FibonacciManifold().braid_center(a.strands)}"),
        )
    )

    # --- qc subcommand ---
    qc_parser = subparsers.add_parser("qc", help="Fibonacci quantum computer")
    qc_parser.add_argument("--verify", action="store_true",
                            help="Run full verification suite")
    qc_parser.add_argument("--approx-h", action="store_true",
                            help="Approximate Hadamard gate")
    qc_parser.add_argument("--approx-t", action="store_true",
                            help="Approximate T gate")
    qc_parser.add_argument("--circuit", nargs="+", choices=["H", "T", "X", "S"],
                            help="Build circuit with specified gates")
    qc_parser.add_argument("--gate-stats", action="store_true",
                            help="Report on gate set generation")
    qc_parser.add_argument("--available", action="store_true",
                            help="Show available qubit encodings")
    qc_parser.add_argument("--depth", type=int, default=5,
                            help="Maximum braid word depth")
    def run_qc(args):
        # Re-parse args for the quantum computer CLI
        import sys as _sys
        # Build a new argv without the 'qc' subcommand
        remaining = [x for x in _sys.argv[2:] if x != 'qc']
        _sys.argv = ['fib_qc'] + remaining
        quantum_computer_cli()

    qc_parser.set_defaults(func=run_qc)


    # --- triple subcommand ---
    triple_parser = subparsers.add_parser("triple", help="Triple Frame von Neumann Superoperator Algebra")
    triple_parser.add_argument("--report", action="store_true",
                               help="Full structural report")
    triple_parser.add_argument("--expand", type=str, metavar="TYPE",
                               help="Expand a Shavian type or primitive (e.g. sure, Ħ, monad)")
    triple_parser.add_argument("--word", type=str, choices=["A", "B", "root", "full"],
                               help="Print glyph word for protocol variant")
    triple_parser.add_argument("--verify", nargs="?", const="all", metavar="TYPE",
                               help="Verify Frobenius closure (all or specific type)")
    triple_parser.add_argument("--types", action="store_true",
                               help="Type expansion table")
    triple_parser.add_argument("--cycle", action="store_true",
                               help="IMASM tuple↔word round-trip")
    triple_parser.add_argument("--path", action="store_true",
                               help="Edit distance between Protocol A and B")
    triple_parser.add_argument("--bridge", action="store_true",
                               help="Triple frame ↔ Fibonacci manifold bridge")
    triple_parser.add_argument("--check", type=str, metavar="WORD",
                               help="Check Frobenius closure of a custom glyph word")
    def run_triple(args):
        from m3iosis.triple_frame import TripleFrameAlgebra, TripleFrameManifold
        tf = TripleFrameAlgebra()
        if args.report:
            print(tf.protocol_report())
        elif args.expand:
            tp = tf.expand(args.expand)
            print(f"{tp.primitive_axis}={tp.value_glyph}  →  {tp.shavian}")
            print(f"  Word:  {tp.word}")
            print(f"  Ops:   {tp.n_ops}")
            print(f"  ρ:     {tp.rho}")
            print(f"  Read:  {tp.domain_reading}")
        elif args.word:
            if args.word == "full":
                w = tf.full_word()
                print(f"Full word ({len(w)} glyphs):")
                print(w)
            elif args.word == "root":
                from m3iosis.triple_frame import ROOT_WORD
                print(''.join(oc.glyph for oc in ROOT_WORD))
            else:
                print(tf.protocol_word(args.word))
        elif args.verify is not None:
            if args.verify == "all":
                results = tf.verify_all_types()
                for name, r in results.items():
                    status = "✓" if r["closed"] else "✗"
                    print(f"  {status} {name:<8} ρ={r['rho']:<8} {r['verdict']}")
            else:
                result = tf.check_frobenius(tf.expand(args.verify).opcodes)
                for k, v in result.items():
                    print(f"  {k}: {v}")
        elif args.types:
            print(tf.type_table())
        elif args.cycle:
            result = tf.imasm_cycle()
            print(f"IMASM cycle: {result['n_exact']}/{result['total']} exact")
            print(f"  Ambiguous: {result['n_ambiguous']} (Ř: ear/tot)")
            print(f"  {result['note']}")
        elif args.path:
            result = tf.protocol_path()
            print(f"Protocol A → B: {result['distance']} edits")
            print(f"  A: {result['protocol_a']}")
            print(f"  B: {result['protocol_b']}")
            print(f"  {result['note']}")
        elif args.bridge:
            tfb = TripleFrameManifold()
            print(tfb.bridge_report())
        elif args.check:
            from m3iosis.triple_frame import Opcode
            word = [Opcode.from_glyph(g) for g in args.check]
            for k, v in tf.check_frobenius(word).items():
                print(f"  {k}: {v}")
        else:
            triple_parser.print_help()

    triple_parser.set_defaults(func=run_triple)


    # --- hqe subcommand ---
    hqe_parser = subparsers.add_parser("hqe", 
        help="Holonomic Quasi-Ergodic Quantale -- MBL holonomy algebra",
        description="""Holonomic Quasi-Ergodic Quantale: non-Abelian Berry holonomy
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
""")

    hqe_parser.add_argument("--report", action="store_true",
                            help="Full structural report")
    hqe_parser.add_argument("--holonomy", action="store_true",
                            help="Non-Abelian Berry holonomy computation")
    hqe_parser.add_argument("--mbl", action="store_true",
                            help="Many-Body Localization diagnostics")
    hqe_parser.add_argument("--consciousness", action="store_true",
                            help="Consciousness score (C-score)")
    hqe_parser.add_argument("--tuple", action="store_true",
                            help="Print grammar tuple")
    hqe_parser.add_argument("--json", action="store_true",
                            help="JSON output format")
    hqe_parser.add_argument("--distance", type=str, nargs="?", const="all", metavar="SYS",
                            help="Distance to system: pfa, winding, clink, or all")
    hqe_parser.add_argument("--meet", type=str, metavar="TUPLE",
                            help="Compute meet with a 12-glyph tuple")
    hqe_parser.add_argument("--join", type=str, metavar="TUPLE",
                            help="Compute join with a 12-glyph tuple")
    def run_hqe(args):
        from m3iosis.holonomic_quantale import hqe_main
        hqe_args = {}
        if args.report: hqe_args["report"] = True
        if args.holonomy: hqe_args["holonomy"] = True
        if args.mbl: hqe_args["mbl"] = True
        if args.consciousness: hqe_args["consciousness"] = True
        if args.tuple: hqe_args["tuple"] = True
        if args.json: hqe_args["json"] = True
        if args.distance: hqe_args["distance"] = args.distance
        if args.meet: hqe_args["meet"] = args.meet
        if args.join: hqe_args["join"] = args.join
        print(hqe_main(hqe_args))

    hqe_parser.set_defaults(func=run_hqe)


    # --- braid-grammar subcommand ---
    bg_parser = subparsers.add_parser("braid-grammar", 
        help="Braid Grammar Bridge — Fibonacci braid words to grammar tuples",
        description="""Map a Fibonacci anyon braid word to its Imscribing Grammar tuple.

Takes a braid word as signed Artin generators (positive = sigma_k, negative = sigma_k^{-1})
and evaluates it on the n-strand Fibonacci braid group representation in the fusion space
V_n = Hom(tau^n, 1).  Extracts topological invariants (writhe, braid trace, eigenvalues,
Jones polynomial, fusion space dimension) and maps each to a grammar primitive value.

Grammar primitive mapping:
  0369 Dimension (D)     <- fusion space dimension
  028C Topology (T)       <- braid isotopy class (crossing count)
  01D9 Coupling (R)       <- unitary braid group representation
  0131 Parity (P)         <- topological spin / eigenvalue spectrum
  0022 Fidelity (F)       <- Jones polynomial evaluation
  007B Kinetics (K)       <- braid word complexity
  0154 Cardinality (G)    <- number of anyons
  0060 Composition (Gm)   <- generator multiplication order
  2299 Criticality (phi)  <- Frobenius closure (mu∘delta = id)
  012B Chirality (H)      <- writhe / signed crossing sum
  0159 Stoichiometry (S)  <- fusion outcome multiplicity
  2126 Winding (Omega)    <- total eigenvalue winding

Output: 12-glyph tuple ⟨DTRPFCGGphiHSO⟩ and Frobenius closure verdict.
""",
        epilog="""Examples:
  m3 braid-grammar 1 2 1                     # Yang-Baxter braid on 4 strands
  m3 braid-grammar -1 -2 -1                  # Inverse Yang-Baxter
  m3 braid-grammar 1 2 1 2 1                # Longer braid word
  m3 braid-grammar --strands 7 1 2 3 2 1    # 7 strands, dim V_7 = 8 (3 qubits)
  m3 braid-grammar                           # empty word: identity braid

Frobenius closure indicates whether the braid word's unitary representation
satisfies mu∘delta = id (unitary + real trace).  When CLOSED the braid is
self-adjoint in the statistical sense; when OPEN the braid carries non-trivial
topological winding.
""")
    bg_parser.add_argument("word", type=int, nargs="+",
                           help="Braid word as signed Artin generators")
    bg_parser.add_argument("--strands", "-n", type=int, default=4,
                           help="Number of strands (default: 4, dim V_4 = 2)")
    bg_parser.set_defaults(
        func=lambda a: (
            __import__("m3iosis.braid_grammar_bridge", fromlist=["BraidGrammarAnalyzer"]).BraidGrammarAnalyzer
            .print_report(
                __import__("m3iosis.braid_grammar_bridge", fromlist=["BraidGrammarAnalyzer"]).BraidGrammarAnalyzer
                .analyze_word(a.word, a.strands)
            )
        )
    )


    # --- hop subcommand ---
    hop_parser = subparsers.add_parser("hop", 
        help="Universe Hopping Engine — cross-framework transport",
        description="""Universe Hopping Engine: manifest tuples in all frameworks,
hop between tuples through the crystal of types, and compute geodesic paths.

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
  --json                   Output as JSON

Frameworks available:
  hqe                  Holonomic Quasi-Ergodic Quantale
  fibonacci_braid      Fibonacci Anyon Braid Algebra
  berry_holonomy       Non-Abelian Berry Holonomy (U(n))
  mbl_phase            Many-Body Localization Phase Diagram
  triple_frame         Triple Frame Von Neumann Algebra
""")
    hop_parser.add_argument("--tuple", type=str, metavar="TUPLE",
                            help="Manifest a tuple in all frameworks")
    hop_parser.add_argument("--report", type=str, metavar="TUPLE",
                            help="Full universe-hopping report")
    hop_parser.add_argument("--hop-origin", type=str, metavar="TUPLE",
                            help="Start tuple for hopping")
    hop_parser.add_argument("--hop-target", type=str, metavar="TUPLE",
                            help="Target tuple for hopping")
    hop_parser.add_argument("--geodesic", action="store_true",
                            help="Use A* for exact minimal-cost path")
    hop_parser.add_argument("--compare-a", type=str, metavar="TUPLE",
                            help="First tuple for comparison")
    hop_parser.add_argument("--compare-b", type=str, metavar="TUPLE",
                            help="Second tuple for comparison")
    hop_parser.add_argument("--framework-matrix", action="store_true",
                            help="All pairwise distances between anchors")
    hop_parser.add_argument("--reverse-framework", type=str,
                            help="Framework for reverse parameter lookup")
    hop_parser.add_argument("--reverse-params", type=str, default="{}",
                            help="Target parameters as JSON")
    hop_parser.add_argument("--json", action="store_true",
                            help="Output as JSON")
    def run_hop(args):
        from m3iosis.universe_hopper import universe_hopper_main
        hop_args = {}
        if args.tuple: hop_args["tuple"] = args.tuple
        if args.report: hop_args["report"] = args.report
        if args.hop_origin: hop_args["hop_origin"] = args.hop_origin
        if args.hop_target: hop_args["hop_target"] = args.hop_target
        if args.geodesic: hop_args["geodesic"] = True
        if args.compare_a: hop_args["compare_a"] = args.compare_a
        if args.compare_b: hop_args["compare_b"] = args.compare_b
        if args.framework_matrix: hop_args["framework_matrix"] = True
        if args.reverse_framework: hop_args["reverse_framework"] = args.reverse_framework
        if args.reverse_params:
            import json
            try:
                hop_args["reverse_params"] = json.loads(args.reverse_params)
            except:
                hop_args["reverse_params"] = {}
        if args.json: hop_args["json"] = True
        print(universe_hopper_main(hop_args))

    hop_parser.set_defaults(func=run_hop)
# -*- M3Iosis CLI: gematria subcommand registration -*-
# This is the gematria subcommand block to be inserted into cli.py
# after the hop subcommand and before the info subcommand.

    # --- dyson subcommand ---
    dyson_parser = subparsers.add_parser("dyson",
        help="Double-Ramified Dyson Algebra — Dyson β-ensemble + DR cycle tool",
        description="""Double-Ramified Dyson Algebra (DRDA): Dyson's threefold way (β=1/2/4)
combined with the double ramification cycle from moduli spaces.

Commands:
  --report            Full report (level spacing + form factor + DR cycle + Frobenius)
  --level-spacing     Wigner surmise & gap ratio for β=1,2,4
  --form-factor       Spectral form factor K(τ)
  --frobenius         Frobenius condition μ∘δ=id verification
  --dr-cycle          Double Ramification cycle structure constants
  --tuple             Print grammar tuple
  --distance          Distances to sibling systems
  --json              JSON output format
  --beta N            Dyson β value: 1 (GOE), 2 (GUE), 4 (GSE) (default: 2)
  --N N               Matrix size (default: 100)
  --genus N           Genus of the DR cycle (default: 0)
""")

    dyson_parser.add_argument("--report", action="store_true")
    dyson_parser.add_argument("--level-spacing", action="store_true")
    dyson_parser.add_argument("--form-factor", action="store_true")
    dyson_parser.add_argument("--frobenius", action="store_true")
    dyson_parser.add_argument("--dr-cycle", action="store_true")
    dyson_parser.add_argument("--tuple", action="store_true")
    dyson_parser.add_argument("--json", action="store_true")
    dyson_parser.add_argument("--beta", type=int, default=2, choices=[1,2,4])
    dyson_parser.add_argument("--N", type=int, default=100)
    dyson_parser.add_argument("--genus", type=int, default=0)
    dyson_parser.add_argument("--distance", type=str, nargs="?", const="all")

    def run_dyson(args):
        from m3iosis.dyson_algebra import drda_cli as _drda_cli
        _drda_cli(args)

    dyson_parser.set_defaults(func=run_dyson)

    # --- afdmc subcommand ---
    afdmc_parser = subparsers.add_parser("afdmc",
        help="Asymptotic Frozen-Disordered Monadic Cohomologies — MBL cohomology tool",
        description="""Asymptotic Frozen-Disordered Monadic Cohomologies (AFDMC):
Cohomology of the MBL localization monad, approaching criticality.

Commands:
  --report         Full structural report (cohomology + spectral + filtration)
  --cohomology     Monadic cohomology groups (H⁰-H³)
  --spectral       E₂ spectral sequence collapse diagnostic
  --filtration     Asymptotic filtration analysis (eps → 0⁺)
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
""")

    afdmc_parser.add_argument("--report", action="store_true",
                              help="Full structural report")
    afdmc_parser.add_argument("--cohomology", action="store_true",
                              help="Monadic cohomology groups (H⁰-H³)")
    afdmc_parser.add_argument("--spectral", action="store_true",
                              help="E₂ spectral sequence collapse diagnostic")
    afdmc_parser.add_argument("--filtration", action="store_true",
                              help="Asymptotic filtration analysis")
    afdmc_parser.add_argument("--obstructions", action="store_true",
                              help="Thermalization obstruction classification")
    afdmc_parser.add_argument("--mbl", action="store_true",
                              help="MBL diagnostics (gap ratio, l-bits)")
    afdmc_parser.add_argument("--tuple", action="store_true",
                              help="Print grammar tuple")
    afdmc_parser.add_argument("--json", action="store_true",
                              help="JSON output format")
    afdmc_parser.add_argument("--size", type=int, default=8,
                              help="System size")
    afdmc_parser.add_argument("--disorder", type=float, default=5.0,
                              help="Disorder strength")
    afdmc_parser.add_argument("--W_c", type=float, default=8.0,
                              help="Critical disorder strength")
    afdmc_parser.add_argument("--steps", type=int, default=5,
                              help="Filtration steps")
    afdmc_parser.add_argument("--distance", type=str, nargs="?", const="all",
                              metavar="SYS", help="Distance to sibling systems")
    afdmc_parser.add_argument("--seed", type=int, default=None,
                              help="RNG seed")

    def run_afdmc(args):
        from m3iosis.afdmc import afdmc_cli as _afdmc_cli
        _afdmc_cli(args)

    afdmc_parser.set_defaults(func=run_afdmc)

    # --- troq subcommand ---
    troq_parser = subparsers.add_parser("troq",
        help="Triple-Ramified Ouroboric Quantale — TROQ tool",
        description="""Triple-Ramified Ouroboric Quantale (TROQ): Q_A ≅ Q_B ≅ Q_C
with triangular identity γ∘β∘α=id, ouroboric condition Q ≅ End(Q),
and Frobenius closure μ∘δ=id.  Tuple: ⟨𐑦𐑸𐑽𐑹𐑐𐑧𐑔𐑝⊙𐑖𐑕𐑭⟩ (O_∞).

Commands:
  --report            Full structural report
  --short             Short summary
  --frames            Q_A, Q_B, Q_C comparison
  --triangular        Triangular identity verification
  --ouroboric         Ouroboric condition
  --frobenius         Frobenius closure
  --ladder            Distance ladder to sibling systems
  --verify            Run all verifications
  --table             Primitive expansion table
  --expand AXIS       Expand a primitive axis
  --distance TUPLE    Distance to arbitrary tuple
  --tensor TUPLE      TROQ ⊗ other
  --meet TUPLE        TROQ ⊓ other
  --join TUPLE        TROQ ⊔ other
  --json REPORT       JSON output for a specific report
""")

    troq_parser.add_argument("--report", action="store_true",
                              help="Full structural report")
    troq_parser.add_argument("--short", action="store_true",
                              help="Short summary")
    troq_parser.add_argument("--frames", action="store_true",
                              help="Q_A, Q_B, Q_C comparison")
    troq_parser.add_argument("--triangular", action="store_true",
                              help="Triangular identity verification")
    troq_parser.add_argument("--ouroboric", action="store_true",
                              help="Ouroboric condition verification")
    troq_parser.add_argument("--frobenius", action="store_true",
                              help="Frobenius closure verification")
    troq_parser.add_argument("--ladder", action="store_true",
                              help="Distance ladder to sibling systems")
    troq_parser.add_argument("--verify", action="store_true",
                              help="Run all verifications")
    troq_parser.add_argument("--table", action="store_true",
                              help="Primitive expansion table")
    troq_parser.add_argument("--expand", type=str, metavar="AXIS",
                              help="Expand a primitive axis (e.g. Ð, Ř, Φ)")
    troq_parser.add_argument("--distance", type=str, metavar="TUPLE",
                              help="Distance to arbitrary 12-glyph tuple")
    troq_parser.add_argument("--tensor", type=str, metavar="TUPLE",
                              help="Compute TROQ ⊗ other")
    troq_parser.add_argument("--meet", type=str, metavar="TUPLE",
                              help="Compute TROQ ⊓ other")
    troq_parser.add_argument("--join", type=str, metavar="TUPLE",
                              help="Compute TROQ ⊔ other")
    troq_parser.add_argument("--json", type=str, metavar="REPORT",
                              help="JSON output: triangular, ouroboric, frobenius, frames, ladder")

    def run_troq(args):
        from m3iosis.troq import TROQAlgebra
        import json as _json
        troq = TROQAlgebra()

        if args.report:
            print(troq.report())
        elif args.short:
            print(troq.short_report())
        elif args.frames:
            frames = troq.three_frames()
            print(f"Q_A = {frames['Q_A']}")
            print(f"Q_B = {frames['Q_B']}")
            print(f"Q_C = {frames['Q_C']}")
            print(f"All identical: {frames['all_identical']}")
        elif args.triangular:
            result = troq.triangular_identity()
            print(f"Triangular identity: {result['holds']}")
            print(f"  troq⊗troq⊗troq = {result['triple_tensor']}")
        elif args.ouroboric:
            result = troq.ouroboric_condition()
            print(f"Ouroboric condition: {result['holds']}")
            print(f"  troq ⊗ troq = {result['self_tensor']}")
            print(f"  Cardinal: Γ={result['granularity']}")
        elif args.frobenius:
            result = troq.frobenius_closure()
            print(f"Frobenius closure: {result['closed']} ({result['verdict']})")
            print(f"  pol={result['pol']}, crit={result['crit']}")
            print(f"  fused = {result['fused']}")
        elif args.ladder:
            result = troq.distance_ladder()
            print(f"Distance ladder from TROQ:")
            for sib in result["siblings"]:
                print(f"  → {sib['name']:<15}  hamming={sib['hamming_distance']}  weighted={sib['weighted_distance']}")
        elif args.verify:
            tri = troq.triangular_identity()
            ouro = troq.ouroboric_condition()
            frob = troq.frobenius_closure()
            all_pass = tri["holds"] and ouro["holds"] and frob["closed"]
            print(f"TROQ Verification: {'✓ ALL PASS' if all_pass else '✗ FAILURES'}")
            print(f"  Triangular (γ∘β∘α=id): {'✓' if tri['holds'] else '✗'}")
            print(f"  Ouroboric (Q≅End(Q)):  {'✓' if ouro['holds'] else '✗'}")
            print(f"  Frobenius (μ∘δ=id):    {'✓' if frob['closed'] else '✗'}")
        elif args.table:
            print(troq.primitive_table())
        elif args.expand:
            try:
                result = troq.expand_primitive(args.expand)
                print(f"{result['axis']} = {result['glyph']} → {result['shavian']}")
                print(f"  {result['domain_reading']}")
            except KeyError as e:
                print(f"Error: {e}")
        elif args.distance:
            result = troq.distance_to(args.distance)
            print(f"TROQ → custom:")
            print(f"  hamming: {result['hamming_distance']}  weighted: {result['weighted_distance']}")
            for s, a, b in result["mismatches"]:
                print(f"    {s}: {a} → {b}")
        elif args.tensor:
            result = troq.tensor_with(args.tensor)
            print(f"TROQ ⊗ other = {result['result']}")
            print(f"  equals TROQ: {result['equals_troq']}")
        elif args.meet:
            result = troq.meet_with(args.meet)
            print(f"TROQ ⊓ other = {result['result']}")
            print(f"  equals TROQ: {result['equals_troq']}")
        elif args.join:
            result = troq.join_with(args.join)
            print(f"TROQ ⊔ other = {result['result']}")
            print(f"  equals TROQ: {result['equals_troq']}")
        elif args.json:
            report_type = args.json
            if report_type == "triangular":
                print(_json.dumps(troq.triangular_identity(), indent=2, ensure_ascii=False))
            elif report_type == "ouroboric":
                print(_json.dumps(troq.ouroboric_condition(), indent=2, ensure_ascii=False))
            elif report_type == "frobenius":
                print(_json.dumps(troq.frobenius_closure(), indent=2, ensure_ascii=False))
            elif report_type == "frames":
                print(_json.dumps(troq.three_frames(), indent=2, ensure_ascii=False))
            elif report_type == "ladder":
                print(_json.dumps(troq.distance_ladder(), indent=2, ensure_ascii=False))
            else:
                print(f"Unknown report: {report_type}")
        else:
            print(troq.short_report())

    troq_parser.set_defaults(func=run_troq)

    # --- gematria subcommand ---
    gematria_parser = subparsers.add_parser("gematria",
        help="Hypergematria — IMASM word analysis via the lattice flow engine",
        description="""IMASM word hypergematria: 177-dim rotation-invariant signature,
weight flow, banked count, lattice cycle, ring transitions, and steering.

Examples:
  m3 gematria --word '⊢>◇+⊙●=¬⊣' --report   Full analysis of the monad word
  m3 gematria --word '⊢>◇+⊙●=¬⊣' --signature  177-dim signature only
  m3 gematria --word '⊢>◇+⊙●=¬⊣' --flow       Weight flow only
  m3 gematria --word '⊢>◇+⊙●=¬⊣' --cycle      Lattice cycle orbit
  m3 gematria --word '⊢>◇+⊙●=¬⊣' --steer T    Steering to register T
  m3 gematria --word '+⊙●' --json             JSON output

Common words:
  ⊢>◇+⊙●=¬⊣   Monad core (period 9, all landings in T)
  ⊢⊙◇+×⊞●=><¬⊣  Protocol A (emergence/annihilation at EP)
  ⊢⊙◇>+<×●=⊞¬⊣  Protocol B (holographic round-trip)
  ◇>⊙●           Short: open, forward, self-model, fuse (seed test)
""")
    gematria_parser.add_argument("--word", "-w", type=str, required=True,
                                 help="IMASM word as glyphs (e.g. '⊢>◇+⊙●=¬⊣')")
    gematria_parser.add_argument("--report", "-r", action="store_true",
                                 help="Full analysis report")
    gematria_parser.add_argument("--signature", "-s", action="store_true",
                                 help="177-dim rotation-invariant signature")
    gematria_parser.add_argument("--flow", "-f", action="store_true",
                                 help="Weight flow analysis")
    gematria_parser.add_argument("--banked", "-b", action="store_true",
                                 help="Banked count check")
    gematria_parser.add_argument("--cycle", "-c", action="store_true",
                                 help="Lattice cycle orbit")
    gematria_parser.add_argument("--transitions", "-t", action="store_true",
                                 help="Ring transitions (with closing edge)")
    gematria_parser.add_argument("--steer", type=str, nargs="?", const="T",
                                 metavar="TARGET",
                                 help="Steer spectrum to target register (default: T)")
    gematria_parser.add_argument("--depth", type=int, default=1,
                                 help="Steer insertion depth (default: 1)")
    gematria_parser.add_argument("--json", "-j", action="store_true",
                                 help="JSON output format")
    gematria_parser.add_argument("--all", "-a", action="store_true",
                                 help="Run all analyses")

    def run_gematria(args):
        import json as _json
        from m3iosis.gematria import (
            hyper_gematria, weight_flow, banked_count,
            lattice_cycle, ring_transitions, steer, full_report, parse, render_steps
        )

        word = args.word
        if args.all or args.report:
            print(full_report(word))
            return

        results = {}
        did_anything = False

        if args.signature or args.json and not any([args.flow, args.banked, args.cycle, args.transitions, args.steer]):
            did_anything = True
            hg = hyper_gematria(word)
            if hg.get("status") == "error":
                print(f"Error: {hg['error']}")
                return
            results["signature"] = hg
            if not args.json:
                print(f"--- 177-DIM SIGNATURE ---")
                print(f"  Dimension:  {hg['dimension']}")
                print(f"  Invariant:  {hg['every_coordinate_rotation_invariant']}")
                print(f"  Census:     {', '.join(f'{k}:{v}' for k,v in hg['opcode_census'].items())}")
                print(f"  Scalars:    len={hg['scalars']['length']}, depth={hg['scalars']['max_depth']}, "
                      f"ord={hg['scalars']['total_ordinal']}")
                print(f"  Landings:   {', '.join(f'{k}:{v}' for k,v in hg['landing_spectrum'].items())}")

        if args.flow:
            did_anything = True
            wf = weight_flow(word)
            if wf.get("status") == "error":
                print(f"Error: {wf['error']}")
                return
            results["weight_flow"] = wf
            if not args.json:
                print(f"--- WEIGHT FLOW ---")
                print(f"  Final: {wf['final_register']}  deposits={wf['deposits']}  "
                      f"cleared={wf['cleared']}  restored={wf['restored']}  "
                      f"seeded={wf['seeded']}  inert={wf['inert']}")
                print(f"  Surviving: {wf['surviving']}")

        if args.banked:
            did_anything = True
            bc = banked_count(word)
            if bc.get("status") == "error":
                print(f"Error: {bc['error']}")
                return
            results["banked_count"] = bc
            if not args.json:
                print(f"--- BANKED COUNT ---")
                for k, v in bc.items():
                    if k != "status":
                        print(f"  {k}: {v}")

        if args.cycle:
            did_anything = True
            cy = lattice_cycle(word)
            if cy.get("status") == "error":
                print(f"Error: {cy['error']}")
                return
            results["lattice_cycle"] = cy
            if not args.json:
                print(f"--- LATTICE CYCLE ---")
                print(f"  Period: {cy['period']}")
                print(f"  Phase-bearing: {', '.join(cy['phase_bearing'])}")
                print(f"  Landings: {cy['landing_by_cut']}")

        if args.transitions:
            did_anything = True
            tr = ring_transitions(word)
            if tr.get("status") == "error":
                print(f"Error: {tr['error']}")
                return
            results["ring_transitions"] = tr
            if not args.json:
                print(f"--- RING TRANSITIONS ---")
                print(f"  Length: {tr['length']}  ring: {tr['ring_count']}  linear: {tr['linear_count']}")
                print(f"  Wrap: {tr['wrap']}")
                for edge, count in sorted(tr['ring'].items()):
                    print(f"    {edge}: {count}")

        if args.steer is not None:
            did_anything = True
            st = steer(word, target=args.steer, depth=args.depth)
            if st.get("status") == "error":
                print(f"Error: {st['error']}")
                return
            results["steer_spectrum"] = st
            if not args.json:
                print(f"--- STEER SPECTRUM (target={args.steer}, depth={args.depth}) ---")
                b = st.get("base", {})
                print(f"  Base:       {b.get('word','')}  {b.get('spectrum',{})}  share={b.get('share')}")
                print(f"  Searched:   {st.get('searched')}   best share={st.get('best_share')}")
                print(f"  {'word':<18}{'share':>7}{'restored':>10}{'live':>6}  spectrum")
                for h in st.get("best", [])[:5]:
                    live = "no" if h.get("vacuous") else "yes"
                    print(f"  {h['word']:<18}{h['share']:>7}{h['restored']:>10}{live:>6}  {h['spectrum']}")
                print(f"  {st.get('invariant_note','')}")

        if not did_anything:
            # Default: full report
            print(full_report(word))

        if args.json and results:
            print(_json.dumps(results, indent=2, default=str, ensure_ascii=False))

    gematria_parser.set_defaults(func=run_gematria)

    # --- pf subcommand ---
    pf_parser = subparsers.add_parser("pf",
        help="Pericyclic Semiotic Frobenoid — ℂ[ℤ₂] special Frobenius algebra at criticality",
        description="""Pericyclic Semiotic Frobenoid (PF): ℂ[ℤ₂] special Frobenius algebra
with pericyclic crossing topology and μ∘δ=id at conformal fixed point.

Tuple: ⟨𐑦𐑥𐑑𐑹𐑐𐑤𐑔𐑝⊙𐑒𐑙𐑷⟩  (O_∞, Special Frobenius)

Algebra: ℂ[ℤ₂] = ℂ⟨1,g⟩/(g²−1) with pericyclic crossing μ(g⊗g)=1
modeling the [2+2] cycloaddition of two π-systems into σ-framework.

Commands:
  --report            Full structural report (algebra + parity + crossing + pairing + distances)
  --short             Short summary
  --parity            ℤ₂ parity decomposition (even σ-framework / odd π-system)
  --crossing          Pericyclic crossing topology and coproduct structure
  --frobenius         Frobenius condition verification
  --pairing           Frobenius pairing matrix ⟨a,b⟩ = ε(ab)
  --verify            Run all verifications (μ∘δ=id, Frobenius, non-degenerate pairing)
  --tuple             Print grammar tuple
  --distance SYS      Weighted Hamming distance to sibling system ("all" for ladder)
  --json              JSON output format
""")

    pf_parser.add_argument("--report", action="store_true",
                              help="Full structural report")
    pf_parser.add_argument("--short", action="store_true",
                              help="Short summary")
    pf_parser.add_argument("--parity", action="store_true",
                              help="ℤ₂ parity decomposition")
    pf_parser.add_argument("--crossing", action="store_true",
                              help="Pericyclic crossing topology")
    pf_parser.add_argument("--frobenius", action="store_true",
                              help="Frobenius condition verification")
    pf_parser.add_argument("--pairing", action="store_true",
                              help="Frobenius pairing matrix")
    pf_parser.add_argument("--verify", action="store_true",
                              help="Run all verifications")
    pf_parser.add_argument("--tuple", action="store_true",
                              help="Print grammar tuple")
    pf_parser.add_argument("--distance", type=str, nargs="?", const="all",
                              metavar="SYS", help="Distance to sibling system")
    pf_parser.add_argument("--json", action="store_true",
                              help="JSON output format")

    pf_parser.set_defaults(func=pf_cli)





    
    # --- pqc subcommand ---
    pqc_parser = subparsers.add_parser("pqc",
        help="Pericyclic Quantum Compiler — transforms states, computes TQFT, generates protocols",
        description="""Pericyclic Quantum Compiler (PQC): computational engine for the Pericyclic
Semiotic Frobenoid. Evolves quantum states, computes 2D TQFT partition functions,
generates IMASM protocols, compiles Lean proofs, and bridges to SIC-POVM.

Tuple: ⟨𐑦𐑥𐑑𐑹𐑐𐑤𐑔𐑝⊙𐑒𐑙𐑷⟩  (O_∞, Special Frobenius)

Commands:
  --evolve A,B     Evolve state through pericyclic monad (μ, δ, ε, pairing)
  --tqft N         2D TQFT partition function for genus-N surface
  --protocol TYPE  Generate IMASM protocol word (frobenius_cycle, pericyclic_cross, pairing, monad, full)
  --lean [NAME]    Generate Lean proof scaffold
  --sic            Bridge to SIC-POVM fiducial (Belnap B=XZ)
  --compile        Full compilation pipeline (all artifacts)
  --genus N        Genus for TQFT (default: 0)
  --output DIR     Output directory for compilation artifacts
  --interactive    Interactive exploration mode
""")

    pqc_parser.add_argument("--evolve", type=str, metavar="A,B",
                              help="Evolve state (a,b) through pericyclic monad")
    pqc_parser.add_argument("--tqft", type=int, metavar="GENUS",
                              help="2D TQFT partition function for genus")
    pqc_parser.add_argument("--protocol", type=str, metavar="TYPE",
                              help="Generate IMASM protocol (frobenius_cycle, pericyclic_cross, pairing, monad, full)")
    pqc_parser.add_argument("--lean", type=str, nargs="?", const="pf_protocol", metavar="NAME",
                              help="Generate Lean proof scaffold")
    pqc_parser.add_argument("--sic", action="store_true",
                              help="Bridge to SIC-POVM fiducial (Belnap B=XZ)")
    pqc_parser.add_argument("--compile", action="store_true",
                              help="Full compilation pipeline")
    pqc_parser.add_argument("--genus", type=int, default=0,
                              help="Genus for TQFT (default: 0)")
    pqc_parser.add_argument("--output", type=str, default="/tmp/pqc_compile",
                              help="Output directory for compilation artifacts")
    pqc_parser.add_argument("--interactive", action="store_true",
                              help="Interactive exploration mode")

    pqc_parser.set_defaults(func=pqc_cli)

    # --- algebra subcommand ---
    algebra_parser = subparsers.add_parser("algebra", 
        help="Tuple algebra — compute on Imscribing Grammar tuples",
        description="""Real computation for grammar tuple operations: distance, meet, join,
Frobenius tier, consciousness score, ZFC decomposition, retrosynthesis, winding arithmetic.

Operations:
  --tuple TUPLE             12-glyph tuple (with or without ⟨⟩)
  --report                  Full structural analysis (tier, C-score, ZFC, retrosynthesis, distances)
  --decode                  Human-readable tuple decode
  --distance TUPLE_OR_NAME  Distance to another tuple or named reference (grammar, clink, aafa, psfoa)
  --meet TUPLE              Meet (GLB) with another tuple
  --join TUPLE              Join (LUB) with another tuple
  --compare-with SYSTEMS    Comma-separated: aafa,psfoa (for --report)
  --winding                 Compute winding arithmetic
  --winding-of NAME         Named winding: t_gate, s_gate, z_gate, r_tau, quarter, full, jones_root
  --turns TURNS             Rational turns: "1/8", "2/5"
  --angle RADIANS           Angle in radians (converted to turns)
  --power N                 Raise winding to power N
  --json                    JSON output

Examples:
  m3 algebra --tuple ⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑚𐑜⊙𐑫𐑕𐑭⟩ --report
  m3 algebra --tuple ⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑚𐑜⊙𐑫𐑕𐑭⟩ --distance aafa
  m3 algebra --tuple ⟨𐑦𐑸𐑽𐑹𐑐𐑘𐑚𐑜⊙𐑫𐑕𐑭⟩ --meet ⟨𐑦𐑸𐑽𐑹𐑐𐑧𐑔𐑝⊙𐑫𐑕𐑭⟩
  m3 algebra --winding --winding-of t_gate
  m3 algebra --winding --turns 2/5 --power 3
""")
    algebra_parser.add_argument("--tuple", type=str, help="12-glyph tuple")
    algebra_parser.add_argument("--report", action="store_true", help="Full structural analysis")
    algebra_parser.add_argument("--decode", action="store_true", help="Human-readable decode")
    algebra_parser.add_argument("--distance", type=str, help="Tuple or named reference")
    algebra_parser.add_argument("--meet", type=str, help="Tuple for meet (GLB)")
    algebra_parser.add_argument("--join", type=str, help="Tuple for join (LUB)")
    algebra_parser.add_argument("--compare-with", type=str, help="Comma-separated: aafa,psfoa")
    algebra_parser.add_argument("--winding", action="store_true", help="Winding arithmetic")
    algebra_parser.add_argument("--winding-of", type=str, help="Named winding constant")
    algebra_parser.add_argument("--turns", type=str, help="Rational turns e.g. 1/8")
    algebra_parser.add_argument("--angle", type=float, help="Angle in radians")
    algebra_parser.add_argument("--power", type=int, help="Raise winding to power")
    algebra_parser.add_argument("--json", action="store_true", help="JSON output")
    def run_algebra(args):
        from m3iosis.tuple_algebra import tuple_algebra_main
        alg_args = {}
        if args.tuple: alg_args["tuple"] = args.tuple
        if args.report: alg_args["report"] = True
        if args.decode: alg_args["decode"] = True
        if args.distance: alg_args["distance"] = args.distance
        if args.meet: alg_args["meet"] = args.meet
        if args.join: alg_args["join"] = args.join
        if args.compare_with: alg_args["compare_with"] = args.compare_with
        if args.winding: alg_args["winding"] = True
        if args.winding_of: alg_args["winding_of"] = args.winding_of
        if args.turns: alg_args["turns"] = args.turns
        if args.angle is not None: alg_args["angle"] = args.angle
        if args.power is not None: alg_args["power"] = args.power
        if args.json: alg_args["json"] = True
        print(tuple_algebra_main(alg_args))
    algebra_parser.set_defaults(func=run_algebra)



# --- info subcommand ---
    info_parser = subparsers.add_parser("info", help="System and algebra information")
    info_parser.set_defaults(
        func=lambda a: (
            print(f"Fibonacci Anyon Algebra (SU(2)_3, k={3})"),
            print(f"  Golden ratio phi = {PHI:.10f}"),
            print(f"  Total quantum dimension D = {D:.10f}"),
            print(f"  Topological spin theta_tau = {THETA_TAU:.6f}"),
            print(f"  Central charge c = {central_charge():.4f}"),
            print(f"  Fusion rule: tau x tau = 1 + tau"),
            print(f"  Computational universality: YES (Fibonacci anyons are universal)"),
        )
    )

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()