"""polyamide-66-1 (#521): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML, and the
statements the folder makes in DESIGN.md, README.md, process.yaml, the design basis and lca/ are
checked against them and against the EU POL BREF (2006, chapter 9):

- the salt solution is the BREF's 52 wt%, concentrated to its example 70 wt%, the mass taken to
  its about 275 C, the melt left at 0.2 wt% water;
- the polycondensation closes the element balance per repeat unit and converts 0.995 of the
  salt; the diamine's excess is what the steam strips, from the BREF's COD;
- the stated specific consumptions and the heat follow from the streams and lie where the
  folder says against the BREF's ranges;
- the recipe's batch makes the flowsheet's year-average rate;
- the hot oil sits above the temperatures it heats, the MTTs above the reactions';
- every energy stream has a duty, every flowsheet terminal reaches the LCI;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.13.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "polyamide-66-1"
ATOMS = {"C": 12.011, "H": 1.008, "N": 14.007, "O": 15.999}


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def components() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def mw(components) -> dict[str, float]:
    return {cid: c["molar_mass"] for cid, c in components.items()}


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


def _step(sheet: dict, sid: str) -> dict:
    return next(s for s in sheet["steps"] if s["id"] == sid)


def _kg(streams, mw, sid: str) -> dict[str, float]:
    state = streams[sid]
    flow = state["flow"]["value"]
    values = state["composition"]["values"]
    if state["composition"]["basis"] == "mole_fraction":
        mean = sum(x * mw[c] for c, x in values.items())
        return {c: flow * x * mw[c] / mean for c, x in values.items()}
    return {c: flow * x for c, x in values.items()}


def _fraction(streams, mw, sid: str, comp: str) -> float:
    kg = _kg(streams, mw, sid)
    return kg.get(comp, 0.0) / sum(kg.values())


def _formula_mass(formula: str) -> float:
    import re

    return sum(ATOMS[el] * (int(n) if n else 1) for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula))


def test_molar_masses_and_the_polycondensation_balance(components, mw):
    for cid, comp in components.items():
        assert comp["molar_mass"] == pytest.approx(_formula_mass(comp["formula"]), abs=2e-3), cid
    reactions = {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}
    for rid, reaction in reactions.items():
        assert sum(n * mw[c] for c, n in reaction["stoichiometry"].items()) == pytest.approx(0.0, abs=1e-3), rid
    assert reactions["POLY"]["conversion"]["value"] == 0.995
    # SRC-2 Table 1: -7870 cal/mol of links, two links per repeat unit
    assert reactions["POLY"]["heat_of_reaction"]["value"] == pytest.approx(-7870 * 4.184 * 2, abs=1.0)


def test_salt_concentrations_and_temperatures_follow_the_bref(sheet, streams, mw):
    assert _fraction(streams, mw, "S5", "AHSALT") == pytest.approx(0.52, abs=5e-4)  # 52 to 53 %
    assert _fraction(streams, mw, "S7", "AHSALT") == pytest.approx(0.70, abs=5e-4)  # e.g. 70 %
    assert streams["S5"]["temperature"]["value"] == pytest.approx(338.15)  # 65 C
    assert streams["S7"]["temperature"]["value"] == pytest.approx(383.15)  # about 110 C
    assert streams["S8"]["temperature"]["value"] == pytest.approx(548.15)  # about 275 C
    assert _fraction(streams, mw, "S11", "H2O") == pytest.approx(0.002, abs=5e-5)
    assert _fraction(streams, mw, "S11", "PA66") == pytest.approx(0.9922, abs=5e-5)
    assert _fraction(streams, mw, "S11", "AHSALT") == pytest.approx(0.0058, abs=5e-5)
    assert "99.22 wt% polymer" in _text("process/design-basis.yaml")
    assert _fraction(streams, mw, "S11", "HMDA") == pytest.approx(0.0, abs=1e-9)


def test_diamine_excess_is_the_bref_cod_as_diamine(streams, mw):
    pellets = streams["S11"]["flow"]["value"]
    stripped = _kg(streams, mw, "S13")["HMDA"] / pellets * 1000  # kg per t of pellets
    thod = 8.5 * 2 * ATOMS["O"] / mw["HMDA"]  # g O2 per g diamine, to CO2, water and ammonia
    assert stripped == pytest.approx(6.3 / thod, rel=2e-3)  # COD 6300 g/t, mid of 5300 to 7300
    assert stripped == pytest.approx(2.69, abs=0.005)
    assert "2.69 kg per t" in _text("DESIGN.md")
    ratio = (_kg(streams, mw, "S4")["HMDA"] / mw["HMDA"]) / (_kg(streams, mw, "S1")["AA"] / mw["AA"])
    assert ratio == pytest.approx(1.005247, abs=2e-6)


def test_specific_consumptions_and_energy(streams, mw):
    pellets = streams["S11"]["flow"]["value"]
    stated = {"S1": 0.644, "S4": 0.515, "S2": 1.064, "S13": 1.223}
    for sid, value in stated.items():
        assert streams[sid]["flow"]["value"] / pellets == pytest.approx(value, abs=6e-4), sid
    monomers = (streams["S1"]["flow"]["value"] + streams["S4"]["flow"]["value"]) / pellets
    assert monomers == pytest.approx(1.159, abs=5e-4)
    assert monomers < 1.165  # below the BREF's batch AH salt per t (Table 9.3), as D-004 says
    oil = sum(streams[q]["duty"]["value"] for q in ("Q3", "Q4", "Q5"))
    assert oil / pellets == pytest.approx(0.859, abs=5e-4)
    delivered = (oil + streams["Q2"]["duty"]["value"] + sum(streams[p]["duty"]["value"] for p in ("P1", "P2", "P3", "P4")))
    assert delivered / pellets * 3.6 == pytest.approx(3.52, abs=5e-3)  # D-009
    gj_per_t = delivered / pellets * 3.6
    assert 3.3 <= gj_per_t <= 7.7  # BREF Table 9.8, batch PA66 total energy
    assert gj_per_t < 5.05  # below Table 9.3's batch range, as D-009 says
    assert "0.859 kWh/kg" in _text("process.yaml")
    assert "3.52 MJ/kg" in _text("DESIGN.md")


def test_recipe_makes_the_flowsheet_rate(streams):
    recipe = _load("process/recipe.yaml")
    batch = recipe["batch_size"]["value"]
    autoclave = next(u for u in recipe["unit_procedures"] if u["id"] == "AUTOCLAVE")
    cycle = sum(op["duration"]["value"] for op in autoclave["operations"])
    assert cycle == pytest.approx(5.25)
    batches = recipe["hours_per_year"]["value"] / cycle
    assert batches == pytest.approx(1508.6, abs=0.05)
    assert batch * batches / recipe["hours_per_year"]["value"] == pytest.approx(streams["S11"]["flow"]["value"], rel=2e-4)
    assert streams["S11"]["flow"]["value"] * 7920 / 1000 == pytest.approx(8000.0, rel=1e-4)
    assert "5303.03 kg per batch, 1508.6 batches a year" in _load("lca/lca.yaml")["technology"]
    assert "1508.6 batches/a of 5303.03 kg" in _text("process.yaml")


def test_steam_bleed_takes_the_water_to_s9s_declared_state(sheet, streams, mw):
    # IAPWS-95 (chemicals 1.5.2): liquid at 383.15 K, 1750 kPa to vapour at 548.15 K, 101.325 kPa
    assert streams["S9"]["temperature"]["value"] == pytest.approx(548.15)
    assert streams["S9"]["pressure"]["value"] == pytest.approx(101.325)
    water = _kg(streams, mw, "S9")["H2O"] / 3600.0  # kg/s
    hmda = _kg(streams, mw, "S9")["HMDA"] / mw["HMDA"] / 3600.0  # kmol/s
    q4_liquid = water / mw["H2O"] * 75.4 * (548.15 - 383.15)
    expected = water * (3024.3414 - 462.5848) * 18.015268 / mw["H2O"] - q4_liquid + hmda * 41968.0
    assert streams["Q5"]["duty"]["value"] == pytest.approx(expected, rel=1e-3)


def test_heating_media_and_hazard_limits(sheet):
    feeds = {f["id"]: f for f in sheet["feeds"]}
    oil = feeds["HOTOIL"]["utility"]
    assert oil["return_temperature"]["value"] - oil["min_approach"]["value"] >= 548.15
    r101, r201 = _step(sheet, "R101"), _step(sheet, "R201")
    assert r101["hazard"]["mtt"] > 338.15 and r101["reactor"] == "semibatch"
    assert 548.15 < r201["hazard"]["mtt"] < oil["supply_temperature"]["value"]
    assert r101["batch"]["dosing"][0]["stream"] == "S4"
    # the autoclave's design temperature covers the hot oil's supply (D-011)
    r_201 = next(e for e in _load("equipment/equipment-list.yaml")["equipment"] if e["tag"] == "R-201")
    assert "design temperature 623 K" in r_201["notes"] and 623.15 > oil["supply_temperature"]["value"]


def test_every_energy_stream_has_a_duty_and_the_lci_is_complete(sheet, streams):
    energy = [s["id"] for s in sheet["streams"] if s.get("kind") == "energy"]
    assert energy and all(streams[e]["duty"]["value"] > 0 for e in energy)
    to_cw = {s["id"] for s in sheet["streams"] if s.get("kind") == "energy" and s["to"].startswith("CW.")}
    assert to_cw == {"Q1", "Q6", "Q7"}
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        keys = {row["key"] for row in csv.DictReader(fh)}
    terminals = {f"feed:{f['id']}" for f in sheet["feeds"]} | {f"product:{p['id']}" for p in sheet["products"]}
    assert terminals <= keys
    manifest = _load("process.yaml")
    listed = {c["inventory_key"] for group in manifest["chemistry"].values() for c in group}
    assert terminals <= listed | {"product:PA66"}
    assert "consumable:nitrogen" in listed


def test_public_licence_and_core_version():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["maturity"] == "concept"
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.13"
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:AAF"]["dataset"]["path"].startswith("processes/adipic-acid-1/")
    assert (KIT / mappings["feed:AAF"]["dataset"]["path"]).exists()
