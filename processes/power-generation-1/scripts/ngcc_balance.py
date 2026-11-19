"""Balance of power-generation-1: a 2x1 F-class natural-gas combined cycle (NGCC) at the
operating point of NETL's Case B31A (DESIGN.md D-002 to D-010).

Run: ``cheme run scripts/ngcc_balance.py`` (prints the balance). With the environment variable
``BALANCE_OUTPUT`` naming a file it also writes there, as JSON, every value the flowsheet cites
from this script (library ADR 0027, ``balance-output/1``), in the flowsheet's units (kg/h, kW).

Every input is either a number read in SRC-1 (NETL, Cost and Performance Baseline for Fossil
Energy Plants Volume 1, Revision 4a, DOE/NETL-2023/4320, 2022), cited by its exhibit and the
report's printed page, or ASSUMED with its reason. Nothing here is a fit.

What the script gives the flowsheet (each value cited there as "scripts/ngcc_balance.py: ..."):
- the HRSG stack gas S4 (complete combustion of the fuel in the air, D-004): the same flow and
  composition core calculates for the turbine exhaust S3, since the HRSG does not change it;
- the water/steam loop's flows (S5 to S12) closed on NETL's stream table (D-006);
- the steam turbine generator's power and loss from NETL's stream enthalpies (D-007);
- the condenser duty (D-008), the cooling tower's water (D-009) and the auxiliary loads (D-010).
The gas turbine's power is NOT given here: core's conversion-step model writes it (D-005). The
script prints its own estimate of it from the same ideal-gas data as a cross-check only.
"""

from __future__ import annotations

import json
import os

# ---------------------------------------------------------------------------------------------
# Molar masses, kg/kmol: process/materials.yaml (`cheme chemistry thermo`, the chemicals package)
MW = {
    "CH4": 16.042, "C2H6": 30.069, "C3H8": 44.096, "C4H10": 58.122, "CO2": 44.01,
    "H2O": 18.015, "N2": 28.013, "O2": 31.999, "AR": 39.948,
}
# Ideal-gas data (dHf_298 kJ/kmol, cp/R polynomial a0..a4, T in K): process/materials.yaml.
DHF = {"CH4": -74534.0, "C2H6": -83780.0, "C3H8": -104390.0, "C4H10": -125850.0,
       "CO2": -393474.0, "H2O": -241822.0, "N2": 0.0, "O2": 0.0, "AR": 0.0}
CP_R = {
    "CH4": [4.568, -0.008975, 3.631e-05, -3.407e-08, 1.091e-11],
    "C2H6": [4.178, -0.004427, 5.66e-05, -6.651e-08, 2.487e-11],
    "C3H8": [3.847, 0.005131, 6.011e-05, -7.893e-08, 3.079e-11],
    "C4H10": [5.547, 0.005536, 8.057e-05, -1.0571e-07, 4.134e-11],
    "CO2": [3.259, 0.001356, 1.502e-05, -2.374e-08, 1.056e-11],
    "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
    "N2": [3.539, -0.000261, 7e-08, 1.57e-09, -9.9e-13],
    "O2": [3.63, -0.001794, 6.58e-06, -6e-09, 1.79e-12],
    "AR": [2.5, 0.0, 0.0, 0.0, 0.0],
}
R = 8.314462618  # kJ/(kmol K)

# ---------------------------------------------------------------------------------------------
# SRC-1, Exhibit 5-8 (Case B31A stream table, p. 563): streams 1 (air) and 2 (natural gas)
AIR_KG_H = 3_834_126.0
AIR_Y = {"AR": 0.0092, "CO2": 0.0003, "H2O": 0.0099, "N2": 0.7732, "O2": 0.2074}
NG_KG_H = 93_272.0
# SRC-1 Exhibit 2-6 (p. 38) and Exhibit 5-8: the fuel's volume (mole) fractions; the
# methanethiol (mole fraction 5.75e-6, 1.0 kg/h of sulfur, Exhibit 5-13) is left out (D-004).
NG_Y = {"CH4": 0.931, "C2H6": 0.032, "C3H8": 0.007, "C4H10": 0.004, "CO2": 0.010, "N2": 0.016}
T_AIR, T_NG, T_EXH = 288.15, 300.15, 898.15  # K: 15, 27 and 625 degC (Exhibit 5-8)

# SRC-1 Exhibit 5-9 (p. 564), 5-10 (p. 565) and section 5.2.4.2 (p. 567)
GT_POWER_KW = 477_000.0   # combustion turbine power at the generator terminals (2 CTGs)
ST_POWER_KW_NETL = 263_000.0
ETA_GEN_GT = 0.985        # generator efficiency, CT (section 5.2.4.2)
ETA_GEN_ST = 0.987        # generator efficiency, steam turbine (section 5.2.4.2)
HHV_KJ_KG, LHV_KJ_KG = 52_295.0, 47_201.0  # Exhibit 2-6 (p. 38)
HHV_INPUT_KW, LHV_INPUT_KW = 1_354_905.0, 1_222_936.0  # Exhibit 5-9
# Exhibit 5-10 auxiliary loads, kW
AUX = {
    "circulating water pumps": 2820.0, "combustion turbine auxiliaries": 1020.0,
    "condensate pumps": 150.0, "cooling tower fans": 1460.0, "feedwater pumps": 4830.0,
    "ground water pumps": 260.0, "miscellaneous balance of plant": 570.0, "SCR": 2.0,
    "steam turbine auxiliaries": 200.0, "transformer losses": 2250.0,
}
AUX_TOTAL_NETL_KW = 13_562.0  # Exhibit 5-9, "Balance of Plant, kWe"

# SRC-1 Exhibit 5-8: the water/steam streams 5 to 11 (kg/h, steam-table enthalpy kJ/kg on the
# report's reference, 32.02 degF and 0.089 psia)
STEAM = {
    "5": (485_855.0, 3528.08),   # HP steam to the HP turbine, 16.50 MPa, 585 degC
    "6": (485_855.0, 3112.11),   # HP turbine exhaust (cold reheat), 3.74 MPa, 356 degC
    "7": (561_194.0, 3642.68),   # hot reheat to the IP turbine, 3.51 MPa, 584 degC
    "8": (561_194.0, 3080.22),   # IP turbine exhaust, 0.52 MPa, 308 degC
    "9": (72_598.0, 3024.62),    # LP steam from the HRSG, 0.51 MPa, 281 degC
    "10": (633_792.0, 2378.69),  # LP turbine exhaust to the condenser, 38 degC (wet)
    "11": (634_582.0, 160.78),   # condensate, 38 degC
}
# Exhibit 5-15 (p. 569): condenser make-up 2,804 lb/h, the deaerator vent the same 2,804 lb/h
LB_KG = 0.45359237
MAKEUP_KG_H = 2804.0 * LB_KG
# Exhibit 5-14 (p. 567): cooling tower water, gpm (US gallons per minute)
GPM_M3_H = 3.785411784e-3 * 60.0
CT_EVAP_GPM, CT_BLOWDOWN_GPM, CT_WITHDRAWAL_GPM = 2245.0, 651.0, 2897.0
RHO_WATER = 999.1  # kg/m3 at 15 degC, ASSUMED (IAPWS-95 gives 999.10 at 288.15 K, 0.1 MPa)
H_MAKEUP_KJ_KG = 63.0  # ASSUMED: liquid water at 15 degC on the steam-table reference (IAPWS)


def h_ig(comp: str, t: float) -> float:
    """Ideal-gas enthalpy kJ/kmol on the elements at 298.15 K (formation basis)."""
    a = CP_R[comp]

    def integral(x: float) -> float:
        return sum(a[i] * x ** (i + 1) / (i + 1) for i in range(5))

    return DHF[comp] + R * (integral(t) - integral(298.15))


def molar(kg_h: float, y: dict[str, float]) -> tuple[float, dict[str, float]]:
    mw = sum(y[c] * MW[c] for c in y)
    kmol = kg_h / mw
    return kmol, {c: kmol * y[c] for c in y}


def combustion() -> dict:
    """Complete combustion of the fuel's hydrocarbons in the air (D-004)."""
    n_air, air = molar(AIR_KG_H, AIR_Y)
    n_ng, ng = molar(NG_KG_H, NG_Y)
    out = {c: air.get(c, 0.0) + ng.get(c, 0.0) for c in MW}
    for fuel, (c, h) in {"CH4": (1, 4), "C2H6": (2, 6), "C3H8": (3, 8), "C4H10": (4, 10)}.items():
        x = out[fuel]
        out[fuel] = 0.0
        out["CO2"] += c * x
        out["H2O"] += h / 2 * x
        out["O2"] -= (c + h / 4) * x
    n_out = sum(out.values())
    y = {c: out[c] / n_out for c in out if out[c] > 0}
    kg_out = sum(out[c] * MW[c] for c in out)
    h_in = sum(air[c] * h_ig(c, T_AIR) for c in air) + sum(ng[c] * h_ig(c, T_NG) for c in ng)
    h_out = sum(out[c] * h_ig(c, T_EXH) for c in out if out[c] > 0)
    return {
        "n_air": n_air, "n_ng": n_ng, "n_out": n_out, "y_out": y, "kg_out": kg_out,
        "shaft_kW": (h_in - h_out) / 3600.0,  # work and losses leaving the gas turbine
        "air": air, "ng": ng,
    }


def combustion_out_moles(c: dict) -> dict[str, float]:
    return {k: y * c["n_out"] for k, y in c["y_out"].items()}


def steam_cycle() -> dict:
    m = {k: v[0] for k, v in STEAM.items()}
    h = {k: v[1] for k, v in STEAM.items()}
    hp = m["5"] * (h["5"] - h["6"])
    ip = m["7"] * (h["7"] - h["8"])
    lp = (m["8"] * h["8"] + m["9"] * h["9"]) - m["10"] * h["10"]
    shaft = (hp + ip + lp) / 3600.0
    # The loop is closed on the turbine's exhaust: the condensate to the HRSG equals stream 10
    # (stream 11 of the report carries 790 kg/h more, the gland-seal and ejector flows it does
    # not show, D-006).
    condensate = m["10"]
    q_cond = (m["10"] * h["10"] + MAKEUP_KG_H * H_MAKEUP_KJ_KG
              - condensate * h["11"] - MAKEUP_KG_H * h["11"]) / 3600.0
    hrsg_water = (m["5"] * h["5"] + m["7"] * h["7"] + m["9"] * h["9"]
                  - m["6"] * h["6"] - condensate * h["11"]) / 3600.0
    return {
        "hp_kW": hp / 3600.0, "ip_kW": ip / 3600.0, "lp_kW": lp / 3600.0, "shaft_kW": shaft,
        "power_kW": shaft * ETA_GEN_ST, "loss_kW": shaft * (1.0 - ETA_GEN_ST),
        "condensate_kg_h": condensate, "q_cond_kW": q_cond, "hrsg_water_kW": hrsg_water,
        "ip_steam_kg_h": m["7"] - m["6"],
    }


def cooling_tower() -> dict:
    evap = CT_EVAP_GPM * GPM_M3_H * RHO_WATER
    blowdown = CT_BLOWDOWN_GPM * GPM_M3_H * RHO_WATER
    return {"evap_kg_h": evap, "blowdown_kg_h": blowdown, "makeup_kg_h": evap + blowdown,
            "withdrawal_netl_kg_h": CT_WITHDRAWAL_GPM * GPM_M3_H * RHO_WATER}


def auxiliaries() -> dict:
    a = AUX
    return {
        "condensate_pump_kW": a["condensate pumps"],
        "feedwater_pump_kW": a["feedwater pumps"],
        "cooling_kW": a["circulating water pumps"] + a["cooling tower fans"],
        "other_kW": (a["combustion turbine auxiliaries"] + a["steam turbine auxiliaries"]
                     + a["ground water pumps"] + a["miscellaneous balance of plant"] + a["SCR"]),
        "transformer_kW": a["transformer losses"],
        "total_kW": sum(a.values()),
    }


def r(x: float, n: int = 1) -> float:
    return round(x, n)


def main() -> None:
    c = combustion()
    s = steam_cycle()
    ct = cooling_tower()
    aux = auxiliaries()
    gt_loss = GT_POWER_KW * (1.0 / ETA_GEN_GT - 1.0)

    print("== gas turbine (2 trains together) ==")
    print(f"air {c['n_air']:.1f} kmol/h (NETL 132,867), fuel {c['n_ng']:.1f} kmol/h (NETL 5,383)")
    print(f"exhaust {c['n_out']:.1f} kmol/h (NETL 138,406), {c['kg_out']:.1f} kg/h (NETL 3,927,398)")
    print("exhaust mole fractions:", {k: round(v, 5) for k, v in c["y_out"].items()},
          "(NETL: Ar .0089, CO2 .0408, H2O .0875, N2 .7428, O2 .1200)")
    print(f"LHV input {NG_KG_H * LHV_KJ_KG / 3600:.0f} kW (NETL {LHV_INPUT_KW:.0f}),"
          f" HHV input {NG_KG_H * HHV_KJ_KG / 3600:.0f} kW (NETL {HHV_INPUT_KW:.0f})")
    print(f"cross-check only: work + losses from the ideal-gas balance {c['shaft_kW']:.0f} kW;"
          f" NETL CT shaft {GT_POWER_KW / ETA_GEN_GT:.0f} kW = {GT_POWER_KW:.0f} / {ETA_GEN_GT}")
    print(f"generator loss (given, Q2): {gt_loss:.1f} kW")
    print("== steam turbine ==")
    print(f"HP {s['hp_kW']:.0f}, IP {s['ip_kW']:.0f}, LP {s['lp_kW']:.0f}, shaft {s['shaft_kW']:.0f} kW")
    print(f"generator {s['power_kW']:.0f} kW (NETL {ST_POWER_KW_NETL:.0f}), loss {s['loss_kW']:.1f} kW")
    t_stack = 356.15  # K, 83 degC: Exhibit 5-8 stream 4
    out = combustion_out_moles(c)
    gas_kW = sum(n * (h_ig(k, T_EXH) - h_ig(k, t_stack)) for k, n in out.items()) / 3600.0
    print(f"cross-check only: heat the exhaust gives up from 625 to 83 degC {gas_kW:.0f} kW"
          f" (ideal gas) against the water/steam's gain {s['hrsg_water_kW']:.0f} kW")
    print(f"IP steam raised {s['ip_steam_kg_h']:.0f} kg/h; HRSG heat to water/steam {s['hrsg_water_kW']:.0f} kW")
    print(f"condenser duty {s['q_cond_kW']:.0f} kW (NETL 1,406 GJ/h = {1406e6 / 3600:.0f} kW)")
    print("== cooling tower ==", {k: r(v) for k, v in ct.items()})
    print("== auxiliaries ==", aux, "(NETL total", AUX_TOTAL_NETL_KW, ")")
    gross = GT_POWER_KW + s["power_kW"]
    net = gross - aux["total_kW"]
    print(f"gross {gross:.0f} kW, net {net:.0f} kW with NETL's CT power;"
          f" net HHV efficiency {net / HHV_INPUT_KW:.4f}, LHV {net / LHV_INPUT_KW:.4f}")

    y4 = {k: round(v, 7) for k, v in c["y_out"].items()}
    cases = {"design": {
        "S4": {"flow": r(AIR_KG_H + NG_KG_H), "composition": y4},
        "S5": {"flow": STEAM["5"][0]}, "S6": {"flow": STEAM["6"][0]},
        "S7": {"flow": STEAM["7"][0]}, "S9": {"flow": STEAM["9"][0]},
        "S10": {"flow": STEAM["10"][0]},
        "S11": {"flow": r(s["condensate_kg_h"])}, "S12": {"flow": r(s["condensate_kg_h"])},
        "S13": {"flow": r(MAKEUP_KG_H)}, "S14": {"flow": r(MAKEUP_KG_H)},
        "S20": {"flow": r(ct["makeup_kg_h"])}, "S21": {"flow": r(ct["evap_kg_h"])},
        "S22": {"flow": r(ct["blowdown_kg_h"])},
        "Q2": {"duty": r(gt_loss)},
        "Q3": {"duty": r(s["power_kW"])}, "Q4": {"duty": r(s["loss_kW"])},
        "Q5": {"duty": r(s["q_cond_kW"])},
        "Q6": {"duty": aux["condensate_pump_kW"]}, "Q7": {"duty": aux["feedwater_pump_kW"]},
        "Q8": {"duty": aux["cooling_kW"]}, "Q9": {"duty": aux["other_kW"]},
        "Q10": {"duty": aux["transformer_kW"]},
    }}
    out = os.environ.get("BALANCE_OUTPUT")
    if out:
        with open(out, "w") as f:
            json.dump({"contract": "balance-output/1", "script": "scripts/ngcc_balance.py",
                       "cases": cases}, f, indent=1)
    else:
        print(json.dumps(cases, indent=1))


if __name__ == "__main__":
    main()
