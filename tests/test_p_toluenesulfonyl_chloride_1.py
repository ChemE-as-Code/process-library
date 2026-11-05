"""p-toluenesulfonyl-chloride-1 (#162): the folder's hand-written numbers against its own model.

Fast, without core: the flowsheet's calculated streams (written by cheme process propagate) and
the materials' molar masses and heat capacities are enough to check what the folder states by
hand (DESIGN.md D-004, D-007, D-009):

- the duties written as hand arithmetic (Q1, Q3, Q4, Q5 and its dilution share, Q7, Q8, Q9)
  follow from the streams they name, and the quench jacket's peak with the dilution heat is the
  one DESIGN.md and the equipment list state;
- every energy flow of the batch reaches the LCI (library ADR 0035): the dryer's vacuum
  condenser and the wash water's chilling are on brine, and product:BRINE per kg is their sum;
- the assumed temperatures of the adiabatic washes, the waste acid and the vent header are the
  mixes of their inlets;
- the feeds keep the patent's ratios per mol of toluene (1.5 + 1.5 mol ClSO3H, 0.45 mol NH4Cl);
- the yield on toluene and the product's assay stated in process.yaml and DESIGN.md hold, and
  both carry their caveats (the yield above the patent's 77 %, the assay an upper bound);
- the property sources cited in the materials and the flowsheet have a register row;
- the recipe's batch size times its batches per year gives the flowsheet's product rate, the
  1000 t/a of the design basis;
- the process is not set public, and carries no licence, in the change that adds it
  (CONTRIBUTING, "Publishing a process").
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "p-toluenesulfonyl-chloride-1"


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    flowsheet = _yaml("process/flowsheet.yaml")
    streams = {s["id"]: s for s in flowsheet["streams"]}
    return materials, streams


def _kmol(model, sid: str) -> dict[str, float]:
    """kmol/h of each component of a material stream."""
    materials, streams = model
    state = streams[sid]["state"]["design"]
    flow = state["flow"]["value"]
    comp = state["composition"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * materials[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mm * x for k, x in comp["values"].items()}
    return {k: flow * w / materials[k]["molar_mass"] for k, w in comp["values"].items()}


def _mcp(model, sid: str) -> float:
    """kJ/(K h) of a stream from the components' liquid heat capacities."""
    materials, _ = model
    return sum(n * materials[k]["liquid_heat_capacity"] for k, n in _kmol(model, sid).items() if n)


def _duty(model, qid: str) -> float:
    return model[1][qid]["state"]["design"]["duty"]["value"]


def test_feed_ratios_follow_the_patent(model):
    tol = _kmol(model, "S4")["TOL"]
    assert _kmol(model, "S1")["CSA"] / tol == pytest.approx(1.5, rel=1e-3)
    assert _kmol(model, "S7")["CSA"] / tol == pytest.approx(1.5, rel=1e-3)
    assert _kmol(model, "S3")["NH4CL"] / tol == pytest.approx(0.45, rel=1e-3)


def test_hand_duties_follow_the_streams(model):
    assert _duty(model, "Q1") == pytest.approx(_mcp(model, "S1") * 40 / 3600, rel=0.01)
    assert _duty(model, "Q4") == pytest.approx(_mcp(model, "S9") * 10 / 3600, rel=0.01)
    s8 = _kmol(model, "S8")
    dilution = s8["H2SO4"] * 75_000 + (s8["PTSA"] + s8["OTSA"]) * 20_000  # kJ/h
    assert dilution / 3600 == pytest.approx(16.03, rel=0.01)  # the share D-009 states
    # Q5: Q101's reactions from its extents, the dilution, S8 cooled from 308 to 288 K
    s12 = _kmol(model, "S12")
    hyd = s8["CSA"] - s12.get("CSA", 0.0)
    amh = s8["AMCS"] - s12.get("AMCS", 0.0)
    tsh = (s8["PTSCL"] - s12["PTSCL"]) + (s8["OTSCL"] - s12["OTSCL"])
    reactions = hyd * 180_000 + amh * 80_000 + tsh * 60_000
    q5 = (reactions + dilution + _mcp(model, "S8") * 20) / 3600
    assert _duty(model, "Q5") == pytest.approx(q5, rel=0.01)
    # Q3: S6 cooled 30 K, the second stage's heat, less S7 warmed 10 K
    s6, s7 = _kmol(model, "S6"), _kmol(model, "S7")
    chl = (s6["PTSA"] - s8["PTSA"]) + (s6["OTSA"] - s8["OTSA"])
    q3 = (_mcp(model, "S6") * 30 + chl * 10_000 - _mcp(model, "S7") * 10) / 3600
    assert _duty(model, "Q3") == pytest.approx(q3, rel=0.01)


def _temperature(model, sid: str) -> float:
    return model[1][sid]["state"]["design"]["temperature"]["value"]


def _mix(model, *sids: str) -> float:
    """Adiabatic mixing temperature of the streams, from their heat capacity flows."""
    return sum(_mcp(model, s) * _temperature(model, s) for s in sids) / sum(
        _mcp(model, s) for s in sids
    )


def _text(rel: str) -> str:
    return (PROCESS / rel).read_text(encoding="utf-8")


def test_quench_jacket_peak_with_the_dilution_heat(model):
    """D-003: the dilution share of Q5 released over Q101's 4 h dosing, on top of the model's
    135 kW peak (`cheme process recipe`)."""
    recipe = _yaml("process/recipe.yaml")
    flowsheet = _yaml("process/flowsheet.yaml")
    q101 = next(s for s in flowsheet["steps"] if s["id"] == "Q101")
    dosing_s = q101["batch"]["dosing"][0]["time"]
    s8 = _kmol(model, "S8")
    dilution_kJ_h = s8["H2SO4"] * 75_000 + (s8["PTSA"] + s8["OTSA"]) * 20_000
    batches = 126.263 * recipe["hours_per_year"]["value"] / recipe["batch_size"]["value"]
    cycle_h = recipe["hours_per_year"]["value"] / batches
    peak = dilution_kJ_h * cycle_h / dosing_s
    assert peak == pytest.approx(55.5, abs=0.1)
    assert 135 + peak == pytest.approx(190.5, abs=0.2)
    for rel in ("DESIGN.md", "equipment/equipment-list.yaml"):
        text = _text(rel)
        assert "55.5 kW" in text and "190.5 kW" in text, rel
        assert "189 kW" not in text and "54 kW" not in text, rel


def test_every_energy_flow_reaches_the_brine(model):
    """Library ADR 0035: the dryer's vacuum condenser (Q8) and the wash water's chilling (Q9)
    are energy streams to brine, so product:BRINE per kg counts them."""
    _, streams = model
    s25 = _kmol(model, "S25")
    water_kg = s25["H2O"] * 18.015
    q8 = water_kg * (2418.0 + 4.18 * 10) / 3600  # D101's latent heat, condensate 308 to 298 K
    assert _duty(model, "Q8") == pytest.approx(q8, rel=0.005)
    assert _duty(model, "Q9") == pytest.approx(_mcp(model, "S31") * 20 / 3600, rel=0.005)
    assert _temperature(model, "S31") - _temperature(model, "S32") == pytest.approx(20)
    brine = [s for s in streams.values() if s.get("kind") == "energy" and s["to"].startswith("BRINE.")]
    assert {s["id"] for s in brine} == {"Q4", "Q5", "Q8", "Q9"}
    per_kg = sum(s["state"]["design"]["duty"]["value"] for s in brine) / 126.263
    assert per_kg == pytest.approx(0.811, abs=0.001)  # D-012, process.yaml
    inventory = {
        row.split(",")[0]: row.split(",") for row in _text("lca/inventory.csv").splitlines()[1:]
    }
    assert float(inventory["product:BRINE"][7]) == pytest.approx(per_kg, rel=1e-3)
    washw = next(f for f in _yaml("lca/lca.yaml")["flows"] if f["key"] == "feed:WASHW")
    assert "not counted" not in washw["missing"]
    assert "0.811 kWh" in _text("process.yaml") and "0.811 kWh" in _text("DESIGN.md")


def test_scrubber_duty_with_the_caustic_dilution(model):
    """Q7 (D-009): NEUT, less the liquor's 10 K rise, plus the 50 wt% caustic's ASSUMED dilution
    heat and the vent gas S27 cooled to the liquor's 308 K."""
    s27 = _kmol(model, "S27")
    neut = 0.999 * s27["HCL"] * 132_000
    liquor = model[1]["S30"]["state"]["design"]["flow"]["value"] * 3.6 * 10
    caustic = _kmol(model, "S28")["NAOH"] * 15_000
    gas = s27["HCL"] * 29.1 * (_temperature(model, "S27") - 308.15)
    assert _duty(model, "Q7") == pytest.approx((neut - liquor + caustic + gas) / 3600, rel=0.002)


def test_assumed_temperatures_are_the_adiabatic_mixes(model):
    """W101, W102 and M201 are adiabatic (process/simulation.yaml, D-009); M202 mixes HCl gas."""
    flowsheet = _yaml("process/flowsheet.yaml")
    steps = {s["id"]: s for s in flowsheet["steps"]}
    assert _yaml("process/simulation.yaml")["specs"]["W101"]["mode"] == "adiabatic"
    t_w101 = _mix(model, "S14", "S16")
    assert t_w101 == pytest.approx(280.24, abs=0.02)
    for sid in ("S17", "S18", "S19"):
        assert _temperature(model, sid) == pytest.approx(t_w101, abs=0.02), sid
    assert steps["W101"]["crystallizer"]["temperature"] == pytest.approx(t_w101, abs=0.02)
    t_w102 = _mix(model, "S18", "S20")
    for sid in ("S21", "S22", "S23"):
        assert _temperature(model, sid) == pytest.approx(t_w102, abs=0.02), sid
    assert steps["W102"]["crystallizer"]["temperature"] == pytest.approx(t_w102, abs=0.02)
    assert _temperature(model, "S26") == pytest.approx(
        _mix(model, "S15", "S19", "S23", "S25"), abs=0.02
    )
    m5, m11 = (model[1][s]["state"]["design"]["flow"]["value"] for s in ("S5", "S11"))
    t27 = (m5 * _temperature(model, "S5") + m11 * _temperature(model, "S11")) / (m5 + m11)
    assert _temperature(model, "S27") == pytest.approx(t27, abs=0.02)


def test_sources_name_the_right_equipment(model):
    """P1 names R-101's given 4 m3 (recipe.yaml), not the 3.15 m3 core would have sized; the
    product is cooled in DR-101, the step S24 leaves (D-008)."""
    recipe = _yaml("process/recipe.yaml")
    r101 = next(u for u in recipe["unit_procedures"] if u["id"] == "CHLOROSULFONATE")
    assert r101["vessel"]["volume"] == 4.0
    p1 = model[1]["P1"]["state"]["design"]["duty"]["source"]
    assert "4 m3" in p1 and "3.15" not in p1
    s24 = model[1]["S24"]
    assert s24["from"].startswith("D101.")
    assert "DR-101" in s24["state"]["design"]["temperature"]["source"]


def test_yield_and_assay_as_stated(model):
    materials, streams = model
    product = _kmol(model, "S24")
    para = product["PTSCL_S"] + product.get("PTSCL", 0.0)
    assert para / _kmol(model, "S4")["TOL"] == pytest.approx(0.788, abs=0.001)  # 78.8 % (D-005)
    mass = streams["S24"]["state"]["design"]["flow"]["value"]
    assay = para * materials["PTSCL"]["molar_mass"] / mass
    assert assay == pytest.approx(0.997, abs=0.0005)  # 99.7 wt% (D-002)
    manifest = _yaml("process.yaml")
    assert "78.8 %" in manifest["description"]


def test_yield_and_assay_carry_their_caveats():
    """The yield is above SRC-1's 77 % para crude and the assay is an upper bound (L-4): every
    place that states them says so."""
    manifest = _yaml("process.yaml")
    description = " ".join(manifest["description"].split())
    assert "upper bound" in description and "77 %" in description
    tscl = next(o for o in manifest["chemistry"]["outputs"] if o["inventory_key"] == "product:TSCL")
    assert "upper bound" in tscl["note"]
    design = " ".join(_text("DESIGN.md").split())
    assert "The 99.7 wt% is an upper bound" in design
    assert "The modelled yield is above the source's" in design
    assert "upper bound" in _yaml("process/design-basis.yaml")["products"][0]["purity"]
    assert "upper bound" in " ".join(_text("README.md").split())


def test_property_sources_are_registered():
    """Every property source the materials and the flowsheet cite has a DESIGN.md register row."""
    register = next(
        line for line in _text("DESIGN.md").splitlines() if line.startswith("| SRC-11 |")
    )
    for name in ("chemicals", "CRC", "CoolProp", "NIST"):
        assert name in register, name
    cited = _text("process/materials.yaml") + _text("process/flowsheet.yaml")
    assert "SRC-11" in cited
    assert "CRC Handbook)" not in cited  # the CRC values are the chemicals package's tables
    assert "IAPWS-IF97" not in cited  # the steam values are CoolProp's IAPWS water


def test_recipe_basis_gives_1000_t_per_year(model):
    recipe = _yaml("process/recipe.yaml")
    rate = model[1]["S24"]["state"]["design"]["flow"]["value"]
    assert rate * recipe["hours_per_year"]["value"] / 1000 == pytest.approx(1000, rel=0.001)
    batches = rate * recipe["hours_per_year"]["value"] / recipe["batch_size"]["value"]
    assert batches == pytest.approx(571.8, abs=0.1)  # D-003


def test_not_published_in_the_change_that_adds_it():
    publication = _yaml("process.yaml")["publication"]
    assert publication["status"] == "internal"
    assert "license" not in publication
