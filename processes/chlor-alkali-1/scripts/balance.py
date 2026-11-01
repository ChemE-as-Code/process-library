"""Heat and material balance of the chlor-alkali-1 membrane-cell plant (DESIGN.md D-006).

Run: ``cheme run scripts/balance.py``. Prints the material and energy streams of
process/flowsheet.yaml (flow-style YAML, kg/h and mass fractions, kW) and the key figures per
tonne of chlorine. Every input below is a design choice or a sourced value with its locator in
DESIGN.md; "BREF" is the EU JRC Best Available Techniques Reference Document for the Production of
Chlor-alkali (2014, DOI 10.2791/13138). Values written into the flowsheet are `assumed` with this
script as their source; cheme checks the balances (cheme validate, cheme process cell).

Simplifications (DESIGN.md D-006): electrolyte enthalpies are not modelled, so the
downstream duties use constant heat capacities and latent heats (ASSUMED); hypochlorite and
chlorate in the anolyte, chloride in the caustic and dissolved gases other than Cl2 are
neglected.
"""

import math

F = 96485.33212  # C/mol, CODATA 2018
MW = {
    "NaCl": 58.443, "H2O": 18.015, "NaOH": 39.997, "Cl2": 70.906, "H2": 2.016, "O2": 31.998,
    "CO2": 44.009, "HCl": 36.461, "Na2SO4": 142.04, "Na2CO3": 105.99, "Na2SO3": 126.04,
    "H2SO4": 98.079, "CaSO4": 136.14, "MgCl2": 95.211, "CaCO3": 100.09, "MgOH2": 58.320,
    "SiO2": 60.084,
}

# --- design basis (D-002 .. D-012) ----------------------------------------------------------
CL2_PRODUCT = 12500.0 / 3600  # kg/s dry chlorine at the gate: 100 kt/a at 8000 h/a (D-002)
CE = 0.965  # current efficiency of 2 NaCl + 2 H2O -> Cl2 + H2 + 2 NaOH (D-004, BREF 2.4.1)
SIDE = 1 - CE  # the rest forms O2 at the anode (back-migrated OH-): net 2 H2O -> 2 H2 + O2
VOLTAGE = 3.0  # V per cell (BREF 4.3.2.3.2: 3.0 V at 6.0 kA/m2, 90 degC, 32 wt-% NaOH)
AREA = 2.7  # m2 active area per bipolar element (ASSUMED, D-004)
J_MAX = 6000.0  # A/m2 design current density (BREF 4.3.2.3.2)
RECTIFIER_EFF = 0.97  # transformer + rectifier, AC -> DC (ASSUMED, D-009)
T_CELL = 363.15  # K (BREF 4.3.2.3.2)
H2O_PER_NA = 4.0  # mol water carried through the membrane per mol Na+ (BREF 2.4.1: 3.5-4.5)
W_NACL_FEED = 0.26  # feed brine NaCl mass fraction, ~310 g/l (BREF 2.5.2: 310-315 g/l)
W_NACL_ANOLYTE = 0.177  # depleted brine, ~200 g/l at 1.13 kg/l (BREF 4.3.2.3.2: 200 g/l)
W_SO4_FEED = 0.006  # Na2SO4 in feed brine, ~7 g/l (BREF Table 2.4: < 4-8 g/l); sets the purge
W_NAOH_CELL = 0.32  # catholyte (BREF 2.4.1: 32 +/- 1 wt-%)
W_NAOH_PRODUCT = 0.50
CL2_IN_ANOLYTE = 0.62e-3  # kg/kg, 0.7 g/l (BREF 2.5.4: 0.4-1 g/l)
CL2_RESIDUAL = 20e-6  # kg/kg after vacuum stripping (BREF 2.5.4: 10-30 mg/l)
CL2_IN_CONDENSATE = 0.007  # kg/kg chlorine water from the gas coolers (ASSUMED, D-007)
HCL_DECHLOR = 0.010  # mol HCl per kg brine to pH ~2 before stripping (BREF 2.5.4: pH 2-2.5)
W_HCL_ACID = 0.32  # purchased hydrochloric acid
W_NAOH_INTERNAL = W_NAOH_CELL  # caustic used in the brine loop is the cells' 32 wt-%
NA2CO3_EXCESS = 0.5e-3  # kg/kg raw brine above stoichiometry (ASSUMED, D-005)
NAOH_EXCESS = 0.3e-3  # kg/kg raw brine above stoichiometry (ASSUMED, D-005)
CAKE_SOLIDS = 0.5  # mass fraction of solids in the brine filter cake (ASSUMED, D-005)
IX_HCL = 1.0e-3  # kg HCl per kg Cl2 for resin regeneration (ASSUMED, D-005)
IX_RINSE = 0.15  # kg demineralised rinse water per kg Cl2 (ASSUMED, D-005)
SALT = {"NaCl": 0.988, "CaSO4": 0.0015, "MgCl2": 0.0005, "SiO2": 0.005, "H2O": 0.005}  # D-003
W_H2SO4_FEED, W_H2SO4_SPENT = 0.98, 0.75  # drying acid in and out (D-008, BREF Table 3.6)
EVAP_ECONOMY = 1.8  # kg water evaporated per kg steam, double effect (ASSUMED, D-010)
AUX_TOTAL = 177.0  # kWh/t Cl2, all electricity but the cells (BREF Table 3.12, median)
# pressures, kPa(a) (ASSUMED, D-007/D-008)
P_ANODE, P_CATHODE, P_CL2_COOLED, P_CL2_DRY, P_CL2_PRODUCT = 115.0, 117.0, 108.0, 105.0, 400.0
P_H2_COOLED, P_H2_PRODUCT = 112.0, 140.0
P_STRIP = 55.0  # vacuum dechlorination (BREF 2.5.4: 50-60 kPa)
# water vapour pressure, kPa (IAPWS-IF97 saturation) and latent heat, kJ/kg
PSAT = {293.15: 2.339, 308.15: 5.629, 313.15: 7.385, 363.15: 70.18}
HFG_90C, HFG_50C, HFG_STEAM = 2283.0, 2382.0, 2015.0  # steam at 1000 kPa(a), 453.0 K
P_W_CATHOLYTE = 28.0  # kPa water over 32 wt-% NaOH at 90 degC (ASSUMED, D-007)
PHI_BRINE = 1.0  # osmotic coefficient of 3.7 mol/kg NaCl (ASSUMED, D-007)
CP_BRINE, CP_WATER, CP_CAUSTIC32, CP_CAUSTIC50 = 3.3, 4.18, 3.5, 3.2  # kJ/(kg K) (ASSUMED)
CP_GAS = {"Cl2": 34.0, "O2": 29.4, "H2": 28.8, "H2O": 33.6}  # J/(mol K), ideal gas ~300-360 K
T_SAT_BRINE, T_FEED_BRINE, T_DMW = 328.15, 343.15, 313.15  # K (ASSUMED, D-005/D-007)


def mol(d):
    return {k: v / MW[k] * 1000 for k, v in d.items()}  # kg/s -> mol/s


def total(d):
    return sum(d.values())


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(d, f):
    return {k: v * f for k, v in d.items()}


def kg(k, n):
    return n * MW[k] / 1000  # mol/s -> kg/s


def water_activity(w_nacl):
    m = w_nacl / MW["NaCl"] * 1000 / (1 - w_nacl)
    return math.exp(-2 * m * PHI_BRINE * MW["H2O"] / 1000)


def cell(xi, feed_w):
    """Feed brine mass F from the anolyte NaCl, and the cell outlets, for xi mol/s Cl2 formed."""
    current = 2 * xi * F / CE
    xs = SIDE * current / (4 * F)  # extent of 2 H2O -> 2 H2 + O2
    y_w = water_activity(W_NACL_ANOLYTE) * PSAT[363.15] / P_ANODE
    feed_mass = 40.0
    for _ in range(50):
        feed = scale(feed_w, feed_mass)
        anolyte = dict(feed)
        anolyte["NaCl"] -= kg("NaCl", 2 * xi)
        anolyte["H2O"] += kg("H2O", -H2O_PER_NA * 2 * xi + 2 * xs)
        cl2_gas_guess = xi
        dissolved = CL2_IN_ANOLYTE * total(anolyte) / (1 - CL2_IN_ANOLYTE)
        gas_cl2 = xi - dissolved / MW["Cl2"] * 1000
        vapour = y_w / (1 - y_w) * (gas_cl2 + xs)
        anolyte["H2O"] -= kg("H2O", vapour)
        anolyte["Cl2"] = dissolved
        # NaCl mass fraction of the depleted brine: adjust the feed linearly
        w = anolyte["NaCl"] / total(anolyte)
        feed_mass *= 1 + (W_NACL_ANOLYTE - w) / (feed_w["NaCl"] - W_NACL_ANOLYTE) * 0.9
        del cl2_gas_guess
    cl2_gas = {"Cl2": kg("Cl2", gas_cl2), "O2": kg("O2", xs), "H2O": kg("H2O", vapour)}
    naoh = kg("NaOH", 2 * xi)
    caustic = {"NaOH": naoh, "H2O": naoh * (1 - W_NAOH_CELL) / W_NAOH_CELL}
    n_h2 = xi + 2 * xs
    y_c = P_W_CATHOLYTE / P_CATHODE
    h2_vapour = y_c / (1 - y_c) * n_h2
    h2_gas = {"H2": kg("H2", n_h2), "H2O": kg("H2O", h2_vapour)}
    dmw = caustic["H2O"] + kg("H2O", h2_vapour + 2 * xi + 4 * xs - H2O_PER_NA * 2 * xi)
    return dict(current=current, xs=xs, feed=feed, anolyte=anolyte, cl2_gas=cl2_gas,
                caustic=caustic, h2_gas=h2_gas, dmw={"H2O": dmw}, vapour=vapour,
                h2_vapour=h2_vapour)


def saturated_gas(gas, t, p):
    """Cool a wet gas to t: the non-condensables stay, the water above saturation condenses."""
    y = PSAT[t] / p
    dry = {k: v for k, v in gas.items() if k != "H2O"}
    n_dry = sum(mol(dry).values())
    water = kg("H2O", y / (1 - y) * n_dry)
    return add(dry, {"H2O": water}), gas["H2O"] - water


def sensible(gas, t_in, t_out):
    return sum(n * CP_GAS[k] for k, n in mol(gas).items()) * (t_in - t_out) / 1000  # kW


def solve():
    feed_w = {"NaCl": W_NACL_FEED, "Na2SO4": W_SO4_FEED, "H2O": 1 - W_NACL_FEED - W_SO4_FEED}
    xi = CL2_PRODUCT / MW["Cl2"] * 1000
    strip = {"Cl2": 0.0, "H2O": 0.0}
    salt, water, purge_frac = 1.7 * CL2_PRODUCT, 2.5, 0.04
    for _outer in range(40):
        c = cell(xi, feed_w)
        # chlorine coolers with the stripped gas, condensate to dechlorination (recycle)
        for _ in range(30):
            wet = add(c["cl2_gas"], strip)
            gas40, cond1 = saturated_gas(wet, 313.15, P_CL2_COOLED + 2)
            gas20, cond2 = saturated_gas(gas40, 293.15, P_CL2_COOLED)
            cond_water = cond1 + cond2
            cond_cl2 = CL2_IN_CONDENSATE * cond_water / (1 - CL2_IN_CONDENSATE)
            cooled = dict(gas20)
            cooled["Cl2"] -= cond_cl2
            condensate = {"H2O": cond_water, "Cl2": cond_cl2}
            brine_in = add(c["anolyte"], condensate)
            n_hcl = HCL_DECHLOR * total(brine_in)
            hcl_dcl = {"HCl": kg("HCl", n_hcl),
                       "H2O": kg("HCl", n_hcl) * (1 - W_HCL_ACID) / W_HCL_ACID}
            stripped = add(brine_in, hcl_dcl)
            residual = CL2_RESIDUAL * total(stripped)
            cl2_strip = stripped["Cl2"] - residual
            y = PSAT[313.15] / P_STRIP
            new = {"Cl2": cl2_strip, "H2O": kg("H2O", y / (1 - y) * cl2_strip / MW["Cl2"] * 1000)}
            stripped["Cl2"] = residual
            stripped["H2O"] -= new["H2O"]
            if abs(new["Cl2"] - strip["Cl2"]) < 1e-12:
                strip = new
                break
            strip = new
        # chemical dechlorination: Na2SO3 + Cl2 + 2 NaOH -> Na2SO4 + 2 NaCl + H2O; HCl + NaOH
        n_res = residual / MW["Cl2"] * 1000
        sulfite = {"Na2SO3": kg("Na2SO3", n_res)}
        n_naoh_dcl = 2 * n_res + n_hcl
        naoh_dcl = {"NaOH": kg("NaOH", n_naoh_dcl),
                    "H2O": kg("NaOH", n_naoh_dcl) * (1 - W_NAOH_INTERNAL) / W_NAOH_INTERNAL}
        dechl = add(stripped, sulfite, naoh_dcl)
        dechl = add(dechl, {"Na2SO3": -kg("Na2SO3", n_res), "Cl2": -kg("Cl2", n_res),
                            "NaOH": -kg("NaOH", n_naoh_dcl), "HCl": -kg("HCl", n_hcl),
                            "Na2SO4": kg("Na2SO4", n_res), "NaCl": kg("NaCl", 2 * n_res + n_hcl),
                            "H2O": kg("H2O", n_res + n_hcl)})
        dechl = {k: v for k, v in dechl.items() if abs(v) > 1e-12}
        # hydrogen cooler; caustic evaporation
        h2_cooled, h2_cond = saturated_gas(c["h2_gas"], 308.15, P_H2_COOLED)
        # internal caustic: computed below; product evaporator condensate depends on it

        def loop(salt, water, purge_frac, final=False):
            purge = scale(dechl, purge_frac)
            ret = scale(dechl, 1 - purge_frac)
            salt_s = scale(SALT, salt)
            # caustic to brine treatment and ion exchange first (needs raw brine) -> two passes
            raw = add(ret, salt_s, {"H2O": water + h2_cond})
            # process condensate from evaporation depends on internal caustic use: iterate
            naoh_int = 0.0
            for _ in range(5):
                evap_feed_naoh = c["caustic"]["NaOH"] - naoh_int
                evap_water = evap_feed_naoh / W_NAOH_CELL - evap_feed_naoh / W_NAOH_PRODUCT
                raw = add(ret, salt_s, {"H2O": water + h2_cond + evap_water})
                n_ca = raw["CaSO4"] / MW["CaSO4"] * 1000
                n_mg = raw["MgCl2"] / MW["MgCl2"] * 1000
                carb = {"Na2CO3": kg("Na2CO3", n_ca) + NA2CO3_EXCESS * total(raw)}
                naoh_r101 = kg("NaOH", 2 * n_mg) + NAOH_EXCESS * total(raw)
                n_ix = IX_HCL * CL2_PRODUCT / MW["HCl"] * 1000
                naoh_ix = kg("NaOH", n_ix)
                naoh_int = naoh_r101 + naoh_ix + naoh_dcl["NaOH"]
            caustic_r101 = {"NaOH": naoh_r101,
                            "H2O": naoh_r101 * (1 - W_NAOH_INTERNAL) / W_NAOH_INTERNAL}
            caustic_ix = {"NaOH": naoh_ix, "H2O": naoh_ix * (1 - W_NAOH_INTERNAL) / W_NAOH_INTERNAL}
            treated = add(raw, carb, caustic_r101)
            treated = add(treated, {
                "CaSO4": -raw["CaSO4"], "Na2CO3": -kg("Na2CO3", n_ca), "CaCO3": kg("CaCO3", n_ca),
                "Na2SO4": kg("Na2SO4", n_ca), "MgCl2": -raw["MgCl2"], "NaOH": -kg("NaOH", 2 * n_mg),
                "MgOH2": kg("MgOH2", n_mg), "NaCl": kg("NaCl", 2 * n_mg)})
            treated = {k: v for k, v in treated.items() if abs(v) > 1e-12}
            solids = {k: treated[k] for k in ("SiO2", "CaCO3", "MgOH2")}
            liquid = {k: v for k, v in treated.items() if k not in solids}
            cake_liquid = total(solids) * (1 - CAKE_SOLIDS) / CAKE_SOLIDS
            entrained = scale(liquid, cake_liquid / total(liquid))
            sludge = add(solids, entrained)
            clear = add(liquid, scale(entrained, -1))
            # ion exchange: brine passes; regeneration HCl + NaOH -> NaCl + H2O in the effluent
            hcl_ix = {"HCl": kg("HCl", n_ix), "H2O": kg("HCl", n_ix) * (1 - W_HCL_ACID) / W_HCL_ACID}
            rinse = {"H2O": IX_RINSE * CL2_PRODUCT}
            regen = add(hcl_ix, caustic_ix, rinse, {"HCl": -kg("HCl", n_ix), "NaOH": -naoh_ix,
                                                    "NaCl": kg("NaCl", n_ix), "H2O": kg("H2O", n_ix)})
            regen = {k: v for k, v in regen.items() if abs(v) > 1e-12}
            # feed acidification: Na2CO3 + 2 HCl -> 2 NaCl + H2O + CO2; NaOH + HCl -> NaCl + H2O
            n_co3 = clear["Na2CO3"] / MW["Na2CO3"] * 1000
            n_oh = clear["NaOH"] / MW["NaOH"] * 1000
            n_hcl_f = 2 * n_co3 + n_oh
            hcl_feed = {"HCl": kg("HCl", n_hcl_f),
                        "H2O": kg("HCl", n_hcl_f) * (1 - W_HCL_ACID) / W_HCL_ACID}
            vent = {"CO2": kg("CO2", n_co3)}
            fed = add(clear, hcl_feed, {"Na2CO3": -clear["Na2CO3"], "NaOH": -clear["NaOH"],
                                        "HCl": -hcl_feed["HCl"], "CO2": 0.0,
                                        "NaCl": kg("NaCl", 2 * n_co3 + n_oh),
                                        "H2O": kg("H2O", n_co3 + n_oh)})
            fed = {k: v for k, v in fed.items() if abs(v) > 1e-12}
            res = (fed["NaCl"] - c["feed"]["NaCl"], fed["H2O"] - c["feed"]["H2O"],
                   fed["Na2SO4"] - c["feed"]["Na2SO4"])
            if not final:
                return res
            return dict(purge=purge, ret=ret, salt=salt_s, water={"H2O": water}, raw=raw,
                        carb=carb, caustic_r101=caustic_r101, caustic_ix=caustic_ix,
                        treated=treated, sludge=sludge, clear=clear, hcl_ix=hcl_ix, rinse=rinse,
                        regen=regen, hcl_feed=hcl_feed, vent=vent, fed=fed, naoh_int=naoh_int,
                        evap_water=evap_water, h2_cond={"H2O": h2_cond})

        x = [salt, water, purge_frac]
        for _ in range(30):  # Newton on salt, make-up water and purge fraction
            r = loop(*x)
            if max(abs(v) for v in r) < 1e-10:
                break
            jac = []
            for i in range(3):
                dx = list(x)
                h = 1e-6 * max(abs(x[i]), 1e-3)
                dx[i] += h
                jac.append([(a - b) / h for a, b in zip(loop(*dx), r)])
            # solve J^T columns: jac[i][j] = d r_j / d x_i
            a = [[jac[i][j] for i in range(3)] for j in range(3)]
            step = gauss(a, [-v for v in r])
            x = [xi_ + s for xi_, s in zip(x, step)]
        salt, water, purge_frac = x
        b = loop(*x, final=True)
        product_cl2 = cooled["Cl2"]
        new_xi = xi + (CL2_PRODUCT - product_cl2) / MW["Cl2"] * 1000
        if abs(new_xi - xi) < 1e-10:
            xi = new_xi
            break
        xi = new_xi
    return xi, c, b, dict(wet=wet, gas40=gas40, cond1=cond1, cond2=cond2, cooled=cooled,
                          condensate=condensate, hcl_dcl=hcl_dcl, stripped=stripped, strip=strip,
                          sulfite=sulfite, naoh_dcl=naoh_dcl, dechl=dechl, h2_cooled=h2_cooled,
                          n_res=n_res, brine_in=brine_in)


def gauss(a, b):
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(m[r][i]))
        m[i], m[p] = m[p], m[i]
        for r in range(i + 1, n):
            f = m[r][i] / m[i][i]
            for k in range(i, n + 1):
                m[r][k] -= f * m[i][k]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (m[i][n] - sum(m[i][k] * x[k] for k in range(i + 1, n))) / m[i][i]
    return x


def main():
    xi, c, b, g = solve()
    t_h = CL2_PRODUCT * 3.6  # t Cl2 per hour
    # drying: water absorbed by the acid
    water_abs = g["cooled"]["H2O"]
    acid = water_abs * W_H2SO4_SPENT / (W_H2SO4_FEED - W_H2SO4_SPENT)  # kg/s H2SO4 (100 %)
    acid_feed = {"H2SO4": acid, "H2O": acid * (1 - W_H2SO4_FEED) / W_H2SO4_FEED}
    spent = add(acid_feed, {"H2O": water_abs})
    dry = {k: v for k, v in g["cooled"].items() if k != "H2O"}
    # caustic
    caustic = c["caustic"]
    naoh_int = b["naoh_int"]
    f_int = naoh_int / caustic["NaOH"]
    to_evap = scale(caustic, 1 - f_int)
    product50 = {"NaOH": to_evap["NaOH"], "H2O": to_evap["NaOH"] * (1 - W_NAOH_PRODUCT) / W_NAOH_PRODUCT}
    proc_cond = {"H2O": to_evap["H2O"] - product50["H2O"]}
    steam_kg = proc_cond["H2O"] / EVAP_ECONOMY
    # energy
    p_dc = c["current"] * VOLTAGE / 1000  # kW
    p_ac = p_dc / RECTIFIER_EFF
    dh_main, dh_side = 445790.0, 571660.0  # J/mol per extent (process/reactions.yaml)
    q_cell = p_dc - (xi * dh_main + c["xs"] * dh_side) / 1000
    q_brine = total(c["feed"]) * CP_BRINE * (T_CELL - T_FEED_BRINE)
    q_dmw = c["dmw"]["H2O"] * CP_WATER * (T_CELL - T_DMW)
    q_evap = (c["cl2_gas"]["H2O"] + c["h2_gas"]["H2O"]) * HFG_90C
    q_catholyte = q_cell - q_brine - q_dmw - q_evap
    q_e201 = total(c["feed"]) * CP_BRINE * (T_FEED_BRINE - T_SAT_BRINE)
    q_e501_cw = sensible(g["wet"], 363.15, 313.15) + g["cond1"] * HFG_90C
    q_e501_chw = sensible(g["gas40"], 313.15, 293.15) + g["cond2"] * 2430.0
    q_e601 = sensible(c["h2_gas"], 363.15, 308.15) + (c["h2_gas"]["H2O"] - b["h2_cond"]["H2O"]) * HFG_90C
    # chlorine compressor: two intercooled stages, eta 0.75, k from cp
    n_dry = sum(mol(dry).values())
    cp = sum(n * CP_GAS[k] for k, n in mol(dry).items()) / n_dry
    k_exp = 8.314 / cp
    r_stage = math.sqrt(P_CL2_PRODUCT / P_CL2_DRY)
    eta = 0.75
    w1 = n_dry * cp * 298.15 * (r_stage ** k_exp - 1) / eta / 1000
    w2 = n_dry * cp * 313.15 * (r_stage ** k_exp - 1) / eta / 1000
    t_dis = 313.15 * (1 + (r_stage ** k_exp - 1) / eta)
    w_k503 = w1 + w2
    q_e504 = w_k503 - n_dry * cp * (313.15 - 298.15) / 1000  # back to 40 degC
    # hydrogen blower
    n_h2 = sum(mol(g["h2_cooled"]).values())
    cph = sum(n * CP_GAS[k] for k, n in mol(g["h2_cooled"]).items()) / n_h2
    rk = (P_H2_PRODUCT / P_H2_COOLED) ** (8.314 / cph) - 1
    w_k602 = n_h2 * cph * 308.15 * rk / 0.70 / 1000
    t_h2 = 308.15 * (1 + rk / 0.70)
    w_aux = AUX_TOTAL * t_h - w_k503 - w_k602
    q_ev_steam = steam_kg * HFG_STEAM
    # evaporator energy closure on constant heat capacities (reference 298.15 K); the heat of
    # dilution of NaOH is not included: the condenser takes the rest
    h_in = total(to_evap) * CP_CAUSTIC32 * (358.15 - 298.15)
    h_out = total(product50) * CP_CAUSTIC50 * (413.15 - 298.15) + proc_cond["H2O"] * CP_WATER * 25
    q_ev_cw = q_ev_steam + h_in - h_out
    q_e702 = total(product50) * CP_CAUSTIC50 * (413.15 - 323.15)
    q_loss = p_ac - p_dc
    n_cells = math.ceil(c["current"] / (J_MAX * AREA))
    i_cell = c["current"] / n_cells

    streams = [
        ("S1", "Rock salt", "SALT.out", "D101.salt", b["salt"], 288.15, 101.325),
        ("S2", "Make-up process water", "WATER.out", "D101.water", b["water"], 288.15, 300),
        ("S3", "Return brine to saturation", "SP403.ret", "D101.ret", b["ret"], 353.15, 250),
        ("S4", "Process condensate from caustic evaporation", "EV701.cond", "D101.cond", proc_cond, 323.15, 250),
        ("S5", "Hydrogen cooler condensate", "E601.cond", "D101.h2cond", b["h2_cond"], 308.15, 250),
        ("S6", "Raw saturated brine", "D101.out", "R101.in", b["raw"], T_SAT_BRINE, 250),
        ("S7", "Soda ash", "NA2CO3.out", "R101.carb", b["carb"], 298.15, 101.325),
        ("S8", "Caustic for magnesium precipitation", "SP303.r101", "R101.naoh", b["caustic_r101"], 358.15, 400),
        ("S9", "Treated brine slurry", "R101.out", "S101.in", b["treated"], T_SAT_BRINE, 250),
        ("S10", "Brine filter cake", "S101.sludge", "SLUDGE.in", b["sludge"], 318.15, 101.325),
        ("S11", "Clarified brine", "S101.clear", "X201.in", b["clear"], T_SAT_BRINE, 400),
        ("S12", "Polished brine", "X201.out", "R202.in", b["clear"], T_SAT_BRINE, 350),
        ("S13", "Hydrochloric acid for resin regeneration", "HCL.ix", "X201.hcl", b["hcl_ix"], 298.15, 300),
        ("S14", "Caustic for resin regeneration", "SP303.x201", "X201.naoh", b["caustic_ix"], 358.15, 400),
        ("S15", "Demineralised rinse water", "DMW.ix", "X201.rinse", b["rinse"], 298.15, 400),
        ("S16", "Resin regeneration effluent", "X201.regen", "WW.ix", b["regen"], 303.15, 150),
        ("S17", "Hydrochloric acid for feed brine", "HCL.feed", "R202.hcl", b["hcl_feed"], 298.15, 300),
        ("S18", "Acidification vent (CO2)", "R202.vent", "VENT.in", b["vent"], T_SAT_BRINE, 101.325),
        ("S19", "Acidified brine", "R202.out", "E201.in", b["fed"], T_SAT_BRINE, 350),
        ("S20", "Feed brine to cells", "E201.out", "EL301.brine", c["feed"], T_FEED_BRINE, 300),
        ("S21", "Demineralised water to catholyte", "DMW.cath", "EL301.dmw", c["dmw"], T_DMW, 400),
        ("S22", "Depleted brine (anolyte)", "EL301.anolyte", "C401.anolyte", c["anolyte"], T_CELL, P_ANODE),
        ("S23", "Wet cell chlorine", "EL301.cl2", "M501.cell", c["cl2_gas"], T_CELL, P_ANODE),
        ("S24", "Wet cell hydrogen", "EL301.h2", "E601.in", c["h2_gas"], T_CELL, P_CATHODE),
        ("S25", "Catholyte 32 wt-% NaOH", "EL301.caustic", "E302.in", caustic, T_CELL, 400),
        ("S26", "Cooled 32 wt-% caustic", "E302.out", "SP303.in", caustic, 358.15, 400),
        ("S27", "32 wt-% caustic to evaporation", "SP303.evap", "EV701.in", to_evap, 358.15, 400),
        ("S28", "Caustic for dechlorination", "SP303.r402", "R402.naoh", g["naoh_dcl"], 358.15, 400),
        ("S29", "Hydrochloric acid for dechlorination", "HCL.dcl", "C401.hcl", g["hcl_dcl"], 298.15, 300),
        ("S30", "Recovered chlorine from dechlorination", "C401.gas", "M501.strip", g["strip"], 313.15, P_ANODE),
        ("S31", "Stripped brine", "C401.out", "R402.in", g["stripped"], 356.15, 250),
        ("S32", "Sodium sulfite", "NA2SO3.out", "R402.sulfite", g["sulfite"], 298.15, 101.325),
        ("S33", "Dechlorinated brine", "R402.out", "SP403.in", g["dechl"], 353.15, 300),
        ("S34", "Brine purge", "SP403.purge", "WW.purge", b["purge"], 353.15, 150),
        ("S35", "Wet chlorine to coolers", "M501.out", "E501.in", g["wet"], T_CELL, P_ANODE),
        ("S36", "Chlorine water condensate", "E501.cond", "C401.cond", g["condensate"], 303.15, 250),
        ("S37", "Cooled wet chlorine", "E501.gas", "C502.in", g["cooled"], 293.15, P_CL2_COOLED),
        ("S38", "Sulfuric acid 98 wt-%", "H2SO4.out", "C502.acid", acid_feed, 298.15, 300),
        ("S39", "Spent sulfuric acid", "C502.spent", "SPENT.in", spent, 303.15, 150),
        ("S40", "Dry chlorine", "C502.gas", "K503.in", dry, 298.15, P_CL2_DRY),
        ("S41", "Compressed chlorine", "K503.out", "E504.in", dry, round(t_dis, 2), P_CL2_PRODUCT + 10),
        ("S42", "Dry chlorine gas product", "E504.out", "CL2.in", dry, 313.15, P_CL2_PRODUCT),
        ("S43", "Cooled hydrogen", "E601.gas", "K602.in", g["h2_cooled"], 308.15, P_H2_COOLED),
        ("S44", "Hydrogen product", "K602.out", "H2.in", g["h2_cooled"], round(t_h2, 2), P_H2_PRODUCT),
        ("S45", "50 wt-% caustic (hot)", "EV701.out", "E702.in", product50, 413.15, 300),
        ("S46", "50 wt-% caustic soda product", "E702.out", "NAOH.in", product50, 323.15, 250),
    ]
    print("# material streams")
    for sid, title, frm, to, comp, t, p in streams:
        comp = {k: v for k, v in comp.items() if v > 1e-12}
        m = total(comp)
        fr = ", ".join(f"{k}: {v / m:.7g}" for k, v in comp.items())
        print(f"  - {{id: {sid}, title: {title}, from: {frm}, to: {to}, state: {{design: "
              f"{{temperature: {t}, pressure: {p}, flow: {m * 3600:.2f}, composition: {{{fr}}}}}}}}}")
    energy = [
        ("Q1", "Rectifier AC supply", "POWER.rect", "T301.ac", p_ac),
        ("Q2", "DC power to the cells", "T301.dc", "EL301.dc", p_dc),
        ("Q3", "Transformer and rectifier losses", "T301.loss", "CW.t301", q_loss),
        ("Q4", "Catholyte cooler duty", "E302.cw", "CW.e302", q_catholyte),
        ("Q5", "Other auxiliaries (pumps, agitators, fans, vacuum, chiller)", "POWER.aux", "D101.aux", w_aux),
        ("Q6", "Feed brine heater duty", "MPS.e201", "E201.steam", q_e201),
        ("Q7", "Chlorine cooler duty (cooling water)", "E501.cw", "CW.e501", q_e501_cw),
        ("Q8", "Chlorine cooler duty (chilled water)", "E501.chw", "CHW.e501", q_e501_chw),
        ("Q9", "Chlorine compressor power", "POWER.k503", "K503.power", w_k503),
        ("Q10", "Chlorine inter- and aftercooler duty", "E504.cw", "CW.e504", q_e504),
        ("Q11", "Hydrogen cooler duty", "E601.cw", "CW.e601", q_e601),
        ("Q12", "Hydrogen blower power", "POWER.k602", "K602.power", w_k602),
        ("Q13", "Caustic evaporator steam", "MPS.ev701", "EV701.steam", q_ev_steam),
        ("Q14", "Caustic evaporator condenser duty", "EV701.cw", "CW.ev701", q_ev_cw),
        ("Q15", "Caustic product cooler duty", "E702.cw", "CW.e702", q_e702),
    ]
    print("# energy streams, kW")
    for sid, title, frm, to, q in energy:
        print(f"  - {{id: {sid}, title: {title}, kind: energy, from: {frm}, to: {to}, duty: {q:.1f}}}")
    print("# key figures")
    print(f"xi {xi:.5f} mol/s, Cl2 formed {kg('Cl2', xi) * 3600:.2f} kg/h, side extent {c['xs']:.5f} mol/s")
    print(f"current {c['current']:.1f} A total, {n_cells} cells x {i_cell:.1f} A, "
          f"j = {i_cell / AREA:.1f} A/m2")
    print(f"DC {p_dc:.1f} kW = {p_dc / t_h:.1f} kWh/t; AC {p_ac:.1f} kW = {p_ac / t_h:.1f} kWh/t")
    print(f"Q_cell {q_cell:.1f} kW; brine {q_brine:.1f}, dmw {q_dmw:.1f}, evaporation {q_evap:.1f}, "
          f"catholyte cooler {q_catholyte:.1f}")
    print(f"K503 {w_k503:.1f} kW (discharge {t_dis:.1f} K), K602 {w_k602:.1f} kW, other aux {w_aux:.1f} kW")
    print(f"evap steam {steam_kg * 3.6:.3f} t/h = {steam_kg / to_evap['NaOH']:.3f} t/t NaOH; "
          f"brine heater steam {q_e201 / HFG_STEAM * 3.6:.3f} t/h = {q_e201 / HFG_STEAM / CL2_PRODUCT:.3f} t/t Cl2")
    per_t = lambda x: x / CL2_PRODUCT  # noqa: E731 kg/kg Cl2 == t/t
    print(f"salt {per_t(total(b['salt'])):.4f} t/t; NaCl {per_t(b['salt']['NaCl']):.4f}")
    print(f"NaOH product {per_t(product50['NaOH']):.4f} t/t (formed {per_t(caustic['NaOH']):.4f}, internal {per_t(naoh_int):.4f})")
    print(f"H2 product {per_t(g['h2_cooled']['H2']) * 1000:.2f} kg/t; O2 in Cl2 {mol(dry)['O2'] / n_dry * 100:.2f} vol-%")
    hcl = b["hcl_ix"]["HCl"] + b["hcl_feed"]["HCl"] + g["hcl_dcl"]["HCl"]
    print(f"HCl {per_t(hcl) * 1000:.2f} kg/t; Na2CO3 {per_t(b['carb']['Na2CO3']) * 1000:.2f}; "
          f"Na2SO3 {per_t(g['sulfite']['Na2SO3']) * 1000:.3f}; NaOH internal {per_t(naoh_int) * 1000:.2f}; "
          f"H2SO4 {per_t(acid) * 1000:.2f} kg/t")
    print(f"purge fraction {b['purge'] and total(b['purge']) / total(g['dechl']):.5f}, purge {per_t(total(b['purge'])):.4f} t/t, "
          f"sludge {per_t(total(b['sludge'])) * 1000:.2f} kg/t, CO2 {per_t(b['vent']['CO2']) * 1000:.3f} kg/t")
    print(f"water make-up {per_t(b['water']['H2O']):.4f} t/t, DMW {per_t(c['dmw']['H2O'] + b['rinse']['H2O']):.4f} t/t, "
          f"Cl2 cond {per_t(g['condensate']['H2O']) * 1000:.1f} kg/t, H2 cond {per_t(b['h2_cond']['H2O']) * 1000:.1f} kg/t")
    print(f"feed brine {total(c['feed']) * 3.6:.2f} t/h, anolyte {total(c['anolyte']) * 3.6:.2f} t/h, "
          f"NaCl in anolyte {c['anolyte']['NaCl'] / total(c['anolyte']):.4f}")
    # overall mass balance
    ins = [b["salt"], b["water"], b["carb"], b["hcl_ix"], b["rinse"], b["hcl_feed"], c["dmw"],
           g["hcl_dcl"], g["sulfite"], acid_feed]
    outs = [b["sludge"], b["regen"], b["vent"], b["purge"], spent, dry, g["h2_cooled"], product50]
    print(f"overall in {sum(map(total, ins)) * 3600:.3f} kg/h, out {sum(map(total, outs)) * 3600:.3f} kg/h")


if __name__ == "__main__":
    main()
