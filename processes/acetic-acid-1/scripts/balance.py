"""Concept heat and material balance of acetic-acid-1 (methanol carbonylation, Ir/Ru, low water).

An independent, transparent shortcut balance (DESIGN.md D-006): every split, recycle ratio and
reflux ratio is an ASSUMED design choice named below with its decision; the by-product ratios
come from US 6,140,535 Examples 1-5 (D-004). The values it prints are entered in
process/flowsheet.yaml as `assumed` with source "scripts/balance.py"; cheme recalculates the mixer,
the pumps and the reactor (`cheme process propagate --fill`) and checks every balance.

Run: cheme run scripts/balance.py            (prints the streams, conversions and duties)
     cheme run scripts/balance.py --yaml     (the streams as YAML for flowsheet.yaml)
No property package covers this polar, associating mixture: the duties use rounded
normal-boiling-point heats of vaporisation and constant liquid heat capacities (D-008).
"""
import sys

M = {"CO": 28.010, "H2": 2.016, "CO2": 44.009, "CH4": 16.043, "N2": 28.014, "CH3OH": 32.042,
     "H2O": 18.015, "CH3COOH": 60.052, "CH3I": 141.939, "MEOAC": 74.079, "C2H5COOH": 74.079}
GASES = ["CO", "H2", "CO2", "CH4", "N2"]

# ---- design basis (D-002, D-003) ---------------------------------------------------------------
PRODUCT = 60000.0                      # kg/h glacial acetic acid stream, ASSUMED (D-002)
MEOH_FEED_X = {"CH3OH": 0.99911105, "H2O": 0.00088895}   # methanol-1 S18 (Grade AA design target)
CO_FEED_X = {"CO": 0.985, "N2": 0.010, "CH4": 0.002, "H2": 0.003}   # ASSUMED (D-005)

# ---- by-products (D-004): US 6,140,535 Examples 1-5 report CO2 0.63-0.98 % and CH4 0.81-1.02 %
# of the carbonylation rate; the mid values are used.
R_WGS = 0.008                          # CO + H2O -> CO2 + H2, per mol carbonylation
R_CH4 = 0.009                          # CH3OH + H2 -> CH4 + H2O, per mol carbonylation
PROP_PPM = 500e-6                      # propionic acid formed, kg per kg product (D-004)
PROP_TO_PRODUCT = 0.10                 # fraction of it leaving with the product (D-009)
HEAVY_ACID_PER_PROP = 2.0              # kg acetic acid per kg propionic acid in the heavy ends (D-009)

# ---- off-gas (D-007) ---------------------------------------------------------------------------
Y_CO_NC = 0.45                         # CO mole fraction of the scrubbed off-gas, non-condensable basis
Y_MEOH_OFF = 0.003                     # methanol slip of the methanol scrubber, mole fraction
Y_MEI_OFF = 20e-6                      # methyl iodide slip, mole fraction
HP_SHARE = 0.70                        # share of the non-condensables leaving by the HP vent
HP_VENT_COND = {"CH3I": 0.03, "MEOAC": 0.01, "CH3OH": 0.003}      # mole fractions of the HP vent
LP_VENT_COND = {"CH3I": 0.08, "MEOAC": 0.04, "H2O": 0.01, "CH3COOH": 0.005, "CH3OH": 0.01}

# ---- reaction loop (D-003, D-006) --------------------------------------------------------------
W_REACTOR = {"H2O": 0.06, "CH3I": 0.08, "MEOAC": 0.15, "CH3OH": 0.003}   # reactor liquid, mass fr.
FLASH_VAP = {"CH3I": 0.90, "MEOAC": 0.75, "H2O": 0.50, "CH3OH": 0.80, "CH3COOH": 0.25,
             "C2H5COOH": 0.20}         # fraction of the reactor liquid flashed (D-006)
# acetic acid recycled, as a fraction of the acid leaving the plant (product + heavy ends)
ACID_C201_TOP, ACID_C201_BOT, ACID_C202_TOP = 0.03, 0.10, 0.08
C201_TOP_WATER = 0.60                  # fraction of the flash-vapour water taken overhead in C-201
DECANT_HEAVY = {"CH3I": 0.97, "MEOAC": 0.50, "H2O": 0.03, "CH3COOH": 0.30, "CH3OH": 0.30}

# ---- energy shortcut data (D-008), kJ/kg; reference: liquid at 298.15 K ------------------------
LAT = {"CH3COOH": 395, "H2O": 2257, "CH3OH": 1100, "CH3I": 192, "MEOAC": 409, "C2H5COOH": 420}
CPL = {"CH3COOH": 2.05, "H2O": 4.18, "CH3OH": 2.53, "CH3I": 0.58, "MEOAC": 1.92, "C2H5COOH": 2.15}
CPG = {"CO": 1.04, "H2": 14.3, "CO2": 0.85, "CH4": 2.2, "N2": 1.04}
DH = {"carb": -134.6e3, "wgs": 2.8e3, "ch4": -121.2e3, "prop": -201.7e3}  # kJ/kmol, liquid basis
REFLUX = {"C201": 1.0, "C202": 3.0, "C203": 1.0}   # mass reflux ratios, ASSUMED (D-008)
T = {"reactor": 463.15, "flash": 413.15, "c201_side": 403.15, "c201_bot": 418.15,
     "c202_bot": 413.15, "cold": 313.15, "c203_top": 391.15, "c203_bot": 423.15}
P_REACTOR, P_FLASH = 2900.0, 250.0     # kPa(a)
ETA_PUMP = 0.65


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def kmol_to_kg(d):
    return {k: v * M[k] for k, v in d.items()}


def kg_to_kmol(d):
    return {k: v / M[k] for k, v in d.items()}


def balance():
    # ---- overall: extents, feeds, product, off-gas (iterated on the product water) ------------
    prop_formed_kg = PROP_PPM * PRODUCT
    xi4 = prop_formed_kg / M["C2H5COOH"]
    prop_prod = PROP_TO_PRODUCT * prop_formed_kg
    prop_heavy = prop_formed_kg - prop_prod
    acid_heavy = HEAVY_ACID_PER_PROP * prop_heavy
    water_prod = 30.0
    for _ in range(50):
        acid_prod = PRODUCT - water_prod - prop_prod
        xi1 = (acid_prod + acid_heavy) / M["CH3COOH"] + xi4
        xi2, xi3 = R_WGS * xi1, R_CH4 * xi1
        f_co = (xi1 + xi2 + xi4) / CO_FEED_X["CO"]
        for _ in range(50):
            nc = {"N2": CO_FEED_X["N2"] * f_co, "CH4": CO_FEED_X["CH4"] * f_co + xi3, "CO2": xi2,
                  "H2": CO_FEED_X["H2"] * f_co + xi2 - xi3 - 2 * xi4}
            nc["CO"] = Y_CO_NC / (1 - Y_CO_NC) * sum(nc.values())
            f_co = (xi1 + xi2 + xi4 + nc["CO"]) / CO_FEED_X["CO"]
        g_off = sum(nc.values()) / (1 - Y_MEOH_OFF - Y_MEI_OFF)
        meoh_slip, mei_slip = Y_MEOH_OFF * g_off, Y_MEI_OFF * g_off
        f_meoh = (xi1 + xi3 + meoh_slip) / MEOH_FEED_X["CH3OH"]
        water_new = (f_meoh * MEOH_FEED_X["H2O"] - xi2 + xi3 + xi4) * M["H2O"]
        if abs(water_new - water_prod) < 1e-9:
            break
        water_prod = water_new
    assert nc["H2"] > 0, "hydrogen balance infeasible: raise the H2 of the CO feed"
    s = {}
    s["S01"] = {k: v * f_meoh for k, v in MEOH_FEED_X.items()}
    s["S03"] = {k: v * f_co for k, v in CO_FEED_X.items()}
    s["S04"] = {"CH3I": mei_slip}
    s["S21"] = kg_to_kmol({"CH3COOH": acid_prod, "H2O": water_prod, "C2H5COOH": prop_prod})
    s["S22"] = kg_to_kmol({"CH3COOH": acid_heavy, "C2H5COOH": prop_heavy})
    s["S23"] = add(nc, {"CH3OH": meoh_slip, "CH3I": mei_slip})

    # ---- reactor outlet (the loop's inventory, D-006) ------------------------------------------
    acid_out_plant = acid_prod + acid_heavy                        # kg/h
    vap_acid = acid_out_plant * (1 + ACID_C201_TOP + ACID_C201_BOT + ACID_C202_TOP)
    acid_reactor = vap_acid / FLASH_VAP["CH3COOH"]
    prop_reactor = prop_formed_kg / FLASH_VAP["C2H5COOH"]
    t_l = (acid_reactor + prop_reactor) / (1 - sum(W_REACTOR.values()))
    liq_kg = {k: w * t_l for k, w in W_REACTOR.items()}
    liq_kg.update({"CH3COOH": acid_reactor, "C2H5COOH": prop_reactor})
    liq = kg_to_kmol(liq_kg)                                       # reactor liquid, kmol/h
    hp_nc = {k: HP_SHARE * v for k, v in nc.items()}
    lp_nc = {k: (1 - HP_SHARE) * v for k, v in nc.items()}
    n_hp = sum(hp_nc.values()) / (1 - sum(HP_VENT_COND.values()))
    s["S08"] = add(hp_nc, {k: y * n_hp for k, y in HP_VENT_COND.items()})
    # V-101 liquid = reactor liquid (inventory W_REACTOR) + the dissolved LP-route gases
    s["S09"] = add(liq, lp_nc)
    s["S07"] = add(s["S08"], s["S09"])
    # ---- flash V-102 ---------------------------------------------------------------------------
    s["S10"] = add({k: FLASH_VAP[k] * v for k, v in liq.items()}, lp_nc)
    s["S11"] = {k: (1 - FLASH_VAP[k]) * v for k, v in liq.items()}
    # ---- light-ends column C-201 ---------------------------------------------------------------
    v = s["S10"]
    top = {k: v[k] for k in GASES + ["CH3I", "MEOAC", "CH3OH"]}
    top["H2O"] = C201_TOP_WATER * v["H2O"]
    top["CH3COOH"] = ACID_C201_TOP * acid_out_plant / M["CH3COOH"]
    bot = {"CH3COOH": ACID_C201_BOT * acid_out_plant / M["CH3COOH"]}
    side = {"H2O": v["H2O"] - top["H2O"], "C2H5COOH": v["C2H5COOH"],
            "CH3COOH": v["CH3COOH"] - top["CH3COOH"] - bot["CH3COOH"]}
    s["S13"], s["S14"], s["S15"] = top, side, bot
    # ---- decanter V-201 ------------------------------------------------------------------------
    n_lp = sum(lp_nc.values()) / (1 - sum(LP_VENT_COND.values()))
    s["S16"] = add(lp_nc, {k: y * n_lp for k, y in LP_VENT_COND.items()})
    rest = {k: top[k] - s["S16"].get(k, 0.0) for k in top if k not in GASES}
    assert min(rest.values()) > 0
    s["S17"] = {k: DECANT_HEAVY[k] * x for k, x in rest.items()}
    s["S18"] = {k: (1 - DECANT_HEAVY[k]) * x for k, x in rest.items()}
    # ---- drying column C-202 and heavy-ends column C-203 ---------------------------------------
    s["S19"] = {"H2O": side["H2O"] - s["S21"]["H2O"],
                "CH3COOH": ACID_C202_TOP * acid_out_plant / M["CH3COOH"]}
    assert s["S19"]["H2O"] > 0
    s["S20"] = {k: side[k] - s["S19"].get(k, 0.0) for k in side}
    # ---- scrubber T-101 (fed with the methanol feed, S02 = S01) --------------------------------
    s["S02"] = dict(s["S01"])
    s["S05"] = {k: x - s["S23"].get(k, 0.0) for k, x in add(s["S02"], s["S08"], s["S16"]).items()}
    s["S05"] = {k: x for k, x in s["S05"].items() if x > 1e-12}
    s["S12"] = dict(s["S11"])
    # ---- mixer and reactor (cheme recalculates both) -------------------------------------------
    s["S06"] = add(s["S03"], s["S04"], s["S05"], s["S12"], s["S15"], s["S17"], s["S18"], s["S19"])
    xi = {"CARB": xi1, "WGS": xi2, "MEOH_CH4": xi3, "PROP": xi4}
    conv = {"CARB": xi1 / s["S06"]["CH3OH"], "MEOH_CH4": xi3 / s["S06"]["CH3OH"],
            "WGS": xi2 / s["S06"]["CO"], "PROP": xi4 / s["S06"]["CO"]}
    stoich = {"CARB": {"CH3OH": -1, "CO": -1, "CH3COOH": 1},
              "WGS": {"CO": -1, "H2O": -1, "CO2": 1, "H2": 1},
              "MEOH_CH4": {"CH3OH": -1, "H2": -1, "CH4": 1, "H2O": 1},
              "PROP": {"CH3COOH": -1, "CO": -1, "H2": -2, "C2H5COOH": 1, "H2O": 1}}
    out = dict(s["S06"])
    for r, nu in stoich.items():
        for k, c in nu.items():
            out[k] = out.get(k, 0.0) + c * xi[r]
    for k in set(out) | set(s["S07"]):
        assert abs(out.get(k, 0) - s["S07"].get(k, 0)) < 1e-6 * max(1, out.get(k, 0)), k
    return s, xi, conv, nc


def enthalpy(kmol, t, vapour=()):
    """kJ/h relative to liquid (gases: gas) at 298.15 K; components in `vapour` as vapour."""
    h = 0.0
    for k, n in kmol.items():
        kg = n * M[k]
        if k in GASES:
            h += kg * CPG[k] * (t - 298.15)
        else:
            h += kg * (CPL[k] * (t - 298.15) + (LAT[k] if k in vapour else 0.0))
    return h


def pump_kw(kmol, dp_kpa, rho=1000.0):
    kg = sum(n * M[k] for k, n in kmol.items() if k not in GASES)
    return kg / 3600 / rho * dp_kpa / ETA_PUMP


def duties(s, xi):
    q = {}
    allv = tuple(LAT)
    qr = -(xi["CARB"] * DH["carb"] + xi["WGS"] * DH["wgs"] + xi["MEOH_CH4"] * DH["ch4"]
           + xi["PROP"] * DH["prop"])
    h_in = (enthalpy(s["S03"], T["cold"]) + enthalpy(s["S04"], T["cold"]) + enthalpy(s["S05"], T["cold"])
            + enthalpy(s["S12"], T["flash"]) + enthalpy(s["S15"], T["c201_bot"])
            + enthalpy(s["S17"], T["cold"]) + enthalpy(s["S18"], T["cold"]) + enthalpy(s["S19"], T["cold"]))
    # reactor R-101 (with HP vent condenser) and flash V-102 separately (review 2026-10-28 #1):
    # the V-101 liquid S09 leaves the reactor at reactor temperature and is flashed to 413 K
    h_s09 = enthalpy(s["S09"], T["reactor"])
    h_flash_out = enthalpy(s["S10"], T["flash"], allv) + enthalpy(s["S11"], T["flash"])
    q["R101_heat_removed"] = (qr + h_in - enthalpy(s["S08"], T["cold"]) - h_s09) / 3600
    # the specified flash split is not adiabatic: E-102 heats the flash with reactor heat (D-014)
    q["V102_heater"] = (h_flash_out - h_s09) / 3600
    q["R101_cooling"] = q["R101_heat_removed"] - q["V102_heater"]   # reactor cooler to CW, kW
    lo, hi = 298.15, T["reactor"]                            # mixer M101 outlet S06 (review #4)
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if enthalpy(s["S06"], mid) < h_in else (lo, mid)
    q["T_S06_K"] = (lo + hi) / 2
    q["reaction_heat"] = qr / 3600
    q["flash_vapour_enthalpy"] = enthalpy(s["S10"], T["flash"], allv) / 3600

    def latent(d):
        return sum(n * M[k] * LAT[k] for k, n in d.items() if k in LAT)
    # C-201: condenser = (1 + R) x overhead latent + subcooling to the decanter; reboiler closes it
    cond1 = (1 + REFLUX["C201"]) * latent(s["S13"]) + (enthalpy(s["S13"], T["flash"]) - enthalpy(s["S13"], T["cold"]))
    reb1 = cond1 + enthalpy(s["S13"], T["cold"]) + enthalpy(s["S14"], T["c201_side"]) \
        + enthalpy(s["S15"], T["c201_bot"]) - enthalpy(s["S10"], T["flash"], allv)
    q["C201_condenser"], q["C201_reboiler"] = cond1 / 3600, max(reb1, 0.0) / 3600
    q["C201_reboiler_raw"] = reb1 / 3600
    cond2 = (1 + REFLUX["C202"]) * latent(s["S19"])
    reb2 = cond2 + enthalpy(s["S19"], T["cold"]) + enthalpy(s["S20"], T["c202_bot"]) - enthalpy(s["S14"], T["c201_side"])
    q["C202_condenser"], q["C202_reboiler"] = (cond2 + enthalpy(s["S19"], T["c201_side"]) - enthalpy(s["S19"], T["cold"])) / 3600, reb2 / 3600
    cond3 = (1 + REFLUX["C203"]) * latent(s["S21"]) + enthalpy(s["S21"], T["c203_top"]) - enthalpy(s["S21"], T["cold"])
    reb3 = cond3 + enthalpy(s["S21"], T["cold"]) + enthalpy(s["S22"], T["c203_bot"]) - enthalpy(s["S20"], T["c202_bot"])
    q["C203_condenser"], q["C203_reboiler"] = cond3 / 3600, reb3 / 3600
    # pumps (D-010): to the reactor 2900 kPa(a); refluxes 300 kPa; product to 400 kPa(a)
    q["P101"] = pump_kw(s["S01"], P_REACTOR - 100, 790)
    q["P102"] = pump_kw(s["S11"], P_REACTOR - P_FLASH, 1050)
    q["C201_pumps"] = pump_kw(add(s["S15"], s["S17"], s["S18"]), P_REACTOR - 200) \
        + pump_kw(s["S13"], 300) * REFLUX["C201"]
    q["C202_pumps"] = pump_kw(s["S19"], P_REACTOR - 200) + pump_kw(s["S19"], 300) * REFLUX["C202"] \
        + pump_kw(s["S20"], 300)
    q["C203_pumps"] = pump_kw(s["S21"], 300) * (1 + REFLUX["C203"]) + pump_kw(s["S22"], 300)
    return q


def fmt_comp(d):
    n = sum(d.values())
    return "{" + ", ".join(f"{k}: {v / n:.8g}" for k, v in d.items() if v / n > 1e-12) + "}"


def main():
    s, xi, conv, nc = balance()
    q = duties(s, xi)
    if "--yaml" in sys.argv:
        for sid in sorted(s):
            kg = sum(kmol_to_kg(s[sid]).values())
            print(f"{sid}: flow {kg:.1f} kg/h, mole_fraction {fmt_comp(s[sid])}")
        return
    print("extents kmol/h:", {k: round(v, 4) for k, v in xi.items()})
    print("conversions:", {k: round(v, 9) for k, v in conv.items()})
    for sid in sorted(s):
        kg = kmol_to_kg(s[sid])
        print(f"{sid}: {sum(kg.values()):12.1f} kg/h  {sum(s[sid].values()):10.3f} kmol/h  "
              + ", ".join(f"{k} {v:.1f}" for k, v in kg.items()))
    fin = sum(kmol_to_kg(s[x]).values() for x in ("S01", "S03", "S04")) if False else \
        sum(sum(kmol_to_kg(s[x]).values()) for x in ("S01", "S03", "S04"))
    fout = sum(sum(kmol_to_kg(s[x]).values()) for x in ("S21", "S22", "S23"))
    print(f"overall in {fin:.2f} out {fout:.2f} kg/h")
    co_yield = xi["CARB"] / s["S03"]["CO"]
    meoh_yield = xi["CARB"] / s["S01"]["CH3OH"]
    print(f"yield on CO {co_yield:.4f}, on methanol {meoh_yield:.4f}")
    print("water in product ppm(wt):", round(1e6 * s["S21"]["H2O"] * M["H2O"] / PRODUCT))
    for k, v in q.items():
        print(f"{k}: {v:.1f} K" if k.startswith("T_") else f"{k}: {v:.0f} kW")


if __name__ == "__main__":
    main()
