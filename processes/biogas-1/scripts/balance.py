"""What core cannot calculate in the biogas plant (DESIGN.md D-002 to D-010).

The plant is the FNR model plant VII (500 kWel, cattle slurry and hygienised biowastes; FNR,
Guide to Biogas, 2010, Tables 8.2, 8.3, 8.4 and 8.7), with its biogas upgraded to biomethane by
a three-stage membrane unit instead of burnt in a CHP engine (D-001). cheme process propagate
computes the mixer, the digesters' conversion (Buswell, complete conversion of the digestible
lumps), the gas-space split, the splitter, the boiler, the compressor's knock-out, the membrane
unit and the digestate store from process/flowsheet.yaml. This script gives what core has no
model for:

- the substrates' compositions in the lumped components (D-004): water and ash from the dry
  matter (DM) and volatile solids (VS) of FNR Table 8.2, and the VS split into the digestible
  carbohydrate CARB, the digestible fat LIPID and the inert RVS such that Buswell's
  stoichiometry gives each substrate's standard biogas yield and methane content of Table 8.2;
- the feed rates from the annual tonnages of Table 8.3 (plant VII) over 8000 h (Table 8.4);
- the water vapour that leaves with the biogas (saturated at the digesters' temperature), that
  condenses in the gas chiller before compression (saturated at the chiller's outlet, D-007) and
  after compression (saturated at the after-cooler's outlet), from the vapour pressure of water
  (IAPWS-95 in the `chemicals` package 1.5.2, iapws95_Psat), and its heat of vaporisation (the
  Clausius-Clapeyron equation on the same IAPWS-95 saturation functions);
- the membrane unit's split (D-006): 99.5 % of the methane to the product (SGC Rapport
  2013:270, sections 2.3.4 and 3.3, design iii), the carbon dioxide left in the product for
  98.0 mol% methane (section 3.1), all water to the permeate (section 2.3.1);
- the heat demand of the digesters (D-008): the substrate warmed from 283.15 to 313.15 K, the
  digesters' wall, floor and roof losses and the heat of vaporisation of the water that leaves
  saturated in the biogas, and the share of the biogas the hot-water boiler burns to cover it,
  from the same ideal-gas enthalpies core uses (process/materials.yaml);
- the heat removed by the gas chiller E300 and by the after-coolers E301 (D-007), from the same
  ideal-gas enthalpies and the heat of vaporisation;
- the electricity (D-009): the upgrading at 0.25 kWh per Nm3 of raw biogas (SGC section 2.3.3,
  0.20 to 0.30), the gas chiller's compressor and the digesters' agitators and pumps (FNR
  Table 8.4);
- cross-checks against the source: the biogas per year and its methane content (Table 8.7,
  plant VII), the hydraulic retention time and the digestate store (Tables 8.4 and 8.7).

Run: `cheme run scripts/balance.py`. With BALANCE_OUTPUT set it writes the values the flowsheet
cites (library ADR 0027). Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import yaml
from chemicals.iapws import iapws95_dPsat_dT, iapws95_Psat, iapws95_rhog_sat, iapws95_rhol_sat, iapws95_Tsat

ROOT = Path(__file__).resolve().parents[1]

# ---- sources --------------------------------------------------------------------------------
# FNR Guide to Biogas (2010), Table 8.2: DM (kg/kg FM), VS (kg/kg DM), biogas (Nm3/t VS), CH4
# (vol. fraction); Table 8.3, plant VII: t FM per year (the column read from the plant's gas
# yield, D-002).
SUBSTRATES = {
    "SLURRY": {"title": "cattle slurry", "dm": 0.08, "vs": 0.80, "yield": 370.0, "ch4": 0.55, "t_a": 4000.0},
    "CATER": {"title": "catering waste", "dm": 0.16, "vs": 0.87, "yield": 680.0, "ch4": 0.60, "t_a": 8000.0},
    "GREASE": {"title": "grease trap waste", "dm": 0.05, "vs": 0.90, "yield": 1000.0, "ch4": 0.68, "t_a": 4600.0},
    "BIOW": {"title": "biowaste", "dm": 0.40, "vs": 0.50, "yield": 615.0, "ch4": 0.60, "t_a": 5500.0},
}
HOURS = 8000.0                    # FNR Table 8.4: 8000 full-load hours per year
SRC_BIOGAS_M3_A = 1_735_468.0     # FNR Table 8.7, plant VII: gas yield, m3/a
SRC_CH4 = 0.607                   # FNR Table 8.7, plant VII: methane content
SRC_HRT_D = 51.0                  # FNR Table 8.7, plant VII: average hydraulic retention time
SRC_DIGESTER_M3 = 3400.0          # FNR Table 8.7, plant VII: gross digester volume
SRC_STORE_M3 = 11400.0            # FNR Table 8.7, plant VII: digestate storage volume

# ---- constants ------------------------------------------------------------------------------
AW = {"C": 12.011, "H": 1.008, "O": 15.999, "Si": 28.085, "N": 14.007}   # IUPAC 2021 abridged
R = 8.314462618                   # J/(mol K), CODATA
T_N, P_N = 273.15, 101.325        # normal conditions of the source's Nm3 (DIN 1343)
V_N = R * T_N / P_N               # m3/kmol of an ideal gas at normal conditions (22.414)
MW = {"H2O": 18.015, "CARB": 162.141, "LIPID": 885.453, "RVS": 162.141, "ASH": 60.083,
      "CH4": 16.043, "CO2": 44.009, "O2": 31.998, "N2": 28.014}

# ---- design choices (ASSUMED unless noted) -------------------------------------------------
T_FEED = 283.15        # substrates and air at the annual mean ambient, ASSUMED
T_DIG = 313.15         # 40 C, inside FNR's mesophilic range 37-43 C (section 5.1.3), ASSUMED
P_GAS = 102.0          # kPa(a): the digesters' gas space under the double-membrane roof, ASSUMED
P_MEM = 1600.0         # kPa(a): membrane feed, inside SGC's 6-20 bar(a) (section 2.3.1), ASSUMED
T_CHILL = 283.15       # gas chiller outlet before compression (SGC section 2.3.1: water removed
                       # by cooling before compression), ASSUMED
P_CHILL = 101.5        # kPa(a): chiller and activated-carbon filter, ASSUMED
COP_CHILL = 3.0        # coefficient of performance of the chiller (chilled water), ASSUMED
T_COOL = 303.15        # after-cooler outlet, ASSUMED
CH4_RECOVERY = 0.995   # SGC sections 2.3.4 and 3.3: 99-99.5 %, about 0.5 % slip with design (iii)
PRODUCT_CH4 = 0.980    # SGC section 3.1: most manufacturers guarantee 98 % CH4
EXCESS_AIR = 1.15      # boiler air ratio, ASSUMED
T_FLUE = 423.15        # boiler flue gas, ASSUMED
CP_SUBSTRATE = 4.18    # kJ/(kg K), the substrates warmed as water (72-95 % water), ASSUMED
# Digesters: two equal tanks of FNR's 3400 m3 gross (two-stage, section 8.1.3), 6 m high, ASSUMED.
N_TANKS, H_TANK = 2, 6.0
U_WALL = 0.035 / 0.10  # W/(m2 K): 10 cm of mineral fibre at 0.035 W/(m K) (FNR Tables 3.30, 3.31)
U_ROOF = 1.0           # W/(m2 K): the double-membrane gas-storage roof, ASSUMED
T_AMB = 283.15         # outside air and ground, annual mean, ASSUMED
E_UPGRADE = 0.25       # kWh/Nm3 raw biogas: SGC section 2.3.3 (membranes 0.20-0.30)
AGIT_W_M3 = (25.0, 15.0)   # W/m3: FNR Table 8.4, mid of 20-30 (first) and 10-20 (second stage)
AGIT_RUN = 0.5         # agitators run half the time (intermittent stirring), ASSUMED
PUMPS_KW = 5.0         # intake pit mixer, feed and transfer pumps, ASSUMED
DIGESTATE_RHO = 1000.0 # kg/m3, ASSUMED
STORE_MONTHS = 6.0     # FNR Table 8.4: storage for 6 months plus 10 %


def mass_frac(flows: dict[str, float]) -> dict[str, float]:
    total = sum(flows.values())
    return {k: v / total for k, v in flows.items() if v > 0}


def substrate_split(s: dict) -> tuple[float, float]:
    """The digestible carbohydrate a and fat b per kg VS that give the yield and CH4 share."""
    g_c, m_c = 6 * V_N / MW["CARB"], 3 * V_N / MW["CARB"]      # Nm3 gas, CH4 per kg CARB
    g_l, m_l = 57 * V_N / MW["LIPID"], 40 * V_N / MW["LIPID"]  # Nm3 gas, CH4 per kg LIPID
    y, c = s["yield"] / 1000.0, s["ch4"]
    det = g_c * m_l - g_l * m_c
    a = (y * m_l - g_l * y * c) / det
    b = (g_c * y * c - m_c * y) / det
    assert a >= 0 and b >= 0 and a + b <= 1, (s["title"], a, b)
    return a, b


def hvap_water(T: float) -> float:
    """Heat of vaporisation of water, kJ/kg: Clausius-Clapeyron on IAPWS-95 (chemicals 1.5.2)."""
    dpdt = iapws95_dPsat_dT(T)
    dpdt = dpdt[0] if isinstance(dpdt, tuple) else dpdt
    return T * dpdt * (1 / iapws95_rhog_sat(T) - 1 / iapws95_rhol_sat(T)) / 1000.0


def enthalpy(comp: dict, T: float) -> float:
    """Ideal-gas molar enthalpy with formation, kJ/kmol (the polynomial core uses)."""
    ig = comp["ideal_gas"]
    c = [float(v) for v in ig["cp_R"]]   # PyYAML reads "-6e-09" (no dot) as a string
    def h(t):
        return R * sum(c[i] * t ** (i + 1) / (i + 1) for i in range(5))
    return ig["dHf_298"] + (h(T) - h(298.15))


def main() -> None:
    mats = yaml.safe_load((ROOT / "process/materials.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in mats["components"]}

    # ---- feeds (D-002, D-004)
    feeds, total = {}, {k: 0.0 for k in MW}
    print("Substrates (FNR Table 8.2; plant VII, Table 8.3):")
    for fid, s in SUBSTRATES.items():
        a, b = substrate_split(s)
        flow = s["t_a"] * 1000.0 / HOURS
        dm, vs = s["dm"], s["vs"]
        x = {"H2O": 1 - dm, "ASH": dm * (1 - vs), "CARB": dm * vs * a, "LIPID": dm * vs * b,
             "RVS": dm * vs * (1 - a - b)}
        feeds[fid] = {"flow": flow, "composition": x}
        for k, v in x.items():
            total[k] += flow * v
        print(f"  {fid:7s} {flow:9.2f} kg/h  digestible VS {a:.4f} CARB + {b:.4f} LIPID, inert {1-a-b:.4f}")
    feed_mass = sum(f["flow"] for f in feeds.values())

    # ---- digesters R101 (Buswell, complete conversion of the lumps)
    n_carb, n_lip = total["CARB"] / MW["CARB"], total["LIPID"] / MW["LIPID"]
    n_ch4 = 3 * n_carb + 40 * n_lip
    n_co2 = 3 * n_carb + 17 * n_lip
    n_h2o = total["H2O"] / MW["H2O"] - n_carb - 28 * n_lip
    dry_nm3_h = (n_ch4 + n_co2) * V_N
    ch4_frac = n_ch4 / (n_ch4 + n_co2)
    print(f"Biogas (dry) {dry_nm3_h:.2f} Nm3/h = {dry_nm3_h*HOURS:,.0f} Nm3/a "
          f"(FNR Table 8.7: {SRC_BIOGAS_M3_A:,.0f}, {100*(dry_nm3_h*HOURS/SRC_BIOGAS_M3_A-1):+.2f} %); "
          f"CH4 {100*ch4_frac:.2f} mol% (source {100*SRC_CH4:.1f})")
    vs_in = total["CARB"] + total["LIPID"] + total["RVS"]
    print(f"VS converted {100*(total['CARB']+total['LIPID'])/vs_in:.1f} % of the VS fed; "
          f"DM of the mixture {100*(1-total['H2O']/feed_mass):.1f} % (FNR Table 8.7: 18.2 %)")

    # ---- gas space V101: wet biogas saturated at T_DIG
    y_w = iapws95_Psat(T_DIG) / 1000.0 / P_GAS
    n_w_gas = y_w / (1 - y_w) * (n_ch4 + n_co2)
    rec_w_gas = n_w_gas / n_h2o
    gas = {"CH4": n_ch4, "CO2": n_co2, "H2O": n_w_gas}
    print(f"V101: water to the biogas {rec_w_gas:.7f} of the digester's water (y = {y_w:.5f})")

    # ---- heat demand of the digesters (D-008)
    q_feed = feed_mass / 3600.0 * CP_SUBSTRATE * (T_DIG - T_FEED)
    q_evap = n_w_gas * MW["H2O"] * hvap_water(T_DIG) / 3600.0
    v_tank = SRC_DIGESTER_M3 / N_TANKS
    d_tank = math.sqrt(4 * v_tank / (math.pi * H_TANK))
    a_wall, a_disc = math.pi * d_tank * H_TANK, math.pi / 4 * d_tank ** 2
    q_loss = N_TANKS * ((a_wall + a_disc) * U_WALL + a_disc * U_ROOF) * (T_DIG - T_AMB) / 1000.0
    q_demand = q_feed + q_loss + q_evap
    print(f"Heat: substrate {q_feed:.2f} kW + losses {q_loss:.2f} kW (D {d_tank:.2f} m) + water "
          f"evaporated into the biogas {q_evap:.2f} kW ({n_w_gas*MW['H2O']:.2f} kg/h at "
          f"{hvap_water(T_DIG):.0f} kJ/kg) = {q_demand:.2f} kW")

    # ---- boiler B101: heat per kmol of biogas methane burnt (ideal gas, as core)
    h = lambda k, T: enthalpy(comps[k], T)  # noqa: E731
    gas_tot = sum(gas.values())
    y_gas = {k: v / gas_tot for k, v in gas.items()}
    o2 = 2 * EXCESS_AIR * y_gas["CH4"]          # per kmol of wet biogas
    n2 = o2 * 0.79 / 0.21                        # dry air 21/79 mol%, argon in N2, ASSUMED
    h_in = sum(y_gas[k] * h(k, T_DIG) for k in y_gas) + o2 * h("O2", T_FEED) + n2 * h("N2", T_FEED)
    out = {"CO2": y_gas["CO2"] + y_gas["CH4"], "H2O": y_gas["H2O"] + 2 * y_gas["CH4"],
           "O2": o2 - 2 * y_gas["CH4"], "N2": n2}
    h_out = sum(v * h(k, T_FLUE) for k, v in out.items())
    q_per_kmol = (h_in - h_out) / 3600.0         # kW per kmol/h of wet biogas
    lhv = (h("CH4", 298.15) + 2 * h("O2", 298.15) - h("CO2", 298.15) - 2 * h("H2O", 298.15)) / 3600.0
    eta = q_per_kmol / (y_gas["CH4"] * lhv)
    split = q_demand / (q_per_kmol * gas_tot)
    print(f"Boiler: efficiency on LHV {eta:.4f}; biogas share {split:.6f} (FNR Table 8.8, plant X: 5 %)")
    n_boil = gas_tot * split
    air = {"O2": o2 * n_boil, "N2": n2 * n_boil}
    air_flow = sum(MW[k] * v for k, v in air.items())

    # ---- upgrading
    up = {k: v * (1 - split) for k, v in gas.items()}
    up_dry_nm3 = (up["CH4"] + up["CO2"]) * V_N
    dry = up["CH4"] + up["CO2"]
    # gas chiller E300 before compression (D-007): saturated at T_CHILL and P_CHILL
    y_chill = iapws95_Psat(T_CHILL) / 1000.0 / P_CHILL
    n_w_chill = y_chill / (1 - y_chill) * dry
    rec_w_chill = n_w_chill / up["H2O"]
    cond_chill = (up["H2O"] - n_w_chill) * MW["H2O"]
    dew_c = iapws95_Tsat(y_chill * P_MEM * 1000.0) - 273.15
    # heat removed: the gas and vapour cooled as ideal gas, and the condensate's heat of
    # vaporisation at the chiller's outlet (the vapour condensed at T_CHILL)
    q_chill = (sum(v * (h(k, T_DIG) - h(k, T_CHILL)) for k, v in up.items())
               + cond_chill * hvap_water(T_CHILL)) / 3600.0
    w_chill = q_chill / COP_CHILL
    print(f"E300: chilled to {T_CHILL:.2f} K, water left in the gas {rec_w_chill:.6f}, condensate "
          f"{cond_chill:.2f} kg/h, duty {q_chill:.2f} kW, chiller power {w_chill:.2f} kW; "
          f"dew point at {P_MEM:.0f} kPa(a) {dew_c:.1f} C")
    y_sat = iapws95_Psat(T_COOL) / 1000.0 / P_MEM
    n_w_left = y_sat / (1 - y_sat) * dry
    rec_w_cool = n_w_left / n_w_chill
    cond_cool = (n_w_chill - n_w_left) * MW["H2O"]
    ret_ch4 = CH4_RECOVERY * up["CH4"]
    ret_co2 = ret_ch4 * (1 - PRODUCT_CH4) / PRODUCT_CH4
    rec_co2 = ret_co2 / up["CO2"]
    print(f"E301: water left in the gas {rec_w_cool:.6f}, condensate {cond_cool:.2f} kg/h; "
          f"M301: CO2 to the product {rec_co2:.6f}")
    prod_kg = ret_ch4 * MW["CH4"] + ret_co2 * MW["CO2"]
    prod_nm3 = (ret_ch4 + ret_co2) * V_N
    lhv_kw = ret_ch4 * lhv
    print(f"Biomethane {prod_kg:.2f} kg/h, {prod_nm3:.2f} Nm3/h, {lhv_kw:.1f} kW (LHV); "
          f"{prod_kg*HOURS/1000:.1f} t/a")

    # ---- electricity (D-009)
    w_upg = E_UPGRADE * up_dry_nm3
    w_ad = AGIT_RUN * sum(w * SRC_DIGESTER_M3 / N_TANKS for w in AGIT_W_M3) / 1000.0 + PUMPS_KW
    w_chill_r = round(w_chill, 2)
    print(f"Power: upgrading {w_upg:.2f} kW, gas chiller {w_chill:.2f} kW, digesters and pumps "
          f"{w_ad:.2f} kW; {(w_upg+w_chill_r+w_ad)/prod_kg:.4f} kWh/kg biomethane")
    # after-coolers E301 (with the compressor's oil cooler): the whole upgrading power is taken to
    # end as heat there (ASSUMED), plus the gas's enthalpy from the chiller's outlet to the
    # after-cooler's outlet and the heat of vaporisation of the water condensed at 1600 kPa(a)
    gas_in = {"CH4": up["CH4"], "CO2": up["CO2"], "H2O": n_w_chill}
    q_cool = (w_upg + (sum(v * (h(k, T_CHILL) - h(k, T_COOL)) for k, v in gas_in.items())
                       + cond_cool * hvap_water(T_COOL)) / 3600.0)
    print(f"E301: heat to the air {q_cool:.2f} kW (upgrading power {w_upg:.2f} kW, gas "
          f"{q_cool - w_upg - cond_cool*hvap_water(T_COOL)/3600:+.2f} kW, condensation "
          f"{cond_cool*hvap_water(T_COOL)/3600:.2f} kW)")

    # ---- cross-checks
    hrt = SRC_DIGESTER_M3 / (feed_mass * 24 / DIGESTATE_RHO)
    digestate = feed_mass - sum(MW[k] * v for k, v in gas.items()) + (up["H2O"] - n_w_left) * MW["H2O"]
    # the digestate cools in the store to 288.15 K (ASSUMED, D-010): its heat to ambient
    q_store = (digestate - cond_chill - cond_cool) / 3600.0 * CP_SUBSTRATE * (T_DIG - 288.15)
    print(f"Digestate store: heat lost to ambient while cooling to 288.15 K {q_store:.1f} kW (D-010)")
    store = digestate * HOURS / 12 * STORE_MONTHS / DIGESTATE_RHO * 1.1
    print(f"HRT on the gross volume {hrt:.1f} d (FNR: {SRC_HRT_D:.0f} d); digestate {digestate:.1f} kg/h; "
          f"6-month store +10 % {store:,.0f} m3 (FNR: {SRC_STORE_M3:,.0f} m3)")

    cases = {"design": {}}
    for i, fid in enumerate(SUBSTRATES, start=1):
        f = feeds[fid]
        cases["design"][f"S{i}"] = {"flow": round(f["flow"], 2),
                                    "composition": {k: round(v, 7) for k, v in mass_frac(f["composition"]).items()}}
    cases["design"]["S13"] = {"flow": round(air_flow, 2),
                              "composition": {k: round(v, 7) for k, v in mass_frac({k: MW[k] * v for k, v in air.items()}).items()}}
    # Q1, the boiler's heat to the hot-water circuit, is B101's conversion duty that propagate
    # writes; the split above makes it equal to q_demand (printed as the cross-check).
    cases["design"]["W1"] = {"duty": round(w_ad, 2)}
    cases["design"]["W2"] = {"duty": round(w_upg, 2)}
    cases["design"]["W3"] = {"duty": w_chill_r}
    # Q3: the heat the chiller takes from the biogas (to its condenser and the air)
    cases["design"]["Q3"] = {"duty": round(q_chill, 2)}
    # Q2: the upgrading power, the gas's cooling and the condensation heat to the air, ASSUMED
    cases["design"]["Q2"] = {"duty": round(q_cool, 2)}
    params = {"V101_H2O_to_gas": rec_w_gas, "X101_split_boiler": split,
              "E300_H2O_to_gas": rec_w_chill, "E301_H2O_to_gas": rec_w_cool,
              "M301_CO2_to_product": rec_co2}
    print("Parameters:", json.dumps({k: round(v, 7) for k, v in params.items()}))
    print("Feeds:", json.dumps(cases["design"], indent=None))
    write_balance_output(cases)


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
