#!/usr/bin/env python3
"""
Compositional Refinement: Mersenne Factor Operator Map
Builds the full ord2(r) operator map, then analyzes the compositional structure
to identify Mersenne-prime-like survivors.

Key insight: "each number is an operation unto itself, and operates on the others."
- Each prime r defines an operator P_r on Mersenne space: P_r(M_p) = "composite" iff ord2(r)|p.
- The composition of r1 and r2 acts via lcm(ord2(r1), ord2(r2)).
- The inclusion topology (Th=𐑰) means p_53 is "contained in" the gap structure of p_52.
"""
import json, os, subprocess, sys, time
from math import isqrt, log
from collections import defaultdict

# ─── Known Mersenne primes ───────────────────────────────────────
KNOWN_MERSENNE = [
    2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423,
    9689,9941,11213,19937,21701,23209,44497,86243,110503,132049,216091,756839,
    859433,1257787,1398269,2976221,3021377,6972593,13466917,20996011,24036583,
    25964951,30402457,32582657,37156667,42643801,43112609,57885161,74207281,
    77232917,82589933,136279841
]

P_MIN = 138_000_000
P_MAX = 560_000_000
P_52 = 136_279_841

# ─── Load Rust factor map ────────────────────────────────────────
def load_factor_map(path="/home/mrnob0dy666/imsgct/mersenne_gpu/compositional_factors_v2.txt"):
    factors = {}
    if not os.path.exists(path):
        return factors
    with open(path) as f:
        for line in f:
            if line.startswith('#'): continue
            p, nf, minf, avgf = line.strip().split('\t')
            factors[int(p)] = {'nf': int(nf), 'minf': int(minf), 'avgf': float(avgf)}
    return factors

# ─── Candidate generation ────────────────────────────────────────
def primes_in_range(lo, hi):
    """Segmented sieve for primes in [lo, hi]."""
    limit = isqrt(hi) + 1
    small = bytearray(limit + 1)
    small[0:2] = b'\x01\x01'
    for i in range(2, isqrt(limit) + 1):
        if not small[i]:
            for j in range(i*i, limit+1, i):
                small[j] = 1
    small_primes = [i for i in range(2, limit+1) if not small[i]]
    n = hi - lo + 1
    seg = bytearray(n)
    for p in small_primes:
        start = max(p*p, ((lo + p - 1) // p) * p)
        for j in range(start, hi+1, p):
            seg[j-lo] = 1
    return [lo+i for i in range(n) if not seg[i] and lo+i >= 2 and (lo+i==2 or (lo+i)&1)]

# ─── Wagstaff / LPW analysis ─────────────────────────────────────
def wagstaff_expected_count(x):
    """Expected number of Mersenne primes with exponent <= x (Wagstaff)."""
    from math import e, log
    gamma = 0.5772156649015329  # Euler-Mascheroni
    return (e**gamma / log(2)) * log(log(x)) if x > 2 else 0

def empirical_cdf():
    """Build empirical CDF from known Mersenne gaps."""
    gaps = []
    for i in range(1, len(KNOWN_MERSENNE)):
        if KNOWN_MERSENNE[i] > 1000:  # skip tiny ones
            gaps.append(KNOWN_MERSENNE[i] / KNOWN_MERSENNE[i-1])
    gaps.sort()
    return gaps

# ─── Compositional Operator Analysis ─────────────────────────────
def analyze_operator_structure(factors, candidates):
    """
    Analyze the operator structure:
    - For each candidate p, how many r have ord2(r) = p?
    - What's the density pattern of eliminated candidates?
    - How does it correlate with Wagstaff predictions?
    """
    n_candidates = len(candidates)
    eliminated = sum(1 for p in candidates if p in factors)
    
    # Cluster analysis: find runs of consecutive survivors
    candidates_set = set(candidates)
    survivor_runs = []
    current_run = []
    for p in sorted(candidates):
        if p in factors:
            if current_run:
                survivor_runs.append(current_run)
                current_run = []
        else:
            current_run.append(p)
    if current_run:
        survivor_runs.append(current_run)
    
    # Analyze survivor runs
    run_lengths = [len(r) for r in survivor_runs]
    run_lengths.sort()
    
    print(f"""
═══ OPERATOR STRUCTURE ANALYSIS ═══
  Candidates:       {n_candidates:,}
  Eliminated:       {eliminated:,} ({100*eliminated/n_candidates:.1f}%)
  Survivors:        {n_candidates - eliminated:,}
  
  Survivor runs:    {len(survivor_runs):,}
  Min run length:   {min(run_lengths)}
  Median run:       {run_lengths[len(run_lengths)//2]}
  Max run length:   {max(run_lengths)}
  Runs length=1:    {sum(1 for r in survivor_runs if len(r)==1)} (isolated survivors)
  Runs length>100:  {sum(1 for r in survivor_runs if len(r)>100)}
""")
    
    return survivor_runs

# ─── Inclusion Topology Analysis ─────────────────────────────────
def inclusion_analysis(survivor_runs, factors):
    """
    Th=𐑰 (inclusion): p_53 should be "included" in the gap structure.
    Analysis:
    1. Compute the empirical gap distribution from p_52
    2. Identify which survivor runs fall in the predicted gap
    3. Mark the "inclusion-consistent" candidates
    """
    gaps = empirical_cdf()
    median_gap = gaps[len(gaps)//2]
    p10_gap = gaps[len(gaps)//10]
    p90_gap = gaps[9*len(gaps)//10]
    
    print(f"""
═══ INCLUSION TOPOLOGY (Th=𐑰) ANALYSIS ═══
  p_52 = {P_52:,}
  Gap distribution (last {len(gaps)} gaps > 1000):
    p10 gap ratio:  {p10_gap:.4f}  →  p_53 ≈ {P_52 * p10_gap:,.0f}
    median ratio:   {median_gap:.4f}  →  p_53 ≈ {P_52 * median_gap:,.0f}
    p90 ratio:      {p90_gap:.4f}  →  p_53 ≈ {P_52 * p90_gap:,.0f}
  
  Grammar prediction: p_53 ≈ 206M (gap ratio ≈ {206_000_000/P_52:.4f})
""")
    
    # Find survivor runs that overlap with the predicted ranges
    lo_pred = int(P_52 * p10_gap)
    hi_pred = int(P_52 * p90_gap)
    
    runs_in_range = []
    for run in survivor_runs:
        if run[0] <= hi_pred and run[-1] >= lo_pred:
            overlap_start = max(run[0], lo_pred)
            overlap_end = min(run[-1], hi_pred)
            runs_in_range.append((run, overlap_start, overlap_end))
    
    print(f"  Survivor runs overlapping [{lo_pred:,}, {hi_pred:,}]: {len(runs_in_range)}")
    
    # Print the best candidates (longest survivor runs in the predicted range)
    runs_in_range.sort(key=lambda x: x[1])  # sort by start
    print(f"\n  Top survivor runs in predicted range:")
    for run, start, end in runs_in_range[:20]:
        print(f"    [{run[0]:,} .. {run[-1]:,}]  len={len(run)}  overlap=[{start:,}, {end:,}]")
    
    return runs_in_range

# ─── Cross-Referencing with GPU survivors ─────────────────────────
def cross_reference_gpu(gpu_survivors_path="/home/mrnob0dy666/imsgct/mersenne_gpu/survivors_v3.txt"):
    """Load GPU survivors and cross-reference with compositional survivors."""
    if not os.path.exists(gpu_survivors_path):
        return set()
    with open(gpu_survivors_path) as f:
        return {int(line.strip()) for line in f if line.strip()}

# ─── Main ────────────────────────────────────────────────────────
def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  COMPOSITIONAL REFINEMENT — Operator Map Analysis       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Load factor map
    t0 = time.time()
    factors = load_factor_map()
    print(f"Loaded {len(factors):,} eliminated exponents ({time.time()-t0:.1f}s)")
    
    # Generate candidates
    t0 = time.time()
    candidates = primes_in_range(P_MIN, P_MAX)
    print(f"Generated {len(candidates):,} candidates in [{P_MIN:,}, {P_MAX:,}] ({time.time()-t0:.1f}s)")
    
    # Operator structure analysis
    survivor_runs = analyze_operator_structure(factors, candidates)
    
    # Inclusion topology analysis
    runs_in_range = inclusion_analysis(survivor_runs, factors)
    
    # Cross-reference with GPU survivors
    gpu_survivors = cross_reference_gpu()
    if gpu_survivors:
        compositional_survivors = {p for p in candidates if p not in factors}
        both_survivors = compositional_survivors & gpu_survivors
        print(f"\n═══ GPU CROSS-REFERENCE ═══")
        print(f"  GPU survivors:      {len(gpu_survivors):,}")
        print(f"  Compositional surv: {len(compositional_survivors):,}")
        print(f"  Both (hardest):     {len(both_survivors):,}")
        
        # Top candidates: in predicted range, in both survivor sets
        top_range = (int(P_52 * 1.05), int(P_52 * 2.50))
        top_candidates = sorted([p for p in both_survivors if top_range[0] <= p <= top_range[1]])
        print(f"\n  Top candidates (both survivors, in [{top_range[0]:,}, {top_range[1]:,}]):")
        for p in top_candidates[:30]:
            print(f"    M_{p}")
        if len(top_candidates) > 30:
            print(f"    ... and {len(top_candidates) - 30} more")
        
        # Save for GPU deep test
        out_path = "/home/mrnob0dy666/imsgct/mersenne_gpu/compositional_top_candidates.txt"
        with open(out_path, 'w') as f:
            for p in top_candidates:
                f.write(f"{p}\n")
        print(f"\n  Top candidates → {out_path}")
    
    # Wagstaff analysis
    print(f"\n═══ WAGSTAFF PREDICTION ═══")
    expected_53 = wagstaff_expected_count(P_52)
    print(f"  Expected Mersenne count up to p_52={P_52:,}: {expected_53:.2f}")
    
    # Find x such that expected count = 53
    from math import e, log, exp
    gamma = 0.5772156649015329
    # wagstaff(N) = (e^gamma / log 2) * log log N = 53
    # log log N = 53 * log 2 / e^gamma
    # log N = exp(53 * log 2 / e^gamma)
    target = 53
    log_log_N = target * log(2) / (e**gamma)
    predicted_N = exp(exp(log_log_N))
    
    # But this assumes Wagstaff constant is correct. Empirically it's off by ~10x.
    # Adjusted: use the ratio of actual count to expected for p_52
    actual_count = 52
    correction = actual_count / wagstaff_expected_count(P_52) if wagstaff_expected_count(P_52) > 0 else 1
    adjusted_target = 53 / correction
    log_log_N_adj = adjusted_target * log(2) / (e**gamma)
    predicted_N_adj = exp(exp(log_log_N_adj))
    
    print(f"  Wagstaff raw prediction: p_53 ≈ {predicted_N:,.0f}")
    print(f"  Empirical correction: {correction:.2f}x")
    print(f"  Adjusted prediction: p_53 ≈ {predicted_N_adj:,.0f}")
    print(f"  Grammar prediction:   p_53 ≈ 206,000,000")
    
    # Gap-based prediction
    recent_gaps = []
    for i in range(len(KNOWN_MERSENNE)-5, len(KNOWN_MERSENNE)-1):
        recent_gaps.append(KNOWN_MERSENNE[i+1] / KNOWN_MERSENNE[i])
    avg_recent_gap = sum(recent_gaps) / len(recent_gaps) if recent_gaps else 1.3
    gap_pred = int(P_52 * avg_recent_gap)
    print(f"  Recent gap avg ({len(recent_gaps)} gaps): {avg_recent_gap:.4f} → p_53 ≈ {gap_pred:,}")
    
    print(f"\n═══ REFINED SEARCH STRATEGY ═══")
    print(f"  1. Focus on [{int(P_52*1.03):,}, {int(P_52*2.5):,}] (inclusion range)")
    print(f"  2. Prioritize p ≡ 3 (mod 4)")
    print(f"  3. Cross compositional survivors × GPU survivors")
    print(f"  4. LL test top ~100 candidates")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
