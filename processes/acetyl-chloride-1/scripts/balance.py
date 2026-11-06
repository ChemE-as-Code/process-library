"""What core cannot calculate in the acetyl chloride plant (DESIGN.md D-006).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
semi-batch R101 with its HCl vent, the batch still ST101 (one Rayleigh stage), the pass-through
steps E101, E102, E103 and the mixers M102 and A101 from process/flowsheet.yaml. This script gives
what core has no model for, from the streams propagate wrote:

- the feeds that make 2000 t/a of acetyl chloride (core propagates from the feeds and does not
  solve them for a product rate; the balance is linear in the feeds, so the PCl3 is scaled by
  the ratio of the target to the product S10, and the acetic acid follows at 3 mol per mol);
- the phase split D101 in R-101: a specified split of the reaction mass S4 into the upper
  (S6) and lower (S7) phases, calibrated to the lower phase of CS 272 248 B2, Example 1
  (core has no liquid-liquid model for these liquids);
- the column K101 on the still: its rectification is a specified split of the still's
  distillate S8 (core's still has no reflux, core ADR 0055, core#173), giving S10 and S11;
- the scrubber water S15 for a 1 wt% HCl bleed;
- the temperatures of the still's streams (bubble points by Raoult's law with the same NIST
  Antoine constants the still uses), of the mixed residue S12 and of the adiabatic scrubber's
  liquor S16;
- the duties Q1 and Q4 to Q8 (no property package of core covers these liquids, and core has
  no column with reflux). Since cheme-as-code 1.9.0 (core ADR 0059) propagate writes R101's Q2
  (its reactions' heat less the PCl3 dose warmed) and the still's Q3 (its net boil-up's latent
  heat) from the models; this script prints its own values of both as a cross-check only. Q7
  is the reboiler's share for the column's reflux (the reflux ratio times the latent heat of
  the still's distillate) and Q8 the still's heat-up (the charge to its bubble point, the
  residue to its end temperature), which the one-stage still does not hold (D-009, D-014).
  The script also bounds R-101's own evaporative cooling: the vapour that the gas leaving
  R-101 while it holds the reacting mass carries to E-103, which the model leaves out of Q2
  (D-009, D-014). E-103's load Q6 is taken per source (R-101's gas off the reacting mass, the
  still's and receivers' nitrogen at 303 K, R-101's dry purge); R101's vent fraction stays the
  upper bound with all of E-103's inert saturated (D-010, D-014).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With BALANCE_OUTPUT
set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

CAPACITY = 2_000_000.0 / 7920.0  # kg/h of acetyl chloride: 2000 t/a in 7920 h (D-002)
ACID_RATIO = 3.0  # mol acetic acid per mol PCl3: CS 272 248 B2, Example 1 (180 g, 3 mol, on 1.0 mol) (D-004)
WATER = 0.000691  # mass fraction of water in the acetic acid: acetic-acid-1's product S21 (D-004)

# D101: share of each component of the reaction mass S4 that settles into the lower phase S7,
# calibrated to CS 272 248 B2, Example 1 (lower phase 96 g per mol PCl3: about 6 wt% HCl, 2 wt%
# acetyl chloride, 10 wt% acetic acid, the rest phosphorous acid) (D-006)
TO_LOWER = {"H3PO3": 0.995, "ACOH": 0.95, "PCL3": 0.05, "ACCL": 0.008, "H2O": 1.0}
# K101, the column on the still: share of each component of the still's distillate S8 that
# reaches the product S10; the rest the column returns to the pot (D-008). PCl3: 6 % of the
# phosphorus went overhead in US 4 209 460 A, Example 1 (a 2 m packed column at reflux 1:1,
# 125 ppm P in the feed, 9 ppm in 83 % of it taken overhead: 0.83 x 9 / 125 = 0.06)
TO_PRODUCT = {"ACCL": 0.99, "PCL3": 0.06, "ACOH": 0.01, "H3PO3": 0.0, "H2O": 1.0}
REFLUX = 1.0  # reflux ratio of K101 (US 4 209 460 A, Examples 1-3: 1:1) (D-008)
HCL_LIQUOR = 0.01  # mass fraction of HCl in the scrubber bleed (D-010)

T_AMBIENT = 298.15  # K, the feeds from storage and the scrubber water (design basis)
T_REACT = 313.15  # K, R101 (D-005)
T_PRODUCT = 303.15  # K, the product and the residue cooled on cooling water (D-008, D-009)
T_VENT = 268.15  # K, the vent gas leaving the brine condenser E103: 10 K above the 258 K brine (D-010)
P = 101.325  # kPa(a), R-101, the still and the vent (D-005, D-007)

# kJ/kmol of the reactions (reactions.yaml, derived from CRC formation enthalpies, D-005)
HEAT = {"ACCL": -10_500.0, "HYD": -64_200.0, "AHYD": -48_000.0}
# kJ/kmol of HCl from gas at 268 K into the dilute bleed: the integral heat of solution of HCl
# in much water, about -75 kJ/mol, ASSUMED order of magnitude (D-010)
ABSORPTION = 75_000.0
CP_GAS = {"HCL": 29.1, "N2": 29.1, "ACCL": 67.8}  # kJ/(kmol K), ideal gas near 298 K (CRC via chemicals 1.5.2; N2 ASSUMED as HCl)
CP_ACID = 4.1  # kJ/(kg K), the 1 wt% bleed (ASSUMED, about water's 4.18)
# nitrogen that leaves through E103 (D-010, lca.yaml): all 8 Nm3 a batch uses, ASSUMED. Of it
# 5 Nm3 purge R-101 (2.5 m3, two volumes) on the dry vessel before the charge (the recipe's
# `inert` step), so it carries no vapour; R-101's blanket is static. The other 3 Nm3 purge and
# blanket the still and the receivers and leave from K-101's condenser and the receivers, taken
# saturated over the product at its 303 K (D-010, D-014)
N2_VENT_NM3_PER_BATCH = 8.0
N2_R101_PURGE_NM3_PER_BATCH = 5.0
N2_STILL_NM3_PER_BATCH = N2_VENT_NM3_PER_BATCH - N2_R101_PURGE_NM3_PER_BATCH
# the gas that leaves R-101 while it holds the reacting mass: the HCl it forms and the head space
# the dosed PCl3 displaces (its liquid volume, materials.yaml), taken saturated with the upper
# phase's vapour at 313 K, an upper bound (recipe.yaml, D-003, D-014)
R_GAS = 8.314  # kJ/(kmol K)


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "process" / name).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in load("materials.yaml")["components"]}
MW = {n: c["molar_mass"] for n, c in MATERIALS.items()}
CP = {n: c.get("liquid_heat_capacity", 0.0) for n, c in MATERIALS.items()}
HVAP = {n: c.get("heat_of_vaporization", 0.0) for n, c in MATERIALS.items()}


def psat(name: str, t: float) -> float:
    """kPa, the NIST Antoine form of materials.yaml (log10 P/bar = a - b/(T + c))."""
    vp = MATERIALS[name].get("vapour_pressure")
    if not vp:
        return 0.0
    return 100.0 * 10.0 ** (vp["a"] - vp["b"] / (t + vp["c"]))


def bubble_point(kmols: dict[str, float]) -> float:
    """K at P by Raoult's law (the still's ideal liquid), bisection."""
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


def fractions(flows: dict[str, float]) -> dict[str, float]:
    total = sum(flows.values())
    return {n: round(v / total, 9) for n, v in flows.items() if round(v / total, 9) > 0}


def main() -> None:
    sheet = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    streams = {s["id"]: s for s in sheet["streams"]}
    recipe = yaml.safe_load((ROOT / "process" / "recipe.yaml").read_text(encoding="utf-8"))
    batch_kg = recipe["batch_size"]["value"]
    hours = recipe["hours_per_year"]["value"]

    # D101: the phase split of the reaction mass
    s4 = component_flows(streams, "S4")
    s7 = {n: v * TO_LOWER.get(n, 0.0) for n, v in s4.items() if v > 0}
    s6 = {n: v - s7.get(n, 0.0) for n, v in s4.items() if v > 0}
    s6 = {n: v for n, v in s6.items() if v > 1e-12}
    if "composition" not in streams["S8"].get("state", {}).get("design", {}):
        # first pass: the still has no charge yet; give the phase split, then propagate again
        print("S8 not solved yet: run cheme process propagate --fill with S6 first")
        write_balance_output({"design": {
            "S6": {"flow": round(sum(s6.values()), 4), "composition": fractions(s6)},
            "S7": {"flow": round(sum(s7.values()), 4), "composition": fractions(s7)},
        }})
        return

    # K101: the specified split of the still's distillate
    s8 = component_flows(streams, "S8")
    s10 = {n: v * TO_PRODUCT[n] for n, v in s8.items() if v > 0}
    s11 = {n: v - s10.get(n, 0.0) for n, v in s8.items() if v > 0}
    product = sum(s10.values())

    # the feeds that make CAPACITY: linear in the PCl3
    pcl3_now = state(streams, "S3")["flow"]["value"]
    pcl3 = pcl3_now * CAPACITY / product
    acid = pcl3 / MW["PCL3"] * ACID_RATIO * MW["ACOH"] / (1.0 - WATER)

    # temperatures: the still's bubble points (as ST101's model), the mixed residue
    t_still0 = bubble_point(kmol(s6))
    s9 = component_flows(streams, "S9")
    t_still1 = bubble_point(kmol(s9))
    c9, c11 = heat_capacity_rate(s9), heat_capacity_rate(s11)
    t_return = t_still1  # the column's hold-up and last cut drain back at the pot's end temperature
    t12 = (c9 * t_still1 + c11 * t_return) / (c9 + c11)

    # the vent's upper bound as until core 1.9.0: all of E-103's inert (the HCl of R101 and the
    # batch's whole nitrogen) taken saturated with the upper phase's vapour at 313 K, cooled to
    # 268 K in E103. It still sets R101's vent fraction (an upper bound, D-010) and R-101's own
    # evaporative cooling below; E-103's load Q6 is taken per source further down
    batches = CAPACITY * hours / batch_kg  # batches a year at the recipe's batch size
    hcl = component_flows(streams, "S5").get("HCL", 0.0)
    n_hcl = hcl / MW["HCL"]
    n_n2 = N2_VENT_NM3_PER_BATCH / 22.414 * batches / hours  # kmol/h
    x6 = {n: v / sum(kmol(s6).values()) for n, v in kmol(s6).items()}
    p_hot = {n: x6.get(n, 0.0) * psat(n, T_REACT) for n in ("ACCL", "PCL3", "ACOH")}
    p_cold = psat("ACCL", T_VENT)  # the condensate is nearly pure acetyl chloride
    inert = n_hcl + n_n2
    vap_hot = {n: inert * p / (P - sum(p_hot.values())) for n, p in p_hot.items()}
    vap_cold = inert * p_cold / (P - p_cold)  # kmol/h of acetyl chloride passing E103
    # E103 condenses the acetyl chloride down to its vapour pressure at 268 K and all the acetic
    # acid; the PCl3 (3.6 kPa at 268 K, above its 0.5 kPa partial pressure at 313 K) passes
    condensed = vap_hot["ACCL"] - vap_cold + vap_hot["ACOH"]
    q6_bound = (
        (vap_hot["ACCL"] - vap_cold) * HVAP["ACCL"]
        + vap_hot["ACOH"] * HVAP["ACOH"]
        + (inert * CP_GAS["HCL"] + sum(vap_hot.values()) * CP_GAS["ACCL"]) * (T_REACT - T_VENT)
    ) / 3600.0

    # duties, kW (kJ/h / 3600)
    s1 = component_flows(streams, "S1")
    s3 = component_flows(streams, "S3")
    q1 = heat_capacity_rate(s1) * (T_REACT - T_AMBIENT) / 3600.0
    n_pcl3 = s3["PCL3"] / MW["PCL3"]
    n_h2o = s1.get("H2O", 0.0) / MW["H2O"]
    extent_hyd = n_h2o / 3.0
    extent_accl = n_pcl3 * (1.0 - kmol(s4).get("PCL3", 0.0) / n_pcl3) - extent_hyd
    released = -(HEAT["ACCL"] * extent_accl + HEAT["HYD"] * extent_hyd)
    dose_heat = heat_capacity_rate(s3) * (T_REACT - T_AMBIENT)
    evaporation = sum(vap_hot[n] * HVAP[n] for n in vap_hot)
    reflux_back = condensed * CP["ACCL"] * (T_REACT - T_VENT)  # the cold condensate rewarmed in R-101
    # R101's duty as core's semi-batch model writes it on Q2 (ADR 0059): a cross-check only
    q2 = (released - dose_heat) / 3600.0
    # R-101's own evaporative cooling, which the model leaves out of Q2 (D-014): the vapour the
    # gas leaving the reacting mass carries, saturated with the upper phase's vapour at 313 K (an
    # upper bound: the HCl forms mostly in the first minutes, over nearly pure acetic acid), and
    # its condensate returned cold from E-103 and rewarmed. The rest of the inert is the batch's
    # nitrogen, which never passes over the reacting mass. Until core 1.9.0 Q2 was typed with all
    # of it deducted (1.27 kW), as if the whole batch's nitrogen swept the reacting mass, and Q6
    # held the same vapour; since then Q6 is taken per source below (D-014)
    displaced = s3["PCL3"] / MW["PCL3"] * MATERIALS["PCL3"]["liquid_molar_volume"]  # m3/h
    gas_displaced = P * displaced / (R_GAS * T_REACT)  # kmol/h, saturated head space
    inert_r101 = n_hcl + gas_displaced * (1.0 - sum(p_hot.values()) / P)
    share_r101 = inert_r101 / inert
    evaporation_r101 = (evaporation + reflux_back) * share_r101

    # E-103's load Q6 per source (D-010, D-014): R-101's gas off the reacting mass (above); the
    # still's and receivers' nitrogen saturated over the product S10 at 303 K; R-101's purge dry,
    # from the ambient. E103 takes each to 268 K, condensing the acetyl chloride down to its
    # vapour pressure there and all the acetic acid; the PCl3 passes
    def e103_load(n_inert: float, vapour: dict[str, float], t_in: float) -> tuple[float, float]:
        """kJ/h E103 removes from one source, and kmol/h of acetyl chloride that passes it."""
        passing = min(vapour.get("ACCL", 0.0), n_inert * p_cold / (P - p_cold))
        latent_e103 = (vapour.get("ACCL", 0.0) - passing) * HVAP["ACCL"] + vapour.get("ACOH", 0.0) * HVAP["ACOH"]
        sensible = (n_inert * CP_GAS["N2"] + sum(vapour.values()) * CP_GAS["ACCL"]) * (t_in - T_VENT)
        return latent_e103 + sensible, passing

    vap_r101 = {n: inert_r101 * p / (P - sum(p_hot.values())) for n, p in p_hot.items()}
    n_still = N2_STILL_NM3_PER_BATCH / 22.414 * batches / hours  # kmol/h
    x10 = {n: v / sum(kmol(s10).values()) for n, v in kmol(s10).items()}
    p_still = {n: x10.get(n, 0.0) * psat(n, T_PRODUCT) for n in ("ACCL", "PCL3", "ACOH")}
    vap_still = {n: n_still * p / (P - sum(p_still.values())) for n, p in p_still.items()}
    n_purge = N2_R101_PURGE_NM3_PER_BATCH / 22.414 * batches / hours  # kmol/h, dry
    load_r101, pass_r101 = e103_load(inert_r101, vap_r101, T_REACT)
    load_still, pass_still = e103_load(n_still, vap_still, T_PRODUCT)
    load_purge, _ = e103_load(n_purge, {}, T_AMBIENT)
    q6 = (load_r101 + load_still + load_purge) / 3600.0
    latent = sum(v / MW[n] * HVAP[n] for n, v in s8.items() if v > 0)
    heat_up = heat_capacity_rate(s6) * (t_still0 - T_REACT) + c9 * (t_still1 - t_still0)
    q3 = latent / 3600.0  # the still's net boil-up: core's still model writes it (ADR 0059)
    q7 = REFLUX * latent / 3600.0  # the boil-up the column returns as reflux (D-009)
    q8 = heat_up / 3600.0  # the charge to its bubble point, the residue to its end (D-009)
    subcool = heat_capacity_rate(s10) * (t_still0 - T_PRODUCT)
    q4 = ((1.0 + REFLUX) * latent + subcool) / 3600.0
    q5 = (c9 + c11) * (t12 - T_PRODUCT) / 3600.0

    # the vent fraction of the acetyl chloride R101 forms that leaves past E103 (R101's
    # batch.vent fraction in the flowsheet, written by hand from this value): an upper bound, all
    # of E-103's inert saturated at 268 K, R-101's dry purge too; per source (the purge carries
    # no vapour) it is lower, printed beside it and not used (D-010)
    vent_fraction = vap_cold / (3.0 * extent_accl)
    vent_fraction_per_source = (pass_r101 + pass_still) / (3.0 * extent_accl)

    # the scrubber: the vented acetyl chloride hydrolysed (AHYD), water for a 1 wt% HCl bleed,
    # adiabatic outlet temperature
    s14 = component_flows(streams, "S14")
    n_accl_vent = s14.get("ACCL", 0.0) / MW["ACCL"]
    n_hcl_liquor = s14.get("HCL", 0.0) / MW["HCL"] + n_accl_vent
    water = n_hcl_liquor * MW["HCL"] / HCL_LIQUOR - sum(s14.values())
    liquor = water + sum(s14.values())
    gas_cp = s14.get("HCL", 0.0) / MW["HCL"] * CP_GAS["HCL"] + n_accl_vent * CP_GAS["ACCL"]
    t16 = T_AMBIENT + (
        n_accl_vent * -HEAT["AHYD"] + n_hcl_liquor * ABSORPTION + gas_cp * (T_VENT - T_AMBIENT)
    ) / (liquor * CP_ACID)

    yield_acid = (s10["ACCL"] / MW["ACCL"]) / (s1["ACOH"] / MW["ACOH"])
    print(f"product S10 {product:.4f} kg/h at the current feeds; target {CAPACITY:.4f} kg/h")
    print(f"feeds for {CAPACITY * 7.92:.0f} t/a: S3 PCl3 {pcl3:.4f}, S1 acetic acid {acid:.4f} kg/h")
    print(f"S6 upper {sum(s6.values()):.4f} kg/h, S7 lower {sum(s7.values()):.4f} kg/h: {fractions(s7)}")
    print(f"S10 {product:.4f} kg/h, ACCL {s10['ACCL'] / product:.6f} by mass, PCl3 {s10.get('PCL3', 0) / product * 1e6:.0f} ppm; S11 {sum(s11.values()):.4f} kg/h")
    print(f"yield on acetic acid {yield_acid:.4%} (1 mol acetyl chloride per mol)")
    print(f"still: first bubble point {t_still0:.2f} K, last {t_still1:.2f} K; S12 {t12:.2f} K")
    print(f"vent: HCl {n_hcl:.6f}, N2 {n_n2:.6f}, vapour at 313 K {sum(vap_hot.values()):.6f} kmol/h, acetyl chloride past E103 {vap_cold:.6f} kmol/h ({vap_cold * MW['ACCL']:.4f} kg/h), vent fraction {vent_fraction:.6f} of what R101 forms; PCl3 past E103 {vap_hot['PCL3']:.6f} kmol/h")
    print(f"vent per source: R-101's gas {inert_r101:.6f}, the still's and receivers' N2 {n_still:.6f}, R-101's dry purge {n_purge:.6f} kmol/h; acetyl chloride into E103 {vap_r101['ACCL'] + vap_still['ACCL']:.6f} (upper bound {vap_hot['ACCL']:.6f}), past E103 {pass_r101 + pass_still:.6f} kmol/h, vent fraction {vent_fraction_per_source:.6f} (not used: the flowsheet keeps the upper bound {vent_fraction:.6f})")
    print(f"Q6 per source {q6:.4f} kW: R-101's gas {load_r101 / 3600:.4f}, the still's and receivers' N2 {load_still / 3600:.4f}, R-101's dry purge {load_purge / 3600:.4f}; the upper bound with all the inert saturated at 313 K {q6_bound:.4f} kW")
    print(f"S15 scrubber water {water:.4f} kg/h; S16 {t16:.2f} K")
    print(f"Q1 {q1:.4f}, Q4 {q4:.4f}, Q5 {q5:.4f}, Q6 {q6:.4f}, Q7 reboiler for the reflux {q7:.4f}, Q8 still heat-up {q8:.4f} kW")
    print(f"cross-check of the model duties propagate writes: Q2 R101 {q2:.4f} (released {released / 3600:.4f}, dose {dose_heat / 3600:.4f}), Q3 still net boil-up {q3:.4f} kW; reboiler Q3 + Q7 + Q8 {q3 + q7 + q8:.4f} kW")
    print(f"R-101's own evaporative cooling (not in Q2, upper bound): gas off the reacting mass {inert_r101:.6f} kmol/h ({share_r101:.4f} of E-103's inert), net {evaporation_r101 / 3600:.4f} kW ({evaporation_r101 / 3600 / q2:.2%} of Q2); E-103's whole vapour with its condensate rewarmed {(evaporation + reflux_back) / 3600:.4f} kW (the 1.8.0 hand Q2 deducted it all: {q2 - (evaporation + reflux_back) / 3600:.4f} kW)")

    write_balance_output(
        {
            "design": {
                "S1": {"flow": round(acid, 4)},
                "S3": {"flow": round(pcl3, 4)},
                "S6": {"flow": round(sum(s6.values()), 4), "composition": fractions(s6)},
                "S7": {"flow": round(sum(s7.values()), 4), "composition": fractions(s7)},
                "S8": {"temperature": round(t_still0, 2)},
                "S9": {"temperature": round(t_still1, 2)},
                "S10": {"flow": round(product, 4), "composition": fractions(s10)},
                "S11": {"flow": round(sum(s11.values()), 5), "composition": fractions(s11), "temperature": round(t_return, 2)},
                "S12": {"temperature": round(t12, 2)},
                "S15": {"flow": round(water, 4)},
                "S16": {"temperature": round(t16, 2)},
                "Q1": {"duty": round(q1, 4)},
                "Q4": {"duty": round(q4, 4)},
                "Q5": {"duty": round(q5, 4)},
                "Q6": {"duty": round(q6, 4)},
                "Q7": {"duty": round(q7, 4)},
                "Q8": {"duty": round(q8, 4)},
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
