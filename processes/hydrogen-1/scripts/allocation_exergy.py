"""Exergy per kg of the two co-products, hydrogen (S17) and export steam (S33), for the
exergy allocation of lca/lca.yaml (DESIGN.md D-013).

Run: cheme run scripts/allocation_exergy.py

Dead state 298.15 K, 101.325 kPa. Physical exergy (h - h0) - T0 (s - s0) from CoolProp
(hydrogen: normal-hydrogen equation of state; water: IAPWS-95), the steam against liquid water
at the dead state. Chemical exergy from the standard chemical exergies of Szargut, Morris and
Steward (1988), Exergy Analysis of Thermal, Chemical, and Metallurgical Processes, Szargut's
reference environment: H2 236.09 kJ/mol, H2O(l) 0.9 kJ/mol. The 0.1 mol% N2 of the product
is neglected (below 0.01 % of its exergy).
"""

from CoolProp.CoolProp import PropsSI

T0, P0 = 298.15, 101325.0
EX_CH = {"Hydrogen": (236.09, 2.01588), "Water": (0.9, 18.01528)}  # kJ/mol, kg/kmol


def physical(fluid, T, P):  # kJ/kg
    h, s = PropsSI("H", "T", T, "P", P, fluid), PropsSI("S", "T", T, "P", P, fluid)
    h0, s0 = PropsSI("H", "T", T0, "P", P0, fluid), PropsSI("S", "T", T0, "P", P0, fluid)
    return ((h - h0) - T0 * (s - s0)) / 1000.0


def chemical(fluid):  # kJ/kg
    ex, mw = EX_CH[fluid]
    return ex * 1000.0 / mw


for name, fluid, T, P in (("H2 (S17)", "Hydrogen", 313.15, 2.85e6), ("STEAMX (S33)", "Water", 673.15, 4.3e6)):
    ph, ch = physical(fluid, T, P), chemical(fluid)
    print(f"{name}: physical {ph:.1f} + chemical {ch:.1f} = {ph + ch:.1f} kJ/kg")
