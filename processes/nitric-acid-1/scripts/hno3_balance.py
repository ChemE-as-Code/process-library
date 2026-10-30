"""Independent heat and material balance of the dual-pressure nitric acid plant (DESIGN.md D-010).

This is NOT a cheme-as-code calculation. Core has no qualified property package for nitrous
gas with water or for aqueous nitric acid, and no reactive-absorption model (core #315, #364).
The results go into process/flowsheet.yaml as `assumed` values with this script as their
source; cheme then checks mass, component and element balances and the reaction extents, and
computes the burner, cooler-condenser and tertiary-reactor outlets itself (conversion reactors
with the conversions printed here).

Model (every choice is a DESIGN.md decision, ASSUMED where marked there):
- burner (D-005): complete NH3 conversion over Pt/Rh; selectivity to NO assumed; N2O formation
  from the IPCC 2006 default for medium-pressure combustion plants (7 kg N2O per t HNO3,
  Vol. 3 Ch. 3, Table 3.3, p. 3.23); the rest of the NH3 to N2;
- cooler-condenser (D-007): weak acid of assumed strength; water vapour of the gas leaving at an
  assumed mole fraction; an assumed NO oxidation degree;
- absorber and bleacher (D-008): a specification model, not a reactive-absorption model:
  product strength, tail-gas NOx (as NO), O2 and H2O are specifications; dissolved NOx (as NO2)
  in the raw acid stripped completely in the bleacher;
- tertiary reactor (D-009): N2O decomposition sized to reach the IPCC default for plants with
  tail-gas N2O destruction (2.5 kg N2O per t HNO3, Table 3.3), SCR of NO with NH3 (no slip);
- enthalpies (D-010): ideal-gas heat capacities and gas formation enthalpies of `thermo` /
  `chemicals` (Poling et al. / TRC correlations, unqualified here); liquid water and acid with
  constant heat capacity and an assumed heat of mixing; NH3 evaporation with CoolProp (pure
  NH3 reference EOS); compressors and expander isentropic with an assumed efficiency.

Run: cheme run scripts/hno3_balance.py   (prints streams and duties; JSON copy in build/)
"""

import json
import math
from pathlib import Path

import CoolProp.CoolProp as CP
import yaml
from chemicals.reaction import Hfg
from thermo import HeatCapacityGas

ROOT = Path(__file__).resolve().parents[1]
MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
C = ["NH3", "N2", "O2", "AR", "H2O", "NO", "NO2", "N2O", "HNO3"]
MW = {c: MAT[c]["molar_mass"] for c in C}
CAS = {c: MAT[c]["cas"] for c in C}
R = 8.314462618  # kJ/(kmol K)
T0 = 298.15

# ---- basis (design-basis.yaml, DESIGN.md)
HNO3_KG_H = 1000e3 / 24        # D-002: 1000 t/d HNO3 (100 %) contained in the product
W_ACID = 0.60                  # D-002: product strength, mass fraction HNO3
AIR = {"N2": 0.773428, "O2": 0.207365, "AR": 0.009247, "H2O": 0.010}  # D-004, 1 mol% humidity
Y_NH3 = 0.100                  # D-005: NH3 in the burner feed, mole fraction
S_NO = 0.955                   # D-005: NH3 -> NO selectivity at the gauze, ASSUMED
EF_N2O_FORMED = 7.0            # kg N2O / t HNO3, IPCC 2006 Table 3.3, medium pressure combustion
EF_N2O_ABATED = 2.5            # kg N2O / t HNO3, IPCC 2006 Table 3.3, tail-gas N2O destruction
W_WEAK = 0.42                  # D-007: weak acid from the cooler-condenser, mass fraction
Y_H2O_V101 = 0.009             # D-007: water vapour leaving the separator
OX_V101 = 0.50                 # D-007: NO2/(NO+NO2) of the gas leaving the cooler-condenser
NOX_TAIL = 500e-6              # D-008: NOx (as NO) leaving the absorber, mole fraction
O2_TAIL = 0.030                # D-008: O2 leaving the absorber, mole fraction
H2O_TAIL = 0.004               # D-008: water vapour leaving the absorber
W_NO2_RAW = 0.005              # D-008: dissolved NOx (as NO2) in the raw acid, mass fraction
SCR_X = 0.90                   # D-009: NO converted in the SCR
# pressures kPa(a) and temperatures K (D-003)
T_AMB, P_AMB = 288.15, 101.325
P_K101 = 520.0
P_NH3L, T_NH3L = 1600.0, 288.15  # liquid NH3 at the battery limit (subcooled)
P_NH3S, T_NH3S = 1300.0, 323.15  # SCR ammonia vaporised on LP steam (E108), above the tail-gas pressure
P_NH3V, T_NH3V = 600.0, 288.15
P_MIX = 510.0
P_R101 = 490.0
T_E102, T_E104, T_E105 = 793.15, 453.15, 313.15
P_E102, P_E103, P_E104, P_V101 = 485.0, 480.0, 475.0, 465.0
P_K102 = 1150.0
P_E106, P_C101 = 1140.0, 1130.0
T_E107 = 313.15
P_TAIL, T_TAIL = 1100.0, 303.15
T_RAW, T_ACID, T_PW, T_WEAK_P = 313.15, 313.15, 303.15, 313.15
P_BLEACH = 500.0
P_E106C, P_E103C, P_R102 = 1090.0, 1070.0, 1050.0
T_R102_IN = 703.15             # D-009: tertiary reactor inlet
P_STACK = 105.0
ETA_K101, ETA_K102, ETA_X101, ETA_PUMP = 0.85, 0.80, 0.85, 0.65  # D-011
DH_MIX = {0.60: -17.0e3, 0.42: -22.0e3}  # kJ per kmol HNO3, heat of mixing HNO3(l)+H2O(l), ASSUMED (D-010)
CP_ACID = 2.7                  # kJ/(kg K), aqueous acid, ASSUMED (D-010)
CP_W = 75.3                    # kJ/(kmol K), liquid water
HF_L = {"H2O": -285830.0, "HNO3": -174100.0}  # kJ/kmol, liquid, standard formation enthalpies

CPG = {c: HeatCapacityGas(CASRN=CAS[c]) for c in C}
HFG = {c: (Hfg(CAS[c]) or 0.0) for c in C}  # J/mol = kJ/kmol


def h_gas(c, T):
    return HFG[c] + CPG[c].T_dependent_property_integral(T0, T)


def H_gas(n, T):
    return sum(n.get(c, 0.0) * h_gas(c, T) for c in C) / 3600.0  # kW


def S_rel(n, T, P):  # ideal-gas entropy change basis for isentropic steps (kJ/K per h, relative)
    tot = sum(n.values())
    return sum(n[c] * (CPG[c].T_dependent_property_integral_over_T(T0, T) - R * math.log(P / 100.0)) for c in n if n[c] > 0)


def T_from_H(n, H_kw, guess=500.0):
    T = guess
    for _ in range(100):
        f = H_gas(n, T) - H_kw
        cp = (H_gas(n, T + 0.5) - H_gas(n, T - 0.5))
        T -= f / cp
        if abs(f) < 1e-6:
            break
    return T


def machine(n, T1, P1, P2, eta, expander=False):
    s1 = S_rel(n, T1, P1)
    T2s = T1 * (P2 / P1) ** 0.2857
    for _ in range(100):
        f = S_rel(n, T2s, P2) - s1
        d = (S_rel(n, T2s + 0.5, P2) - S_rel(n, T2s - 0.5, P2))
        T2s -= f / d
        if abs(f) < 1e-8:
            break
    dHs = H_gas(n, T2s) - H_gas(n, T1)
    dH = dHs * eta if expander else dHs / eta
    T2 = T_from_H(n, H_gas(n, T1) + dH, T2s)
    return T2, dH  # dH kW (positive: work into the gas)


def H_liq(n, T):
    """Aqueous acid or water: formation enthalpy of the liquids, heat of mixing, sensible heat."""
    kg = sum(n.get(c, 0.0) * MW[c] for c in C)
    w = n.get("HNO3", 0.0) * MW["HNO3"] / kg if kg else 0.0
    h = n.get("H2O", 0.0) * HF_L["H2O"] + n.get("HNO3", 0.0) * HF_L["HNO3"]
    if n.get("HNO3", 0.0):
        h += n["HNO3"] * (DH_MIX[0.60] if w > 0.5 else DH_MIX[0.42])
        h += kg * CP_ACID * (T - T0)
    else:
        h += n.get("H2O", 0.0) * CP_W * (T - T0)
    h += n.get("NO2", 0.0) * h_gas("NO2", T)  # dissolved NOx: gas enthalpy, heat of solution neglected
    return h / 3600.0


def kg(n):
    return sum(n.get(c, 0.0) * MW[c] for c in C)


def add(*ns):
    out = {c: 0.0 for c in C}
    for n in ns:
        for c, v in n.items():
            out[c] += v
    return out


def scale(n, f):
    return {c: v * f for c, v in n.items()}


def frac(n):
    t = sum(n.values())
    return {c: v / t for c, v in n.items() if v > 1e-12}


n_hno3 = HNO3_KG_H / MW["HNO3"]
n2o_formed = EF_N2O_FORMED * HNO3_KG_H / 1000.0 / MW["N2O"]

# ---- fixed point on NH3 feed, secondary air and the NO2 recycle
nh3 = n_hno3 / S_NO
sec_air = 0.1 * nh3 * 9
no2_rec = 50.0
for it in range(200):
    # burner
    prim_air_tot = nh3 * (1 - Y_NH3) / Y_NH3
    air1 = {c: prim_air_tot * y for c, y in AIR.items()}
    s_n2o = 2 * n2o_formed / nh3
    s_n2 = 1 - S_NO - s_n2o
    x_ox, x_n2o, x_n2 = S_NO, s_n2o, s_n2
    feed = add(air1, {"NH3": nh3})
    r_ox, r_n2o, r_n2 = nh3 * x_ox / 4, nh3 * x_n2o / 4, nh3 * x_n2 / 4
    # NH3_OX: 4 NH3 + 5 O2 -> 4 NO + 6 H2O ; NH3_N2O: 4 NH3 + 4 O2 -> 2 N2O + 6 H2O ; NH3_N2: 4 NH3 + 3 O2 -> 2 N2 + 6 H2O
    burn = add(feed, {"NH3": -nh3, "O2": -5 * r_ox - 4 * r_n2o - 3 * r_n2, "NO": 4 * r_ox, "N2O": 2 * r_n2o,
                      "N2": 2 * r_n2, "H2O": 6 * (r_ox + r_n2o + r_n2)})
    # cooler-condenser: weak acid, NO oxidation (NO_ABS: 4 NO + 3 O2 + 2 H2O -> 4 HNO3; NO_OX: 2 NO + O2 -> 2 NO2)
    # unknown a = kmol HNO3 formed; condensate water w; gas water fixed by Y_H2O_V101
    gas_dry_guess = sum(v for c, v in burn.items() if c not in ("H2O",))
    a = 0.0
    for _ in range(50):
        no_left = burn["NO"] - a
        no2 = OX_V101 * no_left
        gas = add(burn, {"NO": -a - no2, "NO2": no2, "O2": -0.75 * a - 0.5 * no2, "H2O": -0.5 * a, "HNO3": a})
        gas_nonw = sum(v for c, v in gas.items() if c not in ("H2O", "HNO3"))
        h2o_vap = Y_H2O_V101 / (1 - Y_H2O_V101) * gas_nonw
        w_cond = gas["H2O"] - h2o_vap
        # weak acid strength: a*63 / (a*63 + w_cond*18) = W_WEAK
        a_new = W_WEAK / (1 - W_WEAK) * w_cond * MW["H2O"] / MW["HNO3"]
        if abs(a_new - a) < 1e-9:
            break
        a = a_new
    x_abs_e105 = a / burn["NO"]
    x_ox_e105 = no2 / burn["NO"]
    e105_out = gas
    weak = {"HNO3": a, "H2O": w_cond}
    v101_gas = {c: v for c, v in gas.items()}
    v101_gas["HNO3"] = 0.0
    v101_gas["H2O"] = h2o_vap
    # secondary air and bleacher gas (strips the dissolved NO2)
    air2 = {c: sec_air * y for c, y in AIR.items()}
    bleach_gas = add(air2, {"NO2": no2_rec})
    m102 = add(v101_gas, bleach_gas)
    # absorber: tail gas inerts = N2, AR, N2O ; O2, NO, H2O specified fractions
    inert = m102["N2"] + m102["AR"] + m102["N2O"]
    tail_tot = inert / (1 - O2_TAIL - NOX_TAIL - H2O_TAIL)
    tail = {"N2": m102["N2"], "AR": m102["AR"], "N2O": m102["N2O"], "O2": O2_TAIL * tail_tot,
            "NO": NOX_TAIL * tail_tot, "H2O": H2O_TAIL * tail_tot}
    # N into raw acid as HNO3: N in - N tail(NO) - dissolved NO2
    # overall absorber reaction on NO and NO2 (NO2_ABS: 4 NO2 + O2 + 2 H2O -> 4 HNO3 ; plus NO_ABS)
    n_in_nox = m102["NO"] + m102["NO2"]
    hno3_raw = weak["HNO3"] + n_in_nox - tail["NO"] - no2_rec
    raw = {"HNO3": hno3_raw, "NO2": no2_rec}
    w_h2o_prod = hno3_raw * MW["HNO3"] * (1 - W_ACID) / W_ACID / MW["H2O"]
    raw["H2O"] = w_h2o_prod
    # dissolved NO2 from W_NO2_RAW
    no2_rec_new = W_NO2_RAW / (1 - W_NO2_RAW) * (hno3_raw * MW["HNO3"] + w_h2o_prod * MW["H2O"]) / MW["NO2"]
    # O2 balance gives the secondary air: O2 consumed in the absorber
    no_conv = m102["NO"] - tail["NO"]          # NO -> HNO3 (3/4 O2 each)
    no2_conv = m102["NO2"] - no2_rec           # NO2 -> HNO3 (1/4 O2 each)
    o2_need = 0.75 * no_conv + 0.25 * no2_conv
    o2_tail_from_air = m102["O2"] - o2_need
    # process water: H2O balance of the absorber
    h2o_consumed = 0.5 * no_conv + 0.5 * no2_conv
    pw = raw["H2O"] + tail["H2O"] + h2o_consumed - m102["H2O"] - weak["H2O"]
    # updates
    err_o2 = tail["O2"] - o2_tail_from_air
    sec_air_new = sec_air + err_o2 / AIR["O2"] * 0.7
    nh3_new = nh3 * n_hno3 / hno3_raw
    if abs(sec_air_new - sec_air) < 1e-8 and abs(nh3_new - nh3) < 1e-8 and abs(no2_rec_new - no2_rec) < 1e-9:
        break
    sec_air, nh3, no2_rec = sec_air_new, nh3_new, no2_rec_new
assert sec_air > 0, "secondary air must be positive: primary air already carries the absorber's O2"
product = {"HNO3": hno3_raw, "H2O": raw["H2O"]}

# ---- tertiary reactor: N2O decomposition and SCR
n2o_out = EF_N2O_ABATED * HNO3_KG_H / 1000.0 / MW["N2O"]
x_n2o_dec = 1 - n2o_out / tail["N2O"]
nh3_scr = SCR_X * tail["NO"]
# SCR_NO: 4 NO + 4 NH3 + O2 -> 4 N2 + 6 H2O ; N2O_DEC: 2 N2O -> 2 N2 + O2
r_scr = nh3_scr / 4
r_dec = x_n2o_dec * tail["N2O"] / 2
stack = add(tail, {"NO": -4 * r_scr, "O2": -r_scr + r_dec, "N2": 4 * r_scr + 2 * r_dec, "H2O": 6 * r_scr,
                   "N2O": -2 * r_dec})
nh3_total = nh3 + nh3_scr
air_tot = prim_air_tot + sec_air

# ---- energy
h_nh3_l = CP.PropsSI("H", "T", T_NH3L, "P", P_NH3L * 1e3, "Ammonia")
h_nh3_v = CP.PropsSI("H", "T", T_NH3V, "P", P_NH3V * 1e3, "Ammonia")
Q_E101 = nh3 * MW["NH3"] * (h_nh3_v - h_nh3_l) / 1e3 / 3600.0  # kW, burner ammonia
h_nh3_s = CP.PropsSI("H", "T", T_NH3S, "P", P_NH3S * 1e3, "Ammonia")
Q_E108 = nh3_scr * MW["NH3"] * (h_nh3_s - h_nh3_l) / 1e3 / 3600.0  # kW, SCR ammonia
H_NH3_FEED = H_gas({"NH3": nh3}, T_NH3V) - Q_E101 + H_gas({"NH3": nh3_scr}, T_NH3S) - Q_E108
air_all = {c: air_tot * y for c, y in AIR.items()}
T_K101, W_K101 = machine(air_all, T_AMB, P_AMB, P_K101, ETA_K101)
nh3_v = {"NH3": nh3}
H_mix = H_gas(air1, T_K101) + H_gas(nh3_v, T_NH3V)
T_MIX = T_from_H(feed, H_mix, 450)
T_R101 = T_from_H(burn, H_mix, 1150)        # adiabatic gauze
Q_E102 = H_gas(burn, T_R101) - H_gas(burn, T_E102)
# tail gas train: E106 (cold side) then E103 (cold side) to T_R102_IN
T_K102_IN_guess = T_E105
H_m102 = H_gas(v101_gas, T_E105) + H_gas(bleach_gas, T_K101 - 0.0 if False else 313.15)
T_M102 = T_from_H(m102, H_m102, 313)
T_K102, W_K102 = machine(m102, T_M102, P_V101 - 5.0, P_K102, ETA_K102)
# E106: NOx gas cooled from T_K102 to approach: tail gas heated to (T_K102 - 30)
T_TAIL_E106 = T_K102 - 30.0
Q_E106 = H_gas(tail, T_TAIL_E106) - H_gas(tail, T_TAIL)
T_E106_HOT = T_from_H(m102, H_gas(m102, T_K102) - Q_E106, 350)
Q_E107 = H_gas(m102, T_E106_HOT) - H_gas(m102, T_E107)
Q_E103 = H_gas(tail, T_R102_IN) - H_gas(tail, T_TAIL_E106)
T_E103_HOT = T_from_H(burn, H_gas(burn, T_E102) - Q_E103, 600)
Q_E104 = H_gas(burn, T_E103_HOT) - H_gas(burn, T_E104)
H_e105_out = H_gas(v101_gas, T_E105) + H_liq(weak, T_E105)
Q_E105 = H_gas(burn, T_E104) - H_e105_out
# tertiary reactor adiabatic (SCR NH3 at T_NH3V)
nh3_scr_n = {"NH3": nh3_scr}
H_r102_in = H_gas(tail, T_R102_IN) + H_gas(nh3_scr_n, T_NH3S)
T_R102 = T_from_H(stack, H_r102_in, 720)
T_STACK, W_X101 = machine(stack, T_R102, P_R102 - 10.0, P_STACK, ETA_X101, expander=True)
# weak acid pump
rho_weak = 1260.0  # kg/m3, ~42 wt% acid, ASSUMED
W_P101 = kg(weak) / 3600 / rho_weak * (P_C101 - P_V101) / ETA_PUMP  # kW
# absorber: energy balance closes with its cooling duty (feeds: gas at T_E107, weak acid, water)
pw_n = {"H2O": pw}
H_c101_in = H_gas(m102, T_E107) + H_liq(weak, T_WEAK_P) + H_liq(pw_n, T_PW) + W_P101 * 0
H_c101_out = H_gas(tail, T_TAIL) + H_liq(raw, T_RAW)
Q_C101 = H_c101_in - H_c101_out
# bleacher: secondary air (from K101 discharge, cooled? no: hot air) strips NO2
H_c102_in = H_liq(raw, T_RAW) + H_gas(air2, T_K101)
H_c102_out = H_liq(product, T_ACID) + H_gas(bleach_gas, 313.15)
Q_C102 = H_c102_in - H_c102_out  # heat leaving with the acid cooling (to CW), kW
# absorber cooling also supplies the NH3 evaporator (chilled-water loop): CW gets the rest
Q_C101_CW = Q_C101 - Q_E101
W_NET = W_K101 + W_K102 + W_X101 + W_P101  # W_X101 negative

out = {
    "basis": {"HNO3_kg_h": HNO3_KG_H, "iterations": it},
    "burner_conversions": {"NH3_OX": x_ox, "NH3_N2O": x_n2o, "NH3_N2": x_n2},
    "e105_conversions_of_NO": {"NO_ABS": x_abs_e105, "NO_OX": x_ox_e105},
    "r102_conversions": {"N2O_DEC (key N2O)": x_n2o_dec, "SCR_NO (key NH3)": 1.0},
    "nh3_split_to_scr": nh3_scr / nh3_total,
    "air_split_secondary": sec_air / air_tot,
    "temperatures_K": {"K101 out": T_K101, "mix": T_MIX, "R101 out": T_R101, "E103 hot out": T_E103_HOT,
                       "M102": T_M102, "K102 out": T_K102, "E106 hot out": T_E106_HOT,
                       "E106 cold out": T_TAIL_E106, "R102 out": T_R102, "stack": T_STACK},
    "duties_kW": {"E101 NH3 evaporation": Q_E101, "E108 SCR NH3 vaporiser": Q_E108,"K101": W_K101, "E102 boiler": Q_E102, "E103": Q_E103,
                  "E104 economiser": Q_E104, "E105 cooler-condenser": Q_E105, "K102": W_K102,
                  "E106": Q_E106, "E107": Q_E107, "C101 total": Q_C101, "C101 to CW": Q_C101_CW,
                  "C102 acid cooling": Q_C102, "X101": W_X101, "P101": W_P101, "net shaft": W_NET},
}
streams = {
    "NH3 liquid feed": {"NH3": nh3_total}, "NH3 to burner": nh3_v, "NH3 to SCR": nh3_scr_n,
    "air total": air_all, "primary air": air1, "secondary air": air2, "burner feed": feed,
    "burner out": burn, "E105 out": e105_out, "weak acid": weak, "V101 gas": v101_gas,
    "bleacher gas": bleach_gas, "M102 out": m102, "process water": pw_n, "tail gas": tail, "raw acid": raw,
    "product": product, "stack": stack,
}
out["streams"] = {}
for k, n in streams.items():
    tot = sum(n.values())
    kgh = kg(n)
    out["streams"][k] = {"kg_h": kgh, "kmol_h": tot,
                         "mole_fraction": {c: v / tot for c, v in n.items() if v > 1e-12},
                         "mass_fraction": {c: v * MW[c] / kgh for c, v in n.items() if v > 1e-12}}
# overall checks
m_in = kg({"NH3": nh3_total}) + kg(air_all) + kg(pw_n)
m_out = kg(product) + kg(stack)
N_in = nh3_total
N_out = product["HNO3"] + stack["NO"] + 2 * stack["N2O"] + 2 * stack["N2"] - 2 * air_all["N2"]
E_in = H_NH3_FEED + Q_E108 + H_gas(air_all, T_AMB) + H_liq(pw_n, T_PW) + W_K101 + W_K102 + W_P101
E_out = (H_liq(product, T_ACID) + H_gas(stack, T_STACK) - W_X101 + Q_E102 + Q_E104 + Q_E105 + Q_E107
         + Q_C101_CW + Q_C102)
out["checks"] = {"mass_in": m_in, "mass_out": m_out, "N_NH3_to_HNO3": product["HNO3"] / nh3_total,
                 "N2O_formed_kg_h": n2o_formed * MW["N2O"], "N2O_emitted_kg_h": stack["N2O"] * MW["N2O"],
                 "energy_in_kW": E_in, "energy_out_kW": E_out,
                 "t_NH3_per_t_HNO3": nh3_total * MW["NH3"] / HNO3_KG_H,
                 "steam_heat_kW": Q_E102 + Q_E104, "N_balance_kmol_h": N_in - N_out}
print(json.dumps(out, indent=1))
# the values the flowsheet takes from here, in its own notation (copied by hand, D-010)
print("\n# flow kg/h and mole fractions of the specified (separator and feed) streams")
for k in ["NH3 liquid feed", "air total", "process water", "weak acid", "V101 gas", "tail gas", "raw acid",
          "product", "bleacher gas"]:
    s = out["streams"][k]
    comp = ", ".join(f"{'\"NO\"' if c == 'NO' else c}: {v:.6f}" for c, v in s["mole_fraction"].items())
    print(f"{k}: flow {s['kg_h']:.1f}; composition {{{comp}}}")
(ROOT / "build").mkdir(exist_ok=True)
(ROOT / "build/hno3_balance.json").write_text(json.dumps(out, indent=1))

# ---- the values process/flowsheet.yaml cites from this script (balance-output contract)
W_X101_TO_K102 = -W_X101 - W_K101  # expander power beyond K-101's, to K-102


def _y(n):
    t = sum(n.values())
    return {c: v / t for c, v in n.items() if v > 1e-12}


FLOWSHEET = {
    "S01": {"flow": kg({"NH3": nh3_total})}, "S06": {"flow": kg(air_all)},
    "S07": {"temperature": T_K101}, "S08": {"temperature": T_K101}, "S09": {"temperature": T_K101},
    "S10": {"temperature": T_MIX}, "S11": {"temperature": T_R101},
    "S13": {"temperature": T_E103_HOT},
    "S16": {"flow": kg(v101_gas), "composition": _y(v101_gas)}, "S17": {"flow": kg(weak)},
    "S19": {"flow": kg(bleach_gas), "composition": _y(bleach_gas)},
    "S20": {"temperature": T_M102}, "S21": {"temperature": T_K102},
    "S22": {"temperature": T_E106_HOT}, "S24": {"flow": kg(pw_n)}, "S25": {"flow": kg(tail)},
    "S28": {"temperature": T_R102}, "S29": {"temperature": T_STACK}, "S30": {"flow": kg(raw)},
    "Q01": {"duty": W_K101}, "Q02": {"duty": W_X101_TO_K102},
    "Q03": {"duty": W_K102 - W_X101_TO_K102}, "Q04": {"duty": W_P101}, "Q05": {"duty": Q_E102},
    "Q06": {"duty": Q_E104}, "Q07": {"duty": Q_E105}, "Q08": {"duty": Q_E107},
    "Q09": {"duty": Q_C101_CW}, "Q10": {"duty": Q_C102}, "Q11": {"duty": Q_E101},
    "Q12": {"duty": Q_E108},
}


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0024 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import json
    import os

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


write_balance_output({"design": FLOWSHEET})
