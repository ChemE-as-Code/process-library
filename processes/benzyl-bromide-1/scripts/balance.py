"""What core cannot calculate in the benzyl bromide plant (DESIGN.md D-006).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
charge mixer, the semi-batch R101 with its HBr vent, the vapour the HBr carries and R101's vent
condenser E-102 (core 1.10.0, ADR 0062), the strip ST101 (one Rayleigh stage), the forerun ST102
and the main cut ST103 through C-101's column (Diwekar's shortcut, ADR 0061), the absorber and
the recycle mixer and splitter from process/flowsheet.yaml; it converges the toluene recycle S2
at its tear (ADR 0060) and writes the model duties: E-102's Q4, the stills' steam Q7, Q9 and Q14
and the column's condensers Q10 and Q11 (ADR 0059, 0061, 0062). This script gives what core has
no model for, from the streams propagate wrote and the component data of process/materials.yaml:

- the feeds that make 1000 t/a of distilled benzyl bromide (core propagates from the feeds and
  does not solve them for a product rate; the balance is linear in the feeds, so the bromine is
  scaled by the ratio of the target to the product S15), and the toluene make-up S1 that keeps
  4 mol of toluene in the charge per mol of bromine, the recycle S2's toluene counted;
- E-103, the brine vent condenser after E-102: one flash of the vent gas S7 at 268.15 K (the HBr
  an inert, Raoult over an ideal condensate, as core's vent condenser), its gas S9 to the
  absorber and its condensate S19 to T-201, and its duty Q5 (core's vent has one condenser);
- the absorber water S10 for 48 wt% acid;
- the temperatures that follow from mixing (S3, S17) or from a bubble point (S13, S20);
- the duties core's models leave out: Q1 (the charge's heat-up), Q2 (R-101's jacket: the light
  and the agitator's heat less the heat R101's model takes in), Q3 (the lamp wells), the strip's
  condenser Q8, the forerun cooler Q16, the product cooler and the residue's cool-down Q15, the
  absorber Q6, and the lamps' power P1 (no property package of core covers these liquids);
- as a cross-check only: its own value of R101's model duty and of the stills' and the column's
  duties, and the stills' sensible heat (the charge, the cuts and the residue, which core's
  still leaves out, D-009).

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
HBR_ACID = 0.48  # mass fraction of HBr in the hydrobromic acid (D-008)
# kJ/kmol of HBr from gas to 48 wt% acid: the integral heat of solution at 4.87 mol of water per
# mol, -72.0 kJ/mol, ASSUMED in hydrogen-bromide-1 (its DESIGN.md D-009, from the infinite-
# dilution -85.14 kJ/mol of NSRDS-NBS 2) (D-008)
SOLUTION = 72_000.0
P_ATM = 101.325  # kPa
T_SUPPLY = 298.15  # K, feeds from storage, process water (design basis)
T_REACT = 363.15  # K, R101 (D-005)
T_CW = 303.15  # K, condensates and E-102's gas outlet on cooling water (D-007, D-008)
T_VENT = 268.15  # K, E-103's gas outlet and the forerun on brine (D-007, D-008)
T_ACID = 313.15  # K, the acid leaving the absorber (D-008)
T_RESIDUE = 333.15  # K, the residue cooled in C-101 before draining (D-007)
P_STRIP, P_VAC = 15.0, 2.0  # kPa(a), the stills ST101, ST102 and ST103 (flowsheet.yaml, D-007)
HEATUP_LOSSES = 0.10  # share of the charge's heat-up lost (D-009)
# The lamps (D-005): electricity installed in R-101's lamp wells, the share of it emitted as
# light (LED wall-plug efficiency, ASSUMED), all of the light absorbed by the content
P_LAMP = 20.0  # kW
LIGHT_SHARE = 0.30
QUANTUM_YIELD = 20.0  # mol of bromine reacted per mol of photons absorbed, ASSUMED (D-005)
PHOTON = 6.02214076e23 * 6.62607015e-34 * 2.99792458e8 / 420e-9 / 1000.0  # kJ/mol at 420 nm
# s of light per batch: the dosing and the post-reaction of R101 (cheme process reactors:
# 18000 s dosing, 851.4 s more to 0.999 conversion of the bromine)
LIGHT_S = 18_851.4
R101_AGITATOR = 3.0  # kW while R-101 is occupied; R-101 is the bottleneck (D-003)
STILL_POWER = 1.5 + 4.0  # kW, still agitator and dry vacuum pump while C-101 distils (D-009)
# h of distillation per batch in C-101: ST101's, ST102's and ST103's boil-up times (cheme
# process stills)
STILL_HOURS = 1.129 + 0.444 + 1.301


def load() -> tuple[dict, dict, dict]:
    sheet = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    materials = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text(encoding="utf-8"))
    recipe = yaml.safe_load((ROOT / "process" / "recipe.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in materials["components"]}
    return {s["id"]: s for s in sheet["streams"]}, comps, recipe


def steps() -> dict:
    sheet = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    return {s["id"]: s for s in sheet["steps"]}


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


def mole_fractions(moles: dict[str, float]) -> dict[str, float]:
    total = sum(moles.values())
    return {n: round(v / total, 9) for n, v in moles.items() if v > 0}


def mcp(comps: dict, moles: dict[str, float]) -> float:
    """kJ/(K h): the liquid heat capacity flow (HBr left out: a gas, no liquid data)."""
    return sum(n * comps[k]["liquid_heat_capacity"] for k, n in moles.items() if n and k != "HBR")


def latent(comps: dict, moles: dict[str, float]) -> float:
    """kJ/h: the moles boiled up times their heats of vaporization (the stills' energy)."""
    return sum(n * comps[k]["heat_of_vaporization"] for k, n in moles.items() if n and k != "HBR")


def cp_gas(comps: dict, name: str, t: float) -> float:
    """kJ/(kmol K): the ideal-gas heat capacity of materials.yaml (HBr)."""
    a = comps[name]["ideal_gas"]["cp_R"]
    return 8.314462618 * sum(c * t**k for k, c in enumerate(a))


def h_gas(comps: dict, name: str, t_hot: float, t_cold: float, steps: int = 50) -> float:
    """kJ/kmol: the ideal gas cooled from t_hot to t_cold."""
    dt = (t_hot - t_cold) / steps
    return sum(cp_gas(comps, name, t_cold + (i + 0.5) * dt) for i in range(steps)) * dt


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


def flash(comps: dict, gas: dict[str, float], t: float, p: float) -> tuple[dict, dict]:
    """A partial condenser at t K and p kPa: the HBr an inert, the rest by Raoult over an ideal
    condensate (core's vent condenser, ADR 0062). Returns (gas out, condensate), kmol/h."""
    inert = gas.get("HBR", 0.0)
    cond = {k: v for k, v in gas.items() if k != "HBR" and v > 0}
    k_val = {k: p_sat(comps, k, t) / p for k in cond}
    feed = inert + sum(cond.values())

    def x_sum(v: float) -> float:
        # V kmol/h of gas out, L = feed - V of condensate: x = n / (L + V K), rising with V
        return sum(n / (feed - v + v * k_val[k]) for k, n in cond.items())

    if x_sum(feed) <= 1.0:  # above the dew point: nothing condenses
        return dict(gas), {k: 0.0 for k in cond}
    lo, hi = inert, feed
    for _ in range(200):
        v = 0.5 * (lo + hi)
        lo, hi = (lo, v) if x_sum(v) > 1.0 else (v, hi)
    v = 0.5 * (lo + hi)
    lt = feed - v
    liq = {k: n * lt / (lt + v * k_val[k]) for k, n in cond.items()}
    out = {k: n - liq[k] for k, n in cond.items()}
    out["HBR"] = inert
    return out, liq


def rayleigh(comps: dict, moles: dict[str, float], p: float, cuts: list) -> dict:
    """One Rayleigh stage on Raoult's law at p kPa, as core's still (ADR 0055): the charge
    `moles` (kmol/h) boiled until each cut's end `(name, stop(x))` in turn. Per cut its moles
    and the heat-capacity flow times the pot's temperature at which each part left (kJ/h), the
    pot's first and last temperature."""
    n = {k: v for k, v in moles.items() if v > 0 and k != "HBR"}
    step = 2e-4 * sum(n.values())
    out: dict = {"start": bubble(comps, n, p)}
    for name, stop in cuts:
        cut = {"moles": {k: 0.0 for k in n}, "cpT": 0.0}
        while True:
            total = sum(n.values())
            x = {k: v / total for k, v in n.items()}
            if stop(x):
                break
            t = bubble(comps, n, p)
            ps = {k: x[k] * p_sat(comps, k, t) for k in n}
            y = {k: v / sum(ps.values()) for k, v in ps.items()}
            d = min(step, 2e-3 * total)
            for k in n:
                n[k] = max(n[k] - d * y[k], 0.0)
                cut["moles"][k] += d * y[k]
            cut["cpT"] += d * sum(y[k] * comps[k]["liquid_heat_capacity"] for k in y) * t
        out[name] = cut
    out["residue"] = n
    out["end"] = bubble(comps, n, p)
    return out


def condenser(comps: dict, cut: dict, t_receiver: float) -> float:
    """kJ/h: a cut's vapour condensed from the pot's temperature and cooled to its receiver."""
    return latent(comps, cut["moles"]) + cut["cpT"] - mcp(comps, cut["moles"]) * t_receiver


def sensible(comps: dict, still: dict, t_charge: float) -> float:
    """kJ/h: the one-stage still's heat beyond the latent heat of its boil-up, from a charge at
    t_charge: each cut's vapour leaving at the pot's temperature and the residue at the end,
    against the charge (liquid heat capacities, the latent heats constant)."""
    cuts = [v for k, v in still.items() if isinstance(v, dict) and "cpT" in v]
    leaving = sum(c["cpT"] - mcp(comps, c["moles"]) * t_charge for c in cuts)
    return leaving + mcp(comps, still["residue"]) * (still["end"] - t_charge)


def reactions() -> list[dict]:
    doc = yaml.safe_load((ROOT / "process" / "reactions.yaml").read_text(encoding="utf-8"))
    return doc["reactions"]


def main() -> dict:
    streams, comps, recipe = load()
    mm = {n: c["molar_mass"] for n, c in comps.items()}
    temp = {sid: state(streams, sid).get("temperature", {}).get("value") for sid in streams}
    nodes = steps()
    reflux = {s: nodes[s]["still"]["column"]["ratio"] for s in ("ST102", "ST103")}

    s15 = kmol(streams, comps, "S15")
    product = sum(kg(comps, s15).values())

    # the feeds that make CAPACITY: the bromine scaled (linear), the toluene to RATIO
    br2 = state(streams, "S5")["flow"]["value"] * CAPACITY / product
    n_br2 = br2 / mm["BR2"]
    # E-103: the vent gas S7 past E-102 (at 303.15 K, core's vent condenser) flashed at 268.15 K
    s7 = kmol(streams, comps, "S7")
    t7 = temp["S7"]
    s9, s19 = flash(comps, s7, T_VENT, P_ATM)
    q5 = (
        latent(comps, s19)
        + mcp(comps, s7) * (t7 - T_VENT)
        + s7["HBR"] * h_gas(comps, "HBR", t7, T_VENT)
    ) / 3600.0

    # the toluene make-up for RATIO. propagate converges the recycle S2 at its tear for the
    # current feeds (ADR 0060). The make-up S1 is what the charge's toluene needs beyond the
    # recycle. The recycle is the splitter's share of what T-201 receives: the stills' toluene,
    # a share of the crude S6's (from the converged loop), and E-103's condensate S19; S6's
    # toluene is the charge's less what the reactions and the vent take, both scaled with the
    # bromine. Taking S2 as given instead would move the make-up 49 times the change it makes
    # (the purge is 2 %).
    scale = CAPACITY / product
    split = nodes["SP201"]["split"]["rec"]
    s3, s6 = kmol(streams, comps, "S3"), kmol(streams, comps, "S6")
    s12, s14 = kmol(streams, comps, "S12"), kmol(streams, comps, "S14")
    recovered = (s12["TOL"] + s14["TOL"]) / s6["TOL"]  # the stills' share of the crude's toluene
    charge_tol = RATIO * n_br2
    consumed = (s3["TOL"] - s6["TOL"]) * scale
    recycled_tol = split * (recovered * (charge_tol - consumed) + s19.get("TOL", 0.0) * scale)
    toluene = (charge_tol - recycled_tol) * mm["TOL"]
    s2_now = kmol(streams, comps, "S2")
    s2 = {k: v * recycled_tol / s2_now["TOL"] for k, v in s2_now.items() if v > 0}

    # the absorber water for 48 wt% acid
    hbr = s9["HBR"] * mm["HBR"]
    water = hbr * (1.0 - HBR_ACID) / HBR_ACID

    # temperatures that follow from mixing and bubble points
    s1 = {"TOL": toluene / mm["TOL"]}
    t3 = mix_temperature(comps, [(s1, T_SUPPLY), (s2, temp["S17"])])
    t17 = mix_temperature(comps, [(s12, T_CW), (s14, T_VENT), (s19, T_VENT)])
    s13, s20, s16 = (kmol(streams, comps, s) for s in ("S13", "S20", "S16"))
    t13 = bubble(comps, s13, P_STRIP)  # ST101's end, the residue S13
    t20 = bubble(comps, s20, P_VAC)  # ST102's end, the pot after the forerun
    t16 = bubble(comps, s16, P_VAC)  # ST103's end, the residue
    # the strip again, one Rayleigh stage as core's (Raoult, the same data), to follow the pot's
    # temperature at which each part of the vapour leaves: its condenser and its sensible heat
    strip = rayleigh(comps, s6, P_STRIP, [("top", lambda x: x.get("TOL", 0.0) <= 0.15)])

    # duties, kW (kJ/h / 3600), of the streams as propagate wrote them
    s3 = kmol(streams, comps, "S3")
    q1 = mcp(comps, s3) * (T_REACT - t3) / (1.0 - HEATUP_LOSSES) / 3600.0
    s4, s5 = (kmol(streams, comps, s) for s in ("S4", "S5"))
    # the extents: BALBR from the benzal bromide formed, BNBR the rest of the HBr (one each);
    # the vent takes some of the benzyl and benzal bromide's vapour past E-102 (a trace)
    dh = {r["id"]: r["heat_of_reaction"]["value"] for r in reactions()}
    n_hbr = s7["HBR"]
    e2 = s6.get("BALBR", 0.0) + s7.get("BALBR", 0.0) - s4.get("BALBR", 0.0)
    e1 = n_hbr - e2
    rxn = -(e1 * dh["BNBR"] + e2 * dh["BALBR"])
    batches = state(streams, "S15")["flow"]["value"] * recipe["hours_per_year"]["value"] / recipe["batch_size"]["value"]
    light_h = LIGHT_S / 3600.0 * batches / recipe["hours_per_year"]["value"]  # share of the year lit
    p1 = P_LAMP * light_h
    light = LIGHT_SHARE * p1  # kW absorbed by the content
    q3 = (1.0 - LIGHT_SHARE) * p1  # kW to the lamp wells' cooling water
    warm_br2 = mcp(comps, s5) * (T_REACT - T_SUPPLY)
    # R-101's heat (D-009). Core's model (ADR 0059, 0062): the reactions' heat less the
    # bromine's warming, the vapour the HBr carries off (its latent heat) and the condensate
    # E-102 returns warmed back from 303.15 K. E-102's duty Q4 (core's) is the vapour condensed
    # at T_REACT and all of it cooled as liquid to T_CW, the HBr cooled as a gas; so the vapour's
    # latent heat and the condensate's reheating are Q4 less the cooling of what passes E-102
    # (as liquid, and the HBr as a gas) plus the latent heat of what passes.
    q4 = state(streams, "Q4")["duty"]["value"]
    passes = {k: v for k, v in s7.items() if k != "HBR"}
    vapour = q4 * 3600.0 - mcp(comps, passes) * (T_REACT - T_CW) - n_hbr * h_gas(comps, "HBR", T_REACT, T_CW) + latent(comps, passes)
    model_in = (vapour + warm_br2 - rxn) / 3600.0  # kW into R-101 that the model asks for
    # the jacket Q2: the absorbed light and the agitator's power (both end as heat in the
    # content) less what the model's terms take in
    q2 = light + R101_AGITATOR - model_in
    q6 = (
        s9["HBR"] * SOLUTION
        - s9["HBR"] * cp_gas(comps, "HBR", 0.5 * (T_ACID + T_VENT)) * (T_ACID - T_VENT)
        - water / mm["H2O"] * comps["H2O"]["liquid_heat_capacity"] * (T_ACID - T_SUPPLY)
    ) / 3600.0
    # the stills (D-009): core's model writes the steam Q7, Q9 and Q14 and the column's
    # condensers Q10 and Q11 ((R + 1) times the distillate's latent heat, ADR 0061); the strip's
    # condenser Q8 takes each part of the vapour from the pot's temperature then, condensed and
    # cooled to its receiver; the column's condensates leave at their bubble point at 2 kPa(a)
    # and are cooled to their receivers (the forerun Q16 on brine, the product Q15 on cooling
    # water with the residue's cool-down in C-101)
    q7, q9, q14, q10, q11 = (state(streams, q)["duty"]["value"] for q in ("Q7", "Q9", "Q14", "Q10", "Q11"))
    q7_own = latent(comps, s12) / 3600.0
    q9_own = (reflux["ST102"] + 1.0) * latent(comps, s14) / 3600.0
    q14_own = (reflux["ST103"] + 1.0) * latent(comps, s15) / 3600.0
    q8 = condenser(comps, strip["top"], T_CW) / 3600.0
    t14 = bubble(comps, s14, P_VAC)
    t15 = bubble(comps, s15, P_VAC)
    q16 = mcp(comps, s14) * (t14 - T_VENT) / 3600.0
    q15 = (mcp(comps, s15) * (t15 - T_CW) + mcp(comps, s16) * (t16 - T_RESIDUE)) / 3600.0
    # the sensible heat core's stills leave out (L-6): the strip's (each part of the vapour at
    # the pot's temperature, the residue at its end, against the crude at T_REACT); the
    # column's, over ST102 and ST103 from the stripped crude at t13: the distillates leaving
    # the condenser at their bubble points and the residue at its end
    sens7 = sensible(comps, strip, T_REACT) / 3600.0
    sens_col = (
        mcp(comps, s14) * t14 + mcp(comps, s15) * t15 + mcp(comps, s16) * t16 - mcp(comps, s13) * t13
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
    print(f"T: S3 {t3:.2f}, S17 {t17:.2f}, S13 {t13:.2f}, S20 {t20:.2f}, S16 {t16:.2f}; bubble points at 2 kPa(a): S14 {t14:.2f}, S15 {t15:.2f}")
    print(f"strip from {strip['start']:.2f} to {strip['end']:.2f} K; top {sum(strip['top']['moles'].values()):.5f} kmol/h here, {sum(s12.values()):.5f} in S12 (core)")
    print(f"vent past E-102 (S7): {', '.join(f'{k} {v / n_hbr:.5f}' for k, v in s7.items() if k != 'HBR')} mol per mol of HBr")
    print(f"past E-103 (S9): {', '.join(f'{k} {v / n_hbr:.6f}' for k, v in s9.items() if k != 'HBR')}; condensate S19 {sum(kg(comps, s19).values()):.4f} kg/h")
    print(f"light needed {needed:.2f} kW at quantum yield {QUANTUM_YIELD}; emitted {LIGHT_SHARE * P_LAMP:.2f} kW")
    print(f"yield of S15's benzyl bromide on the bromine {yield_br2:.4%}, on the toluene make-up {s15['BNBR'] / s1['TOL']:.4%}")
    print(f"Q1 {q1:.4f} Q2 {q2:.4f} Q3 {q3:.4f} Q5 {q5:.4f} Q6 {q6:.4f} Q8 {q8:.4f} Q15 {q15:.4f} Q16 {q16:.4f}; P1 {p1:.4f} P2 {p2:.4f} P3 {p3:.4f} kW")
    print(f"R-101: reactions {rxn / 3600.0:.4f}, bromine warmed {warm_br2 / 3600.0:.4f}, vent vapour and condensate return {vapour / 3600.0:.4f}, so the model takes in {model_in:.4f}; light {light:.4f}, agitator {R101_AGITATOR:.4f} kW")
    print(f"cross-check of the model duties propagate writes: Q7 {q7:.4f} (here {q7_own:.4f}), Q9 {q9:.4f} and Q10 {q10:.4f} (here {q9_own:.4f}), Q14 {q14:.4f} and Q11 {q11:.4f} (here {q14_own:.4f}) kW")
    print(f"stills' sensible heat left out of the steam: ST101 {sens7:+.4f}, ST102 and ST103 {sens_col:+.4f}, together {sens7 + sens_col:+.4f} kW")

    write_balance_output(
        {
            "design": {
                "S1": {"flow": round(toluene, 4)},
                "S2": {"temperature": round(t17, 2)},
                "S3": {"temperature": round(t3, 2)},
                "S5": {"flow": round(br2, 4)},
                "S9": {"flow": round(sum(kg(comps, s9).values()), 4), "composition": mole_fractions(s9)},
                "S10": {"flow": round(water, 4)},
                "S13": {"temperature": round(t13, 2)},
                "S17": {"temperature": round(t17, 2)},
                "S18": {"temperature": round(t17, 2)},
                "S19": {"flow": round(sum(kg(comps, s19).values()), 4), "composition": mole_fractions(s19)},
                "S20": {"temperature": round(t20, 2)},
                "Q1": {"duty": round(q1, 4)},
                "Q2": {"duty": round(q2, 4)},
                "Q3": {"duty": round(q3, 4)},
                "Q5": {"duty": round(q5, 4)},
                "Q6": {"duty": round(q6, 4)},
                "Q8": {"duty": round(q8, 4)},
                "Q15": {"duty": round(q15, 4)},
                "Q16": {"duty": round(q16, 4)},
                "P1": {"duty": round(p1, 4)},
                "P3": {"duty": round(p3, 4)},
            }
        }
    )
    return {
        "S1": toluene, "S5": br2, "S9": s9, "S19": s19, "S10": water, "S2T": t17, "S3T": t3,
        "S13T": t13, "S20T": t20, "Q1": q1, "Q2": q2, "Q3": q3, "Q5": q5, "Q6": q6, "Q8": q8,
        "Q15": q15, "Q16": q16, "P1": p1, "P3": p3, "model_in": model_in, "sens7": sens7,
        "sens_col": sens_col, "product": product,
    }


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
