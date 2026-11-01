"""Concept heat and material balance of the methylamines plant (DESIGN.md D-006).

Run: cheme run scripts/mass_balance.py  -> prints a summary, writes build/streams.yaml
(the stream entries of process/flowsheet.yaml, pasted from there by hand).

Model (every choice is a DESIGN.md decision, values ASSUMED unless a source is named):
- converter R-101: ideal-gas equilibrium of MMA_SYN, DMA_SYN, TMA_SYN at the outlet
  temperature (the three reactions conserve moles: pressure has no effect), adiabatic; data of
  process/materials.yaml, the same model cheme's equilibrium reactor applies (D-005);
- recycle loop solved for the net product slate of the design basis at a fixed N/C ratio of the
  converter feed: all ammonia and the TMA recycle return as C-101 distillate (D-007), the MMA
  recycle is split off the C-103 distillate, unconverted methanol returns from C-105;
- columns as sharp splits (D-008); the only loss is methanol in the wastewater (100 ppm(wt));
- enthalpies: ideal gas from the cp_R polynomials, liquid = ideal gas minus the heat of
  vaporisation of each component (thermo 0.6.1), no mixing enthalpy; reboiler duty from the
  column energy balance with condenser duty (R + 1) D dHvap (D-006: +/-30 %).
"""
import math
from pathlib import Path

import yaml
from scipy.optimize import least_squares
from thermo import Chemical

ROOT = Path(__file__).resolve().parents[1]
R = 8.314462618
T0 = 298.15
mat = yaml.safe_load((ROOT / "process/materials.yaml").read_text())
COMP = [c["id"] for c in mat["components"]]
MW = {c["id"]: c["molar_mass"] for c in mat["components"]}
IG = {c["id"]: c["ideal_gas"] for c in mat["components"]}
NAMES = {"NH3": "ammonia", "CH3OH": "methanol", "MMA": "methylamine", "DMA": "dimethylamine",
         "TMA": "trimethylamine", "H2O": "water"}
CHEM = {k: Chemical(v) for k, v in NAMES.items()}
NATOM = {"NH3": 1, "CH3OH": 0, "MMA": 1, "DMA": 1, "TMA": 1, "H2O": 0}
CATOM = {"NH3": 0, "CH3OH": 1, "MMA": 1, "DMA": 2, "TMA": 3, "H2O": 0}
RXN = [{"CH3OH": -1, "NH3": -1, "MMA": 1, "H2O": 1},
       {"CH3OH": -1, "MMA": -1, "DMA": 1, "H2O": 1},
       {"CH3OH": -1, "DMA": -1, "TMA": 1, "H2O": 1}]

# ---- design basis (process/design-basis.yaml) -------------------------------------------
PRODUCT = {"MMA": 2000.0, "DMA": 4400.0, "TMA": 1600.0}   # kg/h net, ASSUMED slate (D-002)
N_TO_C = 2.0          # converter feed N/C, ASSUMED (D-004)
T_RX_OUT = 713.15     # converter outlet 440 C, ASSUMED: inlet and outlet inside 350-450 C (D-004)
P_RX_IN, P_RX_OUT = 2200.0, 2000.0
T_VAP = 453.15        # E-101 outlet, superheated vapour, ASSUMED
WW_MEOH_PPM = 100.0   # methanol in the wastewater, ASSUMED (D-008)
SOLVENT_RATIO = 1.0   # C-102 extraction water per kg of C-102 feed, ASSUMED (D-008)
ETA_PUMP = 0.6        # pump efficiency, ASSUMED
MIN_BOILUP = 0.1      # kmol vapour per kmol bottoms at least, ASSUMED (D-008)
COLUMNS = {           # top pressure kPa(a), reflux ratio (ASSUMED, D-008)
    "C101": (1900.0, 1.0), "C102": (500.0, 3.0), "C103": (600.0, 1.0),
    "C104": (600.0, 4.0), "C105": (150.0, 1.5)}


def h_ig(c, T):
    a = IG[c]["cp_R"]
    integ = sum(a[i] / (i + 1) * (T ** (i + 1) - T0 ** (i + 1)) for i in range(5))
    return IG[c]["dHf_298"] + R * integ          # kJ/kmol


def s_ig(c, T):
    a = IG[c]["cp_R"]
    integ = a[0] * math.log(T / T0) + sum(a[i] / i * (T ** i - T0 ** i) for i in range(1, 5))
    return IG[c]["S_298"] + R * integ             # kJ/(kmol K), at 1 bar


def lnK(rxn, T):
    dg = sum(nu * (h_ig(c, T) - T * s_ig(c, T)) for c, nu in rxn.items())
    return -dg / (R * T)


def hvap(c, T):
    return CHEM[c].EnthalpyVaporization(T) or 0.0   # J/mol = kJ/kmol; 0 above Tc


def H(n, T, phase):
    """Enthalpy flow kJ/h of molar flows n (kmol/h)."""
    return sum(v * (h_ig(c, T) - (hvap(c, T) if phase == "liquid" else 0.0)) for c, v in n.items() if v)


def solve_T(n, phase, target, lo=200.0, hi=900.0):
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if H(n, mid, phase) > target:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def psat(c, T):
    return CHEM[c].VaporPressure(T) / 1000.0     # kPa


def bubble_T(n, P):
    """Ideal (Raoult) bubble temperature, a rough estimate (D-006)."""
    tot = sum(n.values())
    lo, hi = 150.0, 600.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        p = sum(v / tot * psat(c, mid) for c, v in n.items() if v)
        lo, hi = (mid, hi) if p < P else (lo, mid)
    return 0.5 * (lo + hi)


def equilibrium(nin, T):
    lnKs = [lnK(r, T) for r in RXN]

    def res(x):
        n = {c: nin.get(c, 0.0) for c in COMP}
        for xi, r in zip(x, RXN):
            for c, nu in r.items():
                n[c] += nu * xi
        out = []
        for lk, r in zip(lnKs, RXN):
            out.append(sum(nu * math.log(max(n[c], 1e-12)) for c, nu in r.items()) - lk)
        return out

    x0 = [0.3 * nin["CH3OH"], 0.2 * nin["CH3OH"], 0.1 * nin["CH3OH"]]
    sol = least_squares(res, x0, xtol=1e-14, ftol=1e-14, gtol=1e-14)
    n = {c: nin.get(c, 0.0) for c in COMP}
    for xi, r in zip(sol.x, RXN):
        for c, nu in r.items():
            n[c] += nu * xi
    assert min(n.values()) > -1e-9, n
    return n, sol.x, lnKs


# ---- fresh feeds from the product slate -----------------------------------------------
P = {c: PRODUCT[c] / MW[c] for c in PRODUCT}           # kmol/h
water_made = sum(CATOM[c] * P[c] for c in P)            # one water per methyl group
meoh_loss = None


def loop(x):
    r_nh3, r_tma, r_mma, r_meoh = x
    water_kg = water_made * MW["H2O"]
    loss = WW_MEOH_PPM * 1e-6 * water_kg / MW["CH3OH"]
    fresh = {"CH3OH": water_made + loss, "NH3": sum(P.values())}
    feed = {c: 0.0 for c in COMP}
    feed["CH3OH"] = fresh["CH3OH"] + r_meoh
    feed["NH3"] = fresh["NH3"] + r_nh3
    feed["TMA"] = r_tma
    feed["MMA"] = r_mma
    out, ext, lnKs = equilibrium(feed, T_RX_OUT)
    return fresh, feed, out, ext, loss


def residuals(x):
    fresh, feed, out, ext, loss = loop(x)
    nc = sum(NATOM[c] * feed[c] for c in COMP) / sum(CATOM[c] * feed[c] for c in COMP)
    return [(nc - N_TO_C) * 10,
            out["NH3"] - x[0], out["TMA"] - P["TMA"] - x[1], out["MMA"] - P["MMA"] - x[2],
            out["CH3OH"] - loss - x[3], out["DMA"] - P["DMA"]]


sol = least_squares(residuals, [400.0, 30.0, 30.0, 5.0], bounds=([1, 0, 0, 0], [1e5] * 4),
                    xtol=1e-14, ftol=1e-14, gtol=1e-14)
fresh, feed, out, ext, loss = loop(sol.x)
r_nh3, r_tma, r_mma, r_meoh = sol.x
print("residuals", [round(v, 6) for v in residuals(sol.x)])

# check of the equilibrium model against the published equilibrium at 400 C and N/C 2.0
# (US 4,485,261 A, background: fractions MMA 0.288, DMA 0.279, TMA 0.433 among the amines)
chk, _, _ = equilibrium({"CH3OH": 1.0, "NH3": 2.0}, 673.15)
am_m = sum(chk[c] for c in ("MMA", "DMA", "TMA"))
am_w = sum(chk[c] * MW[c] for c in ("MMA", "DMA", "TMA"))
print("check 673.15 K, N/C 2, methanol + ammonia only: mole fractions",
      {c: round(chk[c] / am_m, 3) for c in ("MMA", "DMA", "TMA")}, "mass fractions",
      {c: round(chk[c] * MW[c] / am_w, 3) for c in ("MMA", "DMA", "TMA")},
      "methanol conversion %.4f" % (1 - chk["CH3OH"]))

# ---- stream molar flows ---------------------------------------------------------------
z = lambda **kw: {c: kw.get(c, 0.0) for c in COMP}
water_out = out["H2O"]
S = {}
S["S1"] = z(CH3OH=fresh["CH3OH"])
S["S2"] = z(NH3=fresh["NH3"])
S["S10"] = z(NH3=out["NH3"], TMA=r_tma)
S["S17"] = z(MMA=r_mma)
S["S20"] = z(CH3OH=r_meoh)
S["S3"] = {c: S["S1"][c] + S["S2"][c] + S["S10"][c] + S["S17"][c] + S["S20"][c] for c in COMP}
S["S4"] = dict(S["S3"]); S["S5"] = dict(S["S3"]); S["S6"] = dict(S["S3"])
S["S7"] = dict(out); S["S8"] = dict(out); S["S9"] = dict(out)
S["S11"] = {c: out[c] - S["S10"][c] for c in COMP}
S["S12"] = z(TMA=P["TMA"])
feed_c102_kg = sum(S["S11"][c] * MW[c] for c in COMP)
solvent = SOLVENT_RATIO * feed_c102_kg / MW["H2O"]
# SPW splits C-105 bottoms (water with its methanol) into extraction water and wastewater: the
# methanol in the bottoms is the wastewater's 100 ppm divided by the wastewater fraction
f_solv = solvent / (solvent + water_out)
S["S21"] = z(H2O=water_out + solvent, CH3OH=loss / (1.0 - f_solv))
S["S22"] = {c: f_solv * v for c, v in S["S21"].items()}
S["S23"] = {c: (1.0 - f_solv) * v for c, v in S["S21"].items()}
S["S13"] = {c: S["S11"][c] + S["S22"][c] - S["S12"][c] for c in COMP}
S["S14"] = z(MMA=out["MMA"], DMA=P["DMA"])       # C-103 (dehydration) distillate
S["S15"] = z(MMA=out["MMA"])                     # C-104 distillate
S["S16"] = z(MMA=P["MMA"])
S["S18"] = z(DMA=P["DMA"])                       # C-104 bottoms
S["S19"] = {c: S["S13"][c] - S["S14"][c] for c in COMP}   # C-103 bottoms
for k, v in S.items():
    assert min(v.values()) > -1e-9, (k, v)
    S[k] = {c: max(x, 0.0) for c, x in v.items()}

# ---- conditions and energy --------------------------------------------------------------
Tc = {}
Pp = {"S1": 300.0, "S2": 1500.0, "S3": 1500.0, "S4": 2400.0, "S5": 2300.0, "S6": P_RX_IN,
      "S7": P_RX_OUT, "S8": 1950.0, "S9": 1900.0}
Pp.update({"S10": 1900.0, "S11": 1950.0, "S12": 500.0, "S13": 550.0, "S14": 600.0,
           "S15": 600.0, "S16": 600.0, "S17": 600.0, "S18": 650.0, "S19": 650.0,
           "S20": 150.0, "S21": 200.0, "S22": 200.0, "S23": 200.0})
Tc["S1"] = 303.15
Tc["S2"] = 298.15
for k, col in [("S10", "C101"), ("S12", "C102"), ("S14", "C103"), ("S15", "C104"), ("S20", "C105")]:
    Tc[k] = bubble_T(S[k], COLUMNS[col][0])
Tc["S16"] = Tc["S17"] = Tc["S15"]
for k in ["S11", "S13", "S18", "S19", "S21"]:
    Tc[k] = bubble_T(S[k], Pp[k])
Tc["S22"] = Tc["S23"] = Tc["S21"]
# mixer M-101 (adiabatic, liquids)
hin = sum(H(S[k], Tc[k], "liquid") for k in ["S1", "S2", "S10", "S17", "S20"])
Tc["S3"] = solve_T(S["S3"], "liquid", hin)
Tc["S4"] = Tc["S3"]   # pump temperature rise neglected
Tc["S5"] = T_VAP
Tc["S7"] = T_RX_OUT
# adiabatic converter: inlet temperature from H(in) = H(out), formation-enthalpy basis
Tc["S6"] = solve_T(S["S6"], "vapour", H(S["S7"], T_RX_OUT, "vapour"))
q_e102 = H(S["S6"], Tc["S6"], "vapour") - H(S["S5"], T_VAP, "vapour")
Tc["S8"] = solve_T(S["S8"], "vapour", H(S["S7"], T_RX_OUT, "vapour") - q_e102)
Tc["S9"] = 313.15
Q = {}
Q["E101"] = H(S["S5"], T_VAP, "vapour") - H(S["S4"], Tc["S4"], "liquid")
Q["E102"] = q_e102
Q["E103"] = H(S["S8"], Tc["S8"], "vapour") - H(S["S9"], Tc["S9"], "liquid")
vol = sum(sum(S[k][c] * 1000.0 * CHEM[c].VolumeLiquid(298.15, 2.0e6) for c in COMP if S[k][c]) * (2400.0 - Pp[k])
          for k in ["S1", "S2", "S10", "S17", "S20"])       # m3/h * kPa = kJ/h
Q["P101"] = vol / ETA_PUMP
cols = {"C101": (["S9"], ["S10", "S11"], "S10"), "C102": (["S11", "S22"], ["S12", "S13"], "S12"),
        "C103": (["S13"], ["S14", "S19"], "S14"), "C104": (["S14"], ["S15", "S18"], "S15"),
        "C105": (["S19"], ["S20", "S21"], "S20")}
for col, (ins, outs, top) in cols.items():
    rr = COLUMNS[col][1]
    qc = (rr + 1) * sum(S[top][c] * hvap(c, Tc[top]) for c in COMP if S[top][c])
    hi = sum(H(S[k], Tc[k], "liquid") for k in ins)
    ho = sum(H(S[k], Tc[k], "liquid") for k in outs)
    bot = outs[1]
    # a column fed hotter than its bottoms still needs stripping vapour: at least
    # MIN_BOILUP kmol of vapour per kmol of bottoms (ASSUMED, D-008); the condenser then takes
    # the rest of the column's energy balance
    qmin = MIN_BOILUP * sum(S[bot][c] * hvap(c, Tc[bot]) for c in COMP if S[bot][c])
    qr = max(qc + ho - hi, qmin)
    Q[col + "_reb"] = qr
    Q[col + "_cond"] = qr + hi - ho
kW = {k: v / 3600.0 for k, v in Q.items()}

# ---- report ---------------------------------------------------------------------------
kg = lambda n: sum(n[c] * MW[c] for c in COMP)
print("fresh MeOH %.1f kg/h, fresh NH3 %.1f kg/h, products %.1f kg/h, wastewater %.1f kg/h"
      % (kg(S["S1"]), kg(S["S2"]), sum(PRODUCT.values()), kg(S["S23"])))
print("converter feed %.1f kmol/h (%.1f kg/h), N/C %.3f; recycles NH3 %.2f TMA %.2f MMA %.2f MeOH %.3f kmol/h"
      % (sum(feed.values()), kg(feed), N_TO_C, r_nh3, r_tma, r_mma, r_meoh))
print("methanol conversion per pass %.4f; extents" % (1 - out["CH3OH"] / feed["CH3OH"]),
      [round(e, 3) for e in ext])
am = sum(out[c] * MW[c] for c in ["MMA", "DMA", "TMA"])
print("converter outlet amines wt%%: MMA %.1f DMA %.1f TMA %.1f" % tuple(100 * out[c] * MW[c] / am for c in ["MMA", "DMA", "TMA"]))
print("TMA mole fraction in C-101 distillate %.4f" % (r_tma / (r_tma + out["NH3"])))
print("T (K):", {k: round(v, 1) for k, v in sorted(Tc.items(), key=lambda t: int(t[0][1:]))})
print("duties kW:", {k: round(v, 0) for k, v in kW.items()})
print("elements in/out (kmol/h):")
for el, cnt in [("C", CATOM), ("N", NATOM)]:
    fi = sum(cnt[c] * (S["S1"][c] + S["S2"][c]) for c in COMP)
    fo = sum(cnt[c] * (S["S12"][c] + S["S16"][c] + S["S18"][c] + S["S23"][c]) for c in COMP)
    print(" ", el, round(fi, 4), round(fo, 4))
print("mass in %.3f out %.3f kg/h" % (kg(S["S1"]) + kg(S["S2"]),
                                       kg(S["S12"]) + kg(S["S16"]) + kg(S["S18"]) + kg(S["S23"])))

# ---- stream entries for process/flowsheet.yaml (build/streams.yaml) ---------------------
SRC = "scripts/mass_balance.py (D-006)"
TOPO = [  # id, title, from, to, temperature/pressure source
    ("S1", "Fresh methanol", "MEOH.out", "M101.meoh", "design basis (D-003)"),
    ("S2", "Fresh liquid ammonia", "NH3F.out", "M101.nh3", "design basis (D-003)"),
    ("S3", "Combined converter feed", "M101.out", "P101.in", "adiabatic mixing of liquids, " + SRC),
    ("S4", "Pumped converter feed", "P101.out", "E101.in", "D-004"),
    ("S5", "Vaporised feed", "E101.out", "E102.cold_in", "D-004"),
    ("S6", "Converter feed", "E102.cold_out", "R101.in", "adiabatic converter energy balance, " + SRC),
    ("S7", "Converter effluent", "R101.out", "E102.hot_in", "design basis (D-004)"),
    ("S8", "Effluent after feed/effluent exchanger", "E102.hot_out", "E103.in", "E-102 energy balance, " + SRC),
    ("S9", "Condensed effluent to ammonia column", "E103.out", "C101.feed", "D-008"),
    ("S10", "Ammonia / TMA recycle (C-101 distillate)", "C101.top", "M101.rec_nh3", "ideal bubble point at column pressure, " + SRC),
    ("S11", "C-101 bottoms to TMA column", "C101.bot", "C102.feed", "ideal bubble point, " + SRC),
    ("S12", "TMA product", "C102.top", "TMAP.in", "ideal bubble point at column pressure, " + SRC),
    ("S13", "C-102 bottoms to dehydration column", "C102.bot", "C103.feed", "ideal bubble point, " + SRC),
    ("S14", "MMA / DMA (C-103 distillate)", "C103.top", "C104.feed", "ideal bubble point at column pressure, " + SRC),
    ("S15", "MMA (C-104 distillate)", "C104.top", "SPM.in", "ideal bubble point at column pressure, " + SRC),
    ("S16", "MMA product", "SPM.product", "MMAP.in", "as S15"),
    ("S17", "MMA recycle", "SPM.recycle", "M101.rec_mma", "as S15"),
    ("S18", "DMA product (C-104 bottoms)", "C104.bot", "DMAP.in", "ideal bubble point, " + SRC),
    ("S19", "Water and methanol to methanol column (C-103 bottoms)", "C103.bot", "C105.feed", "ideal bubble point, " + SRC),
    ("S20", "Methanol recycle (C-105 distillate)", "C105.top", "M101.rec_meoh", "ideal bubble point at column pressure, " + SRC),
    ("S21", "C-105 bottoms water", "C105.bot", "SPW.in", "ideal bubble point, " + SRC),
    ("S22", "Extraction water to C-102", "SPW.solvent", "C102.solvent", "as S21"),
    ("S23", "Wastewater to treatment", "SPW.waste", "WW.in", "as S21"),
]
CALC = {"S3", "S4", "S7", "S9", "S16", "S17", "S22", "S23"}
ENERGY = [  # id, title, from, to, duty key, source
    ("Q1", "P-101 pump power (feed and recycle pumps lumped)", "POWER.p101", "P101.power", "P101", "eta 0.6 (D-010)"),
    ("Q2", "E-101 feed vaporiser duty", "MPS.e101", "E101.steam", "E101", "D-006"),
    ("Q3", "E-103 effluent condenser duty", "E103.cw", "CW.e103", "E103", "D-006"),
    ("Q4", "C-101 reboiler duty", "MPS.c101", "C101.reb", "C101_reb", "reflux ratio 1.0 (D-008)"),
    ("Q5", "C-101 condenser duty", "C101.cond", "CW.c101", "C101_cond", "reflux ratio 1.0 (D-008)"),
    ("Q6", "C-102 reboiler duty", "LPS.c102", "C102.reb", "C102_reb", "minimum boil-up 0.1 kmol/kmol bottoms (D-008)"),
    ("Q7", "C-102 condenser duty", "C102.cond", "CW.c102", "C102_cond", "column energy balance (D-008)"),
    ("Q8", "C-103 reboiler duty", "MPS.c103", "C103.reb", "C103_reb", "reflux ratio 1.0 (D-008)"),
    ("Q9", "C-103 condenser duty", "C103.cond", "CW.c103", "C103_cond", "reflux ratio 1.0 (D-008)"),
    ("Q10", "C-104 reboiler duty", "LPS.c104", "C104.reb", "C104_reb", "reflux ratio 4 (D-008)"),
    ("Q11", "C-104 condenser duty", "C104.cond", "CW.c104", "C104_cond", "reflux ratio 4 (D-008)"),
    ("Q12", "C-105 reboiler duty", "LPS.c105", "C105.reb", "C105_reb", "minimum boil-up 0.1 kmol/kmol bottoms (D-008)"),
    ("Q13", "C-105 condenser duty", "C105.cond", "CW.c105", "C105_cond", "column energy balance (D-008)"),
]
out = []
for sid, title, fr, to, tsrc in TOPO:
    n = S[sid]
    tot = sum(n.values())
    comp = {c: round(v / tot, 8) for c, v in n.items() if v / tot > 1e-9}
    out += [f"  - id: {sid}", f"    title: {title}", f"    from: {fr}", f"    to: {to}",
            "    template: mixture", "    state:", "      design:",
            f"        pressure: {{value: {Pp[sid]:.0f}, provenance: assumed, source: \"D-004, D-008\"}}",
            f"        temperature: {{value: {Tc[sid]:.2f}, provenance: assumed, source: \"{tsrc}\"}}"]
    if sid not in CALC:
        cs = ", ".join(f"{c}: {v}" for c, v in comp.items())
        out += [f"        flow: {{value: {kg(n):.1f}, basis: mass, provenance: assumed, source: \"{SRC}\"}}",
                f"        composition: {{basis: mole_fraction, values: {{{cs}}}, provenance: assumed, source: \"{SRC}\"}}"]
for qid, title, fr, to, key, src in ENERGY:
    out.append(f"  - {{id: {qid}, title: {title}, kind: energy, from: {fr}, to: {to}, state: {{design: "
               f"{{duty: {{value: {kW[key]:.0f}, provenance: assumed, source: \"{SRC}: {src}\"}}}}}}}}")
out_dir = ROOT / "build"
out_dir.mkdir(exist_ok=True)
(out_dir / "streams.yaml").write_text("\n".join(out) + "\n")
print("split SPM product %.9f, SPW solvent %.9f" % (P["MMA"] / out_mma if (out_mma := S["S14"]["MMA"]) else 0, f_solv))
for sid in ["S7"]:
    print(sid, {c: round(v / sum(S[sid].values()), 8) for c, v in S[sid].items()}, round(kg(S[sid]), 1))
