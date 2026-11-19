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
  the components' liquid heat capacities (process/materials.yaml) with M-101's metal; no
  property package of core covers this liquor; and M-101's heat-up and cool-down times on an
  ASSUMED jacket (m101_times(), the recipe's durations);
- the heats core's models leave out (D-009): Q7, R-101's metal and the crystals' redissolution
  in the digestion's heat-up, and Q8, the dryer's condenser E-101 and D-101's cool-down;
- the temperature of S18 (the liquors mixed to wastewater);
- the Setschenow coefficient of the acetic acid, calibrated to SRC-1 Example 1 at the
  example's temperature, with the van 't Hoff enthalpy of SRC-3's points (D-007).

It prints the product, its assay, the yield and the losses as a check against propagate, on
the bases DESIGN.md states them (D-004, D-007), and the yield of the same plant crystallising at
SRC-1's temperature (the like-for-like check against Example 4). Run: `cheme run
scripts/balance.py`. With
BALANCE_OUTPUT set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import math
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
# kg paracetamol per kg water, pure water: Jimenez and Martinez (2006), the mole fractions in
# pure water at 20.0 to 40.0 C (SRC-3), x/(1-x) x 151.165/18.015, the values the crystallizers
# CR101 and W101 cite; no salting-in correction here: see SALTING_HOAC (D-007)
POINTS = {293.15: 0.012774, 298.15: 0.015552, 303.15: 0.017574, 308.15: 0.021536, 313.15: 0.026515}
SOLUBILITY = POINTS[293.15]  # at CR101's and W101's 293.15 K
R = 8.314462618e-3  # kJ/(mol K)
# SRC-1 Example 1 isolates the product after cooling to 10 to 15 C: its mid-point, ASSUMED
# (D-007). Below SRC-3's 20 C the pure water's solubility is extrapolated by van 't Hoff (vant_hoff())
T_EX1 = 285.65
# Setschenow coefficient of the acetic acid, kg/mol (negative: salting in): calibrated so that
# CR101's equation reproduces SRC-1 Example 1, 110 g of product from 109 g of 4-aminophenol,
# its 41.0 g of paracetamol taken as dissolved in the mother liquor's 573.9 g of water with
# 4.01 mol/kg of acetic acid at T_EX1 (D-007; calibration() prints it). The other spectators: 0.
SALTING_HOAC = -0.2182
EX1 = {"PAP_g": 109.0, "AC2O_g": 114.0, "liquor_g": 640.0, "HOAC_wt": 0.10, "product_g": 110.0}
RECOVERY = 0.995  # solid to the cake, each centrifuge discharge (D-007)
CAKE_LIQUID = 0.15  # kg liquid per kg dry solid in a centrifuged cake (D-007)
WASH = 0.8  # kg cold water per kg solid in the cake (D-007)
MOISTURE = 0.002  # volatiles' mass fraction of the dried product, D101 (D-008)
VOLATILES = ("H2O", "HOAC", "AC2O")  # D101's volatiles, kept in their inlet ratio
T_FEED, T_DISSOLVE, T_DOSE, T_CRYST, T_CONDENSATE = 298.15, 358.15, 313.15, 293.15, 303.15
T_DRY = 343.15  # D101 (D-008)
# The recipe's batch (process/recipe.yaml batch_size, D-003): the per-batch heats below are
# spread over the year by CAPACITY / BATCH_KG batches an hour
BATCH_KG = 2602.10
# Metal of the vessels heated and cooled with each batch, kJ/K, ASSUMED (D-009): R-101 as the
# recipe's metal_heat_capacity (about 14 t of glass-lined steel at 0.5 kJ/(kg K)); M-101 the
# same vessel in stainless steel (D-003); D-101 as D101's vessel_heat_capacity (about 4 t)
METAL = {"M-101": 7000.0, "R-101": 7000.0, "D-101": 2000.0}
# M-101's jacket for its heating and cooling times (D-003), ASSUMED: R-101's vessel and U, so
# the charge wets the 29.9 m2 the recipe reports for R-101 at the same charge S3; LP steam in
# the jacket at its 412 K (no anhydride in M-101: D-011); cooling water entered as its
# log-mean equivalent at the end, 298.15/308.15 K against 313.15 K: (15 - 5)/ln 3 = 9.10 K
M101_JACKET = {"u": 0.300, "area": 29.9, "steam": 412.0, "cw": 313.15 - (15.0 - 5.0) / math.log(15.0 / 5.0)}
# D101's latent heats at 343.15 K (kJ/kg, the flowsheet's dryer energy, thermo 0.6.1) and the
# paracetamol crystals' heat capacity (process/materials.yaml), for E-101 and D-101's cool-down
LATENT = {"H2O": 2333.0, "HOAC": 393.3, "AC2O": 446.0}


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


def vant_hoff() -> float:
    """kJ/mol: the apparent enthalpy of solution, the least-squares slope of ln x over 1/T
    through SRC-3's five points (x the mole fraction back from kg/kg)."""
    xs = [(1 / t, math.log(w / MW["APAP"] / (w / MW["APAP"] + 1 / MW["H2O"]))) for t, w in POINTS.items()]
    n = len(xs)
    mx, my = sum(a for a, _ in xs) / n, sum(b for _, b in xs) / n
    slope = sum((a - mx) * (b - my) for a, b in xs) / sum((a - mx) ** 2 for a, _ in xs)
    return -slope * R


def solubility_at(t: float) -> float:
    """kg/kg of pure water: SRC-3's value at a data point; below 293.15 K extrapolated from the
    293.15 K point with vant_hoff()'s enthalpy (ASSUMED, D-007)."""
    if t in POINTS:
        return POINTS[t]
    x0 = SOLUBILITY / MW["APAP"] / (SOLUBILITY / MW["APAP"] + 1 / MW["H2O"])
    x = x0 * math.exp(-vant_hoff() / R * (1 / t - 1 / 293.15))
    return x / (1 - x) * MW["APAP"] / MW["H2O"]


def saturate(mixture: dict[str, float], solubility: float = SOLUBILITY) -> dict[str, float]:
    """A crystallizer at equilibrium (CR101, W101): the liquid leaves holding *solubility* kg of
    paracetamol per kg of water, raised by the acetic acid's molality (SALTING_HOAC), the rest
    as crystals; the spectators pass unchanged."""
    out = dict(mixture)
    total = mixture.get("APAP", 0.0) + mixture.get("APAP_S", 0.0)
    molality = 1000.0 * mixture.get("HOAC", 0.0) / MW["HOAC"] / mixture["H2O"]
    out["APAP"] = solubility * 10 ** (-SALTING_HOAC * molality) * mixture["H2O"]
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


def plant(pap: float, t_cryst: float = T_CRYST) -> dict[str, dict[str, float]]:
    """kg/h of every stream for *pap* kmol/h of fresh 4-aminophenol, crystallised at *t_cryst*."""
    sol = solubility_at(t_cryst)
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
        s["S7"] = saturate(s["S6"], sol)  # CR101
        s["S8"], s["S9"] = separate(s["S7"])  # F101
        new = scale(s["S9"], RECYCLE)  # SP101
        if all(abs(new.get(n, 0) - s["S16"].get(n, 0)) < 1e-10 for n in new):
            s["S16"] = new
            break
        s["S16"] = new
    s["S10"] = scale(s["S9"], 1 - RECYCLE)
    s["S11"] = {"H2O": WASH * s["S8"]["APAP_S"]}
    s["S12"] = saturate(add(s["S8"], s["S11"]), sol)  # W101
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
    """kW, year averages (D-009), the heats the models of core do not give:

    - Q1, Q2: the dissolver M-101's charge S3 heated from its mixed temperature to 358.15 K (LP
      steam) and cooled to 313.15 K before R-101 (cooling water), with M-101's metal, which
      swings between 313.15 and 358.15 K; the aminophenol's heat of solution left out (L-1);
    - Q7 (LP steam): R-101's metal heated from 313.15 to 358.15 K with the digestion (core's
      batch model counts the content only, L-5), and the crystals present at 313.15 K
      redissolved in it: R101's heat of reaction takes the product as formed solid (D-005), the
      digested mass S6 carries it dissolved, so the paracetamol solid at 313.15 K in S6's liquor
      (SRC-3's 313.15 K point with the salting in) takes up vant_hoff()'s enthalpy;
    - Q8 (cooling water): the dryer's vapour S17 condensed and cooled in E-101 from D101's
      343.15 K to 303.15 K, and the product with D-101's metal cooled from 343.15 to 303.15 K
      before the discharge (S15)."""
    t_mix = mixed_temperature([(s["S1"], T_FEED), (s["S2"], T_FEED), (s["S16"], T_CRYST)])
    c = heat_flow(s["S3"])
    per_h = CAPACITY / BATCH_KG  # batches an hour, year average
    swing = T_DISSOLVE - T_DOSE
    solid = saturate(s["S6"], POINTS[313.15])["APAP_S"] / MW["APAP"]  # kmol/h
    formed = s["S2"]["PAP"] / MW["PAP"] * CONVERSION_PAP
    vapour = sum(v * (LATENT[n] + CP[n] / MW[n] * (T_DRY - T_CONDENSATE)) for n, v in s["S17"].items())
    cooled = (heat_flow(s["S15"]) + METAL["D-101"] * per_h) * (T_DRY - T_CONDENSATE)
    return {
        "Q1": (c * (T_DISSOLVE - t_mix) + METAL["M-101"] * swing * per_h) / 3600.0,
        "Q2": (c + METAL["M-101"] * per_h) * swing / 3600.0,
        "Q7": (METAL["R-101"] * swing * per_h + solid * 1000.0 * vant_hoff()) / 3600.0,
        "Q8": (vapour + cooled) / 3600.0,
        "T_mix": t_mix,
        "R101_metal": METAL["R-101"] * swing * per_h / 3600.0,
        "redissolved": solid,
        "Q3_over": (formed - solid) * 1000.0 * vant_hoff() / 3600.0,
        # CR101's crystals: the chilled water's heat of crystallisation is Q3's formed product
        # less the redissolved plus these, so the difference is Q3_over less this
        "CR101": (saturate(s["S6"])["APAP_S"] - s["S6"].get("APAP_S", 0.0)) / MW["APAP"] * 1000.0 * vant_hoff() / 3600.0,
        "E101": vapour / 3600.0,
    }


def m101_times(s: dict[str, dict[str, float]]) -> tuple[float, float]:
    """Hours of M-101's heat-up (LP steam in its jacket) and cool-down (cooling water): the
    charge and the metal as one lumped mass, U A constant, the utility at M101_JACKET's
    constant temperature (as core's recipe takes R-101's jacket), D-003."""
    per_h = CAPACITY / BATCH_KG
    mass = heat_flow(s["S3"]) / per_h + METAL["M-101"]  # kJ/K per batch
    tau = mass / (M101_JACKET["u"] * M101_JACKET["area"]) / 3600.0  # h
    t_mix = mixed_temperature([(s["S1"], T_FEED), (s["S2"], T_FEED), (s["S16"], T_CRYST)])
    hot, cw = M101_JACKET["steam"], M101_JACKET["cw"]
    heat = tau * math.log((hot - t_mix) / (hot - T_DISSOLVE))
    cool = tau * math.log((T_DISSOLVE - cw) / (T_DOSE - cw))
    return heat, cool


def solve() -> tuple[float, dict[str, dict[str, float]]]:
    """The 4-aminophenol that makes CAPACITY of dried product (every flow is linear in it)."""
    unit = sum(plant(1.0)["S15"].values())
    pap = CAPACITY / unit
    return pap, plant(pap)


def calibration() -> float:
    """SALTING_HOAC from SRC-1 Example 1 (D-007): 109 g of 4-aminophenol in 640 g of 10 wt%
    acetic acid (its 635 cm3, ASSUMED 1.01 g/cm3), 114 g of acetic anhydride, 110 g of product;
    the paracetamol not isolated taken as dissolved at T_EX1, where SRC-1 isolates it."""
    pap = EX1["PAP_g"] / MW["PAP"]
    ac2o = EX1["AC2O_g"] / MW["AC2O"]
    water = EX1["liquor_g"] * (1 - EX1["HOAC_wt"]) - (ac2o - pap) * MW["H2O"]
    hoac = EX1["liquor_g"] * EX1["HOAC_wt"] + (pap + 2 * (ac2o - pap)) * MW["HOAC"]
    dissolved = pap * MW["APAP"] - EX1["product_g"]
    molality = 1000.0 * hoac / MW["HOAC"] / water
    return -math.log10(dissolved / water / solubility_at(T_EX1)) / molality


def main() -> None:
    print(f"van 't Hoff enthalpy of solution from SRC-3's five points {vant_hoff():.2f} kJ/mol")
    print(f"pure water's solubility at {T_EX1} K {solubility_at(T_EX1):.6f} kg/kg (extrapolated)")
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
    cold = plant(pap, T_EX1)["S15"]
    print(f"  the same plant crystallising at {T_EX1} K (SRC-1's): yield {(cold['APAP_S'] + cold['APAP']) / MW['APAP'] / pap:.4f}")
    print(f"  charge S3 mixed at {q['T_mix']:.2f} K; Q1 {q['Q1']:.3f} kW, Q2 {q['Q2']:.3f} kW")
    print(
        f"  Q7 {q['Q7']:.3f} kW (R-101's metal {q['R101_metal']:.3f} kW, {q['redissolved']:.4f} kmol/h "
        f"redissolved); Q3 counts {q['Q3_over']:.2f} kW of crystallisation the 313 K liquor does not make,"
        f" CR101 makes {q['CR101']:.2f} kW (counted 0): the chilled water's net {q['CR101'] - q['Q3_over']:.2f} kW"
    )
    print(f"  Q8 {q['Q8']:.3f} kW (E-101 {q['E101']:.3f} kW)")
    heat, cool = m101_times(s)
    print(f"  M-101 heat-up {heat:.2f} h, cool-down {cool:.2f} h")
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
    for k in ("Q1", "Q2", "Q7", "Q8"):
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
