"""Steady-state mass balance and utility estimate of the urea-1 concept flowsheet.

Provenance script of the stream values in process/flowsheet.yaml (DESIGN.md D-006): it is
run with `cheme run scripts/urea_balance.py` and prints the stream entries and duties that
were pasted into the flowsheet. It is NOT a thermodynamic model: the separations are fixed
split fractions and specified compositions (ASSUMED, DESIGN.md D-005/D-006), the reactor is a
conversion model, unconverted ammonium carbamate is carried as its NH3 + CO2 equivalent, and
the duties are hand estimates with the latent and reaction heats named below. Every number
that is not computed here is a design choice (ASSUMED) or a fact from a cited source.

Sources (facts only, used in our own form):
  BREF  EC JRC (2007) Reference Document on BAT for the Manufacture of Large Volume Inorganic
        Chemicals - Ammonia, Acids and Fertilisers (LVIC-AAF), chapter 8 (urea).
"""

import math

MW = {"NH3": 17.031, "CO2": 44.0095, "H2O": 18.0153, "UREA": 60.0553, "BIURET": 103.0798,
      "N2": 28.0134, "O2": 31.9988}
COMPS = list(MW)
R = 8.314462  # kJ/(kmol K)
NM3 = 22.414  # Nm3/kmol (273.15 K, 101.325 kPa)

# ---- design basis (DESIGN.md D-002, D-003) --------------------------------------------
PRODUCT = 2000e3 / 24                       # kg/h prilled urea (ASSUMED capacity 2000 t/d)
W_PROD = {"UREA": 0.989, "BIURET": 0.008, "H2O": 0.003}  # ASSUMED design grade (D-003)
CO2_FEED_Y = {"CO2": 0.985, "H2O": 0.005, "N2": 0.010}   # ASSUMED battery-limit CO2 (D-004)
O2_PASSIVATION = 0.006                      # ASSUMED mol O2 per mol CO2-feed gas (D-004)
AIR_Y = {"N2": 0.79, "O2": 0.21}            # dry air, Ar lumped into N2 (ASSUMED)
AIR_HUMIDITY = 0.015                        # kg H2O / kg dry prilling air (ASSUMED, D-009)

# ---- synthesis (D-005) ------------------------------------------------------------------
NC_RATIO = 2.8      # NH3/CO2 at the reactor inlet, mol (BREF Table 8.14, CO2 stripping example)
HC_RATIO = 0.45     # H2O/CO2 at the reactor inlet, mol (ASSUMED). Like N/C, the loop's water
                    # inventory is not fixed by the balance (an identity): it is a specification.
X_CO2 = 0.58        # CO2 conversion per pass (ASSUMED within 50-80 %, BREF section 8.2.1)
# Stripper: share of the NH3, CO2 and water fed to it (reactor effluent + CO2 feed) that leaves
# with the stripped solution (ASSUMED stripping efficiency). The reactor N/C and the conversion
# do not fix how the unconverted carbamate divides between the HP and the LP recycle: these do.
F_N_STRIP, F_C_STRIP, F_W_STRIP = 0.15, 0.12, 0.85
E102_GAS = {"NH3": 0.04, "CO2": 0.03, "H2O": 0.003}  # fraction of E-102 content to the HP scrubber (ASSUMED)
HPS_VENT = {"NH3": 0.25, "CO2": 0.05, "H2O": 0.02}   # HP scrubber vent, mol per mol inerts (ASSUMED)

# ---- LP recirculation and evaporation (D-006) ------------------------------------------
W_UREA_LP = 0.70            # urea mass fraction of the solution leaving the LP rectifier (ASSUMED)
COND_W = {"NH3": 0.06, "CO2": 0.04, "UREA": 0.01}  # process condensate before treatment (ASSUMED
                            # design target from the BREF Table 8.8 remark on a CO2 stripping plant)
W_UREA_EV1 = 0.95           # urea mass fraction after the 1st evaporator (ASSUMED)
W_H2O_MELT = 0.004          # water in the melt to the prilling tower (ASSUMED)
VENT_NH3_PER_T = 0.070      # kg NH3 per t urea from the LP absorber vent (BREF Table 8.10, CO2 stripping, LP scrubber)
VENT_CO2_PER_NH3 = 0.5      # mol CO2 per mol NH3 in that vent (ASSUMED)
VENT_H2O_Y = 0.0185         # water in the LP vent, mol fraction (saturation at 313 K, 300-400 kPa; ASSUMED)
DES_WATER_RATIO = 1.0       # kg water per kg NH3+CO2 in each desorber overhead (ASSUMED)
TREATED_PPM = 1e-6          # NH3 and urea in treated condensate, mass fraction (BREF Table 8.20, new plants)

# ---- prilling (D-007, D-009) ------------------------------------------------------------
T_MELT, T_FUS, T_PRILL, T_AIR_IN, T_AIR_OUT = 413.15, 406.0, 343.15, 303.15, 343.15  # K, ASSUMED
H_FUS = 14000.0 / MW["UREA"]   # kJ/kg, ASSUMED ~14 kJ/mol fusion enthalpy of urea
CP_L, CP_S, CP_AIR, CP_VAP = 2.1, 1.55, 1.006, 1.88  # kJ/(kg K), ASSUMED
DUST_RAW, DUST_OUT = 100.0, 35.0  # mg/Nm3: raw within BREF Table 8.10 (60-130), out within BAT 15-55
NH3_RAW, NH3_OUT = 35.0, 30.0     # mg/Nm3: out within BAT 3-35 (BREF section 8.5), water scrubbing
SCRUB_EVAP_SHARE = 0.5     # share of the heat the air took up that the wet scrubber turns into evaporation (ASSUMED)
SCRUB_LIQUOR_UREA = 0.45   # urea mass fraction of the scrubber liquor recycled to evaporation (ASSUMED)
LAMBDA_SCRUB = 2390.0      # kJ/kg water at about 318 K

# ---- utilities (D-010) ------------------------------------------------------------------
MPS_T_PER_T = 0.8          # t steam per t urea at 24 bar, CO2 stripping with electric CO2 compression (BREF Table 8.5)
H_FG_MPS = 1836.0          # kJ/kg latent heat at 2400 kPa(a) (steam tables)
H_CARB = 120000.0          # kJ per kmol CO2 to decompose/form carbamate in solution (ASSUMED, below the
                           # ~160 MJ/kmol of solid ammonium carbamate from formation enthalpies)
LAMBDA = 2300.0            # kJ/kg water evaporated/condensed in the LP and vacuum sections (ASSUMED)
Q_HYD = 1000.0             # kW net hydrolyser heat after feed/effluent exchange (ASSUMED)


def kmol(d):
    return {c: d.get(c, 0.0) for c in COMPS}


def mass(d):
    return sum(d[c] * MW[c] for c in COMPS)


def add(*ds):
    return {c: sum(d.get(c, 0.0) for d in ds) for c in COMPS}


def sub(a, b):
    return {c: a.get(c, 0.0) - b.get(c, 0.0) for c in COMPS}


def from_mass(dm):
    return kmol({c: v / MW[c] for c, v in dm.items()})


# ---- finishing: product, melt, prilling air, scrubber (fixed by the product) ------------
prod = from_mass({c: W_PROD[c] * PRODUCT for c in W_PROD})
m_melt0 = PRODUCT  # first guess for the heat balance
q_prill = m_melt0 * (CP_L * (T_MELT - T_FUS) + H_FUS + CP_S * (T_FUS - T_PRILL)) / 3600  # kW
dry_air = q_prill * 3600 / ((CP_AIR + AIR_HUMIDITY * CP_VAP) * (T_AIR_OUT - T_AIR_IN))  # kg/h
air_dry = {c: dry_air / (0.79 * MW["N2"] + 0.21 * MW["O2"]) * y for c, y in AIR_Y.items()}
air = kmol({**air_dry, "H2O": dry_air * AIR_HUMIDITY / MW["H2O"]})
nm3 = sum(air.values()) * NM3                      # exhaust volume, Nm3/h (wet, ~ air)
dust_raw, dust_out = DUST_RAW * nm3 * 1e-6, DUST_OUT * nm3 * 1e-6   # kg/h urea
nh3_raw, nh3_out = NH3_RAW * nm3 * 1e-6, NH3_OUT * nm3 * 1e-6       # kg/h NH3
melt_m = {"UREA": prod["UREA"] * MW["UREA"] + dust_raw, "BIURET": prod["BIURET"] * MW["BIURET"],
          "NH3": nh3_raw}
melt_m["H2O"] = W_H2O_MELT / (1 - W_H2O_MELT) * sum(melt_m.values())
melt = from_mass(melt_m)
exhaust_raw = add(air, from_mass({"UREA": dust_raw, "NH3": nh3_raw,
                                  "H2O": melt_m["H2O"] - prod["H2O"] * MW["H2O"]}))
evap = SCRUB_EVAP_SHARE * q_prill * 3600 / LAMBDA_SCRUB          # kg/h water evaporated in C-501
liquor_m = {"UREA": dust_raw - dust_out, "NH3": nh3_raw - nh3_out}
liquor_m["H2O"] = liquor_m["UREA"] * (1 - SCRUB_LIQUOR_UREA) / SCRUB_LIQUOR_UREA
liquor = from_mass(liquor_m)
scrub_water_m = evap + liquor_m["H2O"]        # C-501 water: what evaporates plus the liquor's water

# ---- evaporation ------------------------------------------------------------------------
x_biu = melt["BIURET"]                  # kmol/h biuret formed in E-302 (2 urea -> biuret + NH3)
ev1_out = kmol({"UREA": melt["UREA"] + 2 * x_biu})
ev1_out["H2O"] = ev1_out["UREA"] * MW["UREA"] * (1 - W_UREA_EV1) / W_UREA_EV1 / MW["H2O"]
ev2_vap = kmol({"H2O": ev1_out["H2O"] - melt["H2O"], "NH3": x_biu - melt["NH3"]})
# melt NH3 comes from biuret formation (ASSUMED): ev2_vap NH3 = biuret NH3 less what the melt keeps

# ---- iterate the recycle loops ----------------------------------------------------------
S30 = kmol({})          # LP carbamate solution to the HP scrubber
S32 = kmol({})          # desorber overhead to the LP carbamate condenser
s45_m = 0.0
for it in range(200):
    # process condensate from the evaporators: E-301 vapour carries all NH3/CO2 of its feed and
    # the entrained urea; its NH3/CO2/urea fixed by the condensate targets COND_W.
    w_ev = (None)
    # condensate mass M: water = water evaporated; solve M from the fractions
    water_cond_known = ev2_vap["H2O"] * MW["H2O"]
    # E-301 vapour water = S23 water + liquor water - ev1_out water; S23 water from the urea spec
    # iterate on M (condensate mass)
    M = 40000.0 if it == 0 else M
    for _ in range(50):
        cond_m = {c: COND_W[c] * M for c in COND_W}
        cond_m["NH3"] = COND_W["NH3"] * M
        s23_m = {"UREA": ev1_out["UREA"] * MW["UREA"] + cond_m["UREA"] - liquor_m["UREA"],
                 "NH3": cond_m["NH3"] - ev2_vap["NH3"] * MW["NH3"] - liquor_m["NH3"],
                 "CO2": cond_m["CO2"]}
        s23_total = s23_m["UREA"] / W_UREA_LP
        s23_m["H2O"] = s23_total - s23_m["UREA"] - s23_m["NH3"] - s23_m["CO2"]
        ev1_vap_h2o = s23_m["H2O"] + liquor_m["H2O"] - ev1_out["H2O"] * MW["H2O"]
        M_new = (ev1_vap_h2o + water_cond_known) / (1 - sum(COND_W.values()))
        if abs(M_new - M) < 1e-6:
            break
        M = M_new
    S23 = from_mass(s23_m)
    cond = from_mass({**{c: COND_W[c] * M for c in COND_W}, "H2O": M * (1 - sum(COND_W.values()))})
    ev1_vap = sub(add(S23, liquor), ev1_out)
    U = S23["UREA"]                       # urea formed in R-101 per hour

    # condensate treatment: desorber 1 (C-401), hydrolyser (R-401), desorber 2 (C-402)
    s40_water_guess = cond["H2O"]
    hyd = cond["UREA"] - (TREATED_PPM * s40_water_guess * MW["H2O"]) / MW["UREA"]  # kmol/h hydrolysed
    s39 = add(kmol({"UREA": cond["UREA"] - hyd, "H2O": -hyd, "NH3": 2 * hyd, "CO2": hyd}))
    # C-401 liquid S38: urea and water only (its NH3/CO2 go overhead); S39 = S38 hydrolysed
    nh3_left = TREATED_PPM * s40_water_guess * MW["H2O"] / MW["NH3"]
    s42_nc = kmol({"NH3": 2 * hyd - nh3_left, "CO2": hyd})
    s42 = add(s42_nc, from_mass({"H2O": DES_WATER_RATIO * mass(s42_nc)}))
    s32_nc = kmol({"NH3": cond["NH3"] + s42["NH3"], "CO2": cond["CO2"] + s42["CO2"]})
    S32 = add(s32_nc, from_mass({"H2O": DES_WATER_RATIO * mass(s32_nc)}))
    S38 = sub(add(cond, s42), S32)
    S39 = add(S38, kmol({"UREA": -hyd, "H2O": -hyd, "NH3": 2 * hyd, "CO2": hyd}))
    S40 = sub(S39, s42)

    # LP absorber vent (C-202)
    vent_nh3 = VENT_NH3_PER_T * PRODUCT / 1000 / MW["NH3"]
    co2_feed_gas = None
    # fresh feeds from the overall element balance of the previous iteration
    # the traces of the treated water leave with S45 and, through the scrubber, with S54
    share_out = (s45_m + scrub_water_m) / max(mass(S40), 1)
    out_N = (2 * prod["UREA"] + 3 * prod["BIURET"] + 2 * dust_out / MW["UREA"] + nh3_out / MW["NH3"]
             + vent_nh3 + (2 * S40["UREA"] + S40["NH3"]) * share_out)
    out_C = (prod["UREA"] + 2 * prod["BIURET"] + dust_out / MW["UREA"]
             + VENT_CO2_PER_NH3 * vent_nh3 + S40["UREA"] * share_out)
    S1 = kmol({"NH3": out_N})                               # fresh NH3
    co2gas = out_C / CO2_FEED_Y["CO2"]
    S3 = kmol({c: co2gas * y for c, y in CO2_FEED_Y.items()})
    pas_air_n = O2_PASSIVATION * co2gas / AIR_Y["O2"]
    S4 = kmol({c: pas_air_n * y for c, y in AIR_Y.items()})
    S6 = add(S3, S4)                                        # CO2 + passivation air to stripper
    inerts = {"N2": S6["N2"], "O2": S6["O2"]}

    S21 = kmol({**inerts, **{c: HPS_VENT[c] * (inerts["N2"] + inerts["O2"]) for c in HPS_VENT}})
    n_inert = inerts["N2"] + inerts["O2"]
    vent_nc = vent_nh3 * (1 + VENT_CO2_PER_NH3) + n_inert
    S31 = kmol({**inerts, "NH3": vent_nh3, "CO2": VENT_CO2_PER_NH3 * vent_nh3,
                "H2O": VENT_H2O_Y / (1 - VENT_H2O_Y) * vent_nc})

    # reactor feed and effluent (conversion model)
    co2_in = U / X_CO2
    nh3_in = NC_RATIO * co2_in
    h2o_in = HC_RATIO * co2_in
    S15 = kmol({"NH3": nh3_in, "CO2": co2_in, "H2O": h2o_in})
    S11 = kmol({"NH3": nh3_in - 2 * U, "CO2": co2_in - U, "H2O": h2o_in + U, "UREA": U})
    # stripper: liquid S14 by the retention fractions, gas S13 the rest
    strip_in = add(S11, S6)
    S14 = kmol({"UREA": U, "NH3": F_N_STRIP * strip_in["NH3"], "CO2": F_C_STRIP * strip_in["CO2"],
                "H2O": F_W_STRIP * strip_in["H2O"]})
    S13 = sub(strip_in, S14)
    S22 = sub(S14, S23)                   # LP rectifier gas
    # HP condenser and scrubber
    e102 = add(S13, S1, kmol({}))         # + S20, solved below
    # S20 = S16 + S30 - S21 and S15 = E102 total - S16 => E102 total = S15 + S16
    tot_guess = add(S15, inerts)
    for _ in range(20):
        S16 = kmol({**inerts, **{c: E102_GAS[c] * tot_guess[c] for c in E102_GAS}})
        tot_guess = add(S15, S16)
    S20 = sub(add(S16, S30), S21)
    # LP section water: absorber water closes the loop water balance
    W_abs = (S23["H2O"] + S21["H2O"] - S21["H2O"] + S31["H2O"] - U - S6["H2O"] - S32["H2O"]) * MW["H2O"]
    S41 = {c: S40[c] * W_abs / mass(S40) for c in COMPS}
    S24 = add(S22, S32)                  # LP carbamate condenser outlet
    S30_new = sub(add(S24, S21, S41), S31)
    # treated water split: absorber, scrubber, battery limit
    s45_m = mass(S40) - W_abs - scrub_water_m
    err = sum(abs(S30_new[c] - S30[c]) for c in COMPS)
    S30 = S30_new
    closure = sub(add(S13, S1, S30), add(S21, S15))   # HP loop: must vanish at convergence
    if err < 1e-9 and max(abs(v) for v in closure.values()) < 1e-9:
        break

S44 = from_mass({"H2O": scrub_water_m})
frac = {"abs": W_abs / mass(S40), "scrub": scrub_water_m / mass(S40)}
S41 = {c: S40[c] * frac["abs"] for c in COMPS}
S44 = {c: S40[c] * frac["scrub"] for c in COMPS}
S45 = sub(S40, add(S41, S44))
S52 = add(liquor, {c: 0.0 for c in COMPS})
S51 = prod
S50 = air
S53 = exhaust_raw
S54 = sub(add(S53, S44), S52)
S35 = melt
S33 = ev1_out
S34 = ev1_vap
S36 = ev2_vap
S37 = cond
S5 = add(S3, S4)

# ---- utilities (kW) ---------------------------------------------------------------------
n_co2 = sum(S5.values())
k, stages, eta = 1.28, 4, 0.78   # ASSUMED: 4 intercooled stages, isentropic efficiency 0.78
ratio = 14500 / 160
w_k101 = n_co2 / 3600 * R * 313.15 * k / (k - 1) * stages * (ratio ** ((k - 1) / (k * stages)) - 1) / eta
w_p101 = mass(S1) / 3600 / 610.0 * (15000 - 2200) / 0.65        # rho 610 kg/m3, eta 0.65 (ASSUMED)
w_p102 = mass(S30) / 3600 / 1100.0 * (14200 - 300) / 0.60       # rho 1100 kg/m3, eta 0.60 (ASSUMED)
v_fan = sum(S54.values()) * R * 318.15 / 101.325 / 3600          # m3/s at the fan (after the scrubber)
w_fan = v_fan * 2.0 / 0.70                                       # 2.0 kPa, eta 0.70 (ASSUMED)
q_mps = MPS_T_PER_T * PRODUCT / 1000 * 1000 * H_FG_MPS / 3600    # kW
q_c201 = S22["CO2"] * H_CARB / 3600 + S22["H2O"] * MW["H2O"] * LAMBDA / 3600
q_e301 = (ev1_vap["CO2"] * H_CARB + ev1_vap["H2O"] * MW["H2O"] * LAMBDA) / 3600
q_e302 = ev2_vap["H2O"] * MW["H2O"] * LAMBDA / 3600
q_des = ((S32["CO2"]) * H_CARB + (S32["H2O"] + s42["H2O"]) * MW["H2O"] * LAMBDA) / 3600
q_strip = q_mps - q_e302 - Q_HYD
q_lp = q_c201 + q_e301 + q_des
q_e102_pot = (S13["CO2"] + S1["NH3"] * 0) * H_CARB / 3600 - U * 28000 / 3600  # carbamate formed less urea dehydration (ASSUMED +28 MJ/kmol)
q_e201 = (S24["CO2"] * H_CARB + S24["H2O"] * MW["H2O"] * LAMBDA) / 3600
q_e303 = (cond["CO2"] * H_CARB + cond["H2O"] * MW["H2O"] * LAMBDA) / 3600
q_k101cw = 0.9 * w_k101

STREAMS = [
    # id, title, from, to, T, P, kmol dict, calc (pass-through: propagate fills flow+composition)
    ("S1", "Liquid ammonia from the ammonia plant", "NH3.out", "P101.in", 293.15, 2200, S1, False),
    ("S2", "HP ammonia to the HP carbamate condenser", "P101.out", "E102.nh3", 300.15, 15000, S1, True),
    ("S3", "CO2 from the ammonia plant", "CO2.out", "M101.co2", 313.15, 160, S3, False),
    ("S4", "Passivation air", "PAIR.out", "M101.air", 303.15, 160, S4, False),
    ("S5", "CO2 with passivation air", "M101.out", "K101.in", 313.15, 160, S5, True),
    ("S6", "Compressed CO2 to the HP stripper", "K101.out", "E101.co2", 393.15, 14500, S5, True),
    ("S15", "HP condenser outlet to the reactor", "E102.out", "R101.in", 440.15, 14000, S15, False),
    ("S11", "Reactor effluent to the HP stripper", "R101.out", "E101.liq_in", 453.15, 14000, S11, True),
    ("S13", "HP stripper off-gas", "E101.gas", "E102.gas", 458.15, 14000, S13, False),
    ("S14", "Stripped urea solution", "E101.liq", "C201.feed", 443.15, 14000, S14, False),
    ("S16", "HP condenser gas to the HP scrubber", "E102.vent", "V103.gas", 440.15, 14000, S16, False),
    ("S20", "HP scrubber carbamate to the HP condenser", "V103.liq", "E102.carb", 433.15, 14000, S20, False),
    ("S21", "HP scrubber off-gas", "V103.vent", "C202.gas", 400.15, 14000, S21, False),
    ("S22", "LP rectifier off-gas", "C201.gas", "E201.gas", 408.15, 300, S22, False),
    ("S23", "Urea solution from the LP rectifier", "C201.liq", "E301.feed", 408.15, 300, S23, False),
    ("S32", "Desorber overhead to the LP condenser", "C401.vap", "E201.des", 390.15, 300, S32, False),
    ("S24", "LP carbamate condensate", "E201.out", "C202.liq", 333.15, 300, S24, False),
    ("S41", "Treated water to the LP absorber", "SPL401.abs", "C202.water", 313.15, 300, S41, False),
    ("S31", "LP absorber vent to atmosphere", "C202.vent", "VENT.in", 313.15, 300, S31, False),
    ("S30", "LP carbamate solution", "C202.liq_out", "P102.in", 313.15, 300, S30, False),
    ("S30B", "HP carbamate to the HP scrubber", "P102.out", "V103.carb", 318.15, 14200, S30, True),
    ("S52", "Scrubber liquor to the 1st evaporator", "C501.liq", "E301.liquor", 318.15, 300, S52, False),
    ("S33", "Urea solution 95 wt% to the 2nd evaporator", "E301.liq", "E302.feed", 403.15, 33, S33, False),
    ("S34", "1st evaporator vapour", "E301.vap", "E303.v1", 403.15, 33, S34, False),
    ("S35", "Urea melt to the prilling tower", "E302.liq", "T501.melt", 413.15, 3, S35, False),
    ("S36", "2nd evaporator vapour", "E302.vap", "E303.v2", 413.15, 3, S36, False),
    ("S37", "Process condensate to treatment", "E303.out", "C401.feed", 313.15, 300, S37, False),
    ("S42", "Desorber 2 overhead to desorber 1", "C402.vap", "C401.vap_in", 407.15, 300, s42, False),
    ("S38", "Desorbed condensate to the hydrolyser", "C401.liq", "R401.in", 390.15, 1900, S38, False),
    ("S39", "Hydrolysed condensate to desorber 2", "R401.out", "C402.feed", 473.15, 1900, S39, True),
    ("S40", "Treated process condensate", "C402.liq", "SPL401.in", 313.15, 300, S40, False),
    ("S44", "Treated water to the prilling scrubber", "SPL401.scrub", "C501.water", 313.15, 300, S44, True),
    ("S45", "Treated condensate to battery limit", "SPL401.bl", "WATER.in", 313.15, 300, S45, True),
    ("S50", "Prilling air", "AIR.out", "T501.air", T_AIR_IN, 101.325, S50, False),
    ("S51", "Urea prills to storage", "T501.prills", "UREA.in", T_PRILL, 101.325, S51, False),
    ("S53", "Prilling tower exhaust", "T501.exhaust", "C501.gas", T_AIR_OUT, 101.325, S53, False),
    ("S54", "Scrubbed exhaust to atmosphere", "C501.gas_out", "EXHAUST.in", 318.15, 101.325, S54, False),
]


def fmt_stream(sid, title, frm, to, T, P, d, calc):
    m = mass(d)
    n = sum(v for v in d.values() if v > 0)
    comp = {c: d[c] / n for c in COMPS if d[c] > 1e-12}
    src = "scripts/urea_balance.py (D-006)"
    lines = [f"  - id: {sid}", f"    title: {title}", f"    from: {frm}", f"    to: {to}",
             "    template: urea-process", "    state:", "      design:",
             f"        pressure: {{value: {P}, provenance: assumed, source: D-006}}",
             f"        temperature: {{value: {T}, provenance: assumed, source: D-006}}"]
    if not calc:
        cs = ", ".join(f"{c}: {v:.8g}" for c, v in comp.items())
        lines.append(f"        flow: {{value: {m:.6g}, basis: mass, provenance: assumed, source: \"{src}\"}}")
        lines.append(f"        composition: {{basis: mole_fraction, values: {{{cs}}}, provenance: assumed, source: \"{src}\"}}")
    return "\n".join(lines)


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
    import sys
    # the values process/flowsheet.yaml cites from this script (balance-output contract); the
    # duties as in ENERGY below
    flowsheet = {}
    for sid, title, frm, to, T, P, d, calc in STREAMS:
        n = sum(v for v in d.values() if v > 0)
        flowsheet[sid] = {"temperature": T, "pressure": P,
                          "flow": {"value": mass(d), "basis": "mass"},
                          "composition": {"values": {c: d[c] / n for c in COMPS if d[c] > 1e-12},
                                          "basis": "mole_fraction"}}
    for qid, q in {"Q1": w_k101, "Q2": w_p101, "Q3": w_p102, "Q4": w_fan, "Q5": q_strip,
                   "Q6": q_e302, "Q7": Q_HYD, "Q8": q_c201, "Q9": q_e301, "Q10": q_des,
                   "Q11": q_k101cw, "Q12": q_e201, "Q13": q_e303}.items():
        flowsheet[qid] = {"duty": q}
    write_balance_output({"design": flowsheet})
    if "--streams" in sys.argv:
        for s in STREAMS:
            print(fmt_stream(*s))
        ENERGY = [
            ("Q1", "K-101 shaft power", "POWER.k101", "K101.power", w_k101, "4 intercooled stages, eta 0.78 (D-010)"),
            ("Q2", "P-101 shaft power", "POWER.p101", "P101.power", w_p101, "V dp / 0.65 (D-010)"),
            ("Q3", "P-102 shaft power", "POWER.p102", "P102.power", w_p102, "V dp / 0.60 (D-010)"),
            ("Q4", "Prilling fan power", "POWER.t501", "T501.power", w_fan, "2.0 kPa, eta 0.70 (D-010)"),
            ("Q5", "HP stripper MP steam", "MPS.e101", "E101.steam", q_strip, "BREF Table 8.5 total 0.8 t/t less E-302 and R-401 (D-010)"),
            ("Q6", "2nd evaporator MP steam", "MPS.e302", "E302.steam", q_e302, "water evaporated x 2300 kJ/kg (D-010)"),
            ("Q7", "Hydrolyser MP steam", "MPS.r401", "R401.steam", Q_HYD, "net after feed/effluent exchange, ASSUMED (D-010)"),
            ("Q8", "LP steam from E-102 to the LP rectifier heater", "E102.lps1", "C201.heat", q_c201, "carbamate decomposition 120 MJ/kmol CO2 + water 2300 kJ/kg (D-010)"),
            ("Q9", "LP steam from E-102 to the 1st evaporator", "E102.lps2", "E301.heat", q_e301, "water 2300 kJ/kg + carbamate 120 MJ/kmol CO2 (D-010)"),
            ("Q10", "LP steam from E-102 to the desorbers", "E102.lps3", "C402.heat", q_des, "overhead water 2300 kJ/kg + carbamate 120 MJ/kmol CO2 (D-010)"),
            ("Q11", "K-101 intercoolers", "K101.cw", "CW.k101", q_k101cw, "0.9 x shaft power (D-010)"),
            ("Q12", "LP carbamate condenser", "E201.cw", "CW.e201", q_e201, "carbamate 120 MJ/kmol CO2 + water 2300 kJ/kg (D-010)"),
            ("Q13", "Evaporator condensers", "E303.cw", "CW.e303", q_e303, "water 2300 kJ/kg + carbamate 120 MJ/kmol CO2 (D-010)"),
        ]
        for qid, title, frm, to, q, basis in ENERGY:
            print(f"  - {{id: {qid}, title: {title}, kind: energy, from: {frm}, to: {to}, state: {{design: "
                  f"{{duty: {{value: {q:.0f}, provenance: assumed, source: \"scripts/urea_balance.py, {basis}\"}}}}}}}}")
        sys.exit(0)
    print(f"iterations {it}, U = {U:.3f} kmol/h urea formed in R-101 ({U * MW['UREA']:.0f} kg/h)")
    for s in STREAMS:
        d = s[6]
        m = mass(d)
        wt = " ".join(f"{c}:{100 * d[c] * MW[c] / m:.2f}" for c in COMPS if d[c] * MW[c] / m > 1e-5)
        neg = [c for c in COMPS if d[c] < -1e-9]
        print(f"{s[0]:5s} {m:12.1f} kg/h  {wt}  {'NEGATIVE ' + str(neg) if neg else ''}")
    print(f"SPL401 split: abs {mass(S41) / mass(S40):.8f} scrub {mass(S44) / mass(S40):.8f}; "
          f"hydrolysis conversion {1 - S40['UREA'] / S38['UREA']:.8f}")
    print("HP loop closure kmol/h:", {c: round(v, 6) for c, v in closure.items() if abs(v) > 1e-9})
    print(f"reactor inlet N/C {S15['NH3'] / S15['CO2']:.3f}, H2O/CO2 {S15['H2O'] / S15['CO2']:.3f}")
    print(f"absorber water {W_abs:.0f} kg/h, scrubber water {scrub_water_m:.0f} kg/h, to BL {mass(S45):.0f} kg/h")
    print(f"prilling heat {q_prill:.0f} kW, dry air {dry_air:.0f} kg/h, exhaust {nm3:.0f} Nm3/h")
    t = PRODUCT / 1000
    print(f"per t product: NH3 {mass(S1) / t:.1f} kg, CO2 gas {mass(S3) / t:.1f} kg (CO2 {S3['CO2'] * MW['CO2'] / t:.1f})")
    print(f"power kW: K101 {w_k101:.0f} P101 {w_p101:.0f} P102 {w_p102:.0f} fan {w_fan:.0f}; total "
          f"{(w_k101 + w_p101 + w_p102 + w_fan):.0f} = {(w_k101 + w_p101 + w_p102 + w_fan) / t:.1f} kWh/t (BREF 110)")
    print(f"MP steam {q_mps:.0f} kW: E302 {q_e302:.0f} R401 {Q_HYD:.0f} stripper {q_strip:.0f}")
    print(f"LP demand kW: C201 {q_c201:.0f} E301 {q_e301:.0f} desorbers {q_des:.0f} sum {q_lp:.0f}; E102 potential {q_e102_pot:.0f}")
    cw = q_e201 + q_e303 + q_k101cw
    print(f"CW kW: E201 {q_e201:.0f} E303 {q_e303:.0f} K101 {q_k101cw:.0f} sum {cw:.0f} = "
          f"{cw * 3600 / 4.18 / 10 / 1000 / t:.1f} m3/t at 10 K (BREF 60)")
