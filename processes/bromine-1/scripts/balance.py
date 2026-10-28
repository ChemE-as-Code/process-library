"""Mass and energy balance of bromine-1 (design case), DESIGN.md D-006.

Independent of cheme: it gives the stream values that process/flowsheet.yaml carries as
`assumed` (source: scripts/balance.py) and the duties of the energy streams. Run with
`cheme run scripts/balance.py`; it writes nothing, it prints the values.

Inputs (each in DESIGN.md with its source or ASSUMED):
- product 3 750 kg/h dry bromine (30 kt/a at 8000 h, D-002), 400 ppm Cl2, 30 ppm H2O (D-002);
- brine: 4 300 mg/kg bromide, 185 000 mg/kg chloride, 30 000 mg/kg calcium, 250 mg/kg H2S
  (D-004: AGS, US 4 719 096; Ca and the mass basis ASSUMED); feed at 195 degF (US 4 719 096);
- bromide recovery 95.5 % (US 4 719 096: 95-96 % in conventional towers), all H2S oxidised to
  sulfur by chlorine (the side reaction, D-005);
- tail brine leaves at 229 degF (US 4 719 096: brine boils at 228-230 degF);
- crude bromine 2 wt-% Cl2 and 0.1 wt-% H2O, bromine water 3.5 wt-% Br2, wet bromine
  0.05 wt-% H2O, spent acid 80 wt-% H2SO4 (D-007, D-008, ASSUMED);
- overhead vapour at feed temperature + 2 K and 105 kPa(a), water activity of the brine 0.75
  (D-006, ASSUMED: no electrolyte package covers this brine, core#364).
"""

import math

M = {"H2O": 18.015, "NaCl": 58.443, "CaCl2": 110.984, "NaBr": 102.894, "H2S": 34.081,
     "Br2": 159.808, "Cl2": 70.906, "HCl": 36.461, "S": 32.065, "CaOH2": 74.092,
     "H2SO4": 98.079, "Br": 79.904, "Cl": 35.453, "Ca": 40.078}
F2K = lambda f: (f - 32.0) / 1.8 + 273.15

# --- basis -------------------------------------------------------------------------------
P = 3750.0                                   # kg/h dry bromine (D-002)
x_prod = {"Br2": 1 - 0.0004 - 0.00003, "Cl2": 0.0004, "H2O": 0.00003}
REC = 0.955                                  # bromide recovery to product (D-005)
w_Br, w_Cl, w_Ca, w_H2S = 4300e-6, 185000e-6, 30000e-6, 250e-6   # brine, mass fractions
T_brine = F2K(195.0)                         # feed brine at the tower (D-004)
T_tail = F2K(229.0)                          # tail brine leaving the tower (D-006)
T_top = T_brine + 2.0                        # overhead vapour (D-006)
P_top = 105.0                                # kPa(a)
a_w = 0.75                                   # water activity of the brine (ASSUMED)
T_cond = 303.15                              # condenser outlet and separator (D-007)
T_bp_Br2 = 331.9                             # Br2 normal boiling point
w_Cl2_crude, w_H2O_crude = 0.02, 0.001       # crude bromine (D-007)
r_Br2_ovhd = 1.0                             # kg Br2 per kg Cl2 in the C-104 overhead (D-007)
w_Br2_bw = 0.035                             # Br2 in the bromine water (D-007)
w_H2O_wet = 0.0005                           # water in wet bromine after C-104 (D-008)
acid_in, acid_out = 0.98, 0.80               # H2SO4 strength in and out of C-106 (D-008)
R_C104 = 3.0                                 # reflux ratio of C-104 (D-007)

# --- brine -------------------------------------------------------------------------------
brine = {"NaBr": w_Br * M["NaBr"] / M["Br"], "CaCl2": w_Ca * M["CaCl2"] / M["Ca"], "H2S": w_H2S}
cl_in_ca = brine["CaCl2"] * 2 * M["Cl"] / M["CaCl2"]
brine["NaCl"] = (w_Cl - cl_in_ca) * M["NaCl"] / M["Cl"]
brine["H2O"] = 1.0 - sum(brine.values())

prod = {k: P * v for k, v in x_prod.items()}
br_in = prod["Br2"] / REC                    # kg/h Br (as element) in the brine
F = br_in / w_Br                             # kg/h brine
S1 = {k: F * v for k, v in brine.items()}
n_conv = (S1["NaBr"] / M["NaBr"]) * REC      # kmol/h NaBr oxidised
n_Br2 = n_conv / 2
n_H2S = S1["H2S"] / M["H2S"]
cl2_R1, cl2_R2 = n_Br2 * M["Cl2"], n_H2S * M["Cl2"]
cl2_fresh = cl2_R1 + cl2_R2 + prod["Cl2"]

# --- bromine train ------------------------------------------------------------------------
# wet bromine (C-104 bottoms) and dryer
wet = {"Br2": prod["Br2"], "Cl2": prod["Cl2"]}
wet["H2O"] = w_H2O_wet / (1 - w_H2O_wet) * (wet["Br2"] + wet["Cl2"])
h2o_dry = wet["H2O"] - prod["H2O"]
acid = h2o_dry / (acid_in / acid_out - 1)   # kg/h 98 % acid: 0.98 a = 0.80 (a + w)
S13 = {"H2SO4": acid * acid_in, "H2O": acid * (1 - acid_in)}
S14 = {"H2SO4": S13["H2SO4"], "H2O": S13["H2O"] + h2o_dry}
# crude bromine: Cl2 and H2O fractions, the C-104 overhead takes Cl2, some Br2 and the excess water
cl2_ovhd = 0.0
for _ in range(50):
    tot = (wet["Br2"] + wet["Cl2"] + r_Br2_ovhd * cl2_ovhd + cl2_ovhd) / (1 - w_H2O_crude)
    cl2_new = w_Cl2_crude * tot - wet["Cl2"]
    if abs(cl2_new - cl2_ovhd) < 1e-9:
        break
    cl2_ovhd = cl2_new
S8 = {"Br2": wet["Br2"] + r_Br2_ovhd * cl2_ovhd, "Cl2": wet["Cl2"] + cl2_ovhd}
S8["H2O"] = w_H2O_crude * (S8["Br2"] + S8["Cl2"]) / (1 - w_H2O_crude)
S9 = {"Br2": r_Br2_ovhd * cl2_ovhd, "Cl2": cl2_ovhd, "H2O": S8["H2O"] - wet["H2O"]}

# overhead vapour S5 and bromine water S7: water from the vapour pressure over the brine
def psat_w(T):  # kPa, Antoine (water, 1-100 degC)
    t = T - 273.15
    return 10 ** (8.07131 - 1730.63 / (233.426 + t)) * 0.133322

pw = a_w * psat_w(T_top)
ratio = pw / (P_top - pw)                    # kmol H2O per kmol halogen in S5
h2o_S5 = 0.0
for _ in range(100):
    h2o_bw = h2o_S5 - S8["H2O"]
    br2_bw = w_Br2_bw / (1 - w_Br2_bw) * h2o_bw
    n_hal = (S8["Br2"] + br2_bw) / M["Br2"] + S8["Cl2"] / M["Cl2"]
    new = ratio * n_hal * M["H2O"]
    if abs(new - h2o_S5) < 1e-9:
        break
    h2o_S5 = new
S7 = {"H2O": h2o_bw, "Br2": br2_bw}
S5 = {"Br2": S8["Br2"] + S7["Br2"], "Cl2": S8["Cl2"], "H2O": h2o_S5}

# --- energy ------------------------------------------------------------------------------
cp_brine = 2.9          # kJ/kg K, ~31 wt-% NaCl/CaCl2 brine (ASSUMED)
cp_w, cp_brl, cp_brv, cp_cl2 = 4.18, 0.474, 0.226, 0.48   # kJ/kg K
L_w = lambda T: 2501.0 - 2.36 * (T - 273.15)               # kJ/kg, water latent heat (approx.)
L_br2, L_cl2 = 29960 / M["Br2"], 20410 / M["Cl2"]          # kJ/kg at the normal boiling point
# heats of reaction (aqueous, 298 K), NBS tables (Wagman et al. 1982), D-005:
dH_R1 = 2 * (-167.16) + (-2.59) - 2 * (-121.55)            # kJ/mol: 2 Br- + Cl2(g) -> 2 Cl- + Br2(aq)
dH_R2 = 2 * (-167.16) - (-39.7)                             # kJ/mol: H2S(aq) + Cl2(g) -> S + 2 H+ + 2 Cl-
dH_vap_br2_aq = 30.91 - (-2.59)                             # kJ/mol: Br2(aq) -> Br2(g)
loss = 0.03             # tower heat loss, fraction of the steam heat (ASSUMED)
h_steam = 2731.6        # kJ/kg saturated steam 350 kPa(a) (IAPWS-IF97)
h_cond = cp_w * (T_tail - 273.15)                           # condensed steam leaving with the tail brine

q = 0.0  # kW required by the tower (excluding steam)
q += F * cp_brine * (T_tail - T_brine) / 3600                    # brine heat-up
q += h2o_S5 * (L_w(T_top) + cp_w * (T_top - T_tail)) / 3600      # water leaving as vapour (from tail-brine liquid)
q += S7["H2O"] * cp_w * (T_tail - T_cond) / 3600                 # bromine water heated to tail temperature
q += cl2_fresh * cp_cl2 * (T_tail - 313.15) / 3600               # chlorine heated
# Br2 stripped from solution: the Br2 formed and the Br2 returned dissolved in the bromine water
# (the C-104 overhead S9 arrives and leaves as vapour)
q += (n_Br2 + S7["Br2"] / M["Br2"]) * dH_vap_br2_aq * 1000 / 3600
q += n_Br2 * dH_R1 * 1000 / 3600 + n_H2S * dH_R2 * 1000 / 3600   # reactions (exothermic, negative)
steam = q / ((h_steam - h_cond) * (1 - loss)) * 3600             # kg/h live steam

# tail brine
S15 = {k: v for k, v in S1.items() if k not in ("NaBr", "H2S", "NaCl")}
S15["H2O"] = S1["H2O"] + steam + S7["H2O"] + S9["H2O"] - S5["H2O"]
S15["NaCl"] = S1["NaCl"] + n_conv * M["NaCl"]
S15["NaBr"] = S1["NaBr"] - n_conv * M["NaBr"]
S15["S"] = n_H2S * M["S"]
S15["HCl"] = 2 * n_H2S * M["HCl"]
lime = n_H2S * M["CaOH2"]                                        # 2 HCl + Ca(OH)2 -> CaCl2 + 2 H2O
S17 = dict(S15)
del S17["HCl"]
S17["CaCl2"] += n_H2S * M["CaCl2"]
S17["H2O"] += 2 * n_H2S * M["H2O"]

# condenser E-102: S5 vapour at T_top -> two liquids at T_cond
q_E102 = (S5["H2O"] * (L_w(T_top) + cp_w * (T_top - T_cond))
          + S5["Br2"] * (cp_brv * (T_top - T_bp_Br2) + L_br2 + cp_brl * (T_bp_Br2 - T_cond))
          + S5["Cl2"] * (cp_cl2 * (T_top - T_cond) + L_cl2)) / 3600
# C-104: crude heated to the Br2 boiling point, overhead (Cl2, Br2, water) boiled up (1 + R) times
lat_ovhd = S9["Cl2"] * L_cl2 + S9["Br2"] * L_br2 + S9["H2O"] * L_w(320.0)
q_reb = (sum(S8.values()) * cp_brl * (T_bp_Br2 - T_cond) + (1 + R_C104) * lat_ovhd) / 3600
q_C104c = R_C104 * lat_ovhd / 3600
q_E105 = sum(wet.values()) * cp_brl * (T_bp_Br2 - T_cond) / 3600
rho_b = 1200.0          # kg/m3 brine (ASSUMED)
w_P101 = F / rho_b / 3600 * 350.0 / 0.70                         # kW: 350 kPa, eta 0.70 (ASSUMED)
w_misc = 15.0           # kW: bromine, acid and lime pumps, agitator (ASSUMED)

def show(name, d):
    tot = sum(d.values())
    comp = {k: round(v / tot, 7) for k, v in d.items() if v > 0}
    print(f"{name}: flow {tot:.2f} kg/h  {comp}")

print(f"brine mass fractions {({k: round(v, 7) for k, v in brine.items()})}")
for n, d in [("S1 brine", S1), ("S3 chlorine", {"Cl2": cl2_fresh}), ("S4 steam", {"H2O": steam}),
             ("S5 overhead", S5), ("S6 condensate", {k: S7.get(k, 0) + S8.get(k, 0) for k in S5}),
             ("S7 bromine water", S7), ("S8 crude", S8), ("S9 C-104 overhead", S9),
             ("S10 wet bromine", wet), ("S12 product", prod), ("S13 acid", S13), ("S14 spent acid", S14),
             ("S15 tail brine", S15), ("S16 lime", {"CaOH2": lime}), ("S17 neutralised tail brine", S17)]:
    show(n, d)
print(f"Cl2 fresh {cl2_fresh:.2f} kg/h = {cl2_fresh / P:.4f} kg/kg Br2 (R1 {cl2_R1:.1f}, side R2 {cl2_R2:.1f});"
      f" excess over R1 {100 * (cl2_fresh / (cl2_R1 + prod['Cl2']) - 1):.1f} %")
print(f"steam {steam:.1f} kg/h = {steam / P:.3f} kg/kg Br2; tower heat demand {q:.1f} kW;"
      f" brine heat-up {F * cp_brine * (T_tail - T_brine) / 3600:.1f} kW; reactions"
      f" {(n_Br2 * dH_R1 + n_H2S * dH_R2) * 1000 / 3600:.1f} kW")
print(f"E-102 {q_E102:.1f} kW; C-104 reboiler {q_reb:.1f} kW, condenser {q_C104c:.1f} kW; E-105 {q_E105:.1f} kW")
print(f"P-101 {w_P101:.1f} kW; misc {w_misc} kW; lime {lime:.2f} kg/h; acid {acid:.3f} kg/h")
print(f"T_brine {T_brine:.2f} K, T_tail {T_tail:.2f} K, T_top {T_top:.2f} K, pw {pw:.2f} kPa")
print(f"tail brine bromide {1e6 * S17['NaBr'] * M['Br'] / M['NaBr'] / sum(S17.values()):.0f} mg/kg;"
      f" recovery per m3 brine {prod['Br2'] / (F / rho_b):.3f} kg/m3 = {prod['Br2'] / (F / rho_b) * 0.158987 / 0.453592:.2f} lb/bbl")
# closure
tin = sum(S1.values()) + cl2_fresh + steam + lime + sum(S13.values())
tout = sum(prod.values()) + sum(S14.values()) + sum(S17.values())
print(f"overall in {tin:.2f} out {tout:.2f} kg/h")
