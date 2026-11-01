"""Mass and energy balance of sodium-nitrite-1 (design case), DESIGN.md D-007.

Independent of cheme: it gives the stream values that process/flowsheet.yaml carries as
`assumed` (source: scripts/balance.py) and the duties of the energy streams. Run with
`cheme run scripts/balance.py`; it writes nothing, it prints the values (and, with the
argument `--yaml`, the stream lines of process/flowsheet.yaml).

Inputs (each in DESIGN.md with its source or ASSUMED):
- product: 2 500 kg/h dried sodium nitrite (D-002);
- burner: 10.3 mol-% NH3 in humid air (US 12 565 427 B2), complete NH3 conversion, NO
  selectivity 0.97, N2O from the IPCC 2006 atmospheric-pressure default, rest N2 (D-005);
- absorption: NaNO2 : NaNO3 = 20 : 1 by mass in the absorber liquor (D-006; US 2 032 699
  reports 40 : 1), 99.5 % of the NOx nitrogen absorbed, tail gas water-saturated at 313 K;
- crystallisation: mother liquor 33 wt-% NaNO2, 17 wt-% NaNO3, 1.1 wt-% Na2CO3 (the
  example of US 2 032 699), cake liquid 0.05 kg/kg crystals, recycle 1.5 kg/kg crystals (D-008);
- inversion: the purge's nitrite and carbonate converted completely by 60 wt-% nitric acid,
  the NO returned to the absorbers (US 2 013 984, D-009);
- duties: ideal-gas data of `cheme chemistry thermo` for the burner; standard enthalpies of
  formation of the aqueous salts (NBS tables, Wagman et al. 1982) for the absorption heat;
  evaporator economy, dryer efficiency and machine efficiencies ASSUMED (D-010, D-011).
"""

import sys

M = {"NH3": 17.031, "O2": 31.998, "N2": 28.014, "AR": 39.948, "H2O": 18.015, "NO": 30.006,
     "NO2": 46.005, "N2O": 44.013, "CO2": 44.009, "Na2CO3": 105.988, "NaNO2": 68.995,
     "NaNO3": 84.994, "HNO3": 63.012}
CP = {  # cp/R polynomials, Poling 5th ed. via cheme chemistry thermo
    "NH3": [4.238, -0.004215, 2.041e-05, -2.126e-08, 7.61e-12],
    "O2": [3.63, -0.001794, 6.58e-06, -6e-09, 1.79e-12],
    "N2": [3.539, -0.000261, 7e-08, 1.57e-09, -9.9e-13],
    "AR": [2.5, 0, 0, 0, 0],
    "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
    "NO": [4.534, -0.007644, 2.066e-05, -2.156e-08, 8.06e-12],
    "N2O": [3.165, 0.003401, 9.89e-06, -1.88e-08, 8.9e-12],
    "NO2": [3.32923, 0.00319672, 4.62313e-06, -7.24457e-09, 2.71219e-12],
    "CO2": [3.259, 0.001356, 1.502e-05, -2.374e-08, 1.056e-11],
}
HF = {"NH3": -45558.0, "H2O": -241822.0, "NO": 91089.0, "N2O": 82574.0, "NO2": 34017.0,
      "CO2": -393474.0}  # kJ/kmol ideal gas 298.15 K (ATcT via cheme chemistry thermo)
# aqueous salts and liquid water, kJ/kmol at 298.15 K (NBS tables, Wagman et al. 1982)
HF_AQ = {"NaNO2": -344800.0, "NaNO3": -447480.0, "Na2CO3": -1157380.0, "HNO3": -207360.0}
HF_CR = {"Na2CO3": -1130680.0}
H_VAP_298 = 44004.0         # kJ/kmol water at 298.15 K (H2O(g) - H2O(l), NBS)
R = 8.314462618
T0 = 298.15


def dh(c, t):
    a = CP[c]
    f = lambda x: sum(a[i] * x ** (i + 1) / (i + 1) for i in range(5))
    return R * (f(t) - f(T0))


def gas_h(kmol, t):
    """Ideal-gas enthalpy incl. formation, kJ/h."""
    return sum(n * (HF.get(c, 0.0) + dh(c, t)) for c, n in kmol.items())


def kg(kmol):
    return {c: n * M[c] for c, n in kmol.items() if n > 0}


def kmol(kgs):
    return {c: m / M[c] for c, m in kgs.items() if m > 0}


def tot(d):
    return sum(d.values())


S = {}  # stream id -> (title-free) dict of kg/h, T, p


def put(sid, masses, t, p):
    S[sid] = ({c: v for c, v in masses.items() if v > 1e-9}, t, p)


# --- inputs ---------------------------------------------------------------------------
P_NANO2 = 2500.0            # kg/h dried product (D-002)
W_PROD_H2O = 0.001          # moisture of the dried product (D-002)
Y_NH3 = 0.103               # NH3 in the burner feed, mol (D-005, US 12 565 427 B2)
AIR = {"N2": 0.7734, "O2": 0.2074, "AR": 0.0092, "H2O": 0.0100}  # humid air, mol (D-004)
SEL_NO, SEL_N2O = 0.97, 0.0140  # NH3 fractions to NO and N2O, rest to N2 (D-005)
T_GAS = 473.15              # burner gas after the waste heat boiler (D-005)
LOSS = 0.03                 # heat loss of burner and WHB, fraction of heat released (D-005)
RATIO = 20.0                # NaNO2 : NaNO3 by mass formed in the absorbers (D-006)
ABS_EFF = 0.995             # fraction of the NOx nitrogen absorbed (D-006)
T_ABS = 313.15              # absorber liquor and tail gas (D-006)
P_TAIL = 105.0              # kPa(a), tail gas at the stack inlet
PSAT_ABS = 7.385            # kPa, water at 313.15 K (IAPWS-IF97)
W_SODA = 0.20               # Na2CO3 in the soda solution (D-006)
ML = {"NaNO2": 0.33, "NaNO3": 0.17, "Na2CO3": 0.011}  # mother liquor, mass (D-008)
CAKE_LIQ = 0.05             # kg mother liquor per kg crystals (D-008)
RECYCLE = 1.5               # kg mother liquor recycled to E301 per kg crystals (D-008)
W_HNO3 = 0.60               # nitric acid from nitric-acid-1 (D-009)
NO3_ML = 0.51               # NaNO3 in the NaNO3 cake liquor, saturated near 313 K (D-009)

# --- sodium nitrite crystallisation: product, cake, mother liquor -----------------------
ml_w = 1.0 - sum(ML.values())
dry_salts_per_crystal = 1.0 + CAKE_LIQ * sum(ML.values())
crystals = P_NANO2 * (1 - W_PROD_H2O) / dry_salts_per_crystal
adh = CAKE_LIQ * crystals
prod = {"NaNO2": crystals + adh * ML["NaNO2"], "NaNO3": adh * ML["NaNO3"],
        "Na2CO3": adh * ML["Na2CO3"]}
prod["H2O"] = P_NANO2 * W_PROD_H2O
cake = {"NaNO2": crystals + adh * ML["NaNO2"], "NaNO3": adh * ML["NaNO3"],
        "Na2CO3": adh * ML["Na2CO3"], "H2O": adh * ml_w}
dryer_vap = cake["H2O"] - prod["H2O"]

# nitrate balance: formed in absorption = in the cake + in the purge; nitrite formed = cake
# nitrite + purge nitrite. x = NaNO2 formed (kg/h): x/RATIO = cake_no3 + purge*ML_no3,
# x = cake_no2 + purge*ML_no2
purge = (cake["NaNO2"] / RATIO - cake["NaNO3"]) / (ML["NaNO3"] - ML["NaNO2"] / RATIO)
no2_formed = cake["NaNO2"] + purge * ML["NaNO2"]
no3_formed = no2_formed / RATIO
purge_kg = {c: purge * w for c, w in ML.items()}
purge_kg["H2O"] = purge * ml_w
recycle_kg = {c: RECYCLE * crystals * w for c, w in ML.items()}
recycle_kg["H2O"] = RECYCLE * crystals * ml_w

# --- inversion (R401) -------------------------------------------------------------------
n_no2_p = purge_kg["NaNO2"] / M["NaNO2"]
n_co3_p = purge_kg["Na2CO3"] / M["Na2CO3"]
x_inv = n_no2_p / 3.0       # 3 NaNO2 + 2 HNO3 -> 3 NaNO3 + 2 NO + H2O
x_neu = n_co3_p             # Na2CO3 + 2 HNO3 -> 2 NaNO3 + CO2 + H2O
n_hno3 = 2 * x_inv + 2 * x_neu
acid = {"HNO3": n_hno3 * M["HNO3"]}
acid["H2O"] = acid["HNO3"] / W_HNO3 * (1 - W_HNO3)
inv_gas = kg({"NO": 2 * x_inv, "CO2": x_neu})
inv_liq = {"NaNO3": purge_kg["NaNO3"] + (3 * x_inv + 2 * x_neu) * M["NaNO3"],
           "H2O": purge_kg["H2O"] + acid["H2O"] + (x_inv + x_neu) * M["H2O"]}
# NaNO3 crystallisation (CR401) and drying (D401)
no3_cryst = inv_liq["NaNO3"] / (1 + CAKE_LIQ * NO3_ML)
no3_cake = {"NaNO3": inv_liq["NaNO3"], "H2O": CAKE_LIQ * no3_cryst * (1 - NO3_ML)}
no3_vap = inv_liq["H2O"] - no3_cake["H2O"]
no3_prod = {"NaNO3": inv_liq["NaNO3"]}
no3_prod["H2O"] = no3_prod["NaNO3"] / (1 - W_PROD_H2O) * W_PROD_H2O
no3_dry_vap = no3_cake["H2O"] - no3_prod["H2O"]

# --- absorption (C201) ------------------------------------------------------------------
n_no2f = no2_formed / M["NaNO2"]
n_no3f = no3_formed / M["NaNO3"]
x_b = n_no3f                         # Na2CO3 + 2 NO2 -> NaNO2 + NaNO3 + CO2
x_a = (n_no2f - x_b) / 2.0           # Na2CO3 + NO + NO2 -> 2 NaNO2 + CO2
n_N_abs = n_no2f + n_no3f
n_N_in = n_N_abs / ABS_EFF
n_no_burner = n_N_in - 2 * x_inv     # NO from the burner (the rest is the inversion NO)
n_nh3 = n_no_burner / SEL_NO
n_air = n_nh3 / Y_NH3 * (1 - Y_NH3)
air = {c: n_air * y for c, y in AIR.items()}
# burner R101
r_no, r_n2o = SEL_NO * n_nh3, SEL_N2O * n_nh3
r_n2 = n_nh3 - r_no - r_n2o
gas = dict(air)
gas["O2"] -= 1.25 * r_no + 1.0 * r_n2o + 0.75 * r_n2
gas["H2O"] += 1.5 * n_nh3
gas["NO"] = r_no
gas["N2O"] = r_n2o / 2
gas["N2"] += r_n2 / 2
# air blower K101: S3 288.15 K, 101.3 -> 131.3 kPa(a), isentropic eta 0.75, no aftercooler (D-011)
T_K101_IN, ETA_K101 = 288.15, 0.75
t_s4 = T_K101_IN * (1 + ((131.3 / 101.3) ** (1 / 3.5) - 1) / ETA_K101)
h_in = gas_h({"NH3": n_nh3}, T0) + gas_h(air, t_s4)     # S2 298.15 K, S4 after the blower
h_release = h_in - gas_h(gas, T0)
h_out = gas_h(gas, T_GAS)
q_steam = (h_in - h_out - LOSS * h_release) / 3600.0
# absorbers: NO2 needed = x_a + 2 x_b, from NO + 1/2 O2; tail NOx as NO
n_no2_needed = x_a + 2 * x_b
n_co3 = x_a + x_b + (cake["Na2CO3"] + purge_kg["Na2CO3"]) / M["Na2CO3"]
soda = {"Na2CO3": n_co3 * M["Na2CO3"]}
soda_sol = {"Na2CO3": soda["Na2CO3"], "H2O": soda["Na2CO3"] / W_SODA * (1 - W_SODA)}
tail = {"N2": gas["N2"], "AR": gas["AR"], "N2O": gas["N2O"],
        "O2": gas["O2"] - n_no2_needed / 2 - 0.0,
        "NO": n_N_in - n_N_abs, "CO2": x_a + x_b + x_neu}
dry = sum(tail.values())
y_w = PSAT_ABS / P_TAIL
tail["H2O"] = y_w / (1 - y_w) * dry
liq_out = {"NaNO2": no2_formed, "NaNO3": no3_formed,
           "Na2CO3": cake["Na2CO3"] + purge_kg["Na2CO3"]}
water_in = gas["H2O"] * M["H2O"] + soda_sol["H2O"]
liq_out["H2O"] = water_in - tail["H2O"] * M["H2O"]
# heat removed in C201 (to 313 K): gas cooling, condensation, NO oxidation, absorption
gas_abs_in = dict(gas)
for c, v in kmol(inv_gas).items():
    gas_abs_in[c] = gas_abs_in.get(c, 0.0) + v
h_gas_in = gas_h(gas_abs_in, T_GAS) - gas_h(gas_abs_in, T0)
cond = gas["H2O"] - tail["H2O"]
dH_noox = 0.5 * (2 * HF["NO2"] - 2 * HF["NO"])     # per kmol NO2 formed
dH_a = 2 * HF_AQ["NaNO2"] + HF["CO2"] - HF_AQ["Na2CO3"] - HF["NO"] - HF["NO2"]
dH_b = HF_AQ["NaNO2"] + HF_AQ["NaNO3"] + HF["CO2"] - HF_AQ["Na2CO3"] - 2 * HF["NO2"]
q_rxn = -(n_no2_needed * dH_noox + x_a * dH_a + x_b * dH_b)
# soda dissolver T201, adiabatic: condensate S7 333 K, soda 298 K and the heat of solution
# of Na2CO3 give S8; C201 cools the solution to T_ABS (D-006, D-010)
dH_sol = HF_AQ["Na2CO3"] - HF_CR["Na2CO3"]
CP_SODA = 3.6               # kJ/kg K, 20 wt-% Na2CO3 solution (ASSUMED)
t_s8 = 298.15 + (soda_sol["H2O"] * 4.18 * (333.15 - 298.15) - n_co3 * dH_sol) / (tot(soda_sol) * CP_SODA)
q_soda = tot(soda_sol) * CP_SODA * (t_s8 - T_ABS)
q_c201 = (h_gas_in + cond * H_VAP_298 + q_rxn + q_soda) / 3600.0   # kW, 313 vs 298 K neglected

# --- evaporation and NaNO2 crystallisation (E301, CR301) ---------------------------------
ml_total = adh + RECYCLE * crystals + purge
conc = {"NaNO2": crystals + ml_total * ML["NaNO2"], "NaNO3": ml_total * ML["NaNO3"],
        "Na2CO3": ml_total * ML["Na2CO3"], "H2O": ml_total * ml_w}
evap_in = {c: liq_out.get(c, 0) + recycle_kg.get(c, 0) for c in conc}
evap = evap_in["H2O"] - conc["H2O"]
cond_to_t201 = soda_sol["H2O"]
cond_excess = evap - cond_to_t201
LAT = 2257.0                # kJ/kg (latent heat at 373 K; D-010)
# E301 double effect, backward feed (D-010): the feed enters effect 2 under vacuum, the
# concentrate leaves effect 1 at 398 K / 120 kPa(a), whose calandria takes the WHB and LP steam
# (420.8 K at 450 kPa(a), 22.6 K above the boiling liquor). BPE, approach and cp ASSUMED.
BPE1, BPE2 = 20.0, 8.0      # K, near-saturated concentrate / effect-2 liquor (D-010)
T1 = 398.15                 # effect 1 boiling liquor = S12; vapour saturated at 120 kPa 377.95 K
T2 = 377.95 - 10.0          # effect 2 boiling liquor, 10 K below the effect-1 vapour
TV2 = T2 - BPE2             # effect-2 vapour 360.15 K, saturated at about 63 kPa(a)
H_V1 = 2243.0 + 1.9 * BPE1  # kJ/kg effect-1 vapour (latent at 377.95 K plus superheat, IAPWS)
H_V2 = 2290.0 + 1.9 * BPE2  # kJ/kg effect-2 vapour (latent at 360.15 K plus superheat)
CP_FEED, CP_MID = 3.3, 3.0  # kJ/kg K, feed liquor and effect-2 liquor (ASSUMED)
f_e301 = tot(evap_in)
v1 = evap / 2
for _ in range(50):         # condensate (V1 at 377.95 K, V2 at TV2) preheats the feed to S13 333 K
    t_cond = (v1 * 377.95 + (evap - v1) * TV2) / evap
    q_pre = evap * 4.19 * (t_cond - 333.15)
    t_pre = 318.15 + q_pre / (f_e301 * CP_FEED)
    v1 = (f_e301 * CP_FEED * (T2 - t_pre) + evap * H_V2) / (H_V1 + H_V2)
v2 = evap - v1
q_e301 = ((f_e301 - v2) * CP_MID * (T1 - T2) + v1 * H_V1) / 3600.0
q_e301_cw = v2 * H_V2 / 3600.0                      # effect-2 vapour to the condenser
ECONOMY = evap * LAT / 3600.0 / q_e301              # kg water per kg steam at 2 257 kJ/kg
# CR301 cooling crystalliser: concentrate 398 K -> 328 K (cp 2.8 kJ/kg K) plus heat of
# crystallisation (NaNO2: dHsol 13.9 MJ/kmol, NBS cr vs aq)
CP_LIQ = 2.8
q_cr301 = (tot(conc) * CP_LIQ * (398.15 - 328.15) + crystals / M["NaNO2"] * 13850.0) / 3600.0
q_d301 = dryer_vap * 2500.0 / 0.5 / 3600.0          # dryer efficiency 0.5 (D-010)
# NaNO3 side
q_cr401 = no3_vap * LAT / 1.0 / 3600.0               # single effect (D-010)
q_cr401_cw = no3_vap * 2380.0 / 3600.0
q_d401 = no3_dry_vap * 2500.0 / 0.5 / 3600.0
# NH3 vaporiser E101: liquid 288 K, 1600 kPa -> vapour 298 K, latent ~1180 kJ/kg (D-010)
q_e101 = n_nh3 * M["NH3"] * (1180.0 + 2.2 * 10) / 3600.0
w_k101 = n_air / 3600 * R * T_K101_IN * 3.5 * ((131.3 / 101.3) ** (1 / 3.5) - 1) / ETA_K101
POWER = {"K101": w_k101, "C201": 30.0, "E301": 15.0, "CR301": 25.0, "D301": 15.0,
         "R401": 5.0, "CR401": 10.0, "D401": 5.0}       # ASSUMED (D-011)

# --- streams ----------------------------------------------------------------------------
put("S1", kg({"NH3": n_nh3}), 288.15, 1600.0)
put("S2", kg({"NH3": n_nh3}), 298.15, 400.0)
put("S3", kg(air), 288.15, 101.3)
put("S4", kg(air), round(t_s4, 2), 131.3)
put("S5", kg(gas), T_GAS, 120.0)
put("S6", soda, 298.15, 101.3)
put("S7", {"H2O": cond_to_t201}, 333.15, 300.0)
put("S8", soda_sol, round(t_s8, 2), 300.0)
put("S9", liq_out, T_ABS, 300.0)
put("S10", kg(tail), T_ABS, P_TAIL)
put("S11", {c: evap_in[c] for c in conc}, 318.15, 300.0)
put("S12", conc, 398.15, 120.0)
put("S13", {"H2O": evap}, 333.15, 300.0)
put("S14", {"H2O": cond_excess}, 333.15, 300.0)
put("S15", cake, 328.15, 101.3)
put("S16", recycle_kg, 328.15, 300.0)
put("S17", purge_kg, 328.15, 300.0)
put("S18", prod, 323.15, 101.3)
put("S19", {"H2O": dryer_vap}, 353.15, 101.3)
put("S20", acid, 313.15, 300.0)
put("S21", inv_gas, 333.15, 130.0)
put("S22", inv_liq, 333.15, 300.0)
put("S23", no3_cake, 313.15, 101.3)
put("S24", {"H2O": no3_vap}, 333.15, 101.3)
put("S25", no3_prod, 323.15, 101.3)
put("S26", {"H2O": no3_dry_vap}, 353.15, 101.3)

DUTY = {"Q1": q_steam, "Q2": q_e101, "Q3": w_k101, "Q4": q_c201, "Q5": POWER["C201"],
        "Q6": q_e301 - q_steam, "Q7": q_e301_cw, "Q8": POWER["E301"], "Q9": q_cr301,
        "Q10": POWER["CR301"], "Q11": q_d301, "Q12": POWER["D301"], "Q13": POWER["R401"],
        "Q14": q_cr401, "Q15": q_cr401_cw, "Q16": POWER["CR401"], "Q17": q_d401,
        "Q18": POWER["D401"]}


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


# the values process/flowsheet.yaml cites from this script (balance-output contract): S and DUTY
write_balance_output({"design": {
    **{sid: {"temperature": t, "pressure": p, "flow": {"value": tot(m), "basis": "mass"},
             "composition": {"values": {c: v / tot(m) for c, v in m.items()},
                             "basis": "mass_fraction"}}
       for sid, (m, t, p) in S.items()},
    **{q: {"duty": v} for q, v in DUTY.items()}}})

if "--yaml" in sys.argv:
    for sid, (m, t, p) in S.items():
        f = tot(m)
        w = {c: round(v / f, 7) for c, v in m.items()}
        print(f"{sid}: T {t} p {p} flow {f:.2f} comp {w}")
    for q, v in DUTY.items():
        print(f"{q}: {v:.1f} kW")
    sys.exit(0)

print(f"crystals {crystals:.1f} kg/h, adhering ML {adh:.1f}, purge {purge:.1f}, recycle "
      f"{RECYCLE * crystals:.1f}")
print(f"NaNO2 formed {no2_formed:.1f} kg/h, NaNO3 formed {no3_formed:.1f} kg/h")
print(f"product {prod} = {tot(prod):.1f} kg/h; NaNO2 purity {prod['NaNO2'] / tot(prod):.5f}")
print(f"NH3 {n_nh3 * M['NH3']:.2f} kg/h ({n_nh3:.3f} kmol/h), air {n_air:.2f} kmol/h "
      f"= {tot(kg(air)):.1f} kg/h")
print(f"burner gas {gas}")
print(f"heat released {h_release / 3600:.1f} kW, outlet sensible {(h_out - gas_h(gas, T0)) / 3600:.1f} kW, "
      f"steam duty {q_steam:.1f} kW")
print(f"absorber: x_a {x_a:.3f}, x_b {x_b:.3f}, NO2 needed {n_no2_needed:.3f} kmol/h, "
      f"NO/NO2 to absorbers {(gas_abs_in['NO'] - n_no2_needed) / n_no2_needed:.3f} after oxidation")
print(f"tail gas kmol/h {tail}; NOx {tail['NO'] / dry * 1e6:.0f} ppmv dry, "
      f"O2 {tail['O2'] / dry * 100:.2f} vol-% dry, N2O {tail['N2O'] / dry * 1e6:.0f} ppmv")
print(f"soda {soda['Na2CO3']:.1f} kg/h, solution {tot(soda_sol):.1f}; liquor {tot(liq_out):.1f} "
      f"kg/h, NaNO2 {liq_out['NaNO2'] / tot(liq_out):.4f}")
print(f"C201: gas sensible {h_gas_in / 3600:.1f} kW, condensation {cond * H_VAP_298 / 3600:.1f} kW, "
      f"reactions {q_rxn / 3600:.1f} kW (dH_a {dH_a:.0f}, dH_b {dH_b:.0f} kJ/kmol)")
print(f"evaporation {evap:.1f} kg/h, condensate to T201 {cond_to_t201:.1f}, excess {cond_excess:.1f}")
print(f"E301: feed {f_e301:.1f} kg/h preheated to {t_pre:.1f} K ({q_pre / 3600:.1f} kW from condensate), "
      f"V1 {v1:.1f}, V2 {v2:.1f} kg/h, steam {q_e301:.1f} kW, economy {ECONOMY:.2f}, condenser {q_e301_cw:.1f} kW")
print(f"K101 outlet {t_s4:.2f} K; T201 outlet S8 {t_s8:.2f} K, C201 soda cooling {q_soda / 3600:.1f} kW")
print(f"inversion: HNO3 {acid['HNO3']:.2f} kg/h ({tot(acid):.2f} kg/h acid), gas {inv_gas}, "
      f"NaNO3 product {tot(no3_prod):.2f} kg/h")
print(f"soda dissolution heat {n_co3 * dH_sol / 3600:.1f} kW")
for q, v in DUTY.items():
    print(f"{q}: {v:.1f} kW")
# balances
ins = tot(S["S1"][0]) + tot(S["S3"][0]) + tot(S["S6"][0]) + tot(S["S20"][0])
outs = sum(tot(S[s][0]) for s in ["S10", "S14", "S18", "S19", "S24", "S25", "S26"])
print(f"overall mass in {ins:.2f}, out {outs:.2f}, diff {ins - outs:.4f} kg/h")
EL = {"NH3": {"N": 1, "H": 3}, "O2": {"O": 2}, "N2": {"N": 2}, "AR": {"Ar": 1},
      "H2O": {"H": 2, "O": 1}, "NO": {"N": 1, "O": 1}, "NO2": {"N": 1, "O": 2},
      "N2O": {"N": 2, "O": 1}, "CO2": {"C": 1, "O": 2},
      "Na2CO3": {"Na": 2, "C": 1, "O": 3}, "NaNO2": {"Na": 1, "N": 1, "O": 2},
      "NaNO3": {"Na": 1, "N": 1, "O": 3}, "HNO3": {"H": 1, "N": 1, "O": 3}}


def el(sids):
    e = {}
    for s in sids:
        for c, n in kmol(S[s][0]).items():
            for k, a in EL[c].items():
                e[k] = e.get(k, 0) + a * n
    return e


ei, eo = el(["S1", "S3", "S6", "S20"]), el(["S10", "S14", "S18", "S19", "S24", "S25", "S26"])
for k in ei:
    print(f"element {k}: in {ei[k]:.4f}, out {eo.get(k, 0):.4f} kmol/h")
