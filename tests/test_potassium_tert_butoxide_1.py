"""potassium-tert-butoxide-1 (#418): the folder's hand-written numbers against its own model.

Fast, without core: the flowsheet's calculated streams (written by cheme process propagate), the
materials' molar masses and heat capacities, the recipe and the LCI's inventory are enough to
check what the folder states by hand (DESIGN.md D-004 to D-012):

- the charge holds 8.6 mol of tert-butanol per mol of potassium, and the make-up is the
  azeotrope (11.76 wt% water, US 5 053 560 A);
- the sieve unit's values in the flowsheet are scripts/makeup_drying.py's (ADR 0027), and its
  energy closes;
- the hand duties (Q7, Q8, Q9, Q13) follow from the streams they name, Q1 is the recipe's
  heat-up, Q6 the dryer model's; the dryer's nitrogen bleed sets SP201's split;
- every assumed temperature of a mixed stream is the adiabatic mix of its inlets, and R-101's
  jacket is checked against the cooling water's log-mean;
- the heating media stay below the temperature limits the design states;
- every energy flow reaches the LCI: each utility's total per kg is the sum of its energy streams
  and is what DESIGN.md and process.yaml state;
- the yield and the assay stated hold and carry their caveats;
- the vent capacity's basis and the rate sensitivity are recorded, and the criticality classes
  DESIGN.md states as possible without a TD24 are those core's `criticality()` gives; with core,
  the screening and the largest cooling-failure release over the batch;
- the recipe's batch size times its batches gives 1000 t/a and the flowsheet's rate;
- di-tert-butyl-dicarbonate-1 links this product kg for kg; the process is public with CC-BY-4.0.
"""

from __future__ import annotations

import csv
import importlib.util
import math
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "potassium-tert-butoxide-1"


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


def _flow(model, sid: str) -> float:
    return _state(model, sid)["flow"]["value"]


def _temperature(model, sid: str) -> float:
    return _state(model, sid)["temperature"]["value"]


def _duty(model, qid: str) -> float:
    return _state(model, qid)["duty"]["value"]


def _kmol(model, sid: str) -> dict[str, float]:
    materials = model[0]
    state = _state(model, sid)
    flow, comp = state["flow"]["value"], state["composition"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * materials[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mm * x for k, x in comp["values"].items()}
    return {k: flow * w / materials[k]["molar_mass"] for k, w in comp["values"].items()}


def _mcp(model, sid: str) -> float:
    """kJ/(K h) from the components' liquid heat capacities."""
    return sum(n * model[0][k].get("liquid_heat_capacity", 0.0) for k, n in _kmol(model, sid).items() if n)


def _mix(model, *sids: str) -> float:
    return sum(_mcp(model, s) * _temperature(model, s) for s in sids) / sum(_mcp(model, s) for s in sids)


def _psat_tba(model, t: float) -> float:
    vp = model[0]["TBA"]["vapour_pressure"]
    return 100.0 * 10 ** (vp["a"] - vp["b"] / (t + vp["c"]))  # kPa


def _recipe() -> dict:
    return _yaml("process/recipe.yaml")


def _cycle_h(model) -> float:
    recipe = _recipe()
    batches = _flow(model, "S15") * recipe["hours_per_year"]["value"] / recipe["batch_size"]["value"]
    return recipe["hours_per_year"]["value"] / batches


def test_charge_ratio_and_azeotropic_make_up(model):
    """D-004: 8.6 mol of tert-butanol per mol of potassium in the charge (Organic Syntheses, Coll.
    Vol. 4, 132); the make-up's water is the azeotrope's 11.76 wt%."""
    ratio = _kmol(model, "S9")["TBA"] / _kmol(model, "S2")["K"]
    assert ratio == pytest.approx(8.6, abs=0.01)
    assert _flow(model, "S4") / (_flow(model, "S3") + _flow(model, "S4")) == pytest.approx(0.1176, abs=1e-4)
    assert "8.60 kmol of tert-butanol per kmol" in _text("DESIGN.md")
    # the alkoxide's share of the solution, within US 4 577 045 A's 10-18 wt%
    s10 = _kmol(model, "S10")
    share = s10["KOTBU"] * model[0]["KOTBU"]["molar_mass"] / _flow(model, "S10")
    assert share == pytest.approx(0.166, abs=0.001) and 0.10 < share < 0.18
    assert "16.6 wt%" in _text("DESIGN.md") and "16.6 wt%" in _text("process.yaml")


def _script():
    spec = importlib.util.spec_from_file_location("makeup_drying", PROCESS / "scripts" / "makeup_drying.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sieve_values_are_the_scripts(model):
    """ADR 0027: S6, S7, Q10-Q12 and P4 cite scripts/makeup_drying.py and are its values; the
    unit's energy closes (steam and the regeneration heater in, the two condensers out)."""
    module = _script()
    values = module.balance()
    for sid in ("S6", "S7"):
        state = _state(model, sid)
        assert state["flow"]["source"].startswith("scripts/makeup_drying.py")
        assert state["flow"]["value"] == pytest.approx(values[sid]["flow"], abs=1e-4), sid
        for comp, x in values[sid]["composition"].items():
            assert state["composition"]["values"][comp] == pytest.approx(x, abs=1e-6), (sid, comp)
    for qid in ("Q10", "Q11", "Q12", "P4"):
        assert _state(model, qid)["duty"]["source"].startswith("scripts/makeup_drying.py")
        assert _duty(model, qid) == pytest.approx(values[qid]["duty"], abs=1e-4), qid
    heater = _duty(model, "P4") - module.BLOWER_KW
    assert _duty(model, "Q10") + heater == pytest.approx(_duty(model, "Q11") + _duty(model, "Q12"), abs=1e-3)
    # the dried make-up's water takes potassium to KOH: WAT's extent is the water fed
    assert _kmol(model, "S10")["KOH"] == pytest.approx(_kmol(model, "S6")["H2O"], rel=1e-3)


def test_hand_duties_follow_the_streams(model):
    """D-008, D-009."""
    cycle = _cycle_h(model)
    q7 = (_mcp(model, "S14") * (433.15 - 313.15) + 2000 * 120 / cycle) / 3600
    assert _duty(model, "Q7") == pytest.approx(q7, abs=0.01)
    n16 = _kmol(model, "S16")["TBA"]
    q8 = n16 * (141.0 * (433.15 - 355.45) + 39070 + 246.4 * (355.45 - 308.15)) / 3600 + 1.845
    assert _duty(model, "Q8") == pytest.approx(q8, abs=0.01)
    k = _kmol(model, "S1")["K"]
    q9 = k * (29.6 * (336.65 - 298.15) + 2270 + 32.03 * (353.15 - 336.65)) / 3600
    assert _duty(model, "Q9") == pytest.approx(q9, abs=0.001)
    q13 = _mcp(model, "S21") * (_temperature(model, "S21") - _temperature(model, "S24")) / 3600
    assert _duty(model, "Q13") == pytest.approx(q13, abs=0.01)
    # P3's vacuum pump share is what Q8 adds
    assert "1.845 kW" in _state(model, "Q8")["duty"]["source"] and "1.845 kW" in _state(model, "P3")["duty"]["source"]


def test_dryer_bleed_sets_the_alcohol_loss(model):
    """D-008: 10 Nm3 of nitrogen a batch leaves E-201 saturated with tert-butanol at 308.15 K."""
    flowsheet = _yaml("process/flowsheet.yaml")
    split = next(s for s in flowsheet["steps"] if s["id"] == "SP201")["split"]["loss"]
    y = _psat_tba(model, 308.15) / 101.325
    assert _psat_tba(model, 308.15) == pytest.approx(10.32, abs=0.01)
    lost = 10 / 22.414 * y / (1 - y)  # kmol a batch
    vapour = _kmol(model, "S16")["TBA"] * _cycle_h(model)
    assert split == pytest.approx(lost / vapour, rel=0.002)
    consumable = _yaml("lca/lca.yaml")["consumables"][0]
    assert "DR-101's bleed during the drying (10 Nm3" in consumable["source"]


def test_assumed_temperatures_are_the_adiabatic_mixes(model):
    assert _temperature(model, "S8") == pytest.approx(_mix(model, "S6", "S19"), abs=0.02)
    assert _temperature(model, "S21") == pytest.approx(_mix(model, "S12", "S18"), abs=0.02)
    recipe = _recipe()
    heat = next(op for up in recipe["unit_procedures"] for op in up["operations"] if op["id"] == "heat")
    assert heat["temperatures"][0] == _temperature(model, "S8")
    # the vent header: both inlets at the condensers' 308.15 K
    assert _temperature(model, "S23") == _temperature(model, "S20") == 308.15


def test_jacket_on_the_log_mean_of_the_cooling_water(model):
    """Lesson of the wave-2 reviews: the jacket's coolant temperature is the log-mean equivalent
    of the cooling water's supply and return at the reaction temperature."""
    flowsheet = _yaml("process/flowsheet.yaml")
    cw = next(p for p in flowsheet["products"] if p["id"] == "CW")["utility"]
    t_in, t_out = cw["supply_temperature"]["value"], cw["return_temperature"]["value"]
    tp = _temperature(model, "S9")
    lmtd = ((tp - t_in) - (tp - t_out)) / math.log((tp - t_in) / (tp - t_out))
    jacket = next(u for u in _recipe()["unit_procedures"] if u["id"] == "REACT")["vessel"]["jacket"]
    assert jacket["coolant_temperature"] == pytest.approx(tp - lmtd, abs=0.01)
    # the vent condenser stays above tert-butanol's freezing point (298.3 K)
    r101 = next(s for s in flowsheet["steps"] if s["id"] == "R101")
    assert r101["batch"]["vent"]["condenser"]["temperature"] > 298.3 + 5


def test_heating_media_below_the_stated_limits(model):
    """D-008: MP steam (453 K) below the alkoxide's sublimation at 493 K and 0.13 kPa and its
    melting point 529 K; the dryer at 433 K; the still on LP steam (412 K)."""
    flowsheet = _yaml("process/flowsheet.yaml")
    feeds = {f["id"]: f for f in flowsheet["feeds"]}
    mps = feeds["MPS"]["utility"]["supply_temperature"]["value"]
    lps = feeds["LPS"]["utility"]["supply_temperature"]["value"]
    assert mps < 493.15 < 529.15 and lps < mps
    d101 = next(s for s in flowsheet["steps"] if s["id"] == "D101")["dryer"]
    assert d101["temperature"] < mps
    assert "below the alkoxide's sublimation at 493 K" in _text("DESIGN.md")
    # the alkoxide's vapour pressure at the dryer: Clausius-Clapeyron between Wikipedia's points
    slope = math.log(0.13332 / 0.001) / (1 / 413.15 - 1 / 493.15)
    p433 = 0.001 * math.exp(slope * (1 / 413.15 - 1 / 433.15))
    assert p433 == pytest.approx(0.004, abs=0.0005)


def _inventory() -> dict[str, list[str]]:
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        return {r["key"]: r for r in csv.DictReader(fh)}


def test_every_energy_flow_reaches_the_lci(model):
    """Library ADR 0035: each utility's per-kg total is its energy streams' sum, as stated."""
    _, streams = model
    product = _flow(model, "S15")
    inventory = _inventory()
    expect = {
        "product:CW": ({"Q2", "Q3", "Q5", "Q7", "Q8", "Q11", "Q12", "Q13"}, 1.774),
        "feed:LPS": ({"Q1", "Q4", "Q9", "Q10", "Q14"}, 1.188),
        "feed:MPS": ({"Q6"}, 0.357),
        "feed:POWER": ({"P1", "P2", "P3", "P4"}, 0.325),
    }
    for key, (ids, per_kg) in expect.items():
        node = key.split(":")[1]
        found = {
            s["id"] for s in streams.values()
            if s.get("kind") == "energy" and (s["from"].startswith(node + ".") or s["to"].startswith(node + "."))
        }
        assert found == ids, key
        total = sum(_duty(model, q) for q in ids) / product
        assert total == pytest.approx(per_kg, abs=0.0006), key
        assert float(inventory[key]["quantity"]) == pytest.approx(total, rel=1e-3), key
        assert f"{per_kg:.3f} kWh" in _text("DESIGN.md"), key
        assert f"{per_kg:.3f} kWh" in _text("process.yaml"), key


def test_yield_and_assay_as_stated(model):
    materials, _ = model
    product = _kmol(model, "S15")
    mass = _flow(model, "S15")
    assay = product["KOTBU"] * materials["KOTBU"]["molar_mass"] / mass
    assert assay == pytest.approx(0.9947, abs=0.00005)
    assert product["KOH"] * materials["KOH"]["molar_mass"] / mass == pytest.approx(0.0023, abs=0.00005)
    on_k = product["KOTBU"] / _kmol(model, "S1")["K"]
    assert on_k == pytest.approx(0.995, abs=0.0005)
    on_tba = product["KOTBU"] / _kmol(model, "S3")["TBA"]
    assert on_tba == pytest.approx(0.895, abs=0.0005)
    for rel in ("process.yaml", "DESIGN.md", "README.md"):
        text = _text(rel)
        assert "99.47 wt%" in text and "upper bound" in text, rel
        assert "99.5 % on potassium" in text or "99.55 % on potassium" in text, rel
        assert "89.5 %" in text, rel


def _hazard() -> dict:
    return next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == "R101")["hazard"]


def test_vent_capacity_basis_and_sensitivity_are_recorded():
    """D-006, D-011: the vent's 200 m3/h (ASSUMED) about twice the normal wet peak, its basis in
    the node's source, the rate sensitivity recorded as a design finding; no TD24 estimated."""
    hazard = _hazard()
    assert hazard["vent_capacity"] == 200 and hazard["provenance"] == "assumed"
    assert "td24" not in hazard and "mtt" not in hazard
    # the normal peak before the vent condenser, from the recipe's rate past it
    past = 0.3817  # mol/s, cheme process recipe
    y308 = 10.32 / 101.325
    wet = past * (1 - y308) / (1 - 0.656) / 1000 * 8.314 * 348.15 / 101.325 * 3600
    assert wet == pytest.approx(102.5, abs=0.1)
    assert "102.5 m3/h" in hazard["source"] and "133.4 m3/h" in hazard["source"]
    design = _text("DESIGN.md")
    assert "| k (design) | 3.09 % | 350.1 K | 0.743 h | 38.36 m3/h | 133.4 m3/h, 0.67 of the vent |" in design
    assert "| k/10 | 29.6 % | 366.9 K |" in design and "| k/100 | 85.1 % | 399.9 K |" in design
    assert "**Design finding:**" in design and "emergency relief" in design
    assert "**Loss of the flare**" in design and "**Water and potassium**" in design


def test_criticality_classes_without_td24_are_cores():
    """The classes DESIGN.md states as possible are those core's criticality() can give."""
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import criticality

    mtt = 355.45
    for mtsr, stated in ((350.14, "classes 1 (TD24 above the MTT), 2 (TD24 between the MTSR and the MTT) or 5 (TD24 below the MTSR)"), (366.9, "classes 3 (TD24 above the MTSR), 4 or 5")):
        possible = {criticality(mtsr, mtt, td24) for td24 in (300.0, 340.0, 352.0, 360.0, 380.0, 450.0)}
        assert str(sorted(possible)) and stated in _text("DESIGN.md")
        numbers = {int(c) for c in stated.replace(",", " ").split() if c.isdigit()}
        assert possible == numbers, mtsr


def test_core_screens_the_reactor():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.chemistry.thermochemistry import R
    from chemeascode.domains.process.model import load
    from chemeascode.domains.process.recipe import hours_per_batch
    from chemeascode.domains.process.stirred_tank import solve_node, vent_gas_rate
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    entry = next(e for e in report.entries if e.node == "R101")
    assert entry.mtsr == pytest.approx(350.14, abs=0.01)
    assert entry.mtt == pytest.approx(355.45, abs=0.01)
    assert entry.accumulation == pytest.approx(0.0309, abs=0.0001)
    assert entry.adiabatic_rise == pytest.approx(60.2, abs=0.05)
    gas = entry.gas_release
    assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(133.4, abs=0.1)
    assert gas["noncondensable_m3_h"] == pytest.approx(38.36, abs=0.01)
    assert gas["capacity_ratio"] == pytest.approx(0.67, abs=0.005)
    assert not [f for f in report.findings if f.level in ("warning", "error")]
    # the largest non-condensable release over the batch is at core's worst moment
    process, _ = load(PROCESS)
    fs = process.flowsheet
    case = fs.default_case()
    hours = hours_per_batch(process, case)
    item = process.nodes["R101"]
    inlets = [s for s in fs.streams if s.kind == "material" and (e := process.ends(s)[1]) is not None and e.node == "R101"]
    solved, _ = solve_node(process, item, inlets, case)
    best = max(
        (hours * vent_gas_rate(process, item, p.moles, p.mtsr(), solved.pressure) * R * p.mtsr() / solved.pressure * 3600, p.time)
        for p in solved.cooling_profile
    )
    assert best[0] == pytest.approx(38.36, abs=0.01) and best[1] == pytest.approx(10800.0, abs=1.0)


def test_recipe_basis_gives_1000_t_per_year(model):
    recipe = _recipe()
    rate = _flow(model, "S15")
    assert rate * recipe["hours_per_year"]["value"] / 1000 == pytest.approx(1000, rel=0.001)
    batches = rate * recipe["hours_per_year"]["value"] / recipe["batch_size"]["value"]
    assert batches == pytest.approx(1202.4, abs=0.1)  # D-003
    assert _cycle_h(model) == pytest.approx(6.586, abs=0.001)
    assert "6.586 h" in _text("DESIGN.md") and "1202 batches" in _text("process.yaml")


def test_property_sources_are_registered():
    """ADR 0037: the package values have a register row that names the package, version, method
    and underlying work and does not call them open data."""
    register = next(line for line in (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines() if line.startswith("| SRC-9 |"))
    for name in ("chemicals` 1.5.2", "thermo` 0.6.1", "DIPPR_PERRY_8E", "Perry's", "CRC", "NIST", "CoolProp"):
        assert name in register, name
    assert "not open data" in register
    assert "SRC-9" in _text("process/materials.yaml")


def test_downstream_links_this_product():
    """D-014: di-tert-butyl-dicarbonate-1's feed:KOTBU links this product kg for kg."""
    boc = yaml.safe_load((KIT / "processes" / "di-tert-butyl-dicarbonate-1" / "lca" / "mappings.yaml").read_text(encoding="utf-8"))
    link = boc["exchanges"]["feed:KOTBU"]["dataset"]
    assert link == {"path": "processes/potassium-tert-butoxide-1/lca/dataset.yaml", "product": "product:KOTBU"}
    dataset = _yaml("lca/dataset.yaml")
    assert any(e["key"] == "product:KOTBU" and e["unit"] == "kg" for e in dataset["exchanges"])
    mine = _yaml("lca/mappings.yaml")["exchanges"]
    assert mine["feed:TBAF"]["dataset"]["product"] == "product:tert-butanol"
    assert "feed:K" not in mine  # potassium metal stays a gap (D-012)


def test_requires_core_1_10_and_is_public():
    assert _yaml("plant.yaml")["requires"] == "cheme-as-code>=1.10"
    assert _yaml("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "Needs cheme-as-code 1.10.0" in _text("README.md")
