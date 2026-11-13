"""What core cannot calculate in the methanesulfonyl chloride plant (DESIGN.md D-006).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the dose
tank M101, the semi-batch R101 with its SO2/HCl vent, the vapour the gases carry and R-101's vent
condenser E-102 (core ADRs 0050, 0054, 0062, 0063), the batch stills ST101 (the forerun) and
ST102 (the product) with the column K-101 (core ADRs 0055, 0061), the forerun's recycle at its
tear S3 (ADR 0060), the caustic dilution M102 and the scrubber A101 (a conversion step), and
writes the duties of R101 (Q1), of E-102 (Q2) and of the stills' reboilers (Q3, Q5) and
condensers (Q4, Q6) (core ADR 0059). This script gives what core has no model for, from the
streams propagate wrote:

- the feeds that make 1000 t/a of distilled methanesulfonyl chloride: the acid S1 scaled by the
  ratio of the target to the product S10 (the balance is linear in the feeds), and the fresh
  thionyl chloride S2 that, with the recovered forerun S3, doses 4/3 mol per mol of acid (the
  ratio of Organic Syntheses, D-004): the loop returns nine tenths of what the forerun takes, so
  S3 = 9 (S2 - L), where L is the thionyl chloride the reaction, the water, the vent and the
  stripped crude take; converged in a few passes of propagate and this script;
- the scrubber's caustic S14 (10 % above what the off-gas S6 neutralises) and its dilution water
  S15 to 15 wt% NaOH (D-010);
- the temperatures of the distillate S9 and the residue S11: the bubble points of their
  compositions at the still's 4 kPa(a) (Raoult, the vapour-pressure lines of materials.yaml);
- the duties Q7 (the product cooler) and Q9 (the caustic's heat of dilution less what warms the
  diluted caustic to 308 K, 10 K above the cooling water's supply): no property package of core
  covers these liquids.

It prints cross-checks of what propagate wrote: the dose ratio, the yield, the scrubber's duty
Q8 (the neutralisations of reactions.yaml, the gas and the liquor brought to 308 K), which
core's conversion step A101 writes itself (ADR 0059), and the crude's adiabatic flash as C-101
is evacuated (D-007, L-4): the crude arrives at 368.15 K, far above its bubble point at 4 kPa(a),
and flashes thionyl chloride into E-103 until its sensible heat is spent; as the thionyl
chloride leaves, the liquid's bubble point rises, so the flash ends well above the crude's first
bubble point. That heat is not a duty of its own: core's still ST101 starts at the bubble point
with all the thionyl chloride in the pot, so its boil-up Q3 and condenser Q4 already evaporate
and condense the thionyl chloride the flash takes (Q4 counts the forerun's condensation once;
Q3 is conservative by the flash's heat, which R-101's steam already supplied).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With BALANCE_OUTPUT
set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

CAPACITY = 1_000_000.0 / 7920.0  # kg/h of distilled methanesulfonyl chloride: 1000 t/a in 7920 h (D-002)
# mol of thionyl chloride dosed per mol of acid: Organic Syntheses, Coll. Vol. 4, 571 (2.0 mol on
# 1.5 mol) (D-004)
DOSE_RATIO = 2.0 / 1.5
RECYCLE = 0.9  # share of the forerun returned to the dose tank (SP101, D-008)
NAOH_EXCESS = 1.10  # caustic fed per caustic the off-gas neutralises (D-010)
NAOH_LIQUOR = 0.15  # mass fraction of NaOH in the diluted scrubber caustic (D-010)
NAOH_FEED = 0.50  # mass fraction of NaOH in the caustic soda feed (chlor-alkali-1's grade)
# mol of NaOH each off-gas component takes (reactions.yaml NEU_*)
NAOH_PER = {"HCL": 1.0, "SO2": 2.0, "SOCL2": 4.0, "MSCL": 2.0}
# kJ/kmol released by the neutralisations (reactions.yaml, ASSUMED orders of magnitude, D-010)
NEUTRALISATION = {"HCL": 130_000.0, "SO2": 160_000.0, "SOCL2": 400_000.0, "MSCL": 150_000.0}
# kJ/kmol NaOH released when 50 wt% caustic is diluted to 15 wt%: the order of the published
# integral heats of solution of NaOH (about -22 kJ/mol at 50 wt% against about -42 kJ/mol at 15
# wt%), ASSUMED (D-010)
DILUTION = 20_000.0
# kJ/(kmol K): ideal-gas heat capacities near 280-300 K (chemicals 1.5.2 via materials.yaml's
# cp_R: HCl 29.1, SO2 39.9, SOCl2 66.5; MsCl ASSUMED as SOCl2)
CP_GAS = {"HCL": 29.1, "SO2": 39.9, "SOCL2": 66.5, "MSCL": 66.5}
T_AMBIENT = 298.15  # K, the feeds (design basis)
T_CAUSTIC = 308.15  # K, the diluted caustic off its cooler, 10 K above the cooling water's supply (D-009)
T_SCRUB = 308.15  # K, the scrubber liquor on its cooler (D-010)
T_PRODUCT = 308.15  # K, to storage: 10 K above the cooling water's 298.15 K supply (D-009)
P_STILL = 4.0  # kPa(a), the stills (flowsheet ST101, ST102; D-007)
P_REACTOR = 101.325  # kPa(a), R-101 (D-005)


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "process" / name).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in load("materials.yaml")["components"]}
MW = {n: c["molar_mass"] for n, c in MATERIALS.items()}
CP = {n: c.get("liquid_heat_capacity", 0.0) for n, c in MATERIALS.items()}


def psat(name: str, t: float) -> float:
    """kPa, the NIST Antoine form of materials.yaml (log10 P/bar = a - b/(T + c))."""
    vp = MATERIALS[name].get("vapour_pressure")
    if not vp:
        return 0.0
    return 100.0 * 10.0 ** (vp["a"] - vp["b"] / (t + vp["c"]))


def bubble_point(kmols: dict[str, float], pressure: float) -> float:
    """K at `pressure` by Raoult's law (the stills' ideal liquid), bisection."""
    total = sum(kmols.values())
    x = {n: v / total for n, v in kmols.items() if v > 0}

    def excess(t: float) -> float:
        return sum(xi * psat(n, t) for n, xi in x.items()) - pressure

    low, high = 200.0, 600.0
    for _ in range(200):
        mid = 0.5 * (low + high)
        if excess(mid) > 0:
            high = mid
        else:
            low = mid
    return 0.5 * (low + high)


def adiabatic_flash(kmols: dict[str, float], temperature: float, pressure: float, step: float = 0.001):
    """A liquid above its bubble point at `pressure` flashed adiabatically and differentially
    (Rayleigh): each step cools the liquid by `step` K and its heat evaporates the vapour in
    equilibrium with it (Raoult), until the liquid is at its own bubble point. Returns the end
    temperature K, the kmol evaporated by component and the heat used, kJ."""
    left = {n: v for n, v in kmols.items() if v > 0}
    gone = dict.fromkeys(left, 0.0)
    heat = 0.0
    t = temperature
    while True:
        total = sum(left.values())
        partial = {n: v / total * psat(n, t) for n, v in left.items()}
        if sum(partial.values()) <= pressure:
            return t, gone, heat
        q = sum(v * CP[n] for n, v in left.items()) * step
        y = {n: p / sum(partial.values()) for n, p in partial.items()}
        evaporated = q / sum(y[n] * MATERIALS[n]["heat_of_vaporization"] for n in y)
        for n in left:
            left[n] -= y[n] * evaporated
            gone[n] += y[n] * evaporated
        heat += q
        t -= step


def state(streams: dict, sid: str) -> dict:
    return streams[sid]["state"]["design"]


def component_flows(streams: dict, sid: str) -> dict[str, float]:
    """kg/h of each component of a stream (flow kg/h; mole or mass fractions)."""
    s = state(streams, sid)
    comp = s["composition"]
    if comp["basis"] == "mass_fraction":
        return {n: s["flow"]["value"] * x for n, x in comp["values"].items()}
    mean = sum(x * MW[n] for n, x in comp["values"].items())
    return {n: s["flow"]["value"] * x * MW[n] / mean for n, x in comp["values"].items()}


def kmol(flows: dict[str, float]) -> dict[str, float]:
    return {n: v / MW[n] for n, v in flows.items()}


def heat_capacity_rate(flows: dict[str, float]) -> float:
    """kJ/(K h) of a liquid stream."""
    return sum(v / MW[n] * CP[n] for n, v in flows.items())


def main() -> None:
    sheet = load("flowsheet.yaml")
    streams = {s["id"]: s for s in sheet["streams"]}

    # the product and the feeds as propagate wrote them
    s1, s2, s3, s4 = (kmol(component_flows(streams, s)) for s in ("S1", "S2", "S3", "S4"))
    s10 = component_flows(streams, "S10")
    product = sum(s10.values())
    scale = CAPACITY / product
    acid_now = state(streams, "S1")["flow"]["value"]
    acid = acid_now * scale
    msa = s1["MSA"] * scale  # kmol/h of acid in the new feed
    # the thionyl chloride loop: S3 = R (S2 + S3 - L') with R the recycled share, so
    # S3 = R/(1 - R) (S2 - L'); L' (what the reaction, the water, the vent and the crude take)
    # scales with the acid
    loss = s2["SOCL2"] - s3.get("SOCL2", 0.0) * (1.0 - RECYCLE) / RECYCLE
    target = DOSE_RATIO * msa
    gain = RECYCLE / (1.0 - RECYCLE)
    fresh = (target + gain * loss * scale) / (1.0 + gain)
    fresh_kg = fresh * MW["SOCL2"]

    # the scrubber's caustic and its dilution water (D-010)
    s6 = kmol(component_flows(streams, "S6"))
    naoh = NAOH_EXCESS * sum(NAOH_PER[n] * v for n, v in s6.items())  # kmol/h
    caustic = naoh * MW["NAOH"] / NAOH_FEED
    water = naoh * MW["NAOH"] / NAOH_LIQUOR - caustic

    # the still's stream temperatures: bubble points at 4 kPa(a)
    t_distillate = bubble_point(kmol(component_flows(streams, "S9")), P_STILL)
    t_residue = bubble_point(kmol(component_flows(streams, "S11")), P_STILL)
    s5 = component_flows(streams, "S5")
    t_crude_bubble = bubble_point(kmol(s5), P_STILL)
    t_crude = state(streams, "S5")["temperature"]["value"]

    # duties, kW (kJ/h / 3600)
    q7 = heat_capacity_rate(s10) * (t_distillate - T_PRODUCT) / 3600.0
    t_gas = state(streams, "S6")["temperature"]["value"]
    reacted = sum(NEUTRALISATION[n] * v for n, v in s6.items())
    gas_warmed = sum(CP_GAS[n] * v for n, v in s6.items()) * (T_SCRUB - t_gas)
    s16 = component_flows(streams, "S16")
    liquor_warmed = heat_capacity_rate(s16) * (T_SCRUB - T_CAUSTIC)
    q8 = (reacted - gas_warmed - liquor_warmed) / 3600.0
    q9 = (naoh * DILUTION - heat_capacity_rate(s16) * (T_CAUSTIC - T_AMBIENT)) / 3600.0
    # the crude's flash on evacuation (a cross-check, no duty of its own: it is in Q3 and Q4)
    crude = kmol(s5)
    t_flash, flashed, flash_heat = adiabatic_flash(crude, t_crude, P_STILL)

    # cross-checks of what propagate wrote
    ratio = s4["SOCL2"] / s1["MSA"]
    yield_acid = kmol(s10)["MSCL"] / s1["MSA"]
    purity = s10["MSCL"] / product
    print(f"product S10 {product:.4f} kg/h at the current feeds; target {CAPACITY:.4f} kg/h")
    print(f"dose ratio S4/S1 now {ratio:.5f} mol/mol (target {DOSE_RATIO:.5f}); thionyl chloride taken by the loop L' {loss:.5f} kmol/h")
    print(f"feeds for {CAPACITY * 7.92:.0f} t/a: S1 acid {acid:.4f} kg/h, S2 fresh thionyl chloride {fresh_kg:.4f} kg/h")
    print(f"S10 MSCL {purity:.6f} by mass, SOCL2 {s10.get('SOCL2', 0.0) / product * 1e6:.0f} ppm, MSA {s10.get('MSA', 0.0) / product * 1e6:.3f} ppm")
    print(f"yield on the acid {yield_acid:.4%}")
    print(f"S14 caustic {caustic:.4f} kg/h ({naoh:.5f} kmol/h NaOH), S15 water {water:.4f} kg/h")
    print(f"S9 {t_distillate:.2f} K, S11 {t_residue:.2f} K at {P_STILL} kPa(a); crude bubble point {t_crude_bubble:.2f} K against {t_crude:.2f} K")
    print(f"Q7 product cooler {q7:.4f}, Q9 dilution {q9:.4f} kW")
    print(
        f"the crude's adiabatic flash at {P_STILL} kPa(a) ends at {t_flash:.1f} K, taking "
        f"{flashed['SOCL2'] / crude['SOCL2']:.1%} of its thionyl chloride and "
        f"{flashed['MSCL'] / crude['MSCL']:.1%} of its MsCl to E-103, {flash_heat / 3600:.3f} kW "
        f"year average (in Q3 and Q4, not a duty of its own)"
    )
    print(f"cross-check of the model duty Q8 (scrubber, written by propagate): {q8:.4f} kW")

    write_balance_output(
        {
            "design": {
                "S1": {"flow": round(acid, 4)},
                "S2": {"flow": round(fresh_kg, 4)},
                "S14": {"flow": round(caustic, 4)},
                "S15": {"flow": round(water, 4)},
                "S9": {"temperature": round(t_distillate, 2)},
                "S11": {"temperature": round(t_residue, 2)},
                "Q7": {"duty": round(q7, 4)},
                "Q9": {"duty": round(q9, 4)},
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
