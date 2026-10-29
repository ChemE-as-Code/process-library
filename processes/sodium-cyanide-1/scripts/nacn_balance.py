"""Concept heat and material balance of sodium-cyanide-1 (DESIGN.md D-004..D-010).

Independent estimate: plain Python, ideal-gas enthalpies from the cp polynomials of
process/materials.yaml (chemicals/thermo data written there by `cheme chemistry thermo`), simple
latent-heat and sensible-heat estimates for the liquid duties. Every separation split and every
liquid-side duty here is an ASSUMED design value (DESIGN.md), not a rigorous model: core does not
qualify HCN-water-NH3-salt electrolytes (core #364). The converter outlet is recomputed by
`cheme process propagate` from the conversions printed here; this script only finds them and
the adiabatic gauze temperature.

Run: python3 scripts/nacn_balance.py   (no third-party imports)
"""

R = 8.314462618e-3  # kJ/(mol K) -> per kmol: kJ/(kmol K) * 1e3; we work in kJ/kmol below
RK = 8.314462618    # kJ/(kmol K)

MW = {"CH4": 16.0425, "NH3": 17.0305, "O2": 31.9988, "N2": 28.0134, "H2": 2.01588,
      "CO": 28.0101, "CO2": 44.0095, "HCN": 27.0253, "H2O": 18.0153, "NaOH": 39.9971,
      "NaCN": 49.0072}
# ideal-gas data of process/materials.yaml: dHf_298 kJ/kmol, cp/R polynomial (298-1500 K)
IG = {
    "CH4": (-74534.0, [3.03355, 0.00128716, 1.23235e-05, -1.06141e-08, 2.73706e-12]),
    "NH3": (-45558.0, [3.17207, 0.00327594, 1.90313e-06, -2.08027e-09, 5.26428e-13]),
    "O2": (0.0, [3.33121, 3.73673e-05, 2.68405e-06, -2.58548e-09, 7.32021e-13]),
    "HCN": (129291.0, [2.72083, 0.00710047, -6.7081e-06, 3.80183e-09, -8.79706e-13]),
    "H2O": (-241822.0, [3.95742, -0.000363702, 2.42862e-06, -1.27073e-09, 2.12761e-13]),
    "N2": (0.0, [3.79935, -0.00209702, 4.57541e-06, -3.03024e-09, 6.85763e-13]),
    "H2": (0.0, [3.29621, 0.00115759, -2.3324e-06, 2.10906e-09, -5.98313e-13]),
    "CO": (-110525.0, [3.77154, -0.0020965, 5.00055e-06, -3.5253e-09, 8.41146e-13]),
    "CO2": (-393474.0, [2.35127, 0.00919285, -7.99057e-06, 3.68269e-09, -7.05913e-13]),
}
LHV = {"H2": 241.83e3, "CO": 282.98e3, "CH4": 802.3e3, "HCN": 0.0, "NH3": 316.8e3}  # kJ/kmol
HVAP_W = 43.99e3   # kJ/kmol water at 298 K
HVAP_W_KG = 2333.0  # kJ/kg water at 343 K
CP_W = 4.18        # kJ/(kg K) liquid water / dilute solutions


def h(c, T):
    """Ideal-gas enthalpy incl. formation, kJ/kmol."""
    hf, a = IG[c]
    s = sum(a[i] / (i + 1) * (T ** (i + 1) - 298.15 ** (i + 1)) for i in range(5))
    return hf + RK * s


def H(st, T):
    return sum(n * h(c, T) for c, n in st.items() if c in IG)


def mass(st):
    return sum(n * MW[c] for c, n in st.items())


def show(name, st, T=None, P=None):
    m = mass(st)
    n = sum(st.values())
    x = {c: round(v / n, 9) for c, v in st.items() if v > 0}
    print(f"{name}: {m:.2f} kg/h, {n:.3f} kmol/h, T={T}, P={P}")
    print(f"   mole: {x}")
    w = {c: round(v * MW[c] / m, 9) for c, v in st.items() if v > 0}
    print(f"   mass: {w}")


# ---------------------------------------------------------------- basis (design basis, D-002)
PRODUCT = 6250.0                      # kg/h solid NaCN product, ASSUMED (50 kt/a at 8000 h)
W_NACN, W_NAOH, W_H2O = 0.980, 0.010, 0.010   # product spec, ASSUMED (D-002)
# HCN losses, fractions of converter HCN (ASSUMED, D-007)
F_HCN_TAIL, F_HCN_WW = 0.001, 0.0005

n_nacn = PRODUCT * W_NACN / MW["NaCN"]          # kmol/h NaCN in product
hcn_conv = n_nacn / (1 - F_HCN_TAIL - F_HCN_WW)  # converter HCN

# ---------------------------------------------------------------- converter (D-004)
# feed ratios of US 6,596,251 B2 Table 2 run 1 (air only): O2/NH3 1.15, CH4/NH3 0.98,
# HCN yield on NH3 62.9 %.
O2_NH3, CH4_NH3, Y_HCN = 1.15, 0.98, 0.629
# by-product distribution fitted to the commercial converter gas of US 4,847,062 Example 1
# (wt%: HCN 9.2, H2O 18.2, NH3 1.8, CH4 0.1, H2 1.3, N2 62.2, CO 4.6, CO2 1.5), as mole ratios
ex1 = {"HCN": 9.2, "H2O": 18.2, "NH3": 1.8, "CH4": 0.1, "H2": 1.3, "N2": 62.2, "CO": 4.6, "CO2": 1.5}
ex1m = {c: v / MW[c] for c, v in ex1.items()}
r_nh3 = ex1m["NH3"] / ex1m["HCN"]
r_ch4 = ex1m["CH4"] / ex1m["HCN"]
r_co = ex1m["CO"] / ex1m["HCN"]
r_co2 = ex1m["CO2"] / ex1m["HCN"]
tot = sum(ex1m.values())
print("US 4,847,062 Ex.1 converter gas, mol%:", {c: round(100 * v / tot, 2) for c, v in ex1m.items()})

nh3_in = hcn_conv / Y_HCN
ch4_in = CH4_NH3 * nh3_in
o2_in = O2_NH3 * nh3_in
N2_O2_AIR = 79.0 / 21.0   # ASSUMED dry air, argon lumped with nitrogen (D-003)
n2_in = N2_O2_AIR * o2_in

nh3_out = r_nh3 * hcn_conv
ch4_out = r_ch4 * hcn_conv
co_out = r_co * hcn_conv
co2_out = r_co2 * hcn_conv
# extents
x1 = hcn_conv                                 # ANDRUSSOW  CH4 + NH3 + 1.5 O2 -> HCN + 3 H2O
x2 = (nh3_in - x1 - nh3_out) / 2              # NH3_DEC    2 NH3 -> N2 + 3 H2
x4 = co2_out                                  # CH4_COMB   CH4 + 2 O2 -> CO2 + 2 H2O
x3 = ch4_in - x1 - x4 - ch4_out               # CH4_REF    CH4 + H2O -> CO + 3 H2
O2_RESID = 0.001 * o2_in                      # ASSUMED: oxygen practically consumed
x5 = 2 * (o2_in - 1.5 * x1 - 2 * x4 - O2_RESID)   # H2_OX  H2 + 0.5 O2 -> H2O
assert abs(x3 - co_out) / co_out < 0.2, (x3, co_out)  # CO from carbon balance vs Ex.1 ratio
conv = {"ANDRUSSOW (NH3)": x1 / nh3_in, "NH3_DEC (NH3)": 2 * x2 / nh3_in,
        "CH4_REF (CH4)": x3 / ch4_in, "CH4_COMB (CH4)": x4 / ch4_in, "H2_OX (O2)": 0.5 * x5 / o2_in}
h2o_rec = (0.990 * r_nh3 * hcn_conv) * 0.01 / 0.99   # water of the NH3 recycle S9 (see below)
print("conversions on the inlet flow of the key:", {k: round(v, 6) for k, v in conv.items()})
out6 = {
    "CH4": ch4_in - x1 - x3 - x4, "NH3": nh3_in - x1 - 2 * x2, "O2": O2_RESID,
    "HCN": x1, "H2O": 3 * x1 - x3 + 2 * x4 + x5 + h2o_rec, "N2": n2_in + x2,
    "H2": 3 * x2 + 3 * x3 - x5, "CO": x3, "CO2": x4,
}

# ---------------------------------------------------------------- ammonia recycle (D-006)
REC_NH3 = 0.990        # fraction of converter NH3 recovered and recycled, ASSUMED
WW_NH3 = 0.005         # to the C-101 process water, ASSUMED; the rest slips to C-201
REC_W = 0.01           # recycle gas: mole fraction water, ASSUMED
nh3_rec = REC_NH3 * nh3_out
s9 = {"NH3": nh3_rec, "H2O": nh3_rec * REC_W / (1 - REC_W)}
nh3_fresh = nh3_in - nh3_rec

feeds = {
    "S1 natural gas (CH4)": {"CH4": ch4_in},
    "S2 fresh ammonia": {"NH3": nh3_fresh},
    "S3 air": {"O2": o2_in, "N2": n2_in},
}
s5 = {"CH4": ch4_in, "NH3": nh3_in, "O2": o2_in, "N2": n2_in, "H2O": s9["H2O"]}

# feed temperatures (ASSUMED, D-005)
T_NG, T_NH3V, P_AIR1, P_AIR2, ETA = 298.15, 313.15, 101.325, 180.0, 0.75
kair = 1.4
dTs = 298.15 * ((P_AIR2 / P_AIR1) ** ((kair - 1) / kair) - 1)
T_AIR = 298.15 + dTs / ETA
W_blower = (o2_in + n2_in) * (H({"O2": 1, "N2": N2_O2_AIR}, T_AIR) - H({"O2": 1, "N2": N2_O2_AIR}, 298.15)) / (1 + N2_O2_AIR) / 3600
T_REC = 313.15
# mixed feed temperature: enthalpy balance
Hin = (H({"CH4": ch4_in}, T_NG) + H({"NH3": nh3_fresh}, T_NH3V) + H(s9, T_REC)
       + H({"O2": o2_in, "N2": n2_in}, T_AIR))
lo, hi = 250.0, 600.0
for _ in range(80):
    mid = (lo + hi) / 2
    if H(s5, mid) > Hin:
        hi = mid
    else:
        lo = mid
T5 = mid
# adiabatic gauze temperature (no heat loss)
lo, hi = 800.0, 1600.0
H5 = H(s5, T5)
for _ in range(80):
    mid = (lo + hi) / 2
    if H(out6, mid) > H5:
        hi = mid
    else:
        lo = mid
T6 = mid
print(f"air blower outlet {T_AIR:.1f} K, power {W_blower / ETA * ETA:.1f} kW shaft (isentropic/eta applied in T)")
print(f"mixed feed {T5:.2f} K; adiabatic converter outlet {T6:.2f} K")

# ---------------------------------------------------------------- waste heat boiler E-101
T7 = 523.15
Q_E101 = (H(out6, T6) - H(out6, T7)) / 3600
print(f"E-101 duty {Q_E101:.1f} kW")

# ---------------------------------------------------------------- C-101 ammonia recovery
# gas leaves saturated with water at 333.15 K and 140 kPa(a) (ASSUMED)
P8, T8 = 140.0, 333.15
PSAT = {333.15: 19.946, 283.15: 1.2282}   # kPa, IAPWS (water vapour pressure)
s8 = {c: v for c, v in out6.items() if c not in ("NH3", "H2O")}
nh3_slip = (1 - REC_NH3 - WW_NH3) * nh3_out
s8["NH3"] = nh3_slip
dry8 = sum(s8.values())
y8 = PSAT[T8] / P8
s8["H2O"] = dry8 * y8 / (1 - y8)
s10 = {"NH3": WW_NH3 * nh3_out, "H2O": out6["H2O"] - s8["H2O"] - s9["H2O"]}
# duties (ASSUMED estimates): gas cooling and condensation removed by cooling water;
# stripping steam 10 kg LP steam per kg NH3 recovered (ASSUMED, no open source, D-006)
s10_gas = dict(s10)
Q_C101_cool = (H(out6, T7) - H(s8, T8) - H(s9, T8) - H(s10_gas, T8)) / 3600 \
    + s10["H2O"] * HVAP_W / 3600   # sensible cooling to 333 K + condensation of the water
Q_C101_steam = 10.0 * nh3_rec * MW["NH3"] * 2108.0 / 3600   # LP steam 450 kPa(a), latent 2108 kJ/kg
Q_C101_cw = Q_C101_cool + Q_C101_steam   # stripper steam ends in the condensers/coolers
print(f"C-101 LP steam {Q_C101_steam:.1f} kW, cooling water {Q_C101_cw:.1f} kW")

# ---------------------------------------------------------------- C-201 HCN absorber, C-202 stripper
T11, P11 = 283.15, 130.0
s11 = {c: v for c, v in s8.items() if c not in ("HCN", "NH3", "H2O")}
s11["HCN"] = F_HCN_TAIL * hcn_conv
dry11 = sum(s11.values())
y11 = PSAT[T11] / P11
s11["H2O"] = dry11 * y11 / (1 - y11)
W_RICH = 0.025   # wt% HCN in the rich liquor (US 6,596,251 B2 background: 2-3 wt%), D-007
hcn_abs = s8["HCN"] - s11["HCN"]
water_cond = s8["H2O"] - s11["H2O"]
# HCN product from C-202: 99.5 wt% HCN, 0.5 wt% water (ASSUMED, D-007)
s13 = {"HCN": n_nacn}
s13["H2O"] = n_nacn * MW["HCN"] * 0.005 / 0.995 / MW["H2O"]
hcn_ww = hcn_abs - n_nacn
rich_mass = hcn_abs * MW["HCN"] / W_RICH
lean_water_rec = (rich_mass - hcn_abs * MW["HCN"] - nh3_slip * MW["NH3"]) / MW["H2O"] - water_cond
s15 = {"H2O": lean_water_rec}
s12 = {"HCN": hcn_abs, "NH3": nh3_slip, "H2O": lean_water_rec + water_cond}
s14 = {"HCN": hcn_ww, "NH3": nh3_slip, "H2O": s12["H2O"] - s13["H2O"]}
split_purge = (s14["H2O"] - lean_water_rec) / s14["H2O"]
s16 = {c: v * split_purge for c, v in s14.items()}
s15 = {c: v * (1 - split_purge) for c, v in s14.items()}
# close C-201 exactly: the lean water carries the bottoms' traces back (fixed-point iteration)
L = lean_water_rec
for _ in range(3000):
    s12 = {c: s8.get(c, 0) + s15.get(c, 0) - s11.get(c, 0) for c in ("HCN", "NH3", "H2O")}
    s14 = {c: s12[c] - s13.get(c, 0) for c in s12}
    split_purge = 1 - L / s14["H2O"]
    s15 = {c: v * (1 - split_purge) for c, v in s14.items()}
    s16 = {c: v * split_purge for c, v in s14.items()}
    L += (s12["HCN"] * MW["HCN"] / W_RICH - mass(s12)) / MW["H2O"]
rich_mass = mass(s12)
# duties, ASSUMED estimates (D-007): stripper reboiler = 10 K interchanger loss on the rich
# liquor + HCN vaporisation at reflux ratio 1 + water stripped overhead; chilled water removes
# the lean-water cooling from 303 K to 278 K, the condensed water's latent heat and the gas
# cooling from 333 to 283 K; cooling water the lean water from 313 to 303 K.
HVAP_HCN = 25.2e3   # kJ/kmol at its boiling point, NIST WebBook (D-007)
lean_mass = mass(s15)
Q_C202_reb = rich_mass * CP_W * 10 / 3600 + 2 * n_nacn * HVAP_HCN / 3600
# the feed/bottoms interchanger leaves the bottoms at about 298 K, too cold for cooling water:
# E-202 chills all bottoms 298 -> 278 K (lean water and purge leave the splitter at 278 K)
Q_C202_cw = 2 * n_nacn * HVAP_HCN / 3600            # HCN condenser, reflux ratio 1
Q_E202_chw = mass(s14) * CP_W * 20 / 3600
# gas pre-cooled with cooling water to 308.15 K (water condenses to saturation there), then
# chilled water: gas 308 -> 283 K, the rest of the condensation, the heat of absorption of HCN
# (ASSUMED equal to its condensation, 25 kJ/mol) and the lean water 303 -> 278 K (D-007)
y_308 = 5.629 / 135.0
w_308 = dry8 * y_308 / (1 - y_308)
dry_gas8 = {c: v for c, v in s8.items() if c != "H2O"}
Q_C201_cw = (H(dry_gas8, T8) - H(dry_gas8, 308.15)) / 3600 + (s8["H2O"] - w_308) * HVAP_W / 3600
Q_C201_chw = (H(dry_gas8, 308.15) - H(dry_gas8, T11)) / 3600 + (w_308 - s11["H2O"]) * HVAP_W / 3600 \
    + hcn_abs * 25.0e3 / 3600
print(f"C-202 reboiler {Q_C202_reb:.1f} kW, CW {Q_C202_cw:.1f} kW; E-202 chilled water {Q_E202_chw:.1f} kW; "
      f"C-201 CW {Q_C201_cw:.1f} kW, chilled water {Q_C201_chw:.1f} kW; purge fraction {split_purge:.6f}")

# ---------------------------------------------------------------- neutraliser, crystalliser, dryer
n_naoh_free = PRODUCT * W_NAOH / MW["NaOH"]
n_naoh = n_nacn + n_naoh_free
s20 = {"NaOH": n_naoh, "H2O": n_naoh * MW["NaOH"] / MW["H2O"]}   # 50 wt% caustic
s21 = {"NaCN": n_nacn, "NaOH": n_naoh_free, "H2O": s20["H2O"] + s13["H2O"] + n_nacn}
Q_R401 = n_nacn * 12.3e3 / 3600   # heat of neutralisation of HCN, ASSUMED ~12 kJ/mol (D-008)
print(f"neutraliser duty {Q_R401:.1f} kW; NaCN solution {mass(s21):.1f} kg/h, wt NaCN {s21['NaCN'] * MW['NaCN'] / mass(s21):.4f}")
show("S2 fresh NH3", {"NH3": nh3_fresh})
for k, v in [("S1", {"CH4": ch4_in}), ("S3 air", {"O2": o2_in, "N2": n2_in}), ("S9 NH3 recycle", s9),
             ("S5 mixed feed", s5), ("S6 converter out", out6), ("S8 gas to C-201", s8),
             ("S10 C-101 water", s10), ("S11 tail gas", s11), ("S12 rich", s12), ("S13 HCN", s13),
             ("S14 bottoms", s14), ("S15 lean", s15), ("S16 purge", s16), ("S20 caustic", s20),
             ("S21 NaCN solution", s21)]:
    show(k, v)

# ---------------------------------------------------------------- tail gas boiler B-301 (D-009)
EXCESS = 0.15
o2_need = 0.5 * s11["H2"] + 0.5 * s11["CO"] + 2 * s11["CH4"] + 1.25 * s11["HCN"] - s11.get("O2", 0)
o2_air = (1 + EXCESS) * o2_need
s30 = {"O2": o2_air, "N2": N2_O2_AIR * o2_air}
s31 = {"N2": s11["N2"] + s30["N2"] + 0.5 * s11["HCN"],
       "O2": s11.get("O2", 0) + o2_air - o2_need,
       "CO2": s11["CO2"] + s11["CO"] + s11["CH4"] + s11["HCN"],
       "H2O": s11["H2O"] + s11["H2"] + 2 * s11["CH4"] + 0.5 * s11["HCN"]}
T31 = 423.15
Hin = H(s11, T11) + H(s30, 298.15)
Q_B301 = (Hin - H(s31, T31)) / 3600
lhv = sum(s11.get(c, 0) * LHV[c] for c in LHV) / 3600
print(f"tail gas LHV {lhv:.1f} kW; B-301 steam duty (stack 423 K, no losses) {Q_B301:.1f} kW")
show("S30 combustion air", s30)
show("S31 flue gas", s31)
print("check S11 O2", s11.get("O2"))

# ---------------------------------------------------------------- crystalliser and dryer (D-008)
SOL = 0.80          # kg NaCN per kg water in the mother liquor at 343 K (US 4,847,062 Table 2 filtrate)
CAKE_LIQ = 0.10     # liquid mass fraction of the centrifuge cake, ASSUMED
naoh_kg = n_naoh_free * MW["NaOH"]
nacn_kg = n_nacn * MW["NaCN"]
# C/9 = L ; L = (1+SOL) w + NaOH ; C = NaCN - SOL w  (recycle of all filtrate, no purge)
k = CAKE_LIQ / (1 - CAKE_LIQ)
w_l = (k * nacn_kg - naoh_kg) / ((1 + SOL) + k * SOL)
crystals = nacn_kg - SOL * w_l
liq = (1 + SOL) * w_l + naoh_kg
water_in = s21["H2O"] * MW["H2O"]
evap = water_in - w_l
water_prod = PRODUCT * W_H2O
dry_evap = w_l - water_prod
print(f"cake: crystals {crystals:.1f}, liquor {liq:.1f} (water {w_l:.1f}, NaCN {SOL * w_l:.1f}, NaOH {naoh_kg:.1f}); "
      f"crystalliser evaporation {evap:.1f} kg/h; dryer evaporation {dry_evap:.1f} kg/h")
Q_CR401 = evap * HVAP_W_KG / 3600
Q_D401 = dry_evap * 2400.0 / 0.8 / 3600     # 80 % dryer efficiency, ASSUMED
Q_E401 = (evap + dry_evap) * HVAP_W_KG / 3600
Q_E001 = nh3_fresh * (19.9e3 + 36.0 * 15) / 3600   # vaporise at 1100 kPa(a), superheat 15 K, ASSUMED
print(f"CR-401 steam {Q_CR401:.1f} kW, D-401 steam {Q_D401:.1f} kW, E-401 condenser CW {Q_E401:.1f} kW, E-001 steam {Q_E001:.1f} kW")
steam_use = Q_E001 + Q_C101_steam + Q_C202_reb + Q_CR401 + Q_D401
print(f"steam use {steam_use:.1f} kW; E-101 surplus {Q_E101 - steam_use:.1f} kW; export incl. B-301 {Q_E101 - steam_use + Q_B301:.1f} kW")
W_misc = 400.0   # pumps, vacuum pumps, centrifuge, dryer drive, briquetting, B-301 fan: ASSUMED lump
print(f"power: K-101 {W_blower:.1f} kW + lump {W_misc} kW")
cw_total = Q_C101_cw + Q_C201_cw + Q_C202_cw + Q_R401 + Q_E401
print(f"cooling water total {cw_total:.1f} kW (C-101 {Q_C101_cw:.1f}, C-201 {Q_C201_cw:.1f}, C-202 {Q_C202_cw:.1f}, R-401 {Q_R401:.1f}, E-401 {Q_E401:.1f})")
