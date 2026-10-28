"""Mass and energy balance of hydrogen-bromide-1 (design case), DESIGN.md D-006.

Independent of cheme: it gives the stream values that process/flowsheet.yaml carries as
`assumed` (source: scripts/balance.py) and the duties of the energy streams. Run with
`cheme run scripts/balance.py`; it writes nothing, it prints the values.

Inputs (each in DESIGN.md with its source or ASSUMED):
- product: 1 000 kg/h HBr (100 %) as 48.0 wt-% hydrobromic acid (D-002);
- liquid bromine, taken as pure Br2 (D-003); hydrogen as delivered by hydrogen-1 (S17 there:
  99.9 mol-% H2, 0.1 mol-% N2, 2850 kPa(a), 313 K) (D-003);
- hydrogen excess 5 mol-% over Br2 (D-004); burner R101 converts 99.97 % of the Br2, the
  activated-carbon finishing bed R102 the rest (D-005);
- bromine vaporised at 300 kPa(a) and superheated to 378 K (D-007);
- burner gas leaves R101 at 448 K, the graphite cooler E102 at 333 K (D-007);
- absorber recovery 99.5 % of the HBr, scrubber vent 5 mg HBr/Nm3 (D-008);
- integral heat of solution of HBr(g) to 48 wt-% acid -72.0 kJ/mol (D-009).
Ideal-gas heat capacities and formation enthalpies are the ones `cheme chemistry thermo`
prints (ATcT, Poling 5th ed.), so that this balance and `cheme process reactors` agree.
"""

M = {"HBr": 80.912, "H2": 2.016, "Br2": 159.808, "N2": 28.013, "H2O": 18.015}
# cp/R = a0 + a1 T + a2 T^2 + a3 T^3 + a4 T^4 (Poling 5th ed., via cheme chemistry thermo)
CP = {
    "HBr": [3.842, -0.003098, 9.17e-06, -1.032e-08, 4.26e-12],
    "H2": [2.883, 0.003681, -7.72e-06, 6.92e-09, -2.13e-12],
    "Br2": [3.212, 0.00716, -1.528e-05, 1.445e-08, -4.99e-12],
    "N2": [3.539, -0.000261, 7e-08, 1.57e-09, -9.9e-13],
    "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
}
# kJ/kmol, ideal gas, 298.15 K (ATcT via cheme chemistry thermo); Br2(l) is the reference state
HF = {"HBr": -35850.0, "Br2": 30880.0, "H2O": -241822.0}
R = 8.314462618
T0 = 298.15


def dh(comp, t):
    """Ideal-gas sensible enthalpy from T0 to t, kJ/kmol."""
    a = CP[comp]
    f = lambda x: sum(a[i] * x ** (i + 1) / (i + 1) for i in range(5))
    return R * (f(t) - f(T0))


def gas_h(kmol, t):
    """Formation + sensible enthalpy of an ideal-gas mixture, kJ/h."""
    return sum(n * (HF.get(c, 0.0) + dh(c, t)) for c, n in kmol.items())


def mass(kmol):
    return {c: n * M[c] for c, n in kmol.items()}


def show(name, kmol, t, p):
    m = mass(kmol)
    tot = sum(m.values())
    frac = {c: round(v / tot, 7) for c, v in m.items() if v > 0}
    print(f"{name}: T {t:.2f} K, p {p:.1f} kPa(a), flow {tot:.3f} kg/h, mass fractions {frac}")
    return tot


# --- inputs ---------------------------------------------------------------------------
HBR = 1000.0                # kg/h HBr (100 %) in the product acid (D-002)
W_HBR = 0.480               # mass fraction HBr (D-002)
Y_N2_H2FEED = 0.001         # hydrogen-1 S17: 99.9 mol-% H2, 0.1 mol-% N2 (D-003)
EXCESS_H2 = 0.05            # D-004
X_BURNER = 0.9997           # Br2 conversion in R101 (D-005, US 3 988 427 Example)
T_BR2, P_BR2 = 378.15, 300.0         # vaporiser outlet (D-007)
T_H2 = 313.15
T_R101, T_E102 = 448.15, 333.15      # D-007
REC_ABS = 0.995             # D-008
VENT_HBR_MG_NM3 = 5.0       # D-008
T_ABS, P_ABS = 313.15, 200.0         # absorber acid and top gas (D-008)
T_SCR, P_SCR = 303.15, 190.0         # scrubber top, vent saturated with water here (D-008)
PSAT = {313.15: 7.385, 303.15: 4.247}  # kPa, water (IAPWS-IF97), dilute acid taken as water
CP_ACID = 2.10              # kJ/(kg K), 48 wt-% acid, ASSUMED (D-009)
DH_SOL = -72000.0           # kJ/kmol HBr(g) -> 48 wt-% acid at 298.15 K, ASSUMED (D-009)
DH_VAP = 43990.0            # kJ/kmol water at 298.15 K (IAPWS-IF97)
H_LPS_LATENT = 2120.0       # kJ/kg, condensing LP steam 450 kPa(a) (IAPWS-IF97), D-007
RHO_ACID = 1490.0           # kg/m3, 48 wt-% acid (Wikipedia "Hydrobromic acid", infobox)

# --- product, feeds and vent ----------------------------------------------------------
acid_kg = HBR / W_HBR
n_hbr_acid = HBR / M["HBr"]
n_w_acid = (acid_kg - HBR) / M["H2O"]

n_hbr_vent = 0.0
for _ in range(30):
    n_hbr = n_hbr_acid + n_hbr_vent
    n_br2 = n_hbr / 2
    n_h2 = n_br2 * (1 + EXCESS_H2)
    n_n2 = n_h2 * Y_N2_H2FEED / (1 - Y_N2_H2FEED)
    n_h2_ex = n_h2 - n_br2
    y_w = PSAT[T_SCR] / P_SCR
    n_w_vent = (n_h2_ex + n_n2) * y_w / (1 - y_w)
    nm3 = (n_h2_ex + n_n2 + n_w_vent) * 22.414      # Nm3/h (273.15 K, 101.325 kPa)
    n_hbr_vent = nm3 * VENT_HBR_MG_NM3 * 1e-6 / M["HBr"]

feed_br2 = {"Br2": n_br2}
feed_h2 = {"H2": n_h2, "N2": n_n2}
n_br2_left = n_br2 * (1 - X_BURNER)
burner = {"HBr": 2 * (n_br2 - n_br2_left), "Br2": n_br2_left, "H2": n_h2 - (n_br2 - n_br2_left), "N2": n_n2}
fin = {"HBr": n_hbr, "H2": n_h2_ex, "N2": n_n2}

y_w_abs = PSAT[T_ABS] / P_ABS
n_w_tail = (n_h2_ex + n_n2) * y_w_abs / (1 - y_w_abs)
tail = {"HBr": n_hbr * (1 - REC_ABS), "H2": n_h2_ex, "N2": n_n2, "H2O": n_w_tail}
vent = {"HBr": n_hbr_vent, "H2": n_h2_ex, "N2": n_n2, "H2O": n_w_vent}
n_dmw = n_w_acid + n_w_vent             # no water enters with the feeds or forms
weak = {"HBr": tail["HBr"] - vent["HBr"], "H2O": n_dmw + n_w_tail - n_w_vent}
acid = {"HBr": n_hbr_acid, "H2O": n_w_acid}

print("== streams (design case) ==")
show("S1 liquid bromine feed", feed_br2, 298.15, 400.0)
show("S2 bromine vapour", feed_br2, T_BR2, P_BR2)
show("S3 hydrogen feed", feed_h2, T_H2, 2850.0)
show("S4 burner gas", burner, T_R101, 250.0)
show("S5 finished gas", fin, T_R101, 240.0)
show("S6 cooled HBr gas", fin, T_E102, 230.0)
show("S7 acid from absorber", acid, T_ABS, P_ABS)
show("S8 absorber tail gas", tail, T_ABS, P_ABS)
show("S9 weak acid to absorber", weak, T_SCR, 210.0)
show("S10 demineralised water", {"H2O": n_dmw}, 298.15, 300.0)
show("S11 vent", vent, T_SCR, 105.0)
show("S12 product acid", acid, T_ABS, 300.0)
print(f"vent {nm3:.2f} Nm3/h; H2/Br2 feed ratio {n_h2 / n_br2:.3f} mol/mol; "
      f"Br2 left after R101 {n_br2_left * 1000:.3f} mol/h")

# --- energy ---------------------------------------------------------------------------
# E101: Br2(l) 298.15 K -> Br2(g) at T_BR2; dHf of the gas is the vaporisation enthalpy at T0
q_e101 = n_br2 * (HF["Br2"] + dh("Br2", T_BR2))
m_lps = q_e101 / H_LPS_LATENT
# R101, R102 and E102: heat removed = H_in - H_out (formation basis, ideal gas)
h_s2 = gas_h(feed_br2, T_BR2)
h_s3 = gas_h(feed_h2, T_H2)
h_s4 = gas_h(burner, T_R101)
h_s5 = gas_h(fin, T_R101)
h_s6 = gas_h(fin, T_E102)
q_r101 = h_s2 + h_s3 - h_s4
q_r102 = h_s4 - h_s5
q_e102 = h_s5 - h_s6
print("== energy ==")
print(f"Q1 E101 bromine vaporiser (LP steam): {q_e101 / 3600:.2f} kW = {m_lps:.1f} kg/h steam")
print(f"Q2 R101 burner cooling water: {q_r101 / 3600:.2f} kW "
      f"(reaction heat at 298 K from Br2(g) {n_br2 * X_BURNER * -(2 * HF['HBr'] - HF['Br2']) / 3600:.1f} kW)")
print(f"R102 finishing bed heat released: {q_r102 / 3600:.4f} kW "
      f"(adiabatic rise {q_r102 / sum(n * R * CP[c][0] for c, n in fin.items()):.2f} K, not a utility)")
print(f"Q3 E102 graphite gas cooler: {q_e102 / 3600:.2f} kW")

# absorption block (C201 + C202), reference 298.15 K: HBr(g), liquid water
h_in_abs = sum(n * dh(c, T_E102) for c, n in fin.items())
h_acid = n_hbr_acid * DH_SOL + acid_kg * CP_ACID * (T_ABS - T0)
h_vent = sum(n * dh(c, T_SCR) for c, n in vent.items()) + vent["H2O"] * DH_VAP
h_dmw = 0.0                                   # DMW at 298.15 K
q_c201 = h_in_abs + h_dmw - h_acid - h_vent
print(f"Q4 C201 absorber cooling water: {q_c201 / 3600:.2f} kW "
      f"(of which heat of solution {-n_hbr_acid * DH_SOL / 3600:.1f} kW)")

p_acid = acid_kg / RHO_ACID / 3600 * (300.0 - P_ABS) / 0.5           # kW, eta 0.5
print(f"Q5 P201 product acid pump: {p_acid:.3f} kW; Q6 instruments, burner management, "
      f"analysers 3.0 kW (ASSUMED)")

# --- checks ---------------------------------------------------------------------------
m_in = sum(mass(feed_br2).values()) + sum(mass(feed_h2).values()) + n_dmw * M["H2O"]
m_out = sum(mass(acid).values()) + sum(mass(vent).values())
br_in = 2 * n_br2
br_out = n_hbr_acid + n_hbr_vent
h_in = 2 * n_h2
h_out = n_hbr_acid + n_hbr_vent + 2 * vent["H2"] + 2 * (n_w_acid + n_w_vent)
h_in += 2 * n_dmw
print("== checks ==")
print(f"mass in {m_in:.3f} kg/h, out {m_out:.3f} kg/h, diff {m_in - m_out:.2e}")
print(f"Br in {br_in:.6f}, out {br_out:.6f} kmol/h; H in {h_in:.6f}, out {h_out:.6f} kmol/h")
print(f"per kg HBr: Br2 {n_br2 * M['Br2'] / HBR:.5f} kg, H2 feed {sum(mass(feed_h2).values()) / HBR:.6f} kg, "
      f"DMW {n_dmw * M['H2O'] / HBR:.5f} kg, LP steam {m_lps / HBR:.5f} kg")
try:
    from thermo import Chemical
    print(f"check: Br2 saturation at {P_BR2:.0f} kPa(a) = {Chemical('bromine').Tsat(P_BR2 * 1000):.1f} K (thermo)")
except Exception as exc:  # thermo is an optional extra
    print(f"check: Br2 saturation temperature not evaluated ({exc})")
