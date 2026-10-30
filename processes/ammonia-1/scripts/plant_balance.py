"""Heat and material balance of ammonia-1 (DESIGN.md D-006): the independent balance whose
values process/flowsheet.yaml gives as ASSUMED where core cannot calculate them (separators,
the steam system, the furnace, duties; core #315).

Run: ``cheme run scripts/plant_balance.py`` (cheme-as-code's interpreter: chemicals, thermo,
scipy and cheme's own equilibrium functions). Writes build/balance.json and prints the stream
values and duties. Nothing in the repository is written.

Models (all ASSUMED where not stated, decisions in DESIGN.md):
- reactors with cheme's own functions, so that `cheme process propagate` reproduces them:
  conversion reactors (prereformer, secondary-reformer burner, methanator, furnace) and
  ideal-gas equilibrium (primary and secondary reformer, HT and LT shift) or Peng-Robinson
  equilibrium (converter) at the outlet temperature plus the approach;
- adiabatic outlet temperatures on cheme's ideal-gas enthalpies (elements basis, 298.15 K);
- water knock-out: water saturated at the drum (IAPWS-95 vapour pressure), gases insoluble;
- loop separator, let-down and the loop cold-end duties: thermo Peng-Robinson flash with ChemSep
  interaction parameters (not qualified by ChemE-as-Code for NH3 mixtures: core #315);
- compressors: ideal gas, isentropic efficiency per stage, intercooled;
- steam: IAPWS-IF97 regions 1 and 2 (chemicals.iapws).
The flows are solved per 1000 kmol/h of process natural gas and scaled to 1500 t/d of NH3.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace

import yaml
from chemicals.iapws import (
    iapws95_Psat,
    iapws97_dG0_dtau_region2,
    iapws97_dG_dtau_region1,
    iapws97_dGr_dtau_region2,
)
from scipy.optimize import brentq, fsolve
from thermo import CEOSGas, CEOSLiquid, ChemicalConstantsPackage, FlashVL, PRMIX
from thermo.interaction_parameters import IPDB

from chemeascode.domains.chemistry.equilibrium import equilibrate, equilibrate_real
from chemeascode.domains.chemistry.thermochemistry import IdealGas, ln_k

ROOT = Path(__file__).resolve().parents[1]
MAT = yaml.safe_load((ROOT / "process/materials.yaml").read_text())
C = ["CH4", "C2H6", "C3H8", "CO2", "N2", "H2", "CO", "H2O", "O2", "AR", "NH3"]
MW = {c["id"]: c["molar_mass"] for c in MAT["components"]}
IG = {c["id"]: IdealGas(**{k: v for k, v in c["ideal_gas"].items() if k != "source"}) for c in MAT["components"]}
CRIT = {c["id"]: SimpleNamespace(**{k: c["critical"][k] for k in ("Tc", "Pc", "omega")}) for c in MAT["components"]}

# ---- design basis and ASSUMED design choices (DESIGN.md)
NH3_KG_H = 1500e3 / 24                                   # D-002 contained NH3
# D-040 (I-006): Enbridge Gas typical analysis, trace C4+ (0.027 mol%) counted as C3H8, O2 and
# H2 traces (0.015 mol%) left out, normalised; until S5c the ASSUMED D-004 gas
# {"CH4": 0.910, "C2H6": 0.040, "C3H8": 0.010, "CO2": 0.010, "N2": 0.030}
NG = {"CH4": 0.9467, "C2H6": 0.0440, "C3H8": 0.0023, "CO2": 0.0030, "N2": 0.0040}
# D-040: dry air of the NASA Earth Fact Sheet (2024), normalised; until S5c N2 0.78080,
# O2 0.20946, Ar 0.00934, CO2 0.00040
AIR = {"N2": 0.78075, "O2": 0.20949, "AR": 0.00934, "CO2": 0.00042}
T_AMB, P_AMB = 288.15, 101.325
S_C = 3.0                       # D-007 steam to hydrocarbon carbon
T_R100_IN, T_R101_IN, T_R101 = 773.15, 893.15, 1083.15   # D-007
APP_REF = -10.0                 # reformer approach (K at 10 K colder: less CH4 conversion)
T_AIR_PRE = 773.15              # process air preheat, D-007
T_HTS_IN, T_LTS_IN, APP_SHIFT = 643.15, 478.15, 10.0     # D-008
T_E202 = 403.15                 # LTS effluent after the regenerator reboiler, D-009
T_CW_OUT = 313.15               # process coolers' outlet, D-012
CO2_SLIP = 500e-6               # D-009 CO2 left in the treated gas (mol fraction)
P_CO2 = 150.0                   # CO2 vent pressure kPa(a)
REGEN_MJ_KG = 1.0               # D-009 regeneration heat per kg CO2
PUMP_KWH_T = 21.0               # D-009 solvent pumping per t CO2
T_MET_IN = 553.15               # D-010
T_R501 = 703.15                 # converter outlet, D-011
APP_NH3 = 15.0                  # converter approach, D-011
INERT_TARGET = 0.12             # CH4 + Ar at the converter inlet, D-011
T_SEP = 263.15                  # chiller outlet / separator, D-011
T_REC = 303.15                  # recycle gas after the cold exchanger E-505, D-011
T_E501H = 343.15                # E-501 hot outlet, above the NH3 dew point, D-011
P_VENT = 1700.0                 # refrigeration receiver vent, D-017
P_LD = 2500.0                   # let-down vessel
T_PROD, P_PROD = 240.15, 110.0  # product, D-002
HRU = {"H2": 0.90, "N2": 0.25, "AR": 0.15, "CH4": 0.05}   # D-013 recoveries to the H2-rich gas
NH3_REC = 0.99                  # D-013 NH3 recovered from purge and let-down gas
HRU_MJ_KG = 3.0                 # D-013 LP steam per kg NH3 recovered
EXCESS_O2 = 0.10                # D-014 furnace excess oxygen
T_CAIR, T_BRIDGE, T_STACK = 523.15, 1323.15, 423.15        # D-014
FURNACE_LOSS = 0.015            # D-014 casing losses, fraction of fired duty (LHV)
P_STEAM, T_STEAM, T_FW = 4600.0, 673.15, 313.15          # D-015
BLOWDOWN = 0.02                 # D-015
ETA_C = 0.78                    # D-016 compressor isentropic efficiency per stage
ETA_P, ETA_FAN = 0.70, 0.70
REF_ETA, T_COND = 0.55, 313.15  # D-017 refrigeration: fraction of Carnot, condensing
T_EVAP_CH, T_EVAP_PR = 258.15, 238.15

RX = {
    "C2H6_REF": {"C2H6": -1, "H2O": -2, "CO": 2, "H2": 5},
    "C3H8_REF": {"C3H8": -1, "H2O": -3, "CO": 3, "H2": 7},
    "SMR": {"CH4": -1, "H2O": -1, "CO": 1, "H2": 3},
    "WGS": {"CO": -1, "H2O": -1, "CO2": 1, "H2": 1},
    "H2_OX": {"H2": -2, "O2": -1, "H2O": 2},
    "METH_CO": {"CO": -1, "H2": -3, "CH4": 1, "H2O": 1},
    "METH_CO2": {"CO2": -1, "H2": -4, "CH4": 1, "H2O": 2},
    "NH3_SYN": {"N2": -1, "H2": -3, "NH3": 2},
    "CH4_COMB": {"CH4": -1, "O2": -2, "CO2": 1, "H2O": 2},
    "C2H6_COMB": {"C2H6": -1, "O2": -3.5, "CO2": 2, "H2O": 3},
    "C3H8_COMB": {"C3H8": -1, "O2": -5, "CO2": 3, "H2O": 4},
    "H2_COMB": {"H2": -1, "O2": -0.5, "H2O": 1},
    "CO_COMB": {"CO": -1, "O2": -0.5, "CO2": 1},
    "NH3_COMB": {"NH3": -1, "O2": -0.75, "N2": 0.5, "H2O": 1.5},
}


# ---- helpers on {component: kmol/h}
def z():
    return {c: 0.0 for c in C}


def add(*ns):
    out = z()
    for n in ns:
        for c, v in n.items():
            out[c] += v
    return out


def scale(n, f):
    return {c: v * f for c, v in n.items()}


def tot(n):
    return sum(n.values())


def mass(n):
    return sum(v * MW[c] for c, v in n.items())


def frac(n):
    t = tot(n)
    return {c: v / t for c, v in n.items() if v > 0}


def H(n, t):
    """kW, ideal gas on the elements at 298.15 K (cheme's basis)."""
    return sum(v * IG[c].enthalpy(t) for c, v in n.items() if v) / 3600.0


R_W = 0.461526


def h_liq(t, p_kpa):
    tau, pi = 1386.0 / t, p_kpa / 1e3 / 16.53
    return R_W * t * tau * iapws97_dG_dtau_region1(tau, pi)


def h_vap(t, p_kpa):
    tau, pi = 540.0 / t, p_kpa / 1e3
    return R_W * t * tau * (iapws97_dG0_dtau_region2(tau, pi) + iapws97_dGr_dtau_region2(tau, pi))


def hvap_water(t):
    """kJ/kmol latent heat at t (IF97 at saturation)."""
    p = iapws95_Psat(t) / 1e3
    return (h_vap(t, p * 0.999) - h_liq(t, p * 1.001)) * MW["H2O"]


def H2(n_gas, n_liq_water, t):
    """kW of a gas plus liquid water at t."""
    return H(n_gas, t) + n_liq_water * (IG["H2O"].enthalpy(t) - hvap_water(t)) / 3600.0


def t_of_h(n, h, lo=250.0, hi=2500.0):
    return brentq(lambda t: H(n, t) - h, lo, hi, xtol=1e-6)


def convert(n, rxns, keys):
    """cheme's conversion reactor: each reaction converts its key's inlet flow fully."""
    out = dict(n)
    for r, k in zip(rxns, keys):
        xi = n[k] / -RX[r][k]
        for c, nu in RX[r].items():
            out[c] += nu * xi
    return out


def equilibrium(n, t, p, rxns, approach=0.0, real=False):
    st = [RX[r] for r in rxns]
    ks = [ln_k(s, IG, t + approach) for s in st]
    feed = {c: v for c, v in n.items() if v > 0}
    if real:
        out = equilibrate_real(st, ks, feed, p, t, CRIT)[0]
    else:
        out = equilibrate(st, ks, feed, p)[0]
    return add(out)


def adiabatic_equilibrium(n, h_in, p, rxns, approach, lo, hi, real=False):
    t = brentq(lambda t: H(equilibrium(n, t, p, rxns, approach, real), t) - h_in, lo, hi, xtol=1e-4)
    return equilibrium(n, t, p, rxns, approach, real), t


def knockout(n, t, p):
    """(gas, condensed water) with the gas saturated with water at t, p."""
    y = iapws95_Psat(t) / 1e3 / p
    dry = tot(n) - n["H2O"]
    wv = y / (1 - y) * dry
    if n["H2O"] <= wv:
        return dict(n), 0.0
    g = dict(n)
    g["H2O"] = wv
    return g, n["H2O"] - wv


def compress(n, t1, p1, p2, stages, t_ic=T_CW_OUT, after=True):
    """ideal gas: power kW, intercooler (+aftercooler) duty kW, discharge T (before aftercooler)."""
    r = (p2 / p1) ** (1 / stages)
    w = q = 0.0
    t, p = t1, p1
    nt = tot(n)
    for s in range(stages):
        if s > 0:
            q += H(n, t) - H(n, t_ic)
            t = t_ic
        s1 = sum(v * IG[c].entropy(t) for c, v in n.items() if v)
        t2s = brentq(lambda tt: sum(v * IG[c].entropy(tt) for c, v in n.items() if v) - s1 - nt * 8.314462618 * math.log(r), t, 1500.0)
        dh = (H(n, t2s) - H(n, t)) / ETA_C
        w += dh
        t = t_of_h(n, H(n, t) + dh, t, 1500.0)
        p *= r
    t_dis = t
    if after:
        q += H(n, t) - H(n, t_ic)
    return w, q, t_dis


# ---- thermo PR flash for the loop species
LOOP = ["H2", "N2", "AR", "CH4", "NH3"]
_IDS = ["hydrogen", "nitrogen", "argon", "methane", "ammonia"]
CONSTS, PROPS = ChemicalConstantsPackage.from_IDs(_IDS)
_KIJ = IPDB.get_ip_asymmetric_matrix("ChemSep PR", CONSTS.CASs, "kij")
_KW = dict(Tcs=CONSTS.Tcs, Pcs=CONSTS.Pcs, omegas=CONSTS.omegas, kijs=_KIJ)
FLASH = FlashVL(CONSTS, PROPS, liquid=CEOSLiquid(PRMIX, _KW, HeatCapacityGases=PROPS.HeatCapacityGases),
                gas=CEOSGas(PRMIX, _KW, HeatCapacityGases=PROPS.HeatCapacityGases))
PSAT_NH3_VENT = PROPS.VaporPressures[4](T_EVAP_CH) / 1e3   # kPa, thermo's NH3 vapour pressure


def flash(n, **spec):
    assert all(n[c] < 1e-9 for c in C if c not in LOOP), {c: n[c] for c in C if c not in LOOP and n[c]}
    nt = sum(n[c] for c in LOOP)
    zs = [n[c] / nt for c in LOOP]
    kw = {}
    if "T" in spec:
        kw["T"] = spec["T"]
    if "P" in spec:
        kw["P"] = spec["P"] * 1e3
    if "H" in spec:
        kw["H"] = spec["H"] * 3600 / nt
    r = FLASH.flash(zs=zs, **kw)
    vap, liq = z(), z()
    if r.gas is not None:
        for i, c in enumerate(LOOP):
            vap[c] = r.VF * nt * r.gas.zs[i]
    for c in LOOP:
        liq[c] = n[c] - vap[c]
    return {"T": r.T, "VF": r.VF, "vap": vap, "liq": liq, "H": r.H() * nt / 3600}


def h_th(n, t, p):
    return flash(n, T=t, P=p)["H"]


# ---- the plant per F kmol/h of process natural gas
F0 = 1000.0


def front_end(air):
    s = {}
    ng = scale(add(NG), F0)
    s["ng_proc"] = ng
    carbon = ng["CH4"] + 2 * ng["C2H6"] + 3 * ng["C3H8"]
    steam = z()
    steam["H2O"] = S_C * carbon
    s["steam"] = steam
    mix = add(ng, steam)
    # mixing temperature: NG at 643 K with MP steam at 673 K, both ideal gas (D-015)
    h_mix = H(ng, 643.15) + H(steam, T_STEAM)
    s["T_mix"] = t_of_h(mix, h_mix, 500, 900)
    s["mix"] = mix
    r100 = convert(mix, ["C2H6_REF", "C3H8_REF"], ["C2H6", "C3H8"])
    s["T_r100"] = t_of_h(r100, H(mix, T_R100_IN), 500, 900)
    s["r100"] = r100
    r101 = equilibrium(r100, T_R101, 3500.0, ["SMR", "WGS"], APP_REF)
    s["r101"] = r101
    s["Q_r101"] = H(r101, T_R101) - H(r100, T_R101_IN)
    a = scale(add(AIR), air)
    s["air"] = a
    w, q, t_dis = compress(a, T_AMB, P_AMB, 3600.0, 4, after=False)
    s.update(W_k101=w, Q_k101=q, T_k101=t_dis)
    feed2 = add(r101, a)
    s["m103"] = feed2
    h2in = H(r101, T_R101) + H(a, T_AIR_PRE)
    s["T_m103"] = t_of_h(feed2, h2in, 600, 2500)
    burn = convert(feed2, ["H2_OX"], ["O2"])
    s["T_burn"] = t_of_h(burn, h2in, 800, 3000)
    s["burn"] = burn
    r102, t102 = adiabatic_equilibrium(burn, h2in, 3400.0, ["SMR", "WGS"], APP_REF, 900, 1600)
    s.update(r102=r102, T_r102=t102)
    s["Q_e105"] = H(r102, t102) - H(r102, T_HTS_IN)
    r201, t201 = adiabatic_equilibrium(r102, H(r102, T_HTS_IN), 3300.0, ["WGS"], APP_SHIFT, T_HTS_IN, 900)
    s.update(r201=r201, T_r201=t201, Q_e201=H(r201, t201) - H(r201, T_LTS_IN))
    r202, t202 = adiabatic_equilibrium(r201, H(r201, T_LTS_IN), 3200.0, ["WGS"], APP_SHIFT, T_LTS_IN, 700)
    s.update(r202=r202, T_r202=t202)
    # E-202 gives the regenerator reboiler its duty (D-009): outlet temperature from that duty
    m_co2 = (r202["CO2"] - CO2_SLIP * (tot(r202) - r202["H2O"] - r202["CO2"]) / (1 - CO2_SLIP)) * MW["CO2"]
    q_regen = REGEN_MJ_KG * m_co2 / 3.6

    def gap(t):
        g, wl = knockout(r202, t, 3150.0)
        return H(r202, t202) - H2(g, wl, t) - q_regen

    t_e202 = brentq(gap, 330.0, t202 - 1.0, xtol=1e-4)
    g, wl = knockout(r202, t_e202, 3150.0)
    s["T_e202"] = t_e202
    s["Q_e202"] = H(r202, t202) - H2(g, wl, t_e202)
    g2, wl2 = knockout(r202, T_CW_OUT, 3100.0)
    s["e202_out"] = r202
    s["Q_e203"] = H2(g, wl, T_E202) - H2(g2, wl2, T_CW_OUT)
    s["v201_gas"], s["v201_liq"] = g2, wl2
    # CO2 removal (D-009)
    dry_no_co2 = tot(g2) - g2["H2O"] - g2["CO2"]
    tg = dict(g2)
    tg["CO2"] = CO2_SLIP * dry_no_co2 / (1 - CO2_SLIP)  # slip on the dry treated gas
    tg["H2O"] = 0.0
    y = iapws95_Psat(T_CW_OUT) / 1e3 / 3050.0
    tg["H2O"] = y / (1 - y) * tot(tg)
    co2 = z()
    co2["CO2"] = g2["CO2"] - tg["CO2"]
    y = iapws95_Psat(T_CW_OUT) / 1e3 / P_CO2
    co2["H2O"] = y / (1 - y) * co2["CO2"]
    s["c301_gas"], s["co2"] = tg, co2
    s["c301_water"] = tg["H2O"] + co2["H2O"] - g2["H2O"]
    m_co2 = co2["CO2"] * MW["CO2"]
    s["Q_regen"] = REGEN_MJ_KG * m_co2 / 3.6          # kW
    s["W_c301"] = PUMP_KWH_T * m_co2 / 1000.0          # kW
    s["Q_e401"] = H(tg, T_MET_IN) - H(tg, T_CW_OUT)
    r401 = convert(tg, ["METH_CO", "METH_CO2"], ["CO", "CO2"])
    s["T_r401"] = t_of_h(r401, H(tg, T_MET_IN), 500, 900)
    s["r401"] = r401
    g3, wl3 = knockout(r401, T_CW_OUT, 2900.0)
    s["Q_e402"] = H(r401, s["T_r401"]) - H2(g3, wl3, T_CW_OUT)
    s["v401_gas"], s["v401_liq"] = g3, wl3
    dry = dict(g3)
    s["x401_water"] = dry["H2O"]
    dry["H2O"] = 0.0
    s["makeup"] = dry
    return s


def loop(makeup, x, purge):
    """x: recycle gas (5 loop components) and H2-rich HRU gas (4) -> residuals."""
    rec = z()
    rec.update(dict(zip(LOOP, x[:5])))
    hr = z()
    hr.update(dict(zip(["H2", "N2", "AR", "CH4"], x[5:9])))
    s = {}
    mu = add(makeup, hr)
    s["mu"] = mu
    w501, q501, t501d = compress(mu, T_CW_OUT, 2850.0, 14600.0, 3)
    s.update(W_k501=w501, Q_k501=q501, T_k501=t501d)
    suc = add(mu, rec)
    s["suc"] = suc
    s["T_suc"] = t_of_h(suc, H(mu, T_CW_OUT) + H(rec, T_REC), 200, 400)
    w502, _, t502 = compress(suc, s["T_suc"], 14600.0, 15500.0, 1, after=False)
    s.update(W_k502=w502, T_k502=t502)
    out = equilibrium(suc, T_R501, 15100.0, ["NH3_SYN"], APP_NH3, real=True)
    s["r501"] = out
    h_in = H(out, T_R501)
    s["T_r501_in"] = t_of_h(suc, h_in, 300, 800)
    s["Q_e501"] = h_in - H(suc, t502)
    # E-501 hot side ends above the NH3 dew point (D-011); the WHB E-502 takes the rest
    t_x = t_of_h(out, H(out, T_E501H) + s["Q_e501"], 300, 900)
    s["T_e502"], s["T_e501h"] = t_x, T_E501H
    s["Q_e502"] = H(out, T_R501) - H(out, t_x)
    s["Q_e503"] = h_th(out, T_E501H, 14900.0) - h_th(out, T_CW_OUT, 14800.0)
    f = flash(out, T=T_SEP, P=14700.0)
    vap, liq = f["vap"], f["liq"]
    s["v501_vap"], s["v501_liq"] = vap, liq
    pg = scale(vap, purge)
    rc = scale(vap, 1 - purge)
    s["purge"], s["recycle"] = pg, rc
    # E-505 cold exchanger: recycle gas 263 -> 303 K against the chiller feed (D-011)
    q505 = h_th(rc, T_REC, 14650.0) - h_th(rc, T_SEP, 14700.0)
    h505 = h_th(out, T_CW_OUT, 14800.0) - q505 * tot(out) / tot(out)
    s["T_e505h"] = flash(out, P=14750.0, H=h505)["T"]
    s["Q_e505"] = q505
    s["Q_e504"] = h505 - f["H"]
    ld = flash(liq, P=P_LD, H=flash(liq, T=T_SEP, P=14700.0)["H"])
    s["v502_gas"], s["v502_liq"], s["T_v502"] = ld["vap"], ld["liq"], ld["T"]
    # V-701 product flash and refrigeration inert vent (D-017): the dissolved gases leave with
    # NH3 at saturation in the vent chiller at T_EVAP_CH and P_VENT
    l2 = ld["liq"]
    inert = sum(l2[c] for c in ("H2", "N2", "AR", "CH4"))
    y = PSAT_NH3_VENT / P_VENT
    vent = {c: (l2[c] if c in ("H2", "N2", "AR", "CH4") else 0.0) for c in C}
    vent["NH3"] = y / (1 - y) * inert
    prod = {c: l2[c] - vent[c] for c in C}
    s["vent"], s["v701_liq"] = vent, prod
    hru_in = add(pg, ld["vap"], vent)
    s["hru_in"] = hru_in
    nh3 = z()
    nh3["NH3"] = NH3_REC * hru_in["NH3"]
    h2r = z()
    for c, r in HRU.items():
        h2r[c] = r * hru_in[c]
    tail = {c: hru_in[c] - nh3[c] - h2r[c] for c in C}
    s.update(nh3_rec=nh3, h2_rec=h2r, tail=tail)
    inert = (suc["CH4"] + suc["AR"]) / tot(suc)
    res = [rc[c] - rec[c] for c in LOOP] + [h2r[c] - hr[c] for c in ["H2", "N2", "AR", "CH4"]]
    return s, res, inert


def solve():
    def full(v):
        air, purge = v[0], v[1]
        fe = front_end(air)
        x = v[2:]
        ls, res, inert = loop(fe["makeup"], x, purge)
        h2n2 = ls["suc"]["H2"] / ls["suc"]["N2"]
        return fe, ls, res + [h2n2 - 3.0, inert - INERT_TARGET]

    def resid(v):
        try:
            *_, r = full(v)
        except Exception:
            return [1e6] * len(v)
        # scale the two design residuals like flows
        return r[:-2] + [r[-2] * 100.0, r[-1] * 1e4]

    # starting point from a rough front end
    v0 = [1300.0, 0.03, 9000.0, 3000.0, 700.0, 1300.0, 500.0, 300.0, 50.0, 20.0, 30.0]
    v = fsolve(resid, v0, xtol=1e-12, maxfev=4000)
    fe, ls, r = full(v)
    assert max(abs(x) for x in r[:-2]) < 1e-3 and abs(r[-2]) < 1e-6 and abs(r[-1]) < 1e-6, r
    return v, fe, ls


def main():
    v, fe, ls = solve()
    air, purge = v[0], v[1]
    # product: let-down liquid + recovered NH3, chilled (D-017)
    prod = add(ls["v701_liq"], ls["nh3_rec"])
    k = NH3_KG_H / (prod["NH3"] * MW["NH3"])          # scale to 1500 t/d contained NH3
    q_e701 = (h_th(ls["v502_liq"], ls["T_v502"], P_LD) - h_th(ls["v701_liq"], T_PROD, P_LD)
              - h_th(ls["vent"], T_EVAP_CH, P_VENT))
    q_x601 = h_th(ls["nh3_rec"], 303.15, P_LD) - h_th(ls["nh3_rec"], T_PROD, P_LD)
    T_m701 = T_PROD
    # HRU feed temperature (ideal-gas mixing of purge, let-down gas and vent, D-013)
    T_m601 = t_of_h(ls["hru_in"], H(ls["purge"], T_SEP) + H(ls["v502_gas"], ls["T_v502"]) + H(ls["vent"], T_EVAP_CH), 200, 400)
    hru_steam = HRU_MJ_KG * ls["nh3_rec"]["NH3"] * MW["NH3"] / 3.6
    lp_regen = max(0.0, fe["Q_regen"] - fe["Q_e202"])

    # furnace (D-014): fuel = NG + HRU tail gas, air with 10 % excess O2
    tail = ls["tail"]

    def comb(fuel):
        o2 = fuel["CH4"] * 2 + fuel["C2H6"] * 3.5 + fuel["C3H8"] * 5 + fuel["H2"] * 0.5 + fuel["CO"] * 0.5 + fuel["NH3"] * 0.75
        a = scale(add(AIR), o2 * (1 + EXCESS_O2) / AIR["O2"])
        flue = convert(add(fuel, a), ["CH4_COMB", "C2H6_COMB", "C3H8_COMB", "H2_COMB", "CO_COMB", "NH3_COMB"],
                       ["CH4", "C2H6", "C3H8", "H2", "CO", "NH3"])
        return a, flue

    def lhv(fuel):
        a, flue = comb(fuel)
        return H(add(fuel, a), 298.15) - H(flue, 298.15)

    def radiant_gap(f):
        ngf = scale(add(NG), f)
        fuel = add(ngf, tail)
        a, flue = comb(fuel)
        h_in = H(ngf, T_AMB) + H(tail, 303.15) + H(a, T_CAIR)
        return h_in - H(flue, T_BRIDGE) - FURNACE_LOSS * lhv(fuel) - fe["Q_r101"]

    f_fuel = brentq(radiant_gap, 0.0, 5000.0)
    ngf = scale(add(NG), f_fuel)
    fuel = add(ngf, tail)
    cair, flue = comb(fuel)
    w_fd = tot(cair) / 3600 * 8.314 * T_AMB / P_AMB * 5.0 / ETA_FAN
    w_id = tot(flue) / 3600 * 8.314 * T_STACK / P_AMB * 5.0 / ETA_FAN
    q_conv = H(flue, T_BRIDGE) - H(flue, T_STACK)
    q_e101 = H(fe["ng_proc"], 643.15) - H(fe["ng_proc"], T_AMB)
    q_e102 = H(fe["mix"], T_R100_IN) - H(fe["mix"], fe["T_mix"])
    q_e103 = H(fe["r100"], T_R101_IN) - H(fe["r100"], fe["T_r100"])
    q_e104 = H(fe["air"], T_AIR_PRE) - H(fe["air"], fe["T_k101"])
    q_e106 = H(cair, T_CAIR) - H(cair, T_AMB)
    q_e107 = q_conv - (q_e101 + q_e102 + q_e103 + q_e104 + q_e106)
    q_e201_steam = fe["Q_e201"] - fe["Q_e401"]

    # steam system (D-015), per basis
    hv, hfw, hbd = h_vap(T_STEAM, P_STEAM), h_liq(T_FW, P_STEAM + 1000), h_liq(531.0, P_STEAM)
    q_in = fe["Q_e105"] + q_e201_steam + ls["Q_e502"] + q_e107
    m_raised = q_in * 3600 / ((hv - hfw) + BLOWDOWN * (hbd - hfw))       # kg/h
    m_bd = BLOWDOWN * m_raised
    m_lp = (lp_regen + hru_steam) * 3600 / (hv - hfw)
    m_proc = fe["steam"]["H2O"] * MW["H2O"]
    m_export = m_raised - m_proc - m_lp
    cond = (fe["v201_liq"] + fe["v401_liq"] + fe["x401_water"]) * MW["H2O"]
    m_dmw = m_proc + m_export + m_bd - cond
    w_bfw = (m_raised + m_bd) / 3600 * (P_STEAM + 1000 - P_AMB) / 1000 / ETA_P

    # refrigeration (D-017)
    cop_ch = REF_ETA * T_EVAP_CH / (T_COND - T_EVAP_CH)
    cop_pr = REF_ETA * T_EVAP_PR / (T_COND - T_EVAP_PR)
    w_ref = ls["Q_e504"] / cop_ch + (q_e701 + q_x601) / cop_pr
    q_ref_cw = ls["Q_e504"] + q_e701 + q_x601 + w_ref

    duties = {
        "Q_r101": fe["Q_r101"], "W_k101": fe["W_k101"], "Q_k101": fe["Q_k101"], "Q_e101": q_e101,
        "Q_e102": q_e102, "Q_e103": q_e103, "Q_e104": q_e104, "Q_e105": fe["Q_e105"], "Q_e106": q_e106,
        "Q_e107": q_e107, "W_k102": w_fd, "W_k103": w_id, "Q_e201": fe["Q_e201"], "Q_e201_steam": q_e201_steam,
        "Q_e401": fe["Q_e401"], "Q_e202": fe["Q_e202"], "Q_e203": fe["Q_e203"], "Q_regen": fe["Q_regen"],
        "Q_lp_regen": lp_regen, "Q_c301_cw": fe["Q_regen"] + fe["W_c301"], "W_c301": fe["W_c301"],
        "Q_e402": fe["Q_e402"], "W_k501": ls["W_k501"], "Q_k501": ls["Q_k501"], "W_k502": ls["W_k502"],
        "Q_e501": ls["Q_e501"], "Q_e502": ls["Q_e502"], "Q_e503": ls["Q_e503"], "Q_e504": ls["Q_e504"],
        "Q_e505": ls["Q_e505"], "Q_x601_ref": q_x601, "Q_e701": q_e701, "W_k701": w_ref, "Q_k701_cw": q_ref_cw, "Q_hru_lp": hru_steam, "W_p801": w_bfw,
        "Q_steam_in": q_in, "Q_conv": q_conv,
    }
    duties = {kk: vv * k for kk, vv in duties.items()}
    temps = {kk: vv for kk, vv in {**fe, **ls}.items() if kk.startswith("T_")}
    temps["T_m701"] = T_m701
    temps["T_m601"] = T_m601
    temps["T_m102"] = t_of_h(add(fuel, cair), H(ngf, T_AMB) + H(tail, 303.15) + H(cair, T_CAIR), 250, 800)
    temps["T_m501"] = t_of_h(add(fe["makeup"], ls["h2_rec"]), H(fe["makeup"], T_CW_OUT) + H(ls["h2_rec"], 303.15), 250, 400)
    print(f"NG total {mass(scale(add(fe['ng_proc'], ngf), k)):.2f} kg/h, fuel split {f_fuel / (F0 + f_fuel):.7f}, purge {purge:.8f}")
    flows = {kk: scale(vv, k) for kk, vv in {**fe, **ls}.items() if isinstance(vv, dict)}
    flows.update(prod=scale(prod, k), ng_fuel=scale(ngf, k), fuel=scale(fuel, k), cair=scale(cair, k), flue=scale(flue, k))
    water = {"v201_liq": fe["v201_liq"] * k * MW["H2O"], "v401_liq": fe["v401_liq"] * k * MW["H2O"],
             "x401_water": fe["x401_water"] * k * MW["H2O"], "c301_water": fe["c301_water"] * k * MW["H2O"],
             "m_raised": m_raised * k, "m_bd": m_bd * k, "m_lp": m_lp * k, "m_proc": m_proc * k,
             "m_export": m_export * k, "m_dmw": m_dmw * k}
    res = {"scale": k, "air_basis": air, "purge_fraction": purge, "temps": temps, "duties": duties,
           "water_kg_h": water,
           "flows": {kk: {c: x for c, x in vv.items() if abs(x) > 0} for kk, vv in flows.items()}}
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/balance.json").write_text(json.dumps(res, indent=1))

    print(f"scale {k:.6f} (NG process {F0 * k:.2f} kmol/h), purge fraction {purge:.6f}, air {air * k:.2f} kmol/h")
    print("temperatures K:", {kk: round(vv, 2) for kk, vv in temps.items()})
    print("duties kW:", {kk: round(vv, 1) for kk, vv in duties.items()})
    print("water kg/h:", {kk: round(vv, 1) for kk, vv in water.items()})
    for kk, vv in res["flows"].items():
        fr = frac(vv) if tot(vv) > 0 else {}
        print(f"{kk:10s} {mass(vv):12.2f} kg/h {tot(vv):10.3f} kmol/h  " + ", ".join(f"{c}: {x:.6g}" for c, x in fr.items()))


if __name__ == "__main__":
    main()
