"""Concept heat and material balance of phosgene-1 (DESIGN.md D-006).

Independent of cheme-as-code's property packages, which cover neither phosgene nor the caustic
scrubber liquor. Ideal gas with the Cp/R polynomials of process/materials.yaml;
condensation by Raoult's law with the phosgene and chlorine vapour pressures of the `thermo`
package (cheme chemistry props, Thermo), the non-condensables (CO, N2, O2) insoluble (ASSUMED).
Liquid enthalpy = ideal-gas enthalpy minus the heat of vaporization (Watson from 253.15 K).

Run: cheme run scripts/balance.py   (prints the stream table and duties; writes nothing)
"""

import json
import math
import sys

R = 8.314462618e-3  # kJ/(mol K) == MJ/(kmol K)

# ideal-gas data (cheme chemistry thermo; materials.yaml): dHf kJ/mol, cp/R polynomial
# (cheme chemistry thermo NAME --fit 298.15,1500; the condensation below 298 K extrapolates)
IG = {
    "CO": (-110.525, [3.77154, -0.0020965, 5.00055e-06, -3.5253e-09, 8.41146e-13]),
    "CL2": (0.0, [3.29047, 0.00398283, -5.15265e-06, 3.0598e-09, -6.79757e-13]),
    "COCL2": (-219.030, [3.57477, 0.0158369, -1.73691e-05, 9.14793e-09, -1.87533e-12]),
    "N2": (0.0, [3.79935, -0.00209702, 4.57541e-06, -3.03024e-09, 6.85763e-13]),
    "O2": (0.0, [3.33121, 3.73673e-05, 2.68405e-06, -2.58548e-09, 7.32021e-13]),
    "AR": (0.0, [2.5, 0, 0, 0, 0]),
    "H2O": (-241.822, [3.95742, -0.000363702, 2.42862e-06, -1.27073e-09, 2.12761e-13]),
    "CO2": (-393.474, [2.35127, 0.00919285, -7.99057e-06, 3.68269e-09, -7.05913e-13]),
    "HCL": (-92.173, [3.72699, -0.00134502, 2.41915e-06, -1.18644e-09, 1.87246e-13]),
}
MW = {"CO": 28.010, "CL2": 70.906, "COCL2": 98.916, "N2": 28.013, "O2": 31.999, "AR": 39.948,
      "H2O": 18.015, "CO2": 44.010, "HCL": 36.461, "NAOH": 39.997, "NACL": 58.443,
      "NA2CO3": 105.989, "NAOCL": 74.442}

# vapour pressure (kPa) and heat of vaporization (kJ/mol) at 253.15 K, Tc (K): cheme chemistry
# props <name> -p vapor_pressure -p heat_of_vaporization --temperature T --source Thermo
VAP = {"COCL2": {"Tc": 455.0, "dHv253": 26.019}, "CL2": {"Tc": 416.865, "dHv253": 19.768}}
# phosgene: NIST Antoine log10(P/bar) = 4.27105 - 1072.71/(T - 29.855), 281-447 K (NIST WebBook,
# Stull 1947); below 281 K the Thermo value at 253.15 K (30.56 kPa) is used.
PSAT_253 = {"COCL2": 30.565, "CL2": 180.378}


def psat(c, T):
    if c == "COCL2":
        if T >= 281.0:
            return 100.0 * 10 ** (4.27105 - 1072.71 / (T - 29.855))
        if abs(T - 253.15) < 0.01:
            return PSAT_253[c]
        raise ValueError(T)
    if c == "CL2":
        # chlorine: the Thermo values at 253.15 K and 308.15 K (cheme chemistry props)
        return {253.15: 180.378, 308.15: 1007.963}[round(T, 2)]
    raise KeyError(c)


def h_ig(c, T):
    """kJ/mol, formation basis at 298.15 K."""
    dhf, a = IG[c]
    def H(t):
        return sum(a[i] * t ** (i + 1) / (i + 1) for i in range(5))
    return dhf + R * (H(T) - H(298.15))


def dhvap(c, T):
    d = VAP[c]
    return d["dHv253"] * ((1 - T / d["Tc"]) / (1 - 253.15 / d["Tc"])) ** 0.38


def H_gas(n, T):  # n: kmol/h -> kW
    return sum(v * h_ig(c, T) for c, v in n.items() if v) * 1000 / 3600


def H_liq(n, T):
    return sum(v * (h_ig(c, T) - dhvap(c, T)) for c, v in n.items() if v) * 1000 / 3600


def flash(n, T, P):
    """Raoult flash; CO, N2, O2 non-condensable. Returns (vapour, liquid) kmol/h."""
    cond = [c for c in n if c in ("COCL2", "CL2")]
    K = {c: psat(c, T) / P for c in cond}
    lo, hi = 1e-9, 1 - 1e-9
    nc = sum(v for c, v in n.items() if c not in cond)
    tot = sum(n.values())
    # liquid-fraction iteration on L: L = sum n_i / (1 + K_i * V/L)
    L = sum(n[c] for c in cond) * 0.9
    for _ in range(500):
        V = tot - L
        Lnew = sum(n[c] / (1 + K[c] * V / L) for c in cond)
        if abs(Lnew - L) < 1e-12:
            break
        L = 0.5 * (L + Lnew)
    V = tot - L
    liq = {c: n[c] / (1 + K[c] * V / L) for c in cond}
    vap = {c: n[c] - liq.get(c, 0.0) for c in n}
    return vap, liq


def mass(n):
    return sum(v * MW[c] for c, v in n.items())


def frac(n, basis="mole"):
    tot = sum(n.values()) if basis == "mole" else mass(n)
    return {c: (v if basis == "mole" else v * MW[c]) / tot for c, v in n.items() if v > 0}


def mix_T(streams, guess=300.0):
    Htot = sum(H_gas(n, T) for n, T in streams)
    nsum = {}
    for n, _ in streams:
        for c, v in n.items():
            nsum[c] = nsum.get(c, 0) + v
    T = guess
    for _ in range(100):
        f = H_gas(nsum, T) - Htot
        dT = 0.01
        df = (H_gas(nsum, T + dT) - H_gas(nsum, T)) / dT
        T -= f / df
    return nsum, T


# ---------------------------------------------------------------- basis (DESIGN.md)
CL2_KG_H = 12500.0          # D-002: Cl2 of chlor-alkali-1's design (12 500 kg/h), ASSUMED
X_O2_CL2 = 0.001            # D-003: phosgene-grade chlorine 0.1 mol% O2, ASSUMED
CO_EXCESS = 0.05            # D-004: 5 % molar CO excess (EP1640341: 2-20 %, preferably 5-12 %)
X_N2_CO = 0.002             # D-003: CO 99.8 mol%, impurities lumped as N2, ASSUMED
X_CL2 = 0.99995             # D-005: Cl2 conversion, ASSUMED to meet < 50 ppm Cl2 (EP1640341)
T_CO, T_CL2 = 303.15, 313.15
T_R_OUT = 353.15            # D-005: outlet below 100 C (EP1640341)
P_R_OUT = 350.0
T_E102, P_E102 = 308.15, 345.0   # D-007 cooling-water condenser
T_V101, P_V101 = 253.15, 340.0   # D-007 brine condenser and separator
NAOH_RATIO = 1.5            # D-008: NaOH fed / stoichiometric, ASSUMED
W_NAOH_DIL = 0.18           # D-008: scrubbing liquor 18 wt% NaOH, ASSUMED
X_SCRUB = 0.9999            # D-008: phosgene and Cl2 destroyed in the scrubber, ASSUMED
T_SCRUB_GAS, P_SCRUB = 303.15, 120.0
PSAT_H2O_303 = 4.247        # kPa, water at 303.15 K (IAPWS-95, thermo)
T_EFF = 313.15
X_CO_OX = 0.999             # D-009: CO destruction in the thermal oxidiser, ASSUMED
X_PHOS_OX = 0.99            # D-009: residual phosgene hydrolysed in the oxidiser, ASSUMED
T_OX = 1123.15              # D-009: oxidiser outlet 850 C, ASSUMED; air flow set to reach it
AIR = {"N2": 0.7812, "O2": 0.2095, "AR": 0.0093}

# ---------------------------------------------------------------- feeds
n_cl2 = CL2_KG_H / MW["CL2"]
S2 = {"CL2": n_cl2, "O2": n_cl2 * X_O2_CL2 / (1 - X_O2_CL2)}
n_co = n_cl2 * (1 + CO_EXCESS)
S1 = {"CO": n_co, "N2": n_co * X_N2_CO / (1 - X_N2_CO)}
S3, T3 = mix_T([(S1, T_CO), (S2, T_CL2)])
S3 = {"CO": S3["CO"], "CL2": S3["CL2"], "N2": S3["N2"], "O2": S3["O2"]}

# ---------------------------------------------------------------- reactor
xi = X_CL2 * S3["CL2"]
S4 = dict(S3)
S4["CO"] -= xi
S4["CL2"] -= xi
S4["COCL2"] = xi
Q_R = H_gas(S4, T_R_OUT) - H_gas(S3, T3)          # kW, negative: heat removed

# ---------------------------------------------------------------- condensation
v5, l5 = flash(S4, T_E102, P_E102)
Q_E102 = H_gas(v5, T_E102) + H_liq(l5, T_E102) - H_gas(S4, T_R_OUT)
v6, l6 = flash(S4, T_V101, P_V101)
Q_E103 = H_gas(v6, T_V101) + H_liq(l6, T_V101) - (H_gas(v5, T_E102) + H_liq(l5, T_E102))
S7 = {c: l6.get(c, 0.0) for c in ("COCL2", "CL2")}
S8 = {c: v for c, v in v6.items() if v > 0}

# ---------------------------------------------------------------- caustic scrubber
d_phos = X_SCRUB * S8["COCL2"]
d_cl2 = X_SCRUB * S8["CL2"]
naoh_stoich = 4 * d_phos + 2 * d_cl2
naoh = NAOH_RATIO * naoh_stoich
S20 = {"NAOH": naoh, "H2O": naoh * MW["NAOH"] / MW["H2O"]}           # 50 wt% NaOH
m_dil = naoh * MW["NAOH"] / W_NAOH_DIL
S21 = {"H2O": (m_dil - mass(S20)) / MW["H2O"]}
S22 = {"NAOH": naoh, "H2O": S20["H2O"] + S21["H2O"]}
gas_dry = {c: v for c, v in S8.items()}
gas_dry["COCL2"] -= d_phos
gas_dry["CL2"] -= d_cl2
y_w = PSAT_H2O_303 / P_SCRUB
n_dry = sum(gas_dry.values())
S23 = dict(gas_dry)
S23["H2O"] = n_dry * y_w / (1 - y_w)
S24 = {
    "NAOH": naoh - naoh_stoich,
    "NACL": 2 * d_phos + d_cl2,
    "NA2CO3": d_phos,
    "NAOCL": d_cl2,
    "H2O": S22["H2O"] + 2 * d_phos + d_cl2 - S23["H2O"],
}

# ---------------------------------------------------------------- thermal oxidiser


def ox_out(n_air):
    a = {c: n_air * f for c, f in AIR.items()}
    o = {c: S23.get(c, 0.0) + a.get(c, 0.0) for c in set(S23) | set(a)}
    e_co = X_CO_OX * S23["CO"]
    e_ph = X_PHOS_OX * S23["COCL2"]
    o["CO"] -= e_co
    o["O2"] -= 0.5 * e_co
    o["CO2"] = o.get("CO2", 0.0) + e_co + e_ph
    o["COCL2"] -= e_ph
    o["H2O"] -= e_ph
    o["HCL"] = 2 * e_ph
    return a, o


T_AIR_IN, T_AIR_OUT = 298.15, 303.15
lo, hi = 1.0, 5000.0
for _ in range(200):
    mid = 0.5 * (lo + hi)
    a, o = ox_out(mid)
    resid = H_gas(o, T_OX) - H_gas(S23, T_SCRUB_GAS) - H_gas(a, T_AIR_OUT)
    if resid > 0:    # outlet enthalpy too high: too much air to heat
        hi = mid
    else:
        lo = mid
S30, S32 = ox_out(mid)
S31 = S30

# ---------------------------------------------------------------- power (ASSUMED, D-010)
rho_air = 101.325 * 28.96 / (R * 1000 * T_AIR_IN)        # kg/m3
V_air = mass(S30) / rho_air / 3600                          # m3/s
W_K301 = V_air * 5.0 / 0.65 / 0.95                          # 5 kPa, fan 0.65, motor 0.95
W_P201 = 30.0 / 3600 * 300.0 / 0.60 / 0.95                  # 30 m3/h circulation, 300 kPa
W_R101 = 10.0                                               # coolant-circuit vacuum pump, ASSUMED

streams = {
    "S1": (S1, T_CO, 400.0, "vapor"), "S2": (S2, T_CL2, 400.0, "vapor"),
    "S3": (S3, T3, 390.0, "vapor"), "S4": (S4, T_R_OUT, P_R_OUT, "vapor"),
    "S5": ({c: v5.get(c, 0) + l5.get(c, 0) for c in S4}, T_E102, P_E102, "two-phase"),
    "S6": ({c: v6.get(c, 0) + l6.get(c, 0) for c in S4}, T_V101, P_V101, "two-phase"),
    "S7": (S7, T_V101, P_V101, "liquid"), "S8": (S8, T_V101, P_V101, "vapor"),
    "S20": (S20, 313.15, 400.0, "liquid"), "S21": (S21, 298.15, 400.0, "liquid"),
    "S22": (S22, 303.15, 400.0, "liquid"), "S23": (S23, T_SCRUB_GAS, P_SCRUB, "vapor"),
    "S24": (S24, T_EFF, 200.0, "liquid"), "S30": (S30, T_AIR_IN, 101.325, "vapor"),
    "S31": (S31, T_AIR_OUT, 106.3, "vapor"), "S32": (S32, T_OX, 101.325, "vapor"),
}
duties = {"Q1 R101 to cooling water": -Q_R, "Q2 E102 to cooling water": -Q_E102,
          "Q3 E103 to brine": -Q_E103, "Q4 T201 pump": W_P201, "Q5 K301 fan": W_K301,
          "Q6 R101 vacuum pump": W_R101}

out = {"streams": {}, "duties_kW": duties}
for k, (n, T, P, ph) in streams.items():
    n = {c: v for c, v in n.items() if v > 1e-12}
    out["streams"][k] = {"T": round(T, 2), "P": P, "phase": ph, "kg_h": round(mass(n), 3),
                         "kmol_h": round(sum(n.values()), 5),
                         "x": {c: round(v, 10) for c, v in frac(n).items()},
                         "w": {c: round(v, 10) for c, v in frac(n, "mass").items()}}
out["checks"] = {
    "phosgene_kg_h": mass({"COCL2": S7["COCL2"]}),
    "cl2_in_product_ppm_wt": 1e6 * S7["CL2"] * MW["CL2"] / mass(S7),
    "phosgene_to_vent_fraction": S8["COCL2"] / S4["COCL2"],
    "yield_on_cl2": S7["COCL2"] / n_cl2,
    "air_kmol_h": mid,
    "flue_o2_mol": S32["O2"] / sum(S32.values()),
    "mass_in": mass(S1) + mass(S2) + mass(S20) + mass(S21) + mass(S30),
    "mass_out": mass(S7) + mass(S24) + mass(S32),
    "dH_rxn_298_kJ_mol": h_ig("COCL2", 298.15) - h_ig("CO", 298.15) - h_ig("CL2", 298.15),
}
json.dump(out, sys.stdout, indent=1)
print()
