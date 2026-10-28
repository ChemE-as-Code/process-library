"""Concept heat and material balance of aniline-1 (DESIGN.md D-006).

Run with `cheme run scripts/aniline_balance.py` (thermo is in cheme's interpreter). Writes
build/aniline_balance.yaml (stream states and duties to transcribe into
process/flowsheet.yaml as `assumed` values with this script as their source) and prints a
summary. Nothing in the repository is written.

Model (all choices are the design basis's, ASSUMED unless a source is named in DESIGN.md):
- reactor: complete conversion of nitrobenzene, selectivity 0.997 to aniline, 0.002 to benzene,
  0.0005 kmol diphenylamine per kmol nitrobenzene (D-004); adiabatic, ideal gas;
- loop: H2/NB 60 mol/mol at the reactor inlet, N2 5 mol% in the separator gas (purge), H2 and
  N2 not dissolved in the liquids, all NH3 dissolved in the aqueous phase (D-005);
- V-101 three-phase separator at 333.15 K: vapour partial pressures from pure-component
  vapour pressures (thermo) times activities taken from the mutual solubilities (Raoult's law
  for the solvent of each liquid phase), benzene by Raoult's law in the organic phase (D-007);
- D-101 decanter at 313.15 K: organic phase 5 wt% water, aqueous phase 3.6 wt% aniline (D-007);
- columns: product specifications and ASSUMED splits; duties from enthalpy balances with an
  ASSUMED 30 % reflux margin on the condensers (D-008).
Enthalpy: ideal gas from formation (materials.yaml data), liquid = ideal gas - Hvap(T)
(thermo), ideal solutions, no heat of mixing. A concept estimate, not a qualified method.
"""
import math
from pathlib import Path

from thermo import Chemical

R = 8.314462618  # kJ/(kmol K)
T0 = 298.15

# id: (name for thermo, molar mass, dHf_298 kJ/kmol, cp_R coefficients) - as in materials.yaml
COMP = {
    "NB": ("nitrobenzene", 123.11, 68500.0, [-3.72604, 0.071473, -4.95763e-05, 1.26887e-08]),
    "ANL": ("aniline", 93.126, 87500.0, [2.598, 0.019936, 8.438e-05, -1.3368e-07, 5.63e-11]),
    "H2O": ("water", 18.015, -241822.0, [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12]),
    "H2": ("hydrogen", 2.0159, 0.0, [2.883, 0.003681, -7.72e-06, 6.92e-09, -2.13e-12]),
    "N2": ("nitrogen", 28.013, 0.0, [3.539, -0.000261, 7e-08, 1.57e-09, -9.9e-13]),
    "C6H6": ("benzene", 78.112, 83180.0, [3.551, -0.006184, 0.00014365, -1.9807e-07, 8.234e-11]),
    "DPA": ("diphenylamine", 169.22, 219300.0, [-9.26578, 0.127753, -8.90015e-05, 2.32246e-08]),
    "NH3": ("ammonia", 17.031, -45558.0, [4.238, -0.004215, 2.041e-05, -2.126e-08, 7.61e-12]),
}
IDS = list(COMP)
MW = {k: v[1] for k, v in COMP.items()}
_CHEM = {}


def chem(c):
    if c not in _CHEM:
        _CHEM[c] = Chemical(COMP[c][0])
    return _CHEM[c]


def psat(c, T):  # kPa
    return chem(c).VaporPressure(T) / 1000.0


def hvap(c, T):  # kJ/kmol
    return chem(c).EnthalpyVaporization(T)  # J/mol = kJ/kmol


def h_ig(c, T):  # kJ/kmol
    a = COMP[c][3]
    integ = sum(a[i] / (i + 1) * (T ** (i + 1) - T0 ** (i + 1)) for i in range(len(a)))
    return COMP[c][2] + R * integ


def h_liq(c, T):
    return h_ig(c, T) - hvap(c, T)


def H(n, T, phase="g"):
    """Enthalpy flow kW of molar flows n (kmol/h)."""
    tot = 0.0
    for c, f in n.items():
        if f == 0:
            continue
        tot += f * (h_ig(c, T) if phase == "g" or c in ("H2", "N2") else h_liq(c, T))
    return tot / 3600.0


def add(*ns):
    out = {c: 0.0 for c in IDS}
    for n in ns:
        for c, f in n.items():
            out[c] += f
    return out


def scale(n, s):
    return {c: f * s for c, f in n.items()}


def mass(n):
    return sum(f * MW[c] for c, f in n.items())


def solve_T(fun, lo, hi):
    """Root of fun(T) = 0 by bisection."""
    flo = fun(lo)
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        fm = fun(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------- design basis (D-002..D-008)
PRODUCT_KG_H = 25000.0          # aniline product incl. its water
PRODUCT_WATER_WT = 0.0005       # 0.05 wt% water design target
SEL = {"ANL": 0.997, "C6H6": 0.002, "DPA": 0.0005}  # kmol per kmol NB converted
H2_NB = 60.0
Y_N2 = 0.05
H2_FEED = {"H2": 0.999, "N2": 0.001}
T_SEP, P_SEP = 333.15, 410.0
T_DEC = 313.15
W_ORG = 0.05                    # water mass fraction in the organic phase (decanter)
A_AQ = 0.036                    # aniline mass fraction in the aqueous phase (decanter)
ANL_WW_PPM = 50.0               # aniline in the stripped wastewater
DPA_RESIDUE_WT = 0.5            # diphenylamine mass fraction in the C-202 bottoms
LIGHTS_ANL_PER_BZ = 1.0         # kg aniline per kg benzene in the C-201 low-boiler draw
T_RIN = 513.15                  # reactor inlet
P = {"S1": 500, "S1B": 650, "S2": 2850, "S3": 400, "S4": 560, "S5": 540, "S6": 530, "S7": 500,
     "S8": 485, "S9": 460, "S10": P_SEP}
ETA_K = 0.75
REFLUX_MARGIN = 1.3
C201_PTOP, C201_PBOT = 60.0, 70.0
C202_PTOP, C202_PBOT, C202_R = 20.0, 25.0, 0.5
C202_HEAVY_DT = 15.0            # bottoms above the aniline boiling point (heavies)
C102_P = 101.325


# activities from the mutual solubilities at the separator (Raoult for each phase's solvent)
def x_from_w(wa, a, b):  # mole fraction of a in a binary a/b of mass fraction wa
    na, nb = wa / MW[a], (1 - wa) / MW[b]
    return na / (na + nb)


A_W = 1.0 - x_from_w(A_AQ, "ANL", "H2O")       # water activity
A_AN = 1.0 - x_from_w(W_ORG, "H2O", "ANL")     # aniline activity


def azeotrope(Ptot):
    """Heteroazeotrope water/aniline at Ptot: T and y_aniline (same activity model)."""
    T = solve_T(lambda T: A_W * psat("H2O", T) + A_AN * psat("ANL", T) - Ptot, 300, 470)
    return T, A_AN * psat("ANL", T) / Ptot


prod_anl = PRODUCT_KG_H * (1 - PRODUCT_WATER_WT) / MW["ANL"]
prod_w = PRODUCT_KG_H * PRODUCT_WATER_WT / MW["H2O"]

F = prod_anl / SEL["ANL"]
xb_org = 0.0
s202 = s102 = None
for it in range(200):
    gen = {"ANL": SEL["ANL"] * F, "C6H6": SEL["C6H6"] * F, "DPA": SEL["DPA"] * F}
    ext = {"ANL": gen["ANL"], "BZ": gen["C6H6"], "DPA": gen["DPA"]}
    # extents: R1 ANL, R2 benzene, R3 DPA (2 NB each)
    e1, e2, e3 = gen["ANL"], gen["C6H6"], gen["DPA"]
    cons = {"NB": e1 + e2 + 2 * e3, "H2": 3 * e1 + 4 * e2 + 6 * e3}
    gen["H2O"] = 2 * e1 + 2 * e2 + 4 * e3
    gen["NH3"] = e2 + e3
    # separator vapour fractions
    y_w = A_W * psat("H2O", T_SEP) / P_SEP
    y_an = A_AN * psat("ANL", T_SEP) / P_SEP
    y_b = xb_org * psat("C6H6", T_SEP) / P_SEP
    s = y_w + y_an + y_b
    V_H2 = H2_NB * F - cons["H2"]
    V_N2 = Y_N2 * V_H2 / (1 - s - Y_N2)
    V_tot = (V_H2 + V_N2) / (1 - s)
    V = {"H2": V_H2, "N2": V_N2, "H2O": y_w * V_tot, "ANL": y_an * V_tot, "C6H6": y_b * V_tot}
    phi = cons["H2"] / (999.0 * V_N2 - V_H2)
    M = phi * V_N2 / 0.001
    # separator liquid = generated - purged (condensables); NH3 and DPA all liquid
    L = {c: 0.0 for c in IDS}
    for c in ("H2O", "ANL", "C6H6"):
        L[c] = gen[c] - phi * V[c]
    L["DPA"] = gen["DPA"]
    L["NH3"] = gen["NH3"]
    # benzene mole fraction in the organic phase of the separator
    org_w = W_ORG / (1 - W_ORG) * (L["ANL"] * MW["ANL"] + L["C6H6"] * MW["C6H6"] + L["DPA"] * MW["DPA"]) / MW["H2O"]
    xb_new = L["C6H6"] / (L["ANL"] + L["C6H6"] + L["DPA"] + org_w)
    # decanter loop with C-201 tops and C-102 tops
    T201, ya201 = azeotrope(C201_PTOP)
    T102, ya102 = azeotrope(C102_P)
    top201 = {c: 0.0 for c in IDS}
    top102 = {c: 0.0 for c in IDS}
    for _ in range(200):
        din = add(L, top201, top102)
        A = din["ANL"] * MW["ANL"]
        W = din["H2O"] * MW["H2O"]
        O = din["C6H6"] * MW["C6H6"] + din["DPA"] * MW["DPA"]
        N = din["NH3"] * MW["NH3"]
        ra, rw = A_AQ / (1 - A_AQ), W_ORG / (1 - W_ORG)
        ani_aq = ra * (W - rw * (A + O) + N) / (1 - ra * rw)
        ani_org = A - ani_aq
        w_org = rw * (ani_org + O)
        org = {c: 0.0 for c in IDS}
        aq = {c: 0.0 for c in IDS}
        org.update({"ANL": ani_org / MW["ANL"], "H2O": w_org / MW["H2O"], "C6H6": din["C6H6"], "DPA": din["DPA"]})
        aq.update({"ANL": ani_aq / MW["ANL"], "H2O": (W - w_org) / MW["H2O"], "NH3": din["NH3"]})
        # C-201: all water but the product's overhead with aniline at the azeotrope; benzene to
        # the low-boiler draw with its mass of aniline
        w_top = org["H2O"] - prod_w
        new201 = {c: 0.0 for c in IDS}
        new201.update({"H2O": w_top, "ANL": w_top * ya201 / (1 - ya201)})
        # C-102: aniline overhead down to ANL_WW_PPM in the bottoms, water at the azeotrope
        bot_mass_guess = aq["H2O"] * MW["H2O"] + aq["NH3"] * MW["NH3"]
        anl_bot = ANL_WW_PPM * 1e-6 * bot_mass_guess / MW["ANL"]
        a_top = aq["ANL"] - anl_bot
        new102 = {c: 0.0 for c in IDS}
        new102.update({"ANL": a_top, "H2O": a_top * (1 - ya102) / ya102})
        diff = sum(abs(new201[c] - top201[c]) + abs(new102[c] - top102[c]) for c in IDS)
        top201, top102 = new201, new102
        if diff < 1e-10:
            break
    lights = {c: 0.0 for c in IDS}
    lights.update({"C6H6": org["C6H6"], "ANL": org["C6H6"] * MW["C6H6"] * LIGHTS_ANL_PER_BZ / MW["ANL"]})
    bot201 = {c: 0.0 for c in IDS}
    bot201.update({"ANL": org["ANL"] - top201["ANL"] - lights["ANL"], "H2O": prod_w, "DPA": org["DPA"]})
    residue = {c: 0.0 for c in IDS}
    residue.update({"DPA": bot201["DPA"],
                    "ANL": bot201["DPA"] * MW["DPA"] * (1 - DPA_RESIDUE_WT) / DPA_RESIDUE_WT / MW["ANL"]})
    product = {c: 0.0 for c in IDS}
    product.update({"ANL": bot201["ANL"] - residue["ANL"], "H2O": prod_w})
    ww = {c: 0.0 for c in IDS}
    ww.update({"H2O": aq["H2O"] - top102["H2O"], "ANL": aq["ANL"] - top102["ANL"], "NH3": aq["NH3"]})
    # correct the NB feed for the aniline product
    F_new = F * prod_anl / product["ANL"]
    if abs(F_new - F) < 1e-9 and abs(xb_new - xb_org) < 1e-12:
        break
    F, xb_org = F_new, xb_new

purge = scale(V, phi)
recycle = scale(V, 1 - phi)
nb_feed = {c: 0.0 for c in IDS}
nb_feed["NB"] = F
h2_feed = {c: 0.0 for c in IDS}
h2_feed.update({"H2": 0.999 * M, "N2": 0.001 * M})
s3 = add(recycle, h2_feed)
s6 = add(s3, nb_feed)
s7 = add(s6, {"NB": -cons["NB"], "H2": -cons["H2"], "ANL": e1, "C6H6": e2, "DPA": e3,
              "H2O": gen["H2O"], "NH3": gen["NH3"]})
s10 = add(V, L)

# ---------------------------------------------------------------- energy
T_S2, T_S1 = 313.15, 313.15
T3 = solve_T(lambda T: H(s3, T) - H(recycle, T_SEP) - H(h2_feed, T_S2), 280, 400)
cp_mix = sum(f * R * sum(a * T3 ** i for i, a in enumerate(COMP[c][3])) for c, f in s3.items() if f) / sum(s3.values())
k = cp_mix / (cp_mix - R)
T4s = T3 * (P["S4"] / P["S3"]) ** ((k - 1) / k)
W_K = (H(s3, T4s) - H(s3, T3)) / ETA_K
T4 = solve_T(lambda T: H(s3, T) - H(s3, T3) - W_K, T3, 600)
# NB liquid at T_S1 (below the cp fit's 327.41 K: liquid cp of thermo from 327.41 K down)
h_nb_liq = h_liq("NB", 327.41) - chem("NB").HeatCapacityLiquid(320.0) * (327.41 - T_S1)  # kJ/kmol
H_nb = F * h_nb_liq / 3600.0
W_P101 = F * MW["NB"] / 1200.0 / 3600.0 * (P["S1B"] - P["S1"]) / 0.6   # kW, rho 1200 kg/m3, eta 0.6
# M-102 evaporator: recycle gas hot enough to evaporate the NB and reach T_RIN
H6 = H(s6, T_RIN)
T5 = solve_T(lambda T: H(s3, T) + H_nb + W_P101 * 0 - H6, 300, 800)
Q_E102 = H(s3, T5) - H(s3, T4)
T7 = solve_T(lambda T: H(s7, T) - H6, 500, 1000)
T8 = T5 + 30.0                   # E-102 hot inlet: 30 K approach at its hot end (ASSUMED)
Q_E103 = H(s7, T7) - H(s7, T8)
T9 = solve_T(lambda T: H(s7, T8) - H(s7, T) - Q_E102, 300, T8)
H10 = H(V, T_SEP) + H(L, T_SEP, "l")
Q_E104 = H(s7, T9) - H10
# dew check at S9
y9 = {c: f / sum(s7.values()) for c, f in s7.items()}
dew9 = {c: y9[c] * P["S9"] / psat(c, T9) for c in ("H2O", "ANL")}

# columns
Tb201 = solve_T(lambda T: psat("ANL", T) - C201_PBOT, 350, 500)
top201_vap = add(top201, lights)
Q_C201_cond = REFLUX_MARGIN * (H(top201_vap, T201) - H(top201_vap, T_DEC, "l"))
Q_C201_reb = Q_C201_cond + H(top201, T_DEC, "l") + H(lights, T_DEC, "l") + H(bot201, Tb201, "l") - H(org, T_DEC, "l")
Tt202 = solve_T(lambda T: psat("ANL", T) - C202_PTOP, 330, 500)
Tb202 = solve_T(lambda T: psat("ANL", T) - C202_PBOT, 330, 500) + C202_HEAVY_DT
Q_C202_cond = (1 + C202_R) * (H(product, Tt202) - H(product, Tt202, "l")) + H(product, Tt202, "l") - H(product, T_DEC, "l")
Q_C202_reb = Q_C202_cond + H(product, T_DEC, "l") + H(residue, Tb202, "l") - H(bot201, Tb201, "l")
Tb102 = solve_T(lambda T: psat("H2O", T) - C102_P, 340, 400)
Q_D101 = H(L, T_SEP, "l") + H(top201, T_DEC, "l") + H(top102, T_DEC, "l") - H(org, T_DEC, "l") - H(aq, T_DEC, "l")
Q_C102_cond = REFLUX_MARGIN * (H(top102, T102) - H(top102, T_DEC, "l"))
Q_C102_reb = Q_C102_cond + H(top102, T_DEC, "l") + H(ww, Tb102, "l") - H(aq, T_DEC, "l")
Q_WW_cool = H(ww, Tb102, "l") - H(ww, T_DEC, "l")
Q_reb = Q_C201_reb + Q_C202_reb + Q_C102_reb
Q_export = Q_E103 - Q_reb
W_PUMPS = 150.0                  # ASSUMED: column pumps and C-202 vacuum pump, lumped (D-009)

# ---------------------------------------------------------------- report
streams = [
    ("S1", "Nitrobenzene feed", nb_feed, T_S1, P["S1"], "l"),
    ("S1B", "Nitrobenzene to evaporator", nb_feed, T_S1, P["S1B"], "l"),
    ("S2", "Make-up hydrogen", h2_feed, T_S2, P["S2"], "g"),
    ("S3", "Circulator suction", s3, T3, P["S3"], "g"),
    ("S4", "Circulator discharge", s3, T4, P["S4"], "g"),
    ("S5", "Preheated recycle gas", s3, T5, P["S5"], "g"),
    ("S6", "Reactor feed", s6, T_RIN, P["S6"], "g"),
    ("S7", "Reactor effluent", s7, T7, P["S7"], "g"),
    ("S8", "Effluent after steam generator", s7, T8, P["S8"], "g"),
    ("S9", "Effluent after feed/effluent exchanger", s7, T9, P["S9"], "g"),
    ("S10", "Cooled effluent to separator", s10, T_SEP, P["S10"], "gl"),
    ("S11", "Separator gas", V, T_SEP, P_SEP, "g"),
    ("S12", "Purge gas", purge, T_SEP, P_SEP, "g"),
    ("S13", "Recycle gas", recycle, T_SEP, P_SEP, "g"),
    ("S14", "Crude condensate (both liquid phases)", L, T_SEP, P_SEP, "l"),
    ("S15", "Organic phase to dehydration column", org, T_DEC, 150, "l"),
    ("S16", "Aqueous phase to wastewater stripper", aq, T_DEC, 150, "l"),
    ("S17", "Dehydration column overhead condensate", top201, T_DEC, 150, "l"),
    ("S18", "Low-boiler draw", lights, T_DEC, 300, "l"),
    ("S19", "Dry crude aniline", bot201, Tb201, 300, "l"),
    ("S20", "Aniline product", product, T_DEC, 300, "l"),
    ("S21", "Distillation residue", residue, Tb202, 300, "l"),
    ("S22", "Stripper overhead condensate", top102, T_DEC, 150, "l"),
    ("S23", "Stripped wastewater", ww, T_DEC, 300, "l"),
]
duties = {
    "W_K101": W_K, "W_P101": W_P101, "W_PUMPS": W_PUMPS, "Q_E102": Q_E102, "Q_E103": Q_E103,
    "Q_E104": Q_E104, "Q_D101": Q_D101, "Q_C201_reb": Q_C201_reb, "Q_C201_cond": Q_C201_cond,
    "Q_C202_reb": Q_C202_reb, "Q_C202_cond": Q_C202_cond, "Q_C102_reb": Q_C102_reb,
    "Q_C102_cond": Q_C102_cond, "Q_WW_cool": Q_WW_cool, "Q_export": Q_export,
}
lines = ["# written by scripts/aniline_balance.py (cheme run); scratch, transcribe by hand", "streams:"]
for sid, title, n, T, Pk, ph in streams:
    tot = sum(n.values())
    comp = {c: round(f / tot, 9) for c, f in n.items() if f > 0}
    lines.append(f"  {sid}: {{title: '{title}', T: {T:.2f}, P: {Pk}, phase: {ph}, flow_kg_h: {mass(n):.2f}, "
                 f"kmol_h: {tot:.4f}, x: {comp}}}")
lines.append("duties_kW:")
for k2, v in duties.items():
    lines.append(f"  {k2}: {v:.1f}")
Path("build").mkdir(exist_ok=True)
Path("build/aniline_balance.yaml").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print(f"iterations {it}, F_NB {F:.4f} kmol/h, make-up {M:.4f} kmol/h, purge fraction {phi:.6f}")
print(f"activities a_w {A_W:.4f} a_an {A_AN:.4f}; azeotrope C-201 {T201:.2f} K y_an {ya201:.4f}; C-102 {T102:.2f} K y_an {ya102:.4f}")
print(f"T3 {T3:.2f} T4 {T4:.2f} T5 {T5:.2f} T7 {T7:.2f} T8 {T8:.2f} T9 {T9:.2f}; dew ratios at S9 {dew9}")
print(f"Tb201 {Tb201:.2f} Tt202 {Tt202:.2f} Tb202 {Tb202:.2f} Tb102 {Tb102:.2f}")
mi = mass(nb_feed) + mass(h2_feed)
mo = mass(product) + mass(purge) + mass(lights) + mass(residue) + mass(ww)
print(f"overall mass in {mi:.3f} out {mo:.3f} kg/h")
# element balance
EL = {"NB": {"C": 6, "H": 5, "N": 1, "O": 2}, "ANL": {"C": 6, "H": 7, "N": 1}, "H2O": {"H": 2, "O": 1},
      "H2": {"H": 2}, "N2": {"N": 2}, "C6H6": {"C": 6, "H": 6}, "DPA": {"C": 12, "H": 11, "N": 1},
      "NH3": {"N": 1, "H": 3}}
# overall energy closure: power + enthalpy of the feeds - enthalpy of the material products
# = heat to cooling water + exported steam
Q_cw = Q_E104 + Q_D101 + Q_C201_cond + Q_C202_cond + Q_C102_cond + Q_WW_cool
H_in = H_nb + H(h2_feed, T_S2)
H_out = (H(product, T_DEC, "l") + H(purge, T_SEP) + H(lights, T_DEC, "l") + H(residue, Tb202, "l")
         + H(ww, T_DEC, "l"))
W_tot = W_K + W_P101 + W_PUMPS
print(f"energy: power {W_tot:.1f} kW + H(feeds) - H(products) {H_in - H_out:.1f} kW = {W_tot + H_in - H_out:.1f} kW; "
      f"cooling water {Q_cw:.1f} kW + steam export {Q_export:.1f} kW = {Q_cw + Q_export:.1f} kW "
      f"(difference {(W_tot + H_in - H_out) - (Q_cw + Q_export):.1f} kW: pumps' work counted as power, not as heat)")
for e in "CHNO":
    ein = sum(n.get(c, 0) * EL[c].get(e, 0) for n in (nb_feed, h2_feed) for c in n)
    eout = sum(n.get(c, 0) * EL[c].get(e, 0) for n in (product, purge, lights, residue, ww) for c in n)
    print(f"element {e}: in {ein:.5f} out {eout:.5f} kmol/h")
