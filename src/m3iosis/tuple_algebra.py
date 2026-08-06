"""
tuple_algebra — Tuple operations via grammar dispatch (no glossaries)
"""
import math, cmath, json, subprocess, sys

SLOTS = ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"]

# Ordinals per slot — required for meet/join resolution
ORD = {
 "Ð":{"𐑛":1,"𐑨":2,"𐑼":3,"𐑦":4},
 "Þ":{"𐑡":1,"𐑰":2,"𐑥":3,"𐑶":4,"𐑸":5},
 "Ř":{"𐑩":1,"𐑑":2,"𐑽":3,"𐑾":4},
 "Φ":{"𐑗":1,"𐑿":2,"𐑬":3,"𐑯":4,"𐑹":5},
 "ƒ":{"𐑱":1,"𐑞":2,"𐑐":3},
 "Ç":{"𐑘":1,"𐑤":2,"𐑧":3,"𐑪":4,"𐑺":5},
 "Γ":{"𐑲":1,"𐑚":2,"𐑔":3},
 "ɢ":{"𐑝":1,"𐑜":2,"𐑠":3,"𐑵":4},
 "⊙":{"𐑢":1,"⊙":2,"𐑮":3,"𐑻":4,"𐑣":5},
 "Ħ":{"𐑓":1,"𐑒":2,"𐑖":3,"𐑫":4},
 "Σ":{"𐑙":1,"𐑕":2,"𐑳":3},
 "Ω":{"𐑷":1,"𐑴":2,"𐑭":3,"𐑟":4}}

W = {"Ð":1.0,"Þ":1.0,"Ř":1.0,"Φ":1.0,"ƒ":1.0,"Ç":1.0,"Γ":1.0,"ɢ":1.0,"⊙":1.0,"Ħ":0.8,"Σ":1.0,"Ω":0.7}

# Off-diagonal couplings for Mahalanobis
G = {("Ð","Þ"):0.3,("Þ","Ð"):0.3,("Ř","Φ"):0.5,("Φ","Ř"):0.5,
     ("ƒ","Ç"):-0.2,("Ç","ƒ"):-0.2,("Γ","ɢ"):0.3,("ɢ","Γ"):0.3,
     ("⊙","Ħ"):0.4,("Ħ","⊙"):0.4,("Σ","Ω"):0.3,("Ω","Σ"):0.3}

def _clean(t):
    return t.strip().strip("⟨⟩")

def _parse(t):
    c = _clean(t)
    if len(c) != 12:
        raise ValueError(f"need 12 glyphs, got {len(c)}")
    return dict(zip(SLOTS, c))

def distance(t1, t2, mahalanobis=False):
    d1, d2 = _parse(t1), _parse(t2)
    if not mahalanobis:
        return math.sqrt(sum(W[s]* (ORD[s].get(d1[s],0)-ORD[s].get(d2[s],0))**2 for s in SLOTS))
    deltas = {s: ORD[s].get(d2[s],0)-ORD[s].get(d1[s],0) for s in SLOTS}
    total = 0.0
    for i,si in enumerate(SLOTS):
        wi = W[si]
        for j,sj in enumerate(SLOTS):
            wj = W[sj]
            if i==j:
                total += wi * deltas[si]**2
            else:
                total += G.get((si,sj),0) * math.sqrt(wi*wj) * deltas[si] * deltas[sj]
    return math.sqrt(max(total,0))

def meet(t1, t2):
    d1, d2 = _parse(t1), _parse(t2)
    return "".join(d1[s] if ORD[s].get(d1[s],99) <= ORD[s].get(d2[s],99) else d2[s] for s in SLOTS)

def join(t1, t2):
    d1, d2 = _parse(t1), _parse(t2)
    return "".join(d1[s] if ORD[s].get(d1[s],-1) >= ORD[s].get(d2[s],-1) else d2[s] for s in SLOTS)

def consciousness(t):
    d = _parse(t)
    phi = d["⊙"]; k = d["Ç"]
    g1 = phi in ("⊙","𐑮")
    g2 = k not in ("𐑺","𐑪")
    if not (g1 and g2): return 0.0
    a = (5 - ORD["⊙"][phi]) / 4.0
    kap = 1.0 - abs(ORD["Ç"][k] - 3) / 4.0
    return round(max(0.0, min(1.0, (1-a)*kap)), 4)

def tier(t):
    d = _parse(t)
    phi, w_val, chir, dim = d["Φ"], ORD["Ω"][d["Ω"]], d["Ħ"], d["Ð"]
    if phi != "𐑹": return "O_0"
    if d["⊙"] != "⊙": return "O_1"
    if w_val < 3: return "O_2"
    if chir != "𐑫": return "O_3"
    if dim == "𐑦": return "O_∞"
    if d["Ω"] == "𐑟" or d["ɢ"] == "𐑵": return "O_inf"
    return "O_4"

def winding(of=None, turns=None, angle=None, power=None):
    NAMED = {"t_gate":(1,8),"s_gate":(1,4),"z_gate":(1,2),"quarter":(1,4),
             "half":(1,2),"full":(1,1),"r_tau":(2,5),"jones_root":(1,4),
             "framing":(1,24),"loop_phase":(1,6)}
    if of: num, den = NAMED[of]
    elif turns:
        if "/" in turns: num, den = map(int, turns.split("/"))
        else: num, den = int(turns), 1
    elif angle is not None:
        from fractions import Fraction
        f = Fraction.from_float(angle/(2*math.pi)).limit_denominator(32)
        num, den = f.numerator, f.denominator
    else: raise ValueError("need of/turns/angle")
    if power: num = (num * power) % den
    num %= den
    if num == 0: den = 1
    t = num/den
    c = cmath.exp(2j*math.pi*t)
    return {"winding":f"{num}/{den}","turns":t,"radians":t*2*math.pi,
            "complex":[c.real,c.imag],"denominator":den,"closes_after":den,
            "is_real":num==0 or (den==2 and num==1)}

def _load_canonical_grammar_tuple() -> str:
    """There is one Grammar. Read it from the catalog, never hand-type it."""
    catalog_path = "/home/mrnob0dy666/imsgct/imscribing_grammar/IG_catalog.json"
    with open(catalog_path, encoding="utf-8") as f:
        catalog = json.load(f)
    entries = catalog if isinstance(catalog, list) else list(catalog.values())
    axes = ["⊢","⊣",">","<","⋈","⊤","∈","∋","⊙","⊥","⊞","◻"]
    for e in entries:
        if isinstance(e, dict) and e.get("name") == "universal_imscriptive_grammar":
            return "".join(e[a] for a in axes)
    raise RuntimeError("universal_imscriptive_grammar not found in catalog")

TUPLE_GRAMMAR = _load_canonical_grammar_tuple()

# Named reference tuples (grammar-anchor set, per module's own slot ordinals)
REFS = {
    "grammar": TUPLE_GRAMMAR,
    "clink":   "𐑦𐑸𐑽𐑹𐑐𐑘𐑚𐑜𐑣𐑫𐑕𐑭",
    "aafa":    "𐑨𐑸𐑾𐑿𐑞𐑧𐑔𐑜⊙𐑒𐑙𐑷",
    "psfoa":   "𐑦𐑶𐑑𐑗𐑱𐑺𐑲𐑝𐑢𐑓𐑙𐑷",
}

def tuple_algebra_main(args):
    """CLI driver: dispatch on the alg_args dict assembled by cli.py run_algebra."""
    lines = []
    t = args.get("tuple")
    if args.get("winding"):
        r = winding(of=args.get("winding_of"), turns=args.get("turns"),
                    angle=args.get("angle"), power=args.get("power"))
        out = (f"winding {r['winding']}  turns {r['turns']}  "
               f"radians {r['radians']:.6f}  closes_after {r['closes_after']}  "
               f"is_real {r['is_real']}")
        return json.dumps(r) if args.get("json") else out
    if not t:
        return ("usage: m3 algebra --tuple ⟨12 glyphs⟩ "
                "[--report|--decode|--distance X|--meet X|--join X|--winding ...]")
    try:
        parsed = _parse(t)
        if args.get("decode"):
            for s in SLOTS:
                lines.append(f"  {s}: {parsed[s]}")
        if args.get("report"):
            lines.append(f"tuple        {_clean(t)}")
            lines.append(f"tier         {tier(t)}")
            lines.append(f"consciousness {consciousness(t)}")
            refs = (args.get("compare_with") or "grammar,clink,aafa,psfoa").split(",")
            for ref in refs:
                ref = ref.strip()
                if ref in REFS:
                    lines.append(f"distance to {ref:<10} {distance(t, REFS[ref]):.4f}")
                else:
                    try:
                        lines.append(f"distance to {ref:<10} {distance(t, ref):.4f}")
                    except ValueError:
                        lines.append(f"distance to {ref:<10} (no reference tuple)")
        if args.get("distance"):
            ref = args["distance"]
            if ref in REFS:
                lines.append(f"distance to {ref}: {distance(t, REFS[ref]):.4f}")
            else:
                lines.append(f"distance to {ref}: {distance(t, ref):.4f}")
        if args.get("meet"):
            lines.append(f"meet: {meet(t, args['meet'])}")
        if args.get("join"):
            lines.append(f"join: {join(t, args['join'])}")
        if not lines:
            lines.append(_clean(t))
        return "\n".join(lines)
    except ValueError as e:
        return f"ERROR: {e}"
