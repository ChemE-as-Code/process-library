"""The results of the #330 skid regeneration: invariants, records, resize report, band figures.

Used by scripts/regen.py (steps 14 to 17); reads no core module and runs no command, so every
function here is plain arithmetic on the JSON that scripts/_core.py returned:

- :func:`conditions`: the conditional-invariant check of one skid duty (step 14, DESIGN.md
  D-014): the hours outside the measured current density, temperature, electrolyte state and
  time on stream, and whether FE, WDE, U and kWh/kg may be called invariant;
- :func:`tidy` and :func:`dump`: the calculation record's deterministic JSON (floats to 10
  significant figures, sorted keys, no time stamp or git HEAD; step 16);
- :func:`resize_report`: the resize report between two scenario records (step 17), one row per
  quantity and skid with the rule it follows, its calculated cause and the frozen hand value of
  results/expected.yaml;
- :func:`range_svg` and :func:`band_svg`: the uncertainty figures of `--uncertainty` (step 15),
  drawn here as plain SVG (no plotting library), into figures/skids/<H>h/.
"""

from __future__ import annotations

import json
import math
from html import escape
from typing import Any

#: the record's schema (process-library, #330)
RECORD_SCHEMA = "process-library/skid-record/1"
RESIZE_SCHEMA = "process-library/skid-resize/1"
UNCERTAINTY_SCHEMA = "process-library/skid-uncertainty/1"
LABEL_INVARIANT = "invariant"
LABEL_ASSUMED = "held constant by assumption, not supported by measurement"
RULES = (
    "invariant-of-duration",
    "proportional-to-duration",
    "fixed-by-setpoint",
    "amortisation",
    "infeasible",
)


# -- step 14: conditional invariants -----------------------------------------------------------


def outside_intervals(t_h: list[float], margin: list[float]) -> list[tuple[float, float]]:
    """The intervals with *margin* < 0 (outside), the margin linear between the samples."""
    out: list[tuple[float, float]] = []
    for i in range(len(t_h) - 1):
        t0, t1, m0, m1 = t_h[i], t_h[i + 1], margin[i], margin[i + 1]
        dt = t1 - t0
        if dt <= 0 or (m0 >= 0 and m1 >= 0):
            continue
        if m0 < 0 and m1 < 0:
            a, b = t0, t1
        else:
            cross = t0 + dt * m0 / (m0 - m1)  # where the margin is zero
            a, b = (t0, cross) if m0 < 0 else (cross, t1)
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def union_hours(*intervals: list[tuple[float, float]]) -> tuple[float, float | None]:
    """The hours in the union of interval lists, and the first hour of it."""
    spans = sorted(span for spans in intervals for span in spans)
    total, first, end = 0.0, None, None
    for a, b in spans:
        first = a if first is None else first
        if end is None or a > end:
            total += b - a
            end = b
        elif b > end:
            total += b - end
            end = b
    return total, first


def hours_outside(t_h: list[float], margin: list[float]) -> tuple[float, float | None]:
    """Hours with *margin* < 0 (outside), linear between the samples; and the first such hour.
    For a condition of several margins, interpolate each one on its own and take the union
    (:func:`union_hours` of :func:`outside_intervals`): the minimum of two margins is not
    linear between the samples, and interpolating it puts the crossing early."""
    return union_hours(outside_intervals(t_h, margin))


def carbon_series(species: dict[str, list[float]]) -> list[float]:
    keys = [k for k in ("CO3-2", "HCO3-", "CO2") if k in species]
    return [sum(species[k][i] for k in keys) for i in range(len(species["OH-"]))]


def conditions(
    duty: dict[str, Any],
    measured: dict[str, Any],
    cooler_kw: float,
    stack_heat_kw: float,
    cell_temperature_c: float,
    measured_temperature_c: float,
) -> dict[str, Any]:
    """The four conditions of D-014 for one skid duty, each with its hours outside.

    - current density: core's ``time_outside_measured_range_h`` (the schedule against the
      measured 25-250 mA/cm2);
    - temperature: the duty model is isothermal by assumption; the condition is that the cooler
      removes the stack heat (the cooler duty of the flowsheet >= the stack heat of `cheme
      process stack`) at the measured series' temperature (both 25 degC, ASSUMED);
    - electrolyte state: OH- and dissolved carbon of the duty's species against the measured
      state (fresh 1 M KOH after its 1 h run: OH- >= its end value, carbon <= its end value);
    - time on stream: the duty's hours against the measured 1 h runs.
    """
    series = duty["series"]
    t_h = [float(x) for x in series["t_h"]]
    species = series["species_mol_l"]
    oh = [float(x) for x in species["OH-"]]
    carbon = carbon_series(species)
    tol = 1e-9
    # each margin interpolated on its own, then the union of the hours outside either
    oh_margin = [o - measured["hydroxide_min_mol_l"] + tol for o in oh]
    carbon_margin = [measured["carbon_max_mol_l"] - c + tol for c in carbon]
    oh_out, carbon_out = outside_intervals(t_h, oh_margin), outside_intervals(t_h, carbon_margin)
    electrolyte_h, electrolyte_first = union_hours(oh_out, carbon_out)
    hours = float(duty.get("operating_time_h") or duty["simulated_h"])
    outside_j = float(duty.get("time_outside_measured_range_h") or 0.0)
    cooled = cooler_kw >= stack_heat_kw * (1 - 1e-9)
    same_t = abs(cell_temperature_c - measured_temperature_c) <= 0.5
    conds = {
        "current_density": {
            "basis": "the schedule's current density against the measured 25-250 mA/cm2 (core time_outside_measured_range_h)",
            "hours_outside": outside_j,
            "first_outside_h": duty.get("first_exit_h"),
            "holds": outside_j == 0.0,
        },
        "temperature": {
            "basis": (
                "the duty model is isothermal by assumption: the cooler duty (flowsheet) against the "
                "stack heat (cheme process stack) at the cell temperature against the measured one "
                "(both 25 degC, ASSUMED)"
            ),
            "cooler_kw": cooler_kw,
            "stack_heat_kw": stack_heat_kw,
            "cell_temperature_c": cell_temperature_c,
            "measured_temperature_c": measured_temperature_c,
            "hours_outside": 0.0 if (cooled and same_t) else hours,
            "by_assumption": True,
            "holds": cooled and same_t,
        },
        "electrolyte": {
            "basis": (
                "OH- and dissolved carbon (CO3-2 + HCO3- + CO2) of the duty's species against the "
                "measured state: fresh 1 M KOH after its 1 h run (linear between the samples)"
            ),
            "measured": {k: measured[k] for k in ("hydroxide_min_mol_l", "carbon_max_mol_l")},
            "duty_range": {
                "hydroxide_mol_l": [min(oh), max(oh)],
                "carbon_mol_l": [min(carbon), max(carbon)],
            },
            "hours_outside": electrolyte_h,
            "first_outside_h": electrolyte_first,
            "first_outside_by": {
                "hydroxide_h": oh_out[0][0] if oh_out else None,
                "carbon_h": carbon_out[0][0] if carbon_out else None,
            },
            "holds": electrolyte_h == 0.0,
        },
        "time_on_stream": {
            "basis": "the duty's operating hours against the measured 1 h runs",
            "measured_h": measured["time_on_stream_h"],
            "duty_h": hours,
            "hours_outside": max(0.0, hours - measured["time_on_stream_h"]),
            "holds": hours <= measured["time_on_stream_h"],
        },
    }
    failed = [name for name, c in conds.items() if not c["holds"]]
    return {
        "conditions": conds,
        "failed": failed,
        "fe_wde_u_kwh_per_kg": LABEL_INVARIANT if not failed else LABEL_ASSUMED,
    }


# -- step 16: the deterministic record -----------------------------------------------------------


def tidy(obj: Any, digits: int = 10) -> Any:
    """Floats to *digits* significant figures (so a record does not differ by the last bit of
    the integrator), recursively; tuples to lists."""
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str)):
        return obj
    if isinstance(obj, float):
        if not math.isfinite(obj):
            return None
        return float(f"{obj:.{digits}g}") if obj != 0 else 0.0
    if isinstance(obj, dict):
        return {str(k): tidy(v, digits) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [tidy(v, digits) for v in obj]
    return str(obj)


def dump(obj: Any) -> str:
    return json.dumps(tidy(obj), indent=1, sort_keys=True, ensure_ascii=False) + "\n"


# -- step 17: the resize report ------------------------------------------------------------------

#: one row per quantity and skid: (skid, key in the record's skid block, label, unit, rule,
#: cause, the hand value's key in results/expected.yaml ({h}: the duration) or None, the
#: exponent of the duration a proportional quantity follows)
ROWS: tuple[tuple, ...] = (
    ("A", "cells", "cells", "-", "invariant-of-duration", "the stacks are sized on the product rate, not the campaign", "E1.cells_required", None),
    ("A", "stacks", "stacks on the DC bus", "-", "invariant-of-duration", "floor({max_stack_voltage_v:g} V / U) in series, the cells shared evenly", "E1.stacks", None),
    ("A", "dc_power_kw", "DC power", "kW", "invariant-of-duration", "N U I at the measured point", "E1.dc_power_kw", None),
    ("A", "co_formed_kg_h", "CO formed", "kg/h", "invariant-of-duration", "N I FE M / (2 F)", "E1.co_formed_kg_h", None),
    ("A", "kwh_per_kg_formed", "electricity per kg CO formed (DC)", "kWh/kg", "invariant-of-duration", "2 F U / (FE M): U and FE held constant by assumption (D-014)", "E1.kwh_per_kg_formed", None),
    ("A", "stack_heat_kw", "stack heat (cooler E-111)", "kW", "invariant-of-duration", "N I (U - sum FE U_tn)", "E1.stack_heat_kw", None),
    ("A", "reservoir_volume_exact_l", "reservoir T-101, exact volume to the horizon", "L", "proportional-to-duration", "V = N I H (1 - WDE)((1 - Cx) + Cx g) / (F (c0 - Kw / h + h)) at pH {threshold_ph:g}: the one fill carries the campaign's co-ion charge", "E2.{h}.volume_exact_l", 1.0),
    ("A", "reservoir_volume_l", "reservoir T-101, working volume written", "L", "proportional-to-duration", "the exact volume rounded up to 4 significant figures (reservoir.size: to_horizon)", "E2.{h}.volume_written_l", 1.0),
    ("A", "reservoir_diameter_m", "reservoir T-101 diameter", "m", "proportional-to-duration", "D = (4 V (1 + {reservoir_margin:g}) / (pi {reservoir_aspect_ratio:g}))^(1/3): the cube root of the volume", "E2.{h}.tank.diameter", 1.0 / 3.0),
    ("A", "reservoir_height_m", "reservoir T-101 height", "m", "proportional-to-duration", "H = {reservoir_aspect_ratio:g} D", "E2.{h}.tank.height", 1.0 / 3.0),
    ("A", "final_carbon_mol_l", "anolyte carbon at the end", "mol/L", "invariant-of-duration", "the fill reaches the threshold at the horizon whatever H is", "E2.{h}.final.carbon", None),
    ("A", "final_cation_mol_l", "anolyte K+ at the end", "mol/L", "invariant-of-duration", "as the carbon", "E2.{h}.final.cation", None),
    ("A", "koh_per_kg_delivered", "KOH per kg CO delivered", "kg/kg", "invariant-of-duration", "the fill and the CO both scale with H", "E4.skid_a.{h}", None),
    ("A", "koh_fill_kg_h", "KOH-FILL, campaign-averaged", "kg KOH/h", "invariant-of-duration", "V / H is constant (D-011)", None, None),
    ("A", "totals_charge_c", "charge over the campaign", "C", "proportional-to-duration", "constant current over H", None, 1.0),
    ("A", "totals_product_kg", "CO formed over the campaign", "kg", "proportional-to-duration", "constant output over H", None, 1.0),
    ("A", "items_top_m", "highest item on the frame (top above grade)", "m", "infeasible", "the reservoir grows as the cube root of H; the frame does not", None, None),
    ("A", "feasible", "skid feasible (duty and envelope)", "-", "infeasible", "the reservoir no longer fits the {usable_height_m:.2f} m usable height (D-015)", "E2.{h}.fits_height", None),
    ("B", "cells", "cells", "-", "invariant-of-duration", "the stacks are sized on the product rate, not the campaign", "E1.cells_required", None),
    ("B", "dc_power_kw", "DC power", "kW", "invariant-of-duration", "N U I at the measured point", "E1.dc_power_kw", None),
    ("B", "kwh_per_kg_formed", "electricity per kg CO formed (DC)", "kWh/kg", "invariant-of-duration", "2 F U / (FE M): U and FE held constant by assumption (D-014)", "E1.kwh_per_kg_formed", None),
    ("B", "bleed_l_h", "bleed rate", "L/h", "fixed-by-setpoint", "b = Cx (1 - WDE) N I / (F C_T) at the carbon setpoint {setpoint_carbon_mol_l:g} mol/L", "E3.bleed_l_h", None),
    ("B", "dose_mol_h", "KOH dose", "mol/h", "fixed-by-setpoint", "b [K+] + (1 - Cx)(1 - WDE) N I / F at the setpoints", "E3.dose_mol_h", None),
    ("B", "dose_l_h", "5 M KOH dosed", "L/h", "fixed-by-setpoint", "the dose over {dose_concentration_mol_l:g} mol/L", "E3.dose_solution_l_h", None),
    ("B", "makeup_l_h", "make-up water", "L/h", "fixed-by-setpoint", "b - dose (constant volume)", "E3.makeup_water_l_h", None),
    ("B", "residence_h", "residence time V / b", "h", "fixed-by-setpoint", "{reservoir_volume_l:g} L over the bleed", "E3.residence_h", None),
    ("B", "final_ph", "anolyte pH at the end", "-", "fixed-by-setpoint", "the steady state at {setpoint_hydroxide_mol_l:g} mol/L OH-", "E3.ph", None),
    ("B", "final_cation_mol_l", "anolyte K+ at the end", "mol/L", "fixed-by-setpoint", "the setpoints' charge balance", "E3.cation_mol_l", None),
    ("B", "reservoir_volume_l", "reservoir T-201 working volume", "L", "fixed-by-setpoint", "the ASSUMED {reservoir_volume_l:g} L hold-up, held by the make-up", None, None),
    ("B", "reservoir_diameter_m", "reservoir T-201 diameter", "m", "invariant-of-duration", "sized on the {reservoir_volume_l:g} L working volume", None, None),
    ("B", "dosing_pump_kg_h", "dosing pump P-202 capacity", "kg/h", "invariant-of-duration", "the dose rate x (1 + {dosing_pump_margin:g}) x {dose_density_kg_l:g} kg/L", "E3.dosing_pump_kg_h", None),
    ("B", "dosing_tank_held_l", "day tank T-202 held volume", "L", "invariant-of-duration", "sized over the refill interval {refill_interval_h:g} h (core refill_interval), not the campaign", "E3.dosing_tank_held_l", None),
    ("B", "dosing_tank_diameter_m", "day tank T-202 diameter", "m", "invariant-of-duration", "as its volume", "E3.dosing_tank.diameter", None),
    ("B", "dosing_tank_fills", "day tank fills per campaign", "-", "proportional-to-duration", "ceil(H / {refill_interval_h:g} h)", "E3.refills.{h}", 1.0),
    ("B", "dosed_solution_l", "5 M KOH dosed over the campaign", "L", "proportional-to-duration", "rate x H", "E3.totals.{h}.dosed_solution_l", 1.0),
    ("B", "bleed_l", "bleed over the campaign", "L", "proportional-to-duration", "rate x H", "E3.totals.{h}.bleed_l", 1.0),
    ("B", "makeup_water_l", "make-up water over the campaign", "L", "proportional-to-duration", "rate x H", "E3.totals.{h}.makeup_water_l", 1.0),
    ("B", "koh_dosed_per_kg_delivered", "KOH dosed per kg CO delivered", "kg/kg", "invariant-of-duration", "the dose and the CO both scale with H", "E4.skid_b_makeup", None),
    ("B", "koh_fill_per_kg_delivered", "KOH of the 50 L fill per kg CO delivered", "kg/kg", "amortisation", "one fill over H", "E4.skid_b_fill_share.{h}", -1.0),
    ("B", "koh_fill_kg_h", "KOH-FILL, campaign-averaged", "kg KOH/h", "amortisation", "{reservoir_volume_l:g} L / H (D-011)", None, -1.0),
    ("B", "feasible", "skid feasible (duty and envelope)", "-", "invariant-of-duration", "nothing on Skid B grows with H", None, None),
)  # fmt: skip


def _expected_index(expected: dict) -> dict[str, dict]:
    index = {}
    for block in (expected.get("expectations") or {}).values():
        for item in block.get("items") or []:
            index[item["key"]] = item
    return index


def _status(value, item: dict | None) -> tuple[Any, Any, str]:
    if item is None:
        return None, None, "n/a"
    want, tol = item["value"], item.get("tolerance")
    if value is None:
        return want, tol, "missing"
    if isinstance(want, bool) or tol == "exact":
        return want, tol, "pass" if value == want else "fail"
    if isinstance(tol, dict):
        if "rel" in tol:
            ok = abs(value - want) <= tol["rel"] * abs(want)
        else:
            ok = abs(value - want) <= tol.get("abs", 0.0)
        if ok and tol.get("direction") == "above 1":
            ok = value > 1
        return want, tol, "pass" if ok else "fail"
    return want, tol, "n/a"


def _changed(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)):
        return a != b
    scale = max(abs(a), abs(b), 1e-12)
    return abs(a - b) > 1e-6 * scale


def _cause(template: str, records: dict[float, dict], skid: str) -> str:
    """A cause with its inputs from the records' sizing_basis (both durations' when they
    differ), so the text follows the inputs the runs used."""
    lo, hi = sorted(records)
    texts = []
    for h in (lo, hi):
        basis = records[h]["skids"][skid].get("sizing_basis") or {}
        try:
            texts.append(template.format_map(basis))
        except KeyError as exc:
            raise KeyError(f"resize cause {template!r}: the record has no sizing_basis {exc}") from exc
    return texts[0] if texts[0] == texts[1] else f"{texts[0]} (at {hi:g} h: {texts[1]})"


def resize_report(
    records: dict[float, dict], expected: dict, errata: dict | None = None
) -> dict[str, Any]:
    """The rows between the two scenario records (keys: the durations); *errata*: the
    corrections of the frozen file (results/expected-errata.yaml), reported, never applied."""
    lo, hi = sorted(records)
    index = _expected_index(expected)
    ratio = hi / lo
    rows = []
    for skid, key, label, unit, rule, template, hand, exponent in ROWS:
        cause = _cause(template, records, skid)
        a = records[lo]["skids"][skid].get(key)
        b = records[hi]["skids"][skid].get(key)
        changed = _changed(a, b)
        if rule in ("invariant-of-duration", "fixed-by-setpoint"):
            holds = not changed
            if key == "feasible":
                holds = a == b
        elif rule in ("proportional-to-duration", "amortisation") and exponent is not None:
            want = ratio**exponent
            got = (b / a) if a else None
            tol = 0.2 if key == "dosing_tank_fills" else 2e-3  # ceil(H / 168 h)
            holds = got is not None and abs(got - want) <= tol * want
        else:  # infeasible: the row reports where the skid stops fitting
            holds = True
        values = {}
        for h, v in ((lo, a), (hi, b)):
            item = index.get(hand.format(h=f"{h:g}")) if hand else None
            want, tol, status = _status(v, item)
            values[f"{h:g}"] = {"value": v, "hand": want, "tolerance": tol, "status": status}
        if key == "feasible" and skid == "A":
            calc = "; ".join(records[hi]["skids"]["A"].get("reasons") or []) or "feasible at both"
        elif key == "items_top_m":
            calc = (
                f"{a:.3f} m at {lo:g} h, {b:.3f} m at {hi:g} h against the envelope top "
                f"{records[hi]['skids'][skid]['envelope_top_m']:.3f} m"
            )
        elif rule in ("proportional-to-duration", "amortisation") and a:
            calc = f"x {b / a:.6g} for H x {ratio:g} ({cause})"
        else:
            calc = cause if not changed else f"{cause}; changed by {(b - a) / a if a else b:+.3g}"
        rows.append(
            {
                "skid": skid,
                "quantity": key,
                "label": label,
                "unit": unit,
                "values": values,
                "changed": changed,
                "rule": rule,
                "rule_holds": holds,
                "cause": calc,
            }
        )
    unchanged = {
        "pid_sha256": {
            name: {
                f"{lo:g}": records[lo]["pid_sha256"].get(name),
                f"{hi:g}": records[hi]["pid_sha256"].get(name),
                "unchanged": records[lo]["pid_sha256"].get(name)
                == records[hi]["pid_sha256"].get(name),
            }
            for name in sorted(records[lo]["pid_sha256"])
        },
        "stack_dimensions_m": {
            skid: {
                f"{lo:g}": records[lo]["skids"][skid]["stack_envelope_m"],
                f"{hi:g}": records[hi]["skids"][skid]["stack_envelope_m"],
                "unchanged": records[lo]["skids"][skid]["stack_envelope_m"]
                == records[hi]["skids"][skid]["stack_envelope_m"],
            }
            for skid in ("A", "B")
        },
    }
    return {
        "schema": RESIZE_SCHEMA,
        "issue": 330,
        "durations_h": [lo, hi],
        "records": [f"results/scenarios/{h:g}h/record.json" for h in (lo, hi)],
        "expected": "results/expected.yaml",
        "errata": [
            {k: e.get(k) for k in ("id", "item", "statement", "correction", "effect")}
            for e in (errata or {}).get("errata") or []
        ],
        "rows": rows,
        "unchanged_artefacts": unchanged,
        "summary": {
            "rows": len(rows),
            "hand_checks_failed": sum(
                1 for r in rows for v in r["values"].values() if v["status"] == "fail"
            ),
            "rules_broken": [f"{r['skid']} {r['quantity']}" for r in rows if not r["rule_holds"]],
            "feasible": {
                skid: {f"{h:g}": records[h]["skids"][skid]["feasible"] for h in (lo, hi)}
                for skid in ("A", "B")
            },
            "sentences": sorted(
                {s for h in (lo, hi) for sk in ("A", "B") for s in records[h]["skids"][sk]["sentences"]}
            ),
        },
    }


def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, float):
        if v == 0:
            return "0"
        if abs(v) >= 1e5 or abs(v) < 1e-3:
            return f"{v:.4g}"
        return f"{v:.5g}"
    return str(v)


def resize_markdown(report: dict[str, Any]) -> str:
    lo, hi = (f"{h:g}" for h in report["durations_h"])
    s = report["summary"]
    out = [
        f"# Resize report: {lo} h against {hi} h (#330)",
        "",
        "Generated by `cheme run scripts/regen.py` (step 17) from "
        + " and ".join(f"`{r}`" for r in report["records"])
        + "; the hand values and tolerances are the frozen ones of `results/expected.yaml`. Do not"
        " edit: rerun the scenarios.",
        "",
        "Rules: `invariant-of-duration` (the same at both durations), `proportional-to-duration`"
        " (x the duration ratio, or its cube root for a tank's dimensions), `fixed-by-setpoint`"
        " (held by Skid B's setpoints), `amortisation` (a one-off amount over the campaign),"
        " `infeasible` (where a skid stops fitting). FE, WDE, U and kWh/kg are held constant by"
        " assumption, not supported by measurement (DESIGN.md D-014).",
        "",
    ]
    for sentence in s["sentences"]:
        out += [f"**{sentence}**", ""]
    out += [
        f"| skid | quantity | unit | {lo} h | {hi} h | changed | rule | cause | hand {lo} h | hand {hi} h | status |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in report["rows"]:
        a, b = r["values"][lo], r["values"][hi]
        status = "/".join(sorted({a["status"], b["status"]} - {"n/a"})) or "n/a"
        rule = r["rule"] + ("" if r["rule_holds"] else " (broken)")
        out.append(
            f"| {r['skid']} | {r['label']} | {r['unit']} | {_fmt(a['value'])} | {_fmt(b['value'])} | "
            f"{_fmt(r['changed'])} | {rule} | {r['cause']} | {_fmt(a['hand'])} | {_fmt(b['hand'])} | {status} |"
        )
    if report.get("errata"):
        out += [
            "",
            "Errata of the frozen file (`results/expected-errata.yaml`; the frozen values and "
            "tolerances stand, ADR 0030):",
            "",
        ]
        for e in report["errata"]:
            out.append(
                f"- {e['id']} (`{e['item']}`): the frozen file says \"{e['statement']}\". "
                f"{e['correction']} {e['effect']}"
            )
    u = report["unchanged_artefacts"]
    out += ["", "Unchanged artefacts:", ""]
    for name, v in u["pid_sha256"].items():
        out.append(f"- `{name}` sha256 `{(v[lo] or '-')[:16]}` at both: {_fmt(v['unchanged'])}")
    for skid, v in u["stack_dimensions_m"].items():
        dims = v[lo]
        out.append(
            f"- Skid {skid} stacks {dims['length']:g} x {dims['width']:g} x {dims['height']:g} m"
            f" at both: {_fmt(v['unchanged'])}"
        )
    out += [
        "",
        f"{s['rows']} rows; hand checks failed: {s['hand_checks_failed']}; rules broken: "
        + (", ".join(s["rules_broken"]) if s["rules_broken"] else "none")
        + ".",
        "",
    ]
    return "\n".join(out)


def readme_table(records: dict[float, dict], uncertainty: dict[float, dict] | None = None) -> str:
    """The results table of README.md (regen step 17), from the scenario records and their
    uncertainty runs: one column per skid and duration, "same" where a cell repeats the one
    before it in its row."""
    hs = sorted(records)
    cols = [(skid, h) for skid in ("A", "B") for h in hs]

    def cell(row: str, skid: str, h: float) -> str | None:
        s = records[h]["skids"][skid]
        b = s.get("sizing_basis") or {}
        if row == "stacks":
            return f"{s['stacks']} x {s['cells_per_stack']} cells, {s['stack_voltage_v']:.1f} V, {s['bus_current_a']:g} A"
        if row == "power":
            return f"{s['dc_power_kw']:.3f} kW, {s['co_formed_kg_h']:.4f} / {s['co_delivered_kg_h']:.4f} kg/h"
        if row == "kwh":
            return f"{s['kwh_per_kg_formed']:.2f} kWh/kg"
        if row == "reservoir":
            return (
                f"{s['reservoir_tag']} {s['reservoir_volume_l']:,.0f} L, D {s['reservoir_diameter_m']:.3f}"
                f" x H {s['reservoir_height_m']:.3f} m"
            )
        if row == "dosing":
            if not s.get("dose_mol_h"):
                return "none"
            return (
                f"{s['dose_mol_h']:.3f} mol/h ({s['dose_l_h']:.3f} L/h of "
                f"{b.get('dose_concentration_mol_l', 0):g} M), {s['bleed_l_h']:.3f} L/h, {s['makeup_l_h']:.3f} L/h"
            )
        if row == "end":
            return f"pH {s['final_ph']:.2f}, {s['final_carbon_mol_l']:.2f} mol/L carbon"
        if row == "koh":
            return f"{s['koh_per_kg_delivered']:.3f}"
        if row == "fits":
            if s["envelope_feasible"]:
                return f"yes, {s['headroom_left_m']:.2f} m left"
            if s["headroom_left_m"] < 0:
                return f"**no**: {-s['headroom_left_m']:.2f} m too tall"
            return "**no** (the record's reasons)"
        if row == "wde":
            doc = (uncertainty or {}).get(h)
            case = next((c for c in (doc or {}).get("cases", []) if c["case"] == "WDE -1 sd"), None)
            if case is None:
                return None
            if skid == "A":
                lasts = case["skid_a_design_volume_lasts_h"]
                return f"the {records[h]['skids']['A']['reservoir_volume_l']:,.0f} L reservoir reaches pH {b.get('threshold_ph', 12):g} at {lasts:,.0f} h"
            return f"dose {case['skid_b_dose_mol_h']:.2f} mol/h"
        raise KeyError(row)

    wde_label = "WDE -1 sd"
    for h in hs:
        doc = (uncertainty or {}).get(h)
        case = next((c for c in (doc or {}).get("cases", []) if c["case"] == "WDE -1 sd"), None)
        if case:
            wde_label = f"WDE -1 sd ({case['cell']['wde']:.4f})"
            break
    usable = records[hs[0]]["skids"]["A"].get("sizing_basis", {}).get("usable_height_m", 0.0)
    rows = (
        ("stacks", "stacks"),
        ("power", "DC power, CO formed / delivered"),
        ("kwh", "electricity per kg CO formed (DC)"),
        ("reservoir", "anolyte reservoir"),
        ("dosing", "KOH dosing, bleed, make-up"),
        ("end", "anolyte at the end"),
        ("koh", "KOH per kg CO delivered"),
        ("fits", f"fits the 20 ft frame ({usable:.2f} m usable height)"),
        ("wde", wde_label),
    )
    out = [
        "| | " + " | ".join(f"Skid {skid}, {h:,.0f} h" for skid, h in cols) + " |",
        "|---|" + "---|" * len(cols),
    ]
    for row, label in rows:
        cells = [cell(row, skid, h) for skid, h in cols]
        if all(c is None for c in cells):
            continue
        shown, before = [], None
        for c in cells:
            shown.append("same" if c is not None and c == before else (c or "-"))
            before = c
        out.append(f"| {label} | " + " | ".join(shown) + " |")
    sentences = sorted({x for h in hs for sk in ("A", "B") for x in records[h]["skids"][sk]["sentences"]})
    out.append("")
    for sentence in sentences:
        out.append(f'"{sentence}".')
    return "\n".join(out) + "\n"


# -- step 15: the uncertainty figures ------------------------------------------------------------

_INK = "#0b0b0b"
_INK2 = "#52514e"
_MUTED = "#8a8985"
_GRID = "#e4e3df"
_SURFACE = "#fcfcfb"
_SERIES = ("#2a78d6", "#eb6834", "#1baf7a")  # categorical slots 1-3 (validated all-pairs)


def _svg(width: int, height: int, body: list[str], title: str, desc: str) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif" '
            'role="img" aria-labelledby="t d">',
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>',
            f'<rect width="{width}" height="{height}" fill="{_SURFACE}"/>',
            *body,
            "</svg>",
            "",
        ]
    )


def _case_style(case: str) -> tuple[str, bool]:
    """A bounding case's colour (by parameter) and fill (filled: + 1 sd or the meter basis)."""
    if "20 degC" in case:
        return _INK2, True
    colour = _SERIES[0] if "WDE" in case else _SERIES[1] if "FE" in case else _SERIES[2]
    return colour, "+1 sd" in case


def range_svg(quantities: list[dict], title: str, note: str) -> str:
    """One row per quantity: the change from the specified mean for each bounding case, a marker
    per case on one shared percent axis (colour: the parameter; filled +1 sd, hollow -1 sd; a
    grey square the 20 degC meter basis), the largest change labelled. *quantities*: {label,
    unit, base, cases: [{case, value}]}."""
    left, right, top, row_h = 250, 60, 70, 52
    width = 900
    height = top + row_h * len(quantities) + 80
    spans = [
        abs(c["value"] / q["base"] - 1) * 100
        for q in quantities
        for c in q["cases"]
        if q["base"] and c["value"] is not None
    ]
    lim = max(5.0, math.ceil(max(spans + [0.0]) / 5) * 5)
    x0, x1 = left, width - right

    def x(pct: float) -> float:
        return x0 + (pct + lim) / (2 * lim) * (x1 - x0)

    body = [
        f'<text x="16" y="28" font-size="16" fill="{_INK}" font-weight="600">{escape(title)}</text>',
        f'<text x="16" y="48" font-size="12" fill="{_INK2}">{escape(note)}</text>',
    ]
    step = 5 if lim <= 25 else 10
    bottom = top + row_h * len(quantities)
    for pct in range(-int(lim), int(lim) + 1, step):
        body.append(
            f'<line x1="{x(pct):.1f}" y1="{top - 8}" x2="{x(pct):.1f}" y2="{bottom}" '
            f'stroke="{_GRID if pct else _MUTED}" stroke-width="1"/>'
        )
        body.append(
            f'<text x="{x(pct):.1f}" y="{bottom + 18}" font-size="11" fill="{_INK2}" '
            f'text-anchor="middle">{pct:+d} %</text>'
        )
    body.append(
        f'<text x="{(x0 + x1) / 2:.1f}" y="{bottom + 38}" font-size="12" fill="{_INK2}" '
        'text-anchor="middle">change from the measured mean (specified cell)</text>'
    )
    for i, q in enumerate(quantities):
        y = top + row_h * i + row_h / 2 - 6
        unit = "" if q["unit"] in ("-", "") else f" {q['unit']}"
        body.append(
            f'<text x="{left - 14}" y="{y - 2:.1f}" font-size="12" fill="{_INK}" text-anchor="end">'
            f"{escape(q['label'])}</text>"
        )
        body.append(
            f'<text x="{left - 14}" y="{y + 13:.1f}" font-size="11" fill="{_INK2}" text-anchor="end">'
            f"mean {escape(_fmt(q['base']))}{escape(unit)}</text>"
        )
        pcts = [
            (c, (c["value"] / q["base"] - 1) * 100)
            for c in q["cases"]
            if c["value"] is not None and q["base"]
        ]
        if not pcts:
            continue
        lo_p, hi_p = min(p for _, p in pcts + [({}, 0.0)]), max(p for _, p in pcts + [({}, 0.0)])
        body.append(
            f'<line x1="{x(lo_p):.1f}" y1="{y:.1f}" x2="{x(hi_p):.1f}" y2="{y:.1f}" '
            f'stroke="{_MUTED}" stroke-width="2" stroke-linecap="round"/>'
        )
        for c, p in pcts:
            colour, filled = _case_style(c["case"])
            tip = f"<title>{escape(c['case'])}: {escape(_fmt(c['value']))}{escape(unit)} ({p:+.1f} %)</title>"
            if "20 degC" in c["case"]:
                body.append(
                    f'<rect x="{x(p) - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" rx="2" '
                    f'fill="{colour}" stroke="{_SURFACE}" stroke-width="2">{tip}</rect>'
                )
            else:
                fill = colour if filled else _SURFACE
                body.append(
                    f'<circle cx="{x(p):.1f}" cy="{y:.1f}" r="5" fill="{fill}" stroke="{colour}" '
                    f'stroke-width="2">{tip}</circle>'
                )
        ext = max(pcts, key=lambda cp: abs(cp[1]))
        if abs(ext[1]) > 1e-9:
            anchor = "start" if x(ext[1]) < (x0 + x1) / 2 else "end"
            dx = -8 if anchor == "end" else 8
            body.append(
                f'<text x="{x(ext[1]) + dx:.1f}" y="{y + 19:.1f}" font-size="11" fill="{_INK2}" '
                f'text-anchor="{anchor}">{escape(ext[0]["case"])} {ext[1]:+.1f} %</text>'
            )
    ly = height - 16
    legend = (
        ("WDE", _SERIES[0]),
        ("FE CO", _SERIES[1]),
        ("U", _SERIES[2]),
    )
    lx = 16
    for name, colour in legend:
        body.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{colour}" stroke="{colour}" stroke-width="2"/>')
        body.append(f'<text x="{lx + 16}" y="{ly}" font-size="11" fill="{_INK2}">{name}</text>')
        lx += 80
    body.append(f'<rect x="{lx}" y="{ly - 9}" width="10" height="10" rx="2" fill="{_INK2}"/>')
    body.append(
        f'<text x="{lx + 16}" y="{ly}" font-size="11" fill="{_INK2}">FE at the 20 degC meter basis</text>'
    )
    lx += 210
    body.append(
        f'<text x="{lx}" y="{ly}" font-size="11" fill="{_INK2}">filled: mean + 1 sd; hollow: mean - 1 sd</text>'
    )
    return _svg(width, height, body, title, note)


def band_svg(
    series: list[dict], threshold: float, horizon_h: float, title: str, note: str
) -> str:
    """pH against time for a few runs of one duty (*series*: {label, t_h, ph}), with the
    threshold and the horizon marked; one shared axis, direct labels at the line ends."""
    width, height = 860, 420
    left, right, top, bottom = 70, 210, 64, 56
    t_max = max([horizon_h] + [max(s["t_h"]) for s in series])
    ph_all = [p for s in series for p in s["ph"]]
    p_lo = math.floor(min(ph_all + [threshold]) * 2) / 2 - 0.5
    p_hi = math.ceil(max(ph_all) * 2) / 2 + 0.25

    def x(t: float) -> float:
        return left + t / t_max * (width - left - right)

    def y(p: float) -> float:
        return top + (p_hi - p) / (p_hi - p_lo) * (height - top - bottom)

    body = [
        f'<text x="16" y="28" font-size="16" fill="{_INK}" font-weight="600">{escape(title)}</text>',
        f'<text x="16" y="48" font-size="12" fill="{_INK2}">{escape(note)}</text>',
    ]
    p = math.ceil(p_lo)
    while p <= p_hi:
        body.append(
            f'<line x1="{left}" y1="{y(p):.1f}" x2="{width - right}" y2="{y(p):.1f}" stroke="{_GRID}"/>'
        )
        body.append(
            f'<text x="{left - 8}" y="{y(p) + 4:.1f}" font-size="11" fill="{_INK2}" text-anchor="end">{p:g}</text>'
        )
        p += 0.5
    ticks = 5
    for k in range(ticks + 1):
        t = t_max * k / ticks
        body.append(
            f'<text x="{x(t):.1f}" y="{height - bottom + 18}" font-size="11" fill="{_INK2}" '
            f'text-anchor="middle">{t:,.0f}</text>'
        )
    body.append(
        f'<text x="{(left + width - right) / 2:.1f}" y="{height - 16}" font-size="12" fill="{_INK2}" '
        'text-anchor="middle">time on stream, h</text>'
    )
    body.append(
        f'<text x="18" y="{(top + height - bottom) / 2:.1f}" font-size="12" fill="{_INK2}" '
        f'text-anchor="middle" transform="rotate(-90 18 {(top + height - bottom) / 2:.1f})">'
        "anolyte pH (concentration basis)</text>"
    )
    body.append(
        f'<line x1="{left}" y1="{y(threshold):.1f}" x2="{width - right}" y2="{y(threshold):.1f}" '
        f'stroke="{_MUTED}" stroke-dasharray="4 4"/>'
    )
    body.append(
        f'<text x="{width - right + 6}" y="{y(threshold) + 4:.1f}" font-size="11" fill="{_INK2}">'
        f"threshold pH {threshold:g}</text>"
    )
    body.append(
        f'<line x1="{x(horizon_h):.1f}" y1="{top}" x2="{x(horizon_h):.1f}" y2="{height - bottom}" '
        f'stroke="{_MUTED}" stroke-dasharray="2 4"/>'
    )
    body.append(
        f'<text x="{x(horizon_h) - 4:.1f}" y="{top + 12}" font-size="11" fill="{_INK2}" '
        f'text-anchor="end">campaign {horizon_h:,.0f} h</text>'
    )
    label_y = [y(threshold)]
    for i, s in enumerate(series):
        colour = _SERIES[i % len(_SERIES)]
        pts = " ".join(f"{x(t):.1f},{y(v):.1f}" for t, v in zip(s["t_h"], s["ph"], strict=True))
        body.append(
            f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="2" '
            f'stroke-linejoin="round"><title>{escape(s["label"])}</title></polyline>'
        )
        ly = y(s["ph"][-1])
        while any(abs(ly - o) < 14 for o in label_y):
            ly += 14
        label_y.append(ly)
        body.append(
            f'<text x="{width - right + 6}" y="{ly + 4:.1f}" font-size="11" fill="{_INK}">'
            f'<tspan fill="{colour}">&#9644;</tspan> {escape(s["label"])}</text>'
        )
    return _svg(width, height, body, title, note)
