"""Independent heat and material balance of the cumene plant (DESIGN.md D-007).

This is NOT a cheme-as-code calculation. Core has no qualified property package for aromatics
and light hydrocarbons (its packages cover air and syngas, and the ethanol-water regime), so
the plant is balanced here as an independent cross-check of the DWSIM run (D-011). The
flowsheet's feed flows and split fractions come from this script (`assumed`, source this
script); the other stream values are DWSIM's, and DESIGN.md D-011 compares the two.

Model (every choice is a DESIGN.md decision, ASSUMED where marked there):
- alkylator R-101: liquid phase, propylene converted completely (D-005); of the propylene
  converted, fractions F_CUM to cumene, F_DIPB to diisopropylbenzene, F_TIPB to
  triisopropylbenzene (ASSUMED, D-005); outlet temperature fixed, the heat removed raises LP
  steam (D-004, D-009);
- transalkylator R-102: DIPB + benzene -> 2 cumene, DIPB conversion X_TRANS per pass
  (ASSUMED, D-005), adiabatic;
- columns: component splits from the product and impurity specifications (D-008); minimum
  reflux by Underwood at constant relative volatility (Raoult, vapour pressures of thermo) with
  the feed's thermal condition q; R = R_FACTOR * Rmin, at least R_FLOOR; duties from the
  column energy balance with the arriving feed enthalpy and saturated products;
- enthalpies, flashes and pump volumes: thermo Peng-Robinson with the ChemSep kij set and
  thermo's ideal-gas heat capacities; formation enthalpies of process/materials.yaml added for
  the reactors (unqualified for this mixture, see above);
- loop specifications: benzene/propylene 4 mol/mol at the alkylator inlet (D-004), benzene/DIPB
  5 mol/mol at the transalkylator inlet (D-005), 5 mol% propane in the benzene recycle, which
  sets the slipstream to the depropaniser (D-006).

Run: cheme run scripts/cumene_balance.py   (prints the streams, duties and checks; JSON copy in
build/cumene_balance.json). With BALANCE_OUTPUT set it writes the values the flowsheet cites
(balance-output contract, library ADR 0027).
"""

import json
import os
from pathlib import Path

import numpy as np
import yaml
from scipy.optimize import brentq, fsolve
from thermo import CEOSGas, CEOSLiquid, ChemicalConstantsPackage, FlashVL, PRMIX
from thermo.interaction_parameters import IPDB

ROOT = Path(__file__).resolve().parents[1]
C = ["C3H8", "C3H6", "BZ", "CUM", "DIPB", "TIPB"]
CAS = ["74-98-6", "115-07-1", "71-43-2", "98-82-8", "100-18-5", "717-74-8"]
MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
MW = {c: MAT[c]["molar_mass"] for c in C}
HF = {c: MAT[c]["ideal_gas"]["dHf_298"] for c in C}  # kJ/kmol = J/mol

# ---- basis (DESIGN.md D-002 to D-010)
PRODUCT_KG_H = 34000.0               # D-002: cumene product stream, 272 kt/a at 8000 h/a
PROPYLENE_FEED = {"C3H8": 0.05, "C3H6": 0.95}  # D-003: chemical-grade propylene, mole fractions
BP_RATIO = 4.0                       # D-004: benzene / propylene at the alkylator inlet, molar
F_CUM, F_DIPB, F_TIPB = 0.88, 0.115, 0.005  # D-005: propylene converted to each, molar fraction
X_TRANS = 0.40                       # D-005: DIPB conversion per pass in R-102
B_DIPB_RATIO = 5.0                   # D-005: benzene / DIPB at the transalkylator inlet, molar
Y_C3_RECYCLE = 0.05                  # D-006: propane mole fraction in the C-202 distillate
# column specifications (D-008): impurity mole fractions
X_C201_D_BZ, X_C201_B_C3 = 0.02, 0.0005
X_C202_B_BZ, X_C202_D_CUM = 0.0002, 0.0005
X_C203_D_DIPB, X_C203_B_CUM = 0.0001, 0.01
X_C204_D_TIPB, X_C204_B_DIPB = 0.005, 0.05
R_FACTOR, R_FLOOR = 1.3, 0.5         # D-008
# temperatures (K) and pressures (kPa(a)), D-003, D-004, D-008
T_BZF, P_BZF = 303.15, 400.0
T_PRF, P_PRF = 313.15, 2000.0
P_DRUM = 150.0
P_PUMP = 4200.0                      # P-101, P-102, P-103 discharge
P_R101_IN, T_R101_IN = 4100.0, 413.15
P_R101_OUT, T_R101_OUT = 4000.0, 436.15
P_E101_HOT = 3900.0
P_R102_IN, T_R102_IN = 4100.0, 433.15
P_R102_OUT = 4000.0
P_C201 = (1500.0, 1520.0)
P_C202 = (150.0, 180.0)
P_C203 = (120.0, 150.0)
P_C204 = (30.0, 45.0)
T_PRODUCT = 313.15                   # E-103 cumene product cooler outlet
ETA_P = 0.65                         # D-010: pump efficiency

# ---- thermo
consts, props = ChemicalConstantsPackage.from_IDs(CAS)
kijs = IPDB.get_ip_asymmetric_matrix("ChemSep PR", consts.CASs, "kij")
EOS = dict(Tcs=consts.Tcs, Pcs=consts.Pcs, omegas=consts.omegas, kijs=kijs)
GAS = CEOSGas(PRMIX, EOS, HeatCapacityGases=props.HeatCapacityGases)
LIQ = CEOSLiquid(PRMIX, EOS, HeatCapacityGases=props.HeatCapacityGases)
FL = FlashVL(consts, props, liquid=LIQ, gas=GAS)


def zero():
    return {c: 0.0 for c in C}


def tot(n):
    return sum(n.values())


def zs(n):
    t = tot(n)
    return [max(n[c], 0.0) / t for c in C]


def add(*ns):
    return {c: sum(n[c] for n in ns) for c in C}


def scale(n, f):
    return {c: n[c] * f for c in C}


def mass(n):
    return sum(n[c] * MW[c] for c in C)


def flash(n, **spec):  # T in K, P in kPa
    if "P" in spec:
        spec["P"] = spec["P"] * 1e3
    return FL.flash(zs=zs(n), **spec)


def h(n, res):  # kW, formation enthalpies included (reference: ideal gas, 298.15 K)
    if tot(n) == 0:
        return 0.0
    return tot(n) / 3600 * (res.H() + sum(HF[c] * n[c] / tot(n) for c in C))


def h_tp(n, t, p):
    return h(n, flash(n, T=t, P=p))


def t_of_h(n, hk, p, lo=250.0, hi=650.0):
    return brentq(lambda t: h_tp(n, t, p) - hk, lo, hi)


def split(feed, light, heavy, lk, hk, x_b_lk, x_d_hk):
    """Two products of a column: components lighter than lk all to the top, heavier than hk all to
    the bottom; lk in the bottoms and hk in the distillate at the given mole fractions."""
    others_d = sum(feed[c] for c in light)
    others_b = sum(feed[c] for c in heavy)
    # unknowns a = lk in bottoms, b = hk in distillate
    # a = x_b * (a + feed_hk - b + others_b); b = x_d * (feed_lk - a + b + others_d)
    m = np.array([[1 - x_b_lk, x_b_lk], [x_d_hk, 1 - x_d_hk]])
    rhs = np.array([x_b_lk * (feed[hk] + others_b), x_d_hk * (feed[lk] + others_d)])
    a, b = np.linalg.solve(m, rhs)
    dist, bot = zero(), zero()
    for c in light:
        dist[c] = feed[c]
    for c in heavy:
        bot[c] = feed[c]
    dist[lk], bot[lk] = feed[lk] - a, a
    dist[hk], bot[hk] = b, feed[hk] - b
    return dist, bot


def alkylate(n_in):
    c3 = n_in["C3H6"]
    e1, e2, e3 = F_CUM * c3, F_DIPB * c3 / 2, F_TIPB * c3 / 3   # extents (kmol/h)
    out = dict(n_in)
    out["C3H6"] = 0.0
    out["BZ"] -= e1 + e2 + e3
    out["CUM"] += e1
    out["DIPB"] += e2
    out["TIPB"] += e3
    return out, (e1, e2, e3)


def transalkylate(n_in):
    e = X_TRANS * n_in["DIPB"]
    out = dict(n_in)
    out["DIPB"] -= e
    out["BZ"] -= e
    out["CUM"] += 2 * e
    return out, e


def plant(v):
    """The plant for 100 kmol/h of fresh propylene feed; v: benzene recycle (C3H8, BZ, CUM),
    DIPB recycle (CUM, DIPB, TIPB), C-201 bottoms (C3H8, BZ, CUM), fresh benzene, split
    fractions of the pumped benzene to R-102 and to C-201."""
    rbz = {**zero(), "C3H8": v[0], "BZ": v[1], "CUM": v[2]}
    rdp = {**zero(), "CUM": v[3], "DIPB": v[4], "TIPB": v[5]}
    c201b = {**zero(), "C3H8": v[6], "BZ": v[7], "CUM": v[8]}
    fbz, s_tr, s_dep = v[9], v[10], v[11]
    prf = {**zero(), **{c: 100.0 * y for c, y in PROPYLENE_FEED.items()}}
    bzf = {**zero(), "BZ": fbz}
    drum = add(bzf, rbz)
    alk = scale(drum, 1 - s_tr - s_dep)
    tr = scale(drum, s_tr)
    dep = scale(drum, s_dep)
    r101_in = add(alk, prf)
    r101_out, ext_alk = alkylate(r101_in)
    r102_in = add(tr, rdp)
    r102_out, ext_tr = transalkylate(r102_in)
    eff = add(r101_out, r102_out)
    d201, b201 = split(dep, [], ["CUM", "DIPB", "TIPB", "C3H6"], "C3H8", "BZ", X_C201_B_C3, X_C201_D_BZ)
    f202 = add(eff, c201b)
    d202, b202 = split(f202, ["C3H8", "C3H6"], ["DIPB", "TIPB"], "BZ", "CUM", X_C202_B_BZ, X_C202_D_CUM)
    d203, b203 = split(b202, ["C3H8", "C3H6", "BZ"], ["TIPB"], "CUM", "DIPB", X_C203_B_CUM, X_C203_D_DIPB)
    d204, b204 = split(b203, ["C3H8", "C3H6", "BZ", "CUM"], [], "DIPB", "TIPB", X_C204_B_DIPB, X_C204_D_TIPB)
    return dict(prf=prf, bzf=bzf, rbz=rbz, rdp=rdp, c201b=c201b, drum=drum, alk=alk, tr=tr, dep=dep,
                r101_in=r101_in, r101_out=r101_out, r102_in=r102_in, r102_out=r102_out, eff=eff,
                d201=d201, b201=b201, f202=f202, d202=d202, b202=b202, d203=d203, b203=b203,
                d204=d204, b204=b204, ext_alk=ext_alk, ext_tr=ext_tr, s_tr=s_tr, s_dep=s_dep)


def resid(v):
    st = plant(v)
    r = [st["d202"]["C3H8"] - v[0], st["d202"]["BZ"] - v[1], st["d202"]["CUM"] - v[2],
         st["d204"]["CUM"] - v[3], st["d204"]["DIPB"] - v[4], st["d204"]["TIPB"] - v[5],
         st["b201"]["C3H8"] - v[6], st["b201"]["BZ"] - v[7], st["b201"]["CUM"] - v[8],
         st["r101_in"]["BZ"] / st["r101_in"]["C3H6"] - BP_RATIO,
         st["r102_in"]["BZ"] / st["r102_in"]["DIPB"] - B_DIPB_RATIO,
         st["d202"]["C3H8"] / tot(st["d202"]) - Y_C3_RECYCLE]
    return r


def underwood(feed, dist, hk, t_mean, q):
    """Rmin at constant relative volatility (Raoult, to the heavy key) for a feed of thermal
    condition q."""
    ps = {c: props.VaporPressures[C.index(c)](t_mean) for c in C}
    comps = [c for c in C if feed[c] > 1e-9]
    alpha = {c: ps[c] / ps[hk] for c in comps}
    z = {c: feed[c] / tot(feed) for c in comps}
    xd = {c: dist[c] / tot(dist) for c in comps}
    lk_alpha = min(a for c, a in alpha.items() if a > 1.0 and dist[c] > 1e-12 and feed[c] > 0)
    # roots between hk (alpha 1) and the lightest key that is distributed
    fun = lambda th: sum(alpha[c] * z[c] / (alpha[c] - th) for c in comps) - (1 - q)
    theta = brentq(fun, 1.0 + 1e-7, lk_alpha - 1e-7)
    return sum(alpha[c] * xd[c] / (alpha[c] - theta) for c in comps) - 1


def column(feed, h_feed, dist, bot, p_top, p_bot, hk, t_dist_out=None):
    """Duties (kW) of a column with a total condenser; the reboiler from the energy balance."""
    resd_l = flash(dist, VF=0.0, P=p_top)
    resd_v = flash(dist, VF=1.0, P=p_top)
    resb = flash(bot, VF=0.0, P=p_bot)
    h_sv = h(feed, flash(feed, VF=1.0, P=p_bot))
    h_sl = h(feed, flash(feed, VF=0.0, P=p_bot))
    q = (h_sv - h_feed) / (h_sv - h_sl)
    t_mean = 0.5 * (resd_l.T + resb.T)
    rmin = underwood(feed, dist, hk, t_mean, q)
    r = max(R_FACTOR * rmin, R_FLOOR)
    v_top = scale(dist, r + 1)
    q_cond = h(v_top, resd_v) - h(v_top, resd_l)
    h_d = h(dist, resd_l)
    q_reb = q_cond + h_d + h(bot, resb) - h_feed
    out = dict(q=q, rmin=rmin, r=r, q_cond=q_cond, q_reb=q_reb, t_top=resd_l.T, t_bot=resb.T,
               h_d=h_d, h_b=h(bot, resb))
    if t_dist_out is not None:
        out["q_cool"] = h_d - h_tp(dist, t_dist_out, p_top)
    return out


def pump(n, t, p_in, p_out):
    rho = flash(n, T=t, P=p_in).rho_mass()
    return mass(n) / 3600 / rho * (p_out - p_in) / ETA_P  # kW (kPa * m3/s)


def solve():
    v0 = [20.0, 380.0, 0.2, 2.0, 30.0, 0.2, 0.05, 30.0, 0.1, 95.0, 0.2, 0.08]
    sol, info, ier, msg = fsolve(resid, v0, xtol=1e-12, full_output=True)
    if ier != 1:
        raise SystemExit(f"recycles did not converge: {msg}")
    return plant(sol), max(abs(x) for x in resid(sol))


def main():
    st, worst = solve()
    f = PRODUCT_KG_H / mass(st["d203"])
    S = {k: scale(v, f) for k, v in st.items() if isinstance(v, dict)}
    ext_alk = [e * f for e in st["ext_alk"]]
    ext_tr = st["ext_tr"] * f

    q, temps = {}, {}
    # ---- feed section
    h_bzf = h_tp(S["bzf"], T_BZF, P_BZF)
    c202 = None  # computed below; the drum needs the C-202 distillate enthalpy (saturated)
    res_d202 = flash(S["d202"], VF=0.0, P=P_C202[0])
    h_rbz = h(S["d202"], res_d202)
    h_drum = h_bzf + h_rbz
    temps["drum"] = t_of_h(S["drum"], h_drum, P_DRUM)
    q["P101"] = pump(S["drum"], temps["drum"], P_DRUM, P_PUMP)
    h_drum_p = h_tp(S["drum"], temps["drum"], P_PUMP)  # pump temperature rise neglected (D-010)
    q["P102"] = pump(S["prf"], T_PRF, P_PRF, P_PUMP)
    h_prf_p = h_tp(S["prf"], T_PRF, P_PUMP)
    h_alk_mix = h_drum_p * (tot(S["alk"]) / tot(S["drum"])) + h_prf_p
    temps["M102"] = t_of_h(S["r101_in"], h_alk_mix, P_PUMP)
    # E-101 cold side to the alkylator inlet temperature
    h_r101_in = h_tp(S["r101_in"], T_R101_IN, P_R101_IN)
    q["E101"] = h_r101_in - h_alk_mix
    # R-101: outlet temperature fixed, heat removed to LP steam
    h_r101_out = h_tp(S["r101_out"], T_R101_OUT, P_R101_OUT)
    q["R101"] = h_r101_in - h_r101_out          # heat removed (kW), to LP steam (D-009)
    h_e101_hot_out = h_r101_out - q["E101"]
    temps["E101_hot_out"] = t_of_h(S["r101_out"], h_e101_hot_out, P_E101_HOT)
    # transalkylation: DIPB recycle pumped, mixed with benzene, heated, adiabatic reactor
    res_d204 = flash(S["d204"], VF=0.0, P=P_C204[0])
    q["P103"] = pump(S["d204"], res_d204.T, P_C204[0], P_PUMP)
    h_rdp_p = h_tp(S["d204"], res_d204.T, P_PUMP)
    h_tr_mix = h_drum_p * (tot(S["tr"]) / tot(S["drum"])) + h_rdp_p
    temps["M103"] = t_of_h(S["r102_in"], h_tr_mix, P_PUMP)
    h_r102_in = h_tp(S["r102_in"], T_R102_IN, P_R102_IN)
    q["E102"] = h_r102_in - h_tr_mix
    temps["R102_out"] = t_of_h(S["r102_out"], h_r102_in, P_R102_OUT)
    h_r102_out = h_r102_in
    h_eff = h_e101_hot_out + h_r102_out
    # ---- columns
    h_dep = h_drum_p * (tot(S["dep"]) / tot(S["drum"]))
    c201 = column(S["dep"], h_dep, S["d201"], S["b201"], *P_C201, "BZ")
    h_f202 = h_eff + c201["h_b"]
    c202 = column(S["f202"], h_f202, S["d202"], S["b202"], *P_C202, "CUM")
    c203 = column(S["b202"], c202["h_b"], S["d203"], S["b203"], *P_C203, "DIPB", T_PRODUCT)
    c204 = column(S["b203"], c203["h_b"], S["d204"], S["b204"], *P_C204, "TIPB")
    for name, col in (("C201", c201), ("C202", c202), ("C203", c203), ("C204", c204)):
        q[name + "_cond"], q[name + "_reb"] = col["q_cond"], col["q_reb"]
    q["E103"] = c203["q_cool"]

    # ---- overall energy closure (kW, formation enthalpies included): feeds + work and heat in
    # = products + heat out (LP steam, cooling water). Pump temperature rises are neglected.
    h_in = (h_bzf + h_tp(S["prf"], T_PRF, P_PRF) + q["P101"] + q["P102"] + q["P103"] + q["E102"]
            + q["C201_reb"] + q["C202_reb"] + q["C203_reb"] + q["C204_reb"])
    h_out = (c201["h_d"] + h_tp(S["d203"], T_PRODUCT, P_C203[0]) + c204["h_b"] + q["R101"]
             + q["C201_cond"] + q["C202_cond"] + q["C203_cond"] + q["C204_cond"] + q["E103"])
    pump_rise = q["P101"] + q["P102"] + q["P103"]
    mass_in = mass(S["bzf"]) + mass(S["prf"])
    mass_out = mass(S["d201"]) + mass(S["d203"]) + mass(S["b204"])
    cum = S["d203"]
    out = {
        "streams_kmol_h": {k: {c: round(n[c], 6) for c in C if n[c] > 1e-12} for k, n in S.items()},
        "duties_kW": q,
        "temperatures_K": {**temps, "C201_top": c201["t_top"], "C201_bot": c201["t_bot"],
                           "C202_top": c202["t_top"], "C202_bot": c202["t_bot"],
                           "C203_top": c203["t_top"], "C203_bot": c203["t_bot"],
                           "C204_top": c204["t_top"], "C204_bot": c204["t_bot"]},
        "columns": {k: {kk: vv for kk, vv in col.items() if kk in ("q", "rmin", "r")}
                    for k, col in (("C201", c201), ("C202", c202), ("C203", c203), ("C204", c204))},
        "checks": {
            "recycle_residual_max": worst,
            "split_to_R102": st["s_tr"], "split_to_C201": st["s_dep"],
            "extents_kmol_h": {"ALK": ext_alk[0], "ALK2": ext_alk[1], "ALK3": ext_alk[2], "TRANS": ext_tr},
            "fresh_benzene_kg_h": mass(S["bzf"]), "propylene_feed_kg_h": mass(S["prf"]),
            "benzene_t_per_t_cumene": mass(S["bzf"]) / PRODUCT_KG_H,
            "propylene_feed_t_per_t_cumene": mass(S["prf"]) / PRODUCT_KG_H,
            "propylene_t_per_t_cumene": S["prf"]["C3H6"] * MW["C3H6"] / PRODUCT_KG_H,
            "yield_cumene_per_benzene_and_propylene_kg_kg": PRODUCT_KG_H / (mass(S["bzf"]) + S["prf"]["C3H6"] * MW["C3H6"]),
            "cumene_product_wt_purity": cum["CUM"] * MW["CUM"] / mass(cum),
            "lp_steam_export_kW": q["R101"],
            "mass_in_kg_h": mass_in, "mass_out_kg_h": mass_out,
            "energy_in_kW": h_in, "energy_out_kW": h_out, "pump_temperature_rise_neglected_kW": pump_rise,
        },
    }
    print(json.dumps(out, indent=1, default=float))
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/cumene_balance.json").write_text(json.dumps(out, indent=1, default=float))

    # the values process/flowsheet.yaml cites from this script (balance-output contract)
    drum = S["drum"]
    fs = {"S1": {"flow": mass(S["bzf"])}, "S4": {"flow": mass(S["prf"])},
          "S3": {"flow": mass(drum), "temperature": temps["drum"],
                 "composition": {c: drum[c] / tot(drum) for c in C if drum[c] > 1e-12}}}
    print("flowsheet values:", json.dumps(fs, default=float))
    write_balance_output({"design": fs})


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON
    (the process library's balance-output contract, ADR 0027; scripts/check_balance_scripts.py
    re-runs this script and compares them with process/flowsheet.yaml)."""
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}", "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
