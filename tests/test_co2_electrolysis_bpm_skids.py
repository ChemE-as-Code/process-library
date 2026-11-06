"""The CO2 pilot skids of process-library#330 against their frozen hand expectations.

processes/co2-electrolysis-bpm-1/scripts/regen.py regenerates both skids for one campaign
duration; results/expected.yaml holds the hand values E1 to E9 (tests/skid_formulas.py, frozen in
their own commit before the first regeneration, ADR 0030). Three kinds of test:

- fast, without core: the design basis is what the stacks and duties carry, no script reads the
  library's held-out benchmarks (ADR 0032), the frozen-expectations commit precedes every
  regeneration commit, and the committed calculation records (results/scenarios/<H>h/record.json)
  and the resize report meet E1 to E9;
- slow, with core, marked ``engineering`` (its own CI job, ADR 0033): the folder copied to a temporary directory and regenerated at 1000 h and at
  10000 h (``cheme run scripts/regen.py --duration H``), its records asserted against E1 to E9 and
  the layout and datasheets against E8 after each run. Skipped without cheme-as-code; CI sets
  ATLAS_REQUIRE_CORE, so a missing core fails there.

E10 (#331) is the LCI of both skids (results/scenarios/<H>h/lca.json, regen step 20): its
datasets reconciled with the duty totals of the calculation record, the K and C balances, the
duty run traced, and the hand values frozen in results/expected-lca.yaml (tests/lca_formulas.py)
before the LCA was first computed; fast on the committed files, slow on a regeneration.

The 3D model (DESIGN.md D-040 to D-046): E8 holds at both durations for T-101, T-201, T-202 and
the eight stacks; the record's layout block (regen step 25) has, at 1,000 h, every process line
of DN 25 and above routed or skipped with a reason, no clash, both skids inside the envelope
height and every permitted lift with a clear lane and a laydown, and at 10,000 h the infeasible
Skid A's clash, height and lifts reported; fast on the committed records, slow on a
regeneration, which also runs core's gates layout-3d (without the review-record drawings),
lifting-study, mto and electrical and compares the model, take-off, lifting studies and cable
schedule with the committed bytes.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import lca_formulas as lf
import pytest
import skid_formulas as f
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "co2-electrolysis-bpm-1"
REL = "processes/co2-electrolysis-bpm-1"
DURATIONS = (1000, 10000)
ASSUMED = "held constant by assumption, not supported by measurement"
MM = 1.0e-3 + 1e-9
SENTENCE_A = "Skid A cannot meet the 10,000 h duty within the skid envelope"
#: the files the frozen-expectations commit may touch (and nothing the regeneration writes)
FROZEN_FILES = {f"{REL}/results/expected.yaml", "tests/skid_formulas.py", "tests/test_skid_formulas.py"}
#: files of the skids that the regeneration writes (and that did not exist before #330): every
#: commit touching them comes after the frozen one
REGEN_OUTPUTS = (
    f"{REL}/process/duties.yaml", f"{REL}/process/BFD.xml", f"{REL}/process/PFD.xml",
    f"{REL}/results/scenarios", f"{REL}/results/resize-1000h-10000h.json", f"{REL}/figures/skids",
)  # fmt: skip
#: #331: the files the LCI hand-expectations commit may touch, and the LCA outputs that come
#: after it (E10)
LCA_FROZEN_FILES = {f"{REL}/results/expected-lca.yaml", "tests/lca_formulas.py", "tests/test_lca_formulas.py"}
LCA_OUTPUTS = (
    f"{REL}/lca/dataset.yaml", f"{REL}/lca/datasets", f"{REL}/lca/scenarios", f"{REL}/lca/results.csv",
    f"{REL}/results/scenarios/1000h/lca.json", f"{REL}/results/scenarios/10000h/lca.json",
)  # fmt: skip
#: what core's --balance may not assess (the replaced parts have no composition; Skid A's zero
#: dose and bleed)
UNASSESSED = {
    "consumable:anode-ni-foam", "consumable:cathode-gde-ag", "consumable:cathode-gdl-carbon", "consumable:membrane-bpm",
    "disposal:consumable.anode-ni-foam", "disposal:consumable.cathode-gde-ag", "disposal:consumable.cathode-gdl-carbon",
    "disposal:consumable.membrane-bpm",
    "feed:KOH-DOSE", "product:BLEED",
}  # fmt: skip

try:
    import chemeascode  # noqa: F401
except ImportError:
    if os.environ.get("ATLAS_REQUIRE_CORE"):
        raise
    chemeascode = None
needs_core = pytest.mark.skipif(chemeascode is None, reason="needs cheme-as-code (core) to regenerate the skids")
#: the regeneration takes minutes: its own CI job (ADR 0033)
engineering = pytest.mark.engineering


def _yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def expected() -> dict:
    return f.load_expected()


@pytest.fixture(scope="module")
def items(expected) -> dict[str, dict]:
    return {i["key"]: i for block in expected["expectations"].values() for i in block.get("items") or []}


@pytest.fixture(scope="module")
def hand() -> dict:
    return f.hand_values()


def close(value, item: dict, where: str) -> None:
    """*value* against a frozen item with its tolerance."""
    want, tol = item["value"], item["tolerance"]
    if isinstance(want, bool) or tol == "exact":
        assert value == want, f"{where}: {value!r} != {want!r}"
        return
    if "rel" in tol:
        assert abs(value - want) <= tol["rel"] * abs(want), f"{where}: {value} vs {want} (rel {tol['rel']})"
    else:
        assert abs(value - want) <= tol["abs"], f"{where}: {value} vs {want} (abs {tol['abs']})"
    if tol.get("direction") == "above 1":
        assert value > 1, f"{where}: {value} is not above 1"


def rel(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol * max(abs(a), abs(b))


# -- E1 to E9 on a pair of records ------------------------------------------------------------


def assert_e1_to_e7(records: dict[int, dict], items: dict, hand: dict) -> None:
    for h, rec in records.items():
        for skid in ("A", "B"):
            s = rec["skids"][skid]
            at = f"E1 Skid {skid} {h} h"
            close(s["cells"], items["E1.cells_required"], at)
            close(s["stacks"], items["E1.stacks"], at)
            close(s["cells_per_stack"], items["E1.cells_per_stack"], at)
            for key in ("stack_voltage_v", "bus_current_a", "dc_power_kw", "ac_power_kw", "co_formed_kg_h",
                        "co_delivered_kg_h", "margin", "kwh_per_kg_formed", "kwh_per_kg_delivered",
                        "stack_heat_kw", "recirculation_kg_h"):  # fmt: skip
                close(s[key], items[f"E1.{key}"], f"{at} {key}")
            for dim in ("length", "width", "height"):
                close(s["stack_envelope_m"][dim], items[f"E1.envelope_m.{dim}"], f"{at} stack {dim}")
            assert s["cooler_kw"] >= s["stack_heat_kw"] * (1 - 1e-9), f"{at}: the cooler removes the stack heat"

    # E2: Skid A scales with the duration
    a = {h: rec["skids"]["A"] for h, rec in records.items()}
    for h, s in a.items():
        at = f"E2 {h} h"
        close(s["reservoir_volume_exact_l"], items[f"E2.{h}.volume_exact_l"], at)
        close(s["reservoir_volume_l"], items[f"E2.{h}.volume_written_l"], at)
        close(s["reservoir_held_m3"], items[f"E2.{h}.tank.held_m3"], at)
        close(s["reservoir_diameter_m"], items[f"E2.{h}.tank.diameter"], at)
        close(s["reservoir_height_m"], items[f"E2.{h}.tank.height"], at)
        close(s["final_carbon_mol_l"], items[f"E2.{h}.final.carbon"], at)
        close(s["final_cation_mol_l"], items[f"E2.{h}.final.cation"], at)
        assert s["dosed_solution_l"] == s["bleed_l"] == s["makeup_water_l"] == 0.0, at
        assert s["duty_feasible"] and s["reservoir_limited_by"] == "the pH threshold 12", at
        fits_height = not any("above the envelope" in r for r in s["reasons"])
        close(fits_height, items[f"E2.{h}.fits_height"], at)
        if h == 10000:
            fits_plan = not any("outside the frame in plan" in r or "is not inside structure" in r for r in s["reasons"])
            close(fits_plan, items["E2.10000.fits_plan"], at)
        # the longest campaign whose reservoir fits the envelope height, at this run's rate
        per_h = s["reservoir_volume_exact_l"] / h
        close(hand["E2"]["max_volume_in_envelope_l"] / per_h, items["E2.max_duration_in_envelope_h"], at)
    close(a[10000]["reservoir_volume_l"] / a[1000]["reservoir_volume_l"], items["E2.volume_ratio"], "E2 ratio")
    close(a[10000]["reservoir_diameter_m"] / a[1000]["reservoir_diameter_m"], items["E2.diameter_ratio"], "E2 D ratio")

    # E3: Skid B is steady
    b = {h: rec["skids"]["B"] for h, rec in records.items()}
    for h, s in b.items():
        at = f"E3 {h} h"
        for key, item in (("bleed_l_h", "bleed_l_h"), ("final_cation_mol_l", "cation_mol_l"), ("final_ph", "ph"),
                          ("dose_mol_h", "dose_mol_h"), ("dose_l_h", "dose_solution_l_h"),
                          ("makeup_l_h", "makeup_water_l_h"), ("residence_h", "residence_h"),
                          ("final_ionic_strength_mol_l", "ionic_strength_mol_l"),
                          ("dosing_pump_kg_h", "dosing_pump_kg_h"), ("dosing_tank_held_l", "dosing_tank_held_l"),
                          ("dosing_tank_diameter_m", "dosing_tank.diameter"),
                          ("dosing_tank_height_m", "dosing_tank.height")):  # fmt: skip
            close(s[key], items[f"E3.{item}"], f"{at} {key}")
        close(s["dosing_tank_fills"], items[f"E3.refills.{h}"], at)
        close(s["dosed_solution_l"], items[f"E3.totals.{h}.dosed_solution_l"], at)
        close(s["bleed_l"], items[f"E3.totals.{h}.bleed_l"], at)
        close(s["makeup_water_l"], items[f"E3.totals.{h}.makeup_water_l"], at)
        # the species at H at the algebraic steady state; the volume held
        assert abs(s["final_hydroxide_mol_l"] - 0.5) <= 1e-3 and abs(s["final_carbon_mol_l"] - 0.25) <= 1e-3, at
        assert abs(s["final_volume_l"] - 50.0) <= 0.5, at
        # refill_interval (core A1): the day tank is not sized on the campaign
        assert s["dosing_tank_held_l"] < hand["E3"]["dosing_tank_without_interval_l"][1000], at
    for key in ("reservoir_volume_l", "reservoir_diameter_m", "reservoir_height_m", "dosing_pump_kg_h",
                "dosing_tank_diameter_m", "dosing_tank_height_m", "dosing_tank_held_l", "bleed_l_h", "dose_l_h"):  # fmt: skip
        assert b[1000][key] == b[10000][key], f"E3 {key} changes with the duration"
    for key in ("dosed_solution_l", "bleed_l", "makeup_water_l"):
        assert rel(b[10000][key], 10 * b[1000][key], 1e-3), f"E3 {key} x 10"

    # E4: KOH per kg CO delivered
    floor = items["E4.floor_per_kg_delivered"]["value"]
    for h in DURATIONS:
        close(a[h]["koh_per_kg_delivered"], items[f"E4.skid_a.{h}"], f"E4 A {h} h")
        close(b[h]["koh_dosed_per_kg_delivered"], items["E4.skid_b_makeup"], f"E4 B {h} h")
        close(b[h]["koh_fill_per_kg_delivered"], items[f"E4.skid_b_fill_share.{h}"], f"E4 B fill {h} h")
        close(a[h]["koh_fill_kg"] / a[h]["totals_product_kg"], items["E4.skid_a_per_kg_formed_exact"], f"E4 A formed {h} h")
        assert a[h]["koh_per_kg_delivered"] >= floor and b[h]["koh_per_kg_delivered"] >= floor, f"E4 floor {h} h"
        assert b[h]["koh_dosed_per_kg_delivered"] > a[h]["koh_per_kg_delivered"], "E4: dosing does not save KOH"
    assert rel(a[1000]["koh_per_kg_delivered"], a[10000]["koh_per_kg_delivered"], 1e-3)

    for h, rec in records.items():
        comp = rec["comparisons"]["results"]
        # E5: on/off at equal CO formed
        half = comp["equal-co-half"]
        close(half["target_kg"], items[f"E5.{h}.co_target_kg"], f"E5 {h} h")
        da, onoff, part = (half["rows"][d] for d in ("D-A", "D-A-ONOFF", "D-A-PART"))
        assert da["reached"] and onoff["reached"] and part["reached"], f"E5 {h} h"
        close(onoff["elapsed_h"], items[f"E5.{h}.elapsed_h"], f"E5 {h} h elapsed")
        for key in ("charge_c", "energy_kwh", "hydroxide_deficit_mol"):
            assert rel(onoff[key], da[key], 1e-3), f"E5 {h} h {key}"
        assert abs(onoff["final_ph"] - da["final_ph"]) <= 1e-3, f"E5 {h} h pH"
        # E6: part load at equal CO formed
        close(part["charge_c"] / da["charge_c"], items["E6.charge_ratio"], f"E6 {h} h charge")
        close(part["hydroxide_deficit_mol"] / da["hydroxide_deficit_mol"], items["E6.deficit_ratio"], f"E6 {h} h deficit")
        close(part["energy_kwh"] / da["energy_kwh"], items["E6.energy_ratio"], f"E6 {h} h energy")
        close(rec["skids"]["A"]["kwh_per_kg_formed"], items["E6.kwh_per_kg_p200"], f"E6 {h} h")
        full = comp["part-load-full"]
        assert full["rows"]["D-A"]["reached"] and not full["rows"]["D-A-PART"]["reached"], f"E6 {h} h"
        assert full["rows"]["D-A-PART"]["ended"] == "threshold"
        assert "cheme.duty-target-not-reached" in full["rules"], f"E6 {h} h"
        # E7: D-A against D-B at equal CO
        ab = comp["skid-a-vs-b-half"]["rows"]
        for key in ("charge_c", "energy_kwh"):
            assert rel(ab["D-A"][key], ab["D-B"][key], 1e-3), f"E7 {h} h {key}"
        assert ab["D-A"]["dosing_hydroxide_kg"] == 0.0 < ab["D-B"]["dosing_hydroxide_kg"], f"E7 {h} h"
        want = rec["skids"]["B"]["dose_mol_h"] * f.M_KOH * 1e-3 * ab["D-B"]["elapsed_h"]
        assert rel(ab["D-B"]["dosing_hydroxide_kg"], want, 1e-3), f"E7 {h} h dosed KOH"


def assert_e9(records: dict[int, dict], items: dict) -> None:
    for h, rec in records.items():
        close(rec["measured_state"]["carbon_max_mol_l"], items["measured_state.carbon_mol_l"], f"E9 {h} h")
        close(rec["measured_state"]["time_on_stream_h"], items["measured_state.time_on_stream_h"], f"E9 {h} h")
        for skid in ("A", "B"):
            inv = rec["skids"][skid]["invariants"]
            assert {"electrolyte", "time_on_stream"} <= set(inv["failed"]), f"E9 {skid} {h} h"
            assert inv["fe_wde_u_kwh_per_kg"] == ASSUMED, f"E9 {skid} {h} h"
            assert inv["conditions"]["current_density"]["holds"], f"E9 {skid} {h} h: 200 mA/cm2 is measured"
    a10 = records[10000]["skids"]["A"]
    assert a10["feasible"] is False and a10["envelope_feasible"] is False
    assert any("T-101" in r and "above the envelope" in r for r in a10["reasons"]), a10["reasons"]
    assert SENTENCE_A in a10["sentences"]
    assert records[1000]["skids"]["A"]["feasible"] is True
    assert all(records[h]["skids"]["B"]["feasible"] for h in DURATIONS)


def assert_e8(root: Path, record: dict) -> None:
    """The layout and the datasheets carry the sizes `cheme process stack --write` wrote: the
    plant-model geometry of T-101, T-201, T-202 and every stack is the calculated one."""
    listed = {e["tag"]: e for e in _yaml(root / "equipment" / "equipment-list.yaml")["equipment"]}
    model = {e["tag"]: e for e in _yaml(root / "layout" / "plant-model.yaml")["equipment"]}
    stacks = {t for t in listed if t[:5] in ("E-101", "E-201")}  # E-101A to D, E-201A to D
    checked = set()
    for skid, s in record["skids"].items():
        for e in s["equipment"]:
            if e["role"] not in ("stack", "reservoir", "dosing_tank"):
                continue
            tag, dims = e["tag"], e["values"]
            checked.add(tag)
            at = f"E8 {tag} at {record['duration_h']:g} h"
            ld = listed[tag]["dimensions"]
            for k, v in dims.items():
                assert ld[k] == v, f"{at}: list {k} {ld[k]} != stack {v}"
                assert model[tag]["dimensions"][k] == ld[k], f"{at}: model {k}"
            # the model writes its bounding boxes to the mm: an extent is the size within 1 mm
            x0, y0, z0, x1, y1, z1 = model[tag]["bbox"]
            ds = _yaml(root / "equipment" / "datasheets" / f"{tag}.yaml")["dimensions"]
            if e["role"] == "stack":
                plan = sorted([x1 - x0, y1 - y0])
                for got, want in zip(plan, sorted([dims["length"], dims["width"]]), strict=True):
                    assert math.isclose(got, want, abs_tol=MM), at
                assert math.isclose(z1 - z0, dims["height"], abs_tol=MM), at
                assert (ds["overall_length"]["value"], ds["overall_width"]["value"], ds["overall_height"]["value"]) == (
                    dims["length"], dims["width"], dims["height"]), at  # fmt: skip
            else:
                for extent in (x1 - x0, y1 - y0):
                    assert math.isclose(extent, dims["diameter"], abs_tol=MM), at
                assert math.isclose(z1 - z0, dims["height"], abs_tol=MM), at
                assert ds["outside_diameter"]["value"] == dims["diameter"], at
                assert ds["overall_height"]["value"] == dims["height"], at
                # the duty-sized tanks carry the duty run's fingerprint
                assert e["fingerprint"] == s["run_fingerprint"] == listed[tag]["dimensions"]["fingerprint"], at
    want = {"T-101", "T-201", "T-202"} | stacks
    assert len(stacks) == 8 and want <= checked, f"E8 at {record['duration_h']:g} h: not checked {sorted(want - checked)}"


# -- the 3D model: routed lines, clashes, heights, lifts (regen step 25, DESIGN.md D-046) -------

#: the gates of the 3D model that must pass at the design duration (checks/checks.yaml); the
#: drawings requirement of layout-3d rests on the layout review record (gate layout-review)
MODEL_GATES = ("layout-3d", "lifting-study", "mto", "electrical")
#: what regen writes from the model and --check compares at the design duration
MODEL_OUTPUTS = (
    "layout/plant-model.yaml", "estimate/mto.csv", "estimate/mto.md", "layout/lifting-study.csv",
    "layout/lifting-study.md", "layout/lifting-study-units.csv", "layout/lifting-study-units.md",
    "electrical/cable-schedule.csv", "electrical/cable-schedule.md",
)  # fmt: skip


def _dn25_lines(root: Path) -> set[str]:
    lines = _yaml(root / "piping" / "line-list.yaml")["lines"]
    return {ln["number"] for ln in lines if int(str(ln["nominal_diameter"]).upper().removeprefix("DN")) >= 25}


def assert_layout(root: Path, records: dict[int, dict]) -> None:
    """At 1,000 h every process line of DN 25 and above routed or skipped with a reason, no
    route fallen back to direct, no clash finding (accepted or not), both skids inside the
    envelope height and every permitted unit lift with a clear crane lane or a hoist carry
    within the carry limit, and a laydown; the stacks within reach and free to slide out, the
    ignition sources clear of the zones, no tray at a vent outlet (D-047); at 10,000 h the
    infeasible Skid A's clash, height and lifts reported in the record, not failed."""
    big = _dn25_lines(root)
    for h, rec in records.items():
        lay = rec["layout"]
        assert lay["routed_dn_min"] == 25, h
        lines = lay["lines"]
        assert lines["listed"] == len(big), f"{h} h: {lines['listed']} lines of DN 25+, the list has {len(big)}"
        assert set(lines["routed"]) | set(lines["skipped"]) | set(lines["unrouted"]) == big, h
        assert all(lines["skipped"][k] for k in lines["skipped"]), f"{h} h: a skip without a reason"
        assert {u["id"] for u in rec["lifting"]["unit_lifts"]} >= {"SKID-A", "SKID-B", "T-101", "T-101-full"}, h
    d = records[1000]["layout"]
    assert d["lines"]["unrouted"] == {} and sorted(d["lines"]["routed"]) == sorted(big), d["lines"]
    assert not d["methods"].get("direct"), d["methods"]
    assert d["clashes"] == [] and d["clashes_open"] == 0, d["clashes"]
    for key in ("A", "B"):
        hgt = d["height"][key]
        assert hgt["envelope_feasible"] and hgt["above_envelope_m"] == 0.0, (key, hgt)
        assert hgt["items_top_m"] <= hgt["envelope_top_m"], (key, hgt)
    # a crane lift's lane is clear; a hoist or forklift carry stays at or under the basis's
    # carry limit (above it scripts/_lifting.py marks the lane blocked); every lift a laydown
    limit = records[1000]["lifting"]["carry_limit_m"]
    assert limit, records[1000]["lifting"]
    for lift in records[1000]["lifting"]["unit_lifts"]:
        if "not permitted" not in lift["status"]:
            if lift["method"].startswith("mobile crane"):
                assert lift["lane"] == "clear", lift
            else:
                assert lift["carry_height_m"] and float(lift["carry_height_m"]) <= float(limit), lift
            assert lift["laydown"] and "blocked" not in lift["status"] and "no " not in lift["status"], lift
    # the layout review fixes (D-047): every stack within reach of a person at grade at the
    # frame's south side and its slide lane clear, every ignition source the zone radius plus the
    # margin from every zone source's outline, no cable tray within the clearance of a vent or
    # flue outlet; T-101 leaves by crane to the road
    assert d["vent_tray_clearance"] == [], d["vent_tray_clearance"]
    for key in ("A", "B"):
        skid = records[1000]["skids"][key]
        assert len(skid["stack_removal"]) == 4, skid["stack_removal"]
        for r in skid["stack_removal"]:
            assert r["reach_ok"] and r["reach_m"] <= r["reach_limit_m"] and not r["lane_blocked_by"], r
        assert {g["tag"][0] for g in skid["ignition_clearance"]} == {"U", "X"}, skid["ignition_clearance"]
        assert all(g["ok"] for g in skid["ignition_clearance"]), skid["ignition_clearance"]
    lifts = {u["id"]: u for u in records[1000]["lifting"]["unit_lifts"]}
    assert lifts["T-101"]["method"].startswith("mobile crane") and lifts["T-101"]["laydown"] == "LD-R", lifts["T-101"]
    # 10,000 h: reported in the record, the run not failed (its record exists)
    t = records[10000]["layout"]
    assert t["height"]["A"]["above_envelope_m"] > 1.0 and not t["height"]["A"]["envelope_feasible"], t["height"]
    assert t["height"]["B"]["envelope_feasible"], t["height"]["B"]
    assert any(c["level"] == "error" and "T-101" in c["message"] for c in t["clashes"]), t["clashes"]
    assert t["clashes_open"] >= 1
    skid_a = {u["id"]: u for u in records[10000]["lifting"]["unit_lifts"]}["SKID-A"]
    assert "no laydown" in skid_a["status"], skid_a
    # the grown T-101 drained (about 1 t with its heel) is a crane lift to the road, reported
    t101 = {u["id"]: u for u in records[10000]["lifting"]["unit_lifts"]}["T-101"]
    assert t101["method"].startswith("mobile crane") and float(t101["weight_t"]) > 1.0, t101


def _lca_items() -> dict[str, dict]:
    return {i["key"]: i for i in lf.load_expected()["expectations"]["E10"]["items"]}


def _lca_close(value: float, items: dict, key: str, where: str) -> None:
    item = items[key]
    assert lf.close(value, item["value"], item["tolerance"]), f"E10 {where} {key}: {value} vs {item['value']} {item['tolerance']}"


#: the auxiliary power streams of each skid (the pumps, compressors, PSA; Skid B's dosing pump)
AUX = {"A": ("Q102", "Q103", "Q104"), "B": ("Q202", "Q203", "Q204", "Q206")}
#: the band of an anolyte's mass over its volume, kg/L (scripts/_lca.py DENSITY_BAND_KG_L)
DENSITY_BAND = (0.997, 1.35)


def _duty_side(root: Path, rec: dict, skid: str) -> dict[str, float]:
    """E10's duty side per kg CO, recomputed here from the calculation record's duty totals (and
    the inputs regen reads): what the dataset must equal, by the reconciliation's quantity. The
    auxiliary power comes from the flowsheet the dataset is built from, so only the frozen
    electricity values of results/expected-lca.yaml check it independently."""
    stack = {"A": "STK-A", "B": "STK-B"}[skid]
    cfg = {s["id"]: s for s in _yaml(root / "process" / "cells.yaml")["stacks"]}[stack]
    flowsheet = {s["id"]: s for s in _yaml(root / "process" / "flowsheet.yaml")["streams"]}
    m_koh = next(float(c["molar_mass"]) for c in _yaml(root / "process" / "materials.yaml")["components"] if c["id"] == "KOH")
    s = rec["skids"][skid]
    t = rec["duties"][s["duty"]]["totals"]
    delivered = float(s["totals_delivered_kg"])
    hours = float(s["duty_result"]["operating_time_h"])
    eta = float(cfg["electrical"]["rectifier_efficiency"]["value"])
    aux_kw = sum(float(flowsheet[q]["state"][s["case"]]["duty"]["value"]) for q in AUX[skid])
    rho_fill = float(cfg["equipment"]["recirculation_pump"]["density"]["value"]) / 1000.0
    out_l = t["final_volume_l"] + t["bleed_l"]
    want = {
        "electricity: DC / rectifier efficiency + auxiliaries": (t["energy_kwh"] / eta + aux_kw * hours) / delivered,
        "KOH fill (KOH 100 %)": t["initial_cation_mol"] * m_koh / 1000.0 / delivered,
        "fill solution (initial volume x anolyte density)": t["initial_volume_l"] * rho_fill / delivered,
        "KOH dosed (KOH 100 %)": t["dosing_hydroxide_kg"] / delivered,
        "dosing solution": (t["dosing_solution_kg"] or 0.0) / delivered,
        "bleed K": t["bleed_cation_mol"] / delivered,
        "bleed C": t["bleed_carbon_mol"] / delivered,
        "final inventory K": t["final_cation_mol"] / delivered,
        "final inventory C": t["final_carbon_mol"] / delivered,
        "condensate K (the K+ through the membrane)": t["membrane_cation_mol"] / delivered,
        "spent inventory's share of the anolyte water out (final volume over final volume + bleed)": t["final_volume_l"] / out_l if out_l else 0.0,
        "CO delivered": delivered,
    }  # fmt: skip
    if skid == "B":
        want["make-up water (Skid B's water less Skid A's)"] = t["makeup_water_l"] * 0.997 / delivered
    return want


def assert_e10(root: Path, records: dict[int, dict], docs: dict[int, dict]) -> None:
    """E10 (#331): the LCI of both skids per kg CO, reconciled with the duty totals of the
    scenario's calculation record, its K and C balances closed, the run that sized the
    equipment traced, and the frozen hand values of results/expected-lca.yaml met."""
    items = _lca_items()
    cells_cfg = {s["id"]: s for s in _yaml(root / "process" / "cells.yaml")["stacks"]}
    listed = {e["tag"]: e for e in _yaml(root / "equipment" / "equipment-list.yaml")["equipment"]}
    for h, doc in docs.items():
        rec = records[h]
        assert doc["duration_h"] == h and doc["schema"] == "process-library/skid-lca/1"
        assert doc["manifest_fingerprints_flowsheet"], f"E10 {h} h: lca/manifest.json does not fingerprint the flowsheet"
        assert doc["label"] == "partial screening carbon footprint", doc["label"]
        _lca_close(doc["kg_per_unit"], items, "functional_unit.kg_product_per_kg_co", f"{h} h")
        # the replaced parts: the cells times the cell area, at the stacks' interval
        p = doc["parts"]
        for skid, stack in (("A", "STK-A"), ("B", "STK-B")):
            s = rec["skids"][skid]
            stack_tags = [t for t in listed if t.startswith(f"E-{1 if skid == 'A' else 2}01")]
            assert p["cells"] == s["cells"] == len(stack_tags) * s["cells_per_stack"], f"E10 {h} h {skid} cells"
            assert p["interval_h"] == cells_cfg[stack]["replacement"]["interval"]["value"], f"E10 {h} h {skid} interval"
        assert math.isclose(p["replaced_m2"], p["cells"] * p["cell_area_m2"], rel_tol=1e-12)
        _lca_close(p["replaced_m2"], items, "parts.area_m2", f"{h} h")
        for skid in ("A", "B"):
            s = doc["skids"][skid]
            at = f"{h} h Skid {skid}"
            # the reconciliation with the duty totals (rel 1e-6): its duty side recomputed here from
            # the calculation record, not taken from lca.json
            want = _duty_side(root, rec, skid)
            assert {r["quantity"] for r in s["reconciliation"]} == set(want), f"E10 {at}: {[r['quantity'] for r in s['reconciliation']]}"
            for r in s["reconciliation"]:
                duty = want[r["quantity"]]
                assert rel(r["duty"], duty, 1e-9) or r["duty"] == duty == 0.0, f"E10 {at}: stored duty {r} against {duty}"
                assert rel(r["lca"], duty, 1e-6) or r["lca"] == duty == 0.0, f"E10 {at}: {r} against {duty}"
            # the masses the balance writes over the duty's volumes: a plausible anolyte density
            t = rec["duties"][rec["skids"][skid]["duty"]]["totals"]
            delivered = float(rec["skids"][skid]["totals_delivered_kg"])
            for key, litres in (("product:SPENT", t["final_volume_l"]), ("product:BLEED", t["bleed_l"])):
                if litres:
                    kg_l = s["exchanges"][key]["amount"] * delivered / litres
                    assert DENSITY_BAND[0] <= kg_l <= DENSITY_BAND[1], f"E10 {at}: {key} {kg_l} kg/L"
            assert s["densities_plausible"] and len(s["densities"]) == (2 if t["bleed_l"] else 1), f"E10 {at}: {s['densities']}"
            assert s["reconciled"] and s["lca_cases_agree"], at
            assert all(r["rel"] <= 1e-5 or r["dataset"] == r["lca_cases"] == 0.0 for r in s["lca_cases"]), at
            # K and C close by route (the dataset's compositions) and in core's --balance
            b = s["balance"]
            assert rel(b["k_in_mol"], b["k_out_mol"], 1e-6) and rel(b["c_fed_mol"], sum(b["c_routes_mol"].values()), 1e-6), at
            cb = s["core_balance"]
            assert cb["k_closed"] and cb["c_closed"] and cb["carbon_by_origin_closed"] and cb["mass_closed"], f"E10 {at}: {cb}"
            assert set(cb["no_composition"]) <= UNASSESSED, f"E10 {at}: {cb['no_composition']}"
            # the run that sized the equipment
            assert s["run_fingerprint"] == rec["skids"][skid]["run_fingerprint"], at
            assert s["tanks_carry_run"] and s["sources_uncited"] == [], f"E10 {at}: {s['tank_fingerprints']} {s['sources_uncited']}"
            # the frozen hand values
            ex = s["exchanges"]
            _lca_close(ex["feed:POWER"]["amount"], items, f"electricity.skid_{skid.lower()}_kwh_per_kg", at)
            _lca_close(ex["feed:CO2"]["amount"], items, "co2.fresh_kg_per_kg", at)
            _lca_close(ex["emission:CO2"]["amount"], items, "co2.vented_kg_per_kg", at)
            for route, share in b["c_shares"].items():
                _lca_close(share, items, f"co2.carbon_share.{route}", at)
            for key, field, item in (
                ("feed:KOH-FILL", "KOH", "koh_fill_kg_per_kg"), ("feed:KOH-DOSE", "KOH", "koh_dose_kg_per_kg"),
            ):  # fmt: skip
                if f"routes.{h}.{skid}.{item}" in items:
                    _lca_close(ex[key]["components_kg"].get(field, 0.0) if ex[key].get("components_kg") else 0.0,
                               items, f"routes.{h}.{skid}.{item}", at)  # fmt: skip
            for key, field, item in (
                ("feed:KOH-FILL", "k_mol", "fill_k"), ("product:CONDENSATE", "k_mol", "condensate_k"),
                ("product:SPENT", "k_mol", "spent_k"), ("product:SPENT", "c_mol", "spent_c"),
                ("product:BLEED", "k_mol", "bleed_k"), ("product:BLEED", "c_mol", "bleed_c"),
            ):  # fmt: skip
                if f"routes.{h}.{skid}.{item}" in items:
                    _lca_close(ex[key].get(field, 0.0), items, f"routes.{h}.{skid}.{item}", at)
            _lca_close(s["h2_tail_kg_per_kg"], items, "h2_coproduct.h2_kg_per_kg_co", at)
            life = int(p["interval_h"])
            _lca_close(ex["consumable:membrane-bpm"]["amount"] * 1e3, items, f"parts.{life}.membrane_g_per_kg", at)
            _lca_close(ex["consumable:cathode-gde-ag"]["amount"] * 1e3, items, f"parts.{life}.ag_g_per_kg", at)
            _lca_close(ex["consumable:anode-ni-foam"]["amount"] * 1e3, items, f"parts.{life}.ni_g_per_kg", at)
            # the gaps are listed with their quantities, never zero-filled (ADR 0029)
            gaps = s["impacts"]["gaps"]
            for key in ("feed:CO2", "feed:KOH-FILL", "product:SPENT", "product:CONDENSATE", "product:CW", "consumable:membrane-bpm", "consumable:cathode-gdl-carbon"):
                assert key in gaps and key not in s["impacts"]["contributions"], f"E10 {at}: {key}"
        _lca_close(doc["skids"]["A"]["impacts"]["contributions"]["feed:POWER"]["value"], items, "electricity.skid_a_kg_co2e_per_kg_nl", f"{h} h")
        # the electricity mixes come from one profile: the electricity pair differs in no dimension
        for sid, sc in doc["scenarios"].items():
            for pair in sc["compared"]:
                if pair["baseline"].startswith("ember-2025:") and pair["scenario"].startswith("ember-2025:"):
                    assert pair["differences"] == [], (sid, pair)
        assert doc["scenarios"]["desnz-gb"]["verdict"] == "not comparable"


def _committed_lca() -> dict[int, dict]:
    return {h: json.loads((PROCESS / "results" / "scenarios" / f"{h}h" / "lca.json").read_text()) for h in DURATIONS}


def _committed_records() -> dict[int, dict]:
    return {h: json.loads((PROCESS / "results" / "scenarios" / f"{h}h" / "record.json").read_text()) for h in DURATIONS}


# -- fast -------------------------------------------------------------------------------------


def test_design_basis_is_what_the_stacks_and_duties_carry():
    basis = _yaml(PROCESS / "process" / "design-basis.yaml")["capacity"]["pilot_skid"]
    cells = _yaml(PROCESS / "process" / "cells.yaml")
    duties = {d["id"]: d for d in _yaml(PROCESS / "process" / "duties.yaml")["duties"]}
    for stack in cells["stacks"]:
        for key in ("rate", "recovery", "purity", "pressure"):
            assert stack["product"][key]["value"] == basis["product"][key]["value"], f"{stack['id']} {key}"
        assert stack["product"]["component"] == basis["product"]["component"]
        hours = stack["replacement"]["operating_hours"]
        assert (hours["value"], hours["unit"]) == (basis["operating_hours"]["value"], basis["operating_hours"]["unit"])
    design = basis["duration"]["design"]["value"]
    assert design in basis["duration"]["scenarios"]
    for did in ("D-A", "D-B"):
        assert duties[did]["horizon"] == {"value": design, "unit": "h"}, did
    # every duty, the comparison duties too, ends at the same criterion (E5 and E6 compare them)
    for did, duty in duties.items():
        assert duty["threshold"]["ph"] == basis["threshold"]["ph"], did
    for did in ("D-A-ONOFF", "D-A-PART"):
        assert duties[did]["horizon"] == {"value": 3 * design, "unit": "h"}, did
        assert duties[did]["stack"] == "STK-A", did
        assert duties[did]["reservoir"]["volume"]["value"] == duties["D-A"]["reservoir"]["volume"]["value"], did
    assert duties["D-A"]["reservoir"]["size"] == "to_horizon"
    # the product and compressor discharge pressures of the flowsheet follow the design basis
    flowsheet = {s["id"]: s for s in _yaml(PROCESS / "process" / "flowsheet.yaml")["streams"]}
    to_kpa = {"bar(a)": 100.0, "bar": 100.0, "kPa(a)": 1.0, "kPa": 1.0}
    product = basis["product"]["pressure"]["value"] * to_kpa[basis["product"]["pressure"]["unit"]]
    loss = basis["psa_pressure_loss"]["value"] * to_kpa[basis["psa_pressure_loss"]["unit"]]
    for n in (1, 2):
        for case in ("skid-a", "skid-b"):
            state = {sid: flowsheet[sid]["state"][case] for sid in (f"S{n}07", f"S{n}08")}
            assert math.isclose(state[f"S{n}08"]["pressure"]["value"], product), (n, case)
            assert math.isclose(state[f"S{n}07"]["pressure"]["value"], product + loss), (n, case)


def test_calculated_setpoints_follow_the_model():
    """Every setpoint linked to a stream equals the stream's value, and the stack currents and
    the Skid B pH setpoint equal the design record's (regen step 9 writes them)."""
    loops = {lp["id"]: lp for lp in _yaml(PROCESS / "control" / "loops.yaml")["loops"]}
    flowsheet = {s["id"]: s for s in _yaml(PROCESS / "process" / "flowsheet.yaml")["streams"]}
    for lp in loops.values():
        for target in lp.get("targets") or []:
            if target.get("stream") and target.get("property"):
                case = (target.get("cases") or lp.get("cases"))[0]
                want = flowsheet[target["stream"]]["state"][case][target["property"]]["value"]
                assert math.isclose(target["value"], want, rel_tol=1e-9), f"{lp['id']}: {target['value']} != {want}"
    rec = _committed_records()[1000]
    for key, loop in (("A", "JIC-101"), ("B", "JIC-201")):
        assert loops[loop]["targets"][0]["value"] == rec["skids"][key]["bus_current_a"], loop
    assert loops["AIC-201"]["targets"][0]["value"] == round(rec["skids"]["B"]["final_ph"], 2)


def _docstrings(tree: ast.AST) -> set[int]:
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                ids.add(id(body[0].value))
    return ids


def test_no_script_reads_the_benchmarks():
    """ADR 0032: the held-out reproductions under benchmarks/ never enter a design input."""
    for path in sorted((PROCESS / "scripts").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        skip = _docstrings(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in skip:
                assert "benchmarks" not in node.value, f"{path.relative_to(KIT)}:{node.lineno} names benchmarks/"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=KIT, capture_output=True, text=True, check=True).stdout


def test_frozen_expectations_precede_the_regen_commits():
    try:
        if _git("rev-parse", "--is-shallow-repository").strip() == "true":
            pytest.skip("shallow clone: no history to compare")
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("no git history")
    added = _git("log", "--diff-filter=A", "--format=%H", "--", f"{REL}/results/expected.yaml").split()
    assert added, "results/expected.yaml has no commit that adds it"
    frozen = added[-1]
    touched = set(_git("show", "--format=", "--name-only", frozen).split())
    assert touched <= FROZEN_FILES, f"the frozen-expectations commit also touches {touched - FROZEN_FILES}"
    regen = _git("log", "--format=%H", "--", *REGEN_OUTPUTS).split()
    assert regen, "no regeneration commit"
    for commit in regen:
        assert commit != frozen
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", frozen, commit], cwd=KIT, check=False)
        assert ancestor.returncode == 0, f"regeneration commit {commit[:9]} does not come after the frozen {frozen[:9]}"
    # ADR 0030: the frozen files are not edited afterwards (a correction is a new file,
    # results/expected-errata.yaml); `git diff` also sees an edit made in a merge commit
    changed = _git("diff", "--name-only", frozen, "HEAD", "--", *sorted(FROZEN_FILES)).split()
    assert not changed, f"frozen files changed since the freezing commit {frozen[:9]}: {changed}"
    dirty = _git("status", "--porcelain", "--", *sorted(FROZEN_FILES)).split("\n")
    assert not [d for d in dirty if d.strip()], f"uncommitted changes to the frozen files: {dirty}"


def test_committed_records_meet_the_frozen_expectations(items, hand):
    records = _committed_records()
    assert_e1_to_e7(records, items, hand)
    assert_e9(records, items)
    # the model files are committed at the design duration: E8 holds for its record
    assert_e8(PROCESS, records[1000])
    for h, rec in records.items():
        assert rec["duration_h"] == h and not rec["ad_hoc"]


def test_committed_readme_table_is_the_records():
    """README.md's results table is the one regen writes from the committed records."""
    sys.path.insert(0, str(PROCESS / "scripts"))
    try:
        import _results
    finally:
        sys.path.pop(0)
    records = {float(h): r for h, r in _committed_records().items()}
    unc = {}
    for h in records:
        path = PROCESS / "results" / "scenarios" / f"{h:g}h" / "uncertainty.json"
        if path.exists():
            unc[h] = json.loads(path.read_text())
    text = (PROCESS / "README.md").read_text(encoding="utf-8")
    begin, end = "<!-- regen:results begin (scripts/regen.py step 17; do not edit) -->", "<!-- regen:results end -->"
    assert begin in text and end in text
    block = text.split(begin, 1)[1].split(end, 1)[0]
    assert block == "\n" + _results.readme_table(records, unc)


def test_committed_resize_report_is_clean():
    report = json.loads((PROCESS / "results" / "resize-1000h-10000h.json").read_text())
    s = report["summary"]
    assert s["hand_checks_failed"] == 0 and s["rules_broken"] == []
    assert s["feasible"] == {"A": {"1000": True, "10000": False}, "B": {"1000": True, "10000": True}}
    assert SENTENCE_A in s["sentences"]
    assert {r["rule"] for r in report["rows"]} == {
        "invariant-of-duration", "proportional-to-duration", "fixed-by-setpoint", "amortisation", "infeasible"}  # fmt: skip
    u = report["unchanged_artefacts"]
    assert all(v["unchanged"] for v in u["pid_sha256"].values())
    assert all(v["unchanged"] for v in u["stack_dimensions_m"].values())


def test_lci_frozen_expectations_precede_the_lca_commits():
    """#331: results/expected-lca.yaml was frozen in its own commit before any LCA output, and
    the frozen files are unchanged since (ADR 0030)."""
    try:
        if _git("rev-parse", "--is-shallow-repository").strip() == "true":
            pytest.skip("shallow clone: no history to compare")
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("no git history")
    added = _git("log", "--diff-filter=A", "--format=%H", "--", f"{REL}/results/expected-lca.yaml").split()
    assert added, "results/expected-lca.yaml has no commit that adds it"
    frozen = added[-1]
    touched = set(_git("show", "--format=", "--name-only", frozen).split())
    assert touched <= LCA_FROZEN_FILES, f"the LCI freezing commit also touches {touched - LCA_FROZEN_FILES}"
    for commit in _git("log", "--format=%H", "--", *LCA_OUTPUTS).split():
        assert commit != frozen
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", frozen, commit], cwd=KIT, check=False)
        assert ancestor.returncode == 0, f"LCA commit {commit[:9]} does not come after the frozen {frozen[:9]}"
    changed = _git("diff", "--name-only", frozen, "HEAD", "--", *sorted(LCA_FROZEN_FILES)).split()
    assert not changed, f"frozen files changed since the freezing commit {frozen[:9]}: {changed}"


def test_committed_layout_is_routed_clear_and_lifted():
    """The committed records' 3D results (regen step 25): see assert_layout."""
    assert_layout(PROCESS, _committed_records())


def test_committed_lca_meets_e10():
    assert_e10(PROCESS, _committed_records(), _committed_lca())


def test_committed_lca_datasets_are_the_design():
    """The committed datasets are the design's: per kg CO they are the 1,000 h LCA record's
    exchanges, they were derived from the committed flowsheet, and Skid B's names its case."""
    doc = _committed_lca()[1000]
    datasets = {"A": _yaml(PROCESS / "lca" / "dataset.yaml")}
    case = sorted((PROCESS / "lca" / "datasets").glob("*-skid-b.yaml"))
    assert len(case) == 1, case
    datasets["B"] = _yaml(case[0])
    flowsheet = "sha256:" + hashlib.sha256((PROCESS / "process" / "flowsheet.yaml").read_bytes()).hexdigest()
    for skid, ds in datasets.items():
        s = doc["skids"][skid]
        assert ds["id"] == s["dataset"] and ds["provenance"]["files"]["process/flowsheet.yaml"] == flowsheet, skid
        product = next(e for e in ds["exchanges"] if e["key"] == "product:CO")
        co = product["amount"] / doc["kg_per_unit"]
        for e in ds["exchanges"]:
            if e["key"] != "product:CO":
                assert rel(e["amount"] / co, s["exchanges"][e["key"]]["amount"], 1e-9) or e["amount"] == 0.0, (skid, e["key"])
    b, a = datasets["B"], datasets["A"]
    assert b["provenance"]["case"] == "skid-b" and a["provenance"]["case"] == "skid-a"
    assert b["title"].endswith(", case skid-b") and b["id"] == f"{a['id']}-skid-b"
    assert b["uuid"] != a["uuid"] and b["parent"] == a["uuid"]
    process = _yaml(PROCESS / "process.yaml")
    assert process["publication"] == {"status": "public", "license": "CC-BY-4.0"}  # D-048, ADR 0036
    keys = {i.get("inventory_key") for g in process["chemistry"].values() for i in g}
    assert {"feed:CO2", "feed:KOH-FILL", "feed:KOH-DOSE", "feed:POWER", "product:CO"} <= keys


def test_committed_lca_reports_are_the_records():
    """The sensitivities, the ranking and lca/README.md's tables are what
    scripts/lca_sensitivity.py writes from the committed LCA records; the ranking is not
    determined while a distinguishing flow has no factor."""
    sys.path.insert(0, str(PROCESS / "scripts"))
    try:
        import lca_sensitivity
    finally:
        sys.path.pop(0)
    texts = lca_sensitivity.texts(PROCESS)
    assert set(texts) >= {"lca/README.md", "lca/ranking.json", "lca/sensitivity-membrane-life.json"}
    for rel_path, text in texts.items():
        assert (PROCESS / rel_path).read_text(encoding="utf-8") == text, rel_path
    ranking = json.loads((PROCESS / "lca" / "ranking.json").read_text())
    assert ranking["verdict"] == "ranking not determined"
    assert {"feed:KOH-FILL", "feed:KOH-DOSE", "product:SPENT", "product:BLEED", "construction"} <= set(ranking["undocumented"])
    life = json.loads((PROCESS / "lca" / "sensitivity-membrane-life.json").read_text())
    assert life["impact"].startswith("not computable: gap") and life["datasets_match"]
    assert [r["membrane_life_h"] for r in life["rows"]] == [1000.0, 4000.0, 20000.0]


# -- slow: regenerate in a copy ---------------------------------------------------------------


def _model_gates(root: Path) -> dict[str, str]:
    """`cheme check --no-write` of the 3D model's gates alone (MODEL_GATES, layout-3d without
    its drawings requirement) in the folder *root*: {gate: "ok" or the gate's output}."""
    path = root / "checks" / "checks.yaml"
    text = path.read_text(encoding="utf-8")
    checks = yaml.safe_load(text)
    gates = [dict(c) for c in checks["checks"] if c["id"] in MODEL_GATES]
    assert {c["id"] for c in gates} == set(MODEL_GATES), [c["id"] for c in gates]
    for c in gates:
        if c["id"] == "layout-3d":
            c["require"] = [r for r in c["require"] if r != "drawings"]
    out = {}
    try:
        for c in gates:
            # one gate at a time, with the file's own acceptances (its top-level accept)
            path.write_text(yaml.safe_dump({**checks, "checks": [c]}), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "chemeascode", "check", "--no-write"],
                cwd=root, capture_output=True, text=True, check=False, timeout=900,
            )  # fmt: skip
            out[c["id"]] = "ok" if proc.returncode == 0 else (proc.stdout + proc.stderr)[-2000:]
    finally:
        path.write_text(text, encoding="utf-8")
    return out


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory) -> tuple[dict[int, dict], dict[int, str], dict[int, str], dict]:
    root = tmp_path_factory.mktemp("skids") / PROCESS.name
    shutil.copytree(PROCESS, root, ignore=shutil.ignore_patterns("build", ".claude", "runs", "__pycache__", ".venv"))
    records, e8, lca, e10 = {}, {}, {}, {}
    model: dict = {}
    for h in DURATIONS:
        proc = subprocess.run(
            [sys.executable, "-m", "chemeascode", "run", "scripts/regen.py", "--duration", str(h)],
            cwd=root, capture_output=True, text=True, check=False, timeout=900,
        )  # fmt: skip
        assert proc.returncode == 0, f"regen {h} h exited {proc.returncode}: {proc.stderr[-2000:]}"
        records[h] = json.loads((root / "results" / "scenarios" / f"{h}h" / "record.json").read_text())
        lca[h] = json.loads((root / "results" / "scenarios" / f"{h}h" / "lca.json").read_text())
        if h == 1000:  # the design duration: the model's gates and its outputs as committed
            model["gates"] = _model_gates(root)
            model["differ"] = [r for r in MODEL_OUTPUTS if (root / r).read_bytes() != (PROCESS / r).read_bytes()]
        try:  # E8 on the model as this run left it (the folder then holds the 10000 h model)
            assert_e8(root, records[h])
            e8[h] = "ok"
        except AssertionError as exc:
            e8[h] = str(exc)
        try:  # E10 (#331) on the LCA this run wrote (its datasets are this duration's)
            assert_e10(root, {h: records[h]}, {h: lca[h]})
            e10[h] = "ok"
        except AssertionError as exc:
            e10[h] = str(exc)
    return records, e8, e10, model


@engineering
@needs_core
def test_regenerated_skids_meet_e1_to_e7(regenerated, items, hand):
    assert_e1_to_e7(regenerated[0], items, hand)


@engineering
@needs_core
def test_regenerated_layout_carries_the_sizes_e8(regenerated):
    assert regenerated[1] == {1000: "ok", 10000: "ok"}


@engineering
@needs_core
def test_regenerated_infeasibility_and_ranges_are_reported_e9(regenerated, items):
    assert_e9(regenerated[0], items)


@engineering
@needs_core
def test_regenerated_lca_is_reconciled_e10(regenerated):
    assert regenerated[2] == {1000: "ok", 10000: "ok"}


@engineering
@needs_core
def test_regenerated_layout_is_routed_clear_and_lifted(regenerated):
    """0 clashes and every DN 25+ process line routed or skipped at 1,000 h; the 10,000 h
    clash, height and lifts reported (assert_layout), from the regenerated records."""
    assert_layout(PROCESS, regenerated[0])


@engineering
@needs_core
def test_regenerated_model_gates_pass_and_outputs_are_current(regenerated):
    """At 1,000 h core's gates layout-3d (without drawings: the review record), lifting-study
    (lifting-current), mto (mto-current) and electrical pass on the regenerated folder, and the
    model, take-off, lifting studies and cable schedule regenerate to the committed bytes."""
    model = regenerated[3]
    assert model["gates"] == dict.fromkeys(MODEL_GATES, "ok"), model["gates"]
    assert model["differ"] == [], f"regenerated differently from the committed: {model['differ']}"
