"""What core cannot calculate in the oxalyl chloride plant (DESIGN.md D-004, D-009, D-010).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
semi-batches R101 (chlorination) and R102 (reaction, with its vent and vent condenser E-102),
the batch still ST101 (the crude stripped off the heel at 15 kPa(a)), the batch still ST201 with
its column K-201, the mixers, the splitters, the recycles (torn at S3 and S26, core ADR 0060) and
the absorber's hydrolysis A101 from process/flowsheet.yaml. This script gives what core has no
model for, from the streams propagate wrote:

- the feeds that make 500 t/a of the product cut S17 (core propagates from the feeds and does
  not solve them for a product rate; the plant is linear in the feeds at fixed ratios, so every
  feed is scaled by the ratio of the target to the product S17, the ratios kept);
- the absorber water S21 for about 30 wt% hydrochloric acid, and the split D101 of the
  absorber's outlet S22 into the acid S23 and the tail gas S24;
- the temperatures core does not derive: the mixed charges S4, S10 and S26 from their inlets
  (S4 and S26 with their vessel's metal, which is at the previous step's temperature), the
  stills' streams at their bubble points (Raoult's law with the Antoine lines the stills use);
- the duties Q1 (the charge and R-101's metal warmed), Q9 (the product cooled), Q10 (the POCl3
  and C-201's metal cooled) and Q11 (the absorber), since no property package of core covers
  these liquids or HCl in water. Propagate writes R101's Q2, R102's Q3 and its vent
  condenser's Q4, and the stills' reboilers and condensers Q5 to Q8 from the models (core ADRs
  0059, 0061, 0062, 0063), the metal of R-101 in Q5 and of C-201 in Q7;
- the maximum technical temperatures of R101 and R102 (hazard.mtt): the bubble points at
  101.325 kPa(a) of R101's charge and of R102's final liquid, the lowest over each step, the
  suspended solids and the catalyst (non-volatile) left out of the liquid (D-011);
- the bubble point of R101's liquid at the end of the chlorine dosing with the chlorine that
  has accumulated (dissolved, not yet reacted) at the screening's accumulation of each
  rate-constant case (D-011);
- the stills' jackets by hand (core checks no jacket of a still's pot): the boil-up R-101's
  hot-water loop gives at the strip's end and C-201's steam at the rectification's end, where
  each wets the least area and is hottest, and the time to cool C-201's POCl3 and metal (D-007,
  D-008).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With BALANCE_OUTPUT
set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

CAPACITY = 500_000.0 / 7920.0  # kg/h of the product cut S17: 500 t/a in 7920 h (D-002)
# mol of fresh PCl3 per mol of oxalic acid: the PCl5 the reactions consume (2 for OXC, 1 for
# DEC: 1.85 at the selectivity 0.85) and the heel's purge; US 4 341 720 A, Example 20, adds
# 1025 g (7.46 mol) PCl3 to the previous residue for 375 g (4.17 mol) of acid, 1.79 (D-004)
PCL3_PER_ACID = 1.915
CL2_PER_PCL3 = 1.005  # mol chlorine per mol of fresh PCl3, a slight excess (D-004)
LUT_PER_PCL3 = 0.003137  # kg of catalyst make-up per kg of fresh PCl3: the heel purge's (D-004)
HCL_ACID = 0.30  # mass fraction of HCl in the absorber's acid (D-010)

T_AMBIENT = 298.15  # K, the feeds and the absorber water (design basis)
T_REACT = 333.15  # K, R101 and R102 (D-005)
T_COOLED = 303.15  # K, the product cut cooled on cooling water to storage (D-009)
T_VENT = 283.15  # K, the gas leaving the vent condenser E-102 (flowsheet R102, D-010)
T_ABSORBER = 313.15  # K, the absorber's outlets on cooling water (D-010)
P_ATM = 101.325  # kPa(a), R-101 while it reacts, C-201, the receivers
P_STRIP = 15.0  # kPa(a), R-101 while the crude is stripped off the heel (ST101, D-007)

# kJ/kmol, the absorber's reactions (reactions.yaml, CRC formation enthalpies, D-010)
HEAT = {"OXH": -67_000.0, "POH": -132_700.0}
# kJ/kmol of HCl from the gas into about 30 wt% acid: the integral heat of solution of HCl to
# about 4.7 mol of water per mol, ASSUMED -63 kJ/mol (an order of magnitude between the gas's
# solution in much water, about -75, and in little water; no open table read, D-010)
ABSORPTION = -63_000.0
CP_GAS = 29.1  # kJ/(kmol K), HCl, CO, CO2 and chlorine as ideal gases near 300 K (CRC via chemicals 1.5.2; CO2 37, taken as 29.1, D-010)
CP_ACID = 3.0  # kJ/(kg K), about 30 wt% hydrochloric acid (ASSUMED, D-010)
CP_WATER = 75.3  # kJ/(kmol K), liquid water (materials.yaml)

# components that stay in the liquid of a still or a reactor at its bubble point: the solids,
# the catalyst (as its hydrochloride) and the dissolved gases (the stills' nonvolatile, D-007)
NONVOLATILE = {"PCL5", "OXA", "LUT", "HCL", "CO", "CO2"}
# left out of the liquid for the MTTs: the suspended solids and the catalyst, which has no
# vapour pressure; leaving them out gives the lower, conservative bubble point (D-011)
MTT_LEAVE_OUT = {"PCL5", "OXA", "LUT"}
# R101's accumulation of the dosed chlorine at the end of the dosing, `cheme process
# reactor-hazards` on the design folder and on scratch copies with every rate's A divided by
# 10 and 100 (D-011)
ACCUMULATION = {"design": 0.0095, "k/10": 0.0254, "k/100": 0.0765}

T_POCL3 = 313.15  # K, the POCl3 cooled in C-201 before it is drained (D-008, D-009)
T_CW_MEAN = 303.15  # K, the jacket's cooling water between its 298.15 K supply and 308.15 K return
T_LPS = 412.0  # K, LP steam 350 kPa(a) on C-201's jacket (design basis)
U_JACKET = 0.300  # kW/(m2 K), the enamelled vessels' jackets (recipe.yaml, ASSUMED)
C201_VOLUME = 10.0  # m3, C-201 as `cheme process recipe` sizes it (a test compares)
R101_VOLUME = 16.0  # m3, R-101 as `cheme process recipe` sizes it (a test compares)
ASPECT = 1.2  # the vessels' height over diameter (recipe.yaml)
T_LOOP = 350.65  # K, R-101's hot-water loop at 353/348 K, its mean (recipe.yaml heating_temperature)


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "process" / name).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in load("materials.yaml")["components"]}
MW = {n: c["molar_mass"] for n, c in MATERIALS.items()}
CP = {n: c.get("liquid_heat_capacity", 0.0) for n, c in MATERIALS.items()}


def psat(name: str, t: float) -> float:
    """kPa, the Antoine form of materials.yaml (log10 P/bar = a - b/(T + c))."""
    vp = MATERIALS[name].get("vapour_pressure")
    if not vp or name in NONVOLATILE:
        return 0.0
    return 100.0 * 10.0 ** (vp["a"] - vp["b"] / (t + vp["c"]))


def bubble_point(
    kmols: dict[str, float], pressure: float, solids: bool = False, leave_out: frozenset | set = frozenset()
) -> float:
    """K at `pressure` by Raoult's law, bisection. With `solids` the suspended solids count in
    the liquid's mole fractions, as core's batch still counts them (its stream temperatures);
    without, they are left out, which gives a lower bubble point. `leave_out` drops further
    components from the liquid (the MTTs: MTT_LEAVE_OUT)."""
    liquid = {
        n: v
        for n, v in kmols.items()
        if v > 0 and n not in leave_out and (solids or MATERIALS[n].get("phase") != "solid")
    }
    total = sum(liquid.values())
    x = {n: v / total for n, v in liquid.items()}

    def excess(t: float) -> float:
        return sum(xi * psat(n, t) for n, xi in x.items()) - pressure

    low, high = 250.0, 450.0
    for _ in range(100):
        mid = 0.5 * (low + high)
        if excess(mid) > 0:
            high = mid
        else:
            low = mid
    return 0.5 * (low + high)


def state(streams: dict, sid: str) -> dict:
    return streams[sid]["state"]["design"]


def component_flows(streams: dict, sid: str) -> dict[str, float]:
    """kg/h of each component of a stream (flow kg/h; mole or mass fractions)."""
    s = state(streams, sid)
    comp = s["composition"]
    if comp["basis"] == "mass_fraction":
        return {n: s["flow"]["value"] * x for n, x in comp["values"].items() if x > 0}
    mean = sum(x * MW[n] for n, x in comp["values"].items())
    return {n: s["flow"]["value"] * x * MW[n] / mean for n, x in comp["values"].items() if x > 0}


def kmol(flows: dict[str, float]) -> dict[str, float]:
    return {n: v / MW[n] for n, v in flows.items()}


def heat_capacity_rate(flows: dict[str, float]) -> float:
    """kJ/(K h) of a liquid or slurry stream."""
    return sum(v / MW[n] * CP[n] for n, v in flows.items())


def mixed_temperature(inlets: list[tuple[dict[str, float], float]], metal: tuple[float, float] | None = None) -> float:
    """K of a mixture from its inlets' heat capacity rates and temperatures (no heat of mixing),
    with `metal` (kJ/(K h) on the flowsheet's basis, K) the vessel's metal it meets."""
    rates = [(heat_capacity_rate(f), t) for f, t in inlets] + ([metal] if metal else [])
    return sum(c * t for c, t in rates) / sum(c for c, _ in rates)


def recipe_vessels() -> tuple[float, dict[str, float]]:
    """h of the flowsheet's flows one batch makes (the recipe's batch size over the
    flowsheet's rate of its stream, as core's batch_hours), and each unit procedure's
    metal_heat_capacity, kJ/K."""
    recipe = load("recipe.yaml")
    metal = {up["id"]: up.get("vessel", {}).get("metal_heat_capacity", 0.0) for up in recipe["unit_procedures"]}
    return recipe["batch_size"]["value"], metal


def wetted_area(content: float, diameter: float) -> float:
    """m2 of shell and flat bottom wetted by `content` m3 (core's recipe.wetted_area; a test
    compares)."""
    bottom = math.pi * diameter**2 / 4.0
    return math.pi * diameter * content / bottom + bottom


def liquid_volume(flows: dict[str, float]) -> float:
    """m3/h of a liquid stream from materials.yaml's liquid molar volumes."""
    return sum(v / MW[n] * MATERIALS[n]["liquid_molar_volume"] for n, v in flows.items())


def r101_end_of_dosing(s5: dict[str, float], s6: dict[str, float], accumulation: float) -> dict[str, float]:
    """kmol/h of R101's content at the end of the chlorine dosing with `accumulation` of the
    dosed chlorine left unreacted (dissolved): the rest has turned PCl3 into PCl5 (CHL)."""
    n = kmol(s5)
    dosed = s6["CL2"] / MW["CL2"]
    reacted = min((1.0 - accumulation) * dosed, n.get("PCL3", 0.0))
    n["PCL3"] = n.get("PCL3", 0.0) - reacted
    n["PCL5"] = n.get("PCL5", 0.0) + reacted
    n["CL2"] = n.get("CL2", 0.0) + dosed - reacted
    return n


def fractions(flows: dict[str, float]) -> dict[str, float]:
    total = sum(flows.values())
    return {n: round(v / total, 9) for n, v in flows.items() if round(v / total, 9) > 0}


def temperature(streams: dict, sid: str) -> float:
    return state(streams, sid)["temperature"]["value"]


def main() -> None:
    sheet = load("flowsheet.yaml")
    streams = {s["id"]: s for s in sheet["streams"]}

    # the feeds that make CAPACITY: the plant is linear in its feeds at fixed ratios
    product = sum(component_flows(streams, "S17").values())
    acid = component_flows(streams, "S8")["OXA"] * CAPACITY / product
    pcl3 = acid / MW["OXA"] * PCL3_PER_ACID * MW["PCL3"]
    cl2 = pcl3 / MW["PCL3"] * CL2_PER_PCL3 * MW["CL2"]
    lut = pcl3 * LUT_PER_PCL3
    scale = CAPACITY / product  # every flow of the converged plant scales with it

    # the vessels' metal on the flowsheet's basis: kJ/K per batch over the hours one batch makes
    batch_size, metal = recipe_vessels()
    hours = batch_size / product  # h of the flowsheet's flows per batch
    metal_r101 = metal["REACT"] / hours  # kJ/(K h)
    metal_c201 = metal["DISTIL"] / hours

    # temperatures of the mixed charges from their inlets (D-009)
    s1, s2, s3 = (component_flows(streams, k) for k in ("S1", "S2", "S3"))
    s8, s9, s25 = (component_flows(streams, k) for k in ("S8", "S9", "S25"))
    s11, s13, s14 = (component_flows(streams, k) for k in ("S11", "S13", "S14"))
    s16, s18 = component_flows(streams, "S16"), component_flows(streams, "S18")
    t14 = bubble_point(kmol(s14), P_STRIP, solids=True)  # the heel at the strip's end, kept in R-101
    # the fresh PCl3 meets the heel and R-101's metal, both at the strip's end
    t4 = mixed_temperature([(s1, T_AMBIENT), (s2, T_AMBIENT), (s3, t14)], (metal_r101, t14))
    t25 = bubble_point(kmol(s25), P_ATM)  # the off-cut as K-201 condenses it
    t10 = mixed_temperature([(s8, T_AMBIENT), (s9, T_POCL3)])
    t13 = bubble_point(kmol(s13), P_STRIP)  # the crude as E-103 condenses it, not subcooled
    # C-201's charge: the crude, the off-cut cooled in its receiver, the metal at the POCl3's
    # cooled temperature
    t26 = mixed_temperature([(s13, t13), (s25, T_AMBIENT)], (metal_c201, T_POCL3))
    t16 = bubble_point(kmol(s16), P_ATM)  # the product cut as K-201 condenses it
    t18 = bubble_point(kmol(s18), P_ATM)  # the POCl3 left in C-201 at the end
    offcut_lost = heat_capacity_rate(s25) * (t25 - T_AMBIENT) / 3600.0 * scale  # kW to air

    # maximum technical temperatures (D-011): the bubble points at atmospheric pressure, where
    # the vented vessel boils; R101's is lowest at its charge (PCl3 turns into solid PCl5),
    # R102's at its end (the oxalyl chloride it forms is the most volatile)
    s5 = component_flows(streams, "S5")
    mtt_r101 = bubble_point(kmol(s5), P_ATM, leave_out=MTT_LEAVE_OUT)
    mtt_r102 = bubble_point(kmol(s11), P_ATM, leave_out=MTT_LEAVE_OUT)
    t_strip0 = bubble_point(kmol(s11), P_STRIP, solids=True)  # the still's first bubble point
    # R101 at the end of the chlorine dosing with the accumulated chlorine dissolved (D-011)
    s6 = component_flows(streams, "S6")
    chlorine = {}
    for name, accumulation in ACCUMULATION.items():
        n = r101_end_of_dosing(s5, s6, accumulation)
        chlorine[name] = (
            bubble_point(n, P_ATM, leave_out=MTT_LEAVE_OUT),
            sum(psat(c, T_REACT) * v for c, v in n.items() if c not in MTT_LEAVE_OUT and MATERIALS[c].get("phase") != "solid")
            / sum(v for c, v in n.items() if c not in MTT_LEAVE_OUT and MATERIALS[c].get("phase") != "solid"),
            n["CL2"] * hours,  # kmol a batch
        )

    # duties, kW (kJ/h / 3600), at the scaled flows
    s4 = component_flows(streams, "S4")
    q1 = (heat_capacity_rate(s4) + metal_r101) * (T_REACT - t4) / 3600.0 * scale
    q9 = heat_capacity_rate(s16) * (t16 - T_COOLED) / 3600.0 * scale
    q10 = (heat_capacity_rate(s18) + metal_c201) * (t18 - T_POCL3) / 3600.0 * scale
    q10_metal = metal_c201 * (t18 - T_POCL3) / 3600.0 * scale

    # R-101's jacket on the hot-water loop at the strip's end (D-007): the heel wets the least
    # area and the still is hottest
    d101 = (4.0 * R101_VOLUME / (math.pi * ASPECT)) ** (1.0 / 3.0)
    heel = liquid_volume(s14) * hours  # m3 a batch, the suspended PCl5 with the liquid
    area101 = wetted_area(heel, d101)
    strip_limit = U_JACKET * area101 * (T_LOOP - t14)  # kW

    # C-201's jacket by hand (D-008): at the still's end the POCl3 wets the least area
    diameter = (4.0 * C201_VOLUME / (math.pi * ASPECT)) ** (1.0 / 3.0)
    residue = liquid_volume(s18) * hours  # m3 a batch
    area = wetted_area(residue, diameter)
    boilup_limit = U_JACKET * area * (T_LPS - t18)  # kW
    capacity = (heat_capacity_rate(s18) * hours + metal["DISTIL"])  # kJ/K
    cool_hours = capacity / (U_JACKET * area) * math.log((t18 - T_CW_MEAN) / (T_POCL3 - T_CW_MEAN)) / 3600.0

    # the absorber (D-010): the vented OXCL and POCl3 hydrolysed (A101), the HCl dissolved
    s12 = {n: v * scale for n, v in component_flows(streams, "S12").items()}
    n12 = kmol(s12)
    extent_oxh = n12.get("OXCL", 0.0)
    extent_poh = n12.get("POCL3", 0.0)
    water_used = (extent_oxh + 3.0 * extent_poh) * MW["H2O"]
    hcl = s12.get("HCL", 0.0) + (2.0 * extent_oxh + 3.0 * extent_poh) * MW["HCL"]
    h3po4 = extent_poh * MW["H3PO4"]
    pcl3_gas = s12.get("PCL3", 0.0)  # to the acid, where it hydrolyses (not modelled, D-010)
    water_left = hcl / HCL_ACID - hcl - h3po4 - pcl3_gas
    water = water_left + water_used
    acid_out = {"H2O": water_left, "HCL": hcl, "H3PO4": h3po4, "PCL3": pcl3_gas}
    co = s12.get("CO", 0.0) + extent_oxh * MW["CO"]
    co2 = s12.get("CO2", 0.0) + extent_oxh * MW["CO2"]
    tail = {"CO": co, "CO2": co2, "CL2": s12.get("CL2", 0.0)}
    released = -(HEAT["OXH"] * extent_oxh + HEAT["POH"] * extent_poh + ABSORPTION * hcl / MW["HCL"])
    gas_in = sum(n12.get(n, 0.0) for n in ("HCL", "CO", "CO2", "CL2", "OXCL", "POCL3", "PCL3"))
    warmed = (water / MW["H2O"] * CP_WATER * (T_ABSORBER - T_AMBIENT)
              + gas_in * CP_GAS * (T_ABSORBER - T_VENT))
    q11 = (released - warmed) / 3600.0

    # what the still's model leaves out (D-007): R102's mass enters ST101 at 333.15 K, above its
    # bubble point at 15 kPa(a), and core does not model the flash (no heat-up, and no credit):
    # the heat above the bubble point evaporates part of the crude for free, so Q5 and Q6 are
    # upper bounds by about this much
    flash = (heat_capacity_rate(s11) + metal_r101) * (T_REACT - t_strip0) / 3600.0

    # cross-checks of what the models write
    n8 = kmol(s8)["OXA"]
    oxcl = s16.get("OXCL", 0.0) / MW["OXCL"]
    yield_acid = oxcl / n8
    vented = component_flows(streams, "S12").get("OXCL", 0.0) / MW["OXCL"]
    formed_share = (oxcl + vented) / n8

    print(f"product S17 {product:.4f} kg/h at the current feeds; target {CAPACITY:.4f} kg/h (scale {scale:.6f})")
    print(f"feeds: S1 PCl3 {pcl3:.4f}, S2 catalyst {lut:.4f}, S6 chlorine {cl2:.4f}, S8 oxalic acid {acid:.4f}, S21 water {water:.4f} kg/h")
    print(f"product S16: {s16['OXCL'] / sum(s16.values()):.5f} OXCL by mass; yield on the acid {yield_acid:.4%}; vented OXCL {vented / n8:.4%} of the acid")
    print(f"temperatures: S4 {t4:.2f}, S10 {t10:.2f} (off-cut S25 {t25:.2f}), S13 {t13:.2f}, S14 {t14:.2f}, S16 {t16:.2f}, S18 {t18:.2f} K; ST101 starts at {t_strip0:.2f} K at {P_STRIP} kPa(a)")
    print(f"MTT: R101 {mtt_r101:.2f} K (charge S5), R102 {mtt_r102:.2f} K (final liquid S11), the solids and the catalyst left out")
    for name, (t, p, n) in chlorine.items():
        print(f"R101 at the end of the dosing, {name} ({ACCUMULATION[name]:.2%} of the chlorine accumulated, {n:.3f} kmol a batch): bubble point {t:.2f} K, vapour pressure at {T_REACT} K {p:.1f} kPa")
    print(f"metal per batch: R-101 {metal['REACT']:.0f} kJ/K, C-201 {metal['DISTIL']:.0f} kJ/K; {hours:.4f} h of flows per batch")
    print(f"R-101 at the strip's end: {heel:.3f} m3 of heel, {area101:.3f} m2 wetted (D {d101:.4f} m); the hot-water loop gives {strip_limit:.2f} kW")
    print(f"C-201 at the still's end: {residue:.3f} m3 of POCl3, {area:.3f} m2 wetted (D {diameter:.4f} m); jacket on LP steam gives {boilup_limit:.2f} kW; cooling {t18:.2f} -> {T_POCL3} K on water at {T_CW_MEAN} K: {cool_hours:.3f} h ({capacity:.0f} kJ/K)")
    print(f"metal heat: Q10's metal share {q10_metal:.4f} kW; the off-cut's heat lost to air in its receiver {offcut_lost:.4f} kW; S26 {t26:.2f} K")
    print(f"ST101's charge flash not credited by the still's model: {flash:.4f} kW (Q5 and Q6 upper bounds by it)")
    print(f"duties: Q1 {q1:.4f}, Q9 {q9:.4f}, Q10 {q10:.4f}, Q11 {q11:.4f} kW (absorber released {released / 3600:.4f}, warmed {warmed / 3600:.4f})")
    print(f"acid S23 {sum(acid_out.values()):.4f} kg/h, tail S24 {sum(tail.values()):.4f} kg/h; product and vented OXCL {formed_share:.4%} of the acid")

    write_balance_output(
        {
            "design": {
                "S1": {"flow": round(pcl3, 4)},
                "S2": {"flow": round(lut, 4)},
                "S4": {"temperature": round(t4, 2)},
                "S6": {"flow": round(cl2, 4)},
                "S8": {"flow": round(acid, 4)},
                "S10": {"temperature": round(t10, 2)},
                "S26": {"temperature": round(t26, 2)},
                "S13": {"temperature": round(t13, 2)},
                "S14": {"temperature": round(t14, 2)},
                "S16": {"temperature": round(t16, 2)},
                "S18": {"temperature": round(t18, 2)},
                "S21": {"flow": round(water, 4)},
                "S23": {"flow": round(sum(acid_out.values()), 4), "composition": fractions(acid_out)},
                "S24": {"flow": round(sum(tail.values()), 4), "composition": fractions(tail)},
                "Q1": {"duty": round(q1, 4)},
                "Q9": {"duty": round(q9, 4)},
                "Q10": {"duty": round(q10, 4)},
                "Q11": {"duty": round(q11, 4)},
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
