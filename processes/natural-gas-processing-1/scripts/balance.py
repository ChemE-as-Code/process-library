"""Mass and energy balance of natural-gas-processing-1 (design case), DESIGN.md D-006.

A specified-split model, independent of cheme: it gives the stream values that
process/flowsheet.yaml carries as `assumed` (source: scripts/balance.py) and the duties of the
energy streams. Run with `cheme run scripts/balance.py`; it writes nothing, it prints the
stream entries for process/flowsheet.yaml and a summary.

Inputs (each in DESIGN.md with its source or ASSUMED):
- feed: 100 MMscf/d (dry, 60 degF, 14.696 psia) of Barnett shale gas well 2 of Bullin and
  Krouskop (2009), Table 1: C1 81.2, C2 11.8, C3 5.2, CO2 0.3, N2 1.5 mol-% (D-003),
  water-saturated at 313.15 K and 6000 kPa(a) plus free water 1 bbl/MMscf (ASSUMED, D-004);
- water content of saturated gas: Bukacek correlation (D-004);
- amine unit: CO2 to 50 ppmv (ASSUMED, D-007), MDEA 45 wt-%, loadings and steam ratio ASSUMED;
- TEG unit: 7 lb/MMscf (pipeline specification, D-008), 3 US gal TEG per lb water removed, 1 scf
  gas absorbed per gal TEG, flash tank recovers 90 % of it (EPA Natural Gas STAR, D-008);
- NGL recovery: ethane 90 %, propane 98 % (inside the GSP range of US 11 473 837 B2, D-009);
- compression and fired heat: efficiencies ASSUMED (D-010, D-011).
Ideal-gas heat capacities and formation enthalpies are the ones `cheme chemistry thermo`
prints (ATcT, Poling 5th ed.). Gas-phase sensible heats are ideal-gas estimates: no property
package of cheme is benchmarked for these hydrocarbon mixtures (D-012).
"""

import math

R = 8.314462618  # kJ/(kmol K)
T0 = 298.15
M = {"CH4": 16.042, "C2H6": 30.069, "C3H8": 44.096, "CO2": 44.01, "N2": 28.013,
     "O2": 31.999, "H2O": 18.015, "MDEA": 119.163, "TEG": 150.174}
CP = {  # cp/R polynomials (Poling 5th ed. via cheme chemistry thermo), 50-1000 K
    "CH4": [4.568, -0.008975, 3.631e-05, -3.407e-08, 1.091e-11],
    "C2H6": [4.178, -0.004427, 5.66e-05, -6.651e-08, 2.487e-11],
    "C3H8": [3.847, 0.005131, 6.011e-05, -7.893e-08, 3.079e-11],
    "CO2": [3.259, 0.001356, 1.502e-05, -2.374e-08, 1.056e-11],
    "N2": [3.539, -0.000261, 7e-08, 1.57e-09, -9.9e-13],
    "O2": [3.63, -0.001794, 6.58e-06, -6e-09, 1.79e-12],
    "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
}
HF = {"CH4": -74534.0, "C2H6": -83780.0, "C3H8": -104390.0, "CO2": -393474.0,
      "H2O": -241822.0, "N2": 0.0, "O2": 0.0}  # kJ/kmol ideal gas 298.15 K (ATcT)
CARBON = {"CH4": 1, "C2H6": 2, "C3H8": 3, "CO2": 1}
HYDROGEN = {"CH4": 4, "C2H6": 6, "C3H8": 8, "H2O": 2}
GASES = ["CH4", "C2H6", "C3H8", "CO2", "N2"]
HC = ["CH4", "C2H6", "C3H8"]

LB = 0.45359237           # kg
SCF_PER_KMOL = 379.49 / LB  # scf per kmol at 60 degF, 14.696 psia (379.49 scf/lbmol)
GAL = 3.785411784e-3      # m3


def lhv(c):
    """Lower heating value, kJ/kmol, from the formation enthalpies (water as vapour)."""
    if c not in HC:
        return 0.0
    return -(CARBON[c] * HF["CO2"] + HYDROGEN[c] / 2 * HF["H2O"] - HF[c])


def cp(c, t):
    a = CP[c]
    return R * sum(a[i] * t ** i for i in range(5))


def dh(c, t):
    a = CP[c]
    f = lambda x: sum(a[i] * x ** (i + 1) / (i + 1) for i in range(5))
    return R * (f(t) - f(T0))


def psat_water(t):
    """Saturation pressure of water, kPa (Wagner and Pruss 1993, IAPWS)."""
    tc, pc = 647.096, 22064.0
    tau = 1 - t / tc
    a = [-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502]
    e = [1, 1.5, 3, 3.5, 4, 7.5]
    return pc * math.exp(tc / t * sum(ai * tau ** ei for ai, ei in zip(a, e)))


def bukacek_lb_per_mmscf(t, p_kpa):
    """Water content of sweet natural gas at saturation, lb per MMscf (Bukacek 1955)."""
    tf = (t - 273.15) * 1.8 + 32
    pv = psat_water(t) / 6.894757
    p = p_kpa / 6.894757
    b = 10 ** (-3083.87 / (459.6 + tf) + 6.69449)
    return 47484 * pv / p + b


def mmscfd(n):
    """Dry gas flow in MMscf/d from kmol/h (water excluded)."""
    return sum(v for k, v in n.items() if k in GASES) * SCF_PER_KMOL * 24 / 1e6


def kg(n):
    return {k: v * M[k] for k, v in n.items() if v > 0}


def mass(n):
    return sum(kg(n).values())


def add(*ns):
    out = {}
    for n in ns:
        for k, v in n.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(n, f):
    return {k: v * f for k, v in n.items()}


def cp_mix(n, t):
    tot = sum(v for k, v in n.items() if k in CP)
    return sum(v * cp(k, t) for k, v in n.items() if k in CP) / tot  # kJ/(kmol K)


def kmol(n):
    return sum(n.values())


# ---- feed (D-003, D-004) ---------------------------------------------------------------------
Y_FEED = {"CH4": 0.812, "C2H6": 0.118, "C3H8": 0.052, "CO2": 0.003, "N2": 0.015}
N_DRY = 100e6 / SCF_PER_KMOL / 24  # kmol/h, 100 MMscf/d dry
T_IN, P_IN = 313.15, 6000.0
dry = {k: v * N_DRY for k, v in Y_FEED.items()}
w_sat_in = bukacek_lb_per_mmscf(T_IN, P_IN) * mmscfd(dry) * LB / 24  # kg/h
free_water = 1.0 * 0.158987 * 1000.0 * mmscfd(dry) / 24  # 1 bbl/MMscf liquid water, kg/h
s2 = add(dry, {"H2O": w_sat_in / M["H2O"]})
s3 = {"H2O": free_water / M["H2O"]}
s1 = add(s2, s3)

# ---- amine unit (D-007) -----------------------------------------------------------------------
CO2_SWEET_PPMV = 50.0
HC_COABS = 0.0002      # fraction of each hydrocarbon co-absorbed in the rich amine, ASSUMED
HC_FLASH = 0.90        # of it released in the rich flash drum, ASSUMED
CO2_FLASH = 0.03       # of the absorbed CO2 released in the flash drum, ASSUMED
MDEA_WT = 0.45
LEAN_LOAD, RICH_LOAD = 0.005, 0.25   # mol CO2 / mol MDEA, ASSUMED
T_SWEET, P_SWEET = 318.15, 5950.0
STEAM_LB_PER_GAL = 1.0  # lb LP steam per US gal lean amine, ASSUMED rule of thumb
AMINE_RHO = 1040.0      # kg/m3 lean 45 wt-% MDEA, ASSUMED
HFG_LP = 2120.0         # kJ/kg latent heat of LP steam at 450 kPa(a) (IAPWS-IF97, about)
T_ACID, P_ACID = 323.15, 170.0

g = {k: v for k, v in dry.items()}
co2_out = None
coabs = {k: g[k] * HC_COABS for k in HC}
gas_left = {k: g[k] - coabs.get(k, 0.0) for k in GASES}
# CO2 left so that y(CO2) = 50 ppmv on the dry sweet gas
others = sum(v for k, v in gas_left.items() if k != "CO2")
co2_sweet = CO2_SWEET_PPMV * 1e-6 * others / (1 - CO2_SWEET_PPMV * 1e-6)
co2_abs = g["CO2"] - co2_sweet
gas_left["CO2"] = co2_sweet
w_sweet = bukacek_lb_per_mmscf(T_SWEET, P_SWEET) * mmscfd(gas_left) * LB / 24 / M["H2O"]
s4 = add(gas_left, {"H2O": w_sweet})

n_mdea = co2_abs / (RICH_LOAD - LEAN_LOAD)
m_mdea = n_mdea * M["MDEA"]
m_lean_w = m_mdea * (1 - MDEA_WT) / MDEA_WT
s9 = {"MDEA": n_mdea, "H2O": m_lean_w / M["H2O"], "CO2": n_mdea * LEAN_LOAD}  # lean amine
water_pickup = w_sweet - s2["H2O"]
s5 = add(s9, {"CO2": co2_abs, "H2O": -water_pickup}, coabs)                    # rich amine
s6 = add({k: v * HC_FLASH for k, v in coabs.items()}, {"CO2": co2_abs * CO2_FLASH})  # flash gas
s7 = add(s5, scale(s6, -1))
acid_dry = {"CO2": co2_abs * (1 - CO2_FLASH)}
acid_dry.update({k: v * (1 - HC_FLASH) for k, v in coabs.items()})
y_w_acid = psat_water(T_ACID) / P_ACID
s10 = add(acid_dry, {"H2O": kmol(acid_dry) * y_w_acid / (1 - y_w_acid)})
s8 = {"H2O": water_pickup + s10["H2O"]}  # demineralised make-up water
lean_vol_gal = (mass(s9) / AMINE_RHO) / GAL
steam_kg = STEAM_LB_PER_GAL * lean_vol_gal * LB
q_reboiler = steam_kg * HFG_LP / 3600
w_amine_pump = (mass(s9) / AMINE_RHO / 3600) * (6100 - 150) / 0.70 / 0.95  # kW electric

# ---- TEG dehydration (D-008) ------------------------------------------------------------------
W_DRY_LB = 7.0          # lb/MMscf pipeline specification
TEG_GAL_PER_LB = 3.0
TEG_RHO = 1120.0        # kg/m3, ASSUMED
LEAN_TEG_WT = 0.99      # ASSUMED
ABS_SCF_PER_GAL = 1.0
FLASH_REC = 0.90
T_REB, T_RICH_IN = 477.15, 423.15
CP_TEG = 2.5            # kJ/(kg K), ASSUMED
REFLUX_LOSS = 1.25      # reflux and heat loss factor on the still duty, ASSUMED

w_dry = W_DRY_LB * mmscfd(s4) * LB / 24 / M["H2O"]
w_removed = s4["H2O"] - w_dry  # kmol/h
lb_w = w_removed * M["H2O"] / LB
teg_gal = TEG_GAL_PER_LB * lb_w
m_teg = teg_gal * GAL * TEG_RHO
s15 = {"TEG": m_teg / M["TEG"], "H2O": m_teg * (1 / LEAN_TEG_WT - 1) / M["H2O"]}
gas4 = {k: s4[k] for k in GASES}
abs_kmol = teg_gal * ABS_SCF_PER_GAL / SCF_PER_KMOL
absorbed = {k: v / kmol(gas4) * abs_kmol for k, v in gas4.items()}
s11 = add(gas4, scale(absorbed, -1), {"H2O": w_dry})
s12 = add(s15, {"H2O": w_removed}, absorbed)
s13 = scale(absorbed, FLASH_REC)
s14 = add(s12, scale(s13, -1))
s16 = add(scale(absorbed, 1 - FLASH_REC), {"H2O": w_removed})  # still vent
q_teg = (mass(s14) * CP_TEG * (T_REB - T_RICH_IN) + w_removed * M["H2O"] * 2257.0) * REFLUX_LOSS / 3600
w_teg_pump = (m_teg / TEG_RHO / 3600) * (6000 - 120) / 0.70 / 0.95

# ---- molecular sieve polishing (D-008) ---------------------------------------------------------
REGEN_FRAC, T_REGEN, CP_GAS, HEAT_FRAC = 0.08, 561.15, 2.5, 0.5
s18 = {"H2O": s11["H2O"]}
s17 = {k: v for k, v in s11.items() if k != "H2O"}
q_regen = REGEN_FRAC * mass(s11) * CP_GAS * (T_REGEN - 313.15) * HEAT_FRAC / 3600
q_regen_cool = q_regen

# ---- NGL recovery (D-009) ----------------------------------------------------------------------
REC = {"C2H6": 0.90, "C3H8": 0.98, "CO2": 0.60, "N2": 0.0}
C1_C2_NGL = 0.02
LIQ = {"CH4": 0.04, "C2H6": 0.25, "C3H8": 0.60, "CO2": 0.20, "N2": 0.01}  # V-401 to liquid
T_COLD, P_COLD = 238.15, 5800.0
P_DEMETH = 2200.0
ETA_EXP, ETA_COMP, ETA_MECH, ETA_MOTOR = 0.85, 0.80, 0.97, 0.96

s19 = dict(s17)
s21 = {k: v * LIQ[k] for k, v in s19.items()}
s20 = add(s19, scale(s21, -1))
s23 = {k: s17[k] * REC[k] for k in ("C2H6", "C3H8", "CO2")}
s23["CH4"] = C1_C2_NGL * s23["C2H6"]
s24 = add(s17, scale(s23, -1))

# expander (ideal gas, isentropic efficiency)
def compress_or_expand(n, t1, p1, p2, eta):
    """Ideal-gas compression (p2 > p1) or expansion; returns (T2, work kW, + for compression)."""
    c = cp_mix(n, t1)
    k = c / (c - R)
    t2s = t1 * (p2 / p1) ** ((k - 1) / k)
    if p2 > p1:
        t2 = t1 + (t2s - t1) / eta
    else:
        t2 = t1 - eta * (t1 - t2s)
    c_mean = cp_mix(n, (t1 + t2) / 2)
    return t2, kmol(n) * c_mean * (t2 - t1) / 3600


T_EXP_OUT, w_exp = compress_or_expand(s20, T_COLD, P_COLD, P_DEMETH, ETA_EXP)
w_shaft = -w_exp * ETA_MECH
T_RES_WARM, P_RES_WARM = 308.15, 2150.0
s25 = dict(s24)
# booster: pressure reached with the expander shaft work
c = cp_mix(s25, T_RES_WARM)
k_ = c / (c - R)
dt_s = w_shaft * 3600 / (kmol(s25) * c) * ETA_COMP
P_BOOST = P_RES_WARM * ((T_RES_WARM + dt_s) / T_RES_WARM) ** (k_ / (k_ - 1))
T_BOOST = T_RES_WARM + w_shaft * 3600 / (kmol(s25) * c)
s27 = dict(s25)

# ---- fired heat and fuel gas (D-011) -----------------------------------------------------------
ETA_FIRED, EXCESS_AIR, T_FLUE = 0.80, 0.15, 473.15
q_fired = q_teg + q_regen
fuel_needed = q_fired / ETA_FIRED * 3600  # kJ/h LHV
lhv_flash = sum(v * lhv(k) for k, v in add(s6, s13).items())
lhv_res = sum(v * lhv(k) for k, v in s27.items()) / kmol(s27)  # kJ/kmol residue
n_fuel_res = (fuel_needed - lhv_flash) / lhv_res
fuel_frac = n_fuel_res / kmol(s27)
s29 = scale(s27, fuel_frac)
s28 = scale(s27, 1 - fuel_frac)
s32 = add(s6, s13, s29)
o2_st = sum(v * (CARBON.get(k, 0) + HYDROGEN.get(k, 0) / 4) for k, v in s32.items() if k in HC)
o2 = o2_st * (1 + EXCESS_AIR)
s33 = {"O2": o2, "N2": o2 * 79 / 21}
s34 = {
    "CO2": sum(v * CARBON.get(k, 0) for k, v in s32.items()),
    "H2O": sum(v * HYDROGEN.get(k, 0) / 2 for k, v in s32.items()),
    "O2": o2 - o2_st,
    "N2": s33["N2"] + s32.get("N2", 0.0),
}

# ---- residue compression (D-010) ---------------------------------------------------------------
P_SALES, T_SALES = 7000.0, 313.15
T_K501, w_k501 = compress_or_expand(s28, T_BOOST, P_BOOST, P_SALES, ETA_COMP)
e_k501 = w_k501 / ETA_MOTOR
s30 = dict(s28)
s31 = dict(s28)
q_aftercool = kmol(s30) * cp_mix(s30, (T_K501 + T_SALES) / 2) * (T_K501 - T_SALES) / 3600

# NGL pump
NGL_RHO = 470.0  # kg/m3 ASSUMED
P_NGL = 7000.0
w_ngl_pump = (mass(s23) / NGL_RHO / 3600) * (P_NGL - P_DEMETH) / 0.70 / 0.95
AUX = 150.0      # kW site auxiliaries ASSUMED
q_amine_cw = q_reboiler + w_amine_pump * 0.95 * 0.70

# ---- output ------------------------------------------------------------------------------------
STREAMS = [
    # id, title, from, to, template, n, T, P, source
    ("S1", "Raw gas from gathering", "RAWGAS.out", "V101.in", "gas", s1, T_IN, P_IN, "D-003, D-004: 100 MMscf/d dry gas of Bullin and Krouskop (2009) Table 1 Barnett well 2, saturated (Bukacek) plus 1 bbl/MMscf free water ASSUMED"),
    ("S2", "Water-saturated gas to amine absorber", "V101.gas", "T201.gas", "gas", s2, T_IN, 5980.0, "D-004: free water removed, gas saturated at inlet conditions (Bukacek)"),
    ("S3", "Free water from inlet separator", "V101.water", "PWATER.v101", "water", s3, T_IN, 5980.0, "D-004: 1 bbl/MMscf free water ASSUMED"),
    ("S4", "Sweet water-saturated gas", "T201.gas_out", "T301.gas", "gas", s4, T_SWEET, P_SWEET, "D-007: CO2 to 50 ppmv, co-absorption 0.02 % of each hydrocarbon, saturated at 318 K (Bukacek)"),
    ("S5", "Rich amine", "T201.rich", "V202.in", "amine", s5, 333.15, P_SWEET, "D-007: lean amine plus absorbed CO2 and hydrocarbons, less the water picked up by the gas"),
    ("S6", "Rich amine flash gas to fuel", "V202.gas", "M601.amine", "gas", s6, 333.15, 600.0, "D-007: 90 % of co-absorbed hydrocarbons and 3 % of absorbed CO2 flash at 600 kPa(a), ASSUMED"),
    ("S7", "Flashed rich amine to regenerator", "V202.liq", "T202.rich", "amine", s7, 333.15, 600.0, "D-007"),
    ("S8", "Demineralised make-up water", "DMW.out", "T202.dmw", "water", s8, 298.15, 300.0, "D-007: replaces the water leaving with sweet gas and acid gas"),
    ("S9", "Lean amine (MDEA 45 wt-%)", "T202.lean", "T201.lean", "amine", s9, 323.15, 6100.0, "D-007: MDEA 45 wt-%, loading 0.005 lean / 0.25 rich mol CO2/mol ASSUMED"),
    ("S10", "Acid gas to atmosphere", "T202.acid", "ACIDGAS.in", "gas", s10, T_ACID, P_ACID, "D-007: absorbed CO2 less flash, 10 % of co-absorbed hydrocarbons, water-saturated at 323 K"),
    ("S11", "TEG-dried gas", "T301.gas_out", "A303.in", "gas", s11, 318.15, 5920.0, "D-008: 7 lb/MMscf water, 1 scf gas absorbed per gal TEG (EPA)"),
    ("S12", "Rich TEG", "T301.rich", "V302.in", "teg", s12, 318.15, 5920.0, "D-008: 3 gal TEG per lb water removed (EPA), lean TEG 99 wt-% ASSUMED"),
    ("S13", "TEG flash gas to fuel", "V302.gas", "M601.teg", "gas", s13, 333.15, 450.0, "D-008: flash tank recovers 90 % of absorbed gas (EPA)"),
    ("S14", "Flashed rich TEG to still", "V302.liq", "T302.rich", "teg", s14, 333.15, 450.0, "D-008"),
    ("S15", "Lean TEG", "T302.lean", "T301.lean", "teg", s15, 323.15, 6000.0, "D-008: 99 wt-% TEG ASSUMED"),
    ("S16", "TEG still vent to atmosphere", "T302.vent", "STILLVENT.in", "gas", s16, 373.15, 105.0, "D-008: removed water and 10 % of absorbed gas"),
    ("S17", "Dry gas to cold box", "A303.gas", "E401.feed_in", "gas", s17, 318.15, 5880.0, "D-008: molecular sieve removes the remaining water"),
    ("S18", "Regeneration water knock-out", "A303.water", "PWATER.a303", "water", s18, 313.15, 5800.0, "D-008"),
    ("S19", "Chilled feed to cold separator", "E401.feed_out", "V401.in", "gas", s19, T_COLD, P_COLD, "D-009: cooled against residue gas and side reboilers, 238 K ASSUMED"),
    ("S20", "Cold separator vapour to expander", "V401.vap", "K401.in", "gas", s20, T_COLD, P_COLD, "D-009: V-401 liquid fractions ASSUMED"),
    ("S21", "Cold separator liquid to demethaniser", "V401.liq", "T401.liq", "gas", s21, T_COLD, P_COLD, "D-009"),
    ("S22", "Expander outlet to demethaniser", "K401.out", "T401.vap", "gas", s22 := dict(s20), T_EXP_OUT, P_DEMETH, "D-009: ideal-gas expansion, isentropic efficiency 0.85 ASSUMED"),
    ("S23", "Demethaniser bottoms (NGL)", "T401.btm", "P401.in", "ngl", s23, 283.15, P_DEMETH, "D-009: 90 % ethane, 98 % propane recovery; C1/C2 0.02 mol/mol"),
    ("S24", "Cold residue gas", "T401.ovhd", "E401.res_in", "gas", s24, 173.15, P_DEMETH, "D-009"),
    ("S25", "Warm residue gas to booster", "E401.res_out", "C401.in", "gas", s25, T_RES_WARM, P_RES_WARM, "D-009"),
    ("S26", "NGL product", "P401.out", "NGL.in", "ngl", s23, 288.15, P_NGL, "D-009: pumped to NGL pipeline"),
    ("S27", "Boosted residue gas", "C401.out", "X501.in", "gas", s27, T_BOOST, P_BOOST, "D-010: booster driven by K-401 shaft work"),
    ("S28", "Residue gas to compressor", "X501.comp", "K501.in", "gas", s28, T_BOOST, P_BOOST, "D-011: fuel draw closes the fired-heat balance"),
    ("S29", "Residue gas to fuel header", "X501.fuel", "M601.res", "gas", s29, T_BOOST, P_BOOST, "D-011"),
    ("S30", "Compressed residue gas", "K501.out", "E501.in", "gas", s30, T_K501, P_SALES + 50, "D-010: isentropic efficiency 0.80 ASSUMED"),
    ("S31", "Sales gas", "E501.out", "SALESGAS.in", "gas", s31, T_SALES, P_SALES, "D-010"),
    ("S32", "Fuel gas to fired heaters", "M601.out", "H601.fuel", "gas", s32, 313.15, 450.0, "D-011"),
    ("S33", "Combustion air", "AIR.out", "H601.air", "gas", s33, 298.15, 101.325, "D-011: 15 % excess air, 79/21 N2/O2 dry ASSUMED"),
    ("S34", "Flue gas to atmosphere", "H601.flue", "FLUE.in", "gas", s34, T_FLUE, 101.325, "D-011: complete combustion"),
]
ENERGY = [
    ("Q1", "Amine reboiler LP steam", "STEAM.t202", "T202.steam", q_reboiler, "D-007: 1.0 lb steam per gal lean amine ASSUMED, latent heat 2120 kJ/kg"),
    ("Q2", "Amine condenser and lean amine cooler", "T202.cw", "CW.t202", q_amine_cw, "D-007: equals reboiler duty plus pump work"),
    ("Q3", "Lean amine pump power", "POWER.t202", "T202.power", w_amine_pump, "D-007: 5950 kPa rise, eta 0.70, motor 0.95 ASSUMED"),
    ("Q4", "TEG reboiler heat (fired)", "H601.teg", "T302.heat", q_teg, "D-008: sensible 423-477 K plus water vaporisation, x1.25 ASSUMED"),
    ("Q5", "TEG pump power", "POWER.t302", "T302.power", w_teg_pump, "D-008: eta 0.70, motor 0.95 ASSUMED"),
    ("Q6", "Mole sieve regeneration heat (fired)", "H601.regen", "A303.heat", q_regen, "D-008: 8 % regeneration gas to 561 K, heating half the cycle ASSUMED"),
    ("Q7", "Regeneration gas cooler", "A303.cw", "CW.a303", q_regen_cool, "D-008"),
    ("Q8", "Expander shaft work to booster", "K401.shaft", "C401.shaft", w_shaft, "D-009: mechanical efficiency 0.97 ASSUMED"),
    ("Q9", "NGL pump power", "POWER.p401", "P401.power", w_ngl_pump, "D-009: eta 0.70, motor 0.95 ASSUMED"),
    ("Q10", "Residue compressor motor power", "POWER.k501", "K501.power", e_k501, "D-010: ideal gas, isentropic 0.80, motor 0.96 ASSUMED"),
    ("Q11", "Sales gas aftercooler", "E501.cw", "CW.e501", q_aftercool, "D-010"),
    ("Q12", "Site auxiliaries (instrument air, controls, lighting)", "POWER.v101", "V101.aux", AUX, "D-010: 150 kW ASSUMED"),
]


def fmt_stream(sid, title, frm, to, tpl, n, t, p, src):
    m = kg(n)
    tot = sum(m.values())
    comp = ", ".join(f"{k}: {v / tot:.7f}" for k, v in m.items())
    return (f'  - {{id: {sid}, title: "{title}", from: {frm}, to: {to}, template: {tpl}, state: {{design: {{'
            f'temperature: {{value: {t:.2f}, provenance: assumed, source: "scripts/balance.py"}}, '
            f'pressure: {{value: {p:.1f}, provenance: assumed, source: "scripts/balance.py"}}, '
            f'flow: {{value: {tot:.2f}, basis: mass, provenance: assumed, source: "scripts/balance.py: {src}"}}, '
            f'composition: {{basis: mass_fraction, values: {{{comp}}}, provenance: assumed, source: "scripts/balance.py"}}}}}}}}')


if __name__ == "__main__":
    print("streams:")
    for s in STREAMS:
        print(fmt_stream(*s))
    for qid, title, frm, to, q, src in ENERGY:
        print(f'  - {{id: {qid}, title: "{title}", kind: energy, from: {frm}, to: {to}, state: {{design: {{duty: {{value: {q:.1f}, provenance: assumed, source: "scripts/balance.py: {src}"}}}}}}}}')
    print()
    ins = mass(s1) + mass(s8) + mass(s33)
    outs = mass(s31) + mass(s23) + mass(s10) + mass(s34) + mass(s3) + mass(s18) + mass(s16)
    print(f"# overall: in {ins:.2f} kg/h, out {outs:.2f} kg/h, diff {ins - outs:.4f}")
    print(f"# feed {N_DRY:.1f} kmol/h dry, {mass(dry):.1f} kg/h dry; saturated water {w_sat_in:.2f} kg/h; free water {free_water:.1f} kg/h")
    print(f"# sales gas {mass(s31):.1f} kg/h, {mmscfd(s31):.2f} MMscf/d; NGL {mass(s23):.1f} kg/h")
    lhv_sales = sum(v * lhv(k) for k, v in s31.items()) / mass(s31) / 1000
    lhv_ngl = sum(v * lhv(k) for k, v in s23.items()) / mass(s23) / 1000
    hhv_vol = sum(v * (lhv(k) + HYDROGEN.get(k, 0) / 2 * 44010.0 * (k in HC)) for k, v in s31.items()) / kmol(s31) / SCF_PER_KMOL * 0.947817
    print(f"# LHV sales gas {lhv_sales:.3f} MJ/kg, NGL {lhv_ngl:.3f} MJ/kg; sales gas HHV about {hhv_vol:.0f} Btu/scf")
    y31 = {k: v / kmol(s31) for k, v in s31.items()}
    print(f"# sales gas mol fractions: " + ", ".join(f"{k} {v:.5f}" for k, v in y31.items()))
    print(f"# CO2 absorbed {co2_abs:.3f} kmol/h = {co2_abs * 44.01:.1f} kg/h; lean amine {mass(s9):.0f} kg/h, {lean_vol_gal / 60:.0f} gpm; steam {steam_kg:.0f} kg/h; specific reboiler duty {q_reboiler * 3.6 / (co2_abs * 44.01):.2f} GJ/t CO2")
    print(f"# water removed by TEG {lb_w:.1f} lb/h; TEG circulation {teg_gal:.0f} gal/h = {m_teg:.0f} kg/h; absorbed gas {abs_kmol:.4f} kmol/h")
    print(f"# expander T out {T_EXP_OUT:.1f} K, work {w_exp:.1f} kW; booster to {P_BOOST:.0f} kPa, {T_BOOST:.1f} K; K-501 out {T_K501:.1f} K, shaft {w_k501:.1f} kW")
    print(f"# fired duty {q_fired:.1f} kW; fuel from residue {fuel_frac * 100:.3f} % = {mass(s29):.1f} kg/h; flash gas fuel {mass(s6) + mass(s13):.2f} kg/h")
    ethane_rec = s23["C2H6"] / dry["C2H6"]
    print(f"# overall ethane recovery {ethane_rec:.4f}, propane {s23['C3H8'] / dry['C3H8']:.4f}")
    print(f"# CO2 emitted: acid gas {s10['CO2'] * 44.01:.1f} kg/h, flue {s34['CO2'] * 44.01:.1f} kg/h; CH4 acid {s10.get('CH4', 0) * 16.042:.3f}, still vent {s16.get('CH4', 0) * 16.042:.3f} kg/h")
    print(f"# electricity total {w_amine_pump + w_teg_pump + w_ngl_pump + e_k501 + AUX:.1f} kW; CW total {q_amine_cw + q_regen_cool + q_aftercool:.1f} kW")
