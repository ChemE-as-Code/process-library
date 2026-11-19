"""Exergy of the co-products of acrylic-acid-1 for the LCA allocation (DESIGN.md D-012).

Run with `cheme run scripts/allocation_exergy.py`; prints, writes nothing. It reads the design
case of process/flowsheet.yaml, so rerun it and update lca/lca.yaml when the streams change.

Dead state 298.15 K, 101.325 kPa (the method of cumene-1 and methanol-1).
- Glacial acrylic acid (S27): standard chemical exergy of acrylic acid and acetic acid from the
  ideal-gas formation data of process/materials.yaml and Szargut's element exergies and entropies
  (Szargut, Morris and Steward 1988, as in methanol-1's script: C 410.26, H2 236.09, O2 3.97
  kJ/mol; C 5.74, H2 130.68, O2 205.15 J/(mol K)), less the Gibbs energy of condensation
  RT ln(P0/Psat) at 298.15 K (thermo vapour pressure); the 200 ppm MEHQ is counted at acrylic
  acid's value per kg (no formation data used for it); mixing and physical exergy neglected.
- HP steam export (STMX): exergy added per kWh of heat raised in the reactors' salt coolers:
  saturated steam at 2500 kPa(a) made from boiler feed water at 378.15 K (ASSUMED deaerator
  outlet, as cumene-1 and methanol-1), IAPWS-95 through thermo.
"""
import math
from pathlib import Path

import yaml
from chemicals.iapws import iapws95_Tsat
from thermo import Chemical, IAPWS95Gas, IAPWS95Liquid

ROOT = Path(__file__).resolve().parents[1]
T0, P0, R = 298.15, 101325.0, 8.314462618
EX_EL = {"C": 410.26e3, "H": 236.09e3 / 2, "O": 3.97e3 / 2}    # J/mol of atoms
S_EL = {"C": 5.74, "H": 130.68 / 2, "O": 205.15 / 2}            # J/(mol K) of atoms
ATOMS = {"AA": {"C": 3, "H": 4, "O": 2}, "HAC": {"C": 2, "H": 4, "O": 2}}
CAS = {"AA": "79-10-7", "HAC": "64-19-7"}

mat = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
flows = {s["id"]: s for s in yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text())["streams"]}


def ex_liquid(cid):
    ig = mat[cid]["ideal_gas"]
    at = ATOMS[cid]
    dgf = ig["dHf_298"] - T0 * (ig["S_298"] - sum(n * S_EL[e] for e, n in at.items()))
    ex = dgf + sum(n * EX_EL[e] for e, n in at.items())
    psat = Chemical(CAS[cid]).VaporPressure(T0)
    return ex - R * T0 * math.log(P0 / psat)    # J/mol


z = flows["S27"]["state"]["design"]["composition"]["values"]
mw = {k: mat[k]["molar_mass"] for k in z}
mass = {k: v * mw[k] for k, v in z.items() if v > 0}
total = sum(mass.values())
ex_aa = ex_liquid("AA") / mat["AA"]["molar_mass"]           # kJ/kg
ex_hac = ex_liquid("HAC") / mat["HAC"]["molar_mass"]
ex_product = sum(m / total * (ex_hac if k == "HAC" else ex_aa) for k, m in mass.items())
print(f"acrylic acid (liquid) {ex_aa:.1f} kJ/kg, acetic acid {ex_hac:.1f} kJ/kg")
print(f"PRODUCT (S27): {ex_product:.1f} kJ/kg")

M_W = 18.015268e-3
dead = IAPWS95Liquid(T=T0, P=P0, zs=[1.0])
bfw = IAPWS95Liquid(T=378.15, P=3.0e6, zs=[1.0])
tsat = iapws95_Tsat(2.5e6)
stm = IAPWS95Gas(T=tsat + 0.01, P=2.5e6, zs=[1.0])  # 0.01 K above saturation: the vapour root


def hs(ph):
    return ph.H() / M_W / 1e3, ph.S() / M_W / 1e3


h0, s0 = hs(dead)
hb, sb = hs(bfw)
hg, sg = hs(stm)
q = hg - hb
ex_st = (hg - h0) - T0 * (sg - s0)
ex_bfw = (hb - h0) - T0 * (sb - s0)
print(f"STMX: Tsat {tsat:.2f} K, heat {q:.1f} kJ/kg, exergy added {(ex_st - ex_bfw) / q * 3600:.1f} kJ per kWh of heat")
