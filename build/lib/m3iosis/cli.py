#!/usr/bin/env python3
import argparse
from m3iosis.fibonacci_anyon_tool import run_diagnostic
from m3iosis.simulation import simulate_braid
from m3iosis.manifold import FibonacciManifold
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="M3Iosis Advanced CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Fib Anyon Command
    fib_parser = subparsers.add_parser("fib")
    fib_parser.add_argument("--diag", action="store_true")
    fib_parser.add_argument("--sim", action="store_true")
    fib_parser.add_argument("--manifold", action="store_true")
    fib_parser.add_argument("--word", type=int, nargs="+", default=[1, 2, 1])

    args = parser.parse_args()

    if args.command == "fib":
        if args.diag:
            print(run_diagnostic())
        elif args.sim:
            simulate_braid(args.word)
        elif args.manifold:
            man = FibonacciManifold()
            print(f"Manifold Curvature: {man.curvature()}")
            print(f"Path Integral Measure: {man.path_integral(args.word, 3)}")
            print(f"Braid center word: {man.braid_center(3)}")
        else:
            fib_parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
