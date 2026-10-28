"""Concept heat and material balance of ethylene-glycol-1 (EO by direct O2 oxidation, glycols
by thermal hydration). Independent sequential balance; every parameter is a design choice
marked in DESIGN.md (D-004 to D-008) with its source or as ASSUMED. Plain Python, no
dependencies:

    python3 scripts/eg_balance.py [OUT_DIR]

writes OUT_DIR/streams.yaml (the stream entries of process/flowsheet.yaml), OUT_DIR/summary.txt
(per-kg figures for the LCI check) and prints the summary. OUT_DIR defaults to build/.
The flowsheet copies these values with provenance `assumed` (source: this script); cheme checks
the balances (cheme validate, cheme process streams) and the reactors (cheme process propagate
--check).
"""
import os
import sys

# ---------------------------------------------------------------- components (kg/kmol, IUPAC 2021)
MW = {
    "C2H4": 28.054, "O2": 31.998, "CH4": 16.043, "CO2": 44.009, "H2O": 18.015, "AR": 39.948,
    "C2H6": 30.070, "EO": 44.053, "MEG": 62.068, "DEG": 106.120, "TEG": 150.173, "TTEG": 194.226,
}
COMP = list(MW)

# ---------------------------------------------------------------- design parameters (DESIGN.md)
MEG_PRODUCT_KG_H = 50000.0      # D-002 ASSUMED normalisation basis (400 kt/a at 8000 h/a)
X_C2H4 = 0.09                   # D-004 per-pass ethylene conversion, BREF LVOC 7.2.1.1.1: 8-10 %
S_EO = 0.85                     # D-004 molar selectivity to EO, BREF LVOC 7.2.1.1.1: 75-90 %
Y_IN = {"C2H4": 0.30, "O2": 0.080, "CO2": 0.010}   # D-004 ASSUMED reactor inlet mol fractions
PURGE_FRAC = 0.0015             # D-004 inerts purge, fraction of recycle gas, BREF 7.2.2.1: 0.1-0.2 %
CO2_REMOVAL_EFF = 0.90          # D-004 ASSUMED CO2 removed from the gas sent to the carbonate absorber
Y_H2O_LOOP = 0.0028             # D-004 water in the absorber off-gas: saturation at 308 K, 2000 kPa
O2_FEED = {"O2": 0.995, "AR": 0.005}       # D-003 asu-1 GOX 99.5 mol% O2, rest counted as Ar
C2H4_FEED = {"C2H4": 0.9995, "C2H6": 0.0005}   # D-003 ASSUMED polymer-grade ethylene
VENT_CH4_KG_PER_T_EO = 0.5      # D-006 ASSUMED, inside BREF Table 7.4 (0.03-1.45 kg/t EO)
VENT_C2H4_KG_PER_T_EO = 0.5     # D-006 ASSUMED, NMVOC inside BREF Table 7.4 (0.07-1.35 kg/t EO)
Y_H2O_VENT = 0.064              # D-004 CO2 vent saturated at 313 K, 120 kPa(a)
DISSOLVED = {"CO2": 0.03, "C2H4": 0.015, "CH4": 0.008}   # D-004 ASSUMED kmol/kmol EO, stripped and recycled
W_EO_RICH = 0.03                # D-004 ASSUMED EO mass fraction of the rich absorbent
WATER_EO = 20.0                 # D-005 ASSUMED water:EO mol/mol at the glycol reactor inlet
K_RATIO = 2.0                   # D-005 ASSUMED rate of EO with a glycol relative to water (per mol)
W_MEG_RECYCLE = 0.001           # D-005 ASSUMED MEG mass fraction of the recycle water (carry-over)
BLEED_FRAC = 0.005              # D-005 ASSUMED aldehyde bleed, fraction of the recycle water
W_H2O_EVAP_OUT = 0.15           # D-005 ASSUMED water mass fraction of the evaporator concentrate
MEG_SPEC = {"H2O": 0.0004, "DEG": 0.0006}  # D-002 ASSUMED MEG product impurities (mass fractions)
W_MEG_C601_BOTTOM = 0.002       # D-005 ASSUMED MEG mass fraction of the MEG column bottoms
DEG_LOSS = 0.0005               # D-005 ASSUMED share of DEG fed to C-602 lost to its bottoms
W_TEG_IN_DEG = 0.002            # D-005 ASSUMED TEG mass fraction of the DEG product
TEG_LOSS = 0.05                 # D-005 ASSUMED share of TEG fed to C-603 lost to the heavies
W_TTEG_IN_TEG = 0.005           # D-005 ASSUMED heavies mass fraction of the TEG product

# energy (D-008), all ASSUMED or derived
DH_EO = 105.0e3                 # kJ/kmol released, C2H4 + 1/2 O2 -> EO (BREF 7.2.1.1.1)
DH_COMB = 1323.0e3              # kJ/kmol C2H4 released, total combustion (BREF 7.2.1.1.1)
DH_HYD = 95.0e3                 # kJ/kmol EO released per glycol step, ASSUMED (D-007)
CP_GAS = 40.0                   # kJ/(kmol K) loop gas, ASSUMED
DT_E101 = 60.0                  # K, trim cooler of the reactor effluent 373 -> 313 K, ASSUMED
DT_LEAN_COOLER = 25.0           # K, lean absorbent 333 -> 308 K, ASSUMED
DT_LEAN_RICH = 15.0             # K, approach of the lean/rich exchanger, ASSUMED
DH_EO_DESORB = 30.0e3           # kJ/kmol EO, desorption incl. overhead reflux, ASSUMED
STRIPPER_EXTRA = 1.25           # factor for stripping steam on the EO stripper, ASSUMED
CO2_REGEN_GJ_PER_T = 3.0        # hot potassium carbonate regeneration heat, ASSUMED
EVAP_ECONOMY = 3.2              # kg water per kg steam, 4-effect train, ASSUMED
LAMBDA_W = 2200.0               # kJ/kg water evaporated / condensed, ASSUMED mean
LAMBDA_STEAM = 1802.0           # kJ/kg, condensing MP steam at 2800 kPa(a) (steam tables)
R_DRY, R_MEG, R_DEG, R_TEG = 0.3, 1.2, 2.0, 2.0   # reflux ratios, ASSUMED
LAMBDA_KJ_KMOL = {"MEG": 52.0e3, "DEG": 57.0e3, "TEG": 61.0e3}   # ASSUMED (D-008)
ETA_COMP = 0.75                 # recycle compressor isentropic efficiency, ASSUMED
P_LOOP_LOW, P_LOOP_HIGH = 1950.0, 2200.0   # kPa(a), recycle compressor suction / discharge
KAPPA = 1.25                    # cp/cv of the loop gas, ASSUMED
ETA_PUMP = 0.7
P_HYD = 3000.0                  # kPa(a) glycol reactor (BREF 7.2.2.5: 10-40 barg)
AUX_KWH_PER_T_MEG = 20.0        # ASSUMED lump: carbonate pumps, vacuum pumps, fans, product pumps
H_STEAM_RAISED = 2802.0 - 440.0  # kJ/kg, saturated 2800 kPa(a) from BFW at 378 K (steam tables)


def zero():
    return {c: 0.0 for c in COMP}


def add(*ss):
    out = zero()
    for s in ss:
        for c, v in s.items():
            out[c] += v
    return out


def scale(s, f):
    return {c: v * f for c, v in s.items()}


def total(s):
    return sum(s.values())


def mass(s):
    return {c: v * MW[c] for c, v in s.items()}


def hydration(eo, water, meg0):
    """Consecutive EO + water/glycol reactions to full EO conversion (RK4 in the reaction
    progress tau = integral k*[EO] dt). Returns kmol of MEG, DEG, TEG, TTEG and water left."""
    a = K_RATIO
    y = [eo, water, meg0, 0.0, 0.0, 0.0]

    def f(y):
        e, w, g1, g2, g3, g4 = y
        return [-(w + a * (g1 + g2 + g3)), -w, w - a * g1, a * (g1 - g2), a * (g2 - g3), a * g3]

    h = 1e-4
    while y[0] > 1e-9 * eo:
        k1 = f(y)
        k2 = f([y[i] + h / 2 * k1[i] for i in range(6)])
        k3 = f([y[i] + h / 2 * k2[i] for i in range(6)])
        k4 = f([y[i] + h * k3[i] for i in range(6)])
        yn = [y[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(6)]
        if yn[0] < 0:
            h /= 2
            continue
        y = yn
    # close the last trace of EO onto MEG
    return y


def solve(eo_target):
    """Balance for eo_target kmol/h of EO sent to the glycol reactor."""
    c2h4_react = eo_target / S_EO
    c2h4_comb = c2h4_react - eo_target
    F_c2h4 = c2h4_react / X_C2H4
    G = F_c2h4 / Y_IN["C2H4"]
    # initial guess of the minor loop components
    F = zero()
    F["C2H4"], F["O2"], F["CO2"] = F_c2h4, Y_IN["O2"] * G, Y_IN["CO2"] * G
    F["H2O"], F["AR"], F["C2H6"] = Y_H2O_LOOP * G, 0.05 * G, 0.005 * G
    F["CH4"] = G - (F["C2H4"] + F["O2"] + F["CO2"] + F["H2O"] + F["AR"] + F["C2H6"])
    for _ in range(200000):   # the 0.15 % purge makes the inerts converge slowly
        R = dict(F)
        R["C2H4"] -= c2h4_react
        R["O2"] -= 0.5 * eo_target + 3.0 * c2h4_comb
        R["EO"] += eo_target
        R["CO2"] += 2.0 * c2h4_comb
        R["H2O"] += 2.0 * c2h4_comb
        dis = {c: v * eo_target for c, v in DISSOLVED.items()}
        # absorber off-gas: no EO, water to saturation, dissolved lights to the rich absorbent
        A = dict(R)
        A["EO"] = 0.0
        for c, v in dis.items():
            A[c] -= v
        dry = total(A) - A["H2O"]
        A["H2O"] = Y_H2O_LOOP / (1 - Y_H2O_LOOP) * dry
        lights = zero()
        for c, v in dis.items():
            lights[c] = v
        K = add(A, lights)                     # compressor feed (lights recycled)
        purge = scale(K, PURGE_FRAC)
        rest = scale(K, 1 - PURGE_FRAC)
        # CO2 removal: slip-stream fraction f so that the reactor inlet holds Y_IN CO2
        vent = zero()
        vent["CH4"] = VENT_CH4_KG_PER_T_EO * eo_target * MW["EO"] / 1000 / MW["CH4"]
        vent["C2H4"] = VENT_C2H4_KG_PER_T_EO * eo_target * MW["EO"] / 1000 / MW["C2H4"]
        co2_removed = rest["CO2"] - Y_IN["CO2"] * G
        f_slip = co2_removed / (CO2_REMOVAL_EFF * rest["CO2"])
        vent["CO2"] = co2_removed
        vent["H2O"] = Y_H2O_VENT / (1 - Y_H2O_VENT) * (vent["CO2"] + vent["CH4"] + vent["C2H4"])
        slip = scale(rest, f_slip)
        bypass = scale(rest, 1 - f_slip)
        treated = {c: slip[c] - vent[c] for c in COMP}
        recycle = add(treated, bypass)
        # fresh feeds
        o2_fresh = (F["O2"] - recycle["O2"]) / O2_FEED["O2"]
        eth_fresh = (F["C2H4"] - recycle["C2H4"]) / C2H4_FEED["C2H4"]
        newF = add(recycle, scale(O2_FEED, o2_fresh), scale(C2H4_FEED, eth_fresh))
        # methane make-up keeps the inlet total at G (ballast)
        ch4_fresh = G - total(newF)
        newF["CH4"] += ch4_fresh
        err = max(abs(newF[c] - F[c]) for c in COMP)
        F = newF
        if err < 1e-9 * G:
            break
    feeds = {
        "ETH": scale(C2H4_FEED, eth_fresh), "OXY": scale(O2_FEED, o2_fresh),
        "MET": {"CH4": ch4_fresh},
    }
    loop = dict(F=F, R=R, A=A, K=K, purge=purge, rest=rest, slip=slip, bypass=bypass,
                treated=treated, recycle=recycle, vent=vent, lights=lights, f_slip=f_slip,
                c2h4_comb=c2h4_comb, G=G)
    # EO recovery: lean absorbent L (water), rich = L + EO + condensed water + dissolved lights
    cond_water = R["H2O"] - A["H2O"]
    lean_kg = eo_target * MW["EO"] / W_EO_RICH - eo_target * MW["EO"] - cond_water * MW["H2O"]
    lean = zero()
    lean["H2O"] = lean_kg / MW["H2O"]
    rich = add(lean, {"EO": eo_target, "H2O": cond_water}, lights)
    overhead = {c: rich[c] - lean[c] for c in COMP}     # EO, condensed water, lights
    eo_water = dict(overhead)
    for c in DISSOLVED:
        eo_water[c] = 0.0
    loop.update(lean=lean, rich=rich, overhead=overhead, eo_water=eo_water, cond_water=cond_water)
    return feeds, loop


def glycols(eo_water):
    """Glycol reaction, evaporation, drying and purification for the EO-water feed. The
    recycle water and the make-up are solved together (water:EO at the reactor inlet)."""
    eo = eo_water["EO"]
    w_in = WATER_EO * eo
    # recycle water composition: water with W_MEG_RECYCLE MEG by mass
    meg_per_kg_rec = W_MEG_RECYCLE / MW["MEG"]
    h2o_per_kg_rec = (1 - W_MEG_RECYCLE) / MW["H2O"]
    # iterate: reactor -> evaporation -> drying -> recycle (bleed) -> make-up
    rec_kg = (w_in - eo_water["H2O"]) * MW["H2O"]
    for _ in range(200):
        rec = zero()
        rec["H2O"], rec["MEG"] = rec_kg * h2o_per_kg_rec, rec_kg * meg_per_kg_rec
        makeup_h2o = w_in - eo_water["H2O"] - rec["H2O"]
        feed = add(eo_water, rec, {"H2O": makeup_h2o})
        e, w, g1, g2, g3, g4 = hydration(feed["EO"], feed["H2O"], feed["MEG"])
        prod = zero()
        prod.update(H2O=w, MEG=g1, DEG=g2, TEG=g3, TTEG=g4)
        # products: MEG column top holds all water left after drying (MEG spec)
        # downstream splits
        # C601 bottoms: DEG, TEG, TTEG plus MEG at W_MEG_C601_BOTTOM; top: rest
        # top DEG from spec, so solve top mass
        meg_avail_kg = g1 * MW["MEG"]  # minus carry-over below (solved with the loop)
        # water to the products = MEG_SPEC water of the MEG top
        # evaporator and dryer remove the rest; MEG carry-over to the recycle comes from EV501
        meg_carry_kg = (rec_kg / (1 - BLEED_FRAC)) * W_MEG_RECYCLE
        meg_net_kg = meg_avail_kg - meg_carry_kg
        bot_heavy_kg = (g2 * MW["DEG"] + g3 * MW["TEG"] + g4 * MW["TTEG"])
        # top mass T: MEG(T) = T*(1 - wH2O - wDEG); DEG top = T*wDEG
        # bottoms MEG = W_MEG_C601_BOTTOM * bottoms mass
        # meg_net = MEG_top + MEG_bot; bottoms mass = MEG_bot + bot_heavy - DEG_top
        wm = 1 - MEG_SPEC["H2O"] - MEG_SPEC["DEG"]
        # unknown T: MEG_bot = meg_net - wm*T; B = MEG_bot + bot_heavy - wDEG*T
        # MEG_bot = wb*B -> meg_net - wm*T = wb*(meg_net - wm*T + bot_heavy - wd*T)
        wb, wd = W_MEG_C601_BOTTOM, MEG_SPEC["DEG"]
        T = (meg_net_kg * (1 - wb) - wb * bot_heavy_kg) / (wm * (1 - wb) - wb * wd)
        water_crude_kg = MEG_SPEC["H2O"] * T
        # water removed in EV501 + C501 and recycled (before bleed)
        water_removed = w * MW["H2O"] - water_crude_kg
        new_rec_total = water_removed + meg_carry_kg     # condensate (H2O + carried MEG)
        new_rec_kg = new_rec_total * (1 - BLEED_FRAC)
        if abs(new_rec_kg - rec_kg) < 1e-6:
            rec_kg = new_rec_kg
            break
        rec_kg = new_rec_kg
    out = dict(feed=feed, prod=prod, makeup=makeup_h2o, rec=rec, rec_kg=rec_kg,
               meg_carry_kg=meg_carry_kg, T=T, water_crude_kg=water_crude_kg)
    cond_total_kg = water_removed + meg_carry_kg
    bleed = scale({"H2O": cond_total_kg * (1 - W_MEG_RECYCLE) / MW["H2O"],
                   "MEG": meg_carry_kg / MW["MEG"]}, BLEED_FRAC)
    # EV501: concentrate at W_H2O_EVAP_OUT water
    glyc_kg = prod["MEG"] * MW["MEG"] - meg_carry_kg + bot_heavy_kg
    evap_conc_water_kg = W_H2O_EVAP_OUT / (1 - W_H2O_EVAP_OUT) * glyc_kg
    ev_vap = {"H2O": (w * MW["H2O"] - evap_conc_water_kg) / MW["H2O"], "MEG": meg_carry_kg / MW["MEG"]}
    ev_conc = {c: prod[c] - ev_vap.get(c, 0.0) for c in COMP}
    dry_ovh = {"H2O": (evap_conc_water_kg - water_crude_kg) / MW["H2O"]}
    crude = dict(ev_conc)
    crude["H2O"] = water_crude_kg / MW["H2O"]
    cond_all = add(ev_vap, dry_ovh)
    rec_stream = scale(cond_all, 1 - BLEED_FRAC)
    bleed = scale(cond_all, BLEED_FRAC)
    # C601
    meg_top = zero()
    meg_top["H2O"], meg_top["DEG"] = crude["H2O"], MEG_SPEC["DEG"] * T / MW["DEG"]
    meg_top["MEG"] = wm * T / MW["MEG"]
    c601_bot = {c: crude[c] - meg_top[c] for c in COMP}
    # C602: top all MEG, DEG less loss, TEG at spec
    deg_top = zero()
    deg_top["MEG"] = c601_bot["MEG"]
    deg_top["DEG"] = c601_bot["DEG"] * (1 - DEG_LOSS)
    m_no_teg = deg_top["MEG"] * MW["MEG"] + deg_top["DEG"] * MW["DEG"]
    deg_top["TEG"] = W_TEG_IN_DEG / (1 - W_TEG_IN_DEG) * m_no_teg / MW["TEG"]
    c602_bot = {c: c601_bot[c] - deg_top[c] for c in COMP}
    # C603: top all DEG, TEG less loss, TTEG at spec
    teg_top = zero()
    teg_top["DEG"] = c602_bot["DEG"]
    teg_top["TEG"] = c602_bot["TEG"] * (1 - TEG_LOSS)
    m_no = teg_top["DEG"] * MW["DEG"] + teg_top["TEG"] * MW["TEG"]
    teg_top["TTEG"] = W_TTEG_IN_TEG / (1 - W_TTEG_IN_TEG) * m_no / MW["TTEG"]
    heavies = {c: c602_bot[c] - teg_top[c] for c in COMP}
    out.update(ev_vap=ev_vap, ev_conc=ev_conc, dry_ovh=dry_ovh, crude=crude, cond_all=cond_all,
               rec_stream=rec_stream, bleed=bleed, meg_top=meg_top, c601_bot=c601_bot,
               deg_top=deg_top, c602_bot=c602_bot, teg_top=teg_top, heavies=heavies)
    return out


def run():
    # linear in the EO rate: solve at 1000 kmol/h and scale to the MEG product
    f1, l1 = solve(1000.0)
    g1 = glycols(l1["eo_water"])
    meg_kg = total(mass(g1["meg_top"]))
    k = MEG_PRODUCT_KG_H / meg_kg
    feeds, loop = solve(1000.0 * k)
    gly = glycols(loop["eo_water"])
    return feeds, loop, gly


def energy(feeds, loop, gly):
    eo = loop["eo_water"]["EO"]
    q = {}
    q["R101"] = (eo * DH_EO + loop["c2h4_comb"] * DH_COMB) / 3600.0
    q["E101"] = total(loop["R"]) * CP_GAS * DT_E101 / 3600.0
    lean_kg = loop["lean"]["H2O"] * MW["H2O"]
    q["C201_cw"] = lean_kg * 4.18 * DT_LEAN_COOLER / 3600.0
    q["C202_steam"] = (lean_kg * 4.18 * DT_LEAN_RICH + eo * DH_EO_DESORB) * STRIPPER_EXTRA / 3600.0
    q["C202_cw"] = q["C202_steam"] - lean_kg * 4.18 * DT_LEAN_RICH / 3600.0
    co2_t_h = loop["vent"]["CO2"] * MW["CO2"] / 1000.0
    q["C301_steam"] = co2_t_h * CO2_REGEN_GJ_PER_T * 1e6 / 3600.0
    q["C301_cw"] = 0.9 * q["C301_steam"]
    n = total(loop["K"])
    w_is = n / 3600.0 * 8.314 * 313.15 * KAPPA / (KAPPA - 1) * (
        (P_LOOP_HIGH / P_LOOP_LOW) ** ((KAPPA - 1) / KAPPA) - 1)
    q["K101_power"] = w_is / ETA_COMP
    q["K101_cw"] = q["K101_power"]
    hyd_kg = total(mass(gly["feed"]))
    lean_pump = lean_kg / 1000.0 / 3600.0 * (P_LOOP_HIGH - 200.0) / ETA_PUMP   # m3/s * kPa = kW
    hyd_pump = hyd_kg / 1000.0 / 3600.0 * (P_HYD - 200.0) / ETA_PUMP
    q["lean_pump_power"], q["hyd_pump_power"] = lean_pump, hyd_pump
    q["pumps_power"] = lean_pump + hyd_pump
    q["aux_power"] = AUX_KWH_PER_T_MEG * MEG_PRODUCT_KG_H / 1000.0
    # glycol reactor heat (adiabatic; stays in the effluent and is used by the evaporators)
    p = gly["prod"]
    steps = p["MEG"] + 2 * p["DEG"] + 3 * p["TEG"] + 4 * p["TTEG"] - gly["feed"]["MEG"]
    q["R401_heat"] = steps * DH_HYD / 3600.0
    ev_kg = gly["ev_vap"]["H2O"] * MW["H2O"]
    q["EV501_steam"] = max(ev_kg / EVAP_ECONOMY * LAMBDA_STEAM / 3600.0 - q["R401_heat"], 0.0)
    q["EV501_cw"] = ev_kg / 4.0 * LAMBDA_W / 3600.0
    dry_kg = gly["dry_ovh"]["H2O"] * MW["H2O"]
    q["C501_steam"] = dry_kg * LAMBDA_W * (1 + R_DRY) / 3600.0
    q["C501_cw"] = q["C501_steam"]
    t = gly["meg_top"]
    q["C601_steam"] = t["MEG"] * LAMBDA_KJ_KMOL["MEG"] * (1 + R_MEG) / 3600.0
    q["C601_cw"] = q["C601_steam"]
    t = gly["deg_top"]
    q["C602_steam"] = (t["DEG"] + t["MEG"]) * LAMBDA_KJ_KMOL["DEG"] * (1 + R_DEG) / 3600.0
    q["C602_cw"] = q["C602_steam"]
    t = gly["teg_top"]
    q["C603_steam"] = (t["TEG"] + t["DEG"]) * LAMBDA_KJ_KMOL["TEG"] * (1 + R_TEG) / 3600.0
    q["C603_cw"] = q["C603_steam"]
    # steam: R-101 raises MP steam used for C-202, C-301 and part of EV-501; import the rest
    raised = q["R101"]
    q["R101_to_C202"] = q["C202_steam"]
    q["R101_to_C301"] = q["C301_steam"]
    q["R101_to_EV501"] = q["EV501_steam"]
    q["R101_to_C601"] = raised - q["C202_steam"] - q["C301_steam"] - q["EV501_steam"]
    assert 0 < q["R101_to_C601"] < q["C601_steam"], "steam allocation: not an import case"
    q["MPS_C601"] = q["C601_steam"] - q["R101_to_C601"]
    q["MPS_total"] = q["MPS_C601"] + q["C501_steam"] + q["C602_steam"] + q["C603_steam"]
    q["steam_raised_kg_h"] = raised * 3600.0 / H_STEAM_RAISED
    q["power_total"] = q["K101_power"] + q["pumps_power"] + q["aux_power"]
    q["cw_total"] = sum(v for k2, v in q.items() if k2.endswith("_cw")) + q["E101"]
    return q


def stream_list(feeds, loop, gly):
    """(id, title, from, to, template, kmol dict, T K, P kPa(a))"""
    L, G = loop, gly
    makeup = {"H2O": G["makeup"]}
    s = [
        ("S1", "Ethylene feed (pipeline)", "ETH.out", "M101.eth", "loop", feeds["ETH"], 298.15, 2400),
        ("S2", "Oxygen feed (pipeline GOX)", "OXY.out", "M101.oxy", "loop", feeds["OXY"], 298.15, 2400),
        ("S3", "Methane ballast make-up", "MET.out", "M101.met", "loop", feeds["MET"], 298.15, 2400),
        ("S4", "Recycle gas to the mixer", "M103.out", "M101.rec", "loop", L["recycle"], 333.15, 2200),
        ("S5", "Reactor feed gas", "M101.out", "R101.in", "loop", L["F"], 333.15, 2200),
        ("S6", "Reactor outlet gas", "R101.out", "E101.in", "loop", L["R"], 523.15, 2100),
        ("S7", "Cooled reactor gas to the EO absorber", "E101.out", "C201.gas", "loop", L["R"], 313.15, 2050),
        ("S8", "EO absorber off-gas", "C201.gasout", "M102.gas", "loop", L["A"], 308.15, 2000),
        ("S9", "Rich absorbent (aqueous EO)", "C201.rich", "C202.rich", "aq", L["rich"], 318.15, 2000),
        ("S10", "Lean absorbent (stripped water)", "C202.lean", "C201.lean", "aq", L["lean"], 308.15, 2200),
        ("S11", "EO stripper overhead (EO, water, dissolved gases)", "C202.ovh", "C203.in", "aq", L["overhead"], 313.15, 200),
        ("S12", "Light gases from the lights stripper", "C203.gas", "M102.lights", "loop", L["lights"], 313.15, 200),
        ("S13", "Aqueous EO to the glycol reactor", "C203.eo", "M401.eo", "aq", L["eo_water"], 313.15, 3000),
        ("S14", "Recycle gas to the compressor", "M102.out", "K101.in", "loop", L["K"], 308.15, 1950),
        ("S15", "Compressed recycle gas", "K101.out", "SP101.in", "loop", L["K"], 333.15, 2200),
        ("S16", "Inerts purge to the fuel gas header", "SP101.purge", "PURGE.in", "loop", L["purge"], 333.15, 2200),
        ("S17", "Recycle gas after the purge", "SP101.out", "SP102.in", "loop", L["rest"], 333.15, 2200),
        ("S18", "Slip stream to CO2 removal", "SP102.slip", "C301.in", "loop", L["slip"], 333.15, 2200),
        ("S19", "Recycle gas bypassing CO2 removal", "SP102.bypass", "M103.bypass", "loop", L["bypass"], 333.15, 2200),
        ("S20", "CO2-depleted gas", "C301.out", "M103.treated", "loop", L["treated"], 333.15, 2150),
        ("S21", "CO2 stripper vent to atmosphere", "C301.vent", "CO2V.in", "loop", L["vent"], 313.15, 120),
        ("S22", "Process water make-up (demineralised)", "PW.out", "M401.pw", "aq", makeup, 303.15, 3000),
        ("S23", "Recycle water to the glycol reactor", "SP501.rec", "M401.rec", "aq", G["rec_stream"], 403.15, 3000),
        ("S24", "Glycol reactor feed", "M401.out", "R401.in", "aq", G["feed"], 423.15, 3000),
        ("S25", "Glycol reactor outlet", "R401.out", "EV501.in", "aq", G["prod"], 478.15, 2900),
        ("S26", "Evaporator condensate", "EV501.vap", "M501.ev", "aq", G["ev_vap"], 393.15, 200),
        ("S27", "Concentrated glycols to the drying column", "EV501.conc", "C501.in", "aq", G["ev_conc"], 403.15, 200),
        ("S28", "Drying column overhead water", "C501.ovh", "M501.dry", "aq", G["dry_ovh"], 330.15, 20),
        ("S29", "Crude glycols to the MEG column", "C501.btm", "C601.in", "aq", G["crude"], 433.15, 25),
        ("S30", "Combined recycle water", "M501.out", "SP501.in", "aq", G["cond_all"], 393.15, 300),
        ("S31", "Water bleed to biological treatment", "SP501.bleed", "WW.in", "aq", G["bleed"], 313.15, 300),
        ("S32", "MEG product", "C601.top", "MEG.in", "aq", G["meg_top"], 313.15, 300),
        ("S33", "MEG column bottoms", "C601.btm", "C602.in", "aq", G["c601_bot"], 443.15, 15),
        ("S34", "DEG product", "C602.top", "DEG.in", "aq", G["deg_top"], 313.15, 300),
        ("S35", "DEG column bottoms", "C602.btm", "C603.in", "aq", G["c602_bot"], 463.15, 5),
        ("S36", "TEG product", "C603.top", "TEG.in", "aq", G["teg_top"], 313.15, 300),
        ("S37", "Heavy glycols residue", "C603.btm", "HVY.in", "aq", G["heavies"], 473.15, 300),
    ]
    return s


def fmt_stream(sid, title, frm, to, tpl, kmol, T, P):
    m = mass(kmol)
    tot = total(m)
    fr = {c: v / tot for c, v in m.items() if v / tot >= 5e-7}
    # renormalise the rounded fractions to sum exactly 1 (the largest takes the rest)
    rounded = {c: round(v, 6) for c, v in fr.items()}
    big = max(rounded, key=rounded.get)
    rounded[big] = round(1.0 - sum(v for c, v in rounded.items() if c != big), 6)
    comp = ", ".join(f"{c}: {v}" for c, v in rounded.items())
    src = "eg_balance.py D-006"
    return (
        f"  - {{id: {sid}, title: \"{title}\", from: {frm}, to: {to}, template: {tpl}, state: {{design: {{\n"
        f"      pressure: {{value: {P}, provenance: assumed, source: D-004}},"
        f" temperature: {{value: {T}, provenance: assumed, source: D-004}},\n"
        f"      flow: {{value: {tot:.1f}, basis: mass, provenance: assumed, source: {src}}},\n"
        f"      composition: {{basis: mass_fraction, values: {{{comp}}}, provenance: assumed, source: {src}}}}}}}}}\n"
    )


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "build"
    os.makedirs(out_dir, exist_ok=True)
    feeds, loop, gly = run()
    q = energy(feeds, loop, gly)
    streams = stream_list(feeds, loop, gly)
    with open(os.path.join(out_dir, "streams.yaml"), "w") as f:
        for s in streams:
            f.write(fmt_stream(*s))
    meg = MEG_PRODUCT_KG_H
    kg = lambda s: total(mass(s))
    lines = []
    P = lambda *a: lines.append(" ".join(str(x) for x in a))
    eo = loop["eo_water"]["EO"]
    P(f"EO to glycols {eo:.2f} kmol/h = {eo*MW['EO']:.1f} kg/h; ethylene combusted {loop['c2h4_comb']:.2f} kmol/h")
    P(f"reactor inlet {loop['G']:.1f} kmol/h; f_slip {loop['f_slip']:.4f}")
    yF = {c: round(v / total(loop['F']), 5) for c, v in loop['F'].items() if v > 0}
    P("reactor inlet mol fractions", yF)
    P(f"purge {total(loop['purge']):.2f} kmol/h, Ar fraction {loop['purge']['AR']/total(loop['purge']):.4f}")
    p = gly["prod"]
    gm = {c: p[c] * MW[c] for c in ("MEG", "DEG", "TEG", "TTEG")}
    tg = sum(gm.values())
    P("glycol reactor outlet glycols wt%", {c: round(100 * v / tg, 2) for c, v in gm.items()})
    sel = {c: round(p[c] / (gly['feed']['EO']), 6) for c in ("DEG", "TEG", "TTEG")}
    sel["MEG"] = round((p["MEG"] - gly["feed"]["MEG"]) / gly["feed"]["EO"], 6)
    P("hydration selectivities kmol/kmol EO", sel)
    P("--- per kg MEG product (gate-to-gate)")
    for name, s in (("ethylene", feeds["ETH"]), ("oxygen", feeds["OXY"]), ("methane", feeds["MET"]),
                    ("process water", {"H2O": gly["makeup"]}), ("DEG", gly["deg_top"]), ("TEG", gly["teg_top"]),
                    ("heavies", gly["heavies"]), ("purge", loop["purge"]), ("CO2 vent", loop["vent"]),
                    ("bleed", gly["bleed"])):
        P(f"  {name}: {kg(s)/meg:.6f} kg/kg  ({kg(s):.1f} kg/h)")
    for c in ("CO2", "CH4", "C2H4", "H2O"):
        P(f"  vent {c}: {loop['vent'][c]*MW[c]/meg:.6f} kg/kg")
    ins = kg(feeds["ETH"]) + kg(feeds["OXY"]) + kg(feeds["MET"]) + gly["makeup"] * MW["H2O"]
    outs = (kg(gly["meg_top"]) + kg(gly["deg_top"]) + kg(gly["teg_top"]) + kg(gly["heavies"])
            + kg(loop["purge"]) + kg(loop["vent"]) + kg(gly["bleed"]))
    P(f"overall mass in {ins:.1f} out {outs:.1f} kg/h, diff {ins-outs:.3f}")
    P("--- energy kW")
    for k2, v in q.items():
        P(f"  {k2}: {v:.1f}")
    P(f"  MP steam import {q['MPS_total']/meg:.4f} kWh/kg MEG; power {q['power_total']/meg:.4f} kWh/kg; CW {q['cw_total']/meg:.4f} kWh/kg")
    txt = "\n".join(lines)
    with open(os.path.join(out_dir, "summary.txt"), "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
