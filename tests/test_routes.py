"""Route groups (routes.json, scripts/routes.py): all routes to a product per one functional unit,
with computed comparability flags (ChemE-as-Code/website#38)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_catalog  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
ROUTES = FIXTURES / "routes"
LIBRARY = FIXTURES / "library"


def _routes(library: Path, out: Path, public: bool = False) -> dict:
    report = build_catalog.build(library, out, None, commit="fixture", public=public)
    assert report.errors == []
    return json.loads((out / "routes.json").read_text(encoding="utf-8"))


def _group(data: dict, chemical: str) -> dict:
    return next(g for g in data["products"] if g["chemical"] == chemical)


def _by_process(group: dict) -> dict[str, dict]:
    return {r["process"]: r for r in group["routes"]}


@pytest.fixture
def routes_copy(tmp_path: Path) -> Path:
    copy = tmp_path / "routes"
    shutil.copytree(ROUTES, copy)
    return copy


def _edit(path: Path, change) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_two_routes_to_one_product_per_the_same_functional_unit(tmp_path: Path) -> None:
    report = build_catalog.build(ROUTES, tmp_path / "out", None, commit="fixture")
    assert report.errors == [] and report.warnings == []
    data = json.loads((tmp_path / "out" / "routes.json").read_text())
    assert data["schema"] == "cheme-as-code/catalog/v1" and data["mode"] == "preview"
    assert "critical review" in data["critical_review"] and set(data["criteria"]) == {
        "product", "functional_unit", "boundary", "system_model", "allocation", "background", "dqr",
    }
    hydrogen = _group(data, "hydrogen")
    assert hydrogen["functional_unit"] == "1 kg"
    routes = _by_process(hydrogen)
    assert sorted(routes) == ["route-electrolysis", "route-smr"]
    pem, smr = routes["route-electrolysis"], routes["route-smr"]
    # both per 1 kg of the same grade, the inventory from the datasets divided by the product
    for route in (pem, smr):
        assert route["grade"] == "hydrogen/gaseous-30bar"
        assert route["inventory"]["functional_unit"] == "1 kg"
        assert route["state"] == {"phase": "gas", "pressure": 30}
    assert pem["inventory"]["energy"] == [
        {"key": "feed:POWER", "title": "Stack and balance-of-plant power", "amount": 55.0, "unit": "kWh", "carrier": "electricity"}
    ]
    assert {f["key"]: f["amount"] for f in smr["inventory"]["feedstocks"]} == {"feed:CH4": 3.2, "feed:H2O": 4.5}
    assert smr["inventory"]["emissions"] == [
        {"key": "emission:CO2", "title": "Carbon dioxide from reformer and shift", "amount": 8.8, "unit": "kg", "cas": "124-38-9"}
    ]
    # a free emission (vented oxygen) is not a key emission
    assert [e["key"] for e in pem["inventory"]["emissions"]] == ["emission:H2"]
    # what each route is, read from its manifest and dataset
    assert (pem["technology"], pem["tier"], pem["geography"], pem["year"]) == ("PEM water electrolysis (fixture)", None, "RER", 2026)
    assert (smr["tier"], smr["tier_method"], smr["geography"], smr["year"], smr["maturity"]) == (1, "sourced conceptual (fixture)", "GLO", 2025, "screening")
    assert pem["review"] == smr["review"] == ["none"]
    # the footprint where the catalog has one, with its interval; the manifest-only route has none
    assert pem["footprint"]["value"] == 11.0 and pem["footprint"]["functional_unit"] == "1 kg H2"
    assert pem["footprint"]["interval"] == {"low": 8.2, "median": 11.1, "high": 15.9, "level": 0.95, "iterations": 500, "source": "lca/uncertainty.csv"}
    assert smr["footprint"] is None
    assert pem["data_quality"]["dqr"] == 2.3333 and smr["data_quality"] is None
    assert hydrogen["markets"] == [
        {"code": "market:hydrogen/gaseous-30bar:GLO", "product": "hydrogen/gaseous-30bar", "region": "GLO", "layer": "production-mix",
         "title": "Fixture: hydrogen, gaseous, 30 bar, production mix", "source": "markets/hydrogen.yaml"}
    ]


def test_the_deliberate_mismatch_is_flagged_next_to_the_routes(tmp_path: Path) -> None:
    hydrogen = _group(_routes(ROUTES, tmp_path / "out"), "hydrogen")
    status = {k: v["status"] for k, v in hydrogen["comparability"].items()}
    assert status == {
        "product": "same", "functional_unit": "same", "boundary": "same", "allocation": "same",
        "system_model": "differs",  # route-smr's dataset states apos
        "dqr": "unknown",  # route-smr has no rating
        "background": "not-applicable",  # one route with a footprint
    }
    assert hydrogen["comparable"] is False
    routes = _by_process(hydrogen)
    flags = {pid: {(f["criterion"], f["status"]) for f in r["flags"]} for pid, r in routes.items()}
    # two routes, two system models: no majority, so both rows carry the warning
    assert flags == {
        "route-electrolysis": {("system_model", "differs")},
        "route-smr": {("system_model", "differs"), ("dqr", "unknown")},
    }
    assert "apos" in next(f["message"] for f in routes["route-smr"]["flags"] if f["criterion"] == "system_model")


def test_matching_routes_are_comparable(routes_copy: Path, tmp_path: Path) -> None:
    _edit(routes_copy / "processes/route-smr/lca/datasets/smr.yaml", lambda d: d.update(system_model="cutoff"))
    manifest = json.loads((routes_copy / "processes/route-electrolysis/lca/manifest.json").read_text())
    hydrogen = _group(_routes(routes_copy, tmp_path / "out"), "hydrogen")
    assert hydrogen["comparability"]["system_model"]["status"] == "same"
    assert hydrogen["comparability"]["dqr"]["status"] == "unknown"  # still unrated
    assert manifest["data_quality"]["dqr"] == hydrogen["comparability"]["dqr"]["range"]["best"]


def test_a_dqr_outside_the_stated_range_is_flagged(routes_copy: Path, tmp_path: Path) -> None:
    # the SMR route as a plant's own dataset with a run manifest: a DQR 1.5 worse than the best
    smr = routes_copy / "processes/route-smr"
    (smr / "lca/datasets/smr.yaml").rename(smr / "lca/dataset.yaml")
    (smr / "lca/datasets").rmdir()
    (smr / "lca/manifest.json").write_text(json.dumps({"data_quality": {"dqr": 3.8333}}))
    hydrogen = _group(_routes(routes_copy, tmp_path / "out"), "hydrogen")
    assert hydrogen["comparability"]["dqr"] == {
        "status": "differs", "description": hydrogen["comparability"]["dqr"]["description"], "range": {"best": 2.3333, "spread": 1.0},
    }
    flags = [f for f in _by_process(hydrogen)["route-smr"]["flags"] if f["criterion"] == "dqr"]
    assert flags[0]["status"] == "differs" and "3.8333" in flags[0]["message"]


def test_another_functional_unit_is_flagged_and_the_inventory_converted(routes_copy: Path, tmp_path: Path) -> None:
    _edit(routes_copy / "processes/route-electrolysis/lca/lca.yaml", lambda d: d["functional_unit"].update(unit="t"))
    shutil.copytree(routes_copy / "processes/route-smr", routes_copy / "processes/route-smr-2")
    _edit(routes_copy / "processes/route-smr-2/process.yaml", lambda d: d.update(id="route-smr-2"))
    hydrogen = _group(_routes(routes_copy, tmp_path / "out"), "hydrogen")
    assert hydrogen["functional_unit"] == "1 kg"  # two of three routes
    routes = _by_process(hydrogen)
    assert [(f["criterion"], f["status"]) for f in routes["route-electrolysis"]["flags"] if f["criterion"] == "functional_unit"] == [("functional_unit", "differs")]
    # the inventory of the odd one out in the group's functional unit (mass converts)
    assert routes["route-electrolysis"]["inventory"]["functional_unit"] == "1 kg"
    assert routes["route-electrolysis"]["inventory"]["energy"][0]["amount"] == 55.0
    # its footprint stays per its own functional unit (never converted)
    assert routes["route-electrolysis"]["footprint"]["functional_unit"] == "1 t H2"


def test_another_grade_is_a_product_mismatch(routes_copy: Path, tmp_path: Path) -> None:
    _edit(routes_copy / "chemicals/chemicals.yaml", lambda d: next(c for c in d["chemicals"] if c["slug"] == "hydrogen")["grades"].append(
        {"slug": "liquid", "name": "Hydrogen, liquid", "phase": "liquid"}))
    _edit(routes_copy / "processes/route-smr/process.yaml", lambda d: d["chemistry"]["outputs"][0].update(chemical="hydrogen/liquid"))
    hydrogen = _group(_routes(routes_copy, tmp_path / "out"), "hydrogen")
    assert hydrogen["comparability"]["product"]["status"] == "differs"
    assert {r["process"] for r in hydrogen["routes"] if any(f["criterion"] == "product" for f in r["flags"])} == {"route-electrolysis", "route-smr"}


def test_a_route_without_a_dataset_is_listed_without_numbers(routes_copy: Path, tmp_path: Path) -> None:
    shutil.rmtree(routes_copy / "processes/route-smr/lca")
    routes = _by_process(_group(_routes(routes_copy, tmp_path / "out"), "hydrogen"))
    smr = routes["route-smr"]
    assert smr["dataset"] is None and smr["inventory"] is None and smr["missing"] == "no LCI dataset of this product"
    assert {(f["criterion"], f["status"]) for f in smr["flags"]} >= {("functional_unit", "unknown"), ("system_model", "unknown")}


def test_public_build_keeps_a_publishable_footprint_with_its_interval(tmp_path: Path) -> None:
    data = _routes(ROUTES, tmp_path / "pub", public=True)
    assert data["mode"] == "public"
    pem = _by_process(_group(data, "hydrogen"))["route-electrolysis"]
    assert pem["footprint"]["value"] == 11.0 and pem["footprint"]["interval"]["high"] == 15.9


def test_public_build_withholds_a_placeholder_footprint_in_the_routes(tmp_path: Path) -> None:
    preview = _by_process(_group(_routes(LIBRARY, tmp_path / "preview"), "hydrogen"))["fixture-electrolysis"]
    assert preview["footprint"]["value"] == 24
    data = _routes(LIBRARY, tmp_path / "pub", public=True)
    hydrogen = _group(data, "hydrogen")
    footprint = _by_process(hydrogen)["fixture-electrolysis"]["footprint"]
    assert footprint["values_withheld"] == "placeholder-factors"
    assert "value" not in footprint and "interval" not in footprint
    numbers = [v for v in footprint.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    assert numbers == []
    # only public processes: the internal ammonia route is not in the public routes
    assert [g["chemical"] for g in data["products"]] == ["hydrogen", "oxygen"]
    assert "fixture-ammonia" not in (tmp_path / "pub" / "routes.json").read_text()


def test_a_co_product_of_a_multi_output_dataset_gets_no_unallocated_inventory(tmp_path: Path) -> None:
    data = _routes(LIBRARY, tmp_path / "out")
    oxygen = _by_process(_group(data, "oxygen"))["fixture-electrolysis"]
    assert oxygen["inventory"]["missing"].startswith("a co-product of a multi-output dataset")
    assert oxygen["footprint"] is None  # the LCA's functional unit is the hydrogen
    hydrogen = _by_process(_group(data, "hydrogen"))["fixture-electrolysis"]
    assert hydrogen["inventory"]["basis"].endswith("the other products (product:O2) carry none")
    assert _group(data, "hydrogen")["comparable"] is None  # one route: nothing to compare
