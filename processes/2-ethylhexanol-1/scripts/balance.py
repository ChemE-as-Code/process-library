"""What core cannot calculate in the 2-ethylhexanol plant (DESIGN.md D-009).

`cheme process propagate --fill` solves the material balance from process/flowsheet.yaml: the
feeds (design specifications for the product rate, the oxo feed, the crude's water, the
caustic's strength and the hydrogenation gas), the conversion steps of process/reactions.yaml,
the component separators, the splitters and the six recycles. This script reads the streams
propagate wrote and gives what core has no model for (DESIGN.md L-2):

- the outlet temperatures of the adiabatic mixers M101 (S5), M201 (S20), M301 (S26), M302
  (S36), M402 (S44), M501 (S49) and M502 (S50), of the adiabatic separator V101 (S8 to S10,
  S12, and S51 after the pump) and stripper C101 (S3, S13), and of the compressors K101 (S11)
  and K301 (S33);
- every duty and power (kW), the energy streams Q1, Q3 to Q18 and P1 to P6: R-101's heat
  covers C-102's whole reboiler (Q1 from the hydroformylation step R101, Q17 from the heavies
  step R102) and its surplus goes to cooling water (Q18); R-301's heat raises LP steam for
  R-302's feed heater (Q3), the surplus is exported (Q4); MP steam heats E-301 and the
  reboilers of C-401 to C-403; cooling water takes the rest; electricity drives the
  compressors, the pumps (P3, P6) and the vacuum pumps of the four vacuum columns (P4, P5).

One enthalpy basis, kJ/kmol: each component from its standard formation enthalpy at
298.15 K, liquid for the organics and water (`chemicals` 1.5.2: CRC, NIST WebBook as packaged,
ATcT), ideal gas for propylene, propane, CO, hydrogen and the inerts; a liquid at a constant
heat capacity (process/materials.yaml), a vapour from the liquid through the heat of
vaporization at 298.15 K and a constant ideal-gas heat capacity. The reactors' duties are then
H(out) - H(in) with the heats of reaction in it (they equal process/reactions.yaml's). In a
two-phase or liquid stream the organics and water are liquid and the light gases gaseous: the
dissolved light gases carry gas enthalpies (their heat of solution left out, L-2). Only the
liquid propylene feed (S1) holds its propylene and propane as liquids, the gas less its heat
of vaporization at 298.15 K; that heat is taken up where S1 joins the gas in M101.

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
# NaOH: chemicals' liquid (molten) value Hfl, used for the dissolved caustic (ASSUMED basis); NaOH
# passes every step unreacted, so its formation enthalpy cancels, and the caustic's heat of
# dilution is left out (L-2).
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
# gases and water, TRCIG for n-butanal and n-butanol, WEBBOOK_SHOMATE for NaOH, Joback for the
# rest)
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
# C-403's bottoms: the temperature of the real heavies the pseudo-component stands for (L-4),
# not butyl butyrate's own bubble point at 30 kPa(a) (about 398 K, thermo's vapour pressure)
C403_BOTTOM_K = 453.15
ETA_COMPRESSOR = 0.75
ETA_DRIVE = 0.95
PUMPS_KW = 150.0  # propylene, aldol, hydrogenation, reflux and product pumps together
RHO_CRUDE = 703.0  # kg/m3: n-butanal at 391 K and 5 MPa (thermo 0.6.1, DIPPR Perry 8E, COSTALD)
ETA_PUMP = 0.60
C102_HEAD_KPA = 50.0  # C-102's head, the low end of SRC-1's 50-80 kPa(a)
ETA_VACUUM = 0.40  # liquid-ring vacuum pump, isentropic
VACUUM_LEAK_KW = 15.0  # per vacuum column: the air leaking in and the vapour it carries

# every step but the compressors (their drives' losses leave as heat) and the pumps and vacuum
# pumps (their work, P3 to P6, is neglected in the streams): step, inlets, outlets, energy in, out
CLOSURE = (
    ("M101", ("S1", "S3", "S11", "S4"), ("S5",), (), ()),
    ("R101", ("S5",), ("S6",), (), ("Q1", "Q18")),
    ("R102", ("S6",), ("S7",), (), ("Q17",)),
    ("V101", ("S7",), ("S8", "S12"), (), ()),
    ("X101", ("S8",), ("S9", "S10"), (), ()),
    ("C101", ("S51", "S2"), ("S3", "S13"), (), ()),
    ("C102", ("S13",), ("S14", "S15", "S16", "S17"), ("Q1", "Q17"), ("Q5",)),
    ("M201", ("S17", "S18", "S19"), ("S20",), (), ()),
    ("R201", ("S20",), ("S21",), (), ("Q6",)),
    ("E201", ("S21",), ("S22",), (), ("Q7",)),
    ("V201", ("S22",), ("S23", "S25"), (), ()),
    ("X201", ("S23",), ("S24", "S19"), (), ()),
    ("M301", ("S25", "S33", "S38"), ("S26",), (), ()),
    ("E301", ("S26",), ("S27",), ("Q8",), ()),
    ("R301", ("S27",), ("S28",), (), ("Q3", "Q4")),
    ("E302", ("S28",), ("S29",), (), ("Q9",)),
    ("V301", ("S29",), ("S30", "S34"), (), ()),
    ("X301", ("S30",), ("S31", "S32"), (), ()),
    ("M302", ("S34", "S35"), ("S36",), (), ()),
    ("R302", ("S36",), ("S37",), ("Q3",), ()),
    ("V302", ("S37",), ("S38", "S39"), (), ()),
    ("C401", ("S39",), ("S40", "S41", "S42"), ("Q10",), ("Q11",)),
    ("M402", ("S42", "S43"), ("S44",), (), ()),
    ("C402", ("S44",), ("S45", "S47"), ("Q12",), ("Q13",)),
    ("E401", ("S45",), ("S46",), (), ("Q14",)),
    ("C403", ("S47",), ("S43", "S48"), ("Q15",), ("Q16",)),
    ("M501", ("S9", "S14", "S31"), ("S49",), (), ()),
    ("M502", ("S16", "S24", "S40"), ("S50",), (), ()),
)


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


LIQUID_GASES = ("S1",)  # the only stream whose propylene and propane are liquid


def h_comp(c, t, phase, comps, liquid_gases=False):
    """kJ/kmol of one component on the basis of the module docstring."""
    if c in GASES:
        h = HF[c] + CPG[c] * (t - T0)
        return h - HVAP[c] if liquid_gases and c in HVAP else h
    if phase == "vapor":
        return HF[c] + HVAP[c] + CPG[c] * (t - T0)
    return HF[c] + comps[c]["liquid_heat_capacity"] * (t - T0)


def enthalpy(flows, t, phase, comps, liquid_gases=False):
    return sum(n * h_comp(c, t, phase, comps, liquid_gases) for c, n in flows.items()) / 3600.0


def state(stream, key, default=None):
    value = stream["state"]["design"].get(key)
    return value["value"] if value else default


def solve_t(target_kw, h_of_t, lo=250.0, hi=700.0):
    """The temperature at which h_of_t (kW, rising with t) reaches target_kw."""
    for _ in range(200):
        mid = (lo + hi) / 2
        if h_of_t(mid) > target_kw:
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
        return enthalpy(n(sid), t if t is not None else t_of(sid), phase or ph(sid), comps,
                        sid in LIQUID_GASES)

    def adiabatic(in_sids, out_sids):
        """The outlets of an adiabatic step at one temperature: enthalpy in = enthalpy out."""
        t = solve_t(sum(h(s) for s in in_sids), lambda x: sum(h(s, x) for s in out_sids))
        for s in out_sids:
            temps[s] = t
        return t

    def mix(out_sid, in_sids):
        adiabatic(in_sids, (out_sid,))

    def isentropic(flows, t1, ratio, eta):
        """Ideal-gas compression at the mixture's constant cp: (kW of shaft work, outlet K)."""
        total = sum(flows.values())
        cp = sum(f * (CPG[c]) for c, f in flows.items()) / total
        k = cp / (cp - R)
        dt_s = t1 * (ratio ** ((k - 1) / k) - 1)
        return total * cp * dt_s / eta / 3600.0, t1 + dt_s / eta

    def compress(out_sid, in_sid):
        """A cycle-gas compressor; electric power in kW."""
        ratio = state(streams[out_sid], "pressure") / state(streams[in_sid], "pressure")
        work, temps[out_sid] = isentropic(n(in_sid), t_of(in_sid), ratio, ETA_COMPRESSOR)
        return work / ETA_DRIVE

    def latent(flows, t):
        """kW to condense a vapour of these flows at t (the vapour less the liquid enthalpy)."""
        return (enthalpy(flows, t, "vapor", comps) - enthalpy(flows, t, "liquid", comps))

    # --- oxo: separator, compressor, crude pump, stripper, mixer, reactor (R101 + R102 are one
    # vessel, R-101). V-101 and C-101 have no duty: their outlets take the temperature that
    # closes their balance (the aldehydes and water they evaporate into the gas cool them).
    adiabatic(("S7",), ("S8", "S12"))
    temps["S9"] = temps["S10"] = temps["S8"]  # X101 splits the gas
    temps["S51"] = temps["S12"]  # P-101's work neglected in the stream
    lift = state(streams["S51"], "pressure") - state(streams["S12"], "pressure")  # kPa
    out["P6"] = {"duty": round(state(streams["S12"], "flow") / RHO_CRUDE * lift / 3600.0
                                 / ETA_PUMP / ETA_DRIVE, 1)}
    out["P1"] = {"duty": round(compress("S11", "S10"), 1)}
    adiabatic(("S51", "S2"), ("S3", "S13"))
    mix("S5", ("S1", "S3", "S11", "S4"))
    q_r101 = h("S5") - h("S7")  # heat removed from R-101 (reactions and the feed's warming)

    # C-102: the isobutanal overhead S15 boiled up at (R + 1), R = 1.1 x Underwood's minimum for
    # the iso/n split at ALPHA_ISO; the water S16 condensed once and decanted (D-004: only the
    # organic phase is refluxed); the vent S14 and the overhead products cooled to 313 K by the
    # same condenser; the reboiler closes the balance
    f13 = n("S13")
    aldehydes = f13.get("IBAL", 0.0) + f13.get("NBAL", 0.0)
    x_f = f13["IBAL"] / aldehydes
    d15 = n("S15")
    x_d = d15["IBAL"] / sum(d15.values())
    r_min = (x_d / x_f - ALPHA_ISO * (1 - x_d) / (1 - x_f)) / (ALPHA_ISO - 1)
    r102 = C102_R_OVER_RMIN * r_min
    v102 = {c: v * (r102 + 1) for c, v in d15.items()}
    for c, v in n("S16").items():
        v102[c] = v102.get(c, 0.0) + v
    q_c102 = (latent(v102, C102_TOP_K) + h("S15", C102_TOP_K) - h("S15") + h("S16", C102_TOP_K)
              - h("S16") + h("S14", C102_TOP_K, "vapor") - h("S14"))
    q_reb102 = q_c102 + h("S14") + h("S15") + h("S16") + h("S17") - h("S13")
    if q_r101 < q_reb102:
        raise SystemExit("C-102's reboiler exceeds R-101's heat: add steam to it (D-009)")
    # R-101's heat covers C-102's reboiler (Q17 from the heavies step, Q1 the rest from the
    # hydroformylation step); the hydroformylation step's surplus goes to the trim cooler
    q17 = h("S6") - h("S7")
    out["Q17"] = {"duty": round(q17, 1)}
    out["Q1"] = {"duty": round(q_reb102 - q17, 1)}
    out["Q18"] = {"duty": round(h("S5") - h("S6") - (q_reb102 - q17), 1)}
    out["Q5"] = {"duty": round(q_c102, 1)}
    # C-102's vacuum pump: the vent from the head to 150 kPa(a), and the leak allowance
    vent, _ = isentropic(n("S14"), C102_TOP_K, state(streams["S14"], "pressure") / C102_HEAD_KPA,
                         ETA_VACUUM)
    out["P4"] = {"duty": round(vent / ETA_DRIVE + VACUUM_LEAK_KW, 1)}

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
    out["Q4"] = {"duty": round(q_r301 - q3, 1)}  # surplus LP steam exported

    # --- distillation: condenser = boil-up's latent heat + products cooled to their temperature;
    # reboiler closes each column's balance. C-401: the light ends S41 refluxed, the water S40
    # condensed once and decanted (D-007)
    v401 = {c: v * (REFLUX["C401"] + 1) for c, v in n("S41").items()}
    for c, v in n("S40").items():
        v401[c] = v401.get(c, 0.0) + v
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
    out["P5"] = {"duty": round(3 * VACUUM_LEAK_KW, 1)}  # C-401, C-402 and C-403

    # --- collection
    mix("S49", ("S9", "S14", "S31"))
    mix("S50", ("S16", "S24", "S40"))

    for sid, t in temps.items():
        out[sid] = {"temperature": round(t, 2)}
    print(f"R-101 heat {q_r101:.1f} kW; C-102 reboiler {q_reb102:.1f} kW at R = {r102:.1f} "
          f"(Rmin {r_min:.1f}, x_F {x_f:.4f}, x_D {x_d:.4f}); R-301 heat {q_r301:.1f} kW")
    # every step's energy balance: in - out = 0 with its energy streams (kW)
    for step, ins, outs, q_in, q_out in CLOSURE:
        gap = (sum(h(s) for s in ins) + sum(out[q]["duty"] for q in q_in)
               - sum(h(s) for s in outs) - sum(out[q]["duty"] for q in q_out))
        print(f"closure {step}: {gap:.1f} kW")
        if abs(gap) > 1.0:
            raise SystemExit(f"{step}: energy balance open by {gap:.1f} kW (D-009)")
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
