"""Energy balance of titanium-dioxide-1 on the propagated flowsheet (DESIGN.md D-011, L-1).

Core solves the mass balance (`cheme process propagate --fill`: the chlorine recycle and the
design specifications), but it has no condensed-phase enthalpy for a flowsheet step: the solids
(rutile, coke, FeO, silica, FeCl2) and liquid TiCl4 have no ideal-gas data, so core can neither
give the reactor heats nor the cooler, condenser and heater duties. This script reads the
flows and compositions that propagate wrote into process/flowsheet.yaml and computes:

- the temperature of the chlorine to the bed (S5, adiabatic mixing of S3 and S4);
- the heat lost by the chlorinator R-101 (inlets at their temperatures, outlet S6 at 1273 K);
- the spray quench E-101: cold crude TiCl4 (308 K, the E-102 condensate) sprayed into S6 and
  evaporated to cool it to 473 K. The quench rejects no heat itself: its outlet is above the
  TiCl4 dew point, so all the sprayed liquid evaporates, and E-102 condenses it again. The
  script prints the circulation and the dew point; the circulation is an internal loop of
  E-101/E-102/V-101, not drawn as a stream (S7 and S9 carry the net flows, DESIGN.md D-006);
- the duties of the condensers E-102 (cooling water: the quench heat and the condensation) and
  E-103 (brine), the still T-101 (reboiler on HP steam, condenser on cooling water, reflux
  ratio 1.0 ASSUMED), the TiCl4 vaporiser E-201 (HP steam), the fired TiCl4 superheater E-202
  and oxygen preheater E-203, and the oxidiser product cooler E-204;
- the lime slaker M-401 outlet temperature (S42, adiabatic slaking of the quicklime) and the
  cooling duty of the neutraliser R-401 that holds its outlet S43 at 323 K (D-010);
- the adiabatic outlet temperature of the oxidiser R-201 (S19);
- the combustion air of the thermal oxidiser X-301 for an adiabatic outlet of 1123 K (S35) and
  the power of its fan K-301 (5 kPa, fan 0.65, motor 0.95, ASSUMED).

Enthalpies are molar, referred to the elements at 298.15 K (formation enthalpy plus sensible
heat). Gases: the ideal-gas data of process/materials.yaml (chemicals 1.5.2 / thermo 0.6.1).
Solids: chemicals 1.5.2 Hfs, method CRC (the CRC Handbook of Chemistry and Physics tables
packaged in chemicals) for rutile 1317-80-2, FeO, quartz, FeCl2, CaO, Ca(OH)2 and CaCl2, method
WEBBOOK (NIST Chemistry WebBook) for Fe(OH)2, graphite 0; thermo 0.6.1 HeatCapacitySolid,
method WEBBOOK_SHOMATE (NIST WebBook Shomate equations), JANAF_FIT for graphite. FeCl2 above its
melting point (chemicals Tm 950.15 K, Tb 1296.15 K) is a vapour: in S6 its partial pressure is
about 5 kPa, so it leaves the chlorinator as gas (chemicals Hfg, method WEBBOOK, and thermo
HeatCapacityGas, method JANAF: NIST-JANAF tables); below 950 K it is solid. Liquid TiCl4:
chemicals Hfl (CRC, -804.2 kJ/mol) and thermo HeatCapacityLiquid; liquid water: chemicals Hfl
and thermo HeatCapacityLiquid (HEOS_FIT, the IAPWS-95 formulation in CoolProp). These are single
values of the packages, facts with their source (library ADR 0037); the underlying handbooks
were not read here. The dissolved scrubber salts (NaOH, NaCl, NaOCl) pass the neutraliser
unchanged and are left out of its enthalpy balance; the CaCl2 formed is counted as the solid
(its heat of solution is not in the packages and not counted, DESIGN.md D-010).

Run: cheme run scripts/energy_balance.py   (prints the duties and cross-checks)
With BALANCE_OUTPUT=<file>: writes the values the flowsheet cites (balance-output contract,
library ADR 0027).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml
from chemicals import Hfg, Hfl, Hfs, Tm
from scipy.integrate import quad
from scipy.optimize import brentq
from thermo import HeatCapacityGas, HeatCapacityLiquid, HeatCapacitySolid, VaporPressure

ROOT = Path(__file__).resolve().parents[1]
R = 8.314462618  # J/(mol K)
T0 = 298.15
REFLUX = 1.0  # T-101 reflux ratio, ASSUMED (D-006)
T_OXIDISER_OUT = 1123.15  # X-301 outlet, ASSUMED (D-009)

SOLIDS_CAS = {"TIO2": "1317-80-2", "FEO": "1345-25-1", "SIO2": "14808-60-7", "C": "7440-44-0",
              "FECL2": "7758-94-3", "CAO": "1305-78-8", "FEOH2": "18624-44-7",
              "CACL2": "10043-52-4", "CAOH2": "1305-62-0"}
TICL4_CAS = "7550-45-0"
WATER_CAS = "7732-18-5"
DISSOLVED = {"NAOH", "NACL", "NAOCL"}  # pass R-401 unchanged; left out of its balance
T_SLURRY_OUT = 323.15  # R-401 outlet, ASSUMED (D-010)
T_QUENCH_LIQUID = 308.15  # E-101 spray: crude TiCl4 condensate of E-102 (D-006)


def load(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in load("process/materials.yaml")["components"]}
SHEET = load("process/flowsheet.yaml")
STREAMS = {s["id"]: s for s in SHEET["streams"]}
MW = {k: float(v["molar_mass"]) for k, v in MATERIALS.items()}

_CPS = {k: HeatCapacitySolid(CASRN=cas) for k, cas in SOLIDS_CAS.items()}
_HFS = {k: (0.0 if k == "C" else float(Hfs(cas))) for k, cas in SOLIDS_CAS.items()}
_CPL = HeatCapacityLiquid(CASRN=TICL4_CAS)
_PSAT = VaporPressure(CASRN=TICL4_CAS)
HFL_TICL4 = float(Hfl(TICL4_CAS))
_CPW = HeatCapacityLiquid(CASRN=WATER_CAS)
HFL_WATER = float(Hfl(WATER_CAS))
_CPG_FECL2 = HeatCapacityGas(CASRN=SOLIDS_CAS["FECL2"])
_CPG_FECL2.method = "JANAF"
HFG_FECL2 = float(Hfg(SOLIDS_CAS["FECL2"]))
TM_FECL2 = float(Tm(SOLIDS_CAS["FECL2"]))


def h_gas(cid: str, T: float) -> float:
    ig = MATERIALS[cid]["ideal_gas"]
    a = ig["cp_R"]
    sens = sum(a[i] / (i + 1) * (T ** (i + 1) - T0 ** (i + 1)) for i in range(len(a))) * R
    return ig["dHf_298"] + sens


def h_solid(cid: str, T: float) -> float:
    return _HFS[cid] + quad(lambda t: _CPS[cid].T_dependent_property(t), T0, T)[0]


def h_ticl4_liquid(T: float) -> float:
    return HFL_TICL4 + quad(lambda t: _CPL.T_dependent_property(t), T0, T)[0]


def h_fecl2_gas(T: float) -> float:
    return HFG_FECL2 + quad(lambda t: _CPG_FECL2.T_dependent_property(t), T0, T)[0]


def h_water_liquid(T: float) -> float:
    return HFL_WATER + quad(lambda t: _CPW.T_dependent_property(t), T0, T)[0]


def kmol(sid: str) -> dict[str, float]:
    """Component flows of a stream in kmol/h, from its flow and composition."""
    st = STREAMS[sid]["state"]["design"]
    flow = st["flow"]["value"]
    comp = st["composition"]
    vals = comp["values"]
    if comp["basis"] == "mass_fraction":
        return {c: flow * x / MW[c] for c, x in vals.items() if x}
    mmix = sum(x * MW[c] for c, x in vals.items())
    return {c: flow / mmix * x for c, x in vals.items() if x}


def temperature_p(sid: str) -> float:
    """kPa(a) of a stream."""
    return STREAMS[sid]["state"]["design"]["pressure"]["value"]


def temperature(sid: str) -> float:
    return STREAMS[sid]["state"]["design"]["temperature"]["value"]


def enthalpy(n: dict[str, float], T: float, ticl4_liquid: float = 0.0) -> float:
    """kW of a stream's enthalpy (kmol/h x J/mol = kJ/h; / 3600 = kW); ticl4_liquid: kmol/h of the
    TiCl4 that is liquid, the rest vapour."""
    h = 0.0
    for c, x in n.items():
        if c == "FECL2" and T > TM_FECL2:
            h += x * h_fecl2_gas(T)  # vapour above the melting point (partial pressure ~5 kPa)
        elif c in SOLIDS_CAS:
            h += x * h_solid(c, T)
        elif c == "TICL4":
            liq = min(ticl4_liquid, x)
            h += liq * h_ticl4_liquid(T) + (x - liq) * h_gas(c, T)
        else:
            h += x * h_gas(c, T)
    return h / 3600.0


def enthalpy_slurry(n: dict[str, float], T: float, ticl4_liquid: bool = False,
                    lime_slaked: bool = False) -> float:
    """kW of a waste stream's enthalpy: solids, liquid water, TiCl4 (liquid or vapour); the
    dissolved scrubber salts left out (they pass R-401 unchanged). lime_slaked: the CaO counted
    as Ca(OH)2, taking one water each (the model carries the slaked lime as CaO + H2O)."""
    h = 0.0
    for c, x in n.items():
        if c in DISSOLVED:
            continue
        if c == "H2O":
            h += x * h_water_liquid(T)
        elif c == "TICL4":
            h += x * (h_ticl4_liquid(T) if ticl4_liquid else h_gas(c, T))
        elif c == "CAO" and lime_slaked:
            h += x * (h_solid("CAOH2", T) - h_water_liquid(T))
        elif c in SOLIDS_CAS:
            h += x * h_solid(c, T)
        else:
            raise ValueError(f"no condensed-phase enthalpy for {c} in a waste stream")
    return h / 3600.0


def dew_point_ticl4(p_kpa: float) -> float:
    """K at which pure TiCl4's vapour pressure equals the partial pressure p_kpa."""
    return brentq(lambda T: _PSAT(T) / 1000.0 - p_kpa, 250.0, 600.0)


def adiabatic(n: dict[str, float], H: float, lo: float = 300.0, hi: float = 3000.0) -> float:
    return brentq(lambda T: enthalpy(n, T) - H, lo, hi)


def raoult_vapour(n: dict[str, float], T: float, P_kpa: float) -> float:
    """kmol/h of TiCl4 left in the gas over liquid TiCl4 (the permanent gases insoluble)."""
    inert = sum(x for c, x in n.items() if c not in SOLIDS_CAS and c != "TICL4")
    p = _PSAT(T) / 1000.0
    return inert * p / (P_kpa - p)


def main() -> None:
    out: dict[str, dict] = {}
    duty: dict[str, float] = {}
    n = {sid: kmol(sid) for sid in ("S1", "S2", "S3", "S4", "S5", "S6", "S8", "S9", "S12", "S13",
                                     "S14", "S15", "S17", "S19", "S21", "S33", "S34", "S40",
                                     "S41", "S43")}

    # M-101: chlorine to the bed, adiabatic mixing of make-up and recycle
    h_in = enthalpy(n["S3"], temperature("S3")) + enthalpy(n["S4"], temperature("S4"))
    t5 = adiabatic(n["S5"], h_in)
    out["S5"] = {"temperature": round(t5, 2)}

    # R-101: the chlorinator's heat to ambient (positive: the bed makes more heat than it needs)
    h_feed = enthalpy(n["S1"], temperature("S1")) + enthalpy(n["S2"], temperature("S2")) + h_in
    h6 = enthalpy(n["S6"], temperature("S6"))
    duty["Q1"] = h_feed - h6

    # E-101: spray quench to 473 K with crude TiCl4 condensate at 308 K. All the sprayed liquid
    # evaporates (outlet above the dew point), so the quench heat q_quench leaves in E-102,
    # which condenses the circulating TiCl4 again; S7 has S6's net flows.
    q_quench = h6 - enthalpy(n["S6"], 473.15)
    dh_spray = h_gas("TICL4", 473.15) - h_ticl4_liquid(T_QUENCH_LIQUID)  # J/mol
    circ = q_quench * 3600.0 / dh_spray  # kmol/h of TiCl4 sprayed and evaporated
    gas6 = sum(x for c, x in n["S6"].items() if c not in SOLIDS_CAS)  # FeCl2 solid at 473 K
    p7 = temperature_p("S7")
    y_net = n["S6"]["TICL4"] / gas6
    y_q = (n["S6"]["TICL4"] + circ) / (gas6 + circ)
    t_dew_net, t_dew_q = dew_point_ticl4(y_net * p7), dew_point_ticl4(y_q * p7)

    # E-102 (cooling water to 308 K) and E-103 (brine to 263 K): TiCl4 condensed by Raoult at
    # 308 K, at 263 K to the separator's recovery (V101); the fines pass with S9
    n9 = n["S9"]
    v308 = raoult_vapour(n9, 308.15, STREAMS["S10"]["state"]["design"]["pressure"]["value"])
    liq308 = n9["TICL4"] - v308
    liq263 = n["S12"].get("TICL4", 0.0)
    h9 = enthalpy(n9, temperature("S9"))
    h10 = enthalpy(n9, 308.15, ticl4_liquid=liq308)
    h11 = enthalpy(n9, 263.15, ticl4_liquid=liq263)
    duty["Q3"] = q_quench + h9 - h10
    duty["Q4"] = h10 - h11
    v263 = raoult_vapour(n9, 263.15, STREAMS["S11"]["state"]["design"]["pressure"]["value"])

    # T-101: reboiler and condenser at reflux REFLUX (distillate liquid at the boiling point)
    tb = 409.6
    hvap_tb = h_gas("TICL4", tb) - h_ticl4_liquid(tb)
    d = n["S14"]["TICL4"]
    q_cond = (REFLUX + 1.0) * d * hvap_tb / 3600.0
    h12 = enthalpy(n["S12"], temperature("S12"), ticl4_liquid=n["S12"]["TICL4"])
    h14 = enthalpy(n["S14"], temperature("S14"), ticl4_liquid=d)
    h15 = enthalpy(n["S15"], temperature("S15"), ticl4_liquid=n["S15"].get("TICL4", 0.0))
    duty["Q6"] = q_cond
    duty["Q5"] = h14 + h15 + q_cond - h12

    # E-201 vaporiser (steam), E-202 superheater (fired), E-203 O2 preheater (fired)
    t16, t18, t22 = temperature("S16"), temperature("S18"), temperature("S22")
    duty["Q7"] = enthalpy(n["S14"], t16) - h14
    duty["Q8"] = enthalpy(n["S14"], t18) - enthalpy(n["S14"], t16)
    duty["Q9"] = enthalpy(n["S17"], t22) - enthalpy(n["S17"], temperature("S17"))

    # R-201 adiabatic; E-204 to 423 K
    h_ox = enthalpy(n["S14"], t18) + enthalpy(n["S17"], t22)
    t19 = adiabatic(n["S19"], h_ox)
    out["S19"] = {"temperature": round(t19, 2)}
    duty["Q10"] = h_ox - enthalpy(n["S19"], temperature("S20"))

    # X-301: air for an adiabatic outlet of 1123 K
    vent = dict(n["S33"])
    xi = 0.999 * vent.get("CO", 0.0)
    reacted = dict(vent)
    reacted["CO"] = vent.get("CO", 0.0) - xi
    reacted["O2"] = vent.get("O2", 0.0) - 0.5 * xi
    reacted["CO2"] = vent.get("CO2", 0.0) + xi
    air = {"N2": 0.7812, "O2": 0.2095, "AR": 0.0093}
    h_air = lambda T: sum(x * h_gas(c, T) for c, x in air.items())  # noqa: E731  J/mol
    a = (enthalpy(reacted, T_OXIDISER_OUT) - enthalpy(vent, temperature("S33"))) * 3600.0 / (
        h_air(temperature("S36")) - h_air(T_OXIDISER_OUT))
    m_air = a * sum(x * MW[c] for c, x in air.items())
    out["S35"] = {"flow": round(m_air, 3)}
    # K-301: fan power, 5 kPa rise at 298 K, fan 0.65 x motor 0.95 (ASSUMED, D-009)
    v_air = a * 1000.0 * R * temperature("S35") / (temperature_p("S35") * 1000.0) / 3600.0  # m3/s
    duty["P3"] = v_air * (STREAMS["S36"]["state"]["design"]["pressure"]["value"]
                          - STREAMS["S35"]["state"]["design"]["pressure"]["value"]) / (0.65 * 0.95)

    # M-401: adiabatic slaking, CaO + H2O(l) -> Ca(OH)2(s), in the slaking water
    n_cao, n_w = n["S40"]["CAO"], n["S41"]["H2O"]
    h_lime_in = enthalpy_slurry(n["S40"], temperature("S40")) + enthalpy_slurry(n["S41"], temperature("S41"))
    t42 = brentq(lambda T: enthalpy_slurry({"CAO": n_cao, "H2O": n_w}, T, lime_slaked=True) - h_lime_in,
                 280.0, 373.0)
    out["S42"] = {"temperature": round(t42, 2)}
    q_slake = (enthalpy_slurry({"CAO": n_cao, "H2O": n_w}, T0)
               - enthalpy_slurry({"CAO": n_cao, "H2O": n_w}, T0, lime_slaked=True))
    # R-401: neutraliser held at 323 K by a cooling-water coil (the hot blow-over S8 at 473 K, the
    # still bottoms S15 with liquid TiCl4 at 413 K, the scrubber liquor S34 and the hot slurry S42
    # in; the reactions HYD_LIME, FECL_LIME on the slaked lime; CaCl2 counted as the solid)
    h_r401_in = (enthalpy_slurry(n["S8"], temperature("S8"))
                 + enthalpy_slurry(n["S15"], temperature("S15"), ticl4_liquid=True)
                 + enthalpy_slurry(n["S34"], temperature("S34")) + h_lime_in)
    duty["Q11"] = h_r401_in - enthalpy_slurry(n["S43"], T_SLURRY_OUT, lime_slaked=True)
    water43 = n["S43"]["H2O"] * MW["H2O"]  # kg/h
    rise = duty["Q11"] / (water43 * _CPW.T_dependent_property(T_SLURRY_OUT) / MW["H2O"] / 3600.0)

    for q, v in duty.items():
        out[q] = {"duty": round(v, 1)}

    # --- report ------------------------------------------------------------------------------
    product_t = STREAMS["S21"]["state"]["design"]["flow"]["value"] / 1000.0
    print(f"S5 chlorine to the bed: {t5:.2f} K;  S19 oxidiser outlet (adiabatic): {t19:.2f} K")
    print(f"S35 combustion air: {m_air:.1f} kg/h ({a:.2f} kmol/h)")
    print(f"E-101 quench: {q_quench:.1f} kW taken up by {circ:.1f} kmol/h ({circ * MW['TICL4'] / 1000:.1f} t/h) "
          f"of crude TiCl4 sprayed at {T_QUENCH_LIQUID:.2f} K and evaporated; TiCl4 dew point at "
          f"{p7:.0f} kPa(a) {t_dew_net:.1f} K without and {t_dew_q:.1f} K with the evaporated spray "
          "(outlet 473.15 K: no liquid left); the heat leaves in E-102 (Q3)")
    print(f"S42 lime slurry (adiabatic slaker): {t42:.2f} K, slaking heat {q_slake:.1f} kW; "
          f"R-401 cooling to {T_SLURRY_OUT:.2f} K: {duty['Q11']:.1f} kW "
          f"(uncooled, the slurry water would heat by about {rise:.0f} K)")
    names = {"Q1": "R-101 heat to ambient", "Q3": "E-102 condenser incl. quench heat (CW)",
             "Q4": "E-103 after-condenser (brine)", "Q5": "T-101 reboiler (HP steam)",
             "Q6": "T-101 condenser (CW)", "Q7": "E-201 vaporiser (HP steam)",
             "Q8": "E-202 TiCl4 superheater (fired)", "Q9": "E-203 O2 preheater (fired)",
             "Q10": "E-204 product cooler (CW)", "Q11": "R-401 neutraliser cooling (CW)",
             "P3": "K-301 combustion air fan (power)"}
    for q, v in duty.items():
        print(f"{q:4s} {names[q]:34s} {v:10.1f} kW  {v * 3.6 / product_t / 1000:6.3f} GJ/t TiO2")
    steam = duty["Q5"] + duty["Q7"]
    fired = duty["Q8"] + duty["Q9"]
    print(f"steam {steam * 3.6 / product_t / 1000:.2f} GJ/t, fired heat {fired * 3.6 / product_t / 1000:.2f} GJ/t "
          "(BREF LVIC-S Table 3.16, 1999 averages up to oxidation: steam 2.4, gas 3.2 GJ/t)")
    print(f"cross-check: TiCl4 heat of vaporization at 409.6 K {hvap_tb / 1000:.2f} kJ/mol "
          "(chemicals 1.5.2 CRC_HVAP_TB: 36.2)")
    rec = 1.0 - v263 / n9["TICL4"]
    print(f"cross-check: Raoult recovery of TiCl4 at 263.15 K {rec:.5f} (V101 specifies 0.997); "
          f"at 308.15 K {1.0 - v308 / n9['TICL4']:.4f}")
    print(f"cross-check: CHLOR heat of reaction {(h_gas('TICL4', T0) + h_gas('CO', T0) + 0.5 * h_gas('CO2', T0) - h_solid('TIO2', T0)) / 1000:.3f} kJ/mol, "
          f"FECL {(h_solid('FECL2', T0) + h_gas('CO', T0) - h_solid('FEO', T0)) / 1000:.3f} (FeCl2 solid), "
          f"OXID {(h_solid('TIO2', T0) - h_gas('TICL4', T0)) / 1000:.3f}")
    write_balance_output({"design": out})


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
    main()
