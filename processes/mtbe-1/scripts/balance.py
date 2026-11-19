"""What core cannot calculate in the MTBE plant (DESIGN.md D-008).

`cheme process propagate --fill` solves the material balance from process/flowsheet.yaml: the
fresh methanol and the make-up water (design specifications), the reactive zone R101
(conversion step), the component separators C101, C201 and C202, the purge split and the two
recycles (tears S16 and S20). The column C-101's reboiler and condenser duties are the source's
(Murat et al. 2003, Table 2; DESIGN.md SRC-1). This script reads the propagated streams and
gives what core has no model for:

- the outlet temperature of the adiabatic methanol mixer M101 (S6);
- the duties of the raffinate vaporiser E-104 (Q1), the methanol feed heater E-103 (Q2), the
  product and distillate coolers (Q5, Q6), the methanol column C-202 (Q7, Q8) and the
  wash-water cooler E-201 (Q9), and the pumps (P1, P2).

Enthalpy basis: liquids from 298.15 K at a constant heat capacity (each component's mean over
298.15-424.15 K), vapours through the heat of vaporization at the temperature named. No property
package of core covers these liquids (DESIGN.md L-2); heats of mixing are left out.

Run: cheme run scripts/balance.py (prints the table; writes the balance-output JSON of the
library's ADR 0027 when BALANCE_OUTPUT names a file).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
T0 = 298.15

# Liquid heat capacities, kJ/(kmol K): thermo 0.6.1's HeatCapacityLiquid (HEOS_FIT for methanol,
# water, isobutene and 1-butene; ZABRANSKY_SPLINE for MTBE), each averaged over 298.15-424.15 K
# (single facts with the package named, library ADR 0037; DESIGN.md SRC-6)
CP_LIQ = {"MEOH": 99.1, "H2O": 76.0, "MTBE": 212.5, "B1": 166.2, "IB": 171.6}
# Heats of vaporization, kJ/kmol: thermo 0.6.1's EnthalpyVaporization (HEOS_FIT) at the
# vaporiser's 350 K and at C-202's top, 345.3 K (DESIGN.md SRC-6)
HVAP_350 = {"IB": 16229.0, "B1": 16374.0, "MEOH": 34476.0, "H2O": 41722.0}
HVAP_TOP202 = {"MEOH": 34790.0, "H2O": 41934.0, "B1": 16793.0, "IB": 16656.0}
# Liquid densities, kg/m3: thermo 0.6.1's VolumeLiquid at 313.15 K (C4 at 348.15 K for the
# reflux of C-101), for the pumps
RHO = {"C4": 568.8, "C4HOT": 517.9, "MEOH": 772.2, "H2O": 992.2, "MTBE": 720.4}

# design choices (DESIGN.md D-007, D-008), ASSUMED
C202_REFLUX = 1.5  # reflux ratio of the methanol column
C101_REFLUX = 7.0  # Murat et al. (2003) Table 1: reflux ratio 7 (given)
PUMP_EFF = 0.65  # pump and motor
DP = {  # pressure rises, kPa
    "c4_feed": 1000.0,  # raffinate from storage to the vaporiser
    "meoh_feed": 1000.0,  # fresh methanol
    "c101_reflux": 300.0,
    "mtbe": 300.0,  # bottoms to storage
    "wash": 940.0,  # C-202's bottoms (160 kPa(a)) to the wash (1100 kPa(a))
    "c202_reflux": 200.0,
    "meoh_rec": 1164.0,  # C-202's top (136 kPa(a)) to the methanol feed (1300 kPa(a))
}


def load():
    flowsheet = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text(encoding="utf-8"))
    materials = yaml.safe_load((ROOT / "process/materials.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in materials["components"]}
    return flowsheet, comps


def kmol(stream: dict, comps: dict) -> dict[str, float]:
    """Component flows in kmol/h of a propagated stream (flow in kg/h)."""
    st = stream["state"]["design"]
    comp = st["composition"]
    x = {c: v for c, v in comp["values"].items() if v > 0}
    flow = st["flow"]["value"]
    if comp["basis"] == "mole_fraction":
        total = flow / sum(v * comps[c]["molar_mass"] for c, v in x.items())
        return {c: total * v for c, v in x.items()}
    return {c: flow * v / comps[c]["molar_mass"] for c, v in x.items()}


def h_liq(n: dict[str, float], t: float) -> float:
    """Liquid enthalpy above 298.15 K, kW."""
    return sum(v * CP_LIQ[c] * (t - T0) for c, v in n.items()) / 3600.0


def main() -> None:
    fs, comps = load()
    streams = {s["id"]: s for s in fs["streams"] if s.get("kind") != "energy"}
    n = {sid: kmol(s, comps) for sid, s in streams.items()}
    temp = {sid: s["state"]["design"]["temperature"]["value"] for sid, s in streams.items()}
    mass = {sid: s["state"]["design"]["flow"]["value"] for sid, s in streams.items()}
    out: dict[str, dict] = {}

    # M101: fresh methanol S5 and the recycle S16 mixed adiabatically -> S6
    ncp = {sid: sum(v * CP_LIQ[c] for c, v in n[sid].items()) for sid in ("S5", "S16")}
    t6 = T0 + (ncp["S5"] * (temp["S5"] - T0) + ncp["S16"] * (temp["S16"] - T0)) / sum(ncp.values())
    out["S6"] = {"temperature": round(t6, 2)}

    # E-104: the raffinate heated as liquid to 350 K and vaporised there (S3 -> S4)
    t4 = temp["S4"]
    q1 = h_liq(n["S3"], t4) - h_liq(n["S3"], temp["S3"]) + sum(v * HVAP_350[c] for c, v in n["S3"].items()) / 3600.0
    # E-103: the methanol heated to the column's 320 K (S6 -> S7)
    q2 = h_liq(n["S7"], temp["S7"]) - h_liq(n["S6"], t6)
    # E-101 and E-102: the bottoms and the distillate cooled to 313.15 K
    q5 = h_liq(n["S10"], temp["S10"]) - h_liq(n["S11"], temp["S11"])
    q6 = h_liq(n["S9"], temp["S9"]) - h_liq(n["S12"], temp["S12"])
    # C-202: total condenser at reflux C202_REFLUX; reboiler from the column's balance on
    # saturated liquids (feed S15, top S16 at its bubble point, bottoms S17)
    t_top = temp["S16"]
    q8 = (C202_REFLUX + 1.0) * sum(v * HVAP_TOP202[c] for c, v in n["S16"].items()) / 3600.0
    q7 = q8 + h_liq(n["S16"], t_top) + h_liq(n["S17"], temp["S17"]) - h_liq(n["S15"], temp["S15"])
    # E-201: the column's water cooled to the wash temperature
    q9 = h_liq(n["S17"], temp["S17"]) - h_liq(n["S18"], temp["S18"])

    def pump(kg_h: float, rho: float, dp_kpa: float) -> float:
        return kg_h / 3600.0 / rho * dp_kpa / PUMP_EFF  # kW

    p1 = (pump(mass["S3"], RHO["C4"], DP["c4_feed"]) + pump(mass["S5"], RHO["MEOH"], DP["meoh_feed"])
          + pump(C101_REFLUX * mass["S9"], RHO["C4HOT"], DP["c101_reflux"])
          + pump(mass["S10"], RHO["MTBE"], DP["mtbe"]))
    p2 = (pump(mass["S18"], RHO["H2O"], DP["wash"]) + pump(C202_REFLUX * mass["S16"], RHO["MEOH"], DP["c202_reflux"])
          + pump(mass["S16"], RHO["MEOH"], DP["meoh_rec"]))

    for key, value in (("Q1", q1), ("Q2", q2), ("Q5", q5), ("Q6", q6), ("Q7", q7), ("Q8", q8), ("Q9", q9),
                       ("P1", p1), ("P2", p2)):
        out[key] = {"duty": round(value, 1)}

    for k, v in out.items():
        print(k, v)
    product = mass["S11"]
    print(f"per kg of product: LP steam {(q1 + q2 + q7) / product:.4f} kWh, power {(p1 + p2) / product:.5f} kWh")

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": {"design": out}}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
