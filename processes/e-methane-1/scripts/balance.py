"""What core cannot calculate in the e-methane plant (DESIGN.md D-002 to D-010).

The plant is the two-stage catalytic methanation of the STORE&GO demonstration at Falkenhagen
(STORE&GO D5.9, DVGW 2020, sections 2.1 and 4.1, Table 4-1 and appendix 8.4) at its measured
operating point of 200 Nm3/h hydrogen (9.0045 kmol/h, 95 % load) with stoichiometric CO2, the
CO2 taken from a dense-phase CO2 pipeline instead of the demonstration's liquid CO2 tank (D-003).
cheme process propagate computes the mixer, the honeycomb reactor's conversion (92 %), the
polishing reactor's ideal-gas equilibrium, the knock-outs, the dryer and the condensate mixer
from process/flowsheet.yaml, and writes R-101's duty. This script gives what core has no model
for:

- the feeds: hydrogen (dry, from the electrolysis plant) and CO2 at the stoichiometric ratio of
  four (D5.9 appendix 8.4: the ASPEN model's basis), with carbon-capture-1's 500 ppm water;
- the hydrogen compressor's power, two intercooled stages, ideal gas (D-006);
- the CO2 let-down heater's duty, dense CO2 at 15.3 MPa and 303.15 K to gas at 1.5 MPa and
  313.15 K, from the Span-Wagner equation of state in CoolProp 8.0.0 (D-003);
- the feed/effluent exchanger, the coolers and the electric preheater of the polishing reactor,
  from the ideal-gas enthalpies of process/materials.yaml (the same core uses), with the
  condensed water's heat of vaporisation from IAPWS-95 (`chemicals` 1.5.2);
- the knock-out drums' split: the gas leaves saturated with water at the drum's temperature and
  pressure (IAPWS-95 vapour pressure, Raoult/Dalton, the gases' solubility in the condensate
  neglected, L-4);
- the polishing reactor's equilibrium and duty, solved here with the same ideal-gas data as a
  cross-check of core's equilibrium model;
- the remaining electricity of the methanation unit: D5.9 Table 4-1 measured 41 kW at this
  load; the compressor and the electric preheater computed here, the rest (refrigeration of the
  10 C cooler, oil and cooling pumps, fans, instruments) as the difference (D-006); and the
  grid injection compressor at 0.1 kWh per Nm3 of SNG (D5.9 Table 4-2);
- cross-checks against the source: SNG output, methanation efficiency (HHV), heat, power.

Run: `cheme run scripts/balance.py`. With BALANCE_OUTPUT set it writes the values the flowsheet
cites (library ADR 0027). Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import yaml
from chemicals.iapws import iapws95_Psat, iapws95_dPsat_dT, iapws95_rhog_sat, iapws95_rhol_sat
from CoolProp.CoolProp import PropsSI

ROOT = Path(__file__).resolve().parent.parent
R = 8.314462618  # J/(mol K)
T0 = 298.15
NM3 = 22.414  # Nm3 per kmol, ideal gas at 273.15 K and 101.325 kPa (the flowsheet's normal conditions)

# --- design point (D-002) ---------------------------------------------------------------------
N_H2 = 9.0045          # kmol/h, D5.9 section 4.1: 200 Nm3/h H2, 95 % load of the methanation unit
STOICH = 4.0           # H2/CO2, D5.9 appendix 8.4 (the ASPEN model's ideal ratio)
Y_H2O_CO2 = 0.0005     # mol/mol water in the CO2, carbon-capture-1's 500 ppm (its process.yaml)
X_R101 = 0.92          # D5.9 Table 4-1: honeycomb conversion rate, measured and ASPEN (D-004)

# temperatures (K) and pressures (kPa(a)), D-004 to D-008
T_FEED = 303.15        # hydrogen from the electrolysis plant, ASSUMED
P_H2_IN = 120.0        # ASSUMED, an atmospheric alkaline electrolyser's outlet (D-006)
T_IC = 313.15          # after each intercooler / aftercooler, ASSUMED
P_REACT = 1500.0       # D5.9 section 2.1: compressed up to 14 bar, read as gauge (ASSUMED)
T_CO2_PIPE, P_CO2_PIPE = 303.15, 15300.0   # carbon-capture-1's dense-phase product
T_R101_IN = 523.15     # ASSUMED light-off temperature of the nickel honeycomb (D-004)
T_R101 = 623.15        # D5.9 appendix 8.4: about 350 C, isothermal (ASPEN)
T_KO = 283.15          # D5.9 section 2.1: water cooler to 10 C before each separator
P_KO1 = 1420.0         # ASSUMED pressure drops
T_R102 = 513.15        # D5.9 appendix 8.4: about 240 C, isothermal fixed bed
P_R102 = 1400.0
P_KO2 = 1380.0
P_DRY = 1350.0
KWH_INJ = 0.1          # kWh per Nm3 SNG, D5.9 Table 4-2 (injection unit)
P_EL_METH = 41.0       # kW, D5.9 Table 4-1: electricity demand of the methanation plant at this point
ETA_IS = 0.70          # isentropic efficiency of the hydrogen compressor stages, ASSUMED
STAGES = 2             # ASSUMED


def load_materials():
    doc = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text(encoding="utf-8"))
    return {c["id"]: c for c in doc["components"]}


MAT = load_materials()
MW = {k: v["molar_mass"] for k, v in MAT.items()}


def cp(c, T):
    a = MAT[c]["ideal_gas"]["cp_R"]
    return R * sum(ai * T ** i for i, ai in enumerate(a))


def h(c, T):
    """Ideal-gas molar enthalpy, J/mol, formation basis at 298.15 K."""
    a = MAT[c]["ideal_gas"]["cp_R"]
    integ = sum(ai / (i + 1) * (T ** (i + 1) - T0 ** (i + 1)) for i, ai in enumerate(a))
    return MAT[c]["ideal_gas"]["dHf_298"] + R * integ


def s(c, T):
    a = MAT[c]["ideal_gas"]["cp_R"]
    integ = a[0] * math.log(T / T0) + sum(ai / i * (T ** i - T0 ** i) for i, ai in enumerate(a) if i)
    return MAT[c]["ideal_gas"]["S_298"] + R * integ


def H(n, T):
    """kW for a stream of n kmol/h at T."""
    return sum(v * h(c, T) for c, v in n.items()) / 3600.0


def hvap_water(T):
    """J/mol, Clausius-Clapeyron on IAPWS-95 (chemicals 1.5.2)."""
    dv = 1.0 / iapws95_rhog_sat(T) - 1.0 / iapws95_rhol_sat(T)  # m3/kg
    return T * dv * iapws95_dPsat_dT(T)[0] * MW["H2O"] / 1000.0 if isinstance(iapws95_dPsat_dT(T), tuple) \
        else T * dv * iapws95_dPsat_dT(T) * MW["H2O"] / 1000.0


def knockout(n, T, P):
    """Gas saturated with water at T, P; the rest condenses. Returns (gas, liquid, rec_H2O)."""
    y = iapws95_Psat(T) / 1000.0 / P
    dry = sum(v for c, v in n.items() if c != "H2O")
    w_gas = min(n["H2O"], y / (1.0 - y) * dry)
    gas = dict(n, H2O=w_gas)
    liq = {"H2O": n["H2O"] - w_gas}
    return gas, liq, w_gas / n["H2O"]


def lnK(rx, T):
    dG = sum(nu * (h(c, T) - T * s(c, T)) for c, nu in rx.items())
    return -dG / (R * T)


SAB = {"CO2": -1, "H2": -4, "CH4": 1, "H2O": 2}
RWGS = {"CO2": -1, "H2": -1, "CO": 1, "H2O": 1}


def equilibrium(n0, T, P):
    """Ideal-gas equilibrium of SAB and RWGS at T, P (kPa); Newton on the two extents."""
    K1, K2 = math.exp(lnK(SAB, T)), math.exp(lnK(RWGS, T))
    p = P / 100.0  # bar, standard state 1 bar

    def comp(e):
        n = dict(n0)
        for rx, x in ((SAB, e[0]), (RWGS, e[1])):
            for c, nu in rx.items():
                n[c] = n.get(c, 0.0) + nu * x
        return n

    def f(e):
        n = comp(e)
        if min(n.values()) <= 0:
            return None
        tot = sum(n.values())
        y = {c: v / tot for c, v in n.items()}
        g1 = math.log(y["CH4"] * y["H2O"] ** 2 / (y["CO2"] * y["H2"] ** 4) / p ** 2) - math.log(K1)
        g2 = math.log(y["CO"] * y["H2O"] / (y["CO2"] * y["H2"])) - math.log(K2)
        return g1, g2

    e = [0.9 * n0["CO2"], 1e-6 * n0["CO2"]]
    for _ in range(200):
        g = f(e)
        J = []
        for j in range(2):
            d = max(abs(e[j]) * 1e-7, 1e-14)
            ep = list(e)
            ep[j] += d
            gp = f(ep)
            J.append([(gp[i] - g[i]) / d for i in range(2)])
        det = J[0][0] * J[1][1] - J[1][0] * J[0][1]
        dx0 = (-g[0] * J[1][1] + g[1] * J[1][0]) / det
        dx1 = (-g[1] * J[0][0] + g[0] * J[0][1]) / det
        step = 1.0
        while True:
            en = [e[0] + step * dx0, e[1] + step * dx1]
            if f(en) is not None:
                break
            step /= 2
        e = en
        if abs(dx0) + abs(dx1) < 1e-14:
            break
    return comp(e), e


def mol_frac(n):
    tot = sum(n.values())
    return {c: v / tot for c, v in n.items()}


def mass_flow(n):
    return sum(v * MW[c] for c, v in n.items())


def compressor_power(n, T_in, p_in, p_out):
    """Ideal-gas, equal pressure ratio per stage, intercooled to T_in, kW."""
    k_cp = sum(v * cp(c, T_in) for c, v in n.items()) / sum(n.values())
    kappa = k_cp / (k_cp - R)
    r = (p_out / p_in) ** (1.0 / STAGES)
    w = STAGES * k_cp * T_in * (r ** ((kappa - 1) / kappa) - 1) / ETA_IS  # J/mol
    t_out = T_in * (1 + (r ** ((kappa - 1) / kappa) - 1) / ETA_IS)
    return w * sum(n.values()) / 3600.0, t_out


def main():
    comps = ["H2", "CO2", "CH4", "CO", "H2O"]
    z = {c: 0.0 for c in comps}
    s1 = dict(z, H2=N_H2)
    n_co2 = N_H2 / STOICH
    s3 = dict(z, CO2=n_co2, H2O=n_co2 * Y_H2O_CO2 / (1 - Y_H2O_CO2))

    # hydrogen compressor K-101 (D-006)
    w_k101, t_k101 = compressor_power(s1, T_FEED, P_H2_IN, P_REACT + 30.0)
    q_ic = w_k101  # the compression work ends as heat in the intercoolers and aftercooler (ideal gas, T_out = T_in + ...)
    # CO2 let-down heater E-100 (D-003): Span-Wagner via CoolProp, pure CO2
    h_in = PropsSI("H", "T", T_CO2_PIPE, "P", P_CO2_PIPE * 1e3, "CO2")
    h_out = PropsSI("H", "T", T_IC, "P", (P_REACT + 30.0) * 1e3, "CO2")
    q_e100 = (h_out - h_in) * mass_flow(s3) / 3600.0 / 1000.0  # kW
    t_jt = PropsSI("T", "H", h_in, "P", (P_REACT + 30.0) * 1e3, "CO2")

    s5 = {c: s1[c] + s3[c] for c in comps}
    # feed/effluent exchanger E-101 cold side
    q_e101 = H(s5, T_R101_IN) - H(s5, T_IC)
    # R-101 (core computes the outlet; repeated here for the duties)
    x = X_R101 * s5["CO2"]
    s7 = {c: s5[c] + SAB.get(c, 0) * x for c in comps}
    q_r101 = H(s5, T_R101_IN) - H(s7, T_R101)
    # E-101 hot side: the effluent gives q_e101
    lo, hi = 300.0, T_R101
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if H(s7, T_R101) - H(s7, mid) > q_e101:
            lo = mid
        else:
            hi = mid
    t_s8 = 0.5 * (lo + hi)
    # E-102/E-103 coolers and knock-out V-101
    s9, s10, rec1 = knockout(s7, T_KO, P_KO1)
    q_ko1 = H(s7, t_s8) - H(s9, T_KO) - (H(s10, T_KO) - s10["H2O"] * hvap_water(T_KO) / 3600.0)
    # electric preheater E-104 of the polishing reactor (D5.9 appendix 8.4)
    w_e104 = H(s9, T_R102) - H(s9, T_KO)
    # R-102 equilibrium (core computes it; the duty and a cross-check here)
    s12, ext = equilibrium(s9, T_R102, P_R102)
    q_r102 = H(s9, T_R102) - H(s12, T_R102)
    # E-105/E-106 coolers and knock-out V-102
    s13, s14, rec2 = knockout(s12, T_KO, P_KO2)
    q_ko2 = H(s12, T_R102) - H(s13, T_KO) - (H(s14, T_KO) - s14["H2O"] * hvap_water(T_KO) / 3600.0)
    # dryers A-201: the residual water removed (D-008)
    s16 = dict(s13, H2O=0.0)
    s17 = {"H2O": s13["H2O"]}
    nm3_sng = sum(s16.values()) * NM3
    w_k201 = KWH_INJ * nm3_sng
    w_bop = P_EL_METH - round(w_k101, 2) - round(w_e104, 2)  # the residual of the rounded parts
    q_oil = q_r101 + q_r102 - q_e100

    # cross-checks against D5.9 Table 4-1
    hhv_h2 = 285830.0  # J/mol, H2O(l) -285.830 kJ/mol (CODATA 1989), as the registry derives HHVs
    hhv_ch4 = -(MAT["CH4"]["ideal_gas"]["dHf_298"] * -1 + 2 * -285830.0 + MAT["CO2"]["ideal_gas"]["dHf_298"])
    e_h2 = s1["H2"] * hhv_h2 / 3600.0
    e_sng = s16["CH4"] * hhv_ch4 / 3600.0
    y16 = mol_frac(s16)
    checks = {
        "H2_in_kW_HHV": round(e_h2, 1), "D5.9_H2_in_kW": "708 measured, 715 ASPEN",
        "SNG_CH4_kW_HHV": round(e_sng, 1), "D5.9_SNG_kW": "549 measured, 557 ASPEN",
        "eta_SNG_HHV": round(e_sng / e_h2, 4), "D5.9_eta": "0.775 measured, 0.780 ASPEN",
        "CH4_mol_pct_dry": round(100 * y16["CH4"], 3), "D5.9_CH4": "99 vol-%",
        "H2_conversion_overall": round(1 - s16["H2"] / s1["H2"], 5), "D5.9_X_H2": "0.99 measured, 1.00 ASPEN",
        "R101_heat_kW": round(q_r101, 2), "R102_heat_kW": round(q_r102, 2),
        "oil_heat_net_kW": round(q_oil, 2), "D5.9_heat_usage_kW": "86 measured, 103 ASPEN",
        "heat_kWh_per_Nm3": round(q_oil / nm3_sng, 3), "D5.9_heat_kWh_per_m3": "1.7 (initial), 2.1 optimised",
        "el_meth_kWh_per_Nm3": round(P_EL_METH / nm3_sng, 3), "D5.9_el_kWh_per_m3": "0.8",
        "K101_kW": round(w_k101, 2), "K101_stage_outlet_K": round(t_k101, 1),
        "E104_kW": round(w_e104, 2), "BoP_kW": round(w_bop, 2),
        "CO2_JT_outlet_K_isenthalpic": round(t_jt, 1), "E100_kW": round(q_e100, 2),
        "SNG_Nm3_per_h": round(nm3_sng, 2), "SNG_kg_per_h": round(mass_flow(s16), 3),
        "R102_extents_kmol_h": [round(v, 6) for v in ext],
        "R102_X_CO2_equilibrium": round(1 - s12["CO2"] / s9["CO2"], 6),
        "R102_out_mol_frac": {c: round(v, 7) for c, v in mol_frac(s12).items()},
        "rec_H2O_gas_KO1": round(rec1, 7), "rec_H2O_gas_KO2": round(rec2, 7),
        "E101_kW": round(q_e101, 2), "S8_K": round(t_s8, 2),
        "KO1_cooling_kW": round(q_ko1, 2), "KO2_cooling_kW": round(q_ko2, 2),
        "intercoolers_kW": round(q_ic, 2),
    }
    print(json.dumps(checks, indent=1))

    def mf(n):
        return {c: round(v, 7) for c, v in mol_frac(n).items()}

    cases = {"design": {
        "S1": {"flow": round(mass_flow(s1), 3), "composition": mf(s1)},
        "S3": {"flow": round(mass_flow(s3), 3), "composition": mf(s3)},
        "S8": {"temperature": round(t_s8, 2)},
        "W1": {"duty": round(w_k101, 2)},
        "Q0": {"duty": round(q_ic, 2)},
        "Q1": {"duty": round(q_e100, 2)},
        "Q2": {"duty": round(q_e101, 2)},
        "Q4": {"duty": round(q_ko1, 2)},
        "W3": {"duty": round(w_e104, 2)},
        "Q6": {"duty": round(q_ko2, 2)},
        "W2": {"duty": round(w_bop, 2)},
        "W4": {"duty": round(w_k201, 2)},
        "Q8": {"duty": round(q_oil, 2)},
    }}
    write_balance_output(cases)


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
