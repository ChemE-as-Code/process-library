"""The check of lci/mappings.yaml against a licensed background (scripts/check_mappings.py,
ADR 0017) and its state in the LCI build (datapackage.json brightway.background_check).

The backgrounds here are synthetic: lists of the names the mappings themselves give, so no
licensed data is needed or used. tests/test_lci_brightway.py runs the CLI in a Brightway
project."""

from __future__ import annotations

import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_lci  # noqa: E402
import check_mappings as cm  # noqa: E402

MAPPINGS = build_lci.load_mappings(KIT / "lci" / "mappings.yaml")
FIXTURE_LIBRARY = KIT / "tests" / "fixtures" / "library"
DATE = dt.date(2026, 10, 27)


def _background(mappings: dict, sites: list[str]) -> list[dict]:
    """A background that holds exactly the mappings' activities, at *sites* for `site`."""
    rows = []
    for t in cm.targets(mappings):
        if t["kind"] == "technosphere":
            for location in sites if t["location"] == cm.SITE else [t["location"]]:
                rows.append({"name": t["name"], "reference product": t["reference_product"], "unit": t["unit"], "location": location})
    return rows


def _biosphere(mappings: dict) -> list[dict]:
    return [{"code": t.get("uuid", f"code-{i}"), "name": t["name"], "categories": t["categories"]} for i, t in enumerate(cm.targets(mappings)) if t["kind"] == "biosphere"]


def test_targets_cover_every_activity_and_biosphere_flow_of_the_mappings() -> None:
    targets = cm.targets(MAPPINGS)
    activities = [tid for tid, e in MAPPINGS["technosphere"].items() if "activity" in e]
    assert [t["entry"] for t in targets if t["kind"] == "technosphere"] == [f"technosphere.{tid}" for tid in activities]
    assert {t["entry"] for t in targets if t["kind"] == "biosphere"} == {f"biosphere.{fid}" for fid in MAPPINGS["biosphere"]}
    # proxies are the library's own activities: their inputs name technosphere entries, not the background
    assert not any(t["entry"].startswith("proxies") for t in targets)
    assert {t["location"] for t in targets if t["entry"] == "technosphere.electricity"} == {cm.SITE}


def test_a_background_with_every_name_matches_all() -> None:
    checked, unmatched = cm.check(MAPPINGS, _background(MAPPINGS, ["DE", "NL"]), _biosphere(MAPPINGS), ["DE", "NL"])
    sites = sum(1 for t in cm.targets(MAPPINGS) if t.get("location") == cm.SITE)
    assert unmatched == []
    assert checked == len(cm.targets(MAPPINGS)) + sites  # each site entry once per site


def test_unmatched_names_carry_the_reason() -> None:
    background = _background(MAPPINGS, ["DE"])  # NL missing for the site entries
    background = [r for r in background if r["name"] != "market for lubricating oil"]
    nitrogen = next(r for r in background if r["name"] == "market for nitrogen, liquid")
    nitrogen["location"] = "RoW"  # the mappings say RER
    zeolite = next(r for r in background if r["name"] == "market for zeolite, powder")
    zeolite["unit"] = "cubic meter"
    biosphere = _biosphere(MAPPINGS)
    co2 = next(f for f in biosphere if f["name"] == "Carbon dioxide, fossil")
    co2["categories"] = ["air", "urban air close to ground"]
    biosphere = [f for f in biosphere if f["name"] != "Hydrogen"]

    checked, unmatched = cm.check(MAPPINGS, background, biosphere, ["DE", "NL"])
    by_entry = {(m["entry"], m.get("location")): m for m in unmatched}
    assert by_entry[("technosphere.lube-oil", "RER")]["reason"] == "name not in the background"
    assert by_entry[("technosphere.nitrogen", "RER")]["available_locations"] == ["RoW"]
    assert by_entry[("technosphere.adsorbent", "GLO")]["reason"] == "name in the background, with another reference product or unit"
    assert by_entry[("technosphere.electricity", "NL")]["site"] is True
    assert ("technosphere.electricity", "DE") not in by_entry
    assert by_entry[("biosphere.CO2/fossil", None)]["reason"] == "uuid in the biosphere under another name or categories"
    assert by_entry[("biosphere.H2", None)]["reason"] == "name and categories not in the biosphere"
    record = cm.record(MAPPINGS, checked, unmatched, database="bg", version="1", biosphere="biosphere3", sites=["DE", "NL"], checked_by="test", date=DATE)
    assert cm.validate(record) == []
    assert record["result"] == {"checked": checked, "matched": checked - len(unmatched), "unmatched": len(unmatched)}


def test_the_hash_ignores_comments_and_sources_but_not_names() -> None:
    edited = json.loads(json.dumps(MAPPINGS))
    edited["technosphere"]["electricity"]["source"] = "another text"
    edited["proxies"]["pipe"]["inputs"][0]["amount"] = 21.0
    assert cm.targets_sha256(edited) == cm.targets_sha256(MAPPINGS)
    edited["technosphere"]["lube-oil"]["activity"]["location"] = "GLO"
    assert cm.targets_sha256(edited) != cm.targets_sha256(MAPPINGS)


# --- the build states the latest check ---------------------------------------------------------


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(FIXTURE_LIBRARY, copy)
    return copy


def _write_record(library: Path, name: str, mappings: dict, unmatched: list[dict], date: dt.date = DATE) -> None:
    folder = library / "lci" / "mapping-checks"
    folder.mkdir(exist_ok=True)
    checked = len(cm.targets(mappings)) + 2
    data = cm.record(mappings, checked, unmatched, database="ecoinvent-3.11-cutoff", version="3.11", biosphere="biosphere3", sites=["DE"], checked_by="A. Curator", date=date)
    (folder / name).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _check_state(library: Path, out: Path) -> tuple[dict, list[str]]:
    report = build_lci.build(library, out, "0.1.0", commit="fixture")
    assert report.errors == []
    lci = out / "lci"
    package = json.loads((lci / "datapackage.json").read_text(encoding="utf-8"))
    index = json.loads((lci / "index.json").read_text(encoding="utf-8"))
    return package["brightway"]["background_check"], [c for c in index["caveats"] if c.startswith("Background names")]


def test_without_a_record_the_build_says_unchecked(library: Path, tmp_path: Path) -> None:
    state, caveats = _check_state(library, tmp_path / "out")
    assert state["status"] == "unchecked"
    assert len(caveats) == 1 and "unchecked" in caveats[0]


def test_a_clean_record_verifies_and_the_latest_record_wins(library: Path, tmp_path: Path) -> None:
    mappings = build_lci.load_mappings(library / "lci" / "mappings.yaml")
    miss = {"entry": "technosphere.water", "kind": "technosphere", "name": "x", "reason": "name not in the background"}
    _write_record(library, "2026-10-01-ecoinvent.yaml", mappings, [miss], date=dt.date(2026, 10, 1))
    _write_record(library, "2026-10-27-ecoinvent.yaml", mappings, [])
    state, caveats = _check_state(library, tmp_path / "out")
    assert state["status"] == "verified"
    assert state["record"] == "lci/mapping-checks/2026-10-27-ecoinvent.yaml"
    assert state["background"] == {"database": "ecoinvent-3.11-cutoff", "version": "3.11"}
    assert (state["checked_by"], state["unmatched"]) == ("A. Curator", 0)
    assert caveats == []


def test_unmatched_names_fail_the_check(library: Path, tmp_path: Path) -> None:
    mappings = build_lci.load_mappings(library / "lci" / "mappings.yaml")
    miss = {"entry": "technosphere.water", "kind": "technosphere", "name": "x", "reason": "name not in the background"}
    _write_record(library, "2026-10-27-ecoinvent.yaml", mappings, [miss])
    state, caveats = _check_state(library, tmp_path / "out")
    assert (state["status"], state["unmatched"]) == ("failed", 1)
    assert "1 name(s) did not match ecoinvent-3.11-cutoff" in caveats[0]


def test_a_changed_name_makes_the_record_stale(library: Path, tmp_path: Path) -> None:
    mappings = build_lci.load_mappings(library / "lci" / "mappings.yaml")
    _write_record(library, "2026-10-27-ecoinvent.yaml", mappings, [])
    path = library / "lci" / "mappings.yaml"
    text = path.read_text(encoding="utf-8")
    assert '"market for water, deionised"' in text
    path.write_text(text.replace('"market for water, deionised"', '"market for water, decarbonised"', 1), encoding="utf-8")
    state, caveats = _check_state(library, tmp_path / "out")
    assert state["status"] == "stale"
    assert "stale" in caveats[0]


def test_an_invalid_record_fails_the_build(library: Path, tmp_path: Path) -> None:
    folder = library / "lci" / "mapping-checks"
    folder.mkdir()
    (folder / "bad.yaml").write_text("schema: cheme-as-code/lci-mapping-check/v1\nchecked_by: someone\n", encoding="utf-8")
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert any("lci/mapping-checks/bad.yaml" in e for e in report.errors)


def test_the_library_records_are_valid() -> None:
    _, problems = cm.status(MAPPINGS, KIT / "lci" / "mapping-checks")
    assert problems == []
