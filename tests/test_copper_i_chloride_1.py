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
  law passes through its two open points; on its own basis (m per kg of water, s per kg of
  liquor) it is about 30 % above US 3 030 178 A's brine at the R-101 liquor, as DESIGN.md says;
- with core: the network MTSR (CHL and COMP together) from core's cooling profile, at k, k/10
  and k/100, as DESIGN.md D-011 states it next to core's per-reaction MTSR;
- with core: R-101's vessel and jacket as `cheme process recipe` gives them;
- the liquor's CuCl concentration, the copper lost to the brine and X-101's fines as stated;
- the ethanol's flash point (chemicals) and the flammability safeguards of D-011;
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
    # US 3 030 178 A on the law's own basis: the R-101 liquor S11A, m per kg of water
    m_brine = _excess_chloride(model, "S11A")
    assert m_brine == pytest.approx(5.71, abs=0.01)
    assert law(m_brine) == pytest.approx(159, abs=1)  # g per kg of liquor
    materials = model[0]
    s11a = _kmol(model, "S11A")
    density = sum(_kg(model, "S11A").values()) / 1000 / sum(  # kg/L
        n * materials[k]["liquid_molar_volume"] for k, n in s11a.items() if n
    )
    assert density == pytest.approx(1.25, abs=0.01)
    for rho, low, high in ((density, 1.27, 1.30), (1.3, 1.32, 1.35)):  # 155 g/L as g/kg
        assert low < law(m_brine) / (155 / rho) < high, rho
    design = _text("DESIGN.md")
    assert "m = (1.8349 + 0.0046 + 2 x 0.0026) kmol / 0.32323 t of water = 5.71 mol/kg" in design
    assert "s = (5.71/0.282)^1.686 = 159 g per kg of liquor" in design
    assert "the law is 28-34 % high there" in design
    source = model[2]["CR101"]["crystallizer"]["solubility"]["source"]
    assert "159 g per kg of liquor" in source and "133 g/L" not in source
    # the fit points per litre against the law per kg of water (water 0.99 and 0.95 kg/L)
    m1, m2 = 0.282 / 0.99, 2.5 / 0.95
    refit = (0.621 / m1) ** (math.log(39.6) / math.log(m2 / m1))
    assert refit == pytest.approx(3.63, abs=0.01) and 1 - refit / law(0.621) == pytest.approx(0.04, abs=0.005)
    assert "it gives 3.63 instead of 3.79 g/kg at CR101's liquor, 4 % less" in design
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
    fed = _kmol(model, "S5")["CU"]
    assert lost / fed == pytest.approx(0.223, abs=0.001)
    dissolved = s30["CUCL"] + s30["CUCL2"]  # the crystals and the fines are not dissolved
    assert dissolved / fed == pytest.approx(0.221, abs=0.0005)
    assert s30["CUCL"] / fed == pytest.approx(0.216, abs=0.0005)
    assert s30["CUCL2"] / fed == pytest.approx(0.005, abs=0.0005)
    for rel in ("process.yaml", "README.md", "DESIGN.md"):
        text = _text(rel)
        assert "77.6 %" in text and "upper bound" in text, rel
    for rel in ("process.yaml", "README.md"):
        text = _text(rel)
        assert "22.3 % of the copper leaves with the brine (22.1 % dissolved)" in text, rel
        assert "22.3 % of the copper leaves dissolved" not in text, rel
    stated = "22.1 % of the copper fed leaves dissolved (21.6 % as CuCl, 0.5 % as copper(II)), 22.3 % in all"
    basis = _text("process/design-basis.yaml")
    assert basis.count(stated) == 2 and "21 % of the copper" not in basis
    assert stated in _text("DESIGN.md")
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
    assert "| k (design) | 0.63 % | 354.2 K | 373.1 K | 354.4 K |" in design
    assert "| k/10 | 4.26 % | 357.9 K | 373.1 K | 359.8 K |" in design
    assert "| k/100 | 28.1 % | 363.5 K | 373.1 K | 372.1 K |" in design
    assert not [f for f in report.findings if f.level in ("warning", "error")]


def _network_mtsr(root: Path) -> tuple[float, float, float]:
    """R101's MTSR of the network from core's cooling profile: at every recorded moment the
    accumulated chlorine to CuCl2 (CHL) and every CuCl2 then present to CuCl on the excess copper
    (COMP), T + (274.4 kJ/mol n_Cl2 + 54.3 kJ/mol n_CuCl2) / C, C from core's own CHL rise.
    Returns (the largest, core's MTSR there, the copper's margin over what that needs)."""
    from chemeascode.domains.process.model import load
    from chemeascode.domains.process.stirred_tank import solve_node

    process, _ = load(root)
    item = process.nodes["R101"]
    inlets = [
        s for s in process.flowsheet.streams
        if s.kind == "material" and (e := process.ends(s)[1]) is not None and e.node == "R101"
    ]
    solved, _ = solve_node(process, item, inlets, process.flowsheet.default_case())
    best = None
    for point in solved.cooling_profile:
        n = point.moles
        cl2, cu, cucl2 = n.get("CL2", 0.0), n.get("CU", 0.0), n.get("CUCL2", 0.0)
        if point.rises.get("CHL", 0.0) <= 0 or min(cu, cl2) <= 0:
            continue
        heat_capacity = 220_100 * min(cu, cl2) / point.rises["CHL"]
        network = point.temperature + (274_400 * cl2 + 54_300 * cucl2) / heat_capacity
        if best is None or network > best[0]:
            best = (network, point.mtsr(), cu - (2 * cl2 + cucl2))
    assert best is not None
    return best


def test_network_mtsr_as_stated(tmp_path):
    """D-011, L-2: core's MTSR takes each reaction alone; the network's, with COMP's heat on the
    CuCl2 the accumulated chlorine forms and on the CuCl2 present, is higher, and at k/100 it
    comes within about 1 K of the MTT (water's boiling point)."""
    pytest.importorskip("chemeascode")
    import shutil

    stated = {1: (354.4, 354.2), 10: (359.8, 357.9), 100: (372.1, 363.5)}
    for div, (net, core) in stated.items():
        root = PROCESS
        if div != 1:
            root = tmp_path / f"k{div}"
            shutil.copytree(PROCESS, root, ignore=shutil.ignore_patterns("runs", "build"))
            path = root / "process" / "reactions.yaml"
            text = path.read_text(encoding="utf-8")
            for a in ("1.684e4", "2.476e4"):
                assert text.count(f"k: {{A: {a},") == 1, a
                text = text.replace(f"k: {{A: {a},", f"k: {{A: {float(a) / div:.6g},")
            path.write_text(text, encoding="utf-8")
        found, core_found, copper_margin = _network_mtsr(root)
        assert found == pytest.approx(net, abs=0.05), div
        assert core_found == pytest.approx(core, abs=0.05), div
        assert copper_margin > 0, div  # the copper covers the whole network in every case
    assert 373.12 - stated[100][0] == pytest.approx(1.0, abs=0.05)
    design = _text("DESIGN.md")
    assert "at k/100 it reaches 372.1 K, 1.0 K below water's boiling point" in design
    assert "Safety requirement (recorded, for the basic engineering and the HAZOP):** the chlorine dosing stops on a sign of accumulation" in design
    assert "354.2 / 357.9 / 363.5 K at k, k/10 and k/100; the network gives 354.4 / 359.8 / 372.1 K" in design
    assert "(The MTSR, from the model, is right.)" not in design
    for rel in ("DESIGN.md", "process/reactions.yaml"):
        assert "conservative choice" not in _text(rel), rel
    for rel in ("README.md", "process.yaml"):
        text = _text(rel)
        assert "372.1 K" in text and "within about 1 K of the MTT" in text, rel
        assert "also at a hundred times slower rates" not in text, rel


def test_r101_vessel_and_jacket_as_the_recipe_gives():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.recipe import recipe_report

    result = recipe_report(PROCESS)
    vessel = next(v for v in result.vessels if v.procedure == "CHLORINATE")
    assert vessel.working_volume == pytest.approx(3.643, abs=0.001)
    assert vessel.peak_duty == pytest.approx(57.77, abs=0.01)
    assert vessel.removable == pytest.approx(157.9, abs=0.1)
    assert vessel.jacket_area == pytest.approx(10.6, abs=0.05)
    stated = "(3.64 m3 at the end of the dosing, 73 %); its jacket (U 300 W/(m2 K) glass-lined, 10.6 m2 wetted at the charge) removes 158 kW against the model's peak 57.8 kW"
    assert stated in _text("DESIGN.md")
    assert "peak 57.8 kW against 158 kW" in _text("DESIGN.md")
    r101 = next(e for e in _yaml("equipment/equipment-list.yaml")["equipment"] if e["tag"] == "R-101")
    assert "3.64 m3" in r101["notes"] and "10.6 m2" in r101["notes"]
    assert "removes 158 kW against the model's peak 57.8 kW" in r101["notes"]


def test_liquor_concentration_and_fines_as_stated(model):
    materials = model[0]
    kg = _kg(model, "S11A")
    volume = sum(n * materials[k]["liquid_molar_volume"] for k, n in _kmol(model, "S11A").items() if n)
    assert kg["CUCL"] / volume == pytest.approx(129, abs=0.5)  # g/L
    assert kg["CUCL"] / sum(kg.values()) * 1000 == pytest.approx(103, abs=0.5)  # g/kg
    flowsheet = (PROCESS / "process/flowsheet.yaml").read_text(encoding="utf-8")
    header = " ".join(l.lstrip("# ") for l in flowsheet.splitlines()[:20])
    assert "about 129 g/L CuCl dissolved (103 g/kg, S11A)" in header
    assert "about 129 g/L CuCl, 103 g/kg" in model[2]["F101"]["solid_separation"]["source"]
    assert "about 129 g/L CuCl (103 g/kg)" in _text("process.yaml")
    for rel in ("process.yaml", "process/flowsheet.yaml"):
        text = _text(rel)
        for old in ("150 g/L", "140 g/L", "130 g/L"):
            assert old not in text, (rel, old)
    fines = _kg(model, "S34")
    assert fines["CU"] * CYCLE_H == pytest.approx(0.30, abs=0.01)
    assert sum(fines.values()) * CYCLE_H == pytest.approx(0.60, abs=0.01)
    x101 = next(e for e in _yaml("equipment/equipment-list.yaml")["equipment"] if e["tag"] == "X-101")
    assert "about 0.3 kg of copper fines a batch (0.6 kg wet with liquor)" in x101["notes"]


def test_ethanol_flammability_is_reasoned(model):
    ethanol = _kg(model, "S24")["ETOH"] * CYCLE_H
    assert ethanol == pytest.approx(186, abs=0.5)
    pytest.importorskip("chemicals")
    from chemicals import safety

    assert safety.T_flash("64-17-5") == pytest.approx(285.15)
    assert safety.LFL(CASRN="64-17-5") == pytest.approx(0.031)
    # every step with ethanol in F-101 runs above its flash point
    for sid in ("S25", "S26", "S27"):
        assert _t(model, sid) > safety.T_flash("64-17-5"), sid
    assert model[2]["D101"]["dryer"]["temperature"] > safety.T_flash("64-17-5")
    design = _text("DESIGN.md")
    assert "Ethanol's flash point is 285 K, its lower flammable limit 3.1 vol%" in design
    for safeguard in (
        "nitrogen inerting of F-101, its condenser and T-105 as a flammability safeguard",
        "the vacuum broken with nitrogen only, never with air",
        "discharge only after the dryer's end point",
        "the vacuum pump's exhaust",
        "need a hazardous-area zone",
    ):
        assert safeguard in design, safeguard


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
