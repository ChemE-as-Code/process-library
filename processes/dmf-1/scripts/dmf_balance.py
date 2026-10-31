"""Concept heat and material balance of the DMF plant (DESIGN.md D-006).

One-step carbonylation of dimethylamine (DMA) with CO in methanol, sodium methoxide catalyst
deactivated in situ, salt filtered, methanol/DMA recovered and recycled, DMF finished under
vacuum. Every parameter below is a design input with its decision id; the sourced ones name
their source in DESIGN.md. Plain arithmetic only: no property package covers this polar,
salt-bearing liquid (core #315), so duties are short-cut estimates (latent + sensible heat,
ASSUMED heat capacities and reflux ratios), not a qualified energy balance.

Run: cheme run scripts/dmf_balance.py   (prints the stream table and duties used in
process/flowsheet.yaml)
"""

import math

# Molar masses, kg/kmol (formula weights, IUPAC 2021 atomic weights)
MW = {"CO": 28.010, "N2": 28.014, "H2": 2.016, "DMA": 45.085, "MEOH": 32.042,
      "DMF": 73.095, "NAOME": 54.024, "NAFORM": 68.007, "DME": 46.069}
COMP = list(MW)

# --- design inputs -------------------------------------------------------------------------
PRODUCT_KG_H = 6250.0          # D-002: 50 kt/a at 8000 h/a, ASSUMED
PRODUCT_W_MEOH = 3.0e-5        # D-009: methanol in the product, 30 ppm(wt) design target ASSUMED below the 50 ppm specification (D-002)
CONV_DMA = 0.985               # D-005: DMA conversion per pass, US 4,098,820 Example 1 (98.5 %)
YIELD_CO = 0.95                # D-005: DMF formed per CO fed, US 4,098,820 Example 1 (95 mol %)
CAT_ON_DMA = 0.0075            # D-005: NaOMe 0.75 wt% of the DMA fed (US 4,098,820 Ex. 1/2/6: 0.75-0.79 %)
CAT_SOLUTION_W = 0.30          # D-007: catalyst bought as 30 wt% NaOMe in methanol, ASSUMED
DMA_TO_MEOH_W = 2.3            # D-005: DMA:methanol in the reactor feed, US 4,098,820 Example 1
CO_IMPURITY = {"N2": 0.003, "H2": 0.002}   # D-004: CO 99.5 mol% (patent examples), rest ASSUMED N2/H2
VENT_Y = {"MEOH": 0.03, "DMA": 0.002, "DMF": 0.002}  # D-008: organics in the HP vent, ASSUMED (vapour pressure estimate)
SALT_RECOVERY = 0.99           # D-008: sodium formate to the filter cake, ASSUMED
CAKE_LIQUID_PER_KG = 0.25 / 0.75   # D-008: wet cake 25 wt% liquor, ASSUMED
C201_DMF_TOP = 0.001           # D-009: DMF fraction of the C-201 feed lost overhead (recycled), ASSUMED
C202_RESIDUE = 0.01            # D-009: DMF to the C-202 heavy residue, 1 % of its feed, ASSUMED (US 4,251,460 example: ~1.2 %)

# --- balance -------------------------------------------------------------------------------
def kmol(d):  # kg -> kmol dict helper
    return {k: v / MW[k] for k, v in d.items()}

def mass(n):
    return {k: n.get(k, 0.0) * MW[k] for k in COMP}

def add(*ds):
    out = {k: 0.0 for k in COMP}
    for d in ds:
        for k, v in d.items():
            out[k] += v
    return out

def scale(d, f):
    return {k: v * f for k, v in d.items()}

dma_r = 85.0          # kmol/h DMA to the reactor, first guess
rec = {k: 0.0 for k in COMP}
for _ in range(500):
    m_dma_r = dma_r * MW["DMA"]
    m_cat = CAT_ON_DMA * m_dma_r
    cat = kmol({"NAOME": m_cat, "MEOH": m_cat * (1 - CAT_SOLUTION_W) / CAT_SOLUTION_W})
    meoh_req = m_dma_r / DMA_TO_MEOH_W / MW["MEOH"]
    fresh_dma = {"DMA": dma_r - rec["DMA"]}
    liq_in = add(fresh_dma, cat, rec)        # S6
    xi1 = CONV_DMA * dma_r                   # DMA + CO -> DMF
    xi2 = cat["NAOME"]                       # NaOMe + MeOH + CO -> HCOONa + DME
    co_feed = xi1 / YIELD_CO
    co = {"CO": co_feed * (1 - sum(CO_IMPURITY.values())), **{k: co_feed * y for k, y in CO_IMPURITY.items()}}
    co["CO"] = co_feed * (1 - sum(CO_IMPURITY.values()))
    out = add(liq_in, co)
    out["DMA"] -= xi1; out["CO"] -= xi1; out["DMF"] += xi1
    out["NAOME"] -= xi2; out["MEOH"] -= xi2; out["CO"] -= xi2; out["NAFORM"] += xi2; out["DME"] += xi2
    gas = {k: out[k] for k in ("CO", "N2", "H2", "DME")}
    n_vent = sum(gas.values()) / (1 - sum(VENT_Y.values()))
    vent = add(gas, {k: n_vent * y for k, y in VENT_Y.items()})
    liq = {k: out[k] - vent[k] for k in COMP}
    # F-101
    salt_cake = SALT_RECOVERY * liq["NAFORM"]
    liquor = {k: v for k, v in liq.items() if k != "NAFORM"}
    liquor_kg = sum(mass(liquor).values())
    cake_liq_frac = salt_cake * MW["NAFORM"] * CAKE_LIQUID_PER_KG / liquor_kg
    cake = add(scale(liquor, cake_liq_frac), {"NAFORM": salt_cake})
    filt = {k: liq[k] - cake[k] for k in COMP}
    # C-201: bottoms methanol = the product's methanol
    meoh_bot = PRODUCT_KG_H * PRODUCT_W_MEOH / MW["MEOH"]
    bot1 = {"DMF": filt["DMF"] * (1 - C201_DMF_TOP), "MEOH": meoh_bot, "NAFORM": filt["NAFORM"]}
    top1 = {k: filt[k] - bot1.get(k, 0.0) for k in COMP}
    # C-202
    res = {"DMF": bot1["DMF"] * C202_RESIDUE, "NAFORM": bot1["NAFORM"]}
    prod = {"DMF": bot1["DMF"] - res["DMF"], "MEOH": bot1["MEOH"]}
    # recycle split: recycle methanol = requirement - catalyst methanol
    f_rec = (meoh_req - cat["MEOH"]) / top1["MEOH"]
    new_rec = scale(top1, f_rec)
    purge = scale(top1, 1 - f_rec)
    prod_kg = sum(mass(prod).values())
    # DMA to the reactor scaled to hit the product rate
    new_dma_r = dma_r * PRODUCT_KG_H / prod_kg
    err = abs(new_dma_r - dma_r) + sum(abs(new_rec[k] - rec[k]) for k in COMP)
    dma_r, rec = new_dma_r, new_rec
    if err < 1e-10:
        break

S = {
    "S1 DMA feed": fresh_dma, "S2 CO feed": co, "S3 catalyst solution": cat,
    "S6 reactor liquid feed": liq_in, "S7 reactor effluent": out, "S8 HP vent": vent,
    "S9 reactor liquid": liq, "S10 filter cake": cake, "S11 filtrate": filt,
    "S12 C-201 distillate": top1, "S13 methanol purge": purge, "S14 recycle": rec,
    "S15 C-201 bottoms": bot1, "S16 DMF product": prod, "S17 C-202 residue": res,
}
print(f"converged: DMA to reactor {dma_r:.4f} kmol/h, recycle fraction of C-201 distillate {f_rec:.9f}")
for name, n in S.items():
    m = mass(n)
    tot = sum(m.values())
    ntot = sum(n.get(k, 0.0) for k in COMP)
    x = {k: round(n.get(k, 0.0) / ntot, 8) for k in COMP if n.get(k, 0.0) > 0}
    w = {k: round(m[k] / tot, 6) for k in COMP if m[k] > 0}
    print(f"{name}: {tot:.2f} kg/h, {ntot:.4f} kmol/h\n  x={x}\n  w={w}")

ins = sum(mass(fresh_dma).values()) + sum(mass(co).values()) + sum(mass(cat).values())
outs = sum(sum(mass(S[k]).values()) for k in ("S8 HP vent", "S10 filter cake", "S13 methanol purge", "S16 DMF product", "S17 C-202 residue"))
print(f"overall: in {ins:.3f} kg/h, out {outs:.3f} kg/h, difference {ins - outs:.2e}")
print(f"extents: DMF_SYN {xi1:.4f} kmol/h, CAT_DEACT {xi2:.4f} kmol/h")

# --- duties (short-cut, all ASSUMED inputs; D-010) -------------------------------------------
kw = lambda kj_h: kj_h / 3600.0
DH_R = -109.9e3        # kJ/kmol: DMA(g) + CO(g) -> DMF(l), NIST WebBook formation enthalpies (D-005)
CP_LIQ = 2.2           # kJ/(kg K) reactor liquid / DMF-rich liquid, ASSUMED
CP_CO = 1.04           # kJ/(kg K) CO, ASSUMED ideal gas
T_R, T_FEED = 363.15, 313.15
m_liq_in = sum(mass(liq_in).values()); m_co = sum(mass(co).values())
q_r = -DH_R * xi1 - (m_liq_in * CP_LIQ + m_co * CP_CO) * (T_R - T_FEED)
print(f"R-101 heat removed to cooling water: {kw(q_r):.0f} kW (heat of CAT_DEACT neglected, extent {xi2:.2f} kmol/h)")

# K-101: CO 300 -> 2300 kPa(a), two intercooled stages, isentropic efficiency 0.75, k 1.4
P1, P2, ETA, KAP = 300.0, 2300.0, 0.75, 1.4
r = math.sqrt(P2 / P1)
w_stage = CP_CO * 313.15 * (r ** ((KAP - 1) / KAP) - 1) / ETA
q_k = 2 * w_stage * m_co
print(f"K-101 shaft power {kw(q_k):.0f} kW, inter/aftercooling {kw(q_k):.0f} kW")

# P-101: reactor feed pump 150 -> 2300 kPa(a), density 750 kg/m3, efficiency 0.6 (ASSUMED)
q_p = m_liq_in / 750.0 * (2300 - 150) / 0.6
print(f"P-101 power {kw(q_p):.1f} kW")

# C-201 at 101 kPa(a), reflux ratio 1.0; latent heats at the normal boiling point:
# methanol 35.2 kJ/mol, DMA 26.0 kJ/mol (NIST WebBook), DMF 44 kJ/mol ASSUMED near 426 K
LAT = {"MEOH": 35.2e3 / 32.042, "DMA": 26.0e3 / 45.085, "DMF": 44.0e3 / 73.095}
R1 = 1.0
m_top1 = mass(top1); m_d1 = sum(m_top1.values())
lam1 = sum(m_top1[k] * LAT.get(k, 0) for k in COMP) / m_d1
m_bot1 = sum(mass(bot1).values())
q_reb1 = (1 + R1) * m_d1 * lam1 + m_bot1 * CP_LIQ * (426.0 - T_R)
q_con1 = (1 + R1) * m_d1 * lam1 + m_d1 * 2.6 * (338.0 - 313.15)
print(f"C-201 reboiler {kw(q_reb1):.0f} kW (MP steam), condenser {kw(q_con1):.0f} kW")

# C-202 at 20 kPa(a) top (DMF boils near 379 K), reflux ratio 0.5, DMF latent 43 kJ/mol ASSUMED;
# the feed arrives at 426 K and flashes; product subcooled to 313 K
R2 = 0.5
m_prod = sum(mass(prod).values())
lam2 = 43.0e3 / 73.095
q_reb2 = (1 + R2) * m_prod * lam2 - m_bot1 * CP_LIQ * (426.0 - 390.0)
q_con2 = (1 + R2) * m_prod * lam2 + m_prod * CP_LIQ * (379.0 - 313.15)
print(f"C-202 reboiler {kw(q_reb2):.0f} kW (LP steam), condenser + product cooler {kw(q_con2):.0f} kW")
print("ASSUMED power: R-101 loop pump 30 kW, C-201 pumps 5 kW, C-202 vacuum system and pumps 20 kW")


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


# the values process/flowsheet.yaml cites from this script (balance-output contract): the stream
# table S (mass flow, mole fractions over COMP) and the duties printed above
FLOWSHEET = {}
for name, n in S.items():
    ntot = sum(n.get(k, 0.0) for k in COMP)
    FLOWSHEET[name.split()[0]] = {
        "flow": {"value": sum(mass(n).values()), "basis": "mass"},
        "composition": {"values": {k: n.get(k, 0.0) / ntot for k in COMP}, "basis": "mole_fraction"}}
FLOWSHEET.update({qid: {"duty": kw(q)} for qid, q in {
    "Q1": q_k, "Q2": q_k, "Q3": q_p, "Q5": q_r, "Q6": q_reb1, "Q7": q_con1, "Q9": q_reb2,
    "Q10": q_con2}.items()})
write_balance_output({"design": FLOWSHEET})
