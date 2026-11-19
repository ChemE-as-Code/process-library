"""caprolactam-1 (#464): the folder's hand-written numbers against its own model.

From the files alone (the flowsheet's calculated streams, the materials' molar masses), the test
checks what the folder states by hand:

- the hydroxylammonium sulfate feed is hydroxylamine-1's product as that entry gives it, and the
  plant takes all of it (D-002, D-003);
- the feeds' targets hold: the oxime melt's 4.6 wt% water and 0.6 wt% cyclohexanone (US
  4,031,139), the oleum's 1.17 kg per kg melt with 32 wt% SO3 (US 4,804,754), the crude lactam's
  30 wt% water and the neutraliser's 40 wt% ammonium sulfate solution (US 4,804,754), the 22 wt%
  extract and the 28 wt% aqueous lactam (US 6,448,395 B1);
- the rearrangement's 98.9 % yield and the free SO3 inside 1 to 14 wt% (D-006);
- the ammonium sulfate per kg from the rearrangement's acid lies in US 3,852,273's 1.7 to 1.9;
- the numbers per kg in process.yaml, README.md and DESIGN.md follow from the streams;
- the hand duties carry their arithmetic, the reactors' duties are core's (ADR 0059);
- the economic shares follow from the flows at the stated relative price;
- the LCI's utilities per kg are the sums of the flowsheet's duties;
- the process is public with CC-BY-4.0 (ADR 0036), and its sources have register rows.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "caprolactam-1"
HYDROXYLAMINE = KIT / "processes" / "hydroxylamine-1"


def _yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    """A file's text with its line breaks and runs of spaces as single spaces (phrases wrap)."""
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml(PROCESS / "process/materials.yaml")["components"]}
    flowsheet = _yaml(PROCESS / "process/flowsheet.yaml")
    streams = {s["id"]: s for s in flowsheet["streams"]}
    return materials, streams, flowsheet


def _state(model, sid: str) -> dict:
    return model[1][sid]["state"]["design"]


def _flow(model, sid: str) -> float:
    return _state(model, sid)["flow"]["value"]


def _duty(model, sid: str) -> float:
    return _state(model, sid)["duty"]["value"]


def _kg(model, sid: str) -> dict[str, float]:
    """kg/h of each component of a material stream."""
    materials = model[0]
    state = _state(model, sid)
    flow = state["flow"]["value"]
    comp = state["composition"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * materials[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mm * x * materials[k]["molar_mass"] for k, x in comp["values"].items()}
    return {k: flow * w for k, w in comp["values"].items()}


def _wt(model, sid: str, comp: str) -> float:
    kg = _kg(model, sid)
    return kg.get(comp, 0.0) / sum(kg.values())


def test_feed_is_hydroxylamine_1s_whole_product(model):
    other = {s["id"]: s for s in _yaml(HYDROXYLAMINE / "process/flowsheet.yaml")["streams"]}
    prod = other["S24"]["state"]["design"]
    feed = _state(model, "S02")
    assert feed["flow"]["value"] == pytest.approx(prod["flow"]["value"], rel=1e-9)
    assert feed["composition"]["values"] == pytest.approx(prod["composition"]["values"], rel=1e-9)


def test_oxime_melt_and_oleum(model):
    assert _wt(model, "S05", "H2O") == pytest.approx(0.046, abs=2e-4)
    assert _wt(model, "S05", "CHN") == pytest.approx(0.006, abs=2e-4)
    assert _flow(model, "S07") / _flow(model, "S05") == pytest.approx(1.17, rel=1e-4)
    assert _state(model, "S07")["composition"]["values"]["SO3"] == 0.32


def test_rearrangement_yield_and_free_so3(model):
    oxm = _kg(model, "S05")["OXM"] / model[0]["OXM"]["molar_mass"]
    cpl = _kg(model, "S08")["CPL"] / model[0]["CPL"]["molar_mass"]
    assert cpl / oxm == pytest.approx(0.989, abs=1e-5)
    so3 = _wt(model, "S08", "SO3")
    assert 0.01 <= so3 <= 0.14
    assert so3 == pytest.approx(0.082, abs=0.001)


def test_neutraliser_targets(model):
    assert _wt(model, "S11", "H2O") == pytest.approx(0.30, abs=0.002)
    assert _wt(model, "S11", "AS") == pytest.approx(0.015, abs=0.001)
    assert _wt(model, "S12", "AS") == pytest.approx(0.40, abs=0.002)
    # no fresh water reaches the neutraliser: its diluents are the liquor and the condensate
    sources = {s["from"].split(".")[0] for s in model[1].values() if s.get("to", "").startswith("R301.")}
    assert sources == {"D101", "R201", "NH3F", "X601", "POWER"}


def test_extraction_targets(model):
    assert _wt(model, "S16", "CPL") == pytest.approx(0.22, abs=0.002)
    assert _wt(model, "S21", "CPL") == pytest.approx(0.28, abs=0.002)
    assert _wt(model, "S23", "H2O") == pytest.approx(0.01, abs=0.0005)


def test_ammonium_sulfate_per_kg_and_capacity(model):
    product = _flow(model, "S24")
    assert product * 8000 / 1e6 == pytest.approx(100.1, abs=0.05)
    assert _kg(model, "S24")["CPL"] == pytest.approx(product, rel=1e-9)
    # the salt formed from the rearrangement's acid (NEUT and NEUT3 in R301)
    mm = model[0]
    acid = _kg(model, "S08")
    as_rearr = (acid["H2SO4"] / mm["H2SO4"]["molar_mass"] + acid["SO3"] / mm["SO3"]["molar_mass"]) * mm["AS"]["molar_mass"]
    per_kg = as_rearr / product
    assert 1.7 <= per_kg <= 1.9
    assert f"{per_kg:.2f}" == "1.82"
    crystals = _flow(model, "S29") / product
    assert f"{crystals:.3f}" == "2.478"
    for rel in ("process.yaml", "README.md", "DESIGN.md"):
        assert "2.478" in _text(rel)
        assert "1.82" in _text(rel)


def test_feeds_per_kg_in_the_texts(model):
    product = _flow(model, "S24")
    nh3 = (_flow(model, "S03") + _flow(model, "S09")) / product
    stated = {
        "0.897": _flow(model, "S01") / product,
        "2.931": _flow(model, "S02") / product,
        "0.640": nh3,
        "1.267": _flow(model, "S07") / product,
    }
    for text, value in stated.items():
        assert f"{value:.3f}" == text
        assert text in _text("process.yaml")
        assert text in _text("DESIGN.md")


def test_hand_duties_follow_their_arithmetic(model):
    assert _duty(model, "Q4") == pytest.approx(32221 * 2257 / 3 / 3600, rel=2e-3)
    assert _duty(model, "Q8") == pytest.approx(51567 * 2257 / 3 / 3600, rel=2e-3)
    evaporated = _kg(model, "S19")["H2O"]
    assert evaporated == pytest.approx(32221, rel=2e-3)
    assert _flow(model, "S31") == pytest.approx(51567, rel=2e-3)
    lactam = _kg(model, "S24")["CPL"] / model[0]["CPL"]["molar_mass"]
    assert _duty(model, "Q6") == pytest.approx(2 * lactam * 62.3e3 / 3600 + 80, rel=2e-3)


def test_reactor_duties_are_cores(model):
    for sid, step in (("Q1", "R101"), ("Q2", "R201"), ("Q3", "R301")):
        duty = _state(model, sid)["duty"]
        assert duty["provenance"] == "calculated"
        assert duty["source"].startswith(f"cheme process propagate: conversion duty {step}")


def test_economic_shares_follow_the_flows(model):
    lca = _yaml(PROCESS / "lca/lca.yaml")
    shares = lca["allocation"]["shares"]
    value_cpl = _flow(model, "S24") * 1.0
    value_as = _flow(model, "S29") * 0.07
    assert shares["PROD"] == pytest.approx(value_cpl / (value_cpl + value_as), abs=1e-4)
    assert shares["PROD"] + shares["ASP"] == pytest.approx(1.0, abs=1e-9)


def test_lci_utilities_are_the_flowsheets_duties(model):
    rows = {r["key"]: r for r in csv.DictReader((PROCESS / "lca/inventory.csv").open(encoding="utf-8"))}
    assert float(rows["feed:POWER"]["plant"]) == pytest.approx(sum(_duty(model, f"P{i}") for i in range(1, 7)), rel=1e-4)
    assert float(rows["feed:LPS"]["plant"]) == pytest.approx(_duty(model, "Q4") + _duty(model, "Q8"), rel=1e-4)
    assert float(rows["product:CW"]["plant"]) == pytest.approx(
        sum(_duty(model, q) for q in ("Q1", "Q2", "Q3", "Q5", "Q7", "Q9")), rel=1e-4)


def test_mappings_link_library_producers():
    maps = _yaml(PROCESS / "lca/mappings.yaml")["exchanges"]
    assert maps["feed:HASF"]["dataset"]["path"] == "processes/hydroxylamine-1/lca/dataset.yaml"
    assert maps["feed:NH3F"]["dataset"]["path"] == "processes/ammonia-1/lca/dataset.yaml"
    for path in (maps["feed:HASF"]["dataset"]["path"], maps["feed:NH3F"]["dataset"]["path"]):
        assert (KIT / path).is_file()


def test_public_and_sources_registered():
    manifest = _yaml(PROCESS / "process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    design = _text("DESIGN.md")
    cited = set(re.findall(r"SRC-(\d+)", design))
    rows = set(re.findall(r"\| SRC-(\d+) \|", (PROCESS / "DESIGN.md").read_text(encoding="utf-8")))
    assert cited <= rows
    assert "open data" not in design.replace("not open data", "")


def test_utilities_per_kg_in_the_texts(model):
    product = _flow(model, "S24")
    lps = (_duty(model, "Q4") + _duty(model, "Q8")) / product
    cw = sum(_duty(model, q) for q in ("Q1", "Q2", "Q3", "Q5", "Q7", "Q9")) / product
    power = sum(_duty(model, f"P{i}") for i in range(1, 7)) / product
    for value in (lps, cw, power):
        assert f"{value:.3f}" in _text("process.yaml")
        assert f"{value:.3f}" in _text("DESIGN.md")
