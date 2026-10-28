"""LCI builder without Brightway: workbook layout, determinism, allocation, linking, errors."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
openpyxl = pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_lci  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
LIBRARY = FIXTURES / "library"
ASU = FIXTURES / "asu-lca"
DB = "cheme-as-code-atlas-0.1.0"
H2 = "fixture-electrolysis:fixture-electrolysis:product:H2"
NH3 = "fixture-ammonia:fixture-ammonia-hb:product:ammonia"
H2_MARKET = "market:hydrogen:GLO"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    return copy


def _build(library: Path, out: Path, version: str = "0.1.0") -> build_lci.Report:
    return build_lci.build(library, out, version, commit="fixture")


def _activities(xlsx: Path) -> dict[str, dict]:
    """Read the workbook the way bw2io's ExcelImporter does (sections by their first cell)."""
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    found: dict[str, dict] = {}
    for ws in wb:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        if rows and rows[0][0] == "skip":
            continue
        current = None
        columns = None
        for row in rows:
            first = row[0] if row else None
            if first == "Activity":
                current = {"name": row[1], "meta": {}, "exchanges": []}
                columns = None
            elif current is None or first is None:
                continue
            elif first == "Exchanges":
                columns = []
            elif columns == []:
                columns = [c for c in row if c is not None]
            elif columns:
                current["exchanges"].append({c: v for c, v in zip(columns, row) if v is not None})
            else:
                current["meta"][first] = row[1]
                if first == "code":
                    found[row[1]] = current
    return found


def _exchange(activity: dict, key: str) -> dict:
    return next(e for e in activity["exchanges"] if e.get("atlas key") == key)


# --- output contract -----------------------------------------------------------------------


def test_fixture_build_writes_workbook_datapackage_and_index(library: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    report = _build(library, out)
    assert report.errors == [] and report.warnings == []
    assert sorted(p.name for p in (out / "lci").iterdir()) == sorted([f"{DB}.xlsx", f"{DB}-olca-jsonld.zip", f"{DB}-multifunctional.json", "datapackage.json", "benchmarks.json", "gaps.json", "index.json"])

    index = _json(out / "lci" / "index.json")
    assert index["version"] == "0.1.0" and index["database"] == DB and index["library_commit"] == "fixture"
    for entry in index["files"]:
        data = (out / entry["path"]).read_bytes()
        assert entry["bytes"] == len(data) and entry["sha256"] == hashlib.sha256(data).hexdigest()
    assert sorted(index["processes"]) == ["fixture-ammonia", "fixture-electrolysis"]
    assert [a["code"] for a in index["processes"]["fixture-electrolysis"]] == [H2, H2.replace(":H2", ":O2")]
    assert any("placeholders" in c and c.startswith("fixture-electrolysis") for c in index["caveats"])

    package = _json(out / "lci" / "datapackage.json")
    electrolysis = next(p for p in package["processes"] if p["id"] == "fixture-electrolysis")
    assert electrolysis["maturity"] == "concept" and electrolysis["factors_status"] == "placeholder"
    assert electrolysis["allocation"] == {"method": "mass", "source": "study", "rule": "mass"}
    assert electrolysis["functional_unit"] == {"product": "H2", "amount": 1, "unit": "kg"}
    assert electrolysis["datasets"][0]["data_status"] == {"given": 0, "calculated": 1, "assumed": 8}
    ammonia = next(p for p in package["processes"] if p["id"] == "fixture-ammonia")
    assert ammonia["allocation"] == {"method": "mass", "source": "default", "rule": "single-output"} and ammonia["functional_unit"] is None
    assert ammonia["datasets"][0]["path"] == "processes/fixture-ammonia/lca/datasets/ammonia.yaml"


def test_two_builds_are_byte_identical(library: Path, tmp_path: Path) -> None:
    _build(library, tmp_path / "a")
    _build(library, tmp_path / "b")
    names = sorted(p.name for p in (tmp_path / "a" / "lci").iterdir())
    for name in names:
        assert (tmp_path / "a" / "lci" / name).read_bytes() == (tmp_path / "b" / "lci" / name).read_bytes(), name


def test_workbook_follows_the_bw2io_excel_layout(library: Path, tmp_path: Path) -> None:
    _build(library, tmp_path / "out")
    xlsx = tmp_path / "out" / "lci" / f"{DB}.xlsx"
    wb = openpyxl.load_workbook(xlsx, read_only=True)
    assert wb.sheetnames[0] == "about" and next(wb["about"].iter_rows(values_only=True))[0] == "skip"
    first_cells = [r[0] for ws in wb for r in ws.iter_rows(values_only=True) if r and r[0]]
    assert first_cells.count("Database") == 1
    assert next(wb["database"].iter_rows(values_only=True))[:2] == ("Database", DB)
    assert wb.properties.created.year == 2000 and wb.properties.modified.year == 2000

    activities = _activities(xlsx)
    assert sorted(activities) == sorted([H2, H2.replace(":H2", ":O2"), NH3, H2_MARKET])
    assert "markets" in wb.sheetnames
    for activity in activities.values():
        production = [e for e in activity["exchanges"] if e["type"] == "production"]
        assert len(production) == 1 and production[0]["amount"] == 1
        assert production[0]["name"] == activity["name"]
        assert production[0]["reference product"] == activity["meta"]["reference product"]
        assert set().union(*activity["exchanges"]) <= set(build_lci.EXCHANGE_COLUMNS)
        assert ("Allocation:" if "atlas process" in activity["meta"] else "production mix") in activity["meta"]["comment"]


def test_amounts_are_allocated_per_unit_of_each_product(library: Path, tmp_path: Path) -> None:
    _build(library, tmp_path / "out")
    activities = _activities(tmp_path / "out" / "lci" / f"{DB}.xlsx")
    share = 41.7 / (41.7 + 333.6)
    h2 = activities[H2]
    power = _exchange(h2, "feed:POWER")
    assert power["amount"] == pytest.approx(2293.5 * share / 41.7, rel=1e-11)
    assert power["unit"] == "kilowatt hour" and power["location"] == "DE" and power["atlas location rule"] == "site"
    emission = _exchange(h2, "emission:H2")
    assert emission["type"] == "biosphere" and emission["categories"] == "air" and "database" not in emission
    steel = _exchange(h2, "construction:steel")  # lognormal gsd2 1.21 -> scale ln(1.21)/2
    assert steel["uncertainty type"] == 2 and steel["scale"] == pytest.approx(0.0953101798, rel=1e-9)
    assert not any(e.get("atlas key") == "emission:H2O" for e in h2["exchanges"])  # pass-through
    assert "emission:H2O (pass-through" in h2["meta"]["comment"]
    o2 = activities[H2.replace(":H2", ":O2")]
    assert _exchange(o2, "feed:POWER")["amount"] == pytest.approx(power["amount"])  # mass: same per kg


def test_inputs_made_by_another_atlas_process_name_its_market_and_plant(library: Path, tmp_path: Path) -> None:
    _build(library, tmp_path / "out")
    hydrogen = _exchange(_activities(tmp_path / "out" / "lci" / f"{DB}.xlsx")[NH3], "feed:hydrogen")
    assert hydrogen["name"] == "market for hydrogen, gaseous"  # background by default
    # prefer_atlas: the market of the product (markets/hydrogen.yaml), the plant beside it for pinning
    assert (hydrogen["atlas activity"], hydrogen["atlas reference product"], hydrogen["atlas location"]) == ("market for hydrogen", "Hydrogen", "GLO")
    assert hydrogen["atlas code"] == H2_MARKET and hydrogen["atlas link"] == "market"
    assert hydrogen["atlas check"].startswith("compatible: grade the input names hydrogen only")
    assert (hydrogen["atlas plant activity"], hydrogen["atlas plant reference product"], hydrogen["atlas plant code"]) == ("Fixture: water electrolysis", "Hydrogen at 30 bar", H2)
    assert "boundary plant gate (pinned)" in hydrogen["atlas plant check"]
    package = _json(tmp_path / "out" / "lci" / "datapackage.json")
    assert [(link["consumer"], link["provider"], link["kind"]) for link in package["atlas_links"]] == [(H2_MARKET, H2, "supply"), (NH3, H2_MARKET, "market")]


# --- ASU-1 (real dataset, staged mappings) ----------------------------------------------------


def test_asu_exports_four_exergy_allocated_activities(tmp_path: Path) -> None:
    library = tmp_path / "library"
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
    shutil.copy(KIT / "processes" / "asu-1" / "lca" / "mappings.yaml", library / "processes" / "asu-1" / "lca")  # its own overrides
    shutil.copy(KIT / "chemicals" / "chemicals.yaml", library / "chemicals")
    for name in ("dataset.yaml", "lca.yaml", "factors.yaml"):
        shutil.copy(ASU / name, library / "processes" / "asu-1" / "lca")
    report = _build(library, tmp_path / "out")
    assert report.errors == []
    package = _json(tmp_path / "out" / "lci" / "datapackage.json")
    asu = package["processes"][0]
    # the database's rule (lci/mappings.yaml allocation): exergy, hierarchy step 2a, as the study
    assert asu["allocation"] == {"method": "exergy", "source": "mappings", "rule": "physical-exergy"}
    assert asu["datasets"][0]["allocation"]["follows_hierarchy"] is True
    assert asu["datasets"][0]["allocation"]["shares"]["product:GOXP"] == pytest.approx(0.701, abs=5e-4)
    # the four products are distinct registry grades (chemicals.yaml flow_grades), named by them
    assert [a["reference_product"] for a in asu["activities"]] == [
        "Oxygen, gaseous, >= 99.5 mol%, 30 barg", "Nitrogen, gaseous, <= 10 ppm O2, 8 barg", "Oxygen, liquid", "Nitrogen, liquid"
    ]
    assert [(a["chemical"], a["grade"]) for a in asu["activities"]] == [
        ("oxygen", "gox-30barg-99.5"), ("nitrogen", "gan-8barg-10ppm"), ("oxygen", "lox"), ("nitrogen", "lin")
    ]
    # the study's exergies agree with the registry grades' within 2 %, except LIN (a stated reason)
    checks = {c["key"]: c["status"] for c in asu["datasets"][0]["property_checks"]}
    assert checks == {"product:GOXP": "match", "product:GANP": "match", "product:LOX": "match", "product:LIN": "overridden"}
    assert sorted(p["code"] for p in package["proxies"]) == [  # no credit proxies under cut-off
        "proxy:cooling-water", "proxy:fitting", "proxy:grating", "proxy:insulation", "proxy:pipe",
    ]
    goxp = _activities(tmp_path / "out" / "lci" / "cheme-as-code-atlas-0.1.0.xlsx")["asu-1:asu-1-500-t-d-gox:product:GOXP"]
    assert not [e for e in goxp["exchanges"] if e["type"] == "biosphere"]  # every emission is pass-through
    assert _exchange(goxp, "feed:POWER")["amount"] * 1000 == pytest.approx(377.686, abs=5e-4)  # results.csv
    for key in ("feed:AIR", "product:VENT", "emission:CO2", "emission:N2", "emission:O2", "emission:AR", "emission:H2O"):
        assert key in goxp["meta"]["comment"]


# --- errors -----------------------------------------------------------------------------------


def _edit_dataset(library: Path, change) -> None:
    path = library / "processes" / "fixture-electrolysis" / "lca" / "dataset.yaml"
    data = yaml.safe_load(path.read_text())
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda d: d.update(kind="lca"), "kind is 'lca'"),
                    (lambda d: d["exchanges"][0].update(unit="ea*h"), "unit ea*h: item-hours"),
            (lambda d: d["exchanges"][0].update(unit="barrel"), "unit 'barrel' is not one of"),
        (lambda d: d["exchanges"].append(dict(d["exchanges"][0])), "appear twice: feed:WATER"),
        (lambda d: d["exchanges"][0].update(key="WATER"), "is not <kind>:<id>"),
        (lambda d: d.update(scope="linked"), "only foreground"),
        (lambda d: d.update(allocation={"method": "substitution"}), None),  # the study's mass wins
    ],
)
def test_invalid_datasets_fail_with_the_reason(library: Path, tmp_path: Path, change, message) -> None:
    _edit_dataset(library, change)
    report = _build(library, tmp_path / "out")
    if message is None:
        assert report.errors == [] and any("differs from the dataset's default" in w for w in report.warnings)
    else:
        assert any(message in e and "fixture-electrolysis/lca/dataset.yaml" in e for e in report.errors), report.errors
        assert not (tmp_path / "out" / "lci").exists()


def test_substitution_cannot_be_exported_per_co_product(library: Path, tmp_path: Path) -> None:
    (library / "processes" / "fixture-electrolysis" / "lca" / "lca.yaml").unlink()
    _edit_dataset(library, lambda d: d.update(allocation={"method": "substitution"}))
    report = _build(library, tmp_path / "out")
    assert any("allocation 'substitution' cannot be exported" in e for e in report.errors)


def test_unmapped_exchange_and_uncurated_free_emission_fail(library: Path, tmp_path: Path) -> None:
    def change(d):
        d["exchanges"].append({"key": "feed:CATALYST", "type": "input", "amount": 1.0, "unit": "kg"})
        d["exchanges"].append({"key": "emission:AR", "type": "emission", "amount": 1.0, "unit": "kg", "free": True})

    _edit_dataset(library, change)
    report = _build(library, tmp_path / "out")
    assert any("feed:CATALYST: no mapping" in e for e in report.errors)
    assert any("free emission of AR is not in lci/mappings.yaml pass_through" in e for e in report.errors)


def test_unit_mismatch_with_the_mapping_fails(library: Path, tmp_path: Path) -> None:
    _edit_dataset(library, lambda d: d["exchanges"][0].update(unit="m3"))
    report = _build(library, tmp_path / "out")
    assert any("mapped to 'water' in kilogram, but the exchange is in cubic meter" in e for e in report.errors)


def test_mappings_are_validated(library: Path, tmp_path: Path) -> None:
    path = library / "lci" / "mappings.yaml"
    data = yaml.safe_load(path.read_text())
    data["technosphere"]["water"]["activity"]["unit"] = "kg"
    path.write_text(yaml.safe_dump(data))
    report = _build(library, tmp_path / "out")
    assert any("technosphere/water/activity/unit" in e for e in report.errors)


@pytest.mark.parametrize("path", [KIT / "lci" / "mappings.yaml", LIBRARY / "lci" / "mappings.yaml"], ids=["staged", "fixture"])
def test_mapping_files_load(path: Path) -> None:
    mappings = build_lci.load_mappings(path)
    assert mappings["default_site_location"]


def test_cli(library: Path, tmp_path: Path, capsys) -> None:
    assert build_lci.main(["--library", str(library), "--out", str(tmp_path / "out"), "--version", "1.2.3"]) == 0
    assert "3 activities from 2 process(es)" in capsys.readouterr().out
    assert (tmp_path / "out" / "lci" / "cheme-as-code-atlas-1.2.3.xlsx").is_file()
    assert build_lci.main(["--library", str(library), "--out", str(tmp_path / "x"), "--version", "bad/version"]) == 1


def test_public_build_exports_only_published_processes(library: Path, tmp_path: Path) -> None:
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture", public=True)
    assert report.errors == []
    index = _json(tmp_path / "out" / "lci" / "index.json")
    assert sorted(index["processes"]) == ["fixture-electrolysis"]  # fixture-ammonia is internal
    package = _json(tmp_path / "out" / "lci" / "datapackage.json")
    assert [p["id"] for p in package["processes"]] == ["fixture-electrolysis"]
    # the LCI carries no factors: placeholder factors stay a caveat, as in the preview build
    assert any("placeholders" in c and c.startswith("fixture-electrolysis") for c in index["caveats"])
    names = {a["name"] for a in _activities(tmp_path / "out" / "lci" / f"{DB}.xlsx").values()}
    assert not any("mmonia" in name for name in names)


def test_public_build_without_public_processes_writes_an_empty_database(library: Path, tmp_path: Path, capsys) -> None:
    path = library / "processes" / "fixture-electrolysis" / "process.yaml"
    path.write_text(path.read_text().replace("status: public", "status: candidate"))
    assert build_lci.main(["--library", str(library), "--out", str(tmp_path / "out"), "--public"]) == 0
    assert "from 0 process(es)" in capsys.readouterr().out


def test_a_second_atlas_producer_is_reported_not_chosen_silently(library: Path, tmp_path: Path) -> None:
    # a second hydrogen producer beside fixture-electrolysis: the ammonia input has two
    source = library / "processes" / "fixture-electrolysis"
    twin = library / "processes" / "fixture-electrolysis-b"
    shutil.copytree(source, twin)
    for rel in ("process.yaml", "lca/dataset.yaml"):
        path = twin / rel
        path.write_text(path.read_text().replace("id: fixture-electrolysis", "id: fixture-electrolysis-b"))
    manifest = twin / "process.yaml"  # a second process of the same title would not be installable
    manifest.write_text(manifest.read_text().replace("Fixture: water electrolysis", "Fixture: water electrolysis B", 1))
    report = _build(library, tmp_path / "out")
    assert report.errors == [], report.errors
    (warning,) = [w for w in report.warnings if "several Atlas producers" in w]
    assert "fixture-ammonia" in warning and "fixture-electrolysis-b:" in warning


# --- cut-off criteria (docs/system-model.md section 4, core#180) -------------------------------
# The fixture electrolysis has 750.6 kg of operation inputs in kg (feed and resource water) per
# its basis, so 1 % is about 7.5 kg. The cut flows below are test data, not real inventories.

LUBE = {"key": "aux:lubricant", "amount": 2.0, "unit": "kg", "reason": "test: below the mass rule"}

# The criteria are core's (lca.cutoff). CI installs core and sets ATLAS_REQUIRE_CORE, so a missing
# core fails there instead of skipping.
try:
    import chemeascode.domains.assessment.lca.cutoff as core_cutoff
except ImportError:
    if os.environ.get("ATLAS_REQUIRE_CORE"):
        raise
    core_cutoff = None
needs_core = pytest.mark.skipif(core_cutoff is None, reason="needs cheme-as-code (core's lca.cutoff)")


def _cut(library: Path, *flows: dict) -> None:
    _edit_dataset(library, lambda d: d.update(cutoff=[dict(f) for f in flows]))


def _cutoff_entry(out: Path) -> dict | None:
    package = _json(out / "lci" / "datapackage.json")
    electrolysis = next(p for p in package["processes"] if p["id"] == "fixture-electrolysis")
    return electrolysis["datasets"][0].get("cutoff")


def test_datasets_without_cut_flows_record_no_cutoff_entry(library: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert _build(library, out).warnings == []
    assert _cutoff_entry(out) is None


@needs_core
def test_cut_flows_within_the_criteria_are_recorded(library: Path, tmp_path: Path) -> None:
    _cut(library, LUBE, {"key": "aux:sealant", "reason": "test: amount not known"})
    out = tmp_path / "out"
    report = _build(library, out)
    assert report.errors == [] and report.warnings == []
    entry = _cutoff_entry(out)
    assert entry["checked"] is True and entry["flows"] == ["aux:lubricant", "aux:sealant"]
    assert entry["input_mass_kg"] == pytest.approx(752.6)  # the cut input counts in the basis
    assert [f["rule"] for f in entry["findings"]] == ["cheme.lca-cutoff-unchecked"]  # info, not a warning


@needs_core
@pytest.mark.parametrize(
    ("flows", "rule"),
    [
        ([{**LUBE, "amount": 10.0}], "cheme.lca-cutoff-share"),
        ([{**LUBE, "amount": 5.0}, {**LUBE, "key": "aux:grease", "amount": 5.0}], "cheme.lca-cutoff-sum"),
        ([{"key": "aux:catalyst", "amount": 0.001, "unit": "kg", "reason": "test", "catalyst": True, "contains": ["Pt"]}], "cheme.lca-cutoff-never"),
        ([{"key": "emission:N2O", "direction": "output", "amount": 0.001, "unit": "kg", "reason": "test", "cas": "10024-97-2"}], "cheme.lca-cutoff-never"),
    ],
    ids=["share", "sum", "precious-metal-catalyst", "high-cf"],
)
def test_broken_cutoff_criteria_are_warnings(library: Path, tmp_path: Path, flows, rule) -> None:
    _cut(library, *flows)
    out = tmp_path / "out"
    report = _build(library, out)
    assert report.errors == []
    assert any("fixture-electrolysis/lca/dataset.yaml: cutoff:" in w and rule in w for w in report.warnings), report.warnings
    assert rule in [f["rule"] for f in _cutoff_entry(out)["findings"]]


@needs_core
def test_a_cut_flow_failing_cores_schema_is_an_error(library: Path, tmp_path: Path) -> None:
    _cut(library, {"key": "aux:lubricant", "amount": 2.0})  # no reason
    report = _build(library, tmp_path / "out")
    assert any("fixture-electrolysis/lca/dataset.yaml: cutoff[0].reason:" in e for e in report.errors), report.errors
    assert not (tmp_path / "out" / "lci").exists()


def test_without_core_the_cutoff_criteria_are_not_checked(library: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "chemeascode.domains.assessment.lca.cutoff", None)  # import raises ImportError
    _cut(library, LUBE)
    out = tmp_path / "out"
    report = _build(library, out)
    assert report.errors == []
    assert any("cut-off criteria are not checked" in w for w in report.warnings), report.warnings
    assert _cutoff_entry(out) == {"flows": ["aux:lubricant"], "checked": False, "findings": []}


# --- mapping gaps of unpublished processes, per-process overrides (ADR 0022) -----------------

AMMONIA = "processes/fixture-ammonia/lca/datasets/ammonia.yaml"
OVERRIDES = "processes/fixture-ammonia/lca/mappings.yaml"


def _unmapped_feed_and_emission(library: Path) -> None:
    """fixture-ammonia (internal: no publication status) gets a feed and an emission that
    nothing maps."""
    path = library / AMMONIA
    data = yaml.safe_load(path.read_text())
    data["exchanges"].append({"key": "feed:CATALYST", "title": "Iron catalyst", "type": "input", "amount": 0.2, "unit": "kg"})
    data["exchanges"].append({"key": "emission:XE", "title": "Xenon", "type": "emission", "amount": 0.01, "unit": "kg"})
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _overrides(library: Path, exchanges: dict) -> None:
    (library / OVERRIDES).write_text(yaml.safe_dump({"schema": "cheme-as-code/lci-process-mappings/v1", "exchanges": exchanges}))


def _walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def test_an_internal_process_builds_strictly_with_its_gaps_unlinked(library: Path, tmp_path: Path, capsys) -> None:
    _unmapped_feed_and_emission(library)
    out = tmp_path / "out"
    assert build_lci.main(["--library", str(library), "--out", str(out), "--version", "0.1.0", "--strict"]) == 0
    printed = capsys.readouterr()
    assert f"gap: fixture-ammonia: {AMMONIA} feed:CATALYST: no mapping" in printed.err
    assert f"gap: fixture-ammonia: {AMMONIA} emission:XE: emission of XE (fossil) has no biosphere3 flow identity" in printed.err
    assert "2 mapping gap(s) in 1 unpublished process(es)" in printed.out

    report = build_lci.build(library, tmp_path / "again", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    assert [(g["process"], g["key"], g["link"]) for g in report.gaps] == [("fixture-ammonia", "feed:CATALYST", "technosphere"), ("fixture-ammonia", "emission:XE", "biosphere")]

    # the gaps file and the datapackage list them per process
    gaps = _json(out / "lci" / "gaps.json")
    assert gaps["schema"] == "cheme-as-code/lci-gaps/v1" and gaps["count"] == 2
    assert [(g["key"], g["link"], g["path"]) for g in gaps["processes"]["fixture-ammonia"]] == [("feed:CATALYST", "technosphere", AMMONIA), ("emission:XE", "biosphere", AMMONIA)]
    index = _json(out / "lci" / "index.json")
    assert index["gaps"] == {"fixture-ammonia": 2} and "gaps.json" in [f["name"] for f in index["files"]]
    assert any("mapping gaps" in c for c in index["caveats"])
    package = _json(out / "lci" / "datapackage.json")
    assert [g["key"] for g in next(p for p in package["processes"] if p["id"] == "fixture-ammonia")["gaps"]] == ["feed:CATALYST", "emission:XE"]
    assert next(p for p in package["processes"] if p["id"] == "fixture-electrolysis")["gaps"] == []
    page = next(a for a in package["activities"] if a["code"] == NH3)
    assert {e["key"] for e in page["exchanges"] if "gap" in e} == {"feed:CATALYST", "emission:XE"}

    # in the workbook: exported, with their amounts, unlinked (no database, no categories, no
    # reference product, no Atlas alternative) and marked; nothing zero-filled or dropped
    ammonia = _activities(out / "lci" / f"{DB}.xlsx")[NH3]
    feed, emission = _exchange(ammonia, "feed:CATALYST"), _exchange(ammonia, "emission:XE")
    assert (feed["type"], feed["amount"], feed["unit"]) == ("technosphere", pytest.approx(0.2 / 1000), "kilogram")
    assert (emission["type"], emission["amount"], emission["unit"]) == ("biosphere", pytest.approx(0.01 / 1000), "kilogram")
    for entry in (feed, emission):
        assert entry["atlas gap"].startswith("unlinked, no ")
        assert not {"database", "categories", "reference product", "location", "atlas activity", "atlas flow uuid"} & set(entry)
    assert ammonia["meta"]["atlas gaps"] == 2 and "UNLINKED (mapping gaps" in ammonia["meta"]["comment"]
    # the other activities are untouched
    assert "atlas gaps" not in _activities(out / "lci" / f"{DB}.xlsx")[H2]["meta"]

    # the other formats carry the gaps flagged, never linked
    import zipfile
    with zipfile.ZipFile(out / "lci" / f"{DB}-olca-jsonld.zip") as package_zip:
        members = {n: json.loads(package_zip.read(n)) for n in package_zip.namelist() if n.endswith(".json")}
    flows = [m for n, m in members.items() if n.startswith("flows/") and m.get("category") == "ChemE-as-Code Atlas/unlinked (mapping gaps)"]
    assert sorted(f["name"] for f in flows) == ["CATALYST", "XE"]
    process = next(m for n, m in members.items() if n.startswith("processes/") and "fixture-ammonia" in json.dumps(m) and "CATALYST" in json.dumps(m))
    gap_ids = {f["@id"] for f in flows}
    assert all(e.get("defaultProvider") is None for e in process["exchanges"] if e["flow"]["@id"] in gap_ids)
    assert "UNLINKED" in json.dumps(process)
    multifunctional = _json(out / "lci" / f"{DB}-multifunctional.json")
    marked = [e for e in _walk(multifunctional) if "atlas gap" in e]
    assert sorted(e["atlas key"] for e in marked) == ["emission:XE", "feed:CATALYST"]
    assert not any({"database", "atlas code", "atlas activity code"} & set(e) for e in marked)


def test_the_same_gaps_fail_a_public_process(library: Path, tmp_path: Path) -> None:
    _unmapped_feed_and_emission(library)
    manifest = library / "processes" / "fixture-ammonia" / "process.yaml"
    data = yaml.safe_load(manifest.read_text())
    data["publication"] = {"status": "public", "license": "CC-BY-4.0"}
    manifest.write_text(yaml.safe_dump(data, sort_keys=False))
    assert build_lci.main(["--library", str(library), "--out", str(tmp_path / "out"), "--strict"]) == 1
    for public in (False, True):
        report = build_lci.build(library, tmp_path / f"out-{public}", "0.1.0", commit="fixture", public=public)
        assert report.gaps == []
        assert any(f"{AMMONIA} feed:CATALYST: no mapping" in e for e in report.errors)
        assert any(f"{AMMONIA} emission:XE: emission of XE (fossil) has no biosphere3 flow identity" in e for e in report.errors)
        assert not (tmp_path / f"out-{public}" / "lci").exists()


def test_a_process_override_is_applied(library: Path, tmp_path: Path) -> None:
    _unmapped_feed_and_emission(library)
    _overrides(library, {"feed:CATALYST": {"use": "steel-sections", "source": "test: the catalyst as steel"}, "feed:nitrogen": {"atlas": False}})
    report = _build(library, tmp_path / "out")
    assert report.errors == [] and [g["key"] for g in report.gaps] == ["emission:XE"]
    ammonia = _activities(tmp_path / "out" / "lci" / f"{DB}.xlsx")[NH3]
    shared = build_lci.load_mappings(library / "lci" / "mappings.yaml")
    assert _exchange(ammonia, "feed:CATALYST")["name"] == shared["technosphere"]["steel-sections"]["activity"]["name"]
    assert "atlas gap" not in _exchange(ammonia, "feed:CATALYST")


def test_an_exchange_overridden_in_both_files_is_an_error(library: Path, tmp_path: Path) -> None:
    _overrides(library, {"feed:nitrogen": {"atlas": False}})
    path = library / "lci" / "mappings.yaml"
    data = yaml.safe_load(path.read_text())
    data["exchanges"] = {"fixture-ammonia/feed:nitrogen": {"atlas": False}}
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    report = _build(library, tmp_path / "out")
    assert report.errors == [f"{OVERRIDES}: exchanges.feed:nitrogen is also overridden in lci/mappings.yaml (exchanges.fixture-ammonia/feed:nitrogen): keep one, in this file"]
    assert not (tmp_path / "out" / "lci").exists()


@pytest.mark.parametrize(
    ("exchanges", "message"),
    [
        ({"feed:nitrogen": {"atlas": False, "colour": "red"}}, "exchanges/feed:nitrogen: Additional properties are not allowed ('colour' was unexpected)"),
        ({"fixture-ammonia/feed:nitrogen": {"atlas": False}}, "exchanges: 'fixture-ammonia/feed:nitrogen' does not match"),
        ({"feed:nitrogen": {}}, "exchanges/feed:nitrogen: {} should be non-empty"),
    ],
)
def test_a_process_mappings_file_is_validated_with_its_path(library: Path, tmp_path: Path, exchanges, message) -> None:
    _overrides(library, exchanges)
    report = _build(library, tmp_path / "out")
    assert any(e.startswith(f"{OVERRIDES}: ") and message in e for e in report.errors), report.errors
    assert not (tmp_path / "out" / "lci").exists()


@pytest.mark.parametrize("path", sorted(KIT.glob("processes/*/lca/mappings.yaml")), ids=lambda p: p.parents[1].name)
def test_process_mapping_files_are_valid(path: Path) -> None:
    assert build_lci._schema_problems(yaml.safe_load(path.read_text()), "lci-process-mappings.schema.json") == []
