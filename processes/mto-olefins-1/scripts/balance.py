"""Shortcut duties and the air and caustic feeds of mto-olefins-1 (DESIGN.md D-011).

Run with `cheme run scripts/balance.py` from the process folder. It reads the flows and
compositions that `cheme process propagate --fill` wrote into process/flowsheet.yaml and the
ideal-gas data of process/materials.yaml, and prints, for the values the flowsheet gives as
`assumed` with the source "scripts/balance.py":

- S8: the regeneration air for complete coke combustion with 2 vol% O2 in the dry flue gas;
- S9: the air blower's discharge temperature;
- S16: the fresh caustic, 3 mol NaOH per mol CO2 in the gas (ASSUMED excess), 10 wt%;
- Q1: the feed vaporiser (liquid to the normal boiling point, vaporisation, vapour superheat);
- Q4, Q8 to Q11: the blower and the product gas compressor (ideal gas, isentropic efficiency
  ASSUMED, intercooled to the stage inlet temperature) and its coolers (with the latent heat of
  the water knocked out in V301);
- Q5: the quench tower (the gas cooled from 748 K to 313 K, the water and oxygenates condensed);
- Q6, Q7: the oxygenate stripper (stripping steam per kg of feed, ASSUMED);
- Q12 to Q21: the columns, reflux ratios ASSUMED: (R + 1) x distillate x heat of vaporisation at
  the normal boiling point, reboiler = condenser;
- Q22, Q23: the refrigeration compressors at 60 % of the Carnot COP (ASSUMED) and their heat
  rejected to cooling water.

The reactor and regenerator duties Q2 and Q3 are core's conversion-step duties (cheme process
propagate writes them); this script does not give them.

Heats of vaporisation and liquid heat capacities: the `chemicals` 1.5.2 package's packaged CRC
tables (`phase_change.Hvap_data_CRC`, `heat_capacity.CRC_standard_data`), single values with
their source, not open data (library ADR 0037, DESIGN.md SRC-6). Shortcut estimates for a
concept study: no property package of core covers this mixture (L-1).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
R = 8.314462618  # kJ/(kmol K)
T0 = 298.15

MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())["components"]}
FS = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text())
STREAMS = {s["id"]: s for s in FS["streams"]}

# Heat of vaporisation at the normal boiling point (kJ/kmol) and liquid heat capacity
# (kJ/(kmol K)): chemicals 1.5.2, Hvap_data_CRC 'HvapTb' and CRC_standard_data 'Cpl'.
HVAP_TB = {"MEOH": 35210.0, "DME": 21510.0, "H2O": 40650.0, "C2H4": 13530.0, "C3H6": 18420.0,
           "C3H8": 19040.0, "C2H6": 14690.0, "C4H8": 22070.0, "C5H10": 25200.0}
TB = {"MEOH": 337.75, "DME": 248.35, "H2O": 373.12}
CPL = {"MEOH": 81.1, "H2O": 75.3, "DME": 102.0}  # DME: no CRC value; ASSUMED near methanol's per carbon
# Watson exponent 0.38 with Tc of materials.yaml, for the heat of vaporisation at 313 K.
WATSON = 0.38

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


def main() -> dict:
    out: dict[str, dict] = {}

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

    # --- feed vaporiser Q1: liquid at 313.15 K to vapour at 473.15 K
    n = kmol("S2")
    q1 = 0.0
    for c, v in n.items():
        tb = TB[c]
        q1 += v * (CPL[c] * (tb - 313.15) + HVAP_TB[c] + h_ig(c, 473.15) - h_ig(c, tb))
    out["Q1"] = {"duty": round(q1 / 3600.0, 1)}

    # --- quench Q5: S6 at 748.15 K to S11 (gas) and S12 (condensed) at 313.15 K
    n6 = {c: v for c, v in kmol("S6").items() if c != "COKE"}
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
    out["Q10"] = {"duty": round(p302, 1)}
    out["Q11"] = {"duty": round(p302 + sens, 1)}

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

    # --- refrigeration
    power = 0.0
    for step, q in (("T401", q13), ("T402", q14), ("T403", q15)):
        te = T_EVAP[step]
        cop = COP_FRACTION * te / (T_COND_REF - te)
        power += q / cop
    out["Q22"] = {"duty": round(power, 1)}
    out["Q23"] = {"duty": round(q13 + q14 + q15 + power, 1)}

    for sid, val in out.items():
        print(sid, val)
    print("cross-check: C2 in the tail gas (kmol/h)", round(d402_c2, 3))
    prod = state("S27")["flow"]["value"] + state("S31")["flow"]["value"]
    print("methanol per ethylene + propylene (t/t)", round(state("S1")["flow"]["value"] / prod, 4))
    return out


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
