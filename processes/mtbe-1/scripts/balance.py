"""What core cannot calculate in the MTBE plant (DESIGN.md D-008).

`cheme process propagate --fill` solves the material balance from process/flowsheet.yaml: the
fresh methanol and the make-up water (design specifications), the reactive zone R101
(conversion step), the component separators C101, C201 and C202, the purge split and the two
recycles (tears S16 and S20). The column C-101's reboiler and condenser duties are the source's
(Murat et al. 2003, Table 2; DESIGN.md SRC-1). This script reads the propagated streams and
gives what core has no model for:

- the outlet temperature of the adiabatic methanol mixer M101 (S6) and the temperature of
  C-202's condensate (S16, its bubble point at the column top's pressure);
- the duties of the raffinate vaporiser E-104 (Q1), the methanol feed heater E-103 (Q2), the
  product and distillate coolers (Q5, Q6), the methanol column C-202 (Q7, Q8) and the
  wash-water cooler E-201 (Q9), and the pumps (P1, P2).

Enthalpy basis: liquids from 298.15 K, each component's liquid heat capacity integrated over the
stream's own temperature range (thermo 0.6.1's HeatCapacityLiquid), vapours through the heat of
vaporization at the temperature named. No property package of core covers these liquids
(DESIGN.md L-2); heats of mixing are left out. The script also prints, as a cross-check, the
energy balance of C-101 with the source's duties on this basis (DESIGN.md D-008).

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

# Liquid heat capacities: thermo 0.6.1's HeatCapacityLiquid with its default method (HEOS_FIT for
# methanol, water, isobutene and 1-butene; ZABRANSKY_SPLINE for MTBE), integrated from 298.15 K to
# each stream's temperature (single facts with the package named, library ADR 0037; DESIGN.md
# SRC-6). Over the duties' own ranges the means are, in kJ/(kmol K): 1-butene 138.8 and isobutene
# 143.0 (298-350 K), methanol 87.2 (298-350 K), MTBE 215.4 (313-424 K). A mean taken up to the
# column bottom's 424 K would pass the critical temperatures of 1-butene (419.3 K) and isobutene
# (418.1 K), where the pure liquid's heat capacity diverges; the C4 reach that range only as the
# 1.4 mol% dissolved in the bottoms (S10).
CAS = {"MEOH": "67-56-1", "H2O": "7732-18-5", "MTBE": "1634-04-4", "B1": "106-98-9", "IB": "115-11-7"}
# Heats of vaporization, kJ/kmol: thermo 0.6.1's EnthalpyVaporization (HEOS_FIT) at the
# vaporiser's 350 K and at C-202's top, 345.3 K (DESIGN.md SRC-6)
HVAP_350 = {"IB": 16229.0, "B1": 16374.0, "MEOH": 34476.0, "H2O": 41722.0}
HVAP_TOP202 = {"MEOH": 34790.0, "H2O": 41934.0, "B1": 16793.0, "IB": 16656.0}
# Liquid densities, kg/m3: thermo 0.6.1's VolumeLiquid at 313.15 K (C4 at 348.15 K for the
# reflux of C-101), for the pumps; method HEOS_FIT for 1-butene (C4), methanol and water,
# DIPPR_PERRY_8E for MTBE (Perry's Chemical Engineers' Handbook, 8th ed., drawing on DIPPR 801;
# not read here, library ADR 0037)
RHO = {"C4": 568.8, "C4HOT": 517.9, "MEOH": 772.2, "H2O": 992.2, "MTBE": 720.4}

# design choices (DESIGN.md D-007, D-008), ASSUMED
C202_REFLUX = 1.5  # reflux ratio of the methanol column
C202_TOP_KPA = 136.0  # C-202's top pressure, kPa(a)
C202_TOP_T = 345.3  # C-202's top vapour, K: methanol's boiling point at 136 kPa(a) (SRC-6)
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


_CHEM: dict = {}


def chem(c: str):
    """thermo's Chemical for a component id (cached)."""
    if c not in _CHEM:
        from thermo import Chemical

        _CHEM[c] = Chemical(CAS[c])
    return _CHEM[c]


def h_liq(n: dict[str, float], t: float) -> float:
    """Liquid enthalpy above 298.15 K, kW: thermo's liquid heat capacity integrated from T0 to t."""
    # kmol/h x J/mol (= kJ/kmol) -> kJ/h -> kW
    return sum(v * chem(c).HeatCapacityLiquid.T_dependent_property_integral(T0, t) for c, v in n.items()) / 3600.0


def bubble_t(n: dict[str, float], p_kpa: float) -> float:
    """Bubble point of a liquid, K: modified UNIFAC (Dortmund) activity coefficients and thermo's
    vapour pressures, ideal vapour (thermo 0.6.1; an estimate, DESIGN.md D-007)."""
    from scipy.optimize import brentq
    from thermo.unifac import DOUFIP2016, DOUFSG, UNIFAC

    ids = list(n)
    total = sum(n.values())
    xs = [n[c] / total for c in ids]
    ge = UNIFAC.from_subgroups(T=330.0, xs=xs, chemgroups=[chem(c).UNIFAC_Dortmund_groups for c in ids],
                               version=1, interaction_data=DOUFIP2016, subgroups=DOUFSG)

    def residual(t: float) -> float:
        gammas = ge.to_T_xs(t, xs).gammas()
        return sum(x * g * chem(c).VaporPressure(t) for x, g, c in zip(xs, gammas, ids)) / 1000.0 - p_kpa

    return brentq(residual, 300.0, 400.0)


def main() -> None:
    fs, comps = load()
    streams = {s["id"]: s for s in fs["streams"] if s.get("kind") != "energy"}
    n = {sid: kmol(s, comps) for sid, s in streams.items()}
    temp = {sid: s["state"]["design"]["temperature"]["value"] for sid, s in streams.items()}
    mass = {sid: s["state"]["design"]["flow"]["value"] for sid, s in streams.items()}
    out: dict[str, dict] = {}

    # C-202's condensate: the overhead vapour (C202_TOP_T, its dew point is methanol's boiling
    # point) condensed totally and leaving the reflux drum at its bubble point at the top pressure,
    # so that the dissolved C4 stays in the liquid (DESIGN.md D-007)
    t16 = bubble_t(n["S16"], C202_TOP_KPA)
    out["S16"] = {"temperature": round(t16, 2)}

    # M101: fresh methanol S5 and the recycle S16 mixed adiabatically -> S6
    from scipy.optimize import brentq

    n6 = {c: n["S5"].get(c, 0.0) + n["S16"].get(c, 0.0) for c in set(n["S5"]) | set(n["S16"])}
    h_in = h_liq(n["S5"], temp["S5"]) + h_liq(n["S16"], t16)
    t6 = brentq(lambda t: h_liq(n6, t) - h_in, 280.0, 400.0)
    out["S6"] = {"temperature": round(t6, 2)}

    # E-104: the raffinate heated as liquid to 350 K and vaporised there (S3 -> S4)
    t4 = temp["S4"]
    q1 = h_liq(n["S3"], t4) - h_liq(n["S3"], temp["S3"]) + sum(v * HVAP_350[c] for c, v in n["S3"].items()) / 3600.0
    # E-103: the methanol heated to the column's 320 K (S6 -> S7)
    q2 = h_liq(n["S7"], temp["S7"]) - h_liq(n["S6"], t6)
    # E-101 and E-102: the bottoms and the distillate cooled to 313.15 K
    q5 = h_liq(n["S10"], temp["S10"]) - h_liq(n["S11"], temp["S11"])
    q6 = h_liq(n["S9"], temp["S9"]) - h_liq(n["S12"], temp["S12"])
    # C-202: total condenser at reflux C202_REFLUX, the vapour condensed at C202_TOP_T and the
    # condensate cooled to its bubble point t16; reboiler from the column's balance (feed S15, top
    # S16 at t16, bottoms S17)
    q8 = (C202_REFLUX + 1.0) * (sum(v * HVAP_TOP202[c] for c, v in n["S16"].items()) / 3600.0
                                + h_liq(n["S16"], C202_TOP_T) - h_liq(n["S16"], t16))
    q7 = q8 + h_liq(n["S16"], t16) + h_liq(n["S17"], temp["S17"]) - h_liq(n["S15"], temp["S15"])
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

    # Cross-check, not a flowsheet value: C-101's energy balance with the source's Q3 and Q4 on
    # this script's basis (liquids at 298.15 K). The heat of reaction in the liquid at 298.15 K is
    # the ideal-gas value of process/reactions.yaml corrected by thermo's heats of vaporization.
    reactions = yaml.safe_load((ROOT / "process/reactions.yaml").read_text(encoding="utf-8"))
    rxn = reactions["reactions"][0]
    dh_liq = rxn["heat_of_reaction"]["value"] / 1000.0 + sum(  # kJ/mol
        -nu * chem(c).EnthalpyVaporization(T0) / 1000.0 for c, nu in rxn["stoichiometry"].items())
    extent = n["S8"]["MTBE"] - n["S4"].get("MTBE", 0.0) - n["S7"].get("MTBE", 0.0)  # kmol/h
    q3 = next(s["state"]["design"]["duty"]["value"] for s in fs["streams"] if s["id"] == "Q3")
    q4 = next(s["state"]["design"]["duty"]["value"] for s in fs["streams"] if s["id"] == "Q4")
    c101_in = q1 + h_liq(n["S7"], temp["S7"]) + q3 - extent * dh_liq / 3.6
    c101_out = h_liq(n["S9"], temp["S9"]) + h_liq(n["S10"], temp["S10"]) + q4
    print(f"C-101 cross-check: liquid heat of reaction {dh_liq:.2f} kJ/mol, in {c101_in:.0f} kW, "
          f"out {c101_out:.0f} kW, residual {c101_in - c101_out:.0f} kW "
          f"({(c101_in - c101_out) / c101_in * 100:.1f} % of the input)")

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": {"design": out}}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
