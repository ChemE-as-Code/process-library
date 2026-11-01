"""Concept heat and material balance of the sulfur-burning double-contact plant (sulfuric-acid-1).

Provenance script (DESIGN.md D-006): computes the values that cheme process propagate cannot
(separator outlets of the drying and absorption towers, adiabatic bed and furnace outlet
temperatures, tower acid circulation, exchanger duties, blower and pump power). Its results are
entered in process/flowsheet.yaml as `assumed` with source "scripts/balance.py (D-006)"; the
flows and compositions through the furnace, the beds, the exchangers, the mixer and the
splitter are then recalculated by `cheme process propagate --fill` and must agree.

Run: cheme run scripts/balance.py   (CoolProp for the steam enthalpies; nothing is written)

Every input marked ASSUMED is a design choice of this concept study (design basis, DESIGN.md).
Gas enthalpies: ideal gas, the Cp/R polynomials and formation enthalpies of process/materials.yaml
(chemicals/thermo: Poling 5th ed., CRC), valid to 1000 K; the furnace outlet (about 1400 K) is an
extrapolation, flagged. Liquids: standard enthalpies of formation of H2SO4(l) and H2O(l) (NBS
tables, Wagman et al. 1982) and a constant heat capacity; heat of mixing of water into
98.5-99.5 wt% acid neglected (ASSUMED, a few % of the absorption heat).
"""

import CoolProp.CoolProp as CP

R = 8.314462618e-3  # kJ/(mol K) -> kJ/(kmol K) * 1e-3; used as kJ/(kmol K) below with *1000
R_KJ_KMOL = 8.314462618  # kJ/(kmol K)
T0 = 298.15

# --- components (molar mass kg/kmol; ideal-gas dHf kJ/kmol; Cp/R polynomial) -----------------
MW = {"N2": 28.013, "O2": 31.999, "AR": 39.948, "H2O": 18.015, "SO2": 64.064, "SO3": 80.063,
      "S": 32.065, "H2SO4": 98.078}
HF_GAS = {"N2": 0.0, "O2": 0.0, "AR": 0.0, "H2O": -241822.0, "SO2": -296800.0, "SO3": -395700.0}
CPR = {
    "N2": [3.539, -0.000261, 7e-08, 1.57e-09, -9.9e-13],
    "O2": [3.63, -0.001794, 6.58e-06, -6e-09, 1.79e-12],
    "AR": [2.5],
    "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
    "SO2": [4.417, -0.002234, 2.344e-05, -3.271e-08, 1.393e-11],
    "SO3": [3.426, 0.006479, 1.691e-05, -3.356e-08, 1.59e-11],
}
# liquids, kJ/kmol at 298.15 K (NBS tables, Wagman et al. 1982)
HF_LIQ = {"H2SO4": -813990.0, "H2O": -285830.0}
# liquid sulfur: S(rhombic) = 0 at 298.15 K; fusion 1.721 kJ/mol (thermo); Cp(l) ~ 31 kJ/(kmol K)
# averaged to the feed temperature (ASSUMED, including the solid-solid transition, small)
H_S_FEED = 1721.0 + 31.0 * (413.15 - T0)  # kJ/kmol at 413.15 K
CP_ACID = 1.45   # kJ/(kg K), 98-99.5 wt% acid, ASSUMED constant
CP_WATER = 4.18  # kJ/(kg K)


def h_gas(c, T):
    """Ideal-gas molar enthalpy, kJ/kmol, formation basis at 298.15 K."""
    a = CPR[c]
    integ = sum(a[i] / (i + 1) * (T ** (i + 1) - T0 ** (i + 1)) for i in range(len(a)))
    return HF_GAS[c] + R_KJ_KMOL * integ


def H_gas(n, T):
    return sum(v * h_gas(c, T) for c, v in n.items())


def T_from_H(n, H, guess=600.0):
    T = guess
    for _ in range(100):
        f = H_gas(n, T) - H
        cp = (H_gas(n, T + 0.5) - H_gas(n, T - 0.5))
        T -= f / cp
        if abs(f) < 1e-3:
            break
    return T


def H_liq(m_h2so4, m_h2o, T):
    """Liquid acid (or water) enthalpy, kJ/h; mass flows kg/h."""
    n_a, n_w = m_h2so4 / MW["H2SO4"], m_h2o / MW["H2O"]
    cp = CP_WATER if m_h2so4 == 0 else CP_ACID
    return n_a * HF_LIQ["H2SO4"] + n_w * HF_LIQ["H2O"] + (m_h2so4 + m_h2o) * cp * (T - T0)


def mass(n):
    return sum(v * MW[c] for c, v in n.items())


def frac(n):
    t = sum(n.values())
    return {c: v / t for c, v in n.items() if v > 0}


# --- design basis (process/design-basis.yaml) -------------------------------------------------
H2SO4_T_PER_D = 1000.0          # ASSUMED (D-002), 100 % H2SO4 basis
W_PRODUCT = 0.985               # product strength, wt% H2SO4 (case brief)
SO2_FURNACE = 0.115             # ASSUMED (D-004), burner gas SO2, mol fraction (dry gas)
X_CUM = [0.63, 0.87, 0.95]      # cumulative SO2 conversion after beds 1-3 (D-005, Speight ranges)
X_OVERALL = 0.997               # overall, double absorption (D-005, Speight)
ABS_IPA = 0.999                 # SO3 absorbed in the intermediate tower, ASSUMED (D-007)
ABS_FAT = 0.999                 # SO3 absorbed in the final tower, ASSUMED (D-007)
T_AMB, RH = 298.15, 0.60        # ASSUMED site air
P_AMB = 101.325
DRY_AIR = {"N2": 0.7812, "O2": 0.2095, "AR": 0.0093}  # CO2 lumped into N2 (D-004)
T_S = 413.15                    # molten sulfur feed, ASSUMED
T_ACID_IN = 343.15              # acid to all towers, ASSUMED (one header, D-007)
T_GAS_TOWER_OUT = 348.15        # gas leaving every tower, ASSUMED
# ASSUMED acid outlet temperatures; the drying tower's acid leaves cooler than it enters: heating
# the air to 348 K takes more than the condensation of its moisture gives (heat of dilution
# neglected, which understates the heat into the drying acid)
T_ACID_OUT = {"DT": 338.15, "IPA": 383.15, "FAT": 363.15}
T_PRODUCT = 313.15              # product to storage, ASSUMED
T_PW = 298.15                   # process water
# bed inlet temperatures, ASSUMED (D-005); bed 1 at 688 K keeps its outlet inside the catalyst
# window of process/catalysts.yaml (903 K)
T_BED_IN = [688.15, 713.15, 708.15, 683.15]
T_IPA_IN, T_FAT_IN = 453.15, 443.15           # gas to the towers, ASSUMED
P_BLOWER_OUT = 160.0
ETA_BLOWER, ETA_MOTOR = 0.80, 0.96            # ASSUMED
PUMP_HEAD_M, ETA_PUMP, RHO_ACID = 35.0, 0.70, 1830.0  # ASSUMED
STEAM_P, STEAM_T = 4.1e6, 673.15              # HP steam export, ASSUMED (D-008)
BFW_P, BFW_T = 4.6e6, 378.15                  # boiler feed water at the battery limit, ASSUMED

# --- production and feeds ---------------------------------------------------------------------
n_prod = H2SO4_T_PER_D * 1000 / 24 / MW["H2SO4"]   # kmol/h H2SO4 in the product
# S converted to SO3 and absorbed: overall conversion and both towers' slips
# SO3 leaving to the stack = (1-ABS_FAT) * SO3 into FAT; IPA slip passes bed 4 to the FAT.
# Solve for the sulfur feed n_S so that absorbed SO3 = n_prod.
def absorbed(nS):
    so3_3 = nS * X_CUM[2]
    a_ipa = ABS_IPA * so3_3
    so3_fat = so3_3 - a_ipa + nS * (X_OVERALL - X_CUM[2])
    a_fat = ABS_FAT * so3_fat
    return a_ipa + a_fat


n_S = n_prod / absorbed(1.0)
n_dry = n_S / SO2_FURNACE                     # SO2 fraction = S burned / dry air (1:1 O2:SO2)
psat = CP.PropsSI("P", "T", T_AMB, "Q", 0, "Water") / 1000
y_w = RH * psat / P_AMB
n_air = {c: n_dry * f for c, f in DRY_AIR.items()}
n_air["H2O"] = n_dry * y_w / (1 - y_w)

# --- drying tower and blower ------------------------------------------------------------------
dry = {c: v for c, v in n_air.items() if c != "H2O"}
w_abs_dt = n_air["H2O"] * MW["H2O"]
# blower: isentropic on dry air from the drying tower outlet
P_DT_OUT = 98.0
k = None
cp_mix = (H_gas(dry, T_GAS_TOWER_OUT + 0.5) - H_gas(dry, T_GAS_TOWER_OUT - 0.5)) / sum(dry.values())
kappa = cp_mix / (cp_mix - R_KJ_KMOL)
T2s = T_GAS_TOWER_OUT * (P_BLOWER_OUT / P_DT_OUT) ** ((kappa - 1) / kappa)
dH_s = H_gas(dry, T2s) - H_gas(dry, T_GAS_TOWER_OUT)
dH = dH_s / ETA_BLOWER
T_blow = T_from_H(dry, H_gas(dry, T_GAS_TOWER_OUT) + dH, 400)
W_blower = dH / 3600 / ETA_MOTOR             # kW electric

# --- furnace ------------------------------------------------------------------------------------
g5 = dict(dry)
g5["O2"] -= n_S
g5["SO2"] = n_S
H_in = H_gas(dry, T_blow) + n_S * H_S_FEED
T_furn = T_from_H(g5, H_in, 1300)
Q_whb = H_gas(g5, T_furn) - H_gas(g5, T_BED_IN[0])

# --- converter ------------------------------------------------------------------------------------
def bed(g, x, Tin):
    g = dict(g)
    r = x * g["SO2"]
    g["SO2"] -= r
    g["O2"] -= r / 2
    g["SO3"] = g.get("SO3", 0) + r
    T = T_from_H(g, H_gas({**g, "SO2": g["SO2"] + r, "O2": g["O2"] + r / 2, "SO3": g["SO3"] - r}, Tin), Tin + 100)
    return g, T, r


x1 = X_CUM[0]
x2 = (X_CUM[1] - X_CUM[0]) / (1 - X_CUM[0])
x3 = (X_CUM[2] - X_CUM[1]) / (1 - X_CUM[1])
x4 = (X_OVERALL - X_CUM[2]) / (1 - X_CUM[2])
g7, T7, r1 = bed(g5, x1, T_BED_IN[0])
g9, T9, r2 = bed(g7, x2, T_BED_IN[1])
g11, T11, r3 = bed(g9, x3, T_BED_IN[2])
Q_hot_hot = H_gas(g7, T7) - H_gas(g7, T_BED_IN[1])    # E-201 hot side
Q_sh = H_gas(g9, T9) - H_gas(g9, T_BED_IN[2])         # E-202 superheater

# --- intermediate absorption tower ----------------------------------------------------------------
a_ipa = ABS_IPA * g11["SO3"]
g14 = dict(g11)
g14["SO3"] -= a_ipa
# reheat of the IPA gas: E-203 (cold) then E-201 (hot)
Q_reheat = H_gas(g14, T_BED_IN[3]) - H_gas(g14, T_GAS_TOWER_OUT)
Q_cold = Q_reheat - Q_hot_hot
T15 = T_from_H(g14, H_gas(g14, T_GAS_TOWER_OUT) + Q_cold, 500)
T12 = T_from_H(g11, H_gas(g11, T11) - Q_cold, 550)
Q_eco1 = H_gas(g11, T12) - H_gas(g11, T_IPA_IN)
g16 = g14
g17, T17, r4 = bed(g16, x4, T_BED_IN[3])
Q_eco2 = H_gas(g17, T17) - H_gas(g17, T_FAT_IN)
a_fat = ABS_FAT * g17["SO3"]
g19 = dict(g17)
g19["SO3"] -= a_fat

# --- acid system ----------------------------------------------------------------------------------
def tower_acid(gas_in, T_gin, gas_out, so3_abs, h2o_abs, T_aout, w_in=W_PRODUCT):
    """Circulation (kg/h) from the tower energy balance; returns (m_in, m_out, w_out)."""
    # heat released into the acid per kg circulation: acid in at T_ACID_IN, out at T_aout.
    # Unknown m: H_gas_in + H_acid_in(m) + absorbed-from-gas = H_gas_out + H_acid_out(m)
    def resid(m):
        a_in, w_in_ = m * w_in, m * (1 - w_in)
        a_out = a_in + so3_abs * MW["H2SO4"]
        w_out = w_in_ + h2o_abs * MW["H2O"] - so3_abs * MW["H2O"]
        return (H_gas(gas_in, T_gin) + H_liq(a_in, w_in_, T_ACID_IN)
                - H_gas(gas_out, T_GAS_TOWER_OUT) - H_liq(a_out, w_out, T_aout))
    m = 1e5
    for _ in range(50):
        f = resid(m)
        d = (resid(m * 1.001) - f) / (m * 0.001)
        m -= f / d
        if abs(f) < 1e-2:
            break
    a_in, w_in_ = m * w_in, m * (1 - w_in)
    a_out = a_in + so3_abs * MW["H2SO4"]
    w_out = w_in_ + h2o_abs * MW["H2O"] - so3_abs * MW["H2O"]
    return m, a_out, w_out


m_dt, a_dt, w_dt = tower_acid(n_air, T_AMB, dry, 0.0, n_air["H2O"], T_ACID_OUT["DT"])
m_ipa, a_ipa_out, w_ipa = tower_acid(g11, T_IPA_IN, g14, a_ipa, 0.0, T_ACID_OUT["IPA"])
m_fat, a_fat_out, w_fat = tower_acid(g17, T_FAT_IN, g19, a_fat, 0.0, T_ACID_OUT["FAT"])

m_prod_acid = n_prod * MW["H2SO4"]
m_prod = m_prod_acid / W_PRODUCT
m_prod_w = m_prod - m_prod_acid
# water make-up: H2O in product + H2O reacted - H2O absorbed from air
m_pw = m_prod_w + (a_ipa + a_fat) * MW["H2O"] - n_air["H2O"] * MW["H2O"]
# pump tank: returns + water -> circulation = m_dt + m_ipa + m_fat + m_prod
A_ret = a_dt + a_ipa_out + a_fat_out
W_ret = w_dt + w_ipa + w_fat + m_pw
m_circ = A_ret + W_ret
H_tank_in = (H_liq(a_dt, w_dt, T_ACID_OUT["DT"]) + H_liq(a_ipa_out, w_ipa, T_ACID_OUT["IPA"])
             + H_liq(a_fat_out, w_fat, T_ACID_OUT["FAT"]) + H_liq(0, m_pw, T_PW))
# tank temperature (mixing, heat of dilution neglected)
T_tank = T0 + (H_tank_in - H_liq(A_ret, W_ret, T0)) / (m_circ * CP_ACID)
W_pump = m_circ / RHO_ACID / 3600 * RHO_ACID * 9.81 * PUMP_HEAD_M / ETA_PUMP / 1000 / ETA_MOTOR
Q_acid_cooler = H_liq(A_ret, W_ret, T_tank) - H_liq(A_ret, W_ret, T_ACID_IN)
Q_prod_cooler = m_prod * CP_ACID * (T_ACID_IN - T_PRODUCT)

# --- steam ------------------------------------------------------------------------------------------
h_s = CP.PropsSI("H", "T", STEAM_T, "P", STEAM_P, "Water") / 1000
h_bfw = CP.PropsSI("H", "T", BFW_T, "P", BFW_P, "Water") / 1000
Q_steam = Q_whb + Q_sh + Q_eco1 + Q_eco2
m_steam = Q_steam / (h_s - h_bfw)

# --- report -----------------------------------------------------------------------------------------
kW = lambda q: q / 3600
print(f"H2SO4 {n_prod:.3f} kmol/h = {m_prod_acid:.1f} kg/h; product 98.5 wt% {m_prod:.1f} kg/h")
print(f"sulfur {n_S:.4f} kmol/h = {n_S*MW['S']:.2f} kg/h; dry air {n_dry:.3f} kmol/h, water in air {n_air['H2O']:.4f} kmol/h (y={y_w:.5f})")
print(f"air total {mass(n_air):.1f} kg/h  frac {frac(n_air)}")
print(f"blower: T_out {T_blow:.2f} K, kappa {kappa:.4f}, power {W_blower:.1f} kW")
print(f"furnace out {T_furn:.1f} K (Cp/R extrapolated above 1000 K), WHB duty {kW(Q_whb):.1f} kW")
for i, (g, T, x) in enumerate([(g7, T7, x1), (g9, T9, x2), (g11, T11, x3), (g17, T17, x4)], 1):
    print(f"bed {i}: conversion {x:.6f} of inlet SO2, outlet {T:.2f} K, SO2 {g['SO2']:.4f} SO3 {g['SO3']:.4f} kmol/h")
print(f"E-201 hot interpass {kW(Q_hot_hot):.1f} kW; E-202 superheater {kW(Q_sh):.1f} kW; E-203 cold interpass {kW(Q_cold):.1f} kW")
print(f"E-203 hot out T12 {T12:.2f} K; cold out T15 {T15:.2f} K; E-204 eco1 {kW(Q_eco1):.1f} kW; E-205 eco2 {kW(Q_eco2):.1f} kW")
print(f"IPA absorbs {a_ipa:.4f} kmol/h SO3, FAT {a_fat:.4f}; stack SO2 {g19['SO2']:.4f} SO3 {g19['SO3']:.5f} kmol/h")
print(f"stack {mass(g19):.1f} kg/h frac {frac(g19)}")
for name, m, a, w in [("DT", m_dt, a_dt, w_dt), ("IPA", m_ipa, a_ipa_out, w_ipa), ("FAT", m_fat, a_fat_out, w_fat)]:
    print(f"{name}: acid in {m:.1f} kg/h; out {a+w:.1f} kg/h, H2SO4 {a/(a+w):.6f}")
print(f"process water {m_pw:.2f} kg/h; tank mix {m_circ:.1f} kg/h at {T_tank:.2f} K, w {A_ret/m_circ:.6f}")
print(f"splits of circulation: DT {m_dt/m_circ:.8f} IPA {m_ipa/m_circ:.8f} FAT {m_fat/m_circ:.8f} PROD {m_prod/m_circ:.8f}")
print(f"acid pump {W_pump:.1f} kW; acid cooler {kW(Q_acid_cooler):.1f} kW; product cooler {kW(Q_prod_cooler):.1f} kW")
print(f"steam: gross heat {kW(Q_steam):.1f} kW, h_s {h_s:.1f} h_bfw {h_bfw:.1f} kJ/kg -> {m_steam:.1f} kg/h = {m_steam/m_prod:.4f} kg/kg product")
# overall energy closure (adiabatic plant, no losses)
H_in_tot = H_gas(n_air, T_AMB) + n_S * H_S_FEED + H_liq(0, m_pw, T_PW) + (W_blower * ETA_MOTOR) * 3600
H_out_tot = (H_gas(g19, T_GAS_TOWER_OUT) + H_liq(m_prod_acid, m_prod_w, T_PRODUCT) + Q_steam
             + Q_acid_cooler + Q_prod_cooler)
print(f"energy closure: in {kW(H_in_tot):.1f} kW, out {kW(H_out_tot):.1f} kW, diff {kW(H_in_tot-H_out_tot):.2f} kW (pump heat not counted)")
print(f"per kg product: S {n_S*MW['S']/m_prod:.5f}, air {mass(n_air)/m_prod:.4f}, water {m_pw/m_prod:.5f}, "
      f"power {(W_blower+W_pump)/m_prod:.5f} kWh, steam heat {kW(Q_steam)/m_prod:.5f} kWh, "
      f"CW {kW(Q_acid_cooler+Q_prod_cooler)/m_prod:.5f} kWh, SO2 {g19['SO2']*MW['SO2']/m_prod*1000:.4f} g, "
      f"SO3 {g19['SO3']*MW['SO3']/m_prod*1000:.5f} g")
print("streams (kmol/h):")
for sid, g in [("S1", n_air), ("S2", dry), ("S5", g5), ("S7", g7), ("S9", g9), ("S11", g11),
               ("S14", g14), ("S17", g17), ("S19", g19)]:
    print(sid, f"{mass(g):.2f} kg/h", {c: float(f"{v:.9g}") for c, v in frac(g).items()})
print("temperatures K: furnace", round(T_furn, 2), "blower", round(T_blow, 2), "beds",
      [round(t, 2) for t in (T7, T9, T11, T17)], "E-203 hot out", round(T12, 2), "cold out", round(T15, 2),
      "tank", round(T_tank, 2))
print("acid towers (in, out kg/h, w_out):", [(round(m, 1), round(a + w, 1), float(f"{a/(a+w):.9g}"))
      for m, a, w in [(m_dt, a_dt, w_dt), (m_ipa, a_ipa_out, w_ipa), (m_fat, a_fat_out, w_fat)]])
print("duties kW: WHB", round(kW(Q_whb), 1), "E-201", round(kW(Q_hot_hot), 1), "E-202", round(kW(Q_sh), 1),
      "E-203", round(kW(Q_cold), 1), "E-204", round(kW(Q_eco1), 1), "E-205", round(kW(Q_eco2), 1),
      "E-301", round(kW(Q_acid_cooler), 1), "E-302", round(kW(Q_prod_cooler), 1),
      "K-101", round(W_blower, 1), "P-301", round(W_pump, 1))


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
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


# the values process/flowsheet.yaml cites from this script (balance-output contract): gas streams
# as mass flow and mole fractions, the tower acid returns as mass flow and mass fractions, the
# temperatures and duties printed above
FLOWSHEET = {}
for sid, g in [("S1", n_air), ("S2", dry), ("S5", g5), ("S7", g7), ("S9", g9), ("S11", g11),
               ("S14", g14), ("S17", g17), ("S19", g19)]:
    FLOWSHEET[sid] = {"flow": {"value": mass(g), "basis": "mass"},
                      "composition": {"values": frac(g), "basis": "mole_fraction"}}
for sid, a, w in [("S28", a_dt, w_dt), ("S29", a_ipa_out, w_ipa), ("S30", a_fat_out, w_fat)]:
    FLOWSHEET[sid] = {"flow": {"value": a + w, "basis": "mass"},
                      "composition": {"values": {"H2SO4": a / (a + w), "H2O": w / (a + w)},
                                      "basis": "mass_fraction"}}
FLOWSHEET["S4"] = {"flow": {"value": n_S * MW["S"], "basis": "mass"}}
FLOWSHEET["S31"] = {"flow": {"value": m_pw, "basis": "mass"}}
for sid, t in [("S3", T_blow), ("S5", T_furn), ("S7", T7), ("S9", T9), ("S11", T11), ("S12", T12),
               ("S15", T15), ("S17", T17), ("S20", T_tank)]:
    FLOWSHEET.setdefault(sid, {})["temperature"] = t
FLOWSHEET.update({qid: {"duty": q} for qid, q in {
    "Q1": W_blower, "Q2": W_pump, "Q3": kW(Q_whb), "Q4": kW(Q_sh), "Q5": kW(Q_eco1),
    "Q6": kW(Q_eco2), "Q7": kW(Q_acid_cooler), "Q8": kW(Q_prod_cooler),
    "QE201": kW(Q_hot_hot), "QE203": kW(Q_cold)}.items()})
write_balance_output({"design": FLOWSHEET})
