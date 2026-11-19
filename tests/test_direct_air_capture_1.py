"""direct-air-capture-1 (#518): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (the steady state of scripts/dac_balance.py) are
read as YAML, and the statements the folder makes in DESIGN.md, README.md, process.yaml and
lca/lca.yaml are checked against them:

- the contactor captures 74.5 % of the air's CO2 and evaporates 4.7 t of water per t captured;
- the lean liquor holds 1.10 mol/L KOH and 0.45 mol/L K2CO3 at the stated density, and the
  carbonate swing is 0.21 mol/L;
- the calcium loop closes: CaCO3 calcined at 98 %, CaO slaked at 85 %, the purge's calcium equal
  to the seed's, the purge's potassium equal to the make-up's;
- the calciner's gas follows 5.25 GJ per t of CO2 calcined, the oxidant its ratio and purity;
- the product holds 97.0 wt% CO2 and 0.01 wt% water, and its declared air-carbon fraction is the
  calcined carbon over the product's carbon;
- the power streams are the source's specific consumptions times the flows;
- the stated specific figures per kg of product follow from the streams;
- every energy stream reaches the LCI, the air is a resource and the CO2 product a registry grade;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.13.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "direct-air-capture-1"

MW = {"CO2": 44.009, "H2O": 18.015, "KOH": 56.105, "K2CO3": 138.204, "CAOH2": 74.092,
      "CACO3": 100.086, "CAO": 56.077, "CH4": 16.043, "O2": 31.998, "N2": 28.014}


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


@pytest.fixture(scope="module")
def kg(streams):
    def flows(sid: str) -> dict[str, float]:
        state = streams[sid]
        assert state["composition"]["basis"] == "mass_fraction"
        return {k: w * state["flow"]["value"] for k, w in state["composition"]["values"].items()}

    return flows


def kmol(d: dict[str, float], c: str) -> float:
    return d[c] / MW[c]


def test_materials_match_the_test_molar_masses():
    comps = {c["id"]: c for c in _load("process/materials.yaml")["components"]}
    for cid, mw in MW.items():
        assert comps[cid]["molar_mass"] == pytest.approx(mw, abs=1e-3)


def test_contactor_capture_and_evaporation(kg):
    air, out = kg("S1"), kg("S10")
    captured = air["CO2"] - out["CO2"]
    assert captured / air["CO2"] == pytest.approx(0.745, rel=1e-3)
    assert captured / 1000 == pytest.approx(112.2, abs=0.1)
    evap = out["H2O"] - air["H2O"]
    assert evap / captured == pytest.approx(4.7, rel=2e-3)
    assert air["CO2"] / sum(air.values()) == pytest.approx(0.00060, rel=1e-3)


def test_lean_liquor_and_swing(kg, streams):
    lean = kg("S11")
    litres = sum(lean.values()) / 1.10
    assert kmol(lean, "KOH") * 1000 / litres == pytest.approx(1.10, rel=1e-3)
    assert kmol(lean, "K2CO3") * 1000 / litres == pytest.approx(0.45, rel=1e-3)
    captured = (kg("S1")["CO2"] - kg("S10")["CO2"]) / MW["CO2"]
    assert captured * 1000 / litres == pytest.approx(0.21, rel=2e-3)


def test_calcium_loop_closes(kg):
    pellets, cao, lime, purge, seed = kg("S17"), kg("S18"), kg("S16"), kg("S22"), kg("S5")
    x = kmol(pellets, "CACO3")
    assert kmol(cao, "CAO") / x == pytest.approx(0.98, rel=1e-3)
    slaked = kmol(lime, "CAOH2")
    assert slaked / kmol(cao, "CAO") == pytest.approx(0.85, rel=1e-3)
    assert kmol(purge, "CACO3") == pytest.approx(kmol(seed, "CACO3"), rel=1e-3)
    k_purge = kmol(purge, "KOH") + 2 * kmol(purge, "K2CO3")
    assert k_purge == pytest.approx(kmol(kg("S3"), "KOH"), rel=1e-3)
    # the washed pellets carry 11 wt% water and 1.8 kg K2CO3 per 100 kg CaCO3
    washed = kg("S15")
    assert washed["H2O"] / sum(washed.values()) == pytest.approx(0.11, rel=1e-3)
    assert washed["K2CO3"] / washed["CACO3"] == pytest.approx(0.018, rel=1e-3)
    # 30 wt% Ca(OH)2 slurry
    slurry = kg("S13")
    assert slurry["CAOH2"] / sum(slurry.values()) == pytest.approx(0.30, rel=1e-3)


def test_calciner_fuel_and_oxidant(kg):
    calcined = kmol(kg("S18"), "CAO") * MW["CO2"] / 1000  # t/h
    ch4 = kg("S6")["CH4"]
    assert ch4 / 1000 * 50.0 / calcined == pytest.approx(5.25, rel=1e-3)
    ox = kg("S7")
    assert sum(ox.values()) / ch4 == pytest.approx(58.5 / 13.4, rel=1e-3)
    assert ox["O2"] / sum(ox.values()) == pytest.approx(0.956, rel=1e-4)


def test_product_and_air_carbon_fraction(kg):
    prod = kg("S20")
    total = sum(prod.values())
    assert prod["CO2"] / total == pytest.approx(0.970, abs=0.001)
    assert prod["H2O"] / total == pytest.approx(0.0001, rel=1e-2)
    assert total / 1000 == pytest.approx(148.4, abs=0.1)
    air_c = kmol(kg("S18"), "CAO")
    frac = air_c / kmol(prod, "CO2")
    lca = _load("lca/lca.yaml")
    declared = lca["carbon_accounting"]["content"]["product:CO2P"]["biogenic_fraction"]
    assert declared == pytest.approx(frac, abs=2e-4)
    assert "77.6 %" in _text("README.md")


def test_power_streams_follow_the_specific_consumptions(streams, kg):
    duty = {s: streams[s]["duty"]["value"] for s in ("P1", "P2", "P3", "P4")}
    captured = (kg("S1")["CO2"] - kg("S10")["CO2"]) / 1000
    calcined = kmol(kg("S18"), "CAO") * MW["CO2"] / 1000
    product = sum(kg("S20").values()) / 1000
    assert duty["P1"] == pytest.approx((61 + 21) * captured, rel=1e-3)
    assert duty["P2"] == pytest.approx(27 * captured, rel=1e-3)
    assert duty["P3"] == pytest.approx(32 * calcined, rel=1e-3)
    assert duty["P4"] == pytest.approx(132 * product, rel=1e-3)
    assert sum(duty.values()) / captured == pytest.approx(315, abs=1)


def test_stated_specific_figures(kg, streams):
    product = sum(kg("S20").values())
    per = {
        "air CO2": (kg("S1")["CO2"] - kg("S10")["CO2"]) / product,
        "gas": kg("S6")["CH4"] / product,
        "oxygen": sum(kg("S7").values()) / product,
        "KOH": kg("S3")["KOH"] / product * 1000,
        "seed": kg("S5")["CACO3"] / product * 1000,
        "water": sum(sum(kg(s).values()) for s in ("S2", "S4", "S8")) / product,
        "power": sum(streams[s]["duty"]["value"] for s in ("P1", "P2", "P3", "P4")) / product,
        "purge": sum(kg("S22").values()) / product * 1000,
    }
    stated = {"air CO2": 0.756, "gas": 0.079, "oxygen": 0.345, "KOH": 16.3, "seed": 24.3,
              "water": 3.57, "power": 0.239, "purge": 60.6}
    for key, value in stated.items():
        assert per[key] == pytest.approx(value, rel=5e-3), key


def test_energy_streams_reach_the_lci(sheet):
    lca = _load("lca/lca.yaml")
    keys = {f["key"] for f in lca["flows"]}
    terminals = {t["id"] for t in sheet["feeds"] + sheet["products"]} - {"CO2P"}
    assert lca["functional_unit"]["product"] == "CO2P"
    for t in terminals:
        assert f"feed:{t}" in keys or f"product:{t}" in keys, t
    air = next(f for f in lca["flows"] if f["key"] == "feed:AIR")
    assert air.get("resource") is True
    co2 = next(f for f in lca["flows"] if f["key"] == "resource:CO2")
    assert co2["elementary"]["subcompartment"] == "in-air"


def test_product_grade_in_registry():
    proc = _load("process.yaml")
    main = [o for o in proc["chemistry"]["outputs"] if o["role"] == "main-product"]
    assert main and main[0]["inventory_key"] == "product:CO2P"
    substance, grade = main[0]["chemical"].split("/")
    registry = yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))
    entries = registry["chemicals"] if isinstance(registry, dict) else registry
    entry = next(c for c in entries if c["slug"] == substance)
    assert grade in {g["slug"] for g in entry.get("grades", [])}


def test_balance_script_cited_and_public():
    flowsheet = (PROCESS / "process" / "flowsheet.yaml").read_text(encoding="utf-8")
    cited = set(re.findall(r"- id: (S\d+)", flowsheet))
    assert len(cited) == 20
    assert flowsheet.count('source: "scripts/dac_balance.py:') == 2 * len(cited)
    proc = _load("process.yaml")
    assert proc["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "cheme-as-code>=1.13" in _text("plant.yaml")
    assert proc["basis"]["operating_hours_per_year"] == 7884
