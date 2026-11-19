"""What core cannot calculate in the vinyl acetate plant (DESIGN.md D-008).

`cheme process propagate --fill` solves the material balance from process/flowsheet.yaml: the
feeds (design specifications for the product rate and the reactor feed of US 8 765 995 B2
Table 2), the conversion reactor R101, the component separators, the splitters and the three
recycles (tears S2, S28, S31), and writes R101's duty Q1 on the elements basis from the
ideal-gas data of process/materials.yaml (core ADR 0059). This script reads the streams
propagate wrote and gives what core has no model for:

- the temperatures of the streams core does not derive (DESIGN.md L-4): the outlets of the
  adiabatic mixers M101 (S3), M102 (S8), M103 (S24), M201 (S25), M202 (S29) and M203 (S34),
  the slip-gas scrubber's liquor S37, and the cycle gas S2 at the compressor's discharge;
- every other duty and power (kW), the energy streams Q2 to Q13 and P1 to P3, on one enthalpy
  basis: liquids from 298.15 K at a constant heat capacity, vapours from the liquid at 298.15 K
  through the heat of vaporization at 298.15 K and the ideal-gas heat capacity of
  process/materials.yaml; the permanent gases as ideal gases. The heats of vaporization are the
  differences of the liquid and ideal-gas formation enthalpies, so the vapour is the ideal-gas
  monomer that R-101's duty and process/materials.yaml use. No property package of core covers
  these mixtures (DESIGN.md L-2); acetic acid's association in the vapour is left out.

Run: cheme run scripts/balance.py (prints the table; writes the balance-output JSON of the
library's ADR 0027 when BALANCE_OUTPUT names a file).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
T0 = 298.15
R = 8.314462618  # kJ/(kmol K)

# liquid heat capacities, kJ/(kmol K): acetic acid and water the CRC Handbook's standard-state
# values as packaged in chemicals 1.5.2; vinyl acetate thermo 0.6.1's ZABRANSKY_SPLINE_C, its mean
# over 298-360 K (single facts, library ADR 0037; DESIGN.md SRC-5)
CP_LIQ = {"VAM": 172.0, "ACOH": 123.3, "H2O": 75.3}
# heats of vaporization at 298.15 K from the liquid to the ideal-gas monomer, kJ/kmol: the
# difference of the gas and liquid standard formation enthalpies of chemicals 1.5.2 from one
# source each (DESIGN.md SRC-5), the gas values those of process/materials.yaml:
# acetic acid CRC -432.2 - (-484.3), vinyl acetate CRC -314.4 - (-349.2), water ATcT
# -241.822 - (-285.825) kJ/mol
HVAP_298 = {"ACOH": 52100.0, "VAM": 34800.0, "H2O": 44003.0}
CONDENSABLE = ("VAM", "ACOH", "H2O")

# design choices (DESIGN.md D-008), ASSUMED
ETA_COMPRESSOR = 0.75  # isentropic efficiency of K-101
ETA_DRIVE = 0.95  # motor and gear
REGEN_KJ_PER_KG_CO2 = 2500.0  # hot carbonate regenerator heat per kg CO2 stripped
REGEN_CW_SHARE = 1.0  # the regenerator's overhead condenser and lean-solution cooler reject it
C201_BOILUP_PER_DISTILLATE = 2.0  # mol vapour per mol of the decanted overhead (reflux 1)
C202_TOP_REFLUX = 20.0  # reflux ratio over the small water/low-boiler top product
PUMPS_KW = {"P2": 250.0, "P3": 180.0}  # the solution pumps of A-101; the distillation pumps


def load():
    flowsheet = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text(encoding="utf-8"))
    materials = yaml.safe_load((ROOT / "process/materials.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in materials["components"]}
    streams = {s["id"]: s for s in flowsheet["streams"] if s.get("kind") != "energy"}
    return flowsheet, comps, streams


def kmol(stream, comps):
    """Component flows, kmol/h, of a stream as propagate wrote it."""
    st = stream["state"]["design"]
    flow = st["flow"]["value"]
    comp = st["composition"]
    x = comp["values"]
    if comp["basis"] == "mole_fraction":
        mw = sum(x[c] * comps[c]["molar_mass"] for c in x)
        total = flow / mw
        return {c: total * x[c] for c in x if x[c] > 0}
    return {c: flow * x[c] / comps[c]["molar_mass"] for c in x if x[c] > 0}


def h_ig(comp, t):
    """Ideal-gas sensible enthalpy from 298.15 K, kJ/kmol."""
    a = comp["ideal_gas"]["cp_R"]
    def integral(tt):
        return sum(a[i] * tt ** (i + 1) / (i + 1) for i in range(len(a)))
    return R * (integral(t) - integral(T0))


def enthalpy(flows, t, phase, comps):
    """kW of a stream on the basis of the module docstring."""
    total = 0.0
    for c, n in flows.items():
        if phase == "liquid" and c in CONDENSABLE:
            h = CP_LIQ[c] * (t - T0)
        elif c in CONDENSABLE:
            h = HVAP_298[c] + h_ig(comps[c], t)
        else:  # permanent gases, also where a liquid carries them
            h = h_ig(comps[c], t)
        total += n * h
    return total / 3600.0


def state(stream, key, default=None):
    value = stream["state"]["design"].get(key)
    return value["value"] if value else default


def solve_t(target_kw, flows, phase, comps, lo=250.0, hi=700.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        if enthalpy(flows, mid, phase, comps) > target_kw:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def main() -> None:
    fs, comps, streams = load()
    temps: dict[str, float] = {}  # the temperatures this script derives, used downstream

    def t_of(sid):
        return temps.get(sid, state(streams[sid], "temperature"))

    def h(sid, t=None):
        s = streams[sid]
        # a feed without a stated phase (S1, S7) is a gas
        return enthalpy(kmol(s, comps), t if t is not None else t_of(sid),
                        state(s, "phase", "vapor"), comps)

    def mix(out_sid, in_sids):
        """An adiabatic mixer's outlet temperature from its inlets' enthalpy."""
        t = solve_t(sum(h(s) for s in in_sids), kmol(streams[out_sid], comps),
                    state(streams[out_sid], "phase"), comps)
        temps[out_sid] = t
        return t

    out: dict[str, dict] = {}

    # K-101 first: the cycle gas S24 (M103: the washed, CO2-lean slip S22 and the bypass S23),
    # compressed isentropically to S2's pressure, ideal gas with the mean cp
    mix("S24", ("S22", "S23"))
    f24 = kmol(streams["S24"], comps)
    t24 = temps["S24"]
    p_ratio = state(streams["S2"], "pressure") / state(streams["S24"], "pressure")
    n24 = sum(f24.values())
    cp = sum(n * (h_ig(comps[c], t24 + 1) - h_ig(comps[c], t24)) for c, n in f24.items()) / n24
    t2s = t24 * p_ratio ** (R / cp)
    w_s = enthalpy(f24, t2s, "vapor", comps) - enthalpy(f24, t24, "vapor", comps)
    w = w_s / ETA_COMPRESSOR
    temps["S2"] = solve_t(enthalpy(f24, t24, "vapor", comps) + w, f24, "vapor", comps)
    out["P1"] = {"duty": round(w / ETA_DRIVE, 1)}

    # M101: the fresh ethylene S1 into the compressed cycle gas S2
    mix("S3", ("S1", "S2"))

    # T-101: the cycle gas S3 saturated with the fresh acid S4 and the recycle acid S5 (Q2, steam)
    q2 = h("S6") - h("S3") - h("S4") - h("S5")
    out["Q2"] = {"duty": round(q2, 1)}

    # S8: the acid-saturated gas S6 and the oxygen S7 mixed adiabatically (M102)
    mix("S8", ("S6", "S7"))

    # E-101/E-102: the feed S8 heated to S9 by the effluent S10 (Q3), the rest of the effluent's
    # cooling to S11 on cooling water (Q4)
    q3 = h("S9") - h("S8")
    q4 = h("S10") - h("S11") - q3
    out["Q3"] = {"duty": round(q3, 1)}
    out["Q4"] = {"duty": round(q4, 1)}

    # C-101: the overhead condenser on cooling water (Q5); no reboiler, the feed is hot; the
    # decanter gives the organic phase S13 and the aqueous phase S38
    q5 = h("S11") - h("S12") - h("S13") - h("S14") - h("S38")
    out["Q5"] = {"duty": round(q5, 1)}

    # C-102 with the scrub-acid cooler E-202: the recycle acid cooled from S28's temperature
    # to S15's, the scrubber's heat of condensation (Q6, cooling water)
    q_e202 = h("S15", t_of("S28")) - h("S15")
    q6 = q_e202 + h("S12") + h("S15") - h("S16") - h("S17")
    out["Q6"] = {"duty": round(q6, 1)}

    # C-104: the slip S20 washed with water S35, adiabatic: the gas S36 leaves at its stated
    # temperature, the liquor S37 takes the heat of the acid it absorbs
    t37 = solve_t(h("S20") + h("S35") - h("S36"), kmol(streams["S37"], comps), "liquid", comps)
    temps["S37"] = t37

    # A-101: regenerator steam (Q7) per kg of CO2 stripped, rejected to cooling water (Q8),
    # solution pumps (P2)
    co2_kg = kmol(streams["S21"], comps).get("CO2", 0.0) * comps["CO2"]["molar_mass"]
    q7 = co2_kg * REGEN_KJ_PER_KG_CO2 / 3600.0
    q8 = q7 * REGEN_CW_SHARE + h("S36") - h("S21") - h("S22")
    out["Q7"] = {"duty": round(q7, 1)}
    out["Q8"] = {"duty": round(q8, 1)}
    out["P2"] = {"duty": PUMPS_KW["P2"]}

    # C-201: its feed S25 (M201: C-101's bottoms S14, the scrubber bottoms S17, C-202's bottoms
    # S31 and the slip-gas scrubber's liquor S37), the decanted overhead (organic S26 + aqueous
    # S27) boiled up at C201_BOILUP_PER_DISTILLATE, condensed and cooled to the decanter (Q10,
    # cooling water); the reboiler closes the column's balance (Q1 from R-101's steam, Q9
    # imported steam)
    mix("S25", ("S14", "S17", "S31", "S37"))
    f_ov = {}
    for sid in ("S26", "S27"):
        for c, n in kmol(streams[sid], comps).items():
            f_ov[c] = f_ov.get(c, 0.0) + n
    t_top = 343.15  # ASSUMED top temperature, inside SRC-2's 50-90 C
    v = {c: n * C201_BOILUP_PER_DISTILLATE for c, n in f_ov.items()}
    q10 = enthalpy(v, t_top, "vapor", comps) - enthalpy(v, t_of("S26"), "liquid", comps)
    q_reb201 = q10 + h("S26") + h("S27") + h("S28") - h("S25")
    out["Q10"] = {"duty": round(q10, 1)}

    # C-202: its feed S29 (V-201, M202: the organic phases S13 and S26); the top product S30 at
    # reflux C202_TOP_REFLUX condensed (Q12); the reboiler (Q11) closes the balance with the
    # side draw S32 and the bottoms S31 at their bubble points
    mix("S29", ("S13", "S26"))
    v202 = {c: n * (C202_TOP_REFLUX + 1) for c, n in kmol(streams["S30"], comps).items()}
    q12 = enthalpy(v202, 345.15, "vapor", comps) - enthalpy(v202, 313.15, "liquid", comps)
    q11 = q12 + h("S30") + h("S31") + h("S32") - h("S29")
    out["Q11"] = {"duty": round(q11, 1)}
    out["Q12"] = {"duty": round(q12, 1)}

    # E-201: the side draw cooled to storage (Q13)
    q13 = h("S32") - h("S33")
    out["Q13"] = {"duty": round(q13, 1)}
    out["P3"] = {"duty": PUMPS_KW["P3"]}

    # M203: the aqueous effluent S34 from C-101's and C-201's aqueous phases and C-202's top
    mix("S34", ("S38", "S27", "S30"))

    # R-101's heat raises LP steam at 450 kPa(a) for T-101 (Q2), the regenerator (Q7) and C-202
    # (Q11); propagate writes what is left (Q1) to C-201's reboiler, whose rest is imported (Q9)
    energy = {s["id"]: s for s in fs["streams"] if s.get("kind") == "energy"}
    q1 = energy.get("Q1", {}).get("state", {}).get("design", {}).get("duty", {}).get("value")
    q9 = q_reb201 - (q1 or 0.0)
    out["Q9"] = {"duty": round(q9, 1)}

    for sid, t in temps.items():
        out[sid] = {"temperature": round(t, 2)}
    print("temperatures: " + ", ".join(f"{s} {t:.2f} K" for s, t in temps.items()))
    print(f"R-101 Q1 (propagate) {q1} kW; C-201 reboiler {q_reb201:.1f} kW -> imported Q9 {q9:.1f}")
    steam_users = q2 + q7 + q11 + q_reb201
    print(f"steam users {steam_users:.1f} kW; R-101 covers {steam_users - q9:.1f} kW")
    for k in sorted(out, key=lambda s: (s[0], int(s[1:]))):
        print(k, out[k])
    if q9 < 0:
        raise SystemExit("R-101's steam exceeds the plant's LP steam users: route the excess (D-008)")

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": {"design": out}}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
