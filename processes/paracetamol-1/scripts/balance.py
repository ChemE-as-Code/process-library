"""Independent balance of the paracetamol plant (DESIGN.md D-004, D-006).

Year-average flows (kg/h, the recipe's basis, D-003) of the acetylation of 4-aminophenol in
aqueous acetic acid (US 3 917 695 A, DESIGN.md SRC-1): C6H7NO + C4H6O3 -> C8H9NO2 + C2H4O2,
the anhydride's excess hydrolysed to acetic acid, the product crystallised by cooling,
centrifuged, washed with cold water and dried; half of the mother liquor goes back into the
next charge (SRC-1, Example 4), the rest to wastewater treatment.

Every step is calculated by cheme from process/flowsheet.yaml (`cheme process propagate
--fill`): the semi-batch R101 and the digestion R102 from their rate laws, the crystallizer
CR101 and the wash W101 from the paracetamol's solubility, the centrifuge's specified splits,
the dryer D101, the recycle converged at the tear S16 (core ADR 0060), and the duties of R101,
R102, CR101 and D101. This script keeps only what core still lacks:

- the feeds that make the 2000 t/a of dried product (S1, S2, S4, S11): core propagates from
  the feeds and does not solve them for a product rate. The script repeats the same algebra
  (every flow is linear in the 4-aminophenol), with the recycle iterated to its fixed point,
  and scales it. The reactors' outlet follows from the atom balance alone: R101 ends at 0.998
  conversion of the aminophenol (its batch.target) and R102 at 0.9999 of the anhydride, so
  that what the rate laws decide (the share of the anhydride hydrolysed while it is dosed) is
  hydrolysed by R102's end in any case; the script takes the 1e-4 of it left as zero;
- the duties Q1 (the dissolver heated to 358 K) and Q2 (cooled to 313 K before R-101), from
  the components' liquid heat capacities (process/materials.yaml); no property package of core
  covers this liquor;
- the temperature of S18 (the liquors mixed to wastewater).

It prints the product, its assay, the yield and the losses as a check against propagate, on
the bases DESIGN.md states them (D-004, D-007). Run: `cheme run scripts/balance.py`. With
BALANCE_OUTPUT set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

from pathlib import Path

MW = {  # g/mol, IUPAC 2021 abridged atomic weights applied to the formulas
    "H2O": 18.015,
    "PAP": 109.128,
    "AC2O": 102.089,
    "HOAC": 60.052,
    "APAP": 151.165,
    "APAP_S": 151.165,
}
CP = {  # kJ/(kmol K), process/materials.yaml (liquid_heat_capacity)
    "H2O": 75.3,
    "PAP": 131.5,
    "AC2O": 152.4,
    "HOAC": 132.0,
    "APAP": 176.6,
    "APAP_S": 176.6,
}

CAPACITY = 2_000_000.0 / 7920.0  # kg/h of dried product: 2000 t/a in 7920 h (D-002)
ANHYDRIDE = 1.15  # mol acetic anhydride per mol 4-aminophenol (SRC-1, Example 6; D-004)
AC2O_PURITY = 0.995  # kg/kg of the anhydride feed, the rest acetic acid (acetic-anhydride-1)
# kg of liquid (water and acetic acid, fresh and recycled) per kg of the fresh aminophenol in
# the charge: SRC-1 Example 1, 109 g in 635 cm3 of 10 wt% acetic acid, about 640 g (D-004)
LIQUID_PER_PAP = 5.87
RECYCLE = 0.5  # share of the mother liquor back to the next charge (SRC-1, Example 4; D-008)
# R101's conversion of the aminophenol: its batch.target is 0.998, but the semi-batch model
# reaches it only as the dosing ends and stops there with 3e-7 of it left (cheme process
# reactors; the fast ACET rate law, D-005), so the script takes all of it converted
CONVERSION_PAP = 1.0
# kg paracetamol per kg water at 293.15 K: Jimenez and Martinez (2006), mole fraction 0.00152
# in pure water at 20.0 C (SRC-3), x/(1-x) x 151.165/18.015; no salting-in correction for the
# liquor's acetic acid here: see SALTING (D-007)
SOLUBILITY = 0.012774
# Setschenow coefficient of the acetic acid, kg/mol (negative: salting in): calibrated so that
# CR101's equation reproduces SRC-1 Example 1, 110 g of product from 109 g of 4-aminophenol,
# its 41.0 g of paracetamol taken as dissolved in the mother liquor's 573.9 g of water with
# 4.01 mol/kg of acetic acid (D-007; calibration() prints it). The other spectators: 0.
SALTING_HOAC = -0.1865
EX1 = {"PAP_g": 109.0, "AC2O_g": 114.0, "liquor_g": 640.0, "HOAC_wt": 0.10, "product_g": 110.0}
RECOVERY = 0.995  # solid to the cake, each centrifuge discharge (D-007)
CAKE_LIQUID = 0.15  # kg liquid per kg dry solid in a centrifuged cake (D-007)
WASH = 0.8  # kg cold water per kg solid in the cake (D-007)
MOISTURE = 0.002  # volatiles' mass fraction of the dried product, D101 (D-008)
VOLATILES = ("H2O", "HOAC", "AC2O")  # D101's volatiles, kept in their inlet ratio
T_FEED, T_DISSOLVE, T_DOSE, T_CRYST, T_CONDENSATE = 298.15, 358.15, 313.15, 293.15, 303.15


def add(*flows: dict[str, float]) -> dict[str, float]:
    found: dict[str, float] = {}
    for f in flows:
        for n, v in f.items():
            found[n] = found.get(n, 0.0) + v
    return found


def scale(flow: dict[str, float], factor: float) -> dict[str, float]:
    return {n: v * factor for n, v in flow.items()}


def separate(slurry: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]:
    """A specified centrifuge: RECOVERY of the solid to the cake, CAKE_LIQUID kg of the liquid
    per kg of solid in the cake, the liquid of one composition in cake and filtrate (as core's
    solid_separation)."""
    solid = slurry.get("APAP_S", 0.0)
    liquid = {n: v for n, v in slurry.items() if n != "APAP_S"}
    total = sum(liquid.values())
    held = CAKE_LIQUID * solid * RECOVERY
    share = held / total
    cake = {n: v * share for n, v in liquid.items()} | {"APAP_S": solid * RECOVERY}
    filtrate = {n: v * (1 - share) for n, v in liquid.items()} | {
        "APAP_S": solid * (1 - RECOVERY)
    }
    return cake, filtrate


def saturate(mixture: dict[str, float]) -> dict[str, float]:
    """A crystallizer at equilibrium (CR101, W101): the liquid leaves holding SOLUBILITY kg of
    paracetamol per kg of water, raised by the acetic acid's molality (SALTING_HOAC), the rest
    as crystals; the spectators pass unchanged."""
    out = dict(mixture)
    total = mixture.get("APAP", 0.0) + mixture.get("APAP_S", 0.0)
    molality = 1000.0 * mixture.get("HOAC", 0.0) / MW["HOAC"] / mixture["H2O"]
    out["APAP"] = SOLUBILITY * 10 ** (-SALTING_HOAC * molality) * mixture["H2O"]
    out["APAP_S"] = total - out["APAP"]
    return out


def react(charge: dict[str, float]) -> dict[str, float]:
    """R101 and R102 together by the atom balance: the aminophenol to CONVERSION_PAP, the rest
    of the anhydride hydrolysed (kg/h in, kg/h out)."""
    m = {n: v / MW[n] for n, v in charge.items()}
    acet = CONVERSION_PAP * m.get("PAP", 0.0)
    hyd = m.get("AC2O", 0.0) - acet
    m["PAP"] -= acet
    m["APAP"] = m.get("APAP", 0.0) + acet
    m["HOAC"] = m.get("HOAC", 0.0) + acet + 2 * hyd
    m["H2O"] -= hyd
    m["AC2O"] = 0.0
    return {n: v * MW[n] for n, v in m.items() if v > 0}


def plant(pap: float) -> dict[str, dict[str, float]]:
    """kg/h of every stream for *pap* kmol/h of fresh 4-aminophenol."""
    s: dict[str, dict[str, float]] = {}
    s["S2"] = {"PAP": pap * MW["PAP"]}
    ac2o = ANHYDRIDE * pap * MW["AC2O"]
    s["S4"] = {"AC2O": ac2o, "HOAC": ac2o * (1 - AC2O_PURITY) / AC2O_PURITY}
    liquid = LIQUID_PER_PAP * s["S2"]["PAP"]
    s["S16"] = {}
    for _ in range(200):  # the recycle's fixed point (Wegstein in core; here direct)
        recycled = sum(v for n, v in s["S16"].items() if n not in ("PAP", "APAP", "APAP_S"))
        s["S1"] = {"H2O": liquid - recycled}
        s["S3"] = add(s["S1"], s["S2"], s["S16"])
        s["S6"] = react(add(s["S3"], s["S4"]))
        s["S7"] = saturate(s["S6"])  # CR101
        s["S8"], s["S9"] = separate(s["S7"])  # F101
        new = scale(s["S9"], RECYCLE)  # SP101
        if all(abs(new.get(n, 0) - s["S16"].get(n, 0)) < 1e-10 for n in new):
            s["S16"] = new
            break
        s["S16"] = new
    s["S10"] = scale(s["S9"], 1 - RECYCLE)
    s["S11"] = {"H2O": WASH * s["S8"]["APAP_S"]}
    s["S12"] = saturate(add(s["S8"], s["S11"]))  # W101
    s["S13"], s["S14"] = separate(s["S12"])  # F102
    cake = s["S13"]
    # D101: the volatiles down to MOISTURE of the product, kept in their inlet ratio
    dry = sum(v for n, v in cake.items() if n not in VOLATILES)
    wet = sum(cake.get(n, 0.0) for n in VOLATILES)
    kept = MOISTURE / (1 - MOISTURE) * dry / wet
    s["S15"] = {n: v * (kept if n in VOLATILES else 1.0) for n, v in cake.items()}
    s["S17"] = {n: cake[n] * (1 - kept) for n in VOLATILES if cake.get(n, 0.0) > 0}
    s["S18"] = add(s["S10"], s["S14"], s["S17"])
    return s


def heat_flow(flow: dict[str, float]) -> float:
    """kJ/(K h) of a stream from the components' liquid heat capacities."""
    return sum(v / MW[n] * CP[n] for n, v in flow.items())


def mixed_temperature(parts: list[tuple[dict[str, float], float]]) -> float:
    total = sum(heat_flow(f) for f, _ in parts)
    return sum(heat_flow(f) * t for f, t in parts) / total


def duties(s: dict[str, dict[str, float]]) -> dict[str, float]:
    """kW, year-average: the dissolver M-101 heated from the charge's mixed temperature to
    358.15 K (Q1, LP steam) and cooled to 313.15 K before R-101 (Q2, cooling water). The
    aminophenol's heat of solution and M-101's metal are left out (D-009)."""
    t_mix = mixed_temperature([(s["S1"], T_FEED), (s["S2"], T_FEED), (s["S16"], T_CRYST)])
    c = heat_flow(s["S3"])
    return {
        "Q1": c * (T_DISSOLVE - t_mix) / 3600.0,
        "Q2": c * (T_DISSOLVE - T_DOSE) / 3600.0,
        "T_mix": t_mix,
    }


def solve() -> tuple[float, dict[str, dict[str, float]]]:
    """The 4-aminophenol that makes CAPACITY of dried product (every flow is linear in it)."""
    unit = sum(plant(1.0)["S15"].values())
    pap = CAPACITY / unit
    return pap, plant(pap)


def calibration() -> float:
    """SALTING_HOAC from SRC-1 Example 1 (D-007): 109 g of 4-aminophenol in 640 g of 10 wt%
    acetic acid (its 635 cm3, ASSUMED 1.01 g/cm3), 114 g of acetic anhydride, 110 g of product;
    the paracetamol not isolated taken as dissolved at 293.15 K."""
    import math

    pap = EX1["PAP_g"] / MW["PAP"]
    ac2o = EX1["AC2O_g"] / MW["AC2O"]
    water = EX1["liquor_g"] * (1 - EX1["HOAC_wt"]) - (ac2o - pap) * MW["H2O"]
    hoac = EX1["liquor_g"] * EX1["HOAC_wt"] + (pap + 2 * (ac2o - pap)) * MW["HOAC"]
    dissolved = pap * MW["APAP"] - EX1["product_g"]
    molality = 1000.0 * hoac / MW["HOAC"] / water
    return -math.log10(dissolved / water / SOLUBILITY) / molality


def main() -> None:
    print(f"calibrated Setschenow coefficient of HOAc {calibration():.4f} kg/mol (used {SALTING_HOAC})")
    pap, s = solve()
    q = duties(s)
    product = s["S15"]
    total = sum(product.values())
    print(f"4-aminophenol {pap:.5f} kmol/h ({s['S2']['PAP']:.3f} kg/h); product {total:.3f} kg/h")
    for sid, flow in s.items():
        tot = sum(flow.values())
        comp = ", ".join(f"{n} {v / tot:.6f}" for n, v in sorted(flow.items()))
        print(f"  {sid}: {tot:.4f} kg/h; {comp}")
    apap = product.get("APAP_S", 0.0) + product.get("APAP", 0.0)
    print(f"  assay {apap / total:.5f} paracetamol; yield on 4-aminophenol {apap / MW['APAP'] / pap:.4f}")
    ref = pap * MW["APAP"]
    print(
        "  paracetamol lost per theoretical: purge "
        f"{(s['S10'].get('APAP', 0) + s['S10'].get('APAP_S', 0)) / ref:.4f}, wash filtrate "
        f"{(s['S14'].get('APAP', 0) + s['S14'].get('APAP_S', 0)) / ref:.4f}"
    )
    print(f"  charge S3 mixed at {q['T_mix']:.2f} K; Q1 {q['Q1']:.3f} kW, Q2 {q['Q2']:.3f} kW")
    t18 = mixed_temperature([(s["S10"], T_CRYST), (s["S14"], T_CRYST), (s["S17"], T_CONDENSATE)])
    print(f"  S18 {t18:.2f} K")
    per = {
        "4-aminophenol": s["S2"]["PAP"] / total,
        "acetic anhydride feed": sum(s["S4"].values()) / total,
        "water": (s["S1"]["H2O"] + s["S11"]["H2O"]) / total,
        "wastewater": sum(s["S18"].values()) / total,
    }
    print("  per kg product: " + ", ".join(f"{k} {v:.4f} kg" for k, v in per.items()))
    cases: dict[str, dict] = {"design": {}}
    for sid in ("S1", "S2", "S4", "S11"):  # the feeds the flowsheet cites
        cases["design"][sid] = {"flow": round(sum(s[sid].values()), 4)}
    for k in ("Q1", "Q2"):
        cases["design"][k] = {"duty": round(q[k], 4)}
    cases["design"]["S18"] = {"temperature": round(t18, 2)}
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
