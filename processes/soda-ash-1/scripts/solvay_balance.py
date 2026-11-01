"""Heat and material balance of the Solvay soda ash plant (soda-ash-1), concept stage.

An independent sequential balance on a component basis (no electrolyte thermodynamics: core
cannot yet speciate NH3-CO2-NaCl-H2O liquors). Dissolved ammonia and carbon dioxide
are carried as NH3 and CO2; "free" ammonia in the mother liquor is ammonium bicarbonate
(NH3 + CO2 + H2O, molar ratio CO2/free NH3 = 1). Every design parameter below is ASSUMED unless
its comment names a source; DESIGN.md D-006 lists them with the reasons.

Run: cheme run scripts/solvay_balance.py (or python3, it needs nothing beyond the standard
library). It prints the streams (kg/h, mass fractions), the duties (kW), the element balance
of every unit and the specific consumptions per t of soda ash; process/flowsheet.yaml carries
these values as ASSUMED with this script as their source.
"""

from __future__ import annotations

import json
import sys

# kg/kmol (IUPAC 2021 standard atomic weights)
MW = {
    "H2O": 18.015, "NaCl": 58.443, "NH3": 17.031, "CO2": 44.010, "NH4Cl": 53.491,
    "CaCl2": 110.984, "N2": 28.014, "O2": 31.998, "NaHCO3": 84.007, "Na2CO3": 105.988,
    "CaCO3": 100.087, "CaO": 56.077, "CaOH2": 74.093, "SiO2": 60.084, "C": 12.011,
}
ELEMENTS = {
    "H2O": {"H": 2, "O": 1}, "NaCl": {"Na": 1, "Cl": 1}, "NH3": {"N": 1, "H": 3},
    "CO2": {"C": 1, "O": 2}, "NH4Cl": {"N": 1, "H": 4, "Cl": 1}, "CaCl2": {"Ca": 1, "Cl": 2},
    "N2": {"N": 2}, "O2": {"O": 2}, "NaHCO3": {"Na": 1, "H": 1, "C": 1, "O": 3},
    "Na2CO3": {"Na": 2, "C": 1, "O": 3}, "CaCO3": {"Ca": 1, "C": 1, "O": 3},
    "CaO": {"Ca": 1, "O": 1}, "CaOH2": {"Ca": 1, "O": 2, "H": 2}, "SiO2": {"Si": 1, "O": 2},
    "C": {"C": 1},
}

# --- design parameters (D-002, D-006) ----------------------------------------------------------
PRODUCT = 1000e3 / 24          # kg/h light soda ash, 1000 t/d (D-002, ASSUMED capacity)
W_NA2CO3 = 0.995               # product Na2CO3 mass fraction, rest NaCl (D-002, ASSUMED grade)
U_NA = 0.73                    # sodium utilisation of the carbonating towers (D-006, ASSUMED)
W_BRINE = 0.26                 # NaCl mass fraction of the purified brine (D-003, ASSUMED)
R_NH3 = 1.10                   # NH3/NaCl mol/mol in the ammoniated brine (D-006, ASSUMED)
F_GAS_NH3 = 0.01               # NH3 of the ammoniated brine leaving with the tower gas (ASSUMED)
NH3_VENT = 0.5                 # kg NH3 per t soda ash to the vent (ASSUMED)
NH3_WASTE = 1.5                # kg NH3 per t soda ash in the distiller waste (ASSUMED)
CAKE_LIQ = 0.15                # liquid mass fraction of the washed wet cake (ASSUMED)
CAKE_NH3 = 0.003               # NH3 mass fraction of the wet cake (as NH4HCO3, ASSUMED)
WASH = 0.30                    # wash water, kg per kg dry cake (ASSUMED)
LIME_EXCESS = 0.05             # Ca(OH)2 over the NH4Cl stoichiometry (ASSUMED)
CALC = 0.95                    # degree of calcination (process/furnaces.yaml)
LIMESTONE = {"CaCO3": 0.96, "SiO2": 0.03, "H2O": 0.01}   # mass fractions (D-005, ASSUMED)
COKE = {"C": 0.89, "SiO2": 0.09, "H2O": 0.02}            # mass fractions, ash as SiO2 (D-005)
KILN_HEAT = 29498.2            # kW, cheme process furnace KILN (4.0 GJ/t lime, BREF fallback)
COKE_LHV = 29110.0             # kJ/kg (process/furnaces.yaml)
LAMBDA = 1.10                  # kiln air excess (D-004, ASSUMED)
MILK_SOLIDS = 0.20             # Ca(OH)2 mass fraction of the milk of lime (ASSUMED)
DIST_H2O_NH3 = 0.6             # H2O/NH3 mol/mol of the distiller gas after its condenser (ASSUMED)
P_SAT = {303.15: 4.25, 313.15: 7.38}   # kPa, water vapour pressure (steam tables)

# heats of reaction, MJ/kmol, at 298 K from standard enthalpies of formation (NBS tables,
# Wagman et al. 1982; values to be checked against the table, D-007)
DH_CARB = -83.6       # NaCl(aq) + NH3(aq) + CO2(g) + H2O(l) -> NaHCO3(s) + NH4Cl(aq)
DH_NH3_ABS = -34.4    # NH3(g) -> NH3(aq)
DH_BICARB_AQ = -64.9  # NH3(aq) + CO2(g) + H2O(l) -> NH4HCO3(aq)
DH_DIST = 44.1        # Ca(OH)2(s) + 2 NH4Cl(aq) -> CaCl2(aq) + 2 NH3(g) + 2 H2O(l)
DH_CALC_BICARB = 135.6  # 2 NaHCO3(s) -> Na2CO3(s) + CO2(g) + H2O(g)
DH_VAP = 43.99        # H2O(l) -> H2O(g) at 298 K
CP_LIQ = 3.6          # kJ/(kg K), liquors (ASSUMED)
CP_SOLID = 1.1        # kJ/(kg K), soda ash and bicarbonate (ASSUMED)
CP_GAS = {"CO2": 0.037, "H2O": 0.034, "N2": 0.029, "O2": 0.030, "NH3": 0.036}  # MJ/(kmol K)
ETA = 0.75            # compressor isentropic efficiency (ASSUMED)
P_TOWER = 350.0       # kPa(a), gas to the carbonating towers (ASSUMED)
AUX_POWER = 35.0      # kWh/t soda ash: pumps, vacuum pumps, conveyors, fans, drives (ASSUMED)
H_LPS = 2744.0 - 461.3  # kJ/kg: saturated LP steam 450 kPa(a) condensing into liquor at 383 K
CALC_LOSS = 0.10      # calciner heat losses, fraction of its duty (ASSUMED)
DIST_LOSS = 0.05      # distiller heat losses (ASSUMED)


def kmol(d):
    return {k: v / MW[k] for k, v in d.items()}


def mass(d):
    return {k: v * MW[k] for k, v in d.items()}


def total(d):
    return sum(d.values())


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def elements(dm):
    out = {}
    for k, v in kmol(dm).items():
        for e, n in ELEMENTS[k].items():
            out[e] = out.get(e, 0.0) + n * v
    return out


def compressor_kw(n_kmol_h, t_in, p_in, p_out, k):
    """Adiabatic compression power, ideal gas, kW."""
    r = 8.314
    w = n_kmol_h / 3600 * r * t_in * k / (k - 1) * ((p_out / p_in) ** ((k - 1) / k) - 1)
    return w / ETA


S = {}   # stream id -> component kg/h
Q = {}   # energy stream id -> kW

# --- product and calciner ---------------------------------------------------------------------
n_na2co3 = PRODUCT * W_NA2CO3 / MW["Na2CO3"]
n_ppt = 2 * n_na2co3                                  # NaHCO3 precipitated = to the calciner
S["S19"] = {"Na2CO3": PRODUCT * W_NA2CO3, "NaCl": PRODUCT * (1 - W_NA2CO3)}
# wet cake: NaHCO3 + liquid (water, the product's NaCl, NH3 + CO2 as NH4HCO3)
m_bicarb = n_ppt * MW["NaHCO3"]
m_wet = m_bicarb / (1 - CAKE_LIQ)
a = CAKE_NH3 * m_wet / MW["NH3"]                      # kmol/h NH3 (= CO2) in the cake liquid
cake_liq = {"NaCl": S["S19"]["NaCl"], "NH3": a * MW["NH3"], "CO2": a * MW["CO2"]}
cake_liq["H2O"] = m_wet * CAKE_LIQ - total(cake_liq)
S["S18"] = add({"NaHCO3": m_bicarb}, cake_liq)
# calciner gas: CO2 and H2O of the reaction, the cake liquid's water, NH3 and CO2
S["S14"] = mass({"CO2": n_na2co3 + a, "H2O": n_na2co3 + cake_liq["H2O"] / MW["H2O"], "NH3": a})
# condenser: the gas keeps CO2 with water at saturation (313 K, 101.3 kPa); NH3, an equimolar
# CO2 and the rest of the water to the weak liquor
n_co2_gas = n_na2co3
n_h2o_gas = n_co2_gas * P_SAT[313.15] / (101.325 - P_SAT[313.15])
S["S15"] = mass({"CO2": n_co2_gas, "H2O": n_h2o_gas})
S["S22"] = {k: S["S14"].get(k, 0) - S["S15"].get(k, 0) for k in S["S14"]}
S["S16"] = dict(S["S15"])                               # compressed calciner CO2

# --- sodium, brine ------------------------------------------------------------------------------
n_nacl = n_ppt / U_NA
S["S8"] = {"NaCl": n_nacl * MW["NaCl"], "H2O": n_nacl * MW["NaCl"] * (1 - W_BRINE) / W_BRINE}

# --- kiln and slaker ----------------------------------------------------------------------------
n_caoh2 = n_ppt / 2 * (1 + LIME_EXCESS)
n_caco3 = n_caoh2 / CALC
m_ls = n_caco3 * MW["CaCO3"] / LIMESTONE["CaCO3"]
S["S1"] = {k: m_ls * w for k, w in LIMESTONE.items()}
m_coke = KILN_HEAT * 3600 / COKE_LHV
S["S2"] = {k: m_coke * w for k, w in COKE.items()}
n_c = S["S2"]["C"] / MW["C"]
n_o2 = LAMBDA * n_c
S["S3"] = mass({"O2": n_o2, "N2": n_o2 * 0.7905 / 0.2095})   # dry air, Ar counted as N2
S["S4"] = {"CaO": n_caoh2 * MW["CaO"], "CaCO3": (n_caco3 - n_caoh2) * MW["CaCO3"],
           "SiO2": S["S1"]["SiO2"] + S["S2"]["SiO2"]}
S["S5"] = mass({"CO2": n_caoh2 + n_c, "O2": n_o2 - n_c, "N2": S["S3"]["N2"] / MW["N2"],
                "H2O": (S["S1"]["H2O"] + S["S2"]["H2O"]) / MW["H2O"]})
S["S5B"] = dict(S["S5"])   # cooled kiln gas
S["S5C"] = dict(S["S5"])   # compressed kiln gas
m_milk = n_caoh2 * MW["CaOH2"] / MILK_SOLIDS
S["S7"] = {"CaOH2": n_caoh2 * MW["CaOH2"], "CaCO3": S["S4"]["CaCO3"], "SiO2": S["S4"]["SiO2"]}
S["S7"]["H2O"] = m_milk - total(S["S7"])
S["S6"] = {"H2O": S["S7"]["H2O"] + n_caoh2 * MW["H2O"]}

# --- ammonia loop ---------------------------------------------------------------------------------
n_N = R_NH3 * n_nacl                                  # NH3 in the ammoniated brine
g = F_GAS_NH3 * n_N                                   # NH3 with the tower gas
vent_nh3 = NH3_VENT * PRODUCT / 1000 / MW["NH3"]
waste_nh3 = NH3_WASTE * PRODUCT / 1000 / MW["NH3"]
free = n_N - n_ppt - g                                # free NH3 in the tower mother liquor
c_ab = free                                           # CO2 of the ammoniated brine (CO2/free NH3 = 1)
dist_nh3 = n_N - g - waste_nh3
S["S10"] = {"NH3": (vent_nh3 + waste_nh3) * MW["NH3"]}   # make-up = losses
S["S9"] = mass({"NH3": dist_nh3, "CO2": c_ab, "H2O": DIST_H2O_NH3 * dist_nh3})

# --- carbonating towers -------------------------------------------------------------------------
gas_in = add(S["S5C"], S["S16"])
n_gas_in = kmol(gas_in)
co2_out = n_gas_in["CO2"] - n_ppt                     # CO2 absorbed = NaHCO3 formed (c_ab circulates)
dry = {"CO2": co2_out, "N2": n_gas_in["N2"], "O2": n_gas_in["O2"], "NH3": g}
n_h2o_exit = total(dry) * P_SAT[303.15] / (101.325 - P_SAT[303.15])
S["S12"] = mass(add(dry, {"H2O": n_h2o_exit}))
# scrubber: brine takes the tower gas NH3 down to the vent loss; the water of the gas is kept
S["S13"] = mass({"CO2": co2_out, "N2": dry["N2"], "O2": dry["O2"], "NH3": vent_nh3,
                 "H2O": n_h2o_exit})
S["S8B"] = add(S["S8"], {"NH3": (g - vent_nh3) * MW["NH3"]})
S["S11"] = add(S["S8B"], S["S9"], S["S10"])           # ammoniated brine
# slurry: what enters minus the exit gas, the CARB reaction NaCl+NH3+CO2+H2O -> NaHCO3+NH4Cl
tower_in = kmol(add(S["S11"], gas_in))
tower_out_gas = kmol(S["S12"])
sl = {k: tower_in.get(k, 0) - tower_out_gas.get(k, 0) for k in tower_in}
for k in ("NaCl", "NH3", "CO2", "H2O"):
    sl[k] -= n_ppt
sl["NaHCO3"] = n_ppt
sl["NH4Cl"] = n_ppt
S["S17"] = mass({k: v for k, v in sl.items() if abs(v) > 1e-9})

# --- filter -------------------------------------------------------------------------------------
S["S20"] = {"H2O": WASH * m_bicarb}
fil_in = add(S["S17"], S["S20"])
S["S21"] = {k: fil_in[k] - S["S18"].get(k, 0) for k in fil_in if k != "NaHCO3"}

# --- distiller ----------------------------------------------------------------------------------
d_in = kmol(add(S["S21"], S["S22"], S["S7"]))
waste = {
    "CaCl2": n_ppt / 2,
    "CaOH2": d_in["CaOH2"] - n_ppt / 2,
    "CaCO3": d_in["CaCO3"], "SiO2": d_in["SiO2"],
    "NaCl": d_in["NaCl"], "NH3": waste_nh3,
}
# all water not in the distiller gas, plus the live steam and the reaction water
# (the live steam is solved from the energy balance below)
dist_gas = kmol(S["S9"])


def distiller_steam():
    t_out = 383.15
    q = (total(S["S21"]) * CP_LIQ * (t_out - 303.15) + total(S["S22"]) * CP_LIQ * (t_out - 313.15)
         + total(S["S7"]) * CP_LIQ * (t_out - 353.15)) / 1000   # MJ/h
    q += c_ab * (-DH_BICARB_AQ) + (dist_nh3 - n_ppt - c_ab) * (-DH_NH3_ABS)
    q += n_ppt / 2 * DH_DIST
    q += dist_gas["H2O"] * DH_VAP
    q *= 1 + DIST_LOSS
    return q / 3600 * 1000, q * 1000 / H_LPS            # kW, kg/h steam


Q_DIST, m_lps = distiller_steam()
S["S23"] = {"H2O": m_lps}
h2o_in = d_in["H2O"] + m_lps / MW["H2O"] + n_ppt          # 2 H2O per Ca(OH)2 reacted
waste["H2O"] = h2o_in - dist_gas["H2O"]
S["S24"] = mass(waste)

# --- duties -------------------------------------------------------------------------------------
n5 = kmol(S["S5"])
Q["Q1"] = compressor_kw(total(n5), 313.15, 101.325, P_TOWER, 1.35)        # K-101 power
Q["Q2"] = Q["Q1"]                                                          # K-101 aftercooler
Q["Q3"] = compressor_kw(total(kmol(S["S15"])), 313.15, 101.325, P_TOWER, 1.29)   # K-501
Q["Q4"] = Q["Q3"]
Q["Q5"] = AUX_POWER * PRODUCT / 1000                                       # auxiliaries
# kiln gas cooler 393 -> 313 K
Q["Q6"] = sum(n5[k] * CP_GAS[k] for k in n5) * 80 / 3.6
# absorber: NH3 and CO2 absorption, water condensation, gas 333 -> 313 K, brine 293 -> 313 K
q_abs = (dist_nh3 + kmol(S["S10"])["NH3"]) * -DH_NH3_ABS + c_ab * -DH_BICARB_AQ \
    + dist_gas["H2O"] * DH_VAP
q_abs += sum(dist_gas[k] * CP_GAS[k] for k in dist_gas) * 20
q_abs -= total(S["S8B"]) * CP_LIQ * 20 / 1000
Q["Q7"] = q_abs / 3.6
# towers: CARB, liquor 313 -> 303 K, gas to 303 K, water evaporated into the exit gas
n_gin = kmol(gas_in)
q_t = n_ppt * -DH_CARB + total(S["S11"]) * CP_LIQ * 10 / 1000 \
    + sum(n_gin[k] * CP_GAS[k] for k in n_gin) * 10 \
    - (n_h2o_exit - n_gin["H2O"]) * DH_VAP
Q["Q8"] = q_t / 3.6
# calciner: reaction, cake water and NH4HCO3 out, product 303 -> 433 K, gas to 423 K, losses
q_c = n_na2co3 * DH_CALC_BICARB + cake_liq["H2O"] / MW["H2O"] * DH_VAP + a * 99.3 \
    + total(S["S19"]) * CP_SOLID * 130 / 1000 \
    + sum(kmol(S["S14"])[k] * CP_GAS[k] for k in S["S14"]) * 125
Q["Q9"] = q_c * (1 + CALC_LOSS) / 3.6
# calciner gas condenser 423 -> 313 K: water condensed, gas cooled
n14 = kmol(S["S14"])
Q["Q10"] = (kmol(S["S22"])["H2O"] * DH_VAP + sum(n14[k] * CP_GAS[k] for k in n14) * 110) / 3.6
Q["QD"] = Q_DIST   # distiller heat delivered by the live steam (information)

# --- checks ---------------------------------------------------------------------------------------
UNITS = {
    "KILN": (["S1", "S2", "S3"], ["S4", "S5"]),
    "SLAKER": (["S4", "S6"], ["S7"]),
    "SCRUBBER": (["S8", "S12"], ["S8B", "S13"]),
    "ABSORBER": (["S8B", "S9", "S10"], ["S11"]),
    "TOWERS": (["S11", "S5C", "S16"], ["S12", "S17"]),
    "FILTER": (["S17", "S20"], ["S18", "S21"]),
    "CALCINER": (["S18"], ["S14", "S19"]),
    "CONDENSER": (["S14"], ["S15", "S22"]),
    "DISTILLER": (["S21", "S22", "S7", "S23"], ["S9", "S24"]),
}
PLANT_IN = ["S1", "S2", "S3", "S6", "S8", "S10", "S20", "S23"]
PLANT_OUT = ["S13", "S19", "S24"]


def check():
    worst = 0.0
    for unit, (ins, outs) in UNITS.items():
        ei = elements(add(*[S[s] for s in ins]))
        eo = elements(add(*[S[s] for s in outs]))
        for e in set(ei) | set(eo):
            worst = max(worst, abs(ei.get(e, 0) - eo.get(e, 0)))
        mi, mo = sum(total(S[s]) for s in ins), sum(total(S[s]) for s in outs)
        print(f"# {unit:10s} in {mi:12.1f} out {mo:12.1f} kg/h  diff {mi - mo:+.3f}", file=sys.stderr)
    ei = elements(add(*[S[s] for s in PLANT_IN]))
    eo = elements(add(*[S[s] for s in PLANT_OUT]))
    print("# plant elements kmol/h in/out: " + ", ".join(
        f"{e} {ei[e]:.2f}/{eo.get(e, 0):.2f}" for e in sorted(ei)), file=sys.stderr)
    print(f"# worst unit element imbalance {worst:.2e} kmol/h", file=sys.stderr)
    for s, d in S.items():
        for k, v in d.items():
            if v < -1e-6:
                raise SystemExit(f"negative flow {s} {k} {v}")


def main():
    check()
    t = PRODUCT / 1000
    spec = {s: round(total(S[s]) / t, 1) for s in PLANT_IN + PLANT_OUT}
    print("# kg per t soda ash: " + json.dumps(spec), file=sys.stderr)
    print("# duties kW: " + json.dumps({k: round(v, 1) for k, v in Q.items()}), file=sys.stderr)
    print(f"# LP steam {m_lps:.0f} kg/h = {m_lps / t:.0f} kg/t; HP steam heat "
          f"{Q['Q9'] * 3.6 / t / 1000:.2f} GJ/t; coke {m_coke / t:.1f} kg/t; kiln CO2 "
          f"{S['S5']['CO2'] / t:.0f} kg/t; vent CO2 {S['S13']['CO2'] / t:.0f} kg/t", file=sys.stderr)
    out = {}
    for s, d in S.items():
        m = total(d)
        out[s] = {"flow": round(m, 1),
                  "w": {k: round(v / m, 6) for k, v in d.items() if v / m >= 5e-7}}
    out["duties_kW"] = {k: round(v, 1) for k, v in Q.items()}
    json.dump(out, sys.stdout, indent=None)
    print()
    # the values process/flowsheet.yaml cites from this script (balance-output contract): S and Q
    flowsheet = {s: {"flow": {"value": total(d), "basis": "mass"},
                     "composition": {"values": {k: v / total(d) for k, v in d.items()},
                                     "basis": "mass_fraction"}}
                 for s, d in S.items()}
    flowsheet.update({k: {"duty": v} for k, v in Q.items()})
    write_balance_output({"design": flowsheet})


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


if __name__ == "__main__":
    main()
