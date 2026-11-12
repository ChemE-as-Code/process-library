"""Independent heat and material balance of the styrene plant (DESIGN.md D-006).

This is NOT a cheme-as-code calculation. Core has no qualified property package for aromatics
with water and hydrogen (core#315: the packaged ones cover air and syngas), so the feed flows,
the recycle, the separations and the duties are computed here and the DWSIM simulation of
process/simulation.yaml is checked against them (D-012). The flowsheet cites this script for
the feed flows (balance-output contract, library ADR 0027).

Model (every choice is a DESIGN.md decision, ASSUMED where marked there):
- gas phase (reactors, steam superheater, burners, flue gas, effluent above its dew point): ideal
  gas with the formation enthalpies and cp polynomials of process/materials.yaml;
- liquids: ideal liquid h = h_ig(T) - Hvap(T), with thermo's heats of vaporisation; vapour
  pressures from thermo (Raoult's law, no activity coefficients);
- water and the aromatics are taken as immiscible liquids (D-008): the separator V-101 and the
  compressor coolers are flashed with a pure water phase and an ideal organic phase, the light
  gases (H2, CH4, C2H4) stay in the vapour; the aromatics dissolved in the condensate are added
  at the decanter from their aqueous solubilities (PubChem/HSDB, 25 C) times their mole fraction
  in the organic phase;
- reactors R-101/R-102: adiabatic conversion beds, 40 % of the inlet EB per bed, selectivities of
  D-005; outlet temperatures from the energy balance;
- steam superheater: complete combustion with 15 % excess air; natural gas makes up the fuel so
  that the flue gas leaves at the stack temperature (D-009);
- columns: specified key splits (non-keys sharp), Underwood minimum reflux at constant relative
  volatility from vapour pressures with the feed taken as saturated liquid (a simplification),
  R = 1.3 Rmin (at least 0.5); duties from the column energy balance with the arriving feed.

Run: cheme run scripts/sm_balance.py   (prints the streams, duties and checks; a JSON copy in
build/sm_balance.json)
"""

import json
import math
import os
from pathlib import Path

import yaml
from scipy.optimize import brentq
from thermo import ChemicalConstantsPackage

ROOT = Path(__file__).resolve().parents[1]
MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
C = ["H2", "CH4", "C2H4", "H2O", "BZ", "TOL", "EB", "SM", "BIPH", "N2", "O2", "CO2"]
MW = {c: MAT[c]["molar_mass"] for c in C}
NC = ["H2", "CH4", "C2H4", "N2", "O2", "CO2"]       # non-condensable at 313 K
ORG = ["BZ", "TOL", "EB", "SM", "BIPH"]
R = 8.314462618                                      # kJ/(kmol K)

# ---- basis (DESIGN.md D-002 to D-011)
PRODUCT_KG_H = 300e6 / 8000          # D-002: 300 kt/a styrene product stream, 8000 h/a
STEAM_RATIO = 1.3                    # D-004: kg dilution steam per kg EB to R-101 (ASSUMED)
PRIMARY = 0.10                       # D-004: share of the dilution steam mixed with the EB feed
X_BED = 0.40                         # D-005: EB conversion per bed
SEL = {"DH": 0.952, "TOL": 0.028, "BZ": 0.012, "TAR": 0.008}  # D-005, mol EB per mol EB converted
T_EB, P_EB = 303.15, 300.0           # D-003: fresh EB at the battery limit
P_STEAM = 1100.0                     # D-003: dilution steam, saturated
P_VL101, P_VL102 = 95.0, 150.0       # D-004: let-down valves (EB side, main steam)
T_E101_COLD = 793.15                 # D-004: EB/primary steam to 520 C (LVOC BREF 5.2.3.1.1)
T_RIN = 893.15                       # D-004: R-101 and R-102 inlets, 620 C
T_SSH1 = 1073.15                     # D-004: main steam leaving SSH coil 1 (H-101A)
T_SEP, P_SEP = 313.15, 45.0          # D-007: separator V-101
P_K101 = 300.0                       # D-007: off-gas compressor discharge (burner header)
ETA_K, ETA_P = 0.75, 0.65            # D-010
EXCESS_AIR = 0.15                    # D-009
T_AIR, T_NG = 298.15, 298.15         # D-009
T_STACK = 523.15                     # D-009: flue gas to the stack
Y_O2_AIR = 0.21                      # D-009: dry air, N2/O2 only
# columns (D-008): (light key, heavy key, LK in bottoms, HK in distillate, P top, P bottom)
COLS = {
    "C301": ("TOL", "EB", 0.003, 0.02, 50.0, 65.0),
    "C304": ("BZ", "TOL", 0.01, 0.005, 45.0, 60.0),
    "C302": ("EB", "SM", 0.0015, 0.02, 10.0, 25.0),
    "C303": ("SM", "BIPH", None, 1e-5, 8.0, 12.0),   # LK in bottoms from the tar spec below
}
TAR_SM_WT = 0.30                     # D-008: styrene in the tar (keeps it pumpable), mass fraction
R_FACTOR, R_FLOOR = 1.3, 0.5         # D-008
P_C301_FEED = 150.0                  # D-010: P-201 discharge
P_RECYCLE = 300.0                    # D-010: P-302 discharge into the EB feed drum
# aqueous solubility at 25 C, mg/L, PubChem (HSDB) compound records (D-008)
SOLUBILITY = {"BZ": 1790.0, "TOL": 526.0, "EB": 169.0, "SM": 300.0, "BIPH": 0.0}

consts, props = ChemicalConstantsPackage.from_IDs([MAT[c]["cas"] for c in ["H2O"] + ORG])
IDX = {c: i for i, c in enumerate(["H2O"] + ORG)}


def psat(c, t):
    return props.VaporPressures[IDX[c]](t) / 1e3      # kPa


def hvap(c, t):
    return props.EnthalpyVaporizations[IDX[c]](t)     # J/mol = kJ/kmol


def vliq(c, t):
    return props.VolumeLiquids[IDX[c]](t, 101325.0)   # m3/mol


def cp_r(c, t):
    a = MAT[c]["ideal_gas"]["cp_R"]
    return sum(k * t ** i for i, k in enumerate(a))


def h_ig1(c, t):  # kJ/kmol, formation included, ideal gas
    a = MAT[c]["ideal_gas"]["cp_R"]
    t0 = 298.15
    integ = sum(k / (i + 1) * (t ** (i + 1) - t0 ** (i + 1)) for i, k in enumerate(a))
    return MAT[c]["ideal_gas"]["dHf_298"] + R * integ


def s_ig1(c, t):  # kJ/(kmol K) at 1 bar
    a = MAT[c]["ideal_gas"]["cp_R"]
    t0 = 298.15
    integ = a[0] * math.log(t / t0) + sum(k / i * (t ** i - t0 ** i) for i, k in enumerate(a) if i > 0)
    return MAT[c]["ideal_gas"]["S_298"] + R * integ


def z():
    return {c: 0.0 for c in C}


def tot(n):
    return sum(n.values())


def add(*ns):
    return {c: sum(n[c] for n in ns) for c in C}


def scale(n, f):
    return {c: n[c] * f for c in C}


def mass(n):
    return sum(n[c] * MW[c] for c in C)


def H_gas(n, t):  # kW
    return sum(n[c] * h_ig1(c, t) for c in C if n[c]) / 3600


def H_liq(n, t):  # kW; light gases in a liquid are taken at their ideal-gas enthalpy
    return sum(n[c] * (h_ig1(c, t) - (hvap(c, t) if c in IDX else 0.0)) for c in C if n[c]) / 3600


def t_from(hfun, n, h, lo, hi):
    return brentq(lambda t: hfun(n, t) - h, lo, hi)


def flash_immiscible(n, t, p):
    """Vapour, organic liquid and water liquid of a feed at t, p (immiscible liquids)."""
    nc = sum(n[c] for c in NC)
    k = {c: psat(c, t) / p for c in ORG}
    org = {c: n[c] for c in ORG if n[c] > 0}
    pw = psat("H2O", t) / p

    def lo_of(v):
        if not org:
            return 0.0
        f = lambda lo: sum(m / (lo + v * k[c]) for c, m in org.items()) - 1.0
        if f(0.0) <= 0:
            return 0.0
        return brentq(f, 0.0, sum(org.values()) + 1.0)

    def resid(v):
        lo = lo_of(v)
        yw = min(pw, n["H2O"] / v)
        yorg = sum(k[c] * m / (lo + v * k[c]) for c, m in org.items()) if lo > 0 else sum(org.values()) / v
        return nc / v + yw + yorg - 1.0

    vmax = tot(n)
    v = brentq(resid, max(nc, 1e-9) * (1 + 1e-12), vmax * 1.000001) if resid(vmax * 1.000001) < 0 else vmax
    lo = lo_of(v)
    vap, liq_o, liq_w = z(), z(), z()
    for c in NC:
        vap[c] = n[c]
    vap["H2O"] = min(pw * v, n["H2O"])
    liq_w["H2O"] = n["H2O"] - vap["H2O"]
    for c, m in org.items():
        x = m / (lo + v * k[c]) if lo > 0 else 0.0
        liq_o[c] = x * lo
        vap[c] = m - liq_o[c]
    return vap, liq_o, liq_w


def bubble_t(n, p, lo=250.0, hi=700.0):
    x = {c: n[c] / tot(n) for c in ORG if n[c] > 0}
    return brentq(lambda t: sum(x[c] * psat(c, t) for c in x) - p, lo, hi)


def split(feed, lk, hk, xlk_b, xhk_d):
    order = sorted(ORG, key=lambda c: MAT[c]["normal_boiling_point"])
    light = [c for c in order if MAT[c]["normal_boiling_point"] < MAT[lk]["normal_boiling_point"]]
    heavy = [c for c in order if MAT[c]["normal_boiling_point"] > MAT[hk]["normal_boiling_point"]]
    top, bot = z(), z()
    for c in C:
        if c in NC or c == "H2O" or c in light:
            top[c] = feed[c]
        elif c in heavy:
            bot[c] = feed[c]
    lk_b, hk_d = 0.0, 0.0
    for _ in range(200):
        b_other = sum(bot[c] for c in heavy) + feed[hk] - hk_d
        lk_b = xlk_b * b_other / (1 - xlk_b)
        d_other = sum(top[c] for c in C if c not in (lk, hk)) + feed[lk] - lk_b
        hk_d = xhk_d * d_other / (1 - xhk_d)
    top[lk], bot[lk] = feed[lk] - lk_b, lk_b
    top[hk], bot[hk] = hk_d, feed[hk] - hk_d
    return top, bot


def column(feed, top, bot, lk, hk, p_top, p_bot, h_feed):
    t_top, t_bot = bubble_t(top, p_top), bubble_t(bot, p_bot)
    tm = 0.5 * (t_top + t_bot)
    comps = [c for c in ORG if feed[c] > 1e-12]
    alpha = {c: psat(c, tm) / psat(hk, tm) for c in comps}
    zf = {c: feed[c] / sum(feed[d] for d in comps) for c in comps}
    theta = brentq(lambda th: sum(alpha[c] * zf[c] / (alpha[c] - th) for c in comps), 1.0 + 1e-9, alpha[lk] - 1e-9)
    xd = {c: top[c] / sum(top[d] for d in comps) for c in comps}
    rmin = sum(alpha[c] * xd[c] / (alpha[c] - theta) for c in comps) - 1
    r = max(R_FACTOR * rmin, R_FLOOR)
    q_cond = (r + 1) * sum(top[c] * hvap(c, t_top) for c in comps) / 3600
    q_reb = q_cond + H_liq(top, t_top) + H_liq(bot, t_bot) - h_feed
    return dict(t_top=t_top, t_bot=t_bot, rmin=rmin, r=r, q_cond=q_cond, q_reb=q_reb)


def react(n):
    eb = n["EB"]
    out = dict(n)
    xi = {k: X_BED * s * eb for k, s in SEL.items()}  # mol EB per reaction
    out["EB"] -= X_BED * eb
    out["SM"] += xi["DH"]
    out["H2"] += xi["DH"] - xi["TOL"]
    out["TOL"] += xi["TOL"]
    out["CH4"] += xi["TOL"]
    out["BZ"] += xi["BZ"]
    out["C2H4"] += xi["BZ"] + xi["TAR"]        # TAR: 2 EB -> BIPH + 2 C2H4 + H2
    out["H2"] += xi["TAR"] / 2
    out["BIPH"] += xi["TAR"] / 2
    return out


def ln_q_over_k(n, t, p):
    dg = h_ig1("SM", t) + h_ig1("H2", t) - h_ig1("EB", t) - t * (s_ig1("SM", t) + s_ig1("H2", t) - s_ig1("EB", t))
    lnk = -dg / (R * t)
    y = {c: n[c] / tot(n) for c in ("SM", "H2", "EB")}
    return math.log(y["SM"] * y["H2"] / y["EB"] * p / 100.0) - lnk


def compress(gas, p_in, p_out, stages=1):
    """Compression (D-007: one stage, K-101), ideal gas; cooling to T_SEP after each stage
    (E-104) and the condensate knocked out (V-102)."""
    ratio = (p_out / p_in) ** (1 / stages)
    work, cool, cond = 0.0, 0.0, z()
    p, g = p_in, dict(gas)
    t_out = []
    for _ in range(stages):
        p2 = p * ratio
        s1 = sum(g[c] * (s_ig1(c, T_SEP) - R * math.log(p / 100 * g[c] / tot(g))) for c in C if g[c] > 0)
        t2s = brentq(lambda t: sum(g[c] * (s_ig1(c, t) - R * math.log(p2 / 100 * g[c] / tot(g))) for c in C if g[c] > 0) - s1, T_SEP, 900)
        dh = (H_gas(g, t2s) - H_gas(g, T_SEP)) / ETA_K
        t2 = t_from(H_gas, g, H_gas(g, T_SEP) + dh, T_SEP, 1000)
        work += dh
        t_out.append(t2)
        vap, lo, lw = flash_immiscible(g, T_SEP, p2)
        liq = add(lo, lw)
        cool += H_gas(g, t2) - H_gas(vap, T_SEP) - H_liq(liq, T_SEP)
        cond = add(cond, liq)
        g, p = vap, p2
    return g, cond, work, cool, t_out


def plant(fresh_eb, rec):
    st = {}
    s1 = z(); s1["EB"] = fresh_eb
    s2 = add(s1, rec)
    steam = STEAM_RATIO * s2["EB"] * MW["EB"] / MW["H2O"]
    s3 = z(); s3["H2O"] = steam
    s4, s5 = scale(s3, PRIMARY), scale(s3, 1 - PRIMARY)
    st.update(S1=s1, S2=s2, S3=s3, S4=s4, S5=s5)
    s13 = add(s2, s3)
    s14 = react(s13)
    s16 = react(s14)
    st.update(S13=s13, S14=s14, S15=s14, S16=s16, S17=s16, S18=s16)
    vap, lo, lw = flash_immiscible(s16, T_SEP, P_SEP)
    st.update(S19=vap, S20=add(lo, lw))
    gas, cond, wk, qk, tk = compress(vap, P_SEP, P_K101)
    st.update(S21=gas, S22=cond, k101=(wk, qk, tk))
    s23 = add(st["S20"], cond)
    st["S23"] = s23
    # decanter X-101
    org = {c: s23[c] for c in ORG}
    xorg = {c: org[c] / sum(org.values()) for c in ORG}
    water_kg = s23["H2O"] * MW["H2O"]
    aq, og = z(), z()
    for c in C:
        if c in ORG:
            dissolved = xorg[c] * SOLUBILITY[c] * 1e-6 * water_kg / MW[c]
            aq[c], og[c] = dissolved, s23[c] - dissolved
        else:
            aq[c] = s23[c]          # water and the dissolved light gases to the condensate (D-008)
    st.update(S24=aq, S25=og, S26=og)
    # columns
    t301, b301 = split(og, "TOL", "EB", COLS["C301"][2], COLS["C301"][3])
    t304, b304 = split(t301, "BZ", "TOL", COLS["C304"][2], COLS["C304"][3])
    t302, b302 = split(b301, "EB", "SM", COLS["C302"][2], COLS["C302"][3])
    x_sm_tar = (TAR_SM_WT / MW["SM"]) / (TAR_SM_WT / MW["SM"] + (1 - TAR_SM_WT) / MW["BIPH"])
    t303, b303 = split(b302, "SM", "BIPH", x_sm_tar, COLS["C303"][3])
    st.update(S27=t301, S28=b301, S29=t304, S30=b304, S31=t302, S32=t302, S33=b302, S34=t303, S35=b303)
    st["x_sm_tar"] = x_sm_tar
    return st


def solve():
    rec = z(); rec["EB"] = 50.0
    for it in range(500):
        st = plant(100.0, rec)
        new = st["S32"]
        err = max(abs(new[c] - rec[c]) for c in C)
        rec = new
        if err < 1e-10:
            break
    st = plant(100.0, rec)
    f = PRODUCT_KG_H / mass(st["S34"])
    S = {k: (scale(v, f) if isinstance(v, dict) and set(v) == set(C) else v) for k, v in st.items()}
    S["k101"] = (st["k101"][0] * f, st["k101"][1] * f, st["k101"][2])
    return S, it, err


def main():
    S, iters, err = solve()
    q, T = {}, {}
    # ---- feed side
    # D-003: the dilution steam arrives 3 K above saturation (so that no model sees it as liquid)
    t_sat = brentq(lambda t: psat("H2O", t) - P_STEAM, 350, 500) + 3.0
    T.update(S1=T_EB, S3=t_sat, S4=t_sat, S5=t_sat, S9=t_sat)
    t_rec = bubble_t(S["S31"], COLS["C302"][4])           # C-302 distillate, pump rise neglected
    T["S31"] = T["S32"] = t_rec
    h_s2 = H_liq(S["S1"], T_EB) + H_liq(S["S32"], t_rec)
    T["S2"] = t_from(H_liq, S["S2"], h_s2, 250, 450)
    h_s7 = h_s2 + H_gas(S["S4"], t_sat)                  # M-101 and VL-101 adiabatic
    S["S6"] = S["S7"] = add(S["S2"], S["S4"])
    S["S8"] = S["S7"]
    q["E101"] = H_gas(S["S8"], T_E101_COLD) - h_s7
    T["S8"] = T_E101_COLD
    # mixing at R-101 inlet: the main steam temperature that gives T_RIN
    h13 = H_gas(S["S13"], T_RIN)
    t_c = t_from(H_gas, S["S5"], h13 - H_gas(S["S8"], T_E101_COLD), 600, 1600)
    T.update(S12=t_c, S13=T_RIN)
    T["S14"] = t_from(H_gas, S["S14"], h13, 500, 1000)
    q["E102"] = H_gas(S["S15"], T_RIN) - H_gas(S["S14"], T["S14"])
    T["S15"] = T_RIN
    T["S16"] = t_from(H_gas, S["S16"], H_gas(S["S15"], T_RIN), 500, 1000)
    T["S10"] = T_SSH1
    T["S11"] = t_from(H_gas, S["S5"], H_gas(S["S5"], T_SSH1) - q["E102"], 400, 1200)
    q["H101A"] = H_gas(S["S5"], T_SSH1) - H_gas(S["S5"], t_sat)
    q["H101B"] = H_gas(S["S5"], t_c) - H_gas(S["S5"], T["S11"])
    T["S17"] = t_from(H_gas, S["S16"], H_gas(S["S16"], T["S16"]) - q["E101"], 300, 1000)
    vap, lo, lw = flash_immiscible(S["S16"], T_SEP, P_SEP)
    h18 = H_gas(vap, T_SEP) + H_liq(add(lo, lw), T_SEP)
    q["E103"] = H_gas(S["S16"], T["S17"]) - h18
    T.update(S18=T_SEP, S19=T_SEP, S20=T_SEP, S21=T_SEP, S22=T_SEP, S23=T_SEP, S24=T_SEP, S25=T_SEP)
    q["K101"], q["K101_cool"], t_k = S["k101"]
    # ---- burners: natural gas so that the flue gas leaves at T_STACK
    fuel_gas = S["S21"]
    o2_per = {"H2": 0.5, "CH4": 2, "C2H4": 3, "BZ": 7.5, "TOL": 9, "EB": 10.5, "SM": 10}
    co2_per = {"CH4": 1, "C2H4": 2, "BZ": 6, "TOL": 7, "EB": 8, "SM": 8}
    h2o_per = {"H2": 1, "CH4": 2, "C2H4": 2, "BZ": 3, "TOL": 4, "EB": 5, "SM": 4}

    def burn(ng):
        fuel = dict(fuel_gas); fuel["CH4"] += ng
        o2 = sum(fuel[c] * o2_per[c] for c in o2_per) * (1 + EXCESS_AIR)
        air = z(); air["O2"] = o2; air["N2"] = o2 * (1 - Y_O2_AIR) / Y_O2_AIR
        ngs = z(); ngs["CH4"] = ng
        fg = z()
        fg["N2"] = air["N2"]
        fg["O2"] = o2 - sum(fuel[c] * o2_per[c] for c in o2_per)
        fg["CO2"] = sum(fuel[c] * co2_per[c] for c in co2_per)
        fg["H2O"] = fuel["H2O"] + sum(fuel[c] * h2o_per[c] for c in h2o_per)
        h_in = H_gas(fuel_gas, T_SEP) + H_gas(ngs, T_NG) + H_gas(air, T_AIR)
        return ngs, air, fg, h_in

    def stack_resid(ng):
        ngs, air, fg, h_in = burn(ng)
        return h_in - q["H101B"] - q["H101A"] - H_gas(fg, T_STACK)

    ng = brentq(stack_resid, 0.0, 5000.0)
    ngs, air, fg, h_in = burn(ng)
    S.update(S36=ngs, S37=air, S38=add(fuel_gas, ngs, air), S39=fg, S40=fg, S41=fg)
    T["S39"] = t_from(H_gas, fg, h_in, 800, 3000)
    T["S40"] = t_from(H_gas, fg, h_in - q["H101B"], 400, 3000)
    T["S41"] = T_STACK
    T.update(S36=T_NG, S37=T_AIR)
    # ---- columns
    t301 = bubble_t(S["S28"], COLS["C301"][5])
    c301 = column(S["S26"], S["S27"], S["S28"], "TOL", "EB", COLS["C301"][4], COLS["C301"][5], H_liq(S["S26"], T_SEP))
    c304 = column(S["S27"], S["S29"], S["S30"], "BZ", "TOL", COLS["C304"][4], COLS["C304"][5], H_liq(S["S27"], c301["t_top"]))
    c302 = column(S["S28"], S["S31"], S["S33"], "EB", "SM", COLS["C302"][4], COLS["C302"][5], H_liq(S["S28"], c301["t_bot"]))
    c303 = column(S["S33"], S["S34"], S["S35"], "SM", "BIPH", COLS["C303"][4], COLS["C303"][5], H_liq(S["S33"], c302["t_bot"]))
    cols = {"C301": c301, "C304": c304, "C302": c302, "C303": c303}
    T.update(S27=c301["t_top"], S28=c301["t_bot"], S29=c304["t_top"], S30=c304["t_bot"], S33=c302["t_bot"],
             S34=c303["t_top"], S35=c303["t_bot"])
    # pumps (power from volume flow; temperature rise neglected)
    def pump(n, t, dp):
        vol = sum(n[c] * vliq(c, t) for c in ORG if n[c] > 0) * 1e3 / 3600  # m3/s
        return vol * dp / ETA_P
    q["P201"] = pump(S["S25"], T_SEP, P_C301_FEED - P_SEP)
    q["P302"] = pump(S["S31"], t_rec, P_RECYCLE - COLS["C302"][4])
    for k, c in cols.items():
        q[k + "_reb"], q[k + "_cond"] = c["q_reb"], c["q_cond"]

    # ---- checks
    sm_t = mass(S["S34"]) / 1000
    lhv = {"H2": 241822.0, "CH4": 802584.0, "C2H4": 1323152.0, "BZ": 3169490.0, "TOL": 3772016.0, "EB": 4386802.0, "SM": 4262980.0}
    lhv_fuelgas = sum(fuel_gas[c] * lhv.get(c, 0) for c in C) / 3600
    lhv_ng = ng * lhv["CH4"] / 3600
    ssh_abs = q["H101A"] + q["H101B"]
    steam_heat = S["S3"]["H2O"] * MW["H2O"] * 2.717571 / 3.6   # kWh/h above 15 C water (lci/mappings steam-mp)
    lps = sum(q[k + "_reb"] for k in cols)
    cw = q["E103"] + q["K101_cool"] + sum(q[k + "_cond"] for k in cols)
    power = q["K101"] + q["P201"] + q["P302"]
    h_in = (H_liq(S["S1"], T_EB) + H_gas(S["S3"], t_sat) + H_gas(ngs, T_NG) + H_gas(air, T_AIR) + power + lps)
    h_out = (H_gas(fg, T_STACK) + H_liq(S["S24"], T_SEP) + H_liq(S["S29"], T["S29"]) + H_liq(S["S30"], T["S30"])
             + H_liq(S["S34"], T["S34"]) + H_liq(S["S35"], T["S35"]) + cw)
    eq = {"R101_out": ln_q_over_k(S["S14"], T["S14"], 75.0), "R102_out": ln_q_over_k(S["S16"], T["S16"], 60.0)}
    checks = {
        "recycle_iterations": iters, "recycle_residual": err,
        "per_t_styrene": {
            "ethylbenzene_kg": mass(S["S1"]) / sm_t,
            "toluene_product_kg": mass(S["S30"]) / sm_t,
            "benzene_product_kg": mass(S["S29"]) / sm_t,
            "tar_kg": mass(S["S35"]) / sm_t,
            "dilution_steam_kg": mass(S["S3"]) / sm_t,
            "dilution_steam_heat_kWh": steam_heat / sm_t,
            "reboiler_LP_steam_kWh": lps / sm_t,
            "steam_total_kWh": (steam_heat + lps) / sm_t,
            "natural_gas_kg": mass(ngs) / sm_t,
            "natural_gas_LHV_kWh": lhv_ng / sm_t,
            "off_gas_LHV_kWh": lhv_fuelgas / sm_t,
            "fuel_total_LHV_kWh": (lhv_ng + lhv_fuelgas) / sm_t,
            "electricity_kWh": power / sm_t,
            "cooling_water_kWh": cw / sm_t,
            "process_condensate_kg": mass(S["S24"]) / sm_t,
            "CO2_kg": fg["CO2"] * MW["CO2"] / sm_t,
            "hydrogen_formed_kg": (S["S16"]["H2"]) * MW["H2"] / sm_t,
        },
        "overall_EB_conversion": 1 - S["S16"]["EB"] / S["S13"]["EB"],
        "styrene_yield_mol_per_mol_EB_fed": S["S34"]["SM"] / S["S1"]["EB"],
        "styrene_product_wt_purity": S["S34"]["SM"] * MW["SM"] / mass(S["S34"]),
        "steam_to_EB_mass": mass(S["S3"]) / (S["S13"]["EB"] * MW["EB"]),
        "SSH_absorbed_kW": ssh_abs, "SSH_efficiency_LHV": ssh_abs / (lhv_ng + lhv_fuelgas),
        "flame_T_K": T["S39"], "main_steam_SSH2_out_K": t_c,
        "ln_Q_over_K_DH": eq,
        "aromatics_in_condensate_kg_h": sum(S["S24"][c] * MW[c] for c in ORG),
        "aromatics_to_burners_kg_h": sum(S["S21"][c] * MW[c] for c in ORG),
        "decanter_recovery_to_water": {c: S["S24"][c] / S["S23"][c] for c in ORG if S["S23"][c] > 0},
        "x_sm_tar": S["x_sm_tar"],
        "K101_outlet_T_K": t_k,
        # specified splits of simulation.yaml (D-008): V-101 and V-102 vapour recoveries
        "V101_recovery_to_vapour": {c: S["S19"][c] / S["S16"][c] for c in C if S["S16"][c] > 0},
        "V102_recovery_to_gas": {c: S["S21"][c] / S["S19"][c] for c in C if S["S19"][c] > 0},
        "mass_in_kg_h": mass(S["S1"]) + mass(S["S3"]) + mass(ngs) + mass(air),
        "mass_out_kg_h": sum(mass(S[k]) for k in ("S24", "S29", "S30", "S34", "S35", "S41")),
        "energy_in_kW": h_in, "energy_out_kW": h_out,
        "columns": cols,
    }
    out = {"streams": {}, "duties_kW": q, "checks": checks}
    for sid in sorted((k for k in S if k.startswith("S") and isinstance(S[k], dict)), key=lambda s: int(s[1:])):
        n = S[sid]
        if tot(n) <= 0:
            continue
        out["streams"][sid] = {"T_K": round(T.get(sid, float("nan")), 2), "kmol_h": round(tot(n), 4), "kg_h": round(mass(n), 2),
                               "y": {c: round(n[c] / tot(n), 8) for c in C if n[c] > 1e-12}}
    print(json.dumps(out, indent=1, default=float))
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/sm_balance.json").write_text(json.dumps(out, indent=1, default=float))
    # the values process/flowsheet.yaml cites from this script (balance-output contract)
    fs = {
        "S1": {"flow": mass(S["S1"])},
        "S3": {"flow": mass(S["S3"])},
        "S36": {"flow": mass(ngs)},
        "S37": {"flow": mass(air)},
        # off-gas compression, excluded from the simulation (D-012)
        "S21": {"flow": mass(S["S21"]), "temperature": T_SEP, "pressure": P_K101,
                "composition": {c: S["S21"][c] / tot(S["S21"]) for c in C if S["S21"][c] > 1e-12}},
        "S22": {"flow": mass(S["S22"]), "temperature": T_SEP, "pressure": P_K101,
                "composition": {c: S["S22"][c] / tot(S["S22"]) for c in C if S["S22"][c] > 1e-12}},
        "Q3": {"duty": q["K101"]},
        "Q5": {"duty": q["K101_cool"]},
    }
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}", "cases": {"design": fs}}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
