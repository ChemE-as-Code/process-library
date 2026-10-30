"""Steady-state mass and energy balance of the acetaldehyde-1 one-stage Wacker process concept.

Provenance only (DESIGN.md D-006): the stream values of process/flowsheet.yaml that cheme cannot
calculate (separator outlets, the cycle-gas loop, duties) come from this script and are entered
there as ASSUMED with the decision ids. Run: cheme run scripts/acet_balance.py
It prints a summary and writes build/acet_streams.yaml (scratch, pasted into the flowsheet).

Every specification below is a design choice (ASSUMED) or a sourced fact; the decision id says
which. Standard library only. Units: kmol/h inside, kg/h out, kW, K, kPa(a).
"""
import math
import os

# --- molar masses (kg/kmol) and ideal-gas cp/R polynomials (cheme chemistry thermo, chemicals
#     package: Poling 5th ed. or TRCIG/Joback fits; D-005)
M = {"C2H4": 28.0532, "C2H6": 30.069, "O2": 31.9988, "AR": 39.948, "CO2": 44.0095,
     "H2O": 18.01528, "ACH": 44.0526, "ACOH": 60.052, "CAC": 78.4977, "CROT": 70.0898,
     "ETCL": 64.5141, "MECL": 50.4875, "HCL": 36.4609}
CPR = {"C2H4": [4.221, -0.008782, 5.795e-05, -6.729e-08, 2.511e-11],
       "C2H6": [4.178, -0.004427, 5.66e-05, -6.651e-08, 2.487e-11],
       "O2": [3.63, -0.001794, 6.58e-06, -6e-09, 1.79e-12],
       "AR": [2.5],
       "CO2": [3.259, 0.001356, 1.502e-05, -2.374e-08, 1.056e-11],
       "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
       "ACH": [3.37483, 0.00702043, 2.06222e-05, -2.7856e-08, 1.03703e-11],
       "ACOH": [4.375, -0.002397, 6.757e-05, -8.764e-08, 3.478e-11],
       "CAC": [3.05023, 0.0210597, -1.18348e-05, 2.34531e-09],
       "CROT": [2.64692, 0.0320811, -8.22443e-06, -8.46203e-09, 4.80523e-12],
       "ETCL": [3.029, 0.009885, 2.967e-05, -4.55e-08, 1.871e-11],
       "MECL": [3.578, -0.00175, 3.071e-05, -3.714e-08, 1.408e-11],
       "HCL": [3.827, -0.002936, 8.79e-06, -1.031e-08, 4.39e-12]}
R = 8.314462618e-3                 # kJ/(mol K) -> kJ/kmol per K * 1000 handled below
# heats of vaporisation at 298 K (kJ/mol) for the liquid enthalpies (D-005; rounded literature
# values, ASSUMED +/-10 %): water 44.0, acetaldehyde 25.8, acetic acid 51.6 (monomer basis),
# crotonaldehyde 41, chloroacetaldehyde 37 (estimate)
LAMBDA = {"H2O": 44.0, "ACH": 25.8, "ACOH": 51.6, "CROT": 41.0, "CAC": 37.0}
CPL = {"H2O": 0.0754, "ACH": 0.0897, "ACOH": 0.123, "CROT": 0.14, "CAC": 0.13}  # kJ/(mol K)

# --- reactions (process/reactions.yaml); heats of reaction from ideal-gas formation enthalpies
DHF = {"C2H4": 52.56, "C2H6": -83.78, "O2": 0.0, "AR": 0.0, "CO2": -393.474, "H2O": -241.822,
       "ACH": -165.37, "ACOH": -432.2, "CAC": -191.0, "CROT": -100.6, "ETCL": -111.24,
       "MECL": -82.62, "HCL": -92.173}            # kJ/mol, 298.15 K, gas (cheme chemistry thermo)
RXN = {
    "R1": {"C2H4": -1, "O2": -0.5, "ACH": 1},                          # main Wacker reaction
    "R2": {"C2H4": -1, "O2": -1, "ACOH": 1},                           # acetic acid
    "R3": {"C2H4": -1, "O2": -3, "CO2": 2, "H2O": 2},                  # total oxidation
    "R4": {"C2H4": -1, "HCL": -1, "O2": -1, "CAC": 1, "H2O": 1},       # chlorinated aldehydes
    "R5": {"C2H4": -1, "HCL": -1, "ETCL": 1},                          # ethyl chloride
    "R6": {"C2H4": -1, "HCL": -1, "O2": -1.5, "MECL": 1, "CO2": 1, "H2O": 1},  # methyl chloride (lumped)
    "R7": {"ACH": -2, "CROT": 1, "H2O": 1},                            # aldol condensation
}
DH = {r: sum(n * DHF[k] for k, n in s.items()) for r, s in RXN.items()}  # kJ/mol

# --- specifications
P_KGH = 100_000e3 / 8000           # kg/h product (100 kt/a, 8000 h/a) (D-002)
W_ACH_PROD = 0.999                 # product acetaldehyde mass fraction, rest water (D-002)
# Ethylene fate per 100 mol fed, as reported for the industrial process (Wikipedia "Wacker
# process", section Industrial process, citing Eckert et al., Ullmann's, D-004): about 95
# acetaldehyde, 1.9 chlorinated aldehydes, 1.1 unconverted ethylene, 0.8 CO2, 0.7 acetic acid,
# minor products for the rest. Our split of the minor 0.5 and of the 1.9 (ASSUMED, D-004):
FATE = {"R3": 0.8, "R2": 0.7, "R4": 1.6, "CROT_C2": 0.25, "R5": 0.15, "R6": 0.10}
LOST_C2H4 = 1.1                    # mol per 100 fed leaves unconverted (purge + light ends)
X_PASS = 0.35                      # ethylene conversion per pass, ASSUMED (D-004)
Y_O2_CYCLE = 0.08                  # O2 mole fraction in the cycle gas, ASSUMED (D-007)
X_ETH = {"C2H4": 0.999, "C2H6": 0.001}   # polymer-grade ethylene, mole fractions (D-003)
X_OXY = {"O2": 0.995, "AR": 0.005}       # oxygen 99.5 mol%, rest argon (lumped inerts) (D-003)
W_HCL = 0.30                       # hydrochloric acid make-up, HCl mass fraction (D-003)
# water and steam per t of product scaled from the 13 t/h comparative example of US 4,237,073
# (Hoechst 1980, the fresh-water case): 15 m3/h demineralised water to the reactor, 77.5 m3/h
# wash water, 1.5 m3/h extraction water, 1.5 t/h regeneration steam, 3 and 14 t/h live steam
# to the two columns (D-006, D-008)
SC = P_KGH / 13000.0
DEMIN_R = 15000.0 * SC
WASH = 77500.0 * SC
EXTR = 1500.0 * SC
STM_REG = 1500.0 * SC
STM_C1 = 3000.0 * SC
STM_C2 = 14000.0 * SC
# Henry's law in water (NIST WebBook, SRD 69, Henry's law data, D-007): CO2 0.034 mol/(kg bar),
# 2400 K; ethylene 0.0047 mol/(kg bar), 1800 K
HENRY = {"CO2": (0.034, 2400.0), "C2H4": (0.0047, 1800.0)}
T_CRUDE = 313.15                   # crude acetaldehyde from scrubber and cooler (D-007)
P_SCRUB = 370.0                    # kPa(a) scrubber top (D-007)
Y_ACH_CYCLE = 0.0005               # acetaldehyde left in the scrubbed gas (D-007)
F_ACH_COND = 0.30                  # fraction of the acetaldehyde condensed in E-102 (D-007)
PSAT = {308.15: 5.63, 313.15: 7.38, 318.15: 9.59}  # water vapour pressure, kPa
ACH_LE = 0.002                     # acetaldehyde in the light ends, fraction of the feed (D-008)
CL_WW = 200e-6                     # organic Cl in the waste water, kg/kg, US 4,237,073 (D-008)
ACH_WW = 360e-6                    # aldehyde in the waste water, kg/kg, US 4,237,073 (D-008)
SIDE = {"org": 0.40, "ACH": 0.10, "H2O": 0.50}   # side-draw mass fractions (D-008)
T = {"R": 403.15, "E101": 383.15, "E102": 318.15, "SCR": 308.15, "MPS": 453.0, "LPS": 421.0,
     "C1B": 393.4, "C2B": 406.7, "C2D": 323.15, "SIDE": 340.0, "PROD": 303.15, "WW": 308.15,
     "FEEDC1": 383.15}
H_STEAM = {"MPS": 2777.1, "LPS": 2743.9}   # kJ/kg saturated steam 1000 / 450 kPa(a) (steam tables)
K_CG, ETA_CG = 1.30, 0.75          # cycle-gas compressor: heat capacity ratio, isentropic eff. (D-009)
P_CG_IN, P_CG_OUT = 370.0, 520.0


def h_gas(k, t):
    """kJ/mol of ideal gas k from 298.15 K to t."""
    a = CPR[k]
    f = lambda x: sum(c * x ** (i + 1) / (i + 1) for i, c in enumerate(a))
    return R * (f(t) - f(298.15))


def h_liq(k, t):
    """kJ/mol of liquid k at t, reference ideal gas at 298.15 K."""
    return -LAMBDA[k] + CPL[k] * (t - 298.15)


def henry(k, t):
    kh, b = HENRY[k]
    return kh * math.exp(b * (1.0 / t - 1.0 / 298.15))   # mol/(kg bar)


def add(*ss):
    out = {}
    for s in ss:
        for k, v in s.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(s, f):
    return {k: v * f for k, v in s.items()}


def sub(a, b):
    return add(a, scale(b, -1.0))


def mass(s):
    return {k: v * M[k] for k, v in s.items()}


def tot(s):
    return sum(s.values())


def H(s, t, liquid=()):
    return sum(n * (h_liq(k, t) if k in liquid else h_gas(k, t)) for k, n in s.items())


def solve(FE):
    n = {}
    fed = scale(X_ETH, FE / X_ETH["C2H4"])  # kmol/h fresh feed with FE kmol/h C2H4
    eth = fed["C2H4"]
    conv = eth * (100.0 - LOST_C2H4) / 100.0
    xi = {r: eth * FATE[r] / 100.0 for r in ("R2", "R3", "R4", "R5", "R6")}
    xi["R7"] = eth * FATE["CROT_C2"] / 100.0 / 2.0
    xi["R1"] = conv - sum(xi[r] for r in ("R2", "R3", "R4", "R5", "R6"))
    gen = {}
    for r, s in RXN.items():
        gen = add(gen, scale(s, xi[r]))
    o2_used = -gen["O2"]
    hcl_used = -gen["HCL"]
    inlet_e = conv / X_PASS
    rec_e = inlet_e - eth
    # crude water for gas solubility: wash water + condensed water (first estimate, refined)
    w_crude = WASH + DEMIN_R + STM_REG
    for _ in range(50):
        P = P_SCRUB / 100.0
        kE = henry("C2H4", T_CRUDE) * P * w_crude / 1000.0
        kC = henry("CO2", T_CRUDE) * P * w_crude / 1000.0
        y_w = PSAT[T["SCR"]] / P_SCRUB
        F_O2 = o2_used / X_OXY["O2"]
        for _ in range(50):
            F_AR = F_O2 * X_OXY["AR"]       # F_O2: total oxygen-feed flow, kmol/h
            lo, hi = 1e-3, 1e3
            for _ in range(200):
                Np = 0.5 * (lo + hi)
                y = {"C2H4": eth * LOST_C2H4 / 100.0 / (Np + kE), "CO2": gen["CO2"] / (Np + kC),
                     "AR": F_AR / Np, "C2H6": fed["C2H6"] / Np, "O2": Y_O2_CYCLE, "H2O": y_w,
                     "ACH": Y_ACH_CYCLE}
                if sum(y.values()) > 1.0:
                    lo = Np
                else:
                    hi = Np
            F_O2_new = (o2_used + Np * Y_O2_CYCLE) / X_OXY["O2"]
            if abs(F_O2_new - F_O2) < 1e-10:
                break
            F_O2 = F_O2_new
        N15 = Np + rec_e / y["C2H4"]
        s = Np / N15
        S15 = scale(y, N15)
        S18 = scale(S15, s)
        S19 = scale(S15, 1.0 - s)
        dissolved = {"C2H4": kE * y["C2H4"], "CO2": kC * y["CO2"]}
        S01 = fed
        S02 = add(S01, S19)
        S03 = scale(X_OXY, F_O2)
        S04 = {"HCL": hcl_used, "H2O": hcl_used * M["HCL"] * (1 - W_HCL) / W_HCL / M["H2O"]}
        S05 = {"H2O": DEMIN_R / M["H2O"]}
        S06 = {"H2O": STM_REG / M["H2O"]}
        # reactor energy balance (boiling-cooled, adiabatic): the condensate return S09 closes it
        Qrxn = -sum(xi[r] * DH[r] for r in RXN) * 1000.0 / 3600.0      # kW released
        t_mix = 298.15
        for _ in range(30):      # S02 temperature: adiabatic mixing of S01 (298 K) and S19
            t_mix = t_mix + (H(S19, T["K101"]) + H(S01, 298.15) - H(S02, t_mix)) / max(
                1e-9, sum(v * R * 4.5 for v in S02.values()))
        n["t_mix"] = t_mix
        h_in = (H(S02, t_mix) + H(S03, 298.15) + H(S04, 298.15, liquid=("H2O",))
                + H(S05, 298.15, liquid=("H2O",)) + H(S06, T["MPS"]))
        out_wo_ret = add(S02, S03, S04, S05, S06, gen)
        h_ret = h_liq("H2O", T["E101"])
        h_vap = h_gas("H2O", T["R"])
        W_ret = (h_in + Qrxn * 3.6 - H(out_wo_ret, T["R"])) / (h_vap - h_ret)   # kmol/h
        S09 = {"H2O": W_ret}
        S07 = add(out_wo_ret, S09)
        S08_liq, S10 = S09, sub(S07, S09)
        Q_E101 = (H(S07, T["R"]) - H(S10, T["E101"]) - H(S09, T["E101"], liquid=("H2O",))) / 3.6
        # E-102 / V-102: condense heavies, 30 % of the acetaldehyde and water to saturation
        gas13 = {k: v for k, v in S10.items() if k not in ("ACOH", "CAC", "CROT", "H2O", "ACH")}
        gas13["ACH"] = S10["ACH"] * (1 - F_ACH_COND)
        yw13 = PSAT[T["E102"]] / 380.0
        gas13["H2O"] = yw13 / (1 - yw13) * tot(gas13)
        S13 = gas13
        S12 = sub(S10, S13)
        Q_E102 = (H(S10, T["E101"]) - H(S13, T["E102"])
                  - H(S12, T["E102"], liquid=("H2O", "ACH", "ACOH", "CAC", "CROT"))) / 3.6
        # scrubber C-101: wash water absorbs the acetaldehyde, chlorides and dissolved gases
        S14 = {"H2O": WASH / M["H2O"]}
        S16 = sub(add(S13, S14), S15)
        w_new = (S16["H2O"] + S12["H2O"]) * M["H2O"]
        # gases dissolved in the crude: taken up in the scrubber (the E-102 condensate share is
        # small and counted there)
        if abs(w_new - w_crude) < 1e-6:
            break
        w_crude = w_new
    # the crude: S12 + S16; dissolved gases are in S16 by construction (S16 = S13 + S14 - S15)
    S21 = add(S12, S16)
    # light-ends column C-201 with extraction water and live steam
    S23 = {"H2O": EXTR / M["H2O"]}
    S24 = {"H2O": STM_C1 / M["H2O"]}
    S25 = {k: S21.get(k, 0.0) for k in ("C2H4", "C2H6", "CO2", "O2", "AR", "ETCL", "MECL")}
    S25 = {k: v for k, v in S25.items() if v > 1e-12}
    S25["ACH"] = ACH_LE * S21["ACH"]
    yw25 = PSAT[313.15] / 200.0
    S25["H2O"] = yw25 / (1 - yw25) * tot(S25)
    S26 = sub(add(S21, S23, S24), S25)
    # purification column C-202 with live steam: product, side draw, waste water
    S27 = {"H2O": STM_C2 / M["H2O"]}
    feed2 = add(S26, S27)
    acoh = feed2.get("ACOH", 0.0)
    # waste water: mass fixed by the water balance, solved by iteration
    side_org_kg = feed2["CROT"] * M["CROT"]
    m_ww = feed2["H2O"] * M["H2O"]
    for _ in range(50):
        cac_ww = CL_WW * m_ww / (35.453 / M["CAC"]) / M["CAC"]       # kmol/h
        ach_ww = ACH_WW * m_ww / M["ACH"]
        side_org_kg = feed2["CROT"] * M["CROT"] + (feed2["CAC"] - cac_ww) * M["CAC"]
        side_kg = side_org_kg / SIDE["org"]
        S30 = {"CROT": feed2["CROT"], "CAC": feed2["CAC"] - cac_ww,
               "ACH": SIDE["ACH"] * side_kg / M["ACH"], "H2O": SIDE["H2O"] * side_kg / M["H2O"]}
        ach_d = feed2["ACH"] - ach_ww - S30["ACH"]
        S28 = {"ACH": ach_d, "H2O": ach_d * M["ACH"] * (1 - W_ACH_PROD) / W_ACH_PROD / M["H2O"]}
        S31 = sub(feed2, add(S28, S30))
        m_new = tot(mass(S31))
        if abs(m_new - m_ww) < 1e-6:
            break
        m_ww = m_new
    S31 = {k: v for k, v in S31.items() if abs(v) > 1e-12}
    prod_kg = tot(mass(S28))
    # energies (kW)
    cp_w = 4.19                                                   # kJ/(kg K), aqueous streams
    m21, m31 = tot(mass(S21)), tot(mass(S31))
    Q_rec = m21 * cp_w * (T["FEEDC1"] - T_CRUDE) / 3600.0         # E-201 / E-202
    t_ww2 = T["C2B"] - Q_rec * 3600.0 / (m31 * cp_w)
    Q_C201 = (STM_C1 * (H_STEAM["LPS"] - cp_w * (T["C1B"] - 273.15))
              + m21 * cp_w * (T["FEEDC1"] - T["C1B"]) + EXTR * cp_w * (298.15 - T["C1B"])) / 3600.0
    m26 = tot(mass(S26))
    Q_C202 = (STM_C2 * (H_STEAM["LPS"] - cp_w * (T["C2B"] - 273.15))
              + m26 * cp_w * (T["C1B"] - T["C2B"])
              - prod_kg * 2.2 * (T["C2D"] - T["C2B"])
              - tot(mass(S30)) * 3.0 * (T["SIDE"] - T["C2B"])) / 3600.0
    Q_E203 = prod_kg * 2.2 * (T["C2D"] - T["PROD"]) / 3600.0
    Q_E204 = m31 * cp_w * (t_ww2 - T["WW"]) / 3600.0
    # cycle-gas compressor
    r = P_CG_OUT / P_CG_IN
    ex = (K_CG - 1) / K_CG
    t2 = T["SCR"] * (1 + (r ** ex - 1) / ETA_CG)
    W_K101 = tot(S15) * R * 1000 * K_CG / (K_CG - 1) * (t2 - T["SCR"]) / 3600.0
    # pumps (ASSUMED flows and heads, efficiency 0.70, D-009)
    pumps = {"R101": 50.0 * 1000.0 / 0.70 / 3600.0,          # catalyst to regenerator, 50 m3/h x 1000 kPa
             "C101": (WASH / 1000 * 500 + m21 / 950 * 400) / 0.70 / 3600.0,
             "C202": (4.2 * prod_kg / 780 * 300 + m31 / 950 * 300) / 0.70 / 3600.0}
    n.update(dict(S01=S01, S02=S02, S03=S03, S04=S04, S05=S05, S06=S06, S07=S07, S08=S07,
                  S09=S09, S10=S10, S11=S10, S12=S12, S13=S13, S14=S14, S15=S15, S16=S16,
                  S17=S15, S18=S18, S19=S19, S21=S21, S22=S21, S23=S23, S24=S24, S25=S25,
                  S26=S26, S27=S27, S28=S28, S29=S28, S30=S30, S31=S31, S32=S31, S33=S31))
    n.update(dict(xi=xi, gen=gen, Qrxn=Qrxn, Q_E101=Q_E101, Q_E102=Q_E102, Q_rec=Q_rec,
                  t_ww2=t_ww2, Q_C201=Q_C201, Q_C202=Q_C202, Q_E203=Q_E203, Q_E204=Q_E204,
                  W_K101=W_K101, t_K101=t2, pumps=pumps, s=s, prod_kg=prod_kg, kE=kE, kC=kC,
                  W_ret=W_ret, dissolved=dissolved))
    return n


T["K101"] = 341.7
FE = 300.0
for _ in range(60):
    res = solve(FE)
    T["K101"] = res["t_K101"]
    FE *= P_KGH / res["prod_kg"]
res = solve(FE)

kgh = {k: mass(v) for k, v in res.items() if k.startswith("S") and isinstance(v, dict)}
print(f"fresh ethylene {kgh['S01']['C2H4']:.1f} kg/h C2H4 ({tot(kgh['S01']) / P_KGH * 1000:.1f} kg/t product)")
print(f"oxygen {tot(kgh['S03']):.1f} kg/h ({tot(kgh['S03']) / P_KGH * 1000:.1f} kg/t)")
print(f"HCl 30 % {tot(kgh['S04']):.1f} kg/h; purge fraction {res['s']:.5f}; purge {tot(kgh['S18']):.1f} kg/h")
print("cycle gas mole fractions:", {k: round(v / tot(res['S15']), 4) for k, v in res["S15"].items()})
print(f"cycle gas {tot(res['S15']):.1f} kmol/h, reactor inlet C2H4 {res['S02']['C2H4']:.1f} kmol/h")
print(f"heat of reaction {res['Qrxn']:.0f} kW; condensate return {res['W_ret'] * M['H2O']:.0f} kg/h; feed gas {res['t_mix']:.1f} K")
for q in ("Q_E101", "Q_E102", "Q_rec", "Q_C201", "Q_C202", "Q_E203", "Q_E204", "W_K101"):
    print(f"{q} {res[q]:.1f} kW")
print(f"waste water out of E-202 {res['t_ww2']:.1f} K; K-101 outlet {res['t_K101']:.1f} K; pumps {res['pumps']}")
print("xi:", {k: round(v, 4) for k, v in res["xi"].items()})
# overall balance
ins = ("S01", "S03", "S04", "S05", "S06", "S14", "S23", "S24", "S27")
outs = ("S18", "S25", "S29", "S30", "S33")
m_in = sum(tot(kgh[s]) for s in ins)
m_out = sum(tot(kgh[s]) for s in outs)
print(f"overall mass in {m_in:.2f} out {m_out:.2f} kg/h, difference {m_in - m_out:.4f}")
for s in outs:
    print(s, {k: round(v, 3) for k, v in kgh[s].items()})

# stream table for process/flowsheet.yaml: id, title, from, to, template, P, T, decision;
# calc=True: flow and composition left to cheme process propagate (mixers, reactor, pass-through)
TK = res["t_K101"]
STREAMS = [
    ("S01", "Fresh ethylene", "ETH.out", "M101.eth", "ethylene", 600, 298.15, "D-003", False),
    ("S02", "Reactor feed gas", "M101.out", "R101.gas", "cycle-gas", 500, round(res["t_mix"], 1), "D-005", True),
    ("S03", "Oxygen", "OXY.out", "R101.o2", "oxygen", 600, 298.15, "D-003", False),
    ("S04", "Hydrochloric acid make-up", "HCLA.out", "R101.hcl", "hcl", 600, 298.15, "D-003, D-004", False),
    ("S05", "Demineralised water to the reactor", "DEMIN.r101", "R101.water", "water", 600, 298.15, "D-006", False),
    ("S06", "Regenerator steam", "MPS.out", "R101.steam", "water", 1000, 453.0, "D-006, D-009", False),
    ("S07", "Reactor vapour", "R101.out", "E101.in", "reactor-gas", 400, 403.15, "D-005", True),
    ("S08", "Precondenser outlet (two-phase)", "E101.out", "V101.in", "reactor-gas", 390, 383.15, "D-005", True),
    ("S09", "Condensate return to the reactor", "V101.liq", "R101.ret", "water", 390, 383.15, "D-005: reactor energy balance", False),
    ("S10", "Process gas to the cooler", "V101.gas", "E102.in", "reactor-gas", 390, 383.15, "D-005", False),
    ("S11", "Cooled process gas (two-phase)", "E102.out", "V102.in", "reactor-gas", 380, 318.15, "D-007", True),
    ("S12", "Acetaldehyde-rich condensate", "V102.liq", "T201.cond", "crude", 380, 318.15, "D-007", False),
    ("S13", "Gas to the scrubber", "V102.gas", "C101.gas", "reactor-gas", 380, 318.15, "D-007", False),
    ("S14", "Scrubber wash water", "PW.out", "C101.water", "water", 500, 298.15, "D-006, D-007", False),
    ("S15", "Scrubbed cycle gas (tear stream)", "C101.top", "K101.in", "cycle-gas", 370, 308.15, "D-007", False),
    ("S16", "Scrubber bottoms", "C101.liq", "T201.scrub", "crude", 370, 310.15, "D-007", False),
    ("S17", "Compressed cycle gas", "K101.out", "X101.in", "cycle-gas", 520, round(TK, 1), "D-009", True),
    ("S18", "Cycle-gas purge", "X101.purge", "PURGE.in", "cycle-gas", 520, round(TK, 1), "D-007", True),
    ("S19", "Recycle gas", "X101.rec", "M101.rec", "cycle-gas", 520, round(TK, 1), "D-007", True),
    ("S21", "Crude acetaldehyde", "T201.out", "E201.in", "crude", 450, 313.15, "D-007", True),
    ("S22", "Preheated crude", "E201.out", "C201.feed", "crude", 400, 383.15, "D-008", True),
    ("S23", "Extraction water", "DEMIN.c201", "C201.water", "water", 400, 298.15, "D-006, D-008", False),
    ("S24", "Live steam to the light-ends column", "LPS.c201", "C201.steam", "water", 450, 421.0, "D-006, D-008", False),
    ("S25", "Light ends", "C201.top", "LIGHTS.in", "light-ends", 200, 313.15, "D-008", False),
    ("S26", "Light-ends column bottoms", "C201.bot", "C202.feed", "crude", 200, 393.4, "D-008", False),
    ("S27", "Live steam to the acetaldehyde column", "LPS.c202", "C202.steam", "water", 450, 421.0, "D-006, D-008", False),
    ("S28", "Acetaldehyde distillate", "C202.top", "E203.in", "product", 270, 323.15, "D-008", False),
    ("S29", "Acetaldehyde product", "E203.out", "PROD.in", "product", 300, 303.15, "D-002", True),
    ("S30", "Heavy by-product side draw", "C202.side", "HEAVY.in", "side-draw", 280, 340.0, "D-008", False),
    ("S31", "Acetaldehyde column bottoms", "C202.bot", "E202.in", "wastewater", 300, 406.7, "D-008", False),
    ("S32", "Waste water after heat recovery", "E202.out", "E204.in", "wastewater", 280, round(res["t_ww2"], 1), "D-008", True),
    ("S33", "Waste water to treatment", "E204.out", "WW.in", "wastewater", 250, 308.15, "D-008", True),
]
SRC = "scripts/acet_balance.py"
os.makedirs("build", exist_ok=True)
with open("build/acet_streams.yaml", "w") as f:
    for sid, title, fr, to, tpl, p, t, dec, calc in STREAMS:
        f.write(f"  - id: {sid}\n    title: {title}\n    from: {fr}\n    to: {to}\n    template: {tpl}\n"
                f"    state:\n      design:\n"
                f"        pressure: {{value: {p}, provenance: assumed, source: \"{dec.split(':')[0]}\"}}\n"
                f"        temperature: {{value: {t}, provenance: assumed, source: \"{dec.split(':')[0]}\"}}\n")
        if not calc:
            s = {k: v for k, v in kgh[sid].items() if v > 1e-9}
            m = tot(s)
            comp = ", ".join(f"{k}: {v / m:.8f}" for k, v in sorted(s.items()))
            f.write(f"        flow: {{value: {m:.2f}, basis: mass, provenance: assumed, source: \"{SRC}, {dec}\"}}\n"
                    f"        composition: {{basis: mass_fraction, values: {{{comp}}}, provenance: assumed, source: \"{SRC}, {dec}\"}}\n")
    Q = [("Q01", "K-101 shaft power", "POWER.k101", "K101.power", res["W_K101"], "isentropic efficiency 0.75, 370 to 520 kPa(a), D-009"),
         ("Q02", "Wash-water and crude pumps", "POWER.c101", "C101.power", res["pumps"]["C101"], "flows x heads, efficiency 0.70, D-009"),
         ("Q03", "Catalyst circulation pump to the regenerator", "POWER.r101", "R101.power", res["pumps"]["R101"], "50 m3/h x 1000 kPa, efficiency 0.70, D-009"),
         ("Q04", "Reflux, product and waste-water pumps", "POWER.c202", "C202.power", res["pumps"]["C202"], "flows x heads, efficiency 0.70, D-009"),
         ("Q05", "E-101 precondenser duty", "E101.cw", "CW.e101", res["Q_E101"], "reactor energy balance, D-005"),
         ("Q06", "E-102 process gas cooler duty", "E102.cw", "CW.e102", res["Q_E102"], "383 K to 318 K with condensation, D-007"),
         ("Q07", "C-201 condenser duty", "C201.cond", "CW.c201", res["Q_C201"], "live-steam enthalpy balance, D-008"),
         ("Q08", "C-202 condenser duty", "C202.cond", "CW.c202", res["Q_C202"], "live-steam enthalpy balance, D-008"),
         ("Q09", "Heat recovered from the waste water to the crude", "E202.heat", "E201.heat", res["Q_rec"], "crude 313 K to 383 K, D-008"),
         ("Q10", "E-204 waste-water trim cooler duty", "E204.cw", "CW.e204", res["Q_E204"], "to 308 K, D-008"),
         ("Q11", "E-203 product cooler duty", "E203.cw", "CW.e203", res["Q_E203"], "323 K to 303 K, D-008")]
    f.write("  # Energy streams (scripts/acet_balance.py, D-006; ASSUMED until core qualifies them)\n")
    for qid, title, fr, to, v, src in Q:
        f.write(f"  - {{id: {qid}, title: {title}, kind: energy, from: {fr}, to: {to}, state: {{design: "
                f"{{duty: {{value: {v:.1f}, provenance: assumed, source: \"{SRC}: {src}\"}}}}}}}}\n")
print("wrote build/acet_streams.yaml")

# the values process/flowsheet.yaml cites from this script (balance-output contract): the
# stream table above, flow in kg/h and mass fractions
FLOWSHEET = {}
for sid, title, fr, to, tpl, p, t, dec, calc in STREAMS:
    s = {k: v for k, v in kgh[sid].items() if v > 1e-9}
    FLOWSHEET[sid] = {"flow": {"value": tot(s), "basis": "mass"},
                      "composition": {"values": {k: v / tot(s) for k, v in s.items()},
                                      "basis": "mass_fraction"},
                      "temperature": t, "pressure": p}
for qid, title, fr, to, v, src in Q:
    FLOWSHEET[qid] = {"duty": v}


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0024 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import json
    import os
    from pathlib import Path

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


write_balance_output({"design": FLOWSHEET})
