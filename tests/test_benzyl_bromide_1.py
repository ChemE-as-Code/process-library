"""benzyl-bromide-1 (#139): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) and the materials' data are read as YAML, and what the folder states in
DESIGN.md, process.yaml and lca/ is checked against them:

- the yields on the bromine and on the toluene make-up and the product's assay follow from the
  streams, and the assay carries its caveat (an upper bound) wherever it is stated;
- the absorber makes 48 wt% acid, and the allocation's shares are the mass of the product and of
  the HBr in the acid;
- the recycle S2 is 0.98 of the recovered toluene S17 at its fixed point, and the charge keeps 4
  mol of toluene per mol of bromine;
- every assumed temperature of a mixed stream is the adiabatic mix of its inlets, and the jacket
  is checked against the cooling water's mean temperature;
- every energy flow reaches the LCI: the cooling-water and brine totals per kg are the sums of
  their energy streams, the jacket duty Q2 counts the light and the agitator;
- the recipe's batch size times its batches gives 1000 t/a;
- the criticality classes DESIGN.md states as possible without a TD24 are those core's
  `criticality()` can give, and the MTT is below the content's bubble point at the worst moment;
- water ingress and the loss of the absorber water are open items, and the process is not set
  public in the change that adds it (CONTRIBUTING, "Publishing a process").
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "benzyl-bromide-1"


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    streams = {s["id"]: s for s in _yaml("process/flowsheet.yaml")["streams"]}
    return materials, streams


def _state(model, sid: str) -> dict:
    return model[1][sid]["state"]["design"]


def _kmol(model, sid: str) -> dict[str, float]:
    """kmol/h of each component of a material stream."""
    materials, _ = model
    state = _state(model, sid)
    flow, comp = state["flow"]["value"], state["composition"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * materials[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mm * x for k, x in comp["values"].items()}
    return {k: flow * w / materials[k]["molar_mass"] for k, w in comp["values"].items()}


def _kg(model, sid: str) -> dict[str, float]:
    return {k: n * model[0][k]["molar_mass"] for k, n in _kmol(model, sid).items()}


def _mcp(model, sid: str) -> float:
    return sum(n * model[0][k]["liquid_heat_capacity"] for k, n in _kmol(model, sid).items() if n)


def _temperature(model, sid: str) -> float:
    return _state(model, sid)["temperature"]["value"]


def _duty(model, sid: str) -> float:
    return _state(model, sid)["duty"]["value"]


def test_yields_and_assay_follow_from_the_flowsheet(model):
    product = _kmol(model, "S15")["BNBR"]
    assert product / _kmol(model, "S5")["BR2"] == pytest.approx(0.8846, abs=5e-4)
    assert product / _kmol(model, "S1")["TOL"] == pytest.approx(0.869, abs=5e-4)
    masses = _kg(model, "S15")
    assert masses["BNBR"] / sum(masses.values()) == pytest.approx(0.983, abs=5e-4)
    for rel in ("DESIGN.md", "process.yaml"):
        text = _text(rel)
        assert "88.5 %" in text and "86.9 %" in text and "98.3 wt%" in text, rel
    rate = _state(model, "S15")["flow"]["value"]
    assert _state(model, "S5")["flow"]["value"] / rate == pytest.approx(1.038, abs=5e-4)
    assert _state(model, "S1")["flow"]["value"] / rate == pytest.approx(0.609, abs=5e-4)


def test_the_assay_and_the_yield_carry_their_caveats():
    """The assay is an upper bound (by-products not modelled) everywhere it is stated, and the
    modelled yield on toluene is said to stay below the source's 90 %."""
    manifest = _yaml("process.yaml")
    assert "upper bound" in " ".join(manifest["description"].split())
    note = next(o for o in manifest["chemistry"]["outputs"] if o["inventory_key"] == "product:BNBR")
    assert "upper bound" in note["note"]
    assert "upper bound" in _yaml("process/design-basis.yaml")["products"][0]["purity"]
    assert "upper bound" in _text("README.md")
    design = _text("DESIGN.md")
    assert "The 98.3 wt% is an upper bound" in design
    assert "The modelled yield on toluene is below the source's" in design
    assert 0.869 < 0.90  # SRC-1, Example I: about 90 % on toluene


def test_acid_strength_and_the_allocation_shares(model):
    acid = _kg(model, "S11")
    assert acid["HBR"] / sum(acid.values()) == pytest.approx(0.48, abs=1e-3)
    product = _state(model, "S15")["flow"]["value"]
    allocation = _yaml("lca/lca.yaml")["allocation"]
    share = product / (product + acid["HBR"])
    assert allocation["shares"]["BNBR"] == pytest.approx(share, abs=1e-4)
    assert allocation["shares"]["HBRACID"] == pytest.approx(1 - share, abs=1e-4)
    assert sum(allocation["shares"].values()) == pytest.approx(1.0)


def test_recycle_at_its_fixed_point_and_the_charge_ratio(model):
    s2, s17 = _kmol(model, "S2"), _kmol(model, "S17")
    for k, n in s17.items():
        assert s2.get(k, 0.0) == pytest.approx(0.98 * n, rel=2e-3, abs=1e-6), k
    charge = _kmol(model, "S4")
    assert charge["TOL"] / _kmol(model, "S5")["BR2"] == pytest.approx(4.0, rel=2e-3)


def _mix(model, *parts: tuple[str, float]) -> float:
    return sum(_mcp(model, s) * t for s, t in parts) / sum(_mcp(model, s) for s, _ in parts)


def test_mixed_temperatures_are_the_adiabatic_mixes(model):
    t3 = _mix(model, ("S1", _temperature(model, "S1")), ("S2", _temperature(model, "S2")))
    assert _temperature(model, "S3") == pytest.approx(t3, abs=0.05)
    t17 = _mix(model, ("S12", _temperature(model, "S12")), ("S14", _temperature(model, "S14")))
    assert _temperature(model, "S17") == pytest.approx(t17, abs=0.05)
    for sid in ("S2", "S18"):
        assert _temperature(model, sid) == pytest.approx(t17, abs=0.05), sid
    recipe = _yaml("process/recipe.yaml")
    heat = next(o for o in recipe["unit_procedures"][0]["operations"] if o["id"] == "heat")
    assert heat["temperatures"][0] == pytest.approx(t3, abs=0.05)


def test_jackets_against_the_mean_coolant_and_the_brine_above_bromine_freezing(model):
    products = {p["id"]: p for p in _yaml("process/flowsheet.yaml")["products"]}
    cw = products["CW"]["utility"]
    mean = 0.5 * (cw["supply_temperature"]["value"] + cw["return_temperature"]["value"])
    jacket = _yaml("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    assert jacket["coolant_temperature"] == pytest.approx(mean)
    # the vent gas and the forerun leave the brine coolers above bromine's 265.95 K melting point
    for sid in ("S9", "S14"):
        assert _temperature(model, sid) > 265.95 + 2.0, sid


def test_every_energy_flow_reaches_the_lci(model):
    _, streams = model
    energy = [s for s in streams.values() if s.get("kind") == "energy"]
    rate = _state(model, "S15")["flow"]["value"]
    by_sink = {}
    for s in energy:
        by_sink.setdefault(s["to"].split(".")[0], []).append(s["id"])
        by_sink.setdefault(s["from"].split(".")[0], []).append(s["id"])
    assert set(by_sink["CW"]) == {"Q2", "Q3", "Q4", "Q6", "Q8", "Q11"}
    assert set(by_sink["BRINE"]) == {"Q5", "Q10"}
    assert set(by_sink["LPS"]) == {"Q1", "Q7", "Q9"}
    assert set(by_sink["POWER"]) == {"P1", "P2", "P3"}
    per_kg = {k: sum(_duty(model, q) for q in v) / rate for k, v in by_sink.items() if k in ("CW", "BRINE", "LPS", "POWER")}
    assert per_kg["CW"] == pytest.approx(0.618, abs=5e-4)
    assert per_kg["BRINE"] == pytest.approx(0.039, abs=5e-4)
    assert per_kg["LPS"] == pytest.approx(0.335, abs=5e-4)
    assert per_kg["POWER"] == pytest.approx(0.156, abs=5e-4)
    design, manifest = _text("DESIGN.md"), _text("process.yaml")
    for figure in ("0.618 kWh", "0.039 kWh", "0.335 kWh", "0.156 kWh"):
        assert figure in design and figure in manifest, figure
    inventory = {row.split(",")[0]: row for row in (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8").splitlines()[1:]}
    assert {"product:CW", "product:BRINE", "feed:LPS", "feed:POWER"} <= set(inventory)
    # Q2 counts the light the content absorbs (30 % of the lamps' power) and the 3 kW agitator
    assert "agitator" in streams["Q2"]["state"]["design"]["duty"]["source"]
    assert _duty(model, "Q3") == pytest.approx(0.7 * _duty(model, "P1"), rel=1e-3)
    assert "Recorded exclusions, each with its number" in design


def test_recipe_basis_gives_1000_t_per_year(model):
    recipe = _yaml("process/recipe.yaml")
    rate = _state(model, "S15")["flow"]["value"]
    hours = recipe["hours_per_year"]["value"]
    assert rate * hours / 1000 == pytest.approx(1000, rel=1e-3)
    batches = rate * hours / recipe["batch_size"]["value"]
    assert batches == pytest.approx(1124.1, abs=0.2)  # D-003


def _criticality(mtsr: float, mtt: float, td24: float) -> int:
    """Stoessel's class as core v1.8.0's reaction_hazards.criticality gives it."""
    if td24 < mtsr:
        return 4 if mtt < td24 else 5
    if mtsr < mtt:
        return 1 if mtt < td24 else 2
    return 3


def test_the_stated_criticality_classes_are_those_any_td24_can_give():
    rows = re.findall(
        r"^\| (?:5\.0e-4 \(design\)|k/10|k/100) \| [^|]+ \| ([\d.]+) K \| [^|]+ \| [^|]+ \| [^|]+ \| ([^|]+) \|$",
        (PROCESS / "DESIGN.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    assert len(rows) == 3
    mtt = 383.8
    for mtsr, stated in rows:
        possible = {_criticality(float(mtsr), mtt, 300.0 + 0.5 * i) for i in range(600)}
        assert {int(c) for c in re.findall(r"\d", stated)} == possible, (mtsr, stated)
    assert "and 5 if it lies below (TD24 < 363.9 K" in _text("DESIGN.md")


def _bubble(materials: dict, x: dict[str, float], p: float = 101.325) -> float:
    def total(t: float) -> float:
        out = 0.0
        for k, xi in x.items():
            vp = materials[k]["vapour_pressure"]
            out += xi * 100.0 * 10 ** (vp["a"] - vp["b"] / (t + vp["c"]))
        return out

    lo, hi = 250.0, 600.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if total(mid) < p else (lo, mid)
    return mid


def test_the_mtt_is_below_the_content_bubble_point_in_the_design_case(model):
    materials, _ = model
    hazard = next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == "R101")["hazard"]
    end = {k: v for k, v in _state(model, "S6")["composition"]["values"].items() if v and k != "HBR"}
    # the worst moment: the end of the dosing with 1.73 % of the 5.777 kmol of bromine unreacted
    x_br2 = 0.0173 * 5.777 / 25.088
    worst = {k: v * (1 - x_br2) for k, v in end.items()}
    worst["BR2"] = x_br2
    assert _bubble(materials, worst) == pytest.approx(394.9, abs=0.3)
    assert hazard["mtt"] < _bubble(materials, worst)
    assert "394.9 K at the worst moment" in _text("DESIGN.md")


def test_water_ingress_and_absorber_water_loss_are_open_items():
    design = _text("DESIGN.md")
    assert "Loss of the absorber water while R-101 doses" in design
    assert "Water ingress into R-101" in design
    equipment = _text("equipment/equipment-list.yaml")
    assert "suck-back" in equipment and "A-101's water flow" in equipment
    assert "caustic guard scrubber" in equipment


def test_not_published_in_the_change_that_adds_it():
    publication = _yaml("process.yaml")["publication"]
    assert publication["status"] == "internal"
    assert "license" not in publication
