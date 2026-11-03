"""Independent heat and material balance of the ethylbenzene plant (DESIGN.md D-006).

This is NOT a cheme-as-code calculation, and not the DWSIM model. Core has no qualified property
package for aromatics (the packaged ones cover air and syngas), so this script is the reference
the DWSIM run of process/simulation.yaml is compared with (D-014). The flowsheet cites from it
only the two feed flows (S1 fresh benzene, S6 fresh ethylene) and the recycle split fraction;
everything downstream is calculated by cheme (propagate, simulate).

Model (every choice is a DESIGN.md decision, ASSUMED where marked there):
- alkylator R-101: ethylene converted completely (D-005, ASSUMED); its split between the lumped
  reactions ALK (-> EB), DIALK (-> DEB, the polyethylbenzenes) and PENTA (-> pentaethylbenzene,
  the flux-oil model compound) from US5493065A Example 7 (EB 94.0, DEB 5.7, TEB 0.2 mol% of the
  products, TEB lumped with DEB), the PENTA share set so that the flux oil is 4.3 kg per t of EB
  product (EU LVOC BREF 2017, 5.3.6.1.2: 3 to 5.6 kg/t, midpoint) (D-005);
  benzene/ethylene 4.0 mol/mol at the alkylator (D-004); outlet held at T_R101 by the interbed
  steam generators (D-004, D-009);
- transalkylator R-102: DEB + BZ -> 2 EB, DEB conversion per pass X_TRANS at benzene/DEB
  B_DEB (D-005, both ASSUMED), adiabatic;
- columns: component splits from the key specifications (D-008); Underwood minimum reflux at
  constant relative volatility (vapour pressure ratio at the mean column temperature),
  R = R_FACTOR * Rmin; total condensers, saturated products; reboiler duty from the column energy
  balance with the arriving feed enthalpy;
- flashes and enthalpies: thermo Peng-Robinson with the ChemSep kij set (only ethylene-benzene
  has one), ideal-gas heat capacities of thermo; formation enthalpies of process/materials.yaml
  added for the reactors (unqualified for this mixture, D-006);
- pumps: PR liquid density, efficiency ETA_P, temperature rise neglected (D-010).

Run: cheme run scripts/eb_balance.py  (prints the streams, duties, per-t figures and checks; JSON
copy in build/eb_balance.json). With BALANCE_OUTPUT set it writes the values the flowsheet
cites (balance-output/1, library ADR 0027).
"""

import json
import math
import os
from pathlib import Path

import yaml
from scipy.optimize import brentq
from thermo import CEOSGas, CEOSLiquid, ChemicalConstantsPackage, FlashVL, PRMIX
from thermo.interaction_parameters import IPDB

ROOT = Path(__file__).resolve().parents[1]
C = ["ETY", "BZ", "EB", "DEB", "PETB"]
NAMES = ["ethylene", "benzene", "ethylbenzene", "1,4-diethylbenzene", "605-01-6"]
MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
MW = {c: MAT[c]["molar_mass"] for c in C}
HF = {c: MAT[c]["ideal_gas"]["dHf_298"] for c in C}  # kJ/kmol

# ---- basis (DESIGN.md D-002 to D-010)
PRODUCT_KG_H = 400e6 / 8000          # D-002: 400 kt/a EB product stream, 8000 h/a
B_E = 4.0                            # D-004: benzene/ethylene at the alkylator inlet, molar
# D-005: ethylene shares from US5493065A Example 7 (MCM-22, 220 C, B/E 5.5): products 94.0 EB,
# 5.7 DEB, 0.2 TEB mol%; ethylene in polyethylbenzenes (2 x 5.7 + 3 x 0.2) / (94.0 + 11.4 + 0.6)
F_POLY = (2 * 5.7 + 3 * 0.2) / (94.0 + 2 * 5.7 + 3 * 0.2)
TAR_KG_PER_T = 4.3                   # D-005: flux oil per t EB product (BREF 3 to 5.6, midpoint)
X_TRANS = 0.65                       # D-005: DEB conversion per pass in R-102, ASSUMED
B_DEB = 3.0                          # D-004: benzene/DEB at the transalkylator inlet, ASSUMED
# D-008 column specs (mole fractions)
X_EB_D201, X_BZ_B201 = 0.001, 0.0005     # C-201: EB in recycle benzene, benzene in bottoms
X_DEB_D202, X_EB_B202 = 0.00002, 0.005   # C-202: DEB in EB product, EB in bottoms
X_PETB_D203, X_DEB_B203 = 0.0001, 0.02   # C-203: heavies in PEB recycle, DEB in flux oil
R_FACTOR, R_FLOOR = 1.3, 0.3         # D-008
R_C202_SIM = 0.97                    # D-014: the C-202 reflux of process/simulation.yaml (comparison only)
# pressures kPa(a) and temperatures K (D-003, D-004, D-008)
T_BZF, P_BZF = 303.15, 500.0         # fresh benzene at the battery limit
T_ETYF, P_ETYF = 298.15, 4000.0      # fresh ethylene at the battery limit (no compressor)
P_DRUM = 450.0                       # V-101 benzene drum, P-101/P-102 suction, P-103 discharge
P_PUMP = 3900.0                      # P-101, P-102 discharge
P_E101C = 3850.0                     # E-101 cold outlet
T_E101C = 473.15                     # E-101 cold outlet temperature
P_R101_IN, P_R101_OUT, T_R101 = 3850.0, 3750.0, 513.15
P_E101H = 3700.0                     # E-101 hot outlet
P_E102, T_R102_IN, P_R102_OUT = 3850.0, 503.15, 3750.0
P_C201_TOP, P_C201_BOT = 450.0, 480.0
P_C202_TOP, P_C202_BOT = 150.0, 170.0
P_C203_TOP, P_C203_BOT = 20.0, 30.0
T_PRODUCT = 313.15                   # E-207 EB product cooler outlet
ETA_P = 0.65                         # D-010

# ---- thermo
consts, props = ChemicalConstantsPackage.from_IDs(NAMES)
kijs = IPDB.get_ip_asymmetric_matrix("ChemSep PR", consts.CASs, "kij")
EOS = dict(Tcs=consts.Tcs, Pcs=consts.Pcs, omegas=consts.omegas, kijs=kijs)
GAS = CEOSGas(PRMIX, EOS, HeatCapacityGases=props.HeatCapacityGases)
LIQ = CEOSLiquid(PRMIX, EOS, HeatCapacityGases=props.HeatCapacityGases)
FL = FlashVL(consts, props, liquid=LIQ, gas=GAS)


def tot(n):
    return sum(n[c] for c in C)


def zs(n):
    t = tot(n)
    return [max(n[c], 0.0) / t for c in C]


def add(*ns):
    return {c: sum(n[c] for n in ns) for c in C}


def scale(n, f):
    return {c: n[c] * f for c in C}


def zero():
    return {c: 0.0 for c in C}


def mass(n):
    return sum(n[c] * MW[c] for c in C)


def flash(n, **spec):  # spec in K and kPa
    s = {k: (v * 1e3 if k == "P" else v) for k, v in spec.items()}
    return FL.flash(zs=zs(n), **s)


def h(n, res):
    """kW: sensible (thermo reference: ideal gas 298.15 K) plus formation (materials.yaml)."""
    return tot(n) / 3600 * (res.H() + sum(HF[c] * n[c] / tot(n) for c in C))


def h_tp(n, t, p):
    return h(n, flash(n, T=t, P=p))


def bubble(n, p):
    return flash(n, P=p, VF=0)


def dew(n, p):
    return flash(n, P=p, VF=1)


def t_at(n, hh, p, lo=250.0, hi=700.0):
    return brentq(lambda t: h_tp(n, t, p) - hh, lo, hi)


def psat(c, t):
    return props.VaporPressures[C.index(c)](t)


# ---- reactors
def r101(feed, f_penta):
    """Alkylator: all ethylene converted; shares ALK, DIALK, PENTA of the ethylene."""
    e = feed["ETY"]
    x_dialk = F_POLY - 5 * f_penta  # PENTA ethylene taken from the polyethylbenzene share
    alk, dialk, penta = e * (1 - F_POLY), e * x_dialk / 2, e * f_penta
    out = dict(feed)
    out["ETY"] = 0.0
    out["BZ"] -= alk + dialk + penta
    out["EB"] += alk
    out["DEB"] += dialk
    out["PETB"] += penta
    return out, {"ALK": alk, "DIALK": dialk, "PENTA": penta}


def r102(feed):
    xi = X_TRANS * feed["DEB"]
    out = dict(feed)
    out["DEB"] -= xi
    out["BZ"] -= xi
    out["EB"] += 2 * xi
    return out, xi


# ---- columns: component splits from the key specs
def split_two(feed, lk, hk, x_hk_d, x_lk_b, lights, heavies):
    """Distillate: all `lights`, LK less x_lk_b in the bottoms, HK at x_hk_d; bottoms the rest."""
    fl = sum(feed[c] for c in lights)
    fh = sum(feed[c] for c in heavies)
    # unknowns d_lk, d_hk, linear:
    #   d_hk = x_hk_d (fl + d_lk + d_hk)
    #   f_lk - d_lk = x_lk_b (f_lk + f_hk + fh - d_lk - d_hk)
    a1, b1, c1 = -x_hk_d, 1 - x_hk_d, x_hk_d * fl
    a2, b2, c2 = -(1 - x_lk_b), x_lk_b, x_lk_b * (fh + feed[lk] + feed[hk]) - feed[lk]
    det = a1 * b2 - b1 * a2
    d_lk = (c1 * b2 - b1 * c2) / det
    d_hk = (a1 * c2 - c1 * a2) / det
    d = zero()
    for c in lights:
        d[c] = feed[c]
    d[lk], d[hk] = d_lk, d_hk
    b = {c: feed[c] - d[c] for c in C}
    return d, b


def underwood(feed_n, q, dist, alpha):
    """Rmin of a feed of thermal condition q (constant alpha, relative to the heaviest)."""
    z = {c: feed_n[c] / tot(feed_n) for c in C}
    act = [c for c in C if z[c] > 1e-12]
    ak = sorted(alpha[c] for c in act)

    def f(th):
        return sum(alpha[c] * z[c] / (alpha[c] - th) for c in act) - (1 - q)

    # theta between the keys' alphas: take every root between adjacent alphas, use the max Rmin
    best = 0.0
    xd = {c: dist[c] / tot(dist) for c in C}
    for lo, hi in zip(ak, ak[1:]):
        try:
            th = brentq(f, lo + 1e-9, hi - 1e-9)
        except ValueError:
            continue
        rmin = sum(alpha[c] * xd[c] / (alpha[c] - th) for c in act if xd[c] > 0) - 1
        best = max(best, rmin)
    return best


def column(name, feed, h_feed, dist, bot, p_top, p_bot, ref, r_fixed=None):
    rd = bubble(dist, p_top)
    rb = bubble(bot, p_bot)
    t_mean = 0.5 * (rd.T + rb.T)
    alpha = {c: psat(c, t_mean) / psat(ref, t_mean) for c in C}
    # feed condition q at the column pressure (enthalpy of the arriving feed)
    pf = 0.5 * (p_top + p_bot)
    h_bub = h(feed, bubble(feed, pf))
    h_dew = h(feed, dew(feed, pf))
    q = (h_dew - h_feed) / (h_dew - h_bub)
    rmin = underwood(feed, q, dist, alpha)
    r = r_fixed if r_fixed is not None else max(R_FACTOR * rmin, R_FLOOR)
    v = (r + 1) * tot(dist)
    xd = {c: dist[c] / tot(dist) for c in C}
    top = {c: xd[c] * v for c in C}
    q_cond = h(top, dew(top, p_top)) - h(top, bubble(top, p_top))
    q_reb = q_cond + h(dist, rd) + h(bot, rb) - h_feed
    return {"name": name, "R": r, "Rmin": rmin, "q_feed": q, "q_cond": q_cond, "q_reb": q_reb,
            "t_top": rd.T, "t_bot": rb.T, "V_top_kmol_h": v}


# ---- the loops at a basis of 1 kmol/h ethylene
def solve(f_penta):
    e = 1.0
    bz_rec = {**zero(), "BZ": 3.0 * e}          # guess: recycle benzene (C-201 top)
    peb_rec = {**zero(), "DEB": 0.1 * e}        # guess: PEB recycle (C-203 top)
    for it in range(500):
        xbz = {c: bz_rec[c] / tot(bz_rec) for c in C}
        # transalkylator benzene: B_DEB x DEB at its inlet, from the recycle benzene
        to_trans_tot = max(B_DEB * peb_rec["DEB"] - peb_rec["BZ"], 0.0) / xbz["BZ"]
        to_trans = {c: xbz[c] * to_trans_tot for c in C}
        to_alk = {c: bz_rec[c] - to_trans[c] for c in C}
        fresh_bz = B_E * e - to_alk["BZ"]
        fresh = {**zero(), "BZ": fresh_bz}
        alk_in = add(fresh, to_alk, {**zero(), "ETY": e})
        alk_out, ext = r101(alk_in, f_penta)
        tr_in = add(to_trans, peb_rec)
        tr_out, xi_tr = r102(tr_in)
        c201_feed = add(alk_out, tr_out)
        d201, b201 = split_two(c201_feed, "BZ", "EB", X_EB_D201, X_BZ_B201, ["ETY"], ["DEB", "PETB"])
        d202, b202 = split_two(b201, "EB", "DEB", X_DEB_D202, X_EB_B202, ["ETY", "BZ"], ["PETB"])
        d203, b203 = split_two(b202, "DEB", "PETB", X_PETB_D203, X_DEB_B203, ["ETY", "BZ", "EB"], [])
        res = max(abs(d201[c] - bz_rec[c]) for c in C) + max(abs(d203[c] - peb_rec[c]) for c in C)
        bz_rec, peb_rec = d201, d203
        if res < 1e-13:
            break
    if fresh_bz <= 0:
        raise SystemExit("fresh benzene came out negative: check B_E and the recycle specs")
    return {"fresh_bz": fresh, "ety": {**zero(), "ETY": e}, "to_alk": to_alk, "to_trans": to_trans,
            "alk_in": alk_in, "alk_out": alk_out, "ext": ext, "tr_in": tr_in, "tr_out": tr_out,
            "xi_tr": xi_tr, "c201_feed": c201_feed, "d201": d201, "b201": b201, "d202": d202,
            "b202": b202, "d203": d203, "b203": b203, "residual": res, "iterations": it}


def tar_gap(f_penta):
    st = solve(f_penta)
    return mass(st["b203"]) / mass(st["d202"]) * 1000 - TAR_KG_PER_T


def main():
    f_penta = brentq(tar_gap, 0.0, 0.02, xtol=1e-14)
    st = solve(f_penta)
    f = PRODUCT_KG_H / mass(st["d202"])
    S = {k: scale(v, f) for k, v in st.items() if isinstance(v, dict) and set(v) == set(C)}
    ext = {k: v * f for k, v in st["ext"].items()}
    xi_tr = st["xi_tr"] * f

    # ---- energy
    q = {}
    # V-101 / M101: fresh benzene + recycle benzene (bubble liquid from C-201) mixed at P_DRUM
    rd201 = bubble(S["d201"], P_C201_TOP)
    h_rec_alk = tot(S["to_alk"]) / tot(S["d201"]) * h(S["d201"], rd201)
    h_m101 = h_tp(S["fresh_bz"], T_BZF, P_BZF) + h_rec_alk
    m101 = add(S["fresh_bz"], S["to_alk"])
    t_m101 = t_at(m101, h_m101, P_DRUM)
    rho = flash(m101, T=t_m101, P=P_PUMP).rho_mass()
    q["P101"] = mass(m101) / 3600 / rho * (P_PUMP - P_DRUM) / ETA_P
    h_p101 = h_m101 + q["P101"]
    t_p101 = t_at(m101, h_p101, P_PUMP)
    # E-101 cold side to T_E101C
    h_e101c = h_tp(m101, T_E101C, P_E101C)
    q["E101"] = h_e101c - h_p101
    # M-102: ethylene injection
    h_r101_in = h_e101c + h_tp(S["ety"], T_ETYF, P_ETYF)
    r_in = S["alk_in"]
    t_r101_in = t_at(r_in, h_r101_in, P_R101_IN)
    vf_r101_in = flash(r_in, T=t_r101_in, P=P_R101_IN).VF
    # R-101 at T_R101: heat to the interbed steam generators
    r_out = S["alk_out"]
    res_r101 = flash(r_out, T=T_R101, P=P_R101_OUT)
    q["R101"] = h_r101_in - h(r_out, res_r101)
    # E-101 hot side
    h_e101h = h(r_out, res_r101) - q["E101"]
    t_e101h = t_at(r_out, h_e101h, P_E101H)
    approach = (T_R101 - T_E101C, t_e101h - t_p101)
    # transalkylator: recycle benzene + PEB recycle (bubble liquid from C-203), P-102, E-102
    rd203 = bubble(S["d203"], P_C203_TOP)
    rho3 = flash(S["d203"], T=rd203.T, P=P_DRUM).rho_mass()
    q["P103"] = mass(S["d203"]) / 3600 / rho3 * (P_DRUM - P_C203_TOP) / ETA_P
    h_m103 = tot(S["to_trans"]) / tot(S["d201"]) * h(S["d201"], rd201) + h(S["d203"], rd203) + q["P103"]
    m103 = S["tr_in"]
    t_m103 = t_at(m103, h_m103, P_DRUM)
    rho2 = flash(m103, T=t_m103, P=P_PUMP).rho_mass()
    q["P102"] = mass(m103) / 3600 / rho2 * (P_PUMP - P_DRUM) / ETA_P
    h_p102 = h_m103 + q["P102"]
    t_p102 = t_at(m103, h_p102, P_PUMP)
    h_e102 = h_tp(m103, T_R102_IN, P_E102)
    q["E102"] = h_e102 - h_p102
    t_r102 = t_at(S["tr_out"], h_e102, P_R102_OUT)
    # C-201 feed: both effluents mixed (enthalpy conserved through the letdown)
    h_c201f = h_e101h + h_e102
    c201 = column("C201", S["c201_feed"], h_c201f, S["d201"], S["b201"], P_C201_TOP, P_C201_BOT, "EB")
    h_b201 = h(S["b201"], bubble(S["b201"], P_C201_BOT))
    c202 = column("C202", S["b201"], h_b201, S["d202"], S["b202"], P_C202_TOP, P_C202_BOT, "DEB")
    h_b202 = h(S["b202"], bubble(S["b202"], P_C202_BOT))
    c203 = column("C203", S["b202"], h_b202, S["d203"], S["b203"], P_C203_TOP, P_C203_BOT, "PETB")
    for col in (c201, c202, c203):
        q[col["name"] + "_cond"], q[col["name"] + "_reb"] = col["q_cond"], col["q_reb"]
    # comparison only (D-014): C-202 at the reflux the DWSIM model runs, 1.3 x DWSIM's minimum
    c202_sim = column("C202", S["b201"], h_b201, S["d202"], S["b202"], P_C202_TOP, P_C202_BOT, "DEB",
                      r_fixed=R_C202_SIM)
    # E-207 EB product cooler
    rd202 = bubble(S["d202"], P_C202_TOP)
    q["E207"] = h(S["d202"], rd202) - h_tp(S["d202"], T_PRODUCT, P_C202_TOP)
    rb203 = bubble(S["b203"], P_C203_BOT)

    eb_t = PRODUCT_KG_H / 1000  # t/h
    steam_in = q["E102"] + q["C201_reb"] + q["C202_reb"] + q["C203_reb"]
    steam_out = q["R101"] + q["C201_cond"] + q["C202_cond"]
    per_t = {
        "benzene_t_per_t": mass(S["fresh_bz"]) / PRODUCT_KG_H,
        "ethylene_t_per_t": mass(S["ety"]) / PRODUCT_KG_H,
        "flux_oil_kg_per_t": mass(S["b203"]) / eb_t,
        "electricity_pumps_kWh_per_t": (q["P101"] + q["P102"] + q["P103"]) / eb_t,
        "hp_steam_kWh_per_t": steam_in / eb_t,
        "steam_raised_kWh_per_t": steam_out / eb_t,
        "cooling_water_kWh_per_t": (q["C203_cond"] + q["E207"]) / eb_t,
    }
    # overall energy closure: feeds + work + steam in = products + heat out
    h_in = (h_tp(S["fresh_bz"], T_BZF, P_BZF) + h_tp(S["ety"], T_ETYF, P_ETYF) + q["P101"] + q["P102"]
            + q["P103"] + steam_in)
    h_out = (h_tp(S["d202"], T_PRODUCT, P_C202_TOP) + h(S["b203"], rb203) + steam_out
             + q["C203_cond"] + q["E207"])
    out = {
        "f_penta": f_penta,
        "reaction_conversions": {"ALK": 1 - F_POLY, "DIALK": F_POLY - 5 * f_penta,
                                 "PENTA": 5 * f_penta, "TRANS": X_TRANS},
        "extents_kmol_h": {**ext, "TRANS": xi_tr},
        "streams_kg_h": {k: round(mass(v), 3) for k, v in S.items()},
        "streams_kmol_h": {k: {c: round(v[c], 6) for c in C if abs(v[c]) > 1e-12} for k, v in S.items()},
        "temperatures_K": {"M101": t_m101, "P101_out": t_p101, "R101_in": t_r101_in,
                           "R101_in_VF": vf_r101_in, "E101_hot_out": t_e101h, "M103": t_m103,
                           "P102_out": t_p102, "R102_out": t_r102, "C201_top": c201["t_top"],
                           "C201_bot": c201["t_bot"], "C202_top": c202["t_top"],
                           "C202_bot": c202["t_bot"], "C203_top": c203["t_top"],
                           "C203_bot": c203["t_bot"]},
        "E101_terminal_approach_K": approach,
        "duties_kW": q,
        "columns": {c["name"]: {k: v for k, v in c.items() if k != "name"} for c in (c201, c202, c203)},
        "C202_at_simulated_reflux": {k: v for k, v in c202_sim.items() if k != "name"},
        "per_t_EB": per_t,
        "split_to_alkylator": tot(S["to_alk"]) / tot(S["d201"]),
        "checks": {"loop_residual": st["residual"], "loop_iterations": st["iterations"],
                   "mass_in_kg_h": mass(S["fresh_bz"]) + mass(S["ety"]),
                   "mass_out_kg_h": mass(S["d202"]) + mass(S["b203"]),
                   "energy_in_kW": h_in, "energy_out_kW": h_out,
                   "eb_product_mol_purity": S["d202"]["EB"] / tot(S["d202"])},
    }
    print(json.dumps(out, indent=1, default=float))
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/eb_balance.json").write_text(json.dumps(out, indent=1, default=float))

    # the values process/flowsheet.yaml cites from this script (balance-output contract)
    write_balance_output({"design": {
        "S1": {"flow": mass(S["fresh_bz"])},
        "S6": {"flow": mass(S["ety"])},
    }})


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
