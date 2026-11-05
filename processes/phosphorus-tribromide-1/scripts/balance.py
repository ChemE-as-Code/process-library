"""Independent balance of the phosphorus tribromide plant (DESIGN.md D-006).

Year-average flows (kg/h, the recipe's basis, D-003) of the bromination of white phosphorus in a
PBr3 heel, P4 + 6 Br2 -> 4 PBr3 (DE 1 281 414 / US 3 409 401): molten phosphorus and bromine
dosed together into the heel at 398 K, a 0.4 % bromine excess, the heel kept back in R-101 for
the next batch, the rest of the crude treated with red phosphorus (2 P + 3 Br2 -> 2 PBr3) and
distilled under vacuum. cheme process propagate computes the brominator (semi-batch), the heel
split and the red-phosphorus treatment from process/flowsheet.yaml; this script repeats them,
converges the heel (the recycle the flowsheet gives as an assumed tear stream, S3) and gives the
still's outlets (a specified split: core has no batch distillation yet, core#165) and every
duty. Run: `cheme run scripts/balance.py`. With BALANCE_OUTPUT set it writes the values the
flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import math
from pathlib import Path

MW = {  # g/mol, IUPAC 2021 atomic weights applied to the formulas (P 30.974, Br 79.904)
    "PBR3": 270.686,
    "BR2": 159.808,
    "P4": 123.896,
    "PRED": 30.974,
}

CAPACITY = 1_000_000.0 / 7920.0  # kg/h of distilled PBr3: 1000 t/a in 7920 h (D-002)
# kg of bromine per kg of the stoichiometric need: 0.4 % excess, the patent's example (1554 kg
# of bromine on 200 kg of phosphorus; the stoichiometric need is 1547.8 kg); its claim 1 gives
# 0.05-0.5 % (D-004)
EXCESS = 0.004
HEEL = 3.0  # kg of PBr3 heel per kg of phosphorus per batch: the example's 600 kg on 200 kg (D-004)
RED_P = 0.01  # kg red phosphorus per kg of white phosphorus dosed: the example's 2 kg on 200 kg (D-007)
CONVERSION = 0.9999  # of the white phosphorus, R101's batch.target (D-005)
REDP_CONVERSION = 0.999  # of the free bromine by the red phosphorus in T101 (D-007)
# overall yield of distilled PBr3 on the white phosphorus dosed: the example's 1660 kg of
# 1747.8 kg theoretical (200 kg P x 270.686 / 30.974), 95.0 %; the still's PBr3 recovery is set
# to reproduce it (D-008)
YIELD = 1660.0 / (200.0 * MW["PBR3"] / MW["PRED"])
REFLUX = 0.5  # reflux ratio of the batch still (D-008)
# kJ/kmol: the bromination, from the CRC liquid formation enthalpy of PBr3, -184.5 kJ/mol
# (chemicals package), liquid bromine 0 and molten white phosphorus +0.62 kJ/mol per atom (NIST
# WebBook / JANAF via chemicals): 4 x -184.5 - 4 x 0.62 = -740.48 kJ per mol P4 (D-005)
HF_PBR3_L = -184_500.0
HF_P_L = 620.0
HEAT_OF_REACTION = 4 * HF_PBR3_L - 4 * HF_P_L
# kJ/(kmol K), liquid: bromine 75.7 (NIST WebBook); white phosphorus 26.33 per atom (NIST WebBook
# Shomate fit via thermo); PBr3 132 (thermo's Rowlinson-Poling estimate at 398 K: no measured
# value found; D-006)
CP = {"BR2": 75.7, "P4": 4 * 26.33, "PBR3": 132.0, "PRED": 23.8}
HVAP_PBR3 = 45_600.0  # kJ/kmol at 345 K, thermo's correlation for PBr3 (D-008)
T_REACT = 398.15  # K, 125 C, the middle of the patent's 120-130 C (D-005)
T_BR2, T_P4 = 293.15, 333.15  # K: bromine from storage, molten phosphorus held at 60 C (D-004)
T_STILL = 345.15  # K: PBr3 boiling at 4 kPa(a), thermo's vapour pressure (D-008)
T_PRODUCT = 308.15  # K: distillate subcooled to storage (D-008)
POWER = {"P1": 2.0, "P2": 3.0}  # kW year average: R-101 agitator; still agitator, vacuum pump (D-009)


def kmol(mass: dict[str, float]) -> dict[str, float]:
    return {n: v / MW[n] for n, v in mass.items()}


def mass(moles: dict[str, float]) -> dict[str, float]:
    return {n: v * MW[n] for n, v in moles.items() if v > 1e-15}


def total(flow: dict[str, float]) -> float:
    return sum(flow.values())


def fractions(flow: dict[str, float]) -> dict[str, float]:
    t = total(flow)
    return {n: v / t for n, v in flow.items()}


def plant(p4: float, recovery: float) -> dict[str, dict[str, float]]:
    """kg/h of every stream for *p4* kmol/h of white phosphorus dosed and the still's PBr3
    *recovery* to the distillate."""
    s = {}
    s["S1"] = {"P4": p4 * MW["P4"]}
    s["S2"] = {"BR2": 6 * p4 * (1 + EXCESS) * MW["BR2"]}
    heel = HEEL * 4 * p4 * MW["PRED"]  # kg/h: HEEL kg per kg of phosphorus dosed
    w = {"PBR3": 1.0}
    for _ in range(200):  # the heel is the crude: converge its composition
        s["S3"] = {n: heel * x for n, x in w.items()}
        m = kmol(s["S3"])
        for d in ("S1", "S2"):
            for n, v in kmol(s[d]).items():
                m[n] = m.get(n, 0.0) + v
        xi = CONVERSION * m["P4"]  # the post-reaction's target conversion (R101 batch.target)
        m["P4"] -= xi
        m["BR2"] -= 6 * xi
        m["PBR3"] += 4 * xi
        crude = mass(m)
        new = fractions(crude)
        if max(abs(new.get(n, 0) - w.get(n, 0)) for n in set(new) | set(w)) < 1e-13:
            w = new
            break
        w = new
    s["S4"] = crude
    s["S3"] = {n: heel * x for n, x in w.items()}
    s["S5"] = {n: v - s["S3"][n] for n, v in crude.items()}
    s["S6"] = {"PRED": RED_P * p4 * MW["P4"]}
    m = kmol(s["S5"])
    m["PRED"] = kmol(s["S6"])["PRED"]
    xi2 = REDP_CONVERSION * m["BR2"] / 3
    m["BR2"] -= 3 * xi2
    m["PRED"] -= 2 * xi2
    m["PBR3"] += 2 * xi2
    assert m["PRED"] > 0, "not enough red phosphorus for the free bromine"
    s["S7"] = mass(m)
    s["S8"] = {"PBR3": recovery * s["S7"]["PBR3"], "BR2": s["S7"]["BR2"]}
    s["S9"] = {n: v - s["S8"].get(n, 0.0) for n, v in s["S7"].items()}
    s["S9"] = {n: v for n, v in s["S9"].items() if v > 1e-12}
    s["_xi"] = {"BROM": xi, "REDP": xi2}
    return s


def solve() -> tuple[float, float, dict[str, dict[str, float]]]:
    """The still's recovery that gives YIELD, and the phosphorus that makes CAPACITY (every flow
    is linear in the phosphorus)."""
    lo, hi = 0.5, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        s = plant(1.0, mid)
        y = s["S8"]["PBR3"] / MW["PBR3"] / 4.0
        lo, hi = (mid, hi) if y < YIELD else (lo, mid)
    recovery = (lo + hi) / 2
    p4 = CAPACITY / total(plant(1.0, recovery)["S8"])
    return p4, recovery, plant(p4, recovery)


def duties(s: dict[str, dict[str, float]]) -> dict[str, float]:
    """kW, year averages."""
    xi = s["_xi"]["BROM"]
    dose_warming = (
        kmol(s["S2"])["BR2"] * CP["BR2"] * (T_REACT - T_BR2)
        + kmol(s["S1"])["P4"] * CP["P4"] * (T_REACT - T_P4)
    )
    d = kmol(s["S8"])
    distillate = sum(d.values())
    feed_cp = sum(v * CP[n] for n, v in kmol(s["S7"]).items())
    vapour = (1 + REFLUX) * distillate * HVAP_PBR3
    d_cp = sum(v * CP[n] for n, v in d.items())
    return {
        # R-101, to the tempered-water loop and cooling water: the reaction heat less the
        # doses' warming to 398 K (heel and crude both at 398 K)
        "Q1": (-HEAT_OF_REACTION * xi - dose_warming) / 3600.0,
        # the still's reboiler on LP steam: the boil-up at reflux ratio REFLUX, less the crude's
        # sensible heat from 398 K to the boiling temperature at 4 kPa(a)
        "Q2": (vapour - feed_cp * (T_REACT - T_STILL)) / 3600.0,
        # the still's condenser and product cooler, to cooling water
        "Q3": (vapour + d_cp * (T_STILL - T_PRODUCT)) / 3600.0,
        **POWER,
    }


def rate_constant() -> float:
    """A of BROM's rate law (m3/(kmol s)): k = 1.0 m3/(kmol s) at 398.15 K, Ea 40 kJ/mol (D-005)."""
    return 1.0 * math.exp(40_000.0 / (8.314462618 * T_REACT))


def main() -> None:
    p4, recovery, s = solve()
    q = duties(s)
    product = s["S8"]
    tot = total(product)
    print(f"P4 dosed {p4:.6f} kmol/h ({s['S1']['P4']:.4f} kg/h); product {tot:.4f} kg/h")
    print(f"  still PBr3 recovery {recovery:.6f}; yield on P {YIELD:.5f}")
    for sid, flow in s.items():
        if sid.startswith("_"):
            continue
        t = total(flow)
        comp = ", ".join(f"{n} {v / t:.7f}" for n, v in sorted(flow.items()))
        print(f"  {sid}: {t:.4f} kg/h; {comp}")
    print(f"  extents {s['_xi']}; dHr {HEAT_OF_REACTION:.0f} kJ/kmol; A {rate_constant():.4g}")
    for k, v in q.items():
        print(f"  {k}: {v:.4f} kW")
    per = {
        "P4": s["S1"]["P4"] / tot,
        "Br2": s["S2"]["BR2"] / tot,
        "red P": s["S6"]["PRED"] / tot,
        "residue": total(s["S9"]) / tot,
    }
    print("  per kg product: " + ", ".join(f"{k} {v:.5f} kg" for k, v in per.items()))
    print(f"  assay {product['PBR3'] / tot:.6f} PBr3")
    cases = {"design": {}}
    for sid in ("S1", "S2", "S6"):
        cases["design"][sid] = {"flow": round(total(s[sid]), 4)}
    for sid in ("S3", "S8", "S9"):
        flow = s[sid]
        t = total(flow)
        cases["design"][sid] = {
            "flow": round(t, 4),
            "composition": {n: round(v / t, 8) for n, v in flow.items()},
        }
    for k, v in q.items():
        cases["design"][k] = {"duty": round(v, 4)}
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
