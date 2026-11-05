"""Independent balance of the N-bromosuccinimide plant (DESIGN.md D-006).

Year-average flows (kg/h, the recipe's basis, D-003) of the caustic bromination of
succinimide: C4H5NO2 + NaOH + Br2 -> C4H4BrNO2 + NaBr + H2O, Br2 dosed into the cold alkaline
succinimide solution, NBS precipitating, a reslurry wash, drying. Every step but the dryer is
also computed by cheme process propagate from process/flowsheet.yaml (the semi-batch, the
precipitation and the wash dissolution as conversion steps, the two filters as specified
splits); this script repeats them so that the dryer's outlets and the duties follow from the
same numbers. Run: `cheme run scripts/balance.py`. With BALANCE_OUTPUT set it writes the values
the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

from pathlib import Path

MW = {  # g/mol, IUPAC 2021 atomic weights applied to the formulas
    "H2O": 18.015,
    "NAOH": 39.997,
    "SUCC": 99.089,
    "BR2": 159.808,
    "NBS": 177.985,
    "NBS_S": 177.985,
    "NABR": 102.894,
}

CAPACITY = 500_000.0 / 7920.0  # kg/h of dried product: 500 t/a in 7920 h (D-002)
EXCESS = 1.02  # succinimide and NaOH per Br2 (D-004)
WATER_PER_BR2 = 30.0  # kmol of water in the charge per kmol Br2 (D-004)
SOLUBILITY = 0.0147  # kg NBS per kg water: 1.47 g/100 g at 25 C (PubChem CID 67184, HSDB; D-005)
RECOVERY = 0.998  # solid to the cake, each filtration (D-007)
CAKE_LIQUID = 0.3  # kg liquid per kg dry solid in the cake (D-007)
WASH = 1.5  # kg ice water per kg solid in the cake, reslurry wash (D-007)
MOISTURE = 0.002  # water mass fraction of the dried product (D-008)
CONVERSION = 0.999  # of the bromine, the post-reaction's target (R101's batch.target, D-005)
# kJ/kmol, all ASSUMED (D-005, D-009): the overall heat of SUCC + NaOH + Br2 -> NBS + NaBr + H2O
# is -80 kJ/mol; of it the imide's deprotonation by NaOH (-30 kJ/mol, a weak acid neutralised by
# a strong base) is released in the dissolver M101, the rest in the brominator R101
HEAT_OF_REACTION = -80_000.0
HEAT_OF_DEPROTONATION = -30_000.0  # per kmol of imide, in M101
HEAT_OF_BROMINATION = HEAT_OF_REACTION - HEAT_OF_DEPROTONATION  # R101 (BROM's heat_of_reaction)
# integral heat of diluting 50 wt% caustic soda to the charge's about 6 wt%, per kmol NaOH: of
# the order published for NaOH's integral heats of solution, ASSUMED (D-009)
HEAT_OF_DILUTION = -20_000.0
CP_SOLUTION = 3.8  # kJ/(kg K) of the alkaline charge (D-009)
CP_BR2 = 75.7 / MW["BR2"]  # kJ/(kg K), liquid bromine
CP_CAKE = 1.6  # kJ/(kg K) of the wet cake, mostly NBS (D-009)
LATENT = 2358.0  # kJ/kg of water at 333 K (steam tables)
DRYER_EFFICIENCY = 0.7  # heat to the product over heat supplied (D-009)
T_FEED, T_REACTOR, T_BR2, T_DRY = 298.15, 278.15, 293.15, 333.15


def kmol(mass: dict[str, float]) -> dict[str, float]:
    return {n: v / MW[n] for n, v in mass.items()}


def add(*flows: dict[str, float]) -> dict[str, float]:
    found: dict[str, float] = {}
    for f in flows:
        for n, v in f.items():
            found[n] = found.get(n, 0.0) + v
    return found


def separate(slurry: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]:
    """A specified filter: RECOVERY of the solid to the cake, CAKE_LIQUID kg of the liquid per
    kg of solid in the cake, the liquid of one composition in cake and filtrate (as core's
    solid_separation)."""
    solid = slurry.get("NBS_S", 0.0)
    liquid = {n: v for n, v in slurry.items() if n != "NBS_S"}
    total = sum(liquid.values())
    held = CAKE_LIQUID * solid * RECOVERY
    share = held / total
    cake = {n: v * share for n, v in liquid.items()} | {"NBS_S": solid * RECOVERY}
    filtrate = {n: v * (1 - share) for n, v in liquid.items()} | {"NBS_S": solid * (1 - RECOVERY)}
    return cake, filtrate


def plant(br2: float) -> dict[str, dict[str, float]]:
    """kg/h of every stream for *br2* kmol/h of bromine dosed."""
    s = {}
    naoh = EXCESS * br2 * MW["NAOH"]
    s["S2"] = {"NAOH": naoh, "H2O": naoh}  # caustic soda 50 wt%
    s["S3"] = {"SUCC": EXCESS * br2 * MW["SUCC"]}
    s["S1"] = {"H2O": WATER_PER_BR2 * br2 * MW["H2O"] - naoh}
    s["S4"] = add(s["S1"], s["S2"], s["S3"])
    s["S5"] = {"BR2": br2 * MW["BR2"]}
    m = kmol(add(s["S4"], s["S5"]))
    xi = CONVERSION * m["BR2"]  # the post-reaction's target conversion of the bromine (D-005)
    m["SUCC"] -= xi
    m["NAOH"] -= xi
    m["BR2"] -= xi
    m["NBS"] = xi
    m["NABR"] = xi
    m["H2O"] += xi
    s["S6"] = {n: v * MW[n] for n, v in m.items() if v > 0}
    # precipitation: the liquor leaves saturated
    dissolved = SOLUBILITY * s["S6"]["H2O"]
    s["S7"] = dict(s["S6"])
    s["S7"]["NBS_S"] = s["S6"]["NBS"] - dissolved
    s["S7"]["NBS"] = dissolved
    s["S8"], s["S9"] = separate(s["S7"])
    s["S10"] = {"H2O": WASH * s["S8"]["NBS_S"]}
    wash = add(s["S8"], s["S10"])
    # the wash water dissolves NBS to saturation (the cake liquid is saturated already)
    dissolve = SOLUBILITY * s["S10"]["H2O"]
    wash["NBS_S"] -= dissolve
    wash["NBS"] += dissolve
    s["S11"] = wash
    s["S12"], s["S13"] = separate(s["S11"])
    cake = s["S12"]
    # the dryer: the water down to MOISTURE, the free bromine (boiling at 332 K) with the vapour
    volatile = ("H2O", "BR2")
    dry = sum(v for n, v in cake.items() if n not in volatile)
    water_left = MOISTURE * dry / (1 - MOISTURE)
    s["S14"] = {n: v for n, v in cake.items() if n not in volatile} | {"H2O": water_left}
    s["S15"] = {"H2O": cake["H2O"] - water_left} | (
        {"BR2": cake["BR2"]} if cake.get("BR2", 0.0) > 0 else {}
    )
    s["S16"] = add(s["S9"], s["S13"], s["S15"])
    return s


def duties(s: dict[str, dict[str, float]], br2: float) -> dict[str, float]:
    """kW, year-average."""
    charge = sum(s["S4"].values())
    imide = EXCESS * br2  # kmol/h of imide deprotonated, and of NaOH diluted
    return {
        # the dissolver, to brine: the caustic's dilution and the imide's deprotonation, and the
        # charge cooled from the feeds' 298 K to 278 K
        "Q1": (
            -(HEAT_OF_DILUTION + HEAT_OF_DEPROTONATION) * imide
            + charge * CP_SOLUTION * (T_FEED - T_REACTOR)
        )
        / 3600.0,
        # the brominator, to brine: the bromination of the converted bromine and the bromine
        # cooled from 293 K
        "Q2": (
            -HEAT_OF_BROMINATION * CONVERSION * br2
            + s["S5"]["BR2"] * CP_BR2 * (T_BR2 - T_REACTOR)
        )
        / 3600.0,
        # the dryer: the cake heated to 333 K and its water evaporated, over the efficiency
        "Q3": (
            sum(s["S12"].values()) * CP_CAKE * (T_DRY - T_REACTOR) + s["S15"]["H2O"] * LATENT
        )
        / DRYER_EFFICIENCY
        / 3600.0,
    }


def solve() -> tuple[float, dict[str, dict[str, float]]]:
    """The bromine that makes CAPACITY of dried product (every flow is linear in it)."""
    unit = sum(plant(1.0)["S14"].values())
    br2 = CAPACITY / unit
    return br2, plant(br2)


def main() -> None:
    br2, s = solve()
    q = duties(s, br2)
    product = s["S14"]
    total = sum(product.values())
    print(f"Br2 dosed {br2:.5f} kmol/h ({s['S5']['BR2']:.3f} kg/h); product {total:.3f} kg/h")
    for sid, flow in s.items():
        tot = sum(flow.values())
        comp = ", ".join(f"{n} {v / tot:.5f}" for n, v in sorted(flow.items()))
        print(f"  {sid}: {tot:.3f} kg/h; {comp}")
    nbs = product.get("NBS_S", 0.0) + product.get("NBS", 0.0)
    print(f"  assay {nbs / total:.4f} NBS; yield on Br2 {nbs / MW['NBS'] / br2:.4f}")
    s6 = kmol(s["S6"])
    print(f"  PPT conversion {1 - (SOLUBILITY * s['S6']['H2O']) / s['S6']['NBS']:.5f}")
    print(f"  S16 {mixed_temperature(s):.2f} K; free bromine in S6 {s6.get('BR2', 0):.6f} kmol/h")
    for k, v in q.items():
        print(f"  {k}: {v:.3f} kW")
    per = {
        "Br2": s["S5"]["BR2"] / total,
        "succinimide": s["S3"]["SUCC"] / total,
        "NaOH 50 wt%": sum(s["S2"].values()) / total,
        "water": (sum(s["S1"].values()) + sum(s["S10"].values())) / total,
    }
    print("  per kg product: " + ", ".join(f"{k} {v:.4f} kg" for k, v in per.items()))
    cases = {"design": {}}
    for sid in ("S1", "S2", "S3", "S5", "S10"):  # the feeds the flowsheet cites
        cases["design"][sid] = {"flow": round(sum(s[sid].values()), 4)}
    for sid in ("S14", "S15"):
        flow = s[sid]
        tot = sum(flow.values())
        cases["design"][sid] = {
            "flow": round(tot, 4),
            "composition": {n: round(v / tot, 6) for n, v in flow.items()},
        }
    for k, v in q.items():
        cases["design"][k] = {"duty": round(v, 4)}
    cases["design"]["S16"] = {"temperature": round(mixed_temperature(s), 2)}
    write_balance_output(cases)


def mixed_temperature(s: dict[str, dict[str, float]]) -> float:
    """K of S16: the mother liquor and wash filtrate (278.15 K) and the dryer condensate
    (303.15 K) mixed adiabatically, equal heat capacities (D-008)."""
    cold = sum(s["S9"].values()) + sum(s["S13"].values())
    warm = sum(s["S15"].values())
    return (cold * T_REACTOR + warm * 303.15) / (cold + warm)


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
