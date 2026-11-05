"""What core cannot calculate in the benzyl bromide plant (DESIGN.md D-006).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
charge mixer, the semi-batch R101 with its HBr vent, the stills ST101 and ST102 (one Rayleigh
stage each), the absorber and the recycle mixer and splitter from process/flowsheet.yaml. This
script gives what core has no model for, from the streams propagate wrote and the component
data of process/materials.yaml:

- the feeds that make 1000 t/a of distilled benzyl bromide (core propagates from the feeds and
  does not solve them for a product rate; the balance is linear in the feeds, so the bromine is
  scaled by the ratio of the target to the product S15), and the toluene make-up S1 that keeps
  4 mol of toluene in the charge per mol of bromine;
- the recycle S2 at its fixed point: 0.98 of the recovered toluene S17 (core does not tear a
  recycle; the script and propagate are run in turn until S2 no longer moves);
- the absorber water S10 for 48 wt% acid;
- the temperatures that follow from mixing (S3, S17) or from a bubble point (S13), and the
  duties Q1 to Q11 and the lamps' power P1 (no property package of core covers these liquids).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With BALANCE_OUTPUT
set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

CAPACITY = 1_000_000.0 / 7920.0  # kg/h of distilled benzyl bromide: 1000 t/a in 7920 h (D-002)
RATIO = 4.0  # mol of toluene in R-101's charge per mol of bromine dosed (D-004)
PURGE = 0.02  # share of the recovered toluene S17 purged to incineration (D-007)
HBR_ACID = 0.48  # mass fraction of HBr in the hydrobromic acid (D-008)
# kJ/kmol of HBr from gas to 48 wt% acid: the integral heat of solution at 4.87 mol of water per
# mol, -72.0 kJ/mol, ASSUMED in hydrogen-bromide-1 (its DESIGN.md D-009, from the infinite-
# dilution -85.14 kJ/mol of NSRDS-NBS 2) (D-008)
SOLUTION = 72_000.0
CPG_HBR = 29.1  # kJ/(kmol K), HBr ideal gas at 298 K (CRC table in chemicals 1.5.2, SRC-4)
CPG_TOL = 115.0  # kJ/(kmol K), toluene vapour near 330 K, ASSUMED order (D-009)
P_ATM = 101.325  # kPa
T_SUPPLY = 298.15  # K, feeds from storage, process water (design basis)
T_REACT = 363.15  # K, R101 (D-005)
T_CW = 303.15  # K, condensates and the reflux condenser's gas outlet on cooling water (D-007, D-008)
T_VENT = 268.15  # K, the vent condenser's gas outlet and the forerun on brine (D-007, D-008)
T_ACID = 313.15  # K, the acid leaving the absorber (D-008)
T_RESIDUE = 333.15  # K, the residue cooled in C-101 before draining (D-007)
P_STRIP, P_VAC = 15.0, 2.0  # kPa(a), the stills ST101 and ST102 (flowsheet.yaml, D-007)
HEATUP_LOSSES = 0.10  # share of the charge's heat-up lost (D-009)
# The lamps (D-005): electricity installed in R-101's lamp wells, the share of it emitted as
# light (LED wall-plug efficiency, ASSUMED), all of the light absorbed by the content
P_LAMP = 20.0  # kW
LIGHT_SHARE = 0.30
QUANTUM_YIELD = 20.0  # mol of bromine reacted per mol of photons absorbed, ASSUMED (D-005)
PHOTON = 6.02214076e23 * 6.62607015e-34 * 2.99792458e8 / 420e-9 / 1000.0  # kJ/mol at 420 nm
# s of light per batch: the dosing and the post-reaction of R101 (cheme process reactors:
# 18000 s dosing, 891.8 s more to 0.999 conversion of the bromine)
LIGHT_S = 18_891.8
R101_AGITATOR = 3.0  # kW while R-101 is occupied; R-101 is the bottleneck (D-003)
STILL_POWER = 1.5 + 4.0  # kW, still agitator and dry vacuum pump while C-101 distils (D-009)


def load() -> tuple[dict, dict, dict]:
    sheet = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    materials = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text(encoding="utf-8"))
    recipe = yaml.safe_load((ROOT / "process" / "recipe.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in materials["components"]}
    return {s["id"]: s for s in sheet["streams"]}, comps, recipe


def state(streams: dict, sid: str) -> dict:
    return streams[sid]["state"]["design"]


def kmol(streams: dict, comps: dict, sid: str) -> dict[str, float]:
    """kmol/h of each component of a material stream (flow kg/h; mole or mass fractions)."""
    s = state(streams, sid)
    comp, flow = s["composition"], s["flow"]["value"]
    mm = {n: comps[n]["molar_mass"] for n in comp["values"]}
    if comp["basis"] == "mass_fraction":
        return {n: flow * x / mm[n] for n, x in comp["values"].items()}
    mean = sum(x * mm[n] for n, x in comp["values"].items())
    return {n: flow / mean * x for n, x in comp["values"].items()}


def kg(comps: dict, moles: dict[str, float]) -> dict[str, float]:
    return {n: v * comps[n]["molar_mass"] for n, v in moles.items()}


def mass_fractions(comps: dict, moles: dict[str, float]) -> dict[str, float]:
    masses = {n: v for n, v in kg(comps, moles).items() if v > 0}
    total = sum(masses.values())
    return {n: round(v / total, 9) for n, v in masses.items()}


def mcp(comps: dict, moles: dict[str, float]) -> float:
    """kJ/(K h): the liquid heat capacity flow."""
    return sum(n * comps[k]["liquid_heat_capacity"] for k, n in moles.items() if n)


def latent(comps: dict, moles: dict[str, float]) -> float:
    """kJ/h: the moles boiled up times their heats of vaporization (the stills' energy)."""
    return sum(n * comps[k]["heat_of_vaporization"] for k, n in moles.items() if n)


def p_sat(comps: dict, name: str, t: float) -> float:
    """kPa, the component's Antoine vapour pressure (NIST form, bar)."""
    vp = comps[name]["vapour_pressure"]
    return 100.0 * 10 ** (vp["a"] - vp["b"] / (t + vp["c"]))


def x_of(moles: dict[str, float]) -> dict[str, float]:
    total = sum(v for k, v in moles.items() if k != "HBR")
    return {k: v / total for k, v in moles.items() if k != "HBR" and v > 0}


def p_liquid(comps: dict, moles: dict[str, float], t: float) -> float:
    """kPa: the liquid's total vapour pressure (Raoult)."""
    return sum(x * p_sat(comps, k, t) for k, x in x_of(moles).items())


def bubble(comps: dict, moles: dict[str, float], p: float) -> float:
    """K: the bubble point at p kPa (Raoult, as the stills), by bisection."""
    lo, hi = 250.0, 600.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if p_liquid(comps, moles, mid) < p else (lo, mid)
    return 0.5 * (lo + hi)


def mix_temperature(comps: dict, parts: list[tuple[dict[str, float], float]]) -> float:
    """K: adiabatic mixing of liquids from their heat capacity flows."""
    return sum(mcp(comps, m) * t for m, t in parts) / sum(mcp(comps, m) for m, _ in parts)


def main() -> None:
    streams, comps, recipe = load()
    mm = {n: c["molar_mass"] for n, c in comps.items()}
    temp = {sid: state(streams, sid).get("temperature", {}).get("value") for sid in streams}

    s15 = kmol(streams, comps, "S15")
    product = sum(kg(comps, s15).values())

    # the feeds that make CAPACITY: the bromine scaled (linear), the toluene to RATIO
    br2 = state(streams, "S5")["flow"]["value"] * CAPACITY / product
    n_br2 = br2 / mm["BR2"]
    s17 = kmol(streams, comps, "S17")
    s2 = {k: (1.0 - PURGE) * v for k, v in s17.items() if v > 0}
    # the recycle scales with the feeds: the next pass's recycle at the scaled bromine
    scale = CAPACITY / product
    s2 = {k: v * scale for k, v in s2.items()}
    toluene = (RATIO * n_br2 - s2.get("TOL", 0.0)) * mm["TOL"]

    # the absorber water for 48 wt% acid
    s9 = kmol(streams, comps, "S9")
    hbr = s9["HBR"] * mm["HBR"]
    water = hbr * (1.0 - HBR_ACID) / HBR_ACID

    # temperatures that follow from mixing and bubble points
    s1 = {"TOL": toluene / mm["TOL"]}
    t3 = mix_temperature(comps, [(s1, T_SUPPLY), (s2, temp["S17"])])
    s12, s14 = kmol(streams, comps, "S12"), kmol(streams, comps, "S14")
    t17 = mix_temperature(comps, [(s12, T_CW), (s14, T_VENT)])
    s6, s13, s16 = (kmol(streams, comps, s) for s in ("S6", "S13", "S16"))
    t6_strip = bubble(comps, s6, P_STRIP)  # ST101's first bubble point
    t13 = bubble(comps, s13, P_STRIP)  # ST101's end, the residue S13
    t13_vac = bubble(comps, s13, P_VAC)  # ST102's first bubble point
    t15 = bubble(comps, s15, P_VAC)  # the main cut condensing
    t16 = bubble(comps, s16, P_VAC)  # ST102's end
    t14 = bubble(comps, s14, P_VAC)  # the forerun condensing (its bubble point, the lower bound)
    t12 = bubble(comps, s12, P_STRIP)

    # duties, kW (kJ/h / 3600), of the streams as propagate wrote them
    s3 = kmol(streams, comps, "S3")
    q1 = mcp(comps, s3) * (T_REACT - t3) / (1.0 - HEATUP_LOSSES) / 3600.0
    s4, s5, s7 = (kmol(streams, comps, s) for s in ("S4", "S5", "S7"))
    n_hbr = s7["HBR"]  # kmol/h: one per extent of BNBR and BALBR
    # the extents: BALBR from the benzal bromide formed, BNBR the rest of the HBr (one each)
    dh = {r["id"]: r["heat_of_reaction"]["value"] for r in reactions()}
    e2 = s6.get("BALBR", 0.0) - s4.get("BALBR", 0.0)
    e1 = n_hbr - e2
    rxn = -(e1 * dh["BNBR"] + e2 * dh["BALBR"])
    batches = state(streams, "S15")["flow"]["value"] * recipe["hours_per_year"]["value"] / recipe["batch_size"]["value"]
    light_h = LIGHT_S / 3600.0 * batches / recipe["hours_per_year"]["value"]  # share of the year lit
    p1 = P_LAMP * light_h
    light = LIGHT_SHARE * p1  # kW absorbed by the content
    q3 = (1.0 - LIGHT_SHARE) * p1  # kW to the lamp wells' cooling water
    # the organics the HBr carries out of R-101 at 363 K (Raoult on the liquid at the start and
    # at the end, their mean, ASSUMED), condensed in E-102 down to toluene's vapour pressure at
    # 303 K and in E-103 down to 268 K; the condensate returns to R-101
    def carried(moles: dict[str, float]) -> float:
        p = p_liquid(comps, moles, T_REACT)
        return p / (P_ATM - p)

    r_out = 0.5 * (carried(s4) + carried(s6))
    r_cw = p_sat(comps, "TOL", T_CW) / (P_ATM - p_sat(comps, "TOL", T_CW))
    r_vent = p_sat(comps, "TOL", T_VENT) / (P_ATM - p_sat(comps, "TOL", T_VENT))
    lam, cp = comps["TOL"]["heat_of_vaporization"], comps["TOL"]["liquid_heat_capacity"]
    evaporated = n_hbr * r_out * lam + n_hbr * (r_out - r_cw) * cp * (T_REACT - T_CW) + n_hbr * (
        r_cw - r_vent
    ) * cp * (T_REACT - T_VENT)
    warm_br2 = mcp(comps, s5) * (T_REACT - T_SUPPLY)
    # the agitator's power ends as heat in the content, as the absorbed light does
    q2 = (rxn - warm_br2 - evaporated) / 3600.0 + light + R101_AGITATOR
    q4 = (
        n_hbr * (r_out - r_cw) * (lam + cp * (T_REACT - T_CW))
        + n_hbr * r_cw * CPG_TOL * (T_REACT - T_CW)
        + n_hbr * CPG_HBR * (T_REACT - T_CW)
    ) / 3600.0
    q5 = (
        n_hbr * (r_cw - r_vent) * (lam + cp * (T_CW - T_VENT))
        + n_hbr * r_vent * CPG_TOL * (T_CW - T_VENT)
        + n_hbr * CPG_HBR * (T_CW - T_VENT)
    ) / 3600.0
    q6 = (
        s9["HBR"] * SOLUTION
        - s9["HBR"] * CPG_HBR * (T_ACID - T_VENT)
        - water / mm["H2O"] * comps["H2O"]["liquid_heat_capacity"] * (T_ACID - T_SUPPLY)
    ) / 3600.0
    # the stills: latent heat of what is boiled up, less the sensible heat a charge brings above
    # its first bubble point (it flashes as the still is evacuated); condensers to the receivers
    q7 = (latent(comps, s12) - mcp(comps, s6) * max(T_REACT - t6_strip, 0.0)) / 3600.0
    q8 = (latent(comps, s12) + mcp(comps, s12) * (t12 - T_CW)) / 3600.0
    q9 = (latent(comps, s14) + latent(comps, s15) - mcp(comps, s13) * (t13 - t13_vac)) / 3600.0
    q10 = (latent(comps, s14) + mcp(comps, s14) * (t14 - T_VENT)) / 3600.0
    q11 = (
        latent(comps, s15) + mcp(comps, s15) * (t15 - T_CW) + mcp(comps, s16) * (t16 - T_RESIDUE)
    ) / 3600.0
    p2 = R101_AGITATOR
    still_h = STILL_HOURS * batches / recipe["hours_per_year"]["value"]
    p3 = STILL_POWER * still_h

    # photon budget of the dosing (D-005)
    dosed = n_br2 * recipe["hours_per_year"]["value"] / batches / 18000.0  # kmol/s while dosing
    needed = dosed * 1000.0 / QUANTUM_YIELD * PHOTON  # kW of light absorbed
    yield_br2 = s15["BNBR"] / n_br2
    print(f"product S15 {product:.4f} kg/h at the current feeds; target {CAPACITY:.4f} kg/h")
    print(f"feeds: S5 bromine {br2:.4f}, S1 toluene {toluene:.4f}, S2 recycle {sum(kg(comps, s2).values()):.4f} kg/h")
    print(f"S10 absorber water {water:.4f} kg/h for {hbr:.4f} kg/h HBr")
    print(f"T: S3 {t3:.2f}, S17 {t17:.2f}, S13 {t13:.2f}; still bubble points {t6_strip:.2f} (S6 at {P_STRIP} kPa), {t13_vac:.2f} (S13 at {P_VAC} kPa), S15 {t15:.2f}, S16 {t16:.2f}, S14 {t14:.2f}, S12 {t12:.2f}")
    print(f"organics carried per HBr {r_out:.3f} (start {carried(s4):.3f}, end {carried(s6):.3f}), past E-102 {r_cw:.4f}, past E-103 {r_vent:.5f}")
    print(f"light needed {needed:.2f} kW at quantum yield {QUANTUM_YIELD}; emitted {LIGHT_SHARE * P_LAMP:.2f} kW")
    print(f"yield of S15's benzyl bromide on the bromine {yield_br2:.4%}")
    print(f"Q1 {q1:.3f} Q2 {q2:.3f} Q3 {q3:.3f} Q4 {q4:.3f} Q5 {q5:.3f} Q6 {q6:.3f} Q7 {q7:.3f} Q8 {q8:.3f} Q9 {q9:.3f} Q10 {q10:.3f} Q11 {q11:.3f}; P1 {p1:.3f} P2 {p2:.3f} P3 {p3:.3f} kW")

    write_balance_output(
        {
            "design": {
                "S1": {"flow": round(toluene, 4)},
                "S2": {"flow": round(sum(kg(comps, s2).values()), 4), "composition": mass_fractions(comps, s2), "temperature": round(t17, 2)},
                "S3": {"temperature": round(t3, 2)},
                "S5": {"flow": round(br2, 4)},
                "S10": {"flow": round(water, 4)},
                "S13": {"temperature": round(t13, 2)},
                "S17": {"temperature": round(t17, 2)},
                "S18": {"temperature": round(t17, 2)},
                "Q1": {"duty": round(q1, 4)},
                "Q2": {"duty": round(q2, 4)},
                "Q3": {"duty": round(q3, 4)},
                "Q4": {"duty": round(q4, 4)},
                "Q5": {"duty": round(q5, 4)},
                "Q6": {"duty": round(q6, 4)},
                "Q7": {"duty": round(q7, 4)},
                "Q8": {"duty": round(q8, 4)},
                "Q9": {"duty": round(q9, 4)},
                "Q10": {"duty": round(q10, 4)},
                "Q11": {"duty": round(q11, 4)},
                "P1": {"duty": round(p1, 4)},
                "P3": {"duty": round(p3, 4)},
            }
        }
    )


# h of distillation per batch in C-101: ST101's and ST102's boil-up times (cheme process stills)
STILL_HOURS = 1.153 + 1.201


def reactions() -> list[dict]:
    doc = yaml.safe_load((ROOT / "process" / "reactions.yaml").read_text(encoding="utf-8"))
    return doc["reactions"]


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import json
    import os

    cases = {c: {k: v for k, v in s.items() if v} for c, s in cases.items()}
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
