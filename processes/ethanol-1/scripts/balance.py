"""Concept heat and material balance of ethanol-1 (ethylene direct hydration), DESIGN.md D-006.

An independent estimate, not a qualified simulation (no property package of
cheme-as-code covers ethylene/water/ethanol at loop pressure). What it does:
- solves the recycle loops (reaction gas loop, flash-gas return, water loop, sieve
  regeneration return) by successive substitution;
- reactor R-101: conversion of ethylene and selectivities (D-004), adiabatic, ideal gas with
  the ideal-gas data of process/materials.yaml;
- separators V-101, C-101, V-102, C-201, C-202, V-301 and the splitters: specified component
  splits (ASSUMED, D-005);
- duties: ideal-gas enthalpies plus latent heats (Watson) of the components that condense,
  water partial condensation/evaporation in E-101 by Raoult's law on water only; heats of
  mixing and non-ideal VLE ignored (D-006). Compressors ideal gas, isentropic efficiency 0.75.

Run: cheme run scripts/balance.py  (writes build/balance.txt and prints the stream values)
"""

import math
import os

R = 8.314462618  # kJ/(kmol K)
C = ["C2H4", "C2H6", "CH4", "H2O", "ETOH", "DEE", "C4H8"]
MW = {"C2H4": 28.053, "C2H6": 30.069, "CH4": 16.042, "H2O": 18.015, "ETOH": 46.068,
      "DEE": 74.122, "C4H8": 56.106}
# ideal gas: dHf_298 (kJ/kmol) and cp/R polynomial (Poling 5th ed., via `cheme chemistry thermo`)
HF = {"C2H4": 52560.0, "C2H6": -83780.0, "CH4": -74534.0, "H2O": -241822.0,
      "ETOH": -234570.0, "DEE": -252100.0, "C4H8": -30.0}
CP = {"C2H4": [4.221, -0.008782, 5.795e-05, -6.729e-08, 2.511e-11],
      "C2H6": [4.178, -0.004427, 5.66e-05, -6.651e-08, 2.487e-11],
      "CH4": [4.568, -0.008975, 3.631e-05, -3.407e-08, 1.091e-11],
      "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
      "ETOH": [4.396, 0.000628, 5.546e-05, -7.024e-08, 2.685e-11],
      "DEE": [4.612, 0.037492, -1.87e-05, 1.316e-08, -6.98e-12],
      "C4H8": [4.389, 0.007984, 6.143e-05, -8.2e-08, 3.165e-11]}
# latent heat at Tb (kJ/kmol), Tb, Tc for Watson (NIST WebBook / CRC values, D-006)
LAT = {"H2O": (40657.0, 373.15, 647.1), "ETOH": (38560.0, 351.4, 514.7),
       "DEE": (26520.0, 307.6, 466.7)}
CPL = {"H2O": 75.4, "ETOH": 112.0, "DEE": 172.0}  # liquid cp kJ/(kmol K), 298 K (ASSUMED constant)


def h_ig(c, T):
    a = CP[c]
    t0 = 298.15
    s = sum(a[i] / (i + 1) * (T ** (i + 1) - t0 ** (i + 1)) for i in range(5))
    return HF[c] + R * s


def cp_ig(c, T):
    return R * sum(a * T ** i for i, a in enumerate(CP[c]))


def dhv(c, T):
    h, tb, tc = LAT[c]
    return h * ((tc - T) / (tc - tb)) ** 0.38


def psat_water(T):
    """kPa; Antoine, NIST WebBook (Bridgeman and Aldrich 1964), 379-573 K; below that 304-333 K set."""
    if T >= 379.0:
        return 100.0 * 10 ** (3.55959 - 643.748 / (T - 198.043))
    return 100.0 * 10 ** (5.40221 - 1838.675 / (T - 31.737))


def H(stream, T, liq=None):
    """Enthalpy kJ/h; liq: dict component -> kmol/h in the liquid (latent heat removed)."""
    h = sum(n * h_ig(c, T) for c, n in stream.items())
    for c, nl in (liq or {}).items():
        h -= nl * dhv(c, T)
    return h


def add(*ss):
    out = {c: 0.0 for c in C}
    for s in ss:
        for c in C:
            out[c] += s.get(c, 0.0)
    return out


def scale(s, f):
    return {c: s.get(c, 0.0) * (f[c] if isinstance(f, dict) else f) for c in C}


def mass(s):
    return sum(s[c] * MW[c] for c in C)


def water_liq(s, T, P):
    """kmol/h of water condensed at T, P: Raoult on water, everything else non-condensable."""
    inert = sum(v for c, v in s.items() if c != "H2O")
    y = min(psat_water(T) / P, 0.999)
    vmax = y / (1 - y) * inert
    return max(s["H2O"] - vmax, 0.0)


# ------------------------------------------------------------------ specifications
P_LOOP_IN = 7050.0       # reactor inlet kPa(a), ~1000 psi (US 4003952; US 5349096 6895 kPa examples) D-003
T_RIN = 513.15           # reactor inlet 240 C (US 5349096 example: inlet 240 C, exit 260 C) D-003
WATER_RATIO = 0.35       # H2O/C2H4 mol at reactor inlet (US 5349096 preferred 0.30-0.40) D-003
X_C2H4 = 0.05            # ethylene converted per pass (US 4003952: 4-5 % per pass) D-004
SEL = {"ETOH": 0.97, "DEE": 0.01, "C4H8": 0.005}  # kmol per kmol C2H4 converted, ASSUMED D-004
FRESH = {"C2H4": 0.999, "C2H6": 0.0008, "CH4": 0.0002}  # polymer-grade ethylene, ASSUMED D-002
ETOH_PRODUCT = 12475.0   # kg/h ethanol in the product (12 500 kg/h at 99.8 wt%), D-002
PURGE = 0.001          # fraction of scrubbed gas purged, ASSUMED D-005
WW_FRAC = 0.10           # fraction of C-202 bottoms to wastewater, ASSUMED D-005
WASH = 3600.0 / MW["H2O"]  # kmol/h scrubber wash water, ASSUMED D-005
REFLUX_C202 = 3.0        # reflux ratio, ASSUMED D-005
BOILUP_C201 = 0.05       # kmol vapour per kmol feed, ASSUMED D-005
TOP_WT = 0.93            # C-202 top vapour ethanol wt%, ASSUMED D-005
REGEN = 0.18             # fraction of sieve feed ethanol in the regeneration return, ASSUMED D-005
ETA = 0.75               # compressor isentropic efficiency, ASSUMED
ETA_PUMP = 0.65          # pump efficiency, ASSUMED
DT_MIN = 10.0            # E-101 / E-201 minimum approach, ASSUMED

# fractions to the liquid / bottoms / top (ASSUMED, D-005)
V101_LIQ = {"C2H4": 0.002, "C2H6": 0.002, "CH4": 0.001, "H2O": 0.998, "ETOH": 0.97,
            "DEE": 0.40, "C4H8": 0.03}
C101_BOT = {"C2H4": 0.0006, "C2H6": 0.0006, "CH4": 0.0003, "H2O": 0.0, "ETOH": 0.99,
            "DEE": 0.80, "C4H8": 0.05}
V102_GAS = {"C2H4": 0.98, "C2H6": 0.98, "CH4": 0.99, "H2O": 0.0005, "ETOH": 0.005,
            "DEE": 0.30, "C4H8": 0.90}
C201_TOP = {"C2H4": 1.0, "C2H6": 1.0, "CH4": 1.0, "H2O": 0.002, "ETOH": 0.01, "DEE": 0.99,
            "C4H8": 1.0}

# ------------------------------------------------------------------ solve
Z = {c: 0.0 for c in C}
fresh_n = 300.0
rec = dict(Z)        # S15 recycle gas to M101
flash = dict(Z)      # S34 flash gas to M101
regen = dict(Z)      # S27
wrec = {**Z, "H2O": 2000.0}  # S26 recycled water
for it in range(60000):
    S1 = scale(FRESH, fresh_n)
    S2 = add(S1, rec, flash)
    water_need = WATER_RATIO * S2["C2H4"] - S2["H2O"]
    # water loop: M104 (S26 + make-up S28) -> P101 -> SPL3 -> wash S20 + reactor S31
    S31 = {**Z, "H2O": water_need}
    S20 = {**Z, "H2O": WASH}
    S30 = add(S31, S20)
    S28 = {**Z, "H2O": max(S30["H2O"] - wrec["H2O"], 0.0)}
    S29 = add(wrec, S28)
    # small ethanol in recycled water goes with the reactor water (pro rata)
    f_rx = S31["H2O"] / S30["H2O"]
    S31 = scale(S29, f_rx)
    S20 = scale(S29, 1 - f_rx)
    S30 = add(S31, S20)
    S3 = add(S2, S31)
    S5 = dict(S3)
    xi = X_C2H4 * S5["C2H4"]
    S6 = dict(S5)
    S6["C2H4"] -= xi
    S6["ETOH"] += SEL["ETOH"] * xi
    S6["DEE"] += SEL["DEE"] * xi
    S6["C4H8"] += SEL["C4H8"] * xi
    S6["H2O"] -= SEL["ETOH"] * xi + SEL["DEE"] * xi
    S8 = S6
    S10 = scale(S8, V101_LIQ)
    S9 = {c: S8[c] - S10[c] for c in C}
    S12 = add(scale(S9, C101_BOT), S20)
    S11 = {c: S9[c] + S20[c] - S12[c] for c in C}
    S13 = scale(S11, PURGE)
    S14 = {c: S11[c] - S13[c] for c in C}
    feed_v102 = add(S10, S12)
    S16 = scale(feed_v102, V102_GAS)
    S18 = {c: feed_v102[c] - S16[c] for c in C}
    S19 = scale(S18, C201_TOP)
    S21 = {c: S18[c] - S19[c] for c in C}
    feed_c202 = add(S21, regen)
    # C-202: bottoms water with 100 ppm(wt) ethanol, all DEE and light ends to the top
    wb = feed_c202["H2O"]
    for _ in range(5):
        top_etoh = feed_c202["ETOH"] - 100e-6 * (wb * MW["H2O"]) / MW["ETOH"]
        top_w = top_etoh * MW["ETOH"] * (1 - TOP_WT) / TOP_WT / MW["H2O"]
        wb = feed_c202["H2O"] - top_w
    S22 = {**Z, "ETOH": top_etoh, "H2O": top_w, "DEE": feed_c202["DEE"],
           "C4H8": feed_c202["C4H8"], "C2H4": feed_c202["C2H4"], "C2H6": feed_c202["C2H6"],
           "CH4": feed_c202["CH4"]}
    S24 = {**Z, "H2O": wb, "ETOH": feed_c202["ETOH"] - top_etoh}
    # V-301: product ethanol, 0.2 wt% water; regeneration return the rest
    p_etoh = S22["ETOH"] * (1 - REGEN)
    p_other = (S22["DEE"] + S22["C4H8"]) and (S22["DEE"] * MW["DEE"] + S22["C4H8"] * MW["C4H8"])
    p_w = (p_etoh * MW["ETOH"] + p_other) * 0.002 / 0.998 / MW["H2O"]
    S23 = {**Z, "ETOH": p_etoh, "H2O": p_w, "DEE": S22["DEE"], "C4H8": S22["C4H8"],
           "C2H4": S22["C2H4"], "C2H6": S22["C2H6"], "CH4": S22["CH4"]}
    regen_new = {c: S22[c] - S23[c] for c in C}
    S25 = scale(S24, WW_FRAC)
    wrec_new = {c: S24[c] - S25[c] for c in C}
    # update
    err = abs(mass(S14) - mass(rec)) + abs(mass(S16) - mass(flash)) + abs(mass(wrec_new) - mass(wrec))
    rec, flash, regen, wrec = S14, S16, regen_new, wrec_new
    fresh_n *= (ETOH_PRODUCT / (S23["ETOH"] * MW["ETOH"])) ** 0.7
    if it > 50 and err < 1e-6 and abs(S23["ETOH"] * MW["ETOH"] - ETOH_PRODUCT) < 1e-6:
        break
S15, S34 = S14, S16
S26 = wrec

# ------------------------------------------------------------------ energy
P = {"S1": 7300, "S15": 7300, "S34": 7300, "S2": 7300, "S31": 7300, "S3": 7250, "S4": 7150,
     "S5": P_LOOP_IN, "S6": 6950, "S7": 6900, "S8": 6850, "S9": 6850, "S10": 6850,
     "S20": 7300, "S11": 6800, "S12": 6800, "S13": 6800, "S14": 6800, "S16": 300, "S18": 300,
     "S35": 280, "S19": 250, "S21": 270, "S22": 200, "S24": 230, "S36": 210, "S25": 200,
     "S26": 200, "S28": 400, "S29": 200, "S30": 7350, "S23": 150, "S27": 300}

# reactor outlet temperature (adiabatic, all vapour)
h_in = H(S5, T_RIN)
lo, hi = T_RIN, T_RIN + 100
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if H(S6, mid) < h_in else (lo, mid)
T_ROUT = (lo + hi) / 2

# cold side S3 -> S4 and hot side S6 -> S7 of E-101 (water partial evaporation/condensation)
T_S3 = None
# S3: gas at ~320 K mixed with water at 323 K, water mostly liquid
T_GAS = 318.15  # M101 outlet ASSUMED (fresh gas 303 K, recycle after K-101)
# process water: recycled water after E-201 (T_SEP + 15 K) mixed with make-up at 303.15 K
T_W = ((313.15 + 15.0) * S26["H2O"] + 303.15 * S28["H2O"]) / (S26["H2O"] + S28["H2O"])


def h_cold(T):
    wl = water_liq(S3, T, P["S3"])
    return H(S3, T, {"H2O": wl})


def h_hot(T):
    wl = water_liq(S6, T, P["S6"])
    return H(S6, T, {"H2O": wl})


# S3 temperature from adiabatic mixing of S2 (gas) and S31 (liquid water)
h_mix = H(S2, T_GAS) + H(S31, T_W, {"H2O": S31["H2O"], "ETOH": S31["ETOH"]})
lo, hi = 280.0, 400.0
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if h_cold(mid) < h_mix else (lo, mid)
T_S3 = (lo + hi) / 2


def e101_min_dt(tc_out):
    q = h_cold(tc_out) - h_cold(T_S3)
    target = h_hot(T_ROUT) - q
    lo, hi = 300.0, T_ROUT
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if h_hot(mid) < target else (lo, mid)
    th_out = (lo + hi) / 2
    dmin = 1e9
    for k in range(101):  # along the exchanger, counter-current
        tc = T_S3 + (tc_out - T_S3) * k / 100
        qk = h_cold(tc) - h_cold(T_S3)
        hh = h_hot(th_out) + qk
        lo2, hi2 = 280.0, T_ROUT + 1
        for _ in range(60):
            m = (lo2 + hi2) / 2
            lo2, hi2 = (m, hi2) if h_hot(m) < hh else (lo2, m)
        dmin = min(dmin, (lo2 + hi2) / 2 - tc)
    return dmin, q, th_out


lo, hi = T_S3 + 1, T_RIN
for _ in range(40):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if e101_min_dt(mid)[0] > DT_MIN else (lo, mid)
T_S4 = lo
dmin, Q_E101, T_S7 = e101_min_dt(T_S4)
Q_E102 = h_cold(T_RIN) - h_cold(T_S4)
# E-103: S7 -> 313.15 K, condensed amounts = V-101 liquid
T_SEP = 313.15
liq7 = {"H2O": water_liq(S6, T_S7, P["S7"])}
liq8 = {c: S10[c] for c in ("H2O", "ETOH", "DEE")}
Q_E103 = H(S6, T_S7, liq7) - H(S6, T_SEP, liq8)

# compressors (ideal gas)


def compress(s, T1, P1, P2, stages=1):
    n = sum(s.values()) / 3600.0  # kmol/s
    w = 0.0
    T = T1
    qc = 0.0
    r = (P2 / P1) ** (1.0 / stages)
    for k in range(stages):
        cpm = sum(s[c] * cp_ig(c, T) for c in C) / sum(s.values())
        g = cpm / (cpm - R)
        t2s = T * r ** ((g - 1) / g)
        t2 = T + (t2s - T) / ETA
        w += n * cpm * (t2 - T)
        if k < stages - 1:
            qc += n * cpm * (t2 - T1)
            T = T1
        else:
            T = t2
    return w, T, qc


W_K101, T_S15, _ = compress(S14, T_SEP, P["S14"], P["S15"])
W_K102, T_K102, Q_K102 = compress(S16, T_SEP, P["S16"], P["S34"], stages=3)
Q_K102 += sum(S16[c] * cp_ig(c, T_K102) for c in C) / 3600 * (T_K102 - T_SEP)  # aftercooler
T_S34 = T_SEP
vol_w = mass(S29) / 985.0 / 3600.0  # m3/s
W_P101 = vol_w * (P["S30"] - P["S29"]) / ETA_PUMP

# E-201: crude S18 (313 K) heated by C-202 bottoms S24 (bubble ~ 398 K at 230 kPa ASSUMED)
T_S24 = 398.15
T_S36 = T_SEP + 15.0
cpl = lambda s: sum(s.get(c, 0.0) * CPL.get(c, 0.0) for c in C)
Q_E201 = cpl(S24) * (T_S24 - T_S36) / 3600.0
T_S35 = T_SEP + Q_E201 * 3600.0 / cpl(S18)
T_C201_BUB = 368.15  # ASSUMED crude bubble point at 280 kPa
Q_C201 = (cpl(S18) * max(T_C201_BUB - T_S35, 0) + BOILUP_C201 * sum(S18.values()) * dhv("H2O", T_C201_BUB)) / 3600.0
Q_C201_COND = BOILUP_C201 * sum(S18.values()) * dhv("H2O", 330.0) / 3600.0
D = sum(S22.values())
lam = (S22["ETOH"] * dhv("ETOH", 368.0) + S22["H2O"] * dhv("H2O", 368.0)) / D
Q_C202 = ((REFLUX_C202 + 1) * D * lam + cpl(regen) * (368.15 - 313.15)) / 3600.0
Q_C202_COND = REFLUX_C202 * D * lam / 3600.0
# V-301: product and regeneration vapour condensed and cooled to 313 K; vacuum pump ASSUMED
Q_V301 = (sum(S22[c] * dhv(c, 340.0) for c in ("ETOH", "H2O")) + cpl(S22) * (368.15 - 313.15)) / 3600.0
W_V301 = 75.0  # kW, vacuum pump of the regeneration, ASSUMED

T = {"S1": 303.15, "S15": T_S15, "S34": T_S34, "S2": T_GAS, "S31": T_W, "S3": T_S3, "S4": T_S4,
     "S5": T_RIN, "S6": T_ROUT, "S7": T_S7, "S8": T_SEP, "S9": T_SEP, "S10": T_SEP, "S20": T_W,
     "S11": T_SEP, "S12": T_SEP, "S13": T_SEP, "S14": T_SEP, "S16": T_SEP, "S18": T_SEP,
     "S35": T_S35, "S19": 320.15, "S21": 403.15, "S22": 368.15, "S24": T_S24, "S36": T_S36,
     "S25": T_S36, "S26": T_S36, "S28": 303.15, "S29": T_W, "S30": T_W, "S23": 313.15,
     "S27": 313.15}
streams = {"S1": S1, "S2": S2, "S3": S3, "S4": S3, "S5": S5, "S6": S6, "S7": S6, "S8": S6,
           "S9": S9, "S10": S10, "S11": S11, "S12": S12, "S13": S13, "S14": S14, "S15": S15,
           "S16": S16, "S34": S34, "S18": S18, "S35": S18, "S19": S19, "S21": S21, "S22": S22,
           "S23": S23, "S24": S24, "S36": S24, "S25": S25, "S26": S26, "S27": regen,
           "S28": S28, "S29": S29, "S30": S30, "S20": S20, "S31": S31}

out = []
w = out.append
w(f"iterations {it}, last change {err:.2e} kg/h, fresh ethylene {fresh_n:.3f} kmol/h = {mass(S1):.1f} kg/h")
w(f"reactor: inlet C2H4 {S5['C2H4']:.2f} kmol/h, extent {xi:.3f}, H2O/C2H4 {S5['H2O']/S5['C2H4']:.4f}, "
  f"T out {T_ROUT:.2f} K")
inert = (S11["C2H6"] + S11["CH4"] + S11["C4H8"]) / sum(S11.values())
w(f"loop gas inerts (C2H6+CH4+C4H8) {inert:.4f} mol/mol; recycle/fresh {sum(S15.values())/sum(S1.values()):.2f}")
w(f"split SPL1 purge {PURGE}; SPL2 ww {WW_FRAC}; SPL3 wash {S20['H2O']/S30['H2O']:.9f}")
w(f"E-101 {Q_E101/3600:.0f} kW, S3 {T_S3:.2f} K -> S4 {T_S4:.2f} K, hot out S7 {T_S7:.2f} K, min dT {dmin:.2f}")
w(f"E-102 HP steam {Q_E102/3600:.0f} kW; E-103 CW {Q_E103/3600:.0f} kW")
w(f"K-101 {W_K101:.0f} kW out {T_S15:.2f} K; K-102 {W_K102:.0f} kW cooling {Q_K102:.0f} kW; P-101 {W_P101:.0f} kW")
w(f"E-201 {Q_E201:.0f} kW, S35 {T_S35:.2f} K; C-201 reb {Q_C201:.0f} cond {Q_C201_COND:.0f} kW")
w(f"C-202 reb {Q_C202:.0f} cond {Q_C202_COND:.0f} kW (D {D:.2f} kmol/h, lambda {lam:.0f}); V-301 CW {Q_V301:.0f} kW")
prod = mass(S23)
w(f"product {prod:.2f} kg/h; ethanol {S23['ETOH']*MW['ETOH']:.2f}")
ein = mass(S1) + mass(S28)
eout = mass(S23) + mass(S13) + mass(S19) + mass(S25)
w(f"overall mass in {ein:.3f} out {eout:.3f} kg/h")
c_in = 2 * S1["C2H4"] + 2 * S1["C2H6"] + S1["CH4"]
c_out = sum(s[c] * k for s in (S23, S13, S19, S25) for c, k in
            (("C2H4", 2), ("C2H6", 2), ("CH4", 1), ("ETOH", 2), ("DEE", 4), ("C4H8", 4)))
w(f"carbon in {c_in:.4f} out {c_out:.4f} kmol/h; ethylene to ethanol product {S23['ETOH']/S1['C2H4']:.4f}")
for k, s in streams.items():
    n = sum(s.values())
    comp = ", ".join(f"{c}: {s[c]/n:.8f}" for c in C if s[c] > 0)
    w(f"{k}: T {T[k]:.2f} P {P[k]} flow {mass(s):.2f} kg/h n {n:.3f} | {{{comp}}}")
w("duties kW: " + ", ".join(f"{k} {v:.0f}" for k, v in {
    "E101": Q_E101 / 3600, "E102": Q_E102 / 3600, "E103": Q_E103 / 3600, "K101": W_K101,
    "K102": W_K102, "K102cw": Q_K102, "P101": W_P101, "E201": Q_E201, "C201reb": Q_C201,
    "C201cond": Q_C201_COND, "C202reb": Q_C202, "C202cond": Q_C202_COND, "V301cw": Q_V301,
    "V301power": W_V301}.items()))
# YAML of the streams the flowsheet gives (separator, exchanger and feed outlets, D-006)
GIVEN = ["S1", "S28", "S4", "S7", "S9", "S10", "S11", "S12", "S16", "S18", "S35", "S19", "S21",
         "S22", "S24", "S36", "S23", "S27"]
y = []
for k in GIVEN:
    s = streams[k]
    n = sum(s.values())
    comp = ", ".join(f"{c}: {s[c]/n:.8f}" for c in C if s[c] / n > 5e-9)
    y.append(f"{k}: T {T[k]:.2f} P {P[k]} | flow: {{value: {mass(s):.2f}, basis: mass}} "
             f"composition: {{basis: mole_fraction, values: {{{comp}}}}}")
os.makedirs("build", exist_ok=True)  # build/ is not in git: a fresh checkout lacks it
with open("build/streams.txt", "w") as f:
    f.write("\n".join(y) + "\n")
text = "\n".join(out)
print(text)
with open("build/balance.txt", "w") as f:
    f.write(text + "\n")


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import json
    import os
    from pathlib import Path

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


# the values process/flowsheet.yaml cites from this script (balance-output contract): streams, T
# and P as printed (mass flow, mole fractions over C), and the duties
FLOWSHEET = {}
for k, s in streams.items():
    n = sum(s.values())
    FLOWSHEET[k] = {"temperature": T[k], "pressure": P[k],
                    "flow": {"value": mass(s), "basis": "mass"},
                    "composition": {"values": {c: s[c] / n for c in C}, "basis": "mole_fraction"}}
FLOWSHEET.update({qid: {"duty": q} for qid, q in {
    "Q1": W_K101, "Q2": W_K102, "Q3": Q_K102, "Q4": Q_E102 / 3600, "Q5": Q_E103 / 3600,
    "Q6": W_P101, "Q7": Q_C201, "Q8": Q_C201_COND, "Q9": Q_C202, "Q10": Q_C202_COND,
    "Q11": Q_V301}.items()})
write_balance_output({"design": FLOWSHEET})
