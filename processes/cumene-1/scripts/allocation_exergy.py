"""Exergy of the co-products of cumene-1 for the LCA allocation (DESIGN.md D-013).

Run with `cheme run scripts/allocation_exergy.py`; prints, writes nothing.
- Chemical exergy of each component: ideal-gas formation data of process/materials.yaml and
  Szargut's standard element exergies and entropies (Szargut, Morris and Steward 1988:
  C 410.26 kJ/mol and 5.74 J/(mol K); H2 236.09 kJ/mol and 130.68 J/(mol K)), less the Gibbs
  energy of condensation RT ln(P0/Psat) at 298.15 K (thermo vapour pressure) for the liquid
  products (cumene, heavy ends). The LPG (98 mol% propane) is taken on the gas basis (its
  vapour pressure at 298 K is above P0). Mixing terms and physical exergy (40 C, product
  pressures) are neglected (below 0.1 %).
- Product compositions: the mole fractions of S25 (cumene), S20 (LPG) and S27 (heavy ends) of
  process/flowsheet.yaml.
- LP steam: exergy added per kWh of heat raised by the R-101 interbed coolers: saturated steam
  at 250 kPa(a) made from boiler feed water at 378.15 K (ASSUMED deaerator outlet), dead state
  liquid water at 298.15 K, 101.325 kPa; IAPWS-95 through thermo.
"""
import math
from pathlib import Path

import yaml
from chemicals.iapws import iapws95_Tsat
from thermo import Chemical, IAPWS95Gas, IAPWS95Liquid

ROOT = Path(__file__).resolve().parents[1]
T0, P0, R = 298.15, 101325.0, 8.314462618
EX_EL = {"C": 410.26e3, "H": 236.09e3 / 2}     # J/mol of atoms (H from H2)
S_EL = {"C": 5.74, "H": 130.68 / 2}            # J/(mol K) of atoms
ATOMS = {"C3H8": (3, 8), "C3H6": (3, 6), "BZ": (6, 6), "CUM": (9, 12), "DIPB": (12, 18), "TIPB": (15, 24)}
CAS = {"C3H8": "74-98-6", "C3H6": "115-07-1", "BZ": "71-43-2", "CUM": "98-82-8", "DIPB": "100-18-5", "TIPB": "717-74-8"}

mat = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
flows = {s["id"]: s for s in yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text())["streams"]}


def ex_ch(cid, liquid):
    c, h = ATOMS[cid]
    ig = mat[cid]["ideal_gas"]
    dgf = ig["dHf_298"] - T0 * (ig["S_298"] - c * S_EL["C"] - h * S_EL["H"])
    ex = dgf + c * EX_EL["C"] + h * EX_EL["H"]
    if liquid:
        psat = Chemical(CAS[cid]).VaporPressure(T0)
        ex -= R * T0 * math.log(P0 / psat)
    return ex  # J/mol


def product(sid, liquid):
    z = flows[sid]["state"]["design"]["composition"]["values"]
    z = {c: v for c, v in z.items() if v > 1e-9}
    t = sum(z.values())
    ex = sum(v / t * ex_ch(c, liquid) for c, v in z.items())
    mw = sum(v / t * mat[c]["molar_mass"] for c, v in z.items())
    return ex / mw  # kJ/kg (J/mol / g/mol)


for name, sid, liquid in (("CUMENE", "S25", True), ("LPG", "S20", False), ("HEAVY", "S27", True)):
    print(f"{name}: {product(sid, liquid):.1f} kJ/kg (stream {sid})")

M_W = 18.015268e-3
dead = IAPWS95Liquid(T=T0, P=P0, zs=[1.0])
bfw = IAPWS95Liquid(T=378.15, P=0.5e6, zs=[1.0])
tsat = iapws95_Tsat(2.5e5)
stm = IAPWS95Gas(T=tsat + 0.01, P=2.5e5, zs=[1.0])  # 0.01 K above saturation: the vapour root


def hs(ph):
    return ph.H() / M_W / 1e3, ph.S() / M_W / 1e3


h0, s0 = hs(dead)
hb, sb = hs(bfw)
hg, sg = hs(stm)
q = hg - hb
ex_st = (hg - h0) - T0 * (sg - s0)
ex_bfw = (hb - h0) - T0 * (sb - s0)
print(f"LPSX: Tsat {tsat:.2f} K, heat {q:.1f} kJ/kg, exergy added {(ex_st - ex_bfw) / q * 3600:.1f} kJ per kWh of heat")
