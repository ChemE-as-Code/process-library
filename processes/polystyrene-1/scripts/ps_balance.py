"""Independent heat and material balance of polystyrene-1 (general-purpose polystyrene by
continuous bulk polymerisation of styrene, DESIGN.md D-001).

Run it with `cheme run scripts/ps_balance.py` in the process folder. It

1. solves the plant's mass balance on its own (the same design inputs as process/flowsheet.yaml:
   100 kt/a of polystyrene in 8000 h, 7 wt% ethylbenzene in the reactor feed, the reactors'
   conversions and the separators' recoveries) and prints it beside the flows that
   `cheme process propagate --fill` writes, as a cross-check of the flowsheet's specs and tear;
2. gives the values core's models do not calculate (DESIGN.md D-006, D-008, D-009):
   - S3: the reactor feed's temperature after M101 (fresh styrene at 298.15 K and the
     recycled condensate at 313.15 K, constant liquid heat capacities);
   - Q3: E-101's heat from the hot-oil system: the polymer solution heated from 443.15 to
     513.15 K and the volatiles that flash off in V-101 and V-102 evaporated at 513.15 K
     (V-102's jacket lumped in), D-008;
   - Q4: E-103's heat to cooling water: the devolatilisers' vapours from 513.15 K (ideal gas)
     condensed and cooled to 313.15 K, the enthalpy change taken along the path ideal-gas
     cooling to 313.15 K, then condensation at 313.15 K (a state function), D-008;
   - Q5: the pelletiser's water-loop cooler: the melt cooled from 513.15 to 323.15 K less the
     warming of the make-up water from 298.15 to 323.15 K, plus the shaft work that ends in the
     melt and the water (the melt gear pump, the cutter and the water-loop pump, 90 % of their
     electric power, ASSUMED), D-009.
   The reactor duties Q1 and Q2 are core's (conversion-step model, ADR 0059): printed here
   only as a cross-check, never written to the balance output;
3. prints, not written: R-101's bubble pressure at 403.15 K and the condensing temperatures of
   E-102 (D-005), and the plant's energy balance with its residual and what makes it up (D-008).

Data (DESIGN.md SRC-4): materials.yaml (liquid heat capacities and heats of vaporization at the
normal boiling point, CRC tables as packaged in `chemicals` 1.5.2); the critical temperatures of
`chemicals` 1.5.2 (styrene: method CRC, the CRC Handbook's critical constants; ethylbenzene:
method HEOS, NIST REFPROP's Helmholtz equation of state); ideal-gas heat capacities of `thermo`
0.6.1 (styrene: JOBACK, Joback and Reid 1987; ethylbenzene: HEOS_FIT, thermo's polynomial fit to
REFPROP's Helmholtz equation of state); vapour pressures of `thermo` 0.6.1 (styrene:
WAGNER_MCGARRY, McGarry 1983; ethylbenzene: HEOS_FIT); Watson's correlation (exponent 0.38) for
the heat of vaporization at temperature; the electric powers of process/flowsheet.yaml.

With the environment variable BALANCE_OUTPUT set, it writes the values the flowsheet cites from
it (library ADR 0027, balance-output/1).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from scipy.optimize import fsolve

ROOT = Path(__file__).resolve().parents[1]
MAT = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text(encoding="utf-8"))
COMP = {c["id"]: c for c in MAT["components"]}
MW = {k: c["molar_mass"] for k, c in COMP.items()}
CPL = {k: c["liquid_heat_capacity"] / c["molar_mass"] for k, c in COMP.items()}  # kJ/(kg K)

# Design inputs (process/flowsheet.yaml, DESIGN.md D-002 to D-009), all ASSUMED.
HOURS = 8000.0
PS_T_PER_A = 100_000.0
EB_IN_FEED = 0.07  # mass fraction of ethylbenzene in the reactor feed S3 (D-004)
FRESH = {"STY": 0.9985, "EB": 0.0015}  # styrene-1's product, mass fractions (D-003)
WATER_PER_FRESH = 0.592  # kg process water per kg fresh styrene (D-009)
X_R101, X_R102 = 0.35, 0.615  # styrene converted per pass (D-005)
VAP_V101, VAP_V102 = 0.97, 0.96  # share of each volatile to the vapour (D-007)
VENT = 0.0002  # share of the condensate's volatiles lost with the vacuum vent (D-007)
T_FRESH, T_COND, T_R101, T_R102, T_DEVOL, T_PELLET, T_WATER = (
    298.15, 313.15, 403.15, 443.15, 513.15, 323.15, 298.15)

# Shaft work into the melt and the pelletiser's water (D-009), ASSUMED: 90 % of the electric
# power of the melt gear pump (P4), the cutter and the water-loop pump (P5's 60 and 30 kW); the
# rest of P5 (dryer, conveying, packing), the vacuum system P3 and the drives' losses leave to
# the air and the pumps' own cooling, outside the modelled sinks.
SHAFT_TO_WATER = 0.9
CUTTER_AND_WATER_PUMP = 60.0 + 30.0  # kW, flowsheet P5's source (D-009)

# R-101's bubble pressure (D-005): Raoult's law over the polymer-free volatiles with the solvent
# activity of Flory-Huggins (no open interaction parameter read: chi 0 to 0.5, ASSUMED); the
# polymer's volume fraction from the 298 K densities (styrene 901.6 kg/m3 SRC-4, the polymer
# 1045 kg/m3 SRC-1), ASSUMED to hold at 403 K.
RHO = {"STY": 901.6, "EB": 862.6, "PS": 1045.0}
P_R101 = 65.0  # kPa(a), process/flowsheet.yaml S4 (D-005)

# Critical temperatures (chemicals 1.5.2: CRC for styrene, HEOS for ethylbenzene) and the CRC
# heat of vaporization at its own Tb.
TC = {"STY": 635.0, "EB": 617.12}
TB_HVAP = {"STY": (418.15, 38700.0), "EB": (409.31, 35570.0)}  # K, kJ/kmol (Hvap_data_CRC)
CAS = {"STY": "100-42-5", "EB": "100-41-4"}


def hvap(comp: str, temperature: float) -> float:
    """Heat of vaporization, kJ/kmol, at temperature (Watson from the normal boiling point)."""
    tb, h = TB_HVAP[comp]
    return h * ((1 - temperature / TC[comp]) / (1 - tb / TC[comp])) ** 0.38


def cp_gas_integral(comp: str, t1: float, t2: float) -> float:
    """Ideal-gas enthalpy change from t1 to t2, kJ/kmol (thermo 0.6.1)."""
    from thermo import HeatCapacityGas

    return HeatCapacityGas(CASRN=CAS[comp]).T_dependent_property_integral(t1, t2)  # J/mol


def psat(comp: str, temperature: float) -> float:
    """Vapour pressure, kPa (thermo 0.6.1, its default method)."""
    from thermo import VaporPressure

    return VaporPressure(CASRN=CAS[comp])(temperature) / 1000


def r101_boiling(s4: dict) -> None:
    """Print R-101's bubble pressure at 403.15 K and the condensing temperatures of E-102."""
    import math

    from scipy.optimize import brentq

    vol = {k: s4[k] / MW[k] for k in ("STY", "EB")}
    x = {k: v / sum(vol.values()) for k, v in vol.items()}
    v_ps = s4["PS"] / RHO["PS"]
    phi = v_ps / (v_ps + sum(s4[k] / RHO[k] for k in ("STY", "EB")))
    ideal = sum(x[k] * psat(k, T_R101) for k in x)
    act = {chi: math.exp(math.log(1 - phi) + phi + chi * phi**2) for chi in (0.0, 0.5)}
    print(f"R-101 at {T_R101} K: polymer volume fraction {phi:.3f}; bubble pressure {ideal:.1f} kPa "
          f"ideal, {act[0.0] * ideal:.1f} to {act[0.5] * ideal:.1f} kPa with Flory-Huggins chi 0 to 0.5")
    a = act[0.0]
    t_boil = brentq(lambda t: a * sum(x[k] * psat(k, t) for k in x) - P_R101, 350, 450)
    print(f"  under {P_R101} kPa(a) the solution boils at {t_boil:.1f} K (chi 0; {T_R101} K design)")
    y = {k: a * x[k] * psat(k, T_R101) / (a * ideal) for k in x}
    dew = brentq(lambda t: sum(y[k] * P_R101 / psat(k, t) for k in y) - 1, 330, 450)
    bub = brentq(lambda t: sum(y[k] * psat(k, t) for k in y) - P_R101, 330, 450)
    print(f"  E-102: vapour {100 * y['STY']:.1f} mol% styrene condenses under {P_R101} kPa(a) "
          f"from {dew:.1f} K (dew point) to {bub:.1f} K (its condensate's bubble point)")


def flowsheet_duties() -> dict:
    """The energy streams' duties of process/flowsheet.yaml, kW."""
    sheet = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    return {e["id"]: e["state"]["design"]["duty"]["value"] for e in sheet["streams"]
            if e.get("kind") == "energy"}


def plant(fresh: float, purge: float) -> dict:
    """The steady state for a fresh styrene flow (kg/h) and a purge fraction."""
    rec = {"STY": 0.0, "EB": 0.0}
    for _ in range(2000):
        s1 = {k: fresh * v for k, v in FRESH.items()}
        s3 = {"STY": s1["STY"] + rec["STY"], "EB": s1["EB"] + rec["EB"], "PS": 0.0}
        s4 = dict(s3, STY=s3["STY"] * (1 - X_R101), PS=s3["STY"] * X_R101)
        s5 = dict(s4, STY=s4["STY"] * (1 - X_R102), PS=s4["PS"] + s4["STY"] * X_R102)
        s7 = {k: s5[k] * VAP_V101 for k in ("STY", "EB")}
        s8 = {"STY": s5["STY"] - s7["STY"], "EB": s5["EB"] - s7["EB"], "PS": s5["PS"]}
        s9 = {k: s8[k] * VAP_V102 for k in ("STY", "EB")}
        s11 = {"STY": s8["STY"] - s9["STY"], "EB": s8["EB"] - s9["EB"], "PS": s8["PS"]}
        s16 = {k: s7[k] + s9[k] for k in ("STY", "EB")}
        s18 = {k: s16[k] * VENT for k in s16}
        s19 = {k: s16[k] - s18[k] for k in s16}
        s20 = {k: s19[k] * purge for k in s19}
        new = {k: s19[k] - s20[k] for k in s19}
        if max(abs(new[k] - rec[k]) for k in new) < 1e-9:
            rec = new
            break
        rec = new
    water = fresh * WATER_PER_FRESH
    return {"S1": s1, "S2": rec, "S3": s3, "S4": s4, "S5": s5, "S7": s7, "S8": s8, "S9": s9,
            "S11": s11, "S13": {"H2O": water}, "S16": s16, "S18": s18, "S19": s19, "S20": s20}


def residuals(x):
    fresh, purge = x
    s = plant(fresh, purge)
    feed = sum(s["S3"].values())
    return [s["S11"]["PS"] - PS_T_PER_A * 1000 / HOURS, s["S3"]["EB"] / feed - EB_IN_FEED]


def sensible(stream: dict, t1: float, t2: float) -> float:
    """kW to take a liquid stream (kg/h by component) from t1 to t2."""
    return sum(m * CPL[k] for k, m in stream.items()) * (t2 - t1) / 3600


def main() -> None:
    fresh, purge = fsolve(residuals, [12600.0, 0.015], xtol=1e-12)
    s = plant(fresh, purge)
    total = {k: sum(v.values()) for k, v in s.items()}

    # M101: the reactor feed's temperature (constant liquid heat capacities).
    c1 = sum(m * CPL[k] for k, m in s["S1"].items())
    c2 = sum(m * CPL[k] for k, m in s["S2"].items())
    t3 = (c1 * T_FRESH + c2 * T_COND) / (c1 + c2)

    # Reactors (cross-check of core's conversion duty; heat of reaction at 298.15 K).
    dhr = -73948.0 / MW["STY"]  # kJ/kg converted
    def reactor(sin, sout, tin, tout):
        made = sout["PS"] - sin["PS"]
        return made * dhr / 3600 + sensible(sin, tin, 298.15) + sensible(sout, 298.15, tout)

    q1 = reactor(s["S3"], s["S4"], t3, T_R101)
    q2 = reactor(s["S4"], s["S5"], T_R101, T_R102)

    # E-101 with the devolatilisers: heat-up and the volatiles' evaporation at 513.15 K.
    vap = {k: s["S7"][k] + s["S9"][k] for k in ("STY", "EB")}
    q3 = sensible(s["S5"], T_R102, T_DEVOL) + sum(
        vap[k] / MW[k] * hvap(k, T_DEVOL) for k in vap) / 3600
    # E-103: vapour (ideal gas) cooled 513.15 -> 313.15 K, condensed at 313.15 K.
    q4 = sum(s["S16"][k] / MW[k] * (cp_gas_integral(k, T_COND, T_DEVOL) + hvap(k, T_COND))
             for k in s["S16"]) / 3600
    # Pelletiser: melt 513.15 -> 323.15 K less the make-up water's warming 298.15 -> 323.15 K,
    # plus the gear pump's, the cutter's and the water pump's shaft work (D-009).
    duty = flowsheet_duties()
    shaft = SHAFT_TO_WATER * (duty["P4"] + CUTTER_AND_WATER_PUMP)
    q5 = sensible(s["S11"], T_PELLET, T_DEVOL) - sensible(s["S13"], T_WATER, T_PELLET) + shaft

    print(f"fresh styrene S1 {fresh:.2f} kg/h, purge fraction {purge:.5f}")
    for k in ("S1", "S2", "S3", "S5", "S11", "S13", "S16", "S18", "S20"):
        comp = ", ".join(f"{c} {m:.3f}" for c, m in s[k].items())
        print(f"  {k}: {total[k]:.2f} kg/h ({comp})")
    print(f"fresh feed S1 (styrene-1's product) per kg of pellets {fresh / total['S11']:.4f} kg/kg; "
          f"its styrene per kg of polymer {fresh * FRESH['STY'] / s['S11']['PS']:.4f} kg/kg; "
          f"residual volatiles {1e6 * (s['S11']['STY'] + s['S11']['EB']) / total['S11']:.0f} ppm")
    print(f"T(S3) {t3:.2f} K")
    print(f"Q1 R101 {q1:.1f} kW, Q2 R102 {q2:.1f} kW (H(out) - H(in), before agitator power; "
          "cross-check of core's conversion duty, not written)")
    print(f"Q3 E101 {q3:.1f} kW, Q4 E103 {q4:.1f} kW, Q5 X301 {q5:.1f} kW "
          f"(with {shaft:.1f} kW of shaft work)")
    r101_boiling(s["S4"])
    energy_closure(s, duty, q3, q4, q5, shaft)
    print(f"hvap at 513.15 K: STY {hvap('STY', 513.15):.0f}, EB {hvap('EB', 513.15):.0f}; "
          f"at 313.15 K: STY {hvap('STY', 313.15):.0f}, EB {hvap('EB', 313.15):.0f} kJ/kmol")

    write_balance_output({"design": {
        "S3": {"temperature": round(t3, 2)},
        "Q3": {"duty": round(q3, 1)},
        "Q4": {"duty": round(q4, 1)},
        "Q5": {"duty": round(q5, 1)},
    }})


def energy_closure(s: dict, duty: dict, q3: float, q4: float, q5: float, shaft: float) -> None:
    """Print the plant's energy balance (liquids at 298.15 K the reference) and its residual.

    In: electricity, the hot oil and the heat of polymerisation. Out: the cooling-water duties
    (Q1 and Q2 from the flowsheet, core's; Q4 and Q5 as solved here) and the sensible heat of
    the products above 298.15 K. The residual is what no modelled sink takes: the electric power
    neither core's reactor duties (P1, P2) nor Q5 (the shaft work) count, less the difference
    between E-103's path (ideal gas, Q4) and E-101's (constant liquid heat capacity and Watson at
    513.15 K, Q3) for the same vapour S16.
    """
    power = sum(duty[p] for p in ("P1", "P2", "P3", "P4", "P5"))
    reaction = s["S11"]["PS"] / MW["PS"] * 73948.0 / 3600
    cooling = duty["Q1"] + duty["Q2"] + q4 + q5
    products = (sensible(s["S11"], 298.15, T_PELLET) + sensible(s["S13"], 298.15, T_PELLET)
                + sensible(s["S18"], 298.15, T_COND) + sensible(s["S20"], 298.15, T_COND))
    residual = power + q3 + reaction - cooling - products
    to_air = power - duty["P1"] - duty["P2"] - shaft
    liquid_path = sensible(s["S16"], T_COND, T_DEVOL) + sum(
        s["S16"][k] / MW[k] * hvap(k, T_DEVOL) for k in s["S16"]) / 3600
    path = q4 - liquid_path
    print(f"energy balance: in {power + q3 + reaction:.1f} kW (power {power:.1f}, hot oil {q3:.1f}, "
          f"polymerisation {reaction:.1f}); out {cooling + products:.1f} kW (cooling water "
          f"{cooling:.1f}, products above 298.15 K {products:.1f})")
    print(f"  residual {residual:.1f} kW = power to the air {to_air:.1f} kW less the Q4/Q3 path "
          f"difference {path:.1f} kW (S16 313.15 K liquid to 513.15 K vapour: {liquid_path:.1f} kW "
          f"on E-101's path, {q4:.1f} kW on E-103's); unexplained {residual - to_air + path:.1f} kW")


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
