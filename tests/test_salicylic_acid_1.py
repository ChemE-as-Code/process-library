"""salicylic-acid-1 (#507): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML, and the
statements the folder makes in DESIGN.md, README.md, process.yaml and lca/ are checked against
them and against the source's Example I (US 4 376 867 A):

- the charge ratio, the CO2 dose and the share taken up follow Example I (23.2 mol phenol and
  25 mol CO2 per 23.0 mol NaOH, 20.48 mol of acids formed);
- the salicylate formed per phenol charged is the source's 88 %, the by-product share its
  0.080 / 20.4, and the stated yields, purity and specific consumptions follow from the streams;
- the crystallizers' solubility is Wikipedia's, the first crop at the source's 50 to 60 C;
- the recipe's batch makes the flowsheet's year-average rate;
- the heating media sit above the temperatures they heat, the MTTs above the reactions';
- every energy stream has a duty, every flowsheet terminal reaches the LCI;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "salicylic-acid-1"


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def mw() -> dict[str, float]:
    return {c["id"]: c["molar_mass"] for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


def _step(sheet: dict, sid: str) -> dict:
    return next(s for s in sheet["steps"] if s["id"] == sid)


def _kg(streams, mw, sid: str) -> dict[str, float]:
    state = streams[sid]
    flow = state["flow"]["value"]
    comp = state["composition"]
    values = comp["values"]
    if comp["basis"] == "mole_fraction":
        mean = sum(x * mw[c] for c, x in values.items())
        return {c: flow * x * mw[c] / mean for c, x in values.items()}
    return {c: flow * x for c, x in values.items()}


def _kmol(streams, mw, sid: str, comp: str) -> float:
    return _kg(streams, mw, sid).get(comp, 0.0) / mw[comp]


def test_charge_and_co2_follow_example_one(sheet, streams, mw):
    naoh = _kmol(streams, mw, "S3", "NAOH")
    assert _kmol(streams, mw, "S2", "PHOH") / naoh == pytest.approx(23.2 / 23.0, rel=1e-4)
    assert _kmol(streams, mw, "S7", "CO2") / naoh == pytest.approx(25.0 / 23.0, rel=1e-4)
    dose = _step(sheet, "R102")["batch"]["dosing"][0]
    assert dose["time"] == 5 * 3600 and _step(sheet, "R102")["batch"]["time"] == 3600
    assert dose["absorbed"] == pytest.approx(20.48 / 23.0 * 0.999 / (25.0 / 23.0), abs=5e-6)
    # the phenoxide converted in R102 is Example I's acids per NaOH
    converted = 1 - _kmol(streams, mw, "S9", "NAOPH") / _kmol(streams, mw, "S5", "NAOPH")
    assert converted == pytest.approx(20.48 / 23.0, abs=5e-4)
    assert "R102 converts 89.0 % of the phenoxide" in _text("DESIGN.md")


def test_yield_and_by_products_match_the_source(sheet, streams, mw):
    formed = _kmol(streams, mw, "S9", "NASAL") / _kmol(streams, mw, "S2", "PHOH")
    assert formed == pytest.approx(20.4 / 23.2, abs=2e-3)
    assert "87.8 % of the phenol charged" in _text("DESIGN.md")
    by = _kmol(streams, mw, "S9", "NA4HB") / _kmol(streams, mw, "S9", "NASAL")
    assert by == pytest.approx((0.054 + 0.026) / 20.4, rel=1e-2)
    reactions = {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}
    ratio = reactions["PARA"]["rate"]["k"]["A"] / reactions["CARB"]["rate"]["k"]["A"]
    assert ratio == pytest.approx(0.080 / 20.4, rel=1e-3)


def test_isolation_purity_and_consumptions(streams, mw):
    product = _kg(streams, mw, "S22")
    total = sum(product.values())
    sa = (product["SA_S"] + product["SA"]) / mw["SA"]
    assert sa * mw["SA"] / total == pytest.approx(0.997, abs=5e-4)
    assert "99.7 wt% salicylic acid" in _text("process/design-basis.yaml")
    isolated = sa / _kmol(streams, mw, "S9", "NASAL")
    assert isolated == pytest.approx(0.966, abs=5e-4)
    assert 0.95 < isolated < 1.0  # above the source's two crops (about 95 %), below all
    overall = sa / _kmol(streams, mw, "S1", "PHOH")
    assert overall == pytest.approx(0.955, abs=5e-4)
    assert "95.5 % overall on the fresh phenol" in _text("process.yaml")
    stated = {"S1": 0.711, "S3": 0.675, "S7": 0.404, "S11": 0.429, "S8": 0.073}
    for sid, value in stated.items():
        assert streams[sid]["flow"]["value"] / total == pytest.approx(value, abs=5e-4), sid
    water = (streams["S10"]["flow"]["value"] + streams["S16"]["flow"]["value"]) / total
    assert water == pytest.approx(12.1, abs=0.05)
    assert streams["S27"]["flow"]["value"] / total == pytest.approx(13.27, abs=0.01)
    # stoichiometric phenol floor
    assert mw["PHOH"] / mw["SA"] == pytest.approx(0.681, abs=5e-4)
    assert mw["PHOH"] / mw["SA"] < stated["S1"]


def test_crystallizers_use_the_sourced_solubility(sheet):
    points = [[273.15, 0.00124], [298.15, 0.00248], [313.15, 0.00414], [348.15, 0.01741], [373.15, 0.07779]]
    for sid, temperature in {"CR201": 328.15, "CR202": 298.15, "W201": 298.15}.items():
        cryst = _step(sheet, sid)["crystallizer"]
        assert [list(p) for p in cryst["solubility"]["points"]] == points
        assert cryst["temperature"] == temperature
    assert 323.15 <= _step(sheet, "CR201")["crystallizer"]["temperature"] <= 333.15  # 50 to 60 C


def test_recipe_makes_the_flowsheet_rate(streams):
    recipe = _load("process/recipe.yaml")
    batch = recipe["batch_size"]["value"]
    batches = 357.6
    assert batch * batches / recipe["hours_per_year"]["value"] == pytest.approx(
        streams["S22"]["flow"]["value"], rel=2e-3
    )
    assert streams["S22"]["flow"]["value"] * 7920 / 1000 == pytest.approx(1000.0, rel=1e-4)
    tech = _load("lca/lca.yaml")["technology"]
    assert "2796.53 kg per batch, 357.6 batches a year" in tech
    assert "357.6 batches/a of 2796.53 kg" in _text("process.yaml")


def test_heating_media_and_mtts(sheet):
    feeds = {f["id"]: f for f in sheet["feeds"]}
    hps = feeds["HPS"]["utility"]["supply_temperature"]["value"]
    assert hps - feeds["HPS"]["utility"]["min_approach"]["value"] >= _step(sheet, "D101")["dryer"]["temperature"]
    lps = feeds["LPS"]["utility"]["supply_temperature"]["value"]
    assert lps > _step(sheet, "D201")["dryer"]["temperature"] + 10
    assert _step(sheet, "D201")["dryer"]["temperature"] < 273.15 + 76  # salicylic acid sublimes
    assert _step(sheet, "R101")["hazard"]["mtt"] > 343.15
    assert _step(sheet, "R102")["hazard"]["mtt"] > 463.15


def test_every_energy_stream_has_a_duty_and_reaches_the_lci(sheet):
    for s in sheet["streams"]:
        if s.get("kind") == "energy":
            assert s["state"]["design"]["duty"]["value"] > 0, s["id"]
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        keys = {row["key"] for row in csv.DictReader(fh)}
    for f in sheet["feeds"]:
        assert f"feed:{f['id']}" in keys, f["id"]
    for p in sheet["products"]:
        assert f"product:{p['id']}" in keys, p["id"]


def test_public_and_core_version():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert len(manifest["summary"]) <= 400
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
    mappings = _load("lca/mappings.yaml")["exchanges"]
    for key, path in {
        "feed:PHF": "processes/acetone-1/lca/dataset.yaml",
        "feed:NAOHF": "processes/chlor-alkali-1/lca/dataset.yaml",
        "feed:ACIDF": "processes/sulfuric-acid-1/lca/dataset.yaml",
    }.items():
        assert mappings[key]["dataset"]["path"] == path
        assert (KIT / path).is_file()
