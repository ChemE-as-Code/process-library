"""titanium-dioxide-1 (#463): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, the temperatures, air and
duties given by scripts/energy_balance.py) are read as YAML, and the statements the folder makes
in DESIGN.md, README.md, process.yaml, the equipment list and the benchmarks are checked
against them (the numbers named below; prose elsewhere is not parsed):

- the product rate and the specific consumptions per t of TiO2 (feedstock, coke, chlorine,
  oxygen, lime, caustic, CO2, filter cake) are the stated ones and lie inside the BREF LVIC-S
  ranges DESIGN.md D-012 quotes;
- titanium and chlorine close over the plant's boundary, and the chlorine loop returns what the
  oxidiser frees;
- the design specifications hold on the written streams (coke excess, chlorine slip, oxygen
  excess, caustic and lime excess);
- the duties DESIGN.md quotes are the flowsheet's, and the steam, fired heat and cooling water
  per t are the stated ones (DESIGN.md, process.yaml); the electricity lumps are the BREF's GJ/t
  times the rate, and the air fan P3 is counted on top of them;
- the equipment list's lime rate and duties (R-101, E-101, E-102, R-401, K-301) are the
  flowsheet's;
- the LCA links the library producers it names, every energy stream reaches the inventory, and
  the benchmark binds the dataset's KPIs;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "titanium-dioxide-1"

ELEMENTS = {
    "TIO2": {"Ti": 1, "O": 2}, "FEO": {"Fe": 1, "O": 1}, "SIO2": {"Si": 1, "O": 2}, "C": {"C": 1},
    "FECL2": {"Fe": 1, "Cl": 2}, "CAO": {"Ca": 1, "O": 1}, "FEOH2": {"Fe": 1, "O": 2, "H": 2},
    "TICL4": {"Ti": 1, "Cl": 4}, "CL2": {"Cl": 2}, "O2": {"O": 2}, "CO": {"C": 1, "O": 1},
    "CO2": {"C": 1, "O": 2}, "N2": {"N": 2}, "AR": {"Ar": 1}, "H2O": {"H": 2, "O": 1},
    "HCL": {"H": 1, "Cl": 1}, "NAOH": {"Na": 1, "O": 1, "H": 1}, "NACL": {"Na": 1, "Cl": 1},
    "NAOCL": {"Na": 1, "O": 1, "Cl": 1}, "CACL2": {"Ca": 1, "Cl": 2},
}


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
def mw() -> dict[str, float]:
    return {c["id"]: float(c["molar_mass"]) for c in _load("process/materials.yaml")["components"]}


def kmol(streams, mw, sid: str) -> dict[str, float]:
    st = streams[sid]
    flow, comp = st["flow"]["value"], st["composition"]
    if comp["basis"] == "mass_fraction":
        return {c: flow * x / mw[c] for c, x in comp["values"].items() if x}
    mmix = sum(x * mw[c] for c, x in comp["values"].items())
    return {c: flow / mmix * x for c, x in comp["values"].items() if x}


def kg(streams, mw, sid: str) -> dict[str, float]:
    return {c: n * mw[c] for c, n in kmol(streams, mw, sid).items()}


def per_t(streams, sid: str) -> float:
    """kg of a stream per t of TiO2 product."""
    return streams[sid]["flow"]["value"] / (streams["S21"]["flow"]["value"] / 1000.0)


def test_the_product_rate_and_the_specific_consumptions(streams, mw):
    assert streams["S21"]["flow"]["value"] == pytest.approx(12500.0, rel=1e-6)
    assert kg(streams, mw, "S21")["TIO2"] == pytest.approx(12500.0, rel=1e-6)
    tio2_in_ore = kg(streams, mw, "S1")["TIO2"] / 12.5
    stated = {"S1": 1214, "S2": 316, "S3": 128, "S17": 462, "S40": 102, "S30": 31, "S44": 396, "S45": 569}
    for sid, value in stated.items():
        assert per_t(streams, sid) == pytest.approx(value, abs=0.6), sid
    assert tio2_in_ore == pytest.approx(1069, abs=0.6)
    co2 = kg(streams, mw, "S37")["CO2"] / 12.5
    assert co2 == pytest.approx(982, abs=0.6)
    readme = _text("README.md")
    assert "1.214 t feedstock (1.069 t TiO2 in it), 316 kg coke, 128 kg make-up chlorine, 462 kg oxygen, 102 kg quicklime, 31 kg of 50 wt% caustic; 982 kg fossil CO2 to air, 396 kg filter cake" in readme
    # inside the BREF LVIC-S ranges of DESIGN.md D-012 (kg/t)
    ranges = {"tio2": (975, 1145, tio2_in_ore), "chlorine": (114, 300, per_t(streams, "S3")),
              "coke": (285, 429, per_t(streams, "S2")), "oxygen": (395, 573, per_t(streams, "S17")),
              "lime": (91, 220, per_t(streams, "S40")), "naoh": (7, 178, kg(streams, mw, "S30")["NAOH"] / 12.5),
              "co2": (56, 1790, co2), "waste": (99, 660, per_t(streams, "S44"))}
    for name, (lo, hi, value) in ranges.items():
        assert lo <= value <= hi, name
    design = _text("DESIGN.md")
    for row in ("| TiO2 in the feedstock | 1069 kg | mean 1075, 975-1145", "| make-up chlorine | 128 kg |",
                "| coke | 316 kg |", "| oxygen | 462 kg |", "| lime | 102 kg |", "| NaOH (100 %) | 15.6 kg |",
                "| CO2 to air | 982 kg |", "| solid waste (wet cake; 295 kg undissolved solids) | 396 kg |"):
        assert row in design, row


def _boundary(sheet, streams, mw, element: str) -> tuple[float, float]:
    feeds = {f["id"] for f in sheet["feeds"]}
    products = {p["id"] for p in sheet["products"]}
    inn = out = 0.0
    for s in sheet["streams"]:
        if s.get("kind") == "energy":
            continue
        a, b = s["from"].split(".")[0], s["to"].split(".")[0]
        if a not in feeds and b not in products:
            continue
        atoms = sum(n * ELEMENTS[c].get(element, 0) for c, n in kmol(streams, mw, s["id"]).items())
        if a in feeds:
            inn += atoms
        else:
            out += atoms
    return inn, out


@pytest.mark.parametrize("element", ["Ti", "Cl", "C", "Fe", "Ca", "Na"])
def test_the_elements_close_over_the_boundary(sheet, streams, mw, element):
    inn, out = _boundary(sheet, streams, mw, element)
    assert out == pytest.approx(inn, rel=1e-4, abs=1e-6), element


def test_the_chlorine_loop_and_the_design_specifications(streams, mw):
    s5, s6, s19 = kmol(streams, mw, "S5"), kmol(streams, mw, "S6"), kmol(streams, mw, "S19")
    assert s6["CL2"] / s5["CL2"] == pytest.approx(0.002, rel=1e-2)
    assert s6["C"] / kmol(streams, mw, "S2")["C"] == pytest.approx(0.15, rel=1e-3)
    assert s19["O2"] / s19["TIO2"] == pytest.approx(0.15, rel=1e-3)
    assert kmol(streams, mw, "S32")["NAOH"] / kmol(streams, mw, "S30")["NAOH"] == pytest.approx(1 / 3, rel=2e-3)
    assert kmol(streams, mw, "S43")["CAO"] / kmol(streams, mw, "S40")["CAO"] == pytest.approx(0.0909, rel=1e-3)
    # the recycle carries the chlorine the oxidiser frees (2 Cl2 per TiO2) and its O2 excess
    s4 = kmol(streams, mw, "S4")
    assert s4["CL2"] == pytest.approx(s19["CL2"], rel=1e-6)
    assert s4["CL2"] == pytest.approx(2 * s19["TIO2"], rel=1e-3)
    # 95 % of the TiO2 entering the bed chlorinated (reactions.yaml)
    tio2_in = kmol(streams, mw, "S1")["TIO2"] + s5.get("TIO2", 0.0)
    assert s6["TIO2"] / tio2_in == pytest.approx(0.05, rel=1e-3)


def test_the_duties_and_energy_per_t(sheet, streams):
    duty = {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"] if s.get("kind") == "energy"}
    for s in sheet["streams"]:
        if s.get("kind") == "energy" and s["id"].startswith("Q"):
            assert s["state"]["design"]["duty"]["source"].startswith("scripts/energy_balance.py"), s["id"]
    gj_t = lambda kw: kw * 3.6 / 12.5 / 1000.0  # noqa: E731
    assert gj_t(duty["Q5"] + duty["Q7"]) == pytest.approx(1.72, abs=0.005)
    assert gj_t(duty["Q8"] + duty["Q9"]) == pytest.approx(0.77, abs=0.005)
    assert duty["P1"] == pytest.approx(2.3e6 * 12.5 / 3600.0, abs=0.1)
    assert duty["P2"] == pytest.approx(1.7e6 * 12.5 / 3600.0, abs=0.1)
    kwh_kg = (duty["P1"] + duty["P2"] + duty["P3"]) / 12500.0
    assert kwh_kg == pytest.approx(1.12, abs=0.005)
    design = _text("DESIGN.md")
    assert "Q2" not in duty  # the spray quench rejects no heat itself; its heat leaves in E-102
    assert ("condenser 10.76 MW (with the 7.87 MW quench heat, D-006), still condenser 3.11 MW, product "
            "cooler 10.6 MW and neutraliser 0.75 MW on cooling water (25/35 C; 2.02 kWh/kg TiO2 in all)") in design
    assert f"{duty['Q3'] / 1000:.2f}" == "10.76" and f"{duty['Q11'] / 1000:.2f}" == "0.75"
    assert f"{duty['Q6'] / 1000:.2f}" == "3.11" and f"{duty['Q10'] / 1000:.1f}" == "10.6"
    cw = (duty["Q3"] + duty["Q6"] + duty["Q10"] + duty["Q11"]) / 12500.0
    assert f"{cw:.2f}" == "2.02" and "2.02 kWh/kg TiO2 rejected" in _text("process.yaml")
    assert f"{duty['Q1'] / 1000:.2f}" == "0.20" and "0.20 MW lost through the shell" in design
    assert streams["S42"]["temperature"]["value"] == pytest.approx(365.6, abs=0.05)
    assert "taking the slurry S42 to 366 K" in design
    assert streams["S19"]["temperature"]["value"] == pytest.approx(1997, abs=0.5)
    assert 1173.15 <= streams["S19"]["temperature"]["value"] <= 2273.15  # BREF 900-2000 C


def test_the_lca_links_and_inventory():
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:CL2"]["dataset"]["path"] == "processes/chlor-alkali-1/lca/dataset.yaml"
    assert mappings["feed:NAOH"]["dataset"]["product"] == "product:NAOH"
    assert mappings["feed:OXY"]["dataset"] == {"path": "processes/asu-1/lca/dataset.yaml", "product": "product:GOXP"}
    assert mappings["feed:LIME"]["dataset"]["path"].startswith("processes/lime-1/")
    for ref in mappings.values():
        if "dataset" in ref:
            assert (KIT / ref["dataset"]["path"]).is_file()
    rows = {r["key"]: r for r in csv.DictReader((PROCESS / "lca" / "inventory.csv").open(encoding="utf-8"))}
    for key in ("feed:POWER", "feed:HPS", "feed:FUEL", "product:CW", "product:BRINE", "product:AMB"):
        assert key in rows, key
    assert float(rows["emission:CO2"]["quantity"]) == pytest.approx(0.982, abs=5e-4)
    assert set(rows["product:CW"]["streams"].split()) == {"Q3", "Q6", "Q10", "Q11"}
    assert set(rows["feed:POWER"]["streams"].split()) == {"P1", "P2", "P3"}
    assert float(rows["emission:HCL"]["quantity"]) == 0.0


def test_the_equipment_list_matches_the_flowsheet(sheet, streams):
    duty = {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"] if s.get("kind") == "energy"}
    notes = {e["tag"]: " ".join(e.get("notes", "").split()) for e in _load("equipment/equipment-list.yaml")["equipment"]}
    assert f"{streams['S40']['flow']['value'] / 1000:.2f} t/h quicklime" in notes["M-401"]
    assert f"about {duty['Q1'] / 1000:.1f} MW" in notes["R-101"]
    # the quench heat (7.87 MW, printed by scripts/energy_balance.py) is part of Q3
    assert "The 7.87 MW it takes from the gas" in _text("DESIGN.md")
    assert "its 7.9 MW leaves in E-102" in notes["E-101"] and "the 7.9 MW quench heat" in notes["E-102"]
    assert f"{duty['Q3'] / 1000:.1f} MW" in notes["E-102"]
    assert f"{duty['Q11'] / 1000:.2f} MW (Q11)" in notes["R-401"]
    assert f"Power {duty['P3']:.0f} kW counted separately as P3" in notes["K-301"]
    for tag in ("R-301", "V-301"):
        assert tag not in notes  # the scrubber is T-301 (steps R301, V301)


def test_the_benchmark_binds_the_dataset():
    bench = yaml.safe_load((KIT / "benchmarks" / "inorganic-chemicals.yaml").read_text(encoding="utf-8"))
    entry = next(d for d in bench["datasets"] if d["process"] == "titanium-dioxide-1")
    dataset = yaml.safe_load((PROCESS / "lca" / "dataset.yaml").read_text(encoding="utf-8"))
    assert entry["dataset"] == dataset["id"]
    for kpi in ("tio2-specific-coke", "tio2-specific-chlorine", "tio2-specific-oxygen"):
        ref = entry["kpis"][kpi]["reference"]
        assert any(r["id"] == ref for r in bench["kpis"][kpi]["references"])


def test_public_and_core_version():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "cheme-as-code>=1.12" in (PROCESS / "plant.yaml").read_text(encoding="utf-8")
    coverage = yaml.safe_load((KIT / "coverage.yaml").read_text(encoding="utf-8"))
    entry = next(e for e in coverage["entries"] if e["id"] == "titanium-dioxide")
    assert entry["rank"] == 57
    assert entry["covered_by"][0]["process"] == "titanium-dioxide-1"
