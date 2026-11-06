"""p-toluenesulfonyl-chloride-1 (#162): the folder's hand-written numbers against its own model.

Fast, without core: the flowsheet's calculated streams (written by cheme process propagate) and
the materials' molar masses and heat capacities are enough to check what the folder states by
hand (DESIGN.md D-004, D-007, D-009):

- the duties written as hand arithmetic (Q1, Q4, the dilution heat Q10, Q7, Q8, Q9) follow from
  the streams they name, and the quench jacket's peak with the dilution heat is the one DESIGN.md
  and the equipment list state;
- core 1.9.0 (D-014): the models write Q2, Q3 and Q5 at their `energy_port` (calculated, the
  values a hand Hess path gives), the dilution heat the semi-batch leaves out is its own assumed
  stream Q10 beside Q5, both to brine, and the split keeps the hand total of 1.8.0;
- the vents' stated capacity covers the recipe's normal peak, each vent's source states its own
  basis, and the rate sensitivity's releases at and beyond it (k/10, k/100) are recorded as a
  design finding; with core, the screening itself and the largest cooling-failure release over
  the batch (not only at core's worst moment) against the vent, with the margin DESIGN states;
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
- the process is public with CC-BY-4.0, every library entry is (ADR 0036).
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


def _provenance(model, qid: str) -> str:
    return model[1][qid]["state"]["design"]["duty"]["provenance"]


def test_hand_duties_follow_the_streams(model):
    assert _duty(model, "Q1") == pytest.approx(_mcp(model, "S1") * 40 / 3600, rel=0.01)
    assert _duty(model, "Q4") == pytest.approx(_mcp(model, "S9") * 10 / 3600, rel=0.01)
    s8 = _kmol(model, "S8")
    dilution = s8["H2SO4"] * 75_000 + (s8["PTSA"] + s8["OTSA"]) * 20_000  # kJ/h
    assert dilution / 3600 == pytest.approx(16.03, rel=0.01)  # the share D-009 states
    assert _provenance(model, "Q10") == "assumed"
    assert _duty(model, "Q10") == pytest.approx(dilution / 3600, rel=0.002)


def _dilution_kW(model) -> float:
    s8 = _kmol(model, "S8")
    return (s8["H2SO4"] * 75_000 + (s8["PTSA"] + s8["OTSA"]) * 20_000) / 3600


def test_models_write_their_duties(model):
    """Core 1.9.0, ADR 0059 (D-014): R101, R102 and Q101 name their cooling stream and propagate
    writes it; a hand Hess path from the streams gives the same values."""
    flowsheet = _yaml("process/flowsheet.yaml")
    steps = {s["id"]: s for s in flowsheet["steps"]}
    for node, qid in (("R101", "Q2"), ("R102", "Q3"), ("Q101", "Q5")):
        assert steps[node]["energy_port"] == "q", node
        stream = model[1][qid]
        assert stream["from"] == f"{node}.q", qid
        assert _provenance(model, qid) == "calculated", qid
        assert stream["state"]["design"]["duty"]["fingerprint"], qid
    s6, s7, s8 = _kmol(model, "S6"), _kmol(model, "S7"), _kmol(model, "S8")
    # Q5: Q101's reactions from its extents and the dose S8 cooled from 308 to 288 K, no dilution
    s12 = _kmol(model, "S12")
    hyd = s8["CSA"] - s12.get("CSA", 0.0)
    amh = s8["AMCS"] - s12.get("AMCS", 0.0)
    tsh = (s8["PTSCL"] - s12["PTSCL"]) + (s8["OTSCL"] - s12["OTSCL"])
    reactions = hyd * 180_000 + amh * 80_000 + tsh * 60_000
    q5 = (reactions + _mcp(model, "S8") * 20) / 3600
    assert _duty(model, "Q5") == pytest.approx(q5, rel=0.002)
    assert _duty(model, "Q5") == pytest.approx(38.920, abs=0.001)
    # Q3: Hess's path through the heat's 298.15 K: S6 from 338.15 K and S7 from 298.15 K to it,
    # CHLP and CHLO there, S8 from it to 308.15 K
    chl = (s6["PTSA"] - s8["PTSA"]) + (s6["OTSA"] - s8["OTSA"])
    q3 = (_mcp(model, "S6") * 40 + chl * 10_000 - _mcp(model, "S8") * 10) / 3600
    assert _duty(model, "Q3") == pytest.approx(q3, rel=0.002)
    assert _duty(model, "Q3") == pytest.approx(3.763, abs=0.001)  # the hand 3.719 is dropped
    # Q2: SALT, SULP and SULO from R101's extents, less the doses S3 and S4 warmed to 338 K
    salt = _kmol(model, "S3")["NH4CL"] - s6.get("NH4CL", 0.0)
    sul = s6["PTSA"] + s6["OTSA"]
    doses = (_mcp(model, "S3") + _mcp(model, "S4")) * 40
    q2 = (salt * 20_000 + sul * 100_000 - doses) / 3600
    assert _duty(model, "Q2") == pytest.approx(q2, rel=0.005)
    assert _duty(model, "Q2") == pytest.approx(23.339, abs=0.001)


def test_quench_duty_split_keeps_the_dilution_heat(model):
    """D-014: the hand Q5 of 1.8.0 (54.948 kW) held the dilution heat the semi-batch leaves out
    (L-2); it is split into the model's Q5 and the assumed Q10, both from Q101 to brine."""
    _, streams = model
    assert streams["Q10"]["from"] == "Q101.dil" and streams["Q10"]["to"].startswith("BRINE.")
    assert streams["Q5"]["to"].startswith("BRINE.")
    assert _duty(model, "Q5") + _duty(model, "Q10") == pytest.approx(54.948, abs=0.005)
    assert _duty(model, "Q10") == pytest.approx(_dilution_kW(model), rel=0.002)
    source = streams["Q10"]["state"]["design"]["duty"]["source"]
    assert "leaves out" in source and "L-2" in source


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
    assert _duty(model, "Q10") * 3600 * cycle_h / dosing_s == pytest.approx(peak, rel=0.002)
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
    assert {s["id"] for s in brine} == {"Q4", "Q5", "Q8", "Q9", "Q10"}
    per_kg = sum(s["state"]["design"]["duty"]["value"] for s in brine) / 126.263
    assert per_kg == pytest.approx(0.811, abs=0.001)  # D-012, process.yaml
    inventory = {
        row.split(",")[0]: row.split(",") for row in _text("lca/inventory.csv").splitlines()[1:]
    }
    assert float(inventory["product:BRINE"][7]) == pytest.approx(per_kg, rel=1e-3)
    washw = next(f for f in _yaml("lca/lca.yaml")["flows"] if f["key"] == "feed:WASHW")
    assert "not counted" not in washw["missing"]
    assert "0.811 kWh" in _text("process.yaml") and "0.811 kWh" in _text("DESIGN.md")
    lca_brine = next(f for f in _yaml("lca/lca.yaml")["flows"] if f["key"] == "product:BRINE")
    assert "Q10" in lca_brine["source"] and "Q10" in inventory["product:BRINE"][-1]


def test_cooling_water_per_kg_as_stated(model):
    """product:CW per kg with the models' Q2 and Q3 (D-012, D-014)."""
    _, streams = model
    cw = [s for s in streams.values() if s.get("kind") == "energy" and s["to"].startswith("CW.")]
    assert {s["id"] for s in cw} == {"Q2", "Q3", "Q7"}
    per_kg = sum(s["state"]["design"]["duty"]["value"] for s in cw) / 126.263
    assert per_kg == pytest.approx(0.610, abs=0.0005)
    assert "0.610 kWh" in _text("process.yaml") and "0.610 kWh" in _text("DESIGN.md")
    assert "0.609 kWh" not in _text("process.yaml")


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


def _hazard(node: str) -> dict:
    flowsheet = _yaml("process/flowsheet.yaml")
    return next(s for s in flowsheet["steps"] if s["id"] == node)["hazard"]


def test_vent_capacity_basis_and_finding_are_recorded():
    """D-011, D-014: the vents' 150 m3/h (ASSUMED, the vent sized for the recipe's normal peak,
    144.9 m3/h at the salt's addition), each node's source with its own basis, and the rate
    sensitivity's releases at the vent's capacity (k/10) and beyond it (k/100) recorded as a
    design finding. The releases themselves are checked against core in the next test."""
    peak_normal = 144.9  # cheme process recipe, vent of R101
    r101, q101 = _hazard("R101"), _hazard("Q101")
    for node, hazard in (("R101", r101), ("Q101", q101)):
        assert hazard["provenance"] == "assumed", node
        assert hazard["vent_capacity"] == 150 and hazard["vent_capacity"] >= peak_normal, node
        assert "mtt" not in hazard, node  # core 1.9.0's default MTT (D-014)
        assert "td24" not in hazard, node  # never estimated
        assert "reactions" not in hazard, node  # every reaction counts (D-011)
    assert "144.9 m3/h" in r101["source"] and "145.5 m3/h" in r101["source"]
    assert "end of the salt addition" in r101["source"] and "0.97" in r101["source"]
    q = q101["source"]
    assert "header" in q and "R101's hazard" in q
    assert "14.1 m3/h" in q and "10 % vented share" in q and "141" in q
    design = " ".join(_text("DESIGN.md").split())
    assert "`hazard.vent_capacity: 150`" in design
    assert "| k/10 | 7.64 % | 362.4 K | 2.1 h | 132.7 m3/h | 150.2 m3/h, 1.00 " in design
    assert "| k/100 | 27.1 % | 420.1 K | 26.6 h | 1302 m3/h | 1302 m3/h, 8.7 " in design
    assert "| 0.16 % | 298.2 K | 14.1 m3/h (11.8 at 14404 s) |" in design
    assert "Design finding: the vent has about 3 % margin at the design rates" in design
    assert "emergency relief" in design and "dosing interlocked" in design
    assert "salt addition in R-101 interlocked" in design


def _largest_release(process, node: str) -> tuple[float, float, float, float]:
    """(m3/h, s, K, kmol/s per batch) of the largest cooling-failure gas release over *node*'s
    batch: core's vent_gas_rate at every point of the cooling profile at that point's MTSR, per
    batch as core's screening scales it (D-011)."""
    from chemeascode.domains.chemistry.thermochemistry import R
    from chemeascode.domains.process.recipe import hours_per_batch
    from chemeascode.domains.process.stirred_tank import solve_node, vent_gas_rate

    fs = process.flowsheet
    case = fs.default_case()
    hours = hours_per_batch(process, case)
    item = process.nodes[node]
    inlets = [
        s
        for s in fs.streams
        if s.kind == "material" and (end := process.ends(s)[1]) is not None and end.node == node
    ]
    solved, _ = solve_node(process, item, inlets, case)
    best = (0.0, 0.0, 0.0, 0.0)
    for point in solved.cooling_profile:
        temperature = point.mtsr()
        kmol_s = hours * vent_gas_rate(process, item, point.moles, temperature, solved.pressure)
        m3_h = kmol_s * R * temperature / solved.pressure * 3600.0
        if m3_h > best[0]:
            best = (m3_h, point.time, temperature, kmol_s)
    return best


def test_core_screens_the_gas_release_against_the_vent():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.model import load
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    entries = {e.node: e for e in report.entries}
    # core's value at its worst moment, the highest MTSR (D-011)
    for node, release, mtsr, mtt in (("R101", 60.28, 343.59, 383.75), ("Q101", 11.79, 298.18, 373.12)):
        entry = entries[node]
        gas = entry.gas_release
        assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(release, abs=0.01), node
        assert gas["vent_capacity_m3_h"] == 150.0 and gas["capacity_ratio"] < 1.0, node
        assert entry.mtsr == pytest.approx(mtsr, abs=0.01), node
        assert entry.mtt == pytest.approx(mtt, abs=0.01), node
    assert not [f for f in report.findings if f.level in ("warning", "error")]
    # the largest release over the batch, with the margin DESIGN.md states (D-011, D-014)
    process, _ = load(PROCESS)
    capacity = {n: _hazard(n)["vent_capacity"] for n in ("R101", "Q101")}
    m3_h, time, _, _ = _largest_release(process, "R101")
    assert m3_h == pytest.approx(145.5, abs=0.1) and time == pytest.approx(3600.0, abs=1.0)
    assert m3_h / capacity["R101"] == pytest.approx(0.97, abs=0.005) and m3_h < capacity["R101"]
    m3_h, time, _, _ = _largest_release(process, "Q101")
    assert m3_h == pytest.approx(14.1, abs=0.05) and time == pytest.approx(14400.0, abs=1.0)
    share = process.nodes["Q101"].batch.vent.shares()["HCL"]
    assert share == pytest.approx(0.1)  # the ASSUMED vented share (D-006)
    assert m3_h / share == pytest.approx(141, abs=0.5) and m3_h / share < capacity["Q101"]
    assert m3_h / share / capacity["Q101"] == pytest.approx(0.94, abs=0.005)


def test_requires_core_1_9():
    plant = _yaml("plant.yaml")
    assert plant["requires"] == "cheme-as-code>=1.9"
    assert "1.9.0" in _text("README.md") and "cheme-as-code 1.9.0" in _text("process.yaml")


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


def test_published_public_with_cc_by():
    publication = _yaml("process.yaml")["publication"]
    assert publication == {"status": "public", "license": "CC-BY-4.0"}
