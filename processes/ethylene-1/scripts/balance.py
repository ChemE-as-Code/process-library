"""Heat and material balance of the ethane steam cracker (concept stage).

Run with `cheme run scripts/balance.py` (needs thermo and CoolProp of cheme-as-code's
interpreter). Reads process/materials.yaml; prints the furnace reaction conversions, the
converged recycle balance, the duties and the energy indicators, and writes the stream values to
build/balance.json (scratch). The values are typed into process/flowsheet.yaml as ASSUMED with
this script as their source (DESIGN.md D-006): separators, columns and the recycle loop are
specified splits, not a rigorous simulation (no qualified property package for the
C2+ hydrocarbons).

Every design parameter below names its decision in DESIGN.md; sourced numbers name the source.
"""
import json
import math
from pathlib import Path

import yaml
from CoolProp.CoolProp import PropsSI
from thermo import Chemical

ROOT = Path(__file__).resolve().parents[1]
MAT = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())
COMP = {c["id"]: c for c in MAT["components"]}
MW = {k: c["molar_mass"] for k, c in COMP.items()}
R = 8.314462618  # kJ/(kmol K)

# ---------------------------------------------------------------- design parameters
ETHYLENE_PRODUCT = 125_000.0          # kg/h; 1000 kt/a at 8000 h/a (D-002, ASSUMED)
FRESH = {"CH4": 0.005, "C2H6": 0.968, "C3H8": 0.025, "CO2": 0.002}  # mol, purity ethane (D-003, ASSUMED)
STEAM_RATIO = 0.30                    # kg dilution steam / kg hydrocarbon (D-004, ASSUMED)
COT, P_COIL = 1113.15, 200.0          # coil outlet 840 C, 200 kPa(a) (D-004)
T_TLE_OUT = 623.15                    # TLE outlet 350 C (D-007, ASSUMED)
T_QUENCH, P_QUENCH = 313.15, 150.0    # quench tower overhead (D-007, ASSUMED)
P_CGC = 3600.0                        # CGC discharge kPa(a) (D-008, within 17-35 bar(g) of the olefins skill)
N_STAGES, ETA_IS = 5, 0.78            # stages, isentropic efficiency (D-008, ASSUMED)
NAOH_RATIO, NAOH_WT = 3.0, 0.10       # mol NaOH per mol CO2, wt fraction of fresh caustic (D-009, ASSUMED)
C2H4_LOSS_DM = 0.003                  # ethylene to the demethaniser overhead (D-010, ASSUMED)
H2_PURITY = 0.95                      # mol H2 in the hydrogenation gas (D-010, ASSUMED)
H2_EXCESS = 1.5                       # mol H2 fed per mol alkyne (D-011, ASSUMED)
AH_SEL = {"to_C2H4": 0.80, "to_C2H6": 0.20}   # acetylene converter (D-011, ASSUMED)
MAPD_SEL = {"to_C3H6": 0.90, "to_C3H8": 0.10}  # MAPD converter (D-011, ASSUMED)
C2H4_LOSS_VENT = 0.002                # ethylene in the C2 splitter pasteurisation vent (D-010, ASSUMED)
Y_C2H6_PRODUCT = 0.0005               # mol ethane in polymer-grade ethylene (D-002, ASSUMED)
Y_C2H4_BOTTOMS = 0.01                 # mol ethylene in the ethane recycle (D-010, ASSUMED)
Y_C3H8_PRODUCT = 0.005                # mol propane in polymer-grade propylene (D-002, ASSUMED)
Y_C3H6_BOTTOMS = 0.05                 # mol propylene in the propane recycle (D-010, ASSUMED)
BLOWDOWN = 0.03                       # fraction of process water purged (D-007, ASSUMED)
NG = {"CH4": 0.95, "C2H6": 0.03, "CO2": 0.01, "N2": 0.01}  # make-up natural gas (D-013, ASSUMED)
EXCESS_AIR = 0.15                     # about 3 vol% O2 dry in the flue gas (D-013, ASSUMED)
T_STACK = 393.15                      # stack temperature (D-013, ASSUMED)
CASING_LOSS = 0.015                   # fraction of the fired LHV (D-013, ASSUMED)
SHP_P, SHP_T, BFW_T = 11500e3, 793.15, 388.15   # SHP steam raised (Pa, K), BFW (D-007, ASSUMED)
DS_P, PW_T = 800e3, 363.15            # dilution steam pressure, process water to the DSG (D-007, ASSUMED)
CHILL_C3_SHARE = 0.70                 # share of the C2+ condensation at the propylene level (D-014, ASSUMED)
REFR_CARNOT = 0.60                   # refrigeration COP as a fraction of Carnot (D-014, ASSUMED)
T_AMB_COND = 313.15                   # refrigerant condensing against cooling water (D-014, ASSUMED)
REFLUX = {"T401": 0.5, "T501": 1.0, "T502": 4.0, "T601": 1.0, "T602": 15.0, "T603": 1.0}  # D-014, ASSUMED
T_CONDENSER = {"T401": 173.15, "T501": 258.15, "T502": 243.15, "T601": 318.15, "T602": 318.15, "T603": 318.15}

# ---------------------------------------------------------------- furnace yields (sourced)
# BREF LVOC 2017 (JRC109279, EUR 28882 EN), Table 3.3, 'once-through' furnace yields in wt% for
# ethane and propane feed (reproduced from the 2003 LVOC BREF). The C5/C6 cut is lumped as C6H6,
# propadiene as C3H4, butylenes as C4H8 (D-005).
YIELD_ETHANE = {"H2": 4.3, "CH4": 4.2, "C2H2": 0.4, "C2H4": 56.0, "C2H6": 30.0, "C3H4": 0.1,
                "C3H6": 1.0, "C3H8": 0.2, "C4H6": 1.6, "C4H8": 0.2, "C4H10": 0.2, "C6H6": 1.8}
YIELD_PROPANE = {"C2H4": 40.9, "C3H6": 11.5, "C2H6": 3.6}  # used by the lumped propane set (D-005)

# Ethane formation reactions, all from C2H6 (key), and propane reactions (key C3H8).
RXN = {
    "C2H6_DH":   {"C2H6": -1, "C2H4": 1, "H2": 1},
    "C2H6_C2H2": {"C2H6": -1, "C2H2": 1, "H2": 2},
    "C2H6_HGL":  {"C2H6": -1, "H2": -1, "CH4": 2},
    "C2H6_C3H6": {"C2H6": -3, "C3H6": 2, "H2": 3},
    "C2H6_C3H8": {"C2H6": -3, "C3H8": 2, "H2": 1},
    "C2H6_C3H4": {"C2H6": -3, "C3H4": 2, "H2": 5},
    "C2H6_C4H6": {"C2H6": -2, "C4H6": 1, "H2": 3},
    "C2H6_C4H8": {"C2H6": -2, "C4H8": 1, "H2": 2},
    "C2H6_C4H10": {"C2H6": -2, "C4H10": 1, "H2": 1},
    "C2H6_C6H6": {"C2H6": -3, "C6H6": 1, "H2": 6},
    "C3H8_C2H4": {"C3H8": -1, "C2H4": 1, "CH4": 1},
    "C3H8_DH":   {"C3H8": -1, "C3H6": 1, "H2": 1},
    "C3H8_HGL":  {"C3H8": -1, "H2": -1, "C2H6": 1, "CH4": 1},
    "AH_C2H4":   {"C2H2": -1, "H2": -1, "C2H4": 1},
    "AH_C2H6":   {"C2H2": -1, "H2": -2, "C2H6": 1},
    "MAPD_C3H6": {"C3H4": -1, "H2": -1, "C3H6": 1},
    "MAPD_C3H8": {"C3H4": -1, "H2": -2, "C3H8": 1},
    "COMB_H2":   {"H2": -1, "O2": -0.5, "H2O": 1},
    "COMB_CH4":  {"CH4": -1, "O2": -2, "H2O": 2, "CO2": 1},
    "COMB_C2H4": {"C2H4": -1, "O2": -3, "H2O": 2, "CO2": 2},
    "COMB_C2H6": {"C2H6": -1, "O2": -3.5, "H2O": 3, "CO2": 2},
    "CAUSTIC":   {"CO2": -1, "NAOH": -2, "NA2CO3": 1, "H2O": 1},
}
KEY = {r: next(k for k, v in s.items() if v < 0 and k not in ("H2", "O2", "NAOH") or (r == "COMB_H2" and k == "H2"))
       for r, s in RXN.items()}
KEY["COMB_H2"] = "H2"


def ethane_conversions():
    """Conversions (fraction of inlet C2H6) that reproduce the Table 3.3 ethane column."""
    n0 = 100.0 / MW["C2H6"]
    mol = {k: v / MW[k] for k, v in YIELD_ETHANE.items()}
    xi = {
        "C2H6_DH": mol["C2H4"], "C2H6_C2H2": mol["C2H2"], "C2H6_HGL": mol["CH4"] / 2,
        "C2H6_C3H6": mol["C3H6"] / 2, "C2H6_C3H8": mol["C3H8"] / 2, "C2H6_C3H4": mol["C3H4"] / 2,
        "C2H6_C4H6": mol["C4H6"], "C2H6_C4H8": mol["C4H8"], "C2H6_C4H10": mol["C4H10"],
        "C2H6_C6H6": mol["C6H6"],
    }
    return {r: -RXN[r]["C2H6"] * e / n0 for r, e in xi.items()}


def propane_conversions():
    n0 = 100.0 / MW["C3H8"]
    return {"C3H8_C2H4": YIELD_PROPANE["C2H4"] / MW["C2H4"] / n0,
            "C3H8_DH": YIELD_PROPANE["C3H6"] / MW["C3H6"] / n0,
            "C3H8_HGL": YIELD_PROPANE["C2H6"] / MW["C2H6"] / n0}


X_ETHANE = ethane_conversions()
X_PROPANE = propane_conversions()
X_FURNACE = {**X_ETHANE, **X_PROPANE}
X_AH = {"AH_C2H4": AH_SEL["to_C2H4"], "AH_C2H6": AH_SEL["to_C2H6"]}
X_MAPD = {"MAPD_C3H6": MAPD_SEL["to_C3H6"], "MAPD_C3H8": MAPD_SEL["to_C3H8"]}
X_COMB = {"COMB_H2": 1.0, "COMB_CH4": 1.0, "COMB_C2H4": 1.0, "COMB_C2H6": 1.0}


# ---------------------------------------------------------------- helpers
def add(*ss):
    out = {}
    for s in ss:
        for k, v in s.items():
            out[k] = out.get(k, 0.0) + v
    return {k: v for k, v in out.items() if abs(v) > 1e-12}


def scale(s, f):
    return {k: v * f for k, v in s.items()}


def total(s):
    return sum(s.values())


def mass(s):
    return sum(v * MW[k] for k, v in s.items())


def react(inlet, conv):
    """Conversion reactor: each reaction converts its fraction of the key's inlet flow."""
    out = dict(inlet)
    for r, x in conv.items():
        key = KEY[r]
        xi = x * inlet.get(key, 0.0) / -RXN[r][key]
        for k, nu in RXN[r].items():
            out[k] = out.get(k, 0.0) + nu * xi
    for k, v in out.items():
        assert v > -1e-9, (k, v, conv)
    return {k: max(v, 0.0) for k, v in out.items() if v > 1e-12}


def h_ig(k, T):
    """Ideal-gas molar enthalpy incl. formation, kJ/kmol."""
    ig = COMP[k]["ideal_gas"]
    a = ig["cp_R"]
    t0 = 298.15
    integ = sum(a[i] / (i + 1) * (T ** (i + 1) - t0 ** (i + 1)) for i in range(len(a)))
    return ig["dHf_298"] + R * integ


def H(s, T):
    return sum(v * h_ig(k, T) for k, v in s.items())  # kJ/h


def cp_mix(s, T):
    n = total(s)
    cp = 0.0
    for k, v in s.items():
        a = COMP[k]["ideal_gas"]["cp_R"]
        cp += v * R * sum(a[i] * T ** i for i in range(len(a)))
    return cp / n


def hvap(k, T):
    cas = {"CH4": "74-82-8", "C2H4": "74-85-1", "C2H6": "74-84-0", "C2H2": "74-86-2",
           "C3H6": "115-07-1", "C3H8": "74-98-6", "C3H4": "463-49-0", "C4H6": "106-99-0",
           "C4H8": "106-98-9", "C4H10": "106-97-8", "C6H6": "71-43-2", "H2O": "7732-18-5"}[k]
    return Chemical(cas, T=T).Hvapm / 1000.0 * 1000.0  # J/mol = kJ/kmol


def lhv(k):
    """Lower heating value, kJ/kmol, from the formation enthalpies (water as vapour)."""
    r = {"H2": "COMB_H2", "CH4": "COMB_CH4", "C2H4": "COMB_C2H4", "C2H6": "COMB_C2H6"}.get(k)
    if r is None:
        return 0.0
    return -sum(nu * COMP[c]["ideal_gas"]["dHf_298"] for c, nu in RXN[r].items())


def psat_w(T):
    return PropsSI("P", "T", T, "Q", 0, "Water") / 1000.0  # kPa


def pick(s, keys):
    return {k: v for k, v in s.items() if k in keys}


def drop(s, keys):
    return {k: v for k, v in s.items() if k not in keys}


C2 = {"C2H2", "C2H4", "C2H6"}
C3 = {"C3H4", "C3H6", "C3H8"}
C4 = {"C4H6", "C4H8", "C4H10"}


# ---------------------------------------------------------------- balance
def solve(fresh_kmol, rec2, rec3):
    st = {}
    st["S101"] = scale(FRESH, fresh_kmol)
    st["S102"], st["S103"] = rec2, rec3
    # ethane coils (fresh feed and ethane recycle; propane passes) and a propane recycle coil (D-005)
    hc = add(st["S101"], rec2)
    st["S104"] = {"H2O": STEAM_RATIO * mass(hc) / MW["H2O"]}
    st["S105"] = add(hc, st["S104"])
    st["S106"] = react(st["S105"], X_ETHANE)
    st["S108"] = {"H2O": STEAM_RATIO * mass(rec3) / MW["H2O"]}
    st["S109"] = add(rec3, st["S108"])
    st["S110"] = react(st["S109"], X_PROPANE)
    st["S107"] = add(st["S106"], st["S110"])
    st["S111"] = dict(st["S107"])
    gas = st["S107"]
    dry = drop(gas, {"H2O"})
    yw = psat_w(T_QUENCH) / P_QUENCH
    w_gas = yw / (1 - yw) * total(dry)
    st["S201"] = add(dry, {"H2O": w_gas})
    st["S202"] = {"H2O": gas["H2O"] - w_gas}
    r = (P_CGC / P_QUENCH) ** (1.0 / N_STAGES)
    p3 = P_QUENCH * r ** 3
    st["S301"] = dict(st["S201"])
    yw3 = psat_w(T_QUENCH) / p3
    w3 = yw3 / (1 - yw3) * total(dry)
    st["S302"] = {"H2O": st["S201"]["H2O"] - w3}
    st["S303"] = add(dry, {"H2O": w3})
    co2 = st["S303"].get("CO2", 0.0)
    naoh = NAOH_RATIO * co2
    water_c = naoh * MW["NAOH"] * (1 - NAOH_WT) / NAOH_WT / MW["H2O"]
    st["S304"] = {"NAOH": naoh, "H2O": water_c}
    st["S305"] = {"NAOH": naoh - 2 * co2, "NA2CO3": co2, "H2O": water_c + co2}
    st["S306"] = drop(st["S303"], {"CO2"})
    st["S307"] = dict(st["S306"])
    yw5 = psat_w(T_QUENCH) / P_CGC
    dry2 = drop(st["S306"], {"H2O"})
    w5 = yw5 / (1 - yw5) * total(dry2)
    st["S308"] = {"H2O": st["S306"]["H2O"] - w5}
    st["S309"] = add(dry2, {"H2O": w5})
    st["S310"] = {"H2O": w5}
    st["S311"] = dry2
    # demethaniser: H2, CH4 and an ethylene loss overhead
    d = st["S311"]
    ovhd = add(pick(d, {"H2", "CH4"}), {"C2H4": C2H4_LOSS_DM * d["C2H4"]})
    st["S401"] = ovhd
    st["S402"] = add(drop(d, {"H2", "CH4"}), {"C2H4": -C2H4_LOSS_DM * d["C2H4"]})
    # deethaniser, depropaniser: sharp splits (D-010)
    st["S501"] = pick(st["S402"], C2)
    st["S502"] = drop(st["S402"], C2)
    st["S601"] = pick(st["S502"], C3)
    st["S602"] = drop(st["S502"], C3)
    # hydrogenation gas from the cold box (D-010, D-011)
    h2a = H2_EXCESS * st["S501"].get("C2H2", 0.0)
    h2m = H2_EXCESS * st["S601"].get("C3H4", 0.0)
    ch4f = (1 - H2_PURITY) / H2_PURITY
    st["S403"] = {"H2": h2a, "CH4": h2a * ch4f}
    st["S404"] = {"H2": h2m, "CH4": h2m * ch4f}
    st["S405"] = add(ovhd, scale(st["S403"], -1), scale(st["S404"], -1))
    # acetylene converter and C2 splitter
    st["S503"] = react(add(st["S501"], st["S403"]), X_AH)
    f = st["S503"]
    vent_e = C2H4_LOSS_VENT * f["C2H4"]
    st["S504"] = add(pick(f, {"H2", "CH4"}), {"C2H4": vent_e})
    e_avail = f["C2H4"] - vent_e
    a_tot = f["C2H6"]
    # product: Pe, Pa = y/(1-y) Pe; bottoms: Ba = a_tot - Pa, Be = yb/(1-yb) Ba; Pe + Be = e_avail
    ya, yb = Y_C2H6_PRODUCT / (1 - Y_C2H6_PRODUCT), Y_C2H4_BOTTOMS / (1 - Y_C2H4_BOTTOMS)
    pe = (e_avail - yb * a_tot) / (1 - yb * ya)
    st["S505"] = {"C2H4": pe, "C2H6": ya * pe}
    st["S102_new"] = {"C2H6": a_tot - ya * pe, "C2H4": e_avail - pe}
    # MAPD converter and C3 splitter
    st["S603"] = react(add(st["S601"], st["S404"]), X_MAPD)
    g = st["S603"]
    st["S604"] = pick(g, {"H2", "CH4"})
    ya3, yb3 = Y_C3H8_PRODUCT / (1 - Y_C3H8_PRODUCT), Y_C3H6_BOTTOMS / (1 - Y_C3H6_BOTTOMS)
    pp = (g["C3H6"] - yb3 * g["C3H8"]) / (1 - yb3 * ya3)
    st["S605"] = {"C3H6": pp, "C3H8": ya3 * pp}
    st["S103_new"] = {"C3H8": g["C3H8"] - ya3 * pp, "C3H6": g["C3H6"] - pp}
    st["S606"] = pick(st["S602"], C4)
    st["S607"] = pick(st["S602"], {"C6H6"})
    # process water and dilution steam generation
    pw = add(st["S202"], st["S302"], st["S308"], st["S310"])["H2O"]
    st["S204"] = {"H2O": BLOWDOWN * pw}
    st["S203"] = {"H2O": st["S104"]["H2O"] + st["S108"]["H2O"] - (1 - BLOWDOWN) * pw}
    return st, r


def converge():
    fresh = 4000.0
    rec2, rec3 = {"C2H6": 1500.0}, {"C3H8": 50.0}
    for _ in range(200):
        st, r = solve(fresh, rec2, rec3)
        pe = mass(st["S505"])
        err = max(abs(total(st["S102_new"]) - total(rec2)) / total(rec2),
                  abs(total(st["S103_new"]) - total(rec3)) / total(rec3),
                  abs(pe - ETHYLENE_PRODUCT) / ETHYLENE_PRODUCT)
        rec2, rec3 = st["S102_new"], st["S103_new"]
        fresh *= ETHYLENE_PRODUCT / pe
        if err < 1e-10:
            break
    st, r = solve(fresh, rec2, rec3)
    return st, r


def fuel_and_firing(st):
    """Fuel header and firebox: natural gas make-up closes the firebox heat balance."""
    tsat_ds = PropsSI("T", "P", DS_P, "Q", 1, "Water")
    h_in = H(st["S101"], 313.15) + H(st["S102"], 313.15) + H(st["S104"], tsat_ds)
    h_in3 = H(st["S103"], 313.15) + H(st["S108"], tsat_ds)
    q_coil = H(st["S106"], COT) - h_in                       # kJ/h absorbed by the ethane coils
    q_coil3 = H(st["S110"], COT) - h_in3                     # and by the propane coil
    for sid, hh in (("S105", h_in), ("S109", h_in3)):        # adiabatic mixing temperatures
        lo, hi = 250.0, 700.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if H(st[sid], mid) < hh else (lo, mid)
        print(f"{sid} mixing temperature {mid:.2f} K")
    q_tle = H(st["S107"], COT) - H(st["S107"], T_TLE_OUT)
    hf = PropsSI("H", "P", SHP_P, "Q", 0, "Water")
    hg = PropsSI("H", "P", SHP_P, "Q", 1, "Water")
    hs = PropsSI("H", "P", SHP_P, "T", SHP_T, "Water")
    hb = PropsSI("H", "P", SHP_P, "T", BFW_T, "Water")
    m_shp = q_tle / ((hg - hf) / 1000.0)                      # kg/h
    q_conv_steam = m_shp * ((hf - hb) + (hs - hg)) / 1000.0  # kJ/h
    own = add(st["S405"], st["S504"], st["S604"])
    air_per_o2 = {"N2": 0.79 / 0.21, "O2": 1.0}

    def firebox(ng_kmol):
        fuel = add(own, scale(NG, ng_kmol))
        o2 = sum(-RXN[r]["O2"] * fuel.get(KEY[r], 0.0) for r in X_COMB)
        air = scale(air_per_o2, o2 * (1 + EXCESS_AIR))
        flue = react(add(fuel, air), X_COMB)
        fired = sum(v * lhv(k) for k, v in fuel.items())
        # heat released to the coils, convection steam, stack and casing:
        avail = H(fuel, 313.15) + H(air, 298.15) - H(flue, T_STACK) - CASING_LOSS * fired
        return fuel, air, flue, fired, avail

    lo, hi = -2000.0, 20000.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        *_, avail = firebox(mid)
        if avail > q_coil + q_coil3 + q_conv_steam:
            hi = mid
        else:
            lo = mid
    ng = 0.5 * (lo + hi)
    fuel, air, flue, fired, avail = firebox(ng)
    return dict(ng=ng, own=own, fuel=fuel, air=air, flue=flue, fired=fired, q_coil=q_coil, q_coil3=q_coil3,
                q_tle=q_tle, m_shp=m_shp, q_conv_steam=q_conv_steam, h_shp=(hs - hb) / 1000.0,
                h_in=h_in)


def duties(st, r, fb):
    kw = 1 / 3600.0
    q = {}
    q["Q101"] = fb["q_coil"] * kw
    q["Q104"] = fb["q_coil3"] * kw
    q["Q102"] = fb["q_conv_steam"] * kw
    q["Q103"] = fb["q_tle"] * kw
    # quench: sensible cooling 350 -> 40 C and condensation of the dilution steam
    cond = st["S202"]["H2O"]
    q["Q201"] = (H(st["S107"], T_TLE_OUT) - H(st["S107"], T_QUENCH) + cond * hvap("H2O", T_QUENCH)) * kw
    # DSG: process water 90 C to saturated steam at 8 bar (MP steam)
    dh = (PropsSI("H", "P", DS_P, "Q", 1, "Water") - PropsSI("H", "P", DS_P, "T", PW_T, "Water")) / 1000.0
    q["Q210"] = (1 - BLOWDOWN) * (st["S202"]["H2O"] + st["S302"]["H2O"] + st["S308"]["H2O"] + st["S310"]["H2O"]) * MW["H2O"] * dh * kw
    q["Q210"] += st["S203"]["H2O"] * MW["H2O"] * (PropsSI("H", "P", DS_P, "Q", 1, "Water") - PropsSI("H", "P", DS_P, "T", BFW_T, "Water")) / 1000.0 * kw

    def comp_power(s, n_st):
        n = total(s)
        cp = cp_mix(s, 350.0)
        k_exp = R / cp
        return n_st * n * cp * T_QUENCH * (r ** k_exp - 1) / ETA_IS * kw

    q["Q301"] = comp_power(st["S201"], 3)
    q["Q302"] = q["Q301"] + st["S302"]["H2O"] * hvap("H2O", T_QUENCH) * kw
    q["Q303"] = comp_power(st["S306"], 2)
    q["Q304"] = q["Q303"] + st["S308"]["H2O"] * hvap("H2O", T_QUENCH) * kw
    # cold section: C2+ cooled 40 C -> -100 C and condensed; the H2/CH4 cold is recovered
    # (cooling to -35 C and CHILL_C3_SHARE of the condensation at the propylene level, the rest
    # and the demethaniser condenser at the ethylene level, D-014)
    c2p = drop(st["S311"], {"H2", "CH4"})
    latent = sum(v * hvap(k, 200.0) for k, v in c2p.items())
    q_c3 = (H(c2p, T_QUENCH) - H(c2p, 238.15)) + CHILL_C3_SHARE * latent
    q_c2 = (H(c2p, 238.15) - H(c2p, 173.15)) + (1 - CHILL_C3_SHARE) * latent
    q_dm_cond = REFLUX["T401"] * st["S401"]["CH4"] * hvap("CH4", 140.0)
    q["Q401"] = (q_c3 + q_c2 + q_dm_cond) * kw
    q["Q401_ethylene_level"] = (q_c2 + q_dm_cond) * kw

    def column(top, key, tag):
        n = total(top)
        return (REFLUX[tag] + 1) * n * hvap(key, T_CONDENSER[tag]) * kw

    q["Q501"] = column(st["S501"], "C2H6", "T501")      # deethaniser condenser (refrigeration)
    q["Q502"] = q["Q501"]                               # its reboiler, LP steam (D-014)
    q["Q503"] = column(st["S505"], "C2H4", "T502")      # C2 splitter condenser (refrigeration)
    q["Q601"] = column(st["S601"], "C3H6", "T601")      # depropaniser reboiler ~ condenser
    q["Q602"] = q["Q601"]
    q["Q603"] = column(st["S605"], "C3H6", "T602")      # C3 splitter
    q["Q604"] = q["Q603"]
    q["Q605"] = column(st["S606"], "C4H6", "T603")      # debutaniser
    q["Q606"] = q["Q605"]

    def cop(tc):
        return REFR_CARNOT * tc / (T_AMB_COND - tc)

    q["Q402"] = (q["Q401_ethylene_level"] / cop(168.15) + (q["Q401"] - q["Q401_ethylene_level"]) / cop(233.15)
                 + q["Q501"] / cop(T_CONDENSER["T501"] - 5) + q["Q503"] / cop(T_CONDENSER["T502"] - 5))
    q["Q403"] = q["Q401"] + q["Q501"] + q["Q503"] + q["Q402"]
    q["HPS_kg_h"] = fb["m_shp"]
    return q


def main():
    st, r = converge()
    fb = fuel_and_firing(st)
    q = duties(st, r, fb)
    st["S405"] = st["S405"]
    if fb["ng"] >= 0:
        st["S801"] = scale(NG, fb["ng"])
    else:
        st["S801"] = scale(NG, fb["ng"])  # negative: a fuel gas surplus (reported)
    st["S802"], st["S803"], st["S804"] = fb["fuel"], fb["air"], fb["flue"]
    out = {}
    for sid, s in sorted(st.items()):
        if sid.endswith("_new"):
            continue
        n = total(s)
        out[sid] = {"kmol_h": n, "kg_h": mass(s), "y": {k: v / n for k, v in s.items()}}
    print("furnace conversions (fraction of key inlet):")
    for k, v in X_FURNACE.items():
        print(f"  {k}: {v:.6f}")
    print(f"total ethane conversion {sum(v for k, v in X_FURNACE.items() if k.startswith('C2H6')):.4f}")
    print(f"stage pressure ratio {r:.4f}; stage 3 discharge {P_QUENCH * r ** 3:.1f} kPa(a)")
    for sid in sorted(out):
        o = out[sid]
        ys = ", ".join(f"{k}: {v:.6g}" for k, v in sorted(o["y"].items(), key=lambda kv: -kv[1]))
        print(f"{sid}: {o['kg_h']:.1f} kg/h  {o['kmol_h']:.2f} kmol/h  {{{ys}}}")
    print(f"natural gas make-up {fb['ng']:.2f} kmol/h = {mass(scale(NG, fb['ng'])):.1f} kg/h")
    print(f"fired duty (LHV) {fb['fired'] / 3600 / 1000:.2f} MW; coil {fb['q_coil'] / 3.6e6:.2f} MW; "
          f"TLE {fb['q_tle'] / 3.6e6:.2f} MW; convection steam {fb['q_conv_steam'] / 3.6e6:.2f} MW; "
          f"SHP steam {fb['m_shp'] / 1000:.2f} t/h")
    eth = mass(st["S505"]) / 1000.0
    print(f"fired GJ/t ethylene {fb['fired'] / 1e6 / eth:.2f}")
    for k in sorted(q):
        print(f"  {k}: {q[k]:.1f}")
    pw = q["Q301"] + q["Q303"] + q["Q402"]
    print(f"shaft power {pw / 1000:.2f} MW = {pw * 3.6 / 1000 / eth:.3f} GJ/t ethylene")
    co2 = st["S804"].get("CO2", 0) * MW["CO2"]
    print(f"flue CO2 {co2 / 1000:.2f} t/h = {co2 / 1000 / eth:.3f} t/t ethylene")
    fl = st["S804"]
    dry = total(fl) - fl.get("H2O", 0)
    print(f"flue O2 dry {fl.get('O2', 0) / dry * 100:.2f} vol%; flue dry {dry * 22.414:.0f} Nm3/h")
    # element balance over the boundary
    feeds = ["S101", "S203", "S304", "S801", "S803"]
    prods = ["S505", "S605", "S606", "S607", "S204", "S305", "S804"]
    for el in ["C", "H", "O", "N", "Na"]:
        def cnt(s):
            import re
            tot = 0.0
            for k, v in s.items():
                f = COMP[k]["formula"]
                for e, num in re.findall(r"([A-Z][a-z]?)(\d*)", f):
                    if e == el:
                        tot += v * (int(num) if num else 1)
            return tot
        i = sum(cnt(st[s]) for s in feeds)
        o = sum(cnt(st[s]) for s in prods)
        print(f"element {el}: in {i:.3f} out {o:.3f} kmol/h")
    mi = sum(mass(st[s]) for s in feeds)
    mo = sum(mass(st[s]) for s in prods)
    print(f"mass in {mi:.1f} out {mo:.1f} kg/h")
    # stream state snippets for process/flowsheet.yaml (scratch): flows and compositions of the
    # streams cheme cannot propagate (feeds, separator and column outlets), T and P of all
    tp = {"S101": (313.15, 3000), "S102": (313.15, 600), "S103": (313.15, 600), "S104": (443.6, 800),
          "S105": (343.64, 600), "S106": (COT, P_COIL), "S107": (COT, P_COIL), "S108": (443.6, 800),
          "S109": (344.51, 600), "S110": (COT, P_COIL), "S111": (T_TLE_OUT, 170), "S201": (T_QUENCH, P_QUENCH),
          "S202": (358.15, 160), "S203": (BFW_T, 1000), "S204": (443.6, 800), "S301": (T_QUENCH, 1010),
          "S302": (T_QUENCH, 1010), "S303": (T_QUENCH, 1000), "S304": (313.15, 1200), "S305": (318.15, 1000),
          "S306": (318.15, 990), "S307": (T_QUENCH, P_CGC), "S308": (T_QUENCH, P_CGC), "S309": (T_QUENCH, P_CGC),
          "S310": (T_QUENCH, 300), "S311": (T_QUENCH, 3550), "S401": (173.15, 3300), "S402": (263.15, 3350),
          "S403": (303.15, 3200), "S404": (303.15, 3200), "S405": (303.15, 500), "S501": (258.15, 2500),
          "S502": (343.15, 2550), "S503": (333.15, 2400), "S504": (243.15, 1900), "S505": (243.15, 1900),
          "S601": (318.15, 1800), "S602": (358.15, 1850), "S603": (318.15, 1700), "S604": (318.15, 1600),
          "S605": (318.15, 1600), "S606": (318.15, 500), "S607": (383.15, 550), "S801": (288.15, 2000),
          "S802": (313.15, 400), "S803": (298.15, 101.325), "S804": (T_STACK, 101.325)}
    propagated = {"S105", "S106", "S107", "S109", "S110", "S111", "S301", "S307", "S503", "S603", "S802", "S804"}
    lines = []
    for sid in sorted(out):
        o = out[sid]
        t, p = tp[sid]
        lines.append(f"{sid}:")
        if t is not None:
            lines.append(f"  temperature: {{value: {t:.2f}, provenance: assumed, source: D-006}}")
        lines.append(f"  pressure: {{value: {p:g}, provenance: assumed, source: D-006}}")
        if sid in propagated:
            continue
        ys = {k: float(f"{v:.6g}") for k, v in sorted(o["y"].items(), key=lambda kv: -kv[1]) if v >= 5e-7}
        big = max(ys, key=ys.get)
        ys[big] = round(1.0 - sum(v for k, v in ys.items() if k != big), 7)
        lines.append(f"  flow: {{value: {o['kg_h']:.1f}, basis: mass, provenance: assumed, source: 'scripts/balance.py, D-006'}}")
        lines.append("  composition: {basis: mole_fraction, values: {" + ", ".join(f"{k}: {v:g}" for k, v in ys.items())
                     + "}, provenance: assumed, source: 'scripts/balance.py, D-006'}")
    Path(ROOT / "build").mkdir(exist_ok=True)
    # the values process/flowsheet.yaml cites from this script (balance-output contract)
    flowsheet = {sid: {"flow": {"value": o["kg_h"], "basis": "mass"},
                       "composition": {"values": o["y"], "basis": "mole_fraction"}}
                 for sid, o in out.items()}
    for k, v in q.items():
        flowsheet.setdefault(k, {})["duty"] = v
    write_balance_output({"design": flowsheet})
    (ROOT / "build" / "states.yaml").write_text("\n".join(lines) + "\n")
    (ROOT / "build" / "balance.json").write_text(json.dumps({"streams": out, "duties_kW": q,
                                                             "conversions": X_FURNACE,
                                                             "fired_kW": fb["fired"] / 3600}, indent=1))


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


if __name__ == "__main__":
    main()
