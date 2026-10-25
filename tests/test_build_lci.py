"""LCI builder without Brightway: workbook layout, determinism, allocation, linking, errors."""

from __future__ import annotations

import hashlib
import json
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
    assert sorted(p.name for p in (out / "lci").iterdir()) == [f"{DB}.xlsx", "datapackage.json", "index.json"]

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
    assert sorted(activities) == sorted([H2, H2.replace(":H2", ":O2"), NH3])
    for activity in activities.values():
        production = [e for e in activity["exchanges"] if e["type"] == "production"]
        assert len(production) == 1 and production[0]["amount"] == 1
        assert production[0]["name"] == activity["name"]
        assert production[0]["reference product"] == activity["meta"]["reference product"]
        assert set().union(*activity["exchanges"]) <= set(build_lci.EXCHANGE_COLUMNS)
        assert "Allocation:" in activity["meta"]["comment"]


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


def test_inputs_made_by_another_atlas_process_name_it(library: Path, tmp_path: Path) -> None:
    _build(library, tmp_path / "out")
    hydrogen = _exchange(_activities(tmp_path / "out" / "lci" / f"{DB}.xlsx")[NH3], "feed:hydrogen")
    assert hydrogen["name"] == "market for hydrogen, gaseous"  # background by default
    assert hydrogen["atlas activity"] == "Fixture: water electrolysis"
    assert hydrogen["atlas reference product"] == "Hydrogen at 30 bar"


# --- ASU-1 (real dataset, staged mappings) ----------------------------------------------------


def test_asu_exports_four_exergy_allocated_activities(tmp_path: Path) -> None:
    library = tmp_path / "library"
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
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
        (lambda d: d["exchanges"][0].update(unit="Nm3"), "unit Nm3: a gas volume at a reference state has no Brightway unit"),
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
