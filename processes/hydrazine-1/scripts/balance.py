"""Concept mass balance of hydrazine-1 (peroxide / PCUK process, MEK azine route).

Provenance only: it derives the stream values entered as `assumed` in process/flowsheet.yaml
from the design decisions in DESIGN.md (D-002 to D-012). It prints every separator and boundary
stream (kg/h, mass fractions) and the utility duties (kW). Run: cheme run scripts/balance.py
Not rerun over the flowsheet; cheme process propagate calculates mixers and reactors.
"""

MW = {
    "H2O2": 34.014, "H2O": 18.015, "NH3": 17.031, "MEK": 72.107, "AZN": 140.230,
    "BUOH": 74.123, "O2": 31.998, "N2": 28.014, "N2H4": 32.046, "PYR": 140.230,
    "ACAM": 59.068, "ACOH": 60.052, "NA2HPO4": 141.958,
}

# D-002 capacity: 2000 kg/h hydrazine hydrate product, 64.0 wt% N2H4 (= N2H4.H2O)
PRODUCT_KG_H = 2000.0
W_N2H4_PRODUCT = 0.640
# D-004 azine synthesis, per kmol H2O2 converted (H2O2 conversion complete, ASSUMED):
#   azine 0.85 (AZINE), 2-butanol 0.03 (BUTANOL, 2 H2O2 each), O2 0.045 (DECOMP, 2 H2O2 each)
S_AZN, S_BUOH, S_O2 = 0.85, 0.03, 0.045
assert abs(S_AZN + 2 * S_BUOH + 2 * S_O2 - 1.0) < 1e-12
# D-003 reactor inlet ratios per kmol H2O2 (US 6,562,311 / US 6,605,265: 1.5-4 preferred)
R_MEK, R_NH3 = 2.2, 2.5
# D-003 H2O2 70 wt% (US 6,605,265 Ex. 1)
W_H2O2_FEED = 0.70
# D-005 working solution: 11 kg circulated per kg H2O2 (US 6,605,265 Ex. 1); acetic acid
# make-up 60 kg and Na2HPO4 3 kg per 1000 kg H2O2 (same example); regenerated solution
# 45 wt% acetamide, 500 ppm Na2HPO4 (ASSUMED)
WS_PER_H2O2 = 11.0
ACOH_PER_H2O2, PHOS_PER_H2O2 = 0.060, 0.003
W_ACAM_WS, W_PHOS_WS = 0.45, 0.0005
# D-007 hydrolysis: 0.5 % of the azine isomerises to pyrazolines (ASSUMED); bottoms 30 wt%
# hydrazine hydrate (US 6,562,311: typically 30 %, up to 45 %)
F_PYR = 0.005
W_HH_BOTTOMS = 0.30
# D-006/D-007 phase and column splits (ASSUMED)
ORG_W_H2O, ORG_W_NH3 = 0.03, 0.005      # water and NH3 dissolved in the azine phase
AQ_W_MEK = 0.01                         # MEK dissolved in the aqueous working solution
VENT_Y_NH3, VENT_Y_MEK = 0.01, 0.005    # after the lumped vent condenser/scrubber
# D-015 N2 sweep of the R-101/V-101 headspaces: O2 at most 8 mol% in the vent (ASSUMED, about
# 3 points below a limiting oxygen concentration of about 11 vol% for MEK with N2; to be
# sourced, I-04)
VENT_Y_O2_MAX = 0.08
WW_W_MEK, WW_W_NH3 = 0.001, 0.0001      # C202 bottoms
BLEED_W = {"BUOH": 0.85, "MEK": 0.10, "H2O": 0.05}   # 2-butanol side draw of C301
MEK_TOP_W_H2O = 0.11                    # C401 top: MEK-water near the azeotrope
HEAVY_W_PYR = 0.5                       # pyrazoline purge, rest water
WSP_W_H2O = 0.5                         # working-solution purge, rest acetamide + phosphate


def mass(d):
    return {k: v * MW[k] for k, v in d.items() if abs(v) > 1e-12}


SHOWN = {}  # the streams show() printed, by id (balance-output contract)


def show(name, d_kmol):
    m = mass(d_kmol)
    tot = sum(m.values())
    SHOWN[name.split()[0]] = {"flow": {"value": tot, "basis": "mass"},
                              "composition": {"values": {k: v / tot for k, v in m.items()},
                                              "basis": "mass_fraction"}}
    print(f"{name}: {tot:.3f} kg/h  " + ", ".join(f"{k}: {v / tot:.6f}" for k, v in m.items()))
    return tot


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def from_mass(kg, w):
    return {k: kg * f / MW[k] for k, f in w.items()}


def main():
    n2h4 = PRODUCT_KG_H * W_N2H4_PRODUCT / MW["N2H4"]
    h2o_prod = PRODUCT_KG_H * (1 - W_N2H4_PRODUCT) / MW["H2O"]
    azn_hyd = n2h4 / (1 - F_PYR)          # azine fed to hydrolysis
    pyr = azn_hyd * F_PYR
    h2o2 = azn_hyd / S_AZN                # all azine formed reaches hydrolysis (D-006)
    buoh = S_BUOH * h2o2
    o2 = S_O2 * h2o2
    n2 = buoh
    acoh = ACOH_PER_H2O2 * h2o2 * MW["H2O2"] / MW["ACOH"]
    phos_kg = PHOS_PER_H2O2 * h2o2 * MW["H2O2"]

    # --- feeds
    s01 = {"H2O2": h2o2, "H2O": h2o2 * MW["H2O2"] * (1 / W_H2O2_FEED - 1) / MW["H2O"]}
    s10 = {"ACOH": acoh}
    s11 = {"NA2HPO4": phos_kg / MW["NA2HPO4"]}

    # --- reactor R101 extents (selectivity on H2O2)
    e_azn, e_bu, e_dec = S_AZN * h2o2, buoh, o2
    nh3_react = 2 * e_azn + 2 * e_bu
    mek_react = 2 * e_azn + e_bu
    h2o_made = 4 * e_azn + 4 * e_bu + 2 * e_dec

    # --- hydrolysis block (C401, C402)
    mek_hyd = 2 * n2h4
    s41_mek = mek_hyd                      # all MEK from hydrolysis overhead
    s41 = {"MEK": s41_mek}
    s41["H2O"] = s41_mek * MW["MEK"] * MEK_TOP_W_H2O / (1 - MEK_TOP_W_H2O) / MW["H2O"]
    s46 = {"PYR": pyr}
    s46["H2O"] = pyr * MW["PYR"] * (1 - HEAVY_W_PYR) / HEAVY_W_PYR / MW["H2O"]
    hh_kg = n2h4 * (MW["N2H4"] + MW["H2O"])   # hydrazine hydrate N2H4.H2O
    s47_kg = hh_kg / W_HH_BOTTOMS
    s47 = {"N2H4": n2h4, "H2O": (s47_kg - n2h4 * MW["N2H4"]) / MW["H2O"]}
    s48 = {"N2H4": n2h4, "H2O": h2o_prod}
    s43 = {"H2O": s47["H2O"] - h2o_prod}   # C402 overhead water to hydrolysis
    # water needed at the hydrolysis inlet = bottoms + consumed + overhead + purge
    h2o_in_hyd = s47["H2O"] + 2 * n2h4 + s41["H2O"] + s46["H2O"]
    s40 = {"H2O": h2o_in_hyd - s43["H2O"]}  # demineralised make-up water

    # --- vent (V101), N2 sweep S04 sized on the O2 limit (D-015)
    vent_tot = o2 / VENT_Y_O2_MAX
    s04 = {"N2": vent_tot * (1 - VENT_Y_NH3 - VENT_Y_MEK) - o2 - n2}
    s07 = {"O2": o2, "N2": n2 + s04["N2"], "NH3": VENT_Y_NH3 * vent_tot,
           "MEK": VENT_Y_MEK * vent_tot}

    # --- working solution (C201 bottoms recycle S20, purge S15)
    ws_kg = WS_PER_H2O2 * h2o2 * MW["H2O2"]
    s20 = from_mass(ws_kg, {"ACAM": W_ACAM_WS, "NA2HPO4": W_PHOS_WS,
                            "H2O": 1 - W_ACAM_WS - W_PHOS_WS})
    acam_p = acoh                           # acetamide formed from the make-up leaves in S15
    s15 = {"ACAM": acam_p, "NA2HPO4": s11["NA2HPO4"]}
    dry = acam_p * MW["ACAM"] + phos_kg
    s15["H2O"] = dry * WSP_W_H2O / (1 - WSP_W_H2O) / MW["H2O"]

    # --- 2-butanol bleed S33 (C301 side draw) removes the 2-butanol formed
    s33_kg = buoh * MW["BUOH"] / BLEED_W["BUOH"]
    s33 = from_mass(s33_kg, BLEED_W)

    # --- MEK make-up S03 closes the MEK balance; NH3 feed S02 closes the NH3 balance.
    # WW S24 composition depends on its water flow, solved below by iteration.
    mek_in_target = R_MEK * h2o2
    nh3_in_target = R_NH3 * h2o2
    s24_h2o = 5000.0 / MW["H2O"]
    for _ in range(100):
        s24_kg = s24_h2o * MW["H2O"] / (1 - WW_W_MEK - WW_W_NH3)
        s24 = {"H2O": s24_h2o, "MEK": s24_kg * WW_W_MEK / MW["MEK"],
               "NH3": s24_kg * WW_W_NH3 / MW["NH3"]}
        mek_loss = s07["MEK"] + s33["MEK"] + s24["MEK"]
        s03 = {"MEK": mek_react - mek_hyd + mek_loss}
        nh3_loss = s07["NH3"] + s24["NH3"]
        s02 = {"NH3": nh3_react + acoh + nh3_loss}
        # organic phase S08: azine, excess MEK (all but the dissolved MEK), 2-butanol, water, NH3
        mek_out_r = mek_in_target - mek_react
        # aqueous phase S09 MEK: AQ_W_MEK of its mass; solve with S09 mass (iterate inside)
        nh3_out_r = nh3_in_target - nh3_react
        # S09: working solution + water not in organic phase + NH3 not in org/vent + MEK
        # Everything recycled must balance: water leaving the loop = S24 + S15 + S33 + S07(0)
        # Water entering R101 inlet: S01 + S20 + S41 + S31 + S23 ; made h2o_made
        # C301 top recycle S31 carries the organic phase's MEK, NH3 and water minus the bleed.
        org_azn = e_azn
        org_mek_guess = mek_out_r * 0.9
        for _ in range(100):
            org_dry = org_azn * MW["AZN"] + org_mek_guess * MW["MEK"] + buoh * MW["BUOH"]
            org_kg = org_dry / (1 - ORG_W_H2O - ORG_W_NH3)
            s08 = {"AZN": org_azn, "MEK": org_mek_guess, "BUOH": buoh,
                   "H2O": org_kg * ORG_W_H2O / MW["H2O"], "NH3": org_kg * ORG_W_NH3 / MW["NH3"]}
            aq_mek = mek_out_r - org_mek_guess - s07["MEK"]
            aq_nh3 = nh3_out_r - s08["NH3"] - s07["NH3"]
            # aqueous water from the overall water balance of the reactor
            # R101 outlet water = inlet water + made; inlet water depends on S31, S23 water (0)
            s31 = {"MEK": s08["MEK"] - s33["MEK"], "NH3": s08["NH3"],
                   "H2O": s08["H2O"] - s33["H2O"]}
            s32 = {"AZN": org_azn}
            h2o_in_r = s01["H2O"] + s20["H2O"] + s41["H2O"] + s31["H2O"]
            aq_h2o = h2o_in_r + h2o_made - s08["H2O"]
            s09 = {"ACAM": s20["ACAM"], "NA2HPO4": s20["NA2HPO4"], "H2O": aq_h2o,
                   "NH3": aq_nh3, "MEK": aq_mek}
            s09_kg = sum(mass(s09).values())
            new_aq_mek = AQ_W_MEK * s09_kg / MW["MEK"]
            org_mek_guess = mek_out_r - new_aq_mek - s07["MEK"]
            if abs(new_aq_mek - aq_mek) < 1e-10:
                break
        # C201: S12 = S09 + amidation (ACOH + NH3 -> ACAM + H2O) + phosphate make-up
        s12 = add(s09, {"NA2HPO4": s11["NA2HPO4"], "ACAM": acoh, "H2O": acoh, "NH3": -acoh})
        # C201 top S13 = S12 - S20 - S15 (water, NH3, MEK)
        s13 = {k: s12.get(k, 0) - s20.get(k, 0) - s15.get(k, 0) for k in s12}
        # C202: top NH3 + MEK recycle S23, bottoms S24
        new_s24_h2o = s13["H2O"]
        if abs(new_s24_h2o - s24_h2o) < 1e-9:
            break
        s24_h2o = new_s24_h2o
    s23 = {"NH3": s13["NH3"] - s24["NH3"], "MEK": s13["MEK"] - s24["MEK"]}
    s05 = add(s01, s02, s03, s04, s20, s23, s31, s41)

    print("== feeds and recycles")
    for n, d in [("S01 H2O2 70 wt%", s01), ("S02 NH3", s02), ("S03 MEK make-up", s03), ("S04 N2 sweep", s04),
                 ("S10 acetic acid", s10), ("S11 Na2HPO4", s11), ("S40 make-up water", s40),
                 ("S20 working solution recycle", s20), ("S23 NH3/MEK recycle", s23),
                 ("S31 MEK recycle (C301 top)", s31), ("S41 MEK from hydrolysis", s41),
                 ("S43 water recycle (C402 top)", s43), ("S05 reactor inlet (check)", s05)]:
        show(n, d)
    print("== separator outlets")
    for n, d in [("S07 vent", s07), ("S08 azine phase", s08), ("S09 aqueous phase", s09),
                 ("S12 (check)", s12), ("S13 C201 top", s13), ("S15 WS purge", s15),
                 ("S24 waste water", s24), ("S32 azine", s32), ("S33 2-butanol bleed", s33),
                 ("S46 pyrazoline purge", s46), ("S47 dilute hydrate", s47),
                 ("S48 product", s48)]:
        show(n, d)
    print(f"reactor inlet MEK/H2O2 {s05['MEK'] / h2o2:.3f}, NH3/H2O2 {s05['NH3'] / h2o2:.3f}")
    print(f"hydrolysis water/azine {h2o_in_hyd / azn_hyd:.2f}")

    # --- boundary closure
    ins = [s01, s02, s03, s04, s10, s11, s40]
    outs = [s07, s15, s24, s33, s46, s48]
    m_in = sum(sum(mass(d).values()) for d in ins)
    m_out = sum(sum(mass(d).values()) for d in outs)
    print(f"boundary in {m_in:.3f} kg/h, out {m_out:.3f} kg/h, diff {m_in - m_out:.4f}")

    # --- duties (D-010), kW
    h2o2_kg = h2o2 * MW["H2O2"]
    q = {}
    # C201: 10.5 t/h of 18 bar(a) steam per 1 t/h H2O2 (US 6,605,265 Ex. 1); latent heat at
    # 1800 kPa(a) 1912 kJ/kg (IAPWS-IF97)
    regen = 10.5 * h2o2_kg * 1912 / 3600
    # of which the heater E-201 (R201): S12 heated 323 -> 423 K at 3.4 kJ/(kg K) (ASSUMED)
    q["Q_E201_steam"] = sum(mass(s12).values()) * 3.4 * 100 / 3600
    q["Q_C201_steam"] = regen - q["Q_E201_steam"]
    q["Q_C201_cw"] = regen
    # R101: H2O2 + 2 NH3(g) -> N2H4(l) + 2 H2O(l) -241.5 kJ/mol (NIST WebBook dHf), azine
    # condensation heat neglected; DECOMP -98.2 kJ/mol H2O2; BUTANOL path counted like the azine
    dh_azn, dh_dec = 241.5, 98.2
    q["Q_R101_cw"] = (e_azn * dh_azn + e_bu * dh_azn + 2 * e_dec * dh_dec) / 3.6
    # C301: top vapour (excess MEK, 2-butanol, water, NH3) x (1 + R), R = 1.5; latent heats MEK
    # 434, 2-butanol 551, water 2257, NH3 1370 kJ/kg at 1 atm (ASSUMED round values)
    top = mass(add(s31, s33))
    lat = {"MEK": 434, "BUOH": 551, "H2O": 2257, "NH3": 1370}
    q["Q_C301_steam"] = sum(top[k] * lat[k] for k in top) * 2.5 / 3600
    q["Q_C301_cw"] = q["Q_C301_steam"]
    # C401: top MEK + water at about 9 bar x (1 + R), R = 1 (MEK 330, water 2030 kJ/kg), plus
    # heating the water feed 373 -> 458 K at 4.3 kJ/kg K (ASSUMED)
    t41 = mass(s41)
    q["Q_C401_steam"] = ((t41["MEK"] * 330 + t41["H2O"] * 2030) * 2.0
                         + mass({"H2O": h2o_in_hyd})["H2O"] * 4.3 * 85) / 3600
    q["Q_C401_cw"] = (t41["MEK"] * 330 + t41["H2O"] * 2030) * 2.0 / 3600
    # C402: overhead water x (1 + R), R = 0.3, minus the flash of the 458 K feed to 383 K
    s47_m = sum(mass(s47).values())
    q["Q_C402_steam"] = (mass(s43)["H2O"] * 2257 * 1.3 - s47_m * 4.0 * 75) / 3600
    q["Q_C402_cw"] = mass(s43)["H2O"] * 2257 * 1.3 / 3600
    # C202: stripping steam 0.2 kg per kg feed water (latent 2200 kJ/kg) plus NH3 vaporisation
    q["Q_C202_steam"] = (mass(s13)["H2O"] * 0.2 * 2200 + mass(s23)["NH3"] * 1370) / 3600
    q["Q_C202_cw"] = q["Q_C202_steam"] - mass(s23)["NH3"] * 1370 / 3600
    for k, v in q.items():
        print(f"{k}: {v:.0f} kW")
    # D-010 high-steam variant of C401 (review 2026-10-28#1): reflux ratio 2.5 instead of 1, plus
    # a hydrolysis heat of 25-75 kJ/mol azine (ASSUMED order of magnitude; endothermic per the
    # route's secondary source, no value read)
    feed_heat = mass({"H2O": h2o_in_hyd})["H2O"] * 4.3 * 85 / 3600
    top_lat = (t41["MEK"] * 330 + t41["H2O"] * 2030) / 3600
    for dh_hyd in (25, 50, 75):
        q_hi = top_lat * 3.5 + feed_heat + azn_hyd * dh_hyd / 3.6
        print(f"Q_C401_steam high variant (R 2.5, hydrolysis {dh_hyd} kJ/mol): {q_hi:.0f} kW")
    # the values process/flowsheet.yaml cites from this script (balance-output contract): the
    # stream flows as show() printed them
    write_balance_output({"design": SHOWN})


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
