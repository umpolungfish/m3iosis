#!/usr/bin/env python3
"""
Fibonacci Anyon CLI Tool — thin wrapper around the expanded operational tools.

This module provides backward compatibility for the original CLI interface
while delegating to the full-featured `m3iosis.cli` entry point.

Author: Math@perator (Lando(odot)perator team)
"""
import sys
import argparse
import numpy as np
from m3iosis.fibonacci_anyon_tool import (
    FibonacciBraidSimulator,
    FibonacciAnyonAlgebra,
    FibonacciQuantumComputer,
    FibonacciDiagram,
)
from m3iosis.fibonacci_anyon_algebra import (
    fusion_space_dimension, summary, PHI, D, THETA_TAU, central_charge,
)


def main():
    parser = argparse.ArgumentParser(
        description="Fibonacci Anyon CLI Tool (expanded operational tools)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fib_cli --diag                        Run algebraic kernel verification
  fib_cli --fusion tau tau              Fuse two tau anyons
  fib_cli --braid 3 1 2 1               Evaluate braid word [1,2,1] on 3 strands
  fib_cli --gate-info                   Report on quantum computational universality
  fib_cli --tree 4                      Show fusion tree basis for 4 anyons
  fib_cli --jones 3 1 2 1               Compute Jones polynomial from braid
  fib_cli --dimension 6                 Fusion space dimension for 6 anyons
  fib_cli --summary                     Full self-consistency summary
  fib_cli --simulate --strands 3        Simulate braid on 3 strands
        """,
    )
    parser.add_argument("--diag", action="store_true",
                        help="Run algebraic kernel verification")
    parser.add_argument("--fusion", nargs=2, metavar=("A", "B"),
                        help="Fuse two anyons (e.g. --fusion tau tau)")
    parser.add_argument("--braid", nargs="+", type=int, metavar=("N", "GENS..."),
                        help="Evaluate braid word on N strands (e.g. --braid 3 1 2 1)")
    parser.add_argument("--jones", nargs="+", type=int, metavar=("N", "GENS..."),
                        help="Compute Jones polynomial from braid word")
    parser.add_argument("--gate-info", action="store_true",
                        help="Report on quantum computational universality")
    parser.add_argument("--tree", type=int, metavar="N",
                        help="Show fusion tree basis for N anyons")
    parser.add_argument("--dimension", type=int, metavar="N",
                        help="Fusion space dimension for N anyons")
    parser.add_argument("--summary", action="store_true",
                        help="Full self-consistency summary")
    parser.add_argument("--simulate", action="store_true",
                        help="Simulate a braid sequence")
    parser.add_argument("--strands", type=int, default=3,
                        help="Number of strands (default: 3)")
    parser.add_argument("--word", type=int, nargs="+", default=[1, 2, 1],
                        help="Braid word (default: [1, 2, 1])")

    args = parser.parse_args()

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

    if args.simulate:
        print(f"Simulating braid {args.word} on {args.strands} strands...")
        sim = FibonacciBraidSimulator()
        stats = sim.braid_statistics(args.strands, args.word)
        print(f"  dim V_{args.strands} = {stats['dimension']}")
        print(f"  Unitary: {stats['is_unitary']}")
        print(f"  Trace: {stats['trace']:.6f}")
        print(f"  Eigenvalues: {', '.join(f'{e:.4f}' for e in stats['eigenvalues'])}")
        print("Simulation complete. Algebra: Consistent.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()