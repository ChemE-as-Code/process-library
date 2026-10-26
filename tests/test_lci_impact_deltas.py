"""Reference-impact deltas of the LCI change report (``build_lci.py --previous``,
``scripts/reference_impacts.py``): core's packaged GWP100 on the Atlas foreground, no background."""

from __future__ import annotations

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
import reference_impacts  # noqa: E402

LIBRARY = KIT / "tests" / "fixtures" / "library"
H2 = "fixture-electrolysis:fixture-electrolysis:product:H2"
O2 = H2.replace(":H2", ":O2")
NH3 = "fixture-ammonia:fixture-ammonia-hb:product:ammonia"
GWP = "ipcc2021-gwp100"
#: fixture-electrolysis: kg of product (H2 41.7 + O2 333.6, mass allocation) per basis
PRODUCT_MASS = 41.7 + 333.6
#: fixture-ammonia: kg of hydrogen (from fixture-electrolysis, prefer_atlas) per kg of ammonia
H2_PER_NH3 = 178.0 / 1000.0
#: fossil CO2 in air: its biosphere3 identity as core's crosswalk and lci/mappings.yaml record it
CO2_FLOW = [{"list": "biosphere3", "uuid": "349b29d1-3e58-4c66-98b9-9d1a076efd2e", "name": "Carbon dioxide, fossil", "categories": ["air"], "unit": "kg"}]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _edit(path: Path, change) -> None:
    data = yaml.safe_load(path.read_text())
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _co2(amount: float):
    def change(d):
        d["exchanges"] = [e for e in d["exchanges"] if e["key"] != "emission:CO2"]
        d["exchanges"].append({"key": "emission:CO2", "type": "emission", "amount": amount, "unit": "kg", "cas": "124-38-9", "flow": CO2_FLOW})

    return change


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    return copy


@pytest.fixture
def core():
    return pytest.importorskip("chemeascode.domains.assessment.lca.methods")


def _electrolysis(library: Path) -> Path:
    return library / "processes" / "fixture-electrolysis" / "lca" / "dataset.yaml"


def _impacts(changes: dict) -> dict[str, dict]:
    return {code: entry for d in changes["datasets"] for code, entry in d.get("impacts", {}).items()}


def test_an_exchange_change_gives_the_expected_gwp_delta(library: Path, tmp_path: Path, core) -> None:
    co2 = core.factor(GWP, "124-38-9", "air", "fossil")  # read from core, not restated here
    _edit(_electrolysis(library), _co2(2.0))
    assert build_lci.build(library, tmp_path / "v1", "0.1.0", commit="one").errors == []
    _edit(_electrolysis(library), _co2(3.0))
    assert build_lci.build(library, tmp_path / "v2", "0.2.0", commit="two", previous=tmp_path / "v1").errors == []

    changes = _json(tmp_path / "v2" / "lci" / "changes.json")
    impact = changes["impact"]
    assert impact["status"] == "computed"
    assert [c["id"] for c in impact["categories"]] == [GWP] and impact["categories"][0]["unit"] == "kg CO2-eq"
    assert "IPCC" in impact["categories"][0]["source"] and "cheme-as-code" in impact["categories"][0]["factors"]
    assert impact["background"]["id"] == "none-atlas-foreground-only" and impact["background"]["excluded"]

    impacts = _impacts(changes)
    for code in (H2, O2):  # mass allocation: the same per kg of either product
        value = impacts[code][GWP]
        assert value["previous"] == pytest.approx(2.0 * co2 / PRODUCT_MASS)
        assert value["current"] == pytest.approx(3.0 * co2 / PRODUCT_MASS)
        assert value["delta"] == pytest.approx(1.0 * co2 / PRODUCT_MASS)
        assert value["relative_change"] == pytest.approx(0.5)
    # the ammonia dataset is unchanged, but its hydrogen comes from the Atlas electrolysis
    ammonia = impacts[NH3]
    assert next(d for d in changes["datasets"] if d["dataset"] == "fixture-ammonia-hb")["status"] == "unchanged"
    assert ammonia[GWP]["delta"] == pytest.approx(H2_PER_NH3 * co2 / PRODUCT_MASS)
    # through the Atlas hydrogen market (#76), which takes the electrolysis H2
    assert ammonia["atlas_upstream"] == [H2, "market:hydrogen:GLO"]
    # what is left out is stated per activity: background links and uncharacterised flows
    assert any(i.startswith("market for electricity, medium voltage") for i in impacts[H2]["excluded"]["background_inputs"])
    assert impacts[H2]["excluded"]["uncharacterised_flows"] == ["Hydrogen (air): not in core's elementary-flow crosswalk"]
    assert set(impacts[H2]["excluded"]["background_inputs"]) <= set(ammonia["excluded"]["background_inputs"])

    text = (tmp_path / "v2" / "lci" / "CHANGES.md").read_text()
    assert "## Reference impacts" in text and "No background database" in text and "Excluded (contributes 0)" in text
    assert f"| fixture-electrolysis | fixture-electrolysis | `{H2}` |" in text and "+50.00 %" in text

    # unchanged input: every delta is zero
    assert build_lci.build(library, tmp_path / "v3", "0.2.1", commit="two", previous=tmp_path / "v2").errors == []
    again = _impacts(_json(tmp_path / "v3" / "lci" / "changes.json"))
    assert set(again) == {H2, O2, NH3}
    assert all(e[GWP]["delta"] == 0.0 and e[GWP]["relative_change"] == 0.0 for e in again.values())


def test_added_and_removed_datasets_are_reported_without_a_delta(library: Path, tmp_path: Path, core) -> None:
    assert build_lci.build(library, tmp_path / "v1", "0.1.0", commit="one").errors == []
    path = library / "processes" / "fixture-ammonia" / "lca" / "datasets" / "ammonia.yaml"
    _edit(path, lambda d: d.update(id="fixture-ammonia-hb2", title="Fixture: Haber-Bosch loop, second"))
    assert build_lci.build(library, tmp_path / "v2", "0.2.0", commit="two", previous=tmp_path / "v1").errors == []

    changes = _json(tmp_path / "v2" / "lci" / "changes.json")
    datasets = {d["dataset"]: d for d in changes["datasets"]}
    assert datasets["fixture-ammonia-hb"]["status"] == "removed" and datasets["fixture-ammonia-hb2"]["status"] == "added"
    (removed,) = datasets["fixture-ammonia-hb"]["impacts"].values()
    (added,) = datasets["fixture-ammonia-hb2"]["impacts"].values()
    assert removed["status"] == "removed" and removed[GWP]["previous"] == 0.0 and removed[GWP]["current"] is None
    assert added["status"] == "added" and added[GWP]["previous"] is None and added[GWP]["current"] == 0.0
    assert "delta" not in removed[GWP] and "delta" not in added[GWP]
    assert datasets["fixture-electrolysis"]["impacts"][H2][GWP]["delta"] == 0.0
    text = (tmp_path / "v2" / "lci" / "CHANGES.md").read_text()
    assert "| removed | - |" in text and "| added | - |" in text


def test_without_core_the_report_says_the_impacts_are_not_computed(library: Path, tmp_path: Path, monkeypatch) -> None:
    def missing():
        raise reference_impacts.Unavailable("core's packaged characterisation is not installed (cheme-as-code; test)")

    monkeypatch.setattr(reference_impacts, "_core", missing)
    assert build_lci.build(library, tmp_path / "v1", "0.1.0", commit="one").errors == []
    assert build_lci.build(library, tmp_path / "v2", "0.2.0", commit="two", previous=tmp_path / "v1").errors == []
    changes = _json(tmp_path / "v2" / "lci" / "changes.json")
    assert changes["impact"]["status"].startswith("not computed: core's packaged characterisation is not installed")
    assert not any("impacts" in d for d in changes["datasets"])
    assert "Reference impacts not computed" in (tmp_path / "v2" / "lci" / "CHANGES.md").read_text()


def test_solve_handles_an_atlas_loop() -> None:
    # a -> b -> a with 0.5 each: h_a = 1 + 0.5 h_b, h_b = 0.5 h_a  ->  h_a = 4/3
    solved = reference_impacts._solve([[1.0, -0.5], [-0.5, 1.0]], [[1.0], [0.0]])
    assert solved[0][0] == pytest.approx(4 / 3) and solved[1][0] == pytest.approx(2 / 3)
    assert reference_impacts._solve([[1.0, -1.0], [-1.0, 1.0]], [[1.0], [0.0]]) is None
