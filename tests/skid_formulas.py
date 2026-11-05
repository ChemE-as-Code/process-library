"""Closed-form hand expectations of the CO2 electrolysis pilot skids (process-library#330).

The frozen expectations of ``processes/co2-electrolysis-bpm-1/results/expected.yaml`` (spec
section 7, E1 to E7) as plain formulas. This module imports neither cheme-as-code (core) nor the
process's ``scripts/regen.py``: it is the independent check the regenerated skid results are
compared with. It reads the measured point P200 directly from
``experiments/electrochemistry/rbpm-1m-koh.yaml`` (cell voltage, Faradaic efficiencies, water
dissociation efficiency and co-ion carbon share per replicate, then their means), with the
equations the measurement file documents (Prats Vergel et al., Nat. Chem. Eng. 2025, Methods and
SI Note 5; DESIGN.md D-002, D-005), written out here on their own.

The anolyte closed form is the one of core ADR 0043 for the ``well-mixed-carbonate`` model
without dosing, bleed, make-up or degassing at one operating point: the cation leaves at
``(1 - Cx)(1 - WDE) I / F`` and the carbon enters at ``Cx (1 - WDE) I / F``, the volume stays
constant, and the concentration-basis pH reaches the threshold when the charge balance
``[K+] + [H+] = [OH-] + C_T g(h)`` holds at ``h = 10**-pH``, with ``g`` the charge per mol of
carbon (``HCO3-`` + 2 ``CO3-2``). So

    t = V (c0 - [OH-] + [H+]) F / (N I (1 - WDE) ((1 - Cx) + Cx g)),

which reproduces core's 322.30 h at 1 L, 1 A, WDE 0.95, Cx 0.66 (tests/test_skid_formulas.py).
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml

LIBRARY = Path(__file__).resolve().parents[1]
PROCESS = LIBRARY / "processes" / "co2-electrolysis-bpm-1"
MEASUREMENTS = PROCESS / "experiments" / "electrochemistry" / "rbpm-1m-koh.yaml"
CELLS = PROCESS / "process" / "cells.yaml"
EXPECTED = PROCESS / "results" / "expected.yaml"

#: C/mol, CODATA 2018 (exact)
FARADAY = 96485.33212
#: J/(mol K), CODATA 2018 (exact)
GAS_CONSTANT = 8.314462618
#: the carbonate system at 25 degC on a concentration basis, as core's well-mixed-carbonate v1
#: states it (Kw 1e-14, pK1 6.37, pK2 10.32)
KW = 1.0e-14
PK1 = 6.37
PK2 = 10.32
#: standard atomic weights, IUPAC 2021 abridged, kg/kmol (the values a molar mass is computed
#: with in core, so a kg of CO is the same kg on both sides)
ATOMIC_MASS = {"H": 1.008, "C": 12.011, "O": 15.999, "K": 39.098}
M_CO = ATOMIC_MASS["C"] + ATOMIC_MASS["O"]  # 28.010 kg/kmol
M_KOH = ATOMIC_MASS["K"] + ATOMIC_MASS["O"] + ATOMIC_MASS["H"]  # 56.105 kg/kmol
SECONDS_PER_HOUR = 3600.0


# -- the measured point -----------------------------------------------------------------------


def _mean_sd(values: list[float]) -> tuple[float, float | None, int]:
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return mean, None, n
    return mean, math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)), n


def measured_point(point_id: str = "P200", path: Path = MEASUREMENTS) -> dict:
    """The means (and sample sd, count) of one measured point, from the replicates.

    - FE_i = n_i F x_i Ndot / I, Ndot = outlet_flow (sccm) 1e-6/60 m3/s p_std / (R T_std);
    - n_K = (V0 - V2) c V_anolyte / V_aliquot, n_C = (V2 - V1) c V_anolyte / V_aliquot;
      WDE = 1 - F (n_K + n_C) / (I t); Cx = n_C / (n_K + n_C).
    """
    data = yaml.safe_load(path.read_text())
    point = next(p for p in data["points"] if p["id"] == point_id)
    area_cm2 = float(data["cell"]["active_area"]["value"])
    j_ma_cm2 = float(point["current_density"]["value"])
    current = j_ma_cm2 * 1e-3 * area_cm2  # A
    duration = float(point["duration"]["value"])  # s
    std = data["gas"]["standard_conditions"]
    t_std = float(std["temperature"]["value"])
    p_std = float(std["pressure"]["value"]) * 1e3
    assert data["gas"]["flow_unit"] == "sccm"
    mol_s_per_sccm = 1e-6 / 60.0 * p_std / (GAS_CONSTANT * t_std)
    factor = float(data["gas"].get("flow_correction", {}).get("factor", 1.0))
    electrons = {p["id"]: int(p["electrons"]) for p in data["products"]}
    titration = data["titration"]
    assert titration["titrant_concentration"]["unit"] == "mol/L"
    assert titration["anolyte_volume"]["unit"] == titration["aliquot_volume"]["unit"] == "mL"
    # mol of titrant per mL read, scaled from the aliquot to the anolyte
    scale = (
        1e-3
        * float(titration["titrant_concentration"]["value"])
        * float(titration["anolyte_volume"]["value"])
        / float(titration["aliquot_volume"]["value"])
    )
    voltage, wde, cx = [], [], []
    fe: dict[str, list[float]] = {name: [] for name in electrons}
    for rep in point["replicates"]:
        voltage.append(float(rep["voltage"]["value"]))
        if "outlet_flow" in rep:
            ndot = float(rep["outlet_flow"]) * mol_s_per_sccm * factor
            for name, x in rep.get("fractions", {}).items():
                assert x["unit"] == "ppm"
                fe[name].append(
                    electrons[name] * FARADAY * float(x["value"]) * 1e-6 * ndot / current
                )
        v = rep["titration"]
        n_k = (v["V0"] - v["V2"]) * scale
        n_c = (v["V2"] - v["V1"]) * scale
        wde.append(1.0 - FARADAY * (n_k + n_c) / (current * duration))
        cx.append(n_c / (n_k + n_c))
    out = {
        "point": point_id,
        "current_density_a_m2": j_ma_cm2 * 10.0,
        "bench_current_a": current,
        "bench_area_cm2": area_cm2,
        "voltage_v": _mean_sd(voltage),
        "fe": {name: _mean_sd(values) for name, values in fe.items() if values},
        "wde": _mean_sd(wde),
        "co_ion_carbon_fraction": _mean_sd(cx),
        "duration_h": duration / SECONDS_PER_HOUR,
        "anolyte_volume_ml": float(titration["anolyte_volume"]["value"]),
        "thermoneutral_v": {
            p["id"]: float(p["thermoneutral_voltage"]["value"])
            for p in data["products"]
            if "thermoneutral_voltage" in p
        },
    }
    return out


def stated_co_ion_carbon_fraction(path: Path = CELLS, cell: str = "bench-cell") -> float:
    """The carbon share of the co-ion current the cell's membrane block states (the measured
    P200 titration value rounded): the split the duties run with."""
    data = yaml.safe_load(path.read_text())
    block = next(c for c in data["cells"] if c["id"] == cell)["membrane"]["co_ion_crossover"]
    return float(block["HCO3-"])


# -- anolyte ----------------------------------------------------------------------------------


def charge_per_carbon(ph: float) -> float:
    """g(h) = ([HCO3-] + 2 [CO3-2]) / C_T at h = 10**-pH (eq/mol of carbon)."""
    h = 10.0**-ph
    k1, k2 = 10.0**-PK1, 10.0**-PK2
    return (k1 * h + 2 * k1 * k2) / (h * h + k1 * h + k1 * k2)


def co_ion_charge_per_mol(cx: float, ph: float = 12.0) -> float:
    """(1 - Cx) + Cx g: the drop of [K+] - C_T g per mol of co-ion crossing."""
    return (1.0 - cx) + cx * charge_per_carbon(ph)


def usable_hydroxide(c0: float = 1.0, ph: float = 12.0) -> float:
    """c0 - [OH-] + [H+] at the threshold (mol/L): 0.99 for 1 M at pH 12."""
    h = 10.0**-ph
    return c0 - KW / h + h


def time_to_threshold_h(
    volume_l: float, current_a: float, wde: float, cx: float, c0: float = 1.0, ph: float = 12.0
) -> float:
    """Constant current, no dosing, bleed, make-up or degassing (core ADR 0043)."""
    co_ion_mol_s = (1.0 - wde) * current_a / FARADAY
    return (
        volume_l * usable_hydroxide(c0, ph) / (co_ion_mol_s * co_ion_charge_per_mol(cx, ph)) / 3600
    )


def volume_to_horizon_l(
    horizon_h: float, current_a: float, wde: float, cx: float, c0: float = 1.0, ph: float = 12.0
) -> float:
    """V = N I H (1 - WDE)((1 - Cx) + Cx g) / (F (c0 - [OH-] + [H+])): the exact volume."""
    return horizon_h / time_to_threshold_h(1.0, current_a, wde, cx, c0, ph)


def final_state_mol_l(
    volume_l: float, horizon_h: float, current_a: float, wde: float, cx: float, c0: float = 1.0
) -> dict:
    """[K+] and C_T after the horizon at *volume_l* (no dosing, bleed or make-up)."""
    co_ion_mol = (1.0 - wde) * current_a * horizon_h * 3600 / FARADAY
    return {
        "cation": c0 - (1.0 - cx) * co_ion_mol / volume_l,
        "carbon": cx * co_ion_mol / volume_l,
    }


# -- stacks -----------------------------------------------------------------------------------


def round_up_sig(x: float, digits: int = 4) -> float:
    """*x* > 0 rounded up to *digits* significant figures (core writes a duty volume so)."""
    exponent = math.floor(math.log10(x)) - (digits - 1)
    return float(f"{math.ceil(x / 10.0**exponent - 1e-9)}e{exponent}")


def up_mm(x: float) -> float:
    return math.ceil(x * 1000 - 1e-6) / 1000


def arrangement(
    delivered_kg_h: float,
    recovery: float,
    cell_area_cm2: float,
    current_a: float,
    voltage_v: float,
    fe: float,
    max_stack_voltage_v: float,
    electrons: int = 2,
) -> dict:
    """A = n F Ndot / (FE j) for the product formed, ceil(A / A_cell) cells, at most
    floor(U_max / U) in series, the stacks and the cells shared evenly (core ADR 0044)."""
    formed = delivered_kg_h / recovery
    ndot_mol_s = formed / (M_CO * 1e-3) / SECONDS_PER_HOUR
    a_cell = cell_area_cm2 * 1e-4
    j = current_a / a_cell
    area = electrons * FARADAY * ndot_mol_s / (fe * j)
    cells = math.ceil(area / a_cell - 1e-9)
    most = math.floor(max_stack_voltage_v / voltage_v + 1e-9)
    stacks = math.ceil(cells / most - 1e-9)
    per_stack = math.ceil(cells / stacks - 1e-9)
    total = stacks * per_stack
    dc_w = total * voltage_v * current_a
    formed_out = total * current_a * fe / (electrons * FARADAY) * M_CO * 1e-3 * SECONDS_PER_HOUR
    return {
        "formed_kg_h": formed,
        "area_m2": area,
        "cells_required": cells,
        "max_in_series": most,
        "stacks": stacks,
        "cells_per_stack": per_stack,
        "cells": total,
        "stack_voltage_v": per_stack * voltage_v,
        "bus_current_a": stacks * current_a,
        "total_current_a": total * current_a,
        "dc_power_kw": dc_w / 1e3,
        "co_formed_kg_h": formed_out,
        "co_delivered_kg_h": formed_out * recovery,
        "margin": formed_out / formed - 1.0,
        "kwh_per_kg_formed": dc_w / 1e3 / formed_out,
        "kwh_per_kg_delivered": dc_w / 1e3 / (formed_out * recovery),
    }


def stack_envelope_m(
    per_stack: int, cell_area_cm2: float, pitch_mm: float, end_plates_mm: float, margin_mm: float
) -> dict:
    """L = cells x pitch + end plates, W = H = sqrt(A_cell) + 2 x frame margin."""
    side = math.sqrt(cell_area_cm2) * 1e-2 + 2 * margin_mm * 1e-3
    return {
        "length": per_stack * pitch_mm * 1e-3 + end_plates_mm * 1e-3,
        "width": side,
        "height": side,
    }


def tank_m(volume_l: float, margin: float, aspect: float) -> dict:
    """A vertical flat-ended cylinder holding V (1 + margin) at H/D (core rounds D and H up to
    the mm, H from the unrounded D)."""
    held = volume_l * (1 + margin) / 1000
    d = (4 * held / (math.pi * aspect)) ** (1 / 3)
    return {
        "held_m3": held,
        "diameter": up_mm(d),
        "height": up_mm(aspect * d),
        "diameter_exact": d,
        "height_exact": aspect * d,
    }


def max_volume_for_height_l(height_m: float, margin: float, aspect: float) -> float:
    """The largest working volume whose tank of H/D *aspect* stays within *height_m*."""
    d = height_m / aspect
    return math.pi / 4 * d * d * height_m * 1000 / (1 + margin)


# -- Skid B: continuous dosing at a steady state ----------------------------------------------


def skid_b_steady(
    current_a: float,
    wde: float,
    cx: float,
    hydroxide_mol_l: float,
    carbon_mol_l: float,
    dose_mol_l: float,
    volume_l: float,
) -> dict:
    """The bleed b = Cx (1 - WDE) N I / (F C_T); the cation dosed = the cation bled
    b ([OH-] + C_T g) plus the cation to the cathode (1 - Cx)(1 - WDE) N I / F; the make-up
    water b - dose (constant volume). g at the steady state's pH, from the charge balance."""
    co_ion_mol_h = (1.0 - wde) * current_a / FARADAY * SECONDS_PER_HOUR
    carbon_in = cx * co_ion_mol_h
    cation_out = (1.0 - cx) * co_ion_mol_h
    bleed = carbon_in / carbon_mol_l
    ph = 14.0 + math.log10(hydroxide_mol_l)  # concentration basis, [OH-] = Kw / h
    g = charge_per_carbon(ph)
    cation_mol_l = hydroxide_mol_l + carbon_mol_l * g - 10.0**-ph
    dose_mol_h = bleed * cation_mol_l + cation_out
    dose_l_h = dose_mol_h / dose_mol_l
    ionic = 0.5 * (cation_mol_l + hydroxide_mol_l + carbon_mol_l * ((2 - g) * 1 + (g - 1) * 4))
    return {
        "bleed_l_h": bleed,
        "cation_mol_l": cation_mol_l,
        "ph": ph,
        "dose_mol_h": dose_mol_h,
        "dose_kg_koh_h": dose_mol_h * M_KOH * 1e-3,
        "dose_solution_l_h": dose_l_h,
        "makeup_water_l_h": bleed - dose_l_h,
        "residence_h": volume_l / bleed,
        "ionic_strength_mol_l": ionic,
        "carbon_in_mol_h": carbon_in,
        "cation_to_cathode_mol_h": cation_out,
    }


# -- comparison duties ------------------------------------------------------------------------


def on_off_elapsed_h(t_on_h: float, period_h: float = 24.0, duty_fraction: float = 0.5) -> float:
    """Elapsed time of an on/off schedule starting on, to *t_on_h* of operation."""
    on = period_h * duty_fraction
    full = math.floor(t_on_h / on + 1e-12)
    rest = t_on_h - full * on
    return full * period_h + rest


def koh_floor_mol_per_mol_co(wde: float, cx: float, fe: float, electrons: int = 2) -> float:
    """(1 + Cx)(1 - WDE) n / FE: the cation lost plus two hydroxide per carbon gained (all as
    carbonate) per mol of CO formed: no regime can use less KOH."""
    return (1.0 + cx) * (1.0 - wde) * electrons / fe


def heat_w(current_a: float, voltage_v: float, fe: dict, thermoneutral_v: dict) -> float:
    """Q = I (U - sum FE_i U_tn,i) at an isothermal boundary, per cell."""
    return current_a * (voltage_v - sum(fe[n] * thermoneutral_v[n] for n in thermoneutral_v))


# -- the design inputs the hand values rest on (spec #330 sections 2 to 4, all ASSUMED) -------

DESIGN = {
    "co_delivered_kg_h": 0.100,
    "recovery": 0.90,
    "cell_area_cm2": 100.0,
    "cell_current_a": 20.0,
    "max_stack_voltage_v": 48.0,
    "rectifier_efficiency": 0.95,
    "cell_pitch_mm": 8.0,
    "end_plates_mm": 120.0,
    "frame_margin_mm": 40.0,
    "threshold_ph": 12.0,
    "koh_fill_mol_l": 1.0,
    "durations_h": [1000.0, 10000.0],
    "reservoir_margin": 0.25,
    "reservoir_aspect": 1.5,
    "envelope_height_m": 2.20,
    "envelope_plan_m": [6.06, 2.44],
    "skid_b_volume_l": 50.0,
    "skid_b_hydroxide_mol_l": 0.5,
    "skid_b_carbon_mol_l": 0.25,
    "dose_concentration_mol_l": 5.0,
    "dose_density_kg_l": 1.22,
    "dosing_pump_margin": 0.5,
    "dosing_tank_margin": 0.2,
    "dosing_tank_aspect": 1.2,
    "dosing_tank_refill_h": 168.0,
    "flow_per_area_ml_min_cm2": 4.0,
    "anolyte_density_kg_m3": 1050.0,
    "onoff_period_h": 24.0,
    "onoff_duty_fraction": 0.5,
    "part_load_ma_cm2": [200.0, 100.0],
    "part_load_step_h": [12.0, 12.0],
}


def hand_values(design: dict = DESIGN) -> dict:
    """Every frozen hand value of results/expected.yaml, from the measured points and *design*.

    The duties run with the co-ion split the cell's membrane block states (``HCO3-`` 0.670,
    the P200 titration mean 0.6698 rounded); the hand values use the same split.
    """
    d = design
    p200 = measured_point("P200")
    p100 = measured_point("P100")
    u, fe, wde = p200["voltage_v"][0], p200["fe"]["CO"][0], p200["wde"][0]
    cx = stated_co_ion_carbon_fraction()
    i = d["cell_current_a"]
    arr = arrangement(
        d["co_delivered_kg_h"],
        d["recovery"],
        d["cell_area_cm2"],
        i,
        u,
        fe,
        d["max_stack_voltage_v"],
    )
    total_a = arr["total_current_a"]
    fe_all = {n: s[0] for n, s in p200["fe"].items()}
    out: dict = {
        "inputs": {
            "voltage_v": u,
            "fe_co": fe,
            "fe_h2": fe_all["H2"],
            "wde": wde,
            "co_ion_carbon_fraction_measured": p200["co_ion_carbon_fraction"][0],
            "co_ion_carbon_fraction": cx,
            "charge_per_carbon_ph12": charge_per_carbon(d["threshold_ph"]),
            "usable_hydroxide_mol_l": usable_hydroxide(d["koh_fill_mol_l"], d["threshold_ph"]),
            "sd": {
                "voltage_v": p200["voltage_v"][1],
                "fe_co": p200["fe"]["CO"][1],
                "wde": p200["wde"][1],
                "co_ion_carbon_fraction": p200["co_ion_carbon_fraction"][1],
            },
            "n": {
                "voltage_v": p200["voltage_v"][2],
                "fe_co": p200["fe"]["CO"][2],
                "wde": p200["wde"][2],
            },
        },
        # the measured electrolyte state (E9): the bench anolyte after its 1 h run, carbon
        # Cx (1 - WDE) I t / (F V_anolyte), and the run length
        "measured_state": {
            "carbon_mol_l": p200["co_ion_carbon_fraction"][0]
            * (1 - wde)
            * p200["bench_current_a"]
            * p200["duration_h"]
            * SECONDS_PER_HOUR
            / FARADAY
            / (p200["anolyte_volume_ml"] * 1e-3),
            "hydroxide_fresh_mol_l": d["koh_fill_mol_l"],
            "time_on_stream_h": p200["duration_h"],
        },
        "E1": {
            **arr,
            "envelope_m": stack_envelope_m(
                arr["cells_per_stack"],
                d["cell_area_cm2"],
                d["cell_pitch_mm"],
                d["end_plates_mm"],
                d["frame_margin_mm"],
            ),
            "ac_power_kw": arr["dc_power_kw"] / d["rectifier_efficiency"],
            "stack_heat_kw": arr["cells"] * heat_w(i, u, fe_all, p200["thermoneutral_v"]) / 1e3,
            "recirculation_l_min": d["flow_per_area_ml_min_cm2"]
            * arr["cells"]
            * d["cell_area_cm2"]
            / 1e3,
        },
    }
    out["E1"]["recirculation_kg_h"] = (
        out["E1"]["recirculation_l_min"] * 60 * d["anolyte_density_kg_m3"] / 1e3
    )
    # E2: Skid A, the reservoir lasts the campaign
    e2: dict = {}
    for h in d["durations_h"]:
        exact = volume_to_horizon_l(h, total_a, wde, cx, d["koh_fill_mol_l"], d["threshold_ph"])
        written = round_up_sig(exact * (1 + 1e-6))
        tank = tank_m(written, d["reservoir_margin"], d["reservoir_aspect"])
        e2[int(h)] = {
            "volume_exact_l": exact,
            "volume_written_l": written,
            "tank": tank,
            "fits_height": tank["height"] <= d["envelope_height_m"],
            "fits_plan": tank["diameter"] <= min(d["envelope_plan_m"]),
            "final": final_state_mol_l(written, h, total_a, wde, cx, d["koh_fill_mol_l"]),
        }
    lo, hi = (int(h) for h in d["durations_h"])
    e2["volume_ratio"] = e2[hi]["volume_written_l"] / e2[lo]["volume_written_l"]
    e2["diameter_ratio"] = e2[hi]["tank"]["diameter_exact"] / e2[lo]["tank"]["diameter_exact"]
    vmax = max_volume_for_height_l(
        d["envelope_height_m"], d["reservoir_margin"], d["reservoir_aspect"]
    )
    e2["max_volume_in_envelope_l"] = vmax
    e2["max_duration_in_envelope_h"] = vmax / volume_to_horizon_l(1.0, total_a, wde, cx)
    out["E2"] = e2
    # E3: Skid B, continuous dosing at its steady state
    b = skid_b_steady(
        total_a,
        wde,
        cx,
        d["skid_b_hydroxide_mol_l"],
        d["skid_b_carbon_mol_l"],
        d["dose_concentration_mol_l"],
        d["skid_b_volume_l"],
    )
    window = min(d["dosing_tank_refill_h"], min(d["durations_h"]))
    b["dosing_pump_l_h"] = b["dose_solution_l_h"] * (1 + d["dosing_pump_margin"])
    b["dosing_pump_kg_h"] = b["dosing_pump_l_h"] * d["dose_density_kg_l"]
    b["dosing_tank_held_l"] = b["dose_solution_l_h"] * window * (1 + d["dosing_tank_margin"])
    b["dosing_tank"] = tank_m(
        b["dose_solution_l_h"] * window, d["dosing_tank_margin"], d["dosing_tank_aspect"]
    )
    b["refills"] = {
        int(h): math.ceil(h / d["dosing_tank_refill_h"] - 1e-9) for h in d["durations_h"]
    }
    b["totals"] = {
        int(h): {
            "dosed_solution_l": b["dose_solution_l_h"] * h,
            "bleed_l": b["bleed_l_h"] * h,
            "makeup_water_l": b["makeup_water_l_h"] * h,
        }
        for h in d["durations_h"]
    }
    b["dosing_tank_without_interval_l"] = {
        int(h): b["dose_solution_l_h"] * h * (1 + d["dosing_tank_margin"]) for h in d["durations_h"]
    }
    out["E3"] = b
    # E4: KOH per kg CO delivered (the arrangement's delivered output)
    delivered = arr["co_delivered_kg_h"]
    koh = M_KOH * 1e-3  # kg/mol
    e4: dict = {"skid_a": {}, "skid_b_fill_share": {}}
    for h in d["durations_h"]:
        e4["skid_a"][int(h)] = (
            e2[int(h)]["volume_written_l"] * d["koh_fill_mol_l"] * koh / (delivered * h)
        )
        e4["skid_b_fill_share"][int(h)] = (
            d["skid_b_volume_l"] * d["koh_fill_mol_l"] * koh / (delivered * h)
        )
    e4["skid_b_makeup"] = b["dose_kg_koh_h"] / delivered
    e4["floor_per_kg_formed"] = koh_floor_mol_per_mol_co(wde, cx, fe) * M_KOH / M_CO
    e4["floor_per_kg_delivered"] = e4["floor_per_kg_formed"] / d["recovery"]
    e4["skid_a_per_kg_formed_exact"] = (
        co_ion_charge_per_mol(cx, d["threshold_ph"])
        / usable_hydroxide(d["koh_fill_mol_l"], d["threshold_ph"])
        * (1 - wde)
        * 2
        / fe
        * M_KOH
        / M_CO
    )
    out["E4"] = e4
    # E5: on/off at equal CO formed, 0.5 H of D-A's operation
    out["E5"] = {
        int(h): {
            "co_target_kg": 0.5 * h * arr["co_formed_kg_h"],
            "t_on_h": 0.5 * h,
            "elapsed_h": on_off_elapsed_h(0.5 * h, d["onoff_period_h"], d["onoff_duty_fraction"]),
        }
        for h in d["durations_h"]
    }
    # E6: 12 h at P200 and 12 h at P100, at equal CO formed
    u1, fe1, w1 = p100["voltage_v"][0], p100["fe"]["CO"][0], p100["wde"][0]
    t200, t100 = d["part_load_step_h"]
    r = d["part_load_ma_cm2"][1] / d["part_load_ma_cm2"][0]
    co_full, co_part = fe * t200, fe1 * t100 * r  # per unit of the full current
    per_co = t200 + t100 * r
    out["E6"] = {
        "p100": {"voltage_v": u1, "fe_co": fe1, "wde": w1},
        "co_share_at_p200": co_full / (co_full + co_part),
        "charge_ratio": per_co / (co_full + co_part) * fe,
        "deficit_ratio": ((1 - wde) * t200 + (1 - w1) * t100 * r)
        / (co_full + co_part)
        / ((1 - wde) / fe),
        "energy_ratio": (u * t200 + u1 * t100 * r) / (co_full + co_part) / (u / fe),
        "kwh_per_kg_p200": u * 2 * FARADAY / (fe * M_CO * 1e-3) / 3.6e6,
        "kwh_per_kg_p100": u1 * 2 * FARADAY / (fe1 * M_CO * 1e-3) / 3.6e6,
    }
    return out


def lookup(values: dict, key: str):
    """The value at a dotted *key* of :func:`hand_values` (integer parts are durations)."""
    node = values
    for part in key.split("."):
        node = node[int(part)] if part.isdigit() else node[part]
    return node


def load_expected(path: Path = EXPECTED) -> dict:
    return yaml.safe_load(path.read_text())
