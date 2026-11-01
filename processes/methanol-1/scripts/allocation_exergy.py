"""Exergy of the co-products of methanol-1 for the LCA allocation (DESIGN.md D-015).

Run with `cheme run scripts/allocation_exergy.py`; prints, writes nothing. It reads the design
case of process/flowsheet.yaml, so rerun it and update lca/lca.yaml when the streams change.

Dead state 298.15 K, 101.325 kPa.
- Standard chemical exergies: core's table (Szargut, Morris and Steward 1988, model II) for H2,
  CO, CO2, CH4, N2, H2O. Methanol is not in that table: its value is derived as aniline-1's, from
  the ideal-gas formation data of process/materials.yaml and Szargut's element exergies (C 410.26,
  H2 236.09, O2 3.97 kJ/mol; element entropies C 5.74, H2 130.68, O2 205.15 J/(mol K)), less the
  Gibbs energy of condensation RT ln(P0/Psat) at 298.15 K for the liquid (thermo vapour pressure).
- MEOH (S18): liquid methanol and water with the ideal mixing term; the dissolved gases of the
  simulated S18 (traces below 2e-6) with their gas values; physical exergy at 313 K / 300 kPa
  neglected (below 0.01 %).
- PURGE (S11; not a co-product, its exergy is only for the alternative shown) and FUELGAS (S14 + S16,
  by flow): ideal-gas mixtures: chemical exergy with the
  mixing term plus the pressure exergy RT0 ln(P/P0); the thermal part at 313-315 K is neglected
  (below 0.01 %). Dissolved or condensable parts are counted as gas.
- MPS: exergy added per kWh of heat raised in R-101: saturated steam at 2800 kPa(a) made from
  boiler feed water at 378.15 K (ASSUMED deaerator outlet, as aniline-1; not in this flowsheet),
  against liquid water at the dead state; IAPWS-95 through CoolProp. This is what lca.yaml
  allocates by. Core's dataset also records a Carnot value on the product:MPS exchange (isothermal
  heat at Tsat, no feed water heating), the upper bound this script checks against.
"""
import math
from pathlib import Path

import yaml
from chemeascode.domains.process import exergy
from CoolProp.CoolProp import PropsSI
from thermo import Chemical

T0, P0_KPA = exergy.dead_state()
P0 = P0_KPA * 1000.0
R = exergy.R  # kJ/(kmol K)
ROOT = Path(__file__).resolve().parent.parent

materials = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())["components"]
streams = {s["id"]: s for s in yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text())["streams"]}
MW = {c["id"]: c["molar_mass"] for c in materials}
CAS = {c["id"]: c["cas"] for c in materials}
METHANOL = next(c for c in materials if c["id"] == "CH3OH")["ideal_gas"]

# methanol, kJ/kmol
S_elements = 5.74 + 2 * 130.68 + 0.5 * 205.15
dGf_g = METHANOL["dHf_298"] - T0 * (METHANOL["S_298"] - S_elements)  # J/mol
ex_elements = (410.26 + 2 * 236.09 + 0.5 * 3.97) * 1000.0  # J/mol = kJ/kmol
EX_MEOH_GAS = dGf_g + ex_elements
psat = Chemical("methanol").VaporPressure(T0)
EX_MEOH_LIQ = EX_MEOH_GAS - R * 1000.0 * T0 * math.log(P0 / psat) / 1000.0
print(f"methanol: dGf(g) {dGf_g / 1e3:.2f} kJ/mol, Psat(298 K) {psat:.0f} Pa, ex_ch(g) {EX_MEOH_GAS / 1e3:.1f}, ex_ch(l) {EX_MEOH_LIQ / 1e3:.1f} kJ/mol")


def state(sid):
    return streams[sid]["state"]["design"]


def specific(sid, phase):
    """Exergy of a stream, kJ/kg, and its flow, kg/h."""
    st = state(sid)
    xs = {k: v for k, v in st["composition"]["values"].items() if v > 0}
    total = 0.0
    for k, x in xs.items():
        if k == "CH3OH":
            e = EX_MEOH_LIQ if phase == "liquid" else EX_MEOH_GAS
        else:
            e = exergy.standard(CAS[k], phase)
            if e is None:
                # dissolved gas in the liquid product (simulated traces, H2 .. N2 below 2e-6 in
                # S18): the table has no liquid value, so its gas value is used
                e = exergy.standard(CAS[k], "gas")
        total += x * e
    total += R * T0 * sum(x * math.log(x) for x in xs.values())
    if phase == "gas":
        total += R * T0 * math.log(st["pressure"]["value"] / P0_KPA)
    mw = sum(x * MW[k] for k, x in xs.items())
    return total / mw, st["flow"]["value"]


ex_meoh, m_meoh = specific("S18", "liquid")
print(f"MEOH (S18): {ex_meoh:.1f} kJ/kg, {m_meoh:.1f} kg/h")

ex_purge, m_purge = specific("S11", "gas")
print(f"PURGE (S11): {ex_purge:.1f} kJ/kg, {m_purge:.1f} kg/h")

ex14, m14 = specific("S14", "gas")
ex16, m16 = specific("S16", "gas")
m_fuel = m14 + m16
ex_fuel = (ex14 * m14 + ex16 * m16) / m_fuel
print(f"FUELGAS (S14 {ex14:.1f}, S16 {ex16:.1f} kJ/kg): {ex_fuel:.1f} kJ/kg, {m_fuel:.1f} kg/h")

# steam, per kWh of heat (saturated vapour by quality, never by a phase model at Tsat, which can
# land on the liquid root)
P_STEAM, P_BFW, T_BFW = 2.8e6, 3.0e6, 378.15


def hs(**state):
    (k1, v1), (k2, v2) = state.items()
    return PropsSI("H", k1, v1, k2, v2, "Water") / 1e3, PropsSI("S", k1, v1, k2, v2, "Water") / 1e3  # kJ/kg, kJ/(kg K)


h0, s0 = hs(T=T0, P=P0)
hb, sb = hs(T=T_BFW, P=P_BFW)
hg, sg = hs(P=P_STEAM, Q=1)
Tsat = PropsSI("T", "P", P_STEAM, "Q", 1, "Water")
rho_vapour = PropsSI("D", "P", P_STEAM, "Q", 1, "Water")
ex_per_kwh = (((hg - h0) - T0 * (sg - s0)) - ((hb - h0) - T0 * (sb - s0))) / (hg - hb) * 3600.0
carnot = (1.0 - T0 / Tsat) * 3600.0
print(f"MPS: Tsat {Tsat:.2f} K, vapour {rho_vapour:.2f} kg/m3, h {hg:.1f} kJ/kg, {ex_per_kwh:.1f} kJ per kWh of heat; Carnot at Tsat {carnot:.1f}")
assert rho_vapour < 50.0, "not the vapour: density of a liquid"
assert 0.0 < ex_per_kwh < carnot, "exergy per kWh of heat must stay below the Carnot factor at Tsat"
q_kw = streams["Q4"]["state"]["design"]["duty"]["value"]

flows = {
    "MEOH": ex_meoh * m_meoh,
    "MPS": ex_per_kwh * q_kw,
    "PURGE": ex_purge * m_purge,
    "FUELGAS": ex_fuel * m_fuel,
}
total = sum(flows.values())
rest = total - flows["PURGE"]
# the study's allocation: the purge is not a co-product (D-015)
for name, value in flows.items():
    if name != "PURGE":
        print(f"share {name}: {value / rest:.4%} ({value / 3600.0 / 1000.0:.1f} MW exergy)")
# the rejected alternative, stated in lca.yaml and D-015: the purge as a co-product
for name, value in flows.items():
    print(f"alternative with purge as co-product, share {name}: {value / total:.4%} ({value / 3600.0 / 1000.0:.1f} MW exergy)")
