"""The LCI export reads core's dataset contract v2 (core#294): schema id, units, resources and
elementary flows by biosphere3 UUID, pedigree and its lognormal, carriers and product state,
the dataset's own version, review, system model, deviation and successor, and the data quality
rating of lca/manifest.json. The v1 files are still read (tests/fixtures/asu-lca)."""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
openpyxl = pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_lci  # noqa: E402

LIBRARY = KIT / "tests" / "fixtures" / "library"
DB = "cheme-as-code-atlas-0.1.0"
H2 = "fixture-electrolysis:fixture-electrolysis:product:H2"
WATER_RIVER = "8c75e7ab-8ab8-41e4-b394-c166ff5b050d"
SHARE = 41.7 / (41.7 + 333.6)


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    return copy


def _dataset_path(library: Path) -> Path:
    return library / "processes" / "fixture-electrolysis" / "lca" / "dataset.yaml"


def _edit(library: Path, change) -> None:
    path = _dataset_path(library)
    data = yaml.safe_load(path.read_text())
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _build(library: Path, tmp_path: Path, **kwargs) -> build_lci.Report:
    return build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture", **kwargs)


def _package(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "out" / "lci" / "datapackage.json").read_text(encoding="utf-8"))


def _dataset_entry(tmp_path: Path, dataset: str = "fixture-electrolysis") -> dict:
    return next(d for p in _package(tmp_path)["processes"] for d in p["datasets"] if d["id"] == dataset)


def _activities(tmp_path: Path) -> dict[str, dict]:
    return build_lci.read_workbook(tmp_path / "out" / "lci" / f"{DB}.xlsx")


def _exchange(activity: dict, key: str) -> dict:
    return next(e for e in activity["exchanges"] if e.get("atlas key") == key)


def _ex(key: str, unit: str = "kg", amount: float = 1.0, **more) -> dict:
    return {"key": key, "type": "input", "amount": amount, "unit": unit, **more}


# --- schema ids -------------------------------------------------------------------------------


def test_v2_datasets_build_without_findings(library: Path, tmp_path: Path) -> None:
    assert _dataset_path(library).read_text().split("\nschema: ")[1].startswith("cheme/lci_dataset/v2")
    report = _build(library, tmp_path)
    assert (report.errors, report.warnings) == ([], [])


def test_v1_datasets_are_still_read(library: Path, tmp_path: Path) -> None:
    for schema in ("cheme/lca/v1", "plantcode/lca/v1"):
        _edit(library, lambda d, schema=schema: d.update(schema=schema))
        assert _build(library, tmp_path).errors == []


def test_an_unknown_schema_is_refused_with_the_known_ones(library: Path, tmp_path: Path) -> None:
    _edit(library, lambda d: d.update(schema="cheme/lci_dataset/v3"))
    errors = _build(library, tmp_path).errors
    assert any("cheme/lci_dataset/v3" in e and "cheme/lci_dataset/v2" in e for e in errors), errors


# --- units ------------------------------------------------------------------------------------


def test_units_are_brought_to_the_units_the_export_counts_in(library: Path, tmp_path: Path) -> None:
    def change(d):
        d["exchanges"][0].update(amount=375300.0, unit="g")  # feed:WATER, 375.3 kg
        d["exchanges"][1].update(amount=2293.5 / 1000, unit="MWh")  # feed:POWER
        d["exchanges"][-1].update(amount=0.5 / 1000, unit="t")  # construction:steel, 0.5 kg

    _edit(library, change)
    assert _build(library, tmp_path).errors == []
    h2 = _activities(tmp_path)[H2]
    assert _exchange(h2, "feed:WATER")["amount"] == pytest.approx(375.3 * SHARE / 41.7)
    assert _exchange(h2, "feed:POWER")["amount"] == pytest.approx(2293.5 * SHARE / 41.7)
    assert _exchange(h2, "construction:steel")["amount"] == pytest.approx(0.5 * SHARE / 41.7)
    assert _exchange(h2, "feed:POWER")["unit"] == "kilowatt hour"


def test_a_unit_the_mapping_does_not_count_in_is_an_error_not_a_conversion(library: Path, tmp_path: Path) -> None:
    _edit(library, lambda d: d["exchanges"][1].update(amount=2293.5 * 3.6, unit="MJ"))  # feed:POWER is linked in kWh
    errors = _build(library, tmp_path).errors
    assert any("feed:POWER" in e and "in kilowatt hour, but the exchange is in megajoule" in e for e in errors), errors


def test_the_content_hash_is_that_of_the_dataset_as_written(library: Path, tmp_path: Path) -> None:
    _build(library, tmp_path)
    before = _dataset_entry(tmp_path)["content_sha256"]
    _edit(library, lambda d: d["exchanges"][0].update(amount=375300.0, unit="g"))
    _build(library, tmp_path)
    assert _dataset_entry(tmp_path)["content_sha256"] != before


@pytest.mark.parametrize("unit", ["Nm3", "Sm3", "ea*h", "ea*a"])
def test_units_without_a_brightway_counterpart_are_refused_with_the_reason(library: Path, tmp_path: Path, unit: str) -> None:
    _edit(library, lambda d: d["exchanges"][0].update(unit=unit))
    errors = _build(library, tmp_path).errors
    assert any(f"feed:WATER: unit {unit}:" in e and "state the" in e for e in errors), errors


def test_land_occupation_and_radioactivity_have_biosphere_units() -> None:
    assert build_lci.BW_UNITS[build_lci.UNIT_SCALING["m2*a"][0]] == "square meter-year"
    assert build_lci.BW_UNITS[build_lci.UNIT_SCALING["kBq"][0]] == "kilo Becquerel"
    assert build_lci.UNIT_SCALING["m2*year"] == ("m2*a", 1.0)  # how the crosswalk names biosphere3's unit
    assert set(build_lci.UNIT_SCALING) | set(build_lci.UNSUPPORTED_UNITS) >= {
        "kg", "g", "t", "kWh", "MWh", "MJ", "GJ", "m", "km", "m2", "m2*a", "m3", "L", "Nm3", "Sm3", "ea", "ea*h", "ea*a", "tkm", "kBq"
    }  # every unit of core's LCI_UNITS is mapped or refused


# --- elementary flows --------------------------------------------------------------------------


def test_a_resource_is_a_biosphere_exchange_by_its_biosphere3_uuid(library: Path, tmp_path: Path) -> None:
    assert _build(library, tmp_path).errors == []
    water = _exchange(_activities(tmp_path)[H2], "resource:WATER")
    assert water["type"] == "biosphere"
    assert (water["name"], water["categories"], water["unit"]) == ("Water, river", "natural resource::in water", "cubic meter")
    assert water["atlas flow uuid"] == WATER_RIVER
    assert water["amount"] == pytest.approx(375.3 * 0.001 * SHARE / 41.7)  # kg -> m3 by the identity's per_unit


def test_a_curated_entry_keyed_by_the_uuid_corrects_the_name(library: Path, tmp_path: Path) -> None:
    mappings = yaml.safe_load((library / "lci" / "mappings.yaml").read_text())
    mappings["biosphere"][WATER_RIVER] = {"flow": {"name": "Water, river (renamed)", "categories": ["natural resource", "in water"]}, "source": "test"}
    (library / "lci" / "mappings.yaml").write_text(yaml.safe_dump(mappings, sort_keys=False))
    assert _build(library, tmp_path).errors == []
    water = _exchange(_activities(tmp_path)[H2], "resource:WATER")
    assert (water["name"], water["atlas flow uuid"]) == ("Water, river (renamed)", WATER_RIVER)


def test_the_flow_identity_wins_over_the_component_mapping(library: Path, tmp_path: Path) -> None:
    flow = [{"list": "biosphere3", "uuid": "0795345f-c7ae-410c-ad25-1845784c75f5", "name": "Methane, fossil", "categories": ["air"], "unit": "kg"}]
    _edit(library, lambda d: next(e for e in d["exchanges"] if e["key"] == "emission:H2").update(flow=flow))
    assert _build(library, tmp_path).errors == []
    emission = _exchange(_activities(tmp_path)[H2], "emission:H2")
    assert (emission["name"], emission["atlas flow uuid"]) == ("Methane, fossil", "0795345f-c7ae-410c-ad25-1845784c75f5")


def test_an_emission_by_component_carries_the_uuid_of_the_curated_entry(library: Path, tmp_path: Path) -> None:
    mappings = yaml.safe_load((library / "lci" / "mappings.yaml").read_text())
    mappings["biosphere"]["H2"]["flow"]["uuid"] = "0795345f-c7ae-410c-ad25-1845784c75f5"
    (library / "lci" / "mappings.yaml").write_text(yaml.safe_dump(mappings, sort_keys=False))
    assert _build(library, tmp_path).errors == []
    assert _exchange(_activities(tmp_path)[H2], "emission:H2")["atlas flow uuid"] == "0795345f-c7ae-410c-ad25-1845784c75f5"


def test_a_resource_with_no_identity_and_no_mapping_is_an_error_naming_both(library: Path, tmp_path: Path) -> None:
    _edit(library, lambda d: next(e for e in d["exchanges"] if e["key"] == "resource:WATER").pop("flow"))
    errors = _build(library, tmp_path).errors
    assert any("resource:WATER" in e and "no biosphere3 flow identity" in e and "biosphere" in e for e in errors), errors


def test_a_malformed_identity_or_pedigree_is_refused(library: Path, tmp_path: Path) -> None:
    def change(d):
        water = next(e for e in d["exchanges"] if e["key"] == "resource:WATER")
        water["flow"][1]["uuid"] = "not-a-uuid"
        water["pedigree"]["scores"] = [1, 2, 3]

    _edit(library, change)
    errors = _build(library, tmp_path).errors
    assert any("flow[1].uuid 'not-a-uuid'" in e and "pedigree.scores" in e for e in errors), errors


# --- pedigree ---------------------------------------------------------------------------------


def test_pedigree_gsd2_follows_ciroth_et_al_2016() -> None:
    assert build_lci.pedigree_gsd2([1, 1, 1, 1, 1], 1.05) == pytest.approx(1.05)
    terms = [math.log(1.05) ** 2, math.log(1.69) ** 2, math.log(1.03) ** 2, math.log(1.03) ** 2, math.log(1.11) ** 2, math.log(1.65) ** 2]
    assert build_lci.pedigree_gsd2([4, 2, 2, 5, 3], 1.05) == pytest.approx(math.exp(math.sqrt(sum(terms))))


def test_the_pedigree_is_exported_with_its_lognormal(library: Path, tmp_path: Path) -> None:
    assert _build(library, tmp_path).errors == []
    water = _exchange(_activities(tmp_path)[H2], "resource:WATER")
    gsd2 = build_lci.pedigree_gsd2([4, 3, 1, 5, 3], 1.05)
    assert water["atlas pedigree"] == "4,3,1,5,3"
    assert water["uncertainty type"] == 2
    assert water["loc"] == pytest.approx(math.log(water["amount"]))
    assert water["scale"] == pytest.approx(math.log(gsd2) / 2)
    # the exchange's own gsd2 wins over its pedigree; one without either has no distribution
    steel = _exchange(_activities(tmp_path)[H2], "construction:steel")
    assert steel["scale"] == pytest.approx(math.log(1.21) / 2) and "atlas pedigree" not in steel
    assert "uncertainty type" not in _exchange(_activities(tmp_path)[H2], "feed:WATER")


def test_a_basic_uncertainty_is_the_floor_of_the_pedigree_lognormal(library: Path, tmp_path: Path) -> None:
    _edit(library, lambda d: next(e for e in d["exchanges"] if e["key"] == "resource:WATER").update(basic_uncertainty=1.5))
    _build(library, tmp_path)
    water = _exchange(_activities(tmp_path)[H2], "resource:WATER")
    assert water["scale"] == pytest.approx(math.log(build_lci.pedigree_gsd2([4, 3, 1, 5, 3], 1.5)) / 2)


# --- carriers and product state -----------------------------------------------------------------


def test_carrier_and_product_state_are_written(library: Path, tmp_path: Path) -> None:
    def change(d):
        next(e for e in d["exchanges"] if e["key"] == "feed:POWER")["carrier"] = {"kind": "electricity", "temperature": 25}
        next(e for e in d["exchanges"] if e["key"] == "emission:H2")["carrier"] = {"kind": "fuel", "lhv": 120.0}

    _edit(library, change)
    assert _build(library, tmp_path).errors == []
    h2 = _activities(tmp_path)[H2]
    assert _exchange(h2, "feed:POWER")["atlas carrier"] == "electricity, 25 degC"
    assert _exchange(h2, "emission:H2")["atlas carrier"] == "fuel, LHV 120 MJ/kg"
    assert h2["meta"]["atlas product state"] == "gas, 30 bar(a), 99.99 % H2 (mole)"
    assert "Product state: gas, 30 bar(a)" in h2["meta"]["comment"]
    activities = {a["code"]: a for p in _package(tmp_path)["processes"] for a in p["activities"]}
    assert activities[H2]["state"] == "gas, 30 bar(a), 99.99 % H2 (mole)"
    assert "state" not in activities[H2.replace(":H2", ":O2")]


# --- dataset metadata ---------------------------------------------------------------------------


def test_the_datasets_own_metadata_is_recorded(library: Path, tmp_path: Path) -> None:
    def change(d):
        d.update(
            version="2.1.0", methodology_version="0.9.0", valid_until=2030, technology_level="pilot",
            classification={"isic": "2011", "cpc": "34110"},
            review=[{"type": "internal", "reviewer": "test"}, {"type": "independent-external", "reviewer": "someone", "date": "2026-10-01"}],
        )

    _edit(library, change)
    report = _build(library, tmp_path)
    assert (report.errors, report.warnings) == ([], [])
    entry = _dataset_entry(tmp_path)
    assert (entry["version"], entry["version_source"]) == ("2.1.0", "dataset")
    assert (entry["methodology_version"], entry["methodology_version_source"]) == ("0.9.0", "dataset")
    assert (entry["system_model"], entry["valid_until"]) == ("cutoff", 2030)
    assert entry["review"]["status"] == "independent-external" and len(entry["review"]["records"]) == 2
    assert entry["documentation"]["technology_level"] == "pilot" and entry["documentation"]["classification"]["cpc"] == "34110"
    assert entry["documentation"]["uuid"] == "5b0c1a52-2f0e-5a7e-9d3a-0c3c6c1f7a10"
    other = _dataset_entry(tmp_path, "fixture-ammonia-hb")  # states none: the build's, unreviewed
    assert (other["methodology_version"], other["methodology_version_source"]) == (build_lci.METHODOLOGY_VERSION, "build")
    assert other["review"] == {"status": "unreviewed"} and other["system_model"] is None and other["data_quality"] is None


@pytest.mark.parametrize("value", ["unreviewed", "none", None, [{"type": "none"}]])
def test_an_unreviewed_dataset_is_unreviewed_in_every_spelling(value) -> None:
    assert build_lci._review(value) == {"status": "unreviewed"}


def test_the_system_model_of_a_dataset_must_fit_the_build(library: Path, tmp_path: Path) -> None:
    _edit(library, lambda d: d.update(system_model="consequential"))
    errors = _build(library, tmp_path).errors
    assert any("system_model 'consequential' does not fit the cutoff build" in e for e in errors), errors
    _edit(library, lambda d: d.update(system_model="substitution"))
    assert any("does not fit the cutoff build" in e for e in _build(library, tmp_path).errors)
    assert _build(library, tmp_path, system_model="substitution").errors == []
    _edit(library, lambda d: d.update(system_model="cutoff"))
    assert _build(library, tmp_path, system_model="substitution").errors == []


# --- allocation deviation -----------------------------------------------------------------------


def test_a_deviation_in_the_dataset_is_accepted_without_a_curated_rule(library: Path, tmp_path: Path) -> None:
    # synthetic prices ratio 4: the hierarchy gives mass; the study (lca.yaml) is the base, so its
    # deviation, or else the dataset's, justifies keeping another method
    study = library / "processes" / "fixture-electrolysis" / "lca" / "lca.yaml"
    data = yaml.safe_load(study.read_text())
    data["allocation"].update(method="economic", deviation="test: a sector agreement prescribes economic allocation")
    study.write_text(yaml.safe_dump(data, sort_keys=False))
    report = _build(library, tmp_path)
    assert report.errors == [] and not [w for w in report.warnings if ": allocation:" in w]  # no finding
    entry = _dataset_entry(tmp_path)["allocation"]
    assert (entry["method"], entry["rule"], entry["follows_hierarchy"]) == ("economic", "deviation", True)
    assert entry["reason"] == "test: a sector agreement prescribes economic allocation"


def test_a_deviation_in_the_dataset_when_the_study_has_none(library: Path, tmp_path: Path) -> None:
    study = library / "processes" / "fixture-electrolysis" / "lca" / "lca.yaml"
    data = yaml.safe_load(study.read_text())
    del data["allocation"]
    study.write_text(yaml.safe_dump(data, sort_keys=False))
    _edit(library, lambda d: d.update(allocation={"method": "economic", "prices": {"H2": 2.0, "O2": 0.5}, "deviation": "test: sector agreement"}))
    assert _build(library, tmp_path).warnings == []
    assert _dataset_entry(tmp_path)["allocation"]["rule"] == "deviation"


def test_without_a_deviation_the_hierarchy_still_overrules_the_method(library: Path, tmp_path: Path) -> None:
    study = library / "processes" / "fixture-electrolysis" / "lca" / "lca.yaml"
    data = yaml.safe_load(study.read_text())
    data["allocation"]["method"] = "economic"
    study.write_text(yaml.safe_dump(data, sort_keys=False))
    report = _build(library, tmp_path)
    assert any("allocation.deviation" in w and "mass is exported" in w for w in report.warnings), report.warnings
    assert _dataset_entry(tmp_path)["allocation"]["method"] == "mass"


# --- superseded datasets ------------------------------------------------------------------------


def _with_successor(library: Path) -> None:
    """The electrolysis dataset 0.1.0 is superseded by a copy of it, 0.2.0, in the same process."""
    folder = library / "processes" / "fixture-electrolysis" / "lca" / "datasets"
    folder.mkdir()
    new = yaml.safe_load(_dataset_path(library).read_text())
    new.update(id="fixture-electrolysis-2", version="0.2.0", title="Fixture: water electrolysis, revised")
    (folder / "revised.yaml").write_text(yaml.safe_dump(new, sort_keys=False))
    _edit(library, lambda d: d.update(version="0.1.0", superseded_by={"id": "fixture-electrolysis-2", "version": "0.2.0"}))


def test_a_superseded_dataset_stays_resolvable_with_a_pointer(library: Path, tmp_path: Path) -> None:
    _with_successor(library)
    report = _build(library, tmp_path)
    assert report.errors == []
    old, new = _dataset_entry(tmp_path), _dataset_entry(tmp_path, "fixture-electrolysis-2")
    assert old["deprecated"] is True and new["deprecated"] is False and new["superseded_by"] is None
    new_h2 = "fixture-electrolysis:fixture-electrolysis-2:product:H2"
    assert old["superseded_by"] == {
        "id": "fixture-electrolysis-2", "version": "0.2.0", "process": "fixture-electrolysis", "resolved": True,
        "activities": [new_h2, new_h2.replace(":H2", ":O2")],
    }
    activities = _activities(tmp_path)
    assert H2 in activities and new_h2 in activities  # the deprecated activity is still in the database
    assert activities[H2]["meta"]["atlas superseded by"] == new_h2
    assert "DEPRECATED: superseded by " + new_h2 in activities[H2]["meta"]["comment"]
    assert "atlas superseded by" not in activities[new_h2]["meta"]
    listed = {a["code"]: a for p in _package(tmp_path)["processes"] for a in p["activities"]}
    assert listed[H2]["superseded_by"] == new_h2 and "superseded_by" not in listed[new_h2]


def test_a_dataset_is_linked_to_a_current_producer_before_a_deprecated_one(library: Path, tmp_path: Path) -> None:
    _with_successor(library)
    report = _build(library, tmp_path)
    assert report.errors == []
    hydrogen = _exchange(_activities(tmp_path)["fixture-ammonia:fixture-ammonia-hb:product:ammonia"], "feed:hydrogen")
    assert hydrogen["atlas activity"] == "Fixture: water electrolysis"  # both datasets make it
    assert any("several Atlas producers" in w and "fixture-electrolysis: Fixture: water electrolysis" in w for w in report.warnings)
    # the deprecated H2 activity is the one that is named as the alternative, not the one taken:
    # a build with the revised dataset's product only would take it
    taken = [w for w in report.warnings if "several Atlas producers" in w][0]
    assert "is used, not" in taken


def test_a_successor_that_is_not_in_the_build_is_a_warning_and_keeps_the_pointer(library: Path, tmp_path: Path) -> None:
    _edit(library, lambda d: d.update(superseded_by={"id": "elsewhere", "version": "1.0.0"}))
    report = _build(library, tmp_path)
    assert any("superseded_by elsewhere 1.0.0 is not a dataset of this build" in w for w in report.warnings), report.warnings
    old = _dataset_entry(tmp_path)
    assert old["superseded_by"]["resolved"] is False and old["superseded_by"]["activities"] == []
    assert _activities(tmp_path)[H2]["meta"]["atlas superseded by"] == "dataset elsewhere 1.0.0 (not in this build)"


def test_a_successor_at_another_version_is_a_warning(library: Path, tmp_path: Path) -> None:
    _with_successor(library)
    _edit(library, lambda d: d.update(superseded_by={"id": "fixture-electrolysis-2", "version": "0.3.0"}))
    assert any("but the build has version 0.2.0" in w for w in _build(library, tmp_path).warnings)


def test_a_dataset_cannot_supersede_itself(library: Path, tmp_path: Path) -> None:
    _edit(library, lambda d: d.update(version="0.1.0", superseded_by={"id": "fixture-electrolysis", "version": "0.1.0"}))
    assert any("names the dataset itself" in e for e in _build(library, tmp_path).errors)


# --- data quality rating ------------------------------------------------------------------------

RATING = {
    "TeR": 2.0, "GeR": 1.0, "TiR": 1.0, "dqr": 1.3333, "P": 3.0, "C": 3.0, "dqr_pef": 1.75, "primary_share": 0.0,
    "weighted": True, "basis": "climate-change", "weakest": "TeR", "exchanges": 6,
}


def test_the_rating_of_the_manifest_is_carried_into_the_datapackage(library: Path, tmp_path: Path) -> None:
    manifest = library / "processes" / "fixture-electrolysis" / "lca" / "manifest.json"
    manifest.write_text(json.dumps({"schema": "cheme/lca-manifest/v1", "data_quality": RATING}))
    assert _build(library, tmp_path).errors == []
    assert _dataset_entry(tmp_path)["data_quality"] == RATING
    assert _dataset_entry(tmp_path, "fixture-ammonia-hb")["data_quality"] is None  # a hand-written dataset has none


def test_a_manifest_without_a_rating_or_unreadable_gives_none(library: Path, tmp_path: Path) -> None:
    manifest = library / "processes" / "fixture-electrolysis" / "lca" / "manifest.json"
    manifest.write_text(json.dumps({"schema": "cheme/lca-manifest/v1"}))
    assert _build(library, tmp_path).errors == []
    assert _dataset_entry(tmp_path)["data_quality"] is None
    manifest.write_text("{not json")
    report = _build(library, tmp_path)
    assert report.errors == [] and any("lca/manifest.json: not valid JSON" in w for w in report.warnings)


# --- ASU-1, once its lca/ files are regenerated ---------------------------------------------------


def test_asu_1_regenerated_with_core_v2_builds_with_pedigree_and_flow_identities(tmp_path: Path) -> None:
    folder = KIT / "processes" / "asu-1" / "lca"
    if "cheme/lci_dataset/v2" not in (folder / "dataset.yaml").read_text():
        pytest.skip("processes/asu-1/lca is not regenerated with core's dataset contract v2 yet (separate PR after repos-6a merges)")
    library = tmp_path / "library"
    shutil.copytree(KIT / "processes" / "asu-1", library / "processes" / "asu-1")
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "chemicals" / "chemicals.yaml", library / "chemicals")
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="asu")
    assert report.errors == []
    exchanges = [e for a in _activities(tmp_path).values() for e in a["exchanges"]]
    assert any(e.get("atlas pedigree") for e in exchanges)


def test_two_activities_the_installer_cannot_tell_apart_are_an_error(library: Path, tmp_path: Path) -> None:
    folder = library / "processes" / "fixture-electrolysis" / "lca" / "datasets"
    folder.mkdir()
    twin = yaml.safe_load(_dataset_path(library).read_text())
    twin.update(id="fixture-electrolysis-twin")
    (folder / "twin.yaml").write_text(yaml.safe_dump(twin, sort_keys=False))
    errors = _build(library, tmp_path).errors
    assert any("fixture-electrolysis-twin:product:H2" in e and "cannot tell them apart" in e for e in errors), errors


def test_a_deprecated_activity_is_named_so_that_it_differs_from_its_successor(library: Path, tmp_path: Path) -> None:
    _with_successor(library)
    _build(library, tmp_path)
    activities = _activities(tmp_path)
    assert activities[H2]["name"] == "Fixture: water electrolysis [superseded by fixture-electrolysis-2 0.2.0]"
    assert activities["fixture-electrolysis:fixture-electrolysis-2:product:H2"]["name"] == "Fixture: water electrolysis"
