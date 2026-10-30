#!/usr/bin/env python3
"""Tangent chord analysis at FFUSE₃ apex — the fourth direction."""

import numpy as np

LR = 1.0
sqrt2 = np.sqrt(2)
sqrt3 = np.sqrt(3)

# Chord direction vectors (normalized, from evaluator to apex)
v_T = np.array([1/sqrt2, -1/sqrt2, 0.0])
v_F = np.array([1/sqrt2, 1/(2*sqrt2), -sqrt3/(2*sqrt2)])
v_I = np.array([1/sqrt2, 1/(2*sqrt2), sqrt3/(2*sqrt2)])

apex = np.array([2*LR, 0.0, 0.0])
# Evaluator positions
pos_T = np.array([LR, LR, 0.0])
pos_F = np.array([LR, -LR/2, LR*sqrt3/2])
pos_I = np.array([LR, -LR/2, -LR*sqrt3/2])

print("=== THE FOURTH DIRECTION AT FFUSE₃ APEX ===")
print()

# 1. The null space of the chord DIFFERENCE map
# The direction that is "same" for all three chords = 
# direction orthogonal to all difference vectors (v_T - v_F), (v_T - v_I)
diff_TF = v_T - v_F
diff_TI = v_T - v_I
diff_FI = v_F - v_I

print("1. DIFFERENCE VECTORS (chord-to-chord distinguishability):")
print(f"   v_T - v_F = ({diff_TF[0]:.6f}, {diff_TF[1]:.6f}, {diff_TF[2]:.6f})")
print(f"   v_T - v_I = ({diff_TI[0]:.6f}, {diff_TI[1]:.6f}, {diff_TI[2]:.6f})")
print(f"   v_F - v_I = ({diff_FI[0]:.6f}, {diff_FI[1]:.6f}, {diff_FI[2]:.6f})")

# These span the yz-plane. Find the orthogonal direction
n = np.cross(diff_TF, diff_TI)  # normal to the difference plane
n = n / np.linalg.norm(n)
print(f"\n   Normal to difference plane: ({n[0]:.6f}, {n[1]:.6f}, {n[2]:.6f})")
print(f"   = x-axis? {np.isclose(n[0], 1.0) and np.isclose(n[1], 0.0)}")

# 2. The mutual tangent at apex
# At the apex, each chord has a tangent direction. 
# The "common tangent" is the direction shared by all three.
# But they arrive from different directions. What direction can they CONTINUE in?
# Find the direction w that minimizes Σ (v_i · w)^2 for |w|=1
# = the smallest eigenvector of the frame operator
V = np.column_stack([v_T, v_F, v_I])
F_op = V @ V.T / 3
eigvals, eigvecs = np.linalg.eigh(F_op)
print("\n2. FRAME OPERATOR EIGENSTRUCTURE (weight of each tangent direction):")
for i in range(3):
    print(f"   λ_{i} = {eigvals[i]:.6f}  axis = ({eigvecs[0,i]:.6f}, {eigvecs[1,i]:.6f}, {eigvecs[2,i]:.6f})")
print(f"\n   The x-axis carries λ = 0.5 (double the yz-weight of 0.25)")
print(f"   The yz-plane is a DEGENERATE EIGENSPACE (λ = 0.25)")

# 3. The Hopf fiber tangent at apex
# In the Hopf fibration S³ → S², the fiber at the projection point
# collapses. The "tangent to the fiber" at the collapse is the direction
# in S³ that would have been the S¹ orbit if it hadn't collapsed.
# 
# The S² base is parameterized by the direction of approach.
# The S¹ fiber is the azimuthal phase φ.
# At the apex, all three azimuths converge — the fiber collapses.
# The tangent to the collapsed fiber is... what?
#
# It's the direction in the yz-plane that's orthogonal to the 
# radial direction. Since all three chords share the same yz-magnitude LR,
# the fiber circle has radius LR. At the apex (center of fiber circle),
# the tangent to the fiber is ANY direction in the yz-plane.
# 
# But the three chords arrive from specific φ values. The fiber collapse
# means the φ coordinate becomes undefined — the tangent space at the 
# apex has S¹ worth of directions that are "equivalent under fusion."

print("\n3. HOPF FIBER GEOMETRY AT APEX:")
print(f"   Fiber radius (yz-projection of each chord): LR = {LR}")
print(f"   Fiber circle centers: (LR, 0, 0)")
print(f"   Evaluator positions on fiber circle:")
print(f"     T: φ = atan2(0, 1) = 0°  (along +y)")
print(f"     F: φ = atan2({sqrt3/2:.4f}, {-0.5:.4f}) = {np.degrees(np.arctan2(sqrt3/2, -0.5)):.1f}°")
print(f"     I: φ = atan2({-sqrt3/2:.4f}, {-0.5:.4f}) = {np.degrees(np.arctan2(-sqrt3/2, -0.5)):.1f}°")
print(f"   Chord direction φ (from evaluator TO apex):")
chord_yz_T = -pos_T[1:]  # chord yz = negative of evaluator yz
chord_yz_F = -pos_F[1:]
chord_yz_I = -pos_I[1:]
for name, yz in [("T", chord_yz_T), ("F", chord_yz_F), ("I", chord_yz_I)]:
    phi = np.degrees(np.arctan2(yz[1], yz[0]))
    print(f"     {name}: yz-direction = ({yz[0]:.4f}, {yz[1]:.4f})  φ = {phi:.1f}°")

# 4. The tangent chord: what if a bead continues THROUGH the apex?
# After fusion, the bead continues along the coupler axis (x-direction)
# with half the velocity component (since cos(45°) = 1/√2 of the original
# speed goes into the x-component).
print("\n4. CONTINUATION THROUGH FFUSE₃ (post-fusion tangent):")
# The x-component of each chord's velocity is 1/√2 of total speed
v_x = 1/sqrt2  # x-component of each normalized chord
print(f"   Each chord's x-velocity: {v_x:.6f} = 1/√2 of total")
print(f"   Sum of x-velocities: {3*v_x:.6f} = 3/√2")
print(f"   Continuation direction: x-axis (1, 0, 0)")
print(f"   Continuation is ALONG the coupler axis — the fused output")
print()

# 5. What if the chord is tangent to the evaluator circle?
# The tangent to the evaluator circle at each position, extended to the apex.
# At T position (LR, LR, 0), the circle tangent is along z-axis (0, 0, 1).
# The chord from (LR, LR, t) to apex (2LR, 0, 0) has direction (LR, -LR, -t).
# For this to be at 45° to the x-axis, we need |(-LR, -t)| = LR (yz-mag = LR).
# So sqrt(LR² + t²) = LR → t = 0. So the ONLY chord at 45° from the 
# tangent line that hits the apex is the one FROM the evaluator position itself.

print("5. TANGENT TO EVALUATOR CIRCLE, TERMINATING AT APEX:")
print(f"   Tangent at T to circle centered at (LR, 0, 0): (0, 0, 1)")
print(f"   Point on tangent: (LR, LR, t)")
print(f"   Chord to apex: (LR, -LR, -t)")
print(f"   |yz| = sqrt(LR² + t²)")
print(f"   45° condition requires |yz| = LR  →  t = 0")
print(f"   Result: the ONLY null geodesic from the tangent line to the apex")
print(f"   is the chord from the evaluator position itself.")
print(f"   The chord is NOT tangent to the evaluator circle — it's RADIAL.")
print()

# 6. The actual fourth direction: the Hopf normal
# At the apex, consider the S² of possible incoming directions.
# The three chord directions pierce this S² at three points.
# The normal to the plane containing these three piercing points
# is the direction that's "most different" from all three chords.
# = the x-axis (already confirmed).
#
# But the TANGENT to this S² at the apex — the plane orthogonal to
# ALL chords — doesn't exist. What does exist:
print("6. UNIQUE GEOMETRIC INVARIANTS AT FFUSE₃:")
print(f"   SIC-POVM dot product: cos(θ) = 1/4 (exact, all pairs)")
print(f"   Chord angle at apex: arccos(1/4) = {np.degrees(np.arccos(0.25)):.4f}°")
print(f"   Frame anisotropy: 2:1 ratio (x vs yz)")
print(f"   yz-plane degeneracy: all directions in yz have equal weight")
print(f"   Null geodesic inclination: arccos(1/√2) = 45.0000°")
print()

# 7. The "tangent" in the SIC-POVM sense
# A tangent vector to the SIC-POVM manifold at the fiducial state
# corresponds to a direction in the Hilbert space that's orthogonal
# to the fiducial. In the d=3 SIC-POVM case with 9 vectors,
# the three chords project this structure onto ℝ³.
# The "tangent" direction in ℝ³ to the SIC-POVM measurement
# is the direction that carries NO information — the null direction
# of the measurement. This is the minimal eigenvalue direction.
print("7. SIC-POVM NULL DIRECTION (no information carried):")
# Since yz-plane is degenerate (λ=0.25), EVERY direction in yz carries
# the SAME amount of information (same weight). There is no single null direction.
# But the x-axis carries DOUBLE the weight — it carries more information.
print(f"   yz-plane: λ = 0.25 (constant across all azimuths)")
print(f"   x-axis:  λ = 0.50 (double weight)")
print(f"   Information ratio (x:yz) = 2:1")
print(f"   Interpretation: the coupler axis carries twice the information")
print(f"   of any transverse direction. The azimuth carries the")
print(f"   distingiushability of evaluators; the x-axis carries the")
print(f"   fused evaluation output.")
