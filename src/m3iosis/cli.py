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
        simulate_braid(args.word)
        return

    if args.manifold:
        man = FibonacciManifold()
        print(f"Manifold Curvature: {man.curvature()}")
        print(f"Path Integral Measure: {man.path_integral(args.word, 3)}")
        print(f"Braid center word: {man.braid_center(3)}")
        return

    # Default: print help
    fib_parser.print_help()


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
    fib_parser.set_defaults(func=fib_command)

    # --- sim subcommand ---
    sim_parser = subparsers.add_parser("sim", help="Braid simulation")
    sim_parser.add_argument("--word", type=int, nargs="+", default=[1, 2, 1],
                            help="Braid word to simulate")
    sim_parser.add_argument("--strands", type=int, default=3,
                            help="Number of strands")
    sim_parser.set_defaults(func=lambda a: simulate_braid(a.word))

    # --- manifold subcommand ---
    man_parser = subparsers.add_parser("manifold", help="Topological manifold operations")
    man_parser.add_argument("--word", type=int, nargs="+", default=[1, 2, 1],
                            help="Braid word for path integral")
    man_parser.add_argument("--strands", type=int, default=3,
                            help="Number of strands")
    man_parser.set_defaults(
        func=lambda a: (
            print(f"Manifold Curvature: {FibonacciManifold().curvature()}"),
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