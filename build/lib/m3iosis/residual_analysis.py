#!/usr/bin/env python3
"""Residual analysis: compute every structural prediction vs PDG values."""
import math

# === SIC STRUCTURAL CONSTANTS ===
d_sic = 12
n_outcomes = d_sic + 1  # 13
gear = 4
alphas_inv = 137.035999084  # fine-structure inverse
alpha = 1/alphas_inv
cos2_tilt = 16/17  # cos^2(arctan(1/4))

# === TILT ANGLE ===
tilt_angle = math.atan(1/4)  # arctan(1/4)
print(f"Tilt angle: {tilt_angle:.6f} rad = {math.degrees(tilt_angle):.4f} deg")
print(f"cos^2(tilt) = {cos2_tilt:.10f}")
print(f"sin^2(tilt) = {1-cos2_tilt:.10f}")
print()

# === PMNS SECTOR ===
print("="*60)
print("PMNS SECTOR RESIDUALS")
print("="*60)

# sin²θ₁₂ (solar): 4/13
s12_sq = 4/13
s12 = math.asin(math.sqrt(s12_sq))
print(f"\nsin²θ₁₂ (solar):")
print(f"  Structural: {s12_sq:.6f} = 4/13")
print(f"  θ₁₂ = {math.degrees(s12):.4f} deg")
print(f"  PDG 2022: 0.307 ± 0.013")
print(f"  Residual: {s12_sq - 0.307:.6f} ({(s12_sq-0.307)/0.013*100:.1f}% of 1σ)")

# sin²θ₂₃ (atmospheric): 128/221
s23_sq = 128/221
s23 = math.asin(math.sqrt(s23_sq))
print(f"\nsin²θ₂₃ (atmospheric):")
print(f"  Structural: {s23_sq:.6f} = 128/221")
print(f"  θ₂₃ = {math.degrees(s23):.4f} deg")
print(f"  PDG 2022: 0.572 ± 0.023")
print(f"  Residual: {s23_sq - 0.572:.6f} ({(s23_sq-0.572)/0.023*100:.1f}% of 1σ)")

# sin²θ₁₃ (reactor): 1/48
s13_sq = 1/48
s13 = math.asin(math.sqrt(s13_sq))
print(f"\nsin²θ₁₃ (reactor):")
print(f"  Structural: {s13_sq:.6f} = 1/48")
print(f"  θ₁₃ = {math.degrees(s13):.4f} deg")
print(f"  PDG 2022: 0.0220 ± 0.0007")
print(f"  Residual: {s13_sq - 0.0220:.6f} ({(s13_sq-0.0220)/0.0007*100:.1f}% of 1σ)")
print(f"  Ratio PDG/struct: {0.0220/s13_sq:.6f}")

# δ_CP (PMNS): π + 2·arctan(1/4)
dcp_pmns = math.pi + 2*tilt_angle
print(f"\nδ_CP (Dirac, PMNS):")
print(f"  Structural: {math.degrees(dcp_pmns):.4f} deg = π + 2·arctan(1/4)")
print(f"  NuFIT 5.2 (NO): 217° ± 44°")
print(f"  Residual: {math.degrees(dcp_pmns) - 217:.1f} deg")

# === CKM SECTOR ===
print("\n" + "="*60)
print("CKM SECTOR RESIDUALS")
print("="*60)

# Cabibbo angle: tan(θ_C) = 3/13
tan_theta_C = 3/13
theta_C = math.atan(tan_theta_C)
lambda_ckm_sin = math.sin(theta_C)  # Wolfenstein λ = sin(θ_C)
lambda_ckm_tan = 3/13  # what the module currently uses
print(f"\nCabibbo angle:")
print(f"  tan(θ_C) = {tan_theta_C:.6f} = 3/13")
print(f"  θ_C = {math.degrees(theta_C):.4f} deg")
print(f"  λ = sin(θ_C) = {lambda_ckm_sin:.6f}")
print(f"  λ (module) = {lambda_ckm_tan:.6f} = 3/13")
print(f"  True λ: {lambda_ckm_sin:.6f}")
print(f"  Residual (module - true): {lambda_ckm_tan - lambda_ckm_sin:.6f} ({((lambda_ckm_tan/lambda_ckm_sin)-1)*100:.2f}%)")

# Wolfenstein A = 4/5
A_val = 4/5
print(f"\nWolfenstein A:")
print(f"  Structural: {A_val:.6f} = 4/5")
print(f"  PDG: ~0.825")
print(f"  Residual: {A_val - 0.825:.6f} ({(A_val/0.825-1)*100:.2f}%)")

# |V_cb| = 1/25
Vcb = 1/25
print(f"\n|V_cb|:")
print(f"  Structural: {Vcb:.6f} = 1/25")
print(f"  PDG: ~0.041")
print(f"  Residual: {Vcb - 0.041:.6f}")

# δ_CP (CKM): arctan(13/5)
dcp_ckm = math.atan(13/5)
print(f"\nδ_CP (CKM):")
print(f"  Structural: {math.degrees(dcp_ckm):.4f} deg")
print(f"  PDG: ~68.8° (from UTfit)")

# Jarlskog (CKM)
J_ckm = (4/5)**2 * (3/13)**6 * (13/14)
print(f"\nJarlskog (CKM):")
print(f"  Structural: {J_ckm:.6e}")
print(f"  PDG: ~3.0e-5")
print(f"  Note: uses eta=13/14 approx, which corresponds to rho ≈ 5/14")

# === QUARK-LEPTON COMPLEMENTARITY ===
print("\n" + "="*60)
print("QUARK-LEPTON COMPLEMENTARITY")
print("="*60)

qlc_sum = math.degrees(s12) + math.degrees(theta_C)
print(f"\nθ₁₂ (solar) + θ_C (Cabibbo):")
print(f"  {math.degrees(s12):.4f}° + {math.degrees(theta_C):.4f}° = {qlc_sum:.4f}°")
print(f"  Expected (exact complementarity): 45°")
print(f"  Residual from 45°: {qlc_sum - 45:.4f}° ({(qlc_sum/45-1)*100:.2f}%)")
print(f"  Correction factor: arctan(1/4)/d = {math.degrees(tilt_angle)/12:.4f}°")

# === HUBBLE CONSTANT ===
print("\n" + "="*60)
print("HUBBLE CONSTANT RESIDUALS")
print("="*60)

H0_cmb = 67.44
H0_local = 73.06
print(f"\nH₀(CMB):")
print(f"  Structural: {H0_cmb:.2f} km/s/Mpc")
print(f"  Planck 2018: 67.4 ± 0.5 km/s/Mpc")
print(f"  Residual: {H0_cmb - 67.4:.4f} km/s/Mpc ({(H0_cmb/67.4-1)*100:.4f}%)")

print(f"\nH₀(local):")
print(f"  Structural: {H0_local:.2f} km/s/Mpc")
print(f"  SH0ES 2022: 73.04 ± 1.04 km/s/Mpc")
print(f"  Residual: {H0_local - 73.04:.4f} km/s/Mpc ({(H0_local/73.04-1)*100:.4f}%)")

# === WEINBERG ANGLE ===
print("\n" + "="*60)
print("WEINBERG ANGLE")
print("="*60)

sw2 = 3/13
print(f"\nsin²θ_W:")
print(f"  Structural: {sw2:.6f} = 3/13")
print(f"  PDG (MS-bar): 0.23122 ± 0.00003")
print(f"  Residual: {sw2 - 0.23122:.6f}")
print(f"  Note: 3/13 ≈ 0.23077 is at MS-bar scale")

# === SYSTEMATIC PATTERN ===
print("\n" + "="*60)
print("SYSTEMATIC PATTERN ANALYSIS")
print("="*60)

print("\nCorrection hierarchy needed:")
print("  Tier 1 — Rational fraction (exact): base ratio from SIC partition")
print("  Tier 2 — Tilt correction: cos²(arctan(1/4)) = 16/17 (atmospheric only)")
print("  Tier 3 — Cross-pinch braid trace: sin²θ₁₃ needs correction")
print("  Tier 4 — Horn torus curvature: O(1/d²) corrections everywhere")
print("  Tier 5 — Sin vs tan: CKM λ = sin(θ_C) ≠ tan(θ_C)")

# Cross-pinch correction analysis for sin²θ₁₃
print("\n\nCross-pinch correction for sin²θ₁₃:")
cross_pinch_trace = 2*(math.sqrt(3)-1)  # |Tr(B_3 braid)|
print(f"  Burau trace |Tr| = 2(√3-1) = {cross_pinch_trace:.6f}")
print(f"  |Tr|/d = {cross_pinch_trace/d_sic:.6f}")
print(f"  |Tr|/d² = {cross_pinch_trace/(d_sic**2):.6f}")

# Candidate correction factors
base_s13 = 1/48
print(f"\n  Base: 1/48 = {base_s13:.6f}")
for factor_desc, factor in [
    ("× (1 + |Tr|/d)", base_s13 * (1 + cross_pinch_trace/d_sic)),
    ("× (1 + |Tr|/d²)", base_s13 * (1 + cross_pinch_trace/(d_sic**2))),
    ("× (d+1)/(d-1) (Gerzon ratio)", base_s13 * (d_sic+1)/(d_sic-1)),
    ("× (17/16) (inverse tilt)", base_s13 * (17/16)),
    ("× (137/144) (alpha-1 ratio)", base_s13 * (alphas_inv/(d_sic**2))),
    ("× (d²/(d²-3))? d² correction", base_s13 * d_sic**2/(d_sic**2 - 3)),
    ("× (1 + 1/(2d))", base_s13 * (1 + 1/(2*d_sic))),
]:
    print(f"  {factor_desc}: {factor:.6f} (diff from PDG 0.0220: {factor-0.0220:+.6f})")

# Sin vs Tan correction for CKM
print(f"\n\nCKM λ = sin(θ_C) correction:")
print(f"  tan(θ_C) = 3/13 = {tan_theta_C:.6f}")
print(f"  θ_C = {math.degrees(theta_C):.4f}°")
print(f"  λ_true = sin(θ_C) = {lambda_ckm_sin:.6f}")
print(f"  λ_base = 3/13 = {lambda_ckm_tan:.6f}")
print(f"  Correction factor: sin(θ_C)/tan(θ_C) = cos(θ_C) = {math.cos(theta_C):.6f}")
print(f"  cos(θ_C) = 13/√178 = {13/math.sqrt(178):.6f}")
print(f"  So λ = 3/√178 ≈ {3/math.sqrt(178):.6f}")
