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
KOH_MAKEUP = 0.02161          # t KOH per t CO2 captured: SRC-2 69.8 short ton/d / 122.1 t/h air CO2 (D-005)
SEED = 0.03220                # t CaCO3 seed per t CO2 captured: SRC-2 104 short ton/d / 122.1 t/h (D-005)
CAKE_WATER = 0.30             # water mass fraction of the purge filter cake, ASSUMED (D-005)
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

    # purge: the seed's Ca as CaCO3 and the make-up's K in the lean liquor's K split
    fk_koh = LEAN_M["KOH"] / (LEAN_M["KOH"] + 2 * LEAN_M["K2CO3"])
    purge_n = {"CACO3": seed_n, "KOH": fk_koh * k_m, "K2CO3": (1 - fk_koh) * k_m / 2}
    purge = kmol_to_kg(purge_n)
    purge["H2O"] = total(purge) * CAKE_WATER / (1 - CAKE_WATER)

    # calcium loop
    P = A - purge_n["K2CO3"]                       # kmol/h CaCO3 precipitated (= CO2 calcined)
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

    # pellet reactor R201: rich S12 + slurry S13 + seed S5 + wash water S2 -> lean S11 + pellets S15 + purge S22
    s["S5"] = {"CACO3": seed}
    s["S22"] = purge
    slake_pr = (1 - SLAKE_CONV) * cao              # kmol/h CaO slaked in the reactor
    w_in = rich["H2O"] + slurry["H2O"]
    w_out = lean["H2O"] + pel["H2O"] + purge["H2O"] + slake_pr * MW["H2O"]
    s["S2"] = {"H2O": w_out - w_in}
    assert s["S2"]["H2O"] > 0

    # CO2 compression and drying K501: off-gas S19 -> product S20 + condensate S21
    prod = {k: v for k, v in offgas.items() if k != "H2O"}
    prod["H2O"] = total(prod) * PRODUCT_WATER / (1 - PRODUCT_WATER)
    s["S20"] = prod
    s["S21"] = {"H2O": offgas["H2O"] - prod["H2O"]}

    figures = {"A_kmol_h": A, "captured_t_h": a_t, "evap_kg_h": evap, "lean_m3_h": vol,
               "P_kmol_h": P, "X_kmol_h": X, "ch4_kg_h": ch4, "oxidant_kg_h": ox,
               "product_t_h": total(prod) / 1000}
    return s, figures


STEPS = {  # step: (inputs, outputs)
    "C101": (["S1", "S11", "S3"], ["S10", "S12"]),
    "R201": (["S12", "S13", "S5", "S2"], ["S11", "S15", "S22"]),
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
            "compressor": KWH_COMP * f["product_t_h"]}


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
