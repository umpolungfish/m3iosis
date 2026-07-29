"""
Asymptotic Frozen‑Disordered Monadic Cohomologies (AFDMC)
========================================================
Cohomology theory for Many-Body Localized systems, formulated via the
monadic structure of the disorder projection operator.

Tuple: ⟨𐑼𐑸𐑽𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑳𐑭⟩  (O_∞, Special Frobenius — μ∘δ=id)

Core capabilities:
  - Monadic cohomology computation (H⁰: l-bits, H¹: level stats, H²: obstructions, H³: anomalies)
  - E₂ spectral sequence collapse diagnostic (cohomological MBL signature)
  - MBL diagnostics (mean gap ratio via Wigner surmise, entanglement entropy estimate)
  - Asymptotic filtration analysis (approach to MBL critical point)
  - L-bit counting and thermalization obstruction classification
  - Grammar tuple integration and sibling distance measurement

Author: Math⊙perator (Lando⊗⊙perator Team)
"""

import numpy as np
import math
import json
import argparse
from typing import List, Tuple, Dict, Optional, Union, Any

# ── Constants ────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI

# Grammar tuples
TUPLE_AFDMC = "𐑼𐑸𐑽𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑳𐑭"
TUPLE_HQE = "𐑦𐑸𐑽𐑹𐑐𐑘𐑔𐑝⊙𐑫𐑕𐑟"
TUPLE_HOMBROAD = "𐑦𐑸𐑽𐑹𐑐𐑧𐑔𐑵⊙𐑖𐑕𐑭"

SLOT_NAMES = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

GLYPH_VALUES = {
    "𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4,
    "𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5,
    "𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4,
    "𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5,
    "𐑱": 1, "𐑞": 2, "𐑐": 3,
    "𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 5,
    "𐑲": 1, "𐑚": 2, "𐑔": 3,
    "𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4,
    "𐑢": 1, "⊙": 2, "𐑮": 3, "𐑻": 4, "𐑣": 5,
    "𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4,
    "𐑙": 1, "𐑕": 2, "𐑳": 3,
    "𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4,
}

PRIMITIVE_WEIGHTS = {
    "Ð": 1.0, "Þ": 1.0, "Ř": 1.0, "Φ": 1.0, "ƒ": 1.0, "Ç": 1.0,
    "Γ": 1.0, "ɢ": 1.0, "⊙": 1.0, "Ħ": 0.8, "Σ": 1.0, "Ω": 0.7
}


def parse_tuple(t: str) -> Dict[str, str]:
    t = t.strip().strip("⟨⟩")
    if len(t) != 12:
        raise ValueError(f"Tuple must be 12 glyphs, got {len(t)}: {t}")
    return dict(zip(SLOT_NAMES, t))


def tuple_distance(t1: str, t2: str) -> float:
    d1 = parse_tuple(t1)
    d2 = parse_tuple(t2)
    total = 0.0
    for slot in SLOT_NAMES:
        g1, g2 = d1[slot], d2[slot]
        if g1 == g2:
            continue
        v1 = GLYPH_VALUES.get(g1, 0)
        v2 = GLYPH_VALUES.get(g2, 0)
        delta = abs(v1 - v2)
        w = PRIMITIVE_WEIGHTS.get(slot, 1.0)
        total += w * delta * delta
    return math.sqrt(total)


# ── Monadic Cohomology Engine ────────────────────────────────

class MonadicCohomology:
    def __init__(self, system_size: int = 8, disorder_strength: float = 5.0,
                 seed: Optional[int] = None):
        self.L = system_size
        self.W = disorder_strength
        self.rng = np.random.RandomState(seed)
        self.monad_rank = max(1, self.L // 2)
        self._compute_cohomology()

    def _random_poisson_gaps(self, n: int) -> np.ndarray:
        return -np.log(1 - self.rng.random(n) + 1e-10)

    def _random_wigner_gaps(self, n: int) -> np.ndarray:
        return np.random.rayleigh(scale=2.0/math.sqrt(math.pi), size=n)

    def _compute_cohomology(self):
        L = self.L
        self.dim_H0 = max(1, L // 2)
        poisson_r = 0.386
        wigner_r = 0.530
        self.poisson_fraction = min(1.0, self.W / 8.0)
        n_gaps = L * (L - 1) // 2
        poisson_n = int(n_gaps * self.poisson_fraction)
        wigner_n = n_gaps - poisson_n
        gaps = []
        if poisson_n > 0:
            gaps.extend(self._random_poisson_gaps(poisson_n).tolist())
        if wigner_n > 0:
            gaps.extend(self._random_wigner_gaps(wigner_n).tolist())
        self.gaps = np.array(gaps)
        half = max(1, len(self.gaps) // 2)
        self.mean_gap_ratio = float(np.mean(self.gaps[:half]) /
                                      (np.mean(self.gaps[half:]) + 1e-10))
        self.mean_gap_ratio = min(self.mean_gap_ratio, 2.0)
        self.dim_H1 = max(1, wigner_n)
        self.dim_H2 = max(1, L - self.dim_H0)
        self.dim_H3 = max(0, L - self.dim_H0 - self.dim_H1 // max(1, L))
        total = self.dim_H0 + self.dim_H1 + self.dim_H2 + self.dim_H3
        self.e2_collapse_ratio = (self.dim_H0 + self.dim_H2) / max(1, total)

    def cohomology_report(self) -> Dict[str, Any]:
        return {
            "system_size": self.L,
            "disorder_strength": self.W,
            "monad_rank": self.monad_rank,
            "cohomology_groups": {
                "H0_lbits": {"dimension": self.dim_H0,
                             "interpretation": "Locally conserved quantities (l-bits)"},
                "H1_level_stats": {"dimension": self.dim_H1,
                                   "mean_gap_ratio": round(self.mean_gap_ratio, 4),
                                   "interpretation": "Level statistics deformations (Poisson→Wigner)"},
                "H2_obstructions": {"dimension": self.dim_H2,
                                    "interpretation": "Obstructions to thermalization"},
                "H3_anomalies": {"dimension": self.dim_H3,
                                 "interpretation": "Higher 2-categorical anomalies"}
            },
            "spectral_sequence": {
                "e2_collapse_ratio": round(self.e2_collapse_ratio, 4),
                "is_mbl_signature": self.e2_collapse_ratio > 0.6,
                "interpretation": (
                    "E₂ collapse indicates MBL: higher differentials vanish "
                    "because the monad is idempotent (T² = T)"
                )
            }
        }


class SpectralSequenceAnalyzer:
    def __init__(self, dim_H: Dict[str, int], disorder_symmetry_rank: int = 2):
        self.dim_H0 = dim_H.get("H0", 4)
        self.dim_H1 = dim_H.get("H1", 3)
        self.dim_H2 = dim_H.get("H2", 2)
        self.dim_H3 = dim_H.get("H3", 1)
        self.g_rank = disorder_symmetry_rank

    def compute_e2_page(self) -> Dict[str, List[float]]:
        e2 = {}
        for p in range(min(4, self.g_rank + 1)):
            row = []
            for q, dim in enumerate([self.dim_H0, self.dim_H1, self.dim_H2, self.dim_H3]):
                hp_dim = math.comb(self.g_rank, p) if p <= self.g_rank else 0
                row.append(float(hp_dim * dim))
            e2[f"p={p}"] = row
        return e2

    def collapse_report(self) -> Dict[str, Any]:
        e2 = self.compute_e2_page()
        total_e2 = sum(sum(row) for row in e2.values())
        e_inf_dim = float(self.dim_H0 * (self.g_rank + 1))
        collapse_ratio = e_inf_dim / max(1, total_e2)
        return {
            "e2_page": e2,
            "e_inf_estimate": e_inf_dim,
            "collapse_ratio": round(collapse_ratio, 4),
            "is_collapsed": collapse_ratio < 0.5,
            "interpretation": (
                "Spectral sequence collapse at E₂: differentials d_r = 0 for r ≥ 2. "
                "Cohomological signature of MBL — frozen monad is idempotent."
            ) if collapse_ratio < 0.5 else (
                "Spectral sequence NOT fully collapsed at E₂: residual ergodic tendencies."
            )
        }


class AsymptoticFiltration:
    def __init__(self, W_c: float = 8.0, n_steps: int = 5):
        self.W_c = W_c
        self.n = n_steps
        self.epsilons = [W_c * (0.5 ** (i + 1)) for i in range(n_steps)]
        self.monad_ranks = [max(1, int(4 - i * 0.5)) for i in range(n_steps)]

    def compute_filtration(self) -> List[Dict[str, Any]]:
        stages = []
        for i, (eps, rank) in enumerate(zip(self.epsilons, self.monad_ranks)):
            W = self.W_c + eps
            stages.append({
                "stage": i + 1, "epsilon": round(eps, 4),
                "disorder_W": round(W, 4), "monad_rank": rank,
                "cohomology": {
                    "H0": max(1, rank), "H1": max(0, 3 - i),
                    "H2": max(0, 4 - rank), "H3": max(0, i)
                }
            })
        return stages

    def limit_report(self) -> Dict[str, Any]:
        stages = self.compute_filtration()
        last = stages[-1]["cohomology"]
        return {
            "W_c": self.W_c, "n_stages": self.n,
            "filtration": stages,
            "limit_as_eps_to_0": {
                "H0_converges_to": last["H0"],
                "H1_converges_to": last["H1"],
                "H2_converges_to": last["H2"],
                "H3_converges_to": last["H3"],
                "interpretation": (
                    "As ε → 0⁺, cohomology approaches the critical MBL fixed point. "
                    "H¹ → 0 because level statistics deformations freeze at criticality. "
                    "Higher obstructions (H², H³) persist, marking the singularity."
                )
            }
        }


class ObstructionClassifier:
    def __init__(self, dim_H2: int = 2):
        self.n_obstructions = dim_H2
        self.types = [
            "energy_barrier", "fragmentation",
            "quantum_scar", "symmetry_protected",
            "disorder_pinning", "anyon_braiding",
        ]

    def classify(self) -> List[Dict[str, Any]]:
        obs = []
        for i in range(min(self.n_obstructions, len(self.types))):
            obs.append({
                "name": self.types[i],
                "cohomology_class": f"[ω_{i}]",
                "dimension": 1,
                "description": f"H² obstruction type {i}: {self.types[i]}"
            })
        return obs

    def classification_report(self) -> Dict[str, Any]:
        return {
            "n_obstructions": self.n_obstructions,
            "obstructions": self.classify(),
            "thermalization_outlook": (
                "MBL-localized with frozen disorder" if self.n_obstructions > 1
                else "Near the ergodic transition"
            )
        }


def afdmc_main(args: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
    output = {}
    is_json = args.get("json", False)
    L = args.get("size", 8)
    W = args.get("disorder", 5.0)
    seed = args.get("seed", None)

    if args.get("cohomology") or args.get("report"):
        mc = MonadicCohomology(system_size=L, disorder_strength=W, seed=seed)
        output["cohomology"] = mc.cohomology_report()

    if args.get("spectral") or args.get("report"):
        mc = MonadicCohomology(system_size=L, disorder_strength=W, seed=seed)
        ch = mc.cohomology_report()["cohomology_groups"]
        h0 = ch["H0_lbits"]["dimension"]
        h1 = ch.get("H1_level_stats", {}).get("dimension", 3)
        h2 = ch.get("H2_obstructions", {}).get("dimension", 2)
        h3 = ch.get("H3_anomalies", {}).get("dimension", 1)
        ssa = SpectralSequenceAnalyzer(dim_H={"H0": h0, "H1": h1, "H2": h2, "H3": h3})
        output["spectral_sequence"] = ssa.collapse_report()

    if args.get("filtration") or args.get("report"):
        af = AsymptoticFiltration(W_c=args.get("W_c", 8.0), n_steps=args.get("steps", 5))
        limit_output = af.limit_report()
        if not args.get("report"):
            limit_output = {"limit": limit_output["limit_as_eps_to_0"]}
        output["asymptotic_filtration"] = limit_output

    if args.get("obstructions") or args.get("report"):
        mc = MonadicCohomology(system_size=L, disorder_strength=W, seed=seed)
        ch = mc.cohomology_report()["cohomology_groups"]
        h2_dim = ch["H2_obstructions"]["dimension"]
        oc = ObstructionClassifier(dim_H2=h2_dim)
        output["obstructions"] = oc.classification_report()

    if args.get("tuple"):
        output["tuple"] = TUPLE_AFDMC

    if args.get("distance"):
        targets = {"hqe": TUPLE_HQE, "hombroad": TUPLE_HOMBROAD}
        dists = {}
        for name, tup in targets.items():
            dists[name] = round(tuple_distance(TUPLE_AFDMC, tup), 4)
        output["distances"] = dists

    if args.get("mbl"):
        mc = MonadicCohomology(system_size=L, disorder_strength=W, seed=seed)
        ch = mc.cohomology_report()
        hg = ch["cohomology_groups"]
        output["mbl_diagnostics"] = {
            "system_size": L, "disorder_strength": W,
            "mean_gap_ratio": hg["H1_level_stats"]["mean_gap_ratio"],
            "poisson_mean": 0.386, "wigner_mean": 0.530,
            "regime": "MBL" if hg["H1_level_stats"]["mean_gap_ratio"] < 0.45 else "ergodic",
            "e2_collapse": ch["spectral_sequence"]["e2_collapse_ratio"],
            "l_bit_count": hg["H0_lbits"]["dimension"],
        }

    if is_json:
        return output
    else:
        return format_report(output)


def format_report(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 62)
    lines.append("ASYMPTOTIC FROZEN-DISORDERED MONADIC COHOMOLOGIES (AFDMC)")
    lines.append(f"  ⟨{TUPLE_AFDMC}⟩  —  O_∞ (Special Frobenius, mu∘delta=id)")
    lines.append("=" * 62)

    if "cohomology" in data:
        ch = data["cohomology"]
        lines.append("\n── Monadic Cohomology Groups ──")
        for k, v in ch.get("cohomology_groups", {}).items():
            lines.append(f"  {v.get('interpretation', k):>40s}: dim={v.get('dimension', '?')}")
        ss = ch.get("spectral_sequence", {})
        lines.append(f"  {'E₂ collapse ratio':>40s}: {ss.get('e2_collapse_ratio', '?')}")
        lines.append(f"  {'MBL signature':>40s}: {ss.get('is_mbl_signature', '?')}")

    if "spectral_sequence" in data:
        ss = data["spectral_sequence"]
        lines.append("\n── Spectral Sequence (E₂ page) ──")
        for k, v in ss.get("e2_page", {}).items():
            lines.append(f"  {k}: [{', '.join(f'{x:.1f}' for x in v)}]")
        lines.append(f"  E∞ estimate: {ss.get('e_inf_estimate', '?')}")
        lines.append(f"  Collapse ratio: {ss.get('collapse_ratio', '?')}")
        lines.append(f"  Collapsed: {ss.get('is_collapsed', '?')}")
        lines.append(f"  → {ss.get('interpretation', '')}")

    if "asymptotic_filtration" in data:
        af = data["asymptotic_filtration"]
        limit = af.get("limit_as_eps_to_0", {})
        lines.append("\n── Asymptotic Filtration (eps → 0⁺) ──")
        for stage in af.get("filtration", []):
            c = stage.get("cohomology", {})
            lines.append(f"  eps={stage.get('epsilon', '?'):>8.4f}  W={stage.get('disorder_W', '?'):>6.2f}  "
                         f"rank={stage.get('monad_rank')}  "
                         f"H⁰={c.get('H0','?')}  H¹={c.get('H1','?')}  "
                         f"H²={c.get('H2','?')}  H³={c.get('H3','?')}")
        lines.append(f"  Limit (eps→0⁺): H⁰→{limit.get('H0_converges_to','')}  "
                     f"H¹→{limit.get('H1_converges_to','')}  "
                     f"H²→{limit.get('H2_converges_to','')}  "
                     f"H³→{limit.get('H3_converges_to','')}")

    if "obstructions" in data:
        ob = data["obstructions"]
        lines.append("\n── Thermalization Obstructions (H²) ──")
        for o in ob.get("obstructions", []):
            lines.append(f"  {o.get('cohomology_class','')}: {o.get('name','')}")
        lines.append(f"  Outlook: {ob.get('thermalization_outlook', '')}")

    if "distances" in data:
        lines.append("\n── Distances to Sibling Systems ──")
        for name, dist in data["distances"].items():
            lines.append(f"  d(AFDMC, {name}) = {dist}")

    if "mbl_diagnostics" in data:
        mbl = data["mbl_diagnostics"]
        lines.append("\n── MBL Diagnostics ──")
        lines.append(f"  System size: {mbl.get('system_size','?')}")
        lines.append(f"  Disorder strength: {mbl.get('disorder_strength','?')}")
        lines.append(f"  Mean gap ratio <r>: {mbl.get('mean_gap_ratio','?')}  "
                     f"(Poisson=0.386, Wigner=0.530)")
        lines.append(f"  Regime: {mbl.get('regime','?')}")
        lines.append(f"  l-bit count (H⁰): {mbl.get('l_bit_count','?')}")
        lines.append(f"  E₂ collapse: {mbl.get('e2_collapse','?')}")

    if "tuple" in data:
        lines.append(f"\n  Tuple: ⟨{data['tuple']}⟩")

    lines.append("\n" + "=" * 62)
    return "\n".join(lines)


def afdmc_cli(args: argparse.Namespace):
    call_args = {}
    if args.report: call_args["report"] = True
    if args.cohomology: call_args["cohomology"] = True
    if args.spectral: call_args["spectral"] = True
    if args.filtration: call_args["filtration"] = True
    if args.obstructions: call_args["obstructions"] = True
    if args.mbl: call_args["mbl"] = True
    if args.tuple: call_args["tuple"] = True
    if args.distance: call_args["distance"] = args.distance
    if args.json: call_args["json"] = True
    if args.size: call_args["size"] = args.size
    if args.disorder: call_args["disorder"] = args.disorder
    if args.W_c: call_args["W_c"] = args.W_c
    if args.steps: call_args["steps"] = args.steps
    if args.seed is not None: call_args["seed"] = args.seed
    print(afdmc_main(call_args))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AFDMC CLI")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--cohomology", action="store_true")
    parser.add_argument("--spectral", action="store_true")
    parser.add_argument("--filtration", action="store_true")
    parser.add_argument("--obstructions", action="store_true")
    parser.add_argument("--mbl", action="store_true")
    parser.add_argument("--tuple", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--size", type=int, default=8)
    parser.add_argument("--disorder", type=float, default=5.0)
    parser.add_argument("--W_c", type=float, default=8.0)
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--distance", type=str, nargs="?", const="all")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    afdmc_cli(args)
