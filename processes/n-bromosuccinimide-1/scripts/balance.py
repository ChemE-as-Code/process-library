"""Independent balance of the N-bromosuccinimide plant (DESIGN.md D-006, D-014).

Year-average flows (kg/h, the recipe's basis, D-003) of the caustic bromination of
succinimide: C4H5NO2 + NaOH + Br2 -> C4H4BrNO2 + NaBr + H2O, Br2 dosed into the cold alkaline
succinimide solution, NBS precipitating, a reslurry wash, drying.

Since core 1.8.0 every step is calculated by cheme from
process/flowsheet.yaml (`cheme process propagate --fill`): the semi-batch R101, the precipitation CR101 and the reslurry wash W101 as
crystallizers with spectators (core ADR 0056), the filters F101 and F102 as specified splits,
the dryer D101 to its residual moisture, and its heat Q3 (core ADR 0057, `cheme process
crystallizers`). This script keeps only what core still lacks:

- the feeds that make the 500 t/a of dried product (S1, S2, S3, S5, S10): core propagates from
  the feeds and does not solve them for a product rate, so the script repeats the same algebra
  (every flow is linear in the bromine) and scales it;
- the duties Q1 (dissolver) and Q2 (brominator) from the ASSUMED heats of dilution,
  deprotonation and bromination: no property package of core covers this liquor;
- the temperature of S16 (the liquors mixed after the vacuum condenser).

It prints the product, the yield, the NBS lost and the other streams as a check against
propagate, on the bases DESIGN.md states them (D-005, D-007). Run:
`cheme run scripts/balance.py`. With BALANCE_OUTPUT set it writes the values the flowsheet
cites (library ADR 0027).

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
# kg NBS per kg water: 1.47 g/100 g at 25 C (PubChem CID 67184, HSDB; D-005), taken at 278 K
# and in the mother liquor without a salting-out correction, as CR101 and W101 declare (D-014)
SOLUBILITY = 0.0147
RECOVERY = 0.998  # solid to the cake, each filtration (D-007)
CAKE_LIQUID = 0.3  # kg liquid per kg dry solid in the cake (D-007)
WASH = 1.5  # kg ice water per kg solid in the cake, reslurry wash (D-007)
MOISTURE = 0.002  # volatiles' mass fraction of the dried product, D101 (D-008)
VOLATILES = ("H2O", "BR2")  # D101's volatiles, kept in their inlet ratio (core ADR 0057)
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
T_FEED, T_REACTOR, T_BR2, T_CONDENSATE = 298.15, 278.15, 293.15, 303.15


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


def saturate(mixture: dict[str, float]) -> dict[str, float]:
    """A crystallizer at equilibrium (CR101, W101): the liquid leaves holding SOLUBILITY kg of
    NBS per kg of water, the rest of the NBS as crystals; the spectators pass unchanged."""
    out = dict(mixture)
    total = mixture.get("NBS", 0.0) + mixture.get("NBS_S", 0.0)
    out["NBS"] = SOLUBILITY * mixture["H2O"]
    out["NBS_S"] = total - out["NBS"]
    return out


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
    s["S7"] = saturate(s["S6"])  # CR101
    s["S8"], s["S9"] = separate(s["S7"])  # F101
    s["S10"] = {"H2O": WASH * s["S8"]["NBS_S"]}
    s["S11"] = saturate(add(s["S8"], s["S10"]))  # W101
    s["S12"], s["S13"] = separate(s["S11"])  # F102
    cake = s["S12"]
    # D101: the volatiles down to MOISTURE of the product, kept in their inlet ratio
    dry = sum(v for n, v in cake.items() if n not in VOLATILES)
    wet = sum(cake.get(n, 0.0) for n in VOLATILES)
    kept = MOISTURE / (1 - MOISTURE) * dry / wet
    s["S14"] = {n: v * (kept if n in VOLATILES else 1.0) for n, v in cake.items()}
    s["S15"] = {n: cake[n] * (1 - kept) for n in VOLATILES if cake.get(n, 0.0) > 0}
    s["S16"] = add(s["S9"], s["S13"], s["S15"])
    return s


def duties(s: dict[str, dict[str, float]], br2: float) -> dict[str, float]:
    """kW, year-average (Q3, the dryer's, is core's: `cheme process crystallizers`)."""
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
    }


def solve() -> tuple[float, dict[str, dict[str, float]]]:
    """The bromine that makes CAPACITY of dried product (every flow is linear in it)."""
    unit = sum(plant(1.0)["S14"].values())
    br2 = CAPACITY / unit
    return br2, plant(br2)


def losses(s: dict[str, dict[str, float]], br2: float) -> dict[str, float]:
    """The NBS lost, as fractions of the NBS equivalent of the bromine dosed (the basis of the
    yield, D-007): dissolved in the mother liquor S9 and in the wash filtrate S13, and passed
    through both filters as solid."""
    ref = br2 * MW["NBS"]
    return {
        "mother liquor": s["S9"].get("NBS", 0.0) / ref,
        "wash filtrate": s["S13"].get("NBS", 0.0) / ref,
        "solid through the filters": (s["S9"].get("NBS_S", 0.0) + s["S13"].get("NBS_S", 0.0))
        / ref,
    }


def bromine_fate(s: dict[str, dict[str, float]]) -> dict[str, float]:
    """Where the free bromine left in S6 goes, as fractions of it (D-005): a spectator of the
    crystallizers, it divides with the liquid at the filters; D101's vapour takes the cake's but
    for the share its residual moisture keeps."""
    left = s["S6"].get("BR2", 0.0)
    return {sid: s[sid].get("BR2", 0.0) / left for sid in ("S9", "S13", "S15", "S14")}


def mixed_temperature(s: dict[str, dict[str, float]]) -> float:
    """K of S16: the mother liquor and wash filtrate (278.15 K) and the dryer's condensate
    after the vacuum condenser (303.15 K) mixed adiabatically, equal heat capacities (D-008)."""
    cold = sum(s["S9"].values()) + sum(s["S13"].values())
    warm = sum(s["S15"].values())
    return (cold * T_REACTOR + warm * T_CONDENSATE) / (cold + warm)


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
    lost = losses(s, br2)
    print(
        "  NBS lost per NBS of the Br2 dosed: "
        + ", ".join(f"{k} {v:.4f}" for k, v in lost.items())
    )
    fate = bromine_fate(s)
    print("  free Br2 of S6 to: " + ", ".join(f"{k} {v:.4f}" for k, v in fate.items()))
    print(f"  S16 {mixed_temperature(s):.2f} K")
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
    for k, v in q.items():
        cases["design"][k] = {"duty": round(v, 4)}
    cases["design"]["S16"] = {"temperature": round(mixed_temperature(s), 2)}
    write_balance_output(cases)


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
