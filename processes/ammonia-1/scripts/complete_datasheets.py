"""Complete the equipment datasheets of ammonia-1 around `cheme datasheets fill` (S7, DESIGN.md D-032).

Run with `cheme run scripts/complete_datasheets.py inputs` before the fill and
`cheme run scripts/complete_datasheets.py final` after it. Provenance only: it records how the
drafts written by `cheme datasheets draft` were completed; every value it writes carries its
source, and assumed values are marked.

inputs  - design pressure and temperature by the D-032 rule from the item's flowsheet streams
          (per side for exchangers), written to the datasheet and the equipment list;
        - a preliminary material class per item (D-032, ASSUMED), datasheet and list;
        - operating conditions per stream where the draft has none;
        - the sizing inputs the fill needs: simulated duties and machine powers from
          process/simulation-run.json and process/flowsheet.yaml, the typical-U row, the
          arrangement and the utility temperatures (D-012, D-015, D-017), pump parameters.
final   - the fields core does not calculate (rating, mechanical design, corrosion allowance,
          relief) and the values awaited from a licensor or vendor become `supplier` markers
          with what is awaited; every other TBD is reported and keeps the sheet a draft;
        - a sheet without a TBD loses `draft: true`.
"""

import json
import math
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(".")
DS = ROOT / "equipment" / "datasheets"
LIST = ROOT / "equipment" / "equipment-list.yaml"
P_ATM = 101.325  # kPa

FS = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text())
MAT = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())
RUN = json.loads((ROOT / "process" / "simulation-run.json").read_text())["cases"]["design"]
STREAMS = {s["id"]: s for s in FS["streams"]}
MW = {c["id"]: c["molar_mass"] for c in MAT["components"]}
UNITS = {u["id"]: u.get("results", {}) for u in RUN["units"]}
SIM = "process/simulation-run.json (case design, cheme process simulate, DWSIM 9.0.5, Peng-Robinson, D-026)"

D032 = "DESIGN.md D-032"
RULE_P = ("design pressure = max(1.10 x, +1.7 bar over) the maximum operating gauge pressure, rounded up "
          "to 0.5 bar (heuristic '10 % or 10-25 psi, whichever is greater' of Walas, Chemical Process "
          "Equipment, 1988, Rules of Thumb, and Turton et al., 4th ed., 2012, as summarised by the "
          "Northwestern University Process Design wiki, 'Pressure Vessels'; the books were not read; the "
          "upper end 1.7 bar taken), D-032")
RULE_T = ("design temperature = maximum operating temperature + 28 K (50 degF of Towler and Sinnott, "
          "Chemical Engineering Design, 2nd ed., 2013 / UOP and of Walas 1988, as summarised by the "
          "Northwestern University Process Design wiki, 'Pressure Vessels'; at least Turton's 25 degC), "
          "rounded up to 5 degC, D-032")
RULE_MDMT = ("minimum design metal temperature = minimum operating temperature - 14 K (25 degF, Towler and "
             "Sinnott 2013 as summarised by the Northwestern Process Design wiki, Pressure Vessels), "
             "rounded down to 5 degC, D-032")

# ---- utility conditions used as the other side ------------------------------------------------
NH3_PSAT_313 = 1554.5  # kPa(a), thermo 0.6.1 Chemical('ammonia').Psat at 313.15 K (HEOS fit)
CW = {"utility_inlet_temperature_degc": (25.0, "DESIGN.md D-012 cooling water supply 298.15 K"),
      "utility_outlet_temperature_degc": (35.0, "DESIGN.md D-012 cooling water return 308.15 K")}
MP_BOIL = {"utility_inlet_temperature_degc": (258.78, "saturation of MP steam at 4600 kPa(a), 531.93 K (stream S69, IAPWS, D-015)"),
           "utility_outlet_temperature_degc": (258.78, "saturation of MP steam at 4600 kPa(a), 531.93 K (stream S69, IAPWS, D-015)")}
REFRIG = {"utility_inlet_temperature_degc": (-15.0, "DESIGN.md D-017 ammonia refrigerant evaporating at 258.15 K"),
          "utility_outlet_temperature_degc": (-15.0, "DESIGN.md D-017 ammonia refrigerant evaporating at 258.15 K")}

CW_SIDE = ("supplier", "cooling-water side design pressure: the site cooling-water system's design pressure "
           "(owner's utility specification; the design basis gives temperatures only, D-012)")
FLUE_SIDE = ("supplier", "flue-gas side: part of the H-101 convection casing, designed for draft by the furnace vendor")
MP_SIDE = (4600.0, "MP steam system 4600 kPa(a) (design basis utilities, D-015)")
NH3_SIDE = (NH3_PSAT_313, "ammonia refrigerant settle-out at the condensing temperature 313.15 K: vapour pressure "
            "1554.5 kPa(a) (thermo 0.6.1, HEOS fit; D-017)")
REGEN_SIDE = (150.0, "CO2 regenerator pressure 150 kPa(a) (stream S28, D-009)")
ABS_SIDE = (3100.0, "CO2 absorber pressure 3100 kPa(a) (D-009)")
# Every solvent-wetted item is below the hot outlet of the kettle reboiler E-202 (S22): the pool
# boils below the temperature of every point of the heating side.
SOLVENT_TMAX = (422.284, "bound of the aMDEA loop: E-202 process-gas outlet S22 422.28 K (calculated, D-026); "
                "the kettle pool boils below it (D-032)")

# ---- preliminary material classes (D-032, ASSUMED) --------------------------------------------
CS = ("carbon steel (grade by the materials review)", "carbon_steel")
LA = ("low-alloy Cr-Mo steel (grade by the materials review)", "low_alloy_steel")
SS = ("austenitic stainless steel (grade by the materials review)", "stainless_steel")
LT = ("low-temperature carbon steel, impact tested (grade by the materials review)", "low_temperature_carbon_steel")
LINED = ("steel shell with internal refractory lining (by the vendor)", "lined_steel")
HP = ("centrifugally cast heat-resistant alloy tubes (grade by the furnace vendor)", "other")
PKG = ("package materials by the vendor (cryogenic cold box)", "other")

H2_HOT = "hydrogen-bearing gas above the carbon-steel range of API RP 941 (Nelson curves)"
WET_CO2 = "wet CO2 condensate (carbonic acid corrosion of carbon steel)"
COLD = "below -29 degC minimum metal temperature: impact-tested steel"
AMDEA = "aMDEA service: licensor's materials to confirm (I-06)"

LICENSOR = "aMDEA licensor's solvent-loop design (solvent rate, heat balance, column internals; I-06, D-009)"
CAT_VENDOR = ("catalyst vendor's bed design: no catalyst space velocity or bed data with a source is declared "
              "in process/ (no process/catalysts.yaml), so cheme datasheets fill cannot size the bed (D-032)")
PKG_VENDOR = "package vendor's design (the package is a lumped flowsheet step with specified performance)"

# ---- per item ----------------------------------------------------------------------------------
# sides: name -> list of stream ids, or ("const", kPa(a), source), or ("marker", kind, reason)
# p_points / t_points: replace the item's own streams for the design-condition rule
# ts: type_specific values set before the fill (tuples (value, unit, source, assumed))
# markers: type_specific fields -> (kind, reason) written at the final step when still TBD
# design_p_marker: the design pressure is not set by the rule (casing designed by the vendor)

def q(sid):
    return STREAMS[sid]["state"]["design"]["duty"]["value"]

def sim(unit, key="duty_kW"):
    return abs(UNITS[unit][key])

ITEMS = {
    "V-101": {"mat": (*LA, H2_HOT + ": hydrogenation feed at 370 degC")},
    "R-100": {"mat": (*LA, H2_HOT),
              "markers": {k: ("supplier", CAT_VENDOR) for k in ("catalyst_mass_kg", "catalyst_volume_m3", "pressure_drop_kpa", "volume_m3")}},
    "H-101": {"mat": (*LINED, "fired box: refractory-lined casing"),
              "design_p_marker": "firebox casing design pressure (draft, fan shut-off) by the furnace vendor",
              "ts": {"duty_kw": (sim("R101"), "kW", f"absorbed radiant duty = R-101 duty Q9, {SIM} unit R101", False),
                     "fired_duty_lhv_kw": (121500.0, "kW", "DESIGN.md D-014 (concept balance, about 121.5 MW fuel LHV; H101 is not simulated, D-024)", True)},
              "markers": {"rating": ("supplier", "furnace vendor's radiant and convection design (burners, tube layout, efficiency)")}},
    "R-101": {"mat": (*HP, "reformer tubes at 810 degC outlet, metal above it: heat-resistant cast alloy"),
              "ts": {"duty_kw": (sim("R101"), "kW", f"{SIM} unit R101 (= Q9)", False)},
              "markers": {"area_m2": ("supplier", "furnace vendor's radiant tube design (tube count, length, heat flux): no typical-U row applies to radiant heat transfer")}},
    "E-101": {"mat": (*LA, "tube metal in the flue-gas path above the 370 degC process outlet"),
              "sides": {"process": ["S3", "S4"], "flue_gas": ("marker",) + FLUE_SIDE},
              "ts": {"duty_kw": (sim("E101"), "kW", f"{SIM} unit E101", False)}, "two": (("S82", "S83"), ("S3", "S4")),
              "u": "heater/flue-gases-hydrocarbon-vapours", "arr": "counter-current"},
    "E-102": {"mat": (*SS, "flue gas to 737 degC, mixed feed to 500 degC: tube metal temperature"),
              "sides": {"process": ["S7", "S8"], "flue_gas": ("marker",) + FLUE_SIDE},
              "ts": {"duty_kw": (sim("E102"), "kW", f"{SIM} unit E102", False)}, "two": (("S80", "S81"), ("S7", "S8")),
              "u": "heater/flue-gases-hydrocarbon-vapours", "arr": "counter-current"},
    "E-103": {"mat": (*SS, "flue gas from 1050 degC, process gas to 620 degC: tube metal temperature"),
              "sides": {"process": ["S9", "S10"], "flue_gas": ("marker",) + FLUE_SIDE},
              "ts": {"duty_kw": (sim("E103"), "kW", f"{SIM} unit E103", False)}, "two": (("S65", "S80"), ("S9", "S10")),
              "u": "heater/flue-gases-hydrocarbon-vapours", "arr": "counter-current"},
    "E-104": {"mat": (*LA, "process air to 500 degC: creep range of carbon steel"),
              "sides": {"process_air": ["S13", "S14"], "flue_gas": ("marker",) + FLUE_SIDE},
              "ts": {"duty_kw": (sim("E104"), "kW", f"{SIM} unit E104", False)}, "two": (("S81", "S82"), ("S13", "S14")),
              "u": "exchanger/gases-gases", "arr": "counter-current"},
    "E-106": {"mat": (*CS, "air to 250 degC, flue gas from 326 degC; cold-end dew point to be checked by the vendor"),
              "design_p_marker": "air preheater ducting and casing design pressure (draft, fan shut-off) by the vendor",
              "ts": {"duty_kw": (sim("E106"), "kW", f"{SIM} unit E106", False)}, "two": (("S83", "S84"), ("S62", "S63")),
              "u": "exchanger/gases-gases", "arr": "counter-current"},
    "E-107": {"mat": (*CS, "boiler feed water and flue gas below 150 degC"),
              "sides": {"bfw": ("const",) + MP_SIDE, "flue_gas": ("marker",) + FLUE_SIDE},
              "t_points": [(406.893, "flue gas inlet S84 (calculated): the boiler feed water stays below it")],
              "ts": {"duty_kw": (q("Q8"), "kW", "process/flowsheet.yaml Q8 (calculated; the duty specified in process/simulation.yaml E107 is the concept balance's, D-014, D-024)", True)},
              "markers": {"area_m2": ("supplier", "the boiler-feed-water side belongs to the lumped steam system U-801 (D-015) and its temperatures are not modelled; flue gas 406.9 K in (S84, calculated) and 396.7 K stack (simulated, D-026; S66 keeps the assumed 423.15 K); area by the furnace vendor with the BFW conditions")}},
    "K-101": {"mat": (*CS, "air at 15-160 degC"),
              "stages": [("S12", 288.15, 2.4415), ("S12", 313.15, 2.4415), ("S86", 313.15, 3600 / 1474.6)],
              "ts": {"fluid_power_kw": (q("Q1") + q("Q37"), "kW", f"gas power Q1 + Q37 (stages 1-3 and 4), {SIM} units K101, K101D, isentropic efficiency 0.78 (D-016)", True),
                     "number_of_stages": (4, "", "process/simulation.yaml K101 (3 intercooled stages) + K101D (uncooled fourth stage), D-016, D-024", True),
                     "intercooler_duty_kw": (q("Q2"), "kW", f"Q2, {SIM} unit K101 cooling_kW", False)}},
    "K-102": {"mat": (*CS, "ambient air"),
              "design_p_marker": "fan casing design pressure (shut-off) by the fan vendor",
              "ts": {"fluid_power_kw": (q("Q11"), "kW", f"Q11, {SIM} unit K102, efficiency 0.70 (D-014)", True)},
              "flow_from": "S61"},
    "K-103": {"mat": (*CS, "flue gas at 130-150 degC"),
              "design_p_marker": "fan casing design pressure (shut-off) by the fan vendor",
              "ts": {"fluid_power_kw": (q("Q12"), "kW", f"Q12, {SIM} unit K103, efficiency 0.70 (D-014)", True)},
              "flow_from": "S66"},
    "R-102": {"mat": (*LINED, "burner zone at about 1290 degC: refractory-lined shell"),
              "markers": {k: ("supplier", CAT_VENDOR) for k in ("catalyst_mass_kg", "catalyst_volume_m3", "pressure_drop_kpa", "volume_m3")}},
    "E-105": {"mat": (*LA, "process gas from 992 degC (refractory-lined hot channel by the vendor) in hydrogen service"),
              "sides": {"process": ["S17", "S18"], "steam": ("const",) + MP_SIDE},
              "ts": {"duty_kw": (sim("E105"), "kW", f"{SIM} unit E105 (= Q10)", False)},
              "u": "heater/flue-gases-steam", "arr": "counter-current", "util": MP_BOIL},
    "R-201": {"mat": (*LA, H2_HOT),
              "markers": {k: ("supplier", CAT_VENDOR) for k in ("catalyst_mass_kg", "catalyst_volume_m3", "pressure_drop_kpa", "volume_m3")}},
    "E-201": {"mat": (*LA, H2_HOT),
              "sides": {"process": ["S19", "S75"], "steam": ("const",) + MP_SIDE},
              "ts": {"duty_kw": (sim("E201"), "kW", f"{SIM} unit E201 (= Q13)", False)},
              "u": "heater/flue-gases-steam", "arr": "counter-current", "util": MP_BOIL},
    "R-202": {"mat": (*LA, H2_HOT + " (235 degC at 32 bar)"),
              "markers": {k: ("supplier", CAT_VENDOR) for k in ("catalyst_mass_kg", "catalyst_volume_m3", "pressure_drop_kpa", "volume_m3")}},
    "E-202": {"mat": (*SS, WET_CO2 + " on the process side; " + AMDEA),
              "sides": {"process": ["S21", "S22"], "solvent": ("const",) + REGEN_SIDE},
              "ts": {"duty_kw": (sim("E202"), "kW", f"{SIM} unit E202 (= Q15, regeneration heat 1.0 MJ/kg CO2, D-009)", True)},
              "markers": {"area_m2": ("supplier", "the solvent-side boiling temperature is the aMDEA licensor's (I-06, D-009): no utility temperature to size against")}},
    "E-203": {"mat": (*SS, WET_CO2),
              "sides": {"process": ["S22", "S23"], "cooling_water": ("marker",) + CW_SIDE},
              "ts": {"duty_kw": (sim("E203"), "kW", f"{SIM} unit E203 (= Q16)", False)},
              "u": "cooler/gases-water", "arr": "counter-current", "util": CW},
    "V-201": {"mat": (*SS, WET_CO2)},
    "C-301": {"mat": (*CS, AMDEA), "t_points": [SOLVENT_TMAX],
              "markers": {"number_of_stages": ("supplier", LICENSOR + ": a reactive amine absorber is not a Fenske-Underwood-Gilliland column"),
                          "flooding_diameter_m": ("supplier", LICENSOR)}},
    "C-302": {"mat": (*SS, WET_CO2 + "; " + AMDEA), "p_points": [REGEN_SIDE], "t_points": [SOLVENT_TMAX],
              "markers": {"number_of_stages": ("supplier", LICENSOR + ": a reactive amine stripper is not a Fenske-Underwood-Gilliland column"),
                          "flooding_diameter_m": ("supplier", LICENSOR)}},
    "P-301A": {"mat": (*SS, AMDEA), "nostream": True, "p_points": [ABS_SIDE], "t_points": [SOLVENT_TMAX],
               "design_p_marker": "pump casing design pressure: shut-off pressure from the vendor's curve",
               "ts": {"flow_m3_h": "co2_solvent",
                      "shaft_power_kw": (q("Q17"), "kW", "process/flowsheet.yaml Q17 (assumed: 21 kWh/t CO2, D-009), the whole solvent pumping of the loop on the running pump", True)},
               "markers": {k: ("supplier", LICENSOR + ": solvent density, regenerator elevation and suction line") for k in ("differential_head_m", "npsh_available_m")}},
    "P-301B": {"same": "P-301A"},
    "E-302": {"mat": (*SS, AMDEA), "nostream": True, "t_points": [SOLVENT_TMAX],
              "sides": {"solvent": ("const",) + ABS_SIDE, "cooling_water": ("marker",) + CW_SIDE},
              "markers": {k: ("supplier", LICENSOR + ": E-302 and E-303 share Q18 (21.9 MW, assumed, D-009), the split is the licensor's") for k in ("duty_kw", "area_m2")}},
    "E-301": {"mat": (*SS, AMDEA), "nostream": True, "t_points": [SOLVENT_TMAX],
              "sides": {"rich_solvent": ("const",) + ABS_SIDE, "lean_solvent": ("const",) + REGEN_SIDE},
              "markers": {k: ("supplier", LICENSOR + ": lean/rich duty from the solvent rate and temperatures") for k in ("duty_kw", "area_m2")}},
    "E-303": {"mat": (*SS, WET_CO2), "nostream": True, "t_points": [SOLVENT_TMAX],
              "sides": {"overhead": ("const",) + REGEN_SIDE, "cooling_water": ("marker",) + CW_SIDE},
              "markers": {k: ("supplier", LICENSOR + ": E-302 and E-303 share Q18 (21.9 MW, assumed, D-009), the split is the licensor's") for k in ("duty_kw", "area_m2")}},
    "V-302": {"mat": (*SS, WET_CO2), "nostream": True, "p_points": [REGEN_SIDE], "t_points": [SOLVENT_TMAX]},
    "P-302A": {"mat": (*SS, WET_CO2), "nostream": True, "p_points": [REGEN_SIDE], "t_points": [SOLVENT_TMAX],
               "design_p_marker": "pump casing design pressure: shut-off pressure from the vendor's curve",
               "markers": {k: ("supplier", LICENSOR + ": reflux rate and the regenerator's reflux elevation") for k in ("flow_m3_h", "differential_head_m", "npsh_available_m", "shaft_power_kw")}},
    "P-302B": {"same": "P-302A"},
    "E-401": {"mat": (*LA, H2_HOT),
              "sides": {"hot_hts_effluent": ["S75", "S20"], "cold_methanator_feed": ["S27", "S29"]},
              "ts": {"duty_kw": (sim("E401"), "kW", f"{SIM} unit E401", False)}, "two": (("S75", "S20"), ("S27", "S29")),
              "u": "exchanger/gases-gases", "arr": "counter-current"},
    "R-401": {"mat": (*LA, H2_HOT),
              "markers": {k: ("supplier", CAT_VENDOR) for k in ("catalyst_mass_kg", "catalyst_volume_m3", "pressure_drop_kpa", "volume_m3")}},
    "E-402": {"mat": (*LA, H2_HOT + " (inlet 317 degC)"),
              "sides": {"process": ["S30", "S31"], "cooling_water": ("marker",) + CW_SIDE},
              "ts": {"duty_kw": (sim("E402"), "kW", f"{SIM} unit E402 (= Q19)", False)},
              "u": "cooler/gases-water", "arr": "counter-current", "util": CW},
    "V-401": {"mat": (*CS, "dry synthesis gas and condensate at 40 degC")},
    "X-401": {"mat": (*CS, "synthesis gas at 40 degC; adsorbent and regeneration by the package vendor"),
              "markers": {"volume_m3": ("supplier", PKG_VENDOR + ": adsorbent volume and regeneration, I-05")}},
    "K-501": {"mat": (*CS, "synthesis gas at 40-110 degC"),
              "stages": [("S37", 313.15, (14600 / 2850) ** (1 / 3))],
              "ts": {"fluid_power_kw": (q("Q20"), "kW", f"Q20, {SIM} unit K501, isentropic efficiency 0.78 (D-016)", True),
                     "number_of_stages": (3, "", "process/simulation.yaml K501 stages 3 (D-011)", True),
                     "intercooler_duty_kw": (q("Q21"), "kW", f"Q21 (intercoolers and aftercooler), {SIM} unit K501 cooling_kW", False)}},
    "K-502": {"mat": (*CS, "synthesis gas at 30-40 degC"),
              "ts": {"fluid_power_kw": (q("Q22"), "kW", f"Q22, {SIM} unit K502, isentropic efficiency 0.78 (D-016)", True),
                     "number_of_stages": (1, "", "process/simulation.yaml K502 (one casing, D-011)", True)}},
    "E-501": {"mat": (*LA, H2_HOT + " at 150 bar"),
              "sides": {"cold_converter_feed": ["S41", "S42"], "hot_converter_effluent": ["S44", "S45"]},
              "ts": {"duty_kw": (sim("E501"), "kW", f"{SIM} unit E501", False)}, "two": (("S44", "S45"), ("S41", "S42")),
              "u": "exchanger/gases-gases", "arr": "counter-current"},
    "R-501": {"mat": (*LA, H2_HOT + "; nitriding of the internals by the vendor"),
              "markers": {k: ("supplier", CAT_VENDOR) for k in ("catalyst_mass_kg", "catalyst_volume_m3", "pressure_drop_kpa", "volume_m3")}},
    "E-502": {"mat": (*LA, H2_HOT + " at 150 bar"),
              "sides": {"process": ["S43", "S44"], "steam": ("const",) + MP_SIDE},
              "ts": {"duty_kw": (sim("E502"), "kW", f"{SIM} unit E502 (= Q23)", False)},
              "u": "heater/flue-gases-steam", "arr": "counter-current", "util": MP_BOIL},
    "E-503": {"mat": (*CS, "loop gas at 40-70 degC"),
              "sides": {"process": ["S45", "S46"], "cooling_water": ("marker",) + CW_SIDE},
              "ts": {"duty_kw": (sim("E503"), "kW", f"{SIM} unit E503 (= Q24)", False)},
              "u": "cooler/gases-water", "arr": "counter-current", "util": CW},
    "E-505": {"mat": (*LT, COLD + " (recycle gas from -10 degC)"),
              "sides": {"hot_chiller_feed": ["S46", "S47"], "cold_recycle_gas": ["S51", "S39"]},
              "ts": {"duty_kw": (sim("E505"), "kW", f"{SIM} unit E505", False)}, "two": (("S46", "S47"), ("S51", "S39")),
              "u": "exchanger/gases-gases", "arr": "counter-current"},
    "E-504": {"mat": (*LT, COLD),
              "sides": {"process": ["S47", "S48"], "refrigerant": ("const",) + NH3_SIDE},
              "ts": {"duty_kw": (sim("E504"), "kW", f"{SIM} unit E504 (= Q25)", False)},
              "u": "cooler/gases-brine", "arr": "counter-current", "util": REFRIG},
    "V-501": {"mat": (*LT, COLD)},
    "V-502": {"mat": (*LT, COLD)},
    "V-701": {"mat": (*LT, COLD + " (-34 degC; the minimum design metal temperature is below the usual LTCS limit: materials review)")},
    "K-701": {"mat": (*LT, COLD + " (suction from -35 degC)"), "p_points": [NH3_SIDE, (1700.0, "flash-gas stages discharge 1700 kPa(a) (D-017)")],
              "t_points": [(313.15, "condensing 313.15 K (D-017)"), (238.7, "flash gas S88 238.7 K (calculated)")],
              "stages": [("S88", 238.7, (1700 / 110) ** 0.5), ("S88", 313.15, (1700 / 110) ** 0.5)],
              "design_note": "the design temperature covers the flash-gas stages (K702); the refrigeration circuit's own staging and discharge temperatures are the package vendor's",
              "ts": {"fluid_power_kw": (q("Q27") + q("Q32"), "kW", "Q27 refrigeration compressor (assumed, 0.55 of Carnot, scripts/packages_on_simulated_duties.py, D-017, D-026) + Q32 flash-gas stages (calculated, " + SIM + " unit K702)", True)},
              "markers": {"number_of_stages": ("supplier", "refrigeration package vendor: the refrigeration circuit is an energy-only package (D-026); the flash-gas stages are 2 (process/simulation.yaml K702)")}},
    "E-701": {"mat": (*CS, "ammonia refrigerant condensing at 40 degC"),
              "sides": {"refrigerant": ("const", 1700.0, "flash-gas stages discharge 1700 kPa(a) condensing here (Q33, D-017), above the refrigerant's settle-out 1554.5 kPa(a) at 313.15 K"),
                        "cooling_water": ("marker",) + CW_SIDE},
"t_points": [(313.15, "condensing 313.15 K (D-017)"), (238.7, "flash gas S88 238.7 K (calculated)")],
              "ts": {"duty_kw": (q("Q28") + q("Q33"), "kW", "Q28 refrigerant condenser (assumed, scripts/packages_on_simulated_duties.py, D-026) + Q33 flash-gas intercooler and condenser (calculated, " + SIM + " unit K702 cooling_kW)", True)},
              "manual_area": {"u_row": "condenser/organic-vapours-water", "why": "wrong-node",
                              "hot": (313.15, 313.15, "ammonia condensing, D-017"),
                              "cold": (298.15, 308.15, "cooling water, D-012")}},
    "X-601": {"mat": (*PKG, COLD + "; cryogenic cold box"),
              "markers": {"volume_m3": ("supplier", PKG_VENDOR + ": NH3 wash, distillation and cold box (D-013)")}},
    "U-801": {"mat": (*CS, "boiler water and MP steam at 400 degC (superheater alloy by the vendor)"),
              "p_points": [(4600.0, "MP steam 4600 kPa(a) (D-015)")],
              "markers": {"volume_m3": ("supplier", PKG_VENDOR + ": deaerator, steam drums, superheater and let-down (D-015)")}},
    "P-801": {"mat": (*SS, "boiler feed water: 12-13 % Cr casing usual (ASSUMED)"),
              "p_points": [(5600.0, "BFW pump discharge 5600 kPa(a) = steam 4600 + 1000 kPa allowance (scripts/packages_on_simulated_duties.py, D-015)")],
              "t_points": [(313.15, "boiler feed water 313.15 K (D-015)")],
              "design_p_marker": "pump casing design pressure: shut-off pressure from the vendor's curve",
              "pump": True},
}

# Datasheet values of the cold box etc. that are not their own fields
GENERIC = {
    "rating": "vendor's thermal, hydraulic or machine rating on these process conditions (not calculated by cheme-as-code, docs/framework/sizing.md)",
    "mechanical_design": "vendor's mechanical design to the code on the design conditions of this sheet (wall thickness, MAWP, nozzle loads)",
    "corrosion_allowance_mm": "corrosion allowance from the materials and corrosion review with the vendor; the material class on this sheet is preliminary (D-032)",
    "relief_protection": "relief study, section S8 (skill relief-scenarios): governing case, device and set pressure; the devices drawn are listed in piping/special-items.yaml",
    "npsh_required_m": "pump vendor's NPSHr at the rated point",
    "shaft_power_kw": ("machine vendor's shaft power: the fluid power on this sheet over the mechanical efficiency "
                       "(bearings, seals, gear), which no source in DESIGN.md gives"),
    "flooding_diameter_m": LICENSOR,
}


def ceil_to(x, step):
    return math.ceil(x / step - 1e-9) * step


def floor_to(x, step):
    return math.floor(x / step + 1e-9) * step


def state(sid):
    return STREAMS[sid].get("state", {}).get("design", {})


def val(sid, key):
    v = state(sid).get(key)
    return None if v is None else v.get("value")


def prov(sid, key):
    v = state(sid).get(key, {})
    p = v.get("provenance", "")
    return f"{p}: {v.get('source', '')}".strip(": ")


def design_p(points):
    pmax = max(p for p, _ in points)
    pg = (pmax - P_ATM) / 100.0
    return ceil_to(max(1.10 * pg, pg + 1.7), 0.5), pmax


def design_t(tmax):
    return ceil_to(tmax - 273.15 + 28.0, 5.0)


def mdmt(tmin):
    return floor_to(tmin - 273.15 - 14.0, 5.0)


def item_streams(d):
    """Material streams of the item (internal streams that enter and leave its nodes once each are kept once)."""
    out = []
    for p in d.get("type_specific", {}).get("process_streams", []) or []:
        sid = p["stream"]
        if sid.startswith("Q") or sid in out:
            continue
        out.append(sid)
    return out


def qty(value, unit, source, assumed=False):
    d = {"value": value, "unit": unit, "source": source}
    if assumed:
        d["assumed"] = True
    return d


def marker(kind, reason, unit=""):
    if kind == "supplier":
        return {"value": "supplier", "unit": unit, "source": reason, "reason": reason}
    return {"value": "not_applicable", "unit": unit, "reason": reason}


def is_tbd(v):
    return isinstance(v, dict) and v.get("value") == "TBD" or v == "TBD"


def load(tag):
    path = DS / f"{tag}.yaml"
    text = path.read_text()
    header = "".join(l + "\n" for l in text.splitlines() if l.startswith("#"))
    return path, header, yaml.safe_load(text)


def dump(path, header, d):
    body = yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100)
    path.write_text(header + body)


def cfg(tag):
    c = ITEMS.get(tag, {})
    if "same" in c:
        base = dict(ITEMS[c["same"]])
        return base
    return c


def conditions(tag, d, c):
    """(p points, t points, sides) for the design rule."""
    sids = item_streams(d)
    p_pts = [(val(s, "pressure"), f"stream {s} ({prov(s, 'pressure')})") for s in sids if val(s, "pressure") is not None]
    t_pts = [(val(s, "temperature"), f"stream {s} ({prov(s, 'temperature')})") for s in sids if val(s, "temperature") is not None]
    if "p_points" in c:
        p_pts = list(c["p_points"])
    if "t_points" in c:
        t_pts = list(c["t_points"])
    sides = c.get("sides") or {}
    if any(not isinstance(s, list) and s[1:] == FLUE_SIDE for s in sides.values()):
        # a convection coil: the tubes are designed for the process side; the flue-gas casing and
        # the tube metal temperature in the flue gas are the furnace vendor's
        coil = [s for spec in sides.values() if isinstance(spec, list) for s in spec]
        if coil and "t_points" not in c:
            t_pts =[(val(s, "temperature"), f"stream {s} ({prov(s, 'temperature')})") for s in coil]
    return p_pts, t_pts


def side_design(c):
    out = {}
    for name, spec in (c.get("sides") or {}).items():
        if isinstance(spec, list):
            pts = [(val(s, "pressure"), f"stream {s}") for s in spec]
            out[name] = ("value",) + design_p(pts) + (", ".join(s for _, s in pts),)
        elif spec[0] == "const":
            out[name] = ("value",) + design_p([(spec[1], spec[2])]) + (spec[2],)
        else:
            out[name] = ("marker", spec[1], spec[2])
    return out


def operating_from_streams(tag, d):
    steps = set()
    for s in FS.get("steps", []):
        for l in s.get("links", []) or []:
            if l.get("target") == "equipment" and l.get("ref") == tag:
                steps.add(s["id"])
    op = {}
    used = []
    for sid in item_streams(d):
        s = STREAMS[sid]
        to, fr = s.get("to", ""), s.get("from", "")
        if to.split(".")[0] in steps and fr.split(".")[0] in steps:
            continue  # internal stream between the item's own nodes
        port = to if to.split(".")[0] in steps else fr
        label = f"{sid}_{port.split('.')[-1]}"
        for key, unit, name in (("pressure", "kPa(a)", "pressure"), ("temperature", "K", "temperature"), ("flow", "kg/h", "flow")):
            v = val(sid, key)
            if v is None:
                continue
            p = state(sid)[key]
            op[f"{label}_{name}"] = qty(v, unit, f"process/flowsheet.yaml stream {sid} (case design), {prov(sid, key)}",
                                        p.get("provenance") == "assumed")
        used.append(sid)
    return op, used


def ideal_gas_flow(sid):
    comp = state(sid)["composition"]["values"]
    mw = sum(x * MW[c] for c, x in comp.items())
    m = val(sid, "flow")
    rho = val(sid, "pressure") * mw / (8.314462 * val(sid, "temperature"))
    return m / rho / 3600.0, mw, rho


def co2_solvent_rate():
    """D-009: 18 m3 solvent per t CO2 (assumed); CO2 in the vent S28."""
    s = state("S28")
    comp = s["composition"]["values"]
    mw = sum(x * MW[c] for c, x in comp.items())
    w_co2 = comp["CO2"] * MW["CO2"] / mw
    t_co2 = val("S28", "flow") * w_co2 / 1000.0
    return 18.0 * t_co2, t_co2


def list_update(rows):
    text = LIST.read_text()
    # a rerun replaces what an earlier run wrote
    text = re.sub(r'(design_pressure_barg: [0-9.]+, )?design_temperature_degc: -?[0-9.]+, material: "[^"]*", ', "", text)
    for tag, (p, t, m) in rows.items():
        pat = re.compile(r"(\{tag: " + re.escape(tag) + r", sheet: [^,]+, type: [^,]+, )")
        parts = []
        if p is not None:
            parts.append(f"design_pressure_barg: {p:g}")
        parts.append(f"design_temperature_degc: {t:g}")
        parts.append(f'material: "{m}"')
        new, n = pat.subn(lambda mo: mo.group(1) + ", ".join(parts) + ", ", text)
        if n != 1:
            raise SystemExit(f"{tag}: {n} matches in the equipment list")
        text = new
    LIST.write_text(text)


def inputs():
    rows = {}
    for path in sorted(DS.glob("*.yaml")):
        _, header, d = load(path.stem)
        tag = d["tag"]
        c = cfg(tag)
        if not c:
            raise SystemExit(f"{tag}: no entry in ITEMS")
        ts = d.setdefault("type_specific", {})
        # operating conditions
        if c.get("nostream"):
            op = {}
            for pt in c.get("p_points", []):
                op["operating_pressure"] = qty(pt[0], "kPa(a)", pt[1], True)
            for pt in c.get("t_points", []):
                op["maximum_temperature"] = qty(pt[0], "K", pt[1], True)
            d["operating"] = op
        elif not d.get("operating"):
            op, used = operating_from_streams(tag, d)
            d["operating"] = op
        d["operating"]["case"] = "design"
        # design conditions
        p_pts, t_pts = conditions(tag, d, c)
        if c.get("stages"):
            # the stage discharge before each intercooler is the hottest gas in the casing
            res = [stage_discharge(*s) for s in c["stages"]]
            stage_t = [t for t, _ in res]
            stage_src = max(res)[1]
            t_pts.append(max(res))
        sides = side_design(c)
        design = {}
        if c.get("design_p_marker"):
            design["pressure_barg"] = marker("supplier", c["design_p_marker"], "barg")
            pd = None
        else:
            if sides:
                vals = [(s[1], s[2], s[3], n) for n, s in sides.items() if s[0] == "value"]
                pd, pmax, src, n = max(vals)
                design["pressure_barg"] = qty(pd, "barg", f"{RULE_P}; governing side {n}: {pmax:g} kPa(a) from {src}", True)
            else:
                pd, pmax = design_p(p_pts)
                src = next(s for p, s in p_pts if p == pmax)
                design["pressure_barg"] = qty(pd, "barg", f"{RULE_P}; maximum operating {pmax:g} kPa(a): {src}", True)
        for n, s in sides.items():
            if s[0] == "value":
                design[f"{n}_pressure_barg"] = qty(s[1], "barg", f"{RULE_P}; {s[2]:g} kPa(a) from {s[3]}", True)
            else:
                design[f"{n}_pressure_barg"] = marker(s[1], s[2], "barg")
        tmax = max(t for t, _ in t_pts)
        tsrc = next(s for t, s in t_pts if t == tmax)
        td = design_t(tmax)
        design["temperature_degc"] = qty(td, "degC", f"{RULE_T}; maximum operating {tmax:.2f} K: {tsrc}", True)
        tmin = min(t for t, _ in t_pts)
        if tmin < 273.15:
            tsrc = next(s for t, s in t_pts if t == tmin)
            design["minimum_design_metal_temperature_degc"] = qty(mdmt(tmin), "degC", f"{RULE_MDMT}; minimum operating {tmin:.2f} K: {tsrc}", True)
        if tmax - 273.15 > 345:
            design["note"] = ("above 345 degC the D-032 margin is a process allowance; the metal temperature "
                              "(refractory, tube wall, flue-gas side) is the vendor's")
        if c.get("design_note"):
            design["note"] = c["design_note"]
        d["design"] = design
        # material
        mval, mclass, why = c["mat"]
        d["materials"] = {"main": {"value": mval, "material_class": mclass, "assumed": True,
                                   "source": f"{D032}: preliminary material class by service ({why}); the materials selection review is open"}}
        rows[tag] = (pd, td, mval)
        # sizing inputs
        for k, v in (c.get("ts") or {}).items():
            if v == "co2_solvent":
                rate, t_co2 = co2_solvent_rate()
                ts[k] = qty(round(rate, 1), "m3/h", f"18 m3 solvent per t CO2 (assumed, D-009) x {t_co2:.2f} t/h CO2 in the vent S28 (calculated): the whole lean solvent on the running pump", True)
            else:
                ts[k] = qty(round(v[0], 1) if isinstance(v[0], float) else v[0], v[1], v[2], v[3])
        if c.get("u"):
            ts["u_service"] = c["u"]
            ts["arrangement"] = c["arr"]
        for k, (v, src) in (c.get("util") or {}).items():
            ts[k] = qty(v, "degC", src, True)
        if c.get("flow_from"):
            f, mw, rho = ideal_gas_flow(c["flow_from"])
            ts["gas_flow_m3_s"] = qty(round(f, 2), "m3/s", f"inlet stream {c['flow_from']}: m / rho, ideal gas rho = P M / (R T) = {rho:.4f} kg/m3 (M {mw:.2f} kg/kmol from the composition and process/materials.yaml); {D032}", True)
        if c.get("pump"):
            pump_inputs(ts)
            manual_pump(ts)
        if c.get("manual_area"):
            manual_area(ts, c["manual_area"])
        if c.get("two"):
            manual_area(ts, {"u_row": c["u"], "hot": c["two"][0], "cold": c["two"][1], "why": "two-stream"})
        if c.get("stages"):
            ts["stage_discharge_temperature_k"] = qty(round(max(stage_t), 1), "K", stage_src, True)
        hp_note = ("Area: the typical-U row for gases (Sinnott Table 12.1) is for gases near atmospheric "
                   "pressure; at this design pressure the gas film coefficients are higher, so the area is an "
                   "upper bound until the vendor's rating (D-032).")
        notes = (d.get("notes") or "").replace(" " + hp_note, "")
        if c.get("u") and "gases" in c["u"] and pd is not None and pd > 10:
            notes = f"{notes} {hp_note}".strip()
        d["notes"] = notes
        basis = [b for b in (d.get("sizing_basis") or []) if b.get("parameter") not in ("design conditions", "typical overall coefficient")]
        basis.append({"parameter": "design conditions", "value": "rule of D-032 on the item's operating streams", "reference": D032})
        if c.get("u"):
            basis.append({"parameter": "typical overall coefficient", "value": c["u"], "reference": f"{D032} (Sinnott, C&R Vol. 6, 4th ed., Table 12.1)"})
        d["sizing_basis"] = basis
        dump(path, header, d)
    list_update(rows)
    print(f"inputs written for {len(rows)} datasheets and the equipment list")


def pump_inputs(ts):
    from thermo import Chemical
    w = Chemical("water", T=313.15, P=101325.0)
    flow = val("S69", "flow") / 0.02 * 1.02
    ts["mass_flow_kg_h"] = qty(round(flow, 1), "kg/h", "steam raised plus blowdown = S69 / 0.02 x 1.02 (blowdown 2 % of the steam raised, D-015; S69 assumed, scripts/packages_on_simulated_duties.py)", True)
    ts["density_kg_m3"] = qty(round(w.rho, 1), "kg/m3", "water at 313.15 K, 101.325 kPa (thermo 0.6.1 Chemical('water'), IAPWS-95)")
    ts["viscosity_mpa_s"] = qty(round(w.mu * 1000, 3), "mPa s", "water at 313.15 K (thermo 0.6.1 Chemical('water'))")
    ts["vapour_pressure_kpa"] = qty(round(w.Psat / 1000, 2), "kPa", "water at 313.15 K (thermo 0.6.1, IAPWS)")
    ts["suction_pressure_kpa"] = qty(101.325, "kPa(a)", "feed water at ambient pressure, as scripts/packages_on_simulated_duties.py (D-015)", True)
    ts["discharge_pressure_kpa"] = qty(5600.0, "kPa(a)", "MP steam 4600 kPa(a) + 1000 kPa allowance, as scripts/packages_on_simulated_duties.py (D-015)", True)
    ts["pump_efficiency"] = qty(0.70, "", "DESIGN.md D-015/D-016 (ETA_P 0.70 in scripts/plant_balance.py)", True)
    ts["stream_pressures_at"] = "pump"


U_ROWS = {  # middle of the row of `cheme datasheets fill --list` (Sinnott, C&R Vol. 6, 4th ed., Table 12.1)
    "heater/flue-gases-hydrocarbon-vapours": (65.0, "30-100"),
    "exchanger/gases-gases": (30.0, "10-50"),
    "condenser/organic-vapours-water": (850.0, "700-1000"),
}
WHY_MANUAL = {
    "two-stream": ("cheme datasheets fill (core v1.0.x) sizes an exchanger only from a linked node with one "
                   "material inlet and one outlet; this item is one two-stream exchanger node of the "
                   "flowsheet, so the same method (counter-current LMTD, Table 12.1 middle U, no margin) is "
                   "applied here"),
    "wrong-node": ("the linked flowsheet nodes (K702, K701) are the flash-gas compressor's, so cheme "
                   "datasheets fill would take the wrong sides; same method applied here"),
}


def temps(spec):
    """(T in, T out, text) from two stream ids or two numbers with their source."""
    a, b = spec[0], spec[1]
    if isinstance(a, str):
        return val(a, "temperature"), val(b, "temperature"), f"{a} -> {b}"
    return a, b, spec[2]


def manual_area(ts, m):
    duty = ts["duty_kw"]["value"]
    th_in, th_out, th_src = temps(m["hot"])
    tc_in, tc_out, tc_src = temps(m["cold"])
    d1, d2 = th_in - tc_out, th_out - tc_in
    lmtd = (d1 - d2) / math.log(d1 / d2) if abs(d1 - d2) > 1e-6 else d1
    u, u_range = U_ROWS[m["u_row"]]
    area = duty * 1000 / (u * lmtd)
    ts["lmtd_k"] = qty(round(lmtd, 2), "K", f"LMTD counter-current, hot {th_in:.2f} -> {th_out:.2f} K ({th_src}), cold {tc_in:.2f} -> {tc_out:.2f} K ({tc_src}); {D032}", True)
    ts["overall_u_w_m2k"] = qty(u, "W/(m2 K)", f"design typical, middle of {u_range}: Sinnott, Coulson & Richardson's Chemical Engineering Vol. 6, 4th ed. (2005), Table 12.1, {m['u_row']} (the row table of cheme datasheets fill --list); {D032}", True)
    ts["area_m2"] = qty(round(area, 0), "m2", f"A = Q / (U LMTD) = {duty:.1f} kW / ({u:g} x {lmtd:.2f} K), no margin, by scripts/complete_datasheets.py: {WHY_MANUAL[m['why']]}; {D032}", True)


def manual_pump(ts):
    """P-801: linked to the lumped steam system U801 (many streams), which the fill cannot use."""
    g = 9.80665
    m = ts["mass_flow_kg_h"]["value"]
    rho = ts["density_kg_m3"]["value"]
    p_in, p_out = ts["suction_pressure_kpa"]["value"], ts["discharge_pressure_kpa"]["value"]
    pv, eta = ts["vapour_pressure_kpa"]["value"], ts["pump_efficiency"]["value"]
    head = (p_out - p_in) * 1000 / (rho * g)
    npsha = (p_in - pv) * 1000 / (rho * g)
    power = m / 3600 * g * head / eta / 1000
    why = ("by scripts/complete_datasheets.py: cheme datasheets fill sizes a pump only from a linked node with "
           "one inlet and one outlet or from end points in the layout model; P-801 is linked to the lumped "
           "steam system U801; pressures at the pump, no static head or line loss counted (ASSUMED); " + D032)
    ts["flow_m3_h"] = qty(round(m / rho, 1), "m3/h", f"m / rho = {m:.1f} / {rho:.1f}; {why}", True)
    ts["differential_head_m"] = qty(round(head, 1), "m", f"H = (p_out - p_in) / (rho g) = ({p_out:g} - {p_in:g}) kPa / ({rho:.1f} x {g}); {why}", True)
    ts["npsh_available_m"] = qty(round(npsha, 1), "m", f"NPSHa = (p_in - p_vap) / (rho g) = ({p_in:g} - {pv:g}) kPa / ({rho:.1f} x {g}), no static head counted; a deaerator at saturation would leave only its static head: {why}", True)
    ts["shaft_power_kw"] = qty(round(power, 1), "kW", f"P = m g H / eta = {m:.1f} kg/h x {g} x {head:.1f} m / {eta:g}; {why}", True)


def stage_discharge(sid, t1, ratio, eta=0.78):
    """Ideal-gas stage discharge temperature T1 (1 + (r^((k-1)/k) - 1) / eta), k from cp_R of materials.yaml at T1."""
    comp = state(sid)["composition"]["values"]
    cps = {c["id"]: c["ideal_gas"]["cp_R"] for c in MAT["components"] if c.get("ideal_gas")}
    cp_r = sum(x * sum(a * t1 ** i for i, a in enumerate(cps[c])) for c, x in comp.items() if x)
    k = cp_r / (cp_r - 1.0)
    t2 = t1 * (1 + (ratio ** ((k - 1) / k) - 1) / eta)
    src = (f"stage discharge {t2:.1f} K = T1 (1 + (r^((k-1)/k) - 1) / eta), T1 {t1:.2f} K, r {ratio:.4f}, eta {eta} "
           f"(D-016), ideal gas k {k:.3f} from cp/R of process/materials.yaml at T1 for the composition of {sid}; {D032}")
    return t2, src


def walk_tbd(node, path=""):
    if is_tbd(node):
        yield path
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk_tbd(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_tbd(v, f"{path}[{i}]")


FINAL_HEADER = ("# Datasheet drafted by `cheme datasheets draft`, sized by `cheme datasheets fill` and completed by\n"
                "# scripts/complete_datasheets.py (DESIGN.md D-032). Preliminary process datasheet: every value\n"
                "# says where it comes from; assumed: true marks an assumption; `supplier` names what a vendor,\n"
                "# licensor or study still has to give. Checked by the authoring agent, not yet by an engineer.\n")


def final():
    left = {}
    for path in sorted(DS.glob("*.yaml")):
        _, header, d = load(path.stem)
        tag = d["tag"]
        c = cfg(tag)
        ts = d.get("type_specific", {}) or {}
        for k, (kind, reason) in (c.get("markers") or {}).items():
            if k in ts and not is_tbd(ts[k]):
                continue
            unit = ts.get(k, {}).get("unit", "") if isinstance(ts.get(k), dict) else ""
            ts[k] = marker(kind, reason, unit)
        for k, reason in GENERIC.items():
            if k in ts and is_tbd(ts[k]):
                ts[k] = marker("supplier", reason, ts[k].get("unit", ""))
        open_ = list(walk_tbd(d))
        if open_:
            left[tag] = open_
            d["draft"] = True
            dump(path, header, d)
            continue
        d.pop("draft", None)
        dump(path, FINAL_HEADER, d)
    for tag, o in left.items():
        print(f"{tag}: still TBD: {', '.join(o)}")
    print(f"{len(left)} datasheet(s) left as drafts")


if __name__ == "__main__":
    {"inputs": inputs, "final": final}[sys.argv[1]]()
