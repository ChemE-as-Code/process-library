"""What core cannot calculate in the iodomethane plant (DESIGN.md D-008, D-009, D-011, D-012).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
semi-batch R101 with its vent, the batch stills ST101 and ST102 (one Rayleigh stage each), the
thiosulfate's reduction of the iodine W101 (a conversion step), the mixer M101 and the
pass-through steps from process/flowsheet.yaml. This script gives what core has no model for,
from the streams propagate wrote:

- the feeds that make 500 t/a of iodomethane (core propagates from the feeds and does not
  solve them for a product rate; the balance is linear in the feeds, so the iodine is scaled by
  the ratio of the target to the product S25, and the methanol and the red phosphorus follow at
  the molar ratios of CN 114195616 B, Example 1);
- the thiosulfate solution S13 and the wash water S17 (per kg of crude, ASSUMED);
- the phase splits D102 and D103 (two contacts each: methanol shared between the phases at an
  ASSUMED distribution coefficient, iodomethane dissolved in the aqueous phase at its water
  solubility, the organic saturated with water at an ASSUMED solubility) and the drying X101
  (the water down to an ASSUMED residual); core has no liquid-liquid model with sourced pairs for
  these liquids and no drying of a liquid over a desiccant;
- the temperatures of the stills' streams (bubble points by Raoult's law with the same NIST
  Antoine constants the stills use) and of the adiabatic washes and the dryer;
- R101's vent fraction: the iodomethane the batch's wet nitrogen and displaced head spaces carry
  past the vent condenser E-102 at 268 K, of what R101 forms (D-012);
- the duties Q1, Q4 to Q7 and Q9 to Q12 (no property package of core covers these liquids); since
  cheme-as-code 1.9.0 (core ADR 0059) propagate writes R101's Q2 and the stills' net boil-ups Q3
  and Q8 from the models; this script prints its own values of them as a cross-check only;
- the agitator, feeder, pump and fan powers P1 to P3 from the recipe's durations (core's
  `recipe.evaluate`).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With BALANCE_OUTPUT
set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

CAPACITY = 500_000.0 / 7920.0  # kg/h of iodomethane: 500 t/a in 7920 h (D-002)
# CN 114195616 B, Example 1: 144 kg methanol (99.5 %), 36 kg red phosphorus (98.5 %), 360 kg crude
# iodine (95 %): 4.4717 kmol methanol, 1.14483 kmol P and 1.34748 kmol I2 on a pure basis (D-004)
MEOH_PER_I2 = 4.4717 / 1.34748  # mol methanol per mol iodine
P_PER_I2 = 1.14483 / 1.34748  # mol red phosphorus per mol iodine
WATER_MEOH = 0.0005  # mass fraction of water in methanol-1's product (D-004)
WATER_IODINE = 0.002  # mass fraction of water in iodine-1's product (D-004)

# the washes (D-008); the patent gives no amounts
THIO_PER_CRUDE = 0.20  # kg of 5 wt% thiosulfate solution per kg of crude S10, in two contacts
THIO_STRENGTH = 0.05  # mass fraction of Na2S2O3 in S13
WATER_PER_CRUDE = 0.40  # kg of wash water per kg of crude, in two contacts
CONTACTS = 2  # CN 114195616 B, Examples 1-3: each wash twice
K_MEOH = 5.0  # methanol's mass-fraction ratio aqueous / organic phase (ASSUMED; no open data)
MEI_IN_WATER = 0.0139  # kg iodomethane per kg of water in the aqueous phase: 1.39e4 mg/L at 20 C
#                        (HSDB via PubChem CID 6328); a lower bound with methanol in the phase
WATER_IN_MEI = 0.001  # mass fraction of water dissolved in the washed organic phase (ASSUMED)
DRY_WATER = 0.0001  # mass fraction of water left after A-103 (ASSUMED within the patent's
#                     product spec, water below 80-200 ppm, CN 114195616 B, Examples 1-3)
# K104, the column on the still C-104: the share of each component of the still's distillate S22
# that reaches the product S24; the rest the column returns to the pot (D-010). The iodomethane's
# 0.99 and the water's 1.0 (iodomethane and water boil together; an upper bound) are ASSUMED; the
# methanol's share is calibrated so that the product holds PURITY iodomethane by mass
TO_PRODUCT = {"MEI": 0.99, "H2O": 1.0}
PURITY = 0.996  # CN 114195616 B, Example 3: 99.6 % (Examples 1-3: 99.5 to 99.7 %)
REFLUX = 2.0  # reflux ratio of K104 (ASSUMED; the patent gives none)
# heats of the washes and the dryer, ASSUMED orders (D-011)
H_MEOH_TO_WATER = -7300.0  # kJ/kmol of methanol transferred into the aqueous phase
H_THIO = -30000.0  # kJ/kmol of iodine reduced (reactions.yaml THIO)
H_HYDRATE = -16000.0  # kJ/kmol of water taken up by calcium chloride as its hydrate
CP_AQ = 4.1  # kJ/(kg K) of the dilute aqueous phases

T_AMBIENT = 298.15  # K, feeds from storage, the wash liquids (design basis)
T_REACT = 313.15  # K, R101 (D-005)
T_COND = 303.15  # K, condensate leaving E-101 and E-104 on cooling water (D-008, D-010)
T_PRODUCT = 283.15  # K, product subcooled on brine (D-010)
T_RES = 313.15  # K, ST101's residue cooled before it is drained (D-007)
T_RES2 = 303.15  # K, ST102's residue cooled (D-010)
T_VENT = 268.15  # K, the vent gas leaving the brine condenser E-102: 10 K above the 258 K brine
P = 101.325  # kPa(a)
R_GAS = 8.314  # kJ/(kmol K)
# iodomethane below its boiling point: NIST WebBook (C74884), Stull (1947), 218 to 315.6 K
MEI_LOW = (4.1554, 1177.78, -32.058)
H_VAP_MEI_298 = 27970.0  # kJ/kmol at 298 K (HSDB via PubChem CID 6328), for E-102
CP_GAS = {"N2": 29.1, "MEI": 44.1}  # kJ/(kmol K), ideal gas near 298 K (CRC via chemicals 1.5.2; N2 ASSUMED)
# nitrogen per batch (lca.yaml): 10 Nm3, of which the 5 Nm3 that purge R-101 and the phosphorus
# tank before the charge are dry; the other 5 Nm3 blanket V-102, A-103, C-104 and the tanks and
# leave saturated with iodomethane at 303 K (D-012)
N2_NM3_PER_BATCH = 10.0
N2_DRY_NM3_PER_BATCH = 5.0
RHO_AQ = 1000.0  # kg/m3 of the aqueous liquids, for the displaced head spaces

# powers (kW) and when they run (D-011)
P_R101_AGITATOR = 3.0  # kW, R-101's agitator: charge, warm, dose, react, hold, distil, cool
P_FEEDER = 0.75  # kW, the iodine's closed solids feeder and its nitrogen lock: the dosing
P_V102_AGITATOR = 1.5  # kW, V-102's agitator: 15 min of each of the four washes
P_PUMP = 1.1  # kW, a transfer pump
V102_PUMP_H = 3.0  # h a batch: the thiosulfate and water fed, the four aqueous layers drained, the transfer
P_C104_AGITATOR = 1.5  # kW, C-104's agitator: the distillation and the residue's cooling
C104_PUMP_H = 1.5  # h a batch: the dried crude received, the residue drained, the product to storage
P_FAN = 0.5  # kW, the vent fan to the adsorber, all the time
P_LOOP = 0.75  # kW, a jacket loop's circulation pump (hot water or chilled water) while the jacket works


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "process" / name).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in load("materials.yaml")["components"]}
MW = {n: c["molar_mass"] for n, c in MATERIALS.items()}
CP = {n: c.get("liquid_heat_capacity", 0.0) for n, c in MATERIALS.items()}
HVAP = {n: c.get("heat_of_vaporization", 0.0) for n, c in MATERIALS.items()}
VM = {n: c.get("liquid_molar_volume", 0.0) for n, c in MATERIALS.items()}


def psat(name: str, t: float) -> float:
    """kPa, the NIST Antoine form of materials.yaml (log10 P/bar = a - b/(T + c))."""
    vp = MATERIALS[name].get("vapour_pressure")
    if not vp:
        return 0.0
    return 100.0 * 10.0 ** (vp["a"] - vp["b"] / (t + vp["c"]))


def psat_mei_low(t: float) -> float:
    a, b, c = MEI_LOW
    return 100.0 * 10.0 ** (a - b / (t + c))


def bubble_point(kmols: dict[str, float]) -> float:
    """K at P by Raoult's law (an ideal liquid; dissolved non-volatiles dilute it, a suspended
    solid does not), bisection."""
    kmols = {n: v for n, v in kmols.items() if MATERIALS[n].get("phase") != "solid"}
    total = sum(kmols.values())
    x = {n: v / total for n, v in kmols.items() if v > 0}

    def excess(t: float) -> float:
        return sum(xi * psat(n, t) for n, xi in x.items()) - P

    low, high = 250.0, 450.0
    for _ in range(100):
        mid = 0.5 * (low + high)
        if excess(mid) > 0:
            high = mid
        else:
            low = mid
    return 0.5 * (low + high)


def state(streams: dict, sid: str) -> dict:
    return streams[sid].get("state", {}).get("design", {})


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


def latent(flows: dict[str, float]) -> float:
    """kJ/h to condense a vapour stream at the components' heats of vaporization."""
    return sum(v / MW[n] * HVAP[n] for n, v in flows.items())


def volume(flows: dict[str, float]) -> float:
    """m3/h of a liquid: the materials' molar volumes, the aqueous at RHO_AQ."""
    organic = sum(v / MW[n] * VM[n] for n, v in flows.items() if VM.get(n) and n != "H2O")
    rest = sum(v for n, v in flows.items() if not VM.get(n) or n == "H2O")
    return organic + rest / RHO_AQ


def fractions(flows: dict[str, float]) -> dict[str, float]:
    total = sum(flows.values())
    return {n: round(v / total, 9) for n, v in flows.items() if round(v / total, 9) > 0}


ORGANIC = ("MEI",)  # the organic phase's carrier; methanol and water are shared


def contact(org: dict[str, float], liquid: dict[str, float]) -> tuple[dict, dict, float]:
    """One wash contact: the organic phase and a fresh aqueous liquid settle into two phases.

    Methanol is shared at K_MEOH (mass fractions, aqueous over organic), iodomethane dissolves in
    the aqueous phase at MEI_IN_WATER per kg of its water, the organic leaves saturated with water
    at WATER_IN_MEI, everything else (salts, thiosulfate products) stays aqueous. Returns the two
    phases and the methanol (kmol/h) moved into the aqueous phase.
    """
    total = {n: org.get(n, 0.0) + liquid.get(n, 0.0) for n in set(org) | set(liquid)}
    water = total.get("H2O", 0.0)
    mei_aq = min(total.get("MEI", 0.0), MEI_IN_WATER * water)
    salts = {n: v for n, v in total.items() if n not in ("MEI", "MEOH", "H2O")}
    meoh = total.get("MEOH", 0.0)
    # bisection on the organic's methanol: w_aq = K w_org
    low, high = 0.0, meoh
    for _ in range(200):
        m_org = 0.5 * (low + high)
        org_base = total.get("MEI", 0.0) - mei_aq
        org_water = WATER_IN_MEI * (org_base + m_org) / (1.0 - WATER_IN_MEI)
        aq_mass = water - org_water + mei_aq + sum(salts.values()) + (meoh - m_org)
        org_mass = org_base + org_water + m_org
        if (meoh - m_org) / aq_mass > K_MEOH * m_org / org_mass:
            low = m_org  # too much in the aqueous phase: more stays organic
        else:
            high = m_org
    m_org = 0.5 * (low + high)
    org_base = total.get("MEI", 0.0) - mei_aq
    org_water = WATER_IN_MEI * (org_base + m_org) / (1.0 - WATER_IN_MEI)
    org_out = {"MEI": org_base, "MEOH": m_org, "H2O": org_water}
    aq_out = {"H2O": water - org_water, "MEI": mei_aq, "MEOH": meoh - m_org, **salts}
    moved = (org.get("MEOH", 0.0) - m_org) / MW["MEOH"]
    return org_out, aq_out, moved


def wash(org: dict[str, float], liquid: dict[str, float], contacts: int) -> tuple[dict, dict, float]:
    """`contacts` contacts, each with an equal share of the fresh liquid; the aqueous layers
    are drained together. Returns the organic, the combined aqueous and the methanol moved."""
    aq_all: dict[str, float] = {}
    moved = 0.0
    share = {n: v / contacts for n, v in liquid.items()}
    for i in range(contacts):
        # the first contact carries the whole of any salts already in the mixture
        org, aq, m = contact(org, share)
        moved += m
        for n, v in aq.items():
            aq_all[n] = aq_all.get(n, 0.0) + v
    return org, aq_all, moved


def recipe_hours() -> tuple[float, dict[tuple[str, str], float], float]:
    """The cycle (h), each operation's hours by (procedure, operation), R-101's working volume."""
    from chemeascode.domains.process.model import load as load_process
    from chemeascode.domains.process.recipe import evaluate, load_recipe

    process, _ = load_process(ROOT)
    recipe, _, _ = load_recipe(ROOT)
    result = evaluate(process, recipe)
    hours = {(s.procedure, s.operation): s.end - s.start for s in result.steps}
    working = next((v.working_volume for v in result.vessels if v.procedure == "REACT"), 0.0)
    return result.cycle_time, hours, working


def main() -> None:
    sheet = load("flowsheet.yaml")
    streams = {s["id"]: s for s in sheet["streams"]}
    recipe = load("recipe.yaml")
    batch_kg = recipe["batch_size"]["value"]
    hours_year = recipe["hours_per_year"]["value"]
    out: dict[str, dict] = {}

    # R101 and the first still, as propagate wrote them
    s1, s2, s5 = (component_flows(streams, s) for s in ("S1", "S2", "S5"))
    s6, s7 = component_flows(streams, "S6"), component_flows(streams, "S7")
    s8, s9 = component_flows(streams, "S8"), component_flows(streams, "S9")
    formed = (s6.get("MEI", 0.0) + s7.get("MEI", 0.0)) / MW["MEI"]

    # the washes: D102 after the thiosulfate (W101 has reduced the iodine), D103 the water
    s10 = component_flows(streams, "S10")
    crude = sum(s10.values())
    thio = THIO_PER_CRUDE * crude
    water_wash = WATER_PER_CRUDE * crude
    s14 = component_flows(streams, "S14") if "composition" in state(streams, "S14") else None
    if s14 is None:
        print("S14 not solved yet: run cheme process propagate --fill first")
        return
    org14 = {n: s14.get(n, 0.0) - (0.0 if n not in ("H2O",) else component_flows(streams, "S13").get("H2O", 0.0)) for n in ("MEI", "MEOH", "H2O")}
    liquid14 = {n: v for n, v in s14.items() if n not in ("MEI", "MEOH")}
    liquid14["H2O"] = component_flows(streams, "S13").get("H2O", 0.0)
    s15, s16, moved1 = wash(org14, liquid14, CONTACTS)
    s18, s19, moved2 = wash(s15, {"H2O": water_wash}, CONTACTS)
    # the dryer: the water down to DRY_WATER
    dry_base = sum(v for n, v in s18.items() if n != "H2O")
    left = DRY_WATER * dry_base / (1.0 - DRY_WATER)
    s21 = {"H2O": s18["H2O"] - left}
    s20 = {**s18, "H2O": left}

    # temperatures of the adiabatic washes and the dryer (D-011): the inlets mixed, the heat of
    # the thiosulfate's reaction and of the methanol taken into water
    s13 = component_flows(streams, "S13")
    c10, c13 = heat_capacity_rate(s10), sum(s13.values()) * CP_AQ
    i2_reduced = s10.get("I2", 0.0) / MW["I2"]
    heat14 = -H_THIO * i2_reduced - H_MEOH_TO_WATER * moved1
    t14 = (c10 * T_COND + c13 * T_AMBIENT + heat14) / (c10 + c13)
    c15 = heat_capacity_rate(s15)
    c17 = water_wash * CP_AQ
    t18 = (c15 * t14 + c17 * T_AMBIENT - H_MEOH_TO_WATER * moved2) / (c15 + c17)
    c18 = heat_capacity_rate(s18)
    t20 = t18 - H_HYDRATE * s21["H2O"] / MW["H2O"] / c18

    if "composition" not in state(streams, "S22"):
        print("S22 not solved yet: give the splits, then cheme process propagate --fill again")
        out = {
            "S13": {"flow": round(thio, 4)},
            "S14": {"temperature": round(t14, 2)},
            "S15": {"flow": round(sum(s15.values()), 4), "composition": fractions(s15), "temperature": round(t14, 2)},
            "S16": {"flow": round(sum(s16.values()), 4), "composition": fractions(s16), "temperature": round(t14, 2)},
            "S17": {"flow": round(water_wash, 4)},
            "S18": {"flow": round(sum(s18.values()), 4), "composition": fractions(s18), "temperature": round(t18, 2)},
            "S19": {"flow": round(sum(s19.values()), 4), "composition": fractions(s19), "temperature": round(t18, 2)},
            "S20": {"flow": round(sum(s20.values()), 4), "composition": fractions(s20), "temperature": round(t20, 2)},
            "S21": {"flow": round(sum(s21.values()), 5), "composition": fractions(s21), "temperature": round(t20, 2)},
        }
        write_balance_output({"design": out})
        return

    s22, s23 = component_flows(streams, "S22"), component_flows(streams, "S23")
    # K104: the specified split of the still's distillate
    to_product = dict(TO_PRODUCT)
    mei_p, h2o_p = s22["MEI"] * to_product["MEI"], s22.get("H2O", 0.0) * to_product["H2O"]
    meoh_p = mei_p / PURITY - mei_p - h2o_p
    to_product["MEOH"] = meoh_p / s22["MEOH"]
    s24 = {"MEI": mei_p, "MEOH": meoh_p, "H2O": h2o_p}
    s27 = {n: v - s24.get(n, 0.0) for n, v in s22.items() if v > 0}
    s25 = s24
    product = sum(s25.values())

    # the feeds that make CAPACITY: linear in the iodine
    i2_now = state(streams, "S5")["flow"]["value"]
    iodine = i2_now * CAPACITY / product
    n_i2 = iodine * (1.0 - WATER_IODINE) / MW["I2"]
    methanol = n_i2 * MEOH_PER_I2 * MW["MEOH"] / (1.0 - WATER_MEOH)
    phosphorus = n_i2 * P_PER_I2 * MW["P"]

    # the stills' temperatures (as their models: Raoult's law with the same Antoine constants)
    t8 = bubble_point({n: v for n, v in kmol(s6).items()})
    t9 = bubble_point(kmol(s9))
    t22 = bubble_point(kmol(s20))
    t23 = bubble_point(kmol(s23))
    c23, c27 = heat_capacity_rate(s23), heat_capacity_rate(s27)
    t28 = t23  # the column's hold-up and last cut drain back at the pot's end temperature

    # the recipe: the cycle and the operations' hours (core's recipe.evaluate)
    cycle, op_h, working = recipe_hours()
    batches = hours_year / cycle

    # R101's vent (D-012): the gas that leaves saturated with iodomethane at 303 K through E-102
    # and passes it at 268 K. Per batch: the wet nitrogen, the head spaces the liquids displace as
    # they fill V-102 (the crude, the thiosulfate and the wash water), A-103 (the washed crude),
    # C-104 (the dried crude) and the product tank, and R-101's own rise in volume over the dosing
    per_batch = cycle  # h of the flowsheet's flows in one batch
    s3 = {n: s1.get(n, 0.0) + s2.get(n, 0.0) for n in set(s1) | set(s2)}
    displaced = (
        volume(s10) + volume(s13) + volume({"H2O": water_wash}) + volume(s18) + volume(s20) + volume(s25)
        + max(0.0, volume(s6) - volume(s3))
    ) * per_batch  # m3 a batch
    n_wet = (N2_NM3_PER_BATCH - N2_DRY_NM3_PER_BATCH) / 22.414 + P * displaced / (R_GAS * T_COND)
    n_dry = N2_DRY_NM3_PER_BATCH / 22.414
    p_in, p_out = psat_mei_low(T_COND), psat_mei_low(T_VENT)
    mei_in = n_wet * p_in / (P - p_in)  # kmol a batch into E-102
    mei_out = n_wet * p_out / (P - p_out)  # kmol a batch past E-102
    vent_fraction = mei_out / (formed * per_batch)
    q7 = (
        (mei_in - mei_out) * H_VAP_MEI_298
        + (n_wet * CP_GAS["N2"] + 0.5 * (mei_in + mei_out) * CP_GAS["MEI"]) * (T_COND - T_VENT)
        + n_dry * CP_GAS["N2"] * (T_AMBIENT - T_VENT)
    ) / per_batch / 3600.0

    # duties, kW (kJ/h / 3600)
    q1 = heat_capacity_rate(s3) * (T_REACT - T_AMBIENT) / 3600.0
    released = -(-540_000.0) * formed / 6.0  # kJ/h, reactions.yaml MEI per 6 kmol of iodomethane
    dose_heat = heat_capacity_rate(s5) * (T_REACT - T_AMBIENT)
    q2 = (released - dose_heat) / 3600.0  # cross-check of the model's Q2
    q3 = latent(s8) / 3600.0  # cross-check of the still's net boil-up
    q4 = (heat_capacity_rate(s6) * max(0.0, t8 - T_REACT) + heat_capacity_rate(s9) * (t9 - max(t8, T_REACT))) / 3600.0
    q5 = (latent(s8) + heat_capacity_rate(s8) * (t8 - T_COND)) / 3600.0
    q6 = heat_capacity_rate(s9) * (t9 - T_RES) / 3600.0
    q8 = latent(s22) / 3600.0
    q9 = (heat_capacity_rate(s20) * (t22 - t20) + heat_capacity_rate(s23) * (t23 - t22)) / 3600.0
    q10 = ((1.0 + REFLUX) * latent(s22) + heat_capacity_rate(s24) * (t22 - T_COND)) / 3600.0
    q11 = heat_capacity_rate(s25) * (T_COND - T_PRODUCT) / 3600.0
    q12 = (c23 + c27) * (t28 - T_RES2) / 3600.0
    q13 = REFLUX * latent(s22) / 3600.0

    # power: kWh a batch over the cycle
    r101_on = sum(op_h.get(("REACT", o), 0.0) for o in ("charge", "heat", "dose", "react", "hold", "distil", "cool"))
    e1 = (P_R101_AGITATOR + P_LOOP) * r101_on + P_FEEDER * op_h.get(("REACT", "dose"), 0.0)
    e2 = P_V102_AGITATOR * 4 * 0.25 + P_PUMP * V102_PUMP_H
    c104_on = op_h.get(("DISTIL", "distil"), 0.0) + op_h.get(("DISTIL", "cool"), 0.0)
    e3 = (P_C104_AGITATOR + P_LOOP) * c104_on + P_PUMP * C104_PUMP_H + P_FAN * cycle
    p1, p2, p3 = e1 / cycle, e2 / cycle, e3 / cycle

    # iodine's fate (D-013): where the iodine fed goes, kmol I per hour
    i_fed = 2.0 * s5["I2"] / MW["I2"]
    i_fate = {
        "product S25": s25.get("MEI", 0.0) / MW["MEI"],
        "vent S12": s7.get("MEI", 0.0) / MW["MEI"],
        "residue S11 (MeI and I2)": s9.get("MEI", 0.0) / MW["MEI"] + 2.0 * s9.get("I2", 0.0) / MW["I2"],
        "wash liquors S16 + S19 (MeI)": (s16.get("MEI", 0.0) + s19.get("MEI", 0.0)) / MW["MEI"],
        "wash liquor S16 (NaI)": s16.get("NAI", 0.0) / MW["NAI"],
        "final residue S26 (MeI)": (s23.get("MEI", 0.0) + s27.get("MEI", 0.0)) / MW["MEI"],
    }

    print(f"product S25 {product:.4f} kg/h at the current feeds; target {CAPACITY:.4f} kg/h")
    print(f"feeds for {CAPACITY * 7.92:.0f} t/a: S5 iodine {iodine:.4f}, S1 methanol {methanol:.4f}, S2 red phosphorus {phosphorus:.4f} kg/h")
    print(f"cycle {cycle:.3f} h, {batches:.1f} batches/a; batch {product * cycle:.2f} kg at the current feeds; R-101 working volume {working:.3f} m3")
    print(f"S10 crude {crude:.4f} kg/h: {fractions(s10)}")
    print(f"S13 thiosulfate {thio:.4f} kg/h (Na2S2O3 {thio * THIO_STRENGTH / MW['NA2S2O3']:.5f} kmol/h, {thio * THIO_STRENGTH / MW['NA2S2O3'] / max(2 * i2_reduced, 1e-12):.1f} x the iodine's need); S17 water {water_wash:.4f} kg/h")
    print(f"S15 {sum(s15.values()):.4f} {fractions(s15)}; S16 {sum(s16.values()):.4f} kg/h")
    print(f"S18 {sum(s18.values()):.4f} {fractions(s18)}; S19 {sum(s19.values()):.4f}; S20 {sum(s20.values()):.4f}; S21 {s21['H2O']:.5f} kg/h")
    print(f"methanol moved: thiosulfate washes {moved1:.5f}, water washes {moved2:.5f} kmol/h")
    print(f"temperatures: S8 {t8:.2f}, S9 {t9:.2f}, S14 {t14:.2f}, S18 {t18:.2f}, S20 {t20:.2f}, S22 {t22:.2f}, S23 {t23:.2f} K")
    print(f"S22 one stage: MEI {s22['MEI'] / sum(s22.values()):.6f} by mass, methanol {s22.get('MEOH', 0) / sum(s22.values()):.6f}; K104 methanol share to the product {to_product['MEOH']:.4f}; S27 {sum(s27.values()):.4f} kg/h")
    print(f"S25 {product:.4f} kg/h, MEI {s25.get('MEI', 0) / product:.6f} by mass, methanol {s25.get('MEOH', 0) / product * 1e6:.0f} ppm, water {s25.get('H2O', 0) / product * 1e6:.0f} ppm")
    print(f"yield on iodine {s25.get('MEI', 0) / MW['MEI'] / i_fed:.4%}")
    print("iodine's fate (share of the iodine fed): " + ", ".join(f"{k} {v / i_fed:.4%}" for k, v in i_fate.items()) + f"; unaccounted {1 - sum(i_fate.values()) / i_fed:.4%}")
    print(f"vent: wet gas {n_wet:.4f} kmol a batch (of it displaced {displaced:.3f} m3), MeI into E-102 {mei_in:.4f}, past it {mei_out:.4f} kmol a batch; vent fraction {vent_fraction:.6f} of what R101 forms")
    print(f"Q1 {q1:.4f}, Q4 {q4:.4f}, Q5 {q5:.4f}, Q6 {q6:.4f}, Q7 {q7:.4f}, Q9 {q9:.4f}, Q10 {q10:.4f}, Q11 {q11:.4f}, Q12 {q12:.5f}, Q13 {q13:.4f} kW")
    print(f"cross-check of the model duties propagate writes: Q2 {q2:.4f} (released {released / 3600:.4f}, dose {dose_heat / 3600:.4f}), Q3 {q3:.4f}, Q8 {q8:.4f} kW")
    print(f"power: P1 {p1:.4f} ({e1:.2f} kWh a batch, R-101 on {r101_on:.2f} h), P2 {p2:.4f} ({e2:.2f} kWh), P3 {p3:.4f} ({e3:.2f} kWh, C-104 on {c104_on:.2f} h) kW")

    out = {
        "S1": {"flow": round(methanol, 4)},
        "S2": {"flow": round(phosphorus, 4)},
        "S5": {"flow": round(iodine, 4)},
        "S8": {"temperature": round(t8, 2)},
        "S9": {"temperature": round(t9, 2)},
        "S13": {"flow": round(thio, 4)},
        "S14": {"temperature": round(t14, 2)},
        "S15": {"flow": round(sum(s15.values()), 4), "composition": fractions(s15), "temperature": round(t14, 2)},
        "S16": {"flow": round(sum(s16.values()), 4), "composition": fractions(s16), "temperature": round(t14, 2)},
        "S17": {"flow": round(water_wash, 4)},
        "S18": {"flow": round(sum(s18.values()), 4), "composition": fractions(s18), "temperature": round(t18, 2)},
        "S19": {"flow": round(sum(s19.values()), 4), "composition": fractions(s19), "temperature": round(t18, 2)},
        "S20": {"flow": round(sum(s20.values()), 4), "composition": fractions(s20), "temperature": round(t20, 2)},
        "S21": {"flow": round(sum(s21.values()), 5), "composition": fractions(s21), "temperature": round(t20, 2)},
        "S22": {"temperature": round(t22, 2)},
        "S23": {"temperature": round(t23, 2)},
        "S24": {"flow": round(sum(s24.values()), 4), "composition": fractions(s24)},
        "S27": {"flow": round(sum(s27.values()), 5), "composition": fractions(s27), "temperature": round(t28, 2)},
        "S28": {"temperature": round(t28, 2)},
        "Q1": {"duty": round(q1, 4)},
        "Q4": {"duty": round(q4, 4)},
        "Q5": {"duty": round(q5, 4)},
        "Q6": {"duty": round(q6, 4)},
        "Q7": {"duty": round(q7, 4)},
        "Q9": {"duty": round(q9, 4)},
        "Q10": {"duty": round(q10, 4)},
        "Q11": {"duty": round(q11, 4)},
        "Q12": {"duty": round(q12, 5)},
        "Q13": {"duty": round(q13, 4)},
        "P1": {"duty": round(p1, 4)},
        "P2": {"duty": round(p2, 4)},
        "P3": {"duty": round(p3, 4)},
    }
    write_balance_output({"design": out})
    print(f"vent fraction for R101 (written by hand): {vent_fraction:.6f}")


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
