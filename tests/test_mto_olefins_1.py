"""mto-olefins-1 (#466): the folder's stated numbers against its own files.

Fast, without core: the flowsheet (propagated by core, the rest given by scripts/balance.py),
the reactions, the materials and the LCI dataset are read as YAML, and the statements the folder
makes in DESIGN.md, README.md and process.yaml are checked against them:

- R101's selectivities are US 7 138 557 B2 Table 1's carbon shares (with the stated split of
  the "others"), its conversion the patent's 99.5 %, and they use up exactly the methanol
  converted;
- every reaction balances in its elements, and each given heat of reaction is the sum of the
  materials' ideal-gas formation enthalpies (coke as graphite, 0);
- the products' purities, rates and the methanol per kg of ethylene and propylene are the ones
  the texts state;
- the regeneration air gives 2 vol% O2 in the dry flue gas, the caustic 3 mol NaOH per mol CO2;
- every heat stream has a duty, Q2 and Q3 are core's conversion-step duties and the script's
  are given as ASSUMED with its source;
- the LCI's methanol is linked to methanol-1 and its CO2 is the regenerator's;
- the source register names the packages as single facts, not open data, and the retracted
  article is used for no number;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "mto-olefins-1"

# US 7 138 557 B2, Table 1, mass-% of methanol equivalent read as carbon shares (DESIGN.md D-005);
# the 1.29 of "others" split ASSUMED into CO 0.45, CO2 0.25, butadiene 0.59.
TABLE_1 = {"CH4": 0.85, "C2H4": 33.50, "C2H6": 0.65, "C3H6": 44.50, "C3H8": 0.30, "C4H8": 9.5,
           "C4H10": 0.01, "C5H10": 5.00, "COKE": 2.85, "DME": 1.05, "CO": 0.45, "CO2": 0.25,
           "C4H6": 0.59}
UNREACTED = 0.50
ELEMENT = re.compile(r"([A-Z][a-z]?)(\d*)")


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def materials() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


@pytest.fixture(scope="module")
def steps(sheet) -> dict[str, dict]:
    return {s["id"]: s for s in sheet["steps"]}


@pytest.fixture(scope="module")
def reactions() -> dict[str, dict]:
    return {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}


def _carbon(formula: str) -> int:
    atoms = {e: int(n or 1) for e, n in ELEMENT.findall(formula)}
    return atoms.get("C", 0)


def _kmol(state: dict, materials: dict) -> dict[str, float]:
    comp = state["composition"]
    assert comp["basis"] == "mole_fraction"
    x = comp["values"]
    mw = sum(v * materials[c]["molar_mass"] for c, v in x.items())
    total = state["flow"]["value"] / mw
    return {c: v * total for c, v in x.items()}


def test_r101_selectivities_are_the_patents_carbon_shares(steps, materials):
    sel = steps["R101"]["selectivity"]
    assert sel["key"] == "MEOH"
    assert sel["conversion"] == pytest.approx(1 - UNREACTED / 100)
    assert sel["provenance"] == "given"
    assert "US 7 138 557 B2" in sel["source"]
    converted = sum(TABLE_1.values())
    assert converted == pytest.approx(100 - UNREACTED)
    for comp, share in TABLE_1.items():
        expected = share / converted / _carbon(materials[comp]["formula"])
        assert sel["products"][comp] == pytest.approx(expected, abs=5e-10), comp  # 9 decimals


def test_the_selectivities_use_up_the_converted_methanol(steps, reactions, materials):
    sel = steps["R101"]
    used = 0.0
    for rid in sel["reactions"]:
        stoich = reactions[rid]["stoichiometry"]
        product = next(c for c in stoich if c in sel["selectivity"]["products"])
        used += sel["selectivity"]["products"][product] * -stoich["MEOH"] / stoich[product]
    assert used == pytest.approx(1.0, abs=1e-6)


def test_every_reaction_balances_and_its_heat_is_the_formation_enthalpies(reactions, materials):
    for rid, r in reactions.items():
        totals: dict[str, float] = {}
        for comp, nu in r["stoichiometry"].items():
            for element, n in ELEMENT.findall(materials[comp]["formula"]):
                totals[element] = totals.get(element, 0.0) + nu * int(n or 1)
        assert all(abs(v) < 1e-9 for v in totals.values()), (rid, totals)
        heat = r.get("heat_of_reaction")
        if heat is None:
            continue
        hf = {c: (materials[c]["ideal_gas"]["dHf_298"] if "ideal_gas" in materials[c] else 0.0)
              for c in r["stoichiometry"]}
        assert heat["temperature"] == 298.15
        assert heat["value"] == pytest.approx(
            sum(nu * hf[c] for c, nu in r["stoichiometry"].items()), abs=1.0), rid


def test_the_products_and_the_methanol_per_kg_are_the_stated_ones(streams, materials):
    eth = _kmol(streams["S27"], materials)
    pro = _kmol(streams["S31"], materials)
    assert eth["C2H4"] / sum(eth.values()) == pytest.approx(0.99971, abs=5e-5)
    assert pro["C3H6"] / sum(pro.values()) == pytest.approx(0.99840, abs=5e-5)
    e, p = streams["S27"]["flow"]["value"], streams["S31"]["flow"]["value"]
    assert e == pytest.approx(33267, abs=5)
    assert p == pytest.approx(43703, abs=5)
    meoh = streams["S1"]["flow"]["value"]
    assert meoh == 225000.0
    assert meoh / (e + p) == pytest.approx(2.923, abs=5e-4)
    design = _text("DESIGN.md")
    assert "2.92 kg methanol per kg of ethylene and propylene" in design
    assert "ethylene 99.97 mol%" in design and "propylene 99.84 mol%" in design
    assert "2.92 kg of methanol per kg of the two" in _text("README.md")


def test_the_air_gives_two_percent_oxygen_and_the_caustic_three_to_one(streams, materials):
    flue = streams["S10"]["composition"]["values"]
    dry = {c: v for c, v in flue.items() if c != "H2O" and v}
    assert dry["O2"] / sum(dry.values()) == pytest.approx(0.02, abs=2e-4)
    co2 = _kmol(streams["S15"], materials)["CO2"]
    caustic = streams["S16"]
    naoh = caustic["flow"]["value"] * caustic["composition"]["values"]["NAOH"] / materials["NAOH"]["molar_mass"]
    assert naoh / co2 == pytest.approx(3.0, rel=2e-3)


def test_every_heat_stream_has_a_duty_with_its_provenance(sheet):
    for s in sheet["streams"]:
        if s.get("kind") != "energy":
            continue
        duty = s["state"]["design"]["duty"]
        if s["id"] in ("Q2", "Q3"):
            assert duty["provenance"] == "calculated"
            assert duty["source"].startswith("cheme process propagate: conversion duty")
        else:
            assert duty["provenance"] == "assumed"
            assert duty["source"].startswith("scripts/balance.py")
        assert duty["value"] > 0, s["id"]


def test_the_lci_links_methanol_and_counts_the_regenerator_co2(streams, materials):
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:MEOH"]["dataset"]["path"] == "processes/methanol-1/lca/dataset.yaml"
    assert "feed:CAUSTIC" not in mappings
    dataset = _load("lca/dataset.yaml")
    co2 = next(x for x in dataset["exchanges"] if x["key"] == "emission:CO2")
    coke = _kmol(streams["S7"], materials)["COKE"] if streams["S7"]["composition"]["basis"] == "mole_fraction" else None
    assert coke == pytest.approx(streams["S7"]["flow"]["value"] / materials["COKE"]["molar_mass"], rel=1e-6)
    flue_co2 = _kmol(streams["S10"], materials)["CO2"] * materials["CO2"]["molar_mass"]
    assert flue_co2 == pytest.approx(coke * materials["CO2"]["molar_mass"], rel=1e-4)
    assert co2["amount"] == pytest.approx(flue_co2, rel=1e-3)
    assert "8.93 t/h" in _text("process.yaml")


def test_the_source_register_keeps_the_package_and_retraction_rules():
    rows = {line.split("|")[1].strip(): line for line in (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines()
            if line.startswith("| SRC-")}
    assert "not open data" in rows["SRC-6"] and "ADR 0037" in rows["SRC-6"]
    assert "retracted" in rows["SRC-8"] and "no number from it is used" in rows["SRC-8"]
    for rel in ("process/flowsheet.yaml", "process/reactions.yaml", "scripts/balance.py", "lca/lca.yaml"):
        assert "eng.2020.12.001" not in (PROCESS / rel).read_text(encoding="utf-8"), rel


def test_public_cc_by_and_core_version():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
