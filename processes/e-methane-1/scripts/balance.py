"""What core cannot calculate in the e-methane plant (DESIGN.md D-002 to D-010).

The plant is the two-stage catalytic methanation of the STORE&GO demonstration at Falkenhagen
(STORE&GO D5.9, DVGW 2020, sections 2.1 and 4.1, Table 4-1 and appendix 8.4) at its measured
operating point of 200 Nm3/h hydrogen (9.0045 kmol/h, 95 % load) with stoichiometric CO2, the
CO2 taken from a dense-phase CO2 pipeline instead of the demonstration's liquid CO2 tank (D-003).
cheme process propagate computes the mixers, both reactors as conversion steps (the honeycomb
reactor at the measured 92 %, the polishing reactor at the equilibrium conversion this script
solves), the knock-outs, the dryer and the condensate tank from process/flowsheet.yaml with this
script's recoveries, and writes both reactors' heat (Q3, Q5). Core does not solve an
equilibrium reactor (DESIGN.md L-2), so this script is the source of R-102's conversion. It gives
what core has no model for:

- the feeds: hydrogen (dry, from the electrolysis plant) and CO2 at the stoichiometric ratio of
  four (D5.9 appendix 8.4: the ASPEN model's basis), with carbon-capture-1's 500 ppm water;
- the hydrogen compressor's power, two intercooled stages, ideal gas, and the heat its coolers
  reject (D-006);
- the CO2 let-down heater's duty, dense CO2 at 15.3 MPa and 303.15 K to gas at 1.53 MPa and
  313.15 K, from the Span-Wagner equation of state in CoolProp 8.0.0 (D-003);
- the feed/effluent exchanger, the coolers and the electric preheater of the polishing reactor,
  from the ideal-gas enthalpies of process/materials.yaml (the same core uses), with the
  condensed water's heat of vaporisation from IAPWS-95 (`chemicals` 1.5.2): the effluent is
  below its dew point (about 445 K) on leaving E-101, so its outlet is solved two-phase (D-007);
- the knock-out drums' split: the gas leaves saturated with water at the drum's temperature and
  pressure (IAPWS-95 vapour pressure, Raoult/Dalton), and the condensate holds the gases
  dissolved by Henry's law (ChemSep Henry constants in `thermo` 0.6.1), released at the
  condensate tank (D-007, L-4);
- the polishing reactor's ideal-gas equilibrium of the Sabatier and reverse water-gas shift
  reactions, and its conversion of the CO2 given to the flowsheet (D-005);
- the electricity, computed part by part: the compressor, the electric preheater, the chiller
  of the 10 C coolers and the fans and pumps (D-006); the grid injection compressor at 0.1 kWh
  per Nm3 of SNG (D5.9 Table 4-2) and the heat of its aftercooler (D-008);
- cross-checks against the source: SNG output, methanation efficiency (HHV), heat, and the
  methanation unit's electricity against D5.9's 41 kW measured as built and 0.7 kWh/m3 with a
  changed compressor configuration (section 4.1.2, Table 4-2).

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
from thermo.interaction_parameters import IPDB

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
T_AIR = 333.15         # D5.9 section 2.1: the air cooler after the feed/effluent exchanger, to 60 C
P_S8 = 1440.0          # ASSUMED pressure drops
P_KO1 = 1420.0
T_R102 = 513.15        # D5.9 appendix 8.4: about 240 C, isothermal fixed bed
P_R102 = 1400.0
P_KO2 = 1380.0
P_DRY = 1350.0
T_SNG = 313.15         # SNG after the injection compressor's aftercooler (D-008)
KWH_INJ = 0.1          # kWh per Nm3 SNG, D5.9 Table 4-2 (injection unit)
P_EL_METH = 41.0       # kW, D5.9 Table 4-1: the methanation plant as built (the mixed feed compressed), a cross-check only
KWH_METH_OPT = 0.7     # kWh per m3 SNG, D5.9 section 4.1.2 and Table 4-2: with a changed compressor configuration, a cross-check only
ETA_IS = 0.70          # isentropic efficiency of the hydrogen compressor stages, ASSUMED
STAGES = 2             # ASSUMED
COP_CHILL = 3.0        # chiller of the 10 C coolers, kW cold per kW electric, ASSUMED
F_AUX = 0.02           # fans of the air coolers and pumps of the oil and cooling circuits, kW per kW of heat rejected to air, ASSUMED

# Henry's law constants of the gases in water: the ChemSep Henry parameters packaged in thermo
# 0.6.1 (IPDB "ChemSep Henry", ln H/Pa = A + B/T + C ln T + D T + E T^2 + F/T^2; single package
# values with their source, library ADR 0037); DESIGN.md SRC-6
CAS = {"H2": "1333-74-0", "CO2": "124-38-9", "CH4": "74-82-8", "CO": "630-08-0"}
CAS_WATER = "7732-18-5"


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


def henry(c, T):
    """Pa per mole fraction, the gas c in water (ChemSep Henry, thermo 0.6.1)."""
    k = {x: IPDB.get_ip_specific("ChemSep Henry", [CAS[c], CAS_WATER], x) for x in "ABCDEF"}
    return math.exp(k["A"] + k["B"] / T + k["C"] * math.log(T) + k["D"] * T + k["E"] * T ** 2
                    + k["F"] / T ** 2)


def knockout(n, T, P, dissolve=False):
    """Gas saturated with water at T, P (kPa); the rest condenses. With dissolve, the condensate
    holds the gases at Henry's law equilibrium with the outlet gas. Returns (gas, liquid)."""
    y = iapws95_Psat(T) / 1000.0 / P
    sol = {c: 0.0 for c in n}  # dissolved, kmol/h
    for _ in range(20):  # successive substitution: the dissolved gas leaves the gas phase
        dry = sum(v - sol[c] for c, v in n.items() if c != "H2O")
        w_gas = min(n["H2O"], y / (1.0 - y) * dry)
        gas = {c: (w_gas if c == "H2O" else n[c] - sol[c]) for c in n}
        w_liq = n["H2O"] - w_gas
        if not dissolve or w_liq <= 0:
            break
        tot = sum(gas.values())
        x = {c: gas[c] / tot * P * 1000.0 / henry(c, T) for c in CAS if n.get(c, 0.0) > 0}
        sol = dict({c: 0.0 for c in n}, **{c: xc / (1.0 - sum(x.values())) * w_liq for c, xc in x.items()})
    liq = {c: (w_liq if c == "H2O" else sol[c]) for c in n}
    return gas, liq


def H2p(n, T, P):
    """kW, the stream n at T and P (kPa) with its water condensed to saturation (no dissolved gas)."""
    _, liq = knockout(n, T, P)
    return H(n, T) - liq["H2O"] * hvap_water(T) / 3600.0


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


def compressor_power(n, t_suction, p_in, p_out):
    """Ideal gas, equal pressure ratio per stage, each stage's suction temperature given
    (the first the feed's, the next after an intercooler); constant cp per stage. kW and the
    hottest stage outlet, K."""
    r = (p_out / p_in) ** (1.0 / len(t_suction))
    w, t_max = 0.0, 0.0
    for T_in in t_suction:
        k_cp = sum(v * cp(c, T_in) for c, v in n.items()) / sum(n.values())
        kappa = k_cp / (k_cp - R)
        dt = T_in * (r ** ((kappa - 1) / kappa) - 1) / ETA_IS
        w += k_cp * dt  # J/mol
        t_max = max(t_max, T_in + dt)
    return w * sum(n.values()) / 3600.0, t_max


def main():
    comps = ["H2", "CO2", "CH4", "CO", "H2O"]
    z = {c: 0.0 for c in comps}
    s1 = dict(z, H2=N_H2)
    n_co2 = N_H2 / STOICH
    s3 = dict(z, CO2=n_co2, H2O=n_co2 * Y_H2O_CO2 / (1 - Y_H2O_CO2))

    # hydrogen compressor K-101 (D-006): the first stage from the feed, the second after the
    # intercooler at T_IC; the coolers take the work less the gas's warming to T_IC
    w_k101, t_k101 = compressor_power(s1, [T_FEED, T_IC], P_H2_IN, P_REACT + 30.0)
    q_ic = w_k101 - (H(s1, T_IC) - H(s1, T_FEED))
    # the as-built configuration (the mixed feed compressed, D5.9 section 2.1) under the same
    # assumptions, a cross-check of the measured 41 kW only (D-006)
    w_mixed, _ = compressor_power({c: s1[c] + s3[c] for c in comps}, [T_FEED, T_IC], P_H2_IN,
                                  P_REACT + 30.0)
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
    # E-101 hot side: the effluent gives q_e101; its water starts to condense at the dew point,
    # so the outlet S8 is solved two-phase (D-007)
    y_w7 = s7["H2O"] / sum(s7.values())
    lo, hi = 300.0, T_R101
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if iapws95_Psat(mid) / 1000.0 > y_w7 * P_S8:
            hi = mid
        else:
            lo = mid
    t_dew7 = 0.5 * (lo + hi)
    lo, hi = 300.0, T_R101
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if H(s7, T_R101) - H2p(s7, mid, P_S8) > q_e101:
            lo = mid
        else:
            hi = mid
    t_s8 = 0.5 * (lo + hi)
    _, liq8 = knockout(s7, t_s8, P_S8)
    vf_s8 = 1.0 - liq8["H2O"] / sum(s7.values())
    # air cooler E-102 to 60 C, chilled-water cooler E-103 to 10 C and knock-out V-101, with
    # the gases dissolved in the condensate (L-4)
    s9, s10 = knockout(s7, T_KO, P_KO1, dissolve=True)
    q_ko1 = H2p(s7, t_s8, P_S8) - H(s9, T_KO) - (H(s10, T_KO) - s10["H2O"] * hvap_water(T_KO) / 3600.0)
    q_e102 = H2p(s7, t_s8, P_S8) - H2p(s7, T_AIR, P_S8)
    q_e103 = q_ko1 - q_e102
    _, liq_air = knockout(s7, T_AIR, P_S8)
    # electric preheater E-104 of the polishing reactor (D5.9 appendix 8.4)
    w_e104 = H(s9, T_R102) - H(s9, T_KO)
    # R-102: the ideal-gas equilibrium, given to the flowsheet as a conversion of the CO2 (D-005)
    s12, ext = equilibrium(s9, T_R102, P_R102)
    q_r102 = H(s9, T_R102) - H(s12, T_R102)
    x_r102 = 1 - s12["CO2"] / s9["CO2"]
    # the flowsheet's step: the Sabatier reaction alone at that conversion (no CO, L-2)
    e_sab = x_r102 * s9["CO2"]
    s12f = {c: s9[c] + SAB.get(c, 0) * e_sab for c in comps}
    yq = mol_frac(s12f)
    lnq_r102 = (math.log(yq["CH4"] * yq["H2O"] ** 2 / (yq["CO2"] * yq["H2"] ** 4) / (P_R102 / 100.0) ** 2)
                - lnK(SAB, T_R102))
    # product gas coolers E-105 (air to 60 C, chilled water to 10 C) and knock-out V-102
    s13, s14 = knockout(s12f, T_KO, P_KO2, dissolve=True)
    q_ko2 = H(s12f, T_R102) - H(s13, T_KO) - (H(s14, T_KO) - s14["H2O"] * hvap_water(T_KO) / 3600.0)
    q_e105_air = H(s12f, T_R102) - H2p(s12f, T_AIR, P_KO2)
    q_e105_chill = q_ko2 - q_e105_air
    # dryers A-201: the residual water removed (D-008)
    s16 = dict(s13, H2O=0.0)
    s17 = {"H2O": s13["H2O"]}
    nm3_sng = sum(s16.values()) * NM3
    # injection compressor K-201 and its aftercooler (D-008)
    w_k201 = KWH_INJ * nm3_sng
    q_k201 = w_k201 - (H(s16, T_SNG) - H(s16, T_KO))
    # condensate tank: the dissolved gases released at atmospheric pressure (L-4)
    s15 = {c: s10[c] + s14[c] + (s17["H2O"] if c == "H2O" else 0.0) for c in comps}
    vent = {c: s15[c] for c in comps if c != "H2O"}
    q_oil = q_r101 + q_r102 - q_e100
    # electricity of the methanation unit, part by part (D-006): the chiller of the 10 C coolers
    # and the fans and pumps of the heat rejected to air
    w_chill = (q_e103 + q_e105_chill) / COP_CHILL
    q_air = q_ic + q_e102 + q_e105_air + q_oil + q_k201
    w_aux = F_AUX * q_air
    w_bop = round(w_chill, 2) + round(w_aux, 2)
    w_meth = round(w_k101, 2) + round(w_e104, 2) + w_bop

    # cross-checks against D5.9 Table 4-1
    hhv_h2 = 285830.0  # J/mol, H2O(l) -285.830 kJ/mol (CODATA 1989), as the registry derives HHVs
    hhv_ch4 = -(MAT["CH4"]["ideal_gas"]["dHf_298"] * -1 + 2 * -285830.0 + MAT["CO2"]["ideal_gas"]["dHf_298"])
    e_h2 = s1["H2"] * hhv_h2 / 3600.0
    e_sng = s16["CH4"] * hhv_ch4 / 3600.0
    y16 = mol_frac(s16)
    rec = {k: {c: round(g[c] / n[c], 10) for c in comps if n[c] > 0}
           for k, g, n in (("V101", s9, s7), ("V102", s13, s12f))}
    checks = {
        "H2_in_kW_HHV": round(e_h2, 1), "D5.9_H2_in_kW": "708 measured, 715 ASPEN",
        "SNG_CH4_kW_HHV": round(e_sng, 1), "D5.9_SNG_kW": "549 measured, 557 ASPEN",
        "eta_SNG_HHV": round(e_sng / e_h2, 4), "D5.9_eta": "0.775 measured, 0.780 ASPEN",
        "CH4_mol_pct_dry": round(100 * y16["CH4"], 3), "D5.9_CH4": "99 vol-%",
        "H2_conversion_overall": round(1 - s16["H2"] / s1["H2"], 5), "D5.9_X_H2": "0.99 measured, 1.00 ASPEN",
        "R101_heat_kW": round(q_r101, 2), "R102_heat_kW": round(q_r102, 2),
        "oil_heat_net_kW": round(q_oil, 2), "D5.9_heat_usage_kW": "86 measured, 103 ASPEN",
        "heat_kWh_per_Nm3": round(q_oil / nm3_sng, 3), "D5.9_heat_kWh_per_m3": "1.7 (initial), 2.1 optimised",
        "methanation_unit_kW": round(w_meth, 2), "el_meth_kWh_per_Nm3": round(w_meth / nm3_sng, 3),
        "D5.9_el_meth": "41 kW, 0.8 kWh/m3 as built (mixed feed compressed); 0.7 kWh/m3 with a changed compressor configuration",
        "D5.9_0.7_kWh_per_m3_as_kW": round(KWH_METH_OPT * nm3_sng, 2),
        "K101_kW": round(w_k101, 2), "K101_stage_outlet_K": round(t_k101, 1),
        "K101_mixed_feed_as_built_kW": round(w_mixed, 2),
        "E104_kW": round(w_e104, 2), "chiller_kW": round(w_chill, 2), "fans_pumps_kW": round(w_aux, 2),
        "BoP_kW": round(w_bop, 2), "electricity_total_kW": round(w_meth + round(w_k201, 2), 2),
        "electricity_kWh_per_kg": round((w_meth + round(w_k201, 2)) / mass_flow(s16), 4),
        "electricity_kWh_per_Nm3": round((w_meth + round(w_k201, 2)) / nm3_sng, 4),
        "CO2_JT_outlet_K_isenthalpic": round(t_jt, 1), "E100_kW": round(q_e100, 2),
        "SNG_Nm3_per_h": round(nm3_sng, 2), "SNG_kg_per_h": round(mass_flow(s16), 3),
        "R102_extents_kmol_h": [round(v, 6) for v in ext],
        "R102_X_CO2_equilibrium": round(x_r102, 8),
        "R102_out_mol_frac": {c: round(v, 7) for c, v in mol_frac(s12).items()},
        "R102_lnQ_over_K_Sabatier_step": round(lnq_r102, 4),
        "recoveries_to_gas": rec,
        "E101_kW": round(q_e101, 2), "S7_dew_point_K": round(t_dew7, 2), "S8_K": round(t_s8, 2),
        "S8_vapor_fraction": round(vf_s8, 4), "S8_water_condensed_kmol_h": round(liq8["H2O"], 4),
        "water_condensed_at_60C_kmol_h": round(liq_air["H2O"], 4), "S7_water_kmol_h": round(s7["H2O"], 4),
        "KO1_cooling_kW": round(q_ko1, 2), "E102_air_kW": round(q_e102, 2), "E103_chilled_kW": round(q_e103, 2),
        "KO2_cooling_kW": round(q_ko2, 2), "E105_air_kW": round(q_e105_air, 2), "E105_chilled_kW": round(q_e105_chill, 2),
        "intercoolers_kW": round(q_ic, 2), "K201_aftercooler_kW": round(q_k201, 2),
        "heat_to_air_kW": round(q_air, 2),
        "vent_kg_h": {c: round(v * MW[c], 5) for c, v in vent.items()},
        "vent_kg_per_kg_SNG": {c: round(v * MW[c] / mass_flow(s16), 7) for c, v in vent.items()},
        "Henry_283K_Pa": {c: float(f"{henry(c, T_KO):.4g}") for c in CAS},
    }
    print(json.dumps(checks, indent=1))

    cases = {"design": {
        "S1": {"flow": round(mass_flow(s1), 6), "composition": {c: round(v, 7) for c, v in mol_frac(s1).items()}},
        "S3": {"flow": round(mass_flow(s3), 6), "composition": {c: round(v, 7) for c, v in mol_frac(s3).items()}},
        "S8": {"temperature": round(t_s8, 2), "phase": "two-phase"},
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
        "Q9": {"duty": round(q_k201, 2)},
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
