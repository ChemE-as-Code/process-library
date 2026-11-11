"""Closed-form hand expectations of the LCI of the CO2 pilot skids (process-library#331, E10).

The frozen values of ``processes/co2-electrolysis-bpm-1/results/expected-lca.yaml``: the life
cycle inventory of Skid A and Skid B per kg of CO delivered (contained in the product at the
skid boundary), at the 1,000 h and 10,000 h campaigns, as plain formulas. Like
``tests/skid_formulas.py`` (whose measured point and closed forms it reuses, unchanged), this
module imports neither cheme-as-code (core) nor the process's scripts: it is the independent
check the regenerated LCA (``lca/dataset.yaml``, the skid-b case dataset and
``results/scenarios/<H>h/lca.json``) is compared with.

What it restates (DESIGN.md D-008 to D-012 of the process; every input ASSUMED unless the
measured series gives it):

- the functional unit: 1 kg of CO contained in the product gas at 0.99 mol/mol dry (the rest
  H2), so a kg of product per kg of CO is ``1 / w_CO``;
- the electricity: the stacks' AC power (DC over the rectifier efficiency) and the auxiliaries
  that ``scripts/skid_balance.py`` estimates until the datasheets give them (the recirculation
  pump, the cathode gas compressor, the PSA's own power and Skid B's dosing pump);
- the cathode gas: 10 sccm/cm2 of CO2 at 0 degC, the CO, H2 and co-ion carbon the cells take
  out, 0.95 of the unreacted CO2 recycled, the rest vented as CO2 by the oxidiser with the
  CO the PSA does not recover;
- the potassium and the carbon by route: the fill, the dose, the K+ that crosses to the
  cathode (condensate), the carbon that crosses to the anolyte, the bleed and the inventory
  left at the end of the campaign;
- the H2 that a separation could recover as a co-product (the tail gas's), and its mass and
  lower-heating-value shares against the CO;
- the replaced stack parts per kg CO at a membrane life of 1,000, 4,000 and 20,000 h.

The co-ion split is the measured titration share at P200 (0.66978), the one the duties run
with (results/expected-errata.yaml X-1), not the cell block's rounded 0.670.
"""

from __future__ import annotations

import math
from pathlib import Path

import skid_formulas as sf
import yaml

EXPECTED = sf.PROCESS / "results" / "expected-lca.yaml"

#: IUPAC 2021 abridged atomic weights, as skid_formulas and core (kg/kmol)
ATOMIC_MASS = {**sf.ATOMIC_MASS, "N": 14.007}
M = {
    "CO": sf.M_CO,
    "CO2": ATOMIC_MASS["C"] + 2 * ATOMIC_MASS["O"],
    "H2": 2 * ATOMIC_MASS["H"],
    "H2O": 2 * ATOMIC_MASS["H"] + ATOMIC_MASS["O"],
    "KOH": sf.M_KOH,
    "K": ATOMIC_MASS["K"],
}
#: lower heating values, kJ/mol, CODATA Key Values (Cox, Wagman, Medvedev 1989): CO + 1/2 O2 ->
#: CO2 282.98 (process/reactions.yaml COX); H2 + 1/2 O2 -> H2O(g) 241.826 (dfH(H2O, g))
LHV_KJ_MOL = {"CO": 282.98, "H2": 241.826}

#: the inputs of the LCI hand values (process/design-basis.yaml, process/cells.yaml and the
#: ASSUMED constants of scripts/skid_balance.py; DESIGN.md D-008, D-012, D-024)
LCA_DESIGN = {
    "purity_mol": 0.99,
    "co2_feed_sccm_cm2": 10.0,
    "t_std_k": 273.15,
    "p_std_pa": 101325.0,
    "co2_recycle": 0.95,
    "p_sat_25c_kpa": 3.1699,
    "p_cathode_kpa": 110.0,
    "t_cathode_k": 298.15,
    "condensate_molality": 1.0,
    "product_kpa": 500.0,
    "psa_loss_kpa": 100.0,
    "kappa": 1.3,
    "eta_compressor": 0.5,
    "pump_dp_kpa": 50.0,
    "eta_pump": 0.3,
    "psa_kwh_per_kg": 0.5,
    "dosing_dp_kpa": 300.0,
    "eta_dosing_pump": 0.1,
    "dose_density_kg_l": 1.22,
    # the replaced parts (DESIGN.md D-026, all ASSUMED): 28 cells of 100 cm2, the membrane, the
    # Ag of the cathode (100 nm sputtered, design basis capacity.reference_cell, at the bulk
    # density 10.49 g/cm3) and the Ni foam anode, at the stacks' replacement interval
    "replacement_interval_h": 4000.0,
    "membrane_life_h": [1000.0, 4000.0, 20000.0],
    "membrane_kg_m2": 0.20,
    "ag_thickness_nm": 100.0,
    "ag_density_g_cm3": 10.49,
    "ni_foam_kg_m2": 0.35,
    # the Ember 2025 life-cycle intensity of NL generation (core's packaged profile ember-2025,
    # line 66835 of Ember's yearly CSV, CC BY 4.0), kg CO2e/kWh
    "ember_nl_kg_kwh": 0.253664,
}


def _cathode(total_a: float, cells: int, cell_area_cm2: float, fe: dict, wde: float, cx: float, d: dict) -> dict:
    """mol/h of the cathode gas train (skid_balance's black box, restated)."""
    e = total_a / sf.FARADAY * sf.SECONDS_PER_HOUR  # electrons per hour
    co = fe["CO"] * e / 2.0
    h2 = fe["H2"] * e / 2.0
    k_m = (1.0 - cx) * (1.0 - wde) * e  # K+ to the cathode
    c_m = cx * (1.0 - wde) * e  # carbon to the anolyte
    feed = d["co2_feed_sccm_cm2"] * cells * cell_area_cm2 * 1e-6 / 60.0 * d["p_std_pa"] / (sf.GAS_CONSTANT * d["t_std_k"]) * 3600.0
    carb_cathode = k_m / 2.0
    unreacted = feed - co - c_m - carb_cathode
    recycle = d["co2_recycle"] * unreacted
    y_w = d["p_sat_25c_kpa"] / d["p_cathode_kpa"]
    gas_dry = co + h2 + unreacted
    water_gas = gas_dry * y_w / (1.0 - y_w)
    return {
        "electrons_mol_h": e, "co": co, "h2": h2, "k_m": k_m, "c_m": c_m, "feed": feed,
        "unreacted": unreacted, "recycle": recycle, "fresh": feed - recycle,
        "carb_cathode": carb_cathode, "gas_mol_h": gas_dry + water_gas,
    }  # fmt: skip


def lci_values(design: dict = sf.DESIGN, lca: dict = LCA_DESIGN) -> dict:
    """Every frozen hand value of results/expected-lca.yaml, from the measured point P200,
    the #330 design inputs and *lca*."""
    d, x = design, lca
    p200 = sf.measured_point("P200")
    u, wde = p200["voltage_v"][0], p200["wde"][0]
    fe = {n: s[0] for n, s in p200["fe"].items()}
    cx = p200["co_ion_carbon_fraction"][0]
    i = d["cell_current_a"]
    arr = sf.arrangement(d["co_delivered_kg_h"], d["recovery"], d["cell_area_cm2"], i, u, fe["CO"], d["max_stack_voltage_v"])
    cells, total_a = arr["cells"], arr["total_current_a"]
    delivered = arr["co_delivered_kg_h"]
    g = _cathode(total_a, cells, d["cell_area_cm2"], fe, wde, cx, x)
    co_del_mol = d["recovery"] * g["co"]
    h2_prod_mol = co_del_mol * (1.0 - x["purity_mol"]) / x["purity_mol"]

    # the functional unit: kg of product gas per kg of CO contained
    w_co = co_del_mol * M["CO"] / (co_del_mol * M["CO"] + h2_prod_mol * M["H2"])
    out: dict = {"functional_unit": {"kg_product_per_kg_co": 1.0 / w_co, "co_delivered_kg_h": delivered}}

    # electricity, kW (the auxiliaries as skid_balance estimates them) and per kg CO
    stacks_ac = arr["dc_power_kw"] / d["rectifier_efficiency"]
    loop_kg_h = d["flow_per_area_ml_min_cm2"] * cells * d["cell_area_cm2"] * 60 / 1e6 * d["anolyte_density_kg_m3"]
    pump = loop_kg_h / d["anolyte_density_kg_m3"] / 3600.0 * x["pump_dp_kpa"] / x["eta_pump"]
    ratio = (x["product_kpa"] + x["psa_loss_kpa"]) / x["p_cathode_kpa"]
    k = x["kappa"]
    compressor = (
        g["gas_mol_h"] / 3600.0 * sf.GAS_CONSTANT * x["t_cathode_k"] * k / (k - 1.0)
        * (ratio ** ((k - 1.0) / k) - 1.0) / x["eta_compressor"] / 1000.0
    )  # fmt: skip
    psa = x["psa_kwh_per_kg"] * delivered
    b = sf.skid_b_steady(total_a, wde, cx, d["skid_b_hydroxide_mol_l"], d["skid_b_carbon_mol_l"], d["dose_concentration_mol_l"], d["skid_b_volume_l"])
    dosing = b["dose_solution_l_h"] / 1000.0 / 3600.0 * x["dosing_dp_kpa"] / x["eta_dosing_pump"]
    kw = {"A": stacks_ac + pump + compressor + psa, "B": stacks_ac + pump + compressor + psa + dosing}
    out["electricity"] = {
        "stacks_ac_kwh_per_kg": stacks_ac / delivered,
        "pump_kw": pump, "compressor_kw": compressor, "psa_kw": psa, "dosing_pump_kw": dosing,
        "skid_a_kwh_per_kg": kw["A"] / delivered,
        "skid_b_kwh_per_kg": kw["B"] / delivered,
        "skid_a_kg_co2e_per_kg_nl": kw["A"] / delivered * x["ember_nl_kg_kwh"],
    }  # fmt: skip

    # CO2: fresh, in the product, to the anolyte and the condensate, vented (both skids alike)
    vented_mol = (g["unreacted"] - g["recycle"]) + (g["co"] - co_del_mol)
    per = M["CO2"] * 1e-3 / delivered  # kg CO2 per kg CO for one mol/h
    out["co2"] = {
        "fresh_kg_per_kg": g["fresh"] * per,
        "vented_kg_per_kg": vented_mol * per,
        "carbon_share": {
            "product": co_del_mol / g["fresh"],
            "anolyte": g["c_m"] / g["fresh"],
            "condensate": g["carb_cathode"] / g["fresh"],
            "vented": vented_mol / g["fresh"],
        },
    }

    # potassium and carbon by route, mol per kg CO, per skid and campaign
    routes: dict = {}
    for h in d["durations_h"]:
        exact = sf.volume_to_horizon_l(h, total_a, wde, cx, d["koh_fill_mol_l"], d["threshold_ph"])
        v_a = sf.round_up_sig(exact * (1 + 1e-6))
        co_kg = delivered * h
        cond_k = g["k_m"] * h
        carbon_in = g["c_m"] * h
        fill_a = v_a * d["koh_fill_mol_l"]
        fill_b = d["skid_b_volume_l"] * d["koh_fill_mol_l"]
        dose_b = b["dose_mol_h"] * h
        spent_b_k = d["skid_b_volume_l"] * b["cation_mol_l"]
        spent_b_c = d["skid_b_volume_l"] * d["skid_b_carbon_mol_l"]
        routes[int(h)] = {
            "A": {
                "fill_k": fill_a / co_kg, "dose_k": 0.0, "condensate_k": cond_k / co_kg, "bleed_k": 0.0,
                "spent_k": (fill_a - cond_k) / co_kg, "spent_c": carbon_in / co_kg, "bleed_c": 0.0,
                "koh_fill_kg_per_kg": fill_a * M["KOH"] * 1e-3 / co_kg, "koh_dose_kg_per_kg": 0.0,
            },
            "B": {
                "fill_k": fill_b / co_kg, "dose_k": dose_b / co_kg, "condensate_k": cond_k / co_kg,
                "bleed_k": (fill_b + dose_b - cond_k - spent_b_k) / co_kg, "spent_k": spent_b_k / co_kg,
                "spent_c": spent_b_c / co_kg, "bleed_c": (carbon_in - spent_b_c) / co_kg,
                "koh_fill_kg_per_kg": fill_b * M["KOH"] * 1e-3 / co_kg,
                "koh_dose_kg_per_kg": dose_b * M["KOH"] * 1e-3 / co_kg,
            },
        }  # fmt: skip
    out["routes"] = routes

    # H2: what a separation could recover (the tail gas's), its mass and LHV shares
    h2_kg = (g["h2"] - h2_prod_mol) * M["H2"] * 1e-3 / delivered
    lhv = {c: LHV_KJ_MOL[c] / M[c] for c in LHV_KJ_MOL}  # MJ/kg
    out["h2_coproduct"] = {
        "h2_kg_per_kg_co": h2_kg,
        "lhv_mj_kg": lhv,
        "share_mass": h2_kg / (1.0 + h2_kg),
        "share_lhv": h2_kg * lhv["H2"] / (h2_kg * lhv["H2"] + lhv["CO"]),
    }

    # the replaced stack parts per kg CO, at each membrane life
    area = cells * d["cell_area_cm2"] * 1e-4  # m2 per replacement
    ag_kg_m2 = x["ag_thickness_nm"] * 1e-9 * x["ag_density_g_cm3"] * 1e3
    parts: dict = {"area_m2": area, "ag_kg_m2": ag_kg_m2}
    for life in x["membrane_life_h"]:
        m2 = area / (life * delivered)
        parts[int(life)] = {
            "membrane_m2_per_kg": m2,
            "membrane_g_per_kg": m2 * x["membrane_kg_m2"] * 1e3,
            "ag_g_per_kg": m2 * ag_kg_m2 * 1e3,
            "ni_g_per_kg": m2 * x["ni_foam_kg_m2"] * 1e3,
        }
    out["parts"] = parts
    return out


def lookup(values: dict, key: str):
    """The value at a dotted *key* of :func:`lci_values` (integer parts are durations or lives)."""
    node = values
    for part in key.split("."):
        node = node[int(part)] if part.isdigit() else node[part]
    return node


def load_expected(path: Path = EXPECTED) -> dict:
    return yaml.safe_load(path.read_text())


def close(value: float, want: float, tol: dict) -> bool:
    if "rel" in tol:
        return math.isclose(value, want, rel_tol=tol["rel"], abs_tol=tol.get("abs", 0.0))
    return abs(value - want) <= tol["abs"]
