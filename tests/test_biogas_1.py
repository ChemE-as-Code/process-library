"""biogas-1 (#462): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by scripts/balance.py)
are read as YAML, and the statements the folder makes in DESIGN.md, README.md, process.yaml and
lca/lca.yaml are checked against them:

- the substrates are FNR model plant VII's tonnages over 8000 h, with their DM and VS;
- the dry biogas reproduces the source's 1 735 468 m3/a and 60.7 % methane (FNR Table 8.7);
- the lumped compositions give each substrate's standard yield and methane content by Buswell;
- the membrane product holds 98.0 mol% CH4 at 99.5 % methane recovery (SGC Rapport 2013:270);
- the boiler's calculated heat equals the script's heat demand;
- the water is removed before compression, and the functional unit's CH4 and LHV per kg;
- the element balance of carbon closes over the plant;
- the stated key numbers (biomethane, electricity, methane slip) follow from the streams;
- the LCI keeps the substrates free, the digestate a recyclable, the emissions biogenic;
- the source register, decisions and core limits are present; public with CC-BY-4.0.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "biogas-1"
V_N = 8.314462618 * 273.15 / 101.325   # m3/kmol at normal conditions
MW = {"H2O": 18.015, "CARB": 162.141, "LIPID": 885.453, "RVS": 162.141, "ASH": 60.083,
      "CH4": 16.043, "CO2": 44.009, "O2": 31.998, "N2": 28.014}
CARBON = {"CARB": 6, "LIPID": 57, "RVS": 6, "CH4": 1, "CO2": 1}


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


def kmol(state: dict) -> dict[str, float]:
    """Component molar flows (kmol/h) of a stream given in mass or mole fractions."""
    comp = state["composition"]
    flow = state["flow"]["value"]
    x = {k: float(v) for k, v in comp["values"].items()}
    if comp["basis"] == "mass_fraction":
        return {k: flow * v / MW[k] for k, v in x.items()}
    mean = sum(v * MW[k] for k, v in x.items())
    return {k: flow / mean * v for k, v in x.items()}


def test_substrates_are_fnr_plant_vii(streams):
    tonnes = {"S1": 4000, "S2": 8000, "S3": 4600, "S4": 5500}
    dm = {"S1": 0.08, "S2": 0.16, "S3": 0.05, "S4": 0.40}
    vs = {"S1": 0.80, "S2": 0.87, "S3": 0.90, "S4": 0.50}
    for sid, t in tonnes.items():
        s = streams[sid]
        assert s["flow"]["value"] == pytest.approx(t * 1000 / 8000)
        x = s["composition"]["values"]
        assert 1 - x["H2O"] == pytest.approx(dm[sid], abs=1e-6)
        organic = x["CARB"] + x["LIPID"] + x["RVS"]
        assert organic / (1 - x["H2O"]) == pytest.approx(vs[sid], abs=1e-5)


def test_each_substrate_gives_its_standard_yield(streams):
    # FNR Table 8.2: Nm3 biogas per t VS and methane content; Buswell on CARB and LIPID
    table = {"S1": (370, 0.55), "S2": (680, 0.60), "S3": (1000, 0.68), "S4": (615, 0.60)}
    for sid, (yield_, ch4) in table.items():
        x = streams[sid]["composition"]["values"]
        vs = x["CARB"] + x["LIPID"] + x["RVS"]
        n_c, n_l = x["CARB"] / MW["CARB"], x["LIPID"] / MW["LIPID"]
        gas = (6 * n_c + 57 * n_l) * V_N / vs * 1000
        methane = (3 * n_c + 40 * n_l) / (6 * n_c + 57 * n_l)
        assert gas == pytest.approx(yield_, rel=2e-4)
        assert methane == pytest.approx(ch4, abs=2e-4)


def test_biogas_reproduces_the_source(streams):
    gas = kmol(streams["S8"])
    dry = (gas["CH4"] + gas["CO2"]) * V_N
    assert dry * 8000 == pytest.approx(1_735_468, rel=5e-4)
    assert gas["CH4"] / (gas["CH4"] + gas["CO2"]) == pytest.approx(0.607, abs=5e-4)
    assert "216.93 Nm3/h" in _text("process.yaml")


def test_membrane_split(streams):
    feed, prod, off = kmol(streams["S17"]), kmol(streams["S19"]), kmol(streams["S20"])
    assert prod["CH4"] / feed["CH4"] == pytest.approx(0.995, abs=1e-6)
    assert prod["CH4"] / (prod["CH4"] + prod["CO2"] + prod.get("H2O", 0)) == pytest.approx(0.98, abs=1e-5)
    assert off["CH4"] * MW["CH4"] / streams["S19"]["flow"]["value"] == pytest.approx(0.00476, abs=2e-5)


def test_boiler_heat_meets_the_demand(streams):
    q1 = streams["Q1"]["duty"]
    assert q1["provenance"] == "calculated"
    # the script's demand: substrate 96.23 kW + losses 30.47 kW + water evaporated 9.10 kW
    assert q1["value"] == pytest.approx(135.79, abs=0.05)
    design = _text("DESIGN.md")
    assert "135.79 kW" in design and "96.23" in design and "30.47 kW" in design and "9.10 kW" in design


def test_water_removed_before_compression(streams):
    # SGC Rapport 2013:270 section 2.3.1: the water is removed by cooling before compression
    sheet = _load("process/flowsheet.yaml")
    links = {s["id"]: (s["from"], s["to"]) for s in sheet["streams"]}
    assert links["S12"][1] == "E300.in" and links["S15"][1] == "C301.in"
    y_in = streams["S15"]["composition"]["values"]["H2O"]
    assert y_in == pytest.approx(1228.2 / 101500, rel=2e-3)   # saturated at 283.15 K, 101.5 kPa(a)
    # its partial pressure at 1600 kPa(a) is below water's vapour pressure at the 353.15 K outlet
    assert y_in * 1600 < 47.4


def test_functional_unit_heating_value(streams):
    s19 = kmol(streams["S19"])
    ch4 = s19["CH4"] * MW["CH4"] / streams["S19"]["flow"]["value"]
    assert ch4 == pytest.approx(0.947, abs=5e-4)
    lhv = ch4 * 50.027   # MJ/kg of methane on the materials' ideal-gas data (balance.py)
    assert lhv == pytest.approx(47.4, abs=0.05)
    assert "0.947 kg CH4 per kg" in _text("lca/lca.yaml") and "47.4 MJ LHV per kg" in _text("lca/lca.yaml")
    assert "47.4 MJ LHV per kg" in _text("process.yaml")
    assert "6.7 g per MJ LHV" in _text("DESIGN.md")


def test_carbon_closes(streams):
    def carbon(ids):
        return sum(n * CARBON.get(k, 0) for i in ids for k, n in kmol(streams[i]).items())
    c_in = carbon(["S1", "S2", "S3", "S4"])
    c_out = carbon(["S10", "S14", "S19", "S20"])
    assert c_out == pytest.approx(c_in, rel=1e-4)


def test_key_numbers(streams):
    prod = streams["S19"]["flow"]["value"]
    assert prod == pytest.approx(87.99, abs=0.01)
    power = sum(streams[w]["duty"]["value"] for w in ("W1", "W2", "W3"))
    assert power / prod == pytest.approx(1.028, abs=0.001)
    assert streams["S10"]["flow"]["value"] / prod == pytest.approx(28.40, abs=0.01)
    text = _text("process.yaml")
    assert "87.99 kg/h" in text and "1.028 kWh/kg" in text and "704 t/a" in text


def test_lca_scope():
    lca = _load("lca/lca.yaml")
    flows = {f["key"]: f for f in lca["flows"]}
    for key in ("feed:SLURRY", "feed:CATER", "feed:GREASE", "feed:BIOW"):
        assert flows[key].get("free") is True
    assert flows["product:DIGESTATE"]["treatment"]["kind"] == "recyclable"
    for key in ("emission:CH4", "emission:CO2"):
        assert flows[key]["elementary"]["origin"] == "biogenic"
    assert lca["system_model"] == "cutoff"
    mappings = _load("lca/mappings.yaml")
    assert mappings["exchanges"]["feed:POWER"]["use"] == "electricity"


def test_design_record():
    design = _text("DESIGN.md")
    for sid in ("SRC-1", "SRC-2", "SRC-3", "SRC-4"):
        assert f"| {sid} |" in design
    for d in range(1, 13):
        assert f"D-{d:03d}" in design
    for limit in range(1, 7):
        assert f"**L-{limit}**" in design
    assert "Rejected" in design and "QSDsan" in design


def test_public_and_core_version():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["families"] == ["biogas"]
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
