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
Y_AMID = 0.925                      # D-005: ACH to methacrylamide, the rest decomposes
X_EST = 1.0                         # D-006: methacrylamide esterified completely
R_PUR = 0.99                        # D-007: MMA recovered to the product
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
REBOIL_FACTOR = 2.0                 # D-009: purification reboil = 2 x latent heat of its feed, ASSUMED
ETA_BLOWER = 0.75                   # D-009: isentropic efficiency, ASSUMED
P_MISC_KW = 500.0                   # D-009: pumps, agitators, vacuum, lumped, ASSUMED

# ---- molar masses and formation enthalpies (kJ/mol), chemicals 1.5.2 (SRC-5) ----------------
MW = {"ACETONE": 58.0791, "HCN": 27.0253, "ACH": 85.1045, "MAM": 85.1045, "MMA": 100.1158,
      "MEOH": 32.0419, "H2SO4": 98.0785, "AHS": 115.109, "H2O": 18.0153, "CO": 28.0101,
      "CH4": 16.0425, "O2": 31.9988, "N2": 28.0134, "CO2": 44.0095, "SO2": 64.0638,
      "SO3": 80.0632}
HF_LIQ = {"ACETONE": -248.4, "MMA": -385.6, "MEOH": -238.4, "H2SO4": -814.0, "H2O": -285.825}
HF_GAS = {"ACETONE": -216.07, "HCN": 129.291, "ACH": -133.0, "MAM": -157.7, "MMA": -341.6534,
          "MEOH": -200.7, "H2O": -241.822, "CO": -110.525, "CH4": -74.534, "CO2": -393.474,
          "SO2": -296.8, "SO3": -395.7, "O2": 0.0, "N2": 0.0}
HF_SOLID = {"AHS": -1027.0}         # ammonium hydrogen sulfate, crystalline (chemicals 1.5.2, CRC)
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
    meoh_in = MEOH_PER_MAM * mam
    meoh_excess = meoh_in - X_EST * mam
    meoh_rec = MEOH_RECYCLED * meoh_excess
    meoh_fresh = meoh_in - meoh_rec
    water_feed = WATER_PER_ACH_KG * ach * MW["ACH"] / MW["H2O"]
    h2o_r301 = r201_h2o + water_feed
    vap = {"MMA": X_EST * mam, "MEOH": meoh_excess, "ACETONE": dec, "H2O": H2O_TO_VAPOUR * h2o_r301}
    spent = {"H2SO4": s_loop - ach, "AHS": ach, "H2O": (1 - H2O_TO_VAPOUR) * h2o_r301}
    purge = {"MMA": (1 - R_PUR) * vap["MMA"], "MEOH": vap["MEOH"] - meoh_rec,
             "ACETONE": vap["ACETONE"], "H2O": vap["H2O"]}
    co = dec

    # ---- F-501 adiabatic furnace: unknown CH4 f and air n (kmol/h), linear in both
    o2_need = (0.25 * spent["AHS"] - 0.5 * spent["H2SO4"] + 4 * purge["ACETONE"]
               + 1.5 * purge["MEOH"] + 6 * purge["MMA"] + 0.5 * co)
    out_fixed = {"SO2": s_loop,
                 "H2O": (spent["H2O"] + spent["H2SO4"] + 2.5 * spent["AHS"] + purge["H2O"]
                         + 3 * purge["ACETONE"] + 2 * purge["MEOH"] + 4 * purge["MMA"]),
                 "N2": 0.5 * spent["AHS"],
                 "CO2": 3 * purge["ACETONE"] + purge["MEOH"] + 5 * purge["MMA"] + co,
                 "O2": -o2_need}
    per_f = {"H2O": 2.0, "CO2": 1.0, "O2": -2.0}     # per kmol CH4 burned
    per_air = {"O2": 0.21, "N2": 0.79}               # per kmol air

    h_in_fixed = (spent["H2SO4"] * HF_LIQ["H2SO4"] + spent["AHS"] * HF_SOLID["AHS"]
                  + spent["H2O"] * HF_LIQ["H2O"] + sum(purge[k] * HF_LIQ[k] for k in purge)
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

    # ---- duties, kW
    q = {}
    q["Q1_R101"] = kw(ach, -(HF_GAS["ACH"] - HF_GAS["ACETONE"] - HF_GAS["HCN"]))
    q["Q2_R201"] = kw(mam, -(HF_GAS["MAM"] - HF_GAS["ACH"]))
    q["Q3_R301"] = sum(kw(vap[k], latent(k)) for k in vap)
    q["Q4_C401_steam"] = REBOIL_FACTOR * q["Q3_R301"]
    q["Q5_C401_cw"] = q["Q3_R301"] + q["Q4_C401_steam"]
    q["Q6_E501"] = sum(kw(n, dh_sensible(k, T_FURNACE) - dh_sensible(k, T_WHB_OUT)) for k, n in flue.items())
    q["Q7_C501"] = (sum(kw(n, dh_sensible(k, T_WHB_OUT)) for k, n in flue.items())
                    - sum(kw(n, dh_sensible(k, T_CLEAN)) for k, n in flue.items() if k != "H2O")
                    + kw(flue["H2O"], HF_GAS["H2O"] - HF_LIQ["H2O"]))
    dh_ox = HF_GAS["SO3"] - HF_GAS["SO2"]
    dh_abs = HF_LIQ["H2SO4"] - HF_GAS["SO3"] - HF_LIQ["H2O"]
    q["Q8_R502"] = kw(so3, -(dh_ox + dh_abs))

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

    kg = lambda d: sum(n * MW[k] for k, n in d.items())
    acetone_kg = a * MW["ACETONE"]
    ratios = {
        "HCN": a * MW["HCN"] / acetone_kg,
        "WATER": water_feed * MW["H2O"] / acetone_kg,
        "CH4": f * MW["CH4"] / acetone_kg,
        "AIR": n_air * (0.21 * MW["O2"] + 0.79 * MW["N2"]) / acetone_kg,
        "SECAIR": sec_air * (0.21 * MW["O2"] + 0.79 * MW["N2"]) / acetone_kg,
        "DILW": dil_water * MW["H2O"] / acetone_kg,
    }
    return {"A": a, "ach": ach, "mam": mam, "dec": dec, "f": f, "n_air": n_air,
            "sec_air": sec_air, "flue": flue, "spent": spent, "purge": purge, "vap": vap,
            "makeup": makeup, "makeup_h2o": makeup_h2o, "so3": so3, "q": q, "ratios": ratios,
            "acetone_kg": acetone_kg, "spent_kg": kg(spent), "meoh_fresh": meoh_fresh,
            "water_feed": water_feed, "dil_water": dil_water}


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
