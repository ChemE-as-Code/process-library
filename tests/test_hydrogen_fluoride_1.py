"""hydrogen-fluoride-1 (#513): the folder's stated numbers against its own files.

Fast, without core: the flowsheet's streams (propagated by core) are read as YAML. The numbers
the folder states in DESIGN.md, process.yaml and the design basis are written here as constants
(the files themselves are not parsed, except the LCA files' allocation and mappings, the
publication block and a few anchors) and checked against those streams:

- the spar feed and the kiln temperatures are US 6 699 455 B2 Example 4's;
- the kiln solids keep the patent's CaF2 and free-acid residues;
- the fluorine balance closes over product, anhydrite and fluorosilicic acid;
- the spar, H2SO4 equivalent, anhydrite, electricity and steam per t of HF against the BREF;
- the product purity and the fluorosilicic acid strength;
- the kiln's hand energy balance, the natural gas burnt against the patent's gas and the BREF's
  fuel, and the furnace losses;
- the anhydrite cooler, and the SO2 slip inside the BREF's alkaline-scrubbing range;
- the high-boiler column's reboiler is the BREF's 0.6 GJ/t;
- the LCA allocation and the mappings to library producers;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.13.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "hydrogen-fluoride-1"
M = {"F": 18.998, "Ca": 40.078, "H": 1.008, "Si": 28.085, "S": 32.06, "O": 15.999}


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


def _flow(streams, sid: str) -> float:
    s = streams[sid]
    return s["flow"]["value"] if "flow" in s else s["duty"]["value"]


def _kg(streams, mw, sid: str) -> dict[str, float]:
    """kg/h by component of a material stream."""
    s = streams[sid]
    total = s["flow"]["value"]
    comp = s["composition"]
    if comp["basis"] == "mass_fraction":
        return {n: total * x for n, x in comp["values"].items()}
    mass = {n: x * mw[n] for n, x in comp["values"].items()}
    m = sum(mass.values())
    return {n: total * v / m for n, v in mass.items()}


def test_feed_and_temperatures_are_the_patents_example_4(streams):
    assert _flow(streams, "S1") == 4800  # 80 kg/min
    assert streams["S2"]["temperature"]["value"] == pytest.approx(673.15)
    assert streams["S4"]["temperature"]["value"] == pytest.approx(393.15)
    assert streams["S10"]["temperature"]["value"] == pytest.approx(478.15)
    assert streams["S7"]["temperature"]["value"] == pytest.approx(477.15)


def test_kiln_solids_keep_the_patents_residues(streams, mw):
    solids = _kg(streams, mw, "S7")
    total = sum(solids.values())
    assert 0.005 <= solids["CaF2"] / total <= 0.011  # US 6 699 455 B2: 0.5-1.1 %
    assert solids["H2SO4"] / total == pytest.approx(0.010, abs=2e-5)  # spec acid, 0.5-1.7 %
    assert solids["CaF2"] / total == pytest.approx(0.008, abs=5e-4)  # D-006


def test_fluorine_balance_closes(streams, mw):
    def fluorine(sid):
        kg = _kg(streams, mw, sid)
        f = {"CaF2": 2, "HF": 1, "SiF4": 4, "H2SiF6": 6}
        return sum(kg.get(n, 0.0) / mw[n] * k * M["F"] for n, k in f.items())

    fed = fluorine("S1")
    out = sum(fluorine(s) for s in ("S17", "S9", "S25", "S29", "S30"))
    assert out == pytest.approx(fed, rel=1e-4)
    assert fluorine("S17") / fed > 0.96  # 96 % of the spar's fluorine in the product


def test_specific_consumptions_against_the_bref(streams, mw):
    hf = _flow(streams, "S17")
    spar_caf2 = _kg(streams, mw, "S1")["CaF2"] / hf
    acid = _kg(streams, mw, "S20")["H2SO4"] + _flow(streams, "S31") * mw["H2SO4"] / mw["SO3"]
    assert spar_caf2 == pytest.approx(2.031, abs=0.002)  # BREF 2.1-2.2: below, D-006 (benchmark reason)
    assert 2.6 <= acid / hf <= 2.7  # BREF Table 6.4, 100 % H2SO4 equivalent
    assert _flow(streams, "S9") / hf == pytest.approx(3.63, abs=0.01)  # BREF about 3.7
    assert _flow(streams, "P1") / hf == pytest.approx(0.225, rel=1e-3)  # kWh/kg, BREF 0.15-0.30
    steam_kg = (_flow(streams, "Q5") + _flow(streams, "Q7")) * 3600 / 2120.4 / hf
    assert 0.15 <= steam_kg <= 0.8  # BREF 150-800 kg/t


def test_product_purity_and_fluorosilicic_acid(streams, mw):
    ahf = _kg(streams, mw, "S17")
    assert ahf["HF"] / sum(ahf.values()) > 0.9999
    fsa = _kg(streams, mw, "S25")
    assert fsa["H2SiF6"] / sum(fsa.values()) == pytest.approx(0.25, abs=0.003)  # BREF 25-35 %


def test_kiln_energy_balance_and_fuel(streams, mw):
    caf2 = _kg(streams, mw, "S1")["CaF2"] / mw["CaF2"]
    extent = 0.9613 * caf2
    assert extent * 59000 / 3600 == pytest.approx(944.4, abs=0.1)
    q1, q2 = _flow(streams, "Q1"), _flow(streams, "Q2")
    assert q1 == pytest.approx(4800 * 0.956 * 375 / 3600, abs=0.5)
    assert q2 == pytest.approx(944.4 + 336.9 + 354.7 - 478.1 - 258.5, abs=0.2)
    hf = _flow(streams, "S17")
    assert (q1 + q2) * 3.6 / hf == pytest.approx(2.15, abs=0.01)  # GJ/t absorbed
    lhv = 393.474 + 2 * 241.822 - 74.534  # kJ/mol, SRC-4 formation enthalpies
    kiln_fired = 189 * lhv / 22.414 / 3.6  # kW, SRC-2 Example 4: at most 189 m3/h
    eta = q2 / kiln_fired
    assert eta == pytest.approx(0.478, abs=0.001)  # D-009
    fired = _kg(streams, mw, "S33")["CH4"] / mw["CH4"] * lhv / 3.6  # kW of natural gas burnt
    assert fired == pytest.approx(kiln_fired + q1 / eta, rel=1e-3)
    assert 4 <= fired * 3.6 / hf <= 5  # GJ/t, BREF BAT fuel for new AHF plants (Table 6.14)
    assert _flow(streams, "Q10") == pytest.approx(fired - q1 - q2, abs=0.5)  # flue and shell losses
    co2 = _kg(streams, mw, "S35")["CO2"]
    assert co2 == pytest.approx(_flow(streams, "S33") * mw["CO2"] / mw["CH4"], rel=1e-3)
    o2 = _kg(streams, mw, "S35")["O2"] / mw["O2"]
    assert o2 == pytest.approx(0.1 * 2 * _flow(streams, "S33") / mw["CH4"], rel=1e-3)  # 10 % excess


def test_anhydrite_cooler_and_so2_slip(streams, mw):
    hf = _flow(streams, "S17")
    acid = _kg(streams, mw, "S7")["H2SO4"] / mw["H2SO4"]  # kmol/h neutralised by NEU
    neu = acid * (1434.5 + 285.825 - 634.9 - 814.0) / 3.6  # kW, SRC-4 formation enthalpies
    cool = 336.9 * (477.15 - 333.15) / (477.15 - 298.15)  # the Q2 solids term scaled, D-009
    assert _flow(streams, "Q9") == pytest.approx(cool + neu, abs=0.3)
    assert streams["S9"]["temperature"]["value"] == pytest.approx(333.15)
    so2 = _kg(streams, mw, "S30")["SO2"] / hf  # kg/kg = t/t
    assert 0.001e-3 <= so2 <= 0.01e-3  # BREF Table 6.6 and BAT-AEL Table 6.15: 0.001-0.01 kg/t


def test_high_boiler_reboiler_is_the_brefs(streams):
    assert _flow(streams, "Q7") == pytest.approx(0.6e3 * _flow(streams, "S17") / 3600, abs=0.1)
    assert _flow(streams, "Q8") == _flow(streams, "Q7")


def test_lca_allocation_and_links():
    lca = _load("lca/lca.yaml")
    assert lca["allocation"]["method"] == "none"
    assert lca["functional_unit"]["product"] == "AHF"
    maps = _load("lca/mappings.yaml")["exchanges"]
    assert maps["feed:ACID"]["dataset"]["path"] == "processes/sulfuric-acid-1/lca/dataset.yaml"
    assert maps["feed:LIME"]["dataset"]["path"].startswith("processes/lime-1/")
    assert maps["feed:NAOH"]["dataset"]["path"] == "processes/chlor-alkali-1/lca/dataset.yaml"
    for m in maps.values():
        if "dataset" in m:
            assert (KIT / m["dataset"]["path"]).is_file()
    assert "feed:SPAR" not in maps  # a gap, never a guess


def test_public_and_core_version():
    meta = _load("process.yaml")
    assert meta["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "cheme-as-code>=1.13" in _text("plant.yaml")
    design = _text("DESIGN.md")
    for anchor in ("SRC-1", "SRC-2", "D-001", "D-012", "L-1", "L-4", "Recorded and rejected"):
        assert anchor in design
