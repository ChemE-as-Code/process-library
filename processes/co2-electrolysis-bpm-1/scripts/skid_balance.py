"""Stream values of the two pilot skids (#330) from core's stack and duty results.

Run: ``cheme run scripts/skid_balance.py`` (in the process folder; scripts/regen.py runs it
in step 9 and applies the values to process/flowsheet.yaml). With the environment variable
``BALANCE_OUTPUT`` set it writes the values the flowsheet cites as JSON, contract
``balance-output/1`` (library ADR 0027; scripts/check_balance_scripts.py of the library reruns
it and compares).

What it does (DESIGN.md D-007, D-011, D-012):

1. ``cheme process stack --json`` and ``cheme process duty D-A D-B --json`` at the committed
   horizon H (through scripts/_core.py). Train A (1xx) is the duty D-A at STK-A's
   arrangement, train B (2xx) D-B at STK-B's. Each case runs one train; the other is idle
   (zero flow).
2. Every stream value per hour from the duty totals over H: the charge, the CO and H2 formed
   (the cell's measured Faradaic efficiencies), the cation leaving and the carbon entering
   the anolyte through the membrane and the cation and carbon bled (core's totals by route,
   ADR 0044 amendment), the dosed solution, the make-up water, and the reservoir's initial
   fill and final inventory, each divided by H (KOH-FILL and SPENT are campaign-averaged,
   D-011). A duty that ends before its horizon (threshold, minimum inventory) is a result,
   not a stop: its rates are over the hours it ran, and the output says so (``notes``).
   The conditions that follow the inputs: the anolyte temperatures (the cell temperature, less
   the stack heat over the loop flow across the cooler), the compressor discharge and the
   product pressure (design basis).
3. The cation and the carbon balances of each duty close by route to 1e-9 relative (else the
   script stops): initial + dosed - bled - membrane = final for K, initial + membrane - bled -
   degassed = final for C. Every flowsheet step's mass and component balance then closes by
   construction (the water of the reservoir, the cathode and the oxidiser by balance).
4. The AC power: the stacks' DC power over the rectifier efficiency (cheme process stack),
   plus the recirculation pump, the compressor, the dosing pump (their datasheet shaft power
   once `cheme datasheets fill` gives it, until then the ESTIMATE below) and the PSA's own
   ESTIMATE.

The gas conditioning is a black box (D-012): the PSA recovers 0.90 of the CO formed at
0.99 mol/mol dry (H2 the rest), returns 0.95 of the unreacted CO2 to the cathode feed and
sends the rest with the water to the tail-gas oxidiser, which burns CO and H2 with twice the
stoichiometric air. The water the cathode consumes (hydrogen evolution) and leaves with comes
from the humidification water: the duty model holds the anolyte volume (no net water through
the membrane, ADR 0043), and so does this balance. Every such value is ASSUMED.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import yaml

import _core

ROOT = Path.cwd()
SCRIPT = "scripts/skid_balance.py"
CASES = {"skid-a": "A", "skid-b": "B"}
TRAINS = {
    "A": {"n": 1, "stack": "STK-A", "duty": "D-A"},
    "B": {"n": 2, "stack": "STK-B", "duty": "D-B"},
}

#: standard atomic weights, IUPAC 2021 abridged (the values core computes molar masses with)
ATOMIC = {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "K": 39.098}
FORMULA = {
    "CO2": {"C": 1, "O": 2}, "CO": {"C": 1, "O": 1}, "H2O": {"H": 2, "O": 1}, "H2": {"H": 2},
    "O2": {"O": 2}, "N2": {"N": 2}, "KOH": {"K": 1, "O": 1, "H": 1},
    "K2CO3": {"K": 2, "C": 1, "O": 3},
}  # fmt: skip
M = {c: sum(ATOMIC[e] * n for e, n in f.items()) for c, f in FORMULA.items()}  # g/mol
GAS_CONSTANT = 8.314462618  # J/(mol K)

# -- ASSUMED inputs of the balance (DESIGN.md D-011, D-012); every one is marked in the sources.
# The density of the 1 M KOH fill and the anolyte is the recirculation pump's of process/cells.yaml
# (read from cheme process stack), the cell temperature pilot-cell thermal.temperature, the
# product pressure and the PSA's pressure loss the design basis' (capacity.pilot_skid).
#: density of the make-up water, kg/L (25 degC)
RHO_WATER = 0.997
#: the cathode separator V-x21 and the gas it passes on: 25 degC and 110 kPa(a), saturated (its
#: own design condition, D-012, not the anolyte's temperature)
P_CATHODE_KPA = 110.0
T_CATHODE_K = 298.15
#: heat capacity of the anolyte (about 1 M KOH with its carbonate), kJ/(kg K): ASSUMED, a few %
#: below water's 4.18; it sets the cooler's temperature drop at the stack heat (D-012)
CP_ANOLYTE = 3.95
#: saturation pressure of water at 25 degC, kPa (IAPWS-95, Wagner and Pruss 2002)
P_SAT_25C_KPA = 3.1699
#: the K+ that crosses to the cathode leaves as K2CO3 in its condensate at this molality, mol/kg
CONDENSATE_MOLALITY = 1.0
#: the CO2 feed: 10 sccm/cm2 at the meter's 0 degC (ASSUMED, D-005) and 101.325 kPa
T_STD_K = 273.15
P_STD_PA = 101325.0
#: PSA: share of the CO formed delivered, product purity (mol/mol dry), CO2 recycle share:
#: read from process/design-basis.yaml capacity.pilot_skid
#: tail-gas oxidiser: air over the stoichiometric O2 (ASSUMED), air composition (mol)
AIR_RATIO = 2.0
AIR = {"N2": 0.79, "O2": 0.21}
#: the compressor K-x31 (ESTIMATE until its datasheet is filled): from 110 kPa(a) to the product
#: pressure plus the PSA's loss (design basis), adiabatic from 25 degC, kappa 1.3, efficiency
#: 0.5 (a small diaphragm machine)
KAPPA = 1.3
ETA_COMPRESSOR = 0.5
#: the pumps (ESTIMATE until their datasheets are filled): hydraulic power over efficiency
ETA_PUMP = 0.3
ETA_DOSING_PUMP = 0.1
DOSING_PUMP_DP_KPA = 300.0
#: the PSA's own power (valves, vacuum regeneration, controls): ESTIMATE, kWh per kg CO
#: delivered; TBD with the vendor
PSA_KWH_PER_KG = 0.5


class BalanceError(RuntimeError):
    pass


def _rel_close(a: float, b: float, rel: float) -> bool:
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-300)


#: pressures to kPa
KPA = {"bar(a)": 100.0, "bar": 100.0, "kPa(a)": 1.0, "kPa": 1.0, "MPa(a)": 1000.0}


def _kpa(q: dict, what: str) -> float:
    unit = q.get("unit")
    if unit not in KPA:
        raise BalanceError(f"{what}: pressure unit {unit} is not known to {SCRIPT}")
    return float(q["value"]) * KPA[unit]


def design_basis() -> dict:
    data = yaml.safe_load((ROOT / "process/design-basis.yaml").read_text(encoding="utf-8"))
    skid = data["capacity"]["pilot_skid"]
    cells = yaml.safe_load((ROOT / "process/cells.yaml").read_text(encoding="utf-8"))
    pilot = next(c for c in cells["cells"] if c["id"] == "pilot-cell")
    temperature = pilot["thermal"]["temperature"]
    if temperature.get("unit") not in ("°C", "degC", "K"):
        raise BalanceError(f"pilot-cell temperature unit {temperature.get('unit')} is not known")
    t_cell = float(temperature["value"]) + (0.0 if temperature["unit"] == "K" else 273.15)
    product_kpa = _kpa(skid["product"]["pressure"], "capacity.pilot_skid.product.pressure")
    return {
        "recovery": float(skid["product"]["recovery"]["value"]),
        "purity": float(skid["product"]["purity"]["value"]),
        "co2_feed_sccm_cm2": float(skid["co2_feed_per_area"]["value"]),
        "co2_recycle": float(skid["co2_recycle"]["value"]),
        "product_kpa": product_kpa,
        "discharge_kpa": product_kpa
        + _kpa(skid["psa_pressure_loss"], "capacity.pilot_skid.psa_pressure_loss"),
        "cell_temperature_k": t_cell,
    }


def datasheet_power(tag: str, keys=("shaft_power_kw", "power_kw")) -> float | None:
    """A datasheet's filled power, kW (None while it is TBD or there is no datasheet)."""
    path = ROOT / "equipment" / "datasheets" / f"{tag}.yaml"
    if not path.exists():
        return None
    sheet = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for key in keys:
        value = ((sheet.get("type_specific") or {}).get(key) or {}).get("value")
        if isinstance(value, (int, float)):
            return float(value)
    return None


def mass(mol_h: dict[str, float]) -> float:
    return sum(n * M[c] for c, n in mol_h.items()) / 1000.0


def stream(mol_h: dict[str, float], source: str) -> dict:
    """Flow (kg/h) and mass fractions of a stream given in mol/h per component."""
    kg = {c: n * M[c] / 1000.0 for c, n in mol_h.items() if n != 0.0}
    for c, n in mol_h.items():
        if n < -1e-12:
            raise BalanceError(f"negative amount of {c}: {n} mol/h ({source})")
    total = sum(kg.values())
    return {
        "mol_h": dict(mol_h),
        "flow": total,
        "composition": {c: v / total for c, v in kg.items()} if total > 0 else {},
        "source": source,
    }


def kg_stream(kg_h: dict[str, float], source: str) -> dict:
    return stream({c: v * 1000.0 / M[c] for c, v in kg_h.items()}, source)


def train(t: str, stack_rep: dict, duty_rep: dict, cell_pt: dict, basis: dict) -> dict:
    """The streams (mol/h, kg/h, fractions) and energy flows (kW) of train *t* when it runs."""
    info = TRAINS[t]
    n = info["n"]
    st = _core.stack(stack_rep, info["stack"])
    du = _core.duty(duty_rep, info["duty"])
    if du["refused"]:
        raise BalanceError(f"duty {info['duty']} is refused by core: {du['reasons']}")
    tot = _core.totals(du)
    # the rates per hour over the time the duty ran: H when it reaches its horizon, else its
    # operating time (an infeasible duty is a result, reported, not a stop: DESIGN.md D-023)
    h = float(du["operating_time_h"] or du["simulated_h"] or 0.0)
    if h <= 0:
        raise BalanceError(f"duty {info['duty']} ran no time: no balance")
    notes = []
    if du["ended"] != "horizon" or not du["feasible"]:
        notes.append(
            f"duty {info['duty']} ended by {du['ended']} after {h:g} h of the "
            f"{float(du['horizon_h']):g} h horizon (feasible {du['feasible']}): train {t}'s "
            f"rates are over its {h:g} h of operation, not a campaign of H"
        )
    cells = int(du["cells_in_series"]) * int(du["stacks"])
    if cells != int(_core.stack_value(st, "cells_total")):
        raise BalanceError(
            f"duty {info['duty']} runs {cells} cells, stack {info['stack']} has another"
        )
    src = f"{SCRIPT}: duty {info['duty']} at {du['cells_in_series']} x {du['stacks']} over {h:g} h"
    rho_anolyte = _core.equipment_number(st, f"P-{n}01", "density_kg_m3") / 1000.0  # kg/L

    # the route balances (core ADR 0044 amendment): K and C close on their own
    k_in = tot["initial_cation_mol"] + tot["dosing_cation_mol"]
    k_out = tot["bleed_cation_mol"] + tot["membrane_cation_mol"] + tot["final_cation_mol"]
    c_in = tot["initial_carbon_mol"] + tot["membrane_carbon_mol"]
    c_out = tot["bleed_carbon_mol"] + tot["co2_degassed_mol"] + tot["final_carbon_mol"]
    if not (_rel_close(k_in, k_out, 1e-9) and _rel_close(c_in, c_out, 1e-9)):
        raise BalanceError(f"duty {info['duty']}: K {k_in} != {k_out} or C {c_in} != {c_out}")

    e_mol_h = tot["charge_c"] / h / _core.FARADAY  # electrons per hour, all cells
    wde = cell_pt["wde"]
    k_m = tot["membrane_cation_mol"] / h  # K+ to the cathode
    c_m = tot["membrane_carbon_mol"] / h  # carbon to the anolyte
    # the co-ion current (1 - WDE) Q / F; its split is the duty's: a measured cell's duty takes
    # the titration's carbon share (0.66978 at P200), the cell report the membrane block's
    # rounded 0.670 (DESIGN.md D-011)
    if not _rel_close(k_m + c_m, (1 - wde) * e_mol_h, 1e-6):
        raise BalanceError(
            f"co-ion current: duty {k_m + c_m} mol/h, (1 - WDE) Q / F gives {(1 - wde) * e_mol_h}"
        )
    if not _rel_close(tot["hydroxide_deficit_mol"] / h, (1 - wde) * e_mol_h, 1e-6):
        raise BalanceError("the duty's hydroxide deficit is not (1 - WDE) Q / F")
    co = tot["product_mol"] / h
    fe_h2 = cell_pt["fe"]["H2"]
    h2 = fe_h2 * e_mol_h / 2.0
    o2 = 0.5 * (co + h2)  # the overall reactions CO2R and WS (as cheme process cell)
    if not _rel_close(co, cell_pt["fe"]["CO"] * e_mol_h / 2.0, 1e-6):
        raise BalanceError("the duty's CO is not the cell's at its Faradaic efficiency")

    # cathode: the CO2 fed, reacted, crossed and recycled
    area_cm2 = float(st["point"]["area_m2"]) * 1e4 * cells
    feed = basis["co2_feed_sccm_cm2"] * area_cm2 * 1e-6 / 60.0 * P_STD_PA / (GAS_CONSTANT * T_STD_K)
    feed *= 3600.0  # mol/h
    carb_cathode = k_m / 2.0  # 2 KOH (the K+ crossed) + CO2 -> K2CO3 + H2O at the cathode
    unreacted = feed - co - c_m - carb_cathode
    recycle = basis["co2_recycle"] * unreacted
    fresh = feed - recycle
    y_w = P_SAT_25C_KPA / P_CATHODE_KPA
    gas_dry = co + h2 + unreacted
    water_gas = gas_dry * y_w / (1.0 - y_w)
    cond_k2co3 = carb_cathode
    cond_water = cond_k2co3 / CONDENSATE_MOLALITY * 1000.0 / M["H2O"]  # mol/h
    humid = water_gas + cond_water + h2 - carb_cathode  # WS consumes H2 mol of water

    # gas conditioning: PSA and oxidiser
    co_del = basis["recovery"] * co
    h2_prod = co_del * (1.0 - basis["purity"]) / basis["purity"]
    tail = {"CO": co - co_del, "H2": h2 - h2_prod, "CO2": unreacted - recycle, "H2O": water_gas}
    o2_stoich = 0.5 * (tail["CO"] + tail["H2"])
    o2_air = AIR_RATIO * o2_stoich
    air = {"O2": o2_air, "N2": o2_air * AIR["N2"] / AIR["O2"]}
    flue = {
        "N2": air["N2"],
        "O2": o2_air - o2_stoich,
        "CO2": tail["CO2"] + tail["CO"],
        "H2O": tail["H2O"] + tail["H2"],
    }

    # anolyte: the reservoir's fill and inventory, campaign-averaged; the loop at its mean state
    def solution(cation_mol: float, carbon_mol: float, volume_l: float, rho: float) -> dict:
        koh = cation_mol - 2.0 * carbon_mol
        k2co3 = carbon_mol
        water_kg = volume_l * rho - (koh * M["KOH"] + k2co3 * M["K2CO3"]) / 1000.0
        return {"KOH": koh, "K2CO3": k2co3, "H2O": water_kg * 1000.0 / M["H2O"]}

    fill = {
        k: v / h
        for k, v in solution(
            tot["initial_cation_mol"],
            tot["initial_carbon_mol"],
            tot["initial_volume_l"],
            rho_anolyte,
        ).items()
    }
    dose_mol = tot["dosing_mol"] / h
    dose_kg = (tot["dosing_solution_kg"] or 0.0) / h
    dose = {"KOH": dose_mol, "H2O": (dose_kg - dose_mol * M["KOH"] / 1000.0) * 1000.0 / M["H2O"]}
    makeup = {"H2O": tot["makeup_water_l"] / h * RHO_WATER * 1000.0 / M["H2O"]}
    # what leaves the reservoir as liquid (spent inventory and bleed), by K, C and the water
    water_out = fill["H2O"] + dose["H2O"] + makeup["H2O"] + c_m  # + the carbonation water
    out_k = {"spent": tot["final_cation_mol"] / h, "bleed": tot["bleed_cation_mol"] / h}
    out_c = {"spent": tot["final_carbon_mol"] / h, "bleed": tot["bleed_carbon_mol"] / h}
    vol = {"spent": tot["final_volume_l"], "bleed": tot["bleed_l"]}
    liquid = {}
    for key in ("spent", "bleed"):
        share = vol[key] / (vol["spent"] + vol["bleed"])
        liquid[key] = {
            "KOH": out_k[key] - 2.0 * out_c[key],
            "K2CO3": out_c[key],
            "H2O": water_out * share,
        }
    # the recirculation loop at the campaign's mean state (Skid A: the mean of the initial and
    # final state, exact at constant fluxes and volume; Skid B: the steady state at H)
    if t == "A":
        mean_k = (
            0.5 * (tot["initial_cation_mol"] + tot["final_cation_mol"]) / tot["initial_volume_l"]
        )
        mean_c = (
            0.5 * (tot["initial_carbon_mol"] + tot["final_carbon_mol"]) / tot["initial_volume_l"]
        )
        state_note = "mean of the initial and final reservoir state"
    else:
        mean_k = tot["final_cation_mol"] / tot["final_volume_l"]
        mean_c = tot["final_carbon_mol"] / tot["final_volume_l"]
        state_note = "the steady state at H"
    loop_flow = _core.equipment_number(st, f"P-{n}01", "mass_flow_kg_h")
    per_l = solution(mean_k, mean_c, 1.0, rho_anolyte)
    scale = loop_flow / mass(per_l)
    loop = {c: v * scale for c, v in per_l.items()}
    ret = {
        "KOH": loop["KOH"] - 2.0 * c_m - k_m,
        "K2CO3": loop["K2CO3"] + c_m,
        "H2O": loop["H2O"] + c_m,
        "O2": o2,
    }

    s: dict[str, dict] = {}
    p = f"S{n}"
    s[f"{p}01"] = stream(
        {"CO2": fresh},
        f"{src}: CO2 fed {feed:.6g} mol/h ({basis['co2_feed_sccm_cm2']:g} sccm/cm2) less the recycle",
    )
    s[f"{p}02"] = stream(
        {"H2O": humid},
        f"{src}: water to the humidifier, ASSUMED to cover the cathode's (hydrogen evolution, saturation, condensate)",
    )
    s[f"{p}03"] = stream(
        {"CO2": recycle}, f"{src}: {basis['co2_recycle']:g} of the unreacted CO2 (ASSUMED, D-012)"
    )
    s[f"{p}04"] = stream(
        {"CO2": unreacted, "CO": co, "H2": h2, "H2O": water_gas + cond_water, "K2CO3": cond_k2co3},
        f"{src}: CO and H2 at the measured FE, CO2 less the CO, the carbon to the anolyte and the K+ carbonated",
    )
    s[f"{p}05"] = stream(
        {"K2CO3": cond_k2co3, "H2O": cond_water},
        f"{src}: the K+ crossed as K2CO3 at {CONDENSATE_MOLALITY:g} mol/kg (ASSUMED)",
    )
    s[f"{p}06"] = stream(
        {"CO2": unreacted, "CO": co, "H2": h2, "H2O": water_gas},
        f"{src}: saturated at 25 degC, {P_CATHODE_KPA:g} kPa(a) (ASSUMED)",
    )
    s[f"{p}07"] = dict(s[f"{p}06"], source=f"{src}: as the separator gas")
    s[f"{p}08"] = stream(
        {"CO": co_del, "H2": h2_prod},
        f"{src}: recovery {basis['recovery']:g} of the CO formed at {basis['purity']:g} mol/mol dry (ASSUMED, D-008)",
    )
    # the conditions that follow the design basis (D-012): the compressor discharge is the
    # product pressure plus the PSA's loss
    s[f"{p}07"]["conditions"] = {
        "pressure": (
            basis["discharge_kpa"],
            f"{SCRIPT}: the product pressure {basis['product_kpa']:g} kPa(a) plus the PSA loss "
            f"{basis['discharge_kpa'] - basis['product_kpa']:g} kPa (process/design-basis.yaml "
            "capacity.pilot_skid, ASSUMED, D-012)",
        )
    }
    s[f"{p}08"]["conditions"] = {
        "pressure": (
            basis["product_kpa"],
            f"{SCRIPT}: the product pressure of process/design-basis.yaml capacity.pilot_skid "
            "(ASSUMED, D-008)",
        )
    }
    s[f"{p}09"] = stream(tail, f"{src}: the PSA's rest")
    s[f"{p}10"] = stream(
        air, f"{src}: {AIR_RATIO:g} x the stoichiometric O2 of the tail gas (ASSUMED)"
    )
    s[f"{p}11"] = stream(flue, f"{src}: CO and H2 burnt (COX, HOX)")
    s[f"{p}12"] = stream(
        loop, f"{src}: {loop_flow:g} kg/h (cheme process stack), at the {state_note}"
    )
    s[f"{p}13"] = dict(s[f"{p}12"], source=s[f"{p}12"]["source"])
    s[f"{p}14"] = dict(s[f"{p}12"], source=s[f"{p}12"]["source"])
    s[f"{p}15"] = stream(
        ret,
        f"{src}: the loop with the membrane's K+ out, carbon in (core totals by route) and the anode O2",
    )
    # the anolyte temperatures: the stacks return it at the cell temperature, and the cooler
    # E-x11 takes the stack heat out of the loop flow ahead of them (D-012)
    heat_kw = _core.stack_value(st, "heat_duty_kw")
    t_cell = basis["cell_temperature_k"]
    drop = heat_kw / (loop_flow / 3600.0 * CP_ANOLYTE)
    t_src = (
        f"{SCRIPT}: the pilot-cell temperature (process/cells.yaml, ASSUMED); the stacks return the "
        "anolyte at it"
    )
    s[f"{p}13"]["conditions"] = {"temperature": (t_cell, t_src)}
    s[f"{p}15"]["conditions"] = {"temperature": (t_cell, t_src)}
    s[f"{p}14"]["conditions"] = {
        "temperature": (
            t_cell - drop,
            f"{SCRIPT}: the cell temperature less the stack heat {heat_kw:.4g} kW over "
            f"{loop_flow:g} kg/h at cp {CP_ANOLYTE:g} kJ/(kg K) (ASSUMED): {drop:.3f} K across "
            f"the cooler E-{n}11",
        )
    }
    s[f"{p}16"] = stream({"O2": o2}, f"{src}: the anode O2 (overall reactions), dry (ASSUMED)")
    s[f"{p}17"] = stream(
        fill,
        f"{src}: the initial fill {tot['initial_volume_l']:.6g} L of 1 M KOH over H (campaign-averaged, D-011)",
    )
    s[f"{p}18"] = stream(
        liquid["spent"], f"{src}: the final inventory over H (campaign-averaged, D-011)"
    )
    if t == "B":
        s["S219"] = stream(dose, f"{src}: the KOH dosed, {tot['dosing_solution_l'] / h:.6g} L/h")
        s["S220"] = dict(s["S219"])
        s["S221"] = dict(s["S219"])
        s["S222"] = stream(
            makeup, f"{src}: {tot['makeup_water_l'] / h:.6g} L/h at {RHO_WATER:g} kg/L (ASSUMED)"
        )
        s["S223"] = stream(
            liquid["bleed"],
            f"{src}: {tot['bleed_l'] / h:.6g} L/h at the reservoir's composition (core totals by route)",
        )

    # energy, kW
    dc = tot["energy_kwh"] / h
    if not _rel_close(dc, _core.stack_value(st, "dc_power_kw"), 1e-6):
        raise BalanceError("the duty's power is not the stack's DC power")
    ac = _core.stack_value(st, "ac_power_kw")
    pump_dp = _core.equipment_number(
        st, f"P-{n}01", "discharge_pressure_kpa"
    ) - _core.equipment_number(st, f"P-{n}01", "suction_pressure_kpa")
    rho_pump = _core.equipment_number(st, f"P-{n}01", "density_kg_m3")
    pump = datasheet_power(f"P-{n}01")
    pump_src = f"equipment/datasheets/P-{n}01.yaml"
    if pump is None:
        pump = loop_flow / rho_pump / 3600.0 * pump_dp / ETA_PUMP
        pump_src = (
            f"ESTIMATE {loop_flow:g} kg/h x {pump_dp:g} kPa / {ETA_PUMP:g} until the datasheet fill"
        )
    gas_mol_s = sum(s[f"{p}06"]["mol_h"].values()) / 3600.0
    comp = datasheet_power(f"K-{n}31")
    comp_src = f"equipment/datasheets/K-{n}31.yaml"
    if comp is None:
        ratio = basis["discharge_kpa"] / P_CATHODE_KPA
        comp = (
            gas_mol_s * GAS_CONSTANT * T_CATHODE_K * KAPPA / (KAPPA - 1.0)
            * (ratio ** ((KAPPA - 1.0) / KAPPA) - 1.0) / ETA_COMPRESSOR / 1000.0
        )  # fmt: skip
        comp_src = (
            f"ESTIMATE adiabatic {P_CATHODE_KPA:g} to {basis['discharge_kpa']:g} kPa(a), kappa {KAPPA:g}, "
            f"efficiency {ETA_COMPRESSOR:g} until the datasheet fill"
        )
    psa = PSA_KWH_PER_KG * mass({"CO": co_del})
    q = {
        f"Q{n}01": (
            ac,
            f"{src}: cheme process stack {info['stack']} AC power (DC {dc:.6g} kW over the rectifier efficiency, ASSUMED)",
        ),
        f"Q{n}02": (pump, f"{SCRIPT}: P-{n}01 {pump_src}"),
        f"Q{n}03": (comp, f"{SCRIPT}: K-{n}31 {comp_src}"),
        f"Q{n}04": (
            psa,
            f"{SCRIPT}: X-{n}31 ESTIMATE {PSA_KWH_PER_KG:g} kWh/kg CO delivered, TBD vendor",
        ),
        f"Q{n}05": (
            heat_kw,
            f"{src}: the stacks' heat (cheme process stack), removed by E-{n}11 (isothermal by assumption)",
        ),
    }
    if t == "B":
        dosing = datasheet_power("P-202")
        dsrc = "equipment/datasheets/P-202.yaml"
        if dosing is None:
            dosing = (
                tot["dosing_solution_l"]
                / h
                / 1000.0
                / 3600.0
                * DOSING_PUMP_DP_KPA
                / ETA_DOSING_PUMP
            )
            dsrc = f"ESTIMATE {DOSING_PUMP_DP_KPA:g} kPa / {ETA_DOSING_PUMP:g} until the datasheet fill"
        q["Q206"] = (dosing, f"{SCRIPT}: P-202 {dsrc}")
    return {
        "streams": s,
        "energy": {k: {"duty": v, "source": src_} for k, (v, src_) in q.items()},
        "horizon_h": h,
        "check": {"k": (k_in, k_out), "c": (c_in, c_out)},
        "notes": notes,
    }


def idle(active: dict) -> dict:
    """The same streams with zero flow (the train is idle in the other train's case)."""
    return {
        "streams": {
            k: dict(v, flow=0.0, source=f"{SCRIPT}: the train is idle in this case (D-007)")
            for k, v in active["streams"].items()
        },
        "energy": {
            k: {"duty": 0.0, "source": f"{SCRIPT}: the train is idle in this case (D-007)"}
            for k in active["energy"]
        },
    }


def compute() -> dict:
    basis = design_basis()
    cell_pt = _core.cell_point(_core.cell_report(ROOT), "pilot-cell")
    if cell_pt["refused"]:
        raise BalanceError(f"pilot-cell refused: {cell_pt['reasons']}")
    stack_rep = _core.stack_report(ROOT)
    duty_rep = _core.duty_report(ROOT, ["D-A", "D-B"])
    trains = {t: train(t, stack_rep, duty_rep, cell_pt, basis) for t in TRAINS}
    cases: dict[str, dict] = {}
    sources: dict[str, dict] = {}
    conditions: dict[str, dict] = {}
    for case, running in CASES.items():
        values: dict[str, dict] = {}
        for t, result in trains.items():
            use = result if t == running else idle(result)
            for sid, v in use["streams"].items():
                values[sid] = {"flow": v["flow"], "composition": v["composition"]}
                sources.setdefault(case, {})[sid] = v["source"]
                # the design conditions hold in both cases (an idle train keeps them)
                for quantity, (value, src) in (result["streams"][sid].get("conditions") or {}).items():
                    values[sid][quantity] = value
                    conditions.setdefault(case, {}).setdefault(sid, {})[quantity] = src
            for qid, v in use["energy"].items():
                values[qid] = {"duty": v["duty"]}
                sources.setdefault(case, {})[qid] = v["source"]
        cases[case] = values
    notes = [n for r in trains.values() for n in r["notes"]]
    return {
        "cases": cases,
        "sources": sources,
        "condition_sources": conditions,
        "notes": notes,
        "trains": trains,
    }


def main() -> int:
    try:
        result = compute()
    except (BalanceError, _core.CoreError) as exc:
        print(f"skid_balance: {exc}", file=sys.stderr)
        return 1
    target = os.environ.get("BALANCE_OUTPUT")
    doc = {
        "contract": "balance-output/1",
        "script": SCRIPT,
        "cases": result["cases"],
        "sources": result["sources"],
        "condition_sources": result["condition_sources"],
        "notes": result["notes"],
    }
    for note in result["notes"]:
        print(f"skid_balance: {note}", file=sys.stderr)
    if target:
        Path(target).write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
    for t, r in result["trains"].items():
        s = r["streams"]
        n = TRAINS[t]["n"]
        print(
            f"train {t} over {r['horizon_h']:g} h: CO product {s[f'S{n}08']['flow']:.6g} kg/h, "
            f"CO2 fresh {s[f'S{n}01']['flow']:.6g} kg/h, KOH fill {s[f'S{n}17']['flow']:.6g} kg/h, "
            f"spent {s[f'S{n}18']['flow']:.6g} kg/h, AC {r['energy'][f'Q{n}01']['duty']:.6g} kW"
        )
    if not math.isfinite(
        sum(v.get("flow", 0.0) for c in result["cases"].values() for v in c.values())
    ):
        print("skid_balance: a value is not finite", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
