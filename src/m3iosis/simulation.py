"""Braiding simulation module for Fibonacci anyons.

Evaluates braid words on fusion spaces and computes final anyon states,
outcome probabilities, and fusion channel distributions.

Usage:
    from m3iosis.simulation import simulate_braid
    simulate_braid([1, 2, 1], num_strands=4)
"""

import numpy as np
from m3iosis.fibonacci_anyon_tool import FibonacciBraidSimulator
from m3iosis.fibonacci_anyon_algebra import fusion_space_dimension


def simulate_braid(word, num_strands=3):
    """Evaluate a braid word and compute the resulting anyon state.

    Evaluates an Artin braid word on the fusion space V_n = Hom(tau^n, 1)
    and returns the final state vector with outcome probabilities.

    Args:
        word: List of signed Artin generators (e.g. [1, 2, 1] for 
              sigma_1 sigma_2 sigma_1 on 3 strands). Positive = sigma_k,
              negative = sigma_k^{-1} (adjoint).
        num_strands: Number of strands (default 3, dim V_3 = 1).
                     Must be >= 2. Dim V_n = F_{n-1} (Fibonacci number).
                     For non-trivial dynamics use n >= 4 (dim V_4 = 2).
    
    Returns:
        dict with keys: 'unitary', 'final_state', 'probabilities',
                        'fusion_channels', 'dimension'
    """
    sim = FibonacciBraidSimulator()
    dim = fusion_space_dimension(num_strands)
    
    print(f"Executing sequence: {word} on {num_strands} strands.")
    print(f"  Fusion space dim V_{num_strands} = {dim} (Fibonacci F_{num_strands-1})")
    
    # evaluate_braid_word takes (n, word) — strand count FIRST;
    # the simulator method takes (word, num_strands).
    unitary_op = sim.evaluate_braid_word(word, num_strands)
    d = unitary_op.shape[0]
    
    # Start in the first basis state.
    initial_state = np.zeros(d, dtype=complex)
    initial_state[0] = 1.0
    
    final_state = unitary_op @ initial_state
    probs = [abs(amp)**2 for amp in final_state]
    
    print(f"  Unitary dimension: {d} x {d}")
    print(f"  Final state vector: {final_state}")
    print(f"  Outcome probabilities:")
    for i, p in enumerate(probs):
        print(f"    |state_{i}> : {p:.6f}")
    
    result = {
        'unitary': unitary_op,
        'final_state': final_state,
        'probabilities': probs,
        'dimension': d
    }
    
    # Map fusion channels when basis is large enough.
    if d >= 2:
        print(f"  Fusion channels:")
        print(f"    Vacuum (1):  {probs[0]:.6f}")
        print(f"    Tau (tau):   {probs[1]:.6f}")
        result['fusion_channels'] = {'vacuum': probs[0], 'tau': probs[1]}
    
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Fibonacci braid simulation — evaluate braid words on anyon fusion spaces")
    parser.add_argument("word", type=int, nargs="+",
                        help="Braid word as signed Artin generators (e.g. 1 2 1)")
    parser.add_argument("--strands", "-n", type=int, default=4,
                        help="Number of strands (default: 4, dim V_4 = 2 = 1 qubit)")
    args = parser.parse_args()
    simulate_braid(args.word, args.strands)


if __name__ == "__main__":
    main()
