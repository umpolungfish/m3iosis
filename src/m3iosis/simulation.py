from m3iosis.fibonacci_anyon_tool import FibonacciBraidSimulator
import numpy as np
import argparse

def simulate_braid(word, num_strands=3):
    # Setup simulator
    sim = FibonacciBraidSimulator()
    
    print(f"Executing sequence: {word} on {num_strands} strands.")
    
    # Calculate unitary evolution
    unitary_op = sim.evaluate_braid_word(word, num_strands)
    
    # Starting state: |tau>
    initial_state = np.array([0, 1], dtype=complex)
    final_state = unitary_op @ initial_state
    
    print(f"Final state vector: {final_state}")
    
    # Measure probabilities
    probs = sim.get_fusion_probabilities(final_state)
    print(f"Probabilities: Vacuum (1) = {probs['vacuum']:.4f}, Tau (τ) = {probs['tau']:.4f}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--word", type=int, nargs="+", default=[1, 2, 1])
    args = parser.parse_args()
    simulate_braid(args.word)

if __name__ == "__main__":
    main()
