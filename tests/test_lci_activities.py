"""``datapackage.json`` ``activities``: the per-activity documentation the Atlas dataset pages
render (scripts/lci_activities.py, ChemE-as-Code/website#37)."""

from __future__ import annotations

import json
import shutil
import zipfile
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))
sys.path.insert(0, str(KIT / "tests"))

import build_lci  # noqa: E402
from test_build_lci import ASU, DB, H2, LIBRARY, NH3, _activities  # noqa: E402

#: Keys that would carry an impact value; the LCI has no characterisation factors, so an
#: activity entry never holds one (placeholder factors cannot reach a public page through it).
MARKET = "market:hydrogen:GLO"
IMPACT_KEYS = {"impact", "impacts", "result", "results", "totals", "gwp", "footprint", "score"}


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    return copy


def _package(library: Path, out: Path, public: bool = False) -> dict:
    report = build_lci.build(library, out, "0.1.0", commit="fixture", public=public)
    assert report.errors == [], report.errors
    return json.loads((out / "lci" / "datapackage.json").read_text(encoding="utf-8"))


def _keys(node) -> set[str]:
    if isinstance(node, dict):
        return set(node) | {k for v in node.values() for k in _keys(v)}
    if isinstance(node, list):
        return {k for v in node for k in _keys(v)}
    return set()


def _codes(node) -> set[str]:
    """Every string that names an activity code (``<process>:<dataset>:<key>``) in *node*."""
    if isinstance(node, dict):
        return {c for v in node.values() for c in _codes(v)}
    if isinstance(node, list):
        return {c for v in node for c in _codes(v)}
    return {node} if isinstance(node, str) and node.count(":") >= 3 else set()


def test_every_exported_activity_has_an_entry_with_its_workbook_exchanges(library: Path, tmp_path: Path) -> None:
    package = _package(library, tmp_path / "out")
    workbook = _activities(tmp_path / "out" / "lci" / f"{DB}.xlsx")
    entries = {e["code"]: e for e in package["activities"]}
    assert sorted(entries) == sorted(workbook)  # datasets and proxies alike
    for code, entry in entries.items():
        exported = [e for e in workbook[code]["exchanges"] if e["type"] != "production"]
        assert [(e["key"], e["amount"], e["unit"], e["type"]) for e in entry["exchanges"]] == [
            (e.get("atlas key"), e["amount"], e["unit"], e["type"]) for e in exported
        ]
        assert entry["reference_exchange"]["amount"] == 1 and entry["reference_exchange"]["unit"] == workbook[code]["meta"]["unit"]
        # every database file of the build, each with how to find the activity in it
        assert [d["path"] for d in entry["downloads"]] == [r["path"] for r in package["resources"]]
        for download in entry["downloads"]:
            if download["path"].endswith("-olca-jsonld.zip"):
                with zipfile.ZipFile(tmp_path / "out" / "lci" / download["path"]) as archive:
                    assert download["member"] in archive.namelist() and download["select"] == "process"
            elif download["path"].endswith("-multifunctional.json"):
                multi = json.loads((tmp_path / "out" / "lci" / download["path"]).read_text(encoding="utf-8"))
                assert download["value"] in {p["code"] for p in multi["processes"]}
            else:
                assert download == {**download, "select": "code", "value": code}
        assert not _keys(entry) & IMPACT_KEYS


def test_entry_documents_header_allocation_provenance_pedigree_and_links(library: Path, tmp_path: Path) -> None:
    package = _package(library, tmp_path / "out")
    entries = {e["code"]: e for e in package["activities"]}
    h2 = entries[H2]
    assert h2["process"] == "fixture-electrolysis" and h2["kind"] == "dataset" and h2["publication"] == "public"
    assert h2["dataset"]["id"] == "fixture-electrolysis" and h2["dataset"]["version"] == "0.1.0"
    assert h2["activity_uuid"] is None  # the library assigns none; never invented
    assert h2["system_model"] == {"id": "cutoff", "label": "attributional, cut-off"}
    dataset = package["processes"][1]["datasets"][0]
    assert h2["allocation"]["method"] == "mass" and h2["allocation"]["share"] == dataset["allocation"]["shares"]["product:H2"]
    assert h2["header"]["geography"]["location"] == "GLO"
    assert h2["citation"]["doi"] is None and H2 in h2["citation"]["text"]
    by_key = {e["key"]: e for e in h2["exchanges"]}
    steel = by_key["construction:steel"]
    assert steel["provenance"] == "calculated" and steel["direction"] == "input"
    assert steel["link"]["name"] and steel["link"]["location_rule"] in ("site", "fixed")
    assert by_key["feed:POWER"]["provenance"] == "assumed"  # core's default for an exchange without one
    water = by_key["resource:WATER"]
    assert water["direction"] == "resource" and water["flow"]["compartment"] == ["natural resource", "in water"]
    assert water["flow"]["uuid"] == "8c75e7ab-8ab8-41e4-b394-c166ff5b050d"
    assert by_key["emission:H2"]["flow"]["compartment"] == ["air"]
    assert len(package["pedigree_indicators"]) == 5
    assert all(len(e["pedigree"]["scores"]) == 5 for e in h2["exchanges"] if "pedigree" in e)
    # an Atlas-internal link by code, both ways
    hydrogen = next(e for e in entries[NH3]["exchanges"] if e["key"] == "feed:hydrogen")
    # the input links to the market (markets/hydrogen.yaml), the plant behind it is named
    assert hydrogen["atlas_alternative"]["code"] == MARKET and hydrogen["atlas_alternative"]["kind"] == "market"
    assert hydrogen["atlas_alternative"]["check"].startswith("compatible")
    assert hydrogen["atlas_plant"]["code"] == H2
    assert entries[MARKET]["used_by"] == [NH3]
    assert h2["used_by"] == [MARKET]  # the plant supplies the market
    assert entries[NH3]["publication"] == "preview"  # fixture-ammonia is internal


def test_exchange_names_its_flowsheet_streams_and_nothing_else(library: Path, tmp_path: Path) -> None:
    root = library / "processes" / "fixture-electrolysis"
    stream = "S1"
    (root / "process" / "flowsheet.yaml").write_text(yaml.safe_dump({"streams": [{"id": stream}]}), encoding="utf-8")
    path = root / "lca" / "dataset.yaml"
    dataset = yaml.safe_load(path.read_text(encoding="utf-8"))
    water = next(e for e in dataset["exchanges"] if e["key"] == "feed:WATER")
    water["streams"] = [stream, "steel HEB200 steel rack"]  # a material item is no stream
    steel = next(e for e in dataset["exchanges"] if e["key"] == "construction:steel")
    steel["streams"] = ["steel HEB200 steel rack"]
    path.write_text(yaml.safe_dump(dataset, sort_keys=False), encoding="utf-8")
    entries = {e["code"]: e for e in _package(library, tmp_path / "out")["activities"]}
    by_key = {e["key"]: e for e in entries[H2]["exchanges"]}
    assert by_key["feed:WATER"]["streams"] == [stream]
    assert "streams" not in by_key["construction:steel"]
    assert "streams" not in by_key["feed:POWER"]  # the dataset names none


def test_public_build_withholds_unpublished_processes_from_the_activities(library: Path, tmp_path: Path) -> None:
    package = _package(library, tmp_path / "out", public=True)
    codes = {e["code"] for e in package["activities"]}
    assert codes == {H2, H2.replace(":H2", ":O2"), MARKET}  # the market's supplier is public
    assert all(e["publication"] == "public" for e in package["activities"])
    # no amount, link or back-link of the unpublished process anywhere
    assert not any(c.startswith("fixture-ammonia:") for c in _codes(package["activities"]))
    assert "fixture-ammonia" not in json.dumps(package["activities"])
    # the placeholder factors of fixture-electrolysis stay out: the entries carry no impact value
    assert package["processes"][0]["factors_status"] == "placeholder"
    assert not _keys(package["activities"]) & IMPACT_KEYS


def test_closure_comes_from_the_manifest_balance_or_says_why_not(library: Path, tmp_path: Path) -> None:
    package = _package(library, tmp_path / "a")
    entries = {e["code"]: e for e in package["activities"]}
    assert entries[H2]["closure"]["status"] == "not-assessed" and "balance" in entries[H2]["closure"]["reason"]
    assert entries[NH3]["closure"]["status"] == "not-assessed" and "hand-written" in entries[NH3]["closure"]["reason"]
    manifest = library / "processes" / "fixture-electrolysis" / "lca" / "manifest.json"
    balance = {"dataset": "fixture-electrolysis", "status": {"lci-mass-balance": "closed"}, "tolerance": 0.05, "mass": {"unit": "kg", "residual": 0.0}}
    manifest.write_text(json.dumps({"balance": balance}), encoding="utf-8")
    entries = {e["code"]: e for e in _package(library, tmp_path / "b")["activities"]}
    assert entries[H2]["closure"] == {"status": "assessed", "source": "lca/manifest.json balance", "balance": balance}
    manifest.write_text(json.dumps({"balance": {**balance, "dataset": "another"}}), encoding="utf-8")
    entries = {e["code"]: e for e in _package(library, tmp_path / "c")["activities"]}
    assert entries[H2]["closure"]["status"] == "not-assessed"


def test_asu_activities_carry_classification_and_cas(tmp_path: Path) -> None:
    library = tmp_path / "library"
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
    shutil.copy(KIT / "processes" / "asu-1" / "lca" / "mappings.yaml", library / "processes" / "asu-1" / "lca")  # its own overrides
    shutil.copy(KIT / "chemicals" / "chemicals.yaml", library / "chemicals")
    for name in ("dataset.yaml", "lca.yaml", "factors.yaml"):
        shutil.copy(ASU / name, library / "processes" / "asu-1" / "lca")
    package = _package(library, tmp_path / "out")
    datasets = [e for e in package["activities"] if e["kind"] == "dataset"]
    assert len(datasets) == 4
    goxp = next(e for e in datasets if e["code"].endswith(":GOXP"))
    assert goxp["cas"] == "7782-44-7" and goxp["header"]["classification"]["isic"]["codes"] == ["2011"]
    assert goxp["header"]["classification"]["product"]["cpc"]
    assert sum(e["allocation"]["share"] for e in datasets) == pytest.approx(1.0)
    # inputs linked to the screening proxies name them by code, and the proxies list their users
    proxies = {e["code"]: e for e in package["activities"] if e["kind"] == "proxy"}
    assert goxp["code"] in proxies["proxy:cooling-water"]["used_by"]


def test_market_entry_documents_suppliers_shares_transport_and_sources(library: Path, tmp_path: Path) -> None:
    package = _package(library, tmp_path / "out")
    market = next(e for e in package["activities"] if e["code"] == MARKET)
    listed = next(m for m in package["markets"] if m["code"] == MARKET)
    assert market["kind"] == "market" and market["process"] is None and market["publication"] == "public"
    assert market["market"]["suppliers"] == listed["suppliers"] and market["market"]["facts"] == listed["facts"]
    assert market["market"]["not_exported"] == listed["not_exported"]
    (supplier,) = [e for e in market["exchanges"] if e["key"].startswith("supplier:")]
    assert supplier["atlas"]["code"] == H2 and supplier["atlas"]["kind"] == "supply"
    assert supplier["provenance"] == "assumed" and supplier["source"] == "fixture: synthetic volume"
    assert market["cas"] == "1333-74-0"


def test_a_market_of_an_unpublished_supplier_is_preview(library: Path, tmp_path: Path) -> None:
    path = library / "processes" / "fixture-electrolysis" / "process.yaml"
    path.write_text(path.read_text().replace("status: public", "status: candidate"))
    entries = {e["code"]: e for e in _package(library, tmp_path / "out")["activities"]}
    assert entries[MARKET]["publication"] == "preview" and entries[H2]["publication"] == "preview"
