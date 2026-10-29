"""Concept mass balance of acetone-1 (cumene to phenol and acetone).

Provenance only: it derives the stream values entered as `assumed` in process/flowsheet.yaml
from the design decisions in DESIGN.md (D-003 to D-012). It prints the boundary and separator
streams (kg/h, mass fractions) and the utility duties (kW). Run: python3 scripts/balance.py
Not rerun over the flowsheet; cheme process propagate calculates mixers and reactors.
"""

MW = {
    "CUM": 120.19, "O2": 31.998, "N2": 28.014, "CHP": 152.19, "DMBA": 136.19, "ACP": 120.15,
    "MEOH": 32.042, "PHEN": 94.111, "ACET": 58.079, "AMS": 118.18, "H2O": 18.015,
    "CUMPH": 212.29, "H2": 2.016, "H2SO4": 98.079, "NAOH": 39.997, "NA2SO4": 142.04,
}

# D-002 capacity: 200 kt/a phenol at 8000 h/a
PHENOL_KG_H = 200e6 / 8000
# D-004 oxidation selectivity per kmol cumene converted (ASSUMED)
S_CHP, S_DMBA, S_ACP = 0.94, 0.05, 0.01
# D-005 cleavage: CHP fully cleaved; DMBA 75 % to AMS, 25 % with phenol to cumylphenol (ASSUMED)
F_AMS, F_CUMPH = 0.75, 0.25
# D-004 oxidate 25 wt% CHP; D-006 concentrate 80 wt% CHP
W_CHP_OXIDATE, W_CHP_CONC = 0.25, 0.80
# D-003 spent air 5 mol% O2 (dry, organics-free); cumene vapour in spent gas 2 mol% (ASSUMED)
Y_O2_SPENT, Y_CUM_SPENT = 0.05, 0.02
# D-010 vent after adsorbers: 35 mg C/Nm3 counted as cumene (BREF LVOC 8.3.1.1)
VOC_MGC_NM3 = 35.0
NM3_PER_KMOL = 22.414
# D-007 acid 102 kg/h of 98 wt% H2SO4; caustic 50 wt% NaOH; wash water 1000 kg/h (ASSUMED)
ACID_KG_H, ACID_W = 102.0, 0.98
NAOH_W = 0.50
WASH_KG_H = 1000.0
# D-008 aqueous from the decanter: 1.5 wt% phenol (BREF 8.3.2.2), 1.0 wt% acetone (ASSUMED)
AQ_PHEN, AQ_ACET = 0.015, 0.010
# D-009 products and losses (ASSUMED)
ACET_PRODUCT_H2O = 0.003      # acetone product water mass fraction
C402_BOTTOMS_ACET = 0.005     # acetone in acetone-column bottoms, mass fraction
TAR_PHEN = 0.05               # phenol in tar, mass fraction
H2_VENT_NM3_PER_T = 1.0       # BREF 8.3.1.4: 0.8-1.2 Nm3/t phenol


def frac(d):
    tot = sum(d.values())
    return tot, {k: v / tot for k, v in d.items() if v > 0}


def show(name, d):
    tot, f = frac(d)
    print(f"{name}: {tot:.3f} kg/h  " + ", ".join(f"{k}: {v:.6f}" for k, v in f.items()))
    return tot


def main():
    # Phenol leaving: product + tar + aqueous losses; solve the cumene converted x by iteration
    x = 280.0
    for _ in range(50):
        chp = S_CHP * x
        dmba = S_DMBA * x
        acp = S_ACP * x
        meoh = S_ACP * x
        phen_made = chp - F_CUMPH * dmba
        cumph = F_CUMPH * dmba
        ams = F_AMS * dmba
        tar_org = cumph * MW["CUMPH"] + acp * MW["ACP"]
        tar = tar_org / (1 - TAR_PHEN)
        # aqueous: Na2SO4 + water; phenol and acetone fractions of the whole
        h2so4 = ACID_KG_H * ACID_W / MW["H2SO4"]
        naoh = 2 * h2so4
        na2so4 = h2so4 * MW["NA2SO4"]
        w_aq = ACID_KG_H * (1 - ACID_W) + naoh * MW["NAOH"] * (1 - NAOH_W) / NAOH_W \
            + 2 * h2so4 * MW["H2O"] + WASH_KG_H
        aq_base = na2so4 + w_aq
        aq_tot = aq_base / (1 - AQ_PHEN - AQ_ACET)
        phen_loss = aq_tot * AQ_PHEN + tar * TAR_PHEN
        x_new = x * PHENOL_KG_H / (phen_made * MW["PHEN"] - phen_loss)
        if abs(x_new - x) < 1e-10:
            break
        x = x_new
    print(f"cumene converted x = {x:.4f} kmol/h")
    o2_used = (S_CHP + 0.5 * S_DMBA + S_ACP) * x
    air = (o2_used * (1 - Y_O2_SPENT)) / (0.21 - Y_O2_SPENT)  # kmol/h
    n2 = 0.79 * air
    o2_out = 0.21 * air - o2_used
    spent_dry = n2 + o2_out
    cum_spent = spent_dry * Y_CUM_SPENT / (1 - Y_CUM_SPENT)
    vent_nm3 = spent_dry * NM3_PER_KMOL
    cum_vent_kg = VOC_MGC_NM3 * vent_nm3 * 1e-6 / (9 * 12.011 / MW["CUM"])
    print(f"air {air:.3f} kmol/h = {air * NM3_PER_KMOL:.0f} Nm3/h; spent air {vent_nm3:.0f} Nm3/h"
          f" = {vent_nm3 / (PHENOL_KG_H / 1000):.0f} Nm3/t phenol")
    show("S02 air", {"N2": n2 * MW["N2"], "O2": 0.21 * air * MW["O2"]})
    spent = {"N2": n2 * MW["N2"], "O2": o2_out * MW["O2"], "CUM": cum_spent * MW["CUM"]}
    show("S06 spent gas", spent)
    show("S08 vent", {"N2": n2 * MW["N2"], "O2": o2_out * MW["O2"], "CUM": cum_vent_kg})
    rec_cum = cum_spent * MW["CUM"] - cum_vent_kg
    print(f"S09 recovered cumene: {rec_cum:.3f} kg/h")

    chp_kg = chp * MW["CHP"]
    oxid_heavy = {"CHP": chp_kg, "DMBA": dmba * MW["DMBA"], "ACP": acp * MW["ACP"],
                  "MEOH": meoh * MW["MEOH"]}
    oxidate_tot = chp_kg / W_CHP_OXIDATE
    cum_oxidate = oxidate_tot - sum(oxid_heavy.values())
    show("S07 oxidate", {"CUM": cum_oxidate, **oxid_heavy})
    conc_tot = chp_kg / W_CHP_CONC
    cum_conc = conc_tot - sum(oxid_heavy.values())
    show("S10 concentrate", {"CUM": cum_conc, **oxid_heavy})
    print(f"S11 recycle cumene: {cum_oxidate - cum_conc:.3f} kg/h")
    # reactor feed cumene: oxidate cumene + converted + spent gas cumene
    cum_feed = cum_oxidate + x * MW["CUM"] + cum_spent * MW["CUM"]
    conv = x * MW["CUM"] / cum_feed
    print(f"R101 cumene feed {cum_feed:.3f} kg/h, conversion per pass {conv:.6f}")
    hyd_cum = cum_conc + ams * MW["CUM"]
    fresh = cum_feed - rec_cum - (cum_oxidate - cum_conc) - hyd_cum
    print(f"S01 fresh cumene: {fresh:.3f} kg/h = {fresh / PHENOL_KG_H:.4f} t/t phenol")
    show("S12 acid", {"H2SO4": ACID_KG_H * ACID_W, "H2O": ACID_KG_H * (1 - ACID_W)})
    show("S14 caustic", {"NAOH": naoh * MW["NAOH"], "H2O": naoh * MW["NAOH"]})
    print(f"S30 wash water: {WASH_KG_H:.3f} kg/h")
    aq = {"H2O": w_aq, "NA2SO4": na2so4, "PHEN": aq_tot * AQ_PHEN, "ACET": aq_tot * AQ_ACET}
    show("S16 aqueous", aq)
    acet_made = chp * MW["ACET"]
    water_rx = dmba * MW["H2O"]
    # organic phase to C401
    org = {"CUM": cum_conc, "PHEN": phen_made * MW["PHEN"] - aq["PHEN"],
           "ACET": acet_made - aq["ACET"], "AMS": ams * MW["AMS"], "ACP": acp * MW["ACP"],
           "CUMPH": cumph * MW["CUMPH"], "MEOH": meoh * MW["MEOH"], "H2O": water_rx}
    show("S17 organic", org)
    top = {"ACET": org["ACET"], "H2O": org["H2O"], "MEOH": org["MEOH"]}
    show("S18 crude acetone", top)
    bot = {k: org[k] for k in ("CUM", "PHEN", "AMS", "ACP", "CUMPH")}
    show("S19 C401 bottoms", bot)
    # C402: product acetone 99.7 %; bottoms water + methanol + 0.5 % acetone
    b_base = top["MEOH"] + top["H2O"]
    # unknown P (product kg/h): water in product 0.003 P; bottoms = (b_base - 0.003P)/(1-0.005)
    p = (top["ACET"] - 0.0) / (1 - ACET_PRODUCT_H2O)
    for _ in range(50):
        b_tot = (b_base - ACET_PRODUCT_H2O * p) / (1 - C402_BOTTOMS_ACET)
        p = (top["ACET"] - C402_BOTTOMS_ACET * b_tot) / (1 - ACET_PRODUCT_H2O)
    acet_prod = show("S20 acetone product", {"ACET": p * (1 - ACET_PRODUCT_H2O),
                                             "H2O": p * ACET_PRODUCT_H2O})
    show("S21 acetone column bottoms", {"H2O": top["H2O"] - p * ACET_PRODUCT_H2O,
                                         "MEOH": top["MEOH"], "ACET": b_tot * C402_BOTTOMS_ACET})
    show("S22 cumene/AMS cut", {"CUM": bot["CUM"], "AMS": bot["AMS"]})
    show("S23 crude phenol", {k: bot[k] for k in ("PHEN", "ACP", "CUMPH")})
    phen_prod = bot["PHEN"] - tar * TAR_PHEN
    print(f"S24 phenol product: {phen_prod:.3f} kg/h")
    show("S25 tar", {"PHEN": tar * TAR_PHEN, "ACP": acp * MW["ACP"], "CUMPH": cumph * MW["CUMPH"]})
    h2_vent = H2_VENT_NM3_PER_T * PHENOL_KG_H / 1000 / NM3_PER_KMOL
    print(f"S26 hydrogen: {(ams + h2_vent) * MW['H2']:.3f} kg/h; S28 H2 vent {h2_vent * MW['H2']:.3f}")
    print(f"S29 hydrogenated cumene: {hyd_cum:.3f} kg/h")
    print(f"acetone/phenol {acet_prod / phen_prod:.4f} t/t; tar {tar / PHENOL_KG_H * 1000:.1f} kg/t")

    # Duties (kW): reaction heats from ideal-gas formation enthalpies (cheme chemistry thermo,
    # CRC/ATcT), main reactions only; utilities anchored to BREF LVOC Table 8.5 (D-011)
    dh_ox = -78.4 - 4.0             # kJ/mol: CUM + O2 -> CHP
    dh_clv = -96.4 - 216.07 + 78.4  # CHP -> PHEN + ACET
    dh_hyd = 4.0 - 118.3            # AMS + H2 -> CUM
    q_ox = -dh_ox * chp * 1000 / 3600
    q_clv = -dh_clv * chp * 1000 / 3600
    q_hyd = -dh_hyd * ams * 1000 / 3600
    # air compressor: isothermal 101.3 -> 600 kPa(a), 75 % isothermal efficiency (ASSUMED)
    import math
    w_k = air / 3600 * 8.314 * 298.15 * math.log(600 / 101.325) / 0.75
    t = PHENOL_KG_H / 1000
    mp = 1.9 * t * 1000 * 1912 / 3600   # 18 bar steam, latent heat 1912 kJ/kg (IAPWS-IF97)
    lp = 0.65 * t * 1000 * 2108 / 3600  # 5 bar steam, latent heat 2108 kJ/kg (IAPWS-IF97)
    power = 190 * t
    print(f"q_ox {q_ox:.0f} kW, q_clv {q_clv:.0f} kW, q_hyd {q_hyd:.0f} kW, K101 {w_k:.0f} kW")
    print(f"MP steam {mp:.0f} kW, LP steam {lp:.0f} kW, power total {power:.0f} kW,"
          f" other power {power - w_k:.0f} kW")


if __name__ == "__main__":
    main()
