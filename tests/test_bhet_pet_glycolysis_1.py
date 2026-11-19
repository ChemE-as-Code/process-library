"""bhet-pet-glycolysis-1 (#516): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML, and the
statements the folder makes in DESIGN.md, README.md, process.yaml and lca/ are checked against
them and against the source's Example 2 (EP 0 723 951 A1, method B):

- the charge holds 2 kg of glycol and 1.5 g of zinc acetate per kg of PET, the redissolution
  6 kg of water per kg of crude BHET;
- the conversion split is Example 2's (45 g of oligomers per 300 g PET), and the stated yield,
  purity and specific consumptions follow from the streams;
- the crystallizers sit at the source's temperatures, the second crop at BHET's water solubility;
- the recipe's batch makes the flowsheet's year-average rate;
- the heating media sit above the temperatures they heat, the MTT at the glycol's boiling point;
- every energy stream has a duty, every flowsheet terminal reaches the LCI;
- the process is public with CC-BY-4.0, requires cheme-as-code 1.13 and is in the registry,
  coverage and REFERENCE.md.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "bhet-pet-glycolysis-1"
M_PET, M_BHET, M_DIMER = 192.17, 254.238, 446.408


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


def _bhet(streams, mw, sid: str) -> float:
    kg = _kg(streams, mw, sid)
    return kg.get("BHET", 0.0) + kg.get("BHET_S", 0.0)


def test_charge_and_water_follow_the_source(streams, mw):
    charge = _kg(streams, mw, "S4")
    assert charge["EG"] / charge["PET"] == pytest.approx(2.0, rel=1e-3)
    assert charge["ZNAC"] / charge["PET"] == pytest.approx(0.0015, rel=1e-3)
    water = _kg(streams, mw, "S15")["H2O"] / _kg(streams, mw, "S13")["BHET_S"]
    assert water == pytest.approx(6.0, rel=1e-3)
    assert 1.999 <= charge["EG"] / charge["PET"] <= 3.0  # SRC-3's preferred range
    assert 5.999 <= water <= 8.0


def test_conversion_split_is_example_two():
    reactions = {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}
    oligomer_share = 45.0 / M_DIMER * 2 / (300.0 / M_PET)  # Example 2: 45 g of oligomers per 300 g PET
    assert reactions["OLF"]["conversion"]["value"] == pytest.approx(oligomer_share, abs=0.002)
    assert reactions["GLY"]["conversion"]["value"] + reactions["OLF"]["conversion"]["value"] == pytest.approx(1.0)
    assert reactions["DEP"]["conversion"]["value"] + reactions["DSO"]["conversion"]["value"] == pytest.approx(1.0)
    for r in reactions.values():
        assert r["heat_of_reaction"]["value"] == 0.0 and r["heat_of_reaction"]["provenance"] == "assumed"


def test_yield_purity_and_consumptions(streams, mw):
    product = _kg(streams, mw, "S22")
    total = sum(product.values())
    assert _bhet(streams, mw, "S22") / total == pytest.approx(0.998, abs=5e-4)
    pet = _kg(streams, mw, "S1")["PET"]
    molar_yield = (_bhet(streams, mw, "S22") / M_BHET) / (pet / M_PET)
    assert molar_yield == pytest.approx(0.978, abs=5e-4)
    assert "97.8 %" in _text("process.yaml") and "97.8 %" in _text("README.md")
    per_kg = {
        "flake": streams["S1"]["flow"]["value"] / total,
        "glycol": streams["S2"]["flow"]["value"] / total,
        "water": streams["S31"]["flow"]["value"] / total,
    }
    assert per_kg["flake"] == pytest.approx(0.776, abs=5e-4)
    assert per_kg["glycol"] == pytest.approx(0.315, abs=5e-4)
    assert per_kg["water"] == pytest.approx(0.319, abs=1e-3)
    assert per_kg["flake"] > M_PET / M_BHET  # above the stoichiometric floor
    for text in ("0.776 kg", "0.315 kg"):
        assert text in _text("README.md")


def test_crystallizers_at_the_source_temperatures(sheet, streams, mw):
    assert _step(sheet, "CR201")["crystallizer"]["temperature"] == pytest.approx(343.15)
    assert _step(sheet, "CR202")["crystallizer"]["temperature"] == pytest.approx(288.15)
    assert _step(sheet, "CR203")["crystallizer"]["temperature"] == pytest.approx(353.15)
    second = _step(sheet, "CR204")["crystallizer"]
    assert second["temperature"] == pytest.approx(288.15)
    assert second["solubility"]["value"] == pytest.approx(0.005)
    # the second mother liquor leaves saturated at 0.005 kg BHET per kg water
    ml2 = _kg(streams, mw, "S19")
    assert ml2["BHET"] / ml2["H2O"] == pytest.approx(0.005, rel=1e-3)
    # the redissolution stays below its lower-bound solubility
    s16 = _kg(streams, mw, "S16")
    assert s16["BHET"] / s16["H2O"] < _step(sheet, "CR203")["crystallizer"]["solubility"]["value"]
    assert s16.get("BHET_S", 0.0) == pytest.approx(0.0, abs=1e-6)


def test_recipe_matches_the_flowsheet_rate(streams):
    recipe = _load("process/recipe.yaml")
    assert recipe["batch_size"]["stream"] == "S22"
    rate = streams["S22"]["flow"]["value"]
    cycle = 6.248  # h, the recipe's cycle (cheme process recipe)
    assert recipe["batch_size"]["value"] / cycle == pytest.approx(rate, rel=2e-3)
    assert rate * recipe["hours_per_year"]["value"] / 1000 == pytest.approx(5000, rel=1e-3)
    assert "1268 batches" in _text("process.yaml")


def test_heating_media_and_mtt(sheet):
    feeds = {f["id"]: f for f in sheet["feeds"]}
    hps = feeds["HPS"]["utility"]["supply_temperature"]["value"]
    lps = feeds["LPS"]["utility"]["supply_temperature"]["value"]
    assert hps > 470.15 + feeds["HPS"]["utility"]["min_approach"]["value"]
    assert lps > 353.15 + feeds["LPS"]["utility"]["min_approach"]["value"]
    hazard = _step(sheet, "R101")["hazard"]
    eg = next(c for c in _load("process/materials.yaml")["components"] if c["id"] == "EG")
    assert hazard["mtt"] == pytest.approx(eg["normal_boiling_point"])


def test_energy_streams_have_duties_and_the_lci_is_complete(sheet):
    energy = [s for s in sheet["streams"] if s.get("kind") == "energy"]
    assert energy and all("duty" in s["state"]["design"] for s in energy)
    terminals = {f["id"] for f in sheet["feeds"]} | {p["id"] for p in sheet["products"]}
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        keys = {row["key"].split(":", 1)[1] for row in csv.DictReader(fh)}
    assert terminals <= keys
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:EGF"]["dataset"]["path"] == "processes/ethylene-glycol-1/lca/dataset.yaml"
    assert (KIT / mappings["feed:WATF"]["dataset"]["path"]).exists()


def test_column_dominates_the_heat(streams):
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        rows = {row["key"]: float(row["quantity"]) for row in csv.DictReader(fh)}
    heat = rows["feed:HPS"] + rows["feed:LPS"]
    assert heat == pytest.approx(7.58, abs=0.01)
    assert "7.6 kWh" in _text("README.md") and "6.7 kWh" in _text("README.md")


def test_manifest_publication_and_shared_rows():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["maturity"] == "concept"
    assert "cheme-as-code>=1.13" in _text("plant.yaml")
    slugs = {c["slug"] for c in yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))["chemicals"]}
    for flow in manifest["chemistry"]["inputs"] + manifest["chemistry"]["outputs"]:
        assert flow["chemical"].split("/")[0] in slugs
    coverage = yaml.safe_load((KIT / "coverage.yaml").read_text(encoding="utf-8"))["entries"]
    entry = next(e for e in coverage if e["id"] == "bhet")
    assert entry["covered_by"][0]["process"] == "bhet-pet-glycolysis-1"
    assert "bhet-pet-glycolysis-1" in (KIT / "REFERENCE.md").read_text(encoding="utf-8")
    assert "Closes" not in _text("DESIGN.md")  # the issue is named, not closed, in the folder
    assert "#516" in _text("DESIGN.md")
