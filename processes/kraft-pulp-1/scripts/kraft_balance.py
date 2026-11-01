"""Heat and material balance of the bleached softwood kraft pulp mill (kraft-pulp-1), concept.

An independent sequential balance on a lumped component basis: wood as cellulose, hemicellulose
(both C6H10O5), lignin (coniferyl-alcohol unit C10H12O3), extractives (abietic acid C20H30O2) and
ash (SiO2); black liquor organics as sodium salts of those (lignate, oxidised lignate,
isosaccharinate, resin soap). No electrolyte or wood chemistry is predicted: yields, alkali
charges, washing carry-over, reduction, causticity, calcination and every utility figure are
design parameters, ASSUMED or taken from the sources named in DESIGN.md (D-004 to D-012).

Biogenic and fossil carbon are kept apart: CO2B is CO2 whose carbon comes from the wood (black
liquor combustion, lime mud calcination, bleaching); CO2 is fossil (kiln natural gas). The lime
make-up is purchased CaO, so no limestone carbon enters the boundary (D-009).

Run: cheme run scripts/kraft_balance.py [--yaml]. It prints the specific consumptions per ADt,
the element balance of every unit and the duties; --yaml prints the streams section of
process/flowsheet.yaml (values ASSUMED with this script as their source).
"""

from __future__ import annotations

import re
import sys

from CoolProp.CoolProp import PropsSI

AW = {"H": 1.008, "C": 12.011, "O": 15.999, "N": 14.007, "Na": 22.990, "S": 32.06,
      "Cl": 35.45, "Ca": 40.078, "Si": 28.085}
FORMULA = {
    "H2O": "H2O", "CELL": "C6H10O5", "HEMI": "C6H10O5", "LIG": "C10H12O3", "EXTR": "C20H30O2",
    "ASH": "SiO2", "NaOH": "NaOH", "Na2S": "Na2S", "Na2CO3": "Na2CO3", "Na2SO4": "Na2SO4",
    "NaLIG": "C10H11NaO3", "NaOXL": "C10H11NaO4", "NaISA": "C6H11NaO6", "NaEXT": "C20H29NaO2",
    "OXL": "C10H12O4", "NaCl": "NaCl", "ClO2": "ClO2", "H2O2": "H2O2", "H2SO4": "H2SO4",
    "O2": "O2", "N2": "N2", "CO2": "CO2", "CO2B": "CO2", "SO2": "SO2", "NO2": "NO2",
    "CH4": "CH4", "CaO": "CaO", "CaOH2": "CaO2H2", "CaCO3": "CaCO3",
}


def parse(f):
    return {e: int(n or 1) for e, n in re.findall(r"([A-Z][a-z]?)(\d*)", f)}


EL = {k: parse(v) for k, v in FORMULA.items()}
MW = {k: round(sum(AW[e] * n for e, n in v.items()), 3) for k, v in EL.items()}
FIBRE = ("CELL", "HEMI", "LIG")
SOLIDS = FIBRE + ("ASH", "CaO", "CaOH2", "CaCO3")
GASES = ("O2", "N2", "CO2", "CO2B", "SO2", "NO2", "CH4")

# --- design parameters (DESIGN.md D-002 to D-012) --------------------------------------------
ADT = 1000e3 / 24             # kg/h air-dry pulp (90 % dry), 1000 ADt/d (D-002, ASSUMED basis)
A = ADT / 1000                # ADt/h
OD = 0.9 * ADT                # kg/h oven-dry fibre in the product
WOOD = {"CELL": 0.41, "HEMI": 0.28, "LIG": 0.27, "EXTR": 0.035, "ASH": 0.005}  # D-003 ASSUMED
CHIP_MOIST = 0.50             # wet basis (D-003, ASSUMED)
# kg retained per 100 kg dry wood after each stage (D-004, ASSUMED: kappa ~28 after cook,
# ~14.6 after O2, bleached yield 44 %)
COOK = {"CELL": 37.6, "HEMI": 7.4, "LIG": 2.0}
O2ST = {"CELL": 37.6, "HEMI": 7.0, "LIG": 1.0}
BLEA = {"CELL": 37.2, "HEMI": 6.8, "LIG": 0.0}
EA = 0.19                     # effective alkali as NaOH on dry wood (D-005, ASSUMED)
SULF = 0.35                   # sulfidity Na2S/(NaOH+Na2S), NaOH basis (D-005, ASSUMED)
CAUS = 0.81                   # causticity NaOH/(NaOH+Na2CO3) (Tran & Vakkilainen: 80-83 %)
RED = 0.92                    # reduction efficiency (Tran & Vakkilainen: typically > 90 %)
AA_WF = 0.1068                # active alkali mass fraction as NaOH in WL (125 g/L, rho 1.17; ASSUMED)
F1 = 0.03                     # dissolved solids carried with pulp out of brown stock washing (D-006)
F2 = 0.06                     # dissolved solids carried out of the post-O2 washer to bleaching (D-006)
WCONS = 0.25                  # discharge consistency of the wash presses (D-006, ASSUMED)
CONS = 0.10                   # consistency of the bleached stock to the drying machine (ASSUMED)
WBL_DS = 0.15                 # weak black liquor solids (D-007, ASSUMED)
SBL_DS = 0.80                 # strong black liquor solids (Tran & Vakkilainen: 80-85 % state of art)
O2_DELIG = 22.0               # kg O2/ADt to the O2 stage (BREF 2015 3.2.2.2: 20-25 softwood)
NAOH_O2 = 22.0                # kg NaOH-equivalent/ADt to the O2 stage (BREF 2015 3.2.2.2: 20-25)
CLO2 = 10.0                   # kg ClO2/ADt (D-008, ASSUMED; = 15.8 kg NaClO3, BREF Table 3.3 15-50)
CLO2_WF = 0.01                # ClO2 solution 10 g/kg (D-008, ASSUMED)
NAOH_BL = 18.0                # kg NaOH/ADt in bleaching (D-008, ASSUMED; total NaOH BREF Table 3.3 25-50)
H2O2 = 3.0                    # kg/ADt (D-008, ASSUMED; BREF Table 3.3 2-30)
H2O2_EFF = 0.2                # share of H2O2 reacting with lignin, rest decomposes (D-008, ASSUMED)
O2_EOP = 4.0                  # kg O2/ADt to the EOP stage (D-008, ASSUMED)
O2_EOP_EFF = 0.10            # share of EOP oxygen reacting (D-008, ASSUMED)
H2SO4 = 4.0                   # kg/ADt pH control (D-008, ASSUMED)
EFF_M3 = 18.0                 # bleach plant effluent m3/ADt (BREF 2015 3.3.8: 15-20 modern ECF)
PRESS_DS = 0.50               # dryer press section outlet (D-009, ASSUMED)
DRY_MJ = 3.4                  # MJ LP heat per kg water evaporated in the dryer (D-011, ASSUMED)
EVAP_ECON = 6.0               # kg water evaporated per kg LP steam (D-007, ASSUMED 7 effects)
LATENT = 2100.0               # kJ/kg LP steam heat given in the first effect (ASSUMED)
SO2_S = 0.10                  # kg S/ADt from the recovery boiler (BREF Table 3.13 <0.002-0.65)
NOX_RB = 1.2                  # kg NO2/ADt (BREF Table 3.13 0.73-2.0)
DUST_RB = 0.3                 # kg Na2SO4/ADt after the ESP (BREF Table 3.13 0.02-1.6)
AIR_RB = 1.15                 # recovery boiler air ratio (D-010, ASSUMED)
STEAM_DS = 3.5                # kg HP steam per kg BLDS (Tran & Vakkilainen: about 3.5, 2.5-3.8)
DREGS_MOIST = 0.50            # dregs cake liquid mass fraction (D-009, ASSUMED)
GRITS = 5.0                   # kg CaCO3/ADt (D-009, ASSUMED; BREF Table 3.17 dregs+grits 10-20)
MUD_PURGE = 10.0              # kg dry lime mud/ADt purged (D-009, ASSUMED; BREF Table 3.17 10-20)
WLF_DS = 0.65                 # white liquor filter mud cake solids (D-009, ASSUMED)
MUD_DS = 0.80                 # washed lime mud to the kiln (D-009, ASSUMED)
MUD_WASH = 1.5                # kg condensate per kg dry mud (D-009, ASSUMED)
MUD_CARRY = 0.03              # dissolved solids of the cake left in the washed mud (D-009, ASSUMED)
CALC = 0.95                   # degree of calcination in the kiln (D-009, ASSUMED)
KILN_GJ = 1.5                 # GJ/ADt kiln fuel, LHV (BREF 2015 3.2.2.6.2: 1.5-1.8 GJ/t)
CH4_LHV = 50.0                # MJ/kg (natural gas as methane, D-009 ASSUMED)
AIR_K = 1.10                  # kiln air ratio (ASSUMED)
NOX_K = 0.4                   # kg NO2/ADt from the kiln (D-010, ASSUMED; AP-42 10.2 order 0.5)
AIR_O2 = 0.2314               # mass fraction O2 in dry air (Ar counted with N2)
# heat (GJ/ADt) and power (kWh/ADt) by consumer (D-011, ASSUMED; totals against BREF 2015
# 3.2.2.3: 10-14 GJ/ADt and 600-800 kWh/ADt)
MP_HEAT = {"R101": 1.8, "R301": 0.5, "R401": 1.2, "B701": 1.0}
LP_MISC = 0.8                 # deaeration, feedwater, liquor and water heating inside U1001
POWER = {"R101": 60, "W201": 70, "R301": 50, "R401": 100, "D501": 130, "E601": 40,
         "B701": 70, "R803": 40, "K901": 30, "U1001": 60}
HP = (8400e3, 753.15)         # Pa, K (Tran & Vakkilainen: 84 bar, 480 C, a modern unit)
MPP, LPP, CNP = 1300e3, 450e3, 10e3
T_FW = 398.15                 # feedwater after the deaerator (ASSUMED)
ETA_T, ETA_G = 0.80, 0.97     # turbine isentropic and generator efficiency (ASSUMED)


def z():
    return {k: 0.0 for k in MW}


def add(*ds):
    r = z()
    for d in ds:
        for k, v in d.items():
            r[k] += v
    return r


def scale(d, f):
    return {k: v * f for k, v in d.items()}


def tot(d):
    return sum(d.values())


def diss(d):
    """Dissolved species of a liquor (not fibre, not gas, not water)."""
    return {k: v for k, v in d.items() if k not in FIBRE + ("H2O",) + GASES and k not in
            ("CaO", "CaOH2", "CaCO3")}


def react(d, eq, xi):
    """Apply extent xi (kmol/h) of reaction eq {comp: nu}."""
    for k, nu in eq.items():
        d[k] += nu * xi * MW[k]


def elements(d):
    r = {}
    for k, v in d.items():
        for e, n in EL[k].items():
            r[e] = r.get(e, 0.0) + v / MW[k] * n
    return r


R = {  # reactions (process/reactions.yaml)
    "COOK_LIG": {"LIG": -1, "NaOH": -1, "NaLIG": 1, "H2O": 1},
    "PEEL_C": {"CELL": -1, "NaOH": -1, "NaISA": 1},
    "PEEL_H": {"HEMI": -1, "NaOH": -1, "NaISA": 1},
    "SAPON": {"EXTR": -1, "NaOH": -1, "NaEXT": 1, "H2O": 1},
    "OXD_LIG": {"LIG": -2, "NaOH": -2, "O2": -1, "NaOXL": 2, "H2O": 2},
    "SULF_OX": {"Na2S": -1, "O2": -2, "Na2SO4": 1},
    "BL_CLO2": {"LIG": -5, "ClO2": -2, "NaOH": -2, "OXL": 5, "NaCl": 2, "H2O": 1},
    "BL_H2O2": {"LIG": -1, "H2O2": -1, "OXL": 1, "H2O": 1},
    "BL_O2": {"LIG": -2, "O2": -1, "OXL": 2},
    "PER_DEC": {"H2O2": -2, "H2O": 2, "O2": 1},
    "CARB_OX": {"CELL": -5, "ClO2": -24, "NaOH": -24, "CO2B": 30, "NaCl": 24, "H2O": 37},
    "NEUT": {"H2SO4": -1, "NaOH": -2, "Na2SO4": 1, "H2O": 2},
    "BURN_LIG": {"NaLIG": -2, "O2": -23, "Na2CO3": 1, "CO2B": 19, "H2O": 11},
    "BURN_OXL": {"NaOXL": -2, "O2": -22, "Na2CO3": 1, "CO2B": 19, "H2O": 11},
    "BURN_ISA": {"NaISA": -2, "O2": -12, "Na2CO3": 1, "CO2B": 11, "H2O": 11},
    "BURN_EXT": {"NaEXT": -2, "O2": -53, "Na2CO3": 1, "CO2B": 39, "H2O": 29},
    "CARBON": {"NaOH": -2, "CO2B": -1, "Na2CO3": 1, "H2O": 1},
    "REDUC": {"Na2SO4": -1, "Na2S": 1, "O2": 2},
    "SO2_REL": {"Na2S": -2, "CO2B": -2, "O2": -3, "Na2CO3": 2, "SO2": 2},
    "NOX": {"N2": -1, "O2": -2, "NO2": 2},
    "SLAKE": {"CaO": -1, "H2O": -1, "CaOH2": 1},
    "CAUST": {"Na2CO3": -1, "CaOH2": -1, "CaCO3": 1, "NaOH": 2},
    "CALC": {"CaCO3": -1, "CaO": 1, "CO2B": 1},
    "COMB_NG": {"CH4": -1, "O2": -2, "CO2": 1, "H2O": 2},
}
for _id, _eq in R.items():  # every reaction balances its elements
    _b = {}
    for _k, _nu in _eq.items():
        for _e, _n in EL[_k].items():
            _b[_e] = _b.get(_e, 0) + _nu * _n
    assert all(v == 0 for v in _b.values()), (_id, _b)


def water_for(d_solid_and_diss, total):
    """Water that makes a stream of the given total mass."""
    return total - tot(d_solid_and_diss)


def solve():
    S, XI, U = {}, {}, {}
    wood = {k: v * OD / (sum(BLEA.values()) / 100) for k, v in WOOD.items()}  # dry wood kg/h
    WD = tot(wood)
    chips = dict(wood)
    chips["H2O"] = WD * CHIP_MOIST / (1 - CHIP_MOIST)
    S["S1"] = add(chips)

    # white liquor demand of the digester (composition by spec)
    ea = EA * WD                                      # kg/h as NaOH
    aa = ea / (1 - SULF / 2)
    naoh_eq = {"NaOH": aa * (1 - SULF)}
    na2s = aa * SULF / 2 / MW["NaOH"]                 # kmol Na2S
    na2co3 = naoh_eq["NaOH"] * (1 - CAUS) / CAUS / 2 / MW["NaOH"]
    na2so4 = na2s * (1 - RED) / RED
    wl_unit = {"NaOH": naoh_eq["NaOH"], "Na2S": na2s * MW["Na2S"],
               "Na2CO3": na2co3 * MW["Na2CO3"], "Na2SO4": na2so4 * MW["Na2SO4"]}
    wl_unit["H2O"] = aa / AA_WF - tot(wl_unit)
    wl_dig = add(wl_unit)
    wl_frac = {k: v / tot(wl_dig) for k, v in wl_dig.items()}
    aa_per_kg = aa / tot(wl_dig)

    mk_naoh, mk_salt = 0.002 * OD, 0.004 * OD         # first guesses, kg/h
    cao_mk = 0.0
    xi_caust = (wl_dig["NaOH"]) / 2 / MW["NaOH"]
    of = z()                                          # O2 filtrate (recycle)
    of["H2O"] = 8 * OD
    lime_rec = z()
    ww_k = z()                                        # weak wash (recycle)
    ww_k["H2O"] = 2 * OD
    for it in range(400):
        # ---- O2 stage alkali: purchased NaOH first, the rest as white liquor
        wl_o2_naoh = max(NAOH_O2 * A - mk_naoh, 0.0)
        wl_o2 = scale(wl_frac, wl_o2_naoh / wl_frac["NaOH"])
        wl_tot = add(wl_dig, wl_o2)
        # ---- R101 digester
        d = add(S["S1"], wl_dig)
        f = WD / 100
        XI["COOK_LIG"] = (wood["LIG"] - COOK["LIG"] * f) / MW["LIG"]
        XI["PEEL_C_dig"] = (wood["CELL"] - COOK["CELL"] * f) / MW["CELL"]
        XI["PEEL_H_dig"] = (wood["HEMI"] - COOK["HEMI"] * f) / MW["HEMI"]
        XI["SAPON"] = wood["EXTR"] / MW["EXTR"]
        react(d, R["COOK_LIG"], XI["COOK_LIG"])
        react(d, R["PEEL_C"], XI["PEEL_C_dig"])
        react(d, R["PEEL_H"], XI["PEEL_H_dig"])
        react(d, R["SAPON"], XI["SAPON"])
        S["S3"] = d
        # ---- W201 brown stock washing
        fib = {k: d[k] for k in FIBRE}
        D = add(diss(d), diss(of))
        p1 = add(fib, scale(D, F1))
        p1["H2O"] = water_for(p1, tot(fib) / WCONS)
        wbl = scale(D, 1 - F1)
        wbl["H2O"] = tot(wbl) * (1 - WBL_DS) / WBL_DS
        of_w = p1["H2O"] + wbl["H2O"] - d["H2O"]      # water the O2 filtrate must bring
        S["S4"], S["S5"] = p1, wbl
        # ---- R301 O2 reactor
        naoh_mk = {"NaOH": mk_naoh, "H2O": mk_naoh}   # 50 wt% solution
        o2 = {"O2": O2_DELIG * A}
        r = add(p1, naoh_mk, wl_o2, o2)
        XI["OXD_LIG"] = (COOK["LIG"] - O2ST["LIG"]) * f / MW["LIG"] / 2
        XI["PEEL_H_o2"] = (COOK["HEMI"] - O2ST["HEMI"]) * f / MW["HEMI"]
        XI["SULF_OX"] = r["Na2S"] / MW["Na2S"]
        react(r, R["OXD_LIG"], XI["OXD_LIG"])
        react(r, R["PEEL_H"], XI["PEEL_H_o2"])
        react(r, R["SULF_OX"], XI["SULF_OX"])
        vent_o2 = {"O2": r["O2"]}
        r["O2"] = 0.0
        S["S6"], S["S7"], S["S8"], S["S9"], S["S10"] = naoh_mk, wl_o2, o2, r, vent_o2
        # ---- W301 post-O2 washer
        fib = {k: r[k] for k in FIBRE}
        D2 = diss(r)
        p2 = add(fib, scale(D2, F2))
        p2["H2O"] = water_for(p2, tot(fib) / WCONS)
        of = scale(D2, 1 - F2)
        of["H2O"] = of_w
        cd1 = {"H2O": p2["H2O"] + of["H2O"] - r["H2O"]}
        S["S11"], S["S12"], S["S13"] = p2, of, cd1
        # ---- R401 bleach plant (D0-EOP-D1, lumped)
        clo2 = {"ClO2": CLO2 * A, "H2O": CLO2 * A * (1 - CLO2_WF) / CLO2_WF}
        naoh_b = {"NaOH": NAOH_BL * A, "H2O": NAOH_BL * A}
        h2o2 = {"H2O2": H2O2 * A, "H2O": H2O2 * A}
        h2so4 = {"H2SO4": H2SO4 * A, "H2O": H2SO4 * A * 0.07 / 0.93}
        o2b = {"O2": O2_EOP * A}
        bl = add(p2, clo2, naoh_b, h2o2, h2so4, o2b)
        lig_b = (O2ST["LIG"] - BLEA["LIG"]) * f / MW["LIG"]       # kmol lignin to remove
        XI["BL_H2O2"] = H2O2 * A * H2O2_EFF / MW["H2O2"]
        XI["PER_DEC"] = H2O2 * A * (1 - H2O2_EFF) / MW["H2O2"] / 2
        XI["BL_O2"] = O2_EOP * A * O2_EOP_EFF / MW["O2"]
        XI["BL_CLO2"] = (lig_b - XI["BL_H2O2"] - 2 * XI["BL_O2"]) / 5
        XI["CARB_OX"] = (CLO2 * A / MW["ClO2"] - 2 * XI["BL_CLO2"]) / 24
        XI["PEEL_C_bl"] = (O2ST["CELL"] - BLEA["CELL"]) * f / MW["CELL"] - 5 * XI["CARB_OX"]
        XI["PEEL_H_bl"] = (O2ST["HEMI"] - BLEA["HEMI"]) * f / MW["HEMI"]
        XI["NEUT"] = H2SO4 * A / MW["H2SO4"]
        for k in ("BL_H2O2", "PER_DEC", "BL_O2", "BL_CLO2", "CARB_OX", "NEUT"):
            react(bl, R[k], XI[k])
        react(bl, R["PEEL_C"], XI["PEEL_C_bl"])
        react(bl, R["PEEL_H"], XI["PEEL_H_bl"])
        # ---- D501 dryer (needed for the press water recycle)
        p3 = {k: bl[k] for k in FIBRE}
        p3["H2O"] = tot(p3) / CONS * (1 - CONS)
        prod = {k: p3[k] for k in FIBRE}
        prod["H2O"] = ADT - tot(prod)
        press = {"H2O": p3["H2O"] - tot(prod) * (1 - PRESS_DS) / PRESS_DS}
        vap = {"H2O": p3["H2O"] - press["H2O"] - prod["H2O"]}
        bvent = {"O2": bl["O2"]}
        eff = {k: v for k, v in diss(bl).items()}
        eff["CO2B"] = bl["CO2B"]
        eff["H2O"] = EFF_M3 * A * 1000 - tot(eff)
        fw = {"H2O": eff["H2O"] + p3["H2O"] + bvent.get("H2O", 0) - bl["H2O"] - press["H2O"]}
        S.update(S14=clo2, S15=naoh_b, S16=h2o2, S17=h2so4, S18=o2b, S19=fw, S20=p3,
                 S21=eff, S22=bvent, S23=press, S24=prod, S25=vap)
        # ---- E601 evaporation
        sbl = {k: v for k, v in wbl.items() if k != "H2O"}
        sbl["H2O"] = tot(sbl) * (1 - SBL_DS) / SBL_DS
        evap = wbl["H2O"] - sbl["H2O"]
        S["S26"] = sbl
        # ---- B701 recovery boiler
        salt = {"Na2SO4": mk_salt}
        b = add(sbl, salt)
        bls = tot(sbl) - sbl["H2O"]
        for k, rr in (("NaLIG", "BURN_LIG"), ("NaOXL", "BURN_OXL"), ("NaISA", "BURN_ISA"),
                      ("NaEXT", "BURN_EXT"), ("NaOH", "CARBON")):
            XI[rr] = b[k] / MW[k] / 2
        o2_need = (23 * XI["BURN_LIG"] + 22 * XI["BURN_OXL"] + 12 * XI["BURN_ISA"]
                   + 53 * XI["BURN_EXT"]) * MW["O2"]
        air = {"O2": o2_need * AIR_RB, "N2": o2_need * AIR_RB * (1 - AIR_O2) / AIR_O2}
        b = add(b, air)
        for rr in ("BURN_LIG", "BURN_OXL", "BURN_ISA", "BURN_EXT", "CARBON"):
            react(b, R[rr], XI[rr])
        dust = DUST_RB * A
        XI["SO2_REL"] = SO2_S * A / AW["S"] / 2
        react(b, R["SO2_REL"], XI["SO2_REL"])
        s_tot = (b["Na2S"] / MW["Na2S"]) + (b["Na2SO4"] - dust) / MW["Na2SO4"]
        XI["REDUC"] = RED * s_tot - b["Na2S"] / MW["Na2S"]
        react(b, R["REDUC"], XI["REDUC"])
        XI["NOX_RB"] = NOX_RB * A / MW["NO2"] / 2
        react(b, R["NOX"], XI["NOX_RB"])
        smelt = {k: b[k] for k in ("Na2CO3", "Na2S", "Na2SO4", "ASH", "NaCl")}
        smelt["Na2SO4"] -= dust
        flue = {k: b[k] for k in ("O2", "N2", "CO2B", "SO2", "NO2", "H2O")}
        flue["Na2SO4"] = dust
        S.update(S27=salt, S28=air, S29=flue, S30=smelt)
        # ---- T702 dissolving tank, C801 clarifier, S802 slaker, R803 causticizers
        gl = add(smelt, ww_k)
        # water the dissolving tank needs so that the white liquor matches the demand
        gl_d = diss(gl)
        dregs_liq_frac = None
        # dregs: ASH plus an equal mass of green liquor (DREGS_MOIST)
        ash = gl["ASH"]
        # iterate the water: GL liquor composition depends on the condensate added
        cd3 = max(wl_tot["H2O"] - gl["H2O"], 0.0)
        for _ in range(50):
            g = add(gl, {"H2O": cd3})
            liq = {k: v for k, v in g.items() if k != "ASH"}
            m_liq = ash * DREGS_MOIST / (1 - DREGS_MOIST)
            dregs_liq = scale(liq, m_liq / tot(liq))
            gl_c = add(liq, scale(dregs_liq, -1))
            # slaker
            sl = add(gl_c, lime_rec, {"CaO": cao_mk})
            XI["SLAKE"] = sl["CaO"] / MW["CaO"]
            react(sl, R["SLAKE"], XI["SLAKE"])
            grits = {"CaCO3": GRITS * A}
            sl["CaCO3"] -= GRITS * A
            XI["CAUST"] = sl["CaOH2"] / MW["CaOH2"]
            react(sl, R["CAUST"], XI["CAUST"])
            # white liquor filter
            mud_s = {"CaCO3": sl["CaCO3"]}
            liq2 = {k: v for k, v in sl.items() if k not in ("CaCO3", "CaO", "CaOH2")}
            m_cake_liq = sl["CaCO3"] * (1 - WLF_DS) / WLF_DS
            cake_liq = scale(liq2, m_cake_liq / tot(liq2))
            wl_out = add(liq2, scale(cake_liq, -1))
            err = wl_tot["H2O"] - wl_out["H2O"]
            cd3 += err * tot(liq2) / max(wl_out["H2O"], 1)
            if abs(err) < 1e-6:
                break
        S.update(S31=add(gl, {"H2O": cd3}), S32=add({"ASH": ash}, dregs_liq), S33=gl_c,
                 S34=grits, S35={"CaO": cao_mk}, S36=sl, S37=wl_out)
        S["S33"].pop("ASH", None)
        # ---- F806 lime mud washer
        cake = add(mud_s, cake_liq)
        cd2 = {"H2O": MUD_WASH * mud_s["CaCO3"]}
        cake_d = diss(cake_liq)
        mud_liq_d = scale(cake_d, MUD_CARRY)
        m_mud_liq = mud_s["CaCO3"] * (1 - MUD_DS) / MUD_DS
        mud = add(mud_s, mud_liq_d)
        mud["H2O"] = m_mud_liq - tot(mud_liq_d)
        ww_k = add(cake_liq, cd2, scale(mud, -1), {"CaCO3": mud_s["CaCO3"]})
        ww_k["CaCO3"] = 0.0
        purge_f = MUD_PURGE * A / tot({k: mud[k] for k in mud if k != "H2O"})
        purge = scale(mud, purge_f)
        mud_k = scale(mud, 1 - purge_f)
        S.update(S38=cake, S39=cd2, S40=ww_k, S41=purge, S42=mud_k)
        # ---- K901 lime kiln
        # The burner (K902: natural gas combustion, heat to the kiln) and the calcination
        # (K901) are separate steps, so fossil and biogenic carbon never mix in one reactive
        # step and core's carbon-origin tracing stays exact (D-012); physically the gases
        # pass the same kiln and leave by one stack.
        k = dict(add(mud_k))
        ch4 = {"CH4": KILN_GJ * A * 1000 / CH4_LHV}
        airk = {"O2": ch4["CH4"] / MW["CH4"] * 2 * MW["O2"] * AIR_K}
        airk["N2"] = airk["O2"] * (1 - AIR_O2) / AIR_O2
        bu = add(ch4, airk)
        XI["CALC"] = CALC * k["CaCO3"] / MW["CaCO3"]
        XI["COMB_NG"] = ch4["CH4"] / MW["CH4"]
        XI["NOX_K"] = NOX_K * A / MW["NO2"] / 2
        react(k, R["CALC"], XI["CALC"])
        react(bu, R["COMB_NG"], XI["COMB_NG"])
        react(bu, R["NOX"], XI["NOX_K"])
        lime_new = {kk: k[kk] for kk in k if kk in ("CaO", "CaCO3") or
                    (kk in diss(k) and kk != "CH4")}
        kgas = {kk: k[kk] for kk in ("CO2B", "H2O")}
        bgas = {kk: bu[kk] for kk in ("O2", "N2", "CO2", "NO2", "H2O")}
        S.update(S43=ch4, S44=airk, S45=kgas, S50=bgas)
        # ---- steady-state updates (damped)
        lime_rec = add(scale(lime_rec, 0.5), scale(lime_new, 0.5))
        S["S46"] = lime_rec
        # causticizing target: NaOH in the white liquor
        e_naoh = wl_tot["NaOH"] - wl_out["NaOH"]
        cao_mk += 0.5 * e_naoh / 2 / MW["NaOH"] * MW["CaO"]
        # Na and S: compare white liquor produced with the demand
        en = elements(wl_tot)
        eo = elements(wl_out)
        dS = en.get("S", 0) - eo.get("S", 0)
        dNa = en["Na"] - eo["Na"]
        mk_salt += 0.7 * dS * MW["Na2SO4"]
        mk_naoh += 0.7 * (dNa - 2 * dS) * MW["NaOH"]
        if it > 50 and abs(dS) < 1e-9 and abs(dNa) < 1e-9 and abs(e_naoh) < 1e-6:
            break
    assert min(XI.values()) >= 0, XI
    assert min(min(d.values()) for d in S.values()) > -1e-6, {s: d for s, d in S.items() if min(d.values()) < -1e-6}
    # Ca make-up: what the kiln does not return (grits, purge) is the purchased CaO; here the
    # causticizing target is met by adjusting cao_mk, which converges to the Ca losses.
    S["S2"] = wl_dig
    # condensate distribution
    # condensate: dissolving tank and mud washer first, the rest to the post-O2 washer, whose
    # shortfall is made up with fresh hot water (S48)
    cond = evap
    to_w301 = cond - cd2["H2O"] - cd3
    assert to_w301 > 0 and cd1["H2O"] > to_w301, (to_w301, cd1)
    S["S13"] = {"H2O": to_w301}
    S["S47"] = {"H2O": cd3}
    S["S48"] = {"H2O": cd1["H2O"] - to_w301}
    S["S49"] = wl_tot
    S["COND"] = {"H2O": cond}  # not a stream: total condensate (for the report)
    U.update(evap=evap, bls=bls, it=it, mk_naoh=mk_naoh, mk_salt=mk_salt, cao_mk=cao_mk,
             WD=WD, dNa=dNa, dS=dS, e_naoh=e_naoh, of_w=of_w)
    return S, XI, U


def steam(p, t=None, s=None):
    if t is not None:
        return PropsSI("H", "P", p, "T", t, "Water") / 1e3, PropsSI("S", "P", p, "T", t, "Water") / 1e3
    return PropsSI("H", "P", p, "S", s * 1e3, "Water") / 1e3


def energy(S, U):
    """Steam, power and cooling duties, kW (D-011)."""
    E = {}
    h_hp, s_hp = steam(*HP)
    h_fw = PropsSI("H", "P", 9000e3, "T", T_FW, "Water") / 1e3
    def actual(p):
        return h_hp - ETA_T * (h_hp - steam(p, s=s_hp))
    h_mp, h_lp, h_cn = actual(MPP), actual(LPP), actual(CNP)
    m_hp = STEAM_DS * U["bls"]
    q_hp = m_hp * (h_hp - h_fw) / 3600
    E["Q_HP"] = q_hp
    for k, v in MP_HEAT.items():
        E["MP_" + k] = v * A * 1e6 / 3600
    E["LP_E601"] = U["evap"] / EVAP_ECON * LATENT / 3600
    E["LP_D501"] = S["S25"]["H2O"] * DRY_MJ * 1000 / 3600
    E["LP_misc"] = LP_MISC * A * 1e6 / 3600
    q_mp = sum(v for k, v in E.items() if k.startswith("MP_"))
    q_lp = sum(v for k, v in E.items() if k.startswith("LP_"))
    m_mp = q_mp * 3600 / (h_mp - h_fw)
    m_lp = q_lp * 3600 / (h_lp - h_fw)
    m_cn = m_hp - m_mp - m_lp
    p_gen = (m_mp * (h_hp - h_mp) + m_lp * (h_hp - h_lp) + max(m_cn, 0) * (h_hp - h_cn)) / 3600 * ETA_G
    E["CW_U1001"] = max(m_cn, 0) * (h_cn - h_fw) / 3600
    E["CW_E601"] = 0.9 * E["LP_E601"]
    for k, v in POWER.items():
        E["PW_" + k] = v * A
    p_use = sum(v for k, v in E.items() if k.startswith("PW_"))
    E["GEN"] = p_gen
    E["GRID"] = p_use - p_gen
    E["IMPS"] = 0.0 if m_cn >= 0 else -m_cn * (h_lp - h_fw) / 3600
    E["LOSS"] = q_hp + E["IMPS"] - q_mp - q_lp - E["CW_U1001"] - p_gen
    U.update(m_hp=m_hp, m_mp=m_mp, m_lp=m_lp, m_cn=m_cn, h=(h_hp, h_mp, h_lp, h_cn, h_fw),
             p_use=p_use)
    return E


UNITS = {  # unit: (inputs, outputs) by stream id, for the element check
    "R101": (["S1", "S2"], ["S3"]),
    "W201": (["S3", "S12"], ["S4", "S5"]),
    "R301": (["S4", "S6", "S7", "S8"], ["S9", "S10"]),
    "W301": (["S9", "S13", "S48"], ["S11", "S12"]),
    "R401": (["S11", "S14", "S15", "S16", "S17", "S18", "S19", "S23"], ["S20", "S21", "S22"]),
    "D501": (["S20"], ["S23", "S24", "S25"]),
    "E601": (["S5"], ["S26", "S13", "S39", "S47"]),
    "B701": (["S26", "S27", "S28"], ["S29", "S30"]),
    "T702": (["S30", "S40", "S47"], ["S31"]),
    "C801": (["S31"], ["S32", "S33"]),
    "S802R803": (["S33", "S46", "S35"], ["S34", "S36"]),
    "F804": (["S36"], ["S49", "S38"]),
    "X805": (["S49"], ["S2", "S7"]),
    "F806": (["S38", "S39"], ["S40", "S41", "S42"]),
    "K901": (["S42"], ["S45", "S46"]),
    "K902": (["S43", "S44"], ["S50"]),
}


def check(S):
    worst = 0.0
    for u, (i, o) in UNITS.items():
        ei, eo = elements(add(*[S[s] for s in i])), elements(add(*[S[s] for s in o]))
        mi, mo = tot(add(*[S[s] for s in i])), tot(add(*[S[s] for s in o]))
        d = max(abs(ei.get(e, 0) - eo.get(e, 0)) for e in set(ei) | set(eo))
        worst = max(worst, d)
        print(f"# {u:9s} in {mi:12.1f} out {mo:12.1f} kg/h diff {mi - mo:+.4f}; worst element {d:.1e} kmol/h",
              file=sys.stderr)
    return worst


def main():
    S, XI, U = solve()
    # S36 (causticized slurry) is the slaker+causticizer output; S38 is the WL filter cake
    E = energy(S, U)
    worst = check(S)
    pa = lambda v: v / A
    feeds = {"chips wet": tot(S["S1"]), "wood dry": U["WD"], "WL to digester": tot(S["S2"]),
             "NaOH 100% (O2 make-up)": S["S6"]["NaOH"], "NaOH 100% (bleach)": S["S15"]["NaOH"],
             "Na2SO4 make-up": S["S27"]["Na2SO4"], "CaO make-up": S["S35"]["CaO"],
             "O2 total": S["S8"]["O2"] + S["S18"]["O2"], "ClO2": S["S14"]["ClO2"],
             "H2O2": S["S16"]["H2O2"], "H2SO4": S["S17"]["H2SO4"], "CH4": S["S43"]["CH4"],
             "fresh water": S["S19"]["H2O"], "RB air": tot(S["S28"]), "kiln air": tot(S["S44"]),
             "effluent": tot(S["S21"]), "fresh water W301": S["S48"]["H2O"], "dregs": tot(S["S32"]),
             "grits": tot(S["S34"]), "mud purge": tot(S["S41"]),
             "CO2B RB": S["S29"]["CO2B"], "CO2B kiln": S["S45"]["CO2B"], "CO2 kiln (fossil)": S["S50"]["CO2"],
             "CO2B bleach (dissolved)": S["S21"]["CO2B"], "BLDS fired": U["bls"],
             "evaporated": U["evap"], "condensate to W301": S["S13"]["H2O"], "cd3": S["S47"]["H2O"], "cd2": S["S39"]["H2O"],
             "WL total": tot(S["S49"]), "WL to O2": tot(S["S7"])}
    print("# kg per ADt: " + ", ".join(f"{k} {pa(v):.2f}" for k, v in feeds.items()), file=sys.stderr)
    print("# converged it %d dNa %.2e dS %.2e dNaOH %.2e; worst element %.2e" % (
        U["it"], U["dNa"], U["dS"], U["e_naoh"], worst), file=sys.stderr)
    print("# duties kW: " + ", ".join(f"{k} {v:.0f}" for k, v in E.items()), file=sys.stderr)
    print("# GJ or kWh per ADt: steam HP %.2f GJ, MP %.2f GJ, LP %.2f GJ, gen %.0f kWh, use %.0f kWh, grid %.0f kWh, CW %.2f GJ" % (
        E["Q_HP"] * 3.6 / A / 1000, sum(v for k, v in E.items() if k.startswith("MP_")) * 3.6 / A / 1000,
        sum(v for k, v in E.items() if k.startswith("LP_")) * 3.6 / A / 1000, E["GEN"] / A,
        U["p_use"] / A, E["GRID"] / A, (E["CW_U1001"] + E["CW_E601"]) * 3.6 / A / 1000), file=sys.stderr)
    print("# steam t/h HP %.1f MP %.1f LP %.1f cond %.1f; h %s" % (
        U["m_hp"] / 1e3, U["m_mp"] / 1e3, U["m_lp"] / 1e3, U["m_cn"] / 1e3,
        tuple(round(x, 1) for x in U["h"])), file=sys.stderr)
    sbl = S["S26"]
    ds = tot(sbl) - sbl["H2O"]
    el = elements({k: v for k, v in sbl.items() if k != "H2O"})
    print("# BLDS composition wt%: " + ", ".join(
        f"{e} {el[e] * AW[e] / ds * 100:.1f}" for e in ("C", "H", "Na", "S", "O") if e in el)
        + f"; organic salts {sum(sbl[k] for k in ('NaLIG', 'NaOXL', 'NaISA', 'NaEXT')) / ds * 100:.1f} %",
        file=sys.stderr)
    wl = S["S49"]
    print("# WL produced: " + ", ".join(f"{k} {v / tot(wl):.4f}" for k, v in wl.items() if v), file=sys.stderr)
    print("# reaction extents kmol/h: " + ", ".join(f"{k} {v:.3f}" for k, v in XI.items()), file=sys.stderr)
    if "--yaml" in sys.argv:
        for sid, d in S.items():
            if sid == "COND":
                continue
            t = tot(d)
            comp = {k: round(v / t, 6) for k, v in d.items() if v / t >= 5e-7}
            print(f"{sid}: {t:.1f} {comp}")
        for k, v in E.items():
            print(f"{k}: {v:.1f}")
    # the values process/flowsheet.yaml cites from this script (balance-output contract): every
    # stream by its flowsheet id as mass flow and mass fractions; Q9 is the condenser duty, Q10
    # the power export (generation less mill use, -GRID), kW
    out = {sid: {"flow": tot(d), "composition": {k: v / tot(d) for k, v in d.items() if v}}
           for sid, d in S.items() if sid != "COND" and tot(d)}
    out["Q9"] = {"duty": E["CW_U1001"]}
    out["Q10"] = {"duty": -E["GRID"]}
    write_balance_output({"design": out})


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
