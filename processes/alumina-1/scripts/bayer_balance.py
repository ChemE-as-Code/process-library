"""Heat and material balance of the Bayer alumina refinery (alumina-1), concept stage.

An independent sequential balance on a component basis. Core cannot speciate caustic
aluminate liquors (core #364 covers aqueous NaCl only) or predict gibbsite solubility and
precipitation yield (core #365: single-salt crystallisers only), so the liquor is carried as
neutral NaOH + NaAlO2 + H2O and the digestion and precipitation are fixed by the industry's
liquor ratios (A/C) as ASSUMED design specifications. Every design parameter below is ASSUMED
unless its comment names a source; DESIGN.md D-004..D-008 list them with the reasons.

Liquor convention of the Bayer industry: C = caustic soda (NaOH free + NaOH bound as
aluminate) expressed as g Na2CO3 per litre, A = dissolved alumina as g Al2O3 per litre.

Run: cheme run scripts/bayer_balance.py [--yaml] (standard library only). It prints the
streams (kg/h, mass fractions), the duties (kW), the element balance of every step and the
specific consumptions per t of alumina; --yaml prints the stream entries for
process/flowsheet.yaml, which carries them as ASSUMED with this script as their source.
"""

from __future__ import annotations

import sys

# kg/kmol (IUPAC 2021 standard atomic weights)
AW = {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "Na": 22.990, "Al": 26.982,
      "Si": 28.085, "Ca": 40.078, "Ti": 47.867, "Fe": 55.845}
ELEMENTS = {
    "H2O": {"H": 2, "O": 1}, "NaOH": {"Na": 1, "O": 1, "H": 1},
    "NaAlO2": {"Na": 1, "Al": 1, "O": 2},
    "AlOH3": {"Al": 1, "O": 3, "H": 3}, "AlOOH": {"Al": 1, "O": 2, "H": 1},
    "Kaol": {"Al": 2, "Si": 2, "O": 9, "H": 4},              # Al2Si2O5(OH)4
    "SiO2": {"Si": 1, "O": 2}, "Fe2O3": {"Fe": 2, "O": 3}, "FeOOH": {"Fe": 1, "O": 2, "H": 1},
    "TiO2": {"Ti": 1, "O": 2},
    "DSP": {"Na": 8, "Al": 6, "Si": 6, "O": 26, "H": 2},    # Na8Al6Si6O24(OH)2 hydroxysodalite
    "CaO": {"Ca": 1, "O": 1}, "CaOH2": {"Ca": 1, "O": 2, "H": 2},
    "TCA": {"Ca": 3, "Al": 2, "O": 12, "H": 12},             # Ca3Al2(OH)12
    "Al2O3": {"Al": 2, "O": 3}, "Na2O": {"Na": 2, "O": 1},
    "CH4": {"C": 1, "H": 4}, "O2": {"O": 2}, "N2": {"N": 2}, "CO2": {"C": 1, "O": 2},
}
MW = {k: sum(AW[e] * n for e, n in v.items()) for k, v in ELEMENTS.items()}
SOLIDS = {"AlOH3", "AlOOH", "Kaol", "SiO2", "Fe2O3", "FeOOH", "TiO2", "DSP", "CaO", "CaOH2",
          "TCA", "Al2O3", "Na2O"}
MW_NA2CO3 = 2 * AW["Na"] + AW["C"] + 3 * AW["O"]

# --- design basis (D-002, D-003) -------------------------------------------------------------
PRODUCT = 125000.0             # kg/h smelter-grade alumina, 3000 t/d (D-002, ASSUMED)
W_PROD = {"Al2O3": 0.990, "Na2O": 0.004, "H2O": 0.006}   # product grade (D-002, ASSUMED)
# Bauxite: chemical assay of the Balaya plateau (Debele, Guinea) gibbsitic bauxite, wt% dry,
# as compiled by Zainudeen et al. (2023) Heliyon 9:e19070, Table 6 (column "Balaya Plateau 2"),
# with the mineral list of its Table 5 (gibbsite 83.9, kaolinite 1.1, diaspore 1.3, goethite
# 4.5 + aluminian goethite 6.15, hematite 4.1). Normative mineralogy derived here (D-003).
ASSAY = {"Al2O3": 54.69, "Fe2O3": 12.25, "SiO2": 0.76, "TiO2": 2.85, "LOI": 29.69,
         "minor": 0.05 + 0.05 + 0.05 + 0.074 + 0.049 + 0.022 + 0.073 + 0.01}
KAOL_WT = 1.10                 # wt% kaolinite (Table 5): the reactive silica
MONO_WT = 1.30                 # wt% diaspore (Table 5), carried as AlOOH, not digested at 418 K
GOETHITE_WT = 4.5 + 6.15       # wt% goethite + aluminian goethite (Table 5), as FeOOH
BX_MOIST = 0.10                # free moisture, wet basis (ASSUMED; IAI 2019 LCI report s. 3.4:
                               # bauxite input typically carries 10-20 % water)

# --- liquor and digestion (D-004) ------------------------------------------------------------
C_SPENT = 250.0                # g/L caustic as Na2CO3 in the spent liquor to the mill (ASSUMED)
AC_SPENT = 0.38                # A/C of the spent liquor (ASSUMED)
AC_DIG = 0.70                  # A/C of the digester blow-off (ASSUMED; below gibbsite saturation
                               # at 418 K so that the liquor survives clarification)
RHO_LIQ = 1.30                 # kg/L liquor density (ASSUMED, all Bayer liquors)
X_GIB = 0.98                   # fraction of the gibbsite dissolved in digestion (ASSUMED)
X_KAOL = 1.0                   # kaolinite to DSP in pre-desilication and digestion (ASSUMED)
LIME = 52.0                    # kg CaO per t alumina: IAI 2019 LCI report, s. 3.11.2.3 (2019
                               # surveyed lime consumption ~52 kg/t alumina), used as the dose
MILK = 0.15                    # Ca(OH)2 mass fraction of the milk of lime (ASSUMED)
NAOH_MU = 0.50                 # NaOH mass fraction of the caustic make-up solution (ASSUMED)

# --- clarification and washing (D-005) -------------------------------------------------------
LS_SETTLER = 2.0               # kg liquor / kg solids in the settler underflow (ASSUMED)
LS_WASHER = 1.0                # kg liquor / kg solids in the last washer underflow (ASSUMED)
N_WASH = 6                     # counter-current washer stages (ASSUMED)
R_WASH = 1.6                   # wash water / last-underflow liquor, mass (ASSUMED)
LS_CAKE = 0.43                 # kg liquor / kg solids in the residue filter cake, 70 wt% solids
                               # (ASSUMED, filter press for dry stacking)

# --- precipitation (D-006) -------------------------------------------------------------------
SEED = 250.0                   # g seed hydrate per L pregnant liquor (ASSUMED)
LS_SEED = 1.0                  # kg liquor / kg hydrate in seed and product slurries (ASSUMED)
CAKE_MOIST = 0.08              # free water of the washed hydrate cake, wet basis (ASSUMED)
WASH_HYD = 0.25                # wash water per kg dry hydrate (ASSUMED)

# --- energy (D-007) --------------------------------------------------------------------------
CP_LIQ = 3.35                  # kJ/kg K, liquor and water in slurries (ASSUMED)
CP_S = 1.0                     # kJ/kg K, solids (ASSUMED)
T_PDS = 373.15                 # K, pre-desilication and mill discharge (ASSUMED)
T_AMB = 298.15                 # K, bauxite, lime and make-up (ASSUMED)
T_DIG = 418.15                 # K, digestion (low-temperature digestion of gibbsite; 413-423 K
                               # per the ICSOBA 2024 paper AA05 introduction)
T_FLASH = 379.15               # K, last flash tank (ASSUMED, near atmospheric)
N_FLASH = 3                    # flash / regenerative heater stages (ASSUMED)
DT_APP = 5.0                   # K, approach in each regenerative heater (ASSUMED)
LAMBDA_FLASH = 2230.0          # kJ/kg, latent heat of the flash vapour (~ 383-413 K steam tables)
DH_DIG = 20.6                  # kJ/mol Al(OH)3(s) + NaOH(aq) -> NaAl(OH)4(aq), endothermic, from
                               # formation enthalpies (process/reactions.yaml, ASSUMED)
LOSS_DIG = 0.03                # heat losses of digestion as a fraction of the steam duty (ASSUMED)
T_PREG = 373.15                # K, pregnant liquor leaving the settler (ASSUMED)
T_FILL = 351.15                # K, precipitation fill after the liquor coolers (ASSUMED)
T_END = 335.15                 # K, last precipitator (ASSUMED)
REC_E401 = 0.70                # share of the E-401 duty recovered into the spent liquor (ASSUMED)
ECONOMY = 3.0                  # kg water evaporated per kg LP steam, multiple effect (ASSUMED)
LAMBDA_LPS = 2108.0            # kJ/kg, LP steam 450 kPa(a) latent heat (steam tables)
CALC_ENERGY = 2.8              # GJ/t alumina (LHV) of the gas suspension calciner: ICSOBA 2017
                               # paper AA22 reports ~2.72 GJ/t average for GSC units; ASSUMED 2.8
LHV_CH4 = 50.0                 # MJ/kg (natural gas as methane, ASSUMED)
LAMBDA_AIR = 1.15              # calciner air excess (ASSUMED)
O2_AIR = 0.2314                # O2 mass fraction of dry air (N2 carries the argon)
POWER_T = 152.0                # kWh/t alumina: IAI 2019 LCI report Table 4, electricity 547 MJ/t
                               # Al2O3 (2019 global average), used as the lumped demand
DH_PREC = -DH_DIG              # kJ/mol, precipitation releases the dissolution heat


def mol(stream: dict, c: str) -> float:
    return stream.get(c, 0.0) / MW[c]


def add(*streams: dict) -> dict:
    out: dict = {}
    for s in streams:
        for k, v in s.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(s: dict, f: float) -> dict:
    return {k: v * f for k, v in s.items()}


def total(s: dict) -> float:
    return sum(s.values())


def react(s: dict, stoich: dict, extent: float) -> dict:
    """extent in kmol/h."""
    out = dict(s)
    for c, nu in stoich.items():
        out[c] = out.get(c, 0.0) + nu * extent * MW[c]
        if out[c] < -1e-6:
            raise ValueError(f"negative {c}: {out[c]}")
        out[c] = max(out[c], 0.0)
    return out


R_DESIL = {"Kaol": -3, "NaOH": -8, "DSP": 1, "H2O": 9}
R_DIG = {"AlOH3": -1, "NaOH": -1, "NaAlO2": 1, "H2O": 2}
R_SLAKE = {"CaO": -1, "H2O": -1, "CaOH2": 1}
R_TCA = {"CaOH2": -3, "NaAlO2": -2, "H2O": -4, "TCA": 1, "NaOH": 2}
R_PREC = {"NaAlO2": -1, "H2O": -2, "AlOH3": 1, "NaOH": 1}
R_CALC = {"AlOH3": -2, "Al2O3": 1, "H2O": 3}
R_SODA = {"NaOH": -2, "Na2O": 1, "H2O": 1}
R_COMB = {"CH4": -1, "O2": -2, "CO2": 1, "H2O": 2}


def caustic(s: dict) -> float:
    """C as kg Na2CO3 equivalent per h (NaOH + NaAlO2 sodium)."""
    return (mol(s, "NaOH") + mol(s, "NaAlO2")) / 2 * MW_NA2CO3


def alumina(s: dict) -> float:
    """A as kg Al2O3 per h of the dissolved aluminate."""
    return mol(s, "NaAlO2") / 2 * MW["Al2O3"]


def liquid(s: dict) -> dict:
    return {k: v for k, v in s.items() if k not in SOLIDS}


def solid(s: dict) -> dict:
    return {k: v for k, v in s.items() if k in SOLIDS}


def spent_liquor(mass: float) -> dict:
    """Spent liquor of C_SPENT and AC_SPENT, mass kg/h."""
    litre = mass / RHO_LIQ
    c = C_SPENT * litre / 1000          # kg Na2CO3 eq
    a = AC_SPENT * c                    # kg Al2O3
    n_al = 2 * a / MW["Al2O3"]
    n_na = 2 * c / MW_NA2CO3
    s = {"NaAlO2": n_al * MW["NaAlO2"], "NaOH": (n_na - n_al) * MW["NaOH"]}
    s["H2O"] = mass - s["NaAlO2"] - s["NaOH"]
    return s


def bauxite_dry() -> dict:
    """Normative mineralogy (mass fractions) of the dry bauxite from ASSAY (D-003)."""
    m = MW
    kaol = KAOL_WT
    al_k = kaol * m["Al2O3"] / m["Kaol"]
    si_k = kaol * 2 * m["SiO2"] / m["Kaol"]
    h_k = kaol * 2 * m["H2O"] / m["Kaol"]
    mono = MONO_WT
    al_m = mono * m["Al2O3"] / (2 * m["AlOOH"])
    goe = GOETHITE_WT
    fe_g = goe * m["Fe2O3"] / (2 * m["FeOOH"])
    al_g = ASSAY["Al2O3"] - al_k - al_m
    gib = al_g * 2 * m["AlOH3"] / m["Al2O3"]
    d = {"AlOH3": gib, "AlOOH": mono, "Kaol": kaol, "SiO2": ASSAY["SiO2"] - si_k,
         "FeOOH": goe, "Fe2O3": ASSAY["Fe2O3"] - fe_g,
         "TiO2": ASSAY["TiO2"] + ASSAY["minor"]}   # TiO2 stands for titania and minor oxides
    water = gib - al_g + (mono - al_m) + h_k + (goe - fe_g)
    d_total = sum(d.values())
    info = {"LOI_calc": water, "LOI_assay": ASSAY["LOI"], "sum_raw": d_total}
    return {k: v / d_total for k, v in d.items()}, info


def balance(bx_dry: float, spent: float, verbose=False):
    """One pass of the plant for a dry bauxite feed and a spent liquor circulation (kg/h).
    Returns the streams, duties and the targets for the outer solver."""
    st: dict = {}
    frac, _ = bauxite_dry()
    bx = scale(frac, bx_dry)
    bx["H2O"] = bx_dry * BX_MOIST / (1 - BX_MOIST)
    st["S1"] = bx                                           # wet bauxite
    lime_cao = LIME * PRODUCT / 1000
    st["S2"] = {"CaO": lime_cao}                            # quicklime
    cah = lime_cao / MW["CaO"] * MW["CaOH2"]
    w_slake = cah / MILK - cah + lime_cao / MW["CaO"] * MW["H2O"]
    st["S3"] = {"H2O": w_slake}                             # slaking water
    st["S4"] = react(add(st["S2"], st["S3"]), R_SLAKE, lime_cao / MW["CaO"])   # milk of lime
    sl = spent_liquor(spent)
    return sl, bx, st


def solve():
    """Outer loop: find the spent liquor circulation and the bauxite feed that make PRODUCT at
    AC_DIG, with every recycle (washer overflow, seed, filtrates, condensate) converged by
    successive substitution. The caustic make-up keeps the sodium inventory; the evaporator
    keeps the water inventory (spent liquor back at C_SPENT)."""
    frac, info = bauxite_dry()
    # fixed side feeds
    lime_cao = LIME * PRODUCT / 1000
    S2 = {"CaO": lime_cao}
    cah = lime_cao / MW["CaO"] * MW["CaOH2"]
    S3 = {"H2O": cah / MILK - cah + lime_cao / MW["CaO"] * MW["H2O"]}
    S4 = react(add(S2, S3), R_SLAKE, lime_cao / MW["CaO"])
    # product
    S40 = {k: PRODUCT * w for k, w in W_PROD.items()}
    n_al2o3 = S40["Al2O3"] / MW["Al2O3"]
    n_na2o = S40["Na2O"] / MW["Na2O"]
    hyd = 2 * n_al2o3 * MW["AlOH3"]                         # dry hydrate to the calciner
    occl = 2 * n_na2o * MW["NaOH"]                           # occluded soda (fixed in the cake)

    # initial guesses
    bx_dry = 2.0 * PRODUCT
    spent = 2.0e6
    wash_ovf = {"H2O": 3e5}
    for it in range(400):
        bx = scale(frac, bx_dry)
        bx["H2O"] = bx_dry * BX_MOIST / (1 - BX_MOIST)
        S1 = bx
        # the spent liquor to the mill is the evaporated liquor of the last pass (tear),
        # scaled by the circulation correction until the blow-off A/C is met
        if it == 0:
            mu = {"NaOH": 0.0, "H2O": 0.0}
            s28_prev = spent_liquor(spent)
        S30 = scale(s28_prev, k_circ) if it else s28_prev   # spent liquor to the mill
        S31 = mu                                            # caustic make-up (to the mill)
        # G-101 mill + R-101 pre-desilication (DESIL, TCA)
        S5 = add(S1, S4, S30, S31)                          # mill discharge
        s = react(S5, R_DESIL, X_KAOL * mol(S5, "Kaol") / 3)
        s = react(s, R_TCA, mol(s, "CaOH2") / 3)
        S6 = s                                              # desilicated slurry
        # E-201/E-202 heating, R-201 digestion
        n_dig = X_GIB * mol(S6, "AlOH3")
        S7 = S6
        S8 = react(S7, R_DIG, n_dig)                        # digester blow-off
        # F-201 flash: vapour to E-201
        m8 = total(S8)
        cp8 = CP_LIQ * total(liquid(S8)) + CP_S * total(solid(S8))
        vap = cp8 * (T_DIG - T_FLASH) / LAMBDA_FLASH
        S9 = {"H2O": vap}                                   # flash vapour
        S10 = add(S8, {"H2O": -vap})                        # flashed slurry
        S11 = dict(S9)                                      # flash condensate
        # T-301 settler: washer overflow in, underflow at LS_SETTLER
        feed = add(S10, wash_ovf)
        sol = solid(feed)
        liq = liquid(feed)
        m_uf_liq = LS_SETTLER * total(sol)
        f_uf = m_uf_liq / total(liq)
        S13 = add(sol, scale(liq, f_uf))                    # settler underflow
        S12 = scale(liq, 1 - f_uf)                          # pregnant liquor (overflow)
        # T-302 washers (lumped CCD) with wash water + residue filtrate
        sol = solid(S13)
        liq_in = liquid(S13)
        m_last_liq = LS_WASHER * total(sol)
        wash_water = R_WASH * m_last_liq                    # wash water to the last washer
        # residue filter F-301: filtrate returns to the washers with the wash water
        # solute fraction left in the last underflow liquor (ideal CCD, Kremser form)
        r = R_WASH
        f_sol = (r - 1) / (r ** (N_WASH + 1) - 1)
        solutes = {k: v for k, v in liq_in.items() if k != "H2O"}
        last_solutes = scale(solutes, f_sol)
        last_liq = dict(last_solutes)
        last_liq["H2O"] = m_last_liq - total(last_solutes)
        S15 = add(sol, last_liq)                            # washed mud to the filter
        m_cake_liq = LS_CAKE * total(sol)
        S17 = add(sol, scale(last_liq, m_cake_liq / m_last_liq))   # residue cake
        S16 = scale(last_liq, 1 - m_cake_liq / m_last_liq)         # residue filtrate
        S14 = {"H2O": wash_water}                           # wash water (condensate + PW)
        ovf = add(liq_in, S14, S16, scale(last_liq, -1))
        wash_ovf_new = ovf                                  # washer overflow to the settler
        # E-401 cooling, R-401 precipitation with seed recycle
        preg_l = total(S12) / RHO_LIQ
        seed = SEED * preg_l / 1000
        # seed slurry: hydrate + spent liquor of the overflow composition (from the last pass)
        if it == 0:
            ovf_comp = scale(spent_liquor(1.0), 1.0)
        seed_liq = scale(ovf_comp, LS_SEED * seed / total(ovf_comp))
        S20 = add({"AlOH3": seed}, seed_liq)                # seed slurry recycle
        mix = add(S12, S20)
        liq = liquid(mix)
        c = caustic(liq)
        a_target = AC_SPENT * c
        n_prec = (alumina(liq) - a_target) * 2 / MW["Al2O3"]
        S19 = react(mix, R_PREC, n_prec)                    # precipitator discharge
        # S-401 classification: seed slurry, product slurry, spent liquor overflow
        liq19 = liquid(S19)
        hyd_out = S19["AlOH3"] - seed                       # net hydrate to the filter
        prod_liq = scale(liq19, LS_SEED * hyd_out / total(liq19))
        S21 = add({"AlOH3": hyd_out}, prod_liq)            # product hydrate slurry
        S22 = add(liq19, scale(seed_liq, -1), scale(prod_liq, -1))   # spent liquor overflow
        ovf_comp = scale(liq19, 1 / total(liq19))
        # F-401 hydrate filter: occluded soda stays in the cake, free liquor displaced by
        # wash water; the cake leaves with CAKE_MOIST free water
        wash_h = WASH_HYD * hyd_out
        S23 = {"H2O": wash_h}
        occl_now = occl * hyd_out / hyd
        cake_w = CAKE_MOIST / (1 - CAKE_MOIST) * (hyd_out + occl_now)
        S24 = {"AlOH3": hyd_out, "NaOH": occl_now, "H2O": cake_w}  # washed hydrate cake
        S25 = add(S21, S23, scale(S24, -1))                 # hydrate filtrate
        # E-501 evaporation: spent liquor + filtrate + residue... back to C_SPENT
        S26 = add(S22, S25)                                 # to evaporation
        c26 = caustic(S26)
        litre = c26 / (C_SPENT / 1000)
        m_target = litre * RHO_LIQ
        evap = total(S26) - m_target
        S27 = {"H2O": evap}                                 # evaporator condensate
        S28 = add(S26, {"H2O": -evap})                      # evaporated spent liquor
        # sodium inventory: the make-up replaces what the liquor loses
        # (DSP, residue cake liquor, occluded soda); M-501 mixes it in.
        # The A/C of S28 differs slightly from AC_SPENT (filtrates, TCA): the circulation
        # carried to the mill is S28 itself (S30 = S28 + make-up) in the next pass.
        na_loss = 8 * mol(S6, "DSP") + mol(S17, "NaOH") + mol(S17, "NaAlO2") + mol(S24, "NaOH")
        mu_new = {"NaOH": na_loss * MW["NaOH"]}
        mu_new["H2O"] = mu_new["NaOH"] * (1 - NAOH_MU) / NAOH_MU
        # outer targets: product hydrate and blow-off A/C
        ac_blow = alumina(liquid(S8)) / caustic(liquid(S8))
        # update bauxite to hit the hydrate, spent circulation to hit AC_DIG
        bx_dry *= (hyd / hyd_out) ** 0.7
        k_circ = (ac_blow / AC_DIG) ** 0.7
        s28_prev = S28
        wash_ovf = wash_ovf_new
        mu = mu_new
        err = (abs(hyd_out / hyd - 1) + abs(ac_blow / AC_DIG - 1)
               + abs(total(S28) / total(S30) - 1))
        if err < 1e-10 and it > 20:
            break
    # S28 (evaporated) vs the spent liquor assumed at the mill (S30): report the mismatch
    st = {k: v for k, v in locals().items() if k.startswith("S") and k[1:].isdigit()}
    st["wash_ovf"] = wash_ovf
    st["conv"] = {"DIG": X_GIB, "PREC": n_prec / mol(mix, "NaAlO2")}
    # calciner R-601
    q_fuel = CALC_ENERGY * PRODUCT                          # MJ/h
    ch4 = q_fuel / LHV_CH4
    o2 = 2 * ch4 / MW["CH4"] * MW["O2"] * LAMBDA_AIR
    air = o2 / O2_AIR
    st["S35"] = {"CH4": ch4}
    st["S36"] = {"O2": air * O2_AIR, "N2": air * (1 - O2_AIR)}
    s = add(S24, st["S35"], st["S36"])
    s = react(s, R_CALC, mol(s, "AlOH3") / 2)
    s = react(s, R_SODA, mol(s, "NaOH") / 2)
    s = react(s, R_COMB, mol(s, "CH4"))
    # product keeps LOI water W_PROD
    st["S40"] = S40
    flue = add(s, scale(S40, -1))
    st["S41"] = {k: v for k, v in flue.items() if abs(v) > 1e-9}
    # duties, kW
    cp6 = CP_LIQ * total(liquid(S6)) + CP_S * total(solid(S6))
    t_e201 = T_PDS + (T_DIG - T_FLASH) * N_FLASH / (N_FLASH + 1) - DT_APP
    q_e201 = cp6 * (t_e201 - T_PDS) / 3600
    q_flash = vap * LAMBDA_FLASH / 3600
    q_vent = q_flash - q_e201                               # flash heat not recovered -> CW
    q_e202 = (cp6 * (T_DIG - t_e201) + n_dig * DH_DIG * 1000) / 3600 / (1 - LOSS_DIG)
    cp12 = CP_LIQ * total(S12)
    q_e401 = cp12 * (T_PREG - T_FILL) / 3600
    q_e401_cw = q_e401 * (1 - REC_E401)
    # E-101 spent liquor heater: the mill feed (spent liquor from T_END, bauxite, milk of lime
    # and make-up from ambient) is brought to T_PDS by the heat recovered in E-401 and the
    # flash vapour E-201 cannot use; LP steam covers the rest (D-007)
    q_need = (CP_LIQ * total(S30) * (T_PDS - T_END)
              + (CP_LIQ * S1["H2O"] + CP_S * total(solid(S1))) * (T_PDS - T_AMB)
              + CP_LIQ * (total(S4) + total(S31)) * (T_PDS - T_AMB)) / 3600
    q_rec = q_e401 * REC_E401 + q_vent
    q_e101 = max(q_need - q_rec, 0.0)
    q_vent_cw = max(q_rec - q_need, 0.0)
    q_r401 = (cp12 * (T_FILL - T_END) - n_prec * DH_PREC * 1000) / 3600
    lps = evap / ECONOMY
    q_e501 = lps * LAMBDA_LPS / 3600
    q_e501_cw = q_e501
    duties = {"Q_E201_rec": q_e201, "Q_flash_surplus": q_vent, "Q_E101_need": q_need,
              "Q_E101_rec": q_rec, "Q_E101": q_e101, "Q_vent_cw": q_vent_cw, "Q_E202": q_e202,
              "Q_E401_cw": q_e401_cw, "Q_E401_rec": q_e401 * REC_E401, "Q_R401_cw": q_r401,
              "Q_E501": q_e501, "Q_E501_cw": q_e501_cw, "Q_power": POWER_T * PRODUCT / 1000,
              "Q_fuel_MW": q_fuel / 3600, "t_e201": t_e201, "lps_kg_h": lps}
    return st, duties, info, it, err


def elements(s: dict) -> dict:
    out: dict = {}
    for c, m in s.items():
        for e, n in ELEMENTS[c].items():
            out[e] = out.get(e, 0.0) + m / MW[c] * n * AW[e]
    return out


SRC = "scripts/bayer_balance.py"
FLOWSHEET = {}  # filled by yaml_streams(), see write_balance_output()
PASS_THROUGH = {"S8", "S11", "S12", "S24"}   # heaters and coolers without a phase change


def yaml_streams(st: dict, du: dict) -> str:
    """Stream entries of process/flowsheet.yaml (ids of the flowsheet, not of the script)."""
    pw = st["S14"]["H2O"] + st["S23"]["H2O"] + st["S3"]["H2O"] - st["S11"]["H2O"] - st["S27"]["H2O"]
    s7 = add(st["S28"], st["S31"])
    t_e201 = du["t_e201"]
    rows = [
        # id, title, from, to, stream, T K, P kPa(a), source note
        ("S1", "Bauxite (wet, 10 % moisture)", "BX.out", "G101.bx", st["S1"], 298.15, 101.325, "dry feed solved for 3000 t/d alumina; mineralogy D-003"),
        ("S2", "Quicklime", "LIME.out", "M101.lime", st["S2"], 298.15, 101.325, "52 kg CaO/t alumina (IAI 2019 LCI report), D-004"),
        ("S3", "Slaking water (condensate)", "T501.slk", "M101.water", st["S3"], 353.15, 300, "milk of lime 15 wt% Ca(OH)2, D-004"),
        ("S4", "Milk of lime", "M101.milk", "G101.milk", st["S4"], 353.15, 300, "D-004"),
        ("S5", "Caustic soda make-up (50 wt% NaOH)", "NAOH.out", "M501.naoh", st["S31"], 298.15, 300, "replaces the sodium leaving with DSP, residue liquor and product, D-005"),
        ("S6", "Evaporated spent liquor", "E501.liq", "M501.in", st["S28"], T_END, 101.325, "evaporated to C 250 g/L (Na2CO3), D-006"),
        ("S7", "Spent liquor with caustic make-up", "M501.out", "E101.in", s7, T_END, 500, "D-006"),
        ("S8", "Heated spent liquor to the mill", "E101.out", "G101.liq", s7, T_PDS, 400, "D-007"),
        ("S9", "Mill discharge slurry", "G101.out", "R101.in", st["S5"], T_PDS, 101.325, "D-004"),
        ("S10", "Desilicated slurry", "R101.out", "E201.in", st["S6"], T_PDS, 101.325, "kaolinite to DSP, lime to TCA, D-004"),
        ("S11", "Slurry preheated by flash vapour", "E201.out", "E202.in", st["S6"], round(t_e201, 2), 800, "3 flash stages, 5 K approach, D-007"),
        ("S12", "Slurry heated to digestion", "E202.out", "R201.in", st["S6"], T_DIG, 700, "D-007"),
        ("S13", "Digester blow-off (A/C 0.70)", "R201.out", "F201.in", st["S8"], T_DIG, 600, "98 % of the gibbsite dissolved, D-004"),
        ("S14", "Flash vapour", "F201.vap", "E201.vap", st["S9"], 393.15, 200, "flash from 418 K to 379 K, D-007"),
        ("S15", "Flash vapour condensate", "E201.cond", "T501.fc", st["S11"], 373.15, 300, "D-007"),
        ("S16", "Flashed slurry", "F201.out", "T301.in", st["S10"], T_FLASH, 101.325, "D-004"),
        ("S17", "Washer overflow (weak liquor) to the settler", "T302.ovf", "T301.wash", st["wash_ovf"], 368.15, 101.325, "D-005"),
        ("S18", "Pregnant liquor (settler overflow, after security filtration)", "T301.ovf", "E401.in", st["S12"], T_PREG, 101.325, "solids-free (ASSUMED), D-005"),
        ("S19", "Settler underflow mud", "T301.uf", "T302.mud", st["S13"], T_PREG, 101.325, "2.0 kg liquor/kg solids, D-005"),
        ("S20", "Washed mud", "T302.mud_out", "F301.in", st["S15"], 353.15, 101.325, "6 CCD stages, wash ratio 1.6, D-005"),
        ("S21", "Residue filtrate", "F301.filtrate", "T302.filtrate", st["S16"], 353.15, 101.325, "D-005"),
        ("S22", "Residue wash water (condensate)", "T501.wash", "T302.water", st["S14"], 353.15, 300, "D-005"),
        ("S23", "Bauxite residue filter cake (70 wt% solids)", "F301.cake", "RES.in", st["S17"], 343.15, 101.325, "D-005"),
        ("S24", "Cooled pregnant liquor", "E401.out", "R401.in", st["S12"], T_FILL, 300, "D-006"),
        ("S25", "Seed slurry recycle", "S401.seed", "R401.seed", st["S20"], T_END, 300, "250 g/L seed charge, D-006"),
        ("S26", "Precipitator discharge", "R401.out", "S401.in", st["S19"], T_END, 101.325, "spent A/C 0.38, D-006"),
        ("S27", "Product hydrate slurry", "S401.prod", "F401.in", st["S21"], T_END, 300, "D-006"),
        ("S28", "Spent liquor (classifier overflow)", "S401.ovf", "E501.feed", st["S22"], T_END, 300, "D-006"),
        ("S29", "Hydrate wash water (condensate)", "T501.hwash", "F401.wash", st["S23"], 353.15, 300, "0.25 kg/kg hydrate, D-006"),
        ("S30", "Hydrate filtrate and washings", "F401.filtrate", "E501.filt", st["S25"], T_END, 101.325, "D-006"),
        ("S31", "Washed hydrate cake", "F401.cake", "R601.in", st["S24"], T_END, 101.325, "8 wt% free water; occluded soda for 0.4 % Na2O, D-006"),
        ("S32", "Evaporator condensate", "E501.cond", "T501.ec", st["S27"], 333.15, 101.325, "D-006"),
        ("S33", "Fresh water make-up", "PW.out", "T501.pw", {"H2O": pw}, 298.15, 300, "closes the water balance of the condensate tank, D-005"),
        ("S34", "Natural gas (as methane)", "NG.out", "R601.fuel", st["S35"], 298.15, 400, "2.8 GJ/t alumina LHV (ICSOBA 2017 AA22 range), D-008"),
        ("S35", "Calciner combustion air", "AIR.out", "R601.air", st["S36"], 298.15, 101.325, "air excess 1.15, D-008"),
        ("S36", "Smelter-grade alumina", "R601.prod", "ALU.in", st["S40"], 353.15, 101.325, "design basis 3000 t/d, D-002"),
        ("S37", "Calciner flue gas to the stack (after ESP)", "R601.gas", "STACK.in", st["S41"], 423.15, 101.325, "D-008"),
    ]
    out = []
    for sid, title, fr, to, s, t, p, note in rows:
        m = total(s)
        comp = ", ".join(f"{c}: {v / m:.7f}" for c, v in s.items() if v / m >= 5e-8)
        if sid in PASS_THROUGH:      # flow and composition by cheme process propagate --fill
            out.append(f"  - id: {sid}\n    title: \"{title}\"\n    from: {fr}\n    to: {to}\n"
                       f"    template: bayer\n    state:\n      design:\n"
                       f"        pressure: {{value: {p}, provenance: assumed, source: \"D-007\"}}\n"
                       f"        temperature: {{value: {t}, provenance: assumed, source: \"{SRC}: {note}\"}}")
            continue
        out.append(f"  - id: {sid}\n    title: \"{title}\"\n    from: {fr}\n    to: {to}\n"
                   f"    template: bayer\n    state:\n      design:\n"
                   f"        pressure: {{value: {p}, provenance: assumed, source: \"D-007\"}}\n"
                   f"        temperature: {{value: {t}, provenance: assumed, source: \"D-007\"}}\n"
                   f"        flow: {{value: {m:.1f}, basis: mass, provenance: assumed, source: \"{SRC}: {note}\"}}\n"
                   f"        composition: {{basis: mass_fraction, values: {{{comp}}}, provenance: assumed, source: \"{SRC}\"}}")
    e = [
        ("Q1", "E-202 digestion heater (MP steam)", "MPS.e202", "E202.heat", du["Q_E202"], "slurry to 418 K plus dissolution heat, 3 % losses"),
        ("Q2", "E-101 spent liquor heater (LP steam)", "LPS.e101", "E101.heat", du["Q_E101"], "mill feed to 373 K less the recovered heat Q8, Q9"),
        ("Q3", "E-501 evaporator (LP steam)", "LPS.e501", "E501.heat", du["Q_E501"], "economy 3.0 kg/kg"),
        ("Q4", "E-501 surface condenser", "E501.cw", "CW.e501", du["Q_E501_cw"], "equal to the steam heat"),
        ("Q5", "E-401 liquor cooler, part to cooling water", "E401.cw", "CW.e401", du["Q_E401_cw"], "30 % of the 373 -> 351 K duty"),
        ("Q6", "R-401 precipitator interstage coolers", "R401.cw", "CW.r401", du["Q_R401_cw"], "351 -> 335 K plus precipitation heat"),
        ("Q7", "Electric power (lumped: mills, pumps, agitators, filters, fans)", "POWER.aux", "G101.power", du["Q_power"], "152 kWh/t (IAI 2019 LCI report Table 4)"),
        ("Q8", "E-401 heat recovered into the spent liquor", "E401.rec", "E101.rec", du["Q_E401_rec"], "70 % of the E-401 duty"),
        ("Q9", "Flash vapour heat beyond E-201, to the spent liquor heater", "E201.surplus", "E101.flash", du["Q_flash_surplus"], "flash heat not taken by the slurry"),
    ]
    for qid, title, fr, to, d, note in e:
        out.append(f"  - {{id: {qid}, title: \"{title}\", kind: energy, from: {fr}, to: {to}, state: "
                   f"{{design: {{duty: {{value: {d:.1f}, provenance: assumed, source: \"{SRC}: {note} (D-007)\"}}}}}}}}")
    # the values process/flowsheet.yaml cites from this script (balance-output contract), in the
    # flowsheet's ids: kept for main() to write
    FLOWSHEET.clear()
    for sid, title, fr, to, s, t, p, note in rows:
        m = total(s)
        FLOWSHEET[sid] = {"temperature": t, "pressure": p,
                          "flow": {"value": m, "basis": "mass"},
                          "composition": {"values": {c: v / m for c, v in s.items()},
                                          "basis": "mass_fraction"}}
    FLOWSHEET.update({qid: {"duty": d} for qid, title, fr, to, d, note in e})
    return "\n".join(out)


def main():
    st, du, info, it, err = solve()
    yaml_streams(st, du)  # fills FLOWSHEET
    write_balance_output({"design": FLOWSHEET})
    yaml = "--yaml" in sys.argv
    if yaml:
        print(yaml_streams(st, du))
        return
    if not yaml:
        print(f"iterations {it}, residual {err:.2e}; bauxite LOI calc {info['LOI_calc']:.2f} vs "
              f"assay {info['LOI_assay']:.2f} wt%, normative sum {info['sum_raw']:.2f}")
        print("conversions", st["conv"])
        for k in sorted((x for x in st if x[1:].isdigit()), key=lambda x: int(x[1:])):
            s = st[k]
            m = total(s)
            print(f"{k:4s} {m:12.1f} kg/h  " + ", ".join(
                f"{c}: {v / m:.6f}" for c, v in s.items() if v > 1e-9))
        for k, v in du.items():
            print(f"{k:12s} {v:12.1f}")
        s8 = liquid(st["S8"])
        s30 = st["S30"]
        print(f"A/C blow-off {alumina(s8) / caustic(s8):.4f}; spent (S28) "
              f"{alumina(st['S28']) / caustic(st['S28']):.4f}; C S28 "
              f"{caustic(st['S28']) / (total(st['S28']) / RHO_LIQ):.1f} g/L; S28 vs S30 "
              f"{total(st['S28']) - total(s30):.1f} kg/h")
        p = PRODUCT / 1000
        print("per t alumina: bauxite wet %.0f kg, dry %.0f kg; NaOH %.1f kg; CaO %.1f kg;"
              " residue cake %.0f kg (dry %.0f); CH4 %.1f kg; LPS %.0f kg; MP heat %.0f kWh;"
              " evap %.0f kg; wash water %.0f kg" % (
                  total(st["S1"]) / p, (total(st["S1"]) - st["S1"]["H2O"]) / p,
                  st["S31"]["NaOH"] / p, st["S2"]["CaO"] / p, total(st["S17"]) / p,
                  total(solid(st["S17"])) / p, st["S35"]["CH4"] / p, du["lps_kg_h"] / p,
                  du["Q_E202"] / p, st["S27"]["H2O"] / p,
                  (st["S14"]["H2O"] + st["S23"]["H2O"]) / p))
        cond = st["S11"]["H2O"] + st["S27"]["H2O"]
        need = st["S14"]["H2O"] + st["S23"]["H2O"] + st["S3"]["H2O"]
        print(f"condensate {cond:.1f} kg/h, wash need {need:.1f} kg/h, fresh water "
              f"{need - cond:.1f} kg/h")
        # overall element balance
        ins = add(st["S1"], st["S2"], st["S3"], st["S31"], st["S14"], st["S23"],
                  st["S35"], st["S36"])
        outs = add(st["S17"], st["S40"], st["S41"], st["S11"], st["S27"])
        # S28 -> S30 recycle closure counted as a mismatch
        ei, eo = elements(ins), elements(outs)
        eo_rec = elements(add(st["S28"], scale(st["S30"], -1)))
        for e in sorted(ei):
            print(f"  {e:2s} in {ei[e]:12.2f} out {eo.get(e, 0):12.2f} "
                  f"recycle mismatch {eo_rec.get(e, 0):10.2f}")


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


if __name__ == "__main__":
    main()
