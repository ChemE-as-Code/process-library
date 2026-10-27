"""Benchmark registry: expressions and units, the registry's checks, KPIs in the LCI build and the
catalog, and the deliberately mis-scaled fixture that must fail the strict build."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import benchmarks as bm  # noqa: E402
import build_catalog  # noqa: E402
import build_lci  # noqa: E402
import registry as reg  # noqa: E402

MIS_SCALED = KIT / "tests" / "fixtures" / "benchmarks" / "asu-1-mis-scaled.yaml"
SCHEMA = KIT / "schemas" / "benchmarks.schema.json"
FAMILIES = reg.load_families(KIT / "taxonomy" / "families.yaml")

# Unit conversion goes through core's foundation.units (Pint). Without core the KPIs are
# unchecked; CI installs it and sets ATLAS_REQUIRE_CORE, so a missing core fails there.
try:
    import pint  # noqa: F401
    from chemeascode.foundation import units as core_units
except ImportError:
    if os.environ.get("ATLAS_REQUIRE_CORE"):
        raise
    core_units = None
needs_core = pytest.mark.skipif(core_units is None, reason="needs cheme-as-code[units] (core's foundation.units)")


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _library(tmp_path: Path, dataset: Path = KIT / "processes" / "asu-1" / "lca" / "dataset.yaml") -> Path:
    """A library of ASU-1 (its manifest, the given dataset) with the real registry, taxonomy,
    mappings and benchmarks."""
    library = tmp_path / "library"
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
    shutil.copy(dataset, library / "processes" / "asu-1" / "lca" / "dataset.yaml")
    for folder in ("chemicals", "taxonomy", "lci", "benchmarks"):
        shutil.copytree(KIT / folder, library / folder)
    return library


def _edit_benchmarks(library: Path, change) -> None:
    path = library / "benchmarks" / "air-separation.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# --- expressions -----------------------------------------------------------------------------


def test_expression_values_and_units() -> None:
    amounts = {"feed:POWER": (500.0, "kWh"), "product:GOXP": (1000.0, "kg"), "product:LOX": (250.0, "kg"), "feed:mixed-key_1.a": (2.0, "kg")}
    assert bm.compute("feed:POWER / product:GOXP", amounts) == (0.5, {"kWh": 1, "kg": -1})
    value, units = bm.compute("feed:POWER / (product:GOXP + product:LOX)", amounts)
    assert value == pytest.approx(0.4) and bm.unit_text(units) == "kWh/kg"
    assert bm.compute("2 * feed:mixed-key_1.a - -1e0 * product:LOX", amounts) == (254.0, {"kg": 1})
    assert bm.unit_text(bm.compute("product:GOXP / product:LOX", amounts)[1]) == "1"


@pytest.mark.parametrize(
    "expression, message",
    [
        ("feed:POWER + product:GOXP", "adds kWh and kg"),
        ("feed:POWER / product:NOPE", "no exchange product:NOPE"),
        ("feed:POWER / (product:GOXP - product:GOXP)", "division by zero"),
        ("feed:POWER / (product:GOXP", "missing )"),
        ("feed:POWER ^ 2", "cannot read"),
        ("feed:POWER product:GOXP", "unexpected"),
    ],
)
def test_expression_errors(expression: str, message: str) -> None:
    with pytest.raises(bm.ExpressionError, match=message.replace("(", r"\(").replace(")", r"\)")):
        bm.compute(expression, {"feed:POWER": (1.0, "kWh"), "product:GOXP": (1.0, "kg")})


def test_syntax_check_allows_a_divisor_that_is_zero_only_when_every_key_is_1() -> None:
    # a net-output denominator is a normal KPI; at load, with every key 1, it is 0
    expression = "feed:POWER / (product:GOXP - product:LOX)"
    assert bm.compute(expression) == (1.0, {})
    assert bm.compute(expression, {"feed:POWER": (10.0, "kWh"), "product:GOXP": (20.0, "kg"), "product:LOX": (5.0, "kg")}) == (10 / 15, {"kWh": 1, "kg": -1})


def test_units_of_inventory_without_pint_spelling_must_match() -> None:
    assert bm.convert(3.0, {"tkm": 1, "kg": -1}, "tkm/kg") == 3.0
    with pytest.raises(bm.ExpressionError, match="does not convert"):
        bm.convert(3.0, {"tkm": 1, "kg": -1}, "tkm/t")


@needs_core
def test_units_convert_through_core() -> None:
    assert bm.convert(0.5, {"kWh": 1, "kg": -1}, "kWh/t") == pytest.approx(500.0)
    assert bm.convert(0.5, {"kWh": 1, "kg": -1}, "GJ/t") == pytest.approx(1.8)
    with pytest.raises(bm.ExpressionError, match="does not convert to kg/t"):
        bm.convert(0.5, {"kWh": 1, "kg": -1}, "kg/t")


# --- the registry ----------------------------------------------------------------------------


def test_library_registry_is_sound() -> None:
    registry, problems = bm.load(KIT / "benchmarks", SCHEMA, FAMILIES)
    assert problems == []
    assert ("asu-1", "asu-1-500-t-d-gox") in registry.bindings
    for data in registry.families.values():
        for kid, kpi in data["kpis"].items():
            for ref in kpi.get("references", []):  # a range always names its source and conditions
                assert ref["source"]["citation"] and ref["conditions"], kid


def test_no_benchmarks_folder_means_no_registry(tmp_path: Path) -> None:
    assert bm.load(tmp_path / "benchmarks", SCHEMA, FAMILIES) == (None, [])


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda d: d.update(family="ammonia"), "differs from the file name"),
        (lambda d: d["kpis"]["specific-power-gox"].pop("references"), "is not valid under any of the given schemas"),
        (lambda d: d["kpis"]["specific-power-gox"]["references"][0].update(range=[600, 400]), "range is reversed"),
        (lambda d: d["datasets"][0]["kpis"]["specific-power-gox"].pop("reference"), "reference must be one of air-liquide-yango-2017"),
        (lambda d: d["datasets"][0]["kpis"]["cooling-duty-gox"].update(reference="air-liquide-yango-2017"), "the KPI has no references"),
        (lambda d: d["datasets"][0]["kpis"]["cooling-duty-gox"].update(out_of_range_reason="a reason for a KPI that has no range"), "out_of_range_reason, but the KPI has no range"),
        (lambda d: d["datasets"][0]["kpis"].update({"recovery": {"expression": "product:GOXP / feed:AIR"}}), "unknown KPI 'recovery'"),
        (lambda d: d["datasets"][0]["kpis"]["specific-power-gox"].update(expression="feed:POWER // product:GOXP"), "unexpected '/'"),
        (lambda d: d["datasets"].append(d["datasets"][0]), "listed twice"),
        (lambda d: d["kpis"]["specific-power-gox"]["references"][0]["source"].pop("kind"), "'kind' is a required property"),
    ],
)
def test_registry_problems(tmp_path: Path, change, message: str) -> None:
    library = _library(tmp_path)
    _edit_benchmarks(library, change)
    _, problems = bm.load(library / "benchmarks", SCHEMA, FAMILIES)
    assert any(message in p for p in problems), problems


def test_a_family_outside_the_taxonomy_is_refused(tmp_path: Path) -> None:
    library = _library(tmp_path)
    _edit_benchmarks(library, lambda d: d.update(family="air-sep"))
    (library / "benchmarks" / "air-separation.yaml").rename(library / "benchmarks" / "air-sep.yaml")
    _, problems = bm.load(library / "benchmarks", SCHEMA, FAMILIES)
    assert problems == ["benchmarks/air-sep.yaml: family 'air-sep' is not in taxonomy/families.yaml"]


def test_a_registry_problem_fails_both_builds(tmp_path: Path) -> None:
    library = _library(tmp_path)
    _edit_benchmarks(library, lambda d: d["kpis"]["specific-power-gox"]["references"][0].update(range=[600, 400]))
    assert any("range is reversed" in e for e in build_lci.build(library, tmp_path / "lci", "0.1.0", commit="fixture").errors)
    assert any("range is reversed" in e for e in build_catalog.build(library, tmp_path / "cat", None, "fixture").errors)


# --- evaluation in the builds ----------------------------------------------------------------


@needs_core
def test_asu_kpis_in_the_datapackage(tmp_path: Path) -> None:
    library = _library(tmp_path)
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    dataset = _json(tmp_path / "out" / "lci" / "datapackage.json")["processes"][0]["datasets"][0]
    kpis = {k["kpi"]: k for k in dataset["benchmarks"]}
    power = kpis["specific-power-gox"]
    data = yaml.safe_load((library / "processes" / "asu-1" / "lca" / "dataset.yaml").read_text(encoding="utf-8"))
    amounts = {e["key"]: e["amount"] for e in data["exchanges"]}
    assert power["value"] == pytest.approx(amounts["feed:POWER"] / amounts["product:GOXP"] * 1000)
    assert power["status"] == "inside" and power["reference"]["id"] == "air-liquide-yango-2017"
    assert power["allocated"] == pytest.approx(power["value"] * dataset["allocation"]["shares"]["product:GOXP"])
    cooling = kpis["cooling-duty-gox"]
    assert cooling["status"] == "no-reference" and cooling["reference"] is None and "2026-10-25" in cooling["no_open_reference"]
    assert cooling["value"] == pytest.approx(amounts["product:CW"] / amounts["product:GOXP"] * 3.6)
    recovery = kpis["o2-recovery"]
    o2_in_air = (amounts["feed:AIR"] - amounts["emission:H2O"]) * 0.2314
    assert recovery["value"] == pytest.approx(100 * (1 - amounts["emission:O2"] / o2_in_air))
    assert 80 < recovery["value"] < 86  # DESIGN.md D-066: ~83 %
    assert recovery["status"] == "explained" and "D-066" in recovery["reason"] and "allocated" not in recovery


@needs_core
def test_mis_scaled_fixture_fails_the_strict_build(tmp_path: Path) -> None:
    library = _library(tmp_path, MIS_SCALED)
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == []
    (warning,) = report.warnings
    assert "kpis.specific-power-gox: 5.017e+05 kWh/t is outside 400 to 600 kWh/t of reference air-liquide-yango-2017" in warning
    assert build_lci.main(["--library", str(library), "--out", str(tmp_path / "strict"), "--strict"]) == 1
    assert build_lci.main(["--library", str(library), "--out", str(tmp_path / "lenient")]) == 0
    power = next(k for k in _json(tmp_path / "lenient" / "lci" / "datapackage.json")["processes"][0]["datasets"][0]["benchmarks"] if k["kpi"] == "specific-power-gox")
    assert power["status"] == "outside"


@needs_core
def test_an_explained_value_passes_and_a_stale_reason_is_reported(tmp_path: Path) -> None:
    library = _library(tmp_path, MIS_SCALED)
    reason = "a test: the power is deliberately given in Wh to check the strict build"
    _edit_benchmarks(library, lambda d: d["datasets"][0]["kpis"]["specific-power-gox"].update(out_of_range_reason=reason))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    power = next(k for k in _json(tmp_path / "out" / "lci" / "datapackage.json")["processes"][0]["datasets"][0]["benchmarks"] if k["kpi"] == "specific-power-gox")
    assert power["status"] == "explained" and power["reason"] == reason

    library = _library(tmp_path / "inside")  # the real dataset is inside: the reason is stale
    _edit_benchmarks(library, lambda d: d["datasets"][0]["kpis"]["specific-power-gox"].update(out_of_range_reason=reason))
    (warning,) = build_lci.build(library, tmp_path / "out2", "0.1.0", commit="fixture").warnings
    assert "is inside 400 to 600, but an out_of_range_reason is given" in warning


def test_without_core_a_conversion_is_unchecked_and_fails_strict(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "chemeascode.foundation.units", None)  # import raises ImportError
    library = _library(tmp_path)
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == []
    assert len(report.warnings) == 3 and all("needs core's foundation.units" in w for w in report.warnings)
    statuses = {k["status"] for k in _json(tmp_path / "out" / "lci" / "datapackage.json")["processes"][0]["datasets"][0]["benchmarks"]}
    assert statuses == {"unchecked"}


@needs_core
def test_a_public_process_needs_two_kpis_and_bindings_need_a_dataset(tmp_path: Path) -> None:
    library = _library(tmp_path)
    _edit_benchmarks(library, lambda d: [d["datasets"][0]["kpis"].pop(k) for k in ("cooling-duty-gox", "o2-recovery")])
    (warning,) = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture").warnings
    assert warning.startswith("asu-1: 1 benchmarked KPI(s); a public process needs at least 2")

    library = _library(tmp_path / "renamed")
    _edit_benchmarks(library, lambda d: d["datasets"][0].update(dataset="asu-1-old"))
    warnings = build_lci.build(library, tmp_path / "out2", "0.1.0", commit="fixture").warnings
    assert "benchmarks: datasets asu-1/asu-1-old: no such LCI dataset in the library (renamed?)" in warnings
    assert any(w.startswith("asu-1: 0 benchmarked KPI(s)") for w in warnings)


@needs_core
@pytest.mark.parametrize(
    "per, message",
    [
        ("product:GOX", "per product:GOX is not a product exchange of the dataset"),
        ("feed:POWER", "per feed:POWER is not a product exchange of the dataset"),
    ],
)
def test_a_wrong_per_is_a_warning(tmp_path: Path, per: str, message: str) -> None:
    library = _library(tmp_path)
    _edit_benchmarks(library, lambda d: d["datasets"][0]["kpis"]["specific-power-gox"].update(per=per))
    (warning,) = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture").warnings
    assert message in warning


@needs_core
def test_a_per_without_an_allocation_share_is_a_warning() -> None:
    registry, _ = bm.load(KIT / "benchmarks", SCHEMA, FAMILIES)
    dataset = yaml.safe_load((KIT / "processes" / "asu-1" / "lca" / "dataset.yaml").read_text(encoding="utf-8"))
    results, warnings = bm.evaluate(registry, "asu-1", dataset, {"product:GANP": 1.0})
    assert any("per product:GOXP has no allocation share" in w for w in warnings)
    assert all("allocated" not in k for k in results)


@needs_core
def test_a_binding_outside_the_process_families_is_a_warning(tmp_path: Path) -> None:
    library = _library(tmp_path)
    manifest = library / "processes" / "asu-1" / "process.yaml"
    text = manifest.read_text(encoding="utf-8")
    manifest.write_text(text.replace("families: [air-separation, ", "families: ["), encoding="utf-8")
    message = "asu-1: benchmarks/air-separation.yaml binds asu-1, but process.yaml families does not list 'air-separation'"
    assert message in build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture").warnings
    assert message in build_catalog.build(library, tmp_path / "cat", None, "fixture").warnings


def test_a_library_without_benchmarks_builds_as_before(tmp_path: Path) -> None:
    library = _library(tmp_path)
    shutil.rmtree(library / "benchmarks")
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    assert _json(tmp_path / "out" / "lci" / "datapackage.json")["processes"][0]["datasets"][0]["benchmarks"] == []


@needs_core
def test_catalog_carries_the_same_kpis(tmp_path: Path) -> None:
    library = _library(tmp_path)
    report = build_catalog.build(library, tmp_path / "cat", None, "fixture")
    assert report.errors == [] and report.warnings == []
    build_lci.build(library, tmp_path / "lci", "0.1.0", commit="fixture")
    detail = _json(tmp_path / "cat" / "processes" / "asu-1.json")
    lci = _json(tmp_path / "lci" / "lci" / "datapackage.json")["processes"][0]["datasets"][0]["benchmarks"]
    assert [{k: v for k, v in b.items() if k != "dataset"} for b in detail["benchmarks"]] == [{k: v for k, v in b.items() if k != "allocated"} for b in lci]
    assert {b["dataset"] for b in detail["benchmarks"]} == {"asu-1-500-t-d-gox"}
    summary = _json(tmp_path / "cat" / "catalog.json")["processes"][0]
    assert summary["benchmarks"] == {"explained": 1, "inside": 1, "no-reference": 1}

    mis = _library(tmp_path / "mis", MIS_SCALED)
    report = build_catalog.build(mis, tmp_path / "cat2", None, "fixture")
    assert any("is outside 400 to 600 kWh/t" in w for w in report.warnings)
    assert build_catalog.main(["--library", str(mis), "--out", str(tmp_path / "cat3"), "--strict"]) == 1


@needs_core
def test_both_builds_store_the_benchmark_report(tmp_path: Path) -> None:
    """benchmarks.json (#85): every result with its process and dataset, the counts by status;
    the LCI build's adds the allocated values and is listed in index.json."""
    library = _library(tmp_path)
    assert build_catalog.build(library, tmp_path / "cat", None, "fixture").errors == []
    assert build_lci.build(library, tmp_path / "lci", "0.1.0", commit="fixture").errors == []
    catalog = _json(tmp_path / "cat" / "benchmarks.json")
    lci = _json(tmp_path / "lci" / "lci" / "benchmarks.json")
    detail = _json(tmp_path / "cat" / "processes" / "asu-1.json")["benchmarks"]

    for report in (catalog, lci):
        assert report["schema"] == bm.REPORT_SCHEMA and report["mode"] == "preview"
        assert report["library"]["commit"] == "fixture"
        assert [(r["process"], r["dataset"], r["kpi"]) for r in report["results"]] == [("asu-1", "asu-1-500-t-d-gox", k) for k in ("cooling-duty-gox", "o2-recovery", "specific-power-gox")]
        assert report["summary"] == {"kpis": 3, "by_status": {"explained": 1, "inside": 1, "no-reference": 1}, "processes": {"asu-1": {"explained": 1, "inside": 1, "no-reference": 1}}}
    assert [{k: v for k, v in r.items() if k != "process"} for r in catalog["results"]] == sorted(detail, key=lambda r: r["kpi"])
    power = next(r for r in lci["results"] if r["kpi"] == "specific-power-gox")
    assert "allocated" in power and power["allocated"] < power["value"]  # GOX carries part of the burden (exergy)
    assert "allocated" not in next(r for r in catalog["results"] if r["kpi"] == "specific-power-gox")
    index = _json(tmp_path / "lci" / "lci" / "index.json")
    entry = next(f for f in index["files"] if f["name"] == "benchmarks.json")
    assert entry["format_version"] == bm.REPORT_SCHEMA


def test_a_public_build_reports_public_processes_only(tmp_path: Path) -> None:
    library = _library(tmp_path)
    manifest = library / "processes" / "asu-1" / "process.yaml"
    text = manifest.read_text(encoding="utf-8")
    assert "  status: public\n" in text
    manifest.write_text(text.replace("  status: public\n", "  status: internal\n", 1), encoding="utf-8")
    assert build_catalog.build(library, tmp_path / "cat", None, "fixture", public=True).errors == []
    assert build_lci.build(library, tmp_path / "lci", "0.1.0", commit="fixture", public=True).errors == []
    for path in (tmp_path / "cat" / "benchmarks.json", tmp_path / "lci" / "lci" / "benchmarks.json"):
        report = _json(path)
        assert report["mode"] == "public" and report["results"] == [] and report["summary"] == {"kpis": 0, "by_status": {}, "processes": {}}


def test_report_sorts_and_counts() -> None:
    rows = [
        {"process": "b", "dataset": "d", "kpi": "x", "status": "outside"},
        {"process": "a", "dataset": "d", "kpi": "y", "status": "inside"},
        {"process": "a", "dataset": "d", "kpi": "x", "status": "inside"},
    ]
    report = bm.report(rows, "preview", {"commit": None, "dirty": None})
    assert [(r["process"], r["kpi"]) for r in report["results"]] == [("a", "x"), ("a", "y"), ("b", "x")]
    assert report["summary"] == {"kpis": 3, "by_status": {"inside": 2, "outside": 1}, "processes": {"a": {"inside": 2}, "b": {"outside": 1}}}
