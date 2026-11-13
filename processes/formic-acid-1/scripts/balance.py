"""Concept heat and material balance of formic-acid-1 (DESIGN.md D-006).

Independent of cheme-as-code's property packages: none of them covers the liquid
methanol / methyl formate / water / formic acid system or the methoxide catalyst.
Mass balance: specified conversions (US4216339 Example 1 for the carbonylation; the hydrolysis
at 95 % of the equilibrium conversion of a mole-fraction constant Kx = 0.20, EP2747883A1 and
EP3661904B1) and specified column splits (DESIGN.md D-007..D-009). Recycles are solved by
direct substitution. Energy: shortcut duties ((R+1) x distillate x heat of vaporization) with
ASSUMED reflux ratios, ideal-gas compression, liquid sensible heats with ASSUMED heat
capacities. Every number below that is not a source fact is ASSUMED (DESIGN.md).

Run: cheme run scripts/balance.py   (prints the summary; writes build/balance.json)
"""

import json
import math
import os

MW = {"CO": 28.010, "N2": 28.013, "MEOH": 32.042, "MF": 60.052, "H2O": 18.015, "FA": 46.025,
      "NAOME": 54.024, "NAFORM": 68.007, "O2": 31.999, "AR": 39.948, "CO2": 44.010}

# ---- design basis (ASSUMED unless a source is named) -----------------------------------------
PRODUCT_KG_H = 6250.0          # D-002: 85 wt% formic acid, 50 kt/a at 8000 h
X_PRODUCT = 0.85               # D-002: commercial 85 wt% grade
CO_N2 = 0.01                   # D-003: CO 99 mol%, impurities lumped as N2
X_MEOH_CARB = 0.30             # US4216339 Example 1: 30 % methanol conversion (80 C, 44 bar)
CO_YIELD = 0.92                # US4216339 Example 1: 92 mol% yield on CO
NAOME_WT = 0.025               # catalyst 2.5 wt% in the reactor liquid feed (US4216339 range 0.4-2.5 %)
WATER_PPM_MEOH = 100e-6        # US4216339: methanol < 100 ppm water; recycle methanol at that limit
PURGE_FRACTION = 0.01          # D-007: share of the C-101 bottoms purged (sodium formate removal)
MF_WT_C101_TOP = 0.96          # EP2747883A1: fresh methyl formate holds 4-6 % methanol; 4 % taken
MF_WT_C201_TOP = 0.98          # EP2747883A1: recovered methyl formate holds up to 1-2 % methanol
KX = 0.20                      # EP2747883A1 background: K = 0.18-0.24; EP3661904B1: Kx 0.18
APPROACH = 0.95                # ASSUMED; US4299981 (unverified lead, D-008): sized for >= 95 % of equilibrium
WATER_TO_MF = 1.5              # D-008: molar water/MF at the hydrolyser inlet (prior art 0.8-7)
FA_WT_C301_TOP = 0.005         # D-009: formic acid slip in the C-301 water distillate (recycled)
FA_WT_C301_BOT = 0.77          # D-009: C-301 at 203 kPa(a), azeotrope about 80 wt% (EP3661904B1)
FA_WT_C302_BOT = 0.66          # D-009: C-302 at 12 kPa(a), 63-66 wt% bottoms (EP2747883A1)
AIR = {"N2": 0.7812, "O2": 0.2095, "AR": 0.0093}
AIR_FACTOR = 2.0               # D-010: oxidiser air, twice the stoichiometric O2

# Raoult's law at the V-101 vent condenser, 313.15 K, 4500 kPa(a): Thermo vapour pressures
# (cheme chemistry props ... -p vapor_pressure --temperature 313.15 --source Thermo)
PSAT_313 = {"MF": 136.631, "MEOH": 35.518}
P_V101 = 4500.0


def kmol(d):
    return {k: v for k, v in d.items() if v > 0}


def mass(d):
    return sum(MW[k] * v for k, v in d.items())


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(d, f):
    return {k: v * f for k, v in d.items()}


def from_mass_fractions(total_kg, w):
    return {k: total_kg * x / MW[k] for k, x in w.items()}


# ---- fixed by the product specification --------------------------------------------------------
prod = from_mass_fractions(PRODUCT_KG_H, {"FA": X_PRODUCT, "H2O": 1 - X_PRODUCT})
xi_hyd = prod["FA"]                     # net hydrolysis extent: all formic acid leaves as product
# C-302: feed at 77 wt%, distillate 85 wt%, bottoms 66 wt% (lever rule)
f302 = PRODUCT_KG_H * (X_PRODUCT - FA_WT_C302_BOT) / (FA_WT_C301_BOT - FA_WT_C302_BOT)
s27 = from_mass_fractions(f302, {"FA": FA_WT_C301_BOT, "H2O": 1 - FA_WT_C301_BOT})
s29 = from_mass_fractions(f302 - PRODUCT_KG_H, {"FA": FA_WT_C302_BOT, "H2O": 1 - FA_WT_C302_BOT})

# the carbonylation extent equals the methyl formate leaving C-101 for the hydrolysis plus the
# methyl formate lost with the vent (the methanol it carries is recycled through C-202)


def solve():
    # initial guesses
    s13 = {"MEOH": 200.0, "NAOME": 2.0, "NAFORM": 0.2}
    s24 = {"MEOH": 100.0, "H2O": 0.01}
    s22 = {"MF": 200.0, "MEOH": 5.0}
    s26 = {"H2O": 300.0, "FA": 1.0}
    x_hyd = 0.3
    s9 = {"MF": 0.0}
    for _ in range(500):
        # ---- carbonylation loop: make up the methyl formate lost with the vent
        xi_carb = xi_hyd + s9["MF"]
        meoh_feed = xi_carb / X_MEOH_CARB                    # methanol at the reactor inlet
        h2o_in = s24["H2O"]                                  # water carried by recycle methanol
        # catalyst: 2.5 wt% NaOMe in the liquid feed; make-up = destroyed by water + purged
        liq_mass_est = meoh_feed * MW["MEOH"] / (1 - NAOME_WT)
        naome_feed = NAOME_WT * liq_mass_est / MW["NAOME"]
        naome_makeup = max(naome_feed - s13["NAOME"], 0.0)
        cat_meoh = naome_makeup * MW["NAOME"] * (0.70 / 0.30) / MW["MEOH"]  # 30 wt% solution
        s4 = {"NAOME": naome_makeup, "MEOH": cat_meoh}
        s3 = {"MEOH": meoh_feed - s13["MEOH"] - s24["MEOH"] - cat_meoh}
        s5 = add(s3, s4, s13, s24)
        co_feed = (xi_carb / CO_YIELD)                       # kmol/h CO (US4216339 Ex. 1 yield)
        s1 = {"CO": co_feed, "N2": co_feed * CO_N2 / (1 - CO_N2)}
        # R-101: CARB (MeOH conversion), DEACT (all water: NaOMe + H2O + CO -> HCOONa + MeOH)
        e_carb = X_MEOH_CARB * s5["MEOH"]
        e_deact = s5.get("H2O", 0.0)
        s7 = add(s1, s5)
        s7 = add(s7, {"MEOH": -e_carb, "CO": -e_carb, "MF": e_carb})
        s7 = add(s7, {"NAOME": -e_deact, "H2O": -e_deact, "CO": -e_deact, "NAFORM": e_deact,
                      "MEOH": e_deact})
        # V-101 at 313 K: CO, N2 all to gas; MF, MeOH vapour by Raoult with the liquid
        liq = {k: v for k, v in s7.items() if k not in ("CO", "N2")}
        nl = sum(liq.values())
        y = {k: liq[k] / nl * PSAT_313[k] / P_V101 for k in PSAT_313}
        n_gas = (s7["CO"] + s7["N2"]) / (1 - sum(y.values()))
        s9 = {"CO": s7["CO"], "N2": s7["N2"], "MF": y["MF"] * n_gas, "MEOH": y["MEOH"] * n_gas}
        s10 = add(s7, scale(s9, -1))
        s10 = {k: v for k, v in s10.items() if abs(v) > 1e-12}
        # C-101: all MF overhead with methanol to 96 wt% MF; bottoms methanol and catalyst
        mf_kg = s10["MF"] * MW["MF"]
        meoh_top = mf_kg * (1 - MF_WT_C101_TOP) / MF_WT_C101_TOP / MW["MEOH"]
        s11 = {"MF": s10["MF"], "MEOH": meoh_top}
        s12 = {"MEOH": s10["MEOH"] - meoh_top, "NAOME": s10["NAOME"], "NAFORM": s10["NAFORM"]}
        s13 = scale(s12, 1 - PURGE_FRACTION)
        s14 = scale(s12, PURGE_FRACTION)

        # ---- hydrolysis loop
        mf_feed = xi_hyd / x_hyd
        s22 = {"MF": mf_feed - s11["MF"]}
        s22["MEOH"] = s22["MF"] * MW["MF"] * (1 - MF_WT_C201_TOP) / MF_WT_C201_TOP / MW["MEOH"]
        h2o_feed = WATER_TO_MF * mf_feed
        # water: make-up closes the overall balance; the C-301 distillate fills the rest
        s24_new_h2o = None
        # make-up water = consumed + product + carried to the carbonylation
        # C-301 distillate (water + 0.5 wt% FA) = feed water - make-up - acid recycle water
        h2o_s26 = h2o_feed - s29["H2O"] - (xi_hyd + prod["H2O"] + s24["H2O"])
        s26 = {"H2O": h2o_s26, "FA": h2o_s26 * MW["H2O"] * FA_WT_C301_TOP / (1 - FA_WT_C301_TOP) / MW["FA"]}
        s17 = {"H2O": xi_hyd + prod["H2O"] + s24["H2O"]}
        s18 = add(s11, s22, s26, s29, s17)
        # equilibrium of MF + H2O <=> FA + MeOH in mole fractions (total moles constant)
        a, b, c, d = s18["MF"], s18["H2O"], s18["FA"], s18["MEOH"]
        lo, hi = 0.0, min(a, b) * (1 - 1e-12)
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            g = (c + mid) * (d + mid) - KX * (a - mid) * (b - mid)
            if g > 0:
                hi = mid
            else:
                lo = mid
        x_eq = lo / a
        x_new = APPROACH * x_eq
        e_hyd = x_new * a
        s21 = add(s18, {"MF": -e_hyd, "H2O": -e_hyd, "FA": e_hyd, "MEOH": e_hyd})
        # C-201: all MF overhead with methanol to 98 wt%; C-202: methanol overhead, dry to 100 ppm
        s23 = {"MEOH": s21["MEOH"] - s22["MEOH"], "H2O": s21["H2O"], "FA": s21["FA"]}
        meoh_rec = s23["MEOH"]
        w_rec = meoh_rec * MW["MEOH"] * WATER_PPM_MEOH / (1 - WATER_PPM_MEOH) / MW["H2O"]
        s24 = {"MEOH": meoh_rec, "H2O": w_rec}
        s25 = {"H2O": s23["H2O"] - w_rec, "FA": s23["FA"]}
        err = abs(x_new - x_hyd) + abs(s11["MF"] - xi_hyd)
        x_hyd = x_new
        if err < 1e-12:
            break
    return locals()


r = solve()
s25 = r["s25"]
# C-301: distillate s26 (from the loop), bottoms s27 at 77 wt% FA: check closure
c301_res = {k: s25.get(k, 0) - r["s26"].get(k, 0) - s27.get(k, 0) for k in ("H2O", "FA")}

# ---- off-gas oxidiser X-101 (adiabatic, no support fuel)
s9 = r["s9"]
o2_stoich = 0.5 * s9["CO"] + 2.0 * s9["MF"] + 1.5 * s9["MEOH"]
n_air = AIR_FACTOR * o2_stoich / AIR["O2"]
s15 = {k: n_air * v for k, v in AIR.items()}
conv = 0.999
s16 = add(s9, s15)
s16 = add(s16, {"CO": -conv * s9["CO"], "O2": -0.5 * conv * s9["CO"], "CO2": conv * s9["CO"]})
s16 = add(s16, {"MF": -conv * s9["MF"], "O2": -2 * conv * s9["MF"], "CO2": 2 * conv * s9["MF"],
                "H2O": 2 * conv * s9["MF"]})
s16 = add(s16, {"MEOH": -conv * s9["MEOH"], "O2": -1.5 * conv * s9["MEOH"],
                "CO2": conv * s9["MEOH"], "H2O": 2 * conv * s9["MEOH"]})

# ---- energy (shortcut, ASSUMED) -------------------------------------------------------------
HVAP = {"MF": 27.68, "MEOH": 35.3, "H2O": 40.7, "FA": 20.0}   # kJ/mol near the column top
# MF 27.68 (Thermo, 313 K); MeOH 35.3 (ASSUMED near 338 K, Thermo gives 36.69 at 313 K);
# water 40.7 (ASSUMED near 373 K); formic acid 20.0 (Thermo at 298 K, associated vapour)
# C-301: 2.4 = 1.2 x R_min 1.96 (scripts/c301_rmin.py, feed pinch; D-011, review R-01)
REFLUX = {"C101": 1.0, "C201": 1.0, "C202": 1.5, "C301": 2.4, "C302": 1.5}


def reb(dist, rr):
    return (rr + 1) * sum(v * HVAP[k] for k, v in dist.items() if k in HVAP) / 3.6  # kW


duty = {}
duty["C101"] = reb(r["s11"], REFLUX["C101"])
duty["C201"] = reb(r["s22"], REFLUX["C201"])
duty["C202"] = reb(r["s24"], REFLUX["C202"])
duty["C301"] = reb(r["s26"], REFLUX["C301"])
duty["C302"] = reb(prod, REFLUX["C302"])
# R-101 heat of reaction, liquid phase: -37.7 kJ/mol from ideal-gas dHf (cheme chemistry thermo)
# and heats of vaporization at 298 K (Thermo: MF 28.57, MeOH 37.46)
duty["R101"] = r["e_carb"] * 37.7 / 3.6
# R-201: +7.7 kJ/mol at 298.15 K (CRC liquid formation enthalpies, chemicals 1.5.2), supplied by
# LP steam. The reaction term only: the flowsheet's Q10 is core's conversion-step duty, which
# also brings the liquid streams to and from 298.15 K at the liquid heat capacities of
# materials.yaml (-43.6 kW, D-015), so it is not cited from this script
duty["R201"] = r["e_hyd"] * 7.7 / 3.6
# E-101: reactor effluent 353 -> 313 K, liquid cp 2.5 kJ/(kg K) ASSUMED
duty["E101"] = mass(r["s7"]) * 2.5 * 40 / 3600
# E-201: hydrolyser feed 340 -> 393 K (S19 -> S20), cp 3.0 kJ/(kg K) ASSUMED
duty["E201"] = mass(r["s18"]) * 3.0 * 53 / 3600
# K-101: CO 200 -> 4600 kPa(a), 3 stages, intercooled to 313 K, isentropic 0.75, k = 1.4
n_co = sum(r["s1"].values()) / 3.6   # mol/s
ratio = (4600 / 200) ** (1 / 3)
w_stage = n_co * 8.314 * 313.15 * 1.4 / 0.4 * (ratio ** (0.4 / 1.4) - 1) / 0.75 / 1000  # kW
duty["K101"] = 3 * w_stage / 0.95       # motor 0.95
duty["K101_cool"] = 3 * w_stage          # intercoolers and aftercooler to cooling water
# pumps: P-101 methanol feed to 4600 kPa, P-201 hydrolyser feed to 600 kPa (efficiency 0.6, motor 0.95)
duty["P101"] = mass(r["s5"]) / 790 / 3600 * (4600 - 300) / 0.6 / 0.95
duty["P201"] = mass(r["s18"]) / 1000 / 3600 * (600 - 200) / 0.6 / 0.95
duty["C302_vac"] = 15.0                  # vacuum system allowance, ASSUMED
cond = {k: duty[k] for k in ("C101", "C201", "C202", "C301", "C302")}

out = {"streams": {k: r[k] for k in ("s1", "s3", "s4", "s5", "s7", "s9", "s10", "s11", "s12",
                                    "s13", "s14", "s17", "s18", "s21", "s22", "s23", "s24",
                                    "s26")},
       "x_hyd": r["x_hyd"], "e_hyd": r["e_hyd"], "e_carb": r["e_carb"]}
out["streams"].update({"s15": s15, "s16": s16, "s25": s25, "s27": s27, "s28": prod, "s29": s29})
out["duty_kW"] = duty


def show(name, d):
    m = mass(d)
    n = sum(d.values())
    xs = {k: round(v / n, 6) for k, v in d.items() if v > 0}
    ws = {k: round(MW[k] * v / m, 6) for k, v in d.items() if v > 0}
    print(f"{name:5s} {m:12.3f} kg/h {n:10.4f} kmol/h  x={xs}")
    return {"kg_h": m, "kmol_h": n, "x": xs, "w": ws}


print(f"hydrolysis conversion {r['x_hyd']:.5f} (Kx {KX}, approach {APPROACH}); extent {r['e_hyd']:.4f} kmol/h")
print(f"carbonylation extent {r['e_carb']:.4f} kmol/h; C-301 closure {c301_res}")
table = {}
for k in sorted(out["streams"], key=lambda s: int(s[1:])):
    table[k] = show(k, out["streams"][k])
out["table"] = table
print("duties kW:", {k: round(v, 1) for k, v in duty.items()})
steam = sum(duty[k] for k in ("C101", "C201", "C202", "C301", "C302", "R201", "E201"))
cw = sum(cond.values()) + duty["R101"] + duty["E101"] + duty["K101_cool"]
power = duty["K101"] + duty["P101"] + duty["P201"] + duty["C302_vac"]
print(f"LP steam heat {steam:.0f} kW = {steam / PRODUCT_KG_H:.3f} kWh/kg product;"
      f" cooling water {cw:.0f} kW; power {power:.0f} kW")
print(f"heat per t 85 % acid {steam / PRODUCT_KG_H * 1000:.0f} kWh/t (EP2747883A1 prior art about 2400)")
os.makedirs("build", exist_ok=True)
with open("build/balance.json", "w") as f:
    json.dump(out, f, indent=1)


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


# the values process/flowsheet.yaml cites from this script (balance-output contract): the streams
# of build/balance.json (mass flow, mole fractions) and the duties; a condenser carries its
# column's reboiler duty (cond)
FLOWSHEET = {}
for k, d in out["streams"].items():
    FLOWSHEET["S" + k[1:]] = {"flow": {"value": mass(d), "basis": "mass"},
                              "composition": {"values": {c: v / sum(d.values()) for c, v in d.items()},
                                              "basis": "mole_fraction"}}
for qid, k in {"Q1": "K101", "Q2": "K101_cool", "Q3": "P101", "Q4": "R101", "Q5": "E101",
               "Q6": "C101", "Q8": "P201", "Q9": "E201", "Q11": "C201",
               "Q13": "C202", "Q15": "C301", "Q17": "C302"}.items():
    FLOWSHEET[qid] = {"duty": duty[k]}
for qid, k in {"Q7": "C101", "Q12": "C201", "Q14": "C202", "Q16": "C301", "Q18": "C302"}.items():
    FLOWSHEET[qid] = {"duty": cond[k]}
write_balance_output({"design": FLOWSHEET})
