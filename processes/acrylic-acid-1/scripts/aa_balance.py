"""Independent balance of acrylic-acid-1 (DESIGN.md D-004 to D-010).

Run with `cheme run scripts/aa_balance.py`; it prints the balance and, when the environment
variable BALANCE_OUTPUT names a file, writes the values process/flowsheet.yaml cites from it
(the library's balance-output contract, ADR 0027). It writes nothing else.

What it does, on the ratios and splits of DESIGN.md (sources there):
- sizes the propylene feed for 12 500 kg/h of glacial acrylic acid with 200 ppm MEHQ (D-002);
  the plant is linear in its feeds at fixed ratios, so it runs for 1 kmol/h of propylene and
  scales;
- the feeds of air and steam from the ratios of US 4 873 368 A (Example 2 for the first stage,
  Example 5 for the totals of both stages, D-004), the process water of the quench absorber for
  a 55 wt% acrylic acid bottoms (US 5 910 607 A, Example 1, D-007), the hydroquinone for 800 ppm
  in the dehydration column's bottoms (US 5 910 607 A, D-008), the toluene make-up for 7 wt%
  toluene in that bottoms (US 5 910 607 A, Example 1, D-008), the MEHQ for 200 ppm in the
  product (Arkema data sheet, D-009);
- the reactors and separators as core's conversion and recovery models do (the same
  selectivities and fractions as the flowsheet), so that the duties below rest on the same
  flows; core calculates the streams itself (cheme process propagate --fill) and writes the two
  reactors' duties, which this script only prints as a cross-check;
- temperatures of the adiabatic mixers and of the adiabatic catalytic oxidiser, the air
  compressor's power, and the duties of the gas cooler, the quench absorber and the three
  columns (ideal gas from the ideal_gas data of process/materials.yaml; liquids with thermo's
  liquid heat capacities and heats of vaporisation, acrylic acid's latent heat from the Arkema
  data sheet; no heats of mixing, D-010).
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import yaml
from chemicals.iapws import iapws95_Tsat
from thermo import Chemical

ROOT = Path(__file__).resolve().parents[1]
MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
MW = {k: v["molar_mass"] for k, v in MAT.items()}
R = 8.314462618
T0 = 298.15

# ---- design inputs (DESIGN.md) -----------------------------------------------------------------
PRODUCT_KG_H = 12500.0            # D-002, ASSUMED: 100 kt/a in 8000 h
Y_C3_FEED = 0.995                 # D-003, ASSUMED: chemical-grade propylene, 0.5 mol% propane
AIR = {"O2": 0.2095, "N2": 0.7905}  # dry air, argon and CO2 lumped into N2
# US 4 873 368 A: first stage 12 % propylene, 10 % steam, 78 % air (Example 2); both stages
# together 7.5 % propylene, 15 % steam, 77.5 % air (Example 5), per mol of propylene:
AIR1, STM1 = 78.0 / 12.0, 10.0 / 12.0
AIR_TOT, STM_TOT = 77.5 / 7.5, 15.0 / 7.5
AIR2, STM2 = AIR_TOT - AIR1, STM_TOT - STM1
# first stage (US 4 873 368 A, Example 2): conversion 98.5 %, acrolein 80.2 %, acrylic acid 11.7 %
X1, Y_ACR1, Y_AA1 = 0.985, 0.802, 0.117
# both stages (Example 5): acrolein 0.4 %, acrylic acid 87.8 % of the propylene fed
Y_ACR2, Y_AA2 = 0.004, 0.878
# acetic acid: 1.5 wt% beside 55 wt% acrylic acid in the absorber's bottoms (US 5 910 607 A,
# Example 1), taken as the reactor's ratio (D-005)
HAC_PER_AA = (1.5 / MW["HAC"]) / (55.0 / MW["AA"])
W_AA_BOTTOMS = 0.55               # D-007
T_TOP_ABS, P_TOP_ABS = 313.15, 130.0  # D-007, ASSUMED
HQ_PPM_C401 = 800e-6              # D-008 (US 5 910 607 A: hydroquinone 800 ppm in the bottoms)
W_TOL_C401 = 0.07                 # D-008 (Example 1: 7 % toluene in the bottoms)
MEHQ_PPM = 200e-6                 # D-009 (Arkema: 200 ppm MEHQ)

# separator splits: the flowsheet's recovery fractions (DESIGN.md D-007, D-008, D-009)
T301_GAS = {"N2": 1, "O2": 1, "CO2": 1, "C3H6": 1, "C3H8": 1, "ACR": 1.0, "AA": 0.002, "HAC": 0.03}
C401_AQ = {"H2O": 0.997, "HAC": 0.05, "AA": 0.0007, "TOL": 0.005}
C402_TOP = {"TOL": 0.995, "H2O": 1.0, "HAC": 0.10, "AA": 0.002}
C402_SIDE = {"TOL": 0.005, "HAC": 0.88, "AA": 0.008}
C404_TOP = {"AA": 0.985, "HAC": 1.0, "H2O": 1.0, "TOL": 1.0}
X401_CONV = 0.99                  # D-011, ASSUMED

COMPS = ["C3H6", "C3H8", "O2", "N2", "H2O", "CO2", "ACR", "AA", "HAC", "TOL", "HQ", "MEHQ"]
CAS = {"H2O": "7732-18-5", "AA": "79-10-7", "HAC": "64-19-7", "TOL": "108-88-3", "HQ": "123-31-9",
       "ACR": "107-02-8"}
H_VAP_AA = 634.0 * MW["AA"]       # kJ/kmol (Arkema data sheet: 634 kJ/kg)


def z():
    return {c: 0.0 for c in COMPS}


def add(*ss):
    out = z()
    for s in ss:
        for c, v in s.items():
            out[c] += v
    return out


def split(s, frac):
    a = {c: s[c] * frac.get(c, 0.0) for c in COMPS}
    b = {c: s[c] - a[c] for c in COMPS}
    return a, b


def mass(s):
    return sum(s[c] * MW[c] for c in COMPS)


# ---- ideal-gas enthalpy (kJ/kmol, reference ideal gas 298.15 K, formation included) ----------
def h_ig(c, t):
    ig = MAT[c].get("ideal_gas")
    if ig is None:
        raise KeyError(c)
    a = ig["cp_R"]
    def integ(tt):
        return sum(a[i] * tt ** (i + 1) / (i + 1) for i in range(len(a)))
    return ig["dHf_298"] / 1000.0 * 1000.0 + R * (integ(t) - integ(T0))


def h_gas(s, t):
    return sum(v * h_ig(c, t) for c, v in s.items() if v)


def cpl(c, t):
    return Chemical(CAS[c], T=t).Cplm / 1000.0  # kJ/(kmol K)


def hvap(c, t):
    if c == "AA":
        return H_VAP_AA
    return Chemical(CAS[c], T=t).Hvapm  # J/mol = kJ/kmol


def h_liq(s, t):
    """Liquid enthalpy on the ideal-gas reference: gas at 298.15 K less the heat of vaporisation
    at 298.15 K plus the liquid's sensible heat (no heat of mixing); HQ and MEHQ by liquid Cp."""
    h = 0.0
    for c, v in s.items():
        if not v:
            continue
        if c in ("HQ", "MEHQ"):
            h += v * 0.0  # trace solids: sensible heat neglected (below 1 kW)
            continue
        h += v * (h_ig(c, T0) - hvap(c, T0) + cpl(c, 0.5 * (t + T0)) * (t - T0))
    return h


def t_mix(streams):
    """Adiabatic mixing of ideal-gas streams [(composition, T)]."""
    total = add(*[s for s, _ in streams])
    h = sum(h_gas(s, t) for s, t in streams)
    lo, hi = 250.0, 900.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if h_gas(total, mid) > h:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def solve(f_c3=1.0, pw=None, tol_mu=None, hq=None, mehq=None):
    """One pass of the plant for f_c3 kmol/h of propylene (the recycles iterated)."""
    c3 = z(); c3["C3H6"] = f_c3; c3["C3H8"] = f_c3 * (1 - Y_C3_FEED) / Y_C3_FEED
    air = {c: f_c3 * (AIR1 + AIR2) * AIR.get(c, 0.0) for c in COMPS}
    air1 = {c: air[c] * AIR1 / (AIR1 + AIR2) for c in COMPS}
    air2 = {c: air[c] - air1[c] for c in COMPS}
    stm1 = z(); stm1["H2O"] = f_c3 * STM1
    stm2 = z(); stm2["H2O"] = f_c3 * STM2
    s5 = add(c3, air1, stm1)
    # R101: selectivities per kmol of propylene converted
    conv = X1 * s5["C3H6"]
    acr, aa1, co2 = Y_ACR1 / X1 * conv, Y_AA1 / X1 * conv, 3 * (X1 - Y_ACR1 - Y_AA1) / X1 * conv
    e1, e2, e3 = acr, aa1, co2 / 3
    s6 = dict(s5)
    s6["C3H6"] -= e1 + e2 + e3; s6["O2"] -= e1 + 1.5 * e2 + 4.5 * e3
    s6["ACR"] += e1; s6["AA"] += e2; s6["CO2"] += 3 * e3; s6["H2O"] += e1 + e2 + 3 * e3
    s10 = add(s6, air2, stm2)
    # R201: acrolein converted to acrylic acid, acetic acid + CO2, and burnt
    acr_in = s10["ACR"]; acr_out = Y_ACR2 * f_c3
    e4 = (Y_AA2 - Y_AA1) * f_c3
    e5 = HAC_PER_AA * Y_AA2 * f_c3
    e6 = acr_in - acr_out - e4 - e5
    s11 = dict(s10)
    s11["ACR"] -= e4 + e5 + e6; s11["O2"] -= 0.5 * e4 + 1.5 * e5 + 3.5 * e6
    s11["AA"] += e4; s11["HAC"] += e5; s11["CO2"] += e5 + 3 * e6; s11["H2O"] += 2 * e6
    sel2 = {"AA": e4 / (e4 + e5 + e6), "HAC": e5 / (e4 + e5 + e6), "CO2": (e5 + 3 * e6) / (e4 + e5 + e6)}
    # T301 quench absorber: water to the gas at saturation, process water for 55 wt% AA
    gas_dry = {c: s11[c] * T301_GAS.get(c, 0.0) for c in COMPS if c != "H2O"}
    n_dry = sum(gas_dry.values())
    y_w = Chemical(CAS["H2O"], T=T_TOP_ABS).Psat / 1000.0 / P_TOP_ABS
    w_gas = y_w / (1 - y_w) * n_dry
    aa_b, hac_b = s11["AA"] * (1 - T301_GAS["AA"]), s11["HAC"] * (1 - T301_GAS["HAC"])
    m_w_b = (aa_b * MW["AA"]) / W_AA_BOTTOMS - aa_b * MW["AA"] - hac_b * MW["HAC"]
    w_b = m_w_b / MW["H2O"]
    if pw is None:
        pw = w_b + w_gas - s11["H2O"]
    s13 = z(); s13["H2O"] = pw
    t301_in = add(s11, s13)
    frac_w_gas = w_gas / t301_in["H2O"]
    gas_frac = dict(T301_GAS); gas_frac["H2O"] = frac_w_gas
    s14, s15 = split(t301_in, gas_frac)
    # C401/C402 loop with the toluene recycle S21 (tear)
    s21 = z()
    tol_mu = 0.0 if tol_mu is None else tol_mu
    hq = 0.0 if hq is None else hq
    for _ in range(20000):  # the toluene loop's gain is 0.99: converge tightly
        s19 = z(); s19["TOL"] = tol_mu
        s16 = z(); s16["HQ"] = hq
        c401_in = add(s15, s16, s19, s21)
        s17, s18 = split(c401_in, C401_AQ)
        s21_new, rest = split(s18, C402_TOP)
        side_frac = {c: C402_SIDE.get(c, 0.0) / (1 - C402_TOP.get(c, 0.0)) if C402_TOP.get(c, 0.0) < 1 else 0.0 for c in COMPS}
        s22, s23 = split(rest, side_frac)
        if max(abs(s21_new[c] - s21[c]) for c in COMPS) < 1e-15:
            s21 = s21_new
            break
        s21 = s21_new
    s24, s25 = split(s23, C404_TOP)
    s26 = z(); s26["MEHQ"] = 0.0 if mehq is None else mehq
    s27 = add(s24, s26)
    return dict(c3=c3, air=air, air1=air1, air2=air2, stm1=stm1, stm2=stm2, s5=s5, s6=s6, s10=s10,
                s11=s11, s13=s13, s14=s14, s15=s15, s16=s16, s17=s17, s18=s18, s19=s19, s21=s21,
                s22=s22, s23=s23, s24=s24, s25=s25, s26=s26, s27=s27, frac_w_gas=frac_w_gas,
                sel2=sel2, conv2=(e4 + e5 + e6) / acr_in, pw=pw)


def size():
    """Toluene make-up, HQ and MEHQ for their targets, then the propylene for the product."""
    # the plant is linear in the make-ups: the toluene in C401's bottoms grows by a constant
    # per kmol of make-up, so the make-up for 7 wt% follows from two runs (HQ iterated)
    tol_mu, hq = 0.0, 0.0
    for _ in range(20):
        b0 = solve(tol_mu=0.0, hq=hq)
        b1 = solve(tol_mu=1e-3, hq=hq)
        m0, t0 = mass(b0["s18"]), b0["s18"]["TOL"] * MW["TOL"]
        dm, dt = (mass(b1["s18"]) - m0) / 1e-3, (b1["s18"]["TOL"] * MW["TOL"] - t0) / 1e-3
        tol_mu = (W_TOL_C401 * m0 - t0) / (dt - W_TOL_C401 * dm)
        b = solve(tol_mu=tol_mu, hq=hq)
        hq = HQ_PPM_C401 * mass(b["s18"]) / MW["HQ"]
    b = solve(tol_mu=tol_mu, hq=hq)
    mehq = MEHQ_PPM / (1 - MEHQ_PPM) * mass(b["s24"]) / MW["MEHQ"]
    b = solve(tol_mu=tol_mu, hq=hq, mehq=mehq)
    scale = PRODUCT_KG_H / mass(b["s27"])
    return solve(scale, pw=b["pw"] * scale, tol_mu=tol_mu * scale, hq=hq * scale, mehq=mehq * scale), scale


def kg(s):
    return {c: s[c] * MW[c] for c in COMPS if s[c]}


def main():
    b, f = size()
    out = {}

    def cite(sid, **q):
        out.setdefault(sid, {}).update(q)

    # temperatures and pressures (D-006)
    T_C3, T_AIR, T_STM = 313.15, 298.15, iapws95_Tsat(1.1e6)
    # air compressor K101: 101.325 -> 230 kPa(a), isentropic 0.80, motor 0.95 (ASSUMED, D-006)
    p1, p2, eta, eta_m = 101.325, 230.0, 0.80, 0.95
    air = b["air"]
    lo, hi = T_AIR, 600.0
    def s_ig(t):
        return sum(v * (R * sum(MAT[c]["ideal_gas"]["cp_R"][i] * (t ** i - T_AIR ** i) / i if i else MAT[c]["ideal_gas"]["cp_R"][0] * math.log(t / T_AIR) for i in range(5))) for c, v in air.items() if v)
    n_air = sum(air.values())
    target = n_air * R * math.log(p2 / p1)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if s_ig(mid) > target:
            hi = mid
        else:
            lo = mid
    t2s = 0.5 * (lo + hi)
    dh_s = h_gas(air, t2s) - h_gas(air, T_AIR)
    dh = dh_s / eta
    lo, hi = T_AIR, 700.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if h_gas(air, mid) - h_gas(air, T_AIR) > dh:
            hi = mid
        else:
            lo = mid
    t_k101 = 0.5 * (lo + hi)
    p_k101 = dh / 3600.0 / eta_m   # kW
    t5 = t_mix([(b["c3"], T_C3), (b["air1"], t_k101), (b["stm1"], T_STM)])
    T6 = 533.15
    t10 = t_mix([(b["s6"], T6), (b["air2"], t_k101), (b["stm2"], T_STM)])
    T11, T12 = 538.15, 443.15
    # reactor duties (core writes them; printed as a cross-check)
    q_r101 = (h_gas(b["s5"], t5) - h_gas(b["s6"], T6)) / 3600.0
    q_r201 = (h_gas(b["s10"], t10) - h_gas(b["s11"], T11)) / 3600.0
    q_e301 = (h_gas(b["s11"], T11) - h_gas(b["s11"], T12)) / 3600.0
    # quench absorber T301 (D-007): gas to 313.15 K, bottoms at 333.15 K, process water at 298.15 K
    T14, T15, T13 = T_TOP_ABS, 333.15, 298.15
    q_t301 = (h_gas(b["s11"], T12) + h_liq(b["s13"], T13) - h_gas(b["s14"], T14) - h_liq(b["s15"], T15)) / 3600.0
    # catalytic oxidiser X401 (D-011): adiabatic, the off-gas's organics burnt at 99 %
    s14 = b["s14"]
    s30 = dict(s14)
    for c, (o2, co2, h2o) in {"C3H6": (4.5, 3, 3), "C3H8": (5, 3, 4), "ACR": (3.5, 3, 2), "AA": (3, 3, 2), "HAC": (2, 2, 2)}.items():
        x = s14[c] * X401_CONV
        s30[c] -= x; s30["O2"] -= o2 * x; s30["CO2"] += co2 * x; s30["H2O"] += h2o * x
    h_in = h_gas(s14, T14)
    lo, hi = 300.0, 1200.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if h_gas(s30, mid) > h_in:
            hi = mid
        else:
            lo = mid
    t30 = 0.5 * (lo + hi)
    # dehydration column C401 (D-008): 24.0 kPa top (180 mmHg), top 322.15 K, bottoms 363.15 K;
    # toluene reflux 2.57 kg per kg of feed (Example 1: 830 ml/h toluene, 0.867 kg/l, on 280 g/h)
    T17, T18, T16, T19, T21 = 322.15, 363.15, 298.15, 298.15, 313.15
    m15 = mass(b["s15"])
    rho_tol = Chemical(CAS["TOL"], T=T0).rhol / 1000.0
    reflux_tol = 830.0 * 0.001 * rho_tol / 0.280 * m15 / MW["TOL"]   # kmol/h toluene refluxed
    s17 = b["s17"]
    q_c401_cond = (reflux_tol * hvap("TOL", T17) + sum(s17[c] * hvap(c, T17) for c in ("H2O", "HAC", "AA", "TOL") if s17[c])) / 3600.0
    sens_in = h_liq(b["s15"], T15) + h_liq(b["s16"], T16) + h_liq(b["s19"], T19) + h_liq(b["s21"], T21)
    sens_out = h_liq(s17, T17) + h_liq(b["s18"], T18)
    q_c401_reb = q_c401_cond + (sens_out - sens_in) / 3600.0
    # acetic acid column C402 (D-008): 13.3 kPa top (100 mmHg), reflux ratio 3 on the top product,
    # top product subcooled to 313.15 K, side draw 333.15 K, bottoms at acrylic acid's boiling
    # point at 15 kPa(a)
    lo, hi = 300.0, 450.0
    aa = Chemical(CAS["AA"])
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if aa.VaporPressure(mid) > 15000.0:
            hi = mid
        else:
            lo = mid
    T23 = 0.5 * (lo + hi)
    T22 = 333.15
    s21, s22, s23 = b["s21"], b["s22"], b["s23"]
    q_c402_cond = 4.0 * sum(s21[c] * hvap(c, T21) for c in ("H2O", "HAC", "AA", "TOL") if s21[c]) / 3600.0
    q_c402_reb = q_c402_cond + (h_liq(s21, T21) + h_liq(s22, T22) + h_liq(s23, T23) - h_liq(b["s18"], T18)) / 3600.0
    # product column C404 (D-009): 8 kPa(a) top, reflux ratio 1, distillate subcooled to
    # 303.15 K; bottoms at acrylic acid's boiling point at 10 kPa(a)
    def tsat_aa(p):
        lo, hi = 280.0, 450.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if aa.VaporPressure(mid) > p:
                hi = mid
            else:
                lo = mid
        return 0.5 * (lo + hi)
    T24top, T25 = tsat_aa(8000.0), tsat_aa(10000.0)
    T24, T27 = 303.15, 303.15
    s24 = b["s24"]
    q_c404_cond = (2.0 * sum(s24[c] * hvap(c, T24top) for c in ("H2O", "HAC", "AA", "TOL") if s24[c])
                   + h_liq(s24, T24top) - h_liq(s24, T24)) / 3600.0
    q_c404_reb = 2.0 * sum(s24[c] * hvap(c, T24top) for c in ("H2O", "HAC", "AA", "TOL") if s24[c]) / 3600.0 \
        + (h_liq(s24, T24top) + h_liq(b["s25"], T25) - h_liq(s23, T23)) / 3600.0

    # ---- print ---------------------------------------------------------------------------------
    print(f"scale: {f:.6f} kmol/h propylene; product {mass(b['s27']):.3f} kg/h")
    for k in ("c3", "air", "stm1", "stm2", "s13", "s16", "s19", "s26"):
        print(f"feed {k}: {mass(b[k]):.3f} kg/h")
    for k in ("s5", "s6", "s10", "s11", "s14", "s15", "s17", "s18", "s21", "s22", "s23", "s24", "s25", "s27"):
        m = mass(b[k]); print(f"{k}: {m:.3f} kg/h  " + ", ".join(f"{c} {v / m * 100:.3f}" for c, v in kg(b[k]).items()))
    print(f"T301 water to gas fraction {b['frac_w_gas']:.8f}; R201 conversion {b['conv2']:.8f} selectivities {b['sel2']}")
    print(f"T K101 {t_k101:.2f}, T5 {t5:.2f}, T10 {t10:.2f}, T steam {T_STM:.2f}, T30 {t30:.2f}, T23 {T23:.2f}, T24top {T24top:.2f}, T25 {T25:.2f}")
    print(f"P K101 {p_k101:.1f} kW; R101 {q_r101:.1f} kW; R201 {q_r201:.1f} kW (cross-check of core's duties)")
    print(f"E301 {q_e301:.1f}; T301 {q_t301:.1f}; C401 reb {q_c401_reb:.1f} cond {q_c401_cond:.1f}; "
          f"C402 reb {q_c402_reb:.1f} cond {q_c402_cond:.1f}; C404 reb {q_c404_reb:.1f} cond {q_c404_cond:.1f} kW")
    aa_kg = mass(b["s27"])
    print(f"per kg product: propylene {mass(b['c3']) / aa_kg:.4f} kg, steam {(mass(b['stm1']) + mass(b['stm2'])) / aa_kg:.4f} kg, "
          f"export {(q_r101 + q_r201) / aa_kg:.4f} kWh, LPS {(q_c401_reb + q_c402_reb + q_c404_reb) / aa_kg:.4f} kWh")
    print(f"AA yield on propylene fed: {b['s27']['AA'] / b['c3']['C3H6'] * 100:.2f} %")

    r = lambda v, n=3: round(v, n)
    cite("S1", flow=r(mass(b["c3"])), temperature=T_C3)
    cite("S2", flow=r(mass(b["air"])))
    cite("S3", temperature=r(t_k101, 2))
    cite("S4", flow=r(mass(b["stm1"])), temperature=r(T_STM, 2))
    cite("S5", temperature=r(t5, 2))
    cite("S7", temperature=r(t_k101, 2))
    cite("S8", temperature=r(t_k101, 2))
    cite("S9", flow=r(mass(b["stm2"])), temperature=r(T_STM, 2))
    cite("S10", temperature=r(t10, 2))
    cite("S13", flow=r(mass(b["s13"])))
    cite("S16", flow=r(mass(b["s16"])))
    cite("S19", flow=r(mass(b["s19"])))
    cite("S23", temperature=r(T23, 2))
    cite("S25", temperature=r(T25, 2))
    cite("S26", flow=r(mass(b["s26"])))
    cite("S30", temperature=r(t30, 2))
    for qid, v in (("Q1", p_k101), ("Q4", q_e301), ("Q5", q_t301), ("Q6", q_c401_reb), ("Q7", q_c401_cond),
                   ("Q8", q_c402_reb), ("Q9", q_c402_cond), ("Q10", q_c404_reb), ("Q11", q_c404_cond)):
        cite(qid, duty=r(v, 1))
    write_balance_output({"design": out})
    print(f"T301 H2O gas fraction for the flowsheet: {b['frac_w_gas']:.8f}")


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
