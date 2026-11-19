"""What core does not calculate in the 4-aminophenol plant (DESIGN.md D-003, D-008, D-009).

Year-average flows (kg/h, the recipe's basis, D-003). `cheme process propagate --fill` computes
the semi-batch R101, the stills ST101 and ST102 (their boil-up and condensers: the latent heat
of the vapour only), the neutralisation N101, the crystallizer CR101, the wash W101, the dryer
D101 and the recycles. This script gives, from the streams propagate wrote and the liquid heat
capacities of process/materials.yaml (ideal mixing), the sensible heats and vessel metals those
models leave out (core's batch still counts no heat-up with constant volatilities, a separator
exchanges no heat), so that every heat flow of the batch is on an energy stream (D-009):

- Q1: the charge heated to 358.15 K and R-101's metal back from 333.15 K, less the acid's
  heat of dilution (59.2 kJ/mol, derived from SRC-2 Example 1, ASSUMED);
- Q10: R-101's mass and metal cooled from 358.15 to 333.15 K for the settling;
- Q11: the strip's charge S7 and R-102's metal heated from 333.15 K to the boil (373.12 K);
- Q12: the strip distillate S21 subcooled from 373.12 to 313.15 K in E-102;
- Q13: the neutralised liquor S11 and R-103's metal heated from 363.15 K to the boil, and the
  water fed at constant level, S29, warmed from 298.15 K (in E-105 to 363 K, the rest in R-103);
- Q14: the aniline distillate S12 cooled from 373.12 to 298.15 K for V-102;
- Q15: the dryer's vapour S27 condensed in E-103 at 313 K;
- Q16: K-101's metal cooled from 371.15 to 283.15 K each batch;
- Q17: R-102's metal cooled from 373.12 to 363.15 K with the liquor in the neutralisation;
- P1: R-101's agitator, SRC-1's lower end of 15 HP per 1000 US gallons on the batch volume,
  running through the charge, the dose, the purge and the cool-down.

It also prints the hand checks the recipe relies on (the heat-up times of R-102 and R-103, the
neutralisation's time on R-102's jacket, K-101's cool-down) and the numbers DESIGN.md quotes.

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill` and `cheme process
recipe`. With BALANCE_OUTPUT set it writes the values the flowsheet cites (library ADR 0027).
Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

T_AMB = 298.15  # K, the feeds (design basis)
T_REACT = 358.15  # K, R101 (D-005)
T_SETTLE = 333.15  # K, V101 (D-006)
T_BOIL = 373.12  # K, water's normal boiling point (materials.yaml), the stills' pots
T_NEU = 363.15  # K, the neutralised liquor S11 (D-007)
T_FILTER = 371.15  # K, the hot filtration through F-101 (SRC-1: 98 to 100 C)
T_CRYST = 283.15  # K, K-101 (D-008)
T_S21 = 313.15  # K, the strip distillate held in T-101 (flowsheet S21)
T_V102 = 298.15  # K, V-102 (D-008)
T_E103 = 313.15  # K, the dryer's condensate leaving E-103 on cooling water (D-009)
T_DRY = 333.15  # K, D101 (flowsheet)
DILUTION = 59_200.0  # kJ/kmol H2SO4, the acid's heat of dilution in the charge (D-009)
# kJ/K of the vessels' metal: R-101 and R-102 / R-103 as recipe.yaml; K-101 (16 m3, no vessel in
# the recipe, L-5) scaled from R-101's 6500 kJ/K for 20 m3 by volume
METAL = {"R-101": 8000.0, "R-102": 7500.0, "R-103": 7500.0, "K-101": 5100.0}
# kJ/kg, the dryer's vapour at 333.15 K (flowsheet D101: thermo 0.6.1 Hvap)
LATENT = {"H2O": 2357.7, "NB": 413.5, "AN": 532.4, "NH3": 1166.0}
# SRC-1: "15 to 25 HP per 1000 gallons"; the lower end, 1 HP = 0.7457 kW, 1000 US gal = 3.7854 m3
AGITATION = 15 * 0.7457 / 3.7854  # kW per m3 of batch
R101_BATCH_M3 = 15.24  # m3 of R-101's batch, as `cheme process recipe` sizes it (a test compares)
# h of R-101's cycle the agitator runs: the charge 1.5, the dose 5.5, the purge 0.25 and the
# cool-down 1.33 (recipe.yaml, `cheme process recipe`); off while the phases settle and drain
R101_AGITATED_H = 1.5 + 5.5 + 0.25 + 1.33
# the stills' boil-up on LP steam (flowsheet ST101, ST102, D-007): R-102's jacket 390 kW, R-103's
# jacket and coil 600 kW; on cooling water U 300 W/(m2 K)
BOILUP = {"R-102": 390.0, "R-103": 600.0}  # kW
U_COOL = 0.300  # kW/(m2 K)
R102_AREA = 25.0  # m2 wetted at about 13 m3 in R-102 (D 2.77 m), as R-101's at the charge
T_CW_MEAN = 303.15  # K, cooling water between 298.15 and 308.15 K
T_CHW = 278.15  # K, chilled water supply (design basis)
# m2, K-101 (16 m3, D 2.57 m at an aspect of 1.2): about 22 m2 of jacket wetted at about 11 m3 of
# liquor and an internal coil of about 10 m2 (ASSUMED)
K101_AREA = 32.0
# The Merck Index solubility of 4-aminophenol in water at 96 C, 8.5 wt% (SRC-10)
HOT_SOLUBILITY = 0.085 / (1 - 0.085)  # kg per kg of water at 369.15 K


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "process" / name).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in load("materials.yaml")["components"]}
MW = {n: c["molar_mass"] for n, c in MATERIALS.items()}
CP = {n: c.get("liquid_heat_capacity", 0.0) for n, c in MATERIALS.items()}
FLOWSHEET = load("flowsheet.yaml")
STREAMS = {s["id"]: s["state"]["design"] for s in FLOWSHEET["streams"]}
RECIPE = load("recipe.yaml")


def kg(sid: str) -> dict[str, float]:
    """kg/h of each component of stream *sid*."""
    state = STREAMS[sid]
    flow, comp = state["flow"]["value"], state["composition"]
    if comp["basis"] == "mass_fraction":
        return {k: flow * v for k, v in comp["values"].items()}
    mean = sum(v * MW[k] for k, v in comp["values"].items())
    return {k: flow * v * MW[k] / mean for k, v in comp["values"].items()}


def capacity(sid: str) -> float:
    """kW/K of stream *sid*: sum of kmol/h x kJ/(kmol K) / 3600."""
    return sum(m / MW[k] * CP[k] for k, m in kg(sid).items()) / 3600.0


def flow(sid: str) -> float:
    return STREAMS[sid]["flow"]["value"]


def duty(sid: str) -> float:
    return STREAMS[sid]["duty"]["value"]


def main() -> None:
    hours = RECIPE["batch_size"]["value"] / flow("S26")  # h of flows one batch makes (the cycle)

    def metal(tag: str, dt: float) -> float:  # kW, year average
        return METAL[tag] * dt / hours / 3600.0

    inlets = {"S1": T_AMB, "S2": T_AMB, "S3": T_AMB, "S22": T_AMB, "S20": T_SETTLE, "S21": T_S21}
    sensible = sum(capacity(s) * (T_REACT - t) for s, t in inlets.items())
    acid = kg("S3")["H2SO4"] / MW["H2SO4"]
    q1 = sensible - acid * DILUTION / 3600.0 + metal("R-101", T_REACT - T_SETTLE)
    q10 = capacity("S6") * (T_REACT - T_SETTLE) + metal("R-101", T_REACT - T_SETTLE)
    q11 = capacity("S7") * (T_BOIL - T_SETTLE) + metal("R-102", T_BOIL - T_SETTLE)
    q12 = capacity("S21") * (T_BOIL - T_S21)
    q13_jacket = capacity("S11") * (T_BOIL - T_NEU) + capacity("S29") * (T_BOIL - T_NEU) + metal("R-103", T_BOIL - T_NEU)
    q13_e105 = capacity("S29") * (T_NEU - T_AMB)
    q13 = q13_jacket + q13_e105
    q14 = capacity("S12") * (T_BOIL - T_V102)
    q15 = sum(m * LATENT[k] for k, m in kg("S27").items() if k in LATENT) / 3600.0 + capacity("S27") * (T_DRY - T_E103)
    q16 = metal("K-101", T_FILTER - T_CRYST)
    q17 = metal("R-102", T_BOIL - T_NEU)
    p1 = AGITATION * R101_BATCH_M3 * R101_AGITATED_H / hours

    print(f"cycle (batch hours) {hours:.3f} h; R-101 agitator {AGITATION * R101_BATCH_M3:.1f} kW while running")
    print(f"Q1  {q1:8.3f} kW  (sensible {sensible:.2f}, dilution -{acid * DILUTION / 3600:.2f}, metal {metal('R-101', 25):.2f})")
    for name, v in (("Q10", q10), ("Q11", q11), ("Q12", q12), ("Q13", q13), ("Q14", q14), ("Q15", q15), ("Q16", q16), ("Q17", q17), ("P1", p1)):
        print(f"{name:4s}{v:8.3f} kW")
    print(f"  Q13: in R-103's jacket {q13_jacket:.2f} kW, in the water preheater E-105 {q13_e105:.2f} kW")

    # the recipe's hand durations
    print(f"R-102 heat-up 333 -> 373 K at the boil-up's {BOILUP['R-102']:g} kW: {q11 * hours / BOILUP['R-102']:.2f} h")
    print(f"R-103 heat-up (liquor, metal, the water fed from 363 K) at {BOILUP['R-103']:g} kW: {q13_jacket * hours / BOILUP['R-103']:.2f} h")
    removable = U_COOL * R102_AREA * ((T_BOIL + T_NEU) / 2 - T_CW_MEAN)
    neutral = (duty("Q4") + q17) * hours
    print(f"neutralisation: {neutral:.0f} kWh a batch, R-102's jacket removes {removable:.0f} kW: {neutral / removable:.2f} h")
    cp13 = capacity("S13") * 3600.0 / flow("S13")
    cap_k = capacity("S13") * hours * 3600.0 + METAL["K-101"]  # kJ/K
    t_k = cap_k / (U_COOL * K101_AREA) * math.log((T_FILTER - T_CHW) / (T_CRYST - T_CHW)) / 3600.0
    print(f"S13 heat capacity {cp13:.3f} kJ/(kg K); K-101 cool-down on chilled water at {T_CHW} K: {t_k:.2f} h; "
          f"{(duty('Q7') + q16) * hours:.0f} kWh a batch")

    # numbers DESIGN.md quotes
    s7, s21, s13, s16 = kg("S7"), kg("S21"), kg("S13"), kg("S16")
    print(f"S7 nitrobenzene {s7['NB']:.3f} kg/h in {s7['H2O']:.1f} kg/h water: {100 * s7['NB'] / s7['H2O']:.2f} wt% of its water")
    print(f"heel S20 {flow('S20'):.2f} kg/h, {100 * flow('S20') / flow('S2'):.1f} % of the fresh nitrobenzene")
    print(f"strip returns {100 * s21['NB'] / s7['NB']:.1f} % of the dissolved nitrobenzene")
    print(f"S13: 4-aminophenol {s13['PAP']:.1f} kg/h in {s13['H2O']:.1f} kg/h water, {s13['PAP'] / s13['H2O']:.3f} kg/kg "
          f"(pure water at 369 K, SRC-10: {HOT_SOLUBILITY:.3f}); ammonium sulfate {s13['AS'] / s13['H2O']:.3f} kg/kg")
    print(f"S16 ammonium sulfate {s16['AS'] / s16['H2O']:.3f} kg per kg of water")
    pap = sum(v for k, v in kg("S26").items() if k in ("PAP", "PAP_S"))
    y = pap / MW["PAP"] / (kg("S2")["NB"] / MW["NB"])
    print(f"yield on fresh nitrobenzene {100 * y:.1f} %; product {100 * pap / flow('S26'):.1f} wt%")
    loss = sum(v for k, v in s16.items() if k in ("PAP", "PAP_S"))
    print(f"4-aminophenol in the mother liquor {loss:.2f} kg/h, {100 * loss / (loss + pap):.1f} % of the crystallised and lost")
    ww = kg("S28")
    print(f"liquor S28 {flow('S28'):.2f} kg/h, {flow('S28') / flow('S26'):.2f} kg/kg, ammonium sulfate {100 * ww['AS'] / flow('S28'):.1f} wt%, "
          f"NH4-N {ww['AS'] * 28.0134 / MW['AS']:.1f} kg/h")

    write_balance_output(
        {
            "design": {
                "Q1": {"duty": round(q1, 3)},
                "Q10": {"duty": round(q10, 3)},
                "Q11": {"duty": round(q11, 3)},
                "Q12": {"duty": round(q12, 3)},
                "Q13": {"duty": round(q13, 3)},
                "Q14": {"duty": round(q14, 3)},
                "Q15": {"duty": round(q15, 3)},
                "Q16": {"duty": round(q16, 3)},
                "Q17": {"duty": round(q17, 3)},
                "P1": {"duty": round(p1, 3)},
            }
        }
    )


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
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}", "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
