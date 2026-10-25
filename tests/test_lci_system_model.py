"""The system model of the LCI build (docs/system-model.md) and its governance (docs/governance.md):
cut-off enforcement, the substitution variant, the allocation hierarchy and the change report."""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_lci  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
LIBRARY = FIXTURES / "library"
ASU = FIXTURES / "asu-lca"
H2 = "fixture-electrolysis:fixture-electrolysis:product:H2"
O2 = H2.replace(":H2", ":O2")
GOXP = "asu-1:asu-1-500-t-d-gox:product:GOXP"
END_OF_LIFE = ("end-of-life:steel-recycling", "end-of-life:aluminium-recycling")


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    return copy


@pytest.fixture
def asu_library(tmp_path: Path) -> Path:
    library = tmp_path / "asu-library"
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
    shutil.copy(KIT / "chemicals" / "chemicals.yaml", library / "chemicals")
    for name in ("dataset.yaml", "lca.yaml", "factors.yaml"):
        shutil.copy(ASU / name, library / "processes" / "asu-1" / "lca")
    return library


def _edit(path: Path, change) -> None:
    data = yaml.safe_load(path.read_text())
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _dataset(library: Path) -> Path:
    return library / "processes" / "fixture-electrolysis" / "lca" / "dataset.yaml"


def _electrolysis(out: Path) -> dict:
    """The allocation record of the fixture electrolysis in a build's datapackage.json."""
    package = _json(out / "lci" / "datapackage.json")
    return next(p for p in package["processes"] if p["id"] == "fixture-electrolysis")["datasets"][0]["allocation"]


def _study(library: Path) -> Path:
    return library / "processes" / "fixture-electrolysis" / "lca" / "lca.yaml"


# --- cut-off ------------------------------------------------------------------------------------


def test_cutoff_build_has_no_credits_and_records_the_exclusions(asu_library: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    report = build_lci.build(asu_library, out, "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    activities = build_lci.read_workbook(out / "lci" / "cheme-as-code-atlas-0.1.0.xlsx")
    exchanges = [e for a in activities.values() for e in a["exchanges"]]
    assert not [e for e in exchanges if e["amount"] < 0]  # no avoided burden anywhere
    assert not [code for code in activities if "credit" in code]
    goxp = activities[GOXP]
    assert not [e for e in goxp["exchanges"] if e.get("atlas key") in END_OF_LIFE]
    comment = goxp["meta"]["comment"]
    assert "System model: attributional, cut-off (docs/system-model.md, methodology 1.0.0)." in comment
    assert "Excluded by the cut-off system model (no credit): end-of-life:steel-recycling (End-of-life steel scrap" in comment
    assert goxp["meta"]["atlas system model"] == "cutoff"

    package = _json(out / "lci" / "datapackage.json")
    model = package["system_model"]
    assert model["id"] == "cutoff" and model["default"] is True and model["allocation_findings"] == []
    assert model["methodology"] == {"document": "docs/system-model.md", "version": build_lci.METHODOLOGY_VERSION}
    assert sorted(e["key"] for e in model["excluded"]) == sorted(END_OF_LIFE)
    assert all(e["process"] == "asu-1" and "cut-off" in e["decision"].lower() for e in model["excluded"])
    assert package["name"] == "cheme-as-code-atlas-0.1.0"


def test_substitution_variant_is_labelled_and_carries_the_credits(asu_library: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    report = build_lci.build(asu_library, out, "0.1.0", commit="fixture", system_model="substitution")
    assert report.errors == []
    db = "cheme-as-code-atlas-0.1.0-substitution"
    assert (out / "lci" / f"{db}.xlsx").is_file()
    activities = build_lci.read_workbook(out / "lci" / f"{db}.xlsx")
    credit = activities["proxy:steel-scrap-credit"]
    assert [e["amount"] for e in credit["exchanges"] if e["type"] == "technosphere"] == [-0.5]
    goxp = activities[GOXP]
    steel = next(e for e in goxp["exchanges"] if e.get("atlas key") == "end-of-life:steel-recycling")
    assert steel["name"].startswith("steel scrap to recycling") and steel["amount"] > 0
    assert "A labelled variant, not the default cut-off database" in goxp["meta"]["comment"]
    assert "Excluded by the cut-off" not in goxp["meta"]["comment"]
    package = _json(out / "lci" / "datapackage.json")
    assert package["system_model"]["id"] == "substitution" and package["system_model"]["default"] is False
    assert package["system_model"]["excluded"] == []
    assert any("substitution variant" in c for c in package["caveats"])


def test_credit_proxies_outside_the_substitution_profile_are_refused(library: Path, tmp_path: Path) -> None:
    path = library / "lci" / "mappings.yaml"
    _edit(path, lambda m: m.update(proxies={"scrap-credit": {
        "name": "scrap credit", "reference_product": "scrap", "unit": "kilogram", "location": "GLO",
        "inputs": [{"use": "steel-sections", "amount": -0.5, "source": "test"}], "source": "test",
    }}))
    with pytest.raises(build_lci.BuildError, match="avoided-burden credit; credits belong in substitution.proxies"):
        build_lci.load_mappings(path)


def test_a_negative_technosphere_exchange_is_refused_under_cutoff(library: Path, tmp_path: Path) -> None:
    _edit(_dataset(library), lambda d: d["exchanges"].append(
        {"key": "end-of-life:scrap", "type": "output", "amount": -0.4, "unit": "kg", "link": {"factor": "steel-sections"}}
    ))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert any("end-of-life:scrap: negative technosphere amount" in e and "cut-off build refuses" in e for e in report.errors)
    assert not (tmp_path / "out" / "lci").exists()
    # the substitution variant accepts it (it is where credits belong)
    assert build_lci.build(library, tmp_path / "sub", "0.1.0", commit="fixture", system_model="substitution").errors == []


def test_an_exclusion_without_a_substitution_link_fails_the_variant(library: Path, tmp_path: Path) -> None:
    _edit(library / "lci" / "mappings.yaml", lambda m: m.update(cutoff_exclusions={"scrap": {"decision": "test: recycling, cut-off"}}))
    _edit(_dataset(library), lambda d: d["exchanges"].append({"key": "end-of-life:scrap", "type": "output", "amount": 0.4, "unit": "kg", "link": {"factor": "scrap"}}))
    cutoff = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert cutoff.errors == []
    assert _json(tmp_path / "out" / "lci" / "datapackage.json")["system_model"]["excluded"][0]["key"] == "end-of-life:scrap"
    variant = build_lci.build(library, tmp_path / "sub", "0.1.0", commit="fixture", system_model="substitution")
    assert any("'scrap' is excluded under cut-off and has no substitution mapping" in e for e in variant.errors)


def test_an_exclusion_cannot_also_be_linked(library: Path) -> None:
    path = library / "lci" / "mappings.yaml"
    _edit(path, lambda m: m.update(cutoff_exclusions={"water": {"decision": "test: excluded and linked"}}))
    with pytest.raises(build_lci.BuildError, match="linked or excluded, not both"):
        build_lci.load_mappings(path)


# --- allocation hierarchy -----------------------------------------------------------------------


def test_study_method_outside_the_hierarchy_is_replaced_with_a_finding(library: Path, tmp_path: Path) -> None:
    # price ratio 10 > 5: the WBCSD rule says economic, the study says mass
    _edit(_study(library), lambda s: s["allocation"].update(prices={"H2": 5.0, "O2": 0.5}))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == []
    (finding,) = report.warnings
    assert "the study's mass allocation is not the hierarchy's economic (price ratio 10" in finding
    entry = _electrolysis(tmp_path / "out")
    assert entry["method"] == "economic" and entry["source"] == "hierarchy" and entry["rule"] == "economic"
    assert entry["follows_hierarchy"] is False and "finding" in entry
    assert entry["shares"]["product:H2"] == pytest.approx(41.7 * 5 / (41.7 * 5 + 333.6 * 0.5))
    assert build_lci.main(["--library", str(library), "--out", str(tmp_path / "strict"), "--strict"]) == 1


def test_unprovable_allocation_is_a_finding_and_kept(library: Path, tmp_path: Path) -> None:
    _edit(_study(library), lambda s: s["allocation"].pop("prices"))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == []
    assert any("does not follow the documented hierarchy" in w for w in report.warnings)
    package = _json(tmp_path / "out" / "lci" / "datapackage.json")
    entry = _electrolysis(tmp_path / "out")
    assert entry["method"] == "mass" and entry["rule"] == "unresolved" and entry["follows_hierarchy"] is False
    assert len(package["system_model"]["allocation_findings"]) == 1
    assert "hierarchy rule unresolved" in build_lci.read_workbook(tmp_path / "out" / "lci" / "cheme-as-code-atlas-0.1.0.xlsx")[H2]["meta"]["comment"]


def test_a_curated_deviation_keeps_the_study_method(library: Path, tmp_path: Path) -> None:
    # core's allocation schema has no deviation field: a deviation is a curated rule only
    _edit(_study(library), lambda s: s["allocation"].update(prices={"H2": 5.0, "O2": 0.5}))
    _edit(library / "lci" / "mappings.yaml", lambda m: m.update(allocation={"fixture-electrolysis": {
        "method": "mass", "rule": "deviation", "reason": "test: the PCR of this sector prescribes mass"}}))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    entry = _electrolysis(tmp_path / "out")
    assert (entry["method"], entry["source"], entry["rule"], entry["reason"]) == ("mass", "mappings", "deviation", "test: the PCR of this sector prescribes mass")


def _ammonia_with_co2() -> dict:
    return {"id": "nh3", "exchanges": [
        {"key": "product:NH3", "type": "product", "amount": 1.0, "unit": "kg"},
        {"key": "product:CO2", "type": "product", "amount": 1.25, "unit": "kg"},
    ]}


def _mappings(**allocation) -> dict:
    return {"allocation": allocation}


def test_co2_cutoff_gives_the_co2_no_share_of_the_main_process(library: Path) -> None:
    path = library / "lci" / "mappings.yaml"
    _edit(path, lambda m: m.update(allocation={"fixture-ammonia": {"method": "mass", "rule": "co2-cutoff", "product": "CO2", "reason": "test: CO2 by mass"}}))
    with pytest.raises(build_lci.BuildError, match="method: .shares. was expected"):
        build_lci.load_mappings(path)  # only shares can express the cut before conditioning
    _edit(path, lambda m: m.update(allocation={"fixture-ammonia": {"method": "shares", "rule": "co2-cutoff", "reason": "test: no product named"}}))
    with pytest.raises(build_lci.BuildError, match="product"):
        build_lci.load_mappings(path)

    entry = {"method": "shares", "rule": "co2-cutoff", "product": "CO2", "reason": "test: cut before conditioning", "shares": {"NH3": 1, "CO2": 0}}
    choice = build_lci.choose_allocation("p", _ammonia_with_co2(), None, _mappings(p=entry))
    assert (choice.rule, choice.finding) == ("co2-cutoff", None)
    assert build_lci.shares(_ammonia_with_co2(), choice.allocation, "p") == {"product:NH3": 1.0, "product:CO2": 0.0}
    with pytest.raises(build_lci.BuildError, match="share of 0.5"):
        build_lci.choose_allocation("p", _ammonia_with_co2(), None, _mappings(p={**entry, "shares": {"NH3": 0.5, "CO2": 0.5}}))
    with pytest.raises(build_lci.BuildError, match="not a product"):
        build_lci.choose_allocation("p", _ammonia_with_co2(), None, _mappings(p={**entry, "product": "carbon-dioxide"}))


def test_a_curated_rule_overrides_the_study_and_is_checked(library: Path, tmp_path: Path) -> None:
    mappings = library / "lci" / "mappings.yaml"
    _edit(_study(library), lambda s: s["allocation"].update(prices={"H2": 5.0, "O2": 0.5}))
    _edit(mappings, lambda m: m.update(allocation={"fixture-electrolysis": {"method": "economic", "rule": "economic", "reason": "test: price ratio 10"}}))
    assert build_lci.build(library, tmp_path / "a", "0.1.0", commit="fixture").warnings == []
    entry = _electrolysis(tmp_path / "a")
    assert (entry["method"], entry["source"], entry["rule"]) == ("economic", "mappings", "economic")

    _edit(mappings, lambda m: m.update(allocation={"fixture-electrolysis": {"method": "mass", "rule": "mass", "reason": "test: claims mass"}}))
    (finding,) = build_lci.build(library, tmp_path / "b", "0.1.0", commit="fixture").warnings
    assert "rule mass, but the price ratio 10" in finding

    _edit(mappings, lambda m: m.update(allocation={"fixture-electrolysis": {"method": "mass", "rule": "physical-exergy", "reason": "test: inconsistent"}}))
    with pytest.raises(build_lci.BuildError, match="rule 'physical-exergy' does not allow method 'mass'"):
        build_lci.load_mappings(mappings)


def test_minor_coproducts_do_not_enter_the_price_ratio() -> None:
    dataset = {"id": "d", "exchanges": [
        {"key": "product:A", "type": "product", "amount": 1000.0, "unit": "kg"},
        {"key": "product:B", "type": "product", "amount": 500.0, "unit": "kg"},
        {"key": "product:C", "type": "product", "amount": 5.0, "unit": "kg"},  # 0.3 % of the mass
    ]}
    assert build_lci.price_ratio(dataset, {"prices": {"A": 1.0, "B": 2.0, "C": 100.0}}) == pytest.approx(2.0)
    assert build_lci.price_ratio(dataset, {"prices": {"A": 1.0, "C": 100.0}}) is None  # B has no price


def test_an_unpriced_minor_coproduct_has_no_economic_weight() -> None:
    dataset = {"id": "d", "exchanges": [
        {"key": "product:A", "type": "product", "amount": 100.0, "unit": "kg"},
        {"key": "product:B", "type": "product", "amount": 100.0, "unit": "kg"},
        {"key": "product:C", "type": "product", "amount": 0.5, "unit": "kg"},  # below 1 %, no price
    ]}
    choice = build_lci.choose_allocation("p", dataset, {"method": "economic", "prices": {"A": 10.0, "B": 1.0}}, _mappings())
    assert (choice.allocation["method"], choice.finding) == ("economic", None)
    weights = build_lci.shares(dataset, choice.allocation, "p")
    assert weights["product:C"] == 0.0 and weights["product:A"] == pytest.approx(10 / 11)


def test_one_major_coproduct_left_gives_mass() -> None:
    dataset = {"id": "d", "exchanges": [
        {"key": "product:A", "type": "product", "amount": 100.0, "unit": "kg"},
        {"key": "product:B", "type": "product", "amount": 0.5, "unit": "kg"},
    ]}
    assert build_lci.price_ratio(dataset, {"prices": {"A": 1.0, "B": 50.0}}) == 1.0
    choice = build_lci.choose_allocation("p", dataset, {"method": "mass"}, _mappings())
    assert (choice.rule, choice.finding) == ("mass", None)


def test_the_price_ratio_needs_every_coproduct_in_kg() -> None:
    dataset = {"id": "d", "exchanges": [
        {"key": "product:H2", "type": "product", "amount": 1.0, "unit": "kg"},
        {"key": "product:STEAM", "type": "product", "amount": 10.0, "unit": "MJ"},
    ]}
    study = {"method": "energy", "prices": {"H2": 3.0, "STEAM": 0.01}, "properties": {"H2": {"energy": 120.0}, "STEAM": {"energy": 1.0}}}
    assert build_lci.price_ratio(dataset, study) is None  # per kg against per MJ: no ratio
    choice = build_lci.choose_allocation("p", dataset, study, _mappings())
    assert choice.allocation["method"] == "energy" and choice.rule == "unresolved"
    assert "STEAM is not counted in kg" in choice.finding


# --- governance: versions and change report -----------------------------------------------------


def test_every_dataset_has_a_version_and_a_review_record(library: Path, tmp_path: Path) -> None:
    _edit(_dataset(library), lambda d: d.update(version="1.2.0", review=[{"type": "internal", "reviewer": "test"}]))
    build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    package = _json(tmp_path / "out" / "lci" / "datapackage.json")
    datasets = {d["id"]: d for p in package["processes"] for d in p["datasets"]}
    assert (datasets["fixture-electrolysis"]["version"], datasets["fixture-electrolysis"]["version_source"]) == ("1.2.0", "dataset")
    assert datasets["fixture-electrolysis"]["review"] == {"status": "internal", "records": [{"type": "internal", "reviewer": "test"}]}
    assert (datasets["fixture-ammonia-hb"]["version"], datasets["fixture-ammonia-hb"]["version_source"]) == ("0.1.0", "initial")
    assert datasets["fixture-ammonia-hb"]["review"] == {"status": "unreviewed"}
    assert all(d["methodology_version"] == build_lci.METHODOLOGY_VERSION and len(d["content_sha256"]) == 64 for d in datasets.values())


def test_two_consecutive_builds_produce_a_change_report(library: Path, tmp_path: Path) -> None:
    assert build_lci.build(library, tmp_path / "v1", "0.1.0", commit="one").errors == []

    def change(d):
        power = next(e for e in d["exchanges"] if e["key"] == "feed:POWER")
        power["amount"] = power["amount"] * 1.1
        d["exchanges"].append({"key": "feed:NITROGEN", "type": "input", "amount": 2.0, "unit": "kg", "link": {"factor": "nitrogen"}})

    _edit(_dataset(library), change)
    report = build_lci.build(library, tmp_path / "v2", "0.2.0", commit="two", previous=tmp_path / "v1")
    assert report.errors == []
    lci = tmp_path / "v2" / "lci"
    changes = _json(lci / "changes.json")
    assert changes["from"]["version"] == "0.1.0" and changes["to"]["version"] == "0.2.0"
    assert changes["to"]["system_model"] == "cutoff" and changes["impact"].startswith("not computed")
    assert changes["activities"]["added"] == [] and changes["activities"]["removed"] == []
    h2 = changes["activities"]["changed"][H2]
    assert h2["added"] == ["technosphere feed:NITROGEN"]
    (power,) = [c for c in h2["changed"] if c["exchange"] == "technosphere feed:POWER"]
    assert power["relative_change"] == pytest.approx(0.1)
    assert sorted(changes["activities"]["changed"]) == [H2, O2]
    electrolysis = next(d for d in changes["datasets"] if d["dataset"] == "fixture-electrolysis")
    assert electrolysis["status"] == "changed" and electrolysis["version_not_raised"] is True
    ammonia = next(d for d in changes["datasets"] if d["dataset"] == "fixture-ammonia-hb")
    assert ammonia["status"] == "unchanged"
    text = (lci / "CHANGES.md").read_text()
    assert "content changed, version not raised" in text and "feed:POWER: amount" in text and "(+10.00 %)" in text
    assert {f["name"] for f in _json(lci / "index.json")["files"]} >= {"changes.json", "CHANGES.md"}

    # unchanged input: an empty report
    assert build_lci.build(library, tmp_path / "v3", "0.2.1", commit="two", previous=tmp_path / "v2").errors == []
    again = _json(tmp_path / "v3" / "lci" / "changes.json")
    assert again["activities"] == {"added": [], "removed": [], "changed": {}}
    assert "No activity changed." in (tmp_path / "v3" / "lci" / "CHANGES.md").read_text()


def test_an_allocation_change_alone_needs_a_new_dataset_version(library: Path, tmp_path: Path) -> None:
    # the dataset file stays the same; the allocation changes through the mappings and the study
    assert build_lci.build(library, tmp_path / "v1", "0.1.0", commit="one").errors == []
    _edit(library / "lci" / "mappings.yaml", lambda m: m.update(allocation={"fixture-electrolysis": {
        "method": "shares", "rule": "deviation", "reason": "test: shares from a sector agreement"}}))
    _edit(_study(library), lambda s: s["allocation"].update(shares={"H2": 0.6, "O2": 0.4}))
    assert build_lci.build(library, tmp_path / "v2", "0.2.0", commit="two", previous=tmp_path / "v1").errors == []
    electrolysis = next(d for d in _json(tmp_path / "v2" / "lci" / "changes.json")["datasets"] if d["dataset"] == "fixture-electrolysis")
    assert electrolysis["content_changed"] is False and electrolysis["allocation_changed"] is True
    assert electrolysis["status"] == "changed" and electrolysis["version_not_raised"] is True
    assert electrolysis["allocation"] == ["mass", "shares"]
    assert "allocation changed, version not raised" in (tmp_path / "v2" / "lci" / "CHANGES.md").read_text()

    # same method, other shares
    _edit(_study(library), lambda s: s["allocation"].update(shares={"H2": 0.7, "O2": 0.3}))
    assert build_lci.build(library, tmp_path / "v3", "0.3.0", commit="three", previous=tmp_path / "v2").errors == []
    electrolysis = next(d for d in _json(tmp_path / "v3" / "lci" / "changes.json")["datasets"] if d["dataset"] == "fixture-electrolysis")
    assert electrolysis["status"] == "changed" and "allocation" not in electrolysis and electrolysis["version_not_raised"] is True
    assert "allocation shares changed" in (tmp_path / "v3" / "lci" / "CHANGES.md").read_text()


def test_change_report_inputs_are_checked(library: Path, tmp_path: Path) -> None:
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="x", previous=tmp_path / "nothing")
    assert any("no datapackage.json" in e for e in report.errors)
    build_lci.build(library, tmp_path / "out", "0.1.0", commit="x")
    assert build_lci.main(["--library", str(library), "--out", str(tmp_path / "out"), "--previous", str(tmp_path / "out")]) == 1


def test_the_methodology_version_is_the_documented_one() -> None:
    text = (KIT / "docs" / "system-model.md").read_text(encoding="utf-8")
    assert re.search(rf"Methodology version:\s*\*\*{re.escape(build_lci.METHODOLOGY_VERSION)}\*\*", text)


def test_release_metadata_is_drafted_not_published(tmp_path: Path) -> None:
    import release_metadata

    assert release_metadata.main(["--version", "0.2.0", "--out", str(tmp_path), "--date", "2026-11-01"]) == 0
    zenodo = _json(tmp_path / "archive" / ".zenodo.json")
    assert zenodo["version"] == "0.2.0" and zenodo["publication_date"] == "2026-11-01" and zenodo["license"] == "cc-by-4.0"
    cff = yaml.safe_load((tmp_path / "archive" / "CITATION.cff").read_text())
    assert cff["version"] == "0.2.0" and str(cff["date-released"]) == "2026-11-01"
    assert cff["authors"] == yaml.safe_load((KIT / "CITATION.cff").read_text())["authors"]
    assert cff["title"] == zenodo["title"] and "LCI database" in cff["message"]  # one work, not the whole library
    assert "version" not in yaml.safe_load((KIT / "CITATION.cff").read_text())  # the repository's file is not changed
    assert release_metadata.main(["--version", "v1", "--out", str(tmp_path)]) == 1
    workflow = (KIT / ".github" / "workflows" / "release.yml").read_text()
    assert re.search(r"^on:\n  workflow_dispatch:\n", workflow, re.MULTILINE)  # started by hand only
    assert "contents: read" in workflow and "DEPLOY_ENABLED" not in workflow
