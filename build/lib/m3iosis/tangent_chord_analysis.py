#!/usr/bin/env python3
"""Tangent chord analysis at FFUSE₃ apex."""
import math

LR = 1.0  # sphere radius
center = (LR, 0.0, 0.0)  # sphere center

def sphere_surface(x, y, z):
    """Check if point is on sphere surface."""
    return abs((x - LR)**2 + y**2 + z**2 - LR**2) < 1e-10

def horn_curve(theta):
    """Position on horn curve (poloidal, phi=0)."""
    x = 2 * (1 + math.cos(theta))
    z = 2 * math.sin(theta)
    return (x, 0.0, z)

def chord_tangent_at_FFUSE3(P):
    """Check if chord P→FFUSE3 is tangent to sphere at FFUSE3."""
    FFUSE3 = (2*LR, 0.0, 0.0)
    # radius vector at FFUSE3
    R = (FFUSE3[0] - center[0], FFUSE3[1] - center[1], FFUSE3[2] - center[2])
    # chord direction
    C = (P[0] - FFUSE3[0], P[1] - FFUSE3[1], P[2] - FFUSE3[2])
    # tangent condition: R · C = 0
    dot = R[0]*C[0] + R[1]*C[1] + R[2]*C[2]
    return abs(dot) < 1e-10, dot

def chord_from_horn(theta):
    """Get chord from horn curve point at theta to FFUSE3."""
    P = horn_curve(theta)
    FFUSE3 = (2*LR, 0.0, 0.0)
    return (P[0] - FFUSE3[0], P[1] - FFUSE3[1], P[2] - FFUSE3[2])

print("=" * 60)
print("TANGENT CHORD ANALYSIS AT FFUSE₃ APEX")
print("Sphere: center (LR,0,0), radius LR =", LR)
print("FFUSE₃: (2, 0, 0)")
print("=" * 60)

# Test all 16 sectors
print("\n--- Horn Curve Sectors ---")
print(f"{'Sector':<8} {'θ°':<8} {'θ':<10} {'x':<10} {'z':<10} {'Tangent?':<10} {'R·C':<10}")
print("-" * 66)
for k in range(16):
    theta = k * math.pi / 8
    P = horn_curve(theta)
    is_tan, dot = chord_tangent_at_FFUSE3(P)
    C = chord_from_horn(theta)
    chord_len = math.sqrt(C[0]**2 + C[1]**2 + C[2]**2)
    print(f"{k:<8} {math.degrees(theta):<8.1f} {theta:<10.4f} {P[0]:<10.4f} {P[2]:<10.4f} {'YES' if is_tan else 'no':<10} {dot:<10.4f}")

# Show the tangent condition analytically
print("\n\n--- Analytical Tangent Condition ---")
print("Sphere: (x-1)² + y² + z² = 1")
print("FFUSE₃ at (2, 0, 0)")
print("Radius vector at FFUSE₃: R = (1, 0, 0)")
print("For chord P→FFUSE₃ to be tangent: R · (P - FFUSE₃) = 0")
print("=> (1,0,0) · (P_x - 2, P_y, P_z) = P_x - 2 = 0")
print("=> P_x = 2")

print("\nHorn curve: x(θ) = 2(1+cos θ), z(θ) = 2 sin θ")
print("x=2 => 2(1+cos θ) = 2 => cos θ = 0 => θ = π/2 or 3π/2")
print()

# Where is the FFUSE token?
theta_FFUSE = 6 * math.pi / 8  # sector 6
P_FFUSE = horn_curve(theta_FFUSE)
is_tan_FFUSE, _ = chord_tangent_at_FFUSE3(P_FFUSE)
print(f"FFUSE token at sector 6 (θ=135°): P = ({P_FFUSE[0]:.4f}, {P_FFUSE[2]:.4f})")
print(f"Chord to FFUSE₃ tangent? {'YES' if is_tan_FFUSE else 'NO'}")
print(f"P_x = {P_FFUSE[0]:.4f} — NOT 2, so chord is SECANT (penetrates sphere)")

print("\n\n--- Degenerate Limit: Evaluator Trine Collapse ---")
# The three evaluator chords approach FFUSE₃ from azimuthal directions
# In the limit where all three evaluators coincide with FFUSE₃:
# No split, no evaluation — the measurement collapses

# Show what happens as evaluator position approaches FFUSE₃ along the tangent direction
print("As evaluator approaches FFUSE₃ in yz-plane (tangent direction):")
for r in [2.0, 1.0, 0.5, 0.1, 0.01, 0.001]:
    # Point on y-axis: (2, r, 0) — tangent direction
    P = (2.0, r, 0.0)
    on_surface = sphere_surface(*P)
    is_tan, dot = chord_tangent_at_FFUSE3(P)
    C = (P[0] - 2*LR, P[1], P[2])
    chord_len = math.sqrt(C[0]**2 + C[1]**2 + C[2]**2)
    print(f"  P=({P[0]},{P[1]:.4f},{P[2]}): on_sphere={on_surface}, tang={is_tan}, |chord|={chord_len:.4f}")

print("\n--- Tangent Direction from Sector 4 (θ=90°) ---")
P4 = horn_curve(math.pi/2)
C4 = chord_from_horn(math.pi/2)
print(f"Sector 4: P = ({P4[0]:.4f}, {P4[1]:.4f}, {P4[2]:.4f})")
print(f"Chord to FFUSE₃: ({C4[0]:.4f}, {C4[1]:.4f}, {C4[2]:.4f})")
print(f"Chord length: {math.sqrt(C4[0]**2+C4[1]**2+C4[2]**2):.4f}")

# The tangent chord from sector 4
print("\n\n--- Significance: Tangent Chord from Sector 4 ---")
print("Sector 4 (θ=90°) is the ONLY horn curve sector whose chord to FFUSE₃")
print("is tangent to the sphere at FFUSE₃. This chord is purely in the z-direction.")
print()
print("The tangent chord from sector 4 is a structural null — it carries")
print("no radial information (x-component zero). It grazes the measurement")
print("apex externally.")
print()
print("In IMASM topology, the evaluator sequence uses sectors 0 (EVALT)")
print("and 5 (EVALF). Sector 4 is between them — a silent sector that")
print("carries the tangent, not the evaluation.")
print()
print("The tangent chord at FFUSE₃ is the degenerate limit of the evaluator")
print("trine collapse: when all three evaluator positions coincide, the")
print("azimuthal fiber degenerates to a point, and the chord becomes the")
print("pure-z tangent from sector 4 — no phase, no evaluation.")
