"""Steady-state material balance of the liquid-solvent direct air capture plant (direct-air-capture-1).

A closed-form balance of the two chemical loops of the KOH / calcium-looping process of Keith
et al. (2018, Joule 2, 1573) in its gas-fired configuration with grid electricity (their
scenario C; DESIGN.md D-001): the air contactor (CO2 + 2 KOH -> K2CO3 + H2O), the pellet
reactor (K2CO3 + Ca(OH)2 -> CaCO3 + 2 KOH, and CaO + H2O -> Ca(OH)2 for the lime left
unslaked), the steam slaker (CaO + H2O -> Ca(OH)2), the oxy-fired calciner (CaCO3 -> CaO + CO2,
CH4 + 2 O2 -> CO2 + 2 H2O) and the CO2 compression train with its water knock-out.

No electrolyte, crystallisation or gas-liquid model is used: capture fraction, conversions,
calcium retention, carry-overs, make-ups and the calciner's specific energy are design
parameters, taken from the sources named in DESIGN.md (SRC-1 Keith et al. 2018, SRC-2 NETL
2022) or ASSUMED (D-002 to D-008). The loops are closed algebraically (no iteration): at steady
state the calcium precipitated in the pellet reactor equals the carbonate captured less the
carbonate leaving with the potassium purge, and the calcium purged equals the seed make-up.

Run: cheme run scripts/dac_balance.py [--yaml]. It prints the key figures and the element
balance of every step; --yaml prints the material streams of process/flowsheet.yaml (values
ASSUMED with this script as their source). With BALANCE_OUTPUT set it writes the values the
flowsheet cites (library balance-output contract, ADR 0027).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AW = {"H": 1.008, "C": 12.011, "O": 15.999, "N": 14.007, "K": 39.098, "Ca": 40.078}
FORMULA = {"CO2": "CO2", "N2": "N2", "O2": "O2", "H2O": "H2O", "KOH": "KOH", "K2CO3": "K2CO3",
           "CAOH2": "CaO2H2", "CACO3": "CaCO3", "CAO": "CaO", "CH4": "CH4"}
COMPS = list(FORMULA)


def parse(f):
    return {e: int(n or 1) for e, n in re.findall(r"([A-Z][a-z]?)(\d*)", f)}


EL = {k: parse(v) for k, v in FORMULA.items()}
MW = {k: round(sum(AW[e] * n for e, n in v.items()), 3) for k, v in EL.items()}

# --- design parameters (DESIGN.md) -----------------------------------------------------------
AIR = 251_000e3               # kg/h air through the contactors (SRC-1 Fig. 2), D-002
AIR_W = {"CO2": 0.00060, "O2": 0.2300, "N2": 0.7596, "H2O": 0.0098}  # mass fractions, SRC-1 Fig. 2
CAPTURE = 0.745               # fraction of the air's CO2 captured (SRC-1 Table 1), D-003
EVAP = 4.7                    # t water evaporated per t CO2 captured, 20 C / 64 % RH (SRC-1 p. 1581), D-003
LEAN_M = {"KOH": 1.10, "K2CO3": 0.45}   # mol/L lean liquor (SRC-1 Fig. 2: 2.00 K+, 1.10 OH-, 0.45 CO3--), D-003
SWING = 0.21                  # mol/L carbonate swing, lean 0.45 to rich 0.66 (SRC-1 Fig. 2 reading), D-003
RHO_LIQ = 1.10                # kg/L lean liquor, ASSUMED (D-003)
# Make-ups (D-005): SRC-2's consumables per t of CO2 its KOH liquor takes up, which in SRC-2 Case 1
# is the air's CO2 (909 225 t/a gross) and the NGCC flue gas CO2 of its absorber on the same liquor
# (187 131 t/a), both at an 85 % capacity factor (8760 x 0.85 = 7446 h/a): 147.24 t/h. Here the
# liquor takes up the air's CO2 only, so the rates are applied per t of CO2 captured from the air.
SHORT_TON = 0.90718474        # t per US short ton
SRC2_LIQUOR_CO2 = (909_225 + 187_131) / (8760 * 0.85)        # t/h CO2 taken up by SRC-2's liquor
KOH_MAKEUP = 69.8 * SHORT_TON / 24 / SRC2_LIQUOR_CO2         # t KOH per t CO2 (SRC-2 Exhibit 5-11)
SEED = 104 * SHORT_TON / 24 / SRC2_LIQUOR_CO2                # t CaCO3 seed per t CO2 (SRC-2 Exhibit 5-11)
CAKE_LIQUOR = 0.30            # mass fraction of lean liquor in the drained purge filter cake, ASSUMED (D-005)
K2CO3_CARRY = 0.018           # kg K2CO3 per kg CaCO3 in the pellets (SRC-1 Fig. 2: 5.4 / 300 t/h), D-004
PELLET_WATER = 0.11           # mass fraction of water in the washed pellets (SRC-1 Table 1), D-004
SLAKE_CONV = 0.85             # CaO slaked in the steam slaker (SRC-1 Table 1), D-006
CALC_CONV = 0.98              # CaCO3 calcined (SRC-1 Table 1), D-007
SLURRY_CAOH2 = 0.30           # mass fraction Ca(OH)2 of the lime slurry (SRC-1 p. 1578), D-004
GJ_PER_T_CO2 = 5.25           # GJ (LHV) per t CO2 from calcination (SRC-1 p. 1580), D-007
LHV_CH4 = 50.0                # GJ/t, SRC-1 Fig. 2: 670 GJ/h for 13.4 t/h CH4 (D-007)
O2_PER_CH4 = 58.5 / 13.4      # t oxidant per t CH4 (SRC-1 Fig. 2), D-007
O2_PURITY = 0.956             # mass fraction O2 in the oxidant, rest N2 (SRC-1 Fig. 2), D-007
PRODUCT_WATER = 0.0001        # mass fraction water in the product (SRC-1 Fig. 2: 0.01 %), D-008
# power, kWh per t CO2 processed by the unit (SRC-1 Table 1), D-009
KWH_FAN, KWH_CONTACTOR_PUMP, KWH_PELLET, KWH_SLAKER, KWH_COMP = 61, 21, 27, 32, 132
HOURS = 7884                  # h/a, 90 % utilisation (SRC-1 Table 2 note), D-002


def kmol_to_kg(d):
    return {k: v * MW[k] for k, v in d.items()}


def kg_to_kmol(d):
    return {k: v / MW[k] for k, v in d.items()}


def total(d):
    return sum(d.values())


def balance():
    s = {}  # stream id -> {component: kg/h}
    air = {k: AIR * w for k, w in AIR_W.items()}
    co2_air = air["CO2"] / MW["CO2"]
    A = CAPTURE * co2_air                          # kmol/h CO2 captured
    a_t = A * MW["CO2"] / 1000                     # t/h
    evap = EVAP * a_t * 1000                       # kg/h water evaporated

    # lean liquor (to the contactors)
    vol = A / SWING                                # m3/h
    lean = {"KOH": LEAN_M["KOH"] * vol * MW["KOH"], "K2CO3": LEAN_M["K2CO3"] * vol * MW["K2CO3"]}
    lean["H2O"] = RHO_LIQ * vol * 1000 - total(lean)

    koh = KOH_MAKEUP * a_t * 1000                  # kg/h KOH
    k_m = koh / MW["KOH"]                          # kmol K/h
    seed = SEED * a_t * 1000                       # kg/h CaCO3
    seed_n = seed / MW["CACO3"]

    # purge: the seed's Ca as CaCO3 in a drained filter cake whose liquid is lean liquor (S22);
    # the make-up's K that the cake liquor does not carry leaves as a lean-liquor bleed (S23)
    lean_w = {k: v / total(lean) for k, v in lean.items()}
    k_per_kg = lean_w["KOH"] / MW["KOH"] + 2 * lean_w["K2CO3"] / MW["K2CO3"]   # kmol K per kg liquor
    cake_liq = seed * CAKE_LIQUOR / (1 - CAKE_LIQUOR)                           # kg/h liquor in the cake
    bleed_liq = (k_m - cake_liq * k_per_kg) / k_per_kg                          # kg/h liquor bled
    assert bleed_liq > 0, "the cake liquor carries more potassium than the make-up"
    purge = {"CACO3": seed, **{k: cake_liq * w for k, w in lean_w.items()}}
    bleed = {k: bleed_liq * w for k, w in lean_w.items()}
    k2co3_out = (purge["K2CO3"] + bleed["K2CO3"]) / MW["K2CO3"]                 # kmol/h

    # calcium loop
    P = A - k2co3_out                              # kmol/h CaCO3 precipitated (= CO2 calcined)
    X = P / CALC_CONV                              # kmol/h CaCO3 to the calciner
    cao = CALC_CONV * X
    pel = {"CACO3": X * MW["CACO3"]}
    pel["K2CO3"] = K2CO3_CARRY * pel["CACO3"]
    pel["H2O"] = (pel["CACO3"] + pel["K2CO3"]) * PELLET_WATER / (1 - PELLET_WATER)

    # contactor C101: air S1 + lean S11 + KOH S3 -> air out S10 + rich S12
    s["S1"] = air
    s["S11"] = lean
    s["S3"] = {"KOH": koh}
    out_air = dict(air)
    out_air["CO2"] = air["CO2"] - A * MW["CO2"]
    out_air["H2O"] = air["H2O"] + evap
    s["S10"] = out_air
    rich = {"KOH": lean["KOH"] + koh - 2 * A * MW["KOH"],
            "K2CO3": lean["K2CO3"] + A * MW["K2CO3"],
            "H2O": lean["H2O"] + A * MW["H2O"] - evap}
    s["S12"] = rich

    # calciner F401: dried pellets S17 + CH4 S6 + oxidant S7 -> CaO S18 + off-gas S20
    dried = {"CACO3": pel["CACO3"], "K2CO3": pel["K2CO3"]}
    s["S17"] = dried
    ch4 = GJ_PER_T_CO2 * (P * MW["CO2"] / 1000) / LHV_CH4 * 1000   # kg/h
    ch4_n = ch4 / MW["CH4"]
    ox = O2_PER_CH4 * ch4
    s["S6"] = {"CH4": ch4}
    s["S7"] = {"O2": O2_PURITY * ox, "N2": (1 - O2_PURITY) * ox}
    s["S18"] = {"CAO": cao * MW["CAO"], "CACO3": (X - cao) * MW["CACO3"], "K2CO3": pel["K2CO3"]}
    offgas = {"CO2": (cao + ch4_n) * MW["CO2"], "H2O": 2 * ch4_n * MW["H2O"],
              "O2": O2_PURITY * ox - 2 * ch4_n * MW["O2"], "N2": (1 - O2_PURITY) * ox}
    s["S19"] = offgas

    # steam slaker SL301: washed pellets S15 + CaO S18 + water S8 -> dried pellets S17 + lime S16
    s["S15"] = pel
    need = SLAKE_CONV * cao                        # kmol/h water for slaking
    w_add = need * MW["H2O"] - pel["H2O"]
    assert w_add > 0, "pellet water exceeds the slaking demand: a steam vent would be needed"
    s["S8"] = {"H2O": w_add}
    lime = {"CAOH2": SLAKE_CONV * cao * MW["CAOH2"], "CAO": (1 - SLAKE_CONV) * cao * MW["CAO"],
            "CACO3": (X - cao) * MW["CACO3"], "K2CO3": pel["K2CO3"]}
    s["S16"] = lime

    # lime mix tank M302: lime S16 + water S4 -> slurry S13 (30 wt% Ca(OH)2)
    slurry_total = lime["CAOH2"] / SLURRY_CAOH2
    s["S4"] = {"H2O": slurry_total - total(lime)}
    slurry = dict(lime)
    slurry["H2O"] = s["S4"]["H2O"]
    s["S13"] = slurry

    # pellet reactor R201: rich S12 + slurry S13 + seed S5 + wash water S2
    #   -> lean S11 + pellets S15 + purge S22 + bleed S23
    s["S5"] = {"CACO3": seed}
    s["S22"] = purge
    s["S23"] = bleed
    slake_pr = (1 - SLAKE_CONV) * cao              # kmol/h CaO slaked in the reactor
    w_in = rich["H2O"] + slurry["H2O"]
    w_out = lean["H2O"] + pel["H2O"] + purge["H2O"] + bleed["H2O"] + slake_pr * MW["H2O"]
    s["S2"] = {"H2O": w_out - w_in}
    assert s["S2"]["H2O"] > 0

    # CO2 compression and drying K501: off-gas S19 -> product S20 + condensate S21
    prod = {k: v for k, v in offgas.items() if k != "H2O"}
    prod["H2O"] = total(prod) * PRODUCT_WATER / (1 - PRODUCT_WATER)
    s["S20"] = prod
    s["S21"] = {"H2O": offgas["H2O"] - prod["H2O"]}

    figures = {"A_kmol_h": A, "captured_t_h": a_t, "evap_kg_h": evap, "lean_m3_h": vol,
               "P_kmol_h": P, "X_kmol_h": X, "cao_kmol_h": cao, "slake_sl_kmol_h": need,
               "slake_pr_kmol_h": slake_pr, "ch4_kg_h": ch4, "oxidant_kg_h": ox,
               "koh_kg_h": koh, "seed_kg_h": seed, "k2co3_out_kmol_h": k2co3_out,
               "product_t_h": total(prod) / 1000, "product_co2_t_h": prod["CO2"] / 1000,
               "condensate_kg_h": s["S21"]["H2O"]}
    return s, figures


STEPS = {  # step: (inputs, outputs)
    "C101": (["S1", "S11", "S3"], ["S10", "S12"]),
    "R201": (["S12", "S13", "S5", "S2"], ["S11", "S15", "S22", "S23"]),
    "SL301": (["S15", "S18", "S8"], ["S17", "S16"]),
    "M302": (["S16", "S4"], ["S13"]),
    "F401": (["S17", "S6", "S7"], ["S18", "S19"]),
    "K501": (["S19"], ["S20", "S21"]),
}


def elements(d):
    out = {}
    for k, kg in d.items():
        for e, n in EL[k].items():
            out[e] = out.get(e, 0.0) + kg / MW[k] * n * AW[e]
    return out


def power(s, f):
    a_t = f["captured_t_h"]
    calc_t = f["P_kmol_h"] * MW["CO2"] / 1000
    return {"fans": KWH_FAN * a_t, "contactor_pumps": KWH_CONTACTOR_PUMP * a_t,
            "pellet": KWH_PELLET * a_t, "slaker": KWH_SLAKER * calc_t,
            "compressor": KWH_COMP * f["product_co2_t_h"]}   # per t of CO2 (SRC-1 Table 1 note)


# --- hand energy balances (DESIGN.md D-003, D-006, D-007, D-009; printed, not cited as values) ---
# Stream temperatures as the flowsheet gives them (K); round heat capacities, kJ/(kg K), ASSUMED
# (no property package covers the liquor or the solids, L-1, L-4); the reaction heats of SRC-1
# Fig. 1 (process/reactions.yaml), kJ/mol; psychrometric constants of moist air, ASSUMED round.
T_AIR, T_FEEDS, T_RICH, T_SLURRY, T_CAO, T_SLAKER = 293.15, 293.15, 294.15, 333.15, 947.15, 573.15
T_OFFGAS = 373.15
CP = {"H2O": 4.18, "KOH": 1.0, "K2CO3": 1.0, "CACO3": 0.95, "CAO": 0.9, "CAOH2": 1.3}
CP_GAS = {"CO2": 0.85, "H2O": 1.9, "O2": 0.92, "N2": 1.04, "CH4": 2.2}
DH = {"ABS": 95.8, "CAUST": 5.8, "SLAKE": 63.9, "CALC": 178.3}      # heat released (+) or taken (CALC)
CP_DRY_AIR, CP_VAPOUR, H_VAP_0C = 1.006, 1.86, 2501.0               # kJ/(kg K), kJ/(kg K), kJ/kg
H2O_LATENT_CO2_TRAIN, CP_CO2_GAS, DT_CO2_GAS = 2400.0, 0.85, 60.0   # Q1 round properties (D-009)


def sensible(d, t, t_ref=298.15):
    """kW of a liquid or solid stream {component: kg/h} at t relative to t_ref."""
    return sum(kg * CP[k] for k, kg in d.items()) * (t - t_ref) / 3600


def energy(s, f, p):
    e = {}
    kw = 1000 / 3600                               # kmol/h x kJ/mol -> kW
    # Q1, CO2 train coolers (D-009): compression work + combustion water condensed + gas cooled
    e["Q1_compressor_kW"] = p["compressor"]
    e["Q1_condensation_kW"] = f["condensate_kg_h"] * H2O_LATENT_CO2_TRAIN / 3600
    e["Q1_gas_cooling_kW"] = CP_CO2_GAS * f["product_t_h"] * 1000 * DT_CO2_GAS / 3600
    e["Q1_kW"] = e["Q1_compressor_kW"] + e["Q1_condensation_kW"] + e["Q1_gas_cooling_kW"]
    # Q2, F401's heat not taken by the calcination or carried by its outlets (D-007): the fired heat
    # (LHV, the combustion water as vapour) and the pellets' heat at 300 C, less the calcination,
    # the hot lime to the slaker at 674 C and the off-gas at 373 K
    e["Q2_fired_kW"] = f["ch4_kg_h"] * LHV_CH4 * 1000 / 3600
    e["Q2_calcination_kW"] = f["P_kmol_h"] * DH["CALC"] * kw
    e["Q2_pellets_in_kW"] = sensible(s["S17"], T_SLAKER)
    e["Q2_hot_lime_out_kW"] = sensible(s["S18"], T_CAO)
    gas = lambda d, t: sum(kg * CP_GAS[k] for k, kg in d.items()) * (t - 298.15) / 3600
    e["Q2_offgas_out_kW"] = gas(s["S19"], T_OFFGAS)
    e["Q2_feeds_in_kW"] = gas(s["S6"], T_FEEDS) + gas(s["S7"], T_FEEDS)
    e["Q2_kW"] = (e["Q2_fired_kW"] + e["Q2_pellets_in_kW"] + e["Q2_feeds_in_kW"] - e["Q2_calcination_kW"]
                  - e["Q2_hot_lime_out_kW"] - e["Q2_offgas_out_kW"])
    # R201 (D-004): causticisation and the slaking of the CaO left, plus the warm slurry, raise the
    # outlets (lean liquor, pellets, purge, bleed) to one temperature
    e["R201_caust_kW"] = f["P_kmol_h"] * DH["CAUST"] * kw
    e["R201_slake_kW"] = f["slake_pr_kmol_h"] * DH["SLAKE"] * kw
    h_in = (sensible(s["S12"], T_RICH) + sensible(s["S13"], T_SLURRY)
            + sensible(s["S5"], T_FEEDS) + sensible(s["S2"], T_FEEDS))
    cp_out = sum(sensible(s[o], 299.15) for o in ("S11", "S15", "S22", "S23"))   # kW per K
    e["R201_outlet_K"] = 298.15 + (h_in + e["R201_caust_kW"] + e["R201_slake_kW"]) / cp_out
    e["R201_heat_to_liquor_kW"] = sensible(s["S11"], e["R201_outlet_K"], T_RICH)
    # SL301 (D-006): the slaking heat and the hot lime against the pellets and lime leaving at 300 C
    e["SL301_slake_kW"] = f["slake_sl_kmol_h"] * DH["SLAKE"] * kw
    e["SL301_hot_lime_in_kW"] = sensible(s["S18"], T_CAO)
    e["SL301_surplus_kW"] = (sensible(s["S15"], e["R201_outlet_K"]) + sensible(s["S8"], T_FEEDS)
                             + e["SL301_hot_lime_in_kW"] + e["SL301_slake_kW"]
                             - sensible(s["S17"], T_SLAKER) - sensible(s["S16"], T_SLAKER))
    # C101 (D-003): the air takes up the absorption heat, the fans' and pumps' power, the heat the
    # lean liquor brings from R201 and the CO2 train's cooling water (Q1, cooled in the basin);
    # the moist-air enthalpy h = cp_a t + w (h_v0 + cp_v t) per kg dry air, t in degC, liquid at 0 C
    e["C101_abs_kW"] = f["A_kmol_h"] * DH["ABS"] * kw
    e["C101_power_kW"] = p["fans"] + p["contactor_pumps"]
    e["C101_liquor_kW"] = (sensible(s["S11"], e["R201_outlet_K"], 273.15) + sensible(s["S3"], T_FEEDS, 273.15)
                           - sensible(s["S12"], T_RICH, 273.15))
    e["C101_heat_kW"] = e["C101_abs_kW"] + e["C101_power_kW"] + e["C101_liquor_kW"] + e["Q1_kW"]

    def moist(d):
        dry = total(d) - d["H2O"]
        return dry, d["H2O"] / dry

    dry_in, w_in = moist(s["S1"])
    dry_out, w_out = moist(s["S10"])
    t_in = T_AIR - 273.15
    h_in = dry_in * (CP_DRY_AIR * t_in + w_in * (H_VAP_0C + CP_VAPOUR * t_in)) / 3600
    h_out = (h_in + e["C101_heat_kW"]) * 3600 / dry_out                            # kJ/kg dry air
    e["C101_w_in"], e["C101_w_out"] = w_in, w_out
    e["C101_air_out_K"] = 273.15 + (h_out - w_out * H_VAP_0C) / (CP_DRY_AIR + w_out * CP_VAPOUR)
    t_19 = 19.0
    e["C101_heat_for_19C_kW"] = (dry_out * (CP_DRY_AIR * t_19 + w_out * (H_VAP_0C + CP_VAPOUR * t_19))
                                 / 3600 - h_in)
    return e


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
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


def rounded(x):
    return float(f"{x:.6g}")


def main():
    s, f = balance()
    p = power(s, f)
    if "--yaml" in sys.argv:
        for sid in sorted(s, key=lambda k: int(k[1:])):
            d = s[sid]
            tot = total(d)
            comp = {k: rounded(d.get(k, 0.0) / tot) for k in COMPS}
            print(f"  {sid}: flow {rounded(tot)} composition {comp}")
    else:
        for k, v in f.items():
            print(f"{k}: {v:.6g}")
        for k, v in p.items():
            print(f"power {k}: {v:.1f} kW")
        print(f"power total: {sum(p.values()):.1f} kW = {sum(p.values()) / f['captured_t_h']:.1f} kWh/t air CO2")
        for k, v in energy(s, f, p).items():
            print(f"energy {k}: {v:.6g}")
        for st, (ins, outs) in STEPS.items():
            ei = elements({c: sum(s[i].get(c, 0) for i in ins) for c in COMPS})
            eo = elements({c: sum(s[o].get(c, 0) for o in outs) for c in COMPS})
            dev = max(abs(ei.get(e, 0) - eo.get(e, 0)) for e in set(ei) | set(eo))
            print(f"step {st}: mass in {sum(total(s[i]) for i in ins):.6g} out "
                  f"{sum(total(s[o]) for o in outs):.6g} kg/h, max element deviation {dev:.3g} kg/h")
    cases = {"design": {}}
    for sid, d in s.items():
        tot = total(d)
        cases["design"][sid] = {"flow": rounded(tot),
                                "composition": {k: rounded(d.get(k, 0.0) / tot) for k in COMPS}}
    write_balance_output(cases)


if __name__ == "__main__":
    main()
