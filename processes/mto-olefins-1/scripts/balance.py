"""Shortcut duties and the air and caustic feeds of mto-olefins-1 (DESIGN.md D-011).

Run with `cheme run scripts/balance.py` from the process folder. It reads the flows and
compositions that `cheme process propagate --fill` wrote into process/flowsheet.yaml and the
ideal-gas data of process/materials.yaml, and prints, for the values the flowsheet gives as
`assumed` with the source "scripts/balance.py":

- S8: the regeneration air for complete coke combustion with 2 vol% O2 in the dry flue gas;
- S9: the air blower's discharge temperature;
- S16: the fresh caustic, 3 mol NaOH per mol CO2 in the gas (ASSUMED excess), 10 wt%;
- S4: the outlet temperature of the adiabatic model step R100 (the recycled DME taken as
  methanol, D-006): its small endothermic heat cools the reactor feed;
- S26: the demethaniser bottoms at their bubble point (Raoult, thermo's vapour pressures);
- Q1: the feed vaporiser (liquid to the normal boiling point, vaporisation, vapour superheat to
  the S3 temperature);
- Q4, Q8 to Q11: the blower and the product gas compressor (ideal gas, isentropic efficiency
  ASSUMED, intercooled to the stage inlet temperature) and its coolers (with the latent heat of
  the water knocked out in V301 and of the water and hydrocarbons condensed in V302);
- Q26: the caustic tower's liquor cooler (the heat of neutralisation);
- Q5: the quench tower (the gas cooled from 748 K to 313 K, the water and oxygenates condensed);
- Q6, Q7: the oxygenate stripper (stripping steam per kg of feed, ASSUMED);
- Q12 to Q21, Q24, Q25: the columns, reflux ratios ASSUMED: (R + 1) x distillate x heat of
  vaporisation at the normal boiling point, reboiler = condenser; the demethaniser and C2
  splitter reboilers (Q24, Q25) heated by condensing propylene refrigerant;
- Q22, Q23: the refrigeration compressors at 60 % of the Carnot COP (ASSUMED) and the heat
  they reject to cooling water: the condenser duties lifted to cooling water, except the
  demethaniser's and the C2 splitter's, which are lifted only to their reboilers, whose
  compression work is then lifted to cooling water.

It also prints, as cross-checks the flowsheet cites for its ASSUMED recoveries (they are not
stream values, so the balance-output contract does not carry them):

- the water recoveries of T201 and V301 that leave the gas saturated with water at 313.15 K
  (ideal gas, the water vapour pressure of IAPWS-95 in `chemicals`);
- the three-phase split of V302 (the gas compressed to 2069 kPa(a) and cooled to 311.15 K,
  US 7 138 557 B2's primary product separator): a Peng-Robinson flash with `thermo` 0.6.1
  (ChemSep's PR binary interaction parameters), the fraction of each component in the aqueous
  and in the hydrocarbon liquid.

The reactor and regenerator duties Q2 and Q3 are core's conversion-step duties (cheme process
propagate writes them); this script does not give them.

Heats of vaporisation and liquid heat capacities: the `chemicals` 1.5.2 package's packaged CRC
tables (`phase_change.Hvap_data_CRC`, `heat_capacity.CRC_standard_data`); formation enthalpies
of the solids NaOH and Na2CO3 and of liquid water: `chemicals.reaction` (CRC); single values
with their source, not open data (library ADR 0037, DESIGN.md SRC-6). Shortcut estimates for a
concept study: no property package of core covers this mixture (L-1).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml
from chemicals.iapws import iapws95_Psat
from thermo import (CEOSGas, CEOSLiquid, ChemicalConstantsPackage, FlashVLN, PRMIX,
                    VaporPressure)
from thermo.interaction_parameters import IPDB

ROOT = Path(__file__).resolve().parents[1]
R = 8.314462618  # kJ/(kmol K)
T0 = 298.15

MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())["components"]}
FS = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text())
STREAMS = {s["id"]: s for s in FS["streams"]}

# Heat of vaporisation at the normal boiling point (kJ/kmol) and liquid heat capacity
# (kJ/(kmol K)): chemicals 1.5.2, Hvap_data_CRC 'HvapTb' and CRC_standard_data 'Cpl'.
HVAP_TB = {"MEOH": 35210.0, "DME": 21510.0, "H2O": 40650.0, "C2H4": 13530.0, "C3H6": 18420.0,
           "C3H8": 19040.0, "C2H6": 14690.0, "C4H8": 22070.0, "C5H10": 25200.0, "C4H6": 22470.0,
           "C4H10": 22440.0}
# Normal boiling points of the same table (K), where materials.yaml gives none.
TB = {"MEOH": 337.75, "DME": 248.35, "H2O": 373.12, "C4H6": 268.74, "C4H10": 272.65, "C4H8": 266.89,
      "C5H10": 303.11}
CPL = {"MEOH": 81.1, "H2O": 75.3, "DME": 102.0}  # DME: no CRC value; ASSUMED near methanol's per carbon
# Watson's correlation for the heat of vaporisation away from the normal boiling point, with
# the exponent 0.38 usually taken with it and Tc of materials.yaml: ASSUMED (the correlation's
# original paper was not read), used from 311 to 313 K only.
WATSON = 0.38
# Formation enthalpies at 298.15 K, kJ/kmol, chemicals 1.5.2 `reaction.Hfs`/`Hfl` (method CRC):
# solid NaOH and Na2CO3, liquid water; CO2 gas from materials.yaml.
HF_NAOH_S = -425800.0
HF_NA2CO3_S = -1130700.0
HF_H2O_L = -285825.0

# ASSUMED design values (DESIGN.md D-007, D-009 to D-011)
O2_DRY_FLUE = 0.02          # vol fraction O2 in the dry flue gas
NAOH_PER_CO2 = 3.0          # mol NaOH per mol CO2
CAUSTIC_WT = 0.10           # NaOH mass fraction of the fresh caustic
ETA_BLOWER = 0.80
ETA_COMP = 0.78
STRIP_STEAM = 0.06          # kg LP steam per kg of stripper feed
LPS_LATENT = 2120.0         # kJ/kg, LP steam 450 kPa(a) (steam tables, rounded)
REFLUX = {"T401": 1.0, "T402": 1.5, "T403": 3.5, "T501": 1.0, "T502": 12.0, "T503": 1.0}
COP_FRACTION = 0.60
T_COND_REF = 313.15         # refrigerant condensing against cooling water
T_EVAP = {"T401": 243.15, "T402": 170.15, "T403": 233.15}
# Condensing propylene refrigerant in the demethaniser and C2 splitter reboilers: 10 K above
# their bottoms' bubble points (243.6 K and 262.5 K at 1950 kPa(a)), ASSUMED approach.
T_REB_HEAT = {"T402": 253.15, "T403": 273.15}
T_KO = 313.15               # quench, V301: gas leaves saturated with water here
T_V302, P_V302 = 311.15, 2069.0   # US 7 138 557 B2: about 38 C and 2069 kPa
SCRUB_T201 = {"MEOH": 0.999, "DME": 0.99}   # ASSUMED (D-008), as in the flowsheet


def state(sid: str) -> dict:
    return STREAMS[sid]["state"]["design"]


def kmol(sid: str) -> dict[str, float]:
    st = state(sid)
    comp = st["composition"]
    x = comp["values"]
    if comp["basis"] == "mass_fraction":
        w = {c: v for c, v in x.items() if v}
        n = {c: st["flow"]["value"] * v / MAT[c]["molar_mass"] for c, v in w.items()}
        return n
    mw = sum(v * MAT[c]["molar_mass"] for c, v in x.items())
    total = st["flow"]["value"] / mw
    return {c: v * total for c, v in x.items() if v}


def cp_ig(c: str, t: float) -> float:
    a = MAT[c]["ideal_gas"]["cp_R"]
    return R * sum(k * t**i for i, k in enumerate(a))


def h_ig(c: str, t: float) -> float:
    """Sensible ideal-gas enthalpy from 298.15 K, kJ/kmol."""
    a = MAT[c]["ideal_gas"]["cp_R"]
    return R * sum(k / (i + 1) * (t ** (i + 1) - T0 ** (i + 1)) for i, k in enumerate(a))


def hvap(c: str, t: float) -> float:
    tc = MAT[c]["critical"]["Tc"]
    tb = TB.get(c) or MAT[c].get("normal_boiling_point")
    return HVAP_TB[c] * ((1 - t / tc) / (1 - tb / tc)) ** WATSON


def gas_enthalpy(n: dict[str, float], t: float) -> float:
    return sum(v * h_ig(c, t) for c, v in n.items() if c in MAT and "ideal_gas" in MAT[c])


def compression(n: dict[str, float], t_in: float, p_in: float, p_out: float, stages: int, eta: float):
    """Power (kW) and outlet temperature of each stage, equal pressure ratios, intercooled to t_in."""
    total = sum(n.values())
    cp = sum(v * cp_ig(c, t_in) for c, v in n.items()) / total
    ratio = (p_out / p_in) ** (1.0 / stages)
    dt_s = t_in * (ratio ** (R / cp) - 1.0)
    dt = dt_s / eta
    power = stages * total / 3600.0 * cp * dt
    return power, t_in + dt


def saturation_recovery(n: dict[str, float], p_kpa: float, kept: dict[str, float]) -> float:
    """Water fraction knocked out so that the gas leaves saturated at T_KO (ideal gas);
    *kept*: the fraction of each other component that stays in the gas (default 1)."""
    y = iapws95_Psat(T_KO) / (p_kpa * 1000.0)
    dry = sum(v * kept.get(c, 1.0) for c, v in n.items() if c not in ("H2O", "COKE"))
    return 1.0 - y / (1.0 - y) * dry / n["H2O"]


def three_phase(n: dict[str, float], t: float, p_kpa: float) -> tuple[dict, dict, float]:
    """Peng-Robinson (thermo 0.6.1, ChemSep kij) flash: the fraction of each component in the
    aqueous liquid and in the hydrocarbon liquid, and the vapour fraction."""
    ids = [c for c, v in n.items() if v > 0 and "ideal_gas" in MAT[c] and c != "COKE"]
    consts, props = ChemicalConstantsPackage.from_IDs([MAT[c]["cas"] for c in ids])
    kijs = IPDB.get_ip_asymmetric_matrix("ChemSep PR", consts.CASs, "kij")
    kw = dict(Tcs=consts.Tcs, Pcs=consts.Pcs, omegas=consts.omegas, kijs=kijs)
    gas = CEOSGas(PRMIX, kw, HeatCapacityGases=props.HeatCapacityGases)
    liq = CEOSLiquid(PRMIX, kw, HeatCapacityGases=props.HeatCapacityGases)
    total = sum(n[c] for c in ids)
    res = FlashVLN(consts, props, liquids=[liq, liq], gas=gas).flash(
        T=t, P=p_kpa * 1000.0, zs=[n[c] / total for c in ids])
    aq: dict[str, float] = {}
    hc: dict[str, float] = {}
    lf = 1.0 - res.VF
    iw = ids.index("H2O")
    for phase, beta in zip(res.liquids, res.betas_liquids):
        target = aq if phase.zs[iw] > 0.5 else hc
        for k, c in enumerate(ids):
            target[c] = target.get(c, 0.0) + phase.zs[k] * beta * lf * total / n[c]
    return aq, hc, res.VF


def bubble_point(x: dict[str, float], p_kpa: float) -> float:
    """Raoult bubble point (K) with thermo's vapour pressures."""
    vp = {c: VaporPressure(CASRN=MAT[c]["cas"]) for c, v in x.items() if v}
    lo, hi = 150.0, 400.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if sum(x[c] * vp[c](mid) for c in vp) > p_kpa * 1000.0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def cop(t_cold: float, t_hot: float) -> float:
    return COP_FRACTION * t_cold / (t_hot - t_cold)


def main() -> dict:
    out: dict[str, dict] = {}

    # --- cross-checks for the ASSUMED recoveries (printed, D-008, D-009)
    n6 = {c: v for c, v in kmol("S6").items() if c != "COKE"}
    print("T201 water recovery to saturation at 313.15 K, 200 kPa(a):",
          round(saturation_recovery(n6, 200.0, SCRUB_T201), 4))
    print("V301 water recovery to saturation at 313.15 K, 900 kPa(a):",
          round(saturation_recovery(kmol("S13"), 900.0, {}), 4))
    aq, hc, vf = three_phase(kmol("S20"), T_V302, P_V302)
    print("V302 vapour fraction", round(vf, 4))
    print("V302 aqueous liquid:", {c: round(v, 4) for c, v in aq.items() if v >= 1e-4})
    print("V302 hydrocarbon liquid:", {c: round(v, 4) for c, v in hc.items() if v >= 1e-4})

    # --- R100 adiabatic outlet (S4): the DME counted as methanol takes its heat from the feed
    n3 = kmol("S3")
    t3 = state("S3")["temperature"]["value"]
    h3 = sum(v * (MAT[c]["ideal_gas"]["dHf_298"] + h_ig(c, t3)) for c, v in n3.items())
    n4 = kmol("S4")
    lo, hi = t3 - 50.0, t3
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        h4 = sum(v * (MAT[c]["ideal_gas"]["dHf_298"] + h_ig(c, mid)) for c, v in n4.items())
        lo, hi = (lo, mid) if h4 > h3 else (mid, hi)
    out["S4"] = {"temperature": round(0.5 * (lo + hi), 2)}

    # --- demethaniser bottoms at the bubble point (S26)
    x26 = state("S26")["composition"]["values"]
    out["S26"] = {"temperature": round(bubble_point(x26, state("S26")["pressure"]["value"]), 2)}

    # --- regeneration air (S8) and blower (S9, Q4)
    coke = kmol("S7")["COKE"]
    o2_in = coke / (1.0 - O2_DRY_FLUE / 0.21)  # dry flue: N2 + O2 + CO2 = O2_in / 0.21
    air_kmol = o2_in / 0.21
    air_kg = air_kmol * (0.79 * MAT["N2"]["molar_mass"] + 0.21 * MAT["O2"]["molar_mass"])
    blower, t_air = compression({"N2": 0.79 * air_kmol, "O2": 0.21 * air_kmol}, 298.15, 101.325, 300.0, 1, ETA_BLOWER)
    out["S8"] = {"flow": round(air_kg, 1)}
    out["S9"] = {"temperature": round(t_air, 2)}
    out["Q4"] = {"duty": round(blower, 1)}

    # --- caustic (S16)
    co2 = kmol("S15")["CO2"]
    naoh_kg = NAOH_PER_CO2 * co2 * MAT["NAOH"]["molar_mass"]
    out["S16"] = {"flow": round(naoh_kg / CAUSTIC_WT, 1)}

    # --- caustic tower liquor cooler Q26: CO2(g) + 2 NaOH -> Na2CO3 + H2O(l) on the formation
    # enthalpies of the solids, an upper bound (the heats of solution, not read, lower it)
    co2_reacted = co2 - kmol("S17").get("CO2", 0.0)
    dh_neut = HF_NA2CO3_S + HF_H2O_L - MAT["CO2"]["ideal_gas"]["dHf_298"] - 2.0 * HF_NAOH_S
    out["Q26"] = {"duty": round(-dh_neut * co2_reacted / 3600.0, 1)}
    print("heat of neutralisation (solids basis), kJ/mol CO2:", round(dh_neut / 1000.0, 2))

    # --- feed vaporiser Q1: liquid at 313.15 K to vapour at the S3 temperature
    n = kmol("S2")
    t_feed = state("S3")["temperature"]["value"]
    q1 = 0.0
    for c, v in n.items():
        tb = TB[c]
        q1 += v * (CPL[c] * (tb - 313.15) + HVAP_TB[c] + h_ig(c, t_feed) - h_ig(c, tb))
    out["Q1"] = {"duty": round(q1 / 3600.0, 1)}

    # --- quench Q5: S6 at 748.15 K to S11 (gas) and S12 (condensed) at 313.15 K
    n12 = kmol("S12")
    q5 = gas_enthalpy(n6, 748.15) - gas_enthalpy(n6, 313.15)
    q5 += sum(v * hvap(c, 313.15) for c, v in n12.items())
    out["Q5"] = {"duty": round(q5 / 3600.0, 1)}

    # --- oxygenate stripper Q6, Q7
    feed_kg = state("S36")["flow"]["value"]
    q6 = STRIP_STEAM * feed_kg * LPS_LATENT / 3600.0
    out["Q6"] = {"duty": round(q6, 1)}
    out["Q7"] = {"duty": round(q6, 1)}

    # --- product gas compressor: K301 200 -> 900 kPa(a), 3 stages; K302 880 -> 2069, 2 stages
    p301, _ = compression(kmol("S11"), 313.15, 200.0, 900.0, 3, ETA_COMP)
    water_ko = kmol("S14")["H2O"]
    out["Q8"] = {"duty": round(p301, 1)}
    out["Q9"] = {"duty": round(p301 + water_ko * hvap("H2O", 313.15) / 3600.0, 1)}
    n19 = kmol("S19")
    p302, _ = compression(n19, 313.15, 880.0, 2069.0, 2, ETA_COMP)
    sens = sum(v * cp_ig(c, 312.0) for c, v in n19.items() if "ideal_gas" in MAT[c]) * 2.0 / 3600.0
    # latent heat of what condenses into V302 (S40 aqueous, S41 hydrocarbon); dissolved gases
    # above their critical temperature (H2, CO, CO2, CH4, C2H4, C2H6) counted without one
    condensed: dict[str, float] = {}
    for sid in ("S40", "S41"):
        for c, v in kmol(sid).items():
            condensed[c] = condensed.get(c, 0.0) + v
    latent = sum(v * hvap(c, T_V302) for c, v in condensed.items()
                 if c in HVAP_TB and T_V302 < MAT[c]["critical"]["Tc"])
    out["Q10"] = {"duty": round(p302, 1)}
    out["Q11"] = {"duty": round(p302 + sens + latent / 3600.0, 1)}
    print("V302 condensation heat (kW):", round(latent / 3600.0, 1))

    # --- columns
    def condenser(step: str, top: str, key: str, total_reflux: bool = True) -> float:
        d = sum(kmol(top).values())
        factor = REFLUX[step] + (1.0 if total_reflux else 0.0)
        return factor * d * HVAP_TB[key] / 3600.0

    q13 = condenser("T401", "S23", "C2H4")
    d402_c2 = kmol("S25").get("C2H4", 0.0) + kmol("S25").get("CH4", 0.0)
    q14 = REFLUX["T402"] * sum(kmol("S25").values()) * HVAP_TB["C2H4"] / 3600.0
    q15 = condenser("T403", "S27", "C2H4")
    q17 = condenser("T501", "S29", "C3H6")
    q19 = condenser("T502", "S31", "C3H6")
    q21 = condenser("T503", "S33", "C4H8")
    out["Q12"] = {"duty": round(q13, 1)}
    out["Q13"] = {"duty": round(q13, 1)}
    out["Q14"] = {"duty": round(q14, 1)}
    out["Q15"] = {"duty": round(q15, 1)}
    out["Q16"] = {"duty": round(q17, 1)}
    out["Q17"] = {"duty": round(q17, 1)}
    out["Q18"] = {"duty": round(q19, 1)}
    out["Q19"] = {"duty": round(q19, 1)}
    out["Q20"] = {"duty": round(q21, 1)}
    out["Q21"] = {"duty": round(q21, 1)}
    out["Q24"] = {"duty": round(q14, 1)}   # demethaniser reboiler = condenser
    out["Q25"] = {"duty": round(q15, 1)}   # C2 splitter reboiler = condenser

    # --- refrigeration: T401's condenser duty lifted to cooling water; T402's and T403's lifted
    # to their reboilers (which take it back), the work of that lift then to cooling water
    power = q13 / cop(T_EVAP["T401"], T_COND_REF)
    rejected = q13 + power
    for step, q in (("T402", q14), ("T403", q15)):
        w1 = q / cop(T_EVAP[step], T_REB_HEAT[step])
        w2 = w1 / cop(T_REB_HEAT[step], T_COND_REF)
        power += w1 + w2
        rejected += w1 + w2
    out["Q22"] = {"duty": round(power, 1)}
    out["Q23"] = {"duty": round(rejected, 1)}

    for sid, val in out.items():
        print(sid, val)
    plant_energy_check(out)
    print("cross-check: C2 in the tail gas (kmol/h)", round(d402_c2, 3))
    prod = state("S27")["flow"]["value"] + state("S31")["flow"]["value"]
    print("methanol per ethylene + propylene (t/t)", round(state("S1")["flow"]["value"] / prod, 4))
    return out


def plant_energy_check(out: dict) -> None:
    """Cross-check: the plant's first-law balance over its feeds, products and utilities
    (ideal-gas enthalpies with formation enthalpies; liquid streams less their heats of
    vaporisation; the coke-free streams only). The caustic loop (S16, S18) and its liquor
    cooler Q26 are left out: NaOH and Na2CO3 have no ideal-gas data."""
    def h(sid: str, liquid: bool) -> float:
        t = state(sid)["temperature"]["value"]
        total = 0.0
        for c, v in kmol(sid).items():
            hc = MAT[c]["ideal_gas"]["dHf_298"] + h_ig(c, t)
            if liquid and c in HVAP_TB and t < MAT[c]["critical"]["Tc"]:
                hc -= hvap(c, t)
            total += v * hc
        return total / 3600.0
    liquids = {"S1", "S31", "S33", "S34", "S38"}
    h_in = sum(h(s, s in liquids) for s in ("S1", "S8"))
    h_out = sum(h(s, s in liquids) for s in ("S10", "S27", "S31", "S33", "S34", "S35", "S38"))
    duty = {s["id"]: s["state"]["design"]["duty"]["value"] for s in FS["streams"] if s.get("kind") == "energy"}
    duty.update({k: v["duty"] for k, v in out.items() if "duty" in v})
    q_in = sum(duty[q] for q in ("Q1", "Q4", "Q6", "Q8", "Q10", "Q12", "Q16", "Q18", "Q20", "Q22"))
    q_out = sum(duty[q] for q in ("Q2", "Q3", "Q5", "Q7", "Q9", "Q11", "Q17", "Q19", "Q21", "Q23"))
    print("cross-check: plant energy balance (MW): feeds", round(h_in / 1e3, 1), "+ utilities in",
          round(q_in / 1e3, 1), "- products", round(h_out / 1e3, 1), "- utilities out",
          round(q_out / 1e3, 1), "=", round((h_in + q_in - h_out - q_out) / 1e3, 2))


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    write_balance_output({"design": main()})
