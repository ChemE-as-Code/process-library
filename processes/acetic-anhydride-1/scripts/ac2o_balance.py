"""Concept heat and material balance of acetic-anhydride-1 (ketene route), DESIGN.md D-006.

An independent balance: core cannot qualify flashes, enthalpies or distillation of acetic
acid / ketene / acetic anhydride / water (no property package), so the values the
flowsheet cannot calculate itself (separator and column outlets, recycle streams, utility
duties, the natural gas and air of the firebox) come from here and are entered in
process/flowsheet.yaml as ASSUMED with this script as their source. The reactor outlets,
mixers and pass-through steps are recalculated by `cheme process propagate --fill` from the
same specifications and must agree.

Run: cheme run scripts/ac2o_balance.py

Property data: formation enthalpies (gas: ATcT/CRC; liquid: CRC) and ideal-gas heat capacities
as in process/materials.yaml; liquid heat capacities, enthalpies of vaporisation and vapour
pressures from the `thermo` package correlations (Chemical(...)). Every design specification
below is ASSUMED unless a source is given, with the decision id of DESIGN.md.
"""

import math

from thermo import Chemical

R = 8.314462618e-3  # kJ/(mol K)

# --- components: molar mass, gas formation enthalpy (kJ/mol), cp/R polynomial ------------
MW = {"ACOH": 60.052, "KET": 42.037, "H2O": 18.015, "CH4": 16.042, "CO2": 44.01, "CO": 28.01,
      "C2H4": 28.053, "AC2O": 102.09, "DHA": 168.147, "TEP": 182.155, "NH3": 17.031,
      "N2": 28.013, "O2": 31.999}
HFG = {"ACOH": -432.2, "KET": -48.57, "H2O": -241.822, "CH4": -74.534, "CO2": -393.474,
       "CO": -110.525, "C2H4": 52.56, "AC2O": -572.5, "NH3": -45.558, "N2": 0.0, "O2": 0.0}
HFL = {"ACOH": -483.58, "H2O": -285.825, "AC2O": -624.4}  # liquid, CRC (via `chemicals`)
CPR = {
    "ACOH": [0.617879, 0.0260901, -7.3203e-06, -6.0082e-09, 3.35469e-12],
    "KET": [2.00116, 0.0191987, -2.03343e-05, 1.26482e-08, -3.32816e-12],
    "H2O": [4.07935, -0.00119698, 4.4192e-06, -3.25618e-09, 9.16685e-13],
    "CH4": [3.82014, -0.00391799, 2.43036e-05, -2.20853e-08, 6.63251e-12],
    "CO2": [2.18923, 0.0102771, -1.05204e-05, 6.1439e-09, -1.55652e-12],
    "CO": [3.86739, -0.00271111, 6.365e-06, -4.77973e-09, 1.24831e-12],
    "C2H4": [0.548804, 0.0170151, -4.93399e-06, -3.62204e-09, 2.27528e-12],
    "NH3": [3.524, 0.000891621, 7.5413e-06, -7.64226e-09, 2.47611e-12],
    "N2": [3.78431, -0.00197292, 4.22392e-06, -2.62309e-09, 5.21458e-13],
    "O2": [3.67977, -0.0022921, 8.11147e-06, -7.85653e-09, 2.55027e-12],
}
CAS = {"ACOH": "64-19-7", "H2O": "7732-18-5", "AC2O": "108-24-7", "DHA": "520-45-6",
       "TEP": "78-40-0"}


def dh_ig(c, t1, t2):
    """Ideal-gas enthalpy change kJ/mol from t1 to t2."""
    a = CPR[c]
    f = lambda t: sum(a[i] * t ** (i + 1) / (i + 1) for i in range(5))
    return R * (f(t2) - f(t1))


_chem = {}


def chem(c):
    if c not in _chem:
        _chem[c] = Chemical(CAS[c])
    return _chem[c]


def cpl(c, t):
    """Liquid molar heat capacity kJ/(mol K) at t (thermo correlation)."""
    ch = chem(c)
    ch.calculate(T=t, P=101325)
    return ch.Cplm / 1000.0


def hvap(c, t):
    """Enthalpy of vaporisation kJ/mol at t (thermo correlation; acetic acid: to the
    associated real vapour, about 24 kJ/mol, not to the ideal monomer gas)."""
    ch = chem(c)
    ch.calculate(T=t, P=101325)
    return ch.Hvap * ch.MW / 1e6


def h_liq(n, t):
    """Enthalpy of a liquid (kmol/h dict) at t, kW, formation basis (DHA, TEP, NH3 sensible
    only: they pass through non-reactive steps, where their formation terms cancel)."""
    h = 0.0
    for c, x in n.items():
        if x == 0:
            continue
        hf = HFL.get(c, 0.0)
        if c == "NH3":  # dissolved as ammonium salt; sensible only (tiny)
            h += x * hf
            continue
        tm = 0.5 * (298.15 + t)
        h += x * (hf + cpl(c, tm) * (t - 298.15))
    return h * 1000 / 3600


def h_gas(n, t):
    """Enthalpy of an ideal gas (kmol/h dict) at t, kW, formation basis."""
    return sum(x * (HFG[c] + dh_ig(c, 298.15, t)) for c, x in n.items() if x) * 1000 / 3600


def kg(n):
    return {c: x * MW[c] for c, x in n.items()}


def tot(d):
    return sum(d.values())


# --- design basis -------------------------------------------------------------------------
PRODUCT_KG_H = 50_000_000 / 8000            # D-002: 50 kt/a at 8000 h/a, ASSUMED
W_AC2O_PRODUCT = 0.995                       # D-002: product 99.5 wt% Ac2O, rest acetic acid
X_CRACK = 0.84                               # US 4,455,439 example: 84 % conversion
S_KET = 0.92                                 # US 4,455,439 example: 92 % ketene on acid reacted
S_CH4 = 0.04                                 # D-005: half the 8 % loss to CH4 + CO2, ASSUMED
X_ABS = 0.99                                 # D-007: 1 % of the ketene leaves with the vent, ASSUMED
S_AC2O = 0.99                                # D-007: 1 % of the absorbed ketene to heavies, ASSUMED
W_TEP = 0.002                                # D-005: 0.2 wt% TEP in the cracker feed (US 8,653,303: 0.1-0.5 wt%)
NH3_PER_P = 2.0                              # D-005: 2 mol NH3 per mol P, ASSUMED
W_AC2O_CRUDE = 0.88                          # D-007: crude 88 wt% Ac2O (US 8,653,303: >= 85 wt% preferred)
W_ACOH_TOP201 = 0.98                         # D-008: acid column distillate 98 wt% acid, ASSUMED
W_AC2O_RESIDUE = 0.50                        # D-008: residue 50 wt% Ac2O / 50 wt% heavies, ASSUMED
REC_ARU = 0.99                               # D-009: 99 % of the dilute acid's acid recovered, ASSUMED
W_ACOH_REC = 0.998                           # D-009: recovered acid 99.8 wt%, ASSUMED
Q_ARU_PER_KG_WATER = 3.0                     # D-009: MJ LP steam per kg water in the dilute acid, ASSUMED
BRINE_COND_FRACTION = 0.20                   # D-006: share of the condensate condensed on brine (estimate)
EXCESS_O2 = 0.15                             # D-010: 15 % excess air, ASSUMED
T_STACK = 443.15                             # D-010: flue gas after the convection section, ASSUMED
RADIATION_LOSS = 0.02                        # D-010: of the fired LHV, ASSUMED
R201, R202 = 3.0, 1.0                        # D-008: reflux ratios, ASSUMED

T = dict(feed=303.15, vap=367.0, crack=973.15, cond=268.15, cw_out=308.15, abs=318.15,
         vent_k=333.15, top201=391.0, bot201=413.0, top202=413.0, bot202=450.0, prod=313.15,
         rec=318.15, ww=313.15, air=298.15)

# --- solve the product side backwards -----------------------------------------------------
P_ac2o = PRODUCT_KG_H * W_AC2O_PRODUCT / MW["AC2O"]
P_acoh = PRODUCT_KG_H * (1 - W_AC2O_PRODUCT) / MW["ACOH"]
# ketene to the absorber K: Ac2O formed = X_ABS*S_AC2O*K = product + residue Ac2O,
# DHA = X_ABS*(1-S_AC2O)/4*K, residue Ac2O mass = DHA mass * w/(1-w)
dha_per_k = X_ABS * (1 - S_AC2O) / 4
res_ac2o_per_k = dha_per_k * MW["DHA"] * W_AC2O_RESIDUE / (1 - W_AC2O_RESIDUE) / MW["AC2O"]
K = P_ac2o / (X_ABS * S_AC2O - res_ac2o_per_k)
F_crack = K / (X_CRACK * S_KET)               # acetic acid fed to the cracker, kmol/h

xi1 = X_CRACK * (1 - S_CH4) * F_crack         # AcOH -> KET + H2O
xi2 = X_CRACK * S_CH4 * F_crack               # AcOH -> CH4 + CO2
xi3 = (xi1 - K) / 2                           # 2 KET -> C2H4 + 2 CO

# --- cracker loop with the recovered-acid recycle (water passes through) ------------------
water_rec = 0.0
for _ in range(50):
    acoh_dil = F_crack * (1 - X_CRACK)
    rec_acoh = REC_ARU * acoh_dil
    rec_h2o_new = rec_acoh * MW["ACOH"] * (1 - W_ACOH_REC) / W_ACOH_REC / MW["H2O"]
    if abs(rec_h2o_new - water_rec) < 1e-10:
        break
    water_rec = rec_h2o_new
fresh_crack = F_crack - rec_acoh
S5_noTEP = {"ACOH": F_crack, "H2O": water_rec}
tep = W_TEP * tot(kg(S5_noTEP)) / (1 - W_TEP) / MW["TEP"]
nh3 = NH3_PER_P * tep

S5 = {"ACOH": F_crack, "H2O": water_rec, "TEP": tep}
S7 = {"ACOH": F_crack - xi1 - xi2, "KET": K, "H2O": water_rec + xi1, "CH4": xi2,
      "CO2": xi2, "C2H4": xi3, "CO": 2 * xi3, "TEP": tep}
S9 = dict(S7, NH3=nh3)
S11 = {"KET": K, "CH4": xi2, "CO2": xi2, "C2H4": xi3, "CO": 2 * xi3}      # dry ketene gas
S12 = {"ACOH": S7["ACOH"], "H2O": S7["H2O"], "TEP": tep, "NH3": nh3}     # dilute acid
S21 = {"ACOH": rec_acoh, "H2O": water_rec}
S22 = {"ACOH": S12["ACOH"] - rec_acoh, "H2O": S12["H2O"] - water_rec, "TEP": tep, "NH3": nh3}

# --- absorber and distillation ------------------------------------------------------------
ac2o_formed = X_ABS * S_AC2O * K
dha = dha_per_k * K
res_ac2o = res_ac2o_per_k * K
acoh_consumed = ac2o_formed
# crude: Ac2O = P + residue + recycle Ac2O; AcOH = product AcOH + recycle AcOH; DHA
# recycle distillate D (kg/h) with W_ACOH_TOP201 acid: solve the crude Ac2O fraction
a = (P_ac2o + res_ac2o) * MW["AC2O"]
b = P_acoh * MW["ACOH"] + dha * MW["DHA"]
D201 = (a - W_AC2O_CRUDE * (a + b)) / (W_AC2O_CRUDE - (1 - W_ACOH_TOP201))
S25 = {"ACOH": D201 * W_ACOH_TOP201 / MW["ACOH"], "AC2O": D201 * (1 - W_ACOH_TOP201) / MW["AC2O"]}
S16 = {"AC2O": P_ac2o + res_ac2o + S25["AC2O"], "ACOH": P_acoh + S25["ACOH"], "DHA": dha}
S15 = {"KET": K * (1 - X_ABS), "CH4": xi2, "CO2": xi2, "C2H4": xi3, "CO": 2 * xi3}
fresh_abs = acoh_consumed + P_acoh                 # net acid taken up by the absorber
S3 = {"ACOH": fresh_abs}
S1 = {"ACOH": fresh_crack + fresh_abs}
S18 = {"AC2O": P_ac2o + res_ac2o, "ACOH": P_acoh, "DHA": dha}
S19 = {"AC2O": P_ac2o, "ACOH": P_acoh}
S20 = {"AC2O": res_ac2o, "DHA": dha}

# --- energy -------------------------------------------------------------------------------
n_crack_liq = {"ACOH": F_crack, "H2O": water_rec}
# vaporiser E101: liquid at 303 K (fresh and recovered acid mixed, ASSUMED) to saturated
# associated vapour at 367 K (acetic acid saturation near 45 kPa)
tm = 0.5 * (T["feed"] + T["vap"])
Q_E101 = sum(x * (cpl(c, tm) * (T["vap"] - T["feed"]) + hvap(c, T["vap"]))
             for c, x in n_crack_liq.items()) * 1000 / 3600
H_S5 = h_liq(n_crack_liq, T["feed"])
H_S6 = H_S5 + Q_E101
H_S7 = h_gas({c: x for c, x in S7.items() if c != "TEP"}, T["crack"])
Q_R101 = H_S7 - H_S6                       # fired duty absorbed by the cracking coil
# condenser train E102: cracked gas + NH3 at 973 K to ketene gas and dilute acid at 268 K
H_S9 = H_S7 + h_gas({"NH3": nh3}, 298.15)
H_S11 = h_gas(S11, T["cond"])
H_S12 = h_liq({c: x for c, x in S12.items()}, T["cond"])
Q_E102 = H_S9 - H_S11 - H_S12
cond_latent = sum(S12[c] * (HFG[c] - HFL[c]) for c in ("ACOH", "H2O")) * 1000 / 3600
Q_brine = (BRINE_COND_FRACTION * cond_latent
           + h_gas(S11, T["cw_out"]) - H_S11
           + h_liq({c: S12[c] for c in ("ACOH", "H2O")}, T["cw_out"])
           - h_liq({c: S12[c] for c in ("ACOH", "H2O")}, T["cond"]))
Q_E102_cw = Q_E102 - Q_brine
# absorber T301: ketene gas 268 K + acids 303/318 K -> crude 318 K + vent 318 K
H_in301 = H_S11 + h_liq(S3, T["feed"]) + h_liq(S25, T["rec"])
H_out301 = h_liq(S16, T["abs"]) + h_gas(S15, T["abs"])
Q_T301 = H_in301 - H_out301                # to cooling water (heavies' formation heat neglected)
# vent compressor K301: liquid-ring, about isothermal, 25 -> 120 kPa(a), efficiency 0.35 ASSUMED
P_K301 = tot(S15) / 3600 * R * 1000 * T["abs"] * math.log(120 / 25) / 0.35
# absorber circulation: 100 kg per kg ketene (US 8,653,303), 300 kPa, 1050 kg/m3, eff. 0.65
m_circ = 100 * K * MW["KET"]
P_P301 = m_circ / 3600 / 1050 * 300 / 0.65
# acid column C201: feed S16 at 318 K, distillate S25 to 318 K (subcooled), bottoms 413 K
L201 = (R201 + 1) * (S25["ACOH"] * hvap("ACOH", T["top201"]) + S25["AC2O"] * hvap("AC2O", T["top201"])) * 1000 / 3600
H_F201 = h_liq(S16, T["abs"])
H_D201 = h_liq(S25, T["rec"])
H_B201 = h_liq(S18, T["bot201"])
Q_C201_reb = L201 + h_liq(S25, T["top201"]) + H_B201 - H_F201
Q_C201_cw = Q_C201_reb + H_F201 - H_D201 - H_B201
# anhydride column C202: product overhead, cooled to 313 K; residue 450 K
L202 = (R202 + 1) * (S19["AC2O"] * hvap("AC2O", T["top202"]) + S19["ACOH"] * hvap("ACOH", T["top202"])) * 1000 / 3600
H_F202 = H_B201
H_D202 = h_liq(S19, T["prod"])
H_B202 = h_liq(S20, T["bot202"])
Q_C202_reb = L202 + h_liq(S19, T["top202"]) + H_B202 - H_F202
Q_C202_cw = Q_C202_reb + H_F202 - H_D202 - H_B202
# dilute acid recovery C401 (extraction + azeotropic dehydration, lumped): ASSUMED specific duty
Q_C401 = Q_ARU_PER_KG_WATER * S12["H2O"] * MW["H2O"] / 3.6
Q_C401_cw = Q_C401 + h_liq(S12, T["cond"]) - h_liq(S21, T["feed"]) - h_liq(S22, T["ww"])

# --- firebox H101: natural gas (as methane, ASSUMED) + vent + air ------------------------
O2_COMB = {"CH4": 2.0, "CO": 0.5, "C2H4": 3.0, "KET": 2.0, "CO2": 0.0}
CO2_COMB = {"CH4": 1, "CO": 1, "C2H4": 2, "KET": 2}
H2O_COMB = {"CH4": 2, "CO": 0, "C2H4": 2, "KET": 1}
S17 = dict(S15)


def firebox(ng):
    fuel = dict(S17)
    fuel["CH4"] = fuel.get("CH4", 0) + ng
    o2 = sum(O2_COMB[c] * x for c, x in fuel.items()) * (1 + EXCESS_O2)
    n2 = o2 * 0.79 / 0.21
    flue = {"CO2": fuel["CO2"] + sum(CO2_COMB[c] * x for c, x in fuel.items() if c != "CO2"),
            "H2O": sum(H2O_COMB[c] * x for c, x in fuel.items() if c != "CO2"),
            "N2": n2, "O2": o2 - o2 / (1 + EXCESS_O2)}
    lhv = sum(x * (HFG[c] - CO2_COMB[c] * HFG["CO2"] - H2O_COMB[c] * HFG["H2O"])
              for c, x in fuel.items() if c != "CO2") * 1000 / 3600
    h_in = h_gas(S17, T["vent_k"]) + h_gas({"CH4": ng}, T["feed"]) + h_gas({"O2": o2, "N2": n2}, T["air"])
    h_out = h_gas(flue, T_STACK)
    q_avail = h_in - h_out - RADIATION_LOSS * lhv
    return q_avail, flue, o2, n2, lhv


lo, hi = 0.0, 200.0
for _ in range(200):
    mid = 0.5 * (lo + hi)
    if firebox(mid)[0] < Q_R101:
        lo = mid
    else:
        hi = mid
NG = 0.5 * (lo + hi)
q_fb, FLUE, O2A, N2A, LHV_FIRED = firebox(NG)
AIR = {"N2": N2A, "O2": O2A}
NGs = {"CH4": NG}


def show(name, n, t, p, phase):
    m = kg(n)
    mt = tot(m)
    nt = tot(n)
    xs = ", ".join(f"{c}: {x / nt:.6f}" for c, x in n.items() if x > 0)
    print(f"{name}: {mt:10.2f} kg/h {nt:9.4f} kmol/h  T {t:.2f} K  P {p} kPa  {phase}\n    mole {{{xs}}}")


print(f"cracker acid feed {F_crack:.4f} kmol/h, ketene {K:.4f} kmol/h, fresh acid to cracker split "
      f"{fresh_crack / tot(S1):.6f}")
print(f"extents R1 {xi1:.4f} R2 {xi2:.4f} R3 {xi3:.4f}; absorber A1 {ac2o_formed:.4f} A2 {dha:.5f}")
streams = [
    ("S1 fresh acid", S1, T["feed"], 300, "liquid"),
    ("S2 to cracker", {"ACOH": fresh_crack}, T["feed"], 300, "liquid"),
    ("S3 to absorber", S3, T["feed"], 300, "liquid"),
    ("S4 TEP", {"TEP": tep}, T["feed"], 300, "liquid"),
    ("S5 cracker feed", S5, T["feed"], 300, "liquid"),
    ("S6 vapour", S5, T["vap"], 45, "vapor"),
    ("S7 cracked gas", S7, T["crack"], 36, "vapor"),
    ("S8 NH3", {"NH3": nh3}, 298.15, 300, "vapor"),
    ("S9 + NH3", S9, 960.0, 35.8, "vapor"),
    ("S10 cooled", S9, T["cond"], 27, "two-phase"),
    ("S11 ketene gas", S11, T["cond"], 27, "vapor"),
    ("S12 dilute acid", S12, T["cond"], 27, "liquid"),
    ("S13 absorber feed", {**S11, "ACOH": S3["ACOH"] + S25["ACOH"], "AC2O": S25["AC2O"]}, 300.0, 27, "two-phase"),
    ("S15 vent", S15, T["abs"], 25, "vapor"),
    ("S16 crude", S16, T["abs"], 25, "liquid"),
    ("S17 vent compressed", S17, T["vent_k"], 120, "vapor"),
    ("S18 C201 bottoms", S18, T["bot201"], 110, "liquid"),
    ("S19 product", S19, T["prod"], 300, "liquid"),
    ("S20 residue", S20, T["bot202"], 120, "liquid"),
    ("S21 recovered acid", S21, T["feed"], 300, "liquid"),
    ("S22 wastewater", S22, T["ww"], 300, "liquid"),
    ("S25 acid recycle", S25, T["rec"], 300, "liquid"),
    ("S30 natural gas", NGs, T["feed"], 300, "vapor"),
    ("S31 air", AIR, T["air"], 103, "vapor"),
    ("S32 flue gas", FLUE, T_STACK, 101.3, "vapor"),
]
for s in streams:
    show(*s)
print("duties kW:")
duties = dict(E101_LPS=Q_E101, R101_fired=Q_R101, E102_CW=Q_E102_cw, E102_BRINE=Q_brine,
              T301_CW=Q_T301, T301_POWER=P_P301, K301_POWER=P_K301, C201_MPS=Q_C201_reb,
              C201_CW=Q_C201_cw, C202_MPS=Q_C202_reb, C202_CW=Q_C202_cw, C401_LPS=Q_C401,
              C401_CW=Q_C401_cw)
for k, v in duties.items():
    print(f"  {k}: {v:.1f}")
print(f"firebox: fired LHV {LHV_FIRED:.1f} kW (vent share {(LHV_FIRED - NG * 802.584 / 3.6) / LHV_FIRED:.3f}), "
      f"absorbed {q_fb:.1f} kW, efficiency (LHV) {q_fb / LHV_FIRED:.3f}")
m_in = tot(kg(S1)) + tot(kg({"TEP": tep})) + tot(kg({"NH3": nh3})) + tot(kg(NGs)) + tot(kg(AIR))
m_out = tot(kg(S19)) + tot(kg(S20)) + tot(kg(S22)) + tot(kg(FLUE))
print(f"overall mass in {m_in:.2f} out {m_out:.2f} kg/h")
print(f"specific: acid {tot(kg(S1)) / PRODUCT_KG_H:.4f} kg/kg, NG {tot(kg(NGs)) / PRODUCT_KG_H:.4f} kg/kg, "
      f"yield on acid {2 * P_ac2o / S1['ACOH']:.4f} mol/mol (Ac2O product x 2 / acid)")
