"""bioethanol-1 (#468): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core from the corn, the natural gas
and the air) are read as YAML, and the statements the folder makes in DESIGN.md, README.md,
process.yaml and the LCA are checked against them:

- the yield is SRC-1's 114 gal per dry short ton (NREL/TP-580-28893), from S22 and S1;
- the beer, the beer column's and the rectifier's overheads, the product, the wet cake, the syrup
  and the DDGS have SRC-1's stated compositions; the backset is 15 % of the mash;
- the corn feed is SRC-1's 633 dry short tons a day; steam, natural gas and power follow from
  SRC-1's costs per gallon and its power shares;
- the zero-discharge balance: no wastewater product, water leaves with the dryer and the vent;
- the specific consumptions in process.yaml and README.md follow from the flowsheet;
- the allocation is mass, with the WBCSD price ratio below 5 at SRC-1's prices;
- biogenic and fossil CO2 are kept apart and mapped with their origin;
- the process is public with CC-BY-4.0, requires cheme-as-code 1.12, and its registry slugs exist.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "bioethanol-1"

GAL_L = 3.785411784  # US gallon in litres (definition)
SHORT_TON_KG = 907.18474  # short ton in kg (definition)
RHO_ETOH_60F = 0.7932  # kg/L at 288.71 K (thermo 0.6.1, DESIGN.md SRC-3)
HOURS = 7920


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


def _flow(streams: dict, sid: str) -> float:
    return streams[sid]["flow"]["value"]


MW = {c["id"]: c["molar_mass"] for c in _load("process/materials.yaml")["components"]}


def _mass(streams: dict, sid: str) -> dict[str, float]:
    """Component mass flows (kg/h) of a stream given on a mass flow basis."""
    st = streams[sid]
    comp = st["composition"]
    assert st["flow"].get("basis", "mass") == "mass", sid
    vals = comp["values"]
    if comp["basis"] == "mole_fraction":
        total = sum(x * MW[k] for k, x in vals.items())
        vals = {k: x * MW[k] / total for k, x in vals.items()}
    else:
        assert comp["basis"] == "mass_fraction", sid
    return {k: v * st["flow"]["value"] for k, v in vals.items()}


def _frac(streams: dict, sid: str, comp: str) -> float:
    return _mass(streams, sid).get(comp, 0.0) / _flow(streams, sid)


SOLIDS = ("STARCH", "NFS", "NFD", "GLC", "GLY")


def _solids(streams: dict, sid: str) -> float:
    m = _mass(streams, sid)
    return sum(m.get(k, 0.0) for k in SOLIDS) / _flow(streams, sid)


def test_the_corn_feed_is_src1s_633_dry_tons_a_day(streams):
    dry = _flow(streams, "S1") * (1 - streams["S1"]["composition"]["values"]["H2O"])
    assert dry * 24 / SHORT_TON_KG == pytest.approx(633, rel=1e-4)
    vals = streams["S1"]["composition"]["values"]
    assert vals["STARCH"] / (1 - vals["H2O"]) == pytest.approx(0.70, abs=1e-6)
    assert vals["NFS"] / (1 - vals["H2O"]) == pytest.approx(0.18, abs=1e-6)
    assert vals["NFD"] / (1 - vals["H2O"]) == pytest.approx(0.12, abs=1e-6)


def test_the_yield_is_src1s_114_gal_per_dry_ton(streams):
    etoh = _mass(streams, "S22")["ETOH"]
    dry_tons_h = _flow(streams, "S1") * 0.85 / SHORT_TON_KG
    gal = etoh / RHO_ETOH_60F / GAL_L
    assert gal / dry_tons_h == pytest.approx(114, rel=0.002)
    assert "113.97 gal" in _text("README.md") and "113.97 gal" in _text("DESIGN.md")
    assert round(_flow(streams, "S22") * HOURS / 1000, -2) == 71800


def test_the_stated_compositions_are_src1s(streams):
    assert _frac(streams, "S11", "ETOH") == pytest.approx(0.09, abs=1e-4)  # beer 9 wt%
    assert _frac(streams, "S16", "ETOH") == pytest.approx(0.45, abs=0.01)  # beer column 45 wt%
    assert _frac(streams, "S17", "ETOH") < 0.001  # whole stillage < 0.1 wt%
    assert _frac(streams, "S19", "ETOH") == pytest.approx(0.91, abs=0.005)  # rectifier 91 wt%
    assert _frac(streams, "S20", "ETOH") < 0.001  # stripper bottoms < 0.1 wt%
    assert _frac(streams, "S22", "ETOH") >= 0.995  # anhydrous, at least 99.5 wt%
    assert _solids(streams, "S23") == pytest.approx(0.35, abs=0.005)  # wet cake 35 wt%
    assert _solids(streams, "S28") == pytest.approx(0.55, abs=0.005)  # syrup 55 wt%
    assert _frac(streams, "S30", "H2O") == pytest.approx(0.09, abs=0.001)  # DDGS 9 wt%
    assert _flow(streams, "S25") / _flow(streams, "S7") == pytest.approx(0.15, abs=1e-4)


def test_the_ddgs_against_src1s_table_2(streams):
    src1 = 243.6 * SHORT_TON_KG / 24
    assert _flow(streams, "S30") / src1 - 1 == pytest.approx(-0.057, abs=0.002)


def test_the_utilities_follow_from_src1(streams):
    gal_h = 25e6 / HOURS
    steam_kg_h = 0.085 / 4.50 * 1000 * gal_h * 0.45359237
    assert steam_kg_h == pytest.approx(27045, rel=1e-3)
    q = {k: streams[k]["duty"]["value"] for k in ("Q1", "Q1B", "Q2")}
    assert sum(q.values()) == pytest.approx(steam_kg_h * 2120.2 / 3600, rel=1e-3)
    ft3_h = 0.038 / 2.95 * 1000 * gal_h
    kmol_h = ft3_h * 0.028316846592 * 101.325 / (8.314462618 * 288.7056)
    assert _flow(streams, "S32") == pytest.approx(kmol_h * 16.043, rel=2e-3)
    assert streams["Q9"]["duty"]["value"] == pytest.approx(
        _flow(streams, "S32") / 16.043 * 802584 / 3600, rel=1e-3
    )
    power = {k: streams[k]["duty"]["value"] for k in ("Q3", "Q4", "Q5", "Q6")}
    assert sum(power.values()) == pytest.approx(2090, abs=0.1)
    assert power["Q3"] == pytest.approx(0.08 * 2090, abs=0.1)
    assert power["Q4"] == pytest.approx(0.07 * 2090, abs=0.1)
    assert power["Q5"] == pytest.approx(0.53 * 2090, abs=0.1)


def test_the_fermentation_heat_follows_from_the_extents(streams):
    glc_in = _mass(streams, "S8")["GLC"] / 180.156
    rx = {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}
    ferm = rx["FERM"]["conversion"]["value"] * glc_in
    glyc = rx["GLYC"]["conversion"]["value"] * glc_in / 2
    q = (ferm * -rx["FERM"]["heat_of_reaction"]["value"] + glyc * -rx["GLYC"]["heat_of_reaction"]["value"]) / 3600
    assert streams["Q7"]["duty"]["value"] == pytest.approx(q, rel=0.005)


def test_zero_liquid_discharge(sheet):
    cats = {p["id"]: p.get("category") for p in sheet["products"]}
    assert "wastewater" not in cats.values()
    assert cats["ETOH"] == "product" and cats["DDGS"] == "by_product"


def test_the_stated_consumptions_per_kg(streams):
    etoh = _flow(streams, "S22")
    manifest = _text("process.yaml")
    for sid, stated in (("S1", "3.105 kg/kg"), ("S32", "0.086 kg/kg"), ("S12", "1.045 kg/kg"), ("S30", "0.958 kg/kg")):
        value = float(stated.split()[0])
        assert _flow(streams, sid) / etoh == pytest.approx(value, abs=0.0006), sid
        assert stated in manifest, stated
    co2b = _mass(streams, "S13")["CO2B"] / etoh
    assert co2b == pytest.approx(0.959, abs=0.0006)
    co2 = _mass(streams, "S35")["CO2"] / etoh
    assert co2 == pytest.approx(0.236, abs=0.0006)


def test_mass_allocation_by_the_wbcsd_rule(streams):
    lca = _load("lca/lca.yaml")
    assert lca["allocation"]["method"] == "mass"
    etoh, ddgs = _flow(streams, "S22"), _flow(streams, "S30")
    ddgs_price = 0.045 / 0.45359237  # $/kg, SRC-1 p. 19
    etoh_price = ddgs_price * ddgs * 0.8 / 0.2 / etoh  # DDG about 20 % of the income
    assert 1 < etoh_price / ddgs_price < 5
    assert etoh / (etoh + ddgs) == pytest.approx(0.511, abs=0.001)


def test_biogenic_and_fossil_co2_apart():
    lca = _load("lca/lca.yaml")
    flows = {f["key"]: f for f in lca["flows"]}
    assert flows["emission:CO2B"]["elementary"]["origin"] == "biogenic"
    assert flows["emission:CO2"]["elementary"]["origin"] == "fossil"
    assert lca["carbon_accounting"]["content"]["feed:CORN"]["biogenic_fraction"] == 1.0


def test_every_heat_stream_reaches_the_lci():
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        rows = {r["key"]: r for r in csv.DictReader(fh)}
    assert set(rows["feed:LPS"]["streams"].split()) == {"Q1", "Q1B", "Q2"}
    assert set(rows["feed:POWER"]["streams"].split()) == {"Q3", "Q4", "Q5", "Q6"}
    assert set(rows["product:CW"]["streams"].split()) == {"Q7", "Q8"}


def test_published_public_with_cc_by_and_registry_slugs():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    registry = {c["slug"] for c in _load_registry()}
    for side in ("inputs", "outputs", "utilities"):
        for flow in manifest["chemistry"][side]:
            assert flow["chemical"].split("/")[0] in registry, flow["chemical"]


def _load_registry() -> list[dict]:
    return yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))["chemicals"]


def test_requires_core_1_12():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"


def test_coverage_names_this_entry():
    cov = yaml.safe_load((KIT / "coverage.yaml").read_text(encoding="utf-8"))
    item = next(i for i in cov["entries"] if i.get("id") == "bioethanol")
    assert any(c["process"] == "bioethanol-1" for c in item.get("covered_by", []))
