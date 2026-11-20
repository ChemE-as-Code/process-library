"""methylchlorosilanes-1 (#522): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md, process.yaml and lca/lca.yaml are checked against them:

- the reaction conversions follow from the stated crude distribution and silicon conversion,
  and the reactions balance their elements;
- the reactor converts 95 % of the silicon and half of the methyl chloride per pass, and the
  crude's T/D ratio and residue lie in US 4 500 724 A's continuous fluid-bed range;
- the product meets SRC-2's specification, the MeSiCl3 cut is about 90 wt%;
- the specific consumptions and the energy totals per kg are the stated ones, the copper make-up
  keeps about 2 % copper in the bed;
- C-302's reflux drum keeps the cooling water's approach, and its vent leaves the refrigerated
  vent condenser with the stated methyl chloride;
- the allocation shares are the mass shares of the three silane products, the steam at 0;
- every energy stream reaches the LCI; the methyl chloride is linked to chloromethane-1;
- the registry has the slugs process.yaml names; the process is public with CC-BY-4.0 and
  requires cheme-as-code 1.13.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "methylchlorosilanes-1"
CRUDE_WT = {"DMDCS": 84.0, "MTCS": 7.0, "TMCS": 3.0, "MDCS": 1.5, "DISIL": 4.5}


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
def materials() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def reactions() -> dict[str, dict]:
    return {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}


def _kg(streams: dict, materials: dict, sid: str) -> dict[str, float]:
    state = streams[sid]
    flow = float(state["flow"]["value"])
    comp = state["composition"]
    x = {k: float(v) for k, v in comp["values"].items()}
    if comp["basis"] == "mole_fraction":
        mass = {k: v * materials[k]["molar_mass"] for k, v in x.items()}
        total = sum(mass.values())
        x = {k: v / total for k, v in mass.items()}
    return {k: flow * v for k, v in x.items()}


def _kmol(streams, materials, sid) -> dict[str, float]:
    return {k: v / materials[k]["molar_mass"] for k, v in _kg(streams, materials, sid).items()}


def _duty(streams, sid: str) -> float:
    return float(streams[sid]["duty"]["value"])


def _product(streams, materials) -> float:
    return sum(_kg(streams, materials, "S18").values())


def test_conversions_follow_the_crude_distribution(reactions, materials):
    n = {k: v / materials[k]["molar_mass"] for k, v in CRUDE_WT.items()}
    si = {"DMF": n["DMDCS"], "MTF": n["MTCS"] - n["TMCS"], "TMF": 2 * n["TMCS"],
          "MDF": n["MDCS"], "DSF": 2 * n["DISIL"]}
    total = sum(si.values())
    for rid, v in si.items():
        assert reactions[rid]["conversion"]["key"] == "SI"
        assert reactions[rid]["conversion"]["value"] == pytest.approx(0.95 * v / total, abs=1e-5), rid
    assert sum(r["conversion"]["value"] for r in reactions.values()) == pytest.approx(0.95, abs=1e-4)


def test_reactions_balance_elements(reactions, materials):
    def atoms(formula: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
            out[el] = out.get(el, 0) + int(n or 1)
        return out

    for r in reactions.values():
        total: dict[str, float] = {}
        for k, v in r["stoichiometry"].items():
            for el, n in atoms(materials[k]["formula"]).items():
                total[el] = total.get(el, 0.0) + v * n
        assert all(abs(v) < 1e-9 for v in total.values()), r["id"]


def test_molar_masses_from_the_formula(materials):
    w = {"C": 12.011, "H": 1.008, "Cl": 35.45, "Si": 28.085, "Cu": 63.546}
    for c in materials.values():
        m = sum(w[el] * int(n or 1) for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", c["formula"]))
        assert c["molar_mass"] == pytest.approx(m, abs=0.002), c["id"]


def test_reactor_conversions_and_selectivity(streams, materials):
    s4, s5, s7 = (_kmol(streams, materials, k) for k in ("S4", "S5", "S7"))
    assert 1 - s7["SI"] / s5["SI"] == pytest.approx(0.95, abs=1e-4)
    assert 1 - s7["MECL"] / s4["MECL"] == pytest.approx(0.50, abs=2e-3)
    crude = _kg(streams, materials, "S7")
    silanes = sum(crude[k] for k in CRUDE_WT)
    for k, v in CRUDE_WT.items():
        assert 100 * crude[k] / silanes == pytest.approx(v, abs=0.01), k
    # SRC-1 Example 3 (continuous fluid bed): T/D 0.07 to 0.10, residue 4 to 5 %
    assert 0.07 <= crude["MTCS"] / crude["DMDCS"] <= 0.10
    assert 4.0 <= 100 * crude["DISIL"] / silanes <= 5.0
    assert float(streams["S7"]["temperature"]["value"]) == pytest.approx(573.15)


def test_mecl_ratio_of_the_spec(sheet, streams, materials, reactions):
    spec = next(s for s in sheet["specs"] if s["id"] == "mecl")
    ratio = _kg(streams, materials, "S4")["MECL"] / _kg(streams, materials, "S5")["SI"]
    assert ratio == pytest.approx(spec["target"]["value"], rel=1e-4)
    # methyl chloride consumed per mol of silicon fed, from the reactions' conversions (D-003)
    mecl_per_si = sum(r["conversion"]["value"] * r["stoichiometry"]["MECL"] / r["stoichiometry"]["SI"]
                      for r in reactions.values())
    m = {k: materials[k]["molar_mass"] for k in ("MECL", "SI")}
    assert spec["target"]["value"] == pytest.approx(mecl_per_si / 0.5 * m["MECL"] / m["SI"], abs=1e-3)


def test_product_and_cuts_meet_the_stated_purities(streams, materials):
    p = _kg(streams, materials, "S18")
    assert p["DMDCS"] / sum(p.values()) >= 0.995  # SRC-2: 99.5 %
    assert p.get("MTCS", 0.0) / sum(p.values()) <= 0.005
    cut = _kg(streams, materials, "S17")
    assert cut["MTCS"] / sum(cut.values()) == pytest.approx(0.89, abs=0.02)  # SRC-2: about 90 %
    assert _product(streams, materials) * 8000 / 1000 == pytest.approx(60000, rel=1e-5)


def test_consumptions_as_stated(streams, materials):
    prod = _product(streams, materials)
    si = sum(_kg(streams, materials, "S5").values()) / prod
    mecl = sum(_kg(streams, materials, "S1").values()) / prod
    cu = sum(_kg(streams, materials, "S6").values()) / prod
    assert si == pytest.approx(0.276, abs=0.0005)
    assert mecl == pytest.approx(0.963, abs=0.0005)
    assert cu * 1000 == pytest.approx(0.276, abs=0.001)
    # D-004: the make-up keeps SRC-1's Example 3 copper, about 2 % of the bed's silicon
    spent = _kg(streams, materials, "S8")
    assert spent["CU"] / spent["SI"] == pytest.approx(0.02, abs=1e-4)
    assert si > 28.085 / 129.055  # above the stoichiometric 0.218
    for rel in ("process.yaml", "README.md"):
        text = _text(rel)
        assert "0.276 kg of silicon" in text and "0.963 kg of methyl chloride" in text, rel


def test_energy_totals_as_stated(streams, materials):
    prod = _product(streams, materials)
    mps_in = sum(_duty(streams, k) for k in ("Q1", "Q4", "Q6")) / prod
    lps = sum(_duty(streams, k) for k in ("Q8", "Q10")) / prod
    cw = sum(_duty(streams, k) for k in ("Q3", "Q5", "Q7", "Q9", "Q11")) / prod
    power = sum(_duty(streams, k) for k in ("P1", "P2", "P3")) / prod
    assert mps_in == pytest.approx(0.529, abs=0.001)
    assert lps == pytest.approx(0.492, abs=0.001)
    assert cw == pytest.approx(1.072, abs=0.001)
    assert power == pytest.approx(0.028, abs=0.001)
    assert _duty(streams, "Q12") / prod == pytest.approx(0.033, abs=0.001)
    assert _duty(streams, "Q2") / prod == pytest.approx(0.618, abs=0.001)
    share = _duty(streams, "Q10") / (_duty(streams, "Q10") + _duty(streams, "Q8") + mps_in * prod)
    assert share == pytest.approx(0.40, abs=0.005)
    assert "40 %" in _text("README.md") and "40 %" in _text("DESIGN.md")


def test_c302_vent_and_cooling_water_approach(sheet, streams, materials):
    # D-007: 800 kPa(a), above SRC-2's about 90 psig (722 kPa(a)), so that the reflux drum keeps
    # the cooling water's minimum approach and can vent the hydrocarbons
    assert float(streams["S11"]["pressure"]["value"]) == pytest.approx(800.0)
    assert float(streams["S11"]["pressure"]["value"]) > 90 * 6.894757 + 101.325
    cw = next(p for p in sheet["products"] if p["id"] == "CW")["utility"]
    t_drum = float(streams["S2"]["temperature"]["value"])
    assert t_drum - cw["return_temperature"]["value"] >= cw["min_approach"]["value"] - 1e-9
    # the vent leaves E-304 with methyl chloride at its vapour pressure at 253.15 K, 15.0 mol%
    assert float(streams["S11"]["temperature"]["value"]) == pytest.approx(253.15)
    vent = _kmol(streams, materials, "S11")
    assert vent["MECL"] / sum(vent.values()) == pytest.approx(0.150, abs=0.001)
    assert "15.0 mol%" in _text("DESIGN.md")
    brine = next(p for p in sheet["products"] if p["id"] == "BRINE")["utility"]
    assert 253.15 - brine["supply_temperature"]["value"] >= brine["min_approach"]["value"]


def test_allocation_is_by_mass(streams, materials):
    lca = _load("lca/lca.yaml")
    alloc = lca["allocation"]
    mass = {k: sum(_kg(streams, materials, s).values()) for k, s in
            (("DMDCSP", "S18"), ("MTCSP", "S17"), ("LIGHTSP", "S15"))}
    total = sum(mass.values())
    for k, v in mass.items():
        assert alloc["shares"][k] == pytest.approx(v / total, abs=2e-5), k
    assert alloc["shares"]["MPS"] == 0.0
    assert sum(alloc["shares"].values()) == pytest.approx(1.0, abs=1e-6)


def test_every_energy_stream_reaches_the_lci(sheet):
    keys = {f["key"] for f in _load("lca/lca.yaml")["flows"]}
    for node in sheet["feeds"] + sheet["products"]:
        if node.get("category") == "utility":
            kind = "feed" if node in sheet["feeds"] else "product"
            if node["id"] == "MPS":
                continue  # a co-product of the allocation
            assert f"{kind}:{node['id']}" in keys, node["id"]
    maps = _load("lca/mappings.yaml")["exchanges"]
    assert maps["feed:MECLF"]["dataset"]["path"] == "processes/chloromethane-1/lca/dataset.yaml"
    assert (KIT / maps["feed:MECLF"]["dataset"]["path"]).exists()


def test_registry_and_publication():
    manifest = _load("process.yaml")
    reg = yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))
    slugs = {c["slug"] for c in reg["chemicals"]}
    for group in manifest["chemistry"].values():
        for item in group:
            assert item["chemical"].split("/")[0] in slugs, item["chemical"]
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "cheme-as-code>=1.13" in (PROCESS / "plant.yaml").read_text(encoding="utf-8")
