"""e-methane-1 (#520): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by scripts/balance.py)
are read as YAML, and the statements the folder makes in DESIGN.md, README.md, process.yaml and
lca/ are checked against them:

- the feeds are STORE&GO D5.9's 200 Nm3/h hydrogen with stoichiometric CO2 (H2/CO2 = 4);
- the honeycomb reactor converts 92 % of the CO2 (D5.9 Table 4-1);
- the SNG holds about 99 mol% methane and less than 2 mol% each of H2 and CO2 (D5.9);
- the methanation efficiency (HHV) is within a point of the source's 77.5 % and 78.0 %;
- the electricity reproduces the measured 41 kW plus 0.1 kWh/Nm3 for injection;
- carbon, hydrogen and oxygen balance over the plant;
- the thermal oil's balance and the stated key numbers follow from the streams;
- the LCI keeps the hydrogen a gap and links the CO2 to carbon-capture-1;
- the source register, decisions and core limits are present; public with CC-BY-4.0.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "e-methane-1"
V_N = 8.314462618 * 273.15 / 101.325   # m3/kmol at normal conditions
ATOMS = {"H2": {"H": 2}, "CO2": {"C": 1, "O": 2}, "CH4": {"C": 1, "H": 4}, "CO": {"C": 1, "O": 1},
         "H2O": {"H": 2, "O": 1}}


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def materials() -> dict:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


def kmol(state: dict, materials: dict) -> dict[str, float]:
    """Component molar flows (kmol/h) of a stream given in mole fractions and kg/h."""
    comp = state["composition"]
    assert comp["basis"] == "mole_fraction"
    x = {k: float(v) for k, v in comp["values"].items()}
    mean = sum(v * materials[k]["molar_mass"] for k, v in x.items())
    return {k: state["flow"]["value"] / mean * v for k, v in x.items()}


def test_feeds_are_the_falkenhagen_point(streams, materials):
    h2 = kmol(streams["S1"], materials)
    co2 = kmol(streams["S3"], materials)
    assert h2["H2"] == pytest.approx(9.0045, rel=1e-4)          # 200 Nm3/h, D5.9 section 4.1
    # D5.9 gives 9.0045 kmol/h for its 200 m3/h (STP); as ideal gas that is 201.8 Nm3/h (D-002)
    assert h2["H2"] * V_N == pytest.approx(201.8, abs=0.1)
    assert h2["H2"] / co2["CO2"] == pytest.approx(4.0, rel=1e-4)  # D5.9 appendix 8.4
    assert co2["H2O"] / sum(co2.values()) == pytest.approx(0.0005, rel=1e-3)  # carbon-capture-1


def test_honeycomb_converts_92_percent(streams, materials):
    inlet, outlet = kmol(streams["S6"], materials), kmol(streams["S7"], materials)
    assert 1 - outlet["CO2"] / inlet["CO2"] == pytest.approx(0.92, abs=1e-5)


def test_sng_quality(streams, materials):
    y = streams["S18"]["composition"]["values"]
    assert y["CH4"] == pytest.approx(0.9906, abs=5e-4)       # D5.9: 99 vol-%
    assert y["H2"] < 0.02 and y["CO2"] < 0.02                 # D5.9 section 3.1 grid limits
    assert y["H2O"] == 0.0
    sng = kmol(streams["S18"], materials)
    assert sum(sng.values()) * V_N == pytest.approx(50.84, abs=0.02)
    assert streams["S18"]["flow"]["value"] == pytest.approx(36.27, abs=0.01)
    h2_in = kmol(streams["S1"], materials)["H2"]
    assert 1 - sng["H2"] / h2_in == pytest.approx(0.9981, abs=1e-4)


def test_methanation_efficiency_matches_source(streams, materials):
    # HHV from the formation enthalpies with liquid water (-285.830 kJ/mol, CODATA 1989)
    dhf = {k: materials[k]["ideal_gas"]["dHf_298"] for k in ("CH4", "CO2")}
    hhv_ch4 = -(dhf["CO2"] + 2 * -285830.0 - dhf["CH4"])
    hhv_h2 = 285830.0
    e_sng = kmol(streams["S18"], materials)["CH4"] * hhv_ch4 / 3600
    e_h2 = kmol(streams["S1"], materials)["H2"] * hhv_h2 / 3600
    assert e_h2 == pytest.approx(715.0, abs=1.0)              # D5.9 Table 4-1: 708 measured, 715 ASPEN
    assert 549.0 - 5 < e_sng < 557.0 + 5                      # D5.9 Table 4-1
    assert 0.765 < e_sng / e_h2 < 0.790                       # 77.5 % measured, 78.0 % ASPEN


def test_electricity_reproduces_source(sheet, streams, materials):
    duty = {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"]
            if s.get("kind") == "energy" and "state" in s and "duty" in s["state"]["design"]}
    assert duty["W1"] + duty["W2"] + duty["W3"] == pytest.approx(41.0, abs=0.01)   # Table 4-1
    nm3 = sum(kmol(streams["S18"], materials).values()) * V_N
    assert duty["W4"] / nm3 == pytest.approx(0.1, abs=0.001)                        # Table 4-2
    total = duty["W1"] + duty["W2"] + duty["W3"] + duty["W4"]
    assert total / streams["S18"]["flow"]["value"] == pytest.approx(1.270, abs=0.002)


def test_element_balance_closes(streams, materials):
    inflow = [kmol(streams[s], materials) for s in ("S1", "S3")]
    outflow = [kmol(streams[s], materials) for s in ("S18", "S15")]

    def atoms(flows, el):
        return sum(n * ATOMS[c].get(el, 0) for f in flows for c, n in f.items())

    for el in ("C", "H", "O"):
        assert atoms(outflow, el) == pytest.approx(atoms(inflow, el), rel=1e-4)


def test_oil_balance_and_reactor_duties(sheet):
    duty = {s["id"]: s["state"]["design"]["duty"] for s in sheet["streams"]
            if s.get("kind") == "energy" and "state" in s}
    assert duty["Q3"]["provenance"] == "calculated" and duty["Q5"]["provenance"] == "calculated"
    q8 = duty["Q3"]["value"] + duty["Q5"]["value"] - duty["Q1"]["value"]
    assert duty["Q8"]["value"] == pytest.approx(q8, abs=0.02)
    assert duty["Q3"]["value"] == pytest.approx(93.03, abs=0.01)


def test_stated_numbers(streams):
    readme, design, manifest = _text("README.md"), _text("DESIGN.md"), _text("process.yaml")
    for text in (readme, manifest):
        assert "99.06 mol% CH4" in text and "77.7 %" in text
    assert "36.27 kg/h" in readme and "0.23 kg CO2-eq" in readme
    assert "ln(Q/K) = 0.041" in design and "ln(Q/K) = -4.61" in design


def test_lci_links(sheet):
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:H2"]["atlas"] is False
    assert mappings["feed:CO2"]["dataset"]["path"].startswith("processes/carbon-capture-1/")
    lca = _load("lca/lca.yaml")
    keys = {f["key"]: f for f in lca["flows"]}
    assert "missing" in keys["feed:H2"]
    assert lca["functional_unit"]["product"] == "SNG"
    dataset = _load("lca/dataset.yaml")
    assert dataset["id"].startswith("e-methane")


def test_register_decisions_limits_publication():
    design = (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    for i in range(1, 6):
        assert f"| SRC-{i} |" in design
    for i in range(1, 12):
        assert f"## D-{i:03d} " in design
    for i in range(1, 8):
        assert f"**L-{i}**" in design
    assert "Rejected:" in design.split("## D-002")[0]
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["families"] == ["synthetic-fuels"]
