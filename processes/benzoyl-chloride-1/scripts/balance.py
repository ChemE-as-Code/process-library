"""What core cannot calculate in the benzoyl chloride plant (DESIGN.md D-006).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
melter, the semi-batch R101 with its HCl vent, the vapour the HCl carries and R-101's reflux
condenser E-102 (core 1.10.0, ADR 0062), the batch still ST101 with its column K-101 on
Diwekar's shortcut (core 1.10.0, ADR 0061), the absorber (a mixer) and the product cooler (a
pass-through) from process/flowsheet.yaml, and writes the duties of R101 (Q2), of E-102 (Q8)
and of the still's reboiler (Q4) and condenser (Q5) (core ADR 0059). This script gives what
core has no model for, from the streams propagate wrote:

- the feeds that make 2000 t/a of distilled benzoyl chloride (core propagates from the feeds and
  does not solve them for a product rate; the balance is linear in the feeds, so the
  benzotrichloride is scaled by the ratio of the target to the product S11);
- the absorber water S7 for 30 wt% acid;
- the duties Q1 (the melter), Q3 (the absorber) and Q7 (the product cooler): no property
  package of core covers these liquids or HCl in water.

It prints its own values of the model duties Q2, Q4 and Q5 as a cross-check only (Q2 without
the vent's vapour terms, which come from the vent model's integration).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With BALANCE_OUTPUT
set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

MW = {  # g/mol, IUPAC 2021 atomic weights applied to the formulas (materials.yaml)
    "BTC": 195.467,
    "BA": 122.123,
    "BZCL": 140.566,
    "ZNCL2": 136.28,
    "HCL": 36.458,
    "H2O": 18.015,
}

CAPACITY = 2_000_000.0 / 7920.0  # kg/h of distilled benzoyl chloride: 2000 t/a in 7920 h (D-002)
# mol of benzoic acid per mol of benzotrichloride: US 4 276 231 A, Example 1, 15.0 mol on 14.0
# mol (about 7 % excess; the description prefers 3-8 %) (D-004)
ACID_RATIO = 15.0 / 14.0
# kg of ZnCl2 per kg of benzoic acid: Example 1, 13.6 g on 1832 g (D-004)
CATALYST = 13.6 / 1832.0
REFLUX = 2.0  # reflux ratio of the column K-101 on the still (flowsheet ST101, D-008)
HCL_ACID = 0.30  # mass fraction of HCl in the hydrochloric acid (Example 1: about 30 %; D-010)
# kJ/kmol of HCl from gas to the 30 wt% acid at 313 K: the integral heat of solution of HCl in
# about 4.7 mol of water, -64 kJ/mol (ASSUMED, the order of the published integral heats of
# solution), and the gas from the off-gas's temperature (S6, past R-101's reflux condenser) to
# 313 K at its ideal-gas cp, 29.1 kJ/(kmol K) (chemicals 1.5.2, Poling, at about 310-410 K) (D-010)
HEAT_OF_SOLUTION_HCL = 64_000.0
CP_HCL_GAS = 29.1
# kJ/(kmol K): benzoic acid solid, mean from 298 K to its melting point, 175 (ASSUMED: 146.8 at
# 298 K, NIST WebBook, rising towards the melt); liquid 259 at 413 K (NIST WebBook, Pacor 1967);
# ZnCl2 71.3; benzotrichloride 250 (ASSUMED); benzoyl chloride 187.0 (NIST WebBook); water 75.3
CP = {"BA_S": 175.0, "BA": 259.0, "ZNCL2": 71.3, "BTC": 250.0, "BZCL": 187.0, "H2O": 75.3}
FUSION_BA = 18_000.0  # kJ/kmol at 395.5 K (NIST WebBook, Ginnings and Furukawa 1953)
T_MELT = 395.2  # K, benzoic acid (NIST WebBook, mean of 18 values)
# kJ/kmol, the still's heats of vaporization, as materials.yaml (NIST WebBook)
HVAP = {"BZCL": 49_600.0, "BA": 63_300.0, "BTC": 52_000.0}
HEAT_OF_REACTION = -50_000.0  # kJ/kmol, BZCL with HCl as gas (reactions.yaml, ASSUMED, D-005)
T_AMBIENT, T_REACT = 298.15, 413.15  # K (D-004, D-005)
T_PRODUCT = 308.15  # K, to storage: 10 K above the cooling water's 298.15 K supply (D-009); the distillate's temperature is S9's
T_ACID = 313.15  # K, the acid leaving the absorber (D-010)
MELTER_LOSSES = 0.10  # share of the melter's heat lost (D-009)


def state(streams: dict, sid: str) -> dict:
    return streams[sid]["state"]["design"]


def component_flows(streams: dict, sid: str) -> dict[str, float]:
    """kg/h of each component of a stream propagate wrote (flow kg/h, mole fractions)."""
    s = state(streams, sid)
    comp = s["composition"]
    if comp["basis"] != "mole_fraction":
        values = comp["values"]
        return {n: s["flow"]["value"] * x for n, x in values.items()}
    mean = sum(x * MW[n] for n, x in comp["values"].items())
    return {n: s["flow"]["value"] * x * MW[n] / mean for n, x in comp["values"].items()}


def main() -> None:
    sheet = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    streams = {s["id"]: s for s in sheet["streams"]}

    # the product, from the still with its column (propagate: ST101, then E101)
    s11 = component_flows(streams, "S11")
    product = sum(s11.values())

    # the feeds that make CAPACITY: linear in the benzotrichloride
    btc_now = state(streams, "S4")["flow"]["value"]
    btc = btc_now * CAPACITY / product
    ba = btc / MW["BTC"] * ACID_RATIO * MW["BA"]
    zncl2 = ba * CATALYST

    # the absorber water for 30 wt% acid
    s6 = component_flows(streams, "S6")
    hcl = s6.get("HCL", 0.0)
    water = hcl * (1.0 - HCL_ACID) / HCL_ACID

    # duties, kW (kJ/h / 3600), of the streams as propagate wrote them
    s1 = component_flows(streams, "S1")
    s2 = component_flows(streams, "S2")
    s4 = component_flows(streams, "S4")
    n_ba = s1["BA"] / MW["BA"]
    melt = n_ba * (
        CP["BA_S"] * (T_MELT - T_AMBIENT) + FUSION_BA + CP["BA"] * (T_REACT - T_MELT)
    ) + s2["ZNCL2"] / MW["ZNCL2"] * CP["ZNCL2"] * (T_REACT - T_AMBIENT)
    q1 = melt / (1.0 - MELTER_LOSSES) / 3600.0
    t_gas = state(streams, "S6")["temperature"]["value"]
    absorption = HEAT_OF_SOLUTION_HCL + CP_HCL_GAS * (t_gas - T_ACID)
    q3 = (hcl / MW["HCL"] * absorption - water / MW["H2O"] * CP["H2O"] * (T_ACID - T_AMBIENT)) / 3600.0
    t_distillate = state(streams, "S9")["temperature"]["value"]
    q7 = sum(v / MW[n] * CP.get(n, CP["BZCL"]) for n, v in s11.items()) * (t_distillate - T_PRODUCT) / 3600.0

    # cross-checks of the model duties propagate writes (not written)
    extent = hcl / MW["HCL"]  # kmol/h, one HCl per extent of BZCL
    dose_heat = s4["BTC"] / MW["BTC"] * CP["BTC"] * (T_REACT - T_AMBIENT)
    q2_liquid = (-HEAT_OF_REACTION * extent - dose_heat) / 3600.0
    latent = sum(v / MW[n] * HVAP[n] for n, v in s11.items() if n in HVAP) / 3600.0
    q45 = (1.0 + REFLUX) * latent

    yield_btc = (s11["BZCL"] / MW["BZCL"]) / (2.0 * s4["BTC"] / MW["BTC"])
    organics = sum(v for n, v in s6.items() if n != "HCL")
    print(f"product S11 {product:.4f} kg/h at the current feeds; target {CAPACITY:.4f} kg/h")
    print(f"feeds for {CAPACITY * 7.92:.0f} t/a: S4 benzotrichloride {btc:.4f}, S1 benzoic acid {ba:.4f}, S2 ZnCl2 {zncl2:.5f} kg/h")
    print(f"S11 BZCL {s11['BZCL'] / product:.6f} by mass, BTC {s11.get('BTC', 0.0) / product * 1e6:.1f} ppm")
    print(f"S7 absorber water {water:.4f} kg/h for {hcl:.4f} kg/h HCl; organics past E-102 {organics:.4f} kg/h at {t_gas:.2f} K")
    print(f"yield on benzotrichloride {yield_btc:.4%} (2 mol of benzoyl chloride per mol)")
    print(f"Q1 melter {q1:.3f}, Q3 absorber {q3:.3f}, Q7 product cooler {q7:.3f} kW")
    print(f"cross-check of the model duties: Q2 R101 without the vent's vapour terms {q2_liquid:.3f} kW; reboiler Q4 and condenser Q5 (R + 1) D lambda {q45:.3f} kW")

    write_balance_output(
        {
            "design": {
                "S1": {"flow": round(ba, 4)},
                "S2": {"flow": round(zncl2, 5)},
                "S4": {"flow": round(btc, 4)},
                "S7": {"flow": round(water, 4)},
                "Q1": {"duty": round(q1, 4)},
                "Q3": {"duty": round(q3, 4)},
                "Q7": {"duty": round(q7, 4)},
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
        doc = {
            "contract": "balance-output/1",
            "script": f"scripts/{Path(__file__).name}",
            "cases": cases,
        }
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
