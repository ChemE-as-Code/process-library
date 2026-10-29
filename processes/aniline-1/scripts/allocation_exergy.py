"""Exergy of the co-products of aniline-1 for the LCA allocation (DESIGN.md D-013).

Run with `cheme run scripts/allocation_exergy.py`; prints, writes nothing.
- Aniline (liquid, 313.15 K, 300 kPa): standard chemical exergy from the ideal-gas formation
  data of process/materials.yaml (CRC) and Szargut's standard element exergies (Szargut,
  Morris and Steward 1988: C 410.26, H2 236.09, N2 0.72 kJ/mol; element entropies C 5.74,
  H2 130.68, N2 191.61 J/(mol K)), less the Gibbs energy of condensation RT ln(P0/Psat) at
  298.15 K (thermo vapour pressure); the physical exergy at 313 K / 300 kPa is neglected
  (below 0.01 %); the 0.05 wt% water is counted as aniline.
- MP steam: exergy per kWh of heat raised in E-103: saturated steam at 1500 kPa(a) made from
  boiler feed water at 378.15 K (ASSUMED deaerator outlet), against liquid water at the dead
  state 298.15 K, 101.325 kPa; IAPWS-95 through thermo.
"""
import math

from thermo import Chemical, IAPWS95Gas, IAPWS95Liquid

T0, P0 = 298.15, 101325.0
R = 8.314462618

# aniline
dHf_g, S_g = 87500.0, 317.9                       # J/mol, J/(mol K), materials.yaml
S_el = 6 * 5.74 + 3.5 * 130.68 + 0.5 * 191.61
dGf_g = dHf_g - T0 * (S_g - S_el)
ex_el = 6 * 410.26e3 + 3.5 * 236.09e3 + 0.5 * 0.72e3
psat = Chemical("aniline").VaporPressure(T0)
ex_anl_l = dGf_g + ex_el - R * T0 * math.log(P0 / psat)   # J/mol
mw = 93.126
print(f"aniline: dGf(g) {dGf_g/1e3:.2f} kJ/mol, Psat(298 K) {psat:.1f} Pa, ex_ch(l) {ex_anl_l/1e3:.1f} kJ/mol = {ex_anl_l/mw:.1f} kJ/kg")

# steam per kWh of heat
M_W = 18.015268e-3  # kg/mol
dead = IAPWS95Liquid(T=T0, P=P0, zs=[1.0])
bfw = IAPWS95Liquid(T=378.15, P=1.7e6, zs=[1.0])
from chemicals.iapws import iapws95_Tsat
Tsat = iapws95_Tsat(1.5e6)
stm = IAPWS95Gas(T=Tsat, P=1.5e6, zs=[1.0])
def hs(ph):
    return ph.H() / M_W / 1e3, ph.S() / M_W / 1e3   # kJ/kg, kJ/(kg K)
h0, s0 = hs(dead); hb, sb = hs(bfw); hg, sg = hs(stm)
q = hg - hb
ex_st = (hg - h0) - T0 * (sg - s0)
ex_bfw = (hb - h0) - T0 * (sb - s0)
per_kwh = (ex_st - ex_bfw) / q * 3600.0
print(f"steam: Tsat {Tsat:.2f} K, heat {q:.1f} kJ/kg, ex steam {ex_st:.1f} kJ/kg, ex BFW {ex_bfw:.1f} kJ/kg, "
      f"exergy added per kWh of heat {per_kwh:.1f} kJ/kWh")
