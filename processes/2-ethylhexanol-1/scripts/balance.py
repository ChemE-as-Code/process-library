"""What core cannot calculate in the 2-ethylhexanol plant (DESIGN.md D-009).

`cheme process propagate --fill` solves the material balance from process/flowsheet.yaml: the
feeds (design specifications for the product rate, the oxo feed, the crude's water, the
caustic's strength and the hydrogenation gas), the conversion steps of process/reactions.yaml,
the component separators, the splitters and the six recycles. This script reads the streams
propagate wrote and gives what core has no model for (DESIGN.md L-2):

- the outlet temperatures of the adiabatic mixers M101 (S5), M201 (S20), M301 (S26), M302
  (S36), M402 (S44), M501 (S49) and M502 (S50), and of the compressors K101 (S11) and K301
  (S33);
- every duty and power (kW), the energy streams Q1 to Q17 and P1 to P3: R-101's heat goes to
  C-102's reboiler (Q1 from the hydroformylation step R101, Q17 from the heavies step R102); R-301's heat raises LP steam for the rest of that reboiler (Q2) and
  R-302's feed heater (Q3), the surplus is exported (Q4); MP steam heats E-301 and the
  reboilers of C-401 to C-403; cooling water takes the rest.

One enthalpy basis, kJ/kmol: each component from its standard formation enthalpy at
298.15 K, liquid for the organics and water (`chemicals` 1.5.2: CRC, NIST WebBook as packaged,
ATcT), ideal gas for propylene, propane, CO, hydrogen and the inerts; a liquid at a constant
heat capacity (process/materials.yaml), a vapour from the liquid through the heat of
vaporization at 298.15 K and a constant ideal-gas heat capacity. The reactors' duties are then
H(out) - H(in) with the heats of reaction in it (they equal process/reactions.yaml's). A
two-phase stream is taken as its organics and water liquid, its light gases gaseous; the
dissolved light gases carry gas enthalpies (their heat of solution left out, L-2). Liquid
propylene (S1) is the gas less its heat of vaporization at 298.15 K.

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

GASES = ("C3H6", "C3H8", "CO", "H2", "N2")
# formation enthalpies at 298.15 K, kJ/kmol: gases as ideal gases (ATcT), the rest as liquids
# (CRC; 2-ethylhexenal NIST WebBook; butyl butyrate Yaws's gas value less the Pitzer heat of
# vaporization), all as packaged in chemicals 1.5.2 (DESIGN.md SRC-6)
HF = {
    "C3H6": 20370.0, "C3H8": -104390.0, "CO": -110525.0, "H2": 0.0, "N2": 0.0,
    "NBAL": -239200.0, "IBAL": -247300.0, "H2O": -285825.0, "NAOH": -416880.0,
    "EPA": -261300.0, "EH": -432800.0, "NBOL": -327300.0, "IBOL": -334700.0, "BUBU": -573290.0,
}
# heats of vaporization at 298.15 K, kJ/kmol: CRC gas less CRC liquid formation enthalpy where
# both are packaged (n- and isobutanal, the butanols, 2-ethylhexanol; water ATcT); the Pitzer
# correlation of chemicals for 2-ethylhexenal and butyl butyrate (Tc, omega packaged); propylene
# and propane from the HEOS fits of thermo 0.6.1 (only for liquid propylene, S1). NaOH stays
# dissolved.
HVAP = {
    "NBAL": 34400.0, "IBAL": 31600.0, "H2O": 44003.0, "EPA": 49630.0, "EH": 67500.0,
    "NBOL": 52400.0, "IBOL": 50900.0, "BUBU": 48390.0, "C3H6": 14090.0, "C3H8": 14800.0,
}
# ideal-gas heat capacities, kJ/(kmol K), means over 298-450 K of thermo 0.6.1 (HEOS fits for the
# gases and water, TRCIG for n-butanal and n-butanol, Joback for the rest)
CPG = {
    "C3H6": 76.3, "C3H8": 88.4, "CO": 29.3, "H2": 29.1, "N2": 29.2, "NBAL": 119.8,
    "IBAL": 120.1, "H2O": 34.1, "EPA": 214.3, "EH": 241.8, "NBOL": 130.3, "IBOL": 131.6,
    "BUBU": 242.7, "NAOH": 55.8,
}

# design choices (DESIGN.md D-009), ASSUMED unless stated
ALPHA_ISO = 1.43  # isobutanal/n-butanal relative volatility at 338 K (thermo's vapour pressures)
C102_R_OVER_RMIN = 1.10  # 100 theoretical plates are 2.7 x Fenske's minimum (SRC-1)
C102_TOP_K = 338.15  # head 60-70 C (SRC-1)
REFLUX = {"C401": 3.0, "C402": 1.0, "C403": 1.0}
TOP_K = {"C401": 350.15, "C402": 409.15, "C403": 420.15}
C403_BOTTOM_K = 453.15
ETA_COMPRESSOR = 0.75
ETA_DRIVE = 0.95
PUMPS_KW = 150.0  # propylene, aldol, hydrogenation, reflux and product pumps together


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
        return {c: flow / mw * x[c] for c in x if x[c] > 0}
    return {c: flow * x[c] / comps[c]["molar_mass"] for c in x if x[c] > 0}


def h_comp(c, t, phase, comps):
    """kJ/kmol of one component on the basis of the module docstring."""
    if c in GASES:
        h = HF[c] + CPG[c] * (t - T0)
        return h - HVAP[c] if phase == "liquid" and c in HVAP else h
    if phase == "vapor":
        return HF[c] + HVAP[c] + CPG[c] * (t - T0)
    return HF[c] + comps[c]["liquid_heat_capacity"] * (t - T0)


def enthalpy(flows, t, phase, comps):
    return sum(n * h_comp(c, t, phase, comps) for c, n in flows.items()) / 3600.0


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
    temps: dict[str, float] = {}
    out: dict[str, dict] = {}

    def t_of(sid):
        return temps.get(sid, state(streams[sid], "temperature"))

    def ph(sid):
        p = state(streams[sid], "phase", "liquid")
        return "liquid" if p == "two-phase" else p

    def n(sid):
        return kmol(streams[sid], comps)

    def h(sid, t=None, phase=None):
        return enthalpy(n(sid), t if t is not None else t_of(sid), phase or ph(sid), comps)

    def mix(out_sid, in_sids):
        temps[out_sid] = solve_t(sum(h(s) for s in in_sids), n(out_sid), ph(out_sid), comps)

    def compress(out_sid, in_sid):
        """Isentropic ideal-gas compression at the mixture's constant cp; power in kW."""
        flows = n(in_sid)
        total = sum(flows.values())
        cp = sum(f * (CPG[c]) for c, f in flows.items()) / total
        k = cp / (cp - R)
        ratio = state(streams[out_sid], "pressure") / state(streams[in_sid], "pressure")
        t1 = t_of(in_sid)
        dt_s = t1 * (ratio ** ((k - 1) / k) - 1)
        temps[out_sid] = t1 + dt_s / ETA_COMPRESSOR
        return total * cp * dt_s / ETA_COMPRESSOR / 3600.0 / ETA_DRIVE

    def latent(flows, t):
        """kW to condense a vapour of these flows at t (the vapour less the liquid enthalpy)."""
        return (enthalpy(flows, t, "vapor", comps) - enthalpy(flows, t, "liquid", comps))

    # --- oxo: compressor, mixer, reactor (R101 + R102 are one vessel, R-101)
    out["P1"] = {"duty": round(compress("S11", "S10"), 1)}
    mix("S5", ("S1", "S3", "S11", "S4"))
    q_r101 = h("S5") - h("S7")  # heat removed from R-101 (reactions and the feed's warming)

    # C-102: the overhead (isobutanal product S15 and the decanted water S16) boiled up at
    # (R + 1), R = 1.1 x Underwood's minimum for the iso/n split at ALPHA_ISO; the vent S14 and
    # the overhead products cooled to 313 K by the same condenser; the reboiler closes the balance
    f13 = n("S13")
    aldehydes = f13.get("IBAL", 0.0) + f13.get("NBAL", 0.0)
    x_f = f13["IBAL"] / aldehydes
    d15 = n("S15")
    x_d = d15["IBAL"] / sum(d15.values())
    r_min = (x_d / x_f - ALPHA_ISO * (1 - x_d) / (1 - x_f)) / (ALPHA_ISO - 1)
    r102 = C102_R_OVER_RMIN * r_min
    top = {c: v for c, v in d15.items()}
    for c, v in n("S16").items():
        top[c] = top.get(c, 0.0) + v
    v102 = {c: v * (r102 + 1) for c, v in top.items()}
    q_c102 = (latent(v102, C102_TOP_K) + h("S15", C102_TOP_K) - h("S15") + h("S16", C102_TOP_K)
              - h("S16") + h("S14", C102_TOP_K, "vapor") - h("S14"))
    q_reb102 = q_c102 + h("S14") + h("S15") + h("S16") + h("S17") - h("S13")
    if q_r101 > q_reb102:
        raise SystemExit("R-101's heat exceeds C-102's reboiler: route the excess (D-009)")
    # R-101's heat leaves by two energy streams, one per conversion step of the vessel
    out["Q1"] = {"duty": round(h("S5") - h("S6"), 1)}
    out["Q17"] = {"duty": round(h("S6") - h("S7"), 1)}
    q2 = q_reb102 - q_r101  # the rest of C-102's reboiler, LP steam raised in R-301
    out["Q2"] = {"duty": round(q2, 1)}
    out["Q5"] = {"duty": round(q_c102, 1)}

    # --- aldol: mixing pump, reactor, cooler (the decanter and the splitter isothermal)
    mix("S20", ("S17", "S18", "S19"))
    out["Q6"] = {"duty": round(h("S20") - h("S21"), 1)}  # R-201's heat to cooling water
    out["Q7"] = {"duty": round(h("S21") - h("S22"), 1)}  # E-201

    # --- hydrogenation
    out["P2"] = {"duty": round(compress("S33", "S32"), 1)}
    mix("S26", ("S25", "S33", "S38"))
    out["Q8"] = {"duty": round(h("S27") - h("S26"), 1)}  # E-301 vaporiser (MP steam)
    q_r301 = h("S27") - h("S28")  # R-301's heat raises LP steam at 300 kPa(a)
    out["Q9"] = {"duty": round(h("S28") - h("S29"), 1)}  # E-302 condenser
    mix("S36", ("S34", "S35"))
    q3 = h("S37") - h("S36")  # R-302 with its feed heater, on R-301's LP steam
    out["Q3"] = {"duty": round(q3, 1)}
    out["Q4"] = {"duty": round(q_r301 - q2 - q3, 1)}  # surplus LP steam exported

    # --- distillation: condenser = boil-up's latent heat + products cooled to their temperature;
    # reboiler closes each column's balance
    lights = n("S41")
    for c, v in n("S40").items():
        lights[c] = lights.get(c, 0.0) + v
    v401 = {c: v * (REFLUX["C401"] + 1) for c, v in lights.items()}
    t1 = TOP_K["C401"]
    q_c401 = latent(v401, t1) + h("S40", t1) - h("S40") + h("S41", t1) - h("S41")
    out["Q10"] = {"duty": round(q_c401 + h("S40") + h("S41") + h("S42") - h("S39"), 1)}
    out["Q11"] = {"duty": round(q_c401, 1)}

    mix("S44", ("S42", "S43"))
    v402 = {c: v * (REFLUX["C402"] + 1) for c, v in n("S45").items()}
    q_c402 = latent(v402, TOP_K["C402"])
    out["Q12"] = {"duty": round(q_c402 + h("S45") + h("S47") - h("S44"), 1)}
    out["Q13"] = {"duty": round(q_c402, 1)}
    out["Q14"] = {"duty": round(h("S45") - h("S46"), 1)}  # E-401 product cooler

    v403 = {c: v * (REFLUX["C403"] + 1) for c, v in n("S43").items()}
    q_c403 = latent(v403, TOP_K["C403"]) + h("S48", C403_BOTTOM_K) - h("S48")
    out["Q15"] = {"duty": round(q_c403 + h("S43") + h("S48") - h("S47"), 1)}
    out["Q16"] = {"duty": round(q_c403, 1)}
    out["P3"] = {"duty": PUMPS_KW}

    # --- collection
    mix("S49", ("S9", "S14", "S31"))
    mix("S50", ("S16", "S24", "S40"))

    for sid, t in temps.items():
        out[sid] = {"temperature": round(t, 2)}
    print(f"R-101 heat {q_r101:.1f} kW; C-102 reboiler {q_reb102:.1f} kW at R = {r102:.1f} "
          f"(Rmin {r_min:.1f}, x_F {x_f:.4f}, x_D {x_d:.4f}); R-301 heat {q_r301:.1f} kW")
    for k in sorted(out, key=lambda s: (s[0], int(s[1:]))):
        print(k, out[k])
    for k, v in out.items():
        if "duty" in v and v["duty"] < 0:
            raise SystemExit(f"{k}: negative duty {v['duty']} kW: the energy stream's direction is wrong")

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": {"design": out}}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
