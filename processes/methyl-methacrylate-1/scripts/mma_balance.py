"""Concept balance of methyl-methacrylate-1: feed ratios, furnace fuel and the duties.

Run with `cheme run scripts/mma_balance.py` (or any Python with PyYAML) in the process folder.

What it does (DESIGN.md D-004 to D-010):

- the mass balance of the ACH-sulfo route at steady state, in closed form: every step is a
  complete or fixed conversion or a fixed recovery, so each flow is a multiple of the acetone
  feed A (kmol/h); `cheme process propagate --fill` computes the same flows from the
  flowsheet (the specs and tears there), this script only gives the follower ratios of the
  specs and the values core cannot calculate;
- the SAR furnace F-501: methane fuel and combustion air from an adiabatic energy balance
  (formation enthalpies of the `chemicals` 1.5.2 package, ideal-gas heat capacities of
  process/materials.yaml) at an outlet of 1273 K and 2 mol% O2 (D-008);
- the duties of the reactors, the waste heat boiler, the gas cleaning, the converter and
  absorber, the esterification stripper and the purification columns, and the blower power
  (D-009); every simplification is ASSUMED and named where it is made.

It writes the values the flowsheet cites when the environment variable BALANCE_OUTPUT names a
file (balance-output contract, library ADR 0027).
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent.parent

# ---- design basis (process/design-basis.yaml) ---------------------------------------------
MMA_PRODUCT_KG_H = 12500.0          # ASSUMED (D-002): 100 kt/a in 8000 h
Y_AMID = 0.947                      # D-005: ACH to amide (MAA + MA), US 2023/0416184 A1 Table 1, ex. A2
X_EST = 0.977                       # D-006: amide esterified, ASSUMED: with R_PUR the rest of the
                                    # 91.6 % MMA yield on ACH (Table 4, ex. A2): 0.947 x 0.977 x 0.99
R_PUR = 0.99                        # D-007: MMA recovered to the product
# D-005: share of the decomposition's acetone left free (to the crude); the rest is sulfonated
# and stays in the spent acid. Ex. A2 (Table 1): 26.5 kg/h acetone in streams (8) + (9a) per
# 5000 kg/h ACH, against (1 - 0.947) x 5000 / 85.1045 kmol/h ACH decomposed: 0.1465.
ACETONE_FREE = 0.147
H2SO4_PER_ACH = 1.4                 # D-005: mol H2SO4 per mol ACH at R-201 (US 2023/0416184 A1, ex. A2)
MEOH_PER_MAM = 1.2                  # D-006: mol methanol per mol methacrylamide at R-301 (ASSUMED in 0.7-1.6)
WATER_PER_ACH_KG = 0.44             # D-006: kg water per kg ACH to esterification (ex. A2: 1700 + 500 per 5000)
MEOH_RECYCLED = 0.95                # D-007
H2O_TO_VAPOUR = 0.15                # D-006: share of R-301's water stripped with the crude MMA
ACID_WT = 0.985                     # D-008: regenerated acid 98.5 wt% H2SO4
X_SO2 = 0.997                       # D-008: overall SO2 conversion, as sulfuric-acid-1 D-005
T_FURNACE = 1273.15                 # D-008: SAR furnace outlet, K (US 2023/0416184 A1: above 900 C)
O2_FURNACE = 0.02                   # D-008: O2 mole fraction (wet) at the furnace outlet, ASSUMED
O2_PER_SO2_CONV = 1.0               # D-008: mol O2 per mol SO2 at the converter inlet, ASSUMED
T_WHB_OUT = 623.15                  # D-009: waste heat boiler outlet, ASSUMED
T_CLEAN = 313.15                    # D-009: cleaned, dried gas, ASSUMED
P_CLEAN = 95.0                      # D-009: kPa(a) at the gas cooler outlet and the drying tower
P_SAT_CLEAN = 7.385                 # kPa, water at T_CLEAN: chemicals 1.5.2 iapws95_Psat (IAPWS-95
                                    # formulation; the IAPWS release itself not read), D-008
REBOIL_FACTOR = 2.0                 # D-009: purification reboil = 2 x latent heat of its feed, ASSUMED
ETA_BLOWER = 0.75                   # D-009: isentropic efficiency, ASSUMED
P_MISC_KW = 500.0                   # D-009: pumps, agitators, vacuum, lumped, ASSUMED
# Unmodelled heat effects, sized only (D-006, D-008, D-009): ASSUMED liquid heat capacities
DIRECT_STEAM_PER_ACH = 500.0 / 5000.0   # kg/kg ACH, US 2023/0416184 A1 ex. A1-A3 (16d)
CP_WATER_L, CP_MEOH_L, CP_ACID_L = 4.2, 2.6, 1.5   # kJ/(kg K), ASSUMED round values
T_STEAM = 471.4                     # K, MP steam 1500 kPa(a), D-009

# ---- molar masses and formation enthalpies (kJ/mol), chemicals 1.5.2 (SRC-5) ----------------
# Single values, each the package's default method (DESIGN.md SRC-5 names the method and the
# underlying work of each; those works were not read): ATCT_G / ATCT_L (Active Thermochemical
# Tables) for acetone (g), HCN, methanol, water, CO, CO2, CH4; CRC (CRC Handbook) for acetone (l),
# H2SO4 (l), NH4HSO4 (s), SO2, SO3; YAWS (Yaws' handbook) for ACH (g); WEBBOOK (NIST Chemistry
# WebBook) for methacrylamide (g, s) and MMA (g, l).
MW = {"ACETONE": 58.0791, "HCN": 27.0253, "ACH": 85.1045, "MAM": 85.1045, "MMA": 100.1158,
      "MEOH": 32.0419, "H2SO4": 98.0785, "AHS": 115.109, "H2O": 18.0153, "CO": 28.0101,
      "CH4": 16.0425, "O2": 31.9988, "N2": 28.0134, "CO2": 44.0095, "SO2": 64.0638,
      "SO3": 80.0632}
HF_LIQ = {"ACETONE": -248.4, "MMA": -385.6, "MEOH": -238.4, "H2SO4": -814.0, "H2O": -285.825}
HF_GAS = {"ACETONE": -216.07, "HCN": 129.291, "ACH": -133.0, "MAM": -157.7, "MMA": -341.6534,
          "MEOH": -200.7, "H2O": -241.822, "CO": -110.525, "CH4": -74.534, "CO2": -393.474,
          "SO2": -296.8, "SO3": -395.7, "O2": 0.0, "N2": 0.0}
HF_SOLID = {"AHS": -1027.0,         # ammonium hydrogen sulfate, crystalline (CRC)
            "MAM": -248.4644}       # methacrylamide, solid (WEBBOOK): the unconverted amide in
                                    # the spent acid, the only condensed-phase value (ASSUMED)
R_GAS = 8.314462618e-3              # kJ/(mol K)


def load_cp():
    """Ideal-gas cp/R polynomials of process/materials.yaml (cheme chemistry thermo --fit)."""
    doc = yaml.safe_load((HERE / "process" / "materials.yaml").read_text(encoding="utf-8"))
    return {c["id"]: c["ideal_gas"]["cp_R"] for c in doc["components"] if c.get("ideal_gas")}


CP = load_cp()


def dh_sensible(comp: str, t: float, t0: float = 298.15) -> float:
    """Ideal-gas enthalpy change t0 -> t, kJ/mol."""
    a = CP[comp]

    def h(x):
        return sum(a[i] * x ** (i + 1) / (i + 1) for i in range(len(a)))
    return R_GAS * (h(t) - h(t0))


def cp_mix(moles: dict, t: float) -> float:
    total = sum(moles.values())
    return sum(n * R_GAS * sum(c * t ** i for i, c in enumerate(CP[k])) for k, n in moles.items()) / total


def latent(comp: str) -> float:
    """Vaporisation enthalpy at 298.15 K from the formation enthalpies, kJ/mol (ASSUMED basis)."""
    return HF_GAS[comp] - HF_LIQ[comp]


def kw(kmol_h: float, kj_mol: float) -> float:
    return kmol_h * kj_mol * 1000.0 / 3600.0


def balance():
    mma = MMA_PRODUCT_KG_H / MW["MMA"]
    a = mma / (Y_AMID * X_EST * R_PUR)               # acetone = HCN = ACH, kmol/h
    ach = a
    mam = Y_AMID * ach
    dec = (1.0 - Y_AMID) * ach

    # acid loop: all sulfur entering R-201 leaves R-301 as H2SO4 or NH4HSO4 and goes to F-501
    s_loop = H2SO4_PER_ACH * ach
    so3 = X_SO2 * s_loop
    makeup = s_loop - so3                            # kmol/h H2SO4 in the make-up acid
    water_acid = lambda n_h2so4: n_h2so4 * MW["H2SO4"] * (1 - ACID_WT) / ACID_WT / MW["H2O"]
    regen_h2o = water_acid(so3)
    makeup_h2o = water_acid(makeup)
    dil_water = so3 + regen_h2o                      # dilution water to R-502, kmol/h

    # R-201 (amidation, conversion) and V-201 (CO to F-501)
    r201_h2o = regen_h2o + makeup_h2o - dec
    assert r201_h2o > 0, "the acid brings too little water for the decomposition (D-005)"
    # R-301 esterification
    est = X_EST * mam
    meoh_in = MEOH_PER_MAM * mam
    meoh_excess = meoh_in - est
    meoh_rec = MEOH_RECYCLED * meoh_excess
    meoh_fresh = meoh_in - meoh_rec
    water_feed = WATER_PER_ACH_KG * ach * MW["ACH"] / MW["H2O"]
    h2o_r301 = r201_h2o + water_feed
    ahs = dec + est
    vap = {"MMA": est, "MEOH": meoh_excess, "ACETONE": ACETONE_FREE * dec,
           "H2O": H2O_TO_VAPOUR * h2o_r301}
    # the sulfonated acetone is carried as acetone, the unconverted amide as MAM (D-005, D-006)
    spent = {"H2SO4": s_loop - ahs, "AHS": ahs, "H2O": (1 - H2O_TO_VAPOUR) * h2o_r301,
             "ACETONE": (1 - ACETONE_FREE) * dec, "MAM": mam - est}
    purge = {"MMA": (1 - R_PUR) * vap["MMA"], "MEOH": vap["MEOH"] - meoh_rec,
             "ACETONE": vap["ACETONE"], "H2O": vap["H2O"]}
    co = dec

    # ---- F-501 adiabatic furnace: unknown CH4 f and air n (kmol/h), linear in both
    acet = purge["ACETONE"] + spent["ACETONE"]
    o2_need = (0.25 * spent["AHS"] - 0.5 * spent["H2SO4"] + 4 * acet + 5.25 * spent["MAM"]
               + 1.5 * purge["MEOH"] + 6 * purge["MMA"] + 0.5 * co)
    out_fixed = {"SO2": s_loop,
                 "H2O": (spent["H2O"] + spent["H2SO4"] + 2.5 * spent["AHS"] + purge["H2O"]
                         + 3 * acet + 3.5 * spent["MAM"] + 2 * purge["MEOH"] + 4 * purge["MMA"]),
                 "N2": 0.5 * spent["AHS"] + 0.5 * spent["MAM"],
                 "CO2": 3 * acet + 4 * spent["MAM"] + purge["MEOH"] + 5 * purge["MMA"] + co,
                 "O2": -o2_need}
    per_f = {"H2O": 2.0, "CO2": 1.0, "O2": -2.0}     # per kmol CH4 burned
    per_air = {"O2": 0.21, "N2": 0.79}               # per kmol air

    h_in_fixed = (spent["H2SO4"] * HF_LIQ["H2SO4"] + spent["AHS"] * HF_SOLID["AHS"]
                  + spent["H2O"] * HF_LIQ["H2O"] + spent["ACETONE"] * HF_LIQ["ACETONE"]
                  + spent["MAM"] * HF_SOLID["MAM"] + sum(purge[k] * HF_LIQ[k] for k in purge)
                  + co * HF_GAS["CO"])

    def hout(moles):
        return sum(n * (HF_GAS[k] + dh_sensible(k, T_FURNACE)) for k, n in moles.items())

    # energy: h_in_fixed + f*Hf(CH4) = hout(fixed) + f*hout(per_f) + n*hout(per_air)
    # oxygen: O2_out = O2_FURNACE * N_out
    tot = lambda d: sum(d.values())
    e0 = hout(out_fixed) - h_in_fixed
    ef = hout(per_f) - HF_GAS["CH4"]
    en = hout(per_air)
    o0 = out_fixed["O2"] - O2_FURNACE * tot(out_fixed)
    of = per_f["O2"] - O2_FURNACE * tot(per_f)
    on = per_air["O2"] - O2_FURNACE * tot(per_air)
    det = ef * on - en * of
    f = (-e0 * on + en * o0) / det
    n_air = (-ef * o0 + e0 * of) / det
    flue = {k: out_fixed.get(k, 0) + f * per_f.get(k, 0) + n_air * per_air.get(k, 0)
            for k in ("SO2", "H2O", "N2", "CO2", "O2")}
    assert flue["O2"] > 0 and f > 0

    # converter air for O2/SO2 at R-502
    sec_air = max(0.0, (O2_PER_SO2_CONV * flue["SO2"] - flue["O2"]) / 0.21)

    # C-501 / drying tower (D-008): the gas leaves the coolers saturated at T_CLEAN and P_CLEAN;
    # that water is taken up by the drying acid and stays in the common acid circuit of the
    # absorbers, so it covers part of the absorbers' water; the rest condenses as weak acid water
    dry_flue = sum(n for k, n in flue.items() if k != "H2O")
    w_dry = dry_flue * P_SAT_CLEAN / (P_CLEAN - P_SAT_CLEAN)
    w_cond = flue["H2O"] - w_dry
    pw_abs = dil_water - w_dry                       # process water to the absorbers, kmol/h
    assert w_cond > 0 and pw_abs > 0, "the drying acid takes more water than the acid can hold"

    # ---- duties, kW
    q = {}
    q["Q1_R101"] = kw(ach, -(HF_GAS["ACH"] - HF_GAS["ACETONE"] - HF_GAS["HCN"]))
    q["Q2_R201"] = kw(mam, -(HF_GAS["MAM"] - HF_GAS["ACH"]))
    q["Q3_R301"] = sum(kw(vap[k], latent(k)) for k in vap)
    q["Q4_C401_steam"] = REBOIL_FACTOR * q["Q3_R301"]
    q["Q5_C401_cw"] = q["Q3_R301"] + q["Q4_C401_steam"]
    q["Q6_E501"] = sum(kw(n, dh_sensible(k, T_FURNACE) - dh_sensible(k, T_WHB_OUT)) for k, n in flue.items())
    # gas 623 -> 313 K, the condensed water to liquid at 298 K; the water left in the gas is
    # absorbed by the drying acid and its heat goes to the acid coolers (Q8)
    q["Q7_C501"] = (sum(kw(n, dh_sensible(k, T_WHB_OUT)) for k, n in flue.items())
                    - sum(kw(n, dh_sensible(k, T_CLEAN)) for k, n in flue.items() if k != "H2O")
                    - kw(w_dry, dh_sensible("H2O", T_CLEAN))
                    + kw(w_cond, HF_GAS["H2O"] - HF_LIQ["H2O"]))
    dh_ox = HF_GAS["SO3"] - HF_GAS["SO2"]
    dh_abs = HF_LIQ["H2SO4"] - HF_GAS["SO3"] - HF_LIQ["H2O"]
    q_dry = kw(w_dry, dh_sensible("H2O", T_CLEAN) + HF_GAS["H2O"] - HF_LIQ["H2O"])

    # blowers: combustion air 101.325 -> 115 kPa(a); SO2 blower on the dry gas and the
    # converter air 95 -> 150 kPa(a), both from 298/313 K, ideal gas
    def blower(moles, t, p1, p2):
        cp = cp_mix(moles, t)
        k = cp / (cp - R_GAS)
        w = cp * t * ((p2 / p1) ** ((k - 1) / k) - 1) / ETA_BLOWER  # kJ/mol
        return kw(tot(moles), w)
    dry = {k: v for k, v in flue.items() if k != "H2O"}
    dry["O2"] += 0.21 * sec_air
    dry["N2"] += 0.79 * sec_air
    q["P_K501"] = blower({"O2": 0.21 * n_air, "N2": 0.79 * n_air}, 298.15, 101.325, 115.0)
    q["P_K502"] = blower(dry, T_CLEAN, 95.0, 150.0)
    q["P_misc"] = P_MISC_KW
    # Q8: SO2 oxidation and SO3 absorption, the drying acid's water uptake and K-502's
    # compression heat, all to the acid coolers' cooling water (the tail gas's sensible heat
    # not credited, ASSUMED)
    q["Q8_R502"] = kw(so3, -(dh_ox + dh_abs)) + q_dry + q["P_K502"]

    def discharge_t(moles, t, p1, p2):
        cp = cp_mix(moles, t)
        k = cp / (cp - R_GAS)
        return t * (1 + ((p2 / p1) ** ((k - 1) / k) - 1) / ETA_BLOWER)
    t_k502 = discharge_t(dry, T_CLEAN, 95.0, 150.0)
    t_k501 = discharge_t({"O2": 0.21, "N2": 0.79}, 298.15, 101.325, 115.0)

    # sized only, not in any duty (D-006, D-008, D-009); ideal-gas steam, ASSUMED cp of liquids
    ach_kg = ach * MW["ACH"]
    h_steam = (HF_GAS["H2O"] - HF_LIQ["H2O"] + dh_sensible("H2O", T_STEAM)) / MW["H2O"] * 1000  # kJ/kg
    info = {
        "direct steam heat (in S12 as water)": DIRECT_STEAM_PER_ACH * ach_kg * h_steam / 3600,
        "esterification feeds 298 -> 393 K": (water_feed * MW["H2O"] * CP_WATER_L
                                              + meoh_fresh * MW["MEOH"] * CP_MEOH_L) * 95 / 3600,
        "conversion stage 368 -> 428 K": (ach_kg + s_loop * MW["H2SO4"] / ACID_WT) * CP_ACID_L * 60 / 3600,
        "spent acid 393 K, not credited in F-501": None,  # filled below
        "gas-gas exchangers, internal (S26 313 -> 693 K)": sum(
            kw(n, dh_sensible(k, 693.15) - dh_sensible(k, T_CLEAN)) for k, n in dry.items()),
    }

    kg = lambda d: sum(n * MW[k] for k, n in d.items())
    info["spent acid 393 K, not credited in F-501"] = kg(spent) * CP_ACID_L * 95 / 3600
    acetone_kg = a * MW["ACETONE"]
    ratios = {
        "HCN": a * MW["HCN"] / acetone_kg,
        "WATER": water_feed * MW["H2O"] / acetone_kg,
        "CH4": f * MW["CH4"] / acetone_kg,
        "AIR": n_air * (0.21 * MW["O2"] + 0.79 * MW["N2"]) / acetone_kg,
        "SECAIR": sec_air * (0.21 * MW["O2"] + 0.79 * MW["N2"]) / acetone_kg,
        "DILW": pw_abs * MW["H2O"] / acetone_kg,
    }
    c501_cond = w_cond / flue["H2O"]                 # C-501 recovery of H2O to the condensate
    return {"A": a, "ach": ach, "mam": mam, "dec": dec, "f": f, "n_air": n_air,
            "sec_air": sec_air, "flue": flue, "spent": spent, "purge": purge, "vap": vap,
            "makeup": makeup, "makeup_h2o": makeup_h2o, "so3": so3, "q": q, "ratios": ratios,
            "acetone_kg": acetone_kg, "spent_kg": kg(spent), "meoh_fresh": meoh_fresh,
            "water_feed": water_feed, "dil_water": dil_water, "w_dry": w_dry, "w_cond": w_cond,
            "pw_abs": pw_abs, "c501_cond": c501_cond, "t_k502": t_k502, "t_k501": t_k501,
            "info": info}


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import json
    import os

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


def main():
    b = balance()
    q = b["q"]
    print(f"acetone {b['A']:.3f} kmol/h = {b['acetone_kg']:.1f} kg/h; ACH {b['ach'] * MW['ACH']:.1f} kg/h")
    print("follower ratios (kg per kg acetone):", {k: round(v, 6) for k, v in b["ratios"].items()})
    print(f"spent acid to F-501 {b['spent_kg']:.1f} kg/h = {b['spent_kg'] / (b['ach'] * MW['ACH']):.3f} kg/kg ACH"
          " (US 2023/0416184 A1 ex. A2: 11410/5000 = 2.282)")
    v = b["vap"]
    print(f"V-301 vapour water/MMA {v['H2O'] * MW['H2O'] / (v['MMA'] * MW['MMA']):.3f} kg/kg (ex. B1 stream 12: 5.3/87.9 = 0.060)")
    print(f"CH4 {b['f'] * MW['CH4']:.1f} kg/h, air {b['n_air']:.1f} kmol/h, converter air {b['sec_air']:.1f} kmol/h")
    print("flue (kmol/h):", {k: round(n, 2) for k, n in b["flue"].items()})
    print(f"make-up H2SO4 {b['makeup'] * MW['H2SO4']:.1f} kg/h as 100 %")
    sk = {k: n * MW[k] for k, n in b["spent"].items()}
    toc = (sk["ACETONE"] * 36.0321 / MW["ACETONE"] + sk["MAM"] * 48.0428 / MW["MAM"]) / sum(sk.values())
    print(f"spent acid organics as TOC {100 * toc:.2f} wt% (US 2023/0416184 A1 Table 1, ex. A2: 1.5 wt%)")
    print(f"free acetone {b['vap']['ACETONE'] * MW['ACETONE']:.1f} kg/h; CO {b['dec']:.2f} kmol/h ="
          f" {b['dec'] * 22.414 * 5000 / (b['ach'] * MW['ACH']):.1f} Nm3/h per 5000 kg/h ACH"
          " (ex. A2: off-gas 50 and 65 m3/h, mainly CO)")
    print(f"C-501: water condensed {b['w_cond']:.2f} kmol/h, to the drying acid {b['w_dry']:.2f} kmol/h"
          f" (recovery to cond {b['c501_cond']:.6f}); absorber water {b['pw_abs']:.2f} of"
          f" {b['dil_water']:.2f} kmol/h needed")
    print(f"K-502 discharge {b['t_k502'] - 273.15:.1f} C, K-501 discharge {b['t_k501'] - 273.15:.1f} C")
    for k, val in b["info"].items():
        print(f"sized only: {k}: {val:.0f} kW")
    for k, val in q.items():
        print(f"{k}: {val:.1f} kW")
    steam_need = q["Q3_R301"] + q["Q4_C401_steam"]
    print(f"steam demand {steam_need:.1f} kW; WHB {q['Q6_E501']:.1f} kW; export {q['Q6_E501'] - steam_need:.1f} kW")
    r = {k: round(v, 1) for k, v in q.items()}
    write_balance_output({"design": {
        "Q1": {"duty": r["Q1_R101"]}, "Q2": {"duty": r["Q2_R201"]},
        "Q3": {"duty": r["Q3_R301"]}, "Q4": {"duty": r["Q4_C401_steam"]},
        "Q5": {"duty": r["Q5_C401_cw"]}, "Q7": {"duty": r["Q7_C501"]},
        "Q8": {"duty": r["Q8_R502"]}, "Q9": {"duty": round(q["Q6_E501"] - steam_need, 1)},
        "Q10": {"duty": r["P_K501"]}, "Q11": {"duty": r["P_K502"]},
    }})


if __name__ == "__main__":
    main()
