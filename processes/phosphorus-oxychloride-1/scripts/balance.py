"""Independent heat and material balance of phosphorus-oxychloride-1 (DESIGN.md D-006).

Run with `cheme run scripts/balance.py` (thermo/chemicals are in cheme-as-code's interpreter).
Prints every stream (kg/h, mole and mass fractions) and every duty (kW) that
process/flowsheet.yaml takes as ASSUMED values with source "scripts/balance.py". Mixers and
the conversion reactors are recalculated by `cheme process propagate --fill`, which checks this
script.

Why a script: no property package of core covers PCl3, POCl3, white phosphorus or the caustic
liquor (core #315, #364), so the vent condensers (Raoult's law with thermo vapour pressures),
the columns (specified splits) and the liquid-phase reaction heats are computed here.

Every number below that is not a molar mass or a thermo property is a design choice: the
decision ids name where DESIGN.md gives the reason and the source.
"""

from thermo import Chemical

# --- components (kg/kmol) ---------------------------------------------------------------------
MW = {
    "P4": 123.895, "CL2": 70.906, "O2": 31.999, "AR": 39.948, "PCL3": 137.333,
    "POCL3": 153.332, "H2O": 18.015, "NAOH": 39.997, "NACL": 58.443,
    "NAOCL": 74.442, "NA2HPO3": 125.958, "NA3PO4": 163.941,
}

# --- design choices ---------------------------------------------------------------------------
PRODUCT_TARGET = 4000.0          # kg/h POCl3 product, D-002 (ASSUMED)
CL2_EXCESS = 0.0005              # molar Cl2 excess over P4 stoichiometry in R-101, D-004
X_O2_R101 = 0.99                 # O2 of the chlorine consumed by PCl3 in R-101, D-004
X_PCL3_R201 = 0.995              # PCl3 conversion per pass in R-201, D-005
O2_EXCESS = 0.05                 # molar O2 excess over the PCl3 reacted in R-201, D-005
T_VENT = 283.15                  # K, vent condensers of R-101 and R-201 (chilled water), D-007
P_VENT = 110.0                   # kPa(a) at the vent condensers, D-010
REC_PCL3 = 0.995                 # PCl3 recovered to the C-301 distillate, D-008
X_DIST_PCL3 = 0.5                # mole fraction PCl3 in the C-301 distillate (recycle), D-008
RESIDUE_FRAC = 0.005             # POCl3 fraction of the C-302 feed purged with the residue, D-008
NAOH_EXCESS = 1.5                # NaOH fed / NaOH consumed in T-401, D-009
NAOH_WT = 0.18                   # wt% NaOH of the scrubbing liquor, D-009
X_SCRUB = 0.9999                 # destruction of PCl3, POCl3 and Cl2 in T-401, D-009
T_STACK = 303.15                 # K, scrubbed gas, water-saturated, D-009
P_STACK = 105.0                  # kPa(a)

# chlor-alkali-1 dry chlorine (its stream S42): mass fractions
CL2_FEED_W = {"CL2": 0.9918815, "O2": 0.008118535}
# asu-1 GOX (its stream S7 / S8): mole fractions
O2_FEED_X = {"O2": 0.997115, "AR": 0.002885}

# liquid-phase reaction enthalpies at 298.15 K from the liquid formation enthalpies of
# chemicals (CRC): PCl3(l) -319.7, POCl3(l) -597.1 kJ/mol; white P(l) +0.62 kJ/mol per P atom
H_PCL3_L, H_POCL3_L, H_P4_L = -319700.0, -597100.0, 4 * 620.0     # kJ/kmol
DH_R1 = 4 * H_PCL3_L - H_P4_L          # P4(l) + 6 Cl2(g) -> 4 PCl3(l), kJ/kmol P4
DH_R2 = H_POCL3_L - H_PCL3_L           # PCl3(l) + 1/2 O2(g) -> POCl3(l), kJ/kmol PCl3

# columns and pumps
R_C301, R_C302 = 3.0, 0.5              # reflux ratios, D-008 (ASSUMED)
CP_LIQ = 0.9                           # kJ/(kg K), PCl3/POCl3 liquids, ASSUMED (D-008)
T_R201_OUT, T_C302_TOP, T_PRODUCT = 323.15, 378.9, 308.15
DT_R201_LOOP = 20.0                    # K across the R-201 circulation cooler E-201, D-005
RHO_LIQ = 1600.0                       # kg/m3, PCl3/POCl3 liquids (thermo ~1550-1650)
DP_PUMP, ETA_PUMP = 300.0, 0.55        # kPa, wire-to-water efficiency, D-010 (ASSUMED)
SCRUB_CIRC_M3H = 20.0                  # m3/h scrubber circulation, D-010 (ASSUMED)
AGITATOR_KW = 11.0                     # R-101 agitator allowance, D-010 (ASSUMED)


def psat_kpa(name, t):
    return Chemical(name, T=t, P=101325).Psat / 1000.0


def hvap(name, t):
    c = Chemical(name, T=t, P=101325)
    return c.Hvap * c.MW / 1000.0          # kJ/kmol


def kg(n):
    return {k: v * MW[k] for k, v in n.items() if v}


def add(*streams):
    out = {}
    for s in streams:
        for k, v in s.items():
            out[k] = out.get(k, 0.0) + v
    return out


def vent_vapour(liquid, noncond, t, p):
    """Raoult: kmol/h of PCl3 and POCl3 that the non-condensables carry at t, p."""
    tot = sum(liquid.get(k, 0.0) for k in ("PCL3", "POCL3"))
    pp = {k: liquid.get(k, 0.0) / tot * psat_kpa(n, t) for k, n in (("PCL3", "PCl3"), ("POCL3", "POCl3"))}
    ratio = noncond / (p - sum(pp.values()))
    return {k: v * ratio for k, v in pp.items()}


def run(p4_kmol):
    # R-101: P4 + 6 Cl2 -> 4 PCl3 (P4 fully converted), then PCl3 + 1/2 O2 -> POCl3
    n_cl2_need = 6 * p4_kmol * (1 + CL2_EXCESS)
    m_cl2_feed = n_cl2_need * MW["CL2"] / CL2_FEED_W["CL2"]
    s2 = {k: m_cl2_feed * w / MW[k] for k, w in CL2_FEED_W.items()}
    s1 = {"P4": p4_kmol}
    o2_r1 = X_O2_R101 * s2["O2"]
    liq = {"PCL3": 4 * p4_kmol - 2 * o2_r1, "POCL3": 2 * o2_r1}
    gas = {"CL2": s2["CL2"] - 6 * p4_kmol, "O2": s2["O2"] - o2_r1}
    vap = vent_vapour(liq, sum(gas.values()), T_VENT, P_VENT)
    s4 = add(gas, vap)                              # vent of R-101
    s3 = {k: liq[k] - vap.get(k, 0.0) for k in liq} # crude PCl3 to M-201
    q_r101 = -(p4_kmol * DH_R1 + o2_r1 * DH_R2) / 3600.0
    # chilled-water vent condenser: vapour held at 308 K saturation condensed down to T_VENT
    vap308 = vent_vapour(liq, sum(gas.values()), 308.15, P_VENT)
    q_v101 = sum((vap308[k] - vap[k]) * hvap(n, T_VENT) for k, n in (("PCL3", "PCl3"), ("POCL3", "POCl3"))) / 3600.0

    # recycle loop M-201 / R-201 / C-301
    s13 = {"PCL3": 0.0, "POCL3": 0.0}
    for _ in range(200):
        s5 = add(s3, s13)
        reacted = X_PCL3_R201 * s5["PCL3"]
        o2_feed = (1 + O2_EXCESS) * 0.5 * reacted / O2_FEED_X["O2"]
        s10 = {k: o2_feed * x for k, x in O2_FEED_X.items()}
        liq = {"PCL3": s5["PCL3"] - reacted, "POCL3": s5["POCL3"] + reacted}
        gas = {"O2": s10["O2"] - 0.5 * reacted, "AR": s10["AR"]}
        vap = vent_vapour(liq, sum(gas.values()), T_VENT, P_VENT)
        s7 = add(gas, vap)
        s6 = {k: liq[k] - vap.get(k, 0.0) for k in liq}
        d_pcl3 = REC_PCL3 * s6["PCL3"]
        d_pocl3 = d_pcl3 * (1 - X_DIST_PCL3) / X_DIST_PCL3
        new13 = {"PCL3": d_pcl3, "POCL3": d_pocl3}
        if abs(new13["PCL3"] - s13["PCL3"]) + abs(new13["POCL3"] - s13["POCL3"]) < 1e-12:
            break
        s13 = new13
    s8 = {k: s6[k] - s13[k] for k in s6}
    s12 = {"POCL3": RESIDUE_FRAC * s8["POCL3"]}
    s9 = {"PCL3": s8["PCL3"], "POCL3": s8["POCL3"] - s12["POCL3"]}
    q_r201 = -(reacted * DH_R2) / 3600.0
    vap308 = vent_vapour(liq, sum(gas.values()), 308.15, P_VENT)
    q_v201 = sum((vap308[k] - vap[k]) * hvap(n, T_VENT) for k, n in (("PCL3", "PCl3"), ("POCL3", "POCl3"))) / 3600.0

    # columns (constant molar overflow, saturated reflux)
    hv_d1 = X_DIST_PCL3 * hvap("PCl3", 349.15) + (1 - X_DIST_PCL3) * hvap("POCl3", 365.0)
    d1 = sum(s13.values())
    m6 = sum(kg(s6).values())
    q_c301_cond = (R_C301 + 1) * d1 * hv_d1 / 3600.0
    q_c301_reb = q_c301_cond + m6 * CP_LIQ * (T_C302_TOP - T_R201_OUT) / 3600.0
    d2 = sum(s9.values())
    q_c302_cond = (R_C302 + 1) * d2 * hvap("POCl3", T_C302_TOP) / 3600.0
    q_c302_reb = q_c302_cond
    m9 = sum(kg(s9).values())
    q_e303 = m9 * CP_LIQ * (T_C302_TOP - T_PRODUCT) / 3600.0

    # T-401 caustic scrubber
    vent = add(s4, s7)
    dest = {k: X_SCRUB * vent.get(k, 0.0) for k in ("PCL3", "POCL3", "CL2")}
    naoh_use = 5 * dest["PCL3"] + 6 * dest["POCL3"] + 2 * dest["CL2"]
    naoh_feed = NAOH_EXCESS * naoh_use
    m_naoh50 = naoh_feed * MW["NAOH"] / 0.5
    m_water = naoh_feed * MW["NAOH"] / NAOH_WT - m_naoh50
    s40 = {"NAOH": naoh_feed, "H2O": m_naoh50 * 0.5 / MW["H2O"]}
    s41 = {"H2O": m_water / MW["H2O"]}
    gas_out = {k: v - dest.get(k, 0.0) for k, v in vent.items()}
    p_w = psat_kpa("water", T_STACK)
    gas_out["H2O"] = sum(gas_out.values()) * p_w / (P_STACK - p_w)
    liquor = {
        "NAOH": naoh_feed - naoh_use,
        "NA2HPO3": dest["PCL3"],
        "NA3PO4": dest["POCL3"],
        "NACL": 3 * dest["PCL3"] + 3 * dest["POCL3"] + dest["CL2"],
        "NAOCL": dest["CL2"],
        "H2O": s40["H2O"] + s41["H2O"] + 2 * dest["PCL3"] + 3 * dest["POCL3"] + dest["CL2"] - gas_out["H2O"],
    }

    # electricity
    def pump_kw(m_kgh):
        return m_kgh / RHO_LIQ / 3600.0 * DP_PUMP / ETA_PUMP
    m3 = sum(kg(s3).values())
    m13 = sum(kg(s13).values())
    m12 = sum(kg(s12).values())
    circ_r201 = q_r201 / (CP_LIQ * DT_R201_LOOP) * 3600.0          # kg/h through E-201
    power = {
        "R101": AGITATOR_KW + pump_kw(m3),                         # agitator + P-101 crude PCl3
        "R201": pump_kw(circ_r201) + pump_kw(m6),                  # P-201 loop + P-202 to C-301
        "C301": pump_kw((R_C301 + 1) * m13),                       # P-301 reflux and recycle
        "C302": pump_kw((R_C302 + 1) * m9) + pump_kw(m12),         # P-302 reflux/product, P-303
        "T401": SCRUB_CIRC_M3H / 3600.0 * DP_PUMP / ETA_PUMP,     # P-401
    }
    return dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, s6=s6, s7=s7, s8=s8, s9=s9, s10=s10,
                s12=s12, s13=s13, s40=s40, s41=s41, s21=gas_out, s22=liquor,
                q=dict(Q_R101=q_r101, Q_V101=q_v101, Q_R201=q_r201, Q_V201=q_v201,
                       Q_C301_REB=q_c301_reb, Q_C301_COND=q_c301_cond,
                       Q_C302_REB=q_c302_reb, Q_C302_COND=q_c302_cond, Q_E303=q_e303),
                power=power, circ_r201=circ_r201)


def main():
    p4 = 10.0
    for _ in range(20):
        r = run(p4)
        prod = sum(kg(r["s9"]).values())
        p4 *= PRODUCT_TARGET / prod
    r = run(p4)
    m_in = m_out = 0.0
    for sid in ("s1", "s2", "s10", "s40", "s41"):
        m_in += sum(kg(r[sid]).values())
    for sid in ("s9", "s12", "s21", "s22"):
        m_out += sum(kg(r[sid]).values())
    # internal name -> stream id of process/flowsheet.yaml
    ids = {"s1": "S1", "s2": "S2", "s3": "S4 (V101 liquid)", "s4": "S5 (V101 vent)",
           "s5": "S6 (R201 feed)", "s6": "S8 (V201 liquid)", "s7": "S9 (V201 vent)",
           "s8": "S12 (C301 bottoms)", "s9": "S13/S14 (product)", "s10": "S10 (oxygen)",
           "s12": "S15 (residue)", "s13": "S11 (recycle)", "s40": "S20 (caustic)",
           "s41": "S21 (water)", "s21": "S23 (stack)", "s22": "S24 (liquor)"}
    for sid, label in ids.items():
        n = {k: v for k, v in r[sid].items() if v > 0}
        m = kg(n)
        mt, nt = sum(m.values()), sum(n.values())
        print(f"{label}: {mt:.3f} kg/h, {nt:.5f} kmol/h")
        print("   x:", {k: round(v / nt, 10) for k, v in n.items()})
        print("   w:", {k: round(v / mt, 10) for k, v in m.items()})
    for k, v in r["q"].items():
        print(f"{k}: {v:.3f} kW")
    for k, v in r["power"].items():
        print(f"power {k}: {v:.2f} kW")
    print(f"R-201 circulation through E-201: {r['circ_r201']:.0f} kg/h")
    print(f"mass in {m_in:.3f}, out {m_out:.3f}, difference {m_in - m_out:.4f} kg/h")
    p_in = 4 * r["s1"]["P4"]
    p_out = r["s9"].get("PCL3", 0) + r["s9"]["POCL3"] + r["s12"]["POCL3"] + r["s21"].get("PCL3", 0) + r["s21"].get("POCL3", 0) + r["s22"]["NA2HPO3"] + r["s22"]["NA3PO4"]
    print(f"P atoms in {p_in:.6f}, out {p_out:.6f} kmol/h; P yield to product {r['s9']['POCL3'] / p_in:.5f}")
    print(f"DH_R1 {DH_R1:.0f} kJ/kmol P4, DH_R2 {DH_R2:.0f} kJ/kmol PCl3")


if __name__ == "__main__":
    main()
