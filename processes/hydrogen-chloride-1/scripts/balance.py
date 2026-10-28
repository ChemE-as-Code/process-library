"""Mass and energy balance of hydrogen-chloride-1 (design case), DESIGN.md D-006.

Independent of cheme: it gives the stream values that process/flowsheet.yaml carries as
`assumed` (source: scripts/balance.py) and the duties of the energy streams. Run with
`cheme run scripts/balance.py`; it writes nothing, it prints the values.

Inputs (each in DESIGN.md with its source or ASSUMED):
- product: 10 000 kg/h hydrochloric acid at 33.0 wt-% HCl (D-002);
- chlorine and hydrogen as delivered by chlor-alkali-1 (streams S42 and S44 there, D-003);
- hydrogen excess 10 mol-% over Cl2 + 2 O2 (D-004), complete conversion of Cl2 and O2 (D-005);
- furnace outlet 523.15 K (D-007), heat loss 3 % of the heat released (D-007);
- absorber recovery 99.5 % of the HCl, tail gas scrubber leaves 10 mg HCl/Nm3 (D-008);
- integral heat of solution of HCl(g) to 33 wt-% acid -61.4 kJ/mol (D-009).
Ideal-gas heat capacities and formation enthalpies are the ones `cheme chemistry thermo`
prints (ATcT, Poling 5th ed.), so that this balance and `cheme process reactors` agree.
"""

M = {"HCl": 36.461, "H2": 2.016, "Cl2": 70.906, "O2": 31.998, "H2O": 18.015}
# cp/R = a0 + a1 T + a2 T^2 + a3 T^3 + a4 T^4 (Poling 5th ed., via cheme chemistry thermo)
CP = {
    "HCl": [3.827, -0.002936, 8.79e-06, -1.031e-08, 4.39e-12],
    "H2": [2.883, 0.003681, -7.72e-06, 6.92e-09, -2.13e-12],
    "Cl2": [3.056, 0.0053708, -8.098e-06, 5.693e-09, -1.5256e-12],
    "O2": [3.63, -0.001794, 6.58e-06, -6e-09, 1.79e-12],
    "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
}
HF = {"HCl": -92173.0, "H2O": -241822.0}  # kJ/kmol, ideal gas, 298.15 K (ATcT)
R = 8.314462618
T0 = 298.15


def dh(comp, t):
    """Ideal-gas sensible enthalpy from T0 to t, kJ/kmol."""
    a = CP[comp]
    f = lambda x: sum(a[i] * x ** (i + 1) / (i + 1) for i in range(5))
    return R * (f(t) - f(T0))


def gas_h(kmol, t):
    return sum(n * dh(c, t) for c, n in kmol.items())


def mass(kmol):
    return {c: n * M[c] for c, n in kmol.items()}


def show(name, kmol, t, p):
    m = mass(kmol)
    tot = sum(m.values())
    frac = {c: round(v / tot, 7) for c, v in m.items() if v > 0}
    print(f"{name}: T {t:.2f} K, p {p:.1f} kPa(a), flow {tot:.2f} kg/h, mass fractions {frac}")
    return tot


# --- inputs ---------------------------------------------------------------------------
ACID = 10000.0              # kg/h product acid (D-002)
W_HCL = 0.330               # mass fraction HCl (D-002)
W_CL2_FEED = 0.9918815      # chlor-alkali-1 S42: Cl2 0.9918815, O2 0.008118535 (D-003)
W_H2_FEED = 0.6789415       # chlor-alkali-1 S44: H2 0.6789415, H2O 0.3210585 (D-003)
EXCESS_H2 = 0.10            # D-004
T_FURN = 523.15             # D-007
LOSS = 0.03                 # D-007
REC_ABS = 0.995             # D-008
VENT_HCL_MG_NM3 = 10.0      # D-008
T_ABS_GAS, P_ABS = 313.15, 120.0     # absorber top gas (D-008)
T_VENT, P_VENT = 303.15, 105.0       # vent (D-008)
PSAT = {313.15: 7.385, 303.15: 4.247}  # kPa, water (IAPWS-IF97), dilute acid taken as water
T_ACID = 313.15
CP_ACID = 2.55              # kJ/(kg K), 33 wt-% acid, ASSUMED (D-009)
DH_SOL = -61400.0           # kJ/kmol HCl(g) -> 33 wt-% acid at 298.15 K (D-009)
DH_VAP = 43990.0            # kJ/kmol water at 298.15 K (IAPWS-IF97)
H_STEAM, H_BFW = 2777.1, 441.0       # kJ/kg sat. steam 1000 kPa(a), BFW 378 K (D-010)

# --- product and vent -----------------------------------------------------------------
n_hcl_acid = ACID * W_HCL / M["HCl"]
w_acid = ACID * (1 - W_HCL)

# vent: excess H2 + water vapour + HCl; H2 excess depends on the feed, solved by iteration
n_hcl_vent = 0.0
for _ in range(20):
    n_hcl = n_hcl_acid + n_hcl_vent
    n_cl2 = n_hcl / 2
    m_cl2_gas = n_cl2 * M["Cl2"] / W_CL2_FEED
    n_o2 = m_cl2_gas * (1 - W_CL2_FEED) / M["O2"]
    n_h2_stoich = n_cl2 + 2 * n_o2
    n_h2 = n_h2_stoich * (1 + EXCESS_H2)
    m_h2_gas = n_h2 * M["H2"] / W_H2_FEED
    n_w_feed = m_h2_gas * (1 - W_H2_FEED) / M["H2O"]
    n_h2_ex = n_h2 - n_h2_stoich
    y_w = PSAT[T_VENT] / P_VENT
    n_w_vent = n_h2_ex * y_w / (1 - y_w)
    nm3 = (n_h2_ex + n_w_vent) * 22.414           # Nm3/h (273.15 K, 101.325 kPa)
    n_hcl_vent = nm3 * VENT_HCL_MG_NM3 * 1e-6 / M["HCl"]

n_w_formed = 2 * n_o2
feed_cl2 = {"Cl2": n_cl2, "O2": n_o2}
feed_h2 = {"H2": n_h2, "H2O": n_w_feed}
furn = {"HCl": n_hcl, "H2": n_h2_ex, "H2O": n_w_feed + n_w_formed}

# absorber top gas: unabsorbed HCl, H2, water vapour at the top
y_w_abs = PSAT[T_ABS_GAS] / P_ABS
n_w_abs = n_h2_ex * y_w_abs / (1 - y_w_abs)
tail = {"HCl": n_hcl * (1 - REC_ABS), "H2": n_h2_ex, "H2O": n_w_abs}
vent = {"HCl": n_hcl_vent, "H2": n_h2_ex, "H2O": n_w_vent}

# water: DMW = acid water + vent water - feed water - formed water
n_w_acid = w_acid / M["H2O"]
n_dmw = n_w_acid + n_w_vent - n_w_feed - n_w_formed
# weak acid from the tail tower: DMW + HCl and water taken from the tail gas
weak = {"HCl": tail["HCl"] - vent["HCl"], "H2O": n_dmw + n_w_abs - n_w_vent}
acid = {"HCl": n_hcl_acid, "H2O": n_w_acid}

print("== streams (design case) ==")
show("S1 chlorine feed", feed_cl2, 313.15, 400.0)
show("S2 hydrogen feed", feed_h2, 337.19, 140.0)
show("S3 furnace gas to absorber", furn, T_FURN, 130.0)
show("S4 acid from absorber", acid, T_ACID, 120.0)
show("S5 absorber tail gas", tail, T_ABS_GAS, P_ABS)
show("S6 weak acid to absorber", weak, T_VENT, 130.0)
show("S7 demineralised water", {"H2O": n_dmw}, 298.15, 300.0)
show("S8 vent", vent, T_VENT, P_VENT)
show("S9 product acid", acid, T_ACID, 250.0)
print(f"vent: {nm3:.1f} Nm3/h, H2 {n_h2_ex / (n_h2_ex + n_w_vent + n_hcl_vent):.4f} mol/mol")

# --- energy ---------------------------------------------------------------------------
# furnace, 298.15 K formation basis: heat released = -(H_out - H_in) with ideal gases
q_rxn = -(n_hcl * HF["HCl"] + n_w_formed * HF["H2O"])                   # kJ/h at 298.15 K
h_in = gas_h(feed_cl2, 313.15) + gas_h(feed_h2, 337.19)
h_out = gas_h(furn, T_FURN)
q_release = q_rxn + h_in - h_out                                            # kJ/h
q_loss = LOSS * q_rxn
q_steam = q_release - q_loss
m_steam = q_steam / (H_STEAM - H_BFW)
print("== energy ==")
print(f"furnace: reaction heat at 298 K {q_rxn / 3600:.1f} kW, H_in-H0 {h_in / 3600:.1f} kW, "
      f"H_out-H0 {h_out / 3600:.1f} kW, heat loss {q_loss / 3600:.1f} kW")
print(f"Q1 steam raised: {q_steam / 3600:.1f} kW = {m_steam:.1f} kg/h steam 1000 kPa(a) "
      f"({m_steam / (n_hcl_acid * M['HCl']):.3f} t/t HCl)")

# absorption block (C201 + C202), reference 298.15 K, HCl(g), liquid water
h_in_abs = h_out + furn["H2O"] * DH_VAP                    # gas sensible + latent of vapour
h_acid = n_hcl_acid * DH_SOL + ACID * CP_ACID * (T_ACID - T0)
h_vent = gas_h(vent, T_VENT) + vent["H2O"] * DH_VAP
q_cw = h_in_abs - h_acid - h_vent
print(f"Q3 absorber cooling water: {q_cw / 3600:.1f} kW "
      f"(of which heat of solution {-n_hcl_acid * DH_SOL / 3600:.1f} kW)")

# power: product acid pump and boiler feed water pump (D-011)
rho_acid = 1160.0           # kg/m3 at 33 wt-%, 20 C (D-011)
p_acid = ACID / rho_acid / 3600 * (250.0 - 120.0) / 0.5                   # kW, eta 0.5
p_bfw = m_steam / 950.0 / 3600 * (1100.0 - 101.325) / 0.5                 # kW, eta 0.5
print(f"Q4 acid pump: {p_acid:.2f} kW; Q2 BFW pump {p_bfw:.2f} kW + 3.0 kW instruments, "
      f"burner management and analysers = {p_bfw + 3.0:.2f} kW")

# --- equilibrium at the furnace outlet (D-005) -----------------------------------------
import math

S298 = {"HCl": 186.9, "H2": 130.7, "Cl2": 223.1, "O2": 205.2, "H2O": 188.8}  # kJ/(kmol K)
HF0 = {"HCl": -92173.0, "H2O": -241822.0, "H2": 0.0, "Cl2": 0.0, "O2": 0.0}


def ds(comp, t):
    a = CP[comp]
    g = lambda x: a[0] * math.log(x) + sum(a[i] * x ** i / i for i in range(1, 5))
    return R * (g(t) - g(T0))


def ln_k(nu, t):
    dg = sum(v * (HF0[c] + dh(c, t) - t * (S298[c] + ds(c, t))) for c, v in nu.items())
    return -dg / (R * t)


lk = ln_k({"H2": -1, "Cl2": -1, "HCl": 2}, T_FURN)
ntot = sum(furn.values())
y_cl2 = (furn["HCl"] / ntot) ** 2 / (math.exp(lk) * furn["H2"] / ntot)
print(f"H2 + Cl2 = 2 HCl at {T_FURN} K: ln K {lk:.2f} (K {math.exp(lk):.2e}), "
      f"equilibrium y(Cl2) {y_cl2:.1e}")
lk2 = ln_k({"H2": -2, "O2": -1, "H2O": 2}, T_FURN)
print(f"2 H2 + O2 = 2 H2O at {T_FURN} K: ln K {lk2:.1f}")

# --- balance checks -------------------------------------------------------------------
m_in = sum(mass(feed_cl2).values()) + sum(mass(feed_h2).values()) + n_dmw * M["H2O"]
m_out = ACID + sum(mass(vent).values())
print(f"overall mass: in {m_in:.3f} kg/h, out {m_out:.3f} kg/h")
for el, f in {"Cl": {"HCl": 1, "Cl2": 2}, "H": {"HCl": 1, "H2": 2, "H2O": 2},
              "O": {"O2": 2, "H2O": 1}}.items():
    def cnt(s):
        return sum(f.get(c, 0) * n for c, n in s.items())
    ein = cnt(feed_cl2) + cnt(feed_h2) + n_dmw * f.get("H2O", 0)
    eout = cnt(acid) + cnt(vent)
    print(f"element {el}: in {ein:.4f} kmol/h, out {eout:.4f} kmol/h")
