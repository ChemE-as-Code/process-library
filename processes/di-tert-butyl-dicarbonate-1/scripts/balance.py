"""What core cannot calculate in the Boc2O plant (DESIGN.md D-006, D-007, D-009).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
semi-batch R101 with its vent, the stills DG101, ST101, ST102 and ST301, the mixers, the
splitter, the pass-through steps and the scrubber S101 from process/flowsheet.yaml, and converges
the two recycles at their tears (core ADR 0060). This script gives what core has no model for,
from the streams propagate wrote:

- DC201, the water wash of the stripped melt and its phase split (core has no liquid-liquid
  component separator in propagate): a specified split by component (TO_AQUEOUS), the organic
  phase holding WATER_IN_ORGANIC of water; both phases leave at the adiabatic mix of the melt
  and the warm water less the heat of solution of the KCl (S19, S20);
- X401, the scrubbed vent split from the scrubber's liquor (no gas-liquid separator in
  propagate): the gases to the vent, saturated with water vapour at the scrubber's temperature
  (S33, S34);
- the temperatures of the mixed streams S4, S23 and S28 (adiabatic mixing of their inlets);
- the duties the models leave out (D-009): Q1, Q3, Q4, Q8, Q9, Q10, Q12, Q13, Q14, Q15, Q16.

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With
BALANCE_OUTPUT set it writes the values the flowsheet cites (library ADR 0027). Propagate and
this script are run in turn until neither changes (S19 feeds the paraffin heel's loop, whose
tear propagate converges; nothing of this script lies inside a loop).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# DC201: share of each component of the stripped melt S16 that goes to the brine (D-007)
TO_AQUEOUS = {
    "KCL": 1.0,  # dissolves: 46.8 kg/h in 221 kg/h of water, about 17 wt%, below saturation
    "KTBC": 1.0,  # the unreacted carbonate, a salt (it hydrolyses to KHCO3 and tert-butanol)
    "KOTBU": 1.0,  # traces, a salt (to KOH and tert-butanol)
    "DABCO": 0.95,  # very soluble in water; the rest stays in the melt and ends in the heel
    "TBA": 0.8,  # tert-butanol divides between the melt and the brine, most to the water
    "CO2": 1.0,
    "COCL2": 1.0,  # traces, hydrolysed in the water
    "BOC2O": 0.003,  # Boc2O is insoluble in water (Wikipedia); entrained and dissolved loss
    "HEX": 0.0,
    "PARAF": 0.0,
}
WATER_IN_ORGANIC = 0.002  # kg of water per kg of the washed melt (D-007)
KCL_SOLUTION = 17_000.0  # kJ/kmol, endothermic heat of solution of KCl in water (D-007)

# X401: the gases of the scrubber's outlet S32 go to the vent S33 (D-007)
VENT_GASES = ("CO2", "IB", "COCL2", "HEX", "TBA")
T_SCRUB = 303.15  # K, the scrubber's liquor and vent (D-007)
P_SCRUB = 101.325  # kPa(a)
NAOH_DILUTION = -15_000.0  # kJ/kmol NaOH, the 50 wt% caustic diluted in the liquor (as p-toluenesulfonyl-chloride-1, D-009)

# temperatures (K)
T_AMB = 298.15
T_REACT = 278.15  # R101 (D-005)
T_COND = 283.15  # condensates of the strips and the forerun on brine (D-009)
T_PRODUCT = 303.15  # the main cut cooled to storage, above Boc2O's melting point (D-008)
T_WASH_WATER = 318.15
# Mean temperatures at which the distillates leave the pot (D-009): ST101 and the main cut the
# mean of their stills' start and end (`cheme process stills`: 294.97 -> 312.08 K; the main cut
# 336.28 -> 357.9 K); ST102's pot is held near 313 K while the pressure falls (its model starts
# at 257 K, core limit L-5); the forerun between the charge's 321 K and its end at 336 K
T_VAP = {"ST101": 0.5 * (294.97 + 312.08), "ST102": 313.15, "fore": 328.0, "main": 0.5 * (336.28 + 357.9)}
T_END = {"ST102": 313.15}
V201_METAL = 2000.0  # kJ/K, V-201's steel (about 4 t at 0.5 kJ/(kg K)) (D-009)
# kJ/(kmol K), gas heat capacities near 270-300 K (chemicals 1.5.2, CRC tables): CO2 37.1,
# isobutene 89.1, hexane 143, phosgene 57.7, tert-butanol 113.6, water vapour 33.6
CP_GAS = {"CO2": 37.1, "IB": 89.1, "HEX": 143.0, "COCL2": 57.7, "TBA": 113.6, "H2O": 33.6}
# kJ/(kmol K) of the scrubber's dissolved salts, ASSUMED order (D-009)
CP_LIQ_EXTRA = {"NAOH": 80.0, "NA2CO3": 120.0, "NACL": 50.0, "IB": 120.0}
# liquid phosgene from 253.15 K evaporated at 150 kPa(a) and warmed to 293.15 K: 100 kJ/(kmol K)
# x 40 K + 24800 kJ/kmol (as processes/benzyl-chloroformate-1, D-009)
PHOSGENE_EVAPORATION = 100.0 * 40.0 + 24_800.0
CO2_ABSORPTION = 15_000.0  # kJ/kmol, as materials.yaml's heat_of_vaporization of CO2 (D-009)
HEAT = {"NPH": -400_000.0, "NCO": -110_000.0}  # reactions.yaml (ASSUMED)


def load():
    sheet = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    mats = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in mats["components"]}
    return {s["id"]: s for s in sheet["streams"]}, comps


def state(streams, sid):
    return streams[sid]["state"]["design"]


def kmol(streams, comps, sid):
    """kmol/h of each component of a material stream."""
    s = state(streams, sid)
    if "flow" not in s or "composition" not in s:  # a first pass, before propagate wrote it
        return {}
    flow, comp = s["flow"]["value"], s["composition"]
    if comp["basis"] == "mole_fraction":
        mean = sum(x * comps[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mean * x for k, x in comp["values"].items() if x > 0}
    return {k: flow * w / comps[k]["molar_mass"] for k, w in comp["values"].items() if w > 0}


def cp(comps, name):
    return comps[name].get("liquid_heat_capacity", CP_LIQ_EXTRA.get(name, 0.0))


def mcp(comps, n):
    return sum(v * cp(comps, k) for k, v in n.items())


def latent(comps, n):
    return sum(v * comps[k].get("heat_of_vaporization", 0.0) for k, v in n.items())


def mass(comps, n):
    return sum(v * comps[k]["molar_mass"] for k, v in n.items())


def mole_fractions(n):
    total = sum(n.values())
    return {k: round(v / total, 9) for k, v in n.items() if v > 0}


def water_vapour_pressure(t):
    a, b, c = 4.6543, 1435.264, -64.848  # NIST WebBook (Stull 1947), materials.yaml
    return 100.0 * 10 ** (a - b / (t + c))


def main() -> dict:
    streams, comps = load()
    out: dict[str, dict] = {}
    kw = 1.0 / 3600.0  # kJ/h -> kW

    # DC201: wash and phase split
    melt = kmol(streams, comps, "S16")
    water = kmol(streams, comps, "S18")["H2O"]
    aq = {k: v * TO_AQUEOUS.get(k, 0.0) for k, v in melt.items()}
    org = {k: v - aq[k] for k, v in melt.items()}
    org_dry = mass(comps, org)
    org["H2O"] = WATER_IN_ORGANIC / (1 - WATER_IN_ORGANIC) * org_dry / comps["H2O"]["molar_mass"]
    aq["H2O"] = water - org["H2O"]
    t16 = state(streams, "S16")["temperature"]["value"]
    t18 = state(streams, "S18")["temperature"]["value"]
    heat_in = mcp(comps, melt) * t16 + water * cp(comps, "H2O") * t18 - melt.get("KCL", 0.0) * KCL_SOLUTION
    t_wash = heat_in / (mcp(comps, melt) + water * cp(comps, "H2O"))
    for sid, n in (("S19", org), ("S20", aq)):
        out[sid] = {"flow": round(mass(comps, n), 4), "composition": mole_fractions(n), "temperature": round(t_wash, 2)}

    # mixed temperatures
    def mix_t(sids, temps=None):
        total, cap = 0.0, 0.0
        for sid in sids:
            n = kmol(streams, comps, sid)
            t = (temps or {}).get(sid, state(streams, sid)["temperature"]["value"])
            total += mcp(comps, n) * t
            cap += mcp(comps, n)
        return total / cap

    out["S4"] = {"temperature": round(mix_t(["S1", "S2", "S3", "S30"]), 2)}
    out["S23"] = {"temperature": round(mix_t(["S19", "S21", "S22"], {"S19": t_wash}), 2)}
    g9, g11 = kmol(streams, comps, "S9"), kmol(streams, comps, "S11")
    t9, t11 = state(streams, "S9")["temperature"]["value"], state(streams, "S11")["temperature"]["value"]
    gcp = lambda n: sum(v * CP_GAS.get(k, 0.0) for k, v in n.items())  # noqa: E731
    t28 = (gcp(g9) * t9 + gcp(g11) * t11) / (gcp(g9) + gcp(g11))
    out["S28"] = {"temperature": round(t28, 2)}

    # X401: the scrubbed vent and the liquor
    s32 = kmol(streams, comps, "S32")
    gas = {k: v for k, v in s32.items() if k in VENT_GASES}
    p_w = water_vapour_pressure(T_SCRUB)
    gas["H2O"] = sum(gas.values()) * p_w / (P_SCRUB - p_w)
    liq = {k: v for k, v in s32.items() if k not in VENT_GASES}
    liq["H2O"] = liq.get("H2O", 0.0) - gas["H2O"]
    out["S33"] = {"flow": round(mass(comps, gas), 4), "composition": mole_fractions(gas)}
    out["S34"] = {"flow": round(mass(comps, liq), 4), "composition": mole_fractions(liq)}

    # duties (kW)
    s4 = kmol(streams, comps, "S4")
    out["Q1"] = {"duty": round(mcp(comps, s4) * (out["S4"]["temperature"] - T_REACT) * kw, 4)}
    out["Q3"] = {"duty": round(kmol(streams, comps, "S10").get("CO2", 0.0) * CO2_ABSORPTION * kw, 4)}
    out["Q4"] = {"duty": round(kmol(streams, comps, "S6")["COCL2"] * PHOSGENE_EVAPORATION * kw, 4)}
    s12, s13, s15 = (kmol(streams, comps, s) for s in ("S12", "S13", "S15"))
    s16 = melt
    # V-201: the distillates from 278 K to the pot's mean temperature, the melt to 313 K, the
    # vessel's steel from the wash's temperature back to 313 K
    q8 = (mcp(comps, s13) * (T_VAP["ST101"] - T_REACT) + mcp(comps, s15) * (T_VAP["ST102"] - T_REACT)
          + mcp(comps, s16) * (T_END["ST102"] - T_REACT))
    hours = batch_hours(streams)
    q8 += V201_METAL * (T_END["ST102"] - t_wash) / hours
    out["Q8"] = {"duty": round(q8 * kw, 4)}
    out["Q9"] = {"duty": round((latent(comps, s13) + mcp(comps, s13) * (T_VAP["ST101"] - T_COND)) * kw, 4)}
    out["Q16"] = {"duty": round((latent(comps, s15) + mcp(comps, s15) * (T_VAP["ST102"] - T_COND)) * kw, 4)}
    w17 = kmol(streams, comps, "S17")["H2O"]
    out["Q10"] = {"duty": round(w17 * cp(comps, "H2O") * (T_WASH_WATER - T_AMB) * kw, 4)}
    # C-301: the melt and the paraffin make-up to the temperatures they leave at (the heel enters
    # and leaves at the end temperature, net zero)
    s21, s24, s25, s27 = (kmol(streams, comps, s) for s in ("S21", "S24", "S25", "S27"))
    t27 = state(streams, "S27")["temperature"]["value"]
    q12 = (mcp(comps, s24) * T_VAP["fore"] + mcp(comps, s25) * T_VAP["main"] + mcp(comps, s27) * t27
           - mcp(comps, org) * t_wash - mcp(comps, s21) * state(streams, "S21")["temperature"]["value"])
    out["Q12"] = {"duty": round(q12 * kw, 4)}
    out["Q13"] = {"duty": round((latent(comps, s24) + mcp(comps, s24) * (T_VAP["fore"] - T_COND)) * kw, 4)}
    out["Q14"] = {"duty": round((latent(comps, s25) + mcp(comps, s25) * (T_VAP["main"] - T_PRODUCT)) * kw, 4)}
    # S101: reaction heats, the caustic's dilution, the inlets brought to 303 K, the water
    # evaporated into the vent
    ext_nph = kmol(streams, comps, "S28").get("COCL2", 0.0) - s32.get("COCL2", 0.0)
    ext_nco = kmol(streams, comps, "S28").get("CO2", 0.0) - s32.get("CO2", 0.0)
    q15 = -(HEAT["NPH"] * ext_nph + HEAT["NCO"] * ext_nco)
    q15 -= NAOH_DILUTION * kmol(streams, comps, "S29")["NAOH"]
    q15 -= gcp(kmol(streams, comps, "S28")) * (T_SCRUB - t28)
    for sid in ("S29", "S31"):
        q15 -= mcp(comps, kmol(streams, comps, sid)) * (T_SCRUB - T_AMB)
    q15 -= gas["H2O"] * comps["H2O"]["heat_of_vaporization"]
    out["Q15"] = {"duty": round(q15 * kw, 4)}

    write_balance_output({"design": out})
    return out


def batch_hours(streams) -> float:
    """Hours of flows per batch: the recipe's batch size over its stream's flow (core ADR 0051)."""
    recipe = yaml.safe_load((ROOT / "process" / "recipe.yaml").read_text(encoding="utf-8"))
    size = recipe["batch_size"]
    flow = state(streams, size["stream"]).get("flow")
    if flow is None:  # a first pass, before propagate has written the product
        return 10.0
    return size["value"] / flow["value"]


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    result = main()
    for sid, values in result.items():
        print(sid, json.dumps(values))
