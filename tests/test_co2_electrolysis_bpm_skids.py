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
"""

from __future__ import annotations

import ast
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

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
    """The layout and the datasheets carry the sizes `cheme process stack --write` wrote."""
    listed = {e["tag"]: e for e in _yaml(root / "equipment" / "equipment-list.yaml")["equipment"]}
    model = {e["tag"]: e for e in _yaml(root / "layout" / "plant-model.yaml")["equipment"]}
    for skid, s in record["skids"].items():
        for e in s["equipment"]:
            if e["role"] not in ("stack", "reservoir", "dosing_tank"):
                continue
            tag, dims = e["tag"], e["values"]
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
    design = basis["duration"]["design"]["value"]
    assert design in basis["duration"]["scenarios"]
    for did in ("D-A", "D-B"):
        assert duties[did]["horizon"] == {"value": design, "unit": "h"}, did
        assert duties[did]["threshold"]["ph"] == basis["threshold"]["ph"], did
    for did in ("D-A-ONOFF", "D-A-PART"):
        assert duties[did]["horizon"] == {"value": 3 * design, "unit": "h"}, did
        assert duties[did]["stack"] == "STK-A", did
        assert duties[did]["reservoir"]["volume"]["value"] == duties["D-A"]["reservoir"]["volume"]["value"], did
    assert duties["D-A"]["reservoir"]["size"] == "to_horizon"


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


def test_committed_records_meet_the_frozen_expectations(items, hand):
    records = _committed_records()
    assert_e1_to_e7(records, items, hand)
    assert_e9(records, items)
    # the model files are committed at the design duration: E8 holds for its record
    assert_e8(PROCESS, records[1000])
    for h, rec in records.items():
        assert rec["duration_h"] == h and not rec["ad_hoc"]


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


# -- slow: regenerate in a copy ---------------------------------------------------------------


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory) -> tuple[dict[int, dict], dict[int, str]]:
    root = tmp_path_factory.mktemp("skids") / PROCESS.name
    shutil.copytree(PROCESS, root, ignore=shutil.ignore_patterns("build", ".claude", "runs", "__pycache__", ".venv"))
    records, e8 = {}, {}
    for h in DURATIONS:
        proc = subprocess.run(
            [sys.executable, "-m", "chemeascode", "run", "scripts/regen.py", "--duration", str(h)],
            cwd=root, capture_output=True, text=True, check=False, timeout=900,
        )  # fmt: skip
        assert proc.returncode == 0, f"regen {h} h exited {proc.returncode}: {proc.stderr[-2000:]}"
        records[h] = json.loads((root / "results" / "scenarios" / f"{h}h" / "record.json").read_text())
        try:  # E8 on the model as this run left it (the folder then holds the 10000 h model)
            assert_e8(root, records[h])
            e8[h] = "ok"
        except AssertionError as exc:
            e8[h] = str(exc)
    return records, e8


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
