"""copper-i-chloride-1 (#143): the folder's hand-written numbers against its own model.

Fast, without core: the flowsheet's calculated streams (written by cheme process propagate) and
the materials' molar masses and heat capacities are enough to check what the folder states by
hand (DESIGN.md D-003 to D-012):

- the duties written as hand arithmetic (Q1, Q3, Q6, Q7) follow from the streams they name, and
  R101's model writes Q2 at its `energy_port` (core 1.9.0, ADR 0059) with the value a hand Hess
  path through the reactions' extents gives;
- every temperature assumed for a mixed stream is the mix of its inlets (with the salt's heat of
  solution, the acid's heat of dilution and the ethanol's heat of mixing where the source names
  them), and so are the crystallizers' temperatures;
- the solubilities of CR101 and W101 are the power law of D-006 at their solved liquors, and the
  law passes through its two open points and is 14 % below US 3 030 178 A's brine;
- the two recycles are core's tears (ADR 0060), calculated, and the heel is about half the copper
  consumed;
- the jacket's coolant is the cooling water's log-mean, and the dryer's hot water stays at the
  product's temperature limit;
- the yield on copper and the product's assay stated in process.yaml, README.md and DESIGN.md
  hold, and both carry their caveats (the assay an ASSUMED upper bound, the loss to the brine);
- every energy flow reaches the LCI (library ADR 0035): the utilities per kg in the inventory are
  the sums of their streams, as process.yaml and DESIGN.md state;
- the recipe's batch size times its batches per year gives the flowsheet's product rate, 300 t/a;
- with core: the screening's accumulation, MTSR and MTT, and the classes still possible without a
  TD24 exactly as core's criticality() gives them;
- the process is not set public and carries no licence in the change that adds it.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "copper-i-chloride-1"
RATE = 37.8991  # kg/h of S29, the flowsheet's product rate
CYCLE_H = 9.367  # the recipe's cycle (cheme process recipe, D-003)


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    flowsheet = _yaml("process/flowsheet.yaml")
    streams = {s["id"]: s for s in flowsheet["streams"]}
    steps = {s["id"]: s for s in flowsheet["steps"]}
    return materials, streams, steps


def _kmol(model, sid: str) -> dict[str, float]:
    materials, streams, _ = model
    state = streams[sid]["state"]["design"]
    flow = state["flow"]["value"]
    comp = state["composition"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * materials[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mm * x for k, x in comp["values"].items()}
    return {k: flow * w / materials[k]["molar_mass"] for k, w in comp["values"].items()}


def _kg(model, sid: str) -> dict[str, float]:
    materials = model[0]
    return {k: n * materials[k]["molar_mass"] for k, n in _kmol(model, sid).items()}


def _mcp(model, sid: str) -> float:
    """kJ/(K h) of a stream from the components' liquid heat capacities."""
    materials = model[0]
    return sum(n * materials[k]["liquid_heat_capacity"] for k, n in _kmol(model, sid).items() if n)


def _t(model, sid: str) -> float:
    return model[1][sid]["state"]["design"]["temperature"]["value"]


def _duty(model, qid: str) -> float:
    return model[1][qid]["state"]["design"]["duty"]["value"]


def _mix(model, *sids: str, heat_kj_h: float = 0.0) -> float:
    return (sum(_mcp(model, s) * _t(model, s) for s in sids) + heat_kj_h) / sum(
        _mcp(model, s) for s in sids
    )


def test_hand_duties_follow_the_streams(model):
    assert _duty(model, "Q1") == pytest.approx(_mcp(model, "S7") * (353.15 - _t(model, "S7")) / 3600, rel=0.002)
    assert _duty(model, "Q3") == pytest.approx(_mcp(model, "S9") * 45 / 3600, rel=0.002)
    v = _kg(model, "S28")
    q6 = (v["H2O"] * 2358 + v["ETOH"] * 866 + v.get("HCL", 0.0) * 443 + _mcp(model, "S28") * 43) / 3600
    assert _duty(model, "Q6") == pytest.approx(q6, rel=0.002)
    q7 = (_mcp(model, "S29") * 30 + 2000 * 30 / CYCLE_H) / 3600  # product and F-101's metal
    assert _duty(model, "Q7") == pytest.approx(q7, rel=0.002)
    for qid in ("Q1", "Q3", "Q6", "Q7"):
        assert model[1][qid]["state"]["design"]["duty"]["provenance"] == "assumed", qid


def test_r101_model_writes_its_duty(model):
    """Core ADR 0059: Q2 is calculated at R101's energy port; a hand path through the extents
    (CHL takes all the chlorine, COMP makes the CuCl) less the chlorine warmed to 353 K."""
    _, streams, steps = model
    assert steps["R101"]["energy_port"] == "q"
    q2 = streams["Q2"]
    assert q2["from"] == "R101.q" and q2["to"].startswith("CW.")
    assert q2["state"]["design"]["duty"]["provenance"] == "calculated"
    s7, s8, s9 = _kmol(model, "S7A"), _kmol(model, "S8"), _kmol(model, "S9")
    chl = s8["CL2"] - s9.get("CL2", 0.0)
    comp = (s9["CUCL"] - s7["CUCL"]) / 2
    hand = (chl * 220_100 + comp * 54_300 - _mcp(model, "S8") * (353.15 - 298.15)) / 3600
    assert _duty(model, "Q2") == pytest.approx(hand, rel=0.003)


def test_mixed_temperatures_follow_their_inlets(model):
    """D-009: every assumed mixed temperature, and the crystallizers', is the mix of its inlets."""
    _, _, steps = model
    salt = _kmol(model, "S1")["NACL"] * 3880  # heat of solution, endothermic (ASSUMED)
    acid3 = _kmol(model, "S3")["HCL"] * 17_500
    t4 = _mix(model, "S17", "S1", "S2", "S3", heat_kj_h=acid3 - salt)
    assert _t(model, "S4") == pytest.approx(t4, abs=0.02)
    assert _t(model, "S7") == pytest.approx(_mix(model, "S4", "S5", "S6"), abs=0.02)
    tcr = _mix(model, "S11A", "S12")
    assert steps["CR101"]["crystallizer"]["temperature"] == pytest.approx(tcr, abs=0.02)
    for sid in ("S13", "S14", "S15", "S16", "S17", "S32", "S33"):
        assert _t(model, sid) == pytest.approx(tcr, abs=0.02), sid
    acid19 = _kmol(model, "S19")["HCL"] * 17_500
    assert _t(model, "S20") == pytest.approx(_mix(model, "S18", "S19", heat_kj_h=acid19), abs=0.02)
    tw = _mix(model, "S32", "S20")
    assert steps["W101"]["crystallizer"]["temperature"] == pytest.approx(tw, abs=0.02)
    for sid in ("S21", "S22", "S23"):
        assert _t(model, sid) == pytest.approx(tw, abs=0.02), sid
    liquid = _kmol(model, "S22")["H2O"] + _kmol(model, "S24")["ETOH"]
    tm = _mix(model, "S22", "S24", heat_kj_h=600 * liquid)
    for sid in ("S25", "S26", "S27"):
        assert _t(model, sid) == pytest.approx(tm, abs=0.02), sid
    assert _t(model, "S30") == pytest.approx(_mix(model, "S16", "S33", "S23", "S34"), abs=0.02)
    assert _t(model, "S31") == pytest.approx(_mix(model, "S27", "S28"), abs=0.02)
    assert _yaml("process/simulation.yaml")["specs"]["CR101"]["mode"] == "adiabatic"


EXPONENT = math.log(39.6 / 1.0) / math.log(2.5 / 0.282)  # D-006, through SRC-5's two points


def _excess_chloride(model, sid: str) -> float:
    """mol of chloride not bound to copper(I) per kg of water: NaCl, HCl, 2 x CuCl2."""
    n = _kmol(model, sid)
    return (n["NACL"] + n["HCL"] + 2 * n.get("CUCL2", 0.0)) * 1000 / (n["H2O"] * 18.015)


def test_solubilities_follow_the_power_law(model):
    _, _, steps = model
    assert EXPONENT == pytest.approx(1.686, abs=0.001)
    law = lambda m: 1.0 * (m / 0.282) ** EXPONENT  # g/L, read as g per kg of liquor
    assert law(0.282) == pytest.approx(1.0) and law(2.5) == pytest.approx(39.6)
    assert law(5.13) == pytest.approx(133, abs=1.5)  # the brine; US 3 030 178 A holds 155 g/L
    assert 1 - law(5.13) / 155 == pytest.approx(0.14, abs=0.01)
    for node, sid, m in (("CR101", "S15", 0.621), ("W101", "S23", 0.144)):
        sol = steps[node]["crystallizer"]["solubility"]
        assert sol["measured_in"] == "mother_liquor" and sol["unit"] == "kg/kg_liquor", node
        assert _excess_chloride(model, sid) == pytest.approx(m, abs=0.002), node
        assert sol["value"] * 1000 == pytest.approx(law(_excess_chloride(model, sid)), rel=0.01), node
    # what the crystallizer leaves dissolved: the clear liquor at its solubility per kg of liquor
    s15 = _kg(model, "S15")
    liquor = sum(v for k, v in s15.items() if k not in ("CUCL", "CUCL_S"))
    assert s15["CUCL"] / liquor == pytest.approx(steps["CR101"]["crystallizer"]["solubility"]["value"], rel=0.002)


def test_recycles_are_tears_and_the_heel_is_half_the_copper(model):
    flowsheet = _yaml("process/flowsheet.yaml")
    assert {t["stream"] for t in flowsheet["tears"]} == {"S6", "S17"}
    for sid in ("S6", "S17"):
        flow = model[1][sid]["state"]["design"]["flow"]
        assert flow["provenance"] == "calculated" and "tear" in flow["source"], sid
    s7, s9 = _kmol(model, "S7A"), _kmol(model, "S9")
    consumed = s7["CU"] - s9["CU"]
    assert s9["CU"] / consumed == pytest.approx(0.51, abs=0.01)  # D-004, about SRC-3's 50 %
    assert s9["CUCL2"] / (s9["CUCL2"] + s9["CUCL"]) == pytest.approx(0.0052, abs=0.0003)
    assert model[2]["SP101"]["split"]["mlr"] == pytest.approx(0.1)


def test_jacket_on_the_log_mean_and_the_dryer_below_its_limit(model):
    recipe = _yaml("process/recipe.yaml")
    r101 = next(u for u in recipe["unit_procedures"] if u["id"] == "CHLORINATE")
    jacket = r101["vessel"]["jacket"]
    lmtd = (55 - 45) / math.log(55 / 45)  # CW 298.15/308.15 K against 353.15 K
    assert jacket["coolant_temperature"] == pytest.approx(353.15 - lmtd, abs=0.01)
    assert "log-mean" in jacket["source"]
    heat = next(o for o in r101["operations"] if o["id"] == "heat")
    assert heat["temperatures"][0] == pytest.approx(_t(model, "S7"), abs=0.01)
    dryer = model[2]["D101"]["dryer"]
    assert dryer["temperature"] < 343.15 and "hot water at 343 K" in dryer["energy"]["source"]
    design = _text("DESIGN.md")
    assert "the wet product stays below 343 K, and so does the heating water (343 K)" in design


def test_yield_and_assay_as_stated(model):
    product = _kmol(model, "S29")
    cucl = product["CUCL_S"] + product.get("CUCL", 0.0)
    yield_cu = cucl / _kmol(model, "S5")["CU"]
    assert yield_cu == pytest.approx(0.776, abs=0.001)
    assay = cucl * 98.999 / sum(_kg(model, "S29").values())
    assert assay == pytest.approx(0.998, abs=0.0005)
    s30 = _kmol(model, "S30")
    lost = sum(s30.get(k, 0.0) for k in ("CUCL", "CUCL_S", "CUCL2", "CU"))
    assert lost / _kmol(model, "S5")["CU"] == pytest.approx(0.223, abs=0.001)
    for rel in ("process.yaml", "README.md", "DESIGN.md"):
        text = _text(rel)
        assert "77.6 %" in text and "upper bound" in text, rel
    assert "22.3 %" in _text("process.yaml") and "22.3 %" in _text("README.md")
    assert "upper bound" in _yaml("process/design-basis.yaml")["products"][0]["purity"]


def test_every_energy_flow_reaches_the_lci(model):
    _, streams, _ = model
    energy = [s for s in streams.values() if s.get("kind") == "energy"]
    def per_kg(prefix: str) -> float:
        return sum(s["state"]["design"]["duty"]["value"] for s in energy if s["to"].startswith(prefix) or s["from"].startswith(prefix)) / RATE
    assert {s["id"] for s in energy if s["to"].startswith("CW.")} == {"Q2", "Q3", "Q7"}
    assert {s["id"] for s in energy if s["to"].startswith("CHW.")} == {"Q6"}
    inventory = {r.split(",")[0]: r for r in (PROCESS / "lca/inventory.csv").read_text().splitlines()[1:]}
    def inv(key: str) -> float:
        import csv
        row = next(csv.reader([inventory[key]]))
        return float(row[7])
    for key, prefix, stated in (("product:CW", "CW.", "1.032 kWh"), ("product:CHW", "CHW.", "0.036 kWh"), ("feed:LPS", "LPS.", "0.750 kWh"), ("feed:POWER", "POWER.", "0.304 kWh")):
        assert inv(key) == pytest.approx(per_kg(prefix), rel=1e-3), key
        assert stated in _text("process.yaml") and stated in _text("DESIGN.md"), key
    assert _duty(model, "Q5") == pytest.approx(4.6765, abs=0.001)  # cheme process crystallizers


def test_recipe_basis_gives_300_t_per_year(model):
    recipe = _yaml("process/recipe.yaml")
    rate = model[1]["S29"]["state"]["design"]["flow"]["value"]
    assert rate == pytest.approx(RATE, abs=1e-3)
    assert rate * recipe["hours_per_year"]["value"] / 1000 == pytest.approx(300, rel=0.001)
    assert recipe["batch_size"]["value"] == pytest.approx(rate * CYCLE_H, rel=0.002)
    batches = recipe["hours_per_year"]["value"] / CYCLE_H
    assert batches == pytest.approx(845.6, abs=0.2)


def test_dilution_and_feed_ratios(model):
    vol = sum(n * model[0][k]["liquid_molar_volume"] for k, n in _kmol(model, "S11A").items() if n)
    assert model[1]["S12"]["state"]["design"]["flow"]["value"] / 997 / vol == pytest.approx(6.9, abs=0.05)
    s4 = _kg(model, "S4")
    assert s4["NACL"] / (s4["NACL"] + s4["H2O"]) == pytest.approx(0.249, abs=0.001)
    assert 2 * _kmol(model, "S8")["CL2"] == pytest.approx(_kmol(model, "S7A")["CU"] - _kmol(model, "S9")["CU"] + _kmol(model, "S9")["CUCL2"], rel=0.002)


def test_core_screening_and_the_classes_without_td24():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import criticality, screen

    report = screen(PROCESS)
    entry = next(e for e in report.entries if e.node == "R101")
    assert entry.mtsr == pytest.approx(354.2, abs=0.05)
    assert entry.mtt == pytest.approx(373.12, abs=0.01)
    assert entry.accumulation == pytest.approx(0.0063, abs=0.0002)
    possible = {criticality(entry.mtsr, entry.mtt, td24) for td24 in (300.0, 360.0, 400.0)}
    assert possible == {1, 2, 5}
    design = _text("DESIGN.md")
    assert "the classes still possible are 1 (TD24 above the MTT, 373.1 K), 2 (TD24 between the MTSR and the MTT) and 5 (TD24 below the MTSR, 354.2 K)" in design
    assert "| k/10 | 4.26 % | 357.9 K | 373.1 K |" in design
    assert "| k/100 | 28.1 % | 363.5 K | 373.1 K |" in design
    assert not [f for f in report.findings if f.level in ("warning", "error")]


def test_property_sources_are_registered():
    register = next(l for l in (PROCESS / "DESIGN.md").read_text().splitlines() if l.startswith("| SRC-10 |"))
    for name in ("chemicals", "CRC", "CoolProp"):
        assert name in register, name
    cited = _text("process/materials.yaml") + _text("process/reactions.yaml") + _text("process/flowsheet.yaml")
    assert "SRC-10" in cited
    assert "CRC Handbook)" not in cited.replace("citing the CRC Handbook", "")


def test_requires_core_1_9_and_not_published():
    assert _yaml("plant.yaml")["requires"] == "cheme-as-code>=1.9"
    assert "1.9.0" in _text("README.md") and "cheme-as-code 1.9.0" in _text("process.yaml")
    publication = _yaml("process.yaml")["publication"]
    assert publication["status"] == "internal" and "license" not in publication


def test_duties_stated_in_design_are_the_flowsheets(model):
    design = _text("DESIGN.md")
    for qid in ("Q1", "Q2", "Q3", "Q5", "Q6", "Q7"):
        stated = f"{qid} {_duty(model, qid):.2f} kW"
        assert stated in design, stated
    power = sum(_duty(model, p) for p in ("P1", "P2", "P3"))
    assert f"electricity {power:.2f} kW" in design
