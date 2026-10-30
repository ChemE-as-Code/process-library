"""Concept heat and material balance of acetylene-1 (DESIGN.md D-005..D-012).

BASF-type partial oxidation of natural gas with oxygen (Sachsse-Bartholome), water quench,
soot removal, compression and N-methylpyrrolidone (NMP) acetylene recovery, synthesis-gas
co-product. Independent of cheme-as-code's property packages, which cover neither the burner
(soot, millisecond pyrolysis) nor the NMP solvent (core #315).

Method (every number below is a design input with its source or ASSUMED, see DESIGN.md):
- burner R101: a sourced outlet-composition model. The dry cracked-gas composition of
  US8975460B2 (description, "typical" cracked gas) and the acetylene-to-soot mass ratio of
  US5824834A (comparative example 2) fix the extents of seven lumped reactions; the methane and
  oxygen feeds follow from the element balance (the O2/natural-gas ratio is a result, checked
  against the 0.58-0.75 span of US5824834A's examples). The outlet temperature is the adiabatic
  temperature on ideal-gas data (soot as graphite).
- quench Q101 and cooling column T101: the gas leaves saturated with water (NIST Antoine);
  heat released to the circulating water from the ideal-gas enthalpies plus the latent heat.
- dissolved hydrocarbons in the quench water and their vacuum flash: US11459281B2 (working
  examples: comparative emissions per t acetylene; 99.31 % depletion at 400 mbar(a)).
- compression K201: three stages, isentropic efficiency ASSUMED, ideal gas.
- NMP recovery T301-T304: component splits ASSUMED (D-009); solvent circulation from an
  acetylene loading inside the 15-35 Nm3/m3 range cited in US10059640B2 (background).
- fired preheater F101: burns the stripper off-gas, the flash gas and a natural-gas support fuel.

Run: python3 scripts/balance.py   (prints the stream table and duties; writes nothing)
"""

import math

R = 8.314462618e-3  # kJ/(mol K)

# ideal-gas data: dHf kJ/mol, cp/R polynomial, upper T of the fit (cheme chemistry thermo,
# --fit 298.15,2000 where thermo covers it; materials.yaml)
IG = {
    "CH4": (-74.534, [2.21154, 0.00601079, 3.19918e-06, -3.46333e-09, 7.84827e-13], 2000),
    "C2H2": (228.320, [2.74253, 0.0112955, -9.37674e-06, 4.2908e-09, -7.78711e-13], 2000),
    "H2": (0.0, [3.50982, -7.95931e-05, 7.57219e-08, 2.07688e-10, -7.54348e-14], 2000),
    "CO": (-110.525, [3.54627, -0.00081694, 2.55807e-06, -1.63408e-09, 3.31061e-13], 2000),
    "CO2": (-393.474, [2.48861, 0.00840651, -6.47842e-06, 2.50346e-09, -3.85623e-13], 2000),
    "H2O": (-241.822, [3.95259, -0.000330549, 2.35534e-06, -1.2066e-09, 1.93496e-13], 2000),
    "N2": (0.0, [3.63923, -0.00119537, 2.87099e-06, -1.72444e-09, 3.37502e-13], 2000),
    "AR": (0.0, [2.50001], 2000),
    "O2": (0.0, [3.07185, 0.00153231, -2.12743e-07, -3.07957e-10, 1.08232e-13], 2000),
    "C4H2": (460.370, [1.07121, 0.0414029, -6.53325e-05, 5.29069e-08, -1.66806e-11], 1000),
    "C6H6": (83.180, [3.551, -0.006184, 0.00014365, -1.9807e-07, 8.234e-11], 1000),
    "NMP": (-195.390, [-4.47654, 0.0724304, -4.16142e-05, 8.45515e-09], 1000),
}
MW = {"CH4": 16.043, "C2H2": 26.038, "H2": 2.016, "CO": 28.010, "CO2": 44.010, "H2O": 18.015,
      "N2": 28.014, "AR": 39.948, "O2": 31.999, "C4H2": 50.060, "C6H6": 78.114, "NMP": 99.133,
      "C": 12.011}
ATOMS = {"CH4": {"C": 1, "H": 4}, "C2H2": {"C": 2, "H": 2}, "H2": {"H": 2}, "CO": {"C": 1, "O": 1},
         "CO2": {"C": 1, "O": 2}, "H2O": {"H": 2, "O": 1}, "N2": {"N": 2}, "AR": {"Ar": 1},
         "O2": {"O": 2}, "C4H2": {"C": 4, "H": 2}, "C6H6": {"C": 6, "H": 6},
         "NMP": {"C": 5, "H": 9, "N": 1, "O": 1}, "C": {"C": 1}}
COMPS = list(MW)
CP_GRAPHITE = 0.0210   # kJ/(mol K), mean 298-1900 K (ASSUMED, graphite tables give 8.5-25 J/(mol K))
DHVAP_298 = 44.0       # kJ/mol water at 298.15 K
CP_LIQ_WATER = 0.0753  # kJ/(mol K)
CP_NMP_LIQ = 2.0       # kJ/(kg K), lean/rich solvent (ASSUMED, NMP about 1.7-2.1 between 300-450 K)


def cp(c, T):
    if c == "C":
        return CP_GRAPHITE
    a = IG[c][1]
    T = min(T, IG[c][2])
    return R * sum(k * T**i for i, k in enumerate(a))


def h(c, T):
    """kJ/mol, ideal gas, formation basis at 298.15 K; beyond the fit cp is held constant."""
    if c == "C":
        return CP_GRAPHITE * (T - 298.15)
    a, tmax = IG[c][1], IG[c][2]
    Tf = min(T, tmax)
    s = sum(k * (Tf**(i + 1) - 298.15**(i + 1)) / (i + 1) for i, k in enumerate(a)) * R
    if T > tmax:
        s += cp(c, tmax) * (T - tmax)
    return IG[c][0] + s


def H(stream, T):
    """kW for a stream in kmol/h (gas, soot as graphite)."""
    return sum(n * h(c, T) for c, n in stream.items() if n) / 3.6


def psat_water(T):
    """bar, NIST WebBook Antoine (Bridgeman and Aldrich 1964)."""
    A, B, C = (5.20389, 1733.926, -39.485) if T < 333.5 else (5.0768, 1659.793, -45.854)
    return 10 ** (A - B / (T + C))


def add(*ss):
    out = {}
    for s in ss:
        for c, n in s.items():
            out[c] = out.get(c, 0.0) + n
    return out


def scale(s, f):
    return {c: n * f for c, n in s.items()}


def mass(s):
    return sum(n * MW[c] for c, n in s.items())


def elements(s):
    e = {}
    for c, n in s.items():
        for a, k in ATOMS[c].items():
            e[a] = e.get(a, 0.0) + k * n
    return e


# ------------------------------------------------------------------ design inputs
PRODUCT = 6250.0                      # kg/h acetylene product (50 kt/a at 8000 h, ASSUMED, D-002)
NG = {"CH4": 0.980, "CO2": 0.005, "N2": 0.015}   # pipeline gas, ASSUMED (D-003)
OX = {"O2": 0.995, "AR": 0.005}                  # oxygen from an ASU, ASSUMED (D-003)
T_PRE = 873.15                        # preheat, US8975460B2 / US5824834A / US11459281B2: 600 C
# dry cracked gas, US8975460B2 description: H2 56, CH4 5, C2H2 7.5, CO 26, CO2 3.5, higher
# hydrocarbons 1, rest N2/O2/Ar (vol%); higher hydrocarbons split 0.7 C4H2 / 0.3 C6H6 (ASSUMED)
Y = {"H2": 56.0, "CH4": 5.0, "C2H2": 7.5, "CO": 26.0, "CO2": 3.5, "C4H2": 0.7, "C6H6": 0.3}
Y_O2_RES = 0.001                      # residual O2 in dry cracked gas (ASSUMED; US5824834A: 0.1-0.3 % in syngas)
C2H2_TO_SOOT = 22.0                   # kg/kg, US5824834A comparative example 2 (7.8 vol% C2H2)
# dissolved in the quench water, kg per t acetylene: US11459281B2 comparative example
# (open quench, all stripped to air); butadiene (0.712) has no component here (ASSUMED omitted)
DISSOLVED = {"C2H2": 5.475, "CO": 0.789, "CH4": 0.162, "C6H6": 0.138}
FLASH_DEPLETION = 0.9931              # US11459281B2: decompression to 400 mbar(a)
P_QUENCH, T_QUENCH = 1.20, 353.15     # bar, K: quench outlet 80-90 C (US11459281B2 claim 1)
P_COL, T_COL = 1.15, 308.15           # cooling column outlet (ASSUMED)
T_CW_RET = 303.15                     # circulating water back to quench/column after E101 (ASSUMED)
SOOT_SPLIT = {"Q101": 0.70, "T101": 0.295, "X101": 0.005}  # ASSUMED; ESP outlet ~1 mg/m3 (US11459281B2)
SLUDGE_SOOT_WT = 0.10                 # soot sludge 90 % water, US5824834A (table)
P_SUCT, P_DIS, T_IC = 1.05, 11.0, 313.15  # compressor suction, discharge (ASSUMED), intercooling
ETA_IS, ETA_MOT = 0.78, 0.96          # ASSUMED
# NMP recovery splits (ASSUMED, D-009)
SYN_FRAC = {"H2": 0.998, "CO": 0.995, "CH4": 0.99, "N2": 0.999, "AR": 0.998, "O2": 0.998,
            "CO2": 0.85, "C2H2": 0.004, "C4H2": 0.0, "C6H6": 0.0, "H2O": 0.0}
DEGAS_FRAC = {"H2": 1.0, "CO": 1.0, "CH4": 1.0, "N2": 1.0, "AR": 1.0, "O2": 1.0,
              "CO2": 0.95, "C2H2": 0.15, "C4H2": 0.0, "C6H6": 0.0, "H2O": 0.0}
STRIP_FRAC = {"C2H2": 0.99, "CO2": 0.60}     # of what reaches T303
PROD_H2O = 0.002                      # mol fraction water in the product (ASSUMED)
LOADING = 20.0                        # Nm3 C2H2 / m3 solvent in T301 (inside 15-35, US10059640B2)
RHO_NMP = 1028.0                      # kg/m3 at 298 K
W_LEAN = 0.03                         # water mass fraction of the lean solvent (ASSUMED)
NMP_MAKEUP = 2.0e-3                   # kg/kg C2H2 (ASSUMED, D-009)
T_STRIP_IN, T_HOT = 403.15, 443.15    # rich solvent after interchange; hot stripper bottom (US10059640B2)
T_ABS = 308.15
DH_DES = 25.0                         # kJ/mol desorption heat of C2H2/CO2/higher acetylenes (ASSUMED)
EXCESS_AIR, ETA_FIRED, NG_SUPPORT = 0.15, 0.85, 0.10   # fired heater (ASSUMED)
NM3 = 22.414                          # Nm3/kmol

# ------------------------------------------------------------------ burner: extents
def burner(P):
    """P kmol/h C2H2 formed. Returns feeds, extents, outlet."""
    xi1, xi6, xi7 = P, Y["C4H2"] / Y["C2H2"] * P, Y["C6H6"] / Y["C2H2"] * P
    xi2 = Y["CO"] / Y["C2H2"] * P / 2           # 2 CH4 + O2 -> 2 CO + 4 H2
    xi5 = P * MW["C2H2"] / C2H2_TO_SOOT / MW["C"]  # CH4 -> C + 2 H2
    ch4_out = Y["CH4"] / Y["C2H2"] * P
    co2_out = Y["CO2"] / Y["C2H2"] * P
    rhs = ch4_out + 2 * xi1 + 2 * xi2 + xi5 + 4 * xi6 + 6 * xi7 + co2_out
    F = rhs / (NG["CH4"] + NG["CO2"])
    xi3 = co2_out - NG["CO2"] * F               # CH4 + 2 O2 -> CO2 + 2 H2O
    h2_made = 3 * xi1 + 4 * xi2 + 2 * xi5 + 7 * xi6 + 9 * xi7
    xi4 = (h2_made - Y["H2"] / Y["C2H2"] * P) / 2   # 2 H2 + O2 -> 2 H2O
    dry_wo = sum(Y[c] for c in Y) / Y["C2H2"] * P + NG["N2"] * F
    # O2 residual = Y_O2_RES * (dry_wo + Ar + O2res); Ar = 0.005 G; G*0.995 = O2 used + O2res
    used = xi2 + 2 * xi3 + xi4
    # solve G: 0.995 G - used = y (dry_wo + 0.005 G + 0.995 G - used)
    y = Y_O2_RES
    G = (used * (1 - y) + y * dry_wo) / (OX["O2"] * (1 - y) - y * OX["AR"])
    o2res = OX["O2"] * G - used
    feedNG = scale(NG, F)
    feedOX = scale(OX, G)
    out = {"C2H2": P, "H2": Y["H2"] / Y["C2H2"] * P, "CO": 2 * xi2, "CO2": co2_out, "CH4": ch4_out,
           "C4H2": xi6, "C6H6": xi7, "N2": NG["N2"] * F, "AR": OX["AR"] * G, "O2": o2res,
           "H2O": 2 * xi3 + 2 * xi4, "C": xi5}
    ext = {"C2H2_PYR": xi1, "CH4_POX": xi2, "CH4_COMB": xi3, "H2_COMB": xi4, "SOOT": xi5,
           "C4H2_FORM": xi6, "C6H6_FORM": xi7}
    return feedNG, feedOX, ext, out


def t_adiabatic(feed, out):
    hin = H(feed, T_PRE)
    lo, hi = 1000.0, 3000.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if H(out, mid) > hin:
            hi = mid
        else:
            lo = mid
    return mid


def run(P, prod_t, ret_frac=0.0):
    """prod_t: product t/h acetylene; ret_frac: share of the dissolved load that returns to the
    quench and column with the recirculated water (after flash, sludge and purge)."""
    ng, ox, ext, hot = burner(P)
    feed = add(ng, ox)
    Tad = t_adiabatic(feed, hot)
    # dissolved hydrocarbons X carried by the circuit water into the flash (kg/t product)
    diss = {c: v * prod_t / MW[c] for c, v in DISSOLVED.items()}   # kmol/h
    flash_gas_hc = scale(diss, FLASH_DEPLETION)
    resid = scale(diss, 1 - FLASH_DEPLETION)    # leaves with purge and sludge water or returns
    gas_after = {c: n for c, n in hot.items() if c not in ("H2O", "C")}
    for c, n in diss.items():
        gas_after[c] -= n * (1 - ret_frac)
    dry = sum(gas_after.values())
    # quench outlet: saturated at 353 K, 1.2 bar
    yq = psat_water(T_QUENCH) / P_QUENCH
    h2o_q = dry * yq / (1 - yq)
    yc = psat_water(T_COL) / P_COL
    h2o_c = dry * yc / (1 - yc)
    soot = hot["C"]
    g_q = add(gas_after, {"H2O": h2o_q}, {"C": soot * (SOOT_SPLIT["T101"] + SOOT_SPLIT["X101"])})
    g_c = add(gas_after, {"H2O": h2o_c}, {"C": soot * SOOT_SPLIT["X101"]})
    g_e = add(gas_after, {"H2O": h2o_c})
    # heat to the water: quench (hot gas -> 353 K saturated) and column (353 -> 308 K)
    def Hl(n, T):  # liquid water kW
        return n * (IG["H2O"][0] - DHVAP_298 + CP_LIQ_WATER * (T - 298.15)) / 3.6
    # water evaporated in the quench = h2o_q - formed water (from the quench water)
    evap_q = h2o_q - hot["H2O"]
    # quench water W1 at 303 K heated to 353 K and partly evaporated:
    # H(hot) + Hl(W1, 303) = H(g_q, 353) + Hl(W1 - evap, 353) + H(soot to the water, 353)
    lhs = H(hot, Tad) - H(g_q, T_QUENCH) - H({"C": soot * SOOT_SPLIT["Q101"]}, T_QUENCH)
    hl353, hl303 = Hl(1, T_QUENCH), Hl(1, T_CW_RET)
    W1 = (lhs + evap_q * hl353) / (hl353 - hl303)
    T_col_out = 343.15
    cond_c = h2o_q - h2o_c
    lhs_c = H(g_q, T_QUENCH) - H(g_c, T_COL) - H({"C": soot * SOOT_SPLIT["T101"]}, T_COL)
    hlc = Hl(1, T_col_out)
    W2 = (lhs_c - cond_c * hlc) / (hlc - hl303)
    # compression with intercooling to 313 K; recycle gas from T302 joins at the suction
    return dict(ng=ng, ox=ox, ext=ext, hot=hot, Tad=Tad, diss=diss, flash_hc=flash_gas_hc,
                resid=resid, g_q=g_q, g_c=g_c, g_e=g_e, W1=W1, W2=W2, evap_q=evap_q,
                cond_c=cond_c, soot=soot, lhs=lhs, lhs_c=lhs_c, T_col_out=T_col_out)


def recovery(g_e):
    """compression and NMP section with the degasser recycle; returns streams and duties."""
    rec = {c: 0.0 for c in COMPS}
    for _ in range(200):
        suct = add(g_e, rec)
        # after compression and aftercooler: water saturated at 313 K, 11 bar
        dry = sum(n for c, n in suct.items() if c != "H2O")
        y = psat_water(T_IC) / P_DIS
        h2o_gas = min(suct.get("H2O", 0), dry * y / (1 - y))
        cond = suct.get("H2O", 0) - h2o_gas
        gas = dict(suct)
        gas["H2O"] = h2o_gas
        syn = {c: n * SYN_FRAC.get(c, 0.0) for c, n in gas.items()}
        absd = {c: n - syn[c] for c, n in gas.items()}
        new_rec = {c: n * DEGAS_FRAC.get(c, 0.0) for c, n in absd.items()}
        if max(abs(new_rec.get(c, 0) - rec.get(c, 0)) for c in COMPS) < 1e-10:
            break
        rec = new_rec
    after_deg = {c: n - new_rec.get(c, 0.0) for c, n in absd.items()}
    prod = {"C2H2": after_deg["C2H2"] * STRIP_FRAC["C2H2"], "CO2": after_deg["CO2"] * STRIP_FRAC["CO2"]}
    prod["H2O"] = PROD_H2O / (1 - PROD_H2O) * (prod["C2H2"] + prod["CO2"])
    off = {c: after_deg.get(c, 0) - prod.get(c, 0) for c in after_deg}
    return dict(suct=suct, gas=gas, cond=cond, syn=syn, absd=absd, rec=new_rec, prod=prod, off=off,
                after_deg=after_deg)


def comp_power(stream, p1, p2, T1, stages=3):
    r = (p2 / p1) ** (1 / stages)
    n = sum(stream.values())
    cpm = sum(v * cp(c, T1) for c, v in stream.items()) / n
    k = cpm / (cpm - R)
    w_stage = n / 3.6 * cpm * T1 * (r ** ((k - 1) / k) - 1) / ETA_IS   # kW
    t_out = T1 + T1 * (r ** ((k - 1) / k) - 1) / ETA_IS
    return stages * w_stage, t_out, k, r


# ------------------------------------------------------------------ solve for the product rate
P, ret = 250.0, 0.0
W10 = 10000.0 / MW["H2O"]             # ESP irrigation water, kmol/h (ASSUMED)
for _ in range(40):
    s = run(P, PRODUCT / 1000, ret)
    r = recovery(s["g_e"])
    prod_kg = r["prod"]["C2H2"] * MW["C2H2"]
    P *= PRODUCT / prod_kg
    # share of the residual dissolved load that the recirculated water brings back
    _soot_kg = s["soot"] * MW["C"]
    _sl = _soot_kg * (1 - SLUDGE_SOOT_WT) / SLUDGE_SOOT_WT / MW["H2O"]
    _yv = psat_water(313.15) / 1.013
    _flw = sum(s["flash_hc"].values()) * _yv / (1 - _yv)
    _purge = s["hot"]["H2O"] - s["g_e"]["H2O"] + r["cond"] - _sl - _flw
    _w7 = (s["W1"] - s["evap_q"]) + (s["W2"] + s["cond_c"]) + W10 + r["cond"] - _flw
    _w9 = _w7 - _sl
    ret = (1 - FLASH_DEPLETION) * (_w9 / _w7) * (1 - _purge / _w9)
s = run(P, PRODUCT / 1000, ret)
r = recovery(s["g_e"])
prod_t = mass(r["prod"]) / 1000

# NMP loop
c2h2_abs = r["absd"]["C2H2"]
solv_m3 = c2h2_abs * NM3 / LOADING
nmp_kg = solv_m3 * RHO_NMP
lean = {"NMP": nmp_kg / MW["NMP"], "H2O": nmp_kg * W_LEAN / (1 - W_LEAN) / MW["H2O"]}
mk = NMP_MAKEUP * PRODUCT  # kg/h
nmp_syn, nmp_off = 0.05 * mk, 0.05 * mk   # ASSUMED distribution of the loss
nmp_res = mk - nmp_syn - nmp_off
r["syn"]["NMP"] = nmp_syn / MW["NMP"]
r["off"]["NMP"] = nmp_off / MW["NMP"]
residue = {"NMP": nmp_res / MW["NMP"]}
L_kg = nmp_kg + lean["H2O"] * MW["H2O"]

# duties
w_comp, t_dis, kk, ratio = comp_power(r["suct"], P_SUCT, P_DIS, T_IC)
# intercoolers + aftercooler: each stage's heat of compression removed back to 313 K (ideal gas)
# plus the latent heat of the condensate
q_ic = w_comp * ETA_MOT * 0 + w_comp + r["cond"] * 43.0 / 3.6 - 0.0
des = sum(r["after_deg"].get(c, 0) for c in ("C2H2", "CO2", "C4H2", "C6H6"))
q_t303 = (r["prod"]["C2H2"] + r["prod"]["CO2"]) * DH_DES / 3.6
q_t304 = L_kg * CP_NMP_LIQ * (T_HOT - T_STRIP_IN) / 3600 \
    + sum(r["off"].get(c, 0) for c in ("C2H2", "CO2", "C4H2", "C6H6")) * DH_DES / 3.6 \
    + r["off"].get("H2O", 0) * 40.0 / 3.6
q_t304_cond = r["off"].get("H2O", 0) * 0.0  # water leaves as vapour with the off-gas (ASSUMED)
q_e302 = L_kg * CP_NMP_LIQ * (348.15 - T_ABS) / 3600   # lean solvent after interchanger 348 -> 308 K
q_abs = (c2h2_abs + r["absd"]["CO2"]) * DH_DES / 3.6    # heat of absorption to the lean cooler
q_e302 += q_abs
# pumps
p_solv = L_kg / RHO_NMP * (P_DIS * 100 - 120) / 3600 / 0.70 / ETA_MOT        # kW
W_circ = (s["W1"] + s["W2"]) * MW["H2O"]                                    # kg/h
p_water = W_circ / 995 * 400 / 3600 / 0.75 / ETA_MOT
P_ESP = 150.0          # kW, ASSUMED allowance for the wet ESP
P_VAC = 120.0          # kW, ASSUMED vacuum pump of the flash V102

# preheat duties
q_h101 = H(s["ng"], T_PRE) - H(s["ng"], 303.15)
q_h102 = H(s["ox"], T_PRE) - H(s["ox"], 303.15)

# flash gas: dissolved HC (99.31 %) + water vapour saturated at 313 K, 1.013 bar after the
# vacuum pump's condenser
fl = dict(s["flash_hc"])
yv = psat_water(313.15) / 1.013
fl["H2O"] = sum(fl.values()) * yv / (1 - yv)

LHV = {"CH4": 802.6, "C2H2": 1256.0, "CO": 283.0, "C6H6": 3169.5, "C4H2": 2275.7, "NMP": 0.0, "H2": 241.8}
def lhv_kw(sx):
    return sum(n * LHV.get(c, 0.0) for c, n in sx.items()) / 3.6
fuel_waste = add(r["off"], fl)
q_waste = lhv_kw(fuel_waste)
need = (q_h101 + q_h102) / ETA_FIRED
# support natural gas: 10 % of the firing (ASSUMED); the surplus heat raises MP steam for T304
fire = max(need, q_waste / (1 - NG_SUPPORT))
q_ng = fire * NG_SUPPORT
ng_fuel = scale(NG, q_ng * 3.6 / (NG["CH4"] * LHV["CH4"]))
fuel = add(fuel_waste, ng_fuel)
q_fire = lhv_kw(fuel)
q_steam_gen = q_fire * ETA_FIRED - q_h101 - q_h102
# combustion air
o2_st = sum(n * (ATOMS[c].get("C", 0) + ATOMS[c].get("H", 0) / 4 - ATOMS[c].get("O", 0) / 2)
            for c, n in fuel.items() if c not in ("N2", "AR", "O2", "CO2", "H2O"))
AIR = {"N2": 0.7811, "O2": 0.2096, "AR": 0.0093}
air = scale(AIR, o2_st * (1 + EXCESS_AIR) / AIR["O2"])
p_fan = sum(air.values()) * NM3 / 3600 * 5.0 / 0.65 / ETA_MOT   # kW, 5 kPa

# water circuit: formed water + condensates in; purge out
soot = s["soot"]
sludge_water = soot * MW["C"] * (1 - SLUDGE_SOOT_WT) / SLUDGE_SOOT_WT / MW["H2O"]
water_in = s["hot"]["H2O"] - s["g_e"]["H2O"] + r["cond"]      # kmol/h net into the circuit
flash_w = fl["H2O"]
purge_w = water_in - sludge_water - flash_w
# ---- water circuit streams (kmol/h): dissolved load X, returned shares r1, r2, r10
X = s["diss"]
W1n, W2n = s["W1"], s["W2"]
W9w = W1n + W2n + W10 + purge_w
resid_after_flash = scale(X, 1 - FLASH_DEPLETION)
w7_water = (W1n - s["evap_q"]) + (W2n + s["cond_c"]) + W10 + r["cond"] - flash_w
to_w8 = (w7_water - sludge_water) / w7_water
w9_diss = scale(resid_after_flash, to_w8)
def circ(nw):
    return add({"H2O": nw}, scale(w9_diss, nw / W9w))
sW1, sW2, sW10, sPurge = circ(W1n), circ(W2n), circ(W10), circ(purge_w)
r2 = scale(w9_diss, W2n / W9w)
r10 = scale(w9_diss, W10 / W9w)
sW3 = add({"H2O": W1n - s["evap_q"], "C": soot * SOOT_SPLIT["Q101"]},
          {c: X[c] - r2[c] - r10[c] for c in X})
sW4 = add({"H2O": W2n + s["cond_c"], "C": soot * SOOT_SPLIT["T101"]}, r2)
sW5 = add({"H2O": W10, "C": soot * SOOT_SPLIT["X101"]}, r10)
sKO = {"H2O": r["cond"]}
sW6 = add(sW3, sW4, sW5, sKO)
sW7 = {c: n - fl.get(c, 0.0) for c, n in sW6.items()}
sSludge = add({"C": soot, "H2O": sludge_water}, scale(resid_after_flash, 1 - to_w8))
sW8 = {c: n - sSludge.get(c, 0.0) for c, n in sW7.items()}
cpw = CP_LIQ_WATER / 3.6  # kW per (kmol/h K)
q_e101 = cpw * (sW3["H2O"] * (T_QUENCH - T_CW_RET) + sW4["H2O"] * (s["T_col_out"] - T_CW_RET)
                + sW5["H2O"] * (T_COL - T_CW_RET) + sKO["H2O"] * (T_IC - T_CW_RET)) \
    - cpw * sludge_water * (349.15 - T_CW_RET)

def show(name, sx, T, p):
    m = mass(sx)
    n = sum(sx.values())
    comp = {c: round(v / n, 6) for c, v in sx.items() if v > 1e-12}
    print(f"{name}: T={T:.2f} K p={p:.1f} kPa  {m:.3f} kg/h  {n:.4f} kmol/h  {comp}")

print("== burner")
print("extents kmol/h", {k: round(v, 4) for k, v in s["ext"].items()})
ng_n, ox_n = sum(s["ng"].values()), sum(s["ox"].values())
print(f"O2/NG vol = {ox_n / ng_n:.4f}; O/C atomic = {2 * s['ox']['O2'] / (s['ng']['CH4'] + s['ng']['CO2']):.3f}")
print(f"T adiabatic = {s['Tad']:.1f} K")
conv = {"C2H2_PYR": 2 * s["ext"]["C2H2_PYR"] / s["ng"]["CH4"], "SOOT": s["ext"]["SOOT"] / s["ng"]["CH4"],
        "C4H2_FORM": 4 * s["ext"]["C4H2_FORM"] / s["ng"]["CH4"], "C6H6_FORM": 6 * s["ext"]["C6H6_FORM"] / s["ng"]["CH4"],
        "CH4_POX": s["ext"]["CH4_POX"] / s["ox"]["O2"], "CH4_COMB": 2 * s["ext"]["CH4_COMB"] / s["ox"]["O2"],
        "H2_COMB": s["ext"]["H2_COMB"] / s["ox"]["O2"]}
print("conversions", {k: round(v, 7) for k, v in conv.items()})
print("element in", {k: round(v, 4) for k, v in elements(add(s["ng"], s["ox"])).items()})
print("element out", {k: round(v, 4) for k, v in elements(s["hot"]).items()})
dryhot = {c: n for c, n in s["hot"].items() if c not in ("H2O", "C")}
show("dry cracked gas", dryhot, s["Tad"], 150)
show("S1 NG", s["ng"], 303.15, 400)
show("S3 O2", s["ox"], 303.15, 400)
show("S6 hot cracked gas", s["hot"], s["Tad"], 130)
show("S7 quench gas", s["g_q"], T_QUENCH, 120)
print(f"W1 quench water {s['W1'] * MW['H2O']:.1f} kg/h; evaporated {s['evap_q'] * MW['H2O']:.1f}")
print(f"W2 column water {s['W2'] * MW['H2O']:.1f} kg/h; condensed {s['cond_c'] * MW['H2O']:.1f}")
show("S8 column gas", s["g_c"], T_COL, 115)
show("S9 ESP gas", s["g_e"], T_COL, 110)
print("dissolved kmol/h", {c: round(v, 5) for c, v in s["diss"].items()})
show("flash gas", fl, 313.15, 101.3)
print(f"soot {soot * MW['C']:.2f} kg/h; sludge water {sludge_water * MW['H2O']:.1f} kg/h")
print(f"water in circuit {water_in * MW['H2O']:.1f}; purge {purge_w * MW['H2O']:.1f} kg/h = {purge_w * MW['H2O'] / PRODUCT:.3f} kg/kg")
print("== recovery")
show("suction", r["suct"], T_COL, 105)
show("recycle", r["rec"], 313, 130)
print(f"KO condensate {r['cond'] * MW['H2O']:.2f} kg/h")
show("compressed gas", r["gas"], T_IC, 1100)
show("syngas", r["syn"], T_ABS, 1080)
show("product", r["prod"], 313.15, 120)
show("offgas", r["off"], 313.15, 130)
print(f"absorbed C2H2 {c2h2_abs:.3f} kmol/h; solvent {solv_m3:.1f} m3/h; lean {L_kg:.0f} kg/h {lean}")
print(f"NMP makeup {mk:.2f} kg/h; residue {nmp_res:.3f}")
print("== duties kW")
for k, v in [("compressor shaft", w_comp), ("compressor electric", w_comp / ETA_MOT), ("intercoolers+after (CW)", q_ic),
             ("T303 steam", q_t303), ("T304 heat", q_t304), ("E302 lean cooler (CW)", q_e302),
             ("solvent pumps", p_solv), ("water pumps", p_water), ("ESP", P_ESP), ("vacuum", P_VAC), ("fan", p_fan),
             ("H101", q_h101), ("H102", q_h102), ("waste fuel LHV", q_waste), ("NG support LHV", q_ng),
             ("firing LHV", q_fire), ("steam gen in F101", q_steam_gen), ("E101 water circuit (CW)", q_e101),
             ("quench heat", s["lhs"]), ("column heat", s["lhs_c"])]:
    print(f"  {k}: {v:.1f}")
print(f"compressor k={kk:.3f} r/stage={ratio:.3f} T_dis={t_dis:.1f}")
show("NG fuel", ng_fuel, 303.15, 400)
show("air", air, 298.15, 101.3)
show("fuel mix", fuel, 313.15, 120)
print(f"T304 import steam = {q_t304 - q_steam_gen:.1f} kW")
print("== per kg product")
print(f"NG feed {mass(s['ng']) / PRODUCT:.4f} kg/kg ({sum(s['ng'].values()) * NM3 / PRODUCT:.3f} Nm3/kg); NG fuel {mass(ng_fuel) / PRODUCT:.4f}")
print(f"O2 {mass(s['ox']) / PRODUCT:.4f} kg/kg ({sum(s['ox'].values()) * NM3 / PRODUCT:.3f} Nm3/kg)")
print(f"syngas {mass(r['syn']) / PRODUCT:.4f} kg/kg ({sum(r['syn'].values()) * NM3 / PRODUCT:.3f} Nm3/kg)")
print(f"product mass {mass(r['prod']):.2f}  purity {r['prod']['C2H2'] / sum(r['prod'].values()):.5f}")

# ------------------------------------------------------------------ solvent loop streams
L = {"NMP": lean["NMP"], "H2O": lean["H2O"]}
mk_n = mk / MW["NMP"]
sS30 = L
sS16 = add({c: n for c, n in L.items()}, {"NMP": -r["syn"]["NMP"]}, r["absd"])
sS17 = {c: n - r["rec"].get(c, 0.0) for c, n in sS16.items()}
sS19 = {c: n - r["prod"].get(c, 0.0) for c, n in sS17.items()}
sS20 = {c: n - r["off"].get(c, 0.0) - residue.get(c, 0.0) for c, n in sS19.items()}
sS24 = {"NMP": mk_n}
sS23 = sS20

# ------------------------------------------------------------------ YAML stream lines
def fmt(v):
    return float(f"{v:.6g}")


_Y = []  # (sid, T, p, phase, stream) of every y() call, for the balance output below
FLOWSHEET = {}


def y(sid, title, frm, to, tmpl, T, p, phase, sx, src, calc=False):
    sx = {c: n for c, n in (sx or {}).items() if n > 1e-12}
    _Y.append((sid, T, p, phase, sx))
    st = (f"pressure: {{value: {p}, provenance: assumed, source: \"{src[0]}\"}}, "
          f"temperature: {{value: {T:.2f}, provenance: assumed, source: \"{src[1]}\"}}, "
          f"phase: {{value: {phase}, provenance: assumed, source: \"{src[2]}\"}}")
    if not calc:
        n = sum(sx.values())
        comp = ", ".join(f"{c}: {fmt(v / n)}" for c, v in sx.items())
        st += (f", flow: {{value: {mass(sx):.3f}, basis: mass, provenance: assumed, source: \"{src[3]}\"}}"
               f", composition: {{basis: mole_fraction, values: {{{comp}}}, provenance: assumed, source: \"{src[3]}\"}}")
    print(f"  - {{id: {sid}, title: {title}, from: {frm}, to: {to}, template: {tmpl}, state: {{design: {{{st}}}}}}}")


B = "scripts/balance.py"
print("\n== YAML")
fuelmix = fuel
y("S1", "Natural gas feed", "NG.out", "H101.in", "ng", 303.15, 400.0, "vapor", s["ng"],
  ("battery limit (D-003)", "battery limit (D-003)", "gas", f"{B}: methane for the D-005 cracked gas by element balance"))
y("S3", "Oxygen feed", "OXY.out", "H102.in", "oxygen", 303.15, 400.0, "vapor", s["ox"],
  ("battery limit (D-003)", "battery limit (D-003)", "gas", f"{B}: oxygen for the D-005 cracked gas by element balance"))
y("S6", "Hot cracked gas", "R101.out", "Q101.gas_in", "crackedgas", s["Tad"], 130.0, "vapor", s["hot"],
  ("D-010", f"{B}: adiabatic temperature on ideal-gas data (D-005); US8975460B2: about 1700 C", "gas with soot"), calc=True)
y("S7", "Quenched cracked gas", "Q101.gas_out", "T101.gas_in", "crackedgas", T_QUENCH, 120.0, "vapor", s["g_q"],
  ("D-010", "US11459281B2 claim 1: quench to 80-90 C", "gas saturated with water, soot entrained", f"{B}: saturated at 353 K (NIST Antoine), 70 % of the soot to the quench water (D-006)"))
y("W3", "Quench water with soot", "Q101.water_out", "M102.q", "water", T_QUENCH, 120.0, "liquid", sW3,
  ("D-010", "D-006", "water with suspended soot", f"{B}: quench water, evaporation, soot and dissolved hydrocarbons (D-006)"))
y("S8", "Cooled cracked gas", "T101.gas_out", "X101.gas_in", "crackedgas", T_COL, 115.0, "vapor", s["g_c"],
  ("D-010", "D-006", "gas", f"{B}: saturated at 308 K (D-006)"))
y("W4", "Cooling-column water", "T101.water_out", "M102.c", "water", s["T_col_out"], 115.0, "liquid", sW4,
  ("D-010", "D-006", "water with soot", f"{B} (D-006)"))
y("S9", "Soot-free cracked gas", "X101.gas_out", "M201.gas", "crackedgas", T_COL, 110.0, "vapor", s["g_e"],
  ("D-010", "D-006", "gas", f"{B}: ESP outlet about 1 mg/m3 soot (US11459281B2), taken as zero (D-006)"))
y("W5", "ESP drain", "X101.drain", "M102.e", "water", T_COL, 110.0, "liquid", sW5,
  ("D-010", "D-006", "water with soot", f"{B} (D-006)"))
y("S41", "Quench-water flash gas", "V102.gas", "M401.flash", "crackedgas", 313.15, 101.3, "vapor", fl,
  ("vacuum pump discharge (D-006)", "after the vacuum condenser (D-006)", "gas", f"{B}: 99.31 % of the dissolved hydrocarbons at 400 mbar(a) (US11459281B2), saturated with water"))
y("W7", "Degassed circuit water", "V102.water", "V101.in", "water", 349.15, 40.0, "liquid", sW7,
  ("US11459281B2: 400 mbar(a)", "US11459281B2: 75.8 C after decompression to 400 mbar", "water with soot", f"{B} (D-006)"))
y("S50", "Soot sludge", "V101.sludge", "SLUDGE.in", "water", 349.15, 101.3, "liquid", sSludge,
  ("D-006", "D-006", "slurry, 10 wt% soot", f"{B}: all soot as a sludge of 90 wt% water (US5824834A) (D-006)"))
y("W8", "Clarified circuit water", "V101.water", "E101.in", "water", 349.15, 101.3, "liquid", sW8,
  ("D-006", "D-006", "water", f"{B} (D-006)"))
y("S13", "Compressor condensate", "V201.liquid", "M102.k", "water", T_IC, 1090.0, "liquid", sKO,
  ("D-007", "D-007", "water", f"{B}: water above saturation at 313 K, 11 bar(a) (D-007)"))
y("S22", "Degasser recycle gas", "T302.gas", "M201.rec", "crackedgas", 313.15, 130.0, "vapor", r["rec"],
  ("D-009", "D-009", "gas", f"{B}: less soluble gases and 15 % of the absorbed acetylene released (D-009)"))
y("S14", "Compressed cracked gas", "V201.gas", "T301.gas_in", "crackedgas", T_IC, 1090.0, "vapor", r["gas"],
  ("D-007", "D-007", "gas", f"{B}: saturated at 313 K (D-007)"))
y("S15", "Synthesis gas", "T301.gas_out", "SYNGAS.in", "crackedgas", T_ABS, 1070.0, "vapor", r["syn"],
  ("D-009", "D-009", "gas", f"{B}: absorber splits (D-009)"))
y("S16", "Rich solvent", "T301.liq_out", "T302.in", "solvent", T_ABS, 1070.0, "liquid", sS16,
  ("D-009", "D-009", "solution", f"{B} (D-009)"))
y("S17", "Degassed solvent", "T302.liq", "E301.rich_in", "solvent", T_ABS, 130.0, "liquid", sS17,
  ("D-009", "D-009", "solution", f"{B} (D-009)"))
y("S25", "Heated rich solvent", "E301.rich_out", "T303.in", "solvent", T_STRIP_IN, 800.0, "liquid", sS17,
  ("US10059640B2: 7.5-8.5 bar into the first column", "US10059640B2: 125-135 C", "solution", f"{B} (D-009)"))
y("S18", "Acetylene product", "T303.gas", "ACETYLENE.in", "crackedgas", 313.15, 120.0, "vapor", r["prod"],
  ("D-002: 1.2 bar(a), below the 1.4 bar acetylene partial pressure of US10059640B2", "D-002", "gas", f"{B}: 99 % of the acetylene reaching T303 (D-009)"))
y("S19", "Semi-lean solvent", "T303.liq", "T304.in", "solvent", 418.15, 140.0, "liquid", sS19,
  ("US10059640B2: 1.0-1.5 bar", "US10059640B2: side take-off 140-150 C", "solution", f"{B} (D-009)"))
y("S40", "Hot-stripper off-gas (higher acetylenes)", "T304.gas", "M401.off", "crackedgas", 313.15, 120.0, "vapor", r["off"],
  ("US10059640B2: 1.2 bar(a) release pressure", "D-009", "gas, diluted with water vapour", f"{B}: higher acetylenes, aromatics, rest of the acetylene and water (D-009)"))
y("S21", "Solvent regeneration residue", "T304.residue", "RESIDUE.in", "solvent", 443.15, 140.0, "liquid", residue,
  ("D-009", "D-009", "liquid", f"{B}: 90 % of the NMP make-up, polymers not modelled (D-009)"))
y("S20", "Hot lean solvent", "T304.liq", "E301.lean_in", "solvent", T_HOT, 140.0, "liquid", sS20,
  ("US10059640B2: 1.2-1.5 bar", "US10059640B2: bottom 165-180 C", "solution", f"{B} (D-009)"))
y("S26", "Lean solvent after interchanger", "E301.lean_out", "E302.in", "solvent", 348.15, 1200.0, "liquid", sS20,
  ("D-009: after the lean solvent pump", "D-009", "solution", f"{B} (D-009)"))
y("S24", "NMP make-up", "NMP.out", "M301.mu", "solvent", 298.15, 1200.0, "liquid", sS24,
  ("D-009", "D-009", "liquid", f"{B}: 2 kg NMP per t acetylene (ASSUMED, D-009)"))
y("S42", "Natural-gas support fuel", "FUELNG.out", "M401.ng", "ng", 303.15, 400.0, "vapor", ng_fuel,
  ("battery limit (D-003)", "battery limit (D-003)", "gas", f"{B}: 10 % of the firing (ASSUMED, D-011)"))
y("S44", "Combustion air", "AIR.out", "K401.in", "air", 298.15, 101.325, "vapor", air,
  ("ambient", "design basis", "gas", f"{B}: 15 % excess air (ASSUMED, D-011)"))
print("split SP101:", {k: round(v / W9w, 9) for k, v in (("w1", W1n), ("w2", W2n), ("w10", W10), ("purge", purge_w))})
print(f"W1 {mass(sW1):.1f} W2 {mass(sW2):.1f} W10 {mass(sW10):.1f} purge {mass(sPurge):.1f} kg/h")
print("purge comp", {c: fmt(n / sum(sPurge.values())) for c, n in sPurge.items()})
print(f"E101 {q_e101:.1f} kW; W6 T mix approx {(sW3['H2O']*T_QUENCH + sW4['H2O']*s['T_col_out'] + sW5['H2O']*T_COL + sKO['H2O']*T_IC)/sW6['H2O']:.2f}")
print(f"S30 lean {mass(sS30):.1f} kg/h")

# the values process/flowsheet.yaml cites from this script (balance-output contract): the
# streams printed by y() above, and the duties
for sid, T, p, phase, sx in _Y:
    n = sum(sx.values())
    FLOWSHEET[sid] = {"temperature": T, "pressure": p, "phase": phase}
    if n > 0:
        FLOWSHEET[sid] |= {"flow": {"value": mass(sx), "basis": "mass"},
                           "composition": {"values": {c: v / n for c, v in sx.items()},
                                           "basis": "mole_fraction"}}
FLOWSHEET["S11"] = {"temperature": t_dis}
FLOWSHEET["W6"] = {"temperature": (sW3["H2O"] * T_QUENCH + sW4["H2O"] * s["T_col_out"]
                                   + sW5["H2O"] * T_COL + sKO["H2O"] * T_IC) / sW6["H2O"]}
# the compressor's coolers: three equal stages, so the two intercoolers take 2/3 of the shaft
# work and the aftercooler the last third plus the condensate's latent heat (q_ic in total)
q_after = w_comp / 3 + r["cond"] * 43.0 / 3.6
FLOWSHEET |= {qid: {"duty": v} for qid, v in {
    "Q1": w_comp / ETA_MOT, "Q2": p_solv, "Q3": p_water, "Q6": p_fan, "Q10": q_h101,
    "Q11": q_h102, "Q12": q_steam_gen, "Q20": q_t303, "Q21": q_t304 - q_steam_gen,
    "Q30": q_e101, "Q31": q_ic - q_after, "Q32": q_after, "Q33": q_e302}.items()}


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0024 of the library): case ->
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


write_balance_output({"design": FLOWSHEET})
